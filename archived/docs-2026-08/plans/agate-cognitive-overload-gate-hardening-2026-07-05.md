---
task_id: agate-cognitive-overload-gate-hardening
agent: main
date: 2026-07-05
status: 设计方案
来源: docs/issues/003-main-agent-cognitive-overload.md + T046 复盘
---

# 主 Agent 认知过载防御：gate 硬约束下放

## 问题

agate 的可靠性来自规则密度，但规则密度本身就是认知负担。主 Agent 过载时：
- 忘了派评审、忘了做端到端验证、忘了落盘
- 用"指标正确"替代"功能正确"说服自己
- gate 硬约束（格式）天然优先于功能软约束（验证）

**核心原则**：把"Agent 过载时会跳过的检查"写成 gate 脚本——Agent 可以过载，但不能跳过 gate。

## 评审覆盖缺口（全貌）

role-system.md C8 机械映射定义了哪些阶段需要什么评审角色，但 gate 脚本几乎完全未强制执行：

| 阶段 | 需要的评审 | C8 定义 | gate 强制？ |
|------|-----------|---------|------------|
| **P1** | 需求评审 | ❌ 未定义 | ❌ （连评审角色都没有） |
| **P2** | P2-review.md status:approved | ✅ | ⚠️ 文件存在时查，不存在静默放行 |
| **P2** | plan-design-review（frontend） | ✅ | ❌ |
| **P2** | plan-eng-review（risk=high） | ✅ | ❌ |
| **P2** | plan-ceo-review（业务方向不明） | ✅ | ❌ |
| **P4** | review（backend） | ✅ | ❌ |
| **P4** | design-review（frontend） | ✅ | ❌ |
| **P4** | cso（security） | ✅ | ❌ |
| **P4** | review（mcp） | ✅ | ❌ |

本次计划只覆盖 P2-review.md 强制（G2），其余缺口待后续迭代。

## 范围

三处 gate 脚本改动 + 对应测试用例：

| # | 改动 | gate 脚本 | 影响阶段 |
|---|------|-----------|---------|
| G1 | P2 gate：`ui_affected: true` 时，`gate_commands.P5` 必须含至少一条 E2E 命令 | `check-gate.sh` | P2→P3 |
| G2 | P3 gate：P2 未被裁剪时，检查 `P2-review.md` 存在且 `status: approved` | `check-gate.sh` | P3→P4 |
| G3 | P6 gate：`ui_affected: true` 时，P6 必须至少一条 PASS 以 vision-helper 报告为据；vision-helper 报 blocker>0 时不得仅用程序化指标反驳 | `check-gate.sh` + `check-p6-evidence.sh` / `check-p6-provenance.sh` | P6→P7 |

不涉及：
- orchestrator-log.md 强制（那是防无响应，不是 gate 的事）
- P2 最小验证显式化（触发规则改协议文档，本次不做）
- 否定证据处理规则（属 Agent 行为规范，gate 脚本能覆盖一部分但不全包）

## G1: P2 gate → gate_commands.P5 端到端要求

### 规则

P2 gate 执行时，若 P2-design.md 声明 `ui_affected: true`，检查 `gate_commands.P5_e2e` 字段存在且非空。

### 判定

- `ui_affected: true` 且无 `gate_commands.P5_e2e` 或值为空 → exit 1（E2E 命令缺失）
- `ui_affected: false` → 不检查
- 仅警告不存在的字段名，如 `gate_commands.P5_e2e` 不存在但有 `gate_commands.P5` 含 E2E 语义的命令 → 不阻塞（启发式不够可靠，先不做）

### 协议文档联动

- `task-files.md` P2-design.md 结构：`gate_commands.P5_e2e` 从"建议"改为"ui_affected: true 时必须"
- `dispatch-protocol.md` P2 派发：architect 声明 `ui_affected: true` 时必须填 `P5_e2e`

### 测试用例（G2.E2E.*）

- G2.E2E.1: ui_affected=true + P5_e2e 存在 → exit 2（通过）
- G2.E2E.2: ui_affected=true + 无 P5_e2e → exit 1（拦截）
- G2.E2E.3: ui_affected=false + 无 P5_e2e → exit 2（通过，不检查）
- G2.E2E.4: ui_affected=true + P5_e2e 为空 → exit 1

## G2: P3 gate → P2-review 前置条件

### 规则

P3 gate 执行时，检查 P2-review.md 存在且 `status: approved`。P2 被裁剪时跳过。

### 判定

- P2 未被裁剪（P2-design.md 存在）且 P2-review.md 不存在 → exit 1
- P2 未被裁剪且 P2-review.md 存在但 `status` 不是 `approved` → exit 1
- P2 被裁剪（P2-design.md 不存在）→ 不检查
- P2 未被裁剪且 P2-review.md 存在且 `status: approved` → exit 0

### 注意

当前 `check-gate.sh` P3 阶段委托 `check-tdd-red.sh`。P2-review 检查应作为 P3 的**附加检查项**，和 TDD-red 检查并行——两者都通过才算 P3 gate 通过。

