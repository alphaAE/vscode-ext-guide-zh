# Webview API

> 原文：[Webview API](https://code.visualstudio.com/api/extension-guides/webview)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/webview.md`（DateApproved: 10/7/2026）

> Webview API 让扩展可以在 VS Code 中创建完全可定制的视图。例如，内置的 Markdown 扩展就用 Webview 来渲染 Markdown 预览。Webview 也可以用来构建复杂的用户界面，实现 VS Code 原生 API 所不支持的功能。
>
> 可以把 Webview 想象成 VS Code 中一个由你的扩展控制的 `iframe`。Webview 几乎可以在这个框架中渲染任何 HTML 内容，并通过消息传递（message passing）与扩展通信。这种自由让 Webview 变得非常强大，为扩展开辟了全新的可能性。

**`iframe` 是什么？** 它是网页中嵌入另一个网页的元素。打个比方：VS Code 的界面是一个大网页，Webview 就是在其中挖出一块区域，里面放一个由你完全控制的小网页。这个小网页和 VS Code 是**隔离的**：

```text
┌──────────────── VS Code ─────────────────┐
│                                          │
│  扩展宿主进程（你的扩展代码）               │
│     可以调用 vscode API                    │
│     不能操作 DOM                           │
│              ▲                            │
│              │ 消息传递（postMessage）      │
│              ▼                            │
│  ┌──── Webview（隔离的 iframe）────┐       │
│  │ 你写的 HTML / CSS / JavaScript  │       │
│  │ 可以操作自己的 DOM               │       │
│  │ 不能调用 vscode API              │       │
│  └────────────────────────────────┘       │
└──────────────────────────────────────────┘
```

这张图是理解本篇的关键：**扩展代码能用 VS Code API，但不能操作页面；Webview 能操作页面，但不能用 VS Code API。两者只能通过“发消息”协作。** 本篇的大部分内容，都是围绕这一点展开的。

> Webview 用在以下几种 VS Code API 中：
>
> - 用 `createWebviewPanel` 创建的 Webview 面板。这种情况下，Webview 面板在 VS Code 中显示为独立的编辑器，适合用来显示自定义界面和自定义的可视化内容。
> - 作为[自定义编辑器](./custom-editors.md)的视图。自定义编辑器让扩展可以为工作区中的任意文件提供自定义的编辑界面。自定义编辑器 API 还让扩展能够接入编辑器事件（如撤销、重做）以及文件事件（如保存）。
> - 在侧边栏或面板区域中渲染的 [Webview 视图](https://code.visualstudio.com/api/references/vscode-api#WebviewView)。详情请参阅 [Webview 视图示例扩展](https://github.com/microsoft/vscode-extension-samples/tree/main/webview-view-sample)。

| 用法 | 显示在哪里 | 创建方式 |
|---|---|---|
| Webview 面板 | 编辑器区域，像一个标签页 | `window.createWebviewPanel` |
| 自定义编辑器 | 编辑器区域，打开某类文件时代替文本编辑器 | `window.registerCustomEditorProvider` |
| Webview 视图 | 侧边栏或面板中，和树视图并列 | `window.registerWebviewViewProvider` + `contributes.views` 中声明 `"type": "webview"` |

> 本页重点介绍基本的 Webview 面板 API，不过这里介绍的几乎所有内容，也同样适用于自定义编辑器和 Webview 视图中使用的 Webview。即使你更关心那两种 API，我们也建议先通读本页，熟悉 Webview 的基础知识。

---

<a id="links"></a>
## 链接（Links）

> - [Webview 示例](https://github.com/microsoft/vscode-extension-samples/blob/main/webview-sample/README.md)
> - [自定义编辑器文档](./custom-editors.md)
> - [Webview 视图示例](https://github.com/microsoft/vscode-extension-samples/tree/main/webview-view-sample)

<a id="vs-code-api-usage"></a>
### 用到的 VS Code API（VS Code API Usage）

> - [`window.createWebviewPanel`](https://code.visualstudio.com/api/references/vscode-api#window.createWebviewPanel)
> - [`window.registerWebviewPanelSerializer`](https://code.visualstudio.com/api/references/vscode-api#window.registerWebviewPanelSerializer)

---

<a id="should-i-use-a-webview"></a>
## 应该使用 Webview 吗？（Should I use a webview?）

> Webview 非常强大，但也应该谨慎使用，只在 VS Code 原生 API 不够用时才用。Webview 很耗资源，而且运行在与普通扩展不同的上下文中。设计得不好的 Webview，很容易让人觉得和 VS Code 格格不入。
>
> 在使用 Webview 之前，请考虑以下几点：
>
> - 这个功能真的需要放在 VS Code 里吗？做成一个独立的应用或网站会不会更好？
> - Webview 是实现这个功能的唯一方式吗？能不能改用常规的 VS Code API？
> - 你的 Webview 带来的用户价值，足以抵消它高昂的资源开销吗？
>
> 记住：能用 Webview 做某件事，并不代表就应该这么做。不过，如果你确定需要使用 Webview，那么这篇文档会帮到你。我们开始吧。

在 [扩展能力概览](../extension-capabilities/overview.md) 中也提到过，Webview 是“最后的手段”。可以先对照下表，看看原生部件能不能满足需求：

| 需求 | 优先考虑的原生方案 |
|---|---|
| 显示列表、层级数据 | [树视图](./tree-view.md) |
| 让用户选择、输入 | 快速选择、输入框（见 [通用能力](../extension-capabilities/common-capabilities.md)） |
| 显示简短状态 | 状态栏项 |
| 在代码旁显示信息 | 悬停提示、CodeLens、装饰 |
| 显示一段只读文本 | [虚拟文档](./virtual-documents.md) |
| 图表、复杂表单、富文本预览、可视化编辑器 | 这些才真正需要 Webview |

---

<a id="webviews-api-basics"></a>
## Webview API 基础（Webviews API basics）

> 为了讲解 Webview API，我们将构建一个名为 **Cat Coding** 的简单扩展。这个扩展会用一个 Webview 显示一只猫在写代码的 gif 动图（大概是在用 VS Code 写）。在学习 API 的过程中，我们会不断给扩展添加功能，包括一个记录猫已经写了多少行代码的计数器，以及在猫写出 bug 时通知用户的提示。
>
> 下面是 **Cat Coding** 扩展第一个版本的 `package.json`。示例应用的完整代码在[这里](https://github.com/microsoft/vscode-extension-samples/blob/main/webview-sample/README.md)。扩展的第一个版本[贡献了一个命令](../references/contribution-points.md#contributes.commands)，名为 `catCoding.start`。当用户调用这个命令时，我们会显示一个简单的 Webview，里面有我们的猫。用户可以在**命令面板**中通过 **Cat Coding: Start new cat coding session** 调用这个命令，如果愿意的话，也可以给它绑定一个快捷键。

```json
{
  "name": "cat-coding",
  "description": "Cat Coding",
  "version": "0.0.1",
  "publisher": "bierner",
  "engines": {
    "vscode": "^1.74.0"
  },
  "activationEvents": [],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "catCoding.start",
        "title": "Start new cat coding session",
        "category": "Cat Coding"
      }
    ]
  },
  "scripts": {
    "vscode:prepublish": "tsc -p ./",
    "compile": "tsc -watch -p ./",
    "postinstall": "node ./node_modules/vscode/bin/install"
  },
  "dependencies": {
    "vscode": "*"
  },
  "devDependencies": {
    "@types/node": "^9.4.6",
    "typescript": "^2.8.3"
  }
}
```

命令设置了 `category`，所以在命令面板中显示为 `Cat Coding: Start new cat coding session`（见 [命令指南](./command.md#naming-conventions)）。

**这个 `package.json` 中有一部分已经过时了：** `dependencies` 中的 `vscode` 包和 `postinstall` 脚本，是很早以前获取 VS Code 类型定义的方式，现在已经废弃。新项目应该改用 `devDependencies` 中的 `@types/vscode`，脚手架生成的项目就是这样配置的（见 [扩展的结构](../get-started/extension-anatomy.md)）。

> **注意**：如果你的扩展面向 1.74 之前的 VS Code 版本，必须在 `activationEvents` 中显式写上 `onCommand:catCoding.start`。

> 现在我们来实现 `catCoding.start` 命令。在扩展的主文件中，注册 `catCoding.start` 命令，并用它显示一个基本的 Webview：

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      // 创建并显示一个新的 Webview
      const panel = vscode.window.createWebviewPanel(
        'catCoding', // 标识 Webview 的类型，供内部使用
        'Cat Coding', // 显示给用户的面板标题
        vscode.ViewColumn.One, // 在哪个编辑器列中显示新的 Webview 面板
        {} // Webview 选项，后面会详细介绍
      );
    })
  );
}
```

`createWebviewPanel` 的四个参数：

| 参数 | 示例值 | 说明 |
|---|---|---|
| `viewType` | `'catCoding'` | Webview 的**类型** ID。同一类 Webview 共用一个 viewType。后面的右键菜单、序列化（重启后恢复）都要靠它来识别 |
| `title` | `'Cat Coding'` | 标签页上显示的标题 |
| `showOptions` | `vscode.ViewColumn.One` | 显示在哪一列。`One`、`Two`、`Three` 是编辑器的第 1、2、3 列；`Active` 是当前列；`Beside` 是当前列的旁边。也可以传 `{ viewColumn, preserveFocus: true }`，打开时不抢占焦点 |
| `options` | `{}` | Webview 选项（是否允许脚本、能访问哪些本地文件等），见后文 |

> `vscode.window.createWebviewPanel` 函数会在编辑器中创建并显示一个 Webview。如果你在当前状态下运行 `catCoding.start` 命令，会看到这样的画面：

![一个空白的 Webview](images/webview/basics-no_content.png)

截图中，编辑器里打开了一个标题为 Cat Coding 的标签页，内容是空白的。

> 我们的命令打开了一个标题正确的新 Webview 面板，但里面没有任何内容！要把猫添加到新面板中，还需要用 `webview.html` 设置 Webview 的 HTML 内容：

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      // 创建并显示面板
      const panel = vscode.window.createWebviewPanel(
        'catCoding',
        'Cat Coding',
        vscode.ViewColumn.One,
        {}
      );

      // 然后设置它的 HTML 内容
      panel.webview.html = getWebviewContent();
    })
  );
}

function getWebviewContent() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cat Coding</title>
</head>
<body>
    <img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" width="300" />
</body>
</html>`;
}
```

> 再次运行命令，现在 Webview 是这样的：

![一个带有 HTML 内容的 Webview](images/webview/basics-html.png)

截图中，Webview 里显示出了那只正在敲键盘的猫。

> 有进展了！
>
> `webview.html` 应该始终是一个完整的 HTML 文档。HTML 片段或格式错误的 HTML 可能导致意想不到的行为。

也就是说，要写完整的 `<!DOCTYPE html><html><head>...</head><body>...</body></html>`，不要只写 `<img src="...">` 这样的片段。

**写 HTML 的小技巧：** 示例中的 HTML 写在 TypeScript 的模板字符串（反引号 `` ` ``）里，可以用 `${...}` 插入变量。HTML 很长时，也可以把它放在单独的 `.html` 文件里，运行时再读取进来。

<a id="updating-webview-content"></a>
### 更新 Webview 的内容（Updating webview content）

> 创建 Webview 之后，也可以用 `webview.html` 更新它的内容。我们用这一点让 **Cat Coding** 变得更生动：引入几只轮换出场的猫。

```ts
import * as vscode from 'vscode';

const cats = {
  'Coding Cat': 'https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif',
  'Compiling Cat': 'https://media.giphy.com/media/mlvseq9yvZhba/giphy.gif'
};

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      const panel = vscode.window.createWebviewPanel(
        'catCoding',
        'Cat Coding',
        vscode.ViewColumn.One,
        {}
      );

      let iteration = 0;
      const updateWebview = () => {
        const cat = iteration++ % 2 ? 'Compiling Cat' : 'Coding Cat';
        panel.title = cat;
        panel.webview.html = getWebviewContent(cat);
      };

      // 设置初始内容
      updateWebview();

      // 然后每秒更新一次内容
      setInterval(updateWebview, 1000);
    })
  );
}

function getWebviewContent(cat: keyof typeof cats) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cat Coding</title>
</head>
<body>
    <img src="${cats[cat]}" width="300" />
</body>
</html>`;
}
```

![更新 Webview 的内容](images/webview/basics-update.gif)

动图中，标签页的标题和里面的猫每秒在 Coding Cat 和 Compiling Cat 之间切换一次。

`keyof typeof cats` 是 TypeScript 的写法，意思是“`cats` 对象的键名之一”，即 `'Coding Cat' | 'Compiling Cat'`。这样传入其他字符串时，编译器会报错。

> 设置 `webview.html` 会替换掉 Webview 的全部内容，类似于重新加载一个 iframe。开始在 Webview 中使用脚本后，这一点很重要，因为它意味着设置 `webview.html` 也会重置脚本的状态。
>
> 上面的示例还使用了 `webview.title` 来修改编辑器中显示的文档标题。设置标题不会导致 Webview 重新加载。

（原文这里写的是 `webview.title`，但代码中实际用的是 `panel.title`。`title` 是 `WebviewPanel` 的属性，不是 `Webview` 的属性。）

**重要：** 每次给 `html` 赋值，都相当于**刷新整个页面**，页面里 JavaScript 的变量、用户在输入框里填的内容全都会丢失。所以：

- 只是想更新页面中的一部分数据时，**不要**重新设置 `html`，而是用后面介绍的 [`postMessage`](#passing-messages-from-an-extension-to-a-webview) 把数据发给页面，让页面里的脚本自己更新 DOM；
- 设置 `html` 只适合用来初始化页面，或者确实需要整体重新渲染的情况。

<a id="lifecycle"></a>
<a id="lifecycle"></a>
### 生命周期（Lifecycle）

> Webview 面板归创建它的扩展所有。扩展必须保存好 `createWebviewPanel` 返回的 Webview。如果扩展丢失了这个引用，就再也无法重新获取这个 Webview 了，尽管它仍然会继续显示在 VS Code 中。
>
> 和文本编辑器一样，用户也可以随时关闭 Webview 面板。当用户关闭 Webview 面板时，Webview 本身会被销毁。尝试使用已销毁的 Webview 会抛出异常。这意味着上面使用 `setInterval` 的示例实际上有一个重要的 bug：如果用户关闭了面板，`setInterval` 会继续触发，试图更新 `panel.webview.html`，这当然会抛出异常。猫讨厌异常。我们来修复它！
>
> 当 Webview 被销毁时，会触发 `onDidDispose` 事件。我们可以用这个事件取消后续的更新，并清理 Webview 的资源：

```ts
import * as vscode from 'vscode';

const cats = {
  'Coding Cat': 'https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif',
  'Compiling Cat': 'https://media.giphy.com/media/mlvseq9yvZhba/giphy.gif'
};

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      const panel = vscode.window.createWebviewPanel(
        'catCoding',
        'Cat Coding',
        vscode.ViewColumn.One,
        {}
      );

      let iteration = 0;
      const updateWebview = () => {
        const cat = iteration++ % 2 ? 'Compiling Cat' : 'Coding Cat';
        panel.title = cat;
        panel.webview.html = getWebviewContent(cat);
      };

      updateWebview();
      const interval = setInterval(updateWebview, 1000);

      panel.onDidDispose(
        () => {
          // 面板关闭时，取消之后对 Webview 内容的所有更新
          clearInterval(interval);
        },
        null,
        context.subscriptions
      );
    })
  );
}
```

**`panel.onDidDispose(监听函数, null, context.subscriptions)` 的三个参数：** 这是 VS Code 中所有事件（`Event`）通用的订阅方式：

| 参数 | 含义 |
|---|---|
| 第 1 个 | 事件发生时调用的函数 |
| 第 2 个 `thisArgs` | 调用监听函数时 `this` 指向什么。用箭头函数时不需要，传 `null` 或 `undefined` |
| 第 3 个 `disposables` | 一个数组。订阅返回的 Disposable 会被自动放进这个数组 |

所以第三个参数传 `context.subscriptions`，等价于：

```ts
context.subscriptions.push(panel.onDidDispose(() => clearInterval(interval)));
```

> 扩展也可以调用 Webview 的 `dispose()` 方法，通过代码关闭它。例如，如果我们想把猫的工作时间限制在五秒钟：

```ts
export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      const panel = vscode.window.createWebviewPanel(
        'catCoding',
        'Cat Coding',
        vscode.ViewColumn.One,
        {}
      );

      panel.webview.html = getWebviewContent('Coding Cat');

      // 5 秒后，通过代码关闭 Webview 面板
      const timeout = setTimeout(() => panel.dispose(), 5000);

      panel.onDidDispose(
        () => {
          // 处理用户在 5 秒之前就关闭了面板的情况
          clearTimeout(timeout);
        },
        null,
        context.subscriptions
      );
    })
  );
}
```

无论是用户关闭，还是代码调用 `dispose()`，都会触发 `onDidDispose`。所以清理工作统一写在 `onDidDispose` 中即可。

<a id="visibility-and-moving"></a>
### 可见性与移动（Visibility and Moving）

> 当 Webview 面板被移到后台标签页时，它会被隐藏，但不会被销毁。当面板重新回到前台时，VS Code 会自动根据 `webview.html` 恢复 Webview 的内容：

![Webview 重新可见时，内容会自动恢复](images/webview/basics-restore.gif)

动图中，切换到另一个标签页再切回来，Webview 的内容重新出现了。

注意这里说的“恢复”是**按 `html` 重新加载页面**，页面里脚本的状态并没有保留。这一点在后面的 [持久化](#persistence) 一节会详细讨论。

> `.visible` 属性告诉你 Webview 面板当前是否可见。
>
> 扩展可以调用 `reveal()`，通过代码把 Webview 面板带到前台。这个方法接收一个可选的目标视图列，用来指定在哪一列显示面板。一个 Webview 面板同一时间只能显示在一个编辑器列中。调用 `reveal()` 或者把 Webview 面板拖到新的编辑器列，都会把 Webview 移到新的列中。

![在标签页之间拖动时，Webview 会被移动](images/webview/basics-drag.gif)

> 我们来修改扩展，让它同一时间只允许存在一个 Webview。如果面板在后台，`catCoding.start` 命令会把它带到前台：

```ts
export function activate(context: vscode.ExtensionContext) {
  // 记录当前的 Webview 面板
  let currentPanel: vscode.WebviewPanel | undefined = undefined;

  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      const columnToShowIn = vscode.window.activeTextEditor
        ? vscode.window.activeTextEditor.viewColumn
        : undefined;

      if (currentPanel) {
        // 已经有面板了，就在目标列中显示它
        currentPanel.reveal(columnToShowIn);
      } else {
        // 否则创建一个新面板
        currentPanel = vscode.window.createWebviewPanel(
          'catCoding',
          'Cat Coding',
          columnToShowIn || vscode.ViewColumn.One,
          {}
        );
        currentPanel.webview.html = getWebviewContent('Coding Cat');

        // 当前面板被关闭时，重置变量
        currentPanel.onDidDispose(
          () => {
            currentPanel = undefined;
          },
          null,
          context.subscriptions
        );
      }
    })
  );
}
```

> 下面是新扩展的运行效果：

![使用单个面板和 reveal](images/webview/basics-single_panel.gif)

**“单例面板”是非常常用的模式。** 很多场景下，同一个 Webview 打开多份是没有意义的（比如设置页、欢迎页）。关键在于两点：

1. 用一个变量（`currentPanel`）保存面板的引用；
2. 在 `onDidDispose` 中把变量重置为 `undefined`，否则下次执行命令时会对一个已销毁的面板调用 `reveal`，导致报错。

> 每当 Webview 的可见性发生变化，或者 Webview 被移到新的列时，都会触发 `onDidChangeViewState` 事件。我们的扩展可以利用这个事件，根据 Webview 所在的列来切换猫：

```ts
const cats = {
  'Coding Cat': 'https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif',
  'Compiling Cat': 'https://media.giphy.com/media/mlvseq9yvZhba/giphy.gif',
  'Testing Cat': 'https://media.giphy.com/media/3oriO0OEd9QIDdllqo/giphy.gif'
};

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      const panel = vscode.window.createWebviewPanel(
        'catCoding',
        'Cat Coding',
        vscode.ViewColumn.One,
        {}
      );
      panel.webview.html = getWebviewContent('Coding Cat');

      // 根据视图状态的变化更新内容
      panel.onDidChangeViewState(
        e => {
          const panel = e.webviewPanel;
          switch (panel.viewColumn) {
            case vscode.ViewColumn.One:
              updateWebviewForCat(panel, 'Coding Cat');
              return;

            case vscode.ViewColumn.Two:
              updateWebviewForCat(panel, 'Compiling Cat');
              return;

            case vscode.ViewColumn.Three:
              updateWebviewForCat(panel, 'Testing Cat');
              return;
          }
        },
        null,
        context.subscriptions
      );
    })
  );
}

