# P1 progress — TAG0021-structured-layer（analyst）

> 分阶段落盘：每读完一个输入文件 / 每完成一个关键步骤追加一行。

## 输入文件读取进度
- [x] 1. P0-brief.md —— 四字段齐全；issues（规则散落/解析靠 grep/agent 上下文开销/设计对策）；known_risks（双份维护漂移→S-1~S-4、一次性迁移爆炸→M0-M3、YAML 过深→schema+叙事留 md、工具链自举→双工作区、同类扫描强制、改动面极大→按 M0-M3 分批 commit）；executor_env（opencode/full network/git true）；env_constraints（/tmp 只读、danger-full-access）
- [x] 2. design-structured-layer.md —— 总体架构（YAML 权威源+md 叙事层）、Schema 草案（phases/dispatch/roles + JSON Schema）、S-1~S-6 双向 gate 表、M0-M3 迁移路径表、与现有机制关系（check-protocol-consistency 并存+可考虑合并编号空间/SELF-GATE/UPGRADING）、风险对策
- [x] 3. HANDOFF-TAG0021.md —— 双工作区纪律表；任务范围 M0-M3 交付物；核心约束 5 条；关键验证命令（--basetemp=/home/kity/oclab/dsh-workspace/ptmp）；阶段推进纪律（commit phase=产出阶段、self-gate 声明、同类扫描强制、BDD 按 M0-M3 组织）；状态 P0，分支 feat/TAG0021-structured-layer
- [ ] 4. scripts/*.py 扫描（grep md 解析点）—— 待开始
- [ ] 5. phase-cards/*.md 扫描（门槛/产出/派发字段）—— 待开始
- [ ] 6. check-protocol-consistency.py 扫描（CHECK 编号空间）—— 待开始
- [ ] 7. WORKFLOW/dispatch-protocol/state-machine/role-system —— 待开始

## 关键发现（待补）
## 扫描 1（脚本 grep md 解析点）— 完成
- 工作区脚本总计 57 个 .py；其中约 30 个对 markdown 内容做正则解析（grep 语义）
- 核心解析器族：
  - agate-md-field-get.py：frontmatter/正文字段统一读取器（risk_level/ui_affected/candidate_count/packages/domains/phases/override/跳过风险/ui_render_shape 等），check-pruning/check-gate/check-p6-evidence/check-p6-provenance/ci-gate-backstop/agate-risk-score 都经它读字段
  - gate_commands 块解析器 4 个同源正则（^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)）：agate-read-gate-commands.py / agate-read-p5-commands.py / agate-gate-p5-count.py / agate-gate-missing-cmds.py
  - check-gate.py 直写正则：P2 四字段计数（^(packages|domains|ui_affected|gate_commands):）、candidate_count、P7/P8 多正则、_md_field_get
  - agate-extract-context.py：_grep 正则族（^domains:/^risk_level:/^gate_commands:/P2/P4 字段）
  - check-protocol-consistency.py：CHECK 4 gate_commands 键抽取 + REF_RE/LINEREF_RE 引用完整性
  - check-p6-evidence.py / check-p6-provenance.py / check-p6-format.py / agate-evidence-consistency.py / check-judge-verdict.py：P6/BBD 行解析（- PASS|FAIL BDD-N、截图引用、vision/manual-review 引用）
  - check-pruning.py / check-routing.py：P1 frontmatter 正文 grep（override/coupling_checklist/internal_only/ceremony/cou}
pling_checklist 等）+ check-retrospective/check-scope-resolved（SCOPE+ 标记）

## 扫描 2（phase-cards 门槛/产出/派发字段）— 完成
- 9 张卡片（P0-P8）统一结构：前置条件（checkbox 门槛）/ 派发（角色）/ 产出规格（文件）/ gate 规则 / 推进条件 / 常见错误 / 下游影响
- P1-P8 通用入场块：首次进入（派发步骤）/ 重试（读 rules/state-transitions.md retry 上限）/ 前置条件
- retry 上限：P1=3 P2=3 P3=2 P4=3 P5=2 P6=2 P7=2 P8=2
- P2 特有机器字段：candidate_count / 四字段（packages/domains/ui_affected/gate_commands）/ gate_commands 声明/tim=out_seconds/env_constraints 边界/dispatch_plan
- P3/P6 特有：refactor 回归口径（check-tdd-red 特判、P6 regression.log reuse）
- P6 特有：P6-acceptance.md 结构（- PASS|FAIL BDD-N 行）/ P6-evidence/ / vision-helper 绑定 / P6.5 judge 复核
- P7 特有：DESIGN_GAP_REVIEWED / BLOCKER 计数 / 跨文件引用关键词 / 输入文件数量
- P8 特有：bump_type / debt_check / 版本引用文件清单 / READY 收尾检查
- M3 渲染候选字段：前置条件 checkbox 清单 / 产出规格文件清单 / 派发角色与输入输出 / gate 规则脚本+exit；叙事保留（常见错误/下游影响/首次进入）

## 扫描 3（check-protocol-consistency CHECK 编号空间）— 完成
- 当前编号空间：CHECK 1/2/3/4/6/7/8/9/10/11/12（CHECK 5 已删除，行 95 注释：8 文件必读框架不再适用，Phase Card 取代）
- report id 形如 CHECK1-yaml / CHECK9-align / CHECK10-scriptref；统计用 key = CHECK + title.split()[1]
- 新 S-1~S-6 用独立前缀不与 CHECK 冲突；与 CHECK 编号合并与否是 P2 设计决策（design §6 建议可考虑）——本 P1 建议：独立脚本+独立 S 前缀（M0 纯增量/可回退），合并评估留待 M2 提升阻断时

## 输入 7（WORKFLOW/dispatch-protocol/state-machine/role-system 数据面）— 完成
- WORKFLOW.md（476 行）：P1-P8 阶段总览表（执行角色/评审角色/门槛）= phases.yaml 的 S-1/S-2 对账靶面；核心原则 5 条；pre-commit 检查总览表 = dispatch.yaml gate 表数据
- dispatch-protocol.md（1206 行）：派发三条铁律；五模式编排+并行规则（上限 3/失败批 retry/共享文件后处理/资源密集串行）；全阶段默认模式表；任务粒度基准（输入>5/产出>3 拆分）；可判定门槛规范表（逐条 grep/命令）= dispatch.yaml gate_table 数据；verification_env 失败处理协议（止损 2 轮）
- state-machine.md（730 行）：重试上限唯一权威表（P1=3 P2=3 P3=2 P4=3 P5=2 P6=2 P7=2 P8=2；P6.5 走事件账本≤2 不占 retries.P6.5）→ phases.yaml retry_cap 数据；回退规则表（diff=1 直接退/diff≥2 PAUSED）
- role-system.md（213 行）：双层角色；评审角色机械映射表 C8（domain×risk_level → plan-eng-review/plan-design-review/plan-ceo-review/cso/design-review/qa）→ roles.yaml 数据；status 字段统一映射表；judge P6.5 强制不进 C8

## 扫描 1 定量修正（正式计数）
- 脚本总数 57（含 agate_common/resolve-entry 等基础设施）；对 markdown 内容正则解析 29 个；经 agate-md-field-get 读取链 11 个
- gate_commands 块解析同源正则 ≥5 处实现（read-gate-commands/read-p5-commands/gate-p5-count/gate-missing-cmds + check-protocol-consistency CHECK4 独立键抽取）——漂移高危（DEBT0010 同族）

## 产出与自检 — 完成
- P1-requirements.md 已写（26 KB，16 条 BDD，按 M0/M1/M2/M3 分组 + (M0)-(M3) 标题后缀，数字编号兼容 gate 正则）
- gate 风格自检：^#### BDD-[0-9]+ = 16；行首 [NEED_CONFIRM] = 0；status:.*GAP = 0；frontmatter 四必填字段 + ceremony 已声明
- P0-brief 时效性：[P0_STALE] 轻微漂移 1 处（debug_env 权限声明 vs 实际 workspace-write 沙箱），记录不阻塞
- 三组同类扫描结论已写入正文 §4（脚本 md 解析点 6 组 / 卡片字段 6 类 / CHECK 编号 1-12+5 退役）
- 能力自查：纯文档/分析类，无视觉需求，capability_requirements 无 GAP；[PROD_NOT_TOUCHED]

## 修复轮（gate P1 exit 1 → 复跑 exit 2）— 完成
- 根因：P1-requirements.md 第 78 行 4.1 表格 D 组判据列反引号代码 span 内字面量 `[NEED_CONFIRM]`，触发 check-gate.py 第 529 行（"[NEED_CONFIRM]" in p1_text and nc_blocking == 0 → 报不合规标记格式，exit 1）
- 修复：仅该处改为 `NEED_CONFIRM`（去方括号，保留反引号 span 与行内其余内容原样）；行 229 [NO_NEED_CONFIRM] 声明与行 231-233 [SUGGEST: ...] 声明原样未动；未改任何 BDD Given/When/Then 语义与 frontmatter
- 复跑：timeout 60 python3 /home/kity/oclab/agate/agate/scripts/check-gate.py P1 <task_dir>（worktree 下）→ 无"不合规的 NEED_CONFIRM 标记格式"错误行，仅 GATE P1 WARNING: 3 个 SUGGEST 项（允许，不阻塞）；gate 退出码 2（P1 正常通过码，原 exit 1 消失）
- 复核：grep `\[NEED_CONFIRM\]` 全文件 0 处；[PROD_NOT_TOUCHED]
