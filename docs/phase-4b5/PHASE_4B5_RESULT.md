# Phase 4B.5 Result

## Status

`DIRECTION_A_APPROVED`

`REMOTION_TEMPLATE_VISUAL_VALIDATION_PENDING_USER_REVIEW`

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

The sequence is fail-closed and the five-layout visual-validation timeline never
assigns the same layout to adjacent segments. Caption presentation is integrated
into each layout, sentence-level, two-line maximum and below the 22% height
ceiling. Motion is layout-specific; only paper-cut and column-wipe entrance
families are allowed.

## Stage 4 validation

- Python regression: 182/182 PASS (one pre-existing Pytest return-value warning
  in `tests/test_fonts.py`).
- Node contract tests: 18/18 PASS.
- TypeScript and ESLint: PASS.
- Composition Discovery: PASS.
- Preview render: succeeded.
- Final experimental render: succeeded.
- Five-layout machine checks: PASS.
- Five-layout visual candidate review: READY FOR USER REVIEW; not recorded as
  template approval.
- Prior `PaperCollageVisualV1` full Preview/Final regression: PASS; output SHA-256 values remained `a2717c3c...d64e8` and `d53c2f41...2dbf`, identical to the recorded Phase 4B baseline.
- FFprobe/media contract comparison: PASS.
- External technical QC: PASS.
- Local Experimental Master: PASS.
- Public release: HELD.

The original geometric run remains historical evidence only. The current
visual-validation candidate is
`C:\Users\SSS\AppData\Local\Temp\book-video-factory-phase4b5-visual-validation-20260801-run5`.

- Preview SHA-256: `0f42ff31fdf374ef41a4d5ebae000915689878482fe433ead29211d8437a1cf6`.
- Final SHA-256: `5b9977262f6bf31f9cace5306981f0e836918f3a2fc6f575ea52a6364db88458`.
- Preview duration: 18 seconds.
- Visual assets used by the timeline: Direction A text-free art atlas only.

## Boundary result

Renderer Contract v1, Request/Hash/Attempt/Result/Handoff, Final Mix-only audio, staged asset hashes, External QC, Rights Hold and Legacy rollback remain intact. The Remotion renderer performs no audio mixing.

The candidate uses the approved Direction A collage artwork rather than the old
geometric scene fixture. It validates the Remotion/artwork integration with
synthetic Chinese copy, but it is not evidence that real-book content will have
equivalent editorial quality. User template approval is still pending. Phase 4C
and real-book validation have not started.
