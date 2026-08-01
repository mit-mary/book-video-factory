import type { ContractProps } from "./types";
import type { PaperCollageTheme } from "./paper-collage-types";

export const EDITORIAL_SCENE_TYPES = [
  "full-bleed-metaphor",
  "editorial-detail",
  "sequential-build",
] as const;

export const EDITORIAL_SCENE_SEQUENCE = [
  "full-bleed-metaphor",
  "editorial-detail",
  "sequential-build",
  "full-bleed-metaphor",
  "full-bleed-metaphor",
] as const;

export type EditorialSceneType = (typeof EDITORIAL_SCENE_TYPES)[number];

export type EditorialPaperCollageProps = Omit<ContractProps, "rendererExtension"> & {
  rendererExtension: {
    schemaVersion: "1.0";
    compositionId: "EditorialPaperCollageV1";
    template: {
      id: "editorial-paper-collage-v1";
      version: "0.2.0-experimental";
    };
    theme: {
      assetId: string;
      src: string;
      sha256: string;
      tokens: PaperCollageTheme;
    };
    motionPreset: "editorial-unified-v1";
    transitionPreset: "hard-cut-paper-reveal";
    captionPreset: "fixed-safe-zone-two-line";
    requiredCapabilities: string[];
    sceneTypeSequence: EditorialSceneType[];
    opening: {
      startFrame: number;
      endFrame: number;
      title: string;
      subtitle: string;
    };
  };
};
