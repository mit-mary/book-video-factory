import type { Caption } from "@remotion/captions";

export type ContractCompositionId =
  | "ContractConformanceV1"
  | "PaperCollageVisualV1"
  | "EditorialPaperCollageV1";

export type ContractSegment = {
  segmentId: string;
  startFrame: number;
  endFrame: number;
  visualRefs: string[];
  captionRefs: string[];
};

export type ContractCaption = Caption & {
  cueId: string;
  segmentId: string;
  trackId: string;
};

export type ContractProps = {
  schemaVersion: "1.0";
  requestId: string;
  requestHash: string;
  attemptId: string;
  renderMode: "preview" | "final";
  width: number;
  height: number;
  fps: number;
  durationInFrames: number;
  segments: ContractSegment[];
  audio: {
    assetId: string;
    src: string;
    sha256: string;
  };
  captions: ContractCaption[];
  font: {
    assetId: string;
    family: string;
    src: string;
    sha256: string;
  };
  captionStyle: {
    leftPx: number;
    rightPx: number;
    bottomPx: number;
    maxLines: number;
  };
  assetBase: string;
  rendererExtension: {
    schemaVersion: "1.0";
    compositionId: ContractCompositionId;
  };
};
