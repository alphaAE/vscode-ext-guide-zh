# 扩展的结构（Extension Anatomy）

> 原文：[Extension Anatomy](https://code.visualstudio.com/api/get-started/extension-anatomy)
> 源文件：`microsoft/vscode-docs` → `api/get-started/extension-anatomy.md`（DateApproved: 10/7/2026）

> 上一篇中，你已经让一个基础扩展跑起来了。那它在底层是怎么工作的呢？

[上一篇](./your-first-extension.md) 只讲了操作，这一篇讲原理。**这是整个入门部分最重要的一篇**：这里的三个概念贯穿后面所有章节，后面每学一个新功能，基本都是在这个框架里填充新内容。

---

## 一、Hello World 扩展做了 3 件事

> - 注册了 `onCommand` **激活事件**：`onCommand:helloworld.helloWorld`，这样用户执行 `Hello World` 命令时，扩展就会被激活。
>   > **注意：** 从 VS Code 1.74.0 开始，在 `package.json` 的 `commands` 部分声明的命令，被调用时会自动激活扩展，不再需要在 `activationEvents` 中显式写 `onCommand`。
> - 使用 `contributes.commands` **贡献点**，让 `Hello World` 命令出现在命令面板中，并把它绑定到命令 ID `helloworld.helloWorld`。
> - 使用 `commands.registerCommand` 这个 **VS Code API**，把一个函数绑定到已注册的命令 ID `helloworld.helloWorld` 上。

对应到用户执行一次命令时的完整过程：

```text
用户在命令面板中看到 "Hello World"     ← 贡献点（package.json 声明的）
        │ 点击执行
        ▼
VS Code 发现扩展还没加载，先激活它       ← 激活事件（决定什么时候加载）
        │ 调用扩展的 activate()
        ▼
activate() 里执行 registerCommand       ← VS Code API（代码里实现的）
        │ 命令 ID 和处理函数绑定好了
        ▼
VS Code 调用处理函数 → 弹出 "Hello World!"
```

## 二、三个核心概念

> 理解这三个概念，对编写 VS Code 扩展至关重要：
>
> - **激活事件（Activation Events）**：让扩展被激活的事件。
> - **贡献点（Contribution Points）**：在 `package.json`（扩展清单）中做的静态声明，用来扩展 VS Code。
> - **VS Code API**：一组可以在扩展代码中调用的 JavaScript API。

逐个展开讲：

### 1. 激活事件：扩展**什么时候**加载

VS Code 里可能装了几十个扩展，如果启动时全部加载，会非常慢。所以 VS Code 采用**按需加载**：扩展平时处于“休眠”状态，只有发生特定的事件时才会被加载（激活）。

常见的激活事件：

| 激活事件 | 何时激活 |
|---|---|
| `onCommand:xxx` | 用户执行某个命令时 |
| `onLanguage:python` | 打开 Python 文件时 |
| `workspaceContains:**/package.json` | 打开的文件夹里包含某类文件时 |
| `onStartupFinished` | VS Code 启动完成后（不拖慢启动速度） |
| `*` | VS Code 一启动就激活（不推荐，会拖慢启动） |

扩展**只会激活一次**，激活后就一直保持运行，直到 VS Code 关闭（或扩展被禁用、卸载）。

**关于 1.74 版本的变化：** 以前每个命令都要在 `activationEvents` 里手写一遍 `onCommand:xxx`，和 `contributes.commands` 里的内容重复。1.74 之后 VS Code 会根据声明的命令自动生成这些激活事件，所以现在的脚手架生成的 `activationEvents` 是空数组 `[]`。其他类型的贡献（比如视图、语言）也有类似的自动生成规则。

### 2. 贡献点：在界面上**声明**有什么

贡献点写在 `package.json` 的 `contributes` 字段里，作用是告诉 VS Code：“我这个扩展要往界面上加这些东西。”

**它是“静态”的**：VS Code **不需要运行你的代码**，只读取 `package.json` 就知道要显示哪些命令、菜单、设置项。所以即使扩展还没激活，命令面板里也已经能看到它的命令，这正是上面“先看到命令、点击后才激活”流程能够成立的原因。

常见的贡献点：

| 贡献点 | 作用 |
|---|---|
| `contributes.commands` | 命令 |
| `contributes.menus` | 菜单项（右键菜单、编辑器标题栏按钮等） |
| `contributes.keybindings` | 快捷键 |
| `contributes.configuration` | 设置项（出现在设置页面中） |
| `contributes.views` | 侧边栏视图 |
| `contributes.languages` | 新的语言支持 |

### 3. VS Code API：在代码里**实现**做什么

贡献点只负责声明，不包含任何逻辑。真正的行为要在扩展代码中，通过调用 `vscode` 模块提供的 API 来实现，例如：

```ts
vscode.commands.registerCommand(...)       // 注册命令
vscode.window.showInformationMessage(...)  // 显示消息
vscode.workspace.getConfiguration(...)     // 读取设置
vscode.languages.registerHoverProvider(...) // 提供悬停提示
```

### 三者的关系

> 一般来说，扩展会组合使用贡献点和 VS Code API 来扩展 VS Code 的功能。[扩展能力概览](../extension-capabilities/overview.md) 一节可以帮你找到适合你扩展的贡献点和 API。

可以这样记：

| 概念 | 写在哪 | 回答的问题 |
|---|---|---|
| 激活事件 | `package.json` → `activationEvents` | **什么时候**加载我的代码？ |
| 贡献点 | `package.json` → `contributes` | 界面上**有什么**？ |
| VS Code API | `extension.ts` 等代码文件 | 被触发时**做什么**？ |

以后学习任何新功能，都可以先问自己这三个问题。

> 下面仔细看看 Hello World 示例的源代码，看这些概念是如何体现的。

---

<a id="extension-file-structure"></a>
## 三、扩展的文件结构（Extension File Structure）

```text
.
├── .vscode
│   ├── launch.json     // 启动和调试扩展的配置
│   └── tasks.json      // 编译 TypeScript 的构建任务配置
├── .gitignore          // 忽略构建产物和 node_modules
├── README.md           // 扩展功能的说明文档
├── src
│   └── extension.ts    // 扩展源代码
├── package.json        // 扩展清单
├── tsconfig.json       // TypeScript 配置
```

> 关于这些配置文件，可以进一步阅读：
>
> - `launch.json`：用于配置 VS Code 的[调试](https://code.visualstudio.com/docs/debugtest/debugging)
> - `tasks.json`：用于定义 VS Code 的[任务](https://code.visualstudio.com/docs/debugtest/tasks)
> - `tsconfig.json`：请参考 TypeScript [手册](https://www.typescriptlang.org/docs/handbook/tsconfig-json.html)

这几个文件和上一篇的操作是对应的：

- 按 `F5` 时，VS Code 读取 **`launch.json`**，知道要打开一个“扩展开发宿主”窗口。
- 启动前先执行 **`tasks.json`** 中定义的编译任务（`watch`），把 `src/` 下的 TypeScript 编译到 `out/` 目录。
- 编译怎么进行（编译成哪个 JS 版本、输出到哪里），由 **`tsconfig.json`** 决定。

这三个文件脚手架都已经配好了，入门阶段一般不需要修改。

> 不过，我们先重点关注 `package.json` 和 `extension.ts`，它们是理解 Hello World 扩展的关键。

---

<a id="extension-manifest"></a>
## 四、扩展清单（Extension Manifest）

> 每个 VS Code 扩展都必须有一个 `package.json` 作为[扩展清单](https://code.visualstudio.com/api/references/extension-manifest)。`package.json` 中既有 Node.js 的字段（如 `scripts` 和 `devDependencies`），也有 VS Code 特有的字段（如 `publisher`、`activationEvents` 和 `contributes`）。

也就是说，`package.json` 同时承担两个角色：

- 对 **npm** 来说，它是普通的 Node.js 项目配置（依赖、脚本）；
- 对 **VS Code** 来说，它是扩展的“身份证”和“功能说明书”。

> 最重要的几个字段：
>
> - `name` 和 `publisher`：VS Code 用 `<publisher>.<name>` 作为扩展的唯一 ID。例如 Hello World 示例的 ID 是 `vscode-samples.helloworld-sample`。
> - `main`：扩展的入口文件。
> - `activationEvents` 和 `contributes`：激活事件和贡献点。
> - `engines.vscode`：扩展依赖的 VS Code API 的最低版本。

完整示例（加上了中文注释；实际的 JSON 文件里不能写注释）：

```jsonc
{
  "name": "helloworld-sample",            // 扩展名，和 publisher 组成唯一 ID
  "displayName": "helloworld-sample",     // 在扩展市场中显示的名字
  "description": "HelloWorld example for VS Code",
  "version": "0.0.1",
  "publisher": "vscode-samples",          // 发布者 ID，发布到市场时需要
  "repository": "https://github.com/microsoft/vscode-extension-samples/helloworld-sample",
  "engines": {
    "vscode": "^1.51.0"                   // 最低需要 VS Code 1.51.0
  },
  "categories": ["Other"],                // 在扩展市场中的分类
  "activationEvents": [],                 // 激活事件（1.74 后命令的激活事件自动生成）
  "main": "./out/extension.js",           // 入口：注意是编译后的 .js，不是 .ts
  "contributes": {                        // 贡献点
    "commands": [
      {
        "command": "helloworld.helloWorld", // 命令 ID，和代码中的保持一致
        "title": "Hello World"              // 命令面板中显示的名字
      }
    ]
  },
  "scripts": {                            // npm 脚本
    "vscode:prepublish": "npm run compile", // 打包发布前自动执行
    "compile": "tsc -p ./",               // 编译一次
    "watch": "tsc -watch -p ./"           // 监视文件变化并持续编译
  },
  "devDependencies": {                    // 开发依赖
    "@types/node": "^8.10.25",
    "@types/vscode": "^1.51.0",           // VS Code API 的类型定义
    "tslint": "^5.16.0",
    "typescript": "^3.4.5"
  }
}
```

几个容易混淆的地方：

- **`name` 和 `displayName`**：`name` 是程序用的标识，只能用小写字母和连字符；`displayName` 是给人看的名字，可以随便写。
- **`main` 指向 `out/extension.js`**：VS Code 运行的是编译后的 JavaScript，而不是 TypeScript 源码。如果没编译，或者编译失败，扩展就跑不起来。
- **`vscode:prepublish`**：这是 VS Code 特有的脚本名，打包扩展（`vsce package`）时会自动执行，确保发布的是最新编译的代码。
- **版本号偏旧**：这个示例里的依赖版本比较老（`typescript ^3.4.5`，以及已经停止维护的 `tslint`）。现在用脚手架新建的项目会使用新版本，并用 ESLint 代替 TSLint，不需要照抄这里的版本号。

> **注意：** 如果你的扩展要支持 1.74 之前的 VS Code 版本，就必须在 `activationEvents` 中显式写上 `onCommand:helloworld.helloWorld`。

也就是说，判断要不要手写激活事件，看的是 `engines.vscode` 的最低版本：低于 1.74 就要写，否则不用写。

---

<a id="extension-entry-file"></a>
## 五、扩展入口文件（Extension Entry File）

> 扩展入口文件导出两个函数：`activate` 和 `deactivate`。`activate` 在你注册的**激活事件**发生时执行。`deactivate` 让你有机会在扩展被停用前做清理工作。对很多扩展来说，并不需要专门清理，可以删掉 `deactivate` 方法。但如果扩展需要在 VS Code 关闭、扩展被禁用或卸载时执行某些操作，就应该写在这个方法里。

可以把扩展的生命周期理解成：

```text
激活事件发生  →  activate()  →  扩展运行中……  →  deactivate()  →  结束
              （只调用一次）                    （VS Code 关闭 / 扩展被禁用或卸载时）
```

- **`activate`**：做初始化，最主要的工作是注册命令、注册各种 Provider（提供者）。
- **`deactivate`**：做清理，比如关闭网络连接、停止子进程、保存状态。可以返回一个 Promise（写成 `async` 函数），VS Code 会等待它完成，但等待的时间有限，不要在这里做耗时的操作。

> VS Code 扩展 API 声明在 [@types/vscode](https://www.npmjs.com/package/@types/vscode) 类型定义中。`vscode` 类型定义的版本由 `package.json` 中 `engines.vscode` 字段的值控制。有了 `vscode` 类型定义，你在代码里就能使用智能提示、跳转到定义等 TypeScript 语言功能。

这里有个容易误解的点：**`import * as vscode from 'vscode'` 导入的并不是一个 npm 包。**

- `@types/vscode` 只有**类型定义**，没有任何实现代码，作用是让你在写代码时获得自动补全和类型检查；
- 扩展真正运行时，`vscode` 模块由 **VS Code 自己提供**，也就是你本机 VS Code 版本里的实现。

所以 `@types/vscode` 的版本应该和 `engines.vscode` 保持一致：类型定义版本太高，可能用到老版本 VS Code 里还不存在的 API；版本太低，又看不到新 API。

下面是入口文件的代码（注释已翻译成中文）：

```ts
// 'vscode' 模块包含了 VS Code 扩展 API
// 导入这个模块，并在下面的代码中用别名 vscode 引用它
import * as vscode from 'vscode';

// 扩展被激活时会调用这个方法
// 扩展会在命令第一次被执行时激活
export function activate(context: vscode.ExtensionContext) {
  // 用 console 输出诊断信息（console.log）和错误（console.error）
  // 这行代码只会在扩展激活时执行一次
  console.log('Congratulations, your extension "helloworld-sample" is now active!');

  // 这个命令已经在 package.json 文件中声明了
  // 现在用 registerCommand 提供命令的具体实现
  // commandId 参数必须和 package.json 中的 command 字段一致
  let disposable = vscode.commands.registerCommand('helloworld.helloWorld', () => {
    // 每次执行这个命令时，都会运行这里的代码

    // 向用户显示一个消息框
    vscode.window.showInformationMessage('Hello World!');
  });

  context.subscriptions.push(disposable);
}

// 扩展被停用时会调用这个方法
export function deactivate() {}
```

逐段说明：

**① `activate(context)` 的参数 `context`**

`ExtensionContext` 是 VS Code 传给扩展的“工具箱”，里面有很多有用的东西，例如：

| 属性 | 用途 |
|---|---|
| `context.subscriptions` | 存放需要在停用时自动释放的资源（见下面 ③） |
| `context.extensionPath` / `extensionUri` | 扩展自身的安装目录，用来读取扩展里附带的文件 |
| `context.globalState` / `workspaceState` | 简单的键值存储，用来保存扩展的状态 |
| `context.secrets` | 安全存储，用来保存 token、密码等敏感信息 |

**② `registerCommand` 把 ID 和函数绑定**

第一个参数 `'helloworld.helloWorld'` 必须和 `package.json` 中 `contributes.commands[].command` **完全一致**（区分大小写）。这是新手最常出错的地方：两边对不上时，命令面板里能看到命令，但执行时会报错 `command 'xxx' not found`。

**③ `disposable` 和 `context.subscriptions.push(...)`**

`registerCommand` 的返回值是一个 **Disposable（可释放对象）**，它有一个 `dispose()` 方法，调用后命令就会被注销。

VS Code API 中很多注册类的方法都返回 Disposable，比如注册事件监听、注册 Provider、创建状态栏项等。把它们都放进 `context.subscriptions`，扩展停用时 VS Code 会**自动逐个调用 `dispose()`**，不需要在 `deactivate` 里手动清理。这也是为什么很多扩展的 `deactivate` 是空函数。

记住一条规则：**凡是返回 Disposable 的，都 push 到 `context.subscriptions` 里。**

**④ 小提示：`let` 可以写成 `const`**

示例中的 `let disposable` 变量之后没有被重新赋值，现在一般写成 `const`。新版脚手架生成的代码已经这样改了，两者效果一样。

---

## 本篇小结

```text
package.json（静态声明，VS Code 不运行代码就能读取）
  ├─ name + publisher  → 扩展唯一 ID
  ├─ engines.vscode    → 最低支持的 VS Code 版本（同时决定 @types/vscode 的版本）
  ├─ main              → 入口文件（编译后的 .js）
  ├─ activationEvents  → 【激活事件】什么时候加载
  └─ contributes       → 【贡献点】界面上有什么

extension.ts（运行时代码）
  ├─ activate(context) → 激活时执行一次，用【VS Code API】注册各种功能
  │     └─ 返回的 Disposable 都 push 到 context.subscriptions
  └─ deactivate()      → 停用时做清理（经常是空的）
```

**核心记忆点：贡献点负责“声明”，VS Code API 负责“实现”，激活事件负责“何时加载”。两边的 ID 必须一致。**
