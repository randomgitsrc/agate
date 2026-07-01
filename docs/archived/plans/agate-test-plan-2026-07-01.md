# agate 协议测试计划（v3.1 — 实施完成）

> 日期：2026-07-01
> 范围：agate/scripts/ 全部 15 个 shell 脚本 + 协议一致性
> 目标：把"靠维护者跑命令"改成"机器自动跑"，覆盖率从当前 7/31 手工测过 → 148 个 .bats 用例自动验证（+ 6 sanity = 154）
> 状态：**已完成** — 154/154 全过，CI workflow 已落地

---

## 零、测试位置：放在 `agate/tests/`（决策说明）

**结论**：测试放在 `agate/tests/`（协议本体目录内），不放仓库根或单独仓库。

### 为什么

agate 协议本体由四类组成：
- **协议文档**：`WORKFLOW.md` / `state-machine.md` / `dispatch-protocol.md` 等（告诉 Agent 怎么用）
- **执行脚本**：`scripts/`（机器跑的 gate）
- **角色模板**：`assets/`（用户拷贝的）
- **入口文件**：`AGENTS.md` / `orchestrator-template.md`（文档索引）

**测试是"执行脚本"的伴生物**——和 `scripts/` 同生死。放 `agate/tests/` 的硬理由：

1. **发布时一起带出**：通过软链接 `~/.agate → ~/oclab/agate/agate/` 装的不是"半个 agate"——没有测试的 agate 是没有自检能力的协议。
2. **pre-commit hook 路径自洽**：现有 `pre-commit-gate.sh` 用 `$AGATE_ROOT/scripts/...`，测试天然用 `$AGATE_ROOT/tests/...`，无需在文档里教"先装本体再装测试"。
3. **改完脚本能本地验证**：maintainer 改 `check-pruning.sh` 后直接 `bats agate/tests/unit/check-pruning.bats`，不需要切换工作目录到另一个仓库。
4. **CI 不变**：`.github/workflows/` 路径写 `agate/tests/` 即可，无需跨仓库。

### 怎么避免"用户误以为这是给我的"

`agate/tests/` 有清晰的语义边界：
- `scripts/` 是用户用得上的（被 hook 调用）
- `assets/` 是用户需要拷贝的
- **`tests/` 是给协议 maintainer 的（用户不必读）**

在 `AGENTS.md` 加一行：

```markdown
| 我要做什么 | 看这里 |
|------|------|
| 改 agate 协议本体并跑测试 | `tests/README.md`（maintainer 入口） |
```

`tests/README.md` 写明：这是协议自检套件，普通用户用 agate 完成自己的任务时不需要管它。

### 拒绝的替代方案

| 方案 | 否决理由 |
|------|---------|
| `~/oclab/agate/tests/`（仓库根） | 协议仓库根是项目开发资料（`docs/reviews/`、`docs/plans/` 等），放测试混淆"项目"和"协议"两个层级 |
| `agate-test/` 单独仓库 | 双仓库分发：用户装 agate 还要装 agate-test。改脚本→测测试 跨仓库 PR，体验差 |
| 嵌入式（每个脚本旁 `check-pruning.test.sh`） | agate/scripts/ 已经有 15 个文件，再加 15 个测试文件会让目录变 30 文件难导航 |

---

## 一、目标与背景

### 当前状态

| 维度 | 现状 |
|------|------|
| 测试框架 | 无（手工跑 /tmp 临时夹具） |
| 测试夹具 | 0 个持久化（每次用完即弃） |
| 脚本分支覆盖 | 7/31 = 22.6%（v0.6 实施评审手工覆盖的部分） |
| 自动化触发 | 无（本地 + CI 都不跑测试） |
| 已知 bug 回归保护 | 无（YAML 缩进 bug 直接落到 main） |
| 一致性检查 | `check-protocol-consistency.py` 已在 CI 跑，但未覆盖脚本行为 |

### 目标

- **覆盖率**：每个 `exit 1/2/0` 分支至少 1 个测试用例（happy path + 边界 + 错误）
- **持久化**：所有夹具进 git 仓库，下次改脚本能自动识别回归
- **双线触发**：本地 pre-commit + GitHub Actions 都跑
- **回归套件**：每个 T 编号 bug + v0.6 评审发现的隐性风险，转化为回归测试
- **文档一致**：`state-machine.md` / `dispatch-protocol.md` 中声明的每条 gate 规则，都对应到 `tests/` 中的一个测试

### 非目标（明确不做）

- **不**测 LLM 行为（agent 是否真的写对 P3 test）—— 这是 TDD 检查脚本的责任边界，不是协议行为
- **不**测文档美学（措辞是否清晰）—— 由人评审
- **不**测 CI 配置本身的语法（YAML lint 是另外的事）
- **不**做性能/压力测试（协议是文档，不存在性能问题）

---

## 二、测试框架选型

### 候选对比

| 框架 | 优势 | 劣势 | 结论 |
|------|------|------|------|
| **Bats** | bash 生态标准，apt 装，TAP 输出，可读断言 | 边界 case 需手写 `setup/teardown` | ✅ **推荐** |
| shunit2 | 老牌，更像 xUnit | 配置复杂，断言需 `assertEquals` 等函数 | 备选 |
| shellcheck | 静态分析，能查 syntax + 常见 bug | 不能测运行时行为 | 单独跑，不替代 |
| bash_unit | 极简 | 文档少，社区小 | 不选 |

### 选 Bats 的理由

