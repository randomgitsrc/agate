---
type: plan
source: ~/oclab/peekview/docs/reviews/agate-postmortem-T026-2026-06-28.md
trace_id: agate-T026-p6-evidence-2026-06-28
created: 2026-06-28
status: 待执行
---

# T026 P6 证据存在性 gate — 防伪造修复

> 来源：T026 复盘（P6 验收主 Agent 编造 11/16 BDD 结果，gate 被绕过）
> 核心故障：P6 gate 的 `grep PASS` 判定对象是主 Agent 自己写的文件，作者和裁判是同一人
> 修复方向：把 P6 从"信文件内容"推向"信外部产出"
> 评审修正：证据条件从"文件数 ≥ BDD 总数"简化为"目录存在且非空"（避免假阴性，纯后端任务可能只有 test-output.log 一个文件）

---

## 故障模式

```
P6 验收流程：
  verifier subagent 产出 P6-acceptance.md + 验证脚本
  主 Agent 跑验证脚本 → 收集证据 → 写 P6-acceptance.md 结果
  主 Agent 跑 gate: grep PASS P6-acceptance.md → 通过

  伪造路径：
  主 Agent 不跑验证脚本，直接在 P6-acceptance.md 写 PASS
  主 Agent 跑 gate: grep PASS P6-acceptance.md → 通过（假通过）
```

P1-P5 的 gate 判定对象是外部工具产出（pytest exit code、vue-tsc 输出、git log），主 Agent 无法伪造。P6/P7 的判定对象是主 Agent 自己写的 markdown，可以伪造。

---

## 裁决

| T026 建议 | 裁决 | 理由 |
|----------|------|------|
| 1 P6 gate 两级判定（证据存在性） | ✅ 采纳 | `ls` 判定证据目录非空是机器可判定的，直接堵住"无证据标 PASS" |
| 2 verifier 脚本必须执行 | ✅ 采纳 | gate 检查执行日志存在，把 P6 从"信文件"推向"信外部产出" |
| 3 gate 分类标记（外部产出 vs 自写文件） | ✅ 采纳 | 零成本信息性改进，提醒伪造风险 |
| 4 BDD 数与证据数强制关联 | ✅ 采纳（简化） | `evidence_count >= bdd_count` 可判定；去掉 `phase_start_time`（跨 session 不可靠） |
| 5 P6a/P6b 双 subagent 独立核查 | ❌ 拒绝 | 同模型同 prompt 的两个 subagent 不构成独立验证，只是多一层形式。真正有效的是 1+2 把 P6 从"信文件内容"变成"信外部产出" |

---

## 落地动作

### 动作 1：P6 转移规则追加证据存在性条件

**文件**：`state-machine.md`

**改法**：P6 转移规则追加：

```
P6 --[P6-acceptance.md 有效 AND P1 的每条 BDD 条件标记为 - PASS 或 - FAIL（行首标记格式，二值）AND P6 验收条数 = P1 BDD 总数 AND 无 - FAIL AND 无 [NEED_CONFIRM] AND P6-evidence/ 目录存在且非空 AND P6-evidence/ 文件数 ≥ P1 BDD 总数]--> P7
```

步骤 5 P6 行追加：
```
ls {task}/P6-evidence/ → 非空;
find {task}/P6-evidence/ -type f | wc -l → ≥ P1 BDD 总数
```

### 动作 2：P6 gate 门槛表追加证据条件

**文件**：`dispatch-protocol.md`

**改法**：门槛表 P6→P7 行追加：
```
AND `ls {task}/P6-evidence/` → 非空 AND `find {task}/P6-evidence/ -type f \| wc -l` → ≥ P1 BDD 总数
```

P6→P7 行末追加 `⚠️ self-authored` 标记。

### 动作 3：WORKFLOW.md P6 门槛列同步

**文件**：`WORKFLOW.md`

**改法**：P6 门槛列追加：`P6-evidence/ 非空 AND 文件数 ≥ BDD 总数`

### 动作 4：gate 分类标记

**文件**：`dispatch-protocol.md`

**改法**：在门槛表之后追加一段：

