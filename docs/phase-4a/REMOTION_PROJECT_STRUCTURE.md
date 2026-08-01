# Remotion 实验项目结构

隔离项目位于 `renderers/remotion-contract-v1/`：

```text
config/renderer-capabilities.json
public/attempts/                 # Git ignored，按 Attempt 隔离
scripts/
  contract-props.mjs
  list-compositions.mjs
  render-contract.mjs
src/
  Root.tsx
  components/
    CaptionLayer.tsx
    SegmentScene.tsx
  compositions/
    ContractConformance.tsx
  contract/
    parse-props.ts
    types.ts
  metadata/
    calculate-metadata.ts
tests/contract-props.test.mjs
package.json
package-lock.json
remotion.config.ts
tsconfig.json
```

## 隔离规则

- 项目不包含嵌套 Git 仓库。
- `node_modules/`、`out/`、`public/attempts/` 和构建缓存均被 `.gitignore` 排除。
- 真实 Fixture、字体二进制、staging 媒体和 MP4 不提交。
- Remotion 没有注册为默认 Renderer，也未改变现有生产入口。

## 身份

- Renderer ID：`remotion-contract-conformance-v1`
- Renderer Version：`0.1.0-experimental`
- Composition：`ContractConformanceV1`
- 扩展命名空间：`io.github.mit-mary.book-video-factory.remotion`
