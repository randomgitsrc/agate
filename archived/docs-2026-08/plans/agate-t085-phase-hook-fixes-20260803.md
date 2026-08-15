# T085 复盘：phase 时机 + P3 gate 分离 + 防篡改留痕 + gitignore + P2 正则 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 T085 复盘暴露的 4 个 agate 根因问题：phase 写入时机歧义、check-gate.sh P3 跑测试超时、.state.yaml 被 gitignore 忽略、P2 候选方案正则不匹配 ####。核心变更：P3 红灯检查从 check-gate.sh 分离，hook 永远自己跑 check-gate.sh（结果不可伪造），CI backstop 兜底红灯检查。

**Architecture:** 方案 E——**hook 永远自己跑 check-gate.sh（写真实 .gate-result.json，agent 无法伪造），check-gate.sh P3 从 exec check-tdd-red.sh 改为文件存在性检查（秒级不超时）**。check-tdd-red.sh 独立运行：主 Agent 手动确认红灯 + CI backstop 在 P3 时额外跑。防篡改的本质：hook 自己跑的结果不可伪造，agent 能做的只有 --no-verify 绕过（此时 .gate-result.json 不存在 → CI backstop 检测到）。

**Tech Stack:** Bash, Python 3, Markdown, Bats

---

## 背景

### 问题（T085 复盘）

1. **phase 写入时机在卡片间不一致**：P1/P2 说"预跑 gate → 更新 state"（隐含 commit 前），P3/P5 说"commit → 更新 state"（commit 后），P4/P6/P7 说"预跑 gate → commit → 更新 state"。state-machine.md L445 说"一次 commit 包含 stage output + .state.yaml 更新"——与 P3/P5 矛盾。

2. **check-gate.sh P3 跑测试超时 → --no-verify 8 次**：hook L153 调用 check-gate.sh，P3 分支 `exec check-tdd-red.sh` 真实跑测试命令 → 慢 → hook 超时 → 主 Agent 用 --no-verify 绕过**全部**检查。

3. **.state.yaml 被 .gitignore 忽略**：agate 仓库根 .gitignore 忽略 .state.yaml。项目侧可能复制。`git add docs/tasks/{Txxx}/` 不暂存 .state.yaml → hook 不触发 → gate 被跳过。文档从未说 git add -f。

4. **P2 候选方案正则只匹配 2-3 个 #**：check-gate.sh L87 正则 `^###?\s*` 不匹配 `####`(4)。

### 为什么方案 E（hook 永远自己跑 check-gate.sh）优于方案 D（hook 跳过 check-gate.sh）

用户要求"gate 被验证通过"要留痕且防篡改。方案 D 的缺陷：
- hook 不跑 check-gate.sh → 写假 .gate-result.json（exit_code=2 硬编码）→ 无法做"recorded vs ci"比对
- 不能证明"gate 被验证通过"

方案 E 的防篡改原理：
- **hook 永远自己跑 check-gate.sh** → .gate-result.json 是 hook 运行的真实副产品 → agent 不参与 hook 执行，无法伪造
- agent 能做的只有 --no-verify 绕过（hook 不跑 → .gate-result.json 不存在）
- 密钥方案不可行：agent 有文件系统访问权限，任何密钥都能读到。真正防篡改是"验证不由 agent 执行"。

### .gate-result.json 的 CI 策略（明确设计）

`.gate-result.json` 在 .gitignore 中，CI 用 actions/checkout 全新检出 → **CI 读不到本地 .gate-result.json**。这不是缺陷，是设计：

| 场景 | .gate-result.json | CI 行为 |
|------|------------------|---------|
| 正常 commit | hook 写真实结果（本地留痕） | CI 全新检出无此文件 → 走 WARN 分支 → 独立重跑 check-gate.sh（核心兜底） |
| --no-verify | 不存在 | CI 无此文件 → WARN → 独立重跑 check-gate.sh |
| 伪造 .gate-result.json | agent 手写 | **CI 不读本地文件**，只重跑真实 check-gate.sh → 伪造无意义 |

**核心**：CI 永远独立重跑 check-gate.sh（从干净检出），这是真正的兜底。.gate-result.json 是本地留痕（给主 Agent 看 + 记录 hook 运行），"recorded vs ci" 比对在 .gate-result.json 通过 artifact 上传到 CI 时才生效——这是可选增强，不是核心防篡改机制。

**防篡改的本质**：agent 无法伪造 CI 的独立验证（CI 从干净环境跑真实 check-gate.sh）。agent 能做的只有 --no-verify 让 hook 不跑，但 CI 仍然重跑。

### 不修

| 问题 | 理由 |
|------|------|
| P2.62 E2E 断言矛盾盲区 | P3 不能跑 E2E（太重），P5 会暴露。1 条/任务损耗可接受 |

---

## 文件结构

### 修改文件

