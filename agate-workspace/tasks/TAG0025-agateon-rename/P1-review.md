---
agent: requirements-review
phase: P1
task_id: TAG0025
type: problems
parent: P1-requirements.md
trace_id: TAG0025-P1-review-20260826
status: approved
created: '2026-08-26'
risk_level: medium
phases:
- P1
- P2
- P3
- P4
- P5
- P6
- P7
- P8
packages:
- agate-brand-docs
- agate-installer-scripts
- agate-repo-admin
domains:
- docs
- cli
- ops
---

# P1 — 需求评审：TAG0025 Agateon 品牌改名执行 Phase 0-1

独立视角评审 `P1-requirements.md`（16 条 BDD）。评审方法：不采信 analyst 的自述结论，逐条对照
`design-rename-execution.md`（§1/§4/§5.3/§7）与 `P0-brief.md`，并对可机械验证的断言（文件:行号、
grep 命中、git 拓扑）在本机实测复核，而非仅读文本判断。

## BDD 评审

- BDD-1: **通过** + 覆盖维度：数据✗(N/A) 前端✗(N/A) 多端✗(N/A) 边界✓(首屏区域限定，不含滚动) 兼容✓(新旧品牌词并存)。Given/When/Then 可二值判定（grep "Agateon (formerly agate)" 是否出现于首屏）。
- BDD-2: **通过** + 覆盖维度：数据✗ 前端✗ 多端✗ 边界✓(不强制逐字照搬英文句式，但两词缺一不可，判定边界清晰) 兼容✓。隐含需求1（中文镜像同步）落地为独立 BDD，未被遗漏。
- BDD-3: **通过** + 覆盖维度：数据✓(CHANGELOG 段结构：先建 `[Unreleased]` 段再填条目，隐含需求2) 前端✗ 多端✗ 边界✓(插入位置=`[0.63.0]`段之上，可机械核对) 兼容✓(不改历史发布段)。已实测确认当前 CHANGELOG.md 最新发布段为 `[0.63.0]`（与 Given 陈述一致，未验证但与 P0-brief/dispatch-context 客观查证信息 C 一致）。
- BDD-4: **通过** + 覆盖维度：数据✗ 前端✗ 多端✗ 边界✓(明确"非 agateon 子串意义上的旧仓名残留"排除误判) 兼容✓(301 兜底)。**实测复核**：`install.sh:24` 确为 `git clone https://github.com/randomgitsrc/agate.git`，文件+行引用准确。
- BDD-5: **通过** + 覆盖维度同上。**实测复核**：`agate/scripts/agate-install.py:55` 确为 `DEFAULT_REPO_URL = "https://github.com/randomgitsrc/agate"`，引用准确。
- BDD-6: **通过** + 覆盖维度同上。**实测复核**：`agate/scripts/agate-changes.py:116` 确为 `"https://github.com/randomgitsrc/agate.git"`，引用准确。
- BDD-7: **通过** + 覆盖维度：边界✓(显式禁止"只改其中一行"，把 badge 与安装入口绑定为同一原子判定单元，回应隐含需求7) 兼容✓。**实测复核**：README.md:5(badge)、README.md:29(安装入口) 均命中，引用准确。
- BDD-8: **通过** + 覆盖维度同 BDD-7。**实测复核**：README.zh-CN.md:5、:29 均命中，引用准确。
- BDD-9: **通过** + 覆盖维度：多端✓(7 处跨文件批次一致性) 边界✓("同一 commit"为客观可验证标准，非"⚠️部分完成"式中间态，见下方重点核查①)。
- BDD-10: **通过（含 1 条非阻塞 SUGGEST，见下方重点核查②）** + 覆盖维度：数据✓(全仓字面扫描) 边界✓(显式豁免清单，防止历史文档误判为残留) 兼容✓(保持历史记录真实性不与验收目标冲突)。
- BDD-11: **通过** + 覆盖维度：边界✓(权限核实 vs 放行确认的前置条件拆分，见下方重点核查③) 兼容✗(N/A，不可逆操作无兼容概念)。
- BDD-12: **通过** + 覆盖维度：边界✓(状态码+Location 头双重断言) 兼容✓(301 是老链接兼容手段本身)。
- BDD-13: **通过** + 覆盖维度：边界✓(返回码0 + SHA 非空双重断言，排除"看似成功但空输出"的假阳性)。
- BDD-14: **通过** + 覆盖维度：边界✓("首屏"=不需翻页，可观察断言)。注：搜索索引更新时机不受本任务控制，Given 已用"且 GitHub 搜索索引已更新"限定前提，未把不可控外部时序误判为本任务责任范围，处理得当。
- BDD-15: **通过** + 覆盖维度：多端✓(主 checkout+worktree 一致性) 边界✓。**实测复核**：`git worktree list` 确认当前仅 1 个 worktree + 主 checkout，`git remote -v` 仅 1 个 remote(origin)，与 Given 陈述完全一致。
- BDD-16: **通过** + 覆盖维度：边界✓(两次 fetch 均需返回码0，不因"机制上应自动生效"而省略验证步骤，呼应隐含需求5)。

