# Webview

> 原文：[Webviews](https://code.visualstudio.com/api/ux-guidelines/webviews)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/webviews.md`（DateApproved: 10/7/2026）

> 如果你需要显示超出 VS Code API 所支持范围的自定义功能，可以使用完全可定制的 [Webview](../extension-guides/webview.md)。重要的是要明白，只有在绝对需要时才应该使用 Webview。

**✔️ 应该做**

> - 只在绝对必要时使用 Webview
> - 只在上下文合适时才激活你的扩展
> - 只为活动窗口打开 Webview
> - 确保视图中的所有元素都可以应用主题（参见 [webview-view-sample](https://github.com/microsoft/vscode-extension-samples/blob/main/webview-view-sample/media/main.css) 和[颜色标记](../references/theme-color.md)文档）
> - 确保你的视图遵循[无障碍指导](https://code.visualstudio.com/docs/configure/accessibility/accessibility)（颜色对比度、ARIA 标签、键盘导航）
> - 在工具栏和视图中使用命令操作

**❌ 不应该做**

> - 用于推广（升级、赞助等）
> - 用于向导
> - 在每个窗口中都打开
> - 在扩展更新时打开（改为通过通知询问）
> - 添加与编辑器或工作区无关的功能
> - 重复已有的功能（欢迎页、设置、配置等）

**逐条解释：**

| 规则 | 说明 |
|---|---|
| 只在必要时使用 | 先对照 [Webview 指南](../extension-guides/webview.md#should-i-use-a-webview) 中的表格，看原生部件能不能满足需求 |
| 只为活动窗口打开 | 用户可能同时开着好几个 VS Code 窗口。不要在每个窗口都弹出你的 Webview |
| 所有元素可以应用主题 | 用 `var(--vscode-xxx)` CSS 变量设置颜色（见 [Webview 指南](../extension-guides/webview.md#theming-webview-content)），不要写死颜色 |
| 无障碍 | 颜色对比度要足够；按钮、输入框加上 ARIA 标签（屏幕阅读器读取的文字）；所有功能都能只用键盘完成 |
| 不要在扩展更新时打开 | 很多扩展更新后会自动打开一个“更新说明”的 Webview 页面，这很打扰用户。应该弹一条通知，让用户自己选择要不要看（见 [通知](./notifications.md)） |
| 不要重复已有的功能 | 不要自己做欢迎页（用 [演练](./walkthroughs.md)）、设置页（用 [设置](./settings.md)） |

---

<a id="webview-examples"></a>
## Webview 示例（Webview examples）

**简易浏览器（Simple Browser）**

> 这个扩展在编辑器旁边打开一个浏览器预览。

![Webview 示例：浏览器](images/examples/webview-browser.png)

> *这个示例展示了在 VS Code 中直接开发 VS Code Web。一个 Webview 面板被用来渲染一个类似浏览器的窗口。*

**拉取请求（Pull Request）**

> 这个扩展在一个自定义的树视图中显示工作区所在仓库的拉取请求，然后用一个 Webview 显示拉取请求的详情视图。

![Webview 示例：拉取请求](images/examples/webview-pull-request.png)

这两个都是“确实需要 Webview”的例子：浏览器预览需要渲染网页；拉取请求的详情页包含富文本描述、评论、审查状态等复杂内容，原生部件无法展示。而且第二个例子中，**列表用的是树视图，只有详情才用 Webview**——能用原生部件的部分都用了原生部件。

---

<a id="webview-views"></a>
## Webview 视图（Webview views）

> 你也可以把 Webview 放进任何视图容器（侧边栏或面板）中，这些元素被称为 [Webview 视图](https://code.visualstudio.com/api/references/vscode-api#WebviewView)。同样的 Webview 指导也适用于 Webview 视图。

![Webview 视图](images/examples/webview-view.png)

> *这个 Webview 视图显示了用于创建拉取请求的内容，其中使用了下拉列表、输入框和按钮。*

Webview 视图要特别注意：它可能被用户拖到侧边栏、面板等宽度差别很大的位置，所以布局必须能自适应（见 [面板](./panel.md)）。

---

<a id="links"></a>
## 链接（Links）

> - [Webview 扩展指南](../extension-guides/webview.md)
> - [Webview 扩展示例](https://github.com/Microsoft/vscode-extension-samples/tree/main/webview-sample)
> - [Webview 视图扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/webview-view-sample)
