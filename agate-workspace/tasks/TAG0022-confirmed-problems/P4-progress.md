# P4-progress（batch D-env-tests，implementer）

## 输入读取完成（2026-08-22）
- dispatch-context M15 规格、P2-design §4.5/§1.1 M13-M15/§1.4 SCOPE+/§7/§8、P2-review NB-5/TG-3、P3-test-cases §3/§5 契约注解 3/4/5 已读。
- 现状代码确认：P3 commit f256d2c 已含 test_env_adapt_docs.py（test_bdd_25 位置感知 + test_m15_* 单测）与 test_check_routing.py（_run_routing env 透传 + test_bdd_7 GIT_CEILING_DIRECTORIES）；worktree agate/ 无未提交改动。
- iter_md_files 现状（check-protocol-consistency.py L119-138）：rel_parts 排除链（.git/archived/.archived/.worktrees/.opencode/.claude/node_modules/bats）；env 解析惯例 = os.environ.get("AGATE_*", 默认)。
- conftest _run_cli_impl（L55-73）env 参数支持确认（subprocess env=full_env.update(env)）。

---

# P4-progress（batch A-ruff，implementer）— 追加段（与 batch D 并存）

## 2026-08-22 — batch A-ruff 实施中
- 输入已读：dispatch-context batchA + P4 卡、implementer.md、P0-brief、P1（BDD-1/2、D1）、P2-design（§1.1 M1/M10、§4.1、§5 批表、§7）、protocol-tests.yml 全文、UPGRADING.md（v0.60.0 为格式样板）、根 AGENTS.md 版本发布区。
- 事实确认：ruff job 在 protocol-tests.yml L106-116（job name 已稳定 `ruff`）；L116 为唯一需改行；UPGRADING 最近章节 v0.60.0（L92），新章节插其前；根 AGENTS.md 版本发布 step 5 后为补句落点；CODE-MAP.md 存在 → 新增文件核对表必填，P2-skeleton.md 不存在。
- ✅ 已改 `.github/workflows/protocol-tests.yml`：`pip install ruff` → `pip install ruff==0.16.4`（+ 注释说明对齐本地 ~/.venvs/agate-dev，无行为变化）；job name `ruff` 固化未动。
- ✅ 已改 `agate/UPGRADING.md`：`### v0.60.0` 前新增 `### v0.61.0 — 质量门禁收尾（TAG0022...）` 章节——① RM-AG0037 required check 配置步骤（Settings→Branches→分支保护→勾选 ruff，维护者执行，D1 边界）；② RM-AG0038 权威源切换占位小节（C 批补充）；③ RM-AG0039 judge 强制化占位小节（B 批补充）；末尾通用升级动作。格式对齐 v0.60.0 节（①/②/③ 加粗编号 + 步骤 + 占位引用）。
- ✅ 已改根 `AGENTS.md`：「版本发布」清单 step 5 后补一句——`CI ruff job（RM-AG0037 required check）验证：合并前确认分支保护已将 ruff 勾选为 PR required check，或在第 5 步后验证 CI ruff job 绿（ruff==0.16.4 锁版本，与本地 ~/.venvs/agate-dev/bin/ruff 对齐）`。三个文件改动全部落盘，进入自检。

## M15 实现完成（2026-08-22）
- check-protocol-consistency.py iter_md_files 新增 opt-in 排除钩子：
  - `_env_skip_dir_prefixes()`：解析 AGATE_CONSISTENCY_SKIP_DIRS（os.pathsep 分隔、正斜杠归一、call-time 读 env、默认 ()）。
  - iter_md_files 排除链末尾追加分量前缀命中分支（与既有 rel_parts 排除链同层）；main()/CHECK 2/root 强制未动。
