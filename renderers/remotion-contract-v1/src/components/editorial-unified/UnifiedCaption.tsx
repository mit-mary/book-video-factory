import { useCurrentFrame, useVideoConfig } from "remotion";

import type { PaperCollageTheme } from "../../contract/paper-collage-types";
import type { ContractCaption } from "../../contract/types";

export const UnifiedCaption: React.FC<{
  captions: ContractCaption[];
  family: string;
  theme: PaperCollageTheme;
}> = ({ captions, family, theme }) => {
  const frame = useCurrentFrame();
  const { fps, height, width } = useVideoConfig();
  const absoluteMs = (frame * 1000) / fps;
  const active = captions
    .filter((caption) => caption.startMs <= absoluteMs && absoluteMs < caption.endMs)
    .sort((left, right) => left.trackId.localeCompare(right.trackId));
  if (active.length === 0) return null;
  const unit = Math.min(width / 720, height / 1280);
  return (
    <div
      style={{
        position: "absolute",
        left: "7%",
        right: "7%",
        bottom: "5.5%",
        maxHeight: "17%",
        padding: `${15 * unit}px ${22 * unit}px`,
        boxSizing: "border-box",
        overflow: "hidden",
        backgroundColor: "rgba(42,37,32,0.82)",
        color: "#FFFDF7",
        fontFamily: family,
        fontSize: 36 * unit,
        fontWeight: 720,
        lineHeight: 1.24,
        textAlign: "left",
        whiteSpace: "pre-wrap",
        zIndex: 12,
        boxShadow: `0 ${6 * unit}px ${18 * unit}px rgba(42,37,32,0.18)`,
        borderLeft: `${5 * unit}px solid ${theme.canvas.accent}`,
      }}
    >
      {active.slice(0, 1).map((caption) => (
        <div key={`${caption.cueId}-${caption.trackId}`}>{caption.text}</div>
      ))}
    </div>
  );
};