**BDD 编号连续性**：#### BDD-NN: 格式一致，1-16 连续无跳号，16 条与 dispatch-context 声明一致。
**单场景检查**：BDD-7/8 每条含 2 行(badge+安装入口)，但二者被设计文档与 known_risks 判定为不可分割的同一批次原子单元（非两个独立 Given/When 场景硬凑一条），判定属恰当合并，不属于"多场景未拆分"的反模式。

## 隐含需求覆盖

- 数据维度：覆盖（BDD-3 CHANGELOG 段结构先建后填；BDD-10 全仓扫描属数据完整性核查）
- 前端维度：不适用（domains 无 frontend，已在 frontmatter 与正文 §7 显式声明豁免，无需 UX 类别 BDD）
- 多端维度：覆盖（BDD-9 批次原子性、BDD-15/16 主 checkout↔worktree 一致性，均为本任务语境下的"多端"对应物）
- 边界维度：覆盖（BDD-10 豁免清单处理边界文档；BDD-11 拆分权限核实/放行确认两个前置条件；BDD-12/13 双重断言排除假阳性）
- 兼容维度：覆盖（BDD-12 的 301 是旧链接兼容手段本身；BDD-1/2 新旧品牌词并存不破坏历史认知连续性）

隐含需求识别（正文第 2 节 7 条）逐条核对：均已转化为对应 BDD 或 BDD 内的显式子句，无遗漏、无"识别但未落地"的断层。

## 裁剪评审（phases 全流程不裁）

- **P1/P2/P4/P5/P6 协议硬性不可裁**：属实，无需展开。
- **P3 不裁剪**：理由"risk_level=medium，仅 low 档可裁 P3"——**已核对 `agate/scripts/check-pruning.py` L181-183**：`if "P3" not in phases and risk_level != "low": errors.append("P3 不可裁剪——仅 low 风险可裁剪 TDD 阶段")`，字面依据准确，非套话。
- **P7 保留**：理由是"批次原子性(BDD-9)对应的跨文件一致性风险"。已核对 `check-pruning.py` L185-198：P7 本可裁（源码文件数≤5 且无 implicit_coupling 时），analyst 选择不裁而非"裁不了"，理由（7 处文件+双语镜像的横切改动风险）与 known_risks"须同批全改"直接对应，站得住。
- **P8 保留**：理由是"roadmap RM-AG0035 回写 done 是 P8 gate 硬校验（RM-AG0043）"。已核对 `check-pruning.py` L201-206：P8 可裁但需 `internal_only: true` 声明，本任务对外可见（品牌声明+仓库改名），不满足 internal_only 语境，保留合理。
- **结论**：裁剪声明的每条理由均可在机械 gate 脚本或设计文档中找到对应依据，非"抄卡片模板"式空转。

## 审声明（风险分级/裁剪声明 vs diff 证据）

- **实测 `git status --short`**：暂存区当前仅 4 个 untracked 任务文档（P1-dispatch-context-analyst.md / P1-dispatch-context-requirements-review.md / P1-progress.md / P1-requirements.md），`git diff --cached --stat` 为空——**当前无实现层 diff**。
- 按 dispatch-context 重点核查项⑤的指引：本 P1 阶段的 `risk_level` 判断依据应为"计划中的改动范围"而非"当前已存在的 diff 规模"。正文 §6 末尾的 risk_level=medium 论证（不评 low：含 1 条不可逆外部操作 GitHub 改名+CI 徽章断链风险+7 处跨批一致性要求；不评 high：不触碰 `agate/` 协议正文、不改任何 `check-*.py` gate 脚本逻辑、无数据迁移、无破坏性行为变更）是基于**计划范围**的论证，未因暂存区当前 diff 很小而误判虚高或虚低，逻辑自洽，予以认可。
- `ceremony`：不声明（fail-closed 默认 standard）。**已核对** `agate/rules/phases.yaml` P1 `task_fields: [risk_level, phases, packages, domains]` 与 `agate-md-field-set.py` 的 `GENERIC_HEADER_KEYS`（均不含 `ceremony`）——analyst"当前稳定版 key 白名单未收录该字段"的断言经源码核实**准确**，不是编造理由绕过声明，处理方式（不手写、遵循 fail-closed）符合项目纪律。
- `ceremony: full` 场景不适用（未声明 full，跳过 P7 含否核对）。

