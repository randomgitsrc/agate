---
phase: P1
task_id: TAG0018
type: review
parent: P1-requirements.md
trace_id: TAG0018-P1-REVIEW-20260821
status: approved
created: 2026-08-21
agent: requirements-review
reviewed: P1-requirements.md（19 条 BDD，agent: analyst）
verification_basis: 实机核验（~/.dsh/.agent-presets/agate 软链到 agate-copy 参照实现；DSH 源码 packages/fs/tool-fs-search/README.zh.md、packages/preset/agent-presets/src/metadata.ts）+ P0-brief.md + P1-progress.md
---

# P1 需求基线评审 — TAG0018 agate 原生支持 DSH 平台

## 结论摘要

**判定：approved（可推进 P2）。** 19 条 BDD 全部可二值机器判定，P0-brief 的 3 条 issues + 4 条 known_risks（含强制同类扫描要求）全部落到 BDD 或强制节，四项核心约束（不发明新结构 / 身份薄协议厚 / 测试平台无关 / tool-fs-search 必填配置回归）均已固化。无 BLOCKER；5 条非阻塞建议 + 2 条可忽略项见文末。独立评审，非需求作者自审（agent=requirements-review ≠ analyst）。

**评审过程客观查证锚点**（非仅文本审阅）：

- tool-fs-search 必填配置事实：DSH 官方 `packages/fs/tool-fs-search/README.zh.md` 明文「`sampleOverCapGlobResults` 是必填项且没有回退值」——BDD-2 的缺陷描述与 BDD-17 的回归语义有事实支撑
- 实机安装形态：`~/.dsh/.agent-presets/agate/` 下 agent.cordis.yml / preset.yml 均为软链（指向 agate-copy 参照实现），与 BDD-8 的符号链接安装方案一致
- 参照实现结构：agent.cordis.yml 顶层为行列表、每行含非空 id/name、persona 含 `{agate_root}/orchestrator-template.md` 引用且不含模板首行标题「# Orchestrator（agate 编排 Agent）」、tool-fs-search 行带 `config.sampleOverCapGlobResults: false`——BDD-1/2/3 断言可兑现
- preset.yml 性质：DSH `src/metadata.ts` 确认 preset.yml 是**可选展示元数据**（缺失仍挂载、name 回退 preset id、order 可选）——BDD-4 的 name/description 非空属产品级要求而非 schema 强制（见建议 S-3）
- 参照测试：test_dsh_preset.py 含 5 个 `def test_` 函数，满足 BDD-15「≥5 用例」
- SKILL.md 已实机安装且本会话可加载（`~/.dsh/skills/agate-protocol/SKILL.md`），BDD-5/6 断言可兑现

## BDD 评审（逐条）

> 判定口径：可验收 = Given/When/Then 完整 + 判据可机器二值判定。覆盖维度标注：数据 / 前端 / 多端 / 边界 / 兼容。

### 交付物 1：assets/templates/dsh/agent.cordis.yml

- BDD-1（agent.cordis.yml 合法 YAML 行列表）：可验收。覆盖维度：数据✓ 前端✗ 多端✗ 边界✓（非空 id/name）兼容✗。判据 = YAML 解析（容忍 `!!js`）+ 行级字段检查，机器可判；参照实现与本 BDD 一致
- BDD-2（tool-fs-search 带 sampleOverCapGlobResults: false）：可验收。覆盖维度：数据✓ 边界✓（必填缺失 fail-closed 路径）兼容✗。判据 = 行级 config 字段精确断言；DSH 官方 README 已核实该字段必填无默认值，缺陷回归有据
- BDD-3（persona 薄身份、指向模板而非内嵌正文）：可验收。覆盖维度：兼容✓（模板随 ~/.agate 升级自动更新）。判据 = 含路径引用 + 排除模板首行标题（verbatim 判据已量化），机器可判；无主观词

### 交付物 2：assets/templates/dsh/preset.yml

- BDD-4（preset.yml 合法 YAML、name/description 非空）：可验收。覆盖维度：数据✓ 边界✓（非空）多端✗ 兼容✗。判据 = YAML 解析 + 字段非空断言；参照实现 name/description/order 齐全

