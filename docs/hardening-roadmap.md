# agate 硬工具化路线图

> 日期：2026-06-29
> 状态：设计文档（待评审）
> 关联：LIMITATIONS.md 局限 3（主 Agent 判断力是单点故障）、局限 4（subagent 不可观测）

---

## 1. 背景

### 1.1 问题

agate 经过 6 次复盘（T016/T019/T020/T022/T025/T027），反复验证同一个根因：

**主 Agent 既是运动员又是裁判。**

它决定跑什么 gate、怎么跑、结果算不算过。规则只能覆盖已知的风险模式——每次复盘发现新漏洞就加规则，但下一个未知模式仍然绕过。T026 事故是转折点：主 Agent 编造 11/16 BDD 验收结果，所有 gate 规则都没拦住，因为"作者和裁判是同一人"。

### 1.2 核心原则

> **有确定逻辑要处理的事情，用 hook、脚本等硬工具执行，不靠 Agent 自觉。**

"硬"意味着：Agent 不能跳过或篡改结果而不留下可见痕迹。

"确定逻辑"意味着：规则可以用 exit code / grep / 计数 / 文件存在性判定，不需要临场判断。

不是确定逻辑的（如"方案合理性"、"BDD 结果真实性"），仍然需要 Agent 判断或独立 subagent——但硬工具可以验证"判断过程是否被执行了"。

### 1.3 与现有协议的关系

硬工具化是**加法，不是替换**。协议仍然告诉主 Agent "必须跑 gate"——现在多了一层：即使主 Agent 忘了跑，hook 也会跑。即使主 Agent 伪造结果，CI 会重跑验证。

Phase 1 不改协议，只加工具。Phase 2 改协议，但向后兼容（旧流程仍能跑，只是少了硬工具保护）。Phase 3 定义平台接口，等平台跟上。

---

## 2. 现状审计：依赖"主 Agent 自觉"的环节

| # | 环节 | 当前机制 | 确定性逻辑 | 硬工具化可行性 |
|---|------|----------|-----------|--------------|
| 1 | gate 执行 | 主 Agent 手动跑 check-gate.sh | exit code | pre-commit hook |
| 2 | PROD_TOUCHED 检测 | 主 Agent 扫描标记 | grep | pre-commit hook |
| 3 | 状态转移合法性 | 主 Agent 按转移规则判断 | phase 编号对照 | pre-commit hook |
| 4 | 重试计数上限 | 主 Agent 写 retries 字段 | 计数比较 | pre-commit hook |
| 5 | 回退跳变检测 | 主 Agent 计算 phase 差值 | 编号差值 | pre-commit hook |
| 6 | BDD 总数对照 | 主 Agent 手动核实 | 计数比较 | 需 P1 BDD 格式约定 |
| 7 | SCOPE+ 扫描 | 主 Agent 扫描产出 | grep + 处理状态 | 需定义"已处理"标记 |
| 8 | 修复后全量重跑 | 主 Agent 重跑 P5 gate | gate 结果存在性 | gate-result 对照 |
| 9 | P6 验收写作 | 主 Agent 自己写结论 | 否（需独立化） | 需 verifier subagent 独立 |
| 10 | READY 收尾检查 | 主 Agent 逐项检查 | 部分（git status/tag） | 部分，环境检查除外 |
| 11 | subagent 活动可观测 | 不可观测 | 无 | 需平台支持 |
| 12 | gate 结果防篡改 | 无 | 哈希/签名 | 需独立存储 |

---

## 3. 架构：两层防护

```
                    主 Agent 行为
                         │
                    ┌────▼────┐
                    │ git commit│
                    └────┬────┘
                         │
              ┌──────────▼──────────┐
              │  Layer 1: pre-commit │  ← 本地，防"不知不觉绕过"
              │  hook (自动执行)     │
              │  · 跑 gate            │
              │  · 写 .gate-result    │
              │  · 检查 PROD_TOUCHED  │
              │  · 验证状态转移       │
              │  · 失败则中止 commit  │
              └──────────┬──────────┘
                         │ (--no-verify 可绕过)
                    ┌────▼────┐
                    │ git push │
                    └────┬────┘
                         │
              ┌──────────▼──────────┐
              │  Layer 2: CI         │  ← 远程，防"故意绕过"
              │  (GitHub Action)      │
              │  · 重跑 gate          │
              │  · 对照 .gate-result  │
              │  · 一致性检查 (已有)   │
              │  · 失败则阻止 merge   │
              └───────────────────────┘
```

