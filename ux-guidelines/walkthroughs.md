# 演练（Walkthroughs）

> 原文：[Walkthroughs](https://code.visualstudio.com/api/ux-guidelines/walkthroughs)
> 源文件：`microsoft/vscode-docs` → `api/ux-guidelines/walkthroughs.md`（DateApproved: 10/7/2026）

> 演练通过一个包含丰富内容的多步骤清单，为引导用户上手扩展提供一致的体验。

**演练（Walkthrough）是什么？** 就是 VS Code 欢迎页（**Help: Welcome**）中的“入门”部分：左侧是一个步骤清单（比如“选择主题”“打开文件夹”“试试命令面板”），每完成一步就打上勾；右侧显示当前步骤的图片或说明。扩展可以通过 `contributes.walkthroughs` 贡献自己的演练，在用户安装扩展后引导他们上手。

**✔️ 应该做**

> - 使用有帮助的图片，为当前的演练步骤添加上下文。
> - 确保图片在不同的颜色主题下都能正常显示。如果可能，使用带有 VS Code [主题颜色](../references/theme-color.md)的 SVG。[Visual Studio Code Color Mapper](https://www.figma.com/community/plugin/1218260433851630449) 这个 Figma 插件可以轻松地为 SVG 应用主题。
> - 为每个步骤提供操作（例如“查看所有命令”）。尽可能使用动词。

**❌ 不应该做**

> - 在单个演练中添加过多的步骤
> - 添加多个演练，除非绝对必要

![演练的示例](images/examples/walkthrough.png)

**“图片在不同颜色主题下都能正常显示”** 是什么意思？如果截图是在深色主题下截的，浅色主题的用户看到会很突兀。用 SVG 绘制示意图，并在 SVG 中使用 VS Code 的主题颜色变量（如 `var(--vscode-editor-background)`，原理见 [Webview 指南](../extension-guides/webview.md#theming-webview-content)），图片就会自动跟随用户的主题变色。

**一个演练的基本结构（补充，完整字段见 [贡献点参考](../references/contribution-points.md#contributes.walkthroughs)）：**

```jsonc
"contributes": {
  "walkthroughs": [
    {
      "id": "myExt.getStarted",
      "title": "开始使用 My Extension",
      "description": "几步完成配置",
      "steps": [
        {
          "id": "connect",
          "title": "连接数据库",
          "description": "首先连接你的数据库。\n[连接数据库](command:myExt.connect)",   // 操作：用动词
          "media": { "svg": "media/connect.svg", "altText": "连接数据库的示意图" },
          "completionEvents": ["onCommand:myExt.connect"]   // 执行这个命令后，这一步自动打勾
        }
      ]
    }
  ]
}
```

每一步的 `description` 中，单独一行的命令链接会显示成按钮，和 [视图](./views.md#welcome-views) 中欢迎视图的写法一样。完整的示例见 [入门引导示例](https://github.com/microsoft/vscode-extension-samples/tree/main/getting-started-sample)。

---

<a id="links"></a>
## 链接（Links）

> - [演练贡献点](../references/contribution-points.md#contributes.walkthroughs)
> - [使用主题颜色 CSS 变量的 SVG 示例](https://github.com/microsoft/vscode/blob/a28eab68734e629c61590fae8c4b231c91f0eaaa/src/vs/workbench/contrib/welcomeGettingStarted/common/media/commandPalette.svg?short_path=52f2d6f#L11)
> - [Visual Studio Code Color Mapper](https://www.figma.com/community/plugin/1218260433851630449)
