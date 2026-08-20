---
phase: P3
task_id: TAG0017-toolchain-fixes
batch: fg4-windows-python-probe
agent: test-designer
test_code_dir: agate/tests
---

## 批次 fg4-windows-python-probe（BDD-10/11/12）

> DEBT0014：3 个 hook 薄壳（`pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh`）python 探测循环增强 + Windows 已知限制文档化。
>
> **诚实边界（P0-brief 约束 3，本批次强制）**：本环境是 Linux，无法真实触发 Windows Store `python3.exe` 占位符（exec 非交互模式 exit 49）。以下集成测试全部用**模拟 stub**（构造一个 exit 非零的假可执行文件放进 fake PATH 目录）复现"候选被 `command -v` 找到但不可正常执行"这一症状特征，不代表已在真实 Windows 环境验证；Windows 真实场景由 GitHub Actions Windows CI matrix（`pytest -m windows_smoke`）冒烟兜底（P2-design.md §8 minimal_validation 已用等价模拟 stub 验证判据逻辑可行）。

### BDD-10：探测循环命中不可执行的候选时能继续探测下一候选

- **对应 P1 BDD**：`#### BDD-10`（P1-requirements.md L198-201）
- **测试文件**：`agate/tests/integration/test_pre_commit_hook.py`
- **测试函数**：`test_bdd_10_probe_skips_unexecutable_candidate`（`@pytest.mark.parametrize("hook_filename,gate_py_filename", _PROBE_HOOKS)`，参数化跑 3 个 hook：`pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh`，共 3 个用例实例）
- **场景设计**：
  1. `_build_probe_workflow_root()` 构造一个独立 `workflow_root/scripts/`（复制目标 hook 薄壳 + `resolve-entry.py` + `agate_common.py`，把对应真 gate py 换成只打印 marker 字符串 `AGATE_PROBE_TEST_OK` 的假实现），薄壳直落 `workflow_root/scripts/` 下（非软链），依赖薄壳自身的 `readlink -f` 自定位到该临时根（等价 `test_agate_root_self_locate_worktree`/T086 已验证的模式）。
  2. `_make_broken_python3_stub()` 在 `fake-bin1/` 下放一个 `python3`（`#!/bin/sh\nexit 49\n`，可执行位已设置，模拟 Store 占位符"能被 `command -v` 找到但一律非零退出、忽略传入参数"的症状）。
  3. `_make_working_python_stub()` 在 `fake-bin2/` 下放一个 `python`（软链到本机真实 `python3`，模拟探测循环的第二候选正常可用）。
  4. `PATH="fake-bin1:fake-bin2:$真实PATH"`（保留真实 PATH 末尾，确保 `dirname`/`readlink`/`tr` 等 coreutils 仍可用，只有 `python3`/`python` 名字命中前置 fake 目录），`AGATE_ROOT=""` 触发薄壳自定位分支，直接 `bash <hook_path>` 运行（不经 git commit）。
- **断言（期望的修复后行为）**：`result.returncode == 0` 且 `AGATE_PROBE_TEST_OK in result.output`——即探测循环跳过不可执行的 `python3` stub，继续尝试 `python` 候选并成功 exec 到 `resolve-entry.py` → 假 gate py，打印 marker。
- **当前红灯**：手动复现 + pytest 实跑均确认，当前 3 个薄壳都在 `command -v python3` 命中 broken stub 后立即当作可用候选使用（无可执行性小测试），`exec "$PY" resolve-entry.py ...` 实际是在执行 broken stub 本身（`exit 49`，忽略参数），未继续探测 `python`。3 个参数化实例均 `returncode == 49`，marker 未出现，`AssertionError` 真实抛出（B 类失败）。

### BDD-11：显式指定的 Python 路径可跳过探测循环

- **对应 P1 BDD**：`#### BDD-11`（P1-requirements.md L203-206）
- **测试文件**：`agate/tests/integration/test_pre_commit_hook.py`
- **测试函数**：`test_bdd_11_agate_python_explicit_override_skips_probe_loop`（同样参数化跑 3 个 hook）
- **场景设计**：复用 `_build_probe_workflow_root()`；PATH 上只放 `fake-bin1/python3`（broken stub，唯一能找到的候选，故意不放可用候选，确保"若探测循环真的被执行"必然失败）；额外设置 `AGATE_PYTHON=<真实 python3 绝对路径>`。
- **断言（期望的修复后行为）**：`result.returncode == 0` 且 marker 出现——薄壳应直接使用 `AGATE_PYTHON` 指向的解释器，完全不执行 `command -v` 探测循环，因此不受 PATH 上唯一候选是 broken stub 这件事影响。
- **当前红灯**：3 个薄壳均未读取 `AGATE_PYTHON`，仍走 `for c in python3 python; do command -v "$c" ...` 探测循环，命中 PATH 上唯一存在的 broken `python3` stub，`returncode == 49`，marker 未出现，`AssertionError` 真实抛出。

