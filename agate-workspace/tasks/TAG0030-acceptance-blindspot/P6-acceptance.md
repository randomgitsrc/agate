---
phase: P6
task_id: TAG0030
type: acceptance
parent: P5-verification.md
trace_id: TAG0030-P6-20260904
status: draft
created: 2026-09-04
agent: verifier
pass: 21
fail: 0
ui_affected: false
---

# P6-acceptance — TAG0030 验收盲区机制批（RM-AG0057 四类 + DEBT0024/25/26）

> P6 验收（verifier 模式）：逐条实跑 P1-requirements.md 的 BDD-1~21（全量 21 条），
> 每条 PASS 附 P6-evidence/ 真实证据（断言审计用例 PASS 输出 + 协议文件 grep 锚词命中 +
> consistency 0 ERROR 输出 + count-tests 1457）。验收事实记录于 2026-09-04。
> 环境隔离：本任务为纯协议文档面改造，验收只读 worktree `agate/` 协议文件 + 跑测试/grep，
> 未改动任何协议文件，未触碰生产环境 `[PROD_NOT_TOUCHED]`。

## 验收环境

- worktree：`.worktrees/agate-TAG0030`（分支 `feat/TAG0030-acceptance-blindspot`）
- 断言审计：`python3 -m pytest agate/tests/unit/test_tag0030_assertions.py -q --tb=short` → 21 passed
- consistency：`python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` → 0 ERROR（329 WARNING 存量，exit 0）
- count-tests：`bash agate/tests/scripts/count-tests.sh` → 总计 1457 个测试用例（较基线 1436 +21）
- 证据引用路径相对 P6-evidence/；每条 PASS 的证据文件均真实存在且被引用（provenance 审计 1a/1c）

## Phase 1 — 测试副作用/环境还原 gate（RM-AG0057-①）

- PASS BDD-1: P3 卡声明创建型测试清理钩子要求——「创建型测试清理钩子（强制要求）」节含「清理钩子」「创建即注册」条文，断言审计 test_bdd_1 通过 (bdd-1-anchor.txt, assert-full.log)
- PASS BDD-2: P4 卡同步声明创建型测试清理要求——P4-implementation.md 含与 P3 同源「清理钩子」「创建即注册」锚词（同类补齐，杜绝只修一处），断言审计 test_bdd_2 通过 (bdd-2-anchor.txt, assert-full.log)
- PASS BDD-3: 清理钩子规则含「无条件删除 + 接受 200/204/404」语义——P3 卡条文写明「无条件删除（不因响应非 2xx 中止删除）、删除接受 200/204/404 为已清理（afterEach 清理队列模式）」，断言审计 test_bdd_3 通过 (bdd-3-anchor.txt, assert-full.log)
- PASS BDD-4: P6 卡补 post-test 环境残留检查步骤——P6-acceptance.md 含「残留检查」「post-test」条文（快照比对或清理钩子验证），断言审计 test_bdd_4 通过 (bdd-4-anchor.txt, assert-full.log)
- PASS BDD-5: dispatch-context 模板声明环境清理/还原要求条目位——模板约束节含「环境还原」「残留检查」锚词，断言审计 test_bdd_5 通过 (bdd-5-anchor.txt, assert-full.log)
- PASS BDD-6: 断言审计单测锁定 Phase 1 新增条文（回归防线）——test_tag0030_assertions.py 对 P3/P4/P6 卡路径 + 锚词及模板路径 + 锚词做 grep 断言（test_bdd_6 汇总锁定清理钩子/残留检查/环境还原），全量 21 用例转绿，条文被删即转红 (bdd-6-anchor.txt, assert-full.log)

## Phase 2 — P1 人工体验路径验收节（RM-AG0057-②）

- PASS BDD-7: P1 卡声明「人工体验路径验收」节——P1-requirements.md 卡含「人工体验」「seed」条文（seed 影响页面内容 → 强制补 seed BDD），断言审计 test_bdd_7 通过 (bdd-7-anchor.txt, assert-full.log)
- PASS BDD-8: analyst 角色文件声明同一条人工体验验收要求——analyst.md 含「人工体验」「seed」同源要求句（不得只用 fixture 验收），断言审计 test_bdd_8 通过 (bdd-8-anchor.txt, assert-full.log)
- PASS BDD-9: 「Given seed 数据 → 页面有内容」成为 BDD 强制句式——P1 卡条文含「seed 数据」「页面有内容」强制句式语义，断言审计 test_bdd_9 通过 (bdd-9-anchor.txt, assert-full.log)

## Phase 3 — plan-design-review 形态驱动化（RM-AG0057-③）

