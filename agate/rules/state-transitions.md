# 状态转移与恢复规则

> 权威源：`agate/state-machine.md`。本文提取跨阶段共用的转移/重试/恢复规则，供各阶段卡片按需查阅。

## 状态集合

```
P0 → P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → READY → DONE
任意阶段 → PAUSED（人工介入后恢复）
```

## 转移条件（逐阶段）

### P0 → P1
- P0-brief.md 完成，五字段自查通过（task / known_risks / executor_env / env_constraints / pruning_tendency）

### P1 → P2
- P1-requirements.md 有效 + 含至少一条 BDD 验收条件 + 无未决行首 NEED_CONFIRM（无待确认项写 `[NO_NEED_CONFIRM]`）+ 无 status: GAP（supplementable 不阻）

### P2 → P3
- P2-review.md 有效 + status: approved + P2-design.md 声明 packages/domains/ui_affected/gate_commands + 候选方案 ≥2 + 含权衡/选择理由/取舍/考量/trade-off

### P3 → P4
- check-tdd-red.sh exit 0 + assertion_failures>0 + collection_errors==0
- UI 任务：P3 含 Playwright/E2E 用例

### P4 → P5
- 暂存区含非 md/yaml 文件（git diff --cached）

### P5 → P6
- gate_commands.P5 全部 exit 0 + failed==0 + 无 PROD_TOUCHED（二值格式：触发写 `[PROD_TOUCHED] {描述}`，未触发写 `[PROD_NOT_TOUCHED]`）
- UI 任务：gate_commands.P5 E2E 命令 exit 0

### P6 → P7
- check-gate.sh P6 exit 2（FAIL=0 / NC=0 / 证据非空）
- check-p6-provenance.sh exit 0 或 exit 2（主 Agent 手动核实 BDD 总数）

### P7 → P8
- 声明行 [BLOCKER]: N 条 被排除后 =0 / [DEVIATION-CRITICAL] 同理
- DESIGN_GAP 全部配对 REVIEWED

### P8 → READY
- 各 package 发布检查 exit 0 + version bump 确认 + CHANGELOG 非空
- READY 收尾检查：测试环境清理 / 开发环境还原 / git tag 创建

## 重试上限

| 阶段 | MAX | 说明 |
|------|-----|------|
| P1 | 3 | 需求基线 |
| P2 | 3 | 方案设计 |
| P3 | 2 | TDD 红灯 |
| P4 | 3 | 实现 |
| P5 | 2 | 技术验证 |
| P6 | 2 | 验收 |
| P7 | 2 | 一致性 |
| P8 | 2 | 发布 |

重试记录按阶段独立存储于 `.state.yaml` 的 `retries` 字段。

## 回退规则

| 回退范围 | 允许？ | 处理 |
|----------|--------|------|
| Pn → Pn-1（单步回退）| ✅ 允许 | retry+1，定向回补不清零目标阶段已有的 retry |
| |n-m| ≥ 2（跨多阶段）| ❌ 强制 PAUSED |

## PAUSED 恢复

- 人工确认/决策后恢复到 PAUSED 前的阶段
- PAUSED 原因 = retry 耗尽 → recovery_bonus=1，允许额外 1 次重试（可选，写入 .state.yaml）
- SCOPE+（行首声明格式）暂不处理，恢复后一并纳入 P1 基线增补

## 中断恢复步骤

1. 重读 orchestrator-template.md 的 mapping 表 → 查当前阶段卡片
2. 读 active-tasks.md → 确认进行中任务
3. 读 .state.yaml → 确认 phase + retries
4. 读 docs/tasks/{Txxx}/ → 确认产出文件是否存在（不存在 → 无效标记，回退到 Pn-1）
5. 按卡片指引执行当前阶段

## 状态标记绑定（T019 教训）

.state.yaml 标记 Pn，但 Pn 产出文件不存在 → 无效标记。回退到 Pn-1 重新执行 gate。标记不能在验证之前。

## PROD_TOUCHED

任意阶段出现行首 PROD_TOUCHED 标记（二值格式：触发写 `[PROD_TOUCHED] {描述}`，未触发写 `[PROD_NOT_TOUCHED]`）→ 立即 PAUSED，报告人工。
