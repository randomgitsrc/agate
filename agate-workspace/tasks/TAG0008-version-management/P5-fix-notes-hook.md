---
phase: P5
task_id: TAG0008
type: implementation
parent: FIX-WINDOWS-TAG0008.md
trace_id: TAG0008-P5FIX1-20260816
status: draft
created: 2026-08-16
agent: implementer
---

# P5 修复轮 — 失败 1 `test_csg_1_readme_triggers_warning`（git→hook 边界）

## 根因（实证）

Windows CI 上 `git commit` 执行 copy 模式 hook 失败，hook 未真正运行。机制链（git-for-windows mingw.c 源码逐函数确认）：

1. `find_hook` → `mingw_access`（`_waccess(wfilename, mode & ~X_OK)`）：X_OK 被剥掉仅判文件存在 → 复制到 `.git/hooks/commit-msg` 的薄壳会被 git 找到。
2. `mingw_spawnvpe` → `parse_interpreter` 读薄壳首行 shebang `#!/usr/bin/env bash`：
   - `strrchr(buf+2,'/')` 取最后一段 + `strchr(p+1,' ')` 剥空格后选项 → 返回 **`env`**（`bash` 参数被丢弃）。
3. `path_lookup("env", 1)` 在 PATH 找 `env.exe`；找到后 `mingw_spawnve_fd(env.exe, argv=[hook,msgfile], prepend_cmd="env")` → CreateProcess 以 **`env <hook> <msgfile>`** 执行——**没有 bash**，hook 体依赖 env→(脚本 shebang)→env→bash 的 MSYS 嵌套递归。
4. 该 env 链在 CI 上不产生 hook 输出（实测 returncode==0 + 无 WARNING + 无 GATE ERROR + 无 "cannot spawn"）→ hook 未真正执行。薄壳 fail-closed（GATE ERROR+exit 1 阻断 commit）与 returncode==0 矛盾 → 排除"hook 跑了但 resolve 失败"。

关键证据：
- 决定性对照：unit `test_cmsg_1`（windows_smoke，Windows 通过）用 `bash <薄壳> <msgfile>` + AGATE_ROOT 直调同一薄壳链 → 薄壳+resolve-entry+commit-msg-self-gate.py 全链 Windows 可用。`test_csg_1` 唯一区别 = **git 调用 hook** → 失败点必在 git→hook 边界。
- 反证排除：`test_pre_commit_hook.py` / `test_pre_push_hook.py` 在 Windows 冒烟通过的 hook 用例**均不验证 git 触发后的 hook 输出**（只断言 returncode / install 产物）——不构成"git 能执行 copy hook"的证明；`test_csg_1` 是唯一要求 git→hook 真实输出的用例。

## 修复（方向 a：shebang）

3 个 hook 薄壳 shebang `#!/usr/bin/env bash` → `#!/bin/bash`：
- `agate/scripts/commit-msg-self-gate.sh`
- `agate/scripts/pre-commit-gate.sh`
- `agate/scripts/pre-push-gate.sh`

原理：`parse_interpreter` 对 `#!/bin/bash` 返回 `bash`（无参数可剥）→ git 直连 `bash <hook> <msgfile>`，绕开 env 链 / MSYS 嵌套 shebang 递归。bash.exe 在 GitHub windows runner PATH（`C:\Program Files\Git\usr\bin` / `bin`，runner 自身 shell 即 Git 的 bash.EXE）；Linux `/bin/bash` 恒在 → 跨平台等价。

范围说明：改 3 个而非仅 commit-msg-self-gate.sh——同根因同模式，pre-commit/pre-push 复制模式安装时同样受影响（pre-commit 是 fail-closed 阻断型，Windows 静默失效更严重）。一处一行注释说明原因。

## 验证

| 验证项 | 命令 | 结果 |
|---|---|---|
| 失败测试 | `python3 -m pytest agate/tests/integration/test_commit_msg_self_gate_integration.py -q` | 6 passed |
| 全量 pytest | `python3 -m pytest agate/tests/ -q` | 823 passed, 2 skipped（基线一致） |
| shellcheck | `shellcheck -S warning agate/scripts/*.sh` | 0 error |
| 用例数 | `bash agate/tests/scripts/count-tests.sh` | 825（无漂移） |
| consistency | `python3 agate/scripts/check-protocol-consistency.py` | 0 ERROR |
| Linux 模拟 | 复制 hook + `git commit`（新 shebang） | WARNING 出现 + rc=0（无回归） |

