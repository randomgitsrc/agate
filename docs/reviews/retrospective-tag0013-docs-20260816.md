> 历史复盘（迁移前旧布局），新复盘请见 `tasks/{Txxx}/retrospective.md`（模板：`agate/assets/templates/retrospective-template.md`）

# TAG0013 复盘 — agate 脚本一致性批（v0.48.0）

> 任务：RM-AG0015（CHECK 10 文档脚本名引用漂移 gate）+ RM-AG0017（self-gate 触发面补 README/AGENTS）+ RM-AG0018 剩余（check-retrospective 登记提醒）
> 分支：feat/TAG0013-script-consistency → PR #141（普通 merge）→ v0.48.0
> 执行窗口：2026-08-15 ~ 2026-08-16

---

## 1. 任务概述

TAG0013 是三条同簇子需求的合并批次：三处改动均落在"脚本 + 测试 + consistency"层，改动域重叠（check-protocol-consistency.py / commit-msg-self-gate.py / check-retrospective.py + 对应测试），合并一个 task 减少重复编排。P0-P8 全流程执行，11 条 BDD 全 PASS，768 pytest / 0 consistency ERROR / 770 count，CI 双矩阵（ubuntu + windows）全绿后合并。

## 2. 交付摘要

| 子需求 | 改动 | 验证 |
|--------|------|------|
| RM-AG0015 | CHECK 10 内联（协议文档面脚本名引用漂移 gate，5 类豁免 + CHANGELOG 聚合 WARNING）+ phase-cards/rules 入 PROTOCOL_DIRS + main() split 修复 | P6 BDD-1/2/3/4/5 实测；DEBT0001 关闭 |
| RM-AG0017 | `_SELF_GATE_RE` 补 README.md/AGENTS.md（精确名锚定，CHANGELOG 天然豁免）+ 提示文案同步 | P6 BDD-6/7/8/9 实测（含既有 integration 断言更新） |
| RM-AG0018 剩余 | check-retrospective.py warnings 块追加 DEBT/roadmap 登记提醒行（纯提醒） | P6 BDD-10/11 实测（RT.1 空输出不回归） |

## 3. 做得好的

1. **P1 影响面表一次收敛**：P0-brief known_risks 强制要求"全仓 grep 脚本名引用建影响面表"——P1 analyst 产出 4.1/4.2/4.3 影响面表（378 处协议面引用 + 计数规则可复现），CHECK 10 的 5 类豁免设计一次到位，P1 review 一轮 needs-revision 后 approved，后续 P2/P4 未再返工影响面问题。
2. **BLOCKER-1 在 P2 发现而非 P5**：CHECK 10 与 CHECK 1 的前缀碰撞（`"CHECK10-scriptref".startswith("CHECK1")` 为 True）被 plan-eng-review 在 P2 抓到，避免了 P5 才发现返工。教训本身已记入 P8-release Lessons Learned。
3. **SCOPE+ 处理闭环**：P4 发现既有 integration 测试 `test_csg_1` 断言 README 不触发（旧行为，与 BDD-6 冲突）——主 Agent 登记 [SCOPE+ from P4]，定向修复（断言翻转 + 改名），P7 SCOPE_RESOLVED 闭环，check-scope-resolved 无拦截。
4. **双工作区纪律零事故**：全程 gate 用 `~/.agate` 稳定版、consistency 用 worktree 自己、commit hook 由共享 git 目录触发，未发生"用未验证新 gate 判自己"或改错 checkout。
5. **CHECK 10 增量性保持**：落地后 0 ERROR（279 WARNING 基线仅 +1 条 CHANGELOG 聚合），既有合法引用零误伤，CI 无新增红。

## 4. 问题与教训

### 4.1 P3 测试设计遗漏既有 integration 断言（SCOPE+ 根因）

- **现象**：P3 test-designer 只在 unit 测试文件补了 README/AGENTS/CHANGELOG 3 用例，未检查 integration 层已有的 `test_csg_1_non_trigger_no_warning`（断言 README.md 不触发 = 旧行为）。P4 实现后该用例转红，触发 SCOPE+。
- **根因**：P3 dispatch-context 只列了 unit 测试文件，没让 test-designer grep 全仓相关测试（self-gate 触发面相关的既有断言）。
- **改进**：同类"触发面扩展"变更，P3 应全仓 grep 该脚本的所有测试引用（unit + integration），在 P1/3 影响面阶段就识别既有断言冲突。P8-release Lessons Learned 已记录。

### 4.2 发布时 CI 首轮 pytest fail（CHECK 7 badge vs tag）

