---
phase: P4
task_id: TAG0022-confirmed-problems
type: implementation
parent: P3-test-cases.md
trace_id: TAG0022-P4-20260822
status: draft
created: 2026-08-22
agent: implementer
---

# P4 实现 — batch A-ruff（RM-AG0037，ruff 合并强制）

> 状态标记：[PROD_NOT_TOUCHED]（仅改 worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0022/`；稳定版 `~/.agate` 与主 checkout 未动）
> 派发指令：P4-dispatch-context-implementer-batchA-ruff.md（强制）；本批文件集 = 3 文件（workflow + UPGRADING + 根 AGENTS.md），禁越界。
> 上游：P2-design.md（§1.1 M1/M10、§4.1、§5 批表、§7）+ P1-requirements.md（BDD-1/2、D1）+ P0-brief.md（env_constraints）。

## implementation_dir

`implementation_dir: /home/kity/oclab/agate/.worktrees/agate-TAG0022/`

> 本批**无新增代码文件**——改动全部落在既有跟踪文件上（`.github/workflows/protocol-tests.yml`、`agate/UPGRADING.md`、根 `AGENTS.md`），implementation_dir 指向 worktree 根以声明改动实际落点。

## 新增文件核对表

> 项目已采用 CODE-MAP（`agate-workspace/agents/CODE-MAP.md` 存在）；P2-skeleton.md 不存在，骨架归属列不适用。
> 本批**无新增文件**（仅修改 3 个既有文件）——CODE-MAP 处理按无新增文件豁免。

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| （本批无新增文件；修改：`.github/workflows/protocol-tests.yml` / `agate/UPGRADING.md` / 根 `AGENTS.md`） | within 仓库根既有目录（无骨架声明） | [CODE_MAP_EXEMPT: 本批为既有文件修改（CI + 文档），无新增文件需登记，agents/CODE-MAP.md 无需更新] |

## 改动摘要

### 1. `.github/workflows/protocol-tests.yml`（ruff job，L106-116）

- `pip install ruff` → `pip install ruff==0.16.4`——与本地开发环境 `~/.venvs/agate-dev/bin/ruff` 对齐（P2-design §1.1 M1 / §4.1 的 BDD-2 对齐语义实体化）；新增行内注释记录锁定理由。
- job name `ruff` **保持稳定未改名**（job 层 `name: ruff` 不变），可被 GitHub 分支保护按 check 名引用（BDD-1）。
- 保守原则：仅锁版本 + job 名固化，未引入其他 CI 改动（dispatch 约束 3）。

### 2. `agate/UPGRADING.md`（新增 `### v0.61.0` 章节，插于 v0.60.0 节之前）

- **① RM-AG0037**：CI ruff job 可被 PR required check 引用——配置步骤（维护者执行，D1 实现/配置边界）：GitHub Settings → Branches → 分支保护规则 → 勾选 ruff check（"Require status checks to pass before merging"）；背景（TAG0019/20 带 23/12 处违规合并、事后 PR #183 补修教训）；升级动作 = 无（纯 CI 配置 + 文档）。
- **② RM-AG0038 权威源切换：占位小节**——标明由 C-migration 批（batch C）补充完整条目（影响面/升级动作/对账兜底）。
- **③ RM-AG0039 judge 强制化：占位小节**——标明由 B-judge 批（batch B）补充完整条目（判据/历史跳过语义/升级动作）。
- 通用升级动作句 + 「本版本含破坏性变更」提示（格式对齐 v0.60.0 节：①/②/③ 加粗编号 + 步骤列表）。

### 3. 根 `AGENTS.md`（「版本发布」清单区）

- step 5（CHECK 7）之后补一句：**CI ruff job（RM-AG0037 required check）验证**——合并前确认分支保护已将 `ruff` 勾选为 PR required check，或在第 5 步后验证 CI ruff job 绿（ruff==0.16.4 锁版本，与本地 `~/.venvs/agate-dev/bin/ruff` 对齐），防带 ruff 违规合并复发（TAG0019/20 教训）。

## 自查结果

| 项 | 方法 | 结果 |
|----|------|------|
| workflow YAML 语法 | python3 + yaml.safe_load 解析 `.github/workflows/protocol-tests.yml` | **PASS**：解析成功；jobs 含 `ruff`；job name 字段 = `ruff`；run 命令 = `pip install ruff==0.16.4 && ruff check agate/` |
| UPGRADING 章节文本 | grep `v0.61.0` / `required check` / `分支保护` / `勾选 ruff` / `占位小节` | **PASS**：v0.61.0 节位于 L92；required check 配置步骤（L97-108）与 ②③ 占位小节（L111-120）齐全 |
| AGENTS.md 文案存在 | grep `RM-AG0037 required check` / `ruff==0.16.4` | **PASS**：step 5 新句位于 L157 |
| diff 可见 | `git status --short` + `git diff`（worktree 内） | **PASS**：3 文件 M 状态；diff 逐行核对（workflow +3/-1、AGENTS.md +1、UPGRADING.md +34） |

