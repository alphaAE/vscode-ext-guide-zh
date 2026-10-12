# 扩展宿主（Extension Host）

> 原文：[Extension Host](https://code.visualstudio.com/api/advanced-topics/extension-host)
> 源文件：`microsoft/vscode-docs` → `api/advanced-topics/extension-host.md`（DateApproved: 10/7/2026）

> **扩展宿主（Extension Host）**负责运行扩展。

扩展宿主是一个**独立于 VS Code 界面的进程**（或浏览器中的 Web Worker）。你的扩展代码运行在这里，通过 `vscode` API 与界面通信。这样设计的好处是：扩展即使卡住或崩溃，也不会让编辑器本身失去响应。调试扩展时按 `F5` 打开的“扩展开发宿主”窗口，就是一个专门加载你正在开发的扩展的 VS Code 窗口。

---

<a id="extension-host-configurations"></a>
## 扩展宿主的配置（Extension Host configurations）

> 根据 VS Code 的配置，会有多个扩展宿主在不同的位置、以不同的运行时运行。
>
> - local（本地）– 一个在本地运行的 Node.js 扩展宿主，与用户界面在同一台机器上。
> - web – 一个在浏览器中或本地运行的 Web 扩展宿主，与用户界面在同一台机器上。
> - remote（远程）– 一个在容器或远程位置运行的 Node.js 扩展宿主。
>
> 下表显示了在 VS Code 的各种配置中，有哪些扩展宿主可用：

| 配置 | 本地扩展宿主 | Web 扩展宿主 | 远程扩展宿主 |
| --- | --- | --- | --- |
| 桌面版 VS Code | ✔️ | ✔️ | |
| [使用远程开发的 VS Code](https://code.visualstudio.com/docs/remote/remote-overview)（容器、SSH、WSL、GitHub Codespace、隧道） | ✔️ | ✔️ | ✔️ |
| VS Code for the Web（vscode.dev、github.dev） | | ✔️ | |
| 搭配 Codespaces 的 VS Code for the Web | | ✔️ | ✔️ |

（桌面版也有 Web 扩展宿主：只有 `browser` 入口、没有 `main` 入口的扩展，在桌面版中也会运行在 Web 扩展宿主中。远程开发的细节见 [远程开发与 Codespaces 支持](./remote-extensions.md)。）

<a id="extension-host-runtimes"></a>
### 扩展宿主的运行时（Extension Host runtimes）

> - Node.js - 扩展运行在 Node.js 运行时中。由本地和远程扩展宿主使用。扩展需要一个 `main` 入口文件才能在其中运行。
> - Browser（浏览器）- 扩展运行在[浏览器 WebWorker](https://developer.mozilla.org/docs/Web/API/Web_Workers_API) 运行时中。由 Web 扩展宿主使用。扩展需要一个 `browser` 入口文件才能在其中运行。更多细节请参见 [Web 扩展指南](../extension-guides/web-extensions.md)。

| 运行时 | 入口字段 | 能用 Node.js API（`fs`、`child_process` 等）吗 |
|---|---|---|
| Node.js | `package.json` 的 `main` | 能 |
| 浏览器 WebWorker | `package.json` 的 `browser` | 不能（只有浏览器 API） |

<a id="preferred-extension-location"></a>
### 首选的扩展位置（Preferred extension location）

> 一个扩展被加载到哪个扩展宿主中，取决于：
>
> - VS Code 的配置所提供的可用扩展宿主。
> - 扩展的能力：它能在 Node.js 中运行，和 / 或能在 Web 中运行吗？如果没有指明，它提供了哪些贡献？
> - 扩展安装在哪里：本地机器、远程机器，或两者都有。
> - 扩展所偏好的位置：`extensionKind` 属性。
>
> `extensionKind` 是[扩展清单](../references/extension-manifest.md)中的一个属性。它允许扩展指定一个首选的运行位置。可以是工作区所在的机器（`workspace`），也可以是用户界面所在的机器（`ui`）。如果一个扩展两者都能运行，它可以指定一个偏好顺序。
>
> - `"extensionKind": ["workspace"]` — 表示这个扩展需要访问工作区的内容，因此需要在工作区所在的地方运行。可以是本地机器，也可以是远程机器或 Codespace。大多数扩展都属于这一类。
> - `"extensionKind": ["ui", "workspace"]` — 表示这个扩展**更喜欢**作为 UI 扩展运行，但对本地的资源、设备或能力没有任何硬性要求。使用 VS Code 时，如果这个扩展在本地存在，它会运行在 VS Code 的本地扩展宿主中，这意味着用户不必在远程上安装这个扩展。否则，如果它在工作区扩展宿主那里存在，它就会运行在那里。使用搭配 Codespaces 的 VS Code for the Web 时，它总是运行在远程扩展宿主中（因为没有可用的本地扩展宿主）。
> - `"extensionKind": ["workspace", "ui"]` — 表示这个扩展**更喜欢**作为工作区扩展运行，但对访问工作区内容没有任何硬性要求。使用 VS Code 时，如果这个扩展在远程工作区中存在，它会运行在 VS Code 的工作区扩展宿主中；否则，如果它在本地存在，就运行在 VS Code 的本地扩展宿主中。使用搭配 Codespaces 的 VS Code for the Web 时，它总是运行在远程扩展宿主中（因为没有可用的本地扩展宿主）。
> - `"extensionKind": ["ui"]` — 表示这个扩展**必须**在靠近 UI 的地方运行，因为它需要访问本地的资源、设备或能力，或者因为需要低延迟。在搭配 Codespaces 的 VS Code for the Web 的情况下，由于没有可用的本地扩展宿主，这样的扩展无法加载，除非它也是一个 [Web 扩展](../extension-guides/web-extensions.md)。那样的话，它会被加载到 Web 扩展宿主中，但有一个限制：它不能实例化 Web Worker。
>
> **注意**：之前的 VS Code 版本（<1.40）允许扩展用一个字符串指定单个位置，但这种写法已被弃用，改为用数组指定多个位置。
>
> 如果一个扩展既能在 Node.js 中运行，也能在浏览器中运行，那么只要有可用的 Node.js 扩展宿主，就会选择它。有一个例外：当配置是搭配 Codespaces 的 VS Code for the Web、并且 `extensionKind` 设为 `ui` 时，会优先选择 Web 扩展宿主，而不是远程扩展宿主。
>
> 如果一个扩展只能在 Web 中运行，无论 `extensionKind` 怎么设置，它都总是运行在 Web 扩展宿主中。我们建议在这种情况下不要定义 `extensionKind`。

**以“本地 Windows 电脑 + SSH 连接 Linux 服务器”为例：**

```text
本地机器（UI 所在）                         远程 Linux 服务器（工作区所在）
┌──────────────────────────┐               ┌──────────────────────────┐
│ VS Code 界面               │               │ 远程扩展宿主（Node.js）      │
│ 本地扩展宿主（Node.js）      │ ←── 网络 ──→ │   · 能读写服务器上的项目文件  │
│   · 颜色主题、快捷键映射      │               │   · 能运行服务器上的编译器    │
│   · 访问本地剪贴板、本地程序  │               │   · 大多数语言扩展、linter   │
└──────────────────────────┘               └──────────────────────────┘
      extensionKind: ["ui"]                      extensionKind: ["workspace"]
```

| `extensionKind` | 什么样的扩展 | 例子 |
|---|---|---|
| `["workspace"]` | 需要读写项目文件、运行项目相关的工具 | 语言服务器、linter、调试器、Git 相关扩展 |
| `["ui"]` | 需要本地机器上的东西，或要求低延迟 | 访问本地硬件或本地程序、快捷键映射 |
| `["ui", "workspace"]` | 两边都能运行，优先本地（这样不用在远程上再装一次） | 只操作编辑器文本、不依赖本地也不依赖工作区的工具 |
| `["workspace", "ui"]` | 两边都能运行，优先远程 | |

不写 `extensionKind` 时，VS Code 会根据扩展的内容推断：只有声明式贡献（主题、代码片段、语法等）而没有 `main` 的扩展可以在任何地方运行；有 `main` 的扩展默认按 `workspace` 处理。颜色主题、图标主题这类纯声明式扩展不需要关心这个问题。

---

<a id="stability-and-performance"></a>
## 稳定性和性能（Stability and Performance）

> VS Code 致力于为用户提供一个稳定、高性能的编辑器，行为不当的扩展不应该影响用户体验。VS Code 中的扩展宿主防止扩展：
>
> - 影响启动性能
> - 拖慢 UI 操作
> - 修改 UI
>
> 此外，VS Code 让扩展声明它们的[激活事件](../references/activation-events.md)，并延迟加载它们。例如，Markdown 扩展应该只在用户打开 Markdown 文件时才被加载。这确保了扩展不会消耗不必要的 CPU 和内存。

**“防止扩展修改 UI”的含义：** 扩展无法访问 VS Code 界面的 DOM，不能随意改变界面的样子。扩展只能通过 API 和贡献点，在 VS Code 允许的位置添加内容（视图、状态栏项、菜单、webview……）。这也是为什么有些“想要改变 VS Code 外观”的需求，用扩展做不到。这个设计的思路在 [扩展能力概览](../extension-capabilities/overview.md) 中有更多说明。

**排查扩展性能问题：** 命令面板中的 **Developer: Show Running Extensions** 可以看到每个扩展的激活耗时；**Developer: Restart Extension Host** 可以只重启扩展宿主而不重新加载整个窗口。

---

## 本篇小结

```text
扩展宿主：运行扩展的独立进程 / Web Worker，与 UI 隔离（扩展卡住不会卡住编辑器）

三种扩展宿主：local（本地 Node.js）、web（浏览器 WebWorker）、remote（远程 Node.js）
  入口：Node.js 用 main，浏览器用 browser

extensionKind（偏好顺序的数组）
  ["workspace"]：在工作区所在的机器上运行（大多数扩展）
  ["ui"]：必须在 UI 所在的机器上运行（本地资源、低延迟）
  ["ui","workspace"] / ["workspace","ui"]：两边都可，按顺序优先
  只有 browser 入口的扩展：总在 Web 扩展宿主中运行，不要设置 extensionKind

隔离：扩展不能访问界面 DOM；按激活事件延迟加载
```
