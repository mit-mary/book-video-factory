import { loadFont } from "@remotion/fonts";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile, useVideoConfig } from "remotion";

import { CaptionLayer } from "../components/CaptionLayer";
import { SegmentScene } from "../components/SegmentScene";
import { parseContractProps } from "../contract/parse-props";
import type { ContractProps } from "../contract/types";

const fontLoads = new Map<string, Promise<void>>();

const ensureFont = (family: string, source: string): void => {
  const key = `${family}:${source}`;
  if (!fontLoads.has(key)) {
    fontLoads.set(
      key,
      loadFont({ family, url: staticFile(source), display: "block" }),
    );
  }
};

export const ContractConformance: React.FC<ContractProps> = (rawProps) => {
  const props = parseContractProps(rawProps);
  const { fps } = useVideoConfig();
  ensureFont(props.font.family, props.font.src);
  return (
    <AbsoluteFill style={{ backgroundColor: "#10141b" }}>
      {props.segments.map((segment) => (
        <Sequence
          key={segment.segmentId}
          from={segment.startFrame}
          durationInFrames={segment.endFrame - segment.startFrame}
          premountFor={Math.min(fps, segment.startFrame)}
          name={segment.segmentId}
        >
          <SegmentScene segment={segment} />
        </Sequence>
      ))}
      <Audio src={staticFile(props.audio.src)} />
      <CaptionLayer
        captions={props.captions}
        family={props.font.family}
        style={props.captionStyle}
      />
    </AbsoluteFill>
  );
};
