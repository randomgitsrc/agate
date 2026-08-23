---
phase: P2
task_id: TAG0022-confirmed-problems
type: review
parent: P2-design.md
trace_id: TAG0022-P2-20260822
status: approved
created: 2026-08-22
agent: plan-eng-review
---

# P2 方案独立评审 — TAG0022 三连任务确认问题修复批（RM-AG0037~RM-AG0041）

> 评审对象：`P2-design.md`（376 行，candidate_count=2，dispatch_plan 4 批）
> 评审角色：plan-eng-review（工程维度：数据流/状态机/错误边界/测试策略/多方案/实现就绪度/最小验证/分批纪律/SCOPE+ 判定）
> 状态标记：`[PROD_NOT_TOUCHED]`（评审只读 worktree 协议文件与代码，写操作仅落 P2-review.md 与 P2-progress.md）
> 客观复核：ptmp 写可 / GIT_CEILING_DIRECTORIES rc=128 / count-tests=1202 / read_rules_yaml 10 阶段 / agate-md-field-get domains=backend——全部实测通过（见 §8）

## 结论

**status: approved（0 阻塞）。**

P2-design.md 五子项方案与 BDD-1..10 验收锚逐条对应、未改 BDD 语义；0038 迁移逐点映射清单（§4.2.1 A/B/C/D 组→行号级）经与 worktree 实现代码实读核对，行号与正则面全部对得上；0039 fail-closed 校验强度按 P1-review N1 冻结；0041 的 GIT_CEILING_DIRECTORIES 与 [SCOPE+] M15 排除钩子均为最小且必要（TAG0020 known-failures 条目 2 实证）；dispatch_plan 4 批 D3 错开成立（C→B 串行、批文件集互不交叉）；N1/N2/N3 全部闭环。6 项非阻塞观察（NB-1..6）与 3 项测试缺口建议，不构成 rejected 条件。

## 架构问题（阻塞级）

无。

逐项核对了派发重点中列出的全部疑点（见 §4），无一项达到阻塞：

1. 五子项 ↔ BDD-1..10 全覆盖，P2 未改 BDD 语义——§3 完成标准逐条给出可判定口径（BDD-1/2↔0037、BDD-3/4/5↔0038、BDD-6/7↔0039、BDD-8↔0040、BDD-9/10↔0041），Given/When/Then 未被动过。
2. 0038「行为逐字节等价」——对 well-formed 输入成立（§4.1 NB-3 边界说明）；1202 用例全绿为实际回归兜底。
3. S-3 收紧不误伤既有卡片——R4 缓解（P4 C 批对 10 张卡跑基线 + 「机器可判定命令行」模式匹配）成立；既有 S-3 outputs/orphan/exec_role 检查须保留（§4.1 NB-1）。
4. 0039 判据——ISO 字典序 + 缺失 fail-open 边界成立；falsy 无条件 exit 1 有一处 pre-cutoff 边界偏离（§4.2 NB-4）。
5. 0041 两项修复均为最小必要（§4.3）。
6. N1/N2/N3 闭环（§4.5）。

## 架构问题（非阻塞）

