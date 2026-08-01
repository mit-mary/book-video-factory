import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

import type { EditorialLayout } from "../contract/editorial-paper-types";
import type { PaperCollageTheme } from "../contract/paper-collage-types";
import type { ContractCaption, ContractSegment } from "../contract/types";

type Crop = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export const DIRECTION_A_HOOK_CROP: Crop = {
  x: 18,
  y: 18,
  width: 482,
  height: 656,
};
const SWITCH_CROP: Crop = {
  x: 523,
  y: 18,
  width: 482,
  height: 656,
};
const CLOCK_CROP: Crop = {
  x: 18,
  y: 697,
  width: 312,
  height: 378,
};
const HAND_CROP: Crop = {
  x: 333,
  y: 697,
  width: 343,
  height: 378,
};
const HEART_CROP: Crop = {
  x: 679,
  y: 697,
  width: 326,
  height: 378,
};
const ROAD_CROP: Crop = {
  x: 18,
  y: 1098,
  width: 482,
  height: 422,
};
const WALKER_CROP: Crop = {
  x: 523,
  y: 1098,
  width: 482,
  height: 422,
};

const ATLAS_WIDTH = 1024;
const ATLAS_HEIGHT = 1536;

const keywordFor = (
  captions: ContractCaption[],
  layout: EditorialLayout,
): string => {
  const text = captions[0]?.text.replace(/\s|[，。！？：；,.!?:;]/g, "") ?? "";
  if (layout === "split-column" && text.includes("改变生活")) return "改变生活";
  if (
    layout === "scale-contrast" &&
    (text.includes("小动作") || text.includes("很小的动作"))
  )
    return "小动作";
  if (layout === "full-bleed-turn" && text.includes("转向")) return "转向";
  if (layout === "quiet-asymmetry" && text.includes("小选择")) return "小选择";
  if (layout === "staggered-notes" && text.includes("早睡十分钟")) return "三件小事";
  return [...text].slice(0, 6).join("");
};

export const DirectionAAtlasCrop: React.FC<{
  name: string;
  source: string;
  crop: Crop;
  targetWidth: number;
  targetHeight: number;
  drift?: number;
}> = ({ name, source, crop, targetWidth, targetHeight, drift = 0 }) => {
  const frame = useCurrentFrame();
  const scale = Math.max(targetWidth / crop.width, targetHeight / crop.height);
  const imageWidth = ATLAS_WIDTH * scale;
  const imageHeight = ATLAS_HEIGHT * scale;
  const imageLeft = targetWidth / 2 - (crop.x + crop.width / 2) * scale;
  const imageTop = targetHeight / 2 - (crop.y + crop.height / 2) * scale;
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
      <Img
        name={name}
        src={staticFile(source)}
        style={{
          position: "absolute",
          left: imageLeft,
          top: imageTop,
          width: imageWidth,
          height: imageHeight,
          maxWidth: "none",
          translate: `${interpolate(frame, [0, 120], [-drift, drift], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })}px 0px`,
        }}
      />
    </div>
  );
};

const Photo: React.FC<{
  name: string;
  source: string | undefined;
  left: number;
  top: number;
  width: number;
  height: number;
  rotate?: number;
  enterFrom?: number;
  delay?: number;
  crop: Crop;
}> = ({
  name,
  source,
  left,
  top,
  width,
  height,
  rotate = 0,
  enterFrom = 0,
  delay = 0,
  crop,
}) => {
  const frame = useCurrentFrame();
  if (!source) return null;
  const border = Math.max(7, Math.min(width, height) * 0.028);
  const innerWidth = width - border * 2;
  const innerHeight = height - border * 2;
  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width,
        height,
        border: `${border}px solid #FFFDF7`,
        boxSizing: "border-box",
        overflow: "hidden",
        backgroundColor: "#FFFDF7",
        boxShadow: "10px 13px 0 rgba(42,37,32,0.18)",
        rotate: `${rotate}deg`,
        opacity: interpolate(frame, [delay, delay + 7], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.16, 1, 0.3, 1),
        }),
        translate: `${interpolate(frame, [delay, delay + 9], [enterFrom, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.16, 1, 0.3, 1),
        })}px 0px`,
      }}
      data-layer-name={name}
    >
      <DirectionAAtlasCrop
        name={`${name} atlas crop`}
        source={source}
        crop={crop}
        targetWidth={innerWidth}
        targetHeight={innerHeight}
        drift={3}
      />
    </div>
  );
};

const Copy: React.FC<{
  captions: ContractCaption[];
  family: string;
  color: string;
  align?: "left" | "right" | "center";
  size: number;
}> = ({ captions, family, color, align = "left", size }) => (
  <div
    style={{
      color,
      fontFamily: family,
      fontSize: size,
      fontWeight: 750,
      lineHeight: 1.24,
      textAlign: align,
      whiteSpace: "pre-wrap",
      overflow: "hidden",
    }}
  >
    {captions.slice(0, 2).map((caption) => (
      <div key={`${caption.cueId}-${caption.trackId}`}>{caption.text}</div>
    ))}
  </div>
);

