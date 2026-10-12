# 发布扩展（Publishing Extensions）

> 原文：[Publishing Extensions](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
> 源文件：`microsoft/vscode-docs` → `api/working-with-extensions/publishing-extension.md`（DateApproved: 10/7/2026）

> 当你做出了一个高质量的扩展之后，就可以把它发布到 [VS Code 扩展市场](https://marketplace.visualstudio.com/vscode)，让其他人可以找到、下载和使用你的扩展。或者，你也可以把扩展[打包](#packaging-extensions)成可安装的 VSIX 格式，与其他用户分享。
>
> 本主题涵盖：
>
> - 使用 [vsce](#vsce)，这个管理 VS Code 扩展的命令行工具
> - [打包](#packaging-extensions)、[发布](#publishing-extensions)和[取消发布](#unpublishing-extensions)扩展
> - [注册一个发布者](#create-a-publisher)，这是发布扩展所必需的

**第一次发布的完整流程（先看全貌）：**

```text
1. 安装 vsce                            npm install -g @vscode/vsce
2. 获取身份凭证                          Azure DevOps 个人访问令牌（PAT），或 Microsoft Entra ID（推荐，用于 CI）
3. 创建发布者                            在市场管理页面创建，得到发布者 ID
4. 在 package.json 中填写 "publisher"    值为发布者 ID
5. 登录                                 vsce login <发布者 ID>
6. 发布                                 vsce publish
```

---

<a id="vsce"></a>
## vsce

> [vsce](https://github.com/microsoft/vscode-vsce) 是 “Visual Studio Code Extensions” 的缩写，它是一个用于打包、发布和管理 VS Code 扩展的命令行工具。

<a id="installation"></a>
### 安装（Installation）

> 确保你已经安装了 [Node.js](https://nodejs.org/)。然后运行：

```bash
npm install -g @vscode/vsce
```

（旧的包名是 `vsce`，现在是 `@vscode/vsce`，命令名仍然是 `vsce`。也可以像 [持续集成](./continuous-integration.md) 中那样，把它装为项目的开发依赖，用 `npx vsce` 运行。）

<a id="usage"></a>
### 用法（Usage）

> 你可以使用 `vsce` 轻松地[打包](#packaging-extensions)和[发布](#publishing-extensions)你的扩展：

```bash
$ cd myExtension
$ vsce package
# 生成了 myExtension.vsix
$ vsce publish
# <publisher id>.myExtension 已发布到 VS Code 市场
```

> `vsce` 还可以搜索、获取元数据和取消发布扩展。要查看所有可用的 `vsce` 命令，运行 `vsce --help`。

常用的 `vsce` 命令：

| 命令 | 作用 |
|---|---|
| `vsce package` | 打包成 `.vsix` 文件 |
| `vsce publish` | 发布到市场 |
| `vsce login <发布者>` / `vsce logout <发布者>` | 保存 / 删除发布者的凭证 |
| `vsce ls` | 列出将被打包的文件（检查 `.vscodeignore` 是否正确） |
| `vsce show <发布者.扩展名>` | 查看市场上某个扩展的信息 |
| `vsce search <关键词>` | 搜索市场 |
| `vsce unpublish <发布者.扩展名>` | 从市场删除扩展（见下文，不可撤销） |

`vsce package` 和 `vsce publish` 会先检查 `package.json`：缺少 `publisher`、`README.md` 还是模板内容、没有 `repository` 字段等情况，都会给出错误或警告。

---

<a id="publishing-extensions"></a>
## 发布扩展（Publishing extensions）

---

> **注意**
>
> 出于安全考虑，`vsce` 不会发布包含用户提供的 SVG 图片的扩展。
>
> 发布工具会检查以下约束：
>
> - `package.json` 中提供的图标不能是 SVG。
> - `package.json` 中提供的徽章不能是 SVG，除非它们来自[受信任的徽章提供者](../references/extension-manifest.md#approved-badges)。
> - `README.md` 和 `CHANGELOG.md` 中的图片 URL 需要解析为 `https` URL。
> - `README.md` 和 `CHANGELOG.md` 中的图片不能是 SVG，除非它们来自[受信任的徽章提供者](../references/extension-manifest.md#approved-badges)。

---

SVG 可以包含脚本，存在安全风险，所以市场不允许。图标请使用 PNG（至少 128×128 像素，见下文 [市场集成](#marketplace-integration)）。README 中的图片要用 `https` 的绝对地址，或者在 `package.json` 中设置 `repository` 字段，让 `vsce` 自动把相对路径转换成仓库中的地址。

> Visual Studio Code 使用 [Azure DevOps](https://azure.microsoft.com/services/devops/) 作为它的市场服务。这意味着扩展的身份验证、托管和管理都通过 Azure DevOps 提供。

> **重要**
>
> 2026 年 12 月 1 日，Azure DevOps 中的全局个人访问令牌（PAT）将被停用。要继续发布扩展，请使用基于 Microsoft Entra ID 的[安全自动发布](#secure-automated-publishing-to-visual-studio-marketplace)，而不是 PAT。更多信息请参见[Azure DevOps 中全局个人访问令牌的停用](https://devblogs.microsoft.com/devops/retirement-of-global-personal-access-tokens-in-azure-devops/)。

**这条变更对你意味着什么：** 发布到市场所用的 PAT，必须在创建时选择 “All accessible organizations”（所有可访问的组织），这正是所谓的“全局 PAT”（见下文 [获取个人访问令牌](#get-a-personal-access-token) 和 [常见问题](#i-get-403-forbidden-or-401-unauthorized-error-when-i-try-to-publish-my-extension)）。所以在这个日期之后，本篇和 [持续集成](./continuous-integration.md) 中基于 `VSCE_PAT` 的发布方式将无法继续使用，需要迁移到下一节介绍的方式。具体的过渡安排（例如本地手动发布的替代方式）以上面链接的公告为准。

<a id="secure-automated-publishing-to-visual-studio-marketplace"></a>
### 安全地自动发布到 Visual Studio 市场（Secure automated publishing to Visual Studio Marketplace）

> 我们建议扩展的发布使用[基于 Microsoft Entra ID 的身份验证](https://learn.microsoft.com/en-us/azure/devops/integrate/get-started/authentication/entra?view=azure-devops)，配合**工作负载身份联合（workload identity federation）和托管标识（managed identities）**。这种方式消除了个人访问令牌（PAT）这样的长期机密，并实现了安全的自动发布流水线。
>
> 这种方式通过消除对存储凭证的依赖来增强整体的安全态势；通过与 Azure Pipelines 和 Entra ID 的原生集成来简化运维；能在不同环境中有效扩展；并且符合企业合规所要求的现代身份和访问管理标准。更多信息请参见[减少 PAT 的使用](https://devblogs.microsoft.com/devops/reducing-pat-usage-across-azure-devops/)。

**PAT 与托管标识的区别：**

| | PAT | 托管标识 + 工作负载身份联合 |
|---|---|---|
| 凭证形式 | 一串长期有效的令牌，需要保存在某处（CI 的机密变量中） | 没有需要保存的机密：流水线运行时，Azure 临时签发一个短期令牌 |
| 泄露风险 | 令牌泄露后，在过期前任何人都能用它发布 | 没有可泄露的长期凭证 |
| 适用 | 本地、各种 CI | Azure Pipelines（通过服务连接） |

下面的步骤看起来繁琐，但只需要配置一次。整体关系是：**Azure DevOps 的服务连接** ⇄（联合凭据互相信任）⇄ **Azure 中的托管标识** →（被添加为成员）→ **市场中的发布者**。

> 1. 创建一个服务连接（Azure DevOps）
>
>    - 进入 **Project Settings → Service Connections**（项目设置 → 服务连接）
>    - 新建一个 **Azure Resource Manager** 连接
>    - 选择 **Workload Identity Federation (manual)**（工作负载身份联合，手动）
>    - 以草稿模式保存这个连接，以便之后填入所需的值
>
> 2. 创建一个托管标识（Azure）
>
>    - 在 Azure 中创建一个**用户分配的托管标识**
>    - 为它分配 **Reader**（读取者）角色
>    - 记录以下值：**Client ID**（客户端 ID）、**Tenant ID**（租户 ID）、**Subscription**（订阅）详情
>
> 3. 配置联合凭据
>
>    在 Azure DevOps 与 Azure 之间建立联系：
>
>    - 为托管标识添加一个联合凭据
>    - 在两个系统之间交换所需的值：
>      - 从 Azure DevOps → Azure：**issuer（颁发者）和 subject（主体）**
>      - 从 Azure → Azure DevOps：**client ID、tenant ID、subscription**
>    - 在 Azure DevOps 中，选择 **Verify and save**（验证并保存）
>
> 4. 授予流水线访问权限
>
>    - 打开这个服务连接
>    - 为负责发布的流水线授予访问权限
>
> 5. 获取托管标识的资源 ID（只需一次）
>
>    - 运行一个 Azure CLI 任务来获取标识的信息：
>
>      ```yaml
>      steps:
>      - task: AzureCLI@2
>        displayName: 'Get identity details'
>        inputs:
>          azureSubscription: <ServiceConnectionName>
>          scriptType: pscore
>          scriptLocation: inlineScript
>          inlineScript: |
>            az rest -u https://app.vssps.visualstudio.com/_apis/profile/profiles/me --resource 499b84ac-1321-427f-aa17-267ca6975798
>      ```
>
>    - 从输出的 JSON 中，记下托管标识的资源 ID（`id` 字段）。
>
> 6. 在 Visual Studio 市场中授权这个标识
>
>    - 把这个托管标识（使用它的资源 ID）添加为你的发布者的成员。
>    - 为它分配 **Contributor**（参与者）角色
>
> 7. 配置 CI/CD 流水线
>
>    - 设置你的 Azure Pipelines CI/CD 工作流
>    - 用基于标识的方式替换基于 PAT 的身份验证
>
> 8. 使用托管标识发布
>
>    - 在你的流水线中，通过 Azure CLI 生成一个 Microsoft Entra ID（AAD）访问令牌。
>    - 在发布命令中使用这个令牌（例如：`vsce publish --azure-credential`）。
>
> 示例 YAML 任务。把 `<ExtensionDirectory>` 替换为扩展所在目录的路径。

第 5 步命令中的 `499b84ac-1321-427f-aa17-267ca6975798` 是 Azure DevOps 这个资源的固定 ID，原样使用即可。`<ServiceConnectionName>` 替换为第 1 步创建的服务连接的名称。

```yaml
# 安装 VS Code 扩展管理器（需要 vsce >= v2.26.1）和依赖
- script: |
    cd <ExtensionDirectory>
    npm install -g @vscode/vsce
    npm install
  displayName: "Install vsce and dependencies"

# 发布
- task: AzureCLI@2
  displayName: 'Publish using managed identity'
  inputs:
    azureSubscription: <ServiceConnectionName>
    scriptType: pscore
    scriptLocation: inlineScript
    inlineScript: |
      cd <ExtensionDirectory>
      vsce publish --azure-credential
```

`vsce publish --azure-credential` 会使用当前环境中 Azure CLI 已登录的身份（`AzureCLI@2` 任务会用服务连接自动登录）获取令牌，所以不需要 `VSCE_PAT`。

***

> `vsce` 也可以使用[个人访问令牌](https://learn.microsoft.com/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate)发布扩展。

> **重要**
>
> Azure DevOps 中的全局 PAT 将于 2026 年 12 月 1 日停用。我们建议你使用基于 Microsoft Entra ID 的[安全自动发布](#secure-automated-publishing-to-visual-studio-marketplace)，而不是 PAT。更多信息请参见[Azure DevOps 中全局个人访问令牌的停用](https://devblogs.microsoft.com/devops/retirement-of-global-personal-access-tokens-in-azure-devops/)。

<a id="get-a-personal-access-token"></a>
### 获取个人访问令牌（Get a Personal Access Token）

> 你可以通过 Azure DevOps 门户创建个人访问令牌。要创建个人访问令牌：
>
> 1. 如果你还没有 Azure DevOps 组织，按照[创建组织](https://learn.microsoft.com/azure/devops/organizations/accounts/create-organization)一文中的步骤创建一个。
>
> 1. 进入 [Azure DevOps 门户](https://go.microsoft.com/fwlink/?LinkId=307137)，选择你的组织。
>
> 1. 打开头像旁边的 User settings（用户设置）下拉菜单，选择 **Personal access tokens**（个人访问令牌）：
>
>     ![个人设置菜单](images/publishing-extension/menu-pat.png)
>
> 1. 在 **Personal Access Tokens** 页面，选择 **New Token**（新建令牌）：
>
>     ![新建令牌按钮](images/publishing-extension/new-token.png)
>
> 1. 在“创建新的个人访问令牌”对话框中，为令牌选择以下详细信息：
>
>     - Name（名称）：你想给令牌起的任何名字
>     - Organization（组织）：**All accessible organizations**（所有可访问的组织）
>     - Expiration（过期时间，可选）：为令牌设置想要的过期日期
>     - Scopes（范围）：**Custom defined**（自定义）：
>       - 点击 **Scopes** 部分下方的 **Show all scopes**（显示所有范围）链接
>       - 在范围列表中，滚动到 **Marketplace**（市场），选择 **Manage**（管理）范围
>
>     ![创建个人访问令牌](images/publishing-extension/create-token.png)
>
> 1. 点击 **Create**（创建）。
>
>     你会看到新创建的个人访问令牌。把它**复制**到安全的地方，你在[创建发布者](#create-a-publisher)时需要用到它。

截图中红色箭头标出了要填写的几处：名称（`Marketplace access token`）、组织选择 **All accessible organizations**、范围选择 **Custom defined**、在 **Marketplace** 一栏勾选 **Manage**（勾选后 Read 和 Publish 会自动选中）。

最容易出错的两处就是“组织”和“范围”，选错了会在发布时得到 401 / 403 错误（见 [常见问题](#i-get-403-forbidden-or-401-unauthorized-error-when-i-try-to-publish-my-extension)）。令牌只在创建时显示一次，关闭对话框后就再也看不到了。

<a id="create-a-publisher"></a>
### 创建一个发布者（Create a publisher）

> **发布者（publisher）**是一个可以向 Visual Studio Code 市场发布扩展的身份。每个扩展都需要在它的 [`package.json` 文件](../references/extension-manifest.md)中包含一个 `publisher` 标识符。
>
> 要创建一个发布者：
>
> 1. 进入 [Visual Studio 市场的发布者管理页面](https://marketplace.visualstudio.com/manage)。
> 1. 使用你在上一节中创建[个人访问令牌](#get-a-personal-access-token)时所用的同一个微软账户登录。
> 1. 点击左侧窗格中的 **Create publisher**（创建发布者）。
> 1. 在新的页面中，为新的发布者指定必填的参数，即标识符和名称（分别是 **ID** 和 **Name** 字段）：
>
>     - **ID**：你的发布者在市场中的**唯一**标识符，会用在你的扩展的 URL 中。ID 创建后无法更改。
>     - **Name**：你的发布者的**唯一**名称，会和你的扩展一起显示在市场中。可以是你的公司或品牌名称。
>
>     下面是 Python 扩展的发布者标识符和名称的例子：
>
>     ![发布者标识符和名称的例子](images/publishing-extension/publisher-id-and-name.png)
>
> 1. 可以选择填写其余的字段。
> 1. 点击 **Create**（创建）
> 1. 使用 `vsce` 验证新创建的发布者。在终端中运行以下命令，并在提示时输入上一步创建的个人访问令牌：
>
>     ```bash
>     vsce login <publisher id>
>
>     https://marketplace.visualstudio.com/manage/publishers/
>     Personal Access Token for publisher '<publisher id>': ****************************************************
>
>     The Personal Access Token verification succeeded for the publisher '<publisher id>'.
>     ```
>
> 验证通过后，你就可以发布扩展了。

| | ID | Name |
|---|---|---|
| 用在哪里 | `package.json` 的 `publisher` 字段、扩展 ID（`发布者ID.扩展名`）、市场 URL | 市场页面和 VS Code 中显示的发布者名称 |
| 能否修改 | 不能 | 能（但会导致已认证的发布者失去认证徽章，见下文） |
| 例子（Python 扩展） | `ms-python` | `Microsoft` |

`vsce login` 会把令牌保存在本机，之后 `vsce publish` 就不用再输入。

<a id="publish-an-extension"></a>
### 发布一个扩展（Publish an extension）

> 你可以通过两种方式发布扩展：
>
> 1. 自动发布，使用 `vsce publish` 命令：
>
>     ```bash
>     vsce publish
>     ```
>
>     如果你之前没有用上面的 `vsce login` 命令提供个人访问令牌，`vsce` 会要求你输入。
>
> 1. 手动发布，使用 `vsce package` 把扩展打包成可安装的 VSIX 格式，然后上传到 [Visual Studio 市场的发布者管理页面](https://marketplace.visualstudio.com/manage)：
>
>     ![通过管理页面添加扩展](images/publishing-extension/add-extension.png)

手动上传的方式不需要 PAT（使用网页登录的身份），所以如果你只是偶尔在本地发布，这也是一种不依赖令牌的办法。发布后，市场需要几分钟进行验证（包括病毒扫描），之后扩展才会出现在搜索结果中。

---

<a id="review-extension-installs-and-ratings"></a>
## 查看扩展的安装量和评分（Review extension installs and ratings）

> [Visual Studio 市场的发布者管理页面](https://marketplace.visualstudio.com/manage)让你可以查看每个扩展随时间变化的获取趋势（Acquisition Trend），以及总获取量和评分与评论（Ratings & Reviews）。要查看报告，点击一个扩展，或者选择 **More Actions > Reports**（更多操作 > 报告）。

![市场扩展报告](images/publishing-extension/extension-report.png)

---

<a id="auto-increment-the-extension-version"></a>
## 自动递增扩展版本号（Auto-increment the extension version）

> 发布扩展时，你可以通过指定一个兼容 [SemVer](https://semver.org/) 的版本号，或者要递增的版本部分（`major`、`minor` 或 `patch`），来自动递增扩展的版本号。例如，要把扩展的版本从 1.0.0 更新为 1.1.0，你可以指定：

```bash
vsce publish minor
```

> 或者

```bash
vsce publish 1.1.0
```

> 这两个命令都会先修改扩展 `package.json` 中的 [version](../references/extension-manifest.md#fields) 属性，然后用更新后的版本发布。

> **注意**
>
> 如果你在一个 git 仓库中运行 `vsce publish`，它还会通过 [npm-version](https://docs.npmjs.com/cli/version#description) 创建一个版本提交和标签。默认的提交消息是扩展的版本号，但你可以使用 `-m` 标志提供自定义的提交消息。（在提交消息中可以用 `%s` 引用当前的版本号。）

| 参数 | 1.0.0 变为 |
|---|---|
| `patch` | 1.0.1（修复问题） |
| `minor` | 1.1.0（新增功能） |
| `major` | 2.0.0（不兼容的变更） |

这里说的“在 git 仓库中创建提交和标签”，是指指定了版本参数（如 `vsce publish minor`）时的行为；单独运行 `vsce publish` 只是按 `package.json` 中现有的版本号发布。注意同一个版本号只能发布一次，再次发布前必须递增版本号。

---

<a id="unpublishing-extensions"></a>
## 取消发布扩展（Unpublishing extensions）

> 你可以在 [Visual Studio 市场的发布者管理页面](https://marketplace.visualstudio.com/manage)中，点击 **More Actions > Unpublish**（更多操作 > 取消发布）来取消发布一个扩展：

![通过市场管理页面取消发布扩展](images/publishing-extension/unpublish-extension.png)

> 取消发布后，扩展的可用性（Availability）状态会变为 **Unpublished**（已取消发布），它将无法再从市场和 Visual Studio Code 中下载：

![已取消发布的扩展](images/publishing-extension/unpublished-extension.png)

> **注意**
>
> 当你取消发布一个扩展时，市场会保留扩展的统计数据。这个扩展仍然可以被公开发现，并且可以通过现有的 API 获取。

---

<a id="removing-extensions"></a>
## 删除扩展（Removing extensions）

> 你可以通过两种方式删除一个扩展：
>
> 1. 自动删除，使用 [`vsce`](#vsce) 的 `unpublish` 命令：
>
>     ```bash
>     vsce unpublish <publisher id>.<extension name>
>     ```
>
> 1. 手动删除，在 [Visual Studio 市场的发布者管理页面](https://marketplace.visualstudio.com/manage)中，点击 **More Actions > Remove**（更多操作 > 删除）：
>
>     ![通过市场管理页面删除扩展](images/publishing-extension/remove-extension.png)
>
> 两种情况下，你都会被要求输入扩展的名称来确认删除。注意，删除操作是**不可撤销的**。

> **注意**
>
> 当你删除一个扩展时，市场也会删除这个扩展的所有统计数据。你可能会想取消发布你的扩展，而不是删除它。
>
> 重要！扩展名称是 Visual Studio Code 市场中的唯一标识符。一个扩展被删除后，它的扩展名称会被永久保留，无法再被使用，即使是原来的发布者也不行。这有助于保护用户免受冒充，维护市场生态的信任。在删除扩展之前，请确保你不再需要这个名称，因为这个操作是不可撤销的。

**注意命令名称的陷阱：** `vsce unpublish` 命令执行的是**删除（Remove）**，而不是网页上的“取消发布（Unpublish）”。

| | 取消发布（网页 Unpublish） | 删除（网页 Remove / `vsce unpublish`） |
|---|---|---|
| 用户还能下载吗 | 不能 | 不能 |
| 统计数据 | 保留 | 删除 |
| 能否恢复 | 能（重新发布即可） | 不能 |
| 扩展名称 | 仍归你所有 | 永久作废，任何人都不能再用 |

---

<a id="removing-specific-extension-versions"></a>
## 删除特定的扩展版本（Removing specific extension versions）

> 你可以在 [Visual Studio 市场的发布者管理页面](https://marketplace.visualstudio.com/manage)中，选择 **More Actions > Reports**（更多操作 > 报告）来删除扩展的一个特定版本：

![市场发布者管理页面中，“更多操作”菜单里的“报告”选项](images/publishing-extension/extension-manage.png)

> 在 **Manage**（管理）选项卡中，选择 **Delete this version**（删除此版本）。

![“管理”选项卡中的“删除此版本”按钮](images/publishing-extension/remove-version.png)

> 你会被要求输入扩展的名称来确认删除。这个操作是**不可撤销的**。

> **重要**
>
> 一旦删除，你就不能在新的发布中重新使用这个版本号。此外，你不能删除扩展的最新版本。

如果最新版本有严重问题，正确的做法是尽快发布一个修复版本（更高的版本号），而不是删除它。

---

<a id="deprecating-extensions"></a>
## 弃用扩展（Deprecating extensions）

> 你可以只是弃用一个扩展，也可以弃用它并推荐另一个扩展或一个设置。被弃用的扩展在界面中会以变暗的删除线文字显示：

![在扩展搜索中显示为已弃用的 Rust 扩展](images/publishing-extension/deprecated-extension.png)

截图中搜索 “rust”：第一项 “Rust (deprecated)” 的名称带有删除线并变暗，右下角有一个黄色的警告图标；下面是推荐的替代扩展 rust-analyzer。

> 每个被弃用的扩展，在扩展卡片的右下角都有一个黄色的警告图标（见上面的截图）。把鼠标悬停在扩展卡片上时，你可以在这个图标旁边看到弃用的详细信息，具体是以下哪种情况：
>
> - 这个扩展被弃用，没有任何替代：
>
>   ![没有替代的已弃用扩展](images/publishing-extension/deprecated-with-no-alternatives.png)
>
> - 这个扩展被弃用，推荐使用另一个扩展：
>
>   ![推荐了替代扩展的已弃用扩展](images/publishing-extension/deprecated-with-alternative-extension.png)
>
> - 这个扩展被弃用，推荐使用一个设置：
>
>   ![推荐了替代设置的已弃用扩展](images/publishing-extension/deprecated-with-alternative-setting.png)
>
> VS Code 不会自动迁移或卸载已经安装的被弃用扩展。如果一个被弃用的扩展有替代的扩展或设置，VS Code 会显示一个 **Migrate**（迁移）按钮，帮助你快速切换到指定的替代方案：

![带有迁移按钮的已弃用扩展](images/publishing-extension/deprecated-migrate-button.png)

> 要把你的扩展标记为已弃用，请在 [Deprecated extensions](https://github.com/microsoft/vscode-discussions/discussions/1) 讨论帖中留言。

> **注意**
>
> 目前，扩展在市场中还不会显示为已弃用。这个功能以后会提供。

“推荐使用一个设置”的典型场景：某个扩展的功能已经被 VS Code 内置了，只需打开某个设置即可，比如括号对着色功能内置后，相关的扩展就被弃用并推荐了 `editor.bracketPairColorization.enabled` 设置。弃用不是通过 `vsce` 或 `package.json` 完成的，而是要在上面的讨论帖中申请，由 VS Code 团队设置。

---

<a id="packaging-extensions"></a>
## 打包扩展（Packaging extensions）

> 如果你想做以下事情，可以选择打包你的扩展：
>
> - 在你的 VS Code 实例上测试它。
> - 在不发布到市场的情况下分发它。
> - 私下与他人分享。
>
> 打包就是创建一个包含你的扩展的 `.vsix` 文件。这个文件之后可以安装到 VS Code 中。有些扩展会把 `.vsix` 文件作为它们 GitHub Release 的一部分发布。
>
> 要打包一个扩展，在扩展的根文件夹中运行以下命令：

```bash
vsce package
```

> 这个命令会在扩展的根文件夹中创建一个 `.vsix` 文件。例如 `my-extension-0.0.1.vsix`。
>
> 对用户来说，在 VS Code 中安装一个 `.vsix` 文件的方法有：
>
> - 从 VS Code 的扩展视图：
>
>   1. 进入扩展视图。
>   1. 选择 **Views and More Actions...**（视图和更多操作，即扩展视图顶部的 `...`）
>   1. 选择 **Install from VSIX...**（从 VSIX 安装）
>
> - 从命令行：

```bash
# 如果你使用 VS Code
code --install-extension my-extension-0.0.1.vsix

# 如果你使用 VS Code Insiders
code-insiders --install-extension my-extension-0.0.1.vsix
```

`.vsix` 文件本质上是一个 zip 压缩包（可以改后缀名解压查看），里面是扩展的文件和一个清单。在资源管理器中右键点击 `.vsix` 文件，也有 **Install Extension VSIX** 菜单。打包前一定要先确认 `.vscodeignore` 配置正确（用 `vsce ls` 检查），避免把源代码、`node_modules` 中不需要的内容打进去（见 [打包扩展代码](./bundling-extension.md#publishing)）。

---

<a id="your-extension-folder"></a>
## 你的扩展文件夹（Your extension folder）

> 要加载一个扩展，你需要把文件复制到你的 VS Code 扩展文件夹 `.vscode/extensions` 中。根据你的操作系统，这个文件夹的位置不同：
>
> - **Windows：** `%USERPROFILE%\.vscode\extensions`
> - **macOS：** `~/.vscode/extensions`
> - **Linux：** `~/.vscode/extensions`

这是已安装扩展存放的位置（每个扩展一个文件夹，命名为 `发布者.扩展名-版本号`）。直接把文件复制进来是一种早期的手动安装方式，现在推荐使用上一节的 `.vsix` 安装。Insiders 版本使用的是 `.vscode-insiders/extensions`。

---

<a id="visual-studio-code-compatibility"></a>
## Visual Studio Code 兼容性（Visual Studio Code compatibility）

> 编写扩展时，你必须指定你的扩展兼容哪些 VS Code 版本。为此，使用 `package.json` 中的 `engines.vscode` 属性：

```json
{
  "engines": {
    "vscode": "^1.8.0"
  }
}
```

> - 值 `1.8.0`（不带脱字符）表示你的扩展只兼容 VS Code `1.8.0`。
> - 值 `^1.8.0` 表示你的扩展兼容 VS Code `1.8.0` 及之后的版本，包括 `1.8.1`、`1.9.0` 等。
>
> 你可以使用 `engines.vscode` 属性，确保扩展只会被安装到包含你所依赖的 API 的客户端上。这个机制对稳定版和 Insiders 版都适用。
>
> 例如，假设 VS Code 最新的稳定版是 `1.8.0`。在 `1.9.0` 版本的开发过程中，引入了一个新的 API，并通过版本 `1.9.0-insider` 在 Insiders 版中提供。如果你想发布一个使用这个 API 的扩展版本，你应该声明版本依赖为 `^1.9.0`。这样，你的新扩展版本只会在 VS Code `>=1.9.0` 上可用（换句话说，就是使用当前 Insiders 版本的用户）。使用 VS Code 稳定版的用户，只有在稳定版达到 `1.9.0` 版本时才会收到更新。
>
> 要按日期指定 Insiders 构建，在版本号后面追加一个 `YYYYMMDD` 格式的日期标签。VS Code 1.57 及更高版本会强制检查日期标签。更早的版本只评估版本号的数字部分。例如，`^1.56.0-20210428` 指向 VS Code 1.56 或更高版本中、于 2021 年 4 月 28 日 0:00 UTC 或之后创建的构建。

**`engines.vscode` 与 `@types/vscode` 要保持一致：** `@types/vscode` 的版本决定了你在代码中**能用到**哪些 API；`engines.vscode` 声明了扩展**要求**的最低 VS Code 版本。如果你装了 `@types/vscode@1.100` 却声明 `"vscode": "^1.80.0"`，就可能用到了 1.80 中没有的 API，在旧版本上运行时出错。`vsce` 在打包时会检查这一点：`@types/vscode` 的版本不能高于 `engines.vscode`。

用户的 VS Code 版本低于 `engines.vscode` 时，市场不会向他提供这个扩展版本，而是提供兼容的旧版本（如果有的话）。

---

<a id="advanced-usage"></a>
## 进阶用法（Advanced usage）

<a id="marketplace-integration"></a>
### 市场集成（Marketplace integration）

> 你可以自定义你的扩展在 Visual Studio 市场中的外观。参见 [Go 扩展](https://marketplace.visualstudio.com/items/golang.go)的例子。
>
> 下面是一些让你的扩展在市场中看起来很棒的提示：
>
> - 在扩展的根目录中添加一个 `README.md` 文件，写上你想在扩展的市场页面上显示的内容。
>
>   > **注意**
>   >
>   > 如果你的 `package.json` 中有一个指向公开 GitHub 仓库的 `repository` 属性，`vsce` 会自动检测到它，并相应地调整相对链接，默认使用 `main` 分支。你可以在运行 `vsce package` 或 `vsce publish` 时，用 `--githubBranch` 标志覆盖这个设置。你也可以用 `--baseContentUrl` 和 `--baseImagesUrl` 标志设置链接和图片的基础 URL。
>
> - 在扩展的根目录中添加一个 `LICENSE` 文件，写上扩展的许可证信息。
> - 在扩展的根目录中添加一个 `CHANGELOG.md` 文件，写上扩展的变更历史。
> - 在扩展的根目录中添加一个 `SUPPORT.md` 文件，写上如何获得扩展支持的信息。
> - 通过 `package.json` 中的 `galleryBanner.color` 属性指定对应的十六进制值，设置市场页面上横幅的背景色。
> - 通过 `package.json` 中的 `icon` 属性，指定扩展中一个至少 128x128 像素的 PNG 文件的相对路径，来设置图标。
>
> 更多信息请参见[市场展示技巧](../references/extension-manifest.md#marketplace-presentation-tips)。

| 文件 / 字段 | 显示在 |
|---|---|
| `README.md` | 市场页面和 VS Code 扩展详情页的 **Details**（详细信息）选项卡 |
| `CHANGELOG.md` | **Changelog**（更新日志）选项卡 |
| `LICENSE` | 许可证链接 |
| `icon` | 扩展图标 |
| `galleryBanner.color`（及 `theme: "dark"` / `"light"`） | 市场页面顶部横幅的背景色（及文字颜色） |
| `displayName`、`description`、`categories`、`keywords` | 名称、简介、分类、搜索关键词 |

一个常见的坑：`yo code` 生成的 `README.md` 是模板内容，如果没有修改，`vsce` 会拒绝打包，提示你先编辑 README。

<a id="verify-a-publisher"></a>
### 认证发布者（Verify a publisher）

> 你可以通过验证一个与你的品牌或身份关联的[符合条件的域名](#eligible-domains)的所有权，成为一个**认证发布者（verified publisher）**。一旦你的发布者通过了认证，市场就会在你的扩展详情中添加一个认证徽章。

<a id="prerequisites"></a>
<a id="prerequisites"></a>
#### 前提条件（Prerequisites）

> 要通过认证，一个发布者必须在 VS 市场上拥有一个或多个扩展至少 6 个月，并且域名的注册时间也必须至少有 6 个月。请等到满足这些条件之后再申请认证。

![VS Code 中的认证发布者标识](images/publishing-extension/verified-publisher.png)

截图以 GitLens 扩展为例，红圈标出了认证标识出现的位置：扩展详情页中发布者名称 GitKraken 前面的蓝色对勾；悬停提示中的 “This publisher has verified ownership of gitkraken.com”（这个发布者已验证了 gitkraken.com 的所有权）；扩展列表中发布者名称前的对勾；右侧资源链接中的 gitkraken.com。

> 要认证一个发布者：
>
> 1. 进入 [Visual Studio 市场的发布者管理页面](https://marketplace.visualstudio.com/manage)。
> 2. 在左侧窗格中，选择或[创建](#create-a-publisher)你想要认证的发布者。
> 3. 在主窗格中，选择 **Details**（详细信息）选项卡。
>
>    ![发布者详细信息选项卡的位置](images/publishing-extension/publisher-details-tab.png)
>
> 4. 在 **Details** 选项卡的 **Verified domain**（已验证的域名）部分，输入一个[符合条件的域名](#eligible-domains)。
>
>    ![填写了要验证的域名的发布者详细信息选项卡](images/publishing-extension/publisher-details-tab-verified-domain.png)
>
>    > **注意**：开始输入后，注意 **Details** 选项卡标题旁边出现了一个星号（*）。和在 VS Code 中一样，这表示你有未保存的更改。出于同样的原因，**Verify**（验证）按钮还是禁用的。
>
> 5. 选择 **Save**（保存），然后选择 **Verify**（验证）。
>
>    ![已保存待验证的域名](images/publishing-extension/saved-domain-to-verify.png)
>
>    会出现一个对话框窗口，向你说明如何在域名的 DNS 配置中添加一条 TXT 记录。
>
>    ![TXT 记录验证](images/publishing-extension/txt-record-verification.png)
>
> 6. 按照说明，在域名的 DNS 配置中添加这条 TXT 记录。
> 7. 在对话框窗口中选择 **Verify**（验证），确认 TXT 记录已经成功添加。
>
>    ![已提交验证](images/publishing-extension/validation-submitted.png)
>
>    你的 TXT 记录通过验证之后，市场团队会审核你的请求，并在 5 个工作日内告诉你结果。验证内容包括但不限于：域名、网站和扩展的[过往记录前提条件](#prerequisites)、内容的合规性、合法性、可信度和正面的声誉。
>
> 如果通过了验证，你会在 Visual Studio 市场的发布者管理页面中看到发布者名称旁边的对应徽章：

![发布者管理页面中的认证标识](images/publishing-extension/verified-publisher-manage.png)

> **注意**：
>
> - 对发布者显示名称的任何更改，都会撤销认证徽章。
> - 发布者今后任何违反[使用条款](https://cdn.vsassets.io/v/M190_20210811.1/_content/Microsoft-Visual-Studio-Marketplace-Terms-of-Use.pdf)或上述验证要求的行为，都会导致认证徽章被撤销。

“TXT 记录”是 DNS 中的一种记录，可以存放任意文字。市场给你一串随机的验证码，你把它作为 TXT 记录添加到你的域名中，市场再查询这个域名的 DNS，看到了这串验证码，就证明你确实能控制这个域名。

<a id="eligible-domains"></a>
### 符合条件的域名（Eligible domains）

> 符合条件的域名满足以下标准：
>
> - 你必须能够管理 DNS 配置设置，并添加一条 TXT 记录。
> - 它不是一个子域名（{subdomain}.github.io、{subdomain}.contoso.com 或类似的）。
> - 它必须使用 HTTPS 协议。
> - 它必须能对一个 HEAD 请求返回 HTTP 200 状态。

（例如 `yourname.github.io` 是 GitHub 的子域名，你也无法修改它的 DNS，所以不符合条件，需要一个自己的域名。）

<a id="extension-pricing-label"></a>
### 扩展定价标签（Extension pricing label）

> 你可以选择在扩展的市场页面上显示一个定价标签，表明它是 `Free`（免费）还是 `Free Trial`（免费试用）。
>
> 要显示定价标签，在你的 `package.json` 中添加 `pricing` 属性。例如：

```json
{
  "pricing": "Free"
}
```

> 允许的值是：`Free` 和 `Trial`（区分大小写）。当没有指定 `pricing` 属性时，默认值是 `Free`。

> **注意**
>
> 发布扩展时，请确保使用 `vsce` 版本 >= `2.10.0`，定价标签才能生效。

（`Trial` 在市场页面上显示为 “Free Trial”。市场本身不提供付费功能，`Trial` 适用于扩展免费但需要购买外部服务许可的情况。）

<a id="extension-sponsor"></a>
### 扩展赞助（Extension Sponsor）

> 你可以选择开启赞助，为你的用户提供一种支持你工作的方式。
>
> 要显示赞助链接，在你的 `package.json` 中添加 `sponsor` 属性。例如：

```json
"sponsor": {
  "url": "https://github.com/sponsors/nvaccess"
}
```

> **注意**
>
> 发布扩展时，请确保使用 `vsce` 版本 >= `2.9.1`，赞助功能才能生效。
>
> 赞助链接会出现在市场中你的扩展页面上，以及 VS Code 中扩展详情的标题区域：

![扩展详情页中的赞助链接](images/publishing-extension/sponsor-link-example.png)

> 我们希望这能让用户资助他们所依赖的扩展，以改进扩展的性能、可靠性和稳定性。

<a id="using-vscodeignore"></a>
### 使用 .vscodeignore（Using .vscodeignore）

> 你可以创建一个 `.vscodeignore` 文件，防止一些文件被包含在扩展的包中。这个文件是一组 [glob](https://github.com/isaacs/minimatch) 模式，每行一个。例如：

```text
**/*.ts
**/tsconfig.json
!file.ts
```

> 你应该忽略所有运行时不需要的文件。例如，如果你的扩展是用 TypeScript 编写的，就应该像上面的例子那样，忽略所有的 `**/*.ts` 文件。

> **注意**
>
> 列在 `devDependencies` 中的开发依赖会被自动忽略，所以你不需要显式地添加它们。

`!file.ts` 表示“取反”：虽然前面忽略了所有 `.ts` 文件，但 `file.ts` 仍然要包含进来。使用打包工具时，可以直接忽略整个 `node_modules`（见 [打包扩展代码](./bundling-extension.md#publishing)）；不打包时，`vsce` 会自动只包含 `dependencies` 中的生产依赖。

<a id="pre-publish-step"></a>
### 发布前步骤（Pre-publish step）

> 你可以在清单文件中添加一个发布前步骤，每次打包扩展时都会调用它。例如，你可能想在这个阶段调用 [TypeScript](https://www.typescriptlang.org/) 编译器：

```json
{
  "name": "uuid",
  "version": "0.0.1",
  "publisher": "someone",
  "engines": {
    "vscode": "0.10.x"
  },
  "scripts": {
    "vscode:prepublish": "tsc"
  }
}
```

`vscode:prepublish` 在 `vsce package` 和 `vsce publish` 时都会自动运行，确保打包的是最新编译的代码。使用打包工具时，它通常是 `npm run package`（见 [打包扩展代码](./bundling-extension.md)）。（示例中的 `"vscode": "0.10.x"` 是一个很早期的版本写法，实际项目中应写 `^1.xx.0` 的形式。）

<a id="pre-release-extensions"></a>
### 预发布扩展（Pre-release extensions）

> 用户可以在 VS Code 或 VS Code Insiders 中安装扩展的预发布版本，从而在正式发布之前，定期获得最新的扩展版本。

![扩展视图中 GitHub PR 扩展的预发布版本](images/publishing-extension/pre-release.png)

截图中，“GitHub Pull Requests and Issues” 扩展的安装按钮显示为 **Install Pre-Release**（安装预发布版本），左上角有一个表示预发布的标记。

> 要发布一个预发布版本，向 `vsce package` 或 `vsce publish` 命令传入 `--pre-release` 标志：

```bash
vsce package --pre-release
vsce publish --pre-release
```

> 我们只支持 `major.minor.patch` 形式的扩展版本号，**不支持** `semver` 的预发布标签。预发布版本和正式版本的版本号必须不同。也就是说，如果 `1.2.3` 作为预发布版本上传了，下一个正式版本就必须用一个不同的版本号上传，例如 `1.2.4`。完整的 `semver` 支持将在未来提供。
>
> VS Code 会自动把扩展更新到可用的最高版本，所以即使用户选择了预发布版本，如果有一个版本号更高的正式版本，用户也会被更新到这个正式版本。因此，我们建议扩展在正式版本中使用 `major.EVEN_NUMBER.patch`（主版本.偶数.补丁），在预发布版本中使用 `major.ODD_NUMBER.patch`（主版本.奇数.补丁）。例如：`0.2.*` 用于正式版本，`0.3.*` 用于预发布版本。
>
> 如果扩展作者不希望预发布用户被更新到正式版本，我们建议在发布正式版本之前，总是先递增版本号并发布一个新的预发布版本，确保预发布版本的版本号总是更高。注意，虽然预发布用户会在正式版本更高时被更新到正式版本，但他们仍然有资格自动更新到版本号高于这个正式版本的未来预发布版本。
>
> VS Code `1.63.0` 之后才支持预发布扩展，所以所有的预发布扩展都应该在 `package.json` 中把 `engines.vscode` 的值设为 `>= 1.63.0`。

**“不支持 semver 预发布标签”** 是指不能用 `1.2.3-beta.1` 这样的版本号区分预发布，而是靠 `--pre-release` 标志。

**奇偶版本号方案示例：**

```text
正式版：0.2.0  0.2.1  0.2.2        0.4.0
预发布：             0.3.0  0.3.1        0.5.0 ...
```

预发布用户安装了 `0.3.1`；之后正式版 `0.4.0` 发布，`0.4.0 > 0.3.1`，于是预发布用户也被更新到 `0.4.0`；再之后预发布 `0.5.0` 发布，他们又会被更新到 `0.5.0`。

<a id="platform-specific-extensions"></a>
### 平台特定的扩展（Platform-specific extensions）

> 你可以为 VS Code 所运行的每个平台（Windows、Linux、macOS）发布扩展的 VSIX 包。我们把这样的扩展称为**平台特定的（platform-specific）**扩展。
>
> 从 `1.61.0` 版本开始，VS Code 会查找与当前平台匹配的扩展包。
>
> 如果你的扩展有平台特定的库或依赖，平台特定的扩展就很有用，你可以控制平台包中所包含的具体的二进制文件。一个常见的使用场景是使用**原生 node 模块（native node modules）**。
>
> 平台特定的扩展作为单独的包发布，其中包含平台特定的内容。你可以通过传入 [`--target` 标志](#publishing)来指定目标平台。如果你不传入这个标志，这个包会被用作所有没有平台特定包的平台的后备。
>
> 目前可用的平台有：`win32-x64`、`win32-arm64`、`linux-x64`、`linux-arm64`、`linux-armhf`、`alpine-x64`、`alpine-arm64`、`darwin-x64`、`darwin-arm64` 和 `web`。
>
> 如果你希望一个平台特定的扩展也支持作为 [Web 扩展](../extension-guides/web-extensions.md)在浏览器中运行，它在发布时**必须**以 `web` 平台为目标。`web` 平台遵循 `package.json` 中的 `browser` 入口。要禁用 `web` 中不支持的扩展功能，我们建议在 `package.json` 中使用 `when` 子句，而不是为 web 平台提供单独的 `package.json`，或者从 VSIX 中删除在 `web` 中不能工作的部分。

| 平台标识 | 含义 |
|---|---|
| `win32-x64` / `win32-arm64` | Windows（x64 / ARM64） |
| `linux-x64` / `linux-arm64` / `linux-armhf` | Linux（x64 / ARM64 / 32 位 ARM，如树莓派） |
| `alpine-x64` / `alpine-arm64` | Alpine Linux（常见于 Docker 容器，使用 musl 而不是 glibc，原生模块需要单独编译） |
| `darwin-x64` / `darwin-arm64` | macOS（Intel / Apple 芯片） |
| `web` | 浏览器中的 VS Code（vscode.dev 等） |

**原生 node 模块**是包含 C/C++ 编译产物（`.node` 文件）的 npm 包，每个平台的编译结果都不同。如果只发布一个通用的包，就得把所有平台的二进制文件都塞进去，体积很大；平台特定的扩展让每个平台的用户只下载属于自己平台的那一份。

用于在 `web` 平台上隐藏不支持的功能的 `when` 子句，可以使用 `isWeb` 上下文键，例如 `"when": "!isWeb"`。

<a id="publishing"></a>
<a id="publishing"></a>
#### 发布（Publishing）

> 从 `1.99.0` 版本开始，[vsce](https://github.com/microsoft/vscode-vsce) 支持一个 `--target` 参数，让你在打包和发布 VSIX 时可以指定目标平台。
>
> 下面是为 `win32-x64` 和 `win32-arm64` 平台发布 VSIX 的方法：

```bash
vsce publish --target win32-x64 win32-arm64
```

> 或者，你也可以在打包时使用 `--target` 标志，创建一个平台特定的 VSIX。例如，为 `win32-x64` 平台打包一个 VSIX，然后发布它：

```bash
vsce package --target win32-x64
vsce publish --packagePath PATH_TO_WIN32X64_VSIX
```

（这里的 `1.99.0` 是 **vsce** 的版本号，而不是 VS Code 的版本号；当前的 `@vscode/vsce` 早已高于这个版本。）

注意：`vsce publish --target win32-x64 win32-arm64` 只是给包打上平台标签，并不会帮你准备不同平台的二进制文件。通常的做法是在每个平台（或交叉编译）上分别安装依赖、打包，再发布各自的 VSIX，这就是下一节推荐用 CI 的原因。

<a id="continuous-integration"></a>
#### 持续集成（Continuous integration）

> 管理多个平台特定的 VSIX 可能会让人不堪重负，所以我们建议使用[持续集成](./continuous-integration.md)（CI）工具来自动化扩展的构建过程。例如，你可以使用 [GitHub Actions](https://github.com/features/actions) 来构建你的扩展。我们的[平台特定扩展示例](https://github.com/microsoft/vscode-platform-specific-sample)可以作为学习的起点：它的[工作流](https://github.com/microsoft/vscode-platform-specific-sample/blob/main/.github/workflows/ci.yml)实现了一个常见的场景，即使用平台特定扩展的支持，把原生 node 模块作为依赖分发到所有支持的 VS Code 目标平台上。

---

<a id="next-steps"></a>
## 下一步（Next steps）

> - [扩展市场](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace) - 进一步了解 VS Code 的公共扩展市场。
> - [测试扩展](./testing-extension.md) - 为你的扩展项目添加测试，确保高质量。
> - [打包扩展代码](./bundling-extension.md) - 使用 webpack 打包扩展文件，改善加载时间。

---

<a id="common-questions"></a>
## 常见问题（Common questions）

<a id="i-get-a-you-exceeded-the-number-of-allowed-tags-of-30-error-when-i-try-to-publish-my-extension"></a>
### 我尝试发布扩展时，出现了 "You exceeded the number of allowed tags of 30" 错误？（I get a "You exceeded the number of allowed tags of 30" error when I try to publish my extension?）

> Visual Studio 市场不允许一个扩展包在 `package.json` 中有超过 30 个 `keywords`。把关键词 / 标签的数量限制在最多 30 个，就能避免这个错误。

（错误信息的意思是“你超过了允许的 30 个标签的数量”。）

<a id="i-get-403-forbidden-or-401-unauthorized-error-when-i-try-to-publish-my-extension"></a>
### 我尝试发布扩展时，出现了 403 Forbidden（或 401 Unauthorized）错误？（I get 403 Forbidden (or 401 Unauthorized) error when I try to publish my extension?）

> 创建 PAT（个人访问令牌）时一个容易犯的错误，是在 **Organizations**（组织）字段的下拉框中选择了某个特定的组织，而不是 **All accessible organizations**（所有可访问的组织）。另一个可能的错误是范围不正确，你应该把授权的范围设为 `Marketplace (Manage)`，发布才能成功。

<a id="i-cant-unpublish-my-extension-through-the-vsce-tool"></a>
### 我无法通过 `vsce` 工具取消发布我的扩展？（I can't unpublish my extension through the `vsce` tool?）

> 你可能更改了扩展 ID 或发布者 ID。你也可以直接通过 [Visual Studio 市场的发布者管理页面](https://marketplace.visualstudio.com/manage)管理你的扩展。例如，更新或[取消发布](#unpublishing-extensions)。

<a id="why-does-vsce-not-preserve-file-attributes"></a>
### 为什么 vsce 不保留文件属性？（Why does vsce not preserve file attributes?）

> 注意，在 Windows 上构建和发布扩展时，扩展包中包含的所有文件都会缺少 POSIX 文件属性，也就是可执行位。一些 `node_modules` 依赖需要这些属性才能正常工作。在 Linux 和 macOS 上发布则能按预期工作。

例如扩展中附带了一个需要在 Linux / macOS 上执行的二进制文件或 shell 脚本，从 Windows 打包后它会失去可执行权限，用户运行时会出现 “Permission denied”。解决方法是在 Linux / macOS 上（例如 CI 中）打包发布，或者在扩展运行时用 `fs.chmod` 补上权限。

<a id="can-i-publish-from-a-continuous-integration-ci-build"></a>
### 我可以从持续集成（CI）构建中发布吗？（Can I publish from a continuous integration (CI) build?）

> 可以，参见[持续集成](./continuous-integration.md)主题中的[自动发布](./continuous-integration.md#automated-publishing)一节，了解如何配置 Azure DevOps、GitHub Actions 和 GitLab CI，自动把你的扩展发布到市场。

（同时请注意本篇开头关于全局 PAT 于 2026 年 12 月 1 日停用的说明，以及 [安全地自动发布](#secure-automated-publishing-to-visual-studio-marketplace) 一节。）

<a id="i-get-error-the-extension-name-already-exists-in-the-marketplace-error-when-i-try-to-publish-my-extension"></a>
### 我尝试发布扩展时，出现了 "ERROR The extension 'name' already exists in the Marketplace" 错误？（I get "ERROR The extension 'name' already exists in the Marketplace" error when I try to publish my extension?）

> 市场要求每个扩展的[扩展名称](../references/extension-manifest.md)都是唯一的。如果市场中已经存在一个同名的扩展，你会得到以下错误：

```text
ERROR The extension 'name' already exists in the Marketplace.
```

> 同样的规则也适用于扩展的[显示名称](../references/extension-manifest.md)。

（错误信息的意思是“错误：扩展 'name' 已经存在于市场中”。这里的“名称”是 `package.json` 的 `name` 字段，“显示名称”是 `displayName` 字段，两者都要在整个市场中唯一，即使发布者不同。所以最好在开发初期就去市场搜索一下，确认名称没有被占用。）

<a id="what-package-managers-are-supported"></a>
### 支持哪些包管理器？（What package managers are supported?）

> 你可以使用 npm 或 yarn v1 来管理扩展的依赖。

（pnpm 和 Yarn 2+ 的依赖目录结构不同，`vsce` 不能正确地收集依赖。使用这些包管理器时，最好配合打包工具（见 [打包扩展代码](./bundling-extension.md)），把依赖都打进 `dist/extension.js`，然后用 `vsce package --no-dependencies` 打包，让 `vsce` 不再处理 `node_modules`。）

<a id="i-need-help-with-my-vs-marketplace-account-or-support-in-publishing-an-extension"></a>
### 我的 VS 市场账户需要帮助，或者发布扩展时需要支持？（I need help with my VS Marketplace account or support in publishing an extension?）

> 你可以登录 [Manage Publishers & Extensions](https://marketplace.visualstudio.com/manage)（管理发布者和扩展），点击右上角的 “Contact Microsoft”（联系微软）链接，联系 VS 市场支持团队。

---

## 本篇小结

```text
工具：npm install -g @vscode/vsce
  vsce package（.vsix）/ publish / login / ls / unpublish（= 删除，不可撤销）

第一次发布：凭证（PAT：All accessible organizations + Marketplace Manage）
           → 市场管理页面创建发布者（ID 不可改）→ package.json 的 publisher → vsce login → vsce publish
  重要：全局 PAT 于 2026-12-01 停用 → CI 中改用 Entra ID 托管标识 + vsce publish --azure-credential

发布前检查：图标 PNG ≥ 128px（不能是 SVG）；README 图片用 https；修改模板 README；
           .vscodeignore 正确（vsce ls）；vscode:prepublish 编译 / 打包
           engines.vscode 不低于 @types/vscode 的版本

版本：vsce publish patch / minor / major；同一版本号只能发布一次
下架：取消发布（可恢复，保留数据）/ 删除（不可恢复，名称永久作废）/ 删除某个版本（不能删最新版）
弃用：在讨论帖中申请，可推荐替代扩展或设置
预发布：--pre-release；推荐奇数 minor 为预发布，偶数 minor 为正式版；engines ≥ 1.63.0
平台特定：--target win32-x64 等（含 web）；用 CI 为各平台分别打包
其他：认证发布者（域名 TXT 记录，6 个月门槛）、pricing、sponsor
```
