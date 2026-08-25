# agate 开发指引

> 面向**修改 agate 协议/脚本的开发者**。协议使用者看 `agate/AGENTS.md`。
> 本文件只收录"不读就不知道"的内容——项目特定规则、本机环境事实、历史教训。能从仓库自己读到的
> （目录结构、依赖、命令、CI 配置、协议正文）不重复，见各权威源（`agate/AGENTS.md`、
> `pyproject.toml`、`.github/workflows/`、`agate/tests/README.md`）。

## 仓库三块

- `<仓库根>/`：开发资料（README / CHANGELOG / docs/ / archived/）+ 本文件。**主 checkout 禁止改动**（worktree 开发时它是协议本体 + hook 的 AGATE_ROOT）
- `agate/`：协议本体，`~/.agate` 软链指向这里。改它触发 SELF-GATE（见下）
- `agate-workspace/`：任务数据（tasks/、roadmap/、debt/、reviews/ 等）。roadmap 回写 `done` 是 P8 gate 硬校验（RM-AG0043）

## 改脚本的工作流

1. **先加失败测试确认红** → 改脚本转绿
2. `python3 agate/scripts/check-protocol-consistency.py` 必须 0 ERROR（`--strict` 连 WARNING 都阻断；`--strict-errors-only` 只按 ERROR 判失败，docs-only PR 用它）
3. `bash agate/tests/scripts/count-tests.sh` 确认用例数未漂移
4. 新 bug 先写 `regression/` 测试再修
5. 暂存区含 self-gate 触发文件时，commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由（commit-msg hook 检查，WARNING 不拦截）；触发文件面见 `SELF-GATE.md`

## Gate 脚本分层

- 所有 `git diff` 用 `--cached`，不用 `HEAD~1`——pre-commit hook 运行时 commit 还没创建
- `grep -c || echo 0` 后必须 `| tail -1`——grep 无匹配 exit 1，`|| echo 0` 产生双行
- `printf '%b' "$VAR"`，不用 `printf '%s'`（不解释 `\n`）也不用 `printf "$VAR"`（SC2059）
- Python 调用用 `os.environ`，不用 `open('$VAR')`——shell 注入风险
- 所有脚本 `set -euo pipefail`
- `agate_common.py` 是公共函数库（被 import，不直接执行）：`write_gate_result` / `read_state_phase` / `read_state_task_id` / `resolve_workspace` 等
- 3 个 hook 是 sh 薄壳（`pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh`），只做 AGATE_ROOT 自定位 + python 探测 + exec py 主程序；python 探测支持 `AGATE_PYTHON` 显式覆盖（Windows Store python3 占位符规避，DEBT0014）

## 依赖

运行 agate 只需系统 `python3` + `pyyaml`；开发 agate 本体另需 `ruff`（CI 锁 `ruff==0.16.4`）。完整清单与版本锁定见 `pyproject.toml` + `.github/workflows/protocol-tests.yml`，不在此重复。

## 测试约定（平台无关是硬约束）

- 测试**不得硬编码单平台假设**：不裸 `PATH="/usr/bin:/bin"`、不裸 `python3`（探测 `python3|python`）、不假设 POSIX symlink 语义（Windows `ln -sf` 退化为复制）、不用 `/tmp`（用 pytest `tmp_path` fixture）
- 平台差异场景**按平台分支断言**（Linux 断软链，Windows 断"复制模式 + WARNING"）或用模拟环境覆盖
- Linux 全量覆盖；Windows CI 只跑 `-m windows_smoke` 冒烟（每文件第 1 个用例 + 平台敏感关键词用例）
- fixture 细节读 `agate/tests/conftest.py`；CI 无 `~/.agate`，conftest 用 `AGATE_ROOT` env 覆盖（本地可设）或从 tests/ 上溯反推

## dogfooding 工作流（agate 自身改造任务必读）

> **触发块**：任何 agate 自身改造任务（TAG0004+）需要隔离 worktree 时，**必须先读**：
> - 构建流程：`docs/guides/worktree-dogfooding-guide.md`（10 步标准流程）
> - 交接单模板：`agate/assets/templates/handoff-template.md`（复制到 worktree 根 `HANDOFF-{Txxx}.md` 填写）

