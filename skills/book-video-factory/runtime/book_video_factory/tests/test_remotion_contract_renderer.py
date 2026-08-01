from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[5]
SRC = PACKAGE / "src"
sys.path.insert(0, str(SRC))

from book_video_factory.renderer_contracts import (  # noqa: E402
    CommandResult,
    ContractValidationError,
    RenderExecutionContext,
    RendererErrorCode,
    RenderStatus,
    RootResolver,
    render_request_from_dict,
    render_request_to_dict,
    request_id_from_hash,
    semantic_request_hash,
)
from book_video_factory.renderers import (  # noqa: E402
    REMOTION_COMPOSITION_ID,
    REMOTION_EXTENSION,
    REMOTION_RENDERER_ID,
    REMOTION_RENDERER_VERSION,
    RemotionContractRenderer,
)


RENDERER_PROJECT = REPOSITORY / "renderers" / "remotion-contract-v1"
EXAMPLE = REPOSITORY / "docs" / "phase-2" / "schemas" / "render-request-v1.example.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rehash(payload: dict) -> object:
    payload["request_id"] = "pending"
    payload["request_hash"] = "0" * 64
    digest = semantic_request_hash(payload)
    payload["request_hash"] = digest
    payload["request_id"] = request_id_from_hash(digest)
    return render_request_from_dict(payload)


def build_request(project: Path) -> tuple[object, dict[str, Path]]:
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    files: dict[str, Path] = {}
    for index, asset in enumerate(payload["assets"]):
        suffix = ".ttf" if asset["role"].startswith("font_") else ".wav" if "audio" in asset["role"] or "stem" in asset["role"] else ".png" if asset["role"] == "scene_visual" else ".json"
        path = project / "inputs" / f"{asset['asset_id']}{suffix}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"phase4a-{index}-{asset['asset_id']}".encode("utf-8"))
        asset["ref"] = {"root": "project", "path": path.relative_to(project).as_posix()}
        asset["bytes"] = path.stat().st_size
        asset["sha256"] = sha256(path)
        files[asset["asset_id"]] = path
    capability = RENDERER_PROJECT / "config" / "renderer-capabilities.json"
    payload["renderer"] = {
        "id": REMOTION_RENDERER_ID,
        "version": REMOTION_RENDERER_VERSION,
        "capability_document_ref": {
            "root": "remotion_renderer",
            "path": "config/renderer-capabilities.json",
        },
        "capability_document_sha256": sha256(capability),
        "required_capabilities": [
            "still_images",
            "captions",
            "audio_playback",
            "deterministic_render",
        ],
    }
    payload["roots"] = {
        "project": {"kind": "project", "input_access": "read_only", "output_access": "request_targets_only"},
        "runtime": {"kind": "runtime", "input_access": "read_only", "output_access": "none"},
        "remotion_renderer": {"kind": "artifact", "input_access": "read_only", "output_access": "none"},
    }
    payload["output"]["target"] = {
        "root": "project",
        "path": "outputs/remotion-final.mp4",
    }
    payload["output"]["artifact_id"] = "remotion-final"
    payload["output"]["role"] = "local_experimental_master"
    payload["output_spec"]["artifact_role"] = "local_experimental_master"
    payload["output_spec"]["video"]["encoding_policy"] = "remotion-h264-v1"
    for segment in payload["timeline"]["segments"]:
        ids = list(segment["visual"]["asset_ids"])
        segment["visual"] = {
            "kind": "still",
            "asset_ids": ids[:1] or ["scene-002"],
            "motion": "none",
        }
        segment["overlay_ids"] = []
        segment["transition"] = {"in": "cut", "out": "cut"}
    payload["overlays"] = []
    payload["audio"]["stem_usage"] = "visual_analysis_only"
    for track in payload["captions"]["tracks"]:
        track["style"]["max_lines"] = 2
        track["style"]["highlight_tokens"] = {}
        for cue in track["cues"]:
            cue["highlight"] = None
            cue["words"] = []
            cue["granularity"] = "sentence"
    payload["extensions"] = {
        REMOTION_EXTENSION: {
            "schema_version": "1.0",
            "composition_id": REMOTION_COMPOSITION_ID,
            "audio_source": "final_mix_only",
            "rights_holds": ["fixture hold"],
        }
    }
    return rehash(payload), files


class FakeProbe:
    def probe(self, path: Path) -> dict:
        return {
            "duration_ticks": 12000,
            "video": {
                "codec": "h264",
                "width": 720,
                "height": 960,
                "fps": {"numerator": 30, "denominator": 1},
                "pixel_format": "yuv420p",
                "frame_count": 360,
            },
            "audio": {"codec": "aac", "sample_rate": 48000, "channels": 2},
        }


