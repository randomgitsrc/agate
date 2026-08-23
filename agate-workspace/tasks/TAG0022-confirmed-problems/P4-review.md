---
phase: P4
task_id: TAG0022-confirmed-problems
type: review
parent: P4-implementation.md
trace_id: TAG0022-P4-20260822
status: approved
created: 2026-08-22
agent: review
---

# P4 实现评审 — TAG0022 四批实现（A-ruff / C-migration / B-judge / D-env-tests）

> 评审角色：review（偏执 Staff Engineer；攻击者视角找会在生产炸掉的东西）
> 状态标记：`[PROD_NOT_TOUCHED]`（仅只读消费 worktree 代码与协议文件；写操作仅落 P4-review.md / P4-progress.md；稳定版 ~/.agate 与主 checkout 未动）
> 评审对象：worktree 工作区 diff（`.worktrees/agate-TAG0022/`，四批未提交改动，base=commit f256d2c P3）
> 上游锁点：P2-review.md（锁定决策 1-8 + NB-1..6 + TG-1..3）/ P3-test-cases.md（§5 契约注解 1-5）/ P1-requirements.md（BDD-1..10）

## 结论

**status: approved（0 CRITICAL / 2 INFORMATIONAL，无 BLOCKER）。**

四批实现与 P2 设计逐条对齐、P3 红测试全转绿、全量回归零破坏；Pass 1（判定口径漂移 / S-3 误伤 / judge 边界 / M15 默认行为 / workflow 破坏）逐项实测无 CRITICAL。2 条 DESIGN_GAP（P4-implementation.md L289/L291）已由主 Agent 采纳且 protocol-alignment-review 独立核实成立，本评审复核无新问题，不作为 rejection 依据。2 条 INFORMATIONAL 为批界文档一致性与 import 降级方向观察，均不影响功能正确性，按 review 角色只「说怎么改」，修复归主 Agent 回派。

## 客观验证证据（本评审自跑）

| 项 | 命令（worktree 内） | 结果 |
|----|---------------------|------|
| 全量 pytest | `python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp` | **1213 passed / 2 skipped / 0 failed（exit 0）** |
| 目标测试文件 | pytest test_md_parse_scan / test_check_structure_consistency / test_check_gate / test_env_adapt_docs / test_check_routing | **213 passed** |
| 结构一致性 | `AGATE_ROOT=<worktree>/agate python3 agate/scripts/check-structure-consistency.py` | **S1-S6+S0 全 OK，exit 0**（S-3a/S-3b 真实树零误报） |
| 协议一致性 | `check-protocol-consistency.py --strict-errors-only`（worktree 自己） | **0 ERROR（321 既有 WARNING），exit 0** |
| ruff | `~/.venvs/agate-dev/bin/ruff check agate/` | **All checks passed，exit 0** |
| 用例计数 | `bash agate/tests/scripts/count-tests.sh` | **1215 ≥ 1202 基线（只增不减）** |
| 平台无关 | `check-platform-assumptions.py` | **exit 0，无 R1-R5 命中** |
| judge 端到端 | check-gate.py P1（真实目录） | historical（created 2026-08-19 无 judge）→ **exit 2**；mechanism-after（created 2026-08-22 无 judge）→ **exit 1** |
| workflow YAML | python3 yaml.safe_load | 解析 OK；jobs 含 `ruff`；job name=`ruff`；run=`pip install ruff==0.16.4 && ruff check agate/` |

## Pass 1（CRITICAL）— 数据安全与正确性

### C1. check-gate.py 迁移判定口径漂移 —— 无 CRITICAL，逐分支核对通过

对照 P1 gate 规则（P1-review approved + BDD 锚点 + NEED_CONFIRM 语义 + vision/ui 检查）逐分支核对迁移前后行为：

