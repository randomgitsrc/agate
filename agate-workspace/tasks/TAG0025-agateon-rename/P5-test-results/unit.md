---
phase: P5
task_id: TAG0025
type: test-results
parent: P4-implementation.md
trace_id: TAG0025-P5-20260826-rerun
status: draft
created: 2026-08-26
agent: verifier
---

[PROD_NOT_TOUCHED]

# P5 技术验证结果（修复后全量重跑）— TAG0025-agateon-rename

本文件**覆盖重写**首轮 P5-test-results/unit.md（不是叠加）。触发原因：首轮 P5 在
`P5_unit` 发现真实失败（`test_bdd_34_shellcheck_three_hook_shells_and_ruff`，根因是本任务
新增文件 `agate/tests/regression/test_repo_url_no_stale_rename.py:260` 的 ruff RUF005 违规
`CORE_FILES + ["CHANGELOG.md"]`），已回 P4 修复为语法等价的解包写法
`[*CORE_FILES, "CHANGELOG.md"]`（implementer 自查 3 条命令均通过，详见
P4-implementation.md「重试 1」节）。本次按 dispatch-context 约束 1（T027 教训：修复可能引入
回归，不能只检查修复项）**全量重新执行全部 24 个 `gate_commands.P5_*` key**，不只验证修复项。

独立 verifier subagent 执行，逐 key 独立跑（未用 `&&` 拼接）。执行前 HEAD commit：
`18a6b7b3f7e093d07a7bd3fc621aa02ea4617172`（P4 批次 2，修复本身尚未 commit，仍是工作区改动，
`git diff` 确认只有 `agate/tests/regression/test_repo_url_no_stale_rename.py` 一处一行改动）。
工作目录：`/home/kity/oclab/agate/.worktrees/agate-TAG0025`。执行时间：约
2026-08-26T06:20~06:33 +08:00。本任务不涉及生产数据库/生产 API，未执行任何写操作（`gh api
-X PATCH` 改名与 `git remote set-url` 均已在 P4 完成，本阶段未重复执行；BDD-15/16 相关的
`git remote -v`/`git fetch` 均为只读命令，按 dispatch-context 声明允许在主 checkout 执行）。

按 P2-design.md gate_commands 块，共 24 个 `P5_*` 前缀 key（其中 20 个是可独立执行的命令，
4 个是 formatter/timeout 元数据 key，非独立可执行命令，随对应主命令一并说明）。全部 24 个
逐条重新执行，逐条列出：

## 1. P5_unit — 单元测试全量（本次重点）

命令：`python3 -m pytest agate/tests/unit/ -q --tb=no`（外层 `timeout 200s`，declared budget
`P5_unit_timeout_seconds: 180`，实际耗时 94.56s，未触发 timeout）

exit code: `0`

结果：**0 failed, 1160 passed, 2 skipped**（首轮为 1 failed, 1159 passed, 2 skipped；本轮
failed 数由 1 变为 0，passed 数由 1159 变为 1160，与"修复了 1 个失败测试、未增删其他测试"
完全吻合）

```
........................................................................ [  6%]
..........................s.s........................................... [ 12%]
........................................................................ [ 18%]
........................................................................ [ 24%]
........................................................................ [ 30%]
........................................................................ [ 37%]
........................................................................ [ 43%]
........................................................................ [ 49%]
........................................................................ [ 55%]
........................................................................ [ 61%]
........................................................................ [ 68%]
........................................................................ [ 74%]
........................................................................ [ 80%]
........................................................................ [ 86%]
........................................................................ [ 92%]
........................................................................ [ 99%]
..........                                                               [100%]
1160 passed, 2 skipped in 94.56s (0:01:34)
```

单独复跑首轮失败的那个测试，交叉确认：

```
python3 -m pytest agate/tests/unit/test_env_adapt_docs.py::test_bdd_34_shellcheck_three_hook_shells_and_ruff -v
agate/tests/unit/test_env_adapt_docs.py::test_bdd_34_shellcheck_three_hook_shells_and_ruff PASSED [100%]
1 passed in 0.08s
```