### 交付物 3：assets/templates/dsh/SKILL.md

- BDD-5（frontmatter 含 name: agate-protocol 与 description）：可验收。覆盖维度：数据✓ 多端✗ 边界✗ 兼容✗。判据 = frontmatter 解析 + 字段断言；实机 skill 目录按名发现机制已核验
- BDD-6（正文含 DSH 工具映射与平台注意）：可验收。覆盖维度：多端✓（平台差异映射）兼容✓。判据 = 子串断言（四项职责映射 + 平台注意四要素），已列出具体映射键值对，机器可判

### 交付物 4：SETUP.md 步骤 2-DSH

- BDD-7（含「步骤 2-DSH」章节且位于步骤 2 平台章节区）：可验收。覆盖维度：多端✓（与既有平台小节同构）。判据 = 章节标题存在性 + 位置断言；当前 SETUP.md 步骤 2 确有 Claude Code/OpenCode/Windows 小节（已核验）
- BDD-8（符号链接安装命令指向模板与 DSH 安装目标）：可验收。覆盖维度：数据✓（命令串精确断言）多端✓。判据 = 具体命令串（mkdir -p + 三条 ln -sf + 源路径）子串断言；实机安装路径 `~/.dsh/.agent-presets/agate/`、`~/.dsh/skills/agate-protocol/` 与断言一致
- BDD-9（不发明新结构——仅符号链接 + 唯一 install-hook.py）：可验收。覆盖维度：兼容✓（既有安装原则）。判据 = 章节含 install-hook.py 调用 + 全仓 grep 无 per-platform installer；同类扫描 S-2 已确认 scripts/ 仅 3 个脚本、无 install-dsh.py
- BDD-10（身份薄协议厚说明 + 升级跟随行为）：可验收。覆盖维度：多端✓（Windows/无符号链接权限复制模式退化）兼容✓（升级跟随 + 复制模式重跑）。判据 = 子串断言「身份薄、协议厚」表述 + 升级/复制两条行为说明
- BDD-11（使用与验证指引）：可验收。覆盖维度：多端✓（对应 Claude Code 使用形态）。判据 = 会话选择器使用指引 + orchestrator-template.md「开始」几步验证的子串断言

### 交付物 5：platform-notes.md DSH 条目

- BDD-12（含 DSH 平台条目，与既有条目同级）：可验收。覆盖维度：多端✓（条目结构与既有平台条目对齐）。判据 = 条目标题存在性 + 同级位置；见建议 S-1（断言串缺右括号）
- BDD-13（能力差异对照表 + 已知注意）：可验收。覆盖维度：多端✓ 兼容✓。判据 = 能力表六项 + 已知注意两条的子串断言，内容已在 BDD 内显式枚举
- BDD-14（引用 SETUP.md「步骤 2-DSH」为单一真相源）：可验收。覆盖维度：多端✓（跨文档互链）兼容✓。判据 = 互链引用子串断言；coupling_checklist 第 2 项对应

### 交付物 6：tests/unit/test_dsh_preset.py

- BDD-15（测试存在且 ≥5 用例、pytest 全绿）：可验收。覆盖维度：数据✓（覆盖五类断言对象）。判据 = pytest collect-only 计数 ≥5 + 全绿；参照实现恰好 5 用例，≥5 宽松可容
- BDD-16（测试平台无关——无 DSH 实例/无 ~/.dsh//tmp 不可写可跑）：可验收。覆盖维度：边界✓（无实例/无主目录/无 /tmp 写权限环境）兼容✓（CI 无 DSH 约束）。判据 = 环境约束 + pytest 全绿；核心约束「测试平台无关」在此固化
- BDD-17（回归护栏有效——缺配置红、在位绿）：可验收。覆盖维度：边界✓（配置缺失路径）兼容✓。判据 = 变异测试红/绿双态复现，机器可判；是 BDD-2 缺陷回归的真实性证明，非空断言
- BDD-18（全量回归——全绿 + consistency 0 ERROR + 用例数不漂移）：可验收。覆盖维度：兼容✓（"Linux 现状是基线"不破）。判据 = 三条命令结果断言；见建议 S-4（基线数未钉死，操作上可补）

