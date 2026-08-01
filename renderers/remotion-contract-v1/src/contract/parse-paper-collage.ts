import { parseContractProps } from "./parse-props";
import { exactKeys, validatePaperCollageLayout, validateThemeRanges } from "./paper-collage-layout";
import type { PaperCollageProps, PaperCollageTheme } from "./paper-collage-types";

const SHA256 = /^[0-9a-f]{64}$/;
const PORTABLE = /^(?!\/)(?!.*(?:^|\/)\.\.(?:\/|$))[A-Za-z0-9._\-/]+$/;

const record = (value: unknown, field: string): Record<string, unknown> => {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`${field} must be an object`);
  }
  return value as Record<string, unknown>;
};

const integer = (value: unknown, field: string): number => {
  if (!Number.isInteger(value)) throw new Error(`${field} must be an integer`);
  return value as number;
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

const parseTheme = (value: unknown): PaperCollageTheme => {
  const theme = record(value, "theme.tokens");
  exactKeys(theme, ["schemaVersion", "canvas", "paperTexture", "imageCard", "caption", "motion", "transition"], "theme.tokens");
  if (theme.schemaVersion !== "paper-collage-theme-v1") {
    throw new Error("unsupported paper-collage theme schema");
  }
  const canvas = record(theme.canvas, "theme.tokens.canvas");
  const texture = record(theme.paperTexture, "theme.tokens.paperTexture");
  const imageCard = record(theme.imageCard, "theme.tokens.imageCard");
  const caption = record(theme.caption, "theme.tokens.caption");
  const motion = record(theme.motion, "theme.tokens.motion");
  const transition = record(theme.transition, "theme.tokens.transition");
  exactKeys(canvas, ["background", "ink", "accent", "safeMarginX", "safeMarginTop", "safeMarginBottom"], "theme.tokens.canvas");
  exactKeys(texture, ["assetId", "src", "sha256", "opacityMilli"], "theme.tokens.paperTexture");
  exactKeys(imageCard, ["maxWidth", "maxHeight", "padding", "borderWidth", "shadowOffsetX", "shadowOffsetY", "rotationMillidegrees"], "theme.tokens.imageCard");
  exactKeys(caption, ["maxLines", "fontSize", "lineHeightMilli", "paddingX", "paddingY", "background", "text"], "theme.tokens.caption");
  exactKeys(motion, ["maxScaleDeltaMilli", "maxTranslateX", "maxTranslateY", "maxRotationMillidegrees"], "theme.tokens.motion");
  exactKeys(transition, ["durationFrames", "maxTranslatePx"], "theme.tokens.transition");
  const parsed: PaperCollageTheme = {
    schemaVersion: "paper-collage-theme-v1",
    canvas: {
      background: string(canvas.background, "canvas.background"),
      ink: string(canvas.ink, "canvas.ink"),
      accent: string(canvas.accent, "canvas.accent"),
      safeMarginX: integer(canvas.safeMarginX, "canvas.safeMarginX"),
      safeMarginTop: integer(canvas.safeMarginTop, "canvas.safeMarginTop"),
      safeMarginBottom: integer(canvas.safeMarginBottom, "canvas.safeMarginBottom"),
    },
    paperTexture: {
      assetId: string(texture.assetId, "paperTexture.assetId"),
      src: portable(texture.src, "paperTexture.src"),
      sha256: string(texture.sha256, "paperTexture.sha256"),
      opacityMilli: integer(texture.opacityMilli, "paperTexture.opacityMilli"),
    },
    imageCard: {
      maxWidth: integer(imageCard.maxWidth, "imageCard.maxWidth"),
      maxHeight: integer(imageCard.maxHeight, "imageCard.maxHeight"),
      padding: integer(imageCard.padding, "imageCard.padding"),
      borderWidth: integer(imageCard.borderWidth, "imageCard.borderWidth"),
      shadowOffsetX: integer(imageCard.shadowOffsetX, "imageCard.shadowOffsetX"),
      shadowOffsetY: integer(imageCard.shadowOffsetY, "imageCard.shadowOffsetY"),
      rotationMillidegrees: integer(imageCard.rotationMillidegrees, "imageCard.rotationMillidegrees"),
    },
    caption: {
      maxLines: integer(caption.maxLines, "caption.maxLines"),
      fontSize: integer(caption.fontSize, "caption.fontSize"),
      lineHeightMilli: integer(caption.lineHeightMilli, "caption.lineHeightMilli"),
      paddingX: integer(caption.paddingX, "caption.paddingX"),
      paddingY: integer(caption.paddingY, "caption.paddingY"),
      background: string(caption.background, "caption.background"),
      text: string(caption.text, "caption.text"),
    },
    motion: {
      maxScaleDeltaMilli: integer(motion.maxScaleDeltaMilli, "motion.maxScaleDeltaMilli"),
      maxTranslateX: integer(motion.maxTranslateX, "motion.maxTranslateX"),
      maxTranslateY: integer(motion.maxTranslateY, "motion.maxTranslateY"),
      maxRotationMillidegrees: integer(motion.maxRotationMillidegrees, "motion.maxRotationMillidegrees"),
    },
    // Static validated token data; this is not a CSS transition.
    // eslint-disable-next-line @remotion/non-pure-animation
    transition: {
      durationFrames: integer(transition.durationFrames, "transition.durationFrames"),
      maxTranslatePx: integer(transition.maxTranslatePx, "transition.maxTranslatePx"),
    },
  };
  if (!SHA256.test(parsed.paperTexture.sha256)) {
    throw new Error("paperTexture.sha256 must be lowercase SHA-256");
  }
  validateThemeRanges(parsed);
  return parsed;
};

export const parsePaperCollageProps = (value: unknown): PaperCollageProps => {
  const base = parseContractProps(value);
  const raw = record(value, "props");
  const extension = record(raw.rendererExtension, "rendererExtension");
  exactKeys(extension, ["schemaVersion", "compositionId", "template", "theme", "motionPreset", "transitionPreset", "captionPreset", "requiredCapabilities", "opening"], "rendererExtension");
  if (extension.schemaVersion !== "1.0" || extension.compositionId !== "PaperCollageVisualV1") {
    throw new Error("paper-collage composition identity mismatch");
  }
  const template = record(extension.template, "rendererExtension.template");
  const theme = record(extension.theme, "rendererExtension.theme");
  const opening = record(extension.opening, "rendererExtension.opening");
  exactKeys(template, ["id", "version"], "rendererExtension.template");
  exactKeys(theme, ["assetId", "src", "sha256", "tokens"], "rendererExtension.theme");
  exactKeys(opening, ["startFrame", "endFrame", "title", "subtitle"], "rendererExtension.opening");
  if (template.id !== "paper-collage-visual-v1" || template.version !== "0.1.0-experimental") {
    throw new Error("unknown paper-collage template identity");
  }
  if (extension.motionPreset !== "subtle") throw new Error("unsupported motion preset");
  if (extension.transitionPreset !== "paper-cut") throw new Error("unsupported transition preset");
  if (extension.captionPreset !== "bottom-card") throw new Error("unsupported caption preset");
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
  const parsed: PaperCollageProps = {
    ...base,
    rendererExtension: {
      schemaVersion: "1.0",
      compositionId: "PaperCollageVisualV1",
      template: { id: "paper-collage-visual-v1", version: "0.1.0-experimental" },
      theme: {
        assetId: string(theme.assetId, "theme.assetId"),
        src: portable(theme.src, "theme.src"),
        sha256: themeSha,
        tokens: parseTheme(theme.tokens),
      },
      motionPreset: "subtle",
      transitionPreset: "paper-cut",
      captionPreset: "bottom-card",
      requiredCapabilities,
      opening: {
        startFrame: integer(opening.startFrame, "opening.startFrame"),
        endFrame: integer(opening.endFrame, "opening.endFrame"),
        title: string(opening.title, "opening.title"),
        subtitle: string(opening.subtitle, "opening.subtitle"),
      },
    },
  };
  const openingFrames = parsed.rendererExtension.opening.endFrame - parsed.rendererExtension.opening.startFrame;
  if (
    parsed.rendererExtension.opening.startFrame !== 0 ||
    parsed.rendererExtension.opening.endFrame > parsed.durationInFrames ||
    openingFrames < parsed.fps ||
    openingFrames * 2 > parsed.fps * 3
  ) {
    throw new Error("opening must cover 1.0-1.5 seconds from frame zero");
  }
  validatePaperCollageLayout(parsed);
  return parsed;
};
