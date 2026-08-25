---
phase: P8
task_id: TAG0024
type: release
parent: P7-consistency.md
trace_id: TAG0024-P8-20260825
status: draft
created: 2026-08-25
agent: implementer
bump_type: minor
debt_check: reviewed
---

# P8 发布准备 — TAG0024（agate-md-field-set 工具链批）

## 1. bump_type 判定

**建议：`minor`**

理由（新增 CLI 能力 vs 纯 bug fix 的权衡）：

- 本任务新增了一个全新的 CLI 工具 `agate-md-field-set.py`（含配套
  `agate-md-field-set-gate-commands.py` 子命令），提供"写入即校验"的结构化字段写入能力
  （RM-AG0048 一期）——这是**面向用户可见的新增能力**，不是内部重构或修复，语义上属于
  "加功能"，按 semver 惯例应落在 minor 而非 patch。
- 随附的 DEBT0019/DEBT0020 修复（check-gate.py `_check_roadmap_done()` 列数校验 + 仓库根锚定）、
  RM-AG0049/RM-AG0050（phases.yaml 文档自洽 NIT）、BDD-30 SCOPE+（check-pruning.py 测试隔离修复）
  单独看都是 patch 级别的健壮性修复，但它们与新增能力同批次交付、不可分割为独立发布单元。
- 判定规则："新增能力优先于批次内纯 bug fix 的 patch 判定"——只要批次中有一项达到 minor
  门槛（新增 CLI 能力），整个发布单元的 bump_type 取批次内最高级别，即 `minor`。
- 未发现任何破坏性变更（无 API 删除/语义反转/向后不兼容的行为改变）：新工具是纯新增，
  既有 `agate-md-field-get.py` 等工具的行为未被触及；DEBT 修复是"修正未声明行为"而非
  "改变已声明契约"；phases.yaml 文档自洽修复不改变任何已判定的 gate 逻辑输出。故不判定为
  `major`。

## 2. 建议的新版本号

当前 `v0.62.0` → 建议 **`v0.63.0`**

## 3. 建议的 CHANGELOG.md 条目文案

以下为**建议文案**，供主 Agent 直接采纳或调整后写入 CHANGELOG.md（本 releaser 未修改
CHANGELOG.md 本身）：

```markdown
## [0.63.0] - 2026-08-25

### 新增（TAG0024：工具链批立项，RM-AG0048 一期 + DEBT0019/20 + RM-AG0049/50）

- **`agate-md-field-set` 结构化字段写入工具（RM-AG0048 一期）**：新增
  `agate/scripts/agate-md-field-set.py`（标量字段/简单 list 字段/`gate_commands` 正文块写入
  + 证据字段拒绝端 + 跨文件提示）与配套 `agate-md-field-set-gate-commands.py`
  子命令，key 从 `phases.yaml` task_fields 白名单限定、value 写入时按值域校验、格式由工具
  统一生成——消灭 subagent 手写 frontmatter 的格式摩擦（P1-gate-diagnosis 实证）；核心设计
  遵循"同源铁律"（与 gate 共用 `phases.yaml` 权威源 + resolve-entry 版本链）与"自描述"
  （`--list`/`--help`/错误提示给合法值），"零协议知识 subagent 照提示填对"为验收判据。
  二期（证据字段自动写入/账本留痕/跨文件预检）另行设计。
- **`check-gate.py` roadmap-done 校验健壮性修复（DEBT0019/DEBT0020）**：
  `_check_roadmap_done()` 表格解析由"实际列数 ≥8"改为**精确匹配 9 列**（含首尾空列），
  单元格内含字面 `|` 字符时整行跳过而非错位取值（DEBT0019，消灭潜在漏判/误判）；
  `gate_p8()` 调用点的 roadmap.md 路径定位由"相对 CWD 硬编码拼接"改为
  `git rev-parse --show-toplevel` 仓库根锚定，非仓库根 CWD 调用不再静默失配，
  非 git 仓库环境下输出区分性 stderr 提示（DEBT0020）；均配套回归用例
  （`test_check_gate.py` BDD-20~24）。
- **`phases.yaml` 文档自洽修复（RM-AG0049/RM-AG0050）**：P4 阶段 `outputs` 补齐
  `P4-review.md` 声明（`required: true`），消除"产出声明与 gate 实际要求不对称"
  （RM-AG0049）；统一 P6.5 定位表述为"挂载于 P6→P7 转移的强门槛子阶段，不是独立 phase
  值"（以 `state-machine.md` 口径为准），消除 phases.yaml 与 state-machine.md 两处叙述
  不一致（RM-AG0050）。
- **`check-pruning.py` 测试隔离修复（BDD-30，SCOPE+ 发现）**：`_staged_source_count`
  改为以 `task_dir` 自身所属仓库定位，消除跨仓库/多 worktree 场景下的测试隔离缺口。
- **ADR-011**：新增架构决策记录，落定本批次工具链设计的关键决策依据。
- 新增回归用例覆盖 BDD-1~30（含 RM-AG0048 一期 BDD-1~19、DEBT0019 BDD-20~21、
  DEBT0020 BDD-22~24、RM-AG0049 BDD-25~26、RM-AG0050 BDD-27~28、跨 issue 约束 BDD-29、
  BDD-30 SCOPE+）；全量 pytest 1285 passed / 2 skipped / 0 failed；ruff 0 违规；
  consistency 0 ERROR；P6.5 judge 独立评审 `status: passed`；P7 一致性核对 BLOCKER=0。
```

