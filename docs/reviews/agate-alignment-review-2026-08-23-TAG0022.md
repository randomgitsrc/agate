---
review_date: 2026-08-23
reviewer: protocol-alignment-review
change_summary: TAG0022 P4 A/B/C/D 四批落地后协议-脚本对齐审查——check-gate.py 解析层 A/B/C/D 组迁 agate_common 共享读取器 + agate-md-field-get 新 op 注册 + S-3a/S-3b 双向收紧 + judge P1 强制化 + M15 排除钩子 + ruff 锁版
files_changed:
  - agate/scripts/check-gate.py
  - agate/scripts/agate_common.py
  - agate/scripts/agate-md-field-get.py
  - agate/scripts/check-structure-consistency.py
  - agate/scripts/check-protocol-consistency.py
  - agate/rules/phases.yaml
  - agate/rules/dispatch.yaml
  - agate/rules/schema/dispatch.schema.json
  - agate/state-machine.md
  - agate/phase-cards/P1-requirements.md
  - agate/UPGRADING.md
  - .github/workflows/protocol-tests.yml
  - AGENTS.md
  - agate/tests/unit/test_md_parse_scan.py
  - agate/tests/unit/test_env_adapt_docs.py
  - agate/tests/unit/test_check_gate.py（P3 commit，审）
  - agate/tests/unit/test_check_structure_consistency.py（P3 commit，审）
  - agate/tests/unit/test_check_routing.py（P3 commit，审）
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | NEEDS_HUMAN_REVIEW |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

汇总：**6 ALIGNED / 0 MISALIGNED / 1 NEEDS_HUMAN_REVIEW**

状态标记：`[PROD_TOUCHED]`（审查对象为 worktree 内产品脚本改动；本次审查仅写 docs/reviews/ 下文件，未触碰任何产品文件）。

## 逐项审查

### A1: 文档→脚本对齐

**结论**：ALIGNED

#### 1. P2 §4.2.1 A 组逐点映射（P2-design.md:162）vs check-gate.py

**文档声明**（P2-design.md:162）：
> `_frontmatter_field` L164-170，使用 L500(status)/L506(agent)/L716(status)/L722(agent)/L768(project_phase)/L1108-1109(code_map_*) → agate-md-field-get.py 新 op：`status`/`agent`/`project_phase` → NO_FALLBACK_STRING_FIELDS；`code_map_new_files_count`/`code_map_reviewed_count` → NO_FALLBACK_INT_FIELDS

**脚本实现**（check-gate.py diff）：
- `_frontmatter_field` 定义删除（diff `@@ -161,15 +227,6 @@`），9 处调用全部改走 `_md_field_get`：gate_p1 status/agent（2 处）、gate_p2 status/agent + project_phase（3 处）、gate_p4 status/agent（2 处，NB-6 补全 L799/805）、gate_p7 code_map_new_files_count/code_map_reviewed_count（2 处）。
- agate-md-field-get.py：`NO_FALLBACK_STRING_FIELDS` 新增 status/agent/project_phase/created（diff L102-113）；`NO_FALLBACK_INT_FIELDS` 新增 code_map_new_files_count/code_map_reviewed_count（diff L126-137）。`KNOWN_OPS`（agate-md-field-get.py:252-256）由各字段集自动派生，新 op 自动入白名单。
- 语义核对：`_get`（agate-md-field-get.py:240-249）frontmatter presence → `_format_value`；NO_FALLBACK 字段无正文回退 → 空串——与原 `_frontmatter_field`（sed 式 frontmatter-only 行扫描）对 well-formed frontmatter 等价。
- **NB-3 已知边界**（P2-review.md:42）：畸形/带引号/带注释 frontmatter 存在行为差异，方向为 fail-closed（畸形 → 更早 exit 1）或修正（带引号 → 正确去引号），**不产生假 PASS 漏洞**；等价声明限定「well-formed + 既有 1202 用例全绿」。P2-review 已接受该边界。**不判 MISALIGNED**。

#### 2. P2 §4.2.1 B 组（P2-design.md:164）vs count_markers 族

