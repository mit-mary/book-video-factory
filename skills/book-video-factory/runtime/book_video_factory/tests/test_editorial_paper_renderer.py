from __future__ import annotations

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
    RenderStatus,
    render_request_to_dict,
)
from book_video_factory.renderers import (  # noqa: E402
    EDITORIAL_PAPER_COMPOSITION_ID,
    EDITORIAL_PAPER_SCENE_SEQUENCE,
    EDITORIAL_PAPER_TEMPLATE_ID,
    EDITORIAL_PAPER_TEMPLATE_VERSION,
    REMOTION_EXTENSION,
)
import test_paper_collage_renderer as phase4b_test  # noqa: E402


FakeRunner = phase4b_test.FakeRunner
rehash = phase4b_test.rehash


class EditorialProbe(phase4b_test.phase4a_test.FakeProbe):
    def probe(self, path: Path) -> dict:
        payload = super().probe(path)
        payload["video"]["height"] = 1280
        return payload


def editorial_request(request: object) -> object:
    payload = json.loads(json.dumps(render_request_to_dict(phase4b_test.paper_request(request))))
    payload["output_spec"]["width"] = 720
    payload["output_spec"]["height"] = 1280
    extension = payload["extensions"][REMOTION_EXTENSION]
    extension.update(
        {
            "composition_id": EDITORIAL_PAPER_COMPOSITION_ID,
            "visual_policy": "editorial_unified_three_scene_types_v1",
            "caption_policy": "sentence_two_line_fixed_safe_zone_v1",
            "template_id": EDITORIAL_PAPER_TEMPLATE_ID,
            "template_version": EDITORIAL_PAPER_TEMPLATE_VERSION,
            "motion_preset": "editorial-unified-v1",
            "transition_preset": "hard-cut-paper-reveal",
            "caption_preset": "fixed-safe-zone-two-line",
            "scene_type_sequence": list(EDITORIAL_PAPER_SCENE_SEQUENCE),
        }
    )
    return rehash(payload)


def mutate(request: object, callback) -> object:
    payload = json.loads(json.dumps(render_request_to_dict(request)))
    callback(payload)
    return rehash(payload)


class EditorialPaperTemplateTests(unittest.TestCase):
    def fixture(self):
        helper = phase4b_test.phase4a_test.RemotionContractRendererTests()
        temp, project, request, files, context = helper.fixture()
        return helper, temp, project, editorial_request(request), files, context

    def renderer(self, runner: FakeRunner):
        return phase4b_test.phase4a_test.RemotionContractRenderer(
            phase4b_test.RENDERER_PROJECT,
            runner=runner,
            probe=EditorialProbe(),
            clock=iter(
                [
                    "2026-08-01T01:00:00Z",
                    "2026-08-01T01:00:01Z",
                    "2026-08-01T01:00:02Z",
                ]
            ).__next__,
        )

    def cleanup_staging(self, context) -> None:
        self.addCleanup(
            lambda: __import__("shutil").rmtree(
                phase4b_test.RENDERER_PROJECT / "public" / "attempts" / context.attempt_id,
                ignore_errors=True,
            )
        )

    def test_editorial_template_stages_assets_and_binds_three_scene_types(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        result = self.renderer(FakeRunner()).render(request, context)
        self.cleanup_staging(context)
        self.assertEqual(result.status, RenderStatus.SUCCEEDED)
        props = json.loads(
            (context.attempts_directory / context.attempt_id / "remotion-props.json").read_text(
                encoding="utf-8"
            )
        )
        extension = props["rendererExtension"]
        self.assertEqual(extension["compositionId"], EDITORIAL_PAPER_COMPOSITION_ID)
        self.assertEqual(extension["template"]["id"], EDITORIAL_PAPER_TEMPLATE_ID)
        self.assertEqual(extension["sceneTypeSequence"], list(EDITORIAL_PAPER_SCENE_SEQUENCE))
        self.assertEqual(len(set(extension["sceneTypeSequence"])), 3)
        result_extension = result.extensions[REMOTION_EXTENSION]
        self.assertEqual(result_extension["template_id"], EDITORIAL_PAPER_TEMPLATE_ID)

    def test_reordered_scene_type_sequence_is_fail_closed(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)

        def change(payload):
            scene_types = payload["extensions"][REMOTION_EXTENSION]["scene_type_sequence"]
            scene_types[0], scene_types[1] = scene_types[1], scene_types[0]

        request = mutate(request, change)
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertNotEqual(result.status, RenderStatus.SUCCEEDED)
        self.assertFalse(runner.called)

    def test_legacy_layout_sequence_is_fail_closed(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)

        def change(payload):
            extension = payload["extensions"][REMOTION_EXTENSION]
            extension["layout_sequence"] = [
                "split-column",
                "scale-contrast",
                "staggered-notes",
                "full-bleed-turn",
                "quiet-asymmetry",
            ]
            del extension["scene_type_sequence"]

        request = mutate(request, change)
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertNotEqual(result.status, RenderStatus.SUCCEEDED)
        self.assertFalse(runner.called)

    def test_bottom_card_caption_preset_is_rejected(self) -> None:
        _, temp, _, request, _, context = self.fixture()
        self.addCleanup(temp.cleanup)
        request = mutate(
            request,
            lambda payload: payload["extensions"][REMOTION_EXTENSION].__setitem__(
                "caption_preset", "bottom-card"
            ),
        )
        runner = FakeRunner()
        result = self.renderer(runner).render(request, context)
        self.assertNotEqual(result.status, RenderStatus.SUCCEEDED)
        self.assertFalse(runner.called)


if __name__ == "__main__":
    unittest.main()
