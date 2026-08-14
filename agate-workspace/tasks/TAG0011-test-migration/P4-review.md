---
phase: P4
task_id: TAG0011-test-migration
type: review
parent: P4-implementation.md
trace_id: TAG0011-P4-REVIEW-20260815
status: approved
created: 2026-08-15
agent: review
reviewed_batch: 批次 0（pytest 基座：conftest.py + test_sanity.py + test_agate_workspace_resolve.py + pyproject.toml）
---

# P4 评审 — TAG0011 批次 0 pytest 基座实现

> 评审角色：review（偏执 Staff Engineer）。范围：按 P4-dispatch-context-review.md 派发指引的 5 个关注点。
> **只评审不改**；本次评审未修改任何文件（含一次性探针文件，探针于同一命令内创建并删除，仓库无残留）。

## 结论

**status: approved**（无 BLOCKER；1 项需主 Agent 跟踪的派发/设计偏差 + 1 项后续批次注意点）

## 验证证据（客观查证，非仅代码走读）

| 检查 | 命令 | 结果 |
|------|------|------|
| pytest 批次 0 | `python3 -m pytest agate/tests/test_sanity.py agate/tests/unit/test_agate_workspace_resolve.py -q` | 16 passed |
| 批次 0 验证命令 | `python3 -m pytest agate/tests/ -k "sanity or helpers or workspace" -q` | 16 passed（"helpers" 无匹配，见跟踪项 1） |
| 双跑对照（BDD-6） | `bats agate/tests/sanity.bats agate/tests/unit/agate-workspace-resolve.bats` | 16 ok（与 pytest 16 全绿一致） |
| marker 冒烟 | `python3 -m pytest agate/tests/ -m windows_smoke -q` | 3 passed, 13 deselected（test_sanity_1 / test_wr_1 / test_bdd_18） |
| ruff | `~/.venvs/agate-dev/bin/ruff check <3 新文件>` | All checks passed（exit 0） |
| 平台扫描 | `python3 agate/scripts/check-platform-assumptions.py <3 新文件>` | exit 0（R1-R5 零命中） |
| encoding 守卫（BDD-7 规则） | open()/read_text()/subprocess.run(text=True) 无 encoding= 扫描 | NONE（零违规） |
| 一致性 | `python3 agate/scripts/check-protocol-consistency.py` | 全部通过 |
| py38 语法 | 扫描 match/removeprefix/removesuffix | 无违规（conftest.py:193 的 pattern.match 是 re.Pattern.match，非 match 语句） |
| collect 基线 | `pytest agate/tests/ --collect-only -q` | 16 tests collected（批次 0 范围） |

---

## 关注点 1：合并流语义（BLOCKER-1 核心）— ✅ 正确实现

- `CommandResult.output`（conftest.py:30-32）实现为 property，返回 `self.stdout + self.stderr`，
  与 P2 §3.2 的 bats `$output`（stdout+stderr 合并流）语义一致；`[ -z "$output" ]` / `!=` 空非空
  断言将基于合并流（P3 §5.1 流语义断言规则）。本地实测 `echo out; echo err >&2` 场景下
  `stdout + stderr` 拼接 = "out\nerr\n"，与 bats `$output` 两行结果一致。
