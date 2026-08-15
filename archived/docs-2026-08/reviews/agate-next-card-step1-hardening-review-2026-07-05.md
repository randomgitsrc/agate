---
review_date: 2026-07-05
reviewer: protocol-alignment-review
change_summary: step 1 修订：CLI 测试补 byte-stability 硬保证 + 跨目录/symlink + 文档同步
files_changed:
  - agate/tests/unit/agate-next-card.bats (12 → 17 tests)
  - agate/scripts/README.md (新增「阶段卡片 CLI」小节)
  - CHANGELOG.md (Unreleased 加 step 1 条目)
commit: 07094fd
type: 协议-脚本对齐审查（self-gate，commit 前审查）
---

# 协议-脚本对齐审查 — step 1 CLI 测试硬化

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED（1 个轻缺口，不阻塞） |
| A4 | 测试覆盖 | ALIGNED（从 soft proof 升级为 hard proof） |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |

**总判定**：**PASS**（215/215 bats + 0 ERROR + 0 shellcheck error；9 个 phase sha256 实跑全 MATCH；body = cat *.md 字节完全等价；跨目录/symlink 全部 hash 一致。1 个轻缺口是 tests/README.md 未提 CLI 测试套件，是 A3b 反向传播未触及文档，不影响功能正确性。）

---

## 逐项审查

### A1: 文档→脚本对齐

**scripts/README.md:48-57 声明**（本次新增小节）：

> `agate-next-card.sh` | 输出当前阶段卡片全文（PHASE 取值 P0-P8）
>
> **退出码语义**：
> - 0：成功，stdout 输出卡片全文
> - 1：参数缺失或过多
> - 2：phase 不在 P0-P8 范围
>
> **字节稳定性保证**：`agate/tests/unit/agate-next-card.bats` 的 9 个 sha256 测试断言 CLI 输出 body（去掉前 4 行固定头）的 sha256 等于 `cat ${PHASE}-*.md` 的 sha256。

**agate-next-card.sh:33-47 实现**：

```bash
# exit 1：参数缺失或过多
if [ "$#" -ne 1 ]; then
    echo "GATE: agate-next-card.sh 需要 1 个参数（PHASE: P0-P8），收到 $# 个" >&2
    exit 1
fi

PHASE="$1"

# exit 2：phase 不在 P0-P8 范围
case "$PHASE" in
    P0|P1|P2|P3|P4|P5|P6|P7|P8) ;;
    *)
        echo "GATE: phase '$PHASE' 不在 P0-P8 范围内" >&2
        exit 2
        ;;
esac
```

**验证**（实跑）：

| 测试 | 结果 |
|------|------|
| `bash agate-next-card.sh` (无参) | exit 1 ✓ |
| `bash agate-next-card.sh P3 extra` (双参) | exit 1 ✓ |
| `bash agate-next-card.sh P9` (越界) | exit 2 ✓ |
| `bash agate-next-card.sh p3` (小写) | exit 2 ✓ |
| `bash agate-next-card.sh P0..P8` | exit 0 ✓ |

**结论**：ALIGNED
**差异**：无

---

### A2: 脚本→文档对齐

**agate-next-card.sh:49-59 卡片文件名映射**：

```bash
CARD_FILE="$AGATE_REPO/agate/phase-cards/${PHASE}-$(case "$PHASE" in
    P0) echo "orchestrator" ;;
    P1) echo "requirements" ;;
    ...
esac).md"
```

**agate/phase-cards/ 实存文件**：

```
P0-orchestrator.md    P1-requirements.md   P2-design.md
P3-tdd.md             P4-implementation.md P5-verification.md
P6-acceptance.md      P7-consistency.md     P8-release.md
```

→ 9 个映射 100% 命中文件系统，无悬空指针。

**scripts/README.md:50 字节稳定性声明 ↔ agate-next-card.sh:67-68 实现**：

