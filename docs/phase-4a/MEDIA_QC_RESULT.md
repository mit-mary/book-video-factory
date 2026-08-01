# 媒体与外部 QC 结果

## OutputSpec 对比

Preview 与 Final 的技术属性相同，均满足：

- 1 条 H.264 视频流
- 720×960
- 30/1 FPS
- `yuv420p`
- 1 条 AAC 音频流
- 48,000 Hz、2 channels

合同期望时长为 11,520 ticks（ms）。实际：

- 视频：11,533 ticks
- 音频：11,562 ticks
- Container：11,562 ticks

## 有证据的容差

- 视频容差：1 个 30 FPS frame，记录为 35 ticks。
- AAC/Container 容差：1 个视频 frame + 1 个 1024-sample AAC frame，记录为 57 ticks。
- 实际差异分别为 13 和 42 ticks，均在相应容差内。

此处理没有缩短 Final Mix、修改 Timeline 或放宽核心 V4 合同。Probe 的权威 `duration_ticks` 使用视频帧时间轴，同时单独保留 `audio_duration_ticks` 和 `container_duration_ticks`。

## External QC

外部 Adapter 从当前 Attempt 的 QC Handoff 读取 output hash、Request hash、OutputSpec snapshot 和 Rights Hold，不扫描目录猜测状态。Preview 和 Final 均 `technical_status=pass`，且 `public_release_allowed=false`。
