"""Phase 4B real-media and static-frame experiment for PaperCollageVisualV1."""

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
    ArtifactBinding,
    PortableRef,
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
    PAPER_COLLAGE_COMPOSITION_ID,
    PAPER_COLLAGE_TEMPLATE_ID,
    PAPER_COLLAGE_TEMPLATE_VERSION,
    REMOTION_EXTENSION,
    REMOTION_RENDERER_ID,
    REMOTION_RENDERER_VERSION,
    RemotionContractRenderer,
)
from book_video_factory.renderers.remotion_contract import _paper_layout, _paper_theme_from_dict

from .legacy_v4_real_media import (
    SmokeFixtureError,
    _create_project,
    _font_environment,
    _probe,
    _sha256,
    _shared_assets,
    _write_json,
)
from .remotion_contract_real_media import (
    RIGHTS_HOLD,
    _derived_snapshot,
    _final_mix,
    _media_contract_comparison,
    _record_phase4a_approvals,
    _retarget_request,
    _runtime_root,
)


MARKER_NAME = "PAPER_COLLAGE_SMOKE_FIXTURE.json"
FIXTURE_TYPE = "paper-collage-visual-real-media-experiment"


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
            "version": "1",
            "production_use": False,
            "generated_assets_only": True,
            "provider_calls_allowed": False,
        },
    )


