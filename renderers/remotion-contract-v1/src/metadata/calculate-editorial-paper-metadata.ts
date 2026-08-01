import type { CalculateMetadataFunction } from "remotion";

import { parseEditorialPaperProps } from "../contract/parse-editorial-paper";
import type { EditorialPaperCollageProps } from "../contract/editorial-paper-types";

export const calculateEditorialPaperMetadata: CalculateMetadataFunction<EditorialPaperCollageProps> = ({
  props,
}) => {
  if (props.rendererExtension?.compositionId !== "EditorialPaperCollageV1") {
    return {};
  }
  const parsed = parseEditorialPaperProps(props);
  return {
    durationInFrames: parsed.durationInFrames,
    fps: parsed.fps,
    width: parsed.width,
    height: parsed.height,
    props: parsed,
    defaultOutName: `${parsed.requestId}-editorial-${parsed.renderMode}`,
    defaultCodec: "h264",
  };
};