function updateWebviewForCat(panel: vscode.WebviewPanel, catName: keyof typeof cats) {
  panel.title = catName;
  panel.webview.html = getWebviewContent(catName);
}
```

![响应 onDidChangeViewState 事件](images/webview/basics-ondidchangeviewstate.gif)

动图中，把面板拖到第 2 列、第 3 列时，里面的猫随之变成了 Compiling Cat、Testing Cat。

`WebviewPanel` 上与状态相关的属性：

| 属性 | 含义 |
|---|---|
| `visible` | 是否可见（是否是所在列中当前显示的标签页） |
| `active` | 是否是当前获得焦点的面板 |
| `viewColumn` | 所在的列 |
| `onDidChangeViewState` | 上面三个属性发生变化时触发 |

<a id="inspecting-and-debugging-webviews"></a>
### 检查和调试 Webview（Inspecting and debugging webviews）

> **Developer: Toggle Developer Tools** 命令会打开一个[开发者工具](https://developer.chrome.com/docs/devtools/)窗口，你可以用它来调试和检查 Webview。

![开发者工具](images/webview/developer-overview.png)

VS Code 基于 Chromium（Chrome 的内核），所以这个开发者工具和 Chrome 浏览器中按 `F12` 打开的开发者工具是同一个东西。会用 Chrome 调试网页，就会调试 Webview。

**注意：** 要在**扩展开发宿主窗口**（也就是运行你扩展的那个窗口）中执行这个命令，因为 Webview 显示在那个窗口里。

> 注意，如果你使用的 VS Code 版本低于 1.56，或者你要调试的 Webview 设置了 `enableFindWidget`，就必须改用 **Developer: Open Webview Developer Tools** 命令。这个命令会为每个 Webview 打开一个专属的开发者工具页面，而不是使用由所有 Webview 和编辑器本身共享的开发者工具页面。
>
> 在开发者工具中，可以用左上角的检查工具来检查 Webview 的内容：

![使用开发者工具检查 Webview](images/webview/developer-inspect.png)

> 还可以在开发者工具的控制台（Console）中查看 Webview 的所有错误和日志：

![开发者工具的控制台](images/webview/developer-console.png)

Webview 脚本中的 `console.log` 输出在这里，而**不是**在扩展开发时用的调试控制台里。这是两个不同的地方：

| 代码在哪里运行 | `console.log` 输出到哪里 |
|---|---|
| 扩展代码（`extension.ts`） | 原窗口的“调试控制台” |
| Webview 中的脚本 | 扩展开发宿主窗口的“开发者工具 → Console” |

> 要在 Webview 的上下文中对表达式求值，请确保在开发者工具控制台面板左上角的下拉框中选择 **active frame** 环境：

![选择 active frame](images/webview/developer-active-frame.png)

> **active frame** 环境就是 Webview 脚本实际执行的地方。

默认的环境是 VS Code 自身的界面。不切换到 active frame，在控制台中输入的变量名就找不到 Webview 里的变量。

> 此外，**Developer: Reload Webview** 命令会重新加载所有活动的 Webview。如果你需要重置 Webview 的状态，或者磁盘上的某些 Webview 内容发生了变化、你想加载新内容，这个命令会很有用。

---

<a id="loading-local-content"></a>
## 加载本地内容（Loading local content）

> Webview 运行在隔离的上下文中，不能直接访问本地资源。这是出于安全考虑。这意味着，要从你的扩展中加载图片、样式表和其他资源，或者加载用户当前工作区中的任何内容，都必须使用 `Webview.asWebviewUri` 函数，把本地的 `file:` URI 转换成一个特殊的 URI，VS Code 可以用它来加载一部分本地资源。

**为什么不能直接写本地路径？** Webview 本质上是一个网页，网页出于安全原因不能随便读取电脑上的文件。在 HTML 里写 `<img src="C:/xxx/cat.gif">` 或 `file:///...` 都不会生效。必须用 `asWebviewUri` 转换成 VS Code 能处理的特殊地址。

