# 支持远程开发和 GitHub Codespaces（Supporting Remote Development and GitHub Codespaces）

> 原文：[Supporting Remote Development and GitHub Codespaces](https://code.visualstudio.com/api/advanced-topics/remote-extensions)
> 源文件：`microsoft/vscode-docs` → `api/advanced-topics/remote-extensions.md`（DateApproved: 10/7/2026）

> **[Visual Studio Code 远程开发](https://code.visualstudio.com/docs/remote/remote-overview)**让你可以透明地使用位于其他机器上（无论是虚拟机还是物理机）的源代码和运行时环境。**[GitHub Codespaces](https://github.com/features/codespaces)** 是一项扩展了这些能力的服务，它提供托管在云端的环境，可以从 VS Code 和基于浏览器的编辑器中访问。
>
> 为了确保性能，远程开发和 GitHub Codespaces 都会透明地在远程运行某些 VS Code 扩展。然而，这可能会对扩展的工作方式产生微妙的影响。虽然很多扩展无需任何修改就能工作，但你可能需要做一些更改，让你的扩展在所有环境中都能正常工作，不过这些更改通常都相当小。
>
> 本文总结了扩展作者需要了解的关于远程开发和 Codespaces 的内容，包括扩展的[架构](#architecture-and-extension-kinds)、如何在远程工作区或 Codespaces 中[调试你的扩展](#debugging-extensions)，以及[如果你的扩展不能正常工作该怎么办](#common-problems)的建议。

**远程开发的几种形式**（本篇统称“远程”）：

| 形式 | 代码和工具在哪里 | 用户的界面在哪里 |
|---|---|---|
| Remote - SSH | 通过 SSH 连接的服务器 | 本地 VS Code |
| Dev Containers | 本地或远程的 Docker 容器 | 本地 VS Code |
| WSL | Windows 上的 Linux 子系统 | Windows 上的 VS Code |
| GitHub Codespaces | GitHub 托管的云端容器 | 本地 VS Code，**或浏览器** |
| Remote Tunnels | 通过隧道连接的任意机器 | 本地 VS Code 或浏览器 |

本篇的核心问题只有一个：**你的扩展代码运行在哪台机器上？** 它决定了 `fs` 读到的是哪台机器的文件、`child_process` 启动的是哪台机器上的程序、`localhost` 指的是哪台机器。先读一下 [扩展宿主](./extension-host.md) 会更容易理解本篇。

---

<a id="architecture-and-extension-kinds"></a>
## 架构和扩展的种类（Architecture and extension kinds）

> 为了让用户使用远程开发或 Codespaces 时尽可能感觉不到差别，VS Code 区分了两种扩展：
>
> - **UI 扩展**：这些扩展为 VS Code 的用户界面做贡献，并且总是在用户的本地机器上运行。UI 扩展不能直接访问远程工作区中的文件，也不能运行安装在那个工作区或那台机器上的脚本 / 工具。UI 扩展的例子包括：主题、代码片段、语言语法和快捷键映射。
>
> - **工作区扩展**：这些扩展运行在工作区所在的同一台机器上。在本地工作区中，工作区扩展运行在本地机器上。在远程工作区中或使用 Codespaces 时，工作区扩展运行在远程机器 / 环境上。工作区扩展可以访问工作区中的文件，以提供丰富的多文件语言服务、调试器支持，或者对工作区中的多个文件执行复杂的操作（直接执行，或者通过调用脚本 / 工具执行）。虽然工作区扩展的重点不是修改 UI，但它们也可以贡献资源管理器、视图和其他 UI 元素。
>
> 当用户安装一个扩展时，VS Code 会根据它的种类，自动把它安装到正确的位置。如果一个扩展可以作为任一种类运行，VS Code 会尝试根据情况选择最佳的一种；UI 扩展会运行在 VS Code 的[本地扩展宿主](./extension-host.md)中，而工作区扩展如果在远程工作区中存在，就会运行在一个位于小型 [**VS Code Server**](https://code.visualstudio.com/docs/remote/vscode-server) 中的**远程扩展宿主**里，否则如果它在本地存在，就运行在 VS Code 的本地扩展宿主中。为了确保最新的 VS Code 客户端功能可用，服务器需要与 VS Code 客户端的版本完全一致。因此，当你在容器中、在远程 SSH 主机上、使用 Codespaces 或在适用于 Linux 的 Windows 子系统（WSL）中打开一个文件夹时，远程开发或 GitHub Codespaces 扩展会自动安装（或更新）这个服务器。（VS Code 还会自动管理服务器的启动和停止，所以用户不会察觉到它的存在。）

![架构图](images/remote-extensions/architecture.png)

图中左边是**本地操作系统**：VS Code 中的本地扩展宿主运行着几个 UI 扩展，它们可以访问本地文件系统、启动本地的子进程、调用本地操作系统的 API。右边是**远程操作系统**：VS Code Server 中的远程扩展宿主运行着几个工作区扩展，它们可以访问远程文件系统，并使用远程的终端进程、运行中的应用程序、调试器、子进程和操作系统 API。两边的 VS Code 通过一条连接通信。

> 无论是从 UI 扩展还是从工作区扩展中调用，VS Code 的 API 都被设计为会自动在正确的机器上（本地或远程）运行。但是，如果你的扩展使用了不是由 VS Code 提供的 API（例如使用 Node API 或运行 shell 脚本），那么它在远程运行时可能无法正常工作。我们建议你测试一下，确保扩展的所有功能在本地和远程工作区中都能正常工作。

**“VS Code 的 API 会自动在正确的机器上运行”是什么意思？** 举几个例子：

| 你在远程的工作区扩展中调用 | 实际效果 |
|---|---|
| `vscode.workspace.fs.readFile(uri)` | 读取远程机器上的文件（正确） |
| Node 的 `fs.readFileSync(path)` | 也读取远程机器上的文件（因为扩展就运行在远程），对工作区文件来说没问题 |
| `vscode.window.showInformationMessage` | 在用户本地的界面上显示通知（VS Code 自动转发） |
| `vscode.env.clipboard.writeText` | 写入用户**本地**的剪贴板（正确） |
| 第三方剪贴板库、`child_process` 打开浏览器 | 操作的是**远程机器**的剪贴板 / 浏览器（错误，用户看不到） |

所以原则是：凡是与“用户这一侧”相关的事情（剪贴板、打开浏览器、打开链接），一律通过 `vscode` API 来做，不要直接用 Node 模块。下文的 [常见问题](#common-problems) 就是逐条展开这个原则。

---

<a id="debugging-extensions"></a>
## 调试扩展（Debugging Extensions）

> 虽然你[可以在远程环境中安装扩展的开发版本](#installing-a-development-version-of-your-extension)来进行测试，但如果遇到问题，你很可能会想直接在远程环境中调试你的扩展。在本节中，我们将介绍如何在 [GitHub Codespaces](#debugging-with-github-codespaces)、[本地容器](#debugging-in-a-custom-development-container)、[SSH 主机](#debugging-using-ssh)或 [WSL](#debugging-using-wsl) 中编辑、启动和调试你的扩展。
>
> 通常，最好的测试起点是使用一个限制端口访问的远程环境（例如 Codespaces、容器，或带有严格防火墙的远程 SSH 主机），因为在这些环境中能正常工作的扩展，在 WSL 这类限制较少的环境中往往也能正常工作。

四种环境的调试步骤结构完全相同：**连接到远程环境 → 在远程打开扩展的源代码 → 在远程安装依赖 → 按 `F5`**。这时扩展开发宿主窗口也连接在同一个远程环境中，你的扩展运行在远程扩展宿主里，调试器自动附加。

<a id="debugging-with-github-codespaces"></a>
### 使用 GitHub Codespaces 调试（Debugging with GitHub Codespaces）

> 在 [GitHub Codespaces](https://docs.github.com/github/developing-online-with-codespaces) 预览版中调试你的扩展，可以是一个很好的起点，因为你可以同时使用 VS Code 和 Codespaces 基于浏览器的编辑器进行测试和故障排除。如果你愿意，也可以使用一个[自定义开发容器](#debugging-in-a-custom-development-container)。
>
> 按照以下步骤操作：
>
> 1. 在 GitHub 上进入包含你的扩展的仓库，并[在一个 codespace 中打开它](https://docs.github.com/github/developing-online-with-codespaces/creating-a-codespace)，在基于浏览器的编辑器中使用它。如果你愿意，也可以[在 VS Code 中打开这个 codespace](https://docs.github.com/github/developing-online-with-codespaces/using-codespaces-in-visual-studio-code)。
>
> 2. 虽然 GitHub Codespaces 的默认镜像应该已经包含大多数扩展所需的所有前提条件，但你可以在一个新的 VS Code 终端窗口（`` Ctrl+Shift+` ``）中安装任何其他需要的依赖（例如使用 `yarn install` 或 `sudo apt-get`）。
>
> 3. 最后，按 `F5` 或使用 **Run and Debug**（运行和调试）视图，在 codespace 中启动扩展。
>
>     > **注意**：你无法在出现的窗口中打开扩展的源代码文件夹，但你可以打开一个子文件夹，或者 codespace 中的其他位置。
>
> 出现的扩展开发宿主窗口中，会包含你那个在 codespace 中运行、并附加了调试器的扩展。

（“预览版”是原文早期的说法，Codespaces 现在已正式发布。“无法打开源代码文件夹”的原因：同一个文件夹不能同时在两个窗口中作为工作区打开，所以扩展开发宿主窗口要打开别的文件夹，比如一个测试用的子文件夹。）

<a id="debugging-in-a-custom-development-container"></a>
### 在自定义开发容器中调试（Debugging in a custom development container）

> 按照以下步骤操作：
>
> 1. 要在本地使用开发容器，请[安装并配置 Dev Containers 扩展](https://code.visualstudio.com/docs/devcontainers/containers#getting-started)，然后使用 **File > Open... / Open Folder...**（文件 > 打开... / 打开文件夹...）在 VS Code 中本地打开你的源代码。如果改用 Codespaces，请在 GitHub 上进入包含你的扩展的仓库，并[在一个 codespace 中打开它](https://docs.github.com/github/developing-online-with-codespaces/creating-a-codespace)，在基于浏览器的编辑器中使用它。如果你愿意，也可以[在 VS Code 中打开这个 codespace](https://docs.github.com/github/developing-online-with-codespaces/using-codespaces-in-visual-studio-code)。
>
> 2. 从命令面板（`F1`）中选择 **Dev Containers: Add Dev Container Configuration Files...** 或 **Codespaces: Add Dev Container Configuration Files...**，然后选择 **Node.js & TypeScript**（如果你不使用 TypeScript，就选 Node.js），添加所需的容器配置文件。
>
> 3. **可选**：这个命令运行之后，你可以修改 `.devcontainer` 文件夹的内容，加入额外的构建或运行时要求。详情请参见深入的[创建开发容器](https://code.visualstudio.com/docs/devcontainers/create-dev-container)文档。
>
> 4. 运行 **Dev Containers: Reopen in Container**（在容器中重新打开）或 **Codespaces: Add Dev Container Configuration Files...**，片刻之后，VS Code 就会设置好容器并连接上去。现在你就可以在容器内部开发你的源代码，就像在本地一样。
>
> 5. 在一个新的 VS Code 终端窗口（`` Ctrl+Shift+` ``）中运行 `yarn install` 或 `npm install`，确保安装了 Linux 版本的 Node.js 原生依赖。你也可以安装其他的操作系统或运行时依赖，但你可能也需要把它们添加到 `.devcontainer/Dockerfile` 中，这样在重建容器时它们也可用。
>
> 6. 最后，按 `F5` 或使用 **Run and Debug**（运行和调试）视图，在同一个容器中启动扩展并附加调试器。
>
>     > **注意**：你无法在出现的窗口中打开扩展的源代码文件夹，但你可以打开一个子文件夹，或者容器中的其他位置。
>
> 出现的扩展开发宿主窗口中，会包含你那个在第 2 步定义的容器中运行、并附加了调试器的扩展。

（第 4 步原文写的第二个命令重复了第 2 步的 “Codespaces: Add Dev Container Configuration Files...”，使用 Codespaces 时这一步通常是 **Codespaces: Rebuild Container**，以重新构建 codespace 使配置生效。第 5 步“重新安装依赖”很重要：如果 `node_modules` 是在 Windows / macOS 上安装的，其中的原生模块在 Linux 容器中无法使用。）

<a id="debugging-using-ssh"></a>
### 使用 SSH 调试（Debugging using SSH）

> 按照以下步骤操作：
>
> 1. [安装并配置 Remote - SSH 扩展](https://code.visualstudio.com/docs/remote/ssh#getting-started)之后，在 VS Code 的命令面板（`F1`）中选择 **Remote-SSH: Connect to Host...**（连接到主机）连接到一个主机。
>
> 2. 连接之后，要么使用 **File > Open... / Open Folder...**（文件 > 打开... / 打开文件夹...）选择包含扩展源代码的远程文件夹，要么从命令面板（`F1`）中选择 **Git: Clone**，克隆源代码并在远程主机上打开它。
>
> 3. 在一个新的 VS Code 终端窗口（`` Ctrl+Shift+` ``）中，安装任何可能缺少的依赖（例如使用 `yarn install` 或 `apt-get`）。
>
> 4. 最后，按 `F5` 或使用 **Run and Debug**（运行和调试）视图，在远程主机上启动扩展并附加调试器。
>
>     > **注意**：你无法在出现的窗口中打开扩展的源代码文件夹，但你可以打开一个子文件夹，或者 SSH 主机上的其他位置。
>
> 出现的扩展开发宿主窗口中，会包含你那个在 SSH 主机上运行、并附加了调试器的扩展。

<a id="debugging-using-wsl"></a>
### 使用 WSL 调试（Debugging using WSL）

> 按照以下步骤操作：
>
> 1. [安装并配置 WSL 扩展](https://code.visualstudio.com/docs/remote/wsl)之后，在 VS Code 的命令面板（`F1`）中选择 **WSL: New Window**（新建窗口）。
>
> 2. 在出现的新窗口中，要么使用 **File > Open... / Open Folder...**（文件 > 打开... / 打开文件夹...）选择包含扩展源代码的远程文件夹，要么从命令面板（`F1`）中选择 **Git: Clone**，克隆源代码并在 WSL 中打开它。
>
>     > **提示**：你可以选择 `/mnt/c` 文件夹，访问你在 Windows 一侧克隆的任何源代码。
>
> 3. 在一个新的 VS Code 终端窗口（`` Ctrl+Shift+` ``）中，安装任何可能缺少的依赖（例如使用 `apt-get`）。你至少需要运行 `yarn install` 或 `npm install`，确保可以使用 Linux 版本的 Node.js 原生依赖。
>
> 4. 最后，按 `F5` 或使用 **Run and Debug**（运行和调试）视图，像在本地一样启动扩展并附加调试器。
>
>     > **注意**：你无法在出现的窗口中打开扩展的源代码文件夹，但你可以打开一个子文件夹，或者 WSL 中的其他位置。
>
> 出现的扩展开发宿主窗口中，会包含你那个在 WSL 中运行、并附加了调试器的扩展。

（通过 `/mnt/c` 访问 Windows 一侧的文件比较慢，长期开发建议把代码克隆到 WSL 自己的文件系统中，例如 `~/projects`。）

---

<a id="installing-a-development-version-of-your-extension"></a>
## 安装扩展的开发版本（Installing a development version of your extension）

> 每当 VS Code 在 SSH 主机上、在容器或 WSL 中，或者通过 GitHub Codespaces 自动安装一个扩展时，使用的都是市场上的版本（而不是你本地机器上已经安装的版本）。
>
> 虽然这在大多数情况下是合理的，但你可能希望使用（或分享）扩展的一个未发布版本进行测试，而不必搭建调试环境。要安装扩展的一个未发布版本，你可以把扩展打包成一个 `VSIX`，然后手动把它安装到一个已经连接到运行中的远程环境的 VS Code 窗口中。
>
> 按照以下步骤操作：
>
> 1. 如果这是一个已发布的扩展，你可能需要在 `settings.json` 中添加 `"extensions.autoUpdate": false`，防止它自动更新到市场上的最新版本。
> 2. 接下来，使用 `vsce package` 把你的扩展打包成一个 VSIX。
> 3. 连接到一个 [codespace](https://docs.github.com/github/developing-online-with-codespaces)、[开发容器](https://code.visualstudio.com/docs/devcontainers/containers)、[SSH 主机](https://code.visualstudio.com/docs/remote/ssh)或 [WSL 环境](https://code.visualstudio.com/docs/remote/wsl)。
> 4. 使用扩展视图 **More Actions**（更多操作，`...`）菜单中的 **Install from VSIX...**（从 VSIX 安装）命令，把扩展安装到这个特定的窗口中（而不是一个本地窗口）。
> 5. 按提示重新加载。

> **提示**：安装之后，你可以使用 **Developer: Show Running Extensions**（显示正在运行的扩展）命令，查看 VS Code 是在本地还是在远程运行这个扩展。

---

<a id="handling-dependencies-with-remote-extensions"></a>
## 处理远程扩展的依赖（Handling dependencies with remote extensions）

> 扩展可以依赖其他扩展提供的 API。例如：
>
> - 一个扩展可以从它的 `activate` 函数中导出一个 API。
> - 这个 API 会对运行在同一个扩展宿主中的所有扩展可用。
> - 使用方的扩展在它们的 `package.json` 中，用 `extensionDependencies` 属性声明它们依赖于提供方的扩展。
>
> 当所有的扩展都在本地运行、共享同一个扩展宿主时，扩展依赖可以正常工作。
>
> 在处理远程场景时，一个在远程运行的扩展，可能会依赖一个在本地运行的扩展。例如，本地扩展公开了一个对远程扩展的运行至关重要的命令。在这种情况下，我们建议远程扩展把本地扩展声明为一个 `extensionDependency`，但问题在于，这两个扩展运行在两个不同的扩展宿主中，这意味着提供方的 API 对使用方是不可用的。因此，要求提供方的扩展在它的扩展 `package.json` 中使用 `"api": "none"`，完全放弃导出任何 API 的能力。这些扩展仍然可以使用 VS Code 命令（命令是异步的）进行通信。
>
> 这看起来似乎是对提供方扩展的一个不必要的严格限制，但一个使用 `"api": "none"` 的扩展，只是放弃了从它的 `activate` 方法中返回 API 的能力。在其他扩展宿主上执行的使用方扩展仍然可以依赖它们，并且会被激活。

**为什么跨扩展宿主不能共享 API？** `activate` 返回的 API 是一个普通的 JavaScript 对象（里面可能有函数、类实例），它只存在于提供方所在的那个进程的内存中。使用方在另一台机器的另一个进程中，拿不到这个对象。而命令不同：`executeCommand` 的参数和返回值会被序列化成 JSON，由 VS Code 在两个扩展宿主之间转发（见下文 [使用命令在扩展之间通信](#communicating-between-extensions-using-commands)）。

```json
// 本地的提供方扩展（UI 扩展）的 package.json
{ "extensionKind": ["ui"], "api": "none" }
```

```json
// 远程的使用方扩展（工作区扩展）的 package.json
{ "extensionKind": ["workspace"], "extensionDependencies": ["发布者.提供方扩展"] }
```

---

<a id="common-problems"></a>
## 常见问题（Common problems）

> 无论你的扩展碰巧位于哪里，VS Code 的 API 都被设计为会自动在正确的位置运行。考虑到这一点，有一些 API 可以帮你避免意外的行为。

| 想做的事 | 不要用 | 要用 |
|---|---|---|
| 持久化数据 | 写死路径 `~/.vscode`、`~/.config/Code` | `context.globalState` / `workspaceState`、`globalStorageUri` / `storageUri` |
| 保存密码、令牌 | `globalState`（明文） | `context.secrets` |
| 读写剪贴板 | `clipboardy` 等 Node 模块 | `vscode.env.clipboard` |
| 打开浏览器 / 外部程序 | `child_process`、`opn` | `vscode.env.openExternal` |
| 让外部访问远程的 localhost 服务 | 直接拼 `http://localhost:端口` | `vscode.env.asExternalUri` |
| OAuth 回调 | 写死 `vscode://` | `registerUriHandler` + `asExternalUri` |
| 扩展之间共享功能（跨本地 / 远程） | `getExtension(id).exports` | `vscode.commands.executeCommand` |
| webview 加载扩展资源 | 写死 `vscode-resource:` | `webview.asWebviewUri` |
| webview 与扩展交换数据 | webview 直接请求 localhost | 消息传递（`postMessage`） |

<a id="incorrect-execution-location"></a>
### 错误的执行位置（Incorrect execution location）

> 如果你的扩展没有按预期运行，它可能运行在错误的位置。最常见的表现是，一个扩展在远程运行，而你预期它只在本地运行。你可以从命令面板（`F1`）中使用 **Developer: Show Running Extensions** 命令，查看一个扩展在哪里运行。
>
> 如果 **Developer: Show Running Extensions** 命令显示，一个 UI 扩展被错误地当作了工作区扩展，或者反过来，请尝试按照[扩展种类一节](./extension-host.md#preferred-extension-location)中的描述，在你的扩展的 [package.json](../get-started/extension-anatomy.md#extension-manifest) 中设置 `extensionKind` 属性。
>
> 你可以用 `remote.extensionKind` [设置](https://code.visualstudio.com/docs/configure/settings)快速**测试**更改一个扩展的种类所产生的效果。这个设置是一个从扩展 ID 到扩展种类的映射。例如，如果你想强制 [Azure Databases](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-cosmosdb) 扩展成为一个 UI 扩展（而不是默认的工作区扩展），并强制 [Remote - SSH: Editing Configuration Files](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh-edit) 扩展成为一个工作区扩展（而不是默认的 UI 扩展），你可以这样设置：

```json
{
  "remote.extensionKind": {
      "ms-azuretools.vscode-cosmosdb": ["ui"],
      "ms-vscode-remote.remote-ssh-edit": ["workspace"]
  }
}
```

> 使用 `remote.extensionKind`，你可以快速测试已发布版本的扩展，而无需修改它们的 `package.json` 并重新构建它们。

<a id="persisting-extension-data-or-state"></a>
### 持久化扩展的数据或状态（Persisting extension data or state）

> 在某些情况下，你的扩展可能需要持久化一些状态信息，这些信息不属于 `settings.json` 或一个单独的工作区配置文件（例如 `.eslintrc`）。为了解决这个问题，VS Code 在激活时传给你的扩展的 `vscode.ExtensionContext` 对象上，提供了一组有用的存储属性。如果你的扩展已经在使用这些属性，那么无论它在哪里运行，都应该能继续正常工作。
>
> 但是，如果你的扩展依赖于当前 VS Code 的路径约定（例如 `~/.vscode`）或某些操作系统文件夹的存在（例如 Linux 上的 `~/.config/Code`）来持久化数据，你可能会遇到问题。幸运的是，更新你的扩展、避免这些问题应该很简单。
>
> 如果你持久化的是简单的键值对，可以分别使用 `vscode.ExtensionContext.workspaceState` 或 `vscode.ExtensionContext.globalState` 来存储特定于工作区的或全局的状态信息。如果你的数据比键值对更复杂，`globalStorageUri` 和 `storageUri` 属性提供了“安全”的 URI，你可以用它们在文件中读写全局的或特定于工作区的信息。
>
> 使用这些 API：

```TypeScript
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(
        vscode.commands.registerCommand('myAmazingExtension.persistWorkspaceData', async () => {
            if (!context.storageUri) {
                return;
            }

            // 如果扩展的工作区存储文件夹还不存在，就创建它
            try {
                // 文件夹不存在时，会抛出一个错误
                await vscode.workspace.fs.stat(context.storageUri);
            } catch {
                // 创建扩展的工作区存储文件夹
                await vscode.workspace.fs.createDirectory(context.storageUri)
            }

            const workspaceData = vscode.Uri.joinPath(context.storageUri, 'workspace-data.json');
            const writeData = new TextEncoder().encode(JSON.stringify({ now: Date.now() }));
            vscode.workspace.fs.writeFile(workspaceData, writeData);
        }
    ));

    context.subscriptions.push(
        vscode.commands.registerCommand('myAmazingExtension.persistGlobalData', async () => {

        if (!context.globalStorageUri) {
            return;
        }

        // 如果扩展的全局（跨工作区）文件夹还不存在，就创建它
        try {
            // 文件夹不存在时，会抛出一个错误
            await vscode.workspace.fs.stat(context.globalStorageUri);
        } catch {
            await vscode.workspace.fs.createDirectory(context.globalStorageUri)
        }

        const workspaceData = vscode.Uri.joinPath(context.globalStorageUri, 'global-data.json');
        const writeData = new TextEncoder().encode(JSON.stringify({ now: Date.now() }));
        vscode.workspace.fs.writeFile(workspaceData, writeData);
    ));
}
```

**原文代码的问题：** 第二个命令的箭头函数缺少结尾的 `}`，倒数第三行应为 `}));`，否则无法编译。另外 `writeFile` 返回的是 Thenable，应该 `await` 它，否则写入失败时错误会被吞掉。

| 存储 | 范围 | 适合 |
|---|---|---|
| `context.globalState` | 所有工作区共享 | 简单的键值（如“是否已显示过欢迎页”） |
| `context.workspaceState` | 当前工作区 | 简单的键值（如这个项目上次选择的配置） |
| `context.globalStorageUri` | 所有工作区共享的文件夹 | 较大或复杂的数据（缓存、下载的文件） |
| `context.storageUri` | 当前工作区的文件夹（没有打开工作区时为 `undefined`） | 与项目相关的较大数据 |

（这些在 [常见能力](../extension-capabilities/common-capabilities.md#data-storage) 中也介绍过。注意这些 URI 指向的是扩展运行所在的机器：工作区扩展在远程时，数据就存在远程。使用 `vscode.workspace.fs` 而不是 Node 的 `fs`，在 Web 扩展中也能工作。）

<a id="sync-user-global-state-between-machines"></a>
### 在机器之间同步用户的全局状态（Sync user global state between machines）

> 如果你的扩展需要在不同的机器之间保留一些用户状态，请使用 `vscode.ExtensionContext.globalState.setKeysForSync` 把这些状态提供给[设置同步](https://code.visualstudio.com/docs/configure/settings-sync)。这有助于避免在多台机器上向用户显示相同的欢迎页或更新页面。
>
> 在[扩展能力](../extension-capabilities/common-capabilities.md#data-storage)主题中有一个使用 `setKeysforSync` 的示例。

```ts
context.globalState.setKeysForSync(['myExtension.welcomeShown']);
```

（原文第二处写成了 `setKeysforSync`，正确的方法名是 `setKeysForSync`。）

<a id="persisting-secrets"></a>
### 持久化机密信息（Persisting secrets）

> 如果你的扩展需要持久化密码或其他机密信息，你可能会想使用 Visual Studio Code 的 [SecretStorage API](https://code.visualstudio.com/api/references/vscode-api#SecretStorage)，它提供了一种在文件系统上以加密方式安全地存储文本的方法。例如，在桌面版上，我们使用 Electron 的 [safeStorage API](https://www.electronjs.org/docs/latest/api/safe-storage) 在把机密信息存储到文件系统之前对其进行加密。这个 API 总是把机密信息存储在客户端一侧，但无论你的扩展在哪里运行，你都可以使用这个 API，并取回相同的机密值。

> **注意**：这个 API 是持久化密码和机密信息的推荐方式。你**不应该**使用 `vscode.ExtensionContext.workspaceState` 或 `vscode.ExtensionContext.globalState` 来存储你的机密信息，因为这些 API 以明文形式存储数据。

> 下面是一个示例：

```typescript
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    // ...
    const myApiKey = context.secrets.get('apiKey');
    // ...
    context.secrets.delete('apiKey');
    // ...
    context.secrets.store('apiKey', myApiKey);
}
```

（这个示例只是列出了三个方法，不能直接运行：`get` 返回的是 `Thenable<string | undefined>`，需要 `await`；而 `store` 的第二个参数必须是 `string`。正确的写法如下。）

```ts
export async function activate(context: vscode.ExtensionContext) {
    const myApiKey = await context.secrets.get('apiKey');          // 读取，不存在时为 undefined
    if (!myApiKey) {
        const input = await vscode.window.showInputBox({ prompt: '请输入 API Key', password: true });
        if (input) { await context.secrets.store('apiKey', input); } // 保存
    }
    // await context.secrets.delete('apiKey');                     // 删除（例如用户退出登录时）
}
```

<a id="using-the-clipboard"></a>
### 使用剪贴板（Using the clipboard）

> 过去，扩展作者使用 `clipboardy` 等 Node.js 模块与剪贴板交互。遗憾的是，如果你在一个工作区扩展中使用这些模块，它们会使用远程的剪贴板，而不是用户本地的剪贴板。VS Code 的剪贴板 API 解决了这个问题。无论调用它的是哪种扩展，它总是在本地运行。
>
> 在扩展中使用 VS Code 的剪贴板 API：

```typescript
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(vscode.commands.registerCommand('myAmazingExtension.clipboardIt', async () => {
        // 从剪贴板读取
        const text = await vscode.env.clipboard.readText();

        // 写入剪贴板
        await vscode.env.clipboard.writeText(`It looks like you're copying "${text}". Would you like help?`);
    }));
}
```

（写入的文字意思是：“看起来你正在复制 "……"。需要帮忙吗？”）

<a id="opening-something-in-a-local-browser-or-application"></a>
### 在本地浏览器或应用程序中打开某些东西（Opening something in a local browser or application）

> 启动一个进程，或者使用 `opn` 这样的模块，为特定的 URI 启动浏览器或其他应用程序，在本地场景中可以很好地工作，但工作区扩展是在远程运行的，这可能导致应用程序在错误的一侧启动。VS Code 远程开发**部分地**模拟（shim）了 `opn` node 模块，让现有的扩展可以正常运行。你可以用一个 URI 调用这个模块，VS Code 会让这个 URI 的默认应用程序出现在客户端一侧。不过，这并不是一个完整的实现，因为不支持选项，也不会返回 `child_process` 对象。
>
> 我们建议扩展不要依赖第三方 node 模块，而是利用 `vscode.env.openExternal` 方法，为给定的 URI 在你的本地操作系统上启动默认注册的应用程序。更棒的是，`vscode.env.openExternal` **会自动进行 localhost 端口转发！** 你可以用它指向远程机器或 codespace 上的一个本地 Web 服务器，即使那个端口在外部被阻止，也能提供内容。

> **注意**：目前，Codespaces 基于浏览器的编辑器中的转发机制只支持 **http 和 https 请求**。不过，从 VS Code 连接到 codespace 时，你可以与任何 TCP 连接交互。

> 使用 `vscode.env.openExternal` API：

```typescript
import * as vscode from 'vscode';

export async function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(vscode.commands.registerCommand('myAmazingExtension.openExternal', () => {

        // 示例 1 - 在默认浏览器中打开 VS Code 主页。
        vscode.env.openExternal(vscode.Uri.parse('https://code.visualstudio.com'));

        // 示例 2 - 打开一个自动转发的 localhost HTTP 服务器。
        vscode.env.openExternal(vscode.Uri.parse('http://localhost:3000'));

        // 示例 3 - 打开默认的电子邮件应用程序。
        vscode.env.openExternal(vscode.Uri.parse('mailto:<fill in your email here>'));
    }));
}
```

“自动端口转发”的意思：示例 2 中，你的扩展在远程机器上启动了一个监听 3000 端口的服务器。直接让用户本地的浏览器打开 `http://localhost:3000` 是访问不到的（那是用户自己电脑的 3000 端口）。`openExternal` 会先把远程的 3000 端口转发到本地的某个端口，再在本地浏览器中打开转发后的地址。

<a id="forwarding-localhost"></a>
### 转发 localhost（Forwarding localhost）

> 虽然 [`vscode.env.openExternal` 中的 localhost 转发机制很有用](#opening-something-in-a-local-browser-or-application)，但也可能有一些情况，你想转发某些东西，却不想真的启动一个新的浏览器窗口或应用程序。这就是 `vscode.env.asExternalUri` API 的用武之地。

> **注意**：目前，Codespaces 基于浏览器的编辑器中的转发机制只支持 **http 和 https 请求**。不过，从 VS Code 连接到 codespace 时，你可以与任何 TCP 连接交互。

> 使用 `vscode.env.asExternalUri` API：

```typescript
import * as vscode from 'vscode';
import { getExpressServerPort } from './server';

export async function activate(context: vscode.ExtensionContext) {

    const dynamicServerPort = await getWebServerPort();

    context.subscriptions.push(vscode.commands.registerCommand('myAmazingExtension.forwardLocalhost', async () =>

        // 让这个端口在本地可用，并获取完整的 URI
        const fullUri = await vscode.env.asExternalUri(
            vscode.Uri.parse(`http://localhost:${dynamicServerPort}`));

        // ……用 fullUri 做一些事情……

    }));
}
```

（原文代码有两处错误：导入的是 `getExpressServerPort`，调用的却是 `getWebServerPort`；`async () =>` 后面直接写了多条语句，缺少函数体的 `{`。修正后是 `async () => { const fullUri = ...; }`。`./server` 是示例中假设的、启动 Web 服务器并返回端口的模块。）

> 需要特别注意的是，这个 API 返回的 URI **可能根本不会引用 localhost**，所以你应该完整地使用它。这对 Codespaces 基于浏览器的编辑器尤其重要，因为在那里不能使用 localhost。

例如在 Codespaces 的浏览器中，返回的可能是 `https://xxxx-3000.app.github.dev/` 这样的地址。所以不要从返回的 URI 中取出端口号再自己拼接，而是原样使用整个 URI。

<a id="callbacks-and-uri-handlers"></a>
### 回调和 URI 处理程序（Callbacks and URI handlers）

> `vscode.window.registerUriHandler` API 允许你的扩展注册一个自定义的 URI，如果在浏览器中打开这个 URI，就会触发你的扩展中的一个回调函数。注册 URI 处理程序的一个常见用例，是在实现用 [OAuth 2.0](https://oauth.net/2/) 身份验证提供者（例如 Azure AD）登录某个服务时。不过，它可以用于任何你希望外部应用程序或浏览器向你的扩展发送信息的场景。
>
> 无论你的扩展实际运行在哪里（本地或远程），VS Code 中的远程开发和 Codespaces 扩展都会透明地处理把 URI 传给你的扩展的工作。但是，`vscode://` URI 在 Codespaces 基于浏览器的编辑器中不起作用，因为在浏览器之类的东西中打开这些 URI，会尝试把它们传给本地的 VS Code 客户端，而不是基于浏览器的编辑器。幸运的是，使用 `vscode.env.asExternalUri` API 可以很容易地解决这个问题。
>
> 我们组合使用 `vscode.window.registerUriHandler` 和 `vscode.env.asExternalUri`，来实现一个 OAuth 身份验证回调的示例：

```typescript
import * as vscode from 'vscode';

// 这是 package.json 中的 ${publisher}.${name}
const extensionId = 'my.amazing-extension';

export async function activate(context: vscode.ExtensionContext) {

    // 为身份验证回调注册一个 URI 处理程序
    vscode.window.registerUriHandler({
        handleUri(uri: vscode.Uri): vscode.ProviderResult<void> {

            // 在这里添加身份验证完成时要执行的代码。
            if (uri.path === '/auth-complete') {
                vscode.window.showInformationMessage('Sign in successful!');
            }

        }
    });

    // 注册一个登录命令
    context.subscriptions.push(vscode.commands.registerCommand(`${extensionId}.signin`, async () => {

        // 为处理程序获取一个可以从外部访问的回调 URI，供身份验证提供者使用
        const callbackUri = await vscode.env.asExternalUri(vscode.Uri.parse(`${vscode.env.uriScheme}://${extensionId}/auth-complete`));

        // 在这里添加与身份验证提供者集成的代码，这里我们假装一下。
        vscode.env.clipboard.writeText(callbackUri.toString());
        await vscode.window.showInformationMessage('Open the URI copied to the clipboard in a browser window to authorize.');
    }));
}
```

> 在 VS Code 中运行这个示例时，它会设置一个 `vscode://` 或 `vscode-insiders://` URI，可以用作身份验证提供者的回调。在 Codespaces 基于浏览器的编辑器中运行时，它会设置一个 `https://*.github.dev` URI，无需任何代码更改或特殊条件。
>
> 虽然 OAuth 超出了本文的范围，但请注意，如果你把这个示例改编用于一个真正的身份验证提供者，你可能需要在提供者前面构建一个代理服务。这是因为并不是所有的提供者都允许 `vscode://` 回调 URI，还有一些提供者不允许通过 HTTPS 的回调使用通配符主机名。我们还建议尽可能使用 [OAuth 2.0 授权码 + PKCE 流程](https://oauth.net/2/pkce/)（例如，Azure AD 支持 PKCE），以提高回调的安全性。

几点说明：

- `vscode.env.uriScheme` 会根据当前的产品返回 `vscode` 或 `vscode-insiders`，所以示例没有写死 scheme。URI 的 authority 必须是扩展 ID，见 [激活事件中的 onUri](../references/activation-events.md#onUri)。
- `registerUriHandler` 返回一个 Disposable，示例中没有把它加入 `context.subscriptions`，最好加上。
- 两条消息的意思分别是“登录成功！”和“请在浏览器窗口中打开复制到剪贴板的 URI 以进行授权”。
- 如果你只是想登录 GitHub 或 Microsoft 账户，更简单的做法是直接使用内置的身份验证提供者：`vscode.authentication.getSession('github', ['repo'], { createIfNone: true })`，不需要自己处理回调。

<a id="varying-behaviors-when-running-remotely-or-in-the-codespaces-browser-editor"></a>
### 在远程或 Codespaces 浏览器编辑器中运行时改变行为（Varying behaviors when running remotely or in the Codespaces browser editor）

> 在某些情况下，你的工作区扩展可能需要在远程运行时改变它的行为。在另一些情况下，你可能想在 Codespaces 基于浏览器的编辑器中运行时改变它的行为。VS Code 提供了三个 API 来检测这些情况：`vscode.env.uiKind`、`extension.extensionKind` 和 `vscode.env.remoteName`。
>
> 接下来，你可以这样使用这三个 API：

```typescript
import * as vscode from 'vscode';

export async function activate(context: vscode.ExtensionContext) {

    // 在本地运行时 extensionKind 返回 ExtensionKind.UI，所以用它来检测是否在远程
    const extension = vscode.extensions.getExtension('your.extensionId');
    if (extension.extensionKind === vscode.ExtensionKind.Workspace) {
        vscode.window.showInformationMessage('I am running remotely!');
    }

    // Codespaces 基于浏览器的编辑器中，uiKind 会返回 UIKind.Web
    if (vscode.env.uiKind === vscode.UIKind.Web) {
        vscode.window.showInformationMessage('I am running in the Codespaces browser editor!');
    }

    // 如果使用的是本地工作区，VS Code 的 remoteName 会返回 undefined
    if (typeof(vscode.env.remoteName) === 'undefined') {
        vscode.window.showInformationMessage('Not currently connected to a remote workspace.');
    }

}
```

| API | 值 | 回答的问题 |
|---|---|---|
| `extension.extensionKind` | `ExtensionKind.UI` / `ExtensionKind.Workspace` | **我的扩展**运行在本地还是远程？ |
| `vscode.env.uiKind` | `UIKind.Desktop` / `UIKind.Web` | 用户用的是桌面版还是浏览器？ |
| `vscode.env.remoteName` | `undefined` / `'ssh-remote'`、`'dev-container'`、`'wsl'`、`'codespaces'` 等 | 当前窗口连接到了哪种远程环境？ |

（示例中 `getExtension` 可能返回 `undefined`，严格模式下需要写 `extension?.extensionKind`。获取自己的扩展对象更简单的方式是 `context.extension.extensionKind`。注意 `remoteName` 不是 `undefined` 并不代表**你的扩展**在远程运行：一个 UI 扩展在远程窗口中运行时，`remoteName` 有值，但 `extensionKind` 是 `UI`。）

<a id="communicating-between-extensions-using-commands"></a>
### 使用命令在扩展之间通信（Communicating between extensions using commands）

> 有些扩展会在激活时返回一些 API，供其他扩展使用（通过 `vscode.extension.getExtension(extensionName).exports`）。如果涉及的所有扩展都在同一侧（全部是 UI 扩展，或者全部是工作区扩展），这些 API 可以正常工作，但它们在 UI 扩展和工作区扩展之间无法工作。
>
> 幸运的是，无论扩展位于哪里，VS Code 都会自动把执行的任何命令路由到正确的扩展。你可以自由地调用任何命令（包括由其他扩展提供的命令），而不必担心影响。
>
> 如果你有一组需要彼此交互的扩展，使用一个私有命令来公开功能，可以帮助你避免意外的影响。不过，你作为参数传入的任何对象，在传输之前都会被“字符串化”（`JSON.stringify`），所以这个对象不能有循环引用，并且在另一侧会变成一个“普通的 JavaScript 对象”。
>
> 例如：

```typescript
import * as vscode from 'vscode';

export async function activate(context: vscode.ExtensionContext) {
    // 注册私有的 echo 命令
    const echoCommand = vscode.commands.registerCommand('_private.command.called.echo',
        (value: string) => {
            return value;
        }
    );
    context.subscriptions.push(echoCommand);
}
```

> 关于使用命令的详细信息，请参见[命令 API 指南](../extension-guides/command.md)。

（原文的 `vscode.extension.getExtension` 少了一个 s，正确的是 `vscode.extensions.getExtension`。以 `_` 开头的命令不会出现在命令面板中，适合作为扩展之间的“私有接口”。调用方：`const r = await vscode.commands.executeCommand<string>('_private.command.called.echo', 'hello')`。“普通对象”意味着传 `vscode.Uri` 这类类实例过去，另一侧收到的可能只是一个带有 `scheme`、`path` 等字段的普通对象（VS Code 对 `Uri` 等少数内置类型有特殊处理，会还原成真正的实例），自定义类的方法则会全部丢失。）

---

<a id="using-the-webview-api"></a>
## 使用 Webview API（Using the Webview API）

> 和剪贴板 API 一样，即使是从工作区扩展中使用，[Webview API](../extension-guides/webview.md) 也总是在用户的本地机器上或浏览器中运行。这意味着很多基于 webview 的扩展应该能直接工作，即使在远程工作区或 Codespaces 中使用也一样。不过，有一些注意事项需要了解，以便你的 webview 扩展在远程运行时也能正常工作。

<a id="always-use-aswebviewuri"></a>
### 始终使用 asWebviewUri（Always use asWebviewUri）

> 你应该使用 `asWebviewUri` API 来管理扩展的资源。使用这个 API，而不是硬编码 `vscode-resource://` URI，是确保 Codespaces 基于浏览器的编辑器能够与你的扩展一起工作所必需的。详情请参见 [Webview API](../extension-guides/webview.md) 指南，这里是一个简单的示例。
>
> 你可以这样在内容中使用这个 API：

```typescript
// 创建 webview
const panel = vscode.window.createWebviewPanel(
    'catWebview',
    'Cat Webview',
    vscode.ViewColumn.One);

// 获取内容的 Uri
const catGifUri = panel.webview.asWebviewUri(
    vscode.Uri.joinPath(context.extensionUri, 'media', 'cat.gif'));

// 在你的内容中引用它
panel.webview.html = `<!DOCTYPE html>
<html>
<body>
    <img src="${catGifUri}" width="300" />
</body>
</html>`;
```

（扩展在远程时，`cat.gif` 文件在远程机器上，而 webview 在本地显示。`asWebviewUri` 生成的地址会让 VS Code 通过连接把远程的文件传给本地的 webview。）

<a id="use-the-message-passing-api-for-dynamic-webview-content"></a>
### 使用消息传递 API 实现动态的 webview 内容（Use the message passing API for dynamic webview content）

> VS Code 的 webview 包含一个[消息传递](../extension-guides/webview.md#scripts-and-message-passing) API，它允许你在不使用本地 Web 服务器的情况下动态地更新 webview 的内容。即使你的扩展运行着一些你想要与之交互、以更新 webview 内容的本地 Web 服务，你也可以从扩展本身来完成，而不是直接从你的 HTML 内容中完成。
>
> 这是远程开发和 GitHub Codespaces 的一个重要模式，可以确保你的 webview 代码在 VS Code 和 Codespaces 基于浏览器的编辑器中都能工作。
>
> **为什么用消息传递，而不是 localhost Web 服务器？**
>
> 另一种模式是在一个 `iframe` 中提供 Web 内容，或者让 webview 的内容直接与一个 localhost 服务器交互。遗憾的是，默认情况下，webview 中的 `localhost` 会解析为开发者的本地机器。这意味着，对于一个在远程运行的工作区扩展，它创建的 webview 无法访问由这个扩展启动的本地服务器。即使你使用机器的 IP，你要连接的端口在云虚拟机或容器中通常也默认是被阻止的。即使这在 VS Code 中能工作，在 Codespaces 基于浏览器的编辑器中也不会工作。
>
> 下面是使用 Remote - SSH 扩展时这个问题的示意图，但这个问题在开发容器和 GitHub Codespaces 中同样存在：

![Webview 的问题](images/remote-extensions/webview-problem.png)

图中，本地的 VS Code 中运行着 WebView，远程（Azure 中的虚拟机）的 VS Code Server 中运行着工作区扩展，两者之间通过 SSH 隧道通信；工作区扩展在远程启动了一个“扩展的 Web 服务器（供 WebView 使用）”。WebView 想直接连接这个服务器，但这条连接被打上了红叉：它不经过 SSH 隧道，所以连不上。

> 如果可能，**你应该避免这样做**，因为它会让你的扩展变得复杂得多。[消息传递](../extension-guides/webview.md#scripts-and-message-passing) API 可以实现同样的用户体验，而不会带来这些麻烦。扩展本身会在远程一侧的 VS Code Server 中运行，所以它可以透明地与你的扩展因为 webview 传来的消息而启动的任何 Web 服务器交互。

**消息传递模式的数据流：**

```text
webview（本地）── postMessage({ type: 'getData' }) ──→ 扩展（远程）── fetch('http://localhost:端口') ──→ 远程的 Web 服务器
webview（本地）←── postMessage({ type: 'data', ... }) ── 扩展（远程）←──────────── 响应 ─────────────┘
```

扩展和服务器在同一台机器上，所以扩展访问 `localhost` 没有任何问题；webview 只与扩展通信，而 `postMessage` 会由 VS Code 自动通过远程连接转发。

<a id="workarounds-for-using-localhost-from-a-webview"></a>
### 在 webview 中使用 localhost 的变通方法（Workarounds for using localhost from a webview）

> 如果你出于某种原因不能使用[消息传递](../extension-guides/webview.md#scripts-and-message-passing) API，有两个选项可以与 VS Code 中的远程开发和 GitHub Codespaces 扩展一起工作。
>
> 每个选项都允许 webview 的内容通过 VS Code 与 VS Code Server 通信所用的同一个通道进行路由。例如，如果我们更新上一节中 Remote - SSH 的示意图，你会得到这样的结果：

![Webview 的解决方案](images/remote-extensions/webview-solution.png)

（与上一张图相比，WebView 到“扩展的 Web 服务器”的连接现在也经过了 SSH 隧道，所以能连上了。）

<a id="option-1---use-asexternaluri"></a>
### 选项 1 - 使用 asExternalUri（Option 1 - Use asExternalUri）

> VS Code 1.40 引入了 `vscode.env.asExternalUri` API，允许扩展以编程的方式把本地的 `http` 和 `https` 请求转发到远程。当你的扩展在 VS Code 中运行时，你可以使用同一个 API，把来自 webview 的请求转发到 `localhost` Web 服务器。
>
> 使用这个 API 为 iframe 获取一个完整的 URI，并把它添加到你的 HTML 中。你还需要在 webview 中启用脚本，并在你的 HTML 内容中添加一个 CSP。

```typescript
// 使用 asExternalUri 获取 Web 服务器的 URI
const dynamicWebServerPort = await getWebServerPort();
const fullWebServerUri = await vscode.env.asExternalUri(
        vscode.Uri.parse(`http://localhost:${dynamicWebServerPort}`)
    );

// 创建 webview
const panel = vscode.window.createWebviewPanel(
    'asExternalUriWebview',
    'asExternalUri Example',
    vscode.ViewColumn.One, {
        enableScripts: true
    });

const cspSource = panel.webview.cspSource;
panel.webview.html = `<!DOCTYPE html>
        <head>
            <meta
                http-equiv="Content-Security-Policy"
                content="default-src 'none'; frame-src ${fullWebServerUri} ${cspSource} https:; img-src ${cspSource} https:; script-src ${cspSource}; style-src ${cspSource};"
            />
        </head>
        <body>
        <!-- 来自 Web 服务器的所有内容都必须放在一个 iframe 中 -->
        <iframe src="${fullWebServerUri}">
    </body>
    </html>`;
```

> 注意，上面示例中在 `iframe` 里提供的任何 HTML 内容，**都需要使用相对路径**，而不是硬编码 `localhost`。

（原文 HTML 中的 `<iframe ...>` 缺少结束标签 `</iframe>`，开头也缺少 `<html>`。CSP 中的 `frame-src ${fullWebServerUri}` 允许 iframe 加载这个地址，见 [Webview 的内容安全策略](../extension-guides/webview.md#content-security-policy)。）

<a id="option-2---use-a-port-mapping"></a>
### 选项 2 - 使用端口映射（Option 2 - Use a port mapping）

> 如果你**不打算支持 Codespaces 基于浏览器的编辑器**，可以使用 webview API 中提供的 `portMapping` 选项。（这种方法也适用于从 VS Code 客户端使用 Codespaces，但不适用于浏览器。）
>
> 要使用端口映射，在创建 webview 时传入一个 `portMapping` 对象：

```typescript
const LOCAL_STATIC_PORT = 3000;
const dynamicServerPort = await getWebServerPort();

// 创建 webview 并传入 portMapping
const panel = vscode.window.createWebviewPanel(
    'remoteMappingExample',
    'Remote Mapping Example',
    vscode.ViewColumn.One, {
        portMapping: [
            // 这把 webview 中的 localhost:3000 映射到远程主机上的 Web 服务器端口。
            { webviewPort: LOCAL_STATIC_PORT, extensionHostPort: dynamicServerPort }
        ]
    });

// 在你的 HTML 中引用的任何完整 URI 中引用这个端口。
panel.webview.html = `<!DOCTYPE html>
    <body>
        <!-- 这会解析到远程机器上的动态服务器端口 -->
        <img src="http://localhost:${LOCAL_STATIC_PORT}/canvas.png">
    </body>
    </html>`;
```

> 在这个例子中，无论是远程还是本地的情况，对 `http://localhost:3000` 发出的任何请求，都会被自动映射到一个 Express.js Web 服务器所运行的动态端口上。

| | 选项 1：`asExternalUri` | 选项 2：`portMapping` |
|---|---|---|
| 支持 Codespaces 浏览器编辑器 | 支持 | 不支持 |
| HTML 中的地址 | 使用 API 返回的完整 URI | 固定写 `http://localhost:3000` |
| 适用 | 需要支持所有环境 | 只需支持桌面版 VS Code |

---

<a id="using-native-nodejs-modules"></a>
## 使用原生 Node.js 模块（Using native Node.js modules）

> 与 VS Code 扩展捆绑在一起（或为它动态获取）的原生模块，必须[使用 Electron 的 `electron-rebuild`](https://electronjs.org/docs/tutorial/using-native-node-modules) 重新编译。但是，VS Code Server 运行的是一个标准的（非 Electron 的）Node.js 版本，这可能会导致二进制文件在远程使用时失败。
>
> 要解决这个问题：
>
> 1. 为 VS Code 所附带的 Node.js 的 “modules” 版本，包含（或动态获取）两套二进制文件（Electron 版和标准 Node.js 版）。
> 2. 检查 `vscode.extensions.getExtension('your.extensionId').extensionKind === vscode.ExtensionKind.Workspace`，根据扩展是在远程还是在本地运行，设置正确的二进制文件。
> 3. 你可能还想同时[按照类似的逻辑](#supporting-nonx8664-hosts-or-alpine-linux-containers)，添加对非 x86_64 目标和 Alpine Linux 的支持。
>
> 你可以通过 **Help > Developer Tools**（帮助 > 开发者工具）并在控制台中输入 `process.versions.modules`，找到 VS Code 使用的 “modules” 版本。不过，为了确保原生模块在不同的 Node.js 环境中都能无缝工作，你可能需要针对所有可能的 Node.js “modules” 版本和你想支持的平台（Electron Node.js、官方 Node.js 的 Windows / Darwin / Linux 版本、所有版本）编译原生模块。[node-tree-sitter](https://github.com/tree-sitter/node-tree-sitter/releases/tag/v0.14.0) 模块是一个在这方面做得很好的例子。

**“modules” 版本**（即 `NODE_MODULE_VERSION`，Node 的 ABI 版本号）决定了一个编译好的 `.node` 文件能在哪个 Node.js / Electron 版本上加载。Electron 内置的 Node 与同版本号的官方 Node 的 ABI 往往不同，所以需要两套。（菜单名现在是 **Help > Toggle Developer Tools**。）

**更简单的替代方案：**

- 能不用原生模块就不用：很多功能有纯 JavaScript 或 WebAssembly 的实现（例如 `tree-sitter` 有 `web-tree-sitter` 的 WASM 版本），WASM 在所有平台、本地和远程、甚至 Web 扩展中都能运行。
- 必须用时，使用 [平台特定的扩展](../working-with-extensions/publishing-extension.md#platform-specific-extensions)，为每个平台分别打包。
- 把原生功能放到一个独立的可执行程序中，扩展通过子进程或语言服务器调用它（这是语言服务器的常见做法）。

---

<a id="supporting-non-x8664-hosts-or-alpine-linux-containers"></a>
<a id="supporting-nonx8664-hosts-or-alpine-linux-containers"></a>
## 支持非 x86_64 主机或 Alpine Linux 容器（Supporting non-x86_64 hosts or Alpine Linux containers）

> 如果你的扩展完全是用 JavaScript / TypeScript 编写的，你可能不需要做任何事情，就能让你的扩展支持其他处理器架构或基于 `musl` 的 Alpine Linux。
>
> 但是，如果你的扩展在 Debian 9+、Ubuntu 16.04+ 或 RHEL / CentOS 7+ 的远程 SSH 主机、容器或 WSL 上能工作，却在受支持的非 x86_64 主机（例如 ARMv7l）或 Alpine Linux 容器上失败，那么这个扩展可能包含了特定于 x86_64 `glibc` 的原生代码或运行时，它们在这些架构 / 操作系统上会失败。
>
> 例如，你的扩展可能只包含 x86_64 编译版本的原生模块或运行时。对于 Alpine Linux，由于 Alpine Linux（`musl`）与其他发行版（`glibc`）在 `libc` 的实现方式上存在[根本性的差异](https://wiki.musl-libc.org/functional-differences-from-glibc.html)，所包含的原生代码或运行时可能无法工作。
>
> 要解决这个问题：
>
> 1. 如果你是动态获取编译好的代码，可以通过使用 `process.arch` 检测非 x86_64 的目标，下载为正确架构编译的版本来添加支持。如果你是在扩展中包含了所有受支持架构的二进制文件，可以用这个逻辑来选用正确的那个。
>
> 2. 对于 Alpine Linux，你可以使用 `await fs.exists('/etc/alpine-release')` 检测操作系统，然后再次下载或使用适用于基于 `musl` 的操作系统的正确二进制文件。
>
> 3. 如果你不想支持这些平台，可以使用同样的逻辑，改为提供一条友好的错误消息。
>
> 需要注意的是，一些第三方 npm 模块包含会导致这个问题的原生代码。所以，在某些情况下，你可能需要与 npm 模块的作者合作，添加额外的编译目标。

（Node.js 的 `fs.exists` 已被弃用，也没有 Promise 版本，可以写成 `fs.existsSync('/etc/alpine-release')`，或 `await fs.promises.access(...)` 配合 try/catch。`process.arch` 的值如 `'x64'`、`'arm64'`、`'arm'`。如果使用 [平台特定的扩展](../working-with-extensions/publishing-extension.md#platform-specific-extensions)，市场会为 `linux-arm64`、`alpine-x64` 等平台分发对应的包，就不需要在运行时做这些判断了。）

---

<a id="avoid-using-electron-modules"></a>
## 避免使用 Electron 模块（Avoid using Electron modules）

> 虽然依赖内置的 Electron 模块或扩展 API 没有公开的 VS Code 模块可能很方便，但需要注意的是，VS Code Server 运行的是一个标准的（非 Electron 的）Node.js 版本。在远程运行时，这些模块会缺失。有少数例外，那些地方有专门的代码让它们能够工作。
>
> 使用 Node.js 的基础模块或你的扩展 VSIX 中的模块，以避免这些问题。如果你绝对必须使用一个 Electron 模块，请确保在模块缺失时有一个后备方案。
>
> 下面的示例会在找到 Electron 的 `original-fs` node 模块时使用它，如果找不到，就退回到 Node.js 的基础 `fs` 模块。

```typescript
function requireWithFallback(electronModule: string, nodeModule: string) {
    try {
        return require(electronModule);
    }
    catch (err) { }
    return require(nodeModule);
}

const fs = requireWithFallback('original-fs', 'fs');
```

> 尽可能避免这些情况。

（`original-fs` 是 Electron 中“未经修改的 fs”：Electron 的 `fs` 会把 `.asar` 文件当作文件夹，而 `original-fs` 不会。此外，扩展**只能**依赖 `vscode` API，不要 `require` VS Code 自身的内部模块，它们随时可能变化，在远程和 Web 中也不存在。）

---

<a id="known-issues"></a>
## 已知问题（Known issues）

> 有一些扩展问题，可以通过为工作区扩展添加一些功能来解决。下表是一个正在考虑中的已知问题列表：

| 问题 | 说明 |
| --- | --- |
| **无法从工作区扩展访问连接的设备** | 访问本地连接设备的扩展，在远程运行时将无法连接到这些设备。克服这个问题的一种方法，是创建一个配套的 UI 扩展，它的工作是访问连接的设备，并提供远程扩展也可以调用的命令。<br>另一种方法是反向隧道，这在一个 [VS Code 仓库的 issue](https://github.com/microsoft/vscode/issues/100222) 中被跟踪。 |

（“连接的设备”例如通过 USB 连接的开发板、串口设备。配套 UI 扩展的方案，就是上文 [处理远程扩展的依赖](#handling-dependencies-with-remote-extensions) 和 [使用命令在扩展之间通信](#communicating-between-extensions-using-commands) 的组合：本地 UI 扩展负责访问设备并注册命令，远程工作区扩展通过 `executeCommand` 调用它。）

---

<a id="questions-and-feedback"></a>
## 问题和反馈（Questions and feedback）

> - 请参见[技巧和窍门](https://code.visualstudio.com/docs/remote/troubleshooting)或[常见问题](https://code.visualstudio.com/docs/remote/faq)。
> - 在 [Stack Overflow](https://stackoverflow.com/questions/tagged/vscode-remote) 上搜索答案。
> - [为一个功能投票或请求一个新功能](https://aka.ms/vscode-remote/feature-requests)，搜索[现有的 issue](https://aka.ms/vscode-remote/issues)，或者[报告一个问题](https://aka.ms/vscode-remote/issues/new)。
> - 创建一个[开发容器模板（Template）](https://containers.dev/templates)或[功能（Feature）](https://containers.dev/features)供他人使用。
> - 为[我们的文档](https://github.com/microsoft/vscode-docs)或 [VS Code](https://github.com/microsoft/vscode) 做贡献。
> - 详情请参见我们的 [CONTRIBUTING](https://aka.ms/vscode-remote/contributing) 指南。

---

## 本篇小结

```text
远程开发中有两种扩展
  UI 扩展：在用户本地运行（主题、快捷键、需要本地资源的扩展）
  工作区扩展：在工作区所在的机器上运行（语言服务、调试器、linter……），在远程的 VS Code Server 中
  extensionKind 控制位置；Developer: Show Running Extensions 查看实际位置；remote.extensionKind 设置临时测试

调试：连接远程环境 → 远程打开源码 → 远程 npm install → F5

原则：与“用户这一侧”相关的事一律用 vscode API
  存储：globalState / workspaceState / globalStorageUri / storageUri；同步：setKeysForSync
  机密：context.secrets（await get / store / delete）
  剪贴板：env.clipboard；打开链接：env.openExternal（自动端口转发）；转发端口：env.asExternalUri（原样使用返回的 URI）
  OAuth 回调：registerUriHandler + asExternalUri(`${env.uriScheme}://扩展ID/...`)
  检测环境：context.extension.extensionKind、env.uiKind、env.remoteName
  跨本地 / 远程通信：命令（参数会被 JSON 序列化），提供方用 "api": "none"

Webview：始终 asWebviewUri；用 postMessage 代替 webview 直连 localhost；
        必须直连时用 asExternalUri（全环境）或 portMapping（不支持浏览器）
原生模块 / 非 x86_64 / Alpine：准备多套二进制或使用平台特定扩展；尽量用 WASM 或纯 JS
不要依赖 Electron 模块或 VS Code 内部模块
```