**判定：修复确认生效，且全量 `agate/tests/unit/`（非仅该单个测试）未发现修复引入的任何新
回归**（1160 = 1159 + 1，其余全部测试仍为 passed/skipped，无新增 failed）。

**P5_unit_formatter**（`pytest.sh`）：用于把上述 pytest 输出标准化为 `PASSED`/`FAILED <id>`
签名行，已应用于下方「汇总」与 `fail-list.txt` 的提取（本次 `fail-list.txt` 为空文件）。

## 2. P5_other — 全量测试（排除 unit/）

命令：`python3 -m pytest agate/tests/ --ignore=agate/tests/unit -q --tb=no`（外层
`timeout 150s`，declared budget `P5_other_timeout_seconds: 120`，实际耗时 39.56s，
未触发 timeout；**P5_other_formatter**：`pytest.sh`，同上应用）

exit code: `0`

结果：**142 passed**（与首轮一致，覆盖 `agate/tests/regression/`、`agate/tests/integration/`、
`test_sanity.py`、`agate/tests/scripts/` 等）

```
........................................................................ [ 50%]
......................................................................   [100%]
142 passed in 39.56s
```

补充交叉核对（非 24 key 之一，供背景引用）：`python3 -m pytest
agate/tests/regression/test_repo_url_no_stale_rename.py -v` → **11 passed in 0.15s**（全部
11 个测试函数逐条 PASSED，含含有修复行的 `test_bdd_9_seven_urls_same_commit_batch_atomicity`）；
`ruff check agate/tests/regression/test_repo_url_no_stale_rename.py` → `All checks passed!`

## 3. P5_consistency — 协议一致性检查

命令：`python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`

exit code: `0`

结果：**0 ERROR**（323 条 WARNING，与首轮一致，均为既有叙事文件历史引用，`--strict-errors-only`
不计入判定，本次修复未涉及任何叙事文件，数字理应不变，实测确认不变）

## 4. P5_shellcheck — shell lint（覆盖 `agate/scripts/*.sh` + `install.sh`）

命令：`shellcheck -S warning agate/scripts/*.sh install.sh`

exit code: `0`

结果：**无告警输出**（stdout/stderr 均为空，与首轮一致）

## 5. P5_count_tests — 测试用例计数自检

命令：`bash agate/tests/scripts/count-tests.sh`

exit code: `0`

结果（原始行）：
```
=== pytest 用例覆盖度自检 ===
总计：1304 个测试用例（pytest collect-only 口径）
```

**实际数字 1304，与首轮一致**。按 dispatch-context 约束 3（本次口径已核实：`count-tests.sh`
按测试函数计数，本任务净增 11 个测试函数（不是 1 个文件），预期数字为 1304 = 1293 基线 + 11）
判断，此次修复未增删任何测试函数，数字与首轮完全一致，符合预期。（注：P2-design.md 原文声明
的预期"1294"是按"+1 个文件"折算的口径误差，已在首轮记录中说明，本次不重复展开，只确认数字
未漂移。）

## 6. P5_bdd1_readme_en

命令：`head -15 README.md | grep -F 'Agateon (formerly agate)'`

exit code: `0` → **PASS**（与首轮一致）

## 7. P5_bdd2_readme_zh

命令：`head -15 README.zh-CN.md | grep -E 'Agateon.*agate|agate.*Agateon'`

exit code: `0` → **PASS**（与首轮一致）

## 8. P5_bdd3_unreleased_section

命令：`grep -n '^## \[Unreleased\]' CHANGELOG.md`

exit code: `0` → **PASS**（`11:## [Unreleased]`，与首轮一致）

## 9. P5_bdd3_tag0025_entry

命令：`grep -n TAG0025 CHANGELOG.md`

exit code: `0` → **PASS**（`13:### 变更（TAG0025：Agateon 品牌改名执行 Phase 0-1，RM-AG0035 剩余工作②）`，
与首轮一致）

## 10. P5_bdd4to8_new_url_present

命令：`for f in install.sh agate/scripts/agate-install.py agate/scripts/agate-changes.py README.md README.zh-CN.md; do grep -q randomgitsrc/agateon "$f" || { echo "MISSING:$f"; exit 1; }; done; echo OK`

