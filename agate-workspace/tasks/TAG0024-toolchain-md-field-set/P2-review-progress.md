## plan-eng-review 核验进度记录

### 步骤1：读取材料完成
- 已读 dispatch-context、review-role 定义、P1-requirements.md（29 BDD）、P2-design.md（全文 503 行）、P0-brief.md
- 开始逐项核验 6 个重点

### 步骤2：重点1核验（同源铁律落地）—— 通过
- python3 实测：importlib 加载 agate-frontmatter-check.py，取 SCHEMAS（4 key: P1-requirements.md/P2-design.md/P6-acceptance.md/P7-consistency.md）与 _check() 纯函数；用真实 P2-design.md frontmatter 深拷贝 + candidate_count=0 调用 _check()，返回 `['P2-design.md:candidate_count: 值 0 小于最小值 1']`，与设计 §3.2 声称的错误文案逐字节一致。
- 确认 agate-frontmatter-check.py / agate-md-field-get.py / check-judge-verdict.py 三文件均有 `if __name__ == "__main__": main()` 守卫（tail 验证），importlib exec_module 传入非 "__main__" 模块名不会触发 main()，动态加载零副作用，"零改动" 结构性成立。
- agate-md-field-get.py 动态加载验证：KNOWN_OPS=38，BOOL_FIELDS=3/LIST_FIELDS=6/INT_FIELDS=1/STRING_FIELDS=5/NO_FALLBACK_INT=9/NO_FALLBACK_LIST=5/NO_FALLBACK_BOOL=2/NO_FALLBACK_STRING=6/JSON_FIELDS=1，与 P1 §3 线索1 统计完全一致；criteria_total/criteria_passed/verdict_evidence/status 均不在 KNOWN_OPS 中——验证设计 §1.3 风险1 declared gap 属实。
- check-gate.py gate_p2()（第 759-809 行实测存在，agent=="main" 硬拒绝逻辑在第 789-791 行左右）与设计 §3.4 声称的"逐字节复用"一致。

### 步骤3：重点2核验（候选方案真实性）—— 通过
- 候选 B（下沉 agate_common.py）有实质权衡：需要修改两个"gate 关键、全仓每次 pre-commit 都跑"的稳定文件，且需证明搬迁后行为逐字节等价，验证成本与影响面均高于候选 A；候选 B 段落明确将此类改动定性为"5 项 issue 之外的第 6 类改动"并正确排除出候选 A 实际实现范围（§1.1 改什么表未出现 agate_common.py 重构项）——非稻草人，是有实际工程分量的备选。

### 步骤4：重点3核验（不改什么是否站得住）—— 通过
- 见步骤2 __main__ 守卫验证：三文件"零改动"声明结构性成立（动态加载只读属性，不需要预先暴露/导出机制上的任何改动）。

### 步骤5：重点4核验（minimal_validation 真实性）—— 4/5 完全准确，1 项数值错误（非阻塞）
- DEBT0020：`git rev-parse --show-toplevel` 在仓库根与 agate/scripts 子目录下均返回同一 worktree 根路径 `/home/kity/oclab/agate/.worktrees/agate-TAG0024`；`.git` 实测为文件（ASCII text）非目录——与设计声称完全一致。
- DEBT0019：真实 roadmap.md 表头行与 5 条真实数据行 split("|") 长度均为 9——与设计声称的常量完全一致。
- RM-AG0049：`grep -c "P4-review" agate/phase-cards/P4-implementation.md` 实测为 **10**（行号 90,91,92,93,94,95,97,107,110,153），设计文本两处（§1.3 风险5 与 §3.8）均声称"7 次"——**数值错误**。但结论本身（字符串确实出现，S-3 只判定"是否出现"不判定次数）不受影响，S-3 实际逻辑（`check-structure-consistency.py` 第 223 行左右 `if fname not in card_text`）已核实只做存在性判断，不因次数偏差改变判定结果——**非阻塞，记录：minimal_validation 证据引用有数值笔误，建议 architect 修正为准确次数**。

### 步骤6：重点5核验（gate_commands 拆分）—— 通过，1 项非阻塞记录
- P3/P5/P5_consistency/P5_shellcheck/P5_count/P5_ruff 均为独立 key，无 `&&` 短路链，符合强制要求。
- timeout_seconds=240 引用真实依据（.github/workflows/protocol-tests.yml 第 14 行注释"165.7s 串行"，已核实真实存在）；但 165.7×1.5=248.55，设计取整为 240（向下取整而非向上），与卡片"宁可档位定高"的指导原则方向略有偏差——**非阻塞，记录**。

### 步骤7：重点6核验（files_to_read 精准度）—— 通过
- 17 条目逐条核对，均能对应到设计正文某具体决策点（§2/§3.x），无明显冗余；docs/design-notes/design-md-field-set.md（342 行）虽大但有明确必要性说明（RM-AG0048 完整规格来源）。

### 步骤8：范围核验（29 条 BDD 全覆盖）—— 通过
- 脚本化统计 P2-design.md 全文 BDD- 引用覆盖 BDD-1~29 全部 29 条，无遗漏。

