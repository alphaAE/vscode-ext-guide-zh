# MCP 开发者指南（MCP developer guide）

> 原文：[MCP developer guide](https://code.visualstudio.com/api/extension-guides/ai/mcp)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/ai/mcp.md`（DateApproved: 10/7/2026）

> 模型上下文协议（Model Context Protocol，MCP）是一个开放标准，让 AI 模型可以通过统一的接口与外部工具和服务交互。VS Code 实现了完整的 MCP 规范，让你可以创建 MCP 服务器，提供工具、提示词和资源，扩展 VS Code 中 AI 智能体的能力。
>
> MCP 服务器提供的是 VS Code 中三种可用工具类型中的一种，另外两种是内置工具和扩展贡献的工具。了解更多关于[工具类型](https://code.visualstudio.com/docs/agents/concepts/tools#types-of-tools)的信息。
>
> 本指南涵盖了构建能与 VS Code 及其他 MCP 客户端无缝协作的 MCP 服务器所需了解的一切。

> **提示**
>
> 关于作为最终用户如何使用 MCP 服务器，请参阅[在 VS Code 中使用 MCP 服务器](https://code.visualstudio.com/docs/agent-customization/mcp-servers)。

**本篇的内容分两大块：**

| 部分 | 内容 | 与扩展开发的关系 |
|---|---|---|
| 前半部分（MCP 功能、添加和管理服务器、调试） | **MCP 服务器**本身如何开发，VS Code 支持 MCP 的哪些功能 | MCP 服务器是一个独立的程序，不是 VS Code 扩展 |
| [在扩展中注册 MCP 服务器](#register-an-mcp-server-in-your-extension) | VS Code **扩展**如何把一个 MCP 服务器提供给用户 | 这部分才是扩展 API |

**角色关系：**

```text
MCP 客户端（VS Code、Claude Desktop 等 AI 应用）
        │  MCP 协议（stdio 或 HTTP）
        ▼
MCP 服务器（你写的独立程序，可以用任何语言）
        │
        ▼
外部服务（数据库、Jira、GitHub、内部系统……）
```

---

<a id="why-use-mcp-servers"></a>
## 为什么要使用 MCP 服务器？（Why use MCP servers?）

> 实现一个 MCP 服务器，用语言模型工具扩展 VS Code 中的聊天，有以下好处：
>
> - **扩展智能体模式**：提供专门的、特定于领域的工具，在回应用户提示词的过程中被自动调用。例如，启用数据库的脚手架生成和查询功能，动态地为 LLM 提供相关的上下文。
> - **灵活的部署选项**：适用于本地和远程场景。
> - **复用**：在不同的工具和平台之间复用你的 MCP 服务器。
>
> 在以下场景中，你可以考虑用[语言模型 API](./tools.md) 实现语言模型工具：
>
> - 你想使用扩展 API，与 VS Code 深度集成。
> - 你想通过 Visual Studio 扩展市场分发你的工具和更新。

两者的选择见 [AI 扩展性概览](./ai-extensibility-overview.md)。

---

<a id="mcp-features-supported-by-vs-code"></a>
## VS Code 支持的 MCP 功能（MCP features supported by VS Code）

> VS Code 支持以下 MCP 能力：
>
> - [传输方式（Transports）](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)：
>     - 本地标准输入 / 输出（`stdio`）
>     - 可流式传输的 HTTP（Streamable HTTP，`http`）
>     - 服务器发送事件（Server-sent events，`sse`）：旧版支持。
> - [功能（Features）](https://modelcontextprotocol.io/specification/2025-06-18#features)：
>     - 工具（Tools）：为[智能体模式](https://code.visualstudio.com/docs/chat/chat-overview)扩展额外的工具
>     - 提示词（Prompts）：在聊天中以斜杠命令的形式添加可复用的提示词
>     - 资源（Resources）：提供数据和内容，用户可以把它们添加为聊天上下文，或者直接在 VS Code 中与之交互
>     - 征询（Elicitation）：向用户请求输入
>     - 采样（Sampling）：使用用户配置的模型和订阅发出语言模型请求
>     - 身份验证（Authentication）：使用 OAuth 授权访问 MCP 服务器
>     - 服务器指令（Server instructions）
>     - 根目录（Roots）：提供关于用户工作区根文件夹的信息
>     - [MCP Apps](https://modelcontextprotocol.github.io/ext-apps/api/)：从工具返回可交互的界面组件

**传输方式**是指 VS Code 和 MCP 服务器之间怎么传消息：

| 传输方式 | 服务器在哪里 | 怎么通信 |
|---|---|---|
| `stdio` | 本地：VS Code 启动一个子进程 | 通过子进程的标准输入 / 输出（和 [调试适配器](../debugger-extension.md) 的默认方式一样） |
| `http`（Streamable HTTP） | 本地或远程的 Web 服务 | HTTP 请求 |
| `sse` | 同上 | 旧的方式，新服务器建议用 `http` |

**各项功能一览：**

| 功能 | 方向 | 一句话说明 |
|---|---|---|
| 工具 | 模型 → 服务器 | AI 可以调用的函数（最常用） |
| 提示词 | 用户 → 服务器 | 预先写好的提示词模板，用户通过 `/` 命令使用 |
| 资源 | 用户 / 模型 ← 服务器 | 服务器提供的数据（文件、日志、截图……），可以作为聊天的上下文 |
| 征询 | 服务器 → 用户 | 服务器在执行过程中向用户提问 |
| 采样 | 服务器 → 模型 | 服务器借用用户的模型来调用 AI |
| 身份验证 | | 服务器需要用户登录某个账号 |
| 根目录 | VS Code → 服务器 | 告诉服务器用户的工作区在哪里 |
| MCP Apps | 服务器 → 聊天界面 | 工具返回可交互的界面，而不只是文字 |

<a id="tools"></a>
### 工具（Tools）

<a id="tool-definition"></a>
#### 工具定义（Tool definition）

> VS Code 在智能体模式中支持 MCP 工具，它们会根据任务的需要被调用。用户可以通过工具选择器启用和配置它们。工具的描述会显示在工具选择器中工具名称的旁边，也会显示在运行工具前请求确认的对话框中。

![智能体模式中的工具选择器，高亮显示了来自某个 MCP 服务器的工具](../images/ai/mcp/mcp-tools-picker.png)

截图中，聊天视图的工具选择器里按来源分组列出了可用的工具，来自 MCP 服务器的工具被高亮显示，每个工具旁边是它的描述，用户可以勾选启用或禁用。

> 用户可以在工具确认对话框中编辑模型生成的输入参数。所有没有标记 `readOnlyHint` 注解的工具，都会显示确认对话框。

![MCP 工具的确认对话框，其中包含输入参数](../images/ai/mcp/mcp-tool-input-parameters.png)

截图中，运行工具前弹出的确认对话框里显示了模型生成的输入参数，用户可以在执行前修改它们。

这和 [语言模型工具](./tools.md) 中的确认对话框是同一个机制。

<a id="dynamic-tool-discovery"></a>
#### 动态工具发现（Dynamic tool discovery）

> VS Code 还支持[动态工具发现](https://modelcontextprotocol.io/docs/concepts/tools#tool-discovery-and-updates)，允许服务器在运行时注册工具。例如，服务器可以根据在工作区中检测到的框架或语言提供不同的工具，或者根据用户的聊天提示词提供不同的工具。

<a id="tool-annotations"></a>
#### 工具注解（Tool annotations）

> 要提供关于工具行为的额外元数据，可以使用[工具注解](https://modelcontextprotocol.io/docs/concepts/tools#tool-annotations)：
>
> - `title`：工具的人类可读标题，在聊天视图中调用工具时显示
> - `readOnlyHint`：可选的提示，表示这个工具是只读的。VS Code 运行只读工具时不会请求确认。

只读的工具（比如“查询天气”“读取日志”）不会修改任何东西，没必要每次都让用户确认。给这类工具加上 `readOnlyHint: true`，能减少打扰。但不要给有副作用的工具（写文件、发消息、删数据）加这个注解。

<a id="resources"></a>
### 资源（Resources）

> 资源让你可以以结构化的方式向用户提供数据和内容。用户可以在 VS Code 中直接访问资源，或者在聊天提示词中把它们用作上下文。例如，一个 MCP 服务器可以生成截图并把它们作为资源提供，或者提供对日志文件的访问，这些日志文件会被实时更新。
>
> 定义一个 MCP 资源时，资源的名称会显示在 MCP 资源快速选择列表中。资源可以通过 **MCP: Browse Resources** 命令打开，也可以通过 **Add Context**（添加上下文），然后选择 **MCP Resource**（MCP 资源），附加到聊天请求中。资源可以包含文本或二进制内容。

![MCP 资源的快速选择列表](../images/ai/mcp/mcp-resources-picker.png)

> VS Code 支持资源更新，让用户可以在编辑器中实时看到资源内容的变化。

**工具和资源的区别：** 工具是“AI 主动去调用、执行一个操作”；资源是“一份数据，用户（或 AI）可以拿来作为参考”。比如数据库：“执行查询”是工具，“某张表的结构”可以是资源。

<a id="resource-templates"></a>
#### 资源模板（Resource templates）

> VS Code 还支持[资源模板](https://modelcontextprotocol.io/docs/concepts/resources#resource-templates)，让用户在引用资源时可以提供输入参数。例如，一个数据库查询工具可以要求输入数据库表名。
>
> 访问带有模板的资源时，会在一个快速选择框中提示用户输入所需的参数。你可以提供补全，为参数建议可选的值。

<a id="prompts"></a>
### 提示词（Prompts）

> 提示词是可复用的聊天提示词模板，用户可以在聊天中通过斜杠命令（`mcp.servername.promptname`）调用它们。提示词可以用来引导用户上手使用你的服务器，比如突出介绍各种工具，或者提供内置的复杂工作流，这些工作流可以适应用户的本地上下文和服务。
>
> 如果你定义了[补全](https://modelcontextprotocol.io/specification/2025-06-18/server/utilities/completion)，为提示词的输入参数建议可选值，VS Code 就会显示一个对话框，收集用户的输入。

```typescript
server.prompt(
    "teamGreeting", "Generate a greeting for team members",
    {
        name: completable(z.string(), (value) => {
            return ["Alice", "Bob", "Charlie"].filter(n => n.startsWith(value));
        })
    },
    async ({ name }) => ({
        messages: [{
            role: "assistant",
            content: { type: "text", text: `Hello ${name}, welcome to the team!` }
        }]
    })
);
```

这段代码是用 MCP 的 **TypeScript SDK** 写的 MCP 服务器代码（不是 VS Code 扩展代码）：

| 部分 | 含义 |
|---|---|
| `server.prompt(名称, 描述, 参数定义, 处理函数)` | 定义一个提示词 |
| `"teamGreeting"` | 提示词的名称，用户在聊天中输入 `/mcp.服务器名.teamGreeting` 使用 |
| `z.string()` | `zod` 库的写法，表示参数是字符串 |
| `completable(..., value => [...])` | 为参数提供补全：用户输入时，根据已输入的内容返回候选值 |
| 处理函数返回的 `messages` | 生成的提示词内容，会被放进聊天中 |

![带有输入参数的 MCP 提示词对话框](../images/ai/mcp/mcp-prompt-argument.png)

> **注意**
>
> 用户可以在提示词对话框中输入一条终端命令，并把命令的输出作为提示词的输入。

> 当你在提示词的响应中包含一个资源类型时，VS Code 会把这个资源作为上下文附加到聊天提示词中。

<a id="authorization"></a>
### 授权（Authorization）

> VS Code 支持需要身份验证的 MCP 服务器，让用户可以与一个代表他们在该服务中的用户账号进行操作的 MCP 服务器交互。
>
> [授权规范](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)把作为资源服务器（Resource Server）的 MCP 服务器与授权服务器（Authorization Server）清晰地分离开来，让开发者可以把身份验证委托给现有的身份提供者（IdP），而不必从零开始构建自己的 OAuth 实现。

**OAuth 的基本概念：**

| 角色 | 说明 | 例子 |
|---|---|---|
| 资源服务器 | 存放用户数据、提供服务的一方 | 你的 MCP 服务器 |
| 授权服务器 / 身份提供者（IdP） | 负责验证用户身份、发放访问令牌的一方 | GitHub、Microsoft Entra（原 Azure AD） |
| 客户端 | 代表用户访问资源的应用 | VS Code |

流程是：用户在 IdP 的页面上登录并同意授权 → IdP 给 VS Code 一个令牌 → VS Code 带着令牌访问 MCP 服务器。MCP 服务器自己不处理用户名和密码。

> VS Code 内置了对 GitHub 和 Microsoft Entra 的身份验证支持。如果你的 MCP 服务器实现了最新的规范，并使用 GitHub 或 Microsoft Entra 作为授权服务器，用户就可以通过对应账号的**账户菜单** > **Manage Trusted MCP Servers**（管理受信任的 MCP 服务器）操作，管理哪些 MCP 服务器可以访问他们的账号。

![账户菜单中的 Manage Trusted MCP Servers 操作](../images/ai/mcp/manage-trusted-mcp.png)

> 对于 GitHub 和 Microsoft Entra 以外的其他 IdP，VS Code 支持使用 OAuth 2.1 和 2.0 标准进行授权。VS Code 首先进行[动态客户端注册（Dynamic Client Registration，DCR）](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization#dynamic-client-registration)握手；如果 IdP 不支持 DCR，就退而使用客户端凭据（client-credentials）工作流。这为各种 IdP 提供了更大的灵活性，可以为每个 MCP 服务器相应地创建静态的客户端 ID，或者特定的客户端 ID 和密钥对。
>
> 之后，用户也可以通过**账户菜单**查看他们的身份验证状态。要删除动态客户端注册，用户可以在命令面板中使用 **Authentication: Remove Dynamic Authentication Providers** 命令。

**DCR（动态客户端注册）**：通常一个应用要接入 OAuth，需要先到 IdP 的后台手动注册，拿到一个“客户端 ID”。DCR 让客户端可以自动完成注册，用户不需要做任何配置。IdP 不支持 DCR 时，VS Code 会让用户手动输入客户端 ID 和密钥（见下面的截图）。

> 下面是一份检查清单，确保你的 MCP 服务器能与 VS Code 的 OAuth 工作流配合：
>
> 1. MCP 服务器实现了 [MCP 授权规范](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)。
> 2. IdP 必须支持 DCR 或客户端凭据。
> 3. 重定向 URL 列表必须包含这些 URL：`http://127.0.0.1:33418` 和 `https://vscode.dev/redirect`
>
> 当 MCP 服务器不支持 DCR 时，用户会走退而求其次的客户端凭据流程：

![MCP 服务器不支持 DCR 时的授权提示](../images/ai/mcp/mcp-auth-dynamic-client-required.png)

![请求输入 MCP 服务器的客户端 ID](../images/ai/mcp/mcp-auth-client-id.png)

![请求输入 MCP 服务器的客户端密钥](../images/ai/mcp/mcp-auth-client-secret.png)

这三张截图依次是：提示服务器不支持动态客户端注册、需要手动提供客户端信息；输入客户端 ID 的输入框；输入客户端密钥的输入框。

> **注意**
>
> VS Code 仍然支持自身充当授权服务器的 MCP 服务器，但对于新的服务器，建议使用最新的规范。

<a id="sampling"></a>
### 采样（Sampling）

> VS Code 为 MCP 服务器提供了[采样](https://modelcontextprotocol.io/docs/concepts/sampling)功能。这让你的 MCP 服务器可以使用用户配置的模型和订阅发出语言模型请求。例如，可以用采样来总结大型数据集、在把信息发给客户端之前提取信息，或者在工具中实现智能体式的决策逻辑。
>
> MCP 服务器第一次发出采样请求时，会提示用户授权这个服务器访问他们的模型。

![提示用户授权某个 MCP 服务器访问模型](../images/ai/mcp/mcp-allow-sampling.png)

**采样解决什么问题？** MCP 服务器自己可能也需要 AI 的能力（比如把一份很长的日志先总结一下再返回）。如果让服务器自己去调用 AI 服务，就需要服务器作者提供 API 密钥、承担费用。采样让服务器可以“借用”用户在 VS Code 中已有的模型，费用和配额由用户的订阅承担，所以需要用户授权。

这和扩展中使用 [语言模型 API](./language-model.md) 是同一个思路。

> 当使用特定模型发出采样请求时，请注意，用户可以在命令面板中通过 **MCP: List Servers** > **Configure Model Access**（配置模型访问权限）命令，限制 MCP 服务器可以使用哪些模型。当你在 MCP 服务器中指定 `modelPreferences`，提示采样时希望使用哪些模型时，VS Code 会从允许的模型中进行选择。

![某个 MCP 服务器的“配置模型访问权限”对话框](../images/ai/mcp/mcp-configure-model-access.png)

> 用户可以在命令面板中通过 **MCP: List Servers** > **Show Sampling Requests**（显示采样请求）命令，查看某个 MCP 服务器发出的采样请求。

<a id="workspace-roots"></a>
### 工作区根目录（Workspace roots）

> VS Code 会向 MCP 服务器提供用户工作区根文件夹的信息。

这样服务器就知道用户正在处理哪个项目，可以据此读取项目文件、提供与项目相关的工具。

<a id="mcp-apps"></a>
### MCP Apps

> MCP Apps 让工具可以返回可交互的界面组件，以内联的方式在聊天中渲染，而不只是纯文本输出。这在拖放列表重排、可视化、表单和多步骤工作流等场景中很有用。

<a id="architecture"></a>
#### 架构（Architecture）

> MCP Apps 使用“工具 + 界面资源”的模式：
>
> 1. 定义一个工具，返回一个指向界面资源的 `_meta.ui.resourceUri`
> 2. 创建一个界面资源，使用 `ui://` URI 协议和 MIME 类型 `text/html;profile=mcp-app`
> 3. 这个 HTML 资源运行在一个沙箱化的 iframe 中，并使用 MCP Apps SDK 与 VS Code 通信

```text
AI 调用工具 → 工具结果中带有 _meta.ui.resourceUri: "ui://my-app/view"
           → VS Code 读取这个资源（一段 HTML）
           → 在聊天中用沙箱 iframe 渲染它
           → iframe 中的页面通过 MCP Apps SDK 与 VS Code 通信
```

和 [Webview](../webview.md) 的思路很像：一个隔离的网页，通过消息与宿主通信。

<a id="SDK"></a>
#### SDK

> 使用 [`@modelcontextprotocol/ext-apps`](https://github.com/modelcontextprotocol/ext-apps) 包构建 MCP Apps。这个 SDK 提供了：

**`App` 类**：与宿主通信的主要接口

| 方法 | 作用 |
|---|---|
| `connect()` | 与 VS Code 建立连接 |
| `callServerTool(name, args)` | 调用来源 MCP 服务器上的工具 |
| `sendMessage(content)` | 向聊天输入框发送一条消息 |
| `updateModelContext(context)` | 为之后的对话轮次提供上下文 |
| `openLink(url)` | 请求在浏览器中打开一个 URL |
| `sendLog(level, message)` | 发送调试日志（不会加入对话） |

**通知处理函数**：设置它们来接收来自 VS Code 的事件

| 处理函数 | 何时触发 |
|---|---|
| `ontoolinput` | 收到完整的工具参数 |
| `ontoolinputpartial` | 收到流式传来的部分参数 |
| `ontoolresult` | 收到工具的执行结果 |
| `ontoolcancelled` | 工具被取消 |
| `onhostcontextchanged` | 主题或语言区域发生变化 |
| `onteardown` | 卸载之前，用于清理 |

<a id="vs-code-behavior-and-limitations"></a>
#### VS Code 中的行为与限制（VS Code behavior and limitations）

| 功能 | VS Code 中的支持情况 |
| ------- | --------------- |
| 显示模式 | 只支持 `inline`（内联），不支持 `fullscreen`（全屏）或 `pip`（画中画） |
| 发送消息 | 填入聊天输入框，不会自动发送 |
| 上下文更新 | 显示为附件 |
| 写入剪贴板 | 支持 |
| 摄像头、麦克风、地理位置 | 不支持 |

“发送消息只填入输入框、不自动发送”是一种安全设计：界面组件不能替用户发出请求，用户要自己确认后按回车。

<a id="security"></a>
#### 安全（Security）

> MCP Apps 运行在沙箱化的 iframe 中，并强制执行内容安全策略（CSP）。定义界面资源时，要声明你的应用需要访问的域名：
>
> - `connectDomains`：用于 fetch/XHR 请求的域名
> - `resourceDomains`：用于图片、字体和其他资源的域名
> - `frameDomains`：可以嵌入到 iframe 中的域名

内容安全策略的概念在 [Webview 指南](../webview.md#content-security-policy) 中详细介绍过。

<a id="learn-more"></a>
#### 了解更多（Learn more）

> - [MCP Apps 规范](https://modelcontextprotocol.github.io/ext-apps/api/)
> - [MCP Apps SDK 和示例](https://github.com/modelcontextprotocol/ext-apps)
> - [MCP Apps 发布博客文章](https://code.visualstudio.com/blogs/2026/01/26/mcp-apps-support)

<a id="icons"></a>
### 图标（Icons）

> VS Code 支持 MCP 服务器、资源和工具上提供的 `icons`。MCP 图标有一个 `src` 属性，它是指向图片的 URI：
>
> - 使用 HTTP 或 SSE 传输方式的 MCP 服务器，可以从托管 MCP 服务器的同一个域提供图片。例如，配置在 `https://example.com/mcp` 的服务器，可以从 `example.com` 提供图片。
> - 使用 stdio 传输方式的 MCP 服务器，可以用 `file:///` URI 从文件系统提供图片。
> - 任何 MCP 服务器都可以把图片嵌入为以 `data:` 开头的 data URI。

---

<a id="add-mcp-servers-to-vs-code"></a>
## 向 VS Code 添加 MCP 服务器（Add MCP servers to VS Code）

> 用户可以通过多种方式在 VS Code 中添加 MCP 服务器：
>
> - 直接从网页安装：在你的网站上使用一个特殊的 MCP 安装 URL（`vscode:mcp/install`）。
> - 工作区配置：在工作区的 `.vscode/mcp.json` 文件中指定服务器配置。
> - 全局配置：在用户[配置文件（profile）](https://code.visualstudio.com/docs/configure/profiles)中全局定义服务器。
> - 自动发现：VS Code 可以从 Claude Desktop 等其他工具中发现服务器。
> - 扩展：VS Code 扩展可以通过代码注册 MCP 服务器。
> - 命令行：使用 `--add-mcp` VS Code 命令行选项从命令行安装 MCP 服务器。
>
> 了解更多关于[向 VS Code 添加 MCP 服务器](https://code.visualstudio.com/docs/agent-customization/mcp-servers#add-an-mcp-server)的不同方式。

一个最简单的 `.vscode/mcp.json` 示例：

```json
{
  "servers": {
    "my-mcp-server": {
      "type": "stdio",
      "command": "node",
      "args": ["./build/index.js"]
    }
  }
}
```

其中第五种“扩展”方式，就是本篇后面[在扩展中注册 MCP 服务器](#register-an-mcp-server-in-your-extension)一节的内容。

---

<a id="manage-mcp-servers"></a>
## 管理 MCP 服务器（Manage MCP servers）

> 你可以在 VS Code 的扩展视图（`Ctrl+Shift+X`）中管理已安装的 MCP 服务器列表。

![扩展视图中的 MCP 服务器](../images/ai/mcp/extensions-view-mcp-servers.png)

> 右键点击某个 MCP 服务器，或者选择齿轮图标，可以对服务器执行不同的管理操作。或者，在命令面板中运行 **MCP: List Servers** 命令，查看已配置的 MCP 服务器列表。然后可以选择一个服务器，对它执行操作。

> **提示**
>
> 打开 `.vscode/mcp.json` 文件时，VS Code 会在编辑器中显示命令，让你可以直接在编辑器中启动、停止或重启服务器。
>
> ![MCP 服务器配置上用于管理服务器的 CodeLens](../images/ai/mcp/mcp-server-config-lenses.png)

截图中，`mcp.json` 中每个服务器配置的上方，都显示了一行可点击的灰色小字（Start、Stop、Restart 等），这就是 [扩展能力概览](../../extension-capabilities/overview.md) 中介绍过的 CodeLens。

---

<a id="create-an-mcp-installation-url"></a>
## 创建 MCP 安装 URL（Create an MCP installation URL）

> VS Code 提供了一个 URL 处理程序，可以通过链接安装 MCP 服务器：`vscode:mcp/install?{json-configuration}`（Insiders 版：`vscode-insiders:mcp/install?{json-configuration}`）。
>
> 以 `{\"name\":\"server-name\",\"command\":...}` 的形式提供 JSON 服务器配置，然后对它进行 JSON 序列化和 URL 编码。例如，用下面的逻辑创建安装 URL：

```typescript
// 对于 Insiders 版，用 `vscode-insiders` 代替 `code`
const link = `vscode:mcp/install?${encodeURIComponent(JSON.stringify(obj))}`;
```

> 这个链接可以在浏览器中使用，也可以在命令行中打开，例如在 Linux 上通过 `xdg-open $LINK` 打开。

（代码注释中的 “代替 `code`” 应为 “代替 `vscode`”。）

这和 [命令指南](../command.md#command-uris) 中命令 URI 的参数编码方式（`JSON.stringify` + `encodeURIComponent`）完全一样。比如：

```ts
const obj = { name: 'my-server', command: 'npx', args: ['-y', 'my-mcp-server'] };
const link = `vscode:mcp/install?${encodeURIComponent(JSON.stringify(obj))}`;
// 把 link 放在网页上：<a href="${link}">在 VS Code 中安装</a>
```

---

<a id="register-an-mcp-server-in-your-extension"></a>
## 在扩展中注册 MCP 服务器（Register an MCP server in your extension）

> 要在扩展中注册一个 MCP 服务器，需要执行以下步骤：
>
> 1. 在扩展的 `package.json` 文件中定义 MCP 服务器定义提供者（MCP server definition provider）。
> 2. 在扩展代码中使用 [`vscode.lm.registerMcpServerDefinitionProvider`](https://code.visualstudio.com/api/references/vscode-api#lm.registerMcpServerDefinitionProvider) API 实现这个 MCP 服务器定义提供者。
>
> 你可以从一个基础的[在 VS Code 扩展中注册 MCP 服务器的示例](https://github.com/microsoft/vscode-extension-samples/blob/main/mcp-extension-sample)开始。

**为什么要通过扩展来注册 MCP 服务器？** 用户手写 `mcp.json` 需要知道服务器的启动命令、参数、环境变量。如果你的扩展本身就附带了一个 MCP 服务器（或者知道怎么连接你们公司的远程服务器），就可以通过扩展自动注册，用户只需安装扩展，什么都不用配置。还可以在启动服务器前让用户登录、输入 API 密钥等。

<a id="1-static-configuration-in-packagejson"></a>
### 1. package.json 中的静态配置（1. Static configuration in `package.json`）

> 想要注册 MCP 服务器的扩展，必须在 `package.json` 中贡献 `contributes.mcpServerDefinitionProviders` 扩展点，并带上提供者的 `id`。这个 `id` 应该与实现中使用的那个一致。

```json
{
    ...
    "contributes": {
        "mcpServerDefinitionProviders": [
            {
                "id": "exampleProvider",
                "label": "Example MCP Server Provider"
            }
        ]
    }
    ...
}
```

<a id="2-implement-the-provider"></a>
### 2. 实现提供者（2. Implement the provider）

> 要在扩展中注册 MCP 服务器，使用 [`vscode.lm.registerMcpServerDefinitionProvider`](https://code.visualstudio.com/api/references/vscode-api#lm.registerMcpServerDefinitionProvider) API 为服务器提供 [MCP 配置](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)。这个 API 接收一个 `providerId` 字符串和一个 `McpServerDefinitionProvider` 对象。
>
> `McpServerDefinitionProvider` 对象有三个属性：

| 属性 | 作用 |
|---|---|
| `onDidChangeMcpServerDefinitions` | MCP 服务器配置发生变化时触发的事件（可选） |
| `provideMcpServerDefinitions` | 返回一个 MCP 服务器配置数组（`vscode.McpServerDefinition[]`）的函数 |
| `resolveMcpServerDefinition` | 需要启动 MCP 服务器时，编辑器调用的函数。用这个函数执行可能需要用户交互的额外操作，比如身份验证（可选） |

> `McpServerDefinition` 对象可以是以下类型之一：
>
> - `vscode.McpStdioServerDefinition`：表示一个通过运行本地进程、并在其 stdin 和 stdout 流上操作来使用的 MCP 服务器。
> - `vscode.McpHttpServerDefinition`：表示一个使用 Streamable HTTP 传输方式的 MCP 服务器。

这个“提供（provide）+ 解析（resolve）”的两步模式，和 [任务提供者](../task-provider.md) 的 `provideTasks` / `resolveTask`、[调试器扩展](../debugger-extension.md) 的 `provideDebugConfigurations` / `resolveDebugConfiguration` 是一样的思路：

```text
provideMcpServerDefinitions   ← 列出有哪些服务器（要快，不要弹窗）
         ↓ 用户真正要用某个服务器时
resolveMcpServerDefinition    ← 补全启动所需的信息（可以弹窗让用户登录、输入密钥）
         ↓
启动服务器
```

<details>
<summary>MCP 服务器定义提供者示例</summary>

> 下面的例子演示了如何在扩展中注册 MCP 服务器，并在启动服务器时提示用户输入 API 密钥。

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const didChangeEmitter = new vscode.EventEmitter<void>();

    context.subscriptions.push(vscode.lm.registerMcpServerDefinitionProvider('exampleProvider', {
        onDidChangeMcpServerDefinitions: didChangeEmitter.event,
        provideMcpServerDefinitions: async () => {
            let servers: vscode.McpServerDefinition[] = [];

            // 一个简单的 stdio 服务器定义示例
            servers.push(new vscode.McpStdioServerDefinition(
            {
                label: 'myServer',
                command: 'node',
                args: ['server.js'],
                cwd: vscode.Uri.file('/path/to/server'),
                env: {
                    API_KEY: ''
                },
                version: '1.0.0'
            });

            // 一个 HTTP 服务器定义示例
            servers.push(new vscode.McpHttpServerDefinition(
            {
                label: 'myRemoteServer',
                uri: 'http://localhost:3000',
                headers: {
                    'API_VERSION': '1.0.0'
                },
                version: '1.0.0'
            }));

            return servers;
        },
        resolveMcpServerDefinition: async (server: vscode.McpServerDefinition) => {

            if (server.label === 'myServer') {
                // 从用户那里获取 API 密钥，例如使用 vscode.window.showInputBox
                // 用 API 密钥更新服务器定义
            }

            // 返回 undefined 表示不应该启动这个服务器，或者抛出一个错误
            // 如果有正在等待的工具调用，编辑器会取消它，并向语言模型返回一条错误消息。
            return server;
        }
    }));
}
```

</details>

**原文这段示例代码与当前的 API 不一致，照抄无法编译：**

1. 在 `@types/vscode` 1.140 中，`McpStdioServerDefinition` 和 `McpHttpServerDefinition` 的构造函数接收的是**按位置排列的参数**，而不是一个对象：
    - `new McpStdioServerDefinition(label, command, args?, env?, version?)`，`cwd` 要在创建后单独设置；
    - `new McpHttpServerDefinition(label, uri, headers?, version?)`，其中 `uri` 必须是 `vscode.Uri`，不能是字符串。
2. 第一个 `servers.push(new ...({ ... });` 少了一个右括号，是语法错误。

按当前 API 修正后的写法：

```ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  const didChangeEmitter = new vscode.EventEmitter<void>();

  context.subscriptions.push(vscode.lm.registerMcpServerDefinitionProvider('exampleProvider', {
    onDidChangeMcpServerDefinitions: didChangeEmitter.event,

    provideMcpServerDefinitions: async () => {
      // stdio 服务器：用扩展自带的 server.js 启动
      const local = new vscode.McpStdioServerDefinition(
        'myServer',                    // label
        'node',                        // command
        ['server.js'],                 // args
        { API_KEY: '' },               // env：先留空，等 resolve 时再填
        '1.0.0'                        // version
      );
      local.cwd = vscode.Uri.joinPath(context.extensionUri, 'server');

      // HTTP 服务器
      const remote = new vscode.McpHttpServerDefinition(
        'myRemoteServer',
        vscode.Uri.parse('http://localhost:3000'),
        { 'API_VERSION': '1.0.0' },
        '1.0.0'
      );

      return [local, remote];
    },

    resolveMcpServerDefinition: async (server) => {
      if (server instanceof vscode.McpStdioServerDefinition && server.label === 'myServer') {
        // 启动前向用户要 API 密钥（也可以先从 context.secrets 中读取）
        const apiKey = await vscode.window.showInputBox({ prompt: '请输入 API 密钥', password: true });
        if (!apiKey) {
          return undefined;            // 用户取消：不启动服务器
        }
        server.env = { ...server.env, API_KEY: apiKey };
      }
      return server;
    }
  }));
}
```

- `cwd` 用了 `context.extensionUri`，指向扩展自带的 `server` 目录，比写死一个绝对路径可靠。
- API 密钥这种敏感信息，可以在用户第一次输入后存进 `context.secrets`（见 [通用能力](../../extension-capabilities/common-capabilities.md#data-storage)），下次直接读取，不用每次都问。
- 服务器列表发生变化时（比如用户修改了某个设置），调用 `didChangeEmitter.fire()`，VS Code 会重新调用 `provideMcpServerDefinitions`。

---

<a id="troubleshoot-and-debug-mcp-servers"></a>
## 排查和调试 MCP 服务器（Troubleshoot and debug MCP servers）

<a id="mcp-development-mode-in-vs-code"></a>
### VS Code 中的 MCP 开发模式（MCP development mode in VS Code）

> 开发 MCP 服务器时，你可以在 MCP 服务器配置中添加一个 `dev` 键，为 MCP 服务器启用_开发模式_。它是一个有两个属性的对象：
>
> - `watch`：一个 glob 模式，或者一个 glob 模式数组，用来监视文件的变化，文件变化时重启 MCP 服务器。
> - `debug`：让你可以为 MCP 服务器设置调试器。目前，VS Code 支持调试 Node.js 和 Python 的 MCP 服务器。

<details>
<summary>Node.js MCP 服务器</summary>

> 要调试一个 Node.js MCP 服务器，把 `debug.type` 属性设为 `node`。

```json
{
    "servers": {
        "my-mcp-server": {
            "type": "stdio",
            "command": "node",
            "cwd": "${workspaceFolder}",
            "args": [ "./build/index.js" ],
            "dev": {
                "watch": "src/**/*.ts",
                "debug": { "type": "node" }
            }
        }
    }
}
```

</details>

<details>
<summary>Python MCP 服务器</summary>

> 要调试一个 Python MCP 服务器，把 `debug.type` 属性设为 `debugpy`。如果 `debugpy` 模块没有安装在默认的 Python 环境中，可以选择性地把 `debug.debugpyPath` 属性设为它的路径。

```json
{
    "servers": {
        "my-python-mcp-server": {
            "type": "stdio",
            "command": "python",
            "cwd": "${workspaceFolder}",
            "args": [ "./server.py" ],
            "dev": {
                "watch": "**/*.py",
                "debug": {
                    "type": "debugpy",
                    "debugpyPath": "/path/to/debugpy"
                }
            }
        }
    }
}
```

</details>

开发模式的效果：修改源代码后服务器自动重启（`watch`）；启动服务器时自动附加调试器，可以在服务器代码中打断点（`debug`）。注意 Node.js 示例中 `watch` 监视的是 `src/**/*.ts`，而运行的是 `build/index.js`，所以还需要一个后台编译任务（`tsc --watch`），保证源代码改动后会重新编译。

<a id="mcp-output-log"></a>
### MCP 输出日志（MCP output log）

> 当 VS Code 遇到 MCP 服务器的问题时，会在聊天视图中显示一个错误指示。

![MCP 服务器错误](../images/ai/mcp/mcp-error-loading-tool.png)

> 在聊天视图中选择错误通知，然后选择 **Show Output**（显示输出）选项，查看服务器的日志。或者，在命令面板中运行 **MCP: List Servers**，选择服务器，然后选择 **Show Output**。

![MCP 服务器错误输出](../images/ai/mcp/mcp-server-error-output.png)

截图是“输出”面板中 MCP 服务器对应的输出通道，显示了服务器的启动过程和错误信息。

**stdio 服务器的一个常见坑：** stdio 方式下，标准输出（stdout）是用来传输 MCP 协议消息的。如果在服务器代码中用 `console.log` 打印调试信息，这些文字会混进协议消息里，导致通信出错。调试日志应该输出到标准错误（`console.error`），它会显示在这个输出面板中。

---

<a id="best-practices"></a>
## 最佳实践（Best practices）

> - 遵循**命名约定**，确保名称唯一且具有描述性
> - **实现适当的错误处理和校验**，提供描述性的错误消息
> - **使用进度报告**，告知用户耗时较长的操作
> - **让工具操作保持专注和原子性**，避免复杂的交互
> - **清楚地记录你的工具**，描述要能帮助用户理解什么时候使用它们
> - **妥善处理缺少的输入参数**，提供默认值或清晰的错误消息
> - **为资源设置 MIME 类型**，确保 VS Code 能正确处理不同类型的内容
> - **使用资源模板**，让用户在访问资源时可以提供输入参数
> - **缓存资源内容**，提高性能，减少不必要的网络请求
> - **为采样请求设置合理的 token 限制**，避免过度使用资源
> - **在使用采样响应之前先对其进行校验**

“专注和原子性”：一个工具只做一件明确的事。比如不要做一个“管理数据库”的大工具，而是拆成“列出表”“查询数据”“查看表结构”几个小工具。小工具的描述更清楚，模型更容易用对。工具描述的写法见 [语言模型工具](./tools.md#guidelines-and-conventions)。

<a id="naming-conventions"></a>
### 命名约定（Naming conventions）

> 推荐 MCP 服务器及其组件使用以下命名约定：

| 组件 | 命名约定 |
|-----------|----------------------------|
| 工具名称 | 在 MCP 服务器内唯一；描述操作及其对象；使用蛇形命名（snake case），结构为 `{verb}_{noun}`；示例：`generate_report`、`fetch_data`、`analyze_code` |
| 工具输入参数 | 描述参数的用途；多个单词的参数使用小驼峰命名（camelCase）；示例：`path`、`queryString`、`userId` |
| 资源名称 | 在 MCP 服务器内唯一；描述资源的内容；使用标题式大写；示例：`Application Logs`、`Database Table`、`GitHub Repository` |
| 资源模板参数 | 描述参数的用途；多个单词的参数使用小驼峰命名；示例：`name`、`repo`、`fileType` |
| 提示词名称 | 在 MCP 服务器内唯一；描述提示词的预期用途；多个单词时使用小驼峰命名；示例：`generateApiRoute`、`performSecurityReview`、`analyzeCodeQuality` |
| 提示词输入参数 | 描述参数的用途；多个单词的参数使用小驼峰命名；示例：`filePath`、`queryString`、`userId` |

（注意：这里推荐的工具参数命名是小驼峰（`queryString`），而 [语言模型工具](./tools.md#guidelines-and-conventions) 一篇的示例用的是蛇形（`destination_location`、`file_name`）。两种风格都可以，关键是在同一个服务器或扩展内保持一致。）

---

<a id="get-started-to-create-an-mcp-server"></a>
## 开始创建 MCP 服务器（Get started to create an MCP server）

> VS Code 拥有开发你自己的 MCP 服务器所需的全部工具。虽然 MCP 服务器可以用任何能处理 `stdout` 的语言编写，但 MCP 官方的 SDK 是一个很好的起点：
>
> - [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
> - [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
> - [Java SDK](https://github.com/modelcontextprotocol/java-sdk)
> - [Kotlin SDK](https://github.com/modelcontextprotocol/kotlin-sdk)
> - [C# SDK](https://github.com/modelcontextprotocol/csharp-sdk)
>
> 你可能还会发现 [MCP 初学者课程](https://github.com/microsoft/mcp-for-beginners)对构建你的第一个 MCP 服务器很有帮助。

---

<a id="related-content"></a>
## 相关内容（Related content）

> - [贡献一个语言模型工具](./tools.md)
> - [在智能体模式中使用 MCP 工具](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
> - [VS Code 精选的 MCP 服务器列表](https://code.visualstudio.com/mcp)
> - [模型上下文协议文档](https://modelcontextprotocol.io/)

---

## 本篇小结

```text
MCP：开放协议，MCP 客户端（VS Code 等） ⇄ MCP 服务器（独立程序，任何语言） ⇄ 外部服务
  传输：stdio（本地子进程）/ http（Streamable HTTP）/ sse（旧版）
  功能：工具（readOnlyHint 免确认）、资源（及模板）、提示词（/mcp.服务器.提示词）、
        征询、采样（借用用户的模型，需授权）、授权（OAuth，DCR → 客户端凭据）、根目录、MCP Apps、图标

用户添加服务器：安装 URL（vscode:mcp/install?编码后的 JSON）、.vscode/mcp.json、用户配置、自动发现、扩展、命令行

扩展中注册（扩展 API）
  package.json：contributes.mcpServerDefinitionProviders（id、label）
  代码：vscode.lm.registerMcpServerDefinitionProvider(id, {
          onDidChangeMcpServerDefinitions,
          provideMcpServerDefinitions → [McpStdioServerDefinition | McpHttpServerDefinition]
          resolveMcpServerDefinition  → 启动前补全信息（登录、密钥）；返回 undefined 则不启动
        })
  注意：两个定义类的构造函数是位置参数（1.140），HTTP 的 uri 是 Uri

调试：mcp.json 中 dev.watch（自动重启）、dev.debug（node / debugpy）；Show Output 看日志；
     stdio 服务器的调试输出要写到 stderr
```
