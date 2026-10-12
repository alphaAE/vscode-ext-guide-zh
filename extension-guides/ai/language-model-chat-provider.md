# 语言模型聊天提供者 API（Language Model Chat Provider API）

> 原文：[Language Model Chat Provider API](https://code.visualstudio.com/api/extension-guides/ai/language-model-chat-provider)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/ai/language-model-chat-provider.md`（DateApproved: 10/7/2026）

> 语言模型聊天提供者 API 让你可以向 VS Code 的聊天贡献你自己的语言模型。

> **注意**
>
> 如果你是 Copilot Business 或 Enterprise 用户，你的管理员可以在 GitHub.com 的 [Copilot 策略设置](https://github.com/settings/copilot/features)中，为通过这个 API 提供的模型禁用 **Bring Your Own Language Model Key**（自带语言模型密钥）策略。

**这一篇的方向和前面几篇相反：**

| 前面几篇 | 本篇 |
|---|---|
| 扩展**使用** VS Code 中已有的模型（如 Copilot 提供的模型） | 扩展向 VS Code **提供**一个新的模型 |
| `vscode.lm.selectChatModels` → `sendRequest` | `vscode.lm.registerLanguageModelChatProvider` |

**典型场景：** 你们公司内部部署了一个大模型，或者你想接入某个 VS Code 还不支持的 AI 服务。写一个语言模型聊天提供者后，这个模型就会出现在聊天界面的模型下拉框中，用户可以像使用内置模型一样选择它。其他扩展通过 `selectChatModels` 也能用到它。

“自带语言模型密钥”（BYOK）就是指这种情况：用户用自己的 API 密钥接入其他模型。企业版的管理员可以禁止这种做法。

---

<a id="overview"></a>
## 概述（Overview）

> `LanguageModelChatProvider` 接口遵循“一个提供者对应多个模型”的关系，让提供者可以提供多个模型。每个提供者负责：
>
> - 发现并准备可用的语言模型
> - 处理对其模型的聊天请求
> - 提供 token 计数功能

对应 `LanguageModelChatProvider` 接口的三个方法：

| 职责 | 方法 |
|---|---|
| 告诉 VS Code 有哪些模型 | `provideLanguageModelChatInformation` |
| 处理聊天请求，返回回复 | `provideLanguageModelChatResponse` |
| 计算 token 数 | `provideTokenCount` |

---

<a id="language-model-information"></a>
## 语言模型信息（Language model information）

> 每个语言模型都必须通过 `LanguageModelChatInformation` 接口提供元数据。`provideLanguageModelChatInformation` 方法返回这些对象的数组，告诉 VS Code 有哪些可用的模型。

```typescript
interface LanguageModelChatInformation {
    readonly id: string;                    // 模型的唯一标识符，在提供者内部唯一
    readonly name: string;                  // 语言模型的人类可读名称，显示在模型选择器中
    readonly family: string;                // 模型系列名称
    readonly version: string;               // 版本字符串
    readonly maxInputTokens: number;        // 模型能接收的最大输入 token 数
    readonly maxOutputTokens: number;       // 模型能生成的最大 token 数
    readonly tooltip?: string;              // 可选：在界面中悬停在模型上时显示的提示文字
    readonly detail?: string;               // 显示在模型旁边的人类可读文字
    readonly capabilities: {
        readonly imageInput?: boolean;      // 是否支持图片输入
        readonly toolCalling?: boolean | number; // 是否支持工具调用
    };
}
```

这些字段，就是使用方通过 `selectChatModels` 拿到的模型对象上的那些属性（`family`、`version`、`maxInputTokens` 等，见 [语言模型 API](./language-model.md#send-the-language-model-request)）。

`capabilities` 中的两项很重要：如果模型不支持工具调用，就不要声明 `toolCalling: true`，否则智能体模式会把工具定义发给你，而模型无法正确处理。`toolCalling` 也可以是一个数字，表示最多支持多少个工具。

---

<a id="register-the-provider"></a>
## 注册提供者（Register the provider）

> 1. 第一步是在 `package.json` 的 `contributes.languageModelChatProviders` 部分中注册提供者。提供一个唯一的 `vendor` ID 和一个 `displayName`。

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

> 2. 接下来，在扩展的激活函数中，使用 `lm.registerLanguageModelChatProvider` 方法注册你的语言模型提供者。
>
>     提供你在 `package.json` 中使用的提供者 ID，以及你的提供者类的一个实例：

```typescript
import * as vscode from 'vscode';
import { SampleChatModelProvider } from './provider';

export function activate(_: vscode.ExtensionContext) {
    vscode.lm.registerLanguageModelChatProvider('my-provider', new SampleChatModelProvider());
}
```

`vendor`（供应商）就是使用方在 `selectChatModels({ vendor: 'my-provider' })` 中用来筛选的那个值，相当于 Copilot 的 `'copilot'`。注册返回的 Disposable 记得放进 `context.subscriptions`。

> 3. 你还可以选择在 `package.json` 中提供一个 `contributes.languageModelChatProviders.managementCommand`，让用户可以管理这个语言模型提供者。
>
>     `managementCommand` 属性的值必须是 `package.json` 的 `contributes.commands` 部分中定义的一个命令。在扩展中注册这个命令（`vscode.commands.registerCommand`），并实现管理提供者的逻辑，比如配置 API 密钥或其他设置。

```json
{
    "contributes": {
        "languageModelChatProviders": [
            {
                "vendor": "my-provider",
                "displayName": "My Provider",
                "managementCommand": "my-provider.manage"
            }
        ],
        "commands": [
            {
                "command": "my-provider.manage",
                "title": "Manage My Provider"
            }
        ]
    }
}
```

管理命令的典型实现：让用户输入 API 密钥，并安全地保存起来。

```ts
context.subscriptions.push(
  vscode.commands.registerCommand('my-provider.manage', async () => {
    const key = await vscode.window.showInputBox({ prompt: '请输入 My Provider 的 API 密钥', password: true });
    if (key) {
      await context.secrets.store('my-provider.apiKey', key);   // 存进加密存储，不要放在 globalState 或设置中
    }
  })
);
```

`secrets` 的用法见 [通用能力](../../extension-capabilities/common-capabilities.md#data-storage)。

---

<a id="implement-the-provider"></a>
## 实现提供者（Implement the provider）

> 语言提供者必须实现 `LanguageModelChatProvider` 接口，它有三个主要方法：
>
> - `provideLanguageModelChatInformation`：返回可用模型的列表
> - `provideLanguageModelChatResponse`：处理聊天请求，并以流的方式返回回复
> - `provideTokenCount`：实现 token 计数功能

此外，接口中还有一个可选的事件 `onDidChangeLanguageModelChatInformation`：模型列表发生变化时（比如用户刚配置好 API 密钥），触发它，VS Code 会重新获取模型列表。

<a id="prepare-language-model-information"></a>
### 准备语言模型信息（Prepare language model information）

> VS Code 调用 `provideLanguageModelChatInformation` 方法来发现可用的模型，这个方法返回一个 `LanguageModelChatInformation` 对象的列表。
>
> 使用 `options.silent` 参数，控制是否提示用户输入凭据或额外的配置：

```typescript
async provideLanguageModelChatInformation(
    options: { silent: boolean },
    token: CancellationToken
): Promise<LanguageModelChatInformation[]> {
    if (options.silent) {
        return []; // 静默模式下不提示用户
    } else {
        await this.promptForApiKey(); // 提示用户输入凭据
    }

    // 从你的服务获取可用的模型
    const models = await this.fetchAvailableModels();

    // 把你的模型映射为 LanguageModelChatInformation 格式
    return models.map(model => ({
        id: model.id,
        name: model.displayName,
        family: model.family,
        version: '1.0.0',
        maxInputTokens: model.contextWindow - model.maxOutput,
        maxOutputTokens: model.maxOutput,
        capabilities: {
            imageInput: model.supportsImages,
            toolCalling: model.supportsTools
        }
    }));
}
```

**`silent`（静默）是什么意思？** VS Code 会在不同的时机调用这个方法：

| `silent` | 调用时机 | 能否弹窗 |
|---|---|---|
| `true` | 后台获取模型列表（比如 VS Code 启动时） | **不能**，用户没有主动操作，突然弹出一个输入框会很奇怪 |
| `false` | 用户主动操作（比如在模型选择器中选择了你的提供者） | 可以，此时让用户输入 API 密钥是合理的 |

示例中静默模式下直接返回空数组，这样写有一个问题：即使用户之前已经配置过密钥，启动时模型列表也是空的。更好的写法是：静默模式下检查**已保存的**密钥，有就正常返回模型，没有才返回空数组：

```ts
const apiKey = await this.secrets.get('my-provider.apiKey');
if (!apiKey) {
  if (options.silent) {
    return [];                       // 没有密钥，又不能弹窗
  }
  await this.promptForApiKey();      // 用户主动操作：可以要求输入密钥
}
```

`maxInputTokens: model.contextWindow - model.maxOutput`：很多模型的上下文窗口是“输入 + 输出”的总和，所以要给输出留出空间，可用的输入 token 数要减去最大输出 token 数。

`promptForApiKey` 和 `fetchAvailableModels` 是示例中省略了实现的方法。

<a id="handle-chat-requests"></a>
### 处理聊天请求（Handle chat requests）

> `provideLanguageModelChatResponse` 方法处理实际的聊天请求。提供者会收到一个 `LanguageModelChatRequestMessage` 格式的消息数组，你可以选择把它们转换成你的语言模型 API 所需的格式（参见[消息格式与转换](#message-format-and-conversion)）。
>
> 使用 `progress` 参数以流的方式返回回复的片段。回复可以包含文本部分、工具调用和工具结果（参见[回复的部分](#response-parts)）。

```typescript
async provideLanguageModelChatResponse(
    model: LanguageModelChatInformation,
    messages: readonly LanguageModelChatRequestMessage[],
    options: ProvideLanguageModelChatResponseOptions,
    progress: Progress<LanguageModelResponsePart>,
    token: CancellationToken
): Promise<void> {

    // TODO: 实现消息转换、处理和回复的流式输出

    // 可以根据模型 ID 区分不同的行为
    if (model.id === "my-model-a") {
        progress.report(new LanguageModelTextPart("This is my A response."));
    } else {
        progress.report(new LanguageModelTextPart("Unknown model."));
    }
}
```

| 参数 | 内容 |
|---|---|
| `model` | 使用方选择的是你提供的哪一个模型 |
| `messages` | 使用方发来的消息（就是使用方 `sendRequest(messages, ...)` 中的那些） |
| `options` | 请求选项，比如可用的工具（`tools`）等 |
| `progress` | 用来**逐块返回回复**：每调用一次 `progress.report(...)`，使用方的 `for await` 就会收到一个片段 |
| `token` | 取消令牌：使用方取消请求时，应该中止对你的服务的请求 |

**这里和使用方的代码是一一对应的：**

```text
使用方：  const response = await model.sendRequest(messages, options, token);
          for await (const fragment of response.text) { ... }
             ↓ VS Code 转发
提供者：  provideLanguageModelChatResponse(model, messages, options, progress, token)
          progress.report(new LanguageModelTextPart('片段1'))   → 使用方收到 '片段1'
          progress.report(new LanguageModelTextPart('片段2'))   → 使用方收到 '片段2'
          方法返回（Promise 完成）                              → 使用方的 for await 结束
```

实际实现时，通常是调用你的 AI 服务的流式接口，每收到一段文字就 `progress.report` 一次。

<a id="provide-token-count"></a>
### 提供 token 计数（Provide token count）

> `provideTokenCount` 方法负责估算给定文本输入中的 token 数：

```typescript
async provideTokenCount(
    model: LanguageModelChatInformation,
    text: string | LanguageModelChatRequestMessage,
    token: CancellationToken
): Promise<number> {
    // TODO: 为你的模型实现 token 计数

    // 字符串的估算示例
    return Math.ceil(text.toString().length / 4);
}
```

`length / 4` 是一个非常粗略的估算（英文中平均约 4 个字符一个 token）。对中文来说这个估算偏低（中文大约 1～2 个字符一个 token）。准确的做法是使用你的模型对应的分词器（tokenizer）。使用方调用 `model.countTokens(...)` 时（见 [语言模型 API](./language-model.md#choosing-the-appropriate-model)），实际调用的就是这个方法，[Prompt TSX](./prompt-tsx.md) 裁剪提示词时也依赖它，所以估算得越准，裁剪得越合理。

注意 `text` 也可能是一条消息对象，这时 `text.toString()` 得不到消息的文字内容，需要像下面“消息转换”那样取出其中的文本部分再计算。

---

<a id="message-format-and-conversion"></a>
## 消息格式与转换（Message format and conversion）

> 你的提供者会收到 `LanguageModelChatRequestMessage` 格式的消息，通常需要把它们转换成你的服务的 API 格式。消息的内容可以是文本部分、工具调用和工具结果的混合。

```typescript
interface LanguageModelChatRequestMessage {
    readonly role: LanguageModelChatMessageRole;
    readonly content: ReadonlyArray<LanguageModelInputPart | unknown>;
    readonly name: string | undefined;
}
```

> 你可以选择把这些消息适当地转换为你的语言模型 API 所需的格式：

```typescript
private convertMessages(messages: readonly LanguageModelChatRequestMessage[]) {
    return messages.map(msg => ({
        role: msg.role === vscode.LanguageModelChatMessageRole.User ? 'user' : 'assistant',
        content: msg.content
            .filter(part => part instanceof vscode.LanguageModelTextPart)
            .map(part => (part as vscode.LanguageModelTextPart).value)
            .join('')
    }));
}
```

这段代码把 VS Code 的消息转换成大多数 AI 服务常见的 `{ role: 'user' | 'assistant', content: '文本' }` 格式：只保留文本部分，拼成一个字符串。

这是最简化的转换。如果你的模型支持工具调用，还要处理内容中的 `LanguageModelToolCallPart`（模型之前请求的工具调用）和 `LanguageModelToolResultPart`（工具执行的结果），把它们转换成你的服务要求的工具调用格式；支持图片输入的话，还要处理 `LanguageModelDataPart`。

---

<a id="response-parts"></a>
## 回复的部分（Response parts）

> 你的提供者可以通过 `LanguageModelResponsePart` 类型，经由 progress 回调报告不同类型的回复部分，它可以是以下之一：
>
> - `LanguageModelTextPart`：文本内容
> - `LanguageModelToolCallPart`：工具 / 函数调用
> - `LanguageModelToolResultPart`：工具结果的内容

（当前的类型定义（`@types/vscode` 1.140）中，`LanguageModelResponsePart` 还包括 `LanguageModelDataPart`，用于返回图片等二进制数据。）

当你的模型决定调用工具时，就 `report` 一个 `LanguageModelToolCallPart`：

```ts
progress.report(new vscode.LanguageModelToolCallPart(
  'call_1',                    // callId：这次调用的唯一 ID
  'get_weather',               // name：要调用的工具名
  { location: 'Beijing' }      // input：工具的参数
));
```

使用方（比如 [聊天参与者](./chat.md#implement-tool-calling-yourself) 或智能体模式）读取 `response.stream` 时，就会收到这个工具调用请求，执行工具后再把结果发回来。

---

<a id="getting-started"></a>
## 开始上手（Getting started）

> 你可以从一个[基础的示例项目](https://github.com/microsoft/vscode-extension-samples/blob/main/chat-model-provider-sample)开始。

---

<a id="related-content"></a>
## 相关内容（Related content）

> - [VS Code API 参考](https://code.visualstudio.com/api/references/vscode-api)
> - [语言模型 API 指南](./language-model.md)
> - [聊天 API 扩展](./chat.md)

---

## 本篇小结

```text
方向：扩展向 VS Code 提供模型（与 selectChatModels + sendRequest 的使用方相对）

package.json：contributes.languageModelChatProviders（vendor、displayName、managementCommand）
代码：vscode.lm.registerLanguageModelChatProvider(vendor, provider)

LanguageModelChatProvider
  provideLanguageModelChatInformation(options, token)
    → [{ id, name, family, version, maxInputTokens, maxOutputTokens, capabilities }]
    options.silent 为 true 时不能弹窗（但应该检查已保存的密钥）
  provideLanguageModelChatResponse(model, messages, options, progress, token)
    → 转换消息 → 调用你的服务 → progress.report(TextPart / ToolCallPart / …) 逐块返回
  provideTokenCount(model, text, token) → 越准越好（影响提示词裁剪）
  onDidChangeLanguageModelChatInformation（可选）→ 模型列表变化时通知

密钥：管理命令中让用户输入，存进 context.secrets
```
