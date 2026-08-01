# Remotion Capability 声明

Capability Document：`renderers/remotion-contract-v1/config/renderer-capabilities.json`

## 已声明并验证

- `still_images`
- `captions`（句级、最多两行、无逐词高亮）
- `audio_playback`（`final_mix_only`、音量不变）
- `preview`
- `deterministic_render`（语义级，不承诺跨平台编码字节相同）

## 明确不支持

- `audio_mixing`
- `word_highlight`
- `camera_motion`
- `vector_overlays`
- `waveform`
- `video_clips`
- `layered_images`
- advanced transitions

场景只取每个 Segment 的单张 still image，并以 Hard Cut 切换。请求未声明或实现不支持的 Capability 时，Python Facade 在进程启动前返回 blocked/failed 结果。
