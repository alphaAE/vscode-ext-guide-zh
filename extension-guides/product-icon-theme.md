# 产品图标主题（Product Icon Theme）

> 原文：[Product Icon Theme](https://code.visualstudio.com/api/extension-guides/product-icon-theme)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/product-icon-theme.md`（DateApproved: 10/7/2026）

> VS Code 包含一组内置图标，它们用在视图和编辑器中，也可以在悬停提示、状态栏中引用，甚至扩展也可以引用它们。例如筛选操作按钮中的图标和视图图标、状态栏中的图标、断点图标，以及树和编辑器中的折叠图标。
>
> 产品图标主题让扩展可以重新定义这些图标，给 VS Code 一个自定义的外观。产品图标主题不涵盖文件图标（由文件图标主题负责）和扩展贡献的图标。
>
> VS Code 要求这些图标以图标字体中的字形（glyph）来定义，并且（目前）限制产品图标只能由一种颜色组成。图标使用的颜色取决于它显示的位置，由当前的颜色主题定义。

这些内置图标就是前面多次提到的 **codicon**，比如状态栏项中的 `$(rocket)`、命令图标中的 `$(refresh)`。完整的图标列表见 [标签中的图标](../references/icons-in-labels.md#icon-listing)。

三种主题的分工再回顾一下（详见 [主题](../extension-capabilities/theming.md)）：

| 主题 | 管什么图标 | 颜色由谁决定 |
|---|---|---|
| 文件图标主题 | 文件、文件夹前面的图标 | 图标主题自己（可以多色） |
| **产品图标主题** | VS Code 自身界面的图标（codicon） | **颜色主题**（只能单色） |
| 不受主题控制 | 扩展自己贡献的图标 | 扩展 |

**为什么只能单色、颜色由颜色主题决定？** 同一个图标在不同位置要显示不同的颜色：活动栏中选中的图标是亮的，未选中的是暗的；错误图标是红的，警告图标是黄的。只有把图标做成单色的字形，VS Code 才能根据所在位置和颜色主题自由地给它着色，就像给文字设置颜色一样。

---

<a id="adding-a-new-product-icon-theme"></a>
## 添加新的产品图标主题（Adding a new product icon theme）

> 要定义你自己的产品图标主题，首先创建一个 VS Code 扩展，然后在扩展的 `package.json` 中添加 `productIconThemes` 贡献点。

```json
{
  "contributes": {
    "productIconThemes": [
      {
        "id": "aliensAreBack",
        "label": "Aliens Are Back",
        "path": "./producticons/aliens-product-icon-theme.json"
      }
    ]
  }
}
```

> `id` 是产品图标主题的标识符。它会用在设置中，所以要让它既唯一又可读。`label` 显示在产品图标主题选择器的下拉列表中。`path` 指向扩展中定义图标集的文件。如果你的文件名符合 `*product-icon-theme.json` 的命名规则，在 VS Code 中编辑产品图标主题文件时，就能获得补全支持和悬停提示。

结构和 [文件图标主题](./file-icon-theme.md) 的 `iconThemes` 完全一样。用户选择主题后，设置中保存为 `"workbench.productIconTheme": "aliensAreBack"`。

---

<a id="product-icon-definition-file"></a>
## 产品图标定义文件（Product icon definition file）

> 产品图标定义文件是一个 JSON 文件，定义一个或多个图标字体，以及一组图标定义。

<a id="font-definitions"></a>
### 字体定义（Font definitions）

> `fonts` 部分让你可以声明任意数量想要使用的字形字体，但必须至少定义一个字体。
>
> 之后可以在图标定义中引用这些字体。如果某个图标定义没有指定字体 ID，就会使用第一个声明的字体作为默认字体。
>
> 把字体文件复制到你的扩展中，并相应地设置路径。
>
> 建议使用 [WOFF](https://developer.mozilla.org/docs/Web/Guide/WOFF) 字体。
>
> - 把格式设为 'woff'。
> - weight（字重）属性的取值[在这里](https://developer.mozilla.org/docs/Web/CSS/font-weight#Values)定义。
> - style（样式）属性的取值[在这里](https://developer.mozilla.org/docs/Web/CSS/@font-face/font-style#Values)定义。

```json
{
  "fonts": [
    {
      "id": "alien-font",
      "src": [
        {
          "path": "./alien.woff",
          "format": "woff"
        }
      ],
      "weight": "normal",
      "style": "normal"
    }
  ]
}
```

和文件图标主题的区别：文件图标主题可以用图片（SVG），字体是可选的；产品图标主题**只能用字体**，所以 `fonts` 至少要有一项。

**如何得到图标字体？** 一般先把每个图标画成单色 SVG，再用图标字体生成工具（比如 `fantasticon`、IcoMoon 等）把这些 SVG 打包成一个 woff 字体文件，同时得到每个图标对应的字符编码。

<a id="icon-definitions"></a>
### 图标定义（Icon definitions）

> VS Code 定义了一组图标 ID，视图通过这些 ID 引用图标。产品图标的 `iconDefinitions` 部分为这些 ID 分配新的图标。
>
> 每个定义都用 `fontId` 引用 `fonts` 部分中定义的某个字体。如果省略了 `fontId`，就使用字体定义中列出的第一个字体。

```json
{
  "iconDefinitions": {
    "dialog-close": {
      "fontCharacter": "\\43",
      "fontId": "alien-font"
    },
  }
}
```

> 所有图标标识符的列表，见[图标参考](../references/icons-in-labels.md#icon-listing)。

**和文件图标主题的关键区别：** 在文件图标主题中，`iconDefinitions` 的键（如 `_folder_dark`）是你**自己起的名字**，之后还要通过 `fileNames` 等把文件关联过来。而在产品图标主题中，`iconDefinitions` 的键必须是 **VS Code 规定的图标 ID**（如 `dialog-close`、`remote`、`debug-breakpoint`），定义了就直接生效，不需要再做关联。

没有在你的主题中定义的图标 ID，会继续使用 VS Code 默认的图标。所以不必一次性重新定义全部几百个图标，可以只替换其中一部分。

`"\\43"` 是 Unicode 编码 `0x43` 对应的字符（即字母 C 的编码位置）。示例中的字体把图标放在了这个位置。

---

<a id="develop-and-test"></a>
## 开发与测试（Develop and test）

> VS Code 为 `package.json` 文件以及产品图标主题文件提供了内置的编辑支持。要获得这些支持，你的主题文件名需要以 `product-icon-theme.json` 结尾。这样就能对所有属性（包括已知的图标 ID）进行代码补全，还有悬停提示和校验。
>
> 要试用产品图标主题，在 VS Code 中打开扩展文件夹，按 `F5`。这会在一个扩展开发宿主窗口中运行扩展。这个窗口启用了你的扩展，扩展会自动切换到第一个产品图标主题。
>
> 此外，主题文件会被监视。只要修改了主题文件，图标的更新就会自动生效。在编辑产品图标定义文件时，每次保存都能实时看到变化。
>
> 要在不同的产品图标主题之间切换，使用 **Preferences: Product Icon Theme** 命令。
>
> 要找出 VS Code 界面中某个位置使用的是哪个图标，可以通过 **帮助 > 切换开发人员工具**（**Help > Toggle Developer Tools**）打开开发者工具，然后：
>
> - 点击开发者工具左上角的检查工具。
> - 把鼠标移到要检查的图标上。
> - 如果图标的 class 名称是 `codicon.codicon-remote`，那么图标 ID 就是 `remote`。

![开发者工具的检查工具：悬停在状态栏的远程图标上，显示 codicon-remote](images/product-icon-theme/dev-tool-select-tool.png)

截图中，左下角红圈标出的是检查工具按钮；点击后把鼠标移到状态栏最左侧的远程图标上，弹出的提示显示 `span.codicon.codicon-remote::before`，说明这个图标的 ID 是 `remote`。

规则就是：**去掉 `codicon-` 前缀，剩下的部分就是图标 ID。** 开发者工具的用法也可以参考 [Webview 指南](./webview.md#inspecting-and-debugging-webviews) 中的说明。

---

<a id="sample"></a>
## 示例（Sample）

> [产品图标主题示例](https://github.com/microsoft/vscode-extension-samples/tree/main/product-icon-theme-sample)可以作为练习的起点。

（原文的链接文字写作 “Product Color Theme sample”，实际指向的是产品图标主题示例。）

---

## 本篇小结

| 项目 | 内容 |
|---|---|
| 贡献点 | `contributes.productIconThemes`（`id`、`label`、`path`） |
| 文件命名 | `*product-icon-theme.json`，可获得补全和校验 |
| 图标格式 | 只能用图标字体（推荐 woff），`fonts` 至少一项；图标只能单色 |
| 图标定义 | `iconDefinitions` 的键是 **VS Code 规定的图标 ID**，值是 `fontCharacter` + `fontId` |
| 未定义的图标 | 继续使用默认图标，可以只替换一部分 |
| 颜色 | 由当前颜色主题决定 |
| 查找图标 ID | 开发者工具检查元素，`codicon-xxx` 中的 `xxx` 就是 ID |
| 测试 | `F5`，保存主题文件后实时生效；**Preferences: Product Icon Theme** 切换 |
