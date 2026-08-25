---
phase: P4
task_id: TAG0024
type: review
parent: P4-implementation.md
trace_id: TAG0024-P4-review-20260825
status: approved
created: 2026-08-25
agent: review
---

# P4-review — TAG0024 独立评审（review 角色，单一评审，无需组长汇总）

评审方式：不采信各批次/主 Agent 自述，逐条用 `git diff`/`grep`/独立重跑 pytest/ruff/shellcheck/consistency 复核。以下按 dispatch-context 约束节列出的 6 个重点逐条给出核验结论（含证据）。

## 重点 1：同源铁律是否真正落地

`grep -n "spec_from_file_location" agate/scripts/agate-md-field-set.py` 命中第 50 行：

```python
spec = importlib.util.spec_from_file_location(module_name or name.replace("-", "_"), path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
_CACHE[key] = mod
```

`_load_script()`（第 45-54 行）配模块级 `_CACHE` 缓存，仿 `check-routing.py:41-52` 既有模式。`_fm_check()`/`_fm_get()`/`_judge_verdict()`（第 57-69 行）分别加载 `agate-frontmatter-check.py`/`agate-md-field-get.py`/`check-judge-verdict.py`。关键是**实际调用点**而非只是加载：`_cmd_set()` 第 334-345 行真实取 `fm_check_mod.SCHEMAS.get(basename)` 并调用 `fm_check_mod._check(basename, schema, candidate_fm)`；第 289-293/298-299 行真实取 `get_mod.NO_FALLBACK_INT_FIELDS`/`get_mod.NO_FALLBACK_LIST_FIELDS`/`get_mod.JSON_FIELDS`；`_status_enum_for()` 第 105 行真实取 `_judge_verdict()._VALID_STATUS`。这些都是对加载后模块对象属性/函数的直接引用，不是抄一份等价常量或逻辑。

`agate-md-field-set-gate-commands.py` 只 `import agate_common`（普通共享库 import），未走 importlib——这是正确的，因为它只需要 `agate_common.is_legal_gate_key`/`known_phase_ids`/`parse_gate_commands_block`（无连字符文件名问题的既有共享库函数），P2-design.md §3.3 已如此设计，非遗漏。

零改动核验：
```
git diff --stat -- agate/scripts/agate-frontmatter-check.py agate/scripts/agate-md-field-get.py agate/scripts/check-judge-verdict.py agate/scripts/check-events.py
```
四个文件全部空输出（含 dispatch-context 未点名但同属"不改什么"清单的 `check-events.py`），确认零改动。

**结论：核验通过，不阻塞。** 同源复用是真实的 importlib 动态加载 + 真实调用加载对象的属性/函数，不是"看起来复用"。

## 重点 2：DEBT0019/20 修复精确性

`git diff -- agate/scripts/check-gate.py` 逐行核对，改动仅三处：
1. 新增模块级常量 `_ROADMAP_EXPECTED_COLS = 9`（第 1181-1184 行）+ docstring 补充说明；
2. `_check_roadmap_done()` 内判据由 `len(cols) < 8` 精确为 `len(cols) != _ROADMAP_EXPECTED_COLS`（对应 BDD-20/21）；
3. `gate_p8()` 内 `roadmap_path` 构造：原 `os.path.join("agate-workspace", "roadmap", "roadmap.md")`（CWD 相对）改为先 `_git(["rev-parse", "--show-toplevel"])` 取仓库根、失败时 stderr 输出"仓库根不可得"区分性提示并置 `roadmap_path = None`（对应 BDD-22/23/24）。

`git diff --stat` 显示 `1 file changed, 24 insertions(+), 3 deletions(-)`，未见其他函数/判定逻辑被触及。独立重跑：
```
python3 -m pytest agate/tests/unit/test_check_gate.py --basetemp=.pytest-tmp -p no:cacheprovider -q
→ 182 passed in 23.74s
```
与主 Agent 复核记录的 182 passed 一致（非采信，本轮独立执行）。

**结论：核验通过，不阻塞。** 改动精确落在声明范围内，无越界。

