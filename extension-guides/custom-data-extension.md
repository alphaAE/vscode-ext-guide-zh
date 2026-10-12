# 自定义数据扩展（Custom Data Extension）

> 原文：[Custom Data Extension](https://code.visualstudio.com/api/extension-guides/custom-data-extension)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/custom-data-extension.md`（DateApproved: 10/7/2026）

> [自定义数据格式（Custom Data format）](https://github.com/microsoft/vscode-custom-data)让扩展作者无需编写代码，就能轻松地扩展 VS Code 对 HTML / CSS 的语言支持。
>
> 在扩展中使用自定义数据的两个[贡献点](../references/contribution-points.md)是：
>
> - `contributes.html.customData`
> - `contributes.css.customData`
>
> 例如，在扩展的 `package.json` 中加入这一部分：

```json
{
  "contributes": {
    "html": {
      "customData": ["./html.html-data.json"]
    },
    "css": {
      "customData": ["./css.css-data.json"]
    }
  }
}
```

> VS Code 会加载这两个文件中定义的 HTML / CSS 实体，并为这些实体提供语言支持，例如自动补全和悬停信息。
>
> 你可以在 [microsoft/vscode-extension-samples](https://github.com/microsoft/vscode-extension-samples) 中找到 [custom-data-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/custom-data-sample)。

**适用场景：** 你的框架或组件库定义了自定义的 HTML 标签 / 属性（例如 Web Components 的 `<my-button>`），或者自定义的 CSS 属性 / 伪类 / at 规则。只要写一个 JSON 数据文件，内置的 HTML / CSS 语言支持就会为它们提供补全和悬停说明，不需要写一行代码，也不需要自己实现补全提供者。

**数据文件的格式（补充示例，完整的格式见上面链接的 vscode-custom-data 仓库）：**

```json
// html.html-data.json
{
  "version": 1.1,
  "tags": [
    {
      "name": "my-button",
      "description": "一个自定义按钮组件",
      "attributes": [
        { "name": "variant", "description": "按钮样式", "values": [{ "name": "primary" }, { "name": "secondary" }] }
      ]
    }
  ],
  "globalAttributes": [
    { "name": "data-track", "description": "埋点标识，可用于任意元素" }
  ]
}
```

```json
// css.css-data.json
{
  "version": 1.1,
  "properties": [
    { "name": "my-spacing", "description": "组件库的间距属性", "values": [{ "name": "small" }, { "name": "large" }] }
  ],
  "pseudoClasses": [
    { "name": ":my-active", "description": "组件处于激活状态" }
  ]
}
```

| 文件 | 可以定义 |
|---|---|
| HTML 数据 | `tags`（标签及其属性）、`globalAttributes`（全局属性）、`valueSets`（可复用的属性值集合） |
| CSS 数据 | `properties`（属性）、`atDirectives`（at 规则，如 `@my-rule`）、`pseudoClasses`（伪类）、`pseudoElements`（伪元素） |

用户也可以不通过扩展，直接在设置中使用同样的数据文件：`"html.customData": ["./html.html-data.json"]`、`"css.customData": [...]`（路径相对于工作区）。做成扩展的好处是可以分享给所有使用这个组件库的人。

---

## 本篇小结

```text
无需写代码即可扩展内置 HTML / CSS 语言支持（补全、悬停）
  package.json：contributes.html.customData / contributes.css.customData = [数据文件路径]
  HTML 数据：tags、globalAttributes、valueSets
  CSS 数据：properties、atDirectives、pseudoClasses、pseudoElements
用户也可以在设置 html.customData / css.customData 中直接使用
```