- **NB-1（S-3 语义清晰度，check-structure-consistency.py）**：P2-design §4.2.2 将「S-3」表述为「双向 gate 命令一致性（S-3a/S-3b）」，但现有 S-3 实际是「YAML→cards outputs/orphan/exec_role 一致性」（check-structure-consistency.py L187-239，含 P2 试点锚点强制与孤儿卡片防护）。**必须显式声明：既有 S-3 检查全部保留（test_check_structure_consistency.py L105 的「产出规格缺失 P2-review.md → 非 0」用例必须保持绿），S-3a/S-3b 是叠加在 S-3 下的新增子检查，不是重定义**。P4 C 批 implementer 若理解成「重定义 S-3」会回归 TAG0021 的 outputs 一致性保护。
- **NB-2（S-3a/S-3b 的 P6.5 归属）**：P6.5 无独立卡片（check-structure-consistency.py `_phase_card_path` 对 P6.5 返回 None，既有 S-3 对无卡片阶段跳过）。M6 给 P6.5 gates[].check 补命令串后，S-3a 要求「命令串须在卡片 ## gate 规则（或推进条件）出现」——需明确 P6.5 命令串落在 P6 卡的 P6.5 复查节，或按「无卡片阶段跳过」保持。实现时须定案，避免 S-3a 对 P6.5 误报或漏检。
- **NB-3（「行为逐字节等价」声明边界）**：A 组 `_frontmatter_field`（L164-170，sed 式行扫描）→ `agate-md-field-get` op（YAML frontmatter 解析 + NO_FALLBACK 集合）在 **畸形/带引号/带注释 frontmatter 边界**有行为差异（YAML 解析失败 → 返回 ""；`status: "approved"` 带引号 → 新路径正确去引号）。方向上偏 fail-closed（畸形 → 更早 exit 1）或修正（带引号 → 更正确），不产生假 PASS 漏洞。建议把等价声明限定为「well-formed frontmatter + 既有 1202 用例全绿」口径，不承诺畸形输入的逐字节等价。
- **NB-4（0039 规则 2 的 pre-cutoff 边界）**：§4.3.2 规则 2「judge 为 dict 且 enabled falsy → exit 1」**无条件执行**（不查 created）。与 state-machine.md L443「缺失/false = 历史任务」注释及 gate_p65（check-gate.py L982-986：非 dict+enabled → 早退 0，含 falsy）的历史兼容语义不一致：一个 pre-cutoff 任务若显式写了 `judge.enabled: false` 会被 P1 拦（而 P6.5 会跳过）。实践上机制前任务（TAG0019/20）均无 judge 块、显式 false 仅存在于测试 fixture（test_check_gate.py L2662-2672），故为防御性边界。建议：falsy 与缺失同走 created 判据（falsy + created ≥ cutoff → exit 1；falsy + pre-cutoff → 跳过），或显式记录此偏离与 BDD-7 的关系。
- **NB-5（test_bdd_7 改造的 helper 缺口）**：`_run_routing`（test_check_routing.py L20-26）目前只接受 `cwd`，无 `env` 参数；设计 §4.5.1 的「run_cli 注入 env=GIT_CEILING_DIRECTORIES」需在 D 批改 `_run_routing` 加 env 透传或 test_bdd_7 直接调 run_cli(env=...)。conftest `_run_cli_impl`（L55-71）已支持 env ✓，属实现细节，非设计缺陷。
- **NB-6（A 组映射清单行号微差）**：§4.2.1 写「_frontmatter_field 10 处使用」，实核为 **9 处调用**（L500/506/716/722/768/**799/805**/1108/1109；L799/805 是 gate_p4 的 P4-review status/agent 读点，映射表未显式列出）。P4 C 批按映射表迁移时勿漏 L799/805 两个 P4-review 读点（「等」字覆盖了，但清单应补全以免 implementer 只按表内行号迁移）。

## 测试缺口

- **TG-1（S-3a/S-3b 双向漂移测试未入 P3 清单）**：BDD-5 的单侧漂移验收（卡片加 gate 行不入 YAML → S-3b ERROR；改 YAML gate 不动卡片 → S-3a ERROR）在 P3 测试清单（§11）只写了「0038 静态扫描测试 test_md_parse_scan.py」，**未给 check-structure-consistency.py 的 S-3a/S-3b 漂移用例排测试**（M-table 无对应测试文件增补）。建议 C 批在 test_check_structure_consistency.py 补 S-3a/S-3b 漂移 + 双侧一致 exit 0 用例，使 BDD-5 的漂移判据可重复验证（而非只在 P5/P6 手动构造）。
- **TG-2（0039 判据边界用例缺失）**：§4.3.2 只给 2 个二元 fixture（created 2026-08-22 无 judge → exit 1；created 2026-08-19 无 judge → exit 0）。建议 M11 补：judge.enabled 显式 false（机制后 → exit 1）、created 非 ISO / 缺失（fail-open → 不拦）、judge 非 dict（如 judge: true bool → 按缺失处理）。§3 RM-AG0039 item ③ 的「exit 0/2 不被拦」与「gate_p65 三态用例保持绿」是谓词级陈述，测试化更稳。
- **TG-3（M15 排除钩子单元测试落点未指明）**：R6 缓解「新增该钩子的单元测试」未指明文件/断言形态。建议在 D 批指定（test_env_adapt_docs.py 或 test_check_protocol_consistency.py）：注入 AGATE_CONSISTENCY_SKIP_DIRS 后 iter_md_files 不产出被排除路径 + 默认未设置时逐字节不变（扫面变化可观测）。

## 锁定决策（本次评审确认的技术方向）

