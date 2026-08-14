---
phase: P4
task_id: TAG0011-test-migration
type: implementation
parent: P2-design.md
trace_id: TAG0011-P4-20260815
status: draft
created: 2026-08-15
agent: implementer
change_type: refactor
implementation_dir: agate/tests/
---

# P4 实现记录 — agate 测试框架迁移（bats → pytest）

> 逐批次推进（P2 §5 批次 0-16），每批一个 round。每批追加 `## 批次 N` 小节：
> 迁移清单 + 自查结果 + 偏离点（[DESIGN_GAP] / [SCOPE+] / [CLARIFY]）。

## 批次 0 — pytest 基座（3 文件 / 16 用例；交付 conftest.py + pyproject）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（新建） | 用例数 |
|--------------------------|---------------------|--------|
| `agate/tests/helpers/load.bash` + `fixtures.bash` + `git-helper.bash`（526 行） | `agate/tests/conftest.py` | — |
| `agate/tests/sanity.bats` | `agate/tests/test_sanity.py` | 6 |
| `agate/tests/unit/agate-workspace-resolve.bats` | `agate/tests/unit/test_agate_workspace_resolve.py` | 10 |
| `pyproject.toml`（追加 `[tool.pytest.ini_options]` + ruff src 扩展） | — | — |

### conftest.py 交付内容（P2 §3.1 / P3 §5.1 全量核心 fixture）

- **会话级**：`agate_root`（AGATE_ROOT env 覆盖优先 + `_resolve_agate_root` 反推 + fail-closed）、
  `agate_scripts` / `agate_assets`、`python_exe`（python3→python 探测，fail-closed）、`load_fixture`（静态夹具加载）
- **函数级**：`task_dir`（create_task_dir 等价 factory，参数 phases / risk_level / with_evidence /
  no_state_yaml / legacy_fields）、`git_repo`（GitRepo 类：git_init + `.commit/.stage/.staged_diff/.staged_files/.git`）、
  `run_cli`（`_run_cli_impl` 实现 + fixture 暴露）、`py_path`（cygpath -m / Linux 恒等）
- **纯函数**（`from conftest import`）：`create_task_dir` / `add_agent_field` / `add_given_line` /
  `add_frontmatter_field` / `add_pruning_excuse` / `add_p1_field` / `add_p2_candidate_count` /
  `add_p2_review` / `add_evidence_file` / `add_p6_pass` / `add_p6_fail` / `add_p6_need_confirm` / `add_p1_bdd`
- **`CommandResult.output`** = stdout + stderr 合并流 property（bats `$output` 语义，P2 BLOCKER-1 修复）
- **退役机制**：`create_python_shim_bin` 未迁移（pytest 直跑解释器，P1 §6.1）；bats 源文件保留不删（BDD-6 双跑对照）

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/test_sanity.py agate/tests/unit/test_agate_workspace_resolve.py -q
# 16 passed in 0.44s（6 sanity + 10 workspace-resolve，全绿）
python3 -m pytest agate/tests/ -k "sanity or helpers or workspace" -q   # P3 §6 批次 0 验证命令
# 16 passed in 0.42s
ruff check agate/tests/conftest.py agate/tests/test_sanity.py agate/tests/unit/test_agate_workspace_resolve.py
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py <三个新文件>
# exit 0（R1-R5 零命中）
encoding 守卫（bdd-5 逻辑）
# 零违规
```

- windows_smoke 打标：`test_sanity_1`（每文件第 1 用例）+ `test_wr_1`（每文件第 1 用例）+
  `test_bdd_18`（CRLF 平台关键词，P3 §5.2 表 W）——共 3 处
- 流语义：workspace-resolve 两行输出契约走 stdout（`_ws_out`/`_tasks_out` 从合并流提取，与 bats 一致）；
  本批无 `[ -z "$output" ]` 空断言（26 处分布在批次 1/2/5/7/12/16）

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：`run_cli` 实现函数命名 `_run_cli_impl`（fixture `run_cli` 返回之——
  Python 模块内 `@pytest.fixture def run_cli` 会遮蔽同名模块函数，直接 `return run_cli` 会返回 fixture 自身
  导致 "Fixture called directly"）；`pyproject.toml` 另补 `[tool.pytest.ini_options] testpaths=["agate/tests"]`
  与 `[tool.ruff] src` 扩展 `["agate/scripts", "agate/tests"]`（P2 §2 影响域要求）。
- helpers-python.bats（3 用例）不在本批迁移（P4 批次 0 派发范围仅 3 文件）；`python_exe` fixture 已按
  P2/P3 交付其语义，`test_helpers_python.py` 留待对应批次。
