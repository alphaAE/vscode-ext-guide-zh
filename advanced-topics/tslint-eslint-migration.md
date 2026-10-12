# 从 TSLint 迁移到 ESLint（Migrate from TSLint to ESLint）

> 原文：[Migrate from TSLint to ESLint](https://code.visualstudio.com/api/advanced-topics/tslint-eslint-migration)
> 源文件：`microsoft/vscode-docs` → `api/advanced-topics/tslint-eslint-migration.md`（DateApproved: 10/7/2026）

> [TSLint](https://palantir.github.io/tslint/) 过去是推荐的 linter，但现在 TSLint 已被弃用，[ESLint](https://eslint.org/) 正在接替它的职责。本文将帮助你从 TSLint 迁移到 ESLint。

**先说明适用范围：** 这篇针对的是**老项目**（几年前用旧版 `yo code` 生成、还在用 `tslint.json` 的扩展）。现在用 `yo code` 新建的扩展已经直接配置好了 ESLint，可以跳过本篇。另外，本篇使用的是 ESLint 旧的配置格式（`.eslintrc.js`）和命令参数（`--ext`）。**ESLint 9 起默认使用新的“扁平配置”（`eslint.config.mjs`），`--ext` 参数也已移除。** 迁移时的思路仍然适用，但具体的配置写法建议参考新版 `yo code` 生成的项目和 [typescript-eslint 的入门文档](https://typescript-eslint.io/getting-started)。文末附有新格式的写法。

---

<a id="eslint-installation"></a>
## ESLint：安装（ESLint: Installation）

> 你需要安装 ESLint。ESLint 原生不支持 TypeScript，所以你还需要安装 eslint-typescript-support：

```bash
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

> 或者，如果你使用 yarn 作为包管理器：

```bash
yarn add eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin --dev
```

> 上面的命令添加了 ESLint，添加了一个让 ESLint 理解 TypeScript 的解析器，并添加了一些特定于 TypeScript 的规则。

（原文说的 “eslint-typescript-support” 并不是一个包名，指的就是命令中的 `@typescript-eslint/parser`（解析器）和 `@typescript-eslint/eslint-plugin`（规则）这两个包。）

> 现在，为了让实际的迁移更简单，运行 [tslint-to-eslint-config](https://github.com/typescript-eslint/tslint-to-eslint-config) 工具。这个工具会读取你的 TSLint 配置，并据此创建一个“最接近”的 ESLint 配置。

```bash
npx tslint-to-eslint-config
```

> 这个命令会[下载并执行](https://www.npmjs.com/package/npx)这个工具来完成迁移。关于更多选项，请查看这个工具的[使用指南](https://github.com/typescript-eslint/tslint-to-eslint-config#usage)。
>
> 现在应该会有一个新的 `.eslintrc.js` 文件、一个日志文件（`tslint-to-eslint-config.log`），并且其他文件很可能也有改动，比如 `.vscode/settings.json`。请仔细检查这些改动，尤其是对现有文件所做的改动，并查看日志文件。

（日志文件中会列出无法自动转换的 TSLint 规则，需要你手动找对应的 ESLint 规则或决定放弃。）

---

<a id="eslint-configure"></a>
## ESLint：配置（ESLint: Configure）

> `.eslintrc.js` 文件通常就足以开始使用了，但很可能 `parserOptions.project` 属性仍然指向你的 `tsconfig.json` 文件。这意味着 ESLint 的规则可以使用语义信息，例如，这个变量是一个字符串还是一个数字数组？这个配置启用了一些强大的规则，但也意味着 ESLint 要花更长的时间来计算。扩展的默认规则不需要语义信息，除非你添加了需要语义信息的规则，否则我们建议你删除 `parserOptions.project` 属性。

| | 设置了 `parserOptions.project` | 没有设置 |
|---|---|---|
| ESLint 能否知道变量的类型 | 能（会运行 TypeScript 的类型检查） | 不能，只看语法 |
| 可用的规则 | 包括“需要类型信息”的规则，例如 `@typescript-eslint/no-floating-promises`（检查忘记 `await` 的 Promise） | 只有不需要类型信息的规则 |
| 速度 | 慢 | 快 |

（`no-floating-promises` 在扩展开发中其实挺有用：忘记 `await` 一个 `executeCommand` 或 `showInformationMessage` 是常见的 bug。如果你想要这类规则，就保留 `parserOptions.project`。）

---

<a id="eslint-run"></a>
## ESLint：运行（ESLint: Run）

> 现在你可以运行 ESLint 了，但在这之前，我们建议你禁用 TSLint。为此，打开扩展视图，在 TSLint 扩展的上下文菜单中选择 **Disable**（禁用）。
>
> 是时候进行检查了！使用这个命令：`eslint -c .eslintrc.js --ext .ts <mySrcFolder>`（注意 `--ext .ts` 选项，它告诉 ESLint 去检查 TypeScript 文件）。我们建议把这个命令放到 `package.json` 文件的 `scripts` 部分中，像这样：

```json
"lint": "eslint -c .eslintrc.js --ext .ts <mySrcFolder>"
```

（`<mySrcFolder>` 替换为你的源代码目录，通常是 `src`。）

> 要把 ESLint 与 Visual Studio Code 集成起来，请执行以下操作：
>
> - 安装 [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) 扩展。
> - 通过 **Tasks: Configure Task** 命令创建一个任务，并选择 **npm: lint**。
> - 在生成的 `tasks.json` 文件中，把问题匹配器配置为 `$eslint-stylish`。

```json
{
  "type": "npm",
  "script": "lint",
  "problemMatcher": "$eslint-stylish"
}
```

（ESLint 扩展会在你编辑时实时显示问题；`npm: lint` 任务则用于一次性检查整个项目，问题匹配器把命令行输出转换成“问题”面板中的条目，见 [贡献点](../references/contribution-points.md#contributes.problemMatchers)。）

> **提示**：ESLint 在某些地方有时“更严格”，你可能会看到以前没有的警告，例如指出缺少分号。试试 `--fix` 选项，让 ESLint 为你清理这些问题。

---

<a id="tslint-removal"></a>
## TSLint：移除（TSLint: Removal）

> 恭喜。现在你应该已经有了一个可以正常工作的 ESLint 配置，是时候进行清理了。
>
> TSLint 的移除取决于你的项目，但通常是这些步骤：
>
> - 更新 `.vscode/extensions.json`，推荐 ESLint 扩展，而不再推荐 TSLint：
>
>   ```json
>   "recommendations": [
>     "dbaeumer.vscode-eslint"
>   ]
>   ```
>
> - 删除 `tslint.json` 文件。
> - 删除 `package.json` 文件中对 `tslint` 的依赖。
> - 用 `npm uninstall tslint` 卸载 TSLint。

（后两步其实是一回事：`npm uninstall tslint` 会同时从 `package.json` 中删除依赖。也别忘了删除代码中的 `// tslint:disable` 注释，对应的 ESLint 写法是 `// eslint-disable-next-line 规则名`。）

---

## 补充：ESLint 9 的扁平配置写法

使用 ESLint 9 及以上版本时，配置文件是项目根目录的 `eslint.config.mjs`，一个最小的 TypeScript 扩展配置如下（安装 `npm install --save-dev eslint typescript-eslint`）：

```js
// eslint.config.mjs
import tseslint from 'typescript-eslint';

export default tseslint.config(
  { files: ['src/**/*.ts'] },
  ...tseslint.configs.recommended,
  {
    rules: {
      curly: 'warn',
      eqeqeq: 'warn',
      semi: 'warn',
    },
  },
);
```

```json
"lint": "eslint src"
```

（扁平配置中用 `files` 指定检查哪些文件，不再需要 `-c` 和 `--ext`。具体的规则选择以新版 `yo code` 生成的项目为参考。）

---

## 本篇小结

```text
TSLint 已弃用 → 迁移到 ESLint + typescript-eslint
  1. 安装 eslint、@typescript-eslint/parser、@typescript-eslint/eslint-plugin
  2. npx tslint-to-eslint-config 自动转换配置，检查日志中未转换的规则
  3. 不需要类型信息的规则时，删除 parserOptions.project（更快）
  4. 禁用 TSLint 扩展；scripts 中加 lint 命令；装 ESLint 扩展；任务问题匹配器 $eslint-stylish
  5. 删除 tslint.json、npm uninstall tslint、更新 extensions.json 推荐
注意：ESLint 9+ 使用 eslint.config.mjs 扁平配置，--ext 已移除
```