Windows CI 复跑为最终裁判（bash 直连路径），未在本机验证（无 Windows 环境）。

## 未触碰

- resolve-entry.py / commit-msg-self-gate.py（无改动，Windows 下经 bash 直调已由 test_cmsg_1 证明可用）。
- 测试文件未改（保留"git 调用 hook → WARNING"验证意图）。

[PROD_NOT_TOUCHED]

---

# rev2 — 修复轮 2（方法 B：测试适配 bash 包装 git）

## 前一轮被证伪

上轮（3500192，shebang → `/bin/bash`）push 后 Windows 冒烟**仍失败**：
`test_csg_1` 的 `assert "self-gate-review" in result.output` 仍失败，output 仅
`[master ...] update readme`，无 WARNING、returncode 0。说明 shebang 改动未触及真正根因。

## 新根因（rev2 实证收敛）

对照矩阵（全部经 Windows 冒烟实证）：

| 用例 | 调用方式 | Windows 结果 |
|---|---|---|
| unit `test_cmsg_1` | `bash` 直调薄壳 + AGATE_ROOT env | 通过（WARNING 出现） |
| integration `test_bdd_19` | **`bash -c "cd repo && git commit"`（bash 包装 git）** | 通过 |
| integration `test_csg_1` | **`git -C repo commit`（直接 spawn git）**，仅 env AGATE_ROOT | **失败**（hook 静默跳过） |

收敛结论：薄壳链 Windows 可用，**分歧在 git 进程的 spawn 上下文**。Windows 上 git 直接
spawn hook 走 `mingw_spawnvpe` → `parse_interpreter` 取 interpreter（`bash`）→
`path_lookup("bash", 1)` 在 **git 进程 PATH** 找 bash.exe。`test_csg_1` 直接 spawn git，
git 进程 PATH 不含 bash.exe → spawn 失败 → git **静默忽略 hook** → returncode 0 + 无输出。
`test_bdd_19` 经 bash 包装 git，git 进程 PATH 继承 bash 的 PATH（含 bash.exe）→ hook 正常触发。

> 注意：dispatch-context 提出反证（CI pytest 跑在 `bash.EXE ... -o pipefail` 下、PATH 理论上
> 含 Git bin），PATH 假设可能不成立——因此本修复同样以 **CI 实证为最终裁判**。方法 B 是
> dispatch-context 推荐的最可能最小修复（与 Windows 上已通过的既有测试模式一致）。

## 修复（方法 B：测试适配）

`agate/tests/integration/test_commit_msg_self_gate_integration.py` 的 `_commit` helper
改为 **bash 包装 git**，与 `test_bdd_19`（test_pre_commit_hook.py:1358-1390）一致：

```python
def _commit(run_cli, bash, repo, agate_root, *args):
    msg = " ".join(shlex.quote(a) for a in args)
    return run_cli(
        bash,
        "-c",
        f"cd {shlex.quote(str(repo))} && git commit {msg}",
        cwd=str(repo),
        env={"AGATE_ROOT": str(agate_root)},
    )
```

- 保留 `env={"AGATE_ROOT": ...}`（hook 复制模式依赖，经 bash 继承给 git/hook）——**不删**。
- 6 个 `test_csg_*` 全部改走 `_commit`，统一加 `bash` fixture（Windows 用 conftest bash fixture
  解析 Git Bash 完整路径，排除 System32 WSL bash）。
- **测试意图保留**：仍是"git commit 触发 commit-msg hook → self-gate WARNING"，只改变 git 进程
  的启动方式（spawn 上下文）。实现（薄壳/py）零改动。
- shebang 维持 `/bin/bash` 现状（Linux 全量无回归，Windows 下若 PATH 假设成立则两者配合生效；
  dispatch-context 允许维持现状）。

## 验证（本地 Linux）

| 验证项 | 命令 | 结果 |
|---|---|---|
| 失败测试 | `python3 -m pytest agate/tests/integration/test_commit_msg_self_gate_integration.py -q` | 6 passed |
| 全量 pytest | `python3 -m pytest agate/tests/ -q` | 823 passed, 2 skipped（无回归） |
| shellcheck | `shellcheck -S warning agate/scripts/*.sh` | 0 error |
| consistency | `python3 agate/scripts/check-protocol-consistency.py` | 0 ERROR |

