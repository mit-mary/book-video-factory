# Phase 4A Closure

## Confirmed baseline

- Phase 4A branch result was committed and pushed before Phase 4B.
- Phase 4B baseline: `5f71439` (`docs: record phase 4a remotion experiment`).
- Fork `main` was fast-forwarded to that baseline.
- Phase 4B uses the independent branch `experiment/paper-collage-visual-v1`.
- Baseline renderer: `remotion-contract-conformance-v1@0.1.0-experimental`.
- Baseline composition: `ContractConformanceV1`.
- Baseline regression: Python 171, Node 4, TypeScript and ESLint passed.

## Preserved boundaries

- `ContractConformanceV1` semantics were not changed.
- Renderer Contract v1 schemas and core implementation were not changed.
- Legacy V1–V5 and `LegacyV4Renderer` were not changed.
- Final Mix remains the only audio source.
- The default renderer was not switched.
- H2 Rights Hold remains active.

Conclusion: Phase 4A was a valid clean baseline for the Phase 4B visual experiment.