**文档声明**：`_NC_RE/_SUGGEST_RE/_NO_NEED_RE/_NC_DESC_RE/_SUGGEST_DESC_RE/_SUGGEST_TAIL_BT_RE/_SUGGEST_TAIL_BRACKET_RE` L101-110 + 计数 L523-584 → agate_common `count_markers(text, kind)`（逐字节同正则）+ 描述提取

**脚本实现**（agate_common.py diff L815-885）：
- 7 个正则原样迁入 agate_common（`_NC_RE` 等，逐字节同正则）；check-gate.py 模块级定义删除，改为 import。
- `count_markers` 用 `text.splitlines()`，与 check-gate.py `_lines`（check-gate.py:202-204，即 `text.splitlines()`）逐行语义一致（已核实）。
- `extract_marker_desc` NC 单段剥离 / SUGGEST 三连剥离，与 gate_p1 原内联（check-gate.py diff `@@ -555,11 +618,9 @@`）逐字节一致。
- 消费点：`nc_blocking = count_markers(p1_text, "NC")`、`nc_suggest = count_markers(p1_text, "SUGGEST")`、`has_marker(line, "NC"/"SUGGEST"/"NO_NEED")` 逐行匹配、`extract_marker_desc(line, ...)`——判定口径（退出码）不变。

#### 3. P2 §4.2.1 C 组（P2-design.md:165）vs agate_common 12 读取器

**脚本实现**（agate_common.py diff L887-1016）逐一比对原内联正则：
- `extract_bdd_titles` = `"\n".join(re.findall(r"^#{2,5}\s+BDD-[0-9]+.*$", text, re.MULTILINE))` ✓
- `parse_ui_design_section`：节标题定位 + `渲染形态:`/`适用维度:` 首条声明提取，与原内联 `_lines(ui_block)` 循环一致 ✓
- `candidate_count_value`：`^candidate_count:` 匹配 + 行内首数字 int，匹配但无数字 → 0（与原 `if m: candidate_count = int(...)` + break 等价，因原逻辑 break 时若 m 为空则保持 0）✓
- `design_trivial_declared` = `^(design_trivial|follows_existing_pattern):\s*\S` ✓
- `has_keyword`：tradeoff 组（`权衡|选择理由|取舍|考量|trade-?off|理由与权衡`）/ choice_and_reason 组（`选择` 且 `理由|原因|因为`）/ design_gap 组（`设计偏差|design gap|未列入|gap:` + IGNORECASE）三 kind 与原 P2/P7 内联等价 ✓
- `count_p6_pass_fail`（P6 旧格式，含 BDD 编号、IGNORECASE）、`count_p7_markers`（BLOCKER/DEVIATION-CRITICAL 排除 `: N 条` 汇总行，含全角冒号 alternation）、`count_design_gap`（P7 口径含 blockquote 前缀 `>?`；P4 口径不含——check-gate gate_p7 两消费点分别传 allow_blockquote=True/False）、`count_code_map_lines`、`parse_fail_list_block`（sed 三连等价）、`count_kf_entries`（`^\|\s*[0-9]+\s*\|`）——全部与原内联逐字节等价 ✓
- P4 转抄核对保留前置过滤 `[line for line in p4_gap_lines if "[DESIGN_GAP:" in line]`（check-gate.py:1126），再 `count_design_gap("\n".join(...), allow_blockquote=False)`——与原 grep -cE 口径一致 ✓

#### 4. P2 §4.2.1 D 组（P2-design.md:166）vs extract_embedded_yaml_blocks

**脚本实现**：`_EMBEDDED_YAML_BLOCK_RE = re.compile(r"```(?:yaml|yml)\s*\n(.*?)```", re.DOTALL)`（agate_common.py diff L1019-1030），与原 `_gate_p1_vision_capability` 兜底 `re.finditer` 同正则单点；check-gate.py 兜底循环改 `for block in extract_embedded_yaml_blocks(text)`。E/F 组（.state.yaml / git / CHANGELOG）未迁移（D2 口径）✓

#### 5. S-3 收紧（P2 §4.2.2 / BDD-5）vs check-structure-consistency.py + phases.yaml

