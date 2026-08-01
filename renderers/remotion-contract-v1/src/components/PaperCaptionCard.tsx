import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

import type { ContractCaption } from "../contract/types";
import type {
  PaperCollageLayout,
  PaperCollageTheme,
} from "../contract/paper-collage-types";
import {
  PAPER_CAPTION_OUTLINE,
  PAPER_CAPTION_SHADOW_X,
  PAPER_CAPTION_SHADOW_Y,
} from "../contract/paper-collage-layout";

export const PaperCaptionCard: React.FC<{
  captions: ContractCaption[];
  family: string;
  layout: PaperCollageLayout;
  theme: PaperCollageTheme;
}> = ({ captions, family, layout, theme }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentMs = (frame * 1000) / fps;
  const active = captions
    .filter((caption) => caption.startMs <= currentMs && currentMs < caption.endMs)
    .sort((left, right) => left.trackId.localeCompare(right.trackId))
    .slice(0, theme.caption.maxLines);
  if (active.length === 0) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: layout.captionCard.x,
          top: layout.captionCard.y,
          width: layout.captionCard.width,
          height: layout.captionCard.height,
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          paddingLeft: theme.caption.paddingX,
          paddingRight: theme.caption.paddingX,
          paddingTop: theme.caption.paddingY,
          paddingBottom: theme.caption.paddingY,
          backgroundColor: theme.caption.background,
          color: theme.caption.text,
          outline: `${PAPER_CAPTION_OUTLINE}px solid ${theme.canvas.ink}`,
          boxShadow: `${PAPER_CAPTION_SHADOW_X}px ${PAPER_CAPTION_SHADOW_Y}px 0 rgba(42,37,32,0.22)`,
          fontFamily: family,
          fontSize: theme.caption.fontSize,
          fontWeight: 700,
          lineHeight: theme.caption.lineHeightMilli / 1000,
          overflow: "hidden",
          textAlign: "center",
          whiteSpace: "pre-wrap",
        }}
      >
        {active.map((caption) => (
          <div key={`${caption.cueId}-${caption.trackId}`}>{caption.text}</div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