1. **语义匹配**：agate 脚本都是 bash，Bats 天然匹配
2. **零配置**：单个 `.bats` 文件可读可跑
3. **CI 友好**：输出 TAP，GitHub Actions 用 `bats-core` action 直接读
4. **维护负担低**：每个测试一个 `setup` + `@test` 块，10 行能写一个 case

### 辅助工具

| 工具 | 用途 |
|------|------|
| `shellcheck` | 静态分析（独立 CI 任务） |
| `bats-assert` / `bats-support` | 增强断言（可选） |
| `git` | 真实 repo 测试（`git diff --cached` 类脚本需要） |

---

## 三、测试架构

### 目录结构

```
agate/
├── scripts/                         # 现有：被测脚本
│   ├── check-pruning.sh
│   ├── check-gate.sh
│   ├── ...
├── tests/                           # 新增：测试套件
│   ├── helpers/
│   │   ├── fixtures.bash            # 共享夹具构建函数
│   │   ├── git-helper.bash          # 临时 git repo 初始化
│   │   └── load.bash                # bats load 入口
│   ├── fixtures/                    # 静态夹具（复杂场景）
│   │   ├── full-task/               # 全阶段未裁剪的 Gold 任务目录
│   │   │   ├── .state.yaml
│   │   │   ├── P0-brief.md
│   │   │   ├── P1-requirements.md
│   │   │   ├── P2-design.md
│   │   │   ├── P3-test-design.md
│   │   │   ├── P4-implementation.md
│   │   │   ├── P5-verification.md
│   │   │   ├── P6-acceptance.md
│   │   │   ├── P6-evidence/
│   │   │   ├── P7-consistency.md
│   │   │   └── P8-release.md
│   │   ├── ui-affected/             # ui_affected=true 任务
│   │   └── vision-blocked/          # vision YAML 有 blocker 的任务
│   ├── unit/                        # 单元测试：单脚本
│   │   ├── check-pruning.bats
│   │   ├── check-gate.bats
│   │   ├── check-p6-evidence.bats
│   │   ├── check-p6-provenance.bats
│   │   ├── check-scope-resolved.bats
│   │   ├── check-state-yaml.bats
│   │   ├── check-state-transition.bats
│   │   ├── check-changelog.bats
│   │   ├── check-retrospective.bats
│   │   └── check-tdd-red.bats
│   ├── regression/                  # 回归测试：每个 bug 一组
│   │   ├── v060-yaml-indent.bats    # task-files.md executor_env 缩进
│   │   ├── v060-design-gap.bats     # DESIGN_GAP 配对
│   │   ├── v060-r4-cached.bats      # T045 hardening 裁剪 P7 文件数 (--cached)
│   │   ├── v060-p8-cached.bats      # P8 gate 用 --cached（评审新发现+已修）
│   │   └── ...
│   ├── integration/                 # 集成测试
│   │   ├── pre-commit-hook.bats     # 完整 pre-commit 流程
│   │   └── lifecycle.bats           # P0→DONE 端到端
│   └── README.md                    # 跑测试的方法
```

### 测试命名规范

- 文件：`<被测脚本名（去 .sh）>.bats` 或 `<bug-编号>.bats`
- 测试用例：`@test "<脚本> <场景> 期望 <结果>"`
  - 例：`@test "check-pruning.sh 裁剪 P2 无例外口 期望 exit 1"`

---

## 四、夹具设计

### 4.0 全局 setup（`tests/helpers/load.bash`）

**所有 `.bats` 文件第一行 load 此文件**：

```bash
# tests/helpers/load.bash
# BATS 全局 setup：导出 AGATE_ROOT + load fixtures 库
# 用法：每个 .bats 文件第一行 load helpers/load.bash

# AGATE_ROOT 解析规则（评审发现：CI 直接 checkout 时 ~/.agate 软链接不存在）
# 1. 显式设过 → 用
# 2. 否则 → 用 BATS_TEST_DIRNAME 反推（tests/ 的父目录 = agate/）
export AGATE_ROOT="${AGATE_ROOT:-$(cd "$BATS_TEST_DIRNAME/.." && pwd)}"

# 验证 AGATE_ROOT 下有 scripts/，防止路径错位
[ -d "$AGATE_ROOT/scripts" ] || {
    echo "FATAL: AGATE_ROOT=$AGATE_ROOT 下找不到 scripts/" >&2
    echo "  BATS_TEST_DIRNAME=$BATS_TEST_DIRNAME" >&2
    return 1
}

# 加载 fixtures 库
load "$BATS_TEST_DIRNAME/helpers/fixtures.bash"
load "$BATS_TEST_DIRNAME/helpers/git-helper.bash"
```

**为什么必须**：
- CI 直接 checkout agate 仓库后 `bats agate/tests/`，`~/.agate` 软链接不存在
- 没有这个文件，所有 `bash "$AGATE_ROOT/scripts/check-pruning.sh"` 会找不到脚本
- 评审发现这条假设完全没在计划中明示

### 4.1 共享夹具（`tests/helpers/fixtures.bash`）

提供函数，按需构造任务目录：

