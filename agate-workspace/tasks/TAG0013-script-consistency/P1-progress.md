## P1 progress (analyst)

- 已读 P0-brief.md：三条 issue 确认（RM-AG0015 CHECK 10 / RM-AG0017 _SELF_GATE_RE 扩展 / RM-AG0018 check-retrospective 提醒行）。known_risks 强制：P1 必须全仓 grep 脚本名引用建影响面表 + grep self-gate 触发面测试。
- 已读 analyst.md 角色定义（隐含需求 5 维度、BDD 反模式清单、NEED_CONFIRM/SUGGEST 用法）。
- 已读 dispatch-context（目标/约束/输入/客观查证信息）。
- 已读 check-protocol-consistency.py（844 行）：
  - PROTOCOL_FILES L52-64 不含 phase-cards/rules；PROTOCOL_DIRS L65 只 agate/assets/
  - REF_RE L238 只匹配 docs|assets|scripts 前缀，裸脚本名漏检
  - CHECK 编号 1,2,3,4,6,7,8,9 → 新检查 = CHECK 10
  - CHECK 9 有 SCRIPT_ALIGNMENT_ANCHORS + check_anchor_coverage 反向兜底
- 已读 commit-msg-self-gate.py：_SELF_GATE_RE L38-40 不含 README.md/AGENTS.md（含 SELF-GATE.md）
- 已读 check-retrospective.py：main() warnings → stderr GATE RETRO 提醒（L89-93），exit 0
- 已读三个测试文件：test_commit_msg_self_gate.py（4 用例，.sh/.py 触发/非 agate 不触发/review 清除，无 README/AGENTS/CHANGELOG 覆盖）、test_check_retrospective.py（10 用例）、test_check_protocol_consistency.py（3 用例，CHECK9 锚点）。
- 影响面 grep 完成：
  - phase-cards/rules 脚本名引用 ≈ 51 处（全部裸名，REF_RE 现行正则匹配不上），当前全部能解析到真实脚本（无 MISSING）——v0.46.0 已修但无 gate。
  - 协议文件集（含 WORKFLOW/dispatch/state-machine/README/AGENTS/SETUP 等）共 ≈314 处脚本名引用。
  - MISSING 的 .sh 名（check-gate.sh 等 27 个）仅出现在 UPGRADING.md（迁移对照表，豁免）+ CHANGELOG（叙事）+ archived（叙事）——需豁免。
  - count-tests.sh 目标在 agate/tests/scripts/ 不在 agate/scripts/ → 若按 agate/scripts 解析会误报，需豁免。
  - formatters（assets/formatters/ 的 pytest.sh/vitest.sh/go-test.sh/generic-exit-only.sh）在 assets/ 下不在 agate/scripts/ → 需豁免。
  - 3 hook 薄壳（pre-commit-gate.sh/commit-msg-self-gate.sh/pre-push-gate.sh）在 phase-cards/P6 与 AGENTS/SETUP 有引用，实际存在 → 豁免锁定。
- self-gate 触发面测试缺口：现有 4 用例无 README.md / AGENTS.md / CHAGNELOG.md 覆盖 → 新增后需补测试。
- 产出 P1-requirements.md：11 条 BDD（连续编号 BDD-1..11）、影响面表（3 类引用 ≈314 处、phase-cards/rules 裸名 ≈51 处、当前 0 漂移）、self-gate 触发面现状表（含测试缺口）、[NO_NEED_CONFIRM]、1 条 SUGGEST。
- 自检通过：文件非空（275 行）、BDD ≥1 连续可判、frontmatter 四字段齐全、无 NEED_CONFIRM 残留。
- [PROD_NOT_TOUCHED]