- 仓库外 ptmp 首次自跑：test_env_adapt_docs.py + test_check_routing.py 27 passed（红转绿：test_m15_injected + test_bdd_25 仓库外分支 + test_bdd_7）。
- ✅ 自检通过：workflow YAML 语法有效（yaml.safe_load OK，job name=ruff，run 含 ruff==0.16.4）；UPGRADING v0.61.0 节 grep 命中（required check/分支保护/勾选 ruff/占位小节）；AGENTS.md 新句 L157 命中；git diff 可见（3 文件 M，+37/-1）。
- ✅ 已写 `P4-implementation.md`（batch A-ruff）：Header + implementation_dir + 新增文件核对表（CODE-MAP EXEMPT，本批无新增文件）+ 改动摘要（3 文件）+ 自查结果 + 触发面清单（UPGRADING/AGENTS/CI 配置）+ 门槛对照。
- ⚠️ 提示主 Agent：P4-implementation.md 为批次共享产出，当前含 batch A 内容；batch C/D/B 返回后需追加/合并各自小节（同 P4-progress.md 并存模式）。
- batch A-ruff 完成。[PROD_NOT_TOUCHED]

## 两位置验证 + 复核 + 收尾（2026-08-22）
- **CLI 机制模拟**（污染实证）：
  - worktree 根下建 agate-tmp-bt-sim/polluted/bad-ref.md（docs/does-not-exist.md 坏引用，TAG0020 条目 2 同型）→ 无 env 跑 worktree 自己 check-protocol-consistency.py --root worktree根 → rc=1（CHECK 2 ERROR）；env AGATE_CONSISTENCY_SKIP_DIRS=agate-tmp-bt-sim → rc=0（0 ERROR）。M15 排除机制在 CLI 级成立。
- **位置 1（仓库外 ptmp）**：test_env_adapt_docs + test_check_routing + test_check_protocol_consistency + regression/test_v040_dotarchived_exclusion → 56 passed（红转绿：test_m15_injected + test_bdd_25 仓库外分支 + test_bdd_7；既有一致性用例零回归）。
- **位置 2（worktree 内 basetemp）**：--basetemp=<worktree>/agate-tmp-bt-sim/bt_run（仓库根下）+ pytest 插件 ptpollute.py（dsh-workspace 临时资源）在测试执行阶段注入 bsemp/polluted/bad-ref.md → 27 passed；test_bdd_25 走注入分支（basetemp∈仓库根 → env 注入）0 ERROR；测后 rm -rf 临时目录（已确认不存在）。
- **复核 test_bdd_7**：P3 已改（_run_routing env 透传 + GIT_CEILING_DIRECTORIES）；本批未动 test_check_routing.py；两位置自跑该用例均绿 → 无需改动。
- **平台无关扫描**：check-platform-assumptions.py 对修改后 check-protocol-consistency.py → rc=0 无 R1-R5 命中。
- **ruff**：修改后脚本 ~/.venvs/agate-dev/bin/ruff check → All checks passed（曾 PLW2901 循环变量覆写，已改名修复）。
- **临时资源**：/home/kity/oclab/dsh-workspace/ptpollute.py（pytest 污染注入插件，验证用，非交付物）。

---

# P4-progress（batch C-migration，implementer）

## 2026-08-22 步骤 1：输入读取 + 基线

