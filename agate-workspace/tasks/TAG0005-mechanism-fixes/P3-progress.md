
## 2026-08-13 test-designer progress

- [x] 读 P3-dispatch-context-test-designer.md（6 处修复 + 对应测试文件映射）
- [x] 读 test-designer.md 角色定义
- [x] 读 P0-brief.md（env_constraints: Linux UTF-8；test_cmd bats 全量 + consistency --strict）
- [x] 读 P1-requirements.md（16 条 BDD）
- [x] 读 P2-design.md（6 处修复方案 + gate_commands + files_to_read）
- [x] 读 P2-review.md（approved + NB：GPC.3 formatter 排除 + BDD-9 用 rg -l 单文件判定）
- [x] 读既有测试文件（p5-count/check-gate/render/debt-check）+ helpers
- [x] 读被测脚本现状（count.py/check-gate.sh L249-259/render.sh/check-debt.sh）
- [x] 读 C8 表三文件 + dispatch-protocol.md L105-135 + 模板
- [x] 现状实测：BDD-9 rg -l 仅模板单文件；BDD-15 4 处命中（check-debt:26 非跳过语义 + baseline 3 处跳过）；BDD-1 backend 行现无 plan-eng-review
- [x] 现状实测：GPC 现状输出（P5+P5_unit+P5_e2e=3、P5+P5_formatter=2）；render architect/design-review 均含 Review 指令；README 计数表 + count-tests.sh
- [x] 规划：14 条新增/修改测试，BDD 1:1 映射，含 4 条文档断言 + 脚本断言
- [x] 写 P3-test-cases.md（16 BDD 1:1 映射，test_code_dir 声明，断言类型标注）
- [x] 测试代码落盘：p5-count（GPC.1/2 改 + GPC.3 新）、check-gate（G5_CMD.1/5 改 + BDD-1/2/9/12/13/14/15 新）、render（RP.17/18/19 新）、debt-check（BDD-16 新）
- [x] 自跑确认：红灯 11 个（GPC.1/2/3、G5_CMD.1/5、RP.18、BDD-1/12/13/15、BDD-16），失败原因均为被测对象未修；回归锁绿（RP.17/19、BDD-2/9/14、G5_CMD.2、G5.1）
- [x] count-tests.sh：agate-gate-p5-count 3 / check-gate 124 / render 20 / debt-check 21（无漂移告警，总计 720）