### SELF-GATE 触发面（P8 核对用）

- BDD-19（触发文件 commit 携带 self-gate 标记）：可验收。覆盖维度：兼容✓（协议既有机制）。判据 = commit-msg 含 `self-gate-review:`/`self-gate-skip:`；触发面清单（SETUP.md / platform-notes.md / SKILL.md，tests 不触发）与 commit-msg-self-gate.py 正则已核验一致（P1-progress 记录）

## 隐含需求覆盖

- 数据维度：覆盖（I-1 文件名契约 → BDD-1/4/5；I-4 必填配置 → BDD-2/17）
- 前端维度：不适用——domains=[cli, docs] 无 frontend，无 UX 类别 BDD / ui_render_shape / 视觉能力条目要求（第 8 节已显式声明）
- 多端维度：覆盖（I-2/I-12 Windows 复制模式退化 → BDD-10；I-10 既有平台章节/条目同构 → BDD-7/12/13；I-7 单一真相源互链 → BDD-14）
- 边界维度：覆盖（I-4 配置缺失 fail 路径 → BDD-2/17；非空字段 → BDD-1/4；无实例/无 /tmp 环境 → BDD-16）
- 兼容维度：覆盖（I-3 身份薄协议厚 + 升级跟随 → BDD-3/10；I-8 SELF-GATE → BDD-19 + 第 7 节；I-9 全量回归底线 → BDD-18；I-11 无存量影响显式声明于第 1 节）

隐含需求 I-1~I-12 全部有 BDD 或强制节承接，无遗漏；「无数据/存量影响」也显式声明（I-11），防止误加迁移步骤。

## 核心约束固化核对

- **不发明新结构**：固化（BDD-9 + 同类扫描 S-1/S-2：无 platforms/ 目录、无 install-dsh.py、唯一 install-hook.py；S-4 论证 dsh/ 子目录与 .yml 为 DSH 平台文件名契约强制，非发明）
- **身份薄协议厚**：固化（BDD-3 persona 指向 orchestrator-template.md 且不复制正文；BDD-10 文档说明升级跟随）
- **测试平台无关**：固化（BDD-16 显式声明不写 /tmp、不假设符号链接语义、不调用 DSH、不依赖主目录路径）
- **tool-fs-search 必填配置回归**：固化（BDD-2 配置在位断言 + BDD-17 红/绿变异验证，双保险）

## P0-brief issues / known_risks 覆盖核对

- issue 1（DSH 无 .claude/agents 等价物、agent-preset 注册、薄身份）：→ BDD-1/3/4/7/8/10 覆盖
- issue 2（DSH 工具面映射 + 平台注意，SKILL.md）：→ BDD-5/6/13 覆盖
- issue 3（tool-fs-search 必填配置缺陷回归测试）：→ BDD-2/15/17 覆盖
- known_risk 1（新兴平台、CI 无 DSH、文档待实机验证项）：→ BDD-16 覆盖「测试只校验仓库内文件」实质；实机验证已完成（P0-brief 记录），见建议 S-5
- known_risk 2（sandbox 只读 Errno 30）：→ BDD-6/13 覆盖（SKILL.md + platform-notes 已知注意）
- known_risk 3（改动面触发 SELF-GATE）：→ BDD-19 + 第 7 节覆盖；P0-brief 误列 tests/ 已按轻微漂移记录并修正触发面
- known_risk 4（强制同类扫描）：→ 第 6 节 S-1~S-8 全量执行（命中数 + 逐条判定 + 回归拦截 + 结论落盘），BDD-9 固化"示范不发明新结构"

## 同类扫描核验

8 项扫描（S-1~S-8）均含命中数量 + 文件清单 + 逐条判定；S-3 主仓库 0 命中确认从零引入；S-4 对新增形态（dsh/ 子目录、.yml）给出外部契约论证；回归拦截声明了文档约定 + BDD-9 守护。满足强制节要求（结论落盘于需求文件正文，非仅 progress）。

## 裁剪评审（P7 + coupling_checklist）