- 读 dispatch-context batchC（AGATE_CARD=P4 全文）、implementer.md、P2-design（§1.1 M2-M6 / §4.2 / §4.2.1 逐点映射 / §4.2.2 S-3 / §5 批表 / §7）、P2-review（NB-1/2/3/6 + TG-1）、P3-test-cases（§5 契约注解）、P0-brief、AGENTS.md。
- 实读现状：check-gate.py 全文件 1258 行；agate_common.py（M2 样板 L769-805）；agate-md-field-get.py（KNOWN_OPS 集合）；check-structure-consistency.py（S-1~S-6，_TASK_FRONTMATTER_FIELDS）；phases.yaml；test_md_parse_scan.py（24 条模式）；test_check_structure_consistency.py（S-3a/S-3b 三用例）；9 张 phase 卡的 `## gate 规则` 节（P0 无 gate 节用推进条件）。
- 状态标记：[PROD_NOT_TOUCHED] 前置。
- 基线三文件自跑：**5 failed + 181 passed**——红 = test_md_parse_scan(1) + S-3a/S-3b(2)（C 批转绿目标）+ judge 缺失/falsy(2)（B 批范围，保持红）。
- 卡片 gate 节 token 枚举（S-3b md 侧锚）：P1={check-gate.py P1}；P2={check-gate.py P2, gate_commands.P3, check-tdd-red.py}；P3={check-gate.py P3, check-tdd-red.py, gate_commands.P3}；P4={check-gate.py P4}；P5={check-gate.py P5}；P6={check-p6-format.py, check-gate.py P6, check-p6-evidence.py, check-p6-provenance.py, check-gate.py P6.5}；P7={check-gate.py P7}；P8={check-gate.py P8, check-p6-provenance.py, gate_commands.P5, check-protocol-consistency.py}；P0 无 token；P6.5 无卡片跳过（NB-2）。

## 2026-08-22 步骤 2：A/B/C/D 组迁移完成 + S-3 收紧落盘

### A 组（frontmatter 读取 → agate-md-field-get 新 op）
- agate-md-field-get.py：NO_FALLBACK_STRING_FIELDS += status/agent/project_phase/created；NO_FALLBACK_INT_FIELDS += code_map_new_files_count/code_map_reviewed_count（解 check-gate L1098-1107 DESIGN_GAP 遗留）。docstring 同步登记。
- check-gate.py：删除 `_frontmatter_field` 定义；9 处调用全迁 `_md_field_get`（P1-review status/agent、P2-review status/agent、P1 project_phase、P4-review status/agent（NB-6 L799/805）、P7 code_map_*）；L1098-1107 DESIGN_GAP 注释移除（已解决）。`_frontmatter_lines` 保留（gate_p1 resolved-presence 行首键扫描，不在 A 组迁移面）。
- 验证：op 直测（frontmatter 取数/无 frontmatter 回退 ""）✓；test_md_parse_scan A 组命中 0。

### B 组（行首标记 → agate_common count_markers/has_marker/extract_marker_desc）
- agate_common.py：新增 M2-0038 节——`_NC_RE/_SUGGEST_RE/_NO_NEED_RE/_NC_DESC_RE/_SUGGEST_DESC_RE/_SUGGEST_TAIL_BT_RE/_SUGGEST_TAIL_BRACKET_RE` + count_markers(text, kind) + has_marker(line, kind) + extract_marker_desc(line, kind)（NC 单段剥离 / SUGGEST 三连剥离，逐字节同正则）。
- check-gate.py：模块级 7 正则删除；gate_p1 计数/描述提取改走共享函数（nc_blocking/nc_suggest/nc_unresolved/nc_suggest_unacked/NO_NEED 存在性）。

### C 组（任务产出格式判定 → agate_common 共享读取器）
- agate_common.py 新增：extract_bdd_titles / parse_ui_design_section / candidate_count_value / design_trivial_declared / has_keyword（tradeoff/choice_and_reason/design_gap）/ count_p6_pass_fail / count_p7_markers / count_design_gap（allow_blockquote 两口径）/ count_code_map_lines / parse_fail_list_block / count_kf_entries。
- check-gate.py：P1 bdd_titles、P2 UI 节（标题+形态/维度声明）、candidate_count、design_trivial、权衡 nudge、P6 旧格式计数、P7 BLOCKER/DEVIATION/DESIGN_GAP（两口径）/P4 关键词/CODE_MAP 计数、P5 fail-list/kf 计数——全部改走共享读取器。

### D 组（内嵌 yaml 块 → agate_common extract_embedded_yaml_blocks）
- agate_common.py：`extract_embedded_yaml_blocks(text)`（同正则单点，read_vision_tri_state 已有共享实现同源）。
- check-gate.py：`_gate_p1_vision_capability` 兜底循环改走共享函数。

