# BDD-25/26/27 — 流 D 任务编号规则改造实测

独立重跑（非引用旧记录）：
```
1..11
ok 1 SY.1 BDD-25/26: 新格式 TAG0001 校验通过；旧格式 T001 硬切拒绝（不兼容双格式）
ok 2 SY.2 缺必填字段 → 缺必填字段: xxx（回归，与流 D 编号规则无关）
ok 3 SY.3 phase 非法值 → phase 非法值（新格式 task_id 下回归，不受流 D 硬切影响）
ok 4 CL.1 check-changelog.sh 无 CHANGELOG 文件 期望 exit 0
ok 5 CL.2 check-changelog.sh CHANGELOG 无 [Unreleased] 区域 期望 exit 1
ok 6 CL.3 check-changelog.sh [Unreleased] 无 task_id 期望 exit 1
ok 7 CL.4 check-changelog.sh [Unreleased] 含 task_id 期望 exit 0
ok 8 CL.5 check-changelog.sh task_id 在历史版本 期望 exit 1
ok 9 CL.6 BDD-27: CHANGELOG 含完整新格式 task_id TAG0001 → 直接匹配成功
ok 10 CL.7 BDD-27: CHANGELOG 只含 TAG00012（另一任务的更长编号）时 TAG0001 不误匹配
ok 11 CL.8 BDD-27: 旧版短前缀提取（grep -oE 'T[0-9]+'）对新格式 TAG0001 提取为空——直接匹配已消除该摩擦
```

## BDD-25/26 源码核实（agate-state-yaml-check.py 硬切正则）
```
39:if task_id and not re.match(r"^T[A-Z]{2}\d+$", str(task_id)):
```
现行正则 `^T[A-Z]{2}\d+$`：TAG0001 匹配（BDD-25 通过），T001 不匹配（BDD-26 硬切拒绝，报错含合法格式提示）。

## 独立构造两个真实 .state.yaml 直接验证（不止依赖 bats fixture）
```
-- 新格式 TAG0001（应无错误输出）--
(无输出=校验通过)
-- 旧格式 T001（应报格式错误）--
task_id 格式错误: T001（应为 T + 2 个大写字母项目代号 + 数字，如 TAG0001）
```

## BDD-27 源码核实（check-changelog.sh 去短前缀提取）
```
14:TASK_ID_SHORT="$TASK_ID"
33:if echo "$UNRELEASED_CONTENT" | grep -qE "(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)" 2>/dev/null; then
36:# 无固定字符串 fallback：TASK_ID_SHORT 现已等于完整 TASK_ID，若再对 TASK_ID 做
39:echo "GATE CHANGELOG: [Unreleased] 区域未找到 ${TASK_ID_SHORT}（或 ${TASK_ID}）" >&2
```

## DESIGN_GAP 交叉标注（涉及 BDD-27，P4-implementation.md 流 D 声明，如实转录不裁决）
[DESIGN_GAP: check-changelog.sh 移除了 P2-design.md §3.4.2 要求'保留'的 grep -qF fallback 分支，理由是保留会导致 TAG0001 被 TAG00012 误判匹配（与 BDD-27/CL.7 直接冲突）。移除后 CL.6/CL.7/CL.8 全部转绿，CL.1-CL.5 未受影响，本次已独立复核这 8 条全部通过。]

[DESIGN_GAP: 流 D 硬切后曾额外触发 33 个既有 fixture 回归（1 单元 SY.8 + 26 pre-commit-hook + 6 dispatch-context-card），根因是这些集成测试 fixture 用旧格式 task_id 触发真实 pre-commit hook 拦截。P4-implementation.md 流 D 小节记录此为未清零的红灯，交由主 Agent/P7 裁决。但 git log 显示后续有独立提交 68e4173（wf(T001-P4-streamD-fixturefix): 修复流D硬切引发的33个既有fixture回归），本次已独立重跑全量 bats（见 P5-test-results-retry1/unit.md 及本次独立复核 count-tests.sh=597、bats 603/603），确认这 33 个用例目前全部为绿灯（SY.8/pre-commit-hook.bats/dispatch-context-card.bats 均在全量套件的 603 ok 中，无 not ok）。P4-implementation.md 流 D 小节的 DESIGN_GAP 文字本身未追加'已由后续 commit 修复'的说明，属文档滞后（非功能问题），留存供 P7 核对文档同步。]

结论：SY.1（BDD-25/26 双向）、CL.6/CL.7/CL.8（BDD-27）实测通过；独立构造的 2 个真实 .state.yaml 文件直接验证新旧格式行为符合预期；源码核实正则与短前缀移除均已落地。
