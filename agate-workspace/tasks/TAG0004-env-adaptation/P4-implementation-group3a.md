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

# P4 实现记录 — 组 3a（py encoding + M6 容错组）

## 改动清单

**S3（BDD-5..8）：13 个 py 文本 open() 加 `encoding="utf-8"`（20 处，含读写）**

| 文件 | 行号（改动前） | 改动 |
|------|--------------|------|
| `agate-card-inject.py` | 13 / 15 / 28 | 3 处 `open()` 加 `encoding="utf-8"`（读 2 + 写 1） |
| `agate-changelog-unreleased.py` | 8 | 1 处读 |
| `agate-evidence-consistency.py` | 21 / 30 | 2 处读 |
| `agate-gate-missing-cmds.py` | 12 | 1 处读 |
| `agate-gate-p5-count.py` | 11 | 1 处读 |
| `agate-md-field-get.py` | 112 | 1 处读 |
| `agate-read-gate-commands.py` | 16 | 1 处读 |
| `agate-read-p5-commands.py` | 18 | 1 处读 |
| `agate-retreat-state.py` | 28 / 42 / 49 | 3 处（读 2 + 写 1，写保留 allow_unicode 语义） |
| `agate-state-get.py` | 25 | 1 处读 |
| `agate-state-yaml-check.py` | 21 | 1 处读 |
| `agate-vision-blocker.py` | 17 | 1 处读 |
| `ci-gate-backstop.py` | 51 / 118 / 180 | 3 处读 |

`agate-image-check.py` 的 `Image.open` 为二进制图片读取，不在范围内（BDD-5 断言正则已排除）。

**M6（BDD-14..16，py 侧）：frontmatter 提取入口 CRLF 归一**

- `agate-md-field-get.py` `_read()`：`f.read()` → `f.read().replace("\r\n", "\n")`
- `agate-frontmatter-check.py` `main()` 读取处：`f.read()` → `f.read().replace("\r\n", "\n")`

不改 `.gitattributes`（BDD-16 守卫）。shell 侧（`check-gate.sh` P1/P2 review status 提取、`check-frontmatter.sh` 链路）由组 1/2 负责。

> 注：`agate-frontmatter-check.py` 不在 dispatch 约束节的"13 个 py"清单中，但 M6 目标与实现要点、P2-design §4 files_to_read（`agate-frontmatter-check.py:122-129`，M6 CRLF 归一）均明确指向该文件，且其 `open()` 已带 `encoding="utf-8"`（不在 S3 清单）。故按 M6 范围修改，特此说明。

## 自查结果（自查 ≠ P5 gate）

- `bats agate/tests/unit/agate-scripts-encoding.bats`：**2/2 绿**（bdd-5 断言审计 红→绿，bdd-8 ASCII 回归绿）
- `bats agate/tests/unit/agate-md-field-get.bats`：**12/12 绿**（bdd-6 中文读 绿，bdd-15 LF 回归 绿）
- `bats agate/tests/unit/agate-retreat-state.bats`：**4/4 绿**（bdd-7 中文写 绿）
- 补充：`check-frontmatter.bats` 14/14 绿；`agate-state-get.bats`/`agate-state-yaml-check.bats`/`agate-card-inject.bats` 全绿；14 个 py `py_compile` 全过
- CRLF 手工验证：CRLF 行尾的 P1.md 经 `agate-md-field-get.py` 正确返回 `risk_level=high`；CRLF `.state.yaml` 经 `agate-state-get.py` 正确返回 phase
- `check-gate.bats` bdd-14 仍红：该用例测试 `check-gate.sh`（shell 侧 M6），属组 1/2 范围，本组未改

## 回归守卫（BDD-6/7/8/15）

全部保持绿（见上自查）。

## 说明标记

- `[SCOPE_GAP]` 无：13 个 py + M6 目标文件（`agate-frontmatter-check.py`）均已按 P2/dispatch 实现
- `[DESIGN_GAP]` 无
- `[CLARIFY]` 无
- `[PROD_NOT_TOUCHED]` 本阶段仅修改 worktree 内 `agate/scripts/` 下 14 个 py 文件并跑 bats，未接触任何生产环境。

## 门槛自检

- P4-implementation-group3a.md 存在且含 Header + `implementation_dir: agate/scripts/` ✓
- 14 个 py 已落盘（git diff 22+/22-，含 encoding= 与 CRLF 归一）✓
- BDD-5 红→绿（agate-scripts-encoding.bats）；BDD-14 为 shell 侧（组 1/2）✓
- BDD-6/7/8/15 回归守卫绿 ✓
- 无 [SCOPE_GAP] ✓
