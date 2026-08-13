# agate 协议自检套件

> **这是给协议 maintainer 的测试套件**。普通用户用 agate 完成自己的任务时不需要管这里。

## 快速开始

```bash
# 安装依赖
sudo apt-get install bats shellcheck python3-yaml

# 跑全部测试
bats agate/tests/unit/         # 单元测试
bats agate/tests/regression/   # 回归测试
bats agate/tests/integration/  # 集成测试
bats agate/tests/sanity.bats   # 框架自检

# 一次性全跑
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

## 覆盖度

```bash
# 自动生成（从 .bats 文件 @test 数量统计）
bash agate/tests/scripts/count-tests.sh
```

| 脚本 | 测试文件 | 用例数 |
|------|---------|-------|
| check-pruning.sh | unit/check-pruning.bats | 29 |
| check-gate.sh | unit/check-gate.bats | 124 |
| agate-next-card.sh | unit/agate-next-card.bats | 20 |
| agate-render-dispatch-prompt.sh | unit/agate-render-dispatch-prompt.bats | 20 |
| check-p6-evidence.sh | unit/check-p6-evidence.bats | 28 |
| check-p6-format.sh | unit/check-p6-format.bats | 14 |
| check-p6-provenance.sh | unit/check-p6-provenance.bats | 38 |
| check-scope-resolved.sh | unit/check-scope-resolved.bats | 11 |
| check-frontmatter.sh | unit/check-frontmatter.bats | 10 |
| check-state-yaml.sh | unit/check-state-yaml.bats | 9 |
| check-state-transition.sh | unit/check-state-transition.bats | 26 |
| check-changelog.sh | unit/check-changelog.bats | 8 |
| check-retrospective.sh | unit/check-retrospective.bats | 11 |
| check-tdd-red.sh | unit/check-tdd-red.bats | 38 |
| formatters | unit/check-tdd-red-formatter.bats | 12 |
| ci-gate-backstop.py | unit/ci-gate-backstop.bats | 8 |
| agate-json-get.py | unit/agate-json-get.bats | 8 |
| agate-read-p5-commands.py | unit/agate-read-p5-commands.bats | 4 |
| agate-state-get.py | unit/agate-state-get.bats | 6 |
| agate-retreat-state.py | unit/agate-retreat-state.bats | 3 |
| agate-md-field-get.py | unit/agate-md-field-get.bats | 6 |
| agate-state-yaml-check.py | unit/agate-state-yaml-check.bats | 3 |
| agate-changelog-unreleased.py | unit/agate-changelog-unreleased.bats | 2 |
| agate-card-inject.py | unit/agate-card-inject.bats | 2 |
| agate-vision-blocker.py | unit/agate-vision-blocker.bats | 2 |
| agate-evidence-consistency.py | unit/agate-evidence-consistency.bats | 2 |
| agate-image-check.py | unit/agate-image-check.bats | 4 |
| agate-gate-missing-cmds.py | unit/agate-gate-missing-cmds.bats | 2 |
| agate-gate-p5-count.py | unit/agate-gate-p5-count.bats | 3 |
| install-hook.sh | unit/install-hook.bats | 5 |
| 回归 (R1-R5) | regression/ | 15 |
| pre-commit-hook | integration/pre-commit-hook.bats | 42 |
| pre-push-hook | integration/pre-push-hook.bats | 3 |
| 协议一致性 | integration/consistency.bats | 11 |
| self-gate | integration/protocol-alignment-review.bats | 8 |
| 框架自检 | sanity.bats | 6 |
| **总计** | | **以 `count-tests.sh` 输出为准** |

> 注：`count-tests.sh` 统计不含 sanity.bats 的 6 用例，加上框架自检 6 = 实际 bats 总数。以 `count-tests.sh` 输出为准。

## CI

GitHub Actions workflow 在 `.github/workflows/protocol-tests.yml`：
- `bats` job：单元 + 回归 + 集成 + 框架自检
- `shellcheck` job：静态分析
- `consistency` job：协议一致性检查

## 何时更新

- 改 gate 规则 → **必须先加失败测试，再改脚本**
- 发现新 bug → **修脚本前先写回归测试**（regression/）
- 协议文档声明新规则 → **必须新增对应 .bats 用例**
- 章节标题数字漂移 → 跑 `count-tests.sh` 同步
- 发现平台假设（`PATH="/usr/bin:/bin"`/裸 `python3`/`[[ -L ]]` 单平台断言/`/tmp`）→ **修测试为平台无关**（探测或按平台分支），并在 Linux 上用模拟环境覆盖 Windows 分支——测试套件目标是平台无关（原则见 AGENTS.md「测试约定」）

## 已知风险

| 编号 | 风险 | 兜底 | 状态 |
|------|------|------|------|
| R2.3 | ~~DESIGN_GAP 在 P4 但 architect 忘记转抄 P7 → 静默放过~~ | P4/P7 交叉核对 | 已关闭（v0.6 hardening R2.3） |
| R2.4 | `agate-archive-stale-outputs.bats` 的 `ARCH.4`（同一任务对 P6 归档两次）偶发因归档目录名用秒级时间戳（`agate-archive-stale-outputs.sh` 的 `TS=$(date +%Y%m%d-%H%M%S)`）而在快速连续执行/系统负载较高时撞名，导致该用例单独失败 | 隔离单跑必过（非逻辑错误，纯计时窗口问题）；全量重跑一次可确认是否为此 flaky，而非真实回归 | 已知不修复——功能正确性不受影响（仅影响测试稳定性），根治需把时间戳粒度提到毫秒级或加序号后缀，评估后判定当前收益不足以覆盖改动风险；v0.35 起即存在，非 v0.40.0 引入，v0.40.0（T001）改造过程中多次复现并确认，见 `docs/reviews/agate-alignment-review-final-2026-08-10.md` |

## 目录

```
agate/tests/
├── README.md               ← 你在这里
├── sanity.bats             ← 框架自检
├── scripts/
│   └── count-tests.sh      ← 从 .bats 文件自动统计 @test 数量
├── helpers/
│   ├── load.bash           ← 全局 setup（AGATE_ROOT 解析）
│   ├── fixtures.bash       ← create_task_dir / add_pruning_excuse 等
│   └── git-helper.bash     ← git_init / git_commit / git_stage
├── fixtures/               ← 静态夹具（Gold 任务）
│   ├── full-task/          ← 全阶段未裁剪 Gold
│   ├── ui-affected/        ← UI 任务 + vision YAML
│   ├── vision-blocked/     ← vision YAML blocker_count != 0
│   ├── high-risk/          ← risk_level=high
│   └── paused-task/        ← retries 超限
├── unit/                   ← 单元测试（按脚本分文件）
├── regression/             ← 回归测试（按 bug 分文件）
└── integration/            ← 集成测试
```
