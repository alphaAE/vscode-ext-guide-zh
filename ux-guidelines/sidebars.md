# 侧边栏（Sidebars）

> 原文：[Sidebars](https://code.visualstudio.com/api/ux-guidelines/sidebars)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/sidebars.md`（DateApproved: 10/7/2026）

> 主侧边栏和辅助侧边栏由一个[视图容器](./views.md#view-containers)贡献的一个或多个[视图](./views.md)组成。扩展可以把视图贡献到一个已有的视图容器（例如资源管理器）中，也可以贡献一个全新的视图容器。

**✔️ 应该做**

> - 把相关的视图和内容组织在一起
> - 为视图容器及其视图使用清晰、具有描述性的名称

**❌ 不应该做**

> - 使用过多的视图容器。对于大多数扩展来说，一个视图容器（比如一个包含这个扩展特有视图的侧边栏）通常就足够了。
> - 使用过多的视图（对于大多数屏幕尺寸来说，3～5 个是比较舒适的上限）
> - 在侧边栏中添加一些本来可以做成一个简单命令的内容。
> - 重复已有的功能

![两个侧边栏的示例](images/examples/sidebars.png)

截图中，编辑器的左右两侧各有一个侧边栏：左侧是主侧边栏，右侧是辅助侧边栏。

**“本来可以做成一个简单命令的内容”** 是什么意思？比如一个视图里只有一个“生成代码”按钮，用户点一下就完成了。这样的功能没必要占用侧边栏的空间，做成一个命令（放进命令面板或右键菜单）就够了。侧边栏适合放**需要持续查看、浏览的内容**，比如列表、树形结构。

---

<a id="primary-sidebar"></a>
## 主侧边栏（Primary Sidebar）

> 很多扩展选择向主侧边栏贡献视图和 / 或视图容器，因为它能让内容获得很高的曝光度。在这里添加内容时要做出明智的判断：贡献过多的界面，可能会导致杂乱的体验，让用户感到困惑。

![主侧边栏的示例](images/examples/primary-sidebar.png)

---

<a id="secondary-sidebar"></a>
## 辅助侧边栏（Secondary Sidebar）

> 顾名思义，辅助侧边栏通常被看作视图的辅助位置。虽然默认情况下扩展不能直接向它贡献视图，但用户可以把主侧边栏或面板中的视图拖过来，自定义自己的布局。

![辅助侧边栏的示例](images/examples/secondary-sidebar.png)

也就是说，辅助侧边栏是**用户的**空间，扩展不应该（默认也不能）主动占用它。这也是为什么 [视图](./views.md) 一篇建议每个视图都设置一个图标：视图被用户拖到辅助侧边栏时，是用图标来表示的。

---

<a id="sidebar-toolbars"></a>
## 侧边栏工具栏（Sidebar Toolbars）

> 默认情况下，侧边栏中包含不止一个视图的视图容器，会在侧边栏工具栏中显示一个 `...` 图标按钮，用来显示和隐藏每个视图。看起来是这样的：

![包含两个视图的侧边栏](images/examples/sidebar-toolbar-default.png)

> 不过，如果只使用了一个视图，侧边栏会自动合并界面，用侧边栏工具栏来渲染这个视图特有的所有操作。原本 `...` 按钮的位置，会渲染与 “Notes” 视图相关联的两个操作：

![只有一个视图、工具栏中显示了操作按钮的侧边栏](images/examples/sidebar-toolbar-actions.png)

| 视图容器中的视图数量 | 侧边栏顶部的工具栏显示 |
|---|---|
| 多个 | 一个 `...` 按钮，用来显示 / 隐藏各个视图 |
| 只有一个 | 这个视图自己的操作按钮（即视图标题栏上的按钮被“提升”到了侧边栏顶部） |

所以只有一个视图时，界面会更简洁：视图本身不再单独显示标题栏，它的按钮直接显示在侧边栏顶部。

> 和其他工具栏一样，注意不要添加太多的操作，以减少杂乱和困惑。如果可能，使用已有的产品图标，并配上具有描述性的命令名称。

“产品图标”就是内置的 codicon（见 [产品图标主题](../extension-guides/product-icon-theme.md)）。命令名称会显示为按钮的悬停提示，所以要写清楚（见 [命令指南](../extension-guides/command.md#naming-conventions) 中的命名规范）。

---

<a id="links"></a>
## 链接（Links）

> - [视图容器贡献点](../references/contribution-points.md#contributes.viewsContainers)
> - [视图贡献点](../references/contribution-points.md#contributes.views)
> - [视图操作扩展指南](../extension-guides/tree-view.md#view-actions)
> - [欢迎视图贡献点](../references/contribution-points.md#contributes.viewsWelcome)
> - [树视图扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/tree-view-sample)
> - [Webview 视图扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/webview-view-sample)
> - [欢迎视图扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/welcome-view-content-sample)

---

## 本篇小结

| 要点 | 说明 |
|---|---|
| 视图容器 | 一个扩展通常一个就够 |
| 视图数量 | 3～5 个是舒适的上限 |
| 不适合放在侧边栏的 | 一个按钮就能完成的功能（做成命令）、已有的功能 |
| 辅助侧边栏 | 扩展不能直接贡献，留给用户自定义 |
| 工具栏 | 只有一个视图时，视图的操作会显示在侧边栏顶部；按钮不要太多，用内置图标 |
