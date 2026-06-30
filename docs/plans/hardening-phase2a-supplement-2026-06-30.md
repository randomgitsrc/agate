# Phase 2A 补充实施计划：P2.15 .state.yaml 格式校验

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成 Phase 2A 的 .state.yaml 格式校验（P2.15），防止 Agent 写出不符协议的状态文件导致 hook 静默失效。P2.6（修复后全量重跑验证）经评审移除——hook 无法验证 full run vs partial run，属于流程层规则。

**Architecture:** Python 脚本校验 .state.yaml 必填字段、retries 列表结构、phase 合法值，集成进 pre-commit hook（PROD_TOUCHED 检测之后、状态转移检查之前）。

**Tech Stack:** Bash（hook 集成）、Python（格式校验）

**来源**：
- `docs/hardening-roadmap.md` Phase 2A
- 前轮对话确认：.state.yaml 格式校验应加到 Phase 2A
- 评审修订：P2.6 移除（语义错误），M1（保留 stderr），M2（环境变量传参）

---

## 文件结构

| 文件 | 责任 | 创建/修改 |
|------|------|-----------|
| `scripts/check-state-yaml.sh` | .state.yaml 格式校验 | 创建 |
| `scripts/pre-commit-gate.sh` | 集成格式校验 | 修改 |
| `docs/hardening-roadmap.md` | P2.15 状态更新 + P2.6 标记移除 | 修改 |

---

## Task 1: check-state-yaml.sh 格式校验脚本

**Files:**
- Create: `scripts/check-state-yaml.sh`

**协议依据**（`state-machine.md:412-443`）：
```yaml
task_id: T001          # 必填，格式 T + 数字
phase: P4              # 必填，合法值：P0-P8, PAUSED, READY, DONE
status: in_progress    # 必填
retries:               # 必填，retries[Pn] 必须是列表
  P2: []               # key 必须大写 P + 数字
```

- [ ] **Step 1: 写 check-state-yaml.sh**

```bash
#!/usr/bin/env bash
# check-state-yaml.sh — .state.yaml 格式校验（P2.15）
# 检查 .state.yaml 是否符合 state-machine.md 协议模板
# exit 0 = 格式正确; exit 1 = 格式错误; exit 2 = 无 .state.yaml

set -euo pipefail

STATE_FILE="${1:?用法: check-state-yaml.sh STATE_FILE}"

[ ! -f "$STATE_FILE" ] && exit 2

# 用环境变量传参，避免 shell 变量注入 Python 代码（M2 修复）
# 2>&1 保留 stderr，让 YAML 解析错误信息可见（M1 修复）
ERRORS=$(STATE_FILE="$STATE_FILE" python3 -c "
import yaml, sys, re, os

state_file = os.environ['STATE_FILE']
valid_phases = 'P0 P1 P2 P3 P4 P5 P6 P7 P8 PAUSED READY DONE'.split()

with open(state_file) as f:
    data = yaml.safe_load(f)

errors = []

if data is None:
    errors.append('文件为空')
    print('\n'.join(errors))
    sys.exit(0)

# 必填字段
for field in ('task_id', 'phase', 'status'):
    if field not in data:
        errors.append(f'缺必填字段: {field}')

# task_id 格式：T + 数字
task_id = data.get('task_id', '')
if task_id and not re.match(r'^T\d+$', str(task_id)):
    errors.append(f'task_id 格式错误: {task_id}（应为 T + 数字，如 T001）')

# phase 合法值
phase = str(data.get('phase', ''))
if phase and phase not in valid_phases:
    errors.append(f'phase 非法值: {phase}（合法值: {\" \".join(valid_phases)}）')

# retries 必须是 dict，且每个值是列表
retries = data.get('retries', {})
if retries:
    if not isinstance(retries, dict):
        errors.append(f'retries 应为 dict，实际为 {type(retries).__name__}')
    else:
        for key, val in retries.items():
            if not re.match(r'^P\d+$', str(key)):
                errors.append(f'retries key 格式错误: {key}（应为大写 P + 数字，如 P2）')
            if not isinstance(val, list):
                errors.append(f'retries[{key}] 应为列表，实际为 {type(val).__name__}')

if errors:
    print('\n'.join(errors))
" 2>&1 || true)

if [ -n "$ERRORS" ]; then
    echo "GATE STATE-YAML: .state.yaml 格式错误：" >&2
    echo "$ERRORS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  - $line" >&2
    done
    exit 1
fi

exit 0
```

- [ ] **Step 2: 验证语法**

Run: `bash -n scripts/check-state-yaml.sh`
Expected: 无输出

- [ ] **Step 3: 测试合法格式**

```bash
cat > /tmp/test-state-valid.yaml <<'EOF'
task_id: T001
phase: P5
status: in_progress
retries:
  P2:
    - round: 1
      failure_mode: quality
      prompt_changed: false
      adjustment: null
  P4: []
EOF
bash scripts/check-state-yaml.sh /tmp/test-state-valid.yaml
echo "exit: $?"
```

