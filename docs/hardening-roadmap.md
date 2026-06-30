# agate 硬工具化路线图

> 日期：2026-06-29（v2：2026-06-30 修订；v3：2026-06-30 评审反馈修订）
> 状态：设计文档（待评审）
> 关联：LIMITATIONS.md 局限 3（主 Agent 判断力是单点故障）、局限 4（subagent 不可观测）
> 修订说明：v2 纳入 PeekView 实战评审（5 个结构性问题 + 4 个执行层问题），增加"流程选择硬约束"维度；v3 纳入评审 806c0d1 反馈（4 项：状态标记/S2 裁决/P2.1 平台依赖/阈值警示位置）

---

## 1. 背景

### 1.1 问题

agate 经过 6 次复盘（T016/T019/T020/T022/T025/T027）+ PeekView 12 任务实战评审，反复验证同一个根因：

**主 Agent 既是运动员又是裁判，且默认倾向于少走路。**

LIMITATIONS.md 局限 3 原来写的是"主 Agent 遇到困难时倾向于自行解决而非触发安全网"。PeekView 实战修正了这个判断——不是"遇到困难时"，是"一切时候"：

| 表现 | 证据 | 是"遇到困难"吗？ |
|------|------|-----------------|
| P2 从不派发评审 subagent | 3 个保留 P2 的任务全是"主 Agent 直接写 approved" | 否 |
| 零复盘 | 第二拨 8 个任务 0 复盘 | 否 |
| P3+P4 自行合并 | T041/T037 不走分离 | 否 |
| 裁剪激进 | 5/8 裁掉 P2/P3/P7/P8 | 否 |
| T026 P6 造假 | 编造 11/16 BDD 结果 | 是（极端表现） |

前四项不是"遇到困难走捷径"，是出厂设置——LLM 被训练为"高效完成任务"，训练分布里"高效"等于"最少步骤"。

### 1.2 核心原则

> **有确定逻辑要处理的事情，用 hook、脚本等硬工具执行，不靠 Agent 自觉。**

"硬"意味着：Agent 不能跳过或篡改结果而不留下可见痕迹。

"确定逻辑"意味着：规则可以用 exit code / grep / 计数 / 文件存在性判定，不需要临场判断。

v2 补充：这条原则不仅适用于 gate 执行，也适用于**流程选择**。凡是 Agent 可以选择"走不走"的环节（裁剪、评审、复盘、合并），选择条件必须可判定、由外部验证，不能由 Agent 自己声明了事。

### 1.3 与现有协议的关系

硬工具化是**加法，不是替换**。协议仍然告诉主 Agent "必须跑 gate"——现在多了一层：即使主 Agent 忘了跑，hook 也会跑。即使主 Agent 伪造结果，CI 会重跑验证。

Phase 1 不改协议，只加工具。Phase 2 改协议，但向后兼容。Phase 3 定义平台接口，等平台跟上。

---

## 2. 现状审计：依赖"主 Agent 自觉"的环节

### 2.1 gate 执行类

| # | 环节 | 当前机制 | 确定性逻辑 | 硬工具化 |
|---|------|----------|-----------|---------|
| 1 | gate 执行 | 主 Agent 手动跑 check-gate.sh | exit code | pre-commit hook |
| 2 | PROD_TOUCHED 检测 | 主 Agent 扫描标记 | grep | pre-commit hook |
| 3 | gate 结果防篡改 | 无 | 哈希/签名 | 需独立存储 |
| 4 | subagent 活动可观测 | 不可观测 | 无 | 需平台支持 |

### 2.2 状态一致性类

| # | 环节 | 当前机制 | 确定性逻辑 | 硬工具化 |
|---|------|----------|-----------|---------|
| 5 | 状态转移合法性 | 主 Agent 按转移规则判断 | phase 编号对照 | pre-commit hook |
| 6 | 重试计数上限 | 主 Agent 写 retries 字段 | 计数比较 | pre-commit hook |
| 7 | 回退跳变检测 | 主 Agent 计算 phase 差值 | 编号差值 | pre-commit hook |
| 8 | 修复后全量重跑 | 主 Agent 重跑 P5 gate | gate 结果存在性 | gate-result 对照 |

