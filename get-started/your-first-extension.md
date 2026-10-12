# 你的第一个扩展（Your First Extension）

> 原文：[Your First Extension](https://code.visualstudio.com/api/get-started/your-first-extension)
> 源文件：`microsoft/vscode-docs` → `api/get-started/your-first-extension.md`（DateApproved: 10/7/2026）

这一篇的目标很简单：**用脚手架生成一个 Hello World 扩展，把它跑起来，改一改，再调试一下。** 先把这个流程走通，原理放到下一篇 [扩展的结构](./extension-anatomy.md) 里讲。

---

## 一、准备环境

> 请确保已经安装了 [Node.js](https://nodejs.org) 和 [Git](https://git-scm.com/)。

- **Node.js**：扩展运行在 Node.js 环境里，开发时还要靠它安装依赖、编译 TypeScript。
- **Git**：脚手架会询问是否初始化 Git 仓库，不装也能继续，但建议装上。

可以在终端里检查一下：

```bash
node -v   # 能输出版本号就说明装好了
git --version
```

---

## 二、用脚手架生成项目

> 使用 [Yeoman](https://yeoman.io/) 和 [VS Code Extension Generator](https://www.npmjs.com/package/generator-code) 生成一个可以直接开发的 TypeScript 或 JavaScript 项目。

这里出现了两个工具：

| 工具 | 是什么 |
|---|---|
| **Yeoman**（命令名 `yo`） | 一个通用的“项目脚手架”工具，本身不知道怎么生成 VS Code 扩展 |
| **generator-code** | Yeoman 的一个模板（生成器），专门用来生成 VS Code 扩展项目 |

两者组合起来就是 `yo code`：用 Yeoman 运行 code 这个生成器。

原文给了两种运行方式，**选一种就行**：

**方式 1：不安装，临时运行一次**

```bash
npx --package yo --package generator-code -- yo code
```

`npx` 会临时下载 `yo` 和 `generator-code`，用完不在全局留下东西。适合只建一两个项目的情况。

**方式 2：全局安装，以后反复使用**

```bash
npm install --global yo generator-code

yo code
```

安装一次后，以后每次新建扩展直接执行 `yo code` 即可。

### 回答脚手架的问题

运行后，命令行会依次提问。原文示例如下（`#` 后是问题和推荐的回答）：

```bash
# ? What type of extension do you want to create? New Extension (TypeScript)
# ? What's the name of your extension? HelloWorld
### 下面的选项直接按回车使用默认值 ###

# ? What's the identifier of your extension? helloworld
# ? What's the description of your extension? 留空
# ? Initialize a git repository? Y
# ? Which bundler to use? unbundled
# ? Which package manager to use? npm

# ? Do you want to open the new folder with Visual Studio Code? Open with `code`
```

逐条解释一下：

| 问题 | 含义 | 建议 |
|---|---|---|
| What type of extension... | 扩展类型。除了普通扩展，还有颜色主题、代码片段、语言支持等模板 | 选 `New Extension (TypeScript)` |
| What's the name... | 扩展的显示名称 | 随意，例如 `HelloWorld` |
| What's the identifier... | 扩展的标识符，会写进 `package.json` 的 `name` 字段 | 默认值即可（小写、无空格） |
| What's the description... | 扩展描述 | 先留空，以后可以改 |
| Initialize a git repository? | 是否初始化 Git 仓库 | `Y` |
| Which bundler to use? | 是否使用打包工具（如 webpack、esbuild） | 入门阶段选 `unbundled`（不打包），结构最简单 |
| Which package manager to use? | 用哪个包管理器 | `npm`，用 pnpm / yarn 也可以 |
| Do you want to open... | 生成后是否直接用 VS Code 打开 | 选 `Open with code` |

**关于 bundler：** 打包是指把扩展的所有代码和依赖合并成一个文件，这样加载更快、安装包更小，正式发布时推荐使用。入门阶段不打包更容易看懂项目结构，后面的 [打包扩展](https://code.visualstudio.com/api/working-with-extensions/bundling-extension) 一章会专门讲。

---

## 三、运行扩展

> 在编辑器中打开 `src/extension.ts`，按 `F5`，或者在命令面板（`Ctrl+Shift+P`）中运行 **Debug: Start Debugging**。这会编译扩展，并在一个新的 **扩展开发宿主（Extension Development Host）** 窗口中运行它。

（原文中的快捷键是占位符，这里换成了 Windows/Linux 的默认按键；macOS 上 `Ctrl` 对应 `Cmd`。）

**这是本篇最重要的概念：扩展开发宿主。**

按下 F5 后，会**弹出第二个 VS Code 窗口**：

```text
┌──────────────────────┐        ┌───────────────────────────────┐
│ 窗口 A：你写代码的窗口 │  F5 →  │ 窗口 B：扩展开发宿主             │
│ （打开着扩展项目）     │        │ （临时加载了你正在开发的扩展）   │
└──────────────────────┘        └───────────────────────────────┘
```

- **窗口 A** 是开发环境，在这里改代码、打断点。
- **窗口 B** 是测试环境，相当于“装好了你的扩展的 VS Code”，在这里试用扩展。

这样做的好处是：不需要真的打包、安装扩展，就能马上看到效果；扩展出了问题也不会影响你正在用的 VS Code。

> 在新窗口中，通过命令面板（`Ctrl+Shift+P`）运行 **Hello World** 命令。

> 你应该能看到弹出 `Hello World from HelloWorld!` 的通知。成功！

注意：**要在窗口 B 里运行命令**，在窗口 A 里是找不到这个命令的。

> 如果在调试窗口中看不到 **Hello World** 命令，请检查 `package.json` 文件，确保 `engines.vscode` 的版本与你安装的 VS Code 版本兼容。

这是新手最常遇到的问题。`engines.vscode` 声明了扩展**最低需要哪个版本的 VS Code**，例如：

```json
"engines": {
  "vscode": "^1.105.0"
}
```

`^1.105.0` 表示需要 1.105.0 或更高版本。如果你本机的 VS Code 比这个版本旧，扩展就不会被加载，命令自然也找不到。解决办法：升级 VS Code（`帮助 → 检查更新`），或者把这个版本号改低一些。

**演示视频：** 按 `F5` 启动扩展开发宿主，在新窗口中执行 Hello World 命令，右下角弹出通知。

<video src="images/your-first-extension/launch.mp4" loop muted playsinline controls title="启动第一个 VS Code 扩展">
  视频无法播放时，可以直接打开 <a href="images/your-first-extension/launch.mp4">launch.mp4</a>。
</video>

---

<a id="developing-the-extension"></a>
## 四、修改扩展（Developing the extension）

> 我们来改一下提示消息：
> 1. 在 `extension.ts` 中把消息从 `"Hello World from HelloWorld!"` 改成 `"Hello VS Code"`。
> 2. 在新窗口中运行 **Developer: Reload Window**。
> 3. 再次运行 **Hello World** 命令。
>
> 你应该能看到更新后的消息。

**演示视频：** 修改代码中的提示文字，在扩展开发宿主窗口中执行 Developer: Reload Window，再次运行命令，看到新的提示。

<video src="images/your-first-extension/reload.mp4" loop muted playsinline controls title="重新加载 VS Code 扩展">
  视频无法播放时，可以直接打开 <a href="images/your-first-extension/reload.mp4">reload.mp4</a>。
</video>

这就是日常开发的循环：

```text
在窗口 A 改代码  →  在窗口 B 执行 Developer: Reload Window  →  在窗口 B 重新测试
```

**为什么改完代码要重新加载窗口？** 扩展只在激活时加载一次。窗口 B 里运行的还是旧代码，重新加载窗口后，才会读取新编译出的代码。

**代码是什么时候编译的？** 脚手架生成的调试配置在启动时会同时运行一个 `watch` 任务：它在后台监视源代码，一保存就自动把 TypeScript 编译成 JavaScript。所以保存文件后，直接在窗口 B 里重新加载就行，不用手动编译。

> 你可以试试下面这些练习：
>
> - 在命令面板中给 **Hello World** 命令换一个名字。
> - [贡献（Contribute）](https://code.visualstudio.com/api/references/contribution-points) 另一个命令，用信息提示显示当前时间。贡献点是你在 `package.json`（即[扩展清单](https://code.visualstudio.com/api/references/extension-manifest)）中做的静态声明，用来扩展 VS Code，比如给扩展添加命令、菜单或快捷键。
> - 把 `vscode.window.showInformationMessage` 换成另一个 [VS Code API](https://code.visualstudio.com/api/references/vscode-api) 调用，显示一条警告消息。

这三个练习各有考察的重点，下面给出提示：

**练习 1：改命令名称** —— 改的是 `package.json` 里的 `title`，不是代码：

```json
"contributes": {
  "commands": [
    {
      "command": "helloworld.helloWorld",
      "title": "打个招呼"
    }
  ]
}
```

`command` 是给程序用的 ID，不要动；`title` 是显示给用户看的名字。

**练习 2：新增一个显示时间的命令** —— 需要**两处配合**，这正是下一篇要讲的核心：

```jsonc
// package.json：声明命令（让命令面板里能看到）
"contributes": {
  "commands": [
    { "command": "helloworld.helloWorld", "title": "Hello World" },
    { "command": "helloworld.showTime", "title": "Show Current Time" }
  ]
}
```

```ts
// extension.ts 的 activate 函数里：实现命令（被执行时做什么）
context.subscriptions.push(
  vscode.commands.registerCommand('helloworld.showTime', () => {
    vscode.window.showInformationMessage(new Date().toLocaleString());
  })
);
```

只写其中一处都不行：只声明不实现，执行命令会报错“找不到命令”；只实现不声明，命令面板里看不到这个命令。

**练习 3：显示警告消息** —— 把 `showInformationMessage` 换成 `showWarningMessage` 即可（还有显示错误消息的 `showErrorMessage`）。这个练习的目的是让你熟悉 VS Code API：大部分功能都是通过 `vscode.xxx` 这样的接口调用的。

---

<a id="debugging-the-extension"></a>
## 五、调试扩展（Debugging the extension）

> VS Code 内置的调试功能让调试扩展变得很容易。在代码行号左侧的空白处（gutter）点击即可设置断点，执行到这里时 VS Code 会停下来。你可以把鼠标悬停在编辑器里的变量上，或者在左侧的 **运行和调试** 视图中查看变量的值。在调试控制台里还可以对表达式求值。

具体操作：

1. 在窗口 A 中，点击 `extension.ts` 某一行行号的左边，出现一个**红点**，这就是断点。
2. 在窗口 B 中执行 Hello World 命令。
3. 窗口 A 会在断点处暂停。这时可以：
   - 把鼠标悬停在变量上，查看它的值；
   - 在左侧“运行和调试”面板的“变量”区域查看所有变量；
   - 在底部的“调试控制台”中输入表达式（例如 `context.extensionPath`），立即看到结果。
4. 按 `F5` 继续执行，按 `F10` 单步执行下一行。

**演示视频：** 在代码中设置断点，执行命令后停在断点处，查看变量的值。

<video src="images/your-first-extension/debug.mp4" loop muted playsinline controls title="调试 VS Code 扩展">
  视频无法播放时，可以直接打开 <a href="images/your-first-extension/debug.mp4">debug.mp4</a>。
</video>

**补充：`console.log` 输出到哪里？** 扩展代码里的 `console.log` 显示在**窗口 A 的“调试控制台”**里，而不是窗口 B。刚开始常有人在窗口 B 里找输出，结果找不到。

> 更多内容可以阅读 [Node.js 调试](https://code.visualstudio.com/docs/nodejs/nodejs-debugging) 一节。

---

<a id="next-steps"></a>
## 六、下一步（Next steps）

> 下一篇 [扩展的结构（Extension Anatomy）](./extension-anatomy.md) 会仔细分析 Hello World 示例的源代码，并解释其中的关键概念。

> 本教程的源代码在：[helloworld-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-sample)。[扩展指南](https://code.visualstudio.com/api/extension-guides/overview) 部分还有很多其他示例，每个示例演示一个 VS Code API 或贡献点，并且都遵循 [UX 指南](https://code.visualstudio.com/api/ux-guidelines/overview) 中的建议。

[vscode-extension-samples](https://github.com/microsoft/vscode-extension-samples) 是官方示例仓库，里面有几十个完整可运行的扩展。后面学到某个功能时，去找对应的示例来跑一下，效果比只看文档好得多。

<a id="using-javascript"></a>
### 使用 JavaScript（Using JavaScript）

> 本指南主要介绍如何用 TypeScript 开发 VS Code 扩展，因为我们认为 TypeScript 能提供最好的开发体验。不过如果你更喜欢 JavaScript，也可以参考 [helloworld-minimal-sample](https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-minimal-sample) 跟着学。

推荐用 TypeScript 的主要原因是：VS Code 的 API 有完整的类型定义，写代码时能自动补全接口名、提示参数类型，写错了也会立刻标红。对刚接触这套 API 的人来说，这几乎就是一份随时可查的文档。

<a id="ux-guidelines"></a>
### UX 指南（UX Guidelines）

> 现在也是阅读 [UX 指南](https://code.visualstudio.com/api/ux-guidelines/overview) 的好时机，这样你从一开始就能按照 VS Code 的最佳实践来设计扩展的界面。

---

## 本篇小结

| 要点 | 说明 |
|---|---|
| 生成项目 | `yo code`（Yeoman + generator-code） |
| 运行扩展 | 按 `F5`，会打开**扩展开发宿主**窗口 |
| 测试扩展 | 在**新窗口**中通过命令面板执行命令 |
| 修改后生效 | 保存代码，然后在新窗口中执行 **Developer: Reload Window** |
| 调试 | 在原窗口打断点，`console.log` 输出在原窗口的调试控制台 |
| 找不到命令 | 检查 `engines.vscode` 版本是否高于本机 VS Code |
| 新增命令 | `package.json` 中**声明**，加上 `extension.ts` 中**实现**，两者缺一不可 |