- README：「body（去掉前 4 行固定头）的 sha256 等于 `cat ${PHASE}-*.md` 的 sha256」
- 脚本：`printf '## 当前阶段卡片：%s\n\n路径：%s\n---\n' "$PHASE" "$CARD_FILE"` + `cat "$CARD_FILE"`

实测验证 body 字节等价：
```
cat P3-tdd.md sha256 = 8da15e2c9a38b1261827457da113499c97fb37c6c2b8fab1ed8f04cfc0c843d2
CLI body sha256     = 8da15e2c9a38b1261827457da113499c97fb37c6c2b8fab1ed8f04cfc0c843d2
→ 完全一致
```

→ README 描述精确对应实现。

**结论**：ALIGNED
**差异**：无

---

### A3: 一致性连锁 + 反向传播

**A3a（已知衍生改动）**：

- ✅ `agate/tests/unit/agate-next-card.bats` 12 → 17 测试（在 diff）
- ✅ `agate/scripts/README.md` 新增「阶段卡片 CLI」小节（在 diff）
- ✅ `CHANGELOG.md` Unreleased 加 step 1 条目（在 diff）
- ✅ bats 全量从 203 → 215 OK
- ✅ `count-tests.sh` 输出从 204 → 209（增量 5，与 .bats 文件中 @test 数增量一致）

**A3b（反向传播检查）**：

| 文档 | grep 结果 | 应反向传播？ |
|------|----------|-------------|
| `agate/tests/README.md` | 0 命中 agate-next-card / next-card / 阶段卡片 CLI | **轻缺口**：CLI 测试套件未在 tests/README.md 显式索引（agenda: 增量测试 +1 个 file，未在 test 索引登记）|
| `agate/dispatch-protocol.md` | 0 命中 | 不需要（step 2-3 接入 dispatch-context 时才反向传播；当前 step 1 是 CLI 本体可独立验证）|
| `agate/orchestrator-template.md` | mapping 表已含 9 张 phase-cards 路径（line 112-120）| 不需要（mapping 表独立完整）|
| `agate/WORKFLOW.md` | 0 命中 | 不需要（阶段总览靠 phase-cards/README 反向索引）|
| `agate/AGENTS.md` | 0 命中 | 不需要（CLI 是工具，不是协议入口）|
| `agate/phase-cards/README.md` | 自身内容与 CLI 互不依赖 | 不需要 |
| `SELF-GATE.md` | 0 命中 step 1 / CLI | 不需要（本次是 step 1 自身的 fixup，按 SELF-GATE 触发条件不递归触发自身审查）|
| `agate/assets/execution-roles/*.md` | 0 命中 | 不需要（CLI 是主 Agent 工具，subagent 角色文件无需感知）|
| `agate/assets/review-roles/*.md` | 0 命中 | 不需要 |
| `docs/issues/003-*.md` | 0 命中 | 不需要（issue 内容已涵盖防漂移机制范围）|

**唯一轻缺口**：tests/README.md 未提 CLI 测试套件。但：
- 索引性缺口，不影响功能正确性
- count-tests.sh 已自动枚举该文件（line 13 `for f in unit/*.bats` 包含 agate-next-card.bats）
- 本次 commit 主要修复"byte-stability 硬证明"，未触及 test 文档维护面

**结论**：ALIGNED（1 个轻缺口，建议项 #1）

---

### A4: 测试覆盖

**测试结构对比**：

| 维度 | 之前（12 tests）| 之后（17 tests）|
|------|----------------|----------------|
| 防漂移前提证明 | 仅 grep 关键词（"包含 # P3" / "包含 TDD"）= **soft proof** | 9 个 phase sha256 实测 = **hard proof** |
| 字节稳定性 | 未覆盖 | 连续两次调用 hash 一致 ✓ |
| 跨目录解析 | 未覆盖 | CWD 在 /tmp 仍能解析 AGATE_REPO ✓ |
| 软链接场景 | 未覆盖 | ln -sf + readlink -f hash 等价 ✓ |
| 参数校验 | 2 用例（无参 + P9） | 4 用例（无参 + 双参 + P9 + 小写 p3）✓ |
| 头部分隔契约 | 单用例含 3 断言 | 头部三行固定 + 第 4 行 `---` 分隔 ✓ |

