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

## 批次 1 — 纯工具无 git（5 文件 / 11 @test + 1 回归锁 + helpers-python 3）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（新建） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/agate-changelog-unreleased.bats` | `unit/test_agate_changelog_unreleased.py` | 2 |
| `unit/agate-card-inject.bats` | `unit/test_agate_card_inject.py` | 2 |
| `unit/agate-evidence-consistency.bats` | `unit/test_agate_evidence_consistency.py` | 2 |
| `unit/agate-gate-missing-cmds.bats` | `unit/test_agate_gate_missing_cmds.py` | 2 |
| `unit/agate-gate-p5-count.bats` | `unit/test_agate_gate_p5_count.py` | 3 + 1 流语义回归锁 |
| `unit/helpers-python.bats` | `unit/test_helpers_python.py` | 3（P4 review 跟踪项） |

### 关键实现点

- **合并流（P2 BLOCKER-1）**：3 处 `[ -z "$output" ]`（CL.2 / EC.2 / GMC.2）→ `assert result.output == ""`；
  `[[ "$output" == *"X"* ]]` → `assert "X" in result.output`；精确等值（GPC 的 `"1 2"` 等）→ `.strip()`
  后再比较（`$(...)` 剥尾部换行 vs subprocess 保留，P2 §3.2 精确等值注意）。
- **流语义回归锁**（`test_stream_lock_stderr_hits_merged_output`）：无占位符时 agate-card-inject.py 写
  `注入失败` 到 **stderr** 并 exit 1 —— 先断言 `"注入失败" in result.stderr`（流归属）+ `not in result.stdout`，
  再断言 `"注入失败" in result.output`（合并流命中），等价 EB.8 的"stderr WARNING + $output 合并流断言"。
- **helpers-python**：`create_python_shim_bin` 退役（P2 §3.1）——bdd-13 改用 `python_exe` fixture 语义
  （探测到 + `--version` 可执行，输出含 "Python"）；bdd-15/17 直接测产品代码 `agate_common.probe_python`
  （python3→python 回退 + 无 python 返回空 fail-closed），fakebin 目录跨平台构造（Windows 复制为
  `python.exe` / Linux 复制为 `python`，`shutil.copyfile` + `os.chmod`）。
- run_cli 全部走 conftest fixture（`agate_scripts` / `python_exe` / `run_cli` / `tmp_path`），
  env 经 `run_cli(..., env=...)` 传入（等价 bats `KEY=value $PYTHON ...` 前缀）。
- windows_smoke 打标（P3 §5.2 表 W + 每文件第 1 用例）：`test_cl_1` / `test_ic_1` / `test_ec_1` /
  `test_gmc_1` / `test_gpc_1` / `test_bdd_13`（每文件第 1）+ `test_bdd_15`（平台关键词"无 python3"）——共 7 处。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_agate_changelog_unreleased.py agate/tests/unit/test_agate_card_inject.py agate/tests/unit/test_agate_evidence_consistency.py agate/tests/unit/test_agate_gate_missing_cmds.py agate/tests/unit/test_agate_gate_p5_count.py agate/tests/unit/test_helpers_python.py -q
# 15 passed in 0.42s（2+2+2+2+4+3，全绿）
python3 -m pytest agate/tests/unit/ -k "changelog or card or evidence or gate_missing or gate_p5" -q   # P3 §6 批次 1 验证命令
# 12 passed, 13 deselected（helpers_python 不在该 -k 契约内，属预期）
/home/kity/.venvs/agate-dev/bin/ruff check <6 个新文件>
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py <6 个新文件>
# exit 0（R1-R5 零命中）
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：bdd-15（bats 测已退役的 `fixtures.bash detect_python`）在
  pytest 迁移中直接测产品代码 `agate_common.probe_python`（当前唯一的探测实现，P3 §4 批次 0 口径），
  与 bdd-17 的 PATH 回退场景部分重叠，但 bdd-15 焦点为"回退解析"、bdd-17 焦点为"无 python fail-closed"，
  各自独立成立。

