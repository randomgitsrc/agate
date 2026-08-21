---
phase: P2
task_id: TAG0018
type: review
parent: P2-design.md
trace_id: TAG0018-P2-REVIEW-20260821
status: approved
created: 2026-08-21
agent: plan-eng-review
reviewed: P2-design.md（agent: architect，candidate_count: 1，design_trivial）
verification_basis: worktree 实测（count-tests.sh = 1030；全量 pytest = 1028 passed + 2 skipped，94.6s；check-protocol-consistency.py --strict-errors-only = 0 ERROR / 335 WARNING；check-gate.py P2 预跑唯一失败项 = P2-review.md 缺失）+ agate-copy 参考实现逐文件核对 + phase-cards/P2-design.md 与 dispatch 指引规范对照
---

# P2 方案评审 — TAG0018 agate 原生支持 DSH 平台（工程维度，独立评审）

## 结论摘要

**判定：approved（可推进 P3）。** 六项交付物设计逐条满足 P1 BDD-1~19（§4 对照表全部有具体落点，关键判据经 worktree/参考实现实测核实）；gate_commands 合规（无 `&&` 短路链、`--strict-errors-only` 独立 key、per-key timeout 与实测耗时匹配）；三条核心约束（不发明新结构 / 身份薄协议厚 / 测试平台无关）落实到位；D-1~D-5 决策均有 BDD 字面或 P1-review 建议支撑，取舍自洽；影响面梳理三部分齐全且证据链完整；candidate_count: 1 与 design_trivial 声明一致。无 BLOCKER；7 条非阻塞建议 + 测试缺口见下文（建议项不影响 P3 推进，P3/P4 落地时顺手吸收即可）。

**评审过程客观查证锚点**（非仅文本审阅，均在本会话实测）：

- count-tests 基线：`bash agate/tests/scripts/count-tests.sh` 实测输出「总计：1030 个测试用例」（pytest collect-only 口径），与 P1-review S-4 要求、P2-design §5/§6 的 1030 钉死一致
- 全量回归实测：`python3 -m pytest agate/tests/ -q --tb=no` = 1028 passed + 2 skipped（= 1030 collected），94.56s——P5_timeout_seconds: 120 声明合理（实际 94.6s < 120s，层级 4 兜底 ×1.5 = 180s 有余量）
- consistency 基线实测：`--strict-errors-only` 当前 0 ERROR / 335 WARNING——设计选 `--strict-errors-only` 而非 `--strict` 正确（`--strict` 会因既有 335 个 WARNING 误判失败），R-4 的兜底路径成立
- check-gate.py P2 预跑：唯一失败项 = P2-review.md 缺失（本文件补齐后应 exit 0）；candidate_count/四字段/权衡措辞检查均通过
- 参考实现核对：agent.cordis.yml 顶层行列表每行非空 id/name、tool-fs-search 行含 `config.sampleOverCapGlobResults: false`、persona 含 `{agate_root}/orchestrator-template.md` 且不含模板首行标题（`agate/orchestrator-template.md:12` 确为「# Orchestrator（agate 编排 Agent）」，BDD-3 verbatim 判据有真实锚点）；preset.yml name/description/order 齐全；SKILL.md frontmatter `name: agate-protocol`；参考 test_dsh_preset.py 恰 5 个 `def test_` 函数
- 影响面行号核实：SETUP.md 步骤 2 在 L72、`## 步骤 3` 在 L144；Windows 区实为两个 h3（L111-129「Windows（无 WSL，用 Git for Windows）」+ L130-143「Windows 环境适配要点」）——设计 M-4 的「L111-139」边界少算 4 行，插入点实质正确（见建议 3）

## 一、六项交付物设计 × BDD-1~19 逐条核对

核对口径：设计 §3 落点 + §4 对照表 + 实测证据，逐条确认「判据可机器判定 + 设计有明确落点」：