export const EditorialPaperScene: React.FC<{
  segment: ContractSegment;
  segmentIndex: number;
  durationInFrames: number;
  captions: ContractCaption[];
  family: string;
  layout: EditorialLayout;
  theme: PaperCollageTheme;
}> = ({
  segment,
  segmentIndex,
  durationInFrames,
  captions,
  family,
  layout,
  theme,
}) => {
  const frame = useCurrentFrame();
  const { fps, height, width } = useVideoConfig();
  const absoluteMs = ((segment.startFrame + frame) * 1000) / fps;
  const active = captions
    .filter(
      (caption) =>
        caption.startMs <= absoluteMs && absoluteMs < caption.endMs,
    )
    .sort((left, right) => left.trackId.localeCompare(right.trackId));
  const fallback = captions
    .filter((caption) => segment.captionRefs.includes(caption.cueId))
    .sort((left, right) => left.trackId.localeCompare(right.trackId));
  const copy = active.length > 0 ? active : fallback;
  const source = segment.visualRefs[0];
  const unit = Math.min(width / 720, height / 960);
  const lastFrame = Math.max(1, durationInFrames - 1);
  const label = String(segmentIndex + 1).padStart(2, "0");
  const keyword = keywordFor(copy, layout);
  const actions = ["早睡十分钟", "拒绝一次迎合", "承认自己的不舒服"];

  if (layout === "split-column") {
    return (
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            left: "4%",
            top: "6%",
            width: "61%",
            height: "86%",
            overflow: "hidden",
            backgroundColor: theme.canvas.ink,
            clipPath: "polygon(0 2%, 96% 0, 100% 98%, 3% 100%)",
            translate: `${interpolate(frame, [0, lastFrame], [-5, 4], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })}px 0px`,
          }}
        >
          {source ? (
            <DirectionAAtlasCrop
              name="Split column torn-paper crop"
              source={source}
              crop={DIRECTION_A_HOOK_CROP}
              targetWidth={width * 0.61}
              targetHeight={height * 0.86}
              drift={4}
            />
          ) : null}
        </div>
        <div
          style={{
            position: "absolute",
            right: "4%",
            top: "4%",
            width: "38%",
            height: "88%",
            boxSizing: "border-box",
            padding: "9% 4% 5%",
            backgroundColor: theme.canvas.ink,
            color: theme.canvas.background,
            opacity: interpolate(frame, [2, 10], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
            translate: `${interpolate(frame, [2, 10], [18, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            })}px 0px`,
          }}
        >
          <div style={{ fontFamily: family, fontSize: 13 * unit, letterSpacing: 1.4 }}>
            EDITORIAL / {label}
          </div>
          <div style={{ marginTop: "42%" }}>
            <div style={{ fontFamily: family, fontSize: 43 * unit, fontWeight: 850, lineHeight: 1.05 }}>
              {keyword}
            </div>
            <div style={{ marginTop: "16%" }}>
              <Copy captions={copy} family={family} color={theme.canvas.background} size={23 * unit} />
            </div>
          </div>
          <div style={{ width: "42%", height: 4 * unit, marginTop: "16%", backgroundColor: theme.canvas.accent }} />
        </div>
      </AbsoluteFill>
    );
  }

  if (layout === "scale-contrast") {
    return (
      <AbsoluteFill>
        <div style={{ position: "absolute", left: 0, top: 0, width: "24%", height: "100%", backgroundColor: "#244C68" }} />
        <div
          style={{
            position: "absolute",
            left: "7%",
            top: "16%",
            width: "28%",
            minHeight: "22%",
            padding: "4% 3%",
            boxSizing: "border-box",
            backgroundColor: "#244C68",
            color: "#FFFDF7",
            fontFamily: family,
            fontSize: 29 * unit,
            fontWeight: 800,
            lineHeight: 1.16,
            zIndex: 3,
          }}
        >
          {keyword || label}
        </div>
        <Photo name="Scale contrast image" source={source} left={width * 0.24} top={height * 0.08} width={width * 0.7} height={height * 0.67} rotate={-1.1} enterFrom={16} crop={SWITCH_CROP} />
        <div
          style={{
            position: "absolute",
            left: "35%",
            right: "7%",
            bottom: "8%",
            maxHeight: "20%",
            borderBottom: `4px solid ${theme.canvas.accent}`,
            paddingBottom: "3%",
          }}
        >
          <Copy captions={copy.slice(1).length ? copy.slice(1) : copy} family={family} color={theme.canvas.ink} size={31 * unit} />
        </div>
      </AbsoluteFill>
    );
  }

  if (layout === "staggered-notes") {
    return (
      <AbsoluteFill>
        <div style={{ position: "absolute", left: "5%", top: "4%", padding: "1% 2%", backgroundColor: theme.canvas.ink, color: theme.canvas.background, fontFamily: family, fontSize: 13 * unit }}>
          THREE CUTS / {label}
        </div>
        <div style={{ position: "absolute", right: "6%", top: "5%", color: theme.canvas.accent, fontFamily: family, fontSize: 28 * unit, fontWeight: 850 }}>
          {keyword}
        </div>
        <Photo name="Clock editorial crop" source={source} left={width * 0.07} top={height * 0.12} width={width * 0.48} height={height * 0.25} rotate={1.2} enterFrom={-16} delay={0} crop={CLOCK_CROP} />
        <Photo name="Stop-hand editorial crop" source={source} left={width * 0.45} top={height * 0.39} width={width * 0.48} height={height * 0.24} rotate={-1.1} enterFrom={18} delay={4} crop={HAND_CROP} />
        <Photo name="Paper-heart close-up" source={source} left={width * 0.07} top={height * 0.66} width={width * 0.46} height={height * 0.24} rotate={0.8} enterFrom={-14} delay={8} crop={HEART_CROP} />
        <div style={{ position: "absolute", right: "6%", top: "18%", width: "34%", borderTop: "4px solid #244C68", paddingTop: "3%", color: theme.canvas.ink, fontFamily: family, fontSize: 22 * unit, fontWeight: 750 }}>
          {actions[0]}
        </div>
        <div style={{ position: "absolute", left: "7%", top: "45%", width: "32%", borderTop: `4px solid ${theme.canvas.accent}`, paddingTop: "3%", color: theme.canvas.ink, fontFamily: family, fontSize: 22 * unit, fontWeight: 750 }}>
          {actions[1]}
        </div>
        <div style={{ position: "absolute", right: "6%", bottom: "10%", width: "37%", borderTop: "4px solid #244C68", paddingTop: "3%", color: theme.canvas.ink, fontFamily: family, fontSize: 21 * unit, fontWeight: 750 }}>
          {actions[2]}
        </div>
      </AbsoluteFill>
    );
  }

  if (layout === "full-bleed-turn") {
    return (
      <AbsoluteFill>
        <div style={{ position: "absolute", left: "3%", top: "4%", width: "94%", height: "88%", overflow: "hidden", backgroundColor: theme.canvas.ink }}>
          {source ? (
            <DirectionAAtlasCrop
              name="Full-bleed bending-road crop"
              source={source}
              crop={ROAD_CROP}
              targetWidth={width * 0.94}
              targetHeight={height * 0.88}
              drift={6}
            />
          ) : null}
        </div>
        <div style={{ position: "absolute", left: "3%", top: "4%", width: "78%", minHeight: "16%", padding: "4%", boxSizing: "border-box", backgroundColor: "rgba(42,37,32,0.92)" }}>
          <Copy captions={copy.slice(0, 1)} family={family} color={theme.canvas.background} size={30 * unit} />
        </div>
        <div
          style={{
            position: "absolute",
            right: "3%",
            bottom: "3%",
            width: "32%",
            height: "34%",
            clipPath: "polygon(25% 0, 100% 0, 100% 100%, 0 100%)",
            backgroundColor: theme.canvas.accent,
            opacity: interpolate(frame, [5, 13], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <div style={{ position: "absolute", right: "13%", bottom: "12%", left: "26%" }}>
            <div style={{ color: "#FFFDF7", fontFamily: family, fontSize: 44 * unit, fontWeight: 850, lineHeight: 1.05, textAlign: "right" }}>
              {keyword}
            </div>
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: "4%", top: "5%", width: "69%", height: "87%", overflow: "hidden", clipPath: "polygon(1% 0, 98% 2%, 100% 98%, 0 100%)" }}>
        {source ? (
          <DirectionAAtlasCrop
            name="Quiet asymmetry walker crop"
            source={source}
            crop={WALKER_CROP}
            targetWidth={width * 0.69}
            targetHeight={height * 0.87}
            drift={3}
          />
        ) : null}
      </div>
      <div style={{ position: "absolute", right: "5%", top: "10%", width: "27%", color: "#244C68", fontFamily: family, fontSize: 13 * unit, letterSpacing: 1.2 }}>
        AFTER / {label}
      </div>
      <div
        style={{
          position: "absolute",
          right: "3%",
          top: "24%",
          width: "31%",
          maxHeight: "50%",
          padding: "4% 3%",
          boxSizing: "border-box",
          backgroundColor: "rgba(255,253,247,0.94)",
          boxShadow: "8px 10px 0 rgba(42,37,32,0.12)",
          zIndex: 2,
        }}
      >
        <div style={{ color: theme.canvas.accent, fontFamily: family, fontSize: 35 * unit, fontWeight: 850, lineHeight: 1.08, marginBottom: "14%" }}>
          {keyword}
        </div>
        <Copy captions={copy} family={family} color={theme.canvas.ink} size={28 * unit} />
        <div style={{ width: "100%", height: 4 * unit, marginTop: "18%", backgroundColor: "#DDA52D" }} />
      </div>
    </AbsoluteFill>
  );
};
