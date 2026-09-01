---
agent: requirements-review
phase: P1
task_id: TAG0026
type: review
parent: P1-requirements.md
trace_id: TAG0026-P1-review-20260830
created: '2026-08-30'
status: approved
risk_level: high
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
- agate-scripts
- agate-tests
- agate-phase-cards
- agate-templates
domains:
- backend
---

# P1 — 需求评审：TAG0026 维护性反模式 gate（RM-AG0046）

> 评审对象：`P1-requirements.md`（analyst 产出，13 条 BDD）。
> 评审方法：不采信 analyst 自述，逐条对照设计文档
> `docs/design-notes/rm-ag0046-maintainability-gate-plan.md`（§0/§2/§4/§4.1）、`P0-brief.md`
> （scope/known_risks），并对可机械验证的断言（gate_p4 返回约定、`count_kf_entries` 行首正则、
> `_STAGED_EXCLUDE_RE`）在本机实测复核，而非仅读文本判断。
> 本文件为独立评审产出，只审不写（未修改 P1-requirements.md）。

## 评审结论

**approved**。13 条 BDD 全部通过（BDD-1..13 逐条判定见下），10 项重点核查项全部通过，
无 BLOCKER、无 needs-revision 项。

## BDD 评审（逐条判定 + 覆盖维度标注）

