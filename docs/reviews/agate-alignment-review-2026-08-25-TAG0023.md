---
review_date: 2026-08-25
reviewer: protocol-alignment-review
change_summary: TAG0023 机制校验补强批——check-state-transition.py 新增门槛失败事件↔retries对应性校验（检查3）、check-gate.py gate_p8() 新增 roadmap done 反查、check-debt.py 短哈希动态化、agate-frontmatter-check.py 错误提示增强，配套 5 处协议文档同步
files_changed: [agate/scripts/check-state-transition.py, agate/scripts/check-gate.py, agate/scripts/check-debt.py, agate/scripts/agate-frontmatter-check.py, agate/rules/state-transitions.md, agate/state-machine.md, agate/dispatch-protocol.md, agate/WORKFLOW.md, agate/assets/templates/dispatch-prompt.md]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | MISALIGNED |
| A2 | 脚本→文档对齐 | MISALIGNED |
| A3 | 一致性连锁 + 反向传播 | MISALIGNED（A3b 一项，A3a 其余项 ALIGNED） |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | MISALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（`agate/rules/state-transitions.md:69`）：
> **单步回退必须同步写 retries（RM-AG0042）**：单步回退（Pn→Pn-1）必须同步在 `retries[目标阶段]` 追加一条记录，不能只改 `phase` 字段；`check-state-transition.py` 对"该阶段此前已有 retries 记录、但本次回退未同步追加"的情形做机械校验并拦截（阻断，exit 1）——只手动改 `phase` 而绕过 `agate-retreat-state.py`/`agate-retreat-to.py` 的标准写入路径会被 gate 挡下。

**文档声明**（`agate/state-machine.md:613`，措辞几乎相同）：
> 单步回退（Pn→Pn-1）若**该阶段此前已有 `retries` 记录**、但本次回退未同步追加新条目 → 阻断（exit 1）

两处文档都把"阻断"的适用条件字面限定为"该阶段此前已有 retries 记录"（即 `old_retries_len > 0`）这一前提。

**脚本实现**（`agate/scripts/check-state-transition.py:299-312`）：
```python
# BDD-2：回退（含单步 diff==1，现有检查1的 diff>=2 不覆盖这种情况）且暂存版本
# retries[new_phase] 长度未超过 HEAD 版本长度（本次 commit 没有为这次回退追加记录）
# → 阻断。按 P1-requirements.md BDD-2 原文字面语义实现：不要求"该阶段此前必须已有过
# 记录"这一前提——RM-AG0042 立项证据本身（复盘中四任务 retries 全为 {}）就是"从未记录过"
# 的首次单步回退场景，若保留该前提则本任务修不到自己的立项场景（P4-review.md CRITICAL 1，
# 主 Agent 范围决策：采用方案 A，去掉 old_retries_len>0 守卫）。
if old_num > 0 and new_num > 0 and old_num > new_num:
    old_retries_len = get_old_retries_len(state_file, state_basename, new_phase)
    new_retries_len = _retries_len(current_state_data, new_phase)
    if new_retries_len <= old_retries_len:
        ...
        sys.exit(1)
```
代码明确**不要求** `old_retries_len > 0` 这一前提——`old_retries_len` 可以是 0（该阶段此前从未有过 retries 记录），只要暂存版本的 `retries[new_phase]` 长度没有比 HEAD 版本更长就阻断。测试 `test_bdd_2_first_time_retreat_both_sides_empty_retries_exit_1`（HEAD/暂存两侧 `retries: {}`）实证了这一点：首次单步回退、此前从未有过记录，仍被 exit 1 拦截。

**结论**：**MISALIGNED**
**差异**：文档字面表述的拦截前提（"该阶段此前已有 retries 记录"）比代码实际行为（"无论此前是否有过记录，只要本次没新增即拦截"）更窄。按文档字面理解，读者会以为"从未记录过 retries 的阶段首次回退"不会被拦截，但实际会被拦截。

