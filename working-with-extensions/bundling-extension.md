# 打包扩展代码（Bundling Extensions）

> 原文：[Bundling Extensions](https://code.visualstudio.com/api/working-with-extensions/bundling-extension)
> 源文件：`microsoft/vscode-docs` → `api/working-with-extensions/bundling-extension.md`（DateApproved: 10/7/2026）

> 打包（bundle）你的 Visual Studio Code 扩展的首要原因，是确保它能为在任何平台上使用 VS Code 的所有人工作。只有打包过的扩展才能在 [github.dev](https://github.dev/) 和 [vscode.dev](https://vscode.dev/) 等 VS Code for Web 环境中使用。当 VS Code 在浏览器中运行时，它只能为你的扩展加载一个文件，所以扩展的代码需要被打包成一个适合 Web 的 JavaScript 文件。这一点同样适用于[笔记本输出渲染器](../extension-guides/notebook.md#notebook-renderer)，VS Code 也只会为你的渲染器扩展加载一个文件。
>
> 此外，扩展的体积和复杂度可能会迅速增长。它们可能由多个源文件编写而成，并依赖来自 [npm](https://www.npmjs.com) 的模块。分解与复用是开发中的最佳实践，但在安装和运行扩展时是有代价的。加载 100 个小文件比加载一个大文件慢得多。这就是我们推荐打包的原因。打包就是把多个小的源文件合并成一个文件的过程。
>
> 对于 JavaScript，有多种不同的打包工具可用。流行的有 [rollup.js](https://rollupjs.org)、[Parcel](https://parceljs.org)、[esbuild](https://esbuild.github.io/) 和 [webpack](https://webpack.js.org/)。

**注意区分两个“打包”：** 本篇的 bundle（打包、合并）是把源代码和依赖**合并成一个 JS 文件**；[发布扩展](./publishing-extension.md) 中的 package（`vsce package`）是把整个扩展**压缩成一个 `.vsix` 安装包**。通常的流程是：先 bundle，再 package。

| 打包的好处 | 原因 |
|---|---|
| 能在 Web 版 VS Code 中运行 | 浏览器中只能加载一个文件（见 [Web 扩展](../extension-guides/web-extensions.md)） |
| 安装更快、体积更小 | 不需要把整个 `node_modules`（可能有成千上万个文件）打进安装包 |
| 激活更快 | 加载一个文件比逐个解析几百个 `require` 快得多 |

用 `yo code` 生成新扩展时，可以选择使用 esbuild 或 webpack 作为打包工具，生成的项目已经配置好了本篇介绍的内容。

---

<a id="using-esbuild"></a>
## 使用 esbuild（Using esbuild）

> `esbuild` 是一个快速、配置简单的 JavaScript 打包工具。要获取 esbuild，打开终端并输入：

```bash
npm i --save-dev esbuild
```

<a id="run-esbuild"></a>
### 运行 esbuild（Run esbuild）

> 你可以从命令行运行 esbuild，但为了减少重复并支持问题报告，使用一个构建脚本 `esbuild.js` 会很有帮助：

```js
const esbuild = require("esbuild");

const production = process.argv.includes('--production');
const watch = process.argv.includes('--watch');

async function main() {
	const ctx = await esbuild.context({
		entryPoints: [
			'src/extension.ts'           // 入口文件
		],
		bundle: true,                    // 把所有依赖合并进来
		format: 'cjs',                   // 输出 CommonJS 格式（扩展宿主用 require 加载扩展）
		minify: production,              // 生产模式下压缩
		sourcemap: !production,          // 开发模式下生成 source map，方便调试
		sourcesContent: false,
		platform: 'node',                // 目标平台：Node.js（桌面版扩展宿主）
		outfile: 'dist/extension.js',    // 输出文件
		external: ['vscode'],            // 不打包 vscode 模块
		logLevel: 'warning',
		plugins: [
			/* 添加到 plugins 数组的末尾 */
			esbuildProblemMatcherPlugin,
		],
	});
	if (watch) {
		await ctx.watch();               // 监视模式：文件变化时自动重新打包
	} else {
		await ctx.rebuild();             // 只打包一次
		await ctx.dispose();
	}
}

/**
 * @type {import('esbuild').Plugin}
 */
const esbuildProblemMatcherPlugin = {
	name: 'esbuild-problem-matcher',

	setup(build) {
		build.onStart(() => {
			console.log('[watch] build started');
		});
		build.onEnd((result) => {
			result.errors.forEach(({ text, location }) => {
				console.error(`✘ [ERROR] ${text}`);
                if (location == null) return;
				console.error(`    ${location.file}:${location.line}:${location.column}:`);
			});
			console.log('[watch] build finished');
		});
	}
};

main().catch(e => {
	console.error(e);
	process.exit(1);
});
```

> 这个构建脚本做了以下事情：
>
> - 它用 esbuild 创建一个构建上下文。这个上下文被配置为：
>   - 把 `src/extension.ts` 中的代码打包成一个文件 `dist/extension.js`。
>   - 如果传入了 `--production` 标志，就压缩代码。
>   - 除非传入了 `--production` 标志，否则生成 source map。
>   - 把 'vscode' 模块排除在包之外（因为它由 VS Code 运行时提供）。
> - 使用 esbuildProblemMatcherPlugin 插件，报告那些导致打包无法完成的错误。这个插件以 `esbuild` 问题匹配器能识别的格式输出错误，这个问题匹配器也需要作为一个扩展安装。
> - 如果传入了 `--watch` 标志，它会开始监视源文件的变化，并在检测到变化时重新打包。

**为什么要把 `vscode` 设为 external？** `import * as vscode from 'vscode'` 中的 `vscode` 模块并不在 `node_modules` 中（`@types/vscode` 只有类型声明），它是扩展宿主在运行时注入的。如果不排除，打包工具会因为找不到它而报错。

**问题匹配器插件的作用：** 插件输出的 `[watch] build started`、`✘ [ERROR] ...`、`[watch] build finished` 这几行格式，是给下文 `tasks.json` 中的问题匹配器 `$esbuild-watch` 读取的：VS Code 据此知道构建何时开始和结束，并把错误显示在“问题”面板中。

> esbuild 可以直接处理 TypeScript 文件。不过，esbuild 只是简单地去掉所有的类型声明，不做任何类型检查。只有语法错误会被报告，并可能导致 esbuild 失败。
>
> 因此，我们单独运行 TypeScript 编译器（`tsc`）来检查类型，但不输出任何代码（`--noEmit` 标志）。

| 工具 | 负责 | 不负责 |
|---|---|---|
| esbuild | 把 TS 转成 JS 并打包（非常快） | 类型检查 |
| `tsc --noEmit` | 类型检查 | 输出文件 |

> 现在 `package.json` 中的 `scripts` 部分看起来是这样的：

```json
"scripts": {
    "compile": "npm run check-types && node esbuild.js",
    "check-types": "tsc --noEmit",
    "watch": "npm-run-all -p watch:*",
    "watch:esbuild": "node esbuild.js --watch",
    "watch:tsc": "tsc --noEmit --watch --project tsconfig.json",
    "vscode:prepublish": "npm run package",
    "package": "npm run check-types && node esbuild.js --production"
}
```

> `npm-run-all` 是一个 node 模块，它会并行运行名称匹配给定前缀的脚本。对我们来说，它会运行 `watch:esbuild` 和 `watch:tsc` 两个脚本。你需要把 `npm-run-all` 添加到 `package.json` 的 `devDependencies` 部分。
>
> `compile` 和 `watch` 脚本用于开发，它们生成带有 source map 的包文件。`package` 脚本被 `vscode:prepublish` 脚本使用，而 `vscode:prepublish` 由 VS Code 的打包和发布工具 `vsce` 使用，在发布扩展之前运行。向 esbuild 脚本传入 `--production` 标志，会让它压缩代码并生成一个小的包，但也会让调试变得困难，所以在开发过程中使用其他的标志。要运行上面的脚本，打开终端并输入 `npm run watch`，或者从命令面板（`Ctrl+Shift+P`）中选择 **Tasks: Run Task**。

| 脚本 | 用于 | 做什么 |
|---|---|---|
| `compile` | 开发，构建一次 | 类型检查 + 打包（带 source map） |
| `watch` | 开发，持续构建 | 并行运行 `watch:esbuild` 和 `watch:tsc` |
| `package` | 发布 | 类型检查 + 压缩打包 |
| `vscode:prepublish` | `vsce package` / `vsce publish` 时**自动执行** | 调用 `package` |

（`npm-run-all -p watch:*` 中的 `-p` 表示并行。`npm-run-all` 已经很久没有更新了，也可以使用兼容的分支 `npm-run-all2`，命令相同。macOS 上的命令面板快捷键是 `Cmd+Shift+P`。）

> 如果你像下面这样配置 `.vscode/tasks.json`，每个 watch 任务都会有一个单独的终端。

```json
{
	"version": "2.0.0",
	"tasks": [
		{
            "label": "watch",
            "dependsOn": [
                "npm: watch:tsc",
                "npm: watch:esbuild"
            ],
            "presentation": {
                "reveal": "never"
            },
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "type": "npm",
            "script": "watch:esbuild",
            "group": "build",
            "problemMatcher": "$esbuild-watch",
            "isBackground": true,
            "label": "npm: watch:esbuild",
            "presentation": {
                "group": "watch",
                "reveal": "never"
            }
        },
		{
            "type": "npm",
            "script": "watch:tsc",
            "group": "build",
            "problemMatcher": "$tsc-watch",
            "isBackground": true,
            "label": "npm: watch:tsc",
            "presentation": {
                "group": "watch",
                "reveal": "never"
            }
        }
    ]
}
```

| 配置 | 含义 |
|---|---|
| `"label": "watch"` + `dependsOn` | 一个组合任务，同时启动两个 watch 任务 |
| `group.isDefault: true` | 默认构建任务：按 `Ctrl+Shift+B` 运行它 |
| `isBackground: true` | 后台任务（不会自己结束），VS Code 通过问题匹配器判断“这一轮构建完成了” |
| `problemMatcher` | `$esbuild-watch` 读取 esbuild 的输出，`$tsc-watch` 读取 tsc 的输出（后者是内置的） |
| `presentation.group: "watch"` | 两个终端放在同一个分组中，并排显示 |

在 `launch.json` 的调试配置中设置 `"preLaunchTask": "watch"`（`yo code` 生成的项目已经这样配置），按 `F5` 时会先启动这个任务，等第一轮构建完成后再启动扩展开发宿主。

> 这些 watch 任务依赖扩展 [`connor4312.esbuild-problem-matchers`](https://marketplace.visualstudio.com/items?itemName=connor4312.esbuild-problem-matchers) 来做问题匹配，你需要安装它，任务才能在“问题”视图中报告问题。这个扩展需要安装，启动才能完成。
>
> 为了不忘记这一点，在工作区中添加一个 `.vscode/extensions.json` 文件：

```json
{
  "recommendations": ["connor4312.esbuild-problem-matchers"]
}
```

“启动才能完成”的原因：`$esbuild-watch` 这个问题匹配器是由那个扩展提供的。没有它，VS Code 不认识这个匹配器，也就无法判断后台任务何时完成构建，`F5` 会一直等待 `preLaunchTask` 结束。`extensions.json` 中的推荐，会让打开这个项目的人收到“安装推荐的扩展”的提示。

> 最后，你需要更新 `.vscodeignore` 文件，让编译后的文件被包含在发布的扩展中。详情请查看[发布](#publishing)一节。
>
> 跳到[测试](#tests)一节继续阅读。

---

<a id="using-webpack"></a>
## 使用 webpack（Using webpack）

> Webpack 是一个可以从 [npm](https://www.npmjs.com) 获取的开发工具。要获取 webpack 及其命令行界面，打开终端并输入：

```bash
npm i --save-dev webpack webpack-cli
```

> 这会安装 webpack，并更新你的扩展的 `package.json` 文件，把 webpack 包含在 `devDependencies` 中。
>
> Webpack 是一个 JavaScript 打包工具，但许多 VS Code 扩展是用 TypeScript 编写、然后才编译成 JavaScript 的。如果你的扩展使用 TypeScript，可以使用加载器 `ts-loader`，让 webpack 能够理解 TypeScript。使用下面的命令安装 `ts-loader`：

```bash
npm i --save-dev ts-loader
```

> 所有文件都可以在 [webpack-extension](https://github.com/microsoft/vscode-extension-samples/blob/main/webpack-sample) 示例中找到。

<a id="configure-webpack"></a>
### 配置 webpack（Configure webpack）

> 安装好所有工具后，就可以配置 webpack 了。按照惯例，`webpack.config.js` 文件中包含指导 webpack 打包你的扩展的配置。下面的示例配置是针对 VS Code 扩展的，应该能提供一个很好的起点：

```javascript
//@ts-check

'use strict';

const path = require('path');
const webpack = require('webpack');

/**@type {import('webpack').Configuration}*/
const config = {
    target: 'webworker', // vscode 扩展在 VS Code Web 版中运行在 webworker 上下文中 📖 -> https://webpack.js.org/configuration/target/#target

    entry: './src/extension.ts', // 这个扩展的入口，📖 -> https://webpack.js.org/configuration/entry-context/
    output: { // 打包结果存放在 'dist' 文件夹中（检查 package.json），📖 -> https://webpack.js.org/configuration/output/
        path: path.resolve(__dirname, 'dist'),
        filename: 'extension.js',
        libraryTarget: "commonjs2",
        devtoolModuleFilenameTemplate: "../[resource-path]",
    },
    devtool: 'source-map',
    externals: {
        vscode: "commonjs vscode" // vscode 模块是运行时动态创建的，必须排除。其他无法被 webpack 打包的模块也加在这里，📖 -> https://webpack.js.org/configuration/externals/
    },
    resolve: { // 支持读取 TypeScript 和 JavaScript 文件，📖 -> https://github.com/TypeStrong/ts-loader
        mainFields: ['browser', 'module', 'main'], // 在导入的 node 模块中优先查找 `browser` 入口
        extensions: ['.ts', '.js'],
        alias: {
            // 为 node 模块和源文件提供替代实现
        },
        fallback: {
            // Webpack 5 不再自动为 Node.js 核心模块提供 polyfill。
            // Node.js 核心模块的 polyfill 列表见
            // https://webpack.js.org/configuration/resolve/#resolvefallback
        }
    },
    module: {
        rules: [{
            test: /\.ts$/,
            exclude: /node_modules/,
            use: [{
                loader: 'ts-loader',
            }]
        }]
    },
}
module.exports = config;
```

> 这个文件作为 [webpack-extension](https://github.com/microsoft/vscode-extension-samples/blob/main/webpack-sample) 示例的一部分[提供](https://github.com/microsoft/vscode-extension-samples/blob/main/webpack-sample/webpack.config.js)。Webpack 配置文件是普通的 JavaScript 模块，必须导出一个配置对象。
>
> 在上面的示例中，定义了以下内容：
>
> - `target` 指出你的扩展将在什么上下文中运行。我们推荐使用 `webworker`，这样你的扩展就能同时在 VS Code Web 版和 VS Code 桌面版中工作。
> - webpack 应该使用的入口。这类似于 `package.json` 中的 `main` 属性，区别在于你提供给 webpack 的是一个“源”入口，通常是 `src/extension.ts`，而不是一个“输出”入口。webpack 打包工具理解 TypeScript，所以单独的 TypeScript 编译步骤是多余的。
> - `output` 配置告诉 webpack 把生成的包文件放在哪里。按照惯例，这是 `dist` 文件夹。在这个示例中，webpack 会生成一个 `dist/extension.js` 文件。
> - `resolve` 和 `module/rules` 配置用于支持 TypeScript 和 JavaScript 输入文件。
> - `externals` 配置用于声明排除项，例如不应该包含在包中的文件和模块。`vscode` 模块不应该被打包，因为它不存在于磁盘上，而是在需要时由 VS Code 动态创建的。根据扩展所使用的 node 模块，可能还需要更多的排除项。

**关于 `target: 'webworker'`：** 以 `webworker` 为目标打包出来的代码不能使用 Node.js 的 API（`fs`、`child_process`、`path` 等）。如果你的扩展只运行在桌面版、并且用到了这些 API，应该改用 `target: 'node'`；如果要同时支持两种环境，常见的做法是打包两份：`main` 指向 `node` 目标的包，`browser` 指向 `webworker` 目标的包（见 [Web 扩展](../extension-guides/web-extensions.md)）。另外，`ts-loader` 会在打包时做类型检查，所以 webpack 方案不需要单独的 `tsc --noEmit`。

<a id="run-webpack"></a>
### 运行 webpack（Run webpack）

> 创建了 `webpack.config.js` 文件之后，就可以调用 webpack 了。你可以从命令行运行 webpack，但为了减少重复，使用 npm 脚本会很有帮助。
>
> 把这些条目合并到 `package.json` 的 `scripts` 部分中：

```json
"scripts": {
    "compile": "webpack --mode development",
    "watch": "webpack --mode development --watch",
    "vscode:prepublish": "npm run package",
    "package": "webpack --mode production --devtool hidden-source-map",
},
```

（这段 JSON 末尾多了一个逗号，合并到 `package.json` 时要去掉，否则 JSON 无效。）

> `compile` 和 `watch` 脚本用于开发，它们生成包文件。`vscode:prepublish` 由 VS Code 的打包和发布工具 `vsce` 使用，在发布扩展之前运行。区别在于[模式（mode）](https://webpack.js.org/concepts/mode/)，它控制优化的级别。使用 `production` 生成的包最小，但也更耗时，所以在其他情况下使用 `development`。要运行上面的脚本，打开终端并输入 `npm run compile`，或者从命令面板（`Ctrl+Shift+P`）中选择 **Tasks: Run Task**。

`--devtool hidden-source-map`：生产模式下仍然生成 source map 文件，但不在 JS 文件中引用它。这样发布的扩展体积不受影响（只要在 `.vscodeignore` 中排除 `.map` 文件），而开发者手中保留了 source map，可以用来还原用户报告的错误堆栈。

---

<a id="run-the-extension"></a>
## 运行扩展（Run the extension）

> 在运行扩展之前，`package.json` 中的 `main` 属性必须指向包文件，对于上面的配置来说是 [`"./dist/extension"`](https://github.com/microsoft/vscode-references-view/blob/d649d01d369e338bbe70c86e03f28269cbf87027/package.json#L26)。完成这个修改后，扩展就可以运行和测试了。

```json
"main": "./dist/extension.js"
```

（写 `./dist/extension` 或 `./dist/extension.js` 都可以。不打包时，`main` 通常是 `./out/extension.js`，即 `tsc` 的输出。）

---

<a id="tests"></a>
<a id="tests"></a>
## 测试（Tests）

> 扩展作者经常为扩展的源代码编写单元测试。在架构分层正确的情况下（扩展的源代码不依赖测试），webpack 和 esbuild 生成的包中不应该包含任何测试代码。要运行单元测试，只需要一次简单的编译。
>
> 把这些条目合并到 `package.json` 的 `scripts` 部分中：

```json
"scripts": {
    "compile-tests": "tsc -p . --outDir out",
    "pretest": "npm run compile-tests",
    "test": "vscode-test"
}
```

> `compile-tests` 脚本使用 TypeScript 编译器把扩展编译到 `out` 文件夹中。有了这些中间的 JavaScript 文件，下面这段 `launch.json` 的片段就足以运行测试。

```json
{
    "name": "Extension Tests",
    "type": "extensionHost",
    "request": "launch",
    "runtimeExecutable": "${execPath}",
    "args": [
        "--extensionDevelopmentPath=${workspaceFolder}",
        "--extensionTestsPath=${workspaceFolder}/out/test"
    ],
    "outFiles": [
        "${workspaceFolder}/out/test/**/*.js"
    ],
    "preLaunchTask": "npm: compile-tests"
}
```

> 这个运行测试的配置与不打包的扩展是一样的。没有理由打包单元测试，因为它们不是扩展发布部分的一部分。

**也就是说，项目中有两套构建产物：**

| 产物 | 由谁生成 | 用于 |
|---|---|---|
| `dist/extension.js` | esbuild / webpack | 运行和发布扩展（`main` 指向它） |
| `out/**/*.js` | `tsc --outDir out` | 运行测试 |

`pretest` 是 npm 的生命周期钩子：运行 `npm test` 时，会先自动运行 `pretest`。`vscode-test` 是 `@vscode/test-cli` 提供的命令，它读取 `.vscode-test.mjs` 配置文件来决定运行哪些测试（见 [测试扩展](./testing-extension.md)）。`--extensionTestsPath` 要指向一个导出 `run()` 函数的测试入口模块。

---

<a id="publishing"></a>
<a id="publishing"></a>
## 发布（Publishing）

> 在发布之前，你应该更新 `.vscodeignore` 文件。所有已经被打包进 `dist/extension.js` 文件的内容都可以排除，通常是 `out` 文件夹（如果你还没有删除它的话），以及最重要的 `node_modules` 文件夹。
>
> 一个典型的 `.vscodeignore` 文件看起来是这样的：

```text
.vscode
node_modules
out/
src/
tsconfig.json
webpack.config.js
esbuild.js
```

`.vscodeignore` 的语法和 `.gitignore` 相同，列出的文件和文件夹不会被打进 `.vsix` 安装包。打包后，运行时只需要 `dist/` 和 `package.json`（以及 README、图标等资源），源代码、配置文件、`node_modules` 都不再需要。可以用 `vsce ls` 查看最终会被打包的文件列表（见 [发布扩展](./publishing-extension.md)）。

---

<a id="migrate-an-existing-extension"></a>
## 迁移现有的扩展（Migrate an existing extension）

> 把一个现有的扩展迁移到使用 esbuild 或 webpack 很简单，过程与上面的入门指南类似。一个采用了 webpack 的真实示例，是 VS Code 的 References 视图，可以看这个 [pull request](https://github.com/microsoft/vscode-references-view/pull/50)。
>
> 在那里你可以看到：
>
> - 分别添加 `esbuild`，或 `webpack`、`webpack-cli` 和 `ts-loader` 作为 `devDependencies`。
> - 按上面所示更新 npm 脚本，以使用打包工具
> - 更新任务配置文件 `tasks.json`。
> - 添加并调整 `esbuild.js` 或 `webpack.config.js` 构建文件。
> - 更新 `.vscodeignore`，排除 `node_modules` 和中间输出文件。
> - 享受一个安装和加载都快得多的扩展吧！

别忘了还有一步：把 `package.json` 中的 `main` 改为指向 `dist/` 中的包文件（见 [运行扩展](#run-the-extension)）。

---

<a id="troubleshooting"></a>
## 故障排除（Troubleshooting）

<a id="minification"></a>
### 代码压缩（Minification）

> 以 `production` 模式打包时也会进行代码压缩。压缩通过去掉空白和注释、把变量和函数名改成难看但很短的名字来压缩源代码。使用 `Function.prototype.name` 的源代码的行为会有所不同，所以你可能需要禁用压缩。

例如代码中用 `MyClass.name` 或 `myFunction.name` 来生成日志或做判断，压缩后名字变成了 `a`、`t` 之类，逻辑就会出错。esbuild 可以加上 `keepNames: true` 选项保留名字，webpack 可以在 Terser 插件的配置中设置 `keep_classnames` / `keep_fnames`，而不必完全禁用压缩。

<a id="webpack-critical-dependencies"></a>
### webpack 关键依赖（webpack critical dependencies）

> 运行 webpack 时，你可能会遇到这样的警告：**Critical dependencies: the request of a dependency is an expression**。这类警告必须认真对待，很可能你的包无法正常工作。这条消息的意思是，webpack 无法静态地确定如何打包某个依赖。这通常是由动态的 `require` 语句引起的，例如 `require(someDynamicVariable)`。
>
> 要解决这个警告，你应该：
>
> - 尝试把依赖改为静态的，使它可以被打包。
> - 通过 `externals` 配置排除这个依赖。同时，在 `.vscodeignore` 中使用一个取反的 [glob 模式](https://code.visualstudio.com/docs/editor/glob-patterns)，确保这些 JavaScript 文件没有被排除在打包的扩展之外，例如 `!node_modules/mySpecialModule`。

警告的意思是“关键依赖：依赖的请求是一个表达式”。打包工具只能处理在打包时就能确定的 `require('固定字符串')`，`require(变量)` 要到运行时才知道加载哪个文件，打包工具没法提前把它合并进来。

第二种方法的完整配置：

```text
# .vscodeignore
node_modules/**
!node_modules/mySpecialModule/**
```

```js
// webpack.config.js
externals: {
    vscode: 'commonjs vscode',
    mySpecialModule: 'commonjs mySpecialModule'   // 不打包，运行时从 node_modules 中 require
}
```

这样这个模块不会被打进 `dist/extension.js`，而是作为普通文件随扩展发布，运行时照常 `require`。注意如果这个模块还有自己的依赖，那些依赖也要一并保留。原生模块（`.node` 文件）也需要这样处理。esbuild 中对应的是 `external` 数组。

---

<a id="next-steps"></a>
## 下一步（Next steps）

> - [扩展市场](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace) - 进一步了解 VS Code 的公共扩展市场。
> - [测试扩展](./testing-extension.md) - 为你的扩展项目添加测试，确保高质量。
> - [持续集成](./continuous-integration.md) - 了解如何在 Azure Pipelines 上运行扩展的 CI 构建。

---

## 本篇小结

```text
为什么打包：Web 版只能加载一个文件；安装包更小、激活更快

esbuild（推荐，快）
  esbuild.js：entryPoints、bundle、format: 'cjs'、platform: 'node'、outfile、external: ['vscode']
  esbuild 不做类型检查 → 另外运行 tsc --noEmit
  watch：npm-run-all -p watch:*；tasks.json 用 $esbuild-watch（需安装 connor4312.esbuild-problem-matchers）

webpack
  webpack.config.js：target（webworker / node）、entry、output、externals、ts-loader
  --mode development / production

共同要点
  package.json："main": "./dist/extension.js"；"vscode:prepublish" 在 vsce 打包前自动执行
  测试不打包：tsc 编译到 out/ 运行测试
  .vscodeignore：排除 src/、out/、node_modules/ 和构建配置
  vscode 模块必须 external；动态 require 的模块也要 external，并在 .vscodeignore 中用 ! 保留
```
