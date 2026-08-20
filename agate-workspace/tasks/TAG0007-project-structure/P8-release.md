---
phase: P8
task_id: TAG0007
type: release
parent: P7-consistency.md
trace_id: TAG0007-P8-20260820
status: draft
created: 2026-08-20
agent: implementer
---

# P8 — 发布准备（agate 项目结构管理机制：RM-AG0008 骨架脚手架 + RM-AG0009 CODE-MAP 架构演进纪律）

> P8 releaser 模式：本文件只产出发布准备建议，**不执行 git commit/tag/bump-version**——由主 Agent
在 gate 验证通过后亲自执行。CHANGELOG.md 正文已按 P8-dispatch-context-implementer.md 约束 3 的
授权直接编辑（见下文「CHANGELOG 更新确认」），README.md / README.zh-CN.md version badge 未改动。

## 包声明核对（单包发布）

P2-design.md frontmatter `packages: [phase-cards, execution-roles, templates, scripts]`。按
dispatch-context 约束 1 核实：agate 是单一协议仓库，无独立子包发布结构（无 per-package 版本
文件），P2 的 `packages` 字段是**改动范围分类**，不是多包发布场景清单——四个分类均已在下方
「CHANGELOG 更新确认」中体现，不需要拆批发布、不需要各自独立 bump。**单包发布，无 SCOPE_GAP**
（同类先例：TAG0017 的 P8-release.md「包声明核对」节）。

## bump_type

`bump_type: minor`

## 版本号变更确认（建议值，主 Agent 会实际执行）

- 当前版本（README.md / README.zh-CN.md badge）：`v0.55.0`
- 建议新版本：**`v0.56.0`**
- 判定依据：
  - 本任务新增了两个全新协议机制（RM-AG0008 骨架脚手架 + RM-AG0009 CODE-MAP 架构演进纪律），
    均为**向后兼容的新能力**——`project_phase`（P1）、`code_map_new_files_count`/
    `code_map_reviewed_count`（P7）均为可选 frontmatter 字段，缺失时行为与改动前逐字节一致；
    `gate_p2`/`gate_p4`/`gate_p7` 新增判定分支均为纯增量条件（字段不存在或非目标值时不触发新
    检查），12 个新增回归测试用例已验证该向后兼容性 → **minor**。
  - 无破坏性变更：未删除/修改任何既有字段语义，未改变任何既有 CLI flag 或既有 gate 判定分支的
    既有行为 → 排除 major。
  - 核实结论：与 dispatch-context 建议一致，**采用 minor，v0.55.0 → v0.56.0**。同类先例：
    TAG0017（v0.54→v0.55，minor）、TAG0012（协议机制增强批，v0.51→v0.52，minor）。

## CHANGELOG 更新确认

已直接编辑 `/home/kity/oclab/agate/.worktrees/agate-TAG0007/CHANGELOG.md`：在 `[0.55.0]` 节之上
新增 `## [0.56.0] - 2026-08-20` 节，含：
- 「新增」小节：RM-AG0008（0→1 骨架脚手架：`project_phase: bootstrap` 字段、`P2-skeleton.md`
  产出、`skeleton-template.md` 参数化模板、`gate_p2` 新增判定）+ RM-AG0009（CODE-MAP 架构演进
  纪律：`agents/CODE-MAP.md` 维护物、`code-map-template.md`、「新增文件核对表」机制、
  `gate_p4`/`gate_p7` 新增判定即两层 pairing 校验、consistency-reviewer CODE-MAP 核对职责）+
  关联 BDD 覆盖说明（11 条全覆盖，RM-AG0008 BDD-1~5 / RM-AG0009 BDD-6~11）
- 「已知遗留」小节：DEBT0016 + DEBT0017 各一段简述

格式参照现有 `[0.55.0]` 节结构（三级标题「新增」+ 分组小标题）。`grep -c "## \[0.56.0\]"
CHANGELOG.md` = 1（已核实）。**未修改 README.md / README.zh-CN.md 的 version badge**（`git diff
--stat README.md README.zh-CN.md` 无输出，已核实，留给主 Agent 执行）。

## debt_check

`debt_check: reviewed`

核对 `{AGATE_WORKSPACE}/debt/tech-debt.md`，本任务本轮新登记 2 条债务，均 `status: open`、
`task_id: TAG0007`：

