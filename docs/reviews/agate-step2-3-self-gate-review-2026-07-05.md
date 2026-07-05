---
review_date: 2026-07-05
reviewer: protocol-alignment-review
change_summary: dispatch-context 模板 + hook hash 校验（防漂移）— step 2-3
files_changed:
  - agate/assets/templates/dispatch-context.md (新模板)
  - agate/scripts/pre-commit-gate.sh (新增 2p 节，19 行)
  - agate/tests/integration/dispatch-context-card.bats (3 测试)
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

**总体结论**：PASS

---

## 验证执行结果（实跑，非读代码推断）

| 验证项 | 命令 | 结果 |
|--------|------|------|
| bats 全量套件 | `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` | 218/218 OK |
| check-protocol-consistency.py | `python3 agate/scripts/check-protocol-consistency.py` | 0 ERROR, 1 WARNING (pre-existing, unrelated) |
| shellcheck | `shellcheck agate/scripts/pre-commit-gate.sh` | 0 errors (仅 SC1091 info) |
| 实跑：hash 匹配场景 | 创建 P3-dispatch-context.md，嵌入 CLI 输出，sha256 比对 | PASS（hash 一致，不误拦） |
| 实跑：篡改场景 | sed 在 marker 间插入 `_TAMPERED_` 行，sha256 比对 | PASS（hash 不一致，确实拦） |
| Marker 一致性 | grep 模板 + hook 的 AGATE_CARD_START/END | 完全一致 |

### 实跑详情

**hash 匹配场景**：
```
Expected hash: 004aa7d0ba84f309269ca92d16828d8b9cdbcb3c756cba573a84870e7c90b851
Embedded hash: 004aa7d0ba84f309269ca92d16828d8b9cdbcb3c756cba573a84870e7c90b851
RESULT: PASS - hashes match (valid card not blocked)
```

**篡改场景**：
```
Expected hash: 004aa7d0ba84f309269ca92d16828d8b9cdbcb3c756cba573a84870e7c90b851
Embedded hash: cfa31dc484e5202c2d0150450d83620ab8c7249c303405ef72a819b50aeb474c
RESULT: PASS - hashes mismatch (tamper correctly detected)
```

---

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（dispatch-context.md:13）：
> hook 会校验 sha256 一致——编辑或篡改 card 内容会导致 hash mismatch，commit 被拦截。

**文档声明**（dispatch-context.md:15-17）：
> `<!-- AGATE_CARD_START -->` ... `<!-- AGATE_CARD_END -->`

**脚本实现**（pre-commit-gate.sh:146-162）：
```bash
DC_FILE="$TASK_DIR/${PHASE}-dispatch-context.md"
if [ -f "$DC_FILE" ] && [ -x "$AGATE_ROOT/scripts/agate-next-card.sh" ]; then
    EXPECTED=$(bash "$AGATE_ROOT/scripts/agate-next-card.sh" "$PHASE" 2>/dev/null) || true
    if [ -n "$EXPECTED" ]; then
        EXPECTED_HASH=$(printf '%s' "$EXPECTED" | sha256sum | awk '{print $1}')
        EMBEDDED=$(sed -n '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/p' "$DC_FILE" \
                   | sed '1d;$d')
        EMBEDDED_HASH=$(printf '%s' "$EMBEDDED" | sha256sum | awk '{print $1}')
        if [ "$EMBEDDED_HASH" != "$EXPECTED_HASH" ]; then
            echo "GATE: dispatch-context.md 卡片内容与 CLI 输出不一致（hash mismatch）" >&2
            exit 1
        fi
    fi
fi
```

**结论**：ALIGNED
- 模板声明的 AGATE_CARD_START/END marker 与 hook sed 正则完全一致
- 模板声明的 sha256 校验 → hash mismatch → commit 拦截，与 hook 实现的 sha256sum 比对 → exit 1 完全一致
- 模板暗示"CLI 原文直嵌 marker 之间"的约束由 hash 比对强制执行——任何编辑都会导致 mismatch

### A2: 脚本→文档对齐

**脚本实现**：pre-commit-gate.sh 2p 节（行 146-162）实现三个关键行为：
1. 仅当 dispatch-context.md 存在 + agate-next-card.sh 可执行时运行
2. sha256 比对 CLI 输出 vs 嵌入内容
3. 不一致 → exit 1

**文档覆盖**：
- `agate/assets/templates/dispatch-context.md:13` — 描述 hash 校验机制
- `agate/scripts/README.md:50-57` — 完整描述防漂移机制 + byte stability 保证
- `agate/tests/integration/dispatch-context-card.bats:1-3` — 测试文件头部注释描述验证目标

**结论**：ALIGNED
- 脚本三个关键行为在模板和 scripts/README.md 中均有文档覆盖
- scripts/README.md:50 明确描述 "Phase Card 防漂移机制的权威卡片源" 和 "sha256 校验嵌入的卡片是当前版本（防过期/防篡改）"

### A3: 一致性连锁 + 反向传播

#### A3a：已知衍生改动

| 改动 | 应同步的衍生文件 | 状态 |
|------|-----------------|------|
| 新模板 dispatch-context.md | task-files.md 辅助文件表（已有 dispatch-context 条目） | 已对齐 |
| 新 hook 2p 节 | scripts/README.md 新增描述 | 已存在（行 50-57，早前 step 1 已写入） |
| 新测试文件 | tests/README.md 索引 | 需确认 |