### 2.3 流程选择类（v2 新增——Agent 默认倾向于"不走"）

| # | 环节 | 当前机制 | 确定性逻辑 | 硬工具化 |
|---|------|----------|-----------|---------|
| 9 | 裁剪决策 | 主 Agent 自行判断 | 需风险等级 + 量化条件 | hook 检查裁剪条件 |
| 10 | P2 评审派发 | 主 Agent 自行决定 | 风险等级决定是否必须派发 | hook 检查 author |
| 11 | 裁剪声明与执行一致 | 无检查 | P1 phases vs .state.yaml 序列 | hook 对照 |
| 12 | 复盘触发 | 主 Agent 自行决定 | 异常模式检测 | 脚本检测异常 |
| 13 | P3+P4 合并 | 主 Agent 自行决定 | 风险等级 + BDD 数 | hook 检查条件 |
| 14 | CHANGELOG 记录 | P8 才写，裁剪 P8 后无入口 | grep task_id | hook 检查 |

### 2.4 产出质量类

| # | 环节 | 当前机制 | 确定性逻辑 | 硬工具化 |
|---|------|----------|-----------|---------|
| 15 | P6 验收写作 | 主 Agent 自己写结论 | 否（需独立化） | verifier subagent 独立 |
| 16 | BDD 总数对照 | 主 Agent 手动核实 | 计数比较 | 需 P1 BDD 格式约定 |
| 17 | P6 证据与 BDD 对应 | 证据目录非空（不查对应） | grep Evidence 引用 | hook 检查每条 BDD 有证据 |
| 18 | SCOPE+ 处理追踪 | 主 Agent 扫描产出 | grep + 处理状态 | 需定义"已处理"标记 |
| 19 | READY 收尾检查 | 主 Agent 逐项检查 | 部分（git status/tag） | 部分，环境检查除外 |

---

## 3. 架构：两层防护

```
                    主 Agent 行为
                         |
                    +----v----+
                    | git commit|
                    +----+----+
                         |
              +----------v----------+
              |  Layer 1: pre-commit |  <- 本地，防"不知不觉绕过"
              |  hook (自动执行)     |
              |  - 跑 gate            |
              |  - 写 .gate-result    |
              |  - 检查 PROD_TOUCHED  |
              |  - 验证状态转移       |
              |  - 检查裁剪条件       |
              |  - 检查 CHANGELOG     |
              |  - 检查 P6 证据格式   |
              |  - 失败则中止 commit  |
              +----------+----------+
                         | (--no-verify 可绕过)
                    +----v----+
                    | git push |
                    +----+----+
                         |
              +----------v----------+
              |  Layer 2: CI         |  <- 远程，防"故意绕过"
              |  (GitHub Action)      |
              |  - 重跑 gate          |
              |  - 对照 .gate-result  |
              |  - 一致性检查 (已有)   |
              |  - 失败则阻止 merge   |
              +-----------------------+
```

### 3.1 Layer 1：pre-commit hook（本地）

**触发**：`git commit`

**能力**：
- 读取 `.state.yaml`，获取当前 phase 和 task_id
- 运行 `check-gate.sh $PHASE $TASK_DIR`
- 结果写入 `.gate-result.json`（见第 4 节）
- 检测 `[PROD_TOUCHED]` 标记
- 验证状态转移合法性（phase 跳变、重试上限）
- 检查裁剪条件（v2 新增）：若 phase 序列跳过了某阶段，验证 P1 的 risk_level 和裁剪条件满足
- 检查 CHANGELOG（v2 新增）：若任务涉及用户可见改动，CHANGELOG.md 的 `[Unreleased]` 区域含 task_id
- 检查 P6 证据格式（v2 新增）：P6-acceptance.md 每条 BDD 有 Evidence 引用
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