### 步骤9：dispatch_plan 批次是否真的互不重叠 —— 发现阻塞级问题
- 三批次：md-field-set-tool / check-gate-debt-fixes / phases-yaml-consistency。
- §1.1"改什么"表格中 `agate/tests/unit/test_check_gate.py` 追加用例 一行，改动点写明"DEBT0019 列数精确匹配红/绿用例、DEBT0020 非仓库根 CWD 用例、**RM-AG0049 outputs 声明用例**"，关联 BDD 标注为 **BDD-20~26**（跨 DEBT0019/20 与 RM-AG0049 两个 issue）。
- DEBT0019/20 属于 batch `check-gate-debt-fixes`，RM-AG0049 属于 batch `phases-yaml-consistency`——同一物理文件 `test_check_gate.py` 被两个声称"互不重叠、可并行"的批次同时追加用例，与设计开篇"范围重述"段落"三个 dispatch_plan 批次彼此文件不重叠（见下节改什么），可并行派发 P4"的断言矛盾。
- 已核实该文件现有 roadmap 相关测试位于第 1531-1568 行，gate_p4 相关测试位于第 2552-2673 行（区域不同，物理冲突概率低），但"文件级不重叠"这一硬性声明确实不成立，若两批次真的并行派发两个独立 P4 implementer，会产生同文件并发编辑（即使最终 diff 可能不冲突，也需要人工合并协调，与 dispatch_plan 的"可并行"设计初衷相悖）。
- **判定：阻塞（须打回 architect 修改）**——需要 architect 二选一：①将 RM-AG0049 的 test_check_gate.py 相关用例从"改什么"表格中移除或改标注只在 test_check_structure_consistency.py 落地（BDD-26 已有独立行覆盖）；②明确声明 test_check_gate.py 为跨批次共享文件，dispatch_plan 增加串行依赖或后处理合并步骤。

### 结论
- 1 项阻塞（dispatch_plan 批次文件重叠声明不实）；2 项非阻塞记录（RM-AG0049 grep 次数笔误、timeout_seconds 取整方向）。
- 最终 status: needs-revision

---

## 复评第 2 轮（trace_id: TAG0024-P2-review-rev2-20260825）

### 步骤1：读 dispatch-context-plan-eng-review-rev2.md + P2-dispatch-context-architect-rev2.md
确认本轮唯一复核重心：dispatch_plan 三批次文件零交叉修复（方案①：RM-AG0049 用例全归
test_check_structure_consistency.py）+ 2 处笔误（grep 次数 7→10、timeout 240→250）。
上一轮已通过的 5 个核验维度本轮不重做。

### 步骤2：读 P2-design.md 最新全文（506 行）
frontmatter dispatch_plan 三批次 id 未变：md-field-set-tool / check-gate-debt-fixes /
phases-yaml-consistency；开篇范围重述已改为"三个 dispatch_plan 批次彼此文件零交叉……
RM-AG0049 相关用例统一落在 test_check_structure_consistency.py，不再分散到
test_check_gate.py……可并行派发 P4"。

### 步骤3：核验 dispatch_plan 修复点（frontmatter / 开篇 / §1.1 表格三处一致性）
§1.1 表格第 40 行 test_check_gate.py 追加用例改动点已删除"RM-AG0049 outputs 声明用例"，
关联 BDD 收窄为 BDD-20~24；第 41 行 test_check_structure_consistency.py 行新增
"RM-AG0049 全部用例落地于本文件，不再分散到 test_check_gate.py（避免与
check-gate-debt-fixes 批次同文件交叉）"，关联 BDD 标注 BDD-25~26。三处表述（frontmatter/
开篇/表格）逐字一致，无矛盾。

全文 grep RM-AG0049/BDD-25/BDD-26，除 §1.1 表格、§2 候选方案陪衬提及、§3.8 详细设计、
§4 files_to_read、§6 minimal_validation、§8 完成标志外，未发现残留的
"test_check_gate.py 承载 RM-AG0049 用例"的表述。

### 步骤4：test_check_gate.py 与 test_check_structure_consistency.py 两行是否零交叉
逐文件核对 §1.1 表格全部 11 行改动点归属批次：check-gate.py 的两行改动（_check_roadmap_done
+ gate_p8）均归 check-gate-debt-fixes；phases.yaml 的两行改动（P4 outputs + P6.5 注释）均归
phases-yaml-consistency；test_check_gate.py 单独一行仅标 BDD-20~24（DEBT0019/20），
test_check_structure_consistency.py 单独一行标 BDD-25~26（RM-AG0049）——两个测试文件不再被
同时归属两个不同批次，三批次两两之间无共享文件。BDD 覆盖脚本化扫描 1-29 全覆盖，无遗漏。

### 步骤5：grep 次数与 timeout 笔误复核
§1.3 风险5（行67）与 §3.8（行335）均已改为"10 次"——已同步。但全文 grep 发现
§6 minimal_validation method 第5项（行456）仍写"出现 7 处"，是同一 grep 结果的第三处引用，
dispatch-context 只要求核对"两处"（§1.3+§3.8），此第三处未被架构师同步修正——记录为新的
非阻塞发现（不影响任何技术结论，因 S-3 只做存在性判断非计数判断）。
timeout：P3_timeout_seconds/P5_timeout_seconds 均为 250，已改。

### 步骤6：check-frontmatter.py 自检 + 抽查未改动内容
`FILE=P2-design.md python3 agate/scripts/agate-frontmatter-check.py` exit=0。
抽查候选方案A/B、§1.3 其余6条风险、§3.1-3.7/3.9/3.10详细设计、files_to_read 17条、
env_constraints、minimal_validation 其余4项、gate_commands 其余5个key，均与上一轮评审
引用的原文内容一致，未发现无关改动。

### 结论
唯一阻塞点已修复且验证成立。新增1项非阻塞记录（§6 第5项"7处"未同步为"10次"）。
判定：approved。
