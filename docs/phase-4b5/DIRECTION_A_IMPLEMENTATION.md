# Direction A Implementation

## Identity

- Composition: `EditorialPaperCollageV1`
- Template: `editorial-paper-collage-v1`
- Version: `0.1.0-experimental`
- Selection: pure Direction A
- Default renderer changed: no
- Prior `PaperCollageVisualV1` removed or overwritten: no

## Layout system

The five approved layouts are bound in the hashed Remotion extension. Reordering, repeating, omitting or adding a layout fails before the renderer process starts.

| Layout | Main visual position | Information relationship |
|---|---|---|
| `split-column` | left | dark editorial copy column on right |
| `scale-contrast` | right / center | small cobalt type block overlaps a large image |
| `staggered-notes` | distributed | three cropped image fragments create a local close-up and hierarchy |
| `full-bleed-turn` | full | top copy band and rust directional wedge alter the spatial composition |
| `quiet-asymmetry` | left | right-side negative space carries the closing copy |

The 13 frozen segments cycle through these layouts; adjacent segments cannot share a layout.

## Caption and motion contract

- sentence captions only;
- maximum two lines;
- calculated caption height no greater than 22% of the output height;
- no global bottom white caption card;
- no word highlight, waveform or HUD;
- purposeful motion varies by layout rather than applying a uniform push-in;
- at most two transition families: paper cut and column wipe.

## Contract boundary

The Composition consumes only staged, hash-bound visual refs, the licensed staged font, theme/texture bindings and the single upstream Final Mix. Request identity, Attempt isolation, Result/Handoff and Rights Hold behavior remain owned by the existing Python Renderer Contract facade.