- 未跑全量测试：本批无 P3 红测试关联（仅 CI 配置 + 文档改动），按派发约束 6 不跑，验证归 P5。
- 自查 ≠ gate：不声称「P5 已过」；无 [DESIGN_GAP] / [CLARIFY] / [SCOPE+]（改动均在派发上下文与 P2 设计 §1.1 M1/M10、§4.1 范围内）。

## 触发面清单（SELF-GATE）

| 触发面 | 文件 | 判定 |
|--------|------|------|
| agate 协议 md（`agate/*.md`） | `agate/UPGRADING.md` | 触发（dispatch 约束 5） |
| 仓库根文档 | 根 `AGENTS.md` | 触发（dispatch 约束 5） |
| CI 配置（P0-brief known_risks / P2 §1.3 R7） | `.github/workflows/protocol-tests.yml` | 触发面（CI 配置改动；合并后需验证 CI 行为，P2 R7 缓解） |

> commit message 的 self-gate 声明（`self-gate-review:` 路径 / `self-gate-skip:` 理由）由主 Agent 处理——本 implementer 不执行 commit（dispatch 约束 5 / P4 卡 step 5-6 归主 Agent）。

## 门槛对照（dispatch「什么算完成」）

- [x] 三个文件改动落盘且 diff 可见（grep / git diff 确认）
- [x] workflow YAML 语法有效（yaml.safe_load 通过）
- [x] UPGRADING 章节含 required check 配置步骤文本
- [x] P4-implementation.md 存在且含 implementation_dir + 新增文件核对表 + 触发面清单
- [x] 本批禁改范围（check-gate.py / agate_common.py / rules/*.yaml / state-machine / P1 卡 / 测试文件）未触碰
---

# P4 实现 — batch D-env-tests（RM-AG0041 环境假象测试根治）

> 任务级 Header（phase: P4 / task_id: TAG0022-confirmed-problems / type: implementation / parent: P3-test-cases.md / trace_id: TAG0022-P4-20260822 / status: draft / created: 2026-08-22 / agent: implementer）见本文件顶部——本批为并行批（P2 §5 Wave1 = {A, C, D}），共享任务级 P4-implementation.md，追加本批记录。
> 状态标记：`[PROD_TOUCHED]`（改动了 `agate/scripts/check-protocol-consistency.py` 产品脚本；~/.agate 稳定版与主 checkout 未动）。
> 派发指令：P4-dispatch-context-implementer-batchD-env-tests.md（强制）；本批文件集 = check-protocol-consistency.py（M15 排除钩子）+ test_env_adapt_docs.py（复核）+ test_check_routing.py（复核），禁越界。

## implementation_dir

```
implementation_dir: /home/kity/oclab/agate/.worktrees/agate-TAG0022/agate/scripts/
```

本批**无新增代码文件**——仅修改既有产品脚本 `agate/scripts/check-protocol-consistency.py`；测试文件为 P3 批产出（commit f256d2c），本批只复核（零改动）。

## 新增文件核对表

> CODE-MAP 机制已采用（`agate-workspace/agents/CODE-MAP.md` 存在）；P2-skeleton.md 不存在，骨架归属列不适用。

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| （本批无新增文件；修改：`agate/scripts/check-protocol-consistency.py`） | within 既有 `agate/scripts/` 目录 | [CODE_MAP_EXEMPT: 本批只改既有文件，无新增文件需登记，agents/CODE-MAP.md 无需更新] |

## 改动摘要

| 文件 | 改动 | 归属 |
|------|------|------|
| `agate/scripts/check-protocol-consistency.py` | `iter_md_files` 新增 opt-in 排除钩子 M15：`_env_skip_dir_prefixes()` + 排除分支（+22 行） | RM-AG0041 / BDD-9（[SCOPE+] M15） |
| `agate/tests/unit/test_env_adapt_docs.py` | 复核 test_bdd_25（位置感知）与 test_m15_* 单测——与 P3 §5 契约注解 3/5 一致，**零改动** | 复核 |
| `agate/tests/unit/test_check_routing.py` | 复核 test_bdd_7（_run_routing env 透传 + GIT_CEILING_DIRECTORIES）——两位置绿，**零改动** | 复核 |

### M15 实现点（check-protocol-consistency.py）

- 新增 `_env_skip_dir_prefixes()`：解析 env `AGATE_CONSISTENCY_SKIP_DIRS=<相对根路径列表>` → 分量前缀元组。
  - **分隔符 `os.pathsep`**（POSIX `:` / Windows `;`），沿用仓库既有 `os.environ.get("AGATE_*", 默认)` 解析惯例。
  - **正斜杠归一**：`entry.strip().replace(os.sep, "/")` 后按 `/` 切分量（对齐既有 `rel()` 的 Windows 反斜杠归一）。
  - **call-time 读取**：`iter_md_files` 每次调用时读 env（测试对 import-time / call-time 两种实现均稳健，P3 §5 契约注解 3）。
  - **默认未设置 / 空值 → `()`**：行为与改动前逐字节不变（R6）。
- `iter_md_files` 排除链末尾追加：`if any(rel_parts[: len(sp)] == sp for sp in skip_prefixes): continue`
  - **与既有 rel_parts 排除链同层**：均相对 root 分量判定（绝对路径判定在 worktree 场景会误排除含 `.worktrees/` 的路径）。
  - **分量级前缀匹配**：避免 `foo` 误伤 `foobar.md`；多级路径（`agate-workspace/.pytest-tmp`）整段命中。
- **未动**：main() root 强制（L1117-1120）/ CHECK 2 REF_RE / iter_md_files 其他逻辑（最小改动约束 3）。

### test_bdd_7 复核结论

P3 已按 NB-5 改造（_run_routing 增 env 透传 + test_bdd_7 注入 GIT_CEILING_DIRECTORIES=<tmp_path>）；本批未改动 test_check_routing.py。两位置自跑 `test_bdd_7_thin_score_anomaly_git_ok_false_exit_1` 均绿——git 核心机制在任意 basetemp 位置确定性制造 `git_ok:false` → exit 1（P2 §4.5.1 定案）。**确认无需改动。**

### test_env_adapt_docs.py 校准结论

test_bdd_25 与 test_m15_* 与契约注解 3/5 逐条一致（位置感知 `relative_to` + `as_posix`、env 经 run_cli 注入、monkeypatch 唯一模块名加载），**与契约一致，无需微调**。

## 自查结果（自查≠P5 gate）

### 位置 1：仓库外 basetemp（权威 /home/kity/oclab/dsh-workspace/ptmp）

```
python3 -m pytest test_env_adapt_docs.py test_check_routing.py test_check_protocol_consistency.py regression/test_v040_dotarchived_exclusion.py -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp
→ 56 passed
```

红转绿：`test_m15_iter_md_files_skip_dirs_injected_excluded`（P3 红：skip-dir/c.md 仍产出 → 现被排除）+ test_bdd_25 仓库外分支；既有一致性用例与 iter_md_files 回归（dotarchived 2 个）零回归。

### 位置 2：仓库内 basetemp（worktree 内临时 basetemp 模拟，测后已清理）

```
python3 -m pytest test_env_adapt_docs.py test_check_routing.py -q -p no:cacheprovider -p ptpollute --basetemp=<worktree>/agate-tmp-bt-sim/bt_run
→ 27 passed
```

`ptpollute.py` 插件（dsh-workspace 临时验证资源）在测试执行阶段向 basetemp 注入 `polluted/bad-ref.md`（`docs/does-not-exist.md` 坏引用，TAG0020 条目 2 同型；pytest 9 首个 tmp fixture 使用时 rm_rf basetemp 根，故污染须在首个测试 call 阶段写入）。basetemp ∈ 仓库根 → test_bdd_25 走注入分支（env `AGATE_CONSISTENCY_SKIP_DIRS=<bt_run 相对根 rel>`）→ iter_md_files 排除污染 → **0 ERROR**（P3 现状该位置红：M15 未实现 → env 无效果 → ERROR=1）。绿即证明注入分支 + 排除链真实生效。测后 `rm -rf agate-tmp-bt-sim`（已确认不存在）。

### CLI 级机制模拟（污染 → 排除，独立实证）

worktree 根下建 `agate-tmp-bt-sim/polluted/bad-ref.md`（坏引用）：无 env 跑 worktree 自己 `check-protocol-consistency.py --root <worktree根> --strict-errors-only` → **rc=1（CHECK 2 ERROR）**；env `AGATE_CONSISTENCY_SKIP_DIRS=agate-tmp-bt-sim` → **rc=0（0 ERROR）**。测后清理。

### 平台无关 + 静态卫生

- `check-platform-assumptions.py` 对修改后 check-protocol-consistency.py → **rc=0，无 R1-R5 命中**（无裸 PATH= / 裸 python3 / symlink 硬假设 / /tmp 字面）。
- `~/.venvs/agate-dev/bin/ruff check agate/scripts/check-protocol-consistency.py` → **All checks passed**（初版 PLW2901 循环变量覆写已修复）。
- env 注入均经 conftest run_cli env 参数；rel 路径经 `Path.relative_to` + `as_posix` 归一。

## 触发面清单（SELF-GATE）

| 触发面 | 文件 | 判定 |
|--------|------|------|
| `agate/scripts/*.py` | `agate/scripts/check-protocol-consistency.py` | 触发（SELF-GATE.md）——commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（主 Agent 落实） |

## 门槛对照（dispatch「什么算完成」）

- [x] M15 排除钩子实现落盘（env 读取 + 排除分支 + 默认不变）
- [x] P3 红测试转绿：test_m15_iter_md_files_skip_dirs_injected_excluded + test_bdd_25（两位置口径）
- [x] 目标测试文件既有用例零回归（4 文件 56 用例全绿）
- [x] 平台无关扫描对修改点无 R1-R5 命中
- [x] P4-implementation.md 含实施摘要 + 两位置验证结果
- [x] 本批禁改范围（check-gate.py / agate_common.py / rules/*.yaml / state-machine / P1 卡）未触碰

## 临时资源清单（供主 Agent P8 READY 收尾核对）

- `/home/kity/oclab/dsh-workspace/ptpollute.py`：pytest 污染注入插件（工作区外，验证用，可删）。
- `/home/kity/oclab/dsh-workspace/cli-noenv.out` / `cli-env.out`：CLI 机制模拟输出（可删）。
- worktree 内临时 basetemp `agate-tmp-bt-sim`：**已清理**。

---

# P4 实现 — batch C-migration（RM-AG0038，M2 迁移闭环，最大体量批）

> 任务级 Header（phase: P4 / task_id: TAG0022-confirmed-problems / type: implementation / parent: P3-test-cases.md / trace_id: TAG0022-P4-20260822 / status: draft / created: 2026-08-22 / agent: implementer）见本文件顶部——本批为并行批（P2 §5 Wave1 = {A, C, D}），共享任务级 P4-implementation.md，追加本批记录。
> 状态标记：`[PROD_TOUCHED]`（改动了 5 个产品脚本/规则文件 + 1 个测试校准；~/.agate 稳定版与主 checkout 未动）。
> 派发指令：P4-dispatch-context-implementer-batchC-migration.md（强制）；本批文件集 = 6 文件（check-gate.py / agate_common.py / agate-md-field-get.py / check-structure-consistency.py / rules/phases.yaml / tests/unit/test_md_parse_scan.py），禁越界——phase-cards/ 等不在本批文件集，未触碰。

## implementation_dir

```
implementation_dir: /home/kity/oclab/agate/.worktrees/agate-TAG0022/agate/
```

本批**无新增代码文件**——改动全部落在既有文件（5 产品 + 1 P3 落盘测试校准）。test_md_parse_scan.py 为 P3 新增（commit 已含），本批仅校准一行平台卫生注释（见迁移摘要 §5）。

## 新增文件核对表

> CODE-MAP 机制已采用（`agate-workspace/agents/CODE-MAP.md` 存在）；P2-skeleton.md 不存在，骨架归属列不适用。

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| `agate/tests/unit/test_md_parse_scan.py`（P3 新增，本批校准，非本批新增文件） | within `agate/tests/unit/`（无骨架声明） | [CODE_MAP_EXEMPT: P3 已落盘并 commit（P3 批新增），本批仅校准一行注释；agents/CODE-MAP.md 不在 C 批文件集（禁越界），P3/主 Agent 尚未登记，登记由主 Agent 统一处理] |
| （本批其余 5 文件均为既有文件修改：check-gate.py / agate_common.py / agate-md-field-get.py / check-structure-consistency.py / rules/phases.yaml） | within 既有目录 | [CODE_MAP_EXEMPT: 本批只改既有文件，无新增文件需登记] |

## 迁移摘要（逐组 A/B/C/D + S-3）

### A 组：frontmatter 字段读取 → agate-md-field-get 新 op（`_frontmatter_field` 全删）

- `agate-md-field-get.py`：`NO_FALLBACK_STRING_FIELDS` 注册 **status / agent / project_phase / created**（frontmatter-only，无正文回退）；`NO_FALLBACK_INT_FIELDS` 注册 **code_map_new_files_count / code_map_reviewed_count**——解 check-gate.py L1098-1107 DESIGN_GAP 遗留（此前 KNOWN_OPS 未注册 → `_md_field_get` unknown op exit 2 恒回退空串 → 两层 CODE_MAP 校验整段跳过）。
- `check-gate.py`：删除 `_frontmatter_field` 定义（sed 式行扫描）；**9 处调用全迁** `_md_field_get`：P1-review status/agent（gate_p1）、P2-review status/agent + P1 project_phase（gate_p2）、**P4-review status/agent（NB-6：L799/805 读点，勿漏）**（gate_p4）、P7 code_map_*（gate_p7）。L1098-1107 DESIGN_GAP 注释移除（已解决）。
- `_frontmatter_lines` 保留——仅剩 gate_p1 的 need_confirm_resolved/suggest_resolved 行首键存在性检查使用（不在 A 组迁移面）。
- 行为等价：新 op 为 frontmatter-only（`_frontmatter_field` 本就只扫 frontmatter 块）；well-formed frontmatter 下逐字节等价；畸形/带引号 frontmatter 差向更正确（NB-3 口径，不外扩）。

### B 组：P1 行首标记 → agate_common count_markers/has_marker/extract_marker_desc

- `agate_common.py`：新增 M2-0038 节——`_NC_RE/_SUGGEST_RE/_NO_NEED_RE/_NC_DESC_RE/_SUGGEST_DESC_RE/_SUGGEST_TAIL_BT_RE/_SUGGEST_TAIL_BRACKET_RE`（逐字节同正则）+ `count_markers(text, kind)` + `has_marker(line, kind)` + `extract_marker_desc(line, kind)`（NC 单段剥离 / SUGGEST 三连剥离，含 RM-AG0001 可选反引号前缀语义）。
- `check-gate.py`：模块级 7 正则删除（BDD-3 字面清零）；gate_p1 计数/描述提取改走共享函数（nc_blocking/nc_suggest/nc_unresolved 逐条匹配/nc_suggest_unacked/NO_NEED 存在性），判定口径（退出码）不变。

### C 组：任务产出格式判定 → agate_common 共享读取器

- `agate_common.py` 新增：`extract_bdd_titles`（P1 UI 维度 BDD 标题）/ `parse_ui_design_section`（P2 UI 节标题+形态/维度声明）/ `candidate_count_value`（P2 候选数）/ `design_trivial_declared`（P1 简化声明）/ `has_keyword`（tradeoff/choice_and_reason/design_gap 三 kind）/ `count_p6_pass_fail`（P6 旧格式计数）/ `count_p7_markers`（P7 BLOCKER/DEVIATION，含汇总行排除）/ `count_design_gap`（P7 blockquote 口径 + P4 转抄口径两参）/ `count_code_map_lines`（P4 CODE_MAP 标记）/ `parse_fail_list_block`（P5 pre-task-baseline ```fail-list 块）/ `count_kf_entries`（known-failures 表）。
- `check-gate.py` 对应消费点全部改走共享函数（P1/P2/P5/P6/P7 分支），P0/P3/P4/P8 判定逻辑未动（N5）。

### D 组：内嵌 yaml 块 → agate_common extract_embedded_yaml_blocks

- `agate_common.py`：`extract_embedded_yaml_blocks(text)`（同正则单点；read_vision_tri_state 既有实现同源）。
- `check-gate.py`：`_gate_p1_vision_capability` 兜底循环改走共享函数（E/F 组 .state.yaml/git/CHANGELOG 解析未动，D2 口径）。

### S-3 收紧（check-structure-consistency.py + phases.yaml，BDD-5）

- `check-structure-consistency.py`：
  - `_TASK_FRONTMATTER_FIELDS` 补 **code_map_new_files_count / code_map_reviewed_count**（S-4 已知字段表同步，防 S-4 误报；status/agent/project_phase/created 原已在表内）。
  - 新增 `_MACHINE_GATE_REF_RE`（`check-gate.py P{n}` / `gate_commands.P{n}` / `check-*.py` 三模式）+ `_machine_gate_refs` / `_yaml_gate_cmd_refs` / `_gate_rules_block`（`## gate 规则` 节，S-3a 缺卡节时回退 `## 推进条件`；节止于下一个 `## ` 标题，卡内 `# 注释` 行不算边界）/ `_block_since`。
  - `_check_s3` 逐阶段**叠加** S-3a（YAML→md：gates[].check 机器命令串须在卡片 gate 节出现）+ S-3b（md→YAML：卡片 gate 节机器命令行须在 gates[].check 声明）——NB-1 叠加不重定义既有 S-3 outputs/orphan/exec_role；NB-2 P6.5 无独立卡片 → `_phase_card_path` 返回 None → 天然跳过（test_check_structure_consistency 既有「产出规格缺失 P2-review.md → 非 0」用例保持绿）。
- `agate/rules/phases.yaml`：各阶段 gates[].check 增补实际 gate 命令串，与 9 张卡 `## gate 规则` 节逐一核对（S-3b md 侧锚）：
  - P1/P2/P4/P5/P7 → `check-gate.py P{n} $TASK_DIR`；P3 → + `check-tdd-red.py $TASK_DIR exit 0` + `gate_commands.P3 声明测试运行器`；P6 → + `check-p6-format.py --fix` + `check-gate.py P6.5 $TASK_DIR`（= check-judge-verdict.py + check-events.py）；P6.5 → + `check-gate.py P6.5 $TASK_DIR`；P8 → + `check-p6-provenance.py --audit7-only` + `gate_commands.P5 逐包 exit 0` + `check-protocol-consistency.py 先 tag 后重跑（DEBT0013）`；P0 卡无 `## gate 规则`/`## 推进条件` 命令串 token，保持不动。
- **P5 数据点修正（S-3a 真实树第一跑拦截）**：原 P5 散文 check `gate_commands.P5 exit 0 AND failed==0` 含机器 token `gate_commands.P5`，但 P5 卡 `## gate 规则` 节只有 `check-gate.py P5` → S-3a 报 ERROR。改散文为 `P2 声明的验证命令全部 exit 0 AND failed==0`（去 token）对齐卡片——R4 的「卡片确实缺命令串时补卡片」路径本批不可达（phase-cards/ 不在 C 批文件集，禁越界）。

### test_md_parse_scan.py 校准

24 条判定模式清单与迁移后实际状态逐条对上（A 1 + B 7 + C 15 + D 1），**无需增删模式**——红转绿来自实现（命中 43 → 0），非测试放宽。仅校准一行文件头注释：`无裸 python3 / 无 /tmp 字面` → `无裸解释器字面量 / 无临时目录字面量`（平台卫生——原措辞自伤 check-platform-assumptions R2/R4 扫描，对齐 test_check_structure_consistency.py 同款安全措辞）。

## 自查结果（自查≠P5 gate）

| 项 | 方法 | 结果 |
|----|------|------|
| 静态扫描（BDD-3） | `pytest test_md_parse_scan.py` | **PASS**：命中 43 → **0**（红转绿，24 条模式全清零） |
| S-3a/S-3b 漂移用例（BDD-5） | `pytest test_check_structure_consistency.py` | **PASS**：2 红转绿 + 11 既有全绿（13 passed；既有「产出规格缺失」「S-4 登记」「S-6 引用」等用例零回归） |
| check-gate 全量（含 gate_p65 judge 五用例） | `pytest test_check_gate.py` | **PASS**：170 绿零回归（仅 B 批 2 个新增 judge P1 用例保持红——B-judge 批范围） |
| 真实树结构一致性 | `AGATE_ROOT=<worktree>/agate python3 check-structure-consistency.py` | **PASS**：S1-S6+S0 全 OK，exit 0 |
| 协议一致性（worktree 自己） | `python3 check-protocol-consistency.py --strict-errors-only`（AGATE_ROOT=worktree） | **PASS**：0 ERROR（321 既有 WARNING，rc=0） |
| 全量 pytest（仓库外 basetemp=ptmp） | `pytest agate/tests/ -q -p no:cacheprovider --basetemp=...ptmp` | **1210 passed / 2 skipped / 3 failed**——failed 明细：① 2× judge P1（B 批范围，P3 红→ 待 B-judge 批转绿）；② 1× `test_bdd_8_clean_tree_zero_detection`（test_env_adapt_docs.py:172 注释含「无 /tmp 字面」短语自伤 R4 扫描——该文件属 D 批、禁越界，非 C 批回归；C 批已清自身文件（test_md_parse_scan.py）的同类自伤，残余 1 处需 D 批（或主 Agent 定向）改一行注释为「临时目录字面量」即复绿） |
| md-field-get/common/structure 单测 | `pytest test_agate_md_field_get.py test_agate_common.py test_check_structure_consistency.py` | **PASS**：49 passed |
| 新 op 直测 | FILE=... agate-md-field-get.py status/agent/project_phase/created/code_map_* | **PASS**：frontmatter 取数正确；无 frontmatter 正文同名 → 空串（frontmatter-only 语义） |
| 共享读取器冒烟 | python3 直调 count_markers/extract_marker_desc/count_p6_pass_fail/count_p7_markers/count_design_gap/parse_fail_list_block 等 | **PASS**：输出与旧内联语义一致（AST 解析 + 行为抽查） |
| ruff（4 改动脚本） | `~/.venvs/agate-dev/bin/ruff check` | **PASS**：All checks passed（修 W605 docstring 转义 ×2 + C401 set 推导） |
| count-tests | `bash agate/tests/scripts/count-tests.sh` | **PASS**：1215 ≥ 1202 基线（只增不减） |

## 触发面清单（SELF-GATE）

| 触发面 | 文件 | 判定 |
|--------|------|------|
| `agate/scripts/*.py` | `agate/scripts/check-gate.py` / `agate_common.py` / `agate-md-field-get.py` / `check-structure-consistency.py` | 触发（SELF-GATE.md）——commit message 需含 `self-gate-review:` / `self-gate-skip:`（主 Agent 落实；建议对 check-gate.py 做一次 protocol-alignment-review，P2 §9 已安排在 C 批后） |
| `agate/**/*.md` / rules YAML | `agate/rules/phases.yaml` | 触发（规则权威源数据面） |
| 测试文件 | `agate/tests/unit/test_md_parse_scan.py`（校准注释） | 不触发 SELF-GATE（测试文件非协议本体；commit 纪律照常） |

## 门槛对照（dispatch「什么算完成」）

- [x] 6 文件改动落盘（check-gate.py / agate_common.py / agate-md-field-get.py / check-structure-consistency.py / rules/phases.yaml / test_md_parse_scan.py）
- [x] P3 红测试转绿：test_md_parse_scan（静态扫描命中=0）+ S-3a/S-3b 漂移用例（2 转绿）
- [x] 目标测试文件既有用例零回归：gate_p65 judge 五用例保绿；S-* 既有用例保绿；check-gate 170 用例零回归
- [x] check-structure-consistency.py 0 ERROR（真实树）
- [x] check-protocol-consistency.py --strict-errors-only 0 ERROR（worktree 自己的）
- [x] count-tests ≥ 1202（实测 1215）
- [x] agate_common 共享读取器（count_markers 族 + C/D 组 11 个读取器）与 agate-md-field-get 新 op（status/agent/project_phase/created/code_map_*）就位
- [x] P4-implementation.md 存在且含实施摘要 + 自查结果（本批段）

## 批界声明

- judge P1 校验（2 个红用例）与 gate_p1 judge 块 = **B-judge 批**范围（0039），本批不碰 judge 逻辑（dispatch 约束 3）——gate_p65 及 judge 相关代码逐字节未动。
- dispatch.yaml / state-machine.md / P1 卡 / phase-cards / test_check_gate.py / test_env_adapt_docs.py 等 = B/D/其他批文件，**零改动**。

## 自主决策声明（implementer.md 强制上报）

[DESIGN_GAP: P2 §4.2.2 例「P5→gate_commands.P5」在真实树上不可达——P5 卡 `## gate 规则` 节无 gate_commands.P5 token，而 S-3a 要求 YAML 命令串须在卡节出现；R4 的"补卡片"路径因 phase-cards/ 不在 C 批文件集（禁越界）不可执行。实现取 S-3a/S-3b 双侧一致约束为硬锚：P5 gates 散文改「P2 声明的验证命令全部 exit 0 AND failed==0」（去 token）+ 增补 check-gate.py P5 $TASK_DIR，与卡片对齐后真实树 S-3 exit 0。]

