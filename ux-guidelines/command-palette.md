# 命令面板（Command Palette）

> 原文：[Command Palette](https://code.visualstudio.com/api/ux-guidelines/command-palette)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/command-palette.md`（DateApproved: 10/7/2026）

> [命令面板](../references/contribution-points.md#contributes.commands)是所有命令所在的地方。给命令起恰当的名称很重要，这样用户才能轻松地找到它们。

**✔️ 应该做**

> - 在合适的地方添加快捷键
> - 为命令使用清晰的名称
> - 把命令归入同一个类别（category）

**❌ 不应该做**

> - 覆盖已有的快捷键
> - 在命令名称中使用 emoji

![命令面板](images/examples/command-palette.png)

> *这个示例中的命令都显示了一个清晰的 `category` 前缀，例如 “GitHub Issues”。*

**逐条解释：**

| 规则 | 做法 |
|---|---|
| 清晰的名称 | “动词 + 名词”的形式，如 `Create Issue`，见 [命令指南](../extension-guides/command.md#naming-conventions) 中的命名规范 |
| 同一个类别 | 给扩展的所有命令设置相同的 `category`，命令面板中显示为 `GitHub Issues: Create Issue`。用户输入类别名，就能列出这个扩展的全部命令 |
| 合适时添加快捷键 | 只给最常用的一两个命令配快捷键（`contributes.keybindings`，见 [通用能力](../extension-capabilities/common-capabilities.md#keybinding)） |
| 不要覆盖已有的快捷键 | 用户已经习惯了 `Ctrl+S`、`Ctrl+P` 等快捷键。选择组合键前，先在“键盘快捷方式”面板中搜索，确认没有被占用 |

```json
"commands": [
  { "command": "myExt.createIssue", "title": "Create Issue", "category": "My Issues" },
  { "command": "myExt.refresh",     "title": "Refresh",      "category": "My Issues" }
]
```

另外，不适合从命令面板调用的命令（比如需要文件参数、只用于右键菜单的命令），应该用 `menus.commandPalette` 加 `"when": "false"` 把它们隐藏起来（见 [命令指南](../extension-guides/command.md#controlling-when-a-command-shows-up-in-the-command-palette)），避免命令面板中出现用户执行了也没反应的命令。

---

<a id="links"></a>
## 链接（Links）

> - [命令 API 参考](../references/contribution-points.md#contributes.commands)
> - [命令扩展指南](../extension-guides/command.md)
> - [Hello World 扩展示例](https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-sample)
