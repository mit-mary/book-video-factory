import assert from "node:assert/strict";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { parseContractPropsFile } from "../scripts/contract-props.mjs";
import { computeLayout } from "../scripts/paper-collage-contract.mjs";

const hash = "a".repeat(64);

const validProps = () => ({
  schemaVersion: "1.0",
  requestId: "rrq_phase4b_test",
  requestHash: hash,
  attemptId: "phase4b-node-test",
  renderMode: "final",
  width: 720,
  height: 960,
  fps: 30,
  durationInFrames: 360,
  segments: [
    { segmentId: "OPEN", startFrame: 0, endFrame: 180, visualRefs: ["attempts/a/assets/one.png"], captionRefs: ["c1"] },
    { segmentId: "BODY", startFrame: 180, endFrame: 360, visualRefs: ["attempts/a/assets/two.png"], captionRefs: [] },
  ],
  audio: { assetId: "final-mix", src: "attempts/a/assets/final.wav", sha256: hash },
  captions: [
    { cueId: "c1", segmentId: "OPEN", trackId: "en", text: "CONTROLLED FIXTURE", startMs: 0, endMs: 1200, timestampMs: null, confidence: null },
  ],
  font: { assetId: "font", family: "ContractCaption", src: "attempts/a/assets/font.ttf", sha256: hash },
  captionStyle: { leftPx: 48, rightPx: 48, bottomPx: 96, maxLines: 2 },
  assetBase: "attempts/a/assets",
  rendererExtension: {
    schemaVersion: "1.0",
    compositionId: "PaperCollageVisualV1",
    template: { id: "paper-collage-visual-v1", version: "0.1.0-experimental" },
    theme: {
      assetId: "paper-collage-theme-v1",
      src: "attempts/a/assets/theme.json",
      sha256: hash,
      tokens: {
        schemaVersion: "paper-collage-theme-v1",
        canvas: { background: "#F3EBDD", ink: "#2A2520", accent: "#B65B46", safeMarginX: 72, safeMarginTop: 72, safeMarginBottom: 104 },
        paperTexture: { assetId: "paper-texture-v1", src: "attempts/a/assets/texture.svg", sha256: hash, opacityMilli: 120 },
        imageCard: { maxWidth: 480, maxHeight: 520, padding: 18, borderWidth: 3, shadowOffsetX: 12, shadowOffsetY: 16, rotationMillidegrees: 1500 },
        caption: { maxLines: 2, fontSize: 42, lineHeightMilli: 1250, paddingX: 32, paddingY: 18, background: "#FFFDF7", text: "#2A2520" },
        motion: { maxScaleDeltaMilli: 40, maxTranslateX: 20, maxTranslateY: 16, maxRotationMillidegrees: 500 },
        transition: { durationFrames: 6, maxTranslatePx: 12 },
      },
    },
    motionPreset: "subtle",
    transitionPreset: "paper-cut",
    captionPreset: "bottom-card",
    requiredCapabilities: ["still_images", "captions", "audio_playback", "deterministic_render", "layered_images", "camera_motion", "transitions"],
    opening: { startFrame: 0, endFrame: 36, title: "TEST TITLE", subtitle: "CONTROLLED FIXTURE" },
  },
});

const parse = async (props) => {
  const directory = await mkdtemp(join(tmpdir(), "phase4b-node-"));
  const path = join(directory, "props.json");
  await writeFile(path, JSON.stringify(props), "utf8");
  try {
    return await parseContractPropsFile(path);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
};

test("accepts strict paper-collage props", async () => {
  const props = validProps();
  const parsed = await parse(props);
  assert.equal(parsed.rendererExtension.template.id, "paper-collage-visual-v1");
  const layout = computeLayout(parsed, parsed.rendererExtension.theme.tokens);
  assert.ok(layout.imageEnvelope.x >= 72);
  assert.ok(layout.imageEnvelope.y >= 72);
  assert.ok(layout.imageEnvelope.x + layout.imageEnvelope.width <= 720 - 72);
  assert.ok(layout.imageEnvelope.y + layout.imageEnvelope.height <= layout.caption.y - 24);
  assert.ok(layout.captionEnvelope.x >= 72);
  assert.ok(layout.captionEnvelope.y + layout.captionEnvelope.height <= 960 - 104);
});

test("rejects unknown template identity", async () => {
  const props = validProps();
  props.rendererExtension.template.id = "unknown";
  await assert.rejects(parse(props), /unknown template identity/);
});

test("rejects unknown output-affecting extension fields", async () => {
  const props = validProps();
  props.rendererExtension.randomDecoration = true;
  await assert.rejects(parse(props), /missing or unknown fields/);
});

test("rejects theme tokens outside approved ranges", async () => {
  const props = validProps();
  props.rendererExtension.theme.tokens.motion.maxScaleDeltaMilli = 41;
  await assert.rejects(parse(props), /motion token/);
});

test("rejects captions over two explicit lines", async () => {
  const props = validProps();
  props.captions[0].text = "one\ntwo\nthree";
  await assert.rejects(parse(props), /caption exceeds/);
});

test("rejects caption safety bypass", async () => {
  const props = validProps();
  props.rendererExtension.theme.tokens.canvas.safeMarginBottom = 64;
  await assert.rejects(parse(props), /cannot bypass/);
});

test("rejects image-card layout on an unsafe canvas", async () => {
  const props = validProps();
  props.width = 400;
  await assert.rejects(parse(props), /layout escapes/);
});

test("rejects unsupported motion and transition presets", async () => {
  const motion = validProps();
  motion.rendererExtension.motionPreset = "fast";
  await assert.rejects(parse(motion), /unsupported motion/);
  const transition = validProps();
  transition.rendererExtension.transitionPreset = "wipe";
  await assert.rejects(parse(transition), /unsupported transition/);
});

test("rejects missing template capabilities", async () => {
  const props = validProps();
  props.rendererExtension.requiredCapabilities = props.rendererExtension.requiredCapabilities.filter((item) => item !== "camera_motion");
  await assert.rejects(parse(props), /camera_motion is missing/);
});

test("rejects non-portable staged texture refs", async () => {
  const props = validProps();
  props.rendererExtension.theme.tokens.paperTexture.src = "C:\\texture.svg";
  await assert.rejects(parse(props), /portable public-relative path/);
});
