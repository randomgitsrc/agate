---
task_id: agate-t060-retro-bugfixes
agent: main
date: 2026-07-21
status: draft
来源:
  - docs/reviews/T060-archived-visibility-auth-refresh-retrospective-2026-07-21.md (peekview)
仓库快照: randomgitsrc/agate v0.15.0 (commit 4225d03)
---

# agate T060 复盘发现的 3 个 bug + 1 项设计改进

## 文档说明

本文档源自 PeekView T060 任务复盘。T060 在执行过程中被 agate gate 反复拦截（5 次），其中 3 次根因在 agate 自身，2 次在平台。复盘也暴露了 P5 全量测试缺失导致依赖问题跨 4 个任务周期无人发现的设计缺陷。

本文档聚焦 agate 侧可修复的问题。5 项发现中，3 个是 clear-cut bug（应修）、1 个是设计改进（建议修）、1 个是结构性限制（记录但不修）。

---

# 第一部分：T060 发现汇总

## 发现的 5 项 agate 问题

| # | 问题 | 来源（T060 复盘节） | 类型 | 是否修复 |
|---|------|----|------|----------|
| 1 | `agate-inject-card.sh` 找不到占位符时静默"成功" | §3 问题 B:4 + §5:4 | Bug | ✅ 修 |
| 2 | SCOPE+ 正则匹配 dispatch-context 约束指令 | §3 问题 B:5 + §5:5 | Bug | ✅ 修 |
| 3 | `check-changelog.sh` 用全路径搜索 task_id | §3 问题 B:1 + §5:6 | Bug | ✅ 修 |
| 4 | P5 未强制全量测试 | §3 问题 C + §5:7 | 设计改进 | ✅ 修（WARNING 级） |
| 5 | dispatch-context provenance 链（文件存在≠subagent 读过） | §3 问题 A | 结构性限制 | ❌ 不修（已记录在 LIMITATIONS.md 局限3） |

## 判断标准

- **Bug 1-3**：门禁行为不符合设计意图（用户操作正确但 gate 误拦截 / 工具操作成功但实际未完成）。明确可修复，修复不改变协议语义，不引入新依赖，修复成本低。
- **Bug 4**：设计缺陷——P5 缺少"全量测试是否执行"的验证，导致预存失败被淹没问题。修复为 WARNING 级提示，不改变 gate 通过条件（风险：如果改成阻断，会大幅增大 P5 摩擦且多数项目不需要全量跑）。
- **Bug 5**：dispatch-context 的 provenance 问题——当前平台支持独立 git author 之前，无法区分"subagent 读了文件"和"主 Agent 自己补了文件"。这是深刻的结构性限制，但本次不适合修（修它需要平台能力，不是 agate 协议层能做的），已记录在 LIMITATIONS.md 局限3。

---

# 第二部分：逐项修复

## Bug 1：agate-inject-card.sh 静默成功

**影响**：找不到 `<!-- AGATE_CARD_START -->` 占位符时，`re.sub()` 返回原文不变，脚本输出"AGATE_CARD 已注入"——用户以为注入成功了，实际什么都没做。后续 commit 时 hash mismatch 拦截，用户不知道是注入失败。

**根因**（`agate/scripts/agate-inject-card.sh:49-53`）：
```python
pattern = r'(<!-- AGATE_CARD_START -->\n)(.*?)(<!-- AGATE_CARD_END -->)'
replacement = r'\g<1>' + card + r'\n\3'
new_text = re.sub(pattern, replacement, text, flags=re.DOTALL)
with open(dc, 'w') as f:
    f.write(new_text)
```

`re.sub()` 在 pattern 不匹配时返回原字符串，不会报错。

**修复**：替换后检查 `new_text == text`，若未发生变化则 exit 1：

```diff
- with open(dc, 'w') as f:
-     f.write(new_text)
+ if new_text == text:
+     print(f"AGATE_CARD 注入失败: {os.path.basename(dc)} 中未找到 AGATE_CARD_START/END 占位符", file=sys.stderr)
+     sys.exit(1)
+ with open(dc, 'w') as f:
+     f.write(new_text)
```

需在 Python 代码块开头加 `import sys`。

**bats 测试追加**（`agate/tests/unit/agate-inject-card.bats`）：