- BDD-1（god-file 跨越检测）：**通过** + 覆盖维度：数据✓（diff 前后行数对比） 前端✗(N/A) 多端✗ 边界✓（`before < N and after >= N` 跨越判据） 兼容✗。Given/When/Then 可二值判定（violations 含该文件= PASS）。
- BDD-2（god-file 不误伤存量）：**通过** + 覆盖维度：数据✓ 前端✗ 多端✗ 边界✓（存量 1200 行不跨越阈值线） 兼容✓（存量行为不改变）。判定锚 violations 不含该文件 = PASS，二值清晰。
- BDD-3（fuzzy-boundary Python 检测）：**通过** + 覆盖维度：数据✓（diff 新增行 + 行号） 前端✗ 多端✗ 边界✓（裸 `except:` 类型逃逸） 兼容✗。判定锚 violations 含文件+行号 = PASS。
- BDD-4（fuzzy-boundary 不误伤存量）：**通过** + 覆盖维度：数据✓ 前端✗ 多端✗ 边界✓（存量行不在 diff 新增行中） 兼容✓（存量不误伤）。判定锚二值。
- BDD-5（阈值可配置）：**通过** + 覆盖维度：数据✓（配置值 `god_file_threshold: 500`） 前端✗ 多端✗ 边界✓（480→520 跨 500） 兼容✓（默认 1000 不触发）。配置路径为 `agate-workspace/maintainability.yaml`（非 `.agate/`），符合 ADR-009。判定锚体现"配置生效性"，二值。
- BDD-6（配置缺失兜底）：**通过** + 覆盖维度：数据✓ 前端✗ 多端✗ 边界✓（配置缺失场景） 兼容✓（缺失用默认 N=1000）。判定锚"无配置仍返回有效判定 = PASS / 报错或跳过 = FAIL"，二值。
- BDD-7（三重门槛-登记缺失阻断）：**通过** + 覆盖维度：数据✓（known-violations.md 存在性） 前端✗ 多端✗ 边界✓（violations 非空） 兼容✓（exit code 返回约定 1/2/0）。判定锚 `exit code == 1 = PASS`，且明确"与 verifier/implementer 输出的任何文字无关"——BDD-9 红线对齐。
- BDD-8（登记数量硬校验）：**通过** + 覆盖维度：数据✓（登记条目数 vs violations 数） 前端✗ 多端✗ 边界✓（登记 2 < violations 3） 兼容✓。判定锚 `exit code == 1 = PASS`，不是"有文件就过"。
- BDD-9（数量对齐但评审未 approve 仍阻断）：**通过** + 覆盖维度：数据✓（数量对齐但评审态缺失/非 approved/agent=main） 前端✗ 多端✗ 边界✓ 兼容✓（agent≠main 与 gate_p4 同源）。Then 明确"不能靠'数量对齐'单独放行"——「评审未 approve」与「数量对齐」正确并列为阻断条件，非让数量对齐单独放行。
- BDD-10（三重门槛全满足才放行）：**通过** + 覆盖维度：数据✓（登记 3 + 评审 approved） 前端✗ 多端✗ 边界✓ 兼容✓（不新增第八道 provenance 审计）。判定锚 `exit code == 0 = PASS`，且登记内容不进入 provenance 审计范围，无"登记进审计"措辞。
- BDD-11（平台无关性-路径分隔符）：**通过** + 覆盖维度：数据✓ 前端✗ 多端✓（Windows `\` vs POSIX `/`） 边界✓（分隔符差异） 兼容✓（跨平台判定一致）。判定锚"两种分隔符下 violations 一致 = PASS"，二值。
- BDD-12（移动代码假阳性诚实处理）：**通过** + 覆盖维度：数据✓（diff 删除行+新增行） 前端✗ 多端✗ 边界✓（移动代码场景） 兼容✓（已知行为非缺陷，经登记吸收）。判定锚为"判定为 violation = PASS；被自动识别为移动而忽略 = FAIL"——诚实承认假阳性，非"自动识别移动而忽略"。
- BDD-13（数据源与挂载阶段对齐）：**通过** + 覆盖维度：数据✓（`git diff --cached` 数据源） 前端✗ 多端✓（P4 vs P6 阶段） 边界✓（P6 暂存区空 diff） 兼容✓（P4 挂载、P6 不挂）。Given 明确 P6 只 commit 验收文档（暂存区不含代码 diff），Then 明确"验证检测器挂载在 P4 而非 P6（若挂 P6 则读到空 diff、不产生判定）"，判定锚 P4 调用能读到代码 diff 并判定 = PASS。备注（非阻塞）：判定锚落在 P4 侧，P6 侧为空 diff 的陈述性对比（与设计文档 §4 第 13 条同构），数据源对齐语义清晰，非笼统描述。

## 隐含需求覆盖

- 数据维度：**覆盖**——known-violations 登记格式对齐 `count_kf_entries` 行首 `| N |` 计数（§2 隐含需求 4，BDD-8 依赖）；配置缺失兜底（BDD-6）；数量对齐（BDD-8/9/10）。
- 前端维度：**不适用**——`domains: [backend]`，无 UI/UX 场景，UX 分类框架与 vision 能力声明均不适用（与 objective_info 一致）。
- 多端维度：**覆盖**——BDD-11（平台路径分隔符）、BDD-13（P4/P6 阶段对齐）。
- 边界维度：**覆盖**——存量不误伤（BDD-2/4）、配置缺失（BDD-6）、移动代码假阳性（BDD-12）、空 diff（BDD-13）。
- 兼容维度：**覆盖**——check-gate.py 返回约定 1/2/0（BDD-7..10，§2 隐含需求 1）；不新增第八道审计（BDD-10）；调用链兼容（pre-commit/ci-gate-backstop 消费方，§6 同类扫描首行）。

## 裁剪评审

`risk_level: high` + `ceremony: standard`，`phases: [P1..P8]` 全阶段不裁。逐阶段理由核对：

- P3：**站得住**——"risk_level=high 时 P3 不可裁 + 先写失败测试确认红灯"，非模板套话，符合 AGENTS.md 改脚本工作流第 1 条。
- P7：**站得住**——"本次同时改 check-gate.py、phase cards、模板、配置、测试多文件，跨文件交叉核对必要"，给出本次任务特有理由。
- P8：**站得住**——"RM-AG0046 关联条目须回写 done（RM-AG0043 硬校验）+ 版本发布清单走 P8"。
- 其余 P1/P2/P4/P5/P6 理由（核心阶段 / 核心 gate 回归风险 / 实现+评审闭环 / 验证硬门槛 / 逐条对照 BDD）均与任务实际对应，非逐字抄卡片模板。

## 审声明（风险分级/裁剪声明 vs 证据）

- 暂存区证据：P1 阶段 `git diff --cached` 当前无代码改动（任务文档产出阶段，代码尚未实现），故声明核对以 P0-brief scope + 设计文档 §2 改动面为准。
- `risk_level: high`：与 P0-brief known_risks 第 1 条一致——check-gate.py 是核心 gate（所有任务 P0-P8 都经它判定），改动回归风险高，全量 pytest + consistency 0 ERROR 是硬门槛。分级与实际风险匹配。
- `ceremony: standard`：合法声明；`phases` 含 P7（P1..P8 全列），满足"ceremony=standard 时 phases 含 P7"的强制核查项。
- `packages: [agate-scripts, agate-tests, agate-phase-cards, agate-templates]`：与 P0-brief scope（新脚本 check-maintainability.py + check-gate.py 挂钩 + P4/P6 phase card + known-violations-template.md）对应，覆盖改动面。
- `domains: [backend]`：纯后端脚本/文档/测试，无前端，声明正确。

## 重点核查项逐条结论（dispatch-context 10 项）

1. 挂载阶段 P4 不挂 P6：**通过**——逐条 BDD 无"P6 挂载"/"P4/P6 均可"措辞；BDD-13 明确验证 P4 读到代码 diff、P6 读不到（空 diff）的数据源对齐。
2. 三重门槛不退回"登记即放行"：**通过**——BDD-7（登记缺失阻断）/BDD-8（数量不足阻断）/BDD-9（数量对齐但评审未 approve 仍阻断）/BDD-10（三重全满足才放行）四段闭环，BDD-9 正确并列「评审未 approve」与「数量对齐」为阻断条件。
3. 不新增第八道 provenance 审计：**通过**——BDD-10 只写"放行 + 登记内容不进审计范围"，无"登记进审计"措辞。
4. 阈值 N=1000 仅供参考可配置：**通过**——BDD-5/6 体现"默认值仅供参考可配置 + 缺失兜底"，无"协议断言该阈值"；配置路径为 `agate-workspace/maintainability.yaml`（非 `.agate/`）。
5. fuzzy-boundary 只覆盖 Python/TS：**通过**——§2 隐含需求 7 明确"其它语言项目经 gate_commands 自行补充"，无"支持所有语言"超范围承诺。
6. 移动代码假阳性是已知行为非缺陷：**通过**——BDD-12 判定锚为"判定为 violation = PASS"（诚实承认假阳性），非"自动识别移动而忽略 = PASS"。
7. check-gate.py 返回约定兼容：**通过**——BDD-7/8/9/10 判定锚均为 exit code（1/0），BDD-7 明确"与任何文字无关"，无文字描述判定。
8. 同类扫描完整性：**通过**——正文 §6 表格含 6 项（check-gate.py 消费方 / count_kf_entries 复用 / known-violations 首次引入 / maintainability.yaml 首次引入 / check-maintainability.py 不存在 / ruff E722 关系），每项有命中清单 + 本次处理/不处理 + 理由，且有回归拦截声明，非空白。
9. BDD 可二值判定、编号连续：**通过**——BDD-1..13 连续无跳号，格式 `#### BDD-NN:`，每条 Given/When/Then + 判定锚均为明确 PASS/FAIL，无中间态。
10. 裁剪声明合理性 + frontmatter 完整性：**通过**——risk_level/ceremony/phases/packages/domains/capability_requirements 均已声明且合法；ceremony=standard 时 phases 含 P7；全阶段不裁的逐阶段理由站得住（见裁剪评审）。