### S-3 收紧（check-structure-consistency.py + phases.yaml）
- check-structure-consistency.py：`_TASK_FRONTMATTER_FIELDS` 补 code_map_new_files_count/code_map_reviewed_count（S-4 防误报）；新增 `_MACHINE_GATE_REF_RE` + `_machine_gate_refs` + `_yaml_gate_cmd_refs` + `_gate_rules_block`（gate 规则 节，fallback 推进条件）+ `_block_since`；`_check_s3` 逐阶段叠加 S-3a（YAML→md：gates 命令串须在卡片 gate 节出现）+ S-3b（md→YAML：卡片 gate 节命令行须在 gates[].check 声明）；NB-1 叠加不重定义、NB-2 无卡片阶段跳过（P6.5 天然跳过）。
- phases.yaml：各阶段 gates[].check 增补实际 gate 命令串（与 9 张卡 `## gate 规则` 节逐一核对）——P1/P2/P4/P5/P7=check-gate.py Pn $TASK_DIR；P3 += check-tdd-red.py/gate_commands.P3；P6 += check-p6-format.py/check-p6-evidence.py/check-p6-provenance.py/check-gate.py P6.5；P6.5 += check-gate.py P6.5；P8 += check-p6-provenance.py/gate_commands.P5/check-protocol-consistency.py；P0 卡无命令串（用推进条件，无 token）保持。
- **P5 数据点修正**：原 P5 散文 check "gate_commands.P5 exit 0 AND failed==0" 含 token gate_commands.P5，但 P5 卡 gate 规则 节只有 check-gate.py P5 —— S-3a 真实树跑报错。改散文为 "P2 声明的验证命令全部 exit 0 AND failed==0"（去 token），对齐卡片（card 不可改——不在 C 批文件集，R4 的"补卡片"路径本批不可达）。
- **验证**：
  - test_md_parse_scan.py：**红→绿**（命中 43→0，24 条模式全清零，无需校准——清单与实际迁移点逐条对上）。
  - test_check_structure_consistency.py：**2 红转绿**（S-3a/S-3b）+ 11 既有全绿（13 passed）。
  - test_check_gate.py：170 绿零回归；仅 B 批 2 个 judge 用例保持红。
  - 真实树 check-structure-consistency.py：AGATE_ROOT=worktree **S1-S6+S0 全 OK，exit 0**。
  - check-protocol-consistency.py --strict-errors-only（worktree 自己）：**0 ERROR**（321 既有 WARNING，rc=0）。
  - ruff（4 个改动脚本）：All checks passed（修 W605 docstring 转义 ×2 + C401 set 推导）。
  - count-tests = **1215**（≥ 1202 基线，只增不减）。
  - md-field-get/common/structure 单测：49 passed。

## 2026-08-22 步骤 3：全量自查 + 产出落盘

- 全量 pytest（ptmp 外部 basetemp）：**1210 passed / 2 skipped / 3 failed**
  - 3 failed 归因：① judge P1 ×2（B-judge 批范围，P3 红延续）；② test_bdd_8_clean_tree_zero_detection（test_env_adapt_docs.py:172 注释「无 /tmp 字面」短语自伤 R4——D 批文件禁越界；C 批已清自身 test_md_parse_scan.py 同型自伤（原 2 处→残余 1 处），需 D 批或主 Agent 定向改一行注释）。
  - 全量基线对照：P3 批 5 目标文件红 6 中 C 批 3 个（scan + S-3a/b）已转绿；check-gate 170 用例零回归。
