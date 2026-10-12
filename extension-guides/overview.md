# 扩展指南（Extension Guides）

> 原文：[Extension Guides](https://code.visualstudio.com/api/extension-guides/overview)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/overview.md`（DateApproved: 10/7/2026）

> 通过 [Hello World](../get-started/your-first-extension.md) 示例学会了 VS Code 扩展 API 的基础知识之后，就可以开始构建真正的扩展了。[扩展能力](../extension-capabilities/overview.md) 一节从宏观上介绍了扩展**能**做什么，而这一节列出了一系列详细的代码指南和示例，讲解**怎样**使用某个具体的 VS Code API。
>
> 在每篇指南或示例中，你会看到：
>
> - 带有详细注释的源代码。
> - 演示示例扩展用法的 gif 动图或图片。
> - 运行示例扩展的说明。
> - 用到的 VS Code API 列表。
> - 用到的贡献点列表。
> - 与示例类似的真实扩展。
> - API 概念的讲解。

“扩展能力”回答的是“能不能做”，这一节回答的是“具体怎么做”。每篇指南基本都对应 [vscode-extension-samples](https://github.com/microsoft/vscode-extension-samples) 仓库中的一个示例，**最好的学习方式是把示例克隆下来，按 `F5` 运行，再对照指南阅读源代码。**

这一页本身是一份**索引**：列出每篇指南、每个示例分别用到了哪些 API 和贡献点。以后想实现某个功能时，可以在这里按 API 名称反查有哪些示例可以参考。

---

<a id="guides--samples"></a>
## 指南与示例（Guides & Samples）

> 下面是 VS Code 网站上的指南，以及它们用到的 [VS Code API](https://code.visualstudio.com/api/references/vscode-api) 和[贡献点](../references/contribution-points.md)。别忘了参考 [UX 指南](../ux-guidelines/overview.md)，学习创建扩展界面的最佳实践。

表中 API 链接指向官网的 API 参考，贡献点链接指向本指南的[贡献点参考](../references/contribution-points.md)。

| 指南 | 用到的 API 和贡献点 | 简介 |
| --- | --- | --- |
| [命令](./command.md) | [commands](https://code.visualstudio.com/api/references/vscode-api#commands)<br>[contributes.commands](../references/contribution-points.md#contributes.commands) | 执行、注册命令，控制命令的显示和启用条件 |
| [颜色主题](./color-theme.md) | [contributes.themes](../references/contribution-points.md#contributes.themes) | 制作颜色主题 |
| [文件图标主题](./file-icon-theme.md) | [contributes.iconThemes](../references/contribution-points.md#contributes.iconThemes) | 制作文件图标主题 |
| [产品图标主题](./product-icon-theme.md) | [contributes.productIconThemes](../references/contribution-points.md#contributes.productIconThemes) | 制作产品图标主题 |
| [树视图](./tree-view.md) | [window.createTreeView](https://code.visualstudio.com/api/references/vscode-api#window.createTreeView)<br>[window.registerTreeDataProvider](https://code.visualstudio.com/api/references/vscode-api#window.registerTreeDataProvider)<br>[TreeView](https://code.visualstudio.com/api/references/vscode-api#TreeView)<br>[TreeDataProvider](https://code.visualstudio.com/api/references/vscode-api#TreeDataProvider)<br>[contributes.views](../references/contribution-points.md#contributes.views)<br>[contributes.viewsContainers](../references/contribution-points.md#contributes.viewsContainers) | 在侧边栏中显示树形列表 |
| [Webview](./webview.md) | [window.createWebviewPanel](https://code.visualstudio.com/api/references/vscode-api#window.createWebviewPanel)<br>[window.registerWebviewPanelSerializer](https://code.visualstudio.com/api/references/vscode-api#window.registerWebviewPanelSerializer) | 用 HTML 构建完全自定义的界面 |
| [自定义编辑器](./custom-editors.md) | [window.registerCustomEditorProvider](https://code.visualstudio.com/api/references/vscode-api#window.registerCustomEditorProvider)<br>[CustomTextEditorProvider](https://code.visualstudio.com/api/references/vscode-api#CustomTextEditorProvider)<br>[contributes.customEditors](../references/contribution-points.md#contributes.customEditors) | 为某类文件提供自定义的编辑界面（例如可视化编辑器） |
| [虚拟文档](./virtual-documents.md) | [workspace.registerTextDocumentContentProvider](https://code.visualstudio.com/api/references/vscode-api#workspace.registerTextDocumentContentProvider)<br>[commands.registerCommand](https://code.visualstudio.com/api/references/vscode-api#commands.registerCommand)<br>[window.showInputBox](https://code.visualstudio.com/api/references/vscode-api#window.showInputBox) | 在编辑器中显示不存在于磁盘上的只读文档 |
| [虚拟工作区](./virtual-workspaces.md) | [workspace.fs](https://code.visualstudio.com/api/references/vscode-api#workspace.fs)<br>capabilities.virtualWorkspaces | 让扩展支持“文件不在本地磁盘上”的工作区 |
| [工作区信任](./workspace-trust.md) | [workspace.isTrusted](https://code.visualstudio.com/api/references/vscode-api#workspace.isTrusted)<br>[workspace.onDidGrantWorkspaceTrust](https://code.visualstudio.com/api/references/vscode-api#workspace.onDidGrantWorkspaceTrust)<br>capabilities.untrustedWorkspaces | 在不受信任的工作区中限制扩展的危险操作 |
| [任务提供者](./task-provider.md) | [tasks.registerTaskProvider](https://code.visualstudio.com/api/references/vscode-api#tasks.registerTaskProvider)<br>[Task](https://code.visualstudio.com/api/references/vscode-api#Task)<br>[ShellExecution](https://code.visualstudio.com/api/references/vscode-api#ShellExecution)<br>[contributes.taskDefinitions](../references/contribution-points.md#contributes.taskDefinitions) | 自动提供可运行的任务（如构建脚本） |
| [源代码管理](./scm-provider.md) | [workspace.workspaceFolders](https://code.visualstudio.com/api/references/vscode-api#workspace.workspaceFolders)<br>[SourceControl](https://code.visualstudio.com/api/references/vscode-api#SourceControl)<br>[SourceControlResourceGroup](https://code.visualstudio.com/api/references/vscode-api#SourceControlResourceGroup)<br>[scm.createSourceControl](https://code.visualstudio.com/api/references/vscode-api#scm.createSourceControl)<br>[TextDocumentContentProvider](https://code.visualstudio.com/api/references/vscode-api#TextDocumentContentProvider)<br>[contributes.menus](../references/contribution-points.md#contributes.menus) | 接入 Git 以外的版本控制系统 |
| [调试器扩展](./debugger-extension.md) | [contributes.breakpoints](../references/contribution-points.md#contributes.breakpoints)<br>[contributes.debuggers](../references/contribution-points.md#contributes.debuggers)<br>[debug](https://code.visualstudio.com/api/references/vscode-api#debug) | 为某种语言或运行时提供调试支持 |
| [Markdown 扩展](./markdown-extension.md) | markdown.previewStyles<br>markdown.markdownItPlugins<br>markdown.previewScripts<br>markdown.codeBlockEditorProviders | 扩展内置的 Markdown 预览 |
| [测试扩展](./testing.md) | [TestController](https://code.visualstudio.com/api/references/vscode-api#TestController)<br>[TestItem](https://code.visualstudio.com/api/references/vscode-api#TestItem) | 把测试框架接入 VS Code 的“测试”视图 |
| [自定义数据扩展](./custom-data-extension.md) | contributes.html.customData<br>contributes.css.customData | 不写代码，为 HTML / CSS 补充自定义标签和属性 |

“简介”一列是本指南补充的，原文没有。没有链接的条目（如 `capabilities.virtualWorkspaces`、`markdown.previewStyles`）在原文中也没有链接，具体用法见对应的指南。

此外，扩展指南目录下还有 [Web 扩展](./web-extensions.md)、[笔记本](./notebook.md)、[遥测](./telemetry.md)，以及 [AI 扩展](./ai/ai-extensibility-overview.md) 等系列指南，原文的这张表里没有列出它们。

> 下面是 [VS Code 扩展示例仓库](https://github.com/microsoft/vscode-extension-samples) 中的其他示例。

| GitHub 仓库中的示例 | 用到的 API 和贡献点 | 简介 |
| --- | --- | --- |
| [Webview 示例](https://github.com/microsoft/vscode-extension-samples/tree/main/webview-sample) | [window.createWebviewPanel](https://code.visualstudio.com/api/references/vscode-api#window.createWebviewPanel)<br>[window.registerWebviewPanelSerializer](https://code.visualstudio.com/api/references/vscode-api#window.registerWebviewPanelSerializer) | Webview 的基本用法 |
| [状态栏示例](https://github.com/microsoft/vscode-extension-samples/tree/main/statusbar-sample) | [window.createStatusBarItem](https://code.visualstudio.com/api/references/vscode-api#window.createStatusBarItem)<br>[StatusBarItem](https://code.visualstudio.com/api/references/vscode-api#StatusBarItem) | 在状态栏中显示信息 |
| [树视图示例](https://github.com/microsoft/vscode-extension-samples/tree/main/tree-view-sample) | [window.createTreeView](https://code.visualstudio.com/api/references/vscode-api#window.createTreeView)<br>[window.registerTreeDataProvider](https://code.visualstudio.com/api/references/vscode-api#window.registerTreeDataProvider)<br>[TreeView](https://code.visualstudio.com/api/references/vscode-api#TreeView)<br>[TreeDataProvider](https://code.visualstudio.com/api/references/vscode-api#TreeDataProvider)<br>[contributes.views](../references/contribution-points.md#contributes.views)<br>[contributes.viewsContainers](../references/contribution-points.md#contributes.viewsContainers) | 多种树视图的写法 |
| [任务提供者示例](https://github.com/microsoft/vscode-extension-samples/tree/main/task-provider-sample) | [tasks.registerTaskProvider](https://code.visualstudio.com/api/references/vscode-api#tasks.registerTaskProvider)<br>[Task](https://code.visualstudio.com/api/references/vscode-api#Task)<br>[ShellExecution](https://code.visualstudio.com/api/references/vscode-api#ShellExecution)<br>[contributes.taskDefinitions](../references/contribution-points.md#contributes.taskDefinitions) | 提供自定义任务 |
| [多根工作区示例](https://github.com/microsoft/vscode-extension-samples/tree/main/basic-multi-root-sample) | [workspace.getWorkspaceFolder](https://code.visualstudio.com/api/references/vscode-api#workspace.getWorkspaceFolder)<br>[workspace.onDidChangeWorkspaceFolders](https://code.visualstudio.com/api/references/vscode-api#workspace.onDidChangeWorkspaceFolders) | 处理同时打开多个文件夹的工作区 |
| [补全提供者示例](https://github.com/microsoft/vscode-extension-samples/tree/main/completions-sample) | [languages.registerCompletionItemProvider](https://code.visualstudio.com/api/references/vscode-api#languages.registerCompletionItemProvider)<br>[CompletionItem](https://code.visualstudio.com/api/references/vscode-api#CompletionItem)<br>[SnippetString](https://code.visualstudio.com/api/references/vscode-api#SnippetString) | 提供代码自动补全 |
| [文件系统提供者示例](https://github.com/microsoft/vscode-extension-samples/tree/main/fsprovider-sample) | [workspace.registerFileSystemProvider](https://code.visualstudio.com/api/references/vscode-api#workspace.registerFileSystemProvider) | 实现一个自定义的（内存）文件系统 |
| [编辑器装饰示例](https://github.com/microsoft/vscode-extension-samples/tree/main/decorator-sample) | [TextEditor.setDecorations](https://code.visualstudio.com/api/references/vscode-api#TextEditor.setDecorations)<br>[DecorationOptions](https://code.visualstudio.com/api/references/vscode-api#DecorationOptions)<br>[DecorationInstanceRenderOptions](https://code.visualstudio.com/api/references/vscode-api#DecorationInstanceRenderOptions)<br>[ThemableDecorationInstanceRenderOptions](https://code.visualstudio.com/api/references/vscode-api#ThemableDecorationInstanceRenderOptions)<br>[window.createTextEditorDecorationType](https://code.visualstudio.com/api/references/vscode-api#window.createTextEditorDecorationType)<br>[TextEditorDecorationType](https://code.visualstudio.com/api/references/vscode-api#TextEditorDecorationType)<br>[contributes.colors](../references/contribution-points.md#contributes.colors) | 给编辑器中的文字加背景色、边框等装饰 |
| [本地化（L10N）示例](https://github.com/microsoft/vscode-extension-samples/tree/main/l10n-sample) |  | 让扩展的界面文字支持多语言 |
| [终端示例](https://github.com/microsoft/vscode-extension-samples/tree/main/terminal-sample) | [window.createTerminal](https://code.visualstudio.com/api/references/vscode-api#window.createTerminal)<br>[window.onDidChangeActiveTerminal](https://code.visualstudio.com/api/references/vscode-api#window.onDidChangeActiveTerminal)<br>[window.onDidCloseTerminal](https://code.visualstudio.com/api/references/vscode-api#window.onDidCloseTerminal)<br>[window.onDidOpenTerminal](https://code.visualstudio.com/api/references/vscode-api#window.onDidOpenTerminal)<br>[window.Terminal](https://code.visualstudio.com/api/references/vscode-api#window.Terminal)<br>[window.terminals](https://code.visualstudio.com/api/references/vscode-api#window.terminals) | 创建和控制集成终端 |
| [Vim 示例](https://github.com/microsoft/vscode-extension-samples/tree/main/vim-sample) | [commands](https://code.visualstudio.com/api/references/vscode-api#commands)<br>[StatusBarItem](https://code.visualstudio.com/api/references/vscode-api#StatusBarItem)<br>[window.createStatusBarItem](https://code.visualstudio.com/api/references/vscode-api#window.createStatusBarItem)<br>[TextEditorCursorStyle](https://code.visualstudio.com/api/references/vscode-api#TextEditorCursorStyle)<br>[window.activeTextEditor](https://code.visualstudio.com/api/references/vscode-api#window.activeTextEditor)<br>[Position](https://code.visualstudio.com/api/references/vscode-api#Position)<br>[Range](https://code.visualstudio.com/api/references/vscode-api#Range)<br>[Selection](https://code.visualstudio.com/api/references/vscode-api#Selection)<br>[TextEditor](https://code.visualstudio.com/api/references/vscode-api#TextEditor)<br>[TextEditorRevealType](https://code.visualstudio.com/api/references/vscode-api#TextEditorRevealType)<br>[TextDocument](https://code.visualstudio.com/api/references/vscode-api#TextDocument) | 一个简化的 Vim 模式实现，演示光标和选区的操作 |
| [源代码管理示例](https://github.com/microsoft/vscode-extension-samples/tree/main/source-control-sample) | [workspace.workspaceFolders](https://code.visualstudio.com/api/references/vscode-api#workspace.workspaceFolders)<br>[SourceControl](https://code.visualstudio.com/api/references/vscode-api#SourceControl)<br>[SourceControlResourceGroup](https://code.visualstudio.com/api/references/vscode-api#SourceControlResourceGroup)<br>[scm.createSourceControl](https://code.visualstudio.com/api/references/vscode-api#scm.createSourceControl)<br>[TextDocumentContentProvider](https://code.visualstudio.com/api/references/vscode-api#TextDocumentContentProvider)<br>[contributes.menus](../references/contribution-points.md#contributes.menus) | 源代码管理提供者的完整示例 |
| [评论 API 示例](https://github.com/microsoft/vscode-extension-samples/tree/main/comment-sample) |  | 在代码行旁边添加评论（类似代码审查的批注） |
| [文档编辑示例](https://github.com/microsoft/vscode-extension-samples/tree/main/document-editing-sample) | [commands](https://code.visualstudio.com/api/references/vscode-api#commands)<br>[contributes.commands](../references/contribution-points.md#contributes.commands) | 通过命令修改当前文档的内容 |
| [入门引导示例](https://github.com/microsoft/vscode-extension-samples/tree/main/getting-started-sample) | [contributes.walkthroughs](../references/contribution-points.md#contributes.walkthroughs) | 为扩展制作“入门演练”页面 |
| [测试扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/test-provider-sample) | [TestController](https://code.visualstudio.com/api/references/vscode-api#TestController)<br>[TestItem](https://code.visualstudio.com/api/references/vscode-api#TestItem) | 测试 API 的示例 |

---

<a id="language-extension-samples"></a>
## 语言扩展示例（Language Extension Samples）

> 下面这些是[语言扩展](../language-extensions/overview.md)的示例：

| 示例 | 对应的指南 | 用到的贡献点 |
| --- | --- | --- |
| [代码片段示例](https://github.com/microsoft/vscode-extension-samples/tree/main/snippet-sample) | [代码片段指南](../language-extensions/snippet-guide.md) | [contributes.snippets](../references/contribution-points.md#contributes.snippets) |
| [语言配置示例](https://github.com/microsoft/vscode-extension-samples/tree/main/language-configuration-sample) | [语言配置指南](../language-extensions/language-configuration-guide.md) | [contributes.languages](../references/contribution-points.md#contributes.languages) |
| [LSP 示例](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-sample) | [语言服务器扩展指南](../language-extensions/language-server-extension-guide.md) |  |
| [LSP 日志流示例](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-log-streaming-sample) | 无 |  |
| [LSP 多根工作区服务器示例](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-multi-server-sample) | [Adopting Multi Root Workspace APIs](https://github.com/microsoft/vscode/wiki/Adopting-Multi-Root-Workspace-APIs#language-client--language-server)（GitHub 仓库 wiki） |  |
| [LSP Web 扩展示例](https://github.com/Microsoft/vscode-extension-samples/tree/main/lsp-web-extension-sample) | [语言服务器扩展指南](../language-extensions/language-server-extension-guide.md) |  |

（原文这张表的表头只有两列，但前两行有第三列“贡献点”，这里补上了第三列的表头。）

LSP 是“语言服务器协议（Language Server Protocol）”的缩写，在 [扩展能力概览](../extension-capabilities/overview.md) 中介绍过。

---

## 本篇小结

- 本章的每篇指南基本都对应一个官方示例，**先运行示例，再读指南**，效果最好。
- 这一页可以当作索引用：知道 API 或贡献点的名字时，可以在表中反查有哪些示例可以参考。
- 推荐先学最常用的三篇：[命令](./command.md)、[树视图](./tree-view.md)、[Webview](./webview.md)。
