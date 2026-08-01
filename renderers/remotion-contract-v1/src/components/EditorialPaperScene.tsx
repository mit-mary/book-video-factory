import type { EditorialSceneType } from "../contract/editorial-paper-types";
import type { PaperCollageTheme } from "../contract/paper-collage-types";
import type { ContractSegment } from "../contract/types";
import { EditorialDetail } from "./editorial-unified/EditorialDetail";
import { FullBleedMetaphor } from "./editorial-unified/FullBleedMetaphor";
import { SequentialBuild } from "./editorial-unified/SequentialBuild";

export const EditorialPaperScene: React.FC<{
  segment: ContractSegment;
  segmentIndex: number;
  durationInFrames: number;
  family: string;
  sceneType: EditorialSceneType;
  theme: PaperCollageTheme;
}> = ({ segment, segmentIndex, durationInFrames, family, sceneType, theme }) => {
  const source = segment.visualRefs[0];
  if (sceneType === "editorial-detail") {
    return <EditorialDetail source={source} durationInFrames={durationInFrames} family={family} theme={theme} />;
  }
  if (sceneType === "sequential-build") {
    return <SequentialBuild source={source} durationInFrames={durationInFrames} family={family} theme={theme} />;
  }
  return <FullBleedMetaphor source={source} segmentIndex={segmentIndex} durationInFrames={durationInFrames} family={family} theme={theme} />;
};
