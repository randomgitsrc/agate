---
review_date: 2026-07-31
reviewer: protocol-alignment-review
change_summary: 将 check-tdd-red.sh 和 agate-capture-env-baseline.sh 从硬编码 pytest 输出解析改为 formatter + 标准 JSON 格式，修复 P6 截图 PNG-only 限制、P7 DESIGN_GAP blockquote 正则、文档 pytest 软绑定
files_changed:
  - agate/scripts/check-tdd-red.sh
  - agate/scripts/agate-capture-env-baseline.sh
  - agate/scripts/check-gate.sh
  - agate/scripts/check-p6-evidence.sh
  - agate/scripts/check-protocol-consistency.py
  - agate/scripts/gate-result.sh
  - agate/assets/formatters/README.md
  - agate/assets/formatters/pytest.sh
  - agate/assets/formatters/vitest.sh
  - agate/assets/formatters/go-test.sh
  - agate/assets/formatters/generic-tap.sh
  - agate/assets/formatters/generic-junit-xml.sh
  - agate/assets/formatters/generic-exit-only.sh
  - agate/state-machine.md
  - agate/assets/execution-roles/architect.md
  - agate/assets/execution-roles/test-designer.md
  - agate/assets/execution-roles/verifier.md
  - agate/assets/templates/task-files.md
  - agate/assets/templates/dispatch-prompt.md
  - agate/phase-cards/P0-orchestrator.md
  - agate/phase-cards/P3-tdd.md
  - agate/phase-cards/P5-verification.md
  - agate/tests/README.md
  - agate/tests/unit/check-tdd-red.bats
  - agate/tests/unit/check-tdd-red-formatter.bats
  - agate/tests/unit/check-gate.bats
  - agate/tests/unit/agate-capture-env-baseline.bats
  - docs/hardening-roadmap.md
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED（修复后） |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED（修复后） |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | NEEDS_HUMAN_REVIEW（CHANGELOG 未更新） |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

> **修复记录**：A1/A3 审查发现 4 处 pytest 残留引用（state-machine.md L188/L274, dispatch-protocol.md L61/L545），已在 commit `35de038` 中全部修复。修复后重跑全量验证：502 bats passed / 0 shellcheck / 0 consistency ERROR。

---

## 逐项审查

### A1: 文档→脚本对齐

**MISALIGNED** — 核心脚本逻辑已对齐，但 `state-machine.md` 和 `dispatch-protocol.md` 残留 4 处过时描述。

#### A1-1: state-machine.md:274 — 输出格式描述过时

**文档声明**（state-machine.md:274）：
> **判定方式**：主 Agent 跑 `scripts/check-tdd-red.sh`（见下），不自行解析 pytest 输出。脚本输出 `assertion_failures=N, collection_errors=M` 格式，gate 判定为 exit 0（含经典红灯和 B 类红灯）。

**脚本实现**（check-tdd-red.sh:96-145）：
脚本不再输出 `assertion_failures=N, collection_errors=M` 格式。实际输出为 `TDD_CHECK: classic red-light (assertion failures only)` 等 `TDD_CHECK:` 前缀文本。判定逻辑通过 JSON 字段（`exit_code`/`failed`/`errors`/`syntax_errors`/`import_errors`）在 `judge_result()` 函数内完成。

**差异**：文档描述的输出格式（`assertion_failures=N, collection_errors=M`）已不存在于脚本中。脚本改为内部 JSON 判定 + `TDD_CHECK:` 文本输出。

**建议**：将 state-machine.md:274 修改为：
> **判定方式**：主 Agent 跑 `scripts/check-tdd-red.sh`（见下），不自行解析测试输出。脚本通过 formatter 将输出标准化为 JSON 后判定 A/B 类错误，输出 `TDD_CHECK:` 前缀的诊断行，gate 判定为 exit 0（含经典红灯和 B 类红灯）。

#### A1-2: state-machine.md:274 — "pytest 输出"残留

**文档声明**（state-machine.md:274）：
> 不自行解析 pytest 输出

**脚本实现**（check-tdd-red.sh:12-43）：
脚本注释明确声明"技术栈无关"，通过 formatter 机制支持任意测试运行器，不再绑定 pytest。