- 结构/协议/静态卫生终验：check-structure-consistency（AGATE_ROOT=worktree）S1-S6+S0 全 OK exit 0；check-protocol-consistency --strict-errors-only 0 ERROR；ruff 4 脚本 All checks passed；count-tests 1215 ≥ 1202；AST 四脚本解析 OK。
- P4-implementation.md（batch C 段）落盘：implementation_dir + 新增文件核对表（test_md_parse_scan.py CODE_MAP_EXEMPT）+ 迁移摘要（A/B/C/D/S-3 逐组）+ 自查结果表 + 触发面清单 + 门槛对照 + 批界声明 + 2 条 [DESIGN_GAP]（P5 gate_commands.P5 数据点 / S-3a/S-3b 匹配粒度定案）；grep -c '^\[DESIGN_GAP:' = 2 自检通过。
- batch C-migration 完成。[PROD_TOUCHED]

---

# P4-progress（batch B-judge，implementer）

## 2026-08-22 步骤 1：输入读取 + 基线确认

- 已读 dispatch-context batchB（AGATE_CARD=P4 全文）、implementer.md、P0-brief、P2-design §4.3/§1.1 M7-M9/§5 批表、P2-review（锁定决策 2/5 + NB-4 + TG-2）、P3-test-cases §5 契约注解 1、AGENTS.md。
- 实读现状：check-gate.py gate_p1 全文（L538-637，C 批重构后）+ gate_p65（L997-1021 参照）+ `_load_state_yaml`（L283-297）+ 导入块（L37-156）；agate_common read_rules_yaml（L637-646）/ resolve_rules_root（L649-663）；dispatch.yaml 38 行 + dispatch.schema.json（additionalProperties:false → 须同步）；state-machine L430-459（judge 块 L440-448）；P1 卡产出规格 + frontmatter 样例；test_check_gate.py judge P1 用例 7 个（L2767-2861）。
- 环境确认：`~/.agate` 为 legacy 软链→主 checkout；但 resolve_hook_root（use_legacy=False）对 worktree 脚本走脚本路径上溯兜底 → rules root = **worktree 自己 agate/rules**（测试将读到本批新增 judge_required_since）。AGATE_ROOT 未设置。
- 基线（B 批文件集内待转绿）：judge P1 2 红（missing judge / disabled after cutoff）+ 5 守卫（enabled true / pre-cutoff / 无 created / falsy pre-cutoff / 非 dict）+ gate_p65 三态既有用例保绿。

## 2026-08-22 步骤 2：5 文件改动落盘

- check-gate.py：① 导入块加 `read_rules_yaml`（agate_common，C 批既有）+ except 兜底 `return None`（数据缺失 fail-open）；② 新增 `_ISO_DATE_RE` + `_is_iso_date` helper（ISO 8601 日期/带时间后缀判据，created 缺失/非 ISO → False → 调用方 fail-open）；③ gate_p1 在 NEED_CONFIRM 格式检查后、vision 检查前**纯叠加** judge 块：`judge = _load_state_yaml(task_dir).get("judge")`；dict+enabled truthy → 放行；falsy/缺失/非 dict 同走 created 判据（NB-4）——created ISO 且 ≥ cutoff（read_rules_yaml(resolve_rules_root(SCRIPT_DIR), "dispatch")）→ exit 1；否则跳过。gate_p65 / P2-P8 分支 / 退出码语义逐字节未动。
- dispatch.yaml：新增 `judge_required_since: "2026-08-22"`（顶部，注释说明判据）。
- dispatch.schema.json：properties 新增 `judge_required_since`（type string）——additionalProperties:false 下 S-5 校验通过前提。
- state-machine.md L442-443：`enabled: true` 注释语义更新（机制后新任务必须含 judge.enabled:true，check-gate P1 机械校验；历史任务缺块 → 跳过）；P6.5 硬边界/早退语义未动。
- P1-requirements.md：产出规格 checklist 新增「judge 启用声明」条 + frontmatter 样例注释同步。
- test_check_gate.py：P3 已写 7 用例，未改动（先跑红转绿，仅契约出入时按契约微调）。

## 2026-08-22 步骤 3：调试 + 转绿