- **现象**：PR push 后 pytest 双矩阵 fail——README badge 已 bump v0.48.0，但远端 tag 还是 v0.47.0 → CHECK 7 ERROR。
- **根因**：按 AGENTS.md 版本发布流程，tag 是"bump 后 `git tag && git push origin vN.N.0`"——但本次 PR 先合并前 push 了代码分支，tag 尚未推送，CI checkout 时看不到新 tag。
- **处理**：`git push origin v0.48.0` 推送 tag 后重跑 pytest，双矩阵全绿。
- **改进**：P8 发布时若版本 bump 涉及 badge（CHECK 7），tag 应在 PR CI 跑之前推送（或至少 CI 重跑前）。这是版本发布流程第 4 步（tag push）与 PR CI 时机的衔接问题，非协议缺陷——本次是流程执行顺序问题，已处理。

### 4.3 dispatch-context 行首 `- PASS/FAIL` 预判误触 provenance 审计

- **现象**：P6 dispatch-context「返回给我」节写了 `- PASS/FAIL 计数`，被 check-p6-provenance 预判正则 `^\s*- (PASS|FAIL)` 命中，verifier 自查发现并报告，主 Agent 修复措辞。
- **根因**：dispatch-context 模板明确禁止行首 `- PASS`/`- FAIL`，但"返回给我"节的样例占位符本身用了该格式（`- PASS/FAIL 计数`），主 Agent 复制时未察觉。
- **改进**：主 Agent 写 dispatch-context 时「返回给我」节避免任何行首 `- PASS`/`- FAIL` 措辞（哪怕是说明文字）。

## 5. 复盘机制触发核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 否（无阶段 retry 超限） | — | | |
| PAUSED | 否 | — | | |
| PROD_TOUCHED | 否（纯文件系统 + git 操作） | ✅ [PROD_NOT_TOUCHED] 各 subagent 标注 | | |
| SCOPE+ | 是（P4 发现 integration 断言过时） | ✅ 主 Agent 登记 P1 §8 + P4 定向修复 | 若不登记，既有测试冲突无法追踪 | 需求驱动的行为变更 |
| SCOPE_RESOLVED | 是 | ✅ P7 登记 + P1 §8 回写 | | |
| DESIGN_GAP | 否（实现严格按 P2 候选方案 A） | ✅ P4 声明"无" + P7 DESIGN_GAP_REVIEWED | | |
| DESIGN_GAP_REVIEWED | 是（P4 声明了"无"，P7 需配对说明） | ✅ | | |
| NEED_CONFIRM | 否 | ✅ [NO_NEED_CONFIRM] | | |
| CAPABILITY_GAP | 否 | ✅ capability_requirements 全 available | | |
| gate 验证（每阶段） | 是 | ✅ P1-P8 每阶段预跑 + commit hook 复核 | | |
| 阶段产出文件（每阶段） | 是 | ✅ P0-P8 全部产出齐全 | | |
| .state.yaml phase 同步 | 是 | ✅（P4 commit 前一次 WARNING 提醒后修正） | 修正后 phase 与产出同步 | P4 未先改 phase 再 commit，hook WARNING 提醒 |
| 裁剪条件 + override | 否（phases 全流程无裁剪） | — | | |
| capability_requirements | 是 | ✅ P1 三态声明（python3+pyyaml/pytest/ruff 均 available） | | |
| 分阶段落盘（防 subagent 空返回） | 是 | ✅ 各阶段 progress 文件均存在 | | |
| phase-产出一致性 | 是 | ✅（P4 WARNING 后修正） | | |
| P6 evidence（含截图 + 引用 + vision YAML） | 是（无 UI，无需截图） | ✅ 11 条 BDD 各 1 证据文件 + 引用 | | |
| P2 候选方案 + 权衡（≥2） | 是 | ✅ 6 候选（3 处改动各 2）+ 权衡 + 选择理由 | | |
| P8 internal_only_reason | 否（P8 未裁剪） | — | | |
| dispatch-context.md | 是 | ✅ P1-P8 每阶段派发前写 + agate-inject-card 注入 | | |
| pre-commit hook（gate / 状态转移 / 裁剪） | 是 | ✅ 各 commit hook 自动触发 | | |
| CI backstop | 是 | ✅ push 后 CI 双矩阵全绿 | | |
| 技术债登记 | 是（复盘发现缺口 → DEBT 或 roadmap） | ✅ DEBT0001 已登记（2026-08-15）并于本任务关闭 | 未登记 = 机制缺口（DEBT0001 教训） | 本任务本身即修复 DEBT0001 |

## 6. 版本发布清单核对（AGENTS.md）

- [x] pytest 全过（768 passed / 2 skipped）+ 0 consistency ERROR + 0 ruff error（count-tests 770）
- [x] README.md version badge + CHANGELOG.md [Unreleased] → [0.48.0]
- [x] UPGRADING.md 新增 v0.48.0 章节（无破坏性变更声明）
- [x] `git tag v0.48.0 && git push origin v0.48.0`（CHECK 7 自动通过）
- [x] release PR 普通 merge（--no-ff，非 squash）——tag 保持为 main 祖先，`git describe origin/main` = v0.48.0
