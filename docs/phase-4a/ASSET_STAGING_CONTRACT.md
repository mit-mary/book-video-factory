# Asset Staging 合同

## 路径与生命周期

每个 Attempt 使用独立且 write-once 的目录：

```text
renderers/remotion-contract-v1/public/attempts/<attempt-id>/
```

执行步骤：

1. 从 Request Root Binding 解析 portable ref。
2. 在复制前验证源文件存在、字节数和 SHA-256。
3. 复制 still image、Final Mix 和明确绑定的字体。
4. 对 staged 文件再次计算 SHA-256。
5. 写入 staging manifest 和 sanitized Props。
6. 若 staging 或 Attempt 路径已存在则 fail-closed，不覆盖。

## 已验证行为

- 缺图片、缺 Final Mix、缺字体和 Hash mismatch 均在 Runner 前失败。
- 已存在 Attempt/staging/output 均被保留，不覆盖。
- run1–run4 的失败证据未删除；run5/run6 各自使用新的 Fixture root 和 Attempt ID。
- 成功与失败的 stdout、stderr、command、probe、Result 均保留在 Attempt 证据中。

## Git 边界

`public/attempts/` 被项目 `.gitignore` 明确排除。真实字体、Fixture 资产、MP4 和 staging manifest 不进入版本库。