## 机械复核记录（本机实测，非仅文本判断）

- `check-gate.py:870-927 gate_p4`：P4-review 存在 + status=approved + agent≠main（缺 agent→2，agent=main→1）+ 暂存区含代码文件（`git diff --cached`，`_STAGED_EXCLUDE_RE` 排除 `P[0-8]-*.md` 与 `.state.yaml`）→ 最终 return 0。与 P1-requirements 隐含需求 1/2 的返回约定（1=阻断/2=WARNING/0=通过）一致。
- `agate_common.py:1015-1017 count_kf_entries`：行首 `^\|\s*[0-9]+\s*\|` 计数。与 P1-requirements §6 第二行"known-violations 复用同一计数函数、P4 评审确认列不参与机械计数"一致。
- `check-gate.py:174 _STAGED_EXCLUDE_RE`：`(^|/)P[0-8]-.*\.md$|(^|/)\.state\.yaml$`。与 BDD-13 的 P6 场景（只 commit 验收文档→暂存区无代码 diff）机制自洽。

## 结论锚点

- 13 条 BDD 全部通过：BDD-1, BDD-2, BDD-3, BDD-4, BDD-5, BDD-6, BDD-7, BDD-8, BDD-9, BDD-10, BDD-11, BDD-12, BDD-13。
- 覆盖维度逐条标注：数据/前端/多端/边界/兼容（前端维度全 N/A，因 domains=[backend]）。
- 无 BLOCKER，无 needs-revision。
- 结论：**approved**。
