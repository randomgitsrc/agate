---
phase: P3
task_id: TAG0012-protocol-mechanism-fixes
type: test-cases
parent: P2-design.md
trace_id: TAG0012-P3-20260818
status: draft
created: 2026-08-18
agent: test-designer
test_code_dir: agate/tests/unit/
---

# P3 测试用例 — agate 协议机制增强批（TAG0012）

## 0. 测试性质与产出规格

本任务的 P1-requirements.md 23 条 BDD（BDD-1~22 + BDD-15b）不是常规业务功能断言，而是"协议
文档/角色文件是否含 P2-design.md §2.1 改动落点表指定的新增小节/关键词"的存在性断言（P2-design.md
§3.6 已固化测试设计范式）。

- **测试代码目录**：`test_code_dir: agate/tests/unit/`（沿用既有测试目录，不新建独立子目录——本
  任务只新增 1 个测试文件）
- **测试文件**：`agate/tests/unit/test_protocol_mechanism_anchors.py`（新建）
- **gate_commands.P3**（P2-design.md §6 固化）：
  `python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v`
- **组织范式**：参照 `agate/tests/unit/test_check_protocol_consistency.py`，但更简单——不需要
  importlib 加载脚本模块，直接读文件文本 + 关键词 `in` 判断；平台无关（纯文本判断，不依赖
  shell/grep 二进制），覆盖 `windows_smoke` 标记
- **fixture 复用**：使用 `agate/tests/conftest.py` 既有的 session-scoped `agate_root` fixture
  （从 `tests/` 上溯反推最近含 `scripts/+assets/` 的目录，即本仓库的 `agate/` 目录），仓库根
  `repo_root = agate_root.parent`，与 P2-design.md §2.1 表列出的 `agate/xxx.md` 路径写法直接
  对应，未硬编码绝对路径

## 1. BDD → 测试用例映射（28 条 parametrize 用例，覆盖 22 个 BDD 编号）

| 测试 id | 对应 BDD | 目标文件 | 关键词锚点（逐字复用 P2-design.md §2.1 表） |
|---------|---------|---------|------------------------------------------|
| `BDD-1` | BDD-1 | `agate/phase-cards/P0-orchestrator.md` | `同类/影响面预判` |
| `BDD-2` | BDD-2 | `agate/phase-cards/P0-orchestrator.md` | `[P0_STALE]` |
| `BDD-3` | BDD-3 | `agate/state-machine.md` | `时效性校验` |
| `BDD-4` | BDD-4 | `agate/phase-cards/P1-requirements.md` | `同类扫描` |
| `BDD-5` | BDD-5 | `agate/phase-cards/P1-requirements.md` | `verification_env` **且** `supplementable`（AND，见 §2 说明） |
| `BDD-6` | BDD-6 | `agate/phase-cards/P1-requirements.md` | `[P0_STALE:` |
| `BDD-7` | BDD-7 | `agate/assets/execution-roles/analyst.md` | `同类/影响面` |
| `BDD-8` | BDD-8 | `agate/assets/execution-roles/analyst.md` | `缺的是能力还是环境` |
| `BDD-9` | BDD-9 | `agate/assets/execution-roles/analyst.md` | `[P0_STALE]` |
| `BDD-10-可重试` | BDD-10 | `agate/dispatch-protocol.md` | `可重试` |
| `BDD-10-不可重试` | BDD-10 | `agate/dispatch-protocol.md` | `不可重试` |
| `BDD-10-批处理` | BDD-10 | `agate/dispatch-protocol.md` | `批处理` |
| `BDD-10-止损轮次` | BDD-10 | `agate/dispatch-protocol.md` | `止损轮次` |
| `BDD-11` | BDD-11 | `agate/dispatch-protocol.md` | `环境准备职责边界` |
| `BDD-12` | BDD-12 | `agate/dispatch-protocol.md` | `资源密集型默认串行` |
| `BDD-13-命令超时兜底` | BDD-13 | `agate/dispatch-protocol.md` | `命令超时兜底` |
| `BDD-13-层级4` | BDD-13 | `agate/dispatch-protocol.md` | `层级 4` |
| `BDD-13-倍数` | BDD-13 | `agate/dispatch-protocol.md` | `×1.5` |
| `BDD-14` | BDD-14 | `agate/assets/templates/dispatch-prompt.md` | `命令超时兜底` |
| `BDD-15` | BDD-15 | `agate/phase-cards/P2-design.md` | `影响面梳理` |
| `BDD-15b` | BDD-15b | `agate/assets/execution-roles/architect.md` | `影响面梳理` |
| `BDD-16-P2卡` | BDD-16 | `agate/phase-cards/P2-design.md` | `timeout_seconds` |
| `BDD-16-architect` | BDD-16 | `agate/assets/execution-roles/architect.md` | `timeout_seconds` |
| `BDD-17` | BDD-17 | `agate/phase-cards/P5-verification.md` | `资源密集型默认串行` |
| `BDD-18` | BDD-18 | `agate/phase-cards/P5-verification.md` | `环境准备职责边界` |
| `BDD-19` | BDD-19 | `agate/assets/execution-roles/verifier.md` | `环境准备职责边界` |
| `BDD-20` | BDD-20 | `agate/phase-cards/P6-acceptance.md` | `环境准备职责边界` |
| `BDD-21` | BDD-21 | `agate/assets/templates/task-files.md` | `timeout_seconds` |

