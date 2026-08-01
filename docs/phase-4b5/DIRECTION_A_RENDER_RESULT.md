# Direction A Render Result

## Preview

- Status: `succeeded`
- Bytes: 668,498
- SHA-256: `129365bf7907b3f4ecca9d8bc6e8d5124be8cbc4af80d391fcd571755c82e7d5`
- Composition Discovery: PASS
- External technical QC: PASS

## Final experimental render

- Status: `succeeded`
- Bytes: 859,881
- SHA-256: `e45266a1131a94db50647a6697d0fadc54e0b90acd897fbbc34a220ffe30d986`
- Video: H.264, 720×960, 30 FPS, yuv420p
- Video timeline: 346 frames / 11.533333 s
- Audio: AAC, 48 kHz, stereo
- Container duration: 11.562667 s
- Media contract comparison: PASS
- External technical QC: PASS
- Local Experimental Master: PASS
- Public release: HELD

Hold reason: `H2 external rights-clearance evidence is not recorded.`

The Preview and Final use the same contract timeline and consume the same upstream Final Mix. The renderer does not mix stems.

## Rollback regression

The retained `PaperCollageVisualV1` Composition was rerun after the new Composition was added. Preview, Final, static frames and External QC all passed. Its Preview and Final hashes remained byte-identical to the recorded Phase 4B outputs, confirming that the rollback Composition was not altered by Direction A.