1. **0039 校验强度 = fail-closed exit 1**（§4.3.1，P1-review N1 闭环）：对齐 gate_p65 缺 verdict exit 1 与缺失必填字段惯例；judge.enabled 对机制后新任务升级为必填字段。
2. **0039 判据 = judge 块 presence + P1 created（agate-md-field-get created op）≥ judge_required_since（rules/dispatch.yaml "2026-08-22"，ISO 字典序）+ created 缺失/非 ISO fail-open**（§4.3.2，R5 缓解）。
3. **0038 迁移架构 = 共享读取器单点（候选 1）**：B/C/D 组迁入 agate_common（count_markers/extract_bdd_titles/parse_ui_design_section/count_p6_pass_fail/count_p7_markers/count_design_gap/count_code_map_lines/parse_fail_list_block/count_kf_entries/has_keyword/extract_embedded_yaml_blocks，与 parse_gate_commands_block L784-795 同款）；A 组 `_frontmatter_field` 整体删除，改走 agate-md-field-get 新 op（status/agent/project_phase → NO_FALLBACK_STRING_FIELDS；code_map_new_files_count/code_map_reviewed_count → NO_FALLBACK_INT_FIELDS 解 DESIGN_GAP 遗留 L1098-1107；created → NO_FALLBACK_STRING_FIELDS）。
4. **S-1~S-6 收紧 = S-3 增加双向 gate 命令一致性（S-3a YAML→md / S-3b md→YAML），既有 S-3 outputs/orphan/exec_role 检查保留**（§4.2.2；TG-1/NB-1 落实）。
5. **0041 = GIT_CEILING_DIRECTORIES（test_bdd_7 确定化非 git 上下文）+ [SCOPE+] M15 opt-in 排除钩子（AGATE_CONSISTENCY_SKIP_DIRS，默认关闭、行为不变）**（§4.5；最小且必要，见 §4.3）。
6. **分批纪律 D3 = Wave1 {A-ruff, C-migration, D-env-tests} 并行（文件集互不交叉）→ Wave2 {B-judge} 于 C 后串行**（§5；B 依赖 C 的 created op 注册 + 重构后 gate_p1，依赖方向正确）。
7. **basetemp = /home/kity/oclab/dsh-workspace/ptmp（N2 实证）**；**count-tests 基线 = 1202（N3 冻结，只增不减）**。
8. **技术债登记判断**：P2-design 未提出「后续应重构/架构债」；我评审亦不新增债项——「53 脚本 grep 残留」延伸面（N6）已显式声明为 roadmap 后续批次承接，非本任务 BDD 内，**无需登记 tech-debt.md**。

## 逐项评审结论（引用锚点）

### R1 数据流/状态机/接口契约
- 0038 迁移数据流：check-gate.py A/B/C/D 组（L101-110、L164-170、L336-338、L390、L417-462、L500-506、L523-584、L693-736、L875-954、L1015-1088、L1127-1135）→ agate_common 共享读取器 / agate-md-field-get op，消费路径单一化；E/F 组（L230-241、L982-983、L1162-1230）保持不动（D2 判定口径）。各步无新增外部依赖，异常路径（文件缺失 → "" 回退、unknown op → exit 2 → "" 回退）沿 `_md_field_get` 既有契约。
- 0039 状态机：gate_p1 新增 judge 校验块叠加于 C 重构后基础（§5「gate_p1 末尾纯叠加」）；gate_p65（L972-996）/pre-commit 2i.1/ci-backstop 消费语义逐字节不变（N1 §1.2）。三态转换（judge dict+true 放行 / dict+false exit 1 / 缺失走 created）完整覆盖。
- 0041：test_bdd_7 的 git 上下文判定（run_git rev-parse cwd=task_dir，agate-risk-score.py L217）+ GIT_CEILING_DIRECTORIES 上限截止 → 两位置确定性 git_ok:false；test_bdd_25 的一致性扫描（iter_md_files L119-138 rel_parts 排除链）+ M15 排除 env → 两位置 0 ERROR。

### R2 错误边界
- **0038 逐字节等价漏洞排查**：A 组 frontmatter 迁移在畸形/引号 frontmatter 边界有差异（NB-3，fail-closed/修正方向，非假 PASS）；B/C/D 组「逐字节同正则」机械成立；「回归兜底 = 既有 1202 用例全绿」是实操验证面。无功能性漏洞。
- **S-3 收紧误伤排查**：S-3b 的「机器可判定命令行」模式匹配（check-gate.py P\d+ / gate_commands.P\d+ / check-[\w-]+\.py）对卡片 `## gate 规则` 散文行不匹配（如 P2 卡「- 候选方案数 ≥2」）；M6 数据增补 + R4 基线核对兜底误报。既有 S-3 检查须保留（NB-1）。
- 0041 错误边界：M15 默认关闭（无 env → 逐字节不变，R6）；GIT_CEILING 无 Unix 假设（跨平台 git 核心机制，§8 实测）。

### R3 测试策略
- BDD 覆盖：0038 → test_md_parse_scan.py（A/B/C/D 模式清单命中=0，BDD-3）；0039 → test_check_gate.py 新增 P1 judge 用例（BDD-6/7）+ 既有 gate_p65 三态用例（L2662-2694）保持绿；0041 → test_bdd_7/25 改造 + M15 钩子用例（BDD-9/10）。验收锚覆盖齐备。
- 缺口：TG-1（S-3a/S-3b 漂移用例未排）、TG-2（0039 判据边界用例）、TG-3（M15 钩子测试落点未指明）。

