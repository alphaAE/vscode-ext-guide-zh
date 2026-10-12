# 扩展能力概览（Extension Capabilities Overview）

> 原文：[Extension Capabilities Overview](https://code.visualstudio.com/api/extension-capabilities/overview)
> 源文件：`microsoft/vscode-docs` → `api/extension-capabilities/overview.md`（DateApproved: 10/7/2026）

> VS Code 为扩展提供了很多扩展自身能力的方式。有时候很难找到该用哪个[贡献点](https://code.visualstudio.com/api/references/contribution-points)和 [VS Code API](https://code.visualstudio.com/api/references/vscode-api)。本篇把扩展能力分成几个类别，每个类别会介绍：
>
> - 扩展可以使用的一些功能
> - 指向详细介绍这些功能的文档链接
> - 几个扩展的点子
>
> 不过，为了保证 VS Code 的稳定和性能，我们也对扩展施加了一些[限制](#restrictions)。例如，扩展不能访问 VS Code 界面的 DOM。

这一篇是一张**能力地图**。它不讲具体怎么写代码，而是回答两个问题：

1. 扩展**能做**哪些事？每类能力对应后面的哪些章节？
2. 扩展**不能做**哪些事？

建议通读一遍，留个印象。以后有了扩展想法，先回到这里找到对应的类别，再去读详细的章节。

---

## 能力分类一览

先看全貌，后面再逐类展开：

| 类别 | 一句话说明 | 典型例子 | 详细章节 |
|---|---|---|---|
| 通用能力 | 几乎所有扩展都会用到的基础功能 | 命令、设置、快捷键、通知、存储 | [通用能力](./common-capabilities.md) |
| 主题 | 改变 VS Code 的外观 | 颜色主题、文件图标主题 | [主题](./theming.md) |
| 声明式语言功能 | **不写代码**，只写配置文件，就能支持一种语言的基础编辑功能 | 语法高亮、括号匹配、代码片段 | [语言扩展概览](https://code.visualstudio.com/api/language-extensions/overview#declarative-language-features) |
| 编程式语言功能 | **写代码**实现的高级语言功能 | 悬停提示、跳转定义、智能提示、错误检查 | [语言扩展概览](https://code.visualstudio.com/api/language-extensions/overview#programmatic-language-features) |
| 工作台扩展 | 往 VS Code 的界面上添加新部件 | 侧边栏树视图、状态栏项、Webview | [扩展工作台](./extending-workbench.md) |
| 调试 | 接入调试器，或者自动化调试流程 | 为某种语言提供调试支持 | [调试器扩展](https://code.visualstudio.com/api/extension-guides/debugger-extension) |

---

<a id="common-capabilities"></a>
## 通用能力（Common Capabilities）

> [通用能力](./common-capabilities.md)是任何扩展都可以使用的核心功能。
>
> 其中包括：
>
> - 注册命令、配置、快捷键或上下文菜单项。
> - 存储工作区数据或全局数据。
> - 显示通知消息。
> - 使用快速选择（Quick Pick）收集用户输入。
> - 打开系统的文件选择器，让用户选择文件或文件夹。
> - 使用 Progress API 显示耗时操作的进度。

这些是扩展的“基本功”，下一篇 [通用能力](./common-capabilities.md) 会逐个介绍。

---

<a id="theming"></a>
## 主题（Theming）

> [主题](./theming.md)控制 VS Code 的外观，包括编辑器中源代码的颜色和 VS Code 界面的颜色。如果你想把 VS Code 调成各种深浅的绿色，让自己像在《黑客帝国》里写代码；或者只是想打造一个极致简约的灰度工作区，那么主题就是为你准备的。
>
> **扩展点子**
>
> - 修改源代码的颜色。
> - 修改 VS Code 界面的颜色。
> - 把现有的 TextMate 主题移植到 VS Code。
> - 添加自定义的文件图标。

**TextMate 是什么？** TextMate 是 macOS 上一款较早的文本编辑器，它定义的主题格式和语法定义格式后来被很多编辑器沿用，VS Code 也兼容这套格式。所以在其他编辑器（如 Sublime Text）上已有的很多主题，都能比较方便地移植过来。

---

<a id="declarative-language-features"></a>
## 声明式语言功能（Declarative Language Features）

> [声明式语言功能](https://code.visualstudio.com/api/language-extensions/overview#declarative-language-features)为一种编程语言添加基础的文本编辑支持，比如括号匹配、自动缩进和语法高亮。这些都是以声明的方式实现的，不需要写任何代码。更高级的语言功能，比如智能提示（IntelliSense）或调试，请参阅[编程式语言功能](#programmatic-language-features)。
>
> **扩展点子**
>
> - 把常用的 JavaScript 代码片段打包成一个扩展。
> - 让 VS Code 认识一门新的编程语言。
> - 为某种编程语言添加或替换语法。
> - 通过语法注入（grammar injection）扩展现有的语法。
> - 把现有的 TextMate 语法移植到 VS Code。

“声明式”的意思是：**只写 JSON 等配置文件，告诉 VS Code 规则是什么，不写任何逻辑代码。** 例如：

- 语法高亮：写一个语法文件，用正则表达式描述“哪些文本是关键字、哪些是字符串”；
- 括号匹配、自动缩进：写一个语言配置文件，列出这门语言有哪些括号、注释用什么符号；
- 代码片段：写一个 JSON 文件，列出缩写和展开后的代码模板。

**语法注入**是指在已有语言的语法上“叠加”新规则，而不是替换整个语法。比如在 JavaScript 字符串里识别出 SQL 语句并高亮显示。

---

<a id="programmatic-language-features"></a>
## 编程式语言功能（Programmatic Language Features）

> [编程式语言功能](https://code.visualstudio.com/api/language-extensions/overview#programmatic-language-features)提供丰富的编程语言支持，比如悬停提示、跳转到定义、诊断错误、智能提示（IntelliSense）和 CodeLens。这些语言功能通过 [`vscode.languages.*`](https://code.visualstudio.com/api/references/vscode-api#languages) API 提供。扩展既可以直接使用这些 API，也可以编写一个语言服务器（Language Server），再通过 VS Code 的[语言服务器库](https://github.com/microsoft/vscode-languageserver-node)接入 VS Code。

这里列出的功能，在编辑器里分别是这样的：

| 功能 | 英文 | 在编辑器中的表现 |
|---|---|---|
| 悬停提示 | Hover | 鼠标停在代码上，弹出说明 |
| 跳转到定义 | Go to Definition | `F12` 或 `Ctrl+点击`，跳到定义所在的位置 |
| 诊断 | Diagnostics | 代码下方的红色、黄色波浪线，以及“问题”面板里的条目 |
| 智能提示 | IntelliSense | 输入时弹出的自动补全列表 |
| CodeLens | CodeLens | 代码上方显示的灰色小字，例如“3 个引用”“运行测试” |

**两种实现方式的区别：**

| 方式 | 做法 | 适合 |
|---|---|---|
| 直接使用 `vscode.languages.*` API | 在扩展代码里注册各种提供者（Provider） | 功能较简单，只给 VS Code 用 |
| 语言服务器 | 把语言分析逻辑写成一个独立的服务进程，通过语言服务器协议（LSP）与编辑器通信 | 功能复杂、计算量大，或希望同一套实现也能用于其他编辑器 |

语言服务器协议是一个通用标准，很多编辑器都支持。所以写好一个语言服务器后，不只是 VS Code，其他支持 LSP 的编辑器也能使用。后面的 [语言服务器扩展指南](https://code.visualstudio.com/api/language-extensions/language-server-extension-guide) 会详细讲解。

> 虽然我们提供了一份[语言功能列表](https://code.visualstudio.com/api/language-extensions/programmatic-language-features)，并说明了它们的设计用途，但这并不妨碍你创造性地使用这些 API。例如，CodeLens 和悬停提示很适合在代码旁边显示额外信息，而诊断错误也可以用来标出拼写错误或代码风格问题。

也就是说，这些 API 不一定只能用在“编程语言”上。比如拼写检查扩展就是借用诊断功能，把拼错的单词标上波浪线。

> **扩展点子**
>
> - 添加悬停提示，显示某个 API 的用法示例。
> - 用诊断功能报告源代码中的拼写错误或代码检查（linter）错误。
> - 为 HTML 注册一个新的代码格式化器。
> - 提供丰富的、能感知上下文的智能提示。
> - 为一门语言添加代码折叠、面包屑导航和大纲视图支持。

**面包屑导航**是编辑器顶部显示的“文件路径 › 类名 › 方法名”那一行；**大纲视图**是资源管理器侧边栏下方的 Outline 面板，列出文件中的类、函数等结构。

---

<a id="workbench-extensions"></a>
## 工作台扩展（Workbench Extensions）

> [工作台扩展](./extending-workbench.md)用来扩展 VS Code 的工作台界面。你可以在文件资源管理器中添加新的右键操作，甚至可以使用 VS Code 的 [TreeView](https://code.visualstudio.com/api/extension-guides/tree-view) API 构建一个自定义的资源管理器。如果你的扩展需要完全自定义的用户界面，可以使用 [Webview API](https://code.visualstudio.com/api/extension-guides/webview)，用标准的 HTML、CSS 和 JavaScript 构建自己的文档预览或界面。
>
> **扩展点子**
>
> - 在文件资源管理器中添加自定义的右键菜单操作。
> - 在侧边栏中创建一个新的、可交互的树视图。
> - 定义一个新的活动栏视图。
> - 在状态栏中显示新的信息。
> - 使用 `WebView` API 渲染自定义内容。
> - 贡献源代码管理（Source Control）提供者。

“工作台”就是 VS Code 的整个界面，各个区域的名称见 [扩展工作台](./extending-workbench.md) 一篇中的示意图。

**Webview 是“最后的手段”。** Webview 相当于在 VS Code 里嵌入一个网页，界面完全由你决定，非常灵活。但它更耗资源，外观也很难和 VS Code 原生界面保持一致。所以能用树视图、快速选择等原生部件解决的，优先用原生部件，实在不行再用 Webview。

**源代码管理提供者**：VS Code 左侧“源代码管理”面板默认支持 Git。通过这个 API，可以让它支持其他版本控制系统（例如 SVN、Mercurial）。

---

<a id="debugging"></a>
## 调试（Debugging）

> 你可以编写[调试器扩展](https://code.visualstudio.com/api/extension-guides/debugger-extension)，把 VS Code 的调试界面连接到特定的调试器或运行时，从而利用 VS Code 的[调试](https://code.visualstudio.com/docs/debugtest/debugging)功能。
>
> **扩展点子**
>
> - 贡献一个[调试适配器（Debug Adapter）实现](https://microsoft.github.io/debug-adapter-protocol/implementors/adapters/)，把 VS Code 的调试界面连接到某个调试器或运行时。
> - 指定调试器扩展支持哪些语言。
> - 为调试器使用的调试配置属性提供丰富的智能提示和悬停信息。
> - 提供调试配置的代码片段。

VS Code 自己并不懂怎么调试 Python、Go 或 C++。它定义了一套标准的**调试适配器协议（Debug Adapter Protocol，DAP）**：

```text
VS Code 调试界面  ←— DAP 协议 —→  调试适配器（扩展提供）  ←→  真正的调试器（如 gdb、Python 调试器）
（断点、变量、调用栈）                （负责“翻译”）
```

调试器扩展做的就是中间的“翻译”工作。这和语言服务器协议的思路一样：定义一个通用协议，让编辑器和具体实现解耦。

> 另一方面，VS Code 还提供了一组[调试扩展 API](https://code.visualstudio.com/api/references/vscode-api#debug)。借助它们，你可以在任何 VS Code 调试器之上实现与调试相关的功能，让用户的调试过程自动化。
>
> **扩展点子**
>
> - 根据动态生成的调试配置启动调试会话。
> - 跟踪调试会话的生命周期。
> - 通过代码创建和管理断点。

注意区分这两类调试相关的扩展：

| | 调试器扩展 | 使用调试 API 的扩展 |
|---|---|---|
| 做什么 | **提供**一种新的调试能力 | **使用**已有的调试能力 |
| 例子 | 让 VS Code 能调试某种新语言 | 一键用特定参数启动调试；调试开始时自动打开日志 |
| 难度 | 较高，要实现 DAP 协议 | 较低，调用 `vscode.debug.*` API 即可 |

---

<a id="ux-guidelines"></a>
## UX 指南（UX Guidelines）

> 为了让扩展无缝融入 VS Code 的用户界面，请参考 [UX 指南](https://code.visualstudio.com/api/ux-guidelines/overview)，在那里你会学到创建扩展界面的最佳实践，以及遵循 VS Code 推荐工作流的约定。

---

<a id="restrictions"></a>
## 限制（Restrictions）

> 我们对扩展施加了一些限制。下面是这些限制及其目的。

这一节非常重要。很多人刚开始做扩展时想实现的效果，恰恰是被这里禁止的，提前了解可以少走弯路。

<a id="no-dom-access"></a>
### 不能访问 DOM（No DOM Access）

> 扩展无法访问 VS Code 界面的 DOM。你**不能**编写一个给 VS Code 应用自定义 CSS 的扩展，也不能往 VS Code 界面中添加 HTML 元素。
>
> 在 VS Code 团队，我们一直在努力优化对底层 Web 技术的使用，以提供一个随时可用、响应迅速的编辑器。随着这些技术和产品的发展，我们还会继续调整对 DOM 的使用。为了确保扩展不会干扰 VS Code 的稳定性和性能，同时让我们能继续改进 VS Code 的 DOM 而不破坏现有扩展，我们把扩展运行在一个[扩展宿主（Extension Host）](https://code.visualstudio.com/api/advanced-topics/extension-host)进程中，并禁止扩展直接访问 DOM。

**背景知识：** VS Code 是用 Electron 开发的，它的界面本质上是一个网页，由 HTML 和 CSS 构成，DOM 就是这个网页的元素结构。

**扩展为什么碰不到 DOM？** 因为扩展代码根本不和界面运行在同一个地方：

```text
┌─────────────────────────┐          ┌──────────────────────────┐
│ 界面进程（渲染 DOM）       │  ←通信→  │ 扩展宿主进程               │
│ 编辑器、侧边栏、状态栏……    │          │ 所有扩展的代码都在这里运行  │
└─────────────────────────┘          └──────────────────────────┘
```

扩展运行在独立的“扩展宿主”进程中，只能通过 VS Code API 发出请求，例如“请在状态栏显示这段文字”，再由界面进程去实际渲染。这样做有两个好处：

- **稳定**：某个扩展卡死或崩溃，不会导致整个编辑器界面卡死；
- **可演进**：VS Code 可以随意重构自己的界面，只要 API 不变，扩展就不受影响。

**常见的“做不到”的需求：**

| 想做的事 | 能不能做 | 替代方案 |
|---|---|---|
| 修改 VS Code 界面的字体、间距、布局 | 不能 | 使用 VS Code 自带的设置项 |
| 改变界面颜色 | 能，但不是用 CSS | 写一个[颜色主题](./theming.md) |
| 在界面上任意位置插入 HTML 按钮 | 不能 | 用贡献点添加菜单项、编辑器标题栏按钮、状态栏项 |
| 显示完全自定义的界面 | 能，但只能在指定区域 | 使用 Webview |

Webview 虽然也是用 HTML 写的，但它运行在一个隔离的 iframe 中，只能控制自己内部的内容，同样碰不到 VS Code 自身的 DOM。

<a id="no-custom-style-sheets"></a>
### 不能使用自定义样式表（No custom style sheets）

> 用户或扩展提供的自定义样式表，依赖的是 DOM 结构和 CSS 类名。我们认为这些都属于内部实现，因此没有公开文档。为了演进、重构或改进 VS Code，我们需要能自由地修改用户界面。对 DOM 的任何改动都可能导致现有的自定义样式表失效，让样式表的作者感到沮丧，也会让用户因为样式表失效导致的界面错乱而体验很差。
>
> 相反，VS Code 致力于提供一套设计良好、支持界面定制的扩展 API。这套 API 有文档、有配套的工具和示例，并且在 VS Code 今后的所有版本中都保持稳定。

市面上有一些扩展通过修改 VS Code 的安装文件来注入自定义 CSS。这类做法不是官方支持的方式，VS Code 升级后常常失效，还可能导致 VS Code 提示“安装已损坏”。开发正式的扩展时不要走这条路。

**核心思路：** 只使用公开的 API 和贡献点。它们有文档、有承诺，升级后也能继续工作。

---

## 本篇小结

```text
扩展能做的事
├─ 通用能力：命令、设置、快捷键、菜单、存储、通知、快速选择、文件选择、输出、进度
├─ 主题：颜色主题、文件图标主题、产品图标主题
├─ 语言支持
│   ├─ 声明式（只写配置）：语法高亮、括号匹配、缩进、代码片段
│   └─ 编程式（写代码）：悬停、跳转定义、诊断、补全、CodeLens……
│        └─ 两种实现：直接用 vscode.languages.* API / 语言服务器（LSP）
├─ 工作台：视图容器、树视图、Webview、状态栏项、源代码管理
└─ 调试：调试器扩展（DAP 协议）/ 调试 API（自动化调试流程）

扩展不能做的事
└─ 访问 VS Code 界面的 DOM、注入自定义 CSS
     原因：扩展运行在独立的扩展宿主进程中，只能通过 API 与界面交互
```
