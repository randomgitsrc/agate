## P2 architect progress
- 已读 dispatch-context（设计选型点 6 处、输入文件清单、约束）
- 已读 architect 角色定义（frontmatter 四字段、files_to_read、minimal_validation、SCOPE+ 规范）
- 已读 P0-brief（4 处缺陷 + 强制同类扫描 + env_constraints）
- 已读 P1-requirements.md（16 BDD + I1-I14 + 同类扫描结论：静默exit0 4处/注入1处/P5计数2处）
- 已读 agate-gate-p5-count.py（L19 正则 ^  (P5\w*): 合并计数）
- 已读 agate-render-dispatch-prompt.sh（L63-69 ROLE_DIR 判定 / L78 main_block / L128-142 sed 替换）
- 已读 check-debt.sh（L21-30 --retreat-coverage 依赖加载：两分支都 exit 0；L26 source 失败静默 exit 0）
- 已读 check-gate.sh（P2 L137-211 无条件要求 P2-review.md；P5 L249-259 多命令 WARNING 消费 L253-258）
- 已读 dispatch-prompt.md 模板（L9-13 Review 指令节，main_block 边界=L1 到 "## 阶段特定提示"）
- 已读 role-system.md（C8 表 L54-61：backend 任意 → review(P4后)）
- 已读 review-mapping.md（C8 表 L15-23）
- 已读 phase-cards/P2-design.md（C8 表 L93-97：frontend→plan-design-review / high→plan-eng-review / NEED_CONFIRM→plan-ceo-review）
- 已读 dispatch-protocol.md 空返回恢复策略 L105-135 + 内联模板 L427-494（无 Review 指令节）
- 已读 render bats（RP.1-16 + bdd-20 = 17 @test）；README L33 render=16（现有 1 漂移）
- 已读 check-gate.bats G5.1/G5_CMD.1-5（旧文案断言）；agate-gate-p5-count.bats GPC.1/2；count-tests.sh L22 陈旧引用（P1 排除范围）
- 最小验证：count.py 合并计数输出 3/1（bug 确认）；render 执行/评审角色均注入 Review 指令（bug 确认）；render 不存在角色 exit 2 + stderr（已修复）；check-debt 缺 resolve 脚本 exit 0（bug 确认）
- check-debt.sh --retreat-coverage 无脚本调用方（仅 agate-retreat-to.sh:72 注释 + 文档提及）→ exit 0→2 无 hook 波及
- 设计定案：RM-AG0010=backend→plan-eng-review(P2)+去重说明；RM-AG0011=count.py 输出 "主 辅" 空格分隔；RM-AG0012①=模板拆分独立块 + render 按 ROLE_DIR 追加；RM-AG0012②=RP.17 回归；RM-AG0003=自动重试一次(不占槽位)+<1min 告警；BDD-16=exit 2
- P2-design.md 已产出并自检：candidate_count=12（6 修复 × 2 候选）、四字段齐全、16 BDD 全覆盖、无行首 PASS/FAIL
## plan-eng-review 进度

- [x] 读取 dispatch-context / 角色定义 / AGENTS.md
- [x] 读取 P2-design.md（12 候选方案、6 处修复）
- [x] 读取 P1-requirements.md（16 BDD）
- [x] 读取 P0-brief.md（env_constraints / known_risks）

下一步：核验代码级事实（C8 表、count.py、check-gate.sh、render 脚本、check-debt.sh、dispatch-protocol.md、bats 断言）

- [x] 核验 role-system.md L50-68 / review-mapping.md L15-23 / P2-design.md 卡片 L93-97 三处 C8 表：backend 行现状均为 review（P4 后），设计补 plan-eng-review（P2）成立
- [x] 核验 count.py L19 合并计数 / check-gate.sh L253-258 消费点 / read-p5-commands.py L26-30 _formatter 排除：设计事实准确
- [x] 核验 GPC.1(3)/GPC.2(0)、G5_CMD.1/5(2 个文案)、G5.1、G5_CMD.2/3/4 断言：设计断言同步清单与代码现状一致
- [x] 核验 render 脚本 L63-69 ROLE_DIR / L78 main_block / L74-76 extract / L83 sed 惯用式：方案 A 复用既有机制成立
- [x] 核验 dispatch-protocol.md L105-135 空返回节 / L124 禁止段 / L128 弱信号：RM-AG0003 改写目标准确
- [x] 核验 check-debt.sh L24-30 / L35-37 + 无脚本调用方（grep 证实仅注释/文档/tests）
- [x] 核验 BDD-9 守卫：修复后 rg 命中 dispatch-prompt.md 2 处（节标题+代码块），设计已注明单文件语义
- [x] 核验 self-host 声明：backend+cli/medium → 新规则映射 plan-eng-review，与本派发一致

非阻塞发现：scripts/README.md L23「回退模式恒 0」文档漂移未纳入 §2.6；RP/GPC 缺 formatter 排除的回归测试（仅同步不改断言）；BDD-9 建议 P6 用 rg -l 单文件判定；files_to_read 缺 state-machine.md retry 节
