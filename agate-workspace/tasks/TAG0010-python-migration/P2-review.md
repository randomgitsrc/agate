---
phase: P2
task_id: TAG0010-python-migration
type: review
parent: P2-design.md
trace_id: TAG0010-P2-20260814
status: approved
created: 2026-08-14
agent: plan-eng-review
---

# P2 复评（第二轮）— agate 产品逻辑 Python 化（阶段一）

> 评审人：plan-eng-review（工程经理视角）。
> 复评对象：修复轮修订后的 P2-design.md（v2.0 机器字段不变：candidate_count: 3）。
> 修复依据：P2-review.md（rejected，3 BLOCKER + 2 非阻塞）+ P2-dispatch-context-architect-fix.md（主 Agent 已批决策）。
> 复评范围：只核 5 项是否修订到位；锁定部分（方案 A / 候选 B/C / gate_commands / minimal_validation / env_constraints / frontmatter）抽查未动。

## 结论摘要

**approved** — 上轮 3 个 BLOCKER + 2 个非阻塞全部修订到位，且实测复核了修复引用的技术事实（R2 命中确为 docstring、ci-gate-backstop.py 调用关系、BDD-9 BASELINE_CHANGE 已落 P1）。锁定部分抽查未被动。

---

## 复评结果（5 项逐项）

### BLOCKER-1：BDD-6 前置验证 —— 修订到位

- **§3.2 批次 1 新增 BDD-6 前置验证执行方案**（P2-design.md:140-143）：
  - 预期违规清单明确列出 **4 行 R2，全部位于 docstring**（`agate-json-get.py:5` 的 `echo "$x" | python3 -c '...'` 示例；`check-protocol-consistency.py:23-25` 的 `python3 scripts/check-protocol-consistency.py [--strict|--json]` 用法示例），并指出当前 `r2_exempt` 只豁免 `#`/`@test`/`command -v`/`env` 形态（check-platform-assumptions.sh:43-55）。
  - **实测复核**：本复评重读 `agate-json-get.py` L1-12 与 `check-protocol-consistency.py` L2-26，确认 4 处命中均在 `"""` docstring 块内，与设计声明一致。
  - 处理方式**写死**（主 Agent 决策）：扫描器 py 版 `r2_exempt` 语义扩展到 `"""` docstring 块（docstring 示例不命中 R2，与 `#` 注释行同类豁免）；**不改写既有 py 的 docstring**（守住 §2 边界「18 既有 py 不做功能/文档改写」）。
  - **零命中目标**明确：docstring 豁免后对既有 18 py 扩展扫描器扫描 = 0 命中（exit 0），BDD-6 前置验证通过；新增 py 同受豁免约束。
- **§3.6 补 docstring 豁免两类用例**（P2-design.md:240 ⑥）：docstring 内 python3 引用不命中 R2（豁免生效）+ 真 R2 命中（docstring 外裸 python3）仍被检出（豁免不越界）。用例数 check-platform-assumptions.bats 14→16、总 38→40，不违反 count-tests「用例数不减少」约束。

### BLOCKER-2：批次 0 依赖自相矛盾 —— 修订到位

- **批次 0 收窄**（P2-design.md:134）：只做「`resolve_tasks_dir` 改调 `agate_common.resolve_workspace`」（消除对 agate-workspace-resolve.sh 的 bash subprocess）；`_find_bash`/`_bash_cmd` **保留**（`run_gate` 仍调 check-gate.sh）；`run_gate` 的 check-gate.sh → check-gate.py 切换**移入批次 2**（与 check-gate.py 产出同批）；`_bash_cmd` 随批次 2 各被调脚本 py 化逐个删除（check-gate.py / check-tdd-red.py / check-p6-provenance.py 落地后调用点同步换 py）。
- **实测复核**：ci-gate-backstop.py 中 `run_gate` 调 check-gate.sh（:50-58）、`_bash_cmd` 调 check-tdd-red.sh（:181-184）与 check-p6-provenance.sh（:267-270）——批次 0 若删 `_bash_cmd` 确实 NameError，修订后依赖链闭合。
- **批次 0 验证口径更新**（P2-design.md:135）：仅 `agate-workspace-resolve.bats`(10) 改调 py 后绿 + `helpers-python.bats`(3) 重构后绿 + `ci-gate-backstop.bats`（断言仅 workspace 解析相关）改后绿 + 全量 bats，与修复轮派发要求一致。

### BLOCKER-3：hook 薄壳 fallback 语义 —— 修订到位（BASELINE_CHANGE 已批准）

