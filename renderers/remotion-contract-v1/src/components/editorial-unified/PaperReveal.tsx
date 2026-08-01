import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export const PaperReveal: React.FC<{ color: string }> = ({ color }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        overflow: "hidden",
        pointerEvents: "none",
        zIndex: 8,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: -width * 0.04,
          top: 0,
          width: width * 1.08,
          height: "100%",
          backgroundColor: color,
          clipPath:
            "polygon(0 0, 98% 0, 100% 8%, 97% 18%, 100% 29%, 97% 42%, 100% 55%, 98% 69%, 100% 82%, 97% 92%, 100% 100%, 0 100%)",
          translate: `${interpolate(frame, [0, 6], [0, width * 1.14], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })}px 0px`,
        }}
      />
    </div>
  );
};
