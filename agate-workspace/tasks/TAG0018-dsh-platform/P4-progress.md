# TAG0018 P4 进度（implementer）

## 步骤记录

1. **角色定义**（`agate/assets/execution-roles/implementer.md`）：P4 严守约束实现；最小实现原则；测试不通过决策树；DESIGN_GAP/SCOPE_GAP/CLARIFY 标注纪律；分阶段落盘默认启用。
2. **派发上下文**（`P4-dispatch-context-implementer.md`）：六交付物目标 + 硬约束（不发明新结构 / 身份薄协议厚 / 测试平台无关 / 吸收 P2-review 建议 / SELF-GATE 触发面）+ P2 gate_commands 固化不可改。
3. **P1 需求**：19 条 BDD 权威基线；I-1~I-12 隐含需求；SELF-GATE 触发面（SETUP.md/platform-notes.md/SKILL.md，tests 不触发）。
4. **P2 设计**：六交付物设计 + D-1~D-5 决策（D-1 h3 置于步骤 2 区内；D-2 移除「待实机验证」字样 → 已实机验证 + v0.1.0-rc.8 版本敏感提示；D-3 闭合括号标题；D-4 preset 最小元数据；D-5 双份映射统一口径）；M-4 行号（Windows 区 L111-143、步骤 3 L144）；M-7 tests/README.md 补行。
5. **P2-review**：approved + 7 条非阻塞建议；建议 1/2 已由 P3 吸收为用例 3/7/8；建议 3 行号精度（P4 以实际行号为准）；建议 5 花括号简写 → 三条独立 ln 行；建议 6 基线 WARNING 数（0 ERROR / 335 WARNING）。
6. **P3 测试设计**：8 用例全红（B 类实现缺失）；用例 6/7/8 章节切片断言；命令串与 BDD-8 字面一致。
7. **参考实现**（agate-copy，非权威蓝本）：agent.cordis.yml（含 tool-fs-search 修复）/ preset.yml / SKILL.md / SETUP.md 与 platform-notes.md 的 DSH 章节草稿——结构照抄、措辞按 D-2/D-3 修正。
8. **worktree 现状核实**：`agate/tests/unit/test_dsh_preset.py` 已在位（P3 提交，不修改）；scripts/ 仅 install-hook.py 等、全仓 grep 无 install-dsh.py（BDD-9 后半复证）；orchestrator-template.md 首行标题「# Orchestrator（agate 编排 Agent）」确认为 BDD-3 verbatim 判据锚点。
9. **实现落位**（6 交付物 + 1 顺手项）：
   - `agate/assets/templates/dsh/agent.cordis.yml`：persona 薄身份 + 工具行；tool-fs-search 含 `config.sampleOverCapGlobResults: false`；delegation group/isolate 语法对齐 standard preset；移除草稿字样（D-2）。
   - `agate/assets/templates/dsh/preset.yml`：name: agate 编排者 / description / order: 1（最小集，D-4）。
   - `agate/assets/templates/dsh/SKILL.md`：frontmatter name: agate-protocol；四项职责×DSH 工具表 + 4 食谱 + 平台注意四要素。
   - `agate/SETUP.md`：步骤 2 区内新增「### 步骤 2-DSH」h3（L144，Windows 小节后、步骤 3 L173 前）；命令块 = BDD-8 精确命令串 + install-hook.py 调用（BDD-9）；身份薄协议厚 + 升级行为（BDD-10）；使用指引（BDD-11）；版本敏感提示（D-2）。
   - `agate/platform-notes.md`：末尾追加「## DSH（deepseek-harness）」h2 条目（L174，D-3 闭合括号）；六行能力差异表（设计 §3 交付物 5，未扩 7 行）；两条已知注意；互链 SETUP.md「步骤 2-DSH」（BDD-14）。
   - `agate/tests/README.md`：映射表补「DSH 平台模板结构（TAG0018）| unit/test_dsh_preset.py | 8」（M-7，非 gate 强制）。
10. **测试**：单文件 `python3 -m pytest agate/tests/unit/test_dsh_preset.py` = **8/8 passed**（0.04s）；全量 unit 套件跑批中。
