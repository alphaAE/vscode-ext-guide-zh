# 上下文菜单（Context Menus）

> 原文：[Context Menus](https://code.visualstudio.com/api/ux-guidelines/context-menus)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/context-menus.md`（DateApproved: 10/7/2026）

> [菜单项](../references/contribution-points.md#contributes.menus)出现在视图、操作和右键菜单中。保持菜单分组的一致性很重要。如果你的扩展有与文件相关的操作，就（在合适的时候）把这些操作放在文件资源管理器的上下文菜单中。如果扩展有针对特定文件类型的操作，就只为这些条目显示它。

**✔️ 应该做**

> - 在上下文合适时显示操作
> - 把相似的操作归到一组
> - 把大组的操作放进子菜单

**❌ 不应该做**

> - 不加区分地为每个文件都显示操作

![上下文菜单](images/examples/context-menu.png)

> *这个示例把 **Copy GitHub Permalink**（复制 GitHub 永久链接）放在其他复制命令的旁边。这个操作只出现在来自 GitHub 仓库的文件上。*

**三条规则对应的写法：**

**1. 在上下文合适时显示**：用 `when` 子句限定文件类型。

```json
"menus": {
  "explorer/context": [
    { "command": "myExt.previewImage", "when": "resourceExtname =~ /\\.(png|jpg|svg)$/" }
  ]
}
```

这样只有右键图片文件时才会出现“预览图片”，右键其他文件不会看到它。

**2. 相似的操作归到一组**：用 `group` 把命令放进合适的分组。菜单中不同的组之间有分隔线。截图中的 “Copy GitHub Permalink” 就是放进了内置的“复制”那一组，和 “Copy Path”、“Copy Relative Path” 挨在一起。

```json
{ "command": "myExt.copyPermalink", "group": "6_copypath" }
```

内置菜单中各个组的名称（如资源管理器右键菜单中的 `6_copypath`）见 [贡献点参考](../references/contribution-points.md#contributes.menus) 中的“排序”说明。

**3. 操作多时放进子菜单**：用 `contributes.submenus` 定义一个子菜单，把扩展的一组命令收进去，右键菜单中只占一行。

```json
"contributes": {
  "submenus": [
    { "id": "myExt.tools", "label": "My Tools" }
  ],
  "menus": {
    "explorer/context": [
      { "submenu": "myExt.tools", "group": "navigation" }
    ],
    "myExt.tools": [
      { "command": "myExt.actionA" },
      { "command": "myExt.actionB" },
      { "command": "myExt.actionC" }
    ]
  }
}
```

---

<a id="links"></a>
## 链接（Links）

> - [上下文菜单 API 参考](../references/contribution-points.md#contributes.menus)
