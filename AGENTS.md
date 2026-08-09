# agate 开发指引

> 本文件面向**修改 agate 协议/脚本的开发者**。协议使用者看 `agate/AGENTS.md`。

## 仓库结构

- `agate/` — 协议本体（`~/.agate` 软链接指向这里）
- `docs/` — 开发资料（评审、计划、竞争分析），改协议不改这里
- `archived/` — 历史验证文档
- `SELF-GATE.md` — agate 自身变更的 gate（改协议/脚本时必读）

`agate/` 内部关键目录：
- `scripts/` — gate 检查脚本（bash + python3）
- `tests/` — bats 测试（用例数以 `count-tests.sh` 输出为准）
- `phase-cards/` — 阶段卡片（渐进披露，主 Agent 按需加载）
- `assets/` — 角色/模板文件
- `rules/` — 跨阶段规则

## 依赖

- Bats ≥ 1.2.0（需要 `BATS_TEST_TMPDIR`）
- Python 3.8+ + `pyyaml` + `Pillow`（`pip install pyyaml Pillow`，Pillow 可选）— 检查逻辑抽离为独立 `.py` 工具（`agate/scripts/agate-*.py`），由 `.sh` 薄壳调用。其中 state/vision 类工具（agate-state-get / agate-retreat-state / agate-state-yaml-check / agate-vision-blocker）依赖 pyyaml；agate-image-check 依赖 Pillow（可选，用于像素方差/average hash 检测）
- shellcheck

## 开发命令

```bash
# 跑全部测试（必须全过才能 commit）
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/

# 跑单个脚本的测试
bats agate/tests/unit/check-pruning.bats

# 一致性检查（0 ERROR 才行；--strict 让 WARNING 也阻断；--json 机器可读）
python3 agate/scripts/check-protocol-consistency.py

# shellcheck（CI 用 -S warning）
shellcheck -S warning agate/scripts/*.sh

# 测试用例计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh
```

## 改脚本的工作流

1. **先加失败测试**，确认测试红
2. 改脚本，确认测试绿
3. 跑 `python3 agate/scripts/check-protocol-consistency.py` 确认无 ERROR
4. 跑 `bash agate/tests/scripts/count-tests.sh` 确认用例数未漂移
5. 发现新 bug → 先写 `regression/` 测试再修

## 脚本关键约定

- **所有 `git diff` 用 `--cached`**，不用 `HEAD~1`——pre-commit hook 运行时 commit 还没创建
- **`grep -c || echo 0` 后必须 `| tail -1`**——grep 无匹配时 exit 1，`|| echo 0` 产生双行 `0\n0`
- **`printf '%b' "$VAR"`**，不用 `printf '%s'`（不解释 `\n`）也不用 `printf "$VAR"`（SC2059）
- **Python 调用用 `os.environ`**，不用 `open('$VAR')`——shell 注入风险
- **所有脚本 `set -euo pipefail`**
- **`gate-result.sh` 是工具函数库**（被 source，不直接执行），提供 `write_gate_result`、`read_state_phase`、`read_state_task_id` 等

## 测试约定

- 测试框架：Bats ≥ 1.2.0（需要 `BATS_TEST_TMPDIR`）
- 临时文件用 `$BATS_TEST_TMPDIR`，不用 `/tmp`
- `create_task_dir` 默认写入 `agent: test` frontmatter + Given 行；`--no-state-yaml` 跳过 .state.yaml
- mock pytest：`TEST_RUNNER` 环境变量指向 fake 脚本，无需真实 pytest
- fixture `.state.yaml` 以 `.` 开头，`git add` 需 `-f` 才能暂存
- helpers：`load.bash`（AGATE_ROOT 解析）→ `fixtures.bash`（create_task_dir 等）→ `git-helper.bash`（git_init / git_commit / git_stage）
- 每个 .bats 文件第一行 `load "tests/helpers/load.bash"`
- **CI 里 `~/.agate` 软链接不存在**——`load.bash` 通过 `BATS_TEST_DIRNAME` 反推 `AGATE_ROOT`，本地也可设 `AGATE_ROOT` 环境变量覆盖

## 改 agate 协议本体的检查清单

改协议文档或脚本时，遵循 **SELF-GATE.md**（agate 自身变更的 gate）。

触发 self-gate 的文件：`agate/scripts/*.sh`、`agate/scripts/check-protocol-consistency.py`、`agate/*.md`、`agate/**/*.md`、`SELF-GATE.md`。

commit 时 `commit-msg-self-gate.sh` hook 会检查：暂存区含触发文件时，commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由，否则 WARNING（不拦截）。

## CI