- 首次自跑 7 用例：2 红仍红（exit 2）→ 追踪发现 `resolve_rules_root(SCRIPT_DIR)` 传目录而非文件 → dirname×2 落到 worktree 根 → rules 解析到 worktree 根/rules（错误），dispatch.yaml 读不到 judge_required_since → cutoff None → fail-open 跳过。
- 修复：改 `resolve_rules_root(__file__)`（对齐 check-gate L750 known_phase_ids 与 agate-read-gate-commands L40 的既有用法）。
- 修复后：judge P1 7 用例全绿（2 红转绿：missing judge / disabled after cutoff；5 守卫全保绿）。
- 全量 test_check_gate.py：**172 passed**（C 批 170 + 2 新绿），gate_p65 三态既有用例保绿，零回归。

## 2026-08-22 步骤 4：注释自伤修复 + batch B 文档节落盘（收尾）

- **任务 1（注释自伤）**：`agate/tests/unit/test_env_adapt_docs.py:172` 注释「无 /tmp 字面（用 tmp_path）」→「无临时目录字面量（用 tmp_path）」——R4 正则 `/tmp([\s/\"']|$)` 命中（`/tmp` + 空格），注释行无豁免，改措辞移除字面量。
  - 验证：`check-platform-assumptions.py` **exit 0 无 R1-R5 命中**；`pytest test_check_platform_assumptions.py` **16 passed**。
  - 同类扫描（grep `/tmp`）：TAG0022 改过的 `tests/unit/`（test_env_adapt_docs.py / test_md_parse_scan.py）与 `scripts/`（check-gate.py / agate_common.py / agate-md-field-get.py / check-protocol-consistency.py / check-structure-consistency.py）——仅 `check-structure-consistency.py:33` docstring「无 /tmp、」存量行（git diff 确认非 TAG0022 改动；`/tmp` 后随全角 `、` 不匹配 R4 字符类，扫描器不命中）→ 按任务约束不改动，余者无残留。
- **任务 2（batch B 文档节）**：P4-implementation.md 追加 `# P4 实现 — batch B-judge（RM-AG0039，judge 启用强制化）` 节（`---` 分隔，对齐 batch A/D/C 格式：implementation_dir / 新增文件核对表 / 改动摘要[5 文件逐条 + gate_p1 judge 块详述] / 自查结果 / 触发面清单 / 门槛对照），内容以已落盘实现与本次实测为准。
  - 验证：`pytest test_check_gate.py` **172 passed**；`check-structure-consistency.py` **0 ERROR**（S1-S6+S0 OK）；`check-protocol-consistency.py --strict-errors-only` **0 ERROR**（321 既有 WARNING）；`count-tests.sh` **1215 ≥ 1202**。未跑全量 pytest（归主 Agent）。

---

# P4-progress（review 评审，追加段）

