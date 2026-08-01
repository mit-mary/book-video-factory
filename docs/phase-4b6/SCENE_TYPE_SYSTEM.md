# Scene Type System

## Three scene types

### Full-Bleed Metaphor

Used for Hook, Turning and Ending. The artwork occupies approximately 94% of
the canvas width and at least 92.5% of its height. A short keyword is placed in
an existing visual region; no side card or large color divider is added.

### Editorial Detail

Used for the toggle-switch close-up. The object card occupies the upper visual
field, retains negative space and is paired with the short keyword `小动作`.
There is no forced column split or blue rail.

### Sequential Build

Used for the three actions. Clock, hand and paper heart enter at frames 0, 46
and 92 of the five-second segment. Each enters over eight frames without
bounce. Earlier items remain visible at reduced opacity, so the final state is
a cumulative composition rather than three simultaneous opening cards.

## Bound sequence

| Time | Segment | Scene type |
| --- | --- | --- |
| 0–3 s | Hook | Full-Bleed Metaphor |
| 3–6 s | Detail | Editorial Detail |
| 6–11 s | Three actions | Sequential Build |
| 11–14 s | Turning | Full-Bleed Metaphor |
| 14–18 s | Ending | Full-Bleed Metaphor |

The exact sequence is fail-closed in both the Python adapter and Node props
parser. It deliberately follows the instruction's concrete preview structure.
This creates one documented exception to the more general rule that adjacent
segments should never share a scene type: Turning and Ending are both
Full-Bleed, but use different crops, composition, keyword placement and a new
Paper Reveal.