- 跳过 P7 一致性：理由充分——① 交付物全部为新增文件与文档追加章节，无既有代码路径被修改，无隐式耦合；② coupling_checklist 3 项显式互链逐项 checked 并映射到 BDD-8/9/14/15/17 断言；③ risk_level: low 增量改动；④ 跳过风险（测试断言与文档实现漂移）已声明并由 BDD-8/15 在 P5/P6 兜底
- risk_level: low：与实际风险匹配（新增模板 + 文档章节 + 独立测试文件，不触碰既有协议机制运行时行为，实机验证已完成）
- 其余阶段 P1/P2/P3/P4/P5/P6/P8 保留：合理；P3 保留的论据（BDD-17 红/绿是护栏有效性证明）成立；P8 保留理由（对外功能发版）成立

## 时效性质疑核验

第 0 节逐字段对照（task/issues/known_risks/executor_env/env_constraints），1 处轻微漂移（known_risks 第 3 条 self-gate 触发面）已按「记录」处理并落 `[P0_STALE: 具体漂移点]`（行首声明、含正则证据），无严重漂移，判定与 P1-progress 一致。见建议 S-2（"已更新该字段描述"措辞与 P0-brief 文件未物理改动的事实不符）。

## capability_requirements / verification_env 评审

- 两项 need（yaml-structure-validation、doc-text-assertion）均 status: available，附环境证据（pyyaml 版本、草稿测试已红/绿验证）与纯文本断言无外部依赖说明
- 无 status: GAP；无行首 [NEED_CONFIRM]（第 4 节为 [NO_NEED_CONFIRM]，两条 [SUGGEST] 属可采纳倾向项，不阻塞）
- verification_env 不声明：符合判断树——验收路径 = 仓库内文件断言（python3 + pyyaml + pytest 就绪），真实 DSH 验证已完成且 CI 无 DSH 属既定约束，不标能力三态（引用 TAG0009 教训），机制使用正确

## 建议项（非阻塞，S 系列）

- S-1：BDD-12 的标题断言串 `## DSH（deepseek-harness` 缺右括号，建议统一为 `## DSH（deepseek-harness）`，避免 P6 断言歧义（子串断言当前可通过）
- S-2：第 0 节「已更新该字段描述」与 P0-brief.md 文件未物理改动的事实不符——建议改为「修正已记录于本文件第 0/7 节 + BDD-19，P0-brief 保持锁定未物理改动」，消除 audit 歧义（P0-brief 锁定与卡片「轻微漂移更新对应字段」存在张力，当前以记录方式处理可接受，措辞需澄清）
- S-3：BDD-4 的 name/description 非空是产品级要求（会话选择器展示「agate 编排者」）而非 DSH schema 强制（metadata.ts 证实缺失仍挂载）——建议在 P2/P4 传递此语义，防止实现时误以为缺 name/description 会挂载失败而过度设计
- S-4：BDD-18 的「用例总数 ≥ 改动前基线」未钉死基线数值——建议 P4 启动前把 count-tests.sh 当前值记入 P1-progress 或 P5 派发上下文，P6 比对有据
- S-5：known_risk 1 的「文档标注待实机验证项」缓解措施在实机验证完成后已基本失效——建议 P4 时决定 SETUP.md 步骤 2-DSH 是保留 DSH 版本敏感提示（v0.1.0-rc.8 机制可能变化）还是移除「待实机验证」字样，避免文档留下过时标记

## 可忽略项

- BDD-15「≥5 用例」与参照实现恰好 5 用例：宽松断言可容，无需收紧
- preset.yml 的 order 字段未被断言：DSH schema 中 order 可选且无排序刚需，可忽略
- BDD-8 精确命令串断言较脆弱（字符串漂移风险）：属有意的文档完整性测试，coupling_checklist 已列为 checked 并由 BDD-8/15 兜底，可接受

## 结论

**status: approved。** 19 条 BDD 全部可验收、P0-brief issues/known_risks 全覆盖、四项核心约束固化、同类扫描与时效性质疑满足强制要求、P7 裁剪 + coupling_checklist 合理、capability 三态合法。无 BLOCKER，可推进 P2（P2 需承接建议 S-3 的 preset.yml 语义与 S-4 的基线记录）。