```bash
@test "dispatch-context 无 AGATE_CARD 占位符时 exit 1（非静默成功）" {
    local task_dir
    task_dir="$BATS_TEST_TMPDIR/task_no_placeholder"
    mkdir -p "$task_dir"

    cat > "$task_dir/P1-dispatch-context-analyst.md" <<'EOF'
---
phase: P1
task_id: T001
role: analyst
---

<dispatch_guide>
### 目标
无占位符文件
</dispatch_guide>
EOF

    run bash "$INJECT_CMD" P1 "$task_dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"未找到"* ]] || [[ "$output" == *"占位符"* ]]
}
```

---

## Bug 2：SCOPE+ 正则匹配 dispatch-context 约束指令

**影响**：dispatch-context 文件的 `<dispatch_guide>` 约束节可能包含字面文本 `[SCOPE+]`（例如"如果发现矛盾，标 [SCOPE+] 而非直接做"），`check-scope-resolved.sh` 的正则匹配到它，触发 SCOPE_RESOLVED 检查——这是个正向引用，导致用户被迫在 P1 里加虚假的 SCOPE_RESOLVED 标记。

**现状**（`check-scope-resolved.sh:15-21`）：已通过 `sed` 排除 AGATE_CARD 块内的文本，但 dispatch-context 文件正文中仍可能有 SCOPE+ 字面引用。

```bash
for f in "$TASK_DIR"/*.md; do
    [ -f "$f" ] || continue
    if sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d' "$f" | grep -q '\[SCOPE+\]'; then
        SCOPE_FOUND="${SCOPE_FOUND}$(basename "$f") "
    fi
done
```

**修复**：排除 dispatch-context 文件——它们不是阶段产出，不应参与 SCOPE+ 扫描：

```diff
  for f in "$TASK_DIR"/*.md; do
      [ -f "$f" ] || continue
+     # 跳过 dispatch-context 文件（编排指令，非阶段产出，不含实际 SCOPE+ 指令）
+     basename "$f" | grep -q 'dispatch-context' && continue
      if sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d' "$f" | grep -q '\[SCOPE+\]'; then
          SCOPE_FOUND="${SCOPE_FOUND}$(basename "$f") "
      fi
  done
```

**bats 测试追加**（`agate/tests/unit/check-scope-resolved.bats`）：

```bash
@test "dispatch-context 文件中的 [SCOPE+] 字面引用不触发检查" {
    create_task_dir
    cat > "$TASK_DIR/P4-dispatch-context-implementer.md" <<'EOF'
---
phase: P4
task_id: T001
role: implementer
---

<dispatch_guide>
### 约束
如果发现需求与设计矛盾，标 [SCOPE+] 而非直接做
</dispatch_guide>
EOF

    # P1 无 SCOPE_RESOLVED，但 SCOPE+ 在 dispatch-context 中应被忽略
    run bash "$AGATE_SCRIPTS/check-scope-resolved.sh" "$TASK_DIR"
    [ "$status" -eq 0 ]
}
```

---

## Bug 3：check-changelog.sh 用全路径搜索 task_id

**影响**：`pre-commit-gate.sh` 调用 `check-changelog.sh "$TASK_ID"`，而 `TASK_ID` 来自 `.state.yaml` 的 `task_id` 字段（如 `T060-archived-visibility-auth-refresh`）。`check-changelog.sh` 用 `grep -qF "$TASK_ID"` 在 `[Unreleased]` 区域做固定字符串精确匹配。CHANGELOG 条目通常写 `T060: xxx`（只用短前缀），不会写完整目录名。结果：CHANGELOG 明明有 `T060` 相关条目，但 gate 报 "未找到"。

**根因**（`check-changelog.sh:7, 26`）：脚本接收并使用了调用者传入的完整 task_id，不提取短前缀。

**修复**：在脚本内提取 `T\d+` 前缀作为搜索关键词，分两步匹配：

