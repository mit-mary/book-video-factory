const SHA256 = /^[0-9a-f]{64}$/;
const PORTABLE = /^(?!\/)(?!.*(?:^|\/)\.\.(?:\/|$))[A-Za-z0-9._\-/]+$/;
const HEX = /^#[0-9A-F]{6}$/;
const PAPER_BACKING_OFFSET_X = 9;
const PAPER_BACKING_OFFSET_Y = 11;
const PAPER_BACKING_ROTATION_FACTOR = 0.55;
const PAPER_CAPTION_OUTLINE = 2;
const PAPER_CAPTION_SHADOW_X = 7;
const PAPER_CAPTION_SHADOW_Y = 9;
const MIN_RENDERED_IMAGE_CARD = 240;
const IMAGE_CAPTION_GAP = 24;
const SEGMENT_MARKER_HEIGHT = 30;

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

const integer = (value, field) => {
  if (!Number.isInteger(value)) throw new Error(`${field} must be an integer`);
  return value;
};

const string = (value, field) => {
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`${field} must be a non-empty string`);
  }
  return value;
};

const portable = (value, field) => {
  const parsed = string(value, field);
  if (!PORTABLE.test(parsed) || parsed.includes("\\") || /^[A-Za-z]:/.test(parsed)) {
    throw new Error(`${field} must be a portable public-relative path`);
  }
  return parsed;
};

const themeRanges = (theme) => {
  for (const color of [theme.canvas.background, theme.canvas.ink, theme.canvas.accent, theme.caption.background, theme.caption.text]) {
    if (!HEX.test(color)) throw new Error("theme color must be an uppercase hex value");
  }
  if (theme.canvas.safeMarginX < 48 || theme.canvas.safeMarginX > 160 || theme.canvas.safeMarginTop < 48 || theme.canvas.safeMarginTop > 180 || theme.canvas.safeMarginBottom < 64 || theme.canvas.safeMarginBottom > 200) {
    throw new Error("canvas safety token is outside the approved range");
  }
  if (theme.imageCard.maxWidth < 240 || theme.imageCard.maxWidth > 1200 || theme.imageCard.maxHeight < 240 || theme.imageCard.maxHeight > 1600 || theme.imageCard.padding < 8 || theme.imageCard.padding > 40 || theme.imageCard.borderWidth < 1 || theme.imageCard.borderWidth > 6 || Math.abs(theme.imageCard.shadowOffsetX) > 24 || Math.abs(theme.imageCard.shadowOffsetY) > 24 || Math.abs(theme.imageCard.rotationMillidegrees) > 3000) {
    throw new Error("image-card token is outside the approved range");
  }
  if (theme.caption.maxLines !== 2 || theme.caption.fontSize < 28 || theme.caption.fontSize > 64 || theme.caption.lineHeightMilli < 1000 || theme.caption.lineHeightMilli > 1500 || theme.caption.paddingX < 16 || theme.caption.paddingX > 56 || theme.caption.paddingY < 12 || theme.caption.paddingY > 36) {
    throw new Error("caption token is outside the approved range");
  }
  if (theme.motion.maxScaleDeltaMilli < 0 || theme.motion.maxScaleDeltaMilli > 40 || Math.abs(theme.motion.maxTranslateX) > 20 || Math.abs(theme.motion.maxTranslateY) > 16 || Math.abs(theme.motion.maxRotationMillidegrees) > 500) {
    throw new Error("motion token is outside the approved range");
  }
  if (theme.transition.durationFrames < 1 || theme.transition.durationFrames > 8 || Math.abs(theme.transition.maxTranslatePx) > 20 || theme.paperTexture.opacityMilli < 0 || theme.paperTexture.opacityMilli > 250) {
    throw new Error("transition or texture token is outside the approved range");
  }
};

export const parsePaperCollageTheme = (value) => {
  const theme = record(value, "theme.tokens");
  exactKeys(theme, ["schemaVersion", "canvas", "paperTexture", "imageCard", "caption", "motion", "transition"], "theme.tokens");
  if (theme.schemaVersion !== "paper-collage-theme-v1") throw new Error("unsupported theme schema");
  for (const [field, keys] of [
    ["canvas", ["background", "ink", "accent", "safeMarginX", "safeMarginTop", "safeMarginBottom"]],
    ["paperTexture", ["assetId", "src", "sha256", "opacityMilli"]],
    ["imageCard", ["maxWidth", "maxHeight", "padding", "borderWidth", "shadowOffsetX", "shadowOffsetY", "rotationMillidegrees"]],
    ["caption", ["maxLines", "fontSize", "lineHeightMilli", "paddingX", "paddingY", "background", "text"]],
    ["motion", ["maxScaleDeltaMilli", "maxTranslateX", "maxTranslateY", "maxRotationMillidegrees"]],
    ["transition", ["durationFrames", "maxTranslatePx"]],
  ]) {
    exactKeys(record(theme[field], `theme.tokens.${field}`), keys, `theme.tokens.${field}`);
  }
  if (!SHA256.test(theme.paperTexture.sha256 ?? "")) throw new Error("texture hash is invalid");
  portable(theme.paperTexture.src, "paperTexture.src");
  for (const [field, object] of [["canvas", theme.canvas], ["paperTexture", theme.paperTexture], ["imageCard", theme.imageCard], ["caption", theme.caption], ["motion", theme.motion], ["transition", theme.transition]]) {
    for (const [key, item] of Object.entries(object)) {
      if (typeof item === "number") integer(item, `${field}.${key}`);
    }
  }
  themeRanges(theme);
  return theme;
};