- 批次 0 无 `[ -z "$output" ]` 空断言（正确——26 处分布在批次 1/2/5/7/12/16），未提前引入错误映射。
- `test_agate_workspace_resolve.py` 的 `_ws_out`/`_tasks_out`（:16-27）从**合并流** `result.output`
  提取 `AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 行，与 bats `echo "$output" | grep '^AGATE_WORKSPACE='` 等价
  （取首个匹配行）。实际运行 agate_common.py 确认两行均走 stdout（无 stderr），合并流提取不受影响。
- 未见任何把空/非空断言映射到 `.stdout` 的 BLOCKER-1 回归。

## 关注点 2：fixture 行为等价 — ✅ 与 bats helpers 逐项对照等价

`create_task_dir`（conftest.py:75-154）与 fixtures.bash 对照：
- P0-brief.md / P1-requirements.md（含 legacy_fields 分支）内容**字节级一致**（对照 fixtures.bash:193-240）；
- `.state.yaml` 的 `first_phase = phases[0]`（bats 首个非空 phases）等价；`retries: {}` 一致；
- P2/P3/P4/P5/P6/P7/P8 文件与 P6-acceptance.md 内容一致；frontmatter 补写循环的 glob `P[1-8]-*.md`
  （排除 P0-brief.md）与 bats `"$dir"/P[1-8]-*.md` 等价；
- 选项语义：phases / risk_level / with_evidence / no_state_yaml / legacy_fields 全覆盖。

`add_*` 系列（add_agent_field / add_given_line / add_frontmatter_field / add_pruning_excuse /
add_p1_field / add_p2_candidate_count / add_p2_review / add_evidence_file / add_p6_pass/fail/need_confirm /
add_p1_bdd）与 fixtures.bash 逐项对照：frontmatter 块解析/替换/插入、裁剪理由追加、p1_bdd 编号
（`re.findall('^#### BDD-[0-9]', re.M)` = `grep -cE`）均语义等价。

`GitRepo`（conftest.py:263-301）与 git-helper.bash 对照：init -q + user.email/user.name/commit.gpgsign false
一致；`.commit/.stage/.staged_diff/.staged_files` 等价 git_commit/git_stage/git_staged_diff/git_staged_files。

`agate_root` 反推逻辑与 load.bash `_resolve_agate_root` 等价（AGATE_ROOT env 覆盖优先 + 上溯找
scripts/+assets/ + 失败 fail-closed）。

`task_dir`/`git_repo`/`run_cli`/`py_path`/`python_exe`/`load_fixture` 六 fixture 与 P3 §5.1 清单齐全，
纯函数（from conftest import）13 个全部在列。

## 关注点 3：用例迁移忠实度 — ✅ sanity 6 + workspace-resolve 10 与 bats 语义等价

- **exit code**：`assert result.returncode == 0` 等价 `[ "$status" -eq 0 ]`（10/10）。
- **输出提取**：`_ws_out`/`_tasks_out` 合并流提取等价 bats ws_out/tasks_out；`_realpath`（os.path.realpath）
  等价 `realpath -m`（含不存在路径）。
- **路径断言**：WR.2 的 endswith("/agate-workspace") 等价 `[[ "$ws" == *"/agate-workspace" ]]`；
  WR.3 的 `not (project/"agate-workspace").exists()` 等价 `[ ! -d ... ]`。
- **CRLF（bdd-18）**：`write_bytes(b"AGATE_WORKSPACE=ws-crlf\r\n")` 等价 `printf '...\r\n'`（真 CRLF 字节）；
  断言 `_ws_out == _realpath(project/"ws-crlf")` 与 bats 一致，运行通过。
- **env 传入**：`env={"AGATE_TASKS_DIR": ...}` 等价 bats `run env AGATE_TASKS_DIR=...`（继承 + 覆盖）。
- sanity 6 断言（文件存在 / 不存在的 P2-design / 裁剪文案 / .git / git log 行数）全部等价。
- **双跑对照实证**：pytest 16 passed + 原 bats 16 ok，逐条一致。

## 关注点 4：可扩展性（后续 16 批）— ✅ 支撑到位，含 1 项注意点

- **`from conftest import ...` 子目录可用性**：以一次性探针实证（创建即删）——在真实仓库根
  （pyproject.toml 锚定 rootdir）下，`pytest agate/tests/unit/` 时根 conftest 被加载，
  `agate/tests` 经 import_path(prepend) 注入 sys.path（实测 sys.path 含 `...agate/tests`），
  unit/ 下测试 `from conftest import create_task_dir` 成功。P2 §3.1 的"conftest 所在目录自动加入
  sys.path"声明在真实仓库成立（依赖 rootdir 锚定；无 pyproject 时该机制不成立——注意点）。
  注意：迁移产出 test_*.py 勿以无 pyproject.toml 的孤立目录方式运行。
- **fixture 清单**：P3 §5.1 所列 session（agate_root/agate_scripts/agate_assets/python_exe）+ function
  （task_dir/git_repo/run_cli/py_path）+ 纯函数 + load_fixture 全部交付；后续批次缺 fixture 时按
  P2 §3.1 过渡约定在对应批次追加。
- **Windows 冒烟 marker**：pyproject 注册 `markers = ["windows_smoke: Windows CI smoke representative"]`
  （P3 §5.2 原文），3 处打标符合 P3 §5.2 表 W（workspace-resolve CRLF 1 处 + 每文件第 1 用例）。
- **注意点（后续批次）**：`git_repo` fixture 以 `tmp_path` 本体作为仓库根，而 bats `git_init` 是
  `$BATS_TEST_TMPDIR/repo-XXXX` 独立子目录。批次 0 无测试同时请求 task_dir + git_repo，无影响；但后续
  "create_task_dir + git" 模式批次（check-gate/check-pruning 等，bats 用 `cp -r "$dir" "$repo/task"`
  显式把任务目录复制进仓库）迁移时，task 文件会落在仓库内，`git add -A`/commit 语义与 bats 不同。
  建议后续 implementer 沿用 bats 的"显式复制进 repo"模式或显式指定 stage 路径，避免静默语义漂移。

## 关注点 5：Python 规范 — ✅ 合规

- 所有文本 I/O 显式 `encoding="utf-8"`（_write_utf8 / read_text / open(..., encoding=) /
  subprocess.run(encoding=)），encoding 守卫扫描零违规（BDD-7）。
- ruff（0.16.3, target-version=py38）全过：无 match/removeprefix/removesuffix 等 3.9+/3.10+ 语法（BDD-8）；
  import 顺序、f-string、simplification 规则全部通过。
- 平台无关：无裸 python3 字面量（用 python_exe fixture）、无 /tmp 字面量、无 PATH 硬编码、
  无 `[[ -L ]]` 单平台断言——check-platform-assumptions 对 3 文件零命中（BDD-5）。
- pyproject.toml 变更与 P2 §2 影响域一致：ruff `src` 扩展含 tests + `[tool.pytest.ini_options]`
  testpaths/markers。

---

## 需要主 Agent 跟踪（非本次代码缺陷，不阻塞本批通过）

1. **【必须跟踪】helpers-python.bats（3 用例）未在批次 0 迁移**（派发/设计偏差）：
   - P1 §4 批次 0 = 19 @test、P2 §5 批次 0 = 19、P3 §4 批次 0 = "3 文件 / 19 @test"，均含
     `helpers-python.bats → test_helpers_python.py`（python_exe 探测语义 + create_python_shim_bin 退役）。
   - P4 派发范围仅覆盖 conftest + sanity + workspace-resolve（16 用例），P4-implementation.md 已注明
     "helpers-python.bats 不在本批迁移，留待对应批次"。implementer 按派发执行，无违约。
   - 风险：批次 0 验证命令 `-k "sanity or helpers or workspace"` 的 "helpers" 关键字当前无 pytest 文件匹配
     （16 而非 19）；若后续批次不补 `test_helpers_python.py`，749 迁移基线少 3，P6 BDD-1 `--collect-only
     ≥ 749` 会失败。**请主 Agent 显式安排 helpers-python 到后续批次并更新 P2/P3 批次表计数**（P4-implementation.md
     批次 0 头注的"3 文件 / 16 用例"与 P3"19 @test"不一致，需同步修订）。

## 意见（无 BLOCKER）

- [INFORMATIONAL] conftest.py 的 run_cli 实现命名 `_run_cli_impl` 规避 fixture 同名遮蔽，P4-implementation.md
  :67-69 已记录，方案正确。
- [INFORMATIONAL] `test_wr_8/9` 的 `assert str(ws) != ""` 等价 bats `[ -n "$ws" ]`；`_realpath(ws/agents/...)`
  锚定断言与 bats 一致（解析输出缺行时两端都失败，语义等价）。
- [INFORMATIONAL] GitRepo 各方法不检查 returncode（bats helpers 同样不 set -e），失败通过后续断言暴露，
  等价于 bats 行为。
- [INFORMATIONAL] 批次 0 验证命令实际收集 16（非 19），命令 exit 0 通过——主 Agent 验收批次 0 时以
  "16 passed + 原 2 bats 16 ok" 为判定口径，勿误按 19 计数。

## 返回给主 Agent

- File: `agate-workspace/tasks/TAG0011-test-migration/P4-review.md`
- Status: **approved**（0 BLOCKER；合并流语义与 fixture 行为等价均已实证确认）
- 意见摘要：批次 0 基座实现正确、双跑对照全绿、规范合规；需跟踪 helpers-python（3 用例）迁移排期，
  否则 P6 BDD-1 ≥749 计数不达标；git_repo/task_dir fixture 组合语义留作后续批次注意点。
