# Motion and Transition

## Motion preset

`editorial-unified-v1` assigns motion by scene purpose:

- Full-Bleed: scale 1.00 → 1.02, with no horizontal drift. This is below the
  Phase 4B.6 limit of 0.025.
- Editorial Detail: horizontal translation −8 px → +8 px, exactly 16 px total
  travel and no scale animation.
- Sequential Build: no whole-scene push-in; individual elements enter over
  eight frames from ±14 px with eased opacity and no bounce.
- Ending: the Full-Bleed push-in clamps for the final 45 frames (1.5 s).

## Transition vocabulary

Only two transition families are used:

- Hard Cut at normal segment boundaries.
- Paper Reveal on Full-Bleed entry, implemented as a six-frame torn edge.

Paper Reveal does not change the timeline or audio, and its six-frame duration
is within the required 4–8 frame range. CSS keyframe animation, random motion,
rotation and PPT-like block wipes are not used.
