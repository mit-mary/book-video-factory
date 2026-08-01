from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
TESTS = Path(__file__).resolve().parent
SRC = PACKAGE / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(TESTS))

from book_video_factory.renderer_contracts import (  # noqa: E402
    ContractValidationError,
    RendererErrorCode,
    RenderStatus,
    render_request_to_dict,
)
from book_video_factory.renderers import (  # noqa: E402
    PAPER_COLLAGE_COMPOSITION_ID,
    PAPER_COLLAGE_TEMPLATE_ID,
    PAPER_COLLAGE_TEMPLATE_VERSION,
    REMOTION_EXTENSION,
)
from book_video_factory.renderers.remotion_contract import (  # noqa: E402
    _paper_layout,
    _paper_theme_from_dict,
)
import test_remotion_contract_renderer as phase4a_test  # noqa: E402


FakeRunner = phase4a_test.FakeRunner
RENDERER_PROJECT = phase4a_test.RENDERER_PROJECT
rehash = phase4a_test.rehash


THEME = RENDERER_PROJECT / "config" / "paper-collage-theme-v1.json"
TEXTURE = RENDERER_PROJECT / "assets" / "paper-texture-v1.svg"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paper_request(request: object) -> object:
    payload = json.loads(json.dumps(render_request_to_dict(request)))
    for asset_id, role, path, media_type in (
        ("paper-collage-theme-v1", "renderer_theme_tokens", THEME, "application/json"),
        ("paper-texture-v1", "renderer_texture", TEXTURE, "image/svg+xml"),
    ):
        payload["assets"].append(
            {
                "asset_id": asset_id,
                "role": role,
                "ref": {
                    "root": "remotion_renderer",
                    "path": path.relative_to(RENDERER_PROJECT).as_posix(),
                },
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "media_type": media_type,
                "source_manifest_artifact_id": f"phase4b:{asset_id}",
                "rights_ref": "fixture:program-generated",
            }
        )
    payload["renderer"]["required_capabilities"].extend(
        ["layered_images", "camera_motion", "transitions"]
    )
    payload["extensions"] = {
        REMOTION_EXTENSION: {
            "schema_version": "1.0",
            "composition_id": PAPER_COLLAGE_COMPOSITION_ID,
            "audio_source": "final_mix_only",
            "visual_policy": "paper_collage_single_still_v1",
            "caption_policy": "sentence_two_line_bottom_card_v1",
            "rights_holds": ["fixture hold"],
            "template_id": PAPER_COLLAGE_TEMPLATE_ID,
            "template_version": PAPER_COLLAGE_TEMPLATE_VERSION,
            "motion_preset": "subtle",
            "transition_preset": "paper-cut",
            "caption_preset": "bottom-card",
            "theme_tokens_asset_id": "paper-collage-theme-v1",
            "theme_tokens_sha256": sha256(THEME),
            "texture_asset_id": "paper-texture-v1",
            "texture_sha256": sha256(TEXTURE),
            "opening": {
                "start_tick": 0,
                "end_tick": 1200,
                "title": "TEST TITLE",
                "subtitle": "CONTROLLED FIXTURE",
            },
        }
    }
    return rehash(payload)


def mutate(request: object, callback) -> object:
    payload = json.loads(json.dumps(render_request_to_dict(request)))
    callback(payload)
    return rehash(payload)


def replace_theme(project: Path, request: object, callback) -> object:
    theme = json.loads(THEME.read_text(encoding="utf-8"))
    callback(theme)
    target = project / "inputs" / "phase4b-mutated-theme.json"
    target.write_text(json.dumps(theme, ensure_ascii=False), encoding="utf-8")
    digest = sha256(target)
    payload = json.loads(json.dumps(render_request_to_dict(request)))
    binding = next(
        item for item in payload["assets"] if item["asset_id"] == "paper-collage-theme-v1"
    )
    binding["ref"] = {"root": "project", "path": target.relative_to(project).as_posix()}
    binding["bytes"] = target.stat().st_size
    binding["sha256"] = digest
    payload["extensions"][REMOTION_EXTENSION]["theme_tokens_sha256"] = digest
    return rehash(payload)


