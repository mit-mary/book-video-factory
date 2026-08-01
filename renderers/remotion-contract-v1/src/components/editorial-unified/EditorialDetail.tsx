import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

import type { PaperCollageTheme } from "../../contract/paper-collage-types";
import { DIRECTION_A_CROPS, DirectionAAtlasCrop } from "./DirectionAAtlas";

export const EditorialDetail: React.FC<{
  source: string | undefined;
  durationInFrames: number;
  family: string;
  theme: PaperCollageTheme;
}> = ({ source, durationInFrames, family, theme }) => {
  const frame = useCurrentFrame();
  const { height, width } = useVideoConfig();
  const unit = Math.min(width / 720, height / 1280);
  return (
    <AbsoluteFill style={{ backgroundColor: theme.canvas.background }}>
      <div
        style={{
          position: "absolute",
          left: "9%",
          top: "8%",
          width: "82%",
          height: "59%",
          border: `${10 * unit}px solid #FFFDF7`,
          boxSizing: "border-box",
          overflow: "hidden",
          backgroundColor: "#FFFDF7",
          boxShadow: `${10 * unit}px ${13 * unit}px 0 rgba(42,37,32,0.15)`,
          translate: `${interpolate(frame, [0, Math.max(1, durationInFrames - 1)], [-8, 8], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          })}px 0px`,
        }}
      >
        {source ? (
          <DirectionAAtlasCrop
            name="Toggle switch detail artwork"
            source={source}
            crop={DIRECTION_A_CROPS.detail}
            targetWidth={width * 0.82 - 20 * unit}
            targetHeight={height * 0.59 - 20 * unit}
          />
        ) : null}
      </div>
      <div
        style={{
          position: "absolute",
          left: "10%",
          top: "70%",
          color: theme.canvas.accent,
          fontFamily: family,
          fontSize: 62 * unit,
          fontWeight: 850,
          lineHeight: 1,
        }}
      >
        小动作
      </div>
    </AbsoluteFill>
  );
};