- PASS BDD-10: plan-design-review 先读受评任务 ui_render_shape 再加载维度组——角色文件「形态分派头」节含「ui_render_shape」「维度组」条文，断言审计 test_bdd_10 通过，consistency 0 ERROR（CHECK11 白名单锚点保持） (bdd-10-anchor.txt, assert-full.log, consistency.log)
- PASS BDD-11: 布局型形态加载布局/交互/视觉三组评分细则——角色文件定义「布局型」「三组」（布局/交互/视觉归组，0-10 输出保留），断言审计 test_bdd_11 通过，consistency 0 ERROR (bdd-11-anchor.txt, assert-full.log, consistency.log)
- PASS BDD-12: 渲染组件型形态加载渲染正确性/动效时序组并对接 architect checklist——角色文件含「渲染组件型」「architect」「渲染正确性」条文（引用 architect 渲染 checklist），断言审计 test_bdd_12 通过，consistency 0 ERROR（CHECK11 三锚词保持） (bdd-12-anchor.txt, assert-full.log, consistency.log)
- PASS BDD-13: 每个启用维度要求布局方案 ≥2 候选 + 权衡（candidate_count 下沉 UI 布局层）——角色文件含「候选」「权衡」评审要求条文，断言审计 test_bdd_13 通过，consistency 0 ERROR (bdd-13-anchor.txt, assert-full.log, consistency.log)
- PASS BDD-14: 0-10 评分输出格式与 status 字段保持（门槛读 status 不变）——角色文件保留「0-10」分值行与「status」映射行「原文保留」，断言审计 test_bdd_14 通过，consistency 0 ERROR（check-gate P2 门槛契约未破坏） (bdd-14-anchor.txt, assert-full.log, consistency.log)
- PASS BDD-15: 无形态声明时回落布局型默认（既有行为兼容）——角色文件写明「回落」「布局型」缺省语义（既有 7 维评分路径行为不变），断言审计 test_bdd_15 通过，consistency 0 ERROR (bdd-15-anchor.txt, assert-full.log, consistency.log)

## Phase 4 — 视觉契约断言收录 + DEBT0024/25/26

- PASS BDD-16: 视觉契约「可表达子集」定义收录——architect.md 视觉 checklist 头部单源定义「视觉契约」「可表达子集」（只收可量化 DOM 度量、不收主观视觉），断言审计 test_bdd_16 通过 (bdd-16-anchor.txt, assert-full.log)
- PASS BDD-17: P2 视觉 checklist 提及可量化 DOM 度量断言——architect.md 视觉 checklist 含「DOM 度量」「不收主观视觉」指引（宽度/高度/对齐/重叠/溢出五类），断言审计 test_bdd_17 通过 (bdd-17-anchor.txt, assert-full.log)
- PASS BDD-18: P6/verifier 指南提及 DOM 度量断言为辅助证据形式——verifier.md 证据形式指南含「DOM 度量」+「getBoundingClientRect」示例（截图之外的非截图量化证据），断言审计 test_bdd_18 通过 (bdd-18-anchor.txt, assert-full.log)
- PASS BDD-19: 协议测试设计约定写明「gate 消费方测试夹具走真实 gate 语义」（DEBT0024 closure）——tests/README.md「何时更新」节含「真实 gate 语义」条文，断言审计 test_bdd_19 通过，count-tests 1457（+21） (bdd-19-anchor.txt, assert-full.log, count-tests.log)
- PASS BDD-20: 开发约定写明「新增 CHECK 上线前先全量扫描存量」（DEBT0025 closure）——仓库根 AGENTS.md「改脚本的工作流」节含「全量扫描」「新增 CHECK」第 0 步条文，断言审计 test_bdd_20 通过 (bdd-20-anchor.txt, assert-full.log)
- PASS BDD-21: dispatch-context 模板派发指引含大任务拆小默认指导（DEBT0026 closure）——模板约束节含「拆小」「体量」默认指导（>5 文件/大文档按体量评估拆小，与 TAG0028 内部自主拆互补），断言审计 test_bdd_21 通过，count-tests 1457（+21） (bdd-21-anchor.txt, assert-full.log, count-tests.log)

**Summary**: 21/21 PASS，0 FAIL。全部 21 条 BDD 逐条实跑验收：断言审计 21 用例全绿 + 21 个锚词 grep 命中文件 + consistency --strict-errors-only 0 ERROR + count-tests 1457。自查≠gate：最终判定由主 Agent 跑 check-p6-format.py --fix / check-gate.py P6 / check-p6-evidence.py / check-p6-provenance.py 完成，本文件不自称验收已通过。