**文档声明**（P2-design.md:170-174）：
> S-3a（YAML→md）：每阶段 gates[].check 中的命令串须出现在对应卡片 `## gate 规则`（或推进条件）节。S-3b（md→YAML）：卡片 `## gate 规则` 节中机器可判定命令行（匹配 `check-gate.py P\d+` / `gate_commands.P\d+` / `check-[\w-]+\.py` 模式）须在该阶段 gates[].check 有声明。

**脚本实现**（check-structure-consistency.py diff）：
- `_MACHINE_GATE_REF_RE` = `check-gate\.py P[0-9]+(?:\.[0-9]+)? | gate_commands\.P[0-9]+(?:\.[0-9]+)? | check-[A-Za-z0-9_-]+\.py`——与 P2 §4.2.2 三模式一致 ✓
- S-3a：`_yaml_gate_cmd_refs(phase)` ⊆ `_gate_rules_block(card_text, fallback_to_conditions=True)` 提取的 refs；缺 gate 规则节回退推进条件 ✓
- S-3b：卡片 gate 规则节 refs ⊆ YAML gates refs；**仅 gate 规则节，推进条件不纳入**——与 P2 §4.2.2 措辞一致（S-3a 才带「或推进条件」）✓
- NB-1：既有 S-3 outputs/orphan/exec_role 检查保留（`_check_s3` ①② 原样）✓；NB-2：P6.5 无卡片 → `_phase_card_path` 返回 None → 跳过 ✓
- phases.yaml：各阶段 gates[].check 增补命令串（P1/P2/P4/P5/P7 → check-gate.py P{n}；P3 → + check-tdd-red + gate_commands.P3；P6 → + check-p6-format/check-gate.py P6.5；P6.5 → + check-gate.py P6.5；P8 → + check-p6-provenance --audit7-only + gate_commands.P5 + DEBT0013 时序）
- **实测**：`check-structure-consistency.py` 对 worktree 真实树 → S1-S6+S0 全 OK，exit 0（10 阶段 S-3a/S-3b 双侧一致）

**[KNOWN_DEVIATION: 来源 TAG0022 P4-implementation.md DESIGN_GAP 2，主 Agent 采纳，理由核实成立]**：P2 §4.2.2 未指定 S-3a/S-3b 匹配粒度，实现定案为 token 提取（三模式正则）做子串包含判定，非整串比对；S-3a 缺卡节回退推进条件、S-3b 仅 gate 规则节。P3 三用例（s3a/s3b/双侧一致）+ 真实树 10 阶段 0 ERROR 验证该口径成立，语义不弱于整串比对（YAML 命令串的每个可判定 token 都必须在 md 侧出现）。**按原则 6 不计入需修复项。**

**[KNOWN_DEVIATION: 来源 TAG0022 P4-implementation.md DESIGN_GAP 1，主 Agent 采纳，理由核实成立]**：P2 §4.2.2 示例「P5 → gate_commands.P5」在真实树不可达——P5 卡 gate 规则节（P5-verification.md:82-84）只有 `check-gate.py P5`，无 gate_commands.P5 token，而 S-3a 要求 YAML 命令串须在卡节出现；R4「补卡片」路径因 phase-cards/ 不在 C 批文件集不可执行。实现取 S-3a/S-3b 双侧一致为硬锚：P5 gates 散文改「P2 声明的验证命令全部 exit 0 AND failed==0」（去 token，语义保留——gate_commands.P5 实际命令仍在 P2-design.md gate_commands 块，check-gate P5 分支照常消费）+ 增补 check-gate.py P5 $TASK_DIR。语义无降级，真实树 S-3 exit 0。**按原则 6 不计入需修复项。**

#### 6. judge 判据（P2 §4.3 + P3 契约注解 1）vs check-gate.py judge 块

**文档声明**（P3-test-cases.md:77 契约注解 1）：
> judge 缺失 → 读 P1 frontmatter created（agate-md-field-get created op，ISO 字典序比较）≥ judge_required_since（rules/dispatch.yaml "2026-08-22"）→ exit 1；created 缺失/非 ISO → fail-open（exit 2）；judge.enabled falsy 与缺失同走 created 判据（falsy + created ≥ cutoff → exit 1；falsy + pre-cutoff → 跳过）；judge 非 dict（如 judge: true）→ 按缺失处理（fail-open）

