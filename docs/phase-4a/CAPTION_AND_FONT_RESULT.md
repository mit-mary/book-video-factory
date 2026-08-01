# Caption 与字体结果

## Caption

- 输入来自冻结的批准稿/时间轴映射，不调用 ASR。
- 句级 Caption，不修改文本、起止点，不静默合并或拆分 Cue。
- Fixture 包含中文 15 cue、英文 15 cue；相同时间点最多显示两行。
- CaptionLayer 按当前帧和 FPS 计算毫秒位置，并应用合同安全区。
- 未实现逐词高亮。

## Font

- 字体由既有 Phase 1.5 字体合同显式解析并绑定 SHA-256。
- 字体二进制复制到 Attempt staging，通过 `@remotion/fonts` + `staticFile()` 加载。
- 无字体或 Hash 不匹配时 Runner 前 fail-closed。
- 字体二进制没有提交到 Git。

## 真实画面核对

从 Final 在 5.70 秒抽帧，确认场景 `S07` 与两行 `LINE 10` / `L10` 同时出现，位置在底部安全区内。1、6、10 秒抽帧还确认了多个静态场景的 Hard Cut 输出。run6 与所检 run5 Final 的 SHA-256 完全相同。

此检查只证明实验 Composition 的基础 Caption/Font 能力，不是生产视觉质量验收。
