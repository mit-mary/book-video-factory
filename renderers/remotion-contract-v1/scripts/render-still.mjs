import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

import { parseContractPropsFile } from "./contract-props.mjs";

const args = new Map();
for (let index = 2; index < process.argv.length; index += 2) {
  args.set(process.argv[index], process.argv[index + 1]);
}
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const propsPath = resolve(args.get("--props") ?? "");
const outputPath = resolve(args.get("--output") ?? "");
const compositionId = args.get("--composition-id");
const expectedRequestHash = args.get("--expected-request-hash");
const frame = Number(args.get("--frame"));

if (compositionId !== "PaperCollageVisualV1") throw new Error("unsupported still Composition");
if (!Number.isInteger(frame) || frame < 0) throw new Error("frame must be a non-negative integer");
if (existsSync(outputPath)) throw new Error("still output path already exists");
const props = await parseContractPropsFile(propsPath);
if (props.rendererExtension?.compositionId !== compositionId) {
  throw new Error("props Composition identity mismatch");
}
if (props.requestHash !== expectedRequestHash) throw new Error("props Request hash mismatch");
if (frame >= props.durationInFrames) throw new Error("frame is outside the Composition duration");

const cli = resolve(root, "node_modules", "@remotion", "cli", "remotion-cli.js");
const command = [
  cli,
  "still",
  resolve(root, "src", "index.ts"),
  compositionId,
  outputPath,
  `--props=${propsPath}`,
  `--frame=${frame}`,
  "--image-format=png",
];
const completed = spawnSync(process.execPath, command, {
  cwd: root,
  encoding: "utf8",
  shell: false,
});
process.stdout.write(completed.stdout ?? "");
process.stderr.write(completed.stderr ?? "");
process.exit(completed.status ?? 1);