| 文件 | 改动 |
|------|------|
| `agate/scripts/check-gate.sh` | P3 分支 exec check-tdd-red.sh → 文件存在性检查（Task 2） |
| `agate/scripts/check-gate.sh` | P2 正则 `^#{2,4}\s*`（Task 4） |
| `agate/scripts/check-state-transition.sh` | 删除检查 3 pre-phase-change commit gate（Task 1） |
| `agate/scripts/ci-gate-backstop.py` | P3 时额外跑 check-tdd-red.sh 兜底红灯（Task 2） |
| `agate/scripts/install-hook.sh` | 检测 .gitignore 中 .state.yaml 忽略（Task 3） |
| `agate/phase-cards/P1-requirements.md` ~ `P7-consistency.md` | 统一 phase 时机（Task 1） |
| `agate/phase-cards/P3-tdd.md` | gate 规则说明更新（Task 2） |
| `agate/state-machine.md` | phase 时机 + P3 gate 描述更新（Task 1+2） |
| `agate/git-integration.md` | git add 含 .state.yaml + -f 说明 + L31 规则更新（Task 1+3） |
| `agate/WORKFLOW.md` | P3 gate 表更新（Task 2） |
| `agate/tests/unit/check-gate.bats` | G3 测试适配 + G2.25 正则测试（Task 2+4） |
| `agate/tests/unit/check-state-transition.bats` | ST.17 反转 + ST.18 改写（Task 1） |
| `agate/tests/integration/pre-commit-hook.bats` | hook 跑 check-gate.sh 测试（Task 2） |
| `agate/tests/unit/ci-gate-backstop.bats` | CI backstop P3 兜底测试（Task 2） |
| `docs/hardening-roadmap.md` | 状态更新（Task 5） |

---

## Task 1: 统一 phase 更新时机（文档 + 脚本 + 测试）

**Files:**
- Modify: 7 个阶段卡片 + state-machine.md + git-integration.md
- Modify: `agate/scripts/check-state-transition.sh`（删除检查 3 pre-phase-change commit gate）
- Modify: `agate/tests/unit/check-state-transition.bats`（ST.16-ST.18 适配）
- Add: `agate/tests/unit/check-state-transition.bats`（ST.21 同一 commit 测试）

### 背景：当前矛盾

state-machine.md L445 写的是模式 B（"一次 commit 包含 stage output + .state.yaml 更新"），但 check-state-transition.sh 检查 3（L106-155）强制模式 A（"产出和推进不能同一个 commit"）。文档和脚本从根上不一致。P3/P5 卡片用模式 A，P6/P7 用模糊的合并表述，P1/P2 缺 commit 步骤。本 Task 统一为模式 B 并修复脚本。

### 统一规则

**先更新 .state.yaml phase → 再 git add（含 .state.yaml + 产出）→ 再 git commit。**

state.yaml 和产出在同一个 commit 里（符合 state-machine.md L445 现有设计）。

主 Agent 步骤模板（所有阶段统一）：
```
N. 预跑 check-gate.sh P{N}（确认 gate 通过/exit 2）
N+1. 更新 .state.yaml phase=P{N} → P{N+1}
N+2. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
N+3. git commit -m "wf({Txxx}-P{N}): {摘要}"
```

**commit 失败时的回退**：如果 hook 拦截 commit（gate FAIL），.state.yaml 工作区已是 P{N+1} 但 commit 未成功。agent 需修好问题后重新 commit——不需要手动改回 phase。原因：hook 跑的是 check-gate.sh P{N+1}（新 phase 的 gate），只要 P{N+1} 产出合格，第二次 commit 会通过。如果 agent 需要回退到 P{N} 重做，按 state-machine.md 回退流程执行（改 phase + archive stale outputs）。

### Step 1: 更新各卡片步骤顺序

**P1-requirements.md**：当前"3. 预跑 check-gate.sh P1 → 4. 更新 .state.yaml phase=P1 → P2"（缺 commit 步骤）
改为：
```
3. 预跑 check-gate.sh P1（exit 2，主 Agent 自判）
4. 更新 .state.yaml phase=P1 → P2
5. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件）
6. git commit -m "wf({Txxx}-P1): {摘要}"
```

**P2-design.md**：当前"4. 预跑 check-gate.sh P2 → 5. 更新 .state.yaml phase=P2 → P3"（缺 commit 步骤）
改为：
```
4. 预跑 check-gate.sh P2（脚本化检查）
5. 更新 .state.yaml phase=P2 → P3
6. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件）
7. git commit -m "wf({Txxx}-P2): {摘要}"
```

**P3-tdd.md**：当前"2. 主 Agent 跑 check-tdd-red.sh → 3. git commit → 4. 更新 .state.yaml phase=P3 → P4"（模式 A）
改为：
```
3. 预跑 check-tdd-red.sh 确认红灯（exit 0 = 真红灯可推进）
4. 更新 .state.yaml phase=P3 → P4
5. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件）
6. git commit -m "wf({Txxx}-P3): {摘要}"
```

**P4-implementation.md**：当前"4. git add 代码文件 → git commit → 5. 预跑 check-gate.sh P4 → 6. 更新 .state.yaml phase=P4 → P5"（模式 A，gate 在 commit 后）
改为：
```
4. 预跑 check-gate.sh P4（确认暂存区有代码文件）
5. 更新 .state.yaml phase=P4 → P5
6. git add docs/tasks/{Txxx}/ + 代码文件（含 .state.yaml）
7. git commit -m "wf({Txxx}-P4): {摘要}"
```
L138 "写完代码不改 .state.yaml 就 commit" → "先更新 .state.yaml 再 commit（state 和产出在同一 commit）"

**P5-verification.md**：当前"4. git commit → 5. 更新 .state.yaml phase=P5 → P6"（模式 A）
改为：
```
4. 更新 .state.yaml phase=P5 → P6
5. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件）
6. git commit -m "wf({Txxx}-P5): {摘要}"
```

**P6-acceptance.md**：当前"7. git commit → 更新 .state.yaml phase=P6 → P7"（合并表述，不明确）
改为：
```
7. 更新 .state.yaml phase=P6 → P7
8. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件）
9. git commit -m "wf({Txxx}-P6): {摘要}"
```

