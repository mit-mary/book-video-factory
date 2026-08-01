# Phase 4B 执行结果

## 基本信息

- 仓库：`mit-mary/book-video-factory`
- 基线 SHA：`5f71439`
- 已验证实现 HEAD：`6e56cb1`
- 分支：`experiment/paper-collage-visual-v1`
- Composition：`PaperCollageVisualV1`
- Template ID：`paper-collage-visual-v1`
- Template Version：`0.1.0-experimental`

最终分支 HEAD 还包含本报告提交，以远端分支 HEAD 为准。

## Scope

- Legacy 修改：否
- 核心 Renderer Contract 修改：否
- 默认 Renderer：否
- Final Mix：保持，唯一音频源
- Provider：未调用
- 商业资产：未使用
- 逐词字幕：未实现
- 波形/HUD：未实现

## Template

- Theme：Hash-bound `paper-collage-theme-v1`
- Layers：纸张背景、背板、图片卡、Segment Marker、Caption Card
- Motion：Frame-driven `subtle`
- Transition：六帧可见卡片位移 `paper-cut`
- Opening：Extension 显式声明 0–1.2 秒测试标题卡
- Caption：句级、最多两行、底部纸张卡
- Font：staged 授权字体，缺失 fail-closed

## Contract Adapter

- Extension：`io.github.mit-mary.book-video-factory.remotion`
- Token Hash：PASS
- Capability：`layered_images`、`camera_motion`、`transitions` 已实现并测试
- Fail-closed：PASS

## Static Frames

- Opening：PASS
- Segment 1：PASS
- Segment 2：PASS
- Segment 3：PASS
- Ending：PASS
- Safety checks：图片全运动包络和 Caption 视觉包络均 PASS

## Preview

- Result：PASS
- SHA：`a2717c3c27a96699bc3a4db3e2d051f425cbf5707b97df36ade80e56d90d64e8`
- Probe：H.264 720×960 30 FPS yuv420p + AAC 48 kHz stereo
- QC：PASS

## Final Experimental

- Result：PASS
- SHA：`d53c2f41ac808c42cec22a711055fffdb768d180526703e7257b52ed5f3e2dbf`
- Probe：PASS
- QC：PASS
- Public Release：HELD（H2 Rights Evidence）

## Tests

- 原 Python 基线：171
- Python：186/186（8 + 178；新增 15）
- 原 Node 基线：4
- Node：14/14（原 4 + 新 10）
- TypeScript：PASS
- ESLint：PASS
- Composition Discovery：Preview/Final PASS
- Real renders：Preview/Final/5 stills PASS
- Failure：0
- Error：0
- Skip：0

## Visual Review

- 优点：纸张拼贴语义明确、装饰克制、图片不变形、字幕高对比、运镜轻微且稳定。
- 问题：仅在程序 Fixture 上验证；真实书籍排版、版权与编辑适配仍未知。
- 是否适合进入真实内容验证：适合一条受控验证，不适合批量或公开发布。

## Known Issues

H2 Rights Hold、Remotion 生产许可证复核、9 个 low 开发依赖项、跨平台不承诺字节一致、Partial Output Quarantine 未真实触发。

## 是否通过 Phase 4B

结论：通过。

理由：独立模板已真实生成 Preview 和 Final；静帧、全运动安全包络、Composition Discovery、FFprobe、外部技术 QC、Failure Tests 与全量回归均通过，且 Contract、Final Mix、Legacy 和 Rights Gate 边界保持。

## 是否允许进入 Phase 4C

结论：有条件允许进入单条真实书籍的受控内容验证；不允许默认公开发布或批量化。

前置条件：逐资产权利证据、H2 保持、同一合同/Hash/Attempt/QC 边界及人工视觉审查。

## 唯一下一轮建议

只允许一条真实书籍的受控内容验证，不允许同时批量化。
