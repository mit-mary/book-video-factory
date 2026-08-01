# Failure Tests 结果

## 自动化覆盖

Python Facade：

1. 缺图片：Runner 前 fail-closed。
2. Asset Hash 错误：Runner 前 fail-closed。
3. 缺 Final Mix：Runner 前 fail-closed。
4. 缺字体：Runner 前 fail-closed。
5. 不支持的 Capability：blocked，Runner 不调用。
6. Composition ID 不存在：拒绝，Runner 不调用。
7. Node 进程非零：terminal failed。
8. 进程返回 0 但输出不存在：terminal failed。
9. 固定 Attempt 路径已存在：抛出合同错误并保留原文件。
10. 固定 output 已存在：拒绝并保留原输出。
11. 奇数 H.264 尺寸：拒绝，禁止静默取整。

Node wrapper：

- Props Request identity mismatch：在调用 Remotion 前拒绝。
- 未知 Composition identity：拒绝。
- 基本 Request identity：通过。

## 真实实验中保留的失败证据

- run1：旧兼容 Snapshot 不允许直接插入 Final Mix；修为先生成兼容 Snapshot，再绑定独立 Phase 4A Snapshot。
- run2：Preview `rights.scope=final` 与 render mode 不符；修为 scope 跟随 render mode。
- run3：真实 Preview 渲染成功，但 probe 发现 `yuvj420p` 和 AAC/Container 时长差；未误标成功。修为 PNG 中间帧、视频帧时长权威探测和有证据的 AAC 容差。
- run4：Windows GBK 解码 Remotion UTF-8 进度字符失败；修为 Phase 4A 子进程显式 UTF-8，并保留 run4 证据。
- run5：Preview/Final 均成功。
- run6：在占位尺寸与偶数 H.264 校验修复后重跑，Preview/Final 再次成功且输出 Hash 与 run5 相同。

所有失败路径均未覆盖旧输出，也未修改 Legacy 实现。
