---
review_date: 2026-07-24
reviewer: protocol-alignment-review
change_summary: v0.20.0 全量审查
files_changed: [全部协议文件 + 脚本]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

8 个重点检查项全部 ALIGNED：

1. **BDD 格式标准化**：`#### BDD-NN:` 格式（CONTEXT.md:15, analyst.md:122, task-files.md:140）→ `check-p6-provenance.sh:131` `grep -cE '^#### BDD-[0-9]'` → **ALIGNED**
2. **P1 BDD 锚点正则**：WORKFLOW.md:217 / dispatch-protocol.md:782 含 `BDD-[0-9]` 锚点 → `check-gate.sh:61` `grep -qE 'BDD-[0-9]'` → **ALIGNED**
3. **P6 provenance 审计 3 硬阻**：state-machine.md:117 "P1 `#### BDD-NN` 标题数与 P6 结果数不符时 exit 1 硬阻" → `check-p6-provenance.sh:137-139` P1_BDD==0 → exit 1; P6_TOTAL < P1_BDD → exit 1 → **ALIGNED**
4. **T6 AGATE_CARD 剥离**：dispatch-protocol.md:335 AGATE_CARD 注入声明 → `pre-commit-gate.sh:132` sed 剥离卡片块 → **ALIGNED**
5. **M5 gate_commands P5 计数**：脚本已实现（check-gate.sh:148-167 python3 YAML 块解析），文档未显式描述 → **NEEDS_HUMAN_REVIEW**（见下方）
6. **state-machine.md:117**：P6→P7 转移条件与实际行为一致 → **ALIGNED**
7. **state-machine.md:403**：已改为"审计 3 自动执行，不符时 exit 1" → **ALIGNED**
8. **rules/state-transitions.md:36**：与 check-p6-provenance.sh 行为一致 → **ALIGNED**

其他对齐项（16 条）全部 ALIGNED：P1 review 不可裁、P1/P2 agent=main 硬拦截、P6 BDD 二值规则、P6 证据目录非空、NEED_CONFIRM 三步检测、PROD_TOUCHED 三步检测、P7 BLOCKER/DEVIATION-CRITICAL 排除声明行、P7 DESIGN_GAP 配对、P7 P4→P7 DESIGN_GAP 转抄交叉核对、P8 bump_type 字段、P8 version 双路径检查、P8 CHANGELOG 双路径检查、P8 git tag 检查、回退抵达检测、provenance 审计 1/2/4/5、P6 evidence 截图实质检查。

### A2: 脚本→文档对齐

脚本逻辑均有文档描述对应。唯一缺口同 A1 重点检查项 5。

### A3: 一致性连锁 + 反向传播

| 文件 | 是否需同步 | 状态 |
|------|-----------|------|
| dispatch-protocol.md 可判定门槛规范 P5→P6 行 | 应描述 P5 命令计数 WARNING | 未更新（NEEDS_HUMAN_REVIEW，低优先级） |
| CHECK 9 锚点表 | 已覆盖全部 11 个 gate 脚本 | ALIGNED |
| rules/state-transitions.md P6→P7 条件 | 与 check-p6-provenance.sh 行为一致 | ALIGNED |
| phase-cards/P6-acceptance.md | gate 规则节列出 check-gate + evidence + provenance | ALIGNED |
| phase-cards/P1-requirements.md | gate 规则节含 BDD 编号格式 | ALIGNED |

### A4: 测试覆盖

```
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
399 tests, 0 failed
check-protocol-consistency.py: 0 ERROR, 10 WARNING（全部为叙事文件死链）
shellcheck -S warning agate/scripts/*.sh: clean
```

重点变更相关测试：BDD 格式（PV_BDD_COUNT）、P1 BDD 锚点（check-gate-p1-review.bats）、P6 provenance 硬阻（PV.9/PV.10）、AGATE_CARD 剥离（IT_PT_T6.1-4）、P5 CMD COUNT（G5_CMD.1-5）、P6 代码硬拦截（IT_P6_CODE.1-5）。

### A5: 下游影响 + 文档传播

- 无破坏性变更需额外传播
- CHANGELOG 已由 PR #47 更新

### A6: 锚点表覆盖

CHECK 9 锚点表覆盖全部 11 个 gate 脚本（SG.6 测试通过）。v0.20.0 新增锚点：`P1 BDD 编号格式检查（标准 #### BDD-NN: 格式）` → check-gate.sh → keywords: `BDD-[0-9]`。

### A7: 设计原则一致性

| ADR | 符合？ | 说明 |
|-----|--------|------|
| ADR-001 隔离性 | ✅ | P6 代码硬拦截强化隔离 |
| ADR-002 可判定性 | ✅ | 审计 3 BDD 总数硬阻、P5 命令计数 WARNING 均为机器可判定 |
| ADR-003 最小约定 | ✅ | 无新增硬性约定 |
| ADR-004 安全网分层 | ✅ | AGATE_CARD 剥离防止误拦，CI backstop 兜底 |
| ADR-005 改动性质决定流程 | ✅ | 无变更 |
| ADR-006 双层角色 | ✅ | P1 review 不可裁，agent=main 硬拦截不变 |

## NEEDS_HUMAN_REVIEW 项

### P5 命令计数 WARNING 文档缺失

**脚本**：`check-gate.sh:148-167` — python3 解析 gate_commands YAML 块，P5 键数 >1 时发 WARNING 提醒全部执行（T060 教训）。

**文档缺口**：dispatch-protocol.md 可判定门槛规范 P5→P6 行未显式描述此行为。WORKFLOW.md:254 P5 行只说"从 gate_commands.P5 读取命令执行"，未提计数警告。

**建议**：在 dispatch-protocol.md:786 P5→P6 门槛追加"若 P2 声明多个 gate_commands.P5 命令，check-gate.sh 发 WARNING 提醒确认已全部执行（T060 教训）"。

**优先级**：低。WARNING 不阻断 gate，不影响项目使用。

[HUMAN_CONFIRMED: 2026-07-24 确认：P5 命令计数 WARNING 是辅助提醒而非 gate 规则，不补文档也可接受，暂不修]
