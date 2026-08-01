import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const propsArg = process.argv[2];
if (!propsArg) throw new Error("props path argument is required");
const cli = resolve(root, "node_modules", "@remotion", "cli", "remotion-cli.js");
const completed = spawnSync(
  process.execPath,
  [cli, "compositions", resolve(root, "src", "index.ts"), `--props=${resolve(propsArg)}`],
  { cwd: root, encoding: "utf8", shell: false },
);
process.stdout.write(completed.stdout ?? "");
process.stderr.write(completed.stderr ?? "");
process.exit(completed.status ?? 1);
