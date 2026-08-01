# Caption System

## Narration layer

The narration preset is `fixed-safe-zone-two-line`.

- One global `UnifiedCaption` component renders above all scene layouts.
- The box remains at left/right 7% and bottom 5.5% for every cue.
- Copy is limited to two explicit lines.
- The rendered container is capped at 17% of canvas height; the contract-side
  calculation must remain at or below 20%.
- A translucent charcoal backing and white type provide contrast without a
  large opaque white card.
- The three actions are separate timed cues so narration and sequential build
  share the same reading order.

## Keyword layer

Keywords (`改变生活`, `小动作`, `转向`, `小选择`) may move with composition.
They are short visual anchors and do not replace or duplicate the complete
narration cue.

## Fail-closed checks

The private template contract rejects a caption preset other than
`fixed-safe-zone-two-line`, a track whose `max_lines` is not two, a theme that
bypasses safe margins, or a calculated caption height above 20%.