**P7-consistency.md**：当前"5. git commit → 更新 .state.yaml phase=P7 → P8"（合并表述，不明确）
改为：
```
5. 更新 .state.yaml phase=P7 → P8
6. git add docs/tasks/{Txxx}/（含 .state.yaml + 产出文件）
7. git commit -m "wf({Txxx}-P7): {摘要}"
```

### Step 2: 更新 state-machine.md

L445 追加：
```
**phase 更新时机**：先更新 .state.yaml phase → 再 git add（含 .state.yaml + 产出文件）→ 再 git commit。state 和产出在同一个 commit 里。不要"先 commit 产出再单独 commit state"——两个 commit 会导致 hook 在第一个 commit 时读不到 phase 变更，在第二个 commit 时找不到产出文件。
```

### Step 3: 更新 git-integration.md

**L31** 当前："这个规则由 `check-state-transition.sh` 强制执行——推进 phase 到 Pn+1 前，Pn 产出必须已 commit，否则拦截。"
改为："这个规则由 `check-gate.sh` 强制执行——每个阶段的 gate 检查该阶段产出是否合格。产出和 .state.yaml phase 更新在同一个 commit 里。"

**L107-112** 单步函数改为：
```
    6.5. 更新 .state.yaml phase（先更新再 commit）
    7. git commit（规则 2：一阶段一 commit）
       git add docs/tasks/{task_id}/ docs/tasks/active-tasks.md
       （.state.yaml 在 docs/tasks/{task_id}/ 下。若项目 .gitignore 忽略 .state.yaml，需 git add -f）
       git commit -m "wf({task_id}-{phase}): {摘要}"
```

### Step 4: 删除 check-state-transition.sh 检查 3

**文件**：`agate/scripts/check-state-transition.sh`

删除 L106-155（检查 3：pre-phase-change commit gate）。原因：
- 检查 3 强制模式 A（产出和推进不能同一个 commit），与模式 B 直接冲突
- 检查 3 的"旧产出必须已 commit"检查不必要——check-gate.sh 会检查新 phase 的完成度，如果旧 phase 没产出，新 phase 的 gate 自然过不了
- 删除后，检查 4（回退时 self-authored 产出归档检查，L157-188）不受影响（检查 4 的 `diff` 变量来自检查 1，不依赖检查 3）

**注意**：检查 4 引用了检查 1 的 `diff` 变量（L73）。删除检查 3 后，`diff` 变量仍在检查 1（L72-78）中计算，检查 4 不受影响。

**已验证**：物理删除检查 3 后跑 `check-state-transition.bats` 全部 26 个测试，ST_ARCHIVE.1-6（检查 4 相关）全部通过，证实检查 4 对 `diff` 的依赖不受检查 3 删除影响。ST.17/ST.18 按预期失败（编码旧语义，Step 5 会改写）。

删除后检查 3 的注释也一并删除。检查 4 的注释保留（它仍独立有效）。

### Step 5: 更新 check-state-transition.bats 测试

**ST.16**（P1→P2 推进，P1 产出已 commit → exit 0）：保持不变（模式 B 下也是 exit 0）

**ST.17**（P1→P2 推进，P1 产出在暂存区未 commit → exit 1）：**反转语义**——改为 exit 0
```bash
@test "ST.17 commit gate: P1→P2 推进，P1 产出与 phase 推进在同一 commit → exit 0（模式 B）" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/tasks/T001"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    git -C "$repo" add docs/tasks/T001/.state.yaml
    git -C "$repo" commit -qm "T001 phase P1"
    # P1 产出 + phase 改 P2 在同一个暂存区（模式 B）
    echo "# P1 output" > "$repo/docs/tasks/T001/P1-requirements.md"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git -C "$repo" add docs/tasks/T001/
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' docs/tasks/T001/.state.yaml"
    [ "$status" -eq 0 ]
}
```

**ST.18**（P1→P2 推进，P1 产出从未 commit → exit 1）：**删除**——模式 B 下不再检查"产出是否已 commit"（那是 check-gate.sh 的职责）。但保留一个变体：P1→P2 推进，P1 产出文件根本不存在 → 仍然 exit 0（state-transition 不检查产出存在性，那是 gate 的事）
```bash
@test "ST.18 commit gate: P1→P2 推进，P1 产出不存在 → exit 0（产出存在性由 check-gate.sh 检查）" {
    local repo
    repo=$(git_init)
    mkdir -p "$repo/docs/tasks/T001"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P1
status: active
retries: {}
EOF
    git -C "$repo" add docs/tasks/T001/.state.yaml
    git -C "$repo" commit -qm "T001 phase P1"
    # 改 phase 到 P2，但 P1 产出从未创建
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    git_stage "$repo" "docs/tasks/T001/.state.yaml"
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-state-transition.sh' docs/tasks/T001/.state.yaml"
    [ "$status" -eq 0 ]
}
```

**ST.19**（PAUSED→P3 恢复 → 跳过 commit gate）：保持不变（PAUSED 恢复不触发检查 3，删除检查 3 后仍 exit 0）

**ST.20**（P3→P1 回退 → 跳过 commit gate）：保持不变（回退不触发检查 3，删除检查 3 后仍不触发）

### Step 6: Commit

```bash
git add agate/phase-cards/*.md agate/state-machine.md agate/git-integration.md \
       agate/scripts/check-state-transition.sh \
       agate/tests/unit/check-state-transition.bats
git commit -m "fix: unify phase update timing to state+output same commit (mode B)

- Update 7 phase cards: state update before commit, same commit includes output
- Delete check-state-transition.sh check 3 (pre-phase-change commit gate)
  - Was enforcing mode A (separate commits), conflicting with state-machine.md L445
  - check-gate.sh already validates new phase completeness
- Update ST.17: same commit now exit 0 (was exit 1)
- Update ST.18: output non-existence now exit 0 (gate's responsibility)
- Update git-integration.md L31: gate enforces, not state-transition"
```

