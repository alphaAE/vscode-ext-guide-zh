# UX 指南（UX Guidelines）

> 原文：[UX Guidelines](https://code.visualstudio.com/api/ux-guidelines/overview)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/overview.md`（DateApproved: 10/7/2026）

> 这些指南介绍了创建扩展的最佳实践，让扩展能与 VS Code 原生的界面和模式无缝集成。在这些指南中，你会看到：
>
> - VS Code 整体界面架构和元素的概述
> - 针对扩展所贡献界面的建议和示例
> - 相关指南和示例的链接
>
> 在深入细节之前，了解 VS Code 界面架构的各个部分如何组合在一起，以及你的扩展可以在哪里、以什么方式做贡献，是很重要的。

**UX 指南和前面的章节有什么不同？** 前面的章节讲的是“**能怎么做**”（API 怎么用），UX 指南讲的是“**应该怎么做**”（做成什么样才好用、才像 VS Code 原生的功能）。技术上能实现，不代表就应该这么做：比如每次保存都弹一个通知、在活动栏放五个图标，技术上都可以，但会让用户很烦。

本章共 14 篇，本篇是总览，介绍界面的各个组成部分；后面每篇对应一个部分。每篇通常包含“✔️ 应该做 / ❌ 不应该做”的清单和示例截图。

---

<a id="containers"></a>
## 容器（Containers）

> VS Code 的界面大致可以分为两个主要概念：**容器**和**条目（items）**。一般来说，容器可以被看作 VS Code 界面中较大的区块，它们渲染一个或多个条目：

[![VS Code 界面中容器元素的概览](images/examples/architecture-containers.png)](images/examples/architecture-containers.png)

图中标出了界面的六个容器区域：最左侧一列图标是**活动栏**（Activity Bar），旁边显示文件列表的是**主侧边栏**（Primary Sidebar），中间是**编辑器**（Editor），右侧显示时间线的是**辅助侧边栏**（Secondary Sidebar），编辑器下方显示终端的是**面板**（Panel），最底部的蓝色长条是**状态栏**（Status Bar）。

这张图比 [扩展工作台](../extension-capabilities/extending-workbench.md) 中的示意图多了一个“辅助侧边栏”，它位于编辑器的另一侧。

| 容器 | 扩展可以贡献什么 | 详细 |
|---|---|---|
| 活动栏 | 视图容器（图标） | [活动栏](./activity-bar.md) |
| 主侧边栏 | 视图 | [侧边栏](./sidebars.md#primary-sidebar) |
| 辅助侧边栏 | 不能直接贡献，由用户拖入 | [侧边栏](./sidebars.md#secondary-sidebar) |
| 编辑器 | 自定义编辑器、Webview、编辑器操作按钮 | [编辑器操作](./editor-actions.md) |
| 面板 | 视图容器、视图 | [面板](./panel.md) |
| 状态栏 | 状态栏项 | [状态栏](./status-bar.md) |

<a id="activity-bar"></a>
### 活动栏（Activity Bar）

> [活动栏](./activity-bar.md)是 VS Code 中一个核心的导航区域。扩展可以向活动栏贡献条目，这些条目作为[视图容器](../references/contribution-points.md#contributes.viewsContainers)，在主侧边栏中渲染[视图](./views.md)。

<a id="primary-sidebar"></a>
### 主侧边栏（Primary Sidebar）

> [主侧边栏](./sidebars.md#primary-sidebar)渲染一个或多个[视图](./views.md)。活动栏和主侧边栏紧密相连。点击一个贡献的活动栏条目（即视图容器），会打开主侧边栏，其中会渲染与这个视图容器相关联的一个或多个视图。一个具体的例子是资源管理器：点击资源管理器的条目，会打开主侧边栏，其中可以看到文件夹、时间线和大纲视图。

<a id="secondary-sidebar"></a>
### 辅助侧边栏（Secondary Sidebar）

> [辅助侧边栏](./sidebars.md#secondary-sidebar)同样是一个渲染带有视图的视图容器的区域。用户可以把终端或问题等视图拖到辅助侧边栏中，自定义自己的布局。

<a id="editor"></a>
### 编辑器（Editor）

> 编辑器区域包含一个或多个编辑器组。扩展可以贡献在编辑器区域中打开的[自定义编辑器](../references/contribution-points.md#contributes.customEditors)或 [Webview](../extension-guides/webview.md)。它们还可以贡献[编辑器操作](./editor-actions.md)，在编辑器工具栏中显示额外的图标按钮。

<a id="panel"></a>
### 面板（Panel）

> [面板](./panel.md)是另一个展示视图容器的区域。默认情况下，终端、问题和输出等视图在面板中以每次一个标签页的方式显示。用户也可以像在编辑器中那样，把视图拖成拆分布局。此外，扩展可以选择专门把视图容器添加到面板中，而不是活动栏 / 主侧边栏中。

<a id="status-bar"></a>
### 状态栏（Status Bar）

> [状态栏](./status-bar.md)提供关于工作区和当前活动文件的上下文信息。它渲染两组[状态栏项](./status-bar.md#status-bar-items)。

---

<a id="items"></a>
## 条目（Items）

> 扩展可以向上面列出的各种容器中添加条目。

[![VS Code 界面中各类条目的概览](images/examples/architecture-sections.png)](images/examples/architecture-sections.png)

这张图在容器的基础上，进一步标出了扩展可以添加的条目：侧边栏中的**视图**（View）、视图标题栏上的**视图工具栏**（View Toolbar）、侧边栏顶部的**侧边栏工具栏**（Sidebar Toolbar，资源管理器标题右侧的 `...`）、编辑器右上角的**编辑器工具栏**（Editor Toolbar）、面板中的视图容器与视图、面板右上角的**面板工具栏**（Panel Toolbar），以及状态栏中的**状态栏项**（Status Bar Item）。

<a id="view"></a>
### 视图（View）

> [视图](./views.md)可以以[树视图](./views.md#tree-views)、[欢迎视图](./views.md#welcome-views)或 [Webview 视图](./webviews.md#webview-views)的形式贡献，并且可以被拖到界面的其他区域。

<a id="view-toolbar"></a>
### 视图工具栏（View Toolbar）

> 扩展可以公开特定于视图的[操作](./views.md#view-actions)，它们显示为视图工具栏上的按钮。

<a id="sidebar-toolbar"></a>
### 侧边栏工具栏（Sidebar Toolbar）

> 作用于整个视图容器的操作，也可以显示在[侧边栏工具栏](./sidebars.md#sidebar-toolbars)中。

<a id="editor-toolbar"></a>
### 编辑器工具栏（Editor Toolbar）

> 扩展可以直接在编辑器工具栏中贡献作用于某个编辑器的[编辑器操作](./editor-actions.md)。

<a id="panel-toolbar"></a>
### 面板工具栏（Panel Toolbar）

> [面板工具栏](./panel.md#panel-toolbar)可以显示作用于当前所选视图的选项。例如，终端视图会显示添加新终端、拆分视图布局等操作。切换到问题视图，则会显示另一组不同的操作。

<a id="status-bar-item"></a>
### 状态栏项（Status Bar Item）

> 左侧的[状态栏项](./status-bar.md#status-bar-items)作用于整个工作区。右侧的条目作用于当前活动的文件。

对照截图看：左侧是 Git 分支 `main`、同步状态、错误和警告数量（与整个项目相关）；右侧是行列号、缩进、编码、换行符、语言（与当前打开的文件相关）。扩展添加状态栏项时，要根据内容的性质选择放在左边还是右边。

---

<a id="common-ui-elements"></a>
## 常见的界面元素（Common UI Elements）

<a id="command-palette"></a>
### 命令面板（Command Palette）

> 扩展可以贡献出现在[命令面板](./command-palette.md)中的命令，用来快速执行某些功能。

[![命令面板元素的概览](images/examples/command-palette.png)](images/examples/command-palette.png)

<a id="quick-pick"></a>
### 快速选择（Quick Pick）

> [快速选择](./quick-picks.md)以几种不同的方式获取用户的输入。它们可以要求单选、多选，甚至自由的文本输入。

![快速选择元素的概览](images/examples/quick-pick.png)

<a id="notifications"></a>
### 通知（Notifications）

> [通知](./notifications.md)用来向用户传达信息、警告和错误消息。它们也可以用来显示进度。

![通知元素的概览](images/examples/notification.png)

<a id="webview"></a>
### Webview

> [Webview](./webviews.md) 可以用来显示超出 VS Code“原生”API 范围的自定义内容和功能。

![Webview 元素的概览](images/examples/webview.png)

<a id="context-menus"></a>
### 上下文菜单（Context Menus）

> 与位置固定的命令面板不同，[上下文菜单](./context-menus.md)让用户可以在特定的位置执行操作或进行配置。

![上下文菜单元素的概览](images/examples/context-menu.png)

<a id="walkthroughs"></a>
### 演练（Walkthroughs）

> [演练](./walkthroughs.md)通过一个包含丰富内容的多步骤清单，为引导用户上手扩展提供一致的体验。

![演练 API 的概览](images/examples/walkthrough.png)

<a id="settings"></a>
### 设置（Settings）

> [设置](./settings.md)让用户可以配置与扩展相关的选项。

![设置页面的概览](images/examples/settings.png)

---

## 本篇小结

| 类别 | 元素 | 对应的指南 |
|---|---|---|
| 容器 | 活动栏、主侧边栏、辅助侧边栏、编辑器、面板、状态栏 | [活动栏](./activity-bar.md)、[侧边栏](./sidebars.md)、[面板](./panel.md)、[状态栏](./status-bar.md) |
| 条目 | 视图、视图工具栏、侧边栏工具栏、编辑器工具栏、面板工具栏、状态栏项 | [视图](./views.md)、[编辑器操作](./editor-actions.md) |
| 常见元素 | 命令面板、快速选择、通知、Webview、上下文菜单、演练、设置 | [命令面板](./command-palette.md)、[快速选择](./quick-picks.md)、[通知](./notifications.md)、[Webview](./webviews.md)、[上下文菜单](./context-menus.md)、[演练](./walkthroughs.md)、[设置](./settings.md) |

贯穿整章的原则：**优先使用原生的界面元素，保持克制（少即是多），与 VS Code 现有的风格保持一致。**