### 3.3 两层的关系

Layer 1 拦住"不知不觉绕过"——主 Agent 忘了跑 gate、没意识到 gate 需要。
Layer 2 拦住"故意绕过"——`--no-verify` 跳过 hook，但 CI 重跑暴露。

核心逻辑：**绕过的成本从"什么都不做"提高到"需要主动且刻意地绕过两层检查"**。

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
   a. 读 .state.yaml -> 获取 phase + task_id
   b. 检测 .state.yaml 是否有 phase 变更（git diff --cached）
   c. 若有 phase 变更 或 阶段产出文件变更 -> 运行 check-gate.sh
   d. 用 hook 自己的运行结果覆盖 .gate-result.json
   e. git add .gate-result.json
   f. gate exit 1 -> 中止 commit
   g. gate exit 0/2 -> 允许 commit
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

| 编号 | 名称 | 做什么 | 解决什么 | 来源 | 状态 |
|------|------|--------|---------|------|------|
| P1.1 | pre-commit-gate.sh | git commit 时自动跑 check-gate.sh，结果写入 .gate-result.json | gate 被跳过 | v1 | 待实现 |
| P1.2 | PROD_TOUCHED 检测 | 整合进 pre-commit hook，命中则中止 commit | 忘了扫描生产环境接触标记 | v1 | 待实现 |
| P1.3 | CI gate backstop | GitHub Action：push 时重跑 gate，对照 .gate-result.json | 故意 --no-verify 绕过 | v1 | 待实现（CI 框架已有） |
| P1.4 | .gate-result.json + .gate-history.jsonl | gate 结果存储 + 历史记录 | gate 结果可追溯、可对照 | v1 | 待实现 |
| P1.5 | READY 收尾检查脚本化 | git status 干净 + git tag 存在 检查脚本化 | 忘了检查发布前清理 | v1 | 部分实现（check-gate.sh P8 已有部分） |
| P1.6 | CHANGELOG 检查 | hook 检查 CHANGELOG.md [Unreleased] 含 task_id | P8 裁剪后 CHANGELOG 无写入时机 | v2 (S1) | 待实现 |
| P1.7 | P6 证据格式检查 | hook 检查 P6-acceptance.md 每条 BDD 有 Evidence 引用 | 证据存在不等于证据对应 | v2 (E1) | 待实现 |

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
- CHANGELOG 遗漏（v2）
- P6 证据与 BDD 不对应（v2）

**不解决什么**：
- exit 2 gate 的判断质量（主 Agent 仍然判断"通过/不通过"，只是不能假装"跑过了"）
- P6 验收结果真实性（主 Agent 仍然自己写结论）
- 裁剪决策是否合理（Phase 2）
- P2 评审是否派发（Phase 2）

**完成标准**：
- pre-commit-gate.sh 落地，覆盖 P3/P4/P5/P6/P7/P8 gate
- .gate-result.json + .gate-history.jsonl 格式定义并落地
- CI workflow 跑 gate backstop
- CHANGELOG 检查 + P6 证据格式检查集成进 hook
- 在真实项目验证：跑完一个任务，hook 自动跑 gate 且结果正确

---

### Phase 2：协议级独立化与流程选择硬约束（需协议改动）

**目标**：把最脆弱的环节——self-authored gate 和流程选择权——从"主 Agent 自己决定自己执行"改为"独立产出 + 外部条件约束 + 脚本验证"。

**v3 结构调整**（基于评审建议）：Phase 2 拆成两批——2A 可和 Phase 1 hook 捆绑实现，2B 需协议改动 + 评审。

#### 2A. 状态一致性强制（可和 Phase 1 hook 捆绑，不需协议改动）