## 重点 3：RM-AG0049/50 修复精确性

`git diff -- agate/rules/phases.yaml` 显示仅两处新增：
```diff
     outputs:
       - {file: P4-implementation.md, required: true}
+      - {file: P4-review.md, required: true, status_field: status}
```
```diff
+  # 注：P6.5 是挂载于 P6→P7 转移的强门槛子阶段，不是与 P0-P8 平级的独立 phase 值
+  # （.state.yaml 的 phase 字段保持 P6 直至 P7）；本条目结构化声明其产出/门槛/重试上限，
+  # 供 check-gate.py P6.5 分发与 CLI 调用，口径详见 state-machine.md「状态机定义」节。
   - id: P6.5
```
未删除/修改任何既有 `id`/`name`/`exec_role`/`gates`/`retry_cap`/`task_fields` 字段结构，P6.5 注释块为纯 YAML 注释（`#` 开头），不影响 yaml 解析结构。独立重跑：
```
python3 -m pytest agate/tests/unit/test_check_structure_consistency.py -q → 17 passed
python3 agate/scripts/check-structure-consistency.py → S0~S6 全部 OK，exit 0
```

**结论：核验通过，不阻塞。** 两处均为纯追加，无字段结构变更，S-1~S-6 实测 0 mismatch。

## 重点 4：BDD 覆盖完整性

`grep -n "def test_bdd"` 核对三个测试文件：
- `test_agate_md_field_set.py`：BDD-1~19 全部有对应测试函数（含参数化用例，如 BDD-9 覆盖 10 个证据字段、BDD-18 覆盖 6 个追加字段），独立重跑 `35 passed`（BDD-16 已转绿，非停留在 P4-implementation.md 声称的 34/35）。
- `test_check_gate.py`：BDD-20~24 对应 `test_bdd_20_p8_roadmap_literal_pipe_in_title_not_misjudged` 等 5 个函数（第 1600-1720 行附近），独立重跑 182 passed 含此 5 项。
- `test_check_structure_consistency.py`：BDD-25~28 对应 `test_bdd_25_p4_outputs_includes_review_md` 等 4 个函数（第 293-380 行附近），独立重跑 17 passed 含此 4 项。
- BDD-29（跨 issue 约束）：P1-requirements.md/P2-design.md/P3-test-cases.md 均已明确声明"无自动化测试，以 P7 diff 逐行核对方式验收"，理由（写成字符串匹配脆弱、覆盖面跨全部改动而非单一函数）合理，不视为测试缺口。本轮评审在重点 2 已对 `check-gate.py` 做逐行 diff 核对，等效完成该验收动作。

抽查典型测试实现质量（非仅看函数名存在）：
- BDD-15（`test_bdd_15_value_validation_same_source_as_check`）直接调用真实 `agate-frontmatter-check.py._check()` 取得 `expected_errors` 作为断言依据，而非硬编码期望值字符串——这是真正验证"同源"而非自我循环断言的写法。
- BDD-8（gate_commands 非法块）断言错误信息含具体非法 key 名（`offending_token in result.output`）且拒绝时文件内容与原始一致（`md_file.read_text() == original`），而非弱断言"exit 非 0 即可"。
- BDD-17（`test_bdd_17_writable_keys_is_mechanical_union`）用运行时读取真实 `phases.yaml` 计算的并集与实现的 `_writable_keys()` 返回值比对，且含正/反两个边界断言（`bump_type` 命中、生造 key 不命中）。

未发现"实现绕过测试断言"这类取巧敷衍现象。

**结论：核验通过，不阻塞。** 29 条 BDD 全部有对应落地（自动化测试或声明的等效验收方式），测试断言质量经抽查为真实交叉验证。

## 重点 5：BDD-16 fixture 修复合理性