**9 个 sha256 hard proof 实测**（人工复跑全部 9 phase）：

```
P0: b5cf94b0c4da1685af840becea9e7a031a4da7dd3b3fd3d5a97b82ab6d664ccd ✓
P1: 552cfa18df736bdb1782fbead8ec6e1c367da8f129cdded3b8c98f5974353156 ✓
P2: ae0d87a9567c5d0a39116cb07a4b04941a38cb15933fcc6de032e47361e412a7 ✓
P3: 8da15e2c9a38b1261827457da113499c97fb37c6c2b8fab1ed8f04cfc0c843d2 ✓
P4: e3d47f932e373b633b73743bb8288fb2ebc454e5ee7bd62c42dbe0bb71883a93 ✓
P5: 8a33fd16f210bed15c228679df9618985077f246abf340fc794601448bd6ddf7 ✓
P6: 54a342ec80a87130de3cec25343529fd26d5ac92a677f9a5190d84381d928225 ✓
P7: e99d3812ecd69d28f385e3782684c769d2bffe18ea3bc4aa935c9ddfde39e768 ✓
P8: 15128d0f06f6075e87af837f7f28dde098b90839687a8504d1606f76a4ca6209 ✓
```

**防漂移动态验证**（修改卡片 → CLI 跟随变化）：

```
P3 改前 body hash: 8da15e2c...c843d2
追加一行后:        1bde4961...7596b4
→ CLI body hash 跟随变化（防漂移前提成立）✓
还原 P3-tdd.md 后: hash 恢复 8da15e2c...c843d2 ✓
```

**body = cat *.md 字节等价证明**：

```
sha256(cat agate/phase-cards/P3-tdd.md) == sha256(CLI body) ✓
→ body 完全等于 cat *.md（无 sed 区间偏移、无 echo 多余换行）
→ step 3 hook 复算时只需 `tail -n +5 | sha256sum` 即可拿到同一哈希
```

**字节稳定性证明**：

```
hash1 = 58704988cdbd58bf69343245033fb5192042782869b623f9b41b5f017f96c44f
hash2 = 58704988cdbd58bf69343245033fb5192042782869b623f9b41b5f017f96c44f
→ STABLE ✓
```

**跨目录 + symlink**：

```
native hash:    58704988cdbd58bf69343245033fb5192042782869b623f9b41b5f017f96c44f
from /tmp:      58704988cdbd58bf69343245033fb5192042782869b623f9b41b5f017f96c44f ✓
via symlink:    58704988cdbd58bf69343245033fb5192042782869b623f9b41b5f017f96c44f ✓
```

（首次复跑因 subshell scoping 显示 MISMATCH，纠正后 diff 实际为空，三个调用 hash 完全相同。）

**结论**：ALIGNED（从 soft proof 升级为 hard proof）
**价值**：本次硬证明是 step 3 hook `EXPECTED=$(bash agate-next-card.sh $PHASE) | sha256sum` 能正确工作的前提。没有这 9 个 sha256 测试，step 3 接入时只能靠"CLI 应该输出对应卡片"这种信念——step 1 测试保证了 hook 不需要担心 CLI 实现细节。

---

### A5: 下游影响 + 文档传播

**对已使用 v0.8.0 协议的项目**：

- **CLI 新增**：`agate-next-card.sh` 是新工具，不修改既有任何接口
- **bats 测试新增**：纯增量（+5 tests），不修改既有测试语义
- **scripts/README.md 增量**：在 line 42 与 line 59 之间新增小节，不替换既有内容
- **CHANGELOG Unreleased 增量**：在已有 Unreleased 段尾追加条目
- **破坏性变更**：0
- **向后兼容性**：100%（CLI 是可选工具，未调用时无副作用）

