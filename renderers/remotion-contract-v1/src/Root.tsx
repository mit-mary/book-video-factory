import { Composition } from "remotion";

import { ContractConformance } from "./compositions/ContractConformance";
import { PaperCollageVisual } from "./compositions/PaperCollageVisual";
import { calculateContractMetadata } from "./metadata/calculate-metadata";
import { calculatePaperCollageMetadata } from "./metadata/calculate-paper-collage-metadata";
import type { PaperCollageProps } from "./contract/paper-collage-types";
import type { ContractProps } from "./contract/types";

const placeholderProps: ContractProps = {
  schemaVersion: "1.0",
  requestId: "placeholder",
  requestHash: "0".repeat(64),
  attemptId: "placeholder",
  renderMode: "preview",
  width: 2,
  height: 2,
  fps: 1,
  durationInFrames: 1,
  segments: [
    {
      segmentId: "placeholder",
      startFrame: 0,
      endFrame: 1,
      visualRefs: [],
      captionRefs: [],
    },
  ],
  audio: {
    assetId: "placeholder",
    src: "placeholder.wav",
    sha256: "0".repeat(64),
  },
  captions: [],
  font: {
    assetId: "placeholder",
    family: "ContractCaption",
    src: "placeholder.ttf",
    sha256: "0".repeat(64),
  },
  captionStyle: {
    leftPx: 0,
    rightPx: 0,
    bottomPx: 0,
    maxLines: 2,
  },
  assetBase: "attempts/placeholder/assets",
  rendererExtension: {
    schemaVersion: "1.0",
    compositionId: "ContractConformanceV1",
  },
};

const paperPlaceholderProps: PaperCollageProps = {
  ...placeholderProps,
  width: 720,
  height: 960,
  fps: 30,
  rendererExtension: {
    schemaVersion: "1.0",
    compositionId: "PaperCollageVisualV1",
    template: { id: "paper-collage-visual-v1", version: "0.1.0-experimental" },
    theme: {
      assetId: "paper-collage-theme-v1",
      src: "attempts/placeholder/assets/paper-collage-theme-v1.json",
      sha256: "0".repeat(64),
      tokens: {
        schemaVersion: "paper-collage-theme-v1",
        canvas: {
          background: "#F3EBDD",
          ink: "#2A2520",
          accent: "#B65B46",
          safeMarginX: 72,
          safeMarginTop: 72,
          safeMarginBottom: 104,
        },
        paperTexture: {
          assetId: "paper-texture-v1",
          src: "attempts/placeholder/assets/paper-texture-v1.svg",
          sha256: "0".repeat(64),
          opacityMilli: 120,
        },
        imageCard: {
          maxWidth: 560,
          maxHeight: 600,
          padding: 18,
          borderWidth: 3,
          shadowOffsetX: 12,
          shadowOffsetY: 16,
          rotationMillidegrees: 1500,
        },
        caption: {
          maxLines: 2,
          fontSize: 42,
          lineHeightMilli: 1250,
          paddingX: 32,
          paddingY: 18,
          background: "#FFFDF7",
          text: "#2A2520",
        },
        motion: {
          maxScaleDeltaMilli: 40,
          maxTranslateX: 20,
          maxTranslateY: 16,
          maxRotationMillidegrees: 500,
        },
        // Static token data; this is not a CSS transition.
        // eslint-disable-next-line @remotion/non-pure-animation
        transition: { durationFrames: 6, maxTranslatePx: 12 },
      },
    },
    motionPreset: "subtle",
    transitionPreset: "paper-cut",
    captionPreset: "bottom-card",
    requiredCapabilities: ["layered_images", "camera_motion", "transitions"],
    opening: {
      startFrame: 0,
      endFrame: 36,
      title: "TEST TITLE",
      subtitle: "CONTROLLED FIXTURE",
    },
  },
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ContractConformanceV1"
        component={ContractConformance}
        durationInFrames={1}
        fps={1}
        width={2}
        height={2}
        defaultProps={placeholderProps}
        calculateMetadata={calculateContractMetadata}
      />
      <Composition
        id="PaperCollageVisualV1"
        component={PaperCollageVisual}
        durationInFrames={1}
        fps={30}
        width={720}
        height={960}
        defaultProps={paperPlaceholderProps}
        calculateMetadata={calculatePaperCollageMetadata}
      />
    </>
  );
};