exit code: `0` → **PASS**（输出 `OK`，5 个文件均含新 URL，与首轮一致）

## 11. P5_bdd9_atomic_commit

命令：批次内 5 个文件 + install.sh 逐文件 `git log -1 --format=%H` 比对

exit code: `0` → **PASS**（输出 `OK:751f421a4c36becd657ab12fed0e80cd7423bef3`，6 个文件全部落在
同一 commit，与首轮一致——本次修复未触碰这 6 个文件，该 commit SHA 理应不变，实测确认不变）

## 12. P5_bdd10_residual_scan — 全仓残留扫描（5 类豁免）

命令：`grep -rn 'randomgitsrc/agate\b' --include=*.md --include=*.py --include=*.sh --include=*.yml --include=*.yaml . --exclude-dir=.git --exclude-dir=.worktrees | grep -vE '<5类豁免正则>'`

exit code: `1`（shell 版本命中，非 exit 0，与首轮一致）

命中内容（原样，共 6 行，**全部来自同一个文件**，与首轮完全一致的行号/内容）：
```
./agate/tests/regression/test_repo_url_no_stale_rename.py:6:...
./agate/tests/regression/test_repo_url_no_stale_rename.py:9:...
./agate/tests/regression/test_repo_url_no_stale_rename.py:38:OLD_URL_PATTERN = re.compile(r"randomgitsrc/agate\b")
./agate/tests/regression/test_repo_url_no_stale_rename.py:92:...
./agate/tests/regression/test_repo_url_no_stale_rename.py:195:...
./agate/tests/regression/test_repo_url_no_stale_rename.py:286:...
```

**判定：已知盲区（dispatch-context 约束 2），非真实残留**。本次修复（第 260 行一处语法等价
替换）不涉及第 6/9/38/92/195/286 行任何一行，因此盲区命中内容与首轮逐字一致，符合 dispatch
-context 约束 2 的预期（"修复 ruff 违规不影响这个问题，两者无关"）。按约束 2 的精确规则核对：
失败输出**只**包含 `agate/tests/regression/test_repo_url_no_stale_rename.py` 自身的行（不多
不少），没有命中其他任何文件——该 shell key 的 5 类豁免排除正则未覆盖该测试文件自身的文档
字符串（出于说明目的引用了字面 `randomgitsrc/agate`）。这不算 gate 失败。

以 pytest 版本 `test_bdd_10_repo_wide_residual_scan_zero_after_exemptions` 为 BDD-10 权威判定，
单独执行确认：

命令：`python3 -m pytest agate/tests/regression/test_repo_url_no_stale_rename.py::test_bdd_10_repo_wide_residual_scan_zero_after_exemptions -v`

exit code: `0` → **PASSED**

```
agate/tests/regression/test_repo_url_no_stale_rename.py::test_bdd_10_repo_wide_residual_scan_zero_after_exemptions PASSED [100%]
1 passed in 0.13s
```

## 13. P5_bdd12_301_status

命令：`curl -sI https://github.com/randomgitsrc/agate | grep -Eq '^HTTP/[0-9.]+ 301'`

exit code: `0` → **PASS**（实测响应头 `HTTP/2 301`，与首轮一致）

## 14. P5_bdd12_301_location

命令：`curl -sI https://github.com/randomgitsrc/agate | grep -qi '^location:.*randomgitsrc/agateon'`

exit code: `0` → **PASS**（实测响应头 `location: https://github.com/randomgitsrc/agateon`，
与首轮一致）

## 15. P5_bdd13_ls_remote

命令：`timeout 30 git ls-remote https://github.com/randomgitsrc/agateon.git HEAD | grep -qE '^[0-9a-f]{40}[[:space:]]+HEAD'`

exit code: `0` → **PASS**（与首轮一致）

## 16. P5_bdd14_search — GitHub 搜索索引

命令：`gh api -X GET search/repositories -f q='agateon in:name' --jq '.items[].full_name' | grep -qx randomgitsrc/agateon`

