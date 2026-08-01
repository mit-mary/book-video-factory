# Frame-Driven Motion

## Implementation

- Motion is driven only by `useCurrentFrame()` and `interpolate()`.
- No CSS animation, CSS transition or animation library is used.
- Segment IDs map deterministically to push-in, pull-out, pan-left, pan-right or static.
- Scale delta is at most 0.04; translation is at most 20 px; rotation animation is at most 0.5 degrees.
- `paper-cut` is a six-frame visible-card displacement entrance; it does not change segment boundaries or audio.

## Safety envelope

The layout validator includes maximum scale, base and animated rotation, motion translation, transition translation, outline, shadow and the offset backing sheet. The final 720×960 run produced:

- Base image card: `(134, 131, 452, 490)`.
- Full motion envelope: `(72, 81, 576, 590)`.
- Allowed image region bottom: caption top minus 24 px.

The envelope stayed inside the theme safe area for the entire approved motion range.

## Boundary review

run2 exposed a one-frame invisible card at scene cuts. The opacity entrance was removed, the opening layer now fades as a whole, and run3 boundary frames 0, 35/36 and 120/121/126 were reviewed. No blank flash or abrupt empty frame remained.
