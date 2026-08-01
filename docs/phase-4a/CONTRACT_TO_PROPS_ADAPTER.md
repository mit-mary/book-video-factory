# Contract → Props Adapter

## 权威边界

Python Runtime 仍是 Renderer Contract 的权威 Validator。处理链为：

```text
Release Snapshot
→ RenderRequest v1
→ Python 合同/Hash/Capability/Filesystem 校验
→ Attempt staging
→ Sanitized Props JSON
→ Node 基础身份校验
→ ContractConformanceV1
```

Props 是渲染器内部传输格式，不是新的核心合同。

## Props 内容

包含 Request ID/Hash、Attempt ID、render mode、width/height/fps/duration、Segment 帧区间、staged image refs、Final Mix ref、句级 Caption、字体 ref、安全区和 Renderer 扩展身份。

不包含：

- 生产资产的绝对路径
- Provider 凭据
- 未使用的 Rights/Approval 原文
- Voice/BGM/SFX stems

run6 的实际 Props 搜索未发现 Fixture 项目绝对路径。所有媒体引用均为 `public/` 下的 portable relative path。

## 双侧校验

- Python：完整 Request、Hash、Capability、Root Binding、文件 Hash、Output target、字体、Final Mix、still-only、无 overlay、偶数 H.264 尺寸。
- Node wrapper：Schema Version、Request ID/Hash、Composition ID、render mode 和基本结构。
- Composition：重新解析动态元数据、连续 Segment 覆盖、portable refs。

Node 不复制整个 Python Validator，也不填充会改变输出语义的默认值。