> 假设我们想把猫的 gif 打包进扩展，而不是从 Giphy 网站获取。为此，我们首先创建一个指向磁盘上文件的 URI，然后用 `asWebviewUri` 函数转换这些 URI：

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      const panel = vscode.window.createWebviewPanel(
        'catCoding',
        'Cat Coding',
        vscode.ViewColumn.One,
        {}
      );

      // 获取磁盘上资源的路径
      const onDiskPath = vscode.Uri.joinPath(context.extensionUri, 'media', 'cat.gif');

      // 再转换成 Webview 中可以使用的特殊 URI
      const catGifSrc = panel.webview.asWebviewUri(onDiskPath);

      panel.webview.html = getWebviewContent(catGifSrc);
    })
  );
}

function getWebviewContent(catGifSrc: vscode.Uri) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cat Coding</title>
</head>
<body>
    <img src="${catGifSrc}" width="300" />
</body>
</html>`;
}
```

`context.extensionUri` 是扩展安装目录的 URI，`Uri.joinPath` 在它后面拼接子路径。这里假设扩展目录下有 `media/cat.gif` 文件。

> 调试这段代码时，我们会看到 `catGifSrc` 的实际值类似于：

```text
vscode-resource:/Users/toonces/projects/vscode-cat-coding/media/cat.gif
```

