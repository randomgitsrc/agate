---
phase: P3
task_id: TAG0003-workspace-architecture
type: test-cases
parent: P2-design.md
trace_id: TAG0003-P3-20260812
status: draft
created: 2026-08-12
agent: test-designer
---

# TAG0003 — agate 工作区架构：P3 测试用例清单

> TDD 红灯阶段。所有测试代码已写入 worktree `agate/tests/`，P4 实现尚未开始，断言均针对「未来实现应有的行为」，现处红灯。
> 角色：test-designer（`~/.agate/assets/execution-roles/test-designer.md`）。
> 范围：仅 P2-design.md §1.1/§3.7 明确的 3 个测试文件；既有 8 个 .bats 的 fixture 换血（377 处路径）不在 P3 范围（P4 做）。

**test_code_dir: `agate/tests/`**（新测试落在 `agate/tests/unit/`，P2-design.md §5 gate_commands.P3 固化指向 `agate/tests/unit/agate-workspace-resolve.bats agate/tests/unit/agate-migrate-workspace.bats agate/tests/unit/check-state-transition.bats`，代码须在既有 tests 树内才能被 gate 命令发现）

## 0. 产出总览

| 项 | 值 |
|---|---|
| P1 BDD 总数 | 20（BDD-1..20，risk_level=high） |
| 新增测试文件 | 2（`unit/agate-workspace-resolve.bats` 9 个 @test、`unit/agate-migrate-workspace.bats` 8 个 @test） |
| 修改测试文件 | 1（`unit/check-state-transition.bats`，追加 ST_WS.1-4 检测语义测试，既有 26 用例未动） |
| 新增 @test 合计 | 21 |
| 当前红灯数 | 19（WR.1-9 ×9、MW.1-8 ×8、ST_WS.1/2 ×2） |
| 回归守卫（绿） | 2（ST_WS.3 根级行为不变、ST_WS.4 旧布局行为不变） |
| 用例数基线 | 迁移前 603 → 本任务新增 21 = **624**（BDD-20 口径：既有 603 换血不改数，新增迁移工具/解析器用例允许增长，P2 §3.7） |
| P3 gate 实测 | `bats --formatter tap` 三文件 → 47 用例 / 19 not ok / 28 ok，TAP 可被 generic-tap.sh 解析；check-tdd-red.sh exit 0（classic red-light） |

## 1. 新交付物接口契约（P4 implementer 必须满足，测试按此断言）

### 1.1 `agate-workspace-resolve.sh`

```bash
bash agate-workspace-resolve.sh [PROJECT_ROOT]    # PROJECT_ROOT 默认 $PWD
```

- 输出两行：`AGATE_WORKSPACE=<绝对路径>`、`AGATE_TASKS_DIR=<绝对路径>`（被 source 时同时 export 同名变量）。
- 解析优先级（P2 §3.1）：
  1. 项目根 `.agate.env` 含 `AGATE_WORKSPACE=` → 工作区根 = 该值（相对路径相对项目根解析、绝对路径原样、含空格）；
  2. 否则环境变量 `AGATE_TASKS_DIR` → tasks_base = 该值（向后兼容）；
  3. 否则默认 → 工作区根 = `{PROJECT_ROOT}/agate-workspace`，tasks_base = 工作区根/tasks。
- 全程引号包裹 + `realpath -m` 归一（含空格路径）；解析器不创建目录。

### 1.2 `agate-migrate-workspace.sh`

```bash
cd <project_root> && bash agate-migrate-workspace.sh [--to <workspace>]
```

- 目录级 `git mv docs/tasks {workspace}/tasks`、`git mv docs/archived {workspace}/archived`（物理移动含 gitignore 的 .state.yaml / 未追踪文件，BDD-7）。
- 空源（docs/tasks 不存在或为空）→ no-op exit 0（BDD-19）；已迁移 → 幂等（BDD-9）。
- 目标仓库外 git mv 失败（exit 128）→ fallback 普通 `mv` + 输出含 `WARNING` 的 git 历史限制标注（BDD-3/8）。
- 迁移后输出迁移摘要（含「迁移」字样，BDD-10 不静默）。