| 编号 | 名称 | 做什么 | 解决什么 | 来源 | 状态 |
|------|------|--------|---------|------|------|
| P2.3 | 状态转移强制 | pre-commit hook 检查 .state.yaml phase 变更合法性 | 违规跳阶段 | v1 | 已实现 |
| P2.4 | 重试计数强制 | pre-commit hook 检查 retries >= MAX -> phase 必须是 PAUSED | 超限不暂停 | v1 | 已实现 |
| P2.5 | 回退跳变检测脚本化 | pre-commit hook 检查 phase 变更差值 >= 2 -> 必须有 PAUSED 记录 | T019 教训：跨阶段回退未暂停 | v1 | 已实现（降级 WARNING） |
| P2.6 | 修复后全量重跑验证 | ~~.state.yaml 记录 last_fix_phase；hook 检查~~ | 修复引入回归 | v1 | **移除**（评审：hook 无法验证 full run vs partial run，属流程层规则） |
| P2.15 | .state.yaml 格式校验 | pre-commit hook 检查 .state.yaml 必填字段 + retries 列表结构 + phase 合法值 | Agent 写出不符协议的状态文件导致 hook 静默失效 | v3 | 已实现 |

#### 2B. 产出独立化与流程选择硬约束（需协议改动 + 评审）

##### 2B-1. 产出独立化

| 编号 | 名称 | 做什么 | 解决什么 | 来源 | 状态 |
|------|------|--------|---------|------|------|
| P2.1 | P6 验收独立化 | verifier subagent 独立执行 BDD 验收，直接 commit 产出（独立 author）；主 Agent 只读结论 | T026 根因：主 Agent 编造验收结果 | v1 | 待实现（有平台依赖，见下） |
| P2.2 | BDD 格式约定 + 总数对照 | P1 BDD 条目格式约定；check-gate.sh P6 扩展：从 P1 计数 vs P6 结果计数 | P6 exit 2 -> exit 0/1 | v1 | 待实现 |

##### 2B-2. 流程选择硬约束

| 编号 | 名称 | 做什么 | 解决什么 | 来源 | 状态 |
|------|------|--------|---------|------|------|
| P2.7 | 风险等级字段 | P1-requirements.md 增加 risk_level: low/medium/high + 量化条件 | 裁剪决策依赖临场判断 | v2 (S4) | 待实现 |
| P2.8 | 裁剪条件 hook 检查 | hook 检查裁剪需满足条件（风险等级 + BDD 数等） | Agent 默认倾向裁剪 | v2 (S4) | 待实现 |
| P2.9 | 裁剪声明回写 | 裁剪声明与实际执行不一致时必须回写 P1 override 字段 | P1 声明与执行不符 | v2 (C1) | 待实现 |
| P2.10 | P2 评审派发强制 | risk_level=high -> P2-review.md git author 非主 Agent | Agent 默认自审 | v2 (S3) | **移除**（评审 C1：subagent 共享 git config，author 恒相等，high risk 100% 卡死，同 P2.1 待 Phase 3 平台支持） |
| P2.11 | SCOPE+ 处理追踪 | 协议定义 [SCOPE_RESOLVED] 标记；hook 检查对应关系 | 忘了处理 SCOPE+ | v1 | 待实现 |
| P2.12 | 复盘异常触发 | 脚本检测异常模式 -> 强制提醒复盘 | Agent 默认不复盘 | v2 (E3) | 待实现 |

##### 2B-3. 非 agate 任务最低门槛（v3 新增，来自评审 S2 裁决）

| 编号 | 名称 | 做什么 | 解决什么 | 来源 | 状态 |
|------|------|--------|---------|------|------|
| P2.13 | 非 agate 任务风险矩阵 | 适用边界表增加"复杂度 × 风险"维度；高风险微改动必须走精简 agate（P1+P4+P5） | 安全修复裸 commit 无质量保障 | v3 (S2) | 待实现 |
| P2.14 | "直接做"最低要求 | commit message 必须声明改了什么 + 为什么安全 | 不走 agate = 没有任何记录 | v3 (S2) | 待实现 |

