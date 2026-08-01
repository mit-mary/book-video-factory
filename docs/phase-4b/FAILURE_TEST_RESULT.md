# Failure Test Result

## Phase 4B failure paths

The test suite covers and fails closed for:

1. Unknown template ID.
2. Missing theme token.
3. Theme hash mismatch.
4. Token outside approved ranges.
5. Caption over two lines.
6. Caption safe-area bypass.
7. Image motion envelope unsafe for the canvas.
8. Unsupported motion preset.
9. Unsupported transition preset.
10. Unavailable font.
11. Missing staged texture.
12. Existing Attempt.
13. Composition process failure.
14. Missing output.
15. Missing template capabilities and non-portable texture refs on the Node side.

## Results

- New Python tests: 15/15 PASS.
- Original Phase 4A Node tests: 4/4 PASS.
- Phase 4B Node tests: 10/10 PASS.
- Combined Node: 14/14 PASS.
- Failure: 0; Error: 0; Skip: 0.
