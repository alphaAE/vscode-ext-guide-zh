# 使用提议的 API（Using Proposed API）

> 原文：[Using Proposed API](https://code.visualstudio.com/api/advanced-topics/using-proposed-api)
> 源文件：`microsoft/vscode-docs` → `api/advanced-topics/using-proposed-api.md`（DateApproved: 10/7/2026）

> 在 Visual Studio Code，我们非常重视扩展 API 的兼容性。我们尽最大努力避免破坏性的 API 变更，扩展作者可以期待已发布的扩展继续正常工作。然而，这给我们带来了很大的限制：一旦我们引入了一个 API，就很难再修改它了。
>
> 提议的 API（Proposed APIs）为我们解决了这个问题。提议的 API 是一组不稳定的 API，它们已经在 VS Code 中实现，但没有像稳定 API 那样向公众公开。它们**可能会改变**、**只在 Insiders 发行版中可用**，并且**不应该在已发布的扩展中使用**。尽管如此，扩展作者可以在本地开发中测试这些新的 API，并向 VS Code 团队提供反馈，帮助迭代一个 API。最终，提议的 API 会进入稳定 API，对所有扩展可用。

**在本指南中你多次遇到过它：** 比如 [笔记本](../extension-guides/notebook.md) 中的部分渲染器通信 API、[内联补全](../language-extensions/programmatic-language-features.md#show-inline-completions) 示例中的 `commands` 字段，在 `@types/vscode` 中都找不到，就是因为它们还是提议的 API。判断方法：一个 API 如果在 `@types/vscode`（即 `vscode.d.ts`）中没有，而在 `vscode` 仓库的 `src/vscode-dts/vscode.proposed.*.d.ts` 中有，它就是提议的 API。

| | 稳定 API | 提议的 API |
|---|---|---|
| 类型声明 | `@types/vscode` | `vscode.proposed.<名称>.d.ts`（需要单独下载） |
| 可用的 VS Code | 稳定版和 Insiders | 只有 Insiders（以及开发模式下） |
| 是否会改变 | 保证兼容 | 随时可能改变或删除 |
| 能否发布到市场 | 能 | **不能** |

---

<a id="using-a-proposed-api"></a>
## 使用提议的 API（Using a proposed API）

> 在本地扩展开发中测试一个提议的 API 的步骤如下：
>
> - 使用 VS Code 的 [Insiders](https://code.visualstudio.com/insiders) 版本。
> - 在你的 `package.json` 中添加 `"enabledApiProposals": ["<proposalName>"]`。
> - 把对应的 [vscode.proposed.\<proposalName\>.d.ts](https://github.com/microsoft/vscode/blob/main/src/vscode-dts) 文件复制到你项目的源代码位置中。
>
> [@vscode/dts](https://github.com/microsoft/vscode-dts) 命令行工具可以让你快速下载最新的 `vscode.proposed.<proposalName>.d.ts`，用于扩展开发。它会按照你的 `package.json` 文件中列出的提议，下载对应的定义文件。

```bash
> npx @vscode/dts dev
Downloading vscode.proposed.languageStatus.d.ts
To:   /Users/Me/Code/MyExtension/vscode.proposed.languageStatus.d.ts
From: https://raw.githubusercontent.com/microsoft/vscode/main/src/vscode-dts/vscode.proposed.languageStatus.d.ts
Read more about proposed API at: https://code.visualstudio.com/api/advanced-topics/using-proposed-api
```

> 这里有一个使用提议 API 的示例：[proposed-api-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/proposed-api-sample)。

完整的配置（以示例输出中的 `languageStatus` 为例，它当时还是提议的 API，现在已经稳定）：

```json
{
  "engines": { "vscode": "^1.xx.0" },
  "enabledApiProposals": ["languageStatus"]
}
```

```text
项目根目录/
├── package.json
├── vscode.proposed.languageStatus.d.ts   ← npx @vscode/dts dev 下载到这里
└── src/extension.ts                       ← 直接使用 vscode.languages.createLanguageStatusItem(...)
```

下载的 `.d.ts` 文件中的声明会合并到 `vscode` 模块中，所以代码里照常 `import * as vscode from 'vscode'` 即可。要确保这个文件在 `tsconfig.json` 的编译范围内（`include`）。`<proposalName>` 就是文件名中 `vscode.proposed.` 和 `.d.ts` 之间的那部分。

---

<a id="proposed-api-incompatibility"></a>
## 提议 API 的不兼容问题（Proposed API incompatibility）

> 在 main 分支上，`vscode.proposed.<proposalName>.d.ts` 总是与 `vscode.d.ts` 兼容。然而，当你把 `vscode.proposed.<proposal>.d.ts` 添加到一个使用 `@types/vscode` 的项目中时，最新的 `vscode.proposed.<proposal>.d.ts` 可能与 `@types/vscode` 中的版本不兼容。
>
> 你可以通过以下任一方式解决这个问题：
>
> - 删除对 `@types/vscode` 的依赖，并使用 `npx @vscode/dts main` 从 `microsoft/vscode` 的 main 分支下载 `vscode.d.ts`。
> - 使用 `@types/vscode@<version>`，同时使用 `npx @vscode/dts dev <version>` 从 `microsoft/vscode` 的一个旧分支下载 `vscode.proposed.<proposal>.d.ts`。不过要小心，因为这个 API 在最新版本的 VS Code Insiders 中可能已经改变了。

**为什么会不兼容：** `@types/vscode` 是某个已发布的稳定版的类型（比如 1.140），而 `dev` 下载的提议 API 文件来自 main 分支（比 1.140 新），它可能引用了 1.140 中还不存在的类型。两种解决办法的取舍：

| 方法 | 稳定 API 的类型 | 提议 API 的类型 | 风险 |
|---|---|---|---|
| `npx @vscode/dts main` | main 分支（最新） | main 分支（最新） | 可能用到稳定版中还没有的稳定 API |
| `@types/vscode@<版本>` + `npx @vscode/dts dev <版本>` | 指定版本 | 指定版本对应的分支 | 提议 API 在最新的 Insiders 中可能已经变了 |

---

<a id="sharing-extensions-using-the-proposed-api"></a>
## 分享使用提议 API 的扩展（Sharing extensions using the proposed API）

> 虽然你不应该把使用提议 API 的扩展发布到市场上，但你仍然可以通过打包和分享扩展，与你的同伴分享它。
>
> 要打包你的扩展，可以运行 `vsce package`，为你的扩展创建一个 VSIX 文件。然后你可以把这个 VSIX 文件分享给其他人，让他们在自己的 VS Code 中安装这个扩展。
>
> 要从 VSIX 文件安装一个扩展，你需要进入扩展视图，选择 **...** 省略号按钮 **View and More Actions**（视图和更多操作），然后选择 **Install from VSIX**（从 VSIX 安装）。
>
> 选择 **Install from VSIX** 菜单项的过程如下面的短视频所示。

![演示用户进入扩展视图找到“从 VSIX 安装”菜单项](images/proposed-api/install-from-vsix.gif)

> 对于使用提议 API 的扩展，还需要几个额外的步骤来启用你的扩展。从你的 VSIX 安装之后，你需要退出 VS Code Insiders，然后在你的项目文件夹中，从命令行用 `code-insiders . --enable-proposed-api=<YOUR-EXTENSION-ID>` 重新启动它。
>
> 如果你想设置成每次启动 VS Code Insiders 时，你那个使用提议 API 的扩展都可以使用，可以运行 **Preferences: Configure Runtime Arguments**（首选项：配置运行时参数）命令，编辑 `.vscode-insiders/argv.json` 文件，设置一个启用的扩展列表。

```json
{
    ...
    "enable-proposed-api": ["<YOUR-EXTENSION-ID>"]
}
```

（`<YOUR-EXTENSION-ID>` 是 `发布者.扩展名` 形式的扩展 ID。`vsce package` 打包使用提议 API 的扩展时会给出警告或报错，需要按提示确认。在扩展开发宿主（`F5`）中调试时，提议的 API 会自动对正在开发的扩展启用，不需要这些额外步骤。）

**什么时候值得用提议的 API？** 只用于试验和给 VS Code 团队提供反馈。如果你的扩展要发布，就只能使用稳定 API，等提议的 API 稳定之后再采用。可以在 VS Code 每月的[更新说明](https://code.visualstudio.com/updates)中关注哪些提议的 API 已经稳定了。

---

## 本篇小结

```text
提议的 API：已实现但不稳定，可能改变，只在 Insiders 中可用，不能发布到市场

使用步骤
  1. 使用 VS Code Insiders
  2. package.json："enabledApiProposals": ["<提议名>"]
  3. npx @vscode/dts dev 下载 vscode.proposed.<提议名>.d.ts 到项目中
与 @types/vscode 不兼容时：npx @vscode/dts main，或固定版本 @types/vscode@x + npx @vscode/dts dev x

分享：vsce package → 对方 Install from VSIX → code-insiders --enable-proposed-api=<扩展ID>
  或在 argv.json（Preferences: Configure Runtime Arguments）中设置 "enable-proposed-api"
```