## 4. roadmap.md 回写建议

建议将以下 3 条状态由 `scheduled` → `done`（roadmap.md 表格「状态」列，第 3 数据列）：

| RM 条目 | 当前状态 | 建议状态 | 依据 |
|---|---|---|---|
| RM-AG0048 | scheduled | done | 一期（agate-md-field-set 完整写字段工具）已在本任务 P4 完整实现，P5 测试全绿，P6 验收通过，P6.5 独立 judge 评审 `status: passed`，P7 一致性核对 BLOCKER=0。design note §10 十一条验收锚已在实现中逐条覆盖（见 P4-implementation-md-field-set-tool.md / P6-batch-results-md-field-set-tool.md）。 |
| RM-AG0049 | scheduled | done | phases.yaml P4 `outputs` 已补 `P4-review.md` 声明，`check-structure-consistency.py` 同步核对无遗漏（见 P4-implementation-phases-yaml-consistency.md）；对应 BDD-25/26 用例通过。 |
| RM-AG0050 | scheduled | done | phases.yaml 与 state-machine.md 的 P6.5 定位表述已统一为"强门槛子阶段"口径，`check-gate.py`/`check-judge-verdict.py` 消费端核对不受影响（见 P4-implementation-phases-yaml-consistency.md）；对应 BDD-27/28 用例通过。 |

三条均在本任务 P4→P7 完整交付并验收通过，符合 RM-AG0043（P8 roadmap-done 校验）对"关联
RM 条目状态须为 done"的阻断性要求，回写后可通过该 gate 检查。实际表格编辑由主 Agent 执行
（roadmap.md 是主 Agent 维护的看板类文件，本 releaser 不直接改写）。

## 5. debt_check 核对结论

### DEBT0019：check-gate.py._check_roadmap_done() 列数完整性校验缺失

closure_criteria 逐条核对：

| 验收条件 | 是否满足 | 证据 |
|---|---|---|
| 新增防护逻辑（列数校验，非法列数跳过/WARNING） | ✅ 满足 | `check-gate.py` L1181-1211：`_ROADMAP_EXPECTED_COLS = 9` 常量 + `_check_roadmap_done()` 内 `if len(cols) != _ROADMAP_EXPECTED_COLS: continue`，列数不匹配即整行跳过 |
| 对应回归用例（构造含 `\|` 字符的行验证不误判） | ✅ 满足 | `test_check_gate.py` L1582-1721：BDD-20（标题列含字面 `\|` 导致 10 列，验证不误判/不错位取值）+ BDD-21（列数恰为 9 的既有合法场景回归防呆） |
| 全量测试通过 | ✅ 满足 | P5 结果 1285 passed / 2 skipped / 0 failed（P5-test-results/unit.md） |

**建议：DEBT0019 status 可从 `open` 回写为 `resolved`。**

### DEBT0020：check-gate.py._check_roadmap_done() 调用点路径定位风格不一致

closure_criteria 逐条核对：

| 验收条件 | 是否满足 | 证据 |
|---|---|---|
| 路径定位方式对齐（改用 repo-root 拼接）或加区分性提示 | ✅ 满足 | `check-gate.py` L1236-1244：调用点改用 `git rev-parse --show-toplevel` 取仓库根拼接 roadmap.md 路径；rc != 0（非 git 仓库环境）时输出区分性 stderr `"GATE P8 WARNING: 仓库根不可得（非 git 仓库环境），跳过 roadmap-done 检查"`，不再静默合并为"确实无关联 RM" |
| 回归用例覆盖非仓库根 CWD 调用场景 | ✅ 满足 | `test_check_gate.py` L1670-1721：BDD-22（CWD 非仓库根）+ BDD-23（非 git 仓库环境区分性提示）+ BDD-24（CWD=仓库根既有场景回归防呆） |
| 全量测试通过 | ✅ 满足 | 同上，P5 结果 1285 passed / 2 skipped / 0 failed |