**脚本实现**（check-gate.py diff `@@ -580,9 +641,28 @@`）：
```python
judge = _load_state_yaml(task_dir).get("judge")
if not (isinstance(judge, dict) and judge.get("enabled")):
    created = _md_field_get("created", p1_file)
    dispatch_rules = read_rules_yaml(resolve_rules_root(__file__), "dispatch")
    cutoff = dispatch_rules.get("judge_required_since") if isinstance(dispatch_rules, dict) else None
    if isinstance(cutoff, str) and _is_iso_date(created) and created >= cutoff:
        ... return 1
```
- `judge` dict + enabled truthy → 放行（原 P1 判定 exit 2 不变）✓；falsy/缺失/非 dict → 统一走 created 判据 ✓；created ≥ cutoff → exit 1；pre-cutoff / 缺失 / 非 ISO → 跳过（fail-open，R5）✓
- `_is_iso_date`（check-gate.py:307-312）regex 允许 `YYYY-MM-DD` 或带 `T`/空格时间后缀——与 P1 卡 frontmatter `created: {YYYY-MM-DD}`（P1-requirements.md:72）及 YAML date 对象 `str()` 输出（agate-md-field-get `_format_value` 默认 str）兼容；字典序比较对日期型 cutoff 前缀等价成立 ✓
- **P2 §4.3.2 判定 3 字面**（P2-design.md:193）为「judge 为 dict 且 enabled falsy → exit 1」无条件执行——与实现不符，但 **P2-review NB-4**（P2-review.md:43）已明确记录该边界偏离并推荐「falsy 与缺失同走 created 判据」，P3 契约注解 1 将其固化为实现契约，test_check_gate.py L2795-2806/L2836-2847 按 NB-4 断言。实现从评审决策（非 P2 原文），偏离有完整决策痕迹且方向正确（防 pre-cutoff 任务显式 false 被误拦）。**不判 MISALIGNED**。
- `read_rules_yaml`（agate_common.py:637-646）读 `{rules_root}/dispatch.yaml`，缺失/解析失败 → None → cutoff None → fail-open（规则文件缺失时保守放行，R5 缓解）✓

#### 7. M15（P2 §4.5.2 + P3 契约注解 3）vs check-protocol-consistency.py

**文档声明**（P2-design.md:226）：`iter_md_files` 新增 opt-in 排除：env `AGATE_CONSISTENCY_SKIP_DIRS=<相对根路径列表>`（默认未设置 → 行为逐字节不变，R6）

**脚本实现**（check-protocol-consistency.py diff）：
- `_env_skip_dir_prefixes()`：`os.pathsep` 分隔、正斜杠归一（`replace(os.sep, "/")`）、call-time 读取、默认空 → `()` ✓
- `iter_md_files` 排除链末尾：`if any(rel_parts[: len(sp)] == sp for sp in skip_prefixes): continue`——与既有 rel_parts 排除链同层（相对 root 分量判定），分量级前缀匹配（`foo` 不误伤 `foobar.md`）✓
- 默认未设置 → 行为逐字节不变（实测既有一致性用例全绿）✓

### A2: 脚本→文档对齐

**结论**：ALIGNED

1. **judge 强制化文档面**（B 批）：
   - state-machine.md L442-446（diff）：judge.enabled 注释更新为「机制后新任务（P1 created ≥ judge_required_since "2026-08-22"）必须含 judge.enabled: true，check-gate P1 机械校验 exit 1；历史任务（created < 截止或未声明）缺块 → 跳过」——与 check-gate.py judge 块语义一致 ✓
   - dispatch.yaml L14-17：`judge_required_since: "2026-08-22"`（ISO 字符串）+ 注释声明判据——与脚本读取一致 ✓
   - dispatch.schema.json L19-22：`judge_required_since` string 属性——S-5 schema 校验通过（实测 S5-schema OK）✓
   - phase-cards/P1-requirements.md L58：产出规格 checklist 新增「judge: 启用声明」条；L82-84 frontmatter 样例注释（judge 写在 .state.yaml，非 P1 frontmatter）——与实现一致 ✓
