# Web 扩展（Web Extensions）

> 原文：[Web Extensions](https://code.visualstudio.com/api/extension-guides/web-extensions)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/web-extensions.md`（DateApproved: 10/7/2026）

> VS Code 可以作为编辑器运行在浏览器中。一个例子是 `github.dev` 用户界面：在 GitHub 中浏览仓库或拉取请求时，按下 `.`（句号键）就能打开它。在网页中使用 VS Code 时，已安装的扩展运行在浏览器中的一个扩展宿主里，它被称为“Web 扩展宿主”（web extension host）。能够在 Web 扩展宿主中运行的扩展，称为“Web 扩展”（web extension）。
>
> Web 扩展与普通扩展的结构相同，但由于运行时不同，它们不能使用为 Node.js 运行时编写的扩展的同一套代码运行。Web 扩展仍然可以访问完整的 VS Code API，但不能再使用 Node.js 的 API 和模块加载功能。相反，Web 扩展受到浏览器沙箱的限制，因此与普通扩展相比有一些[限制](#web-extension-main-file)。
>
> 桌面版 VS Code 也支持 Web 扩展运行时。如果你决定把扩展做成 Web 扩展，它就能在[网页版 VS Code](https://code.visualstudio.com/docs/remote/vscode-web)（包括 `vscode.dev` 和 `github.dev`）、桌面版以及 [GitHub Codespaces](https://code.visualstudio.com/docs/remote/codespaces) 等服务中使用。

**两种扩展宿主的区别：**

| | 普通扩展宿主 | Web 扩展宿主 |
|---|---|---|
| 运行环境 | Node.js | 浏览器的 Web Worker |
| 入口字段 | `package.json` 的 `main` | `package.json` 的 `browser` |
| VS Code API | 完整可用 | 完整可用 |
| Node.js API（`fs`、`child_process`、`path`……） | 可用 | **不可用** |
| 运行外部程序 | 可以 | **不可以** |
| 在哪里可用 | 桌面版、远程开发 | 网页版、桌面版、Codespaces |

**做成 Web 扩展的好处：** 一份代码同时支持网页版和桌面版。越来越多的用户会在浏览器中使用 VS Code（比如在 GitHub 上按 `.` 快速改代码），如果你的扩展不支持 Web，这些用户就用不了它。

---

<a id="web-extension-anatomy"></a>
## Web 扩展的结构（Web extension anatomy）

> Web 扩展的[结构和普通扩展一样](../get-started/extension-anatomy.md)。扩展清单（`package.json`）定义了扩展源代码的入口文件，并声明了扩展的贡献。
>
> 对于 Web 扩展，[主入口文件](#web-extension-main-file)由 `browser` 属性定义，而不是像普通扩展那样由 `main` 属性定义。
>
> `contributes` 属性对 Web 扩展和普通扩展的作用方式相同。
>
> 下面的例子展示了一个简单的 hello world 扩展的 `package.json`，它只在 Web 扩展宿主中运行（只有一个 `browser` 入口）：

```json
{
  "name": "helloworld-web-sample",
  "displayName": "helloworld-web-sample",
  "description": "HelloWorld example for VS Code in the browser",
  "version": "0.0.1",
  "publisher": "vscode-samples",
  "repository": "https://github.com/microsoft/vscode-extension-samples/helloworld-web-sample",
  "engines": {
    "vscode": "^1.74.0"
  },
  "categories": ["Other"],
  "activationEvents": [],
  "browser": "./dist/web/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "helloworld-web-sample.helloWorld",
        "title": "Hello World"
      }
    ]
  },
  "scripts": {
    "vscode:prepublish": "npm run package-web",
    "compile-web": "webpack",
    "watch-web": "webpack --watch",
    "package-web": "webpack --mode production --devtool hidden-source-map",
  },
  "devDependencies": {
    "@types/vscode": "^1.59.0",
    "ts-loader": "^9.2.2",
    "webpack": "^5.38.1",
    "webpack-cli": "^4.7.0",
    "@types/webpack-env": "^1.16.0",
    "process": "^0.11.10"
  }
}
```

和 [扩展的结构](../get-started/extension-anatomy.md) 中的普通扩展相比，区别只有两点：入口从 `main` 换成了 `browser`；编译用的是 webpack 打包（Web 扩展必须打包成单个文件，见下文）。

> **注意**：如果你的扩展面向 1.74 之前的 VS Code 版本，必须在 `activationEvents` 中显式写上 `onCommand:helloworld-web-sample.helloWorld`。

> 只有 `main` 入口、没有 `browser` 入口的扩展不是 Web 扩展。Web 扩展宿主会忽略它们，在扩展视图中也无法下载它们。

![扩展视图](images/web-extensions/extensions-view-item-disabled.png)

截图是在网页版 VS Code 的扩展视图中搜索 “git history” 的结果：Git History 扩展旁边有一个黄色警告图标，悬停提示显示 “The 'Git History' extension is not available in Visual Studio Code for the Web”（该扩展在网页版 VS Code 中不可用），因为它只有 `main` 入口。

> 只有声明式贡献的扩展（只有 `contributes`，没有 `main` 或 `browser`）可以是 Web 扩展。扩展作者无需做任何修改，它们就可以在[网页版 VS Code](https://code.visualstudio.com/docs/remote/vscode-web) 中安装和运行。只有声明式贡献的扩展的例子包括主题、语法和代码片段。
>
> 扩展可以同时有 `browser` 和 `main` 两个入口，以便在浏览器和 Node.js 两种运行时中运行。[把现有扩展更新为 Web 扩展](#update-existing-extensions-to-web-extensions)一节展示了如何迁移一个扩展，让它能在两种运行时中工作。
>
> [Web 扩展的启用](#web-extension-enablement)一节列出了用于判断一个扩展能否在 Web 扩展宿主中加载的规则。

| `package.json` 中有 | 是不是 Web 扩展 | 在哪里运行 |
|---|---|---|
| 只有 `contributes` | 是 | 任何地方 |
| 只有 `main` | 否 | 只在 Node.js 扩展宿主中 |
| 只有 `browser` | 是 | 只在 Web 扩展宿主中（桌面版也会用 Web 扩展宿主运行它） |
| `main` 和 `browser` 都有 | 是 | 桌面版用 `main`，网页版用 `browser` |

<a id="web-extension-main-file"></a>
### Web 扩展的主文件（Web extension main file）

> Web 扩展的主文件由 `browser` 属性定义。这个脚本在 Web 扩展宿主中运行，运行环境是一个[浏览器 WebWorker](https://developer.mozilla.org/docs/Web/API/Web_Workers_API)。它受到浏览器 Worker 沙箱的限制，与运行在 Node.js 运行时中的普通扩展相比有一些限制。

| 限制 | 说明 | 解决办法 |
|---|---|---|
| 不支持导入或 require 其他模块，`importScripts` 也不可用 | 因此代码必须打包成单个文件 | 用 webpack 或 esbuild 打包 |
| 只能通过 `require('vscode')` 加载 [VS Code API](https://code.visualstudio.com/api/references/vscode-api) | 这之所以可行，是因为有一个 `require` 的垫片（shim），但这个垫片不能用来加载其他扩展文件或其他 node 模块，只能用于 `require('vscode')` | 打包时把 `vscode` 设为外部模块（external） |
| Node.js 的全局变量和库，如 `process`、`os`、`setImmediate`、`path`、`util`、`url`，在运行时都不可用 | 不过可以用 webpack 之类的工具添加它们，[webpack 配置](#webpack-configuration)一节会解释如何做到 | 用 polyfill（替代实现） |
| 打开的工作区或文件夹位于虚拟文件系统上 | 访问工作区文件需要通过 `vscode.workspace.fs` 提供的 VS Code [文件系统](https://code.visualstudio.com/api/references/vscode-api#FileSystem) API | 见 [虚拟工作区](./virtual-workspaces.md) |
| [扩展上下文](https://code.visualstudio.com/api/references/vscode-api#ExtensionContext)中的位置（`ExtensionContext.extensionUri`）和存储位置（`ExtensionContext.storageUri`、`globalStorageUri`）也位于虚拟文件系统上 | 同样需要通过 `vscode.workspace.fs` 访问 | 用 `Uri` 而不是路径字符串 |
| 访问网络资源必须使用 [Fetch](https://developer.mozilla.org/docs/Web/API/Fetch_API) API | 被访问的资源需要支持[跨域资源共享](https://developer.mozilla.org/docs/HTTP/CORS)（CORS） | 用 `fetch`；服务器端要允许跨域 |
| 不能创建子进程或运行可执行程序 | 不过可以通过 [Worker](https://developer.mozilla.org/en-US/docs/Web/API/Worker) API 创建 Web Worker。[Web 扩展中的语言服务器协议](#language-server-protocol-in-web-extensions)一节介绍了如何用它运行语言服务器 | 用 Web Worker 代替子进程 |
| 和普通扩展一样，扩展的 `activate/deactivate` 函数需要以 `exports.activate = ...` 的方式导出 | | TypeScript 编译后的 `export function activate` 就是这种形式 |

**CORS（跨域资源共享）**：浏览器出于安全原因，默认不允许网页向其他网站发请求，除非那个网站在响应头中明确表示允许。在 Node.js 中没有这个限制，所以普通扩展可以随便请求任何接口；而 Web 扩展只能访问支持 CORS 的接口。

---

<a id="develop-a-web-extension"></a>
## 开发 Web 扩展（Develop a web extension）

> 幸运的是，TypeScript 和 webpack 这样的工具可以隐藏很多浏览器运行时的限制，让你可以用和编写普通扩展一样的方式编写 Web 扩展。Web 扩展和普通扩展常常可以由同一份源代码生成。
>
> 例如，`yo code` [生成器](https://www.npmjs.com/package/generator-code)创建的 `Hello Web Extension` 与普通扩展的唯一区别就是构建脚本。你可以使用提供的启动配置（通过 **Debug: Select and Start Debugging** 命令访问），像运行和调试传统的 Node.js 扩展一样，运行和调试生成的扩展。

---

<a id="create-a-web-extension"></a>
## 创建 Web 扩展（Create a web extension）

> 要搭建一个新的 Web 扩展，使用 `yo code` 并选择 **New Web Extension**。确保安装了最新版本的 [generator-code](https://www.npmjs.com/package/generator-code)（>= generator-code@1.6）。要更新生成器和 yo，运行 `npm i -g yo generator-code`。
>
> 创建的扩展包括扩展的源代码（一个显示 hello world 通知的命令）、`package.json` 清单文件，以及一个 webpack 或 esbuild 配置文件。
>
> 为了简单起见，我们假设你使用 `webpack` 作为打包工具。在文章的最后，我们也会解释选择 `esbuild` 时有哪些不同。

| 文件 | 作用 |
|---|---|
| `src/web/extension.ts` | 扩展的入口源代码文件。它和普通的 hello 扩展完全相同 |
| `package.json` | 扩展清单。它用 `browser` 属性指向入口文件；提供 `compile-web`、`watch-web` 和 `package-web` 脚本，分别用于编译、监视和打包 |
| `webpack.config.js` | webpack 配置文件，把扩展源代码编译并打包成单个文件 |
| `.vscode/launch.json` | 启动配置，在桌面版 VS Code 中用 Web 扩展宿主运行 Web 扩展和测试（不再需要设置 `extensions.webWorker`） |
| `.vscode/task.json` | 启动配置使用的构建任务。它使用 `npm run watch-web`，并依赖 webpack 专用的问题匹配器 `ts-webpack-watch` |
| `.vscode/extensions.json` | 列出提供问题匹配器的扩展。必须安装这些扩展，启动配置才能工作 |
| `tsconfig.json` | 定义与 `webworker` 运行时匹配的编译选项 |

（表中的 `.vscode/task.json` 是原文的写法，实际的文件名是 `tasks.json`。）

> [helloworld-web-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-web-sample) 中的源代码与生成器创建的代码类似。

<a id="webpack-configuration"></a>
### Webpack 配置（Webpack configuration）

> webpack 配置文件由 `yo code` 自动生成。它把扩展的源代码打包成单个 JavaScript 文件，以便加载到 Web 扩展宿主中。
>
> 稍后我们会解释如何使用 esbuild 作为打包工具，不过现在先从 webpack 开始。
>
> [webpack.config.js](https://github.com/microsoft/vscode-extension-samples/blob/main/helloworld-web-sample/webpack.config.js)

```js
const path = require('path');
const webpack = require('webpack');

/** @typedef {import('webpack').Configuration} WebpackConfig **/
/** @type WebpackConfig */
const webExtensionConfig = {
  mode: 'none', // 让代码尽可能接近原始的源代码（打包发布时会设为 'production'）
  target: 'webworker', // 扩展运行在 webworker 环境中
  entry: {
    'extension': './src/web/extension.ts', // Web 扩展主文件的源文件
    'test/suite/index': './src/web/test/suite/index.ts' // Web 扩展测试运行器的源文件
  },
  output: {
    filename: '[name].js',
    path: path.join(__dirname, './dist/web'),
    libraryTarget: 'commonjs',
    devtoolModuleFilenameTemplate: '../../[resource-path]'
  },
  resolve: {
    mainFields: ['browser', 'module', 'main'], // 在导入的 node 模块中优先查找 `browser` 入口
    extensions: ['.ts', '.js'], // 支持 ts 文件和 js 文件
    alias: {
      // 为 node 模块和源文件提供替代实现
    },
    fallback: {
      // Webpack 5 不再自动为 Node.js 核心模块提供 polyfill。
      // Node.js 核心模块的 polyfill 列表见
      // https://webpack.js.org/configuration/resolve/#resolvefallback
      'assert': require.resolve('assert')
    }
  },
  module: {
    rules: [{
      test: /\.ts$/,
      exclude: /node_modules/,
      use: [{
          loader: 'ts-loader'
      }]
    }]
  },
  plugins: [
    new webpack.ProvidePlugin({
      process: 'process/browser', // 为全局变量 `process` 提供一个垫片
    }),
  ],
  externals: {
    'vscode': 'commonjs vscode', // 不打包，因为它在运行时由 VS Code 提供
  },
  performance: {
    hints: false
  },
  devtool: 'nosources-source-map' // 生成指向原始源文件的 source map
};
module.exports = [webExtensionConfig];
```

> `webpack.config.js` 中一些重要的字段：

| 字段 | 作用 |
|---|---|
| `entry` | 扩展和测试套件的主入口。你可能需要调整这个路径，让它正确地指向扩展的入口。对于现有的扩展，可以先把它指向你当前在 `package.json` 的 `main` 中使用的文件。如果不想打包测试，可以省略测试套件那一项 |
| `output` | 编译后的文件放在哪里。`[name]` 会被替换成 `entry` 中使用的键名，所以生成的配置会产生 `dist/web/extension.js` 和 `dist/web/test/suite/index.js` |
| `target` | 编译后的 JavaScript 文件运行在哪种环境中。对于 Web 扩展，要设为 `webworker` |
| `resolve` | 可以为在浏览器中无法工作的 node 库添加别名（alias）和备用实现（fallback）。如果你使用了 `path` 这样的库，可以指定在 Web 编译环境中如何解析 `path`。比如可以指向项目中一个为 Web 定义 `path` 的文件：`path: path.resolve(__dirname, 'src/my-path-implementation-for-web.js')`；或者使用这个库的 Browserify 打包版本 `path-browserify`：`path: require.resolve('path-browserify')`。Node.js 核心模块的 polyfill 列表见 [webpack resolve.fallback](https://webpack.js.org/configuration/resolve/#resolvefallback) |
| `plugins` | 使用 [DefinePlugin 插件](https://webpack.js.org/plugins/define-plugin/) 为 Node.js 的全局变量（如 `process`）提供 polyfill |

（`plugins` 一行是原文的说法，但上面的配置中实际用的是 `ProvidePlugin`，而不是 `DefinePlugin`。两者都能用来处理全局变量：`ProvidePlugin` 在代码用到 `process` 时自动导入 `process/browser` 模块；`DefinePlugin` 则是在编译时把某个表达式直接替换成常量。）

**polyfill（垫片）**是指为当前环境中不存在的功能提供的替代实现。比如浏览器中没有 Node.js 的 `path` 模块，`path-browserify` 就是用浏览器能运行的代码重新实现了一遍 `path`。

`externals` 中的 `vscode` 很关键：`vscode` 模块是在运行时由 VS Code 提供的（见 [扩展的结构](../get-started/extension-anatomy.md)），不能也不需要打包进去。

---

<a id="test-your-web-extension"></a>
## 测试你的 Web 扩展（Test your web extension）

> 在发布到扩展市场之前，目前有三种方式测试 Web 扩展。
>
> - 使用桌面版 VS Code，加上 `--extensionDevelopmentKind=web` 选项，在 VS Code 中运行的 Web 扩展宿主里运行你的 Web 扩展。
> - 使用 [@vscode/test-web](https://github.com/microsoft/vscode-test-web) node 模块打开一个浏览器，其中包含由本地服务器提供的、带有你的扩展的网页版 VS Code。
> - 把你的扩展[旁加载](#test-your-web-extension-in-vscode.dev)到 [vscode.dev](https://vscode.dev) 上，在真实的环境中查看你的扩展。

| 方式 | 优点 | 缺点 |
|---|---|---|
| 桌面版 + `--extensionDevelopmentKind=web` | 调试体验和普通扩展一样（可以打断点） | 不是真正的浏览器环境 |
| `@vscode/test-web` | 真正的浏览器，可以在 Chromium、Firefox、WebKit 中测试，适合自动化测试 | 调试稍麻烦 |
| 旁加载到 vscode.dev | 完全真实的线上环境 | 很难调试，适合发布前最后检查 |

**旁加载（sideload）**是指不通过扩展市场，直接从本地安装扩展。

<a id="test-your-web-extension-in-vs-code-running-on-desktop"></a>
### 在桌面版 VS Code 中测试 Web 扩展（Test your web extension in VS Code running on desktop）

> 为了沿用现有的扩展开发体验，桌面版 VS Code 支持在普通的 Node.js 扩展宿主之外，同时运行一个 Web 扩展宿主。
>
> 使用 **New Web Extension** 生成器提供的 `pwa-extensionhost` 启动配置：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Web Extension in VS Code",
      "type": "pwa-extensionHost",
      "debugWebWorkerHost": true,
      "request": "launch",
      "args": [
        "--extensionDevelopmentPath=${workspaceFolder}",
        "--extensionDevelopmentKind=web"
      ],
      "outFiles": [
        "${workspaceFolder}/dist/web/**/*.js"
      ],
      "preLaunchTask": "npm: watch-web"
    }
  ]
}
```

（`pwa-extensionHost` 是旧的调试类型名称，新版本中直接写 `extensionHost` 即可，本篇后面的测试配置用的就是 `extensionHost`。）

| 配置项 | 作用 |
|---|---|
| `"debugWebWorkerHost": true` | 调试运行在 Web Worker 中的扩展宿主 |
| `--extensionDevelopmentPath` | 要加载的开发中的扩展 |
| `--extensionDevelopmentKind=web` | **关键**：让扩展在 Web 扩展宿主中运行，而不是 Node.js 扩展宿主 |
| `outFiles` | 编译后的文件位置，用于把断点映射回源代码 |
| `preLaunchTask` | 启动前先运行的任务（编译） |

> 它使用任务 `npm: watch-web`，通过调用 `npm run watch-web` 来编译扩展。这个任务应该在 `tasks.json` 中定义：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "type": "npm",
      "script": "watch-web",
      "group": "build",
      "isBackground": true,
      "problemMatcher": [
        "$ts-webpack-watch"
      ]
    }
  ]
}
```

> `$ts-webpack-watch` 是一个可以解析 webpack 工具输出的问题匹配器。它由 [TypeScript + Webpack Problem Matchers](https://marketplace.visualstudio.com/items?itemName=eamodio.tsl-problem-matcher) 扩展提供。

**问题匹配器（problem matcher）**用来解析命令行工具的输出，把其中的错误提取到“问题”面板中。对于 `isBackground: true` 的监视任务，它还要能判断“编译完成了”，VS Code 才知道什么时候可以启动调试。

> 在启动的**扩展开发宿主**实例中，Web 扩展会在一个 Web 扩展宿主中可用并运行。运行 `Hello World` 命令来激活扩展。
>
> 打开**正在运行的扩展**视图（命令：**Developer: Show Running Extensions**），查看哪些扩展正在 Web 扩展宿主中运行。

<a id="test-your-web-extension-in-a-browser-using-vscodetest-web"></a>
### 使用 @vscode/test-web 在浏览器中测试 Web 扩展（Test your web extension in a browser using @vscode/test-web）

> [@vscode/test-web](https://github.com/microsoft/vscode-test-web) node 模块提供了一个命令行工具和 API，用于在浏览器中测试 Web 扩展。
>
> 这个 node 模块贡献了一个 npm 可执行命令 `vscode-test-web`，可以从命令行打开网页版 VS Code：
>
> - 它把 VS Code 的网页版文件下载到 `.vscode-test-web` 中。
> - 在 `localhost:3000` 上启动一个本地服务器。
> - 打开一个浏览器（Chromium、Firefox 或 Webkit）。
>
> 你可以从命令行运行它：

```bash
npx @vscode/test-web --extensionDevelopmentPath=$extensionFolderPath $testDataPath
```

> 或者更好的做法是，把 `@vscode/test-web` 作为开发依赖添加到你的扩展中，并在一个脚本中调用它：

```json
  "devDependencies": {
    "@vscode/test-web": "*"
  },
  "scripts": {
    "open-in-browser": "vscode-test-web --extensionDevelopmentPath=. ."
  }
```

`vscode-test-web --extensionDevelopmentPath=. .` 中，第一个 `.` 表示扩展在当前目录，最后一个 `.` 表示在浏览器中打开当前目录作为工作区。之后执行 `npm run open-in-browser` 即可。

> 更多命令行选项请查看 [@vscode/test-web 的 README](https://www.npmjs.com/package/@vscode/test-web)：

| 选项 | 参数说明 |
|-----|-----|
| --browserType | 要启动的浏览器：`chromium`（默认）、`firefox` 或 `webkit` |
| --extensionDevelopmentPath | 指向一个要包含的、正在开发的扩展的路径。 |
| --extensionTestsPath | 指向要运行的测试模块的路径。 |
| --permission | 授予打开的浏览器的权限：例如 `clipboard-read`、`clipboard-write`。<br>参见[完整的选项列表](https://playwright.dev/docs/api/class-browsercontext#browser-context-grant-permissions)。这个参数可以提供多次。 |
| --folder-uri | 让 VS Code 打开的工作区的 URI。如果提供了 `folderPath`，则忽略此项 |
| --extensionPath | 指向一个文件夹的路径，其中包含要额外包含的扩展。<br>这个参数可以提供多次。 |
| folderPath | 让 VS Code 打开的本地文件夹。<br>文件夹的内容会以虚拟文件系统的形式提供，并作为工作区打开。 |

> VS Code 的网页版文件会被下载到 `.vscode-test-web` 文件夹中。你应该把它添加到 `.gitignore` 文件中。

<a id="test-your-web-extension-in-vscodedev"></a>
<a id="test-your-web-extension-in-vscode.dev"></a>
### 在 vscode.dev 中测试 Web 扩展（Test your web extension in vscode.dev）

> 在把扩展发布给所有人在网页版 VS Code 中使用之前，你可以在真实的 [vscode.dev](https://vscode.dev) 环境中验证扩展的行为。
>
> 要在 vscode.dev 上看到你的扩展，首先需要在你的电脑上托管它，供 vscode.dev 下载和运行。
>
> 首先，你需要[安装 `mkcert`](https://github.com/FiloSottile/mkcert#installation)。
>
> 然后，把 `localhost.pem` 和 `localhost-key.pem` 文件生成到一个不会丢失它们的位置（例如 `$HOME/certs`）：

```text
$ mkdir -p $HOME/certs
$ cd $HOME/certs
$ mkcert -install
$ mkcert localhost
```

**为什么要生成证书？** vscode.dev 是 `https` 网站，浏览器不允许 `https` 网页从不安全的 `http` 地址加载内容。所以本地服务器也必须用 `https`，`mkcert` 就是用来生成一个本机信任的 `localhost` 证书的工具。

> 然后，在扩展的路径下，运行 `npx serve` 启动一个 HTTP 服务器：

```text
$ npx serve --cors -l 5000 --ssl-cert $HOME/certs/localhost.pem --ssl-key $HOME/certs/localhost-key.pem
npx: installed 78 in 2.196s

   ┌────────────────────────────────────────────────────┐
   │                                                    │
   │   Serving!                                         │
   │                                                    │
   │   - Local:            https://localhost:5000       │
   │   - On Your Network:  https://172.19.255.26:5000   │
   │                                                    │
   │   Copied local address to clipboard!               │
   │                                                    │
   └────────────────────────────────────────────────────┘
```

`--cors` 允许跨域访问（vscode.dev 要从另一个网站读取你的扩展），`-l 5000` 指定端口。

> 最后，打开 [vscode.dev](https://vscode.dev)，从命令面板（`Ctrl+Shift+P`）中运行 **Developer: Install Extension From Location...**，粘贴上面的 URL（示例中是 `https://localhost:5000`），然后选择**安装**。

**查看日志（Check the logs）**

> 你可以在浏览器开发者工具的控制台中查看日志，看到扩展的错误、状态和日志。
>
> 你可能还会看到来自 vscode.dev 本身的其他日志。此外，你不能方便地设置断点，也看不到扩展的源代码。这些限制让在 vscode.dev 中调试并不是最愉快的体验，所以我们建议先用前两种方式进行测试，然后再旁加载到 vscode.dev 上。旁加载很适合作为发布扩展之前的最后一次完整性检查。

---

<a id="web-extension-tests"></a>
## Web 扩展的测试（Web extension tests）

> Web 扩展支持测试，实现方式与普通扩展的测试类似。请参阅[测试扩展](../working-with-extensions/testing-extension.md)一文，了解扩展测试的基本结构。
>
> [@vscode/test-web](https://github.com/microsoft/vscode-test-web) node 模块相当于 [@vscode/test-electron](https://github.com/microsoft/vscode-test)（以前叫 `vscode-test`）。它让你可以从命令行在 Chromium、Firefox 和 Safari 上运行扩展测试。
>
> 这个工具会执行以下步骤：
>
> 1. 从一个本地 Web 服务器启动一个网页版 VS Code 编辑器。
> 2. 打开指定的浏览器。
> 3. 运行提供的测试运行器脚本。
>
> 你可以在持续构建中运行这些测试，确保扩展在所有浏览器上都能工作。
>
> 测试运行器脚本运行在 Web 扩展宿主中，和 [Web 扩展主文件](#web-extension-main-file)有同样的限制：
>
> - 所有文件都要打包成一个文件。它应该包含测试运行器（例如 Mocha）和所有测试（通常是 `*.test.ts`）。
> - 只支持 `require('vscode')`。
>
> `yo code` Web 扩展生成器创建的 [webpack 配置](https://github.com/microsoft/vscode-extension-samples/blob/main/helloworld-web-sample/webpack.config.js)中，有一个用于测试的部分。它期望测试运行器脚本位于 `./src/web/test/suite/index.ts`。提供的[测试运行器脚本](https://github.com/microsoft/vscode-extension-samples/blob/main/helloworld-web-sample/src/web/test/suite/index.ts)使用了 Web 版的 Mocha，并包含了 webpack 特有的语法，用来导入所有测试文件。

```ts
require('mocha/mocha'); // 导入 mocha 的 Web 版本

export function run(): Promise<void> {

  return new Promise((c, e) => {
    mocha.setup({
      ui: 'tdd',
      reporter: undefined
    });

    // 把当前目录中所有匹配 `*.test` 的文件打包进来
    const importAll = (r: __WebpackModuleApi.RequireContext) => r.keys().forEach(r);
    importAll(require.context('.', true, /\.test$/));

    try {
      // 运行 mocha 测试
      mocha.run(failures => {
        if (failures > 0) {
          e(new Error(`${failures} tests failed.`));
        } else {
          c();
        }
      });
    } catch (err) {
      console.error(err);
      e(err);
    }
  });
}
```

- **Mocha** 是一个 JavaScript 测试框架，`ui: 'tdd'` 表示使用 `suite` / `test` 风格的写法（另一种是 `describe` / `it` 的 `bdd` 风格）。
- **`require.context`** 是 webpack 特有的语法：在打包时找出目录中所有匹配正则的文件，并把它们都打包进来。因为 Web 扩展不能在运行时动态加载文件，所以要用这种方式在打包时就把所有测试文件“塞”进同一个文件里。
- `run` 函数返回一个 Promise：测试全部通过时 resolve，有失败时 reject。测试工具通过它得知测试结果。

> 要从命令行运行 Web 测试，把下面的内容添加到你的 `package.json` 中，然后用 `npm test` 运行它。

```json
  "devDependencies": {
    "@vscode/test-web": "*"
  },
  "scripts": {
    "test": "vscode-test-web --extensionDevelopmentPath=. --extensionTestsPath=dist/web/test/suite/index.js"
  }
```

> 要让 VS Code 打开一个包含测试数据的文件夹，把一个本地文件夹路径（`folderPath`）作为最后一个参数传入。
>
> 要在桌面版 VS Code（Insiders）中运行（和调试）扩展测试，使用 `Extension Tests in VS Code` 启动配置：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Extension Tests in VS Code",
      "type": "extensionHost",
      "debugWebWorkerHost": true,
      "request": "launch",
      "args": [
        "--extensionDevelopmentPath=${workspaceFolder}",
        "--extensionDevelopmentKind=web",
        "--extensionTestsPath=${workspaceFolder}/dist/web/test/suite/index"
      ],
      "outFiles": [
        "${workspaceFolder}/dist/web/**/*.js"
      ],
      "preLaunchTask": "npm: watch-web"
    }
  ]
}
```

和前面运行扩展的配置相比，只多了一个 `--extensionTestsPath` 参数，指向编译后的测试运行器。

---

<a id="publish-a-web-extension"></a>
## 发布 Web 扩展（Publish a web extension）

> Web 扩展与其他扩展一起托管在[扩展市场](https://marketplace.visualstudio.com/vscode)上。
>
> 一定要使用最新版本的 `vsce` 发布你的扩展。`vsce` 会给所有 Web 扩展打上标记。为此，`vsce` 使用的是 [Web 扩展的启用](#web-extension-enablement)一节中列出的规则。

发布的具体步骤见 [发布扩展](../working-with-extensions/publishing-extension.md)。

---

<a id="update-existing-extensions-to-web-extensions"></a>
## 把现有扩展更新为 Web 扩展（Update existing extensions to Web extensions）

<a id="extension-without-code"></a>
### 没有代码的扩展（Extension without code）

> 没有代码、只有贡献点的扩展（例如主题、代码片段和基础的语言扩展）不需要任何修改。它们可以在 Web 扩展宿主中运行，并且可以从扩展视图中安装。
>
> 不需要重新发布，但在发布扩展的新版本时，一定要使用最新版本的 `vsce`。

<a id="migrate-extension-with-code"></a>
### 迁移有代码的扩展（Migrate extension with code）

> 有源代码的扩展（由 `main` 属性定义）需要提供一个 [Web 扩展主文件](#web-extension-main-file)，并在 `package.json` 中设置 `browser` 属性。
>
> 按照以下步骤，为浏览器环境重新编译扩展代码：
>
> - 添加一个 webpack 配置文件，如 [webpack 配置](#webpack-configuration)一节所示。如果你已经有一个用于 Node.js 扩展代码的 webpack 文件，可以为 Web 新增一个部分。可以参考 [vscode-css-formatter](https://github.com/aeschli/vscode-css-formatter/blob/master/webpack.config.js) 这个例子。
> - 添加 `launch.json` 和 `tasks.json` 文件，如[测试你的 Web 扩展](#test-your-web-extension)一节所示。
> - 在 webpack 配置文件中，把输入文件设为现有的 Node.js 主文件，或者为 Web 扩展创建一个新的主文件。
> - 在 `package.json` 中，添加 `browser` 和 `scripts` 属性，如 [Web 扩展的结构](#web-extension-anatomy)一节所示。
> - 运行 `npm run compile-web` 调用 webpack，看看哪些地方需要修改，才能让你的扩展在 Web 中运行。

第一步“新增一个部分”是指 `module.exports` 导出一个配置数组，一个用于 Node.js（`target: 'node'`，输出给 `main`），一个用于 Web（`target: 'webworker'`，输出给 `browser`），像上面的 webpack 配置那样 `module.exports = [nodeConfig, webConfig]`。

> 为了尽可能多地复用源代码，这里有一些技巧：
>
> - 要为 `path` 这样的 Node.js 核心模块提供 polyfill，在 [resolve.fallback](https://webpack.js.org/configuration/resolve/#resolvefallback) 中添加一项。
> - 要提供 `process` 这样的 Node.js 全局变量，使用 [DefinePlugin 插件](https://webpack.js.org/plugins/define-plugin)。
> - 使用在浏览器和 node 运行时中都能工作的 node 模块。node 模块可以通过同时定义 `browser` 和 `main` 两个入口做到这一点。webpack 会自动使用与它的目标匹配的那一个。这样做的 node 模块的例子有 [request-light](https://github.com/microsoft/node-request-light) 和 [@vscode/l10n](https://github.com/microsoft/vscode-l10n)。
> - 要为 node 模块或源文件提供替代实现，使用 [resolve.alias](https://webpack.js.org/configuration/resolve/#resolvealias)。
> - 把代码分成浏览器部分、Node.js 部分和公共部分。在公共部分中，只使用在浏览器和 Node.js 运行时中都能工作的代码。为在 Node.js 和浏览器中实现不同的功能创建抽象。
> - 注意 `path`、`URI.file`、`context.extensionPath`、`rootPath`、`uri.fsPath` 的用法。在网页版 VS Code 使用的虚拟工作区（非文件系统）中，它们都无法工作。应该改用 `URI.parse`、`context.extensionUri` 创建的 URI。[vscode-uri](https://www.npmjs.com/package/vscode-uri) node 模块提供了 `joinPath`、`dirName`、`baseName`、`extName`、`resolvePath`。
> - 注意 `fs` 的用法。用 vscode 的 `workspace.fs` 替换它。

“分成浏览器部分、Node.js 部分和公共部分”的典型目录结构：

```text
src/
  common/         ← 两边通用的逻辑（只用 VS Code API 和纯 JS）
    feature.ts
  node/
    extension.ts  ← Node.js 入口（main），可以用 fs、child_process
  web/
    extension.ts  ← 浏览器入口（browser），只用 fetch、Web Worker 等
```

两个入口都调用 `common` 中的代码，只在必须用到平台特有功能的地方各自实现。这里列出的 `fsPath`、`fs` 等问题，就是 [虚拟工作区](./virtual-workspaces.md#review-that-the-extension-code-is-ready-for-virtual-resources) 一篇中讲过的那些。

> 当扩展在 Web 中运行时，提供较少的功能是可以接受的。使用 [when 子句上下文](../references/when-clause-contexts.md) 来控制在 Web 上的虚拟工作区中运行时，哪些命令、视图和任务可用或隐藏。
>
> - 使用 `virtualWorkspace` 上下文变量，判断当前工作区是否是一个非文件系统的工作区。
> - 使用 `resourceScheme` 检查当前资源是否是 `file` 资源。
> - 如果存在平台 shell，使用 `shellExecutionSupported`。
> - 实现替代的命令处理函数，显示一个对话框，解释为什么这个命令不适用。

`shellExecutionSupported` 在 [任务提供者](./task-provider.md#when-clause) 中介绍过。

> Web Worker 可以作为派生进程的替代方案。我们已经把几个语言服务器更新为以 Web 扩展的形式运行，包括内置的 [JSON](https://github.com/microsoft/vscode/tree/main/extensions/json-language-features)、[CSS](https://github.com/microsoft/vscode/tree/main/extensions/css-language-features) 和 [HTML](https://github.com/microsoft/vscode/tree/main/extensions/html-language-features) 语言服务器。下面的[语言服务器协议](#language-server-protocol-in-web-extensions)一节给出了更多细节。
>
> 浏览器运行时环境只支持执行 JavaScript 和 [WebAssembly](https://webassembly.org/)。用其他编程语言编写的库需要进行交叉编译，例如，有工具可以把 [C/C++](https://developer.mozilla.org/en-US/docs/WebAssembly/C_to_wasm) 和 [Rust](https://developer.mozilla.org/en-US/docs/WebAssembly/Rust_to_wasm) 编译成 WebAssembly。例如，[vscode-anycode](https://github.com/microsoft/vscode-anycode) 扩展使用了 [tree-sitter](https://www.npmjs.com/package/tree-sitter)，它是被编译成 WebAssembly 的 C/C++ 代码。

**WebAssembly（简称 Wasm）**是一种可以在浏览器中高效运行的二进制格式。用 C、C++、Rust 等语言写的程序，可以编译成 Wasm 后在浏览器中运行。这是 Web 扩展中使用非 JavaScript 代码的唯一途径。

<a id="language-server-protocol-in-web-extensions"></a>
### Web 扩展中的语言服务器协议（Language Server Protocol in web extensions）

> [vscode-languageserver-node](https://github.com/Microsoft/vscode-languageserver-node) 是[语言服务器协议](https://microsoft.github.io/language-server-protocol)（LSP）的一个实现，它被用作 [JSON](https://github.com/microsoft/vscode/tree/main/extensions/json-language-features)、[CSS](https://github.com/microsoft/vscode/tree/main/extensions/css-language-features) 和 [HTML](https://github.com/microsoft/vscode/tree/main/extensions/html-language-features) 等语言服务器实现的基础。
>
> 从 3.16.0 开始，客户端和服务器也提供了浏览器实现。服务器可以运行在一个 Web Worker 中，连接基于 Web Worker 的 `postMessage` 协议。
>
> 浏览器的客户端在 'vscode-languageclient/browser' 中：

```typescript
import { LanguageClient } from `vscode-languageclient/browser`
```

（原文代码中模块名用的是反引号，这在 `import` 语句中是语法错误，应该写成普通的引号：`import { LanguageClient } from 'vscode-languageclient/browser';`。）

> 服务器在 `vscode-languageserver/browser` 中。
>
> [lsp-web-extension-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-web-extension-sample) 展示了这是如何工作的。

| | Node.js 版 | 浏览器版 |
|---|---|---|
| 客户端（在扩展中） | `vscode-languageclient/node` | `vscode-languageclient/browser` |
| 服务器 | `vscode-languageserver/node` | `vscode-languageserver/browser` |
| 服务器运行在 | 子进程 | Web Worker |
| 通信方式 | stdin/stdout、IPC 等 | `postMessage` |

语言服务器的完整开发方法见 [语言服务器扩展指南](../language-extensions/language-server-extension-guide.md)。

---

<a id="web-extension-enablement"></a>
## Web 扩展的启用（Web extension enablement）

> 如果满足以下条件，VS Code 会自动把一个扩展视为 Web 扩展：
>
> - 扩展清单（`package.json`）中有 `browser` 入口。
> - 扩展清单中没有 `main` 入口，并且没有以下任何一个贡献点：`localizations`、`debuggers`、`terminal`、`typescriptServerPlugins`。
>
> 如果扩展想提供一个也能在 Web 扩展宿主中工作的调试器或终端，就需要定义一个 `browser` 入口。

第二条中的几个贡献点，即使不写代码，也隐含着需要 Node.js 环境：比如 `debuggers` 要启动一个调试适配器进程（见 [调试器扩展](./debugger-extension.md)）。

---

<a id="using-esbuild"></a>
## 使用 ESBuild（Using ESBuild）

> 如果你想用 esbuild 代替 webpack，请这样做：
>
> 添加一个 `esbuild.js` 构建脚本：

```js
const esbuild = require('esbuild');
const glob = require('glob');
const path = require('path');
const polyfill = require('@esbuild-plugins/node-globals-polyfill');

const production = process.argv.includes('--production');
const watch = process.argv.includes('--watch');

async function main() {
	const ctx = await esbuild.context({
		entryPoints: [
			'src/web/extension.ts',
			'src/web/test/suite/extensionTests.ts'
		],
		bundle: true,
		format: 'cjs',
		minify: production,
		sourcemap: !production,
		sourcesContent: false,
		platform: 'browser',
		outdir: 'dist/web',
		external: ['vscode'],
		logLevel: 'warning',
		// 把 Node.js 的 global 映射为浏览器的 globalThis
		define: {
			global: 'globalThis',
		},

		plugins: [
			polyfill.NodeGlobalsPolyfillPlugin({
				process: true,
				buffer: true,
			}),
			testBundlePlugin,
			esbuildProblemMatcherPlugin, /* 添加到 plugins 数组的末尾 */
		],
	});
	if (watch) {
		await ctx.watch();
	} else {
		await ctx.rebuild();
		await ctx.dispose();
	}
}

/**
 * 对于 Web 扩展，所有测试（包括测试运行器）都需要打包成
 * 一个导出了 `run` 函数的单一模块。
 * 这个插件实现了一个虚拟文件 extensionTests.ts，把这些全部打包在一起。
 * @type {import('esbuild').Plugin}
 */
const testBundlePlugin = {
	name: 'testBundlePlugin',
	setup(build) {
		build.onResolve({ filter: /[\/\\]extensionTests\.ts$/ }, args => {
			if (args.kind === 'entry-point') {
				return { path: path.resolve(args.path) };
			}
		});
		build.onLoad({ filter: /[\/\\]extensionTests\.ts$/ }, async args => {
			const testsRoot = path.join(__dirname, 'src/web/test/suite');
			const files = await glob.glob('*.test.{ts,tsx}', { cwd: testsRoot, posix: true });
			return {
				contents:
					`export { run } from './mochaTestRunner.ts';` +
					files.map(f => `import('./${f}');`).join(''),
				watchDirs: files.map(f => path.dirname(path.resolve(testsRoot, f))),
				watchFiles: files.map(f => path.resolve(testsRoot, f))
			};
		});
	}
};

/**
 * 这个插件接入构建过程，以 Visual Studio Code 中的问题匹配器
 * 能够理解的格式打印错误。
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
	},
};

main().catch(e => {
	console.error(e);
	process.exit(1);
});
```

> 这个构建脚本做了以下事情：
>
> - 用 esbuild 创建一个构建上下文。上下文的配置是：
>   - 把 `src/web/extension.ts` 中的代码打包成单个文件 `dist/web/extension.js`。
>   - 把所有测试（包括测试运行器 mocha）打包成单个文件 `dist/web/test/suite/extensionTests.js`。
>   - 如果传入了 `--production` 标志，就压缩代码。
>   - 除非传入了 `--production` 标志，否则生成 source map。
>   - 把 'vscode' 模块排除在打包之外（因为它由 VS Code 运行时提供）。
>   - 为 `process` 和 `buffer` 创建 polyfill。
>   - 使用 esbuildProblemMatcherPlugin 插件报告导致打包无法完成的错误。这个插件以 `esbuild` 问题匹配器能识别的格式输出错误，这个问题匹配器同样需要作为扩展安装。
>   - 使用 testBundlePlugin 实现一个测试主文件（`extensionTests.js`），它引用了所有的测试文件和 mocha 测试运行器 `mochaTestRunner.js`。
> - 如果传入了 `--watch` 标志，它就开始监视源文件的变化，并在检测到变化时重新打包。

`testBundlePlugin` 的作用和前面 webpack 测试脚本中的 `require.context` 一样：esbuild 没有 `require.context` 这种语法，所以用一个插件“凭空”生成一个 `extensionTests.ts` 文件，内容是导出测试运行器的 `run`，再导入找到的所有 `*.test.ts` 文件。

> esbuild 可以直接处理 TypeScript 文件。不过，esbuild 只是简单地去掉所有的类型声明，而不做任何类型检查。只有语法错误会被报告，并可能导致 esbuild 失败。
>
> 因此，我们单独运行 TypeScript 编译器（`tsc`）来检查类型，但不输出任何代码（使用 `--noEmit` 标志）。

**esbuild 和 webpack 的取舍：** esbuild 速度极快（通常快几十倍），但它不检查 TypeScript 的类型错误，所以要额外用 `tsc --noEmit` 检查类型。webpack 配合 `ts-loader` 编译时会同时检查类型，但速度较慢。

> `package.json` 中的 `scripts` 部分现在是这样的：

```json
  "scripts": {
    "vscode:prepublish": "npm run package-web",
    "compile-web": "npm run check-types && node esbuild.js",
    "watch-web": "npm-run-all -p watch-web:*",
    "watch-web:esbuild": "node esbuild.js --watch",
    "watch-web:tsc": "tsc --noEmit --watch --project tsconfig.json",
    "package-web": "npm run check-types && node esbuild.js --production",
    "check-types": "tsc --noEmit",
    "pretest": "npm run compile-web",
    "test": "vscode-test-web --browserType=chromium --extensionDevelopmentPath=. --extensionTestsPath=dist/web/test/suite/extensionTests.js",
    "run-in-browser": "vscode-test-web --browserType=chromium --extensionDevelopmentPath=. ."
  }
```

> `npm-run-all` 是一个 node 模块，它可以并行运行名称匹配给定前缀的脚本。对我们来说，它运行 `watch-web:esbuild` 和 `watch-web:tsc` 两个脚本。你需要把 `npm-run-all` 添加到 `package.json` 的 `devDependencies` 部分中。

也就是说，开发时 `npm run watch-web` 会同时启动两个监视进程：一个用 esbuild 快速打包，一个用 tsc 检查类型。

> 下面的 `tasks.json` 文件会为每个监视任务提供单独的终端：

```json
{
	"version": "2.0.0",
	"tasks": [
		{
			"label": "watch-web",
			"dependsOn": [
				"npm: watch-web:tsc",
				"npm: watch-web:esbuild"
			],
			"presentation": {
				"reveal": "never"
			},
			"group": {
				"kind": "build",
				"isDefault": true
			},
			"runOptions": {
				"runOn": "folderOpen"
			}
		},
		{
			"type": "npm",
			"script": "watch-web:esbuild",
			"group": "build",
			"problemMatcher": "$esbuild-watch",
			"isBackground": true,
			"label": "npm: watch-web:esbuild",
			"presentation": {
				"group": "watch",
				"reveal": "never"
			}
		},
		{
			"type": "npm",
			"script": "watch-web:tsc",
			"group": "build",
			"problemMatcher": "$tsc-watch",
			"isBackground": true,
			"label": "npm: watch-web:tsc",
			"presentation": {
				"group": "watch",
				"reveal": "never"
			}
		},
		{
			"label": "compile",
			"type": "npm",
			"script": "compile-web",
			"problemMatcher": [
				"$tsc",
				"$esbuild"
			]
		}
	]
}
```

| 配置项 | 作用 |
|---|---|
| `dependsOn` | `watch-web` 任务本身不做事，只是同时启动它依赖的两个任务 |
| `"runOn": "folderOpen"` | 打开这个文件夹时自动运行（会询问用户是否允许） |
| `"presentation": { "reveal": "never" }` | 运行时不自动显示终端面板 |
| `"presentation": { "group": "watch" }` | 同一组的任务在终端中并排显示 |
| `$esbuild-watch` / `$tsc-watch` | 分别解析 esbuild 和 tsc 输出的问题匹配器 |

> 这是 esbuild 构建脚本中引用的 `mochaTestRunner.js`：

```ts
// 导入浏览器版的 mocha，定义全局的 `mocha`。
import 'mocha/mocha';

mocha.setup({
	ui: 'tdd',
	reporter: undefined
});

export function run(): Promise<void> {

	return new Promise((c, e) => {
		try {
			// 运行 mocha 测试
			mocha.run(failures => {
				if (failures > 0) {
					e(new Error(`${failures} tests failed.`));
				} else {
					c();
				}
			});
		} catch (err) {
			console.error(err);
			e(err);
		}
	});
}
```

和 webpack 版本的测试运行器相比，它不再负责导入测试文件（这件事由 `testBundlePlugin` 生成的虚拟文件完成了）。另外 `mocha.setup` 被移到了模块顶层，确保在测试文件导入、调用 `suite()` 之前就已经完成设置。

---

<a id="samples"></a>
## 示例（Samples）

> - [helloworld-web-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-web-sample)
> - [lsp-web-extension-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/lsp-web-extension-sample)

---

## 本篇小结

```text
Web 扩展 = 入口写在 browser（而不是 main）的扩展，运行在浏览器的 Web Worker 中

限制（与 Node.js 扩展相比）
  只能 require('vscode')        → 必须打包成单个文件（webpack / esbuild），vscode 设为 external
  没有 Node.js API（fs、path…）  → polyfill（resolve.fallback / ProvidePlugin）或改用 VS Code API
  文件都在虚拟文件系统上          → workspace.fs + Uri（不用 fsPath、extensionPath）
  网络请求                       → fetch（需要 CORS）
  不能启动进程                    → Web Worker；其他语言 → WebAssembly

是否为 Web 扩展：有 browser，或者没有 main 且没有 localizations / debuggers / terminal / typescriptServerPlugins

测试
  桌面版：launch.json 中 --extensionDevelopmentKind=web（可打断点）
  浏览器：@vscode/test-web（npx vscode-test-web …）
  线上：mkcert + npx serve --cors → vscode.dev 中 Developer: Install Extension From Location...

迁移：分 common / node / web 三部分；main 和 browser 两个入口共存
LSP：vscode-languageclient/browser + vscode-languageserver/browser（服务器跑在 Web Worker 中）
```