**根因追溯**：`agate-workspace/tasks/TAG0023-mechanism-checks/P4-progress-batchA.md` 记录 batch A 首次实现时确实加了 `old_retries_len > 0` 守卫（当时测试回归失败后引入），文档措辞正是照着"有守卫"的那版代码写的。随后 `P4-review.md` CRITICAL 1 判定该守卫本身是对 `P2-design.md §2.1` BDD-2 字面表述的未声明偏离，要求去掉——代码已按方案 A 修复（去掉守卫），但 `state-transitions.md:69` 与 `state-machine.md:613` 这两处文档描述在同一批次的后续 review 修复轮中未被同步回改，停留在守卫仍存在时的旧措辞。

**建议**：把两处文档中"该阶段此前已有 retries 记录、但本次回退未同步追加"改为"暂存版本 `retries[目标阶段]` 长度未超过 HEAD 版本长度（不要求此前必须已有过记录，含首次单步回退场景）"，与代码/P2-design.md §2.1 原文字面语义对齐。

---

### A2: 脚本→文档对齐

**脚本实现**（`agate/scripts/check-gate.py`，`_check_roadmap_done()` 约 L1181-1206，调用点约 L1222-1232）：
```python
def _check_roadmap_done(task_id, roadmap_path):
    """RM-AG0043（BDD-5/6，P2-design.md §2.2 候选 A / D2 匹配算法）：按 task_id 精确匹配
    roadmap.md「关联任务」列 ... 任一「状态」列非 done → 返回 (rm_id, status) 供 gate_p8() 阻断。"""
    ...

def gate_p8(task_dir):
    ...
    # RM-AG0043（BDD-5/6）：P8 完成时反查 roadmap.md 关联 RM 条目是否已回写 done
    task_id = _load_state_yaml(task_dir).get("task_id", "")
    roadmap_path = os.path.join("agate-workspace", "roadmap", "roadmap.md")
    blocked = _check_roadmap_done(task_id, roadmap_path)
    if blocked:
        rm_id, status = blocked
        sys.stderr.write(f"GATE P8: roadmap.md 关联记录 {rm_id} 状态为 {status}（非 done），须先回写 done 再推进发布\n")
        return 1
```
这是 P8 gate 新增的一个可阻断（exit 1）判定分支。

**文档核查**（逐一读取，均无命中）：
- `agate/phase-cards/P8-release.md`：全文 `grep -n roadmap` 零命中——P8 卡片完全未提及这条新增的强制回写检查。
- `agate/WORKFLOW.md` 「Pre-commit 检查总览」表 P8 行（L301）：只列 `check-gate.py P8` 已有的 version/bump_type/CHANGELOG 等既有检查项，未提 roadmap done 反查。
- `agate/state-machine.md` P8 转移条件（L165）：完整列出了 P8→READY 的全部门槛条件（发布检查命令/bump-version/git tag/version 文件/CHANGELOG），同样没有 roadmap done 反查这一条。
- `agate/dispatch-protocol.md` P8 gate 描述（L774）：与 state-machine.md L165 内容重复，同样遗漏。

**结论**：**MISALIGNED**
**差异**：`gate_p8()` 新增的这条阻断分支（RM-AG0043）在所有理应描述 P8 gate 完整判定条件的协议文档/卡片里都没有对应说明——不是措辞不精确，是完全没提及。发布准备阶段的执行者（无论是主 Agent 还是未来的 releaser subagent）读 P8-release.md 或 state-machine.md 的 P8 门槛清单都无法预知这条新规则的存在，只能在实际触发 exit 1 时才第一次发现。
`agate-workspace/tasks/TAG0023-mechanism-checks/P2-design.md` 已充分设计此分支（dispatch-context 已知信息属实），但设计文档不能替代面向所有任务的协议卡片/权威文档。

