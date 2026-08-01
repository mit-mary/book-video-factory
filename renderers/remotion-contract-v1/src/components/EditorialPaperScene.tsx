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

const Photo: React.FC<{
  name: string;
  source: string | undefined;
  left: string;
  top: string;
  width: string;
  height: string;
  rotate?: number;
  objectPosition?: string;
  enterFrom?: number;
  delay?: number;
}> = ({
  name,
  source,
  left,
  top,
  width,
  height,
  rotate = 0,
  objectPosition = "center",
  enterFrom = 0,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  if (!source) return null;
  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width,
        height,
        padding: "1.4%",
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
      <Img
        src={staticFile(source)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition,
        }}
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

  if (layout === "split-column") {
    return (
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            left: "5%",
            top: "8%",
            width: "55%",
            height: "80%",
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
            <Img
              src={staticFile(source)}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          ) : null}
        </div>
        <div
          style={{
            position: "absolute",
            right: "5%",
            top: "5%",
            width: "37%",
            height: "86%",
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
          <div style={{ marginTop: "48%" }}>
            <Copy captions={copy} family={family} color={theme.canvas.background} size={37 * unit} />
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
          {copy[0]?.text ?? label}
        </div>
        <Photo name="Scale contrast image" source={source} left="25%" top="12%" width="68%" height="63%" rotate={-1.1} enterFrom={16} />
        <div
          style={{
            position: "absolute",
            left: "35%",
            right: "7%",
            bottom: "10%",
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
        <Photo name="Top editorial crop" source={source} left="8%" top="12%" width="51%" height="25%" rotate={1.2} objectPosition="center 25%" enterFrom={-16} delay={0} />
        <Photo name="Middle editorial crop" source={source} left="43%" top="39%" width="49%" height="24%" rotate={-1.1} objectPosition="center" enterFrom={18} delay={4} />
        <Photo name="Detail close-up" source={source} left="8%" top="65%" width="46%" height="24%" rotate={0.8} objectPosition="center 75%" enterFrom={-14} delay={8} />
        <div style={{ position: "absolute", right: "6%", top: "17%", width: "31%", maxHeight: "18%", borderTop: "4px solid #244C68", paddingTop: "3%" }}>
          <Copy captions={copy.slice(0, 1)} family={family} color={theme.canvas.ink} size={24 * unit} />
        </div>
        <div style={{ position: "absolute", right: "6%", bottom: "12%", width: "35%", maxHeight: "18%", borderTop: `4px solid ${theme.canvas.accent}`, paddingTop: "3%" }}>
          <Copy captions={copy.slice(1).length ? copy.slice(1) : copy} family={family} color={theme.canvas.ink} size={24 * unit} />
        </div>
      </AbsoluteFill>
    );
  }

  if (layout === "full-bleed-turn") {
    return (
      <AbsoluteFill>
        <div style={{ position: "absolute", left: "4%", top: "8%", width: "92%", height: "79%", overflow: "hidden", backgroundColor: theme.canvas.ink }}>
          {source ? (
            <Img
              src={staticFile(source)}
              style={{
                width: "104%",
                height: "100%",
                objectFit: "cover",
                translate: `${interpolate(frame, [0, lastFrame], [-12, 0], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                })}px 0px`,
              }}
            />
          ) : null}
        </div>
        <div style={{ position: "absolute", left: "4%", top: "5%", width: "78%", minHeight: "16%", padding: "4%", boxSizing: "border-box", backgroundColor: theme.canvas.ink }}>
          <Copy captions={copy.slice(0, 1)} family={family} color={theme.canvas.background} size={30 * unit} />
        </div>
        <div
          style={{
            position: "absolute",
            right: "4%",
            bottom: "7%",
            width: "30%",
            height: "32%",
            clipPath: "polygon(25% 0, 100% 0, 100% 100%, 0 100%)",
            backgroundColor: theme.canvas.accent,
            opacity: interpolate(frame, [5, 13], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <div style={{ position: "absolute", right: "13%", bottom: "12%", left: "26%" }}>
            <Copy captions={copy.slice(1).length ? copy.slice(1) : copy} family={family} color="#FFFDF7" align="right" size={32 * unit} />
          </div>
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: "5%", top: "7%", width: "66%", height: "82%", overflow: "hidden", clipPath: "polygon(1% 0, 98% 2%, 100% 98%, 0 100%)" }}>
        {source ? (
          <Img
            src={staticFile(source)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              scale: interpolate(frame, [0, lastFrame], [1, 1.02], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
            }}
          />
        ) : null}
      </div>
      <div style={{ position: "absolute", right: "5%", top: "10%", width: "27%", color: "#244C68", fontFamily: family, fontSize: 13 * unit, letterSpacing: 1.2 }}>
        AFTER / {label}
      </div>
      <div style={{ position: "absolute", right: "5%", top: "29%", width: "27%", maxHeight: "42%" }}>
        <Copy captions={copy} family={family} color={theme.canvas.ink} size={28 * unit} />
        <div style={{ width: "100%", height: 4 * unit, marginTop: "18%", backgroundColor: "#DDA52D" }} />
      </div>
    </AbsoluteFill>
  );
};
