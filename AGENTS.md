# agate 开发指引

> 本文件面向**修改 agate 协议/脚本的开发者**。协议使用者看 `agate/AGENTS.md`。

## 这是什么

**agate** 是一套面向软件工程任务的纯文档 AI Agent 编排协议——没有运行时服务、没有编译产物、没有 package.json，"产品"就是一组 Markdown 协议文件 + bash/Python gate 检查脚本，由 Claude Code / OpenCode 的编排 Agent 读取并执行。核心思路：主 Agent（orchestrator）自己不写代码，而是通过 P0-P8 阶段（需求→设计→TDD→实现→验证→验收→一致性→发布）派发专职 subagent，每阶段结束后跑一次客观 gate 检查（exit code 判定），通过才允许状态机推进。完整卖点见 `README.md`，这条路线的已知结构性局限见 `agate/LIMITATIONS.md`（依赖前建议先读，不要误以为协议解决了所有质量问题）。

## 仓库结构

```
<仓库根>/                  # 开发资料：README、CHANGELOG、docs/（设计笔记、评审、路线图）、archived/
└── agate/                 # 协议本体 —— ~/.agate 软链接指向这里，是使用者/Agent 实际消费的东西
    ├── WORKFLOW.md              # P0-P8 阶段定义、裁剪规则 —— 主入口
    ├── dispatch-protocol.md     # 派发模板、gate 表、空返回恢复
    ├── state-machine.md         # 阶段转移规则、重试上限、PAUSED 恢复
    ├── role-system.md           # 双层角色体系（执行角色 vs 评审角色）
    ├── git-integration.md       # commit 规范
    ├── platform-notes.md        # OpenCode / Claude Code 等平台能力差异
    ├── LIMITATIONS.md           # 已知结构性局限
    ├── orchestrator-template.md # 主 Agent 提示词，符号链接接入（不拷贝），见 agate/SETUP.md
    ├── phase-cards/P{0-8}-*.md  # 渐进披露的阶段卡片（orchestrator 每轮只读一张）
    ├── assets/
    │   ├── execution-roles/     # analyst / architect / test-designer / implementer / verifier / vision-analyst / consistency-reviewer
    │   ├── review-roles/        # review / design-review / cso / qa / investigate / protocol-alignment-review / requirements-review / plan-*-review
    │   └── templates/           # active-tasks、dispatch-prompt、dispatch-context、task-files 等模板
    ├── scripts/                 # gate 逻辑：check-*.sh 是 pre-commit/pre-push 入口，.py 是 .sh 薄壳调用的实现
    └── tests/                   # pytest 套件（unit/regression/integration/sanity），见 agate/tests/README.md
```

## 编排模型

主 Agent（orchestrator）职责严格限定为四件事：读状态、派发 subagent、跑 gate 脚本、更新状态（`.state.yaml` + `{AGATE_WORKSPACE}/tasks/active-tasks.md`）。它永远不亲自写阶段产出物。每个阶段（P1 需求 → P2 设计 → P3 TDD → P4 实现 → P5 验证 → P6 验收 → P7 一致性 → P8 发布）由 `assets/execution-roles/` 下的专职 subagent 角色执行，且在状态机推进前必须过 gate：

- **外部产出 gate**（P3-P5）：判定对象是外部工具输出（test runner exit code、类型检查器、git log）——可信度高，主 Agent 无法伪造。
- **自写文件 gate**（P1、P2、P6、P7）：判定对象是主 Agent/subagent 自己写的文件——可信度较低，靠证据存在性检查、provenance/行为审计、BDD 计数对照缓解（非硬保证，见 `agate/LIMITATIONS.md` 局限 3）。

风险分级裁剪：任务的 `risk_level`（P1 阶段设定）决定哪些阶段是强制的——裁剪表见 `README.md` / `agate/WORKFLOW.md`。

## Gate 脚本分层

`scripts/*.sh` 是被 git hook（`pre-commit-gate.sh`、`pre-push-gate.sh`、`commit-msg-self-gate.sh`，经 `install-hook.sh` 以软链方式安装，升级自动生效）调用的薄壳；逻辑较重的检查抽离成独立的 `agate-*.py` 工具供 `.sh` 调用。`gate-result.sh` 是被 source 的函数库（`write_gate_result`、`read_state_phase`、`read_state_task_id` 等），从不直接执行。`check-gate.sh` 是主 Agent 每阶段调用的总闸检查。

## 依赖