---

## Task 2: check-gate.sh P3 分离 check-tdd-red.sh（核心）

**Files:**
- Modify: `agate/scripts/check-gate.sh` P3 分支
- Modify: `agate/scripts/ci-gate-backstop.py`
- Modify: `agate/phase-cards/P3-tdd.md`
- Modify: `agate/state-machine.md`
 - Modify: `agate/WORKFLOW.md`
- Modify: `agate/tests/unit/check-gate.bats`
- Modify: `agate/tests/integration/pre-commit-hook.bats`
- Modify: `agate/tests/unit/ci-gate-backstop.bats`

### 核心变更

**check-gate.sh P3 从 exec check-tdd-red.sh 改为文件存在性检查。**

当前：`exec "$SCRIPT_DIR/check-tdd-red.sh" "$TASK_DIR"`
改为：
```bash
  P3)
      # P3 gate：文件存在性检查（秒级）
      # T085 教训：exec check-tdd-red.sh 会真实跑测试命令 → hook 超时 → --no-verify 绕过全部检查
      # check-tdd-red.sh 独立运行：主 Agent 手动确认红灯 + CI backstop P3 时额外跑兜底
      P3_CASES="$TASK_DIR/P3-test-cases.md"
      if [ ! -f "$P3_CASES" ]; then
          echo "GATE P3: P3-test-cases.md 不存在——P3 产出文件缺失" >&2
          exit 1
      fi
      echo "GATE P3: P3-test-cases.md 存在。TDD 红灯由主 Agent 手动跑 check-tdd-red.sh 确认 + CI backstop P3 兜底。" >&2
      exit 2 ;;
```

### Step 1: 先写失败测试（check-gate.sh P3 行为变化）

在 `check-gate.bats` 中修改 G3 测试（当前测试"P3 委托 check-tdd-red.sh"）：

当前 G3（L367-387）：设置 TEST_RUNNER=fake_pytest，期望 check-gate.sh P3 → check-tdd-red.sh → exit 2。

改为验证新行为：
```bash
@test "G3 check-gate.sh P3 检查 P3-test-cases.md 存在（不跑测试）" {
    local dir
    dir=$(create_task_dir)
    # 无 P3-test-cases.md → exit 1
    run bash "$AGATE_SCRIPTS/check-gate.sh" P3 "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P3-test-cases.md 不存在"* ]]

    # 有 P3-test-cases.md → exit 2
    echo '## P3 test cases' > "$dir/P3-test-cases.md"
    run bash "$AGATE_SCRIPTS/check-gate.sh" P3 "$dir"
    [ "$status" -eq 2 ]
    [[ "$output" == *"check-tdd-red.sh"* ]]
}
```

先运行确认失败（当前 exec check-tdd-red.sh 会跑 fake_pytest → 不同行为）。

### Step 2: 修改 check-gate.sh P3 分支

按核心变更代码修改。

### Step 3: 修改 ci-gate-backstop.py — P3 时额外跑 check-tdd-red.sh

**插入位置（关键）**：在 main() 中 `ci_exit, ci_output = run_gate(phase, task_dir)` **这一行之后、`if not gate_result.exists():` 判断之前**插入 P3 检查代码。P3 检查必须在任何 `.gate-result.json` 存在性判断之前执行——因为 `--no-verify` 场景（`.gate-result.json` 不存在）正是 T085 复盘要覆盖的核心场景，如果放在函数末尾会重蹈现有 P6 provenance audit 的覆辙（那两段审计目前只在 `.gate-result.json` 校验通过后才执行，对 `--no-verify` 场景无效）。

在 main() 中 `ci_exit, ci_output = run_gate(phase, task_dir)` 之后、`if not gate_result.exists():` 之前插入：
```python
    if phase == "P3":
        # P3 红灯检查独立跑（check-gate.sh P3 只检查文件存在）
        # 必须在 .gate-result.json 存在性判断之前执行——
        # --no-verify 场景（无 .gate-result.json）正是 P3 兜底要覆盖的核心场景
        # check-tdd-red.sh exit 语义：
        #   0 = 真红灯（符合 TDD）→ 通过
        #   1 = 假红灯（测试代码自身 bug）→ FAIL
        #   2 = 绿灯（实现先于测试，违反 TDD）→ FAIL
        #   3 = 无测试运行器 → WARN（CI 环境可能未装测试框架，主 Agent 已手动确认过红灯）
        tdd_script = Path(os.environ.get("AGATE_TDD_RED_SCRIPT", str(_AGATE_ROOT / "scripts/check-tdd-red.sh")))
        if tdd_script.exists():
            tdd_result = subprocess.run(
                ["bash", str(tdd_script), task_dir],
                capture_output=True, text=True
            )
            tdd_exit = tdd_result.returncode
            tdd_output = tdd_result.stderr + tdd_result.stdout
            if tdd_exit == 0:
                print(f"OK: P3 check-tdd-red.sh exit=0（真红灯，符合 TDD）")
            elif tdd_exit == 2:
                print(f"FAIL: P3 check-tdd-red.sh exit=2（绿灯，实现先于测试，违反 TDD）")
                print(tdd_output)
                return 1
            elif tdd_exit == 1:
                print(f"FAIL: P3 check-tdd-red.sh exit=1（假红灯，测试代码自身有 bug）")
                print(tdd_output)
                return 1
            else:
                print(f"WARN: P3 check-tdd-red.sh exit={tdd_exit}（无测试运行器，CI 环境可能未装测试框架——主 Agent 已手动确认过红灯）")
        else:
            print("WARN: check-tdd-red.sh 不存在，P3 红灯检查跳过")
```