```bash
# 用法：create_task_dir <basename> [phases...] [extras...]
# phases 默认 P0-P8 全开
# 返回：临时目录路径
create_task_dir() {
    local base="$1"
    shift
    local phases="${@:-P0 P1 P2 P3 P4 P5 P6 P7 P8}"
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/task-XXXXXX")
    # ... 写 .state.yaml, P0-brief.md, P1-requirements.md ...
    echo "$dir"
}

# 用法：add_pruning_excuse <task_dir> <phase> <reason> <risk>
# 声明裁剪某阶段 + 写裁剪理由 + 跳过风险
add_pruning_excuse() { ... }

# 用法：add_evidence_file <task_dir> <rel_path> <content> [size]
# 在 P6-evidence/ 放文件，可指定大小（用于空 png 测试）
add_evidence_file() { ... }

# 用法：git_init <dir> [initial_files...]
# 在临时目录初始化 git repo，提交指定文件（pre-commit 测试需要）
git_init() { ... }

# 用法：git_stage <dir> <file>
# git add 指定文件
git_stage() { ... }
```

### 4.2 静态夹具（`tests/fixtures/`）

复杂场景用预制目录，避免每次测试都重新生成：

| 夹具 | 用途 | 关键文件 |
|------|------|---------|
| `full-task/` | 完整任务目录的"金标准" | 8 个 P* 文件 + 完整证据 |
| `ui-affected/` | UI 任务，有截图+vision YAML | P2 含 `ui_affected: true` |
| `vision-blocked/` | vision YAML 报告 blocker | `summary.blocker_count: 1` |
| `high-risk/` | risk_level=high + 复杂 BDD | P1 含多个 `Given` |
| `paused-task/` | retries 超限状态 | `.state.yaml: phase: PAUSED` |

### 4.3 临时夹具（测试函数内 inline 写）

简单场景直接在 `@test` 块内写：

```bash
@test "check-pruning.sh 缺 risk_level 期望 exit 1" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/task-XXXXXX")
    cat > "$dir/P1-requirements.md" <<EOF
phases: [P0, P1, P2, P3, P4, P5, P6, P7, P8]
task: test
EOF
    run bash "$AGATE_ROOT/scripts/check-pruning.sh" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"缺 risk_level"* ]]
}
```

---

## 五、逐脚本测试用例设计

### 5.1 `check-pruning.sh`（19 个用例）

| # | 测试名 | 夹具 | 预期 |
|---|--------|------|------|
| P2.1 | 缺 risk_level 字段 | P1 无 `risk_level:` | exit 1 |
| P2.2 | 裁剪 P2 无例外口 | phases=[P0,P1,P3..P8]，无例外字段 | exit 1，错误含"不可裁剪" |
| P2.3a | 裁剪 P2 + `legacy_p2_pruned: true` | 同上+字段 | exit 0 |
| P2.3b | 裁剪 P2 + `design_trivial: true` | 同上+字段 | exit 0 |
| P2.3c | 裁剪 P2 + `follows_existing_pattern: [src/foo.py]` | 同上+字段 | exit 0 |
| P2.3d | 裁剪 P2 + `follows_existing_pattern: []` | 空参照 | exit 1（正则边界） |
| P2.4 | 裁剪 P6 无 no_behavior_change | phases 无 P6 | exit 1 |
| P2.4a | 裁剪 P6 + no_behavior_change:true | 同上+字段 | exit 0 |
| P2.5 | 高风险裁剪 P3 | risk_level=high，phases 无 P3 | exit 1 |
| P2.6a | 裁剪 P7，源文件数 > 5 | git 暂存 6 个 .py | exit 1 |
| P2.6b | 裁剪 P7，源文件数 ≤ 5 | git 暂存 3 个 .py | exit 0 |
| P2.6c | 裁剪 P7 + implicit_coupling: [...] | P1 含此字段 | exit 1 |
| P2.7 | 裁剪 P8 无 internal_only | phases 无 P8 | exit 1 |
| P2.7a | 裁剪 P8 + internal_only:true | 同上+字段 | exit 0 |
| P2.8 | 裁剪理由缺"跳过风险" | phases 无 P7，无 `跳过风险:` | exit 1 |
| P2.9 | 裁剪声明 vs 执行不一致 | phases 无 P3 + P3-*.md 存在 + 无 override | exit 1 |
| P2.9a | 裁剪声明 vs 执行不一致 + override | 同上+`override: 手动跳过` | exit 0 |
| P2.10 | 无 P1 文件 | 空目录 | exit 2 |
| P2.11 | risk_level=low + 全 P 阶段 | 全合规 | exit 0（happy path） |

### 5.2 `check-gate.sh`（33 个用例）