### 3.1 Layer 1：pre-commit hook（本地）

**触发**：`git commit`

**能力**：
- 读取 `.state.yaml`，获取当前 phase 和 task_id
- 运行 `check-gate.sh $PHASE $TASK_DIR`
- 结果写入 `.gate-result.json`（见第 4 节）
- 检测 `[PROD_TOUCHED]` 标记
- 验证状态转移合法性（phase 跳变、重试上限）
- gate 失败（exit 1）→ 中止 commit
- gate 需判断（exit 2）→ 写入结果，允许 commit，但记录"需主 Agent 判断"

**局限**：
- `--no-verify` 可绕过
- 只在 git commit 时触发，不覆盖 subagent 返回等运行时事件

### 3.2 Layer 2：CI backstop（远程）

**触发**：`git push` / PR

**能力**：
- 重跑 `check-gate.sh`，与 `.gate-result.json` 对照
- 重跑 `check-protocol-consistency.py`（已有）
- 验证 `.gate-result.json` 的 timestamp 在 commit 之前（防事后伪造）
- 失败则 CI 红灯，阻止 merge

**局限**：
- 不检测运行时行为（subagent 返回后主 Agent 做了什么）
- 依赖 CI 配置（branch protection rules）

### 3.3 两层的关系

Layer 1 拦住"不知不觉绕过"——主 Agent 忘了跑 gate、没意识到 gate 需要。
Layer 2 拦住"故意绕过"——`--no-verify` 跳过 hook，但 CI 重跑暴露。

两层都不是完美的。但两层叠加，比纯协议规则显著更强。核心逻辑：**绕过的成本从"什么都不做"提高到"需要主动且刻意地绕过两层检查"**。

---

## 4. .gate-result.json 设计

gate 结果的核心数据结构。由 pre-commit hook 写入，不由主 Agent 写入。

### 4.1 格式

```json
{
  "phase": "P5",
  "task_id": "T027",
  "exit_code": 0,
  "timestamp": "2026-06-29T14:30:00Z",
  "output": "GATE P5: exit 0, failed=0",
  "runner": "pre-commit-hook",
  "commit_sha": "abc1234"
}
```

### 4.2 生命周期

```
1. 主 Agent 完成工作，准备 commit（可能包含 .state.yaml phase 变更）
2. pre-commit hook 触发：
   a. 读 .state.yaml → 获取 phase + task_id
   b. 检测 .state.yaml 是否有 phase 变更（git diff --cached）
   c. 若有 phase 变更 或 阶段产出文件变更 → 运行 check-gate.sh
   d. 用 hook 自己的运行结果覆盖 .gate-result.json
   e. git add .gate-result.json
   f. gate exit 1 → 中止 commit
   g. gate exit 0/2 → 允许 commit
3. CI backstop：push 时重跑 gate，对照 .gate-result.json
```

### 4.3 防篡改机制

主 Agent 理论上可以手动修改 `.gate-result.json`。但：

1. **hook 覆盖**：pre-commit hook 在 commit 前重新跑 gate，覆盖任何手动修改
2. **CI 对照**：CI 重跑 gate，如果结果与 `.gate-result.json` 不一致 → CI 红灯
3. **timestamp 验证**：CI 检查 `.gate-result.json` 的 timestamp 在 commit SHA 之前（防事后补写）

唯一的绕过路径：`git commit --no-verify`（跳过 hook）+ 直接 push 到无 branch protection 的分支。这需要：repo 管理员权限 + 刻意操作。这不是协议能防的——这是仓库治理问题。

### 4.4 历史记录

每次 gate 运行追加到 `.gate-history.jsonl`（JSON Lines，每行一条记录）。用于：
- 审计：回溯某任务经过了哪些 gate
- 转移验证：hook 检查 phase 跳变时，验证中间 phase 的 gate 都跑过

