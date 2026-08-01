import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

import type { ContractCaption, ContractProps } from "../contract/types";

export const CaptionLayer: React.FC<{
  captions: ContractCaption[];
  family: string;
  style: ContractProps["captionStyle"];
}> = ({ captions, family, style }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const currentMs = (frame * 1000) / fps;
  const active = captions
    .filter((caption) => caption.startMs <= currentMs && currentMs < caption.endMs)
    .sort((left, right) => left.trackId.localeCompare(right.trackId))
    .slice(0, style.maxLines);
  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingLeft: style.leftPx,
        paddingRight: style.rightPx,
        paddingBottom: style.bottomPx,
      }}
    >
      <div
        style={{
          color: "white",
          fontFamily: family,
          fontSize: Math.max(22, Math.round(width * 0.052)),
          fontWeight: 700,
          lineHeight: 1.25,
          maxWidth: "100%",
          overflow: "hidden",
          textAlign: "center",
          textShadow: "0 2px 7px rgba(0,0,0,0.9)",
          whiteSpace: "normal",
        }}
      >
        {active.map((caption: ContractCaption) => (
          <div key={`${caption.cueId}-${caption.trackId}`}>{caption.text}</div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
