---
phase: P6
task_id: TAG0010-python-migration
type: acceptance
parent: P5-test-results/unit.md
trace_id: TAG0010-P6-20260815
status: draft
created: 2026-08-15
agent: verifier
# ── v2.0 机器汇总 ──
pass: 10
fail: 0
ui_affected: false
regression_pass: true
---

# P6 验收报告 — TAG0010（agate 产品逻辑 Python 化，refactor 回归验收口径）

> change_type: refactor（P1 frontmatter）。P6 换用回归验收口径（三段式），非裁剪 P6。
> 验收时间：2026-08-15；执行：verifier subagent（P6 模式）；工作目录：`/home/kity/oclab/agate/.worktrees/agate-TAG0010`。

## 1. 行为不变声明节

verifier 自声明：本次重构仅改变内部实现（30 个 `agate/scripts/*.sh` 的 bash 逻辑迁移到 Python，3 个 hook 入口 pre-commit/commit-msg/pre-push 保留 sh 薄壳，`gate-result.sh` + `agate-workspace-resolve.sh` 并入 `agate_common.py`），不改外部行为（CLI 输出契约 `GATE ...:` 前缀 / exit code 0/1/2 语义 / `AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出 / gate-result.json 结构 / 既有任务数据格式 / consistency 锚点关键字）。判定依据 = 全量回归全绿 + 关键路径 BDD 逐条 PASS。**禁止为凑验收数量新增功能性质 BDD（禁止伪造功能 BDD）**——本次验收的 10 条 BDD 全部为 P1 §4 声明的关键路径行为不变断言，未新增任何 BDD。

## 2. 全量回归全绿节

- PASS BDD-1: 全量回归全绿（重构后完整测试套件 0 失败：sanity+unit+regression+integration 733 ok / 0 not ok，bats 真实 exit code 0；`count-tests.sh` @test 口径 727 与迁移前主 checkout 一致，用例数未减少）(P6-evidence/regression.log)

## 3. 关键路径验收节（BDD-2 到 BDD-10）

- PASS BDD-2: consistency --strict 0 ERROR 0 WARNING（`check-protocol-consistency.py --strict` exit 0，CHECK 1-9 全 PASS——py 版脚本保留表 C 锚点关键字/锚点表已同步）(P6-evidence/consistency-strict.log)
- PASS BDD-3: ruff 静态检查覆盖全部 agate/scripts/*.py 0 error（`ruff check agate/scripts/` exit 0，All checks passed，47 个 py 文件，按 P2 pyproject.toml 规则集）(P6-evidence/ruff-check.log)
- PASS BDD-4: shellcheck 覆盖面收敛到 3 个保留 hook 薄壳 0 error（`shellcheck -S warning` 对 `agate/scripts/*.sh` 受扫集合 == pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh 三个薄壳，无输出 exit 0；install-hook.sh 已 py 化，不在受扫集合）(P6-evidence/shellcheck.log)
- PASS BDD-5: Windows CI 冒烟机制就绪（本地 Linux 无法真机验证——按 P2-design.md §7 minimal_validation 已用 Linux 模拟覆盖关键平台机制：复制模式 .agate-root 恢复 confirmed + python 探测/失败回退 confirmed；Windows 真机行为标「待 Windows CI matrix 确认」，详见说明文件）(P6-evidence/bdd5-windows-ci-note.md)
- PASS BDD-6: 平台假设扫描器扩展覆盖 .py 且非空转（`check-platform-assumptions.py` 对 tests/ + scripts/*.py 扫描 0 命中 exit 0；check-platform-assumptions.bats 16 用例全绿，含 `.py` fixture 检出、docstring 豁免、裸 python3 检出用例——前置验证见 P2 §3.2 批次 1 BLOCKER-1）(P6-evidence/platform-scan.log, P6-evidence/bdd6-platform-assumptions.bats.log)
- PASS BDD-7: 新增 py 代码全部显式 encoding=utf-8（agate-scripts-encoding.bats 2 用例全绿：bdd-5 强守卫覆盖全部 `agate/scripts/*.py` 的 `open()`/`read_text()`，bdd-8 既有行为回归）(P6-evidence/bdd7-encoding.bats.log)
- PASS BDD-8: py 代码兼容 Python 3.8+（pyproject.toml `target-version = "py38"`；ruff 以该 target 对含 `match` 的样例拒绝报 invalid-syntax（P2 minimal_validation confirmed）；全部 py 在 py38 target 下 ruff 0 error）(P6-evidence/bdd8-py38.log, P6-evidence/ruff-check.log)
- PASS BDD-9: hook 薄壳保留复制模式 .agate-root 恢复 + python 探测 exec + 失败 fail-closed 阻断（install-hook.bats 6 用例 + pre-commit-hook.bats 48 用例 + helpers-python.bats 3 用例全绿，含 bdd-19 复制模式 hook 经 .agate-root 解析 AGATE_ROOT、复制模式安装提示重跑、bdd-17 probe_python 探测 python3→python 回退 + 失败返回空 fail-closed 阻断）(P6-evidence/bdd9-install-hook.bats.log, P6-evidence/bdd9-pre-commit-hook.bats.log, P6-evidence/bdd9-helpers-python.bats.log)
- PASS BDD-10: CLI 输出契约与既有数据兼容（agate-workspace-resolve.bats 10 用例全绿含 bdd-18 CRLF 剥离契约；直接实测：`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出不变、valid .state.yaml exit 0、invalid .state.yaml exit 1 + `GATE STATE-YAML:` 前缀不变）(P6-evidence/bdd10-workspace-resolve.bats.log, P6-evidence/bdd10-cli-contract.log)

**Summary**: 10/10 PASS, 0 FAIL

## 附注（供主 Agent 参考）

- **BDD-5 判定口径**：本地 Linux 环境无法真实执行 Windows CI matrix，PASS 基于 P2 minimal_validation（Linux 模拟覆盖） + 本次 Linux 实跑复核；Windows 真机行为（sh.exe shebang 解析 / 复制模式安装 / CRLF）仍待 CI `windows-latest` matrix 冒烟确认——主 Agent 在 P8/CI 阶段留意 CI 冒烟结果。
- **用例数**：bats 运行时 733（含 sanity.bats 与动态展开用例），`count-tests.sh` @test 口径 727，与迁移前主 checkout 一致（未减少）。
- **所有证据文件均被 PASS 行引用**（provenance 审计 1c 全覆盖）；P6-evidence/ 共 14 个文件。
