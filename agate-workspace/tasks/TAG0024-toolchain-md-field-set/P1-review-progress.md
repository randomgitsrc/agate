# P1-review 核验过程记录（requirements-review, agent≠main）

## 步骤1：读取角色定义 + dispatch-context + P0-brief
- 已读 agate/assets/review-roles/requirements-review.md（检查清单：BDD可判定性/隐含需求/跨条一致/裁剪合理性/审声明/P1纯净性；输出格式与门槛映射规则）
- 已读 P1-dispatch-context-requirements-review.md（核心约束：BDD格式/frontmatter四字段/NEED_CONFIRM/同类扫描三线索/capability三态/范围核验对齐5项issue/同源铁律核验/裁剪核验）
- 已读 P0-brief.md（5 项 issue：RM-AG0048一期/DEBT0019/DEBT0020/RM-AG0049/RM-AG0050；known_risks 强调同源铁律与回归约束）

## 步骤2：读取 P1-requirements.md 全文（287行）+ .state.yaml
- frontmatter: risk_level=medium, ceremony=standard, phases=[P1..P8,P6.5], packages=[agate-scripts,agate-rules,agate-docs,agate-tests], domains=[backend]
- .state.yaml 已核实：judge.enabled=true（与 P1 正文裁剪说明第 P6.5 条声明一致）
- [NO_NEED_CONFIRM] 出现 2 处（行25、行287），无未处理 [NEED_CONFIRM]；1 处 [SUGGEST]（BDD-17 关联）

## 步骤3：BDD 格式与编号核验（机械核对，非只读正文声称）
- grep -c "^#### BDD-" = 28；编号 1..28 连续无跳号无重复（独立 paste+awk 核对通过）
- 全部标题严格匹配 "^#### BDD-[0-9]+:" 格式，无变体

## 步骤4：同类扫描三线索——独立复算验证（不采信正文声称，重新 grep/执行代码核实）
- 线索1（get 白名单对齐）：独立 exec agate-md-field-get.py 取 KNOWN_OPS，实测 38 个 op，九组精确计数 3/6/1/5/9/5/2/6/1 与正文声称完全一致——核验通过
- 线索2（roadmap 表格解析消费点）：独立 grep split("|") 仅命中 check-gate.py；grep roadmap 命中 3 文件（check-gate.py/check-protocol-consistency.py/check-retrospective.py）；读取 check-retrospective.py:66-90 确认其用 re.search 整段匹配非列索引解析——判定与正文一致，核验通过
- 线索3（P6.5 定位消费点）：独立 grep 命中 18 文件，8 脚本+10 文档/规则，逐一核对文件名与正文清单完全一致——核验通过

## 步骤5：关键技术断言实地核验
- 读 agate/scripts/check-gate.py:1181-1230 确认 _check_roadmap_done() 用 cols[1]/cols[3]/cols[5] + len(cols)<8 判断（DEBT0019 缺陷坐实）；gate_p8() 用 os.path.join("agate-workspace","roadmap","roadmap.md") 相对 CWD 硬编码（DEBT0020 缺陷坐实）
- 读 agate/rules/phases.yaml：P4 outputs 仅含 P4-implementation.md，无 P4-review.md（RM-AG0049 缺陷坐实）；P6.5 确为与 P4/P5/P6/P7 平级的独立 list item（RM-AG0050 缺陷坐实）
- 读 agate/state-machine.md:74/152 确认明确表述"P6.5 是挂载于 P6→P7 的强门槛子阶段，非独立 phase 值"，与 phases.yaml 结构声明冲突属实
- 读 AGENTS.md「改脚本的工作流」+ agate/WORKFLOW.md 裁剪风险维度表，核对 P1 裁剪说明（P3 不裁理由/P7 不裁理由）站得住

## 步骤6：同源铁律核验（本任务核心风险点，dispatch-context 强制项）
- RM-AG0048 同源要求：BDD-15 明确声明 set 的 value 校验与 check-gate.py/agate_common 读取同一份 phases.yaml/task-files.md schema 源——核验通过
- DEBT0019 不破坏既有判定：BDD-21 明确声明列数精确匹配的既有合法表格判定结果不变（含 TAG0023 P8 回归用例）——核验通过
- DEBT0020 不破坏既有判定：发现缺口——BDD-22/23 仅覆盖"非仓库根 CWD"与"仓库根不可得"两个新场景，未见任何 BDD 显式声明"仓库根 CWD 场景下（既有正常调用路径）gate_p8 判定结果/阻断行为与修复前完全一致"。P0-brief known_risks 与 dispatch-context 均把 DEBT0019/20 并列要求同一层回归约束覆盖，DEBT0019 有 BDD-21 对应，DEBT0020 无对应 BDD——判定为需求基线不完整，按 dispatch-context 指令须打回
- 次要发现（非阻塞）：BDD-28 Then 子句排除措辞为"DEBT0019/20 明确修复的 _check_roadmap_done() 相关行"，但代码核实 DEBT0020 实际改动点在 gate_p8() 内的 roadmap_path 构造行，并非 _check_roadmap_done() 函数体内——措辞可能在 P7 diff 审查时产生边界解释分歧，建议 analyst 修改时把措辞精确化为"_check_roadmap_done() 及其调用点 gate_p8() 中 roadmap_path 定位相关行"，记录不阻塞

