---
phase: P4
task_id: TAG0004-env-adaptation
type: implementation
parent: P2-design.md
trace_id: TAG0004-P4-20260813
status: draft
created: 2026-08-13
agent: implementer
---

implementation_dir: agate/scripts/

# P4 实现 — 组 2（check-tdd-red A/B 判定组）

## 改动文件（仅本组 3 个文件，未触碰组 1/组 3 范围）

| 文件 | 改动 |
|------|------|
| `agate/scripts/check-tdd-red.sh` | judge_result 增加 raw_output 编译/import 关键词判定（RM-AG0002）+ name_errors B 类判定（TPV0090-M4）+ 头注释更新 |
| `agate/scripts/gate-result.sh` | `run_test_with_formatter` 无 formatter / formatter 失败两个降级分支输出 JSON 增 `raw_output` 字段（供 judge_result 关键词判定） |
| `agate/assets/formatters/pytest.sh` | 输出 JSON 增 `name_errors` 数组字段（解析 `NameError: name 'X' is not defined`） |

## 实现要点（对应 dispatch-context 约束）

- **RM-AG0002（BDD-30/31）**：gate-result.sh 无 formatter 分支把测试原始输出以 `raw_output` 字段写入 JSON（复用 `agate-json-get.py escape`，与 write_gate_result 同机制）。judge_result 在 exit 0 检查之后、syntax_count 之前新增：`exit_code == 1` 且 `raw_output` 含 `Traceback|SyntaxError|ImportError|ModuleNotFoundError`（精确组合，不用裸 `error:`）→ 判 A 类（exit 1）；无关键词 → 走原路径判正确红灯（exit 0）。
- **TPV0090-M4（BDD-35/36/37）**：judge_result 在 `errors > 0` 分支前新增 `name_errors_count > 0` 判定——优先按 project_module 前缀匹配（复用 `agate-json-get.py count_prefix`，key=`name_errors`，subkey=`module`，env=`PROJECT_MODULE`）；pytest.sh 对 `NameError: name 'X' is not defined` 解析出 symbol 与 module（点号符号取父路径，如 `myapp.compute` → `myapp`；裸符号 → 空串）。
- **向后兼容（BDD-36）**：`globals().get()` 规避模式失败为普通断言失败（非 NameError）→ formatter 的 name_errors 为空 → 走 failed 分支 classic red-light（exit 0），不受影响。
- **防过宽（BDD-37）**：pytest.sh 的 name_errors 解析只匹配精确的 `NameError: name 'X' is not defined` 形态——TypeError 行不匹配 → name_errors 为空 → 落入 `errors > 0` 分支判 A 类（exit 1），扩展不扩大到所有 errors。

## 关键实现决策（两条）

1. **exit==1 才做 raw_output 关键词判定**：P0-brief known_risk（"如 exit 1 且输出含 compile/error 关键词 → 判 A 类"）、P1 BDD-30 Given（"测试运行器 exit 1 且输出含..."）、dispatch-context 一致写明 exit 1。同时回归守卫 TD.4-TD.8 使用 exit 2 + ImportError/SyntaxError 文本且期望 exit 0（旧 exit-code-only 语义，DEPRECATED 保留用例）——若用 exit>0 判定会把这些用例打回 exit 1，造成回归。两者都要求 exit==1 限定。
2. **裸符号/前缀未匹配的 NameError 仍归 B 类**：见下方 [DESIGN_GAP]。

## [DESIGN_GAP]

[DESIGN_GAP: P2 候选 11A 未明确"formatter 检测到 NameError 但无 project_module 前缀信息"（裸符号 / 前缀不匹配）时的归类——字面读法是"未匹配 → 仍 A 类"，但 bdd-35 测试契约的 fixture（ERROR tests/test_x.py - NameError: name 'compute' is not defined + project_module=myapp）输出中不存在 myapp 字符串，任何基于 module 前缀的严格门禁都无法命中。实现选择：前缀匹配仅影响判定消息措辞，只要 formatter 检测到 NameError 即判 B 类（"测试引用未实现符号正是 TDD 红灯正常状态"，P0-brief known_risk），非 NameError（TypeError 等）由 pytest.sh 精确解析范围 + errors>0 分支兜底仍判 A 类（BDD-37 回归绿）]

## 自查结果（自查 ≠ P5 gate）

- `bats agate/tests/unit/check-tdd-red.bats agate/tests/unit/check-tdd-red-formatter.bats`：**56/56 通过**。
  - 红灯转绿：**bdd-30**（无 formatter + exit 1 + Traceback/SyntaxError → A 类 exit 1）、**bdd-35**（formatter 项目模块内 NameError → B 类 exit 0）、**bdd-35f**（pytest.sh 输出含 name_errors 字段）。
  - 回归守卫保持绿：**bdd-31**（无 formatter 普通失败 → 红灯 exit 0）、**bdd-36**（globals().get() 兼容 → classic red-light）、**bdd-37**（TypeError → A 类 exit 1），以及 TD.1-8 / TDD.* / PYX.* / FMT.1-12 全部既有用例。
- `shellcheck -S warning agate/scripts/check-tdd-red.sh agate/scripts/gate-result.sh`：**0 error**。
- 附带回归：`check-gate.bats / ci-gate-backstop.bats / dispatch-context-warning.bats` 仅 `bdd-14`（M6 CRLF frontmatter，组 1 的 check-gate.sh 范围，P3 已标注当前红）失败，与本组改动无关；其余全绿。

## 改动范围确认

- 未修改任何测试文件（P3 契约原样）。
- 未触碰组 1 文件（pre-commit-gate.sh / check-gate.sh / check-p6-format.sh / check-p6-evidence.sh）与组 3 文件。
- 未改动主 checkout `/home/kity/oclab/agate` 与 `~/.agate`。
- 无范围缺口（SCOPE_GAP）：P2 声明本组的 3 个文件均已覆盖（RM-AG0002 + TPV0090-M4 + pytest.sh formatter），prompt 未遗漏 P2 已声明给本组的任何改动。

`[PROD_NOT_TOUCHED]` 本阶段仅读 worktree 内文件并跑 bats/shellcheck 自查，未接触任何生产环境。