> VS Code 能理解这个特殊的 URI，并会用它从磁盘上加载我们的 gif！

（这是早期版本的格式。新版本 VS Code 中，转换后的地址形如 `https://file+.vscode-resource.vscode-cdn.net/...`。具体格式可能随版本变化，所以**不要自己拼接这种地址，始终使用 `asWebviewUri` 转换**。）

> 默认情况下，Webview 只能访问以下位置中的资源：
>
> - 扩展的安装目录中。
> - 用户当前活动的工作区中。
>
> 使用 `WebviewOptions.localResourceRoots` 可以允许访问其他本地资源。
>
> 你也始终可以使用 data URI，把资源直接嵌入 Webview 中。

data URI 是把文件内容直接编码在地址里，例如 `<img src="data:image/png;base64,iVBORw0KG...">`。适合很小的图片。

<a id="controlling-access-to-local-resources"></a>
### 控制对本地资源的访问（Controlling access to local resources）

> Webview 可以通过 `localResourceRoots` 选项控制能从用户电脑上加载哪些资源。`localResourceRoots` 定义了一组根 URI，只能从这些位置加载本地内容。
>
> 我们可以用 `localResourceRoots` 限制 **Cat Coding** Webview 只能从扩展的 `media` 目录加载资源：

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      const panel = vscode.window.createWebviewPanel(
        'catCoding',
        'Cat Coding',
        vscode.ViewColumn.One,
        {
          // 只允许 Webview 访问扩展 media 目录中的资源
          localResourceRoots: [vscode.Uri.joinPath(context.extensionUri, 'media')]
        }
      );

      const onDiskPath = vscode.Uri.joinPath(context.extensionUri, 'media', 'cat.gif');
      const catGifSrc = panel.webview.asWebviewUri(onDiskPath);

      panel.webview.html = getWebviewContent(catGifSrc);
    })
  );
}
```

> 要禁止访问所有本地资源，只需把 `localResourceRoots` 设为 `[]`。
>
> 一般来说，Webview 加载本地资源的权限应该尽可能严格。不过请记住，`localResourceRoots` 本身并不能提供完整的安全保护。请确保你的 Webview 也遵循了[安全最佳实践](#security)，并添加[内容安全策略](#content-security-policy)，进一步限制可以加载的内容。

**常见问题：图片显示不出来。** 按以下顺序排查：

1. 是否用 `asWebviewUri` 转换了路径？
2. 文件是否在 `localResourceRoots` 允许的目录中？（设置了 `localResourceRoots` 后，默认的“扩展目录 + 工作区”规则就被替换了，只有列出的目录可以访问。）
3. 内容安全策略（CSP）是否允许加载这类资源？（见后文）
4. 打开开发者工具，看 Console 中有没有报错。

<a id="theming-webview-content"></a>
### 为 Webview 内容适配主题（Theming webview content）

> Webview 可以用 CSS 根据 VS Code 的当前主题改变自己的外观。VS Code 把主题分为三类，并在 `body` 元素上添加一个特殊的 class 来表示当前主题：
>
> - `vscode-light`：浅色主题。
> - `vscode-dark`：深色主题。
> - `vscode-high-contrast`：高对比度主题。
>
> 下面的 CSS 会根据用户当前的主题改变 Webview 的文字颜色：

```css
body.vscode-light {
  color: black;
}

body.vscode-dark {
  color: white;
}

body.vscode-high-contrast {
  color: red;
}
```

> 开发 Webview 应用时，请确保它在这三类主题下都能正常使用。并且一定要在高对比度模式下测试你的 Webview，确保有视觉障碍的用户也能使用它。

> Webview 还可以通过 [CSS 变量](https://developer.mozilla.org/docs/Web/CSS/Using_CSS_variables) 使用 VS Code 的主题颜色。这些变量名以 `vscode` 为前缀，并把 `.` 替换为 `-`。例如，`editor.foreground` 对应 `var(--vscode-editor-foreground)`：

```css
code {
  color: var(--vscode-editor-foreground);
}
```

> 可用的主题变量请查阅 [主题颜色参考](../references/theme-color.md)。有一个[扩展](https://marketplace.visualstudio.com/items?itemName=connor4312.css-theme-completions)可以为这些变量提供智能提示。
>
> 还定义了以下与字体相关的变量：
>
> - `--vscode-editor-font-family`：编辑器字体（来自 `editor.fontFamily` 设置）。
> - `--vscode-editor-font-weight`：编辑器字重（来自 `editor.fontWeight` 设置）。
> - `--vscode-editor-font-size`：编辑器字号（来自 `editor.fontSize` 设置）。

**推荐的做法：直接使用 CSS 变量，而不是按三类主题分别写颜色。** 用 CSS 变量时，用户换成任何主题，Webview 都会自动跟着变，而且和 VS Code 的颜色完全一致：

```css
body {
  background-color: var(--vscode-editor-background);
  color: var(--vscode-editor-foreground);
  font-family: var(--vscode-font-family);   /* 界面字体 */
}

button {
  background: var(--vscode-button-background);
  color: var(--vscode-button-foreground);
}

button:hover {
  background: var(--vscode-button-hoverBackground);
}
```

颜色 ID 中的大小写会保留，例如 `button.hoverBackground` 对应 `--vscode-button-hoverBackground`。

> 最后，在少数需要针对某一个主题编写 CSS 的特殊情况下，Webview 的 body 元素上有一个名为 `vscode-theme-id` 的 data 属性，存储了当前活动主题的 ID。这让你可以为 Webview 编写特定于某个主题的 CSS：

```css
body[data-vscode-theme-id="One Dark Pro"] {
    background: hotpink;
}
```

<a id="supported-media-formats"></a>
### 支持的媒体格式（Supported media formats）

> Webview 支持音频和视频，但并不是所有的媒体编解码器或媒体文件容器格式都受支持。
>
> Webview 中可以使用以下音频格式：
>
> - Wav
> - Mp3
> - Ogg
> - Flac
>
> Webview 中可以使用以下视频格式：
>
> - H.264
> - VP8
>
> 对于视频文件，要确保视频轨和音频轨的媒体格式都受支持。例如，很多 `.mp4` 文件的视频使用 `H.264`，音频使用 `AAC`。VS Code 能播放 `mp4` 的视频部分，但由于不支持 `AAC` 音频，所以不会有声音。你需要改用 `mp3` 作为音频轨。

| 类型 | 支持的格式 |
|---|---|
| 音频 | Wav、Mp3、Ogg、Flac |
| 视频 | H.264、VP8 |
| 不支持（常见的坑） | AAC 音频：很多 `.mp4` 文件用的就是 AAC，播放时有画面没声音 |

“容器”和“编解码器”的区别：`.mp4` 是容器（一个文件盒子），里面装的视频轨和音频轨各自用某种编码格式。所以同样是 `.mp4` 文件，能不能完整播放取决于里面用的编码。

<a id="context-menus"></a>
### 上下文菜单（Context menus）

> 高级的 Webview 可以自定义用户在 Webview 中右键时显示的上下文菜单。这是通过[贡献点](../references/contribution-points.md)实现的，方式与 VS Code 的普通上下文菜单类似，所以自定义菜单能和编辑器的其他部分融为一体。Webview 还可以为不同的区域显示不同的上下文菜单。
>
> 要给 Webview 添加新的上下文菜单项，首先在 `menus` 下新的 `webview/context` 部分中添加一个条目。每条贡献都包含一个 `command`（菜单项的标题也来自这个命令）和一个 `when` 子句。[when 子句](../references/when-clause-contexts.md)中应该包含 `webviewId == 'YOUR_WEBVIEW_VIEW_TYPE'`，确保上下文菜单只作用于你的扩展的 Webview：

```jsonc
"contributes": {
  "menus": {
    "webview/context": [
      {
        "command": "catCoding.yarn",
        "when": "webviewId == 'catCoding'"
      },
      {
        "command": "catCoding.insertLion",
        "when": "webviewId == 'catCoding' && webviewSection == 'editor'"
      }
    ]
  },
  "commands": [
    {
      "command": "catCoding.yarn",
      "title": "Yarn 🧶",
      "category": "Cat Coding"
    },
    {
      "command": "catCoding.insertLion",
      "title": "Insert 🦁",
      "category": "Cat Coding"
    },
    ...
  ]
}
```

注意 `webviewId` 的值是创建面板时传入的 **viewType**（这里是 `'catCoding'`），而不是面板标题。

> 在 Webview 内部，还可以用 `data-vscode-context` [data 属性](https://developer.mozilla.org/docs/Learn/HTML/Howto/Use_data_attributes)（或者在 JavaScript 中用 `dataset.vscodeContext`）为 HTML 的特定区域设置上下文。`data-vscode-context` 的值是一个 JSON 对象，指定用户右键这个元素时要设置的上下文。最终的上下文是从文档根节点一直到被点击的元素逐层确定的。
>
> 以下面的 HTML 为例：

```html
<div class="main" data-vscode-context='{"webviewSection": "main", "mouseCount": 4}'>
  <h1>Cat Coding</h1>

  <textarea data-vscode-context='{"webviewSection": "editor", "preventDefaultContextMenuItems": true}'></textarea>