**exit 语义总结**（写入代码注释）：
- 0 → 通过（真红灯）
- 1 → FAIL（假红灯，测试代码 bug）
- 2 → FAIL（绿灯，违反 TDD）
- 3 或其他 → WARN（无运行器，CI 未装测试框架——主 Agent 已手动确认）

### Step 4: 更新文档（P3-tdd.md + state-machine.md + WORKFLOW.md）

**P3-tdd.md** gate 规则节（L39-50）当前写：
```
## gate 规则（check-tdd-red.sh）
check-tdd-red.sh $TASK_DIR
- exit 0：真红灯...
- exit 1：假红灯...
- exit 2：绿了...
- exit 3：无可用测试运行器
**技术栈无关**：check-tdd-red.sh 通过 formatter...
**探测链**：$TEST_RUNNER → gate_commands.P3 → which pytest → exit 3...
**formatter 选择**：...
```

改为：
```
## gate 规则

**check-gate.sh P3**（hook + 主 Agent 预跑，秒级文件检查）：
- exit 1：P3-test-cases.md 不存在
- exit 2：P3-test-cases.md 存在（TDD 红灯由 check-tdd-red.sh 独立确认）

**check-tdd-red.sh**（主 Agent 手动确认红灯 + CI backstop P3 兜底）：
- exit 0：真红灯（assertion 失败 / 项目内 import 失败 = B类错误）— 测试正确但因实现未写而失败
- exit 1：假红灯（SyntaxError / 第三方 import 失败 = A类错误）— 测试代码自身错误
- exit 2：绿了 — 实现先于测试，违反 TDD
- exit 3：无可用测试运行器

**技术栈无关**：check-tdd-red.sh 通过 formatter 将测试输出标准化为 JSON...
**探测链**：$TEST_RUNNER → gate_commands.P3 → which pytest → exit 3...
**formatter 选择**：见 assets/formatters/README.md 速查表...
```

**state-machine.md**：
- L90 `P3 --[scripts/check-tdd-red.sh exit 0 AND assertion_failures>0 AND collection_errors==0]--> P4` 追加说明"check-gate.sh P3 只检查文件存在，红灯由主 Agent 手动跑 check-tdd-red.sh + CI backstop 兜底确认"
- L274-278 的"判定方式：主 Agent 跑 scripts/check-tdd-red.sh"保留，追加"check-gate.sh P3 只检查 P3-test-cases.md 存在"

**WORKFLOW.md** L219 P3 gate 表：
当前：`| P3 | 测试设计 | test-designer | gate 自检（TDD 红灯）| scripts/check-tdd-red.sh exit 0 |`
改为：`| P3 | 测试设计 | test-designer | gate 自检（文件存在）+ TDD 红灯独立确认 | check-gate.sh P3 exit 2（文件存在）+ scripts/check-tdd-red.sh exit 0（主 Agent 手动 + CI backstop 兜底）|`

### Step 5: 测试适配 — pre-commit-hook.bats

现有测试中依赖"hook 跑 check-gate.sh P3 → check-tdd-red.sh"的用例需要适配。检查 `IT.9`/`IT.9b`（裁剪跳阶测试）——它们测的是 check-pruning.sh 拦截（hook 仍跑 check-pruning.sh），不受影响。

新增测试验证 hook 仍跑 check-gate.sh（写真实 .gate-result.json）：
```bash
@test "IT_GATE_REAL.1: hook runs check-gate.sh and writes real .gate-result.json" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-gatereal1")
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$repo/.git/hooks/pre-commit"
    chmod +x "$repo/.git/hooks/pre-commit"
    mkdir -p "$repo/docs/tasks/T001"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P2
status: active
retries: {}
EOF
    # P2 产出（候选方案 + review + 四字段）
    cat > "$repo/docs/tasks/T001/P2-design.md" <<'EOF'
# P2 design
### 候选方案 A：方案一
### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$repo/docs/tasks/T001/P2-review.md" <<'EOF'
---
agent: test
status: approved
---
通过。
EOF
    git -C "$repo" add docs/tasks/T001/
    _write_min_valid_dispatch_context "$repo/docs/tasks/T001" "P2" "architect"
    git -C "$repo" add docs/tasks/T001/P2-dispatch-context-architect.md
    run git -C "$repo" commit -m "P2"
    [ "$status" -eq 0 ]
    # .gate-result.json 存在且是真实的（runner=pre-commit-hook）
    [ -f "$repo/.gate-result.json" ]
    grep -q 'pre-commit-hook' "$repo/.gate-result.json"
}
```

### Step 6: 测试适配 — ci-gate-backstop.bats（TDD）

在 `agate/tests/unit/ci-gate-backstop.bats` 追加 P3 兜底测试。用 mock check-tdd-red.sh 测 exit 分支：

```bash
setup_git_repo_p3() {
    local repo="$1"
    git_init "$repo"
    mkdir -p "$repo/docs/tasks/T001"
    cat > "$repo/docs/tasks/T001/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    echo '## P3 test cases' > "$repo/docs/tasks/T001/P3-test-cases.md"
    git -C "$repo" add -A
    git -C "$repo" commit -qm "p3"
}
```

