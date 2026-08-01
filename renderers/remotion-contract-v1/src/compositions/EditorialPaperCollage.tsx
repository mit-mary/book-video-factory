import { loadFont } from "@remotion/fonts";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Img, Sequence, staticFile, useVideoConfig } from "remotion";

import { EditorialPaperScene } from "../components/EditorialPaperScene";
import { UnifiedCaption } from "../components/editorial-unified/UnifiedCaption";
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
          name={`Unified scene ${String(index + 1).padStart(2, "0")} ${props.rendererExtension.sceneTypeSequence[index % props.rendererExtension.sceneTypeSequence.length]}`}
        >
          <EditorialPaperScene
            segment={segment}
            segmentIndex={index}
            durationInFrames={segment.endFrame - segment.startFrame}
            family={props.font.family}
            sceneType={
              props.rendererExtension.sceneTypeSequence[
                index % props.rendererExtension.sceneTypeSequence.length
              ]
            }
            theme={theme}
          />
        </Sequence>
      ))}
      <UnifiedCaption captions={props.captions} family={props.font.family} theme={theme} />
      <Audio src={staticFile(props.audio.src)} />
    </AbsoluteFill>
  );
};
