# 原文勘误清单

在翻译过程中，对照 `@types/vscode` 1.140.0 和原文上下文发现的问题汇总如下。每一处都已在对应的正文中就地注明（并在可能时给出修正后的写法），这里只列要点，便于集中查看，也可以据此向 [microsoft/vscode-docs](https://github.com/microsoft/vscode-docs) 反馈。

分类说明：**代码错误**（照抄无法编译或运行）、**API 不符**（与 1.140.0 稳定 API 不一致，多为提议中的 API）、**内容错误**（说法或链接有误）、**过时**（工具、版本、做法已经变化）。

## 时效性提醒

| 位置 | 说明 |
|---|---|
| [发布扩展](./working-with-extensions/publishing-extension.md#publishing-extensions)、[持续集成](./working-with-extensions/continuous-integration.md#automated-publishing) | Azure DevOps 全局 PAT 将于 **2026-12-01** 停用，而市场发布正是依赖全局 PAT（All accessible organizations）。基于 `VSCE_PAT` 的 CI 自动发布需要迁移到 Entra ID 托管标识（`vsce publish --azure-credential`） |

## 扩展指南

| 篇目 | 类型 | 问题 |
|---|---|---|
| [Webview](./extension-guides/webview.md) | 代码错误 | 示例中 `webview.title` 应为 `panel.title` |
| [自定义编辑器](./extension-guides/custom-editors.md) | 内容错误 | 示例前后的 `viewType` 不一致 |
| [树视图](./extension-guides/tree-view.md) | 代码错误 | 示例代码直接照抄会有 TypeScript 类型错误 |
| [笔记本](./extension-guides/notebook.md) | 代码错误 / API 不符 | 序列化器示例的读写不能往返（round-trip）；对象键 `custom-data-for-custom-renderer` 缺引号；渲染器脚本与控制器之间的通信 API 属于提议的 API |
| [源代码管理](./extension-guides/scm-provider.md) | 内容错误 | 说有 “6 个菜单”，实际列出了 7 个 |
| [调试器扩展](./extension-guides/debugger-extension.md) | 过时 / 内容遗漏 | npm 包已改名为 `@vscode/*`；调试适配器描述符实际还有第 4 种 `DebugAdapterNamedPipeServer` |
| [测试 API](./extension-guides/testing.md) | 代码错误 | `getOrCreateFile` 创建的测试项从未加入 `controller.items` |
| [Web 扩展](./extension-guides/web-extensions.md) | 代码错误 | `import` 语句中模块名用了反引号 |
| [颜色主题](./extension-guides/color-theme.md) | 内容错误 | 链接 `syntax-highlight-guide#semantic-theming` 指向不存在的小节，应为语义高亮指南的 `#theming` |
| [MCP](./extension-guides/ai/mcp.md) | API 不符 / 代码错误 | 1.140 中 `McpStdioServerDefinition` / `McpHttpServerDefinition` 的构造函数是位置参数；HTTP 的 `uri` 必须是 `Uri`；示例本身有语法错误 |
| [聊天参与者](./extension-guides/ai/chat.md) | API 不符 / 代码错误 | `request.variables`、`request.location` 不在稳定 API 中（应使用 `request.references`）；一个代码块示例多了一组 ` ``` ` |
| [聊天教程](./extension-guides/ai/chat-tutorial.md) | 代码错误 | 构造历史消息时遗漏了用户的轮次；类型断言不安全 |
| [语言模型教程](./extension-guides/ai/language-model-tutorial.md) | 代码错误 | 所谓的“切换”实际上不会关闭注释；装饰类型没有释放，会泄漏 |

## UX 指南、入门与扩展能力

| 篇目 | 类型 | 问题 |
|---|---|---|
| [通知](./ux-guidelines/notifications.md) | 内容错误 | 模态通知的图片说明与截图内容不符 |
| [总结](./get-started/wrapping-up.md) | 格式问题 | 示例中 `menus` 多缩进了一层，看起来像是 `commands` 的下级（JSON 不看缩进，配置本身有效） |
| [语言扩展概览](./language-extensions/overview.md) | 内容错误 | “多根工作区支持”一节说“这个主题讨论了……”，但缺少链接 |

## 语言扩展

| 篇目 | 类型 | 问题 |
|---|---|---|
| [语义高亮](./language-extensions/semantic-highlight-guide.md) | 内容错误 | “modifies” 应为 “modifiers”；示例中 `Position(1,1)` 是从 0 开始计数的第 2 行 |
| [编程式语言功能](./language-extensions/programmatic-language-features.md) | 内容错误 / 代码错误 / API 不符 | `completionItem\resolve`、`codeLens\resolve` 应为 `/`；JSON 中的 `"true"`、`['.']` 不是有效的 LSP 能力写法；`moreTriggerCharacters` 实为 `moreTriggerCharacter`；文档高亮示例签名后多了 `;`；输入时格式化示例的注册调用漏掉了必填的触发字符；`InlineCompletionList.commands` 是提议的 API；工作区符号提供者未列入功能表 |
| [语言服务器扩展指南](./language-extensions/language-server-extension-guide.md) | 内容错误 / 过时 | `activationEvents` 示例写成空数组，与正文 `onLanguage:plaintext` 不符；“增量同步”一节的描述与前文已使用 `Incremental` 的代码矛盾，且通知参数应为 `params.textDocument.uri` 等；`${workspaceRoot}` 已被 `${workspaceFolder}` 取代 |
| [嵌入式语言](./language-extensions/embedded-languages.md) | 内容错误 | 请求转发示例的 `documentSelector` 写的是 `html`，与示例贡献的 `html1` 语言不一致 |

## 测试与发布

| 篇目 | 类型 | 问题 |
|---|---|---|
| [打包扩展代码](./working-with-extensions/bundling-extension.md) | 代码错误 / 过时 | webpack 的 `scripts` JSON 末尾多了逗号；`npm-run-all` 已长期未维护（可用 `npm-run-all2`）；`target: 'webworker'` 下不能使用 Node API，原文未提示 |
| [测试扩展](./working-with-extensions/testing-extension.md) | 内容不一致 | 运行器使用 `ui: 'tdd'`，示例测试却从 `mocha` 导入 BDD 风格的 `after` |
| [持续集成](./working-with-extensions/continuous-integration.md) | 过时 / 显示问题 | Node.js 10.x、18.x、`node:12-buster` 均已过时；网页中的 `$\{{ ... }}` 是模板转义，实际应写 `${{ ... }}`；示例 YAML 来自 vscode-test 仓库本身，与普通扩展的步骤不同；在 npm 项目中仍使用 `vsce publish --yarn` |
| [发布扩展](./working-with-extensions/publishing-extension.md) | 内容提示 | `vsce unpublish` 实际执行的是不可恢复的“删除”，而非网页上的“取消发布”；`--target` 一节的 `1.99.0` 指 vsce 的版本 |

## 参考

| 篇目 | 类型 | 问题 |
|---|---|---|
| [贡献点](./references/contribution-points.md) | 内容错误 / 代码错误 / API 不符 | `workspace.colorCustomization` 应为 `workbench.colorCustomizations`；`colors`、`terminal` 示例 JSON 有尾随逗号；`#icon-in-labels` 锚点应为 `#icons-in-labels`；`languageModelChatProviders` 提到配置示例却没有给出；`provideTerminalProfile` 在 1.140 中应返回 `TerminalProfile`；“提示文件”的链接与“指令文件”指向同一页面；`its` 误写为 `it's` |
| [扩展清单](./references/extension-manifest.md) | 过时 / 内容错误 | 完整示例中的 `node_modules/vscode/bin/compile`、`@types/vscode ^0.10.x`、`typescript ^1.6.2` 早已废弃；`vscode:prepublish` 的锚点 `#prepublish-step` 应为 `#pre-publish-step`；`vscode-nls` 已被 `vscode.l10n` 取代 |
| [内置命令](./references/commands.md) | 内容错误 | `goto` 两处缺少结尾反引号；`notebook.selectKernel` 重复出现；`executeCodeActionProvider` 实际可能返回 `CodeAction` 与 `Command` 混合的数组 |
| [产品图标参考](./references/icons-in-labels.md) | 内容错误 | `distro-fedora` 的描述写成了 “Ubuntu icon”；标签示例的代码块标为 `ts`，但其实是标签字符串 |
| [主题颜色参考](./references/theme-color.md) | 内容错误 | `inputOption.hoverBackground`、`tree.tableColumnsBorder`、`testing.peekHeaderBackground`、`testing.messagePeekHeaderBackground`、`mergeEditor.conflict.*.minimapOverViewRuler` 的描述疑似复制错误；`welcomePage.progress.background/foreground` 的描述写反；`debugIcon.stepOutForeground` 误写为 step over；`editorInlayHint.*` 一节称由 `editor.inlineSuggest.enabled` 控制，实际应为 `editor.inlayHints.enabled` |
| [when 子句上下文](./references/when-clause-contexts.md) | 内容提示 | 称“上下文键的计算结果为布尔值”，但列表中有大量字符串 / 数字类型的键 |

## 高级主题

| 篇目 | 类型 | 问题 |
|---|---|---|
| [远程开发](./advanced-topics/remote-extensions.md) | 代码错误 | 持久化全局数据的示例缺少 `}`；机密示例未 `await` `secrets.get`，且把 `string \| undefined` 传给 `store`；`asExternalUri` 示例导入 `getExpressServerPort` 却调用 `getWebServerPort`，并缺少函数体的 `{`；`setKeysforSync` 大小写错误；`vscode.extension.getExtension` 少了 s；iframe 缺少结束标签；`fs.exists` 已弃用；第 4 步重复了 “Add Dev Container Configuration Files” 命令 |
| [Python 扩展模板](./advanced-topics/python-extension-template.md) | 内容不一致 | 占位符前后写作 `<pythontool-module>` 与 `<pytool-module>` |
| [TSLint 迁移](./advanced-topics/tslint-eslint-migration.md) | 过时 | ESLint 9 起使用 `eslint.config.mjs` 扁平配置，`--ext` 已移除；“eslint-typescript-support”并非真实包名 |
