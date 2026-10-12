# 语法高亮指南（Syntax Highlight Guide）

> 原文：[Syntax Highlight Guide](https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide)
> 源文件：`microsoft/vscode-docs` → `api/language-extensions/syntax-highlight-guide.md`（DateApproved: 10/7/2026）

> 语法高亮决定了 VS Code 编辑器中显示的源代码的颜色和样式。它负责让 JavaScript 中的 `if`、`for` 等关键字，与字符串、注释和变量名显示成不同的颜色。
>
> 语法高亮由两个部分组成：
>
> - [分词（Tokenization）](#tokenization)：把文本拆分成一个标记（token）列表
> - [主题化（Theming）](#theming)：使用主题或用户设置，把这些标记映射到特定的颜色和样式
>
> 在深入细节之前，一个好的开始是试用一下[作用域检查器](#scope-inspector)工具，看看一个源文件中有哪些标记，以及它们匹配了哪些主题规则。要同时查看语义标记和语法标记，可以在一个 TypeScript 文件上使用内置的主题（例如 Dark+）。

**两个部分的分工：**

```text
源代码  ──分词（语言扩展的语法文件负责）──→  标记 + 作用域  ──主题化（颜色主题负责）──→  颜色
"if"                                        keyword.control.js                      紫色
```

- **语言扩展**只负责告诉 VS Code “这段文字是什么”（关键字、字符串、注释……），不决定颜色；
- **颜色主题**负责“什么东西显示成什么颜色”（见 [颜色主题](../extension-guides/color-theme.md)）。

两者通过“作用域”这个名字联系起来。这样一门新语言的语法写好后，自动适配所有的颜色主题。[主题](../extension-capabilities/theming.md) 一篇中的颜色主题原理图，展示的就是这个过程的后半部分。

---

<a id="tokenization"></a>
## 分词（Tokenization）

> 文本的分词，就是把文本拆分成一个个片段，并给每个片段分配一个标记类型。
>
> VS Code 的分词引擎由 [TextMate 语法][tm-grammars]驱动。TextMate 语法是一组结构化的正则表达式，写成 plist（XML）或 JSON 文件。VS Code 扩展可以通过 `grammars` 贡献点贡献语法。
>
> TextMate 分词引擎与渲染器运行在同一个进程中，标记会随着用户的输入而更新。标记用于语法高亮，也用于把源代码划分为注释、字符串、正则表达式等区域。

“划分为注释、字符串等区域”有什么用？[语言配置](./language-configuration-guide.md#autoclosing) 中 `autoClosingPairs` 的 `notIn: ["string", "comment"]` 就依赖它：VS Code 通过分词结果知道光标在不在字符串或注释里。

> 从 1.43 版本开始，VS Code 还允许扩展通过[语义标记提供者（Semantic Token Provider）](https://code.visualstudio.com/api/references/vscode-api#DocumentSemanticTokensProvider)提供分词。语义提供者通常由语言服务器实现，语言服务器对源文件有更深入的理解，可以在项目的上下文中解析符号。例如，一个常量的变量名可以在整个项目中都用常量的高亮来渲染，而不仅仅是在它声明的地方。
>
> 基于语义标记的高亮被看作是基于 TextMate 的语法高亮的补充。语义高亮叠加在语法高亮之上。由于语言服务器可能需要一些时间来加载和分析项目，语义标记的高亮可能会在短暂的延迟之后才出现。
>
> 本文重点介绍基于 TextMate 的分词。语义分词及其主题化，在[语义高亮指南](./semantic-highlight-guide.md)中讲解。

两者的对比在 [主题](../extension-capabilities/theming.md#color-theme) 一篇中有表格。本篇只讲 TextMate 语法。

<a id="textmate-grammars"></a>
### TextMate 语法（TextMate grammars）

> VS Code 使用 [TextMate 语法][tm-grammars]作为语法分词引擎。TextMate 语法是为 TextMate 编辑器发明的，由于开源社区创建和维护了大量的语言包，它已经被许多其他编辑器和 IDE 采用。
>
> TextMate 语法依赖 [Oniguruma 正则表达式](https://macromates.com/manual/en/regular_expressions)，通常写成 plist 或 JSON。你可以在[这里](https://www.apeth.com/nonblog/stories/textmatebundle.html)找到一份不错的 TextMate 语法入门介绍，也可以看看现有的 TextMate 语法，进一步了解它们是如何工作的。

**Oniguruma** 是一个正则表达式库，语法和 JavaScript 的正则大体相同，但支持更多特性（比如后行断言）。写语法时，按平时写正则的习惯来写即可。

**“看看现有的语法”** 是最好的学习方法：VS Code 内置的每一种语言的语法文件都在 [microsoft/vscode 仓库的 extensions 目录](https://github.com/microsoft/vscode/tree/main/extensions) 中，比如 `extensions/javascript/syntaxes/`。

<a id="textmate-tokens-and-scopes"></a>
### TextMate 标记与作用域（TextMate tokens and scopes）

> 标记是属于同一个程序元素的一个或多个字符。标记的例子包括 `+` 和 `*` 等运算符、`myVar` 等变量名，或者 `"my string"` 等字符串。
>
> 每个标记都与一个作用域相关联，作用域定义了这个标记的上下文。作用域是一个用点分隔的标识符列表，指定了当前标记的上下文。例如，JavaScript 中的 `+` 运算的作用域是 `keyword.operator.arithmetic.js`。

作用域名从左到右，从“大类”到“小类”：

```text
keyword.operator.arithmetic.js
   │       │         │      └─ 语言：JavaScript
   │       │         └──────── 具体类别：算术
   │       └────────────────── 子类：运算符
   └────────────────────────── 大类：关键字
```

> 主题把作用域映射到颜色和样式，以提供语法高亮。TextMate 提供了一份许多主题都会针对的[常用作用域列表][tm-grammars]。为了让你的语法得到尽可能广泛的支持，请尽量在已有的作用域基础上构建，而不是定义新的作用域。

**这一点很重要：** 颜色主题只会为常用的作用域设置颜色。如果你的语法把关键字命名为 `mylang.special-word`，所有主题都不认识它，它就不会有颜色；命名为 `keyword.control.mylang`，所有主题都会把它显示成关键字的颜色。常用的作用域大类有：

| 作用域 | 用于 |
|---|---|
| `comment` | 注释（`comment.line`、`comment.block`） |
| `string` | 字符串（`string.quoted.double` 等） |
| `constant` | 常量（`constant.numeric` 数字、`constant.language` 如 `true`） |
| `keyword` | 关键字（`keyword.control` 如 `if`、`keyword.operator` 运算符） |
| `storage` | 类型和修饰符（`storage.type` 如 `function`、`storage.modifier` 如 `static`） |
| `entity` | 实体名称（`entity.name.function` 函数名、`entity.name.type` 类型名） |
| `variable` | 变量（`variable.parameter` 参数） |
| `support` | 框架或库提供的内容（`support.function` 内置函数） |
| `punctuation` | 标点符号 |

> 作用域是嵌套的，所以每个标记还关联着一个父级作用域的列表。下面的示例使用[作用域检查器](#scope-inspector)显示了一个简单的 JavaScript 函数中 `+` 运算符的作用域层级。最具体的作用域列在最上面，较通用的父级作用域列在下面：

![语法高亮的作用域](images/syntax-highlighting/scopes.png)

截图中，光标在 `return [ 1 + 2 ];` 的 `+` 上，检查器的 “textmate scopes” 一栏从上到下列出了：`keyword.operator.arithmetic.js`（`+` 自己）、`meta.array.literal.js`（在一个数组字面量中）、`meta.block.js`（在一个代码块中）、`meta.function.js`（在一个函数中）、`source.js`（在一个 JavaScript 文件中）。最下面一行显示，它最终匹配的主题规则是 `keyword.operator`，颜色为 `#D0D6B5`。

> 父级作用域的信息也用于主题化。当主题针对某个作用域设置样式时，所有具有这个父级作用域的标记都会被着色，除非主题还为它们各自的作用域提供了更具体的着色。

也就是说，主题为 `keyword` 设置了颜色，那么 `keyword.operator.arithmetic.js`、`keyword.control.js` 等所有以 `keyword` 开头的作用域都会使用这个颜色；如果主题还单独为 `keyword.operator` 设置了颜色，那么运算符就使用后者。这就是截图中 `+` 匹配到的是 `keyword.operator` 规则的原因。

<a id="configure-bracket-matching-scopes"></a>
### 配置括号匹配的作用域（Configure bracket matching scopes）

> 有些语言包含一些不应该参与括号匹配的标记，尽管它们在视觉上很像括号。
>
> 有两个用于配置括号匹配行为的属性：
>
> - `balancedBracketScopes`：定义哪些作用域参与括号匹配。默认情况下，所有作用域都包括在内。
> - `unbalancedBracketScopes`：定义应该被排除在括号匹配之外的作用域。

```json
{
  "unbalancedBracketScopes": [
    "meta.scope.case-pattern.shell"
  ]
}
```

示例是 Shell 脚本中的情况：`case` 语句的分支写成 `pattern)`，只有右括号没有左括号。如果它参与括号匹配，括号着色就会全乱。把这个作用域排除掉即可。这两个属性写在 `package.json` 的 `contributes.grammars` 条目中（与 `scopeName`、`path` 同级）。

<a id="contributing-a-basic-grammar"></a>
### 贡献一个基本的语法（Contributing a basic grammar）

> VS Code 支持 JSON 格式的 TextMate 语法。它们通过 `grammars` [贡献点](../references/contribution-points.md)贡献。
>
> 每个语法贡献都指定：这个语法适用的语言的标识符、语法中标记的顶层作用域名，以及语法文件的相对路径。下面的例子展示了一个虚构的 `abc` 语言的语法贡献：

```json
{
  "contributes": {
    "languages": [
      {
        "id": "abc",
        "extensions": [".abc"]
      }
    ],
    "grammars": [
      {
        "language": "abc",
        "scopeName": "source.abc",
        "path": "./syntaxes/abc.tmGrammar.json"
      }
    ]
  }
}
```

| 字段 | 含义 |
|---|---|
| `languages[].id` / `extensions` | 声明一门语言 `abc`，`.abc` 文件属于这种语言 |
| `grammars[].language` | 这个语法用于哪种语言（对应上面的 `id`） |
| `grammars[].scopeName` | 顶层作用域名，整个文件的所有标记都在这个作用域之下。惯例是 `source.语言名`（编程语言）或 `text.语言名`（标记语言，如 `text.html.markdown`） |
| `grammars[].path` | 语法文件的路径 |

> 语法文件本身由一个顶层规则组成。它通常分为一个 `patterns` 部分，列出程序的顶层元素；以及一个 `repository`，定义每一个元素。语法中的其他规则可以用 `{ "include": "#id" }` 引用 `repository` 中的元素。
>
> 这个 `abc` 语法示例把字母 `a`、`b` 和 `c` 标记为关键字，把嵌套的括号标记为表达式。

```json
{
  "scopeName": "source.abc",
  "patterns": [{ "include": "#expression" }],
  "repository": {
    "expression": {
      "patterns": [{ "include": "#letter" }, { "include": "#paren-expression" }]
    },
    "letter": {
      "match": "a|b|c",
      "name": "keyword.letter"
    },
    "paren-expression": {
      "begin": "\\(",
      "end": "\\)",
      "beginCaptures": {
        "0": { "name": "punctuation.paren.open" }
      },
      "endCaptures": {
        "0": { "name": "punctuation.paren.close" }
      },
      "name": "expression.group",
      "patterns": [{ "include": "#expression" }]
    }
  }
}
```

**语法文件的结构：**

| 部分 | 含义 |
|---|---|
| `scopeName` | 与 `package.json` 中的一致 |
| `patterns` | 顶层规则：文件中的文字依次用这些规则去匹配 |
| `repository` | 规则“仓库”：给每条规则起个名字，供其他地方用 `#名字` 引用 |
| `{ "include": "#xxx" }` | 引用 `repository` 中名为 `xxx` 的规则 |

**两种规则：**

| 类型 | 写法 | 用于 | 示例中的 |
|---|---|---|---|
| 单行匹配 | `match` + `name` | 用一个正则匹配一段文字，给它一个作用域 | `letter`：匹配 `a`、`b`、`c`，作用域 `keyword.letter` |
| 区间匹配 | `begin` + `end` + `patterns` | 从 `begin` 匹配到 `end`，中间的内容再用 `patterns` 中的规则匹配；适合字符串、注释、代码块等可以跨多行、可以嵌套的结构 | `paren-expression`：从 `(` 到 `)` |

`beginCaptures` / `endCaptures` 给 `begin` / `end` 匹配到的文字单独指定作用域（`"0"` 表示整个匹配；如果正则中有分组，`"1"`、`"2"` 表示各个分组）。

`paren-expression` 的 `patterns` 中又引用了 `#expression`，而 `expression` 又包含 `paren-expression`，这样就实现了括号的**递归嵌套**。

> 语法引擎会尝试依次把 `expression` 规则应用到文档中的所有文本上。对于下面这样一个简单的程序：

```text
a
(
    b
)
x
(
    (
        c
        xyz
    )
)
(
a
```

> 这个示例语法会产生以下作用域（从左到右，从最具体的作用域列到最不具体的作用域）：

```text
a               keyword.letter, source.abc
(               punctuation.paren.open, expression.group, source.abc
    b           keyword.letter, expression.group, source.abc
)               punctuation.paren.close, expression.group, source.abc
x               source.abc
(               punctuation.paren.open, expression.group, source.abc
    (           punctuation.paren.open, expression.group, expression.group, source.abc
        c       keyword.letter, expression.group, expression.group, source.abc
        xyz     expression.group, expression.group, source.abc
    )           punctuation.paren.close, expression.group, expression.group, source.abc
)               punctuation.paren.close, expression.group, source.abc
(               punctuation.paren.open, expression.group, source.abc
a               keyword.letter, expression.group, source.abc
```

> 注意，没有被任何规则匹配到的文本（比如字符串 `xyz`）会被包含在当前的作用域中。文件末尾的最后一个括号属于 `expression.group`，即使它的 `end` 规则没有被匹配，因为在匹配到 `end` 规则之前，先遇到了文档的结尾。

几点观察：

- `x` 不是 `a`、`b`、`c`，也不是括号，所以只有顶层作用域 `source.abc`；
- 嵌套的括号中，`expression.group` 出现了两次，体现了嵌套的层级；
- 最后一个 `(` 没有对应的 `)`，从它开始到文件末尾的所有内容（包括最后的 `a`）都属于这个未闭合的 `expression.group`。这在写代码的过程中很常见（比如刚输入了一个 `"` 还没输入另一个），所以语法规则要能容忍不完整的代码。

<a id="embedded-languages"></a>
### 嵌入式语言（Embedded languages）

> 如果你的语法中包含嵌入在父语言中的语言，比如 HTML 中的 CSS 样式块，你可以使用 `embeddedLanguages` 贡献点，告诉 VS Code 把嵌入的语言当作与父语言不同的语言来对待。这可以确保括号匹配、注释和其他基本的语言功能在嵌入的语言中按预期工作。
>
> `embeddedLanguages` 贡献点把嵌入语言中的一个作用域映射到一个顶层语言作用域。在下面的例子中，`meta.embedded.block.javascript` 作用域中的所有标记都会被当作 JavaScript 内容：

```json
{
  "contributes": {
    "grammars": [
      {
        "path": "./syntaxes/abc.tmLanguage.json",
        "scopeName": "source.abc",
        "embeddedLanguages": {
          "meta.embedded.block.javascript": "javascript"
        }
      }
    ]
  }
}
```

> 现在，如果你尝试在一组标记为 `meta.embedded.block.javascript` 的标记中注释代码或触发代码片段，它们会使用正确的 JavaScript 风格的 `//` 注释，以及正确的 JavaScript 代码片段。

**效果：** 在 HTML 的 `<script>` 标签中按 `Ctrl+/`，插入的是 `//` 而不是 `<!-- -->`；输入 JavaScript 的代码片段前缀，出现的是 JavaScript 的代码片段。这里只涉及语法高亮和语言配置这类基础功能；要让补全、悬停等智能功能也在嵌入的语言中工作，见 [嵌入式语言](./embedded-languages.md)。

（这里文件名用的是 `.tmLanguage.json`，上一节用的是 `.tmGrammar.json`，两种命名都可以，内容格式相同。）

<a id="developing-a-new-grammar-extension"></a>
### 开发一个新的语法扩展（Developing a new grammar extension）

> 要快速创建一个新的语法扩展，使用 [VS Code 的 Yeoman 模板](../get-started/your-first-extension.md)运行 `yo code`，并选择 `New Language` 选项：

![在 yo code 中选择 “new language” 模板](images/syntax-highlighting/yo-new-language.png)

> Yeoman 会通过一些基本的问题带你搭建新的扩展。创建一个新语法时，重要的问题有：
>
> - `Language id`：你的语言的唯一标识符。
> - `Language name`：你的语言的人类可读名称。
> - `Scope names`：语法的根 TextMate 作用域名。

![填写 “new language” 的问题](images/syntax-highlighting/yo-new-language-questions.png)

> 生成器假设你既要定义一门新的语言，也要为这门语言定义一个新的语法。如果你是在为一门已有的语言创建语法，只需在这些问题中填写目标语言的信息，并且一定要删除生成的 `package.json` 中的 `languages` 贡献点。
>
> 回答完所有问题后，Yeoman 会创建一个具有以下结构的新扩展：

![一个新的语言扩展](images/syntax-highlighting/generated-new-language-extension.png)

生成的扩展中通常包括：`package.json`（包含 `languages` 和 `grammars` 贡献）、`syntaxes/` 目录下的语法文件、`language-configuration.json`（见 [语言配置](./language-configuration-guide.md)）。

> 记住，如果你是在为一门 VS Code 已经认识的语言贡献语法，一定要删除生成的 `package.json` 中的 `languages` 贡献点。

为什么要删除？`languages` 用来**声明一门新语言**。如果 VS Code 已经认识这门语言（比如 `javascript`），再声明一次会和内置的声明发生冲突或重复。只需要保留 `grammars`，用 `language` 字段指向已有的语言 ID 即可。

<a id="converting-an-existing-textmate-grammar"></a>
#### 转换现有的 TextMate 语法（Converting an existing TextMate grammar）

> `yo code` 也可以帮你把一个现有的 TextMate 语法转换成 VS Code 扩展。同样，先运行 `yo code` 并选择 `Language extension`。当询问已有的语法文件时，给出一个 `.tmLanguage` 或 `.json` TextMate 语法文件的完整路径：

![转换现有的 TextMate 语法](images/syntax-highlighting/yo-convert.png)

（这里的 `Language extension` 和上一节的 `New Language` 指的是生成器中的同一个选项。）

<a id="using-yaml-to-write-a-grammar"></a>
#### 使用 YAML 编写语法（Using YAML to write a grammar）

> 随着语法变得越来越复杂，以 JSON 形式理解和维护它可能会变得很困难。如果你发现自己在编写复杂的正则表达式，或者需要添加注释来解释语法的某些方面，可以考虑改用 YAML 来定义语法。
>
> YAML 语法与基于 JSON 的语法结构完全相同，但让你可以使用 YAML 更简洁的语法，以及多行字符串和注释等功能。

![使用多行字符串和注释的 YAML 语法](images/syntax-highlighting/yaml-grammar.png)

> VS Code 只能加载 JSON 语法，所以基于 YAML 的语法必须转换为 JSON。[`js-yaml` 包](https://www.npmjs.com/package/js-yaml)和它的命令行工具可以轻松做到这一点。

```bash
# 在扩展中把 js-yaml 安装为开发依赖
$ npm install js-yaml --save-dev

# 使用命令行工具把 YAML 语法转换为 JSON
$ npx js-yaml syntaxes/abc.tmLanguage.yaml > syntaxes/abc.tmLanguage.json
```

**YAML 的优势在正则上尤其明显：** JSON 中正则的反斜杠要双写（`\\(`），而 YAML 中用单引号字符串可以原样书写（`'\('`）；YAML 还能写注释，可以给复杂的正则加上说明。可以把转换命令放进 `package.json` 的 `scripts` 中，比如 `"build:grammar": "js-yaml syntaxes/abc.tmLanguage.yaml > syntaxes/abc.tmLanguage.json"`，在编译前执行。

<a id="injection-grammars"></a>
### 注入语法（Injection grammars）

> 注入语法让你可以扩展一个已有的语法。注入语法是一个普通的 TextMate 语法，它被注入到一个已有语法中的特定作用域里。注入语法的应用示例：
>
> - 高亮注释中的 `TODO` 等关键字。
> - 为已有的语法添加更具体的作用域信息。
> - 为 Markdown 围栏代码块中的一门新语言添加高亮。

**注入和替换的区别：** 你想让 JavaScript 注释中的 `TODO` 显示成特殊的颜色，但不想（也不应该）重写整个 JavaScript 语法。注入语法就是“在别人的语法里加几条规则”。

<a id="creating-a-basic-injection-grammar"></a>
#### 创建一个基本的注入语法（Creating a basic injection grammar）

> 注入语法和普通语法一样，通过 `package.json` 贡献。不过，注入语法不是指定 `language`，而是使用 `injectTo` 指定一个要注入语法的目标语言作用域列表。
>
> 在这个例子中，我们会创建一个简单的注入语法，把 JavaScript 注释中的 `TODO` 高亮为关键字。为了在 JavaScript 文件中应用我们的注入语法，我们在 `injectTo` 中使用 `source.js` 目标语言作用域：

```json
{
  "contributes": {
    "grammars": [
      {
        "path": "./syntaxes/injection.json",
        "scopeName": "todo-comment.injection",
        "injectTo": ["source.js"]
      }
    ]
  }
}
```

> 语法本身是一个标准的 TextMate 语法，唯一的区别是顶层的 `injectionSelector` 条目。`injectionSelector` 是一个作用域选择器，指定注入的语法应该在哪些作用域中应用。在我们的例子中，我们希望在所有 `//` 注释中高亮 `TODO` 这个词。使用[作用域检查器](#scope-inspector)，我们发现 JavaScript 的双斜杠注释的作用域是 `comment.line.double-slash`，所以我们的注入选择器是 `L:comment.line.double-slash`：

```json
{
  "scopeName": "todo-comment.injection",
  "injectionSelector": "L:comment.line.double-slash",
  "patterns": [
    {
      "include": "#todo-keyword"
    }
  ],
  "repository": {
    "todo-keyword": {
      "match": "TODO",
      "name": "keyword.todo"
    }
  }
}
```

> 注入选择器中的 `L:` 表示注入的规则被添加到已有语法规则的左边。这基本上意味着，我们注入的语法规则会在任何已有的语法规则之前被应用。

两层“定位”：

| 配置 | 作用 | 示例中的值 |
|---|---|---|
| `package.json` 中的 `injectTo` | 注入到**哪种语言**的语法中 | `source.js`（JavaScript） |
| 语法文件中的 `injectionSelector` | 在这种语言的**哪些作用域**中生效 | `comment.line.double-slash`（`//` 注释） |
| `L:` 前缀 | 优先级：比原有的规则先匹配（`R:` 则是后匹配） | 确保 `TODO` 先被识别出来 |

注意 `keyword.todo` 这个作用域，大多数颜色主题会把它当作 `keyword` 显示成关键字的颜色；如果想要更醒目的颜色，用户可以在设置的 `editor.tokenColorCustomizations` 中为 `keyword.todo` 单独设置（见 [颜色主题](../extension-guides/color-theme.md#syntax-colors)）。

<a id="embedded-languages"></a>
#### 嵌入式语言（Embedded languages）

> 注入语法也可以向它的父语法贡献嵌入式语言。和普通语法一样，注入语法可以使用 `embeddedLanguages`，把嵌入语言中的作用域映射到一个顶层语言作用域。
>
> 例如，一个高亮 JavaScript 字符串中 SQL 查询的扩展，可以使用 `embeddedLanguages`，确保字符串中所有标记为 `meta.embedded.inline.sql` 的标记，在括号匹配、代码片段选择等基本语言功能上都被当作 SQL 对待。

```json
{
  "contributes": {
    "grammars": [
      {
        "path": "./syntaxes/injection.json",
        "scopeName": "sql-string.injection",
        "injectTo": ["source.js"],
        "embeddedLanguages": {
          "meta.embedded.inline.sql": "sql"
        }
      }
    ]
  }
}
```

<a id="token-types-and-embedded-languages"></a>
#### 标记类型与嵌入式语言（Token types and embedded languages）

> 对于注入语言中的嵌入式语言，还有一个额外的复杂之处：默认情况下，VS Code 会把字符串中的所有标记当作字符串内容，把注释中的所有标记当作注释内容。由于括号匹配和自动闭合配对等功能在字符串和注释中是被禁用的，所以如果嵌入的语言出现在字符串或注释中，这些功能在嵌入的语言中也会被禁用。
>
> 要覆盖这个行为，你可以使用一个 `meta.embedded.*` 作用域，重置 VS Code 把标记标为字符串或注释内容的标记。最好始终把嵌入的语言包裹在一个 `meta.embedded.*` 作用域中，确保 VS Code 正确地对待嵌入的语言。
>
> 如果你无法为你的语法添加一个 `meta.embedded.*` 作用域，也可以在语法的贡献点中使用 `tokenTypes`，把特定的作用域映射到内容模式。下面的 `tokenTypes` 部分确保 `my.sql.template.string` 作用域中的所有内容都被当作源代码对待：

```json
{
  "contributes": {
    "grammars": [
      {
        "path": "./syntaxes/injection.json",
        "scopeName": "sql-string.injection",
        "injectTo": ["source.js"],
        "embeddedLanguages": {
          "my.sql.template.string": "sql"
        },
        "tokenTypes": {
          "my.sql.template.string": "other"
        }
      }
    ]
  }
}
```

**问题的来源：** 在 [语言配置](./language-configuration-guide.md#autoclosing) 中讲过，`notIn: ["string"]` 会让自动闭合在字符串中失效。SQL 写在 JavaScript 的字符串里，于是在 SQL 中输入 `(` 也不会自动补 `)` 了。

**两种解决方法：**

| 方法 | 做法 |
|---|---|
| 推荐 | 在注入语法中，把 SQL 部分的作用域命名为 `meta.embedded.*`（如 `meta.embedded.inline.sql`），VS Code 看到 `meta.embedded` 就会“重置”，不再把其中的内容当作字符串 |
| 备选 | 作用域名改不了时，用 `tokenTypes` 把这个作用域映射为 `"other"`（普通代码）；可选的值还有 `"string"`、`"comment"` |

---

<a id="theming"></a>
## 主题化（Theming）

> 主题化就是为标记分配颜色和样式。主题规则在颜色主题中指定，但用户可以在用户设置中定制主题规则。
>
> TextMate 主题规则定义在 `tokenColors` 中，语法与普通的 TextMate 主题相同。每条规则定义了一个 TextMate 作用域选择器，以及对应的颜色和样式。
>
> 在计算一个标记的颜色和样式时，会用当前标记的作用域去匹配规则的选择器，为每一个样式属性（前景色、粗体、斜体、下划线）找到最具体的那条规则。
>
> [颜色主题指南](../extension-guides/color-theme.md#syntax-colors)介绍了如何创建颜色主题。语义标记的主题化在[语义高亮指南](./semantic-highlight-guide.md#theming)中讲解。

“为每一个样式属性分别找最具体的规则”：比如主题中有两条规则，`keyword` 设置了颜色为紫色，`keyword.operator` 设置了斜体但没有设置颜色。那么 `+`（`keyword.operator.arithmetic.js`）最终是**紫色 + 斜体**：颜色来自 `keyword`，斜体来自 `keyword.operator`。

---

<a id="scope-inspector"></a>
## 作用域检查器（Scope inspector）

> VS Code 内置的作用域检查器工具，可以帮助调试语法和语义标记。它显示文件中当前位置的标记的作用域和语义标记，以及关于对这个标记应用了哪些主题规则的元数据。
>
> 在命令面板中通过 `Developer: Inspect Editor Tokens and Scopes` 命令触发作用域检查器，或者为它[创建一个快捷键](https://code.visualstudio.com/docs/getstarted/keybindings)：

```json
{
  "key": "cmd+alt+shift+i",
  "command": "editor.action.inspectTMScopes"
}
```

（这是 macOS 的写法，Windows / Linux 上把 `cmd` 换成 `ctrl`。这段配置写在用户的 `keybindings.json` 中。）

![作用域检查器](images/syntax-highlighting/scope-inspector.png)

> 作用域检查器显示以下信息：
>
> 1. 当前的标记。
> 2. 关于这个标记的元数据，以及关于它最终外观的信息。如果你在处理嵌入式语言，这里重要的条目是 `language` 和 `token type`。
> 3. 当当前语言有可用的语义标记提供者、并且当前主题支持语义高亮时，会显示语义标记部分。它显示当前语义标记的类型和修饰符，以及与这个语义标记类型和修饰符匹配的主题规则。
> 4. TextMate 部分显示当前 TextMate 标记的作用域列表，最具体的作用域在最上面。它还显示与这些作用域匹配的最具体的主题规则。这里只显示决定这个标记当前样式的主题规则，不显示被覆盖的规则。如果存在语义标记，只有当主题规则与匹配语义标记的规则不同时，才会显示主题规则。

| 编号 | 部分 | 用途 |
|---|---|---|
| 1 | 当前标记 | 确认光标所在的是哪一段文字 |
| 2 | 元数据（`language`、`token type`、前景色、背景色、对比度） | 调试嵌入式语言时，看 `language` 是不是嵌入的那门语言、`token type` 是不是 `Other`（而不是 `String`、`Comment`） |
| 3 | 语义标记 | 见 [语义高亮指南](./semantic-highlight-guide.md) |
| 4 | TextMate 作用域 | 写语法时最常看的部分：确认规则是否生效，作用域名是否正确 |

**开发语法时的工作流：** 按 `F5` 启动扩展开发宿主 → 打开一个测试文件 → 打开作用域检查器 → 把光标移到不同位置，检查作用域是否符合预期 → 修改语法文件 → 在扩展开发宿主中执行 **Developer: Reload Window** 重新加载。

---

## 本篇小结

```text
语法高亮 = 分词（语法文件：文字 → 作用域） + 主题化（颜色主题：作用域 → 颜色）

package.json：contributes.grammars（language、scopeName、path，
              可选 embeddedLanguages、tokenTypes、injectTo、balanced/unbalancedBracketScopes）

语法文件（.tmLanguage.json）
  scopeName、patterns（顶层规则）、repository（规则仓库，用 #名字 引用）
  规则：match + name（单段匹配）/ begin + end + patterns（区间匹配，可嵌套）
       beginCaptures / endCaptures 给起止符单独命名
  作用域：用常用的名称（keyword、string、comment、entity.name.function……）+ 语言后缀

扩展已有语法：注入语法（injectTo + injectionSelector，L: 表示优先）
嵌入式语言：embeddedLanguages 映射；放在字符串 / 注释中时用 meta.embedded.* 或 tokenTypes
复杂语法可以用 YAML 编写，再用 js-yaml 转成 JSON
调试：Developer: Inspect Editor Tokens and Scopes
```

[tm-grammars]: https://macromates.com/manual/en/language_grammars