**Windows 真实验证 = push 后 CI matrix 重跑**（本机 Linux 无法替代）。本地全绿仅自查。

## 未触碰

- 3 个 hook 薄壳（shebang 维持 `/bin/bash`，本次不改）
- resolve-entry.py / commit-msg-self-gate.py

[PROD_NOT_TOUCHED]

---

# rev3 — 修复轮 3（CI 实证诊断，不修复）

## 前两轮被证伪

| 轮 | 修复 | push | Windows CI 结果 |
|---|---|---|---|
| rev1（3500192） | 薄壳 shebang `#!/usr/bin/env bash` → `#!/bin/bash` | 3500192 | 仍失败 |
| rev2（605a0cc/436bbe6） | 测试 `_commit` 改 bash 包装 git | 436bbe6 | 仍失败 |

rev2 后 Windows 实际失败证据（gh run view 31962129661 --log-failed）：
`AssertionError: assert 'self-gate-review' in '[master f67bede] update readme\n 1 file changed, 1 insertion(+), 1 deletion(-)\n'`
returncode==0（commit 成功），output 无 WARNING、无 GATE ERROR、无 "cannot spawn" → **hook 静默未执行或输出全被吞**。

## 本轮策略：CI 实证诊断（临时诊断打印 a-e）

停止静态猜测。在 `test_csg_1` 加临时诊断打印，push 后从 Windows 真机拿证据：

- **[DIAG-a]** `sys.platform` / `bash` fixture 值 / `shutil.which('bash')` / `os.environ['PATH']` → bash 是否在 PATH、conftest bash fixture 解析结果
- **[DIAG-b]** `hook.exists()` / `os.access(hook, os.X_OK)` / mode → git `find_hook` 的 access(X_OK) 判定在 Windows 是否成立
- **[DIAG-c]** `git version` / `git -C repo config core.hooksPath` → hook 路径配置状态
- **[DIAG-d]** **手动执行 hook**：`bash <hook> <msgfile>`（带 AGATE_ROOT env + 不带 env 两路）→ 薄壳链在测试 repo 环境是否可用（对照 unit test_cmsg_1）
- **[DIAG-e]** commit 的 stdout/stderr 分离 → WARNING 是否被 git 吞/重定向

## 已收集证据（Linux 本地自查，非 Windows）

| 项 | Linux 结果 | 说明 |
|---|---|---|
| DIAG-a | `bash='bash'`, `which(bash)=/usr/bin/bash`, PATH 含 bash | Linux 正常 |
| DIAG-b | hook exists=True, access X_OK=True, mode 0o100755 | Linux 正常 |
| DIAG-c | git 2.43.0, core.hooksPath 空（rc=1） | Linux 正常 |
| DIAG-d 带 env | rc=0, stderr 出 GATE SELF-GATE WARNING | 薄壳链 Linux 可用 |
| DIAG-d 不带 env | rc=1, stderr 出 GATE ERROR（resolve-entry 失败 fail-closed） | 印证 AGATE_ROOT env 必要性 |
| DIAG-e | commit rc=0, WARNING 出现在 stderr，合并流含 self-gate-review | Linux 行为正确 |

**Windows 真机证据 = push 后 CI 输出**（本表仅证明诊断代码语法正确 + Linux 行为基线）。

## 待 push 决策（基于 CI 证据，分支判定）

- 若 DIAG-d 带 env 有 WARNING、DIAG-e 无 WARNING → git→hook 边界问题（spawn/解析）
- 若 DIAG-b X_OK False → find_hook 判定失败（chmod 语义）
- 若 DIAG-a PATH 缺 bash → bash 包装 git 无效的原因浮现
- 若 DIAG-d 也无 WARNING → 薄壳链在测试 repo 环境不可用（与 test_cmsg_1 对照差异定位）

## 状态（rev3 诊断两轮：a-e + f/g/h/i/j/k）

诊断打印已落盘 + 本地验证通过 + integration 6 passed + ruff 0 error。**push 后 CI 为裁判。**

---

# rev3 结论 — 根因（CI 实证，决定性证据）

## 诊断过程（多轮 CI 实证，从不猜）