ci-gate-backstop.py 的 Step 3 代码已包含 `AGATE_TDD_RED_SCRIPT` 环境变量支持（默认指向真实脚本，测试时指向 mock）。测试用 mock check-tdd-red.sh 测 exit 分支：

```bash
@test "backstop P3: 真红灯（exit 0）→ PASS" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-ok")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-ok"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 0' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>&1 || true"
    [[ "$output" == *"真红灯"* ]]
}

@test "backstop P3: 绿灯（exit 2）→ FAIL" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-green")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-green"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 2' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>&1 || true"
    [[ "$output" == *"FAIL"* ]]
    [[ "$output" == *"绿灯"* ]]
}

@test "backstop P3: 假红灯（exit 1）→ FAIL" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-afake")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-fake"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 1' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>&1 || true"
    [[ "$output" == *"FAIL"* ]]
    [[ "$output" == *"假红灯"* ]]
}

@test "backstop P3: 无运行器（exit 3）→ WARN 不 FAIL" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-norunner")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-norunner"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 3' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>&1 || true"
    [[ "$output" == *"WARN"* ]]
    [[ "$output" != *"FAIL"* ]]
}

@test "backstop P3: 无 .gate-result.json（--no-verify）时仍执行 check-tdd-red.sh" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-noverify")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-ok"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 0' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    # 不创建 .gate-result.json（模拟 --no-verify 场景）
    run bash -c "python3 '$AGATE_SCRIPTS/ci-gate-backstop.py' 2>&1 || true"
    [[ "$output" == *"真红灯"* ]]
}
```

**TDD**：先写这 5 个测试（当前 ci-gate-backstop.py 无 P3 分支 → 测试失败），再修改 ci-gate-backstop.py 加 P3 分支 + AGATE_TDD_RED_SCRIPT 环境变量 → 测试通过。

**第 5 个测试**验证 P3 检查在 `--no-verify` 场景（无 `.gate-result.json`）下仍被执行——如果插入位置错误（放在函数末尾），此测试会失败（P3 检查在 `return 0` 后不可达）。

### Step 7: 运行测试验证通过

Run: `bats agate/tests/unit/check-gate.bats agate/tests/integration/pre-commit-hook.bats agate/tests/unit/ci-gate-backstop.bats`
Expected: ALL PASS

### Step 8: shellcheck + consistency

### Step 9: Commit

```bash
git add agate/scripts/check-gate.sh agate/scripts/ci-gate-backstop.py agate/phase-cards/P3-tdd.md agate/state-machine.md agate/WORKFLOW.md agate/tests/
git commit -m "feat: P3 red-light check separated from check-gate.sh (T085 --no-verify fix)
- check-gate.sh P3 now checks file existence (seconds), not exec check-tdd-red.sh
- hook runs check-gate.sh always (real .gate-result.json, not forgeable)
- CI backstop runs check-tdd-red.sh additionally when phase==P3"
```

---

## Task 3: install-hook.sh 检测 .gitignore

**Files:**
- Modify: `agate/scripts/install-hook.sh`
- Modify: `agate/git-integration.md`

### Step 1: install-hook.sh 追加检测

在 install-hook.sh 末尾追加：
```bash
GITIGNORE="$REPO_ROOT/.gitignore"
if [ -f "$GITIGNORE" ] && grep -qE '^\s*[*]*\.state\.yaml' "$GITIGNORE" 2>/dev/null; then
    echo "⚠️  .gitignore 忽略 .state.yaml — 主 Agent 需要 git add -f docs/tasks/{Txxx}/.state.yaml"
    echo "    或从 .gitignore 中移除 .state.yaml 行（推荐：让 .state.yaml 正常被 git 跟踪）"
fi
```

### Step 2: git-integration.md 追加说明

在规则 2 的 git add 命令后追加：
```markdown
> **注意**：若项目 `.gitignore` 忽略 `.state.yaml`，需要 `git add -f` 强制暂存。`install-hook.sh` 安装时会检测并提醒。
```

### Step 2b: 追加 install-hook.sh 测试（TDD）

新建 `agate/tests/unit/install-hook.bats`：

```bash
#!/usr/bin/env bats
# tests/unit/install-hook.bats — install-hook.sh .gitignore 检测

load ../helpers/load.bash

@test "install-hook: .gitignore 忽略 .state.yaml → WARNING 提醒" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-ig1")
    echo ".state.yaml" > "$repo/.gitignore"
    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT' bash '$AGATE_SCRIPTS/install-hook.sh' '$AGATE_ROOT'" 2>&1
    [[ "$output" == *".state.yaml"* ]]
    [[ "$output" == *"忽略"* ]]
}

@test "install-hook: 无 .gitignore → 无 WARNING" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-ig2")
    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT' bash '$AGATE_SCRIPTS/install-hook.sh' '$AGATE_ROOT'" 2>&1
    [[ "$output" != *".state.yaml"* ]]
}
```

**注意**：install-hook.sh 会链接 hook 到临时仓库的 .git/hooks/。测试在 BATS_TEST_TMPDIR 的临时仓库运行，测试后自动清理，不影响真实环境。

### Step 3: Commit

```bash
git add agate/scripts/install-hook.sh agate/git-integration.md agate/tests/unit/install-hook.bats
git commit -m "fix: install-hook.sh warns about .gitignore ignoring .state.yaml"
```

---

## Task 4: P2 候选方案正则支持 ####

**Files:**
- Modify: `agate/scripts/check-gate.sh:87`
- Modify: `agate/tests/unit/check-gate.bats`

### Step 1: 先写失败测试

