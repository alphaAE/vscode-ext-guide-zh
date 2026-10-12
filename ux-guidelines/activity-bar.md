# 活动栏（Activity Bar）

> 原文：[Activity Bar](https://code.visualstudio.com/api/ux-guidelines/activity-bar)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/activity-bar.md`（DateApproved: 10/7/2026）

> 活动栏是 VS Code 中一个核心的导航区域。扩展可以向活动栏贡献[视图容器](./views.md#view-containers)，它们显示为活动栏条目。用户可以把条目拖到面板等其他位置，自定义自己的布局。

活动栏就是窗口最左侧的那一列图标。它的空间非常有限，每个用户装的扩展又很多，所以**一个扩展最多在这里放一个图标**，而且只在确实需要一个独立的入口时才放。

**✔️ 应该做**

> - 使用与默认活动栏条目图标风格一致的图标
> - 为与这个条目关联的[视图容器](./views.md#view-containers)起一个清晰、明了的名称

**❌ 不应该做**

> - 重复使用一个已有的图标
> - 用活动栏条目来打开一个 Webview 面板

![活动栏示例](images/examples/activity-bar.png)

**逐条解释：**

| 规则 | 原因 / 做法 |
|---|---|
| 图标风格与默认图标一致 | 内置图标都是单色、线条风格、24×24 的。用彩色、填充、写实风格的图标会显得格格不入。可以直接使用内置的 codicon（如 `$(package)`），或者按同样的风格绘制单色 SVG（见 [树视图](../extension-guides/tree-view.md#view-container)） |
| 名称清晰 | 鼠标悬停时显示的就是视图容器的 `title`，用户靠它判断这个图标是干什么的 |
| 不要重复已有的图标 | 和资源管理器、搜索、源代码管理等内置图标一样的话，用户分不清 |
| 不要用它打开 Webview 面板 | 用户点击活动栏图标，期望的是在侧边栏中打开一组视图，而不是在编辑器区域打开一个页面。活动栏是“切换侧边栏内容”的地方，不是“启动按钮”。如果需要一个打开 Webview 的入口，应该用命令、编辑器操作按钮等方式 |

---

<a id="links-resources"></a>
## 相关资源（Links Resources）

> - [视图容器贡献点](../references/contribution-points.md#contributes.viewsContainers)
> - [视图贡献点](../references/contribution-points.md#contributes.views)

实现方法见 [树视图](../extension-guides/tree-view.md#view-container) 中的视图容器一节。
