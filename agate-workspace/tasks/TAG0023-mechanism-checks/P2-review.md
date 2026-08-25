---
phase: P2
task_id: TAG0023-mechanism-checks
type: review
parent: P2-design.md
trace_id: TAG0023-P2-review-20260824-r3
status: approved
created: 2026-08-24
agent: plan-eng-review
---

> [PROD_NOT_TOUCHED] 本轮（复评第 3 轮，P2 retry MAX=3 最后一次预算）仅只读读取 P2-design.md /
> P2-dispatch-context-plan-eng-review-retry2.md / P2-review.md（第2轮）/ P1-requirements.md /
> plan-eng-review.md / review-mapping.md / assets/review-roles/*.md + 只读 `find`/`python3 -c`
> 正则实测 + `git`（无写操作）。无任何写操作落在生产路径。

# P2-review — TAG0023 机制校验补强批（plan-eng-review 复评第 3 轮，聚焦 BDD-1/D6 第 4 点修正）

## 架构问题（阻塞级）

无。

## 架构问题（非阻塞）

1. **枚举排除 `qa`/`investigate` 的理由与角色文件原文矛盾（应改为准确的 YAGNI 表述，而非"非本 BDD 覆盖范围"）**
   - **位置**：`P2-design.md` §2.1 正则修正第 3 点（L111）——"同理排除 `protocol-alignment-review`...`qa`/`judge`/`investigate`（均未在 34 个真实文件中观测到，且...非本 BDD 覆盖范围）"
   - **核实**：读 `agate/assets/review-roles/qa.md`（`role_id: qa, type: review, phases: [P5]`）与 `agate/assets/review-roles/investigate.md`（`role_id: investigate, type: review, phases: [any]`），两者正文均**明确写有**"本角色的'打回 / HOLD / 转向 / 有 CRITICAL 或 BLOCKER' → `status: rejected`"——这恰好是 BDD-1 要捕捉的语义（评审 rejected）。design 把 qa/investigate 与 `judge`（有独立 `judge_verdict` 事件账本这一可验证的替代机制）并列，笼统称"非本 BDD 覆盖范围"，但 qa/investigate 并无类似 judge 的替代机制说明，理由不成立
   - **影响评估**：属**假阴性**（若未来出现 `P5-dispatch-context-qa-retry1.md` 或 `investigate` 的 retry 文件，枚举不会命中，WARNING 不会触发）。但因 BDD-1 已降级为 WARNING（非阻断），且 34 个真实历史文件中从未出现过 qa/investigate 的 retry 文件（本轮已独立核实），当前无实际漏判发生，不影响本轮已修正的核心缺陷（真实历史数据假阳性）
   - **建议**：下一次接触 D6 时把排除理由改为准确表述——"qa/investigate 是合法 `type: review` 角色且有 `status: rejected` 语义，但 34 个真实文件中从未以 retry/rev 命名出现过，按 YAGNI 暂不收录，若未来出现可扩展枚举"，不要用"非本 BDD 覆盖范围"这种与角色文件原文矛盾的说法

2. **`protocol-alignment-review` 的排除理由"真出现时会被 review token 命中"经正则实测证伪**
   - **位置**：`P2-design.md` §2.1 正则修正第 3 点（L111）——"排除 `protocol-alignment-review`（该角色 `agent:` 字段实际是 `review`...真出现时会被 `review` token 命中）"
   - **核实**：用本轮新枚举正则 `^P(\d+)-dispatch-context-(requirements-review|plan-eng-review|plan-design-review|plan-ceo-review|cso|review|design-review|review-eng|review-cso)-(retry|rev)\d+\.md$` 对合成字符串 `P4-dispatch-context-protocol-alignment-review-retry1.md` 实测（Python `re.match`）→ **False**。原因：枚举正则要求角色段整体精确等于某个 alternative（`^...$` 全字符串锚定），`protocol-alignment-review` 作为一个整体 token 不等于 `review`，不会被"review"子串命中——这是本轮 design 自身推理的一处技术性错误
   - **影响评估**：同上，属假阴性，但 34 个真实文件中从未以 `protocol-alignment-review` 这一 token 出现过（本轮已独立核实），当前无实际漏判。不影响核心缺陷修正
   - **建议**：下一次接触 D6 时把这条排除理由改为"34 个真实文件从未见此 token，YAGNI，非'会被 review 命中'"，避免下游读者依赖一个已被证伪的技术论断

## 测试缺口

1. 沿用非阻塞发现①②：若后续任务扩展枚举收纳 qa/investigate，需为其补充正/负样本单测（当前 §4 完成标准表 BDD-1 行的正负样本均未覆盖这两个角色，因为二者本就未被收录，非本轮范围）
2. RM-AG0044 的 BDD-9（连续 5 次 CI 稳定）中途失败 1 次是否清零重数——延续第 1/2 轮已提出的非阻塞测试缺口，本轮未见新增修订，继续保留供 P3/P4 参考（非阻塞）

## 锁定决策

- **本轮聚焦的 4 点修正逐条独立验证结论**：
  1. **新正则假阳性/假阴性核实（通过）**：独立重跑 `find` 全仓统计（不采信 architect 自述），确认 34 个历史文件（排除本轮自身新产生的 `P2-dispatch-context-architect-retry2.md` + `P2-dispatch-context-plan-eng-review-retry2.md` 两个文件）；用原宽松正则复现 15/19，用新枚举正则复现 13/21——与 architect 声称的数字完全一致（可复现，非巧合）。逐一核对 13 个匹配文件的 frontmatter/正文，11 个有 frontmatter 者全部为真实评审角色（requirements-review/plan-eng-review/review/cso），TAG0023 自身 2 个无 frontmatter 文件核实为本任务真实历史评审轮次。21 个不匹配文件中含"review"子串的仅 2 个，恰好是已知的 2 个假阳性（T001 implementer-review-fix / TAG0016 consistency-reviewer），其余 19 个不匹配文件角色均非评审角色——**新正则未引入新假阳性，"review"子串维度未发现新遗漏**
  2. **枚举完整性核对 review-mapping.md（部分通过，见上方非阻塞发现①②）**：C8 表内 plan-eng-review/review/plan-design-review/design-review/cso/plan-ceo-review 均在枚举内，覆盖完整；但发现枚举遗漏了 `qa`/`investigate` 两个同样具备 `status: rejected` 语义的 `type: review` 角色，且 `protocol-alignment-review` 的排除理由经正则实测证伪（技术性错误，非方向性错误）。均为假阴性风险，因 BDD-1 已是 WARNING 级且当前无实际历史命中，判定为非阻塞
  3. **WARNING 降级是否符合 P1 BDD-1 双路径（通过）**：读 `P1-requirements.md` L161 原文——"Then 校验以非 0 退出码（阻断）或高优先级 WARNING 输出提示...（两种拦截强度实现路径均满足本条锚点，具体强度由 P2 定案，见 §5 D1）"——WARNING 明确是 P1 本就允许的选项，不是本轮临时松绑验收标准，D1 的降级决策站得住
  4. **残余边界诚实度/兜底路径可行性（基本通过，有一处遗漏）**：D6 已诚实承认"未来新角色恰好撞上已知 token"这一假阳性类残余风险，并给出"P4 交付物固化协议明文 + 线上运行验证无新假阳性后可升级"的具体后续路径（点名 P4 阶段、点名固化对象、点名升级前提），不是模糊的"以后再说"；但残余边界段落**只谈了假阳性维度（碰撞风险），未同步承认假阴性维度（枚举遗漏 qa/investigate 等未被观测角色）**——这是本轮新发现的遗漏，已记入非阻塞发现①，不影响本次 approved 结论
- **round 2 核心阻塞问题已修正**：round 2 的阻塞理由是"BDD-1 定阻断级的依据（'零假阳性'论证）经复核不成立，且论证用的统计数字本身双方对不上"。本轮 architect 用两个动作应对：①正则收紧为 C8 角色 token 精确枚举，独立验证确认两个已知假阳性均被排除、无新假阳性；②校验强度由阻断降为 WARNING，不再依赖"正则 100% 准确"这一无法证明的强假设，转而依赖"WARNING 仅提示不阻断"的容错设计。两个动作共同解除了 round 2 的阻塞理由——不需要 100% 准确的枚举去支撑一个已经不追求 100% 阻断力的校验强度
- **本轮未重新评审的既有通过项延续第 1/2 轮结论**：D2/D3/D4/D5/BDD-2/BDD-3/BDD-4/其余 6 个候选方案/SELF-GATE 处理纪律/gate_commands——本轮 diff 范围（D6 正则收紧 + D1 强度下调 + 残余边界措辞）与这些项目无交集，第 1/2 轮"锁定决策"结论继续有效

## 结论

**status: approved**。round 2 的阻塞理由（BDD-1"零假阳性"论证不成立、且用该论证支撑阻断级判定）已被本轮"正则收紧 + 强度降为 WARNING"的组合动作实质解除，经独立复算验证（不采信 architect 自述数字）确认无新假阳性、无"review"子串维度的新遗漏；WARNING 路径经核对 P1-requirements.md 原文确认是本就允许的选项，非临时松绑。本轮独立核查中额外发现两处枚举完整性/自身推理层面的瑕疵（qa/investigate 的排除理由与角色文件原文矛盾；protocol-alignment-review 的"会被 review 命中"论断经正则实测证伪），均为假阴性性质、WARNING 级、当前无实际历史命中，记为非阻塞架构问题供后续迭代参考，不影响本次批准。
