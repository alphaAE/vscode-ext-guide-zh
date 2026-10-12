# 激活事件（Activation Events）

> 原文：[Activation Events](https://code.visualstudio.com/api/references/activation-events)
> 源文件：`microsoft/vscode-docs` → `api/references/activation-events.md`（DateApproved: 10/7/2026）

> **激活事件（Activation Events）**是你在 `package.json` [扩展清单](./extension-manifest.md)的 `activationEvents` 字段中所做的一组 JSON 声明。当**激活事件**发生时，你的扩展就会被激活。下面是所有可用的**激活事件**的列表：
>
> - [`onAuthenticationRequest`](#onAuthenticationRequest)
> - [`onChatParticipant`](#onChatParticipant)
> - [`onCommand`](#onCommand)
> - [`onCustomEditor`](#onCustomEditor)
> - [`onDebug`](#onDebug)
>   - [`onDebugAdapterProtocolTracker`](#onDebugAdapterProtocolTracker)
>   - [`onDebugDynamicConfigurations`](#onDebugDynamicConfigurations)
>   - [`onDebugInitialConfigurations`](#onDebugInitialConfigurations)
>   - [`onDebugResolve`](#onDebugResolve)
> - [`onEditSession`](#onEditSession)
> - [`onFileSystem`](#onFileSystem)
> - [`onIssueReporterOpened`](#onIssueReporterOpened)
> - [`onLanguage`](#onLanguage)
> - [`onLanguageModelTool`](#onLanguageModelTool)
> - [`onNotebook`](#onNotebook)
> - [`onOpenExternalUri`](#onOpenExternalUri)
> - [`onRenderer`](#onRenderer)
> - [`onSearch`](#onSearch)
> - [`onStartupFinished`](#onStartupFinished)
> - [`onTaskType`](#onTaskType)
> - [`onTerminal`](#onTerminal)
>   - [`onTerminalProfile`](#onTerminalProfile)
>   - [`onTerminalShellIntegration`](#onTerminalShellIntegration)
> - [`onUri`](#onUri)
> - [`onView`](#onView)
> - [`onWalkthrough`](#onWalkthrough)
> - [`onWebviewPanel`](#onWebviewPanel)
> - [`workspaceContains`](#workspaceContains)
> - [`*`](#Start-up)
>
> 我们还提供了 [`package.json` 扩展清单](./extension-manifest.md)中所有字段的参考。

**为什么需要激活事件？** VS Code 启动时不会加载所有已安装的扩展（那样启动会非常慢），而是等到“需要这个扩展的时候”才加载它并调用它的 `activate()` 函数。激活事件就是告诉 VS Code “什么时候需要我”。扩展的生命周期见 [扩展剖析](../get-started/extension-anatomy.md)。

**1.74.0 起的隐式激活（重要）：** 从 VS Code 1.74.0 开始，你在 `contributes` 中贡献的很多东西会**自动生成**对应的激活事件，不需要再在 `activationEvents` 中手写。下文中带有“注意：从 VS Code 1.74.0 开始……”的激活事件都属于这种情况：

| 贡献了 | 自动获得的激活事件 |
|---|---|
| `contributes.commands` | `onCommand:<命令 ID>` |
| `contributes.languages` | `onLanguage:<语言 ID>` |
| `contributes.views` | `onView:<视图 ID>` |
| `contributes.customEditors` | `onCustomEditor:<viewType>` |
| `contributes.authentication` | `onAuthenticationRequest:<提供者 ID>` |
| `contributes.taskDefinitions`（1.76.0 起） | `onTaskType:<类型>` |

所以现在大多数新扩展的 `activationEvents` 都是空数组 `[]`（只要 `engines.vscode` 不低于 `^1.74.0`）。只有在想用其他时机（比如打开了某种语言的文件，但这种语言不是你贡献的；或者工作区中包含某个文件）时，才需要手写。

---

<a id="onLanguage"></a>
## onLanguage

> 每当打开一个解析为特定语言的文件时，就会发出这个激活事件，感兴趣的扩展就会被激活。

```json
"activationEvents": [
    "onLanguage:python"
]
```

> `onLanguage` 事件接受一个[语言标识符](https://code.visualstudio.com/docs/languages/identifiers)值。
>
> 可以在 `activationEvents` 数组中用多个单独的 `onLanguage` 条目声明多种语言。

```json
"activationEvents": [
    "onLanguage:json",
    "onLanguage:markdown",
    "onLanguage:typescript"
]
```

> **注意**：从 VS Code 1.74.0 开始，你的扩展所贡献的语言，不需要再声明对应的 `onLanguage` 激活事件，扩展也会被激活。
>
> 此外，如果你的扩展需要在使用任何语言之前就被激活，可以使用通用的 `onLanguage` 激活事件来确保这一点：

```json
"activationEvents": [
    "onLanguage"
]
```

> **注意**：最佳实践是只在用户需要你的扩展时才激活。如果你的扩展只适用于一部分语言，那么列出这部分语言，比在所有语言上都激活对用户更好。

例如一个给 Markdown 提供功能的扩展，Markdown 是 VS Code 内置的语言而不是这个扩展贡献的，所以需要手写 `"onLanguage:markdown"`。

---

<a id="onCommand"></a>
## onCommand

> 每当一个命令被调用时，就会发出这个激活事件，感兴趣的扩展就会被激活：

```json
"activationEvents": [
    "onCommand:extension.sayHello"
]
```

> **注意**：从 VS Code 1.74.0 开始，你的扩展所贡献的命令，不需要再声明对应的 `onCommand` 激活事件，扩展也会被激活。

注意“贡献的命令”指的是写在 `contributes.commands` 中的命令。如果一个命令只在代码中用 `registerCommand` 注册、没有在 `contributes.commands` 中声明（比如只用于快捷键或其他扩展调用的内部命令），而又希望调用它时能激活扩展，就仍然需要手写 `onCommand`。

---

<a id="onDebug"></a>
## onDebug

> 在一个调试会话开始之前，会发出这个激活事件，感兴趣的扩展就会被激活：

```json
"activationEvents": [
    "onDebug"
]
```

> 还有四个更细粒度的 `onDebug` 激活事件：

<a id="onDebugAdapterProtocolTracker"></a>
### onDebugAdapterProtocolTracker

> 每当一个特定类型的调试会话即将启动、并且可能需要一个调试协议跟踪器时，就会发出 `onDebugAdapterProtocolTracker`。

（写法是 `onDebugAdapterProtocolTracker:<调试类型>`。“调试协议跟踪器”可以观察 VS Code 与调试适配器之间的所有 DAP 消息，见 [调试器扩展](../extension-guides/debugger-extension.md)。）

<a id="onDebugDynamicConfigurations"></a>
### onDebugDynamicConfigurations

> 在调用 `DebugConfigurationProvider` 的 `provideDebugConfigurations` 方法、以便在用户请求时（例如通过 UI 中的 “Select and Start Debugging” 命令）提供动态调试配置之前，会发出这个激活事件。
>
> 这个激活事件的存在，被用作一个信号，表示这个扩展贡献了动态的调试配置。

<a id="onDebugInitialConfigurations"></a>
### onDebugInitialConfigurations

> 在调用 `DebugConfigurationProvider` 的 `provideDebugConfigurations` 方法、以便提供初始调试配置（例如每当需要创建一个 `launch.json` 时）之前，会发出这个激活事件。

<a id="onDebugResolve"></a>
### onDebugResolve

> `onDebugResolve:type` 在调用指定类型的 `DebugConfigurationProvider` 的 `resolveDebugConfiguration` 方法之前触发。
>
> **经验法则：** 如果一个调试扩展的激活是轻量的，就使用 `onDebug`。如果是重量级的，就根据 `DebugConfigurationProvider` 是否实现了对应的方法 `provideDebugConfigurations` 和 / 或 `resolveDebugConfiguration`，使用 `onDebugInitialConfigurations` 和 / 或 `onDebugResolve`。关于这些方法的更多细节，请参见[使用 DebugConfigurationProvider](../extension-guides/debugger-extension.md#using-a-debugconfigurationprovider)。

| 激活事件 | 何时触发 |
|---|---|
| `onDebug` | 任何调试会话开始之前（所以只要用户调试任何东西，扩展都会被激活） |
| `onDebugAdapterProtocolTracker:<类型>` | 指定类型的调试会话启动、可能需要协议跟踪器时 |
| `onDebugDynamicConfigurations:<类型>` | 用户通过 “Select and Start Debugging” 等方式请求动态配置时 |
| `onDebugInitialConfigurations` | 创建 `launch.json`、需要初始配置时 |
| `onDebugResolve:<类型>` | 启动指定类型的调试、解析调试配置之前 |

“轻量 / 重量”是指 `activate()` 的开销：如果激活很快，用 `onDebug` 简单省事；如果激活很慢，就用更精确的事件，避免用户调试别的语言时也拖上你的扩展。

---

<a id="workspaceContains"></a>
## workspaceContains

> `workspaceContains:path` 在打开一个文件夹、并且这个文件夹中至少包含一个与某个 [glob 模式](https://code.visualstudio.com/docs/editor/glob-patterns)匹配的文件时发出，感兴趣的扩展就会被激活。

```json
"activationEvents": [
    "workspaceContains:**/.editorconfig"
]
```

常用于“检测到某种项目就激活”：比如 `workspaceContains:**/package.json`（Node 项目）、`workspaceContains:pom.xml`（Maven 项目）。`**/` 开头的模式会搜索整个工作区，在大型仓库中可能有一定开销；如果只关心根目录，直接写文件名即可。

---

<a id="onFileSystem"></a>
## onFileSystem

> `onFileSystem:scheme` 在读取来自特定 *scheme* 的文件或文件夹时发出，感兴趣的扩展就会被激活。这通常是 `file` scheme，但有了自定义的文件系统提供者，就会出现更多的 scheme，例如 `ftp` 或 `ssh`。

```json
"activationEvents": [
    "onFileSystem:sftp"
]
```

用于实现了 `FileSystemProvider` 的扩展（见 [虚拟工作区](../extension-guides/virtual-workspaces.md)）：当 VS Code 需要访问 `sftp://...` 这样的文件时，先激活负责这个 scheme 的扩展，让它有机会注册文件系统提供者。

---

<a id="onView"></a>
## onView

> 每当在 VS Code 侧边栏中展开一个指定 ID 的视图时，就会发出这个激活事件，感兴趣的扩展就会被激活。内置的视图不会发出激活事件。
>
> 下面的激活事件会在一个 ID 为 `nodeDependencies` 的视图可见时触发：

```json
"activationEvents": [
    "onView:nodeDependencies"
]
```

> **注意**：从 VS Code 1.74.0 开始，你的扩展所贡献的视图，不需要再声明对应的 `onView` 激活事件，扩展也会被激活。

（`nodeDependencies` 是 [树视图](../extension-guides/tree-view.md) 一篇中的示例视图。）

---

<a id="onUri"></a>
## onUri

> 每当打开一个属于这个扩展的、系统范围的 Uri 时，就会发出这个激活事件，感兴趣的扩展就会被激活。这个 Uri 的 scheme 固定为 `vscode` 或 `vscode-insiders`。Uri 的 authority 必须是扩展的标识符。Uri 的其余部分是任意的。

```json
"activationEvents": [
    "onUri"
]
```

> 如果 `vscode.git` 扩展把 `onUri` 定义为一个激活事件，那么打开以下任意一个 Uri 时，它都会被激活：
>
> - `vscode://vscode.git/init`
> - `vscode://vscode.git/clone?url=https%3A%2F%2Fgithub.com%2FMicrosoft%2Fvscode-vsce.git`
> - `vscode-insiders://vscode.git/init`（用于 VS Code Insiders）

**“系统范围的 Uri”** 是指在浏览器或其他程序中点击 `vscode://发布者.扩展名/...` 这样的链接时，操作系统会把它交给 VS Code 打开。常用于 OAuth 登录回调（网页登录完成后跳回 VS Code）、网页上的“在 VS Code 中打开”按钮。扩展中用 `vscode.window.registerUriHandler({ handleUri(uri) { ... } })` 处理这些 Uri。

---

<a id="onWebviewPanel"></a>
## onWebviewPanel

> 每当 VS Code 需要恢复一个具有匹配 `viewType` 的 [webview](../extension-guides/webview.md) 时，就会发出这个激活事件，感兴趣的扩展就会被激活。
>
> 例如，下面这个 `onWebviewPanel` 的声明：

```json
"activationEvents": [
    "onWebviewPanel:catCoding"
]
```

> 会让扩展在 VS Code 需要恢复一个 viewType 为 `catCoding` 的 webview 时被激活。viewType 是在调用 `window.createWebviewPanel` 时设置的，你需要另一个激活事件（例如 onCommand）来最初激活你的扩展并创建这个 webview。

“恢复”指的是：用户上次关闭 VS Code 时这个 webview 面板是打开的，重新打开 VS Code 时要把它恢复出来。这时扩展可能还没被激活，所以需要这个事件，配合 `registerWebviewPanelSerializer` 使用（见 [Webview](../extension-guides/webview.md#persistence) 中的“持久化”一节）。

---

<a id="onCustomEditor"></a>
## onCustomEditor

> 每当 VS Code 需要创建一个具有匹配 `viewType` 的[自定义编辑器](../extension-guides/custom-editors.md)时，就会发出这个激活事件，感兴趣的扩展就会被激活。
>
> 例如，下面这个 `onCustomEditor` 的声明：

```json
"activationEvents": [
    "onCustomEditor:catCustoms.pawDraw"
]
```

> 会让扩展在 VS Code 需要恢复一个 viewType 为 `catCustoms.pawDraw` 的自定义编辑器时被激活。viewType 是在 [`customEditors` 贡献点](../extension-guides/custom-editors.md#contribution-point)中设置的，并通过 `registerCustomEditorProvider` 绑定到一个提供者。

> **注意**：从 VS Code 1.74.0 开始，你的扩展所贡献的自定义编辑器，不需要再声明对应的 `onCustomEditor` 激活事件，扩展也会被激活。

---

<a id="onAuthenticationRequest"></a>
## onAuthenticationRequest

> 每当一个扩展请求一个具有匹配 `providerId` 的身份验证会话（通过 `authentication.getSession()` API）时，就会发出这个激活事件，感兴趣的扩展就会被激活。
>
> 例如，下面这个 `onAuthenticationRequest` 的声明：

```json
"activationEvents": [
    "onAuthenticationRequest:github"
]
```

> 会让扩展在 VS Code 需要获取一个 `github` 类型的 `AuthenticationSession` 时被激活。

> **注意**：从 VS Code 1.74.0 开始，你的扩展所贡献的身份验证提供者，不需要再声明对应的 `onAuthenticationRequest` 激活事件，扩展也会被激活。

这个事件是给**提供**身份验证的扩展用的（它实现了一个身份验证提供者），而不是给使用身份验证的扩展用的。

---

<a id="onStartupFinished"></a>
## onStartupFinished

> 这个激活事件在 VS Code 启动后的**某个时间**发出，感兴趣的扩展就会被激活。它类似于 `*` 激活事件，但不会拖慢 VS Code 的启动。目前，这个事件在所有 `*` 激活的扩展都完成激活之后发出。

```json
"activationEvents": [
    "onStartupFinished"
]
```

**需要“一直在后台运行”的扩展应该用它，而不是 `*`**，比如在状态栏中显示一些信息、定期检查更新的扩展。用户几乎感觉不到差别（只是晚了一两秒），但 VS Code 的启动速度不受影响。

---

<a id="onTaskType"></a>
## onTaskType

> 每当需要列出或解析某个类型的任务时，就会发出 `onTaskType:type`。

```json
"activationEvents": [
    "onTaskType:npm"
]
```

> **注意**：从 VS Code 1.76.0 开始，你的扩展所贡献的任务，不需要再声明对应的 `onTaskType` 激活事件，扩展也会被激活。

（“你的扩展所贡献的任务”指的是 `contributes.taskDefinitions` 中声明的任务类型，见 [任务提供者](../extension-guides/task-provider.md)。）

---

<a id="onEditSession"></a>
## onEditSession

> 当使用给定的 scheme 访问一个编辑会话时，会发出 `onEditSession:scheme`。

```json
"activationEvents": [
    "onEditSession:file"
]
```

（“编辑会话（Edit Sessions）”是 VS Code 在不同环境之间（例如从 vscode.dev 到桌面版）转移未提交的工作区修改的功能，现在称为 “Continue Working On”。这个激活事件主要用于提供相关 scheme 的扩展。）

---

<a id="onSearch"></a>
## onSearch

> 当在给定 scheme 的文件夹中开始一次搜索时，会发出 `onSearch:scheme`。

```json
"activationEvents": [
    "onSearch:file"
]
```

（主要用于为自定义的 scheme 提供搜索功能的扩展，例如虚拟文件系统的扩展。）

---

<a id="onOpenExternalUri"></a>
## onOpenExternalUri

> 每当打开一个外部 URI（例如一个 http 或 https 链接）时，就会发出这个激活事件。

```json
"activationEvents": [
    "onOpenExternalUri"
]
```

（用于想要拦截外部链接的扩展，例如在远程开发中，把指向 `localhost` 的链接转换为端口转发后的地址。）

---

<a id="onNotebook"></a>
## onNotebook

> 当打开指定类型的笔记本文档时，会发出 `onNotebook:type`。

```json
"activationEvents": [
    "onNotebook:jupyter-notebook",
    "onNotebook:interactive"
]
```

（笔记本类型由 `contributes.notebooks` 中的 `type` 定义，见 [笔记本](../extension-guides/notebook.md)。`interactive` 是交互式窗口。）

---

<a id="onRenderer"></a>
## onRenderer

> 当使用一个笔记本输出渲染器时，会发出 `onRenderer:id`。

```json
"activationEvents": [
    "onRenderer:ms-toolsai.jupyter-renderers"
]
```

---

<a id="onTerminal"></a>
## onTerminal

> 当打开一个具有给定 shell 类型的特定终端时，会发出 `onTerminal:shellType`。

```json
"activationEvents": [
  "onTerminal:bash"
]
```

---

<a id="onTerminalProfile"></a>
## onTerminalProfile

> 当启动一个特定的终端配置文件时，会发出 `onTerminalProfile:id`。

```json
"activationEvents": [
    "onTerminalProfile:terminalTest.terminal-profile"
]
```

（终端配置文件由 `contributes.terminal.profiles` 贡献，扩展用 `window.registerTerminalProfileProvider` 提供具体的终端，见 [贡献点](./contribution-points.md#contributes.terminal)。）

---

<a id="onTerminalShellIntegration"></a>
## onTerminalShellIntegration

> 当一个具有给定 shell 类型的终端激活了 shell 集成时，会发出 `onTerminalShellIntegration:shellType`。

```json
"activationEvents": [
    "onTerminalShellIntegration:bash"
]
```

（“shell 集成”让 VS Code 能够识别终端中每条命令的开始、结束和退出码。扩展可以通过 `window.onDidChangeTerminalShellIntegration` 等 API 使用它。）

---

<a id="onWalkthrough"></a>
## onWalkthrough

> 当打开一个指定的演练（walkthrough）时，会发出 `onWalkthrough:id`。

```json
"activationEvents": [
    "onWalkthrough:nodejsWelcome"
]
```

（演练见 [UX 指南：演练](../ux-guidelines/walkthroughs.md)。）

---

<a id="onIssueReporterOpened"></a>
## onIssueReporterOpened

> 当打开问题报告器时（例如使用 **Help: Report Issue** 命令），会发出这个激活事件。

```json
"activationEvents": [
    "onIssueReporterOpened"
]
```

（用于想在用户提交问题报告时附加额外信息的扩展。）

---

<a id="onChatParticipant"></a>
## onChatParticipant

> 当调用指定的聊天参与者时，会发出这个激活事件。

```json
"activationEvents": [
    "onChatParticipant:my-chat-participant"
]
```

（见 [聊天参与者](../extension-guides/ai/chat.md)。）

---

<a id="onLanguageModelTool"></a>
## onLanguageModelTool

> 当调用指定的语言模型工具时，会发出这个激活事件。

```json
"activationEvents": [
    "onLanguageModelTool:my-language-model-tool"
]
```

（见 [语言模型工具](../extension-guides/ai/tools.md)。）

---

<a id="start-up"></a>
<a id="Start-up"></a>
## 启动时（Start up）

> `*` 激活事件在 VS Code 启动时发出，感兴趣的扩展就会被激活。

> **注意**：为了确保良好的用户体验，请只在没有其他激活事件的组合能满足你的使用场景时，才在扩展中使用这个激活事件。

```json
"activationEvents": [
    "*"
]
```

> **注意**：一个扩展可以监听多个激活事件，这比监听 `"*"` 更可取。

> **注意**：一个扩展**必须**从它的主模块中导出一个 `activate()` 函数，当任意一个指定的激活事件发出时，VS Code 会调用它，**且只调用一次**。此外，一个扩展**应该**从它的主模块中导出一个 `deactivate()` 函数，以便在 VS Code 关闭时执行清理任务。如果清理过程是异步的，扩展**必须**从 `deactivate()` 中返回一个 Promise。如果清理是同步执行的，扩展可以从 `deactivate()` 中返回 `undefined`。

```ts
export function activate(context: vscode.ExtensionContext) {
  // 只会被调用一次，即使之后又发生了其他激活事件
}

export async function deactivate() {
  // 异步清理：返回 Promise，VS Code 会等待它完成（但等待时间有限）
}
```

大部分清理工作，更推荐的做法是把可释放的对象 `push` 到 `context.subscriptions` 中，扩展停用时 VS Code 会自动释放它们，`deactivate` 只用来处理无法这样管理的资源。

---

## 本篇小结

```text
激活事件：告诉 VS Code 何时加载扩展、调用 activate()（只调用一次）

1.74.0+ 自动生成（不必手写）：commands、languages、views、customEditors、authentication、taskDefinitions（1.76）
  → 新扩展的 activationEvents 通常为 []

常用的手写激活事件
  onLanguage:<id>              打开某种语言的文件（不是你贡献的语言时）
  workspaceContains:<glob>     工作区中包含某种文件
  onStartupFinished            需要常驻后台（代替 *）
  onUri                        处理 vscode://发布者.扩展名/... 链接
  onWebviewPanel:<viewType>    恢复 webview 面板
  onFileSystem:<scheme>        自定义文件系统
  onDebug / onDebugResolve:<type> 等  调试
  * （尽量避免）

deactivate()：可选，异步清理时返回 Promise；更推荐使用 context.subscriptions
```
