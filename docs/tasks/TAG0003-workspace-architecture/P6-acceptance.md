---
phase: P6
task_id: TAG0003-workspace-architecture
type: acceptance
parent: P5-verification.md
trace_id: TAG0003-P6-20260812
status: draft
created: 2026-08-12
agent: verifier
pass: 20
fail: 0
ui_affected: false
---

# TAG0003 — agate 工作区架构：P6 验收

> 角色：verifier（P6 验收模式，只读验证，未修改任何 agate/ 文件）。
> 验收对象：worktree `agate/`（分支 dev/workspace，HEAD=2bf9221 P5 commit）。
> 对照基线：P1-requirements.md 的 20 条 BDD（含 SCOPE+ 增补），全量逐条实跑/grep 验证。
> 环境标记：`[PROD_NOT_TOUCHED]` 仅在 /tmp/opencode/ fixture 仓库实跑（迁移/解析/roadmap 模拟），未接触生产环境，`~/.agate` 稳定版未动。
> 方法：行为类 BDD（BDD-1/2/3/4/5/6/7/8/9/18/19）用 fixture 实跑；文档/路径类 BDD（BDD-10/11/12/14/15/16/17）用 grep + 模拟闭环；回归类（BDD-13/20）用全量 bats + 一致性 + count 实跑。

## 工作区初始化与目录规范

- PASS BDD-1: 新项目初始化创建完整规范工作区——fixture 实跑初始化命令建出 roadmap/tasks/agents/archived/reviews/decisions/plans/logs 全部 8 子目录，且 orchestrator-template.md:102 + SETUP.md:114 均含同一 mkdir 命令(bdd-01-init.log)
> 【2026-08-12 修订注】口径由 TAG0001 更新为 **9 子目录**（含 `debt/`）——WORKFLOW.md 目录规范已改，本记录保留原 8 子目录证据；BDD-4 重验判据 = 修订注存在 + 三处 mkdir 与目录图一致为 9。
- PASS BDD-2: 默认工作区位置为项目内 agate-workspace/——无 .agate.env 时解析器输出 AGATE_WORKSPACE={project_root}/agate-workspace、tasks_base=工作区根/tasks(bdd-02.log)
- PASS BDD-3: `.agate.env` 可将工作区指向项目外路径——.agate.env 声明外部绝对路径时解析器输出外部路径，且项目根不新建默认 agate-workspace/(bdd-03.log)
- PASS BDD-4: 无 `.agate.env` 时不报错、走默认位置——解析器 exit 0 且工作区用默认位置，无配置错误(bdd-04.log)
- PASS BDD-5: 工作区路径含空格仍正常工作——AGATE_WORKSPACE=My Project/agate-workspace 解析正确（空格保留），含空格路径下 mkdir+写文件成功(bdd-05.log)

## 从 docs/tasks 强制迁移

- PASS BDD-6: 迁移工具将既有 docs/tasks 内容迁入工作区——fixture git 仓库（含 active-tasks.md + T001-fake 任务目录）实跑迁移，看板与任务目录全部落工作区 tasks/，原 docs/tasks/ 消失不再承担编排职责(bdd-06.log)
- PASS BDD-7: 迁移不丢失任务状态与阶段产出——迁移前后文件清单对照（4=4）：active-tasks.md、P1-requirements.md 与**被 gitignore 的 .state.yaml** 全部随迁无丢失(bdd-07-assert.txt)
- PASS BDD-8: 迁移保留 git 历史——目录级 git mv 记 R rename，git log --follow 在新路径可追溯 init+migrate 两个 commit，非删除重建(bdd-08.log)
- PASS BDD-9: 迁移幂等——重复运行迁移工具 no-op exit 0，工作区目录无重复（archived/tasks 各一份）、文件数不变(bdd-09.log)
- PASS BDD-10: 未迁移的旧布局项目在编排时获得明确迁移指引——orchestrator-template.md:71 旧布局检测（docs/tasks/active-tasks.md 存在而工作区无）+ :73-75 迁移指引（给迁移命令 + 停止自动推进）+ :77 不静默继续/不静默失败(bdd-10-assert.txt)