2. **phases.yaml gates 命令串 ↔ 9 张卡 gate 规则节**：S-3b 实测验证（真实树 S-3 exit 0）；抽查 P2 卡 gate 规则节（P2-design.md 卡 L224-234）含 check-gate.py P2 / gate_commands.P3 / check-tdd-red.py 三 token，P5 卡（P5-verification.md:82-84）含 check-gate.py P5 ✓
3. **WORKFLOW.md / dispatch-protocol.md**：judge P6.5 描述（WORKFLOW.md:299/310「历史任务（.state.yaml 无 judge.enabled: true）→ P6.5 早退跳过」）与 RM-AG0039 兼容（机制后新任务有 judge 块则不早退，正是「P6.5 强制所有任务」的兑现）——无冲突引用 ✓
4. **scripts/README.md**：`agate-md-field-get.py` op 清单行（L119）未新增 status/agent/project_phase/created/code_map_*，但该行自声明「全集以脚本内 docstring 为准」，且 docstring（agate-md-field-get.py L44-50 区域）已更新新 op——按既有约定不构成漂移。**可选建议**：README 表格顺带补充新 op 名称，避免读者依赖 docstring 查全集。

### A3: 一致性连锁 + 反向传播

**结论**：ALIGNED

**A3a 连锁（已知衍生改动）**：
- agate_common 新增 14 个共享函数被 check-gate.py 消费，import 与降级 stub（check-gate.py diff L46-160 区域，ImportError 降级返回 0/False/空）成对存在，方向与 parse_gate_commands_block 降级先例一致 ✓
- `_TASK_FRONTMATTER_FIELDS`（S-4 已知词表）补 code_map_new_files_count/code_map_reviewed_count（check-structure-consistency.py:65-68）——status/agent/project_phase/created 原已在表内（L59-60），S-4 无误报（实测 S4-scripts OK）✓
- test_md_parse_scan.py 24 条判定模式清单（A1+B7+C15+D1）与迁移后实际状态逐条对上（实测全绿）✓

**A3b 反向传播（主动推断应被影响的文件）**：
| 应被影响文件 | 核查结论 |
|---|---|
| 其他读任务 md 脚本（check-pruning / check-p6-* / agate-risk-score / check-routing / ci-gate-backstop / agate-feedback） | 无 check-gate.py 内部符号依赖（`_frontmatter_field`/模块级正则均私有）；agate_common 既有函数（parse_gate_commands_block / read_vision_tri_state / count_p2_declared_fields 等）未删未改——**不受影响，无需同步** ✓ |
| task-files.md | P1 模板已含 `created: {YYYY-MM-DD}`（L14）、P7 模板已含 `code_map_new_files_count: 0`（L437）——字段本就存在，本次仅读机制变更——**无需同步** ✓ |
| 角色卡样例（analyst/architect/verifier.md） | 无 agate-md-field-get op 清单承载（grep 确认仅 protocol-alignment-review.md 的反向传播表提及字段集名）；status/agent/created/project_phase 为既有协议字段——**无需同步** ✓ |
| scripts/README.md | op 清单未加新 op（见 A2-4，docstring 权威约定，可选补充）——**可接受** |
| conftest helpers（add_frontmatter_field 系列） | 泛型实现（field:value 直写，无每字段清单），add_p1_field 直接复用——**无需同步** ✓ |
| WORKFLOW / dispatch-protocol / orchestrator-template（state-machine judge 模板变更传播） | grep 确认无「缺失/false = 历史任务」旧语义引用；P6.5 描述与新机制兼容——**无需同步** ✓ |
| WORKFLOW「Pre-commit 检查总览」 | 本次未新增/修改任何 pre-commit 触发行为（check-gate 判定口径不变）——**无需同步** ✓ |

### A4: 测试覆盖

**结论**：ALIGNED

**全量 pytest 实跑（A4 强制，本机权威 basetemp，仓库外）**：
```
$ cd worktree && timeout 900 python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp
1213 passed, 2 skipped in 129.86s (0:02:10)
[exit code: 0]
```
passed=**1213** / failed=**0**（2 skipped 为设计内 skip）。与 C 批自查（1210 passed/3 failed：2×judge P1 红 + 1×test_env_adapt_docs 注释自伤）逐项对账：B 批转绿 2 个 judge 用例、D 批修复注释自伤 1 个 → 1213 全绿，无新增回归。

