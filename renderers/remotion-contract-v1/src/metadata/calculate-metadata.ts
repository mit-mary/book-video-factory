import type { CalculateMetadataFunction } from "remotion";

import { parseContractProps } from "../contract/parse-props";
import type { ContractProps } from "../contract/types";

export const calculateContractMetadata: CalculateMetadataFunction<ContractProps> = ({
  props,
}) => {
  const parsed = parseContractProps(props);
  return {
    durationInFrames: parsed.durationInFrames,
    fps: parsed.fps,
    width: parsed.width,
    height: parsed.height,
    props: parsed,
    defaultOutName: `${parsed.requestId}-${parsed.renderMode}`,
    defaultCodec: "h264",
  };
};
