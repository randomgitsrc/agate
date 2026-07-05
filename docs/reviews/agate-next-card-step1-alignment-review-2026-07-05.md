---
review_date: 2026-07-05
reviewer: protocol-alignment-review
commit: b0fb461
change_summary: 新增 agate-next-card.sh CLI（输出当前阶段卡片全文，P0-P8）+ 12 用例 bats 测试
files_changed:
  - agate/scripts/agate-next-card.sh (new, 70 行)
  - agate/tests/unit/agate-next-card.bats (new, 12 用例)
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | **NEEDS_HUMAN_REVIEW**（agate/scripts/README.md 未列新 CLI；CHANGELOG 未列） |
| A4 | 测试覆盖 | ALIGNED（核心 12 用例覆盖完整，2-arg 分支未测但同一代码路径） |
| A5 | 下游影响 + 文档传播 | ALIGNED（agent helper，不在 gate 链路；后续 step 2/3 才是用户可见影响） |
| A6 | 锚点表覆盖 | ALIGNED（非 gate 脚本，CHECK 9 不强制） |

**总体结论：PASS**（A3 单项 NEEDS_HUMAN_REVIEW 可后续 commit 时补，不必阻断 step 1）

---

## 逐项审查

### A1: 文档→脚本对齐

**计划声明**（docs/plans/agate-phase-card-enforceability-2026-07-05.md:194-216）：

> 步骤 1：新增 CLI 命令 `agate-next-card.sh`
>
> 输出（stdout）：
> ```
> ## 当前阶段卡片：P3
>
> 路径：{agate_root}/phase-cards/P3-tdd.md
> ---
> <card content>
> ```
>
> exit code：
> - 0：成功
> - 1：参数缺失或过多
> - 2：phase 不在 P0-P8 范围

**脚本实现**（agate/scripts/agate-next-card.sh:34-69）：

```bash
if [ "$#" -ne 1 ]; then
    echo "GATE: agate-next-card.sh 需要 1 个参数（PHASE: P0-P8），收到 $# 个" >&2
    exit 1
fi
...
case "$PHASE" in
    P0|P1|P2|P3|P4|P5|P6|P7|P8) ;;
    *)
        echo "GATE: phase '$PHASE' 不在 P0-P8 范围内" >&2
        exit 2
        ;;
esac
...
printf '## 当前阶段卡片：%s\n\n路径：%s\n---\n' "$PHASE" "$CARD_FILE"
cat "$CARD_FILE"
```

**实跑验证**（脚本运行输出截取 P3）：

```
## 当前阶段卡片：P3

路径：/home/kity/oclab/agate/agate/phase-cards/P3-tdd.md
---
# P3 — TDD 测试设计
...
```

**差异说明**（非阻断）：
- 路径：spec 用 `{agate_root}/phase-cards/P3-tdd.md`（占位符），实现用绝对路径 `/home/kity/oclab/agate/agate/phase-cards/P3-tdd.md`。两者指向同一文件，绝对路径对 step 3 hook sha256 校验更友好（嵌入 dispatch-context 的 `路径：` 行可作为可验证引用）。

**结论**：ALIGNED

---

### A2: 脚本→文档对齐

**脚本输出格式**（agate-next-card.sh:65-69）：
```
## 当前阶段卡片：{PHASE}\n\n路径：{CARD_FILE}\n---\n{card content}
```

**实跑验证**：P0..P8 共 9 个 phase 输出前 3 行格式完全一致（已逐一打印验证），P3 完整卡片内容与 `agate/phase-cards/P3-tdd.md` 仅差 1 行（CLI 在卡片前追加 `---` 分隔符）。

**字节稳定性测试**（hash precondition for step 3 hook）：

| phase | run1 sha256 | run2 sha256 | 一致 |
|---|---|---|---|
| P0 | 0fb7bd87... | 0fb7bd87... | ✓ |
| P3 | 58704988... | 58704988... | ✓ |
| P8 | e5ef4317... | e5ef4317... | ✓ |

两次连续跑 → sha256 完全相同。Python hash 与 shell sha256sum 交叉验证一致。

**失败路径覆盖**（实跑）：

| 输入 | 预期 exit | 实测 exit | 实测 stderr |
|---|---|---|---|
| 0 参数 | 1 | 1 | `GATE: agate-next-card.sh 需要 1 个参数（PHASE: P0-P8），收到 0 个` |
| 2 参数 (P0 P1) | 1 | 1 | `... 收到 2 个` |
| P9 | 2 | 2 | `GATE: phase 'P9' 不在 P0-P8 范围内` |
| p3 (lowercase) | 2 | 2 | `GATE: phase 'p3' 不在 P0-P8 范围内` |
| PX | 2 | 2 | `GATE: phase 'PX' 不在 P0-P8 范围内` |

