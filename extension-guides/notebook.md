# 笔记本 API（Notebook API）

> 原文：[Notebook API](https://code.visualstudio.com/api/extension-guides/notebook)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/notebook.md`（DateApproved: 10/7/2026）

> 笔记本 API 让 VS Code 扩展可以把文件作为笔记本打开、执行笔记本中的代码单元格，并以各种丰富的、可交互的格式渲染笔记本的输出。你可能知道 Jupyter Notebook 或 Google Colab 这类流行的笔记本界面，笔记本 API 让你可以在 VS Code 中提供类似的体验。

**笔记本是什么？** 它是一种把**说明文字、代码和运行结果**交织在一起的文档。文档由一个个“单元格”组成：有的单元格写说明（Markdown），有的写代码；代码单元格可以单独运行，结果直接显示在它下方。数据分析、教学、写技术笔记时很常用。VS Code 打开 `.ipynb` 文件看到的界面，就是用这套 API 实现的。

---

<a id="parts-of-a-notebook"></a>
## 笔记本的组成部分（Parts of a Notebook）

> 笔记本由一系列单元格及其输出组成。笔记本的单元格可以是 **Markdown 单元格**，也可以是**代码单元格**，它们都由 VS Code 核心负责渲染。输出可以是各种格式。有些输出格式，比如纯文本、JSON、图片和 HTML，由 VS Code 核心渲染；另一些格式，比如特定于应用的数据或交互式小程序，则由扩展渲染。
>
> 笔记本中的单元格由 `NotebookSerializer` 读取和写入文件系统。它负责从文件系统读取数据并转换成单元格的描述，也负责把对笔记本的修改持久化回文件系统。笔记本的**代码单元格**可以由 `NotebookController` 执行，它读取单元格的内容，据此生成零个或多个输出，格式多种多样，从纯文本到格式化的文档，再到交互式小程序。特定于应用的输出格式和交互式小程序输出，由 `NotebookRenderer` 渲染。
>
> 图示如下：

![笔记本的三个组成部分：NotebookSerializer、NotebookController 和 NotebookRenderer，以及它们之间如何交互](images/notebook/architecture-overview.png)

图中，左边的文件和中间的笔记本之间通过 **NotebookSerializer**（序列化器）双向转换；中间是笔记本的单元格（Markdown 单元格和代码单元格）；代码单元格由 **NotebookController**（控制器）执行，产生的简单输出（文本、JSON、图片、HTML）由 VS Code 直接显示，高级输出（交互式小程序、特定于应用的可视化）还需要 **NotebookRenderer**（渲染器）来显示。

三个组成部分的分工：

| 组成部分 | 职责 | 类比 | 必须实现吗 |
|---|---|---|---|
| `NotebookSerializer`（序列化器） | 文件 ⇄ 单元格：打开时把文件内容解析成单元格，保存时把单元格写回文件 | 文件格式的“翻译官” | 是（否则打不开文件） |
| `NotebookController`（控制器，也叫内核 kernel） | 执行代码单元格，生成输出 | Jupyter 中的“内核” | 需要运行代码时才要 |
| `NotebookRenderer`（渲染器） | 把特定格式的输出显示出来 | 输出的“显示器” | 输出格式 VS Code 不认识时才要 |

这三者可以由同一个扩展提供，也可以分别由不同的扩展提供。比如 Jupyter 扩展提供 `.ipynb` 的序列化器和 Python 内核，另一个扩展可以为同一种笔记本提供一个新的内核，还有一个扩展专门提供某种图表的渲染器。

---

<a id="serializer"></a>
## 序列化器（Serializer）

> [NotebookSerializer API 参考](https://github.com/microsoft/vscode/blob/e1a8566a298dcced016d8e16db95c33c270274b4/src/vs/vscode.d.ts#L11865-L11884)
>
> `NotebookSerializer` 负责读取笔记本序列化后的字节，把它们反序列化成 `NotebookData`，其中包含 Markdown 单元格和代码单元格的列表。它也负责相反方向的转换：读取 `NotebookData`，把数据转换成序列化的字节以便保存。

**序列化 / 反序列化**的意思：

```text
                deserializeNotebook（反序列化，打开文件时）
文件的字节  ────────────────────────────────────────→  NotebookData（单元格列表）
（Uint8Array）←────────────────────────────────────────
                serializeNotebook（序列化，保存文件时）
```

> 示例：
>
> - [JSON 笔记本序列化器](https://github.com/microsoft/notebook-extension-samples/tree/main/notebook-serializer)：一个简单的示例笔记本，接收 JSON 输入，并在一个自定义的 `NotebookRenderer` 中输出格式化后的 JSON。
> - [Markdown 序列化器](https://github.com/microsoft/vscode-markdown-notebook)：把 Markdown 文件作为笔记本打开和编辑。

<a id="example"></a>
### 示例（Example）

> 在这个示例中，我们构建一个简化的笔记本提供者扩展，用来查看 [Jupyter Notebook 格式](https://nbformat.readthedocs.io/en/latest/format_description.html)的文件，文件扩展名为 `.notebook`（而不是传统的 `.ipynb`）。
>
> 笔记本序列化器在 `package.json` 的 `contributes.notebooks` 部分中声明，如下所示：

```json
{
    ...
    "contributes": {
        ...
        "notebooks": [
            {
                "type": "my-notebook",
                "displayName": "My Notebook",
                "selector": [
                    {
                        "filenamePattern": "*.notebook"
                    }
                ]
            }
        ]
    }
}
```

| 字段 | 说明 |
|---|---|
| `type` | 笔记本类型 ID。注册序列化器、创建控制器时都要用到它 |
| `displayName` | 在界面中显示的名称 |
| `selector` | 哪些文件用这种笔记本打开，写法和 [自定义编辑器](./custom-editors.md#contribution-point) 的 `selector` 一样 |

> 然后在扩展的激活事件中注册笔记本序列化器：

```ts
import { TextDecoder, TextEncoder } from "util";
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(
        vscode.workspace.registerNotebookSerializer(
            "my-notebook", new SampleSerializer()
        )
    );
}

// 文件中的原始数据格式
interface RawNotebook {
	cells: RawNotebookCell[];
}

interface RawNotebookCell {
    source: string[];
    cell_type: 'code' | 'markdown';
}

class SampleSerializer implements vscode.NotebookSerializer {
    // 打开文件时：字节 → NotebookData
    async deserializeNotebook(content: Uint8Array, _token: vscode.CancellationToken): Promise<vscode.NotebookData> {
        var contents = new TextDecoder().decode(content);

        let raw: RawNotebookCell[];
        try {
            raw = (<RawNotebook>JSON.parse(contents)).cells;
        } catch {
            raw = [];
        }

        const cells = raw.map(item => new vscode.NotebookCellData(
			item.cell_type === 'code' ? vscode.NotebookCellKind.Code : vscode.NotebookCellKind.Markup,
            item.source.join('\n'),
			item.cell_type === 'code' ? 'python' : 'markdown'
        ));

        return new vscode.NotebookData(cells);
    }

    // 保存文件时：NotebookData → 字节
    async serializeNotebook(data: vscode.NotebookData, _token: vscode.CancellationToken): Promise<Uint8Array> {
        let contents: RawNotebookCell[] = [];

        for (const cell of data.cells) {
            contents.push({
                cell_type: cell.kind === vscode.NotebookCellKind.Code ? 'code' : 'markdown',
                source: cell.value.split(/\r?\n/g)
            });
        }

        return new TextEncoder().encode(JSON.stringify(contents));
    }
}
```

`new vscode.NotebookCellData(类型, 内容, 语言)` 的三个参数：

| 参数 | 示例中的值 | 说明 |
|---|---|---|
| `kind` | `NotebookCellKind.Code` 或 `NotebookCellKind.Markup` | 代码单元格还是 Markdown 单元格 |
| `value` | 单元格的源代码 | Jupyter 格式中 `source` 是按行拆开的数组，所以要 `join('\n')` |
| `languageId` | `'python'` 或 `'markdown'` | 单元格的语言，决定语法高亮 |

**原文示例代码中的一个 bug：** `deserializeNotebook` 读取的格式是 `{ "cells": [...] }`（一个带 `cells` 字段的对象），而 `serializeNotebook` 写入的却是 `[...]`（一个数组）。保存之后再打开，`JSON.parse(contents).cells` 会得到 `undefined`，后面的 `raw.map` 就会抛出错误（它在 `try` 外面）。修正方法是写入时保持同样的结构：

```ts
return new TextEncoder().encode(JSON.stringify({ cells: contents }));
```

另外，`import { TextDecoder, TextEncoder } from "util"` 是 Node.js 的写法。现在的 Node.js 和浏览器中 `TextDecoder` / `TextEncoder` 都是全局可用的，可以不导入；如果要让扩展同时支持 [Web 扩展](./web-extensions.md)，就不能从 Node.js 的 `util` 模块导入。

> 现在试着运行你的扩展，打开一个以 `.notebook` 为扩展名保存的 Jupyter Notebook 格式的文件：

![笔记本显示了 Jupyter Notebook 格式文件的内容](images/notebook/ipynb-simple-provider.png)

> 你应该能打开 Jupyter 格式的笔记本，以纯文本和渲染后的 Markdown 两种形式查看它们的单元格，还能编辑这些单元格。不过，输出不会被保存到磁盘上；要保存输出，还需要对 `NotebookData` 中单元格的输出进行序列化和反序列化。
>
> 要运行单元格，你需要实现一个 `NotebookController`。

---

<a id="controller"></a>
## 控制器（Controller）

> [NotebookController API 参考](https://github.com/microsoft/vscode/blob/e1a8566a298dcced016d8e16db95c33c270274b4/src/vs/vscode.d.ts#L11941)
>
> `NotebookController` 负责读取一个**代码单元格**，执行其中的代码，生成一些输出（或者不生成输出）。
>
> 在创建控制器时，通过设置 `NotebookController#notebookType` 属性，把控制器直接与一个笔记本序列化器以及一种笔记本类型关联起来。然后，在扩展激活时把控制器添加到扩展的 subscriptions 中，就完成了控制器的全局注册。

```ts
export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(new Controller());
}

class Controller {
    readonly controllerId = 'my-notebook-controller-id'
    readonly notebookType = 'my-notebook';
    readonly label = 'My Notebook';
    readonly supportedLanguages = ['python'];

    private readonly _controller: vscode.NotebookController;
    private _executionOrder = 0;

    constructor() {
        this._controller = vscode.notebooks.createNotebookController(this.controllerId, this.notebookType, this.label);

        this._controller.supportedLanguages = this.supportedLanguages;
        this._controller.supportsExecutionOrder = true;
        this._controller.executeHandler = this._execute.bind(this);
    }

    // 用户运行单元格时调用（可能一次运行多个单元格）
    private _execute(cells: vscode.NotebookCell[], _notebook: vscode.NotebookDocument, _controller: vscode.NotebookController): void {
        for (let cell of cells) {
            this._doExecution(cell);
        }
    }

    private async _doExecution(cell: vscode.NotebookCell): Promise<void> {
        const execution = this._controller.createNotebookCellExecution(cell);
        execution.executionOrder = ++this._executionOrder;
        execution.start(Date.now()); // 记录执行单元格所花的时间

        /* 在这里执行代码；示例中没有实现 */

        execution.replaceOutput([new vscode.NotebookCellOutput([vscode.NotebookCellOutputItem.text('Dummy output text!')])])
        execution.end(true, Date.now());
    }
}
```

**`createNotebookController` 的三个参数：**

| 参数 | 示例中的值 | 说明 |
|---|---|---|
| `id` | `'my-notebook-controller-id'` | 控制器的唯一 ID |
| `notebookType` | `'my-notebook'` | 适用于哪种笔记本，必须和 `contributes.notebooks` 中的 `type` 一致 |
| `label` | `'My Notebook'` | 在笔记本右上角“选择内核”中显示的名称 |

**执行一个单元格的完整过程：**

```text
1. createNotebookCellExecution(cell)   为这个单元格创建一次“执行”
2. executionOrder = n                  单元格左侧显示的执行序号 [n]
3. start(开始时间)                     单元格显示为“正在运行”，开始计时
4. ……执行代码……
5. replaceOutput([...])                设置单元格的输出（appendOutput 是追加）
6. end(是否成功, 结束时间)              结束执行：true 显示 ✓，false 显示 ✗；显示耗时
```

几点说明：

- `supportsExecutionOrder = true`：在单元格左侧显示执行序号，就像 Jupyter 中的 `[1]`、`[2]`，用来表示单元格的运行顺序。
- `this._execute.bind(this)`：`executeHandler` 是作为普通函数被调用的，`bind(this)` 保证 `_execute` 中的 `this` 仍然指向 `Controller` 实例。写成箭头函数 `(cells, nb, ctrl) => this._execute(cells, nb, ctrl)` 效果相同。
- 示例中的 `Controller` 类能被 `push` 进 `context.subscriptions`，是因为 subscriptions 要求的是“带有 `dispose()` 方法的对象”。示例省略了这个方法，实际代码中应该加上，在里面调用 `this._controller.dispose()`。
- 如果要支持用户中断运行（点击停止按钮），还可以设置 `interruptHandler`。

> 如果你把提供 `NotebookController` 的扩展与它的序列化器分开发布，就要在它的 `package.json` 的 `keywords` 中添加一个类似 `notebookKernel<ViewTypeUpperCamelCased>` 的条目。例如，如果你为 `github-issues` 笔记本类型发布了一个替代的内核，就应该给扩展添加关键字 `notebookKernelGithubIssues`。这样，在 VS Code 中打开 `<ViewTypeUpperCamelCased>` 类型的笔记本时，可以提高这个扩展被发现的概率。

`<ViewTypeUpperCamelCased>` 是指把笔记本类型名转换成“大驼峰”形式：`github-issues` → `GithubIssues`。

```json
"keywords": ["notebookKernelGithubIssues"]
```

用户打开这种笔记本、点击“选择内核”时，VS Code 会根据这个关键字在扩展市场中推荐你的扩展。

> 示例：
>
> - [GitHub Issues 笔记本](https://github.com/microsoft/vscode-github-issue-notebooks/blob/93359d842cd01dfaef0a78b620c5a3b4cf5c2e38/src/extension/notebookProvider.ts#L29)：执行 GitHub Issues 查询的控制器
> - [REST Book](https://github.com/tanhakabir/rest-book/blob/main/src/extension/notebookKernel.ts)：运行 REST 请求的控制器。
> - [Regexper 笔记本](https://github.com/jrieken/vscode-regex-notebook/blob/master/src/extension/extension.ts#L56)：把正则表达式可视化的控制器。

---

<a id="output-types"></a>
## 输出类型（Output types）

> 输出必须是以下三种格式之一：文本输出、错误输出或富输出（Rich Output）。一个内核可以为单元格的一次执行提供多个输出，这时它们会以列表的形式显示。
>
> 简单的格式，比如文本输出、错误输出，或者富输出的“简单”变体（HTML、Markdown、JSON 等），由 VS Code 核心渲染；而特定于应用的富输出类型，则由 [NotebookRenderer](#notebook-renderer) 渲染。扩展也可以选择自己渲染“简单”的富输出，例如为 Markdown 输出添加 LaTeX 支持。

![上述各种输出类型的示意图](images/notebook/kernel.png)

图中，控制器产生的四类输出分别流向不同的地方：文本输出、错误输出、“简单”的富输出（`text/html`、`image/png`、`application/json`）交给 **VS Code 核心**渲染成简单输出；“高级”的富输出（如 `application/my-data`、`text/latex`）交给**扩展的 NotebookRenderer** 渲染成高级输出。“简单”富输出旁的虚线箭头表示：扩展也可以选择接管这些格式的渲染。

<a id="text-output"></a>
### 文本输出（Text Output）

> 文本输出是最简单的输出格式，用法和你可能熟悉的很多 REPL 类似。它只包含一个 `text` 字段，在单元格的输出元素中渲染为纯文本：

```ts
vscode.NotebookCellOutputItem.text('This is the output...')
```

![带有简单文本输出的单元格](images/notebook/text-output.png)

**REPL**（Read-Eval-Print Loop，读取—求值—输出循环）是指交互式的命令行环境，比如在终端中输入 `node` 或 `python` 后进入的界面：输入一行代码，立即显示结果。

<a id="error-output"></a>
### 错误输出（Error Output）

> 错误输出有助于以一致、易于理解的方式显示运行时错误。它支持标准的 `Error` 对象。

```ts
try {
    /* 一些代码 */
} catch (error) {
    vscode.NotebookCellOutputItem.error(error)
}
```

![带有错误输出的单元格：显示错误名称和消息，以及洋红色文字的堆栈跟踪](images/notebook/error-output.png)

这段代码只是演示如何创建错误输出项，实际使用时要把它放进 `NotebookCellOutput` 中并调用 `replaceOutput`，执行结束时一般调用 `execution.end(false, ...)` 表示失败：

```ts
catch (error) {
  execution.replaceOutput([
    new vscode.NotebookCellOutput([vscode.NotebookCellOutputItem.error(error as Error)])
  ]);
  execution.end(false, Date.now());
}
```

TypeScript 中 `catch` 到的 `error` 类型是 `unknown`，所以要写 `as Error`。

另外，`NotebookCellOutputItem` 还提供了 `stdout(文本)` 和 `stderr(文本)` 两个方法，分别表示程序的标准输出和标准错误输出。

<a id="rich-output"></a>
### 富输出（Rich Output）

> 富输出是显示单元格输出的最高级形式。它允许为输出数据提供多种不同的表示形式，并以 MIME 类型作为键。例如，如果一个单元格的输出表示一个 GitHub Issue，内核可能会生成一个富输出，其 `data` 字段上有多个属性：
>
> - 一个 `text/html` 字段，包含 issue 的格式化视图。
> - 一个 `text/x-json` 字段，包含机器可读的视图。
> - 一个 `application/github-issue` 字段，`NotebookRenderer` 可以用它创建一个完全可交互的 issue 视图。
>
> 在这种情况下，`text/html` 和 `text/x-json` 视图会由 VS Code 原生渲染，但如果没有为 `application/github-issue` 这个 MIME 类型注册 `NotebookRenderer`，这个视图就会显示一条错误。

**MIME 类型**是表示数据格式的标准名称，形如 `类型/子类型`，比如 `text/html`（HTML）、`image/png`（PNG 图片）、`application/json`（JSON）。富输出的思路是：**同一份结果，同时提供多种格式**，由 VS Code 选择能显示的那一种，用户也可以手动切换。

```ts
execution.replaceOutput([new vscode.NotebookCellOutput([
                            vscode.NotebookCellOutputItem.text('<b>Hello</b> World', 'text/html'),
                            vscode.NotebookCellOutputItem.json({ hello: 'world' }),
                            vscode.NotebookCellOutputItem.json({ custom-data-for-custom-renderer: 'data' }, 'application/custom'),
                        ])]);
```

（原文代码第三行的 `custom-data-for-custom-renderer` 作为对象的键时必须加引号，写成 `{ 'custom-data-for-custom-renderer': 'data' }`，否则是语法错误。）

`text()` 和 `json()` 的第二个参数可以指定 MIME 类型，不指定时分别默认为 `text/plain` 和 `application/json`。

![带有富输出的单元格：在格式化的 HTML、JSON 编辑器，以及提示没有可用渲染器（application/hello-world）的错误消息之间切换](images/notebook/rich-output.gif)

动图中，点击输出左侧的 `...` 按钮，可以在同一个输出的几种格式之间切换；切换到没有注册渲染器的自定义 MIME 类型时，显示“没有可用的渲染器”的错误。

> 默认情况下，VS Code 可以渲染以下 MIME 类型：
>
> - application/javascript
> - text/html
> - image/svg+xml
> - text/markdown
> - image/png
> - image/jpeg
> - text/plain
>
> VS Code 会在内置的编辑器中，把以下 MIME 类型渲染为代码：
>
> - text/x-json
> - text/x-javascript
> - text/x-html
> - text/x-rust
> - ……任何其他内置或已安装语言的 text/x-LANGUAGE_ID。
>
> 下面这个笔记本使用内置的编辑器显示了一些 Rust 代码：

![笔记本在内置的 Monaco 编辑器中显示 Rust 代码](images/notebook/rust-output.png)

**Monaco 编辑器**是 VS Code 编辑器核心的名字。也就是说，`text/x-语言ID` 格式的输出会显示成一个带语法高亮的代码框。

> 要渲染其他 MIME 类型，必须为该 MIME 类型注册一个 `NotebookRenderer`。

---

<a id="notebook-renderer"></a>
## 笔记本渲染器（Notebook Renderer）

> 笔记本渲染器负责读取特定 MIME 类型的输出数据，并为这些数据提供渲染后的视图。一个由多个输出单元格共享的渲染器，可以在这些单元格之间维护全局状态。渲染视图的复杂程度，可以从简单的静态 HTML，一直到动态的、完全可交互的小程序。在本节中，我们会探索几种渲染表示 GitHub Issue 的输出的技巧。
>
> 你可以使用我们 Yeoman 生成器中的模板快速开始。为此，首先安装 Yeoman 和 VS Code 生成器：

```bash
npm install -g yo generator-code
```

> 然后运行 `yo code`，选择 `New Notebook Renderer (TypeScript)`。
>
> 如果你不使用这个模板，就要确保在扩展 `package.json` 的 `keywords` 中添加 `notebookRenderer`，并在扩展的名称或描述中提到它支持的 MIME 类型，这样用户才能找到你的渲染器。

<a id="a-simple-non-interactive-renderer"></a>
### 简单的、非交互式的渲染器（A Simple, Non-Interactive Renderer）

> 渲染器通过向扩展 `package.json` 的 `contributes.notebookRenderer` 属性做贡献，为一组 MIME 类型声明。这个渲染器处理 `ms-vscode.github-issue-notebook/github-issue` 格式的输入，我们假设已经安装的某个控制器能够提供这种格式：

```json
{
  "activationEvents": ["...."],
  "contributes": {
    ...
    "notebookRenderer": [
      {
        "id": "github-issue-renderer",
        "displayName": "GitHub Issue Renderer",
        "entrypoint": "./out/renderer.js",
        "mimeTypes": [
          "ms-vscode.github-issue-notebook/github-issue"
        ]
      }
    ]
  }
}
```

| 字段 | 说明 |
|---|---|
| `id` | 渲染器 ID |
| `displayName` | 显示名称 |
| `entrypoint` | 渲染器脚本，**在输出的 iframe 中运行**（不是在扩展宿主中） |
| `mimeTypes` | 这个渲染器负责哪些 MIME 类型 |

> 输出渲染器始终在一个单独的 `iframe` 中渲染，与 VS Code 的其他界面隔离开，以确保它们不会意外地干扰 VS Code 或拖慢 VS Code。这个贡献引用了一个“入口”（entrypoint）脚本，在需要渲染任何输出之前，这个脚本会被加载到笔记本的 `iframe` 中。你的入口文件需要是单个文件，可以自己编写，也可以用 Webpack、Rollup 或 Parcel 之类的打包工具生成。

**这里的运行环境和前面的控制器完全不同：**

| | 控制器（Controller） | 渲染器（Renderer） |
|---|---|---|
| 运行在哪里 | 扩展宿主（和普通扩展代码一样） | 笔记本输出的 iframe 中（和 [Webview](./webview.md) 类似） |
| 能否用 `vscode` API | 能 | 不能 |
| 能否操作 DOM | 不能 | 能 |
| 入口 | `package.json` 的 `main` | `notebookRenderer` 的 `entrypoint` |

所以渲染器的写法更像是在写一个网页脚本，而不是扩展代码。

> 加载后，你的入口脚本应该导出 `vscode-notebook-renderer` 中的 `ActivationFunction`，以便在 VS Code 准备好渲染你的渲染器时渲染你的界面。例如，下面的代码会把所有的 GitHub issue 数据以 JSON 的形式放进单元格的输出中：

```js
import type { ActivationFunction } from 'vscode-notebook-renderer';

export const activate: ActivationFunction = (context) => ({
    renderOutputItem(data, element) {
        element.innerText = JSON.stringify(data.json())
    }
})
```

- `renderOutputItem(data, element)`：每当有一个输出项需要显示时调用。`data` 是输出数据（`data.json()` 解析为 JSON，`data.text()` 取文本，`data.mime` 是 MIME 类型）；`element` 是给这个输出准备好的 DOM 元素，把内容渲染进去即可。
- 渲染器的 `activate` 和扩展的 `activate` 同名，但是两个不同的东西：这个是渲染器在 iframe 中的入口函数。

> 你可以[在这里查看完整的 API 定义](https://github.com/DefinitelyTyped/DefinitelyTyped/blob/master/types/vscode-notebook-renderer/index.d.ts)。如果你使用 TypeScript，可以安装 `@types/vscode-notebook-renderer`，然后把 `vscode-notebook-renderer` 添加到 `tsconfig.json` 的 `types` 数组中，这样代码中就能使用这些类型了。
>
> 要创建更丰富的内容，你可以手动创建 DOM 元素，或者使用 Preact 之类的框架把内容渲染到输出元素中，例如：

```jsx
import type { ActivationFunction } from 'vscode-notebook-renderer';
import { h, render } from 'preact';

const Issue: FunctionComponent<{ issue: GithubIssue }> = ({ issue }) => (
  <div key={issue.number}>
    <h2>
      {issue.title}
      (<a href={`https://github.com/${issue.repo}/issues/${issue.number}`}>#{issue.number}</a>)
    </h2>
    <img src={issue.user.avatar_url} style={{ float: 'left', width: 32, borderRadius: '50%', marginRight: 20 }} />
    <i>@{issue.user.login}</i> Opened: <div style="margin-top: 10px">{issue.body}</div>
  </div>
);

const GithubIssues: FunctionComponent<{ issues: GithubIssue[]; }> = ({ issues }) => (
  <div>{issues.map(issue => <Issue key={issue.number} issue={issue} />)}</div>
);

export const activate: ActivationFunction = (context) => ({
    renderOutputItem(data, element) {
        render(<GithubIssues issues={data.json()} />, element);
    }
});
```

**Preact** 是一个和 React 用法几乎相同、但体积小得多的前端框架。代码中的 `<div>...</div>` 是 JSX 语法，需要打包工具编译。`FunctionComponent`、`GithubIssue` 等类型在示例中省略了导入和定义。

> 在一个带有 `ms-vscode.github-issue-notebook/github-issue` 数据字段的输出单元格上运行这个渲染器，会得到下面的静态 HTML 视图：

![单元格输出显示了 issue 的 HTML 渲染视图](images/notebook/static-renderer-sample.png)

> 如果你在容器之外有元素，或者有其他异步过程，可以用 `disposeOutputItem` 来清理它们。当输出被清除、单元格被删除，以及为已有单元格渲染新输出之前，都会触发这个事件。例如：

```js
const intervals = new Map();

export const activate: ActivationFunction = (context) => ({
    renderOutputItem(data, element) {
        render(<GithubIssues issues={data.json()} />, element);

        intervals.set(data.mime, setInterval(() => {
            if(element.querySelector('h2')) {
                element.querySelector('h2')!.style.color = `hsl(${Math.random() * 360}, 100%, 50%)`;
            }
        }, 1000));
    },
    disposeOutputItem(id) {
        clearInterval(intervals.get(id));
        intervals.delete(id);
    }
});
```

（这个示例中，`intervals` 用 `data.mime` 作为键保存定时器，而 `disposeOutputItem` 收到的参数是输出项的 `id`，两者对不上。实际使用时应该用 `data.id` 作为键，这样才能在清理时找到对应的定时器。）

> 一定要记住，一个笔记本的所有输出，都是在同一个 iframe 的不同元素中渲染的。如果你使用 `document.querySelector` 之类的函数，一定要把查找范围限定在你关心的那个输出内，以免和其他输出冲突。在这个示例中，我们用 `element.querySelector` 来避免这个问题。

也就是说，页面上可能同时有十几个单元格的输出，都在同一个 `document` 中。用 `document.querySelector('h2')` 可能会找到别的单元格里的 `h2`。永远从 `element` 开始查找。

<a id="interactive-notebooks-communicating-with-the-controller"></a>
### 交互式笔记本：与控制器通信（Interactive Notebooks (communicating with the controller)）

> 假设我们想添加一个功能：点击渲染输出中的按钮后，查看 issue 的评论。假设某个控制器能够以 `ms-vscode.github-issue-notebook/github-issue-with-comments` MIME 类型提供带有评论的 issue 数据，我们可能会尝试一开始就获取所有评论，并这样实现：

```jsx
const Issue: FunctionComponent<{ issue: GithubIssueWithComments }> = ({ issue }) => {
  const [showComments, setShowComments] = useState(false);

  return (
    <div key={issue.number}>
      <h2>
        {issue.title}
        (<a href={`https://github.com/${issue.repo}/issues/${issue.number}`}>#{issue.number}</a>)
      </h2>
      <img src={issue.user.avatar_url} style={{ float: 'left', width: 32, borderRadius: '50%', marginRight: 20 }} />
      <i>@{issue.user.login}</i> Opened: <div style="margin-top: 10px">{issue.body}</div>
      <button onClick={() => setShowComments(true)}>Show Comments</button>
      {showComments && issue.comments.map(comment => <div>{comment.text}</div>)}
    </div>
  );
};
```

> 这马上就暴露出一些问题。首先，即使还没点击按钮，我们就已经为所有 issue 加载了完整的评论数据。此外，虽然我们只是想多显示一点数据，却要求控制器支持一种完全不同的 MIME 类型。
>
> 更好的做法是，控制器可以通过附带一个预加载脚本（preload script），为渲染器提供额外的功能，VS Code 也会把这个脚本加载到 iframe 中。这个脚本可以访问全局函数 `postKernelMessage` 和 `onDidReceiveKernelMessage`，用来与控制器通信。

![控制器如何通过 NotebookRendererScript 与渲染器交互的示意图](images/notebook/kernel-communication.png)

图中，中间的虚线把两个运行环境分开：左边是**扩展宿主上下文**，控制器运行在这里，接收执行请求；右边是**笔记本输出上下文**（iframe），渲染器和预加载脚本（NotebookRendererScript）运行在这里。控制器通过 `ActivationFunction` 把 HTML 渲染结果交给渲染器；控制器和预加载脚本之间通过 `postMessage` / `onDidReceiveMessage` 双向通信；预加载脚本再通过一个全局变量（exposed global）把功能提供给渲染器使用。

> **注意（本指南补充）：** 本节接下来用到的 `NotebookController.rendererScripts`、`vscode.NotebookRendererScript`，以及 `NotebookController` 上的 `onDidReceiveMessage` 和 `postMessage`，在当前稳定版的类型定义（`@types/vscode` 1.140）中**都不存在**，它们属于提议 API（proposed API），只能在满足特定条件的扩展中使用（见 [使用提议 API](../advanced-topics/using-proposed-api.md)），发布到扩展市场的扩展一般不能使用。稳定 API 中可用的通信方式，是下一节介绍的 `notebooks.createRendererMessaging`。下面的内容按原文翻译，供了解这种设计思路。

> 例如，你可以修改控制器的 `rendererScripts`，引用一个新文件。在这个文件中建立一个回到扩展宿主的连接，并暴露一个全局的通信脚本供渲染器使用。
>
> 在你的控制器中：

```ts
class Controller {
    // ...

    readonly rendererScriptId = 'my-renderer-script';

    constructor() {
        // ...

        this._controller.rendererScripts.push(new vscode.NotebookRendererScript(vscode.Uri.file(/* 脚本的路径 */), rendererScriptId));
    }
}
```

> 在你的 `package.json` 中，把这个脚本指定为渲染器的依赖：

```json
{
  "activationEvents": ["...."],
  "contributes": {
    ...
    "notebookRenderer": [
      {
        "id": "github-issue-renderer",
        "displayName": "GitHub Issue Renderer",
        "entrypoint": "./out/renderer.js",
        "mimeTypes": [...],
        "dependencies": [
            "my-renderer-script"
        ]
      }
    ]
  }
}
```

> 在你的脚本文件中，可以声明用于与控制器通信的函数：

```js
import "vscode-notebook-renderer/preload";

globalThis.githubIssueCommentProvider = {
  loadComments(issueId: string, callback: (comments: GithubComment[]) => void) {
    postKernelMessage({ command: 'comments', issueId });

    onDidReceiveKernelMessage(event => {
        if (event.data.type === 'comments' && event.data.issueId === issueId) {
            callback(event.data.comments);
        }
    })
  }
};
```

> 然后就可以在渲染器中使用它了。你要确保检查控制器的渲染脚本暴露的全局变量是否可用，因为其他开发者也可能在其他笔记本和控制器中创建 GitHub issue 输出，而那些控制器并没有实现 `githubIssueCommentProvider`。在这种情况下，我们只在全局变量可用时才显示 **Load Comments** 按钮：

```jsx
const canLoadComments = globalThis.githubIssueCommentProvider !== undefined;
const Issue: FunctionComponent<{ issue: GithubIssue }> = ({ issue }) => {
  const [comments, setComments] = useState([]);
  const loadComments = () =>
    globalThis.githubIssueCommentProvider.loadComments(issue.id, setComments);

  return (
    <div key={issue.number}>
      <h2>
        {issue.title}
        (<a href={`https://github.com/${issue.repo}/issues/${issue.number}`}>#{issue.number}</a>)
      </h2>
      <img src={issue.user.avatar_url} style={{ float: 'left', width: 32, borderRadius: '50%', marginRight: 20 }} />
      <i>@{issue.user.login}</i> Opened: <div style="margin-top: 10px">{issue.body}</div>
      {canLoadComments && <button onClick={loadComments}>Load Comments</button>}
      {comments.map(comment => <div>{comment.text}</div>)}
    </div>
  );
};
```

> 最后，我们要建立与控制器的通信。当渲染器使用全局函数 `postKernelMessage` 发送消息时，会调用 `NotebookController.onDidReceiveMessage` 方法。要实现这个方法，订阅 `onDidReceiveMessage` 来监听消息：

```ts
class Controller {
    // ...

    constructor() {
        // ...

        this._controller.onDidReceiveMessage(event => {
            if (event.message.command === 'comments') {
                _getCommentsForIssue(event.message.issueId).then(comments => this._controller.postMessage({
                    type: 'comments',
                    issueId: event.message.issueId,
                    comments,
                }), event.editor);
            }
        })
    }
}
```

这套设计的关键是**按需加载**：渲染器先只显示基本信息，用户点击按钮时，才通过消息向控制器请求评论数据。另外，渲染器要先检查全局变量是否存在，因为同样的 MIME 类型可能来自其他不支持这个功能的控制器——这是一种“能力检测”的写法，在下一节同样会用到。

<a id="interactive-notebooks-communicating-with-the-extension-host"></a>
### 交互式笔记本：与扩展宿主通信（Interactive Notebooks (communicating with the extension host)）

> 假设我们想添加一个功能：在一个单独的编辑器中打开输出项。为了实现这一点，渲染器需要能够向扩展宿主发送消息，再由扩展宿主打开编辑器。
>
> 当渲染器和控制器是两个独立的扩展时，这种方式会很有用。
>
> 在渲染器扩展的 `package.json` 中，把 `requiresMessaging` 的值指定为 `optional`，这样无论能否访问扩展宿主，你的渲染器都能正常工作。

```json
{
  "activationEvents": ["...."],
  "contributes": {
    ...
    "notebookRenderer": [
      {
        "id": "output-editor-renderer",
        "displayName": "Output Editor Renderer",
        "entrypoint": "./out/renderer.js",
        "mimeTypes": [...],
        "requiresMessaging": "optional"
      }
    ]
  }
}
```

> `requiresMessaging` 的可选值包括：

| 值 | 含义 |
|---|---|
| `always` | 必须能通信。只有当渲染器属于一个可以在扩展宿主中运行的扩展时，才会使用这个渲染器 |
| `optional` | 有扩展宿主可用时，有通信会更好，但安装和运行渲染器并不依赖通信 |
| `never` | 渲染器不需要通信 |

> 推荐使用后两个选项，因为这能保证渲染器扩展可以移植到其他不一定有扩展宿主的环境中。

**什么环境下没有扩展宿主？** 比如在 GitHub 网页上预览 `.ipynb` 文件，或者把笔记本导出为 HTML 后在浏览器中打开。这些地方只有输出的 iframe，没有运行扩展代码的扩展宿主。设成 `optional` 的渲染器在这些环境下依然能显示内容，只是需要扩展宿主配合的那部分功能不可用。

> 渲染器脚本文件可以这样建立通信：

```js
import { ActivationFunction } from 'vscode-notebook-renderer';

export const activate: ActivationFunction = (context) => ({
  renderOutputItem(data, element) {
    // 用输出的 `data` 渲染输出
    ....
    // 能否通信取决于 `requiresMessaging` 的值
    if (!context.postMessage){
      return;
    }

    // 当用户在输出中进行某些操作时（比如点击按钮），
    // 向扩展宿主发送消息，请求打开编辑器。
    document.querySelector('#openEditor').addEventListener('click', () => {
      context.postMessage({
        request: 'showEditor',
        data: '<custom data>'
      })
    });
  }
});
```

（结合上一节的提醒：这里用 `document.querySelector` 查找按钮，如果页面上有多个输出都带有 `#openEditor` 按钮，就会冲突。实际使用时应该改成 `element.querySelector('#openEditor')`。）

> 然后，你可以在扩展宿主中这样接收这条消息：

```ts
const messageChannel = notebooks.createRendererMessaging('output-editor-renderer');
messageChannel.onDidReceiveMessage((e) => {
  if (e.message.request === 'showEditor'){
    // 为 `e.message.data` 所标识的输出打开编辑器
  }
});
```

`createRendererMessaging` 的参数是渲染器的 `id`（`package.json` 中声明的那个）。返回的对象除了 `onDidReceiveMessage`，还有 `postMessage(消息, 编辑器?)`，可以反过来向渲染器发送消息；渲染器中通过 `context.onDidReceiveMessage` 接收。这是稳定版 API 中渲染器与扩展通信的方式。

> 注意：
>
> - 为了确保在消息送达之前你的扩展已经在扩展宿主中运行，请把 `onRenderer:<your renderer id>` 添加到 `activationEvents` 中，并在扩展的 `activate` 函数中建立通信。
> - 渲染器扩展发送给扩展宿主的消息，并不保证全部送达。用户可能在渲染器的消息送达之前就关闭了笔记本。

```json
"activationEvents": ["onRenderer:output-editor-renderer"]
```

---

<a id="supporting-debugging"></a>
## 支持调试（Supporting debugging）

> 对于某些控制器，比如实现了某种编程语言的控制器，可能会希望允许调试单元格的执行。要添加调试支持，笔记本内核可以实现一个[调试适配器](./debugger-extension.md)：要么直接实现[调试适配器协议](https://microsoft.github.io/debug-adapter-protocol/)（DAP），要么把协议委托并转换给一个已有的笔记本调试器（就像 'vscode-simple-jupyter-notebook' 示例中那样）。一种简单得多的方式是使用一个现有的、未经修改的调试扩展，并根据笔记本的需要即时转换 DAP（就像 'vscode-nodebook' 中那样）。
>
> 示例：
>
> - [vscode-nodebook](https://github.com/microsoft/vscode-nodebook)：Node.js 笔记本，调试支持由 VS Code 内置的 JavaScript 调试器以及一些简单的协议转换提供
> - [vscode-simple-jupyter-notebook](https://github.com/microsoft/vscode-simple-jupyter-notebook)：Jupyter 笔记本，调试支持由现有的 Xeus 调试器提供

调试适配器协议（DAP）在 [扩展能力概览](../extension-capabilities/overview.md) 中介绍过，详细内容见 [调试器扩展](./debugger-extension.md)。三种方式按难度从高到低：

| 方式 | 做法 | 示例 |
|---|---|---|
| 直接实现 DAP | 自己实现完整的调试适配器 | — |
| 委托给已有的笔记本调试器 | 把协议转换后交给现成的调试器 | vscode-simple-jupyter-notebook（Xeus 调试器） |
| 复用现有的调试扩展 | 不修改调试扩展，只在中间即时转换 DAP 消息 | vscode-nodebook（内置的 JavaScript 调试器） |

---

## 本篇小结

```text
笔记本 = 单元格（Markdown / 代码）+ 输出

三个组成部分
  ├─ NotebookSerializer：文件 ⇄ NotebookData
  │     package.json：contributes.notebooks（type、selector）
  │     代码：workspace.registerNotebookSerializer(type, serializer)
  ├─ NotebookController（内核）：执行代码单元格
  │     notebooks.createNotebookController(id, notebookType, label)
  │     executeHandler → createNotebookCellExecution → start → replaceOutput → end
  └─ NotebookRenderer：显示 VS Code 不认识的输出格式
        package.json：contributes.notebookRenderer（entrypoint、mimeTypes）
        在 iframe 中运行：export activate → renderOutputItem(data, element)

输出：text（纯文本）、error（错误）、富输出（同一结果多种 MIME 格式）
  VS Code 内置：text/plain、text/html、text/markdown、image/png 等；text/x-语言ID 显示为代码

通信
  稳定 API：渲染器 context.postMessage ⇄ 扩展 notebooks.createRendererMessaging(渲染器id)
            requiresMessaging：always / optional / never（推荐后两个）
  提议 API：控制器 rendererScripts + postKernelMessage（稳定版中不可用）

渲染器注意：所有输出共用一个 iframe，DOM 查找从 element 开始
```
