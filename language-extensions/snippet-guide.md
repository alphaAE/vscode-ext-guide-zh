# 代码片段指南（Snippet Guide）

> 原文：[Snippet Guide](https://code.visualstudio.com/api/language-extensions/snippet-guide)
> 源文件：`microsoft/vscode-docs` → `api/language-extensions/snippet-guide.md`（DateApproved: 10/7/2026）

> [`contributes.snippets`](../references/contribution-points.md#contributes.snippets) 贡献点让你可以把代码片段打包进一个 VS Code 扩展，用于分享。

**代码片段（snippet）**是一段代码模板：输入一个简短的前缀（比如 `log`），从补全列表中选中后，就展开成一整段代码（比如 `console.log();`），光标还会自动停在需要填写的位置。

> [创建代码片段](https://code.visualstudio.com/docs/editing/userdefinedsnippets)主题包含了创建代码片段的全部信息。这篇指南 / 示例只展示如何把你自己的代码片段变成一个扩展来分享。建议的工作流程是：
>
> - 使用 `Snippets: Configure User Snippets` 命令创建并测试你的代码片段
> - 对代码片段满意后，把整个 JSON 文件复制到一个扩展文件夹中，比如 `snippets.json`
> - 把下面的代码片段贡献添加到你的 `package.json` 中

```json
{
  "contributes": {
    "snippets": [
      {
        "language": "javascript",
        "path": "./snippets.json"
      }
    ]
  }
}
```

**代码片段文件的格式（补充）**，`snippets.json` 中的每一项是一个代码片段：

```json
{
  "Print to console": {
    "prefix": "log",
    "body": [
      "console.log('$1');",
      "$2"
    ],
    "description": "输出日志到控制台"
  }
}
```

| 字段 | 含义 |
|---|---|
| 键名（`"Print to console"`） | 代码片段的名称 |
| `prefix` | 触发前缀：输入它时出现在补全列表中（也可以是数组，提供多个前缀） |
| `body` | 展开后的内容，数组中的每一项是一行 |
| `description` | 在补全列表中显示的说明 |

`body` 中的特殊语法：

| 语法 | 含义 |
|---|---|
| `$1`、`$2` | 制表位：展开后光标先停在 `$1`，按 `Tab` 跳到 `$2` |
| `$0` | 最终的光标位置 |
| `${1:默认值}` | 带默认文字的占位符，例如 `${1:name}` |
| `${1\|a,b,c\|}` | 下拉选择，在 a、b、c 中选一个 |
| `$TM_FILENAME` 等 | 内置变量，例如当前文件名 |

完整的语法见上面链接的“创建代码片段”文档。[调试器扩展](../extension-guides/debugger-extension.md) 中 `configurationSnippets` 用的也是这套语法。

`language` 指定代码片段对哪种语言生效（语言 ID，如 `javascript`、`typescript`、`python`）。想让一组代码片段同时用于多种语言，可以在 `snippets` 数组中写多项，指向同一个文件。

> **提示**：在 `package.json` 中加上下面的配置，把你的扩展标记为代码片段扩展：

```json
{
  "categories": ["Snippets"]
}
```

> 你可以在 [https://github.com/microsoft/vscode-extension-samples/tree/main/snippet-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/snippet-sample) 找到完整的源代码。

---

<a id="using-textmate-snippets"></a>
## 使用 TextMate 代码片段（Using TextMate snippets）

> 你也可以使用 [yo code](../get-started/your-first-extension.md) 扩展生成器，把 TextMate 代码片段（.tmSnippets）添加到你的 VS Code 中。生成器有一个 `New Code Snippets`（新建代码片段）选项，让你可以指向一个包含多个 .tmSnippets 文件的文件夹，它们会被打包进一个 VS Code 代码片段扩展。生成器也支持 Sublime 的代码片段（.sublime-snippets）。
>
> 生成器最终输出两个文件：一个扩展清单 `package.json`，其中包含把代码片段集成到 VS Code 中的元数据；还有一个 `snippets.json` 文件，其中包含转换为 VS Code 代码片段格式的代码片段。

```text
.
├── snippets                    // VS Code 集成
│   └── snippets.json           // 包含代码片段的 JSON 文件
└── package.json                // 扩展清单
```

> 把生成的 snippets 文件夹复制到你的 `.vscode/extensions` 文件夹下的一个新文件夹中，然后重启 VS Code。

最后一步是“手动安装”扩展的方式：`.vscode/extensions` 指的是用户目录下的扩展安装目录（Windows 上是 `%USERPROFILE%\.vscode\extensions`），不是项目中的 `.vscode` 文件夹。需要复制的是整个扩展文件夹（包括 `package.json`），而不只是 `snippets` 子文件夹。更常用的做法是像普通扩展一样按 `F5` 测试，再打包发布（见 [发布扩展](../working-with-extensions/publishing-extension.md)）。

---

## 本篇小结

| 步骤 | 做法 |
|---|---|
| 编写和测试 | 命令面板 **Snippets: Configure User Snippets**，在自己的用户代码片段中调好 |
| 放进扩展 | 复制成扩展中的 `snippets.json` |
| 声明 | `contributes.snippets`：`[{ "language": "语言 ID", "path": "./snippets.json" }]` |
| 分类 | `"categories": ["Snippets"]` |
| 迁移已有片段 | `yo code` → New Code Snippets，可以转换 TextMate、Sublime 格式 |