- BDD-1（agent.cordis.yml 合法行列表、非空 id/name）：设计 §3 交付物 1 + 用例①（`_js_loader` 容忍 `!!js`）。参考实现已核实满足，判据机器可判
- BDD-2（tool-fs-search `sampleOverCapGlobResults: false`）：设计 §3 交付物 1 + 用例②精确断言；参考实现 L75 已核实在位；BDD-17 变异同源
- BDD-3（persona 薄身份）：设计 §3 交付物 1 persona 行（指向模板 + 排除首行标题）。参考实现已核实满足；但 5 用例清单未含该判据的自动化用例——见「测试缺口」与建议 1（非阻塞）
- BDD-4（preset.yml 合法 + name/description 非空）：设计 §3 交付物 2 + 用例③；S-3 语义（产品级要求非 schema 强制）传递正确，避免过度设计
- BDD-5（SKILL.md frontmatter name: agate-protocol + description 非空）：设计 §3 交付物 3 + 用例④；参考实现已核实
- BDD-6（正文四项职责×工具映射 + 平台注意四要素）：设计 §3 交付物 3 正文两节齐备，判据为子串断言，P6 文本核对可行
- BDD-7（「步骤 2-DSH」标题且位于步骤 2 平台章节区）：设计 D-1 决策 h3 置于步骤 2 区内（Windows 后、步骤 3 前）满足字面要求；标题串「步骤 2-DSH」在位。位置判据无自动化用例——见建议 2（非阻塞）
- BDD-8（mkdir -p + 三条 ln -sf 精确命令串）：设计 §3 交付物 4 命令块与 BDD-8 字面一致；用例⑤断言命令串在位；参考草稿（agate-copy SETUP.md L215-221）即三条独立 ln 行，形态可对齐
- BDD-9（不发明新结构：唯一 install-hook.py + 全仓无 per-platform installer）：设计 N-1 + M-4 含 install-hook.py 调用；worktree scripts/ 实测 40+ 脚本无 install-dsh.py，P4 grep 复证 + 完成标准 #5 兜底。install-hook.py 调用串未进用例⑤断言清单——见建议 2（非阻塞）
- BDD-10（「身份薄、协议厚」表述 + 升级跟随两种模式）：设计 §3 交付物 4 说明段两要素齐备（符号链接免操作 / 复制模式重跑），吸收 I-2/I-12
- BDD-11（会话选择器使用指引 + 模板「开始」几步验证）：设计 §3 交付物 4 使用段两要素齐备，对应 `claude --agent orchestrator` 形态
- BDD-12（platform-notes.md 含 DSH 条目、与既有条目同级）：设计 D-3 闭合括号标题 `## DSH（deepseek-harness）`，子串断言通过且无歧义（吸收 S-1）；h2 与既有 7 个条目同级，worktree 实测无 DSH 条目现状
- BDD-13（能力差异六项 + 已知注意两条）：设计 §3 交付物 5 六行能力表 + 两条注意，内容与 P0-brief issue 2 / known_risk 2 对齐
- BDD-14（互链引用 SETUP.md「步骤 2-DSH」单一真相源）：设计 §3 交付物 5 互链段，命令单一真相源成立（避免双份漂移）
- BDD-15（test_dsh_preset.py 存在 ≥5 用例全绿）：设计 §3 交付物 6 恰 5 用例（≥5 可容），参考实现 5 函数核实；P3/P5 跑单文件/全量
- BDD-16（测试平台无关）：设计 §3 交付物 6 四条禁止项（不写 /tmp / 不假设符号链接语义 / 不调用 DSH / 不依赖主目录路径），只读仓库内文件——CI 无 DSH 环境可跑，P5 全量绿即证明
- BDD-17（回归护栏红/绿可复现）：设计用例② + P3 在 worktree 重做 TDD 红→绿（草稿已红/绿验证），护栏真实性有路径
- BDD-18（全量回归底线）：设计 §5 三独立命令 + P5_count 判据 ≥1030（实测钉死），只增不减；本次实测 1030 collected / 0 ERROR 与声明一致
- BDD-19（self-gate 标记）：设计 R-3 + §4 行；触发面清单（SETUP.md / platform-notes.md / SKILL.md，tests 不触发）与 P1 §7 及 commit-msg-self-gate.py 正则口径一致

核对结论：19 条 BDD 全部有明确设计落点与验收路径，无遗漏、无模糊承接。

## 二、gate_commands 合规核对

- 无 `&&` 短路链：P5 / P5_consistency / P5_count 为三个独立 key，各自独立跑、独立记录——无任何命令串含 `&&`（TAG0004 教训规避正确）
- `--strict-errors-only` 独立 key：仅出现在 P5_consistency 单条命令内，未放入任何串接链路；实测当前基线 0 ERROR / 335 WARNING，选 `--strict-errors-only` 是唯一正确档位（`--strict` 会被既有 WARNING 误拦），设计判断与仓库现状吻合
- timeout_seconds 合理：P5=120s（实测 94.6s，贴合单元测试档位且有余量）；P5_consistency=60s、P5_count=30s（实测 count-tests 0.4s，档位宽松无害，符合"宁可定高"纪律）；P3 不设 `_timeout_seconds`（正确——P3 走既有 AGATE_TDD_TIMEOUT 机制，两层不合并）；无整体共享默认（per-key 声明，符合规则 2）
- 其他：P3 单文件命令（供 check-tdd-red.py 读取）合理；ui_affected: false → 无需 P5_e2e；未声明 formatter 退化为 exit-code-only 已显式说明，不阻断；执行 cwd（worktree 根）已钉死——见建议 4（BDD 字面路径与 gate cwd 两套口径的提示）

