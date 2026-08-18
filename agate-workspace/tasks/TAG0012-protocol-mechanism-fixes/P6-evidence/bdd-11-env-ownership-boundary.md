# 证据：BDD-11 — verification_env 节新增「环境准备职责边界」子节（RM-AG0014 补充）

验收方式：直接打开 HEAD 下的实际协议文件读新增内容，逐条核对 P1-requirements.md 该 BDD 的 Then 子句语义（非关键词存在性检查）。

## Then 子句逐项核对

- Then「节内新增子节」：`**环境准备职责边界**（本节是权威定义，P5 卡片「按包拆分并行」/ P6 卡片 / verifier.md 均引用本节，不重复展开）` 位于 verification_env 节内、失败处理协议之后 —— 满足。
- Then 条款 1「环境的启动/维护/关停默认归主 Agent（或 P0-brief 显式声明的单一责任方），subagent 默认只消费不自行启动」：条款 1 逐字覆盖「**启动 / 维护 / 关停默认归主 Agent**（或 P0-brief 显式声明的单一责任方）；subagent 默认只消费环境，不自行启动」—— 三个动作（启动/维护/关停）与「单一责任方」例外都在，满足。
- Then 条款 2「多个并行 subagent 需要访问同一环境时，由主 Agent 统一启动后通过 dispatch-context 注入访问方式，不允许各 subagent 各自启动导致冲突/资源竞争」：条款 2 逐字覆盖，并具体化注入内容（URL / 端口 / 数据路径）与后果（端口占用、数据库锁、资源竞争）—— 满足。
- Then「该子节与 `.state.yaml` 的 `env_state` 字段（state-machine.md 已有定义）建立引用关系，不重复定义 env_state 的字段语法」：条款 3 写「本节与 `.state.yaml` 的 `env_state` 字段（`debug_backend` / `test_entry_slug` / `env_verified_at`）是引用关系：字段语法与一致性验证步骤的权威定义在 state-machine.md「主 Agent 的单步执行（一轮）」的环境一致性验证步骤，本节**不重复定义**字段语法」—— 建立了引用关系；仅列出三个字段名作为指代（未展开各字段取值语法/校验规则），符合「不重复定义字段语法」。
- 引用目标存在性核实：state-machine.md 确含 `env_state` 定义与「主 Agent 的单步执行（一轮）」节（见下方摘录），引用非悬空。
- 格式风险核对：引用用节标题而非 `xxx.md L123`，符合 CHECK3。

## 实际文件文本摘录（HEAD）

### `agate/dispatch-protocol.md` L1022-1027

```markdown
**环境准备职责边界**（本节是权威定义，P5 卡片「按包拆分并行」/ P6 卡片 / verifier.md 均引用本节，不重复展开）：

1. 环境的**启动 / 维护 / 关停默认归主 Agent**（或 P0-brief 显式声明的单一责任方）；subagent 默认只消费环境，不自行启动
2. 多个并行 subagent 需要访问同一环境时，由主 Agent 统一启动后通过 dispatch-context 注入访问方式（URL / 端口 / 数据路径），不允许各 subagent 各自启动——否则端口占用、数据库锁、资源竞争
3. 本节与 `.state.yaml` 的 `env_state` 字段（`debug_backend` / `test_entry_slug` / `env_verified_at`）是引用关系：字段语法与一致性验证步骤的权威定义在 state-machine.md「主 Agent 的单步执行（一轮）」的环境一致性验证步骤，本节**不重复定义**字段语法

```

### `agate/state-machine.md` L318-325

```markdown
       若 .state.yaml 含 `env_state:` 块（运行时环境状态，如 debug backend URL、test entry ID、端口等）：
       - 验证这些状态在当前环境中仍有效（具体检查方式由项目自定，如 curl health check、查询 entry 是否存在）
       - 若任一失效：重新创建对应资源，更新 .state.yaml 的 env_state，commit 修订
       - 若环境全部失效 → PAUSED 报告人工

       注意：此步骤只适用于 .state.yaml 显式记录了 env_state 的任务。
       无 env_state 的任务跳过此步骤。
    2. 若当前阶段 == P0：主 Agent 亲自写 P0-brief.md（见 dispatch-protocol.md 步骤0），完成后继续
```

## 结论

**PASS** —— 职责边界子节存在，两条职责条款完整，且与 state-machine.md 的 env_state 建立引用关系而非重复定义字段语法。
