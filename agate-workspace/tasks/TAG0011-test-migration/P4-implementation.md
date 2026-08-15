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

## 批次 3 — 内容生成工具（3 文件 / 53 @test）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（新建） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/agate-next-card.bats` | `unit/test_agate_next_card.py` | 22（9 个 sha256 字节稳定性断言） |
| `unit/agate-inject-card.bats` | `unit/test_agate_inject_card.py` | 11 |
| `unit/agate-render-dispatch-prompt.bats` | `unit/test_agate_render_dispatch_prompt.py` | 20 |

### 关键实现点

- **sha256 字节稳定性（next-card 9 处 P0-P8）**：CLI body sha256 == 卡片文件 sha256——body 提取用
  `splitlines(keepends=True)` 按行保留字节（等价 `tail -n +5 | sha256sum`，不丢尾部换行），与
  `card_file.read_bytes()` 的 sha256 逐位比对（P2 §3.2 精确等值注意）；字节稳定性/跨 checkout 用全量
  hash（`_full_sha256`）。
- **合并流（P2 BLOCKER-1）**：失败路径的 `GATE: ...` 消息（`需要 1 个参数` / `不在 P0-P8 范围内` /
  `不存在` / `角色文件不存在` / agate-card-inject 占位符错误）由脚本写 **stderr**，bats `$output` 合并流
  断言 → 一律 `in result.output`；`未找到/占位符` 双关键词用 `or`（bats 的 `[[ ... ]] || [[ ... ]]`）。
- **文件写入断言用 read_text 对照**（P2 §3.2）：inject 的块 sha256 / 内容不变 / grep 旧 / RP.11 渲染产物
  header → 直接读文件断言，等价 bats `sed` 管道 + `run cat`。
- **IC_IDEMPOTENT.2 临时改写真实卡片**：备份 `phase-cards/P3-tdd.md` 字节 → 追加两行 → 重注入 → `finally`
  写回备份（等价 bats `cp` 备份 + 恢复；实测 git diff 无残留，pytest 串行执行无竞态）。
- **平台分支（AGENTS.md 测试约定）**：next-card symlink / 跨 checkout 用例按平台构造链接（Linux
  `os.symlink`；Windows 复制模式 `shutil.copyfile` + 显式 `AGATE_ROOT` env 兜底，等价 Git Bash `ln -sf`
  退化为复制）；bdd-21（Windows 盘符）在 Windows 上 `pytest.skip`（bats 同名 skip 语义），Linux 用字面
  反斜杠目录 `C:\proj\agate` 全覆盖。
- windows_smoke 打标（P3 §5.2 表 W + 每文件第 1 用例）：`test_nc_p0_...` / `test_nc_symlink_...` /
  `test_bdd_21`（表 W 的 2 个平台关键词 = symlink + Windows 盘符，加第 1 用例共 3）、`test_icb_1`、
  `test_rp_1`——共 5 处。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_agate_next_card.py agate/tests/unit/test_agate_inject_card.py agate/tests/unit/test_agate_render_dispatch_prompt.py -q
# 53 passed in 2.10s（22+11+20，全绿）
python3 -m pytest agate/tests/unit/ -k "next_card or inject_card or render_dispatch" -q   # P3 §6 批次 3 验证命令
# 54 passed, 63 deselected（-k 契约命中 3 文件全数 + 批次 1/2 的 card/gate_p5 关联命中，重叠无害）
/home/kity/.venvs/agate-dev/bin/ruff check <3 个新文件>
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py <3 个新文件>
# exit 0（R1-R5 零命中）
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：
  - next-card 9 个 P0-P8 sha256 @test 各写独立 test 函数（1 @test → 1 test 函数，P0 独立打标
    windows_smoke），共用 `_assert_body_matches` helper。
  - IC_IDEMPOTENT.2 的 first_hash/second_hash 用 `_between_markers` 的 join（无尾部换行）与 bats 的
    sed 管道（带尾部换行）数值不同，但断言是**相对不等**（first != second），双跑对照语义等价。
  - inject 块 sha256 断言对 `\r` 归一化（`replace("\r","")`，等价 `tr -d '\r'`）后再哈希。

## 批次 4 — 上下文/归档/回退工具（4 文件 / 37 @test）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（新建） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/agate-extract-context.bats` | `unit/test_agate_extract_context.py` | 16 |
| `unit/agate-archive-stale-outputs.bats` | `unit/test_agate_archive_stale_outputs.py` | 7 |
| `unit/agate-migrate-workspace.bats` | `unit/test_agate_migrate_workspace.py` | 9 |
| `unit/agate-retreat-to.bats` | `unit/test_agate_retreat_to.py` | 5 |

### 关键实现点

- **合并流（P2 BLOCKER-1）**：EC.9 `已追加到`（stdout print）/ MW.5 `迁移` / ARCH.2 `无需归档`
  / RETREAT.1 `共 2 步` 等包含断言一律 `in result.output`；错误/超限消息（EC.2/3、RETREAT.2/3/4/5）
  由脚本写 stderr——按 §3.2 先判流归属后用合并流 `.output` 断言（与 bats `$output` 等价，双跑对照不漂移）。
- **ARCH.4 flaky（时间戳）**：归档目录名含秒级时间戳 `{YYYYmmdd-HHMMSS}-{PHASE}`——两次归档之间
  `time.sleep(1)` 保证时间戳必然不同，隔离单跑必过语义保留（P2 §7.2 R2.4）。查归档目录用
  `_archived_dirs()` glob 等价（`find .archived -name "*-P6"`）。
- **git_repo fixture**：migrate-workspace（9 例）+ retreat-to（5 例）全部用 `git_repo`（git_init 等价），
  `run_cli(..., cwd=str(git_repo.path))` 等价 bats `cd '$repo'`；git 断言经 `git_repo.git(...)`（`git -C` 等价），
  MW.3/MW.9 的 `git log --follow` 用 `git_repo.git("log", "--follow", "--oneline", "--", path)`。
- **MW.9 hook 集成**：`_install_pre_commit_hook()` 用 `os.symlink` + Windows 复制模式 fallback
  （`shutil.copyfile`，等价 Git Bash `ln -sf` 退化）安装 pre-commit 钩子；hook-liveness probe 经
  `git_repo.git("commit", ...)` 断言 returncode != 0（等价 bats `[ "$status" -ne 0 ]`）+ `reset -q`。
- **RETREAT.3 计数**：`git log --oneline | wc -l` → `len([非空行 in git_repo.git("log","--oneline").stdout])`。
- **MW.8 仓库外目标**：`--to` 外部工作区用 `tmp_path.parent / (tmp_path.name + "-ext-ws")`（repo 之外），
  git mv 失败 exit 128 → fallback 普通 mv + `WARNING` 断言。
- **EC.16 无 bc 模拟**：fakebin 前置 `bc` stub（exit 1）+ `env={"PATH": fakebin + os.pathsep + 原 PATH}`
  （等价 bats `env PATH="$fakebin:$PATH"`）；断言 P6 failed 求和仍为 3。
- windows_smoke 打标（P3 §5.2 表 W + 每文件第 1 用例）：`test_ec_1`（第 1）+ `test_ec_16`（平台关键词
  "无bc"）、`test_arch_1`、`test_mw_1`、`test_retreat_1`——共 5 处。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_agate_extract_context.py agate/tests/unit/test_agate_archive_stale_outputs.py agate/tests/unit/test_agate_migrate_workspace.py agate/tests/unit/test_agate_retreat_to.py -q
# 37 passed in 4.03s（16+7+9+5，全绿）
python3 -m pytest agate/tests/unit/ -k "extract or archive or migrate or retreat" -q   # P3 §6 批次 4 验证命令
# 43 passed, 111 deselected（37 本批 + 6 retreat_state 关联命中，重叠无害）
/home/kity/.venvs/agate-dev/bin/ruff check <4 个新文件>
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py <4 个新文件>
# exit 0（R1-R5 零命中）
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：RETREAT 的 `_init_task_repo` 等价 bats setup 的目录 +
  git commit 结构，`retries_yaml` 用 f-string 注入（ruff UP032 要求）；MW.8 外部工作区目录建在
  `tmp_path` 之外（repo 外才触发 git mv 失败 fallback），命名加 `tmp_path.name` 后缀防跨测试冲突。

