---
phase: P8
task_id: TAG0017-toolchain-fixes
type: release
parent: P7-consistency.md
trace_id: TAG0017-P8-20260820
status: draft
created: 2026-08-20
agent: implementer
---

# P8 — 发布准备（协议工具链修复批：DEBT0010/11/12/14/15）

> P8 releaser 模式：本文件只产出发布准备建议，**不执行 git commit/tag/bump-version**——由主 Agent 在 gate 验证通过后亲自执行。CHANGELOG.md 正文已按 P8-dispatch-context-implementer.md 约束 5 的授权直接编辑（见下文「CHANGELOG 更新确认」），README.md version badge 未改动。

## 包声明核对（单包发布）

P2-design.md frontmatter `packages: [gate-scripts, hooks-shell, phase-cards, self-gate-template, platform-notes, agent-roles]`。按 dispatch-context 约束 2 核实：agate 是单一协议仓库，无独立子包发布结构（无 `package.json`/`setup.py` per-package 版本文件），P2 的 `packages` 字段是**改动范围分类**，不是多包发布场景清单——6 个分类均已在下方「改动清单」中体现，不需要拆批发布、不需要各自独立 bump。**单包发布，无 SCOPE_GAP。**

## bump_type

`bump_type: minor`

## 版本号变更确认（建议值，主 Agent 会实际执行）

- 当前版本（README.md / README.zh-CN.md badge）：`v0.54.0`
- 建议新版本：**`v0.55.0`**
- 判定依据（AGENTS.md/dispatch-prompt.md「版本 bump 判定」规则核实）：
  - 本任务新增了两处向后兼容的新能力：① `check-protocol-consistency.py` 新增 `--strict-errors-only` CLI flag（互斥组新增，不改变既有 `--strict`/默认模式行为）；② 3 处 hook 薄壳新增 `AGATE_PYTHON` 环境变量识别机制（未设置时行为不变）；③ SELF-GATE 命名模板新增 `{task_id}` 占位符（协议文档层新增字段位）——均属于"加功能，向后兼容"→ minor。
  - 同时修复了 5 条真实缺陷（DEBT0010/11/12/14/15），若单独看修复本身接近 patch 级别，但与上述新增能力混合发布时，按规则取更高等级 → **minor 优先于 patch**。
  - 无破坏性变更（未改变任何既有 API/CLI flag 的既有行为，`--strict` 语义不变，探测循环未设置 `AGATE_PYTHON` 时行为路径不变）→ 排除 major。
  - 核实结论：与 dispatch-context 建议一致，**采用 minor，v0.54.0 → v0.55.0**。同类先例：TAG0012（协议机制增强批，v0.51→v0.52，minor）。

## CHANGELOG 更新确认

已直接编辑 `/home/kity/oclab/agate/.worktrees/agate-TAG0017/CHANGELOG.md`：在 `[0.54.0]` 节之上新增 `## [0.55.0] - 2026-08-20` 节，含：
- 「新增」小节：5 条 DEBT 修复（DEBT0010/RM-AG0028-DEBT0015/DEBT0011/DEBT0012/DEBT0014）各一段，覆盖对应 BDD 组（BDD-1~4 / BDD-5~6 / BDD-7~8 / BDD-9 / BDD-10~12，合计 12 条 BDD 全覆盖）
- 「关键机制」小节：`is_gate_meta_key` 共享判据函数、`--strict-errors-only`、SELF-GATE `{task_id}` 命名、`AGATE_PYTHON` 探测增强
- 「技术债关闭」小节：DEBT0010/11/12/14/15 五条逐一列出修复状态 + closure_criteria 满足情况

格式参照现有 `[0.54.0]` 节结构（三级标题「新增」+ 分组小标题 + 技术债小节）。**未修改 README.md / README.zh-CN.md 的 version badge**（按约束 3 留给主 Agent 执行）。

## debt_check

`debt_check: reviewed`

核对 `agate-workspace/debt/tech-debt.md`，本任务对应 5 条登记条目均为 `status: open`，closure_criteria 经 P4-implementation.md 自查证据核对已全部满足，**建议主 Agent 在 bump 时机将以下 5 条状态改为 `closed`**（本 P8 releaser 不直接编辑 tech-debt.md，仅建议）：

