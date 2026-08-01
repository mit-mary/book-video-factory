# Dependency Audit Status

Audit date: 2026-08-01.

## Confirmed results

- `npm audit --omit=dev`: 0 vulnerabilities, exit 0.
- Full `npm audit`: 9 low-severity vulnerabilities, exit 1.
- Reported chain is limited to the ESLint development toolchain and begins with `@eslint/plugin-kit` advisory `GHSA-xffm-g5w8-qvg7`.
- npm reports no fix available for the top-level advisory in the current dependency graph.

Phase 4A recorded two low findings. That number is stale under the current advisory database; Phase 4B records the current result of nine.

No `npm audit fix` or `npm audit fix --force` was run. Production dependencies report zero findings, so the current evidence does not show an affected render-runtime dependency path. The development-tooling finding remains a productionization gate for separate review.