### 测试用例（G3.*）

- G3.RV.1: P2 未被裁剪 + P2-review.md 存在 + status:approved → exit 0
- G3.RV.2: P2 未被裁剪 + P2-review.md 不存在 → exit 1
- G3.RV.3: P2 未被裁剪 + P2-review.md status:rejected → exit 1
- G3.RV.4: P2 被裁剪（P2-design.md 不存在）→ 不检查
- G3.RV.5: P2 未被裁剪 + P2-review.md 存在 + 无 status 字段 → exit 1

## G3: P6 gate → vision-helper 结论绑定

### 规则

P6 gate 执行时，若 `ui_affected: true`：

1. 至少一条 PASS 必须含 `(vision: vision-reports/xxx.yaml)` 引用（已有机制的已有检查）
2. 若 P6-evidence/vision-reports/ 下任何 YAML 报告 `blocker_count > 0`，P6-acceptance.md 必须对该 blocker 有"追查结果"——不能仅有"程序化指标正常"的反驳

"追查结果"格式：`- PASS Bxx: ... (vision: xxx.yaml) — 追查: (API 响应头: Content-Type text/plain)` 或独立的追查记录文件（如 `P6-evidence/investigation.md`）。

### 判定规则（在 check-p6-evidence.sh 或 check-p6-provenance.sh 增加）

1. `ui_affected: true` + vision-reports/ 目录不存在或为空 → exit 1（至少一条 PASS 需要 vision 验证）
2. vision YAML 中存在 `blocker_count > 0`：
   - P6-acceptance.md 中有对应追查行（含 `追查:` 或 `investigation` 文件存在）→ 放行
   - P6-acceptance.md 中仅反驳（"程序化指标正常""naturalWidth>0""理论上应该能显示"）而无追查证据 → exit 1

### 边界

- `blocker_count: 0` → 不检查追查
- 非 UI 任务（`ui_affected: false`）→ 不检查 vision 相关项

### 测试用例（G6.VS.*）

- G6.VS.1: ui_affected=true + blocker_count=0 + vision 引用存在 → exit 0
- G6.VS.2: ui_affected=true + blocker_count>0 + 有追查行 → exit 0
- G6.VS.3: ui_affected=true + blocker_count>0 + 无追查行 → exit 1
- G6.VS.4: ui_affected=true + blocker_count>0 + 仅有程序化指标反驳 → exit 1
- G6.VS.5: ui_affected=true + 无 vision-reports/ 目录 → exit 1

## 实施步骤

### 步骤 1：G1 — P5 E2E 检查（check-gate.sh P2 阶段）

- [ ] `check-gate.sh` 的 P2 block 增加：提取 `ui_affected` 字段，若为 `true` 检查 `gate_commands.P5_e2e` 存在
- [ ] `task-files.md` P2-design 结构：`gate_commands.P5_e2e` 注释改为"ui_affected: true 时必须"
- [ ] `dispatch-protocol.md` P2.7：architect 声明 ui_affected 时 P5_e2e 必填
- [ ] `agate/tests/unit/check-gate.bats`：G2.E2E.1-G2.E2E.4

### 步骤 2：G2 — P2-review 前置条件（check-gate.sh P3 阶段）

- [ ] `check-gate.sh` 的 P3 block：在 TDD-red 检查之外，增加 P2-review.md 存在性+status 检查
- [ ] `agate/tests/unit/check-gate.bats`：G3.RV.1-G3.RV.5
- [ ] 确认现有 G3（P3 委托 check-tdd-red.sh）和 G2 测试不受影响

### 步骤 3：G3 — vision-helper 结论绑定（check-p6-evidence.sh / check-p6-provenance.sh）

- [ ] `check-p6-evidence.sh` 或 `check-p6-provenance.sh`：增加 vision blocker 追查检查
- [ ] `agate/tests/unit/check-p6-evidence.bats`：G6.VS.1-G6.VS.5
- [ ] 确认现有 E.* / PV.* 测试不受影响

### 步骤 4：全量验证

- [ ] `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` 全绿
- [ ] `python3 agate/scripts/check-protocol-consistency.py` 0 ERROR
- [ ] `shellcheck agate/scripts/*.sh` 0 error

### 步骤 5：更新文档

- [ ] `docs/issues/003-main-agent-cognitive-overload.md` 状态更新为"已实施"
- [ ] `LIMITATIONS.md` 局限 3 补充：已通过 gate 硬化部分缓解（不是根治）

## 优先级

| # | 优先级 | 理由 |
|---|--------|------|
| G1 | Medium | T046 未直接因此失败，但 P5 无 E2E 是因果链的一环 |
| G2 | High | P2-review 跳过直接导致设计 bug 未被发现（如 T046 的 B1 bug 是评审发现的） |
| G3 | Medium | vision-helper 绑定是防止"说服自己"的机制，但实施复杂度高于 G2 |

建议顺序：G2 → G1 → G3。
