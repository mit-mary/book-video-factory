# Phase 4B.6 Known Issues

## Open gates

- User visual approval is not recorded. Current status is
  `PHASE_4B6_UNIFIED_PREVIEW_PENDING_USER_REVIEW`.
- Public release remains held because H2 external rights-clearance evidence is
  not recorded.
- This controlled fixture uses synthetic Chinese copy and one approved atlas;
  it does not demonstrate quality on real-book content or varied assets.

## Instruction conflict

The Phase 4B.6 instruction simultaneously requires no adjacent segments of the
same scene type and recommends `Full-Bleed Turning → Full-Bleed Ending`. Both
cannot be true for the specified five-segment sequence. The implementation
follows the more concrete preview structure. Turning and Ending therefore share
the Full-Bleed type but use different art, crop geometry, keyword placement and
a six-frame reveal. This exception is documented rather than reported as a
false pass.

## Test warning

The Python suite reports one pre-existing `PytestReturnNotNoneWarning` from
`tests/test_fonts.py::test_font_bytes`, which returns bytes instead of using an
assertion. It does not fail the suite and was not changed in this visual-only
phase.

## Deliberate non-goals

No word-level captioning, waveform, HUD, complex motion graphics, audio
finalizer, web UI, batch production, default-renderer switch or Phase 4C work
is included.