export const computeLayout = (props, theme) => {
  const lineHeight = Math.ceil((theme.caption.fontSize * theme.caption.lineHeightMilli) / 1000);
  const captionHeight = lineHeight * 2 + theme.caption.paddingY * 2;
  const captionRightExtent = Math.max(PAPER_CAPTION_OUTLINE, PAPER_CAPTION_SHADOW_X);
  const captionBottomExtent = Math.max(PAPER_CAPTION_OUTLINE, PAPER_CAPTION_SHADOW_Y);
  const caption = {
    x: theme.canvas.safeMarginX + PAPER_CAPTION_OUTLINE,
    y: props.height - theme.canvas.safeMarginBottom - captionHeight - captionBottomExtent,
    width: props.width - theme.canvas.safeMarginX * 2 - PAPER_CAPTION_OUTLINE - captionRightExtent,
    height: captionHeight,
  };
  const captionEnvelope = {
    x: caption.x - PAPER_CAPTION_OUTLINE,
    y: caption.y - PAPER_CAPTION_OUTLINE,
    width: caption.width + PAPER_CAPTION_OUTLINE + captionRightExtent,
    height: caption.height + PAPER_CAPTION_OUTLINE + captionBottomExtent,
  };
  const safeWidth = props.width - theme.canvas.safeMarginX * 2;
  const imageRegionBottom = caption.y - IMAGE_CAPTION_GAP;
  const availableImageHeight = imageRegionBottom - theme.canvas.safeMarginTop;
  const desiredWidth = Math.min(theme.imageCard.maxWidth, safeWidth);
  const desiredHeight = Math.min(theme.imageCard.maxHeight, availableImageHeight);
  const envelopeFor = (card) => {
    const border = theme.imageCard.borderWidth;
    const centerX = card.x + card.width / 2;
    const centerY = card.y + card.height / 2;
    const localMinX = Math.min(-border, theme.imageCard.shadowOffsetX);
    const localMaxX = Math.max(card.width + border, card.width + theme.imageCard.shadowOffsetX);
    const localMinY = Math.min(-border, theme.imageCard.shadowOffsetY);
    const localMaxY = Math.max(card.height + border, card.height + theme.imageCard.shadowOffsetY);
    const localHalfWidth = Math.max(Math.abs(localMinX - card.width / 2), Math.abs(localMaxX - card.width / 2));
    const localHalfHeight = Math.max(Math.abs(localMinY - card.height / 2), Math.abs(localMaxY - card.height / 2));
    const scale = 1 + theme.motion.maxScaleDeltaMilli / 1000;
    const radians = ((Math.abs(theme.imageCard.rotationMillidegrees) + Math.abs(theme.motion.maxRotationMillidegrees) / 2) / 1000) * (Math.PI / 180);
    const halfWidth = Math.ceil(scale * (localHalfWidth * Math.cos(radians) + localHalfHeight * Math.sin(radians)) + Math.abs(theme.motion.maxTranslateX) + Math.abs(theme.transition.maxTranslatePx));
    const halfHeight = Math.ceil(scale * (localHalfWidth * Math.sin(radians) + localHalfHeight * Math.cos(radians)) + Math.abs(theme.motion.maxTranslateY));
    const main = {
      left: Math.floor(centerX - halfWidth),
      top: Math.floor(centerY - halfHeight),
      right: Math.ceil(centerX + halfWidth),
      bottom: Math.ceil(centerY + halfHeight),
    };
    const backingRadians = ((Math.abs(theme.imageCard.rotationMillidegrees) / 1000) * PAPER_BACKING_ROTATION_FACTOR * Math.PI) / 180;
    const backingHalfWidth = Math.ceil(card.width / 2 * Math.cos(backingRadians) + card.height / 2 * Math.sin(backingRadians));
    const backingHalfHeight = Math.ceil(card.width / 2 * Math.sin(backingRadians) + card.height / 2 * Math.cos(backingRadians));
    const backingCenterX = centerX + PAPER_BACKING_OFFSET_X;
    const backingCenterY = centerY + PAPER_BACKING_OFFSET_Y;
    const left = Math.min(main.left, Math.floor(backingCenterX - backingHalfWidth));
    const top = Math.min(main.top, Math.floor(backingCenterY - backingHalfHeight));
    const right = Math.max(main.right, Math.ceil(backingCenterX + backingHalfWidth));
    const bottom = Math.max(main.bottom, Math.ceil(backingCenterY + backingHalfHeight));
    return {x: left, y: top, width: right - left, height: bottom - top};
  };
  let image = null;
  let imageEnvelope = null;
  for (let permille = 1000; permille >= 1; permille -= 1) {
    const candidateWidth = Math.floor((desiredWidth * permille) / 1000);
    const candidateHeight = Math.floor((desiredHeight * permille) / 1000);
    if (candidateWidth < MIN_RENDERED_IMAGE_CARD || candidateHeight < MIN_RENDERED_IMAGE_CARD) break;
    const candidate = {
      x: Math.floor((props.width - candidateWidth) / 2),
      y: theme.canvas.safeMarginTop + Math.floor((availableImageHeight - candidateHeight) / 2),
      width: candidateWidth,
      height: candidateHeight,
    };
    const envelope = envelopeFor(candidate);
    if (envelope.x >= theme.canvas.safeMarginX && envelope.y >= theme.canvas.safeMarginTop && envelope.x + envelope.width <= props.width - theme.canvas.safeMarginX && envelope.y + envelope.height <= imageRegionBottom && candidate.y + candidate.height + 12 + SEGMENT_MARKER_HEIGHT <= caption.y) {
      image = candidate;
      imageEnvelope = envelope;
      break;
    }
  }
  const within = (box) => box.x >= theme.canvas.safeMarginX && box.y >= theme.canvas.safeMarginTop && box.x + box.width <= props.width - theme.canvas.safeMarginX && box.y + box.height <= props.height - theme.canvas.safeMarginBottom;
  if (image === null || imageEnvelope === null || caption.width <= 0 || caption.height <= 0 || !within(image) || !within(imageEnvelope) || !within(caption) || !within(captionEnvelope) || imageEnvelope.y + imageEnvelope.height > imageRegionBottom) {
    throw new Error("paper-collage layout escapes the contract safe area");
  }
  return {image, imageEnvelope, caption, captionEnvelope};
};

