# P7-dispatch-context-alignment-fix — TAG0023 修复 protocol-alignment-review 发现的 MISALIGNED 项

> 派发对象：implementer（协议文档/脚本修复，非新功能）。这是本轮的强制指令，不是参考信息。
> 任务目录：`{AGATE_WORKSPACE}/tasks/TAG0023-mechanism-checks/`
> 依据：`{project_root}/docs/reviews/agate-alignment-review-2026-08-25-TAG0023.md`（protocol-alignment-review 独立审查，A1/A2/A6 三项 MISALIGNED 需修复，A3b 建议性一并处理）

## 目标

修复 protocol-alignment-review 发现的 3 处必修（A1/A2/A6）+ 1 处建议性（A3b）不一致，均为**纯文档/数据表措辞修正**，不改变任何脚本行为逻辑（脚本行为本身是对的，是文档描述落后于代码）。

## 改动清单（4 处，逐条精确指定）

### 1. A1 修复：`agate/rules/state-transitions.md` 第 69 行附近

现文本（把"该阶段此前已有 retries 记录、但本次回退未同步追加"这个前提去掉，改成不要求此前必须有记录）：

原文大意："单步回退（Pn→Pn-1）必须同步在 retries[目标阶段] 追加一条记录...check-state-transition.py 对'该阶段此前已有 retries 记录、但本次回退未同步追加'的情形做机械校验并拦截（阻断，exit 1）"

改为：说明拦截条件是"暂存版本 retries[目标阶段] 长度未超过 HEAD 版本长度"，**不要求此前必须已有过记录**（含首次单步回退场景，这正是 RM-AG0042 立项证据本身的场景）。

### 2. A1 修复：`agate/state-machine.md` 第 613 行附近

现文本："单步回退（Pn→Pn-1）若该阶段此前已有 `retries` 记录、但本次回退未同步追加新条目 → 阻断（exit 1）"

同样去掉"该阶段此前已有 retries 记录"这个前提限定，改为"暂存版本 retries[目标阶段] 长度未超过 HEAD 版本长度（不要求此前必须已有过记录，含首次单步回退）→ 阻断（exit 1）"

### 3. A2 修复：`agate/phase-cards/P8-release.md`

在合适位置（前置条件/门槛清单类小节）补一句：P8 gate 除既有检查外，若任务在 `agate-workspace/roadmap/roadmap.md` 有关联 RM 条目（按 `task_id` 反查「关联任务」列），须先回写「状态」列为 `done`，否则 `check-gate.py P8` 阻断（RM-AG0043）。

### 4. A2 修复：`agate/state-machine.md` 第 165 行（P8 转移条件枚举行）

这是一行很长的箭头符号（`P8 --[...]--> READY`）枚举了 P8 全部门槛条件，在其中追加一个 `+` 连接的条件短语，如：`+ 若 roadmap.md 有关联 RM 条目须已回写 done（RM-AG0043，check-gate.py P8 反查）`。**只追加，不删除/不重排现有条件**，保持这行的既有格式风格（`+` 连接多个条件短语）。

### 5. A6 修复：`agate/scripts/check-protocol-consistency.py` 的 `SCRIPT_ALIGNMENT_ANCHORS` 列表（约 L508-780）

在合适位置（`check-state-transition.py`/`check-gate.py` 相关条目附近）追加两条新锚点：
```python
{"desc": "门槛失败事件↔retries 对应性校验（RM-AG0042 BDD-1~4）", "script": "agate/scripts/check-state-transition.py", "keywords": ["RM-AG0042"]},
{"desc": "P8 roadmap done 反查（RM-AG0043）", "script": "agate/scripts/check-gate.py", "keywords": ["_check_roadmap_done"]},
```
（先读现有列表附近条目的确切格式/字段名，按现有风格插入，不要臆造字段名）

### 6. A3b 修复（建议性，一并处理）：`agate/LIMITATIONS.md`「局限 3」已落地应对清单

追加一条：门槛失败事件↔retries 对应性机械校验（RM-AG0042，`check-state-transition.py` 检查3）：单步回退未同步写 retries 阻断，评审 rejected 重派/子代理空返回重派未写 retries 高优 WARNING。

## 硬约束

