# 调试器扩展（Debugger Extension）

> 原文：[Debugger Extension](https://code.visualstudio.com/api/extension-guides/debugger-extension)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/debugger-extension.md`（DateApproved: 10/7/2026）

> VS Code 的调试架构让扩展作者可以轻松地把现有的调试器集成到 VS Code 中，同时让所有调试器共享一套统一的用户界面。
>
> VS Code 附带了一个内置的调试器扩展，即 [Node.js](https://nodejs.org) 调试器扩展，它很好地展示了 VS Code 支持的众多调试功能：

![VS Code 的调试功能](images/debugger-extension/debug-features.png)

> 这张截图展示了以下调试功能：
>
> 1. 调试配置管理。
> 2. 用于启动 / 停止和单步执行的调试操作。
> 3. 源代码断点、函数断点、条件断点、行内断点，以及日志点。
> 4. 堆栈跟踪，包括对多线程和多进程的支持。
> 5. 在视图和悬停提示中浏览复杂的数据结构。
> 6. 在悬停提示中或源代码行内显示变量的值。
> 7. 管理监视表达式。
> 8. 用于交互式求值、带自动补全的调试控制台。

截图中的黄色数字标注与上面的列表一一对应：

| 编号 | 位置 | 功能 |
|---|---|---|
| 1 | 左上角的配置下拉框（Server）、左下方的“已加载的脚本” | 调试配置管理 |
| 2 | 顶部中间的浮动工具栏 | 继续、单步跳过、单步进入、单步跳出、重启、停止 |
| 3 | 行号左侧的红点、左下方的“断点”列表 | 各种断点 |
| 4 | 左侧的“调用堆栈” | 堆栈跟踪 |
| 5 | 左侧的“变量”视图 | 浏览数据结构 |
| 6 | 编辑器中悬停弹出的对象内容 | 悬停显示变量值 |
| 7 | 左侧的“监视” | 监视表达式 |
| 8 | 底部的“调试控制台”及补全列表 | 交互式求值 |

**关键在于：这些界面都是 VS Code 提供的，与具体语言无关。** 调试器扩展的任务，只是把某种语言的调试器“接”到这套界面上。

> 本文档将帮助你创建一个调试器扩展，让任何调试器都能在 VS Code 中工作。

---

<a id="debugging-architecture-of-vs-code"></a>
## VS Code 的调试架构（Debugging Architecture of VS Code）

> VS Code 基于一个我们引入的抽象协议，实现了一个通用的（与语言无关的）调试器界面，用这个协议与调试器后端通信。由于调试器通常并不实现这个协议，所以需要一个中间层，把调试器“适配”到这个协议上。这个中间层通常是一个与调试器通信的独立进程。

![VS Code 调试架构](images/debugger-extension/debug-arch1.png)

图中，左边是 VS Code 中的**通用调试器界面**，右边是真正的**调试器**，中间蓝色的方块是**调试适配器**。VS Code 与调试适配器之间使用**调试适配器协议**通信，调试适配器再用调试器自己的方式与调试器通信。

> 我们把这个中间层称为**调试适配器（Debug Adapter，简称 DA）**，DA 与 VS Code 之间使用的抽象协议称为**调试适配器协议（Debug Adapter Protocol，简称 DAP）**。由于调试适配器协议独立于 VS Code，所以它有自己的[网站](https://microsoft.github.io/debug-adapter-protocol/)，你可以在那里找到[介绍和概述](https://microsoft.github.io/debug-adapter-protocol/overview)、详细的[规范](https://microsoft.github.io/debug-adapter-protocol/specification)，以及[已知的实现和支持工具](https://microsoft.github.io/debug-adapter-protocol/implementors/adapters/)的列表。DAP 的历史和背后的动机，在这篇[博客文章](https://code.visualstudio.com/blogs/2018/08/07/debug-adapter-protocol-website#why-the-need-for-decoupling-with-protocols)中有说明。

**为什么要多一个“适配器”？** 每种语言的调试器都有自己的接口：gdb 有自己的命令格式，Python、Node.js 的调试器又各不相同。如果 VS Code 要直接对接每一种调试器，就要写无数套对接代码。有了 DAP 之后：

```text
没有 DAP：  VS Code ──┬── gdb 专用对接代码
                      ├── Python 调试器专用对接代码
                      └── ……（每种都要单独写）

有了 DAP：  VS Code ── DAP ──┬── gdb 的适配器 ── gdb
                            ├── Python 的适配器 ── Python 调试器
                            └── ……（每个调试器写一个适配器，任何支持 DAP 的编辑器都能用）
```

这和 [语言服务器协议（LSP）](../language-extensions/language-server-extension-guide.md) 的思路完全相同：用一个统一的协议，把编辑器和具体实现分开。

DAP 的通信内容大致是这样的：VS Code 发送“请求”（比如“设置断点”“单步执行”“获取变量”），适配器回复“响应”；调试器状态变化时（比如“在断点处停下了”），适配器主动发送“事件”。

> 由于调试适配器独立于 VS Code，可以用在[其他开发工具](https://microsoft.github.io/debug-adapter-protocol/implementors/tools/)中，所以它们与 VS Code 基于扩展和贡献点的扩展架构并不匹配。
>
> 因此，VS Code 提供了一个贡献点 `debuggers`，可以用它在一个特定的调试类型（例如 Node.js 调试器的 `node`）下贡献一个调试适配器。每当用户启动该类型的调试会话时，VS Code 就会启动注册的 DA。
>
> 所以，在最简化的形式下，调试器扩展只是对一个调试适配器实现的声明式贡献，这个扩展基本上就是一个调试适配器的打包容器，不包含任何额外的代码。

![VS Code 调试架构 2](images/debugger-extension/debug-arch2.png)

和上一张图相比，调试适配器外面多了一个“Debugger Extension”（调试器扩展）的框：调试器扩展就是一个装着调试适配器的“包装盒”。

> 一个更实际的调试器扩展，会向 VS Code 贡献以下声明式内容中的大部分或全部：
>
> - 调试器支持的语言列表。VS Code 会为这些语言启用设置断点的界面。
> - 调试器引入的调试配置属性的 JSON schema。VS Code 用这个 schema 在 launch.json 编辑器中校验配置，并提供智能提示。请注意，不支持 JSON schema 中的 `$ref` 和 `definition` 结构。
> - VS Code 创建的初始 launch.json 中的默认调试配置。
> - 用户可以添加到 launch.json 文件中的调试配置代码片段。
> - 可以在调试配置中使用的变量的声明。
>
> 更多信息请参阅 [`contributes.breakpoints`](../references/contribution-points.md#contributes.breakpoints) 和 [`contributes.debuggers`](../references/contribution-points.md#contributes.debuggers) 参考。
>
> 除了上面这些纯声明式的贡献之外，调试扩展 API 还提供了以下基于代码的功能：
>
> - 为 VS Code 创建的初始 launch.json 动态生成默认的调试配置。
> - 动态决定要使用的调试适配器。
> - 在调试配置传给调试适配器之前，对其进行校验或修改。
> - 与调试适配器通信。
> - 向调试控制台发送消息。
>
> 在本文档的其余部分，我们将展示如何开发一个调试器扩展。

**`launch.json` 是什么？** 它是工作区 `.vscode` 目录下的调试配置文件，告诉 VS Code “按 F5 时用哪个调试器、调试哪个程序、带什么参数”。在 [你的第一个扩展](../get-started/your-first-extension.md) 中按 F5 能启动扩展开发宿主，就是因为脚手架生成了一个 `launch.json`。

---

<a id="the-mock-debug-extension"></a>
## Mock Debug 扩展（The Mock Debug Extension）

> 由于在本教程中从零开始创建一个调试适配器有点繁重，我们将从一个简单的 DA 开始，它是我们创建的一个用于学习的“调试适配器入门套件”。它叫作 _Mock Debug_，因为它并不与真正的调试器通信，而是模拟了一个调试器。Mock Debug 模拟了一个调试器，支持单步、继续、断点、异常和变量访问，但它并没有连接到任何真正的调试器。

Mock Debug 的玩法是：把一个普通的文本文件（比如 Markdown 文件）当作“程序”，每一行当作一条“语句”来“执行”。这样不需要真正的编程语言，就能体验调试器的全部交互。

> 在深入了解 mock-debug 的开发环境之前，我们先从 VS Code 扩展市场安装一个[预构建版本](https://marketplace.visualstudio.com/items/andreweinand.mock-debug)来试玩一下：
>
> - 切换到扩展视图，输入 “mock” 搜索 Mock Debug 扩展，
> - 点击“安装”，然后“重新加载”扩展。
>
> 试用 Mock Debug：
>
> - 新建一个空文件夹 `mock test`，用 VS Code 打开它。
> - 创建一个文件 `readme.md`，输入几行任意的文本。
> - 切换到运行和调试视图（`Ctrl+Shift+D`），选择**创建 launch.json 文件**链接。
> - VS Code 会让你选择一个“调试器”，以便创建一个默认的启动配置。选择 “Mock Debug”。
> - 按绿色的**开始**按钮，然后按 `Enter` 确认建议的文件 `readme.md`。
>
> 一个调试会话就开始了，你可以在 readme 文件中“单步”执行，设置断点并命中断点，还会遇到异常（如果某一行中出现了 `exception` 这个词）。

![Mock 调试器运行中](images/debugger-extension/mock-debug.gif)

> 在把 Mock Debug 作为你自己开发的起点之前，我们建议先卸载预构建的版本：
>
> - 切换到扩展视图，点击 Mock Debug 扩展的齿轮图标。
> - 执行“卸载”操作，然后“重新加载”窗口。

为什么要卸载：等一下要运行自己从源码编译的 Mock Debug。如果市场版本还装着，两个扩展注册的是同一个调试类型 `mock`，会互相冲突。

---

<a id="development-setup-for-mock-debug"></a>
## Mock Debug 的开发环境（Development Setup for Mock Debug）

> 现在我们来获取 Mock Debug 的源代码，并在 VS Code 中开始开发：

```bash
git clone https://github.com/microsoft/vscode-mock-debug.git
cd vscode-mock-debug
yarn
```

> 在 VS Code 中打开项目文件夹 `vscode-mock-debug`。
>
> 包里有什么？
>
> - `package.json` 是 mock-debug 扩展的清单：
>   - 它列出了 mock-debug 扩展的贡献。
>   - `compile` 和 `watch` 脚本用于把 TypeScript 源代码编译到 `out` 文件夹中，并监视之后的源代码修改。
>   - 依赖项 `vscode-debugprotocol`、`vscode-debugadapter` 和 `vscode-debugadapter-testsupport` 是 NPM 模块，它们简化了基于 Node 的调试适配器的开发。
> - `src/mockRuntime.ts` 是一个带有简单调试 API 的 _模拟_ 运行时。
> - 把运行时 _适配_ 到调试适配器协议的代码在 `src/mockDebug.ts` 中。在这里可以找到 DAP 各种请求的处理函数。
> - 由于调试器扩展的实现位于调试适配器中，所以根本不需要扩展代码（即在扩展宿主进程中运行的代码）。不过，Mock Debug 有一个小小的 `src/extension.ts`，因为它演示了调试器扩展的扩展代码中可以做些什么。

（这几个 npm 包后来已经迁移到 `@vscode` 作用域下，新名称为 `@vscode/debugprotocol`、`@vscode/debugadapter`、`@vscode/debugadapter-testsupport`。新项目请使用新名称，并以示例仓库中的 `package.json` 为准。）

项目中各部分的角色：

| 文件 | 角色 | 对应架构图中的 |
|---|---|---|
| `src/mockRuntime.ts` | 模拟的“调试器 / 运行时” | 右边的 Debugger |
| `src/mockDebug.ts` | 调试适配器：把 DAP 请求翻译成对运行时的调用 | 中间的 Debug Adapter |
| `src/extension.ts` | 扩展代码：动态配置、交互命令等（可选） | 外面的 Debugger Extension 框 |
| `package.json` | 声明调试类型、配置格式等 | 同上 |

开发自己的调试器扩展时，要替换的主要是前两个文件。

> 现在，选择 **Extension** 启动配置并按 `F5`，构建并启动 Mock Debug 扩展。一开始会把 TypeScript 源代码完整编译到 `out` 文件夹中。完整构建之后，会启动一个_监视任务_，编译你做的任何修改。
>
> 源代码编译完成后，会出现一个标题为 “[Extension Development Host]” 的新 VS Code 窗口，Mock Debug 扩展正以调试模式运行在其中。在这个窗口中打开你的 `mock test` 项目和 `readme.md` 文件，用 'F5' 启动一个调试会话，然后单步执行：

![调试扩展和服务器](images/debugger-extension/debug-mock-session.png)

> 由于你是以调试模式运行这个扩展的，现在可以在 `src/extension.ts` 中设置并命中断点。不过就像我上面提到的，扩展中执行的代码并没有什么有趣的东西。有趣的代码运行在调试适配器中，而它是一个单独的进程。

这里有点绕，因为同时存在**两层调试**：

```text
窗口 A（开发 Mock Debug 的窗口）
  └─ 按 F5（Extension 配置）→ 调试的是“扩展本身”
        ↓
窗口 B（扩展开发宿主，加载了 Mock Debug）
  └─ 按 F5（mock 配置）→ 用 Mock Debug 调试 readme.md
        ↓
     VS Code 启动调试适配器（mockDebug.js）——这是一个独立的进程，窗口 A 的调试器“看不到”它
```

所以在窗口 A 的 `mockDebug.ts` 中打断点不会生效，因为调试适配器不在扩展宿主进程中运行。下面就是解决这个问题的办法。

> 为了调试调试适配器本身，我们必须以调试模式运行它。最简单的方式是以_服务器模式_运行调试适配器，并配置 VS Code 连接到它。在你的 VS Code vscode-mock-debug 项目中，从下拉菜单中选择 **Server** 启动配置，然后按绿色的开始按钮。
>
> 由于我们已经有一个正在进行的扩展调试会话，VS Code 的调试器界面现在进入了_多会话_模式，这可以从调用堆栈视图中同时出现 **Extension** 和 **Server** 两个调试会话的名字看出来：

![同时调试扩展和服务器](images/debugger-extension/debugger-extension-server.png)

截图中，左侧调用堆栈（CALL STACK）中黄框标出了两个同时运行的调试会话：**Extension**（扩展）和 **Server**（调试适配器服务器）；底部调试控制台显示服务器正在 4711 端口等待调试协议的连接（`waiting for debug protocol on port 4711`），并已接受了一个客户端连接。

> 现在我们可以同时调试扩展和 DA 了。更快的方法是使用 **Extension + Server** 启动配置，它会自动启动这两个会话。
>
> [下文](#alternative-approach-to-develop-a-debugger-extension)还介绍了另一种更简单的同时调试扩展和 DA 的方法。
>
> 在 `src/mockDebug.ts` 文件中 `launchRequest(...)` 方法的开头设置一个断点。最后一步，在你的 mock test 启动配置中添加一个端口为 `4711` 的 `debugServer` 属性，配置 mock 调试器连接到 DA 服务器：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "mock",
      "request": "launch",
      "name": "mock test",
      "program": "${workspaceFolder}/readme.md",
      "stopOnEntry": true,
      "debugServer": 4711
    }
  ]
}
```

> 如果现在启动这个调试配置，VS Code 不会把 mock 调试适配器作为单独的进程启动，而是直接连接到已经在运行的服务器的本地端口 4711，你应该会命中 `launchRequest` 中的断点。
>
> 通过这样的设置，你现在可以很方便地编辑、编译和调试 Mock Debug 了。

整个设置的思路：

```text
平时：     按 F5 → VS Code 自己启动一个新的适配器进程（无法调试它）
服务器模式：先在窗口 A 中以调试模式启动适配器（Server 配置），让它监听 4711 端口
           → 窗口 B 中的配置加上 "debugServer": 4711
           → VS Code 不再启动新进程，而是连接到窗口 A 中那个正在被调试的适配器
           → 于是 mockDebug.ts 中的断点可以命中了
```

`debugServer` 这个属性只用于开发调试适配器，发布给用户的配置中不需要它。

> 但现在才是真正的工作开始的时候：你要把 `src/mockDebug.ts` 和 `src/mockRuntime.ts` 中调试适配器的模拟实现，替换成与“真正的”调试器或运行时通信的代码。这需要理解并实现调试适配器协议。更多细节可以在[这里](https://microsoft.github.io/debug-adapter-protocol/overview#How_it_works)找到。

---

<a id="anatomy-of-the-packagejson-of-a-debugger-extension"></a>
## 调试器扩展的 package.json 剖析（Anatomy of the package.json of a Debugger Extension）

> 除了提供一个特定于调试器的调试适配器实现之外，调试器扩展还需要一个 `package.json`，向各种与调试相关的贡献点做贡献。
>
> 我们来仔细看看 Mock Debug 的 `package.json`。
>
> 和每个 VS Code 扩展一样，`package.json` 声明了扩展的基本属性：**name**、**publisher** 和 **version**。使用 **categories** 字段，可以让扩展在 VS Code 扩展市场中更容易被找到。

```json
{
  "name": "mock-debug",
  "displayName": "Mock Debug",
  "version": "0.24.0",
  "publisher": "...",
  "description": "Starter extension for developing debug adapters for VS Code.",
  "author": {
    "name": "...",
    "email": "..."
  },
  "engines": {
    "vscode": "^1.17.0",
    "node": "^7.9.0"
  },
  "icon": "images/mock-debug-icon.png",
  "categories": ["Debuggers"],

  "contributes": {
    "breakpoints": [{ "language": "markdown" }],
    "debuggers": [
      {
        "type": "mock",
        "label": "Mock Debug",

        "program": "./out/mockDebug.js",
        "runtime": "node",

        "configurationAttributes": {
          "launch": {
            "required": ["program"],
            "properties": {
              "program": {
                "type": "string",
                "description": "Absolute path to a text file.",
                "default": "${workspaceFolder}/${command:AskForProgramName}"
              },
              "stopOnEntry": {
                "type": "boolean",
                "description": "Automatically stop after launch.",
                "default": true
              }
            }
          }
        },

        "initialConfigurations": [
          {
            "type": "mock",
            "request": "launch",
            "name": "Ask for file name",
            "program": "${workspaceFolder}/${command:AskForProgramName}",
            "stopOnEntry": true
          }
        ],

        "configurationSnippets": [
          {
            "label": "Mock Debug: Launch",
            "description": "A new configuration for launching a mock debug program",
            "body": {
              "type": "mock",
              "request": "launch",
              "name": "${2:Launch Program}",
              "program": "^\"\\${workspaceFolder}/${1:Program}\""
            }
          }
        ],

        "variables": {
          "AskForProgramName": "extension.mock-debug.getProgramName"
        }
      }
    ]
  },

  "activationEvents": ["onDebug", "onCommand:extension.mock-debug.getProgramName"]
}
```

先总览 `debuggers` 中的各个字段，下面再逐一讲解：

| 字段 | 作用 |
|---|---|
| `type` | 调试类型，用户在 `launch.json` 中用 `"type": "mock"` 引用它 |
| `label` | 在界面中显示的名称 |
| `program` | 调试适配器程序的路径（相对于扩展目录） |
| `runtime` | 运行调试适配器所需的运行时（`node` 或 `mono`） |
| `configurationAttributes` | `launch.json` 中可用属性的 JSON schema（用于校验和智能提示） |
| `initialConfigurations` | 创建默认 `launch.json` 时写入的初始配置 |
| `configurationSnippets` | 编辑 `launch.json` 时的代码片段 |
| `variables` | 把变量绑定到命令，用于 `${command:xxx}` |

> 现在看看 **contributes** 部分，其中包含了调试扩展特有的贡献。
>
> 首先，我们使用 **breakpoints** 贡献点列出启用设置断点功能的语言。没有它的话，就无法在 Markdown 文件中设置断点。

VS Code 默认不允许在任意文件中设置断点（不然在 `README.md` 里点一下行号也会出现红点，毫无意义）。只有声明过的语言，点击行号左侧才能设置断点。

> 接下来是 **debuggers** 部分。这里在调试**类型**（**type**）`mock` 下引入了一个调试器。用户可以在启动配置中引用这个类型。可选属性 **label** 可以在界面中显示时，给调试类型一个好看的名字。
>
> 由于调试扩展使用了一个调试适配器，所以用 **program** 属性给出它的代码的相对路径。为了让扩展自成一体，这个应用程序必须位于扩展文件夹之内。按照惯例，我们把这个应用程序放在一个名为 `out` 或 `bin` 的文件夹中，不过你也可以使用其他名称。
>
> 由于 VS Code 运行在不同的平台上，我们必须确保 DA 程序也支持不同的平台。为此，有以下几种选择：
>
> 1. 如果程序是以与平台无关的方式实现的，例如是一个运行在所有支持的平台上都可用的运行时之上的程序，你可以通过 **runtime** 属性指定这个运行时。目前，VS Code 支持 `node` 和 `mono` 运行时。我们上面的 Mock 调试适配器就使用了这种方式。
>
> 2. 如果你的 DA 实现在不同的平台上需要不同的可执行文件，可以像这样针对特定平台限定 **program** 属性：

```json
"debuggers": [{
    "type": "gdb",
    "windows": {
        "program": "./bin/gdbDebug.exe",
    },
    "osx": {
        "program": "./bin/gdbDebug.sh",
    },
    "linux": {
        "program": "./bin/gdbDebug.sh",
    }
}]
```

> 3. 也可以把两种方式结合起来。下面的例子来自 Mono DA，它是用一个 mono 应用程序实现的，在 macOS 和 Linux 上需要运行时，但在 Windows 上不需要：

```json
"debuggers": [{
    "type": "mono",
    "program": "./bin/monoDebug.exe",
    "osx": {
        "runtime": "mono"
    },
    "linux": {
        "runtime": "mono"
    }
}]
```

（Mono 是 .NET 的跨平台实现。Windows 自带 .NET，可以直接运行 `.exe`；macOS 和 Linux 上则需要通过 `mono` 运行时来运行。）

> **configurationAttributes** 声明了这个调试器可用的 `launch.json` 属性的 schema。这个 schema 用于校验 `launch.json`，并在编辑启动配置时提供智能提示和悬停帮助。

`configurationAttributes` 下的 `launch` 对应 `launch.json` 中的 `"request": "launch"`（启动一个新程序来调试）。调试器如果还支持 `"request": "attach"`（附加到一个已经在运行的程序上调试），还可以再定义一个 `attach` 的 schema。

> **initialConfigurations** 定义了这个调试器的默认 `launch.json` 的初始内容。当项目没有 `launch.json`，而用户启动了一个调试会话，或者选择了运行和调试视图中的**创建 launch.json 文件**链接时，就会用到这些信息。这时，VS Code 会让用户选择一个调试环境，然后创建对应的 `launch.json`：

![选择调试器的快速选择列表](images/debugger-extension/debug-init-config.png)

> 除了在 `package.json` 中静态地定义 `launch.json` 的初始内容，还可以通过实现一个 `DebugConfigurationProvider` 动态地计算初始配置（详见下面[使用 DebugConfigurationProvider](#using-a-debugconfigurationprovider) 一节）。
>
> **configurationSnippets** 定义了启动配置的代码片段，在编辑 `launch.json` 时会出现在智能提示中。按照惯例，代码片段的 `label` 属性要以调试环境的名称作为前缀，这样在一大堆代码片段建议中显示时，可以清楚地识别出它来。

`body` 中的 `${1:Program}`、`${2:Launch Program}` 是代码片段的“占位符”：插入片段后，光标会依次停在 1、2 号占位符上，等待用户输入。`"^\"\\${workspaceFolder}/${1:Program}\""` 这种奇怪的写法，是为了让插入后的文本中保留字面上的 `${workspaceFolder}`（而不被当作占位符），代码片段的语法见 [代码片段指南](../language-extensions/snippet-guide.md)。

> **variables** 贡献把“变量”绑定到“命令”上。这些变量可以在启动配置中通过 **\${command:xyz}** 语法使用，启动调试会话时，变量会被替换成绑定的命令返回的值。
>
> 命令的实现位于扩展中，它可以是一个没有界面的简单表达式，也可以是基于扩展 API 中可用的界面功能的复杂功能。Mock Debug 把变量 `AskForProgramName` 绑定到命令 `extension.mock-debug.getProgramName` 上。这个命令在 `src/extension.ts` 中的[实现](https://github.com/microsoft/vscode-mock-debug/blob/606454ff3bd669867a38d9b2dc7b348d324a3f6b/src/extension.ts#L21-L26)，使用 `showInputBox` 让用户输入一个程序名：

```ts
vscode.commands.registerCommand('extension.mock-debug.getProgramName', config => {
  return vscode.window.showInputBox({
    placeHolder: 'Please enter the name of a markdown file in the workspace folder',
    value: 'readme.md'
  });
});
```

> 现在，这个变量就可以在启动配置的任何字符串类型的值中，以 **\${command:AskForProgramName}** 的形式使用了。

整个过程：

```text
launch.json："program": "${workspaceFolder}/${command:AskForProgramName}"
        ↓ 用户按 F5
VS Code 发现 ${command:AskForProgramName}
        ↓ 查 variables：AskForProgramName → extension.mock-debug.getProgramName
执行命令 → 弹出输入框 → 用户输入 readme.md → 命令返回 "readme.md"
        ↓
最终配置："program": "C:/mock test/readme.md"
```

`${workspaceFolder}` 是 VS Code 内置的变量（当前工作区文件夹的路径）。`${command:...}` 则让扩展可以提供自定义的变量。也可以直接写 `${command:extension.mock-debug.getProgramName}`，`variables` 只是给它起了一个更短、更好记的别名。

另外注意 `activationEvents` 中的 `onCommand:extension.mock-debug.getProgramName`：它让这个命令在扩展尚未激活时也能被调用。1.74 及以上版本中，`contributes.commands` 中声明的命令会自动生成这类激活事件，但这个命令只供变量替换使用，没有在 `commands` 中声明（不需要出现在命令面板中），所以仍要显式写出。

---

<a id="using-a-debugconfigurationprovider"></a>
## 使用 DebugConfigurationProvider（Using a DebugConfigurationProvider）

> 如果 `package.json` 中调试贡献的静态特性不能满足需要，可以使用 `DebugConfigurationProvider` 动态地控制调试扩展的以下方面：
>
> - 可以动态生成新创建的 launch.json 的初始调试配置，例如基于工作区中可用的上下文信息。
> - 一个启动配置在用来启动新的调试会话之前，可以先被_解析_（或修改）。这样就可以根据工作区中可用的信息填入默认值。有两个 _resolve_ 方法：`resolveDebugConfiguration` 在启动配置中的变量被替换之前调用，`resolveDebugConfigurationWithSubstitutedVariables` 在所有变量都被替换之后调用。如果校验逻辑会向调试配置中插入额外的变量，就必须使用前者。如果校验逻辑需要访问所有调试配置属性的最终值，就必须使用后者。

`DebugConfigurationProvider` 的三个方法（以 `@types/vscode` 1.140 为准）：

| 方法 | 何时调用 | 用途 |
|---|---|---|
| `provideDebugConfigurations(folder)` | 创建 `launch.json` 时 | 动态生成初始配置（代替 `initialConfigurations`） |
| `resolveDebugConfiguration(folder, config)` | 启动调试前，**变量替换之前** | 补全默认值；可以插入 `${...}` 变量，之后会被替换 |
| `resolveDebugConfigurationWithSubstitutedVariables(folder, config)` | 启动调试前，**变量替换之后** | 检查最终的值，比如判断 `program` 指向的文件是否存在 |

两个 resolve 方法的顺序：

```text
launch.json 中的配置
   ↓ resolveDebugConfiguration（此时 program 还是 "${workspaceFolder}/app.js"）
   ↓ 替换变量
   ↓ resolveDebugConfigurationWithSubstitutedVariables（此时 program 是 "C:/proj/app.js"）
   ↓
交给调试适配器
```

两个方法都可以返回修改后的配置；返回 `undefined` 表示取消这次调试；返回 `null` 表示取消并打开 `launch.json` 让用户修改。

> `src/extension.ts` 中的 `MockConfigurationProvider` 实现了 `resolveDebugConfiguration`，用来检测这种情况：在没有 launch.json 的情况下启动了调试会话，但活动的编辑器中打开着一个 Markdown 文件。这是一个典型的场景：用户在编辑器中打开了一个文件，只想直接调试它，而不想创建 launch.json。

参考写法（简化自 Mock Debug 示例）：

```ts
class MockConfigurationProvider implements vscode.DebugConfigurationProvider {
  resolveDebugConfiguration(
    folder: vscode.WorkspaceFolder | undefined,
    config: vscode.DebugConfiguration
  ): vscode.ProviderResult<vscode.DebugConfiguration> {
    // 没有 launch.json 时，config 是一个空对象
    if (!config.type && !config.request && !config.name) {
      const editor = vscode.window.activeTextEditor;
      if (editor && editor.document.languageId === 'markdown') {
        // 用当前打开的文件，现场生成一个配置
        config.type = 'mock';
        config.name = 'Launch';
        config.request = 'launch';
        config.program = '${file}';     // 插入了变量，所以要在 resolveDebugConfiguration 中做
        config.stopOnEntry = true;
      }
    }
    return config;
  }
}

// 注册
context.subscriptions.push(
  vscode.debug.registerDebugConfigurationProvider('mock', new MockConfigurationProvider())
);
```

> 调试配置提供者通过 `vscode.debug.registerDebugConfigurationProvider` 为特定的调试类型注册，通常在扩展的 `activate` 函数中注册。为了确保 `DebugConfigurationProvider` 注册得足够早，扩展必须在一开始使用调试功能时就被激活。在 `package.json` 中为 `onDebug` 事件配置扩展激活，就可以轻松做到这一点：

```json
"activationEvents": [
    "onDebug",
    // ...
],
```

> 这个“一网打尽”的 `onDebug` 会在任何调试功能被使用时立即触发。只要扩展的启动开销很小（即不会在启动过程中花费大量时间），这样做就没有问题。如果一个调试扩展的启动开销很大（例如因为要启动一个语言服务器），`onDebug` 激活事件就可能对其他调试扩展产生负面影响，因为它触发得相当早，并且不考虑具体的调试类型。
>
> 对于启动开销大的调试扩展，更好的方式是使用更细粒度的激活事件：
>
> - `onDebugInitialConfigurations` 在 `DebugConfigurationProvider` 的 `provideDebugConfigurations` 方法被调用之前触发。
> - `onDebugResolve:type` 在指定类型的 `DebugConfigurationProvider` 的 `resolveDebugConfiguration` 或 `resolveDebugConfigurationWithSubstitutedVariables` 方法被调用之前触发。
>
> **经验法则：** 如果调试扩展的激活开销很小，就使用 `onDebug`。如果开销很大，就根据 `DebugConfigurationProvider` 是否实现了对应的方法 `provideDebugConfigurations` 和 / 或 `resolveDebugConfiguration`，使用 `onDebugInitialConfigurations` 和 / 或 `onDebugResolve`。

| 激活事件 | 触发时机 | 适合 |
|---|---|---|
| `onDebug` | 使用任何调试功能时 | 激活很快的扩展 |
| `onDebugInitialConfigurations` | 要调用 `provideDebugConfigurations` 之前 | 激活较慢、且实现了这个方法的扩展 |
| `onDebugResolve:mock` | 要为 `mock` 类型调用 resolve 方法之前 | 激活较慢、且实现了 resolve 方法的扩展 |

为什么 `onDebug` 会“影响其他调试扩展”：用户调试 Python 程序时，`onDebug` 也会触发，于是你的 mock 扩展也被激活了。如果你的扩展激活要花好几秒，就会拖慢用户调试 Python。而 `onDebugResolve:mock` 只在调试 `mock` 类型时才触发。

---

<a id="publishing-your-debugger-extension"></a>
## 发布你的调试器扩展（Publishing your debugger extension）

> 创建好调试器扩展后，就可以把它发布到扩展市场：
>
> - 更新 `package.json` 中的属性，反映你的调试器扩展的名称和用途。
> - 按照[发布扩展](../working-with-extensions/publishing-extension.md)中的说明上传到扩展市场。

---

<a id="alternative-approach-to-develop-a-debugger-extension"></a>
## 开发调试器扩展的另一种方法（Alternative approach to develop a debugger extension）

> 我们已经看到，开发调试器扩展通常需要在两个并行的会话中，分别调试扩展和调试适配器。正如上面所解释的，VS Code 很好地支持了这一点，但如果扩展和调试适配器是同一个程序、可以在一个调试会话中调试，开发会更容易。
>
> 只要你的调试适配器是用 TypeScript/JavaScript 实现的，这种方法其实很容易做到。基本思路是：直接在扩展内部运行调试适配器，让 VS Code 连接到它，而不是为每个会话启动一个新的外部调试适配器。
>
> 为此，VS Code 提供了扩展 API 来控制调试适配器如何被创建和运行。`DebugAdapterDescriptorFactory` 有一个方法 `createDebugAdapterDescriptor`，当调试会话启动、需要一个调试适配器时，VS Code 会调用它。这个方法必须返回一个描述符对象（`DebugAdapterDescriptor`），描述调试适配器如何运行。
>
> 目前，VS Code 支持三种不同的调试适配器运行方式，因此也提供了三种不同的描述符类型：

| 描述符 | 调试适配器如何运行 | 说明 |
|---|---|---|
| `DebugAdapterExecutable` | 作为外部可执行程序 | 描述一个外部可执行程序，包括路径、可选的参数和运行时。可执行程序必须实现调试适配器协议，并通过 stdin/stdout 通信。这是 VS Code 的默认工作方式：如果没有显式注册 `DebugAdapterDescriptorFactory`，VS Code 会根据 package.json 中对应的值自动使用这个描述符 |
| `DebugAdapterServer` | 作为服务器 | 描述一个以服务器方式运行、通过特定的本地或远程端口通信的调试适配器。基于 [`vscode-debugadapter`](https://www.npmjs.com/package/vscode-debugadapter) npm 模块的调试适配器实现，会自动支持这种服务器模式 |
| `DebugAdapterInlineImplementation` | 在扩展内部运行 | 描述一个实现了 `vscode.DebugAdapter` 接口的 JavaScript 或 TypeScript 对象。基于 1.38-pre.4 或更高版本的 [`vscode-debugadapter`](https://www.npmjs.com/package/vscode-debugadapter) npm 模块的调试适配器实现，会自动实现这个接口 |

（当前的类型定义中还有第四种描述符 `DebugAdapterNamedPipeServer`，通过命名管道（Windows）或 Unix 域套接字与调试适配器通信，用法与 `DebugAdapterServer` 类似。）

**stdin/stdout** 是程序的标准输入和标准输出。默认模式下，VS Code 启动调试适配器进程，通过向它的标准输入写 DAP 消息、从它的标准输出读 DAP 消息来通信。

> Mock Debug 展示了[三种 DebugAdapterDescriptorFactory](https://github.com/microsoft/vscode-mock-debug/blob/668fa6f5db95dbb76825d4eb670ab0d305050c3b/src/extension.ts#L91-L150) 的示例，以及它们是如何[为 'mock' 调试类型注册的](https://github.com/microsoft/vscode-mock-debug/blob/668fa6f5db95dbb76825d4eb670ab0d305050c3b/src/extension.ts#L50)。可以通过[设置全局变量 `runMode`](https://github.com/microsoft/vscode-mock-debug/blob/668fa6f5db95dbb76825d4eb670ab0d305050c3b/src/extension.ts#L16) 为 `external`、`server` 或 `inline` 中的某个值，来选择要使用的运行模式。
>
> 在开发时，`inline` 和 `server` 模式特别有用，因为它们让你可以在单个进程中调试扩展和调试适配器。

`inline` 模式的写法（简化自 Mock Debug 示例）：

```ts
class InlineDebugAdapterFactory implements vscode.DebugAdapterDescriptorFactory {
  createDebugAdapterDescriptor(_session: vscode.DebugSession): vscode.ProviderResult<vscode.DebugAdapterDescriptor> {
    // 直接在扩展宿主中创建调试适配器对象
    return new vscode.DebugAdapterInlineImplementation(new MockDebugSession());
  }
}

context.subscriptions.push(
  vscode.debug.registerDebugAdapterDescriptorFactory('mock', new InlineDebugAdapterFactory())
);
```

这样，调试适配器就和扩展代码运行在同一个进程（扩展宿主）中，在窗口 A 中按 F5 调试扩展时，`mockDebug.ts` 中的断点也能直接命中，不需要再单独启动 Server 配置。

三种模式的比较：

| 模式 | 调试适配器在哪里运行 | 调试是否方便 | 适合 |
|---|---|---|---|
| `external`（`DebugAdapterExecutable`） | 独立进程（每个会话一个） | 不方便，要借助服务器模式 | 发布给用户（默认方式，隔离性好） |
| `server`（`DebugAdapterServer`） | 一个长期运行的服务器进程 | 方便 | 开发阶段 |
| `inline`（`DebugAdapterInlineImplementation`） | 扩展宿主进程内 | 最方便 | 开发阶段；也可以用于发布（适配器用 JS/TS 写时） |

---

## 本篇小结

```text
架构：VS Code 通用调试界面 ⇄ DAP ⇄ 调试适配器（DA） ⇄ 真正的调试器
      调试器扩展 = 调试适配器的“包装盒”（+ 可选的扩展代码）

package.json
  breakpoints：哪些语言可以设置断点
  debuggers：type、label、program + runtime（或按平台区分 windows/osx/linux）、
             configurationAttributes（launch.json 的 schema）、initialConfigurations、
             configurationSnippets、variables（${command:xxx} → 命令）

扩展代码（可选）
  DebugConfigurationProvider：provideDebugConfigurations（动态初始配置）
                              resolveDebugConfiguration（变量替换前）
                              resolveDebugConfigurationWithSubstitutedVariables（变量替换后）
  激活事件：开销小用 onDebug；开销大用 onDebugInitialConfigurations / onDebugResolve:type

DebugAdapterDescriptorFactory：决定适配器如何运行
  Executable（默认，独立进程）/ Server（端口）/ NamedPipeServer / InlineImplementation（扩展内）

开发调试适配器：server 模式 + launch.json 中的 "debugServer": 4711，或直接用 inline 模式
```