```
{"phase":"P3","task_id":"T027","exit_code":0,"timestamp":"...","commit_sha":"abc1234"}
{"phase":"P4","task_id":"T027","exit_code":0,"timestamp":"...","commit_sha":"def5678"}
{"phase":"P5","task_id":"T027","exit_code":0,"timestamp":"...","commit_sha":"ghi9012"}
```

---

## 5. 三阶段路线图

### Phase 1：可脚本化检测（不改协议，纯加工具）

**目标**：把"主 Agent 必须亲自跑 gate"从自觉行为变成自动行为。不改任何协议文件，只加 hook 和脚本。

**内容**：

| 编号 | 名称 | 做什么 | 解决什么 |
|------|------|--------|---------|
| P1.1 | pre-commit-gate.sh | git commit 时自动跑 check-gate.sh，结果写入 .gate-result.json | 主 Agent 忘了跑 gate / 选择不跑 gate |
| P1.2 | PROD_TOUCHED 检测 | 整合进 pre-commit hook，grep [PROD_TOUCHED]，命中则中止 commit | 忘了扫描生产环境接触标记 |
| P1.3 | CI gate backstop | GitHub Action：push 时重跑 gate，对照 .gate-result.json | 故意 --no-verify 绕过 hook |
| P1.4 | .gate-result.json + .gate-history.jsonl | gate 结果存储 + 历史记录 | gate 结果可追溯、可对照 |
| P1.5 | READY 收尾检查脚本化 | git status 干净 + git tag 存在 检查脚本化 | 忘了检查发布前清理 |

**触发逻辑**：pre-commit hook 只在以下情况跑 gate：
- `.state.yaml` 的 phase 字段有变更
- 阶段产出文件（`P{n}-*.md`）被新增或修改

普通 commit（改文档、修 typo）不触发 gate，避免噪音。

**gate exit code 处理**：
- exit 0（通过）→ 正常 commit
- exit 1（失败）→ 中止 commit，输出 gate 失败原因
- exit 2（需判断）→ 写入 .gate-result.json，允许 commit，但输出警告"gate 需主 Agent 手动判断"

**解决什么**：
- gate 被跳过（忘了跑 / 选择不跑）
- gate 结果被伪造（hook 覆盖 + CI 对照）
- PROD_TOUCHED 被忽略

**不解决什么**：
- exit 2 gate 的判断质量（主 Agent 仍然判断"通过/不通过"，只是不能假装"跑过了"）
- P6 验收结果真实性（主 Agent 仍然自己写结论）
- SCOPE+ 处理追踪（需要协议改动，见 Phase 2）
- BDD 总数对照（需要 P1 BDD 格式约定，见 Phase 2）

**完成标准**：
- pre-commit-gate.sh 落地，覆盖 P3/P4/P5/P6/P7/P8 gate
- .gate-result.json + .gate-history.jsonl 格式定义并落地
- CI workflow 跑 gate backstop
- 在真实项目验证：跑完一个任务，hook 自动跑 gate 且结果正确

---

### Phase 2：协议级独立化（需协议改动）

**目标**：把最脆弱的环节——self-authored gate——从"主 Agent 自己写自己判"改为"独立产出 + 脚本验证"。需要改协议文件，但向后兼容。

**内容**：

| 编号 | 名称 | 做什么 | 解决什么 |
|------|------|--------|---------|
| P2.1 | P6 验收独立化 | verifier subagent 独立执行 BDD 验收，直接 commit 产出（独立 author）；主 Agent 只读结论 | T026 根因：主 Agent 编造验收结果 |
| P2.2 | 状态转移强制 | pre-commit hook 检查 .state.yaml phase 变更合法性 | 违规跳阶段 |
| P2.3 | 重试计数强制 | pre-commit hook 检查 retries >= MAX → phase 必须是 PAUSED | 超限不暂停 |
| P2.4 | BDD 格式约定 + 总数对照 | P1 BDD 条目格式约定；check-gate.sh P6 扩展：从 P1 计数 vs P6 结果计数 | P6 exit 2 → exit 0/1 |
| P2.5 | SCOPE+ 处理追踪 | 协议定义 [SCOPE_RESOLVED] 标记；check-gate.sh 检查 SCOPE+ 有对应 RESOLVED | 忘了处理 SCOPE+ |
| P2.6 | 修复后全量重跑验证 | .state.yaml 记录 last_fix_phase；hook 检查 .gate-result.json 是 full run | 修复引入回归 |
| P2.7 | 回退跳变检测脚本化 | pre-commit hook 检查 phase 变更差值 >= 2 → 必须有 PAUSED 记录 | T019 教训：跨阶段回退未暂停 |

