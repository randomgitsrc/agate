---
phase: P4
task_id: TAG0004-env-adaptation
type: implementation
parent: P2-design.md
trace_id: TAG0004-P4-20260813
status: draft
created: 2026-08-13
agent: implementer
---

implementation_dir: agate/scripts/

# P4 实现记录 — 组 1（sh gate 脚本组）

## 范围

本组负责 5 个 sh 脚本的修复（dispatch-context 组 1 文件清单），让 P3 对应 BDD 红灯变绿（不改测试）：

| 缺陷组 | BDD | 文件:位置 | 方案（P2 选定） |
|-------|-----|----------|----------------|
| S1 | BDD-1/2/3/4 | `pre-commit-gate.sh:50/57/339/343/350` | STAGED_STATE_FILES / PROCESSED_DIRS 数组化（候选 1A） |
| M9 | BDD-17 | `pre-commit-gate.sh:102/133/228` | grep -E 拼路径 → awk 行首字面前缀 + 正则过滤固定段（候选 6A） |
| 其他-b | BDD-19 | `install-hook.sh` 复制模式 + `pre-commit-gate.sh:26` | 复制模式写 `.agate-root` 标记 + readlink 失败读标记兜底（候选 14A） |
| M4 | BDD-11 | `check-gate.sh:356/357` | `[:：]?` bracket → alternation `(:|：)?`（候选 4A） |
| RM-AG0001 | BDD-28/29 | `check-gate.sh:69/71/89/109/125/129` | 行首标记正则加可选反引号前缀（候选 10A） |
| M5 | BDD-12/13 | `check-p6-format.sh:69` | 4 处 sed `[[:space:]:：]` bracket → alternation（与 L84 v0.40.3 统一，候选 4A） |
| S2 | BDD-9/10 | `check-p6-evidence.sh:37` | 证据引用正则负类加宽（候选 3A） |

## 实现细节

### S1 — STAGED_STATE_FILES / PROCESSED_DIRS 数组化

- `STAGED_STATE_FILES=""` → `STAGED_STATE_FILES=()`；收集处 `+=("$REPO_ROOT/$f")`（L53-58）
- 消费处 `for STATE_FILE in $STAGED_STATE_FILES` → `for STATE_FILE in "${STAGED_STATE_FILES[@]}"`（L65，§3 L351）
- `PROCESSED_DIRS=""` → `PROCESSED_DIRS=()` + `+=("$STATE_DIR")`（L349）
- `case " $PROCESSED_DIRS "` 成员判断 → 新增辅助函数 `is_processed_dir`（数组遍历精确 `=` 比对，L355-363）
- 环境确认：bash 5.2.21 下空数组 `${arr[@]}` 在 `set -u` 下安全（实测通过）；两处循环均有 `()` 初始化兜底

### M9 — grep -E 拼路径改 awk 字面前缀（候选 6A）

`^${TASK_REL}/P[0-8]-.*\.md$` 与 `^${TASK_REL}/` 前缀模式统一改为两级过滤：

```bash
... | awk -v p="${TASK_REL}/" 'index($0, p) == 1' | grep -E 'P[0-8]-.*\.md$'
```

- `awk 'index($0, p) == 1'` 保留行首锚定语义（防中段误匹配）+ `-v` 字面传入（免疫正则元字符）
- 覆盖 L102（STAGED_OUTPUTS）/L104（STAGED_ADDED）/L133（PROD_TOUCHED 前缀）/L228（STAGED_IN_TASK）/L290（STAGED_OUTPUT_IN_TASK）
- `[SCOPE+]` L290（2n.1 分支）与 L104 为审计清单 L102/133/228 之外的同缺陷模式（`^${TASK_REL}` 拼入 grep -E），为防同一文件留下同类静默绕过点，一并按同方案改造

### 其他-b — 复制模式 AGATE_ROOT 兜底（候选 14A）

- `install-hook.sh`：`ln -sf` 后 `[ ! -L "$HOOK_FILE" ]`（复制模式）时写 `printf '%s\n' "$AGATE_ROOT" > "$HOOK_DIR/.agate-root"`（L39）
- `pre-commit-gate.sh:26` 后：`$AGATE_ROOT/scripts` 不存在且 hook 所在目录有 `.agate-root` 时，读标记恢复（`tr -d '\r'` 防 Windows CRLF 残留）

