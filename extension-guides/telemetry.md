# 遥测：扩展作者指南（Telemetry extension authors guide）

> 原文：[Telemetry extension authors guide](https://code.visualstudio.com/api/extension-guides/telemetry)
> 源文件：`microsoft/vscode-docs` → `api/extension-guides/telemetry.md`（DateApproved: 10/7/2026）

> VS Code 会收集使用数据并发送给微软，以帮助改进我们的产品和服务。请阅读我们的[隐私声明](https://go.microsoft.com/fwlink/?LinkID=528096&clcid=0x409)和[遥测文档](https://code.visualstudio.com/docs/getstarted/telemetry)了解更多信息。
>
> 本主题为扩展作者提供了一些指导，让他们的扩展能够符合 VS Code 的遥测要求和最佳实践。
>
> **注意**：如果你不想向微软发送使用数据，可以把用户[设置](https://code.visualstudio.com/docs/configure/settings) `telemetry.telemetryLevel` 设为 `off`。

**遥测（telemetry）是什么？** 就是软件自动收集使用情况的数据（比如“某个功能被用了多少次”“发生了哪些错误”），发送给开发者，用来了解用户如何使用产品、发现问题。

**为什么要有专门的规范？** 遥测涉及用户隐私。如果每个扩展各自为政，有的在用户关闭遥测后仍然偷偷上报，用户就无法控制自己的数据。所以 VS Code 要求：**所有扩展都必须尊重用户在 VS Code 中的统一遥测设置**。这是本篇最核心的一条规则。

---

<a id="telemetry-module"></a>
## 遥测模块（Telemetry module）

> VS Code 团队维护着 [@vscode/extension-telemetry](https://www.npmjs.com/package/@vscode/extension-telemetry) 这个 npm 模块，它提供了在 VS Code 中收集遥测数据的一致且安全的方式。这个模块把遥测数据上报到 [Azure Monitor 和 Application Insights](https://azure.microsoft.com/services/monitor/)，并保证对以前版本的 VS Code 向后兼容。
>
> 按照这份指南设置 [Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/app/nodejs)，并获取你的 Application Insights 检测密钥（instrumentation key）。

**Application Insights** 是微软 Azure 云上的应用监控服务，可以接收、存储和分析遥测数据。使用这个模块的好处是：它已经内置了对用户遥测设置的检查，用户关闭遥测后，它会自动停止发送，不需要你自己处理。

基本用法如下（以该模块的文档为准，不同版本的构造参数可能有变化）：

```ts
import TelemetryReporter from '@vscode/extension-telemetry';

let reporter: TelemetryReporter;

export function activate(context: vscode.ExtensionContext) {
  // 参数是 Application Insights 的连接字符串
  reporter = new TelemetryReporter('<你的连接字符串>');
  context.subscriptions.push(reporter);

  // 上报一个事件，可以附带属性和数值
  reporter.sendTelemetryEvent('commandExecuted', { command: 'sayHello' }, { durationMs: 12 });
}
```

---

<a id="without-the-telemetry-module"></a>
## 不使用遥测模块（Without the telemetry module）

> 不想使用 Application Insights 的扩展作者，可以用自己的自定义方案发送遥测数据。在这种情况下，扩展作者仍然必须使用 `isTelemetryEnabled` 和 `onDidChangeTelemetryEnabled` API 来尊重用户的选择。这样，用户就能在一个集中的地方控制他们的遥测设置。

这两个 API 都在 `vscode.env` 命名空间下：

| API | 类型 | 作用 |
|---|---|---|
| `vscode.env.isTelemetryEnabled` | `boolean` | 用户当前是否允许遥测 |
| `vscode.env.onDidChangeTelemetryEnabled` | `Event<boolean>` | 用户修改了遥测设置时触发 |

```ts
function sendTelemetry(eventName: string) {
  if (!vscode.env.isTelemetryEnabled) {
    return;   // 用户关闭了遥测：什么都不发
  }
  // ……发送到你自己的服务器……
}

context.subscriptions.push(
  vscode.env.onDidChangeTelemetryEnabled(enabled => {
    if (!enabled) {
      // 用户刚刚关闭了遥测：停止发送，清空尚未发送的缓存数据
    }
  })
);
```

VS Code 的 API 中还提供了 `vscode.env.createTelemetryLogger`，它会自动检查遥测设置，你只需实现“如何发送数据”的部分（一个 `TelemetrySender`）。自己实现遥测方案时，可以优先考虑用它。

---

<a id="custom-telemetry-setting"></a>
## 自定义遥测设置（Custom telemetry setting）

> 扩展可能希望让用户独立于 VS Code 的遥测，单独控制扩展专属的遥测。这种情况下，我们建议你引入一个专门的扩展设置。建议给自定义的遥测设置加上 `telemetry` 和 `usesOnlineServices` 标签，这样用户在设置界面中查找起来会更容易。添加自定义遥测设置，并不能免除尊重用户决定的义务，必须始终遵守 `isTelemetryEnabled` 和 `onDidChangeTelemetryEnabled` 标志。如果 `isTelemetryEnabled` 报告为 false，即使你的设置是启用的，也绝不能发送遥测数据。

给设置项加标签的写法（见 [通用能力](../extension-capabilities/common-capabilities.md#configuration) 中的配置）：

```json
"contributes": {
  "configuration": {
    "properties": {
      "myExtension.telemetry.enabled": {
        "type": "boolean",
        "default": true,
        "description": "是否发送本扩展的使用数据",
        "tags": ["telemetry", "usesOnlineServices"]
      }
    }
  }
}
```

用户在设置页面中搜索 `@tag:telemetry`，就能找到所有扩展的遥测设置。

**两个开关的关系：只有两者都允许时，才能发送。**

| VS Code 遥测（`isTelemetryEnabled`） | 扩展自己的设置 | 能否发送 |
|---|---|---|
| 开 | 开 | 能 |
| 开 | 关 | 不能 |
| 关 | 开 | **不能** |
| 关 | 关 | 不能 |

扩展自己的设置只能让遥测**更少**，不能绕过用户在 VS Code 中的总开关。

---

<a id="telemetry.json"></a>
## telemetry.json

> 我们理解遥测对很多用户来说是一个敏感的话题，我们的目标是尽可能地透明。VS Code 核心产品和大多数第一方扩展的根目录中都附带了一个 `telemetry.json` 文件。这让用户可以使用带 `--telemetry` 参数的 VS Code 命令行，获取 VS Code 产生的所有遥测数据的清单。扩展作者也可以在扩展的根目录中放一个 `telemetry.json` 文件，它同样会出现在命令行输出的清单中。

用户在终端中执行 `code --telemetry`，就能看到 VS Code 以及这些扩展声明会收集哪些遥测事件和字段。在你的扩展中提供 `telemetry.json`，是向用户公开“我收集了什么”的一种方式。

---

<a id="dos-and-donts"></a>
## 应该做和不应该做的（Do's and Don'ts）

> ✔️ 应该做
>
> - 如果使用 Application Insights 对你来说可行，就使用 [@vscode/extension-telemetry](https://www.npmjs.com/package/@vscode/extension-telemetry) npm 模块。
> - 否则，遵守 `isTelemetryEnabled` 和 `onDidChangeTelemetryEnabled` API。
> - 如果有自定义的遥测设置，给它加上 `telemetry` 和 `usesOnlineServices` 标签。
> - 尽可能少地收集遥测数据。
> - 尽可能向用户公开你收集了什么。
>
> ❌ 不应该做
>
> - 引入一个不征求用户同意的自定义遥测收集方案。
> - 收集个人身份信息（PII）。
> - 收集超出必要范围的遥测数据。
> - 只依据 `telemetry.telemetryLevel` 设置来判断，因为与 `isTelemetryEnabled` 相比，它有时可能是不准确的。

**个人身份信息（PII，Personally Identifiable Information）**是指能识别出具体某个人的信息，比如用户名、邮箱、IP 地址、文件路径（路径中常常包含用户名，如 `C:\Users\张三\...`）、文件内容。上报错误信息时尤其要注意，错误堆栈中经常带有本地文件路径，发送前要做清理。

**为什么不能只看 `telemetry.telemetryLevel`？** 除了这个设置，遥测还可能被其他方式关闭，比如启动 VS Code 时带了 `--disable-telemetry` 参数，或者企业策略统一禁用了遥测。`isTelemetryEnabled` 综合考虑了所有这些情况，所以只有它是准确的。

---

## 本篇小结

| 原则 | 做法 |
|---|---|
| 尊重用户的统一设置 | 发送前检查 `vscode.env.isTelemetryEnabled`，监听 `onDidChangeTelemetryEnabled` |
| 优先使用官方方案 | `@vscode/extension-telemetry`（自动遵守设置），或 `vscode.env.createTelemetryLogger` |
| 扩展自己的开关 | 加 `telemetry`、`usesOnlineServices` 标签；只能更严格，不能绕过总开关 |
| 透明 | 在扩展根目录提供 `telemetry.json` |
| 最小化 | 只收集必要的数据，绝不收集 PII（注意错误堆栈中的文件路径） |
| 不要 | 只依据 `telemetry.telemetryLevel` 判断 |