```diff
  TASK_ID="${1:?用法: check-changelog.sh TASK_ID}"
+
+ # 提取 task_id 短前缀（T\d+）作为 CHANGELOG 搜索关键词
+ # .state.yaml 的 task_id 可能是完整目录名（T060-archived-visibility-auth-refresh），
+ # 但 CHANGELOG 条目通常只写短前缀（T060）
+ TASK_ID_SHORT=$(echo "$TASK_ID" | grep -oE 'T[0-9]+' | head -1)
+ [ -z "$TASK_ID_SHORT" ] && TASK_ID_SHORT="$TASK_ID"

  ...

- if echo "$UNRELEASED_CONTENT" | grep -qF "$TASK_ID"; then
-     exit 0
- else
-     echo "GATE CHANGELOG: [Unreleased] 区域未找到 ${TASK_ID}" >&2
-     exit 1
- fi
+ if echo "$UNRELEASED_CONTENT" | grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)" 2>/dev/null; then
+     exit 0
+ fi
+ # fallback: 尝试完整 task_id 固定字符串匹配（如 CHANGELOG 写了完整目录名）
+ if echo "$UNRELEASED_CONTENT" | grep -qF "$TASK_ID" 2>/dev/null; then
+     exit 0
+ fi
+ echo "GATE CHANGELOG: [Unreleased] 区域未找到 ${TASK_ID_SHORT}（或 ${TASK_ID}）" >&2
+ exit 1
```

**说明**：
- 第一步先匹配短前缀（`T060`），后缀字符集 `( |:|$|,|-)` — 支持 `T060:`、`T060: `、`T060-`、`T060,`、`T060\n` 等边界格式
- 第二步 fallback：如果短前缀不匹配（极少见，但完整目录名可能被直接写进 CHANGELOG），回退到 `grep -qF "$TASK_ID"` 精确匹配
- `[^0-9]` 前缀防止 `T0601` 误匹配 `T060`
- `-` 在后缀集合中：`T060-archived-visibility-auth-refresh:` 中 `T060` 后的 `-` 会触发匹配，不会因为连字符漏掉

**bats 测试追加**（`agate/tests/unit/check-changelog.bats`）：

```bash
@test "CHANGELOG 含短前缀 T060 但 task_id 为完整目录名时正确匹配" {
    local tmpdir="$BATS_TEST_TMPDIR/test_changelog"
    mkdir -p "$tmpdir"

    cat > "$tmpdir/CHANGELOG.md" <<'EOF'
## [Unreleased]

### Fixed
- T060: 修复 archived 条目可见性
EOF

    run bash -c "cd '$tmpdir' && CHANGELOG_FILE=CHANGELOG.md \
        bash '$AGATE_SCRIPTS/check-changelog.sh' T060-archived-visibility-auth-refresh"
    [ "$status" -eq 0 ]
}

@test "CHANGELOG 含 T0601 时短前缀 T060 不误匹配" {
    local tmpdir="$BATS_TEST_TMPDIR/test_changelog"
    mkdir -p "$tmpdir"

    cat > "$tmpdir/CHANGELOG.md" <<'EOF'
## [Unreleased]

### Fixed
- T0601: 其他条目
EOF

    run bash -c "cd '$tmpdir' && CHANGELOG_FILE=CHANGELOG.md \
        bash '$AGATE_SCRIPTS/check-changelog.sh' T060-archived-visibility-auth-refresh"
    [ "$status" -eq 1 ]
    [[ "$output" == *"未找到"* ]]
}

@test "CHANGELOG 含 T060-archived-visibility-auth-refresh: 时后缀 - 正确匹配" {
    local tmpdir="$BATS_TEST_TMPDIR/test_changelog"
    mkdir -p "$tmpdir"

    cat > "$tmpdir/CHANGELOG.md" <<'EOF'
## [Unreleased]

### Fixed
- T060-archived-visibility-auth-refresh: 条目
EOF

    run bash -c "cd '$tmpdir' && CHANGELOG_FILE=CHANGELOG.md \
        bash '$AGATE_SCRIPTS/check-changelog.sh' T060-archived-visibility-auth-refresh"
    [ "$status" -eq 0 ]
}
```

---

## Bug 4（设计改进）：P5 未强制全量测试

**影响**：P5 gate 只检查 `gate_commands.P5` 的命令是否 exit 0 + failed==0。如果 P2 声明了多个测试命令（单元 + 集成 + E2E），但主 Agent 只跑了子集，gate 不会发现。T060 案例中 T056 引入 venv 依赖遗漏，全量测试 41% 失败（395/951），但跨越 4 个任务周期无人发现——因为每个 P5 都只跑了相关子集测试。

