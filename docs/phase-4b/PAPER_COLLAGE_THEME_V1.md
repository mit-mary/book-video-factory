# Paper Collage Theme V1

## Identity

- Schema: `paper-collage-theme-v1`.
- File: `renderers/remotion-contract-v1/config/paper-collage-theme-v1.json`.
- Final run SHA-256: `bbc98f21d425d939a848e3c08328caf24e08d65431e14f959b6da49c2b11a1b6`.
- Texture SHA-256: `d6f864b0dacdd6402bd65009610b07d27252d2cbd11e27dc3e5f0fbb26b9ddf5`.

## Frozen token decisions

- Canvas: neutral paper background, 72 px side/top margins and 104 px bottom margin.
- Image card maximum: 480×520, 18 px padding, 3 px outline and one offset shadow.
- Caption: 42 px, 1.25 line height, two lines, stable paper card.
- Motion ceiling: scale delta 0.04, translate 20×16 px and total rotation animation 0.5 degrees.
- Transition: six frames, maximum 12 px entry displacement.

## Enforcement

- Python and Node reject missing keys, unknown keys, invalid colors and out-of-range numbers.
- Theme and texture are Request assets, SHA-bound and staged per Attempt.
- No remote token, texture or fallback is permitted.
- Tokens cannot alter timeline duration or bypass the contract caption safe area.