## 2. BDD → 测试 1:1 映射（20 条全覆盖）

> 映射口径沿用 T001-P3 先例：可执行 BDD 对应 @test（测试名引用 BDD 编号，带 Examples 的 BDD 拆多个用例共享编号）；
> 无 P3 可断言程序对象的 BDD（roadmap 循环、内容边界判据、初始化 mkdir、一致性/用例数基线）显式声明验证载体（P5/P6/P7 或文档检索），不伪造程序断言。

| BDD | 描述 | 测试用例 | 文件 | 当前状态 |
|---|---|---|---|---|
| BDD-1 | 新项目初始化创建 8 子目录 | 无 P3 @test。验证载体：P4 交付的 orchestrator-template.md §3.3 mkdir 8 子目录 + SETUP.md 初始化步骤，P6 人工核对（初始化路径与迁移路径分离，P2-review 观察项 2） | — | P6 验证（doc 载体） |
| BDD-2 | 默认工作区位置 agate-workspace/ | `WR.1` | unit/agate-workspace-resolve.bats | **红** |
| BDD-3 | .agate.env 指向项目外 | `WR.3`（绝对路径）+ `WR.4`（相对路径边界） | unit/agate-workspace-resolve.bats | **红** ×2 |
| BDD-4 | 无 .agate.env 不报错走默认 | `WR.2` | unit/agate-workspace-resolve.bats | **红** |
| BDD-5 | 路径含空格正常工作 | `WR.5` | unit/agate-workspace-resolve.bats | **红** |
| BDD-6 | docs/tasks 迁入工作区 tasks/ | `MW.1` | unit/agate-migrate-workspace.bats | **红** |
| BDD-7 | 不丢失 .state.yaml 与阶段产出 | `MW.2`（含 gitignore 的 .state.yaml 迁移 + 文件数对照） | unit/agate-migrate-workspace.bats | **红** |
| BDD-8 | 迁移保留 git 历史 | `MW.3`（git log --follow 新路径可追溯旧 commit）+ `MW.8`（仓库外目标 fallback mv + WARNING） | unit/agate-migrate-workspace.bats | **红** ×2 |
| BDD-9 | 迁移幂等 | `MW.4`（重复运行文件清单不变、无重复目录） | unit/agate-migrate-workspace.bats | **红** |
| BDD-10 | 旧布局获得明确迁移指引 | `MW.5`（迁移输出含「迁移」指引、不静默） | unit/agate-migrate-workspace.bats | **红** |
| BDD-11 | orchestrator 读工作区 project.md | `WR.8`（解析输出锚定 $AGATE_WORKSPACE/agents/project.md） | unit/agate-workspace-resolve.bats | **红** |
| BDD-12 | orchestrator 读工作区任务看板 | `WR.9`（解析输出锚定 $AGATE_TASKS_DIR/active-tasks.md） | unit/agate-workspace-resolve.bats | **红** |
| BDD-13 | 状态机与 gate 以工作区为任务根、行为不变 | `WR.6`（AGATE_TASKS_DIR 二级源）+ `WR.7`（.agate.env 优先）+ `ST_WS.1`（agate-workspace/tasks 任务级检测真红）+ `ST_WS.2`（自定义路径任务级检测真红）+ `ST_WS.3`/`ST_WS.4`（根级/旧布局回归守卫，行为不变） | unit/agate-workspace-resolve.bats / unit/check-state-transition.bats | **红** ×4 + 绿 ×2 |
| BDD-14 | 新需求/讨论进入 roadmap | 无 P3 @test。验证载体：P4 交付的 roadmap-template.md + WORKFLOW.md 循环规范（§3.4），P6 人工核对条目状态标识 | — | P6 验证（doc 载体） |
| BDD-15 | 条目拆分进待开始看板 | 同上（WORKFLOW.md 循环规范 + active-tasks「待开始」区关联规则） | — | P6 验证（doc 载体） |
| BDD-16 | 任务完成回写 roadmap | 同上（WORKFLOW.md 循环规范 + roadmap 状态机 done/cancelled） | — | P6 验证（doc 载体） |
| BDD-17 | 内容边界二值判据 | 无 P3 @test。验证载体：P4 交付的 WORKFLOW.md 判据文档锚点（§3.5）+ 双场景对偶断言，P6/P7 核对 | — | P6/P7 验证（doc 载体） |
| BDD-18 | 归档迁入 archived/ 且幂等 | `MW.6`（docs/archived → workspace/archived 相对结构保留 + 重复运行文件数不变） | unit/agate-migrate-workspace.bats | **红** |
| BDD-19 | 空源迁移正常 | `MW.7`（无 docs/tasks 时 no-op exit 0、不建错目录） | unit/agate-migrate-workspace.bats | **红** |
| BDD-20 | 一致性白名单与用例数基线 | 无 P3 @test。验证载体：P5_consistency（check-protocol-consistency.py 0 ERROR）+ P5_count（count-tests.sh，口径见 P2 §3.7：既有 603 换血不改数、新增允许增长） | — | P5 验证 |

