# 自定义编辑器 API（Custom Editor API）

> 原文：[Custom Editor API](https://code.visualstudio.com/api/extension-guides/custom-editors)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/custom-editors.md`（DateApproved: 10/7/2026）

> 自定义编辑器让扩展可以创建完全可定制的读写编辑器，针对特定类型的资源，代替 VS Code 标准的文本编辑器。它的用途非常广泛，例如：
>
> - 直接在 VS Code 中预览着色器、3D 模型等资源。
> - 为 Markdown 或 XAML 等语言创建所见即所得（WYSIWYG）的编辑器。
> - 为 CSV、JSON、XML 等数据文件提供另一种可视化的呈现方式。
> - 为二进制文件或文本文件构建完全可定制的编辑体验。

举几个熟悉的例子：在 VS Code 中打开一张图片，看到的不是一堆乱码，而是图片本身，这就是内置的图片预览自定义编辑器；有些扩展能把 `.csv` 文件显示成表格、把 `.drawio` 文件显示成可编辑的流程图，用的也是自定义编辑器。

> 本文档概述了自定义编辑器 API，以及实现自定义编辑器的基础知识。我们会介绍两种类型的自定义编辑器，它们有什么区别，以及哪一种适合你的使用场景。然后，针对每种类型，我们会讲解构建一个行为良好的自定义编辑器的基础知识。
>
> 虽然自定义编辑器是一个强大的新扩展点，但实现一个基本的自定义编辑器其实并不难！不过，如果你正在开发自己的第一个 VS Code 扩展，可能需要等到更熟悉 VS Code API 的基础知识后，再深入学习自定义编辑器。自定义编辑器建立在很多 VS Code 概念之上，比如 [Webview](./webview.md) 和文本文档，同时学习所有这些新概念可能会有点吃力。
>
> 但如果你觉得已经准备好了，并且正在构思要做的各种酷炫的自定义编辑器，那我们就开始吧！一定要下载[自定义编辑器扩展示例][sample]，这样你可以边看文档边对照，了解自定义编辑器 API 是如何组合在一起的。

**前置知识：** 本篇大量依赖 [Webview](./webview.md) 的内容（HTML 内容、消息传递、CSP、`retainContextWhenHidden`），建议先读完那一篇。

---

<a id="links"></a>
## 链接（Links）

> - [自定义编辑器示例][sample]

<a id="vs-code-api-usage"></a>
### 用到的 VS Code API（VS Code API Usage）

> - [`window.registerCustomEditorProvider`](https://code.visualstudio.com/api/references/vscode-api#window.registerCustomEditorProvider)
> - [`CustomTextEditorProvider`](https://code.visualstudio.com/api/references/vscode-api#CustomTextEditorProvider)

---

<a id="custom-editor-api-basics"></a>
## 自定义编辑器 API 基础（Custom Editor API basics）

> 自定义编辑器是针对特定资源、代替 VS Code 标准文本编辑器显示的另一种视图。自定义编辑器由两部分组成：用户与之交互的**视图**，以及扩展用来与底层资源交互的**文档模型**。
>
> 自定义编辑器的视图部分是用 [Webview](./webview.md) 实现的。这让你可以用标准的 HTML、CSS 和 JavaScript 构建自定义编辑器的用户界面。Webview 不能直接访问 VS Code API，但可以通过来回传递消息与扩展通信。关于 Webview 以及使用 Webview 的最佳实践，请查阅 [Webview 文档](./webview.md)。
>
> 自定义编辑器的另一部分是文档模型。扩展通过这个模型理解它正在处理的资源（文件）。`CustomTextEditorProvider` 使用 VS Code 标准的 [TextDocument](https://code.visualstudio.com/api/references/vscode-api#TextDocument) 作为文档模型，对文件的所有修改都用 VS Code 标准的文本编辑 API 来表达。而 `CustomReadonlyEditorProvider` 和 `CustomEditorProvider` 则让你提供自己的文档模型，因此它们可以用于非文本的文件格式。

**“视图”和“模型”分离**，是理解自定义编辑器的关键：

```text
            文件（磁盘上的 .cscratch）
                     │
              ┌──────┴──────┐
              │  文档模型    │  ← 一个文件只有一份（TextDocument 或你自己的 CustomDocument）
              └──────┬──────┘
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Webview 1  Webview 2  ……       ← 视图：可以有多个（比如分屏时）
```

- **模型**是数据本身：文件现在的内容是什么，有没有被修改过；
- **视图**是数据的呈现：在界面上显示成什么样子。

> 每个资源只有一个文档模型，但这个文档可以有多个编辑器实例（视图）。例如，假设你打开了一个使用 `CustomTextEditorProvider` 的文件，然后运行 **View: Split editor** 命令。这时仍然只有一个 `TextDocument`，因为工作区中这个资源仍然只有一份，但现在这个资源有两个 Webview 了。

<a id="customeditor-vs-customtexteditor"></a>
### `CustomEditor` 与 `CustomTextEditor`（`CustomEditor` vs `CustomTextEditor`）

> 自定义编辑器分为两类：自定义文本编辑器和自定义编辑器。两者的主要区别在于如何定义文档模型。
>
> `CustomTextEditorProvider` 使用 VS Code 标准的 [`TextDocument`](https://code.visualstudio.com/api/references/vscode-api#TextDocument) 作为数据模型。任何基于文本的文件类型都可以使用 `CustomTextEditor`。`CustomTextEditor` 的实现要容易得多，因为 VS Code 已经知道如何处理文本文件，因此可以自己实现保存、为热退出备份文件等操作。
>
> 而使用 `CustomEditorProvider` 时，扩展要自带文档模型。这意味着你可以把 `CustomEditor` 用于图片等二进制格式，但这也意味着扩展要负责更多的事情，包括实现保存和备份。如果你的自定义编辑器是只读的（例如用于预览的自定义编辑器），就可以跳过其中大部分的复杂工作。
>
> 在决定使用哪种类型的自定义编辑器时，选择通常很简单：如果处理的是基于文本的文件格式，就用 `CustomTextEditorProvider`；如果是二进制文件格式，就用 `CustomEditorProvider`。

**热退出（hot exit）**是指：关闭 VS Code 时，即使有未保存的修改，VS Code 也不会弹窗询问，而是把修改备份起来，下次打开时原样恢复。

三种 Provider 的对比：

| Provider | 文档模型 | 适合的文件 | 能否编辑 | 保存、撤销、备份由谁实现 | 难度 |
|---|---|---|---|---|---|
| `CustomTextEditorProvider` | VS Code 的 `TextDocument` | 文本文件（JSON、CSV、XML……） | 能 | **VS Code** | 低 |
| `CustomReadonlyEditorProvider` | 你自己的 `CustomDocument` | 任意文件（常用于二进制） | 不能（只读预览） | 不需要 | 中 |
| `CustomEditorProvider` | 你自己的 `CustomDocument` | 任意文件（常用于二进制） | 能 | **你自己** | 高 |

<a id="contribution-point"></a>
### 贡献点（Contribution point）

> `customEditors` [贡献点](../references/contribution-points.md)是扩展告诉 VS Code 它提供了哪些自定义编辑器的方式。例如，VS Code 需要知道你的自定义编辑器处理哪些类型的文件，以及如何在界面中标识你的自定义编辑器。
>
> 下面是[自定义编辑器扩展示例][sample]中一个基本的 `customEditor` 贡献：

```json
"contributes": {
  "customEditors": [
    {
      "viewType": "catEdit.catScratch",
      "displayName": "Cat Scratch",
      "selector": [
        {
          "filenamePattern": "*.cscratch"
        }
      ],
      "priority": "default"
    }
  ]
}
```

> `customEditors` 是一个数组，所以扩展可以贡献多个自定义编辑器。我们来分解一下自定义编辑器条目本身：

| 字段 | 必填 | 说明 |
|---|---|---|
| `viewType` | 是 | 自定义编辑器的唯一标识符 |
| `displayName` | 是 | 在界面中标识这个自定义编辑器的名称 |
| `selector` | 是 | 指定这个自定义编辑器对哪些文件生效 |
| `priority` | 否 | 指定什么时候使用这个自定义编辑器 |

> - `viewType`：自定义编辑器的唯一标识符。
>
>     VS Code 通过它把 `package.json` 中的自定义编辑器贡献与代码中的自定义编辑器实现联系起来。它在所有扩展中都必须是唯一的，所以不要用 `"preview"` 这样通用的 `viewType`，一定要用你的扩展独有的名称，例如 `"viewType": "myAmazingExtension.svgPreview"`。
>
> - `displayName`：在 VS Code 界面中标识自定义编辑器的名称。
>
>     显示名称会出现在 VS Code 的界面中，例如 **View: Reopen with** 下拉列表。
>
> - `selector`：指定自定义编辑器对哪些文件生效。
>
>     `selector` 是由一个或多个 [glob 模式](https://code.visualstudio.com/docs/editor/glob-patterns)组成的数组。这些 glob 模式会与文件名进行匹配，以确定自定义编辑器能否用于这些文件。`*.png` 这样的 `filenamePattern` 会让自定义编辑器对所有 PNG 文件生效。
>
>     你还可以创建更具体的模式，匹配文件名或目录名，例如 `**/translations/*.json`。
>
> - `priority`（可选）：指定什么时候使用自定义编辑器。
>
>     `priority` 控制打开资源时什么时候使用自定义编辑器。可能的值有：
>
>     - `"default"`：对所有与自定义编辑器的 `selector` 匹配的文件，都尝试使用这个自定义编辑器。如果一个文件有多个自定义编辑器，用户需要选择想用哪一个。
>     - `"option"`：默认不使用这个自定义编辑器，但允许用户切换到它，或者把它配置为默认编辑器。

**glob 模式**是一种用通配符匹配文件路径的写法：`*` 匹配文件名中的任意字符，`**` 匹配任意层级的目录。例如 `**/translations/*.json` 匹配任意位置下 `translations` 目录中的 JSON 文件。

**`priority` 怎么选？** 想清楚“用户打开这类文件时，最常想看到的是什么”：

| 选择 | 适合 | 例子 |
|---|---|---|
| `"default"` | 文件本来就不适合用文本方式查看 | 图片、自定义的二进制格式 |
| `"option"` | 文本方式仍然是主要的编辑方式，自定义编辑器只是一种补充视图 | `*.json` 的表格视图（大多数时候用户还是想直接编辑 JSON 文本） |

注意：给 `*.json`、`*.md` 这类常见文件设置 `"default"`，会让用户每次打开这类文件都进入你的编辑器，非常打扰人。

用户可以在编辑器标签页上右键选择 **Reopen Editor With...**，或者在命令面板中执行 **View: Reopen Editor With...**，在文本编辑器和各个自定义编辑器之间切换；也可以通过 `workbench.editorAssociations` 设置，指定某类文件默认用哪个编辑器打开。

<a id="custom-editor-activation"></a>
### 自定义编辑器的激活（Custom editor activation）

> 当用户打开你的某个自定义编辑器时，VS Code 会触发 `onCustomEditor:VIEW_TYPE` 激活事件。在激活期间，你的扩展必须调用 `registerCustomEditorProvider`，用预期的 `viewType` 注册一个自定义编辑器。
>
> 需要注意的是，只有当 VS Code 需要创建自定义编辑器的实例时，才会触发 `onCustomEditor`。如果 VS Code 只是向用户显示一些关于可用自定义编辑器的信息（例如在 **View: Reopen with** 命令中），你的扩展不会被激活。

1.74 之后的版本中，这个激活事件会根据 `contributes.customEditors` 自动生成，不用手写。

注册的写法（`viewType` 必须和 `package.json` 中的一致）：

```ts
export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.window.registerCustomEditorProvider(
      'catEdit.catScratch',
      new CatScratchEditorProvider(context),
      {
        // 可选：传给 Webview 面板的选项
        webviewOptions: { retainContextWhenHidden: false },
        // 可选：是否允许同一个文档同时打开多个编辑器（见后文）
        supportsMultipleEditorsPerDocument: false,
      }
    )
  );
}
```

---

<a id="custom-text-editor"></a>
## 自定义文本编辑器（Custom Text Editor）

> 自定义文本编辑器让你可以为文本文件创建自定义编辑器。文本文件可以是任何东西，从无结构的纯文本，到 [CSV](https://en.wikipedia.org/wiki/Comma-separated_values)、JSON 或 XML。自定义文本编辑器使用 VS Code 标准的 [TextDocument](https://code.visualstudio.com/api/references/vscode-api#TextDocument) 作为文档模型。
>
> [自定义编辑器扩展示例][sample]中包含一个简单的自定义文本编辑器示例，用于“猫抓板”文件（其实就是以 `.cscratch` 为扩展名的 JSON 文件）。我们来看看实现自定义文本编辑器的几个重要部分。

<a id="custom-text-editor-lifecycle"></a>
### 自定义文本编辑器的生命周期（Custom Text Editor lifecycle）

> VS Code 同时管理自定义文本编辑器的视图部分（Webview）和模型部分（`TextDocument`）的生命周期。当需要创建一个新的自定义编辑器实例时，VS Code 会调用你的扩展；当用户关闭标签页时，VS Code 会清理编辑器实例和文档模型。
>
> 为了理解这一切在实践中是如何运作的，我们从扩展的角度，看看用户打开一个自定义文本编辑器、以及关闭它时，分别会发生什么。

**打开自定义文本编辑器**

> 以[自定义编辑器扩展示例][sample]为例，用户第一次打开 `.cscratch` 文件时，会发生以下事情：
>
> 1. VS Code 触发 `onCustomEditor:catCustoms.catScratch` 激活事件。
>
>     如果扩展还没有被激活，这会激活它。在激活期间，扩展必须调用 `registerCustomEditorProvider`，确保为 `catCustoms.catScratch` 注册了一个 `CustomTextEditorProvider`。
>
> 2. 然后，VS Code 调用为 `catCustoms.catScratch` 注册的 `CustomTextEditorProvider` 上的 `resolveCustomTextEditor` 方法。
>
>     这个方法接收正在打开的资源的 `TextDocument`，以及一个 `WebviewPanel`。扩展必须为这个 Webview 面板填充初始的 HTML 内容。

（注意：原文这里用的 viewType 是 `catCustoms.catScratch`，而上面贡献点示例中写的是 `catEdit.catScratch`。两处应该一致，以你在 `package.json` 中声明的为准。官方示例仓库中的版本可能和文档不同。）

> `resolveCustomTextEditor` 返回后，我们的自定义编辑器就会显示给用户。Webview 里画什么，完全由我们的扩展决定。
>
> 每次打开自定义编辑器时，都会走同样的流程，即使是拆分（split）一个自定义编辑器时也一样。每个自定义编辑器实例都有自己的 `WebviewPanel`，但如果多个自定义文本编辑器打开的是同一个资源，它们会共享同一个 `TextDocument`。记住：把 `TextDocument` 看作资源的模型，而 Webview 面板是这个模型的视图。

和 Webview 指南中的区别：普通 Webview 面板是你调用 `createWebviewPanel` 创建的；在自定义编辑器中，**面板由 VS Code 创建好后交给你**，你只需要填充内容、设置消息监听。

**关闭自定义文本编辑器**

> 当用户关闭一个自定义文本编辑器时，VS Code 会在 `WebviewPanel` 上触发 `WebviewPanel.onDidDispose` 事件。这时，扩展应该清理与这个编辑器相关的所有资源（事件订阅、文件监听器等）。
>
> 当某个资源的最后一个自定义编辑器被关闭时，如果没有其他编辑器在使用这个资源的 `TextDocument`，也没有其他扩展持有它，这个 `TextDocument` 也会被释放。可以检查 `TextDocument.isClosed` 属性，判断 `TextDocument` 是否已经关闭。`TextDocument` 关闭后，再用自定义编辑器打开同一个资源，会打开一个新的 `TextDocument`。

<a id="synchronizing-changes-with-the-textdocument"></a>
### 与 TextDocument 同步修改（Synchronizing changes with the TextDocument）

> 由于自定义文本编辑器使用 `TextDocument` 作为文档模型，所以它们要负责两件事：在自定义编辑器中发生编辑时更新 `TextDocument`，以及在 `TextDocument` 发生变化时更新自己。

这是实现自定义文本编辑器的核心，数据要在两个方向上同步：

```text
         ① Webview 中的操作（点按钮、拖动……）
Webview ─────── postMessage ───────→ 扩展 ──── WorkspaceEdit ────→ TextDocument
   ▲                                                                   │
   │                                                                   │
   └──── postMessage（新内容） ←─── 扩展 ←── onDidChangeTextDocument ──┘
         ② TextDocument 的任何变化（撤销、重做、其他编辑器修改……）
```

**从 Webview 到 `TextDocument`**

> 自定义文本编辑器中的编辑可以有很多种形式：点击按钮、修改文字、拖动某些条目。只要用户在自定义文本编辑器中编辑了文件本身，扩展就必须更新 `TextDocument`。下面是猫抓板扩展的实现方式：
>
> 1. 用户点击 Webview 中的 **Add scratch** 按钮。这会从 Webview [发送一条消息](./webview.md#scripts-and-message-passing)回扩展。
> 2. 扩展收到消息。然后更新它对文档的内部模型（在猫抓板示例中，就是往 JSON 中添加一个新条目）。
> 3. 扩展创建一个 `WorkspaceEdit`，把更新后的 JSON 写入文档。这个编辑通过 `vscode.workspace.applyEdit` 应用。
>
> 尽量让工作区编辑只包含更新文档所需的最小改动。另外请记住，如果处理的是 JSON 这样的语言，扩展应该尽量遵循用户已有的格式习惯（空格还是 Tab、缩进的大小等）。

**为什么要通过 `WorkspaceEdit` 修改，而不是直接写文件？** 因为通过 `WorkspaceEdit` 修改 `TextDocument`，VS Code 会自动帮你处理：文件标记为“未保存”、撤销 / 重做、保存、热退出备份。这正是 `CustomTextEditor` 比 `CustomEditor` 简单的原因。

为什么要“最小改动”？如果每次都把整个文件替换掉，撤销记录会很难看，而且如果用户同时在文本编辑器里打开了这个文件，光标位置也会被打乱。

**从 `TextDocument` 到 Webview**

> 当 `TextDocument` 发生变化时，扩展也需要确保它的 Webview 反映出文档的新状态。`TextDocument` 可能因为以下原因发生变化：用户的操作，例如撤销、重做或还原文件；其他扩展使用 `WorkspaceEdit` 修改了它；或者用户在 VS Code 默认的文本编辑器中打开了这个文件并进行修改。下面是猫抓板扩展的实现方式：
>
> 1. 在扩展中，订阅 `vscode.workspace.onDidChangeTextDocument` 事件。`TextDocument` 的每一次变化都会触发这个事件（包括我们的自定义编辑器自己做出的修改！）。
> 2. 当某个我们打开了编辑器的文档发生变化时，就向 Webview 发送一条包含文档新状态的消息。Webview 随后更新自己，渲染更新后的文档。
>
> 一定要记住，自定义编辑器触发的任何文件编辑，都会导致 `onDidChangeTextDocument` 被触发。请确保你的扩展不会陷入更新循环：用户在 Webview 中做了编辑，触发了 `onDidChangeTextDocument`，导致 Webview 更新，Webview 又触发扩展进行另一次更新，再次触发 `onDidChangeTextDocument`，如此往复。
>
> 还要记住，如果处理的是 JSON 或 XML 这样的结构化语言，文档不一定总是处于有效状态。你的扩展必须能够妥善处理错误，或者向用户显示错误信息，让他们了解出了什么问题、该如何修复。
>
> 最后，如果更新 Webview 的开销很大，可以考虑对 Webview 的更新进行[防抖（debouncing）](https://davidwalsh.name/javascript-debounce-function)。

**避免更新循环的关键：** Webview 收到新内容时，只负责**重新渲染**，不要再把内容发回给扩展。只有用户的真实操作才发送编辑消息。这样循环就断开了：

```text
用户操作 → 编辑消息 → applyEdit → onDidChangeTextDocument → 发新内容给 Webview → Webview 只渲染，到此结束
```

**防抖**是指：短时间内连续发生多次变化时，只在最后一次变化后等一小段时间再处理一次。例如用户连续输入 10 个字符，不必把 Webview 刷新 10 次。

**最小可运行的示例（补充）：** 下面把上述流程写成一个完整的 `CustomTextEditorProvider`，API 以 `@types/vscode` 1.140 为准。它把文件内容原样显示在 Webview 中，并提供一个按钮在末尾追加一行：

```ts
import * as vscode from 'vscode';

export class CatScratchEditorProvider implements vscode.CustomTextEditorProvider {

  constructor(private readonly context: vscode.ExtensionContext) {}

  // VS Code 每打开一个编辑器实例就调用一次
  public resolveCustomTextEditor(
    document: vscode.TextDocument,
    webviewPanel: vscode.WebviewPanel,
    _token: vscode.CancellationToken
  ): void {
    webviewPanel.webview.options = { enableScripts: true };
    webviewPanel.webview.html = this.getHtml(webviewPanel.webview);

    // 把文档的当前内容发给 Webview
    const updateWebview = () => {
      webviewPanel.webview.postMessage({ type: 'update', text: document.getText() });
    };

    // 方向 ②：文档变化 → 更新 Webview（只处理自己这个文档）
    const changeSubscription = vscode.workspace.onDidChangeTextDocument(e => {
      if (e.document.uri.toString() === document.uri.toString()) {
        updateWebview();
      }
    });

    // 编辑器关闭时，取消订阅
    webviewPanel.onDidDispose(() => changeSubscription.dispose());

    // 方向 ①：Webview 中的操作 → 修改文档
    webviewPanel.webview.onDidReceiveMessage(message => {
      if (message.type === 'append') {
        const edit = new vscode.WorkspaceEdit();
        const end = document.lineAt(document.lineCount - 1).range.end;
        edit.insert(document.uri, end, '\n' + message.text);  // 最小改动：只在末尾插入
        vscode.workspace.applyEdit(edit);
      }
    });

    updateWebview();
  }

  private getHtml(webview: vscode.Webview): string {
    const scriptUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this.context.extensionUri, 'media', 'catScratch.js')
    );
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src ${webview.cspSource};">
</head>
<body>
  <button id="add">Add scratch</button>
  <pre id="content"></pre>
  <script src="${scriptUri}"></script>
</body>
</html>`;
  }
}
```

```js
// media/catScratch.js（Webview 中运行）
const vscode = acquireVsCodeApi();

document.getElementById('add').addEventListener('click', () => {
  vscode.postMessage({ type: 'append', text: 'meow' });   // 只发送用户操作
});

window.addEventListener('message', event => {
  if (event.data.type === 'update') {
    // 只渲染，不回发消息，避免更新循环
    document.getElementById('content').textContent = event.data.text;
  }
});
```

用默认的文本编辑器和这个自定义编辑器并排打开同一个文件，在任意一边修改，另一边都会同步更新；按 `Ctrl+Z` 撤销也能正常工作，这些都是 `TextDocument` 帮你完成的。

---

<a id="custom-editor"></a>
## 自定义编辑器（Custom Editor）

> `CustomEditorProvider` 和 `CustomReadonlyEditorProvider` 让你可以为二进制文件格式创建自定义编辑器。这个 API 让你完全掌控文件如何显示给用户、如何对它进行编辑，还能让扩展接入 `save`（保存）和其他文件操作。再次强调，如果你要为基于文本的文件格式构建编辑器，强烈建议改用 [`CustomTextEditor`](#custom-text-editor)，它的实现要简单得多。
>
> [自定义编辑器扩展示例][sample]中包含一个简单的自定义二进制编辑器示例，用于“爪印画”文件（其实就是以 `.pawdraw` 为扩展名的 jpeg 文件）。我们来看看为二进制文件构建自定义编辑器需要做些什么。

<a id="CustomDocument"></a>
### CustomDocument

> 使用自定义编辑器时，扩展要负责通过 `CustomDocument` 接口实现自己的文档模型。这让扩展可以在 `CustomDocument` 上自由存储与自定义编辑器交互所需的任何数据，但这也意味着扩展必须实现基本的文档操作，比如保存、为热退出备份文件数据。
>
> 每个打开的文件对应一个 `CustomDocument`。用户可以为同一个资源打开多个编辑器（比如拆分当前的自定义编辑器），但所有这些编辑器都由同一个 `CustomDocument` 支撑。

`CustomDocument` 接口本身非常简单，只要求两个成员：

```ts
interface CustomDocument {
  readonly uri: Uri;   // 文档对应的文件
  dispose(): void;     // 所有编辑器都关闭后，VS Code 调用它来释放资源
}
```

其他数据（比如图片的像素数据、修改记录）都由你自己在实现类上添加：

```ts
class PawDrawDocument implements vscode.CustomDocument {
  constructor(
    public readonly uri: vscode.Uri,
    private documentData: Uint8Array,   // 自己添加的：文件的二进制内容
  ) {}

  dispose(): void {
    // 释放资源
  }
}
```

<a id="custom-editor-lifecycle"></a>
### 自定义编辑器的生命周期（Custom Editor lifecycle）

**supportsMultipleEditorsPerDocument**

> 默认情况下，VS Code 只允许每个自定义文档有一个编辑器。这个限制让正确实现自定义编辑器变得更容易，因为你不用担心多个自定义编辑器实例之间的同步问题。
>
> 不过，如果你的扩展能够支持，我们建议在注册自定义编辑器时设置 `supportsMultipleEditorsPerDocument: true`，这样同一个文档就可以打开多个编辑器实例。这会让你的自定义编辑器的行为更像 VS Code 普通的文本编辑器。

这个选项就是前面注册代码中 `registerCustomEditorProvider` 的第三个参数里的那一项。设置为 `true` 后，你要保证：一个编辑器中的修改，能同步显示到同一文档的其他所有编辑器中。

**打开自定义编辑器（Opening Custom Editors）**

> 当用户打开一个与 `customEditor` 贡献点匹配的文件时，VS Code 会触发 `onCustomEditor` [激活事件](../references/activation-events.md)，然后调用为对应 viewType 注册的提供者。`CustomEditorProvider` 有两个职责：为自定义编辑器提供文档，然后提供编辑器本身。下面按顺序列出了[自定义编辑器扩展示例][sample]中 `catCustoms.pawDraw` 编辑器打开时发生的事情：
>
> 1. VS Code 触发 `onCustomEditor:catCustoms.pawDraw` 激活事件。
>
>     如果扩展还没有被激活，这会激活它。我们还必须确保扩展在激活期间为 `catCustoms.pawDraw` 注册了一个 `CustomReadonlyEditorProvider` 或 `CustomEditorProvider`。
>
> 2. VS Code 调用为 `catCustoms.pawDraw` 编辑器注册的 `CustomReadonlyEditorProvider` 或 `CustomEditorProvider` 上的 `openCustomDocument`。
>
>     这里扩展会得到一个资源 uri，必须为这个资源返回一个新的 `CustomDocument`。这时扩展应该为这个资源创建内部的文档模型。这可能包括从磁盘读取并解析资源的初始状态，或者初始化新的 `CustomDocument`。
>
>     扩展可以创建一个实现了 `CustomDocument` 的新类来定义这个模型。记住，这个初始化阶段完全由扩展决定；VS Code 并不关心扩展在 `CustomDocument` 上存储了哪些额外的信息。
>
> 3. VS Code 用第 2 步得到的 `CustomDocument` 和一个新的 `WebviewPanel` 调用 `resolveCustomEditor`。
>
>     这里扩展必须为自定义编辑器填充初始的 html。如果需要，我们还可以保存这个 `WebviewPanel` 的引用，以便之后使用，例如在命令中引用它。
>
> `resolveCustomEditor` 返回后，自定义编辑器就会显示给用户。
>
> 如果用户在另一个编辑器组中用我们的自定义编辑器打开了同一个资源（例如拆分第一个编辑器），扩展的工作就简单多了。这种情况下，VS Code 只会用第一个编辑器打开时创建的那个 `CustomDocument` 调用 `resolveCustomEditor`。

与自定义文本编辑器相比，多了一个 `openCustomDocument` 步骤，因为文档模型要由你来创建：

```text
                自定义文本编辑器                      自定义编辑器
打开第 1 个  →  resolveCustomTextEditor(文档, 面板)   openCustomDocument(uri) → 创建 CustomDocument
                （TextDocument 由 VS Code 提供）      resolveCustomEditor(文档, 面板)
打开第 2 个  →  resolveCustomTextEditor(同一文档, 新面板)  resolveCustomEditor(同一文档, 新面板)
（分屏）                                             （不会再调用 openCustomDocument）
```

**关闭自定义编辑器（Closing Custom Editors）**

> 假设我们为同一个资源打开了两个自定义编辑器实例。当用户关闭这些编辑器时，VS Code 会通知扩展，以便它清理与编辑器相关的资源。
>
> 当第一个编辑器实例被关闭时，VS Code 会在被关闭的编辑器的 `WebviewPanel` 上触发 `WebviewPanel.onDidDispose` 事件。这时，扩展必须清理与这个特定编辑器实例相关的所有资源。
>
> 当第二个编辑器被关闭时，VS Code 再次触发 `WebviewPanel.onDidDispose`。不过，这时与这个 `CustomDocument` 相关的所有编辑器也都关闭了。当一个 `CustomDocument` 不再有任何编辑器时，VS Code 会调用它的 `CustomDocument.dispose`。扩展对 `dispose` 的实现必须清理与这个文档相关的所有资源。
>
> 如果用户随后又用我们的自定义编辑器重新打开了同一个资源，就会用一个新的 `CustomDocument` 重新走一遍完整的 `openCustomDocument`、`resolveCustomEditor` 流程。

| 事件 | 清理什么 |
|---|---|
| `WebviewPanel.onDidDispose` | 这一个编辑器实例的资源（这个面板的消息监听等） |
| `CustomDocument.dispose()` | 整个文档的资源（文档数据、文件监听等） |

<a id="readonly-custom-editors"></a>
### 只读的自定义编辑器（Readonly Custom editors）

> 下面的很多小节只适用于支持编辑的自定义编辑器。虽然听起来有点矛盾，但很多自定义编辑器根本不需要编辑功能。比如图片预览，或者内存转储（memory dump）的可视化呈现。两者都可以用自定义编辑器实现，但都不需要可编辑。这时就该用 `CustomReadonlyEditorProvider` 了。
>
> `CustomReadonlyEditorProvider` 让你可以创建不支持编辑的自定义编辑器。它们仍然可以是可交互的，但不支持撤销、保存之类的操作。与完全可编辑的自定义编辑器相比，实现只读的自定义编辑器也要简单得多。

“可交互”是指可以缩放、拖动、切换显示方式等，只是不会修改文件内容。`CustomReadonlyEditorProvider` 只需要实现两个方法：

| 方法 | 作用 |
|---|---|
| `openCustomDocument(uri, openContext, token)` | 为文件创建 `CustomDocument` |
| `resolveCustomEditor(document, webviewPanel, token)` | 为编辑器填充 Webview 内容 |

<a id="editable-custom-editor-basics"></a>
### 可编辑自定义编辑器的基础（Editable Custom Editor Basics）

> 可编辑的自定义编辑器让你可以接入 VS Code 的标准操作，比如撤销和重做、保存以及热退出。这让可编辑的自定义编辑器非常强大，但也意味着正确实现它要比实现一个可编辑的自定义文本编辑器或只读的自定义编辑器复杂得多。
>
> 可编辑的自定义编辑器由 `CustomEditorProvider` 实现。这个接口继承自 `CustomReadonlyEditorProvider`，所以你既要实现 `openCustomDocument` 和 `resolveCustomEditor` 这样的基本操作，还要实现一组编辑专用的操作。我们来看看 `CustomEditorProvider` 中与编辑相关的部分。

原文没有一次性列出全部方法，这里先汇总一下 `CustomEditorProvider` 需要实现的所有成员（以 `@types/vscode` 1.140 为准）：

| 成员 | 作用 | 何时被调用 |
|---|---|---|
| `openCustomDocument` | 创建文档模型 | 打开文件时 |
| `resolveCustomEditor` | 填充编辑器内容 | 每打开一个编辑器实例时 |
| `onDidChangeCustomDocument` | **由你触发**：通知 VS Code 文档被编辑了 | 用户在编辑器中做了修改时 |
| `saveCustomDocument(document, token)` | 把文档保存到原文件 | 用户保存时 |
| `saveCustomDocumentAs(document, destination, token)` | 把文档保存到另一个位置 | 用户“另存为”时 |
| `revertCustomDocument(document, token)` | 丢弃修改，恢复到磁盘上的状态 | 用户执行“还原文件”时 |
| `backupCustomDocument(document, context, token)` | 把未保存的修改备份起来，返回一个 `CustomDocumentBackup` | 热退出、自动备份时 |

`openCustomDocument` 的第二个参数 `openContext` 中有一个 `backupId`：如果不是 `undefined`，说明 VS Code 正在从之前的备份中恢复文档，这时应该从备份中读取数据，而不是从原文件读取。

**编辑（Edits）**

> 对可编辑的自定义文档所做的修改，都通过“编辑”来表达。一次编辑可以是任何东西：一次文本修改、一次图片旋转、一次列表重排。VS Code 完全不关心一次编辑具体做了什么，交给你的扩展决定，但 VS Code 需要知道什么时候发生了编辑。VS Code 正是通过编辑来把文档标记为“已修改”（dirty）的，而这又进一步启用了自动保存和备份。
>
> 每当用户在你的自定义编辑器的任意一个 Webview 中做出编辑时，扩展都必须从它的 `CustomEditorProvider` 触发 `onDidChangeCustomDocument` 事件。根据你的自定义编辑器的实现，`onDidChangeCustomDocument` 事件可以触发两种事件类型：`CustomDocumentContentChangeEvent` 和 `CustomDocumentEditEvent`。

“已修改（dirty）”就是标签页上文件名旁边的那个白色圆点，表示有未保存的修改。

**CustomDocumentContentChangeEvent**

> `CustomDocumentContentChangeEvent` 是一种最简单的编辑。它唯一的作用是告诉 VS Code 文档被编辑了。
>
> 当扩展从 `onDidChangeCustomDocument` 触发一个 `CustomDocumentContentChangeEvent` 时，VS Code 会把对应的文档标记为已修改。此后，文档要变回未修改状态，唯一的办法是用户保存或还原它。使用 `CustomDocumentContentChangeEvent` 的自定义编辑器不支持撤销 / 重做。

**CustomDocumentEditEvent**

> `CustomDocumentEditEvent` 是一种更复杂的编辑，它支持撤销 / 重做。你应该始终尝试用 `CustomDocumentEditEvent` 来实现自定义编辑器，只有在无法实现撤销 / 重做时，才退而使用 `CustomDocumentContentChangeEvent`。
>
> `CustomDocumentEditEvent` 有以下字段：
>
> - `document`：这次编辑所针对的 `CustomDocument`。
> - `label`：可选的文字，描述做了哪种类型的编辑（例如 "Crop"、"Insert" 等）。
> - `undo`：需要撤销这次编辑时，VS Code 调用的函数。
> - `redo`：需要重做这次编辑时，VS Code 调用的函数。
>
> 当扩展从 `onDidChangeCustomDocument` 触发一个 `CustomDocumentEditEvent` 时，VS Code 会把对应的文档标记为已修改。要让文档不再处于已修改状态，用户可以保存或还原文档，或者撤销 / 重做回到文档上次保存时的状态。
>
> VS Code 会在某次特定的编辑需要被撤销或重新应用时，调用这次编辑的 `undo` 和 `redo` 方法。VS Code 维护着一个内部的编辑栈，所以如果扩展用三次编辑触发了 `onDidChangeCustomDocument`，我们把它们叫作 `a`、`b`、`c`：

```ts
onDidChangeCustomDocument(a);
onDidChangeCustomDocument(b);
onDidChangeCustomDocument(c);
```

> 下面这一系列用户操作会产生这些调用：

```text
undo — c.undo()
undo — b.undo()
redo — b.redo()
redo — c.redo()
redo — 无操作，没有更多编辑了
```

> 要实现撤销 / 重做，扩展必须更新与之关联的自定义文档的内部状态，同时更新这个文档所有关联的 Webview，让它们反映文档的新状态。请记住，一个资源可能有多个 Webview。它们必须始终显示相同的文档数据。例如，一个图片编辑器的多个实例必须始终显示相同的像素数据，但可以允许每个编辑器实例有自己的缩放级别和界面状态。

两种事件的对比：

| | `CustomDocumentContentChangeEvent` | `CustomDocumentEditEvent` |
|---|---|---|
| 字段 | 只有 `document` | `document`、`label`、`undo`、`redo` |
| 标记为已修改 | 是 | 是 |
| 支持撤销 / 重做 | 否 | 是 |
| 撤销到保存时的状态后 | 仍然是“已修改” | 自动变回“未修改” |
| 推荐 | 实在无法实现撤销时才用 | 首选 |

**写法示意（补充）：** 代码示意中的 `onDidChangeCustomDocument(a)` 是简写。实际代码中，是用一个 `EventEmitter` 来触发的，和 [树视图](./tree-view.md) 中刷新数据的写法相同：

```ts
class PawDrawEditorProvider implements vscode.CustomEditorProvider<PawDrawDocument> {

  private readonly _onDidChangeCustomDocument =
    new vscode.EventEmitter<vscode.CustomDocumentEditEvent<PawDrawDocument>>();
  public readonly onDidChangeCustomDocument = this._onDidChangeCustomDocument.event;

  // 用户在 Webview 中画了一笔时调用
  private onUserStroke(document: PawDrawDocument, stroke: Stroke) {
    document.addStroke(stroke);                 // 更新文档模型
    this._onDidChangeCustomDocument.fire({
      document,
      label: 'Stroke',
      undo: () => document.removeLastStroke(),  // 撤销：模型中去掉这一笔，并通知所有 Webview 重绘
      redo: () => document.addStroke(stroke),   // 重做：重新加上这一笔，并通知所有 Webview 重绘
    });
  }

  // ……openCustomDocument、resolveCustomEditor、save 等方法省略
}
```

其中 `Stroke`、`addStroke` 等是示意用的自定义类型和方法，需要你根据自己的文档结构来实现。

<a id="saving"></a>
<a id="saving"></a>
### 保存（Saving）

> 当用户保存一个自定义编辑器时，扩展要负责把资源的当前状态写入磁盘。具体怎么做，很大程度上取决于扩展的 `CustomDocument` 类型，以及扩展在内部是如何跟踪编辑的。
>
> 保存的第一步是获取要写入磁盘的数据流。常见的做法有：
>
> - 跟踪资源的状态，以便能快速地把它序列化。
>
>     例如，一个基础的图片编辑器可以维护一个像素数据的缓冲区。
>
> - 重放自上次保存以来的编辑，生成新文件。
>
>     例如，一个更高效的图片编辑器可以跟踪自上次保存以来的编辑，比如 `crop`（裁剪）、`rotate`（旋转）、`scale`（缩放）。保存时，再把这些编辑应用到文件上次保存的状态上，生成新文件。
>
> - 向自定义编辑器的 `WebviewPanel` 请求要保存的文件数据。
>
>     不过请记住，即使自定义编辑器不可见，它也可以被保存。因此，建议扩展的 `save` 实现不要依赖 `WebviewPanel`。如果做不到这一点，可以使用 `WebviewPanelOptions.retainContextWhenHidden` 设置，让 Webview 即使被隐藏也保持存活。`retainContextWhenHidden` 确实有很大的内存开销，所以要谨慎使用。

三种做法的取舍：

| 做法 | 优点 | 缺点 |
|---|---|---|
| 扩展维护完整的数据 | 保存简单、可靠，不依赖界面 | 数据量大时占用内存 |
| 记录编辑操作，保存时重放 | 内存占用小 | 实现复杂 |
| 保存时向 Webview 要数据 | 实现简单 | Webview 隐藏时页面已销毁，拿不到数据；要配合开销很大的 `retainContextWhenHidden` |

为什么第三种有问题：在 [Webview 指南](./webview.md#persistence) 中讲过，Webview 被切到后台时，页面就被销毁了。而“全部保存”、自动保存都可能发生在编辑器不可见的时候。

> 拿到资源的数据之后，一般应该使用 [工作区文件系统 API](https://code.visualstudio.com/api/references/vscode-api#FileSystem) 把它写入磁盘。文件系统 API 接收一个 `UInt8Array` 数据，既可以写二进制文件，也可以写文本文件。对于二进制文件数据，只需把二进制数据放进 `UInt8Array`。对于文本文件数据，用 `Buffer` 把字符串转换成 `UInt8Array`：

```ts
const writeData = Buffer.from("my text data", 'utf8');
vscode.workspace.fs.writeFile(fileUri, writeData);
```

`vscode.workspace.fs.writeFile` 返回的是 Promise，实际代码中应该 `await` 它，确保写完后保存操作才算完成。用 `vscode.workspace.fs` 而不是 Node.js 的 `fs`，扩展在远程开发、虚拟文件系统等环境中也能正常工作（见 [虚拟工作区](./virtual-workspaces.md)）。另外，在 [Web 扩展](./web-extensions.md) 中没有 `Buffer`，可以改用 `new TextEncoder().encode('my text data')`。

---

<a id="next-steps"></a>
## 下一步（Next steps）

> 如果你想进一步了解 VS Code 的扩展能力，可以看看这些主题：
>
> - [扩展 API](../index.md)：了解完整的 VS Code 扩展 API。
> - [扩展能力](../extension-capabilities/overview.md)：看看扩展 VS Code 的其他方式。

[sample]: https://github.com/microsoft/vscode-extension-samples/tree/main/custom-editor-sample

---

## 本篇小结

```text
自定义编辑器 = 视图（Webview，可以有多个） + 文档模型（每个文件一份）

选哪种 Provider
  ├─ 文本文件 → CustomTextEditorProvider（模型是 TextDocument，保存 / 撤销 / 备份都由 VS Code 负责）
  ├─ 二进制，只看不改 → CustomReadonlyEditorProvider（openCustomDocument + resolveCustomEditor）
  └─ 二进制，要编辑 → CustomEditorProvider（还要实现 save / saveAs / revert / backup）

package.json：customEditors（viewType 全局唯一、displayName、selector 的 glob、priority：default / option）

自定义文本编辑器的双向同步
  Webview 操作 → postMessage → WorkspaceEdit（最小改动）→ applyEdit
  onDidChangeTextDocument → postMessage 新内容 → Webview 只渲染（不回发，避免循环）

可编辑自定义编辑器
  编辑 → 触发 onDidChangeCustomDocument
     ├─ CustomDocumentEditEvent（带 undo / redo，首选）
     └─ CustomDocumentContentChangeEvent（只标记已修改，无撤销）
  保存不要依赖 Webview（隐藏时页面已销毁）；写文件用 workspace.fs
```