</div>
```

> 如果用户右键点击 `textarea`，会设置以下上下文：
>
> - `webviewSection == 'editor'`：覆盖了父元素中的 `webviewSection`。
> - `mouseCount == 4`：继承自父元素。
> - `preventDefaultContextMenuItems == true`：这是一个特殊的上下文，会隐藏 VS Code 通常添加到 Webview 上下文菜单中的“复制”和“粘贴”条目。

**上下文的合并规则**和 CSS 的继承类似：从外层元素到被点击的元素，逐层合并 JSON；同名的键，内层覆盖外层。

```text
<div>       {"webviewSection": "main",   "mouseCount": 4}
  <textarea>{"webviewSection": "editor", "preventDefaultContextMenuItems": true}

右键 textarea 时，合并结果：
  webviewSection = "editor"                 ← 内层覆盖外层
  mouseCount = 4                            ← 继承外层
  preventDefaultContextMenuItems = true     ← 内层新增
```

这些键可以直接在 `menus` 的 `when` 子句中使用。所以在上面的配置中，“Insert 🦁” 只在右键 `textarea` 时出现（因为它要求 `webviewSection == 'editor'`），而 “Yarn 🧶” 在整个 Webview 中都会出现。

> 如果用户在 `<textarea>` 内右键，会看到：

![Webview 中显示的自定义上下文菜单](images/webview/webview-context-menus.png)

> 有时，在左键（主按钮）点击时显示菜单也很有用，例如在拆分按钮（split button）上显示菜单。你可以在 `onClick` 事件中派发 `contextmenu` 事件来实现：

```html
<button data-vscode-context='{"preventDefaultContextMenuItems": true }' onClick='((e) => {
        e.preventDefault();
        e.target.dispatchEvent(new MouseEvent("contextmenu", { bubbles: true, clientX: e.clientX, clientY: e.clientY }));
        e.stopPropagation();
    })(event)'>Create</button>
```

![带有菜单的拆分按钮](images/webview/webview-split-button-menu.png)

原理是：左键点击按钮时，用代码模拟一次“右键”（派发 `contextmenu` 事件），VS Code 就会在点击的位置显示上下文菜单。注意这段 HTML 用了内联的 `onClick` 脚本，在启用了内容安全策略（见后文）的 Webview 中，内联脚本会被禁止，需要改成在外部脚本文件中用 `addEventListener` 绑定。

右键菜单的命令被执行时，处理函数会收到一个参数，包含右键位置合并后的上下文对象，可以据此判断用户是在哪个区域右键的。

---

<a id="scripts-and-message-passing"></a>
## 脚本与消息传递（Scripts and message passing）

> Webview 就像 iframe 一样，这意味着它们也可以运行脚本。Webview 中的 JavaScript 默认是禁用的，但只需传入 `enableScripts: true` 选项，就能轻松重新启用。
>
> 我们用一个脚本来添加一个计数器，记录猫写了多少行源代码。运行一个基本的脚本很简单，但请注意，这个示例只是为了演示。在实践中，你的 Webview 应该始终使用[内容安全策略](#content-security-policy)禁用内联脚本：

```ts
import * as path from 'path';
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      const panel = vscode.window.createWebviewPanel(
        'catCoding',
        'Cat Coding',
        vscode.ViewColumn.One,
        {
          // 在 Webview 中启用脚本
          enableScripts: true
        }
      );

      panel.webview.html = getWebviewContent();
    })
  );
}

function getWebviewContent() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cat Coding</title>
</head>
<body>
    <img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" width="300" />
    <h1 id="lines-of-code-counter">0</h1>

    <script>
        const counter = document.getElementById('lines-of-code-counter');

        let count = 0;
        setInterval(() => {
            counter.textContent = count++;
        }, 100);
    </script>
</body>
</html>`;
}
```

![在 Webview 中运行的脚本](images/webview/scripts-basic.gif)

动图中，猫的下方出现了一个飞快增长的数字。

> 哇！真是一只高产的猫。
>
> Webview 脚本几乎可以做普通网页上的脚本能做的任何事情。不过请记住，Webview 存在于自己的上下文中，所以 Webview 中的脚本无法访问 VS Code API。这正是消息传递的用武之地！

回顾本篇开头的图：脚本运行在 Webview 这一侧，`vscode.window.showInformationMessage` 之类的 API 在扩展那一侧。要让两边协作，就要靠消息传递：

| 方向 | 发送 | 接收 |
|---|---|---|
| 扩展 → Webview | 扩展中：`panel.webview.postMessage(数据)` | Webview 中：`window.addEventListener('message', e => e.data)` |
| Webview → 扩展 | Webview 中：`acquireVsCodeApi().postMessage(数据)` | 扩展中：`panel.webview.onDidReceiveMessage(数据 => ...)` |

<a id="passing-messages-from-an-extension-to-a-webview"></a>
### 从扩展向 Webview 传递消息（Passing messages from an extension to a webview）

> 扩展可以使用 `webview.postMessage()` 向它的 Webview 发送数据。这个方法可以发送任何可以 JSON 序列化的数据。Webview 内部通过标准的 `message` 事件接收消息。
>
> 为了演示这一点，我们给 **Cat Coding** 添加一个新命令，指示当前正在写代码的猫重构它的代码（从而减少总行数）。新的 `catCoding.doRefactor` 命令使用 `postMessage` 把指令发送给当前的 Webview，Webview 内部则用 `window.addEventListener('message', event => { ... })` 处理这条消息：

