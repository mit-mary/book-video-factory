import { parsePaperCollageTheme } from "./paper-collage-contract.mjs";

export const EDITORIAL_LAYOUTS = [
  "split-column",
  "scale-contrast",
  "staggered-notes",
  "full-bleed-turn",
  "quiet-asymmetry",
];

const SHA256 = /^[0-9a-f]{64}$/;
const PORTABLE = /^(?!\/)(?!.*(?:^|\/)\.\.(?:\/|$))[A-Za-z0-9._\-/]+$/;

const record = (value, field) => {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`${field} must be an object`);
  }
  return value;
};

const exactKeys = (value, expected, field) => {
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (actual.length !== wanted.length || actual.some((key, index) => key !== wanted[index])) {
    throw new Error(`${field} contains missing or unknown fields`);
  }
};

const portable = (value, field) => {
  if (typeof value !== "string" || !PORTABLE.test(value) || value.includes("\\") || /^[A-Za-z]:/.test(value)) {
    throw new Error(`${field} must be a portable public-relative path`);
  }
  return value;
};

export const validateEditorialPaperProps = (props) => {
  const extension = record(props.rendererExtension, "rendererExtension");
  exactKeys(extension, ["schemaVersion", "compositionId", "template", "theme", "motionPreset", "transitionPreset", "captionPreset", "requiredCapabilities", "layoutSequence", "opening"], "rendererExtension");
  if (extension.schemaVersion !== "1.0" || extension.compositionId !== "EditorialPaperCollageV1") {
    throw new Error("editorial composition identity mismatch");
  }
  const template = record(extension.template, "template");
  const themeRef = record(extension.theme, "theme");
  const opening = record(extension.opening, "opening");
  exactKeys(template, ["id", "version"], "template");
  exactKeys(themeRef, ["assetId", "src", "sha256", "tokens"], "theme");
  exactKeys(opening, ["startFrame", "endFrame", "title", "subtitle"], "opening");
  if (template.id !== "editorial-paper-collage-v1" || template.version !== "0.1.0-experimental") {
    throw new Error("unknown editorial template identity");
  }
  if (extension.motionPreset !== "editorial-purposeful") throw new Error("unsupported editorial motion preset");
  if (extension.transitionPreset !== "paper-cut-column-wipe") throw new Error("unsupported editorial transition preset");
  if (extension.captionPreset !== "integrated-two-line") throw new Error("unsupported editorial caption preset");
  if (!Array.isArray(extension.layoutSequence) || extension.layoutSequence.length !== 5 || extension.layoutSequence.some((item, index) => item !== EDITORIAL_LAYOUTS[index])) {
    throw new Error("layoutSequence must match the approved Direction A order");
  }
  if (!Array.isArray(extension.requiredCapabilities)) throw new Error("requiredCapabilities must be an array");
  for (const capability of ["layered_images", "camera_motion", "transitions"]) {
    if (!extension.requiredCapabilities.includes(capability)) throw new Error(`template capability ${capability} is missing`);
  }
  if (!SHA256.test(themeRef.sha256 ?? "")) throw new Error("theme hash is invalid");
  portable(themeRef.src, "theme.src");
  const theme = parsePaperCollageTheme(themeRef.tokens);
  if (props.width < 600 || props.height < 800) throw new Error("editorial-paper canvas is below the validated minimum");
  const captionHeight = Math.ceil(theme.caption.fontSize * theme.caption.lineHeightMilli / 1000) * theme.caption.maxLines + theme.caption.paddingY * 2;
  if (captionHeight * 100 > props.height * 22 || props.captionStyle?.maxLines !== 2) {
    throw new Error("integrated caption exceeds the 22 percent/two-line contract");
  }
  if (theme.canvas.safeMarginX < Math.max(props.captionStyle.leftPx, props.captionStyle.rightPx) || theme.canvas.safeMarginBottom < props.captionStyle.bottomPx) {
    throw new Error("theme cannot bypass contract caption safety");
  }
  for (const caption of props.captions) {
    if (String(caption.text).split("\n").length > 2) throw new Error("caption exceeds the approved two-line limit");
  }
  const openingFrames = opening.endFrame - opening.startFrame;
  if (opening.startFrame !== 0 || opening.endFrame > props.durationInFrames || openingFrames < props.fps || openingFrames * 2 > props.fps * 3) {
    throw new Error("opening must cover 1.0-1.5 seconds from frame zero");
  }
  return props;
};
