---
type: plan
source: docs/reviews/agate-T025-feedback-review-2026-06-28.md
trace_id: agate-T025-cheatsheet-2026-06-28
created: 2026-06-28
status: 待执行
---

# 修复方案：T025 反馈落地（gate-cheatsheet.md）

> 来源：`docs/reviews/agate-T025-feedback-review-2026-06-28.md`
> 裁决：6 条建议采纳 1 条（A 修正版），拒绝 5 条
> 落地范围：仅 gate-cheatsheet.md（导航索引定位）

## 落地动作

### 动作 1：新增 `gate-cheatsheet.md`

**文件**：`~/.agate/gate-cheatsheet.md`

**定位**：导航索引——告诉主 Agent "每个 gate 跑什么命令"，减少从三个协议文件中提取判定规则的重复劳动。**不是执行替代**——异常时必须读产出全文分析。

**内容结构**：

```markdown
# Gate Cheatsheet — 每阶段判定命令快速索引

> ⚠️ 本文件是导航索引，不是执行替代。
> 正常路径：跑命令 → exit 0 / grep 无命中 → 通过 → next
> 异常路径：命令返回非零或 grep 命中 → 必须读产出全文分析根因，不可仅凭 exit code 跳过分析。

| Gate | 判定命令 | 通过条件 | 产出文件（异常时回溯阅读） |
|------|---------|---------|------------------------|
| P1 | `grep -c NEED_CONFIRM {task}/P1-requirements.md`; `grep -c CAPABILITY_GAP {task}/P1-requirements.md`; `grep -cE '^\s*-?\s*AC\d+.*Given.*When.*Then' {task}/P1-requirements.md` | NEED_CONFIRM=0 AND CAPABILITY_GAP=0 AND BDD≥1 | P1-requirements.md |
| P2 | `grep 'status: approved' {task}/P2-review.md` | 命中 | P2-design.md + P2-review.md |
| P3 | `{project_test_runner} {test_dir} -q 2>&1 \| tail -1` | failed>0 AND errors=0 | check-tdd-red.sh 输出 |
| P4 | `{project_test_runner} -q 2>&1 \| tail -1` | failed=0 AND errors=0 | implementer 产出记录 |
| P5 | `{project_test_runner} -q 2>&1 \| tail -1`; `grep -rc PROD_TOUCHED {task}/` | failed=0 AND PROD_TOUCHED=0 | P5-verification.md |
| P6 | `grep -cE '^\s*- (PASS|FAIL)' {task}/P6-acceptance.md`; `grep -cE '^\s*-?\s*AC\d+.*Given.*When.*Then' {task}/P1-requirements.md` | FAIL_count=0 AND P6_count==P1_BDD_count | P6-acceptance.md |
| P7 | `grep -cE '^\s*-?\s*\[BLOCKER\]' {task}/P7-consistency.md`; `grep -cE '^\s*-?\s*\[DEVIATION-CRITICAL\]' {task}/P7-consistency.md` | BLOCKER=0 AND DEVIATION-CRITICAL=0 | P7-consistency.md |
| P8 | 从 P2 gate_commands 读取每个 package 的发布检查命令逐个执行 | 全部 exit 0 AND bump 后重跑 P5 gate 通过 | P8-release.md |

## 项目级变量

以下变量从 P0-brief.md 的 executor_env 读取，不在本文件硬编码：

- `{project_test_runner}`：项目测试启动命令（如 `.venv/bin/python -m pytest`、`npx vitest run`）
- `{test_dir}`：TDD 测试文件目录（如 `backend/tests/`）
- `{task}`：当前任务目录（如 `docs/tasks/T025`）
```

**关键设计决策**：

1. **全局警告**：文件头部标注"异常时必须读产出全文"，防止主 Agent 把 cheatsheet 当成"只看 exit code 就够了"
2. **产出文件列**：每行列出异常时需回溯阅读的文件，主 Agent 不需要再想"异常时该读什么"
3. **项目级变量不硬编码**：`{project_test_runner}` 等从 P0-brief.md 读取，cheatsheet 本身是协议级文档，不含项目特定值
4. **P3 gate 修正**：T025 暴露了 `check-tdd-red.sh` 用裸 `pytest` 导致假绿灯的 bug。cheatsheet 明确写 `{project_test_runner}` 而非 `pytest`，避免同样的坑
5. **P6 gate 含 BDD count**：与 T022 动作 1（P6 BDD 总数对照）一致，此处一并体现
6. **P7 gate 含 DEVIATION-CRITICAL**：与 T022 动作 4 一致
7. **P8 gate 含 bump 后重跑 P5**：与 T022 动作 2 一致

### 动作 2：dispatch-protocol.md 引用 cheatsheet

**文件**：`~/.agate/dispatch-protocol.md`

**改法**：在「可判定门槛规范」节开头追加一段引用：

```markdown
> 快速索引：每个 gate 的判定命令见 `gate-cheatsheet.md`。cheatsheet 是本节的导航索引，不是替代——异常时仍需阅读本节完整规则和产出文件全文。
```

### 动作 3：state-machine.md 引用 cheatsheet

**文件**：`~/.agate/state-machine.md`

**改法**：在「主 Agent 的单步执行（一轮）」节步骤 5（gate 判定）处追加引用：

```markdown
5. gate 判定：按 `gate-cheatsheet.md` 中的命令执行。正常路径（命令通过）→ 进入下一阶段；异常路径 → 读产出文件全文分析根因。
```

---

## 不落地项

| # | 原始建议 | 不落地理由 |
|---|---------|-----------|
| B | dispatch-base.md 常量段提取 | 不省 subagent 上下文，引入版本一致性风险 |
| C | skip_reviews + 判定规则表 | Agent 自信判断不可信，评审不可跳过 |
| D | 分层 P5 gate | 质量环节不可裁减 |
| E | verification_env 按环境判定写跑分离 | subagent 无 timeout kill，写跑分离隔离 hang 风险 |
| F | 信任等级 | 修正后的 cheatsheet 不需要此分类，全局注释覆盖 |

## 与 T022 计划的交叉

T022 计划（`docs/plans/agate-t022-mechanism-fixes-2026-06-26.md`）中的 7 项动作与本计划无冲突：

- T022 动作 1（P6 BDD count）→ cheatsheet P6 行已体现
- T022 动作 2（P8 bump 后重跑 P5）→ cheatsheet P8 行已体现
- T022 动作 4（P7 DEVIATION-CRITICAL）→ cheatsheet P7 行已体现
- T022 其余动作（3/5/6/7）不涉及 cheatsheet

**执行顺序**：T022 计划先落地（修改 state-machine.md / dispatch-protocol.md 的 gate 定义），本计划后落地（新增 cheatsheet + 添加引用），确保 cheatsheet 反映的是最新的 gate 规则。

## 落地清单

| # | 动作 | 文件 | 工作量 |
|---|------|------|--------|
| 1 | 新增 gate-cheatsheet.md | gate-cheatsheet.md | 15 分钟 |
| 2 | dispatch-protocol.md 追加 cheatsheet 引用 | dispatch-protocol.md | 2 分钟 |
| 3 | state-machine.md 追加 cheatsheet 引用 | state-machine.md | 2 分钟 |

**总计**：3 项动作，约 19 分钟。
