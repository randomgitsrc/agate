## $(date -u +%Y-%m-%dT%H:%M:%SZ) 步骤记录
- 已读 dispatch-context / implementer.md / test_self_gate_naming_docs.py
- SELF-GATE.md（根目录）3 处命名模板已改：
  - L53-54 文件约定表：留痕文件 -> docs/reviews/agate-alignment-{date}-{task_id}-{NN}.progress.md；成果文件 -> docs/reviews/agate-alignment-review-{date}-{task_id}.md
  - 变更触发模式模板（原L133/143）：同步改为含 {task_id}
  - 全量审查模式模板（原L183/193）：同步改为含 {task_id}
- protocol-alignment-review.md 新增「Write 前检查：写入前防误覆盖（BDD-8）」段落（人工验收清单前），含"Write 前"/"目标路径"关键词，区分"同一任务复核轮可覆盖" vs "别的任务遗留不可覆盖"两分支；同步顺手把人工验收清单最后一条的成果文件路径示例改为含 {task_id} 的新模板（与 SELF-GATE.md 改动保持一致，不属于范围外新增逻辑，只是同一文件内的示例文本对齐）。
- 自测：python3 -m pytest agate/tests/unit/test_self_gate_naming_docs.py -q -> 8 passed
- 未修改测试文件 test_self_gate_naming_docs.py（已核实 git status）
- [PROD_NOT_TOUCHED]