- pytest（需要 `pytest` ≥ 7；Bats 已退役，2026-08 TAG0011）
- Python 3.8+ + `pyyaml` + `Pillow`（`pip install pyyaml Pillow`，Pillow 可选）— 检查逻辑抽离为独立 `.py` 工具（`agate/scripts/agate-*.py`），由 `.sh` 薄壳调用。其中 state/vision 类工具（agate-state-get / agate-retreat-state / agate-state-yaml-check / agate-vision-blocker）依赖 pyyaml；agate-image-check 依赖 Pillow（可选，用于像素方差/average hash 检测）
- shellcheck
- ruff（Python 化后替代 shellcheck 对 py 的检查——TAG0010 起生效；运行 agate 不需要，开发 agate 需要）

## 开发环境（建议做法，非硬性要求）

> 运行 agate 只需系统 python3 + pyyaml（见上方「依赖」）。本节讲**开发 agate 本体**（改协议/脚本）时的环境建议。

- **开发 agate 建议用专用虚拟环境**（`python3 -m venv` 或 uv/conda），装 pyyaml + ruff（Python 化后替代 shellcheck 对 py 的检查）。
- 依赖极简（pyyaml + ruff），任何隔离方式都行——不强制特定工具或路径。
- **运行 agate 不需要这个环境**——它只服务"开发 agate 本体"。
- worktree 开发时（同一仓库多 checkout），各 checkout 共用同一开发环境即可（代码一致，环境也该一致）。

## 开发命令