单一 workflow（`protocol-tests.yml`），push/PR 自动触发：
- **bats**：unit + regression + integration + sanity
- **shellcheck**：`shellcheck -S warning agate/scripts/*.sh`
- **consistency**：`python3 agate/scripts/check-protocol-consistency.py`
- **gate-backstop**：`python3 agate/scripts/ci-gate-backstop.py`（push 后重跑 gate + P6 git blame 单 author WARNING）

## v2.0 改造期间执行约定（T001，2026-08-09 起）

> 本任务（agate v2.0 结构化改造，T001）期间的跨会话约定，避免重复踩坑。

- **双工作区**：改造对象 = worktree 的 `agate/`（分支 feat/v2.0）；开发工具 = `~/.agate`（v0.35.0 稳定版，指向主 checkout，**勿动**）。跑 gate/读卡片用 `~/.agate`，改代码/跑测试在 worktree。主 checkout（`/home/kity/oclab/agate`）是协议本体，禁止改动。
- **任务编号空间**：本任务 `T001` 使用 agate 改造项目**独立编号**（从 T001 起），**不沿用**主 checkout git 历史里的 peekview 项目编号（T016-T090 系列）。校验器 `agate-state-yaml-check.py` 要求 `^T\d+$`。
- **工具纪律（卡死教训，2026-08-09 多次实战验证）**：
  - **bash 命令一律加 `timeout`**（外层 `timeout N cmd`，N 按命令预期耗时给 30-90s），工具 timeout 参数同步设（bash 工具 timeout 毫秒）。无 timeout 的 bash 在本环境多次被 abort/挂起。
  - **单步串行，不并行 bash**：一次只发一个 bash 调用；必须链多步时用 `&&` 且每步短。并行 bash 是 abort 高危。
  - **卡住就换路，不重试同一 bash**：bash 偶发长时间无响应。卡住后改用 read/grep/glob **工具**（它们不走 bash，独立通道）替代，不要反复重试同一条 bash。
  - **读文件/搜索优先用工具**：read（分段）、grep、glob 工具不占 bash 通道，能避开 bash 卡死。bash 只用于真正需要 shell 的操作（git/测试/gate）。
  - **长命令分片 + 大 timeout**：全量 bats 分 unit/regression/integration 片跑，每片设大 timeout；gate/consistency 单跑。
  - **输出控制在几十行内**：避免大输出（grep -c 大文件、cat 长文件）——用 `grep -n` 精确匹配或 read 分段。
  - **先看全输出再分析**：不用 `tail` 截断关键输出（count-tests 教训：数字被 tail 吞掉导致误判）。
  - **commit 前检查 hook 会跑什么**：pre-commit 会按 .state.yaml phase 跑 check-gate。commit 时 phase 应与"本次产出所在阶段"一致（P1 产出 → phase=P1 再 commit，commit 后再推进），否则 hook 会因"下一阶段产出不存在"拦截（P2-design 未产出时 phase=P2 → GATE P2 未通过）。
  - **hook 机制在共享 git 目录**：worktree 的 `.git/hooks` 为空，hook 实际在共同 git 目录 `/home/kity/oclab/agate/.git/hooks/`（pre-commit/pre-push 软链已装；commit-msg 已补装）。改 hook 装那里。
- **核心上下文**：任务目标/范围/已踩坑见 `HANDOFF-V2.0.md`（worktree 根目录）；阶段产出在 `docs/tasks/T001-v2.0-structured/`。
- **编号规则将随 v2.0 改造**：流 D 会把编号改为 Jira 式 `TAG0001`（项目代号+动态数字），硬切不兼容旧 `T\d+`（见 P0-brief 流 D）。

## 版本发布

1. 确认 bats 全过 + 0 consistency ERROR + 0 shellcheck error（用例数以 `count-tests.sh` 为准）
2. 更新 `README.md` version badge
3. `git tag vN.N.0 && git push origin vN.N.0`
4. CHECK 7（version badge vs git tag）自动通过

**release PR 必须用普通 merge（`--no-ff`），禁止 squash merge**：`agate-summary.sh` 用 `git describe --tags --abbrev=0` 探测版本，要求 tag 是 HEAD 的祖先。tag 打在 feature 分支头时，普通 merge 会让该提交成为 main 的祖先（tag 保持有效），而 squash merge 会生成一个内容相同但 SHA 不同的新提交，导致 tag 与 main 分叉、`describe` 回退到旧版本（v0.31.0 事故）。若确实用了 squash，合并后必须把 tag 重新指到 squash 后的 main 提交：`git tag -f vN.N.0 <main-commit> && git push origin vN.N.0 --force`。
