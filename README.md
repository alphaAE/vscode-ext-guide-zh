# VS Code 扩展开发中文学习指南

这是 [VS Code 扩展 API 官方文档](https://code.visualstudio.com/api) 的中文二创版本：保留原文结构，关键内容先翻译再讲解，难点配上图示、表格和带中文注释的代码。

- 原文来源：[microsoft/vscode-docs](https://github.com/microsoft/vscode-docs) 仓库的 `api/` 目录（提交 `aeaa6ff`，2026-10-10），共 76 篇，已全部收录
- 目录结构与原文 `api/` 保持一致，方便对照阅读；原文的图片、视频一并收录，路径不变
- 每个标题前都保留了原文的英文锚点（`<a id="...">`），官方文档中的 `#anchor` 在这里同样可用
- 文中补充的 API 用法均对照 `@types/vscode` 1.140.0 核实过；原文中发现的错误和过时内容，在正文中就地注明，并汇总在 [原文勘误清单](./errata.md)
- 编写规则见 [编写规范](./CONVENTIONS.md)，统一译法见 [术语表](./glossary.md)
- 许可：文档沿用原文的 [CC BY 3.0 US](https://creativecommons.org/licenses/by/3.0/us/) 协议，示例代码与 `tools/` 脚本采用 MIT 协议；原作品版权归 Microsoft Corporation 所有，本仓库为非官方的翻译改编版本。详见 [LICENSE.md](./LICENSE.md)

## 建议的阅读顺序

```text
第一阶段（必读）：入门 → 扩展能力 → 扩展指南中的“命令”“树视图”“Webview” → UX 指南概览
第二阶段（按需）：根据要做的扩展类型，阅读扩展指南 / 语言扩展 / AI 扩展中对应的篇目
第三阶段（上线）：测试与发布（打包、测试、CI、发布）
随时查阅：参考（贡献点、激活事件、when 子句、内置命令、主题颜色、图标）
遇到特殊环境：高级主题（扩展宿主、远程开发、提议的 API）
```

## 目录

[扩展 API 总览](./index.md)：整套文档的地图，扩展能做什么、该从哪里读起

<a id="get-started"></a>
### 入门（Get Started）

1. [你的第一个扩展](./get-started/your-first-extension.md)：生成、运行、修改、调试 Hello World
2. [扩展的结构](./get-started/extension-anatomy.md)：激活事件、贡献点、VS Code API 三大核心概念
3. [总结与后续学习路线](./get-started/wrapping-up.md)：后续章节地图、接入问题报告流程

<a id="extension-capabilities"></a>
### 扩展能力（Extension Capabilities）

1. [扩展能力概览](./extension-capabilities/overview.md)：扩展能做什么、不能做什么（能力地图）
2. [通用能力](./extension-capabilities/common-capabilities.md)：命令、配置、快捷键、菜单、数据存储、通知、快速选择、文件选择、输出、进度
3. [扩展工作台](./extension-capabilities/extending-workbench.md)：界面各区域，以及视图容器、树视图、Webview、状态栏项
4. [主题](./extension-capabilities/theming.md)：颜色主题、文件图标主题、产品图标主题

<a id="extension-guides"></a>
### 扩展指南（Extension Guides）

1. [扩展指南概览](./extension-guides/overview.md)：各篇指南与官方示例的对照表
2. [命令](./extension-guides/command.md)：注册与执行命令、命令 URI、处理函数的参数
3. [树视图 API](./extension-guides/tree-view.md)：TreeDataProvider、视图容器、视图操作、欢迎内容
4. [Webview API](./extension-guides/webview.md)：面板、资源加载、消息传递、持久化、安全
5. [自定义编辑器 API](./extension-guides/custom-editors.md)：文本型与二进制型自定义编辑器、撤销 / 保存 / 备份
6. [虚拟文档](./extension-guides/virtual-documents.md)：TextDocumentContentProvider 与自定义 scheme
7. [虚拟工作区](./extension-guides/virtual-workspaces.md)：在非本地文件系统中正确工作
8. [Web 扩展](./extension-guides/web-extensions.md)：在 vscode.dev / github.dev 中运行
9. [工作区信任](./extension-guides/workspace-trust.md)：受限模式下的扩展行为
10. [颜色主题](./extension-guides/color-theme.md)、[文件图标主题](./extension-guides/file-icon-theme.md)、[产品图标主题](./extension-guides/product-icon-theme.md)
11. [Markdown 扩展](./extension-guides/markdown-extension.md)：扩展内置 Markdown 预览
12. [自定义数据扩展](./extension-guides/custom-data-extension.md)：不写代码扩展 HTML / CSS 支持
13. [笔记本 API](./extension-guides/notebook.md)：序列化器、控制器、渲染器
14. [任务提供者](./extension-guides/task-provider.md)：贡献任务类型
15. [源代码管理 API](./extension-guides/scm-provider.md)：实现一个 SCM 提供者
16. [调试器扩展](./extension-guides/debugger-extension.md)：调试适配器协议（DAP）与调试配置
17. [测试 API](./extension-guides/testing.md)：在测试资源管理器中发现与运行测试
18. [遥测](./extension-guides/telemetry.md)：尊重用户设置的遥测

<a id="ai"></a>
#### AI 扩展（AI）

1. [AI 扩展性概览](./extension-guides/ai/ai-extensibility-overview.md)：各种 AI 扩展方式的选择
2. [语言模型工具 API](./extension-guides/ai/tools.md)：为智能体模式提供工具
3. [MCP 开发者指南](./extension-guides/ai/mcp.md)：MCP 服务器与扩展中的 MCP 注册
4. [聊天参与者 API](./extension-guides/ai/chat.md)：实现 `@参与者`
5. [教程：代码教学聊天参与者](./extension-guides/ai/chat-tutorial.md)
6. [语言模型 API](./extension-guides/ai/language-model.md)：在扩展中调用语言模型
7. [教程：用语言模型 API 生成代码注释](./extension-guides/ai/language-model-tutorial.md)
8. [构建语言模型提示词（prompt-tsx）](./extension-guides/ai/prompt-tsx.md)
9. [语言模型聊天提供者 API](./extension-guides/ai/language-model-chat-provider.md)：向模型选择器提供自己的模型

<a id="ux-guidelines"></a>
### UX 指南（UX Guidelines）

1. [UX 指南概览](./ux-guidelines/overview.md)：界面结构与容器、通用原则
2. [活动栏](./ux-guidelines/activity-bar.md)、[侧边栏](./ux-guidelines/sidebars.md)、[视图](./ux-guidelines/views.md)、[面板](./ux-guidelines/panel.md)
3. [编辑器操作](./ux-guidelines/editor-actions.md)、[状态栏](./ux-guidelines/status-bar.md)、[上下文菜单](./ux-guidelines/context-menus.md)
4. [命令面板](./ux-guidelines/command-palette.md)、[快速选择](./ux-guidelines/quick-picks.md)、[通知](./ux-guidelines/notifications.md)
5. [设置](./ux-guidelines/settings.md)、[演练](./ux-guidelines/walkthroughs.md)、[Webview](./ux-guidelines/webviews.md)

<a id="language-extensions"></a>
### 语言扩展（Language Extensions）

1. [语言扩展概览](./language-extensions/overview.md)：声明式与编程式语言功能、LSP
2. [语法高亮指南](./language-extensions/syntax-highlight-guide.md)：TextMate 语法、作用域、注入语法
3. [语义高亮指南](./language-extensions/semantic-highlight-guide.md)：语义标记提供者与主题化
4. [代码片段指南](./language-extensions/snippet-guide.md)
5. [语言配置指南](./language-extensions/language-configuration-guide.md)：注释、括号、自动闭合、缩进、折叠
6. [编程式语言功能](./language-extensions/programmatic-language-features.md)：补全、悬停、定义、诊断、格式化等的 API 与 LSP 对照
7. [语言服务器扩展指南](./language-extensions/language-server-extension-guide.md)：用 vscode-languageclient / server 实现语言服务器
8. [嵌入式编程语言](./language-extensions/embedded-languages.md)：语言服务与请求转发

<a id="working-with-extensions"></a>
### 测试与发布（Working with Extensions）

1. [测试扩展](./working-with-extensions/testing-extension.md)：@vscode/test-cli 集成测试
2. [发布扩展](./working-with-extensions/publishing-extension.md)：vsce、发布者、预发布、平台特定扩展（含 2026-12-01 全局 PAT 停用说明）
3. [打包扩展代码](./working-with-extensions/bundling-extension.md)：esbuild / webpack
4. [持续集成](./working-with-extensions/continuous-integration.md)：Azure Pipelines / GitHub Actions / GitLab CI 测试与自动发布

<a id="references"></a>
### 参考（References）

1. [贡献点](./references/contribution-points.md)：`package.json` 中 `contributes` 的全部字段
2. [激活事件](./references/activation-events.md)
3. [扩展清单](./references/extension-manifest.md)：`package.json` 的全部字段
4. [内置命令](./references/commands.md)：可用 `executeCommand` 调用的命令
5. [when 子句上下文](./references/when-clause-contexts.md)
6. [主题颜色参考](./references/theme-color.md)：全部 971 个颜色 ID
7. [产品图标参考](./references/icons-in-labels.md)：`$(icon)` 语法与全部图标 ID
8. [文档选择器](./references/document-selector.md)
9. VS Code API（`vscode` 命名空间的完整参考）：请直接查阅 [官方 API 参考](https://code.visualstudio.com/api/references/vscode-api) 或本地的 `@types/vscode`（原文中这一篇由 `vscode.d.ts` 自动生成，未收录）

<a id="advanced-topics"></a>
### 高级主题（Advanced Topics）

1. [扩展宿主](./advanced-topics/extension-host.md)：本地 / Web / 远程扩展宿主与 `extensionKind`
2. [支持远程开发和 GitHub Codespaces](./advanced-topics/remote-extensions.md)
3. [使用提议的 API](./advanced-topics/using-proposed-api.md)
4. [编写 Python 扩展](./advanced-topics/python-extension-template.md)
5. [从 TSLint 迁移到 ESLint](./advanced-topics/tslint-eslint-migration.md)
