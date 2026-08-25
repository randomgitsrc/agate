# P4 implementer progress — md-field-set-tool batch

- [读完] dispatch-context / implementer.md / P2-design.md §1-8 / P3-test-cases.md / test_agate_md_field_set.py（534行，35测试项）
- [读完] check-routing.py:29-63（_load_script importlib 模式）/ agate-md-field-get.py（字段分类常量全表）/ agate-frontmatter-check.py（SCHEMAS + _check）
- [读完] agate_common.py:637-796（read_rules_yaml/resolve_rules_root/known_phase_ids/is_legal_gate_key/split_frontmatter/parse_gate_commands_block）
- [读完] check-gate.py:759-813（gate_p2 status/agent 判定）、177-190（_git）；check-judge-verdict.py:50-65（_VALID_STATUS）
- [读完] phases.yaml 全文（task_fields 并集来源）；dispatch-prompt.md/dispatch-context.md 模板全文；role-system.md:37-74（review-roles 清单）；design-md-field-set.md §5（CLI 形态/错误信息格式/边界行为）
- [读完] check-frontmatter.py（BDD-14 验收锚调用方式确认：env FILE 传参）
- [设计确定] key 白名单检查顺序：证据字段 → 追加/嵌套字段 → 全局 writable（_writable_keys 含 agent，调用处减去 agent）；status 走独立分支（枚举校验在前，角色校验在后，仅当值非 draft 时触发）
- [设计确定] --list / 剩余缺失 走 "basename → phases.yaml outputs.file 反查阶段" 方式确定 task_fields，与写入合法性检查（全局 union）分离，对齐 BDD-5/6/16 与 BDD-17 的不同断言口径
- [设计确定] value 强类型转换（int/bool/list）在调用 _check() 之前完成，保证 BDD-15 的错误字符串逐字节匹配
- [开始实现] agate-md-field-set.py / agate-md-field-set-gate-commands.py
- [完成] agate-md-field-set.py 写完，首轮自跑 33/35 通过（BDD-16/19 红）
- [完成] BDD-19 修复：改 dispatch-prompt.md（去掉可复制 frontmatter 围栏，改一行式 set 指引）+ dispatch-context.md（追加"产出文件字段"节）→ 复跑转绿，34/35
- [诊断] BDD-16 复跑仍红：`gate_result.returncode == 1`，stderr "GATE P2: P2-design.md 有 ≥2 候选方案但缺权衡或选择理由描述"（check-gate.py:815-820 has_keyword 检查）。
  用独立脚本复现 task_dir(phases=["P1","P2"]) 生成的 P2-design.md 原始内容 = "---\nagent: test\n---\n\n"（空正文，无"权衡"/"选择理由"关键词）。
  BDD-1 测试手写 P2-design.md 时特意包含了"选择理由如下：候选 A 更简单，权衡后选 A"这句话（满足该 nudge）；BDD-16 改用 task_dir 自动 fixture（空正文）+ 逐字段 set 调用，从未写入过任何正文散文内容——
  agate-md-field-set.py 按 P2-design §3 设计只写 frontmatter/gate_commands 块，不生成/篡改正文散文，这是既定设计边界（同源铁律 + "最小实现"均不支持"自动注入权衡文案"这类越权行为）。
  结论：这是 P3-test-cases 对 BDD-16 fixture 数据的遗漏（测试断言"零协议知识 set 调用应能让 gate 通过"，但 gate_p2 还有一个与 task_fields 完全无关的正文关键词 nudge，BDD-16 fixture 没有像 BDD-1 那样手工注入这段文案）——不是本实现的 bug，且不在本 implementer 权限内修改测试文件。标 [DESIGN_GAP] 上报，不改测试、不在 set 工具里加"自动写入权衡文案"这种超出设计范围的功能。
- [完成] 三个受保护文件（agate-frontmatter-check.py / agate-md-field-get.py / check-judge-verdict.py）git diff 确认零改动
- [完成] importlib.util.spec_from_file_location 用法确认（grep 命中于 agate-md-field-set.py:49）
- [最终自跑] 34/35 通过（1 项为 BDD-16 test-fixture 缺陷，已诊断并上报，非实现问题）
