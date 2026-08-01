"""Phase 4A generated real-media experiment for RemotionContractRenderer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

from book_video_factory.manifests import record_approval
from book_video_factory.renderer_contracts import (
    ArtifactBinding,
    PortableRef,
    RenderExecutionContext,
    RenderMode,
    RenderStatus,
    RootResolver,
    collect_v4_release,
    create_release_snapshot,
    map_v4_snapshot_to_request,
    release_snapshot_to_dict,
    render_request_from_dict,
    render_request_to_dict,
    render_result_to_dict,
    request_id_from_hash,
    semantic_request_hash,
    write_canonical_once,
    write_release_snapshot,
    write_render_request,
)
from book_video_factory.renderers import (
    REMOTION_COMPOSITION_ID,
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
    _write_json,
    _write_pcm_wave,
)


MARKER_NAME = "REMOTION_SMOKE_FIXTURE.json"
FIXTURE_TYPE = "remotion-contract-real-media-experiment"
RELEASE_ID = "phase4a-remotion-release-v1"
RIGHTS_HOLD = "H2 external rights-clearance evidence is not recorded."


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[3]


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
    marker_path = resolved / MARKER_NAME
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SmokeFixtureError("Phase 4A fixture marker is missing or unreadable") from error
    expected = {
        "fixture": True,
        "fixture_type": FIXTURE_TYPE,
        "version": "1",
        "production_use": False,
        "generated_assets_only": True,
        "provider_calls_allowed": False,
    }
    if marker != expected:
        raise SmokeFixtureError("Phase 4A fixture marker does not match")
    if (resolved / "project.json").exists():
        raise SmokeFixtureError("fixture root must not be a production Project root")
    return marker


def _phase4a_subjects(project: Path) -> dict[str, list[Path]]:
    return {
        "script": [project / "02_story_script_故事脚本/script.v2.bilingual.json"],
        "timing": [project / "05_voice_人声/asr-v3/v3-b-locked-master.json"],
        "visual_rights": [
            project / f"03_images_生成图片/approved/v4/S{index:02d}.png"
            for index in range(1, 13)
        ],
        "cover_rights": [
            project / "01_research_资料搜集/sources/cover/cover_manifest.json",
            project / "01_research_资料搜集/sources/cover/cover.png",
        ],
        "bgm_rights": [project / "06_music_音乐/v4-smoke-original-bgm.mp3"],
        "sfx_rights": [project / "06_music_音乐/H2-用户确认原片高频音效层.wav"],
        "voice_rights": [project / "05_voice_人声/v3-b-locked-master.wav"],
    }


def _record_phase4a_approvals(project: Path) -> None:
    for gate, subjects in _phase4a_subjects(project).items():
        record_approval(
            project,
            release_id=RELEASE_ID,
            gate=gate,
            decision="approved",
            reviewer="phase4a-fixture-generator",
            subjects=subjects,
            note="Program-generated, non-production Remotion contract fixture.",
            event_id=f"phase4a-{project.name}-{gate}",
            reviewed_at="2026-08-01T01:00:00+00:00",
        )


def _final_mix(project: Path) -> Path:
    target = project / "06_music_音乐/phase4a-generated-final-mix.wav"
    _write_pcm_wave(
        target,
        duration_seconds=Decimal("11.52"),
        frequency_hz=260,
        amplitude=2400,
        three_sections=True,
    )
    return target


def _derived_snapshot(
    project: Path,
    runtime: Path,
    final_mix: Path,
) -> tuple[Any, Path, Any, Path, Mapping[str, Path]]:
    bundle = collect_v4_release(
        project,
        RELEASE_ID,
        runtime_root=runtime,
        created_at="2026-08-01T01:00:00Z",
    )
    mix_binding = ArtifactBinding(
        asset_id="final-mix",
        role="final_audio_mix",
        ref=PortableRef("project", final_mix.relative_to(project).as_posix()),
        bytes=final_mix.stat().st_size,
        sha256=_sha256(final_mix),
        media_type="audio/wav",
        source_manifest_artifact_id="phase4a:generated-final-mix",
        rights_ref="fixture:program-generated-final-mix",
    )
    audio_manifest_payload = {
        "schema_version": "1.0",
        "release_id": RELEASE_ID,
        "final_mix": {
            "asset_id": mix_binding.asset_id,
            "ref": {"root": mix_binding.ref.root, "path": mix_binding.ref.path},
            "bytes": mix_binding.bytes,
            "sha256": mix_binding.sha256,
            "media_type": mix_binding.media_type,
        },
        "generator": "python-wave-phase4a-fixture",
        "production_use": False,
    }
    audio_manifest = write_canonical_once(
        project / "manifests" / "releases" / "phase4a" / "final-mix-manifest.json",
        audio_manifest_payload,
    )
    audio_source = {
        "id": "phase4a-final-mix-manifest",
        "version": "1.0",
        "ref": {
            "root": "project",
            "path": audio_manifest.relative_to(project).as_posix(),
        },
        "sha256": _sha256(audio_manifest),
    }
    snapshot = create_release_snapshot(
        project_id=bundle.snapshot.project_id,
        release_id=RELEASE_ID,
        created_at="2026-08-01T01:00:00Z",
        profile=bundle.snapshot.profile,
        artifacts=(*bundle.snapshot.artifacts, mix_binding),
        timeline_source=bundle.snapshot.timeline_source,
        audio_source=audio_source,
        caption_source=bundle.snapshot.caption_source,
        rights=bundle.snapshot.rights,
        approvals=bundle.snapshot.approvals,
        release_gates=bundle.snapshot.release_gates,
        source_manifests=(*bundle.snapshot.source_manifests, audio_source),
        metadata={
            "created_by": "phase4a-remotion-fixture-adapter-v1",
            "notes": "Phase 3C semantic fixture plus an upstream generated final mix.",
        },
    )
    snapshot_path = write_release_snapshot(
        snapshot, project / "manifests" / "releases" / "phase4a" / "snapshots"
    )
    return (
        snapshot,
        snapshot_path,
        bundle.snapshot,
        bundle.snapshot_path,
        bundle.root_bindings,
    )


def _retarget_request(
    snapshot: Any,
    snapshot_path: Path,
    compatibility_snapshot: Any,
    compatibility_snapshot_path: Path,
    project: Path,
    runtime: Path,
    renderer_project: Path,
    root_bindings: Mapping[str, Path],
    *,
    mode: RenderMode,
) -> tuple[Any, RootResolver]:
    bindings = {**root_bindings, "remotion_renderer": renderer_project.resolve()}
    resolver = RootResolver(bindings)
    compatibility_ref = PortableRef(
        "project", compatibility_snapshot_path.relative_to(project).as_posix()
    )
    legacy = map_v4_snapshot_to_request(
        compatibility_snapshot,
        compatibility_ref,
        resolver,
        created_at="2026-08-01T01:00:00Z",
    )
    payload = render_request_to_dict(legacy)
    payload["release"] = {
        "id": snapshot.release_id,
        "manifest_id": snapshot.snapshot_id,
        "manifest_version": "1.0",
        "manifest_ref": {
            "root": "project",
            "path": snapshot_path.relative_to(project).as_posix(),
        },
        "manifest_sha256": snapshot.snapshot_hash,
    }
    final_mix_binding = next(
        item for item in snapshot.artifacts if item.asset_id == "final-mix"
    )
    payload["assets"].append(
        {
            "asset_id": final_mix_binding.asset_id,
            "role": final_mix_binding.role,
            "ref": {
                "root": final_mix_binding.ref.root,
                "path": final_mix_binding.ref.path,
            },
            "bytes": final_mix_binding.bytes,
            "sha256": final_mix_binding.sha256,
            "media_type": final_mix_binding.media_type,
            "source_manifest_artifact_id": final_mix_binding.source_manifest_artifact_id,
            "rights_ref": final_mix_binding.rights_ref,
        }
    )
    capability_path = renderer_project / "config" / "renderer-capabilities.json"
    required_capabilities = [
        "still_images",
        "captions",
        "audio_playback",
        "deterministic_render",
    ]
    if mode is RenderMode.PREVIEW:
        required_capabilities.append("preview")
    payload["renderer"] = {
        "id": REMOTION_RENDERER_ID,
        "version": REMOTION_RENDERER_VERSION,
        "capability_document_ref": {
            "root": "remotion_renderer",
            "path": "config/renderer-capabilities.json",
        },
        "capability_document_sha256": _sha256(capability_path),
        "required_capabilities": required_capabilities,
    }
    payload["roots"]["remotion_renderer"] = {
        "kind": "artifact",
        "input_access": "read_only",
        "output_access": "none",
    }
    payload["render_mode"] = mode.value
    payload["rights"]["scope"] = mode.value
    payload["output_spec"]["video"]["encoding_policy"] = "remotion-h264-v1"
    role = "preview_video" if mode is RenderMode.PREVIEW else "local_experimental_master"
    payload["output_spec"]["artifact_role"] = role
    output_name = "preview.mp4" if mode is RenderMode.PREVIEW else "final-experimental.mp4"
    payload["output"] = {
        "artifact_id": "remotion-preview" if mode is RenderMode.PREVIEW else "remotion-final",
        "role": role,
        "target": {
            "root": "project",
            "path": f"08_render_合成/remotion/{mode.value}/{output_name}",
        },
        "overwrite_policy": "fail_if_exists",
    }
    for segment in payload["timeline"]["segments"]:
        visual_ids = list(segment["visual"]["asset_ids"])
        segment["visual"] = {
            "kind": "still",
            "asset_ids": visual_ids[:1],
            "motion": "none",
        }
        segment["overlay_ids"] = []
        segment["transition"] = {"in": "cut", "out": "cut"}
    payload["overlays"] = []
    payload["audio"]["final_mix_asset_id"] = "final-mix"
    payload["audio"]["stem_usage"] = "visual_analysis_only"
    payload["audio"]["mix_policy_id"] = "phase4a-generated-final-mix-v1"
    for track in payload["captions"]["tracks"]:
        track["style"]["font_asset_id"] = "font-english"
        track["style"]["font_role"] = "caption-latin-fixture"
        track["style"]["max_lines"] = 2
        track["style"]["line_break_policy"] = "contract-two-line-v1"
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
            "visual_policy": "one_still_per_segment_v1",
            "caption_policy": "sentence_two_line_v1",
            "rights_holds": [RIGHTS_HOLD],
        }
    }
    payload["metadata"] = {
        "created_at": "2026-08-01T01:00:00Z",
        "created_by": "phase4a-remotion-request-adapter-v1",
        "notes": "Experimental, non-production renderer Request.",
    }
    payload["request_hash"] = "0" * 64
    payload["request_id"] = "pending"
    digest = semantic_request_hash(payload)
    payload["request_hash"] = digest
    payload["request_id"] = request_id_from_hash(digest)
    return render_request_from_dict(payload), resolver


def _composition_discovery(renderer_project: Path, props_path: Path) -> dict[str, Any]:
    command = [
        "node",
        str(renderer_project / "scripts" / "list-compositions.mjs"),
        str(props_path),
    ]
    completed = subprocess.run(
        command,
        cwd=renderer_project,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=dict(os.environ),
    )
    return {
        "argv": command,
        "cwd": str(renderer_project),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "composition_found": REMOTION_COMPOSITION_ID in (completed.stdout or ""),
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
        raise SmokeFixtureError("external QC handoff Request hash mismatch")
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
        "adapter": "phase4a-remotion-technical-qc-v1",
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
        project / "09_qc_质检" / "remotion" / result.attempt_id / "technical-qc.json",
        report,
    )
    return {"path": str(path), "report": report}


def _media_contract_comparison(
    request: Any, detailed_probe: Mapping[str, Any]
) -> dict[str, Any]:
    expected = int(request.output_spec["duration_ticks"])
    fps = request.output_spec["fps"]
    frame_tolerance = (
        1000 * int(fps["denominator"]) + int(fps["numerator"]) - 1
    ) // int(fps["numerator"]) + 1
    aac_frame_tolerance = (
        1024 * 1000 + int(request.output_spec["audio"]["sample_rate"]) - 1
    ) // int(request.output_spec["audio"]["sample_rate"])
    approved_audio_tolerance = frame_tolerance + aac_frame_tolerance
    video_ticks = int(Decimal(str(detailed_probe["video"]["duration"])) * 1000)
    audio_ticks = int(Decimal(str(detailed_probe["audio"]["duration"])) * 1000)
    container_ticks = int(Decimal(str(detailed_probe["format_duration"])) * 1000)
    checks = {
        "video_duration_within_one_frame": abs(video_ticks - expected) <= frame_tolerance,
        "audio_duration_within_frame_plus_aac_packet": abs(audio_ticks - expected)
        <= approved_audio_tolerance,
        "container_duration_within_frame_plus_aac_packet": abs(container_ticks - expected)
        <= approved_audio_tolerance,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "expected_duration_ticks": expected,
        "video_duration_ticks": video_ticks,
        "audio_duration_ticks": audio_ticks,
        "container_duration_ticks": container_ticks,
        "video_frame_tolerance_ticks": frame_tolerance,
        "aac_frame_tolerance_ticks": aac_frame_tolerance,
        "approved_audio_tolerance_ticks": approved_audio_tolerance,
        "basis": "one video frame plus one 1024-sample AAC frame",
    }


def run_experiment(fixture_root: Path, renderer_project: Path) -> dict[str, Any]:
    root = Path(fixture_root).expanduser().resolve()
    marker = validate_fixture_root(root)
    renderer = Path(renderer_project).expanduser().resolve()
    if not (renderer / "package-lock.json").is_file():
        raise SmokeFixtureError("renderer project or lockfile is missing")
    runtime = _runtime_root()
    shared, shared_record = _shared_assets(root)
    project, semantic = _create_project(root, shared, "fixture-remotion-contract")
    _record_phase4a_approvals(project)
    final_mix = _final_mix(project)
    (
        snapshot,
        snapshot_path,
        compatibility_snapshot,
        compatibility_snapshot_path,
        root_bindings,
    ) = _derived_snapshot(
        project, runtime, final_mix
    )
    font_env, font_hashes = _font_environment(runtime)
    environment = dict(os.environ)
    environment.update(font_env)
    results: dict[str, Any] = {}
    for mode in (RenderMode.PREVIEW, RenderMode.FINAL):
        request, resolver = _retarget_request(
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
        request_path = write_render_request(request, project / "manifests" / "requests")
        fixture_token = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:8]
        attempt_id = f"phase4a-remotion-{mode.value}-{fixture_token}"
        context = RenderExecutionContext(
            resolver=resolver,
            attempts_directory=project / "08_render_合成" / "attempts",
            attempt_id=attempt_id,
            environment=environment,
        )
        result = RemotionContractRenderer(renderer).render(request, context)
        if result.status is not RenderStatus.SUCCEEDED:
            raise SmokeFixtureError(
                f"Remotion {mode.value} failed with {result.primary_error_code}; evidence retained"
            )
        props_path = renderer / "public" / "attempts" / attempt_id / "props.json"
        discovery = _composition_discovery(renderer, props_path)
        if discovery["returncode"] != 0 or not discovery["composition_found"]:
            raise SmokeFixtureError("Remotion composition discovery failed")
        output_path = resolver.resolve(result.output[0].ref, require_exists=True)
        detailed_probe = _probe(output_path)
        media_comparison = _media_contract_comparison(request, detailed_probe)
        if not media_comparison["passed"]:
            raise SmokeFixtureError("Remotion media duration exceeds approved technical tolerance")
        qc = _external_qc(project, request, result, resolver, media_comparison)
        results[mode.value] = {
            "request": {
                "id": request.request_id,
                "hash": request.request_hash,
                "path": str(request_path),
            },
            "attempt_id": attempt_id,
            "result": render_result_to_dict(result),
            "result_path": str(
                context.attempts_directory / attempt_id / "render-result-v1.json"
            ),
            "output": str(output_path),
            "detailed_probe": detailed_probe,
            "media_contract_comparison": media_comparison,
            "composition_discovery": discovery,
            "external_qc": qc,
            "props_path": str(props_path),
        }
    final_result = results["final"]["result"]
    final_qc = results["final"]["external_qc"]["report"]
    passed = (
        results["preview"]["external_qc"]["report"]["technical_status"] == "pass"
        and final_qc["technical_status"] == "pass"
        and final_qc["public_release_allowed"] is False
        and RIGHTS_HOLD in final_qc["release_holds"]
        and final_result["qc_handoff"]["request_hash"]
        == results["final"]["request"]["hash"]
    )
    report = {
        "schema_version": "1.0",
        "fixture": marker,
        "renderer": {
            "id": REMOTION_RENDERER_ID,
            "version": REMOTION_RENDERER_VERSION,
            "composition_id": REMOTION_COMPOSITION_ID,
            "project": str(renderer),
        },
        "release_snapshot": {
            "id": snapshot.snapshot_id,
            "hash": snapshot.snapshot_hash,
            "path": str(snapshot_path),
        },
        "shared_assets": shared_record,
        "semantic_input_hashes": semantic,
        "final_mix": {
            "path": str(final_mix),
            "bytes": final_mix.stat().st_size,
            "sha256": _sha256(final_mix),
        },
        "font_hashes": font_hashes,
        "preview": results["preview"],
        "final": results["final"],
        "scope": {
            "provider_calls": 0,
            "network_asset_calls": 0,
            "external_assets": 0,
            "audio_mixing_inside_renderer": False,
            "legacy_modified": False,
            "default_renderer_changed": False,
        },
        "passed": passed,
    }
    report_path = _write_json(root / "phase-4a-experiment-report.json", report)
    summary_path = root / "phase-4a-experiment-report.md"
    summary_path.write_text(
        "\n".join(
            [
                "# Phase 4A Remotion Contract Experiment",
                "",
                f"- Result: {'PASS' if passed else 'FAIL'}",
                f"- Renderer: {REMOTION_RENDERER_ID} {REMOTION_RENDERER_VERSION}",
                f"- Preview: {results['preview']['result']['status']}",
                f"- Final: {results['final']['result']['status']}",
                f"- Final SHA-256: `{results['final']['detailed_probe']['sha256']}`",
                f"- Technical QC: {final_qc['technical_status']}",
                f"- Public release allowed: {str(final_qc['public_release_allowed']).lower()}",
                f"- Rights hold: {RIGHTS_HOLD}",
                "",
                "The adjacent JSON document is the authoritative machine-readable report.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    report["report_path"] = str(report_path)
    report["human_report_path"] = str(summary_path)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4A test-only Remotion Renderer Contract experiment"
    )
    parser.add_argument("--fixture-dir", type=Path, required=True)
    parser.add_argument("--renderer-project", type=Path, required=True)
    parser.add_argument("--initialize-only", action="store_true")
    parser.add_argument("--keep-artifacts", action="store_true")
    args = parser.parse_args()
    try:
        if args.initialize_only:
            marker = initialize_fixture_root(args.fixture_dir)
            print(json.dumps({"initialized": True, "marker": str(marker)}, ensure_ascii=False))
            return 0
        result = run_experiment(args.fixture_dir, args.renderer_project)
    except SmokeFixtureError as error:
        print(json.dumps({"passed": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(
        json.dumps(
            {
                "passed": result["passed"],
                "report": result["report_path"],
                "human_report": result["human_report_path"],
                "preview_sha256": result["preview"]["detailed_probe"]["sha256"],
                "final_sha256": result["final"]["detailed_probe"]["sha256"],
                "public_release_allowed": result["final"]["external_qc"]["report"]["public_release_allowed"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
