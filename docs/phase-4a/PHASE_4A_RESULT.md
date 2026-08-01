# Phase 4A 执行结果

## 基本信息

- 仓库：`mit-mary/book-video-factory`
- 基线 SHA：`798d05b`
- 分支：`experiment/remotion-contract-renderer-v1`
- Remotion：`4.0.503`
- React：`19.2.3`
- Node：`v24.15.0`
- npm：`11.12.1`

最终 HEAD 在本报告提交后由 Git 生成；以分支远端 HEAD 为准。

## Scope

- Renderer ID：`remotion-contract-conformance-v1`
- Capability：still images、sentence captions、Final Mix playback、preview、semantic deterministic render
- Legacy 修改：否
- 默认 Renderer：否
- Provider：未调用
- 商业资产：未使用
- 视觉模板：未开发，仅程序生成几何 Fixture

## Contract Adapter

- Request：Renderer Contract v1，Python 权威校验
- Props：sanitized internal transport，保留 Request ID/Hash
- Asset staging：`public/attempts/<attempt-id>/`，Attempt 隔离、write-once
- Hash：源文件与 staged 文件双重 SHA-256 校验
- Attempt：Result、日志、command、probe、QC Handoff 完整

## Composition

- ID：`ContractConformanceV1`
- width/height：由 Props 动态决定；run6 为 720×960
- fps：由 Props 动态决定；run6 为 30
- duration：由 Props 动态决定；run6 为 346 frames / 11.533333 s 视频时间轴
- Timeline：Request Segment start/end frames，Hard Cut
- Audio：staged Final Mix 唯一播放源
- Caption：句级，最多两行
- Font：显式 Hash 绑定并 staged；缺失时 fail-closed

## Preview

- Result：succeeded
- SHA-256：`26794997259ec8941e4c61e97c9e032e045a0861e421077e0b324732ec72ff13`
- Probe：H.264 720×960 30 FPS yuv420p + AAC 48 kHz stereo
- QC：PASS

## Final Experimental

- Result：succeeded
- SHA-256：`d120f4440fbb10175ff01b7949a905314f561f7342a0162b227a96a9e39baa1c`
- Probe：H.264 720×960 30 FPS yuv420p + AAC 48 kHz stereo
- QC：PASS
- Public Release：HELD（H2 Rights Evidence）

## Failure Tests

Missing asset、Hash mismatch、Missing audio、Missing font、Unsupported Capability、Props identity mismatch、Composition mismatch、Process failure、Output missing、已有 Attempt/output、奇数 H.264 尺寸均已覆盖并 fail-closed。

## Tests

- Phase 3C 原基线：159
- Phase 4A 最终 Python：171（8 + 163；新增 Remotion Python 12）
- Node：4/4
- TypeScript：typecheck PASS
- ESLint：PASS
- Composition discovery：Preview/Final PASS
- Real renders：Preview/Final PASS
- Failure：0
- Error：0
- Skip：0

## 已知问题

H2 Rights Hold、许可证生产复核、2 个 low severity 开发依赖审计项、跨平台不承诺字节一致、Partial Output Quarantine 未真实触发。

## 是否通过 Phase 4A

结论：通过。

理由：受控 Fixture 已由同一核心合同驱动 Remotion 真实生成 Preview 与 Final；OutputSpec、FFprobe、external technical QC、失败路径和完整回归均通过，且 Rights Hold 未被绕过。

## 是否允许进入 Phase 4B

结论：允许进入受控的最小视觉模板实验，不允许直接生产切流。

前置条件：继续保持 Final Mix、合同/Hash、Attempt、external QC、Rights Hold 和 Legacy 回滚边界。

## 唯一下一轮建议

只做一个冻结 Fixture 上的最小视觉模板实验；不要并行启动 Audio Finalizer、Web、批量生产或默认 Renderer 替换。