**建议**：至少在 `agate/phase-cards/P8-release.md`（P8 门槛清单/前置条件）和 `agate/state-machine.md:165`（P8→READY 转移条件枚举）补一句"P2 声明的 `packages` 之外，若任务在 roadmap.md 有关联 RM 条目，须先回写 `状态: done`，否则 `check-gate.py P8` 阻断（RM-AG0043）"；`WORKFLOW.md` 与 `dispatch-protocol.md` 的 P8 表按现有"指向权威源"惯例视需要补充或指向 state-machine.md。

---

### A3: 一致性连锁 + 反向传播

#### A3a：已知连锁（本次改动已同步的部分）——ALIGNED

- `check-debt.py` 的 `_retreat_coverage()` 从固定 `full[:7]` 切片改为 `_short_hash()` 动态调 `git rev-parse --short`：`agate/scripts/README.md:46`、`agate/rules/state-transitions.md:87`、`agate/UPGRADING.md:445` 三处对 `--retreat-coverage` 行为的描述都只讲"git log retreat 提交 vs source: retreat 条目比对"这层语义，从未暴露"7 位定长切片"这个实现细节。属纯粹的内部 bug 修复（CI/本地 auto-abbrev 长度不一致），不改变对外行为契约，**无需同步任何文档**。
- `agate/assets/templates/dispatch-prompt.md` 新增的「P1/P2 声明写时自检」小节：`agate/dispatch-protocol.md:473` 已明确声明"项目占位符映射 / 返回前自检等均已合并进 `assets/templates/dispatch-prompt.md`，本文件不重复维护"——这是既有的"单一权威源，不重复维护副本"约定（角色文件反向传播表中"check-*.py 触发行为只需同步 WORKFLOW.md 唯一权威"是同一模式）。新小节按此约定只写在 dispatch-prompt.md 一处，**符合既有架构，不需要回填 dispatch-protocol.md/WORKFLOW.md**。

#### A3b：反向传播核查（主动推断）——1 项 MISALIGNED

按角色文件反向传播表"`agate/state-machine.md`（状态机表/规则）变更 → 应传播到 ... `agate/LIMITATIONS.md`"这条路径核查：`agate/LIMITATIONS.md`「局限 3：主 Agent 的判断力是单点故障」"现状"段落维护了一份"已落地的应对"清单（`[PROD_TOUCHED]` 客观信号 / **结构性绑定，如状态标记必须绑定 gate 验证、跨阶段回退 phase 跳变检测** / self-authored gate 证据存在性检查）。本次新增的"门槛失败事件↔retries 对应性校验"（RM-AG0042 检查3）在性质上正是同一类"结构性绑定"缓解措施的又一实例（防止主 Agent 手改 `phase` 绕过标准回退工具而不留痕），但该清单未被更新以纳入这条新机制。

（另注意：`agate/LIMITATIONS.md:66`「局限 4」提到"空返回时走 retry→PAUSED，不依赖诊断，只依赖规则遵守"，与本次 BDD-3 新增的"空返回重派信号 + retries 缺失 → WARNING"机制主题相关，但两者是不同问题——局限4谈的是"无法诊断卡死 vs 慢"，本次新增的是"事后审计是否记录"，不构成同一命题的矛盾，故不计入 MISALIGNED，仅供人工参考是否顺带更新措辞。）

**结论**：**MISALIGNED**（A3b 一项，A3a 其余项 ALIGNED）
**差异**：`LIMITATIONS.md` 局限 3"已落地的应对"清单未收录 RM-AG0042 检查3这一新增的结构性绑定机制。
**建议**：在该清单追加一句，如"（4）门槛失败事件↔retries 对应性机械校验（RM-AG0042，`check-state-transition.py` 检查3）：单步回退未同步写 retries 阻断，评审 rejected 重派/子代理空返回重派未写 retries 高优 WARNING"。不阻断本次 commit（LIMITATIONS.md 不属于 self-gate 触发面的强制项），但建议纳入后续小修。

---

### A4: 测试覆盖

