# Phase 4B.5 Result

## Status

`DIRECTION_A_FROZEN_FIXTURE_VALIDATED`

## Selection and scope

- User selection: `A — Editorial Paper Collage`.
- Mix boundary: pure A; no B or C template system was added.
- Baseline: `19a3295` on `codex/phase-4b5-visual-directions`.
- Implementation branch: `codex/phase-4b5-direction-a-template`.
- Real books, Provider calls, stock downloads and commercial assets: none.

## Stage 3 implementation

An independent opt-in `EditorialPaperCollageV1` Composition was added. `ContractConformanceV1` remains the default contract Composition and `PaperCollageVisualV1` remains available as the Phase 4B rollback point.

The selected template binds five layouts in a strict output-affecting extension:

1. `split-column`
2. `scale-contrast`
3. `staggered-notes`
4. `full-bleed-turn`
5. `quiet-asymmetry`

The sequence is fail-closed, repeats cyclically across the 13 frozen segments and never assigns the same layout to adjacent segments. Caption presentation is integrated into each layout, sentence-level, two-line maximum and below the 22% height ceiling. Motion is layout-specific; only paper-cut and column-wipe entrance families are allowed.

## Stage 4 validation

- Python regression: 181/181 PASS.
- Node contract tests: 18/18 PASS.
- TypeScript and ESLint: PASS.
- Composition Discovery: PASS.
- Preview render: succeeded.
- Final experimental render: succeeded.
- Five-layout static-frame review: PASS.
- Prior `PaperCollageVisualV1` full Preview/Final regression: PASS; output SHA-256 values remained `a2717c3c...d64e8` and `d53c2f41...2dbf`, identical to the recorded Phase 4B baseline.
- FFprobe/media contract comparison: PASS.
- External technical QC: PASS.
- Local Experimental Master: PASS.
- Public release: HELD.

The authoritative run is `C:\Users\SSS\AppData\Local\Temp\book-video-factory-phase4b5-20260801-run3`.

## Boundary result

Renderer Contract v1, Request/Hash/Attempt/Result/Handoff, Final Mix-only audio, staged asset hashes, External QC, Rights Hold and Legacy rollback remain intact. The Remotion renderer performs no audio mixing.

The frozen fixture still uses program-generated geometric images. It validates layout and renderer behavior but is not evidence that real-book assets will have equivalent aesthetic quality. Phase 4C and real-book validation have not started.