## 三、核心约束落实核对

- 不发明新结构：落实。worktree 实测 scripts/ 无 install-dsh.py、templates/ 为 13 个 .md 平铺；`dsh/` 子目录 + 固定文件名（agent.cordis.yml/preset.yml/SKILL.md）是 DSH 平台文件名契约（P1 I-1），非发明；BDD-9 固化 + 完成标准 #5 复证路径完整
- 身份薄协议厚：落实。persona 只写薄身份，指向 `{agate_root}/orchestrator-template.md`，不复制模板正文（BDD-3 verbatim 判据实测锚定）；升级跟随行为进 BDD-10 文档说明
- 测试平台无关：落实。四条禁止项写死，只依赖 pyyaml + agate_root fixture + 文本断言（conftest.py:306 实测在位）
- tool-fs-search 必填配置回归：落实。BDD-2（在位断言）+ BDD-17（红/绿变异）双保险，P3 重做红绿证明

## 四、D-1~D-5 决策合理性

- D-1（h3 置于步骤 2 区内 vs 草稿文件末尾 h2）：合理。BDD-7 字面要求「位于步骤 2 平台章节区」，草稿 h2 末尾不满足；h3 与 Claude Code/OpenCode/Windows 小节同级、标题串保留，断言不依赖标题级别——决策有 BDD 字面依据，取舍自洽
- D-2（移除「待实机验证」→ 已实机验证 + 版本敏感提示）：合理。吸收 S-5，陈旧标记移除，新兴平台风险改由 v0.1.0-rc.8 版本提示承载（对应 known_risk 1），措辞与事实一致
- D-3（闭合括号标题）：合理。吸收 S-1，子串断言与文档规范性同时满足，消除 P6 断言歧义
- D-4（preset.yml 最小元数据）：合理。吸收 S-3，name/description 按产品级要求断言非空、不做挂载失败类过度设计，语义边界写清
- D-5（persona/SKILL 双份映射统一口径）：合理。吸收 [SUGGEST] 1，双份是刻意设计（preset 独立可用 + skill 手动加载），R-2 以「四项职责 × DSH 工具」为唯一口径并约定同步

## 五、影响面梳理核对

- 三部分齐全（Modify 7 / Not Modify 7 / Risk 6），且位于候选方案之前（§1 在 §2 前，满足"先影响面后方案"的强制顺序）
- Modify 逐项落到文件 + 小节 + 关联 BDD；Not Modify 的 7 项均给出"看起来该改但决定不改"的理由（N-1 唯一安装脚本、N-2 模板不动、N-3 既有小节一字不动、N-6 P0-brief 锁定等），范围边界清晰，P4 判断有据
- Risk 6 条每条配缓解：R-1（测试-文档漂移，P5/P6 兜底）、R-2（双源同步，统一口径）、R-3（self-gate，commit 标记，触发面与正则口径已核实）、R-4（consistency 新形态扫描，gate 兜底 + 本次实测 0 ERROR 基线）、R-5（平台无关回归，四条禁止项 + P5 无 DSH 环境）、R-6（preset 语义误读，S-3 吸收）——覆盖了跨模块引用、双源同步、schema 变更、环境依赖四类高频风险
- 证据链：P2-progress 记录了 grep/read 命中与 worktree 状态核实（SETUP.md/platform-notes.md/scripts/templates/tests/conftest 各关键事实），非凭印象

## 六、candidate_count / design_trivial 一致性及其他机械项

- candidate_count: 1 与正文唯一候选（§2.1）一致；design_trivial 理由（§2.2）充分——P0 已锁定路线 + 每步有客观证据（实机验证、TDD 红绿、同类扫描 S-1/S-2 排除替代路线），非无效声明
- 四字段齐全（packages: [agate] / domains: [cli, docs] / ui_affected: false / gate_commands），与 P1 frontmatter 一致；ui_affected: false 无需 UI 设计节与 P5_e2e，声明合理
- dispatch_plan: {mode: single, parallel_limit: 1} 合法（单包低复杂度，mode 在契约集合内）
- minimal_validation 声明「纯代码逻辑」+ 理由 + 依赖清单（pyyaml / agate_root fixture / 文本子串断言）齐全；外部平台假设（preset 挂载、skill 按名发现、schemastery 必填、符号链接跟随）以 2026-08-21 实机验证为证据锚点，BDD-17 红/绿已有草稿验证——满足"纯代码逻辑须声明 + 附理由"要求（见建议 7 的措辞提示）
- files_to_read 8 项覆盖实现所需上下文（SETUP.md 步骤 2 区 / platform-notes / conftest:306 / install-hook.py / tests-README + 两参考文件），无上下文爆炸