| DEBT id | 登记时 task_id | closure_criteria 满足情况 |
|---------|---------------|---------------------------|
| DEBT0010 | TAG0016 | 4 脚本统一改用 `is_gate_meta_key`（P4批次1）；新增回归用例覆盖 `P3_timeout_seconds`/`P5_timeout_seconds` 场景；全量 pytest 1011 passed 0 failed |
| DEBT0011 | TAG0016 | SELF-GATE.md 命名模板补 `{task_id}`（P4批次3）；`protocol-alignment-review.md` 新增写前防覆盖检查段落；全量回归通过 |
| DEBT0012 | TAG0016 | `check-protocol-consistency.py` 新增 `--strict-errors-only`（P4批次4）；`P2-design.md` gate_commands 声明示例改用新 flag，不再推荐 `--strict` 放 `&&` 链路中间；回归测试覆盖新旧模式矩阵 |
| DEBT0014 | TAG0017 | 3 处 hook 薄壳逐字同步增强（P4批次5）；`AGATE_PYTHON` 机制文档化（platform-notes.md + AGENTS.md）；集成测试覆盖探测跳过 + 显式指定两类场景；未做"已在 Windows 实测通过"断言（遵守 verification_env 约束） |
| DEBT0015 | TAG0017 | `env_constraints` 声明性 vs 执行性边界文档化（P2 卡片 + architect.md，P4批次2）；`P4-implementation.md`「自查≠gate」节新增 dist 产物确认提醒 |

## 发布检查命令与结果（单包，agate 协议仓库整体验证）

沿用 P0-brief.md `env_constraints.test_cmd` 声明的三条独立命令（DEBT0012 修复后不再用 `&&` 串联 `--strict`）：

| 命令 | 结果 | 来源 |
|------|------|------|
| `python3 -m pytest agate/tests/ -q --tb=no` | 1011 passed, 2 skipped, 0 failed | P4-implementation.md「自查测试结果汇总」（review-fix 后全量），P5-test-results/ 待主 Agent 复用判定（audit7） |
| `python3 agate/scripts/check-protocol-consistency.py`（默认模式） | 0 ERROR，314 WARNING（存量基线，未新增） | 同上 |
| `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` | EXIT=0 | 同上，本任务新增 flag 自身验证 |
| `bash agate/tests/scripts/count-tests.sh` | 未见 P4 自查记录单独跑此命令，但已被 P5/P6 阶段验证覆盖（P5-test-results/ 存在） | 需主 Agent 在「gate 规则」执行时按 audit7 结果决定是否重跑 |

> 上述命令是否可直接判定为本次 P8 gate 的"发布检查命令全部 exit 0"证据，取决于主 Agent 执行 `check-p6-provenance.py --audit7-only` 后的 `AUDIT7_RESULT` 判定（见 dispatch-context 引用的 gate 规则）——本 releaser 不越权代主 Agin 做该判定，仅如实转述 P4 自查证据。

## Lessons Learned

1. **共享判据函数是"改一处忘改一处"缺陷的正确解法，但要守住抽象边界**：DEBT0010 的 4 处解析脚本本可各自内联修复，P2 选择抽取 `is_gate_meta_key` 共享函数，但明确不吞并语义不同的 `project_module` 精确匹配（P2-design.md §1.3 R7）——共享判据函数只应收敛"同性质、同变化方向"的判据，混入语义不同的判据会造成过度抽象和未来修改时的误伤范围扩大。
2. **`&&` 链路 + 严格模式退出码组合是一类容易被管道验证方法掩盖的缺陷**：DEBT0012 的根因（`--strict` WARNING-only 也非 0，与 `&&` 链路短路组合）此前长期未被发现，正是因为历史验证习惯用 `command | tail -N; echo $?` 这类管道模式，`$?` 实际取的是 `tail` 的退出码而非目标命令的真实退出码。本任务修复时同样在 P4 review-fix 轮踩过一次同类陷阱（HTML 注释被 CHECK 1 误判），提示"验证 exit code 必须避免管道掩盖真实值"应成为协议层面的通用检查习惯，而非仅本次债务的一次性教训。
3. **跨项目反馈（TQC0001/DEBT0014、DEBT0015）暴露的是协议边界认知缺口，不是单点 bug**：Windows Store python3 占位符和 `env_constraints` 声明性/执行性边界，都不是"代码写错了"，而是协议设计时对"声明 vs 强制"这条边界没有显式说明，导致下游用户各自以不同方式踩坑后才反馈回来。修复方式除代码增强外，都同时补了文档边界说明——这提示 protocol 类任务的"债务"很大一部分是文档表达力不足，而非纯代码缺陷，P8/P1 阶段登记债务时应有意识区分这两类根因，避免只想着写代码修复而漏了文档边界澄清。

## 临时资源清单

**本任务全程未启动任何临时服务/进程/数据库/端口，无开发安装**（纯脚本 + 协议文档改动，静态验证：pytest 单元/集成测试 + `check-protocol-consistency.py` 静态扫描 + shellcheck 静态检查）。

- 临时服务/进程：无
- 临时数据（测试数据库/临时文件目录）：无
- 开发安装（editable install/全局包）：无

如实记录：**无临时资源**，主 Agent READY 收尾检查该项可直接勾选通过，无需额外清理动作。

## PROD_TOUCHED 声明

`[PROD_NOT_TOUCHED]` —— 各批次自查记录（P4-implementation.md）逐一标注，本任务全程未触及生产环境/生产数据/生产 API。
