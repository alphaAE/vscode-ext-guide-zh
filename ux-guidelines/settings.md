# 设置（Settings）

> 原文：[Settings](https://code.visualstudio.com/api/ux-guidelines/settings)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/settings.md`（DateApproved: 10/7/2026）

> [设置](../references/contribution-points.md#contributes.configuration)是用户配置你的扩展的方式。设置可以是输入框、布尔值、下拉列表、列表、键值对。如果你的扩展需要用户配置特定的设置，可以打开设置界面，并通过设置 ID 查询你的扩展设置。

**✔️ 应该做**

> - 为每个设置添加默认值
> - 为每个设置添加清晰的描述
> - 为复杂的设置链接到文档
> - 链接到相关的其他设置
> - 需要用户配置特定的设置时，链接到设置 ID

**❌ 不应该做**

> - 创建你自己的设置页面 / Webview
> - 编写冗长的描述

![设置](images/examples/settings.png)

> *这个示例使用设置 ID 链接到了一个特定的设置。*

**设置的类型决定了在设置界面中显示成什么样子：**

| `type` | 设置界面中显示为 |
|---|---|
| `string` | 输入框 |
| `boolean` | 复选框 |
| `string` + `enum` | 下拉列表 |
| `array` | 可增删条目的列表 |
| `object` | 键值对编辑器（复杂的对象会提示“在 settings.json 中编辑”） |

**规范对应的写法：**

```json
"contributes": {
  "configuration": {
    "title": "My Extension",
    "properties": {
      "myExtension.formatter": {
        "type": "string",
        "enum": ["prettier", "eslint"],
        "enumDescriptions": ["使用 Prettier 格式化", "使用 ESLint 修复"],
        "default": "prettier",
        "markdownDescription": "保存时使用的格式化工具。需要先启用 `#myExtension.formatOnSave#`。详见[文档](https://example.com/docs/format)。"
      },
      "myExtension.formatOnSave": {
        "type": "boolean",
        "default": false,
        "description": "保存文件时自动格式化"
      }
    }
  }
}
```

| 规则 | 写法 |
|---|---|
| 默认值 | 每个设置都写 `default` |
| 清晰、简短的描述 | `description`；需要链接或格式时用 `markdownDescription` |
| 链接到文档 | `markdownDescription` 中写普通的 Markdown 链接 |
| 链接到相关设置 | `markdownDescription` 中写 `` `#设置ID#` ``，在设置界面中会显示成一个可点击的链接，点击就跳到那个设置（这就是截图中示例的效果） |

**在代码中打开设置界面并定位到某个设置：**

```ts
vscode.commands.executeCommand('workbench.action.openSettings', 'myExtension.formatter');
```

第二个参数是搜索词，传设置 ID 就能直接定位到它。比如检测到用户没有配置必需的设置时，弹一条通知，带一个“去设置”的按钮，点击后执行这条命令。

**为什么不要自己做设置页面？** VS Code 的设置界面支持搜索、同步、用户 / 工作区两级设置、在 `settings.json` 中直接编辑，自己用 Webview 做的页面都没有这些功能，还会让用户在两个地方找设置。设置的读写方法见 [通用能力](../extension-capabilities/common-capabilities.md#configuration)。

---

<a id="links"></a>
## 链接（Links）

> - [配置贡献点](../references/contribution-points.md#contributes.configuration)
