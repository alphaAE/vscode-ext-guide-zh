# 术语表

全指南统一使用以下译法。首次出现时写成“中文（English）”，之后只写中文。

## 核心概念

| 英文 | 中文 | 说明 |
|---|---|---|
| Extension | 扩展 | 不译作“插件”。VS Code 官方中文界面使用“扩展” |
| Extension Manifest | 扩展清单 | 即扩展的 `package.json` |
| Activation Event | 激活事件 | 决定扩展何时被加载 |
| Contribution Point | 贡献点 | `package.json` 中 `contributes` 下的静态声明 |
| Contribute | 贡献 | 动词，指通过贡献点向 VS Code 添加功能 |
| VS Code API | VS Code API | 不译 |
| Extension Host | 扩展宿主 | 运行扩展代码的独立进程 |
| Extension Development Host | 扩展开发宿主 | 按 F5 后打开的、加载了开发中扩展的新窗口 |
| Command | 命令 | |
| Command ID | 命令 ID | |
| Command Palette | 命令面板 | `Ctrl+Shift+P` 打开 |
| Quick Open | 快速打开 | `Ctrl+P` 打开 |
| Disposable | Disposable（可释放对象） | 代码中的类型名保留英文 |
| Provider | 提供者 | 如 Hover Provider 译作“悬停提供者” |
| when clause | when 子句 | 控制显示、启用条件的表达式 |
| Context key | 上下文键 | when 子句中使用的变量 |
| Enablement | 启用条件 | |
| Workspace | 工作区 | |
| Workbench | 工作台 | VS Code 的整体界面 |

## 界面部件

| 英文 | 中文 |
|---|---|
| Activity Bar | 活动栏 |
| Side Bar / Primary Side Bar | 侧边栏 / 主侧边栏 |
| Secondary Side Bar | 辅助侧边栏 |
| Panel | 面板 |
| Status Bar | 状态栏 |
| Editor | 编辑器 |
| Editor Group | 编辑器组 |
| View | 视图 |
| View Container | 视图容器 |
| Tree View | 树视图 |
| Webview | Webview（不译） |
| Notification | 通知 |
| Quick Pick | 快速选择 |
| Context Menu | 上下文菜单（右键菜单） |
| Hover | 悬停提示 |
| Gutter | 装订线（行号左侧区域） |
| Debug Console | 调试控制台 |
| Run and Debug view | 运行和调试视图 |
| Settings | 设置 |
| Keybinding / Keyboard Shortcut | 键绑定 / 键盘快捷方式 |
| Title Bar | 标题栏 |
| Views Container | 视图容器 |
| Status Bar Item | 状态栏项 |
| Output Channel / Output Panel | 输出通道 / 输出面板 |
| File Picker | 文件选择器 |
| Glyph Margin | 字形边距（行号左侧显示断点的区域） |
| Breadcrumbs | 面包屑导航 |
| Outline | 大纲视图 |
| Explorer / File Explorer | 资源管理器 |
| Source Control | 源代码管理 |

## 主题与语言

| 英文 | 中文 | 说明 |
|---|---|---|
| Color Theme | 颜色主题 | |
| File Icon Theme | 文件图标主题 | |
| Product Icon Theme | 产品图标主题 | |
| Codicon | codicon（不译） | VS Code 内置图标集，写作 `$(图标名)` |
| Token | 标记 | 代码被拆分出的最小单元 |
| Scope | 作用域 | 标记的分类名，如 `entity.name.function` |
| Syntax Highlighting | 语法高亮 | |
| Semantic Highlighting | 语义高亮 | |
| Grammar / Grammar Injection | 语法 / 语法注入 | |
| Declarative / Programmatic Language Features | 声明式 / 编程式语言功能 | |
| IntelliSense | 智能提示（IntelliSense） | |
| Diagnostics | 诊断 | 波浪线和“问题”面板中的条目 |
| CodeLens | CodeLens（不译） | |
| Debug Adapter Protocol (DAP) | 调试适配器协议 | |
| Language Server / Language Client | 语言服务器 / 语言客户端 | |
| Language Service | 语言服务 | 只针对一种语言的分析库，如 `vscode-css-languageservice` |
| Semantic Token / Token Type / Token Modifier | 语义标记 / 标记类型 / 标记修饰符 | |
| Legend | 图例 | 语义标记类型和修饰符的索引表 |
| Embedded Language | 嵌入式语言 | 如 HTML 中的 CSS |
| Request Forwarding | 请求转发 | |
| Inlay Hint | 内嵌提示 | 代码中显示的参数名、类型等灰色小字 |
| Inline Completion / Ghost Text | 内联补全 / 幽灵文字 | |
| Signature Help | 签名帮助 | |
| Code Action / Quick Fix | 代码操作 / 快速修复 | |
| Peek View | 速览视图 | |
| Overview Ruler | 概览标尺 | 编辑器右侧滚动条位置的标记条 |
| Minimap | 缩略图 | |
| Sticky Scroll | 粘性滚动 | |
| Problem Matcher | 问题匹配器 | |

## 开发与发布

| 英文 | 中文 |
|---|---|
| Scaffold | 脚手架（动词：生成项目骨架） |
| Bundle / Bundler | 打包 / 打包工具 |
| Marketplace | 扩展市场 |
| Publisher | 发布者 |
| Integration Test | 集成测试 |
| Continuous Integration (CI) | 持续集成 |
| Proposed API | 提议的 API（尚未稳定的 API） |
| Language Server Protocol (LSP) | 语言服务器协议 |
| Pre-release | 预发布版本 |
| Platform-specific Extension | 平台特定的扩展 |
| Personal Access Token (PAT) | 个人访问令牌 |
| Verified Publisher | 认证发布者 |
| Extension Pack / Extension Dependency | 扩展包 / 扩展依赖 |
| Remote Development / Workspace Extension / UI Extension | 远程开发 / 工作区扩展 / UI 扩展 |
| Extension Kind | 扩展种类（`extensionKind`） |
| Virtual Workspace / Workspace Trust / Restricted Mode | 虚拟工作区 / 工作区信任 / 受限模式 |
| Walkthrough | 演练 |
| Chat Participant / Language Model Tool | 聊天参与者 / 语言模型工具 |
| Agent / Agent Mode | 智能体 / 智能体模式 |

## 关于命令名称

原文中出现的命令，如 **Developer: Reload Window**、**Debug: Start Debugging**，在本指南中**保留英文**。

原因：VS Code 的中文界面里，命令面板同时支持用中文和英文名称搜索。直接输入英文名称（例如 `reload window`）就能找到对应命令，所以保留英文可以避免中文译名在不同版本之间不一致的问题。