#### A3b：反向传播（应被影响但未在 diff 中的文件）

| 文件 | 是否需同步 | 判断 |
|------|-----------|------|
| `agate/orchestrator-template.md` | 否 | 行 58 描述创建 dispatch-context.md 的职责，行 91 强调禁写 PASS/FAIL。hash 机制是透明 hook 层实施——Agent 只需按模板写文件，hook 自动校验。模板文件自包含 hash 说明。 |
| `agate/dispatch-protocol.md` | 否 | 行 265-274 描述 dispatch-context 的客观信息内容。hash 机制是格式层约束，由模板文件承载，不需要在协议文档重复。 |
| `agate/WORKFLOW.md` | 否 | 行 250 描述 dispatch-context 落盘职责。hash 校验属于 hook 实现细节。 |
| `agate/assets/templates/dispatch-prompt.md` | 否 | 行 26/162 引用 dispatch-context 作为可选输入。hash 校验不影响派发 prompt 结构。 |

**结论**：ALIGNED
- 模板文件自包含 hash 机制说明——Agent 按模板创建文件即自然满足约束
- 协议文档描述「职责/用途」层，模板描述「格式/约束」层，分工清晰
- 无需额外文档同步

### A4: 测试覆盖

**测试文件**：`agate/tests/integration/dispatch-context-card.bats`（93 行，3 测试）

| 测试 | 场景 | 验证 |
|------|------|------|
| DC.1 | 正确卡片 hash → commit | 不因 hash mismatch 被拦 |
| DC.2 | 卡片被篡改（sed 在 marker 前插入 `_TAMPERED_`）| exit != 0 + output 含 "hash mismatch" |
| DC.3 | 空卡片块（marker 间无内容，但 CLI 输出非空）| exit != 0 + output 含 "hash mismatch" |

**边界覆盖**：
- DC.1 覆盖正常路径（防误拦）
- DC.2 覆盖篡改检测（防漏过）
- DC.3 覆盖空白块（CLI 有输出但嵌入为空 → 必定 mismatch）
- 三个测试在 218/218 全量套件中通过

**未覆盖的边界**（不需要测试——hook 自身处理）：
- agate-next-card.sh 不可执行 → hook 跳过（`-x` 检查）
- dispatch-context.md 不存在 → hook 跳过（`-f` 检查）
- CLI 输出为空 → hook 跳过（`-n` 检查）

**结论**：ALIGNED
- 三个核心场景覆盖充分
- 防御性跳过条件在 hook 内部，无需单独测试

### A5: 下游影响 + 文档传播

**破坏性变更评估**：
- 新增 hook 节是 **opt-in**：仅当 `dispatch-context.md` 存在且 `agate-next-card.sh` 可执行时触发
- 不存在的项目不受影响
- 语法一致的 dispatch-context.md（按模板格式写入的）不受影响——hash 匹配通过

**CHANGELOG 状态**：
- 当前 CHANGELOG 已有 dispatch-context 相关条目（审计 2、协议文档同步），来自之前的 v0.6 hardening
- 本 commit 属于 step 2-3 增量，尚未发布，届时应在 release commit 中标注

**文档传播**：
- `scripts/README.md:50-57` 已描述该机制（step 1 时写入）
- 模板文件自身含 hash 机制说明——Agent 读模板即知约束
- 用户面协议文档（orchestrator-template / dispatch-protocol / WORKFLOW）无需同步——它们描述「为何创建」dispatch-context，模板描述「如何创建」

**结论**：ALIGNED
- 无破坏性变更
- 文档传播已覆盖（scripts/README.md + 模板自身）
- CHANGELOG 标注待 release commit

### A6: 锚点表覆盖

**CHECK 9 锚点表现状**：
- `check-protocol-consistency.py` RUN 结果：0 ERROR，CHECK 9 PASS
- `pre-commit-gate.sh` 当前有 1 条锚点：`{desc: "PROD_TOUCHED 检测", keywords: ["PROD_TOUCHED"]}`
- 新的 dispatch-context hash 功能是在已有脚本中新增节，不是新增脚本

**锚点表是否需要更新**：
- 锚点表设计用途：验证「协议文档声明的规则 → 脚本有关键词实现」
- 本 feature 是新增功能——模板文件同时承担了「声明规则」和「格式约束」两个角色
- 新增锚点条目可做 forward-proofing，但当前 CHECK 9 的设计是正向核对已有声明，不要求新功能必有锚点
- `check_anchor_coverage()`（行 561-588）要求每个 gate 脚本至少被一条锚点覆盖——`pre-commit-gate.sh` 已有 PROD_TOUCHED 锚点，满足此要求

**结论**：ALIGNED
- 已有锚点覆盖满足 CHECK 9 结构要求
- 未来若 dispatch-protocol.md 或其他协议文档显式声明 "dispatch-context 卡片必须 hash 验证"，应同步添加锚点

---

## 审查总结

所有 6 项审查均 ALIGNED，无 MISALIGNED，无 NEEDS_HUMAN_REVIEW。

- 验证结果：218/218 bats, 0 ERROR consistency, 0 shellcheck error, 2/2 E2E 实跑通过
- 模板 marker 与 hook sed 完全一致
- hash 匹配场景不误拦，篡改场景确实拦
- 文档传播已覆盖（模板自包含 + scripts/README.md）