| # | 测试名 | 夹具 | 预期 |
|---|--------|------|------|
| G1 | P1 gate 必 exit 2 | 任何 TASK_DIR | exit 2（主 Agent 判定） |
| G2.1 | P2，0 个候选方案 | P2-design.md 无 `### 候选方案` | exit 1 |
| G2.2 | P2，1 个候选方案 | P2-design.md 1 个 heading | exit 1 |
| G2.3 | P2，2 个候选方案 | P2-design.md 2 个 heading | exit 2 |
| G2.4 | P2，2 个候选 + 深层级 h4 | `#### 候选方案` | exit 1（regex 不匹配 h4） |
| G2.5 | P2，无 P2 文件 | 空目录 | exit 2（design_trivial） |
| G3.1 | P3，调用 check-tdd-red.sh 全绿 | mock 脚本输出 `5 passed` | exit 2（实现先于测试） |
| G3.2 | P3，check-tdd-red.sh 经典红灯（assertion failure） | mock 输出 `2 failed` | exit 0 |
| G3.3 | P3，check-tdd-red.sh B 类（项目内 import 失败） | mock 错误含 `from myapp` | exit 0 |
| G3.4 | P3，check-tdd-red.sh A 类（第三方 import 失败） | mock 错误含 `import requests` | exit 1 |
| G3.5 | P3，check-tdd-red.sh A 类（SyntaxError） | mock 含 `SyntaxError` | exit 1 |
| G3.6 | P3，check-tdd-red.sh 无测试运行器 | unset TEST_RUNNER，PATH 空 | exit 3 |
| G3.7 | P3，check-tdd-red.sh 混合（1 failed + 1 B 类 error） | mock 混合输出 | exit 0 |
| G4.1 | P4，无代码文件 | 暂存区仅 .md | exit 1 |
| G4.2 | P4，有 .py 代码 | 暂存区有 src/app.py | exit 0 |
| G4.3 | P4，.md + .yaml + .py 都行 | 混合 | exit 0 |
| G5 | P5 gate 必 exit 2 | 任何 TASK_DIR | exit 2 |
| G6.1 | P6，有 FAIL 行 | P6-acceptance.md `- FAIL xxx` | exit 1 |
| G6.2 | P6，有 NEED_CONFIRM 行 | 任意 `- NEED_CONFIRM` | exit 1 |
| G6.3 | P6，全 PASS 但证据目录空 | 全 PASS + P6-evidence/ 不存在 | exit 1 |
| G6.4 | P6，全 PASS + 证据目录有文件 | 全 PASS + P6-evidence/screenshot.png | exit 2 |
| G6.5 | P6，无 P6 文件 | 空目录 | exit 2 |
| G7.1 | P7，有 [BLOCKER] | `- [BLOCKER] xxx` | exit 1 |
| G7.2 | P7，有 [DEVIATION-CRITICAL] | `- [DEVIATION-CRITICAL] xxx` | exit 1 |
| G7.3 | P7，DESIGN_GAP 未配对 | `[DESIGN_GAP:x]` 无 REVIEWED | exit 1 |
| G7.4 | P7，DESIGN_GAP 已配对 | 1 GAP + 1 REVIEWED | exit 0 |
| G7.5 | P7，2 GAP + 1 REVIEWED | 不全配对 | exit 1 |
| G7.6 | P7，无任何标记 | 空文件 | exit 0 |
| G8.1 | P8，缺 bump_type | P8-release.md 无 `bump_type:` | exit 1 |
| G8.2 | P8，bump_type 存在但 version 文件无变更 | git HEAD~1 无变更 | exit 1 |
| G8.3 | P8，bump_type + version 变更，但 CHANGELOG 无变更 | git HEAD~1 无 CHANGELOG | exit 1 |
| G8.4 | P8，全合规 | 全满足 | exit 2 |
| G8.5 | P8，无 P8 文件 | 空目录 | exit 2 |

### 5.3 `check-p6-evidence.sh`（11 个用例）

| # | 测试名 | 夹具 | 预期 |
|---|--------|------|------|
| E.1 | P6 文件不存在 | 空目录 | exit 2 |
| E.2 | P6 无 BDD 条目 | 无 `- PASS/- FAIL` | exit 1 |
| E.3 | PASS 缺文件引用 | `- PASS xxx` 无括号 | exit 1 |
| E.4 | PASS 有文件引用但文件不存在 | `(missing.png)` | exit 1 |
| E.5 | 证据目录不存在 | 全 PASS + 引用 + 无 P6-evidence/ | exit 1 |
| E.6 | 证据目录为空 | 全 PASS + P6-evidence/.gitkeep | exit 1 |
| E.7 | 正常通过（无 UI） | 全 PASS + 文件存在 | exit 0 |
| E.8 | UI 任务，截图目录空 | ui_affected=true + (screenshots/) 引用 + 无 screenshots/ | exit 1 |
| E.9 | UI 任务，截图 ≤ 1KB | ui_affected=true + 100 字节 png | exit 1 |
| E.10 | UI 任务，正常通过 | ui_affected=true + 截图 + ≥ 1KB | exit 0 |
| E.11 | 多种文件后缀 | `.log` `.json` `.html` `.txt` `.yaml` | exit 0（不限 png） |

### 5.4 `check-p6-provenance.sh`（15 个用例）

| # | 测试名 | 夹具 | 预期 |
|---|--------|------|------|
| PV.1 | 无 P6 文件 | 空目录 | exit 0（不阻塞非 P6） |
| PV.2 | PASS 引用不存在的文件 | `(ghost.png)` | exit 1 |
| PV.3 | (vision:) 引用被误判为文件 | `(vision: y.yaml) (real.png)` 都有 | exit 0（vision 剥离） |
| PV.4 | 行末 (xxx) 多个括号 | `(a.png) (b.png)` 在同一行 | exit 0（取最后一个） |
| PV.5 | PASS 数 > 证据文件数 | 3 PASS + 1 文件 | exit 1 |
| PV.6 | 证据文件未被任何 PASS 引用 | 1 PASS + 2 文件 | exit 1 |
| PV.7 | .gitkeep 算入证据 | .gitkeep + 引用 .gitkeep | exit 1（hidden file 不计入证据数，触发"无证据"硬拦） |
| PV.8 | dispatch-context 含 PASS 预判 | P6-dispatch-context.md `- PASS` | exit 1 |
| PV.9 | P1 BDD Given 数 > P6 总数 | 3 Given + 1 PASS | exit 1 |
| PV.10 | P1 无 Given 格式 | P1 无 BDD | exit 2（WARNING） |
| PV.11 | UI 任务，截图 PASS 缺 vision 引用 | ui_affected=true + `(screenshots/x.png)` | exit 1 |
| PV.12 | vision YAML 文件不存在 | `(vision: missing.yaml)` | exit 1 |
| PV.13 | vision YAML blocker_count != 0 | summary.blocker_count: 1 | exit 1 |
| PV.14 | P6 缺 agent 字段 | 无 frontmatter agent | exit 2（WARNING） |
| PV.15 | risk=high + P2-review agent=main | self-review | exit 2（WARNING） |

