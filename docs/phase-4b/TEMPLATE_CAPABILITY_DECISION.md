# Template Capability Decision

## Enabled after implementation and tests

- `still_images`
- `layered_images`
- `captions`
- `camera_motion`
- `transitions`
- `audio_playback`
- `preview`
- `deterministic_render`

The newly enabled capabilities are restricted to `paper-collage-visual-v1`, the `subtle` motion preset and `paper-cut` with at most eight frames.

## Explicitly unsupported

- `video_clips`
- `audio_mixing`
- `word_highlight`
- `waveform`
- `vector_overlays`
- advanced transitions

Capability negotiation is fail-closed: the template is blocked if `layered_images`, `camera_motion` or `transitions` is absent from the Request.
