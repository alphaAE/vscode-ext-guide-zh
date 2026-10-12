# 持续集成（Continuous Integration）

> 原文：[Continuous Integration](https://code.visualstudio.com/api/working-with-extensions/continuous-integration)
> 源文件：`microsoft/vscode-docs` → `api/working-with-extensions/continuous-integration.md`（DateApproved: 10/7/2026）

> 扩展的集成测试可以在 CI 服务上运行。[`@vscode/test-electron`](https://github.com/microsoft/vscode-test) 库可以帮你在 CI 提供商上设置扩展测试，它还包含一个在 Azure Pipelines 上设置好的[示例扩展](https://github.com/microsoft/vscode-test/tree/main/sample)。你可以查看它的[构建流水线](https://dev.azure.com/vscode/vscode-test/_build?definitionId=15)，或者直接跳到 [`azure-pipelines.yml` 文件](https://github.com/microsoft/vscode-test/blob/main/sample/azure-pipelines.yml)。

**CI（持续集成）** 指的是每次推送代码时，由云端的服务器自动运行构建和测试。对扩展来说，最大的好处是可以在 Windows、macOS、Linux 三个平台上都跑一遍 [集成测试](./testing-extension.md)，而你手边通常只有其中一种系统。

本篇介绍三种 CI 服务的配置，结构相同，按需选一种即可：

| CI 服务 | 配置文件 | 下文小节 |
|---|---|---|
| Azure Pipelines | `azure-pipelines.yml` | [Azure Pipelines](#azure-pipelines) |
| GitHub Actions | `.github/workflows/*.yml` | [GitHub Actions](#github-actions) |
| GitLab CI | `.gitlab-ci.yml` | [GitLab CI](#gitlab-ci) |

---

<a id="automated-publishing"></a>
## 自动发布（Automated publishing）

> 你也可以配置 CI，让它自动发布扩展的新版本。
>
> 发布命令与在本地环境中使用 [`vsce`](https://github.com/microsoft/vscode-vsce) 发布类似，但你必须以某种安全的方式提供个人访问令牌（PAT）。把 PAT 存储为一个名为 `VSCE_PAT` 的**机密变量**，`vsce` 就能使用它。机密变量永远不会被暴露，所以在 CI 流水线中使用它们是安全的。

**PAT（Personal Access Token，个人访问令牌）** 是发布扩展到市场时用的凭证，创建方法见 [发布扩展](./publishing-extension.md#get-a-personal-access-token)。`vsce publish` 在没有通过 `-p` 参数传入令牌时，会自动读取环境变量 `VSCE_PAT`。所以三种 CI 的做法都一样：

```text
1. 在 CI 服务的设置中，把 PAT 保存为机密变量 VSCE_PAT（不要写进代码仓库！）
2. 把 @vscode/vsce 装为开发依赖，在 package.json 中加一个 deploy 脚本：vsce publish
3. 让 CI 在推送标签（如 v1.2.0）时也运行
4. 加一个发布步骤：仅在测试通过、并且是标签构建时运行 deploy，把机密变量映射为环境变量 VSCE_PAT
```

这样，日常推送只会运行测试；需要发布时，打一个标签推上去（`git tag v1.2.0 && git push origin v1.2.0`），CI 测试通过后就会自动发布。

**时效性提醒：** 本篇的自动发布都基于 PAT。根据 [发布扩展](./publishing-extension.md#publishing-extensions) 一篇中的公告，Azure DevOps 的**全局 PAT 将于 2026 年 12 月 1 日停用**，而发布到市场所需的正是全局 PAT（“All accessible organizations”）。在 Azure Pipelines 中，可以改用 [基于 Microsoft Entra ID 托管标识的发布](./publishing-extension.md#secure-automated-publishing-to-visual-studio-marketplace)（`vsce publish --azure-credential`）；其他 CI 服务的替代方案，请关注该公告的后续说明。

---

<a id="azure-pipelines"></a>
## Azure Pipelines

<a href="https://azure.microsoft.com/services/devops/"><img alt="Azure Pipelines" src="images/continuous-integration/pipelines-logo.png" width="318" /></a>

> [Azure Pipelines](https://azure.microsoft.com/services/devops/pipelines/) 非常适合运行 VS Code 扩展测试，因为它支持在 Windows、macOS 和 Linux 上运行测试。对于开源项目，你可以获得无限的分钟数和 10 个免费的并行作业。本节介绍如何设置 Azure Pipelines 来运行你的扩展测试。
>
> 首先，在 [Azure DevOps](https://azure.microsoft.com/services/devops/) 上创建一个免费账户，并为你的扩展创建一个 [Azure DevOps 项目](https://azure.microsoft.com/features/devops-projects/)。
>
> 然后，把下面的 `azure-pipelines.yml` 文件添加到扩展仓库的根目录。除了 Linux 上的 `xvfb` 设置脚本（在无头的 Linux CI 机器上运行 VS Code 时需要它）之外，这个定义非常简单直接：

```yaml
trigger:                     # 何时触发：推送到 main 分支，或推送以 v 开头的标签
  branches:
    include:
    - main
  tags:
    include:
    - v*

strategy:
  matrix:                    # 矩阵：在三种系统上各运行一次
    linux:
      imageName: 'ubuntu-latest'
    mac:
      imageName: 'macos-latest'
    windows:
      imageName: 'windows-latest'

pool:
  vmImage: $(imageName)

steps:

- task: NodeTool@0
  inputs:
    versionSpec: '10.x'
  displayName: 'Install Node.js'

- bash: |                    # 只在 Linux 上：启动虚拟显示器
    /usr/bin/Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    echo ">>> Started xvfb"
  displayName: Start xvfb
  condition: and(succeeded(), eq(variables['Agent.OS'], 'Linux'))

- bash: |
    echo ">>> Compile vscode-test"
    yarn && yarn compile
    echo ">>> Compiled vscode-test"
    cd sample
    echo ">>> Run sample integration test"
    yarn && yarn compile && yarn test
  displayName: Run Tests
  env:
    DISPLAY: ':99.0'         # 告诉 VS Code 使用 xvfb 提供的显示器 :99
```

**为什么 Linux 上需要 `xvfb`？** VS Code 是一个图形界面程序，启动时需要一个显示器。CI 的 Linux 机器没有图形界面（“无头”），`Xvfb`（X 虚拟帧缓冲区）在内存中模拟一个显示器，VS Code 就可以在上面“显示”。Windows 和 macOS 的 CI 机器自带图形环境，不需要它。

**使用这个示例时要调整的地方：**

- 这个 YAML 来自 `vscode-test` 仓库本身，所以“Run Tests”一步是先编译 `vscode-test`，再进入 `sample` 文件夹运行测试。在你自己的扩展仓库中，这一步通常只需要 `npm ci` 和 `npm test`（使用 Yarn 时是 `yarn` 和 `yarn test`）。
- `versionSpec: '10.x'` 是很老的 Node.js 版本，现在的工具链（`@vscode/test-electron`、`@vscode/vsce` 等）需要更新的 Node.js，请使用当前的 LTS 版本（例如 `'20.x'` 或 `'22.x'`）。

> 最后，在你的 DevOps 项目中[创建一个新的流水线](https://learn.microsoft.com/azure/devops/pipelines/create-first-pipeline)，并让它指向 `azure-pipelines.yml` 文件。触发一次构建，瞧：

![流水线](images/continuous-integration/pipelines.png)

截图是一次名为 “Extension CI” 的构建结果：左侧 Windows Job、macOS Job、Linux Job 三个作业都成功了（绿色对勾），右侧展开的是 Windows Job 的步骤（准备作业、获取源代码、安装 Node、安装依赖、编译源代码、运行测试……），全部成功。右上角的柱状图是最近几次构建的历史，红色表示失败，绿色表示成功。

> 你可以让构建在推送到某个分支时、甚至在拉取请求上持续运行。参见[构建流水线触发器](https://learn.microsoft.com/azure/devops/pipelines/build/triggers)了解更多。

<a id="azure-pipelines-automated-publishing"></a>
### Azure Pipelines 自动发布（Azure Pipelines automated publishing）

> 1. 按照 [Azure DevOps 机密说明](https://learn.microsoft.com/azure/devops/pipelines/process/variables?tabs=classic%2Cbatch#secret-variables)，把 `VSCE_PAT` 设置为一个机密变量。
> 2. 把 `vsce` 安装为 `devDependencies`（`npm install @vscode/vsce --save-dev` 或 `yarn add @vscode/vsce --dev`）。
> 3. 在 `package.json` 中声明一个不带 PAT 的 `deploy` 脚本（默认情况下，`vsce` 会使用 `VSCE_PAT` 环境变量作为个人访问令牌）。

```json
"scripts": {
  "deploy": "vsce publish --yarn"
}
```

`--yarn` 表示用 Yarn（而不是 npm）来检查和列出依赖。如果你的项目使用 npm，去掉它，写成 `"deploy": "vsce publish"`。

> 4. 配置 CI，使得创建标签时也会运行构建：

```yaml
trigger:
  branches:
    include:
    - main
  tags:
    include:
    - refs/tags/v*
```

（与上面完整示例中的 `v*` 写法等价，Azure Pipelines 两种写法都接受。）

> 5. 在 `azure-pipelines.yml` 中添加一个 `publish` 步骤，用机密变量调用 `yarn deploy`。

```yaml
- bash: |
    echo ">>> Publish"
    yarn deploy
  displayName: Publish
  condition: and(succeeded(), startsWith(variables['Build.SourceBranch'], 'refs/tags/'), eq(variables['Agent.OS'], 'Linux'))
  env:
    VSCE_PAT: $(VSCE_PAT)
```

> [condition](https://learn.microsoft.com/azure/devops/pipelines/process/conditions) 属性告诉 CI 只在某些情况下运行发布步骤。
>
> 在我们的示例中，这个条件包含三项检查：
>
> - `succeeded()` - 只有测试通过时才发布。
> - `startsWith(variables['Build.SourceBranch'], 'refs/tags/')` - 只有在打了标签的（发布）构建中才发布。
> - `eq(variables['Agent.OS'], 'Linux')` - 如果你的构建在多个代理（Windows、Linux 等）上运行，就加上这一项。如果不是，就去掉条件中的这一部分。
>
> 由于 `VSCE_PAT` 是一个机密变量，它不能立即作为环境变量使用。因此，我们需要显式地把环境变量 `VSCE_PAT` 映射到这个机密变量。

第三项检查的意义：矩阵中三个系统都会运行这些步骤，如果不限制，同一个版本会被发布三次（后两次会因为版本已存在而失败）。所以只让其中一个系统（这里是 Linux）执行发布。

`env: VSCE_PAT: $(VSCE_PAT)` 中，左边是环境变量名，右边 `$(VSCE_PAT)` 是读取流水线中的机密变量。出于安全考虑，Azure Pipelines 的机密变量不会自动变成环境变量，必须这样显式地映射。

---

<a id="github-actions"></a>
## GitHub Actions

> 你也可以配置 GitHub Actions 来运行扩展的 CI。在无头的 Linux CI 机器上运行 VS Code 需要 `xvfb`，所以如果当前的系统是 Linux，就在启用了 Xvfb 的环境中运行测试：

```yaml
on:
  push:
    branches:
      - main

jobs:
  build:
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    - name: Install Node.js
      uses: actions/setup-node@v4
      with:
        node-version: 18.x
    - run: npm install
    - run: xvfb-run -a npm test       # Linux：用 xvfb-run 包裹测试命令
      if: runner.os == 'Linux'
    - run: npm test                   # Windows / macOS：直接运行
      if: runner.os != 'Linux'
```

几点说明：

- 这个文件放在仓库的 `.github/workflows/` 目录下，例如 `.github/workflows/ci.yml`。
- 原文网页中显示为 `$\{{ matrix.os }}`，反斜杠是文档网站模板的转义字符，实际文件中要写 `${{ matrix.os }}`（下文的 `secrets.VSCE_PAT` 同理）。
- `xvfb-run -a` 会启动一个虚拟显示器、在其中运行命令、结束后关闭显示器，比 Azure Pipelines 示例中手动启动 Xvfb 更简单。GitHub 的 `ubuntu-latest` 镜像中已经预装了 `xvfb`。
- `node-version: 18.x` 已经不是受支持的 LTS 版本，建议改为 `20.x` 或更新。在 CI 中推荐用 `npm ci` 代替 `npm install`，它严格按照 `package-lock.json` 安装，结果可复现。

<a id="github-actions-automated-publishing"></a>
### GitHub Actions 自动发布（GitHub Actions automated publishing）

> 1. 按照 [GitHub Actions 机密说明](https://docs.github.com/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository)，把 `VSCE_PAT` 设置为一个加密的机密（secret）。
> 2. 把 `vsce` 安装为 `devDependencies`（`npm install @vscode/vsce --save-dev` 或 `yarn add @vscode/vsce --dev`）。
> 3. 在 `package.json` 中声明一个不带 PAT 的 `deploy` 脚本。

```json
"scripts": {
  "deploy": "vsce publish --yarn"
}
```

（同样，项目使用 npm 时去掉 `--yarn`。上面的 GitHub Actions 示例用的是 npm。）

> 4. 配置 CI，使得创建标签时也会运行构建：

```yaml
on:
  push:
    branches:
    - main
  release:
    types:
    - created
```

> 5. 在流水线中添加一个 `publish` 作业，用机密变量调用 `npm run deploy`。

```yaml
- name: Publish
  if: success() && startsWith(github.ref, 'refs/tags/') && matrix.os == 'ubuntu-latest'
  run: npm run deploy
  env:
    VSCE_PAT: ${{ secrets.VSCE_PAT }}
```

> [if](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idif) 属性告诉 CI 只在某些情况下运行发布步骤。
>
> 在我们的示例中，这个条件包含三项检查：
>
> - `success()` - 只有测试通过时才发布。
> - `startsWith(github.ref, 'refs/tags/')` - 只有在打了标签的（发布）构建中才发布。
> - `matrix.os == 'ubuntu-latest'` - 如果你的构建在多个代理（Windows、Linux 等）上运行，就加上这一项。如果不是，就去掉条件中的这一部分。

**关于触发方式：** 第 4 步用的是 `release: types: [created]`，即在 GitHub 网页上**创建一个 Release** 时触发（创建 Release 时会同时创建标签，此时 `github.ref` 是 `refs/tags/<标签名>`，所以第 5 步的条件成立）。如果你更习惯直接推送标签来发布，可以改成：

```yaml
on:
  push:
    branches: [main]
    tags: ['v*']        # 推送 v 开头的标签时也触发
```

（原文第 5 步说的是添加一个“作业（job）”，但给出的是一个“步骤（step）”，它要加在上面 `build` 作业的 `steps` 列表的最后，测试步骤之后。）

---

<a id="gitlab-ci"></a>
## GitLab CI

> GitLab CI 可以用来在无头的 Docker 容器中测试和发布扩展。这可以通过拉取一个预先配置好的 Docker 镜像来完成，也可以在流水线中安装 `xvfb` 和运行 Visual Studio Code 所需的库。

```yaml
image: node:12-buster

before_script:
  - npm install

test:
  script:
    - |
      apt update
      apt install -y libasound2 libgbm1 libgtk-3-0 libnss3 xvfb
      xvfb-run -a npm run test
```

GitLab CI 的作业在 Docker 容器中运行，基础镜像（这里是 Node 的 Debian 镜像）中没有图形界面相关的库，所以要先用 `apt` 安装 VS Code（Electron）运行所需的库和 `xvfb`，再用 `xvfb-run` 运行测试。`node:12-buster` 同样已经过时，可以换成较新的镜像（例如 `node:20-bookworm`），较新的系统中个别库的包名可能不同（例如 `libasound2` 在一些新版本中变成了 `libasound2t64`），以安装时的报错为准调整。

<a id="gitlab-ci-automated-publishing"></a>
### GitLab CI 自动发布（GitLab CI automated publishing）

> 1. 按照 [GitLab CI 文档](https://docs.gitlab.com/ee/ci/variables/README.html#mask-a-cicd-variable)，把 `VSCE_PAT` 设置为一个受掩码保护的（masked）变量。
> 2. 把 `vsce` 安装为 `devDependencies`（`npm install @vscode/vsce --save-dev` 或 `yarn add @vscode/vsce --dev`）。
> 3. 在 `package.json` 中声明一个不带 PAT 的 `deploy` 脚本。

```json
"scripts": {
  "deploy": "vsce publish --yarn"
}
```

> 4. 添加一个 `deploy` 作业，用受掩码保护的变量调用 `npm run deploy`，它只在标签上触发。

```yaml
deploy:
  only:
    - tags
  script:
    - npm run deploy
```

GitLab CI 的变量会自动作为环境变量提供给作业，所以不需要像前两种那样显式映射。“掩码（masked）”是指这个变量的值即使被打印出来，在日志中也会显示为 `[MASKED]`。（新版 GitLab 推荐用 `rules: - if: $CI_COMMIT_TAG` 代替 `only: - tags`，效果相同。）

---

<a id="common-questions"></a>
## 常见问题（Common questions）

<a id="do-i-need-to-use-yarn-for-continuous-integration"></a>
### 持续集成必须使用 Yarn 吗？（Do I need to use Yarn for continuous integration?）

> 上面所有的示例都针对一个假设的、用 [Yarn](https://yarnpkg.com/) 构建的项目，但它们也可以调整为使用 [npm](https://www.npmjs.com/)、[Grunt](https://gruntjs.com/)、[Gulp](https://gulpjs.com/) 或任何其他 JavaScript 构建工具。

不需要。把 `yarn` 换成 `npm ci` / `npm run xxx`，并去掉 `vsce publish` 的 `--yarn` 参数即可。

---

## 本篇小结

```text
CI 运行集成测试：矩阵覆盖 Windows / macOS / Linux
  Linux 需要虚拟显示器：xvfb-run -a npm test（或手动启动 Xvfb 并设置 DISPLAY）
  Node.js 版本使用当前 LTS

自动发布（三种 CI 相同的思路）
  1. 机密变量 VSCE_PAT（vsce 默认读取这个环境变量）
  2. devDependencies: @vscode/vsce；scripts: "deploy": "vsce publish"
  3. 标签（或 Release）触发构建
  4. 发布步骤条件：测试通过 && 标签构建 && 只在一个系统上执行

  Azure：condition + env: VSCE_PAT: $(VSCE_PAT)
  GitHub：if + env: VSCE_PAT: ${{ secrets.VSCE_PAT }}
  GitLab：only: tags（变量自动注入）
```