**CHANGELOG 标注**（line 31-34）：

```markdown
### 阶段卡片 CLI（Phase Card 防漂移机制前置）
- **agate-next-card.sh 新增**：主 Agent 调 `agate-next-card.sh P{N}` 拿到对应阶段卡片全文...
- **17 个 unit 测试**（`agate/tests/unit/agate-next-card.bats`）：9 个 sha256 byte-stability 测试... + 字节稳定性 + 跨目录路径解析 + 软链接场景 + 失败路径
- **scripts/README.md 新增「阶段卡片 CLI」小节**
```

→ CHANGELOG 条目准确描述了 CLI + 测试 + README 改动（与 diff 一致）

**文档传播路径**：

- ✅ `agate/scripts/README.md`（CLI 用途/退出码/字节稳定性完整覆盖）
- ✅ `CHANGELOG.md`（Unreleased 标注 step 1）
- ⚠️ `agate/tests/README.md` 未提 CLI 测试套件（与 A3b 轻缺口同源，不阻塞）

**结论**：ALIGNED

---

### A6: 锚点表覆盖

**SCRIPT_ALIGNMENT_ANCHORS（CHECK 9）**：

- 本次未新增 gate 脚本（agate-next-card.sh 是辅助工具，不是 gate）
- 本次未修改 check-*.sh / pre-commit-gate.sh
- 锚点表白名单无变化需求
- 反向兜底（"每个 check-*.sh 必须在锚点表里"）：本次未新增 check-*.sh → 无遗漏风险
- 实测 `python3 agate/scripts/check-protocol-consistency.py`：CHECK 9 PASS ✓

**FILE_COUNT_ANCHORS（CHECK 5 已删除）**：

- 本次不涉及
- 已删 CHECK 5（plan §步骤 0 已处理）

**结论**：ALIGNED

---

## 关键问题回应（用户原始问题）

### Q1: sh 什么时候触发？

**现状**：本次提交后，`agate-next-card.sh` 仍无调用方。

- 本次 commit (`07094fd`) 是 step 1 的修订（测试硬化 + 文档同步），不引入调用方
- 调用方是 step 2（dispatch-context.md 模板）+ step 3（pre-commit-gate.sh 新增 2p 检查）
- plan `agate-phase-card-enforceability-2026-07-05.md:117-358` 列了 step 0-6，step 2-3 是后续独立 commit

**结论**：当前是 dead code（无调用方）。这是诚实降级——plan §"不解决什么" 已声明 step 1 可独立交付，CLI 本体的可验证性本身就是价值。**不阻塞本次 commit。**

### Q2: 触发有什么意义？

**意义层级**：

| 阶段 | 触发情况 | 价值 |
|------|---------|------|
| **现在（step 1 已落）** | 无调用方 | CLI 本体的可验证性 + 字节稳定性证明（本次 9 sha256 测试）|
| **step 2-3 接入后** | pre-commit-gate.sh 2p 触发 | 防漂移机制生效（嵌入 dispatch-context 的卡片 hash 必须 = CLI 输出 hash）|
| **未来** | 主 Agent 主动调 CLI 替代 `cat $PHASE-*.md` | 信息层 + 决策层机械化（plan §方案 A 价值）|

**重要洞察**：step 1 的真正价值在"如果将来要被调用，必须先保证 CLI 本身可验证"——9 个 sha256 测试是 step 3 hook 的前提依赖。没有这层验证，step 3 hook 接入时会假设"CLI 输出 == 卡片文件"，但这种假设未经验证（之前 12 测试是 soft proof）。

### Q3: 字节稳定性 hard proof 还是 soft proof？9 个 phase 是否都覆盖？

**之前（12 tests）**：soft proof（grep 关键词："包含 # P3"、"包含 TDD"）。CLI 改了输出但仍含关键词就能通过——**不能证明 byte-stability**。

**现在（17 tests）**：hard proof。