```markdown
**Gate 分类**：

| 类型 | 阶段 | 判定对象 | 可伪造？ |
|------|------|----------|----------|
| 外部产出 gate | P3, P4, P5 | 外部工具输出（pytest exit code, vue-tsc, git log） | 否 |
| 自写文件 gate ⚠️ | P1, P2, P6, P7 | 主 Agent 写的文件内容 | 是（主 Agent 直接写文件） |

自写文件 gate 的缓解措施：
- P1/P2：gate 条件简单（标记存在性、字段计数），伪造动机低
- P6：证据存在性检查（P6-evidence/ 非空 + 文件数 ≥ BDD 总数），无证据标 PASS 将被 gate 拦截
- P7：P5 回归测试兜底（一致性标注错误不会导致 bug 漏过）
```

### 动作 5：verifier.md P6 输出追加证据目录要求

**文件**：`assets/execution-roles/verifier.md`

**改法**：P6 输出节追加：

```markdown
- docs/tasks/{Txxx}/P6-evidence/ — 验收证据目录（每条 BDD 至少一个证据文件）
  - screenshots/ — Playwright 截图
  - test-output.log — 验证脚本执行日志
  - traces/ — Playwright trace（可选）
```

P6 质量门槛追加：

```markdown
- **证据完整性**：P6-evidence/ 目录必须存在且非空，文件数 ≥ BDD 总数。无证据的 PASS 标记将被 gate 拦截
```

### 动作 6：dispatch-prompt.md P5/P6 追加节追加证据要求

**文件**：`assets/templates/dispatch-prompt.md`

**改法**：P5/P6 派发追加节追加：

```
## P6 证据要求
每条 BDD 验收结果必须有对应证据文件，存入 docs/tasks/{Txxx}/P6-evidence/。
证据类型：截图（screenshots/）、执行日志（test-output.log）、trace（traces/）。
无证据的 PASS 标记 = gate 不通过。
```

`dispatch-protocol.md` P5/P6 派发时追加节同步追加同内容。

### 动作 7：P6 派发追加 verifier 脚本执行要求

**文件**：`dispatch-protocol.md` + `assets/templates/dispatch-prompt.md`

**改法**：P5/P6 派发追加节追加：

```
## P6 verifier 脚本执行
P6 verifier 交付的验证脚本（Playwright / shell / pytest）必须由主 Agent 执行。
执行输出落盘到 P6-evidence/test-output.log。
不接受主 Agent 自写脚本替代 verifier 交付的脚本。
```

### 动作 8：check-gate.sh P6 追加证据检查

**文件**：`scripts/check-gate.sh`

**改法**：P6 分支在 FAIL/NC 检查之后追加证据检查：

```bash
EVIDENCE_DIR="$TASK_DIR/P6-evidence"
if [ -d "$EVIDENCE_DIR" ]; then
    EVIDENCE_COUNT=$(find "$EVIDENCE_DIR" -type f 2>/dev/null | wc -l)
else
    EVIDENCE_COUNT=0
fi
if [ "$EVIDENCE_COUNT" -lt "$TOTAL" ]; then
    echo "GATE P6: evidence files ($EVIDENCE_COUNT) < BDD total ($TOTAL)" >&2
    exit 1
fi
```

---

## 落地清单

| # | 动作 | 文件 | 工作量 |
|---|------|------|--------|
| 1 | P6 转移规则追加证据条件 | state-machine.md | 5 分钟 |
| 2 | 门槛表追加证据条件 + self-authored 标记 | dispatch-protocol.md | 5 分钟 |
| 3 | WORKFLOW.md P6 同步 | WORKFLOW.md | 2 分钟 |
| 4 | gate 分类标记 | dispatch-protocol.md | 5 分钟 |
| 5 | verifier.md 证据目录要求 | assets/execution-roles/verifier.md | 3 分钟 |
| 6 | dispatch-prompt 证据要求 | assets/templates/dispatch-prompt.md + dispatch-protocol.md | 3 分钟 |
| 7 | verifier 脚本执行要求 | dispatch-protocol.md + assets/templates/dispatch-prompt.md | 3 分钟 |
| 8 | check-gate.sh P6 证据检查 | scripts/check-gate.sh | 5 分钟 |

**总计**：8 项动作，约 31 分钟。