## 2026-08-23 review Pass 1/2 核对记录
- 输入读取完成：dispatch-context（AGATE_CARD=P4 全文）、review.md、P4-implementation.md（4 批）、P2-design §1/§3/§4/§5/§6、P1-requirements（BDD-1..10）、P3-test-cases、P2-review（锁定决策+NB+TG）、P0-brief。
- git diff 逐文件核对四批：A（workflow+UPGRADING+AGENTS）、C（check-gate/agate_common/agate-md-field-get/check-structure-consistency/phases.yaml/test_md_parse_scan）、B（check-gate judge 块+dispatch.yaml+schema+state-machine+P1 卡）、D（check-protocol-consistency M15+test_env_adapt_docs L172 注释）。
- 迁移等价核对：A 组 9 读点全迁 _md_field_get（NO_FALLBACK_STRING: status/agent/project_phase/created；NO_FALLBACK_INT: code_map_*）；B 组 7 正则删除，count_markers/has_marker/extract_marker_desc 逐字节同正则（_lines==splitlines 确认）；C 组 12 读取器逐条与原内联正则比对等价（含 P6 汇总行排除/P4-P7 DESIGN_GAP 双口径/SUGGEST 三连剥离）；D 组 extract_embedded_yaml_blocks 同正则。E/F 组未动。
- S-3a/S-3b：既有 S-3 outputs/orphan/exec_role 检查保留（test_bdd_5_s3_card_output_mismatch 保绿）；P6.5 无卡 `if not card_path: continue` 跳过（NB-2）；_gate_rules_block S-3a fallback 推进条件、S-3b 仅 gate 规则节；真实树 S1-S6+S0 全 OK exit 0。P5 散文去 token（DESIGN_GAP 1，无消费方 grep 命中）。
- judge 边界：判据=dict+enabled truthy 放行 / 缺失+falsy+非 dict 同走 created ISO≥cutoff → exit 1；7 用例全边界 + 端到端实跑（historical created 2026-08-19 无 judge → exit 2；mechanism-after created 2026-08-22 无 judge → exit 1）。gate_p65/2i.1/ci-backstop 无 diff。
- M15：默认 () 逐字节不变（R6）；call-time 读 env；分量前缀匹配；单测 2 用例 + 真实树 0 ERROR。
- workflow：ruff job name 稳定 `ruff`，仅 install 行锁 0.16.4；YAML 解析 OK；其余 job 未动。
- 自跑 gate 全绿：全量 pytest 1213 passed/2 skipped/0 failed（exit 0）；目标 5 文件 213 passed；structure S1-S6+S0 OK；consistency --strict-errors-only 0 ERROR；ruff All checks passed；count-tests 1215≥1202；platform-assumptions exit 0。
- 发现 INFORMATIONAL ×2：（1）B 批在 P4-progress 记录了对 test_env_adapt_docs.py:172 注释自伤修复（该文件属 D 批文件集），与 P4-implementation.md B 节「禁改范围未触碰」声明不符——代码正确且必要，文档措辞需主 Agent 修正或标注批界偏差；（2）agate_common import 失败降级 stub 中 count_p7_markers/count_p6_pass_fail/count_code_map_lines 返回 0 呈 false-PASS 方向（仅安装破损边），沿用 parse_gate_commands_block 降级先例，建议记录。
- protocol-alignment-review：6 ALIGNED / 0 MISALIGNED / 1 NEEDS_HUMAN_REVIEW（A5 UPGRADING ②③ 占位，已 HUMAN_CONFIRMED 由 P8 补齐）——与 dispatch-context 提示一致，非 BLOCKER。
- 结论：0 CRITICAL → status: approved。

---

# P4-progress（收尾 implementer，P4-review 2×INFORMATIONAL 处理）

## 2026-08-23 批界偏差标注 + DEBT0018 登记
- **任务 1（批界偏差标注）**：P4-implementation.md batch B-judge 节末尾追加「批界偏差标注」节（L374-376）——test_env_adapt_docs.py:172 注释（R4 平台假设扫描自伤修复「无 /tmp 字面」→「无临时目录字面量」）经收尾 implementer 修改，属跨批必要修复（D 批文件集）；根因 = 扫描器对注释文本中 `/tmp` 字面量误报，修复不改变测试语义；P7 一致性核对按此标注处理。grep 确认落盘。
- **任务 2（DEBT 登记）**：tech-debt.md 追加 DEBT0018（编号 = 既有最大 DEBT0017 + 1）——agate_common import 降级 stub 返回 0/空，安装破损边缘消费脚本（check-gate.py gate_p7/gate_p6/gate_p4 CODE_MAP）false-PASS（漏报方向）；severity low；evidence 实核：P4-review.md INFORMATIONAL #2（L93-96）+ check-gate.py L73-160 降级 stub 块（count_p7_markers L141-142 / count_p6_pass_fail L138-139 / count_code_map_lines L147-148 / count_markers L114-115）+ agate_common.py count_p7_markers L951。schema 校验：worktree 与 ~/.agate 稳定版 check-debt.py 均 exit 0。
- 状态标记：`[PROD_NOT_TOUCHED]`（仅改 worktree agate-workspace 内 3 个文档文件；协议本体/脚本/稳定版 ~/.agate 未动）。