## requirements-review 进度（P1-review）
- [x] 读 dispatch-context / 角色定义 / P0-brief / P1-requirements
- [x] 读三被测脚本 + 三测试文件（核实客观查证信息）
- [x] 实测：REF_RE L238 只匹配 docs/assets/scripts 前缀 ✓；PROTOCOL_FILES/DIRS 不含 phase-cards/rules ✓；_SELF_GATE_RE L38-40 不含 README/AGENTS ✓；check-retrospective GATE RETRO L89-93 + exit 0 ✓
- [x] 实测影响面：phase-cards/rules 脚本名引用 58 处（表 4.1 P3-tdd 漏 ci-gate-backstop.py ×1）；协议面含 UPGRADING 实测 270（表 4.3 声称 314 不可复现）；formatters/count-tests.sh 路径实测 ✓
- [x] 发现关键 gap：scripts/README.md 引用 3 个退役名（gate-result.sh/agate-workspace-resolve.sh/check-windows-smoke.sh）均不存在且非叙事 → BDD-3 豁免清单未含、BDD-1 0 漂移会被打破
- [x] 发现扫描范围歧义：docs/hardening-roadmap.md（agate-create-subtask.sh/agate-feedback.sh 不存在）、docs/superpowers（check-gate.sh 等退役名）不在影响面表扫描范围，BDD-1 "全仓" 措辞冲突
- [x] BDD-4 实测成立：phase-cards/rules 0 行号引用、脚本名全解析 → 入 PROTOCOL_DIRS 不新增 CHECK 2/3 ERROR
- [x] BDD-6/7/8/9 可测；既有 test_commit_msg_self_gate.py 4 用例确认
- [x] 写 P1-review.md
- [x] P1-review.md 已写（status: needs-revision，非空，file 存在）→ 自检通过

## 修复轮进度（analyst revise, 2026-08-16）
- 修订项 1 ✅ BDD-3 豁免清单补 scripts/README.md 退役名（gate-result.sh / agate-workspace-resolve.sh / check-windows-smoke.sh）→ 第 ⑤ 类豁免
- 修订项 2 ✅ 扫描范围定死=协议文档面（PROTOCOL_FILES+CONTEXT+assets+phase-cards/rules+README/AGENTS+UPGRADING+scripts/README+CHANGELOG，不含 docs/ 与 agate-workspace/）；UPGRADING 整文件豁免；BDD-1 措辞收窄为协议文档面
- 修订项 3 ✅ 影响面表：4.1 P3-tdd 补 ci-gate-backstop.py ×1（计数 58 成立）；新增 4.3 agate/assets/** 块（47 处，0 漂移）；4.4 计数规则可复现（58+104+22+86+61+47=378 协议面，含 CHANGELOG 595；独立复核 270/487 吻合）
- 修订项 4 ✅ BDD-5 叙事边界对齐 NARRATIVE_DIRS；docs/ 非叙事非协议文件不在扫描面显式说明（不扫=无 ERROR）
- BDD 编号 BDD-1..11 连续；[NO_NEED_CONFIRM] 保持
## P1 复审轮 progress（requirements-review，复审轮）
- [x] 读 dispatch-context / 角色定义 / 项目约定 / P0-brief
- [x] 核验修订项 1：BDD-3 ⑤ scripts/README.md 退役名已补（gate-result.sh / agate-workspace-resolve.sh / check-windows-smoke.sh，物证 scripts/README.md L45）
- [x] 核验修订项 2：扫描范围钉死协议文档面（§4 开头决策框，不含 docs/ 与 agate-workspace/）；UPGRADING 整文件豁免（BDD-3 ① / §2 / §4.4 ①）；BDD-1 措辞收窄「协议文档面」
- [x] 核验修订项 3：P3-tdd.md 补 ci-gate-backstop.py ×1（物证 L25）；agate/assets/** 新 4.3 节（47 处，实测 rg=47 可复现）；4.4 计数 378/595 可复现（核心 270/487 + 新行 61+47=108）
- [x] 核验修订项 4：BDD-5 与 NARRATIVE_DIRS 对齐 + docs/ 非扫描面处置显式声明
- [x] BDD-1..11 逐条终判（8 条直接通过，BDD-1/3/5 修订后通过）
- [x] 写 P1-review.md（覆盖上轮）
## P1 复审轮 progress 结束