### 5.5 `check-scope-resolved.sh`（6 个用例）

| # | 测试名 | 夹具 | 预期 |
|---|--------|------|------|
| SC.1 | 无 task 目录 | 路径不存在 | exit 2 |
| SC.2 | 无 SCOPE+ 触发 | 任何 .md 无 [SCOPE+] | exit 0 |
| SC.3 | 有 SCOPE+，无 P1 | dispatch-context.md 含 [SCOPE+] | exit 1 |
| SC.4 | 有 SCOPE+，P1 无 SCOPE_RESOLVED | 同上 + 有 P1 | exit 1 |
| SC.5 | 有 SCOPE+，P1 有 [SCOPE_RESOLVED] | 同上 + 有标记 | exit 0 |
| SC.6 | SCOPE+ 出现在非 P 前缀文件 | dispatch-context.md 触发 | exit 0 或 1（按上判定） |

### 5.6 `check-state-yaml.sh`（9 个用例）

| # | 测试名 | 夹具 | 预期 |
|---|--------|------|------|
| SY.1 | 无 .state.yaml | 文件不存在 | exit 2 |
| SY.2 | 空文件 | `0` 字节 | exit 1 |
| SY.3 | 缺 task_id | 仅 `phase: P1` | exit 1 |
| SY.4 | task_id 格式错 | `task_id: T001a` | exit 1 |
| SY.5 | phase 非法 | `phase: P9` | exit 1 |
| SY.6 | retries 非 dict | `retries: 3` | exit 1 |
| SY.7 | retries[P1] 非 list | `retries: {P1: 3}` | exit 1 |
| SY.8 | 全合规 | 完整有效 .state.yaml | exit 0 |
| SY.9 | YAML 语法错 | `task_id: T001\nphase: P1: extra` | exit 1（YAML 解析失败） |

### 5.7 `check-state-transition.sh`（8 个用例）

> **特殊**：此脚本用 `git show HEAD:file`，需要真实 git repo

| # | 测试名 | 夹具 | 预期 |
|---|--------|------|------|
| ST.1 | 无 .state.yaml 暂存 | git 仓库无变更 | exit 0 |
| ST.2 | 新 phase: P1（首次） | 旧 phase 空 | exit 0 |
| ST.3 | 顺序跳 P1→P3 | 跳 2 | exit 0 |
| ST.4 | 回退 P3→P1（差 2） | 警告 | exit 0（降级 WARNING） |
| ST.5 | 回退 P4→P2（差 2） | 警告 | exit 0（降级 WARNING） |
| ST.6 | retries[P2]>=3，phase 非 PAUSED | 列表 3 项 | exit 1 |
| ST.7 | retries[P2]>=3，phase: PAUSED | 列表 3 项 + phase: PAUSED | exit 0 |
| ST.8 | 终止态 PAUSED/READY/DONE | 任意变更 | exit 0 |

### 5.8 `check-changelog.sh`（5 个用例）

| # | 测试名 | 夹具 | 预期 |
|---|--------|------|------|
| CL.1 | 无 CHANGELOG | 文件不存在 | exit 0（不阻塞） |
| CL.2 | 无 [Unreleased] 区域 | 仅历史版本 | exit 1 |
| CL.3 | [Unreleased] 无 task_id | 区域无 T001 | exit 1 |
| CL.4 | [Unreleased] 含 task_id | 含 T001 | exit 0 |
| CL.5 | task_id 在历史版本 | 旧版本含 T001 | exit 1 |

### 5.9 `check-retrospective.sh`（4 个用例）

| # | 测试名 | 夹具 | 预期 |
|---|--------|------|------|
| RT.1 | 无异常 | 正常 .state.yaml + 任务目录 | exit 0，无输出 |
| RT.2 | retries 超限 | retries[P2] 3 项 | exit 0，输出含"重试超限" |
| RT.3 | SCOPE+ 触发 | 产出含 [SCOPE+] | exit 0，输出含"SCOPE+ 触发" |
| RT.4 | override 触发 | P1 含 `override:` | exit 0，输出含"override" |

### 5.10 `check-tdd-red.sh`（8 个用例）

> **特殊**：需 mock 测试运行器（设 TEST_RUNNER env）

| # | 测试名 | 夹具 | 预期 |
|---|--------|------|------|
| TD.1 | 无 TEST_RUNNER + 无 pytest | 空 PATH | exit 3 |
| TD.2 | 测试全绿 | 模拟 pytest 输出 "5 passed" | exit 2 |
| TD.3 | 经典红灯（assertion failure） | 模拟 "2 failed" | exit 0 |
| TD.4 | B 类：ImportError 项目内模块 | `PROJECT_MODULE=myapp` + 错误含 `from myapp` | exit 0 |
| TD.5 | A 类：ImportError 第三方 | `PROJECT_MODULE=myapp` + 错误含 `import requests` | exit 1 |
| TD.6 | A 类：SyntaxError | 模拟 SyntaxError | exit 1 |
| TD.7 | 混合：1 failed + 1 error（B 类） | 模拟混合输出 | exit 0 |
| TD.8 | 启发式：无 PROJECT_MODULE + ImportError | 无 PROJECT_MODULE | exit 0（B 类） |

