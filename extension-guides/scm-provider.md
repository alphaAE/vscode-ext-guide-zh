# 源代码管理 API（Source Control API）

> 原文：[Source Control API](https://code.visualstudio.com/api/extension-guides/scm-provider)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/scm-provider.md`（DateApproved: 10/7/2026）

> 源代码管理 API 让扩展作者可以定义源代码管理（Source Control Management，SCM）功能。它的 API 很精简，但功能强大，可以把许多不同的 SCM 系统集成到 VS Code 中，同时让它们共享一套统一的用户界面。

![VS Code 的源代码管理界面](images/scm-provider/main.png)

截图中，左侧是“源代码管理”视图：顶部是提交信息输入框，下面分成 **STAGED CHANGES**（已暂存的更改）和 **CHANGES**（更改）两组，每组列出发生变化的文件，文件右侧的字母表示变化类型（M 修改、R 重命名、D 删除）；右侧是点击 `README.md` 后打开的差异对比编辑器。

**统一界面是这套 API 的核心思想。** 不管背后是 Git、SVN 还是其他版本控制系统，用户看到的界面都一样：输入框、分组的文件列表、差异对比。扩展只需要告诉 VS Code “有哪些文件变了、属于哪一组”，界面由 VS Code 负责绘制。

> VS Code 自身附带了一个源代码管理提供者，也就是 Git 扩展。它是这个 API 最好的参考，如果你想贡献自己的 SCM 提供者，它也是[一个很好的起点](https://github.com/microsoft/vscode/blob/main/extensions/git/src/repository.ts)。扩展市场中还有其他很好的例子，比如 [SVN 扩展](https://marketplace.visualstudio.com/items?itemName=johnstoncode.svn-scm)。
>
> 本文档将帮助你构建一个扩展，让任何 SCM 系统都能在 VS Code 中工作。
>
> **注意：** 你随时可以查阅文档中的 [`vscode` 命名空间 API 参考](https://code.visualstudio.com/api/references/vscode-api#scm)。

---

<a id="source-control-model"></a>
## 源代码管理模型（Source Control Model）

> `SourceControl` 是负责用**资源状态**（`SourceControlResourceState` 的实例）填充源代码管理模型的实体。资源状态本身按**组**（`SourceControlResourceGroup` 的实例）组织。
>
> 可以用 `vscode.scm.createSourceControl` 创建一个新的 SourceControl。

三个实体的层级关系：

```text
SourceControl（一个源代码管理实例，通常对应一个仓库）
  ├─ SourceControlResourceGroup（资源组，比如“已暂存的更改”）
  │     ├─ SourceControlResourceState（资源状态：一个文件的一次变化）
  │     └─ SourceControlResourceState
  └─ SourceControlResourceGroup（比如“更改”）
        └─ SourceControlResourceState
```

> 为了更好地理解这三个实体之间的关系，我们以 [Git](https://github.com/microsoft/vscode/tree/main/extensions/git) 为例。看看下面这段 `git status` 的输出：

```bash
vsce main* → git status
On branch main
Your branch is up-to-date with 'origin/main'.
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

        modified:   README.md
        renamed:    src/api.ts -> src/test/api.ts

Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

        deleted:    .travis.yml
        modified:   README.md
```

> 这个工作区中发生了很多事情。首先，`README.md` 文件被修改、暂存，然后又被修改了一次。其次，`src/api.ts` 文件被移动到了 `src/test/api.ts`，并且这次移动已经被暂存。最后，`.travis.yml` 文件被删除了。
>
> 对于这个工作区，Git 定义了两个资源组：**工作树（working tree）**和**索引（index）**。组中的每一个**文件变化**都是一个**资源状态**：
>
> - **Index**（索引）：资源组
>   - `README.md`，已修改：资源状态
>   - `src/test/api.ts`，由 `src/api.ts` 重命名而来：资源状态
> - **Working Tree**（工作树）：资源组
>   - `.travis.yml`，已删除：资源状态
>   - `README.md`，已修改：资源状态
>
> 注意，同一个文件 `README.md` 属于两个不同的资源状态。

**Git 术语对照：**

| Git 术语 | 含义 | 在 VS Code 中显示为 |
|---|---|---|
| 索引（index，也叫暂存区） | 已经 `git add`、准备提交的更改 | Staged Changes（已暂存的更改） |
| 工作树（working tree） | 已修改但还没有暂存的更改 | Changes（更改） |

**为什么 `README.md` 出现了两次？** 因为它先被修改、暂存（第一次修改进了索引），之后又被修改了（第二次修改还在工作树中）。所以资源状态表示的不是“一个文件”，而是“**一个文件在某个组中的一次变化**”。

> 下面是 Git 创建这个模型的方式：

```ts
function createResourceUri(relativePath: string): vscode.Uri {
  const absolutePath = path.join(vscode.workspace.rootPath, relativePath);
  return vscode.Uri.file(absolutePath);
}

// 创建源代码管理实例：id 为 'git'，显示名为 'Git'
const gitSCM = vscode.scm.createSourceControl('git', 'Git');

// 创建“索引”资源组，并设置其中的资源状态
const index = gitSCM.createResourceGroup('index', 'Index');
index.resourceStates = [
  { resourceUri: createResourceUri('README.md') },
  { resourceUri: createResourceUri('src/test/api.ts') }
];

// 创建“工作树”资源组
const workingTree = gitSCM.createResourceGroup('workingTree', 'Changes');
workingTree.resourceStates = [
  { resourceUri: createResourceUri('.travis.yml') },
  { resourceUri: createResourceUri('README.md') }
];
```

> 对源代码管理和资源组所做的更改，都会同步到源代码管理视图中。

- `createSourceControl(id, label, rootUri?)` 的第三个参数可以指定仓库的根目录。同时打开多个仓库时，VS Code 会为每个 `SourceControl` 显示一个单独的区域。
- `createResourceGroup(id, label)` 中的 `label` 就是视图中显示的分组标题。
- 更新列表的方式就是**给 `resourceStates` 重新赋值**，VS Code 会自动刷新视图。
- 示例中的 `vscode.workspace.rootPath` 已经废弃（它只能表示第一个文件夹，不支持多根工作区），新代码应该使用 `vscode.workspace.workspaceFolders`。

---

<a id="source-control-view"></a>
## 源代码管理视图（Source Control View）

> 当源代码管理模型发生变化时，VS Code 能够填充源代码管理视图。资源状态可以通过 `SourceControlResourceDecorations` 进行定制：

```ts
export interface SourceControlResourceState {
  readonly decorations?: SourceControlResourceDecorations;
}
```

**装饰（decorations）**控制每个文件在列表中的显示样式，常用的有：

| 属性 | 作用 | 例子 |
|---|---|---|
| `strikeThrough` | 文件名加删除线 | 截图中被删除的 `.travis.yml` |
| `faded` | 文件名显示为淡色 | 被忽略的文件 |
| `tooltip` | 鼠标悬停时的提示 | “已修改” |
| `iconPath` | 文件旁的图标 | |
| `light` / `dark` | 分别为浅色、深色主题设置上述样式 | |

截图中文件右侧的 `M`、`D`、`R` 字母，通常是通过 [文件装饰](https://code.visualstudio.com/api/references/vscode-api#FileDecorationProvider)（`FileDecorationProvider`）显示的，Git 扩展还用它给资源管理器中的文件名着色。

> 前面的示例足以在源代码管理视图中填充一个简单的列表，但用户可能还想对每个资源执行很多交互操作。例如，用户点击一个资源状态时，会发生什么？资源状态可以选择提供一个命令来处理这个操作：

```ts
export interface SourceControlResourceState {
  readonly command?: Command;
}
```

例如，点击文件时打开差异对比编辑器（就像截图中右侧那样），可以调用内置的 `vscode.diff` 命令：

```ts
{
  resourceUri: fileUri,
  command: {
    title: 'Open Changes',
    command: 'vscode.diff',
    arguments: [originalUri, fileUri, 'README.md (Index)']  // 左侧（原始）、右侧（当前）、标题
  }
}
```

`originalUri` 指向文件的原始版本，通常是一个[虚拟文档](./virtual-documents.md)的 URI（见本篇最后的“快速差异”一节）。

<a id="menus"></a>
### 菜单（Menus）

> 源代码管理有六个菜单 ID，你可以在其中放置菜单项，为用户提供更丰富的用户界面。

（原文说“六个”，但下文实际介绍了七个：`scm/title`、`scm/resourceGroup/context`、`scm/resourceState/context`、`scm/resourceFolder/context`、`scm/repository`、`scm/sourceControl`、`scm/change/title`。）

先看总览，再逐个讲解：

| 菜单 ID | 位置 |
|---|---|
| `scm/title` | 源代码管理视图标题的右侧 |
| `scm/resourceGroup/context` | 资源组（如“更改”）上 |
| `scm/resourceState/context` | 资源状态（单个文件）上 |
| `scm/resourceFolder/context` | 树形模式下的中间文件夹上 |
| `scm/repository` | “源代码管理存储库”视图中，每个仓库上（行内按钮和 `...` 菜单） |
| `scm/sourceControl` | “源代码管理存储库”视图中，每个仓库的右键菜单 |
| `scm/change/title` | 快速差异的行内差异编辑器的标题栏 |

> `scm/title` 菜单位于 SCM 视图标题的右侧。`navigation` 组中的菜单项会显示为行内按钮，其他的则放在 `…` 下拉菜单中。
>
> 下面三个是类似的：
>
> - `scm/resourceGroup/context`：向 [`SourceControlResourceGroup`](../references/contribution-points.md#contributes.menus) 条目添加命令。
> - `scm/resourceState/context`：向 [`SourceControlResourceState`](../references/contribution-points.md#contributes.menus) 条目添加命令。
> - `scm/resourceFolder/context`：当 [`SourceControlResourceState`](../references/contribution-points.md#contributes.menus) 的 resourceUri 路径中包含文件夹，并且用户选择了树形视图而不是列表视图模式时，向出现的中间文件夹添加命令。
>
> 把菜单项放在 `inline` 组中，可以让它们显示为行内按钮。其他所有菜单项组，都会显示在通常通过鼠标右键打开的上下文菜单中。

这和 [树视图](./tree-view.md#view-actions) 中 `view/title`（`navigation` 组）、`view/item/context`（`inline` 组）的规则完全一样。

**“中间文件夹”是什么？** 源代码管理视图有两种显示模式：列表模式下所有文件平铺显示；树形模式下按目录层级显示，比如 `src/test/api.ts` 会显示在 `src` → `test` 两层文件夹下面。这些自动生成的 `src`、`test` 就是中间文件夹。

> 注意，SCM 视图支持多选，所以命令收到的参数是一个包含一个或多个资源的数组。
>
> 例如，Git 支持一次暂存多个文件，方法是把 `git.stage` 命令添加到 `scm/resourceState/context` 菜单中，并使用这样的方法声明：

```ts
stage(...resourceStates: SourceControlResourceState[]): Promise<void>;
```

`...resourceStates` 是剩余参数的写法，表示“不管传入多少个参数，都收集到一个数组中”。用户选中三个文件后右键执行命令，`resourceStates` 就是这三个文件的资源状态。

> 在创建 `SourceControl` 和 `SourceControlResourceGroup` 实例时，需要提供一个 `id` 字符串。这些值会分别填入 `scmProvider` 和 `scmResourceGroup` 上下文键中。你可以在菜单项的 `when` 子句中依赖这些[上下文键](../references/when-clause-contexts.md)。下面是 Git 为它的 `git.stage` 命令显示一个行内菜单项的方式：

```json
{
  "command": "git.stage",
  "when": "scmProvider == git && scmResourceGroup == merge",
  "group": "inline"
}
```

| 上下文键 | 对应的值 | 示例中 |
|---|---|---|
| `scmProvider` | `createSourceControl` 的第一个参数 `id` | `git` |
| `scmResourceGroup` | `createResourceGroup` 的第一个参数 `id` | `merge`（Git 的“合并冲突”组） |

所以示例的意思是：只有在 Git 的“合并更改”组中的文件上，才显示暂存按钮。这和树视图中用 `viewItem` 区分节点类型是同样的思路。

> `scm/repository` 菜单是**源代码管理存储库**视图中，每个 `SourceControl` 实例上的菜单。把菜单项放在 `inline` 组中，可以让它们显示为行内按钮。其他所有菜单项组，都会显示在 `...` 菜单中。`inline` 组会根据可用的空间渲染，放不下的菜单项会自动移到 `...` 菜单中。
>
> `scm/sourceControl` 菜单是**源代码管理存储库**视图中，每个 `SourceControl` 实例上的上下文菜单：

![源代码管理菜单](images/scm-provider/sourcecontrol-menu.png)

截图中，顶部的 SOURCE CONTROL REPOSITORIES（源代码管理存储库）视图列出了两个仓库；在 `vscode-website` 上右键，弹出的上下文菜单中除了内置的 Close Repository、Open in Integrated Terminal，还有扩展通过 `scm/sourceControl` 添加的 **My Command**。

> `scm/change/title` 让你可以向[快速差异](https://code.visualstudio.com/api/references/vscode-api#QuickDiffProvider)行内差异编辑器的标题栏贡献命令，详见[后文](#quick-diff)。命令会收到以下参数：文档的 URI、文档中的更改数组，以及行内更改差异编辑器当前聚焦的那个更改的索引。例如，下面是贡献到这个菜单中的 Git 命令 `stageChange` 的声明，它使用了一个 `when` 子句，检查 `originalResourceScheme` [上下文键](../references/when-clause-contexts.md)是否等于 `git`：

```ts
async stageChange(uri: Uri, changes: LineChange[], index: number): Promise<void>;
```

`stageChange` 的作用是只暂存文件中的某一处修改，而不是整个文件。`originalResourceScheme == git` 表示“原始版本的 URI 协议是 `git`”，也就是这个差异是由 Git 扩展提供的。

<a id="scm-input-box"></a>
### SCM 输入框（SCM Input Box）

> 源代码管理输入框位于每个源代码管理视图的顶部，让用户可以输入一段消息。你可以获取（和设置）这段消息来执行操作。例如，在 Git 中，它被用作提交框，用户在其中输入提交信息，`git commit` 命令会读取它。

```ts
export interface SourceControlInputBox {
  value: string;
}

export interface SourceControl {
  readonly inputBox: SourceControlInputBox;
}
```

> 用户可以按 <kbd>Ctrl+Enter</kbd>（macOS 上为 <kbd>Cmd+Enter</kbd>）确认任何消息。你可以为 `SourceControl` 实例提供一个 `acceptInputCommand` 来处理这个事件。

```ts
export interface SourceControl {
  readonly acceptInputCommand?: Command;
}
```

组合起来的写法：

```ts
gitSCM.inputBox.placeholder = '提交信息（按 Ctrl+Enter 提交）';   // 输入框的占位提示文字
gitSCM.acceptInputCommand = {
  title: 'Commit',
  command: 'myScm.commit'      // 用户按 Ctrl+Enter 时执行这个命令
};

vscode.commands.registerCommand('myScm.commit', () => {
  const message = gitSCM.inputBox.value;   // 读取用户输入的提交信息
  // ……执行提交……
  gitSCM.inputBox.value = '';              // 提交后清空输入框
});
```

另外还可以设置 `gitSCM.count`，在活动栏的源代码管理图标上显示一个数字徽标（截图中的 4），通常表示有多少个文件发生了变化。

---

<a id="quick-diff"></a>
## 快速差异（Quick Diff）

> VS Code 还支持在编辑器的装订线（gutter）中显示**快速差异**装饰。点击这些装饰会展开一个行内差异视图，你可以向其中贡献上下文命令：

![SCM 快速差异](images/scm-provider/quickdiff.png)

截图中，编辑器第 366 行的行号左侧有一条蓝色竖线（快速差异装饰），表示这一行被修改过。点击后展开行内差异视图：红色是修改前的内容，绿色是修改后的内容；右上角的按钮（暂存、还原、上一处、下一处、关闭）就位于前面介绍的 `scm/change/title` 菜单中。

装订线中的三种颜色：蓝色表示修改的行，绿色表示新增的行，红色小三角表示此处有行被删除。

> 这些装饰由 VS Code 自己计算。你只需要向 VS Code 提供任意给定文件的原始内容。

```ts
export interface SourceControl {
  quickDiffProvider?: QuickDiffProvider;
}
```

> 通过 `QuickDiffProvider` 的 `provideOriginalResource` 方法，你的实现可以告诉 VS Code：与作为参数传入的 `Uri` 对应的原始资源的 `Uri` 是什么。
>
> 将这个 API 与 [`workspace` 命名空间中的 `registerTextDocumentContentProvider` 方法](https://code.visualstudio.com/api/references/vscode-api#workspace)结合使用，后者让你可以为任意资源提供内容，只要给定的 [`Uri`](https://code.visualstudio.com/api/references/vscode-api#Uri) 与它注册的自定义 `scheme` 匹配即可。

**快速差异的实现分两步：**

```text
1. QuickDiffProvider.provideOriginalResource(当前文件的 URI)
     → 返回“原始版本”的 URI，比如 myscm:/src/a.ts（自定义协议）

2. TextDocumentContentProvider（注册了 myscm 协议）
     → 为 myscm:/src/a.ts 提供原始版本的文本内容（比如上一次提交时的内容）

然后 VS Code 自己对比“当前内容”和“原始内容”，计算出差异，画出装订线中的装饰
```

```ts
// 第 1 步：告诉 VS Code 原始版本在哪里
gitSCM.quickDiffProvider = {
  provideOriginalResource(uri: vscode.Uri) {
    return uri.with({ scheme: 'myscm' });   // 同样的路径，换成自定义协议
  }
};

// 第 2 步：为自定义协议提供原始内容（见“虚拟文档”）
vscode.workspace.registerTextDocumentContentProvider('myscm', {
  provideTextDocumentContent(uri) {
    return getContentFromLastCommit(uri.path);   // 示意：读取上一次提交时的文件内容
  }
});
```

这里的第 2 步就是 [虚拟文档](./virtual-documents.md) 一篇的内容。前面“点击文件打开差异对比”时用到的 `originalUri`，也可以用同样的方式提供。

---

<a id="next-steps"></a>
## 下一步（Next steps）

> 要了解更多关于 VS Code 扩展模型的内容，可以看看这些主题：
>
> - [SCM API 参考](https://code.visualstudio.com/api/references/vscode-api#scm)：阅读完整的 SCM API 文档
> - [Git 扩展](https://github.com/microsoft/vscode/tree/main/extensions/git)：通过阅读 Git 扩展的实现来学习
> - [扩展 API 概览](../index.md)：了解完整的 VS Code 扩展模型。
> - [扩展清单文件](../references/extension-manifest.md)：VS Code 扩展清单文件 package.json 的参考
> - [贡献点](../references/contribution-points.md)：VS Code 贡献点参考

官方还有一个 [源代码管理示例](https://github.com/microsoft/vscode-extension-samples/tree/main/source-control-sample)，比 Git 扩展简单得多，更适合入门时阅读。

---

## 本篇小结

```text
模型：SourceControl（仓库）→ ResourceGroup（分组）→ ResourceState（一个文件在该组中的一次变化）
  scm.createSourceControl(id, label, rootUri?)
  sourceControl.createResourceGroup(id, label)
  group.resourceStates = [...]   重新赋值即刷新视图

资源状态：resourceUri、decorations（删除线、淡色、提示……）、command（点击时执行，如 vscode.diff）

菜单（7 个位置）：scm/title、scm/resourceGroup/context、scm/resourceState/context、
                 scm/resourceFolder/context、scm/repository、scm/sourceControl、scm/change/title
  inline / navigation 组显示为按钮；支持多选，命令收到资源数组
  when 中用 scmProvider（SourceControl 的 id）和 scmResourceGroup（组的 id）区分

输入框：inputBox.value 读写消息；acceptInputCommand 处理 Ctrl+Enter

快速差异：quickDiffProvider.provideOriginalResource 返回原始版本的 URI
         + registerTextDocumentContentProvider 提供原始内容 → VS Code 自动计算差异
```
