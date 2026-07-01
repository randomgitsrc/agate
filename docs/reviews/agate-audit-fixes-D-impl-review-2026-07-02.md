---
task_id: agate-audit-fixes-D
agent: main
date: 2026-07-02
status: 评审完成
来源: docs/plans/agate-audit-fixes-D-design-2026-07-02.md (v2)
---

# D 组实施评审：门槛表对齐修复

## 评审结论

| 维度 | 结果 |
|------|------|
| 代码-设计一致性 | **部分通过** — #13 脚本完全一致；#6/#16 dispatch-protocol.md 一致；但 state-machine.md 和 WORKFLOW.md 存在反向传播遗漏 |
| 逻辑正确性 | **通过** — 逐场景推演无错误 |
| 测试覆盖 | **通过** — 40/40 bats 全绿，设计文档要求的 G2.10-G2.13 均已覆盖 |
| 文档同步 | **未完成** — dispatch-protocol.md 已同步，但 state-machine.md:84-85, :384-385, :94, :388 和 WORKFLOW.md:194, :196 仍为旧措辞 |
| 反向传播 | **2 处遗漏** — state-machine.md + WORKFLOW.md 未随 #6/#16/#13 更新 |
| CHECK 9 影响 | **无新增锚点需求** — CHECK 9 是关键词存在性检查，P2 status:approved 和四字段检查的关键词已在 check-gate.sh 中，但 CHECK 9 锚点表未注册这两个检查项（非本次回归，是既有缺口） |

## 逐项评审

### #12 P1 门槛不实现

- **设计**：不修，P1 保持 exit 2
- **实施**：check-gate.sh:18-20 未改动，exit 2
- **结论**：✅ 一致

### #13 P2 门槛对齐

#### 脚本 check-gate.sh:22-51

**设计要求**：count check → status:approved → 四字段 → form check → exit 2

**实际顺序**（check-gate.sh:22-51）：
1. L24-31: CANDIDATE_COUNT < 2 → exit 1 ✅
2. L32-38: P2-review.md 存在时查 status:approved → exit 1 ✅
3. L39-44: FIELD_COUNT < 4 → exit 1 ✅
4. L45-48: 缺权衡/选择理由 → exit 1 ✅
5. L50-51: exit 2 ✅

**逐场景推演**：

| 场景 | 预期 | 实际 | 判定 |
|------|------|------|------|
| P2-design.md 不存在 | exit 2（跳过 if 块） | exit 2 | ✅ |
| 0 候选方案 | exit 1 | exit 1 | ✅ |
| 1 候选方案 | exit 1 | exit 1 | ✅ |
| ≥2 候选 + 无 P2-review.md | exit 2（跳过 status 检查） | exit 2 | ✅ |
| ≥2 候选 + P2-review.md 无 approved | exit 1 | exit 1 | ✅ |
| ≥2 候选 + P2-review.md 有 approved + 缺字段 | exit 1 | exit 1 | ✅ |
| ≥2 候选 + approved + 四字段 + 无权衡 | exit 1 | exit 1 | ✅ |
| ≥2 候选 + approved + 四字段 + 有权衡 | exit 2 | exit 2 | ✅ |

**关键细节验证**：

1. **status:approved 查 P2-review.md**（不是 P2-design.md）✅ — L32 `P2_REVIEW="$TASK_DIR/P2-review.md"`，L33 `if [ -f "$P2_REVIEW" ]`，L34 `grep -qE 'status:\s*approved' "$P2_REVIEW"`
2. **四字段计数 `< 4`** ✅ — L41 `if [ "$FIELD_COUNT" -lt 4 ]`，用 `<` 不用 `!=`，允许额外字段
3. **P2-review.md 不存在时放行** ✅ — L33 `if [ -f "$P2_REVIEW" ]`，不存在则跳过整个 status 检查块
4. **grep -c || echo 0 | tail -1** ✅ — L39-40 正确处理 grep 无匹配时的双行问题

#### dispatch-protocol.md:577

**设计要求**：补"候选方案≥2"、`=4`→`≥4`、补 form check

**实际**：
```
| P2→P3 | 方案已批准 | `grep 'status: approved' P2-review.md` → 命中 + `grep -cE '^(packages\|domains\|ui_affected\|gate_commands):' P2-design.md → ≥4` + `grep -qE '权衡\|选择理由' P2-design.md` → 命中 + 候选方案 ≥2（`scripts/check-gate.sh P2` 脚本化部分）|
```

- `≥4` ✅（原 `=4` 已改）
- 补了 `grep -qE '权衡\|选择理由'` ✅
- 补了"候选方案 ≥2" ✅

**结论**：✅ dispatch-protocol.md 完全一致

#### 测试覆盖

