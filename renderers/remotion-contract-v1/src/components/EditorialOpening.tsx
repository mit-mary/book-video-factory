import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

import {
  DIRECTION_A_HOOK_CROP,
  DirectionAAtlasCrop,
} from "./EditorialPaperScene";
import type { EditorialPaperCollageProps } from "../contract/editorial-paper-types";
import type { PaperCollageTheme } from "../contract/paper-collage-types";

export const EditorialOpening: React.FC<{
  family: string;
  source: string | undefined;
  theme: PaperCollageTheme;
  opening: EditorialPaperCollageProps["rendererExtension"]["opening"];
}> = ({ family, source, theme, opening }) => {
  const frame = useCurrentFrame();
  const { height, width } = useVideoConfig();
  const unit = Math.min(width / 720, height / 960);
  const duration = opening.endFrame - opening.startFrame;
  return (
    <AbsoluteFill style={{ backgroundColor: theme.canvas.background }}>
      <div style={{ position: "absolute", left: "5%", top: "7%", width: "60%", height: "84%", overflow: "hidden", clipPath: "polygon(0 2%, 97% 0, 100% 97%, 3% 100%)" }}>
        {source ? (
          <DirectionAAtlasCrop
            name="Opening torn-paper crop"
            source={source}
            crop={DIRECTION_A_HOOK_CROP}
            targetWidth={width * 0.6}
            targetHeight={height * 0.84}
            drift={3}
          />
        ) : null}
      </div>
      <div
        style={{
          position: "absolute",
          right: "5%",
          top: "4%",
          width: "39%",
          height: "88%",
          padding: "11% 4% 6%",
          boxSizing: "border-box",
          backgroundColor: theme.canvas.ink,
          color: theme.canvas.background,
          fontFamily: family,
          opacity: interpolate(frame, [duration - 7, duration - 1], [1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.7, 0, 0.84, 0),
          }),
          translate: `${interpolate(frame, [0, 9], [24, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          })}px 0px`,
        }}
      >
        <div style={{ fontSize: 12 * unit, letterSpacing: 1.4 }}>EDITORIAL / HOOK</div>
        <div style={{ marginTop: "55%", fontSize: 43 * unit, fontWeight: 850, lineHeight: 1.08 }}>{opening.title}</div>
        <div style={{ width: "45%", height: 4 * unit, marginTop: "12%", backgroundColor: "#DDA52D" }} />
        <div style={{ marginTop: "12%", fontSize: 23 * unit, fontWeight: 650, lineHeight: 1.28 }}>{opening.subtitle}</div>
      </div>
    </AbsoluteFill>
  );
};
