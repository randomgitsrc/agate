# BDD-5 Windows CI 冒烟 — 本地验收说明（2026-08-15）

## 判定

**PASS（待 Windows CI 真机确认）** —— 本地 Linux 无法真实运行 Windows CI matrix，
按 P2-design.md §7 `minimal_validation` 已用 Linux 模拟覆盖关键平台机制；
Windows 真机行为（sh.exe 解析 shebang / 复制模式安装 / CRLF / 命令名差异）
由 GitHub Actions `windows-latest` matrix 冒烟（`check-windows-smoke.sh` 代表用例）兜底。

## P2 minimal_validation 结果引用（P2-design.md §7）

| assumption | result | 本地实测结论 |
|---|---|---|
| hook 薄壳 python 探测（python3→python）+ exec 失败回退 | **confirmed** | 真 python 存在 → exec py 主程序成功（PY_MAIN_RAN + exit 0）；python3 stub exit 127 且 python 缺失 → 回退 sh fallback（exit 3，非静默放行） |
| 复制模式 `.agate-root` 恢复（薄壳语义） | **confirmed** | 模拟环境（hook 副本目录含 `.agate-root` 标记、本体 scripts/ 不存在）→ 读标记恢复 AGATE_ROOT（RECOVERED_AGATE_ROOT=真实本体路径 + SCRIPTS_DIR_OK） |
| ruff select 规则集让既有 18 py 零违规 | **confirmed** | 候选规则集报 60 错误，54 个 --fix 自动修复（行为保持），剩 6 个 --unsafe-fixes/极小手工调整归零 |
| ruff target-version=py38 拒绝 3.10+ 语法 | **confirmed** | match 语句报 invalid-syntax；str.removeprefix 属运行期方法（局限，靠 code review + 单测覆盖） |
| 纯代码逻辑无外部系统依赖 | **not_needed** | 依赖仅 Python 标准库 + pyyaml，Windows 专属行为由 CI 冒烟覆盖 |

## 本次 P6 复核（Linux 侧对应机制的实跑证据）

- 复制模式 `.agate-root` 恢复：`bdd9-pre-commit-hook.bats` 中 `bdd-19 pre-commit-gate 复制模式 hook 经 .agate-root 标记正确解析 AGATE_ROOT`（ok 48）——见 `bdd9-pre-commit-hook.bats.log`
- 复制模式安装：`bdd9-install-hook.bats` `ok 6 install-hook: ln 复制模式下 pre-push hook 以复制安装并提示重跑（BDD-18/19）`——见 `bdd9-install-hook.bats.log`
- python 探测 fail-closed：`bdd9-helpers-python.bats` `ok 3 bdd-17 probe_python 探测 python3→python 回退 + 失败返回空（fail-closed 阻断）`——见 `bdd9-helpers-python.bats.log`

## 待确认事项（留给主 Agent / CI）

Windows `windows-latest` matrix 冒烟执行后需确认全绿；本 P6 验收将 BDD-5 判定为
「PASS（基于 minimal_validation + Linux 实跑，真机行为待 CI 确认）」。
