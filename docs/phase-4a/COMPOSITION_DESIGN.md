# Composition 设计

## Composition

- ID：`ContractConformanceV1`
- Preview 与 Final 共用同一 Composition。
- `calculateMetadata` 从 Props 返回 width、height、fps 和 durationInFrames。
- `Root.tsx` 的 2×2、1 FPS、1 frame 仅是满足 Remotion 注册约束的无语义占位值；真实渲染值全部由 Props 覆盖。
- Python 对 H.264 奇数 width/height fail-closed，避免 Remotion 静默向下取整。

## Timeline

- 每个 Segment 使用 Props 中的 `startFrame` / `endFrame` 创建 `Sequence`。
- Segment 必须连续、非空并完整覆盖 Composition duration。
- 场景按 Request 顺序 Hard Cut，不使用 CSS animation/transition。
- still image 使用 `staticFile()` 和 `objectFit: contain`，不变形、不加载远程 URL。

## Audio

Composition 只有一个 `Audio`：staged Final Mix。没有 stem 读取、音量修改、ducking 或浏览器侧混音。

## run6 动态发现

`ContractConformanceV1    30    720x960    346 (11.53 sec)`

Composition discovery 在 Preview 和 Final 两个 Attempt 中均返回 0。