### 5.11 辅助脚本（`agate-changes.sh` / `agate-summary.sh` / `install-hook.sh`）

这些是辅助工具，不是 gate。**最低限度**：
- `install-hook.sh`：1 个用例——验证安装路径正确性（mock `$HOME` + `AGATE_ROOT`）
- 其他两个：跳过测试（命令式展示，不需要分支覆盖）

---

## 六、回归测试套件

每个已知 bug/隐患 = 一个独立测试文件，确保不再现：

### R1：v0.6 YAML 缩进（`b028315` 引入）

```bash
# tests/regression/v060-yaml-indent.bats
@test "task-files.md executor_env 块 YAML 可解析" {
    local file="$AGATE_ROOT/assets/templates/task-files.md"
    # 提取 executor_env 块
    local block
    block=$(awk '/^executor_env:/,/^[a-z_]+:/' "$file" | head -10)
    # 验证 yaml.safe_load 成功
    echo "$block" | python3 -c "import yaml, sys; yaml.safe_load(sys.stdin)"
    # 没有 YAMLError 即通过
}
```

### R2：v0.6 DESIGN_GAP 配对（cf6cd80）

> ⚠️ **这是"待关闭的已知风险"，不是设计如此**
>
> 当前行为：`check-gate.sh P7` 只扫描 `P7-consistency.md`。如果 architect 忘记把 `P4-implementation.md` 里的 `[DESIGN_GAP: ...]` 转抄到 `P7-consistency.md`，gate 静默放过。
> 现行兜底：`architect.md` 写明"必须转抄"（纯文本约束，靠 architect 记得）。
> 待办（评审已建议）：`check-gate.sh P7` 同时扫描 `P4-implementation.md` 和 `P7-consistency.md`，交叉核对两边的 `[DESIGN_GAP:` 数量；P4 数量 > P7 数量 → 报"architect 遗漏转抄"。
> 优先级：测试基础设施搭起来后实施。

```bash
# tests/regression/v060-design-gap.bats
@test "DESIGN_GAP + REVIEWED 配对可解除（基本功能）" { ... }
@test "DESIGN_GAP 不在 P7-consistency.md → 静默放过（⚠️ 已知风险，不是修复）" {
    # ⚠️ 这个测试通过 = 漏洞仍在。重构或性能优化时不要"顺手修"它——
    # 修这个测试 = 实施 R2 待办的交叉核对方案，必须先开新 issue/PR。
}
```

### R3：v0.6 T045 hardening R4 文件数 bug（`git diff --cached` vs `HEAD~1`）

> commit `fabca40` "feat(hardening): check-pruning.sh 补 P7/P8 裁剪条件 + 裁剪风险评估（R3/R4/R5）" 修复。
> 测试目的是确保未来不会再有人"为了对齐"把 `--cached` 改回 `HEAD~1`。

```bash
# tests/regression/v060-r4-cached.bats
@test "裁剪 P7 时用 --cached 统计源文件数（不是 HEAD~1）" { ... }
```

### R4：v0.6 T045 hardening P8 internal_only

```bash
@test "P8 internal_only 缺失拦截" { ... }
```

### R5：v0.6 P8 chicken-and-egg bug（本次实施评审新发现）

> `check-gate.sh` P8 分支原本用 `git diff HEAD~1` 检查 version/CHANGELOG 变更。
> pre-commit 时本次 commit 还没创建，`HEAD~1` 是上一个 commit，
> P8 阶段 version/CHANGELOG 都在暂存区里——`HEAD~1` 永远看不到，必然 exit 1。
>
> 这是 P4/P7 已踩过的同款 bug，commit `fabca40` 修了 P4/P7，但漏了 P8。
> 评审发现后已修复（HEAD~1 → --cached）。

```bash
# tests/regression/v060-p8-cached.bats
@test "P8 gate 用 --cached 检查 version 文件（不是 HEAD~1）" {
    # 1. 初始化 git 仓库，commit 一个 init
    # 2. 修改 package.json + CHANGELOG.md，但 git add 到暂存区但不 commit
    # 3. 跑 check-gate.sh P8
    # 4. 断言 exit 2（脚本化检查通过，进入主 Agent 验证）
    # 5. 如果 exit 1 → 鸡生蛋 bug 复现
}

@test "P8 gate 用 --cached 检查 CHANGELOG（不是 HEAD~1）" {
    # 同样套路，但只改 CHANGELOG.md
}
```

### R6：占位（未来 bug）

每发现一个新 bug → 立即加一个 R{N}。

### R6：未来新发现的 bug

每个 bug fix commit 都必须新增一个 `@test` 块（**这是 commit 消息模板的强制项**）。

---

## 七、集成测试

### 7.1 pre-commit-hook 端到端（`tests/integration/pre-commit-hook.bats`）

| # | 测试名 | 场景 | 预期 |
|---|--------|------|------|
| IT.1 | 无 .state.yaml 变更 | git add 无关文件 | exit 0（不触发） |
| IT.2 | phase 变更 + gate 通过 | .state.yaml phase: P1 → P2 + 阶段产出 | exit 0 |
| IT.3 | phase 变更 + gate 不通过 | .state.yaml phase: P1 → P2 + 缺文件 | exit 1 |
| IT.4 | [PROD_TOUCHED] 拦截 | diff 含标记 | exit 1 |
| IT.5 | 完整生命周期 P0→DONE | 8 个 phase 全部 | 端到端 0/1/2 序列正确 |

### 7.2 文档一致性（`tests/integration/consistency.bats`）

