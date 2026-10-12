# 教程：使用聊天 API 构建一个代码教学聊天参与者（Tutorial: Build a code tutorial chat participant with the Chat API）

> 原文：[Tutorial: Build a code tutorial chat participant with the Chat API](https://code.visualstudio.com/api/extension-guides/ai/chat-tutorial)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/ai/chat-tutorial.md`（DateApproved: 10/7/2026）

> 在本教程中，你将学习如何创建一个与 GitHub Copilot 聊天体验集成的 VS Code 扩展。你会使用聊天扩展 API 贡献一个聊天参与者。你的参与者将是一位代码导师，可以为编程概念提供讲解和练习示例。

这是 [聊天参与者 API](./chat.md) 的配套教程，一步一步地实现一个 `@tutor` 参与者。完成后的效果：在聊天中输入 `@tutor 讲讲栈`，它会以引导的方式讲解；输入 `@tutor /exercise 递归`，它会出练习题。

---

<a id="prerequisites"></a>
## 准备工作（Prerequisites）

> 你需要以下工具和账号来完成本教程：
>
> - [Visual Studio Code](https://code.visualstudio.com/download)
> - [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat)
> - [Node.js](https://nodejs.org/en/download/)

---

<a id="step-1-set-up-your-project"></a>
## 第 1 步：设置项目（Step 1: Set up your project）

> 首先，使用 Yeoman 和 VS Code 扩展生成器生成扩展项目。

```bash
npx --package yo --package generator-code -- yo code
```

> 选择以下选项完成设置：

```bash
# ? What type of extension do you want to create? New Extension (TypeScript)
# ? What's the name of your extension? Code Tutor

### 下面的选项直接按回车使用默认值 ###

# ? What's the identifier of your extension? code-tutor
# ? What's the description of your extension? 留空
# ? Initialize a git repository? Yes
# ? Bundle the source code with webpack? No
# ? Which package manager to use? npm

# ? Do you want to open the new folder with Visual Studio Code? Open with `code`
```

> 扩展项目生成后，你要处理的是两个文件：`extension.ts` 和 `package.json`，可以在[扩展的结构文档](../../get-started/extension-anatomy.md#extension-file-structure)中了解更多关于它们的信息。简单概括一下：
>
> - `extension.ts` 是扩展的主入口，包含聊天参与者的逻辑。
> - `package.json` 包含扩展的元数据，比如参与者的名称和描述。
>
> 删除 `extension.ts` 的 `activate()` 方法中自动生成的代码。这里就是我们要放置聊天参与者逻辑的地方。

---

<a id="step-2-register-a-chat-participant"></a>
## 第 2 步：注册聊天参与者（Step 2: Register a Chat participant）

> 在 `package.json` 文件中，把自动生成的 `contributes` 部分替换为以下内容：

```json
"contributes":{
    "chatParticipants": [
    {
        "id": "chat-tutorial.code-tutor",
        "fullName": "Code Tutor",
        "name": "tutor",
        "description": "What can I teach you?",
        "isSticky": true
    }
    ]
}
```

> 这段代码注册了一个具有以下属性的聊天参与者：
>
> - 唯一 ID `chat-tutorial.code-tutor`，在代码中会引用它
> - 全名 `Code Tutor`，会显示在参与者回复的标题区域
> - 名称 `tutor`，在聊天视图中用 `@tutor` 引用这个聊天参与者
> - 描述 “What can I teach you?”（我能教你什么？），会作为占位文字显示在聊天输入框中
>
> 最后，设置 `isSticky: true`，会在用户开始与参与者交互之后，自动在聊天输入框中加上参与者的名称。

各属性的作用在 [聊天参与者 API](./chat.md#1-register-the-chat-participant) 中有详细介绍。注意：替换 `contributes` 后，脚手架生成的 Hello World 命令也被删掉了，所以要同时删除 `extension.ts` 中注册那个命令的代码（上一步已经要求删除 `activate` 中的代码）。

---

<a id="step-3-craft-the-prompt"></a>
## 第 3 步：编写提示词（Step 3: Craft the prompt）

> 参与者注册好之后，就可以开始实现代码导师的逻辑了。在 `extension.ts` 文件中，你要为请求定义一个提示词。
>
> 编写一个好的提示词，是让参与者给出最佳回复的关键。可以查看[这篇文章](https://platform.openai.com/docs/guides/prompt-engineering)，了解提示词工程的技巧。
>
> 你的代码导师应该模仿现实中的导师，引导学生理解概念，而不是直接给出答案。此外，导师应该保持专注于主题，不回答与编程无关的问题。
>
> 看看下面这两个提示词。哪一个更有可能产生规定的行为？
>
> 1. > You are a helpful code tutor. Your job is to teach the user with simple descriptions and sample code of the concept.
> 2. > You are a helpful code tutor. Your job is to teach the user with simple descriptions and sample code of the concept. Respond with a guided overview of the concept in a series of messages. Do not give the user the answer directly, but guide them to find the answer themselves. If the user asks a non-programming question, politely decline to respond.

两个提示词的意思：

| | 内容 | 问题 |
|---|---|---|
| 提示词 1 | 你是一位乐于助人的代码导师。你的工作是用简单的描述和示例代码教会用户相关的概念。 | 只说了“做什么”，没说“怎么做”“不做什么” |
| 提示词 2 | 在提示词 1 的基础上，加上：以引导式概述的方式、分多条消息讲解概念；**不要直接告诉用户答案，而是引导他们自己找到答案**；如果用户问的是与编程无关的问题，礼貌地拒绝回答。 | 明确规定了教学方式和边界 |

> 第二个提示词更具体，为参与者如何回复给出了明确的方向。把这个提示词添加到 `extension.ts` 文件中。

```ts
const BASE_PROMPT = 'You are a helpful code tutor. Your job is to teach the user with simple descriptions and sample code of the concept. Respond with a guided overview of the concept in a series of messages. Do not give the user the answer directly, but guide them to find the answer themselves. If the user asks a non-programming question, politely decline to respond.';
```

这和 [语言模型 API 教程](./language-model-tutorial.md) 中总结的提示词技巧是一致的：**设定角色、说明任务、规定方式、划定边界**。如果希望导师用中文讲解，在提示词末尾加上 “Always respond in Chinese.” 即可。

---

<a id="step-4-implement-the-request-handler"></a>
## 第 4 步：实现请求处理函数（Step 4: Implement the request handler）

> 提示词选好之后，就要实现请求处理函数了。它负责处理用户的聊天请求。你要定义请求处理函数，执行处理请求的逻辑，并向用户返回回复。
>
> 首先，定义处理函数：

```ts
// 定义一个聊天处理函数
const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) => {

    return;
}
```

> 在这个处理函数的函数体中，初始化提示词，以及一个包含这个提示词的 `messages` 数组。然后，把用户在聊天框中输入的内容发送过去。可以通过 `request.prompt` 访问它。
>
> 使用 `request.model.sendRequest` 发送请求，它会用当前选中的模型发送请求。最后，把回复以流的方式传给用户。

```ts
// 定义一个聊天处理函数
const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) => {

    // 初始化提示词
    let prompt = BASE_PROMPT;

    // 用提示词初始化消息数组
    const messages = [
        vscode.LanguageModelChatMessage.User(prompt),
    ];

    // 加入用户的消息
    messages.push(vscode.LanguageModelChatMessage.User(request.prompt));

    // 发送请求
    const chatResponse = await request.model.sendRequest(messages, {}, token);

    // 以流的方式输出回复
    for await (const fragment of chatResponse.text) {
        stream.markdown(fragment);
    }

    return;
};
```

这就是 [语言模型 API](./language-model.md) 的三步（构建提示词 → 发送 → 流式读取），区别只有两点：模型直接用 `request.model`（用户在聊天中选择的模型），不用 `selectChatModels`；回复通过 `stream.markdown` 输出到聊天中，而不是写到编辑器里。

`messages` 中的第一条是指令，第二条是用户的问题，两条都是 User 消息（语言模型 API 不支持 System 消息，见 [语言模型 API](./language-model.md#build-the-language-model-prompt)）。

---

<a id="step-5-create-the-chat-participant"></a>
## 第 5 步：创建聊天参与者（Step 5: Create the chat participant）

> 处理函数实现好之后，最后一步是使用聊天扩展 API 中的 `createChatParticipant` 方法创建聊天参与者。确保使用与 `package.json` 中相同的 ID。
>
> 你还应该为参与者添加一个图标，进一步定制它。与参与者交互时，图标会显示在聊天视图中。

```ts
// 定义一个聊天处理函数
const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) => {

    // 初始化提示词
    let prompt = BASE_PROMPT;

    // 用提示词初始化消息数组
    const messages = [
        vscode.LanguageModelChatMessage.User(prompt),
    ];

    // 加入用户的消息
    messages.push(vscode.LanguageModelChatMessage.User(request.prompt));

    // 发送请求
    const chatResponse = await request.model.sendRequest(messages, {}, token);

    // 以流的方式输出回复
    for await (const fragment of chatResponse.text) {
        stream.markdown(fragment);
    }

    return;
};

// 创建参与者
const tutor = vscode.chat.createChatParticipant("chat-tutorial.code-tutor", handler);

// 为参与者添加图标
tutor.iconPath = vscode.Uri.joinPath(context.extensionUri, 'tutor.jpeg');
```

这段代码要放在 `activate(context)` 函数里面（`context.extensionUri` 来自 `activate` 的参数）。`tutor.jpeg` 是放在扩展根目录下的一张图片，需要自己准备。也可以写一行 `context.subscriptions.push(tutor);`，让扩展停用时自动释放参与者。

**注意变量名冲突：** `activate` 的参数叫 `context`（`ExtensionContext`），处理函数的第二个参数也叫 `context`（`ChatContext`）。在处理函数内部，`context` 指的是 `ChatContext`。为了避免混淆，可以把处理函数的参数改名为 `chatContext`。

---

<a id="step-6-run-the-code"></a>
## 第 6 步：运行代码（Step 6: Run the code）

> 现在可以试用你的聊天参与者了！按 `F5` 运行代码。会打开一个带有你的聊天参与者的新 VS Code 窗口。
>
> 在 Copilot 聊天面板中，现在可以输入 `@tutor` 来调用你的参与者了！

![聊天面板中的参与者](../images/ai/chat-tutorial/participant.png)

> 输入你想学习的内容来测试它。你应该会看到一个对这个概念进行概述的回复！
>
> 如果你输入一条相关的消息继续对话，会发现参与者并没有根据你们的对话给出后续的回复。这是因为我们当前的参与者只发送了用户当前的消息，而没有发送参与者的消息历史。
>
> 在下面的截图中，导师正确地回复了对栈的入门讲解。但是，在后续的对话中，它没有理解用户是在继续这个对话、想看栈的 Python 实现，于是给出了一个关于 Python 的笼统回复。

![没有消息历史的参与者](../images/ai/chat-tutorial/participant-no-message-history.png)

这就是 [语言模型 API](./language-model.md) 中说的：**模型本身没有记忆，每次请求都是独立的**。用户问“那用 Python 怎么写？”时，模型根本不知道“那”指的是栈。

---

<a id="step-7-add-message-history-for-more-context"></a>
## 第 7 步：添加消息历史，提供更多上下文（Step 7: Add message history for more context）

> Copilot 聊天最大的价值之一，是能够通过多轮消息反复迭代，得到最好的回复。为此，你要把参与者的消息历史发送到聊天请求中。可以通过 `context.history` 访问它。
>
> 你需要获取这些历史，并把它们添加到 `messages` 数组中。这需要在添加 `request.prompt` 之前完成。

```ts
// 定义一个聊天处理函数
const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) => {

    // 初始化提示词
    let prompt = BASE_PROMPT;

    // 用提示词初始化消息数组
    const messages = [
        vscode.LanguageModelChatMessage.User(prompt),
    ];

    // 获取参与者之前所有的消息
    const previousMessages = context.history.filter(
        (h) => h instanceof vscode.ChatResponseTurn
    );

    // 把之前的消息添加到消息数组中
    previousMessages.forEach((m) => {
        let fullMessage = '';
        m.response.forEach((r) => {
            const mdPart = r as vscode.ChatResponseMarkdownPart;
            fullMessage += mdPart.value.value;
        });
        messages.push(vscode.LanguageModelChatMessage.Assistant(fullMessage));
    });

    // 加入用户的消息
    messages.push(vscode.LanguageModelChatMessage.User(request.prompt));

    // 发送请求
    const chatResponse = await request.model.sendRequest(messages, {}, token);

    // 以流的方式输出回复
    for await (const fragment of chatResponse.text) {
        stream.markdown(fragment);
    }

    return;
};
```

> 现在运行代码，你就可以带着之前所有消息的上下文与参与者对话了！在下面的截图中，参与者正确地理解了用户是在请求查看栈的 Python 实现。

![带有消息历史的参与者](../images/ai/chat-tutorial/participant-message-history.png)

**这段代码在做什么：**

```text
context.history（之前的对话）
  ├─ ChatRequestTurn：用户问的“讲讲栈”
  └─ ChatResponseTurn：导师回复的一段讲解（由多个部分组成）
        ↓ filter 只保留 ChatResponseTurn
        ↓ 把每次回复中的各个部分的文字拼起来
        ↓ 作为 Assistant 消息加入 messages
```

`ChatResponseTurn.response` 是一个数组，包含回复中的各个部分（Markdown、按钮、文件树等）。`ChatResponseMarkdownPart.value` 是一个 `MarkdownString`，所以要再取一次 `.value` 才是字符串。

**原文代码中值得改进的两处：**

1. **只加入了导师的回复，没有加入用户之前的提问。** 模型看到的对话是“指令 → 导师的回复 → 导师的回复 → ……→ 用户当前的问题”，缺少了每轮用户问了什么。更完整的做法是按顺序同时加入两种历史。
2. **`r as vscode.ChatResponseMarkdownPart` 是强制类型转换。** 如果回复中有按钮之类的非 Markdown 部分，`mdPart.value` 就是 `undefined`，访问 `.value` 会直接报错。应该先用 `instanceof` 判断。

改进后的写法：

```ts
for (const turn of chatContext.history) {
  if (turn instanceof vscode.ChatRequestTurn) {
    // 用户之前的提问
    messages.push(vscode.LanguageModelChatMessage.User(turn.prompt));
  } else if (turn instanceof vscode.ChatResponseTurn) {
    // 导师之前的回复：只取 Markdown 部分的文字
    let fullMessage = '';
    for (const part of turn.response) {
      if (part instanceof vscode.ChatResponseMarkdownPart) {
        fullMessage += part.value.value;
      }
    }
    messages.push(vscode.LanguageModelChatMessage.Assistant(fullMessage));
  }
}
```

对话很长时，历史也会越来越长，可能超出模型的上下文窗口。可以只保留最近的几轮，或者用 [Prompt TSX](./prompt-tsx.md) 按优先级自动裁剪。

---

<a id="step-8-add-a-command"></a>
## 第 8 步：添加命令（Step 8: Add a command）

> 基本的参与者已经实现好了，现在可以通过添加命令来扩展它。命令是表示常见用户意图的简写方式，用 `/` 符号表示。然后，扩展可以根据命令，相应地向语言模型发出提示。
>
> 如果能添加一个让导师为某个概念出练习题的命令就太好了。你需要在 `package.json` 文件中注册这个命令，并在 `extension.ts` 中实现它的逻辑。可以把命令命名为 `exercise`，这样就可以通过输入 `/exercise` 来调用它。
>
> 在 `package.json` 中，为 `chatParticipants` 属性添加 `commands` 属性。在这里指定命令的名称和简短的描述：

```json
"contributes": {
    "chatParticipants": [
      {
        "id": "chat-tutorial.code-tutor",
        "fullName": "Code Tutor",
        "name": "tutor",
        "description": "What can I teach you?",
        "isSticky": true,
        "commands": [
          {
            "name": "exercise",
            "description": "Provide exercises to practice a concept."
          }
        ]
      }
    ]
  },
```

（命令描述的意思是：“提供练习题，练习某个概念。”）

> 要实现从导师那里获取练习题的逻辑，最简单的方式是修改发送给请求的提示词。创建一个新的提示词 `EXERCISES_PROMPT`，要求参与者返回练习题。下面是一个示例：

```ts
const EXERCISES_PROMPT = 'You are a helpful tutor. Your job is to teach the user with fun, simple exercises that they can complete in the editor. Your exercises should start simple and get more complex as the user progresses. Move one concept at a time, and do not move on to the next concept until the user provides the correct answer. Give hints in your exercises to help the user learn. If the user is stuck, you can provide the answer and explain why it is the answer. If the user asks a non-programming question, politely decline to respond.';
```

提示词的意思：

> 你是一位乐于助人的导师。你的工作是用有趣、简单、用户可以在编辑器中完成的练习来教用户。练习应该从简单开始，随着用户的进步变得越来越复杂。一次只讲一个概念，在用户给出正确答案之前，不要进入下一个概念。在练习中给出提示，帮助用户学习。如果用户卡住了，你可以给出答案，并解释为什么这是答案。如果用户问的是与编程无关的问题，礼貌地拒绝回答。

> 然后，在请求处理函数中，你需要添加检测用户是否引用了这个命令的逻辑。可以通过 `request.command` 属性做到这一点。
>
> 如果引用了这个命令，就把提示词更新为新创建的 `EXERCISES_PROMPT`。

```ts
// 定义一个聊天处理函数
const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) => {

    // 初始化提示词
    let prompt = BASE_PROMPT;

    if (request.command === 'exercise') {
        prompt = EXERCISES_PROMPT;
    }

    // 用提示词初始化消息数组
    const messages = [
        vscode.LanguageModelChatMessage.User(prompt),
    ];

    // 获取参与者之前所有的消息
    const previousMessages = context.history.filter(
        (h) => h instanceof vscode.ChatResponseTurn
    );

    // 把之前的消息添加到消息数组中
    previousMessages.forEach((m) => {
        let fullMessage = '';
        m.response.forEach((r) => {
            const mdPart = r as vscode.ChatResponseMarkdownPart;
            fullMessage += mdPart.value.value;
        });
        messages.push(vscode.LanguageModelChatMessage.Assistant(fullMessage));
    });

    // 加入用户的消息
    messages.push(vscode.LanguageModelChatMessage.User(request.prompt));

    // 发送请求
    const chatResponse = await request.model.sendRequest(messages, {}, token);

    // 以流的方式输出回复
    for await (const fragment of chatResponse.text) {
        stream.markdown(fragment);
    }

    return;
};
```

> 这样就全部完成了！获取消息历史、发送请求、以流的方式输出回复，其余的逻辑都保持不变。
>
> 现在你可以输入 `/exercise`，它会调出你的聊天参与者，你可以获得交互式的练习来练习编程！

![带有斜杠命令的参与者](../images/ai/chat-tutorial/exercise-command.png)

用户输入 `@tutor /exercise 递归` 时，`request.command` 是 `'exercise'`，`request.prompt` 是 `'递归'`。**同一个参与者，不同的命令对应不同的提示词**，这就是斜杠命令最常见的用法。

---

<a id="next-steps"></a>
## 下一步（Next steps）

> 恭喜！你已经成功创建了一个能为编程概念提供讲解和练习示例的聊天参与者。你可以通过微调提示词、添加更多的斜杠命令，或者利用[语言模型 API](./language-model.md) 等其他 API，进一步扩展你的参与者。准备好之后，你还可以把扩展发布到 [Visual Studio Code 扩展市场](https://marketplace.visualstudio.com/vscode)。
>
> 你可以在 [vscode-extensions-sample 仓库](https://github.com/microsoft/vscode-extension-samples/tree/main/chat-tutorial)中找到本教程的完整源代码。

可以继续尝试的改进方向（都在 [聊天参与者 API](./chat.md) 中介绍过）：

| 改进 | 用到的 API |
|---|---|
| 回复后给出“再出一道题”“讲下一个概念”的建议 | `followupProvider` |
| 在回复中加一个“在编辑器中打开练习”的按钮 | `stream.button` |
| 把当前打开的文件作为上下文，讲解用户正在看的代码 | `vscode.window.activeTextEditor` + 放进提示词 |
| 自动识别“教我……”类的问题并路由给 `@tutor` | `disambiguation` |

---

<a id="related-content"></a>
## 相关内容（Related content）

> - [聊天 API 扩展指南](./chat.md)
> - [教程：使用语言模型 API 生成 AI 代码注释](./language-model-tutorial.md)
> - [语言模型 API 扩展指南](./language-model.md)

---

## 本篇小结

```text
1. yo code 生成项目
2. package.json：chatParticipants（id、name、fullName、description、isSticky）
3. 提示词：角色 + 任务 + 方式（引导而非直接给答案）+ 边界（拒绝非编程问题）
4. handler：messages = [指令, 用户问题] → request.model.sendRequest → for await → stream.markdown
5. createChatParticipant(id, handler) + iconPath（放在 activate 中）
6. F5 运行，聊天中输入 @tutor
7. 加入 context.history，让模型“记得”之前的对话
   （同时加入 ChatRequestTurn 和 ChatResponseTurn；用 instanceof 判断 Markdown 部分）
8. 斜杠命令：package.json 中 commands + 代码中按 request.command 切换提示词
```
