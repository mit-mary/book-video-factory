import { loadFont } from "@remotion/fonts";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Img, Sequence, staticFile, useVideoConfig } from "remotion";

import { EditorialOpening } from "../components/EditorialOpening";
import { EditorialPaperScene } from "../components/EditorialPaperScene";
import { parseEditorialPaperProps } from "../contract/parse-editorial-paper";
import type { EditorialPaperCollageProps } from "../contract/editorial-paper-types";

const fontLoads = new Map<string, Promise<void>>();

const ensureFont = (family: string, source: string): void => {
  const key = `${family}:${source}`;
  if (!fontLoads.has(key)) {
    fontLoads.set(
      key,
      loadFont({
        family,
        url: staticFile(source),
        display: "block",
        format: source.toLowerCase().endsWith(".ttc") ? "truetype" : undefined,
      }),
    );
  }
};

export const EditorialPaperCollage: React.FC<EditorialPaperCollageProps> = (
  rawProps,
) => {
  const props = parseEditorialPaperProps(rawProps);
  const { fps } = useVideoConfig();
  const theme = props.rendererExtension.theme.tokens;
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
      {props.segments.map((segment, index) => (
        <Sequence
          key={segment.segmentId}
          from={segment.startFrame}
          durationInFrames={segment.endFrame - segment.startFrame}
          premountFor={Math.min(fps, segment.startFrame)}
          name={`Editorial ${String(index + 1).padStart(2, "0")} ${props.rendererExtension.layoutSequence[index % props.rendererExtension.layoutSequence.length]}`}
        >
          <EditorialPaperScene
            segment={segment}
            segmentIndex={index}
            durationInFrames={segment.endFrame - segment.startFrame}
            captions={props.captions}
            family={props.font.family}
            layout={
              props.rendererExtension.layoutSequence[
                index % props.rendererExtension.layoutSequence.length
              ]
            }
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
        name="Editorial Opening Hook"
      >
        <EditorialOpening
          family={props.font.family}
          source={props.segments[0]?.visualRefs[0]}
          theme={theme}
          opening={props.rendererExtension.opening}
        />
      </Sequence>
      <Audio src={staticFile(props.audio.src)} />
    </AbsoluteFill>
  );
};
