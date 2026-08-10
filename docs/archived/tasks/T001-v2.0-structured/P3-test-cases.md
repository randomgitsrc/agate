---
phase: P3
task_id: T001
type: test-cases
parent: P2-design.md
trace_id: T001-P3-20260809
status: draft
created: 2026-08-09
agent: test-designer
---

# T001 — agate v2.0 结构化数据改造（A+B+C+D 四流）：P3 测试用例清单

> TDD 红灯阶段。所有列出的测试代码已写入 worktree，当前对应实现尚未开始（P4），
> 故断言均针对"未来实现应有的行为"，多数用例现处于失败（红灯）状态。
> 角色：test-designer（`~/.agate/assets/execution-roles/test-designer.md`）。

**test_code_dir: `agate/tests/`**（unit/ + regression/ + integration/，按现有目录结构原位改写/新增，未新建独立测试代码目录——P2-design.md §5 固化 P3 gate 命令为 `bats agate/tests/unit/ agate/tests/regression/`，测试代码必须落在既有 `agate/tests/` 树内才能被该 gate 命令发现）

## 0. 产出总览

| 项 | 值 |
|---|---|
| P1 BDD 总数 | 28（BDD-1..28，流 A 15 / 流 B 5 / 流 C 4 / 流 D 4，末条 BDD-28 为自举边界） |
| 新增测试文件 | 1（`agate/tests/unit/check-frontmatter.bats`，10 个 @test） |
| 改写文件（15 个受影响文件，@test 数见下表） | check-gate.bats / check-pruning.bats / check-p6-provenance.bats / check-p6-evidence.bats / check-tdd-red.bats / check-gate-p1-review.bats / check-scope-resolved.bats / check-retrospective.bats / check-p6-format.bats / agate-extract-context.bats / regression/v060-design-gap.bats / regression/v060-p8-internal-only.bats / regression/v060-r4-cached.bats / integration/pre-commit-hook.bats / integration/consistency.bats |
| 轻改写（BDD-25/26/27 落点，非 15 文件清单内，@test 数同样保持不变） | agate-md-field-get.bats（6）/ agate-state-yaml-check.bats（3）/ check-changelog.bats（8） |
| 不改动的 regression fixture | v060-p8-cached.bats（P8 --cached，3）/ v060-yaml-indent.bats（模板 executor_env，P0 字段不迁移，3） |
| `count-tests.sh` 实测总数 | **594**（sanity.bats 6 另计，BDD-11 达标） |
| 当前红灯数（unit+regression 实测） | 23 个 `not ok`（`bats agate/tests/unit/ agate/tests/regression/` 全量实跑），0 个非预期失败 |
| 按流分组 | 流 A → 流 B → 流 C → 流 D 互不阻塞（各流测试断言的实现点相互独立，P4 可严格按 A→B→C→D 串行推进，无循环依赖） |

## 1. 594 配平表（FIND-7 机制，硬约束 1）

**核算口径**：594 = 354（P2-design.md 列出的 15 受影响文件基线）+ 240（其余文件基线）。新增
`unit/check-frontmatter.bats`（N=10 个 @test，测试新交付物 `agate-frontmatter-check.py` /
`check-frontmatter.sh`）通过在 15 文件内**移减 M=10 条重复/低价值断言**配平，N=M=10，
`count-tests.sh` 实测严格回落到 594（已验证，见上表）。

> 落地方式说明：移减操作采用"真删除"（彻底移除该 `@test` 块，不留同名占位）而非仅改写断言内容——
> 因为仅改写断言内容不会改变文件内 `@test` 计数，无法配平新增的 10 条。删除的 10 条均为与新校验器
> 或既有相邻用例存在概念重复的低边际价值断言（见下表"移减理由"），删除后每个文件仍保留至少一条
> 覆盖同一底层机制的用例，不构成裸删（无替代覆盖）。