**协议现状**：
- `dispatch-protocol.md:640`：P5 修复流程明确要求"重跑 P5 gate（全量测试）"
- `phase-cards/P5-verification.md:48`："建议运行全量测试套件（含非本任务测试），若发现预存失败 → WARNING"
- 但这些是**文档层提示**，没有脚本层强制执行或检查

**修复**：不强改 P5 的通过条件（exit 2 保持为"需主 Agent 手动判定"），但加一段 WARNING 级提示——当 task_dir 内存在 P5 修复轮次标记（多轮 P5→P4 回退）或 P2 声明的测试命令超过 1 条时，提醒主 Agent 确认是否跑了全量。

在 `check-gate.sh` 的 P5 分支（第 117 行）之后追加：

```bash
      # WARNING: 如果 P2 声明了多个 gate_commands.P5 命令（单元+集成+E2E），
      # 提醒主 Agent 确认是否全部执行（T060 教训：只跑子集可能掩盖预存失败）
      P5_CMD_COUNT=$(grep -cE '^\s+- ' "$TASK_DIR/P2-design.md" 2>/dev/null || echo 0)
      P5_CMD_COUNT=$(echo "$P5_CMD_COUNT" | tail -1)
      if [ "$P5_CMD_COUNT" -gt 1 ]; then
          echo "GATE P5 WARNING: P2 声明了 ${P5_CMD_COUNT} 个 gate_commands.P5 命令，请确认已全部执行（非子集）。" >&2
          echo "  T060 教训：只跑子集可能掩盖预存失败（T056 venv 遗漏跨 4 个任务周期无人发现）。" >&2
      fi
```

注意：这个检查很粗糙（grep `- ` 行数），无法真正区分"单元测试命令"和"集成测试命令"是否都被执行。但它是低成本 WARNING——提醒主 Agent 多看一眼，不是强制门禁。更精确的检查需要 P5-test-results/ 目录结构与 gate_commands 的结构化对照，那需要改 P5 产出格式，超出本次范围。

**bats 测试追加**（`agate/tests/unit/check-gate.bats`）：

```bash
@test "P2 gate_commands.P5 多命令时 P5 输出 WARNING" {
    create_task_dir --phase P5
    cat > "$TASK_DIR/P2-design.md" <<'EOF'
---
phase: P2
task_id: T001
agent: architect
---

## gate_commands
```yaml
P5:
  - pytest tests/unit
  - pytest tests/integration
  - pytest tests/e2e
```
EOF

    run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$TASK_DIR"
    [ "$status" -eq 2 ]  # P5 恒 exit 2（需主 Agent 手动判定）
    [[ "$output" == *"gate_commands.P5"* || "$output" == *"全量"* || "$output" == *"子集"* ]]
}
```

### 评估：为什么是 WARNING 而非强制

- P5 gate 恒 exit 2 的设计是"主 Agent 自行判定"——因为测试命令是项目特定的（pytest vs cargo test vs go test），agate 无法机器判定"全量"意味着什么
- 改成 exit 1 会大幅增加摩擦：多数项目不需要跑全量测试（非 agate 自身项目只需跑相关测试）
- WARNING 级提示足够提醒主 Agent 警觉，但不改变 gate 的通过条件
- T056 的 venv 问题严格说是项目流程缺陷（P8 应加 `make dev` 检查）而非 agate 协议缺陷

---

# 第三部分：self-gate 影响分析

本次改动全部落在 `agate/scripts/*.sh` → 触发 self-gate（修复 A 的正则已覆盖 `agate/scripts/.*\.sh`，本次无需再修）。

| 文件 | 改动性质 | 是否触发 self-gate |
|------|----------|-------------------|
| `agate/scripts/agate-inject-card.sh` | Bug fix：添加占位符缺失检测 + exit 1 | 是 |
| `agate/scripts/check-scope-resolved.sh` | Bug fix：跳过 dispatch-context 文件 | 是 |
| `agate/scripts/check-changelog.sh` | Bug fix：提取 task_id 短前缀搜索 | 是 |
| `agate/scripts/check-gate.sh` | 新增 P5 全量测试 WARNING | 是 |

**协议文档同步**（A2 反向传播）：