**拆分说明**：P2-design.md §2.1 表部分行对同一 BDD 列出多个独立关键词锚点（BDD-10 对应
可重试/不可重试/批处理/止损轮次 4 个锚点；BDD-13 对应命令超时兜底/层级 4/×1.5 3 个锚点；
BDD-16 对应 P2-design.md 卡片 + architect.md 两个文件各 1 个锚点）。这些拆成同一 BDD 编号下
的多条子用例（test id 加锚点/文件后缀区分），每条仍可逐条追溯回同一个 BDD 编号，1:1 映射关系
不因拆分而破坏。

## 2. BDD-5 特别设计说明（AND 语义，非逐关键词独立断言）

P2-design.md §2.1 表给 BDD-5（P1-requirements.md 卡片新增 verification_env vs supplementable
边界判断树）列出两个关键词锚点：`verification_env`、`supplementable`。

**红灯核实发现的冲突**：全仓核实（`grep -n "supplementable" agate/phase-cards/P1-requirements.md`）
确认 `supplementable` 当前已在该文件中出现 2 次（L57 `capability_requirements:` 能力需求声明
三态说明 / L116 推进条件 checklist），均是**既有**内容，与 BDD-5 要新增的"verification_env vs
supplementable 边界判断树"小节无关。若按"每个关键词独立生成一条断言"的默认处理方式，
`supplementable` 那一条用例在协议文件尚未被本任务改动的当前阶段就已经为真（假绿），违反 P3
"全部用例目前必须失败"的红灯要求。

**设计决策**：BDD-5 保留为**单条**测试用例，两个关键词逐字保留、不做任何意译/改写（满足
P2-design.md §3.5 约束），但断言逻辑改为 **AND 语义**——同时要求 `verification_env` 与
`supplementable` 都出现在文件中。由于 `verification_env` 目前在该文件中 0 命中，AND 组合断言
现在整体为假（真红灯成立）；P4 落地边界判断树后，两个关键词会在同一小节内共同出现，断言转真
（真绿）。此设计既遵守"逐字复用关键词"的硬约束，又避免了因既有无关文本导致的假绿。

## 3. BDD-22 说明（无独立关键词断言）

BDD-22（`check-gate.py` 是否扩展 `timeout_seconds` 校验，取决于 P2 architect 的分支决定）已由
P2-design.md §3.7 明确决定"不做脚本硬校验，仅文档约定 + 本 grep 断言审计测试"分支。按
dispatch-context 约束 4，BDD-22 自身以"本测试文件存在 + 全部 parametrize 用例可运行（此刻全红）"
为验收标准，不设独立关键词断言——本测试文件本身即是 BDD-22 的落地证据（P2-design.md §3.6/§3.7
已明确"两种结果都是合法收敛"，本任务走文档约定分支，回归拦截压力转移到本测试文件）。

## 4. 红灯验证结果

执行 `gate_commands.P3` 固化命令：

```
cd /home/kity/oclab/agate/.worktrees/agate-TAG0012 && python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v
```

结果：**28 个用例全部 FAILED**（`28 failed in 0.10s`），失败原因均为 `AssertionError`
（关键词锚点缺失），无 `ImportError`/`SyntaxError`/collection error——真红灯（B 类，实现未写导致
失败，测试代码本身无 bug）确认成立，符合 check-tdd-red.py 的 exit 0 判据（assertion failure > 0
且 collection error == 0）。

## 5. 追溯覆盖核对

- P1-requirements.md 全部 23 条 BDD（BDD-1~22 + BDD-15b）均有对应测试用例或明确的"无独立断言"
  说明（BDD-22，见 §3）。
- `ui_affected: false`（P2-design.md frontmatter 已声明），本任务无 UI，不含 Playwright/E2E 用例。
- 未裁剪任何一条 BDD 的测试覆盖。