- **双工作区**：改造对象 = worktree 的 `agate/`；开发工具 = `~/.agate`（稳定版，**勿动**）。跑 gate/读卡片用 `~/.agate`，改代码/跑测试在 worktree
- **gate 工具 ≠ 检查对象**：commit hook 用 `~/.agate`（稳定版）判定；但 `check-protocol-consistency.py` **必须用 worktree 自己的**（否则扫到主 checkout 的协议文件）
- **编排/派发类工具一律用 `~/.agate/scripts/` 稳定版**：`agate-inject-card.py` / `agate-render-dispatch-prompt.py` / `agate-next-card.py` 等有 AGATE_ROOT 自解析逻辑，worktree 相对路径调用会读到 worktree 正在修改的协议卡片，把未发布的新机制注入任务（TAG0016 教训）
- `~/.agate` 脚本在 worktree 跑显示主 checkout 上下文（`agate-summary.py` 显示稳定版版本，不代表 worktree 状态）

**工具纪律（本环境实战验证，T001/TAG0004 起）**：
- bash 一律加 `timeout`（外层 `timeout N cmd`，N 按预期耗时 30-90s），工具 timeout 参数同步设——无 timeout 的 bash 多次被 abort/挂起
- 单步串行不并行 bash（并行是 abort 高危）；卡住就换路不重试同一 bash，改用 read/grep/glob 工具（不走 bash 通道）
- 全量 pytest 分 unit/regression/integration 片跑、每片大 timeout；gate/consistency 单跑
- 输出控制在几十行内；先看全输出再分析，不用 tail 截断（count-tests 教训：数字被 tail 吞掉误判）
- commit 前检查 hook 会跑什么：pre-commit 按 .state.yaml phase 跑 check-gate，commit 时 phase 应与本次产出一致（P1 产出 → phase=P1 再 commit），否则 hook 拦截
- hook 在共享 git 目录：worktree 的 `.git/hooks` 为空，hook 实际在 `<主 checkout>/.git/hooks/`（pre-commit / commit-msg / pre-push 软链已装），改 hook 装那里
- CI 等待用 `gh pr checks <PR> --watch [--fail-fast]`，不手写 jq 轮询（2026-08-18 教训）
- git 脚本不在 bash PATH 时用绝对路径：`/home/kity/bin/git-to-pr` / `/home/kity/bin/git-to-main`（非交互 shell 不读 bashrc，2026-08-18 确认）

## 版本发布清单（教训浓缩）

1. pytest 全绿 + 0 consistency ERROR + 0 shellcheck error（用例数以 `count-tests.sh` 为准）
2. 更新 `README.md` version badge + `CHANGELOG.md` [Unreleased] → 新版本号
3. **更新 `agate/UPGRADING.md` 新增本版本章节**——无破坏性变更也写"（无破坏性变更）"（v0.62.0 教训：漏写章节）
4. `git tag vN.N.0 && git push origin vN.N.0`——`git push` 不带 tag **默认不推送 tag**（v0.51.0 教训）；推送后 `git ls-remote --tags origin vN.N.0` 验证远端到达
5. CHECK 7（version badge vs git tag）自动通过；CI ruff job 绿（`ruff==0.16.4`，与本地 `~/.venvs/agate-dev/bin/ruff` 对齐，RM-AG0037 required check）
6. **release PR 合并后最终验证（G-5）**：`git fetch origin && git describe --tags origin/main` == vN.N.0；`git merge-base --is-ancestor vN.N.0 origin/main` 返回 0；合并后 push 的 CI 全绿

**版本引用文件清单（agate 仓库特有，通用 P8 卡不覆盖）**：README badge / CHANGELOG / UPGRADING 章节 / 稳定版引用（文档优先写"稳定版"不写死版本号）。

**CI 一致性失败诊断（E-3，v0.51.0 教训）**：本地绿 CI 红 → 先拉 CI job 完整日志（`gh api repos/{owner}/{repo}/actions/jobs/{id}/logs`）看真实 FAIL 的 `CHECK N` 归属，**禁止臆测根因**；CHECK 7 FAIL 第一排查项 `git ls-remote --tags origin vN.N.N`。

**release PR 必须普通 merge（`--no-ff`），禁止 squash**：CHECK 7（`check_version_badge`）与 G-5 验证都用 `git describe --tags --abbrev=0` 取最新 tag；squash 生成内容相同但 SHA 不同的新提交，tag 与 main 分叉、describe 回退旧版（v0.31.0 事故）。若确实用了 squash：`git tag -f vN.N.0 <main-commit> && git push origin vN.N.0 --force`。