- **A 组（frontmatter → _md_field_get）**：`_frontmatter_field` 删除；9 处调用全迁（gate_p1 的 P1-review status/agent、gate_p2 的 P2-review status/agent + P1 project_phase、gate_p4 的 P4-review status/agent（NB-6 L799/805 两个读点已含）、gate_p7 的 code_map_new_files_count/code_map_reviewed_count）。agate-md-field-get.py 注册 `status/agent/project_phase/created` → NO_FALLBACK_STRING_FIELDS、`code_map_new_files_count/code_map_reviewed_count` → NO_FALLBACK_INT_FIELDS（KNOWN_OPS 自动派生，dispatch 逻辑 L252-262 核实）。对 well-formed frontmatter 逐字节等价；畸形/带引号差向更正确（NB-3 边界，`status: "approved"` 带引号旧路径会假 FAIL、新路径正确放行，方向为修复非假 PASS）。**DESIGN_GAP 遗留 L1098-1107 已解**：CODE_MAP 两层校验从「unknown op 恒回退空串→整段跳过」变为字段存在时真实执行——行为变严格/更正确，非漂移，P7 既有用例保绿。
- **B 组（行首标记）**：7 个模块级正则删除；`count_markers/has_marker/extract_marker_desc`（agate_common L822-858）逐字节同正则（RM-AG0001 可选反引号前缀、SUGGEST 三连剥离、NC 单段剥离）；`_lines == text.splitlines()`（check-gate.py L202-205）→ 计数语义与旧 `sum(1 for line in _lines(...) if _NC_RE.search(line))` 完全一致。need_confirm_resolved/suggest_resolved 结构化匹配、NO_NEED 存在性、typo 兜底 2 条、不合规格式兜底全部保留，退出码语义不变。
- **C 组（任务产出格式判定）**：12 个共享读取器逐条与原内联正则比对等价——extract_bdd_titles（`^#{2,5}\s+BDD-[0-9]+.*$` MULTILINE 逐字）、parse_ui_design_section（节标题定位 + 渲染形态/适用维度首条声明）、candidate_count_value（`^candidate_count:` + 首数字串）、design_trivial_declared（`^(design_trivial|follows_existing_pattern):\s*\S`）、has_keyword ×3（tradeoff/choice_and_reason/design_gap 同正则含 IGNORECASE）、count_p6_pass_fail（PASS|FAIL\b.*BDD-[0-9] 大小写不敏感）、count_p7_markers（BLOCKER/DEVIATION-CRITICAL + 汇总行排除 `[BLOCKER](:|：)?\s*[0-9]+\s*条?\s*$`，M4 全角冒号）、count_design_gap（P7 blockquote 口径 vs P4 无 blockquote 口径两参）、count_code_map_lines、parse_fail_list_block（sed `'1d;$d'` + 空行剔除等价）、count_kf_entries（`^\|\s*[0-9]+\s*\|`）。P0/P3/P4/P5/P8 分支判定逻辑未动（N5）。
- **D 组（内嵌 yaml 块）**：`extract_embedded_yaml_blocks`（同正则 ` ```(?:yaml|yml)\s*\n(.*?)``` ` DOTALL 单点），read_vision_tri_state 与兜底循环共用。
- **vision/ui 检查**：`_gate_p1_vision_capability` / `_gate_p1_ui_shape` / `_gate_p2_ui_design_section` 仅换读取方式（bdd_titles/UI 节/内嵌块），判定口径与 exit 语义不变。
- E 组（.state.yaml）/ F 组（git/CHANGELOG）按 D2 未动。
- BDD-3 静态扫描（test_md_parse_scan.py，24 条模式）命中 0；BDD-4 全量 1213 绿。

### C2. S-3a/S-3b 收紧误伤既有 S-3 —— 无 CRITICAL，叠加验证通过

- **NB-1 叠加不重定义**：S-3a/S-3b 是 `_check_s3`（check-structure-consistency.py L234-291）既有 outputs/orphan/exec_role 检查**之后**新增的两个子检查块，既有检查逐行保留；「产出规格缺失 P2-review.md → 非 0」用例（test_bdd_5_s3_card_output_mismatch_exit_1）保绿。
- **NB-2 无卡片阶段跳过**：S-3a/S-3b 位于 `if not card_path: continue` 之后（L241-244），P6.5 无独立卡片 → `_phase_card_path` 返回 None → 天然跳过；P2 试点锚点强制（M0）仍在。
- **真实树零误报**：S1-S6+S0 全 OK exit 0。逐阶段核对 P1-P8 的 YAML gates 命令串 ↔ 卡片 `## gate 规则`（S-3a 回退 `## 推进条件`；S-3b 仅 gate 规则节）token 双向集合一致：P1/P2/P3/P4/P5/P6/P6.5(跳过)/P7/P8 全部对上（P6 卡 L173-179 含 check-judge-verdict.py/check-events.py token，YAML P6 gates 已声明；P5 卡 gate 节仅 check-gate.py P5，无 gate_commands.P5 token）。
- **P5 散文修正（DESIGN_GAP 1）**：`gate_commands.P5 exit 0 AND failed==0` → `P2 声明的验证命令全部 exit 0 AND failed==0`（去 token）。已 grep 确认 scripts 无该散文的消费方（phases.yaml gates prose 是信息性数据面，check-gate gate_p5 走自己的 P5-test-results 逻辑）——无破坏。
- **token 粒度定案（DESIGN_GAP 2）**：`_MACHINE_GATE_REF_RE` 三模式（check-gate.py P\d+(\.\d+)? / gate_commands.P\d+ / check-[\w-]+\.py）子串包含判定；实测 `check-gate.py P6.5` 与 `check-gate.py P6` 为不同 token（finditer 整体匹配），双向漏检方向均被捕获——无假阴性风险。

