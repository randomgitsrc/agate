---
review_date: 2026-08-08
reviewer: protocol-alignment-review
change_summary: agate/AGENTS.md「升级 agate」节修正过时陈述——pre-push hook 从「写死复制、必须重装」改为「三 hook 均 ln -sf 软链、自动跟随、无需重装，Windows 复制模式需重跑」
files_changed: [agate/AGENTS.md]
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
| A7 | 设计原则一致性 | ALIGNED |

**无 MISALIGNED，无 NEEDS_HUMAN_REVIEW。**

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（agate/AGENTS.md:79，修正后）：
> 下次 commit 自动用新版本协议。pre-commit/commit-msg/pre-push 三个 hook 均为 `install-hook.sh` 以 `ln -sf` 软链方式安装，自动指向最新代码、随协议升级自动跟随，**无需重装**。（Windows 无符号链接权限时以复制模式安装，升级后需重跑 `install-hook.sh`，见 `platform-notes.md`「Windows 原生」章节。）

**脚本实现**（install-hook.sh）：
- pre-commit：`ln -sf "$SOURCE" "$HOOK_FILE"`（L31）
- commit-msg：`ln -sf "$COMMIT_MSG_SOURCE" "$COMMIT_MSG_HOOK"`（L50）
- pre-push：`ln -sf "$PRE_PUSH_SOURCE" "$PRE_PUSH_HOOK"`（L73）
- L62 注释自述：`# v0.32.0：与 pre-commit/commit-msg 统一为软链，bug 修复自动分发，无需重装`
- Windows 复制模式：L34-39（`[ -L "$HOOK_FILE"]` 判定非软链即复制模式，并打印「升级 agate 后需重跑 install-hook.sh（复制不自动跟随源文件）」）；L52-56（commit-msg 复制模式提示）；L75-79（pre-push 复制模式提示）

**结论**：ALIGNED。
**差异**：无。修正后陈述与脚本实际行为逐字一致——三个 hook 确实都是 `ln -sf` 软链，自动跟随升级；Windows 复制模式提示与「需重跑」陈述完全吻合。

### A2: 脚本→文档对齐

**脚本逻辑**（install-hook.sh 软链安装，v0.32.0 已实现）对应协议文档此前为过时陈述（写死复制、必须重装）。本次变更正是把文档修正到与脚本现状一致，方向正确。

**结论**：ALIGNED。其余协议文档中 install-hook 相关描述均已为「三 hook」口径：
- orchestrator-template.md:102「安装 pre-commit + commit-msg + pre-push hook」
- dispatch-protocol.md:824「由 install-hook.sh 安装 pre-commit + commit-msg + pre-push hook」
- scripts/README.md:35「安装 pre-commit + commit-msg + pre-push hook」

### A3: 一致性连锁 + 反向传播

**A3a 连锁**：本次仅 1 行文档修正，无已知衍生改动。

**A3b 反向传播**（扫描范围：`agate/`、README.md、CHANGELOG.md、docs/）：
- ✅ `platform-notes.md:132`：Windows 复制模式「升级 agate 后需重跑此命令」提示存在，与 AGENTS.md 修正后「Windows 复制模式需重跑」交叉一致
- ✅ `platform-notes.md:144`：已知限制表「`ln -sf` 退化为复制 → 重跑 install-hook.sh」一致
- ✅ `README.md:109`：「无需重装 hook——软链接会自动指向最新代码」与修正一致（详见 A5）
- ✅ `CHANGELOG.md [0.32.0]`：「pre-push hook 从写死复制改为软链统一」——历史变更记录，表述准确，不构成过时陈述
- ✅ `orchestrator-template.md:102` / `dispatch-protocol.md:824` / `scripts/README.md:35`：三 hook 口径一致
- ✅ `docs/reviews/` 中旧 review 文档（如 2026-07-21）提及「写死复制」为当时的审查记录，属历史快照，非现行协议陈述，无需改动

**结论**：ALIGNED。未发现其他残留「pre-push 写死复制 / 必须重装」的过时陈述。

### A4: 测试覆盖

本次变更为纯文档陈述修正，不涉及脚本逻辑，无新增测试的语义需求。安装行为本身已有测试覆盖：`unit/install-hook.bats`（4 用例）+ `integration/pre-push-hook.bats`（3 用例）。

**bats 全量实跑输出**（本次审查实测）：
```
598 ok / 0 failed / EXIT=0
（sanity.bats 6 + 其余 @test 总计 592，count-tests.sh 输出：总计 592 个测试用例，与附录 A 一致）
```
覆盖含 `IT_GATE_REAL.1`、`pre-push hook` 三用例（含 T086 回归）、`SG.1-SG.8` self-gate 用例。无回归。

**结论**：ALIGNED。

### A5: 下游影响 + 文档传播

- 非破坏性变更：文档从「必须重装」改为「无需重装」，消除了对用户的错误引导，不改变任何脚本行为或现有项目 gate 行为。
- `README.md:109`（仓库根「升级」节）：「无需重装 hook——软链接会自动指向最新代码」——与本次修正语义一致，无需再改。
- `CHANGELOG.md` 已由 v0.32.0 记录「pre-push hook 从写死复制改为软链统一」，本次文档修正属补全该变更的文档传播，无需新增 CHANGELOG 条目（不属语义变更）。
- 下游文档传播检查：orchestrator-template.md / dispatch-protocol.md / scripts/README.md / platform-notes.md / LIMITATIONS.md 均已核实为正确口径，无需同步。

**结论**：ALIGNED。

### A6: 锚点表覆盖

本次变更未新增任何协议规则，未改变脚本，CHECK 9 锚点表（`check-protocol-consistency.py` SCRIPT_ALIGNMENT_ANCHORS）针对「文档声明的规则 → 脚本关键词」及 gate 脚本反向覆盖，均不涉及本变更。consistency 实跑 0 ERROR（CHECK 1/2/3/4/6/7/8/9 全 PASS）。

**结论**：ALIGNED。

### A7: 设计原则一致性

- **ADR-004（安全网分层——hook 兜底，主动验主流程）**：本次变更不改变 hook 安装机制与兜底分层，仅修正文档使其与实际机制一致，符合 ADR-004「三层防线」设计。
- 未发现未记录的架构决策，无需新增 ADR。

**结论**：ALIGNED。

## 闭环结论

全部 7 项 ALIGNED。允许 commit。无需人工确认标记。
