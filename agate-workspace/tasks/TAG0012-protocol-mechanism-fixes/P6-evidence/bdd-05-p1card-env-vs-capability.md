# 证据：BDD-5 — P1 卡新增 verification_env vs supplementable 边界判断指引位（RM-AG0014 主体）

验收方式：直接打开 HEAD 下的实际协议文件读新增内容，逐条核对 P1-requirements.md 该 BDD 的 Then 子句语义（非关键词存在性检查）。

## Then 子句逐项核对

- Then「存在一段边界判断指引（可用判断树或对照表形式）」：`## verification_env vs supplementable 边界判断树` 内含 ASCII 判断树 —— 满足。
- Then「『能力缺失但有替代获取路径』用 supplementable 三态」：树左枝「缺的是『agent 侧的能力』」→ 走 capability_requirements 三态，其中 supplementable 定义为「当前没有，但能通过派发子角色 / 注入 skill / 换工具补上」并要求写清补充方式，否则等同 GAP —— 语义与 Then 一致，满足。
- Then「『任务依赖特定运行环境（debug server/测试数据库/临时端口等）』用 verification_env 声明」：树右枝「缺的是『运行环境』（服务没起 / 端口没通 / 数据库没建 / 依赖没装 / 平台不支持）」→ 走 verification_env 声明 —— 举例覆盖 debug server / 数据库 / 端口，满足。
- Then「二者不互相替代」：判别口诀 +「**把环境问题标成 `supplementable` 属于机制误用**，不算『环境故障』，不消耗验证轮次预算，应立即改正声明方式」—— 明确不可互替，满足。
- Then「同一小节或紧邻位置声明『当任务涉及 verification_env 时，P1 需一并声明环境验证的轮次预算占位』」：同节末尾「**环境验证轮次预算占位声明位**」段 + `verification_env_budget:` yaml 示例 —— 位置在同一小节内，满足。
- Then「具体轮次数值由 P2 设计，P1 只要求『有声明位』」：文中给的是占位示例（默认止损轮次 = 2，与阶段 `retries[Pn]` 独立计数），并写明「数值与完整规则的权威定义在 dispatch-protocol.md「verification_env 失败处理协议」，本卡片不重写」—— 数值以引用权威节形式出现，本卡片承担的是声明位，满足。

## 实际文件文本摘录（HEAD）

### `agate/phase-cards/P1-requirements.md` L117-145

```markdown
## verification_env vs supplementable 边界判断树

`capability_requirements` 三态（available / supplementable / GAP）和 `verification_env`（运行环境声明）经常被混用——TAG0009 的 11.7 小时就是把一个环境问题错标成 `supplementable` 导致的。P1 声明时按下面的判断树走：

```
先问：缺的是能力还是环境？
├─ 缺的是「agent 侧的能力」（看不见图 / 不会用某工具 / 没有某技能）
│   └─ 走 capability_requirements 三态：
│      ├─ 当前就有 ................................. available
│      ├─ 当前没有，但能通过派发子角色 / 注入 skill / 换工具补上 ... supplementable
│      │   （必须在需求里写清补充方式，否则等同 GAP）
│      └─ 当前没有且补不上 ......................... GAP（阻塞，PAUSED 交人工）
└─ 缺的是「运行环境」（服务没起 / 端口没通 / 数据库没建 / 依赖没装 / 平台不支持）
    └─ 走 verification_env 声明（不是 supplementable）：
       ├─ 环境可由主 Agent 用标准操作准备好 → P1 声明 verification_env，
       │   由主 Agent 按 dispatch-protocol.md「环境准备职责边界」统一准备
       └─ 环境本质不可得（权限/凭据/平台原生不支持）→ 这是不可重试类，
           按 dispatch-protocol.md「verification_env 失败处理协议」立即升级人工
```

**判别口诀**：换个更强的模型/角色就能做 → 能力问题（supplementable）；换谁来做都得先把服务起起来 → 环境问题（verification_env）。**把环境问题标成 `supplementable` 属于机制误用**，不算"环境故障"，不消耗验证轮次预算，应立即改正声明方式。

**环境验证轮次预算占位声明位**：声明了 `verification_env` 的任务，P1 需求里留一行轮次预算占位（默认止损轮次 = 2 轮，与阶段 `retries[Pn]` 独立计数），供 P5/P6 派发时由主 Agent 在 dispatch-context 中接续记录"当前第几轮 + 历次已排除假设"。数值与完整规则的权威定义在 dispatch-protocol.md「verification_env 失败处理协议」，本卡片不重写：

```yaml
verification_env: "debug server http://127.0.0.1:3001 + tests/fixtures/test.db"
verification_env_budget: "止损轮次 2（独立计数，不占 retries[P5]）；轮次追踪由主 Agent 在 dispatch-context 记录"
```

```

## 结论

**PASS** —— 判断树形式的边界指引存在，能力/环境两侧定义与「不互相替代」结论明确，且同节含轮次预算占位声明位并把数值权威定义外引。
