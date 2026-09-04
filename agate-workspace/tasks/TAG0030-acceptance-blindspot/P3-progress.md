# P3-progress — TAG0030 test-designer 分阶段落盘

## 2026-09-04 步骤 1：输入读取完成
- 已读：test-designer.md 角色、P3-dispatch-context、AGENTS.md、P0-brief、P1-requirements（BDD-1~21）、
  P2-design（§0.1 落点表 / §2 改动详述 / §5 gate_commands / §6 files_to_read）、模式源
  test_protocol_mechanism_anchors.py（ANCHOR_CASES 表驱动）与 test_review_role_docs.py（逐条 assert）、
  conftest.py（agate_root fixture）、plan-design-review.md 全文、dispatch-context.md 模板全文、
  tests/README.md 何时更新节、P3/P4 卡 step0 段。
- 决策：选 ANCHOR_CASES 表驱动模式（与 TAG0012 同款，P2-review N1 点名的一致性优先）。

## 2026-09-04 步骤 2：锚词当前命中核实（假绿判定）
- P3/P4/P6/P1 卡 + analyst.md + verifier.md + tests/README + dispatch-context 模板 + AGENTS.md：
  目标锚词（清理钩子/创建即注册/无条件删除/200-204-404/残留检查/post-test/人工体验/seed/页面有内容/
  真实 gate 语义/全量扫描/新增 CHECK/拆小/体量/环境还原/DOM 度量/getBoundingClientRect/视觉契约/可表达子集）当前全 0 命中 → 真红。
- plan-design-review.md 假绿点（既有条文命中，需 AND 语义规避）：「布局型」行 19（常规布局型任务启用）、
  「渲染正确性/动效时序/形态/渲染组件」行 21（渲染正确性与时序维度行）、「0-10」行 13、「status」行 32-35。
  → BDD-10 用（ui_render_shape+形态分派头）、BDD-11 用（布局型三组+布局/交互/视觉）、BDD-12 用（渲染组件型+architect）、
    BDD-14 用（0-10+status+原样保留，原样保留 0 命中保整体红）、BDD-15 用（未声明+缺省）。
- architect.md 假绿点：「对齐」行 111/221（时间戳对齐/批次边界对齐，语义不同）→ BDD-16/17 不用「对齐」作锚词，
  改用（视觉契约+可表达子集+DOM 度量）/（DOM 度量+不收主观视觉）。

## 2026-09-04 步骤 3：产出完成
- 测试代码：agate/tests/unit/test_tag0030_assertions.py（21 个 test_bdd_N_ 用例，BDD-1~21 全覆盖 1:1；
  逐条 assert 模式；windows_smoke 标记 Phase 1~4 首用例；平台无关 Path.read_text + in）
- P3-test-cases.md：frontmatter 8 必填字段（phase/task_id/type/parent/trace_id/status/created/test_code_dir）已写入，
  check-frontmatter.py exit 0；正文含假绿核实表 + BDD-1~21 用例清单 + P4 落笔注意
- 红灯验证：`python3 -m pytest agate/tests/unit/test_tag0030_assertions.py -q` → 21 failed in 0.10s，
  全部 B 类 assertion 失败（无 A 类 SyntaxError / 第三方 import）
- 假绿规避确认：plan-design-review 既有命中词（布局型/渲染正确性/动效时序/0-10/status/形态）全部改 AND 语义
  至少一个当前 0 命中锚词兜底（三组/渲染组件型+architect/原文保留/回落/ui_render_shape/维度组）；
  architect「对齐」行 111/221 语义不同，BDD-16/17 改用视觉契约/可表达子集/不收主观视觉
