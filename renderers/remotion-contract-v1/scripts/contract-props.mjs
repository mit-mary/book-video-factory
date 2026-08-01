import { readFile } from "node:fs/promises";

import { validatePaperCollageProps } from "./paper-collage-contract.mjs";
import { validateEditorialPaperProps } from "./editorial-paper-contract.mjs";

const SHA256 = /^[0-9a-f]{64}$/;

export const parseContractPropsFile = async (path) => {
  const value = JSON.parse(await readFile(path, "utf8"));
  if (value?.schemaVersion !== "1.0") throw new Error("unsupported props schemaVersion");
  if (typeof value.requestId !== "string" || value.requestId.length === 0) {
    throw new Error("requestId is required");
  }
  if (!SHA256.test(value.requestHash ?? "")) throw new Error("requestHash is invalid");
  if (!Number.isInteger(value.width) || !Number.isInteger(value.height)) {
    throw new Error("width and height must be integers");
  }
  if (!Number.isInteger(value.fps) || !Number.isInteger(value.durationInFrames)) {
    throw new Error("fps and durationInFrames must be integers");
  }
  if (!Array.isArray(value.segments) || !Array.isArray(value.captions)) {
    throw new Error("segments and captions must be arrays");
  }
  const compositionId = value.rendererExtension?.compositionId;
  if (compositionId !== "ContractConformanceV1" && compositionId !== "PaperCollageVisualV1" && compositionId !== "EditorialPaperCollageV1") {
    throw new Error("composition identity mismatch");
  }
  if (compositionId === "PaperCollageVisualV1") validatePaperCollageProps(value);
  if (compositionId === "EditorialPaperCollageV1") validateEditorialPaperProps(value);
  return value;
};
