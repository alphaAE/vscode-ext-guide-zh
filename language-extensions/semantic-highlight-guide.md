# 语义高亮指南（Semantic Highlight Guide）

> 原文：[Semantic Highlight Guide](https://code.visualstudio.com/api/language-extensions/semantic-highlight-guide)
> 源文件：`microsoft/vscode-docs` → `api/language-extensions/semantic-highlight-guide.md`（DateApproved: 10/7/2026）

> 语义高亮是对[语法高亮指南](./syntax-highlight-guide.md)中所介绍的语法高亮的补充。VS Code 使用 TextMate 语法作为主要的分词引擎。TextMate 语法以单个文件作为输入，基于用正则表达式表示的词法规则对它进行拆分。
>
> 语义分词让语言服务器可以基于它对如何在项目上下文中解析符号的了解，提供额外的标记信息。主题可以选择使用语义标记，来改进和细化来自语法的高亮。编辑器会把来自语义标记的高亮，叠加在来自语法的高亮之上。

**为什么需要语义高亮？** TextMate 语法只能“看文字的样子”，没有理解代码的能力。比如 `foo(x)`：

- 语法高亮只能看出“`foo` 后面跟着括号，大概是个函数调用”；
- 但 `x` 是参数、局部变量还是全局常量？`Range` 是一个类、一个接口还是一个变量？语法高亮分不清，因为这需要知道它们在哪里被定义。

语言服务器分析了整个项目，知道每个名字指的是什么，就能给出更准确的分类。

> 下面是语义高亮能带来的变化的一个例子：
>
> 没有语义高亮：

![没有语义高亮](images/semantic-highlighting/no-semantic-highlighting.png)

> 有语义高亮：

![有语义高亮](images/semantic-highlighting/with-semantic-highlighting.png)

> 注意基于语言服务对符号的理解所产生的颜色差异：
>
> - 第 10 行：`languageModes` 被着色为参数
> - 第 11 行：`Range` 和 `Position` 被着色为类，`document` 被着色为参数。
> - 第 13 行：`getFoldingRanges` 被着色为函数。

---

<a id="semantic-token-provider"></a>
## 语义标记提供者（Semantic token provider）

> 为了实现语义高亮，语言扩展可以按文档语言和 / 或文件名注册一个“语义标记提供者”。当需要语义标记时，编辑器会向这些提供者发出请求。

```ts
const tokenTypes = ['class', 'interface', 'enum', 'function', 'variable'];
const tokenModifiers = ['declaration', 'documentation'];
const legend = new vscode.SemanticTokensLegend(tokenTypes, tokenModifiers);

const provider: vscode.DocumentSemanticTokensProvider = {
  provideDocumentSemanticTokens(document: vscode.TextDocument): vscode.ProviderResult<vscode.SemanticTokens> {
    // 分析文档，返回语义标记

    const tokensBuilder = new vscode.SemanticTokensBuilder(legend);
    // 在第 1 行，第 1～5 个字符是一个类的声明
    tokensBuilder.push(
      new vscode.Range(new vscode.Position(1, 1), new vscode.Position(1, 5)),
      'class',
      ['declaration'],
    );
    return tokensBuilder.build();
  }
};

const selector = { language: 'java', scheme: 'file' }; // 为本地文件系统中的所有 Java 文档注册

vscode.languages.registerDocumentSemanticTokensProvider(selector, provider, legend);
```

**代码中的三个关键对象：**

| 对象 | 作用 |
|---|---|
| `SemanticTokensLegend`（图例） | 预先声明这个提供者会用到哪些标记类型和修饰符 |
| `SemanticTokensBuilder` | 帮你构建结果：每发现一个标记，就 `push` 一次 |
| `registerDocumentSemanticTokensProvider(selector, provider, legend)` | 注册：对哪些文档生效（[文档选择器](../references/document-selector.md)）、由谁提供、图例是什么 |

几点说明：

- `Position` 的行号和列号**从 0 开始**，所以 `new Position(1, 1)` 实际上是第 2 行第 2 个字符。注释中说的“第 1 行”指的是从 0 开始计数的行号。`Range` 的终点不包含在内，(1,1) 到 (1,5) 覆盖 4 个字符。
- `push` 有两种写法：示例中的写法是 `push(Range, 类型名, 修饰符名数组)`，直接用名字；另一种是 `push(行, 列, 长度, 类型索引, 修饰符位掩码)`，用的是图例中的序号，性能更好，适合大量标记。
- 选择器中的 `scheme: 'file'`，原因见 [虚拟工作区](../extension-guides/virtual-workspaces.md#language-selectors)。

> 语义标记提供者 API 有两种形式，以适应语言服务器的能力：
>
> - `DocumentSemanticTokensProvider`：总是以整个文档作为输入。
>   - `provideDocumentSemanticTokens`：提供文档的所有标记。
>   - `provideDocumentSemanticTokensEdits`：以相对于上一次响应的增量的形式，提供文档的所有标记。
> - `DocumentRangeSemanticTokensProvider`：只作用于一个范围。
>   - `provideDocumentRangeSemanticTokens`：提供文档某个范围内的所有标记。

| 提供者 | 适合 |
|---|---|
| `DocumentSemanticTokensProvider` | 一般情况。`provideDocumentSemanticTokensEdits` 是可选的优化：文档只改了一点时，只返回变化的部分，减少传输量 |
| `DocumentRangeSemanticTokensProvider` | 文件很大时：VS Code 可以只请求屏幕上可见的那一段，先快速显示出来 |

两者可以同时注册。

> 提供者返回的每个标记都带有一个分类，它由一个标记类型、任意数量的标记修饰符，以及一个标记语言组成。
>
> 如上面的示例所示，提供者在一个 `SemanticTokensLegend` 中给出它要使用的类型和修饰符的名称。这让 `provide` 系列 API 可以把标记类型和修饰符以图例中的索引的形式返回。

**为什么要用索引？** 一个大文件可能有几万个标记，如果每个标记都带着 `"class"`、`"declaration"` 这样的字符串，数据量会很大。先在图例中约定好“0 = class，1 = interface……”，每个标记只需要传一个数字。`SemanticTokensBuilder` 会自动帮你完成这种转换。

---

<a id="semantic-token-classification"></a>
## 语义标记的分类（Semantic token classification）

> 语义标记提供者的输出由标记组成。每个标记都有一个范围，以及一个描述这个标记代表哪种语法元素的标记分类。如果这个标记是某个嵌入语言的一部分，分类还可以选择指明一种语言。
>
> 为了描述语法元素的种类，使用的是语义标记类型和修饰符。这些信息类似于[语法高亮指南](./syntax-highlight-guide.md)中介绍的 TextMate 作用域，但我们希望提出一套专门的、更清晰的分类系统。
>
> VS Code 自带了一组标准的语义标记类型和修饰符，供所有语义标记提供者使用。不过，语义标记提供者也可以自由地定义新的类型和修饰符，以及创建标准类型的子类型。

| | TextMate 作用域 | 语义标记 |
|---|---|---|
| 形式 | 一长串名字，如 `entity.name.function.member.ts` | 一个类型 + 若干修饰符，如 `method` + `static`、`readonly` |
| 命名 | 约定俗成，各语言不完全统一 | VS Code 定义了一套标准 |

<a id="standard-token-types-and-modifiers"></a>
### 标准的标记类型和修饰符（Standard token types and modifiers）

> 标准的类型和修饰符涵盖了许多语言都使用的常见概念。虽然每种语言对某些类型和修饰符可能使用不同的术语，但通过遵循标准的分类，主题作者就可以定义跨语言通用的主题规则。
>
> 下面是 VS Code 预定义的标准语义标记类型和语义标记修饰符：

**标准的标记类型：**

| ID | 说明 |
| --- | --- |
| `namespace` | 用于声明或引用命名空间、模块或包的标识符。 |
| `class` | 用于声明或引用类类型的标识符。 |
| `enum` | 用于声明或引用枚举类型的标识符。 |
| `interface` | 用于声明或引用接口类型的标识符。 |
| `struct` | 用于声明或引用结构体类型的标识符。 |
| `typeParameter` | 用于声明或引用类型参数的标识符。 |
| `type` | 用于声明或引用上面没有涵盖的类型的标识符。 |
| `parameter` | 用于声明或引用函数或方法参数的标识符。 |
| `variable` | 用于声明或引用局部或全局变量的标识符。 |
| `property` | 用于声明或引用成员属性、成员字段或成员变量的标识符。 |
| `enumMember` | 用于声明或引用枚举属性、常量或成员的标识符。 |
| `decorator` | 用于声明或引用装饰器和注解的标识符。 |
| `event` | 用于声明事件属性的标识符。 |
| `function` | 用于声明函数的标识符。 |
| `method` | 用于声明成员函数或方法的标识符。 |
| `macro` | 用于声明宏的标识符。 |
| `label` | 用于声明标签的标识符。 |
| `comment` | 用于表示注释的标记。 |
| `string` | 用于表示字符串字面量的标记。 |
| `keyword` | 用于表示语言关键字的标记。 |
| `number` | 用于表示数字字面量的标记。 |
| `regexp` | 用于表示正则表达式字面量的标记。 |
| `operator` | 用于表示运算符的标记。 |

（`typeParameter` 指泛型中的类型参数，比如 `List<T>` 中的 `T`。）

**标准的标记修饰符：**

| ID | 说明 |
| --- | --- |
| `declaration` | 用于符号的声明。 |
| `definition` | 用于符号的定义，例如在头文件中。 |
| `readonly` | 用于只读变量和成员字段（常量）。 |
| `static` | 用于类成员（静态成员）。 |
| `deprecated` | 用于不应再使用的符号。 |
| `abstract` | 用于抽象的类型和成员函数。 |
| `async` | 用于标记为 async 的函数。 |
| `modification` | 用于对变量赋值的变量引用。 |
| `documentation` | 用于符号在文档中出现的地方。 |
| `defaultLibrary` | 用于属于标准库的符号。 |

**类型和修饰符的组合：** 一个标记只有一个类型，但可以有多个修饰符。比如 `const PI = 3.14` 中的 `PI`，是 `variable` + `declaration` + `readonly`；后面引用 `PI` 的地方，是 `variable` + `readonly`。主题可以据此让所有常量（`variable.readonly`）显示成同一种颜色。`deprecated` 修饰符常被用来显示删除线。

> 除了标准的类型和修饰符之外，VS Code 还定义了一份从类型和修饰符到相近的 TextMate 作用域的映射。这在[语义标记作用域映射](#semantic-token-scope-map)一节中介绍。

<a id="custom-token-types-and-modifiers"></a>
### 自定义的标记类型和修饰符（Custom token types and modifiers）

> 如果有必要，扩展可以通过扩展 `package.json` 中的 `semanticTokenTypes` 和 `semanticTokenModifiers` 贡献点，声明新的类型和修饰符，或者创建已有类型的子类型：

```json
{
  "contributes": {
    "semanticTokenTypes": [{
      "id": "templateType",
      "superType": "type",
      "description": "A template type."
    }],
    "semanticTokenModifiers": [{
      "id": "native",
      "description": "Annotates a symbol that is implemented natively"
    }]
  }
}
```

> 在上面的例子中，一个扩展声明了一个新的类型 `templateType` 和一个新的修饰符 `native`。通过把 `type` 指定为父类型，`type` 的主题样式规则也会应用到 `templateType` 上：

```json
{
  "name": "Red Theme",
  "semanticTokenColors": {
    "type": "#ff0011"
  }
}
```

> 上面显示的 `semanticTokenColors` 值 `"#ff0011"` 会同时应用于 `type` 及其所有子类型，包括 `templateType`。

两个描述的意思分别是：`templateType`——“一种模板类型”；`native`——“标注一个以原生方式实现的符号”。

**为什么要指定 `superType`？** 颜色主题不会认识你自定义的 `templateType`。指定了父类型 `type` 之后，主题中为 `type` 设置的颜色就会自动用在它身上，而主题如果想单独处理，也可以为 `templateType` 设置专门的颜色。

> 除了自定义的标记类型，扩展还可以定义这些类型如何映射到 TextMate 作用域。这在[自定义映射](#custom-textmate-scope-mappings)一节中介绍。注意，自定义的映射规则不会自动从父类型继承。子类型需要重新定义映射，最好是映射到更具体的作用域。

---

<a id="enablement-of-semantic-highlighting"></a>
## 语义高亮的启用（Enablement of semantic highlighting）

> 是否计算并高亮语义标记，由设置 `editor.semanticHighlighting.enabled` 决定。它可以取 `true`、`false` 和 `configuredByTheme` 三个值。
>
> - `true` 和 `false` 为所有主题开启或关闭语义高亮。
> - `configuredByTheme` 是默认值，让每个主题自己控制是否启用语义高亮。VS Code 自带的所有主题（例如默认的 “Dark+”）都默认启用了语义高亮。
>
> 依赖语义标记的语言扩展，可以在它们的 `package.json` 中为自己的语言覆盖这个默认值：

```json
{
  "configurationDefaults": {
    "[languageId]": {
      "editor.semanticHighlighting.enabled": true
    }
  }
}
```

（这段 `configurationDefaults` 要写在 `contributes` 下，`[languageId]` 替换成你的语言 ID，比如 `"[mylang]"`。）

**什么时候需要这样做？** 如果你的语言几乎完全依赖语义高亮（比如语法太灵活，用 TextMate 正则很难准确高亮），而用户使用的第三方主题又没有启用语义高亮，那么代码就几乎没有颜色。为自己的语言把它强制设为 `true`，可以保证无论用户用什么主题，都会启用语义高亮。

---

<a id="theming"></a>
## 主题化（Theming）

> 主题化就是为标记分配颜色和样式。主题规则在颜色主题文件（JSON 格式）中指定。用户也可以在用户设置中定制主题规则。

<a id="semantic-coloring-in-color-themes"></a>
### 颜色主题中的语义着色（Semantic coloring in Color Themes）

> 为了支持基于语义标记的高亮，颜色主题文件格式中新增了两个属性。
>
> `semanticHighlighting` 属性定义这个主题是否已经准备好使用语义标记进行高亮。它默认为 false，但我们鼓励所有主题都启用它。当设置 `editor.semanticHighlighting.enabled` 为 `configuredByTheme` 时，会使用这个属性。
>
> `semanticTokenColors` 属性让主题可以定义新的着色规则，这些规则与语义标记提供者发出的语义标记类型和修饰符进行匹配。

```jsonc
{
  "name": "Red Theme",
  "tokenColors": [
    {
      "scope": "comment",
      "settings": {
        "foreground": "#dd0000",
        "fontStyle": "italic"
      }
    }
  ],
  "semanticHighlighting": true,
  "semanticTokenColors": {
    "variable.readonly:java": "#ff0011"
  }
}
```

> `variable.readonly:java` 被称为一个选择器，它的形式是 `(*|tokenType)(.tokenModifier)*(:tokenLanguage)?`。

选择器的语法：

```text
(*|类型)(.修饰符)*(:语言)?

variable.readonly:java
   │        │      └─ 语言：只对 Java 生效（可选）
   │        └──────── 修饰符：readonly（可以有多个，也可以没有）
   └───────────────── 类型：variable；写 * 表示任意类型
```

> 值描述了规则匹配时的样式。它要么是一个表示前景色的字符串，要么是一个对象，形式为 `{ foreground: string, bold: boolean, italic: boolean, underline: boolean }`，或者 `tokenColors` 中 TextMate 主题规则所用的 `{ foreground: string, fontStyle: string }`。
>
> 前景色需要遵循[颜色格式](../references/theme-color.md#color-formats)中描述的颜色格式。不支持透明度。
>
> 下面是其他的选择器和样式示例：
>
> - `"*.declaration": { "bold": true } // 所有的声明都显示为粗体`
> - `"class:java": { "foreground": "#0f0", "italic": true } // Java 中的类`

> 如果没有规则匹配，或者主题没有 `semanticTokenColors` 部分（但启用了 `semanticHighlighting`），VS Code 会使用[语义标记作用域映射](#semantic-token-scope-map)，为给定的语义标记计算出一个 TextMate 作用域。然后用这个作用域去匹配主题 `tokenColors` 中的 TextMate 主题规则。

**一个语义标记最终显示成什么颜色（查找顺序）：**

```text
1. 主题的 semanticTokenColors 中有匹配的规则吗？    有 → 使用它
2. 没有 → 用“语义标记作用域映射”把它换算成 TextMate 作用域
         （比如 variable.readonly → variable.other.constant）
3. 用这个作用域去匹配主题的 tokenColors              匹配到 → 使用它
4. 都没有 → 保留语法高亮原来的颜色
```

这样，即使一个老主题完全不知道语义高亮的存在（只有 `tokenColors`），语义标记也能通过第 2、3 步得到合理的颜色。用户自己调整语义标记颜色的设置是 `editor.semanticTokenColorCustomizations`（见 [颜色主题](../extension-guides/color-theme.md#semantic-colors)）。

---

<a id="semantic-token-scope-map"></a>
## 语义标记作用域映射（Semantic token scope map）

> 为了让没有定义任何特定语义规则的主题也能使用语义高亮，并作为自定义标记类型和修饰符的后备方案，VS Code 维护了一份从语义标记选择器到 TextMate 作用域的映射。
>
> 如果一个主题启用了语义高亮，但没有包含给定语义标记的规则，就会改用这些 TextMate 作用域来查找 TextMate 主题规则。

<a id="predefined-textmate-scope-mappings"></a>
### 预定义的 TextMate 作用域映射（Predefined TextMate scope mappings）

> 下表列出了当前预定义的映射。

| 语义标记选择器 | 后备的 TextMate 作用域 |
| --- | --- |
| `namespace` | `entity.name.namespace` |
| `type` | `entity.name.type` |
| `type.defaultLibrary` | `support.type` |
| `struct` | `storage.type.struct` |
| `class` | `entity.name.type.class` |
| `class.defaultLibrary` | `support.class` |
| `interface` | `entity.name.type.interface` |
| `enum` | `entity.name.type.enum` |
| `function` | `entity.name.function` |
| `function.defaultLibrary` | `support.function` |
| `method` | `entity.name.function.member` |
| `macro` | `entity.name.function.preprocessor` |
| `variable` | `variable.other.readwrite`、`entity.name.variable` |
| `variable.readonly` | `variable.other.constant` |
| `variable.readonly.defaultLibrary` | `support.constant` |
| `parameter` | `variable.parameter` |
| `property` | `variable.other.property` |
| `property.readonly` | `variable.other.constant.property` |
| `enumMember` | `variable.other.enummember` |
| `event` | `variable.other.event` |

<a id="custom-textmate-scope-mappings"></a>
### 自定义的 TextMate 作用域映射（Custom TextMate scope mappings）

> 扩展可以通过它们 `package.json` 中的 `semanticTokenScopes` 贡献点扩展这份映射。
>
> 扩展这样做有两种使用场景：
>
> - 定义了自定义标记类型和标记修饰符的扩展，在主题没有为新增的语义标记类型或修饰符定义主题规则时，提供 TextMate 作用域作为后备：

```json
{
  "contributes": {
    "semanticTokenScopes": [
      {
        "scopes": {
          "templateType": [ "entity.name.type.template" ]
        }
      }
    ]
  }
}
```

> - TextMate 语法的提供者可以描述特定于语言的作用域。这对包含特定于语言的主题规则的主题有帮助。

```json
{
  "contributes": {
    "semanticTokenScopes": [
      {
        "language": "typescript",
        "scopes": {
          "property.readonly": ["variable.other.constant.property.ts"],
        }
      }
    ]
  }
}
```

两种场景：

| 场景 | 示例 | 作用 |
|---|---|---|
| 为自定义类型提供后备 | `templateType` → `entity.name.type.template` | 主题不认识 `templateType`，就按这个 TextMate 作用域上色。前面提到自定义映射不会从父类型继承，所以子类型要自己定义 |
| 为某种语言提供更具体的映射 | TypeScript 中的 `property.readonly` → `variable.other.constant.property.ts` | 有的主题专门为 `.ts` 结尾的作用域设置了颜色，换算时带上语言后缀，就能匹配到这些规则 |

---

<a id="try-it-out"></a>
## 试一试（Try it out）

> 我们有一个[语义标记示例](https://github.com/microsoft/vscode-extension-samples/tree/main/semantic-tokens-sample)，演示了如何创建一个语义标记提供者。
>
> [作用域检查器](./syntax-highlight-guide.md#scope-inspector)工具让你可以浏览一个源文件中有哪些语义标记，以及它们匹配了哪些主题规则。要查看语义标记，可以在一个 TypeScript 文件上使用内置的主题（例如 Dark+）。

---

## 本篇小结

```text
语义高亮：语言服务器根据对代码的理解提供标记分类，叠加在 TextMate 语法高亮之上（会有短暂延迟）

提供者
  legend = new SemanticTokensLegend(类型数组, 修饰符数组)
  provideDocumentSemanticTokens(document) → SemanticTokensBuilder.push(...) → build()
  registerDocumentSemanticTokensProvider(selector, provider, legend)
  可选：provideDocumentSemanticTokensEdits（增量）、DocumentRangeSemanticTokensProvider（只算可见范围）

分类 = 一个类型（class、variable、function……）+ 若干修饰符（declaration、readonly、static……）+ 可选的语言
  自定义：semanticTokenTypes（可指定 superType）、semanticTokenModifiers

启用：editor.semanticHighlighting.enabled（true / false / configuredByTheme）
      依赖语义高亮的语言可以在 configurationDefaults 中为自己的语言设为 true

主题：semanticHighlighting: true + semanticTokenColors（选择器 类型.修饰符:语言）
      没有匹配规则时 → 作用域映射换算成 TextMate 作用域 → 用 tokenColors 匹配
      扩展可以用 semanticTokenScopes 补充映射
```
