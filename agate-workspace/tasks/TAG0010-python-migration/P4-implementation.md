---
phase: P4
task_id: TAG0010-python-migration
type: implementation
parent: P3-test-cases.md
trace_id: TAG0010-P4-20260814
status: draft
agent: implementer
---

# P4 实现记录 — 批次 0（公共库）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 agate/scripts/agate_common.py

按 P2 §3.1 模块设计实现，替代 `gate-result.sh` + `agate-workspace-resolve.sh` 的函数库：

- **数据流函数（gate-result.sh 迁移）**：
  - `write_gate_result(phase, task_id, exit_code, output)`：写 `.gate-result.json`（结构不变）+ 追加 `.gate-history.jsonl`；`output` 用 `json.dumps` 转义（替代 agate-json-get.py escape）；`prev_commit_sha` 用 `git rev-parse HEAD`（失败回退 "pre-commit"）
  - `read_state_phase(state_file)` / `read_state_task_id(state_file)`：yaml.safe_load 读 frontmatter，文件不存在返回 `""`
  - `has_staged_phase_change(state_file)`：`git diff --cached --name-only` + `line.rstrip("\r")` + `^\+.*phase:` 检查
  - `has_staged_phase_output()`：staged 文件名匹配 `P[0-9]+-.*\.(md|yaml)$`
  - `resolve_formatter(fmt, task_dir=None, agate_root=None)`：绝对路径 → `task_dir/.agate/formatters/` → `agate_root/assets/formatters/`
  - `run_test_with_formatter(cmd, fmt_path, timeout_secs=None)`：subprocess 超时 + JSON 结构（含 raw_output），保留 exit 124 语义
- **工作区解析（agate-workspace-resolve.sh 迁移）**：
  - `resolve_workspace(project_root)`：`.agate.env` → env `AGATE_TASKS_DIR` → 默认 `{root}/agate-workspace`；`Path.resolve()` 归一；utf-8 + CRLF 剥离
  - 执行模式 main：`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出（bats 直调契约）
- **hook 公共工具**：
  - `resolve_agate_root(script_path)`：readlink 解析 + 复制模式 `.agate-root` 恢复
  - `probe_python()`：python3 → python（shutil.which）
  - `run_git(args, cwd=None)`：subprocess 封装，utf-8 + errors=replace，返回 (returncode, stdout)

### 修改 agate/scripts/ci-gate-backstop.py

- `resolve_tasks_dir` 改调 `agate_common.resolve_workspace`（消除对 agate-workspace-resolve.sh 的 bash subprocess）；`ImportError` 时退回 env/default（旧 AGATE_ROOT 向后兼容，同原 fallback 语义）
- `_find_bash`/`_bash_cmd` **保留不动**（批次 2 随各被调脚本 py 化才删）；`run_gate` 的 check-gate.sh → check-gate.py 切换**不做**（批次 2）

### 修改 3 个 bats 文件

- `unit/agate-workspace-resolve.bats`：10 处调用 `bash agate-workspace-resolve.sh` → `"$PYTHON" agate_common.py`；两行输出契约与 CRLF 剥离（bdd-18）断言保留
- `unit/helpers-python.bats`：bdd-17 重构为 `agate_common.probe_python` 语义（python3→python 回退 + 无 python 返回空 → fail-closed 阻断）；bdd-13/15 断言保留
- `unit/ci-gate-backstop.bats`：workspace 解析相关断言改后绿（调用方式本就为 py，断言体不变；本批次确认改后绿）

## 自查结果（自查 ≠ P5 gate）

- `bats unit/agate-workspace-resolve.bats`：10/10 绿
- `bats unit/helpers-python.bats`：3/3 绿
- `bats unit/ci-gate-backstop.bats`：11/11 绿
- 全量 `bats agate/tests/unit/`：625/625 绿
- `count-tests.sh`：727 不漂移
- `check-protocol-consistency.py`：0 ERROR
- `agate-scripts-encoding.bats` bdd-5：新 py 全部显式 encoding=utf-8 通过
- `py_compile`：agate_common.py / ci-gate-backstop.py 均编译通过

## 边界与实现说明

- `write_gate_result` 的 JSON 字段结构完整复刻 gate-result.sh（phase/task_id/exit_code/timestamp/output/runner/prev_commit_sha），history 行字段同 sh（phase/task_id/exit_code/timestamp/prev_commit_sha）
- `run_test_with_formatter`：用 subprocess `timeout` 参数替代 GNU timeout 二进制探测（行为等价：保留 exit 124 超时语义）；stdout/stderr 合并（stderr=STDOUT）；formatter 用 `bash <fmt_path> <exit_code>` 子进程调用（formatters 仍为 sh，非本批次迁移对象）
- `resolve_workspace` 不创建任何目录（同 agate-workspace-resolve.sh 边界）
- pyyaml fail-closed：模块顶部 try/except ImportError → stderr 提示 + exit 1（同 agate-state-get.py L18-21 模式）
- Python 3.8+ 兼容：无 match / str.removeprefix；全部文件读写显式 `encoding="utf-8"`

## DESIGN_GAP

[DESIGN_GAP: P2 §3.1 写 "gate-result.json（6 字段结构不变）"，但 gate-result.sh 实际写 7 字段（phase/task_id/exit_code/timestamp/output/runner/prev_commit_sha）。实现按 sh 实际结构保留 7 字段（CLI 契约"结构不变"的判定对象是 sh 现状，ci-gate-backstop 读 phase/exit_code/timestamp/prev_commit_sha 均不受影响），未按"6 字段"裁剪]

## 已知后续（不在本批次）

- `_bash_cmd`/`_find_bash` 于批次 2 随 check-gate.py / check-tdd-red.py / check-p6-provenance.py 落地逐个删除
- 批次 3 薄壳 `resolve_agate_root` / `probe_python` 供 pre-commit-gate.py 等复用
- gate-result.sh / agate-workspace-resolve.sh 的 sh 版本在本批次保留（批次 1-3 各调用方 py 化后才删档）