```ts
export function activate(context: vscode.ExtensionContext) {
  // 只允许存在一个写代码的猫
  let currentPanel: vscode.WebviewPanel | undefined = undefined;

  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      if (currentPanel) {
        currentPanel.reveal(vscode.ViewColumn.One);
      } else {
        currentPanel = vscode.window.createWebviewPanel(
          'catCoding',
          'Cat Coding',
          vscode.ViewColumn.One,
          {
            enableScripts: true
          }
        );
        currentPanel.webview.html = getWebviewContent();
        currentPanel.onDidDispose(
          () => {
            currentPanel = undefined;
          },
          undefined,
          context.subscriptions
        );
      }
    })
  );

  // 新增的命令
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.doRefactor', () => {
      if (!currentPanel) {
        return;
      }

      // 向 Webview 发送一条消息。
      // 可以发送任何可 JSON 序列化的数据。
      currentPanel.webview.postMessage({ command: 'refactor' });
    })
  );
}

function getWebviewContent() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cat Coding</title>
</head>
<body>
    <img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" width="300" />
    <h1 id="lines-of-code-counter">0</h1>

    <script>
        const counter = document.getElementById('lines-of-code-counter');

        let count = 0;
        setInterval(() => {
            counter.textContent = count++;
        }, 100);

        // 在 Webview 内部处理消息
        window.addEventListener('message', event => {

            const message = event.data; // 扩展发送过来的 JSON 数据

            switch (message.command) {
                case 'refactor':
                    count = Math.ceil(count * 0.5);
                    counter.textContent = count;
                    break;
            }
        });
    </script>
</body>
</html>`;
}
```

![向 Webview 传递消息](images/webview/scripts-extension_to_webview.gif)

动图中，在命令面板中执行重构命令后，计数器的数字减半。

**消息格式的约定：** 消息本身没有固定格式，可以是任何能 JSON 序列化的数据。但习惯上会用一个对象，带一个 `command`（或 `type`）字段说明消息的类型，再附带数据。接收方根据类型字段用 `switch` 分别处理。这样消息种类多了也不会乱。

**几点注意：**

- `postMessage` 返回一个 Promise，结果为 `true` 表示消息已投递。但如果 Webview 处于隐藏状态（且没有开启后文介绍的 `retainContextWhenHidden`），页面已经被销毁，消息会丢失。
- 刚设置完 `html` 就立即发送消息，页面里的脚本可能还没加载完、还没开始监听，消息同样会丢失。可靠的做法是：让 Webview 脚本加载完成后先给扩展发一条“我准备好了”的消息，扩展收到后再发送数据。

<a id="passing-messages-from-a-webview-to-an-extension"></a>
### 从 Webview 向扩展传递消息（Passing messages from a webview to an extension）

> Webview 也可以把消息传回给扩展。这是通过 Webview 内部一个特殊的 VS Code API 对象上的 `postMessage` 函数实现的。要获取这个 VS Code API 对象，需要在 Webview 内部调用 `acquireVsCodeApi`。这个函数在每个会话中只能调用一次。你必须保存好这个方法返回的 VS Code API 实例，并把它交给其他需要使用它的函数。
>
> 我们可以在 **Cat Coding** Webview 中使用 VS Code API 和 `postMessage`，在猫的代码中出现 bug 时通知扩展：

```js
export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      const panel = vscode.window.createWebviewPanel(
        'catCoding',
        'Cat Coding',
        vscode.ViewColumn.One,
        {
          enableScripts: true
        }
      );

      panel.webview.html = getWebviewContent();

      // 处理来自 Webview 的消息
      panel.webview.onDidReceiveMessage(
        message => {
          switch (message.command) {
            case 'alert':
              vscode.window.showErrorMessage(message.text);
              return;
          }
        },
        undefined,
        context.subscriptions
      );
    })
  );
}

function getWebviewContent() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cat Coding</title>
</head>
<body>
    <img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" width="300" />
    <h1 id="lines-of-code-counter">0</h1>

    <script>
        (function() {
            const vscode = acquireVsCodeApi();
            const counter = document.getElementById('lines-of-code-counter');

            let count = 0;
            setInterval(() => {
                counter.textContent = count++;

                // 当猫写出 bug 时通知扩展
                if (Math.random() < 0.001 * count) {
                    vscode.postMessage({
                        command: 'alert',
                        text: '🐛  on line ' + count
                    })
                }
            }, 100);
        }())
    </script>
</body>
</html>`;
}
```

![从 Webview 向扩展传递消息](images/webview/scripts-webview_to_extension.gif)

动图中，计数器增长的过程中，右下角不时弹出 “🐛 on line xx” 的错误通知。弹出通知的是扩展（调用了 `showErrorMessage`），触发它的是 Webview 中的脚本。

（这段代码块原文标注为 `js`，但内容实际上是 TypeScript。）

> 出于安全考虑，你必须让 VS Code API 对象保持私有，确保它永远不会泄露到全局作用域中。

**代码中 `(function() { ... }())` 的作用：** 这是“立即执行函数”。把代码包在一个函数里立即执行，里面声明的 `vscode` 变量就只存在于这个函数内部，不会成为全局变量。这正是上面那句安全提示的要求：如果 `vscode` 对象挂在全局（比如 `window.vscode`），Webview 中加载的任何第三方脚本都能拿到它，冒充你的页面给扩展发消息。

`acquireVsCodeApi()` 返回的对象只有三个方法：

