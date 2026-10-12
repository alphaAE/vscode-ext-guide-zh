# 聊天参与者 API（Chat Participant API）

> 原文：[Chat Participant API](https://code.visualstudio.com/api/extension-guides/ai/chat)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/ai/chat.md`（DateApproved: 10/7/2026）

> 聊天参与者是专门的助手，让用户可以用特定领域的专家来扩展 [VS Code 中的聊天](https://code.visualstudio.com/docs/chat/chat-overview)。用户通过 @-提及来调用一个聊天参与者，然后由这个参与者负责处理用户的自然语言提示词。
>
> 在这篇扩展指南中，你将学习如何使用聊天参与者 API 创建一个聊天参与者。
>
> VS Code 有几个内置的聊天参与者，比如 `@vscode`、`@terminal` 或 `@workspace`。它们针对回答各自领域的问题进行了优化。
>
> 聊天参与者不同于[语言模型工具](./tools.md)，后者是在 LLM 编排解决用户聊天提示词所需的步骤时被调用的。聊天参与者接收用户的提示词，并自己编排所需的任务。

回顾 [AI 扩展性概览](./ai-extensibility-overview.md) 中的对比：**工具**是 AI 手里的一件工具，由 AI 决定什么时候用；**聊天参与者**是一个独立的“专家”，用户 `@` 它之后，整个回答过程（用什么提示词、调用哪个模型、调用哪些工具、如何展示）全部由你的代码控制。

---

<a id="why-implement-a-chat-participant-in-your-extension"></a>
## 为什么要在扩展中实现聊天参与者？（Why implement a chat participant in your extension?）

> 在扩展中实现聊天参与者有以下几个好处：
>
> - **扩展聊天**：提供专门的、特定于领域的知识和专业能力。例如，内置的 `@vscode` 参与者了解 VS Code 及其扩展 API。
> - **掌控对话**：管理从用户的聊天提示词到回复的整个过程。
> - **与 VS Code 深度集成**：可以使用大量的扩展 API。例如，使用[调试 API](../debugger-extension.md) 获取当前的调试上下文，并把它作为工具功能的一部分。
> - **分发和部署**：通过 Visual Studio 扩展市场分发和部署聊天参与者，为用户提供可靠、无缝的体验。用户不需要单独的安装和更新过程。
>
> 如果你想提供可以在自主的、智能体式的编码会话中被自动调用的特定领域能力，可以考虑实现一个[语言模型工具](./tools.md)或 [MCP 服务器](./mcp.md)。关于不同选项的详细信息以及如何决定使用哪种方式，请参阅 [AI 扩展性概览](./ai-extensibility-overview.md)。

---

<a id="parts-of-the-chat-user-experience"></a>
## 聊天用户体验的组成部分（Parts of the chat user experience）

> 下面的截图展示了 VS Code 聊天体验中，示例扩展涉及的不同聊天概念。

![聊天概念说明](../images/ai/chat/chat.png)

> 1. 使用 `@` 语法调用 `@cat` 聊天参与者
> 2. 使用 `/` 语法调用 `/teach` 命令
> 3. 用户提供的查询，也叫用户提示词（user prompt）
> 4. 图标和参与者的 `fullName`，表示 Copilot 正在使用 `@cat` 聊天参与者
> 5. 由 `@cat` 提供的 Markdown 回复
> 6. Markdown 回复中包含的代码片段
> 7. `@cat` 回复中包含的按钮，这个按钮会调用一个 VS Code 命令
> 8. 聊天参与者提供的建议的[后续问题](#4-register-follow-up-requests)
> 9. 聊天输入框，其中的占位文字由聊天参与者的 `description` 属性提供

对照截图，每一部分对应的代码：

| 编号 | 界面元素 | 截图中 | 对应的配置或代码 |
|---|---|---|---|
| 1 | 参与者 | `@cat` | `package.json` 中的 `name` |
| 2 | 斜杠命令 | `/teach` | `package.json` 中的 `commands`；代码中 `request.command` |
| 3 | 用户提示词 | “a computer science topic” | 代码中 `request.prompt` |
| 4 | 回复的标题 | 猫的头像 + “Cat” | `iconPath` + `package.json` 中的 `fullName` |
| 5 | Markdown 回复 | 关于递归的解释 | `stream.markdown(...)` |
| 6 | 代码块 | `countdown` 函数 | `stream.markdown` 中的 ` ``` ` 代码块 |
| 7 | 按钮 | “Use Cat Names in Editor” | `stream.button(...)` |
| 8 | 后续问题 | “Play with the cat” | `followupProvider` |
| 9 | 输入框的占位文字 | “Meow! What can I teach you?” | `package.json` 中的 `description` |

---

<a id="create-a-chat-participant"></a>
## 创建聊天参与者（Create a chat participant）

> 实现一个聊天参与者包括以下几个部分：
>
> 1. 在扩展的 `package.json` 文件中定义聊天参与者。
> 2. 实现一个请求处理函数，处理用户的聊天提示词并返回回复。
> 3. （可选）实现聊天斜杠命令，为用户提供执行常见任务的简写方式。
> 4. （可选）定义建议的后续问题。
> 5. （可选）实现参与者检测，让 VS Code 在用户没有显式提及的情况下，自动把聊天请求路由给合适的聊天参与者。
>
> 你可以从一个[基础的示例项目](https://github.com/microsoft/vscode-extension-samples/tree/main/chat-sample)开始。

![展示扩展如何为聊天做贡献的示意图](../images/ai/chat/diagram.png)

图中，整个大框是“聊天扩展”（Chat extension）。实线表示必须的部分，虚线表示可选的部分：

- **必须**：注册聊天参与者（Register chat participant）→ 处理用户查询（蓝色框，Handle the user query）：定义请求处理函数 → 判断请求意图 → 处理请求 → 返回聊天回复。处理请求的过程中，通过**语言模型 API**（Language Model API）调用语言模型。
- **可选**：注册命令（Register commands）、注册后续问题（Register follow-ups）、注册聊天变量（Register chat variables）。

<a id="1-register-the-chat-participant"></a>
### 1. 注册聊天参与者（1. Register the chat participant）

> 创建聊天扩展的第一步，是在 `package.json` 中注册它，包括以下属性：
>
> - `id`：聊天参与者的唯一标识符，在 `package.json` 文件中定义。
> - `name`：聊天参与者的简短名称，用于在聊天中进行 @-提及。
> - `fullName`：聊天参与者的全名，显示在回复的标题区域。
> - `description`：对聊天参与者用途的简要描述，用作聊天输入框中的占位文字。
> - `isSticky`：一个布尔值，表示聊天参与者在回复之后是否保持在聊天输入框中。

```json
"contributes": {
        "chatParticipants": [
            {
                "id": "chat-sample.my-participant",
                "name": "my-participant",
                "fullName": "My Participant",
                "description": "What can I teach you?",
                "isSticky": true
            }
        ]
}
```

**`isSticky` 的效果：** 设为 `true` 时，用户 `@cat` 提问并收到回复后，输入框中会自动保留 `@cat`，下一个问题不用再输入 `@cat`，适合需要连续对话的参与者。

> 我们建议 `name` 使用小写，`fullName` 使用标题式大写，以便与现有的聊天参与者保持一致。了解更多关于[聊天参与者命名约定](#chat-participant-naming-conventions)的信息。

> **注意**
>
> 有些参与者名称是保留的。如果你使用了这样的保留名称，VS Code 会显示你的聊天参与者的完全限定名称（包括扩展 ID）。

<a id="2-implement-a-request-handler"></a>
### 2. 实现请求处理函数（2. Implement a request handler）

> 使用[聊天参与者 API](https://code.visualstudio.com/api/references/vscode-api#chat)实现聊天参与者。包括以下步骤：

> 1. 在扩展激活时，用 `vscode.chat.createChatParticipant` 创建参与者。
>
>     提供你在 `package.json` 中定义的 ID，以及对你在下一步中实现的请求处理函数的引用。

```typescript
export function activate(context: vscode.ExtensionContext) {

    // 注册聊天参与者及其请求处理函数
    const cat = vscode.chat.createChatParticipant('chat-sample.my-participant', handler);

    // 可选：为 @cat 设置一些属性
    cat.iconPath = vscode.Uri.joinPath(context.extensionUri, 'cat.jpeg');

    // 在这里添加聊天请求处理函数
}
```

`createChatParticipant` 返回的参与者对象也是一个 Disposable，实际代码中应该放进 `context.subscriptions`。

> 2. 在 `activate` 函数中，定义 `vscode.ChatRequestHandler` 请求处理函数。
>
>     请求处理函数负责处理用户在 VS Code 聊天视图中的聊天请求。每当用户在聊天输入框中输入一个提示词，就会调用聊天请求处理函数。

```typescript
const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken): Promise<ICatChatResult> => {

    // 聊天请求处理函数的实现写在这里

};
```

处理函数的四个参数：

| 参数 | 类型 | 内容 |
|---|---|---|
| `request` | `ChatRequest` | 这一次的请求：`prompt`（用户输入的文字）、`command`（斜杠命令，没有则为 `undefined`）、`references`（用户附加的上下文，如文件）、`model`（用户在下拉框中选择的模型）、`toolReferences`、`toolInvocationToken` |
| `context` | `ChatContext` | 聊天上下文，主要是 `history`（之前的对话） |
| `stream` | `ChatResponseStream` | 用来**输出回复**：`markdown()`、`button()`、`progress()` 等 |
| `token` | `CancellationToken` | 用户点击停止时被取消 |

返回值是一个 `ChatResult`（示例中的 `ICatChatResult` 是扩展自己定义的、带 `metadata` 的类型），可以在其中附带元数据，供后续问题等使用。

> 3. 从 `vscode.ChatRequest` 中判断用户的意图。
>
>     要判断用户请求的意图，可以引用 `vscode.ChatRequest` 参数，访问用户的提示词文本、命令和聊天位置。
>
>     你也可以选择利用语言模型来判断用户的意图，而不是使用传统的逻辑。在 `request` 对象中，你会得到一个语言模型实例，它是用户在聊天的模型下拉框中选择的那个模型。了解如何在扩展中使用[语言模型 API](./language-model.md)。
>
>     下面的代码片段展示了先使用命令、再使用用户提示词来判断用户意图的基本结构：

```typescript
const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken): Promise<ICatChatResult> => {

    // 检查是否是 `teach` 命令
    if (request.command == 'teach') {

        // 在这里添加处理教学场景的逻辑
        doTeaching(request.prompt, request.variables);

    } else {

        // 判断用户的意图
        const intent = determineUserIntent(request.prompt, request.variables, request.model);

        // 在这里添加处理其他场景的逻辑
    }
};
```

（原文代码中用到的 `request.variables` 是早期版本的属性名。在当前的类型定义（`@types/vscode` 1.140）中，`ChatRequest` 上没有 `variables`，用户附加的上下文在 `request.references` 中。原文上一段提到的“聊天位置”（location）属性，在当前的稳定 API 中也没有。`doTeaching`、`determineUserIntent` 是示意用的函数。）

> 4. 添加处理用户请求的逻辑。
>
>     聊天扩展通常使用 `request.model` 语言模型实例来处理请求。在这种情况下，你可以根据用户的意图调整语言模型的提示词。
>
>     或者，你可以通过调用后端服务、使用传统的编程逻辑，或者结合所有这些方式来实现扩展的逻辑。例如，你可以调用网页搜索来收集额外的信息，然后把这些信息作为上下文提供给语言模型。
>
>     在处理当前请求时，你可能想参考之前的聊天消息。例如，如果之前的回复返回了一段 C# 代码片段，用户当前的请求可能是“给出 Python 版本的代码”。[了解如何使用聊天消息历史](#use-the-chat-message-history)。
>
>     如果你想根据聊天输入的位置（聊天视图、快速聊天、行内聊天）以不同的方式处理请求，可以使用 `vscode.ChatRequest` 的 `location` 属性。例如，如果用户从终端的行内聊天中发送请求，你可能会查找一条 shell 命令；而如果用户使用的是聊天视图，你可以返回一个更详细的回复。

**使用 `request.model` 的原因**（[语言模型 API](./language-model.md) 中也强调过）：用户在聊天界面的下拉框中选了哪个模型，你就应该用哪个，而不是自己用 `selectChatModels` 另选一个。

> 5. 把聊天回复返回给用户。
>
>     处理完请求后，你需要在聊天视图中向用户返回一个回复。可以使用流式传输来回应用户的查询。
>
>     回复可以包含不同类型的内容：Markdown、图片、引用、进度、按钮和文件树。

![cat 扩展的回复，其中包含代码、Markdown 和一个按钮](../images/ai/chat/stream.png)

> 扩展可以这样使用回复流：

```typescript
stream.progress('Picking the right topic to teach...');
stream.markdown(`\`\`\`typescript
const myStack = new Stack();
myStack.push(1); // pushing a number on the stack (or let's say, adding a fish to the stack)
myStack.push(2); // adding another fish (number 2)
console.log(myStack.pop()); // eating the top fish, will output: 2
\`\`\`
So remember, Code Kitten, in a stack, the last fish in is the first fish out - which we tech cats call LIFO (Last In, First Out).`);

stream.button({
    command: 'cat.meow',
    title: vscode.l10n.t('Meow!'),
    arguments: []
});
```

这段代码先显示一条进度消息（“正在挑选要教的主题……”），然后输出一段包含代码块的 Markdown（用“往栈里放鱼、吃最上面的鱼”比喻栈的后进先出），最后显示一个“Meow!”按钮，点击时执行 `cat.meow` 命令。

> 了解更多关于[支持的聊天回复输出类型](#supported-chat-response-output-types)的信息。
>
> 在实践中，扩展通常会向语言模型发送一个请求。拿到语言模型的回复后，它们可能会进一步处理，并决定是否要把一些内容以流的形式传回给用户。VS Code 聊天 API 是基于流的，与基于流的[语言模型 API](./language-model.md)兼容。这让扩展可以持续地报告进度和结果，以提供流畅的用户体验。了解如何使用[语言模型 API](./language-model.md)。

**把上面五步合起来，一个完整的、可以运行的最小聊天参与者（补充）：**

```ts
import * as vscode from 'vscode';

const CAT_PROMPT = '你是一只猫。请用猫的口吻、用中文、借助猫的比喻来解释编程概念，并附上代码示例。';

export function activate(context: vscode.ExtensionContext) {
  const handler: vscode.ChatRequestHandler = async (request, chatContext, stream, token) => {
    // 1. 构建提示词：指令 + 历史对话 + 本次的问题
    const messages = [vscode.LanguageModelChatMessage.User(CAT_PROMPT)];

    for (const turn of chatContext.history) {
      if (turn instanceof vscode.ChatRequestTurn) {
        messages.push(vscode.LanguageModelChatMessage.User(turn.prompt));
      } else if (turn instanceof vscode.ChatResponseTurn) {
        // 把之前回复中的 Markdown 文本拼起来，作为助手消息
        const text = turn.response
          .filter((part): part is vscode.ChatResponseMarkdownPart => part instanceof vscode.ChatResponseMarkdownPart)
          .map(part => part.value.value)
          .join('');
        messages.push(vscode.LanguageModelChatMessage.Assistant(text));
      }
    }

    const topic = request.command === 'teach' ? `请随机挑一个计算机概念讲解。${request.prompt}` : request.prompt;
    messages.push(vscode.LanguageModelChatMessage.User(topic));

    // 2. 用用户选择的模型发送请求
    const response = await request.model.sendRequest(messages, {}, token);

    // 3. 把模型的回复一边生成，一边输出到聊天中
    for await (const fragment of response.text) {
      stream.markdown(fragment);
    }

    return { metadata: { command: request.command } };
  };

  const cat = vscode.chat.createChatParticipant('chat-sample.cat', handler);
  cat.iconPath = vscode.Uri.joinPath(context.extensionUri, 'cat.jpeg');
  context.subscriptions.push(cat);
}
```

对应的 `package.json` 中 `id` 要写成 `chat-sample.cat`。这段代码中的每一部分都对应了本篇和 [语言模型 API](./language-model.md) 中讲过的内容：历史对话见下文[使用聊天消息历史](#use-the-chat-message-history)，`request.model.sendRequest` 和 `for await` 见语言模型 API。

<a id="3-register-slash-commands"></a>
### 3. 注册斜杠命令（3. Register slash commands）

> 聊天参与者可以贡献斜杠命令，它们是扩展所提供的特定功能的快捷方式。用户可以在聊天中通过 `/` 语法引用斜杠命令，例如 `/explain`。
>
> 回答问题时的任务之一是判断用户的意图。例如，VS Code 可以推断出 `Create a new workspace with Node.js Express Pug TypeScript` 的意思是你想要一个新项目，但 `@workspace /new Node.js Express Pug TypeScript` 更明确、更简洁，还能节省打字的时间。如果你在聊天输入框中输入 `/`，VS Code 会列出已注册的命令及其描述。

![@workspace 在聊天中的命令列表](../images/ai/chat/commands.png)

> 聊天参与者可以在 `package.json` 中添加斜杠命令及其描述，从而贡献斜杠命令：

```typescript
"contributes": {
    "chatParticipants": [
        {
            "id": "chat-sample.cat",
            "name": "cat",
            "fullName": "Cat",
            "description": "Meow! What can I teach you?",
            "isSticky": true,
            "commands": [
                {
                    "name": "teach",
                    "description": "Pick at random a computer science concept then explain it in purfect way of a cat"
                },
                {
                    "name": "play",
                    "description": "Do whatever you want, you are a cat after all"
                }
            ]
        }
    ]
}
```

（这段是 `package.json` 中的 JSON 配置，原文代码块标注成了 `typescript`。两个命令的描述分别是：“随机挑选一个计算机科学概念，然后用猫那种完美（purfect，猫叫声的谐音双关）的方式解释它”和“想做什么就做什么，毕竟你是一只猫”。）

用户输入 `@cat /teach` 时，处理函数中 `request.command` 的值就是 `'teach'`（不带斜杠），`request.prompt` 是命令后面的文字。

> 了解更多关于[斜杠命令命名约定](#slash-command-naming-conventions)的信息。

<a id="4-register-follow-up-requests"></a>
### 4. 注册后续问题（4. Register follow-up requests）

> 每次聊天请求之后，VS Code 都会调用后续问题提供者，获取要显示给用户的建议后续问题。用户可以选择某个后续问题，并立即把它发送给聊天扩展。使用 [`ChatFollowupProvider`](https://code.visualstudio.com/api/references/vscode-api#ChatFollowupProvider) API 注册 [`ChatFollowup`](https://code.visualstudio.com/api/references/vscode-api#ChatFollowup) 类型的后续问题。
>
> 下面的代码片段展示了如何在聊天扩展中注册后续问题：

```typescript
cat.followupProvider = {
    provideFollowups(result: ICatChatResult, context: vscode.ChatContext, token: vscode.CancellationToken) {
        if (result.metadata.command === 'teach') {
            return [{
                prompt: 'let us play',
                label: vscode.l10n.t('Play with the cat')
            } satisfies vscode.ChatFollowup];
        }
    }
};
```

> **提示**
>
> 后续问题应该写成问题或指示，而不仅仅是简短的命令。

- `provideFollowups` 的第一个参数 `result` 就是请求处理函数的**返回值**。这就是为什么处理函数要在返回值的 `metadata` 中记录 `command`：后续问题提供者据此判断上一次做了什么，给出相应的建议。
- `label` 是显示在界面上的文字（截图中的 “Play with the cat”），`prompt` 是用户点击后实际发送的内容。
- `satisfies vscode.ChatFollowup` 是 TypeScript 的语法，用来检查这个对象符合 `ChatFollowup` 类型，同时保留它原本的具体类型。

<a id="5-implement-participant-detection"></a>
### 5. 实现参与者检测（5. Implement participant detection）

> 为了让用户更容易通过自然语言使用聊天参与者，你可以实现参与者检测。参与者检测是一种自动把用户的问题路由给合适参与者的方式，用户不必在提示词中显式地提及参与者。例如，如果用户问“我怎样给我的项目添加一个登录页面？”，这个问题会被自动路由给 `@workspace` 参与者，因为它可以回答关于用户项目的问题。
>
> VS Code 使用聊天参与者的描述和示例来决定把聊天提示词路由给哪个参与者。你可以在扩展 `package.json` 文件的 `disambiguation` 属性中指定这些信息。`disambiguation` 属性包含一个检测类别的列表，每个类别都有一个描述和一些示例。

| 属性 | 说明 | 示例 |
|----------|-------------|----------|
| `category` | 检测类别。如果参与者有多种用途，可以为每种用途设一个类别。 | `cat`、`workspace_questions`、`web_questions` |
| `description` | 详细描述适合这个参与者回答的问题类型。 | `The user wants to learn a specific computer science topic in an informal way.`（用户想以非正式的方式学习某个特定的计算机科学主题。）、`The user just wants to relax and see the cat play.`（用户只是想放松一下，看猫玩耍。） |
| `examples` | 一些有代表性的示例问题。 | `Teach me C++ pointers using metaphors`（用比喻教我 C++ 指针）、`Explain to me what is a linked list in a simple way`（用简单的方式给我解释什么是链表）、`Can you show me a cat playing with a laser pointer?`（你能给我看一只猫玩激光笔吗？） |

> 你可以为整个聊天参与者定义参与者检测，也可以为特定的命令定义，或者两者结合。
>
> 下面的代码片段展示了如何在参与者级别实现参与者检测。

```json
"contributes": {
    "chatParticipants": [
        {
            "id": "chat-sample.cat",
            "fullName": "Cat",
            "name": "cat",
            "description": "Meow! What can I teach you?",

            "disambiguation": [
                {
                    "category": "cat",
                    "description": "The user wants to learn a specific computer science topic in an informal way.",
                    "examples": [
                        "Teach me C++ pointers using metaphors",
                        "Explain to me what is a linked list in a simple way",
                        "Can you explain to me what is a function in programming?"
                    ]
                }
            ]
        }
    ]
}
```

> 类似地，你也可以在命令级别配置参与者检测：为 `commands` 属性中的一个或多个条目添加一个 `disambiguation` 属性。
>
> 应用以下准则，提高扩展参与者检测的准确性：
>
> - **要具体**：描述和示例应该尽可能具体，以免与其他参与者冲突。避免在参与者和命令的信息中使用通用的术语。
> - **使用示例**：示例应该代表适合这个参与者回答的那类问题。使用同义词和不同的说法，覆盖范围广泛的用户查询。
> - **使用自然语言**：描述和示例应该用自然语言来写，就像你在向用户解释这个参与者一样。
> - **测试检测效果**：用各种不同的示例问题测试参与者检测，并确认与内置的聊天参与者没有冲突。

> **注意**
>
> 在参与者检测中，内置的聊天参与者优先。例如，一个处理工作区文件的聊天参与者，可能会与内置的 `@workspace` 参与者发生冲突。

如果你的用户主要使用中文提问，`examples` 中也可以加入中文的示例问题，帮助更准确地识别中文提问。

---

<a id="use-the-chat-message-history"></a>
## 使用聊天消息历史（Use the chat message history）

> 参与者可以访问当前聊天会话的消息历史。参与者只能访问提及了它的那些消息。`history` 中的一项要么是 `ChatRequestTurn`，要么是 `ChatResponseTurn`。例如，使用下面的代码片段，获取用户在当前聊天会话中发给你的参与者的所有之前的请求：

```typescript
const previousMessages = context.history.filter(h => h instanceof vscode.ChatRequestTurn);
```

> 历史记录不会被自动包含在提示词中，是否把历史作为额外的上下文添加到发给语言模型的消息中，由参与者自己决定。

| 历史项类型 | 表示 | 常用属性 |
|---|---|---|
| `ChatRequestTurn` | 用户之前的一次提问 | `prompt`、`command`、`references` |
| `ChatResponseTurn` | 参与者之前的一次回复 | `response`（回复的各个部分）、`result` |

“只能访问提及了它的消息”：用户先问了 `@workspace` 一个问题，再问 `@cat`，`@cat` 看不到之前与 `@workspace` 的对话。

如何把历史转换成发给模型的消息，见上文补充的完整示例。

---

<a id="supported-chat-response-output-types"></a>
## 支持的聊天回复输出类型（Supported chat response output types）

> 要返回对一个聊天请求的回复，需要使用 [`ChatRequestHandler`](https://code.visualstudio.com/api/references/vscode-api#ChatRequestHandler) 上的 [`ChatResponseStream`](https://code.visualstudio.com/api/references/vscode-api#ChatResponseStream) 参数。
>
> 下面列出了聊天视图中聊天回复的输出类型。一个聊天回复可以组合多种不同的输出类型。

先看总览（以 `@types/vscode` 1.140 为准）：

| 输出类型 | 方法 | 用途 |
|---|---|---|
| Markdown | `stream.markdown(文本)` | 文字、图片、代码块、命令链接 |
| 命令按钮 | `stream.button(命令)` | 点击执行一个命令 |
| 文件树 | `stream.filetree(树, 基础位置)` | 显示一个可预览的文件树 |
| 进度消息 | `stream.progress(文本)` | 长时间操作时显示中间状态 |
| 引用 | `stream.reference(位置)` | 在引用列表中标明用到了哪些资料 |
| 行内引用 | `stream.anchor(位置, 标题?)` | 在文字中插入一个指向文件或符号的链接 |

<a id="markdown"></a>
### Markdown

> 渲染一段 Markdown 文本、简单文本或图片。你可以使用 [CommonMark](https://commonmark.org/) 规范中的任何 Markdown 语法。使用 [`ChatResponseStream.markdown`](https://code.visualstudio.com/api/references/vscode-api#ChatResponseStream.markdown) 方法并提供 Markdown 文本。
>
> 示例代码片段：

```typescript
// 渲染 Markdown 文本
stream.markdown('# This is a title \n');
stream.markdown('This is stylized text that uses _italics_ and **bold**. ');
stream.markdown('This is a [link](https://code.visualstudio.com).\n\n');
stream.markdown('![VS Code](https://code.visualstudio.com/assets/favicon.ico)');
```

多次调用 `markdown` 的内容会依次拼接在一起，所以可以边生成边输出。

<a id="code-block"></a>
### 代码块（Code block）

> 渲染一个代码块，它支持智能提示、代码格式化，以及把代码应用到活动编辑器的交互控件。要显示代码块，使用 [`ChatResponseStream.markdown`](https://code.visualstudio.com/api/references/vscode-api#ChatResponseStream.markdown) 方法，并使用 Markdown 的代码块语法（使用反引号）。
>
> 示例代码片段：

```typescript
// 渲染一个用户可以交互的代码块
stream.markdown('```bash\n');
stream.markdown('```ls -l\n');
stream.markdown('```');
```

（原文示例的第二行多写了三个反引号，正确的写法是：）

```typescript
stream.markdown('```bash\n');
stream.markdown('ls -l\n');
stream.markdown('```');
```

<a id="command-link"></a>
### 命令链接（Command link）

> 在聊天回复中渲染一个行内链接，用户可以选择它来调用一个 VS Code 命令。要显示命令链接，使用 [`ChatResponseStream.markdown`](https://code.visualstudio.com/api/references/vscode-api#ChatResponseStream.markdown) 方法，并使用 Markdown 的链接语法 `[链接文字](command:commandId)`，在 URL 中提供命令 ID。例如，下面的链接会打开命令面板：`[Command Palette](command:workbench.action.showCommands)`。
>
> 当你从某个服务加载 Markdown 文本时，为了防止命令注入，必须使用一个 [`vscode.MarkdownString`](https://code.visualstudio.com/api/references/vscode-api#MarkdownString) 对象，并把它的 `isTrusted` 属性设置为受信任的 VS Code 命令 ID 列表。要让命令链接生效，这个属性是必需的。如果没有设置 `isTrusted` 属性，或者某个命令没有被列出，这个命令链接就不会生效。
>
> 示例代码片段：

```typescript
// 使用命令 URI，从 Markdown 链接到命令
let markdownCommandString: vscode.MarkdownString = new vscode.MarkdownString(`[Use cat names](command:${CAT_NAMES_COMMAND_ID})`);
markdownCommandString.isTrusted = { enabledCommands: [ CAT_NAMES_COMMAND_ID ] };

stream.markdown(markdownCommandString);
```

> 如果命令需要参数，你需要先把参数进行 JSON 编码，然后把 JSON 字符串编码为 URI 组件。然后把编码后的参数作为查询字符串追加到命令链接后面。

```typescript
// 对命令参数进行编码
const encodedArgs = encodeURIComponent(JSON.stringify(args));

// 使用带参数的命令 URI，从 Markdown 链接到命令
let markdownCommandString: vscode.MarkdownString = new vscode.MarkdownString(`[Use cat names](command:${CAT_NAMES_COMMAND_ID}?${encodedArgs})`);
markdownCommandString.isTrusted = { enabledCommands: [ CAT_NAMES_COMMAND_ID ] };

stream.markdown(markdownCommandString);
```

这就是 [命令指南](../command.md#command-uris) 中详细讲解过的**命令 URI**，`isTrusted` 的两种写法和安全问题也在那里介绍过。在聊天中这一点尤其重要：模型生成的回复内容是不可控的，如果设置 `isTrusted = true`，模型的回复中一旦出现了 `command:` 链接，用户点击后就会执行任意命令。所以一定要用 `enabledCommands` 只放行你需要的命令。

<a id="command-button"></a>
### 命令按钮（Command button）

> 渲染一个调用 VS Code 命令的按钮。这个命令可以是内置命令，也可以是你在扩展中定义的命令。使用 [`ChatResponseStream.button`](https://code.visualstudio.com/api/references/vscode-api#ChatResponseStream.button) 方法，并提供按钮文字和命令 ID。
>
> 示例代码片段：

```typescript
// 渲染一个触发 VS Code 命令的按钮
stream.button({
    command: 'my.command',
    title: vscode.l10n.t('Run my command')
});
```

需要传参数时，加上 `arguments: [...]`，命令的处理函数会收到这些参数。

<a id="file-tree"></a>
### 文件树（File tree）

> 渲染一个文件树控件，让用户可以预览单个文件。例如，在建议创建一个新工作区时显示工作区的预览。使用 [`ChatResponseStream.filetree`](https://code.visualstudio.com/api/references/vscode-api#ChatResponseStream.filetree) 方法，并提供一个文件树元素数组以及这些文件的基础位置（文件夹）。
>
> 示例代码片段：

```typescript
// 创建一个文件树实例
var tree: vscode.ChatResponseFileTree[] = [
    { name: 'myworkspace', children: [
        { name: 'README' },
        { name: 'app.js' },
        { name: 'package.json' }
    ]}
];

// 在一个基础位置上渲染文件树控件
stream.filetree(tree, baseLocation);
```

`baseLocation` 是一个 `Uri`，表示这棵树的根目录在哪里。用户点击树中的文件时，VS Code 会打开 `baseLocation` 下对应路径的文件。

<a id="progress-message"></a>
### 进度消息（Progress message）

> 在长时间运行的操作中渲染一条进度消息，给用户提供中间的反馈。例如，报告一个多步骤操作中每一步的完成情况。使用 [`ChatResponseStream.progress`](https://code.visualstudio.com/api/references/vscode-api#ChatResponseStream.progress) 方法并提供消息。
>
> 示例代码片段：

```typescript
// 渲染一条进度消息
stream.progress('Connecting to the database.');
```

<a id="reference"></a>
### 引用（Reference）

> 在引用列表中为一个外部 URL 或编辑器位置添加一个引用，表明你使用了哪些信息作为上下文。使用 [`ChatResponseStream.reference`](https://code.visualstudio.com/api/references/vscode-api#ChatResponseStream.reference) 方法并提供引用的位置。
>
> 示例代码片段：

```typescript
const fileUri: vscode.Uri = vscode.Uri.file('/path/to/workspace/app.js');  // 在 Windows 上，路径的格式应该是 'c:\\path\\to\\workspace\\app.js'
const fileRange: vscode.Range = new vscode.Range(0, 0, 3, 0);
const externalUri: vscode.Uri = vscode.Uri.parse('https://code.visualstudio.com');

// 添加对整个文件的引用
stream.reference(fileUri);

// 添加对文件中某个特定选区的引用
stream.reference(new vscode.Location(fileUri, fileRange));

// 添加对一个外部 URL 的引用
stream.reference(externalUri);
```

引用会显示在回复上方一个可展开的“已使用 N 个引用”列表中，让用户知道回答依据的是哪些文件或网页，可以点击查看。

<a id="inline-reference"></a>
### 行内引用（Inline reference）

> 添加一个指向 URI 或编辑器位置的行内引用。使用 [`ChatResponseStream.anchor`](https://code.visualstudio.com/api/references/vscode-api#ChatResponseStream.anchor) 方法，并提供锚点的位置和可选的标题。要引用一个符号（例如一个类或变量），需要使用编辑器中的一个位置。
>
> 示例代码片段：

```typescript
const symbolLocation: vscode.Uri = vscode.Uri.parse('location-to-a-symbol');

// 渲染一个指向工作区中某个符号的行内锚点
stream.anchor(symbolLocation, 'MySymbol');
```

和 `reference` 的区别：`reference` 显示在单独的引用列表中；`anchor` 显示在正文文字之间，比如“问题出在 [MySymbol] 这个类中”，点击就跳转过去。

> **重要**：只有当图片和链接来自受信任域名列表中的域名时，它们才可用。了解更多关于 [VS Code 中的链接保护](https://code.visualstudio.com/docs/editing/editingevolved#outgoing-link-protection)的信息。

---

<a id="implement-tool-calling"></a>
## 实现工具调用（Implement tool calling）

> 为了回应用户的请求，聊天扩展可以调用语言模型工具。了解更多关于[语言模型工具](./tools.md)和[工具调用流程](./tools.md#tool-calling-flow)的信息。
>
> 你可以用两种方式实现工具调用：
>
> - 使用 [`@vscode/chat-extension-utils` 库](https://www.npmjs.com/package/@vscode/chat-extension-utils)，简化在聊天扩展中调用工具的过程。
> - 自己实现工具调用，这让你可以更好地控制工具调用的过程。例如，执行额外的校验，或者在把工具的响应发给 LLM 之前，以特定的方式处理它们。

在智能体模式中，工具调用的循环由 Copilot 负责。而在你自己的聊天参与者中，**这个循环要由你来实现**：把工具定义发给模型 → 模型请求调用工具 → 执行工具 → 把结果交回模型 → 重复，直到模型给出最终回答（见 [语言模型工具](./tools.md#tool-calling-flow) 中的流程）。

<a id="implement-tool-calling-with-the-chat-extension-library"></a>
### 使用聊天扩展库实现工具调用（Implement tool calling with the chat extension library）

> 你可以使用 [`@vscode/chat-extension-utils` 库](https://www.npmjs.com/package/@vscode/chat-extension-utils)，简化在聊天扩展中调用工具的过程。
>
> 在你的[聊天参与者](./chat.md)的 `vscode.ChatRequestHandler` 函数中实现工具调用。

> 1. 确定当前聊天上下文中相关的工具。可以用 `vscode.lm.tools` 访问所有可用的工具。
>
>     下面的代码片段展示了如何过滤工具，只保留带有特定标签的工具。

```ts
const tools = request.command === 'all' ?
    vscode.lm.tools :
    vscode.lm.tools.filter(tool => tool.tags.includes('chat-tools-sample'));
```

`vscode.lm.tools` 是所有已注册的工具（包括其他扩展注册的）。`tags` 就是 [语言模型工具](./tools.md) 中 `package.json` 里定义的 `tags`。

> 2. 使用 `sendChatParticipantRequest` 把请求和工具定义发送给 LLM。

```ts
const libResult = chatUtils.sendChatParticipantRequest(
    request,
    chatContext,
    {
        prompt: 'You are a cat! Answer as a cat.',
        responseStreamOptions: {
            stream,
            references: true,
            responseText: true
        },
        tools
    },
    token);
```

> `ChatHandlerOptions` 对象有以下属性：

| 属性 | 说明 |
|---|---|
| `prompt` | （可选）聊天参与者提示词的指令。 |
| `model` | （可选）请求使用的模型。不指定时，使用聊天上下文中的模型。 |
| `tools` | （可选）请求要考虑的工具列表。 |
| `requestJustification` | （可选）一段说明为什么要发出这个请求的字符串。 |
| `responseStreamOptions` | （可选）让 `sendChatParticipantRequest` 把回复流式传回 VS Code。还可以选择启用引用（references）和 / 或回复文本（responseText）。 |

> 3. 返回 LLM 的结果。其中可能包含错误详情或工具调用的元数据。

```ts
return await libResult.result;
```

> 这个[工具调用示例](https://github.com/microsoft/vscode-extension-samples/blob/main/chat-sample/src/chatUtilsSample.ts)的完整源代码可以在 VS Code 扩展示例仓库中找到。

这个库帮你完成了整个工具调用循环：发请求、解析模型的工具调用请求、用 `vscode.lm.invokeTool` 执行工具、把结果交回模型、把最终回复输出到 `stream`。代码中的 `chatUtils` 是导入的库：`import * as chatUtils from '@vscode/chat-extension-utils';`。

<a id="implement-tool-calling-yourself"></a>
### 自己实现工具调用（Implement tool calling yourself）

> 对于更高级的场景，你也可以自己实现工具调用。你可以选择使用 `@vscode/prompt-tsx` 库来构建 LLM 提示词。自己实现工具调用，可以让你更好地控制工具调用的过程。例如，执行额外的校验，或者在把工具的响应发给 LLM 之前，以特定的方式处理它们。
>
> 在 VS Code 扩展示例仓库中查看[使用 prompt-tsx 实现工具调用](https://github.com/microsoft/vscode-extension-samples/blob/main/chat-sample/src/toolParticipant.ts)的完整源代码。

自己实现时，核心的循环大致是这样的（以 `@types/vscode` 1.140 的 API 为准的示意代码）：

```ts
const tools = vscode.lm.tools.filter(t => t.tags.includes('chat-tools-sample'));
const messages = [vscode.LanguageModelChatMessage.User(request.prompt)];

while (true) {
  const response = await request.model.sendRequest(messages, { tools }, token);

  const toolCalls: vscode.LanguageModelToolCallPart[] = [];
  let text = '';
  for await (const part of response.stream) {          // 用 stream 而不是 text，才能拿到工具调用
    if (part instanceof vscode.LanguageModelTextPart) {
      stream.markdown(part.value);
      text += part.value;
    } else if (part instanceof vscode.LanguageModelToolCallPart) {
      toolCalls.push(part);                            // 模型请求调用某个工具
    }
  }

  if (toolCalls.length === 0) {
    break;                                             // 没有工具调用：模型已给出最终回答
  }

  // 把模型的这一轮回复（包括工具调用请求）加入对话
  messages.push(vscode.LanguageModelChatMessage.Assistant([new vscode.LanguageModelTextPart(text), ...toolCalls]));

  // 逐个执行工具，把结果加入对话，然后进入下一轮
  for (const call of toolCalls) {
    const result = await vscode.lm.invokeTool(call.name, {
      input: call.input,
      toolInvocationToken: request.toolInvocationToken   // 让聊天界面显示工具调用和确认框
    }, token);
    messages.push(vscode.LanguageModelChatMessage.User([
      new vscode.LanguageModelToolResultPart(call.callId, result.content)
    ]));
  }
}
```

关键点：发请求时通过 `options.tools` 告诉模型有哪些工具；读取 `response.stream`（而不是 `response.text`），才能拿到 `LanguageModelToolCallPart`；工具结果要用 `LanguageModelToolResultPart` 并带上对应的 `callId`，模型才知道是哪次调用的结果。

---

<a id="measuring-success"></a>
## 衡量成效（Measuring success）

> 我们建议你添加遥测日志，记录 `Unhelpful`（没有帮助）的用户反馈事件，以及你的参与者处理的请求总数，以此衡量参与者的成效。然后可以把参与者最初的成功指标定义为：`unhelpful_feedback_count / total_requests`（“没有帮助”的反馈数 / 请求总数）。

```typescript
const logger = vscode.env.createTelemetryLogger({
     // 遥测日志的实现写在这里
});

cat.onDidReceiveFeedback((feedback: vscode.ChatResultFeedback) => {
    // 记录聊天结果的反馈，以便计算参与者的成功指标
    logger.logUsage('chatResultFeedback', {
        kind: feedback.kind
    });
});
```

> 用户与你的聊天回复之间的任何其他交互，都应该被视为正面的指标（例如，用户选择了聊天回复中生成的某个按钮）。在使用 AI 时，用遥测来衡量成效至关重要，因为它是一种不确定的技术。进行实验、衡量，并不断迭代改进你的参与者，以确保良好的用户体验。

用户可以在每条回复下面点“有帮助”（👍）或“没有帮助”（👎），`onDidReceiveFeedback` 会收到这个事件，`feedback.kind` 是 `ChatResultFeedbackKind.Helpful` 或 `Unhelpful`。`createTelemetryLogger` 的用法和遥测的规范见 [遥测](../telemetry.md)，记得遵守用户的遥测设置。

---

<a id="guidelines-and-conventions"></a>
## 准则与约定（Guidelines and conventions）

<a id="guidelines"></a>
### 准则（Guidelines）

> 聊天参与者不应该只是一个单纯的问答机器人。在构建聊天参与者时，要发挥创意，使用现有的 VS Code API，在 VS Code 中创建丰富的集成。用户也喜欢丰富、便捷的交互，比如回复中的按钮，或者能把用户带到聊天中你的参与者那里的菜单项。思考一下 AI 能在哪些真实的场景中帮助你的用户。
>
> 并不是每个扩展都适合贡献一个聊天参与者。聊天中有太多的参与者，可能会导致糟糕的用户体验。当你想控制完整的提示词（包括给语言模型的指令）时，聊天参与者是最合适的。你可以复用精心编写的 Copilot 系统消息，也可以向其他参与者贡献上下文。
>
> 例如，语言扩展（比如 C++ 扩展）可以通过其他各种方式做出贡献：
>
> - 贡献能把语言服务的智能带入用户查询的工具。例如，C++ 扩展可以把 `#cpp` 工具解析为工作区的 C++ 状态。这能给 Copilot 语言模型提供正确的 C++ 上下文，提高 Copilot 对 C++ 问题回答的质量。
> - 贡献使用语言模型的智能操作，可以选择与传统的语言服务知识结合使用，来提供出色的用户体验。例如，C++ 可能已经提供了一个“提取为方法”的智能操作，它使用语言模型为新方法生成一个合适的默认名称。
>
> 聊天扩展在即将执行代价高昂的操作，或者即将编辑或删除无法撤销的内容时，应该明确地征求用户的同意。为了获得良好的用户体验，我们不鼓励扩展贡献多个聊天参与者。每个扩展最多一个聊天参与者，是一种简单且在界面上可以很好扩展的模式。

**要点：**

| 建议 | 原因 |
|---|---|
| 不要只做问答，要结合 VS Code API 做丰富的交互（按钮、菜单、编辑文件……） | 单纯的问答用通用的 AI 就能做到，体现不出扩展的价值 |
| 不是每个扩展都需要聊天参与者 | 参与者太多，用户记不住、选不过来 |
| 更多时候，提供工具比提供参与者更合适 | 工具能被所有对话（包括智能体模式）使用，参与者只在被 `@` 时才起作用 |
| 危险操作前征求同意 | AI 可能误解用户的意思 |
| 一个扩展最多一个参与者 | 不同功能用斜杠命令区分即可 |

<a id="chat-participant-naming-conventions"></a>
### 聊天参与者命名约定（Chat participant naming conventions）

| 属性 | 说明 | 命名准则 |
|----------|-------------|-------------------|
| `id` | 聊天参与者的全局唯一标识符 | 字符串；以扩展名作为前缀，后面跟一个在你的扩展中唯一的 ID；示例：`chat-sample.cat`、`code-visualizer.code-visualizer-participant` |
| `name` | 聊天参与者的名称，用户通过 `@` 符号引用它 | 由字母数字、下划线和连字符组成的字符串；建议只使用小写，以与现有的聊天参与者保持一致；通过引用你的公司名称或它的功能，让参与者的用途从名称上一目了然；有些参与者名称是保留的，如果使用了保留名称，会显示包括扩展 ID 在内的完全限定名称；示例：`vscode`、`terminal`、`code-visualizer` |
| `fullName` | （可选）参与者的全名，显示为来自这个参与者的回复的标签 | 字符串；建议使用[标题式大写](https://en.wikipedia.org/wiki/Title_case)；使用你的公司名称、品牌名称或用户友好的名称；示例：`GitHub Copilot`、`VS Code`、`Math Tutor` |
| `description` | （可选）对聊天参与者功能的简短描述，显示为聊天输入框中的占位文字，或者显示在参与者列表中 | 字符串；建议使用句子式大写（只有首字母大写），末尾不加标点；描述要简短，避免出现横向滚动；示例：`Ask questions about VS Code`、`Generate UML diagrams for your code` |

> 在任何面向用户的元素中（比如属性、聊天回复或聊天用户界面）提到你的聊天参与者时，建议不要使用“参与者”（participant）这个词，因为这是 API 的名称。例如，`@cat` 扩展可以称为 “Cat extension for GitHub Copilot”（GitHub Copilot 的 Cat 扩展）。

<a id="slash-command-naming-conventions"></a>
### 斜杠命令命名约定（Slash command naming conventions）

| 属性 | 说明 | 命名准则 |
|----------|-------------|-------------------|
| `name` | 斜杠命令的名称，用户通过 `/` 符号引用它 | 字符串；建议使用[小驼峰命名](https://en.wikipedia.org/wiki/Camel_case)，以与现有的斜杠命令保持一致；让命令的用途从名称上一目了然；示例：`fix`、`explain`、`runCommand` |
| `description` | （可选）对斜杠命令功能的简短描述，显示为聊天输入框中的占位文字，或者显示在参与者和命令的列表中 | 字符串；建议使用句子式大写，末尾不加标点；描述要简短，避免出现横向滚动；示例：`Search for and execute a command in VS Code`、`Generate unit tests for the selected code` |

---

<a id="publishing-your-extension"></a>
## 发布你的扩展（Publishing your extension）

> 创建好 AI 扩展之后，就可以把它发布到 Visual Studio 扩展市场：
>
> - 在发布到 VS 扩展市场之前，我们建议你阅读 [Microsoft AI 工具和实践准则](https://www.microsoft.com/en-us/ai/tools-practices)。这些准则提供了负责任地开发和使用 AI 技术的最佳实践。
> - 发布到 VS 扩展市场，意味着你的扩展遵守 [GitHub Copilot 扩展性可接受的开发和使用政策](https://docs.github.com/en/early-access/copilot/github-copilot-extensibility-platform-partnership-plugin-acceptable-development-and-use-policy)。
> - 按照[发布扩展](../../working-with-extensions/publishing-extension.md)中的说明上传到扩展市场。
> - 如果你的扩展除了聊天之外还贡献了其他功能，我们建议你不要在[扩展清单](../../references/extension-manifest.md)中引入对 GitHub Copilot 的扩展依赖。这样可以确保不使用 GitHub Copilot 的扩展用户，无需安装 GitHub Copilot 也能使用非聊天的功能。

---

<a id="extending-github-copilot-via-github-apps"></a>
## 通过 GitHub Apps 扩展 GitHub Copilot（Extending GitHub Copilot via GitHub Apps）

> 另外，也可以通过创建一个 GitHub App 来扩展 GitHub Copilot，在聊天视图中贡献一个聊天参与者。GitHub App 由一个服务支撑，可以在所有 GitHub Copilot 的使用场景中工作，比如 github.com、Visual Studio 或 VS Code。另一方面，GitHub Apps 无法完全访问 VS Code API。要了解更多关于通过 GitHub App 扩展 GitHub Copilot 的信息，请参阅 [GitHub 文档](https://docs.github.com/en/copilot/building-copilot-extensions/about-building-copilot-extensions)。

| | VS Code 扩展中的聊天参与者 | GitHub App |
|---|---|---|
| 在哪里可用 | 只在 VS Code 中 | github.com、Visual Studio、VS Code 等所有 Copilot 场景 |
| 运行在哪里 | 用户本地的扩展宿主 | 你自己的服务器 |
| VS Code API | 完全可用 | 不能完全访问 |

---

<a id="using-the-language-model"></a>
## 使用语言模型（Using the language model）

> 聊天参与者可以以各种方式使用语言模型。有些参与者只用语言模型来获取对自定义提示词的回答，比如[示例聊天参与者](https://github.com/microsoft/vscode-extension-samples/tree/main/chat-sample)。另一些参与者更高级，它们像自主的智能体一样，借助语言模型调用多个工具。这类高级参与者的一个例子是内置的 `@workspace`，它了解你的工作区，可以回答关于工作区的问题。在内部，`@workspace` 由多个工具驱动：GitHub 的知识图谱，结合语义搜索、本地代码索引以及 VS Code 的语言服务。

---

<a id="related-content"></a>
## 相关内容（Related content）

> - [聊天参与者 API 参考](https://code.visualstudio.com/api/references/vscode-api#chat)
> - [在扩展中使用语言模型 API](./language-model.md)
> - [贡献一个语言模型工具](./tools.md)

动手实践可以继续阅读 [教程：创建一个代码导师聊天参与者](./chat-tutorial.md)。

---

## 本篇小结

```text
package.json：contributes.chatParticipants
  id（扩展名.xxx）、name（@名称，小写）、fullName、description（输入框占位文字）、isSticky
  commands：[{ name, description }]（斜杠命令，小驼峰）
  disambiguation：[{ category, description, examples }]（参与者检测）

代码：vscode.chat.createChatParticipant(id, handler)，设置 iconPath、followupProvider
  handler(request, context, stream, token)
    request.prompt / command / references / model（优先用用户选择的模型）
    context.history：ChatRequestTurn / ChatResponseTurn（不会自动加入提示词）
    stream：markdown / button / filetree / progress / reference / anchor
    返回 { metadata }，供 followupProvider 使用

命令链接：MarkdownString + isTrusted = { enabledCommands: [...] }（不要设为 true）
工具调用：@vscode/chat-extension-utils 的 sendChatParticipantRequest，
         或自己实现循环（options.tools → stream 中的 ToolCallPart → lm.invokeTool → ToolResultPart）
衡量：onDidReceiveFeedback，统计“没有帮助”的比例
准则：不只是问答；一个扩展最多一个参与者；很多时候提供工具更合适
```
