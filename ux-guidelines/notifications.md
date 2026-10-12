# 通知（Notifications）

> 原文：[Notifications](https://code.visualstudio.com/api/ux-guidelines/notifications)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/notifications.md`（DateApproved: 10/7/2026）

> [通知](../extension-capabilities/common-capabilities.md#display-notifications)显示简短的信息，从 VS Code 的右下角弹出。

![通知的示例](images/examples/notification.png)

> 你可以发送三种类型的通知：
>
> - [信息（Information）](https://code.visualstudio.com/api/references/vscode-api#window.showInformationMessage)
> - [警告（Warning）](https://code.visualstudio.com/api/references/vscode-api#window.showWarningMessage)
> - [错误（Error）](https://code.visualstudio.com/api/references/vscode-api#window.showErrorMessage)
>
> 为了尊重用户的注意力，限制发送通知的数量很重要。为了帮助你决定是否应该显示通知，请遵循我们的通知决策树：

[![通知决策树](images/examples/notification-decision-tree.png)](images/examples/notification-decision-tree.png)

决策树的内容（原文的替代文字也描述了这张图）：

```text
需要用户立即输入吗？
├─ 是 → 需要多个步骤吗？
│        ├─ 是 → 显示多步骤的快速选择
│        └─ 否 → 显示模态对话框
└─ 否 → 需要显示进度吗？
         ├─ 是 → 内容的优先级是低还是高？
         │        ├─ 低 → 在状态栏中显示进度
         │        └─ 高 → （进入下面的“是否由用户触发？”）
         └─ 否 → 用户真的需要被提醒吗？
                  ├─ 否 → 什么都不显示，放轻松 😎
                  └─ 是 → 这是由用户触发的吗？
                           ├─ 是 → 显示一条通知（toast）
                           └─ 否 → 找一个合适的时机再显示通知：
                                   不要在启动时、也不要在脱离上下文的时候显示
                                   → 显示一条通知
                           显示通知之后：还需要显示更多的通知吗？
                                   ├─ 否 → 🎉 完成
                                   └─ 是 → 把多条通知合并成一条，并链接到更多详情
```

**这棵决策树的核心思想：通知是最后才考虑的手段。** 能不打扰就不打扰；需要用户输入时用快速选择或对话框；不重要的进度放在状态栏；只有确实需要提醒用户时才弹通知，而且要挑合适的时机、一次只弹一条。

---

<a id="notification-examples"></a>
## 通知示例（Notification examples）

![信息通知](images/examples/notification-info.png)

> *这条通知在用户运行 **Update version**（更新版本）命令之后出现。注意它没有任何额外的操作，纯粹是提供信息的。*

![警告通知](images/examples/notification-warning.png)

> *这个示例指出了一个需要用户输入的功能问题，并显示了用来解决问题的操作。*

![错误通知](images/examples/notification-error.png)

> *这个示例展示了一条失败通知，带有一个用来解决问题的操作。*

| 类型 | 适合 | 是否带操作按钮 |
|---|---|---|
| 信息 | 告知用户某个操作已完成 | 一般不需要 |
| 警告 | 有问题需要用户处理，但不影响继续使用 | 提供解决问题的操作 |
| 错误 | 操作失败 | 提供解决问题的操作（如“重试”“打开设置”） |

带按钮的写法见 [通用能力](../extension-capabilities/common-capabilities.md#display-notifications)。

**✔️ 应该做**

> - 尊重用户的注意力，只在绝对必要时发送通知
> - 为每条通知都添加一个 **Do not show again**（不再显示）选项
> - 一次只显示一条通知

**❌ 不应该做**

> - 发送重复的通知
> - 用于推广
> - 在首次安装时请求反馈
> - 没有可用的操作时显示操作按钮

**“不再显示”的实现：** 用 `globalState` 记住用户的选择（见 [通用能力](../extension-capabilities/common-capabilities.md#data-storage)）：

```ts
const KEY = 'myExt.hideTip';
if (!context.globalState.get(KEY)) {
  const choice = await vscode.window.showInformationMessage('提示：可以用 Ctrl+Alt+H 快速打招呼。', '不再显示');
  if (choice === '不再显示') {
    await context.globalState.update(KEY, true);
  }
}
```

---

<a id="progress-notification"></a>
## 进度通知（Progress notification）

> 当需要在一段不确定的时间内显示进度时（例如设置一个环境），可以使用进度通知。这种全局的进度通知应该作为最后的手段使用，因为进度最好保留在上下文中（在视图或编辑器中）。

**✔️ 应该做**

> - 显示一个查看更多详情（比如日志）的链接
> - 随着设置的进行显示信息（正在初始化、正在构建等）
> - 提供一个取消操作的选项（如果适用）
> - 为超时的情况添加计时器

**❌ 不应该做**

> - 让通知一直处于进行中的状态

![进度通知](images/examples/notification-progress.png)

> *这个示例使用进度通知，显示建立远程连接时所涉及的设置过程，同时还提供了一个指向输出日志的链接（**details**，详情）。*

“进度最好保留在上下文中”：比如视图正在加载，就在视图上显示进度（见 [视图](./views.md#views-with-progress)）；后台的小任务，就在状态栏中显示（见 [状态栏](./status-bar.md#progress-status-bar-item)）。只有跨越多个区域、用户需要知道的长时间操作，才用进度通知。

这几条“应该做”在 `withProgress` 中的对应写法（见 [通用能力](../extension-capabilities/common-capabilities.md#progress-api)）：

| 规则 | 写法 |
|---|---|
| 随进度显示信息 | `progress.report({ message: '正在构建……' })` |
| 提供取消 | `cancellable: true`，并检查 `token.isCancellationRequested` |
| 链接到详情 | `message` 中放一个指向输出通道的命令链接，或者在完成 / 失败后的通知中提供“查看日志”按钮 |
| 超时处理 | 自己设一个计时器，超时就结束任务并报错，**不要让进度一直转下去** |

---

<a id="modal-dialog"></a>
## 模态对话框（Modal dialog）

> 当你需要用户立即对某个操作做出输入时，可以选择显示一个模态对话框。使用这个界面元素时要谨慎，因为在模态对话框被关闭之前，它会阻止用户与对话框以外的内容进行交互。

![模态对话框](images/examples/save-ai-generated-changes-dialog.png)

> *这个对话框在移动一个 JavaScript/TypeScript 文件后出现，询问是否更新其他文件中的 import 语句。*

（原文的这句说明与截图内容不符。截图实际是询问“是否保存 GitHub Copilot 在 index.html 中所做的更改？”的对话框，说明文字为“AI 生成的更改可能不正确，应在保存前进行检查”，左下角有一个“始终保存 AI 生成的更改，不再询问”的复选框，右下角是“保存”和“取消”按钮。这张截图恰好体现了下面“用复选框记住用户的选择”这条建议。）

**✔️ 应该做**

> - 只在需要用户立即交互时使用模态对话框
> - 在合适的地方，提供一个避免重复确认的操作（*始终* / *从不*）
> - 考虑使用一个复选框来记住用户的选择

**❌ 不应该做**

> - 用模态对话框确认多个步骤
> - 用模态对话框显示不需要用户做出操作的消息
> - 为不是由用户明确发起的操作显示模态对话框

模态对话框的写法是在通知中加上 `{ modal: true }`（见 [通用能力](../extension-capabilities/common-capabilities.md#display-notifications)）：

```ts
const answer = await vscode.window.showWarningMessage(
  '确定要删除这 12 个文件吗？',
  { modal: true, detail: '此操作无法撤销。' },
  '删除'
);
```

| 用模态对话框 | 不要用模态对话框 |
|---|---|
| 用户主动执行了删除、覆盖等不可撤销的操作，需要确认 | 只是告知一条消息（用普通通知） |
| | 需要多个步骤的输入（用多步骤快速选择，见 [快速选择](./quick-picks.md#multiple-steps)） |
| | 扩展自己在后台发起的操作（用户没做任何事，突然弹出一个必须处理的对话框） |

---

<a id="links"></a>
## 链接（Links）

> - [Hello World 扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-sample)
> - [通知扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/notifications-sample)

---

## 本篇小结

| 要点 | 说明 |
|---|---|
| 先走决策树 | 很多情况下根本不需要通知 |
| 普通通知 | 只在必要时发；一次一条；加“不再显示”；没有操作就不放按钮；不用于推广、不在首次安装时要反馈 |
| 进度通知 | 最后的手段；显示阶段信息、提供取消和日志链接、处理超时 |
| 模态对话框 | 只用于用户发起、需要立即确认的操作；提供“始终 / 从不”或复选框记住选择 |
