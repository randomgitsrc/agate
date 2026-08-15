# P4-progress — TAG0011（测试框架迁移阶段二）

## 批次完成情况（0-18 全部完成）

| 批次 | 内容 | 用例 | commit |
|------|------|------|--------|
| 0 | pytest 基座（conftest + sanity 6 + workspace-resolve 10 + pyproject markers） | 16 | 批次0 |
| 1 | 纯工具 5 文件 + helpers-python 3 + 流语义回归锁 | 15 | 批次1 |
| 2 | 共享工具（json-get/md-field/state-get 等） | 39 | 批次2 |
| 3 | 内容生成（next-card sha256 字节稳定性） | 53 | 批次3 |
| 4 | 上下文/归档/回退工具 | 37 | 批次4 |
| 5 | 环境/债务/编码守卫（Pillow skipif） | 42 | 批次5 |
| 6 | check 状态/裁剪/scope | 69 | 批次6 |
| 7 | check 基础 gate 5 文件 | 57 | 批次7 |
| 8a-8i | check-gate 专项（8 子批 + p1-review + p5-diff + 补遗） | 146 | 批次8a-8i |
| 9a-9c | P6 验收链 + vision + backstop | 79 | 批次9a-9c |
| 10a-10b | TDD 红灯链 + formatter + consistency | 60 | 批次10a-10b |
| 11 | 回归套件 6 文件 | 17 | 批次11 |
| 12 | hook 链 4 文件 | 20 | 批次12 |
| 13a-13c | pre-commit hook 专项 + dispatch-card | 56 | 批次13a-13c |
| 14 | 一致性/self-gate 集成 | 19 | 批次14 |
| 15 | env-adapt-docs + 表 E 文档重写 | 9 | 批次15 |
| 16 | 扫描器行为 | 16 | 批次16 |
| 17 | 退役 check-windows-smoke + count-tests 改写 | — | 批次17 |
| 18 | bats 退役删档（60 .bats + helpers 3） | — | 批次18 |

**最终状态**：pytest 750 collected（748 passed + 2 skipped）；count-tests.sh 改写 pytest 收集（750）；windows_smoke marker 78 用例；bats 全部退役删除；helpers/ 删除（conftest 替代）。

## 关键实现点

- 合并流语义（$output = stdout+stderr → CommandResult.output）全树落实
- subagent 卡死处理：check-tdd-red（43 用例）/ pre-commit-hook（48）空返回 → "只写代码不跑测试"策略 + 拆小（13a/13b/13c）成功
- 批验证发现并修复：pre-commit-hook task_dir mkdir 顺序（12 处）、test_check_tdd_red_formatter 注释 R4 字面、check-gate 4 用例补遗（PG.P2REVIEW/bdd-14/28/29）