| 文档 | 需同步的改动 |
|------|-------------|
| `phase-cards/P5-verification.md` | "全量测试 WARNING" 现有的描述行与 check-gate.sh 新增的脚本层 WARNING 对应（文档已有描述，脚本补上检测逻辑，不冲突） |
| `dispatch-protocol.md:786` | P5→P6 gate 条件表——无变更（P5 恒 exit 2，WARNING 不改变门槛条件） |
| `CHANGELOG.md` | 标注 3 个 bug fix + 1 个 P5 WARNING |
| `agate/scripts/README.md` | check-changelog.sh 描述更新（搜索方式从精确匹配改为 task_id 短前缀提取） |
| `AGENTS.md` shellcheck | 无变更 |

---

# 第四部分：实施顺序

1. **Bug 1–3 实施**（`agate-inject-card.sh`、`check-scope-resolved.sh`、`check-changelog.sh`）——无相互依赖，可并行
2. **Bug 4 实施**（`check-gate.sh` P5 WARNING）
3. **bats 测试**——每个 bug 的测试用例可与代码修复同步写（TDD：先写失败测试）
4. **文档同步**——更新 `scripts/README.md`、`CHANGELOG.md`、`phase-cards/P5-verification.md`
5. **`check-protocol-consistency.py` 跑一遍**——确认 0 ERROR
6. **全量 bats**——确认无退化
7. **shellcheck**——`shellcheck -S warning agate/scripts/*.sh`
8. **protocol-alignment-review**——审查 Bug 1-4 的脚本改动与文档同步
9. **commit**——message 含 `self-gate-review: docs/reviews/agate-alignment-review-{date}.md`
10. **版本判定**——Bug fix 不改变协议语义（exit 2 仍为 exit 2，WARNING 仍是 WARNING），非破坏性变更，patch bump：v0.15.0→v0.15.1

---

# 第五部分：不修的问题及理由

## Bug 5：dispatch-context provenance 链（文件存在 ≠ subagent 读过）

**T060 §3 问题 A 详细记录**：P4 三个子任务的 dispatch-context 文件被写了但 implementer subagent 从未读过——因为主 Agent 用的 inline prompt 而非文件。P7 更甚——dispatch-context 文件在 subagent 完成后才补写。

**为什么本次不修**：
- 当前平台架构下，主 Agent 和 subagent 共享同一个 git author，无法区分谁写了文件
- 验证"subagent 是否真的读了 dispatch-context 文件"需要平台侧能力（subagent 工具调用日志），不是 agate 协议层能做的
- 这已在 `LIMITATIONS.md` 局限 3 中记录："self-authored gate 的造假风险只能缓解（提高成本 + 留痕审计），无法根治"
- 根治方向：Phase 3 独立 git author 落地后，agent 字段升级为 git author 硬检查

**临时缓解**：T060 复盘 §6 建议中"dispatch-context 必须在派发前写"是主 Agent 的自律要求，不是 agate 协议能强制执行的规则。

---

# 第六部分：实施就绪核查清单

| 措施 | 影响文件 | 新增依赖 | 测试 | 破坏性变更 | 状态 |
|------|---------|----------|------|-----------|------|
| Bug 1: inject-card 占位符检测 | `agate-inject-card.sh` | 无（加 `import sys`） | bats 1 新增 | 否（原为 bug）| 待实施 |
| Bug 2: SCOPE+ 排除 dispatch-context | `check-scope-resolved.sh` | 无 | bats 1 新增 | 否（原为 bug）| 待实施 |
| Bug 3: CHANGELOG task_id 短前缀 | `check-changelog.sh` | 无 | bats 3 新增 | 否（原为 bug）| 待实施 |
| Bug 4: P5 全量测试 WARNING | `check-gate.sh` | 无 | bats 1 新增 | 否（新增 WARNING）| 待实施 |
| 文档同步 | `scripts/README.md`、`CHANGELOG.md`、`phase-cards/P5-verification.md` | 无 | 无 | 否 | 待实施 |

## 结论

4 项修复全部是小范围、低风险、有明确根因和验证方式的改动。不引入新依赖，不改变 gate 通过条件（Bug 1 从静默通过改为死错误，但这不是破坏性变更——原来的"通过"是 bug 伪装）。建议 patch bump v0.15.0→v0.15.1。
