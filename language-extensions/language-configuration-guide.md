# 语言配置指南（Language Configuration Guide）

> 原文：[Language Configuration Guide](https://code.visualstudio.com/api/language-extensions/language-configuration-guide)
> 源文件：`microsoft/vscode-docs` → `api/language-extensions/language-configuration-guide.md`（DateApproved: 10/7/2026）

> [`contributes.languages`](../references/contribution-points.md#contributes.languages) 贡献点让你可以定义一个语言配置，控制以下声明式语言功能：
>
> - 注释切换
> - 括号定义
> - 自动闭合
> - 自动包围
> - 折叠
> - 单词模式（Word pattern）
> - 缩进规则

这些都是写代码时最基本的编辑体验：按 `Ctrl+/` 能注释、输入 `(` 自动补 `)`、按回车自动缩进。一门新语言（或者一种自定义格式的文件）如果没有语言配置，这些功能都不会生效。

**语言配置文件是怎么和语言关联起来的？** 原文没有展示这一步，补充如下：在 `contributes.languages` 中声明一门语言时，用 `configuration` 字段指向语言配置文件。

```json
"contributes": {
  "languages": [
    {
      "id": "mylang",                                  // 语言 ID
      "extensions": [".mylang"],                       // 哪些文件属于这种语言
      "aliases": ["My Language", "mylang"],            // 显示名称
      "configuration": "./language-configuration.json" // 语言配置文件
    }
  ]
}
```

> 这里有一个[语言配置示例](https://github.com/microsoft/vscode-extension-samples/tree/main/language-configuration-sample)，它配置了 JavaScript 文件的编辑体验。本指南解释 `language-configuration.json` 的内容：
>
> **注意：如果你的语言配置文件名是 `language-configuration.json`，或者以它结尾，在 VS Code 中编辑时就能获得自动补全和校验。**

```json
{
  "comments": {
    "lineComment": "//",
    "blockComment": ["/*", "*/"]
  },
  "brackets": [["{", "}"], ["[", "]"], ["(", ")"]],
  "autoClosingPairs": [
    { "open": "{", "close": "}" },
    { "open": "[", "close": "]" },
    { "open": "(", "close": ")" },
    { "open": "'", "close": "'", "notIn": ["string", "comment"] },
    { "open": "\"", "close": "\"", "notIn": ["string"] },
    { "open": "`", "close": "`", "notIn": ["string", "comment"] },
    { "open": "/**", "close": " */", "notIn": ["string"] }
  ],
  "autoCloseBefore": ";:.,=}])>` \n\t",
  "surroundingPairs": [
    ["{", "}"],
    ["[", "]"],
    ["(", ")"],
    ["'", "'"],
    ["\"", "\""],
    ["`", "`"]
  ],
  "folding": {
    "markers": {
      "start": "^\\s*//\\s*#?region\\b",
      "end": "^\\s*//\\s*#?endregion\\b"
    }
  },
  "wordPattern": "(-?\\d*\\.\\d\\w*)|([^\\`\\~\\!\\@\\#\\%\\^\\&\\*\\(\\)\\-\\=\\+\\[\\{\\]\\}\\\\\\|\\;\\:\\'\\\"\\,\\.\\<\\>\\/\\?\\s]+)",
  "indentationRules": {
    "increaseIndentPattern": "^((?!\\/\\/).)*(\\{[^}\"'`]*|\\([^)\"'`]*|\\[[^\\]\"'`]*)$",
    "decreaseIndentPattern": "^((?!.*?\\/\\*).*\\*/)?\\s*[\\)\\}\\]].*$"
  }
}
```

各个字段一览：

| 字段 | 控制的功能 | 下文小节 |
|---|---|---|
| `comments` | 注释切换 | [注释切换](#comment-toggling) |
| `brackets` | 括号匹配高亮、跳转到括号 | [括号定义](#brackets-definition) |
| `autoClosingPairs` | 输入左边自动补上右边 | [自动闭合](#autoclosing) |
| `autoCloseBefore` | 光标后面是哪些字符时也自动闭合 | [在……之前自动闭合](#autoclosing-before) |
| `surroundingPairs` | 选中文字后输入括号，自动包起来 | [自动包围](#autosurrounding) |
| `folding` | 折叠标记 | [折叠](#folding) |
| `wordPattern` | 什么算一个“单词” | [单词模式](#word-pattern) |
| `indentationRules` | 自动缩进 | [缩进规则](#indentation-rules) |
| `onEnterRules` | 按回车时的特殊行为（示例中没有） | [回车规则](#on-enter-rules) |

**注意 JSON 中的正则表达式要双重转义**：正则中的 `\s` 在 JSON 字符串里要写成 `\\s`，`\/` 要写成 `\\/`，所以这些正则看起来格外难读。

---

<a id="comment-toggling"></a>
## 注释切换（Comment toggling）

> VS Code 提供了两个用于切换注释的命令：**Toggle Line Comment**（切换行注释）和 **Toggle Block Comment**（切换块注释）。你可以指定 `comments.blockComment` 和 `comments.lineComment`，控制 VS Code 应该如何注释掉行 / 块。

```json
{
  "comments": {
    "lineComment": "//",
    "blockComment": ["/*", "*/"]
  }
}
```

两个命令的默认快捷键：行注释 `Ctrl+/`，块注释 `Shift+Alt+A`。比如 Python 只有行注释 `#`，就只写 `"lineComment": "#"`；HTML 只有块注释，就只写 `"blockComment": ["<!--", "-->"]`。

> 为了向后兼容，`lineComment` 属性支持两种格式：
>
> - 字符串值，用于简单的行注释定义。
> - 对象值，可以配置注释行的缩进行为。

```json
{
  "comments": {
    "lineComment": {
      "comment": "//",
      "noIndent": true
    },
    "blockComment": ["/*", "*/"]
  }
}
```

`noIndent: true` 的效果是：注释符号放在行首（第 0 列），而不是放在代码的缩进位置之后。

```text
noIndent: false（默认）        noIndent: true
    // foo();                 //    foo();
```

---

<a id="brackets-definition"></a>
## 括号定义（Brackets definition）

> 当你把光标移到这里定义的某个括号上时，VS Code 会高亮这个括号以及与它匹配的另一半。

```json
{
  "brackets": [["{", "}"], ["[", "]"], ["(", ")"]]
}
```

> 此外，当你运行 **Go to Bracket**（跳转到括号）或 **Select to Bracket**（选择到括号）时，VS Code 会使用上面的定义，找到最近的括号及其匹配的另一半。

这里定义的括号还用于“括号对着色”（不同层级的括号显示不同颜色）。括号不一定是单个字符，比如 Ruby 中可以定义 `["begin", "end"]`。

---

<a id="autoclosing"></a>
<a id="autoclosing"></a>
## 自动闭合（Autoclosing）

> 当你输入 `'` 时，VS Code 会创建一对单引号，并把光标放在中间：`'|'`。这一部分定义了这样的配对。

```json
{
  "autoClosingPairs": [
    { "open": "{", "close": "}" },
    { "open": "[", "close": "]" },
    { "open": "(", "close": ")" },
    { "open": "'", "close": "'", "notIn": ["string", "comment"] },
    { "open": "\"", "close": "\"", "notIn": ["string"] },
    { "open": "`", "close": "`", "notIn": ["string", "comment"] },
    { "open": "/**", "close": " */", "notIn": ["string"] }
  ]
}
```

> `notIn` 键会在某些代码范围内禁用这个功能。例如，当你编写下面的代码时：

```js
// ES6's Template String
`ES6's Template String`;
```

> 单引号不会被自动闭合。

**`notIn` 的作用：** 在注释或字符串中，单引号常常是英文的撇号（比如 `ES6's`），而不是字符串的开始。如果这时也自动补一个 `'`，用户还得手动删掉。所以对单引号设置 `"notIn": ["string", "comment"]`，在字符串和注释中不自动闭合。`notIn` 可选的值是 `"string"` 和 `"comment"`，“哪里是字符串、哪里是注释”是由 [语法高亮](./syntax-highlight-guide.md) 中的 TextMate 语法判断的。

最后一行 `/**` → ` */` 的效果：输入 `/**` 后自动补上 ` */`，方便写 JSDoc 注释。

> 不需要 `notIn` 属性的配对，也可以使用更简单的语法：

```json
{
  "autoClosingPairs": [ ["{", "}"], ["[", "]"] ]
}
```

> 用户可以通过 `editor.autoClosingQuotes` 和 `editor.autoClosingBrackets` 设置调整自动闭合的行为。

<a id="autoclosing-before"></a>
### 在……之前自动闭合（Autoclosing before）

> 默认情况下，只有当光标后面紧跟着空白时，VS Code 才会自动闭合配对。所以当你在下面的 JSX 代码中输入 `{` 时，不会自动闭合：

```js
const Component = () =>
  <div className={>
                  ^ 默认情况下不会自动闭合
  </div>
```

> 不过，下面的定义会覆盖这个行为：

```json
{
  "autoCloseBefore": ";:.,=}])>` \n\t"
}
```

> 现在，当你在 `>` 之前输入 `{` 时，VS Code 会用 `}` 自动闭合它。

**为什么默认只在空白前自动闭合？** 如果光标后面紧跟着一个单词，比如在 `|foo` 前输入 `(`，用户多半是想把 `foo` 括起来写成 `(foo`，这时自动补一个 `)` 变成 `()foo` 反而碍事。`autoCloseBefore` 列出了“光标后面是这些字符时，也可以放心地自动闭合”的字符。示例的字符串中包括 `;`、`:`、`.`、`,`、`=`、`}`、`]`、`)`、`>`、反引号、空格、换行和 Tab。

---

<a id="autosurrounding"></a>
<a id="autosurrounding"></a>
## 自动包围（Autosurrounding）

> 当你在 VS Code 中选中一个范围并输入一个左括号时，VS Code 会用一对括号把选中的内容包围起来。这个功能叫作自动包围，在这里你可以为特定的语言定义自动包围的配对：

```json
{
  "surroundingPairs": [
    ["{", "}"],
    ["[", "]"],
    ["(", ")"],
    ["'", "'"],
    ["\"", "\""],
    ["`", "`"]
  ]
}
```

> 用户可以通过 `editor.autoSurround` 设置调整自动包围的行为。

例如选中 `hello`，输入 `"`，就变成 `"hello"`。Markdown 中常常还会加上 `["*", "*"]`、`["_", "_"]`，选中文字后输入 `*` 就变成斜体。

---

<a id="folding"></a>
<a id="folding"></a>
## 折叠（Folding）

> 在 VS Code 中，折叠要么基于缩进，要么由贡献的折叠范围提供者来定义：
>
> - **基于缩进、带标记的折叠**：如果给定的语言没有可用的折叠范围提供者，或者用户把 `editor.foldingStrategy` 设为了 `indentation`，就使用基于缩进的折叠。当某一行的缩进比后面一行或多行的缩进小时，就开始一个折叠区域；遇到缩进相同或更小的行时，折叠区域结束。空行会被忽略。
>
>   此外，语言配置还可以定义开始和结束标记。它们被定义为 `folding.markers` 中的 `start` 和 `end` 正则表达式。找到匹配的行时，就会在这一对标记之间创建一个折叠范围。折叠标记必须是非空的，通常看起来像 `//#region` 和 `//#endregion`。
>
> 下面的 JSON 为 `//#region` 和 `//#endregion` 创建了折叠标记。

```json
{
  "folding": {
    "markers": {
      "start": "^\\s*//\\s*#?region\\b",
      "end": "^\\s*//\\s*#?endregion\\b"
    }
  }
}
```

> - **语言服务器折叠**：语言服务器响应 [`textDocument/foldingRange`](https://microsoft.github.io/language-server-protocol/specification#textDocument_foldingRange) 请求，返回一个折叠范围的列表，VS Code 会把这些范围渲染为折叠标记。在[编程式语言功能](./programmatic-language-features.md)主题中了解更多关于语言服务器协议中折叠支持的信息。

| 折叠方式 | 由谁计算 | 准确度 |
|---|---|---|
| 基于缩进 | VS Code 根据缩进自动计算 | 一般，适合 Python、YAML 等靠缩进表示结构的语言 |
| 折叠标记（`folding.markers`） | 语言配置中的正则 | 只用于用户手动标记的区域 |
| 折叠范围提供者（语言服务器） | 扩展代码分析语法 | 最准确，比如能准确折叠多行字符串、多行注释 |

示例中的正则 `^\s*//\s*#?region\b` 匹配“行首可以有空白，然后是 `//`，然后可以有空白，然后可以有 `#`，然后是 `region`”，所以 `// region`、`//#region`、`  // #region` 都能匹配。

---

<a id="word-pattern"></a>
## 单词模式（Word Pattern）

> `wordPattern` 定义了在这门编程语言中什么被视为一个单词。如果设置了 `wordPattern`，代码建议功能会使用这个设置来确定单词的边界。注意，这个设置不会影响与单词相关的编辑器命令，那些命令由编辑器设置 `editor.wordSeparators` 控制。

```json
{
  "wordPattern": "(-?\\d*\\.\\d\\w*)|([^\\`\\~\\!\\@\\#\\%\\^\\&\\*\\(\\)\\-\\=\\+\\[\\{\\]\\}\\\\\\|\\;\\:\\'\\\"\\,\\.\\<\\>\\/\\?\\s]+)"
}
```

这个正则分两部分：第一部分匹配数字（如 `-3.14`）；第二部分匹配“不包含任何标点符号和空白的连续字符”。

**为什么需要自定义？** 不同的语言对“单词”的理解不同。比如 CSS 中 `background-color` 是一个完整的属性名，应该被当作一个单词（补全时整体替换）；而在 JavaScript 中 `a-b` 是 `a` 减 `b`，是两个单词。示例的正则把 `-` 排除在单词之外，适用于 JavaScript；CSS 的语言配置中则会允许 `-`。

“与单词相关的编辑器命令”指的是 `Ctrl+←` / `Ctrl+→` 按单词移动光标、双击选中单词等，它们由 `editor.wordSeparators` 设置控制，与 `wordPattern` 无关。

---

<a id="indentation-rules"></a>
## 缩进规则（Indentation Rules）

> `indentationRules` 定义了在你输入、粘贴和移动行时，编辑器应该如何调整当前行或下一行的缩进。

```json
{
  "indentationRules": {
    "increaseIndentPattern": "^((?!\\/\\/).)*(\\{[^}\"'`]*|\\([^)\"'`]*|\\[[^\\]\"'`]*)$",
    "decreaseIndentPattern": "^((?!.*?\\/\\*).*\\*/)?\\s*[\\)\\}\\]].*$"
  }
}
```

> 例如，`if (true) {` 匹配 `increaseIndentPattern`，所以如果你在左括号 `{` 之后按 `Enter`，编辑器会自动缩进一次，你的代码最终会变成：

```javascript
if (true) {
  console.log();
```

> 除了 `increaseIndentPattern` 和 `decreaseIndentPattern` 之外，还有两条缩进规则：
>
> - `indentNextLinePattern`：如果一行匹配这个模式，那么**只有它的下一行**应该缩进一次。
> - `unIndentedLinePattern`：如果一行匹配这个模式，那么它的缩进不应该被改变，也不应该用其他规则来评估它。

| 规则 | 匹配时的效果 | 例子 |
|---|---|---|
| `increaseIndentPattern` | 下一行开始，缩进加一级 | 以 `{` 结尾的行 |
| `decreaseIndentPattern` | 当前行的缩进减一级 | 以 `}` 开头的行（输入 `}` 时自动往回缩） |
| `indentNextLinePattern` | 只有下一行缩进一级，再下一行恢复 | `if (x)` 后面不带大括号，只有一条语句 |
| `unIndentedLinePattern` | 这一行不参与缩进计算 | 一些特殊的行，比如 C 语言中的 `#define` 预处理指令 |

示例中 `increaseIndentPattern` 的意思是：这一行不是注释（`(?!\/\/)`），并且以一个未闭合的 `{`、`(` 或 `[` 结尾。

> 如果没有为这门编程语言设置缩进规则，编辑器会在一行以左括号结尾时缩进，在你输入右括号时减少缩进。这里的括号由 `brackets` 定义。
>
> 注意，`editor.formatOnPaste` 设置由 [`DocumentRangeFormattingEditProvider`](https://code.visualstudio.com/api/references/vscode-api#DocumentRangeFormattingEditProvider) 控制，不受自动缩进的影响。

也就是说，“粘贴时自动格式化”需要语言扩展通过代码提供格式化功能（见 [编程式语言功能](./programmatic-language-features.md)），只靠语言配置中的缩进规则做不到。

---

<a id="on-enter-rules"></a>
## 回车规则（On Enter Rules）

> `onEnterRules` 定义了一个规则列表，在编辑器中按下 `Enter` 时会对它们进行评估。

```json
{
  "onEnterRules": [{
    "beforeText": "^\\s*(?:def|class|for|if|elif|else|while|try|with|finally|except|async).*?:\\s*$",
    "action": { "indent": "indent" }
  }]
}
```

这个例子是 Python 的规则：光标前的文字是以 `def`、`class`、`if` 等关键字开头、以 `:` 结尾的行（比如 `def foo():`），按回车后，新的一行自动缩进一级。

> 按下 `Enter` 时，会用以下属性检查光标之前、之后或上一行的文字：
>
> - `beforeText`（必填）：一个正则表达式，匹配光标之前的文字（限于当前行）。
> - `afterText`：一个正则表达式，匹配光标之后的文字（限于当前行）。
> - `previousLineText`：一个正则表达式，匹配光标上一行的文字。
>
> 如果所有指定的属性都匹配，就认为这条规则匹配，后面的 `onEnterRules` 不会再被评估。一条 `onEnterRule` 可以指定以下操作：
>
> - `indent`（必填）：`none`、`indent`、`outdent`、`indentOutdent` 之一。
>   - `none` 表示新行会继承当前行的缩进。
>   - `indent` 表示新行会相对于当前行缩进。
>   - `outdent` 表示新行会相对于当前行减少缩进。
>   - `indentOutdent` 表示会插入两个新行，第一行缩进，第二行减少缩进。
> - `appendText`：一个字符串，会被追加在新行中缩进之后的位置。
> - `removeText`：要从新行的缩进中删除的字符数。

**几个常用的回车规则：**

`indentOutdent` 的效果：光标在 `{|}` 中间按回车，变成三行，光标在中间缩进的那一行：

```text
{|}          →     {
                       |
                   }
```

```json
{ "beforeText": "\\{\\s*$", "afterText": "^\\s*\\}", "action": { "indent": "indentOutdent" } }
```

`appendText` 的效果：在 JSDoc 注释中按回车，新行自动以 ` * ` 开头：

```json
{
  "beforeText": "^\\s*\\/\\*\\*(?!\\/)([^\\*]|\\*(?!\\/))*$",
  "afterText": "^\\s*\\*\\/$",
  "action": { "indent": "indentOutdent", "appendText": " * " }
}
```

**与缩进规则的区别：** `indentationRules` 只看“这一行”的内容来决定缩进；`onEnterRules` 可以同时看光标前、光标后和上一行，并且还能追加文字，更灵活。两者冲突时，匹配到的回车规则优先。

---

## 本篇小结

```text
关联：contributes.languages[].configuration → language-configuration.json（以此结尾可获得补全和校验）

comments          行注释 / 块注释（lineComment 可写成对象，noIndent 控制注释符位置）
brackets          括号匹配高亮、跳转到括号、括号着色
autoClosingPairs  自动闭合；notIn: ["string", "comment"] 避免在字符串 / 注释中闭合
autoCloseBefore   光标后是这些字符时也自动闭合（默认只在空白前）
surroundingPairs  选中后输入括号自动包围
folding.markers   //#region 风格的折叠标记（更准确的折叠需要语言服务器）
wordPattern       什么算一个单词（影响补全，不影响按单词移动光标）
indentationRules  increase / decrease / indentNextLine / unIndentedLine
onEnterRules      回车时根据 beforeText / afterText / previousLineText 决定 indent、appendText、removeText

所有正则都写在 JSON 字符串中，反斜杠要双写
```
