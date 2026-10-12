# 通用能力（Common Capabilities）

> 原文：[Common Capabilities](https://code.visualstudio.com/api/extension-capabilities/common-capabilities)
> 源文件：`microsoft/vscode-docs` → `api/extension-capabilities/common-capabilities.md`（DateApproved: 10/7/2026）

> 通用能力是构建扩展的重要基础，几乎所有扩展都会用到其中的一部分。下面介绍如何使用它们。

这一篇原文写得很简短，每个能力基本只有一两句话，再给出 API 链接。为了让你只看本篇就能上手，每个能力后面都**补充了最小可运行的示例代码**。示例代码都写在 `activate(context)` 函数里，需要的 `import * as vscode from 'vscode'` 等前提见 [扩展的结构](../get-started/extension-anatomy.md)。

先看全貌：

| 能力 | 主要用到 | 一句话说明 |
|---|---|---|
| [命令](#command) | `vscode.commands` + `contributes.commands` | 扩展功能的入口 |
| [配置](#configuration) | `contributes.configuration` + `workspace.getConfiguration` | 让用户能在设置页面里调整扩展的行为 |
| [快捷键](#keybinding) | `contributes.keybindings` | 给命令绑定快捷键 |
| [上下文菜单](#context-menu) | `contributes.menus` | 把命令放进右键菜单 |
| [数据存储](#data-storage) | `ExtensionContext` 上的 5 种存储 | 保存扩展的状态和数据 |
| [显示通知](#display-notifications) | `window.show*Message` | 弹出信息、警告、错误提示 |
| [快速选择](#quick-pick) | `QuickPick` | 让用户从列表中选择或输入文字 |
| [文件选择器](#file-picker) | `window.showOpenDialog` | 让用户选择文件或文件夹 |
| [输出通道](#output-channel) | `window.createOutputChannel` | 在“输出”面板中打印日志 |
| [进度 API](#progress-api) | `window.withProgress` | 显示耗时操作的进度 |

可以看出规律：**凡是要出现在界面上、能静态声明的（命令、设置、快捷键、菜单），都用贡献点；凡是运行时的行为（读设置、存数据、弹提示），都用 API。** 这和 [扩展的结构](../get-started/extension-anatomy.md) 中讲的“声明 + 实现”是同一个思路。

---

<a id="command"></a>
## 命令（Command）

> 命令是 VS Code 运作的核心。你打开命令面板来执行命令，给命令绑定自定义快捷键，在上下文菜单中右键调用命令。
>
> 扩展可以：
>
> - 使用 [`vscode.commands`](https://code.visualstudio.com/api/references/vscode-api#commands) API 注册和执行命令。
> - 使用 [`contributes.commands`](../references/contribution-points.md#contributes.commands) 贡献点让命令出现在命令面板中。
>
> 更多内容请参阅 [扩展指南 / 命令](../extension-guides/command.md)。

命令是后面快捷键、菜单的基础：**快捷键和菜单本身不包含逻辑，它们只是“触发某个命令”的入口。** 所以要先有命令，才能给它绑定快捷键、放进菜单。

```jsonc
// package.json
"contributes": {
  "commands": [
    { "command": "myExtension.sayHello", "title": "Say Hello" }
  ]
}
```

```ts
// extension.ts
context.subscriptions.push(
  vscode.commands.registerCommand('myExtension.sayHello', () => {
    vscode.window.showInformationMessage('Hello!');
  })
);
```

命令的完整用法（参数、显示条件、启用条件等）见 [命令指南](../extension-guides/command.md)。

---

<a id="configuration"></a>
## 配置（Configuration）

> 扩展可以通过 [`contributes.configuration`](../references/contribution-points.md#contributes.configuration) 贡献点添加扩展专属的设置，并使用 [`workspace.getConfiguration`](https://code.visualstudio.com/api/references/vscode-api#workspace.getConfiguration) API 读取这些设置。

**第一步：在 `package.json` 中声明设置项。** 声明后，用户就能在“设置”页面中搜到并修改它们：

```jsonc
"contributes": {
  "configuration": {
    "title": "My Extension",
    "properties": {
      "myExtension.greeting": {
        "type": "string",
        "default": "Hello",
        "description": "打招呼时使用的问候语"
      },
      "myExtension.showTime": {
        "type": "boolean",
        "default": false,
        "description": "是否在问候语后面显示当前时间"
      }
    }
  }
}
```

**第二步：在代码中读取设置。**

```ts
// 取出 myExtension 这一组设置
const config = vscode.workspace.getConfiguration('myExtension');

// 读取具体的值；如果用户没设置，会返回 package.json 中声明的 default
const greeting = config.get<string>('greeting');
const showTime = config.get<boolean>('showTime');
```

**第三步（可选）：监听设置的变化。** 用户修改设置后，如果希望立即生效而不是等到下次启动，就要监听变化事件：

```ts
context.subscriptions.push(
  vscode.workspace.onDidChangeConfiguration(e => {
    if (e.affectsConfiguration('myExtension.greeting')) {
      // 问候语设置变了，在这里重新读取
    }
  })
);
```

**注意：** 设置的键名一般以扩展名作为前缀（例如 `myExtension.greeting`），避免与其他扩展的设置冲突。用户修改后的值保存在用户的 `settings.json` 中，并不是改了你的 `package.json`。

---

<a id="keybinding"></a>
## 快捷键（Keybinding）

> 扩展可以添加自定义快捷键。详情请阅读 [`contributes.keybindings`](../references/contribution-points.md#contributes.keybindings) 和 [键绑定](https://code.visualstudio.com/docs/getstarted/keybindings) 两篇文档。

快捷键只需要在 `package.json` 中声明，不需要写代码：

```jsonc
"contributes": {
  "keybindings": [
    {
      "command": "myExtension.sayHello",  // 要触发的命令
      "key": "ctrl+alt+h",                // Windows / Linux 上的按键
      "mac": "cmd+alt+h",                 // macOS 上的按键（可选）
      "when": "editorTextFocus"           // 生效条件：编辑器获得焦点时（可选）
    }
  ]
}
```

- `when` 用的是 when 子句，和 [命令指南](../extension-guides/command.md) 中控制命令显示的写法一样。不写 `when` 的话，任何时候都生效。
- 选择快捷键时，注意不要和 VS Code 内置的快捷键冲突。可以在“键盘快捷方式”面板中搜索按键，看看是否已被占用。
- 你声明的只是**默认**快捷键，用户随时可以在“键盘快捷方式”面板中修改。

---

<a id="context-menu"></a>
## 上下文菜单（Context Menu）

> 扩展可以注册自定义的上下文菜单项，它们会在 VS Code 界面的不同位置、在用户右键时显示。详情请阅读 [`contributes.menus`](../references/contribution-points.md#contributes.menus) 贡献点。

菜单同样只需在 `package.json` 中声明。关键在于 `menus` 下的**键名决定菜单出现在哪里**：

```jsonc
"contributes": {
  "menus": {
    // 编辑器中右键
    "editor/context": [
      { "command": "myExtension.sayHello", "when": "editorHasSelection" }
    ],
    // 资源管理器中右键文件或文件夹
    "explorer/context": [
      { "command": "myExtension.sayHello" }
    ]
  }
}
```

常用的菜单位置：

| 菜单位置 | 出现在哪里 |
|---|---|
| `editor/context` | 编辑器中的右键菜单 |
| `editor/title` | 编辑器标签页右侧的按钮区域 |
| `explorer/context` | 资源管理器中的右键菜单 |
| `view/title` | 视图标题栏上的按钮 |
| `view/item/context` | 树视图条目的右键菜单或行内按钮 |
| `commandPalette` | 命令面板（用来控制命令是否显示） |

完整的菜单位置列表见 [贡献点参考](../references/contribution-points.md#contributes.menus)。

从资源管理器的右键菜单触发命令时，处理函数会收到被点击文件的 `Uri` 作为参数，详见 [命令指南](../extension-guides/command.md) 中“命令处理函数的参数”一节。

---

<a id="data-storage"></a>
## 数据存储（Data Storage）

> 存储数据有五种方式：

原文用列表介绍了 5 种方式。下面先逐条翻译，再整理成对比表。

> - [`ExtensionContext.workspaceState`](https://code.visualstudio.com/api/references/vscode-api#ExtensionContext.workspaceState)：工作区存储，可以写入键值对。VS Code 负责管理这份存储，再次打开同一个工作区时会恢复它。
> - [`ExtensionContext.globalState`](https://code.visualstudio.com/api/references/vscode-api#ExtensionContext.globalState)：全局存储，可以写入键值对。VS Code 负责管理这份存储，每次扩展激活时都会恢复它。你可以在 `globalState` 上调用 `setKeysForSync` 方法，设置需要同步的键，从而有选择地同步全局存储中的键值对。
> - [`ExtensionContext.storageUri`](https://code.visualstudio.com/api/references/vscode-api#ExtensionContext.storageUri)：工作区专属的存储 URI，指向一个本地目录，扩展对它有读写权限。如果需要存储只在当前工作区使用的大文件，这是一个好选择。
> - [`ExtensionContext.globalStorageUri`](https://code.visualstudio.com/api/references/vscode-api#ExtensionContext.globalStorageUri)：全局存储 URI，指向一个本地目录，扩展对它有读写权限。如果需要存储在所有工作区都能使用的大文件，这是一个好选择。
> - [`ExtensionContext.secrets`](https://code.visualstudio.com/api/references/vscode-api#ExtensionContext.secrets)：用于存储机密信息（或任何敏感信息）的全局存储，内容会被加密。这些信息不会在不同机器之间同步。在 VS Code 桌面版中，它使用 Electron 的 [safeStorage API](https://www.electronjs.org/docs/latest/api/safe-storage)；在网页版 VS Code 中，它使用双密钥加密（Double Key Encryption，DKE）实现。
>
> 扩展上下文（extension context）可以在[扩展入口文件](../get-started/extension-anatomy.md#extension-entry-file)的 `activate` 函数中获取。

**对比表：**

| 方式 | 存什么 | 作用范围 | 能否跨机器同步 | 典型用途 |
|---|---|---|---|---|
| `workspaceState` | 键值对 | 当前工作区 | 否 | 记住这个项目上次选中的选项 |
| `globalState` | 键值对 | 所有工作区 | 可以，需要用 `setKeysForSync` 指定要同步的键 | 记住用户是否看过欢迎页 |
| `storageUri` | 文件（一个目录） | 当前工作区 | 否 | 当前项目的索引、缓存文件 |
| `globalStorageUri` | 文件（一个目录） | 所有工作区 | 否 | 下载的工具、全局缓存 |
| `secrets` | 加密的字符串 | 全局 | 否 | 访问令牌（token）、密码 |

**怎么选？** 按两个问题判断：

1. **是不是敏感信息？** 是的话只能用 `secrets`。**不要把 token、密码存进 `globalState`**，它是明文保存的。
2. **数据大不大？** 少量的配置、状态用键值对（`*State`）；大文件用目录（`*StorageUri`）。

然后再按“只属于当前项目”还是“所有项目通用”，在 workspace 和 global 之间选择。

**用法示例：**

```ts
// 键值对：读写 workspaceState / globalState
await context.globalState.update('lastOpened', Date.now());   // 写入（返回 Promise）
const last = context.globalState.get<number>('lastOpened');    // 读取，没有值时返回 undefined
const count = context.globalState.get<number>('count', 0);     // 第二个参数是默认值

// 机密信息：读写 secrets（全部是异步方法）
await context.secrets.store('apiToken', 'xxxxxx');
const token = await context.secrets.get('apiToken');
await context.secrets.delete('apiToken');

// 文件：写入 globalStorageUri 目录
// 注意：这个目录不一定已经存在，写入前要先创建
await vscode.workspace.fs.createDirectory(context.globalStorageUri);
const fileUri = vscode.Uri.joinPath(context.globalStorageUri, 'cache.json');
await vscode.workspace.fs.writeFile(fileUri, Buffer.from('{"data": 1}'));
```

两点注意：

- `storageUri` 在**没有打开文件夹或工作区**时（例如只打开了一个单独的文件）是 `undefined`，使用前要先判断。
- 读写文件时推荐用 `vscode.workspace.fs`，而不是 Node.js 的 `fs` 模块。这样扩展在网页版 VS Code、远程开发等环境中也能正常工作。

### setKeysForSync 示例

> 如果你的扩展需要在不同机器之间保留某些用户状态，可以使用 `vscode.ExtensionContext.globalState.setKeysForSync`，把这些状态交给[设置同步（Settings Sync）](https://code.visualstudio.com/docs/configure/settings-sync)。
>
> 可以使用下面的写法：

```ts
// 在 activate 中
const versionKey = 'shown.version';
context.globalState.setKeysForSync([versionKey]);

// 之后，在要显示页面的时候
const currentVersion = context.extension.packageJSON.version;
const lastVersionShown = context.globalState.get(versionKey);
if (isHigher(currentVersion, lastVersionShown)) {
    context.globalState.update(versionKey, currentVersion);
}
```

> 在多台机器之间共享状态，可以通过共享“已关闭”或“已查看”的标记，避免用户多次看到同一个欢迎页或更新说明页。

**这段代码在做什么？** 这是一个常见场景：扩展升级后，给用户显示一次“新版本说明”页面。

1. 在 `globalState` 中记录“上次给用户显示过说明页的版本号”（键名 `shown.version`）；
2. `context.extension.packageJSON.version` 是扩展当前的版本号（就是 `package.json` 里的 `version` 字段）；
3. 如果当前版本比上次显示过的版本新，就显示说明页，并更新记录。

**为什么要 `setKeysForSync`？** 假设用户在公司电脑和家里电脑上都装了你的扩展，并开启了设置同步。如果不同步这个键，用户在公司电脑上看过说明页后，回家打开又会再看到一次。调用 `setKeysForSync` 把这个键加入同步，两台电脑就共享“已经看过”的状态。

**注意：**

- `isHigher` 不是 VS Code API，是示例中假设的一个比较版本号的函数，需要自己实现（或者使用 `semver` 这样的 npm 包）；
- 只有调用了 `setKeysForSync` 的键才会同步，`globalState` 中的其他键仍然只保存在本机；
- 同步只对 `globalState` 有效，`workspaceState` 和 `secrets` 都不会同步。

---

<a id="display-notifications"></a>
## 显示通知（Display Notifications）

> 几乎所有扩展在某些时候都需要向用户展示信息。VS Code 提供了三个 API，用来显示不同严重程度的通知消息：
>
> - [`window.showInformationMessage`](https://code.visualstudio.com/api/references/vscode-api#window.showInformationMessage)
> - [`window.showWarningMessage`](https://code.visualstudio.com/api/references/vscode-api#window.showWarningMessage)
> - [`window.showErrorMessage`](https://code.visualstudio.com/api/references/vscode-api#window.showErrorMessage)

| API | 级别 | 图标 |
|---|---|---|
| `showInformationMessage` | 信息 | 蓝色 ℹ |
| `showWarningMessage` | 警告 | 黄色 ⚠ |
| `showErrorMessage` | 错误 | 红色 ✖ |

**通知还可以带按钮**，并且能知道用户点了哪个：

```ts
const choice = await vscode.window.showWarningMessage(
  '配置文件不存在，是否创建？',
  '创建',    // 按钮 1
  '取消'     // 按钮 2
);

if (choice === '创建') {
  // 用户点了“创建”
}
// 用户点了“取消”或者直接关闭通知时，choice 是 undefined 或 '取消'
```

**模态对话框：** 对于必须让用户确认的操作（比如删除），可以加上 `{ modal: true }`，显示成一个必须处理的对话框：

```ts
const answer = await vscode.window.showWarningMessage(
  '确定要删除所有缓存吗？',
  { modal: true },
  '删除'
);
```

按照 UX 规范，通知会打扰用户，**不要频繁弹出**。只是想记录运行信息的，应该写到下面介绍的输出通道里。

---

<a id="quick-pick"></a>
## 快速选择（Quick Pick）

> 使用 [`vscode.QuickPick`](https://code.visualstudio.com/api/references/vscode-api#QuickPick) API，你可以很方便地收集用户输入，或者让用户从多个选项中做出选择。[QuickInput 示例](https://github.com/microsoft/vscode-extension-samples/tree/main/quickinput-sample)演示了这个 API。

快速选择就是在窗口顶部弹出的那个输入框和下拉列表，命令面板本身就是一个快速选择。常用的有两个简单版本：

```ts
// 1. 从列表中选择一项
const fruit = await vscode.window.showQuickPick(
  ['苹果', '香蕉', '橙子'],
  { placeHolder: '选择一种水果' }
);
// 用户按 Esc 取消时，fruit 是 undefined

// 2. 让用户输入一段文字
const name = await vscode.window.showInputBox({
  prompt: '请输入你的名字',
  validateInput: text => text.trim() ? null : '名字不能为空', // 返回字符串表示校验失败的提示
});
```

| API | 用途 |
|---|---|
| `window.showQuickPick` | 简单的单选或多选（加 `canPickMany: true`） |
| `window.showInputBox` | 简单的文字输入 |
| `window.createQuickPick` | 创建原文提到的 `QuickPick` 对象，可以完全控制：动态更新选项、多步骤向导、自定义按钮等 |

大多数情况下前两个就够用了。需要做“多步骤向导”（比如先选类型、再输入名称）这类复杂交互时，再用 `createQuickPick`，参考原文给出的 QuickInput 示例。

---

<a id="file-picker"></a>
## 文件选择器（File Picker）

> 扩展可以使用 [`window.showOpenDialog`](https://code.visualstudio.com/api/references/vscode-api#window.showOpenDialog) API 打开系统的文件选择器，选择文件或文件夹。

```ts
const uris = await vscode.window.showOpenDialog({
  canSelectFiles: true,       // 可以选文件
  canSelectFolders: false,    // 不能选文件夹
  canSelectMany: false,       // 只能选一个
  openLabel: '导入',          // 确认按钮上的文字
  filters: { 'JSON 文件': ['json'] },  // 只显示 .json 文件
});

if (uris && uris.length > 0) {
  const fileUri = uris[0];    // 返回的是 Uri 数组
}
```

相对应的还有 `window.showSaveDialog`，用来打开“保存文件”对话框，让用户选择保存位置。

---

<a id="output-channel"></a>
## 输出通道（Output Channel）

> 输出面板显示一组 [`OutputChannel`](https://code.visualstudio.com/api/references/vscode-api#OutputChannel)，非常适合用来记录日志。通过 [`window.createOutputChannel`](https://code.visualstudio.com/api/references/vscode-api#window.createOutputChannel) API 就能轻松使用它。

“输出”面板（菜单 `查看 → 输出`）右上角有一个下拉框，可以切换显示不同的“通道”，例如 Git、扩展宿主等。你的扩展也可以创建自己的通道：

```ts
const output = vscode.window.createOutputChannel('My Extension');
context.subscriptions.push(output);  // 它也是 Disposable

output.appendLine('扩展已启动');      // 追加一行
output.show();                        // 打开输出面板并切换到这个通道
```

还可以创建**日志输出通道**，自动带上时间戳和日志级别，用户还能调整日志级别：

```ts
const log = vscode.window.createOutputChannel('My Extension', { log: true });
log.info('普通信息');
log.warn('警告');
log.error('出错了');
```

**输出通道和 `console.log` 的区别：** `console.log` 的内容只有开发时在调试控制台里能看到；扩展发布后，用户那边看不到。输出通道的内容用户可以直接看到，排查问题时可以让用户把日志复制给你。所以正式发布的扩展应该把运行日志写到输出通道里。

---

<a id="progress-api"></a>
## 进度 API（Progress API）

> 你可以使用 [`vscode.Progress`](https://code.visualstudio.com/api/references/vscode-api#Progress) API 向用户报告进度。
>
> 通过 [`ProgressLocation`](https://code.visualstudio.com/api/references/vscode-api#ProgressLocation) 选项，可以把进度显示在不同的位置：
>
> - 通知区域
> - 源代码管理视图
> - VS Code 窗口中的通用进度
>
> [Progress 示例](https://github.com/microsoft/vscode-extension-samples/tree/main/progress-sample)演示了这个 API。

三个位置对应 `ProgressLocation` 的三个值：

| `ProgressLocation` | 显示位置 | 能否显示百分比和文字 |
|---|---|---|
| `Notification` | 右下角的通知 | 能，还可以带“取消”按钮 |
| `SourceControl` | 源代码管理视图的图标上 | 只显示一个转动的指示 |
| `Window` | 状态栏 | 只显示简短的文字和转动的指示 |

实际使用的是 `window.withProgress`，它会把一个 `Progress` 对象传给你的任务函数：

```ts
await vscode.window.withProgress(
  {
    location: vscode.ProgressLocation.Notification,
    title: '正在下载',
    cancellable: true,                 // 显示“取消”按钮
  },
  async (progress, token) => {
    for (let i = 1; i <= 5; i++) {
      if (token.isCancellationRequested) {
        return;                        // 用户点了取消
      }
      // increment 是本次增加的百分比（累加），不是总进度
      progress.report({ increment: 20, message: `第 ${i}/5 个文件` });
      await new Promise(r => setTimeout(r, 1000));  // 模拟耗时操作
    }
  }
);
// 任务函数执行结束（Promise 完成）时，进度提示自动消失
```

**容易弄错的地方：** `increment` 是**增量**。上面的例子每次加 20，5 次后达到 100%。如果每次都传 `increment: 100`，第一次就满了。

---

## 本篇小结

| 需求 | 用什么 |
|---|---|
| 提供一个功能入口 | 命令：`contributes.commands` + `commands.registerCommand` |
| 让用户调整扩展的行为 | 配置：`contributes.configuration` + `workspace.getConfiguration` |
| 给命令配快捷键 | `contributes.keybindings` |
| 把命令放进右键菜单 | `contributes.menus`（键名决定菜单位置） |
| 存少量状态 | `workspaceState` / `globalState`（需要跨机器同步时用 `setKeysForSync`） |
| 存大文件 | `storageUri` / `globalStorageUri`（使用前先创建目录） |
| 存密码、token | `secrets`（加密，不同步） |
| 提示用户 | `showInformationMessage` / `showWarningMessage` / `showErrorMessage` |
| 让用户选择或输入 | `showQuickPick` / `showInputBox` / `createQuickPick` |
| 让用户选择文件 | `showOpenDialog` / `showSaveDialog` |
| 记录日志 | `createOutputChannel` |
| 显示耗时操作的进度 | `withProgress` + `ProgressLocation` |