`check-protocol-consistency.py` 的 7 项检查，每项至少 1 个测试：

```bash
@test "CHECK 1: 所有 .md 文件的 yaml 代码块可解析" {
    run python3 "$AGATE_ROOT/scripts/check-protocol-consistency.py"
    [ "$status" -eq 0 ]  # 0 ERROR
}
@test "CHECK 2: 所有 [xxx](path) 引用存在" { ... }
@test "CHECK 4: gate_commands 键集合与所有 P*.md 一致" { ... }
@test "CHECK 7: README badge 与 git tag 同步" { ... }
```

### 7.3 state-machine.md vs 脚本（`tests/integration/spec-vs-code.bats`）

> **关键创新**：协议文档声明的 gate 规则必须都有对应测试

```bash
# 提取 state-machine.md 中所有 "grep ... 期望 ..." 模式
# 验证每条都对应到 tests/ 中的一个 .bats 用例
@test "state-machine.md P2 行声明有对应 check-pruning 测试" { ... }
```

---

## 八、CI/hook 集成

### 8.1 本地 pre-commit hook

扩展现有 `install-hook.sh`（或新建 `tests/install-tests-hook.sh`）：

```bash
# 安装一个独立的 pre-push hook（避免与项目 pre-commit 冲突）
# 在 git push 之前跑 bats
bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

### 8.2 GitHub Actions

```yaml
# .github/workflows/protocol-tests.yml
name: Protocol Tests
on: [push, pull_request]
jobs:
  bats:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Bats
        run: sudo apt-get install -y bats
      - name: Install shellcheck
        run: sudo apt-get install -y shellcheck
      - name: Run Bats
        run: bats agate/tests/
      - name: Run shellcheck
        run: shellcheck agate/scripts/*.sh
      - name: Run consistency check
        run: python3 agate/scripts/check-protocol-consistency.py
```

### 8.3 状态徽章

```markdown
<!-- README.md -->
![Protocol Tests](https://github.com/randomgitsrc/agate/workflows/Protocol%20Tests/badge.svg)
```

---

## 九、覆盖度指标

### 当前 → 目标

| 指标 | 当前 | 目标 |
|------|------|------|
| 脚本分支覆盖 | 7/31 exit 点手工测过 | 148 个用例覆盖约 91% 决策点（见附录 B 自动校验） |
| 持久化测试 | 0 个 | 90+ 个 |
| 自动化触发 | 0 处 | 2 处 (pre-push + CI) |
| 回归保护 | 0 个 | ≥5 个 |
| 文档一致测试 | 0 个 | ≥7 个 |

### 进度追踪

`tests/README.md` 维护覆盖度表（**用附录 B 的 count-tests.sh 自动生成，不手写**）：

| 脚本 | 计划用例 | 已测 | 覆盖 | 状态 |
|------|--------|-----|------|------|
| check-pruning.sh | 19 | TBD | TBD% | ⏳ |
| check-gate.sh | 33 | TBD | TBD% | ⏳ |
| check-p6-evidence.sh | 11 | TBD | TBD% | ⏳ |
| check-p6-provenance.sh | 15 | TBD | TBD% | ⏳ |
| check-state-yaml.sh | 9 | TBD | TBD% | ⏳ |
| check-scope-resolved.sh | 6 | TBD | TBD% | ⏳ |
| check-state-transition.sh | 8 | TBD | TBD% | ⏳ |
| check-changelog.sh | 5 | TBD | TBD% | ⏳ |
| check-retrospective.sh | 4 | TBD | TBD% | ⏳ |
| check-tdd-red.sh | 8 | TBD | TBD% | ⏳ |
| install-hook.sh | 1 | TBD | TBD% | ⏳ |
| **总计** | **148** | 154 (含 sanity 6) | 100% | ✅ |

> **为什么不写"100%"**：评审发现把"100% 覆盖"当作可量化指标本身就有问题（phase_num 对 "PAUSED" 返回 0 之类 happy path 唯一函数不需要专门测）。TBD 是诚实标注——写完一个 .bats 文件，把数字填上去。

---

## 十、实施路线图

### Phase A：搭骨架（1 步）

- 创建 `tests/` 目录 + `helpers/` + `bats` 安装文档
- 写 `tests/helpers/fixtures.bash` + `git-helper.bash`
- 创建 5 个静态夹具（full-task / ui-affected / vision-blocked / high-risk / paused-task）
- CI workflow 配置文件

### Phase B：覆盖热区（4 步）

| 步 | 内容 | 工时估计 |
|---|------|---------|
| B1 | `check-pruning.bats`（19 用例） | 2h |
| B2 | `check-gate.bats`（33 用例） | 4h |
| B3 | `check-p6-evidence.bats`（11 用例） | 2h |
| B4 | `check-p6-provenance.sh`（15 用例） | 3h |

### Phase C：覆盖长尾（3 步）

| 步 | 内容 | 工时估计 |
|---|------|---------|
| C1 | `check-scope-resolved.bats` + `check-state-yaml.bats` | 2h |
| C2 | `check-state-transition.bats` + `check-changelog.bats` + `check-retrospective.bats` | 2h |
| C3 | `check-tdd-red.bats`（含 mock 测试运行器） | 2h |

### Phase D：回归与集成（3 步）

| 步 | 内容 | 工时估计 |
|---|------|---------|
| D1 | 6 个回归测试（v0.5/v0.6 已知 bug） | 2h |
| D2 | pre-commit-hook 集成测试（5 用例） | 3h |
| D3 | 文档一致性测试（7+ 用例） | 2h |

### Phase E：CI 与维护（2 步）

| 步 | 内容 | 工时估计 |
|---|------|---------|
| E1 | GitHub Actions workflow + badge | 1h |
| E2 | `tests/README.md` + commit 消息模板 + 维护指南 | 1h |

### 总工时：~25 小时

---

## 十一、维护与所有权

### 11.1 commit 消息模板

```markdown
## 修复

## 关联

- [ ] 同步更新 `tests/regression/` 添加回归用例
- [ ] 同步更新 `tests/README.md` 覆盖度表
- [ ] （如改 gate 规则）同步更新 `tests/integration/spec-vs-code.bats`
```

### 11.2 PR 检查项

- [ ] 新增的 `exit N` 分支都有测试
- [ ] 回归测试覆盖这个 bug
- [ ] `bats` 全过
- [ ] `shellcheck` 无警告

### 11.3 何时跑测试

- **本地**：开发时跑对应脚本的 `.bats`；push 前跑 `bats agate/tests/`
- **CI**：push + PR 自动跑
- **release**：tag 前必须全绿

### 11.4 何时更新

- 改 gate 规则 → 必须先加失败测试，再改脚本
- 发现新 bug → 修脚本前先写回归测试
- 协议文档声明新规则 → 必须新增对应测试

---

## 十二、待评审问题

1. **夹具管理策略**
   - 选 A：纯函数化（`fixtures.bash` 按需构造）——灵活但慢
   - 选 B：静态夹具 + 函数化混合（推荐）——Gold 任务 + 边界 case 函数化

2. **回归测试来源**
   - 选 A：仅 v0.5+ 已知 bug（推荐，先打牢）
   - 选 B：所有 T001+ 历史 bug

3. **是否引入 bats-assert / bats-support 库？**
   - 选 A：纯 Bats（推荐，最小依赖）
   - 选 B：带增强库（断言可读性 +）

4. **TDD 检查脚本的 mock 策略**
   - 选 A：在测试目录里放伪 pytest 脚本（推荐）
   - 选 B：bash function override 真实 pytest

5. **覆盖度指标 100% 是硬指标吗？**
   - 选 A：100% 强制（推荐，符合 TDD 理念）
   - 选 B：核心 gate 100%，辅助工具宽松

> 第 0 节已决定：测试放在 `agate/tests/`，不再列在待评审项中。

---

## 附录 A：现有脚本一览

| 脚本 | 行数 | 测试用例数 | 优先级 |
|------|-----|-----------|-------|
| `check-pruning.sh` | 144 | 19 | P0（高频） |
| `check-gate.sh` | 115 | 33 | P0（核心） |
| `check-p6-provenance.sh` | 242 | 15 | P0（安全） |
| `check-p6-evidence.sh` | 87 | 11 | P0（核心） |
| `check-state-transition.sh` | 91 | 8 | P1（pre-commit） |
| `check-tdd-red.sh` | 109 | 8 | P1（核心） |
| `check-state-yaml.sh` | 74 | 9 | P1（pre-commit） |
| `check-scope-resolved.sh` | 45 | 6 | P2 |
| `check-changelog.sh` | 31 | 5 | P2 |
| `check-retrospective.sh` | 57 | 4 | P2 |
| `gate-result.sh` | 70 | 库函数 | 不测 |
| `pre-commit-gate.sh` | 122 | 集成入口 | 集成测试 |
| `agate-summary.sh` | 69 | 展示脚本 | 跳过 |
| `agate-changes.sh` | 109 | 展示脚本 | 跳过 |
| `install-hook.sh` | 34 | 1 | 安装脚本 |

**总测试用例数**：20+34+11+16+6+9+8+5+4+9+13+5+7+1 = **148 个核心测试用例**（+ 6 sanity = 154）

> 注：v1 初版自报 95，v2 修订为 111，v3 修订为 119，v3.1 修订为 148（实施中新增边界用例 + R2.3 修复新增 2 用例 + G7.7 新增 1 用例）。**所有数字以 `count-tests.sh` 从 `.bats` 文件自动统计为准**——人工数表会漂移。

> 真实决策点 130+，exit 点 63，148 个测试用例覆盖约 91% 决策点。**不要把"100% 决策点覆盖"作为可量化指标**——追求 100% 会逼出无意义测试（如 phase_num 对 "PAUSED" 返回 0 这种只对 happy path 有意义的函数）。

---

## 附录 B：覆盖度自校验脚本

```bash
# tests/scripts/count-tests.sh — 从 .bats 文件自动统计
# 用法：bash tests/scripts/count-tests.sh
# 输出：每个 .bats 文件的 @test 数量 + 总计
# 评审发现 v1 自报数字错位根因：人工数表格行数 + 手算加总会漂移
# 此脚本让"测试用例数"和"实际写的 .bats 文件"保持一致

#!/usr/bin/env bash
cd "$(dirname "$0")/.."
total=0
echo "=== 测试用例覆盖度自检 ==="
for f in unit/*.bats regression/*.bats integration/*.bats; do
    [ -f "$f" ] || continue
    count=$(grep -c '^@test' "$f")
    total=$((total + count))
    printf "  %-50s %3d 个 @test\n" "$f" "$count"
done
echo "==="
echo "总计：$total 个测试用例"
echo ""
echo "如果此数字与本文档附录 A 不一致 → 文档漂移，需要更新。\n如果文档改了但 .bats 文件没动 → 测试计划空头支票。"
```
