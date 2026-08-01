import type { ContractProps } from "./types";

export type PaperCollageTheme = {
  schemaVersion: "paper-collage-theme-v1";
  canvas: {
    background: string;
    ink: string;
    accent: string;
    safeMarginX: number;
    safeMarginTop: number;
    safeMarginBottom: number;
  };
  paperTexture: {
    assetId: string;
    src: string;
    sha256: string;
    opacityMilli: number;
  };
  imageCard: {
    maxWidth: number;
    maxHeight: number;
    padding: number;
    borderWidth: number;
    shadowOffsetX: number;
    shadowOffsetY: number;
    rotationMillidegrees: number;
  };
  caption: {
    maxLines: number;
    fontSize: number;
    lineHeightMilli: number;
    paddingX: number;
    paddingY: number;
    background: string;
    text: string;
  };
  motion: {
    maxScaleDeltaMilli: number;
    maxTranslateX: number;
    maxTranslateY: number;
    maxRotationMillidegrees: number;
  };
  transition: {
    durationFrames: number;
    maxTranslatePx: number;
  };
};

export type PaperCollageProps = Omit<ContractProps, "rendererExtension"> & {
  rendererExtension: {
    schemaVersion: "1.0";
    compositionId: "PaperCollageVisualV1";
    template: {
      id: "paper-collage-visual-v1";
      version: "0.1.0-experimental";
    };
    theme: {
      assetId: string;
      src: string;
      sha256: string;
      tokens: PaperCollageTheme;
    };
    motionPreset: "subtle";
    transitionPreset: "paper-cut";
    captionPreset: "bottom-card";
    requiredCapabilities: string[];
    opening: {
      startFrame: number;
      endFrame: number;
      title: string;
      subtitle: string;
    };
  };
};

export type LayoutBox = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type PaperCollageLayout = {
  imageCard: LayoutBox;
  imageCardMotionEnvelope: LayoutBox;
  captionCard: LayoutBox;
  captionCardVisualEnvelope: LayoutBox;
};

export type MotionMode =
  | "slow-push-in"
  | "slow-pull-out"
  | "gentle-pan-left"
  | "gentle-pan-right"
  | "static";
