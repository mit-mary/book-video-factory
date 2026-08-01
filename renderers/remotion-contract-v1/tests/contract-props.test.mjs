import assert from "node:assert/strict";
import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import test from "node:test";

import { parseContractPropsFile } from "../scripts/contract-props.mjs";

const minimal = () => ({
  schemaVersion: "1.0",
  requestId: "rrq_test",
  requestHash: "a".repeat(64),
  width: 720,
  height: 960,
  fps: 30,
  durationInFrames: 30,
  segments: [],
  captions: [],
  rendererExtension: { compositionId: "ContractConformanceV1" },
});

const writeProps = async (value) => {
  const root = await mkdtemp(join(tmpdir(), "remotion-contract-props-"));
  const path = join(root, "props.json");
  await writeFile(path, JSON.stringify(value), "utf8");
  return path;
};

test("accepts basic Request identity", async () => {
  const value = minimal();
  assert.deepEqual(await parseContractPropsFile(await writeProps(value)), value);
});

test("rejects a mismatched props Request hash shape", async () => {
  const value = minimal();
  value.requestHash = "not-a-hash";
  await assert.rejects(parseContractPropsFile(await writeProps(value)), /requestHash/);
});

test("rejects an unknown composition identity", async () => {
  const value = minimal();
  value.rendererExtension.compositionId = "MissingComposition";
  await assert.rejects(parseContractPropsFile(await writeProps(value)), /composition identity/);
});

test("render wrapper rejects a mismatched Request identity before Remotion", async () => {
  const value = minimal();
  value.renderMode = "preview";
  const props = await writeProps(value);
  const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
  const completed = spawnSync(
    process.execPath,
    [
      resolve(root, "scripts", "render-contract.mjs"),
      "--props",
      props,
      "--output",
      resolve(dirname(props), "out.mp4"),
      "--composition-id",
      "ContractConformanceV1",
      "--expected-request-id",
      "different-request",
      "--expected-request-hash",
      "b".repeat(64),
      "--render-mode",
      "preview",
    ],
    { cwd: root, encoding: "utf8", shell: false },
  );
  assert.notEqual(completed.status, 0);
  assert.match(completed.stderr, /Request identity mismatch/);
});
