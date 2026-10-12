# 贡献点（Contribution Points）

> 原文：[Contribution Points](https://code.visualstudio.com/api/references/contribution-points)
> 源文件：`microsoft/vscode-docs` → `api/references/contribution-points.md`（DateApproved: 10/7/2026）

> **贡献点（Contribution Points）**是你在 `package.json` [扩展清单](./extension-manifest.md)的 `contributes` 字段中所做的一组 JSON 声明。你的扩展通过注册**贡献点**来扩展 Visual Studio Code 中的各种功能。下面是所有可用的**贡献点**的列表：
>
> - [`authentication`](#contributes.authentication)
> - [`breakpoints`](#contributes.breakpoints)
> - [`chatAgents`](#contributes.chatAgents)
> - [`chatInstructions`](#contributes.chatInstructions)
> - [`chatPromptFiles`](#contributes.chatPromptFiles)
> - [`chatSkills`](#contributes.chatSkills)
> - [`colors`](#contributes.colors)
> - [`commands`](#contributes.commands)
> - [`configuration`](#contributes.configuration)
> - [`configurationDefaults`](#contributes.configurationDefaults)
> - [`customEditors`](#contributes.customEditors)
> - [`debuggers`](#contributes.debuggers)
> - [`grammars`](#contributes.grammars)
> - [`icons`](#contributes.icons)
> - [`iconThemes`](#contributes.iconThemes)
> - [`jsonValidation`](#contributes.jsonValidation)
> - [`keybindings`](#contributes.keybindings)
> - [`languages`](#contributes.languages)
> - [`languageModelChatProviders`](#contributes.languageModelChatProviders)
> - [`languageModelTools`](#contributes.languageModelTools)
> - [`menus`](#contributes.menus)
> - [`problemMatchers`](#contributes.problemMatchers)
> - [`problemPatterns`](#contributes.problemPatterns)
> - [`productIconThemes`](#contributes.productIconThemes)
> - [`resourceLabelFormatters`](#contributes.resourceLabelFormatters)
> - [`semanticTokenModifiers`](#contributes.semanticTokenModifiers)
> - [`semanticTokenScopes`](#contributes.semanticTokenScopes)
> - [`semanticTokenTypes`](#contributes.semanticTokenTypes)
> - [`snippets`](#contributes.snippets)
> - [`submenus`](#contributes.submenus)
> - [`taskDefinitions`](#contributes.taskDefinitions)
> - [`terminal`](#contributes.terminal)
> - [`themes`](#contributes.themes)
> - [`typescriptServerPlugins`](#contributes.typescriptServerPlugins)
> - [`views`](#contributes.views)
> - [`viewsContainers`](#contributes.viewsContainers)
> - [`viewsWelcome`](#contributes.viewsWelcome)
> - [`walkthroughs`](#contributes.walkthroughs)

**这是一份按字母顺序排列的参考。** 按用途分类，可以更快地找到需要的贡献点（括号中是本指南中详细讲解它的篇目）：

| 用途 | 贡献点 |
|---|---|
| 命令与交互 | `commands`、`menus`、`submenus`、`keybindings`（[命令](../extension-guides/command.md)、[UX：上下文菜单](../ux-guidelines/context-menus.md)） |
| 设置 | `configuration`、`configurationDefaults` |
| 视图与界面 | `viewsContainers`、`views`、`viewsWelcome`、`walkthroughs`、`customEditors`、`colors`、`icons`、`resourceLabelFormatters`（[树视图](../extension-guides/tree-view.md)、[自定义编辑器](../extension-guides/custom-editors.md)） |
| 语言支持 | `languages`、`grammars`、`snippets`、`jsonValidation`、`semanticTokenTypes`、`semanticTokenModifiers`、`semanticTokenScopes`、`typescriptServerPlugins`（[语言扩展](../language-extensions/overview.md)） |
| 主题 | `themes`、`iconThemes`、`productIconThemes`（[颜色主题](../extension-guides/color-theme.md) 等） |
| 调试与任务 | `debuggers`、`breakpoints`、`taskDefinitions`、`problemMatchers`、`problemPatterns`、`terminal`（[调试器扩展](../extension-guides/debugger-extension.md)、[任务提供者](../extension-guides/task-provider.md)） |
| 身份验证 | `authentication` |
| AI | `languageModelTools`、`languageModelChatProviders`、`chatAgents`、`chatInstructions`、`chatPromptFiles`、`chatSkills`（[AI 扩展](../extension-guides/ai/ai-extensibility-overview.md)） |

**贡献点与 API 的关系：** 贡献点是“静态声明”，VS Code 不需要运行你的代码就能读取它们（比如在命令面板中显示命令名称、在设置界面中显示设置项）；而具体的行为（命令执行什么、树视图显示什么数据）要在扩展激活后通过 API 实现。很多贡献点需要两者配合，例如 `contributes.commands` 声明命令的标题，`vscode.commands.registerCommand` 实现命令的逻辑。

---

<a id="contributes.authentication"></a>
## contributes.authentication

> 贡献一个身份验证提供者。这会为你的提供者设置一个激活事件，并在扩展的功能中显示它。

```json
{
  "contributes": {
    "authentication": [
      {
        "label": "Azure DevOps",
        "id": "azuredevops"
      }
    ]
  }
}
```

（`id` 对应代码中 `vscode.authentication.registerAuthenticationProvider(id, label, provider)` 的第一个参数；其他扩展用 `vscode.authentication.getSession('azuredevops', scopes)` 请求会话时，会触发这个扩展的激活，见 [激活事件](./activation-events.md#onAuthenticationRequest)。“扩展的功能”指扩展详情页的 **Features**（功能贡献）选项卡。）

---

<a id="contributes.breakpoints"></a>
## contributes.breakpoints

> 通常，一个调试器扩展还会有一个 `contributes.breakpoints` 条目，扩展在其中列出允许设置断点的语言文件类型。

```json
{
  "contributes": {
    "breakpoints": [
      {
        "language": "javascript"
      },
      {
        "language": "javascriptreact"
      }
    ]
  }
}
```

没有这个声明，用户在这些语言的文件中点击行号左侧时不会出现断点。详见 [调试器扩展](../extension-guides/debugger-extension.md)。

---

<a id="contributes.chatAgents"></a>
## contributes.chatAgents

> 为 Copilot Chat 贡献[自定义智能体（custom agents）](https://code.visualstudio.com/docs/agent-customization/custom-agents)。自定义智能体是预先配置好的 AI 角色，带有特定的指令和工具限制。使用这个贡献点，把可复用的自定义智能体与你的扩展捆绑在一起，让它们与用户定义的智能体一起出现在智能体下拉列表中。
>
> 每个条目都需要一个 `path`，指向一个相对于扩展根目录的 `.agent.md` 文件。你可以选择指定一个 `when` 子句来有条件地启用这个智能体。智能体的 `name`、`description` 等元数据要写在 `.agent.md` 文件的 frontmatter 中，而不是写在贡献点中。

```json
{
  "contributes": {
    "chatAgents": [
      {
        "path": "./agents/planner.agent.md"
      }
    ]
  }
}
```

<a id="chatagents-properties"></a>
### chatAgents 属性（chatAgents properties）

| 属性 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `path` | `string` | 是 | 相对于扩展根目录的 `.agent.md` 文件路径。路径必须解析到扩展内部的位置。 |
| `when` | `string` | 否 | 一个 [when 子句](./when-clause-contexts.md)条件，为真时这个条目才会启用。 |
| `sessionTypes` | `string[]` | 否 | 应该提供这个智能体的聊天会话类型。 |

> 关于所需的 `.agent.md` 文件格式，包括 `name`、`description`、`tools` 和 `model` 等 frontmatter 字段，请参见 [VS Code 中的自定义智能体](https://code.visualstudio.com/docs/agent-customization/custom-agents)。

“frontmatter” 是 Markdown 文件开头用 `---` 包围的 YAML 元数据块，例如：

```markdown
---
name: planner
description: 先制定计划，再动手修改代码
tools: ['search', 'readFile']
---
你是一个……（智能体的指令正文）
```

**下面四个 `chat*` 贡献点的共同点：** 它们都不需要写代码，只是把一个 Markdown 文件随扩展一起发布，让 Copilot Chat 使用。与 [聊天参与者](../extension-guides/ai/chat.md)（需要写代码处理请求）是不同的扩展方式。

| 贡献点 | 文件 | 作用 |
|---|---|---|
| `chatAgents` | `*.agent.md` | 自定义智能体：一个带有固定指令和工具集的 AI 角色 |
| `chatInstructions` | `*.instructions.md` | 指令：相关时**自动**附加到聊天请求中的规范 |
| `chatPromptFiles` | `*.prompt.md` | 提示文件：用户以斜杠命令的方式**手动**调用的现成提示 |
| `chatSkills` | `SKILL.md`（所在的文件夹） | 技能：包含指令、脚本、资源的文件夹，相关时由 Copilot 加载 |

---

<a id="contributes.chatInstructions"></a>
## contributes.chatInstructions

> 为 Copilot Chat 贡献[指令文件（instructions files）](https://code.visualstudio.com/docs/agent-customization/custom-instructions)。指令文件提供自定义的准则，这些准则会被自动包含在聊天请求中，以引导 Copilot 的行为。使用这个贡献点，把可复用的指令与你的扩展捆绑在一起，例如编码规范、特定框架的准则，或特定领域的规则。
>
> 当用户的聊天请求与指令的使用场景相关时，Copilot 会自动应用贡献的指令。你不需要手动附加它们。
>
> 每个条目都需要一个 `path`，指向一个相对于扩展根目录的 Markdown 文件。你可以选择指定一个 `when` 子句来控制指令何时启用。`name` 和 `description` 元数据要写在 Markdown 文件本身中，而不是写在贡献点中。

```json
{
  "contributes": {
    "chatInstructions": [
      {
        "path": "./prompts/textMateGuidelines.instructions.md"
      }
    ]
  }
}
```

> 你可以使用一个可选的 `when` 子句，根据上下文有条件地启用这些指令：

```json
{
  "contributes": {
    "chatInstructions": [
      {
        "path": "./prompts/textMateGuidelines.instructions.md",
        "when": "resourceExtname == .tmLanguage"
      }
    ]
  }
}
```

<a id="chatinstructions-properties"></a>
### chatInstructions 属性（chatInstructions properties）

| 属性 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `path` | `string` | 是 | 相对于扩展根目录的 Markdown 文件路径。路径必须解析到扩展内部的位置。 |
| `when` | `string` | 否 | 一个 [when 子句](./when-clause-contexts.md)条件，为真时这个条目才会启用。 |

> 要贡献可复用的提示文件，请参见 [`chatPromptFiles`](#contributes.chatPromptFiles) 贡献点。

（示例的场景：一个 TextMate 语法相关的扩展，附带了一份“如何编写 TextMate 语法”的指令，用户编辑 `.tmLanguage` 文件时，向 Copilot 提问就会自动带上这份指令。）

---

<a id="contributes.chatPromptFiles"></a>
## contributes.chatPromptFiles

> 为 Copilot Chat 贡献[提示文件（prompt files）](https://code.visualstudio.com/docs/agent-customization/custom-instructions)。提示文件是可复用的聊天提示，用户可以在聊天中以斜杠命令的方式调用它们。使用这个贡献点，把现成的提示与你的扩展捆绑在一起。
>
> 每个条目都需要一个 `path`，指向一个相对于扩展根目录的 Markdown 文件。你可以选择指定一个 `when` 子句来有条件地启用这个提示。`name` 和 `description` 元数据要写在 Markdown 文件本身中，而不是写在贡献点中。

```json
{
  "contributes": {
    "chatPromptFiles": [
      {
        "path": "./prompts/reviewAndCreateIssue.prompt.md"
      }
    ]
  }
}
```

<a id="chatpromptfiles-properties"></a>
### chatPromptFiles 属性（chatPromptFiles properties）

| 属性 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `path` | `string` | 是 | 相对于扩展根目录的 Markdown 文件路径。路径必须解析到扩展内部的位置。 |
| `when` | `string` | 否 | 一个 [when 子句](./when-clause-contexts.md)条件，为真时这个条目才会启用。 |

> 要贡献可复用的指令文件，请参见 [`chatInstructions`](#contributes.chatInstructions) 贡献点。

（原文中“提示文件”的链接与“指令文件”指向同一个页面 `custom-instructions`，以官方文档的实际位置为准。）

---

<a id="contributes.chatSkills"></a>
## contributes.chatSkills

> 为 Copilot Chat 贡献[智能体技能（Agent Skills）](https://code.visualstudio.com/docs/agent-customization/agent-skills)。智能体技能是由指令、脚本和资源组成的文件夹，Copilot 可以在相关时加载它们来执行专门的任务。使用这个贡献点，把可复用的技能与你的扩展捆绑在一起。
>
> 每个条目都需要一个 `path`，指向一个相对于扩展根目录的 `SKILL.md` 文件。`SKILL.md` 文件必须遵循[智能体技能规范](https://agentskills.io/specification)，并且它的 `name` 字段必须与父目录的名称一致。你可以选择指定一个 `when` 子句来有条件地启用这个技能。

```json
{
  "contributes": {
    "chatSkills": [
      {
        "path": "./skills/my-skill/SKILL.md"
      }
    ]
  }
}
```

<a id="chatskills-properties"></a>
### chatSkills 属性（chatSkills properties）

| 属性 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `path` | `string` | 是 | 相对于扩展根目录的 `SKILL.md` 文件路径。路径必须解析到扩展内部的位置，并且父目录的名称必须与 `SKILL.md` 中的 `name` 字段一致。 |
| `when` | `string` | 否 | 一个 [when 子句](./when-clause-contexts.md)条件，为真时这个条目才会启用。 |

> 关于所需的技能结构和 `SKILL.md` 格式，请参见[从扩展贡献技能](https://code.visualstudio.com/docs/agent-customization/agent-skills#contribute-skills-from-extensions)。

（例如路径是 `./skills/my-skill/SKILL.md`，那么 `SKILL.md` 中必须写 `name: my-skill`。）

---

<a id="contributes.colors"></a>
## contributes.colors

> 贡献新的可主题化的颜色。扩展可以在编辑器装饰器和状态栏中使用这些颜色。定义之后，用户可以在 `workspace.colorCustomization` 设置中自定义这些颜色，用户的主题也可以设置这些颜色的值。

```json
{
  "contributes": {
    "colors": [
      {
        "id": "superstatus.error",
        "description": "Color for error message in the status bar.",
        "defaults": {
          "dark": "errorForeground",
          "light": "errorForeground",
          "highContrast": "#010203",
          "highContrastLight": "#feedc3",
        }
      }
    ]
  }
}
```

> 颜色的默认值可以分别为浅色、深色和高对比度主题定义，可以是对一个已有颜色的引用，也可以是一个[颜色十六进制值](./theme-color.md#color-formats)。
>
> 扩展可以通过 `ThemeColor` API 使用新的和已有的主题颜色：

```ts
const errorColor = new vscode.ThemeColor("superstatus.error");
```

几点说明：

- 原文中的设置名 `workspace.colorCustomization` 有误，正确的是 **`workbench.colorCustomizations`**。
- 示例 JSON 中 `"highContrastLight": "#feedc3",` 后面多了一个逗号，在严格的 JSON 中是不允许的（`package.json` 不允许尾随逗号）。
- `defaults` 中的四个键对应四类主题：`dark`（深色）、`light`（浅色）、`highContrast`（深色高对比度）、`highContrastLight`（浅色高对比度）。值 `"errorForeground"` 是引用 VS Code 已有的颜色 ID（见 [主题颜色参考](./theme-color.md)），这样你的颜色会跟随主题对 `errorForeground` 的定义。
- 描述的意思是“状态栏中错误消息的颜色”。

```ts
// 使用示例：状态栏项的文字颜色
statusBarItem.color = new vscode.ThemeColor('superstatus.error');
// 装饰器中也可以用
vscode.window.createTextEditorDecorationType({ color: new vscode.ThemeColor('superstatus.error') });
```

为什么不直接写死 `#ff0000`？因为写死的颜色在不同的主题下可能看不清。用 `ThemeColor` 引用一个贡献的颜色 ID，主题作者和用户都可以调整它。

---

<a id="contributes.commands"></a>
## contributes.commands

> 为一个命令贡献界面，包括一个标题，以及（可选的）图标、分类和启用状态。启用状态用 [when 子句](./when-clause-contexts.md)表示。默认情况下，命令会显示在**命令面板**（`Ctrl+Shift+P`）中，但它们也可以显示在其他的[菜单](#contributes.menus)中。
>
> 贡献的命令如何呈现，取决于所在的菜单。例如，**命令面板**会给命令加上它们的 `category`（分类）作为前缀，便于分组。不过，**命令面板**不显示图标，也不显示被禁用的命令。另一方面，编辑器上下文菜单会显示被禁用的项，但不显示分类标签。

> **注意**：当一个命令被调用时（通过快捷键、**命令面板**、任何其他菜单，或者以编程方式），VS Code 会发出一个激活事件 `onCommand:${command}`。

> **注意**：使用[产品图标](./icons-in-labels.md#icon-listing)中的图标时，设置 `light` 和 `dark` 会使图标失效。正确的语法是 `"icon": "$(book)"`

<a id="command-example"></a>
### 命令示例（command example）

```json
{
  "contributes": {
    "commands": [
      {
        "command": "extension.sayHello",
        "title": "Hello World",
        "category": "Hello",
        "icon": {
          "light": "path/to/light/icon.svg",
          "dark": "path/to/dark/icon.svg"
        }
      }
    ]
  }
}
```

> 请参见[命令扩展指南](../extension-guides/command.md)，进一步了解如何在 VS Code 扩展中使用命令。

![commands 扩展点示例](images/contribution-points/commands.png)

截图中，命令面板里显示的是 “Hello: Hello World”：分类 `Hello` 作为前缀，冒号后面是标题。

**命令的属性：**

| 属性 | 含义 |
|---|---|
| `command` | 命令 ID，与 `registerCommand` 的第一个参数一致（惯例：`扩展名.动作`） |
| `title` | 显示的标题 |
| `category` | 分类，在命令面板中显示为前缀 |
| `icon` | 图标：`"$(codicon名)"`，或 `{ "light": "浅色主题用的路径", "dark": "深色主题用的路径" }`。用在视图标题栏、编辑器标题栏等显示图标的菜单中 |
| `enablement` | 一个 when 子句，为假时命令被禁用（显示为灰色，无法执行） |
| `shortTitle` | 简短标题，用于空间有限的地方 |

注意区分 `enablement`（命令是否**可用**）和 `menus` 中的 `when`（菜单项是否**显示**），见下文 [menus](#contributes.menus)。

<a id="command-icon-specifications"></a>
### 命令图标规范（Command icon specifications）

> - `Size:`（尺寸）图标应为 16x16，带 1 像素的内边距（图像为 14x14），并且居中。
> - `Color:`（颜色）图标应使用单一颜色。
> - `Format:`（格式）建议图标使用 SVG，不过任何图像文件类型都可以接受。

![命令图标](images/contribution-points/command-icons.png)

截图是几个视图标题栏中的命令图标示例。尽量使用 Codicon（`"$(refresh)"` 等，见 [产品图标参考](./icons-in-labels.md)），这样图标会与 VS Code 的风格一致，并自动适配主题颜色；使用 SVG 时要分别提供浅色和深色两个版本。

---

<a id="contributes.configuration"></a>
## contributes.configuration

> 贡献会公开给用户的设置。用户可以在设置编辑器中设置这些配置选项，或者直接编辑 settings.json 文件。
>
> 这一部分可以是一个单独的对象，表示单个分类的设置；也可以是一个对象数组，表示多个分类的设置。如果有多个分类的设置，设置编辑器会在这个扩展的目录中显示一个子菜单，title 键会被用作子菜单项的名称。

<a id="configuration-example"></a>
### 配置示例（Configuration example）

```json
{
  "contributes": {
    "configuration": {
      "title": "Settings Editor Test Extension",
      "type": "object",
      "properties": {
        "settingsEditorTestExtension.booleanExample": {
          "type": "boolean",
          "default": true,
          "description": "Boolean Example"
        },
        "settingsEditorTestExtension.stringExample": {
          "type": "string",
          "default": "Hello World",
          "description": "String Example"
        }
      }
    }
  }
}
```

![configuration 扩展点示例](images/contribution-points/configuration-2.png)

> 你可以在扩展中使用 `vscode.workspace.getConfiguration('myExtension')` 读取这些值。

**在代码中读取和响应设置（补充）：**

```ts
// 读取：getConfiguration 的参数是设置 ID 的前缀
const config = vscode.workspace.getConfiguration('settingsEditorTestExtension');
const enabled = config.get<boolean>('booleanExample', true);   // 第二个参数是找不到时的默认值

// 修改（写入用户设置）
await config.update('stringExample', 'Hi', vscode.ConfigurationTarget.Global);

// 响应变化
context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(e => {
  if (e.affectsConfiguration('settingsEditorTestExtension.booleanExample')) {
    // 设置变了，重新读取
  }
}));
```

<a id="configuration-schema"></a>
### 配置的架构（Configuration schema）

> 你的配置条目既用于在 JSON 编辑器中编辑设置时提供智能提示，也用于定义它们在设置界面中的显示方式。

![带有编号的设置界面截图](images/contribution-points/settings-ui.png)

截图中的编号对应下文各小节：

| 编号 | 截图中的位置 | 对应的属性 |
|---|---|---|
| 1 | 分类标题 “GitMagic” | [`title`](#title) |
| 2 | 设置的标题 “Blame › Heatmap: Enabled” | [`properties`](#properties) 中的键（设置 ID） |
| 3 | 标题下方的说明文字（带链接） | [`description` / `markdownDescription`](#description--markdowndescription) |
| 4 | 数字输入框 | [`type`](#type)：`number` |
| 5 | 文本输入框 | `type`：`string` |
| 6 | 复选框（说明文字作为复选框的标签） | `type`：`boolean` |
| 7 | 下拉框 | [`enum`](#enum--enumdescriptions--markdownenumdescriptions--enumitemlabels) |
| 8 | “Edit in settings.json” 链接 | 复杂的 `object` / `array` 类型，无法在界面中编辑 |

<a id="title"></a>
#### title

> 分类的 `title` 1️⃣️ 是这个分类所使用的标题。

```json
{
  "configuration": {
    "title": "GitMagic"
  }
}
```

> 对于有多个设置分类的扩展，如果其中一个分类的标题与扩展的显示名称相同，设置界面会把这个分类当作“默认分类”，忽略这个分类的 `order` 字段，并把它的设置放在扩展的主标题下面。
>
> 对于 `title` 和 `displayName` 字段，“Extension”（扩展）、“Configuration”（配置）、“Settings”（设置）这样的词都是多余的。
>
> - ✔ `"title": "GitMagic"`
> - ❌ `"title": "GitMagic Extension"`
> - ❌ `"title": "GitMagic Configuration"`
> - ❌ `"title": "GitMagic Extension Configuration Settings"`

<a id="properties"></a>
#### properties

> 你的 `configuration` 对象中的 `properties` 2️⃣ 会形成一个字典，其中的键是设置 ID，值给出了这个设置的更多信息。虽然一个扩展可以包含多个设置分类，但扩展的每个设置仍然必须有自己唯一的 ID。一个设置 ID 不能是另一个设置 ID 的完整前缀。
>
> 没有显式 `order` 字段的属性，在设置界面中会按字典顺序显示（**不是**它们在清单中列出的顺序）。

“不能是完整前缀”的意思：如果有 `myExt.format` 这个设置，就不能再有 `myExt.format.enabled`，因为在 settings.json 中，前者是一个值，后者要求 `myExt.format` 是一个对象，两者冲突。

<a id="setting-titles"></a>
### 设置的标题（Setting titles）

> 在设置界面中，会使用多个字段为每个设置构造一个显示标题。键中的大写字母用来表示单词的分隔。

<a id="display-titles-for-single-category-and-default-category-configurations"></a>
#### 单分类和默认分类配置的显示标题（Display titles for single-category and default category configurations）

> 如果配置只有一个设置分类，或者分类的标题与扩展的显示名称相同，那么对于这个分类中的设置，设置界面会使用设置 ID 和扩展的 `name` 字段来确定显示标题。
>
> 例如，对于设置 ID `gitMagic.blame.dateFormat` 和扩展名称 `authorName.gitMagic`，因为设置 ID 的前缀与扩展名称的后缀相匹配，所以设置 ID 中的 `gitMagic` 部分会在显示标题中被去掉：“Blame: **Date Format**”。

<a id="display-titles-for-multi-category-configurations"></a>
#### 多分类配置的显示标题（Display titles for multi-category configurations）

> 如果配置有多个设置分类，并且分类的标题与扩展的显示名称不同，那么对于这个分类中的设置，设置界面会使用设置 ID 和分类的 `id` 字段来确定显示标题。
>
> 例如，对于设置 ID `css.completion.completePropertyWithSemicolon` 和分类 ID `css`，因为设置 ID 的前缀与分类 ID 的后缀相匹配，设置 ID 中的 `css` 部分会在设置界面中被去掉，为这个设置生成的标题将是 “Completion: **Complete Property With Semicolon**”。

**标题的生成规则：**

```text
设置 ID：gitMagic.blame.dateFormat
  1. 去掉与扩展名（或分类 id）相同的前缀 gitMagic.  →  blame.dateFormat
  2. 最后一段以外的部分作为“分组前缀”，首字母大写   →  Blame:
  3. 最后一段按大写字母拆分单词、首字母大写        →  Date Format
  结果：Blame: Date Format
```

所以设置 ID 应该用驼峰命名（`dateFormat`），而不是 `date_format` 或 `dateformat`，这样界面上的标题才好看。多分类的写法：

```json
"configuration": [
  { "id": "css", "title": "CSS", "properties": { "css.completion.completePropertyWithSemicolon": { ... } } },
  { "id": "less", "title": "LESS", "order": 2, "properties": { ... } }
]
```

<a id="configuration-property-schema"></a>
### 配置属性的架构（Configuration property schema）

> 配置键是用 [JSON Schema](https://json-schema.org/overview/what-is-jsonschema) 的一个超集来定义的。

<a id="description--markdowndescription"></a>
#### description / markdownDescription

> 你的 `description` 3️⃣ 出现在标题之后、输入框之前，但布尔值例外，对于布尔值，描述被用作复选框的标签。6️⃣

```json
{
  "gitMagic.blame.heatMap.enabled": {
    "description": "Specifies whether to provide a heatmap indicator in the gutter blame annotations"
  }
}
```

> 如果你使用 `markdownDescription` 代替 `description`，你的设置描述会在设置界面中被解析为 Markdown。

```json
{
  "gitMagic.blame.dateFormat": {
    "markdownDescription": "Specifies how to format absolute dates (e.g. using the `${date}` token) in gutter blame annotations. See the [Moment.js docs](https://momentjs.com/docs/#/displaying/format/) for valid formats"
  }
}
```

> 对于 `markdownDescription`，要添加换行或多个段落，请使用字符串 `\n\n` 来分隔段落，而不是只用 `\n`。

（两个描述的意思分别是：“指定是否在行号旁的 blame 注释中提供热力图指示器”、“指定如何格式化 blame 注释中的绝对日期（例如使用 `${date}` 标记）。有效的格式请参见 Moment.js 文档”。描述文字可以通过 `package.nls.json` 本地化：写成 `"%key%"` 的形式，见下文 `scope` 一节中 Git 扩展的例子。）

<a id="type"></a>
#### type

> 类型为 `number` 4️⃣、`string` 5️⃣、`boolean` 6️⃣ 的条目可以直接在设置界面中编辑。

```json
{
  "gitMagic.views.pageItemLimit": {
    "type": "number",
    "default": 20,
    "markdownDescription": "Specifies the number of items to show in each page when paginating a view list. Use 0 to specify no limit"
  }
}
```

> 如果一个字符串设置在配置条目上设置了 `"editPresentation": "multilineText"`，它可以用多行文本输入框来显示。
>
> 对于 `boolean` 条目，`markdownDescription`（如果没有指定 `markdownDescription`，就是 `description`）会被用作复选框旁边的标签。

```json
{
  "gitMagic.blame.compact": {
    "type": "boolean",
    "description": "Specifies whether to compact (deduplicate) matching adjacent gutter blame annotations"
  }
}
```

> 一些 `object` 和 `array` 类型的设置会在设置界面中显示出来。`number`、`string` 或 `boolean` 的简单数组会显示为可编辑的列表。属性类型为 `string`、`number`、`integer` 和 / 或 `boolean` 的对象会显示为可编辑的键值网格。对象设置还应该把 `additionalProperties` 设为 `false`，或者设为一个带有合适 `type` 属性的对象，才能在界面中显示。
>
> 如果一个 `object` 或 `array` 类型的设置还可以包含其他类型，比如嵌套的对象、数组或 null，那么这个值就不会在设置界面中显示，只能通过直接编辑 JSON 来修改。用户会看到一个 **Edit in settings.json**（在 settings.json 中编辑）的链接，如上面的截图所示。8️⃣

| `type` | 设置界面中的显示 |
|---|---|
| `boolean` | 复选框 |
| `number` / `integer` | 数字输入框（`integer` 只允许整数） |
| `string` | 文本输入框；有 `enum` 时为下拉框；`editPresentation: "multilineText"` 时为多行文本框 |
| `string[]` 等简单数组 | 可编辑的列表（可以添加、删除、修改项） |
| 属性都是简单类型的 `object`（并设置了 `additionalProperties`） | 可编辑的键值表格 |
| 其他复杂类型 | “Edit in settings.json” 链接 |

`type` 也可以是数组，表示允许多种类型，例如 `["boolean", "string"]`（见下文 Git 扩展的 `git.autofetch`）。

<a id="order"></a>
#### order

> 分类和分类中的设置都可以使用一个整数类型的 `order` 属性，它指出它们相对于其他分类和 / 或设置应该如何排序。
>
> 如果两个分类都有 `order` 属性，order 数字较小的分类排在前面。如果一个分类没有 `order` 属性，它会出现在有这个属性的分类之后。
>
> 如果同一个分类中的两个设置都有 `order` 属性，order 数字较小的设置排在前面。如果同一个分类中的另一个设置没有 `order` 属性，它会出现在这个分类中有这个属性的设置之后。
>
> 如果两个分类有相同的 `order` 属性值，或者同一个分类中的两个设置有相同的 `order` 属性值，那么它们会在设置界面中按字典顺序递增排列。

<a id="enum--enumdescriptions--markdownenumdescriptions--enumitemlabels"></a>
#### enum / enumDescriptions / markdownEnumDescriptions / enumItemLabels

> 如果你在 `enum` 7️⃣ 属性下提供一个项的数组，设置界面会显示一个包含这些项的下拉菜单。
>
> 你还可以提供一个 `enumDescriptions` 属性，它是一个与 `enum` 属性长度相同的字符串数组。`enumDescriptions` 属性在设置界面中下拉菜单的底部，为每个 `enum` 项提供一段描述。\
> 你也可以使用 `markdownEnumDescriptions` 代替 `enumDescriptions`，你的描述会被解析为 Markdown。`markdownEnumDescriptions` 的优先级高于 `enumDescriptions`。\
> 要在设置界面中自定义下拉选项的名称，你可以使用 `enumItemLabels`。
>
> 示例：

```json
{
  "settingsEditorTestExtension.enumSetting": {
    "type": "string",
    "enum": ["first", "second", "third"],
    "markdownEnumDescriptions": ["The *first* enum", "The *second* enum", "The *third* enum"],
    "enumItemLabels": ["1st", "2nd", "3rd"],
    "default": "first",
    "description": "Example setting with an enum"
  }
}
```

![上面这个枚举设置示例在设置界面中的截图](images/contribution-points/settings-ui-enum-example.png)

三个数组按位置一一对应：

| `enum`（实际保存的值） | `enumItemLabels`（下拉框中显示的名称） | `markdownEnumDescriptions`（选中时下方显示的说明） |
|---|---|---|
| `first` | 1st | The *first* enum |
| `second` | 2nd | The *second* enum |
| `third` | 3rd | The *third* enum |

用户在 settings.json 中写的、代码中读到的，始终是 `enum` 中的值。

<a id="deprecationmessage--markdowndeprecationmessage"></a>
#### deprecationMessage / markdownDeprecationMessage

> 如果你设置了 `deprecationMessage` 或 `markdownDeprecationMessage`，这个设置会带上一条警告下划线，显示你指定的消息。此外，这个设置会在设置界面中被隐藏，除非用户已经配置了它。如果你设置了 `markdownDeprecationMessage`，Markdown 不会在设置的悬停提示或问题视图中渲染。如果你同时设置了这两个属性，`deprecationMessage` 会显示在悬停提示和问题视图中，而 `markdownDeprecationMessage` 会在设置界面中以 Markdown 渲染。
>
> 示例：

```json
{
  "json.colorDecorators.enable": {
    "type": "boolean",
    "description": "Enables or disables color decorators",
    "markdownDeprecationMessage": "**Deprecated**: Please use `#editor.colorDecorators#` instead.",
    "deprecationMessage": "Deprecated: Please use editor.colorDecorators instead."
  }
}
```

（消息的意思是“已弃用：请改用 editor.colorDecorators”。`` `#editor.colorDecorators#` `` 是指向另一个设置的链接写法，见下文 [链接到设置](#linking-to-settings)。重命名设置时，推荐的做法是：保留旧设置并标记弃用，代码中同时读取新旧两个设置（新的优先），过几个版本后再删除旧设置。）

<a id="other-json-schema-properties"></a>
#### 其他 JSON Schema 属性（Other JSON Schema properties）

> 你可以使用任何用于校验的 JSON Schema 属性，来描述对配置值的其他约束：
>
> - `default`：定义属性的默认值
> - `minimum` 和 `maximum`：限制数值
> - `maxLength`、`minLength`：限制字符串的长度
> - `pattern`：把字符串限制为给定的正则表达式
> - `patternErrorMessage`：在模式不匹配时给出一条定制的错误消息。
> - `format`：把字符串限制为常见的格式，例如 `date`、`time`、`ipv4`、`email` 和 `uri`
> - `maxItems`、`minItems`：限制数组的长度
> - `editPresentation`：控制在设置编辑器中，字符串设置显示为单行输入框还是多行文本区域

<a id="unsupported-json-schema-properties"></a>
#### 不支持的 JSON Schema 属性（Unsupported JSON Schema properties）

> 配置部分中不支持的有：
>
> - `$ref` 和 `definition`：配置的架构需要是自包含的，不能假设聚合后的设置 JSON 架构文档是什么样子。
>
> 关于这些以及其他功能的更多细节，请参见 [JSON Schema 参考](https://json-schema.org/overview/what-is-jsonschema)。

<a id="scope"></a>
#### scope

> 一个配置设置可以有以下可能的作用域之一：
>
> - `application` - 适用于所有 VS Code 实例的设置，只能在用户设置中配置。
> - `machine` - 特定于机器的设置，只能在用户设置中，或者只能在远程设置中设置。例如，一个不应该在不同机器之间共享的安装路径。这些设置的值不会被同步。
> - `machine-overridable` - 特定于机器、但可以被工作区或文件夹设置覆盖的设置。这些设置的值不会被同步。
> - `window` - 特定于窗口（实例）的设置，可以在用户、工作区或远程设置中配置。
> - `resource` - 资源设置，适用于文件和文件夹，可以在所有的设置级别中配置，包括文件夹设置。
> - `language-overridable` - 可以在语言级别上覆盖的资源设置。
>
> 配置的作用域决定了一个设置何时可以通过设置编辑器提供给用户，以及这个设置是否适用。如果没有声明 `scope`，默认是 `window`。

| scope | 用户设置 | 远程设置 | 工作区设置 | 文件夹设置 | 语言特定设置 `[lang]` | 同步 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `application` | ✓ | | | | | ✓ |
| `machine` | ✓ | ✓ | | | | ✗ |
| `machine-overridable` | ✓ | ✓ | ✓ | ✓ | | ✗ |
| `window`（默认） | ✓ | ✓ | ✓ | | | ✓ |
| `resource` | ✓ | ✓ | ✓ | ✓ | | ✓ |
| `language-overridable` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

（此表根据上面的说明整理。“文件夹设置”指多根工作区中每个文件夹自己的 `.vscode/settings.json`。）

**怎么选：** 与具体文件相关、不同项目可能不同的设置（如格式化选项）用 `resource`；还希望能按语言单独设置的（如 `editor.tabSize` 这类）用 `language-overridable`；路径类、不应同步到其他机器的用 `machine`；出于安全考虑不允许工作区修改的（例如一个可执行文件的路径，恶意仓库可能会把它改成别的程序）用 `machine` 或 `application`。读取 `resource` 级的设置时，要把资源传给 `getConfiguration`：`vscode.workspace.getConfiguration('myExt', document.uri)`。

> 下面是内置的 Git 扩展中的配置作用域示例：

```json
{
  "contributes": {
    "configuration": {
      "title": "Git",
      "properties": {
        "git.alwaysSignOff": {
          "type": "boolean",
          "scope": "resource",
          "default": false,
          "description": "%config.alwaysSignOff%"
        },
        "git.ignoredRepositories": {
          "type": "array",
          "default": [],
          "scope": "window",
          "description": "%config.ignoredRepositories%"
        },
        "git.autofetch": {
          "type": [
            "boolean",
            "string"
          ],
          "enum": [
            true,
            false,
            "all"
          ],
          "scope": "resource",
          "markdownDescription": "%config.autofetch%",
          "default": false,
          "tags": [
            "usesOnlineServices"
          ]
        }
      }
    }
  }
}
```

> 你可以看到，`git.alwaysSignOff` 具有 `resource` 作用域，可以按用户、工作区或文件夹设置；而具有 `window` 作用域的忽略存储库列表，则更全局地适用于 VS Code 窗口或工作区（可能是多根工作区）。

（`%config.alwaysSignOff%` 这种写法表示从 `package.nls.json` 中读取本地化的文字。`tags` 用于在设置编辑器中按标签筛选，`usesOnlineServices` 表示这个设置涉及在线服务。）

<a id="ignoreSync"></a>
#### ignoreSync

> 你可以把 `ignoreSync` 设为 `true`，防止这个设置与用户的设置一起同步。这对于不是特定于用户的设置很有用。例如，`remoteTunnelAccess.machineName` 设置不是特定于用户的，不应该被同步。请注意，如果你把 `scope` 设为了 `machine` 或 `machine-overridable`，那么无论 `ignoreSync` 的值是什么，这个设置都不会被同步。

```json
{
  "contributes": {
    "configuration": {
      "properties": {
        "remoteTunnelAccess.machineName": {
          "type": "string",
          "default": "",
          "ignoreSync": true
        }
      }
    }
  }
}
```

<a id="linking-to-settings"></a>
#### 链接到设置（Linking to settings）

> 你可以在 Markdown 类型的属性中使用这种特殊的语法：`` `#target.setting.id#` ``，插入一个指向另一个设置的链接，它会在设置界面中显示为一个可点击的链接。这适用于 `markdownDescription`、`markdownEnumDescriptions` 和 `markdownDeprecationMessage`。示例：

```json
  "files.autoSaveDelay": {
    "markdownDescription": "Controls the delay in ms after which a dirty editor is saved automatically. Only applies when `#files.autoSave#` is set to `afterDelay`.",
    // ...
  }
```

> 在设置界面中，它会显示为：

![设置链接示例](images/contribution-points/setting-link.png)

（描述的意思是“控制有未保存更改的编辑器在多少毫秒后自动保存。只有当 `files.autoSave` 设为 `afterDelay` 时才生效”。截图中，`files.autoSave` 显示为可点击的链接 “Files: Auto Save”，点击后跳到那个设置。）

---

<a id="contributes.configurationDefaults"></a>
## contributes.configurationDefaults

> 为其他已注册的配置贡献默认值，覆盖它们原有的默认值。
>
> 下面的例子覆盖了 `files.autoSave` 设置的默认行为，在焦点变化时自动保存文件。

```json
"configurationDefaults": {
      "files.autoSave": "onFocusChange"
}
```

> 你也可以为所提供的语言贡献默认的编辑器配置。例如，下面的代码片段为 `markdown` 语言贡献了默认的编辑器配置：

```json
{
  "contributes": {
    "configurationDefaults": {
      "[markdown]": {
        "editor.wordWrap": "on",
        "editor.quickSuggestions": {
                "comments": "off",
                "strings": "off",
                "other": "off"
        }
      }
    }
  }
}
```

**注意分寸：** 覆盖一个全局设置的默认值（如第一个例子中的 `files.autoSave`）会影响用户使用 VS Code 的所有场景，通常不是一个好主意。更常见、也更合理的用法是第二种：为**你自己贡献的语言**设置语言特定的默认值（`"[mylang]": { ... }`），例如 [语义高亮指南](../language-extensions/semantic-highlight-guide.md#enablement-of-semantic-highlighting) 中为自己的语言开启语义高亮。用户自己的设置始终优先于这些默认值。

---

<a id="contributes.customEditors"></a>
## contributes.customEditors

> `customEditors` 贡献点是你的扩展告诉 VS Code 它所提供的自定义编辑器的方式。例如，VS Code 需要知道你的自定义编辑器适用于哪些类型的文件，以及如何在各种 UI 中识别你的自定义编辑器。
>
> 下面是[自定义编辑器扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/custom-editor-sample)中一个基本的 `customEditor` 贡献：

```json
"contributes": {
  "customEditors": [
    {
      "viewType": "catEdit.catScratch",
      "displayName": "Cat Scratch",
      "selector": [
        {
          "filenamePattern": "*.cscratch"
        }
      ],
      "priority": "default"
    }
  ]
}
```

> `customEditors` 是一个数组，所以你的扩展可以贡献多个自定义编辑器。
>
> - `viewType` - 你的自定义编辑器的唯一标识符。
>
>     VS Code 就是通过它，把 `package.json` 中的自定义编辑器贡献与代码中自定义编辑器的实现联系起来的。它在所有扩展中都必须是唯一的，所以不要使用 `"preview"` 这样通用的 `viewType`，而要确保使用一个对你的扩展来说唯一的值，例如 `"viewType": "myAmazingExtension.svgPreview"`。
>
> - `displayName` - 在 VS Code 的 UI 中标识这个自定义编辑器的名称。
>
>     显示名称会在 VS Code 的 UI 中显示给用户，例如 **View: Reopen with**（用……重新打开）下拉列表中。
>
> - `selector` - 指定自定义编辑器对哪些文件生效。
>
>     `selector` 是一个包含一个或多个 [glob 模式](https://code.visualstudio.com/docs/editor/glob-patterns)的数组。这些 glob 模式会与文件名进行匹配，以确定自定义编辑器能否用于这些文件。像 `*.png` 这样的 `filenamePattern` 会让自定义编辑器对所有的 PNG 文件生效。
>
>     你也可以创建更具体的、匹配文件名或目录名的模式，例如 `**/translations/*.json`。
>
> - `priority` -（可选）指定何时使用这个自定义编辑器。
>
>     `priority` 控制打开一个资源时何时使用自定义编辑器。可能的值有：
>
>   - `"default"` - 尝试为每个与自定义编辑器的 `selector` 匹配的文件使用这个自定义编辑器。如果给定的文件有多个自定义编辑器，用户需要选择想使用哪一个。
>   - `"option"` - 默认不使用这个自定义编辑器，但允许用户切换到它，或者把它配置为默认编辑器。
>
> 你可以在[自定义编辑器](../extension-guides/custom-editors.md)扩展指南中了解更多。

`viewType` 要与代码中 `vscode.window.registerCustomEditorProvider(viewType, provider)` 的第一个参数一致。`priority: "option"` 适合“预览”类的编辑器：文件默认仍用文本编辑器打开，用户可以通过 **Reopen Editor With...** 切换。

---

<a id="contributes.debuggers"></a>
## contributes.debuggers

> 向 VS Code 贡献一个调试器。一个调试器贡献具有以下属性：
>
> - `type` 是一个唯一的 ID，用于在启动配置中标识这个调试器。
> - `label` 是这个调试器在 UI 中对用户可见的名称。
> - `program` 是调试适配器的路径，调试适配器针对真正的调试器或运行时实现了 VS Code 调试协议。
> - `runtime` 用于调试适配器的路径不是一个可执行文件、而需要一个运行时来运行的情况。
> - `configurationAttributes` 是特定于这个调试器的启动配置参数的架构。请注意，不支持 JSON 架构结构 `$ref` 和 `definition`。
> - `initialConfigurations` 列出用于填充初始 launch.json 的启动配置。
> - `configurationSnippets` 列出在编辑 launch.json 时可以通过智能提示获得的启动配置。
> - `variables` 引入替换变量，并把它们绑定到由调试器扩展实现的命令。
> - `languages` 是那些可以把这个调试扩展视为“默认调试器”的语言。

<a id="debugger-example"></a>
### 调试器示例（debugger example）

```json
{
  "contributes": {
    "debuggers": [
      {
        "type": "node",
        "label": "Node Debug",

        "program": "./out/node/nodeDebug.js",
        "runtime": "node",

        "languages": ["javascript", "typescript", "javascriptreact", "typescriptreact"],

        "configurationAttributes": {
          "launch": {
            "required": ["program"],
            "properties": {
              "program": {
                "type": "string",
                "description": "The program to debug."
              }
            }
          }
        },

        "initialConfigurations": [
          {
            "type": "node",
            "request": "launch",
            "name": "Launch Program",
            "program": "${workspaceFolder}/app.js"
          }
        ],

        "configurationSnippets": [
          {
            "label": "Node.js: Attach Configuration",
            "description": "A new configuration for attaching to a running node program.",
            "body": {
              "type": "node",
              "request": "attach",
              "name": "${2:Attach to Port}",
              "port": 9229
            }
          }
        ],

        "variables": {
          "PickProcess": "extension.node-debug.pickNodeProcess"
        }
      }
    ]
  }
}
```

> 关于如何集成一个 `debugger` 的完整讲解，请前往[调试器扩展](../extension-guides/debugger-extension.md)。

`variables` 的用法：用户在 launch.json 中写 `"processId": "${command:PickProcess}"`，启动调试时 VS Code 会执行 `extension.node-debug.pickNodeProcess` 命令（比如弹出一个进程列表让用户选择），用命令的返回值替换这个变量。`configurationSnippets` 中 `${2:Attach to Port}` 是代码片段的占位符语法（见 [代码片段](../language-extensions/snippet-guide.md)）。

---

<a id="contributes.grammars"></a>
## contributes.grammars

> 为一种语言贡献一个 TextMate 语法。你必须提供这个语法所适用的 `language`、语法的 TextMate `scopeName`，以及文件路径。

> **注意**：包含语法的文件可以是 JSON 格式（文件名以 .json 结尾），也可以是 XML plist 格式（所有其他文件）。

<a id="grammar-example"></a>
### 语法示例（grammar example）

```json
{
  "contributes": {
    "grammars": [
      {
        "language": "markdown",
        "scopeName": "text.html.markdown",
        "path": "./syntaxes/markdown.tmLanguage.json",
        "embeddedLanguages": {
          "meta.embedded.block.frontmatter": "yaml"
        }
      }
    ]
  }
}
```

> 请参见[语法高亮指南](../language-extensions/syntax-highlight-guide.md)，进一步了解如何注册与某种语言关联的 TextMate 语法，以获得语法高亮。

![grammars 扩展点示例](images/contribution-points/grammars.png)

`embeddedLanguages` 在这个例子中的作用：Markdown 文件开头 `---` 之间的 frontmatter 部分被当作 YAML 对待（注释、括号匹配等使用 YAML 的规则）。语法贡献的其他可选字段（`injectTo`、`tokenTypes`、`balancedBracketScopes` 等）见 [语法高亮指南](../language-extensions/syntax-highlight-guide.md)。

---

<a id="contributes.icons"></a>
## contributes.icons

> 通过 ID 贡献一个新图标，以及一个默认图标。之后，这个扩展（或任何依赖这个扩展的其他扩展）就可以在任何可以使用 `ThemeIcon` 的地方（`new ThemeIcon("iconId")`）、在 [Markdown 字符串](./icons-in-labels.md#icons-in-labels)中（`$(iconId)`），以及作为某些贡献点中的图标，使用这个图标 ID。

```json
{
  "contributes": {
    "icons": {
      "distro-ubuntu": {
        "description": "Ubuntu icon",
        "default": {
          "fontPath": "./distroicons.woff",
          "fontCharacter": "\\E001"
        }
      },
      "distro-fedora": {
        "description": "Ubuntu icon",
        "default": {
          "fontPath": "./distroicons.woff",
          "fontCharacter": "\\E002"
        }
      }
    }
  }
}
```

（原文中 “Markdown 字符串” 的链接锚点写成了 `#icon-in-labels`，目标标题是 “Icons in labels”，这里改为 `#icons-in-labels`。各字段的含义见 [产品图标参考](./icons-in-labels.md#icon-contribution-point)。）

---

<a id="contributes.iconThemes"></a>
## contributes.iconThemes

> 向 VS Code 贡献一个文件图标主题。文件图标显示在文件名旁边，表示文件的类型。
>
> 你必须指定一个 id（用在设置中）、一个标签，以及文件图标定义文件的路径。

<a id="file-icon-theme-example"></a>
### 文件图标主题示例（file icon theme example）

```json
{
  "contributes": {
    "iconThemes": [
      {
        "id": "my-cool-file-icons",
        "label": "Cool File Icons",
        "path": "./fileicons/cool-file-icon-theme.json"
      }
    ]
  }
}
```

![文件图标主题扩展点示例](images/contribution-points/file-icon-themes.png)

> 关于如何创建文件图标主题，请参见[文件图标主题指南](../extension-guides/file-icon-theme.md)。

（“用在设置中”指 `workbench.iconTheme` 设置的值就是这个 `id`。）

---

<a id="contributes.jsonValidation"></a>
## contributes.jsonValidation

> 为特定类型的 `json` 文件贡献一个校验架构。`url` 的值可以是扩展中包含的一个架构文件的本地路径，也可以是一个远程服务器的 URL，例如 [JSON 架构存储（json schema store）](https://www.schemastore.org/)。

```json
{
  "contributes": {
    "jsonValidation": [
      {
        "fileMatch": ".jshintrc",
        "url": "https://json.schemastore.org/jshintrc"
      }
    ]
  }
}
```

效果：用户打开 `.jshintrc` 文件时，VS Code 内置的 JSON 语言支持会按这个架构提供补全、悬停说明和错误检查，你的扩展不需要写任何代码。适合为你的工具的配置文件（如 `mytool.config.json`）提供编辑支持：`"fileMatch": "mytool.config.json", "url": "./schemas/mytool.schema.json"`。`fileMatch` 也可以是数组或 glob 模式。

---

<a id="contributes.keybindings"></a>
## contributes.keybindings

> 贡献一条快捷键规则，定义用户按下某个按键组合时应该调用哪个命令。请参见[快捷键](https://code.visualstudio.com/docs/getstarted/keybindings)主题，其中详细解释了快捷键。
>
> 贡献一个快捷键后，默认的键盘快捷方式中会显示你的规则，并且这个命令在 UI 中的所有呈现都会显示你添加的快捷键。当然，用户按下这个按键组合时，命令就会被调用。

> **注意**：由于 VS Code 运行在 Windows、macOS 和 Linux 上，而它们的修饰键不同，你可以用 "key" 设置默认的按键组合，再用特定平台的值覆盖它。

> **注意**：当一个命令被调用时（通过快捷键或命令面板），VS Code 会发出一个激活事件 `onCommand:${command}`。

<a id="keybinding-example"></a>
### 快捷键示例（keybinding example）

> 定义在 Windows 和 Linux 下按 `Ctrl+F1`、在 macOS 下按 `Cmd+F1` 触发 `"extension.sayHello"` 命令：

```json
{
  "contributes": {
    "keybindings": [
      {
        "command": "extension.sayHello",
        "key": "ctrl+f1",
        "mac": "cmd+f1",
        "when": "editorTextFocus"
      }
    ]
  }
}
```

![keybindings 扩展点示例](images/contribution-points/keybindings.png)

| 属性 | 含义 |
|---|---|
| `command` | 要执行的命令 ID |
| `key` | 默认的按键组合 |
| `mac` / `linux` / `win` | 特定平台的按键组合，覆盖 `key` |
| `when` | 快捷键何时生效（见 [when 子句上下文](./when-clause-contexts.md)） |
| `args` | 传给命令的参数（可选） |

**选择快捷键时要谨慎：** 很多组合已经被 VS Code 或其他常用扩展占用，抢占它们会让用户很恼火。尽量用 `when` 把快捷键限制在你的功能相关的上下文中（比如 `"editorLangId == mylang"`），或者干脆不提供默认快捷键，让用户自己绑定。多步快捷键（如 `"ctrl+k ctrl+m"`）冲突的可能性更小。

---

<a id="contributes.languages"></a>
## contributes.languages

> 贡献一种编程语言的定义。这会引入一种新的语言，或者丰富 VS Code 对某种语言的了解。
>
> `contributes.languages` 的主要作用是：
>
> - 定义一个 `languageId`，它可以在 VS Code API 的其他部分中复用，例如 `vscode.TextDocument.languageId` 和 `onLanguage` 激活事件。
>   - 你可以用 `aliases` 字段贡献一个人类可读的名称。列表中的第一项会被用作人类可读的标签。
> - 把文件扩展名（`extensions`）、文件名（`filenames`）、文件名 [glob 模式](https://code.visualstudio.com/docs/editor/glob-patterns)（`filenamePatterns`）、以特定的一行开头的文件（例如 hashbang）（`firstLine`）以及 `mimetypes` 与这个 `languageId` 关联起来。
> - 为贡献的语言贡献一组[声明式语言功能](../language-extensions/overview.md#declarative-language-features)。在[语言配置指南](../language-extensions/language-configuration-guide.md)中了解更多关于可配置的编辑功能。
> - 贡献一个图标，如果文件图标主题中没有包含这种语言的图标，就可以使用它。

<a id="language-example"></a>
### 语言示例（language example）

```json
{
  "contributes": {
    "languages": [
      {
        "id": "python",
        "extensions": [".py"],
        "aliases": ["Python", "py"],
        "filenames": [],
        "firstLine": "^#!/.*\\bpython[0-9.-]*\\b",
        "configuration": "./language-configuration.json",
        "icon": {
          "light": "./icons/python-light.png",
          "dark": "./icons/python-dark.png"
        }
      }
    ]
  }
}
```

| 属性 | 含义 | 示例中的值 |
|---|---|---|
| `id` | 语言 ID | `python` |
| `extensions` | 按扩展名关联 | `.py` 文件 |
| `filenames` | 按完整文件名关联 | 例如 `["Dockerfile"]` |
| `filenamePatterns` | 按 glob 模式关联 | 例如 `["*.config.py"]` |
| `firstLine` | 按文件第一行的正则关联 | 以 `#!/usr/bin/env python3` 开头的无扩展名脚本 |
| `aliases` | 显示名称（第一个用作标签） | 状态栏右下角显示 “Python” |
| `configuration` | [语言配置](../language-extensions/language-configuration-guide.md)文件 | 注释、括号、缩进规则等 |
| `icon` | 语言的默认文件图标 | |

“丰富 VS Code 对某种语言的了解”：多个扩展可以为同一个 `id` 贡献 `languages`，它们的设置会合并。比如你只想让 `.pyw` 文件也被识别为 Python，只需贡献 `{ "id": "python", "extensions": [".pyw"] }`。

---

<a id="contributes.languageModelChatProviders"></a>
## contributes.languageModelChatProviders

> 向 VS Code 贡献一个语言模型聊天提供者，让扩展可以提供自定义的语言模型，供用户在模型选择器中选择。每个提供者管理自己的一组模型，并代表它们处理聊天请求。
>
> 为每个提供者注册一个条目，给它一个唯一的 `vendor` ID。然后在扩展激活时使用 `vscode.lm.registerLanguageModelChatProvider` 来连接实现。

```json
{
  "contributes": {
    "languageModelChatProviders": [
      {
        "vendor": "my-provider",
        "displayName": "My Provider"
      }
    ]
  }
}
```

> 要让用户能够配置这个提供者（例如输入 API 密钥），添加一个 `configuration` 架构。用 `"secret": true` 标记敏感的字段，让它们被安全地存储：

（原文在这句话后面没有给出示例。根据下表的说明，大致的写法如下，具体格式以 [语言模型聊天提供者](../extension-guides/ai/language-model-chat-provider.md) 一篇和官方文档为准。）

```json
{
  "vendor": "my-provider",
  "displayName": "My Provider",
  "configuration": {
    "properties": {
      "apiKey": { "type": "string", "description": "API Key", "secret": true }
    }
  }
}
```

<a id="languagemodelchatproviders-properties"></a>
### languageModelChatProviders 属性（languageModelChatProviders properties）

| 属性 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `vendor` | `string` | 是 | 提供者的唯一标识符，用作 `vscode.lm.registerLanguageModelChatProvider` 的第一个参数。 |
| `displayName` | `string` | 是 | 在模型选择器 UI 中显示的人类可读名称。 |
| `configuration` | `object` | 否 | 一个描述提供者配置选项（例如 API 密钥）的 JSON 架构。属性可以标记为 `"secret": true`，以便安全地存储。这是让用户配置提供者的推荐方式。 |
| `managementCommand` | `string` | 否 | *已弃用，请改用 `configuration`。* 打开一个管理这个提供者的 UI 的命令 ID。必须在 `contributes.commands` 中声明。 |
| `when` | `string` | 否 | 一个 [when 子句](./when-clause-contexts.md)，控制这个提供者是否出现在“管理模型（Manage Models）”列表中。 |

> 完整的实现细节请参见[语言模型聊天提供者 API 指南](../extension-guides/ai/language-model-chat-provider.md)。

---

<a id="contributes.languageModelTools"></a>
## contributes.languageModelTools

> 贡献[语言模型工具](../extension-guides/ai/tools.md)，语言模型可以在智能体式编码工作流中自动调用它们。工具用特定领域的能力扩展智能体模式，例如查询数据库、调用外部 API，或者与编辑器交互。
>
> 在 `contributes.languageModelTools` 部分中定义每个工具，然后在扩展激活时用 `vscode.lm.registerTool` 注册实现。

```json
{
  "contributes": {
    "languageModelTools": [
      {
        "name": "my-extension_queryDatabase",
        "displayName": "Query Database",
        "modelDescription": "Executes a read-only SQL query against the project database and returns the results as JSON. Use this tool when the user asks about data stored in the database.",
        "canBeReferencedInPrompt": true,
        "toolReferenceName": "queryDatabase",
        "icon": "$(database)",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "The SQL SELECT statement to execute."
            }
          },
          "required": ["query"]
        }
      }
    ]
  }
}
```

（`modelDescription` 的意思是：“对项目数据库执行一个只读的 SQL 查询，并以 JSON 返回结果。当用户询问存储在数据库中的数据时使用这个工具。”注意它是写给**模型**看的，所以要写清楚“做什么、返回什么、什么时候用”。`query` 的描述是“要执行的 SQL SELECT 语句”。）

<a id="languagemodeltools-properties"></a>
### languageModelTools 属性（languageModelTools properties）

| 属性 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | `string` | 是 | 工具的唯一名称，在扩展的实现中使用。使用 `{动词}_{名词}` 的格式，并加上你的扩展名作为前缀，以避免冲突。 |
| `displayName` | `string` | 是 | 在 UI 中显示的用户友好的名称。 |
| `modelDescription` | `string` | 是 | 语言模型用来决定何时以及如何调用这个工具的描述。要准确：解释这个工具做什么、返回什么，以及什么时候应该或不应该使用它。 |
| `userDescription` | `string` | 否 | 在 UI 中显示在工具名称旁边、面向用户的描述。 |
| `canBeReferencedInPrompt` | `boolean` | 否 | 设为 `true`，允许智能体使用这个工具，或者在聊天提示中通过 `#` 引用它。为 `true` 时，用户可以在聊天视图中启用或禁用这个工具。 |
| `toolReferenceName` | `string` | 否 | 用户在聊天提示中引用这个工具时，在 `#` 后面输入的名称（例如 `#queryDatabase`）。当 `canBeReferencedInPrompt` 为 `true` 时必填。 |
| `icon` | `string` | 否 | 在 UI 中显示的图标，使用[图标 ID](./icons-in-labels.md) 的格式（例如 `$(database)`）。 |
| `inputSchema` | `object` | 否 | 描述工具输入参数的 JSON 架构。这个架构必须描述一个带有类型化属性的 `object`。 |
| `when` | `string` | 否 | 一个 [when 子句](./when-clause-contexts.md)，控制这个工具何时可用。例如，用 `"debugState == 'running'"` 限制一个调试工具。 |
| `tags` | `string[]` | 否 | 用于对工具进行分类或分组的标签。 |

> 关于实现细节，包括如何处理确认、流式返回结果以及定义类型化的输入参数，请参见[语言模型工具 API 指南](../extension-guides/ai/tools.md)。

`name` 要与代码中 `vscode.lm.registerTool(name, tool)` 的第一个参数一致。

---

<a id="contributes.menus"></a>
## contributes.menus

> 为一个命令向编辑器或资源管理器贡献一个菜单项。菜单项的定义包含选中时应该调用的命令，以及这个菜单项应该在什么条件下显示。后者用 `when` 子句定义，它使用快捷键的 [when 子句上下文](./when-clause-contexts.md)。
>
> `command` 属性指出选中一个菜单项时要运行哪个命令。`submenu` 属性指出在这个位置要渲染哪个子菜单。
>
> 声明一个 `command` 菜单项时，还可以用 `alt` 属性定义一个替代命令。在打开菜单时按住 `Alt`，就会显示并调用这个替代命令。在 Windows 和 Linux 上，按住 `Shift` 也能做到这一点，这在 `Alt` 会触发窗口菜单栏的情况下很有用。
>
> 最后，`group` 属性定义菜单项的排序和分组。`navigation` 组比较特殊，它总是被排在菜单的顶部 / 开头。

> **注意**：`when` 子句作用于菜单，`enablement` 子句作用于命令。`enablement` 适用于所有菜单，甚至快捷键，而 `when` 只适用于单个菜单。

| | `menus.<菜单>[].when` | `commands[].enablement` |
|---|---|---|
| 不满足时 | 菜单项**不显示** | 命令**显示为灰色、不可执行** |
| 作用范围 | 只是这一个菜单中的这一项 | 这个命令出现的所有地方，包括快捷键 |

**菜单项的属性：**

| 属性 | 含义 |
|---|---|
| `command` | 要执行的命令（与 `submenu` 二选一） |
| `submenu` | 要显示的子菜单的 ID（见 [submenus](#contributes.submenus)） |
| `alt` | 按住 `Alt` 时替换成的命令 |
| `when` | 何时显示 |
| `group` | 分组和排序，形如 `"navigation"`、`"1_modification@2"`（见下文） |

> 目前，扩展作者可以贡献到：
>
> - `commandPalette` - 全局的命令面板
> - `comments/comment/title` - 注释的标题菜单栏
> - `comments/comment/context` - 注释的上下文菜单
> - `comments/commentThread/title` - 注释线程的标题菜单栏
> - `comments/commentThread/context` - 注释线程的上下文菜单
> - `debug/callstack/context` - 调试调用堆栈视图的上下文菜单
> - `debug/callstack/context` 组 `inline` - 调试调用堆栈视图的内联操作
> - `debug/toolBar` - 调试视图的工具栏
> - `debug/variables/context` - 调试变量视图的上下文菜单
> - `editor/context` - 编辑器的上下文菜单
> - `editor/context/copy` - 编辑器上下文菜单中的 **Copy as**（复制为）子菜单
> - `editor/lineNumber/context` - 编辑器行号的上下文菜单
> - `editor/title` - 编辑器的标题菜单栏
> - `editor/title/context` - 编辑器标题的上下文菜单
> - `editor/title/run` - 编辑器标题菜单栏上的“运行”子菜单
> - `explorer/context` - 资源管理器视图的上下文菜单
> - `extension/context` - 扩展视图的上下文菜单
> - `file/newFile` - “文件”菜单和欢迎页中的“新建文件”项
> - `interactive/toolbar` - 交互式窗口的工具栏
> - `interactive/cell/title` - 交互式窗口单元格的标题菜单栏
> - `notebook/toolbar` - 笔记本的工具栏
> - `notebook/cell/title` - 笔记本单元格的标题菜单栏
> - `notebook/cell/execute` - 笔记本单元格的执行菜单
> - `scm/title` - [源代码管理的标题菜单](../extension-guides/scm-provider.md#menus)
> - `scm/resourceGroup/context` - [源代码管理资源组](../extension-guides/scm-provider.md#menus)的菜单
> - `scm/resourceFolder/context` - [源代码管理资源文件夹](../extension-guides/scm-provider.md#menus)的菜单
> - `scm/resourceState/context` - [源代码管理资源](../extension-guides/scm-provider.md#menus)的菜单
> - `scm/change/title` - [源代码管理更改的标题](../extension-guides/scm-provider.md#menus)菜单
> - `scm/repository` - [源代码管理存储库菜单](../extension-guides/scm-provider.md#menus)
> - `scm/sourceControl` - [源代码管理菜单](../extension-guides/scm-provider.md#menus)
> - `terminal/context` - 终端的上下文菜单
> - `terminal/title/context` - 终端标题的上下文菜单
> - `testing/item/context` - 测试资源管理器中项的上下文菜单
> - `testing/item/gutter` - 测试项在行号旁的装饰的菜单
> - `timeline/title` - 时间线视图的标题菜单栏
> - `timeline/item/context` - 时间线视图中项的上下文菜单
> - `touchBar` - macOS 的触控栏（Touch Bar）
> - `view/title` - [视图的标题菜单](#contributes.views)
> - `view/item/context` - [视图中项的上下文菜单](#contributes.views)
> - `webview/context` - 任何 [webview](../extension-guides/webview.md) 的上下文菜单
> - 任何[贡献的子菜单](#contributes.submenus)
>
> 除了标题之外，贡献的命令还可以指定图标，当调用它的菜单项被呈现为一个按钮时（例如在标题菜单栏上），VS Code 会显示这个图标。

“上下文菜单（context）”指右键菜单；“标题菜单栏（title）”指视图或编辑器顶部右侧的那一排图标按钮（加上 `...` 中的溢出菜单）。最常用的几个：`commandPalette`（控制命令面板中的可见性）、`editor/context`、`editor/title`、`explorer/context`、`view/title`、`view/item/context`。各个菜单的设计建议见 [UX 指南：上下文菜单](../ux-guidelines/context-menus.md) 和 [UX 指南：编辑器操作](../ux-guidelines/editor-actions.md)。

<a id="menu-command-arguments"></a>
### 菜单命令的参数（Menu command arguments）

> 当你从菜单中调用一个扩展命令时，VS Code 会把来自那个菜单的上下文传给用 `vscode.commands.registerCommand` 注册的处理函数。参数取决于菜单的位置：

| 菜单位置 | 按顺序传给处理函数的参数 |
| --- | --- |
| `editor/context` | 打开上下文菜单时所在文档的 `Uri`。 |
| `editor/context/copy` | 打开上下文菜单时所在文档的 `Uri`。 |
| `explorer/context` | 打开上下文菜单时所在的文件或文件夹的 `Uri`，后面跟着一个选中资源 URI 的数组。如果目标是多选中的一部分，这个数组就包含这个选择。否则，它只包含目标资源。 |
| `editor/title` | 编辑器资源的 `Uri`，后面跟着一个包含 `groupId` 的编辑器上下文对象。 |
| `editor/title/context` | 目标编辑器资源的 `Uri`，后面跟着一个包含 `groupId` 和 `editorIndex` 的编辑器上下文对象。 |

> 编辑器上下文标识了一个编辑器组，对于标签页的上下文菜单，还标识了编辑器在这个组中的索引。`groupId` 是一个内部的组标识符，不是 `ViewColumn`。当你的命令操作的是一个文档时，优先使用资源 URI。对于没有资源 URI 的编辑器，上下文对象是第一个参数。
>
> 如果你在资源管理器的空白处打开上下文菜单，当只有一个工作区文件夹时，第一个参数是这个工作区文件夹的 URI，否则是一个空对象。选中资源的数组为空。在把参数当作资源使用之前，请检查它是不是一个 URI。
>
> 贡献到 `editor/lineNumber/context` 的命令会收到一个带有 `uri` 和 `lineNumber` 属性的对象。`uri` 是文档的 URI，`lineNumber` 是从 1 开始的行号。这些菜单项还可以在它们的 `when` 子句中引用 `editorLineNumber` 上下文键，例如对一个由扩展管理的、值为数组的上下文键使用 `in` 或 `not in` 运算符。
>
> 其他的菜单提供特定于它们功能的上下文。例如，在扩展的[树视图](../extension-guides/tree-view.md#view-actions)中，`view/item/context` 会传入由它的 `TreeDataProvider` 提供的树元素。如果目标属于一个多选，第二个参数包含选中的元素。否则，第二个参数是 `undefined`。关于源代码管理菜单的参数，请参见[源代码管理菜单](../extension-guides/scm-provider.md#menus)。
>
> 当你从命令面板或快捷键调用同一个命令时，这些菜单参数不会被自动提供。关于其他的调用方式，以及一个处理缺少资源情况的示例，请参见[命令处理函数的参数](../extension-guides/command.md#command-handler-arguments)。

**处理资源管理器右键菜单的典型写法（补充）：**

```ts
vscode.commands.registerCommand('ext.doSpecial', (uri?: vscode.Uri, selected?: vscode.Uri[]) => {
  // 从命令面板调用时没有参数；在资源管理器空白处调用时可能是空对象
  const targets = selected?.length ? selected
    : uri instanceof vscode.Uri ? [uri]
    : vscode.window.activeTextEditor ? [vscode.window.activeTextEditor.document.uri]
    : [];
  for (const target of targets) { /* ... */ }
});
```

注意 `editor/lineNumber/context` 的 `lineNumber` **从 1 开始**，而 `vscode.Position` 的行号从 0 开始，换算时要减 1。

<a id="menu-example"></a>
### 菜单示例（menu example）

> 下面是一个命令菜单项：

```json
{
  "contributes": {
    "menus": {
      "editor/title": [
        {
          "when": "resourceLangId == markdown",
          "command": "markdown.showPreview",
          "alt": "markdown.showPreviewToSide",
          "group": "navigation"
        }
      ]
    }
  }
}
```

![menus 扩展点示例](images/contribution-points/menus.png)

截图是早期 VS Code 中内置 Markdown 扩展的配置：左边的 `package.json` 中，圈出的部分是 `markdown.showSource` 命令的定义（带有浅色 / 深色两个图标）和它在 `editor/title` 中的菜单项（`"when": "resourceScheme == markdown"`、`"group": "navigation"`）；右边是 Markdown 预览，标题栏右侧圈出的按钮就是这个菜单项，悬停提示为 “Show Source”。

> 类似地，下面是一个添加到特定视图中的命令菜单项。下面的例子贡献到一个任意的视图，比如终端：

```json
{
  "contributes": {
    "menus": {
      "view/title": [
        {
          "command": "terminalApi.sendText",
          "when": "view == terminal",
          "group": "navigation"
        }
      ]
    }
  }
}
```

![在 view/title 中添加一个 view == terminal 的菜单项，会在终端打开时在面板中显示一个操作](images/contribution-points/menu_view_title.png)

> 下面是一个子菜单的菜单项：

```json
{
  "contributes": {
    "menus": {
      "scm/title": [
        {
          "submenu": "git.commit",
          "group": "2_main@1",
          "when": "scmProvider == git"
        }
      ]
    }
  }
}
```

![menus 扩展点示例（子菜单）](images/contribution-points/submenu.png)

（子菜单本身需要先在 [`contributes.submenus`](#contributes.submenus) 中声明，然后再用 `menus` 中的 `"git.commit": [ ... ]` 往子菜单里放命令。）

<a id="context-specific-visibility-of-command-palette-menu-items"></a>
### 命令面板菜单项的上下文相关可见性（Context specific visibility of Command Palette menu items）

> 在 `package.json` 中注册命令时，它们会自动显示在**命令面板**（`Ctrl+Shift+P`）中。为了对命令的可见性进行更多的控制，有一个 `commandPalette` 菜单项。它允许你定义一个 `when` 条件，来控制一个命令是否应该在**命令面板**中可见。
>
> 下面的代码片段让 'Hello World' 命令只在编辑器中有选中内容时，才在**命令面板**中可见：

```json
{
  "commands": [
    {
      "command": "extension.sayHello",
      "title": "Hello World"
    }
  ],
  "menus": {
    "commandPalette": [
      {
        "command": "extension.sayHello",
        "when": "editorHasSelection"
      }
    ]
  }
}
```

一个常见的用法是**在命令面板中完全隐藏**只供菜单或树视图使用的命令（比如需要一个树节点作为参数、单独执行没有意义的命令）：

```json
"commandPalette": [{ "command": "myExt.deleteNode", "when": "false" }]
```

<a id="sorting-of-groups"></a>
### 分组的排序（Sorting of groups）

> 菜单项可以被分到组中。它们按字典顺序排序，有以下的默认值 / 规则。你可以把菜单项添加到这些组中，也可以在它们之间、之下或之上添加新的菜单项组。
>
> **编辑器上下文菜单**有这些默认的组：
>
> - `navigation` - `navigation` 组在任何情况下都排在最前面。
> - `1_modification` - 这个组排在其次，包含修改你的代码的命令。
> - `9_cutcopypaste` - 倒数第二个默认组，包含基本的编辑命令。
> - `z_commands` - 最后一个默认组，包含一个打开命令面板的条目。

![菜单分组的排序](images/contribution-points/groupSorting.png)

截图是编辑器的右键菜单，橙色标签标出了各组：**navigation**（转到定义、速览定义、查找所有引用）、**1_modification**（更改所有匹配项、格式化文档）、**9_cutcopypaste**（剪切、复制、粘贴）、**z_commands**（命令面板）。组与组之间用分隔线隔开。

**组名的命名技巧：** 因为按字典顺序排序，所以用数字前缀来控制位置。比如想放在“修改”和“剪切复制粘贴”之间，可以起名 `5_myGroup`；想放在最前面（但在 `navigation` 之后），可以起名 `0_myGroup`。

> **资源管理器上下文菜单**有这些默认的组：
>
> - `navigation` - 与在 VS Code 中导航相关的命令。这个组在任何情况下都排在最前面。
> - `2_workspace` - 与操作工作区相关的命令。
> - `3_compare` - 与在差异编辑器中比较文件相关的命令。
> - `4_search` - 与在搜索视图中搜索相关的命令。
> - `5_cutcopypaste` - 与剪切、复制和粘贴文件相关的命令。
> - `6_copypath` - 与复制文件路径相关的命令。
> - `7_modification` - 与修改文件相关的命令。
>
> **编辑器标签页上下文菜单**有这些默认的组：
>
> - `1_close` - 与关闭编辑器相关的命令。
> - `3_preview` - 与固定编辑器相关的命令。
>
> **编辑器标题菜单**有这些默认的组：
>
> - `navigation` - 与导航相关的命令。
> - `1_run` - 与运行和调试编辑器相关的命令。
> - `1_diff` - 与使用差异编辑器相关的命令。
> - `3_open` - 与打开编辑器相关的命令。
> - `5_close` - 与关闭编辑器相关的命令。
>
> `navigation` 和 `1_run` 显示在编辑器标题的主区域中。其他的组显示在次要区域中，即 `...` 菜单下。

**这一点对 `editor/title` 和 `view/title` 尤其重要：** 只有 `group` 为 `navigation` 的项才会作为**图标按钮**显示在标题栏上；其他组的项都会被收进 `...` 溢出菜单。如果你发现自己的按钮“没有显示”，先检查 `group` 是否写了 `"navigation"`，以及命令是否有 `icon`。

> **终端标签页上下文菜单**有这些默认的组：
>
> - `1_create` - 与创建终端相关的命令。
> - `3_run` - 与在终端中运行 / 执行某些东西相关的命令。
> - `5_manage` - 与管理终端相关的命令。
> - `7_configure` - 与终端配置相关的命令。
>
> **终端上下文菜单**有这些默认的组：
>
> - `1_create` - 与创建终端相关的命令。
> - `3_edit` - 与操作文字、选择或剪贴板相关的命令。
> - `5_clear` - 与清除终端相关的命令。
> - `7_kill` - 与关闭 / 终止终端相关的命令。
> - `9_config` - 与终端配置相关的命令。
>
> **时间线视图项上下文菜单**有这些默认的组：
>
> - `inline` - 重要的或常用的时间线项命令。渲染为一个工具栏。
> - `1_actions` - 与使用时间线项相关的命令。
> - `5_copy` - 与复制时间线项信息相关的命令。
>
> **扩展视图上下文菜单**有这些默认的组：
>
> - `1_copy` - 与复制扩展信息相关的命令。
> - `2_configure` - 与配置扩展相关的命令。

`inline` 组也适用于 `view/item/context`：放在 `inline` 组中的命令会作为图标按钮显示在树节点的右侧（鼠标悬停时出现），其他组的命令出现在右键菜单中，见 [树视图](../extension-guides/tree-view.md#view-actions)。

<a id="sorting-inside-groups"></a>
### 组内的排序（Sorting inside groups）

> 组内的顺序取决于标题或一个 order 属性。一个菜单项在组内的顺序，是通过在组标识符后面追加 `@<数字>` 来指定的，如下所示：

```json
{
  "editor/title": [
    {
      "when": "editorHasSelection",
      "command": "extension.Command",
      "group": "myGroup@1"
    }
  ]
}
```

（没有 `@数字` 时，组内按标题的字母顺序排列。数字小的排在前面。）

---

<a id="contributes.problemMatchers"></a>
## contributes.problemMatchers

> 贡献问题匹配器模式。这些贡献既适用于输出面板运行器，也适用于终端运行器。下面是一个在扩展中为 gcc 编译器贡献问题匹配器的例子：

```json
{
  "contributes": {
    "problemMatchers": [
      {
        "name": "gcc",
        "owner": "cpp",
        "fileLocation": ["relative", "${workspaceFolder}"],
        "pattern": {
          "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
          "file": 1,
          "line": 2,
          "column": 3,
          "severity": 4,
          "message": 5
        }
      }
    ]
  }
}
```

> 现在可以在 `tasks.json` 文件中通过名称引用 `$gcc` 来使用这个问题匹配器。示例如下：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "build",
      "command": "gcc",
      "args": ["-Wall", "helloWorld.c", "-o", "helloWorld"],
      "problemMatcher": "$gcc"
    }
  ]
}
```

> 另请参见：[定义问题匹配器](https://code.visualstudio.com/docs/debugtest/tasks#defining-a-problem-matcher)

**问题匹配器的作用：** 任务（比如编译）输出的是一行行文字，问题匹配器用正则从中“抠出”错误信息，变成“问题”面板中可点击的条目和编辑器中的波浪线。以 gcc 的一行输出为例：

```text
helloWorld.c:5:3: warning: implicit declaration of function 'prinft'
 └── 1 file ──┘ 2 3  └─ 4 ─┘  └──────────── 5 message ──────────────┘
```

| 字段 | 含义 |
|---|---|
| `name` | 匹配器的名称，在 `tasks.json` 中用 `$名称` 引用 |
| `owner` | 问题的所有者（同一所有者的问题会被一起替换） |
| `fileLocation` | 输出中的文件路径是相对的还是绝对的；`["relative", "${workspaceFolder}"]` 表示相对于工作区文件夹 |
| `pattern.regexp` | 匹配一行输出的正则（JSON 中反斜杠要双写） |
| `pattern.file` / `line` / `column` / `severity` / `message` | 正则中对应的分组编号 |

---

<a id="contributes.problemPatterns"></a>
## contributes.problemPatterns

> 贡献具名的问题模式，可以在问题匹配器中使用（见上文）。

（也就是把上面 `pattern` 那部分单独起个名字，多个匹配器可以通过 `"pattern": "$名称"` 复用。）

---

<a id="contributes.productIconThemes"></a>
## contributes.productIconThemes

> 向 VS Code 贡献一个产品图标主题。产品图标是 VS Code 中使用的所有图标，但不包括文件图标和扩展贡献的图标。
>
> 你必须指定一个 id（用在设置中）、一个标签，以及图标定义文件的路径。

<a id="product-icon-theme-example"></a>
### 产品图标主题示例（product icon theme example）

```json
{
  "contributes": {
    "productIconThemes": [
      {
        "id": "elegant",
        "label": "Elegant Icon Theme",
        "path": "./producticons/elegant-product-icon-theme.json"
      }
    ]
  }
}
```

![产品图标主题扩展点示例](images/contribution-points/product-icon-themes.png)

> 关于如何创建产品图标主题，请参见[产品图标主题指南](../extension-guides/product-icon-theme.md)。

（对应的设置是 `workbench.productIconTheme`。）

---

<a id="contributes.resourceLabelFormatters"></a>
## contributes.resourceLabelFormatters

> 贡献资源标签格式化器，它们指定如何在工作台的各处显示 URI。例如，下面是一个扩展如何为 scheme 为 `remotehub` 的 URI 贡献一个格式化器：

```json
{
  "contributes": {
    "resourceLabelFormatters": [
      {
        "scheme": "remotehub",
        "formatting": {
          "label": "${path}",
          "separator": "/",
          "workspaceSuffix": "GitHub"
        }
      }
    ]
  }
}
```

> 这意味着，所有 scheme 为 `remotehub` 的 URI 在渲染时只显示 URI 的 `path` 部分，分隔符为 `/`。具有 `remotehub` URI 的工作区，会在标签中带上 GitHub 后缀。

适用于实现了自定义文件系统（[虚拟工作区](../extension-guides/virtual-workspaces.md)）的扩展：没有这个格式化器时，标签页、面包屑等处会显示完整的 `remotehub://...` 地址，很不友好。窗口标题中工作区名称后会显示 “[GitHub]”。

---

<a id="contributes.semanticTokenModifiers"></a>
## contributes.semanticTokenModifiers

> 贡献新的语义标记修饰符，可以通过主题规则来高亮它们。

```json
{
  "contributes": {
    "semanticTokenModifiers": [
      {
        "id": "native",
        "description": "Annotates a symbol that is implemented natively"
      }
    ]
  }
}
```

> 请参见[语义高亮指南](../language-extensions/semantic-highlight-guide.md)，了解更多关于语义高亮的内容。

---

<a id="contributes.semanticTokenScopes"></a>
## contributes.semanticTokenScopes

> 贡献语义标记类型和修饰符与作用域之间的映射，既可以作为后备，也可以用来支持特定于语言的主题。

```json
{
  "contributes": {
    "semanticTokenScopes": [
      {
        "language": "typescript",
        "scopes": {
          "property.readonly": ["variable.other.constant.property.ts"]
        }
      }
    ]
  }
}
```

> 请参见[语义高亮指南](../language-extensions/semantic-highlight-guide.md)，了解更多关于语义高亮的内容。

---

<a id="contributes.semanticTokenTypes"></a>
## contributes.semanticTokenTypes

> 贡献新的语义标记类型，可以通过主题规则来高亮它们。

```json
{
  "contributes": {
    "semanticTokenTypes": [
      {
        "id": "templateType",
        "superType": "type",
        "description": "A template type."
      }
    ]
  }
}
```

> 请参见[语义高亮指南](../language-extensions/semantic-highlight-guide.md)，了解更多关于语义高亮的内容。

（这三个贡献点的详细解释都在 [语义高亮指南](../language-extensions/semantic-highlight-guide.md#custom-token-types-and-modifiers) 中。）

---

<a id="contributes.snippets"></a>
## contributes.snippets

> 为特定的语言贡献代码片段。`language` 属性是[语言标识符](https://code.visualstudio.com/docs/languages/identifiers)，`path` 是代码片段文件的相对路径，这个文件以 [VS Code 代码片段格式](https://code.visualstudio.com/docs/editing/userdefinedsnippets#snippet-syntax)定义代码片段。
>
> 下面的例子展示了为 Go 语言添加代码片段。

```json
{
  "contributes": {
    "snippets": [
      {
        "language": "go",
        "path": "./snippets/go.json"
      }
    ]
  }
}
```

（代码片段文件的格式见 [代码片段指南](../language-extensions/snippet-guide.md)。）

---

<a id="contributes.submenus"></a>
## contributes.submenus

> 贡献一个子菜单作为占位符，菜单项可以被贡献到它上面。子菜单需要一个 `label`，以便显示在父菜单中。
>
> 除了标题之外，命令还可以定义图标，VS Code 会在编辑器标题菜单栏中显示这些图标。

<a id="submenu-example"></a>
### 子菜单示例（submenu example）

```json
{
  "contributes": {
    "submenus": [
      {
        "id": "git.commit",
        "label": "Commit"
      }
    ]
  }
}
```

![submenus 扩展点示例](images/contribution-points/submenucontrib.png)

**子菜单的完整用法（三步，补充）：**

```json
"contributes": {
  "submenus": [{ "id": "myExt.tools", "label": "My Tools", "icon": "$(tools)" }],   // 1. 声明子菜单
  "menus": {
    "editor/context": [{ "submenu": "myExt.tools", "group": "navigation" }],     // 2. 把子菜单放到父菜单中
    "myExt.tools": [                                                               // 3. 往子菜单里放命令
      { "command": "myExt.format" },
      { "command": "myExt.lint" }
    ]
  }
}
```

子菜单也可以带 `icon`，放在 `editor/title` 等标题栏中时会显示为一个下拉按钮。

---

<a id="contributes.taskDefinitions"></a>
## contributes.taskDefinitions

> 贡献并定义一个对象字面量的结构，用于在系统中唯一地标识一个贡献的任务。一个任务定义至少有一个 `type` 属性，但它通常还会定义更多的属性。例如，一个表示 package.json 文件中脚本的任务的任务定义如下：

```json
{
  "taskDefinitions": [
    {
      "type": "npm",
      "required": ["script"],
      "properties": {
        "script": {
          "type": "string",
          "description": "The script to execute"
        },
        "path": {
          "type": "string",
          "description": "The path to the package.json file. If omitted the package.json in the root of the workspace folder is used."
        }
      }
    }
  ]
}
```

> 任务定义的 `required` 和 `properties` 属性使用 JSON 架构语法来定义。`type` 属性定义任务的类型。在上面的例子中：
>
> - `"type": "npm"` 把这个任务定义与 npm 任务关联起来
> - `"required": [ "script" ]` 定义了 `script` 属性是必需的。`path` 属性是可选的。
> - `"properties" : { ... }` 定义了额外的属性及其类型。
>
> 当扩展实际创建一个任务（Task）时，它需要传入一个与 package.json 文件中贡献的任务定义相符的 `TaskDefinition`。对于 `npm` 的例子，为 package.json 文件中的 test 脚本创建任务的代码如下：

```ts
let task = new vscode.Task({ type: 'npm', script: 'test' }, ....);
```

（两个属性的描述分别是“要执行的脚本”、“package.json 文件的路径，省略时使用工作区文件夹根目录中的 package.json”。这个定义同时决定了用户在 `tasks.json` 中写 `{ "type": "npm", "script": "test" }` 时能获得的补全和校验。完整的用法见 [任务提供者](../extension-guides/task-provider.md)。）

---

<a id="contributes.terminal"></a>
## contributes.terminal

> 向 VS Code 贡献一个终端配置文件，允许扩展处理这些配置文件的创建。定义之后，在创建终端配置文件时就会出现这个配置文件

```json
{
  "activationEvents": [
    "onTerminalProfile:my-ext.terminal-profile"
  ],
  "contributes": {
    "terminal": {
      "profiles": [
        {
          "title": "Profile from extension",
          "id": "my-ext.terminal-profile"
        }
      ]
    },
  }
}
```

> 定义之后，这个配置文件会出现在终端配置文件选择器中。激活时，通过返回终端选项来处理这个配置文件的创建：

```ts
vscode.window.registerTerminalProfileProvider('my-ext.terminal-profile', {
  provideTerminalProfile(token: vscode.CancellationToken): vscode.ProviderResult<vscode.TerminalOptions | vscode.ExtensionTerminalOptions> {
    return { name: 'Profile from extension', shellPath: 'bash' };
  }
});
```

（终端面板 `+` 按钮旁的下拉列表中会出现 “Profile from extension”。注意示例 JSON 中 `"terminal": {...},` 后面多了一个逗号。另外，`provideTerminalProfile` 在 `@types/vscode` 1.140.0 中的返回类型是 `ProviderResult<TerminalProfile>`，应该写成 `return new vscode.TerminalProfile({ name: 'Profile from extension', shellPath: 'bash' });`。）

---

<a id="contributes.themes"></a>
## contributes.themes

> 向 VS Code 贡献一个颜色主题，定义工作台的颜色和编辑器中语法标记的样式。
>
> 你必须指定一个标签、这个主题是深色主题还是浅色主题（以便 VS Code 的其余部分随之改变，与你的主题相配），以及文件（JSON 格式）的路径。

<a id="theme-example"></a>
### 主题示例（theme example）

```json
{
  "contributes": {
    "themes": [
      {
        "label": "Monokai",
        "uiTheme": "vs-dark",
        "path": "./themes/monokai-color-theme.json"
      }
    ]
  }
}
```

![颜色主题扩展点示例](images/contribution-points/color-themes.png)

> 关于如何创建颜色主题，请参见[颜色主题指南](../extension-guides/color-theme.md)。

`uiTheme` 的取值：`vs`（浅色）、`vs-dark`（深色）、`hc-black`（深色高对比度）、`hc-light`（浅色高对比度）。

---

<a id="contributes.typescriptServerPlugins"></a>
## contributes.typescriptServerPlugins

> 贡献 [TypeScript 服务器插件](https://github.com/microsoft/TypeScript/wiki/Writing-a-Language-Service-Plugin)，增强 VS Code 对 JavaScript 和 TypeScript 的支持：

```json
{
  "contributes": {
    "typescriptServerPlugins": [
      {
        "name": "typescript-styled-plugin"
      }
    ]
  }
}
```

> 上面这个示例扩展贡献了 [`typescript-styled-plugin`](https://github.com/microsoft/typescript-styled-plugin)，它为 JavaScript 和 TypeScript 添加了 styled-component 的智能提示。这个插件会从扩展中加载，并且必须作为一个普通的 NPM `dependency` 安装在扩展中：

```json
{
  "dependencies": {
    "typescript-styled-plugin": "*"
  }
}
```

> 当用户使用 VS Code 自带版本的 TypeScript 时，TypeScript 服务器插件会为所有的 JavaScript 和 TypeScript 文件加载。如果用户使用的是工作区版本的 TypeScript，它们不会被激活，除非插件显式地设置了 `"enableForWorkspaceTypeScriptVersions": true`。

```json
{
  "contributes": {
    "typescriptServerPlugins": [
      {
        "name": "typescript-styled-plugin",
        "enableForWorkspaceTypeScriptVersions": true
      }
    ]
  }
}
```

**这和普通扩展有什么不同：** TypeScript 的智能功能由内置扩展启动的 `tsserver` 进程提供。TS 服务器插件运行在 **`tsserver` 进程内部**，可以修改或增强它的补全、诊断等结果（比如在模板字符串中提供 CSS 补全）。这比自己写一套 TypeScript 语言支持简单得多，也不会与内置功能冲突。因为插件是在运行时被 `tsserver` 按名称加载的，所以它必须作为 `dependencies` 随扩展发布（使用打包工具时也要把它从打包中排除并保留在 `node_modules` 中，见 [打包扩展代码](../working-with-extensions/bundling-extension.md#webpack-critical-dependencies)）。

<a id="plugin-configuration"></a>
### 插件配置（Plugin configuration）

> 扩展可以通过 VS Code 内置的 TypeScript 扩展所提供的 API，向贡献的 TypeScript 插件发送配置数据：

```ts
// 在你的 VS Code 扩展中

export async function activate(context: vscode.ExtensionContext) {
  // 获取 TS 扩展
  const tsExtension = vscode.extensions.getExtension('vscode.typescript-language-features');
  if (!tsExtension) {
    return;
  }

  await tsExtension.activate();

  // 从 TS 扩展获取 API
  if (!tsExtension.exports || !tsExtension.exports.getAPI) {
    return;
  }

  const api = tsExtension.exports.getAPI(0);
  if (!api) {
    return;
  }

  // 配置 'my-typescript-plugin-id' 插件
  api.configurePlugin('my-typescript-plugin-id', {
    someValue: process.env['SOME_VALUE']
  });
}
```

> TypeScript 服务器插件通过一个 `onConfigurationChanged` 方法接收配置数据：

```ts
// 在你的 TypeScript 插件中

import * as ts_module from 'typescript/lib/tsserverlibrary';

export = function init({ typescript }: { typescript: typeof ts_module }) {
  return {
    create(info: ts.server.PluginCreateInfo) {
      // 创建新的语言服务
    },
    onConfigurationChanged(config: any) {
      // 接收从 VS Code 发送来的配置变化
    }
  };
};
```

> 这个 API 让 VS Code 扩展可以把 VS Code 的设置同步给一个 TypeScript 服务器插件，或者动态地改变插件的行为。看看 [TypeScript TSLint 插件](https://github.com/microsoft/vscode-typescript-tslint-plugin/blob/main/src/index.ts)和 [lit-html](https://github.com/mjbvz/vscode-lit-html/blob/master/src/index.ts) 扩展，了解这个 API 在实际中是如何使用的。

（这里用到了 `extensions.getExtension(id).exports`：内置 TypeScript 扩展在 `activate` 中返回了一个对象作为它的公共 API，其他扩展可以这样调用它。`getAPI(0)` 中的 `0` 是 API 的版本号。）

---

<a id="contributes.views"></a>
## contributes.views

> 向 VS Code 贡献一个视图。你必须为视图指定一个标识符和名称。你可以贡献到以下的视图容器中：
>
> - `explorer`：活动栏中的资源管理器视图容器
> - `scm`：活动栏中的源代码管理（SCM）视图容器
> - `debug`：活动栏中的运行和调试视图容器
> - `test`：活动栏中的测试视图容器
> - 由扩展贡献的[自定义视图容器](#contributes.viewsContainers)。
>
> 当用户打开这个视图时，VS Code 会发出一个激活事件 `onView:${viewId}`（下面的例子中是 `onView:nodeDependencies`）。你还可以通过提供 `when` 上下文值来控制视图的可见性。当无法显示标题时（例如视图被拖到活动栏中时），会使用指定的 `icon`。当视图被移出它的默认视图容器、需要额外的上下文时，会使用 `contextualTitle`。

```json
{
  "contributes": {
    "views": {
      "explorer": [
        {
          "id": "nodeDependencies",
          "name": "Node Dependencies",
          "when": "workspaceHasPackageJSON",
          "icon": "media/dep.svg",
          "contextualTitle": "Package Explorer"
        }
      ]
    }
  }
}
```

![views 扩展点示例](images/contribution-points/views.png)

> 视图的内容可以通过两种方式填充：
>
> - 使用一个 [TreeView](https://code.visualstudio.com/api/references/vscode-api#TreeView)：通过 `createTreeView` API 提供一个[数据提供者](https://code.visualstudio.com/api/references/vscode-api#TreeDataProvider)，或者直接通过 `registerTreeDataProvider` API 注册[数据提供者](https://code.visualstudio.com/api/references/vscode-api#TreeDataProvider)来填充数据。树视图非常适合显示层次化的数据和列表。请参考 [tree-view-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/tree-view-sample)。
> - 使用一个 [WebviewView](https://code.visualstudio.com/api/references/vscode-api#WebviewView)：通过 `registerWebviewViewProvider` 注册一个[提供者](https://code.visualstudio.com/api/references/vscode-api#WebviewViewProvider)。Webview 视图允许在视图中渲染任意的 HTML。更多细节请参见 [webview 视图示例扩展](https://github.com/microsoft/vscode-extension-samples/tree/main/webview-view-sample)。

（`workspaceHasPackageJSON` 不是内置的上下文键，而是示例扩展自己用 `setContext` 设置的。使用 Webview 视图时，要在视图定义中加上 `"type": "webview"`。代码中 `registerTreeDataProvider` / `registerWebviewViewProvider` 的第一个参数就是这里的 `id`。详见 [树视图](../extension-guides/tree-view.md)、[Webview](../extension-guides/webview.md)。）

---

<a id="contributes.viewsContainers"></a>
## contributes.viewsContainers

> 贡献一个视图容器，[自定义视图](#contributes.views)可以被贡献到其中。你必须为视图容器指定一个标识符、标题和图标。目前，你可以把它们贡献到活动栏（`activitybar`）和面板（`panel`）中。下面的例子展示了如何把 `Package Explorer` 视图容器贡献到活动栏中，以及如何把视图贡献到其中。

```json
{
  "contributes": {
    "viewsContainers": {
      "activitybar": [
        {
          "id": "package-explorer",
          "title": "Package Explorer",
          "icon": "resources/package-explorer.svg"
        }
      ]
    },
    "views": {
      "package-explorer": [
        {
          "id": "package-dependencies",
          "name": "Dependencies"
        },
        {
          "id": "package-outline",
          "name": "Outline"
        }
      ]
    }
  }
}
```

![自定义视图容器](images/contribution-points/custom-views-container.png)

注意 `views` 中的键 `package-explorer` 就是视图容器的 `id`，这样两个视图就被放进了这个容器中。点击活动栏上的图标，侧边栏中就会显示 “Package Explorer” 标题和 Dependencies、Outline 两个可折叠的视图。

<a id="icon-specifications"></a>
### 图标规范（Icon specifications）

> - `Size:`（尺寸）图标应为 24x24，并且居中。
> - `Color:`（颜色）图标应使用单一颜色。
> - `Format:`（格式）建议图标使用 SVG，不过任何图像文件类型都可以接受。
> - `States:`（状态）所有图标都继承以下状态样式：
>
>   | 状态 | 不透明度 |
>   | --- | --- |
>   | 默认（Default） | 60% |
>   | 悬停（Hover） | 100% |
>   | 活动（Active） | 100% |

活动栏会把图标染成主题的前景色，所以 SVG 中的颜色并不重要（只看形状），单色设计即可。也可以直接用 Codicon：`"icon": "$(package)"`。

---

<a id="contributes.viewsWelcome"></a>
## contributes.viewsWelcome

> 为[自定义视图](#contributes.views)贡献欢迎内容。欢迎内容只适用于空的树视图。如果树没有子项、也没有 `TreeView.message`，这个视图就被认为是空的。按照惯例，单独占一行的任何命令链接都会显示为一个按钮。你可以用 `view` 属性指定欢迎内容应该应用到哪个视图上。欢迎内容的可见性可以用 `when` 上下文值控制。要作为欢迎内容显示的文字用 `contents` 属性设置。

```json
{
  "contributes": {
    "viewsWelcome": [
      {
        "view": "scm",
        "contents": "In order to use git features, you can open a folder containing a git repository or clone from a URL.\n[Open Folder](command:vscode.openFolder)\n[Clone Repository](command:git.clone)\nTo learn more about how to use git and source control in VS Code [read our docs](https://aka.ms/vscode-scm).",
        "when": "config.git.enabled && git.state == initialized && workbenchState == empty"
      }
    ]
  }
}
```

![欢迎内容示例](images/contribution-points/viewsWelcome.png)

截图是“源代码管理”视图在没有打开文件夹时的欢迎内容：一段说明文字，两个蓝色按钮 **Open Folder** 和 **Clone Repository**（它们在 `contents` 中各自单独占一行，所以显示为按钮），最后一句中的 “read our docs” 是普通链接（与文字在同一行）。`command:` 链接即 [命令 URI](../extension-guides/command.md#command-uris)。

> 可以为一个视图贡献多个欢迎内容项。在这种情况下，来自 VS Code 核心的内容排在最前面，然后是来自内置扩展的内容，最后是来自所有其他扩展的内容。

---

<a id="contributes.walkthroughs"></a>
## contributes.walkthroughs

> [示例扩展](https://github.com/microsoft/vscode-extension-samples/tree/main/getting-started-sample)
>
> 贡献演练（walkthroughs），使其出现在“入门（Getting Started）”页面中。安装你的扩展时，演练会自动打开，它们提供了一种向用户介绍扩展功能的便捷方式。
>
> 演练由标题、描述、id 和一系列步骤组成。此外，还可以设置一个 `when` 条件，根据上下文键隐藏或显示演练。例如，一个讲解在 Linux 平台上如何设置的演练，可以设置 `when: "isLinux"`，只在 Linux 机器上显示。
>
> 演练中的每个步骤都有标题、描述、id 和一个媒体元素（图像或 Markdown 内容），以及一组可选的、会让这个步骤被勾选的事件（见下面的例子）。步骤的描述是 Markdown 内容，支持 `**粗体**`、`__下划线__` 和 ``` ``代码`` ``` 的渲染，以及链接。与演练类似，步骤也可以设置 when 条件，根据上下文键隐藏或显示它们。
>
> 推荐使用 SVG 作为图像，因为它们可以缩放，并且支持 VS Code 的主题颜色。使用 [Visual Studio Code Color Mapper](https://www.figma.com/community/plugin/1218260433851630449) 这个 Figma 插件，可以轻松地在 SVG 中引用主题颜色。

```json
{
  "contributes": {
    "walkthroughs": [
      {
        "id": "sample",
        "title": "Sample",
        "description": "A sample walkthrough",
        "steps": [
          {
            "id": "runcommand",
            "title": "Run Command",
            "description": "This step will run a command and check off once it has been run.\n[Run Command](command:getting-started-sample.runCommand)",
            "media": { "image": "media/image.png", "altText": "Empty image" },
            "completionEvents": ["onCommand:getting-started-sample.runCommand"]
          },
          {
            "id": "changesetting",
            "title": "Change Setting",
            "description": "This step will change a setting and check off when the setting has changed\n[Change Setting](command:getting-started-sample.changeSetting)",
            "media": { "markdown": "media/markdown.md" },
            "completionEvents": ["onSettingChanged:getting-started-sample.sampleSetting"]
          }
        ]
      }
    ]
  }
}
```

![演练示例](images/contribution-points/walkthroughs.png)

截图是“入门”页面中的 “Sample” 演练：左侧是步骤列表，“Run Command” 还未完成（空心圆），“Change Setting” 已完成（蓝色对勾）并展开，显示描述和绿色的 **Change Setting** 按钮（来自描述中单独一行的命令链接）；右侧是当前步骤的媒体内容（这里是一张命令面板的截图）。

（两个步骤的描述分别是：“这个步骤会运行一个命令，命令运行后就会被勾选”、“这个步骤会修改一个设置，设置被修改后就会被勾选”。演练的设计建议见 [UX 指南：演练](../ux-guidelines/walkthroughs.md)。）

<a id="completion-events"></a>
### 完成事件（Completion events）

> 默认情况下，如果没有提供 `completionEvents` 事件，当步骤的任意一个按钮被点击时，或者如果步骤没有按钮，当它被打开时，这个步骤就会被勾选。如果需要更精细的控制，可以提供一个 `completionEvents` 列表。
>
> 可用的完成事件包括：
>
> - `onCommand:myCommand.id`：当一个命令被运行后，勾选这个步骤。
> - `onSettingChanged:mySetting.id`：一旦给定的设置被修改，就勾选这个步骤。
> - `onContext:contextKeyExpression`：当一个上下文键表达式的计算结果为真时，勾选这个步骤。
> - `extensionInstalled:myExt.id`：如果给定的扩展已安装，就勾选这个步骤。
> - `onView:myView.id`：一旦给定的视图变得可见，就勾选这个步骤。
> - `onLink:https://...`：一旦通过演练打开了给定的链接，就勾选这个步骤。
>
> 一旦一个步骤被勾选，它就会保持勾选状态，直到用户显式地取消勾选这个步骤，或者重置他们的进度（通过 **Getting Started: Reset Progress** 命令）。

（原文中的 “it's buttons” 应为 “its buttons”。`onContext` 的值是一个 when 子句表达式，例如 `onContext:myExt.isConfigured`。）

---

## 本篇小结

```text
contributes = 静态声明（无需运行代码 VS Code 就能读取）+ 代码中用 API 实现行为

最常用
  commands（command / title / category / icon / enablement）
  menus（<菜单位置>: [{ command | submenu, when, group: "navigation" | "1_xxx@1", alt }]）
    · editor/title、view/title 中只有 navigation 组显示为图标按钮
    · commandPalette + when 控制命令面板中的可见性（"when": "false" 隐藏）
    · 菜单会把 Uri / 树元素等作为参数传给命令处理函数
  keybindings（key / mac / win / linux / when）
  configuration（title、properties：type、default、description / markdownDescription、enum、scope、order……）
    · 代码中 workspace.getConfiguration(前缀).get(...)、onDidChangeConfiguration
  viewsContainers + views + viewsWelcome（侧边栏 / 面板中的自定义视图）

语言：languages、grammars、snippets、jsonValidation、semanticToken*、typescriptServerPlugins
主题：themes、iconThemes、productIconThemes、colors、icons
调试 / 任务：debuggers、breakpoints、taskDefinitions、problemMatchers、terminal
AI：languageModelTools、languageModelChatProviders、chatAgents / chatInstructions / chatPromptFiles / chatSkills
其他：authentication、customEditors、resourceLabelFormatters、walkthroughs、configurationDefaults
```