## 批次 5 — 环境/债务/编码守卫（4 文件 / 42 @test）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（新建） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/agate-capture-env-baseline.bats` | `unit/test_agate_capture_env_baseline.py` | 15 |
| `unit/agate-debt-check.bats` | `unit/test_agate_debt_check.py` | 21 |
| `unit/agate-image-check.bats` | `unit/test_agate_image_check.py` | 4 |
| `unit/agate-scripts-encoding.bats` | `unit/test_agate_scripts_encoding.py` | 2 |

### 关键实现点

- **ENV_BASELINE 流归属先判流（P2 §3.2）**：capture-env-baseline 的 `ENV_BASELINE:` / `已捕获` /
  `复用缓存` / `本身崩溃` / `不一致` / `无 formatter` / `非 git 仓库` 等消息一律 `sys.stderr.write` →
  断言用 `result.stderr`；EB.1 no-op 零输出用合并流 `result.output`（BLOCKER-1）。
- **GATE DEBT WARNING 先判流**（dispatch 约束）：check-debt.py 的错误行 / `GATE DEBT WARNING` /
  `缺少 agate_common` 均写 stderr → 用 `result.stderr`。
- **5 处 `[ -z "$output" ]` 合并流**（bdd_5 / bdd_10 三子场景 / bdd_11 成功零输出）→
  `assert result.output == ""`（合并流 `.output`，BLOCKER-1；成功路径 stdout+stderr 均空）。
- **fake runner 机制**：`_write_fake_runner` / `_write_recording_runner` 在 tmp_path 写可执行 bash
  脚本（cat heredoc 输出 + exit code），P2-design.md 的 P5 命令指向该脚本，等价 bats
  make_fake_runner / make_recording_runner；`run_test_with_formatter` 的 `bash` shell=True 执行路径
  复用 agate/assets/formatters/{pytest,vitest}.sh 原样解析。
- **git_repo fixture**：capture-env 的 EB.4-15 全部走 git_repo（git init + P2-design.md commit +
  `git log`/`rev-parse` 断言）；EB.5 缓存命中用 recording runner 的 sentinel 文件（rm 后断言不再出现）；
  EB.6 commit 变化 / EB.7 命令集合变化 → 缓存 miss。
- **EB.11 非 git 模拟**：`env={"GIT_DIR": <tmp_path 下不存在 .git>}` 等价 bats `GIT_DIR=/nonexistent/.git`，
  git rev-parse 失败 → `非 git 仓库`。
- **debt-check schema 用例**：bdd_5..bdd_11 逐条复制 bats heredoc 的 yaml fenced 块（open 无 task_id /
  closed 含 task_id+P5/P6 证据 / 三态 / 向后兼容纯正文 / T001 回填 T1-T4+A5），断言 returncode + stderr 字段。
- **debt retreat-coverage**：bdd_13-15 用 git_repo + `--allow-empty` retreat 提交（消息格式含
  `retreat: P5 -> P4（诊断：...）`），evidence 引用 rev-parse --short 哈希；bdd_16 复制 check-debt.py
  到隔离目录模拟缺 agate_common → exit 2。
- **Pillow 可选**：模块级 `try: from PIL import Image` 探测 HAS_PIL；IMG.1/IMG.3（无 Pillow 分支）用
  `@pytest.mark.skipif(HAS_PIL)`，IMG.4（需 Pillow 造图）用 `@pytest.mark.skipif(not HAS_PIL)`，
  IMG.2 恒跑（-1 或 SKIP_NO_PILLOW 双值皆可）；运行时造图用 tmp_path（`os.urandom`/`write_bytes`，
  不写字面命中行）；收集数 4 不受影响（本机 Pillow 已装 → 2 pass + 2 skip）。
