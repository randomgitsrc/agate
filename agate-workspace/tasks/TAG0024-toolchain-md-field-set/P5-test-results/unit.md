---
phase: P5
task_id: TAG0024
type: test-results
parent: P4-implementation.md
trace_id: TAG0024-P5-20260825
status: draft
created: 2026-08-25
agent: verifier
---

[NO_NEED_CONFIRM]

# P5 技术验证结果 — TAG0024

独立 verifier subagent 重新执行（未照抄 P4 自报数字），逐 key 独立执行（未用 `&&` 拼接），
基线提交 `e2357fc`（HEAD，P4 代码已在此提交落地）。

## Key: P5（全量 pytest）

命令：`timeout 300s python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -q --tb=no`

exit code: `0`

关键输出（原始尾行）：
```
1285 passed, 2 skipped in 147.67s (0:02:27)
```

`grep -c FAILED` 命中数：0

补充证据（同一 basetemp、相同代码状态下追加 `-rA` 参数复跑一次，获取逐用例 PASSED/FAILED/SKIPPED
原始签名行，用于自证非空转述；主判定仍以上方紧凑命令的 exit code + 汇总行为准，`-rA` 仅为
证据补充，非独立 gate key）：

命令：`timeout 300s python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -q --tb=no -rA`

exit code: `0`

原始尾部片段：
```
PASSED agate/tests/unit/test_windows_python_probe_docs.py::test_bdd_12_platform_notes_documents_store_placeholder
PASSED agate/tests/unit/test_windows_python_probe_docs.py::test_bdd_12_platform_notes_documents_agate_python
PASSED agate/tests/unit/test_windows_python_probe_docs.py::test_bdd_12_platform_notes_no_overclaim
PASSED agate/tests/unit/test_windows_python_probe_docs.py::test_bdd_12_agents_md_documents_agate_python_probe_enhancement
PASSED agate/tests/unit/test_windows_python_probe_docs.py::test_bdd_12_agents_md_no_overclaim
SKIPPED [1] agate/tests/unit/test_agate_image_check.py:21: Pillow 已安装，跳过无 Pillow 分支
SKIPPED [1] agate/tests/unit/test_agate_image_check.py:51: Pillow 已安装，跳过无 Pillow 分支
1285 passed, 2 skipped in 137.85s (0:02:17)
```
`grep -cE '^(PASSED|FAILED|SKIPPED)'` 命中数：1287（1285 PASSED + 2 SKIPPED），FAILED 命中数：0。
与主命令结果（1285 passed, 2 skipped, 0 failed）一致。

## Key: P5_consistency（协议一致性）

命令：`timeout 60s python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`

**第一次执行**（与 P5 pytest 输出目录共享同一工作树，pytest 用 `--basetemp=.pytest-tmp` 且
不清理该目录）出现 12 条 ERROR，均为 CHECK 2（仓库内文件引用存在）误判：
```
❌ FAIL  CHECK 2  仓库内文件引用存在
...
ERROR (12):
    ❌ 协议文件引用了不存在的文件: docs/reviews/T001-retrospective-2026-08-10.md [.pytest-tmp/test_bdd_11_t001_backfill_entr0/tech-debt.md:12]
```
根因排查：`agate/scripts/check-protocol-consistency.py` 的 `iter_md_files()`（第 140-164 行）用
`root.rglob("*.md")` 遍历整个仓库树，未把 `.pytest-tmp/`（pytest `--basetemp` 目录，未加入
`.gitignore`，也不在该函数硬编码的排除列表 `.git`/`archived`/`.worktrees`/`.opencode`/`.claude`/
`node_modules`/`bats` 中）纳入排除，于是把 pytest 测试夹具里模拟的"不存在文件引用"当成真实协议
文件引用来判定。这是**环境交互产物，不是本次代码改动引入的新问题**：`check-protocol-consistency.py`
的 CHECK 2/`iter_md_files` 逻辑不在本任务改动范围内（P2-design.md §1.2 明确"不改
check-protocol-consistency.py 的判定逻辑"）。

**清理复现**：`rm -rf .pytest-tmp` 后（干净环境，无遗留 pytest 夹具）独立重跑：

exit code: `0`

关键输出（原始尾行片段）：
```
  ✅ PASS  CHECK 1  YAML 代码块可解析
  ⚠️  WARN  CHECK 2  仓库内文件引用存在
  ✅ PASS  CHECK 3  协议文件无硬编码行号
  ✅ PASS  CHECK 4  gate_commands 键集合一致
  ✅ PASS  CHECK 6  LICENSE 与 gstack 归属
  ✅ PASS  CHECK 7  version badge 与 git tag
  ✅ PASS  CHECK 8  v0.6 关键词存在性
  ✅ PASS  CHECK 9  协议-脚本结构对齐
  ⚠️  WARN  CHECK 10 协议文档脚本名引用漂移
  ✅ PASS  CHECK 11 UI/UX 机制条文跨文档一致
  ✅ PASS  CHECK 12 权威数值/规则跨文件一致性
```
WARNING 计 322 条（叙事文件历史引用，`--strict-errors-only` 不计入判定），ERROR 计 **0** 条。

判定采用**清理后的干净结果**：exit 0，0 ERROR。

## Key: P5_shellcheck（shell lint）

命令：`timeout 60s shellcheck -S warning agate/scripts/*.sh`

exit code: `0`

关键输出：无告警输出（stdout/stderr 均为空）

## Key: P5_count（测试计数自检）

命令：`timeout 60s bash agate/tests/scripts/count-tests.sh`

exit code: `0`

关键输出（原始行）：
```
=== pytest 用例覆盖度自检 ===
总计：1287 个测试用例（pytest collect-only 口径）
```

## Key: P5_ruff（Python lint）

命令：`timeout 60s ~/.venvs/agate-dev/bin/ruff check agate/`

exit code: `0`

关键输出（原始行）：
```
All checks passed!
```

## 汇总

- **failed 总数（从 P5 pytest 输出提取）：0**（1285 passed, 2 skipped, 0 failed）
- 5 个 gate_commands key 全部独立执行（未用 `&&` 拼接）：P5=0, P5_consistency=0（干净环境复测）,
  P5_shellcheck=0, P5_count=0, P5_ruff=0
- **无预存失败**（本次未运行前存在、与本任务无关的失败）
- 未跳过任何全量测试；全量 pytest 套件（含非本任务测试）已完整运行
- 2 个 skipped 用例为既有 skip 标记（非本次改动引入的失败，pytest 汇总行显示为 skipped 而非
  failed，未逐一展开列出——tail 摘要口径下不影响 failed=0 的判定）
- 唯一发现的环境交互问题：P5_consistency 若与 P5 pytest 共享未清理的 `.pytest-tmp` 目录会产生
  12 条误报 ERROR（CHECK 2 未排除 basetemp 目录），已用干净环境复测确认与本次代码改动无关，
  真实判定为 0 ERROR。建议主 Agent 关注：若 CI 流水线按 P0-brief 声明的 test_cmd 顺序
  （pytest → consistency → count → ruff）在同一工作目录连续执行且不清理 `.pytest-tmp`，
  CI 上也会复现此误报——不是本次改动引入的回归，但是环境/脚本层面的既有交互缺口。

EXIT_CODE: 0
