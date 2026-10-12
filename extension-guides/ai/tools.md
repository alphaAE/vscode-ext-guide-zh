# 语言模型工具 API（Language Model Tool API）

> 原文：[Language Model Tool API](https://code.visualstudio.com/api/extension-guides/ai/tools)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/ai/tools.md`（DateApproved: 10/7/2026）

> 语言模型工具让你可以用特定领域的能力，扩展聊天中大语言模型（LLM）的功能。为了处理用户的聊天提示词，VS Code 中的[智能体](https://code.visualstudio.com/docs/chat/chat-overview)可以自动调用这些工具，在对话中执行专门的任务。
>
> 在 VS Code 扩展中贡献一个语言模型工具，你可以扩展智能体编码工作流，同时与编辑器深度集成。扩展工具是 VS Code 中三种可用的工具类型之一，另外两种是[内置工具和 MCP 工具](https://code.visualstudio.com/docs/agents/concepts/tools#types-of-tools)。
>
> 在这篇扩展指南中，你将学习如何使用语言模型工具 API 创建一个语言模型工具，以及如何在聊天扩展中实现工具调用。
>
> 你也可以通过贡献一个 [MCP 服务器](./mcp.md)，用专门的工具扩展聊天体验。关于不同选项的详细信息以及如何决定使用哪种方式，请参阅 [AI 扩展性概览](./ai-extensibility-overview.md)。

> **提示**
>
> 关于作为最终用户如何使用工具，请参阅[在智能体中使用工具](https://code.visualstudio.com/docs/agents/run/tools)。

---

<a id="what-is-tool-calling-in-an-llm"></a>
## 什么是 LLM 中的工具调用？（What is tool calling in an LLM?）

> 语言模型工具是一个可以在语言模型请求过程中被调用的函数。例如，你可能有一个从数据库中获取信息、执行某些计算或调用某个在线 API 的函数。当你在 VS Code 扩展中贡献一个工具后，智能体模式就可以根据对话的上下文调用这个工具。
>
> LLM 本身永远不会真正执行这个工具，而是生成用于调用你的工具的参数。清楚地描述工具的用途、功能和输入参数非常重要，这样工具才能在正确的上下文中被调用。

**这是理解工具调用最关键的一点：模型不会运行代码，它只是“提出请求”。**

```text
用户：  “现在打开了几个标签页？”
         ↓
模型：  （看了一下可用工具的描述）“我要调用 tabCount 工具，参数是 {}”   ← 模型只生成这个请求
         ↓
VS Code：执行你扩展中 tabCount 工具的代码 → 得到结果 “There are 5 tabs open.”
         ↓
模型：  （拿到结果）“你现在打开了 5 个标签页。”
```

模型怎么知道有哪些工具、什么时候该用哪个？**全靠你写的工具描述**。描述写得不清楚，模型就可能在不该用的时候调用它，或者该用的时候想不起来用它。

> 下图展示了 VS Code 智能体模式中的工具调用流程。关于其中具体的步骤，请参阅[工具调用流程](#tool-calling-flow)。

![Copilot 工具调用流程示意图](../images/ai/tools/copilot-tool-calling-flow.png)

图中各部分的含义：

- **左上**：用户（User）向 Copilot 发送提示词（Prompt），Copilot 把结果以流式方式返回给用户（Streamed result）；Copilot 还会从“机器和工作区”（Machine and workspace）获取工作区和系统环境的摘要作为上下文。
- **右上的橙色框（Loop，循环）**：Copilot 把“提示词 + 上下文 + 工具描述 +（工具调用的结果）”发给 LLM；LLM 返回“结果，或者带参数调用某个工具的决定”。这个过程会循环多次。
- **右下的蓝色框（Tools，工具）**：可用的工具。上半部分是内置工具（`read_file`、`edit_file`、`run_in_terminal` 等），下半部分的绿色框是可扩展的贡献工具（Extensible: contributed tools），如 `get_issues`、`perplexity_search`、`open_diagram`。
- **左下的绿色框**：贡献工具的来源——MCP 服务器（如 Perplexity、GitHub），以及 VS Code 扩展（如 Mermaid Chart）。**本篇讲的就是最下面那种：由 VS Code 扩展贡献工具。**

> 在 OpenAI 的文档中可以了解更多关于[函数调用（function calling）](https://platform.openai.com/docs/guides/function-calling)的信息。

“工具调用”在不同 AI 厂商的文档中也叫“函数调用”（function calling），是同一个概念。

---

<a id="why-implement-a-language-model-tool-in-your-extension"></a>
## 为什么要在扩展中实现语言模型工具？（Why implement a language model tool in your extension?）

> 在扩展中实现语言模型工具有以下几个好处：
>
> - **扩展智能体模式**：提供专门的、特定于领域的工具，在回应用户提示词的过程中被自动调用。例如，启用数据库的脚手架生成和查询功能，动态地为 LLM 提供相关的上下文。
> - **与 VS Code 深度集成**：可以使用大量的扩展 API。例如，使用[调试 API](../debugger-extension.md) 获取当前的调试上下文，并把它作为工具功能的一部分。
> - **分发和部署**：通过 Visual Studio 扩展市场分发和部署工具，为用户提供可靠、无缝的体验。用户不需要为你的工具单独进行安装和更新。
>
> 在以下场景中，你可以考虑用 [MCP 服务器](./mcp.md)来实现语言模型工具：
>
> - 你已经有一个 MCP 服务器的实现，并且也想在 VS Code 中使用它。
> - 你想在不同的开发环境和平台中复用同一个工具。
> - 你的工具作为一个服务托管在远程。
> - 你不需要访问 VS Code API。
>
> 了解更多关于[工具类型之间的区别](https://code.visualstudio.com/docs/agents/concepts/tools#types-of-tools)的信息。

两者的选择在 [AI 扩展性概览](./ai-extensibility-overview.md) 中有详细对比。

---

<a id="create-a-language-model-tool"></a>
## 创建语言模型工具（Create a language model tool）

> 实现一个语言模型工具包括两个主要部分：
>
> 1. 在扩展的 `package.json` 文件中定义工具的配置。
> 2. 使用[语言模型 API 参考](https://code.visualstudio.com/api/references/vscode-api#lm)，在扩展代码中实现这个工具。
>
> 你可以从一个[基础的示例项目](https://github.com/microsoft/vscode-extension-samples/tree/main/chat-sample)开始。

又是熟悉的“声明 + 实现”：`package.json` 中声明工具的名称、描述、参数格式（给模型看），代码中实现工具被调用时做什么。

<a id="1-static-configuration-in-packagejson"></a>
### 1. package.json 中的静态配置（1. Static configuration in `package.json`）

> 在扩展中定义语言模型工具的第一步，是在扩展的 `package.json` 文件中定义它。这份配置包括工具的名称、描述、输入的 schema，以及其他元数据：

> 1. 在扩展 `package.json` 文件的 `contributes.languageModelTools` 部分中，为你的工具添加一个条目。
>
> 2. 给工具起一个唯一的名称：

| 属性 | 说明 |
| -------- | ----------- |
| `name` | 工具的唯一名称，用于在扩展的实现代码中引用这个工具。名称的格式为 `{verb}_{noun}`（动词_名词）。参见[命名准则](#guidelines-and-conventions)。 |
| `displayName` | 工具的用户友好名称，用于在界面中显示。 |

> 3. 如果这个工具可以与[智能体](https://code.visualstudio.com/docs/agents/overview#built-in-agents)一起使用，或者可以在聊天提示词中用 `#` 引用，就添加以下属性：
>
>     用户可以在聊天视图中启用或禁用这个工具，方式与 [模型上下文协议（MCP）工具](https://code.visualstudio.com/docs/agent-customization/mcp-servers)类似。

| 属性 | 说明 |
| -------- | ----------- |
| `canBeReferencedInPrompt` | 如果这个工具可以与[智能体](https://code.visualstudio.com/docs/agents/overview#built-in-agents)一起使用，或者可以在聊天中被引用，就设为 `true`。 |
| `toolReferenceName` | 用户在聊天提示词中通过 `#` 引用这个工具时使用的名称。 |
| `icon` | 在界面中为这个工具显示的图标。 |
| `userDescription` | 工具的用户友好描述，用于在界面中显示。 |

> 4. 在 `modelDescription` 中添加详细的描述。LLM 会根据这些信息，判断应该在什么上下文中使用你的工具。
>
>     - 这个工具到底做什么？
>     - 它返回什么样的信息？
>     - 什么时候应该使用它，什么时候不应该使用？
>     - 说明工具重要的局限或约束。
>
> 5. 如果工具接收输入参数，就添加一个 `inputSchema` 属性，描述工具的输入参数。
>
>     这个 JSON schema 描述了一个对象，包括工具接收哪些属性作为输入，以及它们是否必填。文件路径应该是绝对路径。
>
>     描述每个参数的作用，以及它与工具功能之间的关系。
>
> 6. 添加一个 `when` 子句，控制工具什么时候可用。
>
>     `languageModelTools` 贡献点让你可以使用 [when 子句](../../references/when-clause-contexts.md)，限制工具什么时候可以在智能体模式中使用，或者可以在提示词中被引用。例如，一个获取调试调用堆栈信息的工具，应该只在用户正在调试时才可用。

```json
"contributes": {
    "languageModelTools": [
        {
            "name": "chat-tools-sample_tabCount",
            ...
            "when": "debugState == 'running'"
        }
    ]
}
```

（这个 `when` 示例只是演示写法，原文借用了下面“标签页计数”工具的名字；对计数标签页的工具来说，加上“正在调试”的条件并没有意义。）

**两种“描述”，给不同的读者看：**

| 属性 | 给谁看 | 写什么 |
|---|---|---|
| `userDescription` | **用户**：在界面的工具列表中显示 | 简短地说明这个工具是干什么的 |
| `modelDescription` | **模型**：模型据此决定要不要调用 | 详细、准确：做什么、返回什么、何时用、何时不用、有什么限制 |

`modelDescription` 是整个工具中**最重要的文字**，写得好不好直接决定模型能不能正确地使用工具。

<details>
<summary>工具定义示例</summary>

> 下面的例子展示了如何定义一个计算某个标签组中活动标签页数量的工具。

```json
"contributes": {
    "languageModelTools": [
        {
            "name": "chat-tools-sample_tabCount",
            "tags": [
                "editors",
                "chat-tools-sample"
            ],
            "toolReferenceName": "tabCount",
            "displayName": "Tab Count",
            "modelDescription": "The number of active tabs in a tab group in VS Code.",
            "userDescription": "Count the number of active tabs in a tab group.",
            "canBeReferencedInPrompt": true,
            "icon": "$(files)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tabGroup": {
                        "type": "number",
                        "description": "The index of the tab group to check. This is optional- if not specified, the active tab group will be checked.",
                        "default": 0
                    }
                }
            }
        }
    ]
}
```

</details>

逐项解读这个示例：

| 字段 | 值 | 说明 |
|---|---|---|
| `name` | `chat-tools-sample_tabCount` | 代码中注册工具时用的名字 |
| `tags` | `["editors", ...]` | 标签，用于分类和筛选工具 |
| `toolReferenceName` | `tabCount` | 用户在聊天中写 `#tabCount` 引用它 |
| `displayName` | `Tab Count` | 界面中显示的名称 |
| `modelDescription` | “VS Code 中某个标签组的活动标签页数量。” | 给模型看的描述 |
| `userDescription` | “计算某个标签组中活动标签页的数量。” | 给用户看的描述 |
| `icon` | `$(files)` | 内置图标 |
| `inputSchema` | 一个可选参数 `tabGroup`（数字） | 参数描述：“要检查的标签组的索引。可选——不指定时检查活动的标签组。” |

（这个示例的 `name` 并不符合下文推荐的 `{verb}_{noun}` 命名格式，按照准则应该命名为类似 `get_tab_count` 的形式。示例的 `modelDescription` 也比较简短，实际使用时可以按照第 4 步的要求写得更详细。）

**`inputSchema` 用的是 JSON Schema**，和 [任务提供者](../task-provider.md) 中 `taskDefinitions` 的 `properties`、[调试器扩展](../debugger-extension.md) 中的 `configurationAttributes` 是同一种格式。常用写法：

```json
"inputSchema": {
  "type": "object",
  "properties": {
    "query":    { "type": "string", "description": "要搜索的关键字" },
    "maxCount": { "type": "number", "description": "最多返回多少条结果，默认 10" }
  },
  "required": ["query"]
}
```

**“文件路径应该是绝对路径”**：模型不知道当前工作目录是什么，如果参数允许相对路径，模型传来的路径很可能对不上。要求绝对路径，可以减少歧义。

<a id="2-tool-implementation"></a>
### 2. 工具的实现（2. Tool implementation）

> 使用[语言模型 API](https://code.visualstudio.com/api/references/vscode-api#lm)实现语言模型工具。包括以下步骤：

> 1. 在扩展激活时，用 [`vscode.lm.registerTool`](https://code.visualstudio.com/api/references/vscode-api#lm.registerTool) 注册工具。
>
>     提供你在 `package.json` 的 `name` 属性中指定的工具名称。
>
>     如果你希望这个工具只供你的扩展私有使用，就跳过注册工具这一步。

```ts
export function registerChatTools(context: vscode.ExtensionContext) {
    context.subscriptions.push(vscode.lm.registerTool('chat-tools-sample_tabCount', new TabCountTool()));
}
```

“私有使用”是指：工具只在你自己的聊天参与者内部使用，不提供给智能体模式。这种情况下，你自己在调用模型时把工具的定义传进去，模型请求调用时再自己执行（见 [聊天参与者](./chat.md) 中关于工具调用的部分），不需要注册到 VS Code 中。

> 2. 创建一个实现了 [`vscode.LanguageModelTool<>`](https://code.visualstudio.com/api/references/vscode-api#LanguageModelTool&lt;T&gt;) 接口的类。
>
> 3. 在 `prepareInvocation` 方法中添加工具的确认消息。
>
>     对于来自扩展的工具，总是会显示一个通用的确认对话框，但工具可以定制确认消息。要给用户足够的上下文，让他们了解工具要做什么。消息可以是一个包含代码块的 `MarkdownString`。
>
>     下面的例子展示了如何为标签页计数工具提供确认消息。

```ts
async prepareInvocation(
    options: vscode.LanguageModelToolInvocationPrepareOptions<ITabCountParameters>,
    _token: vscode.CancellationToken
) {
    const confirmationMessages = {
        title: 'Count the number of open tabs',
        message: new vscode.MarkdownString(
            `Count the number of open tabs?` +
            (options.input.tabGroup !== undefined
                ? ` in tab group ${options.input.tabGroup}`
                : '')
        ),
    };

    return {
        invocationMessage: 'Counting the number of tabs',
        confirmationMessages,
    };
}
```

> 如果 `prepareInvocation` 返回 `undefined`，就会显示通用的确认消息。注意，用户也可以选择“始终允许”某个工具。

`prepareInvocation` 返回的两个字段：

| 字段 | 显示在哪里 | 示例中的值 |
|---|---|---|
| `confirmationMessages` | 执行前弹出的**确认框**：`title` 是标题，`message` 是内容 | “统计打开的标签页数量？（在第 N 个标签组中）” |
| `invocationMessage` | 工具**执行过程中**在聊天中显示的状态文字 | “正在统计标签页数量” |

**为什么要确认？** 工具可能做有副作用的事情（修改文件、发请求、删除数据）。模型可能会误解用户的意思，所以执行前让用户看一眼、点一下“继续”。确认消息要写清楚**这次具体要做什么**（比如要删除哪个文件），而不是笼统地说“要执行工具”，这样用户才能做出判断。

> 4. 定义一个描述工具输入参数的接口。
>
>     这个接口会在 `vscode.LanguageModelTool` 类的 `invoke` 方法中使用。输入参数会根据你在 `package.json` 的 `inputSchema` 中定义的 JSON schema 进行校验。
>
>     下面的例子展示了标签页计数工具的接口。

```ts
export interface ITabCountParameters {
    tabGroup?: number;
}
```

这个 TypeScript 接口要和 `package.json` 中的 `inputSchema` **保持一致**：schema 是给模型和 VS Code 校验用的，接口是给你写代码时的类型提示用的，两者描述的是同一个东西。

> 5. 实现 `invoke` 方法。在处理聊天提示词的过程中调用这个语言模型工具时，会调用这个方法。
>
>     `invoke` 方法通过 `options` 参数接收工具的输入参数。这些参数会根据 `package.json` 中 `inputSchema` 定义的 JSON schema 进行校验。
>
>     发生错误时，抛出一个带有对 LLM 有意义的消息的错误。还可以选择提供指示，告诉 LLM 接下来应该怎么做，比如用不同的参数重试，或者执行另一个操作。
>
>     下面的例子展示了标签页计数工具的实现。工具的结果是一个 `vscode.LanguageModelToolResult` 类型的实例。

```ts
async invoke(
    options: vscode.LanguageModelToolInvocationOptions<ITabCountParameters>,
    _token: vscode.CancellationToken
) {
    const params = options.input;
    if (typeof params.tabGroup === 'number') {
        const group = vscode.window.tabGroups.all[Math.max(params.tabGroup - 1, 0)];
        const nth =
            params.tabGroup === 1
                ? '1st'
                : params.tabGroup === 2
                    ? '2nd'
                    : params.tabGroup === 3
                        ? '3rd'
                        : `${params.tabGroup}th`;
        return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(`There are ${group.tabs.length} tabs open in the ${nth} tab group.`)]);
    } else {
        const group = vscode.window.tabGroups.activeTabGroup;
        return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(`There are ${group.tabs.length} tabs open.`)]);
    }
}
```

> 在 VS Code 扩展示例仓库中查看实现[语言模型工具](https://github.com/microsoft/vscode-extension-samples/blob/main/chat-sample/src/tools.ts)的完整源代码。

几点说明：

- `options.input` 就是模型生成的参数，已经按照 `inputSchema` 校验过。
- `vscode.window.tabGroups` 是 VS Code 的标签页 API：`all` 是所有的标签组（分屏时每一屏是一个组），`activeTabGroup` 是当前的组，`group.tabs` 是组中的标签页。这正是语言模型工具的优势：**可以直接调用 VS Code API**，MCP 工具做不到。
- 返回值是 `LanguageModelToolResult`，里面是一个“部分”（part）数组，最常用的是文本部分 `LanguageModelTextPart`。**结果是给模型看的**，模型会把它组织成自然语言回复给用户，所以结果要写成模型能理解的、清晰的文字。
- （示例代码中有一处不一致：`inputSchema` 的描述说 `tabGroup` 是“索引”、默认值为 0，而代码中却把它当作从 1 开始的序号（`params.tabGroup - 1`），并且传入 0 也会被当作第 1 组。实际开发中要让描述和实现保持一致，否则模型传来的参数会被误解。）

**完整的工具类骨架：**

```ts
interface ITabCountParameters {
  tabGroup?: number;
}

class TabCountTool implements vscode.LanguageModelTool<ITabCountParameters> {
  async prepareInvocation(options: vscode.LanguageModelToolInvocationPrepareOptions<ITabCountParameters>, token: vscode.CancellationToken) {
    // 返回确认消息（可选）
  }

  async invoke(options: vscode.LanguageModelToolInvocationOptions<ITabCountParameters>, token: vscode.CancellationToken) {
    // 执行工具，返回 LanguageModelToolResult
  }
}

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(vscode.lm.registerTool('chat-tools-sample_tabCount', new TabCountTool()));
}
```

**错误处理的写法：** 原文说“抛出一个对 LLM 有意义的错误”，意思是错误信息也会交给模型看，模型会据此决定下一步：

```ts
if (!fileExists) {
  throw new Error(`文件 ${path} 不存在。请先用文件搜索工具找到正确的路径，再重试。`);
}
```

比起 `throw new Error('ENOENT')`，这样的信息能让模型知道出了什么问题、接下来该怎么做。

---

<a id="tool-calling-flow"></a>
## 工具调用流程（Tool-calling flow）

> 当用户发送一个聊天提示词时，会发生以下步骤：
>
> 1. Copilot 根据用户的配置，确定可用的工具列表。
>
>     工具列表包括内置工具、扩展注册的工具，以及来自 [MCP 服务器](https://code.visualstudio.com/docs/agent-customization/mcp-servers)的工具。你可以通过扩展或 MCP 服务器为智能体模式做贡献（图中以绿色表示）。
>
> 2. Copilot 把请求发送给 LLM，并向它提供提示词、聊天上下文，以及要考虑的工具定义列表。
>
>     LLM 生成一个回复，其中可能包含一个或多个调用工具的请求。
>
> 3. 如果需要，Copilot 会用 LLM 提供的参数值调用建议的工具。
>
>     工具的响应可能会导致更多的工具调用请求。
>
> 4. 如果出现错误或后续的工具请求，Copilot 会在工具调用流程中反复迭代，直到所有的工具请求都得到解决。
>
> 5. Copilot 把最终的回复返回给用户，其中可能包含来自多个工具的响应。

这就是前面那张图中橙色的“循环”：

```text
① 确定可用工具（内置 + 扩展注册的 + MCP）
② 发给模型：提示词 + 上下文 + 工具定义列表
③ 模型回复：直接回答？还是要调用工具？
     ├─ 要调用工具 → 执行工具（你的 invoke）→ 把结果加入对话 → 回到 ②
     └─ 直接回答 → ⑤ 返回给用户
```

一个问题可能会触发好几轮工具调用。比如“修复这个文件中的错误”：先调用“读取文件”工具，再调用“获取诊断信息”工具，最后调用“编辑文件”工具。

---

<a id="guidelines-and-conventions"></a>
## 准则与约定（Guidelines and conventions）

> - **命名**：为工具和参数编写清晰、具有描述性的名称。
>
>     - **工具名称**：应该是唯一的，并且清楚地描述它的意图。把工具名称组织成 `{verb}_{noun}` 的格式。例如 `get_weather`、`get_azure_deployment` 或 `get_terminal_output`。
>
>     - **参数名称**：应该描述参数的用途。把参数名称组织成 `{noun}` 的格式。例如 `destination_location`、`ticker` 或 `file_name`。
>
> - **描述**：为工具和参数编写详细的描述。
>
>     - 描述工具做什么，以及什么时候应该、什么时候不应该使用它。例如：“这个工具获取给定地点的天气。”
>     - 描述每个参数的作用，以及它与工具功能之间的关系。例如：“`destination_location` 参数指定要获取天气的地点。它应该是一个有效的地名或坐标。”
>     - 描述工具重要的局限或约束。例如：“这个工具只获取美国境内地点的天气数据。对于其他地区可能无法使用。”
>
> - **用户确认**：为工具调用提供一条确认消息。对于来自扩展的工具，总是会显示一个通用的确认对话框，但工具可以定制确认消息。要给用户足够的上下文，让他们了解工具要做什么。
>
> - **错误处理**：发生错误时，抛出一个带有对 LLM 有意义的消息的错误。还可以选择提供指示，告诉 LLM 接下来应该怎么做，比如用不同的参数重试，或者执行另一个操作。
>
> 在 [OpenAI 文档](https://platform.openai.com/docs/guides/function-calling?api-mode=chat#best-practices-for-defining-functions)和 [Anthropic 文档](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview)中可以获取更多创建工具的最佳实践。

**好的描述和不好的描述：**

| | 不好的 | 好的 |
|---|---|---|
| 工具名 | `tool1`、`dataHelper` | `query_database`、`get_open_tabs` |
| 参数名 | `p`、`input` | `table_name`、`max_rows` |
| 工具描述 | “查询数据。” | “在项目连接的 PostgreSQL 数据库中执行只读的 SELECT 查询，返回最多 100 行结果（JSON 格式）。只用于读取数据，不能用于修改数据或表结构。需要用户已在设置中配置数据库连接。” |
| 参数描述 | “SQL” | “要执行的 SELECT 语句。必须是只读查询，不能包含 INSERT、UPDATE、DELETE 等语句。” |

好的描述要回答四个问题：**做什么、返回什么、何时用（何时不用）、有什么限制**。这和 `package.json` 第 4 步的要求是一致的。

---

<a id="related-content"></a>
## 相关内容（Related content）

> - [语言模型 API 参考](https://code.visualstudio.com/api/references/vscode-api#lm)
> - [在 VS Code 扩展中注册 MCP 服务器](./mcp.md)
> - [在智能体模式中使用 MCP 工具](https://code.visualstudio.com/docs/agent-customization/mcp-servers)

---

## 本篇小结

```text
工具调用：模型不执行代码，只生成“调用哪个工具 + 什么参数”；VS Code 执行后把结果交回模型

package.json：contributes.languageModelTools
  name（{verb}_{noun}）、displayName、modelDescription（给模型，最重要）、userDescription（给用户）
  inputSchema（JSON Schema；文件路径用绝对路径）、when
  canBeReferencedInPrompt + toolReferenceName（用户可以 #引用）、icon、tags

代码
  vscode.lm.registerTool(name, new MyTool())（私有工具可以不注册）
  class MyTool implements vscode.LanguageModelTool<IParams>
    prepareInvocation → { invocationMessage, confirmationMessages }（执行前的确认）
    invoke(options) → options.input 是参数 → 返回 LanguageModelToolResult([new LanguageModelTextPart(...)])
  错误：抛出对模型有意义的错误信息，可以附带下一步建议

流程：确定工具 → 发给模型 → 模型请求调用 → 执行 → 结果交回模型 → 循环直到得出最终回答
```
