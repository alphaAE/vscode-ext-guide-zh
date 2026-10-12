# 颜色主题（Color Theme）

> 原文：[Color Theme](https://code.visualstudio.com/api/extension-guides/color-theme)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/color-theme.md`（DateApproved: 10/7/2026）

> VS Code 用户界面中可见的颜色分为两类：
>
> - 视图和编辑器中使用的**工作台颜色**，从活动栏到状态栏都属于这一类。所有这些颜色的完整列表见[主题颜色参考](../references/theme-color.md)。
> - 编辑器中源代码使用的**语法颜色和样式**。这类颜色的主题化方式有所不同，因为语法着色是基于 TextMate 语法和 TextMate 主题，以及语义标记（semantic token）的。
>
> 本指南会介绍创建主题的几种不同方式。

这两类颜色就是 [主题](../extension-capabilities/theming.md) 一篇中介绍的 `colors` 和 `tokenColors` / `semanticTokenColors`。建议先读那一篇，了解颜色主题“映射表”的原理。

**本篇的思路：** 不要从零开始写主题文件，而是先在自己的设置里**调颜色、实时看效果**，满意之后再一键导出成主题文件，最后打包成扩展。

```text
1. 切换到一个接近你想要效果的现有主题
2. 在 settings.json 中用 colorCustomizations 调整颜色（实时生效）
3. 执行命令，把当前效果导出为主题文件
4. 用 yo code 生成主题扩展，放入主题文件
5. 按 F5 测试，然后发布
```

---

<a id="workbench-colors"></a>
## 工作台颜色（Workbench colors）

> 创建新的工作台颜色主题，最简单的方式是从一个现有的颜色主题开始，再进行定制。首先切换到你想修改的颜色主题，然后打开[设置](https://code.visualstudio.com/docs/configure/settings)，修改 `workbench.colorCustomizations` 设置。修改会实时应用到你的 VS Code 中。
>
> 例如，下面的设置会修改标题栏的背景色：

```json
{
  "workbench.colorCustomizations": {
    "titleBar.activeBackground": "#ff0000"
  }
}
```

> 所有可主题化的颜色的完整列表，见[颜色参考](../references/theme-color.md)。

这段配置写在用户的 `settings.json` 中（命令面板执行 **Preferences: Open User Settings (JSON)** 打开）。输入 `"workbench.colorCustomizations": {` 后，在大括号里输入颜色 ID 的开头，会有自动补全提示所有可用的颜色 ID，并且颜色值前面会显示一个色块，点击可以打开取色器。

**颜色值的格式：** `#RGB`、`#RGBA`、`#RRGGBB`、`#RRGGBBAA`。最后的 `AA` 是透明度，例如 `#ff000080` 是半透明的红色。

**只对某个主题生效：** 用方括号包住主题名称，这条定制只在使用该主题时生效：

```json
"workbench.colorCustomizations": {
  "[Default Dark Modern]": {
    "titleBar.activeBackground": "#ff0000"
  }
}
```

---

<a id="syntax-colors"></a>
## 语法颜色（Syntax colors）

> 对于语法高亮的颜色，有两种做法。你可以引用社区中已有的 TextMate 主题（`.tmTheme` 文件），也可以创建自己的主题规则。最简单的方式是从一个现有主题开始进行定制，和上面的工作台颜色一节非常相似。
>
> 首先切换到要定制的颜色主题，然后使用 `editor.tokenColorCustomizations` [设置](https://code.visualstudio.com/docs/configure/settings)。修改会实时应用到你的 VS Code 中，不需要刷新或重新加载。
>
> 例如，下面的设置会修改编辑器中注释的颜色：

```json
{
  "editor.tokenColorCustomizations": {
    "comments": "#FF0000"
  }
}
```

> 这个设置支持一个简单的模型，提供了一组常见的标记类型，如 'comments'（注释）、'strings'（字符串）和 'numbers'（数字）。如果想给更多内容着色，就需要直接使用 TextMate 主题规则，[语法高亮指南](../language-extensions/syntax-highlight-guide.md)中有详细的说明。

`editor.tokenColorCustomizations` 支持的简单类型有：`comments`、`strings`、`keywords`、`numbers`、`types`、`functions`、`variables`。要更精细地控制（比如“只改函数参数的颜色”），就要用 `textMateRules` 按作用域（scope）写规则：

```json
"editor.tokenColorCustomizations": {
  "textMateRules": [
    {
      "scope": "variable.parameter",
      "settings": { "foreground": "#FFA500", "fontStyle": "italic" }
    }
  ]
}
```

`fontStyle` 可以是 `italic`、`bold`、`underline`、`strikethrough` 的组合（用空格分隔），空字符串表示取消样式。

**怎么知道某段代码的作用域？** 在命令面板中执行 **Developer: Inspect Editor Tokens and Scopes**，然后把光标放在代码上，就会显示这个位置的作用域列表和当前使用的颜色。作用域的原理见 [主题](../extension-capabilities/theming.md) 一篇和 [语法高亮指南](../language-extensions/syntax-highlight-guide.md)。

---

<a id="semantic-colors"></a>
## 语义颜色（Semantic colors）

> 在 VS Code 1.43 版本中，TypeScript 和 JavaScript 已经支持语义高亮。我们预计其他语言很快也会采用它。

（这句话是 1.43 时写的。现在很多语言的扩展都已经支持语义高亮，比如 C#、C++、Java、Python 等。）

> 语义高亮基于语言服务提供的符号信息来丰富语法着色，语言服务对项目有更完整的理解。语言服务器运行起来、计算出语义标记之后，着色的变化才会出现。
>
> 每个主题通过主题定义中的一个特定设置，控制是否启用语义高亮。每个语义标记的样式由主题的样式规则定义。
>
> 用户可以使用 `editor.tokenColorCustomizations` 设置覆盖语义高亮功能和着色规则：
>
> 为特定主题启用语义高亮：

```json
"editor.tokenColorCustomizations": {
    "[Material Theme]": {
        "semanticHighlighting": true
    }
},
```

> 主题可以为语义标记定义主题规则，详见[语法高亮指南](../language-extensions/semantic-highlight-guide.md#theming)。

（原文链接指向语法高亮指南中的 `#semantic-theming`，但那里并没有这一节，语义标记的主题化在 [语义高亮指南](../language-extensions/semantic-highlight-guide.md#theming) 中，这里已改为指向那里。）

语法高亮和语义高亮的区别，在 [主题](../extension-capabilities/theming.md) 一篇中有对比表。简单地说：打开文件时，代码先按语法规则（TextMate）着色；等语言服务分析完代码，再按语义信息修正一遍。所以有时会看到打开文件一两秒后，部分代码的颜色“变了一下”，那就是语义高亮生效了。

用户自己调整语义标记的颜色，用的是 `editor.semanticTokenColorCustomizations` 设置：

```json
"editor.semanticTokenColorCustomizations": {
  "enabled": true,
  "rules": {
    "variable.readonly": "#4EC9B0"   // 只读变量（如 const）显示为青绿色
  }
}
```

---

<a id="create-a-new-color-theme"></a>
## 创建新的颜色主题（Create a new Color Theme）

> 用 `workbench.colorCustomizations` 和 `editor.tokenColorCustomizations` 调好主题颜色之后，就可以创建真正的主题了。
>
> 1. 在**命令面板**中执行 **Developer: Generate Color Theme from Current Settings** 命令，生成一个主题文件。
> 2. 使用 VS Code 的 [Yeoman](https://yeoman.io) 扩展生成器，生成一个新的主题扩展：
>
>    ```bash
>    npm install -g yo generator-code
>    yo code
>    ```
>
> 3. 如果你是按上面的方法定制的主题，选择 'Start fresh'。
>
>    ![yo code 生成颜色主题扩展](./images/color-theme/yocode-colortheme.png)
>
> 4. 把根据设置生成的主题文件复制到新扩展中。

截图中，`yo code` 的第一个问题选择了 **New Color Theme**（新建颜色主题），第二个问题“是否导入或转换已有的 TextMate 颜色主题”有三个选项：

| 选项 | 含义 |
|---|---|
| Import an existing theme but keep it as tmTheme file | 导入已有主题，保留为 `.tmTheme` 文件 |
| Import an existing theme and inline it in the Visual Studio Code color theme file | 导入已有主题，并转换写入 VS Code 的颜色主题文件 |
| Start fresh | 从头开始（使用第 1 步导出的文件时选这个） |

`yo code` 的用法见 [你的第一个扩展](../get-started/your-first-extension.md)。

生成的扩展中，主题是通过 `package.json` 的 `contributes.themes` 贡献点注册的（这部分原文没有展示，补充如下）：

```jsonc
"contributes": {
  "themes": [
    {
      "label": "My Theme",                          // 在主题选择列表中显示的名称
      "uiTheme": "vs-dark",                         // 基础主题类型
      "path": "./themes/my-theme-color-theme.json"  // 主题文件的路径
    }
  ]
}
```

`uiTheme` 决定主题的基础类型，没有在主题文件中定义的颜色会使用这个基础类型的默认值：

| `uiTheme` | 类型 |
|---|---|
| `vs` | 浅色 |
| `vs-dark` | 深色 |
| `hc-black` | 深色高对比度 |
| `hc-light` | 浅色高对比度 |

一个扩展可以在 `themes` 数组中包含多个主题，比如同时提供深色版和浅色版。

> 你也可以使用已有的 TextMate 主题：让扩展生成器导入一个 TextMate 主题文件（.tmTheme），并把它打包好供 VS Code 使用。或者，如果你已经下载了主题，就把 `tokenColors` 部分替换为指向要使用的 `.tmTheme` 文件的链接。

```json
{
  "type": "dark",
  "colors": {
    "editor.background": "#1e1e1e",
    "editor.foreground": "#d4d4d4",
    "editorIndentGuide.background": "#404040",
    "editorRuler.foreground": "#333333",
    "activityBarBadge.background": "#007acc",
    "sideBarTitle.foreground": "#bbbbbb"
  },
  "tokenColors": "./Diner.tmTheme"
}
```

`tokenColors` 既可以是一个规则数组（见 [主题](../extension-capabilities/theming.md) 中的示例），也可以像这里一样是一个字符串，指向一个 `.tmTheme` 文件（路径相对于主题文件）。

> **提示：** 把颜色定义文件命名为以 `-color-theme.json` 结尾，编辑时就能获得悬停提示、代码补全、颜色装饰和取色器。

例如命名为 `my-theme-color-theme.json`。VS Code 会根据这个后缀识别出这是颜色主题文件，并应用对应的 JSON 结构定义（schema），这样编辑时就有补全和校验。

> **提示：** [ColorSublime](https://colorsublime.github.io) 上有数百个现成的 TextMate 主题可供选择。挑一个你喜欢的主题，复制它的下载链接，在 Yeoman 生成器中使用，或者放进你的扩展中。链接的格式类似于 `"https://raw.githubusercontent.com/Colorsublime/Colorsublime-Themes/master/themes/(name).tmTheme"`。

---

<a id="test-a-new-color-theme"></a>
## 测试新的颜色主题（Test a new Color Theme）

> 要试用新主题，按 F5 启动一个扩展开发宿主窗口。
>
> 在那里，通过 **文件** > **首选项** > **主题** > **颜色主题** 打开颜色主题选择器，就能在下拉列表中看到你的主题。用上下方向键可以实时预览主题效果。

![在颜色主题选择器中选择 My Theme](images/color-theme/mytheme.png)

截图中，颜色主题选择列表里出现了新增的 “My Theme”。快捷键是 `Ctrl+K Ctrl+T`。

> 在“扩展开发宿主”窗口中，对主题文件的修改会实时生效。

也就是说，测试主题时不需要 **Developer: Reload Window**：在原窗口修改主题文件并保存，扩展开发宿主窗口中的颜色就会立即变化。

---

<a id="publishing-a-theme-to-the-extension-marketplace"></a>
## 把主题发布到扩展市场（Publishing a Theme to the Extension Marketplace）

> 如果你想与社区分享你的新主题，可以把它发布到[扩展市场](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace)。使用 [vsce 发布工具](../working-with-extensions/publishing-extension.md)打包你的主题，并把它发布到 VS Code 扩展市场。
>
> **提示：** 为了让用户更容易找到你的主题，请在扩展的描述中包含 “theme” 这个词，并在 `package.json` 中把 `Category`（分类）设为 `Themes`。

```json
"categories": ["Themes"]
```

> 我们还提供了一些建议，帮助你的扩展在 VS Code 扩展市场中看起来更出色，请参阅[扩展市场展示技巧](../references/extension-manifest.md#marketplace-presentation-tips)。

---

<a id="adding-a-new-color-id"></a>
## 添加新的颜色 ID（Adding a new Color ID）

> 扩展也可以通过[颜色贡献点](../references/contribution-points.md#contributes.colors)贡献颜色 ID。在 `workbench.colorCustomizations` 设置和颜色主题定义文件中使用代码补全时，也会出现这些颜色。用户可以在[扩展贡献](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace#extension-details)标签页中查看某个扩展定义了哪些颜色。

**这和前面的内容有什么不同？** 前面讲的是**制作主题**，给 VS Code 已有的颜色 ID 赋值。这一节讲的是**普通扩展**（不是主题扩展）定义自己的颜色 ID。

比如你的扩展会给代码中的 TODO 加上背景色。如果把颜色写死在代码里，换了主题后可能很难看。更好的做法是定义一个颜色 ID，给浅色、深色、高对比度主题分别设置默认值，主题作者和用户还可以覆盖它：

```jsonc
"contributes": {
  "colors": [
    {
      "id": "myExtension.todoBackground",
      "description": "TODO 注释的背景色",
      "defaults": {
        "light": "#FFFF0040",
        "dark": "#FFFF0020",
        "highContrast": "#FFFF00"
      }
    }
  ]
}
```

在代码中通过 `new vscode.ThemeColor('myExtension.todoBackground')` 引用这个颜色（例如用于编辑器装饰），在 Webview 中则可以通过 CSS 变量 `var(--vscode-myExtension-todoBackground)` 使用（见 [Webview 指南](./webview.md#theming-webview-content)）。

---

<a id="further-reading"></a>
## 扩展阅读（Further reading）

> - [CSS Tricks - Creating a VS Code theme](https://css-tricks.com/creating-a-vs-code-theme/)

---

## 本篇小结

| 步骤 | 做法 |
|---|---|
| 调工作台颜色 | `settings.json` 中的 `workbench.colorCustomizations` |
| 调语法颜色 | `editor.tokenColorCustomizations`（简单类型或 `textMateRules`） |
| 调语义颜色 | `editor.semanticTokenColorCustomizations`；主题中用 `semanticHighlighting` 开关 |
| 查作用域 | **Developer: Inspect Editor Tokens and Scopes** |
| 导出主题文件 | **Developer: Generate Color Theme from Current Settings** |
| 生成扩展 | `yo code` → New Color Theme → Start fresh |
| 注册主题 | `contributes.themes`（`label`、`uiTheme`、`path`） |
| 测试 | `F5`，`Ctrl+K Ctrl+T` 切换主题，修改实时生效 |
| 发布 | `vsce`，分类设为 `Themes` |
| 普通扩展定义颜色 | `contributes.colors` + `ThemeColor` |