def validate_fixture_root(root: Path) -> dict[str, Any]:
    resolved = Path(root).expanduser().resolve()
    try:
        marker = json.loads((resolved / MARKER_NAME).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SmokeFixtureError("Phase 4B fixture marker is missing or unreadable") from error
    expected = {
        "fixture": True,
        "fixture_type": FIXTURE_TYPE,
        "version": "1",
        "production_use": False,
        "generated_assets_only": True,
        "provider_calls_allowed": False,
    }
    if marker != expected:
        raise SmokeFixtureError("Phase 4B fixture marker does not match")
    if (resolved / "project.json").exists():
        raise SmokeFixtureError("fixture root must not be a production Project root")
    return marker


def _binding(asset_id: str, role: str, path: Path, renderer: Path, media_type: str) -> dict[str, Any]:
    return {
        "asset_id": asset_id,
        "role": role,
        "ref": {
            "root": "remotion_renderer",
            "path": path.relative_to(renderer).as_posix(),
        },
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
        "media_type": media_type,
        "source_manifest_artifact_id": f"phase4b:{asset_id}",
        "rights_ref": "fixture:program-generated",
    }


def _paper_request(
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
    base, resolver = _retarget_request(
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
    payload = render_request_to_dict(base)
    theme_path = renderer / "config" / "paper-collage-theme-v1.json"
    texture_path = renderer / "assets" / "paper-texture-v1.svg"
    payload["assets"].extend(
        [
            _binding("paper-collage-theme-v1", "renderer_theme_tokens", theme_path, renderer, "application/json"),
            _binding("paper-texture-v1", "renderer_texture", texture_path, renderer, "image/svg+xml"),
        ]
    )
    payload["renderer"]["required_capabilities"].extend(
        ["layered_images", "camera_motion", "transitions"]
    )
    role = "preview_video" if mode is RenderMode.PREVIEW else "local_experimental_master"
    filename = "paper-collage-preview.mp4" if mode is RenderMode.PREVIEW else "paper-collage-final-experimental.mp4"
    payload["output"] = {
        "artifact_id": "paper-collage-preview" if mode is RenderMode.PREVIEW else "paper-collage-final",
        "role": role,
        "target": {
            "root": "project",
            "path": f"08_render_合成/paper-collage/{mode.value}/{filename}",
        },
        "overwrite_policy": "fail_if_exists",
    }
    payload["extensions"] = {
        REMOTION_EXTENSION: {
            "schema_version": "1.0",
            "composition_id": PAPER_COLLAGE_COMPOSITION_ID,
            "audio_source": "final_mix_only",
            "visual_policy": "paper_collage_single_still_v1",
            "caption_policy": "sentence_two_line_bottom_card_v1",
            "rights_holds": [RIGHTS_HOLD],
            "template_id": PAPER_COLLAGE_TEMPLATE_ID,
            "template_version": PAPER_COLLAGE_TEMPLATE_VERSION,
            "motion_preset": "subtle",
            "transition_preset": "paper-cut",
            "caption_preset": "bottom-card",
            "theme_tokens_asset_id": "paper-collage-theme-v1",
            "theme_tokens_sha256": _sha256(theme_path),
            "texture_asset_id": "paper-texture-v1",
            "texture_sha256": _sha256(texture_path),
            "opening": {
                "start_tick": 0,
                "end_tick": 1200,
                "title": "TEST TITLE",
                "subtitle": "CONTROLLED VISUAL FIXTURE",
            },
        }
    }
    payload["metadata"] = {
        "created_at": "2026-08-01T02:30:00Z",
        "created_by": "phase4b-paper-collage-fixture-adapter-v1",
        "notes": "Generated non-production paper-collage visual fixture.",
    }
    payload["request_hash"] = "0" * 64
    payload["request_id"] = "pending"
    digest = semantic_request_hash(payload)
    payload["request_hash"] = digest
    payload["request_id"] = request_id_from_hash(digest)
    return render_request_from_dict(payload), resolver


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
        "composition_found": PAPER_COLLAGE_COMPOSITION_ID in (completed.stdout or ""),
    }


def _external_qc(
    project: Path,
    request: Any,
    result: Any,
    resolver: RootResolver,
    media_comparison: Mapping[str, Any],
) -> dict[str, Any]:
    handoff = result.qc_handoff
    if handoff is None or handoff.get("attempt_id") != result.attempt_id:
        raise SmokeFixtureError("external QC received a missing or mismatched handoff")
    if handoff.get("request_hash") != request.request_hash:
        raise SmokeFixtureError("external QC Request hash mismatch")
    output = result.output[0]
    output_path = resolver.resolve(output.ref, require_exists=True)
    if _sha256(output_path) != output.sha256:
        raise SmokeFixtureError("external QC output hash mismatch")
    checks = list(handoff.get("renderer_checks", ()))
    technical_pass = (
        bool(checks)
        and all(item.get("result") == "pass" for item in checks)
        and bool(media_comparison.get("passed"))
    )
    holds = list(handoff.get("release_holds", ()))
    report = {
        "schema_version": "1.0",
        "adapter": "phase4b-paper-collage-technical-qc-v1",
        "source": "current_attempt_qc_handoff",
        "request_hash": request.request_hash,
        "attempt_id": result.attempt_id,
        "output_asset_id": output.asset_id,
        "output_sha256": output.sha256,
        "technical_status": "pass" if technical_pass else "fail",
        "local_experimental_master": technical_pass,
        "public_release_allowed": technical_pass and not holds,
        "release_holds": holds,
        "media_comparison": dict(media_comparison),
        "directory_scan": False,
    }
    path = write_canonical_once(
        project / "09_qc_质检" / "paper-collage" / result.attempt_id / "technical-qc.json",
        report,
    )
    return {"path": str(path), "report": report}


def _render_stills(
    renderer: Path,
    project: Path,
    props_path: Path,
    request: Any,
) -> dict[str, Any]:
    output = project / "08_render_合成" / "paper-collage" / "stills"
    output.mkdir(parents=True, exist_ok=False)
    props = json.loads(props_path.read_text(encoding="utf-8"))
    duration = int(props["durationInFrames"])
    frames = {
        "frame-opening.png": 18,
        "frame-segment-1-middle.png": 66,
        "frame-segment-2-middle.png": 129,
        "frame-segment-3-middle.png": 201,
        "frame-ending.png": max(0, duration - 1),
    }
    records = []
    for filename, frame in frames.items():
        target = output / filename
        command = [
            "node",
            str(renderer / "scripts" / "render-still.mjs"),
            "--props", str(props_path),
            "--output", str(target),
            "--composition-id", PAPER_COLLAGE_COMPOSITION_ID,
            "--expected-request-hash", request.request_hash,
            "--frame", str(frame),
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
            raise SmokeFixtureError(f"static frame render failed for {filename}")
        with Image.open(target) as image:
            image.load()
            dimensions_ok = image.size == (int(request.output_spec["width"]), int(request.output_spec["height"]))
            nonempty = image.getbbox() is not None and len(image.getcolors(maxcolors=1_000_000) or ()) >= 4
            alpha_ok = image.mode != "RGBA" or image.getchannel("A").getextrema() == (255, 255)
        records.append(
            {
                "name": filename,
                "frame": frame,
                "path": str(target),
                "bytes": target.stat().st_size,
                "sha256": _sha256(target),
                "dimensions_ok": dimensions_ok,
                "nonempty": nonempty,
                "opaque": alpha_ok,
                "passed": dimensions_ok and nonempty and alpha_ok,
            }
        )
    tokens = props["rendererExtension"]["theme"]["tokens"]
    source_theme = _paper_theme_from_dict(
        json.loads((renderer / "config" / "paper-collage-theme-v1.json").read_text(encoding="utf-8"))
    )
    first_track = request.captions["tracks"][0]
    layout = _paper_layout(
        int(request.output_spec["width"]),
        int(request.output_spec["height"]),
        source_theme,
        first_track["style"]["safe_area"],
        tuple(str(cue["text"]) for track in request.captions["tracks"] for cue in track["cues"]),
    )
    canvas = source_theme["canvas"]
    image_envelope = layout["image_card_motion_envelope"]
    caption_envelope = layout["caption_card_visual_envelope"]
    layout_checks = {
        "image_motion_envelope_inside_safe_area": (
            image_envelope["x"] >= canvas["safe_margin_x"]
            and image_envelope["y"] >= canvas["safe_margin_top"]
            and image_envelope["x"] + image_envelope["width"]
            <= int(request.output_spec["width"]) - canvas["safe_margin_x"]
            and image_envelope["y"] + image_envelope["height"]
            <= layout["caption_card"]["y"] - 24
        ),
        "caption_visual_envelope_inside_safe_area": (
            caption_envelope["x"] >= canvas["safe_margin_x"]
            and caption_envelope["y"] >= canvas["safe_margin_top"]
            and caption_envelope["x"] + caption_envelope["width"]
            <= int(request.output_spec["width"]) - canvas["safe_margin_x"]
            and caption_envelope["y"] + caption_envelope["height"]
            <= int(request.output_spec["height"]) - canvas["safe_margin_bottom"]
        ),
    }
    report = {
        "schema_version": "1.0",
        "composition_id": PAPER_COLLAGE_COMPOSITION_ID,
        "request_hash": request.request_hash,
        "theme_hash": props["rendererExtension"]["theme"]["sha256"],
        "texture_hash": tokens["paperTexture"]["sha256"],
        "layout": layout,
        "layout_checks": layout_checks,
        "contract_safe_area": dict(first_track["style"]["safe_area"]),
        "caption_count": len(props["captions"]),
        "segment_count": len(props["segments"]),
        "frames": records,
        "passed": all(item["passed"] for item in records) and all(layout_checks.values()),
    }
    index = write_canonical_once(output / "static-frame-index.json", report)
    return {"index": str(index), "report": report}


def run_experiment(fixture_root: Path, renderer_project: Path) -> dict[str, Any]:
    root = Path(fixture_root).expanduser().resolve()
    marker = validate_fixture_root(root)
    renderer = Path(renderer_project).expanduser().resolve()
    runtime = _runtime_root()
    shared, shared_record = _shared_assets(root)
    project, semantic = _create_project(root, shared, "fixture-paper-collage")
    _record_phase4a_approvals(project)
    final_mix = _final_mix(project)
    snapshot, snapshot_path, compatibility, compatibility_path, bindings = _derived_snapshot(
        project, runtime, final_mix
    )
    font_env, font_hashes = _font_environment(runtime)
    environment = dict(os.environ)
    environment.update(font_env)
    fixture_token = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:8]
    results: dict[str, Any] = {}
    final_request = None
    final_props = None
    for mode in (RenderMode.PREVIEW, RenderMode.FINAL):
        request, resolver = _paper_request(
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
        attempt_id = f"phase4b-paper-{mode.value}-{fixture_token}"
        context = RenderExecutionContext(
            resolver=resolver,
            attempts_directory=project / "08_render_合成" / "attempts",
            attempt_id=attempt_id,
            environment=environment,
        )
        result = RemotionContractRenderer(renderer).render(request, context)
        if result.status is not RenderStatus.SUCCEEDED:
            raise SmokeFixtureError(
                f"Paper collage {mode.value} failed with {result.primary_error_code}; evidence retained"
            )
        props_path = renderer / "public" / "attempts" / attempt_id / "props.json"
        discovery = _composition_discovery(renderer, props_path)
        if discovery["returncode"] != 0 or not discovery["composition_found"]:
            raise SmokeFixtureError("PaperCollageVisualV1 discovery failed")
        output_path = resolver.resolve(result.output[0].ref, require_exists=True)
        detailed_probe = _probe(output_path)
        media_comparison = _media_contract_comparison(request, detailed_probe)
        if not media_comparison["passed"]:
            raise SmokeFixtureError("paper-collage media duration exceeds technical tolerance")
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
    static_frames = _render_stills(renderer, project, final_props, final_request)
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
            "composition_id": PAPER_COLLAGE_COMPOSITION_ID,
            "template_id": PAPER_COLLAGE_TEMPLATE_ID,
            "template_version": PAPER_COLLAGE_TEMPLATE_VERSION,
            "theme_sha256": _sha256(renderer / "config" / "paper-collage-theme-v1.json"),
            "texture_sha256": _sha256(renderer / "assets" / "paper-texture-v1.svg"),
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
            "provider_calls": 0,
            "network_asset_calls": 0,
            "commercial_assets": 0,
            "audio_mixing_inside_renderer": False,
            "legacy_modified": False,
            "default_renderer_changed": False,
            "word_highlight": False,
            "waveform_or_hud": False,
        },
        "passed": passed,
    }
    report_path = root / "phase-4b-experiment-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    human = root / "phase-4b-experiment-report.md"
    human.write_text(
        "\n".join(
            [
                "# Phase 4B Paper Collage Experiment",
                "",
                f"- Result: {'PASS' if passed else 'FAIL'}",
                f"- Preview: {results['preview']['result']['status']}",
                f"- Final: {results['final']['result']['status']}",
                f"- Static frames: {'PASS' if static_frames['report']['passed'] else 'FAIL'}",
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
    parser.add_argument("--keep-artifacts", action="store_true")
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
                "report": str(Path(args.fixture_dir).resolve() / "phase-4b-experiment-report.json"),
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
