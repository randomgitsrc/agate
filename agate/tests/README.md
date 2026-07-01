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
| check-pruning.sh | unit/check-pruning.bats | 20 |
| check-gate.sh | unit/check-gate.bats | 34 |
| check-p6-evidence.sh | unit/check-p6-evidence.bats | 11 |
| check-p6-provenance.sh | unit/check-p6-provenance.bats | 16 |
| check-scope-resolved.sh | unit/check-scope-resolved.bats | 6 |
| check-state-yaml.sh | unit/check-state-yaml.bats | 9 |
| check-state-transition.sh | unit/check-state-transition.bats | 8 |
| check-changelog.sh | unit/check-changelog.bats | 5 |
| check-retrospective.sh | unit/check-retrospective.bats | 4 |
| check-tdd-red.sh | unit/check-tdd-red.bats | 9 |
| 回归 (R1-R5) | regression/ | 15 |
| pre-commit-hook | integration/pre-commit-hook.bats | 5 |
| 协议一致性 | integration/consistency.bats | 10 |
| self-gate | integration/protocol-alignment-review.bats | 6 |
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

## 已知风险

| 编号 | 风险 | 兜底 | 状态 |
|------|------|------|------|
| R2.3 | ~~DESIGN_GAP 在 P4 但 architect 忘记转抄 P7 → 静默放过~~ | P4/P7 交叉核对 | 已关闭（v0.6 hardening R2.3） |

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