- **encoding 守卫（bdd-5）**：扫描目标随迁移改为 `agate/tests/**/*.py`（P3 批次 5 口径，BDD-7）——
  本文件及全部 test_*.py 自身受检；守卫正则复刻 bats（`(?<!Image\.)\bopen\(` 豁免 Image.open、
  `"rb"`/`"wb"` 豁免二进制、注释/三引号行跳过）。**本文件 assert 消息改为 `"text I/O 缺 encoding"`
  避免自命中字面 `open(`（bats 时代只扫 scripts/*.py 不扫自身，pytest 时代全树受检，这是迁移触发的
  必要改写，语义不变）。** bdd-8 为 agate-state-get.py ASCII .state.yaml 读取回归（STATE_FILE env）。
- windows_smoke 打标（每文件第 1 用例）：`test_eb_1` / `test_bdd_1` / `test_img_1` / `test_bdd_5`——
  共 4 处（本批无平台关键词用例，P3 §5.2 表 W 未列）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_agate_capture_env_baseline.py agate/tests/unit/test_agate_debt_check.py agate/tests/unit/test_agate_image_check.py agate/tests/unit/test_agate_scripts_encoding.py -q
# 40 passed, 2 skipped in 2.77s（42 collected；skip 为 IMG.1/IMG.3 无 Pillow 分支——本机 Pillow 已装）
python3 -m pytest agate/tests/unit/ -k "capture_env or debt or image or encoding" -q   # P3 §6 批次 5 验证命令
# 40 passed, 2 skipped, 154 deselected（-k 契约命中 4 文件全数）
python3 -m pytest agate/tests/unit/test_agate_capture_env_baseline.py agate/tests/unit/test_agate_debt_check.py agate/tests/unit/test_agate_image_check.py agate/tests/unit/test_agate_scripts_encoding.py --collect-only -q
# 42 tests collected（BDD-1 计数不变）
/home/kity/.venvs/agate-dev/bin/ruff check <4 个新文件>
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py <4 个新文件>
# exit 0（R1-R5 零命中）
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：
  - encoding 守卫 assert 消息从 `open()/read_text() 缺 encoding` 改为 `text I/O 缺 encoding`——迁移后
    bdd-5 扫 `agate/tests/**/*.py`（含本文件自身），消息字面 `open(` 会被守卫自命中；bats 时代守卫只扫
    `scripts/*.py` 不扫测试文件故未暴露。断言语义（violations 非空即失败 + 前 30 条拼接）不变。
  - EB.11 非 git 模拟用 tmp_path 下不存在路径而非 bats 的 `/nonexistent/.git` 字面（平台无关纪律，
    R4 只查 `/tmp` 不查 `/nonexistent`，此处为主动保守）。
  - IMG.1/IMG.3 的 skip 条件与 bats 相反方向呈现：bats 在 PIL 已装时 skip，pytest 用
    `skipif(HAS_PIL)` 等价；IMG.4 用 `skipif(not HAS_PIL)`（bats 在无 PIL 时 skip）。收集数 4 不受影响。

## 批次 6 — check 状态/裁剪/scope（3 文件 / 69 @test）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（新建） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-state-transition.bats` | `unit/test_check_state_transition.py` | 30 |
| `unit/check-pruning.bats` | `unit/test_check_pruning.py` | 29 |
| `unit/check-scope-resolved.bats` | `unit/test_check_scope_resolved.py` | 10 |

### 关键实现点

- **流语义（P2 §3.2 / 派发约束，BLOCKER-1）**：check-state-transition / check-pruning 的 gate 失败内容
  （`GATE STATE` / `GATE PRUNING` / `缺 risk_level` / `P2 不可裁剪` / `隐式耦合` 等）由脚本写
  **stderr** → 断言一律用合并流 `result.output`（与 bats `$output` 等价），未映射 `.stdout`。
- **state-transition cwd + subprocess 样板**（派发约束）：`_run_state` = `run_cli(python_exe,
  str(agate_scripts / "check-state-transition.py"), state_arg, cwd=str(repo))` 等价 bats
  `cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/check-state-transition.py' <state>`；`git_repo` fixture
  承接 git init/commit/stage（`git_commit` → `.commit()`，`git_stage` → `.stage()`，`git add -A` 语义一致）。
- **git show HEAD 断言依赖**：脚本经 `git ls-files --full-name` + `git show HEAD:` 取旧 phase——
  ST 全系必须真实 git 仓库，逐用例按 bats 序列复刻（写 .state.yaml → commit → 改写 phase → stage → run）。
- **ST.2 静态夹具**：`load_fixture("full-task/.state.yaml")` + `shutil.copyfile`（等价
  `cp "$AGATE_ROOT/tests/fixtures/full-task/.state.yaml"`）。
- **ST.15 双 commit**：P3 → commit → PAUSED → 再 commit → P4 staged（old_num=0 守卫：PAUSED→Pn
  恢复不被检查 1 误拦）。
- **ST.20 回退被拦截**：P3→P1 差 2 被检查 1 拦截（exit 1 PAUSED），只断言输出不含 commit gate
  消息（`产出必须已 commit` / `尚未 commit`），不断言 exit code（bats 原文如此）。
- **ST_ARCHIVE.5 P1→P0**：new_num=0 → `new_num > 0` 守卫为假 → 归档检查（检查 4）不触发，exit 0
  （与 bats 注释一致，P0 起始阶段豁免）。
- **pruning task_dir 复用**：P2.1-P2.14 用 `task_dir` factory（create_task_dir 等价）+ `add_p1_field` /
  `add_pruning_excuse`（`from conftest import ...`，frontmatter 块写入，T001 v2.0 流 A）。
- **P2.6a/6b git 源码文件数**：`git_repo` 先 commit init（README/src_*.py）再 `shutil.copytree` task 目录
  到 repo/`task` + `git_repo.stage("src_*.py")`（git pathspec glob）——避免 task 目录被 `add -A`
  卷入 init commit（bats 用 repo 外 mktemp 天然隔离，pytest 的 task_dir 建在 repo 根下，故必须在
  commit 之后创建）；`_staged_source_count` 的 `os.path.relpath` 在 cwd=repo 下 tasks_base_rel="."
  → src_*.py 不命中排除模式，6 个 → 超限。
- **P2.5 legacy_fields**：`task_dir(..., risk_level="high", legacy_fields=True)` 等价
  `--legacy-fields`（risk_level 在正文非 frontmatter，走 agate-md-field-get 正则回退）。
- **P2.52/52b YAML 块式 phases**：整文件覆盖 `_YAML_LIST_P1` 常量（复刻 bats heredoc 原文）——
  `phases` 块式列表经 agate-md-field-get `_regex_list` 块式分支解析为 "P1 P2 P4 P5 P6 P8"；
  断言只 exit 0（bats 原文）。
- **scope 排除文件名**：`P2-progress.md` / `P4-dispatch-prompt-implementer.md` /
  `P4-dispatch-context-implementer.md` 命中 `SKIP_NAME_RE`（`progress|dispatch-prompt|dispatch-context`）
  → 不触发检查，exit 0；SC.7 句中 `[SCOPE+]`（非行首）不命中 `SCOPE_PLUS_RE`。
- **SC.1/SC.3 无 task 目录/无 P1**：tmp_path 下裸目录（等价 `mktemp -d`）→ exit 2 / 有 SCOPE+ 无 P1
  → exit 1（`无 P1-requirements.md`）。
- windows_smoke 打标（每文件第 1 用例）：`test_st_1` / `test_p2_1` / `test_sc_1`——共 3 处
  （本批无平台关键词用例，P3 §5.2 表 W 未列）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_state_transition.py agate/tests/unit/test_check_pruning.py agate/tests/unit/test_check_scope_resolved.py -q
# 69 passed in 6.67s（30+29+10，全绿）
python3 -m pytest agate/tests/unit/ -k "state_transition or pruning or scope" -q   # P3 §6 批次 6 验证命令
# 70 passed, 195 deselected（69 本批 + test_agate_debt_check.py::test_bdd_4_..._scope_... 函数名含 scope 重叠，无害）
python3 -m pytest agate/tests/unit/test_check_state_transition.py agate/tests/unit/test_check_pruning.py agate/tests/unit/test_check_scope_resolved.py --collect-only -q
# 69 tests collected（BDD-1 计数不变）
/home/kity/.venvs/agate-dev/bin/ruff check <3 个新文件>
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py <3 个新文件>
# exit 0（R1-R5 零命中）
python3 -m pytest agate/tests/unit/test_agate_scripts_encoding.py -q   # encoding 守卫（BDD-7，本批文件受检）
# 2 passed
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：
  - P2.6a/6b 的 task 目录用 `task_dir` factory 建在 git repo 根下（bats 是 repo 外 `mktemp -d`），
    因此在 `git_repo.commit("init")` **之后**创建再 `copytree`，避免被 `add -A` 卷入 init commit；
    `git add src_*.py` 用 `git_repo.stage("src_*.py")`（git pathspec glob 等价 shell 展开）。
  - ST 系 `.state.yaml` 的 retries 多行段用 `_write_state` 的 `retries_block` 参数注入
    （等价 bats heredoc 原文），简单形态默认 `retries: {}`。

## 批次 7 — check 基础 gate（5 文件 / 57 @test）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（新建） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-changelog.bats` | `unit/test_check_changelog.py` | 8 |
| `unit/check-frontmatter.bats` | `unit/test_check_frontmatter.py` | 14 |
| `unit/check-state-yaml.bats` | `unit/test_check_state_yaml.py` | 9 |
| `unit/check-retrospective.bats` | `unit/test_check_retrospective.py` | 10 |
| `unit/check-p6-format.bats` | `unit/test_check_p6_format.py` | 16 |

### 关键实现点

- **合并流（P2 BLOCKER-1）**：5 处 `[ -z "$output" ]`（CF.11 / CF.14 合法校验零输出、
  RT.1 / RT.6 / RT.7 复盘无异常零输出）→ `assert result.output == ""`（合并流 `.output`，
  未映射 `.stdout`）；错误路径断言（`GATE CHANGELOG` / `GATE STATE-YAML` / `GATE RETRO` 及
  frontmatter 校验错误 print）一律 `in result.output`。frontmatter 校验器错误经 **stdout**
  print（agate-frontmatter-check.py:197 注释确认），但按派发约束「GATE 前缀断言（stderr）→
  合并流」统一用 `.output`，双跑对照不漂移。
- **git_repo fixture**：check-changelog 全 8 例用 `git_repo`（bats `git_init` + `cd "$repo"`），
  `run_cli(..., cwd=str(repo))` 等价；CHANGELOG.md 写 repo 根，脚本默认读 cwd 下 `CHANGELOG.md`。
- **run_cli env 传参**：CF 全系（14 例）用 `run_cli(python_exe, str(agate_scripts/"agate-frontmatter-check.py"),
  env={"FILE": str(file)})` 等价 bats `FILE='...' $PYTHON '.../agate-frontmatter-check.py'`；
  CF.10 用 check-frontmatter.py 薄壳（FILE 位置参数）。F13 / bdd-12 / bdd-13 用
  `env={"LC_ALL": "POSIX", "LANG": ""}` 等价 bats `env LC_ALL=POSIX LANG=` 前缀。
- **check-gate 集成用例**：RT_BDD21.1（check-gate.py P1 need_confirm_resolved 结构化匹配，
  exit 2）+ F_BDD18.1（check-gate.py P6 总结行不计入逐条计数 → 缺 P6-evidence 目录 exit 1）——
  用 `task_dir`（RT_BDD21.1 用 `no_state_yaml=True` 等价 `--no-state-yaml`）+ 复刻 bats heredoc。
- **P6 --fix 文件回写断言**：F3/F9/F10/F12/F13/F_P6FMFIX.* 全部直接
  `(td/"P6-acceptance.md").read_text(encoding="utf-8")` 断言（等价 bats `grep -q`）；
  F_P6FMFIX.1/2 的 inline `$PYTHON -c "import yaml..."` 校验改写为测试内 `yaml.safe_load`
  等价断言（frontmatter 切分 `text[:end]`，`data['pass']`/`data['fail']` 数值断言）。
- **RT.4 override 插入**：`_insert_override_after_phases` 等价 bats
  `sed -i '/^phases:/a override: P2 retained'`（逐行找 `phases:` 后插一行）。
- **RT.2/RT.5/RT.6 retries 多行段**：复刻 bats heredoc 原文（P2: 3 次触发 / P3: 2 次触发 /
  P3: 1 次不触发），`.state.yaml` 整体覆盖写。
- windows_smoke 打标（每文件第 1 用例）：`test_cl_1` / `test_cf_1` / `test_sy_1` / `test_rt_1` /
  `test_f1`——共 5 处（本批无平台关键词用例，P3 §5.2 表 W 未列）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_changelog.py agate/tests/unit/test_check_frontmatter.py agate/tests/unit/test_check_state_yaml.py agate/tests/unit/test_check_retrospective.py agate/tests/unit/test_check_p6_format.py -q
# 57 passed in 2.28s（8+14+9+10+16，全绿）
python3 -m pytest agate/tests/unit/ -k "changelog or frontmatter or state_yaml or retrospective or p6_format" -q   # P3 §6 批次 7 验证命令
# 73 passed, 249 deselected（57 本批 + 批次 1/2 的 changelog/gate_p5 等关联命中，重叠无害）
python3 -m pytest agate/tests/unit/test_check_changelog.py agate/tests/unit/test_check_frontmatter.py agate/tests/unit/test_check_state_yaml.py agate/tests/unit/test_check_retrospective.py agate/tests/unit/test_check_p6_format.py --collect-only -q
# 57 tests collected（BDD-1 计数不变）
/home/kity/.venvs/agate-dev/bin/ruff check <5 个新文件>
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py <5 个新文件>
# exit 0（R1-R5 零命中）
python3 -m pytest agate/tests/unit/test_agate_scripts_encoding.py -q   # encoding 守卫（BDD-7，本批文件受检）
# 2 passed
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：F_P6FMFIX.1/2 的 yaml 校验从 bats inline
  `$PYTHON -c` 改写为测试内 `import yaml` 直读（断言语义等价：frontmatter 仍合法 + pass/fail
  数值不变）；frontmatter 校验器错误虽确认写 stdout，仍按派发约束统一走合并流 `.output`
  （与 bats `$output` 逐位一致，避免双跑对照漂移）。

## 批次 8a — check-gate 子批 a（1 文件 / 11 @test）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（新建） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-gate.bats`（G0 / G1 / G3 / G4 / G_OTHER） | `unit/test_check_gate.py` | 11 |

> 按 P2 §5 批次 8 子批表 8a 范围迁移（G0/G1/G3/G4/G_OTHER，`-k "g0 or g1 or g3 or g4 or other"`）。
> 本子批新建 `test_check_gate.py`（check-gate.bats 124 用例迁移的目标文件），后续子批 8b-8h 继续追加。

### 关键实现点

- **run_cli 调 check-gate.py**（P2 §3.2）：`_run_gate = run_cli(python_exe, str(agate_scripts/"check-gate.py"), PHASE, TASK_DIR, cwd=...)` 等价 bats
  `'$PYTHON' '$AGATE_SCRIPTS/check-gate.py' PHASE "$dir"`；G4 系列用 `cwd=str(repo)` 等价 bats
  `bash -c "cd '$repo' && ..."`。
- **GATE 前缀合并流（P2 BLOCKER-1）**：check-gate.py 的 `GATE P0/P1/P3/P4:` 消息一律 `sys.stderr.write`
  （含 `P1-review.md 不存在` / `P3-test-cases.md 不存在` / `非 approved` / `agent=main` / `未知阶段`）——
  断言一律用合并流 `result.output`（与 bats `$output` 逐位一致），未映射 `.stdout`。
- **G0 反向断言**：bats `[[ "$output" != *"未知"* ]]` → `assert "未知" not in result.output`（合并流）。
- **G3 双段 run 单用例**：无 P3-test-cases.md → exit 1（`P3-test-cases.md 不存在`）+ 有 → exit 2
  （`check-tdd-red.sh`）两段 run 在单个 test 函数内（bats 单 @test 双 run，SY.1 同款）。
- **G4 系列 git_repo + copytree 样板**（复用批次 6 P2.6a/6b 模式）：`git_repo` fixture（init commit README）
  → `shutil.copytree(td, repo/"task")` → 按用例写 P4-review.md / src.py / config.yaml →
  `git_repo.stage(...)`（等价 `git -C "$repo" add ...`；G4.3 用 `stage(".")` 等价 `git add .`）→
  `_run_gate(..., "P4", "task", cwd=str(repo))`。
  - G4.1 只 stage `task/P4-implementation.md`（命中 `_STAGED_EXCLUDE_RE` 的 `P[0-8]-.*\.md$`）→ exit 1；
    G4.2/G4.4 stage `src.py` + `task/P4-review.md`（src.py 不在排除列表）→ exit 0；
    G4.3 stage `.`（含 src.py + config.yaml）→ exit 0；
    G4.5 无 P4-review.md → exit 1（`P4-review.md`）；G4.6 status rejected → exit 1（`非 approved`）；
    G4.7 agent=main → exit 1（`agent=main`）。
- **G_OTHER**：未知阶段 P9 → exit 2（`未知阶段`），`_run_gate(..., "P9", ...)`。
- 函数命名 `test_g0_...` / `test_g1_...` / `test_g3_...` / `test_g4_N_...` / `test_other_...`，匹配
  P2 §5 子批 8a 验证命令 `-k "g0 or g1 or g3 or g4 or other"`。
- windows_smoke 打标（每文件第 1 用例）：`test_g0_p0_no_unknown_exit_2`——共 1 处（本子批无平台
  关键词用例，P3 §5.2 表 W 未列）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_gate.py -q
# 11 passed in 0.68s（G0+G1+G3+G4.1-7+G_OTHER，全绿）
python3 -m pytest agate/tests/unit/test_check_gate.py -k "g0 or g1 or g3 or g4 or other" -q   # P2 §5 子批 8a 验证命令
# 11 passed in 0.71s
python3 -m pytest agate/tests/unit/test_check_gate.py --collect-only -q
# 11 tests collected（BDD-1 计数不变）
/home/kity/.venvs/agate-dev/bin/ruff check agate/tests/unit/test_check_gate.py
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py agate/tests/unit/test_check_gate.py
# exit 0（R1-R5 零命中）
python3 -m pytest agate/tests/unit/test_agate_scripts_encoding.py -q   # encoding 守卫（BDD-7，本文件受检）
# 2 passed
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：本子批用例数 11（P2 §5 子批表预估 ~13 有出入，以
  check-gate.bats 实际 @test 数为准：G0/G1/G3/G4.1-7/G_OTHER 恰 11 个）；`_write_p4_review` 的
  P4-review.md heredoc 用 f-string 注入（ruff UP032 要求）；G4 系列 task 目录统一
  `_init_repo_with_task` helper（init commit + copytree），避免逐用例重复样板。

## 批次 8b — check-gate 子批 b（1 文件 / 29 @test 追加）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（追加） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-gate.bats`（G2 系列 24 + G_BDD1.1 / G_BDD9.1 / G_BDD10.1 / G_CMD_EXEC.1-2） | `unit/test_check_gate.py` | 29 |

> 按 P2 §5 子批表 8b 范围追加（`-k "g2 or bdd1 or bdd9 or bdd10 or cmd_exec"`）。
> check-gate.bats 中 G2 前缀 @test 全部归本子批：G2.1-4 / G2.5 / G2.7-9 / G2.9a-b / G2.10 / G2.10a /
> G2.11 / G2.13 / G2.14 / G2.17-21 / G2.24-27，共 24；加 BDD 锚点 3（BDD1.1/9.1/10.1）+ CMD_EXEC 2 = 29。

### 关键实现点

- **gate_p2 分支纯 task_dir 驱动**（无 git）：全部 29 例用 `task_dir` factory + `_write_p2_design`
  helper（复刻 bats heredoc 原文覆写 P2-design.md）+ `add_p2_candidate_count` / `add_p2_review` /
  `add_p1_field`（conftest 纯函数，frontmatter 块写入，T001 v2.0 流 A）。
- **G2.9a/b 单候选豁免**：`add_p1_field(td, "design_trivial", "true")` /
  `add_p1_field(td, "follows_existing_pattern", "[src/foo.py]")` 把豁免字段写进 P1-requirements.md
  frontmatter，check-gate.py 按行正则 `^(design_trivial|follows_existing_pattern):\s*\S` 命中 →
  min_candidates=1 → candidate_count=1 即可 exit 2（等价 bats `add_p1_field`）。
- **自定义 P2-review.md**（G2.10/10a/11、G_CMD_EXEC.1/2、G2.18/19/20）：bats heredoc 直接覆写
  P2-review.md（含 status:rejected / agent:subagent / agent:main / 缺 agent 等变体），pytest 用
  `write_text` 等价覆写，不走 `add_p2_review` 默认值。
- **G_BDD10.1 frontmatter 优先**：正文末行 `candidate_count: 1` + `add_p2_candidate_count(td, 2)`
  frontmatter 声明 2 → 判定与 frontmatter 一致（exit 2），证明不再走正文正则回退。
- **G_BDD1.1 四字段进 frontmatter**：packages/domains/ui_affected 写 frontmatter 块 + gate_commands
  写正文，gate 正确读取判定（exit 2），等价 bats T001 v2.0 流 A。
- **G_CMD_EXEC.1/2 命令可执行性 WARNING**：P3 命令 `definitely-nonexistent-cmd`（WARNING 不阻断
  exit 2）vs `true`（无 WARNING）；断言合并流含/不含命令 token。
- **流语义（P2 BLOCKER-1）**：gate_p2 的 `GATE P2: ...` 消息一律 `sys.stderr.write` → 断言一律用合并流
  `result.output`（`需至少 2 个候选方案` / `P2-design.md` / `权衡` / `非 approved` / `candidate_count` /
  `agent=main` 等），未映射 `.stdout`。
- 函数命名 `test_g2_N_...` / `test_bdd1_1_...` / `test_bdd9_1_...` / `test_bdd10_1_...` /
  `test_cmd_exec_N_...`，匹配 P2 §5 子批 8b 验证命令 `-k "g2 or bdd1 or bdd9 or bdd10 or cmd_exec"`。
- windows_smoke 打标：本子批无新增（每文件第 1 用例标记已在 8a `test_g0_...`；本子批无平台关键词用例，
  P3 §5.2 表 W 未列）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_gate.py -q
# 40 passed in 2.42s（8a 11 + 8b 29，全绿）
python3 -m pytest agate/tests/unit/test_check_gate.py -k "g2 or bdd1 or bdd9 or bdd10 or cmd_exec" -q   # P2 §5 子批 8b 验证命令
# 29 passed, 11 deselected
python3 -m pytest agate/tests/unit/test_check_gate.py --collect-only -q
# 40 tests collected（BDD-1 计数不变）
/home/kity/.venvs/agate-dev/bin/ruff check agate/tests/unit/test_check_gate.py
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py agate/tests/unit/test_check_gate.py
# exit 0（R1-R5 零命中）
python3 -m pytest agate/tests/unit/test_agate_scripts_encoding.py -q   # encoding 守卫（BDD-7，本文件受检）
# 2 passed
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：本子批用例数 29（P2 §5 子批表预估 ~32 有出入，以
  check-gate.bats 实际 @test 数为准：G2 系列 24 + BDD 锚点 3 + CMD_EXEC 2 恰 29 个）；8b 的 `-k`
  会连带命中 8d 的 `test_bdd_1_*` 前缀用例（N2 已知重叠，本文件 40 用例中无该前缀，deselected 不涉及）。

## 批次 8c — check-gate 子批 c（1 文件 / 7 @test 追加）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（追加） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-gate.bats`（G5 / G5.1 / G5_CMD.1-5） | `unit/test_check_gate.py` | 7 |

> 按 P2 §5 子批表 8c 范围追加（`-k "g5"`）。
> check-gate.bats 中 G5 前缀 @test 全部归本子批：G5（P5 恒 exit 2）+ G5.1（T060 多命令 WARNING）+
> G5_CMD.1（1 主 + 1 辅共 2 条，非 22）+ G5_CMD.2（单 P5 键无 WARNING）+ G5_CMD.3（无 gate_commands
> 块无 WARNING）+ G5_CMD.4（P6 不算 P5 命令）+ G5_CMD.5（无尾随换行仍计数 2 条）——共 7 个。

### 关键实现点

- **gate_p5 分支纯 task_dir 驱动**（无 git）：全部 7 例用 `task_dir` factory + `_write_p2_design`
  helper 复刻 bats heredoc 原文覆写 P2-design.md。
- **G5_CMD.1/2 多 bullet 生成**：bats `for i in $(seq 1 20/10)` 等价为 Python 字符串拼接
  `"".join(f"- 要点 {i}\n" for i in range(...))`，避免字面量逐行硬编码。
- **G5_CMD.5 无尾随换行**：`printf 'gate_commands:\n  P5: ...'` 等价为 `write_text` 不带尾部 `\n`
  （`.write_text(content, encoding="utf-8")`），验证 agate-gate-p5-count.py 的
  `if not content.endswith(chr(10)): content += chr(10)` 边界。
- **流语义（P2 BLOCKER-1）**：gate_p5 的 `GATE P5: ...` / `GATE P5 WARNING: ...` 一律
  `sys.stderr.write` → 断言一律用合并流 `result.output`（`1 个主命令 + 1 个辅助命令` / `共 2 条` /
  `gate_commands.P5 命令` 等），未映射 `.stdout`。
- 函数命名 `test_g5_p5_...` / `test_g5_1_...` / `test_g5_cmd_N_...`，匹配 P2 §5 子批 8c 验证命令
  `-k "g5"`。
- windows_smoke 打标：本子批无新增（每文件第 1 用例标记已在 8a `test_g0_...`；本子批无平台关键词用例，
  P3 §5.2 表 W 未列）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_gate.py -k "g5" -q   # P2 §5 子批 8c 验证命令
# 7 passed, 40 deselected
python3 -m pytest agate/tests/unit/test_check_gate.py -q
# 47 passed in 2.83s（8a 11 + 8b 29 + 8c 7，全绿）
python3 -m pytest agate/tests/unit/test_check_gate.py --collect-only -q
# 47 tests collected（BDD-1 计数不变）
/home/kity/.venvs/agate-dev/bin/ruff check agate/tests/unit/test_check_gate.py
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py agate/tests/unit/test_check_gate.py
# exit 0（R1-R5 零命中）
python3 -m pytest agate/tests/unit/test_agate_scripts_encoding.py -q   # encoding 守卫（BDD-7，本文件受检）
# 2 passed
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：本子批用例数 7（P2 §5 子批表预估 ~10 有出入，以
  check-gate.bats 实际 @test 数为准：G5 / G5.1 / G5_CMD.1-5 恰 7 个，P2 表 8c 列「~10」含估余量）。

## 批次 8d — check-gate 子批 d（1 文件 / 20 @test 追加）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（追加） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-gate.bats`（G6 系列 / G_BDD16.1 / test_bdd_1..8） | `unit/test_check_gate.py` | 20 |

> 按 P2 §5 子批表 8d 范围追加（`-k "g6 or bdd16 or bdd_1 or bdd_2 or bdd_3 or bdd_4 or bdd_5 or
> bdd_6 or bdd_7 or bdd_8"`）。
> 覆盖：G6.1 / G6.3 / G6.4 / G6.5 / G6.7 / G6.9 / G6.10 / G6.11（8）+ G_BDD16.1（1）+
> test_bdd_1 / 2 / 2b / 3 / 4 / 4b / 5 / 6 / 6b / 7 / 8（11）——共 20 个。
> test_bdd_5 / 8 是文档锚点用例（grep 协议 phase-cards 文件），非 gate 行为用例。

### 关键实现点

- **gate_p6 分支 task_dir 驱动**（无 git）：P6-acceptance.md 用 `_write_p6_acceptance` helper
  （write_text 覆写，等价 bats heredoc）；P6-evidence/ 目录 + 证据文件用 `_add_p6_evidence` helper。
- **G6.4 无证据目录**：bats「不建 P6-evidence/」等价为不调 `_add_p6_evidence`，gate_p6 走
  `P6-evidence/ 目录不存在或为空` → exit 1，断言 `P6-evidence` 于合并流。
- **refactor 口径（test_bdd_1..7）**：`add_p1_field(td, "change_type", "refactor")` 写 P1 frontmatter
  （NO_FALLBACK_STRING_FIELDS，正文散文提及不算）；P6 frontmatter pass/fail/regression_pass 原文复刻。
  test_bdd_4 / 4b 分别缺 regression.log / regression_pass → 断言 `regression.log` / `regression_pass`。
- **test_bdd_7 三段走查**：同 task_dir 依次跑 P1→P3→P6 三阶段 gate（bats 同测试多 `run` 等价），
  各阶段独立断言 exit 2。
- **test_bdd_5 / 8 文档锚点**：`re.search(r"禁止.*伪造", (agate_root/"phase-cards"/"P6-acceptance.md")
  .read_text(...))` / `"回归测试口径" in ... P3-tdd.md`——bats `grep -q` 等价（agate_root fixture）。
- **流语义（P2 BLOCKER-1）**：gate_p6 的 `GATE P6: ...` / `GATE P1: ...` 一律 `sys.stderr.write` →
  断言一律用合并流 `result.output`（`FAIL=` / `TOTAL=0` / `P6-evidence` / `FAIL=1` / `FAIL=0` 等），
  未映射 `.stdout`。
- 函数命名 `test_g6_N_...` / `test_bdd16_1_...` / `test_bdd_N[_N b]_...`，匹配 P2 §5 子批 8d 验证命令
  `-k "g6 or bdd16 or bdd_1 ... bdd_8"`（`test_bdd_2b_...` 等含 `bdd_2` 子串，`-k` 子串命中）。
- windows_smoke 打标：本子批无新增（8d 用例名无平台关键词；每文件第 1 用例标记已在 8a
  `test_g0_...`，P3 §5.2 表 W 未列）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_gate.py -k "g6 or bdd16 or bdd_1 or bdd_2 or bdd_3 or bdd_4 or bdd_5 or bdd_6 or bdd_7 or bdd_8" -q   # P2 §5 子批 8d 验证命令
# 20 passed, 47 deselected
python3 -m pytest agate/tests/unit/test_check_gate.py -q
# 67 passed in 5.19s（8a 11 + 8b 29 + 8c 7 + 8d 20，全绿）
python3 -m pytest agate/tests/unit/test_check_gate.py --collect-only -q
# 67 tests collected（BDD-1 计数不变）
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：本子批用例数 20，与 P2 §5 子批表 8d 预估 ~20 一致。

## 批次 8e — check-gate 子批 e（1 文件 / 12 @test 追加）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（追加） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-gate.bats`（G7.1-9 / G_DG_ANCHOR.1-2 / bdd-11） | `unit/test_check_gate.py` | 12 |

> 按 P2 §5 子批表 8e 范围追加（`-k "g7 or dg_anchor or bdd_11"`）。
> 覆盖：G7.1 / G7.2 / G7.3 / G7.4 / G7.5 / G7.6 / G7.7 / G7.8 / G7.9（9）+
> G_DG_ANCHOR.1 / G_DG_ANCHOR.2（2）+ bdd-11（1）——共 12 个（P2 预估 ~14，实计 12，见偏离点）。

### 关键实现点

- **gate_p7 分支 task_dir 驱动**（无 git）：P7-consistency.md 用 `_write_p7` helper
  （write_text 覆写，等价 bats heredoc）。
- **G7.3 / G7.7 多关键词断言**：bats `*"DESIGN_GAP"*"未配对"*` / `*"P4"*"DESIGN_GAP"*"P7"*`
  展开为多个 `in result.output` 子断言（合并流；顺序由输出文本天然满足）。
- **G7.8 / G7.9 计数行排除**：`[BLOCKER]: 0 条` 总结行不误计（`(:|：)?` alternation），
  G7.8 单总结行 exit 0，G7.9 加真实 `[BLOCKER]` 后 exit 1——复刻 gate_p7 的
  `if not re.search(...)` 排除逻辑（同 bdd-11 的 M4 语义）。
- **bdd-11（M4 全角冒号）**：`env={"LC_ALL": "C", "LANG": ""}` 经 `_run_gate` 新增的 `env=`
  参数透传 run_cli（等价 bats `run env LC_ALL=C LANG= ...`）；`task_dir(no_state_yaml=True)`
  等价 `create_task_dir --no-state-yaml`。断言仅 exit 0（不误计全角冒号总结行为 BLOCKER）。
- **G_DG_ANCHOR 行首锚点**：G_DG_ANCHOR.1 句中 `[DESIGN_GAP: xxx]`（非行首）不计入 GAP
  → exit 0；G_DG_ANCHOR.2 行首 `- [DESIGN_GAP: xxx]` 计入 → exit 1（断言 `DESIGN_GAP`）。
- **流语义（P2 BLOCKER-1）**：gate_p7 的 `GATE P7: ...` / `GATE P7 WARNING` / `WARNING P7`
  一律 `sys.stderr.write` → 断言一律用合并流 `result.output`（`BLOCKER=` /
  `DEVIATION-CRITICAL=` / `未配对` 等），未映射 `.stdout`。
- 函数命名 `test_g7_N_...` / `test_dg_anchor_N_...` / `test_bdd_11_...`，匹配 P2 §5 子批 8e
  验证命令 `-k "g7 or dg_anchor or bdd_11"`。
- windows_smoke 打标：本子批无新增（8e 用例名无平台关键词；每文件第 1 用例标记已在 8a
  `test_g0_...`，P3 §5.2 表 W 未列）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_gate.py -k "g7 or dg_anchor or bdd_11" -q   # P2 §5 子批 8e 验证命令
# 12 passed, 67 deselected
python3 -m pytest agate/tests/unit/test_check_gate.py -q
# 79 passed in 6.90s（8a 11 + 8b 29 + 8c 7 + 8d 20 + 8e 12，全绿）
python3 -m pytest agate/tests/unit/test_check_gate.py --collect-only -q
# 79 tests collected（BDD-1 计数递增）
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：本子批用例数 12，P2 §5 子批表 8e 预估 ~14；
  实际 check-gate.bats 中 G7 前缀用例共 9（G7.1-9）+ G_DG_ANCHOR 2 + bdd-11 1 = 12，
  P2 预估为近似值，以 bats 实计为准。

## 批次 8f — check-gate 子批 f（1 文件 / 10 @test 追加）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（追加） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-gate.bats`（G8.1-10） | `unit/test_check_gate.py` | 10 |

> 按 P2 §5 子批表 8f 范围追加（`-k "g8"`）。
> 覆盖：G8.1 / G8.2 / G8.3 / G8.4 / G8.5 / G8.6 / G8.7 / G8.8 / G8.9 / G8.10——共 10 个
> （P2 预估 ~12，实计 10，见偏离点）。

### 关键实现点

- **gate_p8 分支 git repo 驱动**：P8 检查基于 `git diff --cached`（暂存区，不用 HEAD~1）——
  新增 `_init_p8_repo` helper（`_init_repo_with_task` + 逐文件 write_text + `git_repo.stage`
  等价 bats `git -C "$repo" add ...` + 可选 `git_repo.git("tag", ...)`），
  `run_cli(..., cwd=repo)` 等价 bats `cd '$repo' && ...`。
- **G8.5 无 P8 文件不需要 git**：P8-release.md 缺失 → `_read_text` 空串 → bump_type 缺失提前
  return 1（gate_p8 不触达 git 检查），直接 `_run_gate` 无 cwd/repo。
- **G8.6 CHANGELOG_FILE 环境变量覆盖**：`env={"CHANGELOG_FILE": "HISTORY.md"}`
  （等价 bats `CHANGELOG_FILE="HISTORY.md" run bash -c ...`），HISTORY.md 替代默认 CHANGELOG.md。
- **G8.7 / G8.8 tag 存在性**：CHANGELOG 暂存 diff 含 `[0.2.0]` → tag_version=0.2.0 →
  `git tag -l v0.2.0` 空则 WARNING（G8.7 断言 `tag v0.2.0 不存在`）／有 tag 则无 WARNING
  （G8.8 反向断言 `not in result.output`）。
- **G8.2 / G8.3 WARNING 语义**：无 version 变更 → `GATE P8 WARNING: ...version...`；
  有 version 但 CHANGELOG 无变更 → `...CHANGELOG...`——均 WARNING 不阻断 exit 2。
- **流语义（P2 BLOCKER-1）**：`GATE P8: ...` / `GATE P8 WARNING: ...` 一律 `sys.stderr.write`
  → 断言一律用合并流 `result.output`（`bump_type` / `debt_check` / `version` / `CHANGELOG` /
  `tag v0.2.0 不存在`），未映射 `.stdout`。
- 函数命名 `test_g8_N_...`，匹配 P2 §5 子批 8f 验证命令 `-k "g8"`。
- windows_smoke 打标：本子批无新增（8f 用例名无平台关键词；每文件第 1 用例标记已在 8a
  `test_g0_...`，P3 §5.2 表 W 未列）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_gate.py -k "g8" -q   # P2 §5 子批 8f 验证命令
# 10 passed, 79 deselected
python3 -m pytest agate/tests/unit/test_check_gate.py -q
# 89 passed in 8.04s（8a 11 + 8b 29 + 8c 7 + 8d 20 + 8e 12 + 8f 10，全绿）
python3 -m pytest agate/tests/unit/test_check_gate.py --collect-only -q
# 89 tests collected（BDD-1 计数递增）
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：本子批用例数 10，P2 §5 子批表 8f 预估 ~12；
  实际 check-gate.bats 中 G8 前缀用例共 10（G8.1-10），P2 预估为近似值，以 bats 实计为准。


## 批次 8g — check-gate 子批 g（1 文件 / 15 @test 追加）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（追加） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-gate.bats`（G_RETREAT.1-6 + G_NC_BINARY.1/2/3/5/6 + G_SUGGEST.1-4） | `unit/test_check_gate.py` | 15 |

> 按 P2 §5 子批表 8g 范围追加（`-k "retreat or nc_binary or suggest"`）。
> 覆盖：G_RETREAT.1-6（回退抵达检测）、G_NC_BINARY.1/2/3/5/6（P1 NEED_CONFIRM
> 三值分级）、G_SUGGEST.1-4（SUGGEST 不阻塞 + typo 兜底）——共 15 个（P2 预估 ~15，实计 15）。

### 关键实现点

- **`_run_gate` 扩展 OLD_PHASE 第 3 参数**：main() 回退抵达检测用 `sys.argv[3]`（可选）——
  给 `_run_gate` 增 `old_phase=None`，非 None 时追加为第 4 个命令参数
  （等价 bats `check-gate.py P1 "$dir" P2`）。既有 8a-8f 调用不受影响（默认 None）。
- **G_RETREAT 用空目录**：bats 是 `mkdir -p "$BATS_TEST_TMPDIR/g_retreatN"`（非
  create_task_dir）→ pytest 用 `tmp_path / "g_retreatN"` + `mkdir`（空任务目录）。
  - G_RETREAT.1/2/4/6：P1/P6 空目录直跑（P1-review.md / 证据目录缺失在回退分支
    不触达，回退时先 `sys.exit(2)`）；G_RETREAT.3 用 P4+OLD_PHASE=P6。
  - G_RETREAT.5 正常推进方向（P4 ← P3，非回退）：需 git repo 且空暂存区 → exit 1
    → pytest 用 `git_repo` + `run_cli(..., cwd=repo)`（gate_p4 查 `git diff --cached`）。
- **G_NC_BINARY / G_SUGGEST 用 `task_dir(no_state_yaml=True)`**：bats 是
  `create_task_dir --no-state-yaml` + heredoc 覆写 P1-requirements.md / P1-review.md
  → pytest 用 `task_dir(no_state_yaml=True)` + `_write_p1_marker_task` helper
  （write_text 覆写两文件，等价 heredoc；P1-review.md status: approved +
  agent: requirements-review + BDD-1: PASS）。
- **流语义（P2 BLOCKER-1）**：`GATE P1: ...` / `GATE P1 WARNING: ...` 一律
  `sys.stderr.write` → 断言一律用合并流 `result.output`（`NEED_CONFIRM` / `不合规` /
  `WARNING` / `SUGGEST` / `阻塞` / `重命名为` / `SUGGEST 格式不符` / `回退抵达`），
  未映射 `.stdout`。
- 函数命名 `test_g_retreat_N_...` / `test_g_nc_binary_N_...` / `test_g_suggest_N_...`，
  匹配 P2 §5 子批 8g 验证命令 `-k "retreat or nc_binary or suggest"`。
- windows_smoke 打标：本子批无新增（8g 用例名无平台关键词；每文件第 1 用例标记已在
  8a `test_g0_...`，P3 §5.2 表 W 未列）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_gate.py -k "retreat or nc_binary or suggest" -q   # P2 §5 子批 8g 验证命令
# 15 passed, 89 deselected
python3 -m pytest agate/tests/unit/test_check_gate.py -q
# 104 passed in 8.43s（8a 11 + 8b 29 + 8c 7 + 8d 20 + 8e 12 + 8f 10 + 8g 15，全绿）
python3 -m pytest agate/tests/unit/test_check_gate.py --collect-only -q
# 104 tests collected（BDD-1 计数递增）
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离）：G_NC_BINARY.4 在 check-gate.bats 中不存在（编号 1/2/3/5/6），
  按 bats 实计迁移 5 个；G_RETREAT/G_NC_BINARY/G_SUGGEST 三组共 15 个与 P2 预估一致。

## 批次 8h — check-gate 子批 h（1 文件 / 16 @test 追加）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（追加） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-gate.bats`（D-drift-1/2/4/4b/5/6 + G-drift-1/2/3 + TAG0005 BDD-1/2/9/12/13/14/15） | `unit/test_check_gate.py` | 16 |

> 按 P2 §5 子批表 8h 范围追加（`-k "drift or tag0005"`）。
> 覆盖：D-drift-1/2/4/4b/5/6（dispatch 模板关键词守护）、G-drift-1/2/3
> （dispatch-protocol 关键词 + implementer/verifier 反例）、TAG0005 BDD-1/2/9/12/13/14/15
> （role-system / check-gate.py / dispatch-protocol 文档锚点 + scripts 扫描）——共 16 个
> （P2 预估 ~10，实计 16，差异见偏离点）。

### 关键实现点

- **纯文件内容断言，无 run_cli / task_dir / git_repo 依赖**：8h 全部是 bats `grep -q`
  等价（读 `$AGATE_ROOT` 下文件后断言子串），非 `run check-gate.py`。pytest 用
  `agate_root` fixture + `read_text(encoding="utf-8")`（BDD-7）。
- **等价映射**（P2 §3.2 逐断言对照）：
  - `grep -q 'X' FILE` → `assert "X" in text`。
  - `! grep -q 'X' FILE`（G-drift-2/3）→ `assert "X" not in text`（N5 反向断言）。
  - `grep -qE '^\| backend \|.*plan-eng-review'`（TAG0005 BDD-1）→ `re.search(..., re.M)`，
    三文件（role-system.md / rules/review-mapping.md / phase-cards/P2-design.md）。
  - `grep -rl 'Review 角色特别指令' --include='*.md'` + 单文件断言（TAG0005 BDD-9）→
    `agate_root.rglob("*.md")` 收集命中 + `assert len(hits) == 1` + 命中路径为
    `assets/templates/dispatch-prompt.md`（等价 `wc -l == 1` + `grep -q` 路径）。
  - `grep -rnE '>&2;\s*exit 0' scripts/*.sh` + 每命中行须含「跳过」（TAG0005 BDD-15）→
    `(agate_root / "scripts").glob("*.sh")` 逐行正则 + 命中行断言含「跳过」；bats 用
    `while read` 循环逐命中行判定，pytest 同语义。
- **函数命名** `test_drift_N_...` / `test_drift_gN_...` / `test_tag0005_bdd_N_...`，
  匹配 P2 §5 子批 8h 验证命令 `-k "drift or tag0005"`。
- **windows_smoke 打标**：本子批无新增（8h 用例名无平台关键词；每文件第 1 用例标记已在
  8a `test_g0_...`）。
- **`_read_text` helper**：`path.read_text(encoding="utf-8")` 薄封装，8h 全部内容断言复用。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_gate.py -k "drift or tag0005" -q   # P2 §5 子批 8h 验证命令
# 16 passed, 104 deselected
python3 -m pytest agate/tests/unit/test_check_gate.py -q
# 120 passed in 8.33s（8a 11 + 8b 29 + 8c 7 + 8d 20 + 8e 12 + 8f 10 + 8g 15 + 8h 16，全绿）
python3 -m pytest agate/tests/unit/test_check_gate.py --collect-only -q
# 120 tests collected（BDD-1 计数递增）
ruff check agate/tests/unit/test_check_gate.py
# All checks passed!
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- **8h 实计 16 用例 vs P2 预估 ~10**：P2 §5 子批表 8h 标注「~10」，但按 check-gate.bats
  实际 D-drift（6）+ G-drift（3）+ TAG0005 BDD（7）= 16 个全部迁移（1 @test → 1 test
  函数，P1 约束）。子批完成后的整文件覆盖确认：test_check_gate.py 累计 120 用例，
  check-gate.bats 全部 124 用例中的剩余 4 个（PG.P2REVIEW / bdd-14 / bdd-28 / bdd-29）
  按 P2 §5 N1 备注属 `-k` 非穷举分区，由「8 子批完成后整文件跑」兜底，不在 8h 范围内；
  8a-8h 合计 120 用例（104 + 16），check-gate-p1-review / check-gate-p5-diff 两文件
  另覆盖各自 bats 源。

## 批次 8i — check-gate-p1-review / check-gate-p5-diff（2 文件 / 22 @test）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（新建） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-gate-p1-review.bats` | `unit/test_check_gate_p1_review.py` | 9 |
| `unit/check-gate-p5-diff.bats` | `unit/test_check_gate_p5_diff.py` | 13 |

> 按 P2 §5 批次 8 备注「`test_check_gate_p1_review.py` / `test_check_gate_p5_diff.py`
> 各自独立文件」迁移。p1-review = P1-review.md 独立评审流程（BDD-21 流 C，NEED_CONFIRM
> 阻塞判定 + frontmatter status/agent 校验），p5-diff = P5 gate 的 pre-task-baseline.md
> vs fail-list.txt 机械 diff 分支（PG.1-PG.12 + PG.9a）。

### 关键实现点

- **p1-review 分支**（9 用例，`test_pg_p1review_N_*`）：
  - 等价映射：bats `create_task_dir --no-state-yaml` + heredoc 覆写 P1-requirements.md /
    P1-review.md → `task_dir(no_state_yaml=True)` + `write_text` 覆写（bats 源文件仅留
    P0-brief，但 gate_p1 只读 P1-requirements.md / P1-review.md，无影响）。
  - 断言对象：`GATE P1` 消息一律 `sys.stderr.write` → 合并流 `result.output`
    （P2 §3.2 流语义规则，BLOCKER-1）。
  - `_P1_REQ_BODY` 共享常量（frontmatter + Given 行），case 8 追加
    `- [NEED_CONFIRM] z 的边界条件需确认` 验证流 C 未结构化解决仍阻塞。
  - case 3 反向锚点断言 `"BDD" in output or "锚点" in output`（bats `[[ ... == *"BDD"* ]] ||
    [[ ... == *"锚点"* ]]` 等价）。
- **p5-diff 分支**（13 用例，`test_pg_N_*` 与 bats PG.N 一一对应）：
  - `_make_baseline` / `_make_post_fails` 纯函数等价 bats 同名 helper
    （captured_at_commit 头 + ```fail-list 块 / P5-test-results/fail-list.txt 逐行写）。
  - `_write_known_failures` 用 `_KNOWN_FAILURES_HEAD` + 行参数拼接（与 bats heredoc 表格结构
    逐行对照，登记条目数由 `^\|\s*[0-9]+\s*\|` 行计数，PG.9/9a 差分验证）。
  - 全部走 `task_dir()` 默认态（P0-P8 文件存在，P2-design.md touch 空文件 →
    `_gate_p5_count` 回退 (0,0) 无 WARNING，等价 bats `create_task_dir`）。
- **windows_smoke 打标**：两文件各打第 1 用例（`test_pg_p1review_1` / `test_pg_1`），
  符合 P2 §3.4「每文件第 1 个 @test 打标」约定；无平台关键词用例。
- **函数命名**：`test_pg_p1review_N_*` / `test_pg_N_*`（PG 前缀，与 P2 §5 8a-8h
  的 PG.P2REVIEW 同族命名一致）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_gate_p1_review.py agate/tests/unit/test_check_gate_p5_diff.py -q
# 22 passed in 1.32s（9 + 13，全绿）
python3 -m pytest agate/tests/unit/test_check_gate_p1_review.py agate/tests/unit/test_check_gate_p5_diff.py --collect-only -q
# 22 tests collected（BDD-1 计数递增：test_check_gate.py 120 + 本批 22 = 142/749）
ruff check agate/tests/unit/test_check_gate_p1_review.py agate/tests/unit/test_check_gate_p5_diff.py
# All checks passed!
python3 agate/scripts/check-platform-assumptions.py <两文件>
# exit 0（R1-R5 零命中）
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- **函数名前缀选择 `pg`**：两文件与 P2 §5 子批表 8a-8h（全部落在 test_check_gate.py）
  无 `-k` 交叉验证需求，`pg` 前缀不与既有任何子批 `-k` 关键字冲突；与 check-gate.bats
  的 PG.P2REVIEW 系列命名（`test_pg_p2review_*`）同族，便于 P6 BDD 对照。
- p1-review 源 bats 文件名无版本号锚点，本批按 P2 §3.3 module 名契约
  `test_check_gate_p1_review.py` / `test_check_gate_p5_diff.py` 命名。

## 批次 9a — P6 证据链（1 文件 / 30 @test）

### 迁移清单

| 迁移源（bats，只读保留） | 目标 pytest（新建） | 用例数 |
|--------------------------|---------------------|--------|
| `unit/check-p6-evidence.bats` | `unit/test_check_p6_evidence.py` | 30 |

### 关键实现点

- **流语义（P2 BLOCKER-1）**：check-p6-evidence.py 的 `GATE P6-EVIDENCE:` 消息一律
  `sys.stderr.write` → 断言一律用合并流 `result.output`（`无 BDD 条目` / `缺文件证据引用` /
  `P6-evidence` / `screenshots` / `1KB` / `全是纯文本` 等），未映射 `.stdout`。
- **Pillow 无关（P3 §4 备注的"Pillow 可选 skipif"不适用）**：check-p6-evidence.py 调
  agate-image-check.py variance/ahash，缺 Pillow 时返回 `SKIP_NO_PILLOW` 走 WARNING 分支
  （`break` / 不阻断），本批 30 用例的 exit code 判定全部不随 Pillow 安装状态变化（E.9/E.10/
  E.12/E.13/EVIDENCE_* 均已实测双态等价），故无 skipif——与 bats 原文（无 skip）一致。
- **随机字节文件**：bats `head -c N /dev/urandom` → `os.urandom(N)` + `write_bytes`
  （E.9 100B / E.10/E.13 5000B）；md5 重复用例（E.12 / EVIDENCE_MD5_DETAIL.1/2）用
  `base64.b64encode(os.urandom(5000)).decode("ascii")` 同一内容写两文件（等价
  `head -c 5000 /dev/urandom | base64`，逐字节相同 → md5 相同）。
- **ui_affected 读取（T001 v2.0 流 A）**：UI 用例复刻 bats heredoc 覆写 P2-design.md
  （`---\nagent: test\n---\nui_affected: true|false` 正文），check-p6-evidence.py 经
  agate-md-field-get.py 正则回退读到 "true"/"false"（frontmatter 无该字段）。
- **P6-evidence/screenshots 目录**：E.8 只建 P6-evidence/（含 result.json）不建 screenshots/
  → `screenshots` 断言；E.9/E.10/E.12/E.13/EVIDENCE_* 建 screenshots/ 子目录（等价
  `mkdir -p`）；E.15-17 只建 P6-evidence/（纯文本/混合证据类型判定）。
- **函数命名**：`test_e_N_...` / `test_evid_ext_N_...` / `test_evidence_{no_ref,empty,md5}_detail_N_...`
  / `test_bdd_9_...` / `test_bdd_10_...`，匹配 P2 §5 子批 9a 验证命令 `-k "p6_evidence"`。
- **windows_smoke 打标**：每文件第 1 用例 `test_e_1_no_p6_file_exit_2`——共 1 处
  （本批无平台关键词用例，P3 §5.2 表 W 未列）。

### 自查结果

```bash
cd /home/kity/oclab/agate/.worktrees/agate-TAG0010
python3 -m pytest agate/tests/unit/test_check_p6_evidence.py -q
# 30 passed in 2.50s（全绿）
python3 -m pytest agate/tests/unit/ -k "p6_evidence" -q   # P2 §5 子批 9a 验证命令
# 31 passed, 463 deselected（30 本批 + test_agate_archive_stale_outputs.py::test_arch_3_p6_evidence_* 函数名含 p6_evidence 重叠，无害）
python3 -m pytest agate/tests/unit/test_check_p6_evidence.py --collect-only -q
# 30 tests collected（BDD-1 计数不变）
ruff check agate/tests/unit/test_check_p6_evidence.py
# All checks passed（exit 0）
python3 agate/scripts/check-platform-assumptions.py agate/tests/unit/test_check_p6_evidence.py
# exit 0（R1-R5 零命中）
python3 -m pytest agate/tests/unit/test_agate_scripts_encoding.py -q   # encoding 守卫（BDD-7，本文件受检）
# 2 passed
```

### 偏离点

- 无 `[DESIGN_GAP]` / `[SCOPE+]`。
- 实现细节（非偏离，记录供后续批次参照）：本批未使用 fixtures/ 静态夹具——check-p6-evidence.bats
  全部 30 用例都自建 task_dir + heredoc（无 load_fixture 引用），pytest 用 `task_dir` factory +
  write_text 等价构造；P3 §4「fixtures/ 静态夹具（full-task P6-evidence/）」备注不适用于本批
  （full-task/P6-evidence 由批次 9b check-p6-provenance.bats 使用，届时用 load_fixture）。
