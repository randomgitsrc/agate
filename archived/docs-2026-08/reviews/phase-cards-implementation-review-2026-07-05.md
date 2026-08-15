---
review_date: 2026-07-05
reviewer: main
review_target: Phase Card 体系完整实施（commit 2e8cf77）
files:
  - agate/phase-cards/P0-P8 + README（10 文件）
  - agate/rules/state-transitions.md + review-mapping.md（2 文件）
  - agate/orchestrator-template.md（mapping 表叠加）
  - agate/state-machine.md:506（中断恢复语义更新）
  - agate/AGENTS.md（索引更新）
type: 实施评审（完整性 + 一致性 + 导航链）
method: 逐张卡片对照协议文件源规则 + 跨卡片交叉一致性检查
---

# Phase Card 体系实施评审

## 总判定

**实施完整，856 行覆盖了原 2900 行的核心执行逻辑。卡片间导航链闭合，跨阶段规则正确引用。2 个轻度不一致问题（不阻塞），1 个缺失（P0 结构不统一）。**

---

## 逐卡审查

### P0（49行）— 结构不统一

P0 是唯一不遵循 8 节模板的卡片。它的结构是"做什么 / 五字段 / 环境自检 / 任务粒度 / 推进 / loop / 下游影响"。缺少：`## 如果是首次进入`、`## 前置条件`、`## gate 规则`、`## 常见错误`节。

但这有合理性——P0 是主 Agent 亲自执行的简报阶段，不派 subagent，没有 gate 脚本，也没有前置阶段。P0 的 "首次/重试" 区分没有意义（没有 retry 计数，P0 是每次任务启动的唯一入口）。

**判定**：设计合理但不是显式的——模板不统一会轻微增加认知负担（Agent 在 P0 看到一种格式，在 P1-P8 看到另一种）。建议：P0 卡片顶部加一行 "P0 不派 subagent，结构与其他卡片不同" 或在 README 备注。

### P1（67行）— 完整

覆盖了：BDD 格式、domains/risk_level 声明、phases 裁剪、capability_requirements（三态：available/supplementable/GAP）、NEED_CONFIRM 规则、gate exit 2 原因。

**轻不一致**："裁剪跳阶"小节不存在。P1 是不可裁剪的核心阶段（已在卡片顶部说明），但没有显式的"不可裁剪"声明。其他可裁剪的卡片都有 `> 裁剪跳阶 → ...` 的说明行，P1 缺这一行。建议补："P1 不可裁剪（核心阶段）"在顶部。

**缺失**："评审"节（已在 review 中标记为已知缺口，本次不做）。

### P2（102行）— 最完整

覆盖了：候选方案 ≥2 + 例外口、四字段、files_to_read、minimal_validation、gate_commands 固化（含 P5_e2e）、C8 评审映射、常见错误含 T046 教训。

**good**：下游影响明确写了"gate_commands 在 P2 固化后 P4-P6 不能改——设计阶段是声明验证契约的唯一窗口"——这是当前全文本协议里没写清楚的约束。

### P3（63行）— TDD 红灯

覆盖了 check-tdd-red 四种 exit 码的含义（0/1/2/3）、红灯判定细节、test_code_dir 声明。

**轻不一致**：推进条件写了 "P2-review.md status: approved" 但前置条件里也写了它。可合并为前置条件或在推进条件里省略。

### P4（97行）— 实测第一张卡片

覆盖了 files_to_read 导航、上下文控制、写跑分离、C8 评审映射、P4 gate（暂存区含非 md/yaml 文件）。常见错误含 T046 相关教训。

### P5（72行）— 技术验证

正确体现了"主 Agent 亲自跑命令不派 subagent"。覆盖了 gate_commands 执行方式、紧凑输出模式、E2E 必跑规则。

**good**：常见错误直接引用了 T046 教训——"38 个单元测试全绿 + vue-tsc OK，但浏览器里图片是破的"。

### P6（85行）— 验收，含 T046 核心教训

覆盖了 vision-helper 结论绑定（blocker>0 不可用程序化指标反驳）、"先验功能再凑格式"、证据内容质量要求。

**good**：常见错误逐条对标 T046 复盘数据：用 DOM 属性替代视觉验证、凑 PASS 数量、反驳 vision 否定、用中间指标替代用户结果。P6 是 T046 教训最集中的卡片，覆盖密度合理。

### P7（61行）— 一致性

覆盖了 DESIGN_GAP 配对、SCOPE+ 闭环、跨文件一致性。简洁合理——P7 是机械交叉检查阶段。

### P8（88行）— 发布

覆盖了 bump_type、version bump、CHANGELOG、P5 重跑、READY 收尾检查四类（状态/测试/开发/生产），临时资源清单。

---

## 导航链完整性

```
1. orchestrator-template.md mapping表  → 所有9张卡片路径 ✓
2. 每张卡片末尾                                     → 需要明确指向下一张
   P0  末尾: "读 P1 卡片" ✓
   P1  末尾: 未显式指向                               ⚠️  缺显式下一张指针
   P2  末尾: 下游影响节提到后继但未显式说 "读 P3 卡片"  ⚠️
   P3-P8: 同上                                       ⚠️
```