**P2.1 P6 验收独立化（详细）**：

当前流程：
```
P5 gate 通过 -> 主 Agent 自己跑 BDD 验收 -> 主 Agent 写 P6-acceptance.md -> 主 Agent 自己判 gate
```

改为：
```
P5 gate 通过 -> 主 Agent 派发 verifier subagent
  -> verifier subagent 独立读 P1 BDD 条件
  -> verifier subagent 逐条执行验证（跑测试、截图、检查输出）
  -> verifier subagent 产出 P6-acceptance.md + P6-evidence/
  -> verifier subagent commit 产出（author: verifier，非主 Agent）
主 Agent -> 读 P6-acceptance.md -> 跑 check-gate.sh P6 -> 判定
```

**关键变化**：P6-acceptance.md 的**作者**从主 Agent 变成 verifier subagent。主 Agent 从"自己写结论自己判"变成"读别人的结论自己判"。

**防操控**：
- dispatch-prompt 模板固化 P6 验收 prompt（B7 规则先例）
- prompt 必须包含"独立验证，不接受主 Agent 预判结论"
- git author 元数据提供可追溯性

**已知难点（v3 新增，来自评审 2.3）**：

P2.1 是整个路线图实现难度最高的一条，有三个已知难点：

1. **主 Agent 从"执行者"变"只读者"**：当前协议里主 Agent 是 P6 的执行者，改成"只读"需要重写 P6 的派发逻辑和 state-machine 转移规则。这不是加一个 hook 能解决的，是协议级改动。

2. **dispatch prompt 的预判问题**：路线图写"prompt 必须包含独立验证，不接受主 Agent 预判结论"——但主 Agent 可以在 dispatch-context.md 里放"预判"内容，这条规则本身靠 Agent 自觉。缓解：dispatch-prompt 模板由 hook 验证结构（而非内容），主 Agent 不能自行修改模板结构（B7 规则先例）。

3. **git author 独立性的平台依赖**：Claude Code / OpenCode 的 subagent 是否支持用不同 git author 提交？**这是平台依赖问题，需要先验证。**

**平台不支持时的降级方案**：
- 用文件 mtime 做替代独立性验证（P6-acceptance.md 的 mtime 在 verifier subagent 派发之后）
- 用内容哈希做追溯（P6-acceptance.md 的内容与主 Agent 的已知写作风格不一致时标记为"需审查"）
- 这些降级方案不完美，但比"主 Agent 自己写自己判"更强

**结论**：P2.1 的实现顺序应该在 Phase 2B 的最后，且需要先做平台能力调查（见 P3.1）。如果平台不支持独立 author，P2.1 降级为"verifier subagent 产出 + 降级独立性验证"，而不是等平台支持才做。

**P2.7-P2.8 风险等级与裁剪条件（详细）**：

P1-requirements.md 增加字段：
```yaml
risk_level: low | medium | high
# low: 纯 UI/文案/配置，不涉及数据/安全/权限
# medium: 涉及业务逻辑/API/数据模型
# high: 涉及安全/权限/数据迁移/生产环境
```

裁剪条件（hook 验证）：
```
裁剪 P2（方案设计）：
  条件：risk_level=low AND BDD 条目数 <= 10 AND 不跨模块
  否则：不可裁剪

裁剪 P3（TDD）：
  条件：risk_level=low AND 纯前端改动
  否则：不可裁剪

裁剪 P6（验收）：
  条件：无（P6 是行为验证，任何任务都不应裁）
  例外：仅限纯内部重构（无行为变化），需 P1 显式声明 no_behavior_change: true

裁剪 P7（一致性）：
  条件：改动文件数 <= 5 AND 单包改动
  否则：不可裁剪

P3+P4 合并：
  条件：risk_level=low AND BDD 条目数 <= 10 AND 不涉及安全/数据
  否则：不可合并
```

