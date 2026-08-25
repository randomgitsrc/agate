# P7-alignment-fix-progress

## 1. A1 修复：agate/rules/state-transitions.md 第 69 行
状态：完成
把"该阶段此前已有 retries 记录、但本次回退未同步追加"改为"暂存版本 `retries[目标阶段]` 长度未超过 HEAD 版本长度"，并补充说明不要求此前必须已有记录、首次单步回退同样会被拦截。

## 2. A1 修复：agate/state-machine.md 第 613 行
状态：完成
同样去掉"该阶段此前已有 retries 记录"前提，改为"暂存版本 retries[目标阶段] 长度未超过 HEAD 版本长度（不要求此前必须已有过记录，含首次单步回退）→ 阻断（exit 1）"。

## 3. A2 修复：agate/phase-cards/P8-release.md
状态：完成
在「gate 规则」小节的判定项列表末尾追加一条：若任务在 roadmap.md 有关联 RM 条目须先回写「状态」列为 done，否则阻断（RM-AG0043）。

## 4. A2 修复：agate/state-machine.md 第 165 行（P8 转移条件枚举行）
状态：完成
在既有 `+` 连接的条件短语末尾追加：`+ 若 roadmap.md 有关联 RM 条目须已回写 done（RM-AG0043，check-gate.py P8 反查）`，未删除/重排原有条件。

## 5. A6 修复：agate/scripts/check-protocol-consistency.py SCRIPT_ALIGNMENT_ANCHORS
状态：完成
在「回退跳变检测」条目后追加 check-state-transition.py 的 RM-AG0042 锚点（keywords: ["RM-AG0042"]，已核实脚本内确有该关键词）；在「DESIGN_GAP 配对」条目后追加 check-gate.py 的 RM-AG0043 锚点（keywords: ["_check_roadmap_done"]，已核实脚本内确有该函数名）。均按现有字典格式插入，未改动其他条目。

## 6. A3b 修复：agate/LIMITATIONS.md「局限 3」已落地应对清单
状态：完成
在 (3) self-authored gate 证据存在性检查之后追加 (4) 门槛失败事件↔retries 对应性机械校验（RM-AG0042）条目，措辞取自审查报告建议。

## 验证命令结果
1. `timeout 30s python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` → exit 0，322 WARNING（历史遗留，非本次引入），0 ERROR。
2. `timeout 60s python3 -m pytest agate/tests/unit/test_agate_scripts_encoding.py agate/tests/unit/test_docs_assertions.py -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp_alignfix` → 15 passed。
3. `timeout 60s python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp_alignfix2` → 27 passed。

全部通过，无回归。

[PROD_NOT_TOUCHED]