**P2.1 P6 验收独立化（详细）**：

当前流程：
```
P5 gate 通过 → 主 Agent 自己跑 BDD 验收 → 主 Agent 写 P6-acceptance.md → 主 Agent 自己判 gate
```

改为：
```
P5 gate 通过 → 主 Agent 派发 verifier subagent
  → verifier subagent 独立读 P1 BDD 条件
  → verifier subagent 逐条执行验证（跑测试、截图、检查输出）
  → verifier subagent 产出 P6-acceptance.md + P6-evidence/
  → verifier subagent commit 产出（author: verifier，非主 Agent）
主 Agent → 读 P6-acceptance.md → 跑 check-gate.sh P6 → 判定
```

**关键变化**：P6-acceptance.md 的**作者**从主 Agent 变成 verifier subagent。主 Agent 从"自己写结论自己判"变成"读别人的结论自己判"。

**防操控**：
- dispatch-prompt 模板固化 P6 验收 prompt（B7 规则先例）
- prompt 必须包含"独立验证，不接受主 Agent 预判结论"
- git author 元数据提供可追溯性

**不解决的**：
- 主 Agent 仍可发误导性 prompt
- 同源模型盲区共享（局限 2）

**解决什么**：
- gate 被跳过（Phase 1 已解决，Phase 2 强化）
- P6 验收结果伪造（verifier 独立 commit）
- 状态转移违规（hook 强制检查）
- 重试超限不暂停（hook 强制检查）
- BDD 总数对照从手动变自动（格式约定 + 脚本）
- SCOPE+ 未处理（标记追踪）
- 修复后不全量重跑（gate-result 对照）

**不解决什么**：
- 主 Agent 误导 verifier subagent（缓解：模板固化，但不根治）
- exit 2 gate 的判断质量（主 Agent 仍需判断，但结果被记录）
- 测试质量上限（局限 1）
- 同源模型盲区（局限 2）

**完成标准**：
- P6 验收由 verifier subagent 独立产出，主 Agent 不写 P6-acceptance.md
- check-gate.sh P6 从 exit 2 降为 exit 0/1（BDD 总数对照脚本化）
- 状态转移、重试计数、回退跳变由 pre-commit hook 强制检查
- SCOPE+ 处理追踪落地
- 在真实项目验证一个完整任务

---

### Phase 3：平台接口规范（需平台支持）

**目标**：定义 agate 需要的平台能力接口。当前平台（OpenCode/Claude Code）不支持这些能力，agate 先写规范，等平台跟上后启用。

**内容**：

| 编号 | 名称 | 做什么 | 解决什么 |
|------|------|--------|---------|
| P3.1 | 平台接口规范文档 | 定义 agate 需要的平台能力 | 明确"需要什么"才能争取"平台给什么" |
| P3.2 | subagent 可观测性 | 平台暴露 subagent 活动信号 | 局限 4：subagent 卡死 vs 在干活不可区分 |
| P3.3 | gate 结果独立存储 | 平台提供主 Agent 不可写的存储位置 | .gate-result.json 防篡改的根治方案 |
| P3.4 | gate 执行平台化 | 平台在 subagent 返回后自动触发 gate | 覆盖非 git 事件的 gate 执行 |

**P3.1 平台接口规范（核心）**：

