# 测试 API（Testing API）

> 原文：[Testing API](https://code.visualstudio.com/api/extension-guides/testing)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/testing.md`（DateApproved: 10/7/2026）

> 测试 API 让 VS Code 扩展可以发现工作区中的测试并发布测试结果。用户可以在测试资源管理器（Test Explorer）视图中、通过装饰，以及在命令中执行测试。借助这些新的 API，VS Code 能够比以前更丰富地显示输出和差异。
>
> **注意**：测试 API 在 VS Code 1.59 及更高版本中可用。

**这套 API 是做什么的？** 把某个测试框架（比如 Jest、pytest、JUnit）接入 VS Code 的统一测试界面：

- 活动栏中的“测试”视图：以树形列表显示所有测试，可以一键运行、调试；
- 编辑器中测试代码旁边的 ▶ 按钮（“装饰”），点击即可运行这一个测试；
- 运行后显示 ✓ / ✗，失败的测试可以直接查看错误信息和期望值 / 实际值的差异。

注意区分：本篇讲的是**为别人的代码提供测试功能**的扩展；如果是要**测试你自己写的扩展**，请看 [测试扩展](../working-with-extensions/testing-extension.md)。

---

<a id="examples"></a>
## 示例（Examples）

> VS Code 团队维护着两个测试提供者：
>
> - [示例测试扩展](https://github.com/microsoft/vscode-extension-samples/tree/main/test-provider-sample)，它在 Markdown 文件中提供测试。
> - [selfhost 测试扩展](https://github.com/microsoft/vscode-selfhost-test-provider)，我们用它来运行 VS Code 自身的测试。

示例测试扩展把 Markdown 文件中形如 `1 + 2 = 3` 的行当作“测试用例”：运行时计算左边的表达式，看结果是否等于右边。本篇的代码大多来自这个示例。

---

<a id="discovering-tests"></a>
## 发现测试（Discovering tests）

> 测试由 `TestController` 提供，创建它需要一个全局唯一的 ID 和一个人类可读的标签：

```ts
const controller = vscode.tests.createTestController('helloWorldTests', 'Hello World Tests');
```

> 要发布测试，就把 `TestItem` 作为子项添加到控制器的 `items` 集合中。`TestItem` 是测试 API 中 `TestItem` 接口的基础，它是一种通用类型，可以描述代码中存在的测试用例、测试套件或树节点。它们自身也可以有 `children`（子项），从而形成一个层级结构。例如，下面是示例测试扩展创建测试的简化版本：

```ts
parseMarkdown(content, {
  onTest: (range, numberA, mathOperator, numberB, expectedValue) => {
    // 如果这是一个顶层测试，就把它添加到父项的子项中。否则，
    // 添加到控制器的顶层项中。
    const collection = parent ? parent.children : controller.items;
    // 创建一个在父项的子项中唯一的新 ID：
    const id = [numberA, mathOperator, numberB, expectedValue].join('  ');

    // 最后，创建测试项：
    const test = controller.createTestItem(id, data.getLabel(), item.uri);
    test.range = range;
    collection.add(test);
  },
  // ...
});
```

（这段代码是从示例中截取的片段，`parent`、`data`、`item` 等变量来自上下文，这里没有展示定义。另外，第一行注释的意思和代码相反，按代码的逻辑应该是：“如果有父项，就加到父项的子项中；否则加到控制器的顶层项中”。）

**测试树的结构：**

```text
controller.items（顶层）
  ├─ TestItem：math.md（文件）
  │     ├─ TestItem：1 + 2 = 3（测试用例）
  │     └─ TestItem：2 * 3 = 6
  └─ TestItem：other.md
        └─ ……
```

`createTestItem(id, label, uri?)` 的参数：

| 参数 | 说明 |
|---|---|
| `id` | 在**同一个父项的子项中**唯一即可（不需要全局唯一） |
| `label` | 在测试视图中显示的名称 |
| `uri`（可选） | 测试所在的文件。设置后，点击测试可以跳转到文件 |

创建之后还常设置 `test.range`（测试在文件中的位置），这样编辑器中该行旁边就会出现 ▶ 运行按钮。

> 和诊断（Diagnostics）类似，什么时候发现测试，主要由扩展自己控制。一个简单的扩展可能会监视整个工作区，在激活时解析所有文件中的所有测试。但是，对于大型工作区，立即解析所有内容可能会很慢。你可以改为做两件事：
>
> 1. 通过监听 `vscode.workspace.onDidOpenTextDocument`，在文件在编辑器中被打开时，主动发现这个文件中的测试。
> 2. 设置 `item.canResolveChildren = true`，并设置 `controller.resolveHandler`。如果用户执行了需要发现测试的操作，比如在测试资源管理器中展开某一项，就会调用 `resolveHandler`。

这和 [树视图](./tree-view.md) 中“用户展开到哪里，就加载到哪里”的懒加载思路一样。

> 下面是在一个懒解析文件的扩展中，这种策略可能的样子：

```ts
// 首先，创建 `resolveHandler`。一开始可能会用 "undefined" 调用它，
// 要求发现工作区中的所有测试，通常发生在用户第一次打开测试资源管理器时。
controller.resolveHandler = async test => {
  if (!test) {
    await discoverAllFilesInWorkspace();
  } else {
    await parseTestsInFileContents(test);
  }
};

// 文本文档被打开时，解析其中的测试。
vscode.workspace.onDidOpenTextDocument(parseTestsInDocument);
// 也可以监听文档的修改，重新解析未保存的修改：
vscode.workspace.onDidChangeTextDocument(e => parseTestsInDocument(e.document));

// 在这个函数中，如果已经找到过文件对应的 TestItem，就直接返回它；
// 否则用 `canResolveChildren = true` 创建它，表示可以把它传给
// `controller.resolveHandler` 来获取它的子项。
function getOrCreateFile(uri: vscode.Uri) {
  const existing = controller.items.get(uri.toString());
  if (existing) {
    return existing;
  }

  const file = controller.createTestItem(uri.toString(), uri.path.split('/').pop()!, uri);
  file.canResolveChildren = true;
  return file;
}

function parseTestsInDocument(e: vscode.TextDocument) {
  if (e.uri.scheme === 'file' && e.uri.path.endsWith('.md')) {
    parseTestsInFileContents(getOrCreateFile(e.uri), e.getText());
  }
}

async function parseTestsInFileContents(file: vscode.TestItem, contents?: string) {
  // 如果文档是打开的，VS Code 已经知道它的内容了。如果这是在文档没有打开时
  // 从 resolveHandler 调用的，我们就需要自己从磁盘读取内容。
  if (contents === undefined) {
    const rawContent = await vscode.workspace.fs.readFile(file.uri);
    contents = new TextDecoder().decode(rawContent);
  }

  // 一些自定义的逻辑，根据内容填充 test.children……
}
```

**原文代码中需要补上的一处：** `getOrCreateFile` 创建了新的文件节点，但没有把它添加到 `controller.items` 中，所以它不会出现在测试视图里，下次调用 `controller.items.get(...)` 也找不到它。应该在 `return file` 之前加上一行：

```ts
  controller.items.add(file);
```

另外，示例中 `onDidOpenTextDocument` 等事件订阅返回的 Disposable，实际代码中应该放进 `context.subscriptions`。`parseTestsInDocument` 中先检查了 `e.uri.scheme === 'file'`，这正是 [虚拟文档](./virtual-documents.md#events-and-visibility) 中强调的“处理文档事件前先检查 scheme”。

**`resolveHandler` 的两种调用：**

| 调用方式 | 何时发生 | 应该做什么 |
|---|---|---|
| `resolveHandler(undefined)` | 用户第一次打开测试视图时 | 找出工作区中所有可能包含测试的文件（只建立文件节点，不必解析内容） |
| `resolveHandler(某个 TestItem)` | 用户展开某个 `canResolveChildren = true` 的节点时 | 解析这个节点，填充它的子项 |

> `discoverAllFilesInWorkspace` 的实现，可以基于 VS Code 现有的文件监视功能来构建。调用 `resolveHandler` 之后，你应该继续监视文件的变化，让测试资源管理器中的数据保持最新。

```ts
async function discoverAllFilesInWorkspace() {
  if (!vscode.workspace.workspaceFolders) {
    return []; // 处理没有打开文件夹的情况
  }

  return Promise.all(vscode.workspace.workspaceFolders.map(async workspaceFolder => {
    const pattern = new vscode.RelativePattern(workspaceFolder, '**/*.md');
    const watcher = vscode.workspace.createFileSystemWatcher(pattern);

    // 文件被创建时，确保树中有一个对应的“文件”节点
    watcher.onDidCreate(uri => getOrCreateFile(uri));
    // 文件被修改时，重新解析它。注意，你可以优化这一点，
    // 只重新解析之前已经被解析过的子项。
    watcher.onDidChange(uri => parseTestsInFileContents(getOrCreateFile(uri)));
    // 最后，删除已被移除的文件对应的 TestItem。这很简单，
    // 因为我们用 URI 作为 TestItem 的 ID。
    watcher.onDidDelete(uri => controller.items.delete(uri.toString()));

    for (const file of await vscode.workspace.findFiles(pattern)) {
      getOrCreateFile(file);
    }

    return watcher;
  }));
}
```

- `RelativePattern(文件夹, '**/*.md')`：相对于某个工作区文件夹的 glob 模式。多根工作区中要对每个文件夹分别处理，所以用了 `map`。
- `createFileSystemWatcher`：监视匹配的文件的创建、修改、删除。返回的 `watcher` 是 Disposable，不再需要时要释放。
- `findFiles`：一次性找出当前所有匹配的文件。
- 用 URI 作为文件节点的 ID 是个好办法：删除文件时，直接用 URI 就能找到对应的节点。

> `TestItem` 接口很简单，没有存放自定义数据的地方。如果你需要把额外的信息与一个 `TestItem` 关联起来，可以使用 [`WeakMap`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/WeakMap)：

```ts
const testData = new WeakMap<vscode.TestItem, MyCustomData>();

// 关联数据：
const item = controller.createTestItem(id, label);
testData.set(item, new MyCustomData());

// 之后再取回来：
const myData = testData.get(item);
```

> VS Code 保证，传给所有与 `TestController` 相关的方法的 `TestItem` 实例，都与最初通过 `createTestItem` 创建的那些实例是同一个，所以你可以确信，从 `testData` 映射中获取测试项是可行的。

**为什么用 `WeakMap` 而不是 `Map`？** `WeakMap` 对键是“弱引用”：当某个 `TestItem` 从测试树中删除、没有其他地方再引用它时，它会被垃圾回收，`WeakMap` 中对应的数据也会自动消失。用普通的 `Map` 就要自己记得删除，否则会造成内存泄漏。

> 在这个示例中，我们只存储每个测试项的类型：

```ts
enum ItemType {
  File,
  TestCase,
}

const testData = new WeakMap<vscode.TestItem, ItemType>();

const getType = (testItem: vscode.TestItem) => testData.get(testItem)!;
```

---

<a id="running-tests"></a>
## 运行测试（Running tests）

> 测试通过 `TestRunProfile`（测试运行配置）执行。每个配置都属于一种特定的执行 `kind`（类型）：运行、调试或覆盖率。大多数测试扩展在每一类中最多只有一个配置，但也允许有更多。例如，如果你的扩展在多个平台上运行测试，你可以为平台和 `kind` 的每一种组合都创建一个配置。每个配置都有一个 `runHandler`，请求该类型的运行时就会调用它。

```ts

function runHandler(shouldDebug: boolean, request: vscode.TestRunRequest, token: vscode.CancellationToken) {
  // todo
}

const runProfile = controller.createRunProfile('Run', vscode.TestRunProfileKind.Run, (request, token) => {
  runHandler(false, request, token);
});

const debugProfile = controller.createRunProfile('Debug', vscode.TestRunProfileKind.Debug, (request, token) => {
  runHandler(true, request, token);
});
```

三种 `TestRunProfileKind`：

| 类型 | 对应界面上的按钮 | 作用 |
|---|---|---|
| `Run` | ▶ 运行测试 | 普通运行 |
| `Debug` | 🐞 调试测试 | 以调试模式运行，可以在测试代码中打断点 |
| `Coverage` | 带覆盖率运行 | 运行并收集代码覆盖率 |

没有创建某一类配置，界面上就不会出现对应的按钮。`createRunProfile` 还有几个可选参数：`isDefault`（是否作为这一类的默认配置）、`tag`（见下文[测试标签](#test-tags)）、`supportsContinuousRun`（是否支持“文件变化后自动重新运行”）。

> `runHandler` 应该至少调用一次 `controller.createTestRun`，并传入原始的请求。请求中包含了要 `include`（包含）在本次测试运行中的测试（如果用户要求运行所有测试，则省略此项），可能还有要从运行中 `exclude`（排除）的测试。扩展应该使用得到的 `TestRun` 对象，更新本次运行涉及的测试的状态。例如：

```ts
async function runHandler(shouldDebug: boolean, request: vscode.TestRunRequest, token: vscode.CancellationToken) {
  const run = controller.createTestRun(request);
  const queue: vscode.TestItem[] = [];

  // 遍历所有被包含的测试，或者所有已知的测试，把它们加入队列
  if (request.include) {
    request.include.forEach(test => queue.push(test));
  } else {
    controller.items.forEach(test => queue.push(test));
  }

  // 对于队列中的每个测试，尝试运行它。调用 run.passed() 或 run.failed()。
  // `TestMessage` 可以包含额外的信息，比如失败的位置或者差异输出。
  // 但这里我们只给它一条文字消息。
  while (queue.length > 0 && !token.isCancellationRequested) {
    const test = queue.pop()!;

    // 跳过用户要求排除的测试
    if (request.exclude?.includes(test)) {
      continue;
    }

    switch (getType(test)) {
      case ItemType.File:
        // 如果运行的是一个文件，而我们还不知道它包含什么，就现在解析它
        if (test.children.size === 0) {
          await parseTestsInFileContents(test);
        }
        break;
      case ItemType.TestCase:
        // 否则，直接运行这个测试用例。注意，我们不需要手动设置
        // 父测试的状态，它们会被自动设置。
        const start = Date.now();
        try {
          await assertTestPasses(test);
          run.passed(test, Date.now() - start);
        } catch (e) {
          run.failed(test, new vscode.TestMessage(e.message), Date.now() - start);
        }
        break;
    }

    test.children.forEach(test => queue.push(test));
  }

  // 所有测试执行完之后，一定要结束这次运行：
  run.end();
}
```

**运行测试的流程：**

```text
1. createTestRun(request)        创建一次“测试运行”
2. 确定要运行哪些测试：request.include（没有则为全部）减去 request.exclude
3. 逐个运行，更新状态：
     run.enqueued(test)  排队中        run.started(test)  运行中
     run.passed(test, 耗时)  通过      run.failed(test, 消息, 耗时)  失败（断言不成立）
     run.errored(test, 消息)  出错（测试本身无法运行）   run.skipped(test)  跳过
4. run.end()                     结束运行（不调用的话，界面会一直显示“正在运行”）
```

几点说明：

- **`failed` 和 `errored` 的区别**：`failed` 表示测试运行了但结果不对（比如期望 3 得到 4）；`errored` 表示测试根本没能正常运行（比如语法错误、找不到文件）。
- **父节点的状态会自动计算**：所有子测试都通过，文件节点就显示通过；有一个失败，文件节点就显示失败。
- **检查 `token.isCancellationRequested`**：用户点击“停止”时，这个值会变为 `true`，应该尽快停止运行。
- `assertTestPasses` 是示例中假设的函数，代表“实际执行这个测试”的逻辑。
- 在开启了严格模式的 TypeScript 中，`catch (e)` 的 `e` 是 `unknown` 类型，`e.message` 会报错，要写成 `(e as Error).message`。

**显示期望值与实际值的差异：** 测试失败时，如果能告诉 VS Code 期望值和实际值，界面上就会显示一个差异对比：

```ts
const message = vscode.TestMessage.diff(`期望 ${expected}，实际为 ${actual}`, String(expected), String(actual));
message.location = new vscode.Location(test.uri!, test.range!);   // 在编辑器的这个位置显示错误
run.failed(test, message, duration);
```

> 除了 `runHandler`，你还可以在 `TestRunProfile` 上设置一个 `configureHandler`。如果设置了它，VS Code 会提供界面让用户配置测试运行，并在用户进行配置时调用这个处理函数。在这里，你可以打开文件、显示一个快速选择，或者做任何适合你的测试框架的事情。

> VS Code 有意以不同于调试配置或任务配置的方式来处理测试配置。调试和任务传统上是以编辑器或 IDE 为中心的功能，它们在 `.vscode` 文件夹中的特殊文件里进行配置。然而，测试传统上是在命令行中执行的，而大多数测试框架都已经有了自己的配置方式。因此，在 VS Code 中，我们避免重复配置，而是交给扩展来处理。

也就是说，VS Code 不会像 `launch.json`、`tasks.json` 那样提供一个 `tests.json`。测试框架的配置还是用它自己的方式（比如 `jest.config.js`、`pytest.ini`），扩展负责读取这些配置。`configureHandler` 只是给用户一个调整配置的入口。

<a id="test-output"></a>
### 测试输出（Test Output）

> 除了传给 `TestRun.failed` 或 `TestRun.errored` 的消息之外，你还可以用 `run.appendOutput(str)` 追加一般的输出。这些输出可以通过 **Test: Show Output** 命令在终端中显示，也可以通过界面中的各种按钮显示，比如测试资源管理器视图中的终端图标。
>
> 因为这个字符串是在终端中渲染的，所以你可以使用完整的 [ANSI 转义码](https://en.wikipedia.org/wiki/ANSI_escape_code)，包括 [ansi-styles](https://www.npmjs.com/package/ansi-styles) npm 包中提供的样式。请记住，因为是在终端中，所以换行必须使用 CRLF（`\r\n`），而不仅仅是 LF（`\n`），而有些工具默认输出的可能是 LF。

**ANSI 转义码**是终端中控制文字颜色、粗细等样式的特殊字符序列。例如：

```ts
run.appendOutput('\x1b[32m✓ 通过\x1b[0m\r\n');   // \x1b[32m 开始绿色，\x1b[0m 恢复默认
run.appendOutput('\x1b[31m✗ 失败\x1b[0m\r\n');   // 红色
```

`appendOutput` 还有两个可选参数 `location` 和 `test`，可以把这段输出关联到某个测试或某个代码位置。

把测试框架的输出转发给 `appendOutput` 时，记得把 `\n` 替换成 `\r\n`，否则每一行会从上一行的末尾位置开始，显示成“阶梯状”。

<a id="test-coverage"></a>
### 测试覆盖率（Test Coverage）

> 测试覆盖率通过 `run.addCoverage()` 方法与 `TestRun` 关联。按照规范，这应该由 `TestRunProfileKind.Coverage` 类型配置的 `runHandler` 来完成，但在任何测试运行中调用它都是可以的。`addCoverage` 方法接收一个 `FileCoverage` 对象，它是这个文件中覆盖率数据的摘要：

```ts
async function runHandler(shouldDebug: boolean, request: vscode.TestRunRequest, token: vscode.CancellationToken) {
  // ...

  for await (const file of readCoverageOutput()) {
    run.addCoverage(new vscode.FileCoverage(file.uri, file.statementCoverage))
  }
}
```

**代码覆盖率**是指测试运行时，源代码中有多少被执行到了。比如一个函数有 10 行，测试只执行到了其中 7 行，行覆盖率就是 70%。VS Code 会在编辑器中用颜色标出哪些行被覆盖了、哪些没有。

> `FileCoverage` 包含了每个文件中语句、分支和声明的总体覆盖数和未覆盖数。根据你的运行时和覆盖率格式的不同，你可能会看到语句覆盖率被称为行覆盖率，声明覆盖率被称为函数覆盖率或方法覆盖率。你可以为同一个 URI 多次添加文件覆盖率，这种情况下，新的信息会替换旧的信息。

| 覆盖率类型 | 也叫 | 统计什么 |
|---|---|---|
| 语句覆盖率（statement） | 行覆盖率 | 有多少条语句被执行了 |
| 分支覆盖率（branch） | — | `if` / `else` 等分支中，有多少条分支被走到了 |
| 声明覆盖率（declaration） | 函数覆盖率、方法覆盖率 | 有多少个函数被调用了 |

示例中的 `readCoverageOutput` 是假设的函数，代表“读取测试框架生成的覆盖率报告”。`file.statementCoverage` 应该是一个 `TestCoverageCount`（形如 `{ covered: 已覆盖数, total: 总数 }`）。

> 当用户打开一个有覆盖率的文件，或者在**测试覆盖率**视图中展开一个文件时，VS Code 会请求这个文件的更多信息。它通过调用扩展在 `TestRunProfile` 上定义的 `loadDetailedCoverage` 方法来实现，并传入 `TestRun`、`FileCoverage` 和一个 `CancellationToken`。注意，测试运行和文件覆盖率的实例，与 `run.addCoverage` 中使用的是同一个，这对于关联数据很有用。例如，你可以创建一个从 `FileCoverage` 对象到你自己的数据的映射：

```ts
const coverageData = new WeakMap<vscode.FileCoverage, MyCoverageDetails>();

profile.loadDetailedCoverage = (testRun, fileCoverage, token) => {
  return coverageData.get(fileCoverage).load(token);
}

async function runHandler(shouldDebug: boolean, request: vscode.TestRunRequest, token: vscode.CancellationToken) {
  // ...

  for await (const file of readCoverageOutput()) {
    const coverage = new vscode.FileCoverage(file.uri, file.statementCoverage);
    coverageData.set(coverage, file)
    run.addCoverage(coverage);
  }
}
```

> 或者，你可以继承 `FileCoverage`，在子类的实现中包含这些数据：

```ts
class MyFileCoverage extends vscode.FileCoverage {
  // ...
}

profile.loadDetailedCoverage = async (testRun, fileCoverage, token) => {
  return fileCoverage instanceof MyFileCoverage ? await fileCoverage.load() : [];
}

async function runHandler(shouldDebug: boolean, request: vscode.TestRunRequest, token: vscode.CancellationToken) {
  // ...

  for await (const file of readCoverageOutput()) {
    // 'file' 是 MyFileCoverage：
    run.addCoverage(file);
  }
}
```

**为什么要分两步（摘要 + 详情）？** 一个项目可能有上千个文件，如果一次性把每个文件每一行的覆盖情况都交给 VS Code，数据量会非常大。所以先只给每个文件的**摘要**（覆盖了多少、总共多少），用户真正打开某个文件时，再通过 `loadDetailedCoverage` 加载这个文件的**详情**（具体哪些行被覆盖了）。这又是懒加载的思路。

> `loadDetailedCoverage` 应该返回一个 Promise，其结果是一个 `DeclarationCoverage` 和 / 或 `StatementCoverage` 对象的数组。这两种对象都包含一个 `Position` 或 `Range`，表示它们在源文件中的位置。`DeclarationCoverage` 对象包含被声明的东西的名称（比如函数名或方法名），以及这个声明被进入或调用的次数。语句包含它们被执行的次数，以及零个或多个关联的分支。更多信息请参阅 `vscode.d.ts` 中的类型定义。

```ts
// 示意：返回某个文件的覆盖率详情
return [
  new vscode.StatementCoverage(3, new vscode.Position(10, 0)),        // 第 11 行执行了 3 次
  new vscode.StatementCoverage(0, new vscode.Position(11, 0)),        // 第 12 行没有执行到
  new vscode.DeclarationCoverage('add', 5, new vscode.Position(9, 0)) // 函数 add 被调用了 5 次
];
```

`Position` 的行号从 0 开始计数，所以 `Position(10, 0)` 是第 11 行。

> 很多情况下，测试运行后可能会留下一些持久化的文件。最佳实践是把这类覆盖率输出放在系统的临时目录中（可以通过 `require('os').tmpdir()` 获取），不过你也可以监听 VS Code 发出的“不再需要保留这次测试运行”的信号，主动清理它们：

```ts
import { promises as fs } from 'fs';

async function runHandler(shouldDebug: boolean, request: vscode.TestRunRequest, token: vscode.CancellationToken) {
  // ...

  run.onDidDispose(async () => {
    await fs.rm(coverageOutputDirectory, { recursive: true, force: true });
  });
}
```

注意：不能在 `run.end()` 之后马上删除覆盖率文件，因为用户之后打开文件时，`loadDetailedCoverage` 还需要读取它们。要等到 `run.onDidDispose` 触发（VS Code 不再保留这次运行的结果）时才能删除。

<a id="test-tags"></a>
### 测试标签（Test Tags）

> 有时，测试只能在某些配置下运行，或者根本不能运行。对于这些情况，可以使用测试标签。`TestRunProfile` 可以选择关联一个标签，如果关联了，那么只有带有这个标签的测试，才能在这个配置下运行。同样，如果没有合适的配置可以运行、调试某个测试或收集它的覆盖率，界面中就不会显示这些选项。

```ts
// 创建一个 ID 为 "runnable" 的新标签
const runnableTag = new TestTag('runnable');

// 把它分配给一个配置。现在这个配置只能执行带有这个标签的测试。
runProfile.tag = runnableTag;

// 给所有适用的测试加上 "runnable" 标签。
for (const test of getAllRunnableTests()) {
  test.tags = [...test.tags, runnableTag];
}
```

> 用户也可以在测试资源管理器界面中按标签筛选。

（代码中的 `TestTag` 是 `vscode.TestTag`，示例省略了前缀。）

举个例子：有些测试只能在 Linux 上运行。可以创建一个 `linux` 标签，打在这些测试上，再把它分配给“在 Linux 容器中运行”的那个配置。这样，这些测试只能通过那个配置运行，普通的“运行”按钮对它们不显示。

`test.tags = [...test.tags, runnableTag]` 这样写，是因为 `tags` 是一个只读数组，要整体替换成一个新数组。

<a id="publish-only-controllers"></a>
### 只发布结果的控制器（Publish-only controllers）

> 运行配置并不是必须的。控制器可以创建测试，在 `runHandler` 之外调用 `createTestRun`，并在没有任何配置的情况下更新运行中测试的状态。这种做法的常见用例，是从外部来源（比如 CI 或汇总文件）加载结果的控制器。
>
> 在这种情况下，这些控制器通常应该给 `createTestRun` 传入可选的 `name` 参数，并为 `persist` 参数传入 `false`。在这里传入 `false`，是告诉 VS Code 不要像对待编辑器中的运行那样保留测试结果，因为这些结果可以从外部来源重新加载。

```ts
const controller = vscode.tests.createTestController('myCoverageFileTests', 'Coverage File Tests');

vscode.commands.registerCommand('myExtension.loadTestResultFile', async file => {
  const info = await readFile(file);

  // 把控制器的测试项设为从文件中读取的那些：
  controller.items.replace(readTestsFromInfo(info));

  // 创建你自己的自定义测试运行，然后可以立即设置运行中测试项的状态，
  // 并结束运行，从而发布结果：
  const run = controller.createTestRun(new vscode.TestRunRequest(), path.basename(file), false);
  for (const result of info) {
    if (result.passed) {
      run.passed(result.item);
    } else {
      run.failed(result.item, new vscode.TestMessage(result.message));
    }
  }
  run.end();
});
```

**典型场景：** 测试在 CI 服务器（持续集成）上运行，生成一个结果文件。扩展读取这个文件，把结果显示在测试视图中，用户不用在本地重新运行就能看到哪些测试失败了。因为这些测试不在本地运行，所以不需要运行配置（界面上也就不会有 ▶ 按钮）。

`createTestRun(request, name, persist)` 中：`new vscode.TestRunRequest()` 创建一个空请求；`name` 是这次运行的名称（这里用文件名）；`persist: false` 表示不保留结果（重启后不恢复，因为随时可以从文件重新加载）。

---

<a id="migrating-from-the-test-explorer-ui"></a>
## 从 Test Explorer UI 迁移（Migrating from the Test Explorer UI）

> 如果你已有一个使用 Test Explorer UI 的扩展，我们建议你迁移到原生体验，以获得更多的功能和更高的效率。我们整理了一个仓库，在它的 [Git 历史](https://github.com/connor4312/test-controller-migration-example/commits/master)中展示了迁移 Test Adapter 示例的过程。你可以从 `[1] Create a native TestController` 开始，点击每个提交的名称查看每一步。

**Test Explorer UI** 是测试 API 出现之前，社区提供的一个第三方扩展，很多测试扩展基于它来实现测试视图。VS Code 1.59 有了原生的测试 API 后，推荐迁移过来。如果你从零开始写测试扩展，可以跳过这一节。

> 概括来说，一般的步骤是：
>
> 1. 不再获取 Test Explorer UI 的 `TestHub` 并向它注册 `TestAdapter`，而是调用 `const controller = vscode.tests.createTestController(...)`。
> 2. 发现或重新发现测试时，不再触发 `testAdapter.tests`，而是创建测试并放入 `controller.items` 中，例如，用一个通过调用 `vscode.test.createTestItem` 创建的已发现测试数组，调用 `controller.items.replace`。注意，测试发生变化时，你可以修改测试项上的属性、更新它们的子项，这些变化会自动反映在 VS Code 的界面中。
> 3. 不再等待 `testAdapter.load()` 方法被调用来初始加载测试，而是设置 `controller.resolveHandler = () => { /* 发现测试 */ }`。关于测试发现的工作方式，更多信息请参阅[发现测试](#discovering-tests)。
> 4. 要运行测试，应该创建一个[运行配置](#running-tests)，它的处理函数调用 `const run = controller.createTestRun(request)`。不再触发 `testStates` 事件，而是把 `TestItem` 传给 `run` 上的方法来更新它们的状态。

（第 2 步中的 `vscode.test.createTestItem` 应为 `controller.createTestItem`，测试项是通过控制器创建的。）

| Test Explorer UI 的做法 | 原生 API 的做法 |
|---|---|
| 向 `TestHub` 注册 `TestAdapter` | `vscode.tests.createTestController(...)` |
| 触发 `testAdapter.tests` 事件 | 修改 `controller.items`（如 `replace`），属性变化自动同步到界面 |
| 等待 `testAdapter.load()` | 设置 `controller.resolveHandler` |
| 触发 `testStates` 事件 | `controller.createTestRun(request)`，调用 `run.passed()` 等方法 |

---

<a id="additional-contribution-points"></a>
## 其他贡献点（Additional contribution points）

> `testing/item/context` [菜单贡献点](../references/contribution-points.md#contributes.menus)可以用来给测试资源管理器视图中的测试添加菜单项。把菜单项放在 `inline` 组中，可以让它们显示为行内按钮。其他所有菜单项组，都会显示在通过鼠标右键打开的上下文菜单中。
>
> 在菜单项的 `when` 子句中，还可以使用额外的[上下文键](../references/when-clause-contexts.md)：`testId`、`controllerId` 和 `testItemHasUri`。对于更复杂的 `when` 场景，比如你希望某些操作只对部分测试项可用，可以考虑使用 [`in` 条件运算符](../references/when-clause-contexts.md#in-and-not-in-conditional-operators)。

| 上下文键 | 含义 |
|---|---|
| `testId` | 测试项的 ID |
| `controllerId` | 测试项所属控制器的 ID（`createTestController` 的第一个参数） |
| `testItemHasUri` | 测试项是否设置了 `uri` |

```json
"menus": {
  "testing/item/context": [
    {
      "command": "myExtension.openTestSource",
      "when": "controllerId == helloWorldTests && testItemHasUri",
      "group": "inline"
    }
  ]
}
```

**`in` 运算符的用法：** 假设只有部分测试支持“生成快照”操作，可以先用 `setContext` 设置一个包含这些测试 ID 的数组，再用 `in` 判断当前测试的 ID 是否在其中：

```ts
vscode.commands.executeCommand('setContext', 'myExtension.snapshotTests', ['test-1', 'test-5']);
```

```json
"when": "testId in myExtension.snapshotTests"
```

> 如果你想在资源管理器中显示某个测试，可以把这个测试传给命令：`vscode.commands.executeCommand('vscode.revealTestInExplorer', testItem)`。

---

## 本篇小结

```text
控制器：tests.createTestController(id, label)

发现测试
  controller.createTestItem(id, label, uri) → 设置 range → 加入 controller.items 或 parent.children
  懒加载：canResolveChildren = true + controller.resolveHandler(item | undefined)
  保持更新：onDidOpenTextDocument / onDidChangeTextDocument / createFileSystemWatcher
  自定义数据：WeakMap<TestItem, 数据>

运行测试
  controller.createRunProfile(label, Run | Debug | Coverage, runHandler, isDefault?, tag?)
  runHandler：createTestRun(request) → include - exclude → enqueued / started /
              passed / failed / errored / skipped → run.end()（一定要调用）
  失败差异：TestMessage.diff(消息, 期望, 实际)
  输出：run.appendOutput（终端，换行用 \r\n，支持 ANSI 颜色）
  覆盖率：run.addCoverage(FileCoverage 摘要) + profile.loadDetailedCoverage（打开文件时加载详情）
  标签：TestTag，配置只运行带对应标签的测试
  只发布结果：没有运行配置，直接 createTestRun(request, name, false)

菜单：testing/item/context，上下文键 testId / controllerId / testItemHasUri
```
