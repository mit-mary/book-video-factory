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
const expectedRequestId = args.get("--expected-request-id");
const expectedRequestHash = args.get("--expected-request-hash");
const renderMode = args.get("--render-mode");

if (compositionId !== "ContractConformanceV1") throw new Error("unsupported composition ID");
if (existsSync(outputPath)) throw new Error("output path already exists");
const props = await parseContractPropsFile(propsPath);
if (props.requestId !== expectedRequestId || props.requestHash !== expectedRequestHash) {
  throw new Error("props Request identity mismatch");
}
if (props.renderMode !== renderMode) throw new Error("props renderMode mismatch");

const cli = resolve(root, "node_modules", "@remotion", "cli", "remotion-cli.js");
const command = [
  cli,
  "render",
  resolve(root, "src", "index.ts"),
  compositionId,
  outputPath,
  `--props=${propsPath}`,
  "--codec=h264",
  "--audio-codec=aac",
  "--pixel-format=yuv420p",
  "--concurrency=2",
  renderMode === "preview" ? "--crf=28" : "--crf=18",
];
const completed = spawnSync(process.execPath, command, {
  cwd: root,
  encoding: "utf8",
  shell: false,
});
process.stdout.write(completed.stdout ?? "");
process.stderr.write(completed.stderr ?? "");
process.exit(completed.status ?? 1);
