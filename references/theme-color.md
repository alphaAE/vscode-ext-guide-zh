# 主题颜色参考（Theme Color）

> 原文：[Theme Color](https://code.visualstudio.com/api/references/theme-color)
> 源文件：`microsoft/vscode-docs` → `api/references/theme-color.md`（DateApproved: 10/7/2026）

> 你可以用 `workbench.colorCustomizations` 用户[设置](https://code.visualstudio.com/docs/configure/settings)，自定义当前使用的 Visual Studio Code [颜色主题](https://code.visualstudio.com/docs/getstarted/themes)。

```json
{
  "workbench.colorCustomizations": {
    "activityBar.background": "#00AA00"
  }
}
```

> **注意**：如果你想使用一个现有的颜色主题，请参见[颜色主题](https://code.visualstudio.com/docs/getstarted/themes)，在那里你可以了解如何通过 **Preferences: Color Theme**（首选项：颜色主题）下拉框（`Ctrl+K Ctrl+T`）设置当前的颜色主题。
>
> 主题颜色在 [webview](../extension-guides/webview.md) 中以 CSS 变量的形式提供，还有[一个扩展](https://marketplace.visualstudio.com/items?itemName=connor4312.css-theme-completions)可以为它们提供智能提示。

**这份参考的三种用法：**

| 谁在用 | 用在哪里 | 写法 |
|---|---|---|
| 颜色主题作者 | 主题 JSON 文件的 `colors` 部分（见 [颜色主题](../extension-guides/color-theme.md)） | `"colors": { "editor.background": "#1e1e1e" }` |
| 用户 | `settings.json` 的 `workbench.colorCustomizations`，可以按主题分别设置：`"[Default Dark Modern]": { ... }` | 如上面的示例 |
| 扩展开发者 | 代码中引用主题颜色，让你的 UI 跟随主题 | `new vscode.ThemeColor('errorForeground')`；webview 中用 CSS 变量 `var(--vscode-editor-background)`（点号换成连字符） |

**本参考的结构：** 下面按 UI 区域分组列出了所有颜色 ID。每一条的格式是 `` `颜色 ID`：说明 ``。命名有规律：`区域.部位+状态+属性`，例如 `tab.unfocusedActiveBorder` = 标签页（`tab`）+ 在没有焦点的组中（`unfocused`）+ 活动的（`Active`）+ 边框（`Border`）。常见的后缀有 `background`（背景）、`foreground`（前景，即文字 / 图标颜色）、`border`（边框）、`hoverBackground`（悬停背景）、`activeXxx`（活动状态）、`inactiveXxx`（非活动状态）。

（快捷键为 Windows 上的默认值，macOS 上 `Ctrl` 对应 `Cmd`。颜色 ID 本身保持英文不变；部分说明文字中原文存在的明显错误，已在括号中注明。）

---

<a id="color-formats"></a>
## 颜色格式（Color formats）

> 颜色值可以用带有透明度 alpha 通道的 RGB 颜色模型来定义。支持以下十六进制表示格式：`#RGB`、`#RGBA`、`#RRGGBB` 和 `#RRGGBBAA`。R（红）、G（绿）、B（蓝）和 A（alpha，透明度）都是十六进制字符（0-9、a-f 或 A-F）。三位数的表示法（`#RGB`）是六位数形式（`#RRGGBB`）的简写，四位数的 RGB 表示法（`#RGBA`）是八位数形式（`#RRGGBBAA`）的简写。例如 `#e35f` 与 `#ee3355ff` 是同一个颜色。

> 如果没有定义 alpha 值，它默认为 `ff`（不透明，没有透明度）。如果 alpha 设为 `00`，颜色就是完全透明的。

> 有些颜色不应该是不透明的，以免盖住其他的标注。请查看颜色的说明，了解哪些颜色适用这一点。

**补充：**

| 写法 | 等价于 | 含义 |
|---|---|---|
| `#f00` | `#ff0000` | 红色，不透明 |
| `#f008` | `#ff000088` | 红色，约 53% 不透明度 |
| `#ff000040` | | 红色，25% 不透明度（`40` 十六进制 = 64，64 / 255 ≈ 25%） |

透明度常用的值：`ff` = 100%，`cc` ≈ 80%，`99` ≈ 60%，`80` ≈ 50%，`66` ≈ 40%，`33` ≈ 20%，`1a` ≈ 10%。说明中带有“这个颜色不能是不透明的，以免遮住下面的装饰”的颜色（如选择背景、查找匹配背景），一定要带透明度，否则会把文字或其他高亮完全盖住。

---

<a id="contrast-colors"></a>
## 对比度颜色（Contrast colors）

> 对比度颜色通常只在高对比度主题中设置。设置之后，它们会在整个 UI 中的各个项周围添加一个额外的边框，以提高对比度。

- `contrastActiveBorder`：活动元素周围额外的边框，用于把它们与其他元素分隔开，以获得更高的对比度。
- `contrastBorder`：元素周围额外的边框，用于把它们与其他元素分隔开，以获得更高的对比度。

（`contrastBorder` 和 `contrastActiveBorder` 一旦设置，会给几乎所有的 UI 元素加上边框，所以普通主题中通常不设置它们。）

---

<a id="base-colors"></a>
## 基础颜色（Base colors）

- `focusBorder`：拥有焦点的元素的整体边框颜色。只有在没有被某个组件覆盖时，才会使用这个颜色。
- `foreground`：整体的前景色。只有在没有被某个组件覆盖时，才会使用这个颜色。
- `disabledForeground`：被禁用元素的整体前景色。只有在没有被某个组件覆盖时，才会使用这个颜色。
- `widget.border`：编辑器内查找 / 替换等小部件的边框颜色。
- `widget.shadow`：编辑器内查找 / 替换等小部件的阴影颜色。
- `selection.background`：工作台中文本选择的背景色（用于输入框或文本区域，不适用于编辑器和终端中的选择）。
- `descriptionForeground`：提供额外信息的描述文字的前景色，例如用于一个标签的说明。
- `errorForeground`：错误消息的整体前景色（只有在没有被某个组件覆盖时，才会使用这个颜色）。
- `icon.foreground`：工作台中图标的默认颜色。
- `sash.hoverBorder`：可拖动分隔条（sash）在悬停时的边框颜色。

---

<a id="window-border"></a>
## 窗口边框（Window border）

> VS Code 窗口边框的主题颜色。

- `window.activeBorder`：活动（拥有焦点的）窗口的边框颜色。
- `window.inactiveBorder`：非活动（没有焦点的）窗口的边框颜色。

> 窗口边框颜色只在 macOS 和 Linux 上受支持（不支持 Windows），并且只有在启用了自定义标题栏（`"window.titleBarStyle": "custom"`）时才有效。

---

<a id="modern-ui-colors"></a>
## 现代 UI 颜色（Modern UI colors）

> 这些颜色在启用现代 UI 时，用于自定义工作台的表面和控件。

- `surface.background`：带框容器表面（“卡片”）的背景色，例如现代布局中浮动的工作台面板。
- `surface.foreground`：带框容器表面（“卡片”）的前景色，例如现代布局中浮动的工作台面板。
- `surface.border`：带框容器表面（“卡片”）的边框颜色，例如现代布局中浮动的工作台面板。
- `editor.border`：现代布局中编辑器表面的边框颜色。
- `modernPanel.border`：启用现代 UI 时，面板表面的边框颜色。
- `modernSash.gripForeground`：启用现代 UI 时，标记工作台各部分之间可调整大小的边界的拖动手柄的颜色。
- `modernTab.activeBackground`：启用现代标签页样式时，活动标签页的背景色。
- `modernTab.activeForeground`：启用现代标签页样式时，活动标签页的前景色。
- `modernTab.hoverBackground`：启用现代标签页样式时，悬停的标签页的背景色。
- `modernTab.hoverForeground`：启用现代标签页样式时，悬停的标签页的前景色。
- `modernEditorTab.activeBackground`：启用现代标签页样式时，活动编辑器标签页的背景色。
- `modernEditorTab.activeActionBackground`：启用现代标签页样式时，活动编辑器标签页上标签页操作的不透明背景色。
- `modernEditorTab.activeForeground`：启用现代标签页样式时，活动编辑器标签页的前景色。
- `modernEditorTab.inactiveBackground`：启用现代标签页样式时，非活动编辑器标签页的背景色。
- `modernEditorTab.hoverBackground`：启用现代标签页样式时，悬停的编辑器标签页的背景色。
- `modernEditorTab.hoverActionBackground`：启用现代标签页样式时，悬停的编辑器标签页上标签页操作的不透明背景色。
- `modernEditorTab.hoverForeground`：启用现代标签页样式时，悬停的编辑器标签页的前景色。
- `modernEditorTab.activeHoverBackground`：启用现代标签页样式时，悬停的活动编辑器标签页的背景色。
- `modernEditorTab.activeHoverActionBackground`：启用现代标签页样式时，悬停的活动编辑器标签页上标签页操作的不透明背景色。
- `modernEditorTab.selectedActionBackground`：启用现代标签页样式时，选中的编辑器标签页上标签页操作的不透明背景色。
- `modernActivityBar.background`：启用现代 UI 时，位于默认侧边位置的活动栏的背景色。
- `modernActivityBar.inactiveBackground`：活动栏位于默认侧边位置、并且启用了现代 UI 时，非活动窗口中活动栏的背景色。
- `modernActivityBarItem.activeBackground`：启用现代 UI 时，默认侧边位置的活动栏中活动项的背景色。
- `modernActivityBarItem.activeForeground`：启用现代 UI 时，默认侧边位置的活动栏中活动项的前景色。
- `modernActivityBarItem.hoverBackground`：启用现代 UI 时，默认侧边位置的活动栏中悬停项的背景色。
- `modernActivityBarItem.hoverForeground`：启用现代 UI 时，默认侧边位置的活动栏中悬停项的前景色。
- `modernActivityBar.border`：启用现代 UI 时，位于默认侧边位置的活动栏的边框颜色。
- `modernUI.shellBackground`：启用现代 UI 时，浮动的工作台表面周围可见的外壳（shell）的背景色。
- `modernUI.inactiveShellBackground`：窗口处于非活动状态、并且启用了现代 UI 时，浮动的工作台表面周围可见的外壳的背景色。

---

<a id="text-colors"></a>
## 文本颜色（Text colors）

> 文本文档（例如欢迎页）中的颜色。

- `textBlockQuote.background`：文本中块引用的背景色。
- `textBlockQuote.border`：文本中块引用的边框颜色。
- `textCodeBlock.background`：文本中代码块的背景色。
- `textLink.activeForeground`：文本中的链接在被点击和鼠标悬停时的前景色。
- `textLink.foreground`：文本中链接的前景色。
- `textPreformat.foreground`：预格式化文本片段的前景色。
- `textPreformat.background`：预格式化文本片段的背景色。
- `textPreformat.border`：预格式化文本片段的边框颜色。
- `textSeparator.foreground`：文本分隔符的颜色。

---

<a id="action-colors"></a>
## 操作颜色（Action colors）

> 一组控制整个工作台中与操作交互的颜色。

- `toolbar.hoverBackground`：鼠标悬停在操作上时工具栏的背景色
- `toolbar.hoverOutline`：鼠标悬停在操作上时工具栏的轮廓颜色
- `toolbar.activeBackground`：在操作上按住鼠标时工具栏的背景色
- `editorActionList.background`：操作列表的背景色。
- `editorActionList.foreground`：操作列表的前景色。
- `editorActionList.focusForeground`：操作列表中拥有焦点的项的前景色。
- `editorActionList.focusBackground`：操作列表中拥有焦点的项的背景色。

---

<a id="button-control"></a>
## 按钮控件（Button control）

> 一组用于按钮小部件的颜色，例如新窗口的资源管理器中的 **Open Folder**（打开文件夹）按钮。

![按钮控件](images/theme-color/button.png)

- `button.background`：按钮的背景色。
- `button.foreground`：按钮的前景色。
- `button.border`：按钮的边框颜色。
- `button.separator`：按钮分隔线的颜色。
- `button.hoverBackground`：悬停时按钮的背景色。
- `button.secondaryForeground`：次要按钮的前景色。
- `button.secondaryBackground`：次要按钮的背景色。
- `button.secondaryHoverBackground`：悬停时次要按钮的背景色。
- `button.secondaryBorder`：次要按钮的边框颜色。
- `checkbox.background`：复选框小部件的背景色。
- `checkbox.foreground`：复选框小部件的前景色。
- `checkbox.disabled.background`：被禁用的复选框的背景色。
- `checkbox.disabled.foreground`：被禁用的复选框的前景色。
- `checkbox.border`：复选框小部件的边框颜色。
- `checkbox.selectBackground`：复选框所在的元素被选中时，复选框小部件的背景色。
- `checkbox.selectBorder`：复选框所在的元素被选中时，复选框小部件的边框颜色。
- `radio.activeForeground`：活动单选选项的前景色。
- `radio.activeBackground`：活动单选选项的背景色。
- `radio.activeBorder`：活动单选选项的边框颜色。
- `radio.inactiveForeground`：非活动单选选项的前景色。
- `radio.inactiveBackground`：非活动单选选项的背景色。
- `radio.inactiveBorder`：非活动单选选项的边框颜色。
- `radio.inactiveHoverBackground`：悬停时非活动单选选项的背景色。

---

<a id="dropdown-control"></a>
## 下拉框控件（Dropdown control）

> 一组用于所有下拉框小部件的颜色，例如集成终端或输出面板中的下拉框。注意，目前 macOS 上不使用下拉框控件。

![下拉框控件](images/theme-color/dropdown.png)

- `dropdown.background`：下拉框的背景色。
- `dropdown.listBackground`：下拉列表的背景色。
- `dropdown.border`：下拉框的边框颜色。
- `dropdown.foreground`：下拉框的前景色。

---

<a id="input-control"></a>
## 输入框控件（Input control）

> 输入控件的颜色，例如搜索视图或查找 / 替换对话框中的输入框。

![输入框控件](images/theme-color/input.png)

- `input.background`：输入框的背景色。
- `input.border`：输入框的边框颜色。
- `input.foreground`：输入框的前景色。
- `input.placeholderForeground`：输入框中占位文字的前景色。
- `inputOption.activeBackground`：输入框中已激活选项的背景色。
- `inputOption.activeBorder`：输入框中已激活选项的边框颜色。
- `inputOption.activeForeground`：输入框中已激活选项的前景色。
- `inputOption.hoverBackground`：输入框中选项的悬停背景色（原文描述与 activeBackground 相同，应为悬停时的背景色）。
- `inputValidation.errorBackground`：错误级别的输入校验背景色。
- `inputValidation.errorForeground`：错误级别的输入校验前景色。
- `inputValidation.errorBorder`：错误级别的输入校验边框颜色。
- `inputValidation.infoBackground`：信息级别的输入校验背景色。
- `inputValidation.infoForeground`：信息级别的输入校验前景色。
- `inputValidation.infoBorder`：信息级别的输入校验边框颜色。
- `inputValidation.warningBackground`：警告级别的输入校验背景色（原文写作 information warning）。
- `inputValidation.warningForeground`：警告级别的输入校验前景色。
- `inputValidation.warningBorder`：警告级别的输入校验边框颜色。

---

<a id="scrollbar-control"></a>
## 滚动条控件（Scrollbar control）

- `scrollbar.background`：滚动条轨道的背景色。
- `scrollbar.shadow`：表示视图已滚动的滚动条滑块阴影。
- `scrollbarSlider.activeBackground`：点击时滚动条滑块的背景色。
- `scrollbarSlider.background`：滚动条滑块的背景色。
- `scrollbarSlider.hoverBackground`：悬停时滚动条滑块的背景色。

---

<a id="badge"></a>
## 徽章（Badge）

> 徽章是小的信息标签，例如搜索结果的数量。

- `badge.foreground`：徽章的前景色。
- `badge.background`：徽章的背景色。

---

<a id="progress-bar"></a>
## 进度条（Progress bar）

- `progressBar.background`：长时间运行的操作所显示的进度条的背景色。

---

<a id="lists-and-trees"></a>
## 列表和树（Lists and trees）

> 列表和树（如文件资源管理器）的颜色。活动的列表 / 树拥有键盘焦点，非活动的则没有。

- `list.activeSelectionBackground`：列表 / 树处于活动状态时，选中项的背景色。
- `list.activeSelectionForeground`：列表 / 树处于活动状态时，选中项的前景色。
- `list.activeSelectionIconForeground`：列表 / 树处于活动状态时，选中项的图标前景色。活动的列表 / 树拥有键盘焦点，非活动的则没有。
- `list.dropBackground`：使用鼠标移动项时，列表 / 树的拖放背景色。
- `list.focusBackground`：列表 / 树处于活动状态时，拥有焦点的项的背景色。
- `list.focusForeground`：列表 / 树处于活动状态时，拥有焦点的项的前景色。活动的列表 / 树拥有键盘焦点，非活动的则没有。
- `list.focusHighlightForeground`：在列表 / 树中搜索时，处于活动焦点的项上匹配高亮的前景色。
- `list.focusOutline`：列表 / 树处于活动状态时，拥有焦点的项的轮廓颜色。活动的列表 / 树拥有键盘焦点，非活动的则没有。
- `list.focusAndSelectionOutline`：列表 / 树处于活动状态时，拥有焦点并被选中的项的轮廓颜色。活动的列表 / 树拥有键盘焦点，非活动的则没有。
- `list.highlightForeground`：在列表 / 树中搜索时，匹配高亮的前景色。
- `list.hoverBackground`：鼠标悬停在项上时，列表 / 树的背景色。
- `list.hoverForeground`：鼠标悬停在项上时，列表 / 树的前景色。
- `list.inactiveSelectionBackground`：列表 / 树处于非活动状态时，选中项的背景色。
- `list.inactiveSelectionForeground`：列表 / 树处于非活动状态时，选中项的前景色。活动的列表 / 树拥有键盘焦点，非活动的则没有。
- `list.inactiveSelectionIconForeground`：列表 / 树处于非活动状态时，选中项的图标前景色。活动的列表 / 树拥有键盘焦点，非活动的则没有。
- `list.inactiveFocusBackground`：列表处于非活动状态时，拥有焦点的项的背景色。活动的列表拥有键盘焦点，非活动的则没有。目前只在列表中支持。
- `list.inactiveFocusOutline`：列表 / 树处于非活动状态时，拥有焦点的项的轮廓颜色。活动的列表 / 树拥有键盘焦点，非活动的则没有。
- `list.invalidItemForeground`：列表 / 树中无效项的前景色，例如资源管理器中一个无法解析的根。
- `list.errorForeground`：包含错误的列表项的前景色。
- `list.warningForeground`：包含警告的列表项的前景色。
- `listFilterWidget.background`：在列表 / 树中搜索时，输入文字的列表 / 树筛选器背景色。
- `listFilterWidget.outline`：在列表 / 树中搜索时，列表 / 树筛选器小部件中输入文字的轮廓颜色。
- `listFilterWidget.noMatchesOutline`：在列表 / 树中搜索、输入的文字没有找到匹配时，列表 / 树筛选器小部件的轮廓颜色。
- `listFilterWidget.shadow`：列表和树中类型筛选器小部件的阴影颜色。
- `list.filterMatchBackground`：列表和树中被筛选出的匹配项的背景色。
- `list.filterMatchBorder`：列表和树中被筛选出的匹配项的边框颜色。
- `list.deemphasizedForeground`：列表 / 树中被弱化显示的项的前景色。
- `list.dropBetweenBackground`：使用鼠标在项之间移动项时，列表 / 树的拖放边框颜色。
- `tree.indentGuidesStroke`：树小部件中缩进参考线的描边颜色。
- `tree.inactiveIndentGuidesStroke`：树中非活动的缩进参考线的描边颜色。
- `tree.tableColumnsBorder`：树中表格列之间的边框颜色（原文描述与缩进参考线相同，疑为复制错误）。
- `tree.tableOddRowsBackground`：表格奇数行的背景色。

---

<a id="activity-bar"></a>
## 活动栏（Activity Bar）

> 活动栏通常显示在工作台的最左侧或最右侧，用于在侧边栏的视图之间快速切换。

- `activityBar.background`：活动栏的背景色。
- `activityBar.dropBorder`：活动栏项的拖放反馈颜色。活动栏显示在最左侧或最右侧，用于在侧边栏的视图之间切换。
- `activityBar.foreground`：活动栏的前景色（例如用于图标）。
- `activityBar.inactiveForeground`：活动栏项处于非活动状态时的前景色。
- `activityBar.border`：活动栏与侧边栏之间的边框颜色。
- `activityBarBadge.background`：活动通知徽章的背景色。
- `activityBarBadge.foreground`：活动通知徽章的前景色。
- `activityBar.activeBorder`：活动栏中活动指示器的边框颜色。
- `activityBar.activeBackground`：活动栏中活动元素的可选背景色。
- `activityBar.activeFocusBorder`：活动栏中活动项的焦点边框颜色。
- `activityBarTop.foreground`：活动栏位于顶部时，其中项的活动前景色。活动栏用于在侧边栏的视图之间切换。
- `activityBarTop.activeBorder`：活动栏位于顶部时，其中活动项的焦点边框颜色。活动栏用于在侧边栏的视图之间切换。
- `activityBarTop.inactiveForeground`：活动栏位于顶部时，其中项的非活动前景色。活动栏用于在侧边栏的视图之间切换。
- `activityBarTop.dropBorder`：活动栏位于顶部时，其中项的拖放反馈颜色。活动栏用于在侧边栏的视图之间切换。
- `activityBarTop.background`：活动栏设置为顶部 / 底部时的背景色。
- `activityBarTop.activeBackground`：活动栏位于顶部 / 底部时，其中活动项的背景色。活动栏用于在侧边栏的视图之间切换。
- `activityWarningBadge.foreground`：警告活动徽章的前景色
- `activityWarningBadge.background`：警告活动徽章的背景色
- `activityErrorBadge.foreground`：错误活动徽章的前景色
- `activityErrorBadge.background`：错误活动徽章的背景色

---

<a id="profiles"></a>
## 配置文件（Profiles）

- `profileBadge.background`：配置文件徽章的背景色。配置文件徽章显示在活动栏中设置齿轮图标的上方。
- `profileBadge.foreground`：配置文件徽章的前景色。配置文件徽章显示在活动栏中设置齿轮图标的上方。
- `profiles.sashBorder`：配置文件编辑器中拆分视图分隔条的边框颜色。

---

<a id="side-bar"></a>
## 侧边栏（Side Bar）

> 侧边栏包含资源管理器、搜索等视图。

- `sideBar.background`：侧边栏的背景色。
- `sideBar.foreground`：侧边栏的前景色。侧边栏是资源管理器、搜索等视图的容器。
- `sideBar.border`：侧边栏与编辑器之间那一侧的边框颜色。
- `sideBar.dropBackground`：侧边栏各部分的拖放反馈颜色。这个颜色应该带有透明度，以便侧边栏的各部分仍然可以透出来。

- `sideBarTitle.foreground`：侧边栏标题的前景色。
- `sideBarSectionHeader.background`：侧边栏分区标题的背景色。
- `sideBarSectionHeader.foreground`：侧边栏分区标题的前景色。
- `sideBarSectionHeader.border`：侧边栏分区标题的边框颜色。
- `sideBarActivityBarTop.border`：位于顶部 / 底部的活动栏与视图之间的边框颜色。
- `sideBarTitle.background`：侧边栏标题的背景色。侧边栏是资源管理器、搜索等视图的容器。
- `sideBarTitle.border`：侧边栏标题底部、把标题与视图分隔开的边框颜色。侧边栏是资源管理器、搜索等视图的容器。
- `sideBarStickyScroll.background`：侧边栏中粘性滚动的背景色。
- `sideBarStickyScroll.border`：侧边栏中粘性滚动的边框颜色。
- `sideBarStickyScroll.shadow`：侧边栏中粘性滚动的阴影颜色。

---

<a id="minimap"></a>
## 缩略图（Minimap）

> 缩略图显示当前文件的缩小版本。

- `minimap.findMatchHighlight`：文件内搜索匹配项的高亮颜色。
- `minimap.selectionHighlight`：编辑器选择的高亮颜色。
- `minimap.errorHighlight`：编辑器中错误的高亮颜色。
- `minimap.warningHighlight`：编辑器中警告的高亮颜色。
- `minimap.background`：缩略图的背景色。
- `minimap.selectionOccurrenceHighlight`：缩略图中与编辑器选择内容重复的部分的标记颜色。
- `minimap.foregroundOpacity`：缩略图中渲染的前景元素的不透明度。例如，"#000000c0" 会以 75% 的不透明度渲染元素。
- `minimap.infoHighlight`：缩略图中信息的标记颜色。
- `minimap.chatEditHighlight`：缩略图中待处理的编辑区域的颜色。

- `minimapSlider.background`：缩略图滑块的背景色。
- `minimapSlider.hoverBackground`：悬停时缩略图滑块的背景色。
- `minimapSlider.activeBackground`：点击时缩略图滑块的背景色。

- `minimapGutter.addedBackground`：缩略图装订线中新增内容的颜色。
- `minimapGutter.modifiedBackground`：缩略图装订线中修改内容的颜色。
- `minimapGutter.deletedBackground`：缩略图装订线中删除内容的颜色。
- `editorMinimap.inlineChatInserted`：缩略图中内联聊天插入内容的标记颜色。

---

<a id="editor-groups--tabs"></a>
## 编辑器组和标签页（Editor Groups & Tabs）

> 编辑器组是编辑器的容器，可以有多个编辑器组。标签页是一个编辑器的容器，一个编辑器组中可以打开多个标签页。

- `editorGroup.border`：把多个编辑器组彼此分隔开的颜色。

  ![editorGroup.border](images/theme-color/editorGroup-border.gif)

- `editorGroup.dropBackground`：拖动编辑器时的背景色。

  ![editorGroup.dropBackground](images/theme-color/editorGroup-dropbackground.gif)

- `editorGroupHeader.noTabsBackground`：使用单个标签页时（设置 `"workbench.editor.showTabs": "single"`）编辑器组标题头的背景色。

  ![editorGroupHeader.noTabsBackground](images/theme-color/editorgroupheader-notabsbackground.gif)

- `editorGroupHeader.tabsBackground`：标签页容器的背景色。

  ![editorGroupHeader.tabsBackground](images/theme-color/editorgroupheader-tabsbackground.gif)

- `editorGroupHeader.tabsBorder`：启用标签页时，编辑器标签页控件下方的边框颜色。

  ![editorGroupHeader.tabsBorder](images/theme-color/editorgroupheader-tabsborder.gif)

- `editorGroupHeader.border`：编辑器组标题头与编辑器之间的边框颜色（如果启用了面包屑导航，则在面包屑导航下方）。
- `editorGroup.emptyBackground`：空编辑器组的背景色。
- `editorGroup.focusedEmptyBorder`：拥有焦点的空编辑器组的边框颜色。
- `editorGroup.dropIntoPromptForeground`：拖动文件时显示在编辑器上方的文字的前景色。这段文字提示用户可以按住 Shift 键拖放到编辑器中。
- `editorGroup.dropIntoPromptBackground`：拖动文件时显示在编辑器上方的文字的背景色。这段文字提示用户可以按住 Shift 键拖放到编辑器中。
- `editorGroup.dropIntoPromptBorder`：拖动文件时显示在编辑器上方的文字的边框颜色。这段文字提示用户可以按住 Shift 键拖放到编辑器中。

- `tab.activeBackground`：活动组中活动标签页的背景色。
- `tab.unfocusedActiveBackground`：非活动编辑器组中活动标签页的背景色。
- `tab.activeForeground`：活动组中活动标签页的前景色。
- `tab.border`：把标签页彼此分隔开的边框。
- `tab.activeBorder`：活动标签页的底部边框。
- `tab.selectedBorderTop`：选中的标签页的顶部边框。标签页是编辑区域中编辑器的容器。一个编辑器组中可以打开多个标签页，可以有多个编辑器组。
- `tab.selectedBackground`：选中的标签页的背景色。标签页是编辑区域中编辑器的容器。一个编辑器组中可以打开多个标签页，可以有多个编辑器组。
- `tab.selectedForeground`：选中的标签页的前景色。标签页是编辑区域中编辑器的容器。一个编辑器组中可以打开多个标签页，可以有多个编辑器组。
- `tab.dragAndDropBorder`：标签页之间的边框，表示可以把一个标签页插入到两个标签页之间。标签页是编辑区域中编辑器的容器。一个编辑器组中可以打开多个标签页，可以有多个编辑器组。
- `tab.unfocusedActiveBorder`：非活动编辑器组中活动标签页的底部边框。
- `tab.activeBorderTop`：活动标签页的顶部边框。
- `tab.unfocusedActiveBorderTop`：非活动编辑器组中活动标签页的顶部边框
- `tab.lastPinnedBorder`：最后一个固定编辑器右侧的边框，用于与未固定的编辑器分隔开。
- `tab.inactiveBackground`：非活动标签页的背景色。
- `tab.unfocusedInactiveBackground`：没有焦点的组中非活动标签页的背景色
- `tab.inactiveForeground`：活动组中非活动标签页的前景色。
- `tab.unfocusedActiveForeground`：非活动编辑器组中活动标签页的前景色。
- `tab.unfocusedInactiveForeground`：非活动编辑器组中非活动标签页的前景色。
- `tab.hoverBackground`：悬停时标签页的背景色
- `tab.unfocusedHoverBackground`：没有焦点的组中悬停时标签页的背景色
- `tab.hoverForeground`：悬停时标签页的前景色
- `tab.unfocusedHoverForeground`：没有焦点的组中悬停时标签页的前景色
- `tab.hoverBorder`：悬停时用于高亮标签页的边框
- `tab.unfocusedHoverBorder`：没有焦点的组中悬停时用于高亮标签页的边框
- `tab.activeModifiedBorder`：活动组中已修改（有未保存更改）的活动标签页的顶部边框。
- `tab.inactiveModifiedBorder`：活动组中已修改（有未保存更改）的非活动标签页的顶部边框。
- `tab.unfocusedActiveModifiedBorder`：没有焦点的组中已修改（有未保存更改）的活动标签页的顶部边框。
- `tab.unfocusedInactiveModifiedBorder`：没有焦点的组中已修改（有未保存更改）的非活动标签页的顶部边框。
- `editorPane.background`：居中编辑器布局中，左右两侧可见的编辑器窗格的背景色。
- `sideBySideEditor.horizontalBorder`：在一个编辑器组中上下并排显示两个编辑器时，把它们分隔开的颜色。
- `sideBySideEditor.verticalBorder`：在一个编辑器组中左右并排显示两个编辑器时，把它们分隔开的颜色。

（上面列表中的几张动图分别演示了 `editorGroup.border`、`editorGroup.dropBackground`、`editorGroupHeader.noTabsBackground`、`editorGroupHeader.tabsBackground`、`editorGroupHeader.tabsBorder` 所对应的位置。）

---

<a id="editor-colors"></a>
## 编辑器颜色（Editor colors）

> 编辑器中最显眼的颜色，是用于语法高亮的标记颜色，它们基于所安装的语言语法。这些颜色由颜色主题定义，但也可以用 `editor.tokenColorCustomizations` 设置自定义。关于修改颜色主题以及可用的标记类型，详见[自定义颜色主题](https://code.visualstudio.com/docs/configure/themes#customize-a-color-theme)。

> 其他所有的编辑器颜色列在这里：

- `editor.background`：编辑器的背景色。
- `editor.foreground`：编辑器的默认前景色。
- `editorLineNumber.foreground`：编辑器行号的颜色。
- `editorLineNumber.activeForeground`：编辑器活动行号的颜色。
- `editorLineNumber.dimmedForeground`：当 editor.renderFinalNewline 设为 dimmed 时，编辑器最后一行的颜色。
- `editorCursor.background`：编辑器光标的背景色。可以自定义被块状光标覆盖的字符的颜色。
- `editorCursor.foreground`：编辑器光标的颜色。
- `editorMultiCursor.primary.foreground`：存在多个光标时，编辑器主光标的颜色。
- `editorMultiCursor.primary.background`：存在多个光标时，编辑器主光标的背景色。可以自定义被块状光标覆盖的字符的颜色。
- `editorMultiCursor.secondary.foreground`：存在多个光标时，编辑器次要光标的颜色。
- `editorMultiCursor.secondary.background`：存在多个光标时，编辑器次要光标的背景色。可以自定义被块状光标覆盖的字符的颜色。
- `editor.placeholder.foreground`：编辑器中占位文字的前景色。
- `editor.compositionBorder`：输入法（IME）组字时的边框颜色。

> 选择颜色在选中一个或多个字符时可见。除了选择内容本身，所有内容相同的区域也会被高亮。

![选择高亮](images/theme-color/selectionhighlight.png)

- `editor.selectionBackground`：编辑器选择的颜色。
- `editor.selectionForeground`：高对比度下选中文字的颜色。
- `editor.inactiveSelectionBackground`：非活动编辑器中选择的颜色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editor.selectionHighlightBackground`：与选择内容相同的区域的颜色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editor.selectionHighlightBorder`：与选择内容相同的区域的边框颜色。

> 单词高亮颜色在光标位于一个符号或单词中时可见。根据这种文件类型可用的语言支持，所有匹配的引用和声明都会被高亮，读取访问和写入访问使用不同的颜色。如果没有可用的文档符号语言支持，就退回到单词高亮。

![出现处高亮](images/theme-color/occurrences.png)

- `editor.wordHighlightBackground`：符号在读取访问时的背景色，例如读取一个变量时。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editor.wordHighlightBorder`：符号在读取访问时的边框颜色，例如读取一个变量时。
- `editor.wordHighlightStrongBackground`：符号在写入访问时的背景色，例如写入一个变量时。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editor.wordHighlightStrongBorder`：符号在写入访问时的边框颜色，例如写入一个变量时。
- `editor.wordHighlightTextBackground`：一个符号的文本出现处的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editor.wordHighlightTextBorder`：一个符号的文本出现处的边框颜色。

> 查找颜色取决于查找 / 替换对话框中当前的查找字符串。

![查找匹配](images/theme-color/findmatches.png)

- `editor.findMatchBackground`：当前搜索匹配项的颜色。
- `editor.findMatchForeground`：当前搜索匹配项的文字颜色。
- `editor.findMatchHighlightForeground`：其他搜索匹配项的前景色。
- `editor.findMatchHighlightBackground`：其他搜索匹配项的颜色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editor.findRangeHighlightBackground`：限制搜索的范围的颜色（在查找小部件中启用“在选定内容中查找”）。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editor.findMatchBorder`：当前搜索匹配项的边框颜色。
- `editor.findMatchHighlightBorder`：其他搜索匹配项的边框颜色。
- `editor.findRangeHighlightBorder`：限制搜索的范围的边框颜色（在查找小部件中启用“在选定内容中查找”）。

> 搜索颜色用于搜索视图的全局搜索结果中。

![搜索结果](images/theme-color/search-colors.png)

- `search.resultsInfoForeground`：搜索视图完成消息中文字的颜色。例如，这个颜色用于显示 “`{x} results in {y} files`”（{y} 个文件中有 {x} 个结果）的文字。

> 搜索编辑器颜色用于高亮搜索编辑器中的结果。它可以与其他查找匹配分开配置，以便在同一个编辑器中更好地区分不同类别的匹配。

![搜索编辑器匹配](images/theme-color/searchEditorMatches.png)

- `searchEditor.findMatchBackground`：搜索编辑器中结果的颜色。
- `searchEditor.findMatchBorder`：搜索编辑器中结果的边框颜色。
- `searchEditor.textInputBorder`：搜索编辑器文本输入框的边框。

> 悬停高亮显示在正在显示悬停提示的那个符号的后面。

![悬停高亮](images/theme-color/hoverhighlight.png)

- `editor.hoverHighlightBackground`：显示悬停提示的那个单词下面的高亮。这个颜色不能是不透明的，以免遮住下面的装饰。

> 当前行通常用背景高亮或边框中的一种来显示（而不是两者都用）。

![行高亮](images/theme-color/line.png)

- `editor.lineHighlightBackground`：光标所在行的高亮背景色。
- `editor.inactiveLineHighlightBackground`：编辑器没有焦点时，光标所在行的高亮背景色。
- `editor.lineHighlightBorder`：光标所在行周围边框的颜色。

> Unicode 高亮的颜色

- `editorUnicodeHighlight.border`：用于高亮 Unicode 字符的边框颜色。
- `editorUnicodeHighlight.background`：用于高亮 Unicode 字符的背景色。

> 链接颜色在点击链接时可见。

![链接](images/theme-color/link.png)

- `editorLink.activeForeground`：活动链接的颜色。

> 范围高亮在选择一个搜索结果时可见。

![范围高亮](images/theme-color/rangehighlight.png)

- `editor.rangeHighlightBackground`：高亮范围的背景色，由快速打开、文件中的符号和查找功能使用。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editor.rangeHighlightBorder`：高亮范围周围边框的颜色。

> 符号高亮在通过 **Go to Definition**（转到定义）等命令导航到一个符号时可见。

- `editor.symbolHighlightBackground`：高亮符号的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editor.symbolHighlightBorder`：高亮符号周围边框的颜色。

> 要看到编辑器中的空白字符，请启用 **Toggle Render Whitespace**（切换呈现空白字符）。

- `editorWhitespace.foreground`：编辑器中空白字符的颜色。

> 要看到编辑器的缩进参考线，请设置 `"editor.guides.indentation": true` 和 `"editor.guides.highlightActiveIndentation": true`。

- `editorIndentGuide.background`：编辑器缩进参考线的颜色。
- `editorIndentGuide.background1`：编辑器缩进参考线的颜色（1）。
- `editorIndentGuide.background2`：编辑器缩进参考线的颜色（2）。
- `editorIndentGuide.background3`：编辑器缩进参考线的颜色（3）。
- `editorIndentGuide.background4`：编辑器缩进参考线的颜色（4）。
- `editorIndentGuide.background5`：编辑器缩进参考线的颜色（5）。
- `editorIndentGuide.background6`：编辑器缩进参考线的颜色（6）。
- `editorIndentGuide.activeBackground`：编辑器活动缩进参考线的颜色。
- `editorIndentGuide.activeBackground1`：编辑器活动缩进参考线的颜色（1）。
- `editorIndentGuide.activeBackground2`：编辑器活动缩进参考线的颜色（2）。
- `editorIndentGuide.activeBackground3`：编辑器活动缩进参考线的颜色（3）。
- `editorIndentGuide.activeBackground4`：编辑器活动缩进参考线的颜色（4）。
- `editorIndentGuide.activeBackground5`：编辑器活动缩进参考线的颜色（5）。
- `editorIndentGuide.activeBackground6`：编辑器活动缩进参考线的颜色（6）。

> 要看到编辑器的内嵌提示，请设置 `"editor.inlineSuggest.enabled": true`（原文如此；内嵌提示（inlay hints）实际由 `editor.inlayHints.enabled` 控制，`editor.inlineSuggest.enabled` 控制的是内联建议）。

- `editorInlayHint.background`：内嵌提示的背景色。
- `editorInlayHint.foreground`：内嵌提示的前景色。
- `editorInlayHint.typeForeground`：类型内嵌提示的前景色
- `editorInlayHint.typeBackground`：类型内嵌提示的背景色
- `editorInlayHint.parameterForeground`：参数内嵌提示的前景色
- `editorInlayHint.parameterBackground`：参数内嵌提示的背景色

> 要看到编辑器标尺，请用 `"editor.rulers"` 定义它们的位置

- `editorRuler.foreground`：编辑器标尺的颜色。

- `editor.linkedEditingBackground`：编辑器处于链接编辑模式时的背景色。

> CodeLens：

![CodeLens](images/theme-color/codelens.png)

- `editorCodeLens.foreground`：编辑器 CodeLens 的前景色。

> 灯泡：

- `editorLightBulb.foreground`：灯泡操作图标所使用的颜色。
- `editorLightBulbAutoFix.foreground`：灯泡自动修复操作图标所使用的颜色。
- `editorLightBulbAi.foreground`：灯泡 AI 图标所使用的颜色。

> 括号匹配：

![括号颜色](images/theme-color/bracket-colors.png)

- `editorBracketMatch.background`：匹配括号后面的背景色。
- `editorBracketMatch.border`：匹配括号方框的颜色。
- `editorBracketMatch.foreground`：匹配括号的前景色。

> 括号对着色：

- `editorBracketHighlight.foreground1`：括号的前景色（1）。需要启用括号对着色。
- `editorBracketHighlight.foreground2`：括号的前景色（2）。需要启用括号对着色。
- `editorBracketHighlight.foreground3`：括号的前景色（3）。需要启用括号对着色。
- `editorBracketHighlight.foreground4`：括号的前景色（4）。需要启用括号对着色。
- `editorBracketHighlight.foreground5`：括号的前景色（5）。需要启用括号对着色。
- `editorBracketHighlight.foreground6`：括号的前景色（6）。需要启用括号对着色。
- `editorBracketHighlight.unexpectedBracket.foreground`：意外括号（不匹配的括号）的前景色。

> 括号对参考线：

- `editorBracketPairGuide.activeBackground1`：活动括号对参考线的背景色（1）。需要启用括号对参考线。
- `editorBracketPairGuide.activeBackground2`：活动括号对参考线的背景色（2）。需要启用括号对参考线。
- `editorBracketPairGuide.activeBackground3`：活动括号对参考线的背景色（3）。需要启用括号对参考线。
- `editorBracketPairGuide.activeBackground4`：活动括号对参考线的背景色（4）。需要启用括号对参考线。
- `editorBracketPairGuide.activeBackground5`：活动括号对参考线的背景色（5）。需要启用括号对参考线。
- `editorBracketPairGuide.activeBackground6`：活动括号对参考线的背景色（6）。需要启用括号对参考线。

- `editorBracketPairGuide.background1`：非活动括号对参考线的背景色（1）。需要启用括号对参考线。
- `editorBracketPairGuide.background2`：非活动括号对参考线的背景色（2）。需要启用括号对参考线。
- `editorBracketPairGuide.background3`：非活动括号对参考线的背景色（3）。需要启用括号对参考线。
- `editorBracketPairGuide.background4`：非活动括号对参考线的背景色（4）。需要启用括号对参考线。
- `editorBracketPairGuide.background5`：非活动括号对参考线的背景色（5）。需要启用括号对参考线。
- `editorBracketPairGuide.background6`：非活动括号对参考线的背景色（6）。需要启用括号对参考线。

> 折叠：

- `editor.foldBackground`：折叠范围的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editor.foldPlaceholderForeground`：折叠范围第一行之后的折叠文字的颜色。

> 概览标尺：

> 这个标尺位于编辑器右边缘的滚动条下方，提供编辑器中装饰的概览。

- `editorOverviewRuler.background`：编辑器概览标尺的背景色。只在启用了缩略图、并且缩略图位于编辑器右侧时使用。
- `editorOverviewRuler.border`：概览标尺边框的颜色。
- `editorOverviewRuler.findMatchForeground`：概览标尺中查找匹配项的标记颜色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editorOverviewRuler.rangeHighlightForeground`：概览标尺中高亮范围的标记颜色，例如由快速打开、文件中的符号和查找功能产生的高亮。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editorOverviewRuler.selectionHighlightForeground`：概览标尺中选择高亮的标记颜色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editorOverviewRuler.wordHighlightForeground`：概览标尺中符号高亮的标记颜色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editorOverviewRuler.wordHighlightStrongForeground`：概览标尺中写入访问的符号高亮的标记颜色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editorOverviewRuler.wordHighlightTextForeground`：概览标尺中一个符号的文本出现处的标记颜色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editorOverviewRuler.modifiedForeground`：概览标尺中修改内容的标记颜色。
- `editorOverviewRuler.addedForeground`：概览标尺中新增内容的标记颜色。
- `editorOverviewRuler.deletedForeground`：概览标尺中删除内容的标记颜色。
- `editorOverviewRuler.errorForeground`：概览标尺中错误的标记颜色。
- `editorOverviewRuler.warningForeground`：概览标尺中警告的标记颜色。
- `editorOverviewRuler.infoForeground`：概览标尺中信息的标记颜色。
- `editorOverviewRuler.bracketMatchForeground`：概览标尺中匹配括号的标记颜色。
- `editorOverviewRuler.inlineChatInserted`：概览标尺中内联聊天插入内容的标记颜色。
- `editorOverviewRuler.inlineChatRemoved`：概览标尺中内联聊天删除内容的标记颜色。
- `editorOverviewRuler.commentDraftForeground`：编辑器概览标尺中带有草稿注释的注释线程的装饰颜色。这个颜色应该是不透明的。

> 错误和警告：

- `editorError.foreground`：编辑器中错误波浪线的前景色。
- `editorError.border`：编辑器中错误方框的边框颜色。
- `editorError.background`：编辑器中错误文字的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editorWarning.foreground`：编辑器中警告波浪线的前景色。
- `editorWarning.border`：编辑器中警告方框的边框颜色。
- `editorWarning.background`：编辑器中警告文字的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editorInfo.foreground`：编辑器中信息波浪线的前景色。
- `editorInfo.border`：编辑器中信息方框的边框颜色。
- `editorInfo.background`：编辑器中信息文字的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editorHint.foreground`：编辑器中提示的前景色。
- `editorHint.border`：编辑器中提示方框的边框颜色。
- `problemsErrorIcon.foreground`：问题中错误图标所使用的颜色。
- `problemsWarningIcon.foreground`：问题中警告图标所使用的颜色。
- `problemsInfoIcon.foreground`：问题中信息图标所使用的颜色。

> 未使用的源代码：

- `editorUnnecessaryCode.border`：编辑器中不必要的（未使用的）源代码的边框颜色。
- `editorUnnecessaryCode.opacity`：编辑器中不必要的（未使用的）源代码的不透明度。例如，`"#000000c0"` 会以 75% 的不透明度渲染代码。对于高对比度主题，请使用 `"editorUnnecessaryCode.border"` 主题颜色给不必要的代码加下划线，而不是让它变淡。

> 装订线（gutter）包含字形边距和行号：

- `editorGutter.background`：编辑器装订线的背景色。装订线包含字形边距和行号。
- `editorGutter.modifiedBackground`：编辑器装订线中已修改的行的背景色。
- `editorGutter.modifiedSecondaryBackground`：编辑器装订线中已修改的行的次要背景色。
- `editorGutter.addedBackground`：编辑器装订线中新增的行的背景色。
- `editorGutter.addedSecondaryBackground`：编辑器装订线中新增的行的次要背景色。
- `editorGutter.deletedBackground`：编辑器装订线中已删除的行的背景色。
- `editorGutter.deletedSecondaryBackground`：编辑器装订线中已删除的行的次要背景色。
- `editorGutter.commentRangeForeground`：编辑器装订线中注释范围的装饰颜色。
- `editorGutter.commentGlyphForeground`：编辑器装订线中注释字形的装饰颜色。
- `editorGutter.commentUnresolvedGlyphForeground`：编辑器装订线中未解决的注释线程的注释字形的装饰颜色。
- `editorGutter.foldingControlForeground`：编辑器装订线中折叠控件的颜色。
- `editorGutter.itemGlyphForeground`：编辑器装订线中装订线项字形的装饰颜色。
- `editorGutter.itemBackground`：编辑器装订线中装订线项背景的装饰颜色。这个颜色应该是不透明的。
- `editorGutter.commentDraftGlyphForeground`：编辑器装订线中带有草稿注释的注释线程的注释字形的装饰颜色。

> 编辑器注释小部件可以在审阅拉取请求时看到：

- `editorCommentsWidget.resolvedBorder`：已解决的注释的边框和箭头的颜色。
- `editorCommentsWidget.unresolvedBorder`：未解决的注释的边框和箭头的颜色。
- `editorCommentsWidget.rangeBackground`：注释范围的背景色。
- `editorCommentsWidget.rangeActiveBackground`：当前选中或悬停的注释范围的背景色。
- `editorCommentsWidget.replyInputBackground`：注释回复输入框的背景色。

> 编辑器内联编辑可以在使用 Copilot 建议下一处修改时看到：

- `inlineEdit.gutterIndicator.primaryBorder`：主内联编辑装订线指示器的边框颜色。
- `inlineEdit.gutterIndicator.primaryForeground`：主内联编辑装订线指示器的前景色。
- `inlineEdit.gutterIndicator.primaryBackground`：主内联编辑装订线指示器的背景色。
- `inlineEdit.gutterIndicator.secondaryBorder`：次要内联编辑装订线指示器的边框颜色。
- `inlineEdit.gutterIndicator.secondaryForeground`：次要内联编辑装订线指示器的前景色。
- `inlineEdit.gutterIndicator.secondaryBackground`：次要内联编辑装订线指示器的背景色。
- `inlineEdit.gutterIndicator.successfulBorder`：成功状态的内联编辑装订线指示器的边框颜色。
- `inlineEdit.gutterIndicator.successfulForeground`：成功状态的内联编辑装订线指示器的前景色。
- `inlineEdit.gutterIndicator.successfulBackground`：成功状态的内联编辑装订线指示器的背景色。
- `inlineEdit.gutterIndicator.background`：内联编辑装订线指示器的背景色。
- `inlineEdit.originalBackground`：内联编辑中原始文字的背景色。
- `inlineEdit.modifiedBackground`：内联编辑中修改后文字的背景色。
- `inlineEdit.originalChangedLineBackground`：内联编辑的原始文字中已更改的行的背景色。
- `inlineEdit.originalChangedTextBackground`：内联编辑的原始文字中已更改的文字的叠加颜色。
- `inlineEdit.modifiedChangedLineBackground`：内联编辑的修改后文字中已更改的行的背景色。
- `inlineEdit.modifiedChangedTextBackground`：内联编辑的修改后文字中已更改的文字的叠加颜色。
- `inlineEdit.originalBorder`：内联编辑中原始文字的边框颜色。
- `inlineEdit.modifiedBorder`：内联编辑中修改后文字的边框颜色。
- `inlineEdit.tabWillAcceptModifiedBorder`：按 Tab 将接受内联编辑时，内联编辑小部件的修改后边框颜色。
- `inlineEdit.tabWillAcceptOriginalBorder`：按 Tab 将接受内联编辑时，内联编辑小部件在原始文字上方的原始边框颜色。

---

<a id="diff-editor-colors"></a>
## 差异编辑器颜色（Diff editor colors）

> 为插入和删除的文字着色时，使用背景色或边框颜色中的一种，而不要两者都用。

- `diffEditor.insertedTextBackground`：插入的文字的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `diffEditor.insertedTextBorder`：插入的文字的轮廓颜色。
- `diffEditor.removedTextBackground`：删除的文字的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `diffEditor.removedTextBorder`：删除的文字的轮廓颜色。
- `diffEditor.border`：两个文本编辑器之间的边框颜色。
- `diffEditor.diagonalFill`：差异编辑器斜线填充的颜色。斜线填充用于并排的差异视图中。
- `diffEditor.insertedLineBackground`：插入的行的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `diffEditor.removedLineBackground`：删除的行的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `diffEditorGutter.insertedLineBackground`：插入了行的边距处的背景色。
- `diffEditorGutter.removedLineBackground`：删除了行的边距处的背景色。
- `diffEditorOverview.insertedForeground`：差异概览标尺中插入内容的前景色。
- `diffEditorOverview.removedForeground`：差异概览标尺中删除内容的前景色。
- `diffEditor.unchangedRegionBackground`：差异编辑器中未更改的块的颜色。
- `diffEditor.unchangedRegionForeground`：差异编辑器中未更改的块的前景色。
- `diffEditor.unchangedRegionShadow`：未更改区域小部件周围阴影的颜色。
- `diffEditor.unchangedCodeBackground`：差异编辑器中未更改的代码的背景色。
- `diffEditor.move.border`：差异编辑器中被移动的文字的边框颜色。
- `diffEditor.moveActive.border`：差异编辑器中被移动的文字的活动边框颜色。
- `multiDiffEditor.headerBackground`：差异编辑器标题头的背景色
- `multiDiffEditor.background`：多文件差异编辑器的背景色
- `multiDiffEditor.border`：多文件差异编辑器的边框颜色

---

<a id="chat-colors"></a>
## 聊天颜色（Chat colors）

- `chat.requestBorder`：聊天请求的边框颜色。
- `chat.requestBackground`：聊天请求的背景色。
- `chat.slashCommandBackground`：聊天斜杠命令的背景色。
- `chat.slashCommandForeground`：聊天斜杠命令的前景色。
- `chat.avatarBackground`：聊天头像的背景色。
- `chat.avatarForeground`：聊天头像的前景色。
- `chat.editedFileForeground`：已编辑文件列表中，聊天编辑过的文件的前景色。
- `chat.linesAddedForeground`：聊天代码块标签中新增行数的前景色。
- `chat.linesRemovedForeground`：聊天代码块标签中删除行数的前景色。
- `chat.requestCodeBorder`：聊天请求气泡中代码块的边框颜色。
- `chat.requestBubbleBackground`：聊天请求气泡的背景色。
- `chat.requestBubbleHoverBackground`：悬停时聊天请求气泡的背景色。
- `chat.checkpointSeparator`：聊天检查点分隔线的颜色。
- `chat.thinkingShimmer`：“思考中 / 工作中”标签的闪烁高亮。
- `chatManagement.sashBorder`：聊天管理编辑器中拆分视图分隔条的边框颜色。

---

<a id="agent-sessions-colors"></a>
## 智能体会话颜色（Agent sessions colors）

- `agents.background`：智能体会话窗口外壳和渐变底色的背景色。
- `agentsPanel.background`：智能体会话窗口中卡片面板（聊天、文件、终端）的背景色。
- `agentsPanel.foreground`：智能体会话窗口中卡片面板（聊天、文件、终端）的前景色。
- `agentsPanel.border`：智能体会话窗口中卡片面板（聊天、文件、终端）的边框颜色。
- `agentsCard.border`：智能体会话窗口中浮动内容卡片（会话网格和自定义视图网格）的边框颜色。
- `agentsBottomPanel.border`：智能体会话窗口中底部面板的边框颜色。
- `agentsGradient.tintColor`：智能体会话窗口外壳的背景渐变中使用的色调。
- `agentFeedbackEditorWidget.background`：编辑器中显示的智能体反馈小部件的背景色。
- `agentFeedbackEditorWidget.border`：编辑器中显示的智能体反馈小部件的边框颜色。
- `agentFeedbackInputWidget.border`：编辑器中显示的智能体反馈输入小部件的边框颜色。
- `agentsUpdateButton.downloadingBackground`：智能体会话窗口中用于显示下载进度的更新按钮的背景色。
- `agentsUpdateButton.downloadedBackground`：智能体会话窗口中下载完成时更新按钮的背景色。
- `agentsChatInput.background`：智能体会话窗口中聊天输入框的背景色。
- `agentsChatInput.foreground`：智能体会话窗口中聊天输入框的前景色。
- `agentsChatInput.border`：智能体会话窗口中聊天输入框的边框颜色。
- `agentsChatInput.focusBorder`：智能体会话窗口中聊天输入框拥有焦点时的边框颜色。
- `agentsChatInput.placeholderForeground`：智能体会话窗口中聊天输入框中占位文字的颜色。
- `agentsNewSessionButton.background`：智能体会话侧边栏中“新建会话”按钮的背景色。
- `agentsNewSessionButton.foreground`：智能体会话侧边栏中“新建会话”按钮的前景色。
- `agentsNewSessionButton.border`：智能体会话侧边栏中“新建会话”按钮的边框颜色。
- `agentsNewSessionButton.hoverBackground`：智能体会话侧边栏中悬停时“新建会话”按钮的背景色。
- `agentsBadge.background`：智能体会话窗口中徽章的背景色。
- `agentsBadge.foreground`：智能体会话窗口中徽章的前景色。
- `agentsUnreadBadge.background`：侧边栏开关上未读会话数量徽章的背景色。
- `agentsUnreadBadge.foreground`：侧边栏开关上未读会话数量徽章的前景色。
- `activeSessionView.background`：智能体会话窗口中活动会话视图的背景色。
- `inactiveSessionView.background`：智能体会话窗口中非活动会话视图的背景色。
- `activeSessionView.foreground`：智能体会话窗口中活动会话视图的前景色。
- `inactiveSessionView.foreground`：智能体会话窗口中非活动会话视图的前景色。
- `agentsMobileDiff.addedForeground`：智能体会话窗口中移动端更改列表和差异叠加层中，用于新增文件和新增行的前景色。
- `agentsMobileDiff.modifiedForeground`：智能体会话窗口中移动端更改列表中，用于修改的文件的前景色。
- `agentsMobileDiff.deletedForeground`：智能体会话窗口中移动端更改列表和差异叠加层中，用于删除的文件和删除的行的前景色。

---

<a id="inline-chat-colors"></a>
## 内联聊天颜色（Inline Chat colors）

- `inlineChat.background`：交互式编辑器（内联聊天）小部件的背景色。
- `inlineChat.foreground`：交互式编辑器（内联聊天）小部件的前景色
- `inlineChat.border`：交互式编辑器（内联聊天）小部件的边框颜色。
- `inlineChat.shadow`：交互式编辑器（内联聊天）小部件的阴影颜色。
- `inlineChatInput.border`：交互式编辑器输入框的边框颜色。
- `inlineChatInput.focusBorder`：交互式编辑器输入框拥有焦点时的边框颜色。
- `inlineChatInput.placeholderForeground`：交互式编辑器输入框中占位文字的前景色。
- `inlineChatInput.background`：交互式编辑器输入框的背景色。
- `inlineChatDiff.inserted`：交互式编辑器输入中插入的文字的背景色。
- `inlineChatDiff.removed`：交互式编辑器输入中删除的文字的背景色。

---

<a id="panel-chat-colors"></a>
## 面板聊天颜色（Panel Chat colors）

- `interactive.activeCodeBorder`：编辑器拥有焦点时，当前交互式代码单元格的边框颜色。
- `interactive.inactiveCodeBorder`：编辑器没有焦点时，当前交互式代码单元格的边框颜色。

---

<a id="editor-widget-colors"></a>
## 编辑器小部件颜色（Editor widget colors）

> 编辑器小部件显示在编辑器内容的前面。例如查找 / 替换对话框、建议小部件和编辑器悬停提示。

- `editorWidget.foreground`：编辑器小部件（如查找 / 替换）的前景色。
- `editorWidget.background`：编辑器小部件（如查找 / 替换）的背景色。
- `editorWidget.border`：编辑器小部件的边框颜色，除非小部件不包含边框或定义了自己的边框颜色。
- `editorWidget.resizeBorder`：编辑器小部件调整大小条的边框颜色。只有当小部件选择使用调整大小边框、并且这个颜色没有被小部件覆盖时，才会使用这个颜色。

- `editorSuggestWidget.background`：建议小部件的背景色。
- `editorSuggestWidget.border`：建议小部件的边框颜色。
- `editorSuggestWidget.foreground`：建议小部件的前景色。
- `editorSuggestWidget.focusHighlightForeground`：某一项拥有焦点时，建议小部件中匹配高亮的颜色。
- `editorSuggestWidget.highlightForeground`：建议小部件中匹配高亮的颜色。
- `editorSuggestWidget.selectedBackground`：建议小部件中选中条目的背景色。
- `editorSuggestWidget.selectedForeground`：建议小部件中选中条目的前景色。
- `editorSuggestWidget.selectedIconForeground`：建议小部件中选中条目的图标前景色。
- `editorSuggestWidgetStatus.foreground`：建议小部件状态栏的前景色。

- `editorHoverWidget.foreground`：编辑器悬停提示的前景色。
- `editorHoverWidget.background`：编辑器悬停提示的背景色。
- `editorHoverWidget.border`：编辑器悬停提示的边框颜色。
- `editorHoverWidget.highlightForeground`：参数提示中活动项的前景色。
- `editorHoverWidget.statusBarBackground`：编辑器悬停提示状态栏的背景色。

- `editorGhostText.border`：内联补全提供者和建议预览所显示的幽灵文字的边框颜色。
- `editorGhostText.background`：编辑器中幽灵文字的背景色。
- `editorGhostText.foreground`：内联补全提供者和建议预览所显示的幽灵文字的前景色。

- `editorStickyScroll.background`：编辑器粘性滚动的背景色。
- `editorStickyScroll.border`：编辑器中粘性滚动的边框颜色。
- `editorStickyScroll.shadow`：编辑器中粘性滚动的阴影颜色。
- `editorStickyScrollGutter.background`：编辑器中粘性滚动的装订线部分的背景色。
- `editorStickyScrollHover.background`：悬停时编辑器粘性滚动的背景色。

> 调试异常小部件是一个速览视图，在调试停在一个异常处时显示在编辑器中。

- `debugExceptionWidget.background`：异常小部件的背景色。
- `debugExceptionWidget.border`：异常小部件的边框颜色。

> 编辑器标记视图在编辑器中导航到错误和警告时显示（**Go to Next Error or Warning**（转到下一个错误或警告）命令）。

- `editorMarkerNavigation.background`：编辑器标记导航小部件的背景色。
- `editorMarkerNavigationError.background`：编辑器标记导航小部件的错误颜色。
- `editorMarkerNavigationWarning.background`：编辑器标记导航小部件的警告颜色。
- `editorMarkerNavigationInfo.background`：编辑器标记导航小部件的信息颜色。
- `editorMarkerNavigationError.headerBackground`：编辑器标记导航小部件中错误标题的背景色。
- `editorMarkerNavigationWarning.headerBackground`：编辑器标记导航小部件中警告标题的背景色。
- `editorMarkerNavigationInfo.headerBackground`：编辑器标记导航小部件中信息标题的背景色。

---

<a id="peek-view-colors"></a>
## 速览视图颜色（Peek view colors）

> 速览视图用于在编辑器内部以一个视图的形式显示引用和声明。

![速览视图](images/theme-color/peek-view.png)

- `peekView.border`：速览视图的边框和箭头的颜色。
- `peekViewEditor.background`：速览视图编辑器的背景色。
- `peekViewEditorGutter.background`：速览视图编辑器中装订线的背景色。
- `peekViewEditor.matchHighlightBackground`：速览视图编辑器中匹配的高亮颜色。
- `peekViewEditor.matchHighlightBorder`：速览视图编辑器中匹配高亮的边框颜色。
- `peekViewResult.background`：速览视图结果列表的背景色。
- `peekViewResult.fileForeground`：速览视图结果列表中文件节点的前景色。
- `peekViewResult.lineForeground`：速览视图结果列表中行节点的前景色。
- `peekViewResult.matchHighlightBackground`：速览视图结果列表中匹配的高亮颜色。
- `peekViewResult.selectionBackground`：速览视图结果列表中选中条目的背景色。
- `peekViewResult.selectionForeground`：速览视图结果列表中选中条目的前景色。
- `peekViewTitle.background`：速览视图标题区域的背景色。
- `peekViewTitleDescription.foreground`：速览视图标题信息的颜色。
- `peekViewTitleLabel.foreground`：速览视图标题的颜色。
- `peekViewEditorStickyScroll.background`：速览视图编辑器中粘性滚动的背景色。
- `peekViewEditorStickyScrollGutter.background`：速览视图编辑器中粘性滚动的装订线部分的背景色。

---

<a id="merge-conflicts-colors"></a>
## 合并冲突颜色（Merge conflicts colors）

> 当编辑器中包含特殊的差异范围（合并冲突标记）时，会显示合并冲突装饰。

![合并范围](images/theme-color/merge-ranges.png)

- `merge.currentHeaderBackground`：内联合并冲突中“当前”部分标题的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `merge.currentContentBackground`：内联合并冲突中“当前”部分内容的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `merge.incomingHeaderBackground`：内联合并冲突中“传入”部分标题的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `merge.incomingContentBackground`：内联合并冲突中“传入”部分内容的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `merge.border`：内联合并冲突中标题和分隔线的边框颜色。
- `merge.commonContentBackground`：内联合并冲突中共同祖先内容的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `merge.commonHeaderBackground`：内联合并冲突中共同祖先标题的背景色。这个颜色不能是不透明的，以免遮住下面的装饰。
- `editorOverviewRuler.currentContentForeground`：内联合并冲突中“当前”部分在概览标尺中的前景色。
- `editorOverviewRuler.incomingContentForeground`：内联合并冲突中“传入”部分在概览标尺中的前景色。
- `editorOverviewRuler.commonContentForeground`：内联合并冲突中共同祖先在概览标尺中的前景色。
- `editorOverviewRuler.commentForeground`：编辑器概览标尺中已解决的注释的装饰颜色。这个颜色应该是不透明的。
- `editorOverviewRuler.commentUnresolvedForeground`：编辑器概览标尺中未解决的注释的装饰颜色。这个颜色应该是不透明的。
- `mergeEditor.change.background`：更改的背景色。
- `mergeEditor.change.word.background`：单词级更改的背景色。
- `mergeEditor.conflict.unhandledUnfocused.border`：未处理、没有焦点的冲突的边框颜色。
- `mergeEditor.conflict.unhandledFocused.border`：未处理、拥有焦点的冲突的边框颜色。
- `mergeEditor.conflict.handledUnfocused.border`：已处理、没有焦点的冲突的边框颜色。
- `mergeEditor.conflict.handledFocused.border`：已处理、拥有焦点的冲突的边框颜色。
- `mergeEditor.conflict.handled.minimapOverViewRuler`：已处理的冲突在缩略图 / 概览标尺中的前景色（原文描述为“输入 1 中更改的前景色”，疑为复制错误）。
- `mergeEditor.conflict.unhandled.minimapOverViewRuler`：未处理的冲突在缩略图 / 概览标尺中的前景色（原文描述为“输入 1 中更改的前景色”，疑为复制错误）。
- `mergeEditor.conflictingLines.background`：“Conflicting Lines”（冲突行）文字的背景色。
- `mergeEditor.changeBase.background`：基础版本中更改的背景色。
- `mergeEditor.changeBase.word.background`：基础版本中单词级更改的背景色。
- `mergeEditor.conflict.input1.background`：输入 1 中装饰的背景色。
- `mergeEditor.conflict.input2.background`：输入 2 中装饰的背景色。

---

<a id="panel-colors"></a>
## 面板颜色（Panel colors）

> 面板显示在编辑区域的下方，包含输出、集成终端等视图。

- `panel.background`：面板的背景色。
- `panel.border`：把面板与编辑器分隔开的面板边框颜色。
- `panel.dropBorder`：面板标题的拖放反馈颜色。面板显示在编辑区域下方，包含输出、集成终端等视图。
- `panelTitle.activeBorder`：活动面板标题的边框颜色。
- `panelTitle.activeForeground`：活动面板的标题颜色。
- `panelTitle.inactiveForeground`：非活动面板的标题颜色。
- `panelTitle.border`：面板标题底部、把标题与视图分隔开的边框颜色。面板显示在编辑区域下方，包含输出、集成终端等视图。
- `panelTitleBadge.background`：面板标题徽章的背景色。面板显示在编辑区域下方，包含输出、集成终端等视图。
- `panelTitleBadge.foreground`：面板标题徽章的前景色。面板显示在编辑区域下方，包含输出、集成终端等视图。
- `panelInput.border`：面板中输入框的边框。
- `panelSection.border`：在面板中水平堆叠多个视图时使用的面板分区边框颜色。面板显示在编辑区域下方，包含输出、集成终端等视图。
- `panelSection.dropBackground`：面板分区的拖放反馈颜色。这个颜色应该带有透明度，以便面板分区仍然可以透出来。面板显示在编辑区域下方，包含输出、集成终端等视图。
- `panelSectionHeader.background`：面板分区标题的背景色。面板显示在编辑区域下方，包含输出、集成终端等视图。
- `panelSectionHeader.foreground`：面板分区标题的前景色。面板显示在编辑区域下方，包含输出、集成终端等视图。
- `panelStickyScroll.background`：面板中粘性滚动的背景色。
- `panelStickyScroll.border`：面板中粘性滚动的边框颜色。
- `panelStickyScroll.shadow`：面板中粘性滚动的阴影颜色。
- `panelSectionHeader.border`：在面板中垂直堆叠多个视图时使用的面板分区标题边框颜色。面板显示在编辑区域下方，包含输出、集成终端等视图。
- `outputView.background`：输出视图的背景色。
- `outputViewStickyScroll.background`：输出视图粘性滚动的背景色。

---

<a id="status-bar-colors"></a>
## 状态栏颜色（Status Bar colors）

> 状态栏显示在工作台的底部。

- `statusBar.background`：标准状态栏的背景色。
- `statusBar.foreground`：状态栏的前景色。
- `statusBar.border`：把状态栏与编辑器分隔开的状态栏边框颜色。
- `statusBar.debuggingBackground`：正在调试程序时状态栏的背景色。
- `statusBar.debuggingForeground`：正在调试程序时状态栏的前景色。
- `statusBar.debuggingBorder`：正在调试程序时，把状态栏与编辑器分隔开的状态栏边框颜色。
- `statusBar.noFolderForeground`：没有打开文件夹时状态栏的前景色。
- `statusBar.noFolderBackground`：没有打开文件夹时状态栏的背景色。
- `statusBar.noFolderBorder`：没有打开文件夹时，把状态栏与编辑器分隔开的状态栏边框颜色。
- `statusBarItem.activeBackground`：点击时状态栏项的背景色。
- `statusBarItem.hoverForeground`：悬停时状态栏项的前景色。状态栏显示在窗口底部。
- `statusBarItem.hoverBackground`：悬停时状态栏项的背景色。
- `statusBarItem.prominentForeground`：状态栏突出项的前景色。
- `statusBarItem.prominentBackground`：状态栏突出项的背景色。
- `statusBarItem.prominentHoverForeground`：悬停时状态栏突出项的前景色。突出项会从其他状态栏条目中突出显示，以表示重要性。状态栏显示在窗口底部。
- `statusBarItem.prominentHoverBackground`：悬停时状态栏突出项的背景色。
- `statusBarItem.remoteBackground`：状态栏上远程指示器的背景色。
- `statusBarItem.remoteForeground`：状态栏上远程指示器的前景色。
- `statusBarItem.remoteHoverBackground`：悬停时状态栏上远程指示器的背景色。
- `statusBarItem.remoteHoverForeground`：悬停时状态栏上远程指示器的前景色。
- `statusBarItem.errorBackground`：状态栏错误项的背景色。错误项会从其他状态栏条目中突出显示，以表示错误状态。
- `statusBarItem.errorForeground`：状态栏错误项的前景色。错误项会从其他状态栏条目中突出显示，以表示错误状态。
- `statusBarItem.errorHoverBackground`：悬停时状态栏错误项的背景色。错误项会从其他状态栏条目中突出显示，以表示错误状态。状态栏显示在窗口底部。
- `statusBarItem.errorHoverForeground`：悬停时状态栏错误项的前景色。错误项会从其他状态栏条目中突出显示，以表示错误状态。状态栏显示在窗口底部。
- `statusBarItem.warningBackground`：状态栏警告项的背景色。警告项会从其他状态栏条目中突出显示，以表示警告状态。状态栏显示在窗口底部。
- `statusBarItem.warningForeground`：状态栏警告项的前景色。警告项会从其他状态栏条目中突出显示，以表示警告状态。状态栏显示在窗口底部。
- `statusBarItem.warningHoverBackground`：悬停时状态栏警告项的背景色。警告项会从其他状态栏条目中突出显示，以表示警告状态。状态栏显示在窗口底部。
- `statusBarItem.warningHoverForeground`：悬停时状态栏警告项的前景色。警告项会从其他状态栏条目中突出显示，以表示警告状态。状态栏显示在窗口底部。
- `statusBarItem.compactHoverBackground`：悬停在包含两个悬停区域的项上时，状态栏项的背景色。状态栏显示在窗口底部。
- `statusBarItem.focusBorder`：通过键盘导航获得焦点时状态栏项的边框颜色。状态栏显示在窗口底部。
- `statusBar.focusBorder`：通过键盘导航获得焦点时状态栏的边框颜色。状态栏显示在窗口底部。
- `statusBarItem.offlineBackground`：工作台离线时状态栏项的背景色。
- `statusBarItem.offlineForeground`：工作台离线时状态栏项的前景色。
- `statusBarItem.offlineHoverForeground`：工作台离线时状态栏项的悬停前景色。
- `statusBarItem.offlineHoverBackground`：工作台离线时状态栏项的悬停背景色。

> 突出项会从其他状态栏条目中突出显示，以表示重要性。一个例子是 **Toggle Tab Key Moves Focus**（切换 Tab 键移动焦点）命令的模式指示器。

---

<a id="title-bar-colors"></a>
## 标题栏颜色（Title Bar colors）

- `titleBar.activeBackground`：窗口处于活动状态时标题栏的背景色。
- `titleBar.activeForeground`：窗口处于活动状态时标题栏的前景色。
- `titleBar.inactiveBackground`：窗口处于非活动状态时标题栏的背景色。
- `titleBar.inactiveForeground`：窗口处于非活动状态时标题栏的前景色。
- `titleBar.border`：标题栏的边框颜色。

---

<a id="menu-bar-colors"></a>
## 菜单栏颜色（Menu Bar colors）

- `menubar.selectionForeground`：菜单栏中选中的菜单项的前景色。
- `menubar.selectionBackground`：菜单栏中选中的菜单项的背景色。
- `menubar.selectionBorder`：菜单栏中选中的菜单项的边框颜色。
- `menu.foreground`：菜单项的前景色。
- `menu.background`：菜单项的背景色。
- `menu.selectionForeground`：菜单中选中的菜单项的前景色。
- `menu.selectionBackground`：菜单中选中的菜单项的背景色。
- `menu.selectionBorder`：菜单中选中的菜单项的边框颜色。
- `menu.separatorBackground`：菜单中分隔线菜单项的颜色。
- `menu.border`：菜单的边框颜色。

---

<a id="command-center-colors"></a>
## 命令中心颜色（Command Center colors）

- `commandCenter.foreground`：命令中心的前景色。
- `commandCenter.activeForeground`：命令中心的活动前景色。
- `commandCenter.background`：命令中心的背景色。
- `commandCenter.activeBackground`：命令中心的活动背景色。
- `commandCenter.border`：命令中心的边框颜色。
- `commandCenter.inactiveForeground`：窗口处于非活动状态时命令中心的前景色。
- `commandCenter.inactiveBorder`：窗口处于非活动状态时命令中心的边框颜色。
- `commandCenter.activeBorder`：命令中心的活动边框颜色。
- `commandCenter.debuggingBackground`：正在调试程序时命令中心的背景色。

---

<a id="notification-colors"></a>
## 通知颜色（Notification colors）

> 通知弹窗从工作台的右下角向上滑出。

![通知弹窗](images/theme-color/notification-toast.png)

> 在通知中心中打开后，它们显示为一个带有标题的列表：

![通知中心](images/theme-color/notification-center.png)

- `notificationCenter.border`：通知中心的边框颜色。
- `notificationCenterHeader.foreground`：通知中心标题的前景色。
- `notificationCenterHeader.background`：通知中心标题的背景色。
- `notificationToast.border`：通知弹窗的边框颜色。
- `notifications.foreground`：通知的前景色。
- `notifications.background`：通知的背景色。
- `notifications.border`：通知中心中把一条通知与其他通知分隔开的边框颜色。
- `notificationLink.foreground`：通知中链接的前景色。
- `notificationsErrorIcon.foreground`：通知错误图标所使用的颜色。
- `notificationsWarningIcon.foreground`：通知警告图标所使用的颜色。
- `notificationsInfoIcon.foreground`：通知信息图标所使用的颜色。

---

<a id="banner-colors"></a>
## 横幅颜色（Banner colors）

> 横幅出现在标题栏下方，可见时横跨整个工作台的宽度。

- `banner.background`：横幅的背景色。
- `banner.foreground`：横幅的前景色。
- `banner.iconForeground`：横幅文字前面的图标的颜色。

---

<a id="extensions-colors"></a>
## 扩展颜色（Extensions colors）

- `extensionButton.prominentForeground`：扩展视图中按钮的前景色（例如 **Install**（安装）按钮）。
- `extensionButton.prominentBackground`：扩展视图中按钮的背景色。
- `extensionButton.prominentHoverBackground`：扩展视图中按钮的悬停背景色。
- `extensionButton.background`：扩展操作按钮的背景色。
- `extensionButton.foreground`：扩展操作按钮的前景色。
- `extensionButton.hoverBackground`：扩展操作按钮的悬停背景色。
- `extensionButton.separator`：扩展操作按钮的分隔线颜色。
- `extensionButton.border`：扩展操作按钮的边框颜色。
- `extensionBadge.remoteBackground`：扩展视图中远程徽章的背景色。
- `extensionBadge.remoteForeground`：扩展视图中远程徽章的前景色。
- `extensionIcon.starForeground`：扩展评分的图标颜色。
- `extensionIcon.verifiedForeground`：扩展认证发布者的图标颜色。
- `extensionIcon.preReleaseForeground`：预发布扩展的图标颜色。
- `extensionIcon.sponsorForeground`：扩展赞助的图标颜色。
- `extensionIcon.privateForeground`：私有扩展的图标颜色。
- `mcpIcon.starForeground`：MCP 星标的图标颜色。

---

<a id="quick-picker-colors"></a>
## 快速选择器颜色（Quick picker colors）

- `pickerGroup.border`：快速选择器（快速打开）中分组边框的颜色。
- `pickerGroup.foreground`：快速选择器（快速打开）中分组标签的颜色。
- `quickInput.background`：快速输入的背景色。快速输入小部件是颜色主题选择器等视图的容器。
- `quickInput.foreground`：快速输入的前景色。快速输入小部件是颜色主题选择器等视图的容器。
- `quickInputList.focusBackground`：快速选择器中拥有焦点的项的背景色。
- `quickInputList.focusForeground`：快速选择器中拥有焦点的项的前景色。
- `quickInputList.focusIconForeground`：快速选择器中拥有焦点的项的图标前景色。
- `quickInputTitle.background`：快速选择器标题的背景色。快速选择器小部件是命令面板等选择器的容器。

---

<a id="keybinding-label-colors"></a>
## 快捷键标签颜色（Keybinding label colors）

> 当一个命令关联了快捷键时，会显示快捷键标签。快捷键标签的一个例子可以在命令面板中看到：

![快捷键标签](images/theme-color/keybinding-label.png)

> 快捷键标签的使用场景包括（但不限于）：

> - 命令面板
> - 键盘快捷方式编辑器
> - 键盘快捷方式录制对话框
> - 扩展在市场页面上的“功能贡献”部分

> 可以使用以下自定义：

- `keybindingLabel.background`：快捷键标签的背景色。快捷键标签用于表示一个键盘快捷方式。
- `keybindingLabel.foreground`：快捷键标签的前景色。快捷键标签用于表示一个键盘快捷方式。
- `keybindingLabel.border`：快捷键标签的边框颜色。快捷键标签用于表示一个键盘快捷方式。
- `keybindingLabel.bottomBorder`：快捷键标签的底部边框颜色。快捷键标签用于表示一个键盘快捷方式。

---

<a id="keyboard-shortcut-table-colors"></a>
## 键盘快捷方式表格颜色（Keyboard shortcut table colors）

- `keybindingTable.headerBackground`：键盘快捷方式表格标题的背景色。
- `keybindingTable.rowsBackground`：键盘快捷方式表格交替行的背景色。

---

<a id="integrated-terminal-colors"></a>
## 集成终端颜色（Integrated Terminal colors）

- `terminal.background`：集成终端视口的背景色。
- `terminal.border`：终端内分隔拆分窗格的边框颜色。默认为 panel.border。
- `terminal.foreground`：集成终端的默认前景色。
- `terminal.ansiBlack`：终端中的“Black（黑）” ANSI 颜色。
- `terminal.ansiBlue`：终端中的“Blue（蓝）” ANSI 颜色。
- `terminal.ansiBrightBlack`：终端中的“BrightBlack（亮黑）” ANSI 颜色。
- `terminal.ansiBrightBlue`：终端中的“BrightBlue（亮蓝）” ANSI 颜色。
- `terminal.ansiBrightCyan`：终端中的“BrightCyan（亮青）” ANSI 颜色。
- `terminal.ansiBrightGreen`：终端中的“BrightGreen（亮绿）” ANSI 颜色。
- `terminal.ansiBrightMagenta`：终端中的“BrightMagenta（亮品红）” ANSI 颜色。
- `terminal.ansiBrightRed`：终端中的“BrightRed（亮红）” ANSI 颜色。
- `terminal.ansiBrightWhite`：终端中的“BrightWhite（亮白）” ANSI 颜色。
- `terminal.ansiBrightYellow`：终端中的“BrightYellow（亮黄）” ANSI 颜色。
- `terminal.ansiCyan`：终端中的“Cyan（青）” ANSI 颜色。
- `terminal.ansiGreen`：终端中的“Green（绿）” ANSI 颜色。
- `terminal.ansiMagenta`：终端中的“Magenta（品红）” ANSI 颜色。
- `terminal.ansiRed`：终端中的“Red（红）” ANSI 颜色。
- `terminal.ansiWhite`：终端中的“White（白）” ANSI 颜色。
- `terminal.ansiYellow`：终端中的“Yellow（黄）” ANSI 颜色。
- `terminal.selectionBackground`：终端选择的背景色。
- `terminal.selectionForeground`：终端选择的前景色。当它为 null 时，会保留选择内容原来的前景色，并应用最小对比度功能。
- `terminal.inactiveSelectionBackground`：终端没有焦点时选择的背景色。
- `terminal.findMatchBackground`：终端中当前搜索匹配项的颜色。这个颜色不能是不透明的，以免遮住下面的终端内容。
- `terminal.findMatchBorder`：终端中当前搜索匹配项的边框颜色。
- `terminal.findMatchHighlightBackground`：终端中其他搜索匹配项的颜色。这个颜色不能是不透明的，以免遮住下面的终端内容。
- `terminal.findMatchHighlightBorder`：终端中其他搜索匹配项的边框颜色。
- `terminal.hoverHighlightBackground`：悬停在终端中的链接上时高亮的颜色。
- `terminalCursor.background`：终端光标的背景色。可以自定义被块状光标覆盖的字符的颜色。
- `terminalCursor.foreground`：终端光标的前景色。
- `terminal.dropBackground`：在终端上方拖动时的背景色。这个颜色应该带有透明度，以便终端内容仍然可以透出来。
- `terminal.tab.activeBorder`：面板中终端标签页侧边的边框。默认为 `tab.activeBorder`。
- `terminalCommandDecoration.defaultBackground`：终端命令装饰的默认背景色。
- `terminalCommandDecoration.successBackground`：成功的命令的终端命令装饰背景色。
- `terminalCommandDecoration.errorBackground`：出错的命令的终端命令装饰背景色。
- `terminalOverviewRuler.cursorForeground`：概览标尺中光标的颜色。
- `terminalOverviewRuler.findMatchForeground`：终端概览标尺中查找匹配项的标记颜色。
- `terminalStickyScroll.background`：终端中粘性滚动叠加层的背景色。
- `terminalStickyScroll.border`：终端中粘性滚动叠加层的边框。
- `terminalStickyScrollHover.background`：悬停时终端中粘性滚动叠加层的背景色。
- `terminal.initialHintForeground`：终端初始提示的前景色。
- `terminalOverviewRuler.border`：概览标尺左侧边框的颜色。
- `terminalCommandGuide.foreground`：悬停时出现在命令及其输出左侧的终端命令参考线的前景色。

- `terminalSymbolIcon.aliasForeground`：别名图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.branchForeground`：分支图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.commitForeground`：提交图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.flagForeground`：标志（flag）图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.optionForeground`：选项图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.optionValueForeground`：选项值图标的前景色（原文写作“枚举成员图标”）。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.methodForeground`：方法图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.argumentForeground`：参数图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.inlineSuggestionForeground`：内联建议图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.fileForeground`：文件图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.folderForeground`：文件夹图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.pullRequestDoneForeground`：已完成的拉取请求图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.pullRequestForeground`：拉取请求图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.remoteForeground`：远程（remote）图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.stashForeground`：储藏（stash）图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.symbolText`：纯文本建议的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.symbolicLinkFileForeground`：符号链接文件图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.symbolicLinkFolderForeground`：符号链接文件夹图标的前景色。这些图标会出现在终端建议小部件中。
- `terminalSymbolIcon.tagForeground`：标签（tag）图标的前景色。这些图标会出现在终端建议小部件中。

（16 个 `terminal.ansiXxx` 颜色就是命令行程序输出彩色文字时使用的 ANSI 颜色：例如 `ls` 的目录颜色、`git diff` 的红绿色。8 个普通色加 8 个亮色。）

---

<a id="debug-colors"></a>
## 调试颜色（Debug colors）

- `debugToolBar.background`：调试工具栏的背景色。
- `debugToolBar.border`：调试工具栏的边框颜色。
- `editor.stackFrameHighlightBackground`：编辑器中顶部堆栈帧高亮的背景色。
- `editor.focusedStackFrameHighlightBackground`：编辑器中拥有焦点的堆栈帧高亮的背景色。
- `editor.inlineValuesForeground`：调试内联值文字的颜色。
- `editor.inlineValuesBackground`：调试内联值背景的颜色。
- `debugView.exceptionLabelForeground`：调试器在异常处中断时，“调用堆栈”视图中显示的标签的前景色。
- `debugView.exceptionLabelBackground`：调试器在异常处中断时，“调用堆栈”视图中显示的标签的背景色。
- `debugView.stateLabelForeground`：“调用堆栈”视图中显示当前会话或线程状态的标签的前景色。
- `debugView.stateLabelBackground`：“调用堆栈”视图中显示当前会话或线程状态的标签的背景色。
- `debugView.valueChangedHighlight`：在调试视图中（例如“变量”视图）用于高亮值变化的颜色。
- `debugTokenExpression.name`：调试视图中（例如“变量”或“监视”视图）显示的标记名称的前景色。
- `debugTokenExpression.value`：调试视图中显示的标记值的前景色。
- `debugTokenExpression.string`：调试视图中字符串的前景色。
- `debugTokenExpression.boolean`：调试视图中布尔值的前景色。
- `debugTokenExpression.number`：调试视图中数字的前景色。
- `debugTokenExpression.error`：调试视图中表达式错误的前景色。
- `debugTokenExpression.type`：调试视图中（即“变量”或“监视”视图）显示的标记类型的前景色。

---

<a id="testing-colors"></a>
## 测试颜色（Testing colors）

- `testing.runAction`：编辑器中“运行”图标的颜色。
- `testing.iconErrored`：测试资源管理器中“出错”图标的颜色。
- `testing.iconFailed`：测试资源管理器中“失败”图标的颜色。
- `testing.iconPassed`：测试资源管理器中“通过”图标的颜色。
- `testing.iconQueued`：测试资源管理器中“排队中”图标的颜色。
- `testing.iconUnset`：测试资源管理器中“未设置”图标的颜色。
- `testing.iconSkipped`：测试资源管理器中“已跳过”图标的颜色。
- `testing.iconErrored.retired`：测试资源管理器中“出错”图标的过期（retired）颜色。
- `testing.iconFailed.retired`：测试资源管理器中“失败”图标的过期颜色。
- `testing.iconPassed.retired`：测试资源管理器中“通过”图标的过期颜色。
- `testing.iconQueued.retired`：测试资源管理器中“排队中”图标的过期颜色。
- `testing.iconUnset.retired`：测试资源管理器中“未设置”图标的过期颜色。
- `testing.iconSkipped.retired`：测试资源管理器中“已跳过”图标的过期颜色。
- `testing.peekBorder`：速览视图的边框和箭头的颜色。
- `testing.peekHeaderBackground`：速览视图标题的背景色（原文描述与 peekBorder 相同）。
- `testing.message.error.lineBackground`：编辑器中内联显示的错误消息旁边的边距颜色。
- `testing.message.info.decorationForeground`：编辑器中内联显示的测试信息消息的文字颜色。
- `testing.message.info.lineBackground`：编辑器中内联显示的信息消息旁边的边距颜色。
- `testing.messagePeekBorder`：速览一条记录的消息时，速览视图的边框和箭头的颜色。
- `testing.messagePeekHeaderBackground`：速览一条记录的消息时，速览视图标题的背景色（原文描述与 messagePeekBorder 相同）。
- `testing.coveredBackground`：被覆盖的文字的背景色。
- `testing.coveredBorder`：被覆盖的文字的边框颜色。
- `testing.coveredGutterBackground`：代码被覆盖的区域的装订线颜色。
- `testing.uncoveredBranchBackground`：为未覆盖的分支显示的小部件的背景色。
- `testing.uncoveredBackground`：未被覆盖的文字的背景色。
- `testing.uncoveredBorder`：未被覆盖的文字的边框颜色。
- `testing.uncoveredGutterBackground`：代码未被覆盖的区域的装订线颜色。
- `testing.coverCountBadgeBackground`：表示执行次数的徽章的背景色
- `testing.coverCountBadgeForeground`：表示执行次数的徽章的前景色
- `testing.message.error.badgeBackground`：编辑器中内联显示的测试错误消息的背景色。
- `testing.message.error.badgeBorder`：编辑器中内联显示的测试错误消息的边框颜色。
- `testing.message.error.badgeForeground`：编辑器中内联显示的测试错误消息的文字颜色。

---

<a id="welcome-page-colors"></a>
## 欢迎页颜色（Welcome page colors）

- `welcomePage.background`：欢迎页的背景色。
- `welcomePage.progress.background`：欢迎页进度条的前景色（原文的 background / foreground 两条描述似乎写反了）。
- `welcomePage.progress.foreground`：欢迎页进度条的背景色（原文的 background / foreground 两条描述似乎写反了）。
- `welcomePage.tileBackground`：欢迎页上磁贴的背景色。
- `welcomePage.tileHoverBackground`：欢迎页上磁贴的悬停背景色。
- `welcomePage.tileBorder`：欢迎页上磁贴的边框颜色。

- `walkThrough.embeddedEditorBackground`：交互式演练场（Interactive Playground）中嵌入式编辑器的背景色。
- `walkthrough.stepTitle.foreground`：每个演练步骤标题的前景色。

---

<a id="git-colors"></a>
## Git 颜色（Git colors）

- `gitDecoration.addedResourceForeground`：新增的 Git 资源的颜色。用于文件标签和源代码管理视图。
- `gitDecoration.modifiedResourceForeground`：修改的 Git 资源的颜色。用于文件标签和源代码管理视图。
- `gitDecoration.deletedResourceForeground`：删除的 Git 资源的颜色。用于文件标签和源代码管理视图。
- `gitDecoration.renamedResourceForeground`：重命名或复制的 Git 资源的颜色。用于文件标签和源代码管理视图。
- `gitDecoration.stageModifiedResourceForeground`：已暂存的修改的 Git 装饰颜色。用于文件标签和源代码管理视图。
- `gitDecoration.stageDeletedResourceForeground`：已暂存的删除的 Git 装饰颜色。用于文件标签和源代码管理视图。
- `gitDecoration.untrackedResourceForeground`：未跟踪的 Git 资源的颜色。用于文件标签和源代码管理视图。
- `gitDecoration.ignoredResourceForeground`：被忽略的 Git 资源的颜色。用于文件标签和源代码管理视图。
- `gitDecoration.conflictingResourceForeground`：存在冲突的 Git 资源的颜色。用于文件标签和源代码管理视图。
- `gitDecoration.submoduleResourceForeground`：子模块资源的颜色。
- `git.blame.editorDecorationForeground`：blame 编辑器装饰的颜色。

---

<a id="source-control-graph-colors"></a>
## 源代码管理图颜色（Source Control Graph colors）

- `scmGraph.historyItemHoverLabelForeground`：历史记录项悬停标签的前景色。
- `scmGraph.foreground1`：源代码管理图的前景色（1）。
- `scmGraph.foreground2`：源代码管理图的前景色（2）。
- `scmGraph.foreground3`：源代码管理图的前景色（3）。
- `scmGraph.foreground4`：源代码管理图的前景色（4）。
- `scmGraph.foreground5`：源代码管理图的前景色（5）。
- `scmGraph.historyItemHoverAdditionsForeground`：历史记录项悬停提示中新增内容的前景色。
- `scmGraph.historyItemHoverDeletionsForeground`：历史记录项悬停提示中删除内容的前景色。
- `scmGraph.historyItemRefColor`：历史记录项引用的颜色。
- `scmGraph.historyItemRemoteRefColor`：历史记录项远程引用的颜色。
- `scmGraph.historyItemBaseRefColor`：历史记录项基础引用的颜色。
- `scmGraph.historyItemHoverDefaultLabelForeground`：历史记录项悬停提示中默认标签的前景色。
- `scmGraph.historyItemHoverDefaultLabelBackground`：历史记录项悬停提示中默认标签的背景色。

---

<a id="settings-editor-colors"></a>
## 设置编辑器颜色（Settings Editor colors）

> **注意**：这些颜色用于图形界面的设置编辑器，可以用 `Preferences: Open Settings (UI)` 命令打开它。

- `settings.headerForeground`：分区标题或活动标题的前景色。
- `settings.modifiedItemIndicator`：表示设置已被修改的那条竖线。
- `settings.dropdownBackground`：下拉框的背景色。
- `settings.dropdownForeground`：下拉框的前景色。
- `settings.dropdownBorder`：下拉框的边框颜色。
- `settings.dropdownListBorder`：下拉列表的边框颜色。
- `settings.checkboxBackground`：复选框的背景色。
- `settings.checkboxForeground`：复选框的前景色。
- `settings.checkboxBorder`：复选框的边框颜色。
- `settings.rowHoverBackground`：悬停时设置行的背景色。
- `settings.textInputBackground`：文本输入框的背景色。
- `settings.textInputForeground`：文本输入框的前景色。
- `settings.textInputBorder`：文本输入框的边框颜色。
- `settings.numberInputBackground`：数字输入框的背景色。
- `settings.numberInputForeground`：数字输入框的前景色。
- `settings.numberInputBorder`：数字输入框的边框颜色。
- `settings.focusedRowBackground`：拥有焦点的设置行的背景色。
- `settings.focusedRowBorder`：设置行拥有焦点时，行的上下边框颜色。
- `settings.headerBorder`：标题容器边框的颜色。
- `settings.sashBorder`：设置编辑器中拆分视图分隔条的边框颜色。
- `settings.settingsHeaderHoverForeground`：分区标题或悬停的标题的前景色。

---

<a id="breadcrumbs-colors"></a>
## 面包屑导航颜色（Breadcrumbs colors）

> 面包屑导航的主题颜色：

- `breadcrumb.foreground`：面包屑导航项的颜色。
- `breadcrumb.background`：面包屑导航项的背景色。
- `breadcrumb.focusForeground`：拥有焦点的面包屑导航项的颜色。
- `breadcrumb.activeSelectionForeground`：选中的面包屑导航项的颜色。
- `breadcrumbPicker.background`：面包屑导航项选择器的背景色。

---

<a id="snippets-colors"></a>
## 代码片段颜色（Snippets colors）

> 代码片段的主题颜色：

- `editor.snippetTabstopHighlightBackground`：代码片段制表位的高亮背景色。
- `editor.snippetTabstopHighlightBorder`：代码片段制表位的高亮边框颜色。
- `editor.snippetFinalTabstopHighlightBackground`：代码片段最终制表位的高亮背景色。
- `editor.snippetFinalTabstopHighlightBorder`：代码片段最终制表位的高亮边框颜色。

---

<a id="symbol-icons-colors"></a>
## 符号图标颜色（Symbol Icons colors）

> 出现在大纲视图、面包屑导航和建议小部件中的符号图标的主题颜色：

- `symbolIcon.arrayForeground`：数组符号的前景色。
- `symbolIcon.booleanForeground`：布尔值符号的前景色。
- `symbolIcon.classForeground`：类符号的前景色。
- `symbolIcon.colorForeground`：颜色符号的前景色。
- `symbolIcon.constantForeground`：常量符号的前景色。
- `symbolIcon.constructorForeground`：构造函数符号的前景色。
- `symbolIcon.enumeratorForeground`：枚举符号的前景色。
- `symbolIcon.enumeratorMemberForeground`：枚举成员符号的前景色。
- `symbolIcon.eventForeground`：事件符号的前景色。
- `symbolIcon.fieldForeground`：字段符号的前景色。
- `symbolIcon.fileForeground`：文件符号的前景色。
- `symbolIcon.folderForeground`：文件夹符号的前景色。
- `symbolIcon.functionForeground`：函数符号的前景色。
- `symbolIcon.interfaceForeground`：接口符号的前景色。
- `symbolIcon.keyForeground`：键符号的前景色。
- `symbolIcon.keywordForeground`：关键字符号的前景色。
- `symbolIcon.methodForeground`：方法符号的前景色。
- `symbolIcon.moduleForeground`：模块符号的前景色。
- `symbolIcon.namespaceForeground`：命名空间符号的前景色。
- `symbolIcon.nullForeground`：null 符号的前景色。
- `symbolIcon.numberForeground`：数字符号的前景色。
- `symbolIcon.objectForeground`：对象符号的前景色。
- `symbolIcon.operatorForeground`：运算符符号的前景色。
- `symbolIcon.packageForeground`：包符号的前景色。
- `symbolIcon.propertyForeground`：属性符号的前景色。
- `symbolIcon.referenceForeground`：引用符号的前景色。
- `symbolIcon.snippetForeground`：代码片段符号的前景色。
- `symbolIcon.stringForeground`：字符串符号的前景色。
- `symbolIcon.structForeground`：结构体符号的前景色。
- `symbolIcon.textForeground`：文本符号的前景色。
- `symbolIcon.typeParameterForeground`：类型参数符号的前景色。
- `symbolIcon.unitForeground`：单位符号的前景色。
- `symbolIcon.variableForeground`：变量符号的前景色。

---

<a id="debug-icons-colors"></a>
## 调试图标颜色（Debug Icons colors）

- `debugIcon.breakpointForeground`：断点的图标颜色。
- `debugIcon.breakpointDisabledForeground`：已禁用断点的图标颜色。
- `debugIcon.breakpointUnverifiedForeground`：未验证断点的图标颜色。
- `debugIcon.breakpointCurrentStackframeForeground`：当前断点堆栈帧的图标颜色。
- `debugIcon.breakpointStackframeForeground`：所有断点堆栈帧的图标颜色。
- `debugIcon.startForeground`：调试工具栏中“开始调试”图标的颜色。
- `debugIcon.pauseForeground`：调试工具栏中“暂停”图标的颜色。
- `debugIcon.stopForeground`：调试工具栏中“停止”图标的颜色。
- `debugIcon.disconnectForeground`：调试工具栏中“断开连接”图标的颜色。
- `debugIcon.restartForeground`：调试工具栏中“重启”图标的颜色。
- `debugIcon.stepOverForeground`：调试工具栏中“单步跳过”图标的颜色。
- `debugIcon.stepIntoForeground`：调试工具栏中“单步进入”图标的颜色。
- `debugIcon.stepOutForeground`：调试工具栏中“单步跳出”图标的颜色。（原文误写为 step over）
- `debugIcon.continueForeground`：调试工具栏中“继续”图标的颜色。
- `debugIcon.stepBackForeground`：调试工具栏中“单步后退”图标的颜色。

- `debugConsole.infoForeground`：调试 REPL 控制台中信息消息的前景色。
- `debugConsole.warningForeground`：调试 REPL 控制台中警告消息的前景色。
- `debugConsole.errorForeground`：调试 REPL 控制台中错误消息的前景色。
- `debugConsole.sourceForeground`：调试 REPL 控制台中源文件名的前景色。
- `debugConsoleInputIcon.foreground`：调试控制台输入标记图标的前景色。

---

<a id="notebook-colors"></a>
## 笔记本颜色（Notebook colors）

- `notebook.editorBackground`：笔记本的背景色。
- `notebook.cellBorderColor`：笔记本单元格的边框颜色。
- `notebook.cellHoverBackground`：悬停时单元格的背景色。
- `notebook.cellInsertionIndicator`：笔记本单元格插入指示器的颜色。
- `notebook.cellStatusBarItemHoverBackground`：笔记本单元格状态栏项的（悬停）背景色。
- `notebook.cellToolbarSeparator`：单元格底部工具栏中分隔线的颜色
- `notebook.cellEditorBackground`：笔记本单元格编辑器的背景色
- `notebook.focusedCellBackground`：单元格拥有焦点时的背景色。
- `notebook.focusedCellBorder`：单元格拥有焦点时，单元格焦点指示器边框的颜色。
- `notebook.focusedEditorBorder`：笔记本单元格编辑器的边框颜色。
- `notebook.inactiveFocusedCellBorder`：单元格拥有焦点、但主焦点在编辑器之外时，单元格上下边框的颜色。
- `notebook.inactiveSelectedCellBorder`：选中了多个单元格时，单元格边框的颜色。
- `notebook.outputContainerBackgroundColor`：笔记本输出容器的背景色。
- `notebook.outputContainerBorderColor`：笔记本输出容器的边框颜色。
- `notebook.selectedCellBackground`：单元格被选中时的背景色。
- `notebook.selectedCellBorder`：单元格被选中但没有焦点时，单元格上下边框的颜色。
- `notebook.symbolHighlightBackground`：高亮的单元格的背景色
- `notebookScrollbarSlider.activeBackground`：点击时笔记本滚动条滑块的背景色。
- `notebookScrollbarSlider.background`：笔记本滚动条滑块的背景色。
- `notebookScrollbarSlider.hoverBackground`：悬停时笔记本滚动条滑块的背景色。
- `notebookStatusErrorIcon.foreground`：单元格状态栏中笔记本单元格的错误图标颜色。
- `notebookStatusRunningIcon.foreground`：单元格状态栏中笔记本单元格的运行中图标颜色。
- `notebookStatusSuccessIcon.foreground`：单元格状态栏中笔记本单元格的成功图标颜色。
- `notebookEditorOverviewRuler.runningCellForeground`：笔记本编辑器概览标尺中运行中单元格装饰的颜色。

---

<a id="chart-colors"></a>
## 图表颜色（Chart colors）

- `charts.foreground`：图表中文字的对比色。
- `charts.lines`：图表中线条的颜色。
- `charts.red`：图表中红色元素的颜色。
- `charts.blue`：图表中蓝色元素的颜色。
- `charts.yellow`：图表中黄色元素的颜色。
- `charts.orange`：图表中橙色元素的颜色。
- `charts.green`：图表中绿色元素的颜色。
- `charts.purple`：图表中紫色元素的颜色。
- `chart.line`：图表的线条颜色。
- `chart.axis`：图表的坐标轴颜色。
- `chart.guide`：图表的参考线。

---

<a id="ports-colors"></a>
## 端口颜色（Ports colors）

- `ports.iconRunningProcessForeground`：关联了运行中进程的端口的图标颜色。

---

<a id="comments-view-colors"></a>
## 注释视图颜色（Comments View colors）

- `commentsView.resolvedIcon`：已解决的注释的图标颜色。
- `commentsView.unresolvedIcon`：未解决的注释的图标颜色。

---

<a id="action-bar-colors"></a>
## 操作栏颜色（Action Bar colors）

- `actionBar.toggledBackground`：操作栏中处于切换（按下）状态的操作项的背景色。

---

<a id="simple-find-widget-colors"></a>
## 简单查找小部件颜色（Simple Find Widget colors）

- `simpleFindWidget.sashBorder`：（简单查找小部件的）分隔条边框颜色。

---

<a id="gauge-colors"></a>
## 仪表颜色（Gauge colors）

- `gauge.background`：仪表（gauge）的背景色。
- `gauge.foreground`：仪表的前景色。
- `gauge.border`：仪表的边框颜色。
- `gauge.warningBackground`：仪表的警告背景色。
- `gauge.warningForeground`：仪表的警告前景色。
- `gauge.errorBackground`：仪表的错误背景色。
- `gauge.errorForeground`：仪表的错误前景色。

---

<a id="markdown"></a>
## Markdown

- `markdownAlert.note.foreground`：Markdown 中 note（注意）提示块的前景色。
- `markdownAlert.tip.foreground`：Markdown 中 tip（提示）提示块的前景色。
- `markdownAlert.important.foreground`：Markdown 中 important（重要）提示块的前景色。
- `markdownAlert.warning.foreground`：Markdown 中 warning（警告）提示块的前景色。
- `markdownAlert.caution.foreground`：Markdown 中 caution（小心）提示块的前景色。

---

<a id="agent-session-colors"></a>
## 智能体会话颜色（Agent Session）（Agent Session colors）

- `agentSessionReadIndicator.foreground`：智能体会话中已读指示器的前景色。
- `agentSessionSelectedBadge.border`：选中的智能体会话项中徽章的边框颜色。
- `agentSessionSelectedUnfocusedBadge.border`：视图没有焦点时，选中的智能体会话项中徽章的边框颜色。
- `agentStatusIndicator.background`：标题栏中智能体状态指示器的背景色。
- `aiCustomizationManagement.sashBorder`：聊天自定义管理编辑器中拆分视图分隔条的边框颜色。

---

<a id="extension-colors"></a>
## 扩展贡献的颜色（Extension colors）

> 颜色 ID 也可以由扩展通过[颜色贡献点](./contribution-points.md#contributes.colors)贡献。在 `workbench.colorCustomizations` 设置和颜色主题定义文件中使用代码补全时，这些颜色也会出现。用户可以在[扩展贡献](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace#extension-details)选项卡中查看一个扩展定义了哪些颜色。

**扩展开发者的要点：** 扩展需要的颜色，优先**复用**上面列出的颜色 ID（例如错误用 `errorForeground`、警告用 `editorWarning.foreground`、链接用 `textLink.foreground`），这样自动适配所有主题；确实需要新颜色时，再通过 [`contributes.colors`](./contribution-points.md#contributes.colors) 贡献，并让它的默认值引用一个现有的颜色。

---

## 本篇小结

```text
颜色 ID 的三种使用者
  主题作者：主题 JSON 的 "colors": { "<颜色 ID>": "#RRGGBBAA" }
  用户：settings.json 的 "workbench.colorCustomizations"（可用 "[主题名]" 按主题设置）
  扩展：new vscode.ThemeColor('<颜色 ID>')；webview 中 var(--vscode-<颜色 ID，点换成连字符>)

颜色格式：#RGB / #RGBA / #RRGGBB / #RRGGBBAA（无 alpha 默认不透明）
  “不能是不透明的”颜色（选择、查找、高亮背景等）必须带透明度

命名规律：区域.状态+部位+属性（background / foreground / border / hoverBackground / activeXxx / inactiveXxx）
扩展自己的颜色：contributes.colors（默认值尽量引用已有颜色 ID）
```
