---
phase: P4
task_id: TAG0001-tech-debt-closure
type: implementation
parent: P5-test-results/unit.md
trace_id: TAG0001-P4-20260812
status: draft
created: 2026-08-12
agent: implementer
---

# TAG0001 — P4 修复记录（implementer-fix：serialize_evidence YAML int 边界）

> 角色：implementer-fix。范围：仅修复 `agate/scripts/agate-debt-check.py::serialize_evidence` 一处，未触碰其他文件。
> 输入：P5-dispatch-context-implementer-fix.md + P5-test-results/unit.md（失败诊断 §2）+ 既有 P4-implementation-core.md。

## 修复内容

`agate/scripts/agate-debt-check.py:64-76` `serialize_evidence()`：

- **问题**：`yaml.safe_load` 把全数字 YAML 标量解析为 `int`（如 7 位短哈希 `7008516` 无任何字母时）。原实现只拼接 `isinstance(v, str)` 的值 → int 被静默丢弃 → `--covered-hashes` 提取不到该哈希 → `check-debt.sh --retreat-coverage` 误报 `GATE DEBT WARNING`（test_bdd_15 偶发红，实测 1/4 全量运行）。
- **修复**：对 `path`/`note`/`ref` 取值及列表项，除 str 外，对非 bool 的 `int` 标量执行 `str()` 归一后再拼接——全数字哈希保持字符串语义，round-trip 稳定。bool 排除（`str(True)` == `"True"` 无哈希语义，且 bool 是 int 子类，需显式排除避免误归一）。
- 未改 schema 校验逻辑、未改测试语义、未触碰其他函数。

## 修改文件

- `agate/scripts/agate-debt-check.py`（仅 serialize_evidence 函数，+10 行）

## 验证结果（自查 ≠ P5 gate）

| 项目 | 结果 |
|---|---|
| 全数字哈希单元验证 | `path: 7008516` round-trip = `"7008516"`，HEX_RE 提取命中 |
| 端到端 `--covered-hashes` | fixture 含 `7008516` + `29301ad` → 两个哈希均输出（修复前仅 `29301ad`） |
| `bats agate/tests/unit/agate-debt-check.bats` | 20/20 绿 |
| `--filter test_bdd_15` 多轮 | 6/6 绿（≥5 次要求） |
| 全量 bats（sanity+unit+regression+integration） | 676 用例，0 not ok |
| consistency | 0 ERROR（🎉 全部检查通过） |
| shellcheck `-S warning` | 0 行输出 |
| count-tests | 670（unit/regression/integration）+ 6（sanity）= 676 基线一致 |

## [DESIGN_GAP] 声明

无自主设计决策——修复方向完全遵循 verifier 诊断（P5-test-results/unit.md §2「建议 P4 修复 serialize_evidence 对 int 做 str() 归一」）与 dispatch-context 派发指引。bool 排除属 int 子类陷阱的必要防御，不改变非 bool 语义。

## 边界确认

- 仅修改 `agate/scripts/agate-debt-check.py` 一个文件；未改动任何测试、文档、卡片、规则或 `~/.agate`（稳定版开发工具）。
- 状态标记：本次全部在 worktree 协议仓库内完成，未触达生产环境/外部系统，`[PROD_NOT_TOUCHED]`。