class FakeRunner:
    def __init__(self, *, returncode: int = 0, create_output: bool = True) -> None:
        self.returncode = returncode
        self.create_output = create_output
        self.called = False

    def run(self, command, *, cwd: Path, env) -> CommandResult:
        self.called = True
        if self.create_output and self.returncode == 0:
            output = Path(command[command.index("--output") + 1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"phase4a-remotion-test-mp4")
        return CommandResult(self.returncode, stdout="test stdout", stderr="test stderr", elapsed_ms=7)


class RemotionContractRendererTests(unittest.TestCase):
    def fixture(self):
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        project.mkdir()
        request, files = build_request(project)
        resolver = RootResolver(
            {
                "project": project,
                "runtime": project,
                "remotion_renderer": RENDERER_PROJECT,
            }
        )
        context = RenderExecutionContext(
            resolver=resolver,
            attempts_directory=project / "attempts",
            attempt_id=f"phase4a-unit-{project.parent.name}",
            environment={},
        )
        return temp, project, request, files, context

    def renderer(self, runner: FakeRunner) -> RemotionContractRenderer:
        return RemotionContractRenderer(
            RENDERER_PROJECT,
            runner=runner,
            probe=FakeProbe(),
            clock=iter(
                [
                    "2026-08-01T01:00:00Z",
                    "2026-08-01T01:00:01Z",
                    "2026-08-01T01:00:02Z",
                ]
            ).__next__,
        )

    def test_success_stages_props_and_collects_handoff(self) -> None:
        temp, project, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.status, RenderStatus.SUCCEEDED)
        self.assertTrue(runner.called)
        self.assertEqual(result.qc_handoff["request_hash"], request.request_hash)
        self.assertEqual(len(result.sidecars), 4)
        props = RENDERER_PROJECT / "public" / "attempts" / context.attempt_id / "props.json"
        self.addCleanup(lambda: __import__("shutil").rmtree(props.parent, ignore_errors=True))
        payload = json.loads(props.read_text(encoding="utf-8"))
        self.assertEqual(payload["audio"]["assetId"], "final-mix")
        self.assertNotIn(str(project), json.dumps(payload))

    def test_missing_image_fails_before_runner(self) -> None:
        temp, _, request, files, context = self.fixture()
        self.addCleanup(temp.cleanup)
        files["scene-001"].unlink()
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_ASSET_MISSING.value)
        self.assertFalse(runner.called)

    def test_asset_hash_mismatch_fails_before_runner(self) -> None:
        temp, _, request, files, context = self.fixture()
        self.addCleanup(temp.cleanup)
        files["scene-001"].write_bytes(b"mutated")
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_HASH_MISMATCH.value)
        self.assertFalse(runner.called)

    def test_missing_final_mix_fails_before_runner(self) -> None:
        temp, _, request, files, context = self.fixture()
        self.addCleanup(temp.cleanup)
        files["final-mix"].unlink()
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_ASSET_MISSING.value)
        self.assertFalse(runner.called)

    def test_missing_font_fails_before_runner(self) -> None:
        temp, _, request, files, context = self.fixture()
        self.addCleanup(temp.cleanup)
        files["caption-font"].unlink()
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_FONT_UNAVAILABLE.value)
        self.assertFalse(runner.called)

    def test_unsupported_capability_is_blocked(self) -> None:
        temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        payload = json.loads(json.dumps(render_request_to_dict(request)))
        payload["renderer"]["required_capabilities"].append("audio_mixing")
        request = rehash(payload)
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.status, RenderStatus.BLOCKED)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED.value)
        self.assertFalse(runner.called)

    def test_unknown_composition_is_rejected(self) -> None:
        temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        payload = json.loads(json.dumps(render_request_to_dict(request)))
        payload["extensions"][REMOTION_EXTENSION]["composition_id"] = "MissingComposition"
        request = rehash(payload)
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertFalse(runner.called)
        self.assertNotEqual(result.status, RenderStatus.SUCCEEDED)

    def test_odd_h264_dimension_is_rejected_before_runner(self) -> None:
        temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        payload = json.loads(json.dumps(render_request_to_dict(request)))
        payload["output_spec"]["width"] = 719
        request = rehash(payload)
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_INPUT_INVALID.value)
        self.assertFalse(runner.called)

    def test_nonzero_node_process_is_failed(self) -> None:
        temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        runner = FakeRunner(returncode=9, create_output=False)
        result = self.renderer(runner).render(request, context)
        self.addCleanup(lambda: __import__("shutil").rmtree(RENDERER_PROJECT / "public" / "attempts" / context.attempt_id, ignore_errors=True))
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_PROCESS_FAILED.value)
        self.assertTrue(runner.called)

    def test_zero_exit_without_output_is_failed(self) -> None:
        temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        runner = FakeRunner(create_output=False)
        result = self.renderer(runner).render(request, context)
        self.addCleanup(lambda: __import__("shutil").rmtree(RENDERER_PROJECT / "public" / "attempts" / context.attempt_id, ignore_errors=True))
        self.assertEqual(result.primary_error_code, RendererErrorCode.RENDER_OUTPUT_MISSING.value)

    def test_existing_attempt_path_is_preserved_and_runner_not_called(self) -> None:
        temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        guard = context.attempts_directory / context.attempt_id / "guard.txt"
        guard.parent.mkdir(parents=True)
        guard.write_text("preserve", encoding="utf-8")
        runner = FakeRunner()
        with self.assertRaises(ContractValidationError):
            self.renderer(runner).render(request, context)
        self.assertEqual(guard.read_text(encoding="utf-8"), "preserve")
        self.assertFalse(runner.called)

    def test_existing_output_is_preserved_and_runner_not_called(self) -> None:
        temp, project, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        output = project / "outputs" / "remotion-final.mp4"
        output.parent.mkdir(parents=True)
        output.write_bytes(b"preserve")
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertNotEqual(result.status, RenderStatus.SUCCEEDED)
        self.assertEqual(output.read_bytes(), b"preserve")
        self.assertFalse(runner.called)


if __name__ == "__main__":
    unittest.main()