```bash
# 跑全部测试（必须全过才能 commit）
python3 -m pytest agate/tests/

# 跑单个脚本的测试
python3 -m pytest agate/tests/unit/test_check_pruning.py

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

- **测试平台无关原则（agate 测试的核心约束）**：测试**不得硬编码单平台假设**——不允许裸 `PATH="/usr/bin:/bin"`、不允许裸 `python3`（应探测 `python3|python`）、不允许假设 POSIX symlink 语义（Windows Git Bash 的 `ln -sf` 退化为复制，`[[ -L ]]` 判定不同）、不允许假设 `/tmp` 等 Unix-only 路径。平台差异场景**按平台分支断言**（Linux 断言软链，Windows 断言"复制模式 + WARNING"），或在 Linux 上用模拟环境（`PYTHONIOENCODING`/`ln` mock/PATH 探测）覆盖分支。**目标：测试套件平台无关，Linux 全量覆盖，Windows CI 只跑技术路线冒烟**（`@pytest.mark.windows_smoke` marker 标注每文件第 1 个用例 + 名称含平台敏感关键词的用例作代表——Windows 验证"平台敏感机制在 Windows 成立"，功能正确性由 Linux 全量保证）。违反此原则（新引入 Unix 假设）是测试缺陷，应在 review 拦截（TAG0009 起由静态扫描器 gate 兜底）
- 测试框架：pytest ≥ 7（Bats 已退役，TAG0011）
- 临时文件用 pytest `tmp_path` fixture，不用 `/tmp`
- `create_task_dir` 默认写入 `agent: test` frontmatter + Given 行；`--no-state-yaml` 跳过 .state.yaml
- mock pytest：`TEST_RUNNER` 环境变量指向 fake 脚本，无需真实 pytest
- fixture `.state.yaml` 以 `.` 开头，`git add` 需 `-f` 才能暂存
- helpers：`agate/tests/conftest.py`（`agate_root` 解析 + `task_dir` / `git_repo` / `run_cli` / `py_path` 等 fixture）
- 每个 test_*.py 文件无需 load 语句——根 `conftest.py` 自动加载 fixture
- **CI 里 `~/.agate` 软链接不存在**——conftest 通过 `_resolve_agate_root` 从 tests/ 上溯反推 `AGATE_ROOT`，本地也可设 `AGATE_ROOT` 环境变量覆盖

## 改 agate 协议本体的检查清单

改协议文档或脚本时，遵循 **SELF-GATE.md**（agate 自身变更的 gate）。

触发 self-gate 的文件：`agate/scripts/*.sh`、`agate/scripts/check-protocol-consistency.py`、`agate/*.md`、`agate/**/*.md`、`SELF-GATE.md`。

commit 时 `commit-msg-self-gate.sh` hook 会检查：暂存区含触发文件时，commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由，否则 WARNING（不拦截）。

## CI

单一 workflow（`protocol-tests.yml`），push/PR 自动触发：
- **pytest**：`python3 -m pytest agate/tests/`（Linux 全量 + Windows `-m windows_smoke` 冒烟）
- **shellcheck**：`shellcheck -S warning agate/scripts/*.sh`
- **consistency**：`python3 agate/scripts/check-protocol-consistency.py`
- **gate-backstop**：`python3 agate/scripts/ci-gate-backstop.py`（push 后重跑 gate + P6 git blame 单 author WARNING）

## dogfooding 工作流（agate 自身改造任务通用约定）

> 本节是**触发块**：任何 agate 自身改造任务（TAG0004+）需要隔离 worktree 时，**必须先读**：
> - 构建流程：`docs/guides/worktree-dogfooding-guide.md`（10 步标准流程）
> - 交接单模板：`agate/assets/templates/handoff-template.md`（复制到 worktree 根 `HANDOFF-{Txxx}.md` 填写）

- **双工作区**（改造对象 = worktree `agate/`；开发工具 = `~/.agate` 稳定版，**勿动**）：跑 gate/读卡片用 `~/.agate`，改代码/跑测试在 worktree。主 checkout（`/home/kity/oclab/agate`）是协议本体，禁止改动。
- **gate 工具 ≠ 检查对象**：commit hook 用 `~/.agate`（稳定版）判定；但 `check-protocol-consistency.py` 必须用 worktree 自己的（检查 worktree 里的协议文件）。
- **工具稳定优先**：hook 指向 `~/.agate` 稳定版，不指向 worktree（避免"用未验证的新 gate 判自己"）。
- **~/.agate 脚本在 worktree 跑显示主 checkout 上下文**：`agate-summary.sh` 显示稳定版 main/HEAD，不代表 worktree 状态。
- **工具纪律（T001/TAG0004 多次实战验证）**：
  - **bash 命令一律加 `timeout`**（外层 `timeout N cmd`，N 按命令预期耗时给 30-90s），工具 timeout 参数同步设。无 timeout 的 bash 在本环境多次被 abort/挂起。
  - **单步串行，不并行 bash**：一次只发一个 bash 调用；必须链多步时用 `&&` 且每步短。并行 bash 是 abort 高危。
  - **卡住就换路，不重试同一 bash**：bash 偶发长时间无响应。卡住后改用 read/grep/glob **工具**（它们不走 bash，独立通道）替代，不要反复重试同一条 bash。
  - **读文件/搜索优先用工具**：read（分段）、grep、glob 工具不占 bash 通道，能避开 bash 卡死。bash 只用于真正需要 shell 的操作（git/测试/gate）。
  - **长命令分片 + 大 timeout**：全量 pytest 分 unit/regression/integration 片跑，每片设大 timeout；gate/consistency 单跑。
  - **输出控制在几十行内**：避免大输出（grep -c 大文件、cat 长文件）——用 `grep -n` 精确匹配或 read 分段。
  - **先看全输出再分析**：不用 `tail` 截断关键输出（count-tests 教训：数字被 tail 吞掉导致误判）。
  - **commit 前检查 hook 会跑什么**：pre-commit 会按 .state.yaml phase 跑 check-gate。commit 时 phase 应与"本次产出所在阶段"一致（P1 产出 → phase=P1 再 commit，commit 后再推进），否则 hook 会因"下一阶段产出不存在"拦截（P2-design 未产出时 phase=P2 → GATE P2 未通过）。
  - **hook 机制在共享 git 目录**：worktree 的 `.git/hooks` 为空，hook 实际在共同 git 目录 `/home/kity/oclab/agate/.git/hooks/`（pre-commit/pre-push 软链已装；commit-msg 已补装）。改 hook 装那里。

## 版本发布

1. 确认 pytest 全过 + 0 consistency ERROR + 0 shellcheck error（用例数以 `count-tests.sh` 为准）
2. 更新 `README.md` version badge + `CHANGELOG.md` [Unreleased] → 新版本号
3. **更新 `agate/UPGRADING.md` 新增本版本章节**（破坏性变更逐条列——v0.44.0 教训：漏更新；无自动检查，靠本清单 + P8 卡「主 Agent 必须亲自执行」兜底）
4. `git tag vN.N.0 && git push origin vN.N.0`
5. CHECK 7（version badge vs git tag）自动通过

> 版本引用文件清单（agate 仓库自身特有，通用 P8 卡不覆盖）：README badge / CHANGELOG / version 文件 / UPGRADING 章节 / 稳定版引用（文档优先写"稳定版"不写死版本号）。**通用项目的版本清单**（version 文件 + CHANGELOG + 测试重跑 + git log 对照）见 `agate/phase-cards/P8-release.md`「主 Agent 必须亲自执行」。

**release PR 必须用普通 merge（`--no-ff`），禁止 squash merge**：`agate-summary.sh` 用 `git describe --tags --abbrev=0` 探测版本，要求 tag 是 HEAD 的祖先。tag 打在 feature 分支头时，普通 merge 会让该提交成为 main 的祖先（tag 保持有效），而 squash merge 会生成一个内容相同但 SHA 不同的新提交，导致 tag 与 main 分叉、`describe` 回退到旧版本（v0.31.0 事故）。若确实用了 squash，合并后必须把 tag 重新指到 squash 后的 main 提交：`git tag -f vN.N.0 <main-commit> && git push origin vN.N.0 --force`。