## 步骤7：范围核验 + 裁剪核验结论
- 28 条 BDD 精确映射 5 项 issue（BDD1-19→RM-AG0048, BDD20-21→DEBT0019, BDD22-23→DEBT0020, BDD24-25→RM-AG0049, BDD26-27→RM-AG0050, BDD28→跨issue约束），无遗漏无范围蔓延——核验通过
- 裁剪说明：phases 声明全阶段不裁剪，P3/P6.5/P7/P8 逐项理由均可对照 AGENTS.md/WORKFLOW.md 条款坐实——核验通过

## 步骤8：写入 P1-review.md，结论 status: needs-revision（DEBT0020 同源铁律 BDD 覆盖缺口，阻塞打回）

---

# P1-review 复评（第 2 轮）核验过程记录

## 步骤1：读取角色定义 + dispatch-context-rev2 + 上一轮 P1-review.md
- 已读 requirements-review.md 角色定义（无变化）
- 已读 P1-dispatch-context-requirements-review-rev2.md：核心指令——重点复核 BDD-24（新增对称锚点）结构完整性、BDD-29（原 BDD-28）排除措辞精确化、编号完整性独立复算，其余维度（隐含需求/裁剪/范围/P0-brief 时效性/同类扫描）本轮不重新展开，只抽查未改动内容是否原样未动
- 已读上一轮 P1-review.md：唯一阻塞点为 DEBT0020 缺 BDD-21 对称锚点（仓库根 CWD 既有场景判定结果不变），次要记录项为 BDD-28 排除措辞可精确化

## 步骤2：BDD 编号完整性独立复算（不采信 analyst 自述）
- `grep -oP "^#### BDD-\K[0-9]+"` 提取全部编号，Python 排序比对 `list(range(1,30))`：结果 True，count=29，dupes=[]
- 独立确认：编号 1~29 连续、无跳号、无重复
- `check-frontmatter.py` 对 P1-requirements.md 执行：exit 0

## 步骤3：BDD-24（DEBT0020 对称锚点）结构核验
- 原文（226-229 行）：Given "当前工作目录是仓库根（既有正常调用路径，含 TAG0023 P8 roadmap 回写校验覆盖的既有用例）"；When "修复后的 gate_p8() 调用 _check_roadmap_done() 定位并解析 roadmap.md"；Then "判定结果（阻断行为/rm_id/status）与修复前完全一致"
- 逐项比对 dispatch-context 要求的结构（Given 仓库根既有正常调用路径/When gate_p8()+_check_roadmap_done() 解析/Then 判定结果阻断行为/rm_id/status 与修复前完全一致）：三要素全部满足，且与 BDD-21（DEBT0019 侧对称锚点）结构完全对称（同样含 TAG0023 用例、同样"与修复前完全一致"措辞）
- 位置核验：插入在 BDD-23（仓库根不可得提示）之后、RM-AG0049 小节（原 BDD-24）之前，属于 DEBT0020 小节内的第三条 BDD，位置合理
- 核验结论：通过，阻塞点已修复

## 步骤4：BDD-29（原 BDD-28）措辞精确化核验
- 原文（257-260 行）Then 子句："除 `_check_roadmap_done()` 及其调用点 `gate_p8()` 中 `roadmap_path` 定位相关行外，两文件不含其他判定逻辑变更"
- 对照 dispatch-context 要求（措辞需区分 `_check_roadmap_done()` 本体与调用点 `gate_p8()` 的 `roadmap_path` 定位行）：措辞已精确列出两个具体位置（函数本体 + 调用点内的具体行），不再是上一轮"_check_roadmap_done() 相关行"的宽泛表述
- 核验结论：通过，措辞精确化到位

## 步骤5：编号顺延交叉核对（新增 BDD 后，原 BDD-24~28 顺延为 BDD-25~29 内容是否原样未动）
- 独立读取 BDD-25（P4 outputs 声明补全）/BDD-26（S-1/S-2 双向一致性）/BDD-27（phases.yaml 与 state-machine.md 口径一致）/BDD-28（既有判定行为不变）：内容与上一轮 review 记录的原 BDD-24/25/26/27 描述逐字对照一致，仅编号顺延 +1，正文未被误改
- 小节标题（"### RM-AG0049：phases.yaml P4 outputs 声明对齐" / "### RM-AG0050：P6.5 定位口径统一" / "### 跨issue 约束验收"）与归属关系未变

## 步骤6：抽查未改动 BDD（BDD-1~23）内容是否原样未动
- 读取 BDD-1~19（RM-AG0048 全部）、BDD-20~23（DEBT0019/DEBT0020 前三条）全文，逐条与上一轮 P1-review.md 中对每条 BDD 的转述比对：Given/When/Then 措辞与上一轮核验时完全一致，未发现误改
- 抽查覆盖：BDD-1（合法写入读回）、BDD-5（--list 一致性）、BDD-9（证据字段拒绝）、BDD-15（同源铁律核心锚点）、BDD-17（白名单并集）、BDD-20（DEBT0019 核心）、BDD-21（DEBT0019 对称锚点，未变）、BDD-22/23（DEBT0020 前两条边界场景，未变）——共抽查 9 条以上，均确认未被误改

## 步骤7：全文结构核验（章节 1-7 是否完整未破坏）
- `grep "^## \|^### "` 核对全文章节结构：1.需求复述/2.隐含需求识别/3.同类扫描/4.BDD验收条件（5个issue小节+跨issue约束）/5.能力需求声明/6.裁剪说明/7.待确认清单，与上一轮核验时的结构完全一致，无章节缺失或错位
- frontmatter（risk_level/ceremony/phases/packages/domains/需 求head等）与上一轮核验时一致，未被误改

## 步骤8：写入 P1-review.md（覆盖上一轮），结论 status: approved（两处阻塞/记录项均已对症修复，编号无误，其余内容原样未动）
