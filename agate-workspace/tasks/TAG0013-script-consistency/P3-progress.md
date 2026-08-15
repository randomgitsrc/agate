# P3 progress (test-designer)

- [x] 读取 dispatch-context 派发指引（目标/约束/输入文件）
- [x] 读取 test-designer.md 角色定义
- [x] 读取 P0-brief.md（env_constraints / 风险）
- [x] 读取 P1-requirements.md（11 条 BDD、豁免清单 5 类、扫描范围、self-gate 触发面表）
- [x] 读取 P2-design.md（候选 A：check_script_name_refs + SCRIPT_REF_RE + PROTOCOL_DIRS 扩展 + main() split 修复；self-gate 精确名锚定；复盘提醒行；测试策略）
- [x] 读取 P2-review.md（approved；缺口 8 建议：优先 _check_status helper 或端到端跑 main() 避免假绿）
- [x] 读取三个现有测试文件 + conftest.py（_load_cpc importlib 模式 / _run_csg helper / _run_retro helper / git_repo/task_dir/py_path fixtures）
- [x] 读取三个被测脚本（check-protocol-consistency.py / commit-msg-self-gate.py / check-retrospective.py）——确认 CHECK 10 函数/常量、README|AGENTS 分支、DEBT/roadmap 提醒行均未实现
- [x] 读取 check-tdd-red.py + agate_common.py + agate-read-gate-commands.py（formatter 解析路径）
- [ ] 设计用例并写测试代码
- [x] 写测试代码（追加 3 个文件：CPC +13、self-gate +4、retro +2 = 19 用例）
- [x] 自跑新增测试：16 红 / 3 绿锁，全量套件 16 failed, 752 passed, 2 skipped（66s）
- [x] 红灯原因核验：AttributeError(组件未导出) / AssertionError(CHECKS/PROTOCOL_DIRS 未注册、main() BLOCKER-1 未修、正则未扩展、提醒行未实现) — 全部为被测模块未实现，无断言与数据矛盾
- [x] check-tdd-red.py → exit 0（真红灯可推进）
- [x] ruff 3 个测试文件通过；git diff 仅 3 个测试文件 + P3 产出，未改被测脚本
- [x] P3-test-cases.md 含 test_code_dir + BDD 1:1 映射 + 夹具选型