### R4 多方案探索
- candidate_count=2 **真候选**：候选 2（独立工具 agate-task-md-parse.py + subprocess）在「进程隔离」「多脚本复用面」「CLI 工具族风格」三维度上确实优于候选 1——非稻草人；其被否的原因是「本任务验收锚仅 check-gate.py 清零（D2）+ YAGNI（未来 53 脚本迁移非本任务 BDD，N6）」与「30+ 子进程延迟/双轨漂移风险」，选择理由自洽。

### R5 实现就绪度
- files_to_read（§7，17 项）覆盖 check-gate.py 迁移主对象、agate_common 样板（L769-805）、agate-md-field-get KNOWN_OPS、check-structure-consistency S-*、rules yaml/schema、state-machine L440-448、P1 卡、四个测试文件 + conftest + check-protocol-consistency + agate-risk-score + workflow + UPGRADING + count-tests——实现所需上下文全覆盖，无多余项。
- §4.2.1 逐点映射清单到行号级，implementer 可无需步骤计划自主实现；NB-5/NB-6 为两个实现细节补充。

### R6 最小验证
- minimal_validation 五条齐全：ptmp 写可 **confirmed**（§8 assumption 1，实测复算通过）；read_rules_yaml + agate-md-field-get domains **confirmed**（§8 assumption 2，实测：phases 10 阶段解析 OK、known_phase_ids P0-P8+P6.5、is_legal_gate_key('P5_e2e_timeout_seconds')=True、domains=backend）；GIT_CEILING_DIRECTORIES **confirmed**（§8 assumption 3，实测 no-ceiling rc=0 / with-ceiling rc=128）；两条纯代码逻辑（M15 排除钩子、0039 judge 校验）**not_needed 声明含内部依赖函数与数据转换理由**，符合 P2 卡「纯代码逻辑声明须附理由」要求。

### R7 分批纪律（D3）
- 4 批文件集核对：A={workflow+UPGRADING+AGENTS.md}；C={check-gate.py(解析层)+agate_common+agate-md-field-get+check-structure-consistency+phases.yaml+test_md_parse_scan.py}；B={check-gate.py(gate_p1 judge 块)+dispatch.yaml+schema+state-machine+P1 卡+test_check_gate.py}；D={test_check_routing+test_env_adapt_docs+check-protocol-consistency.py}。
- 交叉项仅 check-gate.py（B/C 同文件）——但 C→B **串行**（Wave2 在 C 返回后），且 C=解析层重构块、B=gate_p1 末尾 judge 叠加块为非重叠改动块；其余文件**零交叉**。D3 成立。
- B 依赖 C（created op 注册 + 重构后 gate_p1 挂点）方向合理：B 先于 C 会引用不存在的 op（_md_field_get unknown op exit 2 → 恒回退 ""，DESIGN_GAP L1098-1107 已证明此坑）并叠加在旧解析层上。
- dispatch_plan JSON 合法：mode=static-batch、parallel_limit=4、batches 4 ≤ 4、每批 id+complexity ∈ {low,medium,high}，frontmatter 与 §5 表格一致。

### R8 [SCOPE+] 判定（M15）
- **最小性**：单一 env opt-in（AGATE_CONSISTENCY_SKIP_DIRS，相对根路径列表）+ iter_md_files 既有 rel_parts 排除链加一条分支（L119-138）；默认未设置 → 逐字节不变（R6）。
- **必要性**：TAG0020 known-failures.md 条目 2 实证——全量会话中预存测试在 `agate-workspace/.pytest-tmp/test_*/` 生成坏引用 fixture .md，iter_md_files 未排除 → CHECK 2 误收 12 ERROR；BDD-9 要求「仓库内默认 basetemp」位置全量 0 失败；备选 clean-copy 破坏 CHECK 7（check-protocol-consistency.py L1117-1120 main() 强制 root 含 agate/WORKFLOW.md + L428-434 git describe cwd=root 依赖 .git）被否决、外部 basetemp-only 使「任意 basetemp 0 失败」锚打折——M15 为最小可行根治。**采纳成立。**

### R9 技术债
- 无架构债提议；不新增 DEBT 条目（理由见锁定决策 8）。

## 门槛自检

- P2-review.md 存在且非空 ✓；Header status=approved、agent=plan-eng-review ✓
- 结论引用具体锚点（方案节/文件/函数/BDD 编号）✓
- 复核清单：N1（fail-closed exit 1）✓ / N2（ptmp 写可实证）✓ / N3（count-tests 1202 实测）✓ 全部闭环