**发现**：P0 末尾写了"读 P1 卡片"，但 P1-P8 的末尾只是"下游影响"节描述了后继阶段的需求，没有显式说"完成本阶段 → 读下一张卡片"。Agent 需要从下游影响节推断下一步。这不阻塞（下游影响节已经给了指向），但和 review 里的设计（"卡片末尾一行指向下一张"）有一致性偏差。

**判定**：轻度。Agent 能通过"下游影响"节推断下一步，且 P1-P8 都遵循 P1→P2→...→P8 的固定顺序。但建议在 P1-P8 末尾补一行 `> 完成 → 读 phase-cards/P{N+1}.md`。

---

## 规则覆盖度

### 全覆盖（每个概念至少在对应卡片出现一次）

| 概念 | P0 | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 |
|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| BDD / domains / risk_level | - | ✓ | - | - | - | - | - | - | - |
| 候选方案 ≥2 + 四字段 | - | - | ✓ | - | - | - | - | - | - |
| files_to_read 导航 | - | - | ✓ | - | ✓ | - | - | - | - |
| gate_commands 固化 | - | - | ✓ | - | - | ✓ | - | - | ✓ |
| 最小验证 | - | - | ✓ | - | - | - | - | - | - |
| C8 评审映射 | - | - | ✓ | - | ✓ | - | - | - | - |
| TDD 红灯 (check-tdd-red) | - | - | - | ✓ | - | - | - | - | - |
| 上下文控制 | - | - | - | - | ✓ | - | - | - | - |
| PROD_TOUCHED 禁止 | - | - | - | - | ✓ | ✓ | - | - | ✓ |
| 紧凑输出 | - | - | - | - | - | ✓ | - | - | - |
| vision-helper 绑定 | - | - | - | - | - | - | ✓ | - | - |
| evidence 质量标准 | - | - | - | - | - | - | ✓ | - | - |
| DESIGN_GAP 配对 | - | - | - | - | - | - | - | ✓ | - |
| SCOPE+ 闭环 | - | - | - | - | - | - | - | ✓ | - |
| CHANGELOG / bump | - | - | - | - | - | - | - | - | ✓ |
| READY 收尾 | - | - | - | - | - | - | - | - | ✓ |
| capability_requirements | - | ✓ | - | - | - | - | - | - | - |
| 裁剪 phases 声明 | - | ✓ | - | - | - | - | - | - | - |

### 显式缺失

1. **P6 卡片缺 `check-p6-evidence.sh` 检查项细节**：目前只说 `check-p6-evidence.sh` 会跑，没列出具体检查（证据目录非空、UI 截图 >1KB、md5 去重）。规则在 protocol 文件中有详细描述。不过 P6 卡片已提到"证据内容质量"要求——对执行而言够了。

2. **P7 未提 `check-scope-resolved.sh`**：SCOPE+ 闭环涉及这个脚本，但 P7 卡片只说"P1 有 [SCOPE_RESOLVED] 标记"，未提脚本。不阻塞——主 Agent 在 gate 时 hook 自己会跑这个脚本。

3. **P5 卡片缺 `pytest timeout` 经验**：T046 中 pytest 首次跑超时需要改 timeout。不算协议规则，但如果常见错误节加一条 "设置合理的 test timeout（后端可能需要 2 分钟+）"会更好。

---

## 结构一致性

| 维度 | 结果 |
|------|------|
| 8 节模板遵循度 | P1-P8 全部遵循。P0 不遵循（合理，P0 是特殊阶段） |
| 导航指针（末尾 → 下一张） | P0 有，P1-P8 缺显式指针（靠"下游影响"节隐式指向） |
| retry 上限引用方式 | 一致：每张卡片引用 `agate/rules/state-transitions.md` |
| C8 评审引用方式 | 一致：P2/P4 卡片内联简化表 + 引用 `agate/rules/review-mapping.md` |
| 常见错误风格 | 一致：逐条列举 + 可引实例（T046/T027/T019 等） |
| PROD_TOUCHED 触发规避 | 已处理：所有卡片中去掉了 PROD_TOUCHED 方括号字面量 |

---

## 和旧协议文件的关系

agate/AGENTS.md 已更新为两段式：subagent 指令 + 主 Agent 指令（指向卡片）。旧文件列表保留在 reference 节，且 orchestrator-template.md 同时保留了完整 8 文件列表和 mapping 表——CHECK 5 两锚点均 PASS。

---

## 建议清单

| # | 动作 | 严重度 |
|---|------|--------|
| 1 | P1-P8 卡片末尾补 `> 完成 → 读 phase-cards/P{N+1}.md`（P8 → 任务 DONE） | 低（导航链已有隐式指向，补显式指针只是更精确） |
| 2 | P0 卡片顶部补结构说明："P0 不派 subagent，结构与其他卡片不同" | 低（如果不补，Agent 首次从 P0→P1 时会遇到格式突变） |
| 3 | P1 顶部补"P1 不可裁剪"声明（格式对齐其他卡片的裁剪说明） | 低 |

---

## 验证结果

- 199 bats OK
- CHECK 5/9 PASS（无 ERROR）
- 0 shellcheck error
- 1 pre-existing WARNING（analyst.md:41 YAML）
- git log 干净

---

## 一句话结论

实施完整、覆盖准确。3 个建议都是格式打磨（导航显式指针 + P0 结构说明 + P1 裁剪声明），不影响功能正确性。可以发布。
