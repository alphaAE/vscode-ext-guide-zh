# 构建语言模型提示词（Craft language model prompts）

> 原文：[Craft language model prompts](https://code.visualstudio.com/api/extension-guides/ai/prompt-tsx)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/ai/prompt-tsx.md`（DateApproved: 10/7/2026）

> 你可以通过字符串拼接来构建语言模型提示词，但这样很难组合各种功能，也很难确保提示词保持在语言模型的上下文窗口之内。为了克服这些限制，你可以使用 [`@vscode/prompt-tsx`](https://github.com/microsoft/vscode-prompt-tsx) 库。
>
> `@vscode/prompt-tsx` 库提供了以下功能：
>
> - **基于 TSX 的提示词渲染**：用 TSX 组件组合提示词，让它们更易读、更易维护
> - **基于优先级的裁剪**：自动裁剪提示词中不太重要的部分，使其适应模型的上下文窗口
> - **灵活的 token 管理**：使用 `flexGrow`、`flexReserve` 和 `flexBasis` 等属性，协同地使用 token 预算
> - **工具集成**：与 VS Code 的语言模型工具 API 集成
>
> 关于所有功能的完整概述和详细的使用说明，请参阅[完整的 README](https://github.com/microsoft/vscode-prompt-tsx/blob/main/README.md)。
>
> 本文介绍使用这个库进行提示词设计的一些实用示例。这些示例的完整代码可以在 [prompt-tsx 仓库](https://github.com/microsoft/vscode-prompt-tsx/tree/main/examples)中找到。

**这个库解决什么问题？** 在 [聊天参与者教程](./chat-tutorial.md) 中，提示词是这样拼起来的：

```ts
const messages = [指令, ...所有历史, 用户问题, 当前文件的全部内容];
```

问题是：历史越聊越长、文件可能很大，加起来很容易超出模型的上下文窗口（`model.maxInputTokens`）。超出后请求就会失败。手动处理“超出了先删哪部分、删多少”非常麻烦。

`prompt-tsx` 的思路是：**像写网页组件一样声明提示词的各个部分，并给每个部分标上优先级**。渲染时，库会计算 token 数，超出预算就从优先级最低的部分开始删，直到放得下为止。

**TSX 是什么？** 就是 TypeScript 中的 JSX 语法：在代码中直接写类似 HTML 的标签，比如 `<UserMessage>你好</UserMessage>`。React 用的就是这种语法，但这里它生成的不是网页，而是发给模型的消息。

---

<a id="manage-priorities-in-the-conversation-history"></a>
## 管理对话历史的优先级（Manage priorities in the conversation history）

> 在提示词中包含对话历史很重要，因为这能让用户对之前的消息提出后续问题。但是，你要确保它的优先级被恰当地对待，因为历史会随着时间变得越来越长。我们发现，最合理的模式通常是按以下顺序确定优先级：
>
> 1. 基础的提示词指令
> 2. 用户当前的查询
> 3. 最近几轮的聊天历史
> 4. 任何支撑性的数据
> 5. 在放得下的前提下，尽可能多的剩余历史
>
> 因此，在提示词中把历史分成两部分，让最近的几轮对话优先于一般的上下文信息。
>
> 在这个库中，树中的每个 TSX 节点都有一个优先级，概念上类似于 zIndex：数字越大，优先级越高。

| 优先级（从高到低） | 内容 | 为什么 |
|---|---|---|
| 1 | 基础指令 | 没有它，模型不知道自己该扮演什么、遵守什么规则 |
| 2 | 用户当前的问题 | 这次要回答的就是它 |
| 3 | 最近几轮历史 | 用户很可能在追问刚才的内容 |
| 4 | 支撑性的数据（文件内容等） | 有助于回答得更好，但可以部分省略 |
| 5 | 更早的历史 | 最不相关，最先被删 |

**zIndex** 是 CSS 中控制元素层叠顺序的属性，数字越大越靠上。这里借用这个概念：数字越大，越不容易被删。

<a id="step-1-define-the-historymessages-component"></a>
### 第 1 步：定义 HistoryMessages 组件（Step 1: Define the HistoryMessages component）

> 为了列出历史消息，定义一个 `HistoryMessages` 组件。这个示例提供了一个很好的起点，不过如果你要处理更复杂的数据类型，可能需要扩展它。
>
> 这个示例使用了 `PrioritizedList` 辅助组件，它会自动为它的每个子元素分配递增或递减的优先级。

```tsx
import {
	UserMessage,
	AssistantMessage,
	PromptElement,
	BasePromptElementProps,
	PrioritizedList,
} from '@vscode/prompt-tsx';
import { ChatContext, ChatRequestTurn, ChatResponseTurn, ChatResponseMarkdownPart } from 'vscode';

interface IHistoryMessagesProps extends BasePromptElementProps {
	history: ChatContext['history'];
}

export class HistoryMessages extends PromptElement<IHistoryMessagesProps> {
	render(): PromptPiece {
		const history: (UserMessage | AssistantMessage)[] = [];
		for (const turn of this.props.history) {
			if (turn instanceof ChatRequestTurn) {
				history.push(<UserMessage>{turn.prompt}</UserMessage>);
			} else if (turn instanceof ChatResponseTurn) {
				history.push(
					<AssistantMessage name={turn.participant}>
						{chatResponseToMarkdown(turn)}
					</AssistantMessage>
				);
			}
		}
		return (
			<PrioritizedList priority={0} descending={false}>
				{history}
			</PrioritizedList>
		);
	}
}
```

**组件的写法：**

| 部分 | 说明 |
|---|---|
| `class HistoryMessages extends PromptElement<Props>` | 一个提示词组件就是一个继承 `PromptElement` 的类 |
| `IHistoryMessagesProps extends BasePromptElementProps` | 组件接收的属性（props）。`BasePromptElementProps` 中已经包含了 `priority`、`flexGrow` 等通用属性 |
| `render()` | 返回这个组件渲染出来的内容（类似 React 组件的 `render`） |
| `<UserMessage>` / `<AssistantMessage>` | 库提供的基础组件，分别对应用户消息和助手消息 |
| `<PrioritizedList descending={false}>` | 给列表中的每一项自动分配优先级。`descending={false}` 表示**越靠后（越新）的优先级越高**，所以最早的历史会最先被删 |

这和 [聊天参与者教程](./chat-tutorial.md#step-7-add-message-history-for-more-context) 中改进后的历史处理逻辑一样：同时加入用户的提问（`ChatRequestTurn`）和参与者的回复（`ChatResponseTurn`）。

（示例中的 `chatResponseToMarkdown` 是一个没有给出的辅助函数，作用是把 `turn.response` 中的 Markdown 部分拼成字符串，写法见 [聊天参与者教程](./chat-tutorial.md#step-7-add-message-history-for-more-context) 中的改进代码。`PromptPiece` 也需要从 `@vscode/prompt-tsx` 导入，示例中省略了。）

<a id="step-2-define-the-prompt-component"></a>
### 第 2 步：定义 Prompt 组件（Step 2: Define the Prompt component）

> 接下来，定义一个 `MyPrompt` 组件，它包含基础指令、用户查询，以及带有相应优先级的历史消息。优先级的值只在兄弟元素之间比较。请记住，你可能希望在动提示词中的其他任何部分之前，先裁剪历史中较早的消息，所以需要把历史拆成两个 `<HistoryMessages>` 元素：

```tsx
import {
	UserMessage,
	PromptElement,
	BasePromptElementProps,
} from '@vscode/prompt-tsx';

interface IMyPromptProps extends BasePromptElementProps {
	history: ChatContext['history'];
	userQuery: string;
}

export class MyPrompt extends PromptElement<IMyPromptProps> {
	render() {
		return (
			<>
				<UserMessage priority={100}>
					Here are your base instructions. They have the highest priority because you want to make
					sure they're always included!
				</UserMessage>
				{/* 历史中较早的消息优先级最低，因为它们的相关性较低 */}
				<HistoryMessages history={this.props.history.slice(0, -2)} priority={0} />
				{/* 最后 2 条历史消息优先于下面的任何工作区上下文 */}
				<HistoryMessages history={this.props.history.slice(-2)} priority={80} />
				{/* 用户查询的优先级紧跟在基础指令之后 */}
				<UserMessage priority={90}>{this.props.userQuery}</UserMessage>
				<UserMessage priority={70}>
					With a slightly lower priority, you can include some contextual data about the workspace
					or files here...
				</UserMessage>
			</>
		);
	}
}
```

> 现在，在库尝试裁剪提示词的其他元素之前，所有较早的历史消息都会先被裁剪掉。

示例中各部分的优先级：

```text
priority 100  基础指令（“这里是你的基础指令……”）  ← 永远保留
priority  90  用户当前的问题
priority  80  最近 2 条历史（history.slice(-2)）
priority  70  工作区或文件的上下文数据
priority   0  更早的历史（history.slice(0, -2)）       ← 最先被删
```

- `<>...</>` 是“片段”（fragment）语法：把多个元素包在一起，但不额外生成一层。
- `slice(0, -2)` 取除了最后两条之外的所有元素，`slice(-2)` 取最后两条。
- **“优先级只在兄弟元素之间比较”**：同一层级的元素之间比较优先级。`HistoryMessages` 内部 `PrioritizedList` 分配的优先级，只在这个组件内部比较。
- **注意顺序：** 元素在 `render` 中的书写顺序，就是消息在最终提示词中的排列顺序；优先级只决定“删的时候先删谁”，不影响排列顺序。所以示例中历史写在用户问题之前，模型看到的顺序是：指令 → 历史 → 当前问题 → 上下文数据。

<a id="step-3-define-the-history-component"></a>
### 第 3 步：定义 History 组件（Step 3: Define the History component）

> 为了让使用更方便一些，定义一个 `History` 组件，它包装了历史消息，并使用 `passPriority` 属性充当一个透传容器。使用 `passPriority` 后，在确定优先级时，它的子元素会被当作它所在的那个元素的直接子元素来对待。

```tsx
import { PromptElement, BasePromptElementProps } from '@vscode/prompt-tsx';

interface IHistoryProps extends BasePromptElementProps {
	history: ChatContext['history'];
	newer: number; // 最后 2 条消息的优先级值
	older: number; // 之前消息的优先级值
	passPriority: true; // 要求必须设置这个属性！
}

export class History extends PromptElement<IHistoryProps> {
	render(): PromptPiece {
		return (
			<>
				<HistoryMessages history={this.props.history.slice(0, -2)} priority={this.props.older} />
				<HistoryMessages history={this.props.history.slice(-2)} priority={this.props.newer} />
			</>
		);
	}
}
```

> 现在，你就可以使用并复用这一个元素来包含聊天历史了：

```tsx
<History history={this.props.history} passPriority older={0} newer={80}/>
```

**为什么需要 `passPriority`？** 根据“优先级只在兄弟之间比较”的规则，如果把两个 `HistoryMessages` 包进 `History` 组件，它们就变成了 `History` 的子元素，`older={0}` 和 `newer={80}` 只在这两者之间比较，无法和外面的“用户问题（90）”“上下文（70）”比较了。

加上 `passPriority` 后，`History` 就像“透明”的一样：它的两个子元素被当作直接放在 `MyPrompt` 中，和外面的元素一起比较优先级。效果与第 2 步中直接写两个 `HistoryMessages` 完全相同，只是写起来更简洁、可以复用。

接口中把 `passPriority` 的类型写成 `true`，意思是“这个属性必须设置为 `true`”，忘了写的话 TypeScript 会报错。

---

<a id="grow-file-contents-to-fit"></a>
## 让文件内容自动扩展以填满空间（Grow file contents to fit）

> 在这个示例中，你希望在提示词中包含用户当前正在查看的所有文件的内容。这些文件可能很大，大到如果全部包含进去，它们的文本就会被裁剪掉！这个示例展示了如何使用 `flexGrow` 属性，协同地调整文件内容的大小，使其适应 token 预算。

**问题：** 优先级裁剪是“整块删除”的。如果文件内容是一个低优先级的整体，一旦超出预算就会整个被删掉，模型就完全看不到文件了。更好的做法是：**先把其他部分放好，剩下多少空间，就放多少文件内容**（比如只放用户光标附近的几十行）。这就是 `flexGrow` 的作用。

<a id="step-1-define-base-instructions-and-user-query"></a>
### 第 1 步：定义基础指令和用户查询（Step 1: Define base instructions and user query）

> 首先，定义一个包含基础指令的 `UserMessage` 组件。

```tsx
<UserMessage priority={100}>Here are your base instructions.</UserMessage>
```

> 然后，使用 `UserMessage` 组件包含用户查询。这个组件的优先级很高，确保它紧跟在基础指令之后被包含进来。

```tsx
<UserMessage priority={90}>{this.props.userQuery}</UserMessage>
```

<a id="step-2-include-the-file-contents"></a>
### 第 2 步：包含文件内容（Step 2: Include the File Contents）

> 现在可以使用 `FileContext` 组件包含文件内容了。为它设置 [`flexGrow`](https://github.com/microsoft/vscode-prompt-tsx?tab=readme-ov-file#flex-behavior) 值为 `1`，确保它在基础指令、用户查询和历史之后才被渲染。

```tsx
<FileContext priority={70} flexGrow={1} files={this.props.files} />
```

> 有了 `flexGrow` 值，这个元素就能获得所有_未使用的_ token 预算，这些预算通过传给它的 `render()` 和 `prepare()` 调用的 `PromptSizing` 对象提供。你可以在 [prompt-tsx 文档](https://github.com/microsoft/vscode-prompt-tsx?tab=readme-ov-file#flex-behavior)中了解更多关于 flex 元素行为的信息。

**`flexGrow` 的工作方式：**

```text
1. 先渲染所有没有 flexGrow 的元素（指令、用户问题），计算它们用掉了多少 token
2. 再渲染 flexGrow={1} 的元素：告诉它“还剩 N 个 token”，它根据 N 决定放多少内容
3. 再渲染 flexGrow={2} 的元素：告诉它“现在还剩 M 个 token”
```

数字越小越先渲染，越先分到剩余的预算。名字借用了 CSS 弹性布局（flexbox）中的 `flex-grow`：元素“伸展”以填满剩余的空间。

<a id="step-3-include-the-history"></a>
### 第 3 步：包含历史（Step 3: Include the history）

> 接下来，使用前面创建的 `History` 组件包含历史消息。这有点棘手，因为你既希望显示一些历史，又希望文件内容占据提示词的大部分。
>
> 因此，为 `History` 组件设置 `flexGrow` 值为 `2`，确保它在所有其他元素（包括 `<FileContext />`）之后才被渲染。但同时设置 `flexReserve` 值为 `"/5"`，为历史预留总预算的 1/5。

```tsx
<History
	history={this.props.history}
	passPriority
	older={0}
	newer={80}
	flexGrow={2}
	flexReserve="/5"
/>
```

**`flexReserve` 的作用：** 如果只设 `flexGrow={2}`，文件内容（`flexGrow={1}`）先渲染，可能把剩余的空间全部用光，历史就一点都放不下了。`flexReserve="/5"` 表示“先给我留出总预算的 1/5”，文件内容渲染时，能用的空间会扣掉这一部分。

| 属性 | 作用 |
|---|---|
| `flexGrow` | 渲染的先后顺序，越小越先拿到剩余的预算 |
| `flexReserve` | 在其他 flex 元素渲染之前，先为自己预留一部分预算（如 `"/5"` 表示 1/5） |
| `flexBasis` | 多个 flex 元素分配预算时的比例（原文未展开，详见库的 README） |

<a id="step-3-combine-all-elements-of-the-prompt"></a>
### 第 3 步：组合提示词的所有元素（Step 3: Combine all elements of the prompt）

（原文这里的步骤编号重复了，实际上是第 4 步。）

> 现在，把所有元素组合到 `MyPrompt` 组件中。

```tsx
import {
	UserMessage,
	PromptElement,
	BasePromptElementProps,
} from '@vscode/prompt-tsx';
import { History } from './history';

interface IFilesToInclude {
	document: TextDocument;
	line: number;
}

interface IMyPromptProps extends BasePromptElementProps {
	history: ChatContext['history'];
	userQuery: string;
	files: IFilesToInclude[];
}

export class MyPrompt extends PromptElement<IMyPromptProps> {
	render() {
		return (
			<>
				<UserMessage priority={100}>Here are your base instructions.</UserMessage>
				<History
					history={this.props.history}
					passPriority
					older={0}
					newer={80}
					flexGrow={2}
					flexReserve="/5"
				/>
				<UserMessage priority={90}>{this.props.userQuery}</UserMessage>
				<FileContext priority={70} flexGrow={1} files={this.props.files} />
			</>
		);
	}
}
```

`IFilesToInclude` 描述了要包含的文件：`document` 是文件，`line` 是“感兴趣的那一行”（比如光标所在的行）。`FileContext` 会以这一行为中心，在预算允许的范围内尽可能多地包含它周围的代码。

<a id="step-4-define-the-filecontext-component"></a>
### 第 4 步：定义 FileContext 组件（Step 4: Define the FileContext component）

> 最后，定义一个 `FileContext` 组件，它包含用户当前正在查看的文件的内容。因为你使用了 `flexGrow`，所以可以利用 `PromptSizing` 中的信息，实现为每个文件获取“感兴趣”的那一行周围尽可能多的行的逻辑。
>
> 为简洁起见，这里省略了 `getExpandedFiles` 的实现逻辑。你可以在 [prompt-tsx 仓库](https://github.com/microsoft/vscode-prompt-tsx/blob/5501d54a5b9a7608582e8419cd968a82ca317cc9/examples/file-contents.tsx#L103)中查看它。

```tsx
import { PromptElement, BasePromptElementProps, PromptSizing, PromptPiece } from '@vscode/prompt-tsx';

class FileContext extends PromptElement<{ files: IFilesToInclude[] } & BasePromptElementProps> {
	async render(_state: void, sizing: PromptSizing): Promise<PromptPiece> {
		const files = await this.getExpandedFiles(sizing);
		return <>{files.map(f => f.toString())}</>;
	}

	private async getExpandedFiles(sizing: PromptSizing) {
		// 这里只概括了实现细节。
		// 完整的实现请参阅仓库。
	}
}
```

`render` 的第二个参数 `sizing`（`PromptSizing`）告诉组件“你有多少 token 可用”（`sizing.tokenBudget`），还提供了计算文本 token 数的方法（`sizing.countTokens`）。`getExpandedFiles` 的思路大致是：

```text
从感兴趣的那一行开始，向上下两个方向逐行扩展
  每加一行，用 sizing.countTokens 计算总 token 数
  一旦超出 sizing.tokenBudget，就停止
返回能放下的这一段代码
```

`render` 可以是 `async` 的，这在需要读取文件等异步操作时很方便。

---

<a id="summary"></a>
## 总结（Summary）

> 在这些示例中，你创建了一个 `MyPrompt` 组件，它以不同的优先级包含了基础指令、用户查询、历史消息和文件内容。你使用了 `flexGrow`，协同地调整文件内容的大小，使其适应 token 预算。
>
> 遵循这种模式，你可以确保提示词中最重要的部分始终被包含进来，而不太重要的部分会根据需要被裁剪，以适应模型的上下文窗口。关于 `getExpandedFiles` 方法和 `FileContextTracker` 类的完整实现细节，请参阅 [prompt-tsx 仓库](https://github.com/microsoft/vscode-prompt-tsx/tree/main/examples)。

---

## 补充：如何使用定义好的提示词组件

原文没有展示如何把组件“渲染”成消息、交给模型。下面根据库的 README 补充基本用法（具体的 API 和配置以 [prompt-tsx 的 README](https://github.com/microsoft/vscode-prompt-tsx/blob/main/README.md) 为准）。

**1. 配置 TypeScript 支持 TSX。** 在 `tsconfig.json` 中加上：

```jsonc
{
  "compilerOptions": {
    "jsx": "react",
    "jsxFactory": "vscpp",
    "jsxFragmentFactory": "vscppf"
  }
}
```

并把包含组件的文件命名为 `.tsx`。（这里的 `jsxFactory` 告诉 TypeScript，`<UserMessage>` 这样的标签要编译成库提供的 `vscpp(...)` 函数调用，而不是 React 的函数。）

**2. 在聊天参与者中渲染并发送：**

```ts
import { renderPrompt } from '@vscode/prompt-tsx';
import { MyPrompt } from './prompts';

const handler: vscode.ChatRequestHandler = async (request, chatContext, stream, token) => {
  // 把组件渲染成消息数组，预算就是模型的最大输入 token 数
  const { messages } = await renderPrompt(
    MyPrompt,
    { history: chatContext.history, userQuery: request.prompt },
    { modelMaxPromptTokens: request.model.maxInputTokens },
    request.model
  );

  const response = await request.model.sendRequest(messages, {}, token);
  for await (const fragment of response.text) {
    stream.markdown(fragment);
  }
};
```

`renderPrompt` 会根据模型的 `maxInputTokens` 和优先级完成裁剪，返回可以直接传给 `sendRequest` 的消息数组。完整的用法可以参考 [聊天扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/chat-sample) 中的 `toolParticipant.ts`。

---

## 本篇小结

```text
为什么用 prompt-tsx：字符串拼接难以控制长度；超出上下文窗口时需要“按重要程度裁剪”

组件：class X extends PromptElement<Props> { render() { return <>...</> } }
  基础组件：<UserMessage>、<AssistantMessage>、<PrioritizedList>

优先级（priority）：数字越大越重要；超出预算时从最小的开始删；只在兄弟元素之间比较
  推荐顺序：指令 > 当前问题 > 最近历史 > 支撑数据 > 更早的历史
  passPriority：容器“透明”，子元素与外层元素一起比较优先级

弹性分配：
  flexGrow：数字小的先渲染，拿到剩余的预算（适合“能放多少放多少”的文件内容）
  flexReserve：提前为自己预留一部分预算（如 "/5"）
  render(state, sizing)：sizing.tokenBudget、sizing.countTokens

使用：tsconfig 配置 jsx → renderPrompt(组件, props, { modelMaxPromptTokens }, model) → messages → sendRequest
```
