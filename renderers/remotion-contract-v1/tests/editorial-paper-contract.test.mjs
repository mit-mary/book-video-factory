import assert from "node:assert/strict";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { parseContractPropsFile } from "../scripts/contract-props.mjs";
import { EDITORIAL_SCENE_SEQUENCE } from "../scripts/editorial-paper-contract.mjs";

const hash = "a".repeat(64);

const validProps = () => ({
  schemaVersion: "1.0",
  requestId: "rrq_phase4b5_editorial",
  requestHash: hash,
  attemptId: "phase4b5-node-test",
  renderMode: "final",
  width: 720,
  height: 1280,
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
    compositionId: "EditorialPaperCollageV1",
    template: { id: "editorial-paper-collage-v1", version: "0.2.0-experimental" },
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
    motionPreset: "editorial-unified-v1",
    transitionPreset: "hard-cut-paper-reveal",
    captionPreset: "fixed-safe-zone-two-line",
    requiredCapabilities: ["layered_images", "camera_motion", "transitions"],
    sceneTypeSequence: [...EDITORIAL_SCENE_SEQUENCE],
    opening: { startFrame: 0, endFrame: 36, title: "TEST TITLE", subtitle: "CONTROLLED FIXTURE" },
  },
});

const parse = async (props) => {
  const directory = await mkdtemp(join(tmpdir(), "phase4b5-node-"));
  const path = join(directory, "props.json");
  await writeFile(path, JSON.stringify(props), "utf8");
  try {
    return await parseContractPropsFile(path);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
};

test("accepts the unified Direction A scene system", async () => {
  const parsed = await parse(validProps());
  assert.equal(parsed.rendererExtension.compositionId, "EditorialPaperCollageV1");
  assert.deepEqual(parsed.rendererExtension.sceneTypeSequence, EDITORIAL_SCENE_SEQUENCE);
  assert.equal(new Set(parsed.rendererExtension.sceneTypeSequence).size, 3);
});

test("rejects a reordered Direction A scene sequence", async () => {
  const reordered = validProps();
  [reordered.rendererExtension.sceneTypeSequence[0], reordered.rendererExtension.sceneTypeSequence[1]] = [reordered.rendererExtension.sceneTypeSequence[1], reordered.rendererExtension.sceneTypeSequence[0]];
  await assert.rejects(parse(reordered), /sceneTypeSequence/);
});

test("rejects caption and preset regressions", async () => {
  const caption = validProps();
  caption.captionStyle.maxLines = 3;
  await assert.rejects(parse(caption), /two-line contract/);
  const preset = validProps();
  preset.rendererExtension.captionPreset = "bottom-card";
  await assert.rejects(parse(preset), /caption preset/);
});

test("rejects a canvas below the validated editorial minimum", async () => {
  const props = validProps();
  props.width = 400;
  await assert.rejects(parse(props), /9:16/);
});

test("rejects the legacy 3:4 canvas", async () => {
  const props = validProps();
  props.height = 960;
  await assert.rejects(parse(props), /9:16/);
});

test("rejects the legacy five-layout extension", async () => {
  const props = validProps();
  props.rendererExtension.layoutSequence = [
    "split-column",
    "scale-contrast",
    "staggered-notes",
    "full-bleed-turn",
    "quiet-asymmetry",
  ];
  delete props.rendererExtension.sceneTypeSequence;
  await assert.rejects(parse(props), /missing or unknown fields/);
});
