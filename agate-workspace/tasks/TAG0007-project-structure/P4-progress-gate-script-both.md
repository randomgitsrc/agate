[P4-progress] 已读取 dispatch-context / implementer.md / check-gate.py(gate_p2/p4/p7) / test_check_gate.py(2400-2624) / conftest.py 相关 fixture。
[P4-progress] gate_p2 分支已实现：project_phase==bootstrap 时检查 P2-skeleton.md 是否存在且含 "## 骨架声明"，缺失 return 1（stderr 含 P2-skeleton.md）；非 bootstrap 完全跳过，插入位置在 ui_design_section 检查之后、最终 return 2 之前。
[P4-progress] gate_p4 分支已实现：暂存区含代码文件时新增 OR 条件判定（P2-skeleton.md 存在 或 {AGATE_WORKSPACE}/agents/CODE-MAP.md 存在）且 P4-implementation.md 缺少 "## 新增文件核对表" → WARNING（stderr 含 WARNING + 新增文件核对表），仍 return 0 不阻断；不读取 change_type 字段。CODE-MAP.md 路径解析已标 [DESIGN_GAP]（task_dir 向上两级推导 workspace 根）。
[P4-progress] gate_p7 分支已实现：用 _frontmatter_field 本地读取 code_map_new_files_count/code_map_reviewed_count（原计划用 _md_field_get，因 agate-md-field-get.py KNOWN_OPS 未注册这两字段且该文件不在本批次改动范围内，改用本地纯函数，已标 [DESIGN_GAP]）。两字段均缺失→跳过；内部一致性层 reviewed<new→return 1；转抄核对层 P4 实际标记数>new_files_count→return 1；不读 change_type。
[P4-progress] 自跑测试：12 个新增测试全部 PASSED；test_check_gate.py 全量 159 passed（无回归）；agate/tests/unit 全量 gate 相关 898 passed, 2 skipped（既有 skip 与本次改动无关）。
[P4-progress] git status --porcelain agate/scripts/ 仅显示 check-gate.py 一个文件改动，符合硬约束。