[DESIGN_GAP: P2 §4.2.2 未指定 S-3a/S-3b 的匹配粒度。实现定案：机器可判定命令按 **token 提取**（`check-gate.py P{n}` / `gate_commands.P{n}` / `check-*.py`）做子串包含判定（非整串/整行比对）；S-3a 扫描卡片 gate 规则节（缺节回退推进条件），S-3b 仅扫描 gate 规则节（推进条件不纳入）。P3 三用例（s3a/s3b/双侧一致）对该口径全绿，真实树 10 阶段 0 ERROR。]

---

# P4 实现 — batch B-judge（RM-AG0039，judge 启用强制化）

> 任务级 Header（phase: P4 / task_id: TAG0022-confirmed-problems / type: implementation / parent: P3-test-cases.md / trace_id: TAG0022-P4-20260822 / status: draft / created: 2026-08-22 / agent: implementer）见本文件顶部——本批为 B-judge 批（P2 §5 并行批族），共享任务级 P4-implementation.md，追加本批记录。
> 状态标记：`[PROD_TOUCHED]`（改动了 `agate/scripts/check-gate.py` 产品脚本 + `agate/rules/` 规则权威源数据面 + 2 协议文档；~/.agate 稳定版与主 checkout 未动）。
> 派发指令：P4-dispatch-context-implementer-batchB-judge.md（强制）；本批文件集 = 5 文件（check-gate.py / rules/dispatch.yaml / rules/schema/dispatch.schema.json / state-machine.md / phase-cards/P1-requirements.md），禁越界——test_check_gate.py 的 judge P1 用例由 P3 批落盘（commit f256d2c），本批仅使红转绿、未改测试文件。
> 上游：P2-design.md（§4.3 + §1.1 M7-M9 + §4.2.1 created op 行）+ P2-review.md（锁定决策 2/5 + NB-4 + TG-2）+ P3-test-cases.md（§5 契约注解 1）；时序：叠加于 C-migration 批（agate-md-field-get `created` op + `read_rules_yaml` 规则读取路径）之后。

