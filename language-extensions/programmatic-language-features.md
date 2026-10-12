# 编程式语言功能（Programmatic Language Features）

> 原文：[Programmatic Language Features](https://code.visualstudio.com/api/language-extensions/programmatic-language-features)
> 源文件：`microsoft/vscode-docs` → `api/language-extensions/programmatic-language-features.md`（DateApproved: 10/7/2026）

> 编程式语言功能是一组由 [`vscode.languages.*`](https://code.visualstudio.com/api/references/vscode-api#languages) API 驱动的智能编辑功能。在 Visual Studio Code 中提供动态的语言功能，有两种常见的方式。我们以[悬停](#show-hovers)为例：

```ts
vscode.languages.registerHoverProvider('javascript', {
  provideHover(document, position, token) {
    return {
      contents: ['Hover Content']
    };
  }
});
```

> 如上所示，[`vscode.languages.registerHoverProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerHoverProvider) API 提供了一种为 JavaScript 文件提供悬停内容的简单方式。这个扩展被激活之后，每当你把鼠标悬停在某段 JavaScript 代码上，VS Code 就会查询所有针对 JavaScript 的 [`HoverProvider`](https://code.visualstudio.com/api/references/vscode-api#HoverProvider)，并在一个悬停小部件中显示结果。下面的[语言功能列表](#language-features-listing)和配图的 gif 可以帮你轻松找到你的扩展需要哪个 VS Code API / LSP 方法。

参数中的三个对象，是几乎所有提供者方法共有的：

| 参数 | 含义 |
|---|---|
| `document` | 当前的文本文档（`TextDocument`），可以用 `getText()`、`getWordRangeAtPosition(position)` 等读取内容 |
| `position` | 光标（或鼠标）的位置（`Position`，行列从 0 开始） |
| `token` | 取消令牌（`CancellationToken`）：用户已经移开鼠标、继续输入时，`token.isCancellationRequested` 会变为 `true`，耗时的计算应该及时停止 |

第一个参数 `'javascript'` 是一个[文档选择器](../references/document-selector.md)，最简单的写法是语言 ID。

> 另一种方式是实现一个使用[语言服务器协议](https://microsoft.github.io/language-server-protocol/)通信的语言服务器。它的工作方式是：
>
> - 一个扩展为 JavaScript 提供一个语言客户端和一个语言服务器。
> - 语言客户端和其他 VS Code 扩展一样，运行在 Node.js 扩展宿主的上下文中。它被激活时，会在另一个进程中启动语言服务器，并通过[语言服务器协议](https://microsoft.github.io/language-server-protocol/)与它通信。
> - 你在 VS Code 中把鼠标悬停在 JavaScript 代码上
> - VS Code 把这次悬停告知语言客户端
> - 语言客户端向语言服务器查询悬停结果，并把结果发回 VS Code
> - VS Code 在悬停小部件中显示悬停结果
>
> 这个过程看起来更复杂，但它带来了两大好处：
>
> - 语言服务器可以用任何语言编写
> - 语言服务器可以被复用，为多个编辑器提供智能编辑功能
>
> 更深入的指南，请前往[语言服务器扩展指南](./language-server-extension-guide.md)。

| | 直接实现（Direct Implementation） | 语言服务器（LSP） |
|---|---|---|
| 写法 | 在扩展中调用 `vscode.languages.registerXxxProvider` | 服务端实现 LSP 的请求处理，客户端用 `vscode-languageclient` 自动对接 |
| 运行位置 | 扩展宿主进程 | 单独的进程 |
| 编写语言 | TypeScript / JavaScript | 任意语言 |
| 能否在其他编辑器中复用 | 不能 | 能 |
| 适合 | 功能简单、分析量小 | 正式的语言支持、分析量大（不会拖慢扩展宿主） |

本篇下面的每一节都同时给出了两种写法：“语言服务器协议”小节说明 LSP 服务端要声明的能力和要响应的请求；“直接实现”小节说明对应的 VS Code API。

---

<a id="language-features-listing"></a>
## 语言功能列表（Language Features Listing）

> 这份列表为每个语言功能列出了以下内容：
>
> - 这个语言功能在 VS Code 中的示意图
> - 相关的 VS Code API
> - 相关的 LSP 方法

| VS Code API | LSP 方法 |
| --- | --- |
| [`createDiagnosticCollection`](https://code.visualstudio.com/api/references/vscode-api#languages.createDiagnosticCollection) | [Document Diagnostics](https://microsoft.github.io/language-server-protocol/specification#textDocument_diagnostic) 和 [Publish Diagnostics](https://microsoft.github.io/language-server-protocol/specification#textDocument_publishDiagnostics) |
| [`registerCompletionItemProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerCompletionItemProvider) | [Completion](https://microsoft.github.io/language-server-protocol/specification#textDocument_completion) 和 [Completion Resolve](https://microsoft.github.io/language-server-protocol/specification#completionItem_resolve) |
| [`registerInlineCompletionItemProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerInlineCompletionItemProvider) | |
| [`registerHoverProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerHoverProvider) | [Hover](https://microsoft.github.io/language-server-protocol/specification#textDocument_hover) |
| [`registerSignatureHelpProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerSignatureHelpProvider) | [SignatureHelp](https://microsoft.github.io/language-server-protocol/specification#textDocument_signatureHelp) |
| [`registerDefinitionProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerDefinitionProvider) | [Definition](https://microsoft.github.io/language-server-protocol/specification#textDocument_definition) |
| [`registerTypeDefinitionProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerTypeDefinitionProvider) | [TypeDefinition](https://microsoft.github.io/language-server-protocol/specification#textDocument_typeDefinition) |
| [`registerImplementationProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerImplementationProvider) | [Implementation](https://microsoft.github.io/language-server-protocol/specification#textDocument_implementation) |
| [`registerReferenceProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerReferenceProvider) | [References](https://microsoft.github.io/language-server-protocol/specification#textDocument_references) |
| [`registerDocumentHighlightProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerDocumentHighlightProvider) | [DocumentHighlight](https://microsoft.github.io/language-server-protocol/specification#textDocument_documentHighlight) |
| [`registerDocumentSymbolProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerDocumentSymbolProvider) | [DocumentSymbol](https://microsoft.github.io/language-server-protocol/specification#textDocument_documentSymbol) |
| [`registerCodeActionsProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerCodeActionsProvider) | [CodeAction](https://microsoft.github.io/language-server-protocol/specification#textDocument_codeAction) |
| [`registerCodeLensProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerCodeLensProvider) | [CodeLens](https://microsoft.github.io/language-server-protocol/specification#textDocument_codeLens) 和 [CodeLens Resolve](https://microsoft.github.io/language-server-protocol/specification#codeLens_resolve) |
| [`registerDocumentLinkProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerDocumentLinkProvider) | [DocumentLink](https://microsoft.github.io/language-server-protocol/specification#textDocument_documentLink) 和 [DocumentLink Resolve](https://microsoft.github.io/language-server-protocol/specification#documentLink_resolve) |
| [`registerColorProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerColorProvider) | [DocumentColor](https://microsoft.github.io/language-server-protocol/specification#textDocument_documentColor) 和 [Color Presentation](https://microsoft.github.io/language-server-protocol/specification#textDocument_colorPresentation) |
| [`registerDocumentFormattingEditProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerDocumentFormattingEditProvider) | [Formatting](https://microsoft.github.io/language-server-protocol/specification#textDocument_formatting) |
| [`registerDocumentRangeFormattingEditProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerDocumentRangeFormattingEditProvider) | [RangeFormatting](https://microsoft.github.io/language-server-protocol/specification#textDocument_rangeFormatting) |
| [`registerOnTypeFormattingEditProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerOnTypeFormattingEditProvider) | [OnTypeFormatting](https://microsoft.github.io/language-server-protocol/specification#textDocument_onTypeFormatting) |
| [`registerRenameProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerRenameProvider) | [Rename](https://microsoft.github.io/language-server-protocol/specification#textDocument_rename) 和 [Prepare Rename](https://microsoft.github.io/language-server-protocol/specification#textDocument_prepareRename) |
| [`registerSelectionRangeProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerSelectionRangeProvider) | [Selection Range](https://microsoft.github.io/language-server-protocol/specification#textDocument_selectionRange) |
| [`registerFoldingRangeProvider`](https://code.visualstudio.com/api/references/vscode-api#languages.registerFoldingRangeProvider) | [FoldingRange](https://microsoft.github.io/language-server-protocol/specification#textDocument_foldingRange) |

**表格的补充说明：**

- 内联补全（`registerInlineCompletionItemProvider`）是 VS Code 自己的 API，LSP 规范中没有对应的方法（所以 LSP 一栏为空）。
- 下文的 [工作区符号](#show-all-symbol-definitions-in-folder) 一节使用的 `registerWorkspaceSymbolProvider`（LSP 方法 `workspace/symbol`）没有列在表中。
- 表中的“类型定义”、“实现”、“文档链接”、“选择范围”、“折叠范围”在下文没有单独的小节，它们的写法与“跳转到定义”等完全类似。另外还有一些提供者没有列入表中，例如 [语义高亮](./semantic-highlight-guide.md) 的 `registerDocumentSemanticTokensProvider`、调用层次的 `registerCallHierarchyProvider`、内嵌提示的 `registerInlayHintsProvider`，完整列表见 [`vscode.languages`](https://code.visualstudio.com/api/references/vscode-api#languages) 命名空间。

**列表中的功能对应 VS Code 中的哪些操作：**

| 功能 | 用户怎么用 |
|---|---|
| 诊断 | 红色 / 黄色波浪线，以及“问题”面板 |
| 补全 | 输入时弹出的建议列表，或按 `Ctrl+Space` |
| 内联补全 | 灰色的“幽灵文字”建议，按 `Tab` 接受 |
| 悬停 | 鼠标悬停 |
| 签名帮助 | 输入 `(` 后显示函数的参数信息 |
| 定义 / 类型定义 / 实现 | `F12` 跳转到定义、**Go to Type Definition**、`Ctrl+F12` 跳转到实现 |
| 引用 | `Shift+F12` 查找所有引用 |
| 文档高亮 | 光标放在一个符号上，同一文件中的其他出现处被高亮 |
| 文档符号 | 大纲视图、`Ctrl+Shift+O`（**Go to Symbol in Editor**，即 `@`）、面包屑导航 |
| 工作区符号 | `Ctrl+T`（**Go to Symbol in Workspace**，即 `#`） |
| 代码操作 | 灯泡图标、`Ctrl+.` 快速修复、重构 |
| CodeLens | 代码上方的可点击小字（如“3 个引用”） |
| 文档链接 | 代码中可以 `Ctrl+点击` 的链接 |
| 颜色 | 颜色值前的小色块和颜色选择器 |
| 格式化 | `Shift+Alt+F` 格式化文档、格式化选定内容、输入时格式化 |
| 重命名 | `F2` |
| 选择范围 | `Shift+Alt+→` 扩大选择 |
| 折叠范围 | 行号旁的折叠箭头 |

（快捷键为 Windows 上的默认值，macOS 上 `Ctrl` 对应 `Cmd`。）

---

<a id="provide-diagnostics"></a>
## 提供诊断（Provide Diagnostics）

> 诊断是一种指出代码中问题的方式。

![用诊断指出一个拼写错误的方法名](images/language-support/diagnostics.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 语言服务器可以通过拉取（pull）或推送（push）模型提供诊断。
>
> 使用拉取诊断时，服务器声明一个诊断提供者，并响应客户端发来的 `textDocument/diagnostic` 请求。使用推送诊断时，服务器向客户端发送 `textDocument/publishDiagnostics` 通知。

| 模型 | 谁发起 | 时机 |
|---|---|---|
| 推送（push） | 服务器主动发送通知 | 服务器自己决定何时检查（比如文档变化后） |
| 拉取（pull） | 客户端发送请求 | 客户端决定何时需要诊断（比如文档可见时），服务器按需计算。LSP 3.17 新增，`vscode-languageclient` 支持 |

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
let diagnosticCollection: vscode.DiagnosticCollection;

export function activate(ctx: vscode.ExtensionContext): void {
  ...
  ctx.subscriptions.push(getDisposable());
  // 创建一个诊断集合，名字会显示在“问题”面板中作为来源
  diagnosticCollection = vscode.languages.createDiagnosticCollection('go');
  ctx.subscriptions.push(diagnosticCollection);
  ...
}

function onChange() {
  let uri = document.uri;
  // check 是 Go 扩展自己的检查函数（例如调用编译器），返回错误列表
  check(uri.fsPath, goConfig).then(errors => {
    diagnosticCollection.clear();
    let diagnosticMap: Map<string, vscode.Diagnostic[]> = new Map();
    errors.forEach(error => {
      let canonicalFile = vscode.Uri.file(error.file).toString();
      // 编译器的行号从 1 开始，VS Code 从 0 开始，所以要减 1
      let range = new vscode.Range(error.line-1, error.startColumn, error.line-1, error.endColumn);
      let diagnostics = diagnosticMap.get(canonicalFile);
      if (!diagnostics) { diagnostics = []; }
      diagnostics.push(new vscode.Diagnostic(range, error.msg, error.severity));
      diagnosticMap.set(canonicalFile, diagnostics);
    });
    // 按文件分组后，为每个文件设置诊断
    diagnosticMap.forEach((diags, file) => {
      diagnosticCollection.set(vscode.Uri.parse(file), diags);
    });
  })
}
```

**诊断与其他功能的不同：** 其他功能都是“VS Code 来问，提供者回答”；诊断则是扩展**主动**把结果放进 `DiagnosticCollection`，VS Code 负责显示。所以没有 `registerDiagnosticProvider`，而是由扩展自己决定何时检查，常见的时机是监听 `workspace.onDidChangeTextDocument`（内容变化）、`onDidSaveTextDocument`（保存）、`onDidOpenTextDocument`（打开）、`onDidCloseTextDocument`（关闭时用 `diagnosticCollection.delete(uri)` 清除）。示例只是一个片段，`document`、`check`、`goConfig` 都来自上下文。

`new vscode.Diagnostic(range, message, severity)` 的 `severity` 是 `vscode.DiagnosticSeverity.Error`（红）、`Warning`（黄）、`Information`（蓝）、`Hint`（只显示省略号）之一。

> **基础**
>
> 为打开的编辑器报告诊断。至少需要在每次保存时进行。更好的做法是，基于编辑器中尚未保存的内容计算诊断。

> **进阶**
>
> 不仅为打开的编辑器报告诊断，还要为打开的文件夹中的所有资源报告诊断，不管它们是否曾在编辑器中打开过。

每个功能小节末尾的“基础 / 进阶”，是对实现完整度的建议：“基础”是最低要求，“进阶”是做得更好的方向。

---

<a id="show-code-completion-proposals"></a>
## 显示代码补全建议（Show Code Completion Proposals）

> 代码补全为用户提供与上下文相关的建议。

![编写代码时，代码补全提示变量、方法和参数名](images/language-support/code-completion.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供补全，以及是否支持 `completionItem\resolve` 方法，为计算出的补全项提供额外的信息。

```json
{
    ...
    "capabilities" : {
        "completionProvider" : {
            "resolveProvider": "true",
            "triggerCharacters": [ '.' ]
        }
        ...
    }
}
```

**关于本篇中的这些 JSON 片段：**

- `initialize` 是 LSP 的第一个请求：客户端启动服务器后，服务器在响应中通过 `capabilities` 告诉客户端“我支持哪些功能”。客户端只会为声明了的功能发送请求。
- 原文中的方法名写成了 `completionItem\resolve`，正确的写法是 `completionItem/resolve`（下文的 `codeLens\resolve` 同理）。
- 这些片段是示意性的：真实的 LSP 中这些值是布尔值 `true`，而不是字符串 `"true"`；`[ '.' ]` 应写成 `[ "." ]`。使用 `vscode-languageserver` 库时，这些是 TypeScript 对象，见 [语言服务器扩展指南](./language-server-extension-guide.md)。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoCompletionItemProvider implements vscode.CompletionItemProvider {
    public provideCompletionItems(
        document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken):
        Thenable<vscode.CompletionItem[]> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(getDisposable());
    ctx.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(
            // 最后的参数是触发字符：输入 . 或 " 时自动弹出补全
            GO_MODE, new GoCompletionItemProvider(), '.', '\"'));
    ...
}
```

（`GO_MODE` 是 Go 扩展中定义的文档选择器，例如 `{ language: 'go', scheme: 'file' }`。）

> **基础**
>
> 你不支持 resolve 提供者。

> **进阶**
>
> 你支持 resolve 提供者，为用户选中的补全建议计算额外的信息。这些信息会显示在选中项的旁边。

**resolve（解析）的意义：** 补全列表可能有几百项，如果每一项都附带完整的文档说明，计算和传输都很慢。所以先只返回标签等基本信息；用户在列表中选中（高亮）某一项时，VS Code 再调用 `resolveCompletionItem` 只为这一项补充 `documentation`、`detail` 等详细信息。直接实现中，就是在提供者类中再实现可选的 `resolveCompletionItem(item, token)` 方法。

---

<a id="show-inline-completions"></a>
## 显示内联补全（Show Inline Completions）

> 内联补全直接在编辑器中呈现多个标记的建议（*幽灵文字*）。

![编写代码时，内联补全以幽灵文字的形式建议代码](images/language-support/inline-completions.gif)

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```ts
vscode.languages.registerInlineCompletionItemProvider({ language: 'javascript' }, {
    provideInlineCompletionItems(document, position, context, token) {
        const result: vscode.InlineCompletionList = {
            items: [],
            commands: [],
        };

        ...

        return result;
    }
});
```

> 你可以在[内联补全示例扩展](https://github.com/microsoft/vscode-extension-samples/blob/main/inline-completions)中查看一个完整的例子。

**补全和内联补全的区别：** 补全是弹出一个下拉列表，通常补全一个单词；内联补全是在光标后直接显示灰色的建议文字（可以是一整行或多行代码，GitHub Copilot 用的就是这种形式），按 `Tab` 接受。

（注意：在 `@types/vscode` 1.140.0 的稳定 API 中，`InlineCompletionList` 只有 `items` 属性，示例中的 `commands` 来自提议中的 API，使用稳定 API 时去掉它即可。也可以直接返回 `InlineCompletionItem[]` 数组，每一项用 `new vscode.InlineCompletionItem(插入的文本, 范围?)` 创建。）

> **基础**
>
> 只针对特定的语言，基于当前行的内容，为一组已知的模式返回内联补全。

> **进阶**
>
> 基于整个文档或工作区的内容，以及更复杂的模式返回内联补全。

---

<a id="show-hovers"></a>
## 显示悬停（Show Hovers）

> 悬停显示鼠标光标下的符号 / 对象的信息。这通常是符号的类型和一段描述。

![悬停在一个工作区和一个方法上时显示详细信息](images/language-support/hovers.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供悬停。

```json
{
    ...
    "capabilities" : {
        "hoverProvider" : "true",
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/hover` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoHoverProvider implements HoverProvider {
    public provideHover(
        document: TextDocument, position: Position, token: CancellationToken):
        Thenable<Hover> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerHoverProvider(
            GO_MODE, new GoHoverProvider()));
    ...
}
```

> **基础**
>
> 显示类型信息，如果有文档的话也包含进来。

> **进阶**
>
> 用与代码着色相同的样式，为方法签名着色。

“与代码相同的样式着色”的做法：悬停内容使用 `MarkdownString`，把签名放进一个带语言标记的代码块中，VS Code 就会用这门语言的语法高亮来显示它：

```ts
const md = new vscode.MarkdownString();
md.appendCodeblock('func Println(a ...any) (n int, err error)', 'go'); // 带高亮的签名
md.appendMarkdown('Println formats using the default formats...');      // 文档说明
return new vscode.Hover(md);
```

---

<a id="help-with-function-and-method-signatures"></a>
## 帮助了解函数和方法签名（Help With Function and Method Signatures）

> 当用户输入一个函数或方法时，显示正在调用的函数 / 方法的信息。

![显示 getPackageInfo 方法的信息，包括必需的参数](images/language-support/signature-help.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供签名帮助。

```json
{
    ...
    "capabilities" : {
        "signatureHelpProvider" : {
            "triggerCharacters": [ '(' ]
        }
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/signatureHelp` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoSignatureHelpProvider implements SignatureHelpProvider {
    public provideSignatureHelp(
        document: TextDocument, position: Position, token: CancellationToken):
        Promise<SignatureHelp> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerSignatureHelpProvider(
            // 输入 ( 时弹出签名帮助，输入 , 时更新当前高亮的参数
            GO_MODE, new GoSignatureHelpProvider(), '(', ','));
    ...
}
```

返回的 `SignatureHelp` 中，`signatures` 是候选签名（函数有重载时可能有多个），`activeSignature` 和 `activeParameter` 指出当前是哪个签名的第几个参数，VS Code 会把它加粗显示。

> **基础**
>
> 确保签名帮助中包含函数或方法的参数的文档。

> **进阶**
>
> 没有额外的要求。

---

<a id="show-definitions-of-a-symbol"></a>
## 显示符号的定义（Show Definitions of a Symbol）

> 让用户在变量 / 函数 / 方法被使用的地方，就能看到它们的定义。

![右键点击一个变量、函数或方法，选择 “Go to Definition” 跳转到定义](images/language-support/goto-definition.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供跳转到定义的位置。

```json
{
    ...
    "capabilities" : {
        "definitionProvider" : "true"
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/definition` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoDefinitionProvider implements vscode.DefinitionProvider {
    public provideDefinition(
        document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken):
        Thenable<vscode.Location> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerDefinitionProvider(
            GO_MODE, new GoDefinitionProvider()));
    ...
}
```

返回的 `Location` 由“哪个文件”（`Uri`）和“文件中的哪个位置”（`Range` 或 `Position`）组成：`new vscode.Location(uri, range)`。实现了定义提供者，也就同时获得了 `Ctrl+点击` 跳转和 **Peek Definition**（`Alt+F12`）。

> **基础**
>
> 如果一个符号有歧义，你可以显示多个定义。

> **进阶**
>
> 没有额外的要求。

（返回 `Location[]` 数组即可显示多个定义。原文用的 “ambivalent” 一词，这里理解为“有歧义”。）

---

<a id="find-all-references-to-a-symbol"></a>
## 查找一个符号的所有引用（Find All References to a Symbol）

> 让用户看到某个变量 / 函数 / 方法 / 符号被使用的所有源代码位置。

![右键点击并选择 “Find All References”，高亮这个符号被使用的所有位置](images/language-support/find-references.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供符号引用的位置。

```json
{
    ...
    "capabilities" : {
        "referencesProvider" : "true"
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/references` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoReferenceProvider implements vscode.ReferenceProvider {
    public provideReferences(
        document: vscode.TextDocument, position: vscode.Position,
        options: { includeDeclaration: boolean }, token: vscode.CancellationToken):
        Thenable<vscode.Location[]> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerReferenceProvider(
            GO_MODE, new GoReferenceProvider()));
    ...
}
```

第三个参数在 API 中的类型是 `vscode.ReferenceContext`，它只有一个属性 `includeDeclaration`：为 `true` 时，结果中还要包含符号的声明处。

> **基础**
>
> 返回所有引用的位置（资源 URI 和范围）。

> **进阶**
>
> 没有额外的要求。

---

<a id="highlight-all-occurrences-of-a-symbol-in-a-document"></a>
## 高亮一个符号在文档中的所有出现（Highlight All Occurrences of a Symbol in a Document）

> 让用户看到一个符号在打开的编辑器中的所有出现之处。

![选中一个符号，高亮它的所有出现之处](images/language-support/document-highlights.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供符号在文档中的位置。

```json
{
    ...
    "capabilities" : {
        "documentHighlightProvider" : "true"
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/documentHighlight` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoDocumentHighlightProvider implements vscode.DocumentHighlightProvider {
    public provideDocumentHighlights(
        document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken):
        vscode.DocumentHighlight[] | Thenable<vscode.DocumentHighlight[]>;
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerDocumentHighlightProvider(
            GO_MODE, new GoDocumentHighlightProvider()));
    ...
}
```

（原文代码中，方法签名后面多了一个 `;`，缺少了方法体的 `{`，实际写的时候是 `...: vscode.DocumentHighlight[] | Thenable<vscode.DocumentHighlight[]> { ... }`。）

**与“查找所有引用”的区别：** 文档高亮只针对当前文件，而且是光标一放上去就自动显示，所以要快；查找所有引用会搜索整个工作区，由用户主动触发。`DocumentHighlight` 还可以带一个 `kind`（`Read` 读取 / `Write` 写入 / `Text` 文本），VS Code 会用不同的背景色区分读和写。

> **基础**
>
> 返回编辑器的文档中找到这些引用的范围。

> **进阶**
>
> 没有额外的要求。

---

<a id="show-all-symbol-definitions-within-a-document"></a>
## 显示文档中的所有符号定义（Show all Symbol Definitions Within a Document）

> 让用户快速导航到打开的编辑器中的任何符号定义。

![使用 @ 导航到打开的编辑器中的符号定义](images/language-support/document-symbols.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供符号在文档中的位置。

```json
{
    ...
    "capabilities" : {
        "documentSymbolProvider" : "true"
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/documentSymbol` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoDocumentSymbolProvider implements vscode.DocumentSymbolProvider {
    public provideDocumentSymbols(
        document: vscode.TextDocument, token: vscode.CancellationToken):
        Thenable<vscode.SymbolInformation[]> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerDocumentSymbolProvider(
            GO_MODE, new GoDocumentSymbolProvider()));
    ...
}
```

文档符号除了用于 `@` 跳转，还驱动**大纲视图**、**面包屑导航**和**粘性滚动**（Sticky Scroll）。

`provideDocumentSymbols` 可以返回两种类型之一：

| 返回类型 | 结构 | 效果 |
|---|---|---|
| `SymbolInformation[]`（示例中的） | 扁平列表，用 `containerName` 表示所属 | 大纲是扁平的 |
| `DocumentSymbol[]` | 树形结构，每个符号有 `children` | 大纲有层级（类下面嵌套方法），推荐使用 |

`DocumentSymbol` 有两个范围：`range` 是符号的完整范围（比如整个函数体），`selectionRange` 是符号名的范围（点击时选中的部分）。

> **基础**
>
> 返回文档中的所有符号。定义符号的种类，例如变量、函数、类、方法等。

> **进阶**
>
> 没有额外的要求。

“符号的种类”是 `vscode.SymbolKind` 枚举（`Variable`、`Function`、`Class`、`Method`……），决定了符号在列表中显示的图标。

---

<a id="show-all-symbol-definitions-in-folder"></a>
## 显示文件夹中的所有符号定义（Show all Symbol Definitions in Folder）

> 让用户快速导航到 VS Code 中打开的文件夹（工作区）中任何位置的符号定义。

![使用 # 导航到工作区中的符号定义](images/language-support/workspace-symbols.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供全局的符号位置。

```json
{
    ...
    "capabilities" : {
        "workspaceSymbolProvider" : "true"
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `workspace/symbol` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoWorkspaceSymbolProvider implements vscode.WorkspaceSymbolProvider {
    public provideWorkspaceSymbols(
        query: string, token: vscode.CancellationToken):
        Thenable<vscode.SymbolInformation[]> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerWorkspaceSymbolProvider(
            new GoWorkspaceSymbolProvider()));
    ...
}
```

注意两点不同：`registerWorkspaceSymbolProvider` **没有**文档选择器参数（它不针对某个文档，而是针对整个工作区）；`provideWorkspaceSymbols` 的参数是用户输入的搜索文字 `query`，而不是文档和位置。

> **基础**
>
> 返回打开的文件夹中，由源代码定义的所有符号。定义符号的种类，例如变量、函数、类、方法等。

> **进阶**
>
> 没有额外的要求。

（工作区中的符号可能非常多，实际上应该按 `query` 过滤后再返回。）

---

<a id="possible-actions-on-errors-or-warnings"></a>
## 针对错误或警告的可能操作（Possible Actions on Errors or Warnings）

> 在错误或警告的旁边，为用户提供可能的纠正操作。如果有可用的操作，错误或警告的旁边会出现一个灯泡。用户点击灯泡时，会显示一个可用的代码操作列表。

![点击灯泡，查看可用的代码操作列表](images/language-support/quick-fixes.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供代码操作。

```json
{
    ...
    "capabilities" : {
        "codeActionProvider" : "true"
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/codeAction` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoCodeActionProvider implements vscode.CodeActionProvider<vscode.CodeAction> {
    public provideCodeActions(
        document: vscode.TextDocument, range: vscode.Range | vscode.Selection,
        context: vscode.CodeActionContext, token: vscode.CancellationToken):
        Thenable<vscode.CodeAction[]> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            GO_MODE, new GoCodeActionProvider()));
    ...
}
```

**代码操作的组成：**

```ts
// context.diagnostics 是光标所在范围内的诊断，据此决定提供哪些修复
const fix = new vscode.CodeAction('将 fmt.Prinln 改为 fmt.Println', vscode.CodeActionKind.QuickFix);
fix.edit = new vscode.WorkspaceEdit();                 // 执行这个操作时应用的编辑
fix.edit.replace(document.uri, range, 'Println');
fix.diagnostics = [context.diagnostics[0]];            // 这个操作修复的是哪条诊断
fix.isPreferred = true;                                // 首选修复，可以用“自动修复”快捷键直接应用
```

| `CodeActionKind` | 用途 |
|---|---|
| `QuickFix` | 快速修复错误或警告 |
| `Refactor`（`RefactorExtract`、`RefactorInline`、`RefactorRewrite`……） | 重构，出现在 **Refactor...** 菜单中 |
| `Source`（`SourceOrganizeImports`、`SourceFixAll`） | 作用于整个文件的操作，比如整理导入；可以配置为保存时执行（`editor.codeActionsOnSave`） |

`registerCodeActionsProvider` 的第三个参数 `metadata` 可以声明 `providedCodeActionKinds`，让 VS Code 知道这个提供者能提供哪些种类，从而在只请求特定种类（例如只要重构）时跳过它。

> **基础**
>
> 为纠正错误 / 警告的操作提供代码操作。

> **进阶**
>
> 此外，提供源代码操纵类的操作，例如重构。比如 **Extract Method**（提取方法）。

---

<a id="codelens---show-actionable-context-information-within-source-code"></a>
## CodeLens：在源代码中显示可操作的上下文信息（CodeLens - Show Actionable Context Information Within Source Code）

> 为用户提供可操作的、上下文相关的信息，穿插显示在源代码之间。

![CodeLens 提供上下文信息](images/language-support/code-lens.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供 CodeLens 结果，以及是否支持用 `codeLens\resolve` 方法把 CodeLens 绑定到它的命令。

```json
{
    ...
    "capabilities" : {
        "codeLensProvider" : {
            "resolveProvider": "true"
        }
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/codeLens` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoCodeLensProvider implements vscode.CodeLensProvider {
    public provideCodeLenses(document: TextDocument, token: CancellationToken):
        CodeLens[] | Thenable<CodeLens[]> {
    ...
    }

    public resolveCodeLens?(codeLens: CodeLens, token: CancellationToken):
         CodeLens | Thenable<CodeLens> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerCodeLensProvider(
            GO_MODE, new GoCodeLensProvider()));
    ...
}
```

**CodeLens 的两阶段：**

| 阶段 | 方法 | 做什么 |
|---|---|---|
| 1 | `provideCodeLenses` | 快速返回“哪些位置要显示 CodeLens”（只有 `range`，还没有 `command`） |
| 2 | `resolveCodeLens`（可选） | 当 CodeLens 滚动到可见区域时，再计算它的 `command`（显示的文字 `title` 和点击时执行的命令） |

比如“3 个引用”：第 1 阶段只需要找出所有函数的位置；第 2 阶段才去统计这个函数的引用数，计算量大的部分只对可见的 CodeLens 进行。如果 `provideCodeLenses` 返回时已经带上了 `command`，就不需要 resolve。CodeLens 的 `command` 是一个 `vscode.Command` 对象（`{ title, command, arguments }`），点击时执行的命令需要已经注册（见 [命令](../extension-guides/command.md)）。

> **基础**
>
> 定义一个文档可用的 CodeLens 结果。

> **进阶**
>
> 通过响应 `codeLens/resolve`，把 CodeLens 结果绑定到一个命令。

---

<a id="show-color-decorators"></a>
## 显示颜色装饰器（Show Color Decorators）

> 让用户预览和修改文档中的颜色。

![显示颜色选择器](images/language-support/color-decorators.png)

截图中，CSS 代码里每个颜色值（如 `#fff`、`rgb(...)`）前面都有一个小色块；鼠标悬停在色块上，弹出了颜色选择器，可以拖动选择颜色，上方的标题栏可以在不同的颜色格式之间切换。

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供颜色信息。

```json
{
    ...
    "capabilities" : {
        "colorProvider" : "true"
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/documentColor` 和 `textDocument/colorPresentation` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoColorProvider implements vscode.DocumentColorProvider {
    public provideDocumentColors(
        document: vscode.TextDocument, token: vscode.CancellationToken):
        Thenable<vscode.ColorInformation[]> {
    ...
    }
    public provideColorPresentations(
        color: Color, context: { document: TextDocument, range: Range }, token: vscode.CancellationToken):
        Thenable<vscode.ColorPresentation[]> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerColorProvider(
            GO_MODE, new GoColorProvider()));
    ...
}
```

| 方法 | 做什么 |
|---|---|
| `provideDocumentColors` | 找出文档中所有的颜色值，返回它们的位置和颜色值（`ColorInformation` = `Range` + `Color`，`Color` 的 RGBA 分量取值为 0～1） |
| `provideColorPresentations` | 用户在颜色选择器中选了一个新颜色后，返回这个颜色可以写成的文字形式（`ColorPresentation`，如 `#ff0000`、`rgb(255, 0, 0)`），用户可以在它们之间切换 |

> **基础**
>
> 返回文档中所有的颜色引用。为支持的颜色格式（例如 rgb(...)、hsl(...)）提供颜色表示。

> **进阶**
>
> 没有额外的要求。

---

<a id="format-source-code-in-an-editor"></a>
## 在编辑器中格式化源代码（Format Source Code in an Editor）

> 为用户提供格式化整个文档的支持。

![右键点击并选择格式化代码](images/language-support/format-document.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供文档格式化。

```json
{
    ...
    "capabilities" : {
        "documentFormattingProvider" : "true"
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/formatting` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoDocumentFormatter implements vscode.DocumentFormattingEditProvider {
    provideDocumentFormattingEdits(
        document: vscode.TextDocument, options: vscode.FormattingOptions, token: vscode.CancellationToken)
        : vscode.ProviderResult<vscode.TextEdit[]> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerDocumentFormattingEditProvider(
            GO_MODE, new GoDocumentFormatter()));
    ...
}
```

`options` 中有 `tabSize`（缩进宽度）和 `insertSpaces`（用空格还是 Tab 缩进），格式化时应该遵守用户的这些设置。返回值是 `TextEdit[]`，常用 `vscode.TextEdit.replace(range, newText)`、`insert(position, text)`、`delete(range)` 创建。

> **基础**
>
> 不提供格式化支持。

> **进阶**
>
> 你应该始终返回能使源代码被格式化的最小文本编辑。这对于确保诊断结果等标记能被正确调整、不会丢失至关重要。

**为什么要“最小编辑”？** 最省事的做法是返回一个编辑：用格式化后的全文替换整个文档。但这样一来，VS Code 无法知道哪些内容没有变，文档中原有的诊断波浪线、断点、书签、光标位置都会因为“整个文档被替换了”而丢失或错位。只修改真正变化的地方（比如只在某处插入一个空格），这些标记就能跟着正确地移动。如果你的格式化工具只能输出全文，可以先对新旧文本做一次差异比较（diff），再把差异转换成多个小的 `TextEdit`。

---

<a id="format-the-selected-lines-in-an-editor"></a>
## 格式化编辑器中选中的行（Format the Selected Lines in an Editor）

> 为用户提供格式化文档中选中的若干行的支持。

![选中若干行，右键点击并选择格式化代码](images/language-support/format-document-range.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它为行范围提供格式化支持。

```json
{
    ...
    "capabilities" : {
        "documentRangeFormattingProvider" : "true"
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/rangeFormatting` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoDocumentRangeFormatter implements vscode.DocumentRangeFormattingEditProvider{
    public provideDocumentRangeFormattingEdits(
        document: vscode.TextDocument, range: vscode.Range,
        options: vscode.FormattingOptions, token: vscode.CancellationToken):
        vscode.ProviderResult<vscode.TextEdit[]> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerDocumentRangeFormattingEditProvider(
            GO_MODE, new GoDocumentRangeFormatter()));
    ...
}
```

前面 [语言配置](./language-configuration-guide.md#indentation-rules) 一篇提到，`editor.formatOnPaste`（粘贴时格式化）依赖的就是这个范围格式化提供者。

> **基础**
>
> 不提供格式化支持。

> **进阶**
>
> 你应该始终返回能使源代码被格式化的最小文本编辑。这对于确保诊断结果等标记能被正确调整、不会丢失至关重要。

---

<a id="incrementally-format-code-as-the-user-types"></a>
## 在用户输入时增量格式化代码（Incrementally Format Code as the User Types）

> 为用户提供在输入时格式化文本的支持。
>
> **注意**：用户[设置](https://code.visualstudio.com/docs/configure/settings) `editor.formatOnType` 控制在用户输入时是否格式化源代码。

![输入代码时进行格式化的视觉效果](images/language-support/format-on-type.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它在用户输入时提供格式化。它还需要告诉客户端，在哪些字符上应该触发格式化。`moreTriggerCharacters` 是可选的。

```json
{
    ...
    "capabilities" : {
        "documentOnTypeFormattingProvider" : {
            "firstTriggerCharacter": "}",
            "moreTriggerCharacter": [";", ","]
        }
        ...
    }
}
```

（LSP 规范中的字段名是 `moreTriggerCharacter`，没有 s，以 JSON 中的写法为准。）

> 此外，你的语言服务器需要响应 `textDocument/onTypeFormatting` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoOnTypingFormatter implements vscode.OnTypeFormattingEditProvider{
    public provideOnTypeFormattingEdits(
        document: vscode.TextDocument, position: vscode.Position,
        ch: string, options: vscode.FormattingOptions, token: vscode.CancellationToken):
        vscode.ProviderResult<vscode.TextEdit[]> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerOnTypeFormattingEditProvider(
            GO_MODE, new GoOnTypingFormatter()));
    ...
}
```

注意：示例的注册调用中漏掉了触发字符。`registerOnTypeFormattingEditProvider` 的签名是 `(selector, provider, firstTriggerCharacter, ...moreTriggerCharacter)`，触发字符是**必填**的，例如：

```ts
vscode.languages.registerOnTypeFormattingEditProvider(GO_MODE, new GoOnTypingFormatter(), '}', ';', ',');
```

参数 `ch` 就是刚刚输入的那个触发字符，比如输入 `}` 时，可以只格式化这个 `}` 所闭合的代码块。

> **基础**
>
> 不提供格式化支持。

> **进阶**
>
> 你应该始终返回能使源代码被格式化的最小文本编辑。这对于确保诊断结果等标记能被正确调整、不会丢失至关重要。

---

<a id="rename-symbols"></a>
## 重命名符号（Rename Symbols）

> 让用户重命名一个符号，并更新对这个符号的所有引用。

![重命名一个符号，并把所有引用更新为新名称](images/language-support/rename.gif)

<a id="language-server-protocol"></a>
#### 语言服务器协议（Language Server Protocol）

> 在对 `initialize` 方法的响应中，你的语言服务器需要声明它提供重命名。

```json
{
    ...
    "capabilities" : {
        "renameProvider" : "true"
        ...
    }
}
```

> 此外，你的语言服务器需要响应 `textDocument/rename` 请求。

<a id="direct-implementation"></a>
#### 直接实现（Direct Implementation）

```typescript
class GoRenameProvider implements vscode.RenameProvider {
    public provideRenameEdits(
        document: vscode.TextDocument, position: vscode.Position,
        newName: string, token: vscode.CancellationToken):
        Thenable<vscode.WorkspaceEdit> {
    ...
    }
}

export function activate(ctx: vscode.ExtensionContext): void {
    ...
    ctx.subscriptions.push(
        vscode.languages.registerRenameProvider(
            GO_MODE, new GoRenameProvider()));
    ...
}
```

返回的是 `WorkspaceEdit`（工作区编辑），而不是 `TextEdit[]`，因为重命名通常要修改多个文件：

```ts
const edit = new vscode.WorkspaceEdit();
edit.replace(fileA, rangeInA, newName);  // 修改文件 A 中的一处
edit.replace(fileB, rangeInB, newName);  // 修改文件 B 中的一处
return edit;
```

`RenameProvider` 还有一个可选方法 `prepareRename(document, position, token)`，对应表格中的 LSP 方法 **Prepare Rename**：在弹出重命名输入框之前调用，用来检查光标位置是否可以重命名（不能重命名时抛出错误，给出提示），并返回要重命名的范围或默认的名称。

> **基础**
>
> 不提供重命名支持。

> **进阶**
>
> 返回需要执行的所有工作区编辑的列表，例如在所有包含这个符号引用的文件中进行的所有编辑。

---

## 本篇小结

```text
两种实现方式
  直接实现：vscode.languages.registerXxxProvider(selector, provider)
  语言服务器：initialize 响应中声明 capabilities，并响应对应的 textDocument/xxx 请求

共同模式：VS Code 在需要时调用 provideXxx(document, position, token)，提供者返回结果
  例外：诊断由扩展主动写入 createDiagnosticCollection()；工作区符号没有 selector
  两阶段：补全、CodeLens、文档链接可以先返回简要结果，再 resolve 补充细节

功能 → 主要返回类型
  补全 CompletionItem[]       内联补全 InlineCompletionItem[]    悬停 Hover（MarkdownString）
  签名 SignatureHelp          定义 / 引用 Location[]              文档高亮 DocumentHighlight[]
  文档符号 DocumentSymbol[]    工作区符号 SymbolInformation[]      代码操作 CodeAction[]
  CodeLens CodeLens[]         颜色 ColorInformation[]            格式化 TextEdit[]（最小编辑）
  重命名 WorkspaceEdit（跨文件）
```
