---
phase: P4
task_id: TAG0013-script-consistency
type: implementation
parent: P2-design.md
trace_id: TAG0013-P4-20260816
status: draft
created: 2026-08-16
agent: implementer
---

implementation_dir: agate/scripts/

# P4 实现记录 — agate 脚本一致性批（RM-AG0015 / RM-AG0017 / RM-AG0018 剩余）

> 上游：P2-design.md（approved，候选方案 A）+ P2-review.md（approved，BLOCKER-1 修复已纳入）
> \+ P3-test-cases.md（19 用例，TC-01..19）。按 P2 方案实现，让红灯转绿。

## 改动清单（3 个脚本，worktree 内 `agate/scripts/`）

### 1. `agate/scripts/check-protocol-consistency.py`（CHECK 10 + PROTOCOL_DIRS 扩展 + BLOCKER-1）

| 改动点 | 实现 |
|--------|------|
| `SCRIPT_REF_RE`（P2 §2 步骤 1） | 新增模块级正则，白名单形状：`check-*` / `agate-*`（连字符与下划线两形，覆盖 `agate_common.py`）/ 3 hook 薄壳 / `install-hook` / `count-tests.sh` / `ci-gate-backstop.py`。formatters 名天然不匹配 → 豁免②自动成立 |
| `SCRIPT_REF_SCAN_FILES` / `SCRIPT_REF_SCAN_DIRS`（P2 §2 步骤 2） | 显式文件集 = `PROTOCOL_FILES | {AGENTS.md, agate/AGENTS.md, agate/CONTEXT.md, agate/UPGRADING.md, agate/scripts/README.md}`；目录集复用扩展后的 `PROTOCOL_DIRS`；`CHANGELOG.md` 单独加入作叙事文件 |
| `check_script_name_refs`（P2 §2 步骤 3） | 扫描面逐行 `finditer`；判定顺序：a. token∈`agate/scripts/` 实际文件名 → 合法；b. `count-tests.sh` → 校验 `agate/tests/scripts/count-tests.sh` 存在（豁免④同名不同目录）；c. 3 hook 薄壳 → 豁免③；d. formatters 目录比对 → 豁免②（forward-defense，当前不可达）；e. `agate/UPGRADING.md` 整文件跳过（豁免①）；f. `agate/scripts/README.md` 退役名 3 个 → 豁免⑤。未命中 → 协议文件 `rep.error`，叙事文件（CHANGELOG）聚合单条 WARNING |
| `PROTOCOL_DIRS` 扩展（P2 §1） | `("agate/assets/", "agate/phase-cards/", "agate/rules/")`（BDD-4） |
| `CHECKS` 追加（P2 §2 步骤 4） | `("CHECK 10 协议文档脚本名引用漂移", check_script_name_refs)` |
| main() 状态匹配修复（BLOCKER-1，P2-review 强制） | `e["check"].startswith(key)` → `e["check"].split("-")[0] == key`（error/warning 两处），避免 `"CHECK10-scriptref".startswith("CHECK1")` 前缀碰撞 |
| 模块 docstring（非阻塞 5） | 补一行 `CHECK 10  协议文档脚本名引用漂移（白名单形状对照 agate/scripts/ 实际文件）` |

### 2. `agate/scripts/commit-msg-self-gate.py`（RM-AG0017）

- `_SELF_GATE_RE` 追加 `|README\.md|AGENTS\.md`（根级精确名锚定；CHANGELOG.md 天然豁免）。
- stderr 触发面提示文案同步补 `README.md / AGENTS.md`（避免"提示说 A、实际匹配 B"漂移）。

### 3. `agate/scripts/check-retrospective.py`（RM-AG0018 剩余）

- `if warnings:` 块内追加提醒行：`复盘发现的新缺口请登记 DEBT/roadmap（技术债清单 / 路线图）`。
- 只写在 `if warnings:` 内 → RT.1 空输出约束不破（BDD-11）；exit 0 不变。

## 自测结果（自查 ≠ P5 gate）

| 验证项 | 结果 |
|--------|------|
| 新增用例（TC-01..19 所在 3 个单元测试文件） | `36 passed`（13 CHECK10 + 4 self-gate + 2 复盘 + 17 既有） |
| 全量 pytest（除下方 [SCOPE+] 冲突用例 deselect） | `767 passed, 2 skipped, 1 deselected` |
| ruff | `All checks passed!`（~/.venvs/agate-dev/bin/ruff） |
| consistency | `0 ERROR / 279 WARNING`；CHECK 10 仅 CHANGELOG 聚合 1 条 WARNING（`叙事文件含无法解析的脚本名引用（聚合提醒）: check-windows-smoke.sh [CHANGELOG.md:17]`）——非 CHANGELOG 漂移 = 0（增量性成立） |
| count-tests.sh | `总计：770 个测试用例`（基线 751 + 19 新增） |

## [SCOPE+] 报告

[SCOPE+ from P4] 既有集成测试 `agate/tests/integration/test_commit_msg_self_gate_integration.py::test_csg_1_non_trigger_no_warning` 断言"暂存根级 README.md → 无 self-gate WARNING"，这正是 RM-AG0017 声明的**缺陷行为**（P1 §1.2 / §5 表：README.md 现行 ❌ 触发，扩展后 ✅ 触发）。P3 仅追加了单元测试（TC-14），未覆盖/未更新该集成测试 → 本实现落地后该用例转红（README.md 现在正确触发 WARNING，输出含 self-gate-review 帮助文案）。该测试文件不在 P2 files_to_read / P3 test_code_dir（`agate/tests/unit/`）范围内，按约束我不改测试——需主 Agent 决策：更新该集成测试断言为"README.md 触发"（与 BDD-6 语义一致），或另立处理。这是唯一一处"既有用例被本需求语义破坏"，其余全量 767 用例绿。

## [DESIGN_GAP]

无（实现严格按 P2 候选方案 A；未自主做 P2 未指定的决策）。

## 回归锁定对照（P3 §2）

- TC-04/05（BLOCKER-1 real main() 驱动）：实现后 CHECK 10 报 ERROR/WARNING 时 CHECK 1 状态行保持 ✅ PASS；旧逻辑 `startswith("CHECK1")` 对 `"CHECK10-scriptref"` 为 True 的根因已显式锁定在测试中。
- TC-06..10（豁免①-⑤）：按序实现，全部转绿。
- TC-16/17/19（回归锁）：既有行为未回归（CHANGELOG 豁免、agate/*.md 触发、RT.1 空输出）。
