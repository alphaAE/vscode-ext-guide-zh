# Markdown 扩展（Markdown Extension）

> 原文：[Markdown Extension](https://code.visualstudio.com/api/extension-guides/markdown-extension)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/markdown-extension.md`（DateApproved: 10/7/2026）

> Markdown 扩展让你可以扩展和增强 VS Code 内置的 Markdown 支持。你可以改变 Markdown 预览的外观，添加对新 Markdown 语法的支持，还可以为围栏代码块（fenced code block）贡献交互式编辑器。

VS Code 内置的 Markdown 预览（`Ctrl+Shift+V` 打开）本身就是一个扩展，它对外开放了几个扩展点。本篇介绍的四种方式，难度依次递增：

| 方式 | 贡献点 | 能做什么 | 需要写代码吗 |
|---|---|---|---|
| 样式 | `markdown.previewStyles` | 改变预览的外观 | 只写 CSS |
| markdown-it 插件 | `markdown.markdownItPlugins` | 支持新的 Markdown 语法 | 是（扩展代码） |
| 预览脚本 | `markdown.previewScripts` | 在预览中运行脚本，实现动态内容 | 是（预览中的 JS） |
| 代码块编辑器（实验性） | `markdown.codeBlockEditorProviders` | 把代码块替换成交互式编辑器 | 是 |

**围栏代码块**就是用三个反引号包起来的代码块，反引号后面的那个词（如 `json`、`mermaid`）叫作 **info string**（信息字符串），通常表示代码块的语言。

---

<a id="changing-the-look-of-the-markdown-preview-with-css"></a>
## 用 CSS 改变 Markdown 预览的外观（Changing the look of the Markdown preview with CSS）

> 扩展可以贡献 CSS，来改变 Markdown 预览的外观或布局。样式表通过扩展 `package.json` 中的 `markdown.previewStyles` [贡献点](../references/contribution-points.md)注册：

```json
"contributes": {
    "markdown.previewStyles": [
        "./style.css"
    ]
}
```

> `"markdown.previewStyles"` 是一组文件，路径相对于扩展的根文件夹。
>
> 贡献的样式会添加在内置的 Markdown 预览样式之后，但在用户的 `"markdown.styles"` 之前。

样式的加载顺序决定了谁能覆盖谁（后加载的优先）：

```text
内置的预览样式  →  扩展贡献的样式（markdown.previewStyles）  →  用户设置的样式（markdown.styles）
                                                                    （优先级最高）
```

也就是说，你的扩展可以覆盖内置样式，而用户自己的设置又可以覆盖你的扩展。

例如，让预览中的标题显示为蓝色：

```css
/* style.css */
h1, h2, h3 {
  color: #3a7bd5;
}
```

预览本身也是一个 Webview，所以同样可以使用 VS Code 的主题 CSS 变量（如 `var(--vscode-editor-foreground)`），让样式自动适配当前主题（见 [Webview 指南](./webview.md#theming-webview-content)）。

> [Markdown Preview GitHub Styling](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-preview-github-styles) 扩展是一个很好的例子，它演示了如何用样式表让 Markdown 预览看起来像 GitHub 渲染的 Markdown。你可以在 [GitHub](https://github.com/mjbvz/vscode-github-markdown-preview-style) 上查看这个扩展的源代码。

---

<a id="adding-support-for-new-syntax-with-markdown-it-plugins"></a>
## 用 markdown-it 插件添加对新语法的支持（Adding support for new syntax with markdown-it plugins）

> VS Code 的 Markdown 预览支持 [CommonMark 规范](https://spec.commonmark.org)。扩展可以通过贡献一个 [markdown-it 插件](https://github.com/markdown-it/markdown-it#syntax-extensions)来支持更多的 Markdown 语法。

**背景知识：**

- **CommonMark** 是 Markdown 的一个标准规范。原始的 Markdown 有很多模糊的地方，不同工具的渲染结果不一致，CommonMark 把这些规则统一了下来。
- **markdown-it** 是一个把 Markdown 转换成 HTML 的 JavaScript 库，VS Code 的 Markdown 预览就是用它来渲染的。它支持插件，社区已经有大量现成的插件，比如支持 emoji 短代码（`:smile:`）、脚注、数学公式等。

> 要贡献一个 markdown-it 插件，首先在扩展的 `package.json` 中添加 `"markdown.markdownItPlugins"` 贡献：

```json
"contributes": {
    "markdown.markdownItPlugins": true
}
```

> 然后，在扩展主文件的 `activate` 函数中，返回一个包含 `extendMarkdownIt` 函数的对象。这个函数接收当前的 markdown-it 实例，并且必须返回一个新的 markdown-it 实例：

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  return {
    extendMarkdownIt(md: any) {
      return md.use(require('markdown-it-emoji'));
    }
  };
}
```

**`activate` 的返回值是做什么用的？** 在前面的所有示例中，`activate` 都没有返回值。实际上，`activate` 返回的对象就是这个扩展**对外公开的 API**，其他扩展可以通过 `vscode.extensions.getExtension('发布者.扩展名').exports` 拿到它。内置的 Markdown 扩展正是利用了这个机制：它会找到所有声明了 `markdown.markdownItPlugins` 的扩展，取出它们返回的 `extendMarkdownIt` 函数，把自己的 markdown-it 实例交给这些函数加工。

`md.use(插件)` 是 markdown-it 加载插件的方法，它返回 markdown-it 实例本身，所以可以直接返回。示例中的 `markdown-it-emoji` 需要先用 npm 安装到扩展的依赖中：`npm install markdown-it-emoji`。

> 要贡献多个 markdown-it 插件，可以返回链式调用的多个 `use` 语句：

```ts
return md.use(require('markdown-it-emoji')).use(require('markdown-it-hashtag'));
```

> 贡献 markdown-it 插件的扩展会被延迟激活，在第一次显示 Markdown 预览时才激活。

> [markdown-emoji](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-emoji) 扩展演示了如何使用 markdown-it 插件为 Markdown 预览添加 emoji 支持。你可以在 [GitHub](https://github.com/mjbvz/vscode-markdown-emoji) 上查看这个 Emoji 扩展的源代码。
>
> 你可能还想看看：
>
> - 面向 markdown-it 插件开发者的[指南](https://github.com/markdown-it/markdown-it/blob/master/docs/development.md)
> - [现有的 markdown-it 插件](https://www.npmjs.com/browse/keyword/markdown-it-plugin)

---

<a id="adding-advanced-functionality-with-scripts"></a>
## 用脚本添加高级功能（Adding advanced functionality with scripts）

> 对于高级功能，扩展可以贡献在 Markdown 预览中执行的脚本。

```json
"contributes": {
    "markdown.previewScripts": [
        "./main.js"
    ]
}
```

> 贡献的脚本是异步加载的，并且每次内容变化时都会重新加载。

**markdown-it 插件和预览脚本的区别：**

| | markdown-it 插件 | 预览脚本 |
|---|---|---|
| 在哪里运行 | 扩展宿主中，Markdown 转 HTML 的阶段 | 预览页面（Webview）中，HTML 显示出来之后 |
| 能做什么 | 改变 Markdown 如何**转换**成 HTML | 对已经显示出来的页面做**后处理**，比如把某段文字渲染成图表 |
| 例子 | 把 `:smile:` 转换成 😄 | 把 `mermaid` 代码块画成流程图 |

“每次内容变化时都会重新加载”意味着用户每改一个字，预览刷新时脚本都会重新执行一遍。所以脚本中要能处理“页面内容整体被替换”的情况，不要假设脚本只执行一次。

> [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) 扩展演示了如何使用脚本，为 Markdown 预览添加 [Mermaid](https://mermaid.js.org) 图表和流程图支持。你可以在 [GitHub](https://github.com/mjbvz/vscode-markdown-mermaid) 上查看这个 Mermaid 扩展的源代码。

---

<a id="add-code-block-editors-experimental"></a>
## 添加代码块编辑器（实验性）（Add code block editors (Experimental)）

> 扩展可以在 Markdown 编辑器中，把围栏代码块替换为基于 iframe 的交互式编辑器。例如，扩展可以为 JSON 提供一个表单编辑器、一个图表编辑器，或者一个任务进度视图。代码块仍然是文档内容的权威来源，并与扩展贡献的编辑器保持同步。

> **注意**
>
> Markdown 代码块编辑器是实验性功能，作用于 Markdown **编辑器**，而不是标准的 Markdown 预览。这个贡献点和扩展导出 API 可能会发生变化。

**请特别注意这两点：**

1. 这是**实验性**功能，API 随时可能变化。本节内容翻译自 2026 年 10 月的原文，使用前请对照官网最新文档。
2. 它作用于 **Markdown 编辑器**，不是前面几节说的“预览”。也就是说，这里讲的是在编辑 Markdown 时，代码块直接显示成一个交互式的小部件；而前面几节讲的是旁边那个只读的预览窗口。

> 代码块编辑器只在[受信任的工作区](https://code.visualstudio.com/docs/editing/workspaces/workspace-trust)中加载。在受限模式（Restricted Mode）下，Markdown 编辑器不会加载扩展贡献的代码块编辑器及其资源。

工作区信任的概念见 [工作区信任](./workspace-trust.md)。

<a id="register-a-static-code-block-editor"></a>
### 注册静态代码块编辑器（Register a static code block editor）

> 使用 `markdown.codeBlockEditorProviders` 贡献点选择围栏代码块，并提供一个 HTML 入口文件：

```json
{
  "contributes": {
    "markdown.codeBlockEditorProviders": [
      {
        "id": "taskProgress",
        "selector": {
          "language": "task-progress"
        },
        "source": {
          "kind": "static",
          "entrypoint": "./editor/index.html"
        },
        "runtimeKey": "task-progress-v1",
        "contentType": "text",
        "initialHeight": 80
      }
    ]
  }
}
```

> 这个贡献会替换 info string 恰好是 `task-progress` 的围栏代码块：

````markdown
```task-progress
- [x] Create the extension
- [ ] Publish the extension
```
````

> 提供者支持以下属性：

| 属性 | 必填 | 说明 |
| --- | --- | --- |
| `id` | 是 | 在扩展内标识这个提供者。值不能为空。 |
| `selector` | 是 | 用 `language` 选择一个完全相同的 info string，或者用 `languagePrefix` 选择所有以某个值开头的 info string。只能指定其中一种选择方式。值不能为空。 |
| `source` | 是 | `static` 类型的提供者使用一个相对于扩展的 HTML 入口文件 `entrypoint`；`exportApi` 类型的提供者使用扩展导出的 API。 |
| `runtimeKey` | 否 | 标识可以复用的、相互兼容的 iframe 运行时。值必须包含 1 到 256 个字符。 |
| `contentType` | 否 | 代码块内容的表示形式：`text` 或 `json`。默认是 `text`。 |
| `initialHeight` | 否 | 在编辑器报告实际测量的高度之前，预留的高度（正数，单位为像素）。 |
| `sandbox` | 否 | 设置提供者可以请求的 iframe 可选权限的上限。支持的属性有 `forms`、`downloads`、`pointerLock` 和 `clipboardWrite`。每项权限默认都是 `false`。 |

> `entrypoint` 路径相对于扩展根目录。HTML 中的相对路径的脚本、样式表和其他资源，相对于入口文件所在的目录解析。

**两种 `source` 的区别：**

| | `static` | `exportApi` |
|---|---|---|
| HTML 从哪里来 | 固定的 HTML 文件 | 扩展代码在运行时决定 |
| 扩展宿主能否参与 | 不能，iframe 只和代码块内容同步 | 能，可以和 iframe 双向发消息 |
| 适合 | 纯前端就能完成的编辑器 | 需要扩展参与的编辑器（比如读取工作区的其他文件） |

`initialHeight` 的作用：iframe 加载需要时间，加载完成前不知道它有多高。如果不预留高度，内容加载完时页面会突然“跳”一下。

<a id="connect-the-iframe-editor"></a>
### 连接 iframe 编辑器（Connect the iframe editor）

> 在 iframe 应用中安装并打包实验性的 `@vscode/web-editors` 包。这个包负责在代码块和 iframe 之间同步内容、只读状态和尺寸。
>
> HTML 入口文件可以加载一个打包好的 JavaScript 模块：

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Task progress editor</title>
</head>
<body>
  <textarea id="editor"></textarea>
  <script type="module" src="./dist/main.js"></script>
</body>
</html>
```

> 把 iframe 连接到它的父窗口，把用户的编辑应用到根内容值上，并响应来自宿主的更新：

```ts
import { WebEditorClient } from '@vscode/web-editors';

const editor = document.querySelector<HTMLTextAreaElement>('#editor');
if (!editor) {
  throw new Error('Task progress editor element not found');
}

// 连接到父窗口（Markdown 编辑器），内容按文本处理
const client = await WebEditorClient.connect({
  connection: 'windowParent',
  contentType: 'text'
});

// 把收到的内容显示到 textarea 中（内容相同时不重复赋值，避免光标跳动）
const updateContent = (content: unknown) => {
  if (typeof content === 'string' && editor.value !== content) {
    editor.value = content;
  }
};

// 初始化：读取当前内容和只读状态
updateContent(client.getContent());
editor.readOnly = client.getReadOnly();

// 宿主中的内容或只读状态变化时，更新界面
client.onDidChangeContent(event => updateContent(event.content));
client.onDidChangeReadOnly(event => {
  editor.readOnly = event.readOnly;
});

// 用户在 textarea 中输入时，把整段内容替换回代码块（path: [] 表示根内容）
editor.addEventListener('input', () => {
  client.applyEdits([{
    kind: 'replace',
    path: [],
    newValue: editor.value
  }]);
});

// 页面尺寸变化时，把高度报告给宿主，让代码块区域随之调整
const resizeObserver = new ResizeObserver(() => {
  client.reportSize(document.documentElement.scrollHeight);
});
resizeObserver.observe(document.documentElement);

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
  resizeObserver.disconnect();
  client.dispose();
}, { once: true });
```

这段代码的结构和 [自定义编辑器](./custom-editors.md#synchronizing-changes-with-the-textdocument) 中的双向同步是同一个思路：

```text
代码块内容 ──onDidChangeContent──→ iframe 界面（只更新显示）
iframe 中的用户输入 ──applyEdits──→ 代码块内容
```

同样要注意避免循环更新：`updateContent` 中先判断 `editor.value !== content`，内容没变就不赋值。

这里的 `WebEditorClient` 来自实验性的 `@vscode/web-editors` 包，不属于 `vscode` 扩展 API，它的接口以这个包的文档为准。

<a id="resolve-editors-from-the-extension-host"></a>
### 从扩展宿主解析编辑器（Resolve editors from the extension host）

> 当扩展宿主需要动态选择 HTML，或者需要与 iframe 运行时通信时，使用 `exportApi` 类型的 source。用 API 版本 2 注册这个 source：

```json
{
  "contributes": {
    "markdown.codeBlockEditorProviders": [
      {
        "id": "taskProgress",
        "selector": {
          "languagePrefix": "task-progress"
        },
        "source": {
          "kind": "exportApi",
          "apiVersion": 2
        },
        "runtimeKey": "task-progress-v1",
        "contentType": "text",
        "initialHeight": 80
      }
    ]
  }
}
```

注意这里用的是 `languagePrefix`，所以 `task-progress`、`task-progress-v2`、`task-progress extra` 等所有以 `task-progress` 开头的 info string 都会被匹配。

> 从扩展的 `activate` 函数中返回 `markdownCodeBlockEditors.apiV2` API。`getProvider` 返回的提供者 ID 必须与贡献中的 `id` 一致。

```ts
import * as vscode from 'vscode';

interface ResolveRequest {
  readonly providerId: string;
  readonly language: string;
  readonly documentUri: vscode.Uri;
}

interface HostTransport {
  readonly runtimeKey: string;
  readonly onDidReceiveMessage: vscode.Event<unknown>;
  readonly onDidDispose: vscode.Event<void>;
  sendMessage(message: unknown): void;
}

const providerId = 'taskProgress';

export function activate(context: vscode.ExtensionContext) {
  const provider = {
    // 决定这个代码块使用什么 HTML
    resolve(_request: ResolveRequest, _token: vscode.CancellationToken) {
      return {
        content: {
          uri: vscode.Uri.joinPath(context.extensionUri, 'editor', 'index.html')
        },
        runtimeKey: 'task-progress-v1',
        contentType: 'text' as const,
        initialHeight: 80
      };
    },

    // 建立扩展宿主与 iframe 运行时之间的消息通道
    createHostTransport(
      transport: HostTransport,
      token: vscode.CancellationToken
    ) {
      if (token.isCancellationRequested) {
        return;
      }

      // 收到 iframe 的 ready 消息后，回复 hostReady
      return transport.onDidReceiveMessage(message => {
        if (isReadyMessage(message)) {
          transport.sendMessage({ type: 'hostReady' });
        }
      });
    }
  };

  // activate 的返回值就是扩展对外公开的 API
  return {
    markdownCodeBlockEditors: {
      apiV2: {
        getProvider(id: string) {
          return id === providerId ? provider : undefined;
        }
      }
    }
  };
}

function isReadyMessage(message: unknown): message is { type: 'ready' } {
  return typeof message === 'object'
    && message !== null
    && 'type' in message
    && message.type === 'ready';
}
```

这里再次用到了前面 markdown-it 插件一节讲过的机制：**`activate` 的返回值是扩展对外公开的 API**。内置的 Markdown 扩展会读取你返回的 `markdownCodeBlockEditors.apiV2`，调用 `getProvider` 拿到提供者。

代码中的 `ResolveRequest`、`HostTransport` 两个接口是示例自己定义的类型（这个实验性 API 在 `vscode` 的类型定义中并没有对应的类型），只是为了让代码有类型提示。`isReadyMessage` 是一个 TypeScript 的**类型守卫**函数（返回类型写成 `message is { type: 'ready' }`），用来安全地判断 `unknown` 类型的消息格式。

> `resolve` 方法会接收到提供者 ID、完整的围栏代码块 info string，以及 Markdown 文档的 URI。它既可以用 `content.html`（以及可选的 `content.baseUri`）直接返回 HTML，也可以用 `content.uri` 返回一个 HTML 文件。返回的资源必须位于扩展或工作区之内。
>
> 解析出的编辑器还可以覆盖 `runtimeKey`、`contentType`、`initialHeight` 和 `sandbox`。返回的 `runtimeKey` 同样必须包含 1 到 256 个字符。返回的沙箱权限，只有在贡献中也允许了的情况下才会被授予。

`resolve` 可以返回的内容：

| 字段 | 说明 |
|---|---|
| `content.uri` | HTML 文件的 URI |
| `content.html` | 直接返回 HTML 字符串 |
| `content.baseUri` | （配合 `content.html`）HTML 中相对路径的解析基准 |
| `runtimeKey`、`contentType`、`initialHeight`、`sandbox` | 覆盖贡献中的同名设置。`sandbox` 只能在贡献允许的范围内收紧，不能放宽 |

> API 版本 2 的提供者可以实现 `createHostTransport`，在扩展宿主和 iframe 运行时之间进行双向通知。在 iframe 中，使用可选的 `WebEditorClient.hostTransport`：

```ts
const transport = client.hostTransport;
if (transport) {
  transport.onMessage(message => {
    console.log('Message from the extension host', message);
  });
  transport.sendMessage({ type: 'ready' });
}
```

> 在 `createHostTransport` 初始化期间，宿主会缓冲消息。返回一个 `vscode.Disposable`，以便在 iframe 运行时被释放时清理监听器和资源。如果扩展需要在运行时被释放时立即作出反应，可以使用 `transport.onDidDispose`。

完整的握手过程：

```text
iframe：   sendMessage({ type: 'ready' })
              ↓
扩展宿主： onDidReceiveMessage 收到 ready → sendMessage({ type: 'hostReady' })
              ↓
iframe：   onMessage 收到 hostReady
```

这与 [Webview 指南](./webview.md#passing-messages-from-an-extension-to-a-webview) 中建议的“页面准备好后先通知扩展，扩展再发数据”是同一个思路。不同的是，这里宿主会在初始化期间缓冲消息，减少了消息丢失的问题。

示例中 `createHostTransport` 返回的 `transport.onDidReceiveMessage(...)` 本身就是一个 Disposable，所以满足“返回一个 `vscode.Disposable`”的要求。

<a id="reuse-iframe-runtimes"></a>
### 复用 iframe 运行时（Reuse iframe runtimes）

> Markdown 编辑器会对物理 iframe 进行虚拟化和池化。具有相同 `runtimeKey` 的编辑器，可以在代码块进入和离开视口时复用同一个 iframe 运行时。只有当编辑器的 HTML、脚本和运行时行为相互兼容时，才使用相同的键。
>
> 对于静态提供者，默认的运行时键由提供者 ID 和扩展版本组合而成。对于导出的提供者，解析出的 `runtimeKey` 优先于贡献中的值。如果两者都没有，Markdown 编辑器会根据提供者、扩展版本和语言推导出一个键。
>
> 运行时复用会保留 iframe 应用和宿主通道，但 Web 编辑器协议会为每个逻辑编辑器更新代码块的内容和只读状态。除非在内容变化时重置状态，否则不要把特定于某个代码块的状态存储在同步内容之外。

**虚拟化和池化是什么意思？** 一篇 Markdown 文档中可能有几十个代码块。如果每个都创建一个 iframe，非常耗资源。所以 Markdown 编辑器只为**屏幕上能看到的**代码块创建 iframe（虚拟化），代码块滚出屏幕后，它的 iframe 不销毁，而是放回“池子”里，留给下一个滚进屏幕的代码块使用（池化）。

这带来一个要注意的问题：**同一个 iframe 先后会服务于不同的代码块。** 比如 iframe 先显示代码块 A，你在 JavaScript 变量里记了一些 A 的状态；滚动后这个 iframe 被拿去显示代码块 B，变量里还是 A 的状态，就会出错。所以原文最后强调：代码块相关的状态要么都放在同步的内容中，要么在收到 `onDidChangeContent` 时重置。

---

## 本篇小结

| 需求 | 贡献点 | 关键点 |
|---|---|---|
| 改预览样式 | `markdown.previewStyles` | 加载顺序：内置 → 扩展 → 用户设置 |
| 支持新语法 | `markdown.markdownItPlugins: true` | `activate` 返回 `{ extendMarkdownIt(md) { return md.use(插件) } }` |
| 预览中运行脚本 | `markdown.previewScripts` | 每次内容变化都会重新加载 |
| 代码块变成交互式编辑器（实验性） | `markdown.codeBlockEditorProviders` | 作用于 Markdown 编辑器而非预览；仅在受信任的工作区加载；`static` 或 `exportApi`；同一 iframe 可能被多个代码块复用 |

**贯穿全篇的机制：`activate` 的返回值就是扩展对外公开的 API**，其他扩展（这里是内置的 Markdown 扩展）通过它与你的扩展协作。
