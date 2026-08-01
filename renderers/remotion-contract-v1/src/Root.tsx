import { Composition } from "remotion";

import { ContractConformance } from "./compositions/ContractConformance";
import { calculateContractMetadata } from "./metadata/calculate-metadata";
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

export const RemotionRoot: React.FC = () => {
  return (
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
  );
};
