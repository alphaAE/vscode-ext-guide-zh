# 任务提供者（Task Provider）

> 原文：[Task Provider](https://code.visualstudio.com/api/extension-guides/task-provider)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/task-provider.md`（DateApproved: 10/7/2026）

> 用户通常在 `tasks.json` 文件中定义 VS Code 的[任务](https://code.visualstudio.com/docs/debugtest/tasks)。不过，软件开发过程中有些任务可以由 VS Code 扩展通过任务提供者（Task Provider）自动检测出来。当用户在 VS Code 中运行 **Tasks: Run Task** 命令时，所有活动的任务提供者都会贡献出用户可以运行的任务。`tasks.json` 文件让用户可以为特定的文件夹或工作区手动定义任务，而任务提供者则可以检测工作区的细节，然后自动创建对应的 VS Code 任务。例如，任务提供者可以检查是否存在特定的构建文件，比如 `make` 或 `Rakefile`，然后创建一个构建任务。本主题介绍扩展如何自动检测任务并提供给最终用户。
>
> 本指南教你构建一个任务提供者，自动检测 [Rakefile](https://ruby.github.io/rake/) 中定义的任务。完整的源代码在：[https://github.com/microsoft/vscode-extension-samples/tree/main/task-provider-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/task-provider-sample)。

**任务（Task）是什么？** 它是 VS Code 中“运行一条外部命令”的标准方式，比如编译、打包、运行测试。任务运行在集成终端中，可以配置快捷键，还能把命令输出中的错误解析成“问题”面板中的条目。

**任务提供者解决什么问题？** 不用让用户手写 `tasks.json`。比如 npm 内置扩展就是一个任务提供者：打开一个有 `package.json` 的项目，执行 **Tasks: Run Task**，就能直接看到 `npm: build`、`npm: test` 等任务，这些都是它根据 `package.json` 中的 `scripts` 自动生成的。

```text
用户执行 Tasks: Run Task
        ↓
VS Code 询问所有任务提供者：“你们能提供哪些任务？”
        ↓
npm 提供者：npm: build、npm: test ……   rake 提供者：rake: compile ……
        ↓
合并显示在列表中，用户选择一个运行
```

**Rake** 是 Ruby 生态中的构建工具，相当于 C 语言的 `make`，任务写在名为 `Rakefile` 的文件中。本篇以它为例，换成其他构建工具，思路完全一样。

---

<a id="task-definition"></a>
## 任务定义（Task Definition）

> 为了在系统中唯一地标识一个任务，贡献任务的扩展需要定义能够标识任务的属性。在 Rake 示例中，任务定义是这样的：

```json
"taskDefinitions": [
    {
        "type": "rake",
        "required": [
            "task"
        ],
        "properties": {
            "task": {
                "type": "string",
                "description": "The Rake task to customize"
            },
            "file": {
                "type": "string",
                "description": "The Rake file that provides the task. Can be omitted."
            }
        }
    }
]
```

（这段配置写在 `package.json` 的 `contributes` 下。）

> 这为 `rake` 任务贡献了一个任务定义。这个任务定义有两个属性：`task` 和 `file`。`task` 是 Rake 任务的名称，`file` 指向包含这个任务的 `Rakefile`。`task` 属性是必需的，`file` 属性是可选的。如果省略了 `file` 属性，就使用工作区文件夹根目录下的 `Rakefile`。

**任务定义有什么用？** 它规定了“一个 rake 任务由哪些信息唯一确定”。这些信息有两个用途：

1. 用户可以在 `tasks.json` 中引用、定制你提供的任务。写法就是按照这个定义来写，VS Code 还会根据 `properties` 提供补全和校验：

    ```json
    // .vscode/tasks.json
    {
      "version": "2.0.0",
      "tasks": [
        {
          "type": "rake",              // 对应 taskDefinitions 中的 type
          "task": "compile",           // 必需属性
          "group": "build",            // 用户追加的定制：设为默认构建任务
          "problemMatcher": []
        }
      ]
    }
    ```

2. VS Code 用这些属性判断“`tasks.json` 中的这个任务”和“提供者提供的那个任务”是不是同一个。

`properties` 的写法就是 JSON Schema，和 `contributes.configuration` 中定义设置项的写法相同。

<a id="when-clause"></a>
### When 子句（When clause）

> 任务定义可以有一个可选的 `when` 属性。`when` 属性指定了在什么条件下这种类型的任务可用。`when` 属性的作用方式与 [VS Code 中其他有 `when` 属性的地方](../references/when-clause-contexts.md)相同。创建任务定义时，始终应该考虑以下上下文：

| 上下文键 | 何时为 true |
|---|---|
| `shellExecutionSupported` | VS Code 能够运行 `ShellExecution` 任务时，例如 VS Code 作为桌面应用运行，或者使用 Dev Containers 等远程扩展时 |
| `processExecutionSupported` | VS Code 能够运行 `ProcessExecution` 任务时，例如 VS Code 作为桌面应用运行，或者使用 Dev Containers 等远程扩展时。目前它的值始终与 `shellExecutionSupported` 相同 |
| `customExecutionSupported` | VS Code 能够运行 `CustomExecution` 时。这个值始终为 true |

**为什么要考虑这些？** 在浏览器中使用的 VS Code（如 vscode.dev）中，没有可以运行命令的系统 shell，`ShellExecution` 任务根本跑不起来。如果你的任务依赖 shell，就应该加上条件，在这类环境中不显示：

```json
"taskDefinitions": [
  {
    "type": "rake",
    "when": "shellExecutionSupported",
    "required": ["task"],
    "properties": { ... }
  }
]
```

三种执行方式（`ShellExecution`、`ProcessExecution`、`CustomExecution`）的区别见下文。

---

<a id="task-provider"></a>
## 任务提供者（Task provider）

> 类似于让扩展支持代码补全的语言提供者，扩展可以注册一个任务提供者，来计算所有可用的任务。这是通过 `vscode.tasks` 命名空间完成的，如下面的代码片段所示：

```ts
import * as vscode from 'vscode';

let rakePromise: Thenable<vscode.Task[]> | undefined = undefined;
const taskProvider = vscode.tasks.registerTaskProvider('rake', {
  provideTasks: () => {
    if (!rakePromise) {
      rakePromise = getRakeTasks();
    }
    return rakePromise;
  },
  resolveTask(_task: vscode.Task): vscode.Task | undefined {
		const task = _task.definition.task;
		// Rake 任务由一个 task 和一个可选的 file 组成，如 RakeTaskDefinition 中所规定。
		// 检查是否有 task，确认这看起来是一个 Rake 任务。
		if (task) {
			// resolveTask 要求使用同一个 definition 对象。
			const definition: RakeTaskDefinition = <any>_task.definition;
			return new vscode.Task(definition, _task.scope ?? vscode.TaskScope.Workspace, definition.task, 'rake', new vscode.ShellExecution(`rake ${definition.task}`));
		}
		return undefined;  }
});
```

`registerTaskProvider` 的第一个参数 `'rake'` 必须和 `taskDefinitions` 中的 `type` 一致。

示例中的 `rakePromise` 是一个**缓存**：第一次调用 `provideTasks` 时执行 `getRakeTasks()`（要运行 `rake` 命令，比较慢），之后直接返回同一个结果。完整的示例中，还会监听 `Rakefile` 的变化，文件改了就把 `rakePromise` 清空，下次重新获取。

> 和 `provideTasks` 一样，`resolveTask` 方法也由 VS Code 调用，用来从扩展获取任务。`resolveTask` 可以代替 `provideTasks` 被调用，它的目的是为实现了它的提供者带来可选的性能提升。例如，如果用户有一个运行扩展所提供任务的快捷键，那么 VS Code 最好是为这个任务调用该任务提供者的 `resolveTask`，快速地只获取这一个任务，而不是调用 `provideTasks` 并等待扩展提供它的全部任务。提供一个让用户关闭单个任务提供者的设置是一种好的做法，所以这种情况很常见。用户可能会注意到某个提供者的任务获取得比较慢，于是关闭了这个提供者。在这种情况下，用户可能仍然在他们的 `tasks.json` 中引用了这个提供者的一些任务。如果没有实现 `resolveTask`，就会出现一条警告，提示 `tasks.json` 中的任务没有被创建。有了 `resolveTask`，扩展仍然可以为 `tasks.json` 中定义的任务提供任务。

两个方法的区别：

| 方法 | 何时调用 | 输入 | 输出 |
|---|---|---|---|
| `provideTasks` | 用户打开 **Tasks: Run Task** 列表等，需要“全部任务”时 | 无 | 所有能检测到的任务 |
| `resolveTask` | 只需要“某一个任务”时，比如通过快捷键或 `tasks.json` 运行某个任务 | `tasks.json` 中的一个任务（只有定义，没有执行方式） | 补全了执行方式（`execution`）的任务 |

`resolveTask` 的关键作用是：`tasks.json` 中的任务只写了 `{ "type": "rake", "task": "compile" }`，并没有说具体要执行什么命令，**由 `resolveTask` 根据定义补上“执行 `rake compile`”**。

“resolveTask 要求使用同一个 definition 对象”是指：返回的新任务必须使用传入任务的 `_task.definition`，不能自己新建一个定义对象，否则 VS Code 无法把它和 `tasks.json` 中的那个任务对应起来。

> `getRakeTasks` 的实现做了以下事情：
>
> - 对每个工作区文件夹，使用 `rake -AT -f Rakefile` 命令列出 `Rakefile` 中定义的所有 rake 任务。
> - 解析标准输出的内容。
> - 为列出的每个任务创建一个 `vscode.Task` 实现。
>
> 由于实例化一个 Rake 任务需要一个与 `package.json` 文件中定义一致的任务定义，VS Code 还用一个 TypeScript 接口定义了它的结构，像这样：

```typescript
interface RakeTaskDefinition extends vscode.TaskDefinition {
  /**
   * 任务名称
   */
  task: string;

  /**
   * 包含该任务的 rake 文件
   */
  file?: string;
}
```

（原文说“VS Code 还用一个 TypeScript 接口定义了它的结构”，实际上这个接口是**扩展作者自己**写的，让代码中的定义对象有类型提示，结构与 `package.json` 中的 `taskDefinitions` 保持一致。`vscode.TaskDefinition` 本身只规定了必须有一个 `type` 字段。）

> 假设输出来自第一个工作区文件夹中一个名为 `compile` 的任务，对应的任务创建代码是这样的：

```typescript
let task = new vscode.Task(
  { type: 'rake', task: 'compile' },
  vscode.workspace.workspaceFolders[0],
  'compile',
  'rake',
  new vscode.ShellExecution('rake compile')
);
```

`new vscode.Task(...)` 的参数：

| 参数 | 示例中的值 | 说明 |
|---|---|---|
| `taskDefinition` | `{ type: 'rake', task: 'compile' }` | 任务定义，结构与 `taskDefinitions` 一致 |
| `scope` | `workspaceFolders[0]` | 任务属于哪个工作区文件夹；也可以是 `TaskScope.Workspace`（整个工作区）或 `TaskScope.Global` |
| `name` | `'compile'` | 任务名称 |
| `source` | `'rake'` | 任务的来源，在列表中显示为 `rake: compile` |
| `execution` | `new ShellExecution('rake compile')` | 任务具体如何执行 |
| `problemMatchers`（可选） | 如 `'$tsc'` | 用哪个问题匹配器把输出中的错误解析到“问题”面板 |

> 对于输出中列出的每个任务，都按照上面的模式创建一个对应的 VS Code 任务，然后从 `getRakeTasks` 调用中返回所有任务组成的数组。
>
> `ShellExecution` 会在特定于操作系统的 shell 中执行 `rake compile` 命令（例如在 Windows 下，命令会在 PowerShell 中执行；在 Ubuntu 下，会在 bash 中执行）。如果任务应该直接执行一个进程（不启动 shell），可以使用 `vscode.ProcessExecution`。`ProcessExecution` 的优势是扩展可以完全控制传给进程的参数。使用 `ShellExecution` 则会利用 shell 对命令的解释（比如 bash 中的通配符展开）。如果 `ShellExecution` 是用单个命令行创建的，扩展就需要确保命令中正确地使用了引号和转义（例如处理空格）。

**`ShellExecution` 和 `ProcessExecution` 的区别：**

| | `ShellExecution` | `ProcessExecution` |
|---|---|---|
| 执行方式 | 启动一个 shell（PowerShell、bash……），由 shell 解释并执行命令 | 直接启动程序，不经过 shell |
| 写法 | `new ShellExecution('rake compile')` | `new ProcessExecution('rake', ['compile'])` |
| shell 特性 | 能用：通配符 `*.txt`、管道 `\|`、环境变量 `$HOME` | 不能用 |
| 参数中的空格、特殊字符 | 要自己处理引号和转义（不同 shell 的规则不一样） | 不用处理，参数数组原样传给程序 |

举个例子说明“引号和转义”的问题：如果文件路径是 `C:\My Project\Rakefile`（中间有空格），`new ShellExecution('rake -f C:\My Project\Rakefile')` 会被 shell 拆成两个参数而出错。可以改用 `ShellExecution` 的另一种构造方式，把命令和参数分开传，由 VS Code 负责加引号：

```ts
new vscode.ShellExecution('rake', ['-f', 'C:\\My Project\\Rakefile', 'compile']);
```

---

<a id="CustomExecution"></a>
## CustomExecution

> 一般来说，最好使用 `ShellExecution` 或 `ProcessExecution`，因为它们很简单。不过，如果你的任务需要在多次运行之间保存大量状态，不适合作为单独的脚本或进程运行，或者需要大量处理输出，那么 `CustomExecution` 可能会很合适。`CustomExecution` 的现有用途通常是复杂的构建系统。`CustomExecution` 只有一个回调函数，在任务运行时执行。这让任务能做的事情更加灵活，但也意味着任务提供者要负责所有需要进行的进程管理和输出解析。任务提供者还负责实现 `Pseudoterminal`，并从 `CustomExecution` 的回调中返回它。

```typescript
return new vscode.Task(definition, vscode.TaskScope.Workspace, `${flavor} ${flags.join(' ')}`,
  CustomBuildTaskProvider.CustomBuildScriptType, new vscode.CustomExecution(async (): Promise<vscode.Pseudoterminal> => {
    // 任务执行时，会运行这个回调。在这里为运行任务做准备。
    return new CustomBuildTaskTerminal(this.workspaceRoot, flavor, flags, () => this.sharedState, (state: string) => this.sharedState = state);
  }));
```

> 包括 `Pseudoterminal` 实现在内的完整示例，在 [https://github.com/microsoft/vscode-extension-samples/tree/main/task-provider-sample/src/customTaskProvider.ts](https://github.com/microsoft/vscode-extension-samples/tree/main/task-provider-sample/src/customTaskProvider.ts)。

**`CustomExecution` 是什么？** 前两种执行方式都是“运行一个外部命令”，而 `CustomExecution` 是“**用扩展自己的代码来完成任务**”。任务运行时，VS Code 调用你的回调，你返回一个 `Pseudoterminal`（伪终端），然后在 TypeScript 代码里做任何事，再把输出写到这个伪终端中显示给用户。

**`Pseudoterminal`（伪终端）** 是一个由扩展控制的“假”终端：它看起来和普通终端一样，但背后没有真正的 shell 进程，显示什么内容、何时结束，都由你的代码决定。实现它最少需要这几个成员：

```ts
class MyTaskTerminal implements vscode.Pseudoterminal {
  private writeEmitter = new vscode.EventEmitter<string>();
  onDidWrite = this.writeEmitter.event;        // 通过它向终端输出文字

  private closeEmitter = new vscode.EventEmitter<number>();
  onDidClose = this.closeEmitter.event;        // 通过它结束任务，参数是退出码

  open(): void {
    // 终端打开时调用：在这里开始执行任务
    this.writeEmitter.fire('开始构建……\r\n');   // 终端中换行要写 \r\n
    // ……用扩展代码完成任务……
    this.closeEmitter.fire(0);                 // 0 表示成功
  }

  close(): void {
    // 用户关闭终端或终止任务时调用：在这里中止正在进行的工作
  }
}
```

示例中 `CustomBuildTaskTerminal` 构造函数的最后两个参数（`() => this.sharedState` 和 `(state) => this.sharedState = state`），正是原文所说的“在多次运行之间保存状态”：任务提供者持有一个 `sharedState`，每次任务运行时读取上一次的状态，结束时写回新的状态（比如记录上次构建的时间，实现增量构建）。

**三种执行方式怎么选：**

| 方式 | 适合 | 运行环境限制 |
|---|---|---|
| `ShellExecution` | 大多数情况：运行一条命令行 | 需要 shell（`shellExecutionSupported`） |
| `ProcessExecution` | 直接运行一个程序，参数复杂或含特殊字符 | 需要能启动进程（`processExecutionSupported`） |
| `CustomExecution` | 任务逻辑本身就是扩展代码；需要保存状态；输出需要大量加工 | 任何环境都可以（`customExecutionSupported` 始终为 true） |

---

## 本篇小结

```text
package.json：contributes.taskDefinitions
  type（任务类型）、required、properties（JSON Schema）、when（如 shellExecutionSupported）

代码：tasks.registerTaskProvider(type, { provideTasks, resolveTask })
  provideTasks：检测并返回所有任务（建议缓存，耗时）
  resolveTask：给 tasks.json 中的任务补上执行方式（必须使用传入的 definition 对象）

new Task(definition, scope, name, source, execution, problemMatchers?)
  execution：
    ShellExecution   —— 经过 shell，注意引号和转义（可分开传命令和参数）
    ProcessExecution —— 直接运行程序，参数原样传递
    CustomExecution  —— 扩展代码完成任务，返回 Pseudoterminal（onDidWrite / onDidClose / open / close）
```
