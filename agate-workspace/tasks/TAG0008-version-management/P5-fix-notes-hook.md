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
