# 文档选择器（Document Selectors）

> 原文：[Document Selectors](https://code.visualstudio.com/api/references/document-selector)
> 源文件：`microsoft/vscode-docs` → `api/references/document-selector.md`（DateApproved: 10/7/2026）

> 扩展可以基于文档选择器，按语言、文件类型和位置来过滤它们的功能。本主题讨论文档选择器、文档 scheme，以及扩展作者需要注意的事项。

**文档选择器回答的问题是：“这个功能对哪些文档生效？”** 所有的 `vscode.languages.registerXxxProvider` 的第一个参数都是文档选择器（见 [编程式语言功能](../language-extensions/programmatic-language-features.md)），语言客户端的 `documentSelector` 选项也是（见 [语言服务器扩展指南](../language-extensions/language-server-extension-guide.md)）。

---

<a id="text-documents-not-on-disk"></a>
## 不在磁盘上的文本文档（Text documents not on disk）

> 并不是所有的文本文档都存储在磁盘上，例如新创建的文档。除非另外指定，否则一个文档选择器适用于**所有**类型的文档。使用 [DocumentFilter](https://code.visualstudio.com/api/references/vscode-api#DocumentFilter) 的 `scheme` 属性可以缩小到特定的 scheme，例如 `{ scheme: 'file', language: 'typescript' }` 表示存储在磁盘上的 TypeScript 文件。

---

<a id="document-selectors"></a>
## 文档选择器（Document selectors）

> Visual Studio Code 扩展 API 通过 [DocumentSelector](https://code.visualstudio.com/api/references/vscode-api#DocumentSelector) 类型，把智能提示（IntelliSense）这样的特定于语言的功能与文档选择器结合起来。它们是把功能限定到特定语言的一种简单机制。
>
> 下面的代码片段为 TypeScript 文件注册了一个 [HoverProvider](https://code.visualstudio.com/api/references/vscode-api#HoverProvider)，文档选择器是 `typescript` 这个语言标识符字符串。

```ts
vscode.languages.registerHoverProvider('typescript', {
  provideHover(doc: vscode.TextDocument) {
    return new vscode.Hover('For *all* TypeScript documents.');
  }
});
```

> 文档选择器不仅仅可以是一个语言标识符，更复杂的选择器可以使用一个 [DocumentFilter](https://code.visualstudio.com/api/references/vscode-api#DocumentFilter)，基于 `scheme` 和通过 `pattern` 路径 glob 模式表示的文件位置进行过滤：

```ts
vscode.languages.registerHoverProvider(
  { pattern: '**/test/**' },
  {
    provideHover(doc: vscode.TextDocument) {
      return new vscode.Hover('For documents inside `test`-folders only');
    }
  }
);
```

> 下一个代码片段使用了 `scheme` 过滤器，并把它与一个语言标识符结合起来。`untitled` scheme 用于尚未保存到磁盘的新文件。

```ts
vscode.languages.registerHoverProvider(
  { scheme: 'untitled', language: 'typescript' },
  {
    provideHover(doc: vscode.TextDocument) {
      return new vscode.Hover('For new, unsaved TypeScript documents only');
    }
  }
);
```

三个示例悬停显示的文字分别是：“针对*所有* TypeScript 文档”、“只针对 `test` 文件夹中的文档”、“只针对新建的、未保存的 TypeScript 文档”。

**`DocumentSelector` 的完整形式**（根据 `@types/vscode` 1.140.0）：

```ts
type DocumentSelector = DocumentFilter | string | ReadonlyArray<DocumentFilter | string>;
```

| 写法 | 含义 |
|---|---|
| `'typescript'` | 字符串：语言 ID，等价于 `{ language: 'typescript' }` |
| `{ language, scheme, pattern, notebookType }` | `DocumentFilter`：所有写出的属性**同时**满足才匹配（“与”） |
| `['typescript', { language: 'javascript', scheme: 'file' }]` | 数组：满足**其中任意一项**就匹配（“或”） |

`DocumentFilter` 的四个属性：

| 属性 | 匹配什么 | 例子 |
|---|---|---|
| `language` | 文档的语言 ID | `'typescript'`、`'json'` |
| `scheme` | 文档 URI 的 scheme | `'file'`（磁盘文件）、`'untitled'`（未保存的新文件） |
| `pattern` | 文档路径的 glob 模式（也可以是 `RelativePattern`，限定在某个文件夹内） | `'**/test/**'`、`'**/*.config.json'` |
| `notebookType` | 文档所在的笔记本的类型（用于笔记本中的单元格） | `'jupyter-notebook'` |

---

<a id="document-scheme"></a>
## 文档 scheme（Document scheme）

> 文档的 `scheme` 常常被忽视，但它是一条重要的信息。大多数文档都保存在磁盘上，扩展作者通常假设他们处理的是磁盘上的文件。例如，对于一个简单的 `typescript` 选择器，所做的假设是**磁盘上的 TypeScript 文件**。但是，在一些场景中，这个假设太宽松了，应该使用一个更明确的选择器，比如 `{ scheme: 'file', language: 'typescript' }`。
>
> 当功能依赖于从磁盘读取文件或向磁盘写入文件时，这一点的重要性就体现出来了。看看下面的代码片段：

```ts
// 👎 太宽松
vscode.languages.registerHoverProvider('typescript', {
  provideHover(doc: vscode.TextDocument) {
    const { size } = fs.statSync(doc.uri.fsPath); // ⚠️ 'untitled:/Untitled1.ts' 或其他情况怎么办？
    return new vscode.Hover(`Size in bytes is ${size}`);
  }
});
```

> 上面的悬停提供者想显示文档在磁盘上的大小，但它没有检查文档是否真的存储在磁盘上。例如，它可能是新创建的，还没有保存。正确的做法是告诉 VS Code，这个提供者只能处理磁盘上的文件。

```ts
// 👍 只处理磁盘上的文件
vscode.languages.registerHoverProvider(
  { scheme: 'file', language: 'typescript' },
  {
    provideHover(doc: vscode.TextDocument) {
      const { size } = fs.statSync(doc.uri.fsPath);
      return new vscode.Hover(`Size in bytes is ${size}`);
    }
  }
);
```

**会出现哪些非 `file` 的文档？**

| scheme | 什么时候出现 |
|---|---|
| `untitled` | 新建了一个文件但还没保存 |
| `git` | 在源代码管理视图中查看文件的旧版本、差异对比的左侧 |
| `vscode-remote` / `vscode-vfs` 等 | 远程开发、[虚拟工作区](../extension-guides/virtual-workspaces.md)（如 GitHub 仓库直接在浏览器中打开） |
| 扩展自定义的 scheme | [虚拟文档](../extension-guides/virtual-documents.md)（`registerTextDocumentContentProvider`） |
| `vscode-notebook-cell` | 笔记本中的单元格 |

反过来也要注意：如果你的功能**不**依赖磁盘（比如只分析 `doc.getText()`），就不要加 `scheme: 'file'`，否则它在未保存的文件、虚拟工作区中都会失效。[虚拟工作区](../extension-guides/virtual-workspaces.md#language-selectors) 一篇中对此有更多的讨论。

---

<a id="summary"></a>
## 小结（Summary）

> 文档通常存储在文件系统中，但并不总是如此：还有未命名（untitled）的文档、Git 使用的缓存文档、来自 FTP 等远程来源的文档，等等。如果你的功能依赖于磁盘访问，请确保使用带有 `file` scheme 的文档选择器。

---

<a id="next-steps"></a>
## 下一步（Next steps）

> 要进一步了解 VS Code 的扩展模型，可以试试这些主题：
>
> - [扩展清单文件](./extension-manifest.md) - VS Code package.json 扩展清单文件参考
> - [贡献点](./contribution-points.md) - VS Code 贡献点参考

---

## 本篇小结

```text
DocumentSelector = 字符串（语言 ID）| DocumentFilter | 二者的数组（数组中任意一项匹配即可）
DocumentFilter = { language?, scheme?, pattern?, notebookType? }（写出的属性同时满足才匹配）

不写 scheme = 所有类型的文档（untitled、git、虚拟文档、远程……）
依赖磁盘（fs、fsPath）→ 必须加 scheme: 'file'
只分析文本内容 → 不要限制 scheme，让功能在更多场景中可用
```
