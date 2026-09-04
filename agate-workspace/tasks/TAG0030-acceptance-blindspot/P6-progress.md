# P6-progress — TAG0030 验收（verifier）

> 本文件为 P6 验收分阶段落盘记录。**不含行首 `- PASS`/`- FAIL`**（provenance 审计 2 拦截）。
> 验收结论以 `P6-acceptance.md` 为准。

## 输入读取（2026-09-04）

- [x] `agate/assets/execution-roles/verifier.md`（P6 模式：先验证后结论、证据路径必引、自查≠gate）
- [x] `P6-dispatch-context-verifier.md`（目标/约束/上游关联；21 条 BDD 全量验收）
- [x] `P0-brief.md`（环境隔离 `[PROD_NOT_TOUCHED]`）
- [x] `P1-requirements.md`（BDD-1~21 验收唯一基准，`#### BDD-NN` 标题 21 个已核对）
- [x] `P2-design.md`（§2 锚词 + §9 完成标志）
- [x] `P5-test-results/unit.md`（断言审计 21/21 全绿；unit 片 1 预存 flaky 登记 known-failures）
- [x] `agate/tests/unit/test_tag0030_assertions.py`（21 用例逐 BDD 对应已核对）
- [x] `check-p6-format.py` / `check-p6-evidence.py` / `check-p6-provenance.py` / `check-gate.py`（P6 判定语义）
- [x] worktree 根 `AGENTS.md`（BDD-20 载体：全量扫描/新增 CHECK）

## 客观验证记录（2026-09-04）

- 断言审计：`timeout 240s python3 -m pytest agate/tests/unit/test_tag0030_assertions.py -q --tb=short`
  → `21 passed in 0.03s`（输出落盘 P6-evidence/assert-full.log，尾行 EXIT_CODE: 0）
- 锚词 grep：21 个 BDD 对应协议文件锚词全部命中（无 no-match），逐 BDD 快照落盘
  `P6-evidence/bdd-NN-anchor.txt`（含目标文件 + grep 命令 + 命中行）
- consistency：`timeout 180s python3 agate/scripts/check-protocol-consistency.py --strict-errors-only`
  → exit 0，0 ERROR（329 WARNING 存量），输出落盘 P6-evidence/consistency.log（尾行 EXIT_CODE: 0）
- count-tests：`timeout 120s bash agate/tests/scripts/count-tests.sh`
  → exit 0，总计 1457 个测试用例（基线 1436 +21），落盘 P6-evidence/count-tests.log（尾行 EXIT_CODE: 0）

## 自查预检（自查≠gate，判定权在主 Agent）

- `check-p6-format.py --check P6-acceptance.md` → exit 0
- `check-p6-evidence.py $TASK` → exit 0（21 条 BDD，证据目录非空）
- `check-p6-provenance.py $TASK` → exit 2（唯一 WARNING：P3-test-cases.md 缺 agent 字段，
  系 P3 阶段既有产出 commit 167a044，协作规范不阻塞；审计 1/2/3/5/7 全部通过）
- `check-gate.py P6 $TASK` → exit 2（通过码：P6_TOTAL=21，FAIL=0）

## 环境隔离声明

验收全程只读 worktree `agate/` 协议文件 + 跑测试/grep，未改动任何协议文件，
未触碰生产环境。`[PROD_NOT_TOUCHED]`

## 产出

- P6-acceptance.md（21 条 BDD 验收结果，frontmatter pass=21/fail=0/ui_affected=false）
- P6-evidence/（21 个 bdd-NN-anchor.txt + assert-full.log + consistency.log + count-tests.log）
