import {
  AbsoluteFill,
  Easing,
  Sequence,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

import type { PaperCollageTheme } from "../../contract/paper-collage-types";
import type { AtlasCrop } from "./DirectionAAtlas";
import { DIRECTION_A_CROPS, DirectionAAtlasCrop } from "./DirectionAAtlas";

const BuildItem: React.FC<{
  source: string;
  crop: AtlasCrop;
  name: string;
  label: string;
  side: "left" | "right";
  top: string;
  family: string;
  theme: PaperCollageTheme;
  dimAfter?: number;
}> = ({ source, crop, name, label, side, top, family, theme, dimAfter }) => {
  const frame = useCurrentFrame();
  const { height, width } = useVideoConfig();
  const unit = Math.min(width / 720, height / 1280);
  const cardWidth = width * 0.55;
  const cardHeight = height * 0.205;
  const opacity = dimAfter
    ? interpolate(frame, [0, 8, dimAfter, dimAfter + 8], [0, 1, 1, 0.48], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.bezier(0.16, 1, 0.3, 1),
      })
    : interpolate(frame, [0, 8], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.bezier(0.16, 1, 0.3, 1),
      });
  return (
    <div style={{ position: "absolute", inset: 0, opacity }}>
      <div
        style={{
          position: "absolute",
          left: side === "left" ? "7%" : "38%",
          top,
          width: "55%",
          height: "20.5%",
          border: `${8 * unit}px solid #FFFDF7`,
          boxSizing: "border-box",
          overflow: "hidden",
          backgroundColor: "#FFFDF7",
          boxShadow: `${8 * unit}px ${10 * unit}px 0 rgba(42,37,32,0.14)`,
          translate: `${interpolate(frame, [0, 8], [side === "left" ? -14 : 14, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          })}px 0px`,
        }}
      >
        <DirectionAAtlasCrop
          name={name}
          source={source}
          crop={crop}
          targetWidth={cardWidth - 16 * unit}
          targetHeight={cardHeight - 16 * unit}
        />
      </div>
      <div
        style={{
          position: "absolute",
          left: side === "left" ? "66%" : "7%",
          top: `calc(${top} + 8%)`,
          width: "29%",
          color: theme.canvas.ink,
          fontFamily: family,
          fontSize: 25 * unit,
          fontWeight: 780,
          lineHeight: 1.18,
        }}
      >
        {label}
      </div>
    </div>
  );
};

export const SequentialBuild: React.FC<{
  source: string | undefined;
  durationInFrames: number;
  family: string;
  theme: PaperCollageTheme;
}> = ({ source, durationInFrames, family, theme }) => {
  const { fps } = useVideoConfig();
  if (!source) return <AbsoluteFill style={{ backgroundColor: theme.canvas.background }} />;
  return (
    <AbsoluteFill style={{ backgroundColor: theme.canvas.background }}>
      <Sequence durationInFrames={durationInFrames} premountFor={Math.min(8, fps)} name="Clock action">
        <BuildItem source={source} crop={DIRECTION_A_CROPS.clock} name="Clock detail" label="早睡十分钟" side="left" top="5%" family={family} theme={theme} dimAfter={46} />
      </Sequence>
      <Sequence from={46} durationInFrames={durationInFrames - 46} premountFor={8} name="Boundary action">
        <BuildItem source={source} crop={DIRECTION_A_CROPS.hand} name="Stop hand detail" label="拒绝一次迎合" side="right" top="29%" family={family} theme={theme} dimAfter={46} />
      </Sequence>
      <Sequence from={92} durationInFrames={durationInFrames - 92} premountFor={8} name="Honesty action">
        <BuildItem source={source} crop={DIRECTION_A_CROPS.heart} name="Paper heart detail" label="承认自己的不舒服" side="left" top="53%" family={family} theme={theme} />
      </Sequence>
    </AbsoluteFill>
  );
};
