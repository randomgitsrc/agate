---
task_id: agate-audit-fixes-D
agent: main
date: 2026-07-02
status: 设计文档（已修订 v2，评审修订已纳入）
来源: docs/plans/agate-audit-fixes-2026-07-01.md §D + docs/reviews/agate-audit-fixes-plan-review-2026-07-01.md §D
---

# D 组设计：门槛表对齐修复（4 项）

## 变更清单

| # | 问题 | 修改文件 | 修改类型 |
|---|------|----------|----------|
| #12 | P1 门槛过度保守（有可脚本化 grep 但完全 exit 2） | — | 不修（已知局限） |
| #13 | P2 门槛错位：脚本查候选方案≥2，文档查 status:approved + 四字段 | check-gate.sh + dispatch-protocol.md | 脚本+文档 |
| #6 | P4 路径偏离：文档写"P4-implementation/ 下文件非空"，脚本查暂存区 | dispatch-protocol.md | 文档 |
| #16 | P4 文档滞后：门槛表写 git log，脚本用 --cached | dispatch-protocol.md | 文档 |

## 详细设计

### #12 P1 门槛不实现

**决策**：不修。P1 gate 设计为 exit 2（BDD 编号格式不固定），实现 grep 检查改动大且影响主 Agent 判断流程。文档的 grep 命令仍列在门槛表里供主 Agent 手动执行。

### #13 P2 门槛对齐

**现状**：
- 脚本 check-gate.sh P2 case 查候选方案 ≥2（v0.6 加的多方案探索），文档门槛表没列
- 文档门槛表（dispatch-protocol.md:577）列 `grep 'status: approved' P2-review.md` + 四字段计数，脚本没查
- 评审修订（D.2）：status:approved 应查 P2-review.md（评审结论），不是 P2-design.md（设计方案）

**决策**：同步文档和脚本。

**改动**：

1. **check-gate.sh P2 case**（在 C#10 form check 之前插入 status:approved + 四字段检查）：
```bash
# 在 CANDIDATE_COUNT >= 2 通过后、form check 之前加：
P2_REVIEW="$TASK_DIR/P2-review.md"
if [ -f "$P2_REVIEW" ]; then
    if ! grep -qE 'status:\s*approved' "$P2_REVIEW" 2>/dev/null; then
        echo "GATE P2: P2-review.md 缺 status: approved" >&2
        exit 1
    fi
fi
FIELD_COUNT=$(grep -cE '^(packages|domains|ui_affected|gate_commands):' "$P2_FILE" 2>/dev/null || echo 0)
FIELD_COUNT=$(echo "$FIELD_COUNT" | tail -1)
if [ "$FIELD_COUNT" -lt 4 ]; then
    echo "GATE P2: P2-design.md 缺字段（需 packages/domains/ui_affected/gate_commands 四字段，实际 ${FIELD_COUNT}）" >&2
    exit 1
fi
```

放置顺序（C+D 合并后）：count check → status:approved → 四字段 → form check → exit 2

2. **dispatch-protocol.md:577**（补"候选方案≥2"到门槛表，评审修订：`=4`→`≥4`，补 form check 判定命令）：
```markdown
# 当前：
| P2→P3 | 方案已批准 | `grep 'status: approved' P2-review.md` → 命中 + `grep -cE '^(packages\|domains\|ui_affected\|gate_commands):' P2-design.md → =4` |

# 改为：
| P2→P3 | 方案已批准 | `grep 'status: approved' P2-review.md` → 命中 + `grep -cE '^(packages\|domains\|ui_affected\|gate_commands):' P2-design.md → ≥4` + `grep -qE '权衡\|选择理由' P2-design.md` → 命中 + 候选方案 ≥2（`scripts/check-gate.sh P2` 脚本化部分）|
```

### #6 P4 路径偏离：改文档

**现状**：dispatch-protocol.md:579 写"P4-implementation/ 下文件非空"，脚本 check-gate.sh:40 查"暂存区有非 md/yaml 文件"（`git diff --cached`）。脚本更适合 pre-commit 场景。

**决策**：改文档对齐脚本。

**改动**：
```markdown
# dispatch-protocol.md:579
# 当前：P4-implementation/ 下文件非空 + `git log --oneline -1` → 含 "P4" 或 "wf(Txxx-P4)"
# 改为：暂存区含非 md/yaml 文件（`git diff --cached --name-only | grep -qvE '\.(md|yaml)$|^\.state'`）
```

### #16 P4 git log → --cached

**现状**：dispatch-protocol.md:579 写 `git log --oneline -1`，脚本用 `git diff --cached`。pre-commit 时 commit 还没创建，git log 查不到。

**决策**：改文档。与 #6 合并修改。

**改动**：已在 #6 中一并修改（去掉 git log，改为 --cached）。

## 测试计划

### check-gate.bats 新增

| ID | 描述 | 期望 |
|----|------|------|
| G2.10 | P2 有候选方案 + 权衡 + 四字段，但 P2-review.md 无 status:approved | exit 1，含"status: approved" |
| G2.11 | P2 有候选方案 + 权衡 + 四字段 + P2-review.md 有 status:approved | exit 2（happy path） |
| G2.12 | P2-design.md 缺字段（<4） | exit 1，含"缺字段" |
| G2.13 | P2 有候选方案 + 权衡 + 四字段，无 P2-review.md | exit 2（评审修订补充：隐藏依赖 #2 测试覆盖） |

### check-gate.bats 修改（变红测试同步更新）

| ID | 变更 |
|----|------|
| G2.3 | P2-design.md 需补四字段（packages/domains/ui_affected/gate_commands） |
| G2.6 | 同上 |
| G2.7 | 同上 |
| G2.8 | 同上（评审修订补充：G2.8 也缺四字段） |
| G2.9 | 同上 |

注：所有 P2 测试 fixture 的 P2-design.md 都必须包含四字段，否则会在四字段检查 exit 1。

## 隐藏依赖

1. **G2.3/G2.6/G2.7/G2.9 会变红**：加四字段检查后，这些测试的 P2-design.md 缺四字段会 exit 1。必须同步更新。
2. **P2-review.md 不存在时放行**：status:approved 检查只在 P2-review.md 存在时执行。P2-review.md 不存在（如 P2 刚完成还没评审）→ 跳过 status 检查 → 只查 count + 四字段 + form → exit 2。这是合理的——评审文件可能还没创建。
3. **四字段计数用 `≥` 不用 `=`**：允许 P2-design.md 有额外字段（如 env_constraints、files_to_read 等）。文档写 `=4` 是最小要求，脚本用 `< 4` 拦截不足 4 个的情况。
