# 文件图标主题（File Icon Theme）

> 原文：[File Icon Theme](https://code.visualstudio.com/api/extension-guides/file-icon-theme)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/file-icon-theme.md`（DateApproved: 10/7/2026）

> VS Code 会在界面的各个位置、在文件名旁边显示图标，扩展可以贡献新的文件图标集，供用户选择。

文件图标会显示在资源管理器、编辑器标签页、面包屑导航、快速打开列表等地方。用户通过命令面板中的 **Preferences: File Icon Theme** 切换文件图标主题。

在 [主题](../extension-capabilities/theming.md) 一篇中已经介绍过它的原理：**两步映射**——先定义图标（`iconDefinitions`），再把文件关联到图标。本篇是完整的配置说明。

---

<a id="adding-a-new-file-icon-theme"></a>
## 添加新的文件图标主题（Adding a new File Icon Theme）

> 你可以用图标（最好是 SVG）或图标字体来创建自己的文件图标主题。可以参考两个内置主题作为示例：[Minimal](https://github.com/microsoft/vscode/tree/main/extensions/theme-defaults) 和 [Seti](https://github.com/microsoft/vscode/tree/main/extensions/theme-seti)。
>
> 首先，创建一个 VS Code 扩展，并添加 `iconTheme` 贡献点。

```json
{
  "contributes": {
    "iconThemes": [
      {
        "id": "turtles",
        "label": "Turtles",
        "path": "./fileicons/turtles-icon-theme.json"
      }
    ]
  }
}
```

（原文这里写的是 `iconTheme`，但实际的贡献点名称是 `iconThemes`，如代码所示。）

> `id` 是图标主题的标识符。它会作为设置中的标识符使用，所以要让它既唯一又可读。`label` 显示在文件图标主题选择器的下拉列表中。`path` 指向扩展中定义图标集的文件。如果你的图标集文件名符合 `*icon-theme.json` 的命名规则，在 VS Code 中编辑它时就能获得补全和悬停提示。

| 字段 | 作用 |
|---|---|
| `id` | 主题标识符。用户选择这个主题后，设置中会保存为 `"workbench.iconTheme": "turtles"` |
| `label` | 在主题选择列表中显示的名称 |
| `path` | 图标集文件的路径（建议以 `-icon-theme.json` 结尾，以获得编辑提示） |

<a id="file-icon-set-file"></a>
### 文件图标集文件（File Icon Set File）

> 文件图标集文件是一个 JSON 文件，由文件图标关联和图标定义组成。
>
> 图标关联把一种文件类型（'file'、'folder'、'json-file'……）映射到一个图标定义。图标定义指定图标在哪里：可以是一个图片文件，也可以是字体中的一个字形（glyph）。

文件的整体结构：

```jsonc
{
  "fonts": [ ... ],            // （可选）字体定义：使用图标字体时需要
  "iconDefinitions": { ... },  // 图标定义：定义每个图标是什么
  // ↓ 以下是文件关联：哪些文件用哪个图标
  "file": "...",
  "folder": "...",
  "fileExtensions": { ... },
  "fileNames": { ... },
  "languageIds": { ... },
  "light": { ... },            // 浅色主题下的覆盖
  "highContrast": { ... },     // 高对比度主题下的覆盖
  "hidesExplorerArrows": false,
  "showLanguageModeIcons": false
}
```

<a id="icon-definitions"></a>
### 图标定义（Icon definitions）

> `iconDefinitions` 部分包含所有的定义。每个定义都有一个 id，用来引用这个定义。一个定义也可以被多个文件关联引用。

```json
{
  "iconDefinitions": {
    "_folder_dark": {
      "iconPath": "./images/Folder_16x_inverse.svg"
    }
  }
}
```

> 上面的图标定义中包含一个标识符为 `_folder_dark` 的定义。
>
> 支持以下属性：

| 属性 | 用于 | 说明 |
|---|---|---|
| `iconPath` | 图片（svg / png） | 图片的路径 |
| `fontCharacter` | 图标字体 | 要使用的字体中的字符 |
| `fontColor` | 图标字体 | 字形使用的颜色 |
| `fontSize` | 图标字体 | 字号。默认使用字体定义中指定的大小。应该是相对于父级字号的相对大小（例如 150%） |
| `fontId` | 图标字体 | 字体的 id。不指定时，使用字体定义部分中的第一个字体 |

图标 id 前面的下划线（如 `_folder_dark`）只是一种命名习惯，用来和文件名、扩展名区分开，不是必须的。

**图片还是字体？**

| | 图片（SVG） | 图标字体 |
|---|---|---|
| 颜色 | 图片本身的颜色，可以是多色 | 单色，通过 `fontColor` 设置，修改颜色很方便 |
| 制作 | 每个图标一个文件，简单直观 | 需要把所有图标做成一个字体文件 |
| 文件数量 | 图标多时文件很多 | 一个字体文件 |

<a id="file-association"></a>
### 文件关联（File association）

> 图标可以关联到文件夹、文件夹名、文件、文件扩展名、文件名，以及[语言 ID](../references/contribution-points.md#contributes.languages)。
>
> 此外，这些关联中的每一种，都可以针对“浅色”和“高对比度”颜色主题分别细化。
>
> 每个文件关联都指向一个图标定义。

```json
{
  "file": "_file_dark",
  "folder": "_folder_dark",
  "folderExpanded": "_folder_open_dark",
  "folderNames": {
    ".vscode": "_vscode_folder"
  },
  "fileExtensions": {
    "ini": "_ini_file"
  },
  "fileNames": {
    "win.ini": "_win_ini_file"
  },
  "languageIds": {
    "ini": "_ini_file"
  },
  "light": {
    "folderExpanded": "_folder_open_light",
    "folder": "_folder_light",
    "file": "_file_light",
    "fileExtensions": {
      "ini": "_ini_file_light"
    }
  },
  "highContrast": {}
}
```

所有关联属性的完整说明：

| 属性 | 作用 | 说明 |
|---|---|---|
| `file` | 默认文件图标 | 所有没有匹配到任何扩展名、文件名或语言 ID 的文件，都显示这个图标。目前，`file` 图标定义的所有属性都会被继承（只对字体字形有意义，可用于统一设置 `fontSize`） |
| `folder` | 折叠状态的文件夹图标 | 如果没有设置 `folderExpanded`，展开状态的文件夹也用它。特定名称的文件夹可以用 `folderNames` 关联图标。文件夹图标是可选的，不设置时文件夹不显示图标 |
| `folderExpanded` | 展开状态的文件夹图标 | 可选。不设置时显示 `folder` 的图标 |
| `folderNames` | 按文件夹名关联图标 | 键是文件夹名，可以加上一级父目录前缀（*）。不支持模式和通配符。匹配时不区分大小写 |
| `folderNamesExpanded` | 按文件夹名关联展开状态的图标 | 规则同 `folderNames` |
| `rootFolder` | 折叠状态的工作区根文件夹图标 | 如果没有设置 `rootFolderExpanded`，展开状态的根文件夹也用它。不设置时，根文件夹显示 `folder` 的图标 |
| `rootFolderExpanded` | 展开状态的工作区根文件夹图标 | 不设置时显示 `rootFolder` 的图标 |
| `rootFolderNames` | 按根文件夹名关联图标 | 键是文件夹名。不支持模式和通配符。匹配时不区分大小写 |
| `rootFolderNamesExpanded` | 按根文件夹名关联展开状态的图标 | 规则同 `rootFolderNames` |
| `languageIds` | 按语言关联图标 | 键是[语言贡献点](../references/contribution-points.md#contributes.languages)中定义的语言 ID。文件的语言根据语言贡献中定义的文件扩展名和文件名来判断。注意，语言贡献中的“首行匹配”（first line match）不会被考虑 |
| `fileExtensions` | 按文件扩展名关联图标 | 键是扩展名，即文件名中点后面的部分（不含点）。有多个点的文件名，如 `lib.d.ts`，可以匹配多个扩展名：`d.ts` 和 `ts`。可以加上一级父目录前缀（*）。比较时不区分大小写 |
| `fileNames` | 按文件名关联图标 | 键是完整的文件名，不包含任何路径部分。可以加上一级父目录前缀（*）。不支持模式和通配符。匹配时不区分大小写。文件名匹配是最强的匹配，优先于扩展名匹配和语言 ID 匹配 |

**几点解读：**

- **工作区根文件夹**是指在资源管理器中最顶层的那个文件夹（你用“打开文件夹”打开的那个）。多根工作区中会有多个根文件夹。
- **首行匹配不被考虑**：有些语言是根据文件第一行的内容识别的，比如第一行是 `#!/bin/bash` 的无扩展名文件会被识别为 Shell 脚本。但文件图标主题在判断语言时不会读取文件内容，所以这类文件不会通过 `languageIds` 匹配到图标。
- **`lib.d.ts` 的匹配**：可以同时在 `fileExtensions` 中写 `"d.ts"` 和 `"ts"`，给 TypeScript 声明文件一个和普通 `.ts` 文件不同的图标。更长的扩展名会优先匹配。

> (*) 有些属性的键（`folderNames`、`folderNamesExpanded`、`fileExtensions`、`fileNames`）可以加上一级父目录作为前缀。只有当资源的直接父文件夹与这个父目录匹配时，才会使用这个图标。这可以用来让某个特定文件夹（例如 `system`）中的资源显示不同的外观：

```json
  "fileNames": {
    "system/win.ini": "_win_ini_file"
  },
```

> `system/win.ini` 表示这条关联匹配直接位于 `system` 文件夹中、名为 `win.ini` 的文件。

```json
  "fileExtensions": {
    "system/ini": "_ini_file"
  },
```

> `system/ini` 表示这条关联匹配直接位于 `system` 文件夹中的 `*.ini` 文件。

注意是**直接**父文件夹，而且**只能有一级**：`system/win.ini` 能匹配 `system/win.ini`、`a/b/system/win.ini`，但不能匹配 `system/sub/win.ini`；也不能写成 `a/system/win.ini` 这样的两级前缀。

> 扩展名匹配优先于语言匹配，但比文件名匹配弱。同一种匹配中，带父目录前缀的匹配优先于不带前缀的匹配。

```text
带父目录的文件名匹配 > 文件名匹配 > 带父目录的扩展名匹配 > 扩展名匹配 > 语言匹配 ...
```

举例：资源管理器中有一个 `system/win.ini` 文件，按优先级依次检查：

```text
1. fileNames 中有 "system/win.ini" 吗？   有 → 使用它
2. fileNames 中有 "win.ini" 吗？
3. fileExtensions 中有 "system/ini" 吗？
4. fileExtensions 中有 "ini" 吗？
5. languageIds 中有 "ini" 吗？
6. 都没有 → 使用 file 默认图标
```

> `light` 和 `highContrast` 部分拥有上面列出的所有文件关联属性。它们用于为对应类型的主题覆盖图标。

也就是说，顶层的关联默认用于深色主题；当用户使用浅色主题时，`light` 中定义的关联会覆盖顶层的同名关联，没有覆盖的部分继续使用顶层的设置。

<a id="font-definitions"></a>
### 字体定义（Font definitions）

> `fonts` 部分让你可以声明任意数量想要使用的字形字体。之后可以在图标定义中引用这些字体。如果某个图标定义没有指定字体 id，就会使用第一个声明的字体作为默认字体。
>
> 把字体文件复制到你的扩展中，并相应地设置路径。建议使用 [WOFF](https://developer.mozilla.org/docs/Web/Guide/WOFF) 字体。
>
> - 把格式设为 'woff'。
> - weight（字重）属性的取值[在这里](https://developer.mozilla.org/docs/Web/CSS/font-weight#Values)定义。
> - style（样式）属性的取值[在这里](https://developer.mozilla.org/docs/Web/CSS/@font-face/font-style#Values)定义。
> - size（大小）应该相对于使用图标处的字号。因此，始终使用百分比。

```json
{
  "fonts": [
    {
      "id": "turtles-font",
      "src": [
        {
          "path": "./turtles.woff",
          "format": "woff"
        }
      ],
      "weight": "normal",
      "style": "normal",
      "size": "150%"
    }
  ],
  "iconDefinitions": {
    "_file": {
      "fontCharacter": "\\E002",
      "fontColor": "#5f8b3b",
      "fontId": "turtles-font"
    }
  }
}
```

`fontCharacter` 中的 `\\E002` 是 Unicode 编码 `E002` 对应的字符。在 JSON 中反斜杠要写两次转义。图标字体通常把图标放在 Unicode 的“私用区”（`E000`–`F8FF`），这个区域的编码不对应任何普通文字。

<a id="folder-icons-in-file-icon-themes"></a>
### 文件图标主题中的文件夹图标（Folder icons in File Icon Themes）

> 如果文件夹图标本身足以表示文件夹的展开状态，文件图标主题可以要求资源管理器不显示默认的文件夹指示图标（那个会旋转的小三角，也叫 “twisties”）。在文件图标主题定义文件中设置 `"hidesExplorerArrows":true` 即可启用这个模式。

例如图标主题已经用“打开的文件夹”和“关闭的文件夹”两种图标区分了展开状态，那么前面的小箭头就是多余的，可以隐藏掉。

<a id="language-default-icons"></a>
### 语言默认图标（Language default icons）

> 语言贡献者可以为语言定义一个图标。

```jsonc
{
  "contributes": {
    "languages": [
      {
        "id": "latex",
        // ...
        "icon": {
          "light": "./icons/latex-light.png",
          "dark": "./icons/latex-dark.png"
        }
      }
    ]
  }
}
```

> 如果某个文件图标主题对这种语言只有一个通用的文件图标，就会使用这个图标。
>
> 只有满足以下条件时，才会显示语言默认图标：
>
> - 文件图标主题有特定的文件图标。例如，`Minimal` 没有特定的文件图标，因此不会使用语言默认图标。
> - 文件图标主题中没有包含针对给定语言、文件扩展名或文件名的图标。
> - 文件图标主题没有定义 `"showLanguageModeIcons":false`。
>
> 如果满足以下条件，语言默认图标总是会显示：
>
> - 文件图标主题定义了 `"showLanguageModeIcons":true`。

**这一节是写给谁的？** 不是写给图标主题作者的，而是写给**语言扩展作者**的（见 [语言扩展](../language-extensions/overview.md)）。比如你做了一个支持某种新语言的扩展，用户安装的图标主题里肯定没有这种语言的图标，这时就可以用 `icon` 字段自带一个默认图标，让它在大多数图标主题下也能显示得好看。

`showLanguageModeIcons` 则是图标主题作者用来控制“要不要显示语言扩展自带的默认图标”的开关：

| 图标主题的设置 | 语言默认图标 |
|---|---|
| `"showLanguageModeIcons": true` | 总是显示 |
| `"showLanguageModeIcons": false` | 从不显示 |
| 不设置 | 主题有特定文件图标，且没有为这种文件定义图标时才显示 |

---

## 本篇小结

```text
package.json：contributes.iconThemes（id、label、path）

图标集文件（*-icon-theme.json）
  ├─ fonts：（可选）图标字体（推荐 woff，size 用百分比）
  ├─ iconDefinitions：定义图标（iconPath 图片 / fontCharacter + fontColor 字体）
  ├─ 关联：file、folder(Expanded)、rootFolder(Expanded)、
  │        folderNames(Expanded)、rootFolderNames(Expanded)、
  │        fileExtensions、fileNames、languageIds
  ├─ light / highContrast：按主题类型覆盖关联
  ├─ hidesExplorerArrows：隐藏文件夹前的小三角
  └─ showLanguageModeIcons：是否显示语言扩展自带的默认图标

匹配优先级：带父目录的文件名 > 文件名 > 带父目录的扩展名 > 扩展名 > 语言
```