## 5 个重点核查项逐一结论

① **BDD-9 批次原子性是否可二值判定**：**是**。"同一个 commit 的 diff 中"是可通过 `git show --stat <sha>` 或 `git log --oneline` 客观核验的边界，未退化为"须协调一致"之类主观描述。

② **BDD-10 豁免清单是否真的让验收锚可判定**：**是，但有 1 条非阻塞改进建议**。已实跑 dispatch-context 给出的全仓 grep 命令并逐条比对 BDD-10 的 4 类豁免（①archived/+agate-workspace/tasks/**+agate-workspace/archived/** ②商标调研文档 ③历史评审快照 ④HANDOFF-TAG0025.md）：**当前全部命中均被 Phase1 核心 7 处（将被修复）或 4 类豁免之一覆盖，排除后剩余命中数=0**，验收锚可判定不会永远 FAIL。`[SUGGEST: 豁免类别①的措辞"agate-workspace/tasks/**、agate-workspace/archived/**"比设计文档 §5.3 原文"agate-workspace/"（整体豁免，含 roadmap/debt/reviews/plans/agents 等未列出子目录）窄；已实测这些未列出子目录当前 0 命中，不构成现时误判，但严格按设计原文口径会更稳健、避免未来这些子目录偶然引入历史 URL 引用时的伪 FAIL。建议 P2/P3 阶段视野内简单加宽为 agate-workspace/**（不改变判定语义，只是扩大豁免面），非阻塞，可不改。]`

③ **BDD-11 与"gh 权限已核实"是否被正确区分**：**是**。Given 明确"权限核实已完成，不需要在本 BDD 里重复设计申请权限步骤"；Then 明确"权限核实（技术上能不能做）不能替代放行确认（现在要不要做），二者是并列的两个前置条件，缺一不可"。两者未混为一谈，且把"确认发生在本次改名操作执行窗口内"作为时效性限定（不能用更早的一次性确认顶替），处理严谨。

④ **内部命名空间禁动是否被误触**：**未误触**。BDD-4~10 全部点名具体文件+行（install.sh:24 等），无一条使用"全局替换 agate→agateon"式笼统措辞；BDD-10 的扫描目标是 `randomgitsrc/agate\b`（仓库路径 URL 片段）而非裸词 `agate`，天然排除内部命名空间 token（`agate/`、`~/.agate`、`AGATE_*`、`agate-*.py`、`agate_common`）被误伤的可能；BDD-1/2 甚至要求品牌声明句中显式保留小写 `agate` 一词（"formerly agate"），进一步印证未误触三层解耦原则。

⑤ **risk_level: medium 是否与需求范围匹配**：**匹配**，见上方"审声明"节，已用 git 实测证据排除"因暂存区 diff 小而应判 low"的误判路径，论证基于计划改动范围（1 条不可逆操作+CI 耦合风险+7 处跨批一致性 vs 不碰协议正文/gate 脚本/无数据迁移），low/high 两侧排除理由均可自洽。

## P1 纯净性

未发现掺入解决方案设计。BDD 中出现的具体文件路径/行号/grep 命令/curl 命令均属"验收锚如何客观判定"的必要精度（回应正文警戒线"必须点名具体文件+行"的强制要求），不是"怎么实现"的方案设计；BDD-11 引用的 `gh api -X PATCH ...` 命令形态仅作为"改名调用"的illustrative 例示（"如"），未强制实现方式。3.4 节的回归测试建议已正确标注为 `[SUGGEST]` 并声明"由 P2/P3 决定具体落地形式"，未在 P1 提前拍板方案，纯净性符合要求。

## 总体判定

approved。16 条 BDD 全部可二值判定、编号连续、文件行号引用经实测核实准确；隐含需求 5 维覆盖完整；跨条一致性无矛盾；裁剪声明逐条有机械依据；risk_level/ceremony 声明与暂存区证据/工具白名单核实一致；5 个重点核查项全部过关，仅 1 条非阻塞 SUGGEST（BDD-10 豁免类别①措辞可进一步加宽以对齐设计原文，不影响当前判定的可判定性）。
