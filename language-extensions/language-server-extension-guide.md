# 语言服务器扩展指南（Language Server Extension Guide）

> 原文：[Language Server Extension Guide](https://code.visualstudio.com/api/language-extensions/language-server-extension-guide)
> 源文件：`microsoft/vscode-docs` → `api/language-extensions/language-server-extension-guide.md`（DateApproved: 10/7/2026）

> 正如你在[编程式语言功能](./programmatic-language-features.md)主题中看到的，可以直接使用 `languages.*` API 来实现语言功能。而语言服务器扩展，则提供了实现这类语言支持的另一种方式。
>
> 本主题：
>
> - 解释语言服务器扩展的好处。
> - 带你使用 [`Microsoft/vscode-languageserver-node`](https://github.com/microsoft/vscode-languageserver-node) 库构建一个语言服务器。你也可以直接跳到 [lsp-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-sample) 中的代码。

---

<a id="why-language-server"></a>
## 为什么需要语言服务器？（Why Language Server?）

> 语言服务器是一种特殊的 Visual Studio Code 扩展，它为许多编程语言提供编辑体验。借助语言服务器，你可以实现自动补全、错误检查（诊断）、跳转到定义，以及 VS Code 支持的许多其他[语言功能](./programmatic-language-features.md)。
>
> 然而，在 VS Code 中实现语言功能支持的过程中，我们发现了三个常见的问题：
>
> 首先，语言服务器通常是用它们自己的原生编程语言实现的，这给把它们与运行在 Node.js 运行时上的 VS Code 集成带来了挑战。
>
> 此外，语言功能可能很消耗资源。例如，为了正确地校验一个文件，语言服务器需要解析大量文件，为它们构建抽象语法树，并进行静态程序分析。这些操作可能带来显著的 CPU 和内存占用，而我们需要确保 VS Code 的性能不受影响。
>
> 最后，把多种语言工具与多种代码编辑器集成，可能需要大量的工作。从语言工具的角度看，它们需要适配具有不同 API 的代码编辑器。从代码编辑器的角度看，它们无法指望语言工具提供任何统一的 API。这使得在 `N` 个代码编辑器中实现 `M` 种语言的支持，需要 `M * N` 份工作。
>
> 为了解决这些问题，微软制定了[语言服务器协议](https://microsoft.github.io/language-server-protocol)，它标准化了语言工具与代码编辑器之间的通信。这样，语言服务器就可以用任何语言实现，并运行在自己的进程中以避免性能开销，因为它们通过语言服务器协议与代码编辑器通信。此外，任何兼容 LSP 的语言工具都可以与多个兼容 LSP 的代码编辑器集成，任何兼容 LSP 的代码编辑器也可以轻松地接入多个兼容 LSP 的语言工具。LSP 对语言工具的提供者和代码编辑器的厂商来说是双赢的！

![LSP、语言和编辑器](images/language-server-extension-guide/lsp-languages-editors.png)

左边 “NO LSP”：JavaScript、Python、Java 三种语言的工具，要分别对接 VS Code、Atom、Vim 三个编辑器，箭头两两交叉，共 3 × 3 = 9 份对接工作。右边 “LSP”：所有语言都只对接中间的协议（补全、诊断、悬停、格式化、定义……），所有编辑器也只对接这个协议，只需 3 + 3 = 6 份工作。

**三个问题与 LSP 的对应：**

| 问题 | LSP 的解决方式 |
|---|---|
| 语言工具通常用自己的语言写（比如 Go 的工具用 Go 写），难以集成进 Node.js 的 VS Code | 语言服务器是独立进程，用任意语言编写，通过协议通信 |
| 语言分析很耗资源，可能拖慢编辑器 | 在单独的进程中运行，不占用扩展宿主 |
| M 种语言 × N 个编辑器 = M × N 份工作 | 统一协议，变成 M + N |

> 在本指南中，我们将：
>
> - 解释如何使用提供的 [Node SDK](https://github.com/microsoft/vscode-languageserver-node) 在 VS Code 中构建一个语言服务器扩展。
> - 解释如何运行、调试、记录日志和测试语言服务器扩展。
> - 为你指出一些关于语言服务器的进阶主题。

---

<a id="implementing-a-language-server"></a>
## 实现一个语言服务器（Implementing a Language Server）

<a id="overview"></a>
### 概览（Overview）

> 在 VS Code 中，一个语言服务器由两部分组成：
>
> - 语言客户端（Language Client）：一个用 JavaScript / TypeScript 编写的普通 VS Code 扩展。这个扩展可以访问所有的 [VS Code 命名空间 API](https://code.visualstudio.com/api/references/vscode-api)。
> - 语言服务器（Language Server）：一个运行在单独进程中的语言分析工具。
>
> 如上所述，在单独的进程中运行语言服务器有两个好处：
>
> - 分析工具可以用任何语言实现，只要它能按照语言服务器协议与语言客户端通信。
> - 由于语言分析工具通常很消耗 CPU 和内存，在单独的进程中运行它们可以避免性能开销。
>
> 下面是 VS Code 运行两个语言服务器扩展的示意图。HTML 语言客户端和 PHP 语言客户端是用 TypeScript 编写的普通 VS Code 扩展。它们各自实例化一个对应的语言服务器，并通过 LSP 与之通信。尽管 PHP 语言服务器是用 PHP 编写的，它仍然可以通过 LSP 与 PHP 语言客户端通信。

![LSP 示意图](images/language-server-extension-guide/lsp-illustration.png)

图中，左边的 VS Code 里有一个扩展宿主（Extension Host），其中运行着 HTML 语言客户端和 PHP 语言客户端（都标着 TS，用 TypeScript 编写）；右边是两个独立进程：HTML 语言服务器（TS）和 PHP 语言服务器（PHP）。客户端和服务器之间的双向箭头是语言服务器协议，底层的消息格式是 **JSON RPC**。

| | 语言客户端 | 语言服务器 |
|---|---|---|
| 是什么 | 一个普通的 VS Code 扩展 | 一个独立的程序 |
| 运行在 | 扩展宿主中 | 自己的进程中 |
| 可以使用 `vscode` API | 可以 | 不可以（它只通过协议与客户端通信） |
| 使用的库（Node.js） | `vscode-languageclient` | `vscode-languageserver` |
| 职责 | 启动服务器；把 VS Code 的事件和请求转换成 LSP 消息，再把服务器的响应转换回来 | 分析代码，响应请求 |

使用 `vscode-languageclient` 时，客户端这一侧几乎不用写什么代码：库会根据服务器声明的能力，自动注册对应的 `registerXxxProvider`。

> 本指南会教你使用我们的 [Node SDK](https://github.com/microsoft/vscode-languageserver-node) 构建一个语言客户端 / 服务器。下文假设你已经熟悉 VS Code [扩展 API](../index.md)。

<a id="lsp-sample---a-simple-language-server-for-plain-text-files"></a>
### LSP 示例：一个用于纯文本文件的简单语言服务器（LSP Sample - A simple Language Server for plain text files）

> 我们来构建一个简单的语言服务器扩展，为纯文本文件实现自动补全和诊断。我们还会介绍客户端 / 服务器之间配置的同步。
>
> 如果你想直接看代码：
>
> - **[lsp-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-sample)**：本指南的源代码，带有详细的注释。
> - **[lsp-multi-server-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-multi-server-sample)**：**lsp-sample** 的一个带有详细注释的进阶版本，它为每个工作区文件夹启动一个不同的服务器实例，以支持 VS Code 中的[多根工作区](https://code.visualstudio.com/docs/editor/multi-root-workspaces)功能。
>
> 克隆仓库 [Microsoft/vscode-extension-samples](https://github.com/microsoft/vscode-extension-samples) 并打开示例：

```bash
> git clone https://github.com/microsoft/vscode-extension-samples.git
> cd vscode-extension-samples/lsp-sample
> npm install
> npm run compile
> code .
```

> 上面的命令会安装所有依赖，并打开 **lsp-sample** 工作区，其中同时包含客户端和服务器的代码。下面是 **lsp-sample** 结构的大致概览：

```text
.
├── client // 语言客户端
│   ├── src
│   │   ├── test // 语言客户端 / 服务器的端到端测试
│   │   └── extension.ts // 语言客户端的入口
├── package.json // 扩展清单
└── server // 语言服务器
    └── src
        └── server.ts // 语言服务器的入口
```

客户端和服务器是两个独立的 npm 项目（各有自己的 `package.json` 和依赖），根目录的 `package.json` 是扩展清单，同时用脚本统一编译两者。

<a id="explaining-the-language-client"></a>
### 解读“语言客户端”（Explaining the 'Language Client'）

> 我们先来看看 `/package.json`，它描述了语言客户端的能力。其中有两个值得关注的部分：
>
> 首先，看看 [`configuration`](../references/contribution-points.md#contributes.configuration) 部分：

```json
"configuration": {
    "type": "object",
    "title": "Example configuration",
    "properties": {
        "languageServerExample.maxNumberOfProblems": {
            "scope": "resource",
            "type": "number",
            "default": 100,
            "description": "Controls the maximum number of problems produced by the server."
        }
    }
}
```

> 这一部分向 VS Code 贡献了 `configuration` 设置。示例会解释这些设置是如何在启动时、以及每次设置变化时被发送给语言服务器的。

这个设置的描述是：“控制服务器产生的问题的最大数量”。`"scope": "resource"` 表示它可以针对每个文件夹 / 文件单独设置（见 [贡献点](../references/contribution-points.md#contributes.configuration)），所以下文的服务器代码要按文件读取设置。

> **注意**：如果你的扩展兼容 1.74.0 之前的 VS Code 版本，你必须在 `/package.json` 的 [`activationEvents`](../references/activation-events.md) 字段中声明 `onLanguage:plaintext`，告诉 VS Code 一旦打开纯文本文件（例如扩展名为 `.txt` 的文件），就激活这个扩展：
>
> ```json
> "activationEvents": []
> ```

（原文这里的 JSON 写的是空数组，与正文不符，按正文应为 `"activationEvents": ["onLanguage:plaintext"]`。1.74.0 起，VS Code 会根据 `contributes` 中的内容自动生成激活事件，所以新扩展通常不需要手写，见 [激活事件](../references/activation-events.md)。不过这个示例并没有通过 `contributes.languages` 贡献语言，如果你发现扩展没有激活，就手动加上这一行。）

> 实际的语言客户端源代码和对应的 `package.json` 在 `/client` 文件夹中。`/client/package.json` 文件中值得关注的部分是：它通过 `engines` 字段引用 `vscode` 扩展宿主 API，并添加了对 `vscode-languageclient` 库的依赖：

```json
"engines": {
    "vscode": "^1.100.0"
},
"dependencies": {
    "vscode-languageclient": "^9.0.1"
}
```

> 如前所述，客户端是作为一个普通的 VS Code 扩展实现的，它可以访问所有的 VS Code 命名空间 API。
>
> 下面是对应的 extension.ts 文件的内容，它是 **lsp-sample** 扩展的入口：

```typescript
import * as path from 'path';
import { workspace, ExtensionContext } from 'vscode';

import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient | undefined;

export async function activate(context: ExtensionContext) {
  // 服务器是用 Node 实现的
  let serverModule = context.asAbsolutePath(path.join('server', 'out', 'server.js'));

  // 如果扩展以调试模式启动，就使用 debug 中的服务器选项
  // 否则使用 run 中的选项
  let serverOptions: ServerOptions = {
    run: { module: serverModule, transport: TransportKind.ipc },
    debug: {
      module: serverModule,
      transport: TransportKind.ipc
    }
  };

  // 控制语言客户端的选项
  let clientOptions: LanguageClientOptions = {
    // 为纯文本文档注册服务器
    documentSelector: [{ scheme: 'file', language: 'plaintext' }],
    synchronize: {
      // 当工作区中的 '.clientrc' 文件发生变化时，通知服务器
      fileEvents: workspace.createFileSystemWatcher('**/.clientrc')
    }
  };

  // 创建语言客户端，并启动客户端
  client = new LanguageClient(
    'languageServerExample',
    'Language Server Example',
    serverOptions,
    clientOptions
  );

  // 启动客户端。这也会启动服务器
  await client.start();
}

export async function deactivate() {
  await client?.dispose();
  client = undefined
}
```

**逐项解读：**

| 部分 | 含义 |
|---|---|
| `serverModule` | 服务器编译后的 JS 文件的绝对路径。`asAbsolutePath` 把扩展内的相对路径转为绝对路径 |
| `ServerOptions` 的 `run` / `debug` | 正常运行和调试时如何启动服务器，可以分别配置（比如调试时加上 `execArgv: ['--nolazy', '--inspect=6009']`，以便调试器附加） |
| `module` + `TransportKind.ipc` | 用 Node.js 启动这个模块，通过 Node 的 IPC 通道通信。其他传输方式有 `stdio`（标准输入输出）、`pipe`（命名管道）、`socket`。如果服务器不是 Node 程序，用 `{ command: '可执行文件路径', args: [...] }` 代替 `module` |
| `documentSelector` | 服务器负责哪些文档：只有这些文档的打开 / 修改 / 关闭事件和语言功能请求才会发给服务器 |
| `synchronize.fileEvents` | 把这些文件的变化（创建、修改、删除）通知服务器，服务器中由 `onDidChangeWatchedFiles` 处理 |
| `new LanguageClient(id, name, ...)` | `id` 用于设置项前缀（如下文的 `languageServerExample.trace.server`），`name` 是输出通道的名称 |
| `client.start()` | 启动服务器进程，完成 `initialize` 握手，并根据服务器声明的能力自动注册各种提供者 |
| `deactivate` 中的 `dispose()` | 停止客户端并关闭服务器进程。返回 Promise，VS Code 会等待它完成 |

<a id="explaining-the-language-server"></a>
### 解读“语言服务器”（Explaining the 'Language Server'）

> **注意**：从 GitHub 仓库克隆下来的“服务器”实现，已经是本次讲解最终的完整实现。如果想一步步跟着做，你可以新建一个 `server.ts`，或者修改克隆下来的版本的内容。
>
> 在这个示例中，服务器也是用 TypeScript 实现、用 Node.js 执行的。由于 VS Code 已经自带了一个 Node.js 运行时，所以没有必要提供你自己的运行时，除非你对运行时有特殊的要求。
>
> 语言服务器的源代码在 `/server` 中。服务器的 `package.json` 文件中值得关注的部分是：

```json
"dependencies": {
    "vscode-languageserver": "^9.0.1",
    "vscode-languageserver-textdocument": "^1.0.11"
}
```

> 这会引入 `vscode-languageserver` 库。
>
> 下面是一个服务器实现，它使用了库提供的文本文档管理器，这个管理器通过始终从 VS Code 向服务器发送增量变化来同步文本文档。

| 库 | 作用 |
|---|---|
| `vscode-languageserver` | 服务器端的 LSP 实现：创建连接、注册请求处理函数 |
| `vscode-languageserver-textdocument` | `TextDocument` 的实现：在服务器端维护文档内容，提供 `getText()`、`positionAt(offset)`、`offsetAt(position)` 等方法 |

```typescript
import {
  createConnection,
  TextDocuments,
  Diagnostic,
  DiagnosticSeverity,
  ProposedFeatures,
  InitializeParams,
  DidChangeConfigurationNotification,
  CompletionItem,
  CompletionItemKind,
  TextDocumentPositionParams,
  TextDocumentSyncKind,
  InitializeResult,
  DocumentDiagnosticReportKind,
  type DocumentDiagnosticReport
} from 'vscode-languageserver/node';

import {
  TextDocument
} from 'vscode-languageserver-textdocument';

// 为服务器创建一个连接，使用 Node 的 IPC 作为传输方式。
// 同时包含所有预览 / 提议中的 LSP 功能。
let connection = createConnection(ProposedFeatures.all);

// 创建一个简单的文本文档管理器。
let documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument);

let hasConfigurationCapability: boolean = false;
let hasWorkspaceFolderCapability: boolean = false;
let hasDiagnosticRelatedInformationCapability: boolean = false;

connection.onInitialize((params: InitializeParams) => {
  let capabilities = params.capabilities;

  // 客户端是否支持 `workspace/configuration` 请求？
  // 如果不支持，就退而使用全局设置。
  hasConfigurationCapability = !!(
    capabilities.workspace && !!capabilities.workspace.configuration
  );
  hasWorkspaceFolderCapability = !!(
    capabilities.workspace && !!capabilities.workspace.workspaceFolders
  );
  hasDiagnosticRelatedInformationCapability = !!(
    capabilities.textDocument &&
    capabilities.textDocument.publishDiagnostics &&
    capabilities.textDocument.publishDiagnostics.relatedInformation
  );

  const result: InitializeResult = {
    capabilities: {
      textDocumentSync: TextDocumentSyncKind.Incremental,
      // 告诉客户端，这个服务器支持代码补全。
      completionProvider: {
        resolveProvider: true
      },
      // 告诉客户端，这个服务器支持拉取诊断。
      diagnosticProvider: {
        interFileDependencies: false,
        workspaceDiagnostics: false
      }
    }
  };
  if (hasWorkspaceFolderCapability) {
    result.capabilities.workspace = {
      workspaceFolders: {
        supported: true
      }
    };
  }
  return result;
});

connection.onInitialized(() => {
  if (hasConfigurationCapability) {
    // 注册以接收所有配置变化的通知。
    connection.client.register(DidChangeConfigurationNotification.type, undefined);
  }
  if (hasWorkspaceFolderCapability) {
    connection.workspace.onDidChangeWorkspaceFolders(_event => {
      connection.console.log('Workspace folder change event received.');
    });
  }
});

// 示例的设置
interface ExampleSettings {
  maxNumberOfProblems: number;
}

// 全局设置，在客户端不支持 `workspace/configuration` 请求时使用。
// 请注意，在这个示例中搭配示例提供的客户端使用时，不会出现这种情况，
// 但搭配其他客户端时可能会出现。
const defaultSettings: ExampleSettings = { maxNumberOfProblems: 1000 };
let globalSettings: ExampleSettings = defaultSettings;

// 缓存所有打开的文档的设置
let documentSettings: Map<string, Thenable<ExampleSettings>> = new Map();

connection.onDidChangeConfiguration(change => {
  if (hasConfigurationCapability) {
    // 清空所有缓存的文档设置
    documentSettings.clear();
  } else {
    globalSettings = <ExampleSettings>(
      (change.settings.languageServerExample || defaultSettings)
    );
  }

  // 请客户端使用更新后的设置重新请求诊断。
  connection.languages.diagnostics.refresh();
});

function getDocumentSettings(resource: string): Thenable<ExampleSettings> {
  if (!hasConfigurationCapability) {
    return Promise.resolve(globalSettings);
  }
  let result = documentSettings.get(resource);
  if (!result) {
    result = connection.workspace.getConfiguration({
      scopeUri: resource,
      section: 'languageServerExample'
    });
    documentSettings.set(resource, result);
  }
  return result;
}

// 只保留打开的文档的设置
documents.onDidClose(e => {
  documentSettings.delete(e.document.uri);
});

// 当客户端为一个文档请求诊断时，调用这个处理函数。
connection.languages.diagnostics.on(async (params): Promise<DocumentDiagnosticReport> => {
  const document = documents.get(params.textDocument.uri);
  if (document !== undefined) {
    return {
      kind: DocumentDiagnosticReportKind.Full,
      items: await validateTextDocument(document)
    };
  } else {
    // 这个示例只校验由 TextDocuments 管理的打开的文档。
    // 对于我们不认识的文档，返回一个空的报告。
    return {
      kind: DocumentDiagnosticReportKind.Full,
      items: []
    };
  }
});

async function validateTextDocument(textDocument: TextDocument): Promise<Diagnostic[]> {
  // 在这个简单的示例中，每次校验时都获取一次设置。
  let settings = await getDocumentSettings(textDocument.uri);

  // 校验器为所有长度为 2 及以上的全大写单词创建诊断
  let text = textDocument.getText();
  let pattern = /\b[A-Z]{2,}\b/g;
  let m: RegExpExecArray | null;

  let problems = 0;
  let diagnostics: Diagnostic[] = [];
  while ((m = pattern.exec(text)) && problems < settings.maxNumberOfProblems) {
    problems++;
    let diagnostic: Diagnostic = {
      severity: DiagnosticSeverity.Warning,
      range: {
        start: textDocument.positionAt(m.index),
        end: textDocument.positionAt(m.index + m[0].length)
      },
      message: `${m[0]} is all uppercase.`,
      source: 'ex'
    };
    if (hasDiagnosticRelatedInformationCapability) {
      diagnostic.relatedInformation = [
        {
          location: {
            uri: textDocument.uri,
            range: Object.assign({}, diagnostic.range)
          },
          message: 'Spelling matters'
        },
        {
          location: {
            uri: textDocument.uri,
            range: Object.assign({}, diagnostic.range)
          },
          message: 'Particularly for names'
        }
      ];
    }
    diagnostics.push(diagnostic);
  }

  return diagnostics;
}

connection.onDidChangeWatchedFiles(_change => {
  // 被监视的文件在 VS Code 中发生了变化
  connection.console.log('We received a file change event');
});

// 这个处理函数提供补全项的初始列表。
connection.onCompletion(
  (_textDocumentPosition: TextDocumentPositionParams): CompletionItem[] => {
    // 传入的参数包含了请求代码补全的文本文档中的位置。
    // 在这个示例中，我们忽略这个信息，总是提供相同的补全项。
    return [
      {
        label: 'TypeScript',
        kind: CompletionItemKind.Text,
        data: 1
      },
      {
        label: 'JavaScript',
        kind: CompletionItemKind.Text,
        data: 2
      }
    ];
  }
);

// 这个处理函数为补全列表中选中的项解析额外的信息。
connection.onCompletionResolve(
  (item: CompletionItem): CompletionItem => {
    if (item.data === 1) {
      item.detail = 'TypeScript details';
      item.documentation = 'TypeScript documentation';
    } else if (item.data === 2) {
      item.detail = 'JavaScript details';
      item.documentation = 'JavaScript documentation';
    }
    return item;
  }
);

// 让文本文档管理器在连接上监听
// 文本文档的打开、修改和关闭事件
documents.listen(connection);

// 在连接上开始监听
connection.listen();
```

这段代码较长，按执行的先后顺序梳理一下：

```text
1. createConnection          建立与客户端的连接（传输方式由客户端启动时的参数决定，这里是 IPC）
2. new TextDocuments         文档管理器：自动处理 didOpen / didChange / didClose，在服务器端保存文档的最新内容
3. onInitialize              握手：读取客户端的能力（params.capabilities），返回服务器的能力（result.capabilities）
4. onInitialized             握手完成后：动态注册配置变化通知、监听工作区文件夹变化
5. 各种处理函数               onDidChangeConfiguration、diagnostics.on、onCompletion、onCompletionResolve……
6. documents.listen + connection.listen   开始工作
```

**能力的双向协商：** `onInitialize` 中有两种“能力”，不要混淆：

| | 来源 | 示例中的用法 |
|---|---|---|
| 客户端能力（`params.capabilities`） | 客户端告诉服务器“我支持什么” | 检查客户端是否支持 `workspace/configuration`（按文件读取设置）、诊断的 `relatedInformation`。不支持时退而求其次，这样服务器也能配合其他功能较少的编辑器使用 |
| 服务器能力（返回的 `capabilities`） | 服务器告诉客户端“我提供什么” | `textDocumentSync`（文档同步方式）、`completionProvider`（补全）、`diagnosticProvider`（拉取诊断） |

`textDocumentSync: TextDocumentSyncKind.Incremental` 表示文档修改时，客户端只发送变化的部分（增量），而不是整个文档；`TextDocuments` 管理器会把增量应用到它保存的文档上。

<a id="adding-a-simple-validation"></a>
### 添加一个简单的校验（Adding a Simple Validation）

> 要为服务器添加文档校验，需要为 `textDocument/diagnostic` 请求注册一个处理函数。使用拉取诊断时，由客户端决定何时需要新的结果，例如在你打开或编辑一个文档之后。`TextDocuments` 管理器让服务器保存的文档副本保持最新，所以处理函数可以校验文档的当前内容。
>
> 初始化代码中的 `diagnosticProvider` 能力告诉客户端，服务器支持这些请求。这个示例把 `interFileDependencies` 设为 `false`，因为每个文档都是独立校验的；把 `workspaceDiagnostics` 设为 `false`，因为它不提供工作区范围的诊断。
>
> 处理函数调用 `validateTextDocument`，它会标记出两个及以上字母的全大写单词，并把结果返回给客户端：

```typescript
// 当客户端为一个文档请求诊断时，调用这个处理函数。
connection.languages.diagnostics.on(async (params): Promise<DocumentDiagnosticReport> => {
  const document = documents.get(params.textDocument.uri);
  if (document !== undefined) {
    return {
      kind: DocumentDiagnosticReportKind.Full,
      items: await validateTextDocument(document)
    };
  } else {
    // 这个示例只校验由 TextDocuments 管理的打开的文档。
    // 对于我们不认识的文档，返回一个空的报告。
    return {
      kind: DocumentDiagnosticReportKind.Full,
      items: []
    };
  }
});

async function validateTextDocument(textDocument: TextDocument): Promise<Diagnostic[]> {
  // 在这个简单的示例中，每次校验时都获取一次设置。
  let settings = await getDocumentSettings(textDocument.uri);

  // 校验器为所有长度为 2 及以上的全大写单词创建诊断
  let text = textDocument.getText();
  let pattern = /\b[A-Z]{2,}\b/g;
  let m: RegExpExecArray | null;

  let problems = 0;
  let diagnostics: Diagnostic[] = [];
  while ((m = pattern.exec(text)) && problems < settings.maxNumberOfProblems) {
    problems++;
    let diagnostic: Diagnostic = {
      severity: DiagnosticSeverity.Warning,
      range: {
        // positionAt 把字符偏移量换算成 { line, character }
        start: textDocument.positionAt(m.index),
        end: textDocument.positionAt(m.index + m[0].length)
      },
      message: `${m[0]} is all uppercase.`,
      source: 'ex'   // 诊断的来源，显示在“问题”面板中
    };
    if (hasDiagnosticRelatedInformationCapability) {
      // 相关信息：在诊断的悬停和“问题”面板中显示为可点击的附加位置
      diagnostic.relatedInformation = [
        {
          location: {
            uri: textDocument.uri,
            range: Object.assign({}, diagnostic.range)
          },
          message: 'Spelling matters'
        },
        {
          location: {
            uri: textDocument.uri,
            range: Object.assign({}, diagnostic.range)
          },
          message: 'Particularly for names'
        }
      ];
    }
    diagnostics.push(diagnostic);
  }

  return diagnostics;
}
```

> 完整报告（full report）会替换这个文档之前的诊断。返回一个空的 `items` 数组会清除之前的所有问题。与推送模型不同，服务器不会在文档变化的监听函数中发送诊断，而是在响应客户端的请求时返回它们。

| | 拉取模型（本示例） | 推送模型 |
|---|---|---|
| 服务器能力 | `diagnosticProvider` | 不需要声明 |
| 服务器代码 | `connection.languages.diagnostics.on(...)` 返回报告 | 在 `documents.onDidChangeContent` 中校验，然后 `connection.sendDiagnostics({ uri, diagnostics })` |
| 何时计算 | 客户端需要时（打开、编辑、可见时） | 服务器自己决定 |
| 设置变化后 | `connection.languages.diagnostics.refresh()` 请客户端重新拉取 | 服务器自己对所有文档重新校验并推送 |

`DocumentDiagnosticReportKind` 除了 `Full`，还有 `Unchanged`：如果服务器知道结果没有变化，可以只返回 `resultId`，客户端沿用上次的结果，节省计算。示例为了简单，每次都返回完整报告。

<a id="diagnostics-tips-and-tricks"></a>
### 诊断的小技巧（Diagnostics Tips and Tricks）

> - 如果开始位置和结束位置相同，VS Code 会用波浪线标出这个位置上的单词。
> - 如果你想用波浪线一直标到行尾，就把结束位置的 character 设为 Number.MAX_VALUE。

第一条适合“只知道错误在哪个位置、不知道范围”的情况（很多编译器只报告行列号）。

> 要运行语言服务器，执行以下步骤：
>
> - 按 `Ctrl+Shift+B` 启动构建任务。这个任务会同时编译客户端和服务器。
> - 打开 **Run**（运行）视图，选择 **Launch Client** 启动配置，然后点击 **Start Debugging**（开始调试）按钮，启动一个额外的 VS Code **扩展开发宿主**实例来执行扩展代码。
> - 在根文件夹中创建一个 `test.txt` 文件，并粘贴以下内容：

（macOS 上的构建快捷键是 `Cmd+Shift+B`。）

```text
TypeScript lets you write JavaScript the way you really want to.
TypeScript is a typed superset of JavaScript that compiles to plain JavaScript.
ANY browser. ANY host. ANY OS. Open Source.
```

> 这时**扩展开发宿主**实例看起来是这样的：

![校验一个文本文件](images/language-server-extension-guide/validation.png)

截图中，第 3 行的 `ANY`（3 处）和 `OS` 下面都有波浪线，共 4 个警告（状态栏左下角显示 0 个错误、4 个警告，资源管理器中 `test.txt` 旁边也显示数字 4）。`TypeScript` 和 `JavaScript` 不是全大写，所以没有被标出。

<a id="debugging-both-client-and-server"></a>
### 同时调试客户端和服务器（Debugging both Client and Server）

> 调试客户端代码和调试普通扩展一样简单。在客户端代码中设置一个断点，然后按 `F5` 调试扩展。

![调试客户端](images/language-server-extension-guide/debugging-client.png)

> 示例的 **Launch Client** 配置启用了 `autoAttachChildProcesses`，所以 VS Code 也会附加到由 `LanguageClient` 启动的服务器上。要调试校验逻辑，就在 `server/src/server.ts` 中的 `validateTextDocument` 里设置一个断点，然后在 **Run and Debug**（运行和调试）视图中启动 **Launch Client**。在**扩展开发宿主**中打开或编辑一个纯文本文件，就会触发断点。

![自动附加的语言服务器在 validateTextDocument 中的断点处暂停的截图](images/language-server-extension-guide/debugging-server.png)

截图中，“调用堆栈”里同时有 `Extension Host [0]`（客户端所在的扩展宿主）和 `server.js [99784]`（语言服务器进程，状态为 PAUSED ON BREAKPOINT），服务器停在 `server.ts` 第 154 行 `getDocumentSettings` 的调用处；左侧“变量”面板中可以看到 `textDocument` 的内容（`_content` 为 `'TypeScript lets you write JavaScript the way ...'`、`_languageId` 为 `'plaintext'`）。

**为什么服务器需要单独附加？** 服务器是另一个进程，调试扩展宿主不会自动调试它。`autoAttachChildProcesses: true` 让调试器自动附加到扩展宿主启动的子进程上，于是一次 `F5` 就能同时调试两边。

<a id="logging-support-for-language-server"></a>
### 语言服务器的日志支持（Logging Support for Language Server）

> 如果你在使用 `vscode-languageclient`，可以设置 `[clientId].trace.server` 来记录客户端 / 服务器之间的通信，其中 `clientId` 是传给 `LanguageClient` 的 ID。输出通道使用客户端的 `name`。
>
> 对于 **lsp-sample**，你可以这样设置：`"languageServerExample.trace.server": "verbose"`。在**输出**面板中打开 **Language Server Example** 通道。跟踪信息显示，客户端发送了一个 `textDocument/diagnostic` 请求，并收到了一个完整的诊断报告：

![输出面板中显示一次拉取诊断请求及服务器响应的截图](images/language-server-extension-guide/lsp-log.png)

截图中的两段日志：

```text
[Trace - 12:00:51 AM] Sending request 'textDocument/diagnostic - (5)'.    ← 客户端发出的第 5 个请求
Params: { "textDocument": { "uri": "file:///.../test.txt" } }

[Trace - 12:00:51 AM] Received response 'textDocument/diagnostic - (5)' in 0ms.
Result: { "kind": "full", "items": [] }                                  ← 完整报告，这次没有问题
```

`trace.server` 的取值是 `off`、`messages`（只记录消息名称）、`verbose`（同时记录消息内容）。这个设置由 `vscode-languageclient` 自动支持，但要在设置中看到它的补全，需要在扩展的 `contributes.configuration` 中也声明 `languageServerExample.trace.server`（lsp-sample 的完整 `package.json` 中就声明了它）。调试 LSP 时，这是最直接的手段：能看到每一个请求、通知和响应。

<a id="using-configuration-settings-in-the-server"></a>
### 在服务器中使用配置设置（Using Configuration Settings in the Server）

> 编写扩展的客户端部分时，我们已经定义了一个控制报告的问题最大数量的设置。我们也在服务器端编写了代码，从客户端读取这些设置：

```typescript
function getDocumentSettings(resource: string): Thenable<ExampleSettings> {
  if (!hasConfigurationCapability) {
    return Promise.resolve(globalSettings);
  }
  let result = documentSettings.get(resource);
  if (!result) {
    // 向客户端发送 workspace/configuration 请求，读取这个文件的设置
    result = connection.workspace.getConfiguration({
      scopeUri: resource,
      section: 'languageServerExample'
    });
    documentSettings.set(resource, result);
  }
  return result;
}
```

服务器不能直接调用 `vscode.workspace.getConfiguration`（它不在扩展宿主中），所以通过 LSP 的 `workspace/configuration` 请求**向客户端索要**设置。`scopeUri` 指明要哪个文件的设置（因为设置的 `scope` 是 `resource`，不同文件夹的值可能不同），`section` 是设置的前缀。结果按文件缓存在 `documentSettings` 中，避免每次校验都发请求。

> `validateTextDocument` 中的校验逻辑会读取 `maxNumberOfProblems` 设置，并限制返回的诊断数量：

```typescript
async function validateTextDocument(textDocument: TextDocument): Promise<Diagnostic[]> {
  // 在这个简单的示例中，每次校验时都获取一次设置。
  let settings = await getDocumentSettings(textDocument.uri);

  // 校验器为所有长度为 2 及以上的全大写单词创建诊断
  let text = textDocument.getText();
  let pattern = /\b[A-Z]{2,}\b/g;
  let m: RegExpExecArray | null;

  let problems = 0;
  let diagnostics: Diagnostic[] = [];
  while ((m = pattern.exec(text)) && problems < settings.maxNumberOfProblems) {
    problems++;
    let diagnostic: Diagnostic = {
      severity: DiagnosticSeverity.Warning,
      range: {
        start: textDocument.positionAt(m.index),
        end: textDocument.positionAt(m.index + m[0].length)
      },
      message: `${m[0]} is all uppercase.`,
      source: 'ex'
    };
    if (hasDiagnosticRelatedInformationCapability) {
      diagnostic.relatedInformation = [
        {
          location: {
            uri: textDocument.uri,
            range: Object.assign({}, diagnostic.range)
          },
          message: 'Spelling matters'
        },
        {
          location: {
            uri: textDocument.uri,
            range: Object.assign({}, diagnostic.range)
          },
          message: 'Particularly for names'
        }
      ];
    }
    diagnostics.push(diagnostic);
  }

  return diagnostics;
}
```

> 即使文档的文字没有变化，配置的变化也可能影响诊断。清除缓存的设置，并调用 `connection.languages.diagnostics.refresh()` 发送一个 `workspace/diagnostic/refresh` 请求。然后客户端会请求新的诊断，校验器会读取更新后的设置：

```typescript
connection.onDidChangeConfiguration(change => {
  if (hasConfigurationCapability) {
    // 清空所有缓存的文档设置
    documentSettings.clear();
  } else {
    globalSettings = <ExampleSettings>(
      (change.settings.languageServerExample || defaultSettings)
    );
  }

  // 请客户端使用更新后的设置重新请求诊断。
  connection.languages.diagnostics.refresh();
});
```

配置相关的完整流程：

```text
用户修改设置
  → 客户端发送 workspace/didChangeConfiguration 通知（因为 onInitialized 中注册了 DidChangeConfigurationNotification）
  → 服务器 onDidChangeConfiguration：清空设置缓存
  → 服务器发送 workspace/diagnostic/refresh 请求
  → 客户端对打开的文档重新发送 textDocument/diagnostic 请求
  → 服务器 validateTextDocument → getDocumentSettings（缓存已清空，重新向客户端读取）→ 按新的上限返回诊断
```

> 再次启动客户端，并把设置改为最多报告 1 个问题，校验结果如下：

![最多一个问题](images/language-server-extension-guide/validationOneProblem.png)

（截图中只有第一个 `ANY` 下面有波浪线。）

<a id="adding-additional-language-features"></a>
### 添加更多的语言功能（Adding additional Language Features）

> 语言服务器通常实现的第一个有意思的功能，是文档校验。从这个意义上说，即使是一个 linter 也算是一个语言服务器，而在 VS Code 中，linter 通常都是作为语言服务器实现的（参见 [eslint](https://github.com/microsoft/vscode-eslint) 和 [jshint](https://github.com/microsoft/vscode-jshint) 的例子）。但语言服务器能做的远不止这些。它们可以提供代码补全、查找所有引用或跳转到定义。下面的示例代码为服务器添加了代码补全。它会建议 'TypeScript' 和 'JavaScript' 这两个词。

```typescript
// 这个处理函数提供补全项的初始列表。
connection.onCompletion(
  (_textDocumentPosition: TextDocumentPositionParams): CompletionItem[] => {
    // 传入的参数包含了请求代码补全的文本文档中的位置。
    // 在这个示例中，我们忽略这个信息，总是提供相同的补全项。
    return [
      {
        label: 'TypeScript',
        kind: CompletionItemKind.Text,
        data: 1
      },
      {
        label: 'JavaScript',
        kind: CompletionItemKind.Text,
        data: 2
      }
    ];
  }
);

// 这个处理函数为补全列表中选中的项解析额外的信息。
connection.onCompletionResolve(
  (item: CompletionItem): CompletionItem => {
    if (item.data === 1) {
      item.detail = 'TypeScript details';
      item.documentation = 'TypeScript documentation';
    } else if (item.data === 2) {
      item.detail = 'JavaScript details';
      item.documentation = 'JavaScript documentation';
    }
    return item;
  }
);
```

> `data` 字段用于在 resolve 处理函数中唯一地标识一个补全项。data 属性对协议是透明的。由于底层的消息传递协议基于 JSON，data 字段只应该保存可以与 JSON 相互序列化的数据。

“对协议透明”：协议不关心 `data` 里是什么，原样把它传给客户端，用户选中这一项时，客户端再原样传回 `completionItem/resolve` 请求中。所以它是服务器给自己留的“记号”，常用来存放一个 ID 或者计算详细信息所需的参数。不能放函数、类实例等无法 JSON 序列化的东西。

> 现在只差告诉 VS Code，服务器支持代码补全请求。为此，在 initialize 处理函数中标记对应的能力：

```typescript
connection.onInitialize((params): InitializeResult => {
    ...
    return {
        capabilities: {
            ...
            // 告诉客户端，服务器支持代码补全
            completionProvider: {
                resolveProvider: true
            }
        }
    };
});
```

> 下面的截图显示了完成的代码在一个纯文本文件上运行的效果：

![代码补全](images/language-server-extension-guide/codeComplete.png)

**添加其他语言功能的通用步骤**（以悬停为例）：

1. 在 `onInitialize` 返回的 `capabilities` 中声明 `hoverProvider: true`；
2. 注册处理函数 `connection.onHover(params => ({ contents: '...' }))`。

客户端不需要任何改动。`connection.onXxx` 与 LSP 方法、VS Code API 的对应关系，见 [编程式语言功能](./programmatic-language-features.md#language-features-listing)。

<a id="testing-the-language-server"></a>
### 测试语言服务器（Testing The Language Server）

> 要创建一个高质量的语言服务器，我们需要构建一个覆盖其功能的良好测试套件。测试语言服务器有两种常见的方式：
>
> - 单元测试：如果你想通过模拟发送给语言服务器的所有信息，来测试语言服务器中的特定功能，这种方式很有用。VS Code 的 [HTML](https://github.com/microsoft/vscode-html-languageservice) / [CSS](https://github.com/microsoft/vscode-css-languageservice) / [JSON](https://github.com/microsoft/vscode-json-languageservice) 语言服务器采用的就是这种测试方式。LSP 的 npm 模块也使用这种方式。[这里](https://github.com/microsoft/vscode-languageserver-node/blob/main/protocol/src/node/test/connection.test.ts)有一些使用 npm 协议模块编写的单元测试。
> - 端到端测试：这类似于 [VS Code 扩展测试](../working-with-extensions/testing-extension.md)。这种方式的好处是，它在运行测试时会实例化一个带有工作区的 VS Code 实例，打开文件，激活语言客户端 / 服务器，并运行 [VS Code 命令](../references/commands.md)。如果你有难以甚至无法模拟的文件、设置或依赖（例如 `node_modules`），这种方式更胜一筹。流行的 [Python](https://github.com/microsoft/vscode-python) 扩展采用的就是这种测试方式。
>
> 单元测试可以用你选择的任何测试框架来做。这里我们介绍如何为语言服务器扩展做端到端测试。
>
> 打开 `.vscode/launch.json`，你可以找到一个 `E2E` 测试目标：

```json
{
  "name": "Language Server E2E Test",
  "type": "extensionHost",
  "request": "launch",
  "runtimeExecutable": "${execPath}",
  "args": [
    "--extensionDevelopmentPath=${workspaceRoot}",
    "--extensionTestsPath=${workspaceRoot}/client/out/test/index",
    "${workspaceRoot}/client/testFixture"
  ],
  "outFiles": ["${workspaceRoot}/client/out/test/**/*.js"]
}
```

| 参数 | 含义 |
|---|---|
| `--extensionDevelopmentPath` | 要加载的开发中的扩展 |
| `--extensionTestsPath` | 测试入口（编译后的测试运行器） |
| 最后一个参数 `client/testFixture` | 在测试实例中打开的工作区文件夹，里面放着测试用的文件（如 `completion.txt`） |

（`${workspaceRoot}` 是旧的变量名，现在推荐使用 `${workspaceFolder}`，两者含义相同。）

> 如果你运行这个调试目标，它会启动一个以 `client/testFixture` 为活动工作区的 VS Code 实例。然后 VS Code 会执行 `client/src/test` 中的所有测试。一个调试技巧是，你可以在 `client/src/test` 中的 TypeScript 文件里设置断点，它们会被命中。
>
> 我们来看看 `completion.test.ts` 文件：

```ts
import * as vscode from 'vscode';
import * as assert from 'assert';
import { getDocUri, activate } from './helper';

suite('Should do completion', () => {
  const docUri = getDocUri('completion.txt');

  test('Completes JS/TS in txt file', async () => {
    await testCompletion(docUri, new vscode.Position(0, 0), {
      items: [
        { label: 'JavaScript', kind: vscode.CompletionItemKind.Text },
        { label: 'TypeScript', kind: vscode.CompletionItemKind.Text }
      ]
    });
  });
});

async function testCompletion(
  docUri: vscode.Uri,
  position: vscode.Position,
  expectedCompletionList: vscode.CompletionList
) {
  await activate(docUri);

  // 执行 `vscode.executeCompletionItemProvider` 命令，模拟触发补全
  const actualCompletionList = (await vscode.commands.executeCommand(
    'vscode.executeCompletionItemProvider',
    docUri,
    position
  )) as vscode.CompletionList;

  assert.ok(actualCompletionList.items.length >= 2);
  expectedCompletionList.items.forEach((expectedItem, i) => {
    const actualItem = actualCompletionList.items[i];
    assert.equal(actualItem.label, expectedItem.label);
    assert.equal(actualItem.kind, expectedItem.kind);
  });
}
```

> 在这个测试中，我们：
>
> - 激活扩展。
> - 用一个 URI 和一个位置运行 `vscode.executeCompletionItemProvider` 命令，模拟触发补全。
> - 把返回的补全项与我们期望的补全项进行断言比较。

注意期望的顺序是 `JavaScript` 在前、`TypeScript` 在后，与服务器返回的顺序相反：`vscode.executeCompletionItemProvider` 返回的列表是经过 VS Code 排序的（默认按标签字母顺序）。这也说明端到端测试验证的是“用户实际看到的结果”。`suite` / `test` 是 Mocha 的 TDD 风格接口。

> 我们再深入看看 `activate(docURI)` 函数。它定义在 `client/src/test/helper.ts` 中：

```ts
import * as vscode from 'vscode';
import * as path from 'path';

export let doc: vscode.TextDocument;
export let editor: vscode.TextEditor;
export let documentEol: string;
export let platformEol: string;

/**
 * 激活 vscode.lsp-sample 扩展
 */
export async function activate(docUri: vscode.Uri) {
  // extensionId 是 package.json 中的 `publisher.name`
  const ext = vscode.extensions.getExtension('vscode-samples.lsp-sample')!;
  await ext.activate();
  try {
    doc = await vscode.workspace.openTextDocument(docUri);
    editor = await vscode.window.showTextDocument(doc);
    await sleep(2000); // 等待服务器启动
  } catch (e) {
    console.error(e);
  }
}

async function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

> 在激活部分，我们：
>
> - 使用 `package.json` 中定义的 `{publisher.name}.{extensionId}` 获取扩展。
> - 打开指定的文档，并在活动的文本编辑器中显示它。
> - 等待 2 秒，以确保语言服务器已经实例化。

扩展的 ID 是 `发布者.扩展名`，即 `package.json` 中的 `publisher` 字段和 `name` 字段用点连接（这里是 `vscode-samples.lsp-sample`）。原文列表中的 `{publisher.name}.{extensionId}` 写法有些含糊，以代码注释为准。

固定等待 2 秒是一种简单但不太可靠的做法（机器慢时可能不够，快时又浪费时间）。更稳妥的做法是让客户端扩展的 `activate` 返回 `client`（或者一个在 `client.start()` 完成后才 resolve 的 Promise），测试中通过 `ext.exports` 拿到它并等待。

> 准备工作完成之后，我们就可以运行与每个语言功能对应的 [VS Code 命令](../references/commands.md)，并对返回的结果进行断言。
>
> 还有一个测试覆盖了我们刚刚实现的诊断功能。可以在 `client/src/test/diagnostics.test.ts` 中查看它。

诊断的测试不通过命令，而是在打开文档后用 `vscode.languages.getDiagnostics(docUri)` 读取诊断，再与期望值比较。

---

<a id="advanced-topics"></a>
## 进阶主题（Advanced Topics）

> 到目前为止，本指南介绍了：
>
> - 语言服务器和语言服务器协议的简要概述。
> - VS Code 中语言服务器扩展的架构
> - **lsp-sample** 扩展，以及如何开发 / 调试 / 检查 / 测试它。
>
> 还有一些更进阶的主题我们没能放进本指南中。我们会附上这些资源的链接，供你进一步学习语言服务器开发。

<a id="additional-language-server-features"></a>
### 更多的语言服务器功能（Additional Language Server features）

> 除了代码补全之外，语言服务器目前还支持以下语言功能：
>
> - *文档高亮（Document Highlights）*：高亮文本文档中所有“相同”的符号。
> - *悬停（Hover）*：为文本文档中选中的符号提供悬停信息。
> - *签名帮助（Signature Help）*：为文本文档中选中的符号提供签名帮助。
> - *跳转到定义（Goto Definition）*：为文本文档中选中的符号提供跳转到定义的支持。
> - *跳转到类型定义（Goto Type Definition）*：为文本文档中选中的符号提供跳转到类型 / 接口定义的支持。
> - *跳转到实现（Goto Implementation）*：为文本文档中选中的符号提供跳转到实现定义的支持。
> - *查找引用（Find References）*：为文本文档中选中的符号查找项目范围内的所有引用。
> - *列出文档符号（List Document Symbols）*：列出文本文档中定义的所有符号。
> - *列出工作区符号（List Workspace Symbols）*：列出项目范围内的所有符号。
> - *代码操作（Code Actions）*：为给定的文本文档和范围，计算要运行的命令（通常是美化 / 重构）。
> - *CodeLens*：为给定的文本文档计算 CodeLens 统计信息。
> - *文档格式化（Document Formatting）*：包括整个文档的格式化、文档范围的格式化，以及输入时的格式化。
> - *重命名（Rename）*：在项目范围内重命名一个符号。
> - *文档链接（Document Links）*：计算并解析文档中的链接。
> - *文档颜色（Document Colors）*：计算并解析文档中的颜色，以在编辑器中提供颜色选择器。
>
> [编程式语言功能](./programmatic-language-features.md)主题描述了上面的每一个语言功能，并就如何通过语言服务器协议、或者直接在你的扩展中使用扩展 API 来实现它们给出了指导。

<a id="incremental-text-document-synchronization"></a>
### 增量文本文档同步（Incremental Text Document Synchronization）

> 这个示例使用 `vscode-languageserver` 模块提供的简单文本文档管理器，在 VS Code 和语言服务器之间同步文档。
>
> 这有两个缺点：
>
> - 由于文本文档的全部内容会被反复发送给服务器，传输的数据量很大。
> - 如果使用了一个现有的语言库，这些库通常支持增量的文档更新，以避免不必要的解析和抽象语法树的创建。
>
> 因此，协议也支持增量的文档同步。
>
> 要使用增量文档同步，服务器需要安装三个通知处理函数：
>
> - *onDidOpenTextDocument*：在 VS Code 中打开一个文本文档时调用。
> - *onDidChangeTextDocument*：在 VS Code 中文本文档的内容发生变化时调用。
> - *onDidCloseTextDocument*：在 VS Code 中关闭一个文本文档时调用。
>
> 下面的代码片段演示了如何在连接上挂接这些通知处理函数，以及如何在 initialize 时返回正确的能力：

```typescript
connection.onInitialize((params): InitializeResult => {
    ...
    return {
        capabilities: {
            // 启用增量文档同步
            textDocumentSync: TextDocumentSyncKind.Incremental,
            ...
        }
    };
});

connection.onDidOpenTextDocument((params) => {
    // 在 VS Code 中打开了一个文本文档。
    // params.uri 唯一地标识这个文档。对于存储在磁盘上的文档，这是一个 file URI。
    // params.text 是文档最初的完整内容。
});

connection.onDidChangeTextDocument((params) => {
    // 在 VS Code 中，一个文本文档的内容发生了变化。
    // params.uri 唯一地标识这个文档。
    // params.contentChanges 描述了文档内容的变化。
});

connection.onDidCloseTextDocument((params) => {
    // 在 VS Code 中关闭了一个文本文档。
    // params.uri 唯一地标识这个文档。
});

/*
让文本文档管理器在连接上监听文本文档的打开、修改和关闭事件。

注释掉这一行，才能让 `connection.onDidOpenTextDocument`、
`connection.onDidChangeTextDocument` 和 `connection.onDidCloseTextDocument` 处理这些事件
*/
// documents.listen(connection);
```

**这一节需要结合前面的代码来理解：**

- 这一节的描述有些过时。前面的示例代码已经设置了 `textDocumentSync: TextDocumentSyncKind.Incremental`，而 `TextDocuments` 管理器本身就支持增量同步（正如“解读语言服务器”一节所说，它“始终从 VS Code 向服务器发送增量变化”）。所以“全部内容被反复发送”这个缺点，只在使用 `TextDocumentSyncKind.Full` 时才存在。
- 这一节真正要说的是：如果你使用的语言库**自己**就能处理增量更新（比如它维护着自己的语法树，可以只重新解析变化的部分），那么可以不用 `TextDocuments` 管理器，直接处理三个通知，把 `contentChanges` 交给你的库。注意 `TextDocuments.listen` 和这三个处理函数**只能二选一**，所以示例中注释掉了 `documents.listen(connection)`。
- 代码注释中的参数写法不准确：在 LSP 中，打开通知的参数是 `params.textDocument.uri` 和 `params.textDocument.text`；修改和关闭通知中也是 `params.textDocument.uri`。

| `TextDocumentSyncKind` | 含义 |
|---|---|
| `None` | 不同步文档 |
| `Full` | 每次变化都发送文档的全部内容 |
| `Incremental` | 只发送变化的部分（`contentChanges` 中是若干个 `{ range, text }`） |

<a id="using-vs-code-api-directly-to-implement-language-features"></a>
### 直接使用 VS Code API 实现语言功能（Using VS Code API directly to implement Language Features）

> 虽然语言服务器有很多好处，但它们并不是扩展 VS Code 编辑能力的唯一选择。如果你只是想为某种文档添加一些简单的语言功能，可以考虑使用 `vscode.languages.register[LANGUAGE_FEATURE]Provider`。
>
> 这里有一个 [`completions-sample`](https://github.com/microsoft/vscode-extension-samples/tree/main/completions-sample)，它使用 `vscode.languages.registerCompletionItemProvider`，为纯文本文件添加了几个作为补全项的代码片段。
>
> 更多演示 VS Code API 用法的示例可以在 [https://github.com/microsoft/vscode-extension-samples](https://github.com/microsoft/vscode-extension-samples) 找到。

两种方式的选择见 [编程式语言功能](./programmatic-language-features.md) 开头的对比表。

<a id="error-tolerant-parser-for-language-server"></a>
### 语言服务器的容错解析器（Error Tolerant Parser for Language Server）

> 大多数时候，编辑器中的代码是不完整的、有语法错误的，但开发者仍然期望自动补全和其他语言功能能够工作。因此，容错解析器对语言服务器来说是必需的：解析器从部分完成的代码中生成有意义的 AST，语言服务器基于这个 AST 提供语言功能。
>
> 在改进 VS Code 中的 PHP 支持时，我们意识到官方的 PHP 解析器不是容错的，无法直接在语言服务器中复用。因此，我们开发了 [Microsoft/tolerant-php-parser](https://github.com/microsoft/tolerant-php-parser)，并留下了详细的[笔记](https://github.com/microsoft/tolerant-php-parser/blob/master/docs/HowItWorks.md)，可能会对需要实现容错解析器的语言服务器作者有所帮助。

**为什么“容错”这么重要？** 想想补全最常发生的时刻：用户刚输入了 `obj.`，这时这一行在语法上是不完整的。一个普通的编译器解析器遇到语法错误就会停止，给不出任何 AST，也就无从得知 `obj` 是什么类型。容错解析器会“跳过”错误的部分，尽量为其余的代码建立完整的语法树，并把不完整的地方标记出来。（这和 [语法高亮](./syntax-highlight-guide.md) 中 TextMate 语法要容忍未闭合的括号是同一个道理。）

---

<a id="common-questions"></a>
## 常见问题（Common questions）

<a id="when-i-try-to-attach-to-the-server-i-get-cannot-connect-to-runtime-process-timeout-after-5000-ms"></a>
### 我尝试附加到服务器时，出现了 "cannot connect to runtime process (timeout after 5000 ms)"？（When I try to attach to the server, I get "cannot connect to runtime process (timeout after 5000 ms)"?）

> 如果你尝试附加调试器时服务器没有在运行，就会看到这个超时错误。服务器是由客户端启动的，所以请确保你已经启动了客户端，这样服务器才会运行。如果客户端的断点干扰了服务器的启动，你可能还需要禁用它们。

错误信息的意思是“无法连接到运行时进程（5000 毫秒后超时）”。这适用于使用单独的“附加到服务器”配置的情况（旧版示例中有一个 **Attach to Server** 配置）。现在 lsp-sample 的 **Launch Client** 启用了 `autoAttachChildProcesses`，通常不需要再手动附加。“客户端断点的干扰”指的是：如果客户端停在 `client.start()` 之前的断点上，服务器进程还没有被启动，这时去附加自然会超时。

<a id="i-have-read-through-this-guide-and-the-lsp-specification-but-i-still-have-unresolved-questions-where-can-i-get-help"></a>
### 我已经读完了本指南和 [LSP 规范](https://microsoft.github.io/language-server-protocol/)，但仍有没解决的问题。我可以在哪里获得帮助？（I have read through this guide and the LSP Specification, but I still have unresolved questions. Where can I get help?）

> 请在 [https://github.com/microsoft/language-server-protocol](https://github.com/microsoft/language-server-protocol) 提交一个 issue。

---

## 本篇小结

```text
语言服务器扩展 = 语言客户端（普通扩展，vscode-languageclient）+ 语言服务器（独立进程，vscode-languageserver）
  好处：任意语言实现、不拖慢编辑器、一个服务器服务多个编辑器（M + N）

客户端（client/src/extension.ts）
  ServerOptions：run / debug，module + TransportKind.ipc（或 command 启动任意可执行文件）
  LanguageClientOptions：documentSelector、synchronize.fileEvents、middleware
  new LanguageClient(id, name, serverOptions, clientOptions) → await client.start()
  deactivate 中 await client.dispose()

服务器（server/src/server.ts）
  createConnection(ProposedFeatures.all) + new TextDocuments(TextDocument)
  onInitialize：读取客户端能力，返回服务器能力（textDocumentSync、completionProvider、diagnosticProvider……）
  onInitialized：动态注册（配置变化通知等）
  功能处理：languages.diagnostics.on（拉取诊断）、onCompletion / onCompletionResolve、onHover……
  设置：workspace.getConfiguration({ scopeUri, section }) 向客户端读取；变化后 diagnostics.refresh()
  documents.listen(connection); connection.listen();

开发
  构建 Ctrl+Shift+B → Launch Client（autoAttachChildProcesses 同时调试服务器）
  日志："<clientId>.trace.server": "verbose"，在输出面板查看每条 LSP 消息
  测试：端到端测试用 vscode.executeXxxProvider 命令 / getDiagnostics 断言

要点：服务器必须容错解析不完整的代码
```
