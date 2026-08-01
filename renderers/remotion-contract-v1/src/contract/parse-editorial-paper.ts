import { EDITORIAL_LAYOUTS } from "./editorial-paper-types";
import type {
  EditorialLayout,
  EditorialPaperCollageProps,
} from "./editorial-paper-types";
import { exactKeys, validateThemeRanges } from "./paper-collage-layout";
import { parsePaperCollageTheme } from "./parse-paper-collage";
import { parseContractProps } from "./parse-props";

const SHA256 = /^[0-9a-f]{64}$/;
const PORTABLE = /^(?!\/)(?!.*(?:^|\/)\.\.(?:\/|$))[A-Za-z0-9._\-/]+$/;

const record = (value: unknown, field: string): Record<string, unknown> => {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`${field} must be an object`);
  }
  return value as Record<string, unknown>;
};

const string = (value: unknown, field: string): string => {
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`${field} must be a non-empty string`);
  }
  return value;
};

const portable = (value: unknown, field: string): string => {
  const parsed = string(value, field);
  if (!PORTABLE.test(parsed) || parsed.includes("\\") || /^[A-Za-z]:/.test(parsed)) {
    throw new Error(`${field} must be a portable public-relative path`);
  }
  return parsed;
};

const integer = (value: unknown, field: string): number => {
  if (!Number.isInteger(value)) throw new Error(`${field} must be an integer`);
  return value as number;
};

const parseLayouts = (value: unknown): EditorialLayout[] => {
  if (!Array.isArray(value) || value.length !== EDITORIAL_LAYOUTS.length) {
    throw new Error("layoutSequence must bind exactly five layouts");
  }
  const layouts = value.map((item, index) =>
    string(item, `layoutSequence[${index}]`),
  );
  if (
    layouts.some((item, index) => item !== EDITORIAL_LAYOUTS[index]) ||
    new Set(layouts).size !== EDITORIAL_LAYOUTS.length
  ) {
    throw new Error("layoutSequence must match the approved Direction A order");
  }
  return layouts as EditorialLayout[];
};

export const parseEditorialPaperProps = (
  value: unknown,
): EditorialPaperCollageProps => {
  const base = parseContractProps(value);
  const raw = record(value, "props");
  const extension = record(raw.rendererExtension, "rendererExtension");
  exactKeys(
    extension,
    [
      "schemaVersion",
      "compositionId",
      "template",
      "theme",
      "motionPreset",
      "transitionPreset",
      "captionPreset",
      "requiredCapabilities",
      "layoutSequence",
      "opening",
    ],
    "rendererExtension",
  );
  if (
    extension.schemaVersion !== "1.0" ||
    extension.compositionId !== "EditorialPaperCollageV1"
  ) {
    throw new Error("editorial-paper composition identity mismatch");
  }
  const template = record(extension.template, "rendererExtension.template");
  const theme = record(extension.theme, "rendererExtension.theme");
  const opening = record(extension.opening, "rendererExtension.opening");
  exactKeys(template, ["id", "version"], "rendererExtension.template");
  exactKeys(theme, ["assetId", "src", "sha256", "tokens"], "rendererExtension.theme");
  exactKeys(opening, ["startFrame", "endFrame", "title", "subtitle"], "rendererExtension.opening");
  if (
    template.id !== "editorial-paper-collage-v1" ||
    template.version !== "0.1.0-experimental"
  ) {
    throw new Error("unknown editorial-paper template identity");
  }
  if (extension.motionPreset !== "editorial-purposeful") {
    throw new Error("unsupported editorial motion preset");
  }
  if (extension.transitionPreset !== "paper-cut-column-wipe") {
    throw new Error("unsupported editorial transition preset");
  }
  if (extension.captionPreset !== "integrated-two-line") {
    throw new Error("unsupported editorial caption preset");
  }
  if (!Array.isArray(extension.requiredCapabilities)) {
    throw new Error("requiredCapabilities must be an array");
  }
  const requiredCapabilities = extension.requiredCapabilities.map((item, index) =>
    string(item, `requiredCapabilities[${index}]`),
  );
  for (const capability of ["layered_images", "camera_motion", "transitions"]) {
    if (!requiredCapabilities.includes(capability)) {
      throw new Error(`template capability ${capability} is missing`);
    }
  }
  const themeSha = string(theme.sha256, "theme.sha256");
  if (!SHA256.test(themeSha)) throw new Error("theme.sha256 must be lowercase SHA-256");
  const tokens = parsePaperCollageTheme(theme.tokens);
  validateThemeRanges(tokens);
  const openingStart = integer(opening.startFrame, "opening.startFrame");
  const openingEnd = integer(opening.endFrame, "opening.endFrame");
  const openingFrames = openingEnd - openingStart;
  if (
    openingStart !== 0 ||
    openingEnd > base.durationInFrames ||
    openingFrames < base.fps ||
    openingFrames * 2 > base.fps * 3
  ) {
    throw new Error("opening must cover 1.0-1.5 seconds from frame zero");
  }
  if (base.width < 600 || base.height < 800) {
    throw new Error("editorial-paper canvas is below the validated minimum");
  }
  const captionHeight =
    Math.ceil((tokens.caption.fontSize * tokens.caption.lineHeightMilli) / 1000) *
      tokens.caption.maxLines +
    tokens.caption.paddingY * 2;
  if (captionHeight * 100 > base.height * 22 || base.captionStyle.maxLines !== 2) {
    throw new Error("integrated caption exceeds the 22 percent/two-line contract");
  }
  if (
    tokens.canvas.safeMarginX <
      Math.max(base.captionStyle.leftPx, base.captionStyle.rightPx) ||
    tokens.canvas.safeMarginBottom < base.captionStyle.bottomPx
  ) {
    throw new Error("theme cannot bypass contract caption safety");
  }
  for (const caption of base.captions) {
    if (caption.text.split("\n").length > 2) {
      throw new Error("caption exceeds the approved two-line limit");
    }
  }
  return {
    ...base,
    rendererExtension: {
      schemaVersion: "1.0",
      compositionId: "EditorialPaperCollageV1",
      template: {
        id: "editorial-paper-collage-v1",
        version: "0.1.0-experimental",
      },
      theme: {
        assetId: string(theme.assetId, "theme.assetId"),
        src: portable(theme.src, "theme.src"),
        sha256: themeSha,
        tokens,
      },
      motionPreset: "editorial-purposeful",
      transitionPreset: "paper-cut-column-wipe",
      captionPreset: "integrated-two-line",
      requiredCapabilities,
      layoutSequence: parseLayouts(extension.layoutSequence),
      opening: {
        startFrame: openingStart,
        endFrame: openingEnd,
        title: string(opening.title, "opening.title"),
        subtitle: string(opening.subtitle, "opening.subtitle"),
      },
    },
  };
};
