# 工作区信任扩展指南（Workspace Trust Extension Guide）

> 原文：[Workspace Trust Extension Guide](https://code.visualstudio.com/api/extension-guides/workspace-trust)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/workspace-trust.md`（DateApproved: 10/7/2026）

---

<a id="what-is-workspace-trust"></a>
## 什么是工作区信任？（What is Workspace Trust?）

> [工作区信任](https://code.visualstudio.com/docs/editing/workspaces/workspace-trust)是一项由安全风险推动的功能：用户在 VS Code 中打开一个工作区时，可能会意外地执行其中的代码。例如，一个语言扩展为了提供功能，可能会执行当前加载的工作区中的代码。在这种情况下，用户应该信任工作区的内容不是恶意的。工作区信任把这个决定集中交给 VS Code 处理，并支持一种[受限模式（Restricted Mode）](https://code.visualstudio.com/docs/editing/workspaces/workspace-trust#restricted-mode)来防止代码被自动执行，这样扩展作者就不必自己去处理这套基础设施。VS Code 提供了静态声明和 API 支持，让扩展可以快速接入，而无需在各个扩展之间重复编写代码。

**为什么需要工作区信任？** 设想你从网上下载了一个陌生的项目，用 VS Code 打开它。即使你什么都没点，一些扩展也可能在后台执行项目中的代码：

- 语言扩展加载项目 `node_modules` 中的工具（比如项目自带的 ESLint 插件）；
- 扩展读取项目的 `.vscode/settings.json`，其中某个设置指定了“要执行的程序路径”，而这个路径指向项目里的一个恶意脚本。

工作区信任就是为了防止这种情况。打开一个新的文件夹时，VS Code 会弹窗询问“是否信任此文件夹中的文件的作者？”：

```text
信任   → 正常模式：所有扩展正常工作
不信任 → 受限模式：只能浏览代码；可能执行代码的功能会被禁用
```

**扩展作者要做的，就是告诉 VS Code：我的扩展在受限模式下能不能用、哪些功能要禁用。**

---

<a id="onboarding"></a>
## 接入（Onboarding）

<a id="static-declarations"></a>
### 静态声明（Static declarations）

> 在扩展的 `package.json` 中，VS Code 支持以下新的 `capabilities` 属性 `untrustedWorkspaces`：

```typescript
capabilities:
  untrustedWorkspaces:
    { supported: true } |
    { supported: false, description: string } |
    { supported: 'limited', description: string, restrictedConfigurations?: string[] }
```

上面是类型描述的写法，实际写在 `package.json` 中是这样的：

```json
{
  "capabilities": {
    "untrustedWorkspaces": {
      "supported": "limited",
      "description": "在受限模式下，不会执行项目中的格式化工具。",
      "restrictedConfigurations": ["myExtension.formatterPath"]
    }
  }
}
```

> 对于 `supported` 属性，接受以下值：

| `supported` | 含义 | 受限模式下扩展的状态 |
|---|---|---|
| `true` | 扩展在受限模式下完全受支持，因为它的任何功能都不需要工作区信任 | 和以前完全一样地启用 |
| `false` | 扩展在受限模式下不受支持，因为没有工作区信任它就无法工作 | 保持禁用，直到授予工作区信任 |
| `'limited'` | 扩展的部分功能在受限模式下受支持。对信任敏感的功能应该禁用，直到授予工作区信任。扩展可以使用 VS Code API 隐藏或禁用这些功能。可以通过 `restrictedConfigurations` 属性，让工作区设置自动受信任状态的控制 | 启用，但部分功能需要扩展自己控制 |

> 对于 `description` 属性，必须提供一段说明为什么需要信任的描述，帮助用户了解哪些功能会被禁用，或者在授予或拒绝工作区信任之前应该检查哪些内容。如果 `supported` 设为 `true`，这个属性会被忽略。
>
> `description` 属性的值应该添加到 `package.nls.json` 中，然后在 `package.json` 文件中引用，以支持本地化。

`package.json` 中的文字可以通过 `%键名%` 的写法引用 `package.nls.json` 中的文字，再为不同语言提供 `package.nls.zh-cn.json` 等文件，实现多语言：

```json
// package.json
"description": "%untrustedWorkspaces.description%"
```

```json
// package.nls.json
{ "untrustedWorkspaces.description": "In Restricted Mode, the formatter from the workspace will not run." }
```

> `restrictedConfigurations` 属性接收一个配置设置 ID 的数组。对于列出的设置，在不受信任的工作区处于受限模式时，扩展不会获得在工作区中定义的值。

---

<a id="how-to-support-restricted-mode"></a>
## 如何支持受限模式？（How to support Restricted Mode?）

> 为了帮助扩展作者了解哪些内容属于工作区信任的范围、哪些类型的功能在受限模式下是安全的，下面列出了一些需要考虑的问题。

可以按下面的问题逐个判断你的扩展：

```text
扩展有 main 入口吗？
  └─ 没有（纯主题、纯语法高亮）→ 不需要处理，受限模式下照常工作

扩展会用到工作区中的文件（内容或设置）吗？
  └─ 不会 → 大概率不需要信任，可以声明 supported: true

扩展会把工作区中的内容当作代码执行吗？
  └─ 会 → 需要信任

扩展会读取工作区设置，并据此决定执行什么吗？
  └─ 会 → 把这些设置列入 restrictedConfigurations
```

<a id="does-my-extension-have-a-main-entry-point"></a>
### 我的扩展有 main 入口吗？（Does my extension have a main entry point?）

> 如果扩展没有 `main` 入口（例如主题和语言语法），这个扩展就不需要工作区信任。对于这类扩展，扩展作者无需采取任何行动，因为无论工作区是否受信任，它们都会继续正常工作。

没有 `main` 就意味着扩展中没有任何代码会被执行，只有 `package.json` 中的静态声明，所以不存在安全风险。

<a id="does-my-extension-rely-on-files-in-the-opened-workspace-to-provide-features"></a>
### 我的扩展是否依赖打开的工作区中的文件来提供功能？（Does my extension rely on files in the opened workspace to provide features?）

> 这可能是指可以由工作区设置的配置，也可能是工作区中实际的代码。如果扩展从不使用工作区中的任何内容，它很可能不需要信任。否则，请看看其他几个问题。

<a id="does-my-extension-treat-any-contents-of-the-workspace-as-code"></a>
### 我的扩展是否把工作区中的任何内容当作代码对待？（Does my extension treat any contents of the workspace as code?）

> 最常见的例子是使用项目的工作区依赖，比如存放在本地工作区中的 Node.js 模块。一个恶意的工作区可能会提交一个被篡改过的模块版本。因此，这对用户和扩展来说都是一个安全风险。此外，扩展可能依赖 JavaScript 或其他配置文件来控制扩展或其他模块的行为。还有很多其他的例子，比如执行一个打开的代码文件来获取它的输出，用于报告错误。

常见的需要信任的行为：

| 行为 | 风险 |
|---|---|
| `require` 工作区 `node_modules` 中的模块 | 模块可能被篡改 |
| 加载工作区中的配置文件（如 `.eslintrc.js`、`webpack.config.js`） | `.js` 配置文件本身就是可执行的代码 |
| 运行工作区中的脚本，获取结果 | 脚本可以做任何事 |
| 调用工作区中自带的可执行程序 | 同上 |

<a id="does-my-extension-use-settings-that-determine-code-execution-that-can-be-defined-in-the-workspace"></a>
### 我的扩展是否使用了可以在工作区中定义、并决定代码执行的设置？（Does my extension use settings that determine code execution that can be defined in the workspace?）

> 你的扩展可能把设置值作为参数，传给扩展执行的某个命令行工具。如果这些设置被一个恶意的工作区覆盖了，它们就可能被用作攻击你的扩展的手段。另一方面，如果设置的值只是用来检测某些条件，那么它可能不是安全风险，也就不需要工作区信任。例如，一个扩展可能会检查首选 shell 设置的值是 `bash` 还是 `pwsh`，来决定显示哪份文档。下面的[配置（设置）](#configurations-settings)一节提供了关于设置的指导，帮助你为扩展找到最佳的配置。

**设置的“层级”：** VS Code 的设置可以写在几个地方，后面的覆盖前面的：

```text
默认值 → 用户设置（你自己电脑上的 settings.json）→ 工作区设置（项目中的 .vscode/settings.json）
```

工作区设置跟着项目走，**下载陌生项目时，它的作者可以在里面写任何东西**。所以像 `"myExtension.formatterPath": "./evil.sh"` 这样的工作区设置，就是一个攻击入口。而如果设置只是用来比较、判断（比如“是 bash 还是 pwsh”），即使被改了也不会执行任何东西，就没有风险。

> 这并不是一份可能需要工作区信任的情况的完整列表。随着我们审查更多的扩展，我们会更新这份列表。考虑工作区信任时，可以参考这份列表，想想你的扩展是否有类似的行为。

<a id="what-if-i-dont-make-changes-to-my-extension"></a>
### 如果我不修改我的扩展会怎样？（What if I don't make changes to my extension?）

> 如上所述，一个没有在 `package.json` 中做任何贡献的扩展，会被视为不支持工作区信任。当工作区处于受限模式时，它会被禁用，并且用户会收到通知，告知某些扩展由于工作区信任而无法工作。这种措施对用户来说是最注重安全的做法。尽管这是默认行为，但最佳实践仍然是设置一个合适的值，表明作为扩展作者，你已经努力保护用户和你的扩展免受恶意工作区内容的侵害。

也就是说：**不声明 = `supported: false`**。即使你的扩展完全安全，不声明的话，它在受限模式下也会被禁用。所以无论如何都应该明确地声明一个值。

---

<a id="workspace-trust-api"></a>
## 工作区信任 API（Workspace Trust API）

> 如上所述，使用 API 的第一步，是在 `package.json` 中添加静态声明。最简单的接入方式，是为 `supported` 属性使用 `false` 值。再说一次，即使你什么都不做，这也是默认的行为，但这是一个很好的信号，告诉用户你是经过深思熟虑才做出这个选择的。在这种情况下，你的扩展不需要做任何其他的事情。在授予信任之前，它不会被激活，这样你的扩展就能知道，它是在用户同意的情况下执行的。不过，如果你的扩展只有一部分功能需要信任，这可能不是最好的选择。
>
> 如果扩展希望根据工作区信任来控制它的功能，应该为 `supported` 属性使用 `'limited'` 值，VS Code 提供了以下 API：

```typescript
export namespace workspace {
  /**
    * 为 true 时，表示用户已经明确信任了工作区的内容。
    */
  export const isTrusted: boolean;

  /**
    * 当前工作区被信任时触发的事件。
    */
  export const onDidGrantWorkspaceTrust: Event<void>;
}
```

> 使用 `isTrusted` 属性判断当前工作区是否受信任，使用 `onDidGrantWorkspaceTrust` 事件监听工作区何时被授予信任。你可以用这个 API 阻止特定的代码路径，并在工作区被信任后执行必要的注册。
>
> VS Code 还提供了一个上下文键 `isWorkspaceTrusted`，可以在 `when` 子句中使用，如下文所述。

一个 `'limited'` 扩展的典型写法：

```ts
export function activate(context: vscode.ExtensionContext) {
  // 安全的功能：始终注册
  registerSafeFeatures(context);

  if (vscode.workspace.isTrusted) {
    // 已信任：直接注册需要信任的功能
    registerTrustedFeatures(context);
  } else {
    // 未信任：等用户授予信任后再注册
    context.subscriptions.push(
      vscode.workspace.onDidGrantWorkspaceTrust(() => registerTrustedFeatures(context))
    );
  }
}
```

注意只有“被授予信任”的事件，没有“被撤销信任”的事件：用户撤销信任时，VS Code 会要求重新加载窗口，所以扩展会重新激活，不需要处理这种情况。

---

<a id="contribution-points"></a>
## 贡献点（Contribution points）

<a id="commands-views-or-other-ui"></a>
### 命令、视图或其他界面（Commands, views, or other UI）

> 当用户没有信任工作区时，他们将在受限模式下操作，功能有限，主要用于浏览代码。你在受限模式下禁用的任何功能，都应该对用户隐藏。这可以通过 [when 子句上下文](../references/when-clause-contexts.md)和上下文键 `isWorkspaceTrusted` 来实现。即使命令没有显示在界面中，它仍然可以被调用，所以你应该在扩展代码中，根据上面的 API 阻止命令的执行，或者不注册这个命令。

**两层防护缺一不可：**

```json
// 第一层：界面上隐藏（package.json）
"menus": {
  "commandPalette": [
    { "command": "myExtension.runFormatter", "when": "isWorkspaceTrusted" }
  ]
}
```

```ts
// 第二层：代码中拦截（即使界面隐藏了，其他扩展或快捷键仍可能调用它）
vscode.commands.registerCommand('myExtension.runFormatter', () => {
  if (!vscode.workspace.isTrusted) {
    vscode.window.showWarningMessage('受限模式下无法运行格式化工具。');
    return;
  }
  // ……
});
```

`when` 子句只控制“看不看得见”，不能阻止命令被调用，这一点在 [命令指南](./command.md) 中也提到过。

<a id="configurations-settings"></a>
### 配置（设置）（Configurations (settings)）

> 首先，你应该检查你的设置，判断它们是否需要考虑信任。如上所述，工作区可能为你的扩展使用的某个设置定义了一个对用户有害的值。如果你找到了易受攻击的设置，就应该为 `supported` 属性使用 `'limited'`，并在 `restrictedConfigurations` 数组中列出这个设置的 ID。
>
> 当你把一个设置 ID 添加到 `restrictedConfigurations` 数组中后，在受限模式下，VS Code 只会返回这个设置的用户定义的值。这样，你的扩展就不需要做任何额外的代码修改来处理这个设置。当授予信任时，除了工作区信任事件之外，还会触发一个配置变更事件。

`restrictedConfigurations` 的效果：

| 工作区状态 | `getConfiguration().get('myExtension.formatterPath')` 返回 |
|---|---|
| 已信任 | 正常的值（工作区设置优先） |
| 受限模式 | **只考虑默认值和用户设置**，忽略工作区设置中的值 |

这样，扩展代码完全不用改，危险的工作区设置会被 VS Code 自动屏蔽。被授予信任后会触发 `onDidChangeConfiguration`，扩展如果已经在监听配置变化（见 [通用能力](../extension-capabilities/common-capabilities.md#configuration)），就会自动用上工作区的值。

<a id="debug-extensions"></a>
### 调试扩展（Debug extensions）

> VS Code 在受限模式下会阻止调试。因此，调试扩展通常不需要信任，应该为 `supported` 属性选择 `true`。不过，如果你的扩展提供了不属于内置调试流程的其他功能、命令或设置，就应该使用 `'limited'`，并遵循上面的指导。

<a id="task-providers"></a>
### 任务提供者（Task providers）

> 与调试类似，VS Code 在受限模式下会阻止运行任务。如果你的扩展提供了不属于内置任务流程的其他功能、命令或设置，就应该使用 `'limited'` 并遵循上面的指导。否则，可以指定 `supported: true`。

也就是说，调试和任务这两个“会执行代码”的功能，VS Code 已经在受限模式下统一拦截了，[调试器扩展](./debugger-extension.md)和[任务提供者](./task-provider.md)本身不需要再做处理。

---

<a id="testing-workspace-trust"></a>
## 测试工作区信任（Testing Workspace Trust）

> 关于启用和配置工作区信任的详细信息，请参阅[工作区信任用户指南](https://code.visualstudio.com/docs/editor/workspace-trust)。

测试受限模式下的行为时，可以在扩展开发宿主窗口中执行 **Workspaces: Manage Workspace Trust** 命令，切换当前工作区的信任状态。

---

## 本篇小结

| `supported` | 适合 | 扩展要做的事 |
|---|---|---|
| `true` | 不执行工作区中任何代码的扩展；调试、任务扩展 | 无 |
| `false`（也是不声明时的默认值） | 离开信任就完全无法工作的扩展 | 写一段 `description` 说明原因 |
| `'limited'` | 部分功能需要信任 | `description` + `restrictedConfigurations` + 用 API 控制功能 |

```text
API：workspace.isTrusted、workspace.onDidGrantWorkspaceTrust
界面：when 子句中的 isWorkspaceTrusted（只隐藏，不能阻止调用）
代码：命令中再检查 isTrusted
设置：restrictedConfigurations 中的设置，受限模式下自动忽略工作区中的值
```