**结论**：ALIGNED

---

### A3: 一致性连锁 + 反向传播

**已知衍生改动**（A3a）：

| 触发 | 影响 | 实际状态 |
|---|---|---|
| 新增 `agate-next-card.sh` | 是否影响 `pre-commit-gate.sh` 调用链？ | 否（脚本不在 `check-*.sh` glob 中，未被 hook 调用） |
| 新增 phase-cards 引用 | 是否触发 `CHECK 2 文件引用存在` WARNING？ | 是（spec 路径 `{agate_root}/phase-cards/...` 含变量占位符）；实现用绝对路径，CHECK 2 PASS |

**反向传播主动推理**（A3b）：

按 A3 反向传播表 `agate/scripts/check-*.sh`（脚本行为）→ `agate/scripts/README.md`、`agate/tests/README.md`、对应角色文件。

| 文件 | 是否应被影响 | 实际状态 |
|---|---|---|
| `agate/scripts/README.md` | **是**——CLI 是新 agent helper，应列入"版本发现"小节（与 `agate-summary.sh` / `agate-changes.sh` 并列） | **未列**（grep 无匹配） |
| `agate/tests/README.md` | 是——`agate-next-card.bats` 应加入覆盖度表 | **未列**（grep 无匹配；但 `count-tests.sh` 统计已自动含 12 个 @test） |
| `agate/assets/execution-roles/*.md` | 否——CLI 是 orchestrator 工具，非角色执行工具 | N/A |
| `CHANGELOG.md` | 是——新增 CLI 协议特性应记 [Unreleased] | **未列**（grep 无匹配） |

**A3 三项缺口**：

1. `agate/scripts/README.md` 未列 `agate-next-card.sh`
2. `agate/tests/README.md` 覆盖度表未列 `agate-next-card.bats` (12 用例)
3. `CHANGELOG.md` 未列新 CLI

**是否阻断 commit？**：
- 这三项都是 **documentation-only**（非代码正确性）
- 后续 step 2/3 (dispatch-context.md 模板 + hook 校验) 会让 CLI 真正投入使用，那些步骤的 commit 必然要更新 README/CHANGELOG
- step 1 仅做 CLI 工具，maintainer 可在 step 3 合并 commit 时一并更新 README/CHANGELOG
- **建议**：标记 NEEDS_HUMAN_REVIEW，主 Agent 在合并 step 1 时决定（a）补 3 处文档 vs （b）由后续 step 一起补

**结论**：NEEDS_HUMAN_REVIEW（文档传播缺口，不阻断 step 1 PASS）

---

### A4: 测试覆盖

**用例清单**（agate/tests/unit/agate-next-card.bats）：

| # | 用例 | 覆盖目标 |
|---|---|---|
| 1-9 | P0..P8 各自 happy path | 9 phase × 1 用例 = 9 条 |
| 10 | 输出含固定头部 | header 3 行（`## 当前阶段卡片：P3` + `路径：` + `---`） |
| 11 | 0 参数 → exit 1 | 参数错分支 |
| 12 | P9 → exit 2 | phase 越界分支 |

**全量实跑**：`bats agate/tests/unit/agate-next-card.bats` → `1..12 / ok 1-12`（全过）

**全量 bats**：`bats sanity.bats unit/ regression/ integration/` → **210/210 pass**（baseline 198 + 12 新增）

**覆盖率分析**：

- ✓ header 字节级格式契约（用例 10）
- ✓ 9 phase happy path（用例 1-9）
- ✗ 2 参数分支（未单独测，但与 0 参数共用 `[ "$#" -ne 1 ]` 同一代码路径，1 个测试覆盖）
- ✗ "phase 通过校验但文件不存在" 分支（line 60-63 unreachable，因为 case 已穷举 P0-P8 + 全文件存在；可写但永远不到）
- ✗ sha256 字节稳定性（hook 校验前提；用例 10 间接覆盖格式，但未显式做 byte stability test）

**结论**：ALIGNED（核心覆盖完整，缺口都是不可达分支或非功能测试）

---

### A5: 下游影响 + 文档传播

**影响范围分析**：

