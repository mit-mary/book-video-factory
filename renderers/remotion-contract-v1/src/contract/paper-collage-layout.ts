import type {
  MotionMode,
  PaperCollageLayout,
  PaperCollageProps,
  PaperCollageTheme,
} from "./paper-collage-types";

const HEX = /^#[0-9A-F]{6}$/;

export const PAPER_BACKING_OFFSET_X = 9;
export const PAPER_BACKING_OFFSET_Y = 11;
export const PAPER_BACKING_ROTATION_FACTOR = 0.55;
export const PAPER_CAPTION_OUTLINE = 2;
export const PAPER_CAPTION_SHADOW_X = 7;
export const PAPER_CAPTION_SHADOW_Y = 9;
const MIN_RENDERED_IMAGE_CARD = 240;
const IMAGE_CAPTION_GAP = 24;
const SEGMENT_MARKER_HEIGHT = 30;

export const exactKeys = (
  value: Record<string, unknown>,
  expected: readonly string[],
  field: string,
): void => {
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (actual.length !== wanted.length || actual.some((key, index) => key !== wanted[index])) {
    throw new Error(`${field} contains missing or unknown fields`);
  }
};

export const validateThemeRanges = (theme: PaperCollageTheme): void => {
  for (const [field, color] of [
    ["canvas.background", theme.canvas.background],
    ["canvas.ink", theme.canvas.ink],
    ["canvas.accent", theme.canvas.accent],
    ["caption.background", theme.caption.background],
    ["caption.text", theme.caption.text],
  ] as const) {
    if (!HEX.test(color)) throw new Error(`${field} must be an uppercase hex color`);
  }
  if (
    theme.canvas.safeMarginX < 48 ||
    theme.canvas.safeMarginX > 160 ||
    theme.canvas.safeMarginTop < 48 ||
    theme.canvas.safeMarginTop > 180 ||
    theme.canvas.safeMarginBottom < 64 ||
    theme.canvas.safeMarginBottom > 200
  ) {
    throw new Error("canvas safety token is outside the approved range");
  }
  if (
    theme.imageCard.maxWidth < 240 ||
    theme.imageCard.maxWidth > 1200 ||
    theme.imageCard.maxHeight < 240 ||
    theme.imageCard.maxHeight > 1600 ||
    theme.imageCard.padding < 8 ||
    theme.imageCard.padding > 40 ||
    theme.imageCard.borderWidth < 1 ||
    theme.imageCard.borderWidth > 6 ||
    Math.abs(theme.imageCard.shadowOffsetX) > 24 ||
    Math.abs(theme.imageCard.shadowOffsetY) > 24 ||
    Math.abs(theme.imageCard.rotationMillidegrees) > 3000
  ) {
    throw new Error("image-card token is outside the approved range");
  }
  if (
    theme.caption.maxLines !== 2 ||
    theme.caption.fontSize < 28 ||
    theme.caption.fontSize > 64 ||
    theme.caption.lineHeightMilli < 1000 ||
    theme.caption.lineHeightMilli > 1500 ||
    theme.caption.paddingX < 16 ||
    theme.caption.paddingX > 56 ||
    theme.caption.paddingY < 12 ||
    theme.caption.paddingY > 36
  ) {
    throw new Error("caption token is outside the approved range");
  }
  if (
    theme.motion.maxScaleDeltaMilli < 0 ||
    theme.motion.maxScaleDeltaMilli > 40 ||
    Math.abs(theme.motion.maxTranslateX) > 20 ||
    Math.abs(theme.motion.maxTranslateY) > 16 ||
    Math.abs(theme.motion.maxRotationMillidegrees) > 500
  ) {
    throw new Error("motion token is outside the approved range");
  }
  if (
    theme.transition.durationFrames < 1 ||
    theme.transition.durationFrames > 8 ||
    Math.abs(theme.transition.maxTranslatePx) > 20 ||
    theme.paperTexture.opacityMilli < 0 ||
    theme.paperTexture.opacityMilli > 250
  ) {
    throw new Error("transition or texture token is outside the approved range");
  }
};

