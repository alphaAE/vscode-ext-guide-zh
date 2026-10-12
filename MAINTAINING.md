# 维护指南：跟进官方文档更新

本文记录如何把官方英文文档的更新同步到本指南。任何人（或任何 AI 工具）只要按本文操作，就能完成一次同步，不依赖之前的对话或个人记忆。

## 一、当前同步状态

上游基准提交：`aeaa6ffe7e675ab1eaf3e9e8af1df9358c91911b`

| 项目 | 值 |
|---|---|
| 上游仓库 | [microsoft/vscode-docs](https://github.com/microsoft/vscode-docs)，分支 `main`，只关心 `api/` 目录 |
| 基准提交 | `aeaa6ff`（2026-10-10，“Reference Ruby testing in Testing user guide next steps”） |
| 对照的 API 类型版本 | `@types/vscode` 1.140.0（补充代码以此为准核对） |

上面“上游基准提交”一行会被 `tools/sync_check.py` 读取，**请保持这一行的格式不变**（完整的 40 位提交号放在反引号中）。每次同步完成后更新它，并在文末的“同步记录”中加一行。

## 二、核心原理

本指南的每一版都对应上游的某一个提交。同步时，比较“基准提交”和“上游最新提交”之间 `api/` 目录的差异，**只处理有变化的文件**，没有变化的文件不用动。

注意：每篇文件头里的 `DateApproved` 只能作参考，**不能用来判断原文是否变化**。官方经常统一批量修改这个日期，而修改正文时又不一定会改它。判断依据始终是提交之间的差异。

本仓库的目录结构与上游 `api/` 完全一致：上游的 `api/extension-guides/webview.md` 对应本仓库的 `extension-guides/webview.md`，上游的 `api/extension-guides/images/webview/` 对应本仓库的 `extension-guides/images/webview/`。

## 三、准备工作（第一次做时）

需要 Git、[Git LFS](https://git-lfs.com/) 和 Python 3.8 或更高版本。

1. 克隆本仓库，并启用 LFS（图片和视频存放在 LFS 中）：

   ```bash
   git lfs install
   git clone https://git.alphaae.com/alphaae/vscode-ext-guide-zh.git
   ```

2. 在本仓库旁边克隆上游仓库。上游仓库很大，只需要 `api/` 目录，用稀疏克隆即可：

   ```bash
   git clone --filter=blob:none --sparse --depth=200 https://github.com/microsoft/vscode-docs.git
   cd vscode-docs
   git sparse-checkout set api
   ```

   如果比较时提示找不到基准提交，说明克隆的历史不够深，执行 `git fetch --deepen=500 origin main` 再试。

## 四、同步步骤

以下命令都在本仓库根目录执行，假设上游仓库克隆在 `../vscode-docs`。

### 1. 列出需要处理的文件

```bash
python tools/sync_check.py ../vscode-docs --fetch
```

脚本会自动读取本文中的基准提交，获取上游最新版本，并列出 `api/` 下所有变化的文件：

- **文档变化**：`[修改]`、`[新增]`、`[删除]`、`[重命名]` 的 `.md` 文件，已换算成本仓库中的路径；
- 标注“仅文件头元数据变化”的文件，只是 `DateApproved` 等元数据变了，正文没变，只需更新译文的文件头；
- **图片 / 其他资源变化**：`images/` 目录下的文件等。

如果输出“api/ 目录没有变化”，说明无需同步，到此结束。

### 2. 查看每一篇的具体改动

```bash
git -C ../vscode-docs diff <基准提交前 7 位> <目标提交前 7 位> -- api/extension-guides/webview.md
```

脚本输出的最后几行会给出带好提交号的命令。

### 3. 按变化类型修改译文

| 原文变化 | 要做的事 |
|---|---|
| 修改 | 对照差异，修改译文中对应的段落；表格、列表的增删要逐项同步；更新文件头的 `DateApproved` |
| 仅元数据变化 | 只把译文文件头的 `DateApproved` 改成与原文一致 |
| 新增 | 按 [编写规范](./CONVENTIONS.md) 新译一篇，复制对应的 `images/` 目录，在 [README](./README.md) 目录中加入 |
| 删除 | 删除译文和不再使用的图片，从 README 中移除，查找并修改指向它的链接 |
| 重命名 / 移动 | 移动译文文件和图片，修改所有指向它的链接 |
| 图片变化 | 把上游 `api/` 下对应的图片、视频复制到本仓库的相同位置 |

修改时同时检查本仓库自己写的内容是否过时：

- 如果原文修复了我们在正文中标注过的错误（搜索“原文”二字可以找到这些说明），删掉对应的说明，并从 [原文勘误清单](./errata.md) 中移除；
- 如果原文改了标题，英文锚点也会变，其他篇里指向旧锚点的链接会失效（下一步的校验能查出来）；
- 新出现的术语先加入 [术语表](./glossary.md)。

翻译和讲解的写法见 [编写规范](./CONVENTIONS.md)，其中最重要的几条：原文翻译放在引用块 `>` 中、讲解放在引用块外；标题写成“中文（English）”；原文 `/api/...` 的链接改为本仓库内的相对链接；补充的代码要对照 `@types/vscode` 核对。

### 4. 补锚点并校验

```bash
python tools/anchors.py      # 在标题前补上原文的英文锚点 <a id="...">
python tools/clean.py        # 清理脚本误生成的中文锚点
python tools/check.py        # 校验所有本地链接、锚点和图片路径
```

`check.py` 的最后一行显示坏链接数量。目前有 4 处“坏链接”是正文中作为反例写出的路径（`C:/xxx/cat.gif`、`data:image/...` 等），另外 2 处遗留项在 `CONVENTIONS.md` 的示例中，都属于正常现象；除此之外的问题都需要修复。

### 5. 更新基准提交并提交

1. 把本文“一、当前同步状态”中的上游基准提交，改成脚本输出最后一行给出的新提交号，同时更新表格中的提交号和日期；
2. 把 [README](./README.md) 和 [LICENSE](./LICENSE.md) 中写的基准提交号和日期也改成新的；
3. 在本文末尾的“同步记录”中加一行；
4. 提交并推送，提交信息写明同步范围，例如 `同步上游 aeaa6ff..1234567`。

## 五、提交与推送的注意事项

| 事项 | 说明 |
|---|---|
| 提交身份 | 本仓库单独配置了 `user.name = alphaae`、`user.email = alphaae@foxmail.com`（仓库级配置，新克隆后需要重新设置：`git config user.name alphaae`、`git config user.email alphaae@foxmail.com`） |
| 图片和视频 | `*.png`、`*.gif`、`*.jpg`、`*.mp4` 走 Git LFS（规则在 `.gitattributes` 中，与上游一致），新增的图片会自动按 LFS 处理 |
| 推送大小限制 | 服务器限制单次推送的请求大小（超过会返回 HTTP 413）。大文件必须走 LFS，不要把图片、视频直接存进 git |
| 换行符 | `.gitattributes` 规定文本文件统一以 LF 存储，Windows 上工作区显示 CRLF 属于正常现象 |
| 中文提交信息 | 在 Windows 上用脚本生成提交信息时，务必以 UTF-8 写入文件再用 `git commit -F 文件`；Python 默认的 GBK 编码会导致服务器上显示乱码 |
| LFS 补传 | 如果推送后网页上的图片显示为一小段文本（LFS 指针），执行 `git lfs push --all origin` 补传 |

## 六、工具说明

| 脚本 | 作用 |
|---|---|
| `tools/sync_check.py` | 列出上游自基准提交以来的变化，对应到本仓库路径，并识别“仅元数据变化”的文件 |
| `tools/anchors.py` | 根据标题中括号里的英文原文，在标题前插入原文的英文锚点；`--dry` 只检查不修改 |
| `tools/clean.py` | 删除脚本误生成的非 ASCII 锚点（例如由“本篇小结”生成的锚点） |
| `tools/check.py` | 校验所有本地链接、锚点和图片是否存在 |

所有脚本都按自身位置定位本仓库根目录，可以在任意目录下运行。

## 七、同步记录

| 日期 | 上游提交范围 | 说明 |
|---|---|---|
| 2026-10-12 | 首次翻译，基于 `aeaa6ff` | 收录 `api/` 下全部 76 篇及图片、视频 |
