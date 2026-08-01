# Remotion 许可证与版本

## 安装记录

- 安装/核对日期：2026-08-01
- Remotion：`4.0.503`
- `@remotion/cli`：`4.0.503`
- `@remotion/media`：`4.0.503`
- `@remotion/fonts`：`4.0.503`
- `@remotion/captions`：`4.0.503`
- React / React DOM：`19.2.3`
- TypeScript：`5.9.3`
- Node：`v24.15.0`
- npm：`11.12.1`
- Lockfile：`renderers/remotion-contract-v1/package-lock.json`

依赖均由 lockfile 固定。项目未加入 Tailwind、UI 组件库、动画库或 Provider SDK。

## 许可证核对

2026-08-01 阅读：

- <https://www.remotion.dev/license>
- <https://www.remotion.dev/pricing>

页面当时标注更新日期为 2026-07-31。官方说明区分个人/不超过 3 人的组织、4 人及以上的营利组织，以及自动化产品的 Automators 计费场景。

本轮已确认的使用形态仅是本机受控实验：不部署 SaaS、不向第三方提供渲染服务、不调用外部 Provider。用户所属组织规模和未来产品形态没有得到确认，因此不能据此断言生产使用免费。

## 生产化前必须复核

1. 实际组织人数、营利属性和使用主体。
2. 是否形成自动化产品、SaaS 或第三方渲染服务。
3. 届时生效的 License、Pricing 和 Automators 条款。
4. 所有字体、图像、音频及内容本身的授权链。

## 依赖审计

- `npm audit --omit=dev --audit-level=low`：0 vulnerabilities。
- 完整 `npm audit --audit-level=low`：2 个 low severity，来自 ESLint 开发工具链的 `@eslint/plugin-kit`。
- npm 只提供 `--force` 且越过当前声明范围的升级方案；本轮未执行强制升级，详见 Known Issues。