**差异**：文档仍写"pytest 输出"，但脚本已不解析任何特定框架的输出。

**建议**：改为"不自行解析测试运行器输出"。

#### A1-3: state-machine.md:188 — "P5 的 pytest 全绿兜底"

**文档声明**（state-machine.md:188）：
> （P3 跳过时 P4 gate 不要求红灯变绿，P5 的 pytest 全绿兜底）

**脚本实现**（check-gate.sh:145-204）：
P5 gate 从 `gate_commands.P5` 动态读取命令，不硬编码 pytest。

**差异**：文档写"pytest 全绿"，但 P5 gate 是技术栈无关的。

**建议**：改为"P5 的 gate_commands.P5 全绿兜底"。

#### A1-4: dispatch-protocol.md:61 — "主 Agent 跑 pytest -q"

**文档声明**（dispatch-protocol.md:61）：
> 例：P5 subagent 说 "failed=0" → 主 Agent 跑 pytest -q
>     确认 exit 0 且 failed 行确实为 0，才算通过。

**脚本实现**（check-gate.sh:146）：
P5 gate 从 P2-design.md gate_commands.P5 动态读取命令。

**差异**：文档示例用 pytest，但实际应跑 gate_commands.P5 声明的命令。

**建议**：改为"主 Agent 跑 gate_commands.P5 声明的命令"。

#### A1-5: dispatch-protocol.md:545 — "Playwright / shell / pytest" 残留

**文档声明**（dispatch-protocol.md:545）：
> P6 verifier 交付的验证脚本（Playwright / shell / pytest）应由主 Agent 执行。

**对比**：dispatch-prompt.md:130 已同步修改为"Playwright / shell / 测试框架"，但 dispatch-protocol.md 未同步。

**差异**：dispatch-protocol.md 与 dispatch-prompt.md 不一致。

**建议**：dispatch-protocol.md:545 同步改为"Playwright / shell / 测试框架"。

---

### A2: 脚本→文档对齐

**ALIGNED** — 脚本的核心逻辑变更在文档中有对应描述。

**脚本实现**（check-tdd-red.sh:54-83, gate-result.sh:72-100）：
- `read_gate_commands()` 从 P2-design.md 解析 `P3`/`P3_{suffix}`/`P3_{suffix}_formatter`/`project_module` 键
- `resolve_formatter()` 和 `run_test_with_formatter()` 是 gate-result.sh 新增的公共函数
- formatter 路径解析：绝对路径 → `task_dir/.agate/formatters/` → `agate_root/assets/formatters/`

**文档声明**（state-machine.md:276-290）：
> 脚本通过 **formatter** 将测试输出标准化为 JSON，再判定 A/B 类错误。formatter 在 `gate_commands.P3_formatter` 中声明（可选键，见 P2-design.md）。不提供 formatter 时退化为 exit-code-only（所有红灯 = 可推进，精度降低但不会阻断）。

**文档声明**（assets/formatters/README.md:1-124）：
完整的 formatter 契约文档，含 JSON 格式定义、字段说明、速查表、gate_commands 声明方式、路径解析规则、多技术栈声明。

**结论**：脚本逻辑与文档描述一致。formatter 契约、探测链、退化策略、路径解析规则在文档中均有对应。

---

### A3: 一致性连锁 + 反向传播

**MISALIGNED** — A3a（连锁）有 1 处未同步，A3b（反向传播）基本覆盖但 CHANGELOG 缺失。

#### A3a: 一致性连锁

**dispatch-protocol.md:545 未同步**：

dispatch-prompt.md:130 已将"Playwright / shell / pytest"改为"Playwright / shell / 测试框架"，但 dispatch-protocol.md:545 的相同文本未同步。这两个文件是模板（dispatch-prompt.md）与权威源（dispatch-protocol.md）的关系，模板注释明确写"本模板与 dispatch-protocol.md「派发 prompt 模板」节保持同步，协议文件为权威来源"。

**建议**：dispatch-protocol.md:545 同步修改。

#### A3b: 反向传播检查

