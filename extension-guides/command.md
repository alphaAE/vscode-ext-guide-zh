# 命令（Commands）

> 原文：[Commands](https://code.visualstudio.com/api/extension-guides/command)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/command.md`（DateApproved: 10/7/2026）

> 命令用来触发 VS Code 中的操作。如果你曾经[配置过快捷键](https://code.visualstudio.com/docs/getstarted/keybindings)，那你就已经和命令打过交道了。扩展也会用命令来向用户提供功能、绑定到 VS Code 界面中的操作，以及实现内部逻辑。

**核心概念：命令就是“一个字符串 ID + 一个处理函数”。** 例如 `editor.action.addCommentLine` 是 ID，对应的函数会把选中的行注释掉。

VS Code 里的按钮、菜单、快捷键，底层几乎都是在执行某个命令：

```text
命令面板 ─┐
快捷键   ─┤
菜单项   ─┼──→  命令 ID  ──→  处理函数
链接     ─┤
代码调用 ─┘
```

所以“命令”是扩展开发中最基础、也最常用的概念。本篇分三部分：

1. **使用命令**：调用 VS Code 或其他扩展已有的命令；
2. **创建命令**：注册自己的命令，并控制它在界面上的显示和启用；
3. **命名规范**：命令标题怎么写。

---

<a id="using-commands"></a>
## 使用命令（Using Commands）

> VS Code 包含大量[内置命令](../references/commands.md)，可以用来与编辑器交互、控制用户界面或执行后台操作。很多扩展也会把自己的核心功能作为命令公开出来，供用户和其他扩展使用。

也就是说，你的扩展既能调用 VS Code 的内置命令，也能调用其他扩展公开的命令。

<a id="programmatically-executing-a-command"></a>
### 通过代码执行命令（Programmatically executing a command）

> [`vscode.commands.executeCommand`](https://code.visualstudio.com/api/references/vscode-api#commands.executeCommand) API 用于通过代码执行命令。借助它，你可以使用 VS Code 的内置功能，也可以在其他扩展（例如 VS Code 内置的 Git 和 Markdown 扩展）的基础上进行开发。
>
> 例如，`editor.action.addCommentLine` 命令会把当前活动文本编辑器中选中的行注释掉：

```ts
import * as vscode from 'vscode';

function commentLine() {
  // 效果相当于用户按下 Ctrl+K Ctrl+C
  vscode.commands.executeCommand('editor.action.addCommentLine');
}
```

> 有些命令可以接收参数来控制它们的行为，命令也可能返回结果。例如，类似 API 的 `vscode.executeDefinitionProvider` 命令会在文档的指定位置查询定义。它接收一个文档 URI 和一个位置作为参数，并返回一个包含定义列表的 Promise：

```ts
import * as vscode from 'vscode';

async function printDefinitionsForActiveEditor() {
  const activeEditor = vscode.window.activeTextEditor;
  if (!activeEditor) {
    return; // 没有打开的编辑器就直接返回
  }

  // <vscode.Location[]> 是 TypeScript 泛型，声明返回值的类型
  const definitions = await vscode.commands.executeCommand<vscode.Location[]>(
    'vscode.executeDefinitionProvider',
    activeEditor.document.uri,       // 参数 1：哪个文件
    activeEditor.selection.active    // 参数 2：光标所在的位置
  );

  for (const definition of definitions) {
    console.log(definition);
  }
}
```

几点说明：

- `executeCommand` 返回的是一个 Promise（类型是 `Thenable<T>`），需要用 `await` 等待结果。
- 第一个参数是命令 ID，后面的参数会按顺序传给命令的处理函数。
- **“类似 API 的命令”是什么？** `vscode.executeDefinitionProvider` 相当于“跳转到定义”，但它不跳转，而是把定义的位置作为数据返回给你。VS Code 提供了一批这样以 `vscode.execute` 开头的命令，用来以编程方式调用语言功能（查定义、查引用、获取补全项等）。完整列表见 [内置命令](../references/commands.md)。
- 泛型 `<vscode.Location[]>` 只是告诉 TypeScript 返回值的类型，VS Code 不会检查它。类型写错了，编译能通过，运行时才会出问题。

> 查找可用的命令：
>
> - [浏览键盘快捷方式](https://code.visualstudio.com/docs/getstarted/keybindings)
> - [查阅 VS Code 内置的高级命令 API](../references/commands.md)

**小技巧：** 打开“键盘快捷方式”面板（`文件 → 首选项 → 键盘快捷方式`，或 `Ctrl+K Ctrl+S`），在任意一项上右键选择“复制命令 ID”，就能得到这个命令的 ID。几乎所有界面上的操作都能在这里找到对应的命令。

<a id="command-uris"></a>
### 命令 URI（Command URIs）

> 命令 URI 是执行指定命令的链接。它们可以作为可点击的链接，用在悬停文本、补全项详情或 Webview 中。
>
> 命令 URI 使用 `command` 协议（scheme），后面跟着命令名称。例如，`editor.action.addCommentLine` 命令的命令 URI 是 `command:editor.action.addCommentLine`。下面是一个悬停提供者，它在当前活动文本编辑器中显示一个链接，点击后会注释掉当前行：

**为什么需要命令 URI？** VS Code 中很多地方显示的是 **Markdown 文本**，例如悬停提示、补全项的文档说明。这些地方只能放文字和链接，没法放一个按钮再绑定 `onClick` 回调。命令 URI 就是用来解决这个问题的：把链接地址写成 `command:命令ID`，用户点击时执行的就不是打开网页，而是这个命令。

格式：

```text
command:命令ID
command:命令ID?参数（JSON 数组，经过 encodeURIComponent 编码）
```

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  vscode.languages.registerHoverProvider(
    'javascript',
    new class implements vscode.HoverProvider {
      provideHover(
        _document: vscode.TextDocument,
        _position: vscode.Position,
        _token: vscode.CancellationToken
      ): vscode.ProviderResult<vscode.Hover> {
        const commentCommandUri = vscode.Uri.parse(`command:editor.action.addCommentLine`);
        const contents = new vscode.MarkdownString(`[Add comment](${commentCommandUri})`);

        // 要在 Markdown 内容中启用命令 URI，必须设置 `isTrusted` 标志。
        // 创建可信的 Markdown 字符串时，一定要对所有输入内容做好清理，
        // 确保只有预期的命令 URI 能被执行
        contents.isTrusted = true;

        return new vscode.Hover(contents);
      }
    }()
  );
}
```

这段代码的效果：在 JavaScript 文件中悬停鼠标，弹出的提示里有一个 “Add comment” 链接，点击就会注释当前行。

代码中的几个写法说明：

- `registerHoverProvider('javascript', ...)`：注册一个悬停提供者，只对 JavaScript 文件生效。悬停提供者属于“编程式语言功能”，详见 [编程式语言功能](../language-extensions/programmatic-language-features.md)。
- `new class implements vscode.HoverProvider { ... }()`：这是 TypeScript 的写法，**定义一个匿名类并立即创建它的实例**，效果等同于传入一个带有 `provideHover` 方法的对象。
- 参数名前面的下划线（`_document`）是一种约定，表示“这个参数没有用到”。
- 示例为了简洁，没有把 `registerHoverProvider` 返回的 Disposable 放进 `context.subscriptions`。实际开发中应该放进去。

**`isTrusted` 为什么是必需的？** 出于安全考虑，VS Code 默认**不执行** Markdown 中的命令链接。否则，任何显示在悬停提示里的内容（比如文件中的一段注释）都可以借此执行命令。设置 `isTrusted` 有两种方式：

```ts
contents.isTrusted = true;                                         // 允许执行所有命令
contents.isTrusted = { enabledCommands: ['editor.action.addCommentLine'] }; // 只允许执行指定的命令（更安全）
```

原文注释中说的“对输入内容做好清理”是指：如果你把**外部内容**（比如文件里的文字、网络请求的结果）拼接进可信的 Markdown 中，别人就可能在里面塞进一个恶意的 `command:` 链接。所以拼接外部内容时，要么对内容进行转义，要么使用第二种方式，只放行指定的命令。

> 传给命令的参数列表，以经过正确 URI 编码的 JSON 数组形式传递。下面的示例使用 `git.stage` 命令，创建一个暂存当前文件的悬停链接：

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  vscode.languages.registerHoverProvider(
    'javascript',
    new class implements vscode.HoverProvider {
      provideHover(
        document: vscode.TextDocument,
        _position: vscode.Position,
        _token: vscode.CancellationToken
      ): vscode.ProviderResult<vscode.Hover> {
        const args = [{ resourceUri: document.uri }];
        const stageCommandUri = vscode.Uri.parse(
          `command:git.stage?${encodeURIComponent(JSON.stringify(args))}`
        );
        const contents = new vscode.MarkdownString(`[Stage file](${stageCommandUri})`);
        contents.isTrusted = true;
        return new vscode.Hover(contents);
      }
    }()
  );
}
```

参数的构造过程分三步：

```text
1. 写成数组          [{ resourceUri: document.uri }]
2. JSON.stringify   '[{"resourceUri":{...}}]'
3. encodeURIComponent → 拼到 ? 后面
```

点击链接时，效果相当于执行了：

```ts
vscode.commands.executeCommand('git.stage', { resourceUri: document.uri });
```

数组中的每一项，依次作为命令的一个参数。

**注意：** 参数经过了 JSON 序列化，所以只能传普通数据（字符串、数字、普通对象、数组），不能传函数或类的实例。上例中的 `document.uri` 是 `Uri` 对象，序列化后会变成一个带有特殊标记的普通对象，VS Code 执行命令时会把这类对象还原成 `Uri`。其他自定义类的实例没有这种待遇，传过去后只剩下普通对象的属性。

> 在创建 [Webview](./webview.md) 时，在 `WebviewOptions` 中设置 `enableCommandUris`，就可以在 Webview 中启用命令 URI。

和 `isTrusted` 类似，`enableCommandUris` 既可以设为 `true`（允许所有命令），也可以设为一个命令 ID 数组（只允许这些命令）。

---

<a id="creating-new-commands"></a>
## 创建新命令（Creating new commands）

<a id="registering-a-command"></a>
### 注册命令（Registering a command）

> [`vscode.commands.registerCommand`](https://code.visualstudio.com/api/references/vscode-api#commands.registerCommand) 把一个命令 ID 绑定到扩展中的一个处理函数上：

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  const command = 'myExtension.sayHello';

  // 处理函数，参数 name 的默认值是 'world'
  const commandHandler = (name: string = 'world') => {
    console.log(`Hello ${name}!!!`);
  };

  context.subscriptions.push(vscode.commands.registerCommand(command, commandHandler));
}
```

> 无论 `myExtension.sayHello` 命令是通过 `executeCommand` 在代码中执行的、从 VS Code 界面中执行的，还是通过快捷键执行的，这个处理函数都会被调用。

`registerCommand` 返回一个 Disposable，放进 `context.subscriptions` 后，扩展停用时命令会被自动注销（见 [扩展的结构](../get-started/extension-anatomy.md)）。

**注意：同一个命令 ID 只能注册一次。** 重复注册会抛出错误，提示命令已经存在。

<a id="command-handler-arguments"></a>
### 命令处理函数的参数（Command handler arguments）

> 用 `registerCommand` 注册的处理函数会收到什么参数，取决于命令是怎么被调用的：

| 调用方式 | 处理函数收到的参数 |
| --- | --- |
| `vscode.commands.executeCommand(commandId, ...args)` | 命令 ID 后面的那些参数，顺序不变。 |
| 命令 URI | URI 查询部分中 JSON 数组的各个元素，见[命令 URI](#command-uris)。 |
| 命令面板 | 对于你的扩展贡献的命令，**没有参数**。当前活动的编辑器或资源管理器中的选择，都不会作为参数传入。 |
| 快捷键 | 如果快捷键配置中指定了 `args`，则把它的值作为**一个**参数传入。`args` 是数组时，会作为一个数组整体传入，而不是拆成多个参数。见[命令参数](https://code.visualstudio.com/docs/configure/keybindings#command-arguments)。 |
| 菜单项 | 菜单提供的上下文，例如文档 URI 或选中的资源。见[菜单命令的参数](../references/contribution-points.md#menu-command-arguments)。 |

**这是最容易踩坑的地方：同一个命令，从不同地方触发时，收到的参数不一样。** 举例说明：

```ts
vscode.commands.registerCommand('myExtension.demo', (...args: unknown[]) => {
  console.log(args);
});
```

| 触发方式 | `args` 的值 |
|---|---|
| `executeCommand('myExtension.demo', 1, 'a')` | `[1, 'a']` |
| 命令面板 | `[]` |
| 快捷键配置了 `"args": { "x": 1 }` | `[{ x: 1 }]` |
| 快捷键配置了 `"args": [1, 2]` | `[[1, 2]]`（一个数组参数，不是两个参数） |
| 在资源管理器中右键某个文件 | `[被点击文件的 Uri, 所有选中文件的 Uri 数组]` |

快捷键的 `args` 写在 `keybindings.json` 或扩展的 `contributes.keybindings` 中：

```jsonc
{
  "key": "ctrl+alt+h",
  "command": "myExtension.sayHello",
  "args": "VS Code"     // 处理函数会收到 "VS Code" 作为参数
}
```

> `when` 子句控制菜单项是否可见，它**不会**把自己用到的上下文键传给命令处理函数。

也就是说，即使菜单项的 `when` 写的是 `resourceLangId == markdown`，处理函数也拿不到“当前语言是 markdown”这个信息。需要的话，要在处理函数里自己获取。

> 如果一个命令同时出现在资源菜单和命令面板中，就要处理没有资源参数的调用。当菜单传入了 URI 时，应该优先使用它：上下文菜单的目标可能和当前活动的编辑器不是同一个。例如，下面这个命令会输出菜单传入的资源 URI，没有传入 URI 时，则退而使用当前活动文本编辑器的 URI：

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('myExtension.logResource', (resource?: unknown) => {
      const uri = resource instanceof vscode.Uri
        ? resource                                       // 从右键菜单触发：使用传入的文件
        : vscode.window.activeTextEditor?.document.uri;  // 从命令面板触发：使用当前打开的文件

      if (!uri) {
        return; // 两种方式都拿不到 URI，就不处理
      }

      console.log(uri.toString());
    })
  );
}
```

- `resource?: unknown`：`?` 表示参数可能不存在；`unknown` 表示类型不确定。所以要先用 `instanceof` 检查，确认是 `Uri` 后再使用。
- “上下文菜单的目标可能和当前活动的编辑器不是同一个”：比如编辑器里打开的是 `a.ts`，用户却在资源管理器中右键了 `b.ts`。这时应该处理 `b.ts`，也就是菜单传入的那个文件。

> [`vscode.commands.registerTextEditorCommand`](https://code.visualstudio.com/api/references/vscode-api#commands.registerTextEditorCommand) 的回调签名不同：它会在命令参数之前，先传入当前活动的 `TextEditor` 和一个 `TextEditorEdit`。它只在有活动的文本编辑器时才会执行。

适合“修改当前文件内容”的命令：

```ts
context.subscriptions.push(
  vscode.commands.registerTextEditorCommand(
    'myExtension.insertHello',
    (editor, edit, ...args) => {
      // editor：当前活动的文本编辑器
      // edit：用来修改文档内容的编辑对象
      // args：命令本身的参数，排在 editor 和 edit 之后
      edit.insert(editor.selection.active, 'Hello');  // 在光标处插入文字
    }
  )
);
```

**注意：** `edit` 对象只能在回调函数**同步执行期间**使用。如果在回调里 `await` 了某个异步操作之后再调用 `edit.insert`，修改不会生效。需要异步修改时，改用 `editor.edit(builder => { ... })`。

<a id="creating-a-user-facing-command"></a>
### 创建面向用户的命令（Creating a user facing command）

> `vscode.commands.registerCommand` 只是把一个命令 ID 绑定到一个处理函数上。要让命令出现在命令面板中、让用户能够找到它，还需要在扩展的 `package.json` 中添加对应的命令贡献（`contribution`）：

```json
{
  "contributes": {
    "commands": [
      {
        "command": "myExtension.sayHello",
        "title": "Say Hello"
      }
    ]
  }
}
```

> `commands` 贡献告诉 VS Code：你的扩展提供了这个命令，并且在这个命令被调用时应该激活扩展；同时，它也让你能够控制命令在界面中的显示方式。创建命令时，请遵循[命令命名规范](#naming-conventions)。

![命令面板中显示了扩展贡献的命令](images/commands/palette.png)

截图中，在命令面板里输入 `say`，就能找到扩展贡献的 “Say Hello” 命令（标题栏显示的是 Extension Development Host，即扩展开发宿主窗口）。

> 现在，当用户第一次通过命令面板或快捷键调用 `myExtension.sayHello` 命令时，扩展会被激活，`registerCommand` 会把 `myExtension.sayHello` 绑定到对应的处理函数上。

**两边的分工：**

| | `extension.ts` 中的 `registerCommand` | `package.json` 中的 `contributes.commands` |
|---|---|---|
| 作用 | 命令**被触发时做什么**（逻辑） | 命令**在界面上叫什么、显示在哪里**（声明） |
| 缺少它会怎样 | 命令面板中能看到命令，但执行时报错“找不到命令” | 命令只能通过代码调用，命令面板中看不到 |

两边的命令 ID 必须完全一致。

> **注意**：面向 1.74.0 之前 VS Code 版本的扩展，必须为所有面向用户的命令显式注册 `onCommand` 激活事件，这样扩展才会被激活，`registerCommand` 才会执行：
>
> ```json
> {
>   "activationEvents": ["onCommand:myExtension.sayHello"]
> }
> ```

1.74 之后，VS Code 会根据 `contributes.commands` 自动生成这个激活事件。是否需要手写，取决于 `package.json` 中 `engines.vscode` 声明的最低版本（见 [扩展的结构](../get-started/extension-anatomy.md)）。

> 内部命令不需要 `onCommand` 激活事件，但满足以下任一条件的命令必须定义它：
>
> - 可以通过命令面板调用。
> - 可以通过快捷键调用。
> - 可以通过 VS Code 界面调用，例如通过编辑器标题栏。
> - 打算作为 API 供其他扩展使用。

**内部命令**是指只在扩展自己的代码里调用的命令。调用它时扩展肯定已经激活了，所以不需要激活事件。而上面四种情况，命令可能在扩展还没激活时就被调用，因此需要激活事件来“唤醒”扩展。（同样，这条规则只针对 1.74 之前的版本；1.74 之后，在 `contributes.commands` 中声明过的命令会自动激活扩展。）

<a id="controlling-when-a-command-shows-up-in-the-command-palette"></a>
### 控制命令何时出现在命令面板中（Controlling when a command shows up in the Command Palette）

> 默认情况下，通过 `package.json` 的 `commands` 部分贡献的所有面向用户的命令，都会显示在命令面板中。但是，很多命令只在特定情况下才有意义，比如当前活动的是某种语言的文本编辑器，或者用户设置了某个配置项。
>
> [`menus.commandPalette`](../references/contribution-points.md#contributes.menus) 贡献点让你可以限制命令何时显示在命令面板中。它接收目标命令的 ID，以及一个控制何时显示该命令的 [when 子句](../references/when-clause-contexts.md)：

```json
{
  "contributes": {
    "menus": {
      "commandPalette": [
        {
          "command": "myExtension.sayHello",
          "when": "editorLangId == markdown"
        }
      ]
    }
  }
}
```

> 现在，`myExtension.sayHello` 命令只有在用户编辑 Markdown 文件时，才会出现在命令面板中。

**when 子句**就是一个条件表达式。VS Code 内置了很多上下文变量（称为“上下文键”），例如：

| 上下文键 | 含义 |
|---|---|
| `editorLangId` | 当前编辑器中文件的语言 ID，如 `markdown`、`typescript` |
| `editorHasSelection` | 编辑器中是否选中了文字 |
| `resourceExtname` | 当前文件的扩展名，如 `.json` |
| `config.xxx` | 某个设置项的值，如 `config.editor.wordWrap` |

表达式支持 `==`、`!=`、`&&`、`||`、`!` 等运算符，例如 `editorLangId == markdown && editorHasSelection`。完整语法和上下文键列表见 [when 子句上下文](../references/when-clause-contexts.md)。

**常用技巧：** 有些命令只想放在右键菜单里，不想出现在命令面板中（比如需要文件参数的命令，从命令面板调用没有意义），可以写成 `"when": "false"`，让它在命令面板中永远不显示。

<a id="enablement-of-commands"></a>
### 命令的启用条件（Enablement of commands）

> 命令支持通过 `enablement` 属性设置启用条件，它的值是一个 [when 子句](../references/when-clause-contexts.md)。启用条件对所有菜单和已注册的快捷键都生效。

`enablement` 写在命令的贡献中：

```json
{
  "contributes": {
    "commands": [
      {
        "command": "myExtension.sayHello",
        "title": "Say Hello",
        "enablement": "editorHasSelection"
      }
    ]
  }
}
```

> **注意**：`enablement` 和菜单项的 `when` 条件在语义上有重叠。后者用来避免菜单中充满被禁用的条目。例如，一个分析 JavaScript 正则表达式的命令，应该在文件是 JavaScript 时**显示**（when），并且只在光标位于正则表达式上时才**启用**（enabled）。`when` 子句通过在其他语言的文件中不显示这个命令，避免菜单变得杂乱。强烈建议避免让菜单变得杂乱。
>
> 最后，显示命令的各种菜单（例如命令面板或上下文菜单）处理启用状态的方式不同。编辑器和资源管理器的上下文菜单会把命令显示为启用或禁用（灰色）状态，而命令面板会把禁用的命令过滤掉。

把两者放在一起对比：

| | 菜单中的 `when` | 命令上的 `enablement` |
|---|---|---|
| 写在哪里 | `contributes.menus` 中的每个菜单项上 | `contributes.commands` 中的命令上 |
| 作用范围 | 只影响**那一个菜单位置** | 影响**所有地方**：所有菜单和快捷键 |
| 条件不满足时 | 不显示 | 上下文菜单中显示为灰色、不能点击；命令面板中不显示；快捷键不生效 |
| 适合 | “这里跟这个命令无关” | “这个命令现在暂时用不了” |

用原文的例子理解：一个分析正则表达式的命令——

- 在 Python 文件里，这个命令完全无关，用 `when` 把它**隐藏**掉，菜单保持简洁；
- 在 JavaScript 文件里，命令是相关的，应该**显示**出来，但光标不在正则表达式上时暂时没法分析，用 `enablement` 让它**变灰**。

<a id="using-a-custom-when-clause-context"></a>
### 使用自定义的 when 子句上下文（Using a custom when clause context）

> 如果你在开发自己的 VS Code 扩展，需要用 `when` 子句上下文来启用或禁用命令、菜单或视图，而现有的上下文键都不能满足需求，那么你可以添加自己的上下文。
>
> 下面第一个例子把键 `myExtension.showMyCommand` 设为 true，你可以在命令的启用条件或 `when` 属性中使用它。第二个例子存储了一个数值，你可以在 `when` 子句中用它检查打开的“酷东西”的数量是否大于 2。

```js
vscode.commands.executeCommand('setContext', 'myExtension.showMyCommand', true);

vscode.commands.executeCommand('setContext', 'myExtension.numberOfCoolOpenThings', 2);
```

然后在 `package.json` 中使用：

```jsonc
"when": "myExtension.showMyCommand"                   // 为 true 时满足
"when": "myExtension.numberOfCoolOpenThings > 2"      // 数值大于 2 时满足
```

**典型用途：** 内置的上下文键只知道编辑器的状态，不知道你的扩展的状态。比如“用户登录后才显示某个命令”：

```ts
async function login() {
  // ……登录逻辑……
  await vscode.commands.executeCommand('setContext', 'myExtension.loggedIn', true);
}
```

```json
"menus": {
  "commandPalette": [
    { "command": "myExtension.logout", "when": "myExtension.loggedIn" }
  ]
}
```

两点注意：

- `setContext` 本身也是一个内置命令，这正好呼应了本篇开头的“用 `executeCommand` 调用内置命令”。
- 上下文键的名字建议以扩展名作为前缀（如 `myExtension.`），避免和其他扩展冲突。上下文的值只保存在内存中，VS Code 重启后需要重新设置，所以一般在 `activate` 中初始化。

---

<a id="naming-conventions"></a>
## 命名规范（Naming conventions）

> 创建命令时，应该遵循以下命名规范：
>
> - 命令标题
>   - 使用标题式大写。四个字母及以下的介词（如 on、to、in、of、with、for）不要大写，除非它是第一个或最后一个单词。
>   - 以动词开头，描述将要执行的操作。
>   - 用名词描述操作的对象。
>   - 标题中不要使用 “command” 这个词。

| 规则 | 好的例子 | 不好的例子 |
|---|---|---|
| 标题式大写 | `Open File in Editor` | `open file in editor` |
| 短介词小写 | `Add Item to List` | `Add Item To List` |
| 以动词开头 | `Format Document` | `Document Formatting` |
| 动词 + 名词 | `Toggle Word Wrap` | `Toggle` |
| 不用 “command” | `Run Tests` | `Run Tests Command` |

这些规范针对的是英文标题。如果你的扩展提供中文界面（通过本地化，参见 [L10N 示例](https://github.com/microsoft/vscode-extension-samples/tree/main/l10n-sample)），中文标题同样建议“动词 + 对象”的形式，例如“格式化文档”“切换自动换行”。

**命令 ID 的命名**原文没有专门规定，但惯例是 `扩展名.动作`，例如 `myExtension.sayHello`，用扩展名作前缀可以避免和其他扩展冲突。

另外，命令还可以设置 `category`（分类），命令面板中会显示成 `分类: 标题` 的形式，例如 `Git: Commit`。同一个扩展的命令使用相同的分类，用户更容易找到：

```json
{ "command": "myExtension.sayHello", "title": "Say Hello", "category": "My Extension" }
```

---

## 本篇小结

```text
命令 = ID + 处理函数

调用已有命令
  ├─ 代码中：executeCommand('id', ...args)（返回 Promise）
  └─ 链接中：command:id?编码后的 JSON 数组   ← 命令 URI，需要 isTrusted / enableCommandUris

创建自己的命令
  ├─ extension.ts：registerCommand 写逻辑（或 registerTextEditorCommand）
  │     └─ 参数随触发方式变化：命令面板无参数、菜单传 Uri、快捷键传 args
  ├─ package.json：contributes.commands 让用户能看到
  ├─ menus.commandPalette + when：控制显示还是隐藏
  ├─ enablement：控制能用还是不能用（菜单中变灰，命令面板中隐藏）
  └─ setContext：自定义 when 子句中使用的上下文键

命名：标题“动词 + 名词”、标题式大写、不用 command；ID 用“扩展名.动作”
```