## implementation_dir

```
implementation_dir: /home/kity/oclab/agate/.worktrees/agate-TAG0022/agate/scripts/ + agate/rules/ + agate/state-machine.md + agate/phase-cards/（协议本体）
```

本批**无新增代码文件**——改动落在产品脚本（check-gate.py）、规则权威源数据面（dispatch.yaml + dispatch.schema.json）、协议文档面（state-machine.md + P1 卡）四处既有文件上。

## 新增文件核对表

> CODE-MAP 机制已采用（`agate-workspace/agents/CODE-MAP.md` 存在）；P2-skeleton.md 不存在，骨架归属列不适用。

| 新增文件路径 | 骨架归属 | CODE-MAP 处理 |
|------------|---------|--------------|
| （本批无新增文件；修改：check-gate.py / dispatch.yaml / dispatch.schema.json / state-machine.md / phase-cards/P1-requirements.md） | within 既有目录（无骨架声明） | [CODE_MAP_EXEMPT: 本批只改既有文件，无新增文件需登记；test_check_gate.py 的 judge P1 用例为 P3 批增量（commit f256d2c），本批红转绿未改测试文件，agents/CODE-MAP.md 无需更新] |

## 改动摘要

| 文件 | 改动 | 归属 |
|------|------|------|
| `agate/scripts/check-gate.py` | gate_p1 新增 judge 校验块（L647-664，纯叠加于 C 批重构后的 P1 分支） | RM-AG0039 / BDD-6/7 |
| `agate/rules/dispatch.yaml` | 新增 `judge_required_since: "2026-08-22"`（L17，ISO 字符串，YAML 权威判据 + 注释 L14-16 声明语义） | 规则权威源数据面 |
| `agate/rules/schema/dispatch.schema.json` | `properties.judge_required_since`（L19-22）同步声明（string + description 判据说明） | 数据面 schema 同步 |
| `agate/state-machine.md` | L442-446 judge 模板语义更新（机制后新任务必须含 `judge.enabled: true`；历史任务缺块跳过） | M8 文档面 |
| `agate/phase-cards/P1-requirements.md` | 产出规格 checklist 新增「`judge:` 启用声明（RM-AG0039 强制）」条（L58）+ frontmatter 样例注释同步（L82-84） | M9 文档面 |

