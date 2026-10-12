# 面板（Panel）

> 原文：[Panel](https://code.visualstudio.com/api/ux-guidelines/panel)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/panel.md`（DateApproved: 10/7/2026）

> 面板是另一个用来显示[视图容器](../references/contribution-points.md#contributes.viewsContainers)的主要区域。

面板就是编辑器下方放终端、问题、输出、调试控制台的那块区域。扩展可以用 `viewsContainers.panel` 在这里添加自己的视图容器（见 [树视图](../extension-guides/tree-view.md#view-container)）。

**✔️ 应该做**

> - 把能从更多水平空间中受益的视图渲染在面板中
> - 用于提供辅助功能的视图

**❌ 不应该做**

> - 用于本应始终可见的视图，因为用户经常会把面板最小化
> - 渲染那些在被拖到其他视图容器（比如主侧边栏或辅助侧边栏）时，无法正确调整大小 / 重新排版的自定义 Webview 内容

![面板的示例](images/examples/panel.png)

**侧边栏和面板怎么选？**

| | 侧边栏 | 面板 |
|---|---|---|
| 形状 | 窄而高 | 宽而矮 |
| 适合的内容 | 层级列表、树形结构 | 宽表格、日志、终端式的输出 |
| 可见性 | 用户常常保持打开 | 用户常常把它最小化 |

关于 Webview 内容：用户可以把面板中的视图拖到侧边栏，宽度会一下子变窄很多。如果你的 Webview 布局是写死宽度的，拖过去后就会显示不全。所以 Webview 视图要用自适应的布局（比如 CSS 中用百分比、弹性布局，而不是固定像素）。

---

<a id="panel-toolbar"></a>
## 面板工具栏（Panel Toolbar）

> 面板工具栏可以显示作用于当前所选视图的选项。例如，终端视图会显示[视图操作](../extension-guides/tree-view.md#view-actions)，用来添加新终端、拆分视图布局等。切换到问题视图，则会显示另一组不同的操作。与[侧边栏工具栏](./sidebars.md#sidebar-toolbars)类似，只有当只有一个视图时，才会渲染这个工具栏。如果使用了多个视图，每个视图会渲染自己的工具栏。

**✔️ 应该做**

> - 如果有合适的，就使用已有的[产品图标](../references/icons-in-labels.md#icon-listing)
> - 提供清晰、有用的工具提示（tooltip）

**❌ 不应该做**

> - 不要添加过多的图标按钮。如果某个按钮需要更多的选项，可以考虑使用[上下文菜单](../references/contribution-points.md#contributes.menus)。
> - 不要重复面板默认的图标（折叠 / 展开、关闭等）

![只有一个视图时的面板工具栏示例](images/examples/panel-toolbar.png)

> *在这个示例中，面板中只渲染了一个视图，它的视图操作被渲染在面板的主工具栏中。*

![有多个视图时的面板工具栏示例](images/examples/panel-toolbar-multiple-views.png)

> *在这个示例中，使用了多个视图，所以每个视图都显示了各自特定的视图操作。*

工具栏中按钮的“工具提示”就是命令的 `title`，所以命令名称要写清楚（见 [命令指南](../extension-guides/command.md#naming-conventions)）。

---

<a id="links"></a>
## 链接（Links）

> - [视图容器贡献点](../references/contribution-points.md#contributes.viewsContainers)
> - [视图贡献点](../references/contribution-points.md#contributes.views)
> - [视图操作扩展指南](../extension-guides/tree-view.md#view-actions)