export const computePaperCollageLayout = (
  width: number,
  height: number,
  theme: PaperCollageTheme,
): PaperCollageLayout => {
  validateThemeRanges(theme);
  const lineHeight = Math.ceil(
    (theme.caption.fontSize * theme.caption.lineHeightMilli) / 1000,
  );
  const captionHeight =
    lineHeight * theme.caption.maxLines + theme.caption.paddingY * 2;
  const captionRightExtent = Math.max(
    PAPER_CAPTION_OUTLINE,
    PAPER_CAPTION_SHADOW_X,
  );
  const captionBottomExtent = Math.max(
    PAPER_CAPTION_OUTLINE,
    PAPER_CAPTION_SHADOW_Y,
  );
  const captionCard = {
    x: theme.canvas.safeMarginX + PAPER_CAPTION_OUTLINE,
    y:
      height -
      theme.canvas.safeMarginBottom -
      captionHeight -
      captionBottomExtent,
    width:
      width -
      theme.canvas.safeMarginX * 2 -
      PAPER_CAPTION_OUTLINE -
      captionRightExtent,
    height: captionHeight,
  };
  const captionCardVisualEnvelope = {
    x: captionCard.x - PAPER_CAPTION_OUTLINE,
    y: captionCard.y - PAPER_CAPTION_OUTLINE,
    width:
      captionCard.width + PAPER_CAPTION_OUTLINE + captionRightExtent,
    height:
      captionCard.height + PAPER_CAPTION_OUTLINE + captionBottomExtent,
  };
  const safeWidth = width - theme.canvas.safeMarginX * 2;
  const imageRegionBottom = captionCard.y - IMAGE_CAPTION_GAP;
  const availableImageHeight = imageRegionBottom - theme.canvas.safeMarginTop;
  const desiredWidth = Math.min(theme.imageCard.maxWidth, safeWidth);
  const desiredHeight = Math.min(theme.imageCard.maxHeight, availableImageHeight);

  const envelopeFor = (card: {x: number; y: number; width: number; height: number}) => {
    const border = theme.imageCard.borderWidth;
    const centerX = card.x + card.width / 2;
    const centerY = card.y + card.height / 2;
    const localMinX = Math.min(-border, theme.imageCard.shadowOffsetX);
    const localMaxX = Math.max(
      card.width + border,
      card.width + theme.imageCard.shadowOffsetX,
    );
    const localMinY = Math.min(-border, theme.imageCard.shadowOffsetY);
    const localMaxY = Math.max(
      card.height + border,
      card.height + theme.imageCard.shadowOffsetY,
    );
    const localHalfWidth = Math.max(
      Math.abs(localMinX - card.width / 2),
      Math.abs(localMaxX - card.width / 2),
    );
    const localHalfHeight = Math.max(
      Math.abs(localMinY - card.height / 2),
      Math.abs(localMaxY - card.height / 2),
    );
    const scale = 1 + theme.motion.maxScaleDeltaMilli / 1000;
    const radians =
      ((Math.abs(theme.imageCard.rotationMillidegrees) +
        Math.abs(theme.motion.maxRotationMillidegrees) / 2) /
        1000) *
      (Math.PI / 180);
    const cosine = Math.cos(radians);
    const sine = Math.sin(radians);
    const halfWidth = Math.ceil(
      scale * (localHalfWidth * cosine + localHalfHeight * sine) +
        Math.abs(theme.motion.maxTranslateX) +
        Math.abs(theme.transition.maxTranslatePx),
    );
    const halfHeight = Math.ceil(
      scale * (localHalfWidth * sine + localHalfHeight * cosine) +
        Math.abs(theme.motion.maxTranslateY),
    );
    const main = {
      left: Math.floor(centerX - halfWidth),
      top: Math.floor(centerY - halfHeight),
      right: Math.ceil(centerX + halfWidth),
      bottom: Math.ceil(centerY + halfHeight),
    };
    const backingRadians =
      ((Math.abs(theme.imageCard.rotationMillidegrees) / 1000) *
        PAPER_BACKING_ROTATION_FACTOR *
        Math.PI) /
      180;
    const backingHalfWidth = Math.ceil(
      (card.width / 2) * Math.cos(backingRadians) +
        (card.height / 2) * Math.sin(backingRadians),
    );
    const backingHalfHeight = Math.ceil(
      (card.width / 2) * Math.sin(backingRadians) +
        (card.height / 2) * Math.cos(backingRadians),
    );
    const backingCenterX = centerX + PAPER_BACKING_OFFSET_X;
    const backingCenterY = centerY + PAPER_BACKING_OFFSET_Y;
    const left = Math.min(main.left, Math.floor(backingCenterX - backingHalfWidth));
    const top = Math.min(main.top, Math.floor(backingCenterY - backingHalfHeight));
    const right = Math.max(main.right, Math.ceil(backingCenterX + backingHalfWidth));
    const bottom = Math.max(main.bottom, Math.ceil(backingCenterY + backingHalfHeight));
    return {x: left, y: top, width: right - left, height: bottom - top};
  };

  let imageCard: {x: number; y: number; width: number; height: number} | null = null;
  let imageCardMotionEnvelope: ReturnType<typeof envelopeFor> | null = null;
  for (let permille = 1000; permille >= 1; permille -= 1) {
    const candidateWidth = Math.floor((desiredWidth * permille) / 1000);
    const candidateHeight = Math.floor((desiredHeight * permille) / 1000);
    if (
      candidateWidth < MIN_RENDERED_IMAGE_CARD ||
      candidateHeight < MIN_RENDERED_IMAGE_CARD
    ) {
      break;
    }
    const candidate = {
      x: Math.floor((width - candidateWidth) / 2),
      y:
        theme.canvas.safeMarginTop +
        Math.floor((availableImageHeight - candidateHeight) / 2),
      width: candidateWidth,
      height: candidateHeight,
    };
    const envelope = envelopeFor(candidate);
    if (
      envelope.x >= theme.canvas.safeMarginX &&
      envelope.y >= theme.canvas.safeMarginTop &&
      envelope.x + envelope.width <= width - theme.canvas.safeMarginX &&
      envelope.y + envelope.height <= imageRegionBottom &&
      candidate.y + candidate.height + 12 + SEGMENT_MARKER_HEIGHT <= captionCard.y
    ) {
      imageCard = candidate;
      imageCardMotionEnvelope = envelope;
      break;
    }
  }
  const within = (box: {x: number; y: number; width: number; height: number}) =>
    box.x >= theme.canvas.safeMarginX &&
    box.y >= theme.canvas.safeMarginTop &&
    box.x + box.width <= width - theme.canvas.safeMarginX &&
    box.y + box.height <= height - theme.canvas.safeMarginBottom;
  if (
    imageCard === null ||
    imageCardMotionEnvelope === null ||
    captionCard.width <= 0 ||
    captionCard.height <= 0 ||
    !within(imageCard) ||
    !within(imageCardMotionEnvelope) ||
    !within(captionCard) ||
    !within(captionCardVisualEnvelope) ||
    imageCardMotionEnvelope.y + imageCardMotionEnvelope.height > imageRegionBottom
  ) {
    throw new Error("paper-collage layout escapes the contract safe area");
  }
  return {
    imageCard,
    imageCardMotionEnvelope,
    captionCard,
    captionCardVisualEnvelope,
  };
};