```bash
@test "G2.25: P2 #### headings matched as candidates" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P2-design.md" <<'EOF'
# P2 design
#### 候选方案 A：方案一
#### 候选方案 B：方案二
## 权衡
A 更简单，B 更稳健。
packages: [pkg-a]
domains: [backend]
ui_affected: false
gate_commands: {}
EOF
    cat > "$dir/P2-review.md" <<'EOF'
---
agent: test
status: approved
---
通过。
EOF
    run bash "$AGATE_SCRIPTS/check-gate.sh" P2 "$dir"
    [ "$status" -eq 2 ]
}
```

### Step 2: 修改正则

L87：`^###?\s*` → `^#{2,4}\s*`

### Step 2b: 适配现有测试 G2.4

G2.4（"h4 候选方案不识别"）当前用 `####`（4 个 #），新正则 `^#{2,4}` 会识别它 → 语义反转（不再是"h4 不识别"而是"缺四字段"）。改为用 `#####`（5 个 #，新正则确实不匹配）：

当前 G2.4 的 P2-design.md 中 `#### 候选方案` → 改为 `##### 候选方案`，测试标题 `@test "G2.4 check-gate.sh P2 h4 候选方案不识别（regex 边界）"` 同步改为 `h5 候选方案不识别`，注释改为"h5 不被 ^#{2,4} 匹配"。

### Step 2c: 更新 check-gate.sh header 注释

check-gate.sh L9-10 当前：
```
# 可脚本化的 gate（exit 0/1）：P3（check-tdd-red.sh，自动读取 gate_commands.P3）/ P4 / P7
# 需主 Agent 自判的 gate（exit 2）：P0 / P1 / P2 / P5 / P6 / P8
```
改为：
```
# 可脚本化的 gate（exit 0/1）：P3（P3-test-cases.md 存在性）/ P4 / P7
# 需主 Agent 自判的 gate（exit 2）：P0 / P1 / P2 / P3 / P5 / P6 / P8
# P3 红灯（check-tdd-red.sh）由主 Agent 手动确认 + CI backstop P3 兜底，不在此脚本内执行
```

### Step 3: 运行测试 + Commit

---

## Task 5: roadmap + 全量验证

### Step 1: 更新 roadmap

```markdown
**P2.64: phase 时机统一 + P3 gate 分离 + gitignore + P2 正则**

**状态**：已实施
**来源**：T085 复盘（--no-verify 8 次）
**改动**：
- 统一 phase 更新时机：state + 产出同一 commit（7 个卡片 + state-machine.md + git-integration.md）
- 删除 check-state-transition.sh 检查 3（pre-phase-change commit gate）——与模式 B 冲突，产出存在性由 check-gate.sh 检查
- check-gate.sh P3 从 exec check-tdd-red.sh 改为文件存在性检查（秒级，hook 不超时）
- hook 永远自己跑 check-gate.sh（写真实 .gate-result.json，不可伪造）
- CI backstop P3 时额外跑 check-tdd-red.sh 兜底红灯
- install-hook.sh 检测 .gitignore 中 .state.yaml 忽略并提醒
- P2 候选方案正则支持 ####（2-4 个 #）
```

### Step 2: 全量验证

Run: `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`
Expected: ALL PASS

Run: `python3 agate/scripts/check-protocol-consistency.py`
Expected: 0 ERROR

Run: `shellcheck -S warning agate/scripts/*.sh`
Expected: 0 errors

Run: `bash agate/tests/scripts/count-tests.sh`
Expected: 总计增加（+G2.25 +G3 重写 +ci-gate-backstop 5 +install-hook 2 +IT_GATE_REAL.1 ≈ +9）

### Step 2b: 同步 tests/README.md 用例数表

`agate/tests/README.md` 覆盖度表当前已漂移（pre-commit-hook 表写 5 实际 37、consistency 表写 10 实际 11）。本次改动后：
- check-gate.bats：95 → **96**（+G2.25）
- ci-gate-backstop.bats：3 → **8**（+5 个 P3 兜底：真红灯/绿灯/假红灯/无运行器/--no-verify 场景）
- install-hook.bats：**新增行**，值 2
- pre-commit-hook.bats：37 → **38**（+IT_GATE_REAL.1）
- check-state-transition.bats：总数不变（ST.17 反转语义、ST.18 改写，不增不减）
- 以 `count-tests.sh` 实际输出为准修正表

### Step 3: Commit

---

## Self-Review

### 1. Spec coverage

| 需求 | Task |
|------|------|
| phase 时机统一 | Task 1 |
| P3 gate 分离 + 防篡改留痕 | Task 2 |
| install-hook.sh .gitignore | Task 3 |
| P2 正则 #### | Task 4 |
| roadmap + 验证 | Task 5 |

### 2. 防篡改有效性验证

- **hook 永远自己跑 check-gate.sh**：.gate-result.json 是 hook 运行的真实副产品。agent 不参与 hook 执行（pre-commit hook 由 git 触发，agent 无法注入代码）。agent 能做的：
  - 修改暂存区文件 → 影响 check-gate.sh 结果 → 真实的 gate 失败 → 拦截
  - --no-verify → hook 不跑 → .gate-result.json 不存在
  - 手动写 .gate-result.json → hook 自己跑会覆盖 → 无意义；且 CI 全新检出不读本地文件 → 伪造不影响 CI 独立验证
- **密钥方案不可行**：agent 有文件系统访问权限，任何密钥都能读到。真正防篡改是"验证不由 agent 执行"（hook + CI 独立验证）
- **CI 独立验证**：CI 用 actions/checkout 全新检出 → 无本地 .gate-result.json → 独立重跑 check-gate.sh（核心兜底）。伪造 .gate-result.json 无意义（CI 不读本地文件）