## 架构问题（阻塞级）

无。

## 架构问题（非阻塞）

1. BDD-3（身份薄协议厚，核心约束）无 CI 护栏：§3 交付物 6 的 5 用例清单未含 persona 两判据（含 `{agate_root}/orchestrator-template.md` 引用 + 不含「# Orchestrator（agate 编排 Agent）」），而 §4 BDD-3 行声称「测试按子串 + 排除判据可机器断言」——设计与用例清单存在内部不一致（参考实现同样未覆盖）。建议用例①扩展或新增用例⑥断言 persona.text 两判据；BDD-15 是 ≥5，加用例不违约，核心约束值得 CI 守护
2. BDD-7 位置判据与 BDD-9 install-hook.py 调用串未进用例⑤：建议用例⑤增加 index 断言（「步骤 2-DSH」出现于 `## 步骤 2` 与 `## 步骤 3` 之间）+ `python3 ~/.agate/scripts/install-hook.py` 子串断言，使 BDD-7 前半与 BDD-9 前半机器化（BDD-9 后半「全仓无 per-platform installer」保留 P4 grep + P6 人工核对，完成标准 #5 已含）
3. M-4 影响面行号精度：SETUP.md Windows 区实为两个 h3（L111-129 + L130-143），步骤 3 在 L144，设计写「L111-139」少算 4 行；插入点实质正确（步骤 2 区末、步骤 3 前），建议 P4 以实际行号为准或修正表述为 L111-143
4. pytest 两套 cwd 口径：P1 BDD-15/16/18 字面路径（`pytest tests/…` / `pytest agate/tests/…`，相对 agate/）与 §5 gate_commands 的 worktree 根 cwd（`pytest agate/tests/…`）前缀不同——§5 已钉 cwd=worktree 根，建议 §11 完成标准补一句「pytest/consistency/count 命令一律以 §5 gate_commands 的 worktree 根 cwd 为准」，防 P6 按 BDD 字面路径跑错目录
5. §3 交付物 4 命令块用花括号简写 `{agent.cordis.yml,preset.yml}`，与 BDD-8「三条 ln -sf」措辞存在歧义（花括号展开是单条多源 ln）——参考草稿是三条独立 ln 行，建议 P4 按三条独立 `ln -sf` 行书写，与 BDD-8 字面及测试断言一致
6. R-4 可补客观证据：本次实测 consistency 当前基线 0 ERROR / 335 WARNING（`--strict` 会因既有 WARNING 误失败），建议在 R-4 或 §5 注明基线 WARNING 数，供 P4 判断新形态是否引入新 ERROR 时对照
7. minimal_validation 声明建议保留「纯代码逻辑，无外部系统依赖」原文字样（当前为释义式表述「方案为纯代码逻辑…无外部系统行为依赖」）；语义已满足要求，若未来 gate 做 verbatim 解析可零成本兼容

## 测试缺口

- BDD-3 persona 薄身份两判据无自动化用例（核心约束无 CI 护栏）——建议 1
- BDD-7 位置判据、BDD-9 install-hook.py 调用串无自动化用例——建议 2
- 其余 BDD 覆盖路径成立：BDD-6/13（SKILL.md/platform-notes 正文子串）与 BDD-10/11/12/14（SETUP.md/platform-notes 文本）由 P6 实跑文本核对；BDD-16 由 P5 无 DSH 环境全绿证明；BDD-18 由 P5 三命令兜底；BDD-19 由 P8 按触发面清单核对——均无需新增

## 锁定决策

- 六项交付物形态与落点锁定（§3），BDD-1~19 逐条有落点；dsh/ 三模板 + SETUP.md 步骤 2 区内 h3 小节 + platform-notes h2 条目 + test_dsh_preset.py 5 用例
- gate_commands 固化：P3（单文件）/ P5（全量）/ P5_consistency（`--strict-errors-only` 独立 key）/ P5_count（≥1030），per-key timeout（120/60/30）——P4-P6 不得修改
- D-1~D-5 决策锁定；影响面 Modify 7 / Not Modify 7 / Risk 6 作为 P4 范围边界与「顺手改进」拦截依据
- P7 裁剪沿用（交付物全为新增/追加，无既有代码路径修改；测试断言替代 P7 一致性职责），与 P1 结论一致

## 结论

**status: approved。** 无 BLOCKER；六项核对全部通过（BDD 逐条映射 / gate_commands 合规 / 核心约束 / D-1~D-5 / 影响面 / candidate_count 一致性），7 条非阻塞建议与测试缺口建议在 P3/P4 落地时顺手吸收（尤其建议 1、2 为低成本高收益的测试增强），不影响 P3 推进。