| 轮 | push | Windows 证据 | 排除的假设 |
|---|---|---|---|
| rev3-r1 (4443e76) | DIAG-a..e | bash 在 PATH（`C:\Program Files\Git\usr\bin\bash.EXE`）；hook exists + X_OK；git 2.55.0.windows.3；手动 `bash <hook> <msgfile>` 出 WARNING；**git commit stderr 空** | PATH 缺 bash ✗；hook 文件缺失 ✗；薄壳链不可用 ✗ |
| rev3-r2 (f7b4e00) | DIAG-f/g/h | GIT_TRACE：git **确实 attempt** hook（`trace: start_command: .git/hooks/commit-msg`）；**trivial `#!/bin/bash` hook 经 git commit：TRIVIAL_HOOK_RAN + marker 创建成功** → git for windows 能执行 bash hook | "git 不能跑 .sh hook" ✗；"hook 未被执行" ✗（git 尝试+能跑）|
| rev3-r3/r4 (76b7644/98205cd) | DIAG-i/j | probe（== 真实薄壳链）经 git 调用：PROBE0→PROBE5-EXEC→PROBE6-RC=0 全链可跑；真实场景 staged README：PJ0-STAGED=README.md（git diff --cached 能看到 staged）→ resolve-entry exec → RC=0 **但 WARNING 未出现在重定向的 marker**（Linux 同场景 WARNING 入 marker）| 薄壳 resolve 失败 ✗；py 看不到 staged ✗ |
| rev3-r5 (d23e42e) | DIAG-k | **直接调 commit-msg-self-gate.py（绕过 resolve-entry）：PK3-STDERR=GATE SELF-GATE 完整 WARNING** + RC=0 | — |

## 根因（实证收敛）

```
git 能跑 bash hook（DIAG-g）→ 薄壳链 Windows 可用（DIAG-i）
→ 直接调 gate py 出 WARNING（DIAG-k：PK3-STDERR 完整）
→ 但经 resolve-entry 的 os.execv → WARNING 丢失（DIAG-j：marker 无 WARNING）
```

**`resolve-entry.py` 的 `os.execv(sys.executable, [.., gate_py, ..])` 在 Windows 上不继承已重定向的 std 句柄**——CPython 的 `os.execv` 在 Windows 走 `_wexecv`（posixmodule.c:5813，模拟 spawn 而非真 exec），新进程的 stdout/stderr 不会接到调用方的重定向目标 → gate py 的 GATE SELF-GATE WARNING 写到丢失的句柄，git stderr 为空，test 断言失败。

> 连带修复意义：pre-commit / pre-push 的 gate 输出（fail-closed 时 stderr）在 Windows 复制模式下同样经 resolve-entry → 同 bug。一个共享 fix 覆盖 3 个 hook。

## 修复

`agate/scripts/resolve-entry.py`：os.execv 仅在 POSIX 保留；Windows（`os.name == "nt"`）改用 `subprocess.run([py, gate, *rest])` + `sys.exit(rc)`：

```python
if os.name == "nt":
    import subprocess
    sys.exit(subprocess.run(
        [sys.executable, gate_path, *sys.argv[2:]]).returncode)
os.execv(sys.executable, [sys.executable, gate_path, *sys.argv[2:]])
```

- subprocess.run 默认继承父进程 stdout/stderr（未 capture_output）→ gate 输出直通 git。
- `sys.exit(rc)` 透传 gate 退出码（pre-commit fail-closed `exit 1` 语义保持）。
- **测试文件恢复 rev2 干净版本**（删光 4 轮临时诊断打印，`_commit` bash 包装 + AGATE_ROOT env 保留）。

## 验证（本地 Linux）

| 验证项 | 结果 |
|---|---|
| integration test_commit_msg_self_gate_integration.py | 6 passed |
| resolve-entry unit test_hook_resolve_entry.py | 5 passed |
| 全量 pytest | 823 passed, 2 skipped |
| ruff（resolve-entry.py + 测试文件）| 0 error |
| consistency | 0 ERROR |
| shellcheck | 0 error |

**Windows 真实验证 = push 后 CI 冒烟**（本地无 Windows，不宣称已修复）。

## 回滚预案

若 CI 仍失败 → resolve-entry 换回 os.execv（git revert resolve-entry 改动即可），诊断结论已完整落盘（rev3 各轮证据），主 Agent 可据证据决定后续方向。

[PROD_NOT_TOUCHED]