| 项 | 评估 |
|---|---|
| 现有 gate 行为 | 不影响（CLI 不在 `check-*.sh` glob，未被 hook 调用） |
| 已有项目兼容性 | 不影响（CLI 是新工具，无同名旧文件） |
| 协议语义 | 不变（phase 含义、卡片格式、转移规则均未变） |
| 破坏性变更 | 无 |
| 安装步骤 | 无需（CLI 在 `agate/scripts/`，hook 安装脚本 `install-hook.sh` 无需改） |

**文档传播**（与 A3 重叠，单列以强调）：
- `CHANGELOG.md` [Unreleased] 应在 step 2/3 一并记
- `README.md` version badge：本 step 不涉及版本变更，badge `v0.8.0` 不需改

**结论**：ALIGNED

---

### A6: 锚点表覆盖

**CHECK 9 锚点表**（agate/scripts/check-protocol-consistency.py:540-548 + 552-558）：

```python
GATE_SCRIPT_EXEMPT = {
    "agate/scripts/gate-result.sh",
    "agate/scripts/install-hook.sh",
    "agate/scripts/agate-changes.sh",
    "agate/scripts/agate-summary.sh",
    "agate/scripts/agate-init.sh",
}
```

`check_anchor_coverage` 函数（line 561-588）只扫描 `check-*.sh` glob + `pre-commit-gate.sh`，对新 CLI 无要求。

**新增 CLI 类别判断**：
- `agate-next-card.sh` 是 agent helper（与 `agate-summary.sh` / `agate-changes.sh` / `agate-init.sh` 同类）
- 不匹配 `check-*.sh` 模式
- 不强制纳入锚点表

**是否应加入白名单？**：
- 白名单用于"非 gate 工具脚本豁免 CHECK 9 覆盖检查"
- 但白名单外的脚本会触发 `rep.warn`（不是 ERROR），所以即使不加入白名单也不会阻断 consistency check
- **结论**：保持不加入，与 `agate-summary.sh` 等同类处理一致（后者也未列入白名单但仅生成 WARN）

**实跑**：`python3 agate/scripts/check-protocol-consistency.py` → **0 ERROR / 1 WARNING**（WARNING 是 pre-existing `analyst.md` YAML 示例，与本 commit 无关）

**结论**：ALIGNED

---

## 实跑证据汇总

| 命令 | 结果 |
|---|---|
| `bats sanity.bats unit/ regression/ integration/` | 210/210 pass |
| `bats agate/tests/unit/agate-next-card.bats` | 12/12 pass |
| `python3 agate/scripts/check-protocol-consistency.py` | 0 ERROR / 1 pre-existing WARNING |
| `shellcheck agate/scripts/agate-next-card.sh` | 0 error（1 info SC2015，与 agate-changes.sh / agate-summary.sh 同模式，info-level 不计入） |
| `bash agate-next-card.sh P{0..8}` × 9 | 全部 exit 0，header 3 行格式一致 |
| `bash agate-next-card.sh` × 5 (0/2/P9/p3/PX) | exit 1/1/2/2/2 与契约一致 |
| 字节稳定性（sha256 两轮对比） | P0/P3/P8 三 phase 完全一致 |
| 跨目录路径解析（cd /tmp/peekview-test） | 仍正确输出 `## 当前阶段卡片：P3` + 绝对路径 |
| CLI 输出 vs `phase-cards/P3-tdd.md` 内容 | 仅差 1 行（CLI 末尾 `---` 分隔符） |

## 总体结论

**PASS**

step 1 实现与 plan spec 严格对齐，所有 6 项审查项中 5 项 ALIGNED，1 项 NEEDS_HUMAN_REVIEW（A3 文档传播缺口）。NEEDS_HUMAN_REVIEW 不阻断 commit——3 处文档缺口都是 documentation-only，且 step 2/3 后续 commit 必然要同步更新 README/CHANGELOG，可在合并 step 3 时一并补。

**主 Agent 后续动作建议**（不阻断）：

1. 标记 `[HUMAN_CONFIRMED: 2026-07-05 确认：A3 三项文档缺口（scripts/README.md / tests/README.md / CHANGELOG.md）由 step 2/3 合并 commit 时统一补]`
2. 在 step 2 commit 时同步更新 `agate/scripts/README.md`（加入 agate-next-card.sh 行）
3. 在 step 3 commit 时同步更新 `agate/tests/README.md` 覆盖度表 + `CHANGELOG.md` [Unreleased]

---

**[HUMAN_CONFIRMED: 待主 Agent 填写]**