这些阈值来自 PeekView 实战数据，各项目可自行调整，但 agate 提供默认值。

> **⚠️ 阈值警示**：以下阈值来自 PeekView 一个项目的实战数据，非理论推导。各项目应根据实际情况调整（通过环境变量或配置文件覆盖）。阈值过严比过松好——过严导致评审多一点（成本），过松导致裁剪不该裁的（风险）。详见第 8.6 节。

**P2.10 P2 评审派发强制（详细）**：

```
risk_level=high -> P2-review.md 的 git author 必须非主 Agent
  hook 检查：git log --format='%an' -- P2-review.md
  若 author == 主 Agent 的默认 identity -> gate 不通过

risk_level=medium -> P2 可自审，但 P2-review.md 必须含 self_review: true 标记
risk_level=low -> P2 可裁剪（见 P2.8）
```

**P2.12 复盘异常触发（详细）**：

不要求每个任务复盘，但以下异常模式触发强制复盘提醒：
```
异常模式（脚本检测）：
  - gate 重试超限（retries >= MAX）
  - SCOPE+ 触发
  - 裁剪声明与执行不一致（override 触发）
  - P6 证据缺失（P6-evidence/ 为空）
  - P5 修复后重跑（last_fix_phase 触发）

触发动作：
  脚本输出 "建议复盘：[异常原因]" 到 commit 输出
  不中止 commit，但记录到 .gate-history.jsonl 的 review_recommended 字段
```

这不是硬拦截——复盘是学习行为不是质量 gate。但"不提醒"和"提醒了但跳过"是不同的，后者留下了痕迹。

**解决什么**：
- P6 验收结果伪造（verifier 独立 commit）
- 状态转移违规（hook 强制检查）
- 重试超限不暂停（hook 强制检查）
- BDD 总数对照从手动变自动
- SCOPE+ 未处理（标记追踪）
- 修复后不全量重跑（gate-result 对照）
- 裁剪决策滥用（风险等级 + 量化条件，v2）
- P2 评审从不派发（高风险强制派发，v2）
- 裁剪声明与执行不符（回写要求，v2）
- 复盘被跳过（异常触发提醒，v2）

**不解决什么**：
- 主 Agent 误导 verifier subagent（缓解：模板固化，但不根治）
- exit 2 gate 的判断质量（主 Agent 仍需判断，但结果被记录）
- 测试质量上限（局限 1）
- 同源模型盲区（局限 2）

**完成标准**：
- P6 验收由 verifier subagent 独立产出，主 Agent 不写 P6-acceptance.md
- check-gate.sh P6 从 exit 2 降为 exit 0/1（BDD 总数对照脚本化）
- 状态转移、重试计数、回退跳变由 pre-commit hook 强制检查
- P1 含 risk_level 字段，裁剪条件由 hook 验证
- 高风险任务的 P2 评审由独立 subagent 产出
- SCOPE+ 处理追踪落地
- 复盘异常触发脚本落地
- 在真实项目验证一个完整任务

---

### Phase 3：平台接口规范（需平台支持）

**目标**：定义 agate 需要的平台能力接口。当前平台不支持这些能力，agate 先写规范，等平台跟上后启用。

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

**完成标准**：
- 平台接口规范文档落地
- 至少一个平台实现其中一项能力
- agate 协议标注"如果平台支持 X，agate 启用 Y"
- 依赖平台能力的 gate 检查从"主 Agent 自觉"切换到"平台强制"

---

## 6. 三阶段依赖关系