| 应被影响的文件 | 实际状态 | 结论 |
|---------------|---------|------|
| agate/WORKFLOW.md | gate 表均用 `gate_commands.P5`，无 pytest 硬编码 | ✅ 已覆盖 |
| agate/dispatch-protocol.md | 4 处 pytest 残留（见 A1-4/A1-5） | ❌ 未完全覆盖 |
| agate/state-machine.md | 2 处 pytest 残留 + 1 处输出格式过时（见 A1-1/A1-2/A1-3） | ❌ 未完全覆盖 |
| agate/orchestrator-template.md | :17 `"pytest*": allow` 是 permissions 示例值 | ⚠️ 示例性，NEEDS_HUMAN_REVIEW |
| agate/git-integration.md | :51 `chore: 升级 pytest` 是 commit message 示例 | ✅ 示例性引用，合理 |
| agate/role-system.md | 无 pytest 引用 | ✅ 已覆盖 |
| agate/LIMITATIONS.md | 无 pytest 引用 | ✅ 已覆盖 |
| agate/CONTEXT.md | 无 pytest 引用 | ✅ 已覆盖 |
| assets/execution-roles/architect.md | 已更新 gate_commands 示例含 formatter | ✅ 已覆盖 |
| assets/execution-roles/verifier.md | 已更新"技术栈无关"段 | ✅ 已覆盖 |
| assets/execution-roles/test-designer.md | 新增 vitest mock hoisting 说明 | ✅ 已覆盖 |
| assets/templates/task-files.md | 已更新 gate_commands 模板 + P5 门槛描述 | ✅ 已覆盖 |
| assets/templates/dispatch-prompt.md | 已更新"测试框架" | ✅ 已覆盖 |
| phase-cards/P0-orchestrator.md | 已扩展测试框架自检列表 | ✅ 已覆盖 |
| phase-cards/P3-tdd.md | 已更新"技术栈无关"段 | ✅ 已覆盖 |
| phase-cards/P5-verification.md | 已更新"技术栈无关"段 + fail-list 描述 | ✅ 已覆盖 |
| CHANGELOG.md | 未检查到本次变更的 `[Unreleased]` 条目 | ⚠️ NEEDS_HUMAN_REVIEW |

---

### A4: 测试覆盖

**ALIGNED** — 测试覆盖充分，附实跑输出。

