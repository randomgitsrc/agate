# P4-progress — implementer batch 0

- [x] 读 dispatch-context（批次 0 范围：agate_common.py + ci-gate-backstop.py resolve_tasks_dir + 3 bats + P4-implementation.md）
- [x] 读 implementer.md 角色定义 + AGENTS.md 约定
- [x] 读 P2-design.md §3.1/§3.2/§3.6、P3-test-cases.md、P0-brief.md
- [x] 全读 gate-result.sh（write_gate_result/read_state_phase/read_state_task_id/has_staged_phase_change/has_staged_phase_output/resolve_formatter/run_test_with_formatter）
- [x] 全读 agate-workspace-resolve.sh（resolve_workspace 迁移源）
- [x] 读 ci-gate-backstop.py resolve_tasks_dir（L88-104 改造点）
- [x] 读 agate-state-get.py（pyyaml fail-closed 模式 L17-21）
- [x] 读 fixtures.bash（$PYTHON detect_python）
- [x] 读 3 个 bats（agate-workspace-resolve 10 / helpers-python 3 / ci-gate-backstop 11）
- [x] 全读 3 个 bats（agate-workspace-resolve 10 / helpers-python 3 / ci-gate-backstop 11）
- [x] 读 check-tdd-red.bats 超时用例 + fixtures.bash + scanner 规则
- [x] 调研 callers：write_gate_result/read_state_phase 等被 pre-commit-gate.sh/check-tdd-red.sh/agate-capture-env-baseline.sh 使用（批次 0 只建库，不改它们）
- [ ] 建 agate_common.py
- [ ] 改 ci-gate-backstop.py resolve_tasks_dir
- [ ] 改 3 个 bats
- [ ] 更新 P4-implementation.md
- [ ] 自跑 3 个 bats 自查
- [x] 建 agate/scripts/agate_common.py（数据流 7 函数 + resolve_workspace + 3 hook 工具 + 执行模式 main）
- [x] 改 ci-gate-backstop.py resolve_tasks_dir → agate_common.resolve_workspace（try/except ImportError 向后兼容）
- [x] 改 agate-workspace-resolve.bats（10 处调用改 py）
- [x] 改 helpers-python.bats（bdd-17 重构为 probe_python 探测+失败回退）
- [x] 自查：3 个 bats 全绿（10/3/11）+ 全量 unit 625 绿 + count-tests 727 不漂移 + consistency 0 ERROR + encoding guard 通过
- [ ] 更新 P4-implementation.md
- [x] 更新 P4-implementation.md（含 implementation_dir 声明 + DESIGN_GAP + 自查结果）
- [x] 最终自查：grep 确认 resolve_workspace/write_gate_result/probe_python 落盘、ci-gate-backstop 改调、bats 调用改 py
- [x] 批次 0 完成（ci-gate-backstop.bats 断言本就全绿无需改动，其余 2 个 bats 已改）

## 批次 1a（implementer）

- [x] 读 dispatch-context batch1a（4 脚本范围 + 迁移规则 + bats 调用点改造）
- [x] 读 P2 §3.2 批次 1 + §3.5 锚点同步 + 参考 agate_common.py / agate-state-get.py
- [x] 全读 4 个 .sh 迁移源 + 依赖 py（agate-changelog-unreleased / agate-frontmatter-check / agate-state-yaml-check / agate-md-field-get）
- [x] 读 4 个 bats + dispatch-context-warning / consistency / pre-commit-hook 引用核查
- [x] 新建 4 个 .py（check-changelog / check-frontmatter / check-state-yaml / check-scope-resolved）
- [x] 改 4 个 bats 调用点（.sh → $PYTHON .py），@test 数不变
- [x] 自查：8/14/9/10 全绿；consistency 0 ERROR；py_compile 通过；sh/py 输出逐字节等价（含 post-bump / AGATE_CARD 剥离边界）
- [x] 更新 P4-implementation.md 批次 1a 节（含 1 条 DESIGN_GAP：$(...) 尾部换行剥离语义）
- [x] 自查完成返回