### C3. judge 校验边界（BDD-6/7）—— 无 CRITICAL，双向边界实测通过

- 实现（check-gate.py L644-664）与 P2-review 锁定决策 2 + NB-4 逐字一致：`judge = _load_state_yaml(task_dir).get("judge")`；dict + enabled truthy → 放行（原 P1 exit 2 语义不变）；缺失 / dict+falsy / 非 dict → 同走 created 判据（NB-4 推荐口径）：`created = _md_field_get("created", p1_file)`（created op 已注册 NO_FALLBACK_STRING，frontmatter-only）+ `cutoff = read_rules_yaml(resolve_rules_root(__file__), "dispatch").get("judge_required_since")`（rules 缺失 → None → fail-open，R5）。
- **漏拦面**：created 缺失/非 ISO → `_is_iso_date` False → 跳过（fail-open，R5 语义，P1 卡软层兜底 created+judge 必填）；pre-cutoff（created < "2026-08-22" 字典序）→ 跳过。端到端实测：historical（created 2026-08-19 无 judge）→ **exit 2 不拦**。
- **误拦面**：created ≥ cutoff 缺失/未启用 judge → **exit 1 + stderr 提示**；端到端实测 mechanism-after（created 2026-08-22 无 judge）→ **exit 1**。`_ISO_DATE_RE` 接受 ISO 日期 + 可选时间/时区后缀，同日后缀值字典序 ≥ 同日日期 → 恒判 mechanism-after，保守方向无漏拦。
- **判据健壮性**：`resolve_rules_root(__file__)` 传文件路径（对齐 known_phase_ids 既有用法 L750），B 批曾误传目录已修复；`_is_iso_date` 对非 str 返回 False；`judge: true`（bool 非 dict）按缺失处理（TG-2 用例断言 created 缺失时不拦）。
- **P6.5 链未动**：gate_p65 / pre-commit 2i.1 / ci-backstop 无 diff（锁定决策 5）；gate_p65 judge 三态既有用例（test_check_gate.py L2663-2729）保绿。
- 7 个 judge P1 用例覆盖全边界（缺失/falsy-after-cutoff exit 1 ×2；enabled-true/pre-cutoff/无 created/falsy-pre-cutoff/非 dict fail-open ×5）。

### C4. M15 排除钩子默认行为（R6）—— 无 CRITICAL，默认逐字节不变

- `_env_skip_dir_prefixes()`（check-protocol-consistency.py L119-140）：默认未设置/空值 → `()` → iter_md_files 无任何排除分支命中（R6）；call-time 读 env（import-time 注入与 call-time 注入均稳健，P3 §5 契约注解 3）；分隔符 os.pathsep（POSIX `/` 冒号 / Windows 分号）；正斜杠归一 `entry.strip().replace(os.sep, "/")`。
- 排除分支（L157-161）与既有 rel_parts 排除链同层（相对 root 分量判定，避免 worktree `.worktrees/` 绝对路径误排）；分量级前缀匹配 `rel_parts[:len(sp)] == sp` 避免 `foo` 误伤 `foobar.md`。
- 单测 2 用例（injected excluded / default unchanged）绿；真实树 consistency 0 ERROR 且 `test_m15_iter_md_files_default_unchanged` 断言默认产出全部 .md——无误排正常文件。

### C5. workflow 破坏既有 CI job —— 无 CRITICAL

- `.github/workflows/protocol-tests.yml` 仅 ruff job 的 install 行 `pip install ruff` → `pip install ruff==0.16.4`（+ 注释）；job name `ruff` 稳定未改名（BDD-1 可被分支保护引用）；pytest/shellcheck/consistency/gate-backstop/platform-scan job 零改动；YAML 解析 OK。required check 勾选为维护者配置（D1 边界），实现侧只交付 workflow + 文档（UPGRADING v0.61.0 ① 节含 Settings→Branches→分支保护→勾选 ruff 步骤；根 AGENTS.md step 5 后补验证句）。

### C6. 其他 CRITICAL 面

