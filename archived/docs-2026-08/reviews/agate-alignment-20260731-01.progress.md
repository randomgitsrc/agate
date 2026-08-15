- [check-tdd-red.sh] 完全重写：废弃 pytest pattern 解析，改用 formatter+JSON 标准格式。探测链：$TEST_RUNNER→gate_commands.P3→which pytest→exit3。judge_result 按 JSON 字段判定 A/B 类。
- [agate-capture-env-baseline.sh] fail-list 提取改用 formatter+JSON。无 formatter 时放弃捕获（不写文件，exit 0）。缓存 key 含 formatter 集合。
- [gate-result.sh] 新增 resolve_formatter() 和 run_test_with_formatter() 公共函数。formatter 路径解析：绝对路径→task_dir/.agate/formatters→agate_root/assets/formatters。
- [check-gate.sh] P7 DESIGN_GAP 正则从 ^\s*-?\s*\[ 改为 ^\s*>?\s*-?\s*\[ 匹配 blockquote。其余未变。
- [check-p6-evidence.sh] 截图格式从 PNG-only 放宽为任意图片（file 命令检测 MIME，fallback magic number 检测 PNG/JPEG/GIF/WebP）。变量名 PNG_WARNING→SMALL_IMAGE_WARNING。
- [state-machine.md] 删除内联 check-tdd-red.sh bash 代码（~80行），替换为 formatter 契约描述。探测链描述更新含 exit-code-only 退化说明。
- [architect.md] gate_commands 示例增加 P3_formatter/P5_formatter/project_module 键。P3/P5 formatter 说明段。
- [task-files.md] gate_commands 模板增加 formatter 键。P5 门槛描述从"跑 pytest"改为"跑 gate_commands.P5"。
- [dispatch-prompt.md] P6 verifier 脚本从 "Playwright / shell / pytest" 改为 "Playwright / shell / 测试框架"。
- [verifier.md] "非 pytest 技术栈"段改为"技术栈无关"段，指向 formatter。
- [P3-tdd.md] 增加"技术栈无关"段+formatter 选择指引。
- [P5-verification.md] "非 pytest 技术栈"改为"技术栈无关"。fail-list.txt 描述改为 formatter 提取。
- [P0-orchestrator.md] 测试框架自检从 "pytest/vitest" 扩展为 "pytest/vitest/go test/cargo test"。
- [check-protocol-consistency.py] CHECK 9 锚点 check-tdd-red.sh keywords 从 ["pytest"] 改为 ["formatter","pytest"]。
- [tests/README.md] check-tdd-red.sh 用例数从 9 更新为 28，新增 formatters 行 12。
- [formatters/] 6 个新文件：pytest.sh/vitest.sh/go-test.sh/generic-tap.sh/generic-junit-xml.sh/generic-exit-only.sh + README.md 契约文档。
- [hardening-roadmap.md] 新增 v0.26.0 P2.51 条目记录本次改动。
- [test-designer.md] 新增 vitest mock hoisting 反模式说明（T079 教训）。

A1: state-machine.md:274 仍写"不自行解析 pytest 输出"但脚本已改为 formatter+JSON / 结论: MISALIGNED（残留 pytest 硬引用）
A1: state-machine.md:274 仍写"脚本输出 assertion_failures=N, collection_errors=M 格式"但脚本实际输出 TDD_CHECK: 前缀文本 / 结论: MISALIGNED（输出格式描述过时）
A1: dispatch-protocol.md:61 例"P5 subagent 说 failed=0 → 主 Agent 跑 pytest -q" / 结论: MISALIGNED（pytest 软绑定残留）
A1: state-machine.md:188 "P5 的 pytest 全绿兜底" / 结论: MISALIGNED（pytest 软绑定残留）
A1: dispatch-protocol.md:545 "Playwright / shell / pytest" / 结论: MISALIGNED（dispatch-prompt.md 已修但 dispatch-protocol.md 未同步）
A2: 脚本 check-tdd-red.sh 通过 formatter+JSON 实现，state-machine.md 已更新 formatter 契约描述 / 结论: ALIGNED（核心逻辑对齐）
A3a: dispatch-protocol.md:545 pytest 残留——dispatch-prompt.md 已改为"测试框架"但 dispatch-protocol.md 未同步 / 结论: MISALIGNED
A3b: WORKFLOW.md 无残留 pytest 硬绑定（gate 表均用 gate_commands.P5） / 结论: ALIGNED
A3b: orchestrator-template.md:17 permissions 示例含 "pytest*"——是示例值非硬编码 / 结论: NEEDS_HUMAN_REVIEW
A3b: git-integration.md:51 "chore: 升级 pytest" 是 commit message 示例 / 结论: ALIGNED（示例性引用）
A4: bats 全量 503 passed / check-tdd-red.bats 28用例 + formatter 12用例 / 结论: ALIGNED
A5: CHANGELOG 未更新 / 结论: NEEDS_HUMAN_REVIEW
A6: CHECK 9 锚点表已更新 check-tdd-red.sh keywords / 结论: ALIGNED
A7: ADR-003 不绑定技术栈——本次改动正是落实 ADR-003 / 结论: ALIGNED
