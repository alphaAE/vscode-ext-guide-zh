# 许可（License）

本仓库是 [microsoft/vscode-docs](https://github.com/microsoft/vscode-docs) 中 `api/` 目录的中文翻译与改编版本（基于提交 `aeaa6ff`，2026-10-10），按原仓库的许可条款分发。

## 原作品

Copyright (c) Microsoft Corporation. All rights reserved.

原仓库的许可条款（[LICENSE.md](https://github.com/microsoft/vscode-docs/blob/main/LICENSE.md)）：

> 1. Documentation is licensed under the [Creative Commons Attribution 3.0 United States License](https://creativecommons.org/licenses/by/3.0/us/legalcode). Code is licensed under the [MIT License](https://opensource.org/licenses/MIT).
>
> 2. This license does not grant you rights to use any trademarks or logos of Microsoft. For Microsoft's general trademark guidelines, go to https://go.microsoft.com/fwlink/?LinkID=254653.

## 本仓库各部分的许可

| 内容 | 许可 |
|---|---|
| 文档（各章节的 `.md` 文件，含译文与新增的讲解、表格、示例说明） | [知识共享 署名 3.0 美国（CC BY 3.0 US）](https://creativecommons.org/licenses/by/3.0/us/legalcode) |
| 文档中的示例代码（来自原文的代码，以及在原文基础上补充或修改的代码） | [MIT 许可](#mit-license) |
| 图片、视频等资源（`images/` 目录） | 来自原仓库，沿用原仓库的许可（CC BY 3.0 US） |
| `tools/` 目录中的维护脚本 | [MIT 许可](#mit-license) |

## 对原作品所做的修改

依照 CC BY 3.0 的要求，在此说明本仓库相对原作品的修改：

- 把原文翻译为简体中文，原文的段落以引用块（`>`）形式保留其译文；
- 增加了原文没有的讲解、对比表格、流程示意、补充示例代码和每篇末尾的小结；
- 修正或标注了原文中发现的错误和过时内容（汇总见 [原文勘误清单](./errata.md)）；
- 把站内链接改为指向本仓库对应文件，并在标题前插入原文的英文锚点；
- 新增 `README.md`、`CONVENTIONS.md`、`glossary.md`、`errata.md` 和 `tools/` 脚本。

本仓库不是 Microsoft 的官方出版物，未获得 Microsoft 的认可或背书。译文和新增内容中的任何错误由本仓库的贡献者负责。Visual Studio Code、VS Code 等名称和标志是 Microsoft 的商标，本许可不授予使用这些商标的任何权利。

<a id="mit-license"></a>
## MIT 许可

适用于上表中标注为 MIT 许可的部分。原文示例代码的版权归 Microsoft Corporation 所有；补充和修改的代码及 `tools/` 脚本的版权归本仓库的贡献者所有。

```text
MIT License

Copyright (c) Microsoft Corporation.
Copyright (c) 本仓库的贡献者 (contributors of this repository)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
