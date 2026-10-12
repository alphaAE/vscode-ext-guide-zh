# 扩展工作台（Extending Workbench）

> 原文：[Extending Workbench](https://code.visualstudio.com/api/extension-capabilities/extending-workbench)
> 源文件：`microsoft/vscode-docs` → `api/extension-capabilities/extending-workbench.md`（DateApproved: 10/7/2026）

> “工作台（Workbench）”指的是 VS Code 的整体界面，它包含以下界面部件：
>
> - 标题栏（Title Bar）
> - 活动栏（Activity Bar）
> - 侧边栏（Side Bar）
> - 面板（Panel）
> - 编辑器组（Editor Group）
> - 状态栏（Status Bar）

先认清这几个区域，后面的文档会反复提到它们的名字：

```text
┌──────────────────────────────────────────────────────────┐
│                       标题栏 Title Bar                    │
├────┬──────────────┬──────────────────────────────────────┤
│    │              │                                      │
│ 活 │   侧边栏     │           编辑器组 Editor Group        │
│ 动 │  Side Bar    │      （打开的文件，可以左右分屏）        │
│ 栏 │              │                                      │
│    │ （资源管理器、 ├──────────────────────────────────────┤
│Act-│  搜索、源代码 │            面板 Panel                 │
│ivi-│  管理等）     │   （终端、输出、问题、调试控制台）       │
│ty  │              │                                      │
│Bar │              │                                      │
├────┴──────────────┴──────────────────────────────────────┤
│                       状态栏 Status Bar                   │
└──────────────────────────────────────────────────────────┘
```

- **活动栏**：最左侧那一列图标。点击图标，切换侧边栏中显示的内容。
- **侧边栏**：显示资源管理器、搜索、源代码管理等内容。
- **编辑器组**：编辑文件的区域。可以分成多个组并排显示，每组里有多个标签页。
- **面板**：底部区域，放终端、输出、问题、调试控制台。
- **状态栏**：最底部的一条，显示当前分支、行列号、文件编码等信息。

> VS Code 提供了多种 API，让你可以往工作台中添加自己的部件。例如下图中：

![扩展向工作台添加的四种部件：视图容器、树视图、Webview、状态栏项](images/extending-workbench/workbench-contribution.png)

图中用红框标出了扩展添加的四个部件（截图是英文界面）：左侧活动栏中的 Azure 图标是**视图容器（Tree View Container）**，侧边栏底部的 NPM SCRIPTS 是**树视图（Tree View）**，右侧编辑器组中的 Markdown 预览是 **Webview**，底部状态栏中的 `-- NORMAL --` 是**状态栏项（Status Bar Item）**。

> - 活动栏：[Azure App Service 扩展](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azureappservice) 添加了一个[视图容器](#views-container)
> - 侧边栏：内置的 [NPM 扩展](https://github.com/microsoft/vscode/tree/main/extensions/npm) 在资源管理器视图中添加了一个[树视图](#tree-view)
> - 编辑器组：内置的 [Markdown 扩展](https://github.com/microsoft/vscode/tree/main/extensions/markdown-language-features) 在编辑器组中、其他编辑器的旁边添加了一个 [Webview](#webview)
> - 状态栏：[VSCodeVim 扩展](https://marketplace.visualstudio.com/items?itemName=vscodevim.vim) 在状态栏中添加了一个[状态栏项](#status-bar-item)

整理成表格：

| 区域 | 部件 | 图中的例子 | 用什么实现 |
|---|---|---|---|
| 活动栏 | 视图容器 | Azure 图标 | `contributes.viewsContainers` |
| 侧边栏 | 树视图 | NPM SCRIPTS 列表 | `contributes.views` + `TreeDataProvider` |
| 编辑器组 | Webview | Markdown 预览 | `window.createWebviewPanel` |
| 状态栏 | 状态栏项 | Vim 的 `-- NORMAL --` 模式提示 | `window.createStatusBarItem` |

有意思的是，图中的 NPM 和 Markdown 都是 **VS Code 内置的扩展**。VS Code 的很多自带功能本身就是用同一套扩展 API 实现的，所以这些 API 足以做出“原生”水准的功能。

---

<a id="views-container"></a>
## 视图容器（Views Container）

> 通过 [`contributes.viewsContainers`](../references/contribution-points.md#contributes.viewsContainers) 贡献点，你可以添加新的视图容器，它们会显示在五个内置视图容器的旁边。详情请参阅 [树视图](../extension-guides/tree-view.md) 一节。

**视图容器和视图的关系：** 视图容器是“装视图的盒子”，在活动栏上显示为一个图标；点击图标后，侧边栏中会显示这个容器里的所有视图。

```text
活动栏图标（视图容器）
   └─ 点击后，侧边栏中显示：
        ├─ 视图 1（可以折叠展开）
        ├─ 视图 2
        └─ ……
```

“五个内置视图容器”指的是活动栏上默认的资源管理器、搜索、源代码管理、运行和调试、扩展。

```jsonc
"contributes": {
  "viewsContainers": {
    "activitybar": [               // 放在活动栏上（也可以是 "panel"，放在底部面板中）
      {
        "id": "myContainer",       // 容器 ID，下面的 views 会用到
        "title": "My Tools",       // 鼠标悬停时显示的名字
        "icon": "media/icon.svg"   // 活动栏上的图标
      }
    ]
  }
}
```

---

<a id="tree-view"></a>
## 树视图（Tree View）

> 通过 [`contributes.views`](../references/contribution-points.md#contributes.views) 贡献点，你可以添加新的视图，显示在任意一个视图容器中。详情请参阅 [树视图](../extension-guides/tree-view.md) 一节。

视图可以放进你自己创建的容器，也可以放进内置的容器（比如资源管理器）：

```jsonc
"contributes": {
  "views": {
    "myContainer": [                    // 放进上面创建的容器（键名就是容器的 id）
      { "id": "myTreeView", "name": "Items" }
    ],
    "explorer": [                       // 放进内置的资源管理器
      { "id": "myExplorerView", "name": "My Files" }
    ]
  }
}
```

这里同样体现了“声明 + 实现”：`package.json` 只声明了“这里有一个叫 Items 的视图”，**树里显示哪些条目**要在代码中实现一个 `TreeDataProvider` 来提供。具体写法在 [树视图指南](../extension-guides/tree-view.md) 中详细介绍。

---

<a id="webview"></a>
## Webview

> Webview 是用 HTML/CSS/JavaScript 构建的、高度可定制的视图。它显示在编辑器组区域中，和文本编辑器并排。详情请阅读 [Webview 指南](../extension-guides/webview.md)。

在 [扩展能力概览](./overview.md) 中讲过：Webview 最灵活，但成本也最高。能用树视图、快速选择等原生部件实现的，优先用原生部件。

另外，Webview 不只能显示在编辑器组中，也可以通过 `WebviewView` 显示在侧边栏或面板的视图里，这部分在 Webview 指南中介绍。

---

<a id="status-bar-item"></a>
## 状态栏项（Status Bar Item）

> 扩展可以创建自定义的 [`StatusBarItem`](https://code.visualstudio.com/api/references/vscode-api#StatusBarItem)，显示在状态栏中。状态栏项可以显示文字和图标，并在被点击时执行命令。
>
> - 显示文字和图标
> - 点击时执行命令
>
> 更多内容可以查看 [状态栏扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/statusbar-sample)。

状态栏项不需要在 `package.json` 中声明，直接在代码中创建：

```ts
const item = vscode.window.createStatusBarItem(
  vscode.StatusBarAlignment.Right,  // 显示在状态栏右侧（Left 为左侧）
  100                               // 优先级：数值越大，越靠左
);
item.text = '$(rocket) 已就绪';     // $(图标名) 会显示成内置图标
item.tooltip = '点击打招呼';
item.command = 'myExtension.sayHello';  // 点击时执行的命令
item.show();                            // 创建后默认是隐藏的，要调用 show() 才会显示

context.subscriptions.push(item);
```

几个要点：

- **`$(rocket)` 这种写法**叫 codicon，是 VS Code 内置的图标集。可用的图标名见 [标签中的图标](../references/icons-in-labels.md)。
- **创建后必须调用 `show()`**，否则不会显示。这是新手常见的“为什么不显示”的原因。
- **文字可以随时修改**：给 `item.text` 重新赋值，状态栏就会立即更新，常用来显示实时状态。
- 按 UX 规范，状态栏空间有限，内容要简短，一般只放一个图标加几个字。

---

## 本篇小结

| 想在哪里加东西 | 部件 | `package.json` 声明 | 代码实现 |
|---|---|---|---|
| 活动栏 | 视图容器 | `viewsContainers` | 不需要 |
| 侧边栏 / 面板 | 树视图 | `views` | `TreeDataProvider` 提供数据 |
| 编辑器组 | Webview | 不需要 | `window.createWebviewPanel` + HTML |
| 状态栏 | 状态栏项 | 不需要 | `window.createStatusBarItem` + `show()` |
