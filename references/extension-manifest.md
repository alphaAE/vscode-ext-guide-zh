# 扩展清单（Extension Manifest）

> 原文：[Extension Manifest](https://code.visualstudio.com/api/references/extension-manifest)
> 源文件：`microsoft/vscode-docs` → `api/references/extension-manifest.md`（DateApproved: 10/7/2026）

> 每个 Visual Studio Code 扩展都需要在扩展目录结构的根部有一个清单文件 `package.json`。

扩展的 `package.json` 就是 npm 的 `package.json`，只是多了一些 VS Code 专用的字段（`engines.vscode`、`contributes`、`activationEvents` 等）。

---

<a id="fields"></a>
## 字段（Fields）

| 名称 | 必填 | 类型 | 详细说明 |
| --- | :---: | --- | --- |
| `name` | Y | `string` | 扩展的名称，应该全部小写，不含空格。<br>名称在市场中必须是唯一的。 |
| `version` | Y | `string` | 兼容 [SemVer](https://semver.org/) 的版本号。 |
| `publisher` | Y | `string` | [发布者标识符](../working-with-extensions/publishing-extension.md#publishing-extensions) |
| `engines` | Y | `object` | 一个对象，至少包含 `vscode` 键，其值与扩展所[兼容](../working-with-extensions/publishing-extension.md#visual-studio-code-compatibility)的 VS Code 版本相匹配。不能是 `*`。例如：`^0.10.5` 表示兼容的最低 VS Code 版本为 `0.10.5`。 |
| `license` | | `string` | 参考 [npm 的文档](https://docs.npmjs.com/cli/v7/configuring-npm/package-json#license)。如果你在扩展的根目录中有一个 `LICENSE` 文件，`license` 的值应该是 `"SEE LICENSE IN <filename>"`。 |
| `displayName` | | `string` | 扩展在市场中使用的显示名称。<br>显示名称在市场中必须是唯一的。 |
| `description` | | `string` | 简短地描述你的扩展是什么、做什么。 |
| `categories` | | `string[]` | 你想为扩展使用的分类。允许的值：`[Programming Languages, Snippets, Linters, Themes, Debuggers, Formatters, Keymaps, SCM Providers, Other, Extension Packs, Language Packs, Data Science, Machine Learning, Visualization, Notebooks, Education, Testing]` |
| `keywords` | | `array` | 一个**关键词**数组，让扩展更容易被找到。它们会和其他的扩展**标签（Tags）**一起显示在市场中。这个列表目前最多 30 个关键词。 |
| `galleryBanner` | | `object` | 帮助调整市场页面头部的格式，以搭配你的图标。详见下文。 |
| `preview` | | `boolean` | 把扩展标记为市场中的预览（Preview）版。 |
| `main` | | `string` | 扩展的入口。 |
| `browser` | | `string` | 你的 [Web 扩展](../extension-guides/web-extensions.md)的入口。 |
| [`contributes`](./contribution-points.md) | | `object` | 一个描述扩展的[贡献](./contribution-points.md)的对象。 |
| [`activationEvents`](./activation-events.md) | | `array` | 这个扩展的[激活事件](./activation-events.md)的数组。 |
| `badges` | | `array` | 显示在市场扩展页面侧边栏中的[经过批准的](#approved-badges)徽章数组。每个徽章是一个对象，包含 3 个属性：`url` 是徽章图片的 URL，`href` 是用户点击徽章时会打开的链接，以及 `description`。 |
| `markdown` | | `string` | 控制市场中使用的 Markdown 渲染引擎。`github`（默认）或 `standard`。 |
| `qna` | | `marketplace`（默认）、`string`、`false` | 控制市场中的**问与答（Q & A）**链接。设为 `marketplace` 启用默认的市场问答网站。设为一个字符串，提供自定义问答网站的 URL。设为 `false` 完全禁用问答。 |
| `sponsor` | | `object` | 指定用户可以赞助你的扩展的位置。这是一个只有一个属性 `url` 的对象，链接到用户可以赞助你的扩展的页面。 |
| `dependencies` | | `object` | 扩展需要的所有运行时 Node.js 依赖。与 [npm 的 `dependencies`](https://docs.npmjs.com/cli/v7/configuring-npm/package-json#dependencies) 完全相同。 |
| `devDependencies` | | `object` | 扩展需要的所有开发时 Node.js 依赖。与 [npm 的 `devDependencies`](https://docs.npmjs.com/cli/v7/configuring-npm/package-json#devdependencies) 完全相同。 |
| `extensionPack` | | `array` | 一个可以一起安装的扩展的 ID 数组。扩展的 ID 总是 `${publisher}.${name}`。例如：`vscode.csharp`。 |
| `extensionDependencies` | | `array` | 这个扩展所依赖的扩展的 ID 数组。扩展的 ID 总是 `${publisher}.${name}`。例如：`vscode.csharp`。 |
| `extensionKind` | | `array` | 一个数组，指出在远程配置中扩展应该在哪里运行。值为 `ui`（在本地运行）、`workspace`（在远程机器上运行），或者两者都有，顺序表示偏好。例如：`[ui, workspace]` 表示扩展可以在任一位置运行，但更喜欢在本地机器上运行。详见[这里](../advanced-topics/extension-host.md#preferred-extension-location)。 |
| `scripts` | | `object` | 与 [npm 的 `scripts`](https://docs.npmjs.com/misc/scripts) 完全相同，但有额外的 VS Code 专用字段，例如 [vscode:prepublish](../working-with-extensions/publishing-extension.md#pre-publish-step) 或 [vscode:uninstall](#extension-uninstall-hook)。 |
| `icon` | | `string` | 图标的路径，至少 128x128 像素（Retina 屏幕为 256x256）。 |
| `pricing` | | `string` | 扩展的定价信息。允许的值：`Free`、`Trial`。默认值：`Free`。详见[这里](../working-with-extensions/publishing-extension.md#extension-pricing-label)。 |
| `capabilities` | | `object` | 一个描述扩展在受限工作区中的能力的对象：[`untrustedWorkspaces`](../extension-guides/workspace-trust.md#static-declarations)、[`virtualWorkspaces`](../extension-guides/virtual-workspaces.md#signal-whether-your-extension-can-handle-virtual-workspaces)。 |

> 另请查看 [npm 的 `package.json` 参考](https://docs.npmjs.com/cli/v7/configuring-npm/package-json)。

（`vscode:prepublish` 的链接在原文中指向 `#prepublish-step`，但目标小节的标题是 “Pre-publish step”，这里改为正确的 `#pre-publish-step`。）

**按用途对这些字段分组：**

| 用途 | 字段 |
|---|---|
| 身份（必填） | `name`、`version`、`publisher`、`engines` |
| 运行 | `main`（桌面版入口）、`browser`（Web 版入口）、`activationEvents`、`contributes`、`extensionKind`、`capabilities`、`extensionDependencies` |
| 市场展示 | `displayName`、`description`、`icon`、`galleryBanner`、`categories`、`keywords`、`badges`、`preview`、`pricing`、`sponsor`、`qna`、`markdown`，以及 npm 的 `license`、`repository`、`bugs`、`homepage` |
| 构建 | `scripts`（含 `vscode:prepublish`、`vscode:uninstall`）、`dependencies`、`devDependencies` |
| 组合 | `extensionPack` |

**几个容易混淆的字段：**

- **`name` 与 `displayName`**：`name` 是机器用的（小写、无空格，参与组成扩展 ID `publisher.name`，发布后不能改）；`displayName` 是给人看的名称，可以有大写、空格、中文。两者在市场中都必须唯一。
- **`main` 与 `browser`**：桌面版 VS Code 加载 `main`，浏览器中的 VS Code 加载 `browser`。只有 `main` 的扩展不能在 vscode.dev 中运行（见 [Web 扩展](../extension-guides/web-extensions.md)）。
- **`extensionPack` 与 `extensionDependencies`**：前者是“推荐一起安装”，被打包的扩展可以单独卸载或禁用；后者是“必须依赖”，VS Code 会先安装并激活被依赖的扩展，被依赖的扩展不能单独卸载。详见下文的 [扩展包](#extension-packs)。
- **`preview: true`**：在市场中显示 “Preview” 标记，表示还不稳定。这和 [预发布版本](../working-with-extensions/publishing-extension.md#pre-release-extensions)（`--pre-release`）是两回事。

---

<a id="example"></a>
## 示例（Example）

> 下面是一个完整的 `package.json`

```json
{
  "name": "wordcount",
  "displayName": "Word Count",
  "version": "0.1.0",
  "publisher": "ms-vscode",
  "description": "Markdown Word Count Example - reports out the number of words in a Markdown file.",
  "author": {
    "name": "sean"
  },
  "categories": ["Other"],
  "icon": "images/icon.png",
  "galleryBanner": {
    "color": "#C80000",
    "theme": "dark"
  },
  "pricing": "Free",
  "activationEvents": ["onLanguage:markdown"],
  "engines": {
    "vscode": "^1.0.0"
  },
  "main": "./out/extension",
  "scripts": {
    "vscode:prepublish": "node ./node_modules/vscode/bin/compile",
    "compile": "node ./node_modules/vscode/bin/compile -watch -p ./"
  },
  "devDependencies": {
    "@types/vscode": "^0.10.x",
    "typescript": "^1.6.2"
  },
  "license": "SEE LICENSE IN LICENSE.txt",
  "bugs": {
    "url": "https://github.com/microsoft/vscode-wordcount/issues",
    "email": "sean@contoso.com"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/microsoft/vscode-wordcount.git"
  },
  "homepage": "https://github.com/microsoft/vscode-wordcount/blob/main/README.md"
}
```

**这个示例非常老旧**，其中 `scripts` 使用的 `node_modules/vscode/bin/compile` 来自早已废弃的 `vscode` npm 包，`@types/vscode` 和 `typescript` 的版本也不存在或过时，不要照抄。下面是一个与现在 `yo code` 生成的项目相近的写法（补充示例，版本号按实际情况填写）：

```json
{
  "name": "wordcount",
  "displayName": "Word Count",
  "description": "Markdown Word Count Example - reports out the number of words in a Markdown file.",
  "version": "0.1.0",
  "publisher": "your-publisher-id",
  "engines": { "vscode": "^1.100.0" },
  "categories": ["Other"],
  "icon": "images/icon.png",
  "activationEvents": ["onLanguage:markdown"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [{ "command": "wordcount.count", "title": "Count Words" }]
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "pretest": "npm run compile",
    "test": "vscode-test"
  },
  "devDependencies": {
    "@types/vscode": "^1.100.0",
    "@types/node": "20.x",
    "@vscode/test-cli": "^0.0.10",
    "@vscode/test-electron": "^2.4.0",
    "typescript": "^5.4.0"
  },
  "license": "MIT",
  "repository": { "type": "git", "url": "https://github.com/your-name/wordcount.git" }
}
```

注意 `@types/vscode` 的版本不能高于 `engines.vscode`（见 [发布扩展](../working-with-extensions/publishing-extension.md#visual-studio-code-compatibility)）。

---

<a id="marketplace-presentation-tips"></a>
## 市场展示技巧（Marketplace Presentation Tips）

> 下面是一些让你的扩展在 [VS Code 市场](https://marketplace.visualstudio.com/VSCode)中显示得更好看的技巧和建议。
>
> 始终使用最新的 `vsce`，可以运行 `npm install -g @vscode/vsce` 来确保这一点。
>
> 在扩展的根文件夹中放一个 `README.md` Markdown 文件，我们会把它的内容放在（市场上）扩展详情的正文中。你可以在 `README.md` 中使用相对路径的图片链接。
>
> 下面是一些例子：
>
> 1. [Word Count](https://marketplace.visualstudio.com/items?itemName=ms-vscode.wordcount)
> 2. [MD Tools](https://marketplace.visualstudio.com/items/seanmcbreen.MDTools)
>
> 提供一个好的显示名称和描述。这对市场和产品内的显示都很重要。这些字符串也用于 VS Code 中的文本搜索，包含相关的关键词会很有帮助。

```json
    "displayName": "Word Count",
    "description": "Markdown Word Count Example - reports out the number of words in a Markdown file.",
```

（README 中的相对路径图片，需要 `package.json` 中有指向公开仓库的 `repository` 字段，`vsce` 才能把它们转换成绝对地址，见 [发布扩展](../working-with-extensions/publishing-extension.md#marketplace-integration)。）

> 图标和一个对比鲜明的横幅颜色，在市场页面的头部看起来会很棒。`theme` 属性指的是横幅中使用的字体颜色，`dark` 或 `light`。

```json
{
  "icon": "images/icon.png",
  "galleryBanner": {
    "color": "#C80000",
    "theme": "dark"
  }
}
```

（`theme: "dark"` 表示横幅背景是深色的，所以文字用浅色；`light` 则相反。）

> 你可以设置几个可选的链接（`bugs`、`homepage`、`repository`），它们会显示在市场的 **Resources**（资源）部分下。

```json
{
  "license": "SEE LICENSE IN LICENSE.txt",
  "homepage": "https://github.com/microsoft/vscode-wordcount/blob/main/README.md",
  "bugs": {
    "url": "https://github.com/microsoft/vscode-wordcount/issues",
    "email": "sean@contoso.com"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/microsoft/vscode-wordcount.git"
  }
}
```

| 市场资源链接 | package.json 属性 |
| --- | --- |
| Issues（问题） | `bugs:url` |
| Repository（仓库） | `repository:url` |
| Homepage（主页） | `homepage` |
| License（许可证） | `license` |

> 为你的扩展设置一个 `category`（分类）。同一 `category` 中的扩展会在市场上归为一组，这能改善过滤和发现。

> **注意**：只使用对你的扩展有意义的值。允许的值是 `[Programming Languages, Snippets, Linters, Themes, Debuggers, Formatters, Keymaps, SCM Providers, Other, Extension Packs, Language Packs, Data Science, Machine Learning, Visualization, Notebooks, Education, Testing]`。对于语法高亮和代码补全这样的通用语言功能，使用 `Programming Languages`。`Language Packs` 分类保留给显示语言扩展（例如，保加利亚语本地化）。

```json
{
  "categories": ["Linters", "Programming Languages", "Other"]
}
```

各分类的含义：

| 分类 | 含义 |
|---|---|
| `Programming Languages` | 编程语言支持（语法高亮、补全等） |
| `Snippets` | 代码片段 |
| `Linters` | 代码检查 |
| `Themes` | 主题（颜色主题、图标主题） |
| `Debuggers` | 调试器 |
| `Formatters` | 格式化工具 |
| `Keymaps` | 快捷键映射（如模拟其他编辑器的快捷键） |
| `SCM Providers` | 源代码管理提供者 |
| `Other` | 其他 |
| `Extension Packs` | 扩展包 |
| `Language Packs` | 界面语言包（如中文语言包），保留给本地化扩展 |
| `Data Science` / `Machine Learning` / `Visualization` / `Notebooks` | 数据科学 / 机器学习 / 可视化 / 笔记本 |
| `Education` | 教育 |
| `Testing` | 测试 |

分类的值区分大小写，必须完全照写。

<a id="approved-badges"></a>
### 经过批准的徽章（Approved Badges）

> 出于安全考虑，我们只允许来自可信服务的徽章。
>
> 我们允许来自以下 URL 前缀的徽章：
>
> - api.travis-ci.com
> - app.fossa.io
> - badge.buildkite.com
> - badge.fury.io
> - badgen.net
> - badges.frapsoft.com
> - badges.gitter.im
> - cdn.travis-ci.com
> - ci.appveyor.com
> - circleci.com
> - cla.opensource.microsoft.com
> - codacy.com
> - codeclimate.com
> - codecov.io
> - coveralls.io
> - david-dm.org
> - deepscan.io
> - dev.azure.com
> - docs.rs
> - flat.badgen.net
> - github.com（仅限 Workflows）
> - gitlab.com
> - godoc.org
> - goreportcard.com
> - img.shields.io
> - isitmaintained.com
> - marketplace.visualstudio.com
> - nodesecurity.io
> - opencollective.com
> - snyk.io
> - travis-ci.com
> - visualstudio.com
> - vsmarketplacebadges.dev
>
> 注意：请把 vsmarketplacebadge.apphb.com 的徽章替换为 vsmarketplacebadges.dev 的徽章。
>
> 如果你还想使用其他徽章，请提交一个 GitHub [issue](https://github.com/microsoft/vscode/issues)，我们很乐意看看。

这份列表同时适用于 `package.json` 的 `badges` 字段，以及 `README.md` / `CHANGELOG.md` 中的 SVG 图片：来自这些域名的 SVG 徽章可以使用，其他来源的 SVG 会导致 `vsce` 拒绝打包（见 [发布扩展](../working-with-extensions/publishing-extension.md#publishing-extensions)）。“github.com（仅限 Workflows）”指的是 GitHub Actions 工作流的状态徽章。

---

<a id="combining-extension-contributions"></a>
## 组合扩展的贡献（Combining Extension Contributions）

> `yo code` 生成器让你可以轻松地打包 TextMate 主题、着色器和代码片段，并创建新的扩展。运行生成器时，它会为每个选项创建一个完整的、独立的扩展包。但是，把多种贡献组合到一个扩展中，往往会更方便。例如，如果你正在为一门新语言添加支持，你会希望同时为用户提供带有着色的语言定义、代码片段，甚至可能还有调试支持。
>
> 要组合扩展的贡献，编辑一个现有的扩展清单 `package.json`，添加新的贡献和相关的文件。
>
> 下面是一个扩展清单，它包含了一个 LaTex 语言定义（语言标识符和文件扩展名）、着色（`grammars`）和代码片段。

```json
{
  "name": "language-latex",
  "description": "LaTex Language Support",
  "version": "0.0.1",
  "publisher": "someone",
  "engines": {
    "vscode": "0.10.x"
  },
  "categories": ["Programming Languages", "Snippets"],
  "contributes": {
    "languages": [
      {
        "id": "latex",
        "aliases": ["LaTeX", "latex"],
        "extensions": [".tex"]
      }
    ],
    "grammars": [
      {
        "language": "latex",
        "scopeName": "text.tex.latex",
        "path": "./syntaxes/latex.tmLanguage.json"
      }
    ],
    "snippets": [
      {
        "language": "latex",
        "path": "./snippets/snippets.json"
      }
    ]
  }
}
```

> 注意，扩展清单的 `categories` 属性现在同时包含 `Programming Languages` 和 `Snippets`，便于在市场上发现和过滤。

> **提示**：确保你合并的贡献使用相同的标识符。在上面的例子中，三个贡献都使用 "latex" 作为语言标识符。这让 VS Code 知道着色器（`grammars`）和代码片段是针对 LaTeX 语言的，会在编辑 LaTeX 文件时生效。

三个贡献分别在 [语法高亮](../language-extensions/syntax-highlight-guide.md)、[代码片段](../language-extensions/snippet-guide.md)、[语言配置](../language-extensions/language-configuration-guide.md) 中介绍过。（`"vscode": "0.10.x"` 同样是很早期的写法，实际中写 `^1.xx.0`。）

---

<a id="extension-packs"></a>
## 扩展包（Extension Packs）

> 你可以把多个独立的扩展捆绑在一起，形成**扩展包（Extension Packs）**。扩展包是一组会被一起安装的扩展。这样可以轻松地与其他用户分享你喜欢的扩展，或者为特定的场景创建一组扩展，比如 PHP 开发，帮助 PHP 开发者快速上手 VS Code。
>
> 扩展包通过 `package.json` 文件中的 `extensionPack` 属性来捆绑其他扩展。
>
> 例如，下面是一个 PHP 扩展包，它包含一个调试器和一个语言服务：

```json
{
  "extensionPack": [
    "xdebug.php-debug",
    "zobo.php-intellisense"
  ]
}
```

> 安装扩展包时，VS Code 现在也会安装它的扩展依赖。
>
> 扩展包应该归入市场中的 `Extension Packs` 分类：

```json
{
  "categories": ["Extension Packs"]
}
```

> 要创建一个扩展包，你可以使用 `yo code` Yeoman 生成器，选择 **New Extension Pack** 选项。有一个选项可以用你当前 VS Code 实例中已安装的扩展来初始化这个扩展包。这样，你就可以轻松地用你喜欢的扩展创建一个扩展包，把它发布到市场上，与他人分享。
>
> 扩展包不应该与它捆绑的扩展存在任何功能上的依赖，被捆绑的扩展应该可以独立于扩展包进行管理。如果一个扩展依赖于另一个扩展，这种依赖应该用 `extensionDependencies` 属性声明。

| | `extensionPack` | `extensionDependencies` |
|---|---|---|
| 关系 | “这些扩展常常一起用” | “没有它，我就无法工作” |
| 安装 | 安装扩展包时一起安装 | 安装本扩展时一起安装 |
| 卸载 / 禁用 | 被捆绑的扩展可以单独卸载或禁用 | 被依赖的扩展不能单独卸载（要先卸载依赖它的扩展） |
| 激活 | 无影响 | 激活本扩展前，先激活被依赖的扩展 |
| 典型用途 | “PHP 开发套装”、“前端开发套装” | 你的扩展调用了另一个扩展导出的 API（`vscode.extensions.getExtension(id).exports`） |

一个扩展包也可以同时是一个普通扩展（既有 `extensionPack`，又有自己的 `main` 和 `contributes`）。

---

<a id="extension-uninstall-hook"></a>
## 扩展卸载钩子（Extension uninstall hook）

> 如果你的扩展在从 VS Code 中卸载时需要做一些清理，你可以在扩展 package.json 的 `scripts` 部分下，向卸载钩子 `vscode:uninstall` 注册一个 `node` 脚本。

```json
{
  "scripts": {
    "vscode:uninstall": "node ./out/src/lifecycle"
  }
}
```

> 这个脚本在扩展从 VS Code 中被完全卸载时执行，也就是在扩展被卸载后 VS Code 重启（关闭再启动）时。

> **注意**：只支持 Node.js 脚本。

这个脚本运行在一个单独的 Node.js 进程中，**不能**使用 `vscode` API，适合做删除扩展自己创建的临时文件、缓存目录之类的事情。注意它只在扩展被真正卸载（而不是禁用或更新）、并且 VS Code 重启之后才运行，所以不要用它做“用户卸载时立即需要发生”的事情。

---

<a id="useful-node-modules"></a>
## 有用的 Node 模块（Useful Node modules）

> npmjs 上有几个 Node.js 模块，可以帮助编写 VS Code 扩展。你可以把它们包含在扩展的 `dependencies` 部分中。
>
> - [vscode-nls](https://www.npmjs.com/package/vscode-nls) - 支持外部化和本地化。
> - [vscode-uri](https://www.npmjs.com/package/vscode-uri) - VS Code 及其扩展所使用的 URI 实现。
> - [jsonc-parser](https://www.npmjs.com/package/jsonc-parser) - 一个扫描器和容错的解析器，用于处理带注释或不带注释的 JSON。
> - [request-light](https://www.npmjs.com/package/request-light) - 一个轻量级的、支持代理的 Node.js 请求库
> - [vscode-extension-telemetry](https://www.npmjs.com/package/@vscode/extension-telemetry) - 为 VS Code 扩展提供一致的遥测报告。
> - [vscode-languageclient](https://www.npmjs.com/package/vscode-languageclient) - 轻松集成遵循[语言服务器协议](https://microsoft.github.io/language-server-protocol)的语言服务器。

补充说明：

- **本地化：** `vscode-nls` 是旧的方案。现在推荐使用 VS Code 内置的 `vscode.l10n` API（代码中用 `vscode.l10n.t('...')`）配合 `@vscode/l10n-dev` 工具提取字符串；`package.json` 中的文字用 `package.nls.json` / `package.nls.zh-cn.json` 本地化。
- **遥测：** 包名现在是 `@vscode/extension-telemetry`，使用方法见 [遥测](../extension-guides/telemetry.md)。
- `vscode-uri` 和 `jsonc-parser` 在语言服务器中尤其有用：语言服务器不能使用 `vscode` API 中的 `Uri`，用 `vscode-uri` 可以得到相同的行为。

---

<a id="next-steps"></a>
## 下一步（Next steps）

> 要进一步了解 VS Code 的扩展模型，可以试试这些主题：
>
> - [贡献点](./contribution-points.md) - VS Code 贡献点参考
> - [激活事件](./activation-events.md) - VS Code 激活事件参考
> - [扩展市场](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace) - 进一步了解 VS Code 扩展市场

---

## 本篇小结

```text
package.json = npm 清单 + VS Code 专用字段

必填：name（小写、唯一）、version（SemVer）、publisher、engines.vscode（如 ^1.100.0，不能是 *）
运行：main / browser、activationEvents、contributes、extensionKind、capabilities、extensionDependencies
市场：displayName、description、icon（PNG ≥128px）、galleryBanner、categories（固定取值）、
     keywords（≤30）、badges（只允许可信来源）、repository / bugs / homepage / license、pricing、sponsor
构建：scripts（vscode:prepublish 打包前、vscode:uninstall 卸载后重启时）

扩展 ID = publisher.name
extensionPack（推荐一起装，可独立管理）vs extensionDependencies（硬依赖，先激活）
多种贡献（语言 + 语法 + 代码片段）可以放在同一个扩展中，用相同的语言 ID 关联
```
