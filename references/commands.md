# 内置命令（Built-in Commands）

> 原文：[Built-in Commands](https://code.visualstudio.com/api/references/commands)
> 源文件：`microsoft/vscode-docs` → `api/references/commands.md`（DateApproved: 10/7/2026）

> 本文档列出了 Visual Studio Code 命令的一个子集，你可能会在 `vscode.commands.executeCommand` API 中使用它们。
>
> 关于如何使用命令 API，请阅读[命令指南](../extension-guides/command.md)。
>
> 下面是一个在 VS Code 中打开新文件夹的示例：

```javascript
let uri = Uri.file('/some/path/to/folder');
let success = await commands.executeCommand('vscode.openFolder', uri);
```

> **注意**：你可以通过键盘快捷方式编辑器（**File** > **Preferences** > **Keyboard Shortcuts**，即“文件 > 首选项 > 键盘快捷方式”）查看完整的 VS Code 命令集。键盘快捷方式编辑器列出了 VS Code 内置的或由扩展贡献的所有命令，以及它们的快捷键和可见性 when 子句。

**本篇的用法：** 这是一份**查阅用**的参考，不需要通读。最常用的是两类命令：

| 类别 | 例子 | 用途 |
|---|---|---|
| `vscode.executeXxxProvider` | `vscode.executeCompletionItemProvider`、`vscode.executeDefinitionProvider` | **调用**其他扩展（包括内置语言扩展）注册的语言功能提供者，拿到结果。常用于测试（见 [测试扩展](../working-with-extensions/testing-extension.md)、[语言服务器扩展指南](../language-extensions/language-server-extension-guide.md#testing-the-language-server)）和组合功能（见 [嵌入式语言](../language-extensions/embedded-languages.md#request-forwarding) 中的请求转发） |
| 编辑器 / 工作台操作 | `vscode.open`、`vscode.diff`、`vscode.openFolder`、`setContext` | 执行 VS Code API 中没有直接对应函数的操作 |

调用方式都是 `await vscode.commands.executeCommand<返回类型>('命令 ID', 参数1, 参数2, ...)`，参数按下面列出的顺序传入。

**阅读格式：** 每个命令下的列表中，*斜体*的是参数名（按顺序），*(returns)* 是返回值；“no result” 表示没有返回值。

---

<a id="commands"></a>
## 命令（Commands）

### 笔记本序列化

`vscode.executeDataToNotebook` - 调用笔记本序列化器

* *notebookType* - 一个笔记本类型
* *data* - 要转换为数据的字节
* *(returns)* - 笔记本数据（NotebookData）

`vscode.executeNotebookToData` - 调用笔记本序列化器

* *notebookType* - 一个笔记本类型
* *NotebookData* - 要转换为字节的笔记本数据
* *(returns)* - 字节

（这两个命令分别调用某个笔记本类型的 `NotebookSerializer` 的 `deserializeNotebook` 和 `serializeNotebook`，可用于测试你的序列化器，见 [笔记本](../extension-guides/notebook.md)。）

`notebook.selectKernel` - 为指定的笔记本编辑器小部件触发内核选择器

* *options* - 选择内核的选项
* *(returns)* - 无结果

`interactive.open` - 打开交互式窗口，返回笔记本编辑器和输入的 URI

* *showOptions* - 显示选项
* *resource* - 交互式资源的 Uri
* *controllerId* - 笔记本控制器 ID
* *title* - 交互式编辑器的标题
* *(returns)* - 笔记本和输入的 URI

`vscode.editorChat.start` - 发起一个新的编辑器内聊天会话

* *Run arguments* -（运行参数，原文无说明）
* *(returns)* - 无结果

（原文的列表没有分组，这里为了便于查阅加了分组小标题，命令的顺序与原文一致。）

### 语言功能：导航与信息

`vscode.executeDocumentHighlights` - 执行文档高亮提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *(returns)* - 一个 Promise，解析为 DocumentHighlight 实例的数组。

`vscode.executeDocumentSymbolProvider` - 执行文档符号提供者。

* *uri* - 文本文档的 Uri
* *(returns)* - 一个 Promise，解析为 SymbolInformation 和 DocumentSymbol 实例的数组。

`vscode.executeFormatDocumentProvider` - 执行文档格式化提供者。

* *uri* - 文本文档的 Uri
* *options* - 格式化选项
* *(returns)* - 一个 Promise，解析为 TextEdit 的数组。

`vscode.executeFormatRangeProvider` - 执行范围格式化提供者。

* *uri* - 文本文档的 Uri
* *range* - 文本文档中的一个范围
* *options* - 格式化选项
* *(returns)* - 一个 Promise，解析为 TextEdit 的数组。

`vscode.executeFormatOnTypeProvider` - 执行输入时格式化提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *ch* - 触发字符
* *options* - 格式化选项
* *(returns)* - 一个 Promise，解析为 TextEdit 的数组。

`vscode.executeDefinitionProvider` - 执行所有的定义提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *(returns)* - 一个 Promise，解析为 Location 或 LocationLink 实例的数组。

`vscode.executeTypeDefinitionProvider` - 执行所有的类型定义提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *(returns)* - 一个 Promise，解析为 Location 或 LocationLink 实例的数组。

`vscode.executeDeclarationProvider` - 执行所有的声明提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *(returns)* - 一个 Promise，解析为 Location 或 LocationLink 实例的数组。

`vscode.executeImplementationProvider` - 执行所有的实现提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *(returns)* - 一个 Promise，解析为 Location 或 LocationLink 实例的数组。

`vscode.executeReferenceProvider` - 执行所有的引用提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *(returns)* - 一个 Promise，解析为 Location 实例的数组。

`vscode.executeHoverProvider` - 执行所有的悬停提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *(returns)* - 一个 Promise，解析为 Hover 实例的数组。

`vscode.executeSelectionRangeProvider` - 执行选择范围提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *(returns)* - 一个 Promise，解析为范围的数组。

`vscode.executeWorkspaceSymbolProvider` - 执行所有的工作区符号提供者。

* *query* - 搜索字符串
* *(returns)* - 一个 Promise，解析为 SymbolInformation 实例的数组。

**使用示例**（获取光标处符号的定义）：

```ts
const editor = vscode.window.activeTextEditor!;
const locations = await vscode.commands.executeCommand<(vscode.Location | vscode.LocationLink)[]>(
  'vscode.executeDefinitionProvider',
  editor.document.uri,          // uri
  editor.selection.active       // position
);
```

注意 “Execute **all** ... providers” 的含义：如果有多个扩展为这种语言注册了提供者，结果会被合并在一起返回。

### 调用层次

`vscode.prepareCallHierarchy` - 在文档内的一个位置准备调用层次

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *(returns)* - 一个 Promise，解析为 CallHierarchyItem 实例的数组

`vscode.provideIncomingCalls` - 计算一个项的传入调用

* *item* - 一个调用层次项
* *(returns)* - 一个 Promise，解析为 CallHierarchyIncomingCall 实例的数组

`vscode.provideOutgoingCalls` - 计算一个项的传出调用

* *item* - 一个调用层次项
* *(returns)* - 一个 Promise，解析为 CallHierarchyOutgoingCall 实例的数组

（“传入调用”是谁调用了这个函数，“传出调用”是这个函数调用了谁。先用 `prepareCallHierarchy` 拿到项，再把项传给后两个命令。）

### 重命名与链接

`vscode.prepareRename` - 执行重命名提供者的 prepareRename。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *(returns)* - 一个 Promise，解析为一个范围和占位文字。

`vscode.executeDocumentRenameProvider` - 执行重命名提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *newName* - 新的符号名称
* *(returns)* - 一个 Promise，解析为一个 WorkspaceEdit。

`vscode.executeLinkProvider` - 执行文档链接提供者。

* *uri* - 文本文档的 Uri
* *linkResolveCount* -（可选）应该被解析的链接数量，只在链接未解析时有效。
* *(returns)* - 一个 Promise，解析为 DocumentLink 实例的数组。

（`executeDocumentRenameProvider` 只返回编辑，不会应用它。要真正执行重命名，再调用 `vscode.workspace.applyEdit(edit)`。）

### 语义标记

`vscode.provideDocumentSemanticTokensLegend` - 为一个文档提供语义标记图例

* *uri* - 文本文档的 Uri
* *(returns)* - 一个 Promise，解析为 SemanticTokensLegend。

`vscode.provideDocumentSemanticTokens` - 为一个文档提供语义标记

* *uri* - 文本文档的 Uri
* *(returns)* - 一个 Promise，解析为 SemanticTokens。

`vscode.provideDocumentRangeSemanticTokensLegend` - 为一个文档范围提供语义标记图例

* *uri* - 文本文档的 Uri
* *range* -（可选）文本文档中的一个范围
* *(returns)* - 一个 Promise，解析为 SemanticTokensLegend。

`vscode.provideDocumentRangeSemanticTokens` - 为一个文档范围提供语义标记

* *uri* - 文本文档的 Uri
* *range* - 文本文档中的一个范围
* *(returns)* - 一个 Promise，解析为 SemanticTokens。

（返回的 `SemanticTokens.data` 是编码后的整数数组，需要配合图例解码，见 [语义高亮指南](../language-extensions/semantic-highlight-guide.md)。）

### 语言功能：编辑辅助

`vscode.executeCompletionItemProvider` - 执行补全项提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *triggerCharacter* -（可选）当用户输入这个字符时触发补全，例如 `,` 或 `(`
* *itemResolveCount* -（可选）要解析的补全项的数量（数字太大会拖慢补全）
* *(returns)* - 一个 Promise，解析为一个 CompletionList 实例。

`vscode.executeSignatureHelpProvider` - 执行签名帮助提供者。

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *triggerCharacter* -（可选）当用户输入这个字符时触发签名帮助，例如 `,` 或 `(`
* *(returns)* - 一个 Promise，解析为 SignatureHelp。

`vscode.executeCodeLensProvider` - 执行 CodeLens 提供者。

* *uri* - 文本文档的 Uri
* *itemResolveCount* -（可选）应该被解析并返回的 CodeLens 的数量。只会返回已解析的 CodeLens，会影响性能
* *(returns)* - 一个 Promise，解析为 CodeLens 实例的数组。

`vscode.executeCodeActionProvider` - 执行代码操作提供者。

* *uri* - 文本文档的 Uri
* *rangeOrSelection* - 文本文档中的范围。有些重构提供者需要 Selection 对象。
* *kind* -（可选）要返回其代码操作的代码操作种类
* *itemResolveCount* -（可选）要解析的代码操作的数量（数字太大会拖慢代码操作）
* *(returns)* - 一个 Promise，解析为 Command 实例的数组。

（实际返回的数组中可能同时有 `Command` 和 `CodeAction`，因为代码操作提供者两者都可以返回。）

`vscode.executeDocumentColorProvider` - 执行文档颜色提供者。

* *uri* - 文本文档的 Uri
* *(returns)* - 一个 Promise，解析为 ColorInformation 对象的数组。

`vscode.executeColorPresentationProvider` - 执行颜色表示提供者。

* *color* - 要显示和插入的颜色
* *context* - 包含 uri 和 range 的上下文对象
* *(returns)* - 一个 Promise，解析为 ColorPresentation 对象的数组。

`vscode.executeInlayHintProvider` - 执行内嵌提示提供者

* *uri* - 文本文档的 Uri
* *range* - 文本文档中的一个范围
* *(returns)* - 一个 Promise，解析为 Inlay 对象的数组

`vscode.executeFoldingRangeProvider` - 执行折叠范围提供者

* *uri* - 文本文档的 Uri
* *(returns)* - 一个 Promise，解析为 FoldingRange 对象的数组

`vscode.resolveNotebookContentProviders` - 解析笔记本内容提供者

* *(returns)* - 一个 Promise，解析为 NotebookContentProvider 静态信息对象的数组。

（`NotebookContentProvider` 是早期的笔记本 API，已被 `NotebookSerializer` 取代，这个命令可以忽略。）

`vscode.executeInlineValueProvider` - 执行内联值提供者

* *uri* - 文本文档的 Uri
* *range* - 文本文档中的一个范围
* *context* - 一个 InlineValueContext
* *(returns)* - 一个 Promise，解析为 InlineValue 对象的数组

（“内联值”是调试时在代码行尾显示的变量值。“内嵌提示”（Inlay Hints）是在代码中显示的参数名、类型等灰色小字。）

### 打开与比较

`vscode.open` - 在编辑器中打开给定的资源。可以是文本文件或二进制文件，也可以是一个 http(s) URL。如果你需要对打开文本文件的选项有更多的控制，请改用 `vscode.window.showTextDocument`。

* *uri* - 文本文件或二进制文件的 Uri，或一个 http(s) URL
* *columnOrOptions* -（可选）要在其中打开的列，或者编辑器选项，参见 `vscode.TextDocumentShowOptions`
* *label* - 编辑器标签（可选）
* *(returns)* - 无结果

`vscode.openWith` - 用一个特定的编辑器打开给定的资源。

* *resource* - 要打开的资源
* *viewId* - 自定义编辑器的视图 ID，或者 'default' 表示使用 VS Code 的默认编辑器
* *columnOrOptions* -（可选）要在其中打开的列，或者编辑器选项，参见 vscode.TextDocumentShowOptions
* *(returns)* - 无结果

`vscode.diff` - 在差异编辑器中打开给定的资源，比较它们的内容。

* *left* - 差异编辑器左侧的资源
* *right* - 差异编辑器右侧的资源
* *title* - 差异编辑器的人类可读标题
* *options* -（可选）要在其中打开的列，或者编辑器选项（参见 vscode.TextDocumentShowOptions）

`vscode.changes` - 在变更编辑器中打开一组资源，比较它们的内容。

* *title* - 变更编辑器的人类可读标题
* *resourceList* - 要比较的资源列表

**使用示例：**

```ts
// 用浏览器打开网址
await vscode.commands.executeCommand('vscode.open', vscode.Uri.parse('https://code.visualstudio.com'));

// 比较两个文件（右侧可以是虚拟文档，见“虚拟文档”一篇）
await vscode.commands.executeCommand('vscode.diff', leftUri, rightUri, '旧版本 ↔ 新版本');

// 用自定义编辑器打开（viewId 为 customEditors 贡献点中的 viewType）
await vscode.commands.executeCommand('vscode.openWith', uri, 'catCustoms.pawDraw');
```

`vscode.changes` 的 `resourceList` 中每一项是一个三元组 `[资源标识 Uri, 原始版本 Uri, 修改后版本 Uri]`，它会打开一个包含多个文件差异的“多文件差异编辑器”。

### 类型层次与测试

`vscode.prepareTypeHierarchy` - 在文档内的一个位置准备类型层次

* *uri* - 文本文档的 Uri
* *position* - 文本文档中的一个位置
* *(returns)* - 一个 Promise，解析为 TypeHierarchyItem 实例的数组

`vscode.provideSupertypes` - 计算一个项的父类型

* *item* - 一个类型层次项
* *(returns)* - 一个 Promise，解析为 TypeHierarchyItem 实例的数组

`vscode.provideSubtypes` - 计算一个项的子类型

* *item* - 一个类型层次项
* *(returns)* - 一个 Promise，解析为 TypeHierarchyItem 实例的数组

`vscode.revealTestInExplorer` - 在资源管理器中显示一个测试实例

* *testItem* - 一个 VS Code 的 TestItem。
* *(returns)* - 无结果

（“资源管理器”在这里指测试资源管理器，见 [测试 API](../extension-guides/testing.md)。）

### 上下文

`setContext` - 设置一个可以在 when 子句中使用的自定义上下文键的值。

* *name* - 上下文键的名称
* *value* - 上下文键的值
* *(returns)* - 无结果

**这是扩展开发中最常用的命令之一**，用于控制菜单、视图、快捷键的显示条件：

```ts
await vscode.commands.executeCommand('setContext', 'myExtension.isLoggedIn', true);
```

```json
"menus": {
  "view/title": [{ "command": "myExtension.logout", "when": "myExtension.isLoggedIn" }]
}
```

详见 [when 子句上下文](./when-clause-contexts.md#add-a-custom-when-clause-context)。

### 光标与滚动

`cursorMove` - 把光标移动到视图中的一个逻辑位置

* *Cursor move argument object*（光标移动参数对象） - 可以通过这个参数传递的属性-值对：
  * 'to'：必填的逻辑位置值，指出把光标移动到哪里。

    ```text
    'left', 'right', 'up', 'down', 'prevBlankLine', 'nextBlankLine',
    'wrappedLineStart', 'wrappedLineEnd', 'wrappedLineColumnCenter'
    'wrappedLineFirstNonWhitespaceCharacter', 'wrappedLineLastNonWhitespaceCharacter'
    'viewPortTop', 'viewPortCenter', 'viewPortBottom', 'viewPortIfOutside'
    ```

  * 'by'：移动的单位。默认值根据 'to' 的值计算。

    ```text
    'line', 'wrappedLine', 'character', 'halfLine'
    ```

  * 'value'：移动的单位数。默认为 '1'。
  * 'select'：如果为 'true'，则进行选择。默认为 'false'。

| `to` 的值 | 含义 |
|---|---|
| `left` / `right` / `up` / `down` | 左 / 右 / 上 / 下 |
| `prevBlankLine` / `nextBlankLine` | 上一个 / 下一个空行 |
| `wrappedLineStart` / `wrappedLineEnd` / `wrappedLineColumnCenter` | 当前（自动换行后的）视觉行的开头 / 结尾 / 中间 |
| `wrappedLineFirstNonWhitespaceCharacter` / `wrappedLineLastNonWhitespaceCharacter` | 视觉行中第一个 / 最后一个非空白字符 |
| `viewPortTop` / `viewPortCenter` / `viewPortBottom` | 可见区域的顶部 / 中间 / 底部 |
| `viewPortIfOutside` | 如果光标在可见区域之外，就移到可见区域内 |

```ts
// 向下移动 3 行并选中
await vscode.commands.executeCommand('cursorMove', { to: 'down', by: 'line', value: 3, select: true });
```

`editorScroll` - 沿给定的方向滚动编辑器

* *Editor scroll argument object*（编辑器滚动参数对象） - 可以通过这个参数传递的属性-值对：
  * 'to'：必填的方向值。

    ```text
    'up', 'down'
    ```

  * 'by'：移动的单位。默认值根据 'to' 的值计算。

    ```text
    'line', 'wrappedLine', 'page', 'halfPage', 'editor'
    ```

  * 'value'：移动的单位数。默认为 '1'。
  * 'revealCursor'：如果为 'true'，当光标在可见区域之外时显示光标。

`revealLine` - 在给定的逻辑位置显示给定的行

* *Reveal line argument object*（显示行参数对象） - 可以通过这个参数传递的属性-值对：
  * 'lineNumber'：必填的行号值。
  * 'at'：显示这一行的逻辑位置。

    ```text
    'top', 'center', 'bottom'
    ```

（`revealLine` 只滚动，不移动光标。如果要同时移动光标，用 `TextEditor.selection` 加 `TextEditor.revealRange` 更直接。）

### 折叠

`editor.unfold` - 展开编辑器中的内容

* *Unfold editor argument*（展开编辑器参数） - 可以通过这个参数传递的属性-值对：
  * 'levels'：要展开的层级数。如果没有设置，默认为 1。
  * 'direction'：如果为 'up'，向上展开给定的层级数，否则向下展开。
  * 'selectionLines'：要应用展开操作的编辑器选择的起始行（从 0 开始）的数组。如果没有设置，将使用活动的选择。

`editor.fold` - 折叠编辑器中的内容

* *Fold editor argument*（折叠编辑器参数） - 可以通过这个参数传递的属性-值对：
  * 'levels'：要折叠的层级数。
  * 'direction'：如果为 'up'，向上折叠给定的层级数，否则向下折叠。
  * 'selectionLines'：要应用折叠操作的编辑器选择的起始行（从 0 开始）的数组。如果没有设置，将使用活动的选择。
  如果没有设置 levels 或 direction，就折叠这些位置上的区域；如果已经折叠了，就折叠第一个未折叠的父区域。

`editor.toggleFold` - 根据当前的状态，折叠或展开编辑器中的内容

### 查找与跳转

`editor.actions.findWithArgs` - 用特定的选项打开一个新的编辑器内查找小部件。

* searchString - 预填到查找输入框的字符串
* replaceString - 预填到替换输入框的字符串
* isRegex - 启用正则表达式
* preserveCase - 替换时尽量保持相同的大小写
* findInSelection - 把查找范围限制在当前选择内
* matchWholeWord（全字匹配）
* isCaseSensitive（区分大小写）

`editor.action.goToLocations` - 从文件中的一个位置跳转到一组位置

* *uri* - 起始的文本文档
* *position* - 起始的位置
* *locations* - 一个位置的数组。
* *multiple* - 定义有多个结果时怎么做，可以是 `peek`、`gotoAndPeek` 或 `goto`
* *noResultsMessage* - 当 locations 为空时显示的人类可读消息。

`editor.action.peekLocations` - 从文件中的一个位置速览一组位置

* *uri* - 起始的文本文档
* *position* - 起始的位置
* *locations* - 一个位置的数组。
* *multiple* - 定义有多个结果时怎么做，可以是 `peek`、`gotoAndPeek` 或 `goto`

（原文中这两处的 `goto` 少了结尾的反引号。`goToLocations` / `peekLocations` 常用在 CodeLens 的命令中，例如点击“3 个引用”后，用速览窗口显示这些引用的位置。）

`workbench.action.quickOpen` - 快速访问

* *prefix* -（前缀，原文无说明）

（`prefix` 是预填到快速打开框中的文字，例如传 `'>'` 打开命令面板、传 `'@'` 跳转到符号、传 `':'` 跳转到行。）

### 笔记本操作

`notebook.cell.toggleOutputs` - 切换输出

* *options* - 单元格范围选项

`notebook.fold` - 折叠单元格

* *index* - 单元格的索引

`notebook.unfold` - 展开单元格

* *index* - 单元格的索引

`notebook.selectKernel` - 笔记本内核参数

* *kernelInfo* - 内核信息

（`notebook.selectKernel` 在原文中出现了两次，参数说明不同，这是同一个命令的两种参数形式。）

`notebook.cell.changeLanguage` - 更改单元格的语言

* *range* - 单元格范围
* *language* - 目标单元格语言

`notebook.execute` - 全部运行

* *uri* - 文档的 uri

`notebook.cell.execute` - 执行单元格

* *options* - 单元格范围选项

`notebook.cell.executeAndFocusContainer` - 执行单元格并聚焦容器

* *options* - 单元格范围选项

`notebook.cell.cancelExecution` - 停止单元格的执行

* *options* - 单元格范围选项

### 搜索与交互式窗口

`workbench.action.findInFiles` - 打开一次工作区搜索

* *A set of options for the search*（一组搜索选项） -

（选项对象中常用的属性有 `query`（搜索文字）、`replace`、`isRegex`、`isCaseSensitive`、`matchWholeWord`、`filesToInclude`、`filesToExclude`、`triggerSearch`（是否立即开始搜索）。）

`_interactive.open` - 打开交互式窗口

* *showOptions* - 显示选项
* *resource* - 交互式资源的 Uri
* *controllerId* - 笔记本控制器 ID
* *title* - 笔记本编辑器的标题

（以 `_` 开头的命令通常是内部命令，优先使用上面的 `interactive.open`。）

`interactive.execute` - 执行输入框中的内容

* *resource* - 交互式资源的 Uri

`search.action.openNewEditor` - 打开一个新的搜索编辑器。传入的参数可以包含 ${relativeFileDirname} 这样的变量。

* *Open new Search Editor args*（打开新搜索编辑器的参数） -

`search.action.openEditor` - 打开一个新的搜索编辑器。传入的参数可以包含 ${relativeFileDirname} 这样的变量。

* *Open new Search Editor args*（打开新搜索编辑器的参数） -

`search.action.openNewEditorToSide` - 打开一个新的搜索编辑器。传入的参数可以包含 ${relativeFileDirname} 这样的变量。

* *Open new Search Editor args*（打开新搜索编辑器的参数） -

（“搜索编辑器”是把搜索结果显示在一个编辑器标签页中，而不是侧边栏。`openNewEditorToSide` 会在侧边的编辑器组中打开。）

### 窗口与文件夹

`vscode.openFolder` - 根据 newWindow 参数，在当前窗口或新窗口中打开一个文件夹或工作区。注意，在同一个窗口中打开会关闭当前的扩展宿主进程，并在给定的文件夹 / 工作区上启动一个新的扩展宿主进程，除非 newWindow 参数被设为 true。

* *uri* -（可选）要打开的文件夹或工作区文件的 Uri。如果没有提供，会弹出一个原生对话框让用户选择文件夹
* *options* -（可选）选项。具有以下属性的对象：`forceNewWindow`：是否在新窗口中打开文件夹 / 工作区，默认在同一窗口中打开。`forceReuseWindow`：是否强制在同一个窗口中打开文件夹 / 工作区，默认为 false。`noRecentEntry`：打开的 URI 是否不出现在 “Open Recent”（打开最近的文件）列表中，默认为 false。注意，为了向后兼容，options 也可以是 boolean 类型，表示 `forceNewWindow` 设置。

**特别注意：** 在当前窗口中打开文件夹，会**关闭你的扩展**（扩展宿主被重启），`executeCommand` 之后的代码可能根本不会执行。所以调用它之前，要先保存好需要的状态（例如用 `context.globalState`）。

`vscode.newWindow` - 根据 newWindow 参数打开一个新窗口。

* *options* -（可选）选项。具有以下属性的对象：`reuseWindow`：是否在同一个窗口中打开（而不是新窗口），默认在新窗口中打开。

`vscode.removeFromRecentlyOpened` - 从最近打开的列表中删除具有给定路径的条目。

* *path* - 要从最近打开的列表中删除的 URI 或 URI 字符串。

### 编辑器布局

`moveActiveEditor` - 按标签页或编辑器组移动活动编辑器

* *Active editor move argument*（活动编辑器移动参数） - 参数的属性：
  * 'to'：字符串值，指出移动到哪里。
  * 'by'：字符串值，指出移动的单位（按标签页还是按编辑器组）。
  * 'value'：数字值，指出移动几个位置，或者一个要移动到的绝对位置。

（`to` 的取值有 `left`、`right`、`first`、`last`、`center`、`position` 等，`by` 的取值为 `tab` 或 `group`。例如 `{ to: 'right', by: 'group' }` 把当前编辑器移到右边的编辑器组。）

`copyActiveEditor` - 按编辑器组复制活动编辑器

* *Active editor copy argument*（活动编辑器复制参数） - 参数的属性：
  * 'to'：字符串值，指出复制到哪里。
  * 'value'：数字值，指出复制几个位置，或者一个要复制到的绝对位置。

`vscode.getEditorLayout` - 获取编辑器布局

* *(returns)* - 一个编辑器布局对象，与 vscode.setEditorLayout 的格式相同

（对应的 `vscode.setEditorLayout` 命令可以设置编辑器的分栏布局，例如 `{ orientation: 0, groups: [{}, {}] }` 表示左右两栏。）

`workbench.action.files.newUntitledFile` - 新建无标题的文本文件

* *New Untitled Text File arguments*（新建无标题文本文件的参数） - 编辑器视图类型或语言 ID（如果已知）

（参数形如 `{ languageId: 'markdown' }`。也可以用 API `vscode.workspace.openTextDocument({ language: 'markdown', content: '...' })` 达到类似的效果。）

### 扩展管理

`workbench.extensions.installExtension` - 安装给定的扩展

* *extensionIdOrVSIXUri* - 扩展 ID 或 VSIX 资源的 uri
* *options* -（可选）安装扩展的选项。具有以下属性的对象：`installOnlyNewlyAddedFromExtensionPackVSIX`：启用后，VS Code 只安装扩展包 VSIX 中新添加的扩展。只有在安装 VSIX 时才会考虑这个选项。

`workbench.extensions.uninstallExtension` - 卸载给定的扩展

* *Id of the extension to uninstall*（要卸载的扩展的 ID） -

`workbench.extensions.search` - 搜索一个特定的扩展

* *Query to use in search*（搜索使用的查询） -

（`workbench.extensions.search` 会打开扩展视图并填入搜索文字，例如 `'@category:themes'`，可用于在欢迎页或演练中引导用户查找扩展。）

### 任务、问题报告与其他

`workbench.action.tasks.runTask` - 运行任务

* *args* - 过滤快速选择中显示的任务

（参数可以是任务的标签字符串，或者 `{ type: 'npm', task: 'build' }` 这样的对象，用于直接运行某个任务。）

`workbench.action.openIssueReporter` - 打开问题报告器，并可选地预填一部分表单。

* *options* - 用于预填问题报告器的数据。

`vscode.openIssueReporter` - 打开问题报告器，并可选地预填一部分表单。

* *options* - 用于预填问题报告器的数据。

（常用的预填选项是 `{ extensionId: '发布者.扩展名', issueTitle, issueBody }`，可以让用户直接为你的扩展报告问题。）

`workbench.action.openLogFile` - workbench.action.openLogFile（打开日志文件）

* *logFile* -（日志文件，原文无说明）

`workbench.action.openWalkthrough` - 打开演练。

* *walkthroughID* - 要打开的演练的 ID。
* *toSide* - 在侧边的新编辑器组中打开演练。

（`walkthroughID` 的格式是 `发布者.扩展名#演练ID`，见 [UX 指南：演练](../ux-guidelines/walkthroughs.md)。）

---

<a id="simple-commands"></a>
## 简单命令（Simple commands）

> 不需要参数的简单命令，可以在默认的 `keybindings.json` 文件的键盘快捷方式列表中找到。未绑定快捷键的命令列在文件底部的一个注释块中。
>
> 要查看默认的 `keybindings.json`，从命令面板（`Ctrl+Shift+P`）中运行 **Preferences: Open Default Keyboard Shortcuts (JSON)**。

（macOS 上的命令面板快捷键是 `Cmd+Shift+P`。）

**怎样找到某个操作的命令 ID：** 在键盘快捷方式编辑器（`Ctrl+K Ctrl+S`）中搜索这个操作的名称，右键点击它，选择 **Copy Command ID**（复制命令 ID）。这些命令大多数都可以直接用 `executeCommand` 调用，例如 `workbench.action.files.save`（保存）、`editor.action.formatDocument`（格式化文档）、`workbench.action.reloadWindow`（重新加载窗口）。

---

## 本篇小结

```text
调用：await vscode.commands.executeCommand<T>('命令 ID', ...参数)

最常用
  vscode.executeXxxProvider        调用已注册的语言功能，拿到结果（测试、组合功能）
  setContext                       设置自定义 when 子句上下文键
  vscode.open / openWith / diff    打开资源、用指定编辑器打开、比较差异
  vscode.openFolder                打开文件夹（在当前窗口打开会重启扩展宿主！）
  cursorMove / editorScroll / revealLine / editor.fold / unfold  编辑器操作
  editor.action.goToLocations / peekLocations                  跳转 / 速览一组位置
  workbench.action.findInFiles / quickOpen / tasks.runTask / openWalkthrough

查找更多：键盘快捷方式编辑器 → 右键 → Copy Command ID；或默认的 keybindings.json
```