Expected: `exit: 0`

- [ ] **Step 4: 测试非法格式（缺字段 + retries 非列表 + 非法 phase）**

```bash
cat > /tmp/test-state-invalid.yaml <<'EOF'
task_id: invalid
phase: P99
status: in_progress
retries:
  p2: 3
EOF
bash scripts/check-state-yaml.sh /tmp/test-state-invalid.yaml 2>&1
echo "exit: $?"
```

Expected: exit 1，输出含 "task_id 格式错误"、"phase 非法值"、"retries key 格式错误"、"retries[p2] 应为列表"

- [ ] **Step 5: 测试 YAML 语法错误（M1：错误信息应可见）**

```bash
cat > /tmp/test-state-bad-yaml.yaml <<'EOF'
task_id: T001
phase: P5
  bad: indent
EOF
bash scripts/check-state-yaml.sh /tmp/test-state-bad-yaml.yaml 2>&1
echo "exit: $?"
```

Expected: exit 1，输出含 YAML 解析错误信息（不是泛泛的"YAML 解析失败"）

- [ ] **Step 6: Commit**

```bash
git add scripts/check-state-yaml.sh
git commit -m "feat(hardening): check-state-yaml.sh 格式校验

P2.15 .state.yaml 必填字段 + retries 列表结构 + phase 合法值检查
M1: 保留 YAML 解析错误信息
M2: 环境变量传参避免 shell 注入"
```

---

## Task 2: 集成进 pre-commit-gate.sh

**Files:**
- Modify: `scripts/pre-commit-gate.sh`

- [ ] **Step 1: 在 PROD_TOUCHED 检测之后、状态转移检查之前插入格式校验**

在 `pre-commit-gate.sh` 的 `# 3. 状态转移检查` 之前插入：

```bash
# 2.5 .state.yaml 格式校验（P2.15）
if [ -f "$STATE_FILE" ]; then
    bash "$REPO_ROOT/scripts/check-state-yaml.sh" "$STATE_FILE" || exit 1
fi
```

修改后的步骤顺序：
```
0. 检测触发条件
1. 读取状态
2. PROD_TOUCHED 检测
2.5 .state.yaml 格式校验（新增）
3. 状态转移检查
4. 运行 gate + write_gate_result
5. CHANGELOG 检查
6. P6 证据格式检查
7. gate 结果处理
```

- [ ] **Step 2: 验证语法**

Run: `bash -n scripts/pre-commit-gate.sh`
Expected: 无输出

- [ ] **Step 3: 测试格式校验集成——合法格式不拦截**

```bash
cat > .state.yaml <<'EOF'
task_id: T001
phase: P5
status: in_progress
retries:
  P5: []
EOF
git add -f .state.yaml
git commit -m "test: 合法 .state.yaml 不应被格式校验拦截" 2>&1
```

Expected: 格式校验通过，进入 gate 执行（可能 exit 2 需主 Agent 判断，但不是格式错误）

- [ ] **Step 4: 测试格式校验集成——非法格式被拦截**

```bash
cat > .state.yaml <<'EOF'
task_id: invalid
phase: P99
retries:
  p2: 3
EOF
git add -f .state.yaml
git commit -m "test: 非法格式应被拦截" 2>&1
```

Expected: commit 被中止，输出 "GATE STATE-YAML: .state.yaml 格式错误"

- [ ] **Step 5: 清理测试文件**

```bash
rm -f .state.yaml .gate-result.json
git add -A
git commit -m "test: 清理 P2.15 集成测试文件"
```

- [ ] **Step 6: Commit**

```bash
git add scripts/pre-commit-gate.sh
git commit -m "feat(hardening): pre-commit-gate.sh 集成 P2.15 格式校验

在 PROD_TOUCHED 检测之后、状态转移检查之前
校验 .state.yaml 必填字段 + retries 列表 + phase 合法值"
```

---

## Task 3: 更新 roadmap 状态

**Files:**
- Modify: `docs/hardening-roadmap.md`

- [ ] **Step 1: 更新 2A 表格**

将 P2.3-P2.5 的状态从"待实现"改为"已实现"。
将 P2.6 标记为"移除（评审：hook 无法验证 full run vs partial run）"。
追加 P2.15 行。

- [ ] **Step 2: Commit**

```bash
git add docs/hardening-roadmap.md
git commit -m "docs: roadmap 2A 状态更新

P2.3-P2.5: 已实现
P2.6: 移除（评审：hook 无法验证 full run，属流程层规则）
P2.15: 已实现（.state.yaml 格式校验）"
```

---

## 完成标准

- [ ] check-state-yaml.sh 落地，校验 .state.yaml 必填字段 + retries 列表结构 + phase 合法值
- [ ] YAML 解析错误信息可见（不是泛泛"解析失败"）
- [ ] 格式校验集成进 pre-commit-gate.sh（PROD_TOUCHED 之后、状态转移之前）
- [ ] 合法格式不拦截
- [ ] 非法格式被拦截
- [ ] roadmap 2A 状态更新