- **只改文档/数据表措辞，不改任何脚本的判定逻辑**（`check-state-transition.py`/`check-gate.py` 的实际代码行为已经是对的，本轮只是让文档/锚点表追上代码，不动 `if`/`sys.exit` 等判定语句本身）
- 每处改动前先读该文件对应上下文，确认精确的行号/措辞后再改（本 dispatch-context 给的是"改动方向"，不是可以直接复制粘贴的最终文案，你需要读原文后自己写出通顺、与上下文风格一致的替换文案）
- 改完后跑一遍 `timeout 30s python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` 确认仍 0 ERROR
- 改完后跑一遍 `timeout 60s python3 -m pytest agate/tests/unit/test_agate_scripts_encoding.py agate/tests/unit/test_docs_assertions.py -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp_alignfix` 确认无回归（这两个文件常检查文档/脚本文本内容的既有断言）
- 改完 `check-protocol-consistency.py` 后额外跑 `timeout 60s python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp_alignfix2`（若该文件存在）确认锚点表改动未破坏自身测试

## 输入文件

1. `{project_root}/docs/reviews/agate-alignment-review-2026-08-25-TAG0023.md`（完整审查报告，含每条 MISALIGNED 的原文引用+行号）
2. `agate/rules/state-transitions.md`
3. `agate/state-machine.md`
4. `agate/phase-cards/P8-release.md`
5. `agate/scripts/check-protocol-consistency.py`（`SCRIPT_ALIGNMENT_ANCHORS` 定义处）
6. `agate/LIMITATIONS.md`（「局限 3」小节）

## 命令超时兜底

所有命令 `timeout 30s`/`timeout 60s`（已在上方标注）。

## 产出

原地修改上述 6 处（4 个文件：state-transitions.md/state-machine.md/P8-release.md/check-protocol-consistency.py/LIMITATIONS.md，共 5 个文件，6 处改动点）。不新建文件。

## 门槛

- 6 处改动全部完成，措辞准确、与上下文风格一致
- `check-protocol-consistency.py --strict-errors-only` 仍 0 ERROR
- 相关测试无回归

## 返回给我

只返回两行：① 改动的文件路径列表；② 一句话摘要（6处修复完成，≤30字）。绝不返回文件全文。

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P7

路径：phase-cards/P7-consistency.md
---
# P7 — 一致性检查

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P7 + 源文件数 ≤5 + 无 implicit_coupling + 有 coupling_checklist（须列出至少 2 个已检查的耦合点，空清单不合规）→ 跳过，读 P8 卡片
> ⑨ P7 subagent 化

## 如果是首次进入本阶段

1. 主 Agent 派发 consistency-reviewer subagent 执行交叉检查
   1.1 写 P7-dispatch-context-consistency-reviewer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 对照 P1-P6 产出做跨文件一致性审查
3. 产出 P7-consistency.md
4. 预跑 check-gate.py P7
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P7，不要提前写 P8——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P7): {摘要}"（phase=P7，P7 产出含 P7-consistency.md）
7. P7 commit 完成后进入 P8：**phase 推进 P8 随 P8 产出 commit 一起**（P8-release.md 就绪后），不是单独 phase commit

## 如果是重试

→ 读 agate/rules/state-transitions.md 确认 retry 上限（P7 MAX=2）

## 前置条件

- [ ] P1-P6 全部产出文件就绪

## 执行方式

consistency-reviewer subagent 执行。检查清单：

1. **DESIGN_GAP 配对**：P4-implementation.md 中的 DESIGN_GAP 声明 → 必须在 P7-consistency.md 中逐条转抄 + 配 REVIEWED 标记。未配对 → gate 不通过
2. **SCOPE+ 闭环**：P1-requirements.md 有 [SCOPE_RESOLVED] 标记，确认所有 SCOPE+ 增补已纳入基线
3. **跨文件一致性**：P2 声明的 packages 与 P8 release 的 bump 范围一致？P1 的 BDD 和 P6 的验收结果数量匹配？P4 的实现路径和 P2 的方案设计吻合？
4. **未决项清零**：P1-requirements.md 无残留行首 [NEED_CONFIRM]（P6 不再有 NEED_CONFIRM）、[BLOCKER]、[DEVIATION-CRITICAL]
5. **CODE-MAP 核对**：对照 `{AGATE_WORKSPACE}/agents/CODE-MAP.md` 与 P4「新增文件核对表」逐条核对，发现依赖方向偏离标 `[CODE_MAP_DRIFT:]`（WARNING 级，不阻断）；核对通过标 `[CODE_MAP_SYNC:]`