| 方法 | 作用 |
|---|---|
| `postMessage(msg)` | 向扩展发送消息 |
| `getState()` | 读取保存的状态（见后文[持久化](#persistence)） |
| `setState(state)` | 保存状态 |

记住它**只能调用一次**，第二次调用会报错。如果脚本分成多个文件，要在入口处调用一次，再把对象传给其他模块使用。

**一个完整的“双向通信”例子：** Webview 中有个按钮，点击后让扩展读取当前文件名，再显示回页面上：

```ts
// 扩展侧
panel.webview.onDidReceiveMessage(message => {
  if (message.type === 'getFileName') {
    const name = vscode.window.activeTextEditor?.document.fileName ?? '（没有打开的文件）';
    panel.webview.postMessage({ type: 'fileName', value: name });
  }
}, undefined, context.subscriptions);
```

```js
// Webview 侧（写在外部脚本文件中）
const vscode = acquireVsCodeApi();

document.getElementById('btn').addEventListener('click', () => {
  vscode.postMessage({ type: 'getFileName' });           // 1. 请求
});

window.addEventListener('message', event => {
  const message = event.data;
  if (message.type === 'fileName') {                      // 2. 收到回复
    document.getElementById('output').textContent = message.value;
  }
});
```

<a id="using-web-workers"></a>
### 使用 Web Worker（Using Web Workers）

> Webview 中支持 [Web Worker](https://developer.mozilla.org/docs/Web/API/Web_Workers_API/Using_web_workers)，但有几个重要的限制需要注意。
>
> 首先，Worker 只能通过 `data:` 或 `blob:` URI 加载。你不能直接从扩展的文件夹中加载 Worker。
>
> 如果确实需要从扩展中的 JavaScript 文件加载 Worker 代码，可以尝试使用 `fetch`：

```js
const workerSource = 'absolute/path/to/worker.js';

fetch(workerSource)
  .then(result => result.blob())
  .then(blob => {
    const blobUrl = URL.createObjectURL(blob)
    new Worker(blobUrl);
  });
```

**Web Worker 是什么？** 它让网页可以在后台线程中运行 JavaScript，执行耗时的计算时不会卡住页面。

这段代码的思路是：先用 `fetch` 把 worker 脚本的内容下载下来，转成 `blob`，再用 `blob:` 地址创建 Worker，绕过“不能直接从扩展文件夹加载”的限制。代码中的 `workerSource` 是一个占位写法，实际应该是扩展侧用 `asWebviewUri` 转换后传给页面的地址。

> Worker 脚本也不支持用 `importScripts` 或 `import(...)` 导入源代码。如果你的 Worker 需要动态加载代码，可以尝试使用 [webpack](https://webpack.js.org) 之类的打包工具，把 Worker 脚本打包成一个单独的文件。
>
> 使用 `webpack` 时，可以用 `LimitChunkCountPlugin` 强制把编译后的 Worker JavaScript 打包成单个文件：

```js
const path = require('path');
const webpack = require('webpack');

module.exports = {
  target: 'webworker',
  entry: './worker/src/index.js',
  output: {
    filename: 'worker.js',
    path: path.resolve(__dirname, 'media'),
  },
  plugins: [
    new webpack.optimize.LimitChunkCountPlugin({
      maxChunks: 1,   // 最多只生成一个代码块，即所有代码打包进一个文件
    }),
  ],
};
```

打包工具的用法见 [打包扩展](../working-with-extensions/bundling-extension.md)。

---

<a id="security"></a>
<a id="security"></a>
## 安全（Security）

> 和任何网页一样，创建 Webview 时，必须遵循一些基本的安全最佳实践。

**为什么 Webview 特别需要注意安全？** Webview 里显示的内容常常来自用户的工作区，比如文件内容、文件名。如果某个恶意文件里藏着一段 `<script>`，而你又直接把文件内容拼进了 HTML，这段脚本就会在 Webview 中运行，进而可以通过消息调用你扩展提供的功能。下面这几条规则就是用来防止这种情况的。

<a id="limit-capabilities"></a>
### 限制能力（Limit capabilities）

> Webview 应该只拥有它所需要的最少能力。例如，如果你的 Webview 不需要运行脚本，就不要设置 `enableScripts: true`。如果你的 Webview 不需要从用户的工作区加载资源，就把 `localResourceRoots` 设为 `[vscode.Uri.file(extensionContext.extensionPath)]`，甚至设为 `[]`，禁止访问所有本地资源。

`WebviewOptions` 中与能力相关的选项（以 `@types/vscode` 1.140 为准）：

| 选项 | 默认值 | 作用 |
|---|---|---|
| `enableScripts` | `false` | 是否允许运行 JavaScript |
| `enableForms` | 启用脚本时默认允许 | 是否允许提交表单 |
| `enableCommandUris` | `false` | 是否允许 `command:` 链接，也可以是允许的命令 ID 数组（见 [命令指南](./command.md#command-uris)） |
| `localResourceRoots` | 扩展目录 + 工作区 | 允许加载哪些本地资源 |
| `portMapping` | 无 | 把 Webview 中访问的 localhost 端口映射到扩展所在机器的端口（用于远程开发场景） |

`createWebviewPanel` 的 `options` 参数还可以包含面板专属的选项：`enableFindWidget`（启用 `Ctrl+F` 查找框）和 `retainContextWhenHidden`（见后文）。

<a id="content-security-policy"></a>
### 内容安全策略（Content security policy）

> [内容安全策略](https://developers.google.com/web/fundamentals/security/csp/)（CSP）进一步限制了 Webview 中可以加载和执行的内容。例如，内容安全策略可以确保只有一组允许的脚本能在 Webview 中运行，甚至可以要求 Webview 只通过 `https` 加载图片。
>
> 要添加内容安全策略，在 Webview 的 `<head>` 顶部放置一条 `<meta http-equiv="Content-Security-Policy">` 指令：

```ts
function getWebviewContent() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">

    <meta http-equiv="Content-Security-Policy" content="default-src 'none';">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Cat Coding</title>
</head>
<body>
    ...
</body>
</html>`;
}
```

> `default-src 'none';` 这条策略会禁止所有内容。然后，我们可以再开启扩展正常运行所需的最少内容。下面是一条允许加载本地脚本和样式表、并允许通过 `https` 加载图片的内容安全策略：

```html
<meta
  http-equiv="Content-Security-Policy"
  content="default-src 'none'; img-src ${webview.cspSource} https:; script-src ${webview.cspSource}; style-src ${webview.cspSource};"
/>
```

> `${webview.cspSource}` 这个值是一个占位符，它的值来自 Webview 对象本身。完整的使用示例请参阅 [Webview 示例](https://github.com/microsoft/vscode-extension-samples/blob/main/webview-sample)。
>
> 这条内容安全策略还隐式地禁用了内联脚本和内联样式。最佳实践是把所有内联样式和脚本都提取到外部文件中，这样不用放宽内容安全策略，也能正确加载它们。

**逐项解读这条 CSP：**

| 指令 | 含义 |
|---|---|
| `default-src 'none'` | 默认禁止一切，下面没有单独放开的类型都不能加载 |
| `img-src ${webview.cspSource} https:` | 图片：允许加载扩展的本地资源（经过 `asWebviewUri` 转换的地址），以及任意 `https` 地址 |
| `script-src ${webview.cspSource}` | 脚本：只允许加载扩展的本地脚本文件，内联的 `<script>...</script>` 会被禁止 |
| `style-src ${webview.cspSource}` | 样式：只允许加载扩展的本地样式文件，内联的 `style="..."` 和 `<style>` 会被禁止 |

**`webview.cspSource`** 是 `Webview` 对象上的一个只读属性，代表“经过 `asWebviewUri` 转换的本地资源”的来源。它是在扩展代码（TypeScript）中、拼接 HTML 字符串时插入的，所以 `${webview.cspSource}` 是模板字符串里的变量，不是 HTML 的语法。

**把脚本提取到外部文件后，完整的写法：**

```ts
function getWebviewContent(webview: vscode.Webview, extensionUri: vscode.Uri) {
  // 把扩展中的脚本和样式文件转换成 Webview 能用的地址
  const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'main.js'));
  const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'main.css'));

  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy"
          content="default-src 'none'; img-src ${webview.cspSource} https:; script-src ${webview.cspSource}; style-src ${webview.cspSource};">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="${styleUri}" rel="stylesheet">
    <title>Cat Coding</title>
</head>
<body>
    <h1 id="lines-of-code-counter">0</h1>
    <script src="${scriptUri}"></script>
</body>
</html>`;
}
```

官方 Webview 示例中还用到了 **nonce**（一次性随机数）：每次生成 HTML 时随机生成一个字符串，写进 CSP 的 `script-src 'nonce-随机串'`，同时给 `<script>` 标签加上 `nonce="随机串"`。这样只有带着正确随机串的脚本才能运行，安全性更高。具体写法可参考上面链接的示例代码。

**调试提示：** 设置 CSP 后，被拦截的资源会在开发者工具的 Console 中显示 `Refused to load ...` 之类的错误。页面空白、样式丢失时，先去看这里。

<a id="only-load-content-over-https"></a>
### 只通过 https 加载内容（Only load content over https）

> 如果你的 Webview 允许加载外部资源，强烈建议只允许通过 `https` 加载这些资源，而不是通过 http。上面的内容安全策略示例已经做到了这一点：它只允许通过 `https:` 加载图片。

<a id="sanitize-all-user-input"></a>
### 清理所有用户输入（Sanitize all user input）

> 就像对待普通网页一样，在为 Webview 构建 HTML 时，必须清理所有用户输入。如果没有正确清理输入，就可能导致内容注入，让用户面临安全风险。
>
> 必须清理的值包括：
>
> - 文件内容。
> - 文件和文件夹的路径。
> - 用户设置和工作区设置。
>
> 可以考虑使用辅助库来构建 HTML 字符串，或者至少确保来自用户工作区的所有内容都经过了正确的清理。
>
> 永远不要只依赖清理来保证安全。请确保同时遵循其他安全最佳实践，例如设置[内容安全策略](#content-security-policy)，把任何潜在的内容注入的影响降到最低。

“清理”最基本的做法是**转义 HTML 特殊字符**，让它们显示成文字，而不是被当作 HTML 标签解析：

```ts
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// 拼接文件名时先转义
panel.webview.html = `...<h1>${escapeHtml(fileName)}</h1>...`;
```

更好的做法是：HTML 只放固定的页面结构，**动态数据通过 `postMessage` 发给页面**，页面中用 `textContent`（而不是 `innerHTML`）把数据放进 DOM。`textContent` 永远把内容当作纯文本，从根本上避免了注入。

---

<a id="persistence"></a>
<a id="persistence"></a>
## 持久化（Persistence）

> 在标准的 Webview [生命周期](#lifecycle)中，Webview 由 `createWebviewPanel` 创建，在用户关闭它或调用 `.dispose()` 时被销毁。然而，Webview 的**内容**是在 Webview 变为可见时创建、在 Webview 被移到后台时销毁的。Webview 被移到后台标签页时，Webview 内部的所有状态都会丢失。
>
> 解决这个问题的最佳方式是让你的 Webview 无状态。使用[消息传递](#passing-messages-from-a-webview-to-an-extension)保存 Webview 的状态，然后在 Webview 重新可见时恢复状态。

这里要区分两个“生命周期”：

| | 何时创建 | 何时销毁 |
|---|---|---|
| Webview **面板**（`WebviewPanel` 对象） | `createWebviewPanel` | 用户关闭，或调用 `dispose()` |
| Webview **内容**（页面和脚本状态） | 面板变为可见 | 面板被切到后台 |

也就是说，用户只是切换了一下标签页，页面就会被销毁、重新加载，计数器归零，输入框里的内容也没了。下面介绍三种解决方案，按推荐程度排列。

### getState 和 setState

> Webview 中运行的脚本可以使用 `getState` 和 `setState` 方法保存和恢复一个可 JSON 序列化的状态对象。即使 Webview 面板被隐藏、Webview 内容本身被销毁，这个状态依然会保留。当 Webview 面板被销毁时，状态也随之销毁。

```js
// 在 Webview 脚本中
const vscode = acquireVsCodeApi();

const counter = document.getElementById('lines-of-code-counter');

// 检查是否有可以恢复的旧状态
const previousState = vscode.getState();
let count = previousState ? previousState.count : 0;
counter.textContent = count;

setInterval(() => {
  counter.textContent = count++;
  // 更新保存的状态
  vscode.setState({ count });
}, 100);
```

> `getState` 和 `setState` 是持久化状态的首选方式，因为它们的性能开销比 `retainContextWhenHidden` 低得多。

**思路：** 页面每次状态变化时都调用 `setState` 存一份；页面重新加载时，先调用 `getState` 看看有没有存过的状态，有就从那里继续。状态由 VS Code 帮你保管，页面销毁了它也还在。

<a id="serialization"></a>
### 序列化（Serialization）

> 通过实现 `WebviewPanelSerializer`，你的 Webview 可以在 VS Code 重启后自动恢复。序列化建立在 `getState` 和 `setState` 的基础之上，并且只有当你的扩展为 Webview 注册了 `WebviewPanelSerializer` 时才会启用。

`getState` / `setState` 解决的是“切换标签页”，序列化解决的是“**关闭 VS Code 再打开**”：不注册序列化器的话，重启后 Webview 标签页就消失了；注册之后，VS Code 会把标签页恢复到原来的位置，并把保存的状态交给你。

> 要让我们写代码的猫在 VS Code 重启后依然存在，首先在扩展的 `package.json` 中添加 `onWebviewPanel` 激活事件：

```json
"activationEvents": [
    ...,
    "onWebviewPanel:catCoding"
]
```

> 这个激活事件确保 VS Code 需要恢复 viewType 为 `catCoding` 的 Webview 时，我们的扩展会被激活。

这一步很关键：VS Code 重启时，扩展还没有被激活。如果没有这个激活事件，VS Code 想恢复 Webview 时找不到能处理它的扩展。`onWebviewPanel:` 后面跟的是 viewType。

> 然后，在扩展的 `activate` 方法中，调用 `registerWebviewPanelSerializer` 注册一个新的 `WebviewPanelSerializer`。`WebviewPanelSerializer` 负责根据持久化的状态恢复 Webview 的内容。这个状态就是 Webview 内容使用 `setState` 设置的那个 JSON 数据。

```ts
export function activate(context: vscode.ExtensionContext) {
  // 常规的初始化……

  // 并确保为我们的 Webview 类型注册一个序列化器
  vscode.window.registerWebviewPanelSerializer('catCoding', new CatCodingSerializer());
}

class CatCodingSerializer implements vscode.WebviewPanelSerializer {
  async deserializeWebviewPanel(webviewPanel: vscode.WebviewPanel, state: any) {
    // `state` 就是在 Webview 中用 `setState` 保存的状态
    console.log(`Got state: ${state}`);

    // 恢复 Webview 的内容。
    //
    // 一定要保存好这里传入的 `webviewPanel`，
    // 并且重新为它添加需要的事件监听。
    webviewPanel.webview.html = getWebviewContent();
  }
}
```

> 现在，如果你在打开 Cat Coding 面板的情况下重启 VS Code，面板会自动恢复到同一个编辑器位置。

**恢复时的注意事项：**

- `deserializeWebviewPanel` 收到的 `webviewPanel` 是 VS Code 重新创建的面板。原来在 `createWebviewPanel` 之后做的事（设置 `html`、监听 `onDidReceiveMessage`、`onDidDispose`、保存到 `currentPanel` 变量等），这里都要再做一遍。所以实际开发中，通常把这些初始化逻辑抽成一个函数，新建和恢复两处共用。
- 恢复的面板需要用和原来相同的 `options`（比如 `enableScripts`）。恢复时可以通过 `webviewPanel.webview.options = {...}` 重新设置。
- 示例中的 `console.log(\`Got state: ${state}\`)` 会把对象打印成 `[object Object]`，想看内容可以用 `JSON.stringify(state)`。

<a id="retainContextWhenHidden"></a>
### retainContextWhenHidden

> 对于界面非常复杂、或者状态无法快速保存和恢复的 Webview，可以改用 `retainContextWhenHidden` 选项。这个选项会让 Webview 即使不在前台时，也把内容保留在隐藏状态中。
>
> 虽然 **Cat Coding** 的状态很难称得上复杂，但我们还是来试试启用 `retainContextWhenHidden`，看看这个选项如何改变 Webview 的行为：

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('catCoding.start', () => {
      const panel = vscode.window.createWebviewPanel(
        'catCoding',
        'Cat Coding',
        vscode.ViewColumn.One,
        {
          enableScripts: true,
          retainContextWhenHidden: true
        }
      );
      panel.webview.html = getWebviewContent();
    })
  );
}

function getWebviewContent() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cat Coding</title>
</head>
<body>
    <img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" width="300" />
    <h1 id="lines-of-code-counter">0</h1>

    <script>
        const counter = document.getElementById('lines-of-code-counter');

        let count = 0;
        setInterval(() => {
            counter.textContent = count++;
        }, 100);
    </script>
</body>
</html>`;
}
```

![retainContextWhenHidden 演示](images/webview/retainContextWhenHidden.gif)

动图中，切换到其他标签页再切回来，计数器从离开时的数字继续增长，没有归零。

> 注意，现在 Webview 被隐藏后再恢复时，计数器不会被重置了。不需要任何额外的代码！启用 `retainContextWhenHidden` 后，Webview 的行为就像浏览器中的后台标签页：即使标签页不处于活动状态或不可见，脚本和其他动态内容也会继续运行。启用 `retainContextWhenHidden` 后，你还可以向隐藏的 Webview 发送消息。
>
> 虽然 `retainContextWhenHidden` 看起来很有吸引力，但请记住，它的内存开销很高，只应在其他持久化技术都行不通时才使用。

**三种方案的对比：**

| 方案 | 解决的问题 | 开销 | 需要写的代码 | 推荐程度 |
|---|---|---|---|---|
| `getState` / `setState` | 切换标签页后恢复状态 | 低 | 页面中保存、恢复状态 | 首选 |
| `WebviewPanelSerializer` | VS Code 重启后恢复面板 | 低 | 激活事件 + 序列化器（配合 `setState` 使用） | 需要“重启后还在”时使用 |
| `retainContextWhenHidden` | 切换标签页后页面完全不重新加载 | **高**（隐藏的页面一直占用内存） | 几乎不用写 | 只在状态复杂、无法保存时才用 |

---

<a id="accessibility"></a>
## 无障碍（Accessibility）

> 当用户使用屏幕阅读器操作 VS Code 时，Webview 的 body 元素上会添加 `vscode-using-screen-reader` 这个 class。此外，当用户表示希望减少窗口中的动画效果时，文档的 body 元素上会添加 `vscode-reduce-motion` 这个 class。通过检查这些 class 并相应地调整渲染方式，你的 Webview 内容能更好地照顾用户的偏好。

例如，用户开启了“减少动画”时，关闭页面中的过渡动画：

```css
body.vscode-reduce-motion * {
  transition: none !important;
  animation: none !important;
}
```

| body 上的 class | 含义 |
|---|---|
| `vscode-light` / `vscode-dark` / `vscode-high-contrast` | 当前主题的类型（见[主题适配](#theming-webview-content)） |
| `vscode-using-screen-reader` | 用户正在使用屏幕阅读器 |
| `vscode-reduce-motion` | 用户希望减少动画 |

---

<a id="next-steps"></a>
## 下一步（Next steps）

> 如果你想进一步了解 VS Code 的扩展能力，可以看看这些主题：
>
> - [扩展 API](../index.md)：了解完整的 VS Code 扩展 API。
> - [扩展能力](../extension-capabilities/overview.md)：看看扩展 VS Code 的其他方式。

如果要在侧边栏中使用 Webview，或者为某类文件做可视化编辑器，接下来可以阅读 [自定义编辑器](./custom-editors.md)，以及 [Webview 视图示例](https://github.com/microsoft/vscode-extension-samples/tree/main/webview-view-sample)。

---

## 本篇小结

```text
核心模型：扩展（能用 API，不能碰 DOM） ⇄ 消息传递 ⇄ Webview（能碰 DOM，不能用 API）

创建与显示
  createWebviewPanel(viewType, title, column, options)
  webview.html = 完整的 HTML 文档（每次赋值 = 整页刷新，脚本状态丢失）
  单例面板：保存引用 + onDidDispose 中重置；reveal() 带到前台

本地资源
  asWebviewUri() 转换地址；localResourceRoots 限制可访问的目录
  主题：body 上的 class + var(--vscode-xxx) CSS 变量

消息
  扩展 → 页面：webview.postMessage   / window.addEventListener('message')
  页面 → 扩展：acquireVsCodeApi().postMessage（只能调用一次，不要放到全局） / onDidReceiveMessage

安全
  最少能力（enableScripts 等按需开启）
  CSP：default-src 'none' + 按需放开 ${webview.cspSource}；脚本、样式放外部文件
  转义所有用户输入；动态数据用 postMessage + textContent

持久化
  getState/setState（首选） → Serializer（重启恢复） → retainContextWhenHidden（最后手段）

调试：在扩展开发宿主窗口执行 Developer: Toggle Developer Tools，Console 中切换到 active frame
```
