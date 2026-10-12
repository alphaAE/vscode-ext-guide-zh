# 产品图标参考（Product Icon Reference）

> 原文：[Product Icon Reference](https://code.visualstudio.com/api/references/icons-in-labels)
> 源文件：`microsoft/vscode-docs` → `api/references/icons-in-labels.md`（DateApproved: 10/7/2026）

> Visual Studio Code 包含一组内置的图标，它们用在视图和编辑器中，也可以用在悬停、状态栏中，并且可以被扩展使用。这些图标是**产品图标（product icons）**，与之相对的是**文件图标（file icons）**，后者显示在整个 UI 中的文件名旁边。
>
> VS Code 自带的产品图标包含在 [Codicon 图标字体](https://github.com/microsoft/vscode-codicons)中，构成了**默认的**产品图标主题。扩展可以提供新的[产品图标主题](../extension-guides/product-icon-theme.md)来重新定义这些图标，赋予 VS Code 新的外观。
>
> 为了做到这一点，所有的产品图标都由一个 ID 来标识。图标标识符被用在 UI 组件的标签中（`$(pencil)`），在 API 中用作 `ThemeIcon`，以及在需要图标的贡献中使用。
>
> 图标标识符与实际的图标字体字形之间的关联，是在产品图标主题中完成的。

| | 产品图标 | 文件图标 |
|---|---|---|
| 出现在 | 活动栏、视图标题、工具栏、状态栏、菜单等 UI 各处 | 资源管理器、编辑器标签页等处的文件名旁边 |
| 默认来源 | Codicon 图标字体 | 文件图标主题（如内置的 Seti） |
| 替换方式 | [产品图标主题](../extension-guides/product-icon-theme.md) | [文件图标主题](../extension-guides/file-icon-theme.md) |

**扩展中使用图标的三种方式：**

| 位置 | 写法 | 例子 |
|---|---|---|
| 文字标签中（状态栏文字、快速选择项的标签、Markdown 悬停） | `$(图标ID)` | `statusBarItem.text = '$(sync~spin) 同步中'` |
| API 中的图标参数（树项、快速选择按钮等） | `new vscode.ThemeIcon('图标ID')` | `treeItem.iconPath = new vscode.ThemeIcon('folder')` |
| `package.json` 的贡献中（命令图标、视图容器图标等） | `"$(图标ID)"` | `"icon": "$(refresh)"` |

---

<a id="icons-in-labels"></a>
## 标签中的图标（Icons in labels）

> 图标可以用在悬停中的 Markdown 标签、[StatusBarItem](https://code.visualstudio.com/api/references/vscode-api#StatusBarItem) 的文字，以及 [QuickPickItem](https://code.visualstudio.com/api/references/vscode-api#QuickPickItem) 的标签 API 中。在 Markdown 中添加图标的语法是 `$(iconIdentifier)`：

```ts
$(alert);
```

> 你也可以嵌入文字，并使用多个图标：

```ts
$(eye) $(heart) $(mark-github) GitHub
```

> 要在标签中放置字面的 `${...}` 文字，用反斜杠转义 `$`：

```ts
\$(eye)
```

（原文代码块标的语言是 `ts`，但这些其实是标签字符串的内容，不是 TypeScript 代码。在代码中的写法是 `item.text = '$(eye) $(heart) $(mark-github) GitHub'`；转义时，JavaScript 字符串中的反斜杠本身也要写两个：`'\\$(eye)'`。）

在 Markdown 悬停中使用图标时，`MarkdownString` 需要开启 `supportThemeIcons`：

```ts
const md = new vscode.MarkdownString('$(info) 这是一条提示', true); // 第二个参数 supportThemeIcons
```

---

<a id="animation"></a>
## 动画（Animation）

> 你可以给以下图标的名称后面加上 `~spin`，为它们应用旋转动画：
>
> - `sync`
> - `loading`
> - `gear`

```ts
$(sync~spin)
```

常用于状态栏中表示“正在进行中”，例如 `'$(loading~spin) 正在加载...'`。

---

<a id="icon-contribution-point"></a>
## 图标贡献点（Icon contribution point）

> 图标贡献点允许扩展通过 ID 定义额外的图标，以及一个默认图标。之后，这个扩展（或任何依赖这个扩展的其他扩展）就可以在标签中（`$(iconId)`），或者在所有可以使用 `ThemeIcon` 的地方（`new ThemeIcon("iconId")`）使用这个图标 ID。

```json
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
```

> 产品图标主题可以重新定义这个图标（如果它们知道这个图标 ID 的话）。

| 字段 | 含义 |
|---|---|
| 键名（`distro-ubuntu`） | 图标 ID |
| `description` | 图标的说明（原文中 `distro-fedora` 的说明也写成了 “Ubuntu icon”，应为 “Fedora icon”） |
| `default.fontPath` | 图标字体文件的路径（`.woff` 格式） |
| `default.fontCharacter` | 图标在字体中的字符码（`\\E001` 在 JSON 中表示 Unicode 码点 U+E001，通常位于私有使用区） |

`default` 也可以是另一个已有图标的 ID（字符串），例如 `"default": "zap"`，表示默认使用 Codicon 中的 `zap` 图标。这让你可以给自己的扩展定义一个语义化的图标 ID（比如 `myext-run`），默认指向某个 Codicon，产品图标主题的作者再根据需要替换它。

---

<a id="icon-listing"></a>
## 图标列表（Icon Listing）

> 下面是按标识符列出的内置产品图标。
>
> 图标的 ID 标识了这个图标被使用的位置。默认的 codicon ID 说明了默认使用 codicon 库中的哪一个图标，预览展示了这个图标的样子。
>
> [产品图标主题](../extension-guides/product-icon-theme.md)可以单独替换每个图标，也可以替换 codicon 库中的所有图标。

**关于预览列：** 表格中的“预览”列使用了 `<i class="codicon codicon-xxx"></i>`，它依赖官方文档网站加载的 Codicon 字体样式，在本地或 GitHub 上查看时不会显示出图标。要查看图标的样子，请访问 [原文页面](https://code.visualstudio.com/api/references/icons-in-labels#icon-listing) 或 [Codicon 图标一览](https://microsoft.github.io/vscode-codicons/dist/codicon.html)。

**两张表的区别：**

- 第一张表是**产品图标 ID**（如 `debug-start`）：它表示的是“在 VS Code 的某个位置使用的图标”，默认指向某个 codicon。产品图标主题通过这些 ID 替换特定位置的图标。
- 第二张表是 **Codicon 库中的所有图标 ID**（如 `play`）：这是扩展在 `$(...)` 和 `ThemeIcon` 中最常用的那一组。

例如 `debug-start` 默认使用的是 codicon `debug-start`；扩展在自己的标签中写 `$(debug-start)` 时，引用的是产品图标 ID，如果用户使用了某个产品图标主题，显示的就是主题替换后的图标。

<div id="codicon-listing">

| 预览 | 标识符 | 默认 codicon ID | 说明 |
| --- | --- | --- | --- |
|<i class="codicon codicon-account"></i>|accounts-view-bar-icon|account|视图栏中的账户图标。|
|<i class="codicon codicon-activate-breakpoints"></i>|breakpoints-activate|activate-breakpoints|断点视图中“激活”操作的图标。|
|<i class="codicon codicon-close-all"></i>|breakpoints-remove-all|close-all|断点视图中“全部删除”操作的图标。|
|<i class="codicon codicon-debug-alt"></i>|breakpoints-view-icon|debug-alt|断点视图的视图图标。|
|<i class="codicon codicon-call-incoming"></i>|callhierarchy-incoming|call-incoming|调用层次视图中传入调用的图标。|
|<i class="codicon codicon-call-outgoing"></i>|callhierarchy-outgoing|call-outgoing|调用层次视图中传出调用的图标。|
|<i class="codicon codicon-debug-alt"></i>|callstack-view-icon|debug-alt|调用堆栈视图的视图图标。|
|<i class="codicon codicon-bug"></i>|callstack-view-session|bug|调用堆栈视图中会话图标的图标。|
|<i class="codicon codicon-comment-discussion"></i>|chat-editor-label-icon|comment-discussion|聊天编辑器标签的图标。|
|<i class="codicon codicon-comment-discussion"></i>|comments-view-icon|comment-discussion|注释视图的视图图标。|
|<i class="codicon codicon-debug-breakpoint"></i>|debug-breakpoint|debug-breakpoint|断点的图标。|
|<i class="codicon codicon-debug-breakpoint-conditional"></i>|debug-breakpoint-conditional|debug-breakpoint-conditional|条件断点的图标。|
|<i class="codicon codicon-debug-breakpoint-conditional-disabled"></i>|debug-breakpoint-conditional-disabled|debug-breakpoint-conditional-disabled|已禁用的条件断点的图标。|
|<i class="codicon codicon-debug-breakpoint-conditional-unverified"></i>|debug-breakpoint-conditional-unverified|debug-breakpoint-conditional-unverified|未验证的条件断点的图标。|
|<i class="codicon codicon-debug-breakpoint-data"></i>|debug-breakpoint-data|debug-breakpoint-data|数据断点的图标。|
|<i class="codicon codicon-debug-breakpoint-data-disabled"></i>|debug-breakpoint-data-disabled|debug-breakpoint-data-disabled|已禁用的数据断点的图标。|
|<i class="codicon codicon-debug-breakpoint-data-unverified"></i>|debug-breakpoint-data-unverified|debug-breakpoint-data-unverified|未验证的数据断点的图标。|
|<i class="codicon codicon-debug-breakpoint-disabled"></i>|debug-breakpoint-disabled|debug-breakpoint-disabled|已禁用的断点的图标。|
|<i class="codicon codicon-debug-breakpoint-function"></i>|debug-breakpoint-function|debug-breakpoint-function|函数断点的图标。|
|<i class="codicon codicon-debug-breakpoint-function-disabled"></i>|debug-breakpoint-function-disabled|debug-breakpoint-function-disabled|已禁用的函数断点的图标。|
|<i class="codicon codicon-debug-breakpoint-function-unverified"></i>|debug-breakpoint-function-unverified|debug-breakpoint-function-unverified|未验证的函数断点的图标。|
|<i class="codicon codicon-debug-breakpoint-log"></i>|debug-breakpoint-log|debug-breakpoint-log|日志断点的图标。|
|<i class="codicon codicon-debug-breakpoint-log-disabled"></i>|debug-breakpoint-log-disabled|debug-breakpoint-log-disabled|已禁用的日志断点的图标。|
|<i class="codicon codicon-debug-breakpoint-log-unverified"></i>|debug-breakpoint-log-unverified|debug-breakpoint-log-unverified|未验证的日志断点的图标。|
|<i class="codicon codicon-debug-breakpoint-unsupported"></i>|debug-breakpoint-unsupported|debug-breakpoint-unsupported|不受支持的断点的图标。|
|<i class="codicon codicon-debug-breakpoint-unverified"></i>|debug-breakpoint-unverified|debug-breakpoint-unverified|未验证的断点的图标。|
|<i class="codicon codicon-collapse-all"></i>|debug-collapse-all|collapse-all|调试视图中“全部折叠”操作的图标。|
|<i class="codicon codicon-gear"></i>|debug-configure|gear|调试“配置”操作的图标。|
|<i class="codicon codicon-debug-console"></i>|debug-console|debug-console|“打开调试控制台”操作的图标。|
|<i class="codicon codicon-clear-all"></i>|debug-console-clear-all|clear-all|调试控制台中“全部清除”操作的图标。|
|<i class="codicon codicon-arrow-small-right"></i>|debug-console-evaluation-input|arrow-small-right|调试求值输入标记的图标。|
|<i class="codicon codicon-chevron-right"></i>|debug-console-evaluation-prompt|chevron-right|调试求值提示符的图标。|
|<i class="codicon codicon-debug-console"></i>|debug-console-view-icon|debug-console|调试控制台视图的视图图标。|
|<i class="codicon codicon-debug-continue"></i>|debug-continue|debug-continue|调试“继续”操作的图标。|
|<i class="codicon codicon-debug-disconnect"></i>|debug-disconnect|debug-disconnect|调试“断开连接”操作的图标。|
|<i class="codicon codicon-gripper"></i>|debug-gripper|gripper|调试工具栏拖动手柄的图标。|
|<i class="codicon codicon-debug-hint"></i>|debug-hint|debug-hint|在编辑器字形边距中悬停时显示的断点提示的图标。|
|<i class="codicon codicon-debug-pause"></i>|debug-pause|debug-pause|调试“暂停”操作的图标。|
|<i class="codicon codicon-debug-restart"></i>|debug-restart|debug-restart|调试“重启”操作的图标。|
|<i class="codicon codicon-debug-restart-frame"></i>|debug-restart-frame|debug-restart-frame|调试“重启帧”操作的图标。|
|<i class="codicon codicon-debug-reverse-continue"></i>|debug-reverse-continue|debug-reverse-continue|调试“反向继续”操作的图标。|
|<i class="codicon codicon-debug-stackframe"></i>|debug-stackframe|debug-stackframe|显示在编辑器字形边距中的堆栈帧的图标。|
|<i class="codicon codicon-debug-stackframe-focused"></i>|debug-stackframe-focused|debug-stackframe-focused|显示在编辑器字形边距中的、拥有焦点的堆栈帧的图标。|
|<i class="codicon codicon-debug-start"></i>|debug-start|debug-start|调试“启动”操作的图标。|
|<i class="codicon codicon-debug-step-back"></i>|debug-step-back|debug-step-back|调试“单步后退”操作的图标。|
|<i class="codicon codicon-debug-step-into"></i>|debug-step-into|debug-step-into|调试“单步进入”操作的图标。|
|<i class="codicon codicon-debug-step-out"></i>|debug-step-out|debug-step-out|调试“单步跳出”操作的图标。|
|<i class="codicon codicon-debug-step-over"></i>|debug-step-over|debug-step-over|调试“单步跳过”操作的图标。|
|<i class="codicon codicon-debug-stop"></i>|debug-stop|debug-stop|调试“停止”操作的图标。|
|<i class="codicon codicon-window"></i>|default-view-icon|window|默认的视图图标。|
|<i class="codicon codicon-arrow-down"></i>|diff-editor-next-change|arrow-down|差异编辑器中“下一个更改”操作的图标。|
|<i class="codicon codicon-arrow-up"></i>|diff-editor-previous-change|arrow-up|差异编辑器中“上一个更改”操作的图标。|
|<i class="codicon codicon-whitespace"></i>|diff-editor-toggle-whitespace|whitespace|差异编辑器中“切换空白”操作的图标。|
|<i class="codicon codicon-add"></i>|diff-insert|add|差异编辑器中插入内容的行装饰。|
|<i class="codicon codicon-remove"></i>|diff-remove|remove|差异编辑器中删除内容的行装饰。|
|<i class="codicon codicon-close"></i>|diff-review-close|close|差异审阅中“关闭”的图标。|
|<i class="codicon codicon-add"></i>|diff-review-insert|add|差异审阅中“插入”的图标。|
|<i class="codicon codicon-remove"></i>|diff-review-remove|remove|差异审阅中“删除”的图标。|
|<i class="codicon codicon-debug"></i>|disassembly-editor-label-icon|debug|反汇编编辑器标签的图标。|
|<i class="codicon codicon-files"></i>|explorer-view-icon|files|资源管理器视图的视图图标。|
|<i class="codicon codicon-clear-all"></i>|extensions-clear-search-results|clear-all|扩展视图中“清除搜索结果”操作的图标。|
|<i class="codicon codicon-pencil"></i>|extensions-configure-recommended|pencil|扩展视图中“配置推荐的扩展”操作的图标。|
|<i class="codicon codicon-extensions"></i>|extensions-editor-label-icon|extensions|扩展编辑器标签的图标。|
|<i class="codicon codicon-filter"></i>|extensions-filter|filter|扩展视图中“筛选”操作的图标。|
|<i class="codicon codicon-info"></i>|extensions-info-message|info|在扩展编辑器中与信息消息一起显示的图标。|
|<i class="codicon codicon-cloud-download"></i>|extensions-install-count|cloud-download|在扩展视图和编辑器中与安装数量一起显示的图标。|
|<i class="codicon codicon-cloud-download"></i>|extensions-install-local-in-remote|cloud-download|扩展视图中“在远程中安装本地扩展”操作的图标。|
|<i class="codicon codicon-cloud-download"></i>|extensions-install-workspace-recommended|cloud-download|扩展视图中“安装工作区推荐的扩展”操作的图标。|
|<i class="codicon codicon-gear"></i>|extensions-manage|gear|扩展视图中“管理”操作的图标。|
|<i class="codicon codicon-star"></i>|extensions-rating|star|在扩展视图和编辑器中与评分一起显示的图标。|
|<i class="codicon codicon-refresh"></i>|extensions-refresh|refresh|扩展视图中“刷新”操作的图标。|
|<i class="codicon codicon-remote"></i>|extensions-remote|remote|在扩展视图和编辑器中表示某个扩展是远程扩展的图标。|
|<i class="codicon codicon-star-empty"></i>|extensions-star-empty|star-empty|扩展编辑器中用于评分的空心星形图标。|
|<i class="codicon codicon-star-full"></i>|extensions-star-full|star-full|扩展编辑器中用于评分的实心星形图标。|
|<i class="codicon codicon-star-half"></i>|extensions-star-half|star-half|扩展编辑器中用于评分的半星图标。|
|<i class="codicon codicon-sync"></i>|extensions-sync-enabled|sync|表示某个扩展已同步的图标。|
|<i class="codicon codicon-sync-ignored"></i>|extensions-sync-ignored|sync-ignored|表示某个扩展在同步时被忽略的图标。|
|<i class="codicon codicon-extensions"></i>|extensions-view-icon|extensions|扩展视图的视图图标。|
|<i class="codicon codicon-warning"></i>|extensions-warning-message|warning|在扩展编辑器中与警告消息一起显示的图标。|
|<i class="codicon codicon-chevron-right"></i>|find-collapsed|chevron-right|表示编辑器查找小部件已折叠的图标。|
|<i class="codicon codicon-chevron-down"></i>|find-expanded|chevron-down|表示编辑器查找小部件已展开的图标。|
|<i class="codicon codicon-arrow-down"></i>|find-next-match|arrow-down|编辑器查找小部件中“查找下一个”的图标。|
|<i class="codicon codicon-arrow-up"></i>|find-previous-match|arrow-up|编辑器查找小部件中“查找上一个”的图标。|
|<i class="codicon codicon-replace"></i>|find-replace|replace|编辑器查找小部件中“替换”的图标。|
|<i class="codicon codicon-replace-all"></i>|find-replace-all|replace-all|编辑器查找小部件中“全部替换”的图标。|
|<i class="codicon codicon-selection"></i>|find-selection|selection|编辑器查找小部件中“在选定内容中查找”的图标。|
|<i class="codicon codicon-chevron-right"></i>|folding-collapsed|chevron-right|编辑器字形边距中已折叠范围的图标。|
|<i class="codicon codicon-chevron-down"></i>|folding-expanded|chevron-down|编辑器字形边距中已展开范围的图标。|
|<i class="codicon codicon-lightbulb"></i>|getting-started-beginner|lightbulb|入门（Getting Started）中初学者类别使用的图标|
|<i class="codicon codicon-github"></i>|getting-started-codespaces|github|入门中 Codespaces 类别使用的图标|
|<i class="codicon codicon-pass-filled"></i>|getting-started-item-checked|pass-filled|用于表示已完成的入门项|
|<i class="codicon codicon-circle-large-outline"></i>|getting-started-item-unchecked|circle-large-outline|用于表示尚未完成的入门项|
|<i class="codicon codicon-heart"></i>|getting-started-setup|heart|入门中设置类别使用的图标|
|<i class="codicon codicon-arrow-down"></i>|goto-next-location|arrow-down|“转到下一个编辑器位置”的图标。|
|<i class="codicon codicon-arrow-up"></i>|goto-previous-location|arrow-up|“转到上一个编辑器位置”的图标。|
|<i class="codicon codicon-add"></i>|keybindings-add|add|快捷键 UI 中“添加”操作的图标。|
|<i class="codicon codicon-edit"></i>|keybindings-edit|edit|快捷键 UI 中“编辑”操作的图标。|
|<i class="codicon codicon-keyboard"></i>|keybindings-editor-label-icon|keyboard|快捷键编辑器标签的图标。|
|<i class="codicon codicon-record-keys"></i>|keybindings-record-keys|record-keys|快捷键 UI 中“录制按键”操作的图标。|
|<i class="codicon codicon-sort-precedence"></i>|keybindings-sort|sort-precedence|快捷键 UI 中“按优先级排序”开关的图标。|
|<i class="codicon codicon-debug-alt"></i>|loaded-scripts-view-icon|debug-alt|已加载脚本视图的视图图标。|
|<i class="codicon codicon-chevron-down"></i>|marker-navigation-next|chevron-down|“转到下一个标记（问题）”的图标。|
|<i class="codicon codicon-chevron-up"></i>|marker-navigation-previous|chevron-up|“转到上一个标记（问题）”的图标。|
|<i class="codicon codicon-filter"></i>|markers-view-filter|filter|标记（问题）视图中筛选配置的图标。|
|<i class="codicon codicon-warning"></i>|markers-view-icon|warning|标记（问题）视图的视图图标。|
|<i class="codicon codicon-chevron-down"></i>|markers-view-multi-line-collapsed|chevron-down|表示标记（问题）视图中多行内容已折叠的图标。|
|<i class="codicon codicon-chevron-up"></i>|markers-view-multi-line-expanded|chevron-up|表示标记（问题）视图中多行内容已展开显示的图标。|
|<i class="codicon codicon-diff-multiple"></i>|multi-diff-editor-label-icon|diff-multiple|多文件差异编辑器标签的图标。|
|<i class="codicon codicon-clear-all"></i>|notebook-clear|clear-all|在笔记本编辑器中清除单元格输出的图标。|
|<i class="codicon codicon-chevron-right"></i>|notebook-collapsed|chevron-right|在笔记本编辑器中标注已折叠区域的图标。|
|<i class="codicon codicon-trash"></i>|notebook-delete-cell|trash|在笔记本编辑器中删除单元格的图标。|
|<i class="codicon codicon-pencil"></i>|notebook-edit|pencil|在笔记本编辑器中编辑单元格的图标。|
|<i class="codicon codicon-play"></i>|notebook-execute|play|在笔记本编辑器中执行的图标。|
|<i class="codicon codicon-run-all"></i>|notebook-execute-all|run-all|在笔记本编辑器中执行所有单元格的图标。|
|<i class="codicon codicon-chevron-down"></i>|notebook-expanded|chevron-down|在笔记本编辑器中标注已展开区域的图标。|
|<i class="codicon codicon-settings-gear"></i>|notebook-kernel-configure|settings-gear|笔记本编辑器的内核配置小部件中的配置图标。|
|<i class="codicon codicon-server-environment"></i>|notebook-kernel-select|server-environment|在笔记本编辑器中选择内核的配置图标。|
|<i class="codicon codicon-code"></i>|notebook-mimetype|code|笔记本编辑器中 MIME 类型的图标。|
|<i class="codicon codicon-arrow-down"></i>|notebook-move-down|arrow-down|在笔记本编辑器中下移单元格的图标。|
|<i class="codicon codicon-arrow-up"></i>|notebook-move-up|arrow-up|在笔记本编辑器中上移单元格的图标。|
|<i class="codicon codicon-file-code"></i>|notebook-open-as-text|file-code|在文本编辑器中打开笔记本的图标。|
|<i class="codicon codicon-preview"></i>|notebook-render-output|preview|在差异编辑器中渲染输出的图标。|
|<i class="codicon codicon-discard"></i>|notebook-revert|discard|在笔记本编辑器中还原的图标。|
|<i class="codicon codicon-split-vertical"></i>|notebook-split-cell|split-vertical|在笔记本编辑器中拆分单元格的图标。|
|<i class="codicon codicon-error"></i>|notebook-state-error|error|在笔记本编辑器中表示错误状态的图标。|
|<i class="codicon codicon-check"></i>|notebook-state-success|check|在笔记本编辑器中表示成功状态的图标。|
|<i class="codicon codicon-primitive-square"></i>|notebook-stop|primitive-square|在笔记本编辑器中停止执行的图标。|
|<i class="codicon codicon-check"></i>|notebook-stop-edit|check|在笔记本编辑器中停止编辑单元格的图标。|
|<i class="codicon codicon-unfold"></i>|notebook-unfold|unfold|在笔记本编辑器中展开单元格的图标。|
|<i class="codicon codicon-close"></i>|notifications-clear|close|通知中“清除”操作的图标。|
|<i class="codicon codicon-clear-all"></i>|notifications-clear-all|clear-all|通知中“全部清除”操作的图标。|
|<i class="codicon codicon-chevron-down"></i>|notifications-collapse|chevron-down|通知中“折叠”操作的图标。|
|<i class="codicon codicon-gear"></i>|notifications-configure|gear|通知中“配置”操作的图标。|
|<i class="codicon codicon-chevron-up"></i>|notifications-expand|chevron-up|通知中“展开”操作的图标。|
|<i class="codicon codicon-chevron-down"></i>|notifications-hide|chevron-down|通知中“隐藏”操作的图标。|
|<i class="codicon codicon-book"></i>|open-editors-view-icon|book|打开的编辑器视图的视图图标。|
|<i class="codicon codicon-symbol-class"></i>|outline-view-icon|symbol-class|大纲视图的视图图标。|
|<i class="codicon codicon-output"></i>|output-view-icon|output|输出视图的视图图标。|
|<i class="codicon codicon-close"></i>|panel-close|close|关闭面板的图标。|
|<i class="codicon codicon-chevron-up"></i>|panel-maximize|chevron-up|最大化面板的图标。|
|<i class="codicon codicon-chevron-down"></i>|panel-restore|chevron-down|还原面板的图标。|
|<i class="codicon codicon-chevron-down"></i>|parameter-hints-next|chevron-down|“显示下一个参数提示”的图标。|
|<i class="codicon codicon-chevron-up"></i>|parameter-hints-previous|chevron-up|“显示上一个参数提示”的图标。|
|<i class="codicon codicon-plus"></i>|ports-forward-icon|plus|“转发”操作的图标。|
|<i class="codicon codicon-globe"></i>|ports-open-browser-icon|globe|“打开浏览器”操作的图标。|
|<i class="codicon codicon-x"></i>|ports-stop-forward-icon|x|“停止转发”操作的图标。|
|<i class="codicon codicon-plug"></i>|ports-view-icon|plug|远程端口视图的视图图标。|
|<i class="codicon codicon-clear-all"></i>|preferences-clear-input|clear-all|设置和快捷键 UI 中清除输入的图标。|
|<i class="codicon codicon-go-to-file"></i>|preferences-open-settings|go-to-file|打开设置命令的图标。|
|<i class="codicon codicon-lock"></i>|private-ports-view-icon|lock|表示私有远程端口的图标。|
|<i class="codicon codicon-eye"></i>|public-ports-view-icon|eye|表示公共远程端口的图标。|
|<i class="codicon codicon-lightbulb"></i>|refactor-preview-view-icon|lightbulb|重构预览视图的视图图标。|
|<i class="codicon codicon-book"></i>|remote-explorer-documentation|book|远程资源管理器视图中的文档图标。|
|<i class="codicon codicon-twitter"></i>|remote-explorer-feedback|twitter|远程资源管理器视图中的反馈图标。|
|<i class="codicon codicon-star"></i>|remote-explorer-get-started|star|远程资源管理器视图中的入门图标。|
|<i class="codicon codicon-comment"></i>|remote-explorer-report-issues|comment|远程资源管理器视图中的报告问题图标。|
|<i class="codicon codicon-issues"></i>|remote-explorer-review-issues|issues|远程资源管理器视图中的查看问题图标。|
|<i class="codicon codicon-remote-explorer"></i>|remote-explorer-view-icon|remote-explorer|远程资源管理器视图的视图图标。|
|<i class="codicon codicon-chevron-up"></i>|review-comment-collapse|chevron-up|折叠审阅注释的图标。|
|<i class="codicon codicon-debug-alt"></i>|run-view-icon|debug-alt|运行和调试视图的视图图标。|
|<i class="codicon codicon-extensions"></i>|runtime-extensions-editor-label-icon|extensions|运行时扩展编辑器标签的图标。|
|<i class="codicon codicon-clear-all"></i>|search-clear-results|clear-all|搜索视图中清除结果的图标。|
|<i class="codicon codicon-collapse-all"></i>|search-collapse-results|collapse-all|搜索视图中折叠结果的图标。|
|<i class="codicon codicon-ellipsis"></i>|search-details|ellipsis|显示搜索详细信息的图标。|
|<i class="codicon codicon-search"></i>|search-editor-label-icon|search|搜索编辑器标签的图标。|
|<i class="codicon codicon-expand-all"></i>|search-expand-results|expand-all|搜索视图中展开结果的图标。|
|<i class="codicon codicon-chevron-right"></i>|search-hide-replace|chevron-right|折叠搜索视图中替换区域的图标。|
|<i class="codicon codicon-new-file"></i>|search-new-editor|new-file|“打开新的搜索编辑器”操作的图标。|
|<i class="codicon codicon-refresh"></i>|search-refresh|refresh|搜索视图中刷新的图标。|
|<i class="codicon codicon-close"></i>|search-remove|close|删除一个搜索结果的图标。|
|<i class="codicon codicon-replace"></i>|search-replace|replace|搜索视图中替换的图标。|
|<i class="codicon codicon-replace-all"></i>|search-replace-all|replace-all|搜索视图中全部替换的图标。|
|<i class="codicon codicon-list-selection"></i>|search-show-context|list-selection|在搜索编辑器中切换上下文的图标。|
|<i class="codicon codicon-chevron-down"></i>|search-show-replace|chevron-down|展开搜索视图中替换区域的图标。|
|<i class="codicon codicon-search-stop"></i>|search-stop|search-stop|搜索视图中停止的图标。|
|<i class="codicon codicon-search"></i>|search-view-icon|search|搜索视图的视图图标。|
|<i class="codicon codicon-add"></i>|settings-add|add|设置 UI 中“添加”操作的图标。|
|<i class="codicon codicon-discard"></i>|settings-discard|discard|设置 UI 中“放弃”操作的图标。|
|<i class="codicon codicon-edit"></i>|settings-edit|edit|设置 UI 中“编辑”操作的图标。|
|<i class="codicon codicon-settings"></i>|settings-editor-label-icon|settings|设置编辑器标签的图标。|
|<i class="codicon codicon-triangle-down"></i>|settings-folder-dropdown|triangle-down|拆分式 JSON 设置编辑器中文件夹下拉按钮的图标。|
|<i class="codicon codicon-chevron-right"></i>|settings-group-collapsed|chevron-right|拆分式 JSON 设置编辑器中已折叠区域的图标。|
|<i class="codicon codicon-chevron-down"></i>|settings-group-expanded|chevron-down|拆分式 JSON 设置编辑器中已展开区域的图标。|
|<i class="codicon codicon-gear"></i>|settings-more-action|gear|设置 UI 中“更多操作”操作的图标。|
|<i class="codicon codicon-close"></i>|settings-remove|close|设置 UI 中“删除”操作的图标。|
|<i class="codicon codicon-sync"></i>|settings-sync-view-icon|sync|设置同步视图的视图图标。|
|<i class="codicon codicon-settings-gear"></i>|settings-view-bar-icon|settings-gear|视图栏中的设置图标。|
|<i class="codicon codicon-source-control"></i>|source-control-view-icon|source-control|源代码管理视图的视图图标。|
|<i class="codicon codicon-chevron-right"></i>|suggest-more-info|chevron-right|建议小部件中“更多信息”的图标。|
|<i class="codicon codicon-gear"></i>|tasks-list-configure|gear|任务选择列表中的配置图标。|
|<i class="codicon codicon-close"></i>|tasks-remove|close|任务选择列表中删除的图标。|
|<i class="codicon codicon-trash"></i>|terminal-kill|trash|终止终端实例的图标。|
|<i class="codicon codicon-add"></i>|terminal-new|add|创建新终端实例的图标。|
|<i class="codicon codicon-gear"></i>|terminal-rename|gear|终端快捷菜单中重命名的图标。|
|<i class="codicon codicon-terminal"></i>|terminal-view-icon|terminal|终端视图的视图图标。|
|<i class="codicon codicon-beaker"></i>|test-view-icon|beaker|测试视图的视图图标。|
|<i class="codicon codicon-close"></i>|testing-cancel-icon|close|取消正在进行的测试运行的图标。|
|<i class="codicon codicon-debug-alt"></i>|testing-debug-icon|debug-alt|“调试测试”操作的图标。|
|<i class="codicon codicon-warning"></i>|testing-error-icon|warning|为出错的测试显示的图标。|
|<i class="codicon codicon-close"></i>|testing-failed-icon|close|为失败的测试显示的图标。|
|<i class="codicon codicon-pass"></i>|testing-passed-icon|pass|为通过的测试显示的图标。|
|<i class="codicon codicon-watch"></i>|testing-queued-icon|watch|为排队中的测试显示的图标。|
|<i class="codicon codicon-run-all"></i>|testing-run-all-icon|run-all|“运行所有测试”操作的图标。|
|<i class="codicon codicon-run"></i>|testing-run-icon|run|“运行测试”操作的图标。|
|<i class="codicon codicon-list-tree"></i>|testing-show-as-list-icon|list-tree|测试资源管理器不以树形式显示（以列表显示）时显示的图标。|
|<i class="codicon codicon-debug-step-over"></i>|testing-skipped-icon|debug-step-over|为跳过的测试显示的图标。|
|<i class="codicon codicon-circle-outline"></i>|testing-unset-icon|circle-outline|为处于未设置状态的测试显示的图标。|
|<i class="codicon codicon-history"></i>|timeline-open|history|“打开时间线”操作的图标。|
|<i class="codicon codicon-pin"></i>|timeline-pin|pin|“固定时间线”操作的图标。|
|<i class="codicon codicon-refresh"></i>|timeline-refresh|refresh|“刷新时间线”操作的图标。|
|<i class="codicon codicon-pinned"></i>|timeline-unpin|pinned|“取消固定时间线”操作的图标。|
|<i class="codicon codicon-history"></i>|timeline-view-icon|history|时间线视图的视图图标。|
|<i class="codicon codicon-debug-alt"></i>|variables-view-icon|debug-alt|变量视图的视图图标。|
|<i class="codicon codicon-chevron-right"></i>|view-pane-container-collapsed|chevron-right|已折叠的视图窗格容器的图标。|
|<i class="codicon codicon-chevron-down"></i>|view-pane-container-expanded|chevron-down|已展开的视图窗格容器的图标。|
|<i class="codicon codicon-add"></i>|watch-expressions-add|add|监视视图中“添加”操作的图标。|
|<i class="codicon codicon-add"></i>|watch-expressions-add-function-breakpoint|add|监视视图中“添加函数断点”操作的图标。|
|<i class="codicon codicon-close-all"></i>|watch-expressions-remove-all|close-all|监视视图中“全部删除”操作的图标。|
|<i class="codicon codicon-debug-alt"></i>|watch-view-icon|debug-alt|监视视图的视图图标。|
|<i class="codicon codicon-close"></i>|widget-close|close|小部件中“关闭”操作的图标。|
|<i class="codicon codicon-shield"></i>|workspace-trust-editor-label-icon|shield|工作区信任编辑器标签的图标。|

> Codicon 库包含 VS Code 视图中使用的所有图标，以及一组实用的图标。
>
> VS Code 扩展可以在标签、视图和树中使用这些图标。

| 预览 | 标识符 |
| --- | --- |
|<i class="codicon codicon-account"></i>|account|
|<i class="codicon codicon-activate-breakpoints"></i>|activate-breakpoints|
|<i class="codicon codicon-add"></i>|add|
|<i class="codicon codicon-alert"></i>|alert|
|<i class="codicon codicon-archive"></i>|archive|
|<i class="codicon codicon-array"></i>|array|
|<i class="codicon codicon-arrow-both"></i>|arrow-both|
|<i class="codicon codicon-arrow-circle-down"></i>|arrow-circle-down|
|<i class="codicon codicon-arrow-circle-left"></i>|arrow-circle-left|
|<i class="codicon codicon-arrow-circle-right"></i>|arrow-circle-right|
|<i class="codicon codicon-arrow-circle-up"></i>|arrow-circle-up|
|<i class="codicon codicon-arrow-down"></i>|arrow-down|
|<i class="codicon codicon-arrow-left"></i>|arrow-left|
|<i class="codicon codicon-arrow-right"></i>|arrow-right|
|<i class="codicon codicon-arrow-small-down"></i>|arrow-small-down|
|<i class="codicon codicon-arrow-small-left"></i>|arrow-small-left|
|<i class="codicon codicon-arrow-small-right"></i>|arrow-small-right|
|<i class="codicon codicon-arrow-small-up"></i>|arrow-small-up|
|<i class="codicon codicon-arrow-swap"></i>|arrow-swap|
|<i class="codicon codicon-arrow-up"></i>|arrow-up|
|<i class="codicon codicon-azure-devops"></i>|azure-devops|
|<i class="codicon codicon-azure"></i>|azure|
|<i class="codicon codicon-beaker-stop"></i>|beaker-stop|
|<i class="codicon codicon-beaker"></i>|beaker|
|<i class="codicon codicon-bell"></i>|bell|
|<i class="codicon codicon-bell-dot"></i>|bell-dot|
|<i class="codicon codicon-bell-slash"></i>|bell-slash|
|<i class="codicon codicon-bell-slash-dot"></i>|bell-slash-dot|
|<i class="codicon codicon-bold"></i>|bold|
|<i class="codicon codicon-book"></i>|book|
|<i class="codicon codicon-bookmark"></i>|bookmark|
|<i class="codicon codicon-bracket-dot"></i>|bracket-dot|
|<i class="codicon codicon-bracket-error"></i>|bracket-error|
|<i class="codicon codicon-bracket"></i>|bracket|
|<i class="codicon codicon-briefcase"></i>|briefcase|
|<i class="codicon codicon-broadcast"></i>|broadcast|
|<i class="codicon codicon-browser"></i>|browser|
|<i class="codicon codicon-bug"></i>|bug|
|<i class="codicon codicon-calendar"></i>|calendar|
|<i class="codicon codicon-call-incoming"></i>|call-incoming|
|<i class="codicon codicon-call-outgoing"></i>|call-outgoing|
|<i class="codicon codicon-case-sensitive"></i>|case-sensitive|
|<i class="codicon codicon-check"></i>|check|
|<i class="codicon codicon-check-all"></i>|check-all|
|<i class="codicon codicon-checklist"></i>|checklist|
|<i class="codicon codicon-chevron-down"></i>|chevron-down|
|<i class="codicon codicon-chevron-left"></i>|chevron-left|
|<i class="codicon codicon-chevron-right"></i>|chevron-right|
|<i class="codicon codicon-chevron-up"></i>|chevron-up|
|<i class="codicon codicon-chip"></i>|chip|
|<i class="codicon codicon-chrome-close"></i>|chrome-close|
|<i class="codicon codicon-chrome-maximize"></i>|chrome-maximize|
|<i class="codicon codicon-chrome-minimize"></i>|chrome-minimize|
|<i class="codicon codicon-chrome-restore"></i>|chrome-restore|
|<i class="codicon codicon-circle-filled"></i>|circle-filled|
|<i class="codicon codicon-circle-large-filled"></i>|circle-large-filled|
|<i class="codicon codicon-circle-large-outline"></i>|circle-large-outline|
|<i class="codicon codicon-circle-outline"></i>|circle-outline|
|<i class="codicon codicon-circle-slash"></i>|circle-slash|
|<i class="codicon codicon-circuit-board"></i>|circuit-board|
|<i class="codicon codicon-clear-all"></i>|clear-all|
|<i class="codicon codicon-clippy"></i>|clippy|
|<i class="codicon codicon-clock"></i>|clock|
|<i class="codicon codicon-clone"></i>|clone|
|<i class="codicon codicon-close"></i>|close|
|<i class="codicon codicon-close-all"></i>|close-all|
|<i class="codicon codicon-close-dirty"></i>|close-dirty|
|<i class="codicon codicon-cloud"></i>|cloud|
|<i class="codicon codicon-cloud-download"></i>|cloud-download|
|<i class="codicon codicon-cloud-upload"></i>|cloud-upload|
|<i class="codicon codicon-code"></i>|code|
|<i class="codicon codicon-coffee"></i>|coffee|
|<i class="codicon codicon-collapse-all"></i>|collapse-all|
|<i class="codicon codicon-color-mode"></i>|color-mode|
|<i class="codicon codicon-combine"></i>|combine|
|<i class="codicon codicon-comment"></i>|comment|
|<i class="codicon codicon-comment-add"></i>|comment-add|
|<i class="codicon codicon-comment-discussion"></i>|comment-discussion|
|<i class="codicon codicon-comment-draft"></i>|comment-draft|
|<i class="codicon codicon-comment-unresolved"></i>|comment-unresolved|
|<i class="codicon codicon-compare-changes"></i>|compare-changes|
|<i class="codicon codicon-compass-active"></i>|compass-active|
|<i class="codicon codicon-compass-dot"></i>|compass-dot|
|<i class="codicon codicon-compass"></i>|compass|
|<i class="codicon codicon-console"></i>|console|
|<i class="codicon codicon-copilot"></i>|copilot|
|<i class="codicon codicon-copy"></i>|copy|
|<i class="codicon codicon-credit-card"></i>|credit-card|
|<i class="codicon codicon-dash"></i>|dash|
|<i class="codicon codicon-dashboard"></i>|dashboard|
|<i class="codicon codicon-database"></i>|database|
|<i class="codicon codicon-debug-all"></i>|debug-all|
|<i class="codicon codicon-debug"></i>|debug|
|<i class="codicon codicon-debug-alt"></i>|debug-alt|
|<i class="codicon codicon-debug-alt-small"></i>|debug-alt-small|
|<i class="codicon codicon-debug-breakpoint"></i>|debug-breakpoint|
|<i class="codicon codicon-debug-breakpoint-conditional"></i>|debug-breakpoint-conditional|
|<i class="codicon codicon-debug-breakpoint-conditional-disabled"></i>|debug-breakpoint-conditional-disabled|
|<i class="codicon codicon-debug-breakpoint-conditional-unverified"></i>|debug-breakpoint-conditional-unverified|
|<i class="codicon codicon-debug-breakpoint-data"></i>|debug-breakpoint-data|
|<i class="codicon codicon-debug-breakpoint-data-disabled"></i>|debug-breakpoint-data-disabled|
|<i class="codicon codicon-debug-breakpoint-data-unverified"></i>|debug-breakpoint-data-unverified|
|<i class="codicon codicon-debug-breakpoint-disabled"></i>|debug-breakpoint-disabled|
|<i class="codicon codicon-debug-breakpoint-function"></i>|debug-breakpoint-function|
|<i class="codicon codicon-debug-breakpoint-function-disabled"></i>|debug-breakpoint-function-disabled|
|<i class="codicon codicon-debug-breakpoint-function-unverified"></i>|debug-breakpoint-function-unverified|
|<i class="codicon codicon-debug-breakpoint-log"></i>|debug-breakpoint-log|
|<i class="codicon codicon-debug-breakpoint-log-disabled"></i>|debug-breakpoint-log-disabled|
|<i class="codicon codicon-debug-breakpoint-log-unverified"></i>|debug-breakpoint-log-unverified|
|<i class="codicon codicon-debug-breakpoint-unsupported"></i>|debug-breakpoint-unsupported|
|<i class="codicon codicon-debug-breakpoint-unverified"></i>|debug-breakpoint-unverified|
|<i class="codicon codicon-debug-console"></i>|debug-console|
|<i class="codicon codicon-debug-continue-small"></i>|debug-continue-small|
|<i class="codicon codicon-debug-continue"></i>|debug-continue|
|<i class="codicon codicon-debug-coverage"></i>|debug-coverage|
|<i class="codicon codicon-debug-disconnect"></i>|debug-disconnect|
|<i class="codicon codicon-debug-hint"></i>|debug-hint|
|<i class="codicon codicon-debug-line-by-line"></i>|debug-line-by-line|
|<i class="codicon codicon-debug-pause"></i>|debug-pause|
|<i class="codicon codicon-debug-rerun"></i>|debug-rerun|
|<i class="codicon codicon-debug-restart"></i>|debug-restart|
|<i class="codicon codicon-debug-restart-frame"></i>|debug-restart-frame|
|<i class="codicon codicon-debug-reverse-continue"></i>|debug-reverse-continue|
|<i class="codicon codicon-debug-stackframe"></i>|debug-stackframe|
|<i class="codicon codicon-debug-stackframe-active"></i>|debug-stackframe-active|
|<i class="codicon codicon-debug-stackframe-dot"></i>|debug-stackframe-dot|
|<i class="codicon codicon-debug-stackframe-focused"></i>|debug-stackframe-focused|
|<i class="codicon codicon-debug-start"></i>|debug-start|
|<i class="codicon codicon-debug-step-back"></i>|debug-step-back|
|<i class="codicon codicon-debug-step-into"></i>|debug-step-into|
|<i class="codicon codicon-debug-step-out"></i>|debug-step-out|
|<i class="codicon codicon-debug-step-over"></i>|debug-step-over|
|<i class="codicon codicon-debug-stop"></i>|debug-stop|
|<i class="codicon codicon-desktop-download"></i>|desktop-download|
|<i class="codicon codicon-device-camera"></i>|device-camera|
|<i class="codicon codicon-device-camera-video"></i>|device-camera-video|
|<i class="codicon codicon-device-desktop"></i>|device-desktop|
|<i class="codicon codicon-device-mobile"></i>|device-mobile|
|<i class="codicon codicon-diff"></i>|diff|
|<i class="codicon codicon-diff-added"></i>|diff-added|
|<i class="codicon codicon-diff-ignored"></i>|diff-ignored|
|<i class="codicon codicon-diff-modified"></i>|diff-modified|
|<i class="codicon codicon-diff-removed"></i>|diff-removed|
|<i class="codicon codicon-diff-renamed"></i>|diff-renamed|
|<i class="codicon codicon-discard"></i>|discard|
|<i class="codicon codicon-edit"></i>|edit|
|<i class="codicon codicon-editor-layout"></i>|editor-layout|
|<i class="codicon codicon-ellipsis"></i>|ellipsis|
|<i class="codicon codicon-empty-window"></i>|empty-window|
|<i class="codicon codicon-error-small"></i>|error-small|
|<i class="codicon codicon-error"></i>|error|
|<i class="codicon codicon-exclude"></i>|exclude|
|<i class="codicon codicon-expand-all"></i>|expand-all|
|<i class="codicon codicon-export"></i>|export|
|<i class="codicon codicon-extensions"></i>|extensions|
|<i class="codicon codicon-eye"></i>|eye|
|<i class="codicon codicon-eye-closed"></i>|eye-closed|
|<i class="codicon codicon-eye-unwatch"></i>|eye-unwatch|
|<i class="codicon codicon-eye-watch"></i>|eye-watch|
|<i class="codicon codicon-feedback"></i>|feedback|
|<i class="codicon codicon-file"></i>|file|
|<i class="codicon codicon-file-add"></i>|file-add|
|<i class="codicon codicon-file-binary"></i>|file-binary|
|<i class="codicon codicon-file-code"></i>|file-code|
|<i class="codicon codicon-file-directory"></i>|file-directory|
|<i class="codicon codicon-file-directory-create"></i>|file-directory-create|
|<i class="codicon codicon-file-media"></i>|file-media|
|<i class="codicon codicon-file-pdf"></i>|file-pdf|
|<i class="codicon codicon-file-submodule"></i>|file-submodule|
|<i class="codicon codicon-file-symlink-directory"></i>|file-symlink-directory|
|<i class="codicon codicon-file-symlink-file"></i>|file-symlink-file|
|<i class="codicon codicon-file-text"></i>|file-text|
|<i class="codicon codicon-file-zip"></i>|file-zip|
|<i class="codicon codicon-files"></i>|files|
|<i class="codicon codicon-filter-filled"></i>|filter-filled|
|<i class="codicon codicon-filter"></i>|filter|
|<i class="codicon codicon-flame"></i>|flame|
|<i class="codicon codicon-fold"></i>|fold|
|<i class="codicon codicon-fold-down"></i>|fold-down|
|<i class="codicon codicon-fold-up"></i>|fold-up|
|<i class="codicon codicon-folder"></i>|folder|
|<i class="codicon codicon-folder-active"></i>|folder-active|
|<i class="codicon codicon-folder-library"></i>|folder-library|
|<i class="codicon codicon-folder-opened"></i>|folder-opened|
|<i class="codicon codicon-game"></i>|game|
|<i class="codicon codicon-gather"></i>|gather|
|<i class="codicon codicon-gear"></i>|gear|
|<i class="codicon codicon-gift"></i>|gift|
|<i class="codicon codicon-gist"></i>|gist|
|<i class="codicon codicon-gist-fork"></i>|gist-fork|
|<i class="codicon codicon-gist-new"></i>|gist-new|
|<i class="codicon codicon-gist-private"></i>|gist-private|
|<i class="codicon codicon-gist-secret"></i>|gist-secret|
|<i class="codicon codicon-git-branch"></i>|git-branch|
|<i class="codicon codicon-git-branch-create"></i>|git-branch-create|
|<i class="codicon codicon-git-branch-delete"></i>|git-branch-delete|
|<i class="codicon codicon-git-commit"></i>|git-commit|
|<i class="codicon codicon-git-compare"></i>|git-compare|
|<i class="codicon codicon-git-fetch"></i>|git-fetch|
|<i class="codicon codicon-git-fork-private"></i>|git-fork-private|
|<i class="codicon codicon-git-merge"></i>|git-merge|
|<i class="codicon codicon-git-pull-request"></i>|git-pull-request|
|<i class="codicon codicon-git-pull-request-abandoned"></i>|git-pull-request-abandoned|
|<i class="codicon codicon-git-pull-request-closed"></i>|git-pull-request-closed|
|<i class="codicon codicon-git-pull-request-create"></i>|git-pull-request-create|
|<i class="codicon codicon-git-pull-request-draft"></i>|git-pull-request-draft|
|<i class="codicon codicon-git-pull-request-new-changes"></i>|git-pull-request-new-changes|
|<i class="codicon codicon-git-pull-request-go-to-changes"></i>|git-pull-request-go-to-changes|
|<i class="codicon codicon-github"></i>|github|
|<i class="codicon codicon-github-action"></i>|github-action|
|<i class="codicon codicon-github-alt"></i>|github-alt|
|<i class="codicon codicon-github-inverted"></i>|github-inverted|
|<i class="codicon codicon-globe"></i>|globe|
|<i class="codicon codicon-go-to-file"></i>|go-to-file|
|<i class="codicon codicon-grabber"></i>|grabber|
|<i class="codicon codicon-graph"></i>|graph|
|<i class="codicon codicon-graph-left"></i>|graph-left|
|<i class="codicon codicon-graph-line"></i>|graph-line|
|<i class="codicon codicon-graph-scatter"></i>|graph-scatter|
|<i class="codicon codicon-gripper"></i>|gripper|
|<i class="codicon codicon-group-by-ref-type"></i>|group-by-ref-type|
|<i class="codicon codicon-heart"></i>|heart|
|<i class="codicon codicon-history"></i>|history|
|<i class="codicon codicon-home"></i>|home|
|<i class="codicon codicon-horizontal-rule"></i>|horizontal-rule|
|<i class="codicon codicon-hubot"></i>|hubot|
|<i class="codicon codicon-inbox"></i>|inbox|
|<i class="codicon codicon-indent"></i>|indent|
|<i class="codicon codicon-info"></i>|info|
|<i class="codicon codicon-insert"></i>|insert|
|<i class="codicon codicon-inspect"></i>|inspect|
|<i class="codicon codicon-issue-closed"></i>|issue-closed|
|<i class="codicon codicon-issue-draft"></i>|issue-draft|
|<i class="codicon codicon-issue-opened"></i>|issue-opened|
|<i class="codicon codicon-issue-reopened"></i>|issue-reopened|
|<i class="codicon codicon-issues"></i>|issues|
|<i class="codicon codicon-italic"></i>|italic|
|<i class="codicon codicon-jersey"></i>|jersey|
|<i class="codicon codicon-json"></i>|json|
|<i class="codicon codicon-kebab-horizontal"></i>|kebab-horizontal|
|<i class="codicon codicon-kebab-vertical"></i>|kebab-vertical|
|<i class="codicon codicon-key"></i>|key|
|<i class="codicon codicon-keyboard"></i>|keyboard|
|<i class="codicon codicon-law"></i>|law|
|<i class="codicon codicon-layers-active"></i>|layers-active|
|<i class="codicon codicon-layers-dot"></i>|layers-dot|
|<i class="codicon codicon-layers"></i>|layers|
|<i class="codicon codicon-layout-activitybar-left"></i>|layout-activitybar-left|
|<i class="codicon codicon-layout-activitybar-right"></i>|layout-activitybar-right|
|<i class="codicon codicon-layout-centered"></i>|layout-centered|
|<i class="codicon codicon-layout-menubar"></i>|layout-menubar|
|<i class="codicon codicon-layout-panel-center"></i>|layout-panel-center|
|<i class="codicon codicon-layout-panel-justify"></i>|layout-panel-justify|
|<i class="codicon codicon-layout-panel-left"></i>|layout-panel-left|
|<i class="codicon codicon-layout-panel-right"></i>|layout-panel-right|
|<i class="codicon codicon-layout-panel"></i>|layout-panel|
|<i class="codicon codicon-layout-sidebar-left"></i>|layout-sidebar-left|
|<i class="codicon codicon-layout-sidebar-right"></i>|layout-sidebar-right|
|<i class="codicon codicon-layout-statusbar"></i>|layout-statusbar|
|<i class="codicon codicon-layout"></i>|layout|
|<i class="codicon codicon-library"></i>|library|
|<i class="codicon codicon-light-bulb"></i>|light-bulb|
|<i class="codicon codicon-lightbulb"></i>|lightbulb|
|<i class="codicon codicon-lightbulb-autofix"></i>|lightbulb-autofix|
|<i class="codicon codicon-link"></i>|link|
|<i class="codicon codicon-link-external"></i>|link-external|
|<i class="codicon codicon-list-filter"></i>|list-filter|
|<i class="codicon codicon-list-flat"></i>|list-flat|
|<i class="codicon codicon-list-ordered"></i>|list-ordered|
|<i class="codicon codicon-list-selection"></i>|list-selection|
|<i class="codicon codicon-list-tree"></i>|list-tree|
|<i class="codicon codicon-list-unordered"></i>|list-unordered|
|<i class="codicon codicon-live-share"></i>|live-share|
|<i class="codicon codicon-loading"></i>|loading|
|<i class="codicon codicon-location"></i>|location|
|<i class="codicon codicon-lock-small"></i>|lock-small|
|<i class="codicon codicon-lock"></i>|lock|
|<i class="codicon codicon-log-in"></i>|log-in|
|<i class="codicon codicon-log-out"></i>|log-out|
|<i class="codicon codicon-logo-github"></i>|logo-github|
|<i class="codicon codicon-magnet"></i>|magnet|
|<i class="codicon codicon-mail"></i>|mail|
|<i class="codicon codicon-mail-read"></i>|mail-read|
|<i class="codicon codicon-mail-reply"></i>|mail-reply|
|<i class="codicon codicon-mark-github"></i>|mark-github|
|<i class="codicon codicon-markdown"></i>|markdown|
|<i class="codicon codicon-megaphone"></i>|megaphone|
|<i class="codicon codicon-mention"></i>|mention|
|<i class="codicon codicon-menu"></i>|menu|
|<i class="codicon codicon-merge"></i>|merge|
|<i class="codicon codicon-mic"></i>|mic|
|<i class="codicon codicon-mic-filled"></i>|mic-filled|
|<i class="codicon codicon-microscope"></i>|microscope|
|<i class="codicon codicon-milestone"></i>|milestone|
|<i class="codicon codicon-mirror"></i>|mirror|
|<i class="codicon codicon-mirror-private"></i>|mirror-private|
|<i class="codicon codicon-mirror-public"></i>|mirror-public|
|<i class="codicon codicon-more"></i>|more|
|<i class="codicon codicon-mortar-board"></i>|mortar-board|
|<i class="codicon codicon-move"></i>|move|
|<i class="codicon codicon-multiple-windows"></i>|multiple-windows|
|<i class="codicon codicon-music"></i>|music|
|<i class="codicon codicon-mute"></i>|mute|
|<i class="codicon codicon-new-file"></i>|new-file|
|<i class="codicon codicon-new-folder"></i>|new-folder|
|<i class="codicon codicon-newline"></i>|newline|
|<i class="codicon codicon-no-newline"></i>|no-newline|
|<i class="codicon codicon-note"></i>|note|
|<i class="codicon codicon-notebook"></i>|notebook|
|<i class="codicon codicon-notebook-template"></i>|notebook-template|
|<i class="codicon codicon-octoface"></i>|octoface|
|<i class="codicon codicon-open-preview"></i>|open-preview|
|<i class="codicon codicon-organization"></i>|organization|
|<i class="codicon codicon-organization-filled"></i>|organization-filled|
|<i class="codicon codicon-organization-outline"></i>|organization-outline|
|<i class="codicon codicon-output"></i>|output|
|<i class="codicon codicon-package"></i>|package|
|<i class="codicon codicon-paintcan"></i>|paintcan|
|<i class="codicon codicon-pass"></i>|pass|
|<i class="codicon codicon-pass-filled"></i>|pass-filled|
|<i class="codicon codicon-pencil"></i>|pencil|
|<i class="codicon codicon-person"></i>|person|
|<i class="codicon codicon-person-add"></i>|person-add|
|<i class="codicon codicon-person-filled"></i>|person-filled|
|<i class="codicon codicon-person-follow"></i>|person-follow|
|<i class="codicon codicon-person-outline"></i>|person-outline|
|<i class="codicon codicon-pie-chart"></i>|pie-chart|
|<i class="codicon codicon-piano"></i>|piano|
|<i class="codicon codicon-pin"></i>|pin|
|<i class="codicon codicon-pinned"></i>|pinned|
|<i class="codicon codicon-pinned-dirty"></i>|pinned-dirty|
|<i class="codicon codicon-play"></i>|play|
|<i class="codicon codicon-play-circle"></i>|play-circle|
|<i class="codicon codicon-plug"></i>|plug|
|<i class="codicon codicon-plus"></i>|plus|
|<i class="codicon codicon-preserve-case"></i>|preserve-case|
|<i class="codicon codicon-preview"></i>|preview|
|<i class="codicon codicon-primitive-dot"></i>|primitive-dot|
|<i class="codicon codicon-primitive-square"></i>|primitive-square|
|<i class="codicon codicon-project"></i>|project|
|<i class="codicon codicon-pulse"></i>|pulse|
|<i class="codicon codicon-question"></i>|question|
|<i class="codicon codicon-quote"></i>|quote|
|<i class="codicon codicon-radio-tower"></i>|radio-tower|
|<i class="codicon codicon-reactions"></i>|reactions|
|<i class="codicon codicon-record"></i>|record|
|<i class="codicon codicon-record-keys"></i>|record-keys|
|<i class="codicon codicon-record-small"></i>|record-small|
|<i class="codicon codicon-redo"></i>|redo|
|<i class="codicon codicon-references"></i>|references|
|<i class="codicon codicon-refresh"></i>|refresh|
|<i class="codicon codicon-regex"></i>|regex|
|<i class="codicon codicon-remote"></i>|remote|
|<i class="codicon codicon-remote-explorer"></i>|remote-explorer|
|<i class="codicon codicon-remove"></i>|remove|
|<i class="codicon codicon-remove-close"></i>|remove-close|
|<i class="codicon codicon-repl"></i>|repl|
|<i class="codicon codicon-replace"></i>|replace|
|<i class="codicon codicon-replace-all"></i>|replace-all|
|<i class="codicon codicon-reply"></i>|reply|
|<i class="codicon codicon-repo"></i>|repo|
|<i class="codicon codicon-repo-clone"></i>|repo-clone|
|<i class="codicon codicon-repo-create"></i>|repo-create|
|<i class="codicon codicon-repo-delete"></i>|repo-delete|
|<i class="codicon codicon-repo-force-push"></i>|repo-force-push|
|<i class="codicon codicon-repo-forked"></i>|repo-forked|
|<i class="codicon codicon-repo-pull"></i>|repo-pull|
|<i class="codicon codicon-repo-push"></i>|repo-push|
|<i class="codicon codicon-repo-sync"></i>|repo-sync|
|<i class="codicon codicon-report"></i>|report|
|<i class="codicon codicon-request-changes"></i>|request-changes|
|<i class="codicon codicon-rocket"></i>|rocket|
|<i class="codicon codicon-root-folder"></i>|root-folder|
|<i class="codicon codicon-root-folder-opened"></i>|root-folder-opened|
|<i class="codicon codicon-rss"></i>|rss|
|<i class="codicon codicon-ruby"></i>|ruby|
|<i class="codicon codicon-run"></i>|run|
|<i class="codicon codicon-run-all"></i>|run-all|
|<i class="codicon codicon-run-above"></i>|run-above|
|<i class="codicon codicon-run-below"></i>|run-below|
|<i class="codicon codicon-run-errors"></i>|run-errors|
|<i class="codicon codicon-save"></i>|save|
|<i class="codicon codicon-save-all"></i>|save-all|
|<i class="codicon codicon-save-as"></i>|save-as|
|<i class="codicon codicon-screen-full"></i>|screen-full|
|<i class="codicon codicon-screen-normal"></i>|screen-normal|
|<i class="codicon codicon-search"></i>|search|
|<i class="codicon codicon-search-save"></i>|search-save|
|<i class="codicon codicon-search-stop"></i>|search-stop|
|<i class="codicon codicon-search-fuzzy"></i>|search-fuzzy|
|<i class="codicon codicon-selection"></i>|selection|
|<i class="codicon codicon-send"></i>|send|
|<i class="codicon codicon-server"></i>|server|
|<i class="codicon codicon-server-environment"></i>|server-environment|
|<i class="codicon codicon-server-process"></i>|server-process|
|<i class="codicon codicon-settings"></i>|settings|
|<i class="codicon codicon-settings-gear"></i>|settings-gear|
|<i class="codicon codicon-shield"></i>|shield|
|<i class="codicon codicon-sign-in"></i>|sign-in|
|<i class="codicon codicon-sign-out"></i>|sign-out|
|<i class="codicon codicon-smiley"></i>|smiley|
|<i class="codicon codicon-snake"></i>|snake|
|<i class="codicon codicon-sparkle"></i>|sparkle|
|<i class="codicon codicon-sort-precedence"></i>|sort-precedence|
|<i class="codicon codicon-source-control"></i>|source-control|
|<i class="codicon codicon-split-horizontal"></i>|split-horizontal|
|<i class="codicon codicon-split-vertical"></i>|split-vertical|
|<i class="codicon codicon-squirrel"></i>|squirrel|
|<i class="codicon codicon-star"></i>|star|
|<i class="codicon codicon-star-add"></i>|star-add|
|<i class="codicon codicon-star-delete"></i>|star-delete|
|<i class="codicon codicon-star-empty"></i>|star-empty|
|<i class="codicon codicon-star-full"></i>|star-full|
|<i class="codicon codicon-star-half"></i>|star-half|
|<i class="codicon codicon-stop"></i>|stop|
|<i class="codicon codicon-stop-circle"></i>|stop-circle|
|<i class="codicon codicon-symbol-array"></i>|symbol-array|
|<i class="codicon codicon-symbol-boolean"></i>|symbol-boolean|
|<i class="codicon codicon-symbol-class"></i>|symbol-class|
|<i class="codicon codicon-symbol-color"></i>|symbol-color|
|<i class="codicon codicon-symbol-constant"></i>|symbol-constant|
|<i class="codicon codicon-symbol-constructor"></i>|symbol-constructor|
|<i class="codicon codicon-symbol-enum"></i>|symbol-enum|
|<i class="codicon codicon-symbol-enum-member"></i>|symbol-enum-member|
|<i class="codicon codicon-symbol-event"></i>|symbol-event|
|<i class="codicon codicon-symbol-field"></i>|symbol-field|
|<i class="codicon codicon-symbol-file"></i>|symbol-file|
|<i class="codicon codicon-symbol-folder"></i>|symbol-folder|
|<i class="codicon codicon-symbol-function"></i>|symbol-function|
|<i class="codicon codicon-symbol-interface"></i>|symbol-interface|
|<i class="codicon codicon-symbol-key"></i>|symbol-key|
|<i class="codicon codicon-symbol-keyword"></i>|symbol-keyword|
|<i class="codicon codicon-symbol-method"></i>|symbol-method|
|<i class="codicon codicon-symbol-misc"></i>|symbol-misc|
|<i class="codicon codicon-symbol-module"></i>|symbol-module|
|<i class="codicon codicon-symbol-namespace"></i>|symbol-namespace|
|<i class="codicon codicon-symbol-null"></i>|symbol-null|
|<i class="codicon codicon-symbol-number"></i>|symbol-number|
|<i class="codicon codicon-symbol-numeric"></i>|symbol-numeric|
|<i class="codicon codicon-symbol-object"></i>|symbol-object|
|<i class="codicon codicon-symbol-operator"></i>|symbol-operator|
|<i class="codicon codicon-symbol-package"></i>|symbol-package|
|<i class="codicon codicon-symbol-parameter"></i>|symbol-parameter|
|<i class="codicon codicon-symbol-property"></i>|symbol-property|
|<i class="codicon codicon-symbol-reference"></i>|symbol-reference|
|<i class="codicon codicon-symbol-ruler"></i>|symbol-ruler|
|<i class="codicon codicon-symbol-snippet"></i>|symbol-snippet|
|<i class="codicon codicon-symbol-string"></i>|symbol-string|
|<i class="codicon codicon-symbol-struct"></i>|symbol-struct|
|<i class="codicon codicon-symbol-structure"></i>|symbol-structure|
|<i class="codicon codicon-symbol-text"></i>|symbol-text|
|<i class="codicon codicon-symbol-type-parameter"></i>|symbol-type-parameter|
|<i class="codicon codicon-symbol-unit"></i>|symbol-unit|
|<i class="codicon codicon-symbol-value"></i>|symbol-value|
|<i class="codicon codicon-symbol-variable"></i>|symbol-variable|
|<i class="codicon codicon-sync"></i>|sync|
|<i class="codicon codicon-sync-ignored"></i>|sync-ignored|
|<i class="codicon codicon-tag-add"></i>|tag-add|
|<i class="codicon codicon-tag-remove"></i>|tag-remove|
|<i class="codicon codicon-tag"></i>|tag|
|<i class="codicon codicon-target"></i>|target|
|<i class="codicon codicon-tasklist"></i>|tasklist|
|<i class="codicon codicon-telescope"></i>|telescope|
|<i class="codicon codicon-terminal-bash"></i>|terminal-bash|
|<i class="codicon codicon-terminal-cmd"></i>|terminal-cmd|
|<i class="codicon codicon-terminal-debian"></i>|terminal-debian|
|<i class="codicon codicon-terminal-linux"></i>|terminal-linux|
|<i class="codicon codicon-terminal-powershell"></i>|terminal-powershell|
|<i class="codicon codicon-terminal-tmux"></i>|terminal-tmux|
|<i class="codicon codicon-terminal-ubuntu"></i>|terminal-ubuntu|
|<i class="codicon codicon-terminal"></i>|terminal|
|<i class="codicon codicon-text-size"></i>|text-size|
|<i class="codicon codicon-three-bars"></i>|three-bars|
|<i class="codicon codicon-thumbsdown"></i>|thumbsdown|
|<i class="codicon codicon-thumbsdown-filled"></i>|thumbsdown-filled|
|<i class="codicon codicon-thumbsup"></i>|thumbsup|
|<i class="codicon codicon-thumbsup-filled"></i>|thumbsup-filled|
|<i class="codicon codicon-tools"></i>|tools|
|<i class="codicon codicon-trash"></i>|trash|
|<i class="codicon codicon-trashcan"></i>|trashcan|
|<i class="codicon codicon-triangle-down"></i>|triangle-down|
|<i class="codicon codicon-triangle-left"></i>|triangle-left|
|<i class="codicon codicon-triangle-right"></i>|triangle-right|
|<i class="codicon codicon-triangle-up"></i>|triangle-up|
|<i class="codicon codicon-twitter"></i>|twitter|
|<i class="codicon codicon-type-hierarchy-sub"></i>|type-hierarchy|
|<i class="codicon codicon-type-hierarchy-sub"></i>|type-hierarchy-sub|
|<i class="codicon codicon-type-hierarchy-super"></i>|type-hierarchy-super|
|<i class="codicon codicon-unfold"></i>|unfold|
|<i class="codicon codicon-ungroup-by-ref-type"></i>|ungroup-by-ref-type|
|<i class="codicon codicon-unlock"></i>|unlock|
|<i class="codicon codicon-unmute"></i>|unmute|
|<i class="codicon codicon-unverified"></i>|unverified|
|<i class="codicon codicon-variable"></i>|variable|
|<i class="codicon codicon-verified-filled"></i>|verified-filled|
|<i class="codicon codicon-verified"></i>|verified|
|<i class="codicon codicon-versions"></i>|versions|
|<i class="codicon codicon-vm"></i>|vm|
|<i class="codicon codicon-vm-active"></i>|vm-active|
|<i class="codicon codicon-vm-connect"></i>|vm-connect|
|<i class="codicon codicon-vm-outline"></i>|vm-outline|
|<i class="codicon codicon-vm-running"></i>|vm-running|
|<i class="codicon codicon-vr"></i>|vr|
|<i class="codicon codicon-warning"></i>|warning|
|<i class="codicon codicon-watch"></i>|watch|
|<i class="codicon codicon-whitespace"></i>|whitespace|
|<i class="codicon codicon-whole-word"></i>|whole-word|
|<i class="codicon codicon-window"></i>|window|
|<i class="codicon codicon-word-wrap"></i>|word-wrap|
|<i class="codicon codicon-workspace-trusted"></i>|workspace-trusted|
|<i class="codicon codicon-workspace-unknown"></i>|workspace-unknown|
|<i class="codicon codicon-workspace-untrusted"></i>|workspace-untrusted|
|<i class="codicon codicon-wrench"></i>|wrench|
|<i class="codicon codicon-wrench-subaction"></i>|wrench-subaction|
|<i class="codicon codicon-x"></i>|x|
|<i class="codicon codicon-zap"></i>|zap|
|<i class="codicon codicon-zoom-in"></i>|zoom-in|
|<i class="codicon codicon-zoom-out"></i>|zoom-out|
</div>

**在扩展中选择图标的建议：** 优先使用 Codicon 中语义明确的图标（如 `refresh`、`add`、`trash`、`gear`、`play`、`debug-start`），与 VS Code 自身的界面保持一致，并且会自动适配用户的产品图标主题和颜色主题。只有确实找不到合适的图标时，才通过上面的 `icons` 贡献点或 SVG 文件提供自定义图标（视图容器、命令等也支持 `{ "light": "...", "dark": "..." }` 形式的 SVG 路径）。

---

## 本篇小结

```text
产品图标（Codicon，默认产品图标主题）≠ 文件图标（文件图标主题）

使用
  标签字符串：$(图标ID)，多个图标和文字可以混排，\$(...) 转义；MarkdownString 需 supportThemeIcons
  API：new vscode.ThemeIcon('图标ID')（可带 ThemeColor）
  package.json："icon": "$(图标ID)"
  动画：$(sync~spin) / $(loading~spin) / $(gear~spin)

自定义图标：contributes.icons { id: { description, default: { fontPath, fontCharacter } 或 已有图标 ID } }

两张表：产品图标 ID（按 UI 位置命名，指向默认 codicon）/ Codicon 库的全部图标 ID
预览列需要在官方网站或 Codicon 一览页查看
```
