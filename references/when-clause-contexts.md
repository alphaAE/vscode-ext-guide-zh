# when 子句上下文（when clause contexts）

> 原文：[when clause contexts](https://code.visualstudio.com/api/references/when-clause-contexts)
> 源文件：`microsoft/vscode-docs` → `api/references/when-clause-contexts.md`（DateApproved: 10/7/2026）

> Visual Studio Code 会根据 VS Code UI 中哪些元素可见、哪些元素处于活动状态，设置各种上下文键（context key）及其具体的值。这些上下文可以用来有选择地启用或禁用扩展的命令和 UI 元素，例如菜单和视图。
>
> 例如，VS Code 使用 when 子句来启用或禁用命令的快捷键，你可以在默认快捷键 JSON 中看到（**Preferences: Open Default Keyboard Shortcuts (JSON)**）：

```json
{ "key": "f5",  "command": "workbench.action.debug.start",
                   "when": "debuggersAvailable && !inDebugMode" },
```

> 上面，内置的 **Start Debugging**（开始调试）命令的快捷键是 `F5`，它只在有合适的调试器可用（上下文键 `debuggersAvailable` 为 true）、并且编辑器不在调试模式（上下文键 `inDebugMode` 为 false）时才会启用。

**when 子句用在哪里：** 它是一个写在 `package.json` 中的字符串表达式，VS Code 会根据当前的上下文实时计算它的真假。

| 位置 | 作用 |
|---|---|
| `contributes.keybindings[].when` | 快捷键何时生效 |
| `contributes.menus.<菜单>[].when` | 菜单项何时显示（见 [贡献点](./contribution-points.md#contributes.menus)） |
| `contributes.commands[].enablement` | 命令何时可用（不满足时显示为灰色） |
| `contributes.views.<容器>[].when` | 视图何时显示 |
| `contributes.viewsWelcome[].when` | 视图欢迎内容何时显示 |
| `contributes.walkthroughs` 的步骤 `when` | 演练步骤何时显示 |

所有可以写 when 子句的地方，使用的都是同一套语法和上下文键。

---

<a id="conditional-operators"></a>
## 条件运算符（Conditional operators）

> 一个 when 子句可以由一个上下文键组成（例如 `inDebugMode`），也可以使用各种运算符来表达更细致的编辑器状态。

<a id="logical-operators"></a>
### 逻辑运算符（Logical operators）

> 逻辑运算符可以组合简单的上下文键，或者包含其他逻辑、相等、比较、匹配、`in` / `not in` 运算符或括号表达式的 when 子句表达式。

| 运算符 | 符号 | 示例 |
| --- | --- | --- |
| 非（Not） | `!` | `"!editorReadonly"` 或 `"!(editorReadonly \|\| inDebugMode)"` |
| 与（And） | `&&` | `"textInputFocus && !editorReadonly"` |
| 或（Or） | `\|\|` | `"isLinux \|\| isWindows"` |

> 关于逻辑运算符优先级的说明：上表按优先级从高到低列出运算符。示例：

| 写成 | 解释为 |
| --- | --- |
| `!foo && bar` | `(!foo) && bar` |
| `!foo \|\| bar` | `(!foo) \|\| bar` |
| `foo \|\| bar && baz` | `foo \|\| (bar && baz)` |
| `!foo && bar \|\| baz` | `(!foo && bar) \|\| baz` |
| `!(foo \|\| bar) && baz` | （保持不变）`!(foo \|\| bar) && baz` |

优先级与 JavaScript 相同：`!` 最高，`&&` 其次，`||` 最低。拿不准时加括号。

<a id="equality-operators"></a>
### 相等运算符（Equality operators）

> 你可以检查一个上下文键的值是否等于一个指定的值。注意，右侧是一个值，而不会被解释为一个上下文键，也就是说它不会在上下文中查找。

| 运算符 | 符号 | 示例 |
| --- | --- | --- |
| 相等 | `==` | `"editorLangId == typescript"` 或 `"editorLangId == 'typescript'"` |
| 不相等 | `!=` | `"resourceExtname != .js"` 或 `"resourceExtname != '.js'"` |

> 注意：
>
> - 如果右侧的值是一个包含空白的字符串，它必须用单引号括起来：`"resourceFilename == 'My New File.md'"`。
> - `===` 的行为与 `==` 相同，`!==` 的行为与 `!=` 相同。

“右侧不会被解释为上下文键”：`"editorLangId == typescript"` 中的 `typescript` 就是字符串 `'typescript'`，不会去查找一个叫 `typescript` 的上下文键。如果想比较两个上下文键，可以用下文的 `in` 运算符。

<a id="comparison-operators"></a>
### 比较运算符（Comparison operators）

> 你可以把一个上下文键的值与一个数字进行比较。注意，运算符的左右两侧必须用空白分隔，例如 `foo < 1`，而不是 `foo<1`。

| 运算符 | 符号 | 示例 |
| --- | --- | --- |
| 大于 | `>`、`>=` | `"gitOpenRepositoryCount >= 1"`，而不是 `"gitOpenRepositoryCount>=1"` |
| 小于 | `<`、`<=` | `"workspaceFolderCount < 2"`，而不是 `"workspaceFolderCount<2"` |

<a id="match-operator"></a>
### 匹配运算符（Match operator）

> （以前的名称：键值对匹配运算符）

| 运算符 | 符号 | 示例 |
| --- | --- | --- |
| 匹配 | `=~` | `"resourceScheme =~ /^untitled$\|^file$/"` |

> when 子句有一个匹配运算符（`=~`）。表达式 `key =~ regularExpressionLiteral` 把右侧当作一个正则表达式字面量，用它去匹配左侧。例如，要为所有 Docker 文件贡献上下文菜单项，可以这样写：

```json
   "when": "resourceFilename =~ /docker/"
```

> 注意：
>
> - `=~` 运算符的右侧遵循与 JavaScript 中的正则表达式字面量（[参考](https://developer.mozilla.org/docs/Web/JavaScript/Guide/Regular_Expressions#creating_a_regular_expression)）相同的规则，只是字符需要同时遵循 JSON 字符串和正则表达式两者的转义规则。例如，一个匹配子字符串 `file://` 的正则表达式字面量，在 JavaScript 中是 `/file:\/\//`，而在 when 子句中是 `/file:\\/\\//`，因为反斜杠在 JSON 字符串中需要转义，斜杠在正则表达式模式中需要转义。
> - 不存在 `!=~` 运算符，但你可以对匹配表达式取反：`!(foo =~ /baz/)`。

**双重转义的推导：**

```text
想匹配的文字：      file://
正则中 / 要转义：    /file:\/\//
JSON 中 \ 要转义：   "/file:\\/\\//"     ← 写进 package.json 的形式
```

（表格中的 `/^untitled$\|^file$/` 是 Markdown 表格的转义写法，实际的正则是 `/^untitled$|^file$/`。）

<a id="regular-expression-flags"></a>
#### 正则表达式标志（Regular expression flags）

> 可以在正则表达式字面量中使用标志。例如，`resourceFilename =~ /json/i` 或 `myContextKey =~ /baz/si`。
>
> 支持的标志：`i`、`s`、`m`、`u`。
>
> 会被忽略的标志：`g`、`y`。

| 标志 | 含义 |
|---|---|
| `i` | 忽略大小写 |
| `s` | `.` 也匹配换行符 |
| `m` | 多行模式（`^` `$` 匹配每一行的开头和结尾） |
| `u` | Unicode 模式 |

<a id="in-and-not-in-conditional-operators"></a>
### 'in' 和 'not in' 条件运算符（'in' and 'not in' conditional operators）

> when 子句的 `in` 运算符允许在另一个上下文键的值中，动态地查找一个上下文键的值。例如，如果你想为包含某种类型文件的文件夹（或者其他无法静态得知的东西）添加一个上下文菜单命令，现在就可以使用 `in` 运算符来实现。你可以使用 `not in` 运算符来检查相反的条件。

| 运算符 | 符号 | 示例 |
| --- | --- | --- |
| 在其中 | `in` | `"resourceFilename in supportedFolders"` |
| 不在其中 | `not in` | `"resourceFilename not in supportedFolders"` |

> 首先，确定哪些文件夹应该支持这个命令，把文件夹的名称添加到一个数组中。然后，使用 [`setContext` 命令](#add-a-custom-when-clause-context)把这个数组变成一个上下文键：

```ts
vscode.commands.executeCommand('setContext', 'ext.supportedFolders', [ 'test', 'foo', 'bar' ]);

// 或者

// 注意，在这种情况下（使用一个对象），值是什么并不重要，判断的依据是对象中是否存在这个键
// 值必须是简单类型
vscode.commands.executeCommand('setContext', 'ext.supportedFolders', { 'test': true, 'foo': 'anything', 'bar': false });
```

> 然后，在 `package.json` 中，你可以为 `explorer/context` 菜单添加一个菜单贡献：

```json
// 注意，这里假设你已经定义了一个名为 ext.doSpecial 的命令
"menus": {
  "explorer/context": [
    {
      "command": "ext.doSpecial",
      "when": "explorerResourceIsFolder && resourceFilename in ext.supportedFolders"
    }
  ]
}
```

> 在这个例子中，我们取 `resourceFilename` 的值（在这里是文件夹的名称），检查它是否存在于 `ext.supportedFolders` 的值中。如果存在，菜单就会显示出来。这个强大的运算符应该能为支持 `when` 子句的贡献（例如菜单、视图等）提供更丰富的条件和动态贡献。

**`in` 的典型用途：** 扩展在运行时扫描工作区，算出“哪些文件 / 文件夹需要显示某个菜单”，用 `setContext` 存成数组，菜单的 when 子句用 `resourcePath in ext.xxx` 判断。这样菜单就能根据运行时的数据动态显示，而不必在 `package.json` 中写死。（用对象的形式时，`'bar': false` 也算“存在”，因为判断的只是键是否存在。）

---

<a id="available-context-keys"></a>
## 可用的上下文键（Available context keys）

> 下面是一些可用的上下文键，它们的计算结果为布尔值 true / false。
>
> 这里的列表并不完整，你可以在键盘快捷方式编辑器（**Preferences: Open Keyboard Shortcuts**）中搜索和过滤，或者查看默认快捷键 JSON 文件（**Preferences: Open Default Keyboard Shortcuts (JSON)**），找到其他的 when 子句上下文。你也可以使用[检查上下文键工具](#inspect-context-keys-utility)找出你感兴趣的上下文键。

（虽然原文说“计算结果为布尔值”，但列表中有不少键的值是字符串或数字，例如 `editorLangId`、`resourceExtname`、`workspaceFolderCount`，要配合 `==`、`>=` 等运算符使用。）

| 上下文名称 | 何时为真 |
| --- | --- |
| **编辑器上下文（Editor contexts）** | |
| `editorFocus` | 一个编辑器拥有焦点，可以是文字部分或某个小部件。 |
| `editorTextFocus` | 编辑器中的文字拥有焦点（光标在闪烁）。 |
| `textInputFocus` | 任意编辑器拥有焦点（普通编辑器、调试 REPL 等）。 |
| `inputFocus` | 任意文本输入区域拥有焦点（编辑器或文本框）。 |
| `editorTabMovesFocus` | `Tab` 键是否会把焦点移出编辑器。 |
| `editorHasSelection` | 编辑器中有选中的文字。 |
| `editorHasMultipleSelections` | 选中了多个文字区域（多光标）。 |
| `editorReadonly` | 编辑器是只读的。 |
| `editorLangId` | 当编辑器关联的[语言 ID](https://code.visualstudio.com/docs/languages/identifiers)匹配时为真。<br>示例：`"editorLangId == typescript"`。 |
| `isInDiffEditor` | 活动编辑器是一个差异编辑器。 |
| `isInEmbeddedEditor` | 当焦点在一个嵌入式编辑器中时为真。 |
| **操作系统上下文（Operating system contexts）** | |
| `isLinux` | 操作系统是 Linux 时为真。 |
| `isMac` | 操作系统是 macOS 时为真。 |
| `isWindows` | 操作系统是 Windows 时为真。 |
| `isChromeOS` | 在 ChromeOS 上通过 Web 浏览器访问编辑器时为真。 |
| `isWeb` | 通过 Web 访问编辑器时为真。 |
| **列表上下文（List contexts）** | |
| `listFocus` | 一个列表拥有焦点。 |
| `listSupportsMultiselect` | 一个列表支持多选。 |
| `listHasSelectionOrFocus` | 一个列表有选中项或焦点。 |
| `listDoubleSelection` | 一个列表选中了 2 个元素。 |
| `listMultiSelection` | 一个列表选中了多个元素。 |
| **模式上下文（Mode contexts）** | |
| `inSnippetMode` | 编辑器处于代码片段模式。 |
| `inQuickOpen` | 快速打开下拉框拥有焦点。 |
| **资源上下文（Resource contexts）** | |
| `resourceScheme` | 当资源 Uri 的 scheme 匹配时为真。<br>示例：`"resourceScheme == file"` |
| `resourceFilename` | 当资源管理器或编辑器的文件名匹配时为真。<br>示例：`"resourceFilename == gulpfile.js"` |
| `resourceExtname` | 当资源管理器或编辑器的文件扩展名匹配时为真。<br>示例：`"resourceExtname == .js"` |
| `resourceDirname` | 当资源管理器或编辑器的资源所在文件夹的绝对路径匹配时为真。<br>示例：`"resourceDirname == /users/alice/project/src"` |
| `resourcePath` | 当资源管理器或编辑器的资源的绝对路径匹配时为真。<br>示例：`"resourcePath == /users/alice/project/gulpfile.js"` |
| `resourceLangId` | 当资源管理器或编辑器标题的[语言 ID](https://code.visualstudio.com/docs/languages/identifiers)匹配时为真。<br>示例：`"resourceLangId == markdown"` |
| `isFileSystemResource` | 当资源管理器或编辑器的文件是一个可以由文件系统提供者处理的文件系统资源时为真。 |
| `resourceSet` | 当设置了一个资源管理器或编辑器的文件时为真。 |
| `resource` | 资源管理器或编辑器的文件的完整 Uri。 |
| **资源管理器上下文（Explorer contexts）** | |
| `explorerViewletVisible` | 资源管理器视图可见时为真。 |
| `explorerViewletFocus` | 资源管理器视图拥有键盘焦点时为真。 |
| `filesExplorerFocus` | 文件资源管理器部分拥有键盘焦点时为真。 |
| `openEditorsFocus` | “打开的编辑器（OPEN EDITORS）”部分拥有键盘焦点时为真。 |
| `explorerResourceIsFolder` | 在资源管理器中选中了一个文件夹时为真。 |
| **源代码管理上下文（Source control contexts）** | |
| `scmProvider` | 当源代码管理提供者的 ID 匹配时为真。<br>示例：`"scmProvider == git"`。 |
| `scmResourceGroup` | 当源代码管理资源组的 ID 匹配时为真。<br>示例：`"scmResourceGroup == merge"`。 |
| `originalResourceScheme` | 当快速差异编辑器中原始资源的 scheme 匹配时为真。<br>示例：`"originalResourceScheme == git"`。 |
| **编辑器小部件上下文（Editor widget contexts）** | |
| `findWidgetVisible` | 编辑器的查找小部件可见。 |
| `suggestWidgetVisible` | 建议小部件（智能提示）可见。 |
| `suggestWidgetMultipleSuggestions` | 显示了多个建议。 |
| `hasOtherSuggestions` | 一个已接受的 Tab 补全还有其他可以循环切换的备选建议。 |
| `hasSnippetCompletions` | 当 `editor.tabCompletion` 设为 `onlySnippets` 时，有一个匹配的代码片段补全可用。 |
| `inlineSuggestionVisible` | 当一个内联建议（幽灵文字）可见时为真。 |
| `inlineSuggestionHasIndentation` | 当内联建议以空白缩进开头时为真。 |
| `renameInputVisible` | 重命名输入框可见。 |
| `referenceSearchVisible` | “速览引用（Peek References）”窗口打开着。 |
| `inReferenceSearchEditor` | “速览引用”窗口中的编辑器拥有焦点。 |
| `config.editor.stablePeek` | 保持速览编辑器打开（由 `editor.stablePeek` 设置控制）。 |
| `codeActionMenuVisible` | 代码操作菜单可见。 |
| `parameterHintsVisible` | 参数提示可见（由 `editor.parameterHints.enabled` 设置控制）。 |
| `parameterHintsMultipleSignatures` | 显示了多个参数提示。 |
| **调试器上下文（Debugger contexts）** | |
| `debuggersAvailable` | 有一个合适的调试器扩展可用。 |
| `inDebugMode` | 一个调试会话正在运行。 |
| `debugState` | 活动调试器的状态。<br>可能的值为 `inactive`、`initializing`、`stopped`、`running`。 |
| `debugType` | 当调试类型匹配时为真。<br>示例：`"debugType == 'node'"`。 |
| `inDebugRepl` | 焦点在调试控制台的 REPL 中。 |
| **集成终端上下文（Integrated terminal contexts）** | |
| `terminalFocus` | 一个集成终端拥有焦点。 |
| `terminalIsOpen` | 打开了一个集成终端。 |
| **任务执行上下文（Task execution contexts）** | |
| `shellExecutionSupported` | 当 VS Code 可以运行 `ShellExecution` 任务时为真。 |
| `processExecutionSupported` | 当 VS Code 可以运行 `ProcessExecution` 任务时为真。 |
| `customExecutionSupported` | 当 VS Code 可以运行 `CustomExecution` 任务时为真。 |
| **时间线视图上下文（Timeline view contexts）** | |
| `timelineFollowActiveEditor` | 当时间线视图跟随活动编辑器时为真。 |
| **时间线视图项上下文（Timeline view item contexts）** | |
| `timelineItem` | 当时间线项的上下文值匹配时为真。<br>示例：`"timelineItem =~ /git:file:commit\\b/"`。 |
| **扩展上下文（Extension contexts）** | |
| `extension` | 当扩展的 ID 匹配时为真。<br>示例：`"extension == eamodio.gitlens"`。 |
| `extensionStatus` | 当扩展已安装时为真。<br>示例：`"extensionStatus == installed"`。 |
| `extensionHasConfiguration` | 当扩展有配置时为真。 |
| **测试上下文（Testing contexts）** | |
| `testId` | 当前测试项的 ID 匹配时为真。 |
| `controllerId` | 当前测试控制器的 ID 匹配时为真。 |
| `testing.testItemHasUri` | 当前测试项关联了一个 URI 时为真。 |
| **工作区上下文（Workspace contexts）** | |
| `virtualWorkspace` | 当前工作区使用虚拟文件系统时为真。 |
| `isWorkspaceTrusted` | 当前工作区受信任时为真。 |
| **全局 UI 上下文（Global UI contexts）** | |
| `notificationFocus` | 通知拥有键盘焦点。 |
| `notificationCenterVisible` | VS Code 右下角的通知中心可见。 |
| `notificationToastsVisible` | VS Code 右下角的通知弹窗可见。 |
| `searchViewletVisible` | 搜索视图打开着。 |
| `sideBarVisible` | 侧边栏显示着。 |
| `sideBarFocus` | 侧边栏拥有焦点。 |
| `panelFocus` | 面板拥有焦点。 |
| `inZenMode` | 窗口处于禅模式（Zen Mode）。 |
| `isCenteredLayout` | 编辑器处于居中布局模式。 |
| `workbenchState` | 可以是 `empty`（空窗口）、`folder`（1 个文件夹）或 `workspace`（工作区）。 |
| `workspaceFolderCount` | 工作区文件夹的数量。 |
| `replaceActive` | 搜索视图的替换文本框打开着。 |
| `view` | 用于 `view/title` 和 `view/item/context`，要在其中显示命令的视图。<br>示例：`"view == myViewsExplorerID"`。 |
| `viewItem` | 用于 `view/item/context`，树项的 `contextValue`。<br>示例：`"viewItem == someContextValue"`。 |
| `webviewId` | 用于 `webview/context`，要在其中显示命令的 webview 的 ID。<br>示例：`"webviewId == catCoding"`。 |
| `webviewSection` | 用于 `webview/context`，要在其中显示命令的 webview 的区域。<br>示例：`"webviewSection == 'editor'"`。 |
| `isFullscreen` | 窗口处于全屏状态时为真。 |
| `focusedView` | 当前拥有焦点的视图的标识符。 |
| `canNavigateBack` | 可以后退导航时为真。 |
| `canNavigateForward` | 可以前进导航时为真。 |
| `canNavigateToLastEditLocation` | 可以导航到上一个编辑位置时为真。 |
| **全局编辑器 UI 上下文（Global Editor UI contexts）** | |
| `textCompareEditorVisible` | 至少有一个差异（比较）编辑器可见。 |
| `textCompareEditorActive` | 一个差异（比较）编辑器处于活动状态。 |
| `editorIsOpen` | 有一个编辑器打开时为真。 |
| `groupEditorsCount` | 一个编辑器组中的编辑器数量。 |
| `activeEditorGroupEmpty` | 活动编辑器组中没有编辑器时为真。 |
| `activeEditorGroupIndex` | 一个从 `1` 开始的数字，反映编辑器组在编辑器网格中的位置。<br>索引为 `1` 的组位于左上角第一个。 |
| `activeEditorGroupLast` | 对于编辑器网格中的最后一个编辑器组，值为 `true`。 |
| `multipleEditorGroups` | 存在多个编辑器组时为真。 |
| `activeEditor` | 一个组中的活动编辑器的标识符。 |
| `activeEditorIsDirty` | 一个组中的活动编辑器有未保存的更改时为真。 |
| `activeEditorIsNotPreview` | 一个组中的活动编辑器不处于预览模式时为真。 |
| `activeEditorIsPinned` | 一个组中的活动编辑器被固定时为真。 |
| `inSearchEditor` | 焦点在一个搜索编辑器中时为真。 |
| `activeWebviewPanelId` | 当前活动的 [webview 面板](../extension-guides/webview.md)的 ID。 |
| `activeCustomEditorId` | 当前活动的[自定义编辑器](../extension-guides/custom-editors.md)的 ID。 |
| **配置设置上下文（Configuration settings contexts）** | |
| `config.editor.minimap.enabled` | 当设置 `editor.minimap.enabled` 为 `true` 时为真。 |

> **注意**：在这里，你可以使用任何计算结果为布尔值的用户或工作区设置，只需加上 `"config."` 前缀。

**扩展开发中最常用的几个：**

| 场景 | when 子句 |
|---|---|
| 只在某种语言的编辑器中显示命令 | `"editorLangId == markdown"` 或 `"resourceLangId == markdown"` |
| 只对某种文件显示右键菜单 | `"resourceExtname == .json"`、`"resourceFilename =~ /\\.config\\.js$/"` |
| 只对文件夹显示右键菜单 | `"explorerResourceIsFolder"` |
| 树视图中只对某类节点显示操作 | `"view == myView && viewItem == file"`（`viewItem` 对应 `TreeItem.contextValue`，见 [树视图](../extension-guides/tree-view.md)） |
| 根据扩展自己的状态显示 | `"myExtension.isLoggedIn"`（见下文 [自定义上下文](#add-a-custom-when-clause-context)） |
| 区分桌面版和 Web 版 | `"!isWeb"` |

`editorLangId` 与 `resourceLangId` 的区别：前者是当前**拥有焦点的编辑器**的语言，用于快捷键、编辑器内的菜单；后者是**菜单所针对的资源**的语言，用于资源管理器右键菜单、编辑器标题菜单等（同一个菜单作用于不同的文件时，`resourceXxx` 会随之变化）。

---

<a id="visiblefocused-view-when-clause-context"></a>
## 可见 / 拥有焦点的视图的 when 子句上下文（Visible/focused view when clause context）

> 你可以使用一个 when 子句，检查某个特定的[视图](../ux-guidelines/views.md)是否可见或拥有焦点。

| 上下文名称 | 何时为真 |
| --- | --- |
| `view.${viewId}.visible` | 特定的视图可见时为真。<br>示例：`"view.workbench.explorer.fileView.visible"` |
| `focusedView` | 特定的视图拥有焦点时为真。<br>示例：`"focusedView == 'workbench.explorer.fileView'"` |

> 视图标识符：
>
> - `workbench.explorer.fileView` - 文件资源管理器
> - `workbench.explorer.openEditorsView` - 打开的编辑器
> - `outline` - 大纲视图
> - `timeline` - 时间线视图
> - `workbench.scm` - 源代码管理
> - `workbench.scm.repositories` - 源代码管理存储库
> - `workbench.debug.variablesView` - 变量
> - `workbench.debug.watchExpressionsView` - 监视
> - `workbench.debug.callStackView` - 调用堆栈
> - `workbench.debug.loadedScriptsView` - 已加载的脚本
> - `workbench.debug.breakPointsView` - 断点
> - `workbench.debug.disassemblyView` - 反汇编
> - `workbench.views.extensions.installed` - 已安装的扩展
> - `extensions.recommendedList` - 推荐的扩展
> - `workbench.panel.markers.view` - 问题
> - `workbench.panel.output` - 输出
> - `workbench.panel.repl.view` - 调试控制台
> - `terminal` - 集成终端
> - `workbench.panel.comments` - 注释

你自己贡献的视图同样适用，`viewId` 就是 `contributes.views` 中的 `id`，例如 `"view.nodeDependencies.visible"`。

---

<a id="visible-view-container-when-clause-context"></a>
## 可见的视图容器的 when 子句上下文（Visible view container when clause context）

> 你可以使用一个 when 子句，检查某个特定的[视图容器](../ux-guidelines/views.md#view-containers)是否可见。

| 上下文名称 | 何时为真 |
| --- | --- |
| `activeViewlet` | 视图容器在侧边栏中可见时为真。<br>示例：`"activeViewlet == 'workbench.view.explorer'"` |
| `activePanel` | 视图容器在面板中可见时为真。<br>示例：`"activePanel == 'workbench.panel.output'"` |
| `activeAuxiliary` | 视图容器在辅助侧边栏中可见时为真。<br>示例：`"activeAuxiliary == 'workbench.view.debug'"` |

> 视图容器标识符：
>
> - `workbench.view.explorer` - 文件资源管理器
> - `workbench.view.search` - 搜索
> - `workbench.view.scm` - 源代码管理
> - `workbench.view.debug` - 运行
> - `workbench.view.extensions` - 扩展
> - `workbench.panel.markers` - 问题
> - `workbench.panel.output` - 输出
> - `workbench.panel.repl` - 调试控制台
> - `terminal` - 集成终端
> - `workbench.panel.comments` - 注释
>
> 如果你想要一个只在特定视图容器拥有焦点时才启用的 when 子句，可以把 `sideBarFocus`、`panelFocus` 或 `auxiliaryBarFocus` 与 `activeViewlet`、`activePanel` 或 `activeAuxiliary` 上下文键组合使用。
>
> 例如，下面的 when 子句只在文件资源管理器拥有焦点时为真：

```json
"sideBarFocus && activeViewlet == 'workbench.view.explorer'"
```

你自己贡献的视图容器（`contributes.viewsContainers`），在活动栏中的标识符是 `workbench.view.extension.<容器 id>`，例如 `"activeViewlet == 'workbench.view.extension.package-explorer'"`。

---

<a id="check-a-setting-in-a-when-clause"></a>
## 在 when 子句中检查设置（Check a setting in a when clause）

> 在一个 when 子句中，你可以通过加上 `config.` 前缀来引用一个配置（设置）的值，例如 `config.editor.tabCompletion` 或 `config.breadcrumbs.enabled`。

这也适用于你的扩展自己的设置：

```json
"when": "config.myExtension.showStatusBarItem"
```

```json
"when": "config.myExtension.mode == 'advanced'"
```

用户修改设置后，when 子句会立即重新计算，不需要扩展写任何代码。

---

<a id="add-a-custom-when-clause-context"></a>
## 添加一个自定义的 when 子句上下文（Add a custom when clause context）

> 如果你正在编写自己的 VS Code 扩展，需要使用一个 when 子句上下文来启用 / 禁用命令、菜单或视图，而现有的键都不能满足你的需要，你可以用 `setContext` 命令添加你自己的上下文键。
>
> 下面的第一个例子把键 `myExtension.showMyCommand` 设为 true，你可以把它用于命令的启用条件（enablement），或者用于 `when` 属性。第二个例子存储了一个值，你可以在 when 子句中用它来检查打开的酷东西的数量是否大于 2。

```js
vscode.commands.executeCommand('setContext', 'myExtension.showMyCommand', true);

vscode.commands.executeCommand('setContext', 'myExtension.numberOfCoolOpenThings', 4);
```

对应的使用方式：

```json
"menus": {
  "commandPalette": [
    { "command": "myExtension.doCool", "when": "myExtension.showMyCommand" },
    { "command": "myExtension.manageCool", "when": "myExtension.numberOfCoolOpenThings > 2" }
  ]
}
```

几个要点：

- 上下文键是**全局**的，所有扩展共享同一个命名空间，所以一定要加上扩展名前缀（如 `myExtension.`），避免冲突。
- 上下文键不会持久化：VS Code 重启后它们就没有了，扩展激活时要重新设置。在扩展激活之前，这个键不存在，when 子句中引用它会被视为 false（或 `undefined`）。
- 值可以是布尔、字符串、数字、数组或对象（数组和对象用于 `in` 运算符）。

---

<a id="inspect-context-keys-utility"></a>
## 检查上下文键工具（Inspect Context Keys utility）

> 如果你想在运行时查看当前所有活动的上下文键，可以从命令面板（`Ctrl+Shift+P`）中使用 **Developer: Inspect Context Keys** 命令。**Inspect Context Keys** 会在 VS Code 开发者工具的 **Console**（控制台）选项卡（**Help** > **Toggle Developer Tools**，即“帮助 > 切换开发人员工具”）中显示上下文键及其值。
>
> 当你运行 **Developer: Inspect Context Keys** 时，你的光标会高亮 VS Code UI 中的元素，当你点击一个元素时，当前的上下文键及其状态会作为一个对象输出到控制台。

![检查上下文键的输出](images/when-clause-contexts/inspect-context-keys.png)

截图是开发者工具的 Console 选项卡，输出了一个对象，展开后按字母顺序列出了所有上下文键及其值，例如 `activeEditorGroupIndex: 1`、`activeViewlet: "workbench.view.debug"`、`breakpointSelected: false`；对象的开头还有一些 `config.` 开头的设置值。

> 活动的上下文键的列表非常长，并且可能包含来自你已安装的扩展的[自定义上下文键](#add-a-custom-when-clause-context)。

> **注意**：有些上下文键是供 VS Code 内部使用的，将来可能会改变。

**调试 when 子句的方法：** 菜单没有按预期显示时，运行 **Developer: Inspect Context Keys**，点击菜单所在的位置（比如资源管理器中的某个文件），然后在控制台中搜索你用到的键，看看它们的实际值。在扩展开发宿主中做这件事，可以看到你的扩展用 `setContext` 设置的键。

---

## 本篇小结

```text
when 子句：package.json 中的字符串表达式，根据当前 UI 状态实时求值
  用于 keybindings、menus、commands.enablement、views、viewsWelcome、walkthroughs

运算符（优先级 ! > && > ||）
  ! && ||           逻辑
  == != （=== !==）  相等（右侧是字面值；含空格时用单引号）
  > >= < <=         比较（两侧必须有空格）
  =~ /正则/标志      匹配（JSON 中反斜杠要双写；标志 i s m u）
  in / not in       在数组或对象的键中查找

常用上下文键
  editorLangId、resourceLangId、resourceExtname、resourceFilename、resourceScheme
  explorerResourceIsFolder、view、viewItem、webviewId、isWeb、isWorkspaceTrusted
  view.<id>.visible、focusedView、activeViewlet、activePanel
  config.<设置名>

自定义：executeCommand('setContext', '扩展名.键', 值)（全局、不持久化、加前缀）
调试：Developer: Inspect Context Keys → 开发者工具控制台
```