**证据 1（历史全量实跑，引用）**：`agate-workspace/tasks/TAG0023-mechanism-checks/P5-test-results/unit.md`（HEAD commit `551e2017`）：
```
timeout 300s python3 -m pytest agate/tests/ -q -p no:cacheprovider --basetemp=...
1238 passed, 2 skipped in 143.29s (0:02:23)
```
判定：failed=0，与 P4 阶段主 Agent 独立跑出结果一致。同文件另确认 `check-protocol-consistency.py --strict-errors-only` exit 0（0 ERROR，321 WARNING 均为历史遗留）。

**证据 2（本次审查独立重跑，针对本次改动的 4 个脚本对应测试文件，当前 HEAD `0968e4a`）**：
```
$ python3 -m pytest agate/tests/unit/test_check_state_transition.py agate/tests/unit/test_check_gate.py agate/tests/unit/test_check_frontmatter.py -q -p no:cacheprovider
238 passed in 33.17s

$ python3 -m pytest agate/tests/unit/test_agate_debt_check.py -q -p no:cacheprovider
22 passed in 1.26s
```
`git diff HEAD --` 对本次审查的 9 个目标文件确认无未提交改动，targeted 重跑与全量结果一致，无回归。

**结论**：**ALIGNED**——双重证据（历史全量 + 本次独立 targeted 重跑），均为真实 exit code，非"应该没问题"。

---

### A5: 下游影响 + 文档传播

**下游影响（破坏性变更排查）**：`agate-workspace/tasks/active-tasks.md`「进行中的任务」表核实，当前仓库内**只有 TAG0023 自身**处于"进行中"（🔄），其余全部任务状态为 READY/归档。`check-state-transition.py` 检查3新增的 BDD-2 阻断行为（单步回退必须同步写 retries）不会影响任何其他当前活跃任务的 pre-commit；该行为变化本身是本任务的既定目标（强制标准回退工具路径），且 `P4-review.md` CRITICAL 1 已用 `test_pre_commit_hook.py::test_retreat_1_real_hook_each_step` 做真实集成测试验证无回归。

**CHANGELOG.md 标注**：`CHANGELOG.md` 顶部直接是 `## [0.61.0] - 2026-08-22`，**当前无 `[Unreleased]` 小节**——确认 TAG0023 的改动尚未写入 CHANGELOG，符合协议约定（`check-changelog.py` 仅在 P8 phase 触发，P1-P7 不检查，`WORKFLOW.md` 1.6 行）。本任务当前处于 P7 阶段，CHANGELOG 更新留待 P8 处理，本轮无需完成，符合预期。

**结论**：**ALIGNED**

---

### A6: 锚点表覆盖

**锚点表现状**（`agate/scripts/check-protocol-consistency.py` `SCRIPT_ALIGNMENT_ANCHORS`，约 L508-780）：`check-state-transition.py` 已有两条既有锚点——

```python
{"desc": "重试上限检查（MAX_RETRY）", "script": "agate/scripts/check-state-transition.py", "keywords": ["MAX_RETRY"]},
{"desc": "回退跳变检测", "script": "agate/scripts/check-state-transition.py", "keywords": ["diff", "phase_num"]},
```

`check-gate.py` 也已有多条既有锚点（`DESIGN_GAP`、`agent=main`、`DESIGN_GAP_REVIEWED` 等）。但整张表里**没有任何一条**对应本次新增的两个具体协议规则：
1. RM-AG0042 检查3（门槛失败事件↔retries 对应性校验，BDD-1~4）
2. RM-AG0043 `_check_roadmap_done()`（P8 roadmap done 反查，BDD-5/6）

`check_anchor_coverage()`（反向覆盖检查，约 L787-820）只校验"每个 gate 脚本是否**至少**出现在锚点表某一条里"，`check-state-transition.py`/`check-gate.py` 因为已有其他锚点条目而不会触发这项反向 WARNING——这正是角色文件 A6 说明里提到的局限（"结构性覆盖 ≠ 逐规则覆盖"），本次 `P5-test-results/unit.md` 里 CHECK 9 显示 PASS 并不能证明这两条新规则已被锚点表覆盖，实测确认锚点表条目本身确实缺失。

