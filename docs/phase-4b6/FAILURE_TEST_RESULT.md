# Failure Test Result

## Node contract tests

`npm test`: 20/20 PASS.

Phase 4B.6 negative coverage confirms fail-closed behavior for:

- reordered three-scene sequence;
- legacy 3:4 canvas;
- legacy five-layout extension;
- old/unsupported caption, motion and transition presets;
- canvas below the validated 9:16 minimum;
- caption safety bypass and captions over two lines;
- unknown output-affecting fields, unsafe theme values and non-portable refs.

## Python renderer tests

The full Python suite passed 183/183. New renderer tests bind the three scene
types and reject both reordered scene sequences and the legacy layout sequence
before the runner is called.

## Static/media failure boundary

The smoke fixture also checks exact 9:16 dimensions, exact sequence, all three
scene types, seven expected validation states, three sequential-build states,
fixed two-line caption policy, at most two transition types, absence of legacy
labels, synthetic fixture copy, and a 15–20 second duration. The aggregate
check passed.