`sed -n '805,820p' agate/scripts/check-gate.py` 确认 `gate_p2()` 确有一条独立于 `task_fields` 的正文关键词 nudge：
```python
if has_keyword(p2_text, "tradeoff") or has_keyword(p2_text, "choice_and_reason"):
    pass
else:
    sys.stderr.write("GATE P2: P2-design.md 有 ≥2 候选方案但缺'权衡'或'选择理由'描述\n")
    return 1
```
该检查读取正文散文关键词，与 `agate-md-field-set.py` 负责的 frontmatter 字段/`gate_commands` 正文块写入完全是两回事——工具设计上不应该、也没有能力生成任意正文散文来满足这条 nudge。

`git diff -- agate/tests/unit/test_agate_md_field_set.py` 显示修复范围精确：仅在 `test_bdd_16_zero_protocol_knowledge_walkthrough_converges` 函数体内追加 5 行（3 行注释 + 2 行 `p2_file.open("a").write(...)` 直接写入与本 BDD 无关的正文前提），其余 34 个测试函数逐字节未动（diff 中另两处改动是移除 `noqa: PLC0415` 注释，属于同批次 ruff lint 清理，不涉及测试逻辑）。修复后该测试的核心断言未被削弱——仍然要求 `--list` 最终无"剩余缺失"、且 `check-gate.py P2` 返回值 `!= 1`，这正是 BDD-16 声明的"零协议知识收敛"核心契约，修复没有放松这一断言，只是补齐了一个与本工具契约无关的独立正文前提。

**结论：核验通过，不阻塞。** 这是合理的测试数据缺陷修复，不是"为通过测试而弱化断言"。

## 重点 6：范围核验（无范围蔓延）

对照 P2-design.md §1.2"不改什么"清单逐项核验：
- `agate-md-field-get.py`/`agate-frontmatter-check.py`/`check-judge-verdict.py`/`check-events.py`：`git diff --stat` 均空（见重点 1）。
- `check-retrospective.py`/`check-protocol-consistency.py` 判定逻辑：`git diff --stat` 均空（未列出改动，未在改动文件清单中出现）。
- `phases.yaml` 之外阶段的 `id`/`outputs`/`gates`/`retry_cap`/`task_fields` 结构：`git diff` 显示唯二改动点即 P4 outputs 追加行与 P6.5 注释块，无其他阶段被触及（见重点 3）。
- 追加/嵌套字段类型语义（`need_confirm_resolved` 等 6 个字段）：BDD-18 测试确认均被拒绝写入，未实现覆盖式之外的语义。

改动文件全集（`git status --short` 非文档类）：`agate-md-field-set.py`（新建）、`agate-md-field-set-gate-commands.py`（新建）、`dispatch-prompt.md`/`dispatch-context.md`（修改，BDD-19）、`check-gate.py`（修改）、`phases.yaml`（修改）+ 3 个测试文件——与 P4-implementation.md 声明的改动分布完全一致，三批次文件互不交叉（分别属于各自 `implementation_dir`）。`gate-events.jsonl` 的变化是本任务自身状态机从 P2→P3 推进产生的事件账本追加，非实现代码改动，不构成范围问题。

**结论：核验通过，不阻塞。** 无范围蔓延。

## 独立复核环境验证（非采信主 Agent 复核记录，本轮独立重跑）

```
python3 -m pytest agate/tests/unit/test_agate_md_field_set.py -q        → 35 passed
python3 -m pytest agate/tests/unit/test_check_gate.py -q                → 182 passed
python3 -m pytest agate/tests/unit/test_check_structure_consistency.py -q → 17 passed
~/.venvs/agate-dev/bin/ruff check agate/                                 → All checks passed
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only → exit 0（322 个历史 WARNING，非本次改动引入，与主 Agent 记录口径一致）
shellcheck -S warning agate/scripts/*.sh                                 → exit 0
```

全部与 P4-implementation.md 主 Agent 复核记录的数字一致。

## 总体结论

6 个重点核验全部通过，未发现 CRITICAL 或需打回 implementer 修改的问题。三批次改动精确落在 P1-requirements.md 锁定的 29 条 BDD 范围内，同源复用真实落地，DEBT/RM 修复精确无越界，BDD-16 fixture 修复合理不取巧。

**status: approved**