## 实质锚点要求（N3⑨）

| gate 断言 | 实质锚点（P7 产出须包含） |
|-----------|--------------------------|
| BLOCKER=0 | DESIGN_GAP 配对项 + REVIEWED 标记 |
| CRITICAL=0 | 跨文件检查项 + 源文件节名 |
| SCOPE+ 闭环 | 条目 + SCOPE_RESOLVED |

gate 脚本校验说明：
- DESIGN_GAP_REVIEWED：P4 声明的每条 DESIGN_GAP 在 P7 产出中须有对应行含 `DESIGN_GAP_REVIEWED`
- 跨文件引用关键词：P7 产出中须含源文件节名（如 `P2§packages`、`P4§impl-path`），否则 WARNING

## 产出规格

- P7-consistency.md：一致性审查结论
- 逐条检查结果，无 [BLOCKER] 标记

`blocker_count`/`deviation_count`/`deviation_critical_count`/`design_gap_count`/
`design_gap_reviewed_count`/`code_map_new_files_count`/`code_map_reviewed_count` 写在文件头
**frontmatter**（`---` 分隔块），不写正文；正文
`[BLOCKER]`/`[DEVIATION-CRITICAL]`/`[DESIGN_GAP]`/`[DESIGN_GAP_REVIEWED]` 散文标记保留为
人类痕迹（不迁移），gate 判定改读 frontmatter 结构化计数。**可直接复制的完整样例**：
```yaml
---
phase: P7
task_id: TAG0001           # 替换为实际任务编号
type: consistency
parent: P2-design.md
trace_id: T001-P7-20260101 # {task_id}-P7-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0                  # int ≥0
deviation_count: 0                # int ≥0
deviation_critical_count: 0       # int ≥0
design_gap_count: 0                # int ≥0
design_gap_reviewed_count: 0       # int ≥0
code_map_new_files_count: 0        # int ≥0（可选，仅骨架/CODE-MAP 机制已采用时填）
code_map_reviewed_count: 0         # int ≥0（可选，语义对应 design_gap_reviewed_count）
---
```

## gate 规则

```bash
check-gate.py P7 $TASK_DIR
```

- [BLOCKER] 存在 → exit 1
- [DEVIATION-CRITICAL] 存在 → exit 1
- DESIGN_GAP 未配对（P4 有但 P7 无 REVIEWED）→ exit 1
- CODE-MAP 未配对（code_map_reviewed_count < code_map_new_files_count，或 P4 实际标记数 > code_map_new_files_count）→ exit 1（两字段均缺失时机制未采用，跳过）
- 含 DESIGN_GAP_REVIEWED 但缺跨文件引用关键词 → WARNING（不改变 exit code）
- 全部通过 → exit 0

BLOCKER → consistency-reviewer 修改 → 再验 gate → … → 通过（⑩迭代循环，review 和 gate 重试共享 retry 预算）

## 推进条件（全部满足才写 phase: P8）

- [ ] P7-consistency.md 存在
- [ ] 无 [BLOCKER] / [DEVIATION-CRITICAL]
- [ ] DESIGN_GAP 全部 REVIEWED 配对
- [ ] SCOPE+ 闭环（P1 有 [SCOPE_RESOLVED]）

## P7 输入文件数量

P7 是输入文件数量限制的例外（模式 1 单发 + 输入数量豁免特例，见 dispatch-protocol「派发编排机制」全阶段适用表），不拆分。原因：
1. 跨文件一致性比较需要全部源文件同时可见
2. 角色文件（consistency-reviewer）已列出所需输入清单
3. dispatch-context 为 subagent 提供摘要，无需逐文件全文注入

## 常见错误

1. **漏转抄 P4 的 DESIGN_GAP**：P4 implementer 声明了实现偏差但 P7 没转抄 → gate 拦截
2. **一致性检查只看标题不对内容**：P1 BDD 数 = 15，P6 PASS 数 = 15 → 数量对，但 BDD-8 的内容在 P6 里被映射到错误的验收结果
3. **裸 'BLOCKER=0' 不引用锚点**：未做实质交叉检查，只写 '一致' → gate WARNING 提醒

gate 不过 ≠ 你失败了。红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P8 发布前最后一道质量门——P7 通过后进入机械发布步骤

> 完成 → 读 phase-cards/P8-release.md
<!-- AGATE_CARD_END -->
