# P7-progress — consistency-reviewer（TAG0019-risk-routing）

- [x] 读角色定义 consistency-reviewer.md + P7-dispatch-context（强制指令）+ P7 卡
- [x] 读 P0-brief / P1-requirements.md（15 BDD、SUGGEST-1/2、NO_NEED_CONFIRM、无 SCOPE+/SCOPE_RESOLVED）
- [x] 读 P2-design.md（方案 B、candidate_count=3、packages、gate_commands P5 四条、P5_platform 7 文件集）
- [x] 读 P3-test-cases.md / P3-progress.md（红灯确认 30 failed 无 A 类测试 bug；无 DESIGN_GAP 声明）
- [x] 读 P4-implementation.md / P4-progress.md / P4-review.md（无 [DESIGN_GAP:] 残留；test_bdd_2/bdd_5 以测试代码缺陷修复闭环；终裁 approved）
- [x] 读 P5-test-results/unit.md（1099 passed / 1 env-premise I1；consistency 0 ERROR；platform 7 文件 0 命中；count-tests 1102）
- [x] 读 P6-acceptance.md + P6-evidence（15 PASS / 0 FAIL；抽查 bdd-10-same-source.log、bdd-15-consistency.log 与 PASS 行一致）
- [x] 读 check-gate.py gate_p7 机器判定口径（frontmatter 计数：blocker/devcrit/dg/cm 两层校验）
- [x] 核验 worktree 实现：check-routing.py（importlib 复用 check-pruning 三函数 + score_task，exit 0/1/2 分支齐）；agate-risk-score.py（score_task/run_git/git_ok/_SENSITIVE_RE/_is_task_artifact/relpath/rstrip）
- [x] CODE-MAP 核对：agents/CODE-MAP.md 存在；P4 声明"[CODE_MAP_EXEMPT: 无 CODE-MAP 机制]"与文件存在不符；新文件未登记 → [CODE_MAP_DRIFT]（WARNING 级）
- [x] 未决项：P1 无行首 [NEED_CONFIRM]；SUGGEST-1 采纳为方案 B（P2 §1.4）、SUGGEST-2 同实现批合并
- [x] 跨文件一致性：P1§BDD 15 ⇔ P6 pass 15 ✓；P2§packages ⇔ P4 交付目录三包全覆盖 ✓；P2§gate_commands ⇔ P5§unit.md 逐条一致 ✓
- [x] **新发现（DEVIATION 非 CRITICAL）**：I9 五处文档同步面仅 2/5 落地——analyst.md / task-files.md / dispatch-protocol.md 三文件 ceremony 说明缺失（case-insensitive grep 0 命中；P2 §0.1 C 表声明修改点未实现；P6 附注仅记 dispatch-protocol.md:931，P7 扩展确认 analyst/task-files 亦缺）→ P8 收尾
- [x] 产出 P7-consistency.md（frontmatter 计数：blocker 0 / deviation 1 / deviation_critical 0 / design_gap 0 / design_gap_reviewed 0 / code_map_new 0 / code_map_reviewed 0）