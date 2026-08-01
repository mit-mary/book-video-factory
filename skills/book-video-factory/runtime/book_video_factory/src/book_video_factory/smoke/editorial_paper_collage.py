"""Phase 4B.5 frozen-fixture validation for EditorialPaperCollageV1."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Mapping

from PIL import Image

from book_video_factory.renderer_contracts import (
    RenderExecutionContext,
    RenderMode,
    RenderStatus,
    RootResolver,
    render_request_from_dict,
    render_request_to_dict,
    render_result_to_dict,
    request_id_from_hash,
    semantic_request_hash,
    write_canonical_once,
    write_render_request,
)
from book_video_factory.renderers import (
    EDITORIAL_PAPER_COMPOSITION_ID,
    EDITORIAL_PAPER_LAYOUTS,
    EDITORIAL_PAPER_TEMPLATE_ID,
    EDITORIAL_PAPER_TEMPLATE_VERSION,
    REMOTION_EXTENSION,
    REMOTION_RENDERER_ID,
    REMOTION_RENDERER_VERSION,
    RemotionContractRenderer,
)

from .legacy_v4_real_media import (
    SmokeFixtureError,
    _create_project,
    _font_environment,
    _probe,
    _sha256,
    _shared_assets,
    _write_pcm_wave,
    _write_json,
)
from .paper_collage_real_media import _external_qc, _paper_request
from .remotion_contract_real_media import (
    RIGHTS_HOLD,
    _derived_snapshot,
    _final_mix,
    _media_contract_comparison,
    _record_phase4a_approvals,
    _runtime_root,
)


MARKER_NAME = "EDITORIAL_PAPER_SMOKE_FIXTURE.json"
FIXTURE_TYPE = "editorial-paper-collage-frozen-fixture-experiment"
VISUAL_DURATION_TICKS = 18_000
VISUAL_SEGMENTS = (
    (
        "HOOK",
        "改变生活的，\n通常不是一个重大决定。",
    ),
    (
        "SMALL_ACTION",
        "真正起作用的，\n往往只是一个很小的动作。",
    ),
    (
        "THREE_ACTIONS",
        "早睡十分钟。拒绝一次迎合。\n承认自己的不舒服。",
    ),
    (
        "TURNING",
        "生活不会突然改变，\n它只是慢慢转向。",
    ),
    (
        "ENDING",
        "你今天的一个小选择，\n可能正在改变以后的人生。",
    ),
)


def initialize_fixture_root(root: Path) -> Path:
    requested = Path(root).expanduser()
    if requested.exists() and any(requested.iterdir()):
        raise SmokeFixtureError("fixture initialization requires an empty directory")
    requested.mkdir(parents=True, exist_ok=True)
    return _write_json(
        requested / MARKER_NAME,
        {
            "fixture": True,
            "fixture_type": FIXTURE_TYPE,
            "version": "2",
            "production_use": False,
            "generated_assets_only": True,
            "provider_calls_allowed": False,
            "selected_direction": "A",
            "visual_asset": "direction-a-text-free-art-atlas",
            "duration_ticks": VISUAL_DURATION_TICKS,
        },
    )


def validate_fixture_root(root: Path) -> dict[str, Any]:
    resolved = Path(root).expanduser().resolve()
    try:
        marker = json.loads((resolved / MARKER_NAME).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SmokeFixtureError("Phase 4B.5 fixture marker is missing or unreadable") from error
    expected = {
        "fixture": True,
        "fixture_type": FIXTURE_TYPE,
        "version": "2",
        "production_use": False,
        "generated_assets_only": True,
        "provider_calls_allowed": False,
        "selected_direction": "A",
        "visual_asset": "direction-a-text-free-art-atlas",
        "duration_ticks": VISUAL_DURATION_TICKS,
    }
    if marker != expected:
        raise SmokeFixtureError("Phase 4B.5 fixture marker does not match")
    if (resolved / "project.json").exists():
        raise SmokeFixtureError("fixture root must not be a production Project root")
    return marker


def _editorial_request(
    snapshot: Any,
    snapshot_path: Path,
    compatibility_snapshot: Any,
    compatibility_snapshot_path: Path,
    project: Path,
    runtime: Path,
    renderer: Path,
    root_bindings: Mapping[str, Path],
    *,
    mode: RenderMode,
) -> tuple[Any, RootResolver]:
    paper, resolver = _paper_request(
        snapshot,
        snapshot_path,
        compatibility_snapshot,
        compatibility_snapshot_path,
        project,
        runtime,
        renderer,
        root_bindings,
        mode=mode,
    )
    payload = render_request_to_dict(paper)
    atlas_root = renderer.parents[1] / "docs" / "phase-4b5" / "visual-directions" / "source-assets"
    atlas_path = atlas_root / "direction-a-art-atlas.png"
    if not atlas_path.is_file():
        raise SmokeFixtureError("Direction A text-free art atlas is missing")
    payload["roots"]["phase4b5_visual_assets"] = {
        "kind": "artifact",
        "input_access": "read_only",
        "output_access": "none",
    }
    payload["assets"].append(
        {
            "asset_id": "direction-a-art-atlas",
            "role": "approved_direction_a_visual_atlas",
            "ref": {
                "root": "phase4b5_visual_assets",
                "path": "direction-a-art-atlas.png",
            },
            "bytes": atlas_path.stat().st_size,
            "sha256": _sha256(atlas_path),
            "media_type": "image/png",
            "source_manifest_artifact_id": "phase4b5:direction-a-art-atlas",
            "rights_ref": "fixture:built-in-image-generation-direction-a",
        }
    )
    segment_duration = VISUAL_DURATION_TICKS // len(VISUAL_SEGMENTS)
    timeline_segments = []
    caption_cues = []
    for index, (segment_id, text) in enumerate(VISUAL_SEGMENTS):
        start_tick = index * segment_duration
        end_tick = (index + 1) * segment_duration
        cue_id = f"direction-a-caption-{index + 1:02d}"
        timeline_segments.append(
            {
                "segment_id": segment_id,
                "start_tick": start_tick,
                "end_tick": end_tick,
                "visual": {
                    "kind": "still",
                    "asset_ids": ["direction-a-art-atlas"],
                    "motion": "none",
                },
                "narration": None,
                "caption_cue_ids": [cue_id],
                "overlay_ids": [],
                "transition": {"in": "cut", "out": "cut"},
                "metadata": {
                    "scene_ids": ["DIRECTION_A_ATLAS"],
                    "script_line_ids": [cue_id],
                },
            }
        )
        caption_cues.append(
            {
                "cue_id": cue_id,
                "segment_id": segment_id,
                "start_tick": start_tick + 180,
                "end_tick": end_tick - 180,
                "text": text,
                "granularity": "sentence",
                "words": [],
                "highlight": None,
            }
        )
    payload["timeline"] = {
        "model": "narration_segments_v1",
        "timebase": {"ticks_per_second": 1000},
        "duration_ticks": VISUAL_DURATION_TICKS,
        "frame_rounding": "integer_round_half_up_v1",
        "segments": timeline_segments,
    }
    payload["captions"] = {
        "tracks": [
            {
                "track_id": "direction-a-synthetic-zh-CN",
                "language": "zh-CN",
                "text_source_asset_id": "approved-script",
                "timing_source_asset_id": "asr-timing",
                "alignment_revision": 1,
                "style": {
                    "font_asset_id": "font-chinese",
                    "font_role": "caption-chinese-fixture",
                    "safe_area": {"left_px": 72, "right_px": 72, "bottom_px": 104},
                    "max_lines": 2,
                    "overflow_policy": "fail",
                    "line_break_policy": "contract-two-line-v1",
                    "highlight_tokens": {},
                },
                "cues": caption_cues,
            }
        ]
    }
    payload["audio"]["cues"] = []
    payload["output_spec"]["duration_ticks"] = VISUAL_DURATION_TICKS
    extension = payload["extensions"][REMOTION_EXTENSION]
    extension.update(
        {
            "composition_id": EDITORIAL_PAPER_COMPOSITION_ID,
            "visual_policy": "editorial_paper_collage_five_layout_v1",
            "caption_policy": "sentence_two_line_integrated_v1",
            "template_id": EDITORIAL_PAPER_TEMPLATE_ID,
            "template_version": EDITORIAL_PAPER_TEMPLATE_VERSION,
            "motion_preset": "editorial-purposeful",
            "transition_preset": "paper-cut-column-wipe",
            "caption_preset": "integrated-two-line",
            "layout_sequence": list(EDITORIAL_PAPER_LAYOUTS),
            "opening": {
                "start_tick": 0,
                "end_tick": 1200,
                "title": "改变生活的",
                "subtitle": "通常不是一个重大决定。",
            },
        }
    )
    filename = (
        "editorial-direction-a-preview.mp4"
        if mode is RenderMode.PREVIEW
        else "editorial-direction-a-final-experimental.mp4"
    )
    payload["output"] = {
        "artifact_id": f"editorial-direction-a-{mode.value}",
        "role": "preview_video" if mode is RenderMode.PREVIEW else "local_experimental_master",
        "target": {
            "root": "project",
            "path": f"08_render_合成/editorial-direction-a/{mode.value}/{filename}",
        },
        "overwrite_policy": "fail_if_exists",
    }
    payload["metadata"] = {
        "created_at": "2026-08-01T04:30:00Z",
        "created_by": "phase4b5-direction-a-fixture-adapter-v1",
        "notes": "Visual-validation fixture using the approved text-free Direction A atlas and synthetic Chinese copy.",
    }
    payload["request_hash"] = "0" * 64
    payload["request_id"] = "pending"
    digest = semantic_request_hash(payload)
    payload["request_hash"] = digest
    payload["request_id"] = request_id_from_hash(digest)
    expanded_resolver = RootResolver(
        {**resolver.bindings, "phase4b5_visual_assets": atlas_root.resolve()}
    )
    return render_request_from_dict(payload), expanded_resolver


def _visual_validation_final_mix(project: Path) -> Path:
    target = project / "06_music_音乐" / "phase4b5-direction-a-final-mix.wav"
    _write_pcm_wave(
        target,
        duration_seconds=18,
        frequency_hz=260,
        amplitude=2400,
        three_sections=True,
    )
    return target


def _composition_discovery(renderer: Path, props_path: Path) -> dict[str, Any]:
    command = ["node", str(renderer / "scripts" / "list-compositions.mjs"), str(props_path)]
    completed = subprocess.run(
        command,
        cwd=renderer,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=dict(os.environ),
    )
    return {
        "argv": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout or "",
        "stderr": completed.stderr or "",
        "composition_found": EDITORIAL_PAPER_COMPOSITION_ID in (completed.stdout or ""),
    }


def _render_layout_stills(
    renderer: Path,
    project: Path,
    props_path: Path,
    request: Any,
) -> dict[str, Any]:
    output = project / "08_render_合成" / "editorial-direction-a" / "stills"
    output.mkdir(parents=True, exist_ok=False)
    props = json.loads(props_path.read_text(encoding="utf-8"))
    segments = props["segments"]
    records: list[dict[str, Any]] = []
    for layout_index, layout in enumerate(EDITORIAL_PAPER_LAYOUTS):
        candidate_indexes = list(range(layout_index, len(segments), len(EDITORIAL_PAPER_LAYOUTS)))
        if not candidate_indexes:
            raise SmokeFixtureError(f"frozen fixture does not exercise layout {layout}")
        segment_index = candidate_indexes[-1] if layout_index == 0 else candidate_indexes[0]
        segment = segments[segment_index]
        frame = (int(segment["startFrame"]) + int(segment["endFrame"])) // 2
        target = output / f"layout-{layout_index + 1:02d}-{layout}.png"
        command = [
            "node",
            str(renderer / "scripts" / "render-still.mjs"),
            "--props",
            str(props_path),
            "--output",
            str(target),
            "--composition-id",
            EDITORIAL_PAPER_COMPOSITION_ID,
            "--expected-request-hash",
            request.request_hash,
            "--frame",
            str(frame),
        ]
        completed = subprocess.run(
            command,
            cwd=renderer,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=dict(os.environ),
        )
        if completed.returncode != 0 or not target.is_file():
            raise SmokeFixtureError(f"static frame render failed for {layout}")
        with Image.open(target) as image:
            image.load()
            dimensions_ok = image.size == (
                int(request.output_spec["width"]),
                int(request.output_spec["height"]),
            )
            nonempty = image.getbbox() is not None and len(image.getcolors(maxcolors=1_000_000) or ()) >= 8
            opaque = image.mode != "RGBA" or image.getchannel("A").getextrema() == (255, 255)
        records.append(
            {
                "layout": layout,
                "segment_index": segment_index,
                "frame": frame,
                "path": str(target),
                "bytes": target.stat().st_size,
                "sha256": _sha256(target),
                "dimensions_ok": dimensions_ok,
                "nonempty": nonempty,
                "opaque": opaque,
                "passed": dimensions_ok and nonempty and opaque,
            }
        )
    layout_sequence = props["rendererExtension"]["layoutSequence"]
    assigned = [layout_sequence[index % len(layout_sequence)] for index in range(len(segments))]
    tokens = props["rendererExtension"]["theme"]["tokens"]
    caption = tokens["caption"]
    caption_height = (
        (caption["fontSize"] * caption["lineHeightMilli"] + 999) // 1000
        * caption["maxLines"]
        + caption["paddingY"] * 2
    )
    checks = {
        "five_unique_layouts": len(layout_sequence) == 5 and len(set(layout_sequence)) == 5,
        "no_adjacent_layout_repeat": all(
            assigned[index] != assigned[index - 1] for index in range(1, len(assigned))
        ),
        "visual_positions_cover_left_right_center_full": set(layout_sequence)
        == set(EDITORIAL_PAPER_LAYOUTS),
        "caption_height_at_most_22_percent": caption_height * 100
        <= int(props["height"]) * 22,
        "caption_max_two_lines": caption["maxLines"] == 2
        and props["captionStyle"]["maxLines"] == 2,
        "transition_types_at_most_two": props["rendererExtension"]["transitionPreset"]
        == "paper-cut-column-wipe",
        "direction_a_atlas_only_visual": all(
            segment["visualRefs"]
            == [
                f"attempts/{props['attemptId']}/assets/direction-a-art-atlas.png"
            ]
            for segment in segments
        ),
        "synthetic_chinese_copy_present": all(
            any(character > "\u007f" for character in caption["text"])
            for caption in props["captions"]
        ),
        "duration_between_15_and_20_seconds": 15 * int(props["fps"])
        <= int(props["durationInFrames"])
        <= 20 * int(props["fps"]),
    }
    report = {
        "schema_version": "1.0",
        "composition_id": EDITORIAL_PAPER_COMPOSITION_ID,
        "request_hash": request.request_hash,
        "layout_sequence": layout_sequence,
        "assigned_layouts": assigned,
        "checks": checks,
        "frames": records,
        "passed": all(item["passed"] for item in records) and all(checks.values()),
    }
    index = write_canonical_once(output / "editorial-static-frame-index.json", report)
    return {"index": str(index), "report": report}


def run_experiment(fixture_root: Path, renderer_project: Path) -> dict[str, Any]:
    root = Path(fixture_root).expanduser().resolve()
    marker = validate_fixture_root(root)
    renderer = Path(renderer_project).expanduser().resolve()
    runtime = _runtime_root()
    shared, shared_record = _shared_assets(root)
    project, semantic = _create_project(root, shared, "fixture-editorial-direction-a")
    _record_phase4a_approvals(project)
    final_mix = _visual_validation_final_mix(project)
    snapshot, snapshot_path, compatibility, compatibility_path, bindings = _derived_snapshot(
        project, runtime, final_mix
    )
    font_env, font_hashes = _font_environment(runtime)
    environment = dict(os.environ)
    environment.update(font_env)
    results: dict[str, Any] = {}
    fixture_token = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:8]
    final_request = None
    final_props = None
    for mode in (RenderMode.PREVIEW, RenderMode.FINAL):
        request, resolver = _editorial_request(
            snapshot,
            snapshot_path,
            compatibility,
            compatibility_path,
            project,
            runtime,
            renderer,
            bindings,
            mode=mode,
        )
        request_path = write_render_request(request, project / "manifests" / "requests")
        attempt_id = f"phase4b5-editorial-{mode.value}-{fixture_token}"
        context = RenderExecutionContext(
            resolver=resolver,
            attempts_directory=project / "08_render_合成" / "attempts",
            attempt_id=attempt_id,
            environment=environment,
        )
        result = RemotionContractRenderer(renderer).render(request, context)
        if result.status is not RenderStatus.SUCCEEDED:
            raise SmokeFixtureError(
                f"Editorial Direction A {mode.value} failed with {result.primary_error_code}; evidence retained"
            )
        props_path = renderer / "public" / "attempts" / attempt_id / "props.json"
        discovery = _composition_discovery(renderer, props_path)
        if discovery["returncode"] != 0 or not discovery["composition_found"]:
            raise SmokeFixtureError("EditorialPaperCollageV1 discovery failed")
        output_path = resolver.resolve(result.output[0].ref, require_exists=True)
        detailed_probe = _probe(output_path)
        media_comparison = _media_contract_comparison(request, detailed_probe)
        if not media_comparison["passed"]:
            raise SmokeFixtureError("editorial media duration exceeds technical tolerance")
        qc = _external_qc(project, request, result, resolver, media_comparison)
        results[mode.value] = {
            "request": {"id": request.request_id, "hash": request.request_hash, "path": str(request_path)},
            "attempt_id": attempt_id,
            "result": render_result_to_dict(result),
            "output": str(output_path),
            "detailed_probe": detailed_probe,
            "media_contract_comparison": media_comparison,
            "composition_discovery": discovery,
            "external_qc": qc,
            "props_path": str(props_path),
        }
        if mode is RenderMode.FINAL:
            final_request = request
            final_props = props_path
    assert final_request is not None and final_props is not None
    static_frames = _render_layout_stills(renderer, project, final_props, final_request)
    final_qc = results["final"]["external_qc"]["report"]
    passed = (
        results["preview"]["external_qc"]["report"]["technical_status"] == "pass"
        and final_qc["technical_status"] == "pass"
        and final_qc["public_release_allowed"] is False
        and RIGHTS_HOLD in final_qc["release_holds"]
        and static_frames["report"]["passed"]
    )
    report = {
        "schema_version": "1.0",
        "fixture": marker,
        "renderer": {"id": REMOTION_RENDERER_ID, "version": REMOTION_RENDERER_VERSION},
        "template": {
            "composition_id": EDITORIAL_PAPER_COMPOSITION_ID,
            "template_id": EDITORIAL_PAPER_TEMPLATE_ID,
            "template_version": EDITORIAL_PAPER_TEMPLATE_VERSION,
        },
        "release_snapshot": {"id": snapshot.snapshot_id, "hash": snapshot.snapshot_hash, "path": str(snapshot_path)},
        "shared_assets": shared_record,
        "semantic_input_hashes": semantic,
        "final_mix": {"path": str(final_mix), "bytes": final_mix.stat().st_size, "sha256": _sha256(final_mix)},
        "font_hashes": font_hashes,
        "preview": results["preview"],
        "final": results["final"],
        "static_frames": static_frames,
        "scope": {
            "selected_direction": "A",
            "provider_calls": 0,
            "network_asset_calls": 0,
            "commercial_assets": 0,
            "audio_mixing_inside_renderer": False,
            "legacy_modified": False,
            "default_renderer_changed": False,
            "real_book_used": False,
            "geometric_scene_assets_used_by_timeline": False,
            "direction_a_text_free_atlas_used": True,
            "word_highlight": False,
            "waveform_or_hud": False,
        },
        "visual_validation": {
            "direction_status": "DIRECTION_A_APPROVED",
            "template_status": "REMOTION_TEMPLATE_VISUAL_VALIDATION_PENDING_USER_REVIEW",
            "machine_checks_passed": static_frames["report"]["passed"],
            "user_visual_approval_recorded": False,
        },
        "passed": passed,
    }
    report_path = root / "phase-4b5-direction-a-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    human = root / "phase-4b5-direction-a-report.md"
    human.write_text(
        "\n".join(
            [
                "# Phase 4B.5 Direction A Visual-Validation Report",
                "",
                f"- Technical result: {'PASS' if passed else 'FAIL'}",
                "- Direction status: DIRECTION_A_APPROVED",
                "- Template status: REMOTION_TEMPLATE_VISUAL_VALIDATION_PENDING_USER_REVIEW",
                f"- Preview: {results['preview']['result']['status']}",
                f"- Final: {results['final']['result']['status']}",
                f"- Five-layout composition machine check: {'PASS' if static_frames['report']['passed'] else 'FAIL'}",
                f"- Technical QC: {final_qc['technical_status']}",
                f"- Public release allowed: {str(final_qc['public_release_allowed']).lower()}",
                f"- Rights hold: {RIGHTS_HOLD}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-dir", type=Path, required=True)
    parser.add_argument("--renderer-project", type=Path, required=True)
    parser.add_argument("--initialize-only", action="store_true")
    args = parser.parse_args()
    if args.initialize_only:
        marker = initialize_fixture_root(args.fixture_dir)
        print(json.dumps({"initialized": True, "marker": str(marker)}, ensure_ascii=False))
        return 0
    report = run_experiment(args.fixture_dir, args.renderer_project)
    print(
        json.dumps(
            {
                "passed": report["passed"],
                "report": str(Path(args.fixture_dir).resolve() / "phase-4b5-direction-a-report.json"),
                "preview_sha256": report["preview"]["result"]["output"][0]["sha256"],
                "final_sha256": report["final"]["result"]["output"][0]["sha256"],
                "static_frames_passed": report["static_frames"]["report"]["passed"],
                "public_release_allowed": report["final"]["external_qc"]["report"]["public_release_allowed"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
