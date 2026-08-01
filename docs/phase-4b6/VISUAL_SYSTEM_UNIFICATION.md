# Visual System Unification

## Result

The five-layout system was replaced by one 9:16 editorial paper-collage system
with three reusable scene types. Direction A remains the selected visual
direction (`DIRECTION_A_APPROVED`); the unified video itself remains pending
user review.

## Shared language

- Warm off-white paper ground, charcoal, deep blue, rust red and warm gold.
- Torn-paper edges, realistic objects/body details, restrained shadows and
  deliberate negative space.
- A single Direction A art atlas supplies the controlled fixture imagery.
- Keywords relate to composition, while narration uses one fixed safe zone.
- Hero scenes are near-full-bleed instead of being split by side cards.

## Removed from the active composition

- `EDITORIAL / HOOK`, `EDITORIAL / 01`, `THREE CUTS / 03`, `AFTER / 05`.
- Blue vertical rail, orange turning block and content-free numbering.
- Independent white narration cards and large PPT-like title rectangles.
- The old five-layout extension and the standalone `EditorialOpening` layer.

## Engineering shape

`EditorialPaperScene` now dispatches only to `FullBleedMetaphor`,
`EditorialDetail` or `SequentialBuild`. Shared atlas cropping, caption and
paper-reveal components keep the scene implementations small and explicit.
The template-private extension is versioned as `0.2.0-experimental` and rejects
the prior extension rather than silently interpreting it.