## 3. 红灯自检（P3 门槛）

| 红测试 | 失败原因 | 合规性 |
|---|---|---|
| WR.1-9（9 个） | `bash: agate-workspace-resolve.sh: No such file or directory`（run exit 127）→ 首个断言 `[ "$status" -eq 0 ]` 失败 | ✅ 被测模块未实现（脚本不存在） |
| MW.1-8（8 个） | `bash: agate-migrate-workspace.sh: No such file or directory`（run exit 127）→ 首个断言 `[ "$status" -eq 0 ]` 失败 | ✅ 被测模块未实现（脚本不存在） |
| ST_WS.1/2（2 个） | check-state-transition.sh L28 仍为 `grep -qE 'docs/tasks/[^/]+/'`，`agate-workspace/tasks/T001/.state.yaml` 与 `custom-tasks/T001/.state.yaml` 均不匹配 → 任务级文件误走 basename 分支 → `git show HEAD:.state.yaml` 取空 → 回退 P3→P1（差 2）未被拦截（期望 exit 1，实际 exit 0） | ✅ 被测模块未改（仍是旧 grep 逻辑） |

- 无一条红灯的失败原因是「断言与测试数据矛盾」——均为被测模块未实现/未改，非测试代码 bug。
- 回归守卫 ST_WS.3/4 当前绿（根级/旧布局在去硬编码前后行为一致），是「行为不变」锚点，非实现先行。
- 既有 check-state-transition.bats 26 用例全部保持绿（未改 fixture、未换血）；其余 8 个 .bats 文件未触碰。

## 4. P6 二值规则自检

所有测试断言均为可二值判定的程序行为（exit code / 文件存在性 / 输出子串 / git 历史可追溯），无「调整/跳过/覆盖」中间态。P6 逐条 PASS/FAIL 判定有明确载体（BDD 对照表 + 各 @test）。

## 5. UI 任务判断

P2-design.md 声明 `ui_affected: false`，本任务非 UI 任务，不产出 Playwright/E2E 用例。

## 6. TAP 兼容性确认

P3 gate 命令 `bats --formatter tap <3 文件>` 实测输出 `1..47` + `ok N` / `not ok N`，与 generic-tap.sh 正则（`^ok\b` / `^not ok\b`）匹配；check-tdd-red.sh 读 P2 gate_commands.P3 实测 exit 0（classic red-light）。测试名不含行首 `- PASS` / `- FAIL` 格式。

## 参考

- P1-requirements.md（20 条 BDD 全文，测试主要来源）
- P2-design.md §3.1/3.2（解析器/迁移工具接口）、§3.6（任务级检测去硬编码）、§3.7（白名单/用例数口径）、§5（gate_commands）
- P2-review.md（观察项 2：BDD-19/BDD-1 判定分离）
- AGENTS.md（测试约定：helpers、BATS_TEST_TMPDIR、load.bash）
- T001-P3 先例（docs/archived/tasks/T001-v2.0-structured/P3-test-cases.md）
