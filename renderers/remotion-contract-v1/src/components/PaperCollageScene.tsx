import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";

import {
  motionModeForSegment,
  PAPER_BACKING_OFFSET_X,
  PAPER_BACKING_OFFSET_Y,
  PAPER_BACKING_ROTATION_FACTOR,
} from "../contract/paper-collage-layout";
import type { PaperCollageLayout, PaperCollageTheme } from "../contract/paper-collage-types";
import type { ContractSegment } from "../contract/types";

export const PaperCollageScene: React.FC<{
  segment: ContractSegment;
  durationInFrames: number;
  family: string;
  layout: PaperCollageLayout;
  theme: PaperCollageTheme;
}> = ({ segment, durationInFrames, family, layout, theme }) => {
  const frame = useCurrentFrame();
  const lastFrame = Math.max(1, durationInFrames - 1);
  const transitionEnd = Math.min(theme.transition.durationFrames, lastFrame);
  const mode = motionModeForSegment(segment.segmentId);
  const deltaScale = theme.motion.maxScaleDeltaMilli / 1000;
  const baseRotation =
    (segment.segmentId.length % 2 === 0 ? -1 : 1) *
    (theme.imageCard.rotationMillidegrees / 1000);
  const scaleStart = mode === "slow-pull-out" ? 1 + deltaScale : 1;
  const scaleEnd = mode === "slow-push-in" ? 1 + deltaScale : 1;
  const translateStartX =
    mode === "gentle-pan-left"
      ? theme.motion.maxTranslateX
      : mode === "gentle-pan-right"
        ? -theme.motion.maxTranslateX
        : 0;
  const translateEndX = -translateStartX;
  const rotationDelta = theme.motion.maxRotationMillidegrees / 2000;
  const source = segment.visualRefs[0];
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: layout.imageCard.x + PAPER_BACKING_OFFSET_X,
          top: layout.imageCard.y + PAPER_BACKING_OFFSET_Y,
          width: layout.imageCard.width,
          height: layout.imageCard.height,
          backgroundColor: theme.canvas.accent,
          rotate: `${-baseRotation * PAPER_BACKING_ROTATION_FACTOR}deg`,
          opacity: 0.42,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: layout.imageCard.x,
          top: layout.imageCard.y,
          width: layout.imageCard.width,
          height: layout.imageCard.height,
          boxSizing: "border-box",
          padding: theme.imageCard.padding,
          backgroundColor: "#FFFDF7",
          outline: `${theme.imageCard.borderWidth}px solid ${theme.canvas.ink}`,
          boxShadow: `${theme.imageCard.shadowOffsetX}px ${theme.imageCard.shadowOffsetY}px 0 rgba(42,37,32,0.2)`,
          overflow: "hidden",
          scale: interpolate(frame, [0, lastFrame], [scaleStart, scaleEnd], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          translate: `${interpolate(frame, [0, lastFrame], [translateStartX, translateEndX], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }) + interpolate(frame, [0, transitionEnd], [theme.transition.maxTranslatePx, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          })}px ${interpolate(frame, [0, lastFrame], [0, theme.motion.maxTranslateY / 2], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })}px`,
          rotate: `${baseRotation + interpolate(frame, [0, lastFrame], [-rotationDelta, rotationDelta], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })}deg`,
        }}
      >
        {source ? (
          <Img
            src={staticFile(source)}
            style={{ width: "100%", height: "100%", objectFit: "contain" }}
          />
        ) : null}
      </div>
      <div
        style={{
          position: "absolute",
          left: theme.canvas.safeMarginX,
          top: layout.imageCard.y + layout.imageCard.height + 12,
          padding: "5px 11px",
          backgroundColor: theme.canvas.ink,
          color: theme.canvas.background,
          fontFamily: family,
          fontSize: 17,
          letterSpacing: 1,
        }}
      >
        {segment.segmentId}
      </div>
    </AbsoluteFill>
  );
};