## 批次 2 — 共享工具（6 文件 / 39 @test）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（新建） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/agate-json-get.bats` | `unit/test_agate_json_get.py` | 8 |
| `unit/agate-md-field-get.bats` | `unit/test_agate_md_field_get.py` | 14 |
| `unit/agate-state-get.bats` | `unit/test_agate_state_get.py` | 6 |
| `unit/agate-retreat-state.bats` | `unit/test_agate_retreat_state.py` | 4 |
| `unit/agate-state-yaml-check.bats` | `unit/test_agate_state_yaml_check.py` | 3 |
| `unit/agate-read-p5-commands.bats` | `unit/test_agate_read_p5_commands.py` | 4 |

### 关键实现点

- **合并流（P2 BLOCKER-1）**：7 处 `[ -z "$output" ]`（JGET.7 / STGET.2 / STGET.6 / RSTATE.2 / SY.1 合法态 /
  P5C.2 / P5C.3）→ `assert result.output.strip() == ""`
  （`.strip()` 兜底：bats `$output` 剥尾部换行，pytest subprocess 保留 `print("")` 产生的 `\n`）。
- **精确等值**：bats `[[ "$output" == "2" ]]` 等（JGET.1/3/4/6、MDF 全字段、STGET.1/3/4、RSTATE.1）
  → `assert result.output.strip() == "2"`（同上换行差，P2 §3.2 精确等值注意）；STGET.5 前缀断言
  `"P1=3 (MAX=3)" in result.output`；JGET.5/7、SY.2/3、P5C.1/4 的包含断言直接 `in result.output`。
- **stdin 管道**：JGET 全部 op + STGET.3 用 `run_cli(..., input=...)`（JGET.8 输入含真实换行
  `'a"b\nc'`，断言 `'a\\"b' in result.output`）；bats `echo '...' | ...` 管道等价。
- **env 传参**：JGET.5/6 `PROJECT_MODULE`、STGET/RSTATE/SY 的 `STATE_FILE`、RSTATE 的 `CUR/TGT/
  NEW_PHASE/RETREAT_REASON`、MDF 的 `FILE`、P5C 的 `P2_DESIGN` 全部经 `run_cli(..., env=...)`
  （等价 bats `KEY=value $PYTHON ...` 前缀）。
- **多段 run 单用例**：SY.1（TAG0001 通过 + T001 拒绝两段 run 同 @test，P2-review FIND 要求）在单个
  test 函数内写两次 `.state.yaml` + 两次 run_cli。
- **文件回写断言**：RSTATE.3 / bdd-7（bats `run cat .state.yaml` 后断言合并流）→ 直接
  `state_file.read_text(encoding="utf-8")` 断言内容（`phase: P3` / `attempt: 2` / 中文 reason）。
- windows_smoke 打标（P3 §5.2：本批 6 文件无平台关键词用例，仅每文件第 1 用例）：
  `test_jget_1` / `test_mdf_1` / `test_stget_1` / `test_rstate_1` / `test_sy_1` / `test_p5c_1`——共 6 处。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_agate_json_get.py agate/tests/unit/test_agate_md_field_get.py agate/tests/unit/test_agate_state_get.py agate/tests/unit/test_agate_retreat_state.py agate/tests/unit/test_agate_state_yaml_check.py agate/tests/unit/test_agate_read_p5_commands.py -q
# 39 passed in 1.13s（8+14+6+4+3+4，全绿）
python3 -m pytest agate/tests/unit/ -k "json or md_field or state_get or retreat_state or state_yaml or read_p5" -q   # P3 §6 批次 2 验证命令
# 39 passed, 25 deselected（-k 契约命中 6 文件全数）
/home/kity/.venvs/agate-dev/bin/ruff check <6 个新文件>
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py <6 个新文件>
# exit 0（R1-R5 零命中）
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：空断言统一 `result.output.strip() == ""` 而非设计表的
  `result.output == ""`——因被测脚本空值路径多走 `print("")`（stdout 为 `"\n"`），bats `$output` 剥尾部
  换行后为空，`.strip()` 才与 bats 语义逐位一致（批次 1 的 GMC.2 空路径是零 print，`== ""` 恰好等价，
  本批 STGET.2 / MDF.8/10/11/12 / JGET.2 必须 strip，统一口径更稳）。