const textUnits = (text: string): number =>
  [...text].reduce((total, character) => total + (character.codePointAt(0)! > 255 ? 1000 : 600), 0);

export const captionFits = (
  text: string,
  theme: PaperCollageTheme,
  layout: PaperCollageLayout,
): boolean => {
  const lines = text.split("\n");
  if (lines.length > theme.caption.maxLines) return false;
  const innerWidth = layout.captionCard.width - theme.caption.paddingX * 2;
  const unitsPerLine = Math.floor((innerWidth * 1000) / theme.caption.fontSize);
  if (unitsPerLine <= 0 || lines.some((line) => textUnits(line) > unitsPerLine)) {
    return false;
  }
  return textUnits(text.split("\n").join("")) <= unitsPerLine * theme.caption.maxLines;
};

export const motionModeForSegment = (segmentId: string): MotionMode => {
  let hash = 2166136261;
  for (const character of segmentId) {
    hash ^= character.codePointAt(0) ?? 0;
    hash = Math.imul(hash, 16777619) >>> 0;
  }
  const modes: MotionMode[] = [
    "slow-push-in",
    "slow-pull-out",
    "gentle-pan-left",
    "gentle-pan-right",
    "static",
  ];
  return modes[hash % modes.length];
};

export const validatePaperCollageLayout = (props: PaperCollageProps): PaperCollageLayout => {
  const layout = computePaperCollageLayout(
    props.width,
    props.height,
    props.rendererExtension.theme.tokens,
  );
  if (props.captionStyle.maxLines !== 2) {
    throw new Error("contract caption maxLines must remain two");
  }
  if (
    props.rendererExtension.theme.tokens.canvas.safeMarginX <
      Math.max(props.captionStyle.leftPx, props.captionStyle.rightPx) ||
    props.rendererExtension.theme.tokens.canvas.safeMarginBottom <
      props.captionStyle.bottomPx
  ) {
    throw new Error("theme cannot bypass the contract caption safe area");
  }
  for (const caption of props.captions) {
    if (!captionFits(caption.text, props.rendererExtension.theme.tokens, layout)) {
      throw new Error(`caption ${caption.cueId} exceeds the approved two-line box`);
    }
  }
  return layout;
};
