# agate 开发指引

> 本文件面向**修改 agate 协议/脚本的开发者**。协议使用者看 `agate/AGENTS.md`。

## 仓库结构

```
agate/                  ← 协议本体（~/.agate 软链接指向这里）
  AGENTS.md             ← 协议本体入口（面向使用者/Agent）
  WORKFLOW.md           ← P0-P8 主流程
  dispatch-protocol.md  ← 派发协议 + gate 表
  state-machine.md      ← 状态转移/重试上限
  phase-cards/          ← 阶段卡片（渐进披露，主 Agent 按需加载）
  rules/                ← 跨阶段规则（review-mapping, state-transitions）
  scripts/              ← gate 检查脚本（bash + python3）
  tests/                ← bats 测试（以 count-tests.sh 输出为准）
  assets/               ← 角色/模板文件
SELF-GATE.md            ← agate 自身变更的 gate（改协议/脚本时必读）
docs/                   ← 项目开发资料（评审、计划、竞争分析）
.github/workflows/      ← CI（protocol-tests.yml：bats + shellcheck + consistency + gate-backstop）
```

**`agate/` 是协议本体，`docs/` 是开发资料。** 改协议改 `agate/`，改文档改 `docs/`。

## 依赖

- Bats ≥ 1.2.0（需要 `BATS_TEST_TMPDIR`）
- Python 3.8+ + `pyyaml`（`pip install pyyaml`）
- shellcheck

## 开发命令

```bash
# 跑全部测试（必须全过才能 commit）
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/

# 跑单个脚本的测试
bats agate/tests/unit/check-pruning.bats

# 一致性检查（0 ERROR 才行；--strict 让 WARNING 也阻断；--json 机器可读）
python3 agate/scripts/check-protocol-consistency.py

# shellcheck
shellcheck agate/scripts/*.sh

# 测试用例计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh
```

## 改脚本的工作流

1. **先加失败测试**，确认测试红
2. 改脚本，确认测试绿
3. 跑 `python3 agate/scripts/check-protocol-consistency.py` 确认无 ERROR
4. 发现新 bug → 先写 `regression/` 测试再修

## 脚本关键约定

- **所有 `git diff` 用 `--cached`**，不用 `HEAD~1`——pre-commit hook 运行时 commit 还没创建
- **`grep -c || echo 0` 后必须 `| tail -1`**——grep 无匹配时 exit 1，`|| echo 0` 产生双行 `0\n0`
- **`printf '%b' "$VAR"`**，不用 `printf '%s'`（不解释 `\n`）也不用 `printf "$VAR"`（SC2059）
- **Python 调用用 `os.environ`**，不用 `open('$VAR')`——shell 注入风险
- **所有脚本 `set -euo pipefail`**

## 测试约定

- 测试框架：Bats ≥ 1.2.0（需要 `BATS_TEST_TMPDIR`）
- 临时文件用 `$BATS_TEST_TMPDIR`，不用 `/tmp`
- `create_task_dir` 默认写入 `agent: test` frontmatter + Given 行
- mock pytest：`TEST_RUNNER` 环境变量指向 fake 脚本，无需真实 pytest
- fixture `.state.yaml` 以 `.` 开头，`git add` 需 `-f` 才能暂存
- helpers：`load.bash`（AGATE_ROOT 解析）→ `fixtures.bash`（create_task_dir 等）→ `git-helper.bash`（git_init / git_commit / git_stage）
- 每个 .bats 文件第一行 `load "tests/helpers/load.bash"`

## 改 agate 协议本体的检查清单

改协议文档或脚本时，遵循 **SELF-GATE.md**（agate 自身变更的 gate）。

触发 self-gate 的文件：`agate/scripts/*.sh`、`agate/scripts/check-protocol-consistency.py`、`agate/*.md`、`agate/**/*.md`、`SELF-GATE.md`。

commit 时 `commit-msg-self-gate.sh` hook 会检查：暂存区含触发文件时，commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由，否则 WARNING（不拦截）。

## CI

单一 workflow（`protocol-tests.yml`），push/PR 自动触发：
- **bats**：unit + regression + integration + sanity
- **shellcheck**：静态分析
- **consistency**：协议结构一致性检查
- **gate-backstop**：CI 兜底重跑 gate + ci-gate-backstop.py

## 版本发布

1. 确认 bats 全过 + 0 consistency ERROR + 0 shellcheck error（用例数以 `count-tests.sh` 为准）
2. 更新 `README.md` version badge
3. `git tag vN.N.0 && git push origin vN.N.0`
4. CHECK 7（version badge vs git tag）自动通过
