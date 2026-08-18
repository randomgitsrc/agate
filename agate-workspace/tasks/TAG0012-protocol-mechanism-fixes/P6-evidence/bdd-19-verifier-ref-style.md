# 证据：BDD-19 — verifier.md verification_env 引用节补边界注 + 失败处理协议引用（RM-AG0014）

验收方式：直接打开 HEAD 下的实际协议文件读新增内容，逐条核对 P1-requirements.md 该 BDD 的 Then 子句语义（非关键词存在性检查）。

## Then 子句逐项核对

- Given 复核：改动前该条目全文为「若 P0-brief 声明 ui_affected=true，verification_env 字段必填（列出验收环境与生产环境的已知差异）。非 UI、无 e2e、无环境依赖的任务无需声明。」——只描述「何时需要声明」，与 dispatch-protocol.md 同段近似重复。Given 前提成立（git show 27509a2 该文件 diff 为 -1/+3 行）。
- Then「该节改为引用 dispatch-protocol.md 的权威定义（BDD-10/BDD-11）」：条目追加「条件化触发条件、失败处理协议（可重试/不可重试分类、批处理要求、止损轮次、READY 后归属判定）与**环境准备职责边界**的权威定义在 dispatch-protocol.md「verification_env 条件化」「verification_env 失败处理协议」「环境准备职责边界」**三节**——本文件只引用，不重复展开」—— 三节权威源逐一点名（含 BDD-10 的四项内容与 BDD-11 的职责边界），满足。
- Then「不重复展开失败处理协议/职责边界的完整内容」：本文件未出现可/不可重试判据表、止损轮次数值来源、READY 后三条归属判据、职责边界三条条款等完整内容；保留的只有两条**落到 verifier 身上的操作约束**——① 默认不自行启动环境，dispatch-context 没给访问方式就返回主 Agent 要；② 失败先分类再动作（可重试类在主 Agent 给定的止损轮次预算内**一次性批量**验完所有待验假设；不可重试类——权限/凭据缺失、平台本质不支持、机制误用如把环境问题标成 supplementable——立即返回主 Agent 升级人工，不消耗轮次）—— 属角色可执行动作而非规则副本，满足。
- Then「避免『权威定义 + 卡片引用』惯例被破坏（同一内容散落两处、后续改一处漏一处）」：唯一权威源在 dispatch-protocol.md（该两节头部亦自声明「本节是权威定义，P5/P6 卡片与 verifier.md 引用本节」），verifier.md / P5 卡 / P6 卡三处均为引用式 —— 单点修改可传导，满足。
- 语义一致性核对：verifier.md 保留的两条约束与 dispatch-protocol.md 权威节结论逐条一致（不自启环境 = 职责边界条款 1；批量验证 = 失败处理协议规则 2；不可重试类不消耗轮次 = 规则 1 表右列），无分叉表述。
- 关键词可 grep：条目含逐字「环境准备职责边界」，pytest 锚点 BDD-19 本轮独立实跑 PASSED。

## 实际文件文本摘录（HEAD）

### `agate/assets/execution-roles/verifier.md` L252-255

```markdown
- **verification_env 条件化**：若 P0-brief 声明 ui_affected=true，verification_env 字段必填（列出验收环境与生产环境的已知差异）。非 UI、无 e2e、无环境依赖的任务无需声明。条件化触发条件、失败处理协议（可重试/不可重试分类、批处理要求、止损轮次、READY 后归属判定）与**环境准备职责边界**的权威定义在 dispatch-protocol.md「verification_env 条件化」「verification_env 失败处理协议」「环境准备职责边界」三节——本文件只引用，不重复展开。落到你身上的两条操作约束：
  - 你**默认不自行启动环境**（debug server / 测试数据库 / 临时端口由主 Agent 统一准备并通过 dispatch-context 注入访问方式）；dispatch-context 没给访问方式就返回主 Agent 要，不要自己起一个
  - 环境验证失败时先分类再动作：可重试类在主 Agent 给定的止损轮次预算内**一次性批量**验证完所有待验假设（不要一个假设起一轮）；不可重试类（权限/凭据缺失、平台本质不支持、机制误用如把环境问题标成 supplementable）立即返回主 Agent 升级人工，不消耗轮次

```

## 结论

**PASS** —— verification_env 条目已改为引用 dispatch-protocol.md 三节权威定义，只保留两条 verifier 侧操作约束，未重复展开协议内容。