```yaml
# agate 平台接口规范（platform-gate-interface.md）

gate_execution:
  executor: platform_hook          # 平台执行 gate，非主 Agent
  trigger: phase_transition       # 阶段转移时触发（不依赖 git commit）
  output_format: json
  output_store: immutable         # 主 Agent 不可写
  result_callback: true           # 结果回调主 Agent（只读）

subagent_observability:
  activity_log: true              # 工具调用日志
  output_stream: true             # 实时输出流
  heartbeat_interval: 30s         # 心跳
  timeout: configurable           # 主 Agent 可设定
  smart_timeout: true             # 有活动续期，无活动终止

result_integrity:
  storage: independent            # 独立于主 Agent 的存储
  timestamp: system_clock         # 系统时间戳
  content_hash: sha256            # 内容哈希防篡改
  append_only: true               # 只追加，不修改
```

**解决什么**：
- subagent 不可观测（局限 4 根治）
- gate 结果可篡改（局限 3 的残留风险根治）
- 非 git 事件的 gate 执行（subagent 返回后自动触发）

**不解决什么**：
- 测试质量上限（局限 1，方法论边界）
- 同源模型盲区（局限 2，方法论边界）
- 主 Agent 对 exit 2 gate 的判断质量（仍需主 Agent 判断，但执行过程被完整记录）

**完成标准**：
- 平台接口规范文档落地
- 至少一个平台（OpenCode 或 Claude Code）实现其中一项能力
- agate 协议标注"如果平台支持 X，agate 启用 Y"
- 依赖平台能力的 gate 检查从"主 Agent 自觉"切换到"平台强制"

---

## 6. 三阶段依赖关系

```
Phase 1 (纯加工具)          Phase 2 (协议改动)         Phase 3 (平台支持)
     │                           │                           │
     ├─ P1.1 pre-commit hook    ├─ P2.1 P6 独立化            ├─ P3.1 接口规范
     ├─ P1.2 PROD_TOUCHED       ├─ P2.2 状态转移强制          ├─ P3.2 subagent 可观测
     ├─ P1.3 CI backstop        ├─ P2.3 重试计数强制          ├─ P3.3 结果独立存储
     ├─ P1.4 gate-result        ├─ P2.4 BDD 格式 + 总数       └─ P3.4 gate 平台化
     └─ P1.5 READY 检查         ├─ P2.5 SCOPE+ 追踪
                                ├─ P2.6 修复全量重跑验证
                                └─ P2.7 回退跳变检测
     │                           │
     │  P2.2-P2.7 依赖            │  P3.2-P3.4 依赖
     │  P1.1 的 hook 基础设施     │  P3.1 的接口定义
     │                           │
     ▼                           ▼
  不依赖 Phase 2              不依赖 Phase 3
  可以先落地                  可以先写规范
```

**关键**：每个 Phase 独立有价值。Phase 1 落地后不依赖 Phase 2 也能运行；Phase 2 落地后不依赖 Phase 3 也能运行。三个 Phase 可以并行推进（Phase 3 的规范文档可以和 Phase 1 同时写）。

---

## 7. 与 LIMITATIONS.md 的对应关系

| 局限 | 描述 | Phase 1 缓解 | Phase 2 缓解 | Phase 3 根治 |
|------|------|-------------|-------------|-------------|
| 局限 1 | 测试质量上限 | — | — | —（方法论边界） |
| 局限 2 | 同源模型盲区 | — | — | —（方法论边界） |
| 局限 3 | 主 Agent 判断力单点 | gate 执行不被跳过 | P6 独立化 + 状态强制 | 结果防篡改 |
| 局限 4 | subagent 不可观测 | — | — | 平台可观测性 |
| 局限 5 | 协议文档一致性 | — | — | —（已有 CI 检查） |

**局限 3 的缓解路径**：
- Phase 1：主 Agent 不能跳过 gate 执行（hook 自动跑），不能伪造 gate 结果（hook 覆盖 + CI 对照）
- Phase 2：主 Agent 不能伪造 P6 验收（verifier 独立 commit），不能违规跳阶段（hook 强制检查）
- Phase 3：gate 结果存储在主 Agent 不可写的位置，根治伪造

