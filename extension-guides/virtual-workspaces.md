# 虚拟工作区（Virtual Workspaces）

> 原文：[Virtual Workspaces](https://code.visualstudio.com/api/extension-guides/virtual-workspaces)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/virtual-workspaces.md`（DateApproved: 10/7/2026）

> 像 [GitHub Repositories](https://marketplace.visualstudio.com/items?itemName=GitHub.remotehub) 这样的扩展，会让 VS Code 打开一个或多个由[文件系统提供者](./virtual-documents.md#file-system-api)支撑的文件夹。当扩展实现了一个文件系统提供者时，工作区中的资源可能并不在本地磁盘上，而是**虚拟的**，位于服务器或云端，编辑操作也发生在那里。
>
> 这种配置称为**虚拟工作区**。当 VS Code 窗口中打开了一个虚拟工作区时，左下角的远程指示器中会显示一个标签，和其他[远程开发](https://code.visualstudio.com/docs/remote/remote-overview)窗口类似。

![远程指示器](images/virtual-workspaces/remote-indicator.png)

截图是 VS Code 窗口左下角的远程指示器，显示当前打开的是一个 GitHub 仓库（虚拟工作区）。

**举个例子：** 安装 GitHub Repositories 扩展后，可以不克隆代码，直接在 VS Code 中浏览、编辑 GitHub 上的仓库。资源管理器里的文件看起来和本地文件一样，但它们其实在 GitHub 的服务器上，URI 是 `vscode-vfs://github/...` 这样的形式，而不是 `file:///...`。

> 并不是所有扩展都能处理虚拟资源，有些扩展可能需要资源位于磁盘上。有些扩展使用依赖磁盘访问的工具，需要同步的文件访问，或者没有必要的文件系统抽象。在这些情况下，在虚拟工作区中，VS Code 会提示用户正在受限模式下运行，某些扩展被停用了，或者只能使用有限的功能。
>
> 一般来说，用户希望尽可能多的扩展能在虚拟工作区中工作，并且在浏览和编辑远程资源时有良好的用户体验。本指南介绍扩展如何在虚拟工作区中进行测试，说明为了让扩展在虚拟工作区中工作需要做哪些修改，并介绍 `virtualWorkspaces` 能力属性。
>
> 修改扩展使其能在虚拟工作区中工作，也是让扩展在[网页版 VS Code](https://code.visualstudio.com/docs/remote/vscode-web) 中良好运行的重要一步。网页版 VS Code 完全运行在浏览器中，由于浏览器的沙箱限制，工作区都是虚拟的。详情请参阅 [Web 扩展](./web-extensions.md)指南。

**为什么很多扩展在虚拟工作区中不能工作？** 因为它们默认“文件就在本地磁盘上”：

| 扩展的写法 | 在虚拟工作区中的问题 |
|---|---|
| 用 Node.js 的 `fs` 模块读写文件 | `fs` 只能访问本地磁盘，读不到服务器上的文件 |
| 使用 `uri.fsPath` 拼接路径 | 虚拟文件没有本地路径 |
| 调用命令行工具处理文件（如编译器、格式化工具） | 工具在本地运行，文件却不在本地 |
| 启动的语言服务器直接读磁盘 | 同上 |

注意这里的“受限模式”和 [工作区信任](./workspace-trust.md) 中的受限模式是两回事，只是名字相同：一个因为“文件不在本地”，一个因为“不信任文件的作者”。

---

<a id="is-my-extension-affected"></a>
## 我的扩展受影响吗？（Is my extension affected?）

> 如果扩展没有可执行的代码，而是纯声明式的，比如主题、快捷键、代码片段或语法扩展，它就可以在虚拟工作区中运行，不需要任何修改。
>
> 有代码的扩展，也就是定义了 `main` 入口的扩展，需要进行检查，并可能需要修改。

这和 [工作区信任](./workspace-trust.md) 中的判断方法一样：没有 `main` 入口就没有代码执行，自然不受影响。

---

<a id="run-your-extension-against-a-virtual-workspace"></a>
## 在虚拟工作区中运行你的扩展（Run your extension against a virtual workspace）

> 安装 [GitHub Repositories](https://marketplace.visualstudio.com/items?itemName=GitHub.remotehub) 扩展，然后从命令面板中运行 **Open GitHub Repository...** 命令。这个命令会显示一个快速选择下拉框，你可以粘贴任意 GitHub URL，或者选择搜索某个特定的仓库或拉取请求（pull request）。
>
> 这会为一个虚拟工作区打开一个 VS Code 窗口，其中所有的资源都是虚拟的。

测试自己的扩展时：在扩展开发宿主窗口中执行这个命令，打开一个 GitHub 仓库，就能检验扩展在虚拟工作区中的表现。

---

<a id="review-that-the-extension-code-is-ready-for-virtual-resources"></a>
## 检查扩展代码是否已经为虚拟资源做好准备（Review that the extension code is ready for virtual resources）

> VS Code API 对虚拟文件系统的支持已经存在相当长的时间了。你可以查看[文件系统提供者 API](./virtual-documents.md#file-system-api)。
>
> 文件系统提供者为一个新的 URI 协议注册（例如 `vscode-vfs`），这个文件系统上的资源会用使用该协议的 URI 来表示（`vscode-vfs://github/microsoft/vscode/package.json`）。
>
> 检查你的扩展如何处理从 VS Code API 返回的 URI：
>
> - 永远不要假设 URI 的协议是 `file`。只有当 URI 的协议是 `file` 时，才能使用 `URI.fsPath`。
> - 注意那些使用 `fs` Node 模块进行文件系统操作的地方。如果可能，请使用 `vscode.workspace.fs` API，它会把操作委托给对应的文件系统提供者。
> - 检查那些依赖 `fs` 访问的第三方组件（例如语言服务器或某个 Node 模块）。
> - 如果你通过命令运行可执行程序和任务，请检查这些命令在虚拟工作区窗口中是否有意义，或者是否应该禁用它们。

**改写示例：**

```ts
// ❌ 只能用于本地文件
import * as fs from 'fs';
const text = fs.readFileSync(uri.fsPath, 'utf8');
const configPath = path.join(folder.uri.fsPath, 'config.json');

// ✅ 任何文件系统都能用
const bytes = await vscode.workspace.fs.readFile(uri);
const text = new TextDecoder().decode(bytes);
const configUri = vscode.Uri.joinPath(folder.uri, 'config.json');
```

| 本地写法 | 通用写法 |
|---|---|
| `fs.readFile` / `fs.writeFile` | `vscode.workspace.fs.readFile` / `writeFile` |
| `fs.stat` / `fs.readdir` | `vscode.workspace.fs.stat` / `readDirectory` |
| `path.join(uri.fsPath, ...)` | `vscode.Uri.joinPath(uri, ...)` |
| 字符串形式的路径 | 始终传递 `Uri` 对象 |

`vscode.workspace.fs` 会根据 URI 的协议，自动把操作交给对应的文件系统提供者：`file:` 交给本地磁盘，`vscode-vfs:` 交给 GitHub Repositories 扩展，依此类推。这也是前面几篇（[通用能力](../extension-capabilities/common-capabilities.md#data-storage)、[自定义编辑器](./custom-editors.md#saving)）一直推荐 `vscode.workspace.fs` 的原因。

---

<a id="signal-whether-your-extension-can-handle-virtual-workspaces"></a>
## 声明扩展能否处理虚拟工作区（Signal whether your extension can handle virtual workspaces）

> `package.json` 中 `capabilities` 下的 `virtualWorkspaces` 属性，用来声明扩展是否支持虚拟工作区。

<a id="no-support-for-virtual-workspaces"></a>
### 不支持虚拟工作区（No support for virtual workspaces）

> 下面的例子声明了一个扩展不支持虚拟工作区，在这种环境下 VS Code 不应该启用它。

```json
{
  "capabilities": {
    "virtualWorkspaces": {
      "supported": false,
      "description": "Debugging is not possible in virtual workspaces."
    }
  }
}
```

<a id="partial-and-full-support-for-virtual-workspaces"></a>
### 部分支持和完全支持虚拟工作区（Partial and full support for virtual workspaces）

> 当扩展能在虚拟工作区中工作，或者能部分工作时，应该定义 `"virtualWorkspaces": true`。

```json
{
  "capabilities": {
    "virtualWorkspaces": true
  }
}
```

> 如果扩展能工作，但功能有限，应该向用户说明这些限制：

```json
{
  "capabilities": {
    "virtualWorkspaces": {
      "supported": "limited",
      "description": "In virtual workspaces, resolving and finding references across files is not supported."
    }
  }
}
```

> 这段描述会显示在扩展视图中：

![扩展视图](images/virtual-workspaces/extensions-view.png)

截图中，扩展视图里该扩展的详情处显示了 `description` 中的说明文字，告诉用户在虚拟工作区中哪些功能不可用。

> 然后，扩展应该按照下文的说明，禁用在虚拟工作区中不受支持的功能。

三种写法汇总（与 [工作区信任](./workspace-trust.md) 的 `untrustedWorkspaces` 写法几乎一样）：

| 写法 | 含义 |
|---|---|
| `"virtualWorkspaces": true` | 完全支持（简写） |
| `{ "supported": "limited", "description": "..." }` | 部分支持，并说明限制（原文前一段说部分支持也可以写 `true`，但推荐用这种写法说明限制） |
| `{ "supported": false, "description": "..." }` | 不支持，在虚拟工作区中不启用 |

<a id="default"></a>
### 默认值（Default）

> 对于所有尚未填写 `virtualWorkspaces` 能力的扩展，默认值是 `"virtualWorkspaces": true`。
>
> 不过，在测试虚拟工作区时，我们整理了一份我们认为应该在虚拟工作区中禁用的扩展列表。这份列表可以在 [issue #122836](https://github.com/microsoft/vscode/issues/122836) 中找到。这些扩展的默认值是 `"virtualWorkspaces": false`。
>
> 当然，扩展作者更适合做出这个决定。扩展 `package.json` 中的 `virtualWorkspaces` 能力会覆盖我们的默认值，我们最终也会废弃这份列表。

注意与工作区信任的区别：**工作区信任不声明时默认为 `false`（禁用），虚拟工作区不声明时默认为 `true`（启用）**。所以如果你的扩展在虚拟工作区中会出错，一定要主动声明 `false` 或 `limited`。

---

<a id="disable-functionality-when-a-virtual-workspace-is-opened"></a>
## 打开虚拟工作区时禁用功能（Disable functionality when a virtual workspace is opened）

<a id="disable-commands-and-view-contributions"></a>
### 禁用命令和视图贡献（Disable commands and view contributions）

> 命令、视图和许多其他贡献的可用性，都可以通过 [when 子句](../references/when-clause-contexts.md)中的上下文键来控制。
>
> 当所有工作区文件夹都位于虚拟文件系统上时，会设置 `virtualWorkspace` 上下文键。下面的例子只在不处于虚拟工作区时，才在命令面板中显示 `npm.publish` 命令：

```json
{
    "menus": {
      "commandPalette": [
        {
          "command": "npm.publish",
          "when": "!virtualWorkspace"
        }
      ]
    }
}
```

> `resourceScheme` 上下文键被设置为文件资源管理器中当前选中的元素、或编辑器中打开的元素的 URI 协议。
>
> 在下面的例子中，只有当底层资源位于本地磁盘上时，`npm.runSelectedScript` 命令才会显示在编辑器的上下文菜单中。

```json
{
    "menus": {
      "editor/context": [
        {
          "command": "npm.runSelectedScript",
          "when": "resourceFilename == 'package.json' && resourceScheme == file"
        }
      ]
    }
}
```

| 上下文键 | 判断的是 | 适合 |
|---|---|---|
| `virtualWorkspace` | **整个工作区**是否都是虚拟的 | 与整个项目相关的命令（如发布） |
| `resourceScheme` | **当前选中或打开的这个文件**的协议 | 与具体文件相关的命令（如运行这个文件） |

`resourceScheme` 在 [虚拟文档](./virtual-documents.md#add-editor-commands) 中也用到过。

<a id="detect-virtual-workspaces-programmatically"></a>
### 通过代码检测虚拟工作区（Detect virtual workspaces programmatically）

> 要检查当前工作区是否由非 `file` 协议组成、是虚拟的，可以使用下面的源代码：

```ts
const isVirtualWorkspace = workspace.workspaceFolders && workspace.workspaceFolders.every(f => f.uri.scheme !== 'file');
```

即：有打开的工作区文件夹，并且**每一个**文件夹的协议都不是 `file`。（没有打开任何文件夹时，结果是 `undefined`。）

---

<a id="language-extensions-and-virtual-workspaces"></a>
## 语言扩展与虚拟工作区（Language extensions and virtual workspaces）

<a id="what-are-the-expectations-for-language-support-with-virtual-workspaces"></a>
### 对虚拟工作区中的语言支持有什么期望？（What are the expectations for language support with virtual workspaces?）

> 要求所有扩展都能完全处理虚拟资源是不现实的。很多扩展使用的外部工具需要同步的文件访问，需要文件位于磁盘上。因此，只提供有限的功能是可以接受的，比如下面列出的**基础**支持和**单文件**支持。

| 级别 | 包含的功能 | 能否在虚拟工作区中实现 |
|---|---|---|
| A. **基础**语言支持 | TextMate 分词和着色；特定于语言的编辑支持：括号配对、注释、回车规则、折叠标记；代码片段 | 能（都是声明式的） |
| B. **单文件**语言支持 | 文档符号（大纲）、折叠、选区范围；文档高亮、语义高亮、文档颜色；基于当前文件中的符号和静态语言库的补全、悬停、签名帮助、查找引用 / 声明；格式化、联动编辑；语法校验、同一文件内的语义校验，以及代码操作（Code Actions） | 能（只需要当前文件的内容，VS Code 已经提供给你了） |
| C. **跨文件、感知工作区**的语言支持 | 跨文件的引用；工作区符号；对工作区 / 项目中所有文件的校验 | 很难（需要读取整个项目的文件） |

> VS Code 附带的丰富语言扩展（TypeScript、JSON、CSS、HTML、Markdown），在处理虚拟资源时，都只提供单文件的语言支持。

各项功能的具体含义见 [语言扩展概览](../language-extensions/overview.md) 和 [编程式语言功能](../language-extensions/programmatic-language-features.md)。

<a id="disabling-a-language-extension"></a>
### 禁用语言扩展（Disabling a language extension）

> 如果连单文件处理都做不到，语言扩展也可以决定在虚拟工作区中禁用扩展。
>
> 如果你的扩展既提供了语法，又提供了需要被禁用的丰富语言支持，那么语法也会随之被禁用。为了避免这种情况，你可以创建一个与丰富语言支持分离的基础语言扩展（语法、语言配置、代码片段），也就是做成两个扩展。
>
> - 基础语言扩展设置 `"virtualWorkspaces": true`，提供语言 ID、配置、语法和代码片段。
> - 丰富语言扩展设置 `"virtualWorkspaces": false`，包含 `main` 文件。它贡献语言支持和命令，并且有一个对基础语言扩展的扩展依赖（`extensionDependencies`）。丰富语言扩展应该保留原有扩展的扩展 ID，这样用户只需安装一个扩展，就能继续获得完整的功能。
>
> 你可以在内置的语言扩展中看到这种做法，例如 JSON，它由一个 JSON 扩展和一个 JSON 语言功能扩展组成。

```text
my-lang（原有的扩展 ID，用户安装的就是它）
  ├─ virtualWorkspaces: false
  ├─ main: ./out/extension.js（语言服务器、命令等）
  └─ extensionDependencies: ["publisher.my-lang-basics"]
           ↓ 安装时自动一起安装
my-lang-basics（新拆出来的扩展）
  ├─ virtualWorkspaces: true
  └─ 没有 main：只有 languages、grammars、snippets 等声明
```

这样，在虚拟工作区中，`my-lang` 被禁用，但 `my-lang-basics` 依然工作，用户至少还有语法高亮和代码片段。`extensionDependencies` 的写法见 [扩展清单](../references/extension-manifest.md)。

> 这种拆分也有助于在[受限模式](https://code.visualstudio.com/docs/editor/workspace-trust#restricted-mode)下运行的[不受信任的工作区](./workspace-trust.md)。丰富的语言扩展通常需要信任，而基础语言功能可以在任何环境下运行。

<a id="language-selectors"></a>
### 语言选择器（Language selectors）

> 为语言功能（例如补全、悬停、代码操作等）注册提供者时，一定要指定这个提供者支持哪些协议：

```ts
return vscode.languages.registerCompletionItemProvider({ language: 'typescript', scheme: 'file' }, {
  provideCompletionItems(document, position, token) {
    // ...
  }
});
```

第一个参数叫**文档选择器**（document selector），决定这个提供者对哪些文档生效。写成 `{ language: 'typescript', scheme: 'file' }` 表示只对本地磁盘上的 TypeScript 文件生效，在虚拟工作区中就不会被调用，也就不会因为读不到本地文件而出错。

如果提供者只依赖文档本身的内容（`document.getText()`），在虚拟文件中也能正常工作，就可以不限定 `scheme`，或者写成 `[{ language: 'typescript', scheme: 'file' }, { language: 'typescript', scheme: 'vscode-vfs' }]`。文档选择器的完整写法见 [文档选择器](../references/document-selector.md)。

<a id="what-about-support-in-the-language-server-protocol-lsp-for-accessing-virtual-resources"></a>
### 语言服务器协议（LSP）对访问虚拟资源的支持如何？（What about support in the Language Server Protocol (LSP) for accessing virtual resources?）

> 为 LSP 添加文件系统提供者支持的工作正在进行中。在语言服务器协议的 [issue #1264](https://github.com/microsoft/language-server-protocol/issues/1264) 中跟踪。

---

## 本篇小结

```text
虚拟工作区：文件由 FileSystemProvider 提供，不在本地磁盘（URI 协议不是 file）

是否受影响：没有 main 入口 → 不受影响；有代码 → 检查
  × 假设协议是 file、使用 uri.fsPath
  × 使用 Node.js 的 fs 模块        → 改用 vscode.workspace.fs + Uri.joinPath
  × 依赖本地磁盘的第三方工具、语言服务器

声明：capabilities.virtualWorkspaces
  true（默认值）/ { supported: "limited", description } / { supported: false, description }

禁用功能
  when 子句：!virtualWorkspace（整个工作区）、resourceScheme == file（当前文件）
  代码：workspaceFolders.every(f => f.uri.scheme !== 'file')
  语言提供者：文档选择器中指定 scheme

语言扩展：基础（声明式）+ 单文件支持即可；可以拆成“基础扩展 + 丰富扩展”两个扩展
```