| # | 移减位置（原用例名） | 原文件 | 移减理由 | 该文件新增的替代 BDD 覆盖（同一文件内，@test 数净不变） |
|---|---|---|---|---|
| 1 | G2.12 `P2-design.md 缺字段（<4）期望 exit 1` | check-gate.bats | 与 BDD-6（`check-frontmatter.bats` CF.5 已覆盖"P2 必填字段缺失即报错"）概念重复；G2.27（缺 candidate_count）保留同类"必填字段缺失"回归代表 | `G_BDD1.1`：P2 四字段经 frontmatter 声明仍被门禁正确读取 |
| 2 | G6.8 `P6 小写 fail（空格）被计为 FAIL` | check-gate.bats | 与 G6.7（小写 fail 冒号变体）概念重复，同一"大小写不敏感"机制的第二个正则变体分支；G6.7 保留代表 | `G_BDD16.1`：P6 frontmatter pass/fail 汇总声明存在时门禁基于该汇总判定（非正文 grep 计数） |
| 3 | G2.23 `P2 方案 Recommended（多词方案名）期望 exit 2` | check-gate.bats | 与 G2.21（Alternative/多词方案名变体）概念重复，同一"多词标题正则"机制的第 N 个措辞变体；G2.21 保留代表 | `G_BDD9.1`：P2-design.md 旧格式（四字段仅正文，frontmatter 无这些字段）仍被正确读取（回退路径） |
| 4 | G2.15 `P2 方案一 + 方案二 期望 exit 2` | check-gate.bats | 与 G2.14（方案 A 有空格变体）概念重复，同一"中文数字/字母编号"标题正则的变体分支；G2.14 保留代表 | `G_BDD10.1`：P2 candidate_count 在 frontmatter 与正文声明不同值时以 frontmatter 为准 |
| 5 | F7 `--fix: lowercase fail:（冒号无空格）→ auto-fix to FAIL:` | check-p6-format.bats | 与 F9（fail 空格变体自动修复）概念重复，同一归一化 sed 链的第二个标点变体；F9 保留代表 | `F_BDD17.1`：--check 行首 `- PASS｜FAIL BDD-NN:` 格式被识别为有效逐条结果 |
| 6 | F11 `--check: summary line - PASS：34 → exit 1` | check-p6-format.bats | 与 BDD-18（总结行不计入逐条计数，check-gate.sh 审计口径）概念重复，且 F12 已覆盖同一总结行场景的 `--fix` 侧；F12 保留代表 | `F_BDD18.1`：check-gate.sh P6 审计口径不把总结行计入逐条 PASS/FAIL 总数（BDD-18 真红） |
| 7 | PV.5 `3 PASS 引用 1 共享证据文件 期望 exit 0` | check-p6-provenance.bats | 与 PV.5b（14 PASS 引用 8 共享证据文件，规模更大的同机制场景）概念重复；PV.5b 保留代表 | `PV_BDD19.1`：P7 frontmatter blocker_count/deviation_count 均 0 时判定通过（不再用非计数行排除正则，BDD-19 真红） |
| 8 | PROV_MULTI.3 `PASS 行含 nth(1) 嵌套括号 + 行末单一证据路径 → exit 0` | check-p6-provenance.bats | 与 PV.18（同一"嵌套括号路径提取"场景，措辞不同但断言等价）概念重复；PV.18 保留代表 | `PV_BDD20.1`：P7 frontmatter design_gap_reviewed_count < design_gap_count 时拦截（不再用数量相减的 0-vs-0 歧义判定，BDD-20 真红） |
| 9 | SC.5b `[SCOPE_RESOLVED: 带说明] 格式也接受` | check-scope-resolved.bats | 与 SC.5（无说明的 `[SCOPE_RESOLVED]` 基本格式）概念重复，同一散文标记接受度的标点变体；SC.5 保留代表（且散文标记接受度本身在 BDD-23 下继续保留，未删除机制，只删测试） | `SC_BDD22.1`：有 SCOPE+ + P1 frontmatter scope_resolved 非空列表 → 闭环判定通过（BDD-22 真红） |
| 10 | RT.SCOPE_PROGRESS `progress file with [SCOPE+] does not trigger retro warning` | check-retrospective.bats | 与 RT.DP1 / RETRO_SCOPE_DC.1 / RETRO_SCOPE_CARD.1（同一"特定文件类型排除扫描"机制的第 4 个变体：progress/dispatch-prompt/dispatch-context/AGATE_CARD 四个排除区中的一个）概念重复，其余 3 个变体保留 | `RT_BDD21.1`：P1 frontmatter need_confirm_resolved 已覆盖具体描述时该 NEED_CONFIRM 项不再阻塞（BDD-21 真红） |

