# 扩展 API（Extension API）

> 原文：[Extension API](https://code.visualstudio.com/api)
> 源文件：`microsoft/vscode-docs` → `api/index.md`（DateApproved: 10/7/2026）

> VS Code 在设计时就充分考虑了可扩展性。从用户界面到编辑体验，VS Code 的几乎每一个部分都可以通过扩展 API 进行定制和增强。事实上，VS Code 的很多核心功能本身就是以[扩展](https://github.com/microsoft/vscode/tree/main/extensions)的形式构建的，并且使用的是同一套扩展 API。

这是官方扩展文档的首页，也是本指南的入口。前面的章节中我们已经多次看到这一点：Git、Markdown 预览、npm 脚本、各种主题，都是 VS Code 自带的扩展，用的就是你学到的这些 API。

> 本文档介绍了：
>
> - 如何构建、运行、调试、测试和发布扩展
> - 如何利用 VS Code 丰富的扩展 API
> - 在哪里可以找到帮助你上手的[指南](./extension-guides/overview.md)和[代码示例](https://github.com/microsoft/vscode-extension-samples)
> - 遵循我们的 [UX 指南](./ux-guidelines/overview.md)，了解最佳实践
>
> 代码示例可以在 [Microsoft/vscode-extension-samples](https://github.com/microsoft/vscode-extension-samples) 中找到。
>
> 如果你在寻找已发布的扩展，请前往 [VS Code 扩展市场](https://marketplace.visualstudio.com/vscode)。

---

<a id="what-can-extensions-do"></a>
## 扩展能做什么？（What can extensions do?）

> 下面是使用扩展 API 可以实现的一些例子：
>
> - 用颜色主题或文件图标主题改变 VS Code 的外观：[主题](./extension-capabilities/theming.md)
> - 在界面中添加自定义的组件和视图：[扩展工作台](./extension-capabilities/extending-workbench.md)
> - 创建一个 Webview，显示用 HTML/CSS/JS 构建的自定义网页：[Webview 指南](./extension-guides/webview.md)
> - 支持一门新的编程语言：[语言扩展概览](./language-extensions/overview.md)
> - 支持调试某个特定的运行时：[调试器扩展指南](./extension-guides/debugger-extension.md)
>
> 如果你想更全面地了解扩展 API，请参阅[扩展能力概览](./extension-capabilities/overview.md)页面。[扩展指南概览](./extension-guides/overview.md)也列出了一系列演示各种扩展 API 用法的代码示例和指南。

---

<a id="how-to-build-extensions"></a>
## 如何构建扩展？（How to build extensions?）

> 构建一个好的扩展可能需要花费大量的时间和精力。下面是 API 文档的各个部分能为你提供的帮助：

| 部分 | 内容 | 本指南中的入口 |
|---|---|---|
| **入门**（Get Started） | 通过 [Hello World](https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-sample) 示例，教你构建扩展的基本概念。 | [你的第一个扩展](./get-started/your-first-extension.md) |
| **扩展能力**（Extension Capabilities） | 把 VS Code 庞大的 API 拆分成几个较小的类别，并指引你去看更详细的主题。 | [扩展能力概览](./extension-capabilities/overview.md) |
| **扩展指南**（Extension Guides） | 包含讲解 VS Code 扩展 API 具体用法的指南和代码示例。 | [扩展指南](./extension-guides/overview.md) |
| **UX 指南**（UX Guidelines） | 展示在扩展中提供出色用户体验的最佳实践。 | [UX 指南](./ux-guidelines/overview.md) |
| **语言扩展**（Language Extensions） | 通过指南和代码示例，说明如何为一门编程语言添加支持。 | [语言扩展概览](./language-extensions/overview.md) |
| **测试与发布**（Testing and Publishing） | 包含关于各种扩展开发主题的深入指南，比如[测试](./working-with-extensions/testing-extension.md)和[发布](./working-with-extensions/publishing-extension.md)扩展。 | [发布扩展](./working-with-extensions/publishing-extension.md) |
| **高级主题**（Advanced Topics） | 解释一些高级概念，比如[扩展宿主](./advanced-topics/extension-host.md)、[支持远程开发和 GitHub Codespaces](./advanced-topics/remote-extensions.md)，以及[提议 API](./advanced-topics/using-proposed-api.md)。 | [扩展宿主](./advanced-topics/extension-host.md) |
| **参考**（References） | 包含 [VS Code API](https://code.visualstudio.com/api/references/vscode-api)、[贡献点](./references/contribution-points.md)以及许多其他主题的详尽参考。 | [贡献点](./references/contribution-points.md) |

推荐的学习路线见 [总结](./get-started/wrapping-up.md) 末尾的小结，完整的目录见 [README](./README.md)。

---

<a id="whats-new"></a>
## 有什么新内容？（What's new?）

> VS Code 每周更新一次，扩展 API 也是如此。每周都会有新的功能和 API 推出，不断提升 VS Code 扩展的能力和范围。
>
> 要及时了解扩展 API 的变化，可以查看每周的发布说明，其中有专门介绍扩展开发和提议 API 的章节。

发布说明在 [code.visualstudio.com/updates](https://code.visualstudio.com/updates)，其中 “Extension Authoring”（扩展开发）一节列出了新增和变化的 API。本指南翻译时依据的是 2026 年 10 月的文档和 `@types/vscode` 1.140，之后的版本可能会有新的变化。

---

<a id="looking-for-help"></a>
## 寻求帮助（Looking for help）

> 如果你对扩展开发有疑问，可以尝试在以下地方提问：
>
> - [VS Code Discussions](https://github.com/microsoft/vscode-discussions)：讨论 VS Code 扩展平台的 GitHub 社区，可以提问、帮助社区的其他成员、获得解答。
> - [Stack Overflow](https://stackoverflow.com/questions/tagged/vscode-extensions)：有[成千上万个](https://stackoverflow.com/questions/tagged/vscode-extensions)带有 `vscode-extensions` 标签的问题，其中一半以上已经有了答案。搜索你的问题、提问，或者回答 VS Code 扩展开发的问题来帮助其他开发者！
> - [VS Code Dev Slack](https://vscode-dev-community.slack.com)：面向扩展开发者的公共聊天室。VS Code 团队的成员也经常参与讨论。
>
> 要对文档提供反馈，请在 [Microsoft/vscode-docs](https://github.com/microsoft/vscode-docs/issues) 中新建 issue。如果你有找不到答案的扩展问题，或者遇到了 VS Code 扩展 API 的问题，请在 [Microsoft/vscode](https://github.com/microsoft/vscode/issues) 中新建 issue。
