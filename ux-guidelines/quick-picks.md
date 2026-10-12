# 快速选择（Quick Picks）

> 原文：[Quick Picks](https://code.visualstudio.com/api/ux-guidelines/quick-picks)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/quick-picks.md`（DateApproved: 10/7/2026）

> [快速选择](../extension-capabilities/common-capabilities.md#quick-pick)是执行操作、接收用户输入的一种简便方式。在选择一个配置选项、需要筛选内容，或者从一个条目列表中挑选时，它很有帮助。

![快速选择示例](images/examples/quick-pick.png)

**✔️ 应该做**

> - 为清晰的比喻使用图标
> - 使用经过斟酌的图标，让条目更清晰，并帮助区分不同的条目
> - 用 description 显示当前的条目（如果适用）
> - 用 detail 提供（简短的）额外上下文
> - 对一系列基本的输入使用多步骤模式
> - 从列表中挑选时，提供一个创建新条目的选项（如果适用）
> - 为多步骤的快速选择使用标题
> - 为没有文本输入的快速选择使用标题
> - 为要求输入文本的快速选择使用标题（用占位文字显示提示或示例）
> - 为带有全局按钮（例如刷新图标）的快速选择使用标题

**❌ 不应该做**

> - 重复已有的功能
> - 在占位文字本身就能说明用途时使用标题
> - 使用没有占位文字的输入框

**一个快速选择条目（`QuickPickItem`）的各个部分：**

```ts
const items: vscode.QuickPickItem[] = [
  {
    label: '$(repo) vscode',                 // 主要文字，可以带图标
    description: '当前',                      // 显示在 label 右侧的灰色文字
    detail: 'github.com/microsoft/vscode'    // 显示在下一行的说明文字
  },
  { label: '$(add) 新建仓库……' }              // “创建新条目”的选项
];

const picked = await vscode.window.showQuickPick(items, {
  title: '选择仓库',                         // 标题栏
  placeHolder: '输入名称进行筛选'            // 输入框中的占位文字
});
```

| 部分 | 规范中的用法 |
|---|---|
| `label` 中的图标 | 只在比喻清晰、能帮助区分条目时使用 |
| `description` | 标出“当前”的那一项（比如当前选中的分支、当前使用的配置） |
| `detail` | 简短的额外说明 |
| `title` | 多步骤、没有输入框、有全局按钮时使用；如果和占位文字说的是一回事，就不要重复 |
| `placeHolder` | 输入框**一定要有**占位文字，给出提示或示例 |

---

<a id="multiple-steps"></a>
## 多个步骤（Multiple steps）

> 快速选择可以被配置成多个步骤。当你需要在一个流程中获取几个相关但彼此独立的选择时，就使用这种方式。避免在步骤很多的长流程中使用快速选择，它们并不适合作为向导（wizard）或类似的复杂体验。

![多步骤快速选择示例](images/examples/quick-pick-multi-step.png)

> *注意快速选择标题中的 “1/3” 文字，它表示流程中的当前步骤和总步骤数。*

多步骤快速选择要用 `window.createQuickPick()` 创建，通过 `step` 和 `totalSteps` 属性在标题中显示“1/3”（完整写法见 [QuickInput 示例](https://github.com/microsoft/vscode-extension-samples/tree/main/quickinput-sample)）：

```ts
const qp = vscode.window.createQuickPick();
qp.title = '创建项目';
qp.step = 1;           // 当前第 1 步
qp.totalSteps = 3;     // 共 3 步 → 标题显示 “创建项目 (1/3)”
```

**“不适合作为向导”**：如果流程有七八步，或者每一步都有复杂的表单，快速选择的体验就很差（看不到前后步骤、不方便回头修改）。这种情况下应该重新考虑流程设计；[Webview](./webviews.md) 的规范同样不建议用 Webview 做向导。

---

<a id="multiple-selections"></a>
## 多选（Multiple selections）

> 对于需要在一个步骤中选出的、密切相关的多个选项，使用多选快速选择。

![多选快速选择示例](images/examples/quick-pick-multi-select.png)

写法是 `showQuickPick(items, { canPickMany: true })`，返回值是选中条目的数组。

---

<a id="title"></a>
## 标题（Title）

> 快速选择还可以配置为在主输入框和选择界面的上方显示一个标题栏。当用户需要更多的上下文来做出选择时，就使用标题。避免使用与快速选择输入框中的占位文字相同的文字作为标题。

![带标题的快速选择示例](images/examples/quick-pick-title.png)

---

<a id="using-separators"></a>
## 使用分隔符（Using separators）

> 可以用快速选择的分隔符，把快速选择的条目分成清晰的几个部分。分隔符带有一条分隔线和一个标签，可以清楚地显示各个部分。如果扩展的快速选择包含多组明显不同的选项，就使用分隔符。

![带分隔符的快速选择](images/examples/quick-pick-separators.png)

分隔符也是一个条目，只是把 `kind` 设为 `Separator`：

```ts
const items: vscode.QuickPickItem[] = [
  { label: '最近使用', kind: vscode.QuickPickItemKind.Separator },
  { label: 'project-a' },
  { label: 'project-b' },
  { label: '全部项目', kind: vscode.QuickPickItemKind.Separator },
  { label: 'project-c' },
];
```

---

<a id="links"></a>
## 链接（Links）

> - [快速选择 API 参考](https://code.visualstudio.com/api/references/vscode-api#QuickPick)
> - [快速选择条目 API 参考](https://code.visualstudio.com/api/references/vscode-api#QuickPickItem)
> - [快速选择扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/quickinput-sample)

---

## 本篇小结

| 要点 | 说明 |
|---|---|
| 条目 | `label`（可带图标）、`description`（标出当前项）、`detail`（简短说明）；可加“新建……”选项 |
| 标题与占位文字 | 输入框必须有占位文字；多步骤、无输入框、有全局按钮时加标题；两者不要重复 |
| 多步骤 | `createQuickPick` + `step` / `totalSteps`；步骤不要太多，不要当向导用 |
| 多选 | `canPickMany: true` |
| 分隔符 | `kind: QuickPickItemKind.Separator` |
