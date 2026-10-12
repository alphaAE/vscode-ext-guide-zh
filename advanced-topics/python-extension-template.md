# 编写 Python 扩展（Authoring Python Extensions）

> 原文：[Authoring Python Extensions](https://code.visualstudio.com/api/advanced-topics/python-extension-template)
> 源文件：`microsoft/vscode-docs` → `api/advanced-topics/python-extension-template.md`（DateApproved: 10/7/2026）

> **注意**：如果你刚开始编写 VS Code 扩展，可以先阅读[你的第一个扩展](../get-started/your-first-extension.md)教程，尝试创建一个简单的 Hello World 扩展。
>
> [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) 扩展提供了 API，让其他扩展可以使用用户机器上可用的 Python 环境。请查看 [@vscode/python-extension](https://www.npmjs.com/package/@vscode/python-extension) npm 模块，它包含了在你的扩展中访问这些 API 所需的类型和辅助工具。

**本篇的场景：** 你有一个用 Python 写的工具（比如一个代码检查器或格式化工具），想把它做成 VS Code 扩展。VS Code 扩展本身必须用 JavaScript / TypeScript 编写，但借助 [语言服务器](../language-extensions/language-server-extension-guide.md) 的架构，“干活”的部分可以完全用 Python 写。

**使用 Python 扩展的 API（补充示例）：** 例如获取用户当前选择的 Python 解释器：

```ts
import { PythonExtension } from '@vscode/python-extension';

const api = await PythonExtension.api();                         // 获取 Python 扩展导出的 API
const env = api.environments.getActiveEnvironmentPath();         // 当前选中的环境
const resolved = await api.environments.resolveEnvironment(env); // 解析出解释器路径、版本等信息
console.log(resolved?.executable.uri?.fsPath);
```

（具体的 API 以该 npm 包的说明为准。使用它的扩展应该在 `package.json` 中声明 `"extensionDependencies": ["ms-python.python"]`。）

---

<a id="python-extension-template"></a>
## Python 扩展模板（Python extension template）

> [Python 扩展模板](https://github.com/microsoft/vscode-python-tools-extension-template)帮助你开始为你喜欢的 Python 工具构建一个 Visual Studio Code 扩展。它可以是一个 linter、格式化工具或代码分析工具，或者三者兼而有之。这个模板会为你提供构建一个把你的工具集成到 VS Code 中的扩展所需的基本构件，并且它已经可以访问上面提到的 Python API。

---

<a id="programming-languages-and-frameworks"></a>
## 编程语言和框架（Programming languages and frameworks）

> 这个扩展模板由两部分组成：扩展部分和语言服务器部分。扩展部分用 TypeScript 编写，语言服务器部分用 Python 编写，基于 `pygls`（Python 语言服务器）库。
>
> 使用这个模板时，你主要会在代码的 Python 部分上工作。你会使用[语言服务器协议](https://microsoft.github.io/language-server-protocol)把你的工具与扩展部分集成起来。`pygls` 目前支持 [LSP 的 3.16 版本](https://microsoft.github.io/language-server-protocol/specifications/specification-3-16)。
>
> TypeScript 部分负责与 VS Code 及其 UI 打交道。扩展模板内置了几个可供你的工具使用的设置。如果你需要添加新的设置来支持你的工具，就需要写一点 TypeScript。扩展模板中有几个设置的示例，你也可以看看我们团队为一些流行工具[开发的扩展](#examples)。

```text
VS Code ─ 扩展部分（TypeScript）─── LSP ─── 语言服务器（Python + pygls）─── 你的工具（Python 包）
           · 启动服务器、读取设置                     · 收到“文档已保存”等通知
           · 选择 Python 解释器                       · 调用你的工具，把结果转成诊断 / 格式化编辑
```

这与 [语言服务器扩展指南](../language-extensions/language-server-extension-guide.md) 中的架构完全一样，只是服务器换成了 Python 写的。（`pygls` 的新版本已经支持更新的 LSP 版本，以模板实际使用的版本为准。）

---

<a id="requirements"></a>
## 要求（Requirements）

> 1. VS Code 1.64.0 或更高版本
> 1. Python 3.7 或更高版本
> 1. node >= 14.19.0
> 1. npm >= 8.3.0（`npm` 随 node 一起安装，请检查 npm 的版本，使用 `npm install -g npm@8.3.0` 来更新）
> 1. VS Code 的 [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) 扩展
>
> 你应该知道如何创建和使用 Python 虚拟环境。

（这些是最低版本要求，实际开发时建议使用当前受支持的 Python 和 Node.js LTS 版本。）

---

<a id="getting-started"></a>
## 开始使用（Getting started）

> 要开始使用，请按照模板 [README](https://github.com/microsoft/vscode-python-tools-extension-template#readme) 中的说明操作。在那里你会了解如何使用[模板来创建你的仓库](https://docs.github.com/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)，以及如何安装必要的工具（例如 [nox](https://nox.thea.codes) 任务运行器）和可选的依赖（测试支持）。
>
> [README](https://github.com/microsoft/vscode-python-tools-extension-template#readme) 中有最新的说明，还详细介绍了如何自定义扩展 `package.json` 中的占位符（`<pythontool-module>`、`<pythontool-display-name>` 等）。

（GitHub 的“模板仓库”功能：在模板仓库页面点击 **Use this template**，就能以它为起点创建一个新仓库。`nox` 是一个 Python 的任务运行工具，类似于 npm scripts，模板用它来安装依赖、打包等。）

---

<a id="features-of-the-template"></a>
## 模板的功能（Features of the template）

> 通过模板创建扩展之后，它会包含以下扩展贡献。假设 `<pytool-module>` 被替换为 `mytool`，`<pytool-display-name>` 被替换为 `My Tool`：
>
> 1. 一个命令 **My Tool: Restart Server**（重启服务器，命令 ID：`mytool.restart`）。
> 1. 以下设置：
>     - `mytool.logLevel`
>     - `mytool.args`
>     - `mytool.path`
>     - `mytool.importStrategy`
>     - `mytool.interpreter`
>     - `mytool.showNotification`
> 1. 以下扩展激活的触发条件：
>     - 在 `python` 语言上（On Language）。
>     - 在打开的工作区中找到扩展名为 `.py` 的文件时（On File）。
>     - 在命令 `mytool.restart` 上（On Command）。
> 1. 用于记录日志的输出通道 **Output** > **My Tool**。

（注意原文前面写的占位符是 `<pythontool-module>`，这里写的是 `<pytool-module>`，以模板 README 为准。）

| 设置 | 含义（根据模板的约定） |
|---|---|
| `mytool.logLevel` | 输出通道中日志的详细程度 |
| `mytool.args` | 传给工具的额外命令行参数 |
| `mytool.path` | 使用指定路径的工具可执行文件，而不是模板自带的版本 |
| `mytool.importStrategy` | 使用扩展自带（bundled）的工具，还是从当前 Python 环境中导入 |
| `mytool.interpreter` | 运行语言服务器所用的 Python 解释器 |
| `mytool.showNotification` | 何时显示通知（如出错时） |

三个激活触发条件对应的就是 [激活事件](../references/activation-events.md)：`onLanguage:python`、`workspaceContains:*.py`、`onCommand:mytool.restart`。

---

<a id="integrating-your-tool"></a>
## 集成你的工具（Integrating your tool）

> 生成的 `bundled/tool/server.py` 文件是你会做大部分修改的地方。文件中的 `TODO` 注释指出了各个可定制的位置。也请在模板的其他位置搜索 `TODO` 注释，例如其他的 Python 和 Markdown 文件。你还需要检查 LICENSE 文件，即使你打算保留 MIT 许可证。

一个 pygls 服务器中处理“保存时检查”的大致样子（示意，具体以模板的 `server.py` 为准）：

```python
from pygls.server import LanguageServer
from lsprotocol import types as lsp

server = LanguageServer("mytool-server", "v0.1")

@server.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
def did_save(params: lsp.DidSaveTextDocumentParams):
    document = server.workspace.get_document(params.text_document.uri)
    diagnostics = run_my_tool(document.source)   # 调用你的工具，转换成 lsp.Diagnostic 列表
    server.publish_diagnostics(document.uri, diagnostics)
```

（这里用的是推送诊断模型，见 [编程式语言功能](../language-extensions/programmatic-language-features.md#provide-diagnostics)。pygls 不同大版本的 API 有差异，例如 2.x 中发布诊断的方法名有变化，以你所用的版本为准。）

---

<a id="examples"></a>
<a id="examples"></a>
## 示例（Examples）

> 有几个用这个模板创建的示例实现：
>
> - [Pylint](https://github.com/microsoft/vscode-pylint/tree/main/bundled/tool) - 实现了在文件 `open`（打开）、`save`（保存）和 `close`（关闭）时的代码检查和代码操作。
> - [Flake8](https://github.com/microsoft/vscode-flake8/tree/main/bundled/tool) - 实现了代码检查和代码操作。
> - [Black Formatter](https://github.com/microsoft/vscode-black-formatter/tree/main/bundled/tool) - 集成了 [*Black*](https://github.com/python/black) 格式化工具。
> - [autopep8](https://github.com/microsoft/vscode-autopep8/tree/main/bundled/tool) - 集成了 [autopep8](https://pypi.org/project/autopep8) 格式化工具。
> - [isort](https://github.com/microsoft/vscode-isort/blob/main/bundled/tool) - 添加了排序导入语句的代码操作。
>
> 你也可以查阅[语言服务器协议规范](https://microsoft.github.io/language-server-protocol/specifications/specification-3-16)，以更好地理解 `pygls` 语言服务器的集成。

这些都是微软官方维护的、真实在市场上发布的扩展，遇到问题时直接参考它们的 `bundled/tool` 目录是最快的办法：Pylint / Flake8 是 linter 的写法，Black / autopep8 是格式化工具的写法，isort 是代码操作的写法。

---

<a id="extension-development"></a>
## 扩展开发（Extension development）

> 模板的 README 详细介绍了模板所包含的[开发周期支持](https://github.com/microsoft/vscode-python-tools-extension-template#debugging)。模板中有命令和配置，可以让你构建、运行、调试和测试你的扩展。
>
> 如果你在开发过程中遇到问题，有一个[故障排除](https://github.com/microsoft/vscode-python-tools-extension-template#troubleshooting)部分可以帮助解决常见的问题。

---

<a id="packaging-and-publishing"></a>
## 打包和发布（Packaging and publishing）

> 在发布你的扩展之前，你需要为你的扩展更新 `package.json` 中的字段（例如 `publisher` 和 `license`）。你还需要更新辅助的 Markdown 文件（`CODE_OF_CONDUCT.md`、`CHANGELOG.md` 等）。
>
> 当你的扩展准备好发布时，有一个 `nox` 的 `build-package` 任务可以创建一个 `.vsix` 文件，然后你可以把它上传到你的扩展[管理页面](https://marketplace.visualstudio.com/manage)。
>
> 如果你刚开始创建和发布 VS Code 扩展，我们建议你遵循主要的 VS Code [扩展编写](../working-with-extensions/publishing-extension.md#advanced-usage)主题中概述的最佳实践。在那里，你会找到帮助你的扩展在市场上看起来更棒的指导，以及如何成为认证发布者，让用户安心地安装你的扩展。

**Python 工具扩展的打包要点：** 模板会把你的 Python 工具及其依赖“捆绑”（bundle）到扩展的 `bundled/libs` 目录中一起发布，这样用户不需要自己 `pip install` 就能使用（`importStrategy` 设置决定了是用捆绑的版本还是用户环境中的版本）。如果依赖包含平台相关的二进制文件，就需要使用 [平台特定的扩展](../working-with-extensions/publishing-extension.md#platform-specific-extensions)。发布流程本身与普通扩展相同，见 [发布扩展](../working-with-extensions/publishing-extension.md)。

---

## 本篇小结

```text
Python 工具 → VS Code 扩展：使用 vscode-python-tools-extension-template
  扩展部分（TypeScript）：启动服务器、设置、命令、选择解释器（借助 Python 扩展的 API）
  语言服务器（Python + pygls）：bundled/tool/server.py，按 TODO 注释集成你的工具
  两者通过 LSP 通信

模板自带：Restart Server 命令、logLevel / args / path / importStrategy / interpreter / showNotification 设置、
         python 语言 / .py 文件 / 命令三种激活方式、输出通道
参考实现：Pylint、Flake8、Black、autopep8、isort
打包：nox build-package → .vsix → 市场
其他扩展使用 Python 环境：@vscode/python-extension + extensionDependencies: ["ms-python.python"]
```
