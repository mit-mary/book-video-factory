import type { ContractProps } from "./types";
import type { PaperCollageTheme } from "./paper-collage-types";

export const EDITORIAL_LAYOUTS = [
  "split-column",
  "scale-contrast",
  "staggered-notes",
  "full-bleed-turn",
  "quiet-asymmetry",
] as const;

export type EditorialLayout = (typeof EDITORIAL_LAYOUTS)[number];

export type EditorialPaperCollageProps = Omit<ContractProps, "rendererExtension"> & {
  rendererExtension: {
    schemaVersion: "1.0";
    compositionId: "EditorialPaperCollageV1";
    template: {
      id: "editorial-paper-collage-v1";
      version: "0.1.0-experimental";
    };
    theme: {
      assetId: string;
      src: string;
      sha256: string;
      tokens: PaperCollageTheme;
    };
    motionPreset: "editorial-purposeful";
    transitionPreset: "paper-cut-column-wipe";
    captionPreset: "integrated-two-line";
    requiredCapabilities: string[];
    layoutSequence: EditorialLayout[];
    opening: {
      startFrame: number;
      endFrame: number;
      title: string;
      subtitle: string;
    };
  };
};