- **§3.3 fallback 语义改为 fail-closed**（P2-design.md:179-184）：薄壳只承担「python 探测 + exec 主程序 + 失败阻断」三件事；exec 失败时输出明确 GATE ERROR + exit 非 0，**不运行保留的 sh gate 逻辑**（保 sh 逻辑需双份维护 gate 判定，违背本任务宗旨）。薄壳代码与注释描述现在自洽（删除了「保留 sh 逻辑 fallback」的误导表述）。
- **引用 P1 BDD-9 BASELINE_CHANGE**：§3.3 明确标注「此语义为主 Agent 已批准的 [BASELINE_CHANGE]（P1 BDD-9，P1-requirements.md §4 BDD-9 标注）」；§2 风险点（:98）与 §8 完成标志 hook 行（:367）同步为 fail-closed 表述。
- **实测复核**：P1-requirements.md:302 已含主 Agent 2026-08-14 批准的 BASELINE_CHANGE 标注（含理由 ①②③ + 影响面：Windows 无 python 用户 commit 被阻断）。**这是合法变更，非缺陷**——fail-closed 阻断 + UPGRADING 明示 python3+pyyaml 为强制安装项，P3 test-designer 按 fail-closed 语义写用例。

### 非阻塞-1：pyproject.toml 死 ignore 条目 —— 修订到位

- **§3.4 清理**（P2-design.md:210）：`E501`（select 只含 E4/E7/E9，未选中）、`PLR0911/0912/0915/2004` 与 `PLC0415`（select 只含 PLW，PLR/PLC 未选中）均移除，并注明「属误导性死条目，不再列出」。现 ignore 只含 4 组生效条目（BLE001/PLW1510/SIM115/RUF001-003），与 select 集自洽。

### 非阻塞-2：files_to_read 补薄壳源 —— 修订到位

- **§5 补两项**（P2-design.md:295-298）：`pre-push-gate.sh`（批次 3 薄壳化独立迁移源——AGATE_ALIGNMENT_REVIEW_THRESHOLD 关键字保留，表 C 锚点）+ `commit-msg-self-gate.sh`（批次 3 薄壳化独立迁移源——self-gate 触发面 grep）。批次 3 三个薄壳的迁移源现已齐备，消除 P4 实现就绪度缺口。

---

## 测试缺口复核

- **BLOCKER-1 关联**：docstring 豁免两类用例已进 §3.6 ⑥（豁免生效 + 豁免不越界）——闭合。
- **BLOCKER-2 关联**：批次 0 收窄后「_bash_cmd 存活」由设计变更直接消解（不再存在批次 0 中间态），无需新增中间态用例——闭合。
- **BLOCKER-3 关联**：fail-closed 语义下无「运行 sh 兜底逻辑」用例需求；minimal_validation 项 1 已验证 python 缺失时 exit 非 0（未静默放行），与 fail-closed 一致；P3 按 BDD-9 fail-closed 语义写用例——闭合。
- **扫描器扩展反向用例**：§3.2 批次 1 的 BDD-6 前置验证方案（预期违规清单 + 零命中目标）即反向基线；§3.6 ⑤ 新增 `.py` fixture R1-R5 正向检出用例——闭合。
- **count-tests 口径**：§3.6 保留「用例数不减少」约束；每文件用例数对照已列（16/9/2/3/10 = 40，两处新增均来自 docstring 豁免用例）——闭合。

---

## 锁定部分抽查（未被动）

- **frontmatter**（P2-design.md:11-14）：candidate_count: 3 / packages 6 项 / domains [backend, cli] / ui_affected: false 均不变。
- **方案 A 推荐 + 候选 B/C**（§1）：表述与权衡表未动；方案 C 仍以「违背 SUGGEST-1」明确否决。
- **gate_commands**（§4）：P3/P3_formatter/P5 + P5_consistency/P5_ruff/P5_scan/P5_ci 原样。
- **minimal_validation**（§7）：5 条（4 confirmed + 1 not_needed 纯代码逻辑声明）未动。
- **env_constraints**（§6）：未动，未弱化。

---

## 总体结论

**approved**。3 个 BLOCKER + 2 个非阻塞全部按修复轮派发要求修订到位，引用技术事实均经本复评实测复核成立；锁定部分抽查未被动。P3 test-designer 可依据修订后 P2-design.md 写测试（尤其 docstring 豁免两类用例、fail-closed 薄壳语义、批次 0 收窄后的验证口径）。

阻塞问题数量：0