## orchestrator 工作区感知

- PASS BDD-11: orchestrator 从工作区内路径读取 project.md——{AGATE_WORKSPACE}/agents/project.md 3 处引用，旧的 docs/agents 路径已从 orchestrator-template 移除(bdd-11-assert.txt)
- PASS BDD-12: orchestrator 从工作区内路径读取任务看板——{AGATE_WORKSPACE}/tasks/active-tasks.md 为读取路径（4 处引用），docs/tasks/active-tasks.md 仅作旧布局检测条件(bdd-12-assert.txt)
- PASS BDD-13: 任务状态机与 gate 以工作区为任务根、行为不变——pre-commit-gate.sh 经解析器取 AGATE_TASKS_DIR、check-state-transition.sh 改用 dirname!=REPO_ROOT 去硬编码、check-pruning.sh 跟随工作区路径；全量 bats 631 ok / 0 not ok（plan 1..631）行为不变，工作区相关测试（resolve/migrate/state-transition）48/0(bdd-13-bats.log, ../P5-test-results/unit.md)

## roadmap 项目级任务管理循环

- PASS BDD-14: 新需求/讨论进入工作区 roadmap——WORKFLOW.md:110 backlog 规范 + roadmap-template.md 存在 + 模拟执行真实追加含状态标识的 backlog 条目(bdd-14-assert.txt, roadmap-simulate.md)
- PASS BDD-15: roadmap 条目拆分为任务进入待开始看板——WORKFLOW.md:111 scheduled 规范 + 模拟拆分：工作区建任务目录、active-tasks.md「待开始」写任务行含 roadmap: 关联、条目状态→scheduled(bdd-15-assert.txt, roadmap-simulate.md)
- PASS BDD-16: 任务完成回写 roadmap（闭环）——WORKFLOW.md:112 done/cancelled 回写规范 + 模拟回写：条目状态→done、关联任务列可见、双向可追溯(bdd-16-assert.txt, roadmap-simulate.md)

## 内容边界

- PASS BDD-17: 编排状态与项目文档按二值判据分流——WORKFLOW.md:93-104 判据正式规则（二值判定 + 对偶自洽性），双场景对偶应用结论相反：任务验收记录→工作区、项目 README→项目 docs/(bdd-17-assert.txt)

## 归档迁移、空源迁移与工具链

- PASS BDD-18: 存量归档迁入工作区 archived/ 且幂等——fixture docs/archived/tasks/T000-old/report.md 整体迁入工作区 archived/、相对结构保留、无文件丢失、重复运行 no-op(bdd-18.log)
- PASS BDD-19: 项目从未有过 docs/tasks/ 时迁移工具正常运行——空源 fixture 实跑 no-op exit 0，迁移后工作区 tasks/ 仍可正常初始化(bdd-19.log)
- PASS BDD-20: 迁移后一致性检查白名单与用例数基线全绿——check-protocol-consistency.py 0 ERROR（CHECK 1-4/6-9 全 PASS，白名单已含 agate-workspace/）+ count-tests 总计 625 与 P5 基线一致无漂移(bdd-20-consistency.log, bdd-20-count.log)

**Summary**: PASS 20, FAIL 0(20/20 BDD 全覆盖，无中间态)

## 附注

- BDD-6 中「原 docs/tasks/ 不再承担编排职责」的推论落点（P1 注）：fixture 迁移后 docs/tasks 物理消失 + BDD-11/12/13 的读取路径切换均已独立验证，推论成立。
- BDD-8 外部工作区场景（.agate.env 指向项目外）下 git mv 失败走 fallback 普通 mv——本验收仅在仓库内场景实跑，外部场景限制由迁移工具 WARNING 明确标注（agate-migrate-workspace.sh:88），属设计声明的固有限制，不影响本 BDD 判定。
- 证据文件均在 P6-evidence/（22 个），每条 PASS 均有对应证据引用；全部 .log 末行含 EXIT_CODE: 0。