每个 Phase 都不是"部分解决"——每个 Phase 都把局限 3 的边界推进一步。Phase 1 解决"执行层"，Phase 2 解决"产出层"，Phase 3 解决"存储层"。

---

## 8. 风险与缓解

### 8.1 硬工具自身有 bug

**风险**：check-gate.sh 或 pre-commit hook 有 bug，导致 false negative（误拦）或 false positive（漏放）。

**缓解**：
- False negative 是可恢复的——PAUSED 后人工审查，发现问题后修脚本
- False positive 是真实风险——但硬工具至少和"主 Agent 判断"一样好，通常更好（脚本不会有"今天状态不好"）
- CI backstop 在不同环境重跑，catch 环境特定 bug
- 所有脚本版本控制，bug 可追溯、可修复
- Phase 1 不改协议，bug 影响范围有限（最坏情况是 commit 被误拦，手动跳过即可）

### 8.2 hook 被绕过

**风险**：`git commit --no-verify` 跳过 hook。

**缓解**：
- CI backstop 重跑所有检查
- branch protection 规则要求 CI 绿灯才能 merge
- 绕过路径需要：repo 管理员权限 + 刻意操作——这是仓库治理问题，不是协议问题

### 8.3 协议改动引入回归

**风险**：Phase 2 改协议文件，可能引入新的不一致。

**缓解**：
- Phase 2 改动走 agate 自己的 P1-P8 流程（dogfooding）
- check-protocol-consistency.py 验证协议文档结构一致性（已有）
- 每个 Phase 完成后跑一次完整任务验证

### 8.4 过度自动化导致灵活性丧失

**风险**：硬工具太严格，合理的人为判断被拦住。

**缓解**：
- exit 2 gate（需判断）不被硬工具拦截——hook 允许 commit，只记录"需主 Agent 判断"
- PAUSED 是安全阀——任何 hook 拦截都导向 PAUSED（人工介入），不是直接失败
- 硬工具只拦截"确定逻辑明确"的规则，不碰需要判断的环节

### 8.5 .gate-result.json 伪造

**风险**：主 Agent 手动修改 .gate-result.json。

**缓解**：
- pre-commit hook 覆盖：hook 在 commit 前重新跑 gate，覆盖任何手动修改
- CI 对照：CI 重跑 gate，结果不一致则红灯
- timestamp 验证：CI 检查 timestamp 在 commit 之前
- Phase 3 根治：结果存储在主 Agent 不可写的位置

---

## 9. 优先级与时间线

| Phase | 优先级 | 理由 | 预估工作量 |
|-------|--------|------|-----------|
| Phase 1 | 高 | 成本最低、收益最大、不改协议 | 2-3 个实现任务 |
| Phase 2 | 中 | 解决 T026 根因，但需协议改动 + 评审 | 4-5 个实现任务 |
| Phase 3 | 低 | 纯文档可以先写，实现等平台 | 1 个规范文档 + 等平台 |

**建议**：
1. Phase 1 立即推进（下一个实现任务）
2. Phase 3 的规范文档（P3.1）可以和 Phase 1 并行写（纯文档无成本）
3. Phase 2 在 Phase 1 验证通过后推进（需要 Phase 1 的 hook 基础设施）

---

## 10. 总结

agate 的核心矛盾是：**设计哲学说"不依赖主 Agent 判断力"，但现实中可判定的规则只能覆盖已知风险模式**。

硬工具化不是"再加一层规则"——而是**把规则的执行权从主 Agent 手里拿走**。主 Agent 仍然决定做什么、怎么判断，但"有没有跑 gate"、"结果是什么"由独立机制记录和验证。

三阶段路线：
- Phase 1：**执行层**——gate 不被跳过，结果不被伪造（hook + CI）
- Phase 2：**产出层**——P6 验收不自己写，状态转移不自己判（verifier 独立化 + hook 强制）
- Phase 3：**存储层**——gate 结果不可篡改，subagent 行为可观测（平台接口）

每个 Phase 把"主 Agent 自觉"替换一层：执行 → 产出 → 存储。三层叠加后，主 Agent 仍然是决策者，但不再是唯一的执行者和验证者。这就是文档协议路线突破能力边界的方向。