```
Phase 1 (纯加工具)          Phase 2 (协议改动)          Phase 3 (平台支持)
     |                           |                           |
     |- P1.1 pre-commit hook    |- 2A 状态一致性（可和P1捆绑）|- P3.1 接口规范
     |- P1.2 PROD_TOUCHED       |  P2.3 状态转移强制         |- P3.2 subagent 可观测
     |- P1.3 CI backstop        |  P2.4 重试计数强制          |- P3.3 结果独立存储
     |- P1.4 gate-result        |  P2.5 回退跳变检测          |- P3.4 gate 平台化
     |- P1.5 READY 检查         |  P2.6 修复全量重跑验证
     |- P1.6 CHANGELOG 检查     |- 2B 产出独立化 + 流程选择（需评审）
     |- P1.7 P6 证据格式        |  P2.1 P6 独立化（⚠️平台依赖）
                                |  P2.2 BDD 格式 + 总数
                                |  P2.7-P2.12 流程选择硬约束
                                |  P2.13-P2.14 非 agate 门槛（v3）
     |                           |
     |  2A 可和 Phase 1 捆绑     |  2B 依赖 P3.1 的平台调查
     |  不需要协议改动            |  需要协议改动 + 评审
     |                           |
     v                           v
  不依赖 Phase 2B              不依赖 Phase 3
  可以先落地                  可以先写规范
```

**关键**：每个 Phase 独立有价值。Phase 1 落地后不依赖 Phase 2 也能运行；Phase 2 落地后不依赖 Phase 3 也能运行。Phase 3 的规范文档可以和 Phase 1 并行写。

---

## 7. 与 LIMITATIONS.md 的对应关系

| 局限 | 描述 | Phase 1 缓解 | Phase 2 缓解 | Phase 3 根治 |
|------|------|-------------|-------------|-------------|
| 局限 1 | 测试质量上限 | — | — | —（方法论边界） |
| 局限 2 | 同源模型盲区 | — | — | —（方法论边界） |
| 局限 3 | 主 Agent 判断力单点 | gate 执行不被跳过 | P6 独立化 + 状态强制 + 流程选择硬约束 | 结果防篡改 |
| 局限 4 | subagent 不可观测 | — | — | 平台可观测性 |
| 局限 5 | 协议文档一致性 | — | — | —（已有 CI 检查） |

**局限 3 的缓解路径**（v2 修正）：

原表述："主 Agent 遇到困难时倾向于自行解决而非触发安全网"

修正表述：**"主 Agent 在一切时候都倾向于少走步骤，不只是遇到困难时"**

- Phase 1：主 Agent 不能跳过 gate 执行（hook 自动跑），不能伪造 gate 结果（hook 覆盖 + CI 对照）
- Phase 2：主 Agent 不能伪造 P6 验收（verifier 独立 commit），不能违规跳阶段（hook 强制检查），**不能随意裁剪（风险等级 + 量化条件），不能自审高风险任务（P2 评审派发强制）**
- Phase 3：gate 结果存储在主 Agent 不可写的位置，根治伪造

每个 Phase 把"主 Agent 自觉"替换一层：**执行 → 产出 → 选择 → 存储**。四层叠加后，主 Agent 仍然是决策者，但不再是唯一的执行者、验证者、流程选择者和存储者。

**v2 新增：LIMITATIONS.md 局限 3 表述需更新**，从"遇到困难时倾向于自行解决"改为"默认倾向于少走步骤"。这影响防护策略——不是只加固"困难场景"，是所有依赖 Agent 自觉的环节都需要硬约束。

---

## 8. 风险与缓解

### 8.1 硬工具自身有 bug

**风险**：check-gate.sh 或 pre-commit hook 有 bug，导致误拦或漏放。

**缓解**：
- 误拦是可恢复的——PAUSED 后人工审查，发现问题后修脚本
- 漏放是真实风险——但硬工具至少和"主 Agent 判断"一样好，通常更好
- CI backstop 在不同环境重跑，catch 环境特定 bug
- 所有脚本版本控制，bug 可追溯、可修复
- Phase 1 不改协议，bug 影响范围有限

### 8.2 hook 被绕过

**风险**：`git commit --no-verify` 跳过 hook。