### gate_p1 judge 校验块（check-gate.py L647-664）

判据（P2-review 锁定决策 2 + NB-4）：`judge = _load_state_yaml(task_dir).get("judge")`。

- judge 为 dict 且 `enabled` truthy → **放行**（继续原 P1 判定，exit 2 语义不变）。
- judge dict + enabled falsy / judge 缺失 / judge 非 dict（如 `judge: true`）→ **同走 created 判据**（NB-4）：
  - `created = _md_field_get("created", p1_file)`（C 批 agate-md-field-get `created` op）；`cutoff = read_rules_yaml(resolve_rules_root(__file__), "dispatch").get("judge_required_since")`（C 批规则读取路径）；
  - `cutoff` 为 str 且 `_is_iso_date(created)` 且 `created >= cutoff`（ISO 字典序）→ **exit 1**（机制后新任务缺/未启用 judge）；
  - 否则（pre-cutoff / created 缺失或非 ISO）→ **跳过**（fail-open，R5）。
- **未动**：gate_p65（L1034-1056 judge 强门槛子阶段）/ P2-P8 分支 / 退出码语义 / NEED_CONFIRM 判定（L640-645 原样，锁定决策 5）。

### 文档面同步

- `state-machine.md` L442-446：`.state.yaml` 模板 judge.enabled 注释更新为「机制后新任务（P1 created ≥ `judge_required_since`，rules/dispatch.yaml "2026-08-22"）必须含 `judge.enabled: true`，check-gate P1 机械校验 exit 1；历史任务（created < 截止或未声明）缺块 → 跳过」；P6.5 硬边界/早退语义（L153/155）未改（约束 3）。
- `phase-cards/P1-requirements.md` L58：产出规格 checklist 新增「`judge:` 启用声明」条（kick 新任务 P1 初始化须在 .state.yaml 写 `judge.enabled: true`；check-gate P1 机械校验缺失/未启用 → exit 1；历史任务缺块跳过）；L82-84 frontmatter 样例注释同步（judge 声明写在 .state.yaml，非 P1 frontmatter）。

