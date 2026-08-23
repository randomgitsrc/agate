# P3-progress — TAG0023-mechanism-checks (test-designer)

## 读取记录

1. [DONE] P3-dispatch-context-test-designer.md — 核心指令：13条BDD映射、批次组织(A/B/C/D)、BDD-1 WARNING降级+负面锚点、BDD-8文档四要素、BDD-9占位声明、BDD-7当前应为红灯（roadmap.md未补记RM-AG0032 done）
2. [DONE] test-designer.md 角色定义 — TDD认知模式、分阶段落盘要求、退出契约
3. [DONE] P1-requirements.md 全文 — BDD-1..13 原文、§4三组同类扫描结论、§5范围声明D1-D5决策、frontmatter risk_level:high / packages:[agate] / domains:[backend]
4. [DONE] P2-design.md 全文 — §4 完成标准表逐条判据(BDD-1..13)、§5 files_to_read 5批分组、dispatch_plan(batch A-E)、BDD-1正则(D6收紧后13/21匹配含review-eng/review-cso)+负面样本2个(implementer-review-fix / consistency-reviewer)、BDD-9连续5次CI(P6覆盖非P3)、BDD-7当前FAIL(roadmap.md未补记)、ENV-SENSITIVE-TESTS.md路径与登记字段
5. [DONE] P2-review.md — status: approved (round 3)，D6正则最终结论确认(13/21匹配，2假阳性排除)，非阻塞发现①②不影响本轮测试设计（qa/investigate/protocol-alignment-review 均未收录进枚举，不需要为其写正负样本）
6. [DONE] check-state-transition.py 全文(181行) — main()流程：仅当 .state.yaml 在 staged diff 中才继续；get_old_phase()用git show HEAD:path；_run_state_get 调 agate-state-get.py子进程；现有检查1(回退>=2)/检查2(retries超限)/检查4(stale outputs)；新函数需在main()内新增调用点，输出走stderr，WARNING不应exit非0
7. [DONE] test_check_state_transition.py 全文(481行,30用例st_1..ws_4) — 命名规范test_st_N_描述；用_write_state()+git_repo.commit/stage+_run_state()；result.output为stdout+stderr合并流；助手函数模式确认，新增测试将复用_write_state/_run_state helper
8. [DONE] check-debt.py 全文(135行) — _retreat_coverage() L75 `short = full[:7]`固定切片是BDD-8根因；main()覆盖两种模式(FILE schema / --retreat-coverage)
9. [DONE] test_agate_debt_check.py 全文(605行) — 已有 test_bdd_1..20 命名（另一个历史任务的BDD编号，非TAG0023），确认collision规则：完整函数名（含描述性后缀）不同即不冲突；test_bdd_14/15(retreat coverage) 用 git_repo + git commit "retreat: ..." + tech-debt.md fixture 构造覆盖/未覆盖场景，_run_check_debt_retreat helper模式；决定TAG0023 BDD-8/9/10测试函数用 test_bdd_8_env_sensitive_.../test_bdd_9_.../test_bdd_10_... 描述性后缀避免歧义
10. [DONE] check-gate.py gate_p8() 全文读取 — 确认现状：无任何 roadmap.md 读取；gate_p8 只有 return 1(缺bump_type/debt_check) 或最终 return 2(WARNING+继续)，从不 return 0 — BDD-6判据按P2-design §4完成标准表用 return 2（非P1原文exit 0），已按该表设计断言
11. [DONE] agate-frontmatter-check.py 全文 — 现状错误消息：缺字段="缺必填字段X"(无"补")/非法值="非法值...(合法值:...)"(无"改用")/类型错误已含"应为"/深度超限 — BDD-12测试挑"补"/"改用"两个当前缺失的关键词做红灯断言
12. [DONE] check-routing.py + check-pruning.py 走查(_staged_source_count/score_task) — 确认BDD-13的3类历史错误检测机制(coupling_checklist类型/FIND-5全角冒号/源码数>5)均已在现状代码实现(非新增)，测试作为回归防呆锚点可能已是绿灯，已在P3-test-cases.md/测试docstring中如实标注
13. [DONE] roadmap.md 核实 RM-AG0032 当前两行(L30 backlog/L31 scheduled)均非done — BDD-7测试基于此构造真红灯
14. [WRITE] 测试代码已写入6个文件：
    - agate/tests/unit/test_check_state_transition.py（追加，BDD-1~4，10个测试函数）
    - agate/tests/unit/test_check_gate.py（追加，BDD-5~7，3个测试函数）
    - agate/tests/unit/test_agate_debt_check.py（追加，BDD-8，1个测试函数+BDD-9占位声明注释）
    - agate/tests/unit/test_env_sensitive_tests_registry.py（新建，BDD-10，1个测试函数）
    - agate/tests/unit/test_check_frontmatter.py（追加，BDD-12~13前两类，4个测试函数）
    - agate/tests/unit/test_check_routing.py（追加，BDD-13第三类，1个测试函数）
    - agate/tests/unit/test_agate_render_dispatch_prompt.py（追加，BDD-11，1个测试函数）
15. [FIX] test_agate_render_dispatch_prompt.py BDD-11测试初版触发既有 test_bdd_5_all_test_py_text_io_explicit_encoding 假阳性（.read_text(\n encoding="utf-8"\n) 跨行写法被行级正则误判缺 encoding）；改为单行 tmpl_path.read_text(encoding="utf-8") 后修复，验证不再破坏该既有测试
16. [VERIFY] 全量 pytest 复跑两次确认：目标7个改动文件独立跑 = 10 failed/285 passed（干净basetemp，无teardown噪音error）；全量 agate/tests/ 跑 = 10 failed/1224 passed/2 skipped，与改动前基线对比仅新增这10个失败，无其他既有用例受影响
17. [DONE] 全部核实完成，进入写 P3-test-cases.md 步骤
18. [DONE] P3-test-cases.md 已写入（含 test_code_dir 声明、13条BDD映射表、实测pytest结果、BDD-9/6/13/4等特殊情况如实说明）。自检：13条BDD全覆盖(BDD-9占位)/真红灯10个(B类断言失败非A类语法错误)/全量回归1224 passed无既有测试受损。任务完成。