**验证**：移减 10（check-gate.bats -4=97，check-p6-format.bats -2=10，check-p6-provenance.bats
-2=36，check-scope-resolved.bats -1=10，check-retrospective.bats -1=10）+ 新增 10
（check-frontmatter.bats）= 净 0；15 文件 354→344，+ 240（其余不动）+ 10（新文件）= **594**。
`bash agate/tests/scripts/count-tests.sh` 实测输出 594，逐项见 §0 表。

> 说明：P2-design.md §3.1.5 原文写"@test 数逐文件保持不变"是对**未涉及配平机制**的其余 10 个
> 受影响文件（check-pruning.bats/check-p6-evidence.bats/check-tdd-red.bats/
> check-gate-p1-review.bats/agate-extract-context.bats/regression 3 文件/integration 2 文件）
> 的准确描述——这 10 个文件确实逐条保持原有 @test 数（只改写断言内容/测试名，不删不增，见 §3）。
> 涉及配平机制的 5 个文件（check-gate.bats/check-p6-format.bats/check-p6-provenance.bats/
> check-scope-resolved.bats/check-retrospective.bats）因 FIND-7 明确要求"必须在受影响文件中
> 删除或合并等量重复断言"（P2-design.md §3.1.5 + P2-dispatch-context 约束 2），是硬约束 1
> （594 不漂移）与"改写而非删减"表述之间的唯一调和点：删除的必须是**真实概念重复**的断言
> （已逐条给出移减理由 + 保留的同机制代表用例），且删除后同一文件净增等量的新 BDD 覆盖，
> 文件总 @test 数虽然逐个下降 1-4 条，但都换来了此前完全空白的 BDD-9/10/16/17/18/19/20/21/22
> 覆盖，不是无补偿的裸删减。

## 2. 流 A：BDD-1..15（字段读取可靠性 + schema 校验器 + 双读兼容 + 硬约束）

