# Phase 4A 已知问题

1. H2 外部权利证明缺失。技术 QC 通过也不能 Public Release。
2. Remotion 许可证的生产适用性取决于组织规模和未来产品形态；当前只完成本地实验判断，生产化前必须复核。
3. 完整 `npm audit` 有 2 个 low severity ESLint 开发依赖问题；生产依赖审计为 0。当前自动修复要求 `--force` 并越过声明范围，本轮没有强制升级。
4. 字节级确定性不跨平台承诺；Capability 只声明 semantic determinism。
5. AAC 编码导致音频/Container 比视频帧时间轴长 42 ms；外部 QC 使用已记录的一帧视频加一帧 AAC 容差。
6. 真实进程创建 Partial Output 后失败的 Quarantine 场景仍未被专门触发。
7. Caption 只完成句级、最多两行；没有逐词高亮、文本溢出自适应或生产级排版。
8. 只支持单张 still image 和 Hard Cut；没有 camera motion、video clip、overlay 或复杂转场。
9. 本轮没有把 Remotion 设为默认 Renderer，也没有生产切流/回滚演练。
10. Phase 3C 上游 PR #4 仍为 Draft，Phase 4A 分支直接基于其已推送 HEAD `798d05b`。
