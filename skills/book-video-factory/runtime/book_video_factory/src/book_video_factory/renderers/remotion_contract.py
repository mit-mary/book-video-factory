"""Experimental Remotion facade for Renderer Contract v1.

The Python runtime remains authoritative. Remotion receives only write-once staged
assets and a sanitized props document for one Attempt.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

from book_video_factory.renderer_contracts import (
    ArtifactBinding,
    CommandResult,
    FFprobeMediaProbe,
    PortableRef,
    RenderExecutionContext,
    RenderRequest,
    RendererErrorCode,
    RendererIdentity,
    RenderResult,
    RenderStatus,
    capabilities_from_dict,
    stable_issues,
    validate_capabilities,
    validate_render_request,
    validate_request_capabilities,
    validate_request_filesystem,
    validate_request_hash,
    write_attempt_event,
    write_canonical_once,
    write_render_result,
)
from book_video_factory.renderer_contracts.errors import ContractValidationError, RenderIssue
from book_video_factory.renderer_contracts.paths import PortablePathError


REMOTION_RENDERER_ID = "remotion-contract-conformance-v1"
REMOTION_RENDERER_VERSION = "0.2.0-experimental"
REMOTION_EXTENSION = "io.github.mit-mary.book-video-factory.remotion"
REMOTION_COMPOSITION_ID = "ContractConformanceV1"
PAPER_COLLAGE_COMPOSITION_ID = "PaperCollageVisualV1"
PAPER_COLLAGE_TEMPLATE_ID = "paper-collage-visual-v1"
PAPER_COLLAGE_TEMPLATE_VERSION = "0.1.0-experimental"
_SAFE_ATTEMPT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_HEX_COLOR = re.compile(r"^#[0-9A-F]{6}$")
_PAPER_BACKING_OFFSET_X = 9
_PAPER_BACKING_OFFSET_Y = 11
_PAPER_BACKING_ROTATION_FACTOR = 0.55
_PAPER_CAPTION_OUTLINE = 2
_PAPER_CAPTION_SHADOW_X = 7
_PAPER_CAPTION_SHADOW_Y = 9
_MIN_RENDERED_IMAGE_CARD = 240
_IMAGE_CAPTION_GAP = 24
_SEGMENT_MARKER_HEIGHT = 30


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _issue(
    code: RendererErrorCode,
    message: str,
    field: str,
    *,
    stage: str,
    details: Mapping[str, Any] | None = None,
) -> RenderIssue:
    return RenderIssue(code, message, field, details or {}, stage)


def _portable(project: Path, path: Path) -> PortableRef:
    try:
        relative = path.resolve().relative_to(project.resolve())
    except ValueError as error:
        raise PortablePathError("attempt artifact is outside the project root") from error
    return PortableRef("project", relative.as_posix())


def _artifact(
    project: Path,
    path: Path,
    *,
    asset_id: str,
    role: str,
    media_type: str,
) -> ArtifactBinding:
    return ArtifactBinding(
        asset_id=asset_id,
        role=role,
        ref=_portable(project, path),
        bytes=path.stat().st_size,
        sha256=_sha256(path),
        media_type=media_type,
    )


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value


def _round_frame(ticks: int, fps: int) -> int:
    return (ticks * fps * 2 + 1000) // 2000


def _exact_keys(value: Mapping[str, Any], expected: set[str], field: str) -> None:
    if set(value) != expected:
        raise ValueError(f"{field} contains missing or unknown fields")


def _integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer")
    return value


def _paper_theme_from_dict(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("theme must be an object")
    _exact_keys(
        value,
        {"schema_version", "canvas", "paper_texture", "image_card", "caption", "motion", "transition"},
        "theme",
    )
    if value.get("schema_version") != "paper-collage-theme-v1":
        raise ValueError("unsupported theme schema")
    sections = {
        "canvas": {"background", "ink", "accent", "safe_margin_x", "safe_margin_top", "safe_margin_bottom"},
        "paper_texture": {"asset_id", "opacity_milli"},
        "image_card": {"max_width", "max_height", "padding", "border_width", "shadow_offset_x", "shadow_offset_y", "rotation_millidegrees"},
        "caption": {"max_lines", "font_size", "line_height_milli", "padding_x", "padding_y", "background", "text"},
        "motion": {"max_scale_delta_milli", "max_translate_x", "max_translate_y", "max_rotation_millidegrees"},
        "transition": {"duration_frames", "max_translate_px"},
    }
    parsed: dict[str, Any] = {"schema_version": "paper-collage-theme-v1"}
    for section, keys in sections.items():
        item = value.get(section)
        if not isinstance(item, Mapping):
            raise ValueError(f"theme.{section} must be an object")
        _exact_keys(item, keys, f"theme.{section}")
        parsed[section] = dict(item)
    for field in ("background", "ink", "accent"):
        if not isinstance(parsed["canvas"][field], str) or _HEX_COLOR.fullmatch(parsed["canvas"][field]) is None:
            raise ValueError(f"theme.canvas.{field} must be an uppercase hex color")
    for field in ("background", "text"):
        if not isinstance(parsed["caption"][field], str) or _HEX_COLOR.fullmatch(parsed["caption"][field]) is None:
            raise ValueError(f"theme.caption.{field} must be an uppercase hex color")
    integer_fields = {
        "canvas": ("safe_margin_x", "safe_margin_top", "safe_margin_bottom"),
        "paper_texture": ("opacity_milli",),
        "image_card": ("max_width", "max_height", "padding", "border_width", "shadow_offset_x", "shadow_offset_y", "rotation_millidegrees"),
        "caption": ("max_lines", "font_size", "line_height_milli", "padding_x", "padding_y"),
        "motion": ("max_scale_delta_milli", "max_translate_x", "max_translate_y", "max_rotation_millidegrees"),
        "transition": ("duration_frames", "max_translate_px"),
    }
    for section, fields in integer_fields.items():
        for field in fields:
            parsed[section][field] = _integer(parsed[section][field], f"theme.{section}.{field}")
    canvas = parsed["canvas"]
    image = parsed["image_card"]
    caption = parsed["caption"]
    motion = parsed["motion"]
    transition = parsed["transition"]
    texture = parsed["paper_texture"]
    if not (48 <= canvas["safe_margin_x"] <= 160 and 48 <= canvas["safe_margin_top"] <= 180 and 64 <= canvas["safe_margin_bottom"] <= 200):
        raise ValueError("canvas safety token is outside the approved range")
    if not (240 <= image["max_width"] <= 1200 and 240 <= image["max_height"] <= 1600 and 8 <= image["padding"] <= 40 and 1 <= image["border_width"] <= 6 and abs(image["shadow_offset_x"]) <= 24 and abs(image["shadow_offset_y"]) <= 24 and abs(image["rotation_millidegrees"]) <= 3000):
        raise ValueError("image-card token is outside the approved range")
    if not (caption["max_lines"] == 2 and 28 <= caption["font_size"] <= 64 and 1000 <= caption["line_height_milli"] <= 1500 and 16 <= caption["padding_x"] <= 56 and 12 <= caption["padding_y"] <= 36):
        raise ValueError("caption token is outside the approved range")
    if not (0 <= motion["max_scale_delta_milli"] <= 40 and abs(motion["max_translate_x"]) <= 20 and abs(motion["max_translate_y"]) <= 16 and abs(motion["max_rotation_millidegrees"]) <= 500):
        raise ValueError("motion token is outside the approved range")
    if not (1 <= transition["duration_frames"] <= 8 and abs(transition["max_translate_px"]) <= 20 and 0 <= texture["opacity_milli"] <= 250):
        raise ValueError("transition or texture token is outside the approved range")
    if not isinstance(texture["asset_id"], str) or not texture["asset_id"]:
        raise ValueError("paper texture asset ID is invalid")
    return parsed


def _paper_layout(
    width: int,
    height: int,
    theme: Mapping[str, Any],
    safe_area: Mapping[str, Any],
    captions: Sequence[str],
) -> dict[str, dict[str, int]]:
    canvas = theme["canvas"]
    image = theme["image_card"]
    caption = theme["caption"]
    line_height = (caption["font_size"] * caption["line_height_milli"] + 999) // 1000
    caption_height = line_height * 2 + caption["padding_y"] * 2
    caption_right_extent = max(_PAPER_CAPTION_OUTLINE, _PAPER_CAPTION_SHADOW_X)
    caption_bottom_extent = max(_PAPER_CAPTION_OUTLINE, _PAPER_CAPTION_SHADOW_Y)
    caption_box = {
        "x": canvas["safe_margin_x"] + _PAPER_CAPTION_OUTLINE,
        "y": height - canvas["safe_margin_bottom"] - caption_height - caption_bottom_extent,
        "width": width - canvas["safe_margin_x"] * 2 - _PAPER_CAPTION_OUTLINE - caption_right_extent,
        "height": caption_height,
    }
    caption_envelope = {
        "x": caption_box["x"] - _PAPER_CAPTION_OUTLINE,
        "y": caption_box["y"] - _PAPER_CAPTION_OUTLINE,
        "width": caption_box["width"] + _PAPER_CAPTION_OUTLINE + caption_right_extent,
        "height": caption_box["height"] + _PAPER_CAPTION_OUTLINE + caption_bottom_extent,
    }
    safe_width = width - canvas["safe_margin_x"] * 2
    image_region_bottom = caption_box["y"] - _IMAGE_CAPTION_GAP
    available_image_height = image_region_bottom - canvas["safe_margin_top"]
    desired_width = min(image["max_width"], safe_width)
    desired_height = min(image["max_height"], available_image_height)

    def envelope_for(box: Mapping[str, int]) -> dict[str, int]:
        border = image["border_width"]
        center_x = box["x"] + box["width"] / 2
        center_y = box["y"] + box["height"] / 2
        local_min_x = min(-border, image["shadow_offset_x"])
        local_max_x = max(box["width"] + border, box["width"] + image["shadow_offset_x"])
        local_min_y = min(-border, image["shadow_offset_y"])
        local_max_y = max(box["height"] + border, box["height"] + image["shadow_offset_y"])
        local_half_width = max(
            abs(local_min_x - box["width"] / 2),
            abs(local_max_x - box["width"] / 2),
        )
        local_half_height = max(
            abs(local_min_y - box["height"] / 2),
            abs(local_max_y - box["height"] / 2),
        )
        scale = 1 + theme["motion"]["max_scale_delta_milli"] / 1000
        radians = math.radians(
            (
                abs(image["rotation_millidegrees"])
                + abs(theme["motion"]["max_rotation_millidegrees"]) / 2
            )
            / 1000
        )
        cosine = math.cos(radians)
        sine = math.sin(radians)
        half_width = math.ceil(
            scale * (local_half_width * cosine + local_half_height * sine)
            + abs(theme["motion"]["max_translate_x"])
            + abs(theme["transition"]["max_translate_px"])
        )
        half_height = math.ceil(
            scale * (local_half_width * sine + local_half_height * cosine)
            + abs(theme["motion"]["max_translate_y"])
        )
        main_left = math.floor(center_x - half_width)
        main_top = math.floor(center_y - half_height)
        main_right = math.ceil(center_x + half_width)
        main_bottom = math.ceil(center_y + half_height)
        backing_radians = math.radians(
            abs(image["rotation_millidegrees"]) / 1000
            * _PAPER_BACKING_ROTATION_FACTOR
        )
        backing_half_width = math.ceil(
            box["width"] / 2 * math.cos(backing_radians)
            + box["height"] / 2 * math.sin(backing_radians)
        )
        backing_half_height = math.ceil(
            box["width"] / 2 * math.sin(backing_radians)
            + box["height"] / 2 * math.cos(backing_radians)
        )
        backing_center_x = center_x + _PAPER_BACKING_OFFSET_X
        backing_center_y = center_y + _PAPER_BACKING_OFFSET_Y
        left = min(main_left, math.floor(backing_center_x - backing_half_width))
        top = min(main_top, math.floor(backing_center_y - backing_half_height))
        right = max(main_right, math.ceil(backing_center_x + backing_half_width))
        bottom = max(main_bottom, math.ceil(backing_center_y + backing_half_height))
        return {"x": left, "y": top, "width": right - left, "height": bottom - top}

    image_box: dict[str, int] | None = None
    image_envelope: dict[str, int] | None = None
    for permille in range(1000, 0, -1):
        candidate_width = desired_width * permille // 1000
        candidate_height = desired_height * permille // 1000
        if candidate_width < _MIN_RENDERED_IMAGE_CARD or candidate_height < _MIN_RENDERED_IMAGE_CARD:
            break
        candidate = {
            "x": (width - candidate_width) // 2,
            "y": canvas["safe_margin_top"] + (available_image_height - candidate_height) // 2,
            "width": candidate_width,
            "height": candidate_height,
        }
        envelope = envelope_for(candidate)
        if (
            envelope["x"] >= canvas["safe_margin_x"]
            and envelope["y"] >= canvas["safe_margin_top"]
            and envelope["x"] + envelope["width"] <= width - canvas["safe_margin_x"]
            and envelope["y"] + envelope["height"] <= image_region_bottom
            and candidate["y"] + candidate["height"] + 12 + _SEGMENT_MARKER_HEIGHT <= caption_box["y"]
        ):
            image_box = candidate
            image_envelope = envelope
            break

    def within(box: Mapping[str, int]) -> bool:
        return (
            box["x"] >= canvas["safe_margin_x"]
            and box["y"] >= canvas["safe_margin_top"]
            and box["x"] + box["width"] <= width - canvas["safe_margin_x"]
            and box["y"] + box["height"] <= height - canvas["safe_margin_bottom"]
        )
    if (
        image_box is None
        or image_envelope is None
        or caption_box["width"] <= 0
        or caption_box["height"] <= 0
        or not within(image_box)
        or not within(image_envelope)
        or not within(caption_box)
        or not within(caption_envelope)
        or image_envelope["y"] + image_envelope["height"] > image_region_bottom
    ):
        raise ValueError("paper-collage layout escapes the contract safe area")
    if canvas["safe_margin_x"] < max(int(safe_area["left_px"]), int(safe_area["right_px"])) or canvas["safe_margin_bottom"] < int(safe_area["bottom_px"]):
        raise ValueError("theme cannot bypass the contract caption safe area")
    inner_width = caption_box["width"] - caption["padding_x"] * 2
    capacity = inner_width * 1000 // caption["font_size"]
    def units(text: str) -> int:
        return sum(1000 if ord(character) > 255 else 600 for character in text)
    for text in captions:
        lines = text.split("\n")
        if len(lines) > 2 or any(units(line) > capacity for line in lines) or units("".join(lines)) > capacity * 2:
            raise ValueError("caption exceeds the approved two-line box")
    return {
        "image_card": image_box,
        "image_card_motion_envelope": image_envelope,
        "caption_card": caption_box,
        "caption_card_visual_envelope": caption_envelope,
    }


class RemotionFFprobeMediaProbe:
    """Probe the frame timeline while retaining container and AAC durations."""

    def probe(self, path: Path) -> Mapping[str, Any]:
        completed = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate,pix_fmt,nb_frames,sample_rate,channels,duration",
                "-of",
                "json",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        payload = json.loads(completed.stdout)
        streams = payload.get("streams", [])
        video = next(item for item in streams if item.get("codec_type") == "video")
        audio = next(item for item in streams if item.get("codec_type") == "audio")
        rate = Fraction(str(video["avg_frame_rate"]))
        frame_count = int(video["nb_frames"])
        video_duration = Decimal(str(video.get("duration")))
        audio_duration = Decimal(str(audio.get("duration")))
        container_duration = Decimal(str(payload["format"]["duration"]))
        to_ticks = lambda value: int(
            (value * 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )
        return {
            "duration_ticks": to_ticks(video_duration),
            "container_duration_ticks": to_ticks(container_duration),
            "audio_duration_ticks": to_ticks(audio_duration),
            "video": {
                "codec": str(video["codec_name"]),
                "width": int(video["width"]),
                "height": int(video["height"]),
                "fps": {
                    "numerator": rate.numerator,
                    "denominator": rate.denominator,
                },
                "pixel_format": str(video["pix_fmt"]),
                "frame_count": frame_count,
            },
            "audio": {
                "codec": str(audio["codec_name"]),
                "sample_rate": int(audio["sample_rate"]),
                "channels": int(audio["channels"]),
            },
        }


class RemotionSubprocessCommandRunner:
    """Run Node with an explicit output encoding on localized Windows hosts."""

    def run(
        self,
        command: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
    ) -> CommandResult:
        started = datetime.now(UTC)
        completed = subprocess.run(
            list(command),
            cwd=cwd,
            env=dict(env),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        elapsed = datetime.now(UTC) - started
        return CommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            elapsed_ms=max(0, int(elapsed.total_seconds() * 1000)),
        )


class RemotionContractRenderer:
    def __init__(
        self,
        renderer_project: Path,
        *,
        runner: Any | None = None,
        probe: Any | None = None,
        node_executable: str = "node",
        clock: Any = _utc_now,
    ) -> None:
        self._project = Path(renderer_project).expanduser().resolve()
        self._runner = runner or RemotionSubprocessCommandRunner()
        self._probe = probe or RemotionFFprobeMediaProbe()
        self._node = node_executable
        self._clock = clock

    def _validate_context(self, context: RenderExecutionContext) -> None:
        project = context.resolver.bindings.get("project")
        renderer = context.resolver.bindings.get("remotion_renderer")
        issues: list[RenderIssue] = []
        if project is None or renderer is None or renderer != self._project:
            issues.append(
                _issue(
                    RendererErrorCode.RENDER_INPUT_INVALID,
                    "Execution context requires project and exact remotion_renderer bindings.",
                    "$.execution_context.root_bindings",
                    stage="validate",
                )
            )
        if _SAFE_ATTEMPT.fullmatch(context.attempt_id) is None:
            issues.append(
                _issue(
                    RendererErrorCode.RENDER_INPUT_INVALID,
                    "Attempt ID is not safe for persistent paths.",
                    "$.execution_context.attempt_id",
                    stage="validate",
                )
            )
        if project is not None:
            attempts = Path(context.attempts_directory).expanduser().resolve(strict=False)
            try:
                attempts.relative_to(project)
            except ValueError:
                issues.append(
                    _issue(
                        RendererErrorCode.RENDER_INPUT_INVALID,
                        "Attempt evidence must remain inside the Project root.",
                        "$.execution_context.attempts_directory",
                        stage="validate",
                    )
                )
            if (attempts / context.attempt_id).exists():
                issues.append(
                    _issue(
                        RendererErrorCode.RENDER_INPUT_INVALID,
                        "Write-once Attempt evidence path already exists.",
                        "$.execution_context.attempt_id",
                        stage="validate",
                    )
                )
        staging = self._project / "public" / "attempts" / context.attempt_id
        if staging.exists():
            issues.append(
                _issue(
                    RendererErrorCode.RENDER_INPUT_INVALID,
                    "Write-once Remotion staging path already exists.",
                    "$.execution_context.attempt_id",
                    stage="stage",
                )
            )
        if issues:
            raise ContractValidationError(stable_issues(issues))

    def _capabilities(self, request: RenderRequest, context: RenderExecutionContext) -> Any:
        ref = request.renderer.capability_document_ref
        if ref is None:
            raise ContractValidationError(
                (_issue(RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED, "Capability ref is missing.", "$.renderer.capability_document_ref", stage="negotiate"),)
            )
        issues: list[RenderIssue] = []
        try:
            path = context.resolver.resolve(ref, require_exists=True)
            document = capabilities_from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            raise ContractValidationError(
                (_issue(RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED, "Capability document is unreadable.", "$.renderer.capability_document_ref", stage="negotiate"),)
            ) from error
        issues.extend(validate_capabilities(document))
        if _sha256(path) != request.renderer.capability_document_sha256:
            issues.append(
                _issue(RendererErrorCode.RENDER_HASH_MISMATCH, "Capability document hash changed.", "$.renderer.capability_document_sha256", stage="validate")
            )
        issues.extend(validate_request_capabilities(request, document))
        if issues:
            raise ContractValidationError(stable_issues(issues))
        return document

    def _output_path(self, request: RenderRequest, context: RenderExecutionContext) -> Path:
        target = request.output.get("target")
        if not isinstance(target, Mapping):
            raise PortablePathError("output target is not a portable ref")
        return context.resolver.resolve_output(
            PortableRef(str(target.get("root", "")), str(target.get("path", "")))
        )

    def _paper_theme(
        self, request: RenderRequest, context: RenderExecutionContext
    ) -> tuple[dict[str, Any], ArtifactBinding, ArtifactBinding]:
        extension = request.extensions[REMOTION_EXTENSION]
        assets = {item.asset_id: item for item in request.assets}
        theme_id = str(extension["theme_tokens_asset_id"])
        texture_id = str(extension["texture_asset_id"])
        theme_binding = assets[theme_id]
        texture_binding = assets[texture_id]
        theme_path = context.resolver.resolve(theme_binding.ref, require_exists=True)
        theme = _paper_theme_from_dict(json.loads(theme_path.read_text(encoding="utf-8")))
        if theme_binding.sha256 != extension.get("theme_tokens_sha256"):
            raise ContractValidationError(
                (_issue(RendererErrorCode.RENDER_HASH_MISMATCH, "Theme token hash does not match its Request binding.", f"$.extensions.{REMOTION_EXTENSION}.theme_tokens_sha256", stage="validate"),)
            )
        if texture_binding.sha256 != extension.get("texture_sha256"):
            raise ContractValidationError(
                (_issue(RendererErrorCode.RENDER_HASH_MISMATCH, "Texture hash does not match its Request binding.", f"$.extensions.{REMOTION_EXTENSION}.texture_sha256", stage="validate"),)
            )
        if theme["paper_texture"]["asset_id"] != texture_id:
            raise ValueError("theme texture identity differs from the Request")
        return theme, theme_binding, texture_binding

    def _paper_issues(
        self, request: RenderRequest, context: RenderExecutionContext, extension: Mapping[str, Any]
    ) -> tuple[RenderIssue, ...]:
        field = f"$.extensions.{REMOTION_EXTENSION}"
        issues: list[RenderIssue] = []
        expected = {
            "schema_version", "composition_id", "audio_source", "visual_policy",
            "caption_policy", "rights_holds", "template_id", "template_version",
            "motion_preset", "transition_preset", "caption_preset",
            "theme_tokens_asset_id", "theme_tokens_sha256", "texture_asset_id",
            "texture_sha256", "opening",
        }
        if set(extension) != expected:
            issues.append(_issue(RendererErrorCode.RENDER_INPUT_INVALID, "Paper-collage extension contains missing or unknown fields.", field, stage="validate"))
        if extension.get("template_id") != PAPER_COLLAGE_TEMPLATE_ID or extension.get("template_version") != PAPER_COLLAGE_TEMPLATE_VERSION:
            issues.append(_issue(RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED, "Unknown paper-collage template identity.", f"{field}.template_id", stage="negotiate"))
        if extension.get("motion_preset") != "subtle":
            issues.append(_issue(RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED, "Unsupported motion preset.", f"{field}.motion_preset", stage="negotiate"))
        if extension.get("transition_preset") != "paper-cut":
            issues.append(_issue(RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED, "Unsupported transition preset.", f"{field}.transition_preset", stage="negotiate"))
        if extension.get("caption_preset") != "bottom-card":
            issues.append(_issue(RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED, "Unsupported caption preset.", f"{field}.caption_preset", stage="negotiate"))
        required = set(request.renderer.required_capabilities)
        for capability in ("layered_images", "camera_motion", "transitions"):
            if capability not in required:
                issues.append(_issue(RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED, "Template capability was not requested.", "$.renderer.required_capabilities", stage="negotiate", details={"capability": capability}))
        opening = extension.get("opening")
        if not isinstance(opening, Mapping) or set(opening) != {"start_tick", "end_tick", "title", "subtitle"}:
            issues.append(_issue(RendererErrorCode.RENDER_INPUT_INVALID, "Opening declaration is missing or contains unknown fields.", f"{field}.opening", stage="validate"))
        else:
            start_tick = opening.get("start_tick")
            end_tick = opening.get("end_tick")
            title = opening.get("title")
            subtitle = opening.get("subtitle")
            if not isinstance(start_tick, int) or isinstance(start_tick, bool) or not isinstance(end_tick, int) or isinstance(end_tick, bool) or start_tick != 0 or end_tick - start_tick < 1000 or end_tick - start_tick > 1500 or end_tick > int(request.output_spec["duration_ticks"]):
                issues.append(_issue(RendererErrorCode.RENDER_INPUT_INVALID, "Opening must cover 1.0-1.5 seconds from tick zero.", f"{field}.opening", stage="validate"))
            if not isinstance(title, str) or not title or len(title) > 80 or not isinstance(subtitle, str) or not subtitle or len(subtitle) > 120:
                issues.append(_issue(RendererErrorCode.RENDER_INPUT_INVALID, "Opening uses invalid controlled fixture text.", f"{field}.opening", stage="validate"))
        try:
            theme, _, _ = self._paper_theme(request, context)
            first_track = request.captions["tracks"][0]
            if any(int(track["style"]["max_lines"]) > 2 for track in request.captions["tracks"]):
                raise ValueError("caption max_lines exceeds two")
            _paper_layout(
                int(request.output_spec["width"]),
                int(request.output_spec["height"]),
                theme,
                first_track["style"]["safe_area"],
                tuple(str(cue["text"]) for track in request.captions["tracks"] for cue in track["cues"]),
            )
        except ContractValidationError as error:
            issues.extend(error.issues)
        except KeyError:
            issues.append(_issue(RendererErrorCode.RENDER_ASSET_MISSING, "Theme token or staged texture binding is missing.", f"{field}.theme_tokens_asset_id", stage="validate"))
        except FileNotFoundError:
            issues.append(_issue(RendererErrorCode.RENDER_ASSET_MISSING, "Theme token file is missing.", f"{field}.theme_tokens_asset_id", stage="validate"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            issues.append(_issue(RendererErrorCode.RENDER_INPUT_INVALID, str(error), f"{field}.theme_tokens_asset_id", stage="validate"))
        return stable_issues(issues)

    def validate(
        self, request: RenderRequest, context: RenderExecutionContext
    ) -> tuple[RenderIssue, ...]:
        issues: list[RenderIssue] = [
            *validate_render_request(request),
            *validate_request_hash(request),
            *validate_request_filesystem(request, context.resolver),
        ]
        if (
            request.renderer.id != REMOTION_RENDERER_ID
            or request.renderer.version != REMOTION_RENDERER_VERSION
        ):
            issues.append(
                _issue(RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED, "Request does not select the experimental Remotion renderer.", "$.renderer", stage="negotiate")
            )
        try:
            self._capabilities(request, context)
        except ContractValidationError as error:
            issues.extend(error.issues)
        extension = request.extensions.get(REMOTION_EXTENSION)
        if not isinstance(extension, Mapping):
            issues.append(_issue(RendererErrorCode.RENDER_INPUT_INVALID, "Remotion extension is missing.", f"$.extensions.{REMOTION_EXTENSION}", stage="validate"))
        else:
            composition_id = extension.get("composition_id")
            if extension.get("schema_version") != "1.0" or composition_id not in {REMOTION_COMPOSITION_ID, PAPER_COLLAGE_COMPOSITION_ID}:
                issues.append(_issue(RendererErrorCode.RENDER_INPUT_INVALID, "Remotion extension identity is invalid.", f"$.extensions.{REMOTION_EXTENSION}", stage="validate"))
            if extension.get("audio_source") != "final_mix_only":
                issues.append(_issue(RendererErrorCode.RENDER_AUDIO_INVALID, "Remotion renderer only consumes final_mix.", f"$.extensions.{REMOTION_EXTENSION}.audio_source", stage="validate"))
            if composition_id == PAPER_COLLAGE_COMPOSITION_ID:
                issues.extend(self._paper_issues(request, context, extension))
        if request.audio.get("stem_usage") == "legacy_audio_mixing":
            issues.append(_issue(RendererErrorCode.RENDER_AUDIO_INVALID, "Remotion must not consume the legacy stem-mixing policy.", "$.audio.stem_usage", stage="validate"))
        for dimension in ("width", "height"):
            value = request.output_spec.get(dimension)
            if isinstance(value, int) and value % 2 != 0:
                issues.append(
                    _issue(
                        RendererErrorCode.RENDER_INPUT_INVALID,
                        "H.264 output dimensions must be even; silent rounding is forbidden.",
                        f"$.output_spec.{dimension}",
                        stage="validate",
                    )
                )
        for index, segment in enumerate(request.timeline.get("segments", ())):
            visual = segment.get("visual") if isinstance(segment, Mapping) else None
            if not isinstance(visual, Mapping) or visual.get("kind") != "still" or len(visual.get("asset_ids", ())) > 1:
                issues.append(_issue(RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED, "Experiment supports one still image per segment.", f"$.timeline.segments[{index}].visual", stage="negotiate"))
        if request.overlays:
            issues.append(_issue(RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED, "Experiment does not support overlays.", "$.overlays", stage="negotiate"))
        try:
            output = self._output_path(request, context)
            if output.exists():
                issues.append(_issue(RendererErrorCode.RENDER_INPUT_INVALID, "Write-once output target already exists.", "$.output.target", stage="validate"))
        except (KeyError, PortablePathError):
            issues.append(_issue(RendererErrorCode.RENDER_INPUT_INVALID, "Output target is invalid.", "$.output.target", stage="validate"))
        return stable_issues(issues)

    def _input_hashes(self, request: RenderRequest) -> dict[str, str]:
        hashes = {
            "request": request.request_hash,
            "release_snapshot": request.release.manifest_sha256,
            "release_profile": request.profile.sha256,
            "renderer_capabilities": request.renderer.capability_document_sha256,
        }
        hashes.update({item.asset_id: item.sha256 for item in request.assets})
        return hashes

    def _event(
        self,
        request: RenderRequest,
        context: RenderExecutionContext,
        index: int,
        status: RenderStatus,
        recorded_at: str,
    ) -> None:
        write_attempt_event(
            {
                "schema_version": "1.0",
                "request_id": request.request_id,
                "request_hash": request.request_hash,
                "attempt_id": context.attempt_id,
                "event_index": index,
                "status": status.value,
                "recorded_at": recorded_at,
            },
            context.attempts_directory,
        )

    def _terminal_result(
        self,
        request: RenderRequest,
        context: RenderExecutionContext,
        *,
        status: RenderStatus,
        started_at: str,
        errors: tuple[RenderIssue, ...] = (),
        output: tuple[ArtifactBinding, ...] = (),
        sidecars: tuple[ArtifactBinding, ...] = (),
        media_probe: Mapping[str, Any] | None = None,
        metrics: Mapping[str, int] | None = None,
        qc_handoff: Mapping[str, Any] | None = None,
        logs: tuple[Mapping[str, Any], ...] = (),
        extension_details: Mapping[str, Any] | None = None,
    ) -> RenderResult:
        finished_at = self._clock()
        output_hashes = {item.asset_id: item.sha256 for item in (*output, *sidecars)}
        result = RenderResult(
            schema_version="1.0",
            request_id=request.request_id,
            request_hash=request.request_hash,
            attempt_id=context.attempt_id,
            status=status,
            renderer=RendererIdentity(
                request.renderer.id,
                request.renderer.version,
                request.renderer.capability_document_sha256,
            ),
            started_at=started_at,
            finished_at=finished_at,
            output=output,
            sidecars=sidecars,
            media_probe=media_probe,
            warnings=(),
            errors=tuple(item.to_dict() for item in errors),
            primary_error_code=errors[0].code.value if errors else None,
            metrics=metrics or {},
            input_hashes=self._input_hashes(request),
            output_hashes=output_hashes,
            qc_handoff=qc_handoff,
            logs=logs,
            extensions={
                REMOTION_EXTENSION: {
                    "schema_version": "1.0",
                    "post_qc_invoked": False,
                    **(dict(extension_details or {})),
                }
            },
        )
        write_render_result(result, context.attempts_directory)
        self._event(request, context, 2, status, finished_at)
        return result

    def _failed(
        self,
        request: RenderRequest,
        context: RenderExecutionContext,
        issues: tuple[RenderIssue, ...],
        started_at: str,
        *,
        metrics: Mapping[str, int] | None = None,
        logs: tuple[Mapping[str, Any], ...] = (),
    ) -> RenderResult:
        blocked = {
            RendererErrorCode.RENDER_CAPABILITY_UNSUPPORTED,
            RendererErrorCode.RENDER_GATE_BLOCKED,
            RendererErrorCode.RENDER_RIGHTS_BLOCKED,
        }
        status = RenderStatus.BLOCKED if issues and issues[0].code in blocked else RenderStatus.FAILED
        return self._terminal_result(
            request,
            context,
            status=status,
            started_at=started_at,
            errors=issues,
            metrics=metrics,
            logs=logs,
        )

    def _required_stage_assets(self, request: RenderRequest) -> tuple[str, ...]:
        asset_ids: set[str] = set()
        for segment in request.timeline["segments"]:
            asset_ids.update(str(item) for item in segment["visual"]["asset_ids"])
        asset_ids.add(str(request.audio["final_mix_asset_id"]))
        for track in request.captions["tracks"]:
            asset_ids.add(str(track["style"]["font_asset_id"]))
        extension = request.extensions.get(REMOTION_EXTENSION)
        if isinstance(extension, Mapping) and extension.get("composition_id") == PAPER_COLLAGE_COMPOSITION_ID:
            asset_ids.add(str(extension["theme_tokens_asset_id"]))
            asset_ids.add(str(extension["texture_asset_id"]))
        return tuple(sorted(asset_ids))

    def _stage_assets(
        self,
        request: RenderRequest,
        context: RenderExecutionContext,
        attempt_dir: Path,
    ) -> tuple[Path, dict[str, str], Path, Path]:
        staging = self._project / "public" / "attempts" / context.attempt_id
        assets_dir = staging / "assets"
        staging.mkdir(parents=True, exist_ok=False)
        assets_dir.mkdir()
        assets = {item.asset_id: item for item in request.assets}
        public_refs: dict[str, str] = {}
        records: list[dict[str, Any]] = []
        for asset_id in self._required_stage_assets(request):
            binding = assets[asset_id]
            source = context.resolver.resolve(binding.ref, require_exists=True)
            suffix = source.suffix.lower() or ".bin"
            filename = f"{asset_id}{suffix}"
            target = assets_dir / filename
            with source.open("rb") as reader, target.open("xb") as writer:
                for chunk in iter(lambda: reader.read(1024 * 1024), b""):
                    writer.write(chunk)
            actual = _sha256(target)
            if actual != binding.sha256 or target.stat().st_size != binding.bytes:
                raise ContractValidationError(
                    (_issue(RendererErrorCode.RENDER_HASH_MISMATCH, "Staged asset differs from its frozen binding.", "$.assets", stage="stage", details={"asset_id": asset_id}),)
                )
            public_ref = f"attempts/{context.attempt_id}/assets/{filename}"
            public_refs[asset_id] = public_ref
            records.append(
                {
                    "asset_id": asset_id,
                    "public_ref": public_ref,
                    "bytes": target.stat().st_size,
                    "sha256": actual,
                }
            )
        manifest = {
            "schema_version": "1.0",
            "request_id": request.request_id,
            "request_hash": request.request_hash,
            "attempt_id": context.attempt_id,
            "write_once": True,
            "assets": records,
        }
        staging_manifest = write_canonical_once(staging / "staging-manifest.json", manifest)
        evidence_manifest = write_canonical_once(attempt_dir / "staging-manifest.json", manifest)
        return staging, public_refs, staging_manifest, evidence_manifest

    def _props(
        self,
        request: RenderRequest,
        context: RenderExecutionContext,
        public_refs: Mapping[str, str],
    ) -> dict[str, Any]:
        fps_value = request.output_spec["fps"]
        fps_fraction = Fraction(int(fps_value["numerator"]), int(fps_value["denominator"]))
        if fps_fraction.denominator != 1:
            raise ContractValidationError(
                (_issue(RendererErrorCode.RENDER_INPUT_INVALID, "Experiment requires integer FPS.", "$.output_spec.fps", stage="adapt"),)
            )
        fps = fps_fraction.numerator
        segments = []
        for segment in request.timeline["segments"]:
            segments.append(
                {
                    "segmentId": str(segment["segment_id"]),
                    "startFrame": _round_frame(int(segment["start_tick"]), fps),
                    "endFrame": _round_frame(int(segment["end_tick"]), fps),
                    "visualRefs": [public_refs[str(item)] for item in segment["visual"]["asset_ids"]],
                    "captionRefs": [str(item) for item in segment["caption_cue_ids"]],
                }
            )
        captions = []
        for track in request.captions["tracks"]:
            for cue in track["cues"]:
                captions.append(
                    {
                        "cueId": str(cue["cue_id"]),
                        "segmentId": str(cue["segment_id"]),
                        "trackId": str(track["track_id"]),
                        "text": str(cue["text"]),
                        "startMs": int(cue["start_tick"]),
                        "endMs": int(cue["end_tick"]),
                        "timestampMs": None,
                        "confidence": None,
                    }
                )
        first_track = request.captions["tracks"][0]
        font_id = str(first_track["style"]["font_asset_id"])
        font_asset = next(item for item in request.assets if item.asset_id == font_id)
        final_mix_id = str(request.audio["final_mix_asset_id"])
        final_mix = next(item for item in request.assets if item.asset_id == final_mix_id)
        safe_area = first_track["style"]["safe_area"]
        extension = request.extensions[REMOTION_EXTENSION]
        props = {
            "schemaVersion": "1.0",
            "requestId": request.request_id,
            "requestHash": request.request_hash,
            "attemptId": context.attempt_id,
            "renderMode": request.render_mode.value,
            "width": int(request.output_spec["width"]),
            "height": int(request.output_spec["height"]),
            "fps": fps,
            "durationInFrames": _round_frame(int(request.output_spec["duration_ticks"]), fps),
            "segments": segments,
            "audio": {
                "assetId": final_mix_id,
                "src": public_refs[final_mix_id],
                "sha256": final_mix.sha256,
            },
            "captions": captions,
            "font": {
                "assetId": font_id,
                "family": "ContractCaption",
                "src": public_refs[font_id],
                "sha256": font_asset.sha256,
            },
            "captionStyle": {
                "leftPx": int(safe_area["left_px"]),
                "rightPx": int(safe_area["right_px"]),
                "bottomPx": int(safe_area["bottom_px"]),
                "maxLines": min(2, int(first_track["style"]["max_lines"])),
            },
            "assetBase": f"attempts/{context.attempt_id}/assets",
            "rendererExtension": {
                "schemaVersion": str(extension["schema_version"]),
                "compositionId": str(extension["composition_id"]),
            },
        }
        if extension["composition_id"] == PAPER_COLLAGE_COMPOSITION_ID:
            theme, theme_binding, texture_binding = self._paper_theme(request, context)
            canvas = theme["canvas"]
            texture = theme["paper_texture"]
            image = theme["image_card"]
            caption = theme["caption"]
            motion = theme["motion"]
            transition = theme["transition"]
            opening = extension["opening"]
            props["rendererExtension"] = {
                "schemaVersion": "1.0",
                "compositionId": PAPER_COLLAGE_COMPOSITION_ID,
                "template": {
                    "id": PAPER_COLLAGE_TEMPLATE_ID,
                    "version": PAPER_COLLAGE_TEMPLATE_VERSION,
                },
                "theme": {
                    "assetId": theme_binding.asset_id,
                    "src": public_refs[theme_binding.asset_id],
                    "sha256": theme_binding.sha256,
                    "tokens": {
                        "schemaVersion": "paper-collage-theme-v1",
                        "canvas": {
                            "background": str(canvas["background"]),
                            "ink": str(canvas["ink"]),
                            "accent": str(canvas["accent"]),
                            "safeMarginX": int(canvas["safe_margin_x"]),
                            "safeMarginTop": int(canvas["safe_margin_top"]),
                            "safeMarginBottom": int(canvas["safe_margin_bottom"]),
                        },
                        "paperTexture": {
                            "assetId": texture_binding.asset_id,
                            "src": public_refs[texture_binding.asset_id],
                            "sha256": texture_binding.sha256,
                            "opacityMilli": int(texture["opacity_milli"]),
                        },
                        "imageCard": {
                            "maxWidth": int(image["max_width"]),
                            "maxHeight": int(image["max_height"]),
                            "padding": int(image["padding"]),
                            "borderWidth": int(image["border_width"]),
                            "shadowOffsetX": int(image["shadow_offset_x"]),
                            "shadowOffsetY": int(image["shadow_offset_y"]),
                            "rotationMillidegrees": int(image["rotation_millidegrees"]),
                        },
                        "caption": {
                            "maxLines": int(caption["max_lines"]),
                            "fontSize": int(caption["font_size"]),
                            "lineHeightMilli": int(caption["line_height_milli"]),
                            "paddingX": int(caption["padding_x"]),
                            "paddingY": int(caption["padding_y"]),
                            "background": str(caption["background"]),
                            "text": str(caption["text"]),
                        },
                        "motion": {
                            "maxScaleDeltaMilli": int(motion["max_scale_delta_milli"]),
                            "maxTranslateX": int(motion["max_translate_x"]),
                            "maxTranslateY": int(motion["max_translate_y"]),
                            "maxRotationMillidegrees": int(motion["max_rotation_millidegrees"]),
                        },
                        "transition": {
                            "durationFrames": int(transition["duration_frames"]),
                            "maxTranslatePx": int(transition["max_translate_px"]),
                        },
                    },
                },
                "motionPreset": str(extension["motion_preset"]),
                "transitionPreset": str(extension["transition_preset"]),
                "captionPreset": str(extension["caption_preset"]),
                "requiredCapabilities": list(request.renderer.required_capabilities),
                "opening": {
                    "startFrame": _round_frame(int(opening["start_tick"]), fps),
                    "endFrame": _round_frame(int(opening["end_tick"]), fps),
                    "title": str(opening["title"]),
                    "subtitle": str(opening["subtitle"]),
                },
            }
        return props

    def _probe_issues(
        self, request: RenderRequest, probe: Mapping[str, Any]
    ) -> tuple[RenderIssue, ...]:
        issues: list[RenderIssue] = []
        expected = request.output_spec
        video = probe.get("video")
        audio = probe.get("audio")
        if not isinstance(video, Mapping) or not isinstance(audio, Mapping):
            return (_issue(RendererErrorCode.RENDER_PROBE_FAILED, "Probe lacks video/audio streams.", "$.media_probe", stage="probe"),)
        checks = (
            (video.get("codec"), expected["video"]["codec"], "video.codec"),
            (video.get("width"), expected["width"], "video.width"),
            (video.get("height"), expected["height"], "video.height"),
            (_plain(video.get("fps")), _plain(expected["fps"]), "video.fps"),
            (video.get("pixel_format"), expected["pixel_format"], "video.pixel_format"),
            (audio.get("codec"), expected["audio"]["codec"], "audio.codec"),
            (audio.get("sample_rate"), expected["audio"]["sample_rate"], "audio.sample_rate"),
            (audio.get("channels"), expected["audio"]["channels"], "audio.channels"),
        )
        for actual, wanted, field in checks:
            if actual != wanted:
                issues.append(_issue(RendererErrorCode.RENDER_PROBE_FAILED, "Probe value differs from OutputSpec.", f"$.media_probe.{field}", stage="probe"))
        fps = expected["fps"]
        tolerance = (1000 * int(fps["denominator"]) + int(fps["numerator"]) - 1) // int(fps["numerator"]) + 1
        duration = probe.get("duration_ticks")
        if not isinstance(duration, int) or abs(duration - int(expected["duration_ticks"])) > tolerance:
            issues.append(_issue(RendererErrorCode.RENDER_PROBE_FAILED, "Probe duration exceeds one-frame tolerance.", "$.media_probe.duration_ticks", stage="probe"))
        return stable_issues(issues)

    def render(
        self, request: RenderRequest, context: RenderExecutionContext
    ) -> RenderResult:
        self._validate_context(context)
        started_at = self._clock()
        self._event(request, context, 0, RenderStatus.PENDING, started_at)
        preflight = self.validate(request, context)
        if preflight:
            return self._failed(request, context, preflight, started_at)
        project = context.resolver.bindings["project"]
        attempt_dir = Path(context.attempts_directory).resolve() / context.attempt_id
        try:
            staging, public_refs, _, staging_evidence = self._stage_assets(
                request, context, attempt_dir
            )
            props = self._props(request, context, public_refs)
            props_path = write_canonical_once(staging / "props.json", props)
            props_evidence = write_canonical_once(attempt_dir / "remotion-props.json", props)
        except ContractValidationError as error:
            return self._failed(request, context, error.issues, started_at)
        except Exception:
            return self._failed(
                request,
                context,
                (_issue(RendererErrorCode.RENDER_INPUT_INVALID, "Asset staging or Props adaptation failed.", "$.attempt", stage="stage"),),
                started_at,
            )
        output_path = self._output_path(request, context)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        composition_id = str(request.extensions[REMOTION_EXTENSION]["composition_id"])
        command = [
            self._node,
            str(self._project / "scripts" / "render-contract.mjs"),
            "--props",
            str(props_path),
            "--output",
            str(output_path),
            "--composition-id",
            composition_id,
            "--expected-request-id",
            request.request_id,
            "--expected-request-hash",
            request.request_hash,
            "--render-mode",
            request.render_mode.value,
        ]
        environment = dict(os.environ if context.environment is None else context.environment)
        command_record = write_canonical_once(
            attempt_dir / "render-command.json",
            {
                "schema_version": "1.0",
                "argv": command,
                "cwd": str(self._project),
                "environment_keys": sorted(environment),
                "shell": False,
            },
        )
        self._event(request, context, 1, RenderStatus.RUNNING, self._clock())
        logs_dir = attempt_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = logs_dir / "renderer.stdout.log"
        stderr_path = logs_dir / "renderer.stderr.log"
        try:
            completed: CommandResult = self._runner.run(
                command, cwd=self._project, env=environment
            )
        except Exception:
            completed = CommandResult(-1, stderr="Remotion runner raised an exception.")
        stdout_path.write_text(completed.stdout, encoding="utf-8", errors="replace")
        stderr_path.write_text(completed.stderr, encoding="utf-8", errors="replace")
        logs = (
            {"role": "renderer_stdout", "ref": {"root": "project", "path": _portable(project, stdout_path).path}},
            {"role": "renderer_stderr", "ref": {"root": "project", "path": _portable(project, stderr_path).path}},
        )
        metrics = {
            "elapsed_ms": max(0, int(completed.elapsed_ms)),
            "runner_return_code": int(completed.returncode),
        }
        if completed.returncode != 0:
            return self._failed(
                request,
                context,
                (_issue(RendererErrorCode.RENDER_PROCESS_FAILED, "Remotion process failed.", "$.attempt", stage="render", details={"returncode": completed.returncode}),),
                started_at,
                metrics=metrics,
                logs=logs,
            )
        post_hash_issues = validate_request_filesystem(request, context.resolver)
        if post_hash_issues:
            return self._failed(request, context, post_hash_issues, started_at, metrics=metrics, logs=logs)
        if not output_path.is_file() or output_path.stat().st_size <= 0:
            return self._failed(
                request,
                context,
                (_issue(RendererErrorCode.RENDER_OUTPUT_MISSING, "Remotion output is missing or empty.", "$.output", stage="collect"),),
                started_at,
                metrics=metrics,
                logs=logs,
            )
        try:
            probe_payload = dict(self._probe.probe(output_path))
            probe_issues = self._probe_issues(request, probe_payload)
            if probe_issues:
                return self._failed(request, context, probe_issues, started_at, metrics=metrics, logs=logs)
            probe_path = write_canonical_once(attempt_dir / "probe" / "media-probe.json", probe_payload)
        except Exception:
            return self._failed(
                request,
                context,
                (_issue(RendererErrorCode.RENDER_PROBE_FAILED, "Remotion output probe failed.", "$.media_probe", stage="probe"),),
                started_at,
                metrics=metrics,
                logs=logs,
            )
        output_artifact = _artifact(
            project,
            output_path,
            asset_id=str(request.output["artifact_id"]),
            role=str(request.output["role"]),
            media_type="video/mp4",
        )
        sidecars = (
            _artifact(project, props_evidence, asset_id="remotion-props", role="renderer_props", media_type="application/json"),
            _artifact(project, staging_evidence, asset_id="staging-manifest", role="asset_staging_manifest", media_type="application/json"),
            _artifact(project, command_record, asset_id="render-command", role="render_command", media_type="application/json"),
            _artifact(project, probe_path, asset_id="media-probe", role="media_probe", media_type="application/json"),
        )
        media_probe = {"sidecar_artifact_id": "media-probe", **probe_payload}
        checks = [
            {"id": "output_exists", "result": "pass", "severity": "error"},
            {"id": "output_nonzero", "result": "pass", "severity": "error"},
            {"id": "input_hashes_stable", "result": "pass", "severity": "error"},
            {"id": "staging_hashes_match", "result": "pass", "severity": "error"},
            {"id": "final_mix_only", "result": "pass", "severity": "error"},
            {"id": "media_probe_readable", "result": "pass", "severity": "error"},
            {"id": "output_spec_match", "result": "pass", "severity": "error"},
        ]
        extension = request.extensions[REMOTION_EXTENSION]
        holds = list(extension.get("rights_holds", ()))
        qc_handoff = {
            "release_id": request.release.id,
            "request_hash": request.request_hash,
            "attempt_id": context.attempt_id,
            "output_asset_ids": [output_artifact.asset_id],
            "output_spec_snapshot": _plain(request.output_spec),
            "media_probe_artifact_id": "media-probe",
            "renderer_checks": checks,
            "expected_post_qc_profile_id": "remotion-contract-technical-qc-v1",
            "rights_snapshot_sha256": str(request.rights["snapshot_sha256"]),
            "approval_snapshot_sha256": str(request.approvals["snapshot_sha256"]),
            "release_holds": holds,
        }
        metrics.update(
            {
                "output_bytes": output_artifact.bytes,
                "duration_ticks": int(probe_payload["duration_ticks"]),
                "frame_count": int(probe_payload["video"]["frame_count"]),
            }
        )
        return self._terminal_result(
            request,
            context,
            status=RenderStatus.SUCCEEDED,
            started_at=started_at,
            output=(output_artifact,),
            sidecars=sidecars,
            media_probe=media_probe,
            metrics=metrics,
            qc_handoff=qc_handoff,
            logs=logs,
            extension_details={
                "composition_id": composition_id,
                **(
                    {
                        "template_id": PAPER_COLLAGE_TEMPLATE_ID,
                        "template_version": PAPER_COLLAGE_TEMPLATE_VERSION,
                        "theme_asset_id": str(extension["theme_tokens_asset_id"]),
                        "texture_asset_id": str(extension["texture_asset_id"]),
                    }
                    if composition_id == PAPER_COLLAGE_COMPOSITION_ID
                    else {}
                ),
                "staging_ref": f"attempts/{context.attempt_id}",
                "props_asset_id": "remotion-props",
                "staging_manifest_asset_id": "staging-manifest",
            },
        )


__all__ = [
    "PAPER_COLLAGE_COMPOSITION_ID",
    "PAPER_COLLAGE_TEMPLATE_ID",
    "PAPER_COLLAGE_TEMPLATE_VERSION",
    "REMOTION_COMPOSITION_ID",
    "REMOTION_EXTENSION",
    "REMOTION_RENDERER_ID",
    "REMOTION_RENDERER_VERSION",
    "RemotionContractRenderer",
]