**建议：DEBT0020 status 可从 `open` 回写为 `resolved`。**

实际 tech-debt.md 的 `status:` 字段回写由主 Agent 执行（该文件为主 Agent 维护的债务台账）。

## 6. 临时资源清单

**本任务全程未启动任何临时服务/进程/数据库。** 全部改动为纯脚本改动
（`agate/scripts/agate-md-field-set.py`、`agate/scripts/agate-md-field-set-gate-commands.py`、
`agate/scripts/check-gate.py`、`agate/scripts/check-pruning.py`）+ 纯文档/规则改动
（`agate/rules/phases.yaml`、`agate/state-machine.md` 等）+ 测试代码新增，无需运行时环境：

- 临时服务/进程：无
- 临时数据（测试数据库/临时文件目录）：无（pytest 使用 `--basetemp=.pytest-tmp`，属既有测试
  基础设施常规产物，非本任务新增，且已由 pytest 自身生命周期管理）
- 开发安装（editable install / 全局包安装）：无
- 无需 READY 收尾阶段的运行时清理动作

## 7. 发布单元与验证命令（供主 Agent 执行）

P2-design.md packages 声明：`[agate-scripts, agate-rules, agate-docs, agate-tests]`
（单一逻辑发布单元，非多包拆分，共享同一版本号 `v0.63.0`）。

发布检查命令（P2-design.md `gate_commands`）：

```bash
python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -v          # P3
python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -q --tb=no  # P5
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only              # P5_consistency
shellcheck agate/scripts/*.sh                                                          # P5_shellcheck
bash agate/tests/scripts/count-tests.sh                                               # P5_count
~/.venvs/agate-dev/bin/ruff check agate/                                              # P5_ruff
```

P5-test-results/unit.md 已记录本批次执行结果：1285 passed / 2 skipped / 0 failed，
`ruff check` All checks passed，`check-protocol-consistency.py` 0 ERROR
（详见 P5-test-results/unit.md）。是否需要在 bump-version + commit + tag 后重新执行
`gate_commands.P5`，按 P8 phase-card「gate 规则」的 AUDIT7 条件化表述判定
（`check-p6-provenance.py --audit7-only` 的 `AUDIT7_RESULT` 决定复用 vs 重跑），
由主 Agent 亲自执行判定与验证，本 releaser 不代为判定。

## 8. Lessons Learned

1. **[流程] roadmap-done gate 前置依赖顺序**：RM-AG0043 引入的 P8 roadmap-done 校验要求
   "先回写 roadmap 三条 done，才能过 P8 gate"，而 roadmap 回写的合理依据（P6.5 judge 通过 +
   P7 一致性核对 BLOCKER=0）恰好要到 P7 才齐备——P8 releaser 产出建议、主 Agent 统一在
   gate 验证前完成回写，是当前协议下唯一可行的时序，值得在后续任务的 P8 卡片说明中显式提示
   "roadmap 回写在 P8 releaser 产出之后、gate 验证之前执行"，减少每次都要重新推导时序的成本。
   来源任务：TAG0024，2026-08-25。
2. **[架构] 同批次多问题共享一次 minor bump 的判定规则值得沉淀**："新增能力 + 若干 patch 级
   修复"同批次交付时，bump_type 取批次内最高级别（本例为 minor）而非逐条打分求和——这条
   规则目前只在 dispatch-context 里以自然语言口头提示，未落进任何 checklist 或 rules/*.yaml，
   下次判定仍需人工重新推导。来源任务：TAG0024，2026-08-25。
3. **[测试] 表格解析类 gate 逻辑的"合法列数"应作为具名常量而非魔数**：DEBT0019 修复中把
   `_ROADMAP_EXPECTED_COLS = 9` 提为模块级常量并注释推导依据（7 数据列 + split 首尾 2 个
   空字符串），比原先散落在函数体内的字面量 `>= 8` 更易在未来 roadmap.md 表格结构变化时
   被正确同步——这类"魔数 → 具名常量 + 推导注释"的模式值得作为 review checklist 一项。
   来源任务：TAG0024，2026-08-25。

## 9. PROD 标记

`[PROD_NOT_TOUCHED]`——本任务全程未涉及任何生产环境/生产数据/生产 API 的读写。
