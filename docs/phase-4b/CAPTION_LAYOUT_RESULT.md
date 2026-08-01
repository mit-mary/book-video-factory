# Caption Layout Result

## Contract

- Sentence-level captions only.
- Maximum two lines; no rewriting, re-segmentation or word animation.
- Hash-bound staged local font; unavailable fonts fail closed.
- Bottom paper card with stable padding and high-contrast text.

## Final layout

- Caption card: `(74, 705, 567, 142)`.
- Visual envelope including outline and shadow: `(72, 703, 576, 153)`.
- Canvas safe boundary bottom: 856 px.
- Caption visual envelope bottom: 856 px.

Both Python and Node check line count, estimated width, total two-line capacity, contract safe area and visual envelope. The run3 index records `caption_visual_envelope_inside_safe_area: true`.

Visual review found no clipping, overflow or overlap with the segment marker in the frozen fixture.
