# 语言模型 API（Language Model API）

> 原文：[Language Model API](https://code.visualstudio.com/api/extension-guides/ai/language-model)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/ai/language-model.md`（DateApproved: 10/7/2026）

> 语言模型 API 让你可以在 VS Code 扩展中[使用语言模型](https://code.visualstudio.com/api/references/vscode-api#lm)，集成 AI 功能和自然语言处理能力。
>
> 你可以在不同类型的扩展中使用语言模型 API。这个 API 的一种典型用途是在[聊天扩展](./chat.md)中，用语言模型来理解用户的请求，并帮助给出回答。不过，语言模型 API 的用途并不局限于这种场景。你可以在[语言](../../language-extensions/overview.md)扩展或[调试器](../debugger-extension.md)扩展中使用语言模型，也可以在自定义扩展的[命令](../command.md)或[任务](../task-provider.md)中使用它。例如，Rust 扩展可能会用语言模型提供默认的名称，改进它的重命名体验。
>
> 使用语言模型 API 的过程包括以下几个步骤：
>
> 1. 构建语言模型提示词（prompt）
> 2. 发送语言模型请求
> 3. 解析响应
>
> 下面几节会详细介绍如何在扩展中实现这些步骤。
>
> 要开始上手，可以看看[聊天扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/chat-sample)。

这是 AI 系列中**最基础的一篇**：后面的工具、聊天参与者，归根结底都要用到这里讲的“如何调用语言模型”。

三个步骤对应的代码骨架：

```ts
// 1. 构建提示词
const messages = [vscode.LanguageModelChatMessage.User('用一句话解释什么是递归')];

// 2. 选择模型并发送请求
const [model] = await vscode.lm.selectChatModels({ vendor: 'copilot' });
const response = await model.sendRequest(messages, {}, token);

// 3. 解析响应（流式读取）
for await (const fragment of response.text) {
  console.log(fragment);
}
```

---

<a id="build-the-language-model-prompt"></a>
## 构建语言模型提示词（Build the language model prompt）

> 要与语言模型交互，扩展首先应该精心构建它的提示词，然后向语言模型发送请求。你可以用提示词向语言模型说明你要用它完成的总体任务。提示词还可以定义理解用户消息时所处的上下文。
>
> 在构建语言模型提示词时，语言模型 API 支持两种类型的消息：
>
> - **User**（用户）：用来提供指令和用户的请求
> - **Assistant**（助手）：用来把语言模型之前的回复历史作为上下文添加到提示词中
>
> **注意**：目前，语言模型 API 不支持使用系统消息（system message）。

**消息的角色：** 和大多数 AI 接口一样，提示词是一个“对话”数组，每条消息有一个角色：

| 角色 | 含义 | 创建方式 |
|---|---|---|
| User | 用户说的话；也用来放给模型的指令 | `LanguageModelChatMessage.User(...)` |
| Assistant | 模型之前说过的话（用来提供对话历史） | `LanguageModelChatMessage.Assistant(...)` |

很多 AI 接口还有一个 System（系统）角色，专门用来放“你是一个……助手，请遵守……规则”这类指令。VS Code 的语言模型 API 不支持它（当前类型定义中 `LanguageModelChatMessageRole` 只有 `User` 和 `Assistant`），所以这类指令也写成 User 消息，放在最前面。

> 你可以用两种方式构建语言模型提示词：
>
> - `LanguageModelChatMessage`：以字符串的形式提供一条或多条消息来创建提示词。如果你刚开始使用语言模型 API，可以采用这种方式。
> - [`@vscode/prompt-tsx`](https://www.npmjs.com/package/@vscode/prompt-tsx)：用 TSX 语法声明提示词。
>
> 如果你想更好地控制语言模型提示词的组成方式，可以使用 `prompt-tsx` 库。例如，这个库可以帮助你根据每个语言模型的上下文窗口大小，动态地调整提示词的长度。了解更多关于 [`@vscode/prompt-tsx`](https://www.npmjs.com/package/@vscode/prompt-tsx) 的信息，或者查看[聊天扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/chat-sample)开始上手。

**上下文窗口**是指模型一次最多能处理多少 token（可以粗略理解为“字数”）。提示词太长（比如塞进了一个很大的文件），就会超出限制而报错。`prompt-tsx` 能按优先级自动裁剪内容，详见 [Prompt TSX](./prompt-tsx.md)。

> 要了解更多关于提示词工程（prompt engineering）的概念，我们建议阅读 OpenAI 出色的[提示词工程指南](https://platform.openai.com/docs/guides/prompt-engineering)。
>
> **提示：** 充分利用丰富的 VS Code 扩展 API，获取最相关的上下文并把它包含在提示词中。例如，包含编辑器中当前活动文件的内容。

这正是在 VS Code 扩展中使用 AI 的最大优势：扩展可以拿到编辑器中的各种信息（当前文件、选中的代码、诊断错误、项目结构……），把它们放进提示词，模型就能给出与用户当前工作紧密相关的回答。

<a id="use-the-languagemodelchatmessage-class"></a>
### 使用 `LanguageModelChatMessage` 类（Use the `LanguageModelChatMessage` class）

> 语言模型 API 提供了 `LanguageModelChatMessage` 类来表示和创建聊天消息。可以分别使用 `LanguageModelChatMessage.User` 或 `LanguageModelChatMessage.Assistant` 方法创建用户消息或助手消息。
>
> 在下面的例子中，第一条消息为提示词提供了上下文：
>
> - 模型在回复中使用的人设（这里是一只猫）
> - 模型生成回复时应该遵守的规则（这里是用猫的比喻，以幽默的方式解释计算机科学概念）
>
> 第二条消息则提供了来自用户的具体请求或指令。在第一条消息提供的上下文下，它决定了要完成的具体任务。

```typescript
const craftedPrompt = [
    vscode.LanguageModelChatMessage.User('You are a cat! Think carefully and step by step like a cat would. Your job is to explain computer science concepts in the funny manner of a cat, using cat metaphors. Always start your response by stating what concept you are explaining. Always include code samples.'),
    vscode.LanguageModelChatMessage.User('I want to understand recursion')
];
```

第一条消息的意思是：“你是一只猫！像猫一样仔细地、一步一步地思考。你的工作是用猫的比喻，以猫那种幽默的方式解释计算机科学概念。回复时总是先说明你在解释什么概念。总是包含代码示例。”第二条消息是用户的问题：“我想理解递归”。

提示词也可以用中文写，模型同样能理解。如果希望模型用中文回答，在指令中写明“请用中文回答”即可。

**加入多轮对话的历史：**

```ts
const messages = [
  vscode.LanguageModelChatMessage.User('你是一个耐心的编程老师。'),
  vscode.LanguageModelChatMessage.User('什么是闭包？'),           // 上一轮用户的问题
  vscode.LanguageModelChatMessage.Assistant('闭包是指……'),         // 上一轮模型的回答
  vscode.LanguageModelChatMessage.User('能举个 JavaScript 的例子吗？') // 这一轮的问题
];
```

模型本身没有“记忆”，每次请求都是独立的。要让它知道之前聊过什么，就要把历史对话一起发过去。

---

<a id="send-the-language-model-request"></a>
## 发送语言模型请求（Send the language model request）

> 构建好语言模型的提示词之后，首先用 [`selectChatModels`](https://code.visualstudio.com/api/references/vscode-api#lm.selectChatModels) 方法选择你想使用的语言模型。这个方法返回一个与指定条件匹配的语言模型数组。如果你实现的是一个聊天参与者，我们建议你改用聊天请求处理函数中 `request` 对象传入的那个模型。这样可以确保你的扩展尊重用户在聊天的模型下拉框中所选择的模型。然后，使用 [`sendRequest`](https://code.visualstudio.com/api/references/vscode-api#LanguageModelChat) 方法向语言模型发送请求。
>
> 选择语言模型时，可以指定以下属性：`vendor`（供应商）、`id`、`family`（系列）或 `version`（版本）。使用这些属性，可以宽泛地匹配某个供应商或系列的所有模型，也可以通过 ID 选择某一个特定的模型。在 [API 参考](https://code.visualstudio.com/api/references/vscode-api#LanguageModelChat)中了解这些属性的更多信息。

| 属性 | 含义 | 示例 |
|---|---|---|
| `vendor` | 模型的提供方 | `'copilot'` |
| `family` | 模型系列 | `'gpt-4o'` |
| `version` | 模型版本 | |
| `id` | 某个模型的唯一 ID | |

条件越少，匹配的模型越多。不传任何条件（`selectChatModels()`）会返回所有可用的模型。

> **注意**：目前，语言模型系列支持 `gpt-4o`、`gpt-4o-mini`、`o1`、`o1-mini`、`claude-3.5-sonnet`。如果你不确定使用哪个模型，我们推荐 `gpt-4o`，因为它的性能和质量都不错。对于直接在编辑器中的交互，我们推荐 `gpt-4o-mini`，因为它的速度快。

（这份模型列表是原文较早时写的，可用的模型会随时间变化，现在很可能已经有更新的模型。实际可用的模型以 `selectChatModels()` 的返回结果为准，不要在代码中写死某个模型名，见下文[模型的可用性](#model-availability)。）

> 如果没有与指定条件匹配的模型，`selectChatModels` 方法会返回一个空数组。你的扩展必须妥善处理这种情况。
>
> 下面的例子展示了如何选择所有的 `Copilot` 模型，无论系列或版本：

```typescript
const models = await vscode.lm.selectChatModels({
  vendor: 'copilot'
});

// 没有可用的模型
if (models.length === 0) {
  // TODO: 处理没有可用模型的情况
}
```

什么时候会没有可用的模型？比如用户没有安装或登录 GitHub Copilot，或者用户所在的组织禁用了某些模型。这时应该给出友好的提示，而不是直接报错。

> **重要**：在扩展可以使用 Copilot 的语言模型之前，需要征得用户的同意。同意是通过一个身份验证对话框来实现的。因此，`selectChatModels` 应该作为用户发起的操作（例如一个命令）的一部分来调用。

也就是说，**不要在 `activate` 中一启动就调用 `selectChatModels` 并发送请求**。第一次使用时，VS Code 会弹出对话框，询问用户“是否允许这个扩展使用语言模型”。如果在扩展激活时就弹出，用户会莫名其妙。应该在用户主动执行某个 AI 功能时再调用。

> 选择好模型之后，可以在模型实例上调用 [`sendRequest`](https://code.visualstudio.com/api/references/vscode-api#LanguageModelChat) 方法，向语言模型发送请求。你需要传入之前构建的[提示词](#build-the-language-model-prompt)，以及其他选项和一个取消令牌。
>
> 向语言模型 API 发出请求时，请求可能会失败。例如，因为模型不存在，或者用户没有同意使用语言模型 API，或者超出了配额限制。使用 `LanguageModelError` 来区分不同类型的错误。
>
> 下面的代码片段展示了如何发出语言模型请求：

```typescript
try {
    const [model] = await vscode.lm.selectChatModels({ vendor: 'copilot', family: 'gpt-4o' });
    const request = model.sendRequest(craftedPrompt, {}, token);
} catch (err) {
    // 发出聊天请求可能会失败，因为
    // - 模型不存在
    // - 用户没有同意
    // - 超出了配额限制
    if (err instanceof vscode.LanguageModelError) {
        console.log(err.message, err.code, err.cause);
        if (err.cause instanceof Error && err.cause.message.includes('off_topic')) {
            stream.markdown(vscode.l10n.t('I\'m sorry, I can only explain computer science concepts.'));
        }
    } else {
        // 添加其他的错误处理逻辑
        throw err;
    }
}
```

几点说明：

- `sendRequest(消息数组, 选项, 取消令牌)`。选项中可以传 `justification`（一段说明，在征求用户同意时显示，告诉用户扩展为什么要使用模型）。
- 示例中 `model.sendRequest(...)` 没有加 `await`，这样 `try/catch` 是捕获不到异步错误的。实际代码中应该写成 `const response = await model.sendRequest(...)`。另外 `selectChatModels` 返回空数组时，`model` 会是 `undefined`，要先判断。
- `stream` 是聊天参与者中用来输出回复的对象（见 [聊天参与者](./chat.md)），这段代码是从聊天参与者的场景中截取的。
- `'off_topic'` 表示请求被判定为“偏离主题”而被拒绝。
- `vscode.l10n.t(...)` 是本地化函数，用来让文字支持多语言。

`LanguageModelError` 的常见错误码（`err.code`）：

| 错误码 | 含义 |
|---|---|
| `NoPermissions` | 用户没有授权扩展使用语言模型 |
| `Blocked` | 请求被阻止（比如超出配额、触发了限制） |
| `NotFound` | 请求的模型不存在 |

---

<a id="interpret-the-response"></a>
## 解析响应（Interpret the response）

> 发送请求之后，你需要处理来自语言模型 API 的响应。根据你的使用场景，你可以把响应直接传给用户，也可以解析响应并执行额外的逻辑。
>
> 语言模型 API 的响应（[`LanguageModelChatResponse`](https://code.visualstudio.com/api/references/vscode-api#LanguageModelChatResponse)）是基于流式传输的，这让你能提供流畅的用户体验。例如，在与[聊天 API](./chat.md) 结合使用时，可以持续地报告结果和进度。

**流式（streaming）响应**：模型生成回复是一个字一个字往外“吐”的。流式响应让你可以边生成边显示，用户不用等待整段回复全部生成完。这就是聊天界面中文字逐渐出现的效果。

`LanguageModelChatResponse` 有两种读取方式（以 `@types/vscode` 1.140 为准）：

| 属性 | 内容 | 适合 |
|---|---|---|
| `text` | 只包含文本片段（`AsyncIterable<string>`） | 只需要文字回复时 |
| `stream` | 包含文本片段、工具调用请求等各种部分 | 使用了工具调用时（见 [语言模型工具](./tools.md)） |

两者都是**异步可迭代对象**，用 `for await (const x of ...)` 逐个读取。

不需要流式效果时，也可以把所有片段拼起来再用：

```ts
let result = '';
for await (const fragment of response.text) {
  result += fragment;
}
// result 就是完整的回复
```

> 处理流式响应时也可能出错，比如网络连接问题。请确保在代码中添加适当的错误处理，来应对这些错误。
>
> 下面的代码片段展示了扩展如何注册一个命令，这个命令使用语言模型，把活动编辑器中的所有变量名改成有趣的猫名字。注意，扩展会把代码以流式的方式写回编辑器，以提供流畅的用户体验。

```typescript
 vscode.commands.registerTextEditorCommand('cat.namesInEditor', async (textEditor: vscode.TextEditor) => {
    // 把活动编辑器中的所有变量替换成猫的名字和词语

    const [model] = await vscode.lm.selectChatModels({ vendor: 'copilot', family: 'gpt-4o' });
    let chatResponse: vscode.LanguageModelChatResponse | undefined;

    const text = textEditor.document.getText();

    const messages = [
        vscode.LanguageModelChatMessage.User(`You are a cat! Think carefully and step by step like a cat would.
        Your job is to replace all variable names in the following code with funny cat variable names. Be creative. IMPORTANT respond just with code. Do not use markdown!`),
        vscode.LanguageModelChatMessage.User(text)
    ];

    try {
        chatResponse = await model.sendRequest(messages, {}, new vscode.CancellationTokenSource().token);
    } catch (err) {
        if (err instanceof vscode.LanguageModelError) {
            console.log(err.message, err.code, err.cause)
        } else {
            throw err;
        }
        return;
    }

    // 在插入新内容之前，先清空编辑器的内容
    await textEditor.edit(edit => {
        const start = new vscode.Position(0, 0);
        const end = new vscode.Position(textEditor.document.lineCount - 1, textEditor.document.lineAt(textEditor.document.lineCount - 1).text.length);
        edit.delete(new vscode.Range(start, end));
    });

    try {
        // 语言模型的代码一边传回来，一边流式写入编辑器
        for await (const fragment of chatResponse.text) {
            await textEditor.edit(edit => {
                const lastLine = textEditor.document.lineAt(textEditor.document.lineCount - 1);
                const position = new vscode.Position(lastLine.lineNumber, lastLine.text.length);
                edit.insert(position, fragment);
            });
        }
    } catch (err) {
        // 异步的响应流可能会失败，例如网络中断或服务器端的错误
        await textEditor.edit(edit => {
            const lastLine = textEditor.document.lineAt(textEditor.document.lineCount - 1);
            const position = new vscode.Position(lastLine.lineNumber, lastLine.text.length);
            edit.insert(position, (<Error>err).message);
        });
    }
});
```

提示词的意思是：“你是一只猫！……你的工作是把下面代码中的所有变量名替换成有趣的猫变量名。要有创意。重要：只用代码回复，不要使用 markdown！”

这段代码的流程：

```text
1. 选择模型，把整个文件的内容和指令一起发给模型
2. 清空编辑器
3. 模型每返回一个片段，就追加到文档末尾 → 用户看到代码被一点点“打”出来
4. 中途出错，就把错误信息写到文档末尾
```

几点说明：

- 这里用的是 `registerTextEditorCommand`，回调的第一个参数就是当前编辑器（见 [命令指南](../command.md)）。
- 提示词中特别强调“只用代码回复，不要使用 markdown”，否则模型很可能会在代码外面包上 ` ``` `，写进文件就不对了。这是写提示词时常用的技巧：**明确规定输出格式**。
- 示例中 `new vscode.CancellationTokenSource().token` 是一个新建的、永远不会被取消的令牌。如果想让用户能中途取消，可以配合 [进度 API](../../extension-capabilities/common-capabilities.md#progress-api) 的 `cancellable: true`，使用它提供的 token。
- 示例同样没有处理 `model` 为 `undefined` 的情况。

---

<a id="considerations"></a>
## 注意事项（Considerations）

<a id="model-availability"></a>
### 模型的可用性（Model availability）

> 我们不希望特定的模型永远保持受支持。当你在扩展中引用一个语言模型时，在向这个语言模型发送请求时一定要采取“防御性”的做法。这意味着你应该妥善处理无法访问某个特定模型的情况。

**防御性写法：** 优先选择想要的模型，找不到时退而选择其他可用的模型：

```ts
let [model] = await vscode.lm.selectChatModels({ vendor: 'copilot', family: 'gpt-4o' });
if (!model) {
  [model] = await vscode.lm.selectChatModels({ vendor: 'copilot' });   // 退而求其次：任意 Copilot 模型
}
if (!model) {
  vscode.window.showWarningMessage('没有可用的语言模型，请先安装并登录 GitHub Copilot。');
  return;
}
```

模型列表可能在运行过程中变化（比如用户刚刚登录），可以监听 `vscode.lm.onDidChangeChatModels` 事件。

<a id="choosing-the-appropriate-model"></a>
### 选择合适的模型（Choosing the appropriate model）

> 扩展作者可以选择最适合自己扩展的模型。我们推荐使用 `gpt-4o`，因为它的性能和质量都不错。要获取可用模型的完整列表，可以使用下面的代码片段：

```typescript
const allModels = await vscode.lm.selectChatModels(MODEL_SELECTOR);
```

（这里的 `MODEL_SELECTOR` 是一个占位写法。要获取**所有**模型，直接调用 `vscode.lm.selectChatModels()`，不传参数即可。）

> **注意**
>
> 推荐的 GPT-4o 模型有 `64K` token 的限制。`selectChatModels` 调用返回的模型对象有一个 `maxInputTokens` 属性，显示了 token 的限制。随着我们更多地了解扩展是如何使用语言模型的，这些限制会被放宽。

**token** 是模型处理文本的基本单位。英文中一个单词大约是 1～2 个 token，中文中一个汉字大约是 1～2 个 token。把大文件放进提示词前，可以用 `model.countTokens(文本)` 计算 token 数，与 `model.maxInputTokens` 比较，超出时截取一部分。

<a id="rate-limiting"></a>
### 速率限制（Rate limiting）

> 扩展应该负责任地使用语言模型，并注意速率限制。VS Code 对用户是透明的：扩展如何使用语言模型、每个扩展发送了多少请求、这对它们各自的配额有什么影响，用户都可以看到。
>
> 由于速率限制，扩展不应该使用语言模型 API 进行集成测试。在内部，VS Code 使用一个专用的非生产环境语言模型来进行模拟测试，我们目前正在考虑如何为扩展提供一个可扩展的语言模型测试方案。

模型的调用次数是有配额的（用户的 Copilot 订阅有使用限制）。所以：不要在用户每敲一个字时都发请求；对结果做缓存；只在用户明确需要时才调用。

---

<a id="testing-your-extension"></a>
## 测试你的扩展（Testing your extension）

> 语言模型 API 提供的响应是不确定的（nondeterministic），这意味着对于相同的请求，你可能会得到不同的响应。这种行为可能给扩展的测试带来挑战。
>
> 扩展中构建提示词和解析语言模型响应的部分是确定的，因此可以在不使用真正语言模型的情况下进行单元测试。不过，与语言模型本身交互、从它那里获取响应，是不确定的，无法轻松地测试。请考虑以模块化的方式设计扩展代码，以便能对可以测试的特定部分进行单元测试。

例如，把代码拆成三个函数：

```ts
function buildPrompt(code: string): vscode.LanguageModelChatMessage[] { ... }  // 可以测试：输入相同，输出必然相同
async function callModel(messages): Promise<string> { ... }                     // 难以测试：每次结果不同
function parseResponse(text: string): Annotation[] { ... }                      // 可以测试：给一段固定的文字，检查解析结果
```

测试时，用一段事先准备好的“假回复”来测试 `parseResponse`，就不需要真正调用模型了。

---

<a id="publishing-your-extension"></a>
## 发布你的扩展（Publishing your extension）

> 创建好 AI 扩展之后，就可以把它发布到 Visual Studio 扩展市场：
>
> - 在发布到 VS 扩展市场之前，我们建议你阅读 [Microsoft AI 工具和实践准则](https://www.microsoft.com/en-us/ai/tools-practices)。这些准则提供了负责任地开发和使用 AI 技术的最佳实践。
> - 发布到 VS 扩展市场，意味着你的扩展遵守 [GitHub Copilot 扩展性可接受的开发和使用政策](https://docs.github.com/en/early-access/copilot/github-copilot-extensibility-platform-partnership-plugin-acceptable-development-and-use-policy)。
> - 如果你的扩展除了使用语言模型 API 之外，还提供了其他功能，我们建议你不要在[扩展清单](../../references/extension-manifest.md)中引入对 GitHub Copilot 的扩展依赖。这样可以确保不使用 GitHub Copilot 的用户，无需安装 GitHub Copilot 也能使用不依赖语言模型的功能。在这种情况下，访问语言模型时一定要有适当的错误处理。
> - 按照[发布扩展](../../working-with-extensions/publishing-extension.md)中的说明上传到扩展市场。

“扩展依赖”指的是 `package.json` 中的 `extensionDependencies` 字段：写上它，安装你的扩展时就会强制同时安装 Copilot。如果你的扩展只是“部分功能”用到 AI，就不要这样做，而是在用到 AI 时检查有没有可用的模型（就是前面“防御性写法”的那段代码）。

---

<a id="related-content"></a>
## 相关内容（Related content）

> - [语言模型 API 参考](https://code.visualstudio.com/api/references/vscode-api#lm)
> - [了解更多关于 @vscode/prompt-tsx 的信息](https://www.npmjs.com/package/@vscode/prompt-tsx)
> - [构建 VS Code 聊天扩展](./chat.md)

---

## 本篇小结

```text
三步：构建提示词 → 选择模型并发送 → 流式读取响应

1. 提示词：LanguageModelChatMessage.User / .Assistant（不支持 System，指令也写成 User）
          复杂提示词用 @vscode/prompt-tsx；利用 VS Code API 获取上下文放进提示词

2. 模型：vscode.lm.selectChatModels({ vendor, family, version, id })
        返回数组，可能为空 → 一定要处理
        首次使用需要用户同意 → 在用户主动操作时才调用
        聊天参与者中优先用 request.model（尊重用户的选择）
   请求：await model.sendRequest(messages, options, token)
        错误：LanguageModelError（NoPermissions / Blocked / NotFound）

3. 响应：for await (const fragment of response.text) { ... }
        stream 还包含工具调用等其他部分

注意：不要写死模型名（防御性选择）；maxInputTokens / countTokens 控制长度；
     注意配额；把提示词构建和响应解析拆出来做单元测试；
     部分功能用 AI 时不要依赖 Copilot 扩展
```
