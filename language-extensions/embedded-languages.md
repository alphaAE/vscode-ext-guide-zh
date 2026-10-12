# 嵌入式编程语言（Embedded Programming Languages）

> 原文：[Embedded Programming Languages](https://code.visualstudio.com/api/language-extensions/embedded-languages)
> 源文件：`microsoft/vscode-docs` → `api/language-extensions/embedded-languages.md`（DateApproved: 10/7/2026）

> Visual Studio Code 为编程语言提供了丰富的语言功能。正如你在[语言服务器扩展指南](./language-server-extension-guide.md)中读到的，你可以编写语言服务器来支持任何编程语言。不过，要为嵌入式语言提供这样的支持，需要付出更多的努力。
>
> 如今，嵌入式语言越来越多，例如：
>
> - HTML 中的 JavaScript 和 CSS
> - JavaScript 中的 JSX
> - 模板语言中的插值，例如 Vue、Handlebars 和 Razor
> - PHP 中的 HTML
>
> 本指南重点介绍如何为嵌入式语言实现语言功能。如果你想为嵌入式语言提供语法高亮，可以在[语法高亮指南](./syntax-highlight-guide.md#embedded-languages)中找到相关信息。

**本篇要解决的问题：** 语法高亮层面的嵌入式语言（`embeddedLanguages`）很简单，只是告诉 VS Code “这段是 CSS”。但补全、悬停、错误检查这类智能功能就难了：你的 HTML 语言服务器收到“在第 2 行第 15 列补全”的请求时，它自己并不懂 CSS，该怎么给出 CSS 的补全？

> 本指南包含两个示例，演示了构建这样一个语言服务器的两种方法：**语言服务（Language Services）**和**请求转发（Request Forwarding）**。我们会逐一介绍这两个示例，最后总结每种方法的优缺点。
>
> 两个示例的源代码都可以在这里找到：
>
> - [使用语言服务的嵌入式语言服务器](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-embedded-language-service)
> - [使用请求转发的嵌入式语言服务器](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-embedded-request-forwarding)
>
> 下面是我们将要构建的嵌入式语言服务器：

![示例](images/embedded-languages/embedded-lsp-sample.gif)

> 出于演示的目的，两个示例都贡献了一门新语言 `html1`。你可以创建一个 `.html1` 文件，测试以下功能：
>
> - HTML 标签的补全
> - `<style>` 标签中 CSS 的补全
> - CSS 的诊断（仅限语言服务示例）

| 方法 | 一句话概括 |
|---|---|
| 语言服务 | 自己的语言服务器**内置**各个嵌入语言的分析库，自己算 |
| 请求转发 | 把请求**转交**给 VS Code 中已有的、负责那门语言的扩展去算 |

---

<a id="language-services"></a>
## 语言服务（Language Services）

> **语言服务**是一个为单一语言实现[编程式语言功能](./programmatic-language-features.md)的库。**语言服务器**可以嵌入多个语言服务，来处理嵌入式语言。
>
> 下面是 VS Code 对 HTML 的支持的概况：
>
> - 内置的 [html 扩展](https://github.com/microsoft/vscode/tree/main/extensions/html)只为 HTML 提供语法高亮和语言配置。
> - 内置的 [html-language-features 扩展](https://github.com/microsoft/vscode/tree/main/extensions/html-language-features)包含一个 HTML 语言服务器，为 HTML 提供编程式语言功能。
> - HTML 语言服务器使用 [vscode-html-languageservice](https://github.com/microsoft/vscode-html-languageservice) 来支持 HTML。
> - CSS 语言服务器使用 [vscode-css-languageservice](https://github.com/microsoft/vscode-css-languageservice) 来支持 HTML 中的 CSS。

**语言服务和语言服务器的区别：**

| | 语言服务（language service） | 语言服务器（language server） |
|---|---|---|
| 形式 | 一个普通的库（npm 包），提供 `doComplete(document, position)` 这样的函数 | 一个独立的进程，通过 LSP 协议和编辑器通信 |
| 范围 | 只懂一门语言 | 可以组合多个语言服务 |
| 例子 | `vscode-css-languageservice` | HTML 语言服务器（内部同时用了 HTML 和 CSS 的语言服务） |

> HTML 语言服务器分析一个 HTML 文档，把它拆分成多个语言区域，并使用对应的语言服务来处理语言服务器请求。
>
> 例如：
>
> - 对于在 `<|` 处的自动补全请求，HTML 语言服务器使用 HTML 语言服务提供 HTML 补全。
> - 对于在 `<style>.foo { | }</style>` 处的自动补全请求，HTML 语言服务器使用 CSS 语言服务提供 CSS 补全。

（`|` 表示光标位置。）

> 我们来看看 [lsp-embedded-language-service](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-embedded-language-service) 示例，它是 HTML 语言服务器的一个简化版本，实现了 HTML 和 CSS 的自动补全，以及 CSS 的诊断错误。

<a id="language-services-sample"></a>
### 语言服务示例（Language Services sample）

> **注意**：这个示例假设你已经了解[编程式语言功能主题](./programmatic-language-features.md)和[语言服务器扩展指南](./language-server-extension-guide.md)。代码基于 [lsp-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-sample) 构建。

建议先读完 [语言服务器扩展指南](./language-server-extension-guide.md) 再看本节。

> 源代码可以在 [microsoft/vscode-extension-samples](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-embedded-language-service) 找到。
>
> 与 [lsp-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-sample) 相比，客户端的代码是一样的。
>
> 如上所述，服务器把文档拆分成不同的语言区域，来处理嵌入的内容。
>
> 下面是一个简单的例子：

```html
<div></div>
<style>.foo { }</style>
```

> 在这种情况下，服务器检测到 `<style>` 标签，并把 `.foo { }` 标记为一个 CSS 区域。
>
> 给定一个在特定位置的自动补全请求，服务器使用以下逻辑计算响应：
>
> - 如果这个位置落在某个区域中
>   - 用一个使用这个区域的语言的虚拟文档来处理它，同时把其他所有区域替换为空白
> - 如果这个位置不在任何区域中
>   - 用一个 HTML 的虚拟文档来处理它，同时把所有区域替换为空白
>
> 例如，在这个位置进行自动补全时：

```html
<div></div>
<style>.foo { | }</style>
```

> 服务器判断出这个位置在区域内，并计算出一个具有以下内容的虚拟 CSS 文档（█ 代表空格）：

```css
███████████
███████.foo { | }████████
```

> 然后服务器使用 `vscode-css-languageservice` 分析这个文档，计算出一个补全项列表。因为现在的内容中不包含任何 HTML，CSS 语言服务可以毫无问题地处理它。通过把所有非 CSS 的内容替换为空白，我们省去了手动换算位置偏移的麻烦。

**“替换为空白”这个技巧的妙处：** 如果只把 `.foo { }` 单独拿出来交给 CSS 语言服务，那么原文件中“第 2 行第 15 列”在新文档中就变成了“第 1 行第 8 列”，请求进去要换算，结果出来还要换算回去。而把其他字符都换成空格（换行保留），文档的长度、每一行的位置都与原文件完全一致，**位置可以直接使用，不需要任何换算**。CSS 语言服务只会把这些空格当作空白忽略掉。

> 处理补全请求的服务器代码：

```ts
connection.onCompletion(async (textDocumentPosition, token) => {
  const document = documents.get(textDocumentPosition.textDocument.uri);
  if (!document) {
    return null;
  }

  // 根据光标位置，找到对应的语言模式（HTML 或 CSS）
  const mode = languageModes.getModeAtPosition(document, textDocumentPosition.position);
  if (!mode || !mode.doComplete) {
    return CompletionList.create();
  }
  const doComplete = mode.doComplete!;

  // 交给这个语言模式去计算补全
  return doComplete(document, textDocumentPosition.position);
});
```

> 负责处理所有落在 CSS 区域中的语言服务器请求的 CSS 模式：

```ts
export function getCSSMode(
  cssLanguageService: CSSLanguageService,
  documentRegions: LanguageModelCache<HTMLDocumentRegions>
): LanguageMode {
  return {
    getId() { return 'css' },
    doComplete(document: TextDocument, position: Position) {
      // 获取虚拟 CSS 文档，其中所有非 CSS 的代码都被替换成了空白
      const embedded = documentRegions.get(document).getEmbeddedDocument('css')
      // 使用 vscode-css-languageservice 计算响应
      const stylesheet = cssLanguageService.parseStylesheet(embedded)
      return cssLanguageService.doComplete(embedded, position, stylesheet)
    }
  }
}
```

结构上是“语言模式（LanguageMode）”的分派：每种语言一个模式对象（HTML 模式、CSS 模式……），都实现 `doComplete` 等方法；`getModeAtPosition` 根据光标所在的区域选择模式。要支持新的嵌入语言，就再加一个模式。注意 `position` 原样传给了 CSS 语言服务，这正是“替换为空白”带来的好处。

> 这是一种处理嵌入式语言的简单而有效的方法。不过，这种方法也有一些缺点：
>
> - 你必须不断更新你的语言服务器所依赖的语言服务。
> - 要包含不是用和你的语言服务器同一种语言编写的语言服务，可能很困难。例如，一个用 PHP 编写的 PHP 语言服务器，会发现很难包含用 TypeScript 编写的 `vscode-css-languageservice`。
>
> 下面我们来介绍**请求转发**，它可以解决上述问题。

---

<a id="request-forwarding"></a>
## 请求转发（Request Forwarding）

> 简而言之，请求转发的工作方式与语言服务类似。请求转发方法也接收语言服务器请求，计算出虚拟内容，再计算出响应。
>
> 主要的区别在于：
>
> - 语言服务方法使用库来计算语言服务器的响应，而请求转发则把请求发回 VS Code，让那些处于激活状态、并为嵌入语言注册了补全提供者的扩展来处理。
>
> 还是这个简单的例子：

```html
<div></div>
<style>.foo { | }</style>
```

> 自动补全是这样进行的：
>
> - 语言客户端使用 `workspace.registerTextDocumentContentProvider`，为 `embedded-content` 文档注册一个虚拟文本文档提供者。
> - 语言客户端拦截对 `<FILE_URI>` 的补全请求。
> - 语言客户端判断出请求的位置落在一个 CSS 区域中。
> - 语言客户端构造一个新的 URI，例如 `embedded-content://css/<FILE_URI>.css`。
> - 然后语言客户端调用 `commands.executeCommand('vscode.executeCompletionItemProvider', ...)`
>   - VS Code 的 CSS 语言服务器响应这个提供者请求。
>   - 虚拟文本文档提供者向 CSS 语言服务器提供虚拟内容，其中所有非 CSS 的代码都被替换为空白。
>   - 语言客户端从 VS Code 收到响应，并把它作为响应返回。

整个流程（全部发生在**客户端**，也就是扩展进程这一侧）：

```text
用户在 <style> 中触发补全
  → 语言客户端的 middleware 拦截补全请求
  → 判断位置在 CSS 区域中
  → 把“CSS 虚拟内容”存进 Map，构造 URI：embedded-content://css/<原文件 URI 编码>.css
  → executeCommand('vscode.executeCompletionItemProvider', 虚拟 URI, 位置)
       → VS Code 发现这是 .css 文档，调用内置 CSS 扩展的补全提供者
       → CSS 扩展读取这个虚拟文档的内容（由 embedded-content 内容提供者从 Map 中取出）
       → 返回 CSS 补全
  → 把结果作为原文件的补全结果返回
```

用到的两个机制前面都学过：

- **虚拟文档**（`registerTextDocumentContentProvider`）：见 [虚拟文档](../extension-guides/virtual-documents.md)；
- **执行内置命令**（`vscode.executeCompletionItemProvider` 让 VS Code 调用某个文档上已注册的补全提供者，返回 `CompletionList`）：见 [内置命令](../references/commands.md)。

> 通过这种方法，即使我们的代码中不包含任何理解 CSS 的库，我们也能计算出 CSS 的自动补全。随着 VS Code 更新它的 CSS 语言服务器，我们无需更新代码就能获得最新的 CSS 语言支持。
>
> 下面我们来看看示例代码。

<a id="request-forwarding-sample"></a>
### 请求转发示例（Request Forwarding sample）

> **注意**：这个示例假设你已经了解[编程式语言功能主题](./programmatic-language-features.md)和[语言服务器扩展指南](./language-server-extension-guide.md)。代码基于 [lsp-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-sample) 构建。
>
> 源代码可以在 [microsoft/vscode-extension-samples](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-embedded-request-forwarding) 找到。
>
> 维护一份文档 URI 与其虚拟文档之间的映射，并为对应的请求提供它们：

```ts
const virtualDocumentContents = new Map<string, string>()

workspace.registerTextDocumentContentProvider('embedded-content', {
  provideTextDocumentContent: uri => {
    // 去掉开头的 `/` 和结尾的 `.css`，得到原始的 URI
    const originalUri = uri.path.slice(1).slice(0, -4);
    const decodedUri = decodeURIComponent(originalUri);
    return virtualDocumentContents.get(decodedUri);
  }
})
```

URI 的拆解：对于 `embedded-content://css/<编码后的原 URI>.css`，`css` 是 authority，`uri.path` 是 `/<编码后的原 URI>.css`。`slice(1)` 去掉开头的 `/`，`slice(0, -4)` 去掉结尾的 `.css`（4 个字符），再解码，就得到 Map 的键。URI 以 `.css` 结尾，是为了让 VS Code 把这个虚拟文档识别为 CSS 语言，从而交给 CSS 扩展处理。

> 通过使用语言客户端的 `middleware` 选项，我们拦截自动补全的请求：

```ts
let clientOptions: LanguageClientOptions = {
  documentSelector: [{ scheme: 'file', language: 'html' }],
  middleware: {
    provideCompletionItem: async (document, position, context, token, next) => {
      // 如果不在 `<style>` 中，就不进行请求转发
      if (!isInsideStyleRegion(htmlLanguageService, document.getText(), document.offsetAt(position))) {
        return await next(document, position, context, token);
      }

      const originalUri = document.uri.toString(true);
      // 计算 CSS 虚拟内容（非 CSS 部分替换为空白），存入 Map
      virtualDocumentContents.set(originalUri, getCSSVirtualContent(htmlLanguageService, document.getText()));

      const vdocUriString = `embedded-content://css/${encodeURIComponent(
        originalUri
      )}.css`;
      const vdocUri = Uri.parse(vdocUriString);
      // 让 VS Code 调用 CSS 的补全提供者
      return await commands.executeCommand<CompletionList>(
        'vscode.executeCompletionItemProvider',
        vdocUri,
        position,
        context.triggerCharacter
      );
    }
  }
}
```

**`middleware`（中间件）** 是 `vscode-languageclient` 提供的拦截机制：每一种语言功能请求在发给语言服务器之前，都会先经过对应的中间件函数。调用 `next(...)` 表示“照常发给语言服务器”；不调用 `next`，自己返回结果，就是拦截。这里不在 `<style>` 中时调用 `next`，交给 HTML 语言服务器；在 `<style>` 中时自己转发给 CSS。

（`document.uri.toString(true)` 中的 `true` 是 `skipEncoding`，表示不对 URI 进行百分号编码，这样 Map 的键与内容提供者中 `decodeURIComponent` 解码后的结果一致。示例中的 `documentSelector` 写的是 `language: 'html'`，而上文说示例贡献的是 `html1` 语言，以示例仓库中的实际代码为准。）

---

<a id="potential-issues"></a>
## 潜在的问题（Potential issues）

> 在实现嵌入式语言服务器的过程中，我们遇到了许多问题。虽然我们还没有完美的解决方案，但我们想提醒你注意，因为你很可能也会遇到这些问题。

<a id="hard-to-implement-language-features"></a>
### 难以实现的语言功能（Hard to implement language features）

> 一般来说，跨越语言区域边界工作的语言功能更难实现。例如，自动补全或悬停内容很容易实现，因为你可以检测出嵌入内容的语言，并基于嵌入的内容计算出响应。但格式化或重命名这样的语言功能可能需要特殊处理。在格式化的情况下，你需要在单个文档中处理多个区域的缩进和格式化设置。对于重命名，要让它在不同文档的不同区域之间工作，可能很有挑战性。

| 功能 | 难度 | 原因 |
|---|---|---|
| 补全、悬停 | 容易 | 只涉及光标所在的一个区域 |
| 格式化 | 难 | CSS 区域格式化后的缩进，要和外层 HTML 的缩进协调 |
| 重命名 | 难 | 一个 CSS 类名可能同时出现在 `<style>` 和 `class="..."` 中，还可能跨多个文件 |

<a id="language-services-can-be-stateful-and-hard-to-embed"></a>
### 语言服务可能是有状态的，难以嵌入（Language Services can be stateful and hard to embed）

> VS Code 的 HTML 支持提供了 HTML、CSS 和 JavaScript 的语言功能。虽然 HTML 和 CSS 的语言服务是无状态的，但驱动 JavaScript 语言功能的 TypeScript 服务器是有状态的。我们在 HTML 文档中只提供基础的 JavaScript 支持，因为很难把项目的状态告知 TypeScript。例如，如果你引入了一个指向 CDN 上托管的 `lodash` 库的 `<script>` 标签，你在 `<script>` 标签中输入 `_.` 时不会得到补全。

“无状态”是指只看当前这一个文档就能给出结果（CSS 补全只需要知道这段 CSS）；“有状态”是指需要了解整个项目（JavaScript 的补全要知道引入了哪些库、有哪些全局变量、`tsconfig` 是什么）。嵌入一个有状态的语言服务，就要把这些项目状态也同步给它，这很难做好。

<a id="encoding-and-decoding"></a>
### 编码和解码（Encoding and decoding）

> 一个文档的主语言，可能和它的嵌入语言有着不同的编码或转义规则。例如，根据 [HTML 规范](https://www.w3.org/TR/html401/appendix/notes.html#h-B.3.2)，下面这个 HTML 文档是无效的：

```html
<SCRIPT type="text/javascript">
  document.write ("<EM>This won't work</EM>")
</SCRIPT>
```

> 在这种情况下，如果嵌入的 JavaScript 的语言服务器返回的结果中包含 `</`，就应该把它转义为 `<\/`。

原因：HTML 解析器看到 `<script>` 中的 `</` 时，可能会认为脚本在这里结束了（规范中，`</` 后跟字母就可能结束 `<script>` 的内容）。所以在 HTML 中写 JavaScript 时，字符串里的 `</EM>` 要写成 `<\/EM>`。嵌入的 JavaScript 语言服务对此一无所知，它给出的补全或格式化结果，需要外层的 HTML 服务器再做一次转义。

---

<a id="conclusion"></a>
## 结论（Conclusion）

> 两种方法各有优缺点。
>
> 语言服务：
>
> - \+ 对语言服务器和用户体验有完全的控制。
> - \+ 不依赖其他语言服务器。所有代码都在一个仓库中。
> - \+ 这个语言服务器可以在所有[兼容 LSP 的代码编辑器](https://microsoft.github.io/language-server-protocol/implementors/tools/)中复用。
> - \- 可能很难嵌入用其他语言编写的语言服务。
> - \- 需要持续维护，才能从语言服务依赖中获得新功能。
>
> 请求转发：
>
> - \+ 避免了嵌入不是用语言服务器的语言编写的语言服务时遇到的问题（例如，在一个 Razor 语言服务器中嵌入 C# 编译器来支持 C#）。
> - \+ 无需维护，就能从其他语言服务的上游获得新功能。
> - \- 不适用于诊断错误。VS Code API 不支持可以“拉取”（请求）诊断的诊断提供者。
> - \- 由于缺乏控制，很难与其他语言服务器共享状态。
> - \- 跨语言的功能可能很难实现（例如，当存在 `<div class="foo">` 时，为 `.foo` 提供 CSS 补全）。
>
> 总的来说，我们推荐通过嵌入语言服务来构建语言服务器，因为这种方法让你对用户体验有更多的控制，而且服务器可以在任何兼容 LSP 的编辑器中复用。不过，如果你的使用场景很简单，嵌入的内容不需要上下文或语言服务器状态就能轻松处理；或者打包 Node.js 库对你来说是个问题，那么你可以考虑请求转发的方法。

| | 语言服务 | 请求转发 |
|---|---|---|
| 实现位置 | 语言服务器（服务端） | 语言客户端的 middleware（扩展进程） |
| 嵌入语言的分析由谁做 | 你打包进来的语言服务库 | VS Code 中已安装的其他扩展 |
| 诊断（错误检查） | 支持 | 不支持（诊断是由各扩展主动推送的，没法“请求”某个虚拟文档的诊断） |
| 其他编辑器中复用 | 可以 | 不可以（依赖 VS Code 的命令和虚拟文档） |
| 维护 | 要跟进依赖库的更新 | 自动获得新功能 |
| **推荐** | **一般情况** | 场景简单，或无法打包 Node.js 库时 |

“不适用于诊断”的原因可以这样理解：补全是“问一下，得到答案”（`vscode.executeCompletionItemProvider`）；而诊断在 VS Code 稳定版 API 中只能由扩展通过 `DiagnosticCollection` 主动设置，没有一个“请对这个文档做一次检查并把结果给我”的命令，所以无法转发。

---

## 本篇小结

```text
问题：HTML 中的 CSS/JS 等嵌入语言，如何获得补全、悬停、诊断等智能功能

共同技巧：把文档按语言拆分成区域；为某种语言生成“虚拟文档”，
         其他区域的字符全部替换为空格（保留换行），位置无需换算

方法一：语言服务（推荐）
  语言服务器内置 vscode-css-languageservice 等库
  getModeAtPosition 选择语言模式 → mode.doComplete(虚拟文档, 原位置)

方法二：请求转发
  客户端 middleware.provideCompletionItem 拦截
  → 虚拟文档（registerTextDocumentContentProvider，URI 以 .css 结尾）
  → executeCommand('vscode.executeCompletionItemProvider', 虚拟 URI, 位置)
  不支持诊断，不能在其他编辑器中复用

需要注意：格式化 / 重命名跨区域很难；有状态的语言服务（TypeScript）难以嵌入；
         主语言与嵌入语言的转义规则不同（<script> 中 </ 要转义为 <\/）
```