- 9 个 sha256 测试覆盖 P0/P1/P2/P3/P4/P5/P6/P7/P8 = **100% phase 覆盖** ✓
- 每个 phase 的实测：CLI 输出 body hash == `cat ${PHASE}-*.md` hash ✓
- 防漂移动态验证：改 P3 → CLI body 跟随变化 ✓
- 字节等价证明：CLI body == cat 输出（无 sed 偏移） ✓
- 字节稳定性：连续两次调用 hash 一致 ✓

**结论**：本次 9 个 phase 100% 覆盖，从 soft proof 升级为 hard proof。

---

## 实证测试结果

| 测试 | 结果 |
|------|------|
| `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` | **215/215 OK** |
| `python3 agate/scripts/check-protocol-consistency.py` | **0 ERROR**，1 WARNING（pre-existing analyst.md:41，与本次无关）|
| `shellcheck agate/scripts/agate-next-card.sh` | **0 error**（1 info SC2015，与 agate-changes.sh:14 / agate-summary.sh:11 同模式，project-wide 既有 pattern）|
| `shellcheck agate/scripts/*.sh`（全量）| 5 info + 0 error（无新增 error）|
| `bash agate/tests/scripts/count-tests.sh` | unit/agate-next-card.bats: 17 @test；总计 209（不含 sanity.bats 的 6 个——这是既有事实，非本次回归）|
| 实跑 9 phase sha256 | 9/9 MATCH ✓ |
| 实跑改 P3 → CLI 跟随 | hash 跟随变化 ✓（防漂移前提成立）|
| 实跑 CLI body == cat *.md | sha256 完全一致 ✓ |
| 实跑字节稳定性 | hash1 == hash2 ✓ |
| 实跑跨目录 (/tmp) | hash == native ✓ |
| 实跑 symlink | hash == native ✓ |
| 实跑 case-sensitive（小写 p3）| exit 2 ✓ |

---

## 总判定与建议

**总判定**：**PASS**

- 215/215 bats OK（含 17 个 CLI 测试，其中 9 个 phase sha256 硬证明）
- 0 ERROR / 0 shellcheck error / 0 行为回归
- 字节稳定性已升级为 hard proof（9 phase 100% 覆盖）
- 跨目录 + symlink + case-sensitive 鲁棒性已覆盖
- 文档同步完整（scripts/README.md 新章节 + CHANGELOG Unreleased 条目）
- 无破坏性变更，向后兼容 100%

**建议（按优先级）**：

| # | 动作 | 优先级 | 阻塞？ |
|---|------|--------|--------|
| 1 | `agate/tests/README.md` 加 CLI 测试套件索引（`unit/agate-next-card.bats 17 tests`）| 低 | 不阻塞（A3b 反向传播轻缺口）|
| 2 | shellcheck SC2015 改写（`A && B || C` → 显式 if）| 低 | 不阻塞（与既有 agate-changes.sh / agate-summary.sh 同模式，project-wide 既有）|
| 3 | count-tests.sh 加 sanity.bats 范围（修复"209 vs 215 不一致"）| 低 | 不阻塞（本次新增 +5 tests 已正确反映在 209 内，sanity.bats 不在计数范围是既有设计）|

无 MISALIGNED 项。无 NEEDS_HUMAN_REVIEW 项。可安全 commit。

---

## 用户问题总结

| 用户问题 | 回答 |
|---------|------|
| sh 什么时候触发？ | 当前无调用方（dead code）；step 2-3 接入后由 pre-commit-gate.sh 2p 触发 |
| 触发有什么意义？ | step 1 价值在 CLI 本体可验证性（9 sha256 硬证明），不是"已被调用"；调用价值在 step 3（防漂移）|
| 字节稳定性 hard proof 还是 soft proof？ | 本次升级为 hard proof（之前 12 测试是 soft proof）|
| 9 个 phase 是否都覆盖？ | 是，100%（P0/P1/P2/P3/P4/P5/P6/P7/P8 各 1 sha256 测试）|