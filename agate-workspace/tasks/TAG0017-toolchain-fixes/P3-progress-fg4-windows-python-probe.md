## P3 test-designer fg4-windows-python-probe progress

2026-08-20T10:40:56+08:00 开始：读取 dispatch-context 完成，读取 test-designer.md 完成

2026-08-20T10:43:31+08:00 读取完成：P1-requirements.md（BDD-10/11/12 原文）、P2-design.md（§1.1/2.4/8 minimal_validation）、3 个 hook 薄壳全文（逐字确认探测循环结构一致，L14-15/15-16/15-16）、test_pre_commit_hook.py 全文（style: fixtures git_repo/agate_root/agate_scripts/run_cli/bash/python_exe，run_cli env= 与 os.environ merge 语义）、test_pre_push_hook.py 与 test_commit_msg_self_gate_integration.py 头部（各自 helper 风格）。
手动复现确认当前红灯：构造 fake-bin1/python3（exit 49 broken stub）+ fake-bin2/python（symlink 真实 python3），PATH=fake-bin1:fake-bin2:$PATH 跑 pre-commit-gate.sh（AGATE_ROOT="" 触发自定位到临时 workflow-root），结果 exit=49（未跳过不可执行候选，命中 BDD-10 缺陷）。AGATE_PYTHON 场景同样验证：设置 AGATE_PYTHON=真实python3 但 PATH 只放 broken python3 stub，结果仍 exit=49（AGATE_PYTHON 被忽略，命中 BDD-11 缺陷）。
决定：采用参数化测试覆盖 3 个 hook 薄壳（dispatch-context 明确允许"同一组用例参数化跑三个脚本"），写入 test_pre_commit_hook.py 集中维护，helper 复用 test_agate_root_self_locate_worktree 的 workflow_root 自定位模式（copy hook + resolve-entry.py + agate_common.py + 写 dummy gate.py 打印 marker）。
2026-08-20T10:46:30+08:00 完成：新增 9 个红灯用例（BDD-10 x3 hook + BDD-11 x3 hook + BDD-12 x3 正面断言），另 2 个 BDD-12 负面断言（不含"已实测通过"）当前天然为绿属预期设计。pytest 实跑确认 9 fail/2 pass；全量 collect-only 1013 测试无导入错误，未影响其他并行批次。写入 P3-test-cases-fg4-windows-python-probe.md。自检确认未改动 3 个 hook 薄壳 / platform-notes.md / AGENTS.md 本身，测试与文档中均无"已在 Windows 实测通过"类不实断言。任务完成。