## 自查结果（自查≠P5 gate）

| 项 | 方法 | 结果 |
|----|------|------|
| check-gate 全量（含 judge P1 七用例 + gate_p65 三态既有用例） | `python3 -m pytest agate/tests/unit/test_check_gate.py -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp` | **PASS**：**172 passed**（judge P1 7 用例全绿——3 红转绿 [机制后缺失/falsy-after-cutoff/disabled-after-cutoff exit 1] + 4 守卫保绿 [enabled-true / pre-cutoff / 无 created / 非 dict fail-open]；gate_p65 judge 三态既有用例保绿，P2-P8 零回归） |
| 真实树结构一致性（dispatch.yaml schema 同步验证） | `python3 agate/scripts/check-structure-consistency.py` | **PASS**：S1-S6+S0 全 OK，exit 0 |
| 协议一致性（worktree 自己的） | `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` | **PASS**：0 ERROR（321 既有 WARNING，rc=0） |
| 用例计数 | `bash agate/tests/scripts/count-tests.sh` | **PASS**：1215 ≥ 1202 基线（只增不减） |

- 未跑全量 pytest（主 Agent 稍后统一验证）；自查 ≠ gate，不声称「P5 已过」。

## 触发面清单（SELF-GATE）

| 触发面 | 文件 | 判定 |
|--------|------|------|
| `agate/scripts/*.py` | `agate/scripts/check-gate.py` | 触发（SELF-GATE.md）——commit message 需含 `self-gate-review:` / `self-gate-skip:`（主 Agent 落实） |
| `agate/**/*.md` / rules YAML | `agate/rules/dispatch.yaml` / `agate/state-machine.md` / `agate/phase-cards/P1-requirements.md` | 触发（协议本体 md + 规则权威源数据面） |
| 测试文件 | `agate/tests/unit/test_check_gate.py`（P3 落盘，本批未改） | 不触发 SELF-GATE（测试文件非协议本体；commit 纪律照常） |

