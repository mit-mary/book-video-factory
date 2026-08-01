# Phase 4B 前置条件

## 可以继续的范围

Phase 4A 已证明 Contract → Props → Remotion → Result/QC Handoff 的基础链路可行。下一轮可以进行一个受控的视觉模板实验，但不得把实验 Renderer 直接设为默认生产 Renderer。

## 必须保留

- Renderer Contract v1、Request Hash、Attempt write-once 与 external QC 边界。
- Final Mix 唯一音频源；Remotion 不读取 stems、不混音。
- 资产 staging、Hash 再校验、portable refs 与无远程资源。
- Preview/Final 共享 Composition 语义。
- H2 Rights Hold 和 `public_release_allowed=false`。
- Legacy 回滚路径及旧 V1–V5 不修改。

## 进入生产化前仍需完成

1. 许可证/组织规模复核。
2. Partial Output 后真实进程失败与 Quarantine 演练。
3. 字幕溢出、长文本、多语言字体覆盖的系统测试。
4. 更广泛的 width/height/fps/duration 合同矩阵。
5. 开发依赖审计问题的兼容升级评估。
6. Phase 3C/4A 审核与合并策略确认。

## 唯一下一轮建议

只启动“基于同一 Composition 和冻结 Fixture 的最小视觉模板实验”，不要同时启动 Audio Finalizer、Web、批量生产或默认 Renderer 切换。