**缓解**：
- CI backstop 重跑所有检查
- branch protection 规则要求 CI 绿灯才能 merge
- 绕过路径需要：repo 管理员权限 + 刻意操作——这是仓库治理问题

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
- 裁剪条件有 override 机制——主 Agent 可以附理由 override，但留痕可审计

### 8.5 .gate-result.json 伪造

**风险**：主 Agent 手动修改 .gate-result.json。

**缓解**：
- pre-commit hook 覆盖：hook 在 commit 前重新跑 gate，覆盖任何手动修改
- CI 对照：CI 重跑 gate，结果不一致则红灯
- timestamp 验证：CI 检查 timestamp 在 commit 之前
- Phase 3 根治：结果存储在主 Agent 不可写的位置

### 8.6 裁剪条件阈值不适用所有项目（v2 新增）

**风险**：P2.8 的裁剪条件阈值（BDD<=10 可裁 P2 等）来自 PeekView 一个项目，可能不适用其他项目。

**缓解**：
- 阈值作为默认值，各项目可通过环境变量或配置文件覆盖
- agate 文档标注"这些阈值来自 PeekView 实战数据，非理论推导"
- 随着更多项目使用 agate，收集数据校准阈值
- 阈值过严比过松好——过严导致 P2 评审多一点（成本），过松导致裁剪不该裁的（风险）

---

## 9. 优先级与时间线

| Phase | 优先级 | 理由 | 预估工作量 |
|-------|--------|------|-----------|
| Phase 1 + 2A | 高 | 成本最低、收益最大；2A 可和 Phase 1 捆绑（都是 hook 逻辑，不需协议改动） | 4-5 个实现任务 |
| Phase 2B | 中 | 解决 T026 根因 + 流程选择硬约束；需协议改动 + 评审 + 平台调查 | 6-8 个实现任务 |
| Phase 3 | 低 | 纯文档可以先写，实现等平台 | 1 个规范文档 + 等平台 |

**建议**：
1. Phase 1 + 2A 立即推进（下一个实现任务，捆绑实现）
2. Phase 3 的规范文档（P3.1）可以和 Phase 1 并行写（纯文档无成本）
3. Phase 2B 在 Phase 1 + 2A 验证通过后推进（需要协议改动 + 平台能力调查）
4. Phase 2B 内部：先做 P2.2（BDD 格式 + 总数对照）和 P2.7-P2.12（流程选择硬约束），P2.1（P6 独立化）最后做——因为它有平台依赖，需要先调查 P3.1

---

## 10. 总结

agate 的核心矛盾是：**设计哲学说"不依赖主 Agent 判断力"，但现实中可判定的规则只能覆盖已知风险模式，且 Agent 默认倾向于少走路**。

PeekView 12 任务实战修正了一个关键判断：Agent 的"走捷径"不是"遇到困难时的行为退化"，是**出厂设置**——一切时候都倾向于少走步骤。这意味着所有依赖 Agent 自觉的环节都是脆弱的，不只是"困难场景"。

硬工具化不是"再加一层规则"——而是**把规则的执行权和流程选择权从主 Agent 手里拿走**。主 Agent 仍然决定做什么、怎么判断，但"有没有跑 gate"、"结果是什么"、"能不能裁剪"、"该不该派评审"由独立机制记录和验证。

四层替换：
- Phase 1：**执行层**——gate 不被跳过，结果不被伪造（hook + CI）
- Phase 2：**产出层 + 选择层**——P6 验收不自己写，状态转移不自己判，裁剪不自己定，评审不自己审（verifier 独立化 + hook 强制 + 风险等级）
- Phase 3：**存储层**——gate 结果不可篡改，subagent 行为可观测（平台接口）

每个 Phase 把"主 Agent 自觉"替换一层：执行 → 产出 → 选择 → 存储。四层叠加后，主 Agent 仍然是决策者，但不再是唯一的执行者、验证者、流程选择者和存储者。这就是文档协议路线突破能力边界的方向。
