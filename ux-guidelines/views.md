# 视图（Views）

> 原文：[Views](https://code.visualstudio.com/api/ux-guidelines/views)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/views.md`（DateApproved: 10/7/2026）

> [视图](../references/contribution-points.md#contributes.views)是可以出现在侧边栏或面板中的内容容器。视图可以包含树视图、欢迎视图或 Webview 视图，还可以显示视图操作。用户也可以重新排列视图，或者把视图移到另一个视图容器中（例如从主侧边栏移到辅助侧边栏）。请限制创建的视图数量，因为其他扩展也可能向同一个视图容器做贡献。

**✔️ 应该做**

> - 尽可能使用已有的图标
> - 为语言文件使用文件图标
> - 使用树视图来显示数据
> - 为每个视图都添加一个图标（以防它被移到活动栏或辅助侧边栏，这两个地方都用图标来表示视图）
> - 尽量减少视图的数量
> - 尽量缩短名称的长度
> - 限制自定义 Webview 视图的使用

**❌ 不应该做**

> - 重复已有的功能
> - 把树节点用作单一操作的条目（例如点击时触发一个命令）
> - 在不必要的时候使用自定义的 Webview 视图
> - 用一个活动栏条目（视图容器）在编辑器中打开一个 Webview

![视图示例](images/examples/view.png)

> *这个示例使用树视图显示了一个由树视图条目组成的扁平列表。*

**几条规则的解释：**

| 规则 | 说明 |
|---|---|
| 为语言文件使用文件图标 | 如果树中的条目代表文件，就给 `TreeItem` 设置 `resourceUri`，它会自动使用用户当前文件图标主题中的图标，和资源管理器保持一致（见 [树视图](../extension-guides/tree-view.md)） |
| 每个视图都要有图标 | 视图被拖到活动栏或辅助侧边栏时，是用图标表示的；没有图标就只能显示一个通用的占位图标 |
| 不要把树节点当按钮用 | 树视图是用来**展示数据**的。如果一个节点点了只是“执行某个命令”，它应该是一个命令或视图标题栏上的按钮，而不是树中的一项 |
| 限制 Webview 视图 | 原因见 [Webview 指南](../extension-guides/webview.md#should-i-use-a-webview) |

---

<a id="view-locations"></a>
## 视图的位置（View Locations）

> 视图可以放在[已有的视图容器](../references/contribution-points.md#contributes.views)中，例如文件资源管理器、源代码管理（SCM）和调试视图容器。也可以通过活动栏，把视图添加到一个自定义的[视图容器](./views.md#view-containers)中。此外，视图还可以被添加到面板中的任何视图容器。它们也可以被拖到辅助侧边栏中。

![视图的位置](images/examples/view-locations.png)

| 位置 | 怎么放 |
|---|---|
| 已有的视图容器（资源管理器、源代码管理、运行和调试、测试） | `contributes.views` 中的键名用 `explorer`、`scm`、`debug`、`test` |
| 自定义的视图容器（活动栏） | 先用 `viewsContainers.activitybar` 创建容器 |
| 面板中的视图容器 | 先用 `viewsContainers.panel` 创建容器 |
| 辅助侧边栏 | 由用户拖入 |

具体写法见 [树视图](../extension-guides/tree-view.md#package-json-contribution)。如果你的视图和文件、源代码管理、调试等内置功能紧密相关，优先放进已有的容器，而不是新建一个。

---

<a id="view-containers"></a>
## 视图容器（View Containers）

> 顾名思义，视图容器是渲染视图的“父”容器。扩展可以向[活动栏](./activity-bar.md) / [主侧边栏](./sidebars.md)或面板贡献自定义的视图容器。用户可以把整个视图容器从活动栏拖到面板（反之亦然），也可以移动单个视图。

![视图容器的示例](images/examples/view-container.png)

> *这是一个放在活动栏 / 主侧边栏中的视图容器的示例*

![面板中的视图容器的示例](images/examples/view-container-panel.png)

> *这是一个放在面板中的视图容器的示例*

---

<a id="tree-views"></a>
## 树视图（Tree Views）

> 树视图是在视图中显示内容的一种强大而灵活的格式。扩展可以添加从简单的扁平列表到深度嵌套的树等各种内容。
>
> - 使用具有描述性的标签为条目提供上下文（如果适用）
> - 使用产品图标区分条目的类型（如果适用）

**❌ 不应该做**

> - 把树视图条目用作触发命令的按钮
> - 除非必要，避免深层嵌套。对于大多数情况，几层文件夹 / 条目是一个很好的平衡。
> - 为一个条目添加三个以上的操作

![树视图的示例](images/examples/tree-view.png)

“具有描述性的标签”可以利用 `TreeItem` 的 `description`（名称右侧的灰色文字），比如在依赖包名后面显示版本号（见 [树视图](../extension-guides/tree-view.md) 中的 Node Dependencies 示例）。“一个条目不超过三个操作”指的是 `view/item/context` 菜单中的行内按钮（`inline` 组），多了的放进右键菜单。

---

<a id="welcome-views"></a>
## 欢迎视图（Welcome Views）

> 当视图为空时，你可以[添加内容来引导用户](../references/contribution-points.md#contributes.viewsWelcome)了解如何使用你的扩展，或者如何开始。欢迎视图中支持链接和图标。

**✔️ 应该做**

> - 只在必要时使用欢迎视图
> - 尽可能使用链接而不是按钮
> - 只为主要的操作使用按钮
> - 使用清晰的链接文字，表明链接指向哪里
> - 限制内容的长度
> - 限制欢迎视图的数量
> - 限制视图中按钮的数量

**❌ 不应该做**

> - 在不必要的时候使用按钮
> - 把欢迎视图用于推广
> - 使用笼统的“阅读更多”作为链接文字

![欢迎视图](images/examples/welcome-view.png)

> *这个示例展示了扩展的一个主要操作，以及一个指向文档的附加链接。*

回顾 [树视图](../extension-guides/tree-view.md#welcome-content) 中的写法：在 `viewsWelcome` 的 `contents` 中，单独占一行的链接显示为按钮，与文字写在同一行的链接显示为普通链接。所以：

```json
"contents": "还没有连接任何数据库。\n[连接数据库](command:myExt.connect)\n查看[如何配置数据库连接](https://example.com/docs/connect)。"
```

| 部分 | 显示为 | 是否符合规范 |
|---|---|---|
| `[连接数据库](command:myExt.connect)`（单独一行） | 按钮 | ✔️ 一个主要操作 |
| `查看[如何配置数据库连接](...)` | 普通链接 | ✔️ 链接文字说明了去向，而不是“阅读更多” |

“不要用于推广”：比如在欢迎视图里放“升级到专业版”“关注我们的公众号”之类的内容。

---

<a id="views-with-progress"></a>
## 带进度的视图（Views With Progress）

> 你也可以通过引用视图的 ID，[在视图中显示进度](https://code.visualstudio.com/api/references/vscode-api#ProgressLocation)。

![带有进度的视图](images/examples/view-with-progress.png)

截图中，视图标题下方显示了一条进度条，表示视图正在加载数据。

写法是把 `location` 设为 `{ viewId: '视图 ID' }`（[通用能力](../extension-capabilities/common-capabilities.md#progress-api) 中介绍的 `withProgress` 的另一种用法）：

```ts
await vscode.window.withProgress(
  { location: { viewId: 'nodeDependencies' } },
  async () => {
    await loadDependencies();   // 加载期间，视图上方显示进度条
  }
);
```

---

<a id="view-actions"></a>
## 视图操作（View Actions）

> 视图可以在视图工具栏上公开[视图操作](../extension-guides/tree-view.md#view-actions)。注意不要添加太多的操作，以免造成干扰和困惑。使用内置的产品图标，有助于扩展与原生界面融为一体。不过，如果需要自定义图标，也可以提供一个 SVG 图标。

![视图操作的示例](images/examples/view-toolbar.png)

---

<a id="links"></a>
## 链接（Links）

> - [视图容器 API 参考](../references/contribution-points.md#contributes.viewsContainers)
> - [视图 API 参考](../references/contribution-points.md#contributes.views)
> - [视图操作扩展指南](../extension-guides/tree-view.md#view-actions)
> - [树视图扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/tree-view-sample)
> - [欢迎视图扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/welcome-view-content-sample)
> - [Webview 视图扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/webview-view-sample)

---

## 本篇小结

| 主题 | 要点 |
|---|---|
| 视图总体 | 数量少、名称短、每个视图都要有图标；优先树视图，少用 Webview 视图 |
| 位置 | 与内置功能相关的放进已有容器；否则才新建视图容器 |
| 树视图 | 用 `description` 和图标提供上下文；不要把节点当按钮；嵌套不要太深；每个条目行内操作不超过 3 个 |
| 欢迎视图 | 只在必要时用；只有主要操作用按钮，其余用链接；链接文字要说明去向；不用于推广 |
| 进度 | `withProgress({ location: { viewId } })` |
| 视图操作 | 按钮不要多，优先用内置图标 |
