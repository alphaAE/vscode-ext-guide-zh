# 状态栏（Status Bar）

> 原文：[Status Bar](https://code.visualstudio.com/api/ux-guidelines/status-bar)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/status-bar.md`（DateApproved: 10/7/2026）

> [状态栏](../extension-capabilities/extending-workbench.md#status-bar-item)位于 VS Code 工作台的底部，显示与你的工作区相关的信息和操作。条目被分为两组：主要的（左侧）和次要的（右侧）。与整个工作区相关的条目（状态、问题 / 警告、同步）放在左侧，次要的或与上下文相关的条目（语言、缩进、反馈）放在右侧。请限制添加的条目数量，因为其他扩展也会向同一个区域做贡献。

![状态栏示例](images/examples/status-bar.png)

| 位置 | 放什么 | 内置的例子 | 代码中的写法 |
|---|---|---|---|
| 左侧（主要） | 与**整个工作区**相关的信息 | Git 分支、同步状态、错误和警告数量 | `StatusBarAlignment.Left` |
| 右侧（次要） | 与**当前文件或上下文**相关的信息 | 行列号、缩进、编码、语言 | `StatusBarAlignment.Right` |

状态栏项的创建方法见 [扩展工作台](../extension-capabilities/extending-workbench.md#status-bar-item)。

**✔️ 应该做**

> - 使用简短的文字标签
> - 只在必要时使用图标
> - 只在比喻清晰时使用图标
> - 把主要的（全局的）条目放在左侧
> - 把次要的（与上下文相关的）条目放在右侧

**❌ 不应该做**

> - 添加自定义的颜色
> - 添加一个以上的图标（除非必要）
> - 添加一个以上的条目（除非必要）

“比喻清晰”的图标是指一看就知道是什么意思的图标，比如 `$(check)` 表示完成、`$(warning)` 表示警告。如果图标的含义需要用户猜，就直接用文字。

---

<a id="status-bar-items"></a>
## 状态栏项（Status Bar Items）

![状态栏项](images/examples/status-bar-item.png)

> *这个示例展示了 GitHub Pull Requests and Issues 扩展贡献的一个条目。它与整个工作区相关，所以被放在左侧。*

<a id="progress-status-bar-item"></a>
### 进度状态栏项（Progress Status Bar item）

> 当需要显示不显眼的进度（在后台进行的进度）时，建议显示一个带有加载图标的状态栏项（还可以加上旋转动画）。如果进度需要提升到引起用户注意的程度，我们建议改用进度通知。

![状态栏中的进度](images/examples/status-bar-progress.png)

> *这个示例展示了一个不显眼的进度状态栏项。*

图标名后面加上 `~spin` 就会旋转：

```ts
item.text = '$(sync~spin) 正在同步';   // 旋转的同步图标
// 或者
item.text = '$(loading~spin) 正在加载';
```

| 进度的重要程度 | 显示方式 |
|---|---|
| 后台进行，用户不需要关心 | 状态栏中的旋转图标（或 `withProgress` 的 `ProgressLocation.Window`） |
| 需要用户知道、可能要等待 | 进度通知（`ProgressLocation.Notification`，见 [通知](./notifications.md)） |

<a id="error-and-warning-status-bar-items"></a>
### 错误和警告状态栏项（Error and Warning Status Bar Items）

> 如果你需要显示一个非常醒目的条目，用于警告或错误，可以把状态栏项配置为使用警告或错误的背景色。鉴于它们在状态栏中的显眼程度，只应把这种模式作为最后的手段，并且只用于特殊情况。

![状态栏中的错误](images/examples/status-bar-error.png)

> *这个示例使用错误状态栏项，显示文件中的一个阻塞性错误。*

![状态栏中的警告](images/examples/status-bar-warning.png)

> *这个示例使用警告状态栏项，显示文件中的一个警告。*

写法是设置 `backgroundColor`。根据当前的类型定义，**只支持这两种颜色**，设置其他颜色不会生效：

```ts
item.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');    // 错误（红色）
item.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');  // 警告（黄色）
```

这就是“不要添加自定义颜色”的另一面：VS Code 只开放了这两种颜色，而且只用于确实需要立即引起注意的情况。

---

<a id="links"></a>
## 链接（Links）

> - [状态栏项 API 参考](https://code.visualstudio.com/api/references/vscode-api#StatusBarItem)
> - [状态栏扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/statusbar-sample)

---

## 本篇小结

| 要点 | 说明 |
|---|---|
| 左右分组 | 全局信息放左边，与当前文件相关的放右边 |
| 数量 | 一个扩展通常只放一个条目 |
| 内容 | 文字简短；图标只在含义清晰时使用，最多一个 |
| 颜色 | 不要自定义；确实需要醒目时，只能用 `statusBarItem.errorBackground` / `warningBackground` |
| 后台进度 | `$(sync~spin)` 这类旋转图标；需要用户注意时改用进度通知 |