- **测试覆盖**：P3 红测试全转绿——C 批 3 红（test_md_parse_scan + S-3a + S-3b）、B 批 2 红（judge 缺失/falsy-after-cutoff）、D 批 1 红（M15 injected）→ 全量 1213 passed 0 failed；守卫用例（gate_p65 三态、S-3 既有、M15 默认、历史 fail-open）保绿；test_env_adapt_docs.py:172 注释自伤（`/tmp` 字面命中 R4）已修复，test_bdd_8_clean_tree_zero_detection 转绿。
- **P4-implementation.md 合规**：implementation_dir 逐批声明（A: worktree 根；C: agate/；B: scripts+rules+state-machine+P1 卡；D: agate/scripts/）；新增文件核对表每批含 CODE-MAP 判定（CODE-MAP 为模块级架构图无逐文件登记，test_md_parse_scan.py 为 P3 新增、本批校准，EXEMPT 理由成立）；`[DESIGN_GAP:` 计数 = 2（L289/L291）；触发面清单每批齐全。

## Pass 2（INFORMATIONAL）— 代码健康

### I1. 批界文档不一致：B 批实际触碰了 D 批文件集内的 test_env_adapt_docs.py

- **现象**：P4-progress.md（batch B 步骤 4）记录 B 批把 `agate/tests/unit/test_env_adapt_docs.py:172` 注释「无 /tmp 字面」改为「无临时目录字面量」（R4 自伤修复，必要且正确）；但 P4-implementation.md（batch B 节「本批禁改范围…未触碰」）声明该文件未触碰——两处记录自相矛盾；D 批复核结论「test_env_adapt_docs.py 零改动」也随之不再精确。
- **影响**：代码内容正确（该注释是 test_bdd_8 红的原因之一，修复后全量绿）；无功能缺陷。属批界纪律（D3/HANDOFF §7）的执行偏差 + 实现文档事实性瑕疵，P7 一致性核对时会被交叉检查。
- **Fix（说怎么改）**：主 Agent 回派 implementer 在 P4-implementation.md batch B 节补一条批界偏差声明（如 `[BATCH_BOUNDARY_DEVIATION: 为修复 R4 自伤注释触碰 D 批文件 test_env_adapt_docs.py:172 单行注释，内容为必要修复，D 批复核已覆盖]`），或由 D 批复核记录认领该行；无需代码重做。

### I2. agate_common import 失败降级 stub 的 false-PASS 方向（安装破损边缘）

- **现象**：check-gate.py except ImportError 降级 stub 中 `count_p7_markers` → (0,0)、`count_p6_pass_fail` → (0,0)、`count_code_map_lines` → 0——若 agate_common 缺失/损坏（安装破损），gate_p7 的 BLOCKER/DEVIATION 计数与 CODE_MAP 转抄核对会**假通过**；`count_markers` → 0 侧是 fail-closed（`[NEED_CONFIRM]` 字面 + nc_blocking==0 → exit 1）。方向不一致是既有降级先例（parse_gate_commands_block 同返 0）的延续，代码注释已声明；仅在 agate_common 整体不可用时触发，正常安装不可达。
- **Fix（说怎么改，可选）**：降级 stub 改为显式失败（如 P7 分支检测 `read_rules_yaml is None or count_p7_markers is None` 时输出「安装破损」错误并 return 1），或在 tech-debt.md 登记该边缘（低优先）；当前不阻断。

### I3. 其他观察（非阻塞）

- `_is_iso_date` 对带时区后缀的 created 值做字典序比较，方向恒保守（不漏拦），无假 PASS 风险。
- agate_common 新增 M2-0038 节命名/风格与既有 `parse_gate_commands_block`、`count_p2_declared_fields` 一致（模块 docstring + 函数级 docstring + 与原内联语义等价注释），无资源泄漏/错误吞掉问题（yaml.safe_load 异常 → None/continue 均显式处理）。
- A5 UPGRADING v0.61.0 ②③ 占位小节：protocol-alignment-review 判 NEEDS_HUMAN_REVIEW 已获 `[HUMAN_CONFIRMED]`（P8 版本发布阶段补齐，P8 核对清单已加「UPGRADING ②③ 占位已补齐」项）——按派发指引不构成 BLOCKER，本评审复核同意。

## 门槛自检

- P4-review.md 存在且非空 ✓；Header status=approved、agent=review（非 main）✓
- 结论引用具体锚点（文件/行号/测试名）✓；CRITICAL 面全部逐项给出证据
- 已跑全量 pytest 并附 passed/failed 计数（1213 passed / 2 skipped / 0 failed）✓
- 状态标记：`[PROD_NOT_TOUCHED]` ✓