**新逻辑覆盖**：
- 静态扫描（BDD-3）：test_md_parse_scan.py 24 模式命中=0 ✓
- S-3a/S-3b（BDD-5）：test_check_structure_consistency.py 三用例（单侧漂移×2 + 双侧一致）✓ + 真实树 S-3 exit 0 ✓
- judge P1（BDD-6/7）：test_check_gate.py 七用例全分支——机制后缺失 exit 1 / enabled-true 放行 exit 2 / disabled-after-cutoff exit 1（NB-4）/ pre-cutoff 无 judge exit 2 / 无 created fail-open exit 2 / disabled-pre-cutoff exit 2（NB-4）/ 非 dict fail-open exit 2 ✓
- M15（契约注解 3）：test_env_adapt_docs.py test_m15_injected_excluded + test_m15_default_unchanged ✓
- test_bdd_7 GIT_CEILING_DIRECTORIES（P2 §4.5.1）+ test_bdd_25 位置感知（契约注解 5）✓

**边界覆盖 note（非缺陷）**：契约注解 1「created 非 ISO → fail-open」分支未显式构造测试（缺失 created 用例 test_bdd_7_gate_p1_historical_no_created_fail_open_exit_2 覆盖同一条 fail-open 路径；非 ISO 由 `_is_iso_date` 返回 False 保证不拦）。实现正确，覆盖略欠一角，可选补一条 `add_p1_field(td, "created", "not-a-date")` 用例。

### A5: 下游影响 + 文档传播

**结论**：NEEDS_HUMAN_REVIEW

**下游影响（gate 行为）**：
- check-gate.py：判定口径不变（读取方式变，well-formed 等价——NB-3 边界已记录）——已有项目现有任务零行为变化 ✓
- judge 强制化（RM-AG0039）：**机制后新任务**（P1 created ≥ 2026-08-22）缺 judge.enabled: true → P1 gate exit 1——**破坏性变更**（对新任务）✓ 已标
- S-3a/S-3b 收紧（RM-AG0038）：已有项目若 phases.yaml gates 命令串与卡片 gate 规则节有漂移，check-structure-consistency 将新报 ERROR——**破坏性变更**（权威源切换）✓ 已标
- M15 排除钩子：默认关闭，行为逐字节不变（R6）✓
- ruff 锁版 0.16.4：CI 行为变化（版本固定），本地需 `~/.venvs/agate-dev/bin/ruff` 对齐 ✓

**文档传播缺口（NEEDS_HUMAN_REVIEW 项）**：
- UPGRADING.md v0.61.0 章节 ②③ 小节（diff L100-119）为**占位**，且文字声明「条目由 C-migration / B-judge 实现批在下方 ②③ 占位小节补充」——但 P2 §5 批表（P2-design.md:236-241）中 C 批文件集 = {check-gate.py, agate_common.py, agate-md-field-get.py, check-structure-consistency.py, phases.yaml, test_md_parse_scan.py}、B 批文件集 = {check-gate.py, dispatch.yaml, dispatch.schema.json, state-machine.md, P1 卡, test_check_gate.py}，**均不含 UPGRADING.md**（禁越界）——「由 B/C 批补充」的声明与批分工不符，实际未补全。
  - 协议语义本身无漂移（权威语义已在 state-machine.md L442-446 / dispatch.yaml / P1 卡完整声明；UPGRADING 为发布说明文档）。
  - AGENTS.md 版本发布流程 step 3 要求「更新 agate/UPGRADING.md 新增本版本章节（破坏性变更逐条列）」，P8 卡「主 Agent 必须亲自执行」——发布期义务存在，但「由 C/B 批补充」的**文字承诺无法兑现**，需主 Agent 裁决：
    1. 改 UPGRADING 占位措辞为「由 P8 主 Agent 补齐」；或
    2. 在 P8 前派发专门批次补齐 ②③ 完整条目（影响面/升级动作/对账兜底）。
  - 风险：若 P8 未显式跟踪，②③ 占位可能随版本发布流出。**建议在 P8 卡核对清单显式加入「UPGRADING ②③ 占位已补齐」项。**

- CHANGELOG 未更新：**正常**（版本发布在 P8）✓

### A6: 锚点表覆盖

**结论**：ALIGNED

