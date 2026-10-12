# 树视图 API（Tree View API）

> 原文：[Tree View API](https://code.visualstudio.com/api/extension-guides/tree-view)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/tree-view.md`（DateApproved: 10/7/2026）

> 树视图 API 让扩展可以在 VS Code 的侧边栏中显示内容。这些内容以树形结构组织，样式与 VS Code 的[内置视图](https://code.visualstudio.com/docs/editing/getting-started/userinterface#views)保持一致。
>
> 例如，内置的“引用搜索视图”扩展会在一个单独的视图中显示引用搜索的结果。

![引用搜索视图：以树形列表显示“查找所有引用”的结果](images/tree-view/references-search-tree-view.png)

> **查找所有引用（Find All References）**的结果显示在 **References: Results** 树视图中，这个树视图位于 **References** 视图容器里。

截图中，左侧活动栏最下方的图标（悬停提示 References）就是视图容器；右边的列表按文件分组显示了 12 条引用结果，每个文件节点可以展开、折叠。

> 本指南会教你如何编写一个扩展，向 VS Code 贡献树视图和视图容器。

树视图是扩展最常用的界面部件之一：项目文件、依赖列表、数据库表、接口列表……凡是有层级关系的数据，都适合用树视图展示。在 [扩展工作台](../extension-capabilities/extending-workbench.md) 中我们已经知道，树视图需要“`package.json` 声明 + 代码提供数据”两部分配合，本篇详细讲解具体写法。

---

<a id="tree-view-api-basics"></a>
## 树视图 API 基础（Tree View API Basics）

> 为了讲解树视图 API，我们将构建一个名为 **Node Dependencies** 的示例扩展。这个扩展会用一个树视图显示当前文件夹中所有的 Node.js 依赖。添加树视图的步骤是：在 `package.json` 中贡献树视图，创建一个 `TreeDataProvider`，然后注册这个 `TreeDataProvider`。这个示例扩展的完整源代码在 [vscode-extension-samples](https://github.com/microsoft/vscode-extension-samples/tree/main/tree-view-sample/README.md) GitHub 仓库的 `tree-view-sample` 中。

三个步骤：

```text
1. package.json：用 contributes.views 声明视图（视图 ID + 名称）
2. 代码：实现 TreeDataProvider（告诉 VS Code 树里有哪些节点、每个节点长什么样）
3. 代码：把 TreeDataProvider 注册到视图 ID 上
```

<a id="packagejson-contribution"></a>
<a id="package-json-contribution"></a>
### package.json 中的贡献（package.json Contribution）

> 首先，你需要在 `package.json` 中使用 [contributes.views](../references/contribution-points.md#contributes.views) 贡献点，告诉 VS Code 你要贡献一个视图。
>
> 下面是这个扩展第一个版本的 `package.json`：

```json
{
    "name": "custom-view-samples",
    "displayName": "Custom view Samples",
    "description": "Samples for VS Code's view API",
    "version": "0.0.1",
    "publisher": "alexr00",
    "engines": {
        "vscode": "^1.74.0"
    },
    "activationEvents": [],
    "main": "./out/extension.js",
    "contributes": {
        "views": {
            "explorer": [
                {
                    "id": "nodeDependencies",
                    "name": "Node Dependencies"
                }
            ]
        }
    },
    "scripts": {
        "vscode:prepublish": "npm run compile",
        "compile": "tsc -p ./",
        "watch": "tsc -watch -p ./"
    },
    "devDependencies": {
        "@types/node": "^10.12.21",
        "@types/vscode": "^1.42.0",
        "typescript": "^3.5.1",
        "tslint": "^5.12.1"
    }
}
```

关键部分只有 `contributes.views`：在 `explorer`（资源管理器）中添加一个 ID 为 `nodeDependencies`、名称为 “Node Dependencies” 的视图。示例中的依赖版本比较旧，新项目不用照抄（参见 [扩展的结构](../get-started/extension-anatomy.md) 中的说明）。

> **注意**：如果你的扩展面向 1.74 之前的 VS Code 版本，必须在 `activationEvents` 中显式写上 `onView:nodeDependencies`。

> 你必须为视图指定一个标识符（id）和名称（name），并且可以把它贡献到以下位置：
>
> - `explorer`：侧边栏中的资源管理器视图
> - `debug`：侧边栏中的运行和调试视图
> - `scm`：侧边栏中的源代码管理视图
> - `test`：侧边栏中的测试资源管理器视图
> - [自定义视图容器](#view-container)

| 位置（`views` 下的键名） | 对应活动栏上的哪个图标 |
|---|---|
| `explorer` | 资源管理器 |
| `debug` | 运行和调试 |
| `scm` | 源代码管理 |
| `test` | 测试 |
| 自定义视图容器的 `id` | 你自己创建的图标（见下文[视图容器](#view-container)） |

<a id="tree-data-provider"></a>
### 树数据提供者（Tree Data Provider）

> 第二步是为你注册的视图提供数据，这样 VS Code 才能在视图中显示它们。为此，你首先要实现 [TreeDataProvider](https://code.visualstudio.com/api/references/vscode-api#TreeDataProvider)。我们的 `TreeDataProvider` 会提供 Node 依赖数据，不过你也可以写一个提供其他类型数据的数据提供者。
>
> 这个 API 中有两个必须实现的方法：
>
> - `getChildren(element?: T): ProviderResult<T[]>`：实现这个方法，返回给定 `element` 的子节点；如果没有传入 element，则返回根节点。
> - `getTreeItem(element: T): TreeItem | Thenable<TreeItem>`：实现这个方法，返回元素在视图中显示的界面表示（[TreeItem](https://code.visualstudio.com/api/references/vscode-api#TreeItem)）。

**理解 TreeDataProvider 的关键是区分“数据”和“显示”：**

```text
T（你自己的数据类型）            TreeItem（VS Code 的显示对象）
例如：{ name, version }   ──getTreeItem──→   label、图标、描述、是否可展开……
        │
        └──getChildren──→ 这个节点的子节点（也是 T 的数组）
```

- `T` 是你自己定义的数据类型，可以是任何东西：一个字符串、一个对象、一个类的实例；
- `getChildren` 负责**数据结构**：给我某个节点，返回它的子节点；
- `getTreeItem` 负责**显示**：给我某个节点，返回它在界面上的样子。

VS Code 不会一次性要你提供整棵树，而是**用户展开到哪里，就问到哪里**（懒加载）：

```text
视图打开时         → getChildren(undefined)  得到根节点 [A, B, C]
                  → 对 A、B、C 分别调用 getTreeItem，显示出来
用户展开 A 时      → getChildren(A)          得到 A 的子节点 [A1, A2]
                  → 对 A1、A2 分别调用 getTreeItem
```

所以即使数据量很大（比如几万个文件），只要用户不展开，就不会去加载。

> 当用户打开树视图时，会在不传入 `element` 的情况下调用 `getChildren` 方法。这时，你的 `TreeDataProvider` 应该返回顶层的树节点。在我们的示例中，顶层树节点的 `collapsibleState` 是 `TreeItemCollapsibleState.Collapsed`，表示顶层节点会显示为折叠状态。把 `collapsibleState` 设为 `TreeItemCollapsibleState.Expanded` 会让节点显示为展开状态。让 `collapsibleState` 保持默认值 `TreeItemCollapsibleState.None`，表示这个节点没有子节点。对于 `collapsibleState` 为 `TreeItemCollapsibleState.None` 的节点，不会调用 `getChildren`。

| `collapsibleState` | 显示效果 | 会调用 `getChildren` 吗 |
|---|---|---|
| `None`（默认） | 没有展开箭头，是叶子节点 | 不会 |
| `Collapsed` | 有箭头，初始为折叠 | 用户展开时调用 |
| `Expanded` | 有箭头，初始为展开 | 显示时立即调用 |

**常见错误：** 节点明明有子节点，却忘了设置 `collapsibleState`，结果节点前面没有箭头、无法展开。这是因为默认值是 `None`，VS Code 认为它是叶子节点，根本不会去调用 `getChildren`。

> 下面是一个提供 Node 依赖数据的 `TreeDataProvider` 实现示例：

```ts
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class NodeDependenciesProvider implements vscode.TreeDataProvider<Dependency> {

    constructor(private workspaceRoot: string) {}

    // 节点本身就是 TreeItem（Dependency 继承自 TreeItem），直接返回即可
    getTreeItem(element: Dependency): vscode.TreeItem {
        return element;
    }

    getChildren(element?: Dependency): Thenable<Dependency[]> {
        if (!this.workspaceRoot) {
            vscode.window.showInformationMessage('No dependency in empty workspace');
            return Promise.resolve([]);
        }

        if (element) {
            // 有 element：返回这个依赖包自己的依赖（读取 node_modules/包名/package.json）
            return Promise.resolve(this.getDepsInPackageJson(path.join(this.workspaceRoot, 'node_modules', element.label, 'package.json')));
        } else {
            // 没有 element：返回根节点，即工作区 package.json 中的依赖
            const packageJsonPath = path.join(this.workspaceRoot, 'package.json');
            if (this.pathExists(packageJsonPath)) {
                return Promise.resolve(this.getDepsInPackageJson(packageJsonPath));
            } else {
                vscode.window.showInformationMessage('Workspace has no package.json');
                return Promise.resolve([]);
            }
        }

    }

    /**
     * 根据 package.json 的路径，读取其中所有的 dependencies 和 devDependencies。
     */
    private getDepsInPackageJson(packageJsonPath: string): Dependency[] {
        if (this.pathExists(packageJsonPath)) {
            const toDep = (moduleName: string, version: string): Dependency => {
                // 依赖包已安装（node_modules 中存在）时可以展开，否则作为叶子节点
                if (this.pathExists(path.join(this.workspaceRoot, 'node_modules', moduleName))) {
                    return new Dependency(moduleName, version, vscode.TreeItemCollapsibleState.Collapsed);
                } else {
                    return new Dependency(moduleName, version, vscode.TreeItemCollapsibleState.None);
                }
            };

            const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));

            const deps = packageJson.dependencies
                ? Object.keys(packageJson.dependencies).map(dep => toDep(dep, packageJson.dependencies[dep]))
                : [];
            const devDeps = packageJson.devDependencies
                ? Object.keys(packageJson.devDependencies).map(dep => toDep(dep, packageJson.devDependencies[dep]))
                : [];
            return deps.concat(devDeps);
        } else {
            return [];
        }
    }

    private pathExists(p: string): boolean {
        try {
            fs.accessSync(p);
        } catch (err) {
            return false;
        }
        return true;
    }
}

// 树节点：继承 TreeItem，同时携带自己的数据（version）
class Dependency extends vscode.TreeItem {

    constructor(
        public readonly label: string,
        private version: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
    ) {
        super(label, collapsibleState);
        this.tooltip = `${this.label}-${this.version}`;  // 鼠标悬停时显示的提示
        this.description = this.version;                 // 显示在名称右侧的灰色文字
    }

    // 浅色主题和深色主题使用不同的图标
    iconPath = {
        light: path.join(__filename, '..', '..', 'resources', 'light', 'dependency.svg'),
        dark: path.join(__filename, '..', '..', 'resources', 'dark', 'dependency.svg')
    };

}
```

**这个示例的设计：** `Dependency` 继承了 `TreeItem`，所以它**既是数据，又是显示对象**，`getTreeItem` 直接返回它本身。这是一种简便的写法。另一种写法是 `T` 只存纯数据，在 `getTreeItem` 中再创建 `TreeItem`，数据和显示分离得更清楚。两种都可以。

**`TreeItem` 的常用属性：**

| 属性 | 作用 | 示例中的用法 |
|---|---|---|
| `label` | 节点名称 | 包名 |
| `description` | 名称右侧的灰色文字 | 版本号 |
| `tooltip` | 鼠标悬停时的提示 | `包名-版本号` |
| `iconPath` | 图标 | 浅色、深色主题各一个 SVG |
| `collapsibleState` | 是否可展开 | 已安装的包可展开 |
| `contextValue` | 节点的“类型标记”，用于控制菜单显示 | 见下文[视图操作](#view-actions) |
| `command` | 点击节点时执行的命令 | 例如点击后打开某个文件 |
| `resourceUri` | 节点对应的文件 | 设置后会自动使用文件图标主题中的图标 |
| `id` | 节点的唯一 ID | 用来在刷新时保持节点的展开、选中状态 |
| `checkboxState` | 在节点前显示复选框 | |

**原文代码在新版本中的两个问题：**

1. **`iconPath` 的类型。** 在当前的类型定义（`@types/vscode` 1.140）中，`light` / `dark` 必须是 `Uri`，不能是字符串路径。直接照抄原文代码，TypeScript 会报类型错误。应该改成：

    ```ts
    iconPath = {
        light: vscode.Uri.file(path.join(__filename, '..', '..', 'resources', 'light', 'dependency.svg')),
        dark: vscode.Uri.file(path.join(__filename, '..', '..', 'resources', 'dark', 'dependency.svg'))
    };
    ```

    更简单的做法是使用内置图标（codicon），不需要准备图片文件，而且会自动适配主题颜色：

    ```ts
    iconPath = new vscode.ThemeIcon('package');
    ```

2. **`path.join(__filename, '..', '..', ...)`** 的意思是从编译后的 `out/xxx.js` 往上两级到扩展根目录，再进入 `resources` 目录。这种写法依赖编译输出的目录结构；如果用了打包工具，结构变了就会找不到文件。更稳妥的做法是用 `context.extensionUri` 拼接路径：`vscode.Uri.joinPath(context.extensionUri, 'resources', 'light', 'dependency.svg')`。

<a id="registering-the-treedataprovider"></a>
### 注册 TreeDataProvider（Registering the TreeDataProvider）

> 第三步是把上面的数据提供者注册到你的视图上。
>
> 有以下两种方式：
>
> - `vscode.window.registerTreeDataProvider`：传入已注册的视图 ID 和上面的数据提供者，注册树数据提供者。

```typescript
const rootPath = (vscode.workspace.workspaceFolders && (vscode.workspace.workspaceFolders.length > 0))
	? vscode.workspace.workspaceFolders[0].uri.fsPath : undefined;
vscode.window.registerTreeDataProvider('nodeDependencies', new NodeDependenciesProvider(rootPath));
```

> - `vscode.window.createTreeView`：传入已注册的视图 ID 和上面的数据提供者，创建树视图。这样你就能拿到 [TreeView](https://code.visualstudio.com/api/references/vscode-api#TreeView) 对象，可以用它执行其他视图操作。如果你需要 `TreeView` 的 API，就使用 `createTreeView`。

```typescript
vscode.window.createTreeView('nodeDependencies', { treeDataProvider: new NodeDependenciesProvider(rootPath)});
```

两种方式的区别：

| | `registerTreeDataProvider` | `createTreeView` |
|---|---|---|
| 返回值 | `Disposable` | `TreeView` 对象（它本身也是 Disposable） |
| 能做什么 | 只提供数据 | 提供数据，还能控制视图：获取选中项、定位到某个节点、设置标题和提示文字、监听展开折叠等 |
| 额外选项 | 无 | `showCollapseAll`（标题栏显示“全部折叠”按钮）、`canSelectMany`（允许多选）、`dragAndDropController`（拖放） |
| 适合 | 简单的只读列表 | 需要和视图交互的场景 |

**说明：**

- `rootPath` 的写法是“有打开的文件夹就取第一个文件夹的路径，否则为 `undefined`”。`workspaceFolders` 是一个数组，因为 VS Code 支持同时打开多个文件夹（多根工作区）。
- 示例中构造函数参数声明为 `string`，却可能传入 `undefined`。开启 TypeScript 严格模式时会报错，可以把参数类型改为 `string | undefined`。
- 实际项目中，记得把返回值放进 `context.subscriptions`。

> 下面是扩展运行的效果：

![扩展运行效果：资源管理器中出现 Node Dependencies 视图，列出依赖包及其版本](images/tree-view/view.png)

截图中，资源管理器下方红框里就是新增的 NODE DEPENDENCIES 视图：每一行是一个依赖包，右侧的灰色文字是版本号（即 `description`）；已安装的包可以展开，查看它自己的依赖。

<a id="updating-tree-view-content"></a>
### 更新树视图的内容（Updating Tree View content）

> 我们的 Node 依赖视图很简单，数据显示出来后就不会再更新了。不过，如果视图中有一个刷新按钮，能按照 `package.json` 的当前内容更新 Node 依赖视图，会很有用。为此，我们可以使用 `onDidChangeTreeData` 事件。
>
> - `onDidChangeTreeData?: Event<T | undefined | null | void>`：如果你的树数据会变化，并且你希望更新树视图，就实现这个事件。
>
> 把下面的代码添加到 `NodeDependenciesProvider` 中。

```ts
  private _onDidChangeTreeData: vscode.EventEmitter<Dependency | undefined | null | void> = new vscode.EventEmitter<Dependency | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<Dependency | undefined | null | void> = this._onDidChangeTreeData.event;

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }
```

**这是 VS Code API 中非常常见的“事件发射器”写法，后面会反复见到：**

```text
_onDidChangeTreeData（EventEmitter，私有）  ← 自己用：调用 .fire() 发出事件
        │ .event
        ▼
onDidChangeTreeData（Event，公开）           ← 给 VS Code 用：VS Code 订阅它
```

- `EventEmitter` 是事件的“发送端”，留在类内部，只有自己能调用 `fire()`；
- `.event` 是事件的“订阅端”，公开给外部。VS Code 看到你的 Provider 有 `onDidChangeTreeData`，就会订阅它；
- 调用 `fire()` 后，VS Code 收到通知，会重新调用 `getChildren` 来获取最新数据。

**`fire()` 的参数决定刷新范围：**

| 调用方式 | 刷新范围 |
|---|---|
| `fire()` 或 `fire(undefined)` | 刷新整棵树（从根节点重新获取） |
| `fire(某个节点)` | 只刷新这个节点及其子节点 |
| `fire([节点1, 节点2])` | 刷新多个节点（当前类型定义还支持传数组） |

数据量大时，只刷新发生变化的节点，性能更好。

> 现在我们有了一个刷新方法，但还没有地方调用它。我们可以添加一个命令来调用 refresh。
>
> 在 `package.json` 的 `contributes` 部分中添加：

```json
    "commands": [
            {
                "command": "nodeDependencies.refreshEntry",
                "title": "Refresh",
                "icon": {
                    "light": "resources/light/refresh.svg",
                    "dark": "resources/dark/refresh.svg"
                }
            },
    ]
```

（这段是从完整配置中截取的片段，末尾多余的逗号在完整的 JSON 中需要去掉。）

> 然后在扩展激活时注册这个命令：

```ts
import * as vscode from 'vscode';
import { NodeDependenciesProvider } from './nodeDependencies';

export function activate(context: vscode.ExtensionContext) {
    const rootPath = (vscode.workspace.workspaceFolders && (vscode.workspace.workspaceFolders.length > 0))
		? vscode.workspace.workspaceFolders[0].uri.fsPath : undefined;
    const nodeDependenciesProvider = new NodeDependenciesProvider(rootPath);
    vscode.window.registerTreeDataProvider('nodeDependencies', nodeDependenciesProvider);
    vscode.commands.registerCommand('nodeDependencies.refreshEntry', () => nodeDependenciesProvider.refresh());
}
```

> 现在我们有了一个能刷新 Node 依赖视图的命令，但如果视图上有一个按钮就更好了。我们已经给命令添加了 `icon`，所以把它添加到视图上时，就会以这个图标显示。
>
> 在 `package.json` 的 `contributes` 部分中添加：

```json
"menus": {
    "view/title": [
        {
            "command": "nodeDependencies.refreshEntry",
            "when": "view == nodeDependencies",
            "group": "navigation"
        },
    ]
}
```

这样，视图的标题栏右侧就会出现一个刷新按钮。三处配置的配合：

| 配置 | 作用 |
|---|---|
| `commands` 中的 `icon` | 命令显示成按钮时用什么图标 |
| `menus.view/title` | 把命令放到视图标题栏上 |
| `"when": "view == nodeDependencies"` | 只在 `nodeDependencies` 这个视图上显示（否则所有视图的标题栏都会出现这个按钮） |
| `"group": "navigation"` | 直接显示为图标按钮，而不是收进 `...` 菜单 |

命令的 `icon` 同样可以用内置图标，写成 `"icon": "$(refresh)"`，就不用准备浅色、深色两套 SVG 了。

**自动刷新：** 除了手动点按钮，还可以在数据变化时自动刷新。比如监听 `package.json` 的变化：

```ts
const watcher = vscode.workspace.createFileSystemWatcher('**/package.json');
watcher.onDidChange(() => nodeDependenciesProvider.refresh());
context.subscriptions.push(watcher);
```

---

<a id="activation"></a>
## 激活（Activation）

> 很重要的一点是：只有当用户需要你的扩展提供的功能时，才激活扩展。在这个例子中，应该考虑只在用户开始使用视图时才激活扩展。当你的扩展声明了视图贡献时，VS Code 会自动帮你做到这一点：用户打开视图时，VS Code 会发出激活事件 [onView:${viewId}](../references/activation-events.md#onView)（上面的例子中是 `onView:nodeDependencies`）。

> **注意**：对于 1.74.0 之前的 VS Code 版本，你必须在 `package.json` 中显式注册这个激活事件，VS Code 才会在打开这个视图时激活你的扩展：
>
> ```json
> "activationEvents": [
>         "onView:nodeDependencies",
> ],
> ```

和命令一样，1.74 之后视图的激活事件会根据 `contributes.views` 自动生成。

**注意一个细节：** 如果视图默认处于折叠状态，或者用户还没切换到它所在的视图容器，视图就没有“打开”，扩展也就不会激活。所以不要在别的功能里假设“视图一定已经注册好了 Provider”。

---

<a id="view-container"></a>
## 视图容器（View Container）

> 视图容器包含一组视图，它和内置的视图容器一起显示在活动栏或面板中。内置视图容器的例子有源代码管理和资源管理器。

![视图容器：活动栏中新增的图标](images/tree-view/view-container.png)

截图中，活动栏最下方红框里的列表图标就是新增的视图容器，点击后侧边栏显示 PACKAGE EXPLORER 容器中的视图。

> 要贡献一个视图容器，首先要在 `package.json` 中使用 [contributes.viewsContainers](../references/contribution-points.md#contributes.viewsContainers) 贡献点注册它。
>
> 你必须指定以下必填字段：
>
> - `id`：你创建的新视图容器的 ID。
> - `title`：显示在视图容器顶部的名称。
> - `icon`：视图容器在活动栏中显示的图片。

```json
"contributes": {
  "viewsContainers": {
    "activitybar": [
      {
        "id": "package-explorer",
        "title": "Package Explorer",
        "icon": "media/dep.svg"
      }
    ]
  }
}
```

活动栏图标的建议：使用 **24×24 像素、单色的 SVG**。VS Code 会根据主题自动给它着色，所以图标的颜色本身不重要。也可以直接写成内置图标，如 `"icon": "$(package)"`。

> 你也可以把它放在 `panel` 节点下，把这个视图容器贡献到面板中。

```json
"contributes": {
  "viewsContainers": {
    "panel": [
      {
        "id": "package-explorer",
        "title": "Package Explorer",
        "icon": "media/dep.svg"
      }
    ]
  }
}
```

放在 `panel` 下的容器会出现在底部面板中，和“终端”“输出”“问题”等并列显示为一个标签页。

---

<a id="contributing-views-to-view-containers"></a>
## 向视图容器中贡献视图（Contributing views to View Containers）

> 创建好视图容器之后，就可以在 `package.json` 中使用 [contributes.views](../references/contribution-points.md#contributes.views) 贡献点了。

```json
"contributes": {
  "views": {
    "package-explorer": [
      {
        "id": "nodeDependencies",
        "name": "Node Dependencies",
        "icon": "media/dep.svg",
        "contextualTitle": "Package Explorer"
      }
    ]
  }
}
```

`views` 下的键名 `package-explorer` 就是上面视图容器的 `id`，这样视图就放进了这个容器。

| 字段 | 作用 |
|---|---|
| `id` | 视图 ID，注册 TreeDataProvider 时用的就是它 |
| `name` | 视图名称，显示在视图标题上 |
| `icon` | 视图的图标。视图被用户拖到其他位置、单独显示时会用到 |
| `contextualTitle` | 视图离开原来的容器后，用来说明它来自哪里的标题 |

`icon` 和 `contextualTitle` 的用途：VS Code 允许用户把视图拖到别的地方，比如从你的容器拖到底部面板。这时视图就离开了原来的容器，VS Code 需要用 `icon` 和 `contextualTitle` 来标识它。

> 视图还可以有一个可选的 `visibility` 属性，可以设为 `visible`、`collapsed` 或 `hidden`。VS Code 只在第一次打开包含这个视图的工作区时才会遵循这个属性。之后，可见性由用户的选择决定。如果你的视图容器中有很多视图，或者你的视图不是对扩展的每个用户都有用，可以考虑把视图设为 `collapsed` 或 `hidden`。设为 `hidden` 的视图会出现在视图容器的“视图”菜单中：

![视图菜单：资源管理器的 ... 菜单中列出了可以显示或隐藏的视图](images/tree-view/views-menu.png)

截图中，点击资源管理器标题栏的 `...`，菜单里列出了各个视图，打勾的是当前显示的。NPM Scripts 没有打勾，说明它是隐藏的，用户可以在这里勾选来显示它。

| `visibility` | 第一次打开工作区时 |
|---|---|
| `visible`（默认） | 显示并展开 |
| `collapsed` | 显示，但处于折叠状态 |
| `hidden` | 不显示，用户可以在“视图”菜单中手动打开 |

---

<a id="view-actions"></a>
## 视图操作（View Actions）

> 操作可以显示在三个位置：单个树节点上的行内图标、树节点的上下文菜单，以及视图顶部的标题栏。操作就是命令，通过在 `package.json` 中添加贡献，让它们显示在这些位置。
>
> 要贡献到这三个位置，可以在 package.json 中使用以下菜单贡献点：
>
> - `view/title`：在视图标题栏中显示操作的位置。主要操作或行内操作使用 `"group": "navigation"`，其余的是次要操作，放在 `...` 菜单中。
> - `view/item/context`：为树节点显示操作的位置。行内操作使用 `"group": "inline"`，其余的是次要操作，放在 `...` 菜单中。
>
> 你可以用 [when 子句](../references/when-clause-contexts.md) 控制这些操作是否可见。

![视图操作：标题栏上的按钮、... 菜单中的命令、节点上的行内按钮和右键菜单](images/tree-view/view-actions.png)

截图中用红字标出了四个操作的位置和配置：

| 操作 | 显示在哪里 | 菜单位置 | group |
|---|---|---|---|
| 刷新（↻ 图标） | 标题栏上的图标按钮 | `view/title` | `navigation` |
| Add | 标题栏的 `...` 菜单中 | `view/title` | 不设置 |
| 编辑（✎ 图标） | 鼠标悬停在节点上时出现的行内按钮 | `view/item/context` | `inline` |
| Delete | 节点的右键菜单中 | `view/item/context` | 不设置 |

> 示例：

```json
"contributes": {
  "commands": [
    {
      "command": "nodeDependencies.refreshEntry",
      "title": "Refresh",
      "icon": {
        "light": "resources/light/refresh.svg",
        "dark": "resources/dark/refresh.svg"
      }
    },
    {
      "command": "nodeDependencies.addEntry",
      "title": "Add"
    },
    {
      "command": "nodeDependencies.editEntry",
      "title": "Edit",
      "icon": {
        "light": "resources/light/edit.svg",
        "dark": "resources/dark/edit.svg"
      }
    },
    {
      "command": "nodeDependencies.deleteEntry",
      "title": "Delete"
    }
  ],
  "menus": {
    "view/title": [
      {
        "command": "nodeDependencies.refreshEntry",
        "when": "view == nodeDependencies",
        "group": "navigation"
      },
      {
        "command": "nodeDependencies.addEntry",
        "when": "view == nodeDependencies"
      }
    ],
    "view/item/context": [
      {
        "command": "nodeDependencies.editEntry",
        "when": "view == nodeDependencies && viewItem == dependency",
        "group": "inline"
      },
      {
        "command": "nodeDependencies.deleteEntry",
        "when": "view == nodeDependencies && viewItem == dependency"
      }
    ]
  }
}
```

注意：要显示为图标按钮（`navigation` 或 `inline`）的命令，必须设置 `icon`，否则会显示成文字。上例中 Add 和 Delete 没有图标，所以放在菜单里。

> 默认情况下，操作按字母顺序排列。要指定不同的顺序，可以在组名后面加上 `@` 和你想要的序号。例如，`navigation@3` 会让这个操作在 `navigation` 组中排第 3 位。
>
> 你还可以创建不同的组，进一步把 `...` 菜单中的条目分隔开。组名可以任意取，各组按组名的字母顺序排列。

```json
"view/title": [
  { "command": "myExt.refresh",  "when": "view == myView", "group": "navigation@1" },
  { "command": "myExt.collapse", "when": "view == myView", "group": "navigation@2" },
  { "command": "myExt.export",   "when": "view == myView", "group": "1_file" },
  { "command": "myExt.settings", "when": "view == myView", "group": "2_config" }
]
```

`...` 菜单中，`1_file` 组和 `2_config` 组之间会显示一条分隔线。用数字前缀给组命名（如 `1_`、`2_`），就能控制各组的先后顺序。

> **注意：** 如果你只想为特定的树节点显示某个操作，可以用 `TreeItem.contextValue` 定义树节点的上下文，然后在 `when` 表达式中为键 `viewItem` 指定这个上下文值。
>
> 示例：

```json
"contributes": {
  "menus": {
    "view/item/context": [
      {
        "command": "nodeDependencies.deleteEntry",
        "when": "view == nodeDependencies && viewItem == dependency"
      }
    ]
  }
}
```

**`contextValue` 和 `viewItem` 是怎么配合的：**

```ts
// 代码中：给节点打上“类型标记”
class Dependency extends vscode.TreeItem {
  contextValue = 'dependency';
}
```

```text
节点的 contextValue = 'dependency'
        ↓
when 子句中的 viewItem 就等于 'dependency'
        ↓
viewItem == dependency 成立，这个菜单项对该节点显示
```

这样就可以让不同类型的节点显示不同的菜单。例如文件节点显示“打开”，文件夹节点显示“新建文件”。

一个节点有多种状态时，可以把多个标记拼在一个字符串里，再用正则匹配：

```ts
item.contextValue = 'dependency installed';          // 同时具有两个标记
```

```json
"when": "view == nodeDependencies && viewItem =~ /installed/"
```

`=~` 是 when 子句中的正则匹配运算符，详见 [when 子句上下文](../references/when-clause-contexts.md)。

**菜单命令收到的参数：** 从 `view/item/context` 菜单触发命令时，处理函数的第一个参数就是被点击的节点（也就是你在 `getChildren` 中返回的那个 `T` 对象）：

```ts
vscode.commands.registerCommand('nodeDependencies.deleteEntry', (node: Dependency) => {
  vscode.window.showInformationMessage(`删除 ${node.label}`);
});
```

---

<a id="welcome-content"></a>
## 欢迎内容（Welcome content）

> 如果你的视图可能为空，或者你想给其他扩展的空视图添加欢迎内容，可以贡献 `viewsWelcome` 内容。空视图是指没有 `TreeView.message`、并且树为空的视图。

```json
"contributes": {
  "viewsWelcome": [
    {
      "view": "nodeDependencies",
      "contents": "No node dependencies found [learn more](https://www.npmjs.com/).\n[Add Dependency](command:nodeDependencies.addEntry)"
    }
  ]
}
```

![欢迎内容：空视图中显示一行说明文字和一个 Add Dependency 按钮](images/tree-view/welcome-content.png)

> 欢迎内容中支持链接。按照惯例，单独占一行的链接会显示为按钮。每条欢迎内容还可以包含一个 `when` 子句。更多示例可以参考[内置的 Git 扩展](https://github.com/microsoft/vscode/tree/main/extensions/git)。

对照截图看 `contents` 的写法：

| `contents` 中的内容 | 显示效果 |
|---|---|
| `No node dependencies found [learn more](https://www.npmjs.com/).` | 一行文字，其中 learn more 是普通链接 |
| `\n` | 换行 |
| `[Add Dependency](command:nodeDependencies.addEntry)` | 这个链接单独占一行，所以显示为按钮；点击执行命令 |

按钮链接用的就是 [命令指南](./command.md) 中介绍的**命令 URI**（`command:命令ID`）。

**典型用途：** 打开新安装的扩展时，视图往往是空的（比如还没登录、还没打开项目）。与其显示一片空白，不如显示一段说明和一个“登录”或“打开文件夹”按钮，引导用户进行下一步。配合 `when` 子句，还可以根据不同状态显示不同的欢迎内容：

```json
"viewsWelcome": [
  { "view": "myView", "contents": "请先登录。\n[登录](command:myExt.login)", "when": "!myExt.loggedIn" },
  { "view": "myView", "contents": "还没有数据。\n[刷新](command:myExt.refresh)", "when": "myExt.loggedIn" }
]
```

这里的 `myExt.loggedIn` 就是用 `setContext` 设置的自定义上下文键（见[命令指南](./command.md#using-a-custom-when-clause-context)）。

---

<a id="TreeDataProvider"></a>
## TreeDataProvider

> 扩展作者应该在代码中注册一个 [TreeDataProvider](https://code.visualstudio.com/api/references/vscode-api#TreeDataProvider)，用来为视图填充数据。

```typescript
vscode.window.registerTreeDataProvider('nodeDependencies', new DepNodeProvider());
```

> 具体实现请参阅 `tree-view-sample` 中的 [nodeDependencies.ts](https://github.com/microsoft/vscode-extension-samples/tree/main/tree-view-sample/src/nodeDependencies.ts)。

`TreeDataProvider` 接口的全部成员：

| 成员 | 是否必须 | 作用 |
|---|---|---|
| `getChildren(element?)` | 必须 | 返回子节点；不传 element 时返回根节点 |
| `getTreeItem(element)` | 必须 | 返回节点的显示对象 |
| `onDidChangeTreeData` | 可选 | 数据变化时通知 VS Code 刷新 |
| `getParent(element)` | 可选 | 返回节点的父节点。要使用 `TreeView.reveal` 定位节点时**必须**实现 |
| `resolveTreeItem(item, element, token)` | 可选 | 延迟补充节点信息（例如悬停时才去加载 `tooltip`），用于优化性能 |

---

<a id="TreeView"></a>
## TreeView

> 如果你想通过代码对视图执行一些界面操作，可以使用 `window.createTreeView` 代替 `window.registerTreeDataProvider`。这样你就能拿到视图对象，用它来执行视图操作。

```typescript
vscode.window.createTreeView('ftpExplorer', {
  treeDataProvider: new FtpTreeDataProvider()
});
```

> 具体实现请参阅 `tree-view-sample` 中的 [ftpExplorer.ts](https://github.com/microsoft/vscode-extension-samples/tree/main/tree-view-sample/src/ftpExplorer.ts)。

`TreeView` 对象的常用成员（以 `@types/vscode` 1.140 为准）：

| 成员 | 作用 |
|---|---|
| `selection` / `onDidChangeSelection` | 当前选中的节点 / 选中项变化事件 |
| `visible` / `onDidChangeVisibility` | 视图是否可见 / 可见性变化事件 |
| `onDidExpandElement` / `onDidCollapseElement` | 节点展开 / 折叠事件 |
| `onDidChangeCheckboxState` | 复选框状态变化事件 |
| `reveal(element, options)` | 滚动到并选中、展开某个节点（需要 Provider 实现 `getParent`） |
| `message` | 显示在视图顶部的一段提示文字 |
| `title` / `description` | 修改视图的标题，以及标题旁的灰色描述文字 |
| `badge` | 在视图容器图标上显示的数字徽标（像源代码管理图标上的修改数量） |

```ts
const treeView = vscode.window.createTreeView('nodeDependencies', {
  treeDataProvider: nodeDependenciesProvider,
  showCollapseAll: true,   // 标题栏显示“全部折叠”按钮
});
context.subscriptions.push(treeView);

treeView.onDidChangeSelection(e => {
  console.log('选中了', e.selection);
});

treeView.message = '共 12 个依赖';
treeView.badge = { value: 3, tooltip: '3 个依赖有更新' };
```

---

## 本篇小结

```text
1. package.json
   ├─ viewsContainers：（可选）在活动栏 / 面板中新增一个容器图标
   ├─ views：在容器中声明视图（id、name、visibility……）
   ├─ menus.view/title：视图标题栏上的按钮（navigation）和 ... 菜单
   ├─ menus.view/item/context：节点上的行内按钮（inline）和右键菜单
   │     └─ 用 viewItem == xxx 区分节点类型（对应 TreeItem.contextValue）
   └─ viewsWelcome：视图为空时显示的说明和按钮

2. TreeDataProvider<T>
   ├─ getChildren(element?)：返回子节点（懒加载，展开到哪里问到哪里）
   ├─ getTreeItem(element)：返回显示对象（label、description、icon、collapsibleState……）
   ├─ onDidChangeTreeData：EventEmitter.fire() 通知刷新
   └─ getParent：使用 reveal 时需要

3. 注册
   ├─ registerTreeDataProvider：只提供数据
   └─ createTreeView：还能控制视图（选中、定位、标题、徽标……）

常见坑：有子节点却忘了设 collapsibleState；iconPath 的 light/dark 要用 Uri；按钮命令没设 icon
```
