import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";

import type {
  PaperCollageLayout,
  PaperCollageProps,
  PaperCollageTheme,
} from "../contract/paper-collage-types";

export const PaperOpeningCard: React.FC<{
  family: string;
  layout: PaperCollageLayout;
  theme: PaperCollageTheme;
  opening: PaperCollageProps["rendererExtension"]["opening"];
}> = ({ family, layout, theme, opening }) => {
  const frame = useCurrentFrame();
  const duration = opening.endFrame - opening.startFrame;
  const fadeFrames = Math.min(theme.transition.durationFrames, Math.max(1, duration - 1));
  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.canvas.background,
        opacity: interpolate(
          frame,
          [duration - fadeFrames, duration - 1],
          [1, 0],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.7, 0, 0.84, 0),
          },
        ),
      }}
    >
      <div
        style={{
          position: "absolute",
          left: layout.imageCard.x,
          top: layout.imageCard.y,
          width: layout.imageCard.width,
          height: layout.imageCard.height,
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 44,
          backgroundColor: "#FFFDF7",
          color: theme.canvas.ink,
          outline: `${theme.imageCard.borderWidth}px solid ${theme.canvas.ink}`,
          boxShadow: `${theme.imageCard.shadowOffsetX}px ${theme.imageCard.shadowOffsetY}px 0 rgba(42,37,32,0.2)`,
          fontFamily: family,
          textAlign: "center",
          translate: `${interpolate(frame, [0, fadeFrames], [theme.transition.maxTranslatePx, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          })}px 0px`,
          rotate: `${theme.imageCard.rotationMillidegrees / 1000}deg`,
        }}
      >
        <div style={{ fontSize: 68, fontWeight: 800 }}>{opening.title}</div>
        <div style={{ marginTop: 22, fontSize: 32, fontWeight: 500 }}>
          {opening.subtitle}
        </div>
      </div>
    </AbsoluteFill>
  );
};
