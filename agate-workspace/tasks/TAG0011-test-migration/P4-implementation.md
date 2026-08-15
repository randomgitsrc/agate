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