### M4 — check-gate.sh P7 全角冒号（候选 4A）

- `[BLOCKER\][:：]?` → `[BLOCKER\](:|：)?`；`[DEVIATION-CRITICAL\][:：]?` → `[DEVIATION-CRITICAL\](:|：)?`（L358/359）

### RM-AG0001 — check-gate.sh P1 反引号容错（候选 10A）

- 行首标记正则 `^\s*-?\s*\[` → `^\s*`*-?\s*`*\[`（L69/71/89/109/129）
  - P3 测试实际形态为 `- `[NEED_CONFIRM]` z...`（dash 前缀之后才是反引号），故在 `-?\s*` 之后也加 `*`（可选反引号），两处均容错
- sed 描述提取同步加反引号剥离：`s/^\s*`*-?\s*`*\[SUGGEST:[[:space:]]*//; s/`[[:space:]]*$//; s/\]\s*$//`（L109）
- L125 无需改：其 grep `\[NEED_CONFIRM\]` 为行中无锚点匹配，反引号不阻断；计数修复后 `NC_BLOCKING>0` 使该"不合规格式"分支短路跳过

### M5 — check-p6-format.sh:69 全角冒号（候选 4A）

- 4 处 sed `([[:space:]:：]|$)` → `([[:space:]]|:|：|$)`（保持 group 3 编号与 `\3` 回写不变）

### S2 — check-p6-evidence.sh:37 中文文件名（候选 3A）

- `\([a-zA-Z0-9_/. -]*[a-zA-Z0-9_-]\.[a-zA-Z0-9]+[^)]*\)` → `\([^()]*[^()[:space:]]\.[a-zA-Z0-9]+[^)]*\)`
- 维持"文件名+扩展名"结构：`[^()[:space:]]\.` 保证扩展名前至少一个非空格非括号字符（BDD-10 `(见截图)` 仍拒绝）

## 自查结果（自查 ≠ P5 gate）

| 检查项 | 结果 |
|--------|------|
| `bats agate/tests/unit/check-p6-evidence.bats` | 全绿（含 bdd-9/10） |
| `bats agate/tests/unit/check-p6-format.bats` | 全绿（含 bdd-12/13） |
| `bats agate/tests/unit/check-gate.bats` | 117 例仅 bdd-14（M6 CRLF，组 2/3 范围）红，bdd-11/28/29 全绿 |
| `bats agate/tests/integration/pre-commit-hook.bats` | 48 例全绿（含 bdd-1/2/3/4/17/19） |
| `bats agate/tests/unit/`（全量） | 607 例，剩余 9 红全属组 2/3 范围（Q1/其他-c/S3/其他-a/M6/Q2/Q5/CI），本组 0 红 |
| `bats agate/tests/regression/` | 17 例全绿（无回归） |
| `bats agate/tests/sanity.bats` | 6 例全绿 |
| `shellcheck -S warning` 5 脚本 | 0 error |

## 范围外说明（组 2/3 负责，非本组缺口）

- **bdd-14（M6 CRLF frontmatter）**：check-gate.sh P1/P2 的 `sed -n '/^---$/...'` frontmatter 提取 CRLF 容错——未列入本组 BDD 清单，属 M6 跨组修复（py + sh 入口），不在本组文件职责内。标注 `[SCOPE_GAP: dispatch-context 组 1 BDD 清单不含 M6/bdd-14，check-gate.sh CRLF frontmatter 提取容错未实现——由负责 M6 的组补齐]`。
- 其余 8 条红灯（bdd-5/18/20/21/23/26/27/33）分属组 2/组 3 文件，非本组范围。

## 未触发项

- 无 [DESIGN_GAP]（P2 方案实现无歧义/缺口自主决策）。
- `[PROD_NOT_TOUCHED]` 本阶段仅改 worktree `agate/scripts/` 下 5 个 sh 并跑 bats/shellcheck，未接触任何生产环境。