**结论**：**MISALIGNED**
**差异**：两条新协议规则（对应 `state-transitions.md:69`/`state-machine.md:613`/`state-machine.md:698 附近 BDD-1 说明，以及 `check-gate.py` 的 roadmap done 分支）未反映为锚点表的独立条目，与表里"P8 CHANGELOG 检查""SCOPE+ 追踪""DESIGN_GAP 配对"等既有条目"一条协议规则对一条锚点"的既定粒度不一致。
**建议**：追加两条锚点，例如：
```python
{"desc": "门槛失败事件↔retries 对应性校验（RM-AG0042 BDD-1~4）", "script": "agate/scripts/check-state-transition.py", "keywords": ["RM-AG0042"]},
{"desc": "P8 roadmap done 反查（RM-AG0043）", "script": "agate/scripts/check-gate.py", "keywords": ["_check_roadmap_done"]},
```

---

### A7: 设计原则一致性

**相关 ADR**：
- `ADR-002: 可判定性——gate 门槛机器可判定`（L41-64）：门槛必须由脚本 exit code 决定，不依赖主 Agent 自我报告。本次新增的检查3三条分支（BDD-1/2/3）与 roadmap done 反查均严格走 exit code（0/1，配合 stderr WARNING 文案），未引入任何依赖主 Agent 主观判断的路径，符合。
- `ADR-004: 安全网分层——hook 兜底，主动验主流程`（L97-127）：多层防线、不同强度分层是既定模式。本次 BDD-1/BDD-3 定为"高优 WARNING 不阻断"（信号源置信度较低——文件名正则/关键词扫描的启发式判定）、BDD-2 定为"阻断"（结构化数值比较，误报率低）——这种"按信号可靠度分层拦截强度"的做法与 `check-p6-evidence.py` 里 md5 精确去重阻断 vs 像素方差/average hash 相似度检测降级为 WARNING 的既有先例是同一设计范式，未发现新的、未被记录的架构决策。
- `ADR-005: 改动性质决定流程`：本次改动全部是"机制交叉/脚本行为"类改动，走的是 P0-P8 完整流程（本任务本身即为此类），与该 ADR 描述一致。

未发现需要补充新 ADR 的架构决策——"事件源置信度分层决定阻断/WARNING 强度"是既有模式的重复应用，不构成新的、独立的设计原则。

**结论**：**ALIGNED**

---

## 附：MISALIGNED 汇总（供主 Agent 修复参考）

| # | 文件 | 问题 | 建议修复 |
|---|------|------|----------|
| A1 | `agate/rules/state-transitions.md:69`、`agate/state-machine.md:613` | 拦截前提措辞（"该阶段此前已有 retries 记录"）比代码实际行为（不要求此前已有记录，含首次回退场景）窄 | 改措辞为"暂存版本长度未超过 HEAD 版本长度（不要求此前必须已有过记录）" |
| A2 | `agate/phase-cards/P8-release.md`、`agate/state-machine.md:165`（可选：`dispatch-protocol.md:774`/`WORKFLOW.md:301`） | `check-gate.py` 新增的 roadmap done 反查（RM-AG0043）未见于任何 P8 权威文档 | 在 P8 门槛清单补充一句说明 |
| A3b | `agate/LIMITATIONS.md`「局限 3」已落地应对清单 | 未收录 RM-AG0042 检查3这一新结构性绑定机制 | 追加一条清单项（非阻断，建议性） |
| A6 | `agate/scripts/check-protocol-consistency.py` `SCRIPT_ALIGNMENT_ANCHORS` | 未新增 RM-AG0042/RM-AG0043 两条协议规则对应的锚点 | 追加两条锚点条目 |

四项中 A1/A2/A6 为需修复的 MISALIGNED，A3b 为建议性（非 self-gate 强制触发文件）。按闭环规则，A1/A2/A6 应修脚本或修文档后重审；A3b 可视主 Agent 判断决定是否本轮一并处理。