| 测试 ID | 场景 | 设计要求 | 实际 |
|---------|------|----------|------|
| G2.10 | 有候选+权衡+四字段，P2-review.md 无 approved | exit 1 | ✅ pass |
| G2.11 | 有候选+权衡+四字段+status:approved | exit 2 | ✅ pass |
| G2.12 | 缺字段（<4） | exit 1 | ✅ pass |
| G2.13 | 有候选+权衡+四字段，无 P2-review.md | exit 2 | ✅ pass |

**G2.3/G2.6/G2.7/G2.8/G2.9 四字段补充**：

| 测试 ID | P2-design.md 含四字段？ | pass？ |
|---------|------------------------|--------|
| G2.3 | ✅ packages/domains/ui_affected/gate_commands | ✅ |
| G2.6 | ✅ | ✅ |
| G2.7 | ✅ | ✅ |
| G2.8 | ✅ | ✅ |
| G2.9 | ✅ | ✅ |

**结论**：✅ 测试完全覆盖

### #6 P4 路径偏离 + #16 P4 git log → --cached

#### dispatch-protocol.md:579

**设计要求**：去掉"P4-implementation/ 下文件非空"和"git log"，改为暂存区检查

**实际**：
```
| P4→P5 | 实现完成 | 暂存区含非 md/yaml 文件（`git diff --cached --name-only | grep -qvE '\.(md|yaml)$|^\.state'`）|
```

- 去掉了 `P4-implementation/` ✅
- 去掉了 `git log` ✅
- 改为 `git diff --cached` ✅
- 与 check-gate.sh:57 完全一致 ✅

**结论**：✅ dispatch-protocol.md 完全一致

## 反向传播遗漏

### 遗漏 1：state-machine.md

| 位置 | 当前措辞 | 应改为 |
|------|----------|--------|
| L84 | `P2 --[P2-review.md 有效 AND status==approved AND P2-design.md 声明 packages/domains/ui_affected/gate_commands]--> P3` | 补"候选方案≥2"和"权衡/选择理由"条件 |
| L85 | `P2 --[P2-review.md status==rejected && retry<MAX]--> P2 (retry+1)` | 无需改 |
| L94 | `P4 --[P4-implementation/ 下文件非空 AND git log --oneline -1 包含 P4 commit]--> P5` | `P4 --[暂存区含非 md/yaml 文件（git diff --cached）]--> P5` |
| L384-385 | `P2: grep 'status: approved' {task}/P2-review.md → 命中; grep -cE '...' → =4` | `→ ≥4` + 补候选方案≥2 + 补权衡/选择理由 |
| L388 | `P4: git log --oneline -1 → 含 "P4" 或 "wf(Txxx-P4)"` | `P4: git diff --cached --name-only | grep -qvE '\.(md|yaml)$|^\.state'` |

### 遗漏 2：WORKFLOW.md

| 位置 | 当前措辞 | 应改为 |
|------|----------|--------|
| L194 | `P2-review.md 的 status == approved；grep -cE '...' P2-design.md → =4` | `→ ≥4` + 补候选方案≥2 + 补权衡/选择理由 |
| L196 | `git log --oneline -1 含 P4 commit` | `暂存区含非 md/yaml 文件（git diff --cached）` |

### 影响评估

- **严重度**：中。state-machine.md 和 WORKFLOW.md 是协议核心文档，与 dispatch-protocol.md 门槛表不一致会导致使用者困惑。
- **CHECK 9 影响**：CHECK 9 当前锚点表未注册 P2 status:approved / 四字段 / P4 --cached 的检查项。这是既有缺口（非本次回归），但本次改动加剧了文档-脚本不一致的风险。建议后续补注册。
- **一致性检查**：`check-protocol-consistency.py` 当前 0 ERROR，因为 CHECK 9 只做关键词存在性（不查语义对齐），且 CHECK 8 的 `--cached` 关键词已在 check-gate.sh 中存在。

## 自动化验证结果

| 检查 | 结果 |
|------|------|
| bats agate/tests/unit/check-gate.bats | 40/40 pass |
| shellcheck agate/scripts/check-gate.sh | 0 error |
| python3 agate/scripts/check-protocol-consistency.py | 0 ERROR, 5 WARNING |
| 测试用例总数 | 177（与 count-tests.sh 一致） |

## 总结

**D 组 #13/#6/#16 的直接修改（check-gate.sh + dispatch-protocol.md）实施正确**，代码逻辑、测试覆盖、文档同步均与设计文档 v2 一致。

**反向传播未完成**：state-machine.md（5 处）和 WORKFLOW.md（2 处）仍为旧措辞，需同步更新。这是本次评审发现的唯一阻塞项。

**建议**：
1. 更新 state-machine.md L84, L94, L384-385, L388
2. 更新 WORKFLOW.md L194, L196
3. 考虑在 CHECK 9 锚点表补注册 P2 status:approved / 四字段 / P4 --cached（非阻塞，可后续处理）