exit code: `0` → **PASS**（首次执行即命中，`randomgitsrc/agateon` 在结果中，未出现索引延迟，
无需复跑；与首轮一致）

## 17. P5_bdd15_remote_main

命令：`git -C /home/kity/oclab/agate remote -v | grep -q randomgitsrc/agateon`（只读命令，
dispatch-context 声明允许在主 checkout 执行）

exit code: `0` → **PASS**（`origin https://github.com/randomgitsrc/agateon.git (fetch/push)`，
与首轮一致）

## 18. P5_bdd15_remote_worktree

命令：`git -C /home/kity/oclab/agate/.worktrees/agate-TAG0025 remote -v | grep -q randomgitsrc/agateon`

exit code: `0` → **PASS**（与首轮一致）

## 19. P5_bdd16_fetch_main

命令：`git -C /home/kity/oclab/agate fetch`（只读 fetch，未做任何写操作）

exit code: `0` → **PASS**

## 20. P5_bdd16_fetch_worktree

命令：`git -C /home/kity/oclab/agate/.worktrees/agate-TAG0025 fetch`

exit code: `0` → **PASS**

## 21-24. 元数据 key（非独立可执行命令，随对应主命令说明）

- **P5_unit_formatter**：`"pytest.sh"` — 已应用于第 1 节输出的标准化提取
- **P5_unit_timeout_seconds**：`180` — 实际执行外层用 `timeout 200s`（declared 180s），
  实际耗时 94.56s，未触发任一 timeout，数值无影响
- **P5_other_formatter**：`"pytest.sh"` — 已应用于第 2 节输出的标准化提取
- **P5_other_timeout_seconds**：`120` — 实际执行外层用 `timeout 150s`（declared 120s），
  实际耗时 39.56s，未触发任一 timeout，数值无影响

## 汇总

- **24 个 `P5_*` key 全量重新执行完毕**（20 个可执行命令 + 4 个 formatter/timeout 元数据 key），
  非仅验证首轮修复项
- **failed 总数：0**（首轮唯一失败 `test_bdd_34_shellcheck_three_hook_shells_and_ruff` 本次
  确认 PASSED；全量 `agate/tests/unit/` 重跑未发现该一行语法等价替换引入的任何其他新问题）
- `P5_bdd10_residual_scan`（shell 版）exit 1，但按 dispatch-context 约束 2 精确判定为**已知
  盲区、非真实残留**，与首轮内容逐字一致（本次修复不涉及这些行）；未计入 failed 总数；权威
  判定 `test_bdd_10_repo_wide_residual_scan_zero_after_exemptions` PASSED
- `P5_count_tests` 实际输出 **1304**，与首轮一致，符合 dispatch-context 约束 3 核实后的预期
  （1293 基线 + 11 个测试函数），未漂移
- **无 PROD_TOUCHED**：全程 `[PROD_NOT_TOUCHED]`，未执行任何写操作（改名/remote 迁移均已在
  P4 完成，本阶段仅只读验证）
- 全量测试已真正运行（`P5_unit` + `P5_other`，非仅本任务 `regression/` 子集，也非仅重跑首轮
  失败的单个测试）
- 无预存失败（本轮 0 failed，无需登记 known-failures.md）
- BDD-14（GitHub 搜索）首次即命中，无需复跑
- BDD-12~16（改名后验收锚 + remote 迁移验证）全部 PASS，与首轮及 env-rename-handoff.md §六
  记录一致
- 与首轮的差异点仅限于：`P5_unit` 由 `1 failed, 1159 passed` 变为 `0 failed, 1160 passed`；
  其余 19 条可执行 key 结果与首轮逐一比对完全一致（数值/输出未漂移）

EXIT_CODE_SUMMARY: 0 failed across all 24 P5_* keys (20 executable commands all PASS, including
the previously-failing P5_unit which now shows 0 failed / 1160 passed / 2 skipped after the P4
ruff-RUF005 fix; P5_bdd10_residual_scan shell version resolved via documented known-blind-spot
rule, authoritative pytest equivalent PASSED); P5_count_tests reports 1304, consistent with
round 1 and with dispatch-context's confirmed expectation.
