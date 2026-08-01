import type { ContractCaption, ContractProps, ContractSegment } from "./types";

const SHA256 = /^[0-9a-f]{64}$/;
const PORTABLE = /^(?!\/)(?!.*(?:^|\/)\.\.(?:\/|$))[A-Za-z0-9._\-/]+$/;

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

const integer = (value: unknown, field: string, minimum: number): number => {
  if (!Number.isInteger(value) || (value as number) < minimum) {
    throw new Error(`${field} must be an integer >= ${minimum}`);
  }
  return value as number;
};

const string = (value: unknown, field: string): string => {
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`${field} must be a non-empty string`);
  }
  return value;
};

const portable = (value: unknown, field: string): string => {
  const parsed = string(value, field);
  if (!PORTABLE.test(parsed) || parsed.includes("\\") || /^[A-Za-z]:/.test(parsed)) {
    throw new Error(`${field} must be a portable public-relative path`);
  }
  return parsed;
};

const sha256 = (value: unknown, field: string): string => {
  const parsed = string(value, field);
  if (!SHA256.test(parsed)) {
    throw new Error(`${field} must be a lowercase SHA-256`);
  }
  return parsed;
};

const parseSegment = (value: unknown, index: number): ContractSegment => {
  if (!isRecord(value)) {
    throw new Error(`segments[${index}] must be an object`);
  }
  if (!Array.isArray(value.visualRefs) || !Array.isArray(value.captionRefs)) {
    throw new Error(`segments[${index}] refs must be arrays`);
  }
  return {
    segmentId: string(value.segmentId, `segments[${index}].segmentId`),
    startFrame: integer(value.startFrame, `segments[${index}].startFrame`, 0),
    endFrame: integer(value.endFrame, `segments[${index}].endFrame`, 1),
    visualRefs: value.visualRefs.map((item, refIndex) =>
      portable(item, `segments[${index}].visualRefs[${refIndex}]`),
    ),
    captionRefs: value.captionRefs.map((item, refIndex) =>
      string(item, `segments[${index}].captionRefs[${refIndex}]`),
    ),
  };
};

const parseCaption = (value: unknown, index: number): ContractCaption => {
  if (!isRecord(value)) {
    throw new Error(`captions[${index}] must be an object`);
  }
  const timestamp = value.timestampMs;
  const confidence = value.confidence;
  if (timestamp !== null && !Number.isFinite(timestamp)) {
    throw new Error(`captions[${index}].timestampMs must be null or finite`);
  }
  if (confidence !== null && !Number.isFinite(confidence)) {
    throw new Error(`captions[${index}].confidence must be null or finite`);
  }
  return {
    cueId: string(value.cueId, `captions[${index}].cueId`),
    segmentId: string(value.segmentId, `captions[${index}].segmentId`),
    trackId: string(value.trackId, `captions[${index}].trackId`),
    text: string(value.text, `captions[${index}].text`),
    startMs: integer(value.startMs, `captions[${index}].startMs`, 0),
    endMs: integer(value.endMs, `captions[${index}].endMs`, 1),
    timestampMs: timestamp as number | null,
    confidence: confidence as number | null,
  };
};

export const parseContractProps = (value: unknown): ContractProps => {
  if (!isRecord(value)) {
    throw new Error("props must be an object");
  }
  if (value.schemaVersion !== "1.0") {
    throw new Error("unsupported props schemaVersion");
  }
  const requestHash = sha256(value.requestHash, "requestHash");
  const renderMode = value.renderMode;
  if (renderMode !== "preview" && renderMode !== "final") {
    throw new Error("renderMode must be preview or final");
  }
  if (!Array.isArray(value.segments) || value.segments.length === 0) {
    throw new Error("segments must be a non-empty array");
  }
  if (!Array.isArray(value.captions)) {
    throw new Error("captions must be an array");
  }
  const segments = value.segments.map(parseSegment);
  const durationInFrames = integer(value.durationInFrames, "durationInFrames", 1);
  let previousEnd = 0;
  for (const [index, segment] of segments.entries()) {
    if (segment.startFrame !== previousEnd || segment.endFrame <= segment.startFrame) {
      throw new Error(`segments[${index}] must be contiguous and non-empty`);
    }
    previousEnd = segment.endFrame;
  }
  if (previousEnd !== durationInFrames) {
    throw new Error("segments must cover durationInFrames exactly");
  }
  if (!isRecord(value.audio) || !isRecord(value.font) || !isRecord(value.captionStyle)) {
    throw new Error("audio, font and captionStyle must be objects");
  }
  if (!isRecord(value.rendererExtension)) {
    throw new Error("rendererExtension must be an object");
  }
  if (
    value.rendererExtension.schemaVersion !== "1.0" ||
    (value.rendererExtension.compositionId !== "ContractConformanceV1" &&
      value.rendererExtension.compositionId !== "PaperCollageVisualV1" &&
      value.rendererExtension.compositionId !== "EditorialPaperCollageV1")
  ) {
    throw new Error("rendererExtension identity is invalid");
  }
  return {
    schemaVersion: "1.0",
    requestId: string(value.requestId, "requestId"),
    requestHash,
    attemptId: string(value.attemptId, "attemptId"),
    renderMode,
    width: integer(value.width, "width", 1),
    height: integer(value.height, "height", 1),
    fps: integer(value.fps, "fps", 1),
    durationInFrames,
    segments,
    audio: {
      assetId: string(value.audio.assetId, "audio.assetId"),
      src: portable(value.audio.src, "audio.src"),
      sha256: sha256(value.audio.sha256, "audio.sha256"),
    },
    captions: value.captions.map(parseCaption),
    font: {
      assetId: string(value.font.assetId, "font.assetId"),
      family: string(value.font.family, "font.family"),
      src: portable(value.font.src, "font.src"),
      sha256: sha256(value.font.sha256, "font.sha256"),
    },
    captionStyle: {
      leftPx: integer(value.captionStyle.leftPx, "captionStyle.leftPx", 0),
      rightPx: integer(value.captionStyle.rightPx, "captionStyle.rightPx", 0),
      bottomPx: integer(value.captionStyle.bottomPx, "captionStyle.bottomPx", 0),
      maxLines: integer(value.captionStyle.maxLines, "captionStyle.maxLines", 1),
    },
    assetBase: portable(value.assetBase, "assetBase"),
    rendererExtension: {
      schemaVersion: "1.0",
      compositionId: value.rendererExtension.compositionId,
    },
  };
};
