# 编辑器操作（Editor Actions）

> 原文：[Editor Actions](https://code.visualstudio.com/api/ux-guidelines/editor-actions)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/editor-actions.md`（DateApproved: 10/7/2026）

> [编辑器操作](../references/contribution-points.md#contributes.commands)可以出现在编辑器工具栏中。你可以添加一个图标作为快捷操作，也可以在溢出菜单（**...**）中添加菜单项。

编辑器工具栏就是编辑器标签页右侧的那一排按钮（比如“拆分编辑器”“打开预览”）。扩展通过 `menus.editor/title` 往这里添加按钮，写法见 [虚拟文档](../extension-guides/virtual-documents.md#add-editor-commands) 和 [语言模型 API 教程](../extension-guides/ai/language-model-tutorial.md#add-a-button-to-the-editor-title-bar)：

| 显示方式 | 写法 |
|---|---|
| 图标按钮（快捷操作） | `"group": "navigation"`，命令要设置 `icon` |
| 溢出菜单 `...` 中的菜单项 | 不设置 `group`，或者用其他组名 |

**✔️ 应该做**

> - 只在上下文合适时才显示
> - 使用图标库中的图标
> - 次要的操作放在溢出菜单中

**❌ 不应该做**

> - 添加一个以上的图标
> - 添加自定义的颜色
> - 使用 emoji

![编辑器操作](images/examples/editor-actions.png)

> *这个来自 GitHub Pull Requests and Issues 扩展的示例会打开一个差异视图，并且只在有更改的文件上显示。*

**逐条解释：**

| 规则 | 说明 |
|---|---|
| 只在上下文合适时显示 | 编辑器工具栏是所有扩展共用的。如果你的按钮对每个文件都显示，就会和其他扩展的按钮挤在一起。一定要用 `when` 子句限定，比如 `"when": "resourceLangId == markdown"` 只在 Markdown 文件中显示 |
| 使用图标库中的图标 | 即内置的 codicon，写成 `"icon": "$(图标名)"`，完整列表见 [标签中的图标](../references/icons-in-labels.md) |
| 次要操作放进溢出菜单 | 常用的一个放成图标，其余的放进 `...` |
| 不要添加一个以上的图标 | 每个扩展在这里最多放一个图标按钮 |
| 不要自定义颜色、不要用 emoji | 内置按钮都是单色的，彩色或 emoji 会显得突兀 |

截图中的示例就是“只在上下文合适时显示”的典型：打开差异视图的按钮，只在有改动的文件上才出现。

---

<a id="links"></a>
## 链接（Links）

> - [自定义编辑器扩展指南](../extension-guides/custom-editors.md)
> - [自定义编辑器 API 参考](../references/contribution-points.md#contributes.customEditors)
> - [自定义编辑器扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/custom-editor-sample)
> - [Webview 扩展指南](../extension-guides/webview.md)
> - [Webview 扩展示例](https://github.com/microsoft/vscode-extension-samples/blob/main/webview-sample)