### 3. 不增加 agent 负担

- Task 1：统一后步骤更清晰（消除歧义）
- Task 2：主 Agent 手动跑 check-tdd-red.sh 是 P3 卡片已要求的（步骤 2"主 Agent 跑 check-tdd-red.sh 确认红灯"）。hook 跑 check-gate.sh 秒级不超时。主 Agent 不需要做额外的事
- Task 3：install-hook.sh 自动检测提醒
- Task 4：正则放宽

### 4. 向后兼容

- check-gate.sh P3 行为变化：从"跑测试"到"检查文件存在"。主 Agent 手动跑 check-gate.sh P3 得到 exit 2（不再有红灯语义）——主 Agent 需要手动跑 check-tdd-red.sh 确认红灯（P3 卡片步骤 2 已要求）
- hook 仍跑 check-gate.sh（L153 不变）—— 只是 check-gate.sh P3 内部变了
- .gate-result.json 仍由 hook 写（真实结果）
- CI backstop 重跑 check-gate.sh（不变）+ P3 额外跑 check-tdd-red.sh（新增，通过 AGATE_TDD_RED_SCRIPT 环境变量可 mock）
- P2 正则 `^#{2,4}` 是 `^###?` 超集
- G2.4 从 `####`（4 个 #）改为 `#####`（5 个 #）——语义从"h4 不识别"变"h5 不识别"
- check-gate.sh header 注释更新（P3 从"可脚本化"改"需自判"）
- **check-state-transition.sh 检查 3 删除**：从"产出和推进不能同一个 commit"变为"允许同一 commit"。ST.17 语义反转（exit 1 → exit 0）。旧任务在模式 A 下已有两个 commit 的历史不受影响——检查 3 只拦截暂存区行为，不审计历史
- **commit 失败回退**：模式 B 下 commit 失败时 .state.yaml 工作区已是新 phase，但 commit 未成功。agent 不需要手动改回 phase——修好问题后重新 commit 即可（hook 跑的是新 phase 的 gate，通过后 commit 成功）

### 5. 风险

- **check-gate.sh P3 语义变化**：从"检查红灯"变"检查文件存在"。需要所有引用 check-gate.sh P3 的文档/脚本同步（state-machine.md L90、WORKFLOW.md L219、P3-tdd.md、check-gate.sh header、ci-gate-backstop.py）
- **CI backstop P3 额外跑 check-tdd-red.sh**：需要 TASK_DIR。ci-gate-backstop.py 已有 task_dir 计算（L69）。exit 语义：0 → 通过（真红灯）、1 → FAIL（假红灯）、2 → FAIL（绿灯）、3+ → WARN（无运行器，CI 可能没装测试框架，主 Agent 已手动确认过红灯）
- **tests/README.md 用例数**：check-gate.bats 95→96（+G2.25）、ci-gate-backstop.bats 3→8（+5 个 P3 兜底）、install-hook.bats 新增 2、check-state-transition.bats ST.17 反转 + ST.18 改写（总数不变）。Task 5 需同步更新
- **check-state-transition.sh 检查 4 依赖**：检查 4（L157-188，回退时 self-authored 产出归档检查）引用检查 1 的 `diff` 变量（L73）。删除检查 3 不影响 `diff` 计算（检查 1 保留）。需验证删除后检查 4 仍正常工作

### 6. 评审修复记录

本轮独立评审发现的 BLOCKER/SHOULD_FIX 已全部修复：

| # | 级别 | 问题 | 修复 |
|---|------|------|------|
| 1 | BLOCKER | ci-gate-backstop exit 3 处理自相矛盾 | 统一为：0→通过、1→FAIL、2→FAIL、3+→WARN |
| 2 | BLOCKER | ci-gate-backstop 缺 exit 1（假红灯）分支 | 补 `elif tdd_exit == 1: return 1` |
| 3 | BLOCKER | ci-gate-backstop P3 逻辑零测试 | 加 4 个 TDD 测试（ok/green/fake/norunner）+ AGATE_TDD_RED_SCRIPT 环境变量 mock |
| 4 | SHOULD_FIX | G2.4 语义被新正则反转 | G2.4 改用 `#####`（5 个 #） |
| 5 | SHOULD_FIX | check-gate.sh header 注释过时 | 更新 P3 分类（可脚本化→需自判） |
| 6 | SHOULD_FIX | .gate-result.json 被 gitignore + CI 全新检出 | 明确设计：CI 独立重跑是核心兜底，伪造本地文件无意义 |
| 7 | SHOULD_FIX | tests/README.md 用例数未同步 | Task 5 加同步步骤 |
| 8 | SHOULD_FIX | install-hook.sh 检测无测试 | 加 2 个 TDD 测试 |
| 9 | BLOCKER | Task 1 "同一 commit"与 check-state-transition.sh 检查 3 冲突 | 删除检查 3 + ST.17 反转 + ST.18 改写 + git-integration.md L31 更新 + commit 失败回退说明 |
| 10 | BLOCKER | Task 2 Step 3 P3 检查插入位置歧义，--no-verify 场景下可能失效 | 明确"run_gate 之后、gate_result.exists() 之前"插入 + 补第 5 个测试（无 .gate-result.json 时仍执行 P3 检查） |
| 11 | SHOULD_FIX | Task 1 Step 4 缺检查 3/4 独立性实测证据 | 补充"物理删除检查 3 后 ST_ARCHIVE.1-6 全通过"验证记录 |