---

# P4-progress（P5→P4 回退修复轮：BDD-9 缺口，RM-AG0041）

> 本段为 P5 验证 → P4 定向修复轮（只修根因）。状态标记：`[PROD_TOUCHED]`（改动仅限测试文件
> agate/tests/unit/test_check_gate.py；协议文档/生产脚本/稳定版 ~/.agate 未动）。

## 2026-08-23 根因（P5 verifier 实测，unit.md 记录）

`test_tag0005_bdd_9_review_role_instruction_single_file`（L1804-1811）对 `agate_root` 做
`rglob("*.md")` 全树扫描并断言「Review 角色特别指令」命中恰 1 处。当 pytest basetemp 位于仓库根内
（如 `agate/.bt-p5-inrepo/`）时，同会话其他测试（test_agate_render_dispatch_prompt.py 的 rp_*、
test_bdd_20；test_pre_commit_hook.py 的 test_b3 等）向 basetemp 下写入渲染的 dispatch-prompt .md
（含该标记）→ rglob 扫到 → `len(hits)==5 != 1` → AssertionError。仓库外 basetemp 无此问题。
与 M15（test_bdd_25 一致性扫描排除钩子）同类 basetemp 位置依赖，直接命中 BDD-9 验收锚。

## 2026-08-23 修复（P4 implementer）

- 文件：`agate/tests/unit/test_check_gate.py`（仅此一文件；改该测试函数 + 补 `from pathlib import Path`）
- 方式：测试加 `tmp_path_factory` fixture，`basetemp = Path(tmp_path_factory.getbasetemp())`；
  遍历 `rglob("*.md")` 时 `p.relative_to(basetemp)`（ValueError 即不在 basetemp 下）跳过 basetemp
  子树产物；其余扫描/断言语义不变（协议目录内「Review 角色特别指令」恰 1 处 =
  assets/templates/dispatch-prompt.md）。
- 平台无关：无裸 PATH=/裸 python3/POSIX symlink//tmp 字面量（R1-R5 无新增命中）。

## 2026-08-23 验证进度

- [x] 单测（外部 basetemp /home/kity/oclab/dsh-workspace/ptmp）：1 passed（exit 0）
- [x] 全量位置 1（外部 basetemp /home/kity/oclab/dsh-workspace/ptmp，timeout 900）：**1213 passed, 2 skipped, exit 0**
- [x] 全量位置 2（仓库内 basetemp agate/.bt-fix，timeout 900）：**1213 passed, 2 skipped, exit 0**；测后 `rm -rf agate/.bt-fix` 已执行（BTFIX GONE）
- [x] 平台扫描 `check-platform-assumptions.py`：exit 0（R1-R5 0 命中）
- [x] R4 自伤守卫 `test_check_platform_assumptions.py`（外部 basetemp）：16 passed（exit 0）

## 结论

- **两位置均 0 failed** → BDD-9 验收锚（任意 basetemp 位置下全量 pytest 0 失败）达成，无需登记 known-failure。
- 改动文件：`agate/tests/unit/test_check_gate.py`（import + 1 测试函数，git diff 确认仅此）。
- 仓库内 basetemp 下无其他同类位置依赖失败（位置 2 全量 1213 passed 覆盖，test_bdd_25 走 M15 注入分支正常）。
- 注：git status 中 `gate-events.jsonl` 的 +2 与未跟踪的 P5-* 文件为 P5 verifier/主 Agent 既有产物，非本修复轮改动。
- 状态标记：`[PROD_TOUCHED]`（改动仅限测试文件；协议文档/生产脚本/稳定版 ~/.agate 未动）。
