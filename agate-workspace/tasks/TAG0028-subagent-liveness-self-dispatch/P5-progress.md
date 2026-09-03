# P5 progress — TAG0028 verifier（技术验证）

- [x] 读 P5-dispatch-context-verifier.md（目标/约束/输入文件，5 key + timeout 档位确认）
- [x] 读 verifier.md 模式一（P5 技术验证角色定义）
- [x] 读 AGENTS.md（双工作区纪律：consistency 必须用 worktree 自己的）
- [x] 读 P0-brief.md（env_constraints：SELF-GATE / 系统 python3 / fixture 脱敏）
- [x] 读 P2-design.md §4 gate_commands（命令权威来源，与 dispatch-context 一致）
- [x] 读 P4-implementation.md（实现声明：三脚本 + 协议改写，验证对象）
- [x] P5 全量 pytest（900s timeout）：exit=1，1 failed / 1433 passed / 2 skipped（43.64s）
  → FAILED agate/tests/scripts/test_check_platform_assumptions.py::test_bdd_8_clean_tree_zero_detection
  → 根因：TAG0028 新增 3 测试文件 fixture 数据串含裸 python3（17 处 R2 命中：adapters 13 / detect 3 / ir 1），
    破坏 TAG0011 旧测试 bdd-8「tests 树 0 命中」不变量 → 本任务引入回归，非预存失败
- [x] P5_consistency（180s）：exit=0，329 WARNING 基线 / 0 ERROR
- [x] P5_cmdstream_verify（180s）：exit=0，9 场景全 PASS（签名行「全部断言通过——命令流日志可机械区分九种状态」）
- [x] P5_shellcheck（180s）：exit=0，0 输出（无 warning 级及以上）
- [x] P5_count_tests（180s）：exit=0，1436 用例 ≥ 749 基线
- [x] 写 P5-test-results/unit.md + fail-list.txt

## P5 重跑 round 2（fix3 已提交 34366ab）
- [ ] P5 全量 pytest（900s 兜底，后台 job）— 执行中
- [ ] P5_consistency（180s）— 待执行
- [ ] P5_cmdstream_verify（180s）— 待执行
- [ ] P5_shellcheck（180s）— 待执行
- [ ] P5_count_tests（180s）— 待执行
- [ ] 覆盖写 P5-test-results/unit.md（round 2）+ fail-list.txt
- [x] P5_consistency（180s）：exit=0
- [x] P5_cmdstream_verify（180s）：exit=0
- [x] P5_shellcheck（180s）：exit=0
- [x] P5_count_tests（180s）：exit=0，1436 ≥ 749
- [x] P5 全量 pytest（900s 兜底）：exit=0，1434 passed / 2 skipped（41.31s），0 FAILED
- [ ] 覆盖写 P5-test-results/unit.md（round 2）+ fail-list.txt
- [x] 覆盖写 P5-test-results/unit.md（round 2，HEAD=34366ab）+ fail-list.txt（空，无失败）
- [x] 验证：unit.md 含行首签名（passed 1434 / failed 0），fail-list.txt 0 字节
- [x] round 2 全部 5 key 通过（P5 全量 pytest exit 0 / 0 failed）
