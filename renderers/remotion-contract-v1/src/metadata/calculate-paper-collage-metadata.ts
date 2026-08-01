import type { CalculateMetadataFunction } from "remotion";

import { parsePaperCollageProps } from "../contract/parse-paper-collage";
import type { PaperCollageProps } from "../contract/paper-collage-types";

export const calculatePaperCollageMetadata: CalculateMetadataFunction<PaperCollageProps> = ({
  props,
}) => {
  const parsed = parsePaperCollageProps(props);
  return {
    durationInFrames: parsed.durationInFrames,
    fps: parsed.fps,
    width: parsed.width,
    height: parsed.height,
    props: parsed,
    defaultOutName: `${parsed.requestId}-${parsed.renderMode}-paper-collage`,
    defaultCodec: "h264",
  };
};
