# agate 开发指引

## 仓库结构

```
agate/              ← 协议本体（~/.agate 软链接指向这里）
  AGENTS.md         ← 协议本体入口（面向使用者）
  scripts/          ← gate 检查脚本（bash + python3）
  tests/            ← 161 个 bats 测试用例
  assets/           ← 角色/模板文件
docs/               ← 项目开发资料（评审、计划、竞争分析）
.github/workflows/  ← CI
```

**`agate/` 是协议本体，`docs/` 是开发资料。** 改协议改 `agate/`，改文档改 `docs/`。

## 开发命令

```bash
# 跑全部测试（必须全过才能 commit）
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/

# 跑单个脚本的测试
bats agate/tests/unit/check-pruning.bats

# 一致性检查（0 ERROR 才行）
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

## 改 agate 协议本体的检查清单

改协议文档或脚本时（`agate/scripts/*.sh`、`agate/scripts/check-protocol-consistency.py`、`agate/**/*.md`），除了常规测试，还需：

1. **跑 check-protocol-consistency.py** — 确认 CHECK 1-9 无 ERROR
2. **派发 protocol-alignment-review subagent** — 语义对齐审查（见 `dispatch-protocol.md`「agate 自身变更的对齐审查」+ `assets/review-roles/protocol-alignment-review.md`）
3. **读审查报告** — MISALIGNED 必须修复，NEEDS_HUMAN_REVIEW 需附 `[HUMAN_CONFIRMED: ...]` 标记
4. **跑全量 bats** — 确认无退化
5. **如果改了 gate 逻辑** — 确认下游项目（如 PeekView）的 gate 仍能跑通

## 版本发布

1. 确认 161 bats + 0 consistency ERROR + 0 shellcheck error
2. 更新 `README.md` version badge
3. `git tag vN.N.0 && git push origin vN.N.0`
4. CHECK 7（version badge vs git tag）自动通过
