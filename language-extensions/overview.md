# 语言扩展概览（Language Extensions Overview）

> 原文：[Language Extensions Overview](https://code.visualstudio.com/api/language-extensions/overview)
> 源文件：`microsoft/vscode-docs` → `api/language-extensions/overview.md`（DateApproved: 10/7/2026）

> VS Code 通过语言扩展为各种编程语言提供智能编辑功能。VS Code 的核心编辑器并不提供内置的语言支持，而是提供了一组实现丰富语言功能的 API。
>
> 例如，[HTML](https://github.com/microsoft/vscode/tree/main/extensions/html) 扩展使用这些 API 为 HTML 文件显示语法高亮。同样，当你输入 `console.` 时智能提示中出现了 `log`，这是 [TypeScript Language Features](https://github.com/microsoft/vscode/tree/main/extensions/typescript-language-features) 扩展在工作。
>
> VS Code 自带了其中一些扩展，让你从一开始就拥有丰富的语言支持。

**也就是说，VS Code 编辑器本身对任何一门语言都“一无所知”。** 你打开一个 `.ts` 文件看到的高亮、补全、跳转定义、红色波浪线，全部来自扩展。所以，为一门新语言（或者一种自定义的配置文件格式）提供支持，用的就是这一章介绍的方法。

> 语言功能大致可以分为两类：

| 类别 | 怎么实现 | 包括 | 本章对应的篇目 |
|---|---|---|---|
| 声明式语言功能 | 只写配置文件，不写代码 | 语法高亮、代码片段、括号匹配、注释切换、自动缩进、折叠 | [语法高亮](./syntax-highlight-guide.md)、[代码片段](./snippet-guide.md)、[语言配置](./language-configuration-guide.md) |
| 编程式语言功能 | 写代码（或语言服务器）实现 | 悬停、补全、跳转定义、错误检查、格式化、重构…… | [编程式语言功能](./programmatic-language-features.md)、[语言服务器](./language-server-extension-guide.md)、[语义高亮](./semantic-highlight-guide.md) |

这两类在 [扩展能力概览](../extension-capabilities/overview.md) 中也介绍过。

---

<a id="declarative-language-features"></a>
## 声明式语言功能（Declarative language features）

> 声明式语言功能定义在配置文件中。例如 VS Code 自带的 [html](https://github.com/microsoft/vscode/tree/main/extensions/html)、[css](https://github.com/microsoft/vscode/tree/main/extensions/css) 和 [typescript-basic](https://github.com/microsoft/vscode/tree/main/extensions/typescript-basics) 扩展，它们提供了以下声明式语言功能中的一部分：
>
> - 语法高亮
> - 代码片段补全
> - 括号匹配
> - 括号自动闭合
> - 括号自动包围
> - 注释切换
> - 自动缩进
> - 折叠（基于标记）

几个功能的含义：

| 功能 | 效果 |
|---|---|
| 括号自动闭合 | 输入 `(`，自动补上 `)` |
| 括号自动包围 | 选中一段文字后输入 `(`，选中的文字被括号包起来 |
| 注释切换 | `Ctrl+/` 注释或取消注释当前行 |
| 折叠（基于标记） | 用特殊的注释（如 `// #region` 和 `// #endregion`）标出可折叠的区域 |

注意 TypeScript 有两个扩展：`typescript-basics` 提供声明式的基础功能，`typescript-language-features` 提供编程式的智能功能。这正是 [虚拟工作区](../extension-guides/virtual-workspaces.md#disabling-a-language-extension) 中建议的“基础扩展 + 丰富扩展”的拆分方式。

> 我们为编写提供声明式语言功能的语言扩展准备了三篇指南。
>
> - [语法高亮指南](./syntax-highlight-guide.md)：VS Code 使用 TextMate 语法来实现语法高亮。这篇指南会带你编写一个简单的 TextMate 语法，并把它转换成一个 VS Code 扩展。
> - [代码片段补全指南](./snippet-guide.md)：这篇指南介绍如何把一组代码片段打包成一个扩展。
> - [语言配置指南](./language-configuration-guide.md)：VS Code 允许扩展为任何编程语言定义一个**语言配置**。这个文件控制基本的编辑功能，比如注释切换、括号匹配 / 包围，以及区域折叠（旧版）。

---

<a id="programmatic-language-features"></a>
## 编程式语言功能（Programmatic language features）

> 编程式语言功能包括自动补全、错误检查和跳转到定义。这些功能通常由语言服务器提供支持，语言服务器是一个分析你的项目、提供动态功能的程序。
>
> 一个例子是 VS Code 自带的 [`typescript-language-features`](https://github.com/microsoft/vscode/tree/main/extensions/typescript-language-features) 扩展。它利用 [TypeScript 语言服务](https://github.com/microsoft/TypeScript/wiki/Using-the-Language-Service-API)提供编程式语言功能，例如：
>
> - 悬停信息（[`vscode.languages.registerHoverProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerHoverProvider)）
> - 自动补全（[`vscode.languages.registerCompletionItemProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerCompletionItemProvider)）
> - 跳转到定义（[`vscode.languages.registerDefinitionProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerDefinitionProvider)）
> - 错误检查
> - 格式化
> - 重构
> - 折叠
>
> 这里有一份完整的[编程式语言功能](./programmatic-language-features.md)列表。

![multi-ls](images/overview/multi-ls.png)

图中，左边是 VS Code 提供的各种语言功能 API（悬停 API、补全 API、定义 API、其他语言功能 API），右边是两个语言服务器（HTML 和 Python），每个语言服务器都要分别对接 VS Code 的每一个 API（`provideHoverInfo()`、`provideCompletionItems()`、`provideDefinition()` ……）。

`registerXxxProvider` 系列 API 的模式都一样：注册一个“提供者”，VS Code 在需要时（比如用户把鼠标悬停在代码上）调用它，它返回结果（比如悬停要显示的内容）。命令指南中的命令 URI 示例就用过 `registerHoverProvider`（见 [命令指南](../extension-guides/command.md#command-uris)）。

---

<a id="language-server-protocol"></a>
## 语言服务器协议（Language Server Protocol）

> 通过标准化语言服务器（一种静态代码分析工具）和语言客户端（通常是源代码编辑器）之间的通信，[语言服务器协议](https://microsoft.github.io/language-server-protocol/)让扩展作者可以编写一个代码分析程序，并在多个编辑器中复用它。
>
> 在[编程式语言功能](./programmatic-language-features.md)列表中，你可以找到所有 VS Code 语言功能的列表，以及它们如何对应到[语言服务器协议规范](https://microsoft.github.io/language-server-protocol/specification)。
>
> 我们提供了一篇深入的指南，解释如何在 VS Code 中实现一个语言服务器扩展：
>
> - [语言服务器扩展指南](./language-server-extension-guide.md)

![multi-editor](images/overview/multi-editor.png)

和上一张图对比：中间多了一条竖线“语言服务器协议”。VS Code 和另一个编辑器（图中是 Atom）各自有一个 **LSP 客户端**，负责把自己的语言功能 API 转换成 LSP 协议的消息；右边只需要**一个** HTML 语言服务器，同时服务两个编辑器。

```text
没有 LSP：每个语言服务器 × 每个编辑器，都要单独对接一次（N × M 份工作）
有了 LSP：每个编辑器实现一次 LSP 客户端，每个语言实现一次 LSP 服务器（N + M 份工作）
```

这和 [调试器扩展](../extension-guides/debugger-extension.md#debugging-architecture-of-vs-code) 中调试适配器协议（DAP）、[MCP](../extension-guides/ai/mcp.md) 的思路完全一样。

---

<a id="special-cases"></a>
## 特殊情况（Special cases）

<a id="multi-root-workspace-support"></a>
### 多根工作区支持（Multi-root workspace support）

> 当用户打开一个[多根工作区](https://code.visualstudio.com/docs/editor/multi-root-workspaces)时，你可能需要相应地调整你的语言服务器扩展。这个主题讨论了支持多根工作区的多种方法。

（原文这里说“这个主题讨论了……”，但没有给出链接。相关内容可以参考 [扩展指南](../extension-guides/overview.md#language-extension-samples) 中列出的“LSP 多根工作区服务器示例”，以及它所链接的 [Adopting Multi Root Workspace APIs](https://github.com/microsoft/vscode/wiki/Adopting-Multi-Root-Workspace-APIs#language-client--language-server) wiki 页面。）

**多根工作区**是指在同一个 VS Code 窗口中同时打开多个文件夹（`workspaceFolders` 是数组的原因）。每个文件夹可能是一个独立的项目，有各自的配置。语言服务器要么为每个文件夹启动一个实例，要么在一个实例中区分不同的文件夹。

<a id="embedded-languages"></a>
### 嵌入式语言（Embedded languages）

> 嵌入式语言在 Web 开发中很常见。例如，HTML 中的 CSS / JavaScript，以及 JavaScript / TypeScript 中的 GraphQL。[嵌入式语言](./embedded-languages.md)主题讨论了如何让语言功能在嵌入式语言中也可用。

---

## 本篇小结

```text
VS Code 编辑器本身不懂任何语言 → 一切语言支持都来自语言扩展

声明式（配置文件）
  语法高亮（TextMate 语法）、代码片段、语言配置（括号、注释、缩进、折叠）

编程式（代码）
  vscode.languages.registerXxxProvider（悬停、补全、定义、诊断、格式化……）
  通常由语言服务器实现；LSP 让一个语言服务器服务于多个编辑器（N + M 而不是 N × M）

特殊情况：多根工作区、嵌入式语言（HTML 中的 CSS/JS 等）
```
