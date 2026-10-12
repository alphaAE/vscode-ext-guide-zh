# 主题（Theming）

> 原文：[Theming](https://code.visualstudio.com/api/extension-capabilities/theming)
> 源文件：`microsoft/vscode-docs` → `api/extension-capabilities/theming.md`（DateApproved: 10/7/2026）

> 在 VS Code 中，主题分为三种：
>
> - **颜色主题（Color Theme）**：把界面部件标识符和文本标记（token）标识符映射到颜色。颜色主题让你可以把喜欢的颜色应用到 VS Code 的界面部件和编辑器中的文本上。
> - **文件图标主题（File Icon Theme）**：把文件类型或文件名映射到图片。文件图标会显示在 VS Code 界面的各个位置，比如文件资源管理器、快速打开列表和编辑器标签页。
> - **产品图标主题（Product Icon Theme）**：整个界面中使用的一套图标，涵盖侧边栏、活动栏、状态栏，一直到编辑器的字形边距（glyph margin）。

三种主题的区别：

| 主题类型 | 改变什么 | 例子 | 切换方式（命令面板中搜索） |
|---|---|---|---|
| 颜色主题 | 界面颜色 + 代码高亮颜色 | Dark+、One Dark Pro | `Preferences: Color Theme` |
| 文件图标主题 | 文件、文件夹前面的图标 | Seti、Material Icon Theme | `Preferences: File Icon Theme` |
| 产品图标主题 | VS Code 自身界面的图标（活动栏图标、按钮图标等） | Fluent Icons | `Preferences: Product Icon Theme` |

**“映射”是理解主题的关键。** 三种主题本质上都是一张“对照表”：

- 颜色主题：`某个界面部件 / 某类代码文本` → `某种颜色`
- 文件图标主题：`某种文件` → `某个图标`
- 产品图标主题：`某个界面图标` → `另一个图标`

所以做主题基本不用写代码，主要是编写这些 JSON 对照表。

**字形边距（glyph margin）**是编辑器行号左边的一窄条区域，断点的红点就显示在这里。

---

<a id="color-theme"></a>
## 颜色主题（Color Theme）

![颜色主题的工作原理：编辑器背景色来自 colors，代码文字颜色来自 tokenColors](images/theming/color-theme.png)

这张图展示了颜色主题的两部分配置是怎么起作用的（截图是英文界面）：

- **右上角的红框**：主题文件中 `colors` 下的 `"editor.background": "#1E1E1E"`，决定了编辑器的背景色。
- **中间的白色区域**：VS Code 把代码 `function f1() {` 拆分成一个个标记（token），并给每个标记打上作用域名称。其中 `f1` 被识别为 `entity.name.function.js`。
- **右侧中间的红框**：`tokenColors` 中有一条规则，把作用域 `entity.name.function` 的颜色设为 `#DCDCAA`。
- **底部的说明**：所以 `f1` 最终显示为 `#DCDCAA`（淡黄色）。

> 从图中可以看到，颜色主题既定义了界面部件的颜色，也定义了编辑器中的高亮颜色：
>
> - `colors` 映射控制界面部件的颜色。
> - `tokenColors` 定义编辑器中高亮的颜色和样式。[语法高亮指南](https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide)中有更多这方面的内容。
> - `semanticTokenColors` 映射以及 `semanticHighlighting` 设置可以增强编辑器中的高亮效果。[语义高亮指南](https://code.visualstudio.com/api/language-extensions/semantic-highlight-guide)介绍了相关的 API。

三个字段的分工：

| 字段 | 控制什么 | 例子 |
|---|---|---|
| `colors` | **界面**的颜色 | 编辑器背景、侧边栏背景、状态栏颜色 |
| `tokenColors` | **代码文字**的颜色（基于语法高亮） | 关键字、字符串、函数名的颜色 |
| `semanticTokenColors` | **代码文字**的颜色（基于语义高亮） | 区分“局部变量”和“参数”、“只读变量” |

一个最小的颜色主题文件大致是这样的：

```jsonc
{
  "name": "My Theme",
  "type": "dark",                        // 主题是深色还是浅色
  "colors": {
    "editor.background": "#1E1E1E",       // 编辑器背景色
    "statusBar.background": "#007ACC"     // 状态栏背景色
  },
  "tokenColors": [
    {
      "name": "Function declarations",
      "scope": ["entity.name.function"],  // 作用域：函数名
      "settings": {
        "foreground": "#DCDCAA"           // 文字颜色
      }
    }
  ],
  "semanticHighlighting": true            // 是否启用语义高亮
}
```

**语法高亮和语义高亮有什么区别？**

| | 语法高亮 | 语义高亮 |
|---|---|---|
| 依据 | 语法规则（正则表达式匹配文本） | 语言服务对代码的理解 |
| 速度 | 快，打开文件立即生效 | 稍慢，要等语言服务分析完成 |
| 能力 | 只看文本形式，例如“`f1` 后面跟着括号，所以是函数” | 知道含义，例如“这个变量是常量”“这个名字是一个类” |
| 对应字段 | `tokenColors` | `semanticTokenColors` |

两者是叠加关系：先用语法高亮快速着色，语义分析完成后，再用语义高亮修正和细化。

`colors` 中有几百个可以设置的界面颜色 ID，完整列表见 [主题颜色参考](https://code.visualstudio.com/api/references/theme-color)。

> 我们有一篇 [颜色主题指南](https://code.visualstudio.com/api/extension-guides/color-theme) 和一个 [颜色主题示例](https://github.com/microsoft/vscode-extension-samples/tree/main/theme-sample)，演示如何创建主题。

**小技巧：** 不知道某个界面区域或某段代码对应哪个颜色 ID、哪个作用域时，可以在命令面板中执行 **Developer: Inspect Editor Tokens and Scopes**，然后点击代码，会显示这个位置的标记类型、作用域和当前使用的颜色。

---

<a id="file-icon-theme"></a>
## 文件图标主题（File Icon Theme）

> 文件图标主题让你可以：
>
> - 建立从唯一的文件图标标识符到图片或字体图标的映射。
> - 通过文件名或文件的语言类型，把文件关联到这些图标标识符。
>
> [文件图标主题指南](https://code.visualstudio.com/api/extension-guides/file-icon-theme)介绍了如何创建文件图标主题。

![文件图标主题的工作原理：通过 iconDefinitions 定义图标，再通过 fileNames 和 languageIds 把文件关联到图标](images/theming/file-icon-theme.png)

图中展示了两个例子（截图是英文界面）：

- **顶部说明**：`README.md` 使用 `_info` 图标；`_info` 图标使用 `seti.woff` 字体中的 `\E044` 字符，颜色为 `#519aba`。所以 `README.md` 前面显示的是这个蓝色图标。
- **底部说明**：TypeScript 文件使用 `_typescript` 图标；`_typescript` 图标使用 `seti.woff` 字体中的 `\E083` 字符，颜色同样是 `#519aba`。所以 `extension.ts` 前面显示的是这个图标。
- **左侧的红框**：标出了这些图标出现的位置——资源管理器、编辑器标签页、面包屑导航。

也就是说，文件图标主题是**两步映射**：

```text
第 1 步：定义图标（iconDefinitions）
  _info        → 字体 seti.woff 中的字符 \E044，颜色 #519aba
  _typescript  → 字体 seti.woff 中的字符 \E083，颜色 #519aba

第 2 步：把文件关联到图标
  fileNames:   "readme.md"  → _info          （按文件名匹配）
  languageIds: "typescript" → _typescript    （按语言类型匹配）
```

对应的主题文件：

```jsonc
{
  "fonts": [
    {
      "id": "seti",
      "src": [{ "path": "./seti.woff", "format": "woff" }],
      "weight": "normal",
      "style": "normal",
      "size": "150%"
    }
  ],
  "iconDefinitions": {
    "_info": { "fontCharacter": "\\E044", "fontColor": "#519aba" },
    "_typescript": { "fontCharacter": "\\E083", "fontColor": "#519aba" }
  },
  "fileNames": {
    "readme.md": "_info"
  },
  "languageIds": {
    "typescript": "_typescript"
  }
}
```

图标既可以用字体中的字符（如上例，体积小、可以自由着色），也可以直接用 SVG、PNG 等图片文件。

**为什么要分两步？** 同一个图标往往要给很多种文件使用。先定义一次，再让多个文件名、扩展名、语言去引用它，就不用重复定义图标。

---

<a id="product-icon-theme"></a>
## 产品图标主题（Product Icon Theme）

> 产品图标主题让你可以：
>
> 重新定义工作台中使用的所有内置图标。例如筛选操作按钮中的图标和视图图标、状态栏中的图标、断点图标，以及树和编辑器中的折叠图标。
>
> [产品图标主题指南](https://code.visualstudio.com/api/extension-guides/product-icon-theme)介绍了如何创建产品图标主题。

**和文件图标主题的区别：**

- **文件图标主题**改的是**文件**前面的图标（`.ts`、`.json` 等文件各显示什么图标）；
- **产品图标主题**改的是 **VS Code 自身界面**的图标，例如活动栏上资源管理器、搜索的图标，状态栏中的图标，断点的红点，折叠代码时的小箭头。

VS Code 的内置图标叫 **codicon**。在 [扩展工作台](./extending-workbench.md) 一篇中，状态栏项使用的 `$(rocket)` 就是一个 codicon。产品图标主题的作用，就是把这些 codicon 换成另一套图标。

---

## 本篇小结

| 主题 | 本质 | 关键字段 |
|---|---|---|
| 颜色主题 | 界面部件 / 代码标记 → 颜色 | `colors`（界面）、`tokenColors`（语法高亮）、`semanticTokenColors`（语义高亮） |
| 文件图标主题 | 文件 → 图标（两步映射） | `iconDefinitions` 定义图标，`fileNames` / `fileExtensions` / `languageIds` 关联文件 |
| 产品图标主题 | 内置界面图标（codicon） → 新图标 | 详见产品图标主题指南 |

三种主题都主要靠编写 JSON 配置完成，基本不需要写扩展代码。详细的制作方法见扩展指南中对应的三篇。
