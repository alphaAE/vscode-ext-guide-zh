# 教程：使用语言模型 API 生成 AI 代码注释（Tutorial: Generate AI-powered code annotations by using the Language Model API）

> 原文：[Tutorial: Generate AI-powered code annotations by using the Language Model API](https://code.visualstudio.com/api/extension-guides/ai/language-model-tutorial)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/ai/language-model-tutorial.md`（DateApproved: 10/7/2026）

> 在本教程中，你将学习如何创建一个 VS Code 扩展，构建一个 AI 驱动的“代码导师”（Code Tutor）。你会使用语言模型（LM）API 生成改进代码的建议，并利用 VS Code 扩展 API，把这些建议以行内注释的形式无缝地集成到编辑器中，用户可以把鼠标悬停在上面查看更多信息。完成本教程后，你就会知道如何在 VS Code 中实现自定义的 AI 功能。

![VS Code 中显示来自 GitHub Copilot 的自定义注释](../images/ai/lm-api/code-tutor-annotations-gif.gif)

动图中，点击编辑器标题栏上的评论图标后，代码中某些行的末尾陆续出现了灰色的建议文字；鼠标悬停在上面，会弹出完整的建议。

这个教程把 [语言模型 API](./language-model.md) 中讲的“构建提示词 → 发送请求 → 解析响应”三个步骤完整地走一遍，同时用到了前面学过的命令、编辑器装饰、菜单等知识。

---

<a id="prerequisites"></a>
## 准备工作（Prerequisites）

> 你需要以下工具和账号来完成本教程：
>
> - [Visual Studio Code](https://code.visualstudio.com/download)
> - [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat)
> - [Node.js](https://nodejs.org/en/download/)

需要 GitHub Copilot，是因为本教程用的是 Copilot 提供的语言模型。你需要登录一个有 Copilot 使用权限的 GitHub 账号。

---

<a id="scaffold-out-the-extension"></a>
## 生成扩展的脚手架（Scaffold out the extension）

> 首先，使用 Yeoman 和 VS Code 扩展生成器，搭建一个可以直接开发的 TypeScript 或 JavaScript 项目。

```bash
npx --package yo --package generator-code -- yo code
```

> 选择以下选项，完成新建扩展的向导……

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

这和 [你的第一个扩展](../../get-started/your-first-extension.md) 中的步骤一样。（新版生成器中关于打包工具的问题写作 “Which bundler to use?”，选 `unbundled` 即可。）

---

<a id="modify-the-packagejson-file-to-include-the-correct-commands"></a>
## 修改 package.json，加入正确的命令（Modify the package.json file to include the correct commands）

> 生成的项目在 `package.json` 文件中包含一个 “helloWorld” 命令。扩展安装后，这个命令会出现在命令面板中。

```json
"contributes": {
  "commands": [
      {
      "command": "code-tutor.helloWorld",
      "title": "Hello World"
      }
  ]
}
```

> 由于我们要构建的是一个会给代码行添加注释的代码导师扩展，所以需要一个命令，让用户可以开启和关闭这些注释。更新 `command` 和 `title` 属性：

```json
"contributes": {
  "commands": [
      {
      "command": "code-tutor.annotate",
      "title": "Toggle Tutor Annotations"
      }
  ]
}
```

> `package.json` 定义了扩展的命令和界面元素，而 `src/extension.ts` 文件中放的是这些命令要执行的代码。
>
> 打开 `src/extension.ts` 文件，修改 `registerCommand` 方法，让它与 `package.json` 文件中的 `command` 属性一致。

```ts
const disposable = vscode.commands.registerCommand('code-tutor.annotate', () => {
```

> 按 `F5` 运行扩展。这会打开一个安装了扩展的新 VS Code 实例。按 `Ctrl+Shift+P` 打开命令面板，搜索 “tutor”。你应该能看到 “Tutor Annotations” 命令。

![VS Code 命令面板中的 “Toggle Tutor Annotations” 命令](../images/ai/lm-api/tutor-command-command-palette.png)

> 如果选择 “Tutor Annotations” 命令，你会看到一条 “Hello World” 通知消息。

![通知中显示了消息 “Hello World from Code Tutor”](../images/ai/lm-api/code-tutor-hello-world.png)

到这里为止，和 Hello World 扩展完全一样，只是改了命令 ID 和标题。“声明 + 实现两边 ID 一致”的原理见 [扩展的结构](../../get-started/extension-anatomy.md)。

---

<a id="implement-the-annotate-command"></a>
## 实现 “annotate” 命令（Implement the "annotate" command）

> 为了让代码导师的注释功能工作起来，我们需要把一些代码发给它，并要求它提供注释。我们分三步来做：
>
> 1. 从用户当前打开的标签页中获取代码，并带上行号。
> 2. 把这些代码和一个自定义的提示词一起发送给语言模型 API，提示词会指示模型如何提供注释。
> 3. 解析注释，并在编辑器中显示它们。

<a id="step-1-get-the-code-with-line-numbers"></a>
### 第 1 步：获取带行号的代码（Step 1: Get the code with line numbers）

> 要从当前标签页获取代码，我们需要一个对用户当前打开的标签页的引用。可以把 `registerCommand` 方法改成 `registerTextEditorCommand` 来得到它。这两个命令的区别是，后者会给我们一个对用户当前打开的标签页的引用，称为 `TextEditor`。

```ts
const disposable = vscode.commands.registerTextEditorCommand('code-tutor.annotate', async (textEditor: vscode.TextEditor) => {
```

`registerTextEditorCommand` 在 [命令指南](../command.md) 中介绍过：它会自动把当前活动的编辑器作为第一个参数传进来，并且只在有活动的文本编辑器时才执行。

> 现在，我们可以用 `textEditor` 引用获取“可见编辑器区域”中的所有代码。也就是屏幕上能看到的代码，不包括可见区域上方或下方的代码。
>
> 在 `extension.ts` 文件底部的 `export function deactivate() { }` 这一行的正上方，添加下面的方法。

```ts
function getVisibleCodeWithLineNumbers(textEditor: vscode.TextEditor) {
  // 获取第一个和最后一个可见行的位置
  let currentLine = textEditor.visibleRanges[0].start.line;
  const endLine = textEditor.visibleRanges[0].end.line;

  let code = '';

  // 获取当前位置那一行的文本。
  // 行号是从 0 开始的，所以加 1，让它从 1 开始。
  while (currentLine < endLine) {
    code += `${currentLine + 1}: ${textEditor.document.lineAt(currentLine).text} \n`;
    // 移动到下一行的位置
    currentLine++;
  }
  return code;
}
```

> 这段代码使用 TextEditor 的 `visibleRanges` 属性，获取编辑器中当前可见的那些行的位置。然后从第一行的位置开始，一直移动到最后一行的位置，把每一行代码连同行号一起添加到一个字符串中。最后，返回包含所有可见代码及其行号的字符串。

生成的字符串类似这样：

```text
1: function add(a, b) {
2:   var result = a + b
3:   return result
4: }
```

**为什么要加行号？** 我们希望模型告诉我们“第几行有问题”。给每行加上行号，模型才能在回复中准确地指出行号，我们再根据行号把建议显示在对应的行上。

**为什么只取可见区域？** 一是控制提示词的长度（大文件全部发过去可能超出 token 限制，也更慢、更费配额）；二是用户关心的通常就是眼前这段代码。

（小问题：`while (currentLine < endLine)` 会漏掉最后一个可见行，改成 `<=` 更准确。）

> 现在，我们可以在 `code-tutor.annotate` 命令中调用这个方法了。修改命令的实现，让它看起来像这样：

```ts
const disposable = vscode.commands.registerTextEditorCommand('code-tutor.annotate', async (textEditor: vscode.TextEditor) => {

  // 从当前编辑器获取带行号的代码
  const codeWithLineNumbers = getVisibleCodeWithLineNumbers(textEditor);

});
```

<a id="step-2-send-code-and-prompt-to-language-model-api"></a>
### 第 2 步：把代码和提示词发送给语言模型 API（Step 2: Send code and prompt to language model API）

> 下一步是调用 GitHub Copilot 的语言模型，把用户的代码连同创建注释的指令一起发送给它。
>
> 为此，我们首先需要指定要使用哪个聊天模型。这里我们选择 4o，因为对于我们要构建的这种交互来说，它是一个快速又能干的模型。

```ts
const disposable = vscode.commands.registerTextEditorCommand('code-tutor.annotate', async (textEditor: vscode.TextEditor) => {

  // 从当前编辑器获取带行号的代码
  const codeWithLineNumbers = getVisibleCodeWithLineNumbers(textEditor);

  // 选择 4o 聊天模型
  let [model] = await vscode.lm.selectChatModels({
    vendor: 'copilot',
    family: 'gpt-4o',
  });
});
```

（如 [语言模型 API](./language-model.md#model-availability) 中所说，可用的模型会随时间变化。如果 `gpt-4o` 不可用，可以去掉 `family` 条件，使用任意可用的 Copilot 模型。）

> 我们需要一些指令，也就是“提示词”，告诉模型去创建注释，以及我们希望回复是什么格式。把下面的代码添加到文件顶部、紧挨在 import 语句下方的位置。

```ts
const ANNOTATION_PROMPT = `You are a code tutor who helps students learn how to write better code. Your job is to evaluate a block of code that the user gives you and then annotate any lines that could be improved with a brief suggestion and the reason why you are making that suggestion. Only make suggestions when you feel the severity is enough that it will impact the readability and maintainability of the code. Be friendly with your suggestions and remember that these are students so they need gentle guidance. Format each suggestion as a single JSON object. It is not necessary to wrap your response in triple backticks. Here is an example of what your response should look like:

{ "line": 1, "suggestion": "I think you should use a for loop instead of a while loop. A for loop is more concise and easier to read." }{ "line": 12, "suggestion": "I think you should use a for loop instead of a while loop. A for loop is more concise and easier to read." }
`;
```

提示词的意思是：

> 你是一位帮助学生学习如何写出更好代码的代码导师。你的工作是评估用户给你的一段代码，然后为任何可以改进的行添加注释，给出简短的建议，以及提出这个建议的原因。只有当你觉得问题严重到会影响代码的可读性和可维护性时，才提出建议。建议要友好，记住这些是学生，他们需要温和的指导。把每条建议格式化为一个单独的 JSON 对象。不需要用三个反引号包裹你的回复。下面是你的回复应该是什么样子的示例：（后面是两个 JSON 对象的示例）

> 这是一个特殊的提示词，它指示语言模型如何生成注释。它还包含了模型应该如何格式化回复的示例。这些示例（也叫“多样本”，multi-shot）让我们可以定义回复的格式，以便解析它并把它显示为注释。

**这段提示词体现了几个常用的技巧：**

| 技巧 | 在提示词中的体现 |
|---|---|
| 设定角色 | “你是一位代码导师” |
| 说明任务 | 评估代码，为可以改进的行添加建议 |
| 控制范围 | “只有问题严重时才提出建议”，避免模型对每一行都挑毛病 |
| 设定语气 | “友好”“温和的指导” |
| **规定输出格式** | 每条建议是一个 JSON 对象，不要用反引号包裹 |
| **给出示例**（multi-shot） | 直接展示期望的输出长什么样 |

最后两点最关键：我们的代码要**用程序解析**模型的回复，所以必须让模型严格按照固定的格式输出。只用文字描述格式，模型不一定照做；给出具体的示例，效果会好得多。

如果希望建议用中文显示，可以在提示词中加一句 “Write the suggestions in Chinese.”（或者直接用中文写整段提示词）。

> 我们以数组的形式把消息传给模型。这个数组可以包含任意多条消息。在我们的例子中，它包含提示词，后面跟着带行号的用户代码。

```ts
const disposable = vscode.commands.registerTextEditorCommand('code-tutor.annotate', async (textEditor: vscode.TextEditor) => {

  // 从当前编辑器获取带行号的代码
  const codeWithLineNumbers = getVisibleCodeWithLineNumbers(textEditor);

  // 选择 4o 聊天模型
  let [model] = await vscode.lm.selectChatModels({
    vendor: 'copilot',
    family: 'gpt-4o',
  });

  // 初始化聊天消息
  const messages = [
    vscode.LanguageModelChatMessage.User(ANNOTATION_PROMPT),
    vscode.LanguageModelChatMessage.User(codeWithLineNumbers),
  ];
});
```

> 要把消息发送给模型，我们首先要确保所选的模型是可用的。这可以处理扩展还没准备好、或者用户没有登录 GitHub Copilot 的情况。然后我们把消息发送给模型。

```ts
const disposable = vscode.commands.registerTextEditorCommand('code-tutor.annotate', async (textEditor: vscode.TextEditor) => {

  // 从当前编辑器获取带行号的代码
  const codeWithLineNumbers = getVisibleCodeWithLineNumbers(textEditor);

  // 选择 4o 聊天模型
  let [model] = await vscode.lm.selectChatModels({
    vendor: 'copilot',
    family: 'gpt-4o',
  });

  // 初始化聊天消息
  const messages = [
    vscode.LanguageModelChatMessage.User(ANNOTATION_PROMPT),
    vscode.LanguageModelChatMessage.User(codeWithLineNumbers),
  ];

  // 确保模型可用
  if (model) {

    // 把消息数组发送给模型，并获取响应
    let chatResponse = await model.sendRequest(messages, {}, new vscode.CancellationTokenSource().token);

    // 处理聊天响应
    await parseChatResponse(chatResponse, textEditor);
  }
});
```

`if (model)` 就是 [语言模型 API](./language-model.md) 中强调的“处理没有可用模型的情况”。不过这里模型不可用时什么都不做，用户会觉得命令没反应，最好加一个 `else` 分支，提示用户登录 Copilot。另外 `sendRequest` 也可能抛出 `LanguageModelError`（比如用户拒绝授权），可以用 `try/catch` 包起来。

### 第 3 步：解析响应并显示注释

（原文这一部分没有单独的小标题，这里为了清晰加上了。）

> 聊天的响应是以片段（fragment）的形式传来的。这些片段通常只包含单个单词，但有时只包含标点符号。为了在响应流式传来时就显示注释，我们要等到拿到一条完整的注释之后再显示它。根据我们指示模型返回回复的方式，我们知道看到一个右大括号 `}` 时，就得到了一条完整的注释。然后就可以解析这条注释，并在编辑器中显示它。
>
> 在 `extension.ts` 文件中 `getVisibleCodeWithLineNumbers` 方法的上方，添加缺少的 `parseChatResponse` 函数。

```ts
async function parseChatResponse(chatResponse: vscode.LanguageModelChatResponse, textEditor: vscode.TextEditor) {
 let accumulatedResponse = "";

 for await (const fragment of chatResponse.text) {
  accumulatedResponse += fragment;

  // 如果片段中有 }，就可以尝试解析整行
  if (fragment.includes("}")) {
   try {
    const annotation = JSON.parse(accumulatedResponse);
    applyDecoration(textEditor, annotation.line, annotation.suggestion);
    // 为下一行重置累加器
    accumulatedResponse = "";
   }
   catch (e) {
    // 什么也不做
   }
  }
 }
}
```

**流式解析的思路：**

```text
模型返回的片段：  { "line  ":  3,  "sugg  estion  ":  "Use  const  ..."  }  { "line ...
累加到字符串：   {"line": 3, "suggestion": "Use const ..."}
                                                         ↑ 看到 }，尝试 JSON.parse
                 解析成功 → 显示这条注释 → 清空累加的字符串，开始接收下一条
                 解析失败 → 说明还不完整（比如建议文字里本身就有 }），继续累加
```

这样，模型每生成完一条建议，编辑器中就立即显示一条，而不用等全部生成完。这就是动图中注释一条一条出现的原因。

（这种写法比较简单，有一种情况会出问题：如果一个片段中既包含上一条的 `}`，又包含下一条的开头 `{`，解析会失败，两条建议就都丢了。更稳妥的做法是在累加的字符串中查找每一个完整的 `{...}` 对象再解析。）

> 我们还需要最后一个方法来真正显示注释。VS Code 把它们称为“装饰”（decoration）。在 `extension.ts` 文件中 `parseChatResponse` 方法的上方，添加下面的方法。

```ts
function applyDecoration(editor: vscode.TextEditor, line: number, suggestion: string) {

 const decorationType = vscode.window.createTextEditorDecorationType({
  after: {
   contentText: ` ${suggestion.substring(0, 25) + "..."}`,
   color: "grey",
  },
 });

 // 获取指定行号那一行的末尾
 const lineLength = editor.document.lineAt(line - 1).text.length;
 const range = new vscode.Range(
  new vscode.Position(line - 1, lineLength),
  new vscode.Position(line - 1, lineLength),
 );

 const decoration = { range: range, hoverMessage: suggestion };

 vscode.window.activeTextEditor?.setDecorations(decorationType, [
  decoration,
 ]);
}
```

> 这个方法接收我们从模型解析出的注释，并用它创建一个装饰。首先创建一个 `TextEditorDecorationType`，指定装饰的外观。在这个例子中，我们只是添加一条灰色的注释，并把它截断为 25 个字符。用户把鼠标悬停在这条消息上时，我们会显示完整的消息。
>
> 然后设置装饰应该出现的位置。它需要在注释中指定的那个行号上，并且位于这一行的末尾。
>
> 最后，在活动的文本编辑器上设置装饰，这样注释就会出现在编辑器中。

**编辑器装饰（decoration）**是在编辑器中给文本添加视觉效果的 API，比如背景色、边框、下划线，或者像这里一样在行尾追加一段文字。它分两步：

| 步骤 | API | 作用 |
|---|---|---|
| 1. 定义样式 | `window.createTextEditorDecorationType({...})` | 定义“长什么样”：颜色、边框、`before` / `after` 中追加的文字等 |
| 2. 应用到位置 | `editor.setDecorations(样式, [范围...])` | 指定“在哪里显示”；每个范围还可以带 `hoverMessage`（悬停提示） |

代码中的几个细节：

- **`line - 1`**：模型返回的行号是从 1 开始的（因为我们在第 1 步中给行号加了 1），而 VS Code 的 `Position` 行号是从 0 开始的，所以要减 1。
- **范围的起点和终点相同**：`after` 装饰会把文字显示在范围的后面，所以只需要一个“点”（行末尾的位置）。
- **截断为 25 个字符**：行尾空间有限，只显示开头，悬停时通过 `hoverMessage` 显示完整内容。

**原文代码中值得改进的几处：**

1. 示例用的是 `vscode.window.activeTextEditor?.setDecorations(...)`，而不是传进来的 `editor`。如果用户在模型生成的过程中切换了标签页，注释就会被加到错误的文件上。应该改成 `editor.setDecorations(...)`。
2. 每条建议都新建一个 `decorationType`，但从来没有释放。`setDecorations` 是“替换”语义：对同一个样式再次调用，会替换掉它之前的所有范围。原文为了让多条注释同时显示，只好每条用一个新样式，结果这些样式永远留在编辑器中，也就无法再清除。
3. 命令叫 “Toggle”（切换），但原文的实现只能添加注释，不能关闭。

**补充：一个真正能“切换”的写法。** 用同一个装饰样式，收集所有注释后一起设置；再次执行命令时清除：

```ts
// 整个扩展共用一个装饰样式
const annotationDecoration = vscode.window.createTextEditorDecorationType({
  after: { color: 'grey', margin: '0 0 0 1em' }
});

// 记录哪些编辑器当前显示着注释
const annotatedEditors = new Set<vscode.TextEditor>();

async function toggleAnnotations(textEditor: vscode.TextEditor) {
  if (annotatedEditors.has(textEditor)) {
    textEditor.setDecorations(annotationDecoration, []);   // 传空数组 = 清除
    annotatedEditors.delete(textEditor);
    return;
  }
  // ……获取代码、调用模型（同上）……
}

// 每解析出一条注释，就加到数组里，再整体设置一次
const decorations: vscode.DecorationOptions[] = [];
function addAnnotation(editor: vscode.TextEditor, line: number, suggestion: string) {
  const end = editor.document.lineAt(line - 1).range.end;
  decorations.push({
    range: new vscode.Range(end, end),
    hoverMessage: suggestion,
    renderOptions: { after: { contentText: suggestion.substring(0, 25) + '...' } }  // 每条显示不同的文字
  });
  editor.setDecorations(annotationDecoration, decorations);
  annotatedEditors.add(editor);
}
```

关键在于 `renderOptions`：样式中定义公共的外观（灰色、左边距），每条注释的文字通过各自的 `renderOptions.after.contentText` 单独指定。这样只需要一个装饰样式，清除时传空数组即可。记得在 `activate` 中把 `annotationDecoration` 放进 `context.subscriptions`。（`decorations` 数组在每次开始新的注释前要清空；这里为了突出重点省略了。）

> 如果你的扩展仍在运行，就选择调试工具栏上的绿色箭头重启它。如果你关闭了调试会话，就按 `F5` 运行扩展。在打开的新 VS Code 窗口实例中打开一个代码文件。从命令面板中选择 “Toggle Tutor Annotations” 时，你应该能看到代码注释出现在编辑器中。

![一个带有 GitHub Copilot 注释的代码文件](../images/ai/lm-api/code-with-annotations.png)

---

<a id="add-a-button-to-the-editor-title-bar"></a>
## 在编辑器标题栏中添加按钮（Add a button to the editor title bar）

> 你可以让命令在命令面板之外的地方也能被调用。在我们的例子中，可以在当前标签页的顶部添加一个按钮，让用户可以方便地开关注释。
>
> 为此，按如下方式修改 `package.json` 的 “contributes” 部分：

```json
"contributes": {
  "commands": [
    {
      "command": "code-tutor.annotate",
      "title": "Toggle Tutor Annotations",
      "icon": "$(comment)"
    }
  ],
  "menus": {
    "editor/title": [
      {
        "command": "code-tutor.annotate",
        "group": "navigation"
      }
    ]
  }
}
```

> 这会让一个按钮出现在编辑器标题栏的导航区域（右侧）。“icon” 来自[产品图标参考](../../references/icons-in-labels.md)。

用到的都是前面学过的内容：

| 配置 | 作用 | 在哪里学过 |
|---|---|---|
| `"icon": "$(comment)"` | 命令显示成按钮时，用内置的 `comment` 图标（codicon） | [产品图标主题](../product-icon-theme.md) |
| `menus.editor/title` | 把命令放到编辑器标题栏 | [虚拟文档](../virtual-documents.md#add-editor-commands) |
| `"group": "navigation"` | 显示为图标按钮，而不是收进 `...` 菜单 | [树视图](../tree-view.md#view-actions) |

> 如果扩展还没有运行，就用绿色箭头重启它，或者按 `F5`。现在你应该能看到一个评论图标，点击它会触发 “Toggle Tutor Annotations” 命令。

![VS Code 中活动标签页的标题栏上出现了一个评论图标](../images/ai/lm-api/code-tutor-annotations-gif.gif)

---

<a id="next-steps"></a>
## 下一步（Next Steps）

> 在本教程中，你学会了如何创建一个 VS Code 扩展，用语言模型 API 把 AI 集成到编辑器中。你使用 VS Code 扩展 API 从当前标签页获取代码，用一个自定义的提示词把它发送给模型，然后解析模型的结果，并用装饰直接在编辑器中显示出来。
>
> 接下来，你可以扩展你的代码导师扩展，让它也[包含一个聊天参与者](./chat-tutorial.md)，这样用户就可以通过 GitHub Copilot 的聊天界面直接与你的扩展交互。你还可以[浏览 VS Code 中的全部 API](https://code.visualstudio.com/api/references/vscode-api)，探索构建自定义 AI 编辑器体验的新方式。
>
> 你可以在 [vscode-extensions-sample 仓库](https://github.com/microsoft/vscode-extension-samples/tree/main/lm-api-tutorial)中找到本教程的完整源代码。

---

<a id="related-content"></a>
## 相关内容（Related content）

> - [语言模型 API 扩展指南](./language-model.md)
> - [教程：使用聊天 API 创建一个代码导师聊天参与者](./chat-tutorial.md)
> - [VS Code 聊天 API 参考](./chat.md)

---

## 本篇小结

```text
命令：registerTextEditorCommand（直接拿到当前编辑器）

1. 获取代码：editor.visibleRanges → 逐行加上行号（让模型能准确指出行号）
2. 提示词：角色 + 任务 + 范围 + 语气 + 严格的输出格式（JSON）+ 示例（multi-shot）
   selectChatModels → 检查是否可用 → sendRequest
3. 解析：for await 累加片段，遇到 } 尝试 JSON.parse，成功就立即显示（流式效果）
4. 显示：createTextEditorDecorationType（样式）+ setDecorations（位置 + hoverMessage）
   行号要减 1；同一样式 setDecorations 是“替换”，传 [] 清除；
   每条文字不同时用 renderOptions，只需一个样式
5. 按钮：命令加 icon（$(comment)），menus.editor/title + group: navigation
```