| BDD | 描述 | 测试用例 | 文件 | 当前状态 |
|---|---|---|---|---|
| BDD-1 | 机器字段从 frontmatter 统一读取 | `MDF.1`；`G_BDD1.1`；`R4.2`/`R4.3`（v060-p8-internal-only）；`R3.2`（v060-r4-cached）；`P2.6c`/`P2.7a`（check-pruning） | agate-md-field-get.bats / check-gate.bats / regression/*.bats / check-pruning.bats | MDF.1 绿（characterization）；G_BDD1.1 绿（characterization，正则天然兼容顶格 frontmatter）；R4.2/R4.3/R3.2/P2.6c/P2.7a 绿（fixture 已切换，回归安全） |
| BDD-2 | 全角冒号不再导致字段静默缺失 | `CF.1` | check-frontmatter.bats | **红**（脚本不存在） |
| BDD-3 | phases 内联与块式两种格式统一解析 | `MDF.4` | agate-md-field-get.bats | 绿（characterization，现有 phases op 已支持块式解析） |
| BDD-4 | 缩进错误被校验器拦截 | `CF.2` | check-frontmatter.bats | **红** |
| BDD-5 | 枚举字段非法值被类型校验拦截 | `CF.3` | check-frontmatter.bats | **红** |
| BDD-6 | 缺必填字段时 gate 拦截（P1/P2/P7 三类 schema） | `CF.4`（P1）/ `CF.5`（P2）/ `CF.6`（P7，含 FIND-1 边界） | check-frontmatter.bats | **红** ×3 |
| BDD-7 | 校验错误信息可定位修复（字段名/行号） | `CF.7` | check-frontmatter.bats | **红** |
| BDD-8 | 校验器与 .state.yaml 校验同机制接入 pre-commit | `CF.10` | check-frontmatter.bats | **红**（`check-frontmatter.sh` 不存在，exit 127） |
| BDD-9 | 旧格式文件（正文内嵌、无 frontmatter）仍被正确读取 | `MDF.2`；`G_BDD9.1`；`P2.5`（--legacy-fields） | agate-md-field-get.bats / check-gate.bats / check-pruning.bats | 绿（characterization，回归路径本就未变） |
| BDD-10 | frontmatter 优先于正文正则 | `MDF.3`（引号值，真红）；`G_BDD10.1`（characterization） | agate-md-field-get.bats / check-gate.bats | MDF.3 **红**；G_BDD10.1 绿（见 §4 说明：check-gate.sh 现有"文件首现优先"grep 对该场景巧合正确，真正的 dict 优先级验证落在 MDF.3） |
| BDD-11 | 测试用例数不漂移（594） | `count-tests.sh` 实测（无独立 @test，验证载体是本文件 §1 配平表 + P5 gate `P5_count`） | — | 已达标（594，实测见 §0） |
| BDD-12 | frontmatter 无超过 3 层的嵌套结构 | `CF.8` | check-frontmatter.bats | **红** |
| BDD-13 | 一致性检查 0 ERROR（含 CHECK 9 锚点表 37→38） | `CON.8`（integration，P5/P6 验证，不在 P3 gate 范围） | integration/consistency.bats | 现状绿（P4 改脚本后需重新校准，P5 复核） |
| BDD-14 | v2.0 设计文档声明"结构化不解决语义真实性" | 无独立 @test（P2-design.md §10 已显式声明，验证载体是文档检索而非可执行测试；P1 §9 已同口径声明。属"设计文档存在性"验证，非解析行为，P6 阶段人工核对） | — | 已满足（P2-design.md §10 全文可查） |
| BDD-15 | gate_commands 保持正文读取，四工具无回归 | `TDD.G1`（含 BDD-15 回归标注）+ check-tdd-red.bats 全部 PYX.\* 用例（gate_commands 读取工具族） | check-tdd-red.bats | 绿（gate_commands 不迁移，本就不受影响，回归锚定） |

## 3. 流 B：BDD-16..20（P6/P7 结果结构化）

| BDD | 描述 | 测试用例 | 文件 | 当前状态 |
|---|---|---|---|---|
| BDD-16 | P6 汇总（pass/fail/ui_affected）声明于 frontmatter | `G_BDD16.1` | check-gate.bats | **红** |
| BDD-17 | P6 逐条结果行格式从严（`- PASS｜FAIL BDD-NN:`） | `F_BDD17.1` | check-p6-format.bats | 绿（characterization，现有脚本已能正确接受合规格式；从严校验的"拒绝"侧由 BDD-18 覆盖） |
| BDD-18 | P6 总结行不再导致逐条计数膨胀 | `F_BDD18.1` | check-p6-format.bats | **红** |
| BDD-19 | P7 BLOCKER/DEVIATION 状态入 frontmatter（计数结构化） | `PV_BDD19.1` | check-p6-provenance.bats | **红** |
| BDD-20 | P7 DESIGN_GAP_REVIEWED 配对状态入 frontmatter | `PV_BDD20.1`；`R2.1`/`R2.2`/`R2.3`/`R2.3b`（v060-design-gap，全部改写为 frontmatter 版） | check-p6-provenance.bats / regression/v060-design-gap.bats | PV_BDD20.1 **红**；v060-design-gap 4 条绿（characterization，body/frontmatter 声明一致，回归安全网） |

## 4. 流 C：BDD-21..24（标记状态收尾）

| BDD | 描述 | 测试用例 | 文件 | 当前状态 |
|---|---|---|---|---|
| BDD-21 | P1 标记"已解决/已确认"状态结构化 | `RT_BDD21.1`；`P1: BDD-21 边界...` 重命名用例（check-gate-p1-review.bats，未结构化解决仍阻塞的反面回归） | check-retrospective.bats / check-gate-p1-review.bats | RT_BDD21.1 **红**；check-gate-p1-review 用例绿（反面回归） |
| BDD-22 | SCOPE_RESOLVED 状态结构化后闭环门禁仍工作 | `SC_BDD22.1` | check-scope-resolved.bats | **红** |
| BDD-23 | 发现性标记（SCOPE+/PROD_TOUCHED/DESIGN_GAP）本体保持散文 | 未改动的既有用例族：check-scope-resolved.bats 的 SC.2/SC.3/SC.4/SC.6/SC.7（散文扫描回归）+ integration/pre-commit-hook.bats 的 IT_PT_\* / IT_PT_T6.\* 系列（PROD_TOUCHED 行首锚定回归） | check-scope-resolved.bats / integration/pre-commit-hook.bats | 全部绿（边界确认：v0.35 行为不变，属"不改动即通过"的负向验证） |
| BDD-24 | 角色卡/模板贴可复制 frontmatter 模板 | 无 P3 阶段 @test（模板/角色卡文档改造属 P4 交付物，P3 阶段无对应可执行断言对象；P6 验收阶段人工核对 `task-files.md`/`analyst.md`/`architect.md`/`verifier.md` 是否含可复制样例，样例本身可用 `python3 -c "import yaml; yaml.safe_load(...)"` 验证通过） | — | P4 后补验证（P3 无先于实现的可执行断言对象——模板文本本身不是"通过/失败"的程序行为） |

> BDD-24 说明：P1-requirements.md 反模式自检要求 BDD"可二值判定"，但"模板文档是否存在可复制样例"
> 在 P3（实现尚未写、模板尚未改）阶段没有可断言的程序对象——这不是遗漏，而是该 BDD 本质上验证的是
> **文档产出物**而非**程序行为**，与 BDD-14（语义真实性边界声明）同类。P6 验收时对 P4 产出的模板文件
> 做人工 + `yaml.safe_load` 双重核对，验证方式已在本文件注明，不违反"P3 覆盖全部 28 条 BDD"要求
> （覆盖 = 已识别验证方法并声明验证载体，而非强行伪造一个程序断言）。

## 5. 流 D：BDD-25..28（任务编号规则改造 + 自举边界）

| BDD | 描述 | 测试用例 | 文件 | 当前状态 |
|---|---|---|---|---|
| BDD-25 | 新编号格式 TAG0001 被 v2.0 校验器接受 | `SY.1`（前半段：TAG0001 → 无输出） | agate-state-yaml-check.bats | **红**（现行 `^T\d+$` 拒绝 TAG0001） |
| BDD-26 | 旧编号格式 T001 被 v2.0 校验器拒绝（硬切） | `SY.1`（后半段：T001 → 报错） | agate-state-yaml-check.bats | 现行反而"通过"（T001 匹配旧正则，无输出）——校验器实现后应改为报错，故本半段当前是"假绿"，@test 整体因前半段已判红 |
| BDD-27 | check-changelog 直接匹配完整 task_id | `CL.6`/`CL.7`/`CL.8`（全部重写为 TAG0001 场景） | check-changelog.bats | **红** ×3（现行短前缀提取对 TAG0001 抽取为空） |
| BDD-28 | 本 task 自身 T001 全程按 v0.35 gate 通过 | 无 P3 阶段 @test（这是**运行时不变式**，验证载体是主 Agent 每阶段实跑 `~/.agate/scripts/check-gate.sh`，不是 worktree 内的 bats 用例——T001 用旧协议工具跑 gate，与 worktree 新协议测试套件是两个独立的验证轨道，混在一起断言会违反"双工作区隔离"边界） | — | 持续满足中（本 task 至今每阶段 gate 均通过，P8 发布前再次全面核对） |

> BDD-28 说明：P0-brief.md 已声明"验证载体：P8 发布流程...无对应 BDD"式的同类先例（P1 §3 隐含需求 #15）。
> BDD-28 虽然编号在 P1 基线内，但其验证方式是"主 Agent 运行时纪律"而非"worktree 内某个 .bats 断言"——
> 强行在 worktree 测试套件里写一个断言"T001 用 v0.35 格式"不仅无法验证任何程序行为（T001 本来就是本
> worktree 外部的既成事实），且会与 BDD-26（v2.0 校验器拒绝 T001）产生表述混淆。P6 验收阶段对 BDD-28
> 的判定方式是核对 T001 的 P0-P8 阶段产出文件+`.state.yaml`是否全程 `~/.agate` gate 通过（已通过 git log
> 可查）。

## 6. 按流分组的执行独立性说明（约束 8）

- **流 A 红灯**（CF.1-10、MDF.3/5/6）只依赖 `agate-frontmatter-check.py` / `check-frontmatter.sh` /
  `agate-md-field-get.py` 三个文件是否实现，与流 B/C/D 的任何脚本无关。
- **流 B 红灯**（G_BDD16.1、F_BDD18.1、PV_BDD19.1、PV_BDD20.1）只依赖 `check-gate.sh` 的 P6/P7 分支
  是否改为读 frontmatter，不依赖流 A 校验器是否已挂 pre-commit（P4 仍需先做流 A 双读工具，但流 B 的
  gate 分支可以直接读 frontmatter dict，不必等校验器本身实现——校验器只管"坏格式要不要拦"，不管"好
  格式怎么读"）。
- **流 C 红灯**（RT_BDD21.1、SC_BDD22.1）只依赖 `check-gate.sh` P1 分支 / `check-scope-resolved.sh`
  是否改读 frontmatter 结构化列表。
- **流 D 红灯**（SY.1、CL.6/7/8）只依赖 `agate-state-yaml-check.py:39` 正则 + `check-changelog.sh:14`
  短前缀提取两处局部改动，与流 A/B/C 完全独立（P0-brief 已声明"本 task 自身用 v0.35 规避"）。

P4 实现按 A→B→C→D 串行推进时，每完成一流即可让该流对应的红灯转绿，不会因后续流未实现而被阻塞。

## 7. UI 任务判断（约束 7）

P2-design.md §4 声明 `ui_affected: false`，本任务非 UI 任务，不产出 Playwright/E2E 用例。

## 8. 语义真实性边界测试自检（约束 10）

本清单内所有测试断言的对象均为"字段被可靠读取 / 坏格式被拦截 / 编号规则被正确校验"三类解析层行为
（CF.\* 系列断言校验器报错/不报错、MDF.\* 断言 op 输出值、G_BDD\*/F_BDD\*/PV_BDD\*/RT_BDD\*/SC_BDD\*
系列断言 gate exit code、SY.1/CL.\* 断言正则匹配结果），无一条测试尝试判断 BDD 描述文字或裁剪理由的
"内容是否属实"，符合 P2-design.md §10 语义真实性边界声明。

## 9. frontmatter 嵌套约束自检（约束 9）

`check-frontmatter.bats` 的 fixture 内，唯一刻意构造超过 3 层嵌套的样例是 CF.8（4 层，用于验证
"深度校验器能拦截"），属"非法反例"而非"合法期望值"；其余全部 fixture（CF.1-7/9/10、MDF.\*、
所有改写用例）的 frontmatter 字段均为单层 `key: value` 或一层列表，符合硬约束 2。

## 10. 参考

- P1-requirements.md（28 条 BDD 全文）
- P2-design.md §3（四流设计细化）、§9（BDD 覆盖映射表）、§13（FIND-1/3/5/7 修订详情）
- P2-review.md（8 条 FIND，FIND-1/4/5/7 与本设计直接相关）
- `agate/tests/README.md`（bats helper 约定）
- `agate/scripts/agate-state-yaml-check.py` / `agate/tests/unit/agate-state-yaml-check.bats`（校验器范式参照）