class PaperCollageTemplateTests(unittest.TestCase):
    def fixture(self):
        helper = phase4a_test.RemotionContractRendererTests()
        temp, project, request, files, context = helper.fixture()
        request = paper_request(request)
        return helper, temp, project, request, files, context

    def renderer(self, runner: FakeRunner):
        return phase4a_test.RemotionContractRendererTests().renderer(runner)

    def cleanup_staging(self, context) -> None:
        self.addCleanup(
            lambda: __import__("shutil").rmtree(
                RENDERER_PROJECT / "public" / "attempts" / context.attempt_id,
                ignore_errors=True,
            )
        )

    def test_paper_template_stages_theme_texture_and_succeeds(self) -> None:
        _, temp, project, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.cleanup_staging(context)
        self.assertEqual(result.status, RenderStatus.SUCCEEDED)
        props = json.loads(
            (context.attempts_directory / context.attempt_id / "remotion-props.json").read_text(
                encoding="utf-8"
            )
        )
        extension = props["rendererExtension"]
        self.assertEqual(extension["template"]["id"], PAPER_COLLAGE_TEMPLATE_ID)
        self.assertEqual(extension["theme"]["sha256"], sha256(THEME))
        self.assertIn("paper-texture-v1", extension["theme"]["tokens"]["paperTexture"]["src"])
        self.assertNotIn(str(project), json.dumps(props))
        payload = render_request_to_dict(request)
        layout = _paper_layout(
            payload["output_spec"]["width"],
            payload["output_spec"]["height"],
            _paper_theme_from_dict(json.loads(THEME.read_text(encoding="utf-8"))),
            payload["captions"]["tracks"][0]["style"]["safe_area"],
            tuple(
                cue["text"]
                for track in payload["captions"]["tracks"]
                for cue in track["cues"]
            ),
        )
        envelope = layout["image_card_motion_envelope"]
        self.assertGreaterEqual(envelope["x"], 72)
        self.assertGreaterEqual(envelope["y"], 72)
        self.assertLessEqual(envelope["x"] + envelope["width"], 720 - 72)
        self.assertLessEqual(
            envelope["y"] + envelope["height"],
            layout["caption_card"]["y"] - 24,
        )

    def test_unknown_template_id_is_blocked(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        request = mutate(request, lambda p: p["extensions"][REMOTION_EXTENSION].__setitem__("template_id", "unknown"))
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.status, RenderStatus.BLOCKED)
        self.assertFalse(runner.called)

    def test_missing_theme_fails_before_runner(self) -> None:
        _, temp, project, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        def change(payload):
            binding = next(item for item in payload["assets"] if item["asset_id"] == "paper-collage-theme-v1")
            binding["ref"] = {"root": "project", "path": "inputs/missing-theme.json"}
        request = mutate(request, change)
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_ASSET_MISSING.value)
        self.assertFalse(runner.called)

    def test_theme_hash_mismatch_fails_before_runner(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        request = mutate(request, lambda p: p["extensions"][REMOTION_EXTENSION].__setitem__("theme_tokens_sha256", "f" * 64))
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_HASH_MISMATCH.value)
        self.assertFalse(runner.called)

    def test_token_range_is_fail_closed(self) -> None:
        _, temp, project, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        request = replace_theme(project, request, lambda t: t["motion"].__setitem__("max_scale_delta_milli", 41))
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_INPUT_INVALID.value)
        self.assertFalse(runner.called)

    def test_caption_over_two_lines_is_fail_closed(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        def change(payload):
            payload["captions"]["tracks"][0]["cues"][0]["text"] = "one\ntwo\nthree"
        request = mutate(request, change)
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_INPUT_INVALID.value)
        self.assertFalse(runner.called)

    def test_caption_safe_area_cannot_be_bypassed(self) -> None:
        _, temp, project, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        request = replace_theme(project, request, lambda t: t["canvas"].__setitem__("safe_margin_bottom", 64))
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_INPUT_INVALID.value)
        self.assertFalse(runner.called)

    def test_image_card_layout_rejects_too_small_canvas(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        def change(payload):
            payload["output_spec"]["width"] = 400
        request = mutate(request, change)
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_INPUT_INVALID.value)
        self.assertFalse(runner.called)

    def test_motion_preset_is_fail_closed(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        request = mutate(request, lambda p: p["extensions"][REMOTION_EXTENSION].__setitem__("motion_preset", "fast"))
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.status, RenderStatus.BLOCKED)
        self.assertFalse(runner.called)

    def test_transition_preset_is_fail_closed(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        request = mutate(request, lambda p: p["extensions"][REMOTION_EXTENSION].__setitem__("transition_preset", "wipe"))
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.status, RenderStatus.BLOCKED)
        self.assertFalse(runner.called)

    def test_missing_font_remains_fail_closed(self) -> None:
        _, temp, _, request, files, context = self.fixture()
        self.addCleanup(temp.cleanup)
        files["caption-font"].unlink()
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_FONT_UNAVAILABLE.value)
        self.assertFalse(runner.called)

    def test_missing_staged_texture_fails_before_runner(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        def change(payload):
            binding = next(item for item in payload["assets"] if item["asset_id"] == "paper-texture-v1")
            binding["ref"] = {"root": "project", "path": "inputs/missing-texture.svg"}
        request = mutate(request, change)
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_ASSET_MISSING.value)
        self.assertFalse(runner.called)

    def test_existing_attempt_is_preserved(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        guard = context.attempts_directory / context.attempt_id / "guard.txt"
        guard.parent.mkdir(parents=True)
        guard.write_text("preserve", encoding="utf-8")
        runner = FakeRunner()
        with self.assertRaises(ContractValidationError):
            self.renderer(runner).render(request, context)
        self.assertEqual(guard.read_text(encoding="utf-8"), "preserve")
        self.assertFalse(runner.called)

    def test_composition_process_failure_is_terminal(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        runner = FakeRunner(returncode=7, create_output=False)
        result = self.renderer(runner).render(request, context)
        self.cleanup_staging(context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_PROCESS_FAILED.value)

    def test_missing_output_is_terminal(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        runner = FakeRunner(create_output=False)
        result = self.renderer(runner).render(request, context)
        self.cleanup_staging(context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_OUTPUT_MISSING.value)


if __name__ == "__main__":
    unittest.main()