| DEBT id | 状态 | 一句话说明 |
|---------|------|-----------|
| DEBT0016 | open | `check-gate.py` 的 `gate_p4` 中 CODE-MAP.md 路径用本地"task_dir 向上两级"推导，未调用 `agate_common.resolve_workspace` 权威解析函数；标准两级嵌套场景下代数等价，但非标准布局存在潜在分歧——本轮登记，留待后续任务改用权威函数并补边界回归测试后关闭。 |
| DEBT0017 | open | `check-gate.py` 的 `gate_p4`「## 新增文件核对表」子串判定在自指/dogfooding 场景下存在假阴性（说明性文字可误判为已满足），且 TAG0007 自身 P4 产出未对新增文件逐条打标准 CODE-MAP 标记——本轮登记，留待后续任务改整行匹配 + 补齐自我应用标记后关闭。 |

两条的 `closure_criteria` 均为"留待后续任务处理"性质，不是本任务范围内必须完成的收尾项，
**不建议本次改为 closed**（与 TAG0017 场景不同——TAG0017 的 5 条债务继承自更早任务且本轮已
满足 closure_criteria；TAG0007 的 2 条是本轮才发现且明确设计为留待未来处理）。

## 发布检查命令与结果

沿用 P0-brief.md `env_constraints.test_cmd` 声明的命令（不用 `--strict`），汇总本任务全程已
验证的结果（引用 P5-test-results/unit.md + P6-evidence/test-output.log 既有证据，未重新独立
复核）：

| 命令 | 结果 |
|------|------|
| `python3 -m pytest agate/tests/ -q --tb=no` | 1028 passed, 2 skipped, 0 failed |
| `python3 agate/scripts/check-protocol-consistency.py`（默认模式） | 0 ERROR |
| `bash agate/tests/scripts/count-tests.sh` | 1030 个测试用例 |
| `shellcheck -S warning agate/scripts/*.sh` | 0 issue |

> 上述命令是否可直接判定为本次 P8 gate 的"发布检查命令全部 exit 0"证据，取决于主 Agent 执行
`check-p6-provenance.py --audit7-only` 后的 `AUDIT7_RESULT` 判定——本 releaser 不越权代主 Agent
做该判定，仅如实转述已有证据。

## Lessons Learned

1. **复用既有机制模板时，字段对应关系是最容易写反的地方，即使有源码可参照**：P2 review 首轮
   打回的问题即 CODE-MAP 与 DESIGN_GAP 双轨判定模式的 pairing 字段对应关系错误——`code_map_new_
   files_count`/`code_map_reviewed_count` 语义上应分别对应既有 `design_gap_count`/`design_gap_
   reviewed_count`，但首轮设计把对应关系写反了。教训：复用既有机制的参数化模板不是"看着抄一遍"，
   而要逐字段核对语义对应方向，源码在手不代表不会写反。
2. **self-gate 应在 commit 前做，而非事后补救**：本任务的 self-gate 审查是事后补做的，虽然
   补救成功且发现了 5 处真实的文档传播缺口（新机制字段在部分协议文档中未同步提及），但这类
   缺口如果在 commit 前的 self-gate 阶段就发现，修复成本远低于事后补丁。教训：self-gate 的时序
   本身就是质量保障的一部分，不能把它当成"最后补一道保险"的可选步骤。
3. **dogfooding/自指场景下 gate 判定逻辑的字符串匹配容易脆弱**：DEBT0017 的根因是 `gate_p4`
   用子串包含（`in`）判定"是否已补新增文件核对表"，在自指场景下——任务自己的产出文档里用
   说明性文字描述"给协议卡片新增了一个标题叫『## 新增文件核对表』的小节"——这段元描述文字本身
   就命中了子串匹配，导致真正应该触发的 WARNING 被静默跳过。教训：未来新增类似"检测某标题/
   标记是否存在"的 gate 检查时，应优先用整行匹配或结构化正则（如 `^## 标题\s*$`），而非子串
   包含判定，尤其是在协议自身会产出"描述协议机制"的文本时，字符串匹配的假阳性风险显著更高。

## 临时资源清单

**本任务全程未启动任何临时服务/进程/数据库/端口，无开发安装**（纯脚本 + 协议文档改动，静态
验证：pytest 单元测试 + `check-protocol-consistency.py` 静态扫描 + shellcheck 静态检查）。

- 临时服务/进程：无
- 临时数据（测试数据库/临时文件目录）：无
- 开发安装（editable install/全局包）：无

如实记录：**无临时资源**，主 Agent READY 收尾检查该项可直接勾选通过，无需额外清理动作。

## PROD_TOUCHED 声明

`[PROD_NOT_TOUCHED]` —— 本任务无生产环境接触，全程未触及生产环境/生产数据/生产 API。
