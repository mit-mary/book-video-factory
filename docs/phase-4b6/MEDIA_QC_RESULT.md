# Media QC Result

## Preview

- Render status: `succeeded`
- Request hash: `b2b5b9cd039811bf3adfacd89e3eacecafe4ce120c81a6687bdd0cf16bd8c145`
- 720×1280, H.264, 30 FPS, yuv420p, 540 frames
- Video duration: 18.000 s
- Audio/container duration: 18.048 s
- Audio: AAC, 48 kHz, stereo
- SHA-256: `3b80e4d62ba21fd4c85641defe112592987d4a27bc2520c9a50bb8fb943b138d`
- External technical QC: PASS

## Final experimental master

- Render status: `succeeded`
- Request hash: `4fe5890b155b23c13d3971ad66a4fa2cc331ddf37148accbfdd9acf3d2cb3cc1`
- 1080×1920, H.264, 30 FPS, yuv420p, 540 frames
- Video duration: 18.000 s
- Audio/container duration: 18.048 s
- Audio: AAC, 48 kHz, stereo
- SHA-256: `aac90d79321e1951815ccb4a57d8f087bbeee73f5dfd278be1e6e1e193d924ae`
- Bytes: 4,607,850
- Media contract comparison: PASS
- External technical QC: PASS
- Local Experimental Master: PASS
- Public release allowed: false

The 48 ms audio/container tail is within the approved one-video-frame plus one
AAC-packet tolerance. The renderer consumes the hash-bound upstream Final Mix
as its only audio source; it does not mix stems.

Rights hold remains: `H2 external rights-clearance evidence is not recorded.`
