import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

import type { PaperCollageTheme } from "../../contract/paper-collage-types";
import { DIRECTION_A_CROPS, DirectionAAtlasCrop } from "./DirectionAAtlas";
import { PaperReveal } from "./PaperReveal";

export const FullBleedMetaphor: React.FC<{
  source: string | undefined;
  segmentIndex: number;
  durationInFrames: number;
  family: string;
  theme: PaperCollageTheme;
}> = ({ source, segmentIndex, durationInFrames, family, theme }) => {
  const frame = useCurrentFrame();
  const { height, width } = useVideoConfig();
  const unit = Math.min(width / 720, height / 1280);
  const variant = segmentIndex === 0 ? "hook" : segmentIndex === 3 ? "turning" : "ending";
  const keyword = variant === "hook" ? "改变生活" : variant === "turning" ? "转向" : "小选择";
  const stillStart = Math.max(1, durationInFrames - (variant === "ending" ? 45 : 1));
  return (
    <AbsoluteFill style={{ backgroundColor: theme.canvas.background, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          inset: variant === "turning" ? "2.5% 3% 5%" : "2.5% 3% 4%",
          overflow: "hidden",
          scale: interpolate(frame, [0, stillStart], [1, 1.02], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
            output: "perceptual-scale",
          }),
        }}
      >
        {source ? (
          <DirectionAAtlasCrop
            name={`${variant} hero artwork`}
            source={source}
            crop={DIRECTION_A_CROPS[variant]}
            targetWidth={width * 0.94}
            targetHeight={height * (variant === "turning" ? 0.925 : 0.935)}
          />
        ) : null}
      </div>
      <div
        style={{
          position: "absolute",
          left: variant === "turning" ? "auto" : "7%",
          right: variant === "turning" ? "8%" : "auto",
          top: variant === "ending" ? "8%" : variant === "turning" ? "52%" : "9%",
          color: variant === "turning" ? theme.canvas.accent : "#FFFDF7",
          fontFamily: family,
          fontSize: (variant === "turning" ? 72 : 58) * unit,
          fontWeight: 850,
          lineHeight: 1.05,
          letterSpacing: -1 * unit,
          textShadow: "0 3px 12px rgba(42,37,32,0.48)",
        }}
      >
        {keyword}
      </div>
      <PaperReveal color={theme.canvas.background} />
    </AbsoluteFill>
  );
};