**实跑命令**：
```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

**实跑结果**：
```
503 tests passed, 0 failed
```

关键测试文件覆盖：
- `unit/check-tdd-red.bats`：30 个用例（从 9 个扩展到 30 个），覆盖 formatter 探测链、A/B 类判定、多技术栈命令、exit-code-only 退化
- `unit/check-tdd-red-formatter.bats`：12 个用例（新增），覆盖 6 个内置 formatter 的 JSON 输出契约
- `unit/check-gate.bats`：91 个用例（含新增 G_DG_ANCHOR.3 blockquote DESIGN_GAP 测试）
- `unit/agate-capture-env-baseline.bats`：15 个用例（从 9 个扩展），覆盖 formatter 提取 fail-list、缓存命中/未命中
- `unit/check-p6-evidence.bats`：25 个用例（含非 PNG 图片格式检测）

**一致性检查**：
```bash
python3 agate/scripts/check-protocol-consistency.py
```
结果：0 ERROR，13 WARNING（均为叙事文件引用不存在，与本次变更无关）。

**Shellcheck**：
```bash
shellcheck -S warning agate/scripts/*.sh agate/assets/formatters/*.sh
```
结果：0 warnings。

**测试用例计数**：
```bash
bash agate/tests/scripts/count-tests.sh
```
结果：497 个测试用例（不含 sanity.bats 6 个），与 tests/README.md 表格一致。

---

### A5: 下游影响 + 文档传播

**NEEDS_HUMAN_REVIEW** — 破坏性变更影响评估 + CHANGELOG 缺失。

**破坏性变更分析**：

1. **check-tdd-red.sh 输出格式变更**：旧脚本输出 `assertion_failures=N, collection_errors=M`，新脚本输出 `TDD_CHECK:` 前缀文本。若有外部脚本/CI 解析旧格式，会断裂。但根据协议设计，check-tdd-red.sh 的消费者是主 Agent（看 exit code）和 pre-commit hook（看 exit code），不解析 stdout 文本。**风险低**。

2. **gate_commands 新增键（P3_formatter/P5_formatter/project_module）**：可选键，不声明时退化为 exit-code-only。向后兼容。**无破坏性**。

3. **check-p6-evidence.sh 截图格式放宽**：从 PNG-only 放宽为任意图片格式。旧行为（PNG 合法 ≤1KB → WARNING）保持不变，新增 JPEG/GIF/WebP 支持。**无破坏性，是放宽**。

4. **check-gate.sh P7 DESIGN_GAP 正则放宽**：从 `^\s*-?\s*\[DESIGN_GAP:` 放宽为 `^\s*>?\s*-?\s*\[DESIGN_GAP:`，额外匹配 blockquote 格式。原有匹配不受影响。**无破坏性，是放宽**。

5. **agate-capture-env-baseline.sh 行为变更**：无 formatter 时从"尝试解析"变为"放弃捕获"。旧脚本在无 formatter 时也尝试 grep `FAILED` 前缀提取 fail-list，新脚本直接放弃。**行为变更**：无 formatter 的项目不再生成 pre-task-baseline.md。但 P5 gate 对缺失 baseline 有优雅降级（WARNING-only），**风险低**。

**CHANGELOG**：未检查到本次变更的 `[Unreleased]` 条目。协议语义变更（check-tdd-red.sh 重写 + formatter 体系 + gate_commands 扩展）应标注 CHANGELOG。

**建议**：
- 在 CHANGELOG.md `[Unreleased]` 节新增条目，标注 check-tdd-red.sh formatter 化 + 截图格式放宽 + DESIGN_GAP 正则修复
- 确认无外部项目依赖 check-tdd-red.sh 的 `assertion_failures=N` 输出格式

---

### A6: 锚点表覆盖

**ALIGNED** — CHECK 9 锚点表已更新。

**文档声明**（check-protocol-consistency.py:537-540）：
```python
{
    "desc": "TDD 红灯检查",
    "script": "agate/scripts/check-tdd-red.sh",
    "keywords": ["formatter", "pytest"],
},
```

**脚本实现**（check-tdd-red.sh:12-43）：
脚本注释含 `formatter` 和 `pytest`（探测链 fallback）关键词。

**结论**：锚点表 keywords 从 `["pytest"]` 更新为 `["formatter", "pytest"]`，与脚本当前内容一致。`pytest` 保留是因为探测链仍含 `which pytest` fallback。

gate-result.sh 新增的 `resolve_formatter` / `run_test_with_formatter` 函数已在 GATE_SCRIPT_EXEMPT 白名单中注释说明（"无 gate 逻辑 + formatter 公共函数（受调用方测试覆盖），不需要锚点"），合理。

---

### A7: 设计原则一致性

**ALIGNED** — 本次变更直接落实 ADR-003。

**ADR-003 声明**（adr.md:69-93）：
> agate 不硬编码测试框架/语言/部署方式，只定义流程骨架。技术栈相关的命令通过 P2-design.md 的 `gate_commands` 字段注入，由项目自定义。
> ...
> 后果：agate 不能自动发现项目的测试/构建命令，依赖人工声明

**本次变更**：
- check-tdd-red.sh 从硬编码 pytest 输出解析改为 formatter + JSON 标准格式——直接消除 ADR-003 指出的"硬编码测试框架"问题
- formatter 是可选的（退化为 exit-code-only），保持"不绑定"原则
- gate_commands 扩展 P3_formatter/P5_formatter/project_module 可选键，通过 P2 注入而非硬编码
- check-p6-evidence.sh 从 PNG-only 放宽为任意图片格式——消除对特定截图工具的绑定

**ADR-002（可判定性）**：formatter 体系保持 gate 门槛机器可判定（JSON 字段 → exit code），符合 ADR-002。

**ADR-004（安全网分层）**：formatter 不改变三层防线结构（主 Agent 主动验 + hook + CI backstop），符合 ADR-004。

**未记录的架构决策**：formatter 体系本身是一个新的架构决策（"通过 formatter 适配层实现技术栈无关的测试输出解析"），建议补充新 ADR 记录此决策。但这不阻断——hardening-roadmap.md P2.51 已有记录。

**结论**：ALIGNED。
