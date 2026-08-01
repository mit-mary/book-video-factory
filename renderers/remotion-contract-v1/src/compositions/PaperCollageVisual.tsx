import { loadFont } from "@remotion/fonts";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Img, Sequence, staticFile, useVideoConfig } from "remotion";

import { PaperCaptionCard } from "../components/PaperCaptionCard";
import { PaperCollageScene } from "../components/PaperCollageScene";
import { PaperOpeningCard } from "../components/PaperOpeningCard";
import { validatePaperCollageLayout } from "../contract/paper-collage-layout";
import { parsePaperCollageProps } from "../contract/parse-paper-collage";
import type { PaperCollageProps } from "../contract/paper-collage-types";

const fontLoads = new Map<string, Promise<void>>();

const ensureFont = (family: string, source: string): void => {
  const key = `${family}:${source}`;
  if (!fontLoads.has(key)) {
    fontLoads.set(
      key,
      loadFont({ family, url: staticFile(source), display: "block" }),
    );
  }
};

export const PaperCollageVisual: React.FC<PaperCollageProps> = (rawProps) => {
  const props = parsePaperCollageProps(rawProps);
  const { fps } = useVideoConfig();
  const theme = props.rendererExtension.theme.tokens;
  const layout = validatePaperCollageLayout(props);
  ensureFont(props.font.family, props.font.src);
  return (
    <AbsoluteFill style={{ backgroundColor: theme.canvas.background }}>
      <Img
        src={staticFile(theme.paperTexture.src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: theme.paperTexture.opacityMilli / 1000,
        }}
      />
      {props.segments.map((segment) => (
        <Sequence
          key={segment.segmentId}
          from={segment.startFrame}
          durationInFrames={segment.endFrame - segment.startFrame}
          premountFor={Math.min(fps, segment.startFrame)}
          name={`Paper ${segment.segmentId}`}
        >
          <PaperCollageScene
            segment={segment}
            durationInFrames={segment.endFrame - segment.startFrame}
            family={props.font.family}
            layout={layout}
            theme={theme}
          />
        </Sequence>
      ))}
      <Sequence
        from={props.rendererExtension.opening.startFrame}
        durationInFrames={
          props.rendererExtension.opening.endFrame -
          props.rendererExtension.opening.startFrame
        }
        premountFor={Math.min(fps, props.rendererExtension.opening.startFrame)}
        name="Paper Opening"
      >
        <PaperOpeningCard
          family={props.font.family}
          layout={layout}
          theme={theme}
          opening={props.rendererExtension.opening}
        />
      </Sequence>
      <Audio src={staticFile(props.audio.src)} />
      <PaperCaptionCard
        captions={props.captions}
        family={props.font.family}
        layout={layout}
        theme={theme}
      />
    </AbsoluteFill>
  );
};