const textUnits = (text) => [...text].reduce((total, character) => total + (character.codePointAt(0) > 255 ? 1000 : 600), 0);

export const validatePaperCollageProps = (props) => {
  const extension = record(props.rendererExtension, "rendererExtension");
  exactKeys(extension, ["schemaVersion", "compositionId", "template", "theme", "motionPreset", "transitionPreset", "captionPreset", "requiredCapabilities", "opening"], "rendererExtension");
  if (extension.schemaVersion !== "1.0" || extension.compositionId !== "PaperCollageVisualV1") throw new Error("composition identity mismatch");
  const template = record(extension.template, "template");
  const themeRef = record(extension.theme, "theme");
  const opening = record(extension.opening, "opening");
  exactKeys(template, ["id", "version"], "template");
  exactKeys(themeRef, ["assetId", "src", "sha256", "tokens"], "theme");
  exactKeys(opening, ["startFrame", "endFrame", "title", "subtitle"], "opening");
  if (template.id !== "paper-collage-visual-v1" || template.version !== "0.1.0-experimental") throw new Error("unknown template identity");
  if (extension.motionPreset !== "subtle") throw new Error("unsupported motion preset");
  if (extension.transitionPreset !== "paper-cut") throw new Error("unsupported transition preset");
  if (extension.captionPreset !== "bottom-card") throw new Error("unsupported caption preset");
  if (!Array.isArray(extension.requiredCapabilities)) throw new Error("requiredCapabilities must be an array");
  for (const capability of ["layered_images", "camera_motion", "transitions"]) {
    if (!extension.requiredCapabilities.includes(capability)) throw new Error(`template capability ${capability} is missing`);
  }
  if (!SHA256.test(themeRef.sha256 ?? "")) throw new Error("theme hash is invalid");
  portable(themeRef.src, "theme.src");
  const theme = parsePaperCollageTheme(themeRef.tokens);
  const layout = computeLayout(props, theme);
  if (props.captionStyle?.maxLines !== 2) throw new Error("contract caption maxLines must remain two");
  if (theme.canvas.safeMarginX < Math.max(props.captionStyle.leftPx, props.captionStyle.rightPx) || theme.canvas.safeMarginBottom < props.captionStyle.bottomPx) throw new Error("theme cannot bypass contract caption safety");
  const capacity = Math.floor(((layout.caption.width - theme.caption.paddingX * 2) * 1000) / theme.caption.fontSize);
  for (const caption of props.captions) {
    const lines = string(caption.text, "caption.text").split("\n");
    if (lines.length > 2 || lines.some((line) => textUnits(line) > capacity) || textUnits(lines.join("")) > capacity * 2) {
      throw new Error("caption exceeds the approved two-line box");
    }
  }
  const openingFrames = integer(opening.endFrame, "opening.endFrame") - integer(opening.startFrame, "opening.startFrame");
  if (opening.startFrame !== 0 || opening.endFrame > props.durationInFrames || openingFrames < props.fps || openingFrames * 2 > props.fps * 3) throw new Error("opening must cover 1.0-1.5 seconds from frame zero");
  return props;
};