## 门槛对照（dispatch「什么算完成」）

- [x] 5 文件改动落盘（check-gate.py / dispatch.yaml / dispatch.schema.json / state-machine.md / P1 卡）
- [x] P3 红测试转绿：judge P1 缺失/falsy 机制后用例 exit 1（3 红转绿）；历史任务 + 非 dict fail-open 守卫保绿（4 守卫）
- [x] gate_p65 三态既有用例保绿（锁定决策 5：gate_p65/2i.1/ci-backstop 消费语义逐字节不变）
- [x] check-structure-consistency.py 0 ERROR（dispatch.yaml schema 同步验证）
- [x] check-protocol-consistency.py --strict-errors-only 0 ERROR（worktree 自己的）
- [x] count-tests ≥ 1202（实测 1215）
- [x] P4-implementation.md 存在且含实施摘要 + 自查结果（本批段）
- [x] 本批禁改范围（check-protocol-consistency.py / test_check_routing.py / test_env_adapt_docs.py / workflow / UPGRADING 章节本体 = A/D 批范围）未触碰

## 批界偏差标注（收尾 implementer，P4-review INFORMATIONAL #1 处理）

[批界偏差：test_env_adapt_docs.py:172 注释（R4 平台假设扫描自伤修复「无 /tmp 字面」→「无临时目录字面量」）经收尾 implementer 修改，属跨批必要修复（D 批文件集）；根因 = 平台假设扫描器对注释文本中的 `/tmp` 字面量误报，修复不改变测试语义。P7 一致性核对时按此标注处理]
