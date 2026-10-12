# 总结（Wrapping Up）

> 原文：[Wrapping Up](https://code.visualstudio.com/api/get-started/wrapping-up)
> 源文件：`microsoft/vscode-docs` → `api/get-started/wrapping-up.md`（DateApproved: 10/7/2026）

> 在[你的第一个扩展](./your-first-extension.md)主题中，你学会了如何创建、运行和调试一个扩展。在[扩展的结构](./extension-anatomy.md)主题中，你学习了 Visual Studio Code 扩展开发的基础概念。不过，我们看到的只是冰山一角，下面是一些继续提升 VS Code 扩展开发技能的建议路线。

这一篇是入门部分的收尾，主要是给出**后续文档的地图**，告诉你接下来该去看哪些章节。另外中间夹了一个实用的小功能：**接入“报告问题”流程**。

---

<a id="extension-capabilities"></a>
## 扩展能力（Extension Capabilities）

> 在这一部分中，我们把 [VS Code API](https://code.visualstudio.com/api/references/vscode-api) 和[贡献点](../references/contribution-points.md)分成了几个类别，每个类别都简要说明了你的扩展能实现什么。你可以查看 [VS Code API](https://code.visualstudio.com/api/references/vscode-api)，验证你的扩展想法是否可以实现；也可以阅读[扩展能力](../extension-capabilities/overview.md)一节，寻找新的扩展点子。

**这一节适合什么时候看：** 当你有了一个扩展想法，但不确定 VS Code 是否支持、该用哪个接口时。它按功能分类讲解扩展能做什么：

| 篇目 | 内容 |
|---|---|
| [通用能力](../extension-capabilities/common-capabilities.md) | 命令、设置、快捷键、通知、数据存储等 |
| [扩展工作台](../extension-capabilities/extending-workbench.md) | 侧边栏视图、Webview、状态栏等 |
| [主题](../extension-capabilities/theming.md) | 颜色主题、文件图标主题、产品图标主题 |
| [扩展能力概览](../extension-capabilities/overview.md) 中的语言部分 | 语法高亮、代码补全、跳转到定义等 |

**另外要知道扩展“不能做什么”：** VS Code 不允许扩展直接操作界面的 DOM，也就是说不能随意修改 VS Code 自身的样式和布局。扩展只能通过官方提供的 API 和贡献点来扩展界面。这个限制保证了 VS Code 的稳定和性能，但也意味着有些想法是实现不了的，所以动手前先确认一下可行性（见 [扩展能力概览](../extension-capabilities/overview.md#restrictions) 中的“限制”一节）。

---

<a id="guides--samples"></a>
## 指南与示例（Guides & Samples）

> 我们有大量很棒的示例扩展，你可以在它们的基础上改造，其中一些还配有详细讲解源代码的指南。你可以在[扩展指南列表](../extension-guides/overview.md)或 [vscode-extension-samples](https://github.com/microsoft/vscode-extension-samples) 仓库中找到所有的示例和指南。

推荐的学习方法：**想做什么功能，就去找对应的示例跑一遍，再改造成自己的。**

例如想做一个侧边栏树形列表，就去示例仓库找 `tree-view-sample`，克隆下来按 `F5` 运行，看看效果，再对照 [树视图 API](../extension-guides/tree-view.md) 阅读源码。这比从零开始照着文档写要快得多。

---

<a id="ux-guidelines"></a>
## UX 指南（UX Guidelines）

> 为了让你的扩展无缝地融入 VS Code 的用户界面，请参考 [UX 指南](../ux-guidelines/overview.md)，在那里你会学到创建扩展界面的最佳实践，以及遵循 VS Code 推荐工作流的约定。

技术上能实现，不代表就应该这么做。UX 指南讲的是“怎样做得像 VS Code 原生功能一样”，例如：

- 通知不要弹得太频繁，否则会打扰用户（见 [通知](../ux-guidelines/notifications.md)）；
- 状态栏上的内容要简短（见 [状态栏](../ux-guidelines/status-bar.md)）；
- 命令名称要清楚易懂，并用分类前缀归组（见 [命令面板](../ux-guidelines/command-palette.md)）。

如果你打算把扩展发布给别人用，建议通读一遍。

---

<a id="issue-reporting"></a>
## 问题报告（Issue Reporting）

> VS Code 用户可以通过 **Help: Report Issue...** 命令（`workbench.action.openIssueReporter`）报告问题，也可以在快速打开（`workbench.action.quickOpen`）中输入 `issue `（后面带一个空格），然后选择一个已安装的扩展。这为用户报告 VS Code 本身或已安装扩展的问题，提供了一致的体验。

也就是说，VS Code 内置了一个统一的“问题报告器”窗口，可以直接给 VS Code 本身或任何一个扩展提交问题。快速打开的默认快捷键是 `Ctrl+P`（macOS 上是 `Cmd+P`）。

> 作为扩展作者，你可以把扩展接入 **Help: Report Issue...** 这个问题报告器流程，而不必另外贡献一个单独的报告问题命令。这种集成还让你可以在用户报告问题时附加任何额外的信息。

**接入有什么好处？**

- 用户不用到处找你的 GitHub 仓库地址，在统一的入口就能提交问题；
- 你可以自动附带诊断信息（比如扩展的配置、日志），省去来回追问用户“你用的是什么版本、怎么配置的”。

> 要接入问题报告器流程，你需要贡献一个自定义命令和一个 `issue/reporter` 菜单贡献点。这个自定义命令会调用 `openIssueReporter`。
>
> 下面是 `package.json` 的 `contributes` 中贡献的命令和菜单的示例（关于如何添加菜单贡献和命令，请参见[贡献点](../references/contribution-points.md)）：

```json
"commands": [
    {
        "command": "extension.myCommand",
        "title": "Report Issue"
    }
],
    "menus": {
        "issue/reporter": [
            {
                "command": "extension.myCommand"
            }
        ]
    }

```

（原文这段配置中 `menus` 的缩进有误：`commands` 和 `menus` 都是 `contributes` 下的同级字段，`menus` 不应该多缩进一层。JSON 不看缩进，所以这段配置本身仍然有效。）

理解这段配置，需要用上前两篇学到的知识：

1. **`commands`**：声明一个命令，和 Hello World 里的一样；
2. **`menus` → `issue/reporter`**：`menus` 贡献点用来把命令放进各种菜单，`issue/reporter` 是其中一个特殊的“菜单位置”，表示“问题报告器”。放在这里的命令，会在用户通过问题报告器给你的扩展提交问题时被调用。

配置只完成了一半，还需要在代码里**实现**这个命令，在其中调用 `workbench.action.openIssueReporter` 打开问题报告器。原文没有给出代码，下面是一个参考写法（补充内容）：

```ts
context.subscriptions.push(
  vscode.commands.registerCommand('extension.myCommand', () => {
    vscode.commands.executeCommand('workbench.action.openIssueReporter', {
      extensionId: 'publisher.extension-name', // 你的扩展 ID：<publisher>.<name>
      issueBody: '在这里写入附加的诊断信息',   // 预先填入问题正文
    });
  })
);
```

这又是“贡献点声明 + VS Code API 实现”的组合。传给 `openIssueReporter` 的参数可能随版本变化，实际使用时请对照 [内置命令](../references/commands.md) 确认。

> 我们希望以前在命令面板中贡献了 `workbench.action.openIssueReporter` 命令的扩展，开始改用这种新的问题报告流程。

---

<a id="testing-and-publishing"></a>
## 测试与发布（Testing and Publishing）

> 这一部分包含帮助你开发高质量 VS Code 扩展的主题。例如，你可以学习：
>
> - 如何为你的扩展添加[集成测试](../working-with-extensions/testing-extension.md)
> - 如何把你的扩展[发布](../working-with-extensions/publishing-extension.md)到 VS Code [扩展市场](https://marketplace.visualstudio.com/)
> - 如何为你的扩展设置[持续集成](../working-with-extensions/continuous-integration.md)

对应原文中的 “Working with Extensions” 部分，包括测试、打包、发布、持续集成四篇。等扩展功能做得差不多、准备给别人用时再看即可。

---

## 本篇小结

结合整个文档的目录，下面是一条推荐的学习顺序（补充内容）：

| 阶段 | 章节 | 什么时候看 |
|---|---|---|
| ✅ 入门 | Get Started（本部分） | 已完成 |
| 1. 了解全貌 | [扩展能力](../extension-capabilities/overview.md)（4 篇） | 马上看，知道扩展能做什么 |
| 2. 学具体功能 | [扩展指南](../extension-guides/overview.md)（命令、树视图、Webview 等） | 按需挑选，**配合示例代码**学习 |
| 3. 做得规范 | [UX 指南](../ux-guidelines/overview.md) | 开始设计界面时 |
| 4. 语言支持 | [语言扩展](../language-extensions/overview.md) | 想给某种语言做高亮、补全时 |
| 5. 测试和发布 | [测试与发布](../working-with-extensions/testing-extension.md) | 准备发布时 |
| 随时查阅 | 参考：[贡献点](../references/contribution-points.md)、[激活事件](../references/activation-events.md)、[when 子句上下文](../references/when-clause-contexts.md)、[VS Code API](https://code.visualstudio.com/api/references/vscode-api) | 当字典用，用到时再查 |

**入门部分的核心只有一句话：** 扩展 = `package.json` 里的**声明**（贡献点 + 激活事件）+ 代码里的**实现**（VS Code API）。后面所有章节，都是在这个框架里增加新的贡献点和新的 API。
