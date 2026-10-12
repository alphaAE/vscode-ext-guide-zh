# 测试扩展（Testing Extensions）

> 原文：[Testing Extensions](https://code.visualstudio.com/api/working-with-extensions/testing-extension)
> 源文件：`microsoft/vscode-docs` → `api/working-with-extensions/testing-extension.md`（DateApproved: 10/7/2026）

> Visual Studio Code 支持为你的扩展运行和调试测试。这些测试会在一个名为**扩展开发宿主（Extension Development Host）**的特殊 VS Code 实例中运行，并且可以完全访问 VS Code API。我们把这些测试称为集成测试，因为它们超出了不需要 VS Code 实例就能运行的单元测试的范畴。本文档重点介绍 VS Code 集成测试。

| | 单元测试 | 集成测试（本篇） |
|---|---|---|
| 运行环境 | 普通的 Node.js | 一个真实的 VS Code 实例中 |
| 能否 `import * as vscode from 'vscode'` | 不能（`vscode` 模块只在扩展宿主中存在） | 能 |
| 适合测试 | 不依赖 VS Code API 的纯逻辑（解析、计算……） | 命令、编辑器操作、提供者的结果等真实行为 |
| 速度 | 快 | 慢（要启动 VS Code） |

**建议：** 把不依赖 `vscode` 的逻辑拆到单独的模块中，用单元测试覆盖；与 VS Code 交互的部分用集成测试覆盖。

---

<a id="overview"></a>
## 概览（Overview）

> 如果你使用 [Yeoman 生成器](../get-started/your-first-extension.md)搭建扩展，集成测试已经为你创建好了。
>
> 在生成的扩展中，你可以使用 `npm run test` 或 `yarn test` 来运行集成测试，它会：
>
> - 下载并解压最新版本的 VS Code。
> - 运行扩展测试运行器脚本所指定的 [Mocha](https://mochajs.org) 测试。

注意：测试使用的是**另外下载**的一份 VS Code（存放在项目的 `.vscode-test/` 文件夹中，应该加入 `.gitignore` 和 `.vscodeignore`），而不是你正在使用的这一份。

---

<a id="quick-setup-the-test-cli"></a>
## 快速设置：测试 CLI（Quick Setup: The test CLI）

> VS Code 团队发布了一个用于运行扩展测试的命令行工具。你可以在[扩展示例仓库](https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-test-cli-sample)中找到一个例子。
>
> 测试 CLI 提供了快速的设置，还让你可以使用 [Extension Test Runner](https://marketplace.visualstudio.com/items?itemName=ms-vscode.extension-test-runner) 轻松地运行和调试 VS Code UI 中的测试。这个 CLI 在底层只使用 [Mocha](https://mochajs.org)。
>
> 要开始使用，你首先需要安装 `@vscode/test-cli` 模块，以及让测试可以在 VS Code 桌面版中运行的 `@vscode/test-electron` 模块：

```bash
npm install --save-dev @vscode/test-cli @vscode/test-electron
```

| 包 | 作用 |
|---|---|
| `@vscode/test-electron` | 底层工具：下载 VS Code，用测试参数启动它 |
| `@vscode/test-cli` | 上层的命令行工具 `vscode-test`：读取配置文件，调用 `test-electron`，用 Mocha 运行测试 |
| Extension Test Runner（扩展） | 让 `vscode-test` 配置的测试出现在 VS Code 的**测试资源管理器**中，可以点击运行和调试单个测试（基于 [测试 API](../extension-guides/testing.md)） |

> 安装这些模块之后，你就有了 `vscode-test` 命令行，可以把它添加到 `package.json` 的 `scripts` 部分：

```diff
{
  "name": "my-cool-extension",
  "scripts": {
+   "test": "vscode-test"
```

> `vscode-test` 会在当前工作目录中查找一个 [`.vscode-test.js/mjs/cjs`](https://github.com/microsoft/vscode-extension-samples/blob/main/helloworld-test-cli-sample/.vscode-test.mjs) 文件。这个文件为测试运行器提供配置，完整的定义可以在[这里](https://github.com/microsoft/vscode-test-cli/blob/main/src/config.cts)找到。
>
> 常用的选项包括：
>
> - **（必填）** `files` - 一个模式、一组模式，或者包含要运行的测试的绝对路径。
> - `version` - 运行测试所用的 VS Code 版本（默认为 `stable`）。
> - `workspaceFolder` - 测试期间要打开的工作区的路径。
> - `extensionDevelopmentPath` - 你的扩展文件夹的路径（默认为配置文件所在的目录）。
> - `mocha` - 一个对象，包含要传给 Mocha 的额外[选项](https://mochajs.org/api/mocha#Mocha)。
>
> 配置可以很简单：

```js
// .vscode-test.js
const { defineConfig } = require('@vscode/test-cli');

module.exports = defineConfig({ files: 'out/test/**/*.test.js' });
```

> ……也可以更进阶：

```js
// .vscode-test.js
const { defineConfig } = require('@vscode/test-cli');

module.exports = defineConfig([
  {
    label: 'unitTests',
    files: 'out/test/**/*.test.js',
    version: 'insiders',              // 使用 Insiders 版本
    workspaceFolder: './sampleWorkspace',
    mocha: {
      ui: 'tdd',                      // 使用 suite / test 风格
      timeout: 20000,                 // 每个测试的超时时间（毫秒）
    },
  },
  // 你也可以指定更多的测试配置
]);
```

> 如果你传入一个数组来定义多个配置，运行 `vscode-test` 时它们会依次运行。你可以用 `--label` 标志按 `label` 过滤，单独运行它们，例如 `vscode-test --label unitTests`。运行 `vscode-test --help` 查看完整的命令行选项。

**注意 `files` 指向的是编译后的 JS 文件**（`out/test/**/*.test.js`）：`vscode-test` 不会编译 TypeScript，要先运行 `tsc`。通常在 `package.json` 中加上 `"pretest": "npm run compile"`（使用打包工具时是 `"pretest": "npm run compile-tests"`，见 [打包扩展](./bundling-extension.md#tests)），这样 `npm test` 会先编译再测试。

`version` 除了 `stable` 和 `insiders`，还可以写具体的版本号（如 `'1.90.0'`）。CI 中常用它来测试扩展在 `engines.vscode` 声明的最低版本上能否正常工作。

<a id="test-scripts"></a>
### 测试脚本（Test scripts）

> CLI 设置好之后，你就可以编写和运行测试了。测试脚本可以访问 VS Code API，并在 Mocha 下运行。下面是一个示例（[src/test/suite/extension.test.ts](https://github.com/microsoft/vscode-extension-samples/blob/main/helloworld-test-sample/src/test/suite/extension.test.ts)）：

```ts
import * as assert from 'assert';

// 你可以导入并使用 'vscode' 模块中的所有 API
// 也可以导入你的扩展来测试它
import * as vscode from 'vscode';
// import * as myExtension from '../extension';

suite('Extension Test Suite', () => {
  suiteTeardown(() => {
    // 所有测试结束后执行
    vscode.window.showInformationMessage('All tests done!');
  });

  test('Sample test', () => {
    assert.strictEqual(-1, [1, 2, 3].indexOf(5));
    assert.strictEqual(-1, [1, 2, 3].indexOf(0));
  });
});
```

> 你可以使用 `npm test` 命令运行这个测试，或者在安装了 [Extension Test Runner](https://marketplace.visualstudio.com/items?itemName=ms-vscode.extension-test-runner) 之后，在 VS Code 中使用 **Test: Run All Tests** 命令。你也可以使用 **Test: Debug All Tests** 命令调试测试。

Mocha 的两种接口风格（由 `mocha.ui` 选项决定）：

| TDD 风格（`ui: 'tdd'`） | BDD 风格（`ui: 'bdd'`，Mocha 的默认值） | 作用 |
|---|---|---|
| `suite` | `describe` | 一组测试 |
| `test` | `it` | 一个测试 |
| `suiteSetup` / `suiteTeardown` | `before` / `after` | 整组测试之前 / 之后执行一次 |
| `setup` / `teardown` | `beforeEach` / `afterEach` | 每个测试之前 / 之后执行 |

`@vscode/test-cli` 默认使用 `tdd` 风格，所以示例中用的是 `suite` / `test` / `suiteTeardown`。

**一个更贴近实际的测试**（补充示例，测试 [第一个扩展](../get-started/your-first-extension.md) 中的 Hello World 命令）：

```ts
suite('Hello World', () => {
  test('命令已注册', async () => {
    const commands = await vscode.commands.getCommands(true);
    assert.ok(commands.includes('helloworld.helloWorld'));
  });

  test('命令可以执行', async () => {
    // executeCommand 会激活扩展（如果还没激活）并运行命令
    await vscode.commands.executeCommand('helloworld.helloWorld');
  });
});
```

其他常用的测试手段：用 `vscode.workspace.openTextDocument` + `vscode.window.showTextDocument` 打开测试文件；用 `vscode.commands.executeCommand('vscode.executeXxxProvider', ...)` 获取语言功能的结果（见 [内置命令](../references/commands.md)）；用 `vscode.extensions.getExtension('发布者.扩展名')` 获取扩展并读取它 `activate` 返回的 `exports`。

---

<a id="advanced-setup-your-own-runner"></a>
## 进阶设置：自己的运行器（Advanced setup: Your own runner）

> 你可以在 [helloworld-test-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-test-sample) 中找到本指南的配置。本文档的其余部分会结合这个示例来解释这些文件：
>
> - **测试脚本**（[`src/test/runTest.ts`](https://github.com/microsoft/vscode-extension-samples/blob/main/helloworld-test-sample/src/test/runTest.ts)）
> - **测试运行器脚本**（[`src/test/suite/index.ts`](https://github.com/microsoft/vscode-extension-samples/blob/main/helloworld-test-sample/src/test/suite/index.ts)）

不使用 `@vscode/test-cli`，自己控制整个流程。适合需要使用 Mocha 以外的测试框架，或者有特殊准备步骤的情况。两个文件运行在不同的地方：

```text
npm test
  → node out/test/runTest.js              【测试脚本】运行在普通的 Node.js 中
      → 下载 VS Code，用 --extensionDevelopmentPath / --extensionTestsPath 启动它
          → VS Code 的扩展宿主加载 out/test/suite/index.js   【测试运行器脚本】运行在 VS Code 中
              → 调用它导出的 run()，在其中用 Mocha 运行所有 *.test.js
```

> VS Code 为运行扩展测试提供了两个命令行参数：`--extensionDevelopmentPath` 和 `--extensionTestsPath`。
>
> 例如：

```bash
# - 启动 VS Code 扩展宿主
# - 加载 <EXTENSION-ROOT-PATH> 处的扩展
# - 执行 <TEST-RUNNER-SCRIPT-PATH> 处的测试运行器脚本
code \
--extensionDevelopmentPath=<EXTENSION-ROOT-PATH> \
--extensionTestsPath=<TEST-RUNNER-SCRIPT-PATH>
```

> **测试脚本**（[`src/test/runTest.ts`](https://github.com/microsoft/vscode-extension-samples/blob/main/helloworld-test-sample/src/test/runTest.ts)）使用 `@vscode/test-electron` API，简化了下载、解压 VS Code，以及带着扩展测试参数启动 VS Code 的过程：

```ts
import * as path from 'path';

import { runTests } from '@vscode/test-electron';

async function main() {
  try {
    // 包含扩展清单 package.json 的文件夹
    // 传给 `--extensionDevelopmentPath`
    const extensionDevelopmentPath = path.resolve(__dirname, '../../');

    // 扩展测试运行器脚本的路径
    // 传给 --extensionTestsPath
    const extensionTestsPath = path.resolve(__dirname, './suite/index');

    // 下载 VS Code，解压，并运行集成测试
    await runTests({ extensionDevelopmentPath, extensionTestsPath });
  } catch (err) {
    console.error(err);
    console.error('Failed to run tests');
    process.exit(1);
  }
}

main();
```

（`__dirname` 是编译后的 `out/test/`，所以 `../../` 是扩展根目录。这时 `package.json` 中的脚本是 `"test": "node ./out/test/runTest.js"`。）

> `@vscode/test-electron` API 还允许：
>
> - 用一个特定的工作区启动 VS Code。
> - 下载一个不同的 VS Code 版本，而不是最新的稳定版。
> - 用额外的命令行参数启动 VS Code。
>
> 你可以在 [microsoft/vscode-test](https://github.com/microsoft/vscode-test) 找到更多的 API 用法示例。

对应 `runTests` 的选项：`launchArgs`（额外的命令行参数，第一个参数如果是路径就会被打开，可用于指定工作区）、`version`（VS Code 版本）、`extensionTestsEnv`（传给测试的环境变量）。

<a id="the-test-runner-script"></a>
### 测试运行器脚本（The test runner script）

> 运行扩展集成测试时，`--extensionTestsPath` 指向以编程方式运行测试套件的**测试运行器脚本**（[`src/test/suite/index.ts`](https://github.com/microsoft/vscode-extension-samples/blob/main/helloworld-test-sample/src/test/suite/index.ts)）。下面是 `helloworld-test-sample` 的[测试运行器脚本](https://github.com/microsoft/vscode-extension-samples/blob/main/helloworld-test-sample/src/test/suite/index.ts)，它使用 Mocha 运行测试套件。你可以以此为起点，用 [Mocha 的 API](https://mochajs.org/api/mocha) 定制你的设置。你也可以把 Mocha 替换为任何其他可以以编程方式运行的测试框架。

```ts
import * as path from 'path';
import * as Mocha from 'mocha';
import { glob } from 'glob';

// VS Code 会调用这个导出的 run 函数，并等待它返回的 Promise
export function run(): Promise<void> {
  // 创建 mocha 测试
  const mocha = new Mocha({
    ui: 'tdd',
    color: true
  });

  const testsRoot = path.resolve(__dirname, '..');

  return new Promise((c, e) => {
    // 找到所有测试文件
    glob('**/**.test.js', { cwd: testsRoot }).then((files) => {
      // 把文件添加到测试套件中
      files.forEach(f => mocha.addFile(path.resolve(testsRoot, f)));

      try {
        // 运行 mocha 测试
        mocha.run(failures => {
          if (failures > 0) {
            e(new Error(`${failures} tests failed.`));  // 有失败的测试：reject
          } else {
            c();                                        // 全部通过：resolve
          }
        });
      } catch (err) {
        e(err);
      }
    }).catch((err) => {
      return e(err);
    });
  });
}
```

`run()` 返回的 Promise 决定了测试的结果：resolve 表示通过，reject 表示失败。VS Code 据此以对应的退出码退出，`runTests` 再据此 resolve 或 reject，最终让 `npm test` 成功或失败（CI 依赖这个退出码判断结果）。`glob` 的这种 Promise 写法需要 `glob` 9 及以上版本。

> 测试运行器脚本和 `*.test.js` 文件都可以访问 VS Code API。
>
> 下面是一个测试示例（[src/test/suite/extension.test.ts](https://github.com/microsoft/vscode-extension-samples/blob/main/helloworld-test-sample/src/test/suite/extension.test.ts)）：

```ts
import * as assert from 'assert';
import { after } from 'mocha';

// 你可以导入并使用 'vscode' 模块中的所有 API
// 也可以导入你的扩展来测试它
import * as vscode from 'vscode';
// import * as myExtension from '../extension';

suite('Extension Test Suite', () => {
  after(() => {
    vscode.window.showInformationMessage('All tests done!');
  });

  test('Sample test', () => {
    assert.strictEqual(-1, [1, 2, 3].indexOf(5));
    assert.strictEqual(-1, [1, 2, 3].indexOf(0));
  });
});
```

（这个示例与前面的基本相同，只是用了从 `mocha` 导入的 `after`。运行器配置的是 `ui: 'tdd'`，按 TDD 风格，对应的写法是前一个示例中的 `suiteTeardown`，推荐与所选的风格保持一致。）

<a id="debugging-the-tests"></a>
### 调试测试（Debugging the tests）

> 调试测试与调试扩展类似。
>
> 下面是一个 `launch.json` 调试器配置的示例：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Extension Tests",
      "type": "extensionHost",
      "request": "launch",
      "runtimeExecutable": "${execPath}",
      "args": [
        "--extensionDevelopmentPath=${workspaceFolder}",
        "--extensionTestsPath=${workspaceFolder}/out/test/suite/index"
      ],
      "outFiles": ["${workspaceFolder}/out/test/**/*.js"]
    }
  ]
}
```

<video src="images/testing-extension/debug.mp4" autoplay loop muted playsinline controls>
  <a href="images/testing-extension/debug.mp4">调试测试的演示视频（debug.mp4）</a>
</video>

视频演示：在测试文件中设置断点，在“运行和调试”视图中选择 **Extension Tests** 配置并启动，测试运行到断点处暂停，可以查看变量、单步执行。

这个配置与普通的 **Run Extension** 配置的区别，只是多了 `--extensionTestsPath`：有了它，扩展开发宿主启动后会运行测试，测试结束后自动关闭。`"type": "extensionHost"` 的调试配置使用的是**当前**的 VS Code（`${execPath}`），而不是 `.vscode-test/` 中下载的那一份。使用 `@vscode/test-cli` 时，更方便的做法是用 Extension Test Runner 在测试资源管理器中直接调试。

---

<a id="tips"></a>
## 提示（Tips）

<a id="using-insiders-version-for-extension-development"></a>
### 使用 Insiders 版本进行扩展开发（Using Insiders version for extension development）

> 由于 VS Code 的限制，如果你正在使用 VS Code 稳定版，并尝试**在命令行中**运行集成测试，它会抛出一个错误：

```text
Running extension tests from the command line is currently only supported if no other instance of Code is running.
```

> 一般来说，如果你从命令行运行扩展测试，测试所用的版本不能已经在运行中。作为一种变通方法，你可以在 VS Code 稳定版中运行测试，并使用 [VS Code Insiders](https://code.visualstudio.com/insiders/) 进行开发。只要你不是在 VS Code Insiders 中、而是在 VS Code 稳定版中从命令行运行测试，这样的设置就能正常工作。
>
> 另一种做法是在 VS Code 自身中，通过调试启动配置运行扩展测试。这样做还有一个额外的好处：你甚至可以调试测试。

错误信息的意思是“目前只有在没有其他 Code 实例运行时，才支持从命令行运行扩展测试”。简单地说：你正在用稳定版写代码，测试也要用稳定版跑，两者会冲突。解决方法二选一：

| 方法 | 做法 |
|---|---|
| 开发和测试用不同的版本 | 用 Insiders 写代码，测试配置 `version: 'stable'`；或者反过来，用稳定版写代码，测试配置 `version: 'insiders'` |
| 不从命令行运行 | 用调试配置（`F5`）或 Extension Test Runner 在 VS Code 内部运行 |

在 CI 中没有正在运行的 VS Code，不受这个限制。

<a id="disabling-other-extensions-while-debugging"></a>
### 调试时禁用其他扩展（Disabling other extensions while debugging）

> 当你在 VS Code 中调试扩展测试时，VS Code 使用全局安装的 VS Code 实例，并且会加载所有已安装的扩展。你可以在 `launch.json` 中添加 `--disable-extensions` 配置，或者把它添加到 `@vscode/test-electron` 的 `runTests` API 的 `launchArgs` 选项中。

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Extension Tests",
      "type": "extensionHost",
      "request": "launch",
      "runtimeExecutable": "${execPath}",
      "args": [
        "--disable-extensions",
        "--extensionDevelopmentPath=${workspaceFolder}",
        "--extensionTestsPath=${workspaceFolder}/out/test/suite/index"
      ],
      "outFiles": ["${workspaceFolder}/out/test/**/*.js"]
    }
  ]
}
```

```ts
await runTests({
  extensionDevelopmentPath,
  extensionTestsPath,
  /**
   * 传给 VS Code 可执行文件的启动参数列表，作为 `--extensionDevelopmentPath`
   * 和 `--extensionTestsPath` 之外的补充（这两个参数由 `extensionDevelopmentPath`
   * 和 `extensionTestsPath` 选项提供）。
   *
   * 如果第一个参数是一个文件 / 文件夹 / 工作区的路径，启动的 VS Code 实例
   * 会打开它。
   *
   * 可用的参数见 `code --help`。
   */
  launchArgs: ['--disable-extensions']
});
```

为什么要禁用？你自己安装的其他扩展可能会影响测试结果（比如另一个扩展也注册了同一种语言的补全），也会拖慢启动。`--disable-extensions` 只禁用已安装的扩展，正在开发的扩展（`--extensionDevelopmentPath`）照常加载。使用 `@vscode/test-cli` 时，在配置中写 `launchArgs: ['--disable-extensions']` 即可。

<a id="custom-setup-with-vscodetest-electron"></a>
### 使用 `@vscode/test-electron` 进行自定义设置（Custom setup with `@vscode/test-electron`）

> 有时你可能想运行一些自定义的设置，例如在开始测试之前运行 `code --install-extension` 安装另一个扩展。`@vscode/test-electron` 有一个更细粒度的 API 来满足这种情况：

```ts
import * as cp from 'child_process';
import * as path from 'path';
import {
  downloadAndUnzipVSCode,
  resolveCliArgsFromVSCodeExecutablePath,
  runTests
} from '@vscode/test-electron';

async function main() {
  try {
    const extensionDevelopmentPath = path.resolve(__dirname, '../../../');
    const extensionTestsPath = path.resolve(__dirname, './suite/index');
    // 1. 下载指定版本的 VS Code，得到可执行文件的路径
    const vscodeExecutablePath = await downloadAndUnzipVSCode('1.40.1');
    // 2. 由可执行文件路径得到 CLI 的路径和参数
    const [cliPath, ...args] = resolveCliArgsFromVSCodeExecutablePath(vscodeExecutablePath);

    // 使用 cp.spawn / cp.exec 进行自定义设置
    // 3. 用 CLI 安装测试所需的其他扩展（比如你的扩展所依赖的扩展）
    cp.spawnSync(cliPath, [...args, '--install-extension', '<EXTENSION-ID-OR-PATH-TO-VSIX>'], {
      encoding: 'utf-8',
      stdio: 'inherit'
    });

    // 运行扩展测试
    await runTests({
      // 使用指定的 `code` 可执行文件
      vscodeExecutablePath,
      extensionDevelopmentPath,
      extensionTestsPath
    });
  } catch (err) {
    console.error('Failed to run tests');
    process.exit(1);
  }
}

main();
```

典型的使用场景：你的扩展在 `package.json` 中声明了 `extensionDependencies`（依赖另一个扩展），测试前必须先把那个扩展装进测试用的 VS Code 中，否则你的扩展无法激活。示例中的 `'1.40.1'` 只是一个例子，可以换成 `'stable'`、`'insiders'` 或其他版本号。`resolveCliArgsFromVSCodeExecutablePath` 返回的 `args` 中包含了 `--extensions-dir` 等参数，确保扩展被安装到测试用的那份 VS Code 中，而不是你自己的 VS Code 中。

---

<a id="testing-workspace-trust-behavior"></a>
## 测试工作区信任的行为（Testing Workspace Trust behavior）

> 如果你的扩展在 `package.json` 中声明了 `capabilities.untrustedWorkspaces`，就要为受信任和不受信任的工作区都添加集成测试。你无法在扩展测试中以编程方式授予或撤销工作区信任。请为受信任和不受信任两种状态分别运行测试。
>
> 使用 `@vscode/test-cli` 时，定义不同的测试配置，这样你就可以独立运行每一种信任状态：
>
> - **trustedWorkspaceTests**：给你一次不应用信任限制的基准运行。这有助于验证扩展的完整功能行为，并发现受信任路径中的回归问题。
> - **untrustedWorkspaceTests**：在工作区信任仍然启用的情况下，验证受限模式下的行为。使用一个专门的 `--user-data-dir`，可以防止之前保存的信任决定让这次运行意外地变成受信任的。
>
> 因为每个配置都有自己的 `label`，你可以独立地运行它们（例如 `vscode-test --label trustedWorkspaceTests` 和 `vscode-test --label untrustedWorkspaceTests`），也可以依次运行两者。

```js
// .vscode-test.js
const { defineConfig } = require('@vscode/test-cli');
const path = require('path');

module.exports = defineConfig([
  {
    label: 'trustedWorkspaceTests',
    files: 'out/test/**/*.test.js',
    workspaceFolder: './test/fixtures/trusted-workspace',
    // 可选：在这次运行中禁用工作区信任
    launchArgs: ['--disable-workspace-trust'],
  },
  {
    label: 'untrustedWorkspaceTests',
    files: 'out/test/**/*.test.js',
    workspaceFolder: './test/fixtures/untrusted-workspace',
    // 保持工作区信任启用，并隔离用户数据，使运行结果可以确定
    launchArgs: [
      '--user-data-dir',
      path.join(__dirname, '.vscode-test', 'user-data-untrusted'),
    ],
  },
]);
```

| 配置 | 启动参数 | 效果 |
|---|---|---|
| 受信任 | `--disable-workspace-trust` | 完全关闭信任功能，所有工作区都当作受信任的 |
| 不受信任 | 一个全新的 `--user-data-dir` | 信任功能照常启用，而且这个用户数据目录中从未信任过任何文件夹，所以打开的工作区处于受限模式 |

> 在你的测试中，通过检查 `vscode.workspace.isTrusted` 来断言与信任相关的行为：

```ts
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Workspace Trust Tests', () => {
  test('extension behavior changes by trust state', async () => {
    // 调用扩展自己提供的一个命令，查询某个受限功能是否可用
    const isFeatureAvailable = await vscode.commands.executeCommand<boolean>(
      'myExtension.isRestrictedFeatureEnabled'
    );

    if (vscode.workspace.isTrusted) {
      assert.strictEqual(isFeatureAvailable, true);
    } else {
      assert.strictEqual(isFeatureAvailable, false);
    }
  });
});
```

> 关于如何在扩展清单中声明信任要求，以及如何使用 `vscode.workspace.isTrusted` API，更多信息请参见[工作区信任扩展指南](../extension-guides/workspace-trust.md)。

`myExtension.isRestrictedFeatureEnabled` 是一个假设的、专门为了测试而注册的命令。同一份测试文件在两种配置下都会运行，通过 `isTrusted` 判断当前是哪种状态，再断言对应的行为。

---

<a id="next-steps"></a>
## 下一步（Next steps）

> - [持续集成](./continuous-integration.md) - 在 Azure DevOps 等持续集成服务中运行你的扩展测试。
> - [工作区信任扩展指南](../extension-guides/workspace-trust.md) - 了解如何在扩展中声明和处理工作区信任。

---

## 本篇小结

```text
集成测试：在下载的 VS Code 实例（扩展开发宿主）中运行，可以使用 vscode API；底层用 Mocha

推荐：@vscode/test-cli + @vscode/test-electron
  package.json："test": "vscode-test"（先 pretest 编译 TS）
  .vscode-test.js：defineConfig({ files, version, workspaceFolder, mocha, launchArgs, label })
  多个配置用数组，vscode-test --label 选择运行
  Extension Test Runner 扩展：在测试资源管理器中运行 / 调试

进阶：自己的运行器
  runTest.ts（Node 中）：runTests({ extensionDevelopmentPath, extensionTestsPath, launchArgs, version })
  suite/index.ts（VS Code 中）：export function run(): Promise<void>，用 Mocha 运行 *.test.js
  launch.json：extensionHost + --extensionTestsPath 调试测试

提示
  命令行测试与正在运行的同版本 VS Code 冲突 → 开发用 Insiders，或在 VS Code 内部运行
  --disable-extensions 排除其他扩展的干扰
  downloadAndUnzipVSCode + resolveCliArgsFromVSCodeExecutablePath 预先安装依赖扩展
  工作区信任：--disable-workspace-trust / 独立的 --user-data-dir 分别测试两种状态
```