- 本次无新增 gate 脚本（agate_common.py 为公共库、agate-md-field-get.py 为既有工具，均非 gate 脚本）——CHECK 9 反向兜底（check-protocol-consistency.py:787-818）无新增未锚脚本 ✓
- check-structure-consistency.py 已在锚点表（check-protocol-consistency.py:736-742，「协议结构一致性 S-1~S-6 双向 gate」）——S-3a/S-3b 是既有 S-1~S-6 的叠加子检查，关键词「S-1」「check-yaml-schema.py」仍命中（实测 CHECK 9 无 ERROR）✓
- check-gate.py 锚点不变（行为未变）✓
- 实测 `check-protocol-consistency.py --strict-errors-only` → 0 ERROR（321 既有 WARNING）exit 0 ✓

### A7: 设计原则一致性

**结论**：ALIGNED

| ADR | 与本变更关系 | 判定 |
|---|---|---|
| ADR-007（机器字段并入 frontmatter，单工具双读，agate/adr.md:195-222） | A 组迁移方向一致：status/agent/project_phase/created/code_map_* 统一经 agate-md-field-get 单工具读取（NO_FALLBACK 无正文回退，frontmatter-only 语义与 ADR-007「结构化读取」方向一致）| ALIGNED |
| ADR-002（可判定性——gate 门槛机器可判定，agate/adr.md:41-67） | judge 强制化 = fail-closed 机器判定（exit 1，不依赖主 Agent 自觉）；S-3a/S-3b = 机器可判定双向 gate——均符合「门槛机器可判定」原则 | ALIGNED |
| ADR-001（隔离性——主 Agent 不写产出） | 本次为协议本体维护（gate 脚本/规则权威源），评审角色独立审查——不冲突 | ALIGNED |

- 共享读取器架构（agate_common M2-0038 节）是 TAG0021/RM-AG0022 结构化层的延续（parse_gate_commands_block 既有先例，agate_common.py:805-810 注释），非新架构决策；P2-review 锁定决策 3 已记录——**无需新增 ADR**。
- 未发现未记录的架构决策。A7 两态结论：ALIGNED。

## 闭环备注

[HUMAN_CONFIRMED: 2026-08-23 确认——A5 UPGRADING v0.61.0 ②③ 占位小节：采纳方案 2（P8 前补齐的等价路径 = P8 版本发布阶段补齐）。理由：① AGENTS.md 版本发布清单 step 3 强制「更新 agate/UPGRADING.md 新增本版本章节（破坏性变更逐条列）」，P8 卡「主 Agent 必须亲自执行」——②③ 的完整条目（RM-AG0038 权威源切换 / RM-AG0039 judge 强制化的影响面、升级动作、对账兜底）本就在 P8 发布义务内；② 版本号（v0.61.0）与发布说明内容在 P8 才最终定稿，占位小节在 P8 重写整章时自然消解；③ P2 §5 批表文件集不含 UPGRADING.md 是「禁越界」正确约束，A 批写入占位是为 P8 预留位置，非遗漏。跟踪：P8 核对清单显式加入「UPGRADING ②③ 占位已补齐（RM-AG0038/0039 破坏性变更逐条列）」项，由主 Agent 亲自执行并验证；本 HUMAN_CONFIRMED 标记 + 审查报告随仓库入库，P8 引用。]

- 本报告 0 项 MISALIGNED，1 项 NEEDS_HUMAN_REVIEW（A5 UPGRADING 占位），需主 Agent 裁决后附 `[HUMAN_CONFIRMED: 日期 确认：理由]` 方可 commit。
- 2 条 DESIGN_GAP（P4-implementation.md）经原则 6 核查：任务尚在 P4（无 P7 REVIEWED-ACCEPTED），但裁决理由经独立核实成立（P5 去 token 保语义 + S-3 双侧一致实测；S-3a/b token 粒度与 P3 三用例 + 真实树验证吻合），按「主 Agent 已采纳 + 理由成立」记为 ALIGNED + KNOWN_DEVIATION 标注，不计入需修复项。
- P2 §4.3.2 判定 3 字面（falsy 无条件 exit 1）与实现（falsy 同走 created）差异：P2-review NB-4 已记录并推荐，实现从评审决策——不判 MISALIGNED。
