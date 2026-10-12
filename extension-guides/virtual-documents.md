# 虚拟文档（Virtual Documents）

> 原文：[Virtual Documents](https://code.visualstudio.com/api/extension-guides/virtual-documents)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/virtual-documents.md`（DateApproved: 10/7/2026）

> 文本文档内容提供者（text document content provider）API 让你可以在 VS Code 中，用任意来源的内容创建只读文档。示例扩展的源代码在：[https://github.com/microsoft/vscode-extension-samples/blob/main/virtual-document-sample/README.md](https://github.com/microsoft/vscode-extension-samples/blob/main/virtual-document-sample/README.md)。

**虚拟文档是什么？** 它是一种**在编辑器中打开、但不对应磁盘上任何文件**的文档。内容由你的扩展在运行时生成，可以来自网络请求、命令输出、计算结果……打开后，它和普通文件一样显示在编辑器中，有语法高亮、可以搜索、可以复制，只是不能编辑。

常见的例子：

- Git 扩展中“查看某个文件在上一次提交时的内容”，打开的就是虚拟文档；
- 查看反编译结果、接口返回的 JSON、日志；
- 在 [Webview 指南](./webview.md) 中提到过：只是想显示一段只读文本时，用虚拟文档比用 Webview 轻量得多。

---

<a id="TextDocumentContentProvider"></a>
## TextDocumentContentProvider

> 这个 API 的工作方式是：认领一个 URI 协议（scheme），然后由你的提供者为这个协议的 URI 返回文本内容。协议必须在注册提供者时指定，之后不能更改。同一个提供者可以用于多个协议，一个协议也可以注册多个提供者。

**URI 协议（scheme）**是 URI 中冒号前面的部分。普通文件的 URI 是 `file:///C:/a.txt`，协议是 `file`；Git 扩展用的是 `git:`。你的扩展可以起一个自己的协议名，比如下面示例中的 `cowsay`：

```text
cowsay:Hello World
└─┬──┘ └────┬────┘
 协议       路径（path）
```

当 VS Code 要打开一个 `cowsay:` 开头的 URI 时，就会去问你注册的提供者：“这个 URI 的内容是什么？”

```ts
vscode.workspace.registerTextDocumentContentProvider(myScheme, myProvider);
```

> 调用 `registerTextDocumentContentProvider` 会返回一个 Disposable，可以用它撤销注册。提供者只需要实现 `provideTextDocumentContent` 函数，这个函数会接收一个 uri 和一个取消令牌（cancellation token）作为参数。

```ts
const myProvider = new class implements vscode.TextDocumentContentProvider {
  provideTextDocumentContent(uri: vscode.Uri): string {
    // 调用 cowsay，把 uri 的 path 作为文字
    return cowsay.say({ text: uri.path });
  }
};
```

`cowsay` 是一个 npm 包，可以生成“一头牛说话”的字符画（见下文截图）。示例中把 URI 的路径部分当作牛要说的话。

`provideTextDocumentContent` 可以返回字符串，也可以返回 Promise（内容需要异步获取时，比如发网络请求）。**取消令牌**（`CancellationToken`）用来告诉你“这个请求已经不需要了”（比如用户在内容生成好之前就关掉了文档），这时可以提前结束耗时的操作。VS Code 中很多 Provider 方法的最后一个参数都是它。

> 注意，提供者并不负责为虚拟文档创建 uri，它的职责是根据给定的 uri **提供**内容。作为交换，内容提供者被接入了打开文档的逻辑中，所以始终会考虑这些提供者。

也就是说，**谁想打开虚拟文档，谁负责构造 URI**（通常是你自己的命令），提供者只负责“给 URI，还内容”。

> 这个示例用一个 `cowsay` 命令构造一个 uri，然后让编辑器显示它：

```ts
vscode.commands.registerCommand('cowsay.say', async () => {
  let what = await vscode.window.showInputBox({ placeHolder: 'cow say?' });
  if (what) {
    let uri = vscode.Uri.parse('cowsay:' + what);
    let doc = await vscode.workspace.openTextDocument(uri); // 这里会回调提供者
    await vscode.window.showTextDocument(doc, { preview: false });
  }
});
```

> 这个命令会提示用户输入，创建一个 `cowsay` 协议的 uri，为这个 uri 打开一个文档，最后为这个文档打开一个编辑器。在第 3 步（打开文档）时，提供者会被要求为这个 uri 提供内容。

完整的流程：

```text
1. showInputBox            用户输入 "Hello"
2. Uri.parse               构造 URI：cowsay:Hello
3. openTextDocument(uri)   VS Code 发现协议是 cowsay → 调用你的 provideTextDocumentContent(uri)
                           → 得到文本，创建一个只读的 TextDocument
4. showTextDocument        在编辑器中显示这个文档
```

`openTextDocument` 和 `showTextDocument` 的区别：前者只是在内存中**加载**文档，不显示；后者才是在编辑器中**打开**它。`{ preview: false }` 表示不以“预览模式”打开（预览模式的标签页标题是斜体，打开另一个文件时会被替换掉）。

> 这样，我们就有了一个功能完整的文本文档内容提供者。下面几节介绍虚拟文档如何更新，以及如何为虚拟文档注册界面命令。

<a id="update-virtual-documents"></a>
### 更新虚拟文档（Update Virtual Documents）

> 根据使用场景的不同，虚拟文档的内容可能会变化。为了支持这一点，提供者可以实现一个 `onDidChange` 事件。
>
> `vscode.Event` 类型定义了 VS Code 中事件的约定。实现事件最简单的方式是使用 `vscode.EventEmitter`，像这样：

```ts
const myProvider = new class implements vscode.TextDocumentContentProvider {
  // 事件发射器和它的事件
  onDidChangeEmitter = new vscode.EventEmitter<vscode.Uri>();
  onDidChange = this.onDidChangeEmitter.event;

  //...
};
```

> 事件发射器有一个 `fire` 方法，可以用来在文档发生变化时通知 VS Code。发生变化的文档通过传给 `fire` 方法的 uri 来标识。如果文档仍处于打开状态，VS Code 会再次调用提供者，获取更新后的内容。

这和 [树视图](./tree-view.md#updating-tree-view-content) 中刷新数据的写法完全一样：`EventEmitter` 留在内部用来 `fire()`，`.event` 公开给 VS Code 订阅。例如每隔几秒刷新一次文档内容：

```ts
setInterval(() => {
  myProvider.onDidChangeEmitter.fire(vscode.Uri.parse('cowsay:Hello'));
}, 5000);
```

> 这就是让 VS Code 监听虚拟文档变化所需的全部内容。要查看使用这个功能的更复杂的示例，请看：[https://github.com/microsoft/vscode-extension-samples/blob/main/contentprovider-sample/README.md](https://github.com/microsoft/vscode-extension-samples/blob/main/contentprovider-sample/README.md)。

<a id="add-editor-commands"></a>
### 添加编辑器命令（Add Editor Commands）

> 可以添加只与关联的内容提供者所提供的文档交互的编辑器操作。下面是一个示例命令，把牛刚才说的话倒过来：

```ts
// 注册一个更新当前 cowsay 的命令
subscriptions.push(
  vscode.commands.registerCommand('cowsay.backwards', async () => {
    if (!vscode.window.activeTextEditor) {
      return; // 没有编辑器
    }
    let { document } = vscode.window.activeTextEditor;
    if (document.uri.scheme !== myScheme) {
      return; // 不是我的协议
    }
    // 获取 path 部分，把它反转，再创建一个新的 uri
    let say = document.uri.path;
    let newSay = say
      .split('')
      .reverse()
      .join('');
    let newUri = document.uri.with({ path: newSay });
    await vscode.window.showTextDocument(newUri, { preview: false });
  })
);
```

> 上面的代码片段会检查是否有活动的编辑器，以及它的文档是否属于我们的协议。之所以需要这些检查，是因为命令对所有人都是可见的（也可以被执行）。然后，把 uri 的 path 部分反转，用它创建一个新的 uri，最后打开一个编辑器。

- `subscriptions` 指的是 `context.subscriptions`，原文省略了前缀。
- `document.uri.with({ path: newSay })`：`Uri` 对象是不可修改的，`with` 方法会返回一个**新的** URI，只替换指定的部分（这里替换了 path，协议保持 `cowsay` 不变）。
- `showTextDocument` 也可以直接接收一个 URI，内部会先帮你 `openTextDocument`。

> 要通过编辑器命令来完善这个功能，还需要在 `package.json` 中添加一部分声明。在 `contributes` 部分中添加以下配置：

```json
"menus": {
  "editor/title": [
    {
      "command": "cowsay.backwards",
      "group": "navigation",
      "when": "resourceScheme == cowsay"
    }
  ]
}
```

> 这里引用了在 `contributes/commands` 部分中定义的 `cowsay.backwards` 命令，并指定它应该显示在编辑器标题菜单中（右上角的工具栏）。光是这样的话，这个命令会在每一个编辑器中都显示。这就是 `when` 子句的作用：它描述了显示这个操作必须满足的条件。在这个示例中，它要求编辑器中文档的协议必须是 `cowsay`。然后，对 `commandPalette` 菜单重复同样的配置，因为命令面板默认会显示所有命令。

![cowsay 文档的编辑器标题栏上显示了反转按钮](images/virtual-documents/cowsay-bwd.png)

截图中，编辑器里显示的是一头牛的字符画；右上角黄线标出的就是 `cowsay.backwards` 命令的按钮（命令设置了 `icon` 时显示为图标，否则显示为文字）。只有打开 `cowsay:` 文档时，这个按钮才会出现。

原文说“对 `commandPalette` 菜单重复同样的配置”，但没有给出代码，完整写法是：

```json
"menus": {
  "editor/title": [
    { "command": "cowsay.backwards", "group": "navigation", "when": "resourceScheme == cowsay" }
  ],
  "commandPalette": [
    { "command": "cowsay.backwards", "when": "resourceScheme == cowsay" }
  ]
}
```

`resourceScheme` 是内置的上下文键，表示当前资源 URI 的协议。（`menus` 和 `when` 子句的用法见 [命令指南](./command.md)。）

<a id="events-and-visibility"></a>
### 事件与可见性（Events and Visibility）

> 文档提供者是 VS Code 中的“一等公民”，它们的内容出现在普通的文本文档中，与文件使用相同的基础设施，等等。不过，这也意味着“你的”文档无法隐藏起来：它们会出现在 `onDidOpenTextDocument` 和 `onDidCloseTextDocument` 事件中，是 `vscode.workspace.textDocuments` 的一部分，诸如此类。所有人都要遵守的规则是：先检查文档的 `scheme`，再决定要不要对这个文档做些什么。

这条规则对**所有扩展**都适用，不只是提供虚拟文档的扩展。例如，你写了一个“文件打开时自动格式化”的扩展，监听了 `onDidOpenTextDocument`。如果不检查 `scheme`，用户打开一个 Git 历史版本（虚拟文档）时，你的扩展也会尝试去格式化它，而虚拟文档是只读的，就会出错。

```ts
vscode.workspace.onDidOpenTextDocument(doc => {
  if (doc.uri.scheme !== 'file') {
    return;   // 只处理磁盘上的真实文件
  }
  // ……
});
```

常见的 scheme：

| scheme | 是什么 |
|---|---|
| `file` | 本地磁盘上的文件 |
| `untitled` | 新建的、还没保存过的文件 |
| `git` | Git 扩展提供的历史版本 |
| `vscode-remote` | 远程开发时远端机器上的文件 |
| `output` | 输出面板的内容 |
| 你自己定义的（如 `cowsay`） | 你的虚拟文档 |

---

<a id="file-system-api"></a>
## 文件系统 API（File System API）

> 如果你需要更大的灵活性和能力，可以看看 [`FileSystemProvider`](https://code.visualstudio.com/api/references/vscode-api#FileSystemProvider) API。它让你可以实现一个完整的文件系统，包括文件、文件夹、二进制数据、删除和创建文件等等。
>
> 示例扩展的源代码在：[https://github.com/microsoft/vscode-extension-samples/tree/main/fsprovider-sample/README.md](https://github.com/microsoft/vscode-extension-samples/tree/main/fsprovider-sample/README.md)。
>
> 当 VS Code 打开这样一个文件系统上的文件夹或工作区时，我们称之为**虚拟工作区**。在 VS Code 窗口中打开虚拟工作区时，左下角的远程指示器上会显示一个标签，与远程窗口类似。扩展如何支持这种情况，请参阅[虚拟工作区指南](./virtual-workspaces.md)。

两种 API 的对比：

| | `TextDocumentContentProvider` | `FileSystemProvider` |
|---|---|---|
| 提供什么 | 单个只读文本文档的内容 | 一个完整的文件系统 |
| 能否编辑、保存 | 不能，只读 | 能（读写、创建、删除、重命名……） |
| 能否有文件夹 | 不能 | 能，可以在资源管理器中浏览 |
| 二进制数据 | 不支持，只有文本 | 支持 |
| 实现难度 | 一个方法 | 需要实现 `stat`、`readDirectory`、`readFile`、`writeFile`、`delete`、`rename` 等一系列方法 |
| 典型用途 | 只读的预览、生成的内容 | 把远程存储（FTP、云盘、数据库）当作本地文件夹来编辑 |

只需要显示一段内容时，用 `TextDocumentContentProvider` 就足够了；需要让用户像操作本地文件一样浏览、编辑时，才用 `FileSystemProvider`。

---

## 本篇小结

```text
虚拟文档 = 自定义协议的 URI + 内容提供者（只读）

registerTextDocumentContentProvider('cowsay', provider)
  provider.provideTextDocumentContent(uri) → 返回文本（可以异步）
  provider.onDidChange → EventEmitter.fire(uri) 通知内容更新

打开：自己构造 URI → openTextDocument（加载，会调用提供者）→ showTextDocument（显示）

给虚拟文档加按钮：menus.editor/title + "when": "resourceScheme == cowsay"
                 （命令面板也要加同样的 when）

所有扩展的通用规则：处理文档事件前，先检查 document.uri.scheme

需要读写、文件夹、二进制 → FileSystemProvider（虚拟工作区）
```