### BDD-12：Windows 已知问题已在协议文档中说明（文档断言型，非交互）

- **对应 P1 BDD**：`#### BDD-12`（P1-requirements.md L208-211）
- **测试文件**：新增 `agate/tests/unit/test_windows_python_probe_docs.py`（纯文本断言，读文件 + grep 式检查，不涉及子进程）
- **读取范围**：
  - `platform-notes.md`「Windows 原生（Git for Windows，不用 WSL）」整节（`## Windows 原生...` 标题到文件末尾，含「已知限制（Windows 原生）」表，L85-169）
  - `AGENTS.md`「Gate 脚本分层」节（`## Gate 脚本分层` 到下一个 `## 依赖` 之间，约 L40-43）
- **正面断言（当前红灯，条目尚不存在）**：
  - `test_bdd_12_platform_notes_documents_store_placeholder`：章节含 `"Store"` + （`"占位符"` 或 `"placeholder"`）且提及 `"python3"`（定位到具体探测循环候选，而非泛泛的"Windows 有问题"）。**当前失败**：P1 同类扫描 3.6 已确认全仓 0 命中，`assert has_store_wording` 真实抛出。
  - `test_bdd_12_platform_notes_documents_agate_python`：章节含 `"AGATE_PYTHON"`。**当前失败**：0 命中，`AssertionError` 真实抛出。
  - `test_bdd_12_agents_md_documents_agate_python_probe_enhancement`：AGENTS.md「Gate 脚本分层」节含 `"AGATE_PYTHON"`（对应 P2-design.md §1.1 声明的"追加一句：探测循环支持 AGATE_PYTHON 显式覆盖 + 候选可执行性小测试"）。**当前失败**：`AssertionError` 真实抛出。
- **负面断言（诚实性护栏，BDD-12 要求"不含夸大断言"，当前天然为绿——文档条目本就不存在，谈不上夸大；P4 写入说明后此断言持续把关，防止实现阶段把"模拟 stub 回归验证"包装成"已实测通过"）**：
  - `test_bdd_12_platform_notes_no_overclaim` / `test_bdd_12_agents_md_no_overclaim`：断言两处文本均不包含 `"已在 Windows 实测通过"`（及 `"已在真实 Windows 环境实测通过"` / `"已在 Windows 环境实测通过"` / `"Windows 实测通过"` 三个变体）。当前通过（P4 实现阶段必须保持通过，不得倒退）。

### 红灯确认（本批次实跑记录）

```
$ python3 -m pytest agate/tests/integration/test_pre_commit_hook.py -k "bdd_10_probe or bdd_11_agate_python" agate/tests/unit/test_windows_python_probe_docs.py -q
...
FAILED test_pre_commit_hook.py::test_bdd_10_probe_skips_unexecutable_candidate[pre-commit]
FAILED test_pre_commit_hook.py::test_bdd_10_probe_skips_unexecutable_candidate[commit-msg]
FAILED test_pre_commit_hook.py::test_bdd_10_probe_skips_unexecutable_candidate[pre-push]
FAILED test_pre_commit_hook.py::test_bdd_11_agate_python_explicit_override_skips_probe_loop[pre-commit]
FAILED test_pre_commit_hook.py::test_bdd_11_agate_python_explicit_override_skips_probe_loop[commit-msg]
FAILED test_pre_commit_hook.py::test_bdd_11_agate_python_explicit_override_skips_probe_loop[pre-push]
FAILED test_windows_python_probe_docs.py::test_bdd_12_platform_notes_documents_store_placeholder
FAILED test_windows_python_probe_docs.py::test_bdd_12_platform_notes_documents_agate_python
FAILED test_windows_python_probe_docs.py::test_bdd_12_agents_md_documents_agate_python_probe_enhancement
9 failed, 2 passed（负面断言）
```

全量 `agate/tests/` 收集（`--collect-only`）确认 1013 个测试正常收集，无导入/语法错误——本批次新增测试未破坏其他并行批次（fg1/fg2/fg3）产出。

### 未覆盖 / 边界说明

- 本批次未真实触发 Windows Store 占位符（环境限制，见诚实边界声明）；exit 49 的具体数值只用于让 broken stub "看起来像"占位符症状，实现侧判据按 P2-design.md 选定为**通用 exit code 判据**（任意非零即跳过），测试断言也只检查最终 `returncode == 0` + marker 出现，不绑定 exit 49 这个具体数值，避免测试对实现判据形式过度耦合。
- 未修改 `pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh` / `platform-notes.md` / `AGENTS.md` 本身——按 dispatch-context 约束，这些是 P4 implementer 的工作范围。
