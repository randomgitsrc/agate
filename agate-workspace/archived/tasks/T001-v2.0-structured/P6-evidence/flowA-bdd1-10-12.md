# BDD-1/2/3/4/5/6/7/8/9/10/12 — 流 A 字段读取可靠性 + schema 校验器实测

验收方式：本次验收独立重跑（非照抄归档）以下命令，全部实测通过，并对照 P4-implementation.md 的实现说明确认逻辑落点。

```
1..16
ok 1 CF.1 BDD-2: P1 frontmatter risk_level 用全角冒号（risk_level：high）→ 校验失败且报错含 risk_level
ok 2 CF.2 BDD-4: P1 frontmatter coupling_checklist 列表项缩进错误 → 校验失败且报错可定位
ok 3 CF.3 BDD-5: P1 frontmatter risk_level 枚举外的值（HIGH）→ 校验失败且提示 low/medium/high
ok 4 CF.4 BDD-6: P1 frontmatter 缺 risk_level（其余必填齐全）→ 校验失败
ok 5 CF.5 BDD-6: P2 frontmatter 缺 candidate_count（其余必填齐全）→ 校验失败
ok 6 CF.6 BDD-6+FIND-1: P7 frontmatter 只含 blocker_count（无任何流 A 字段）仍按 P7 schema 校验，缺 design_gap_count → 报错
ok 7 CF.7 BDD-7: P2 frontmatter candidate_count 类型错误（字符串而非 int）→ 报错含字段名 candidate_count
ok 8 CF.8 BDD-12: P1 frontmatter 字段嵌套深度 > 3 层 → 校验失败
ok 9 CF.9 FIND-5: P1 frontmatter 块仅一行全角冒号纯量（非 dict，无 YAMLError）→ 仍被硬拦截
ok 10 CF.10 BDD-8: check-frontmatter.sh 与 check-state-yaml.sh 同构——非空校验输出 → exit 1；合规文件 → exit 0
ok 11 MDF.1 BDD-1: risk_level 从 frontmatter 块读取（字段级 presence 优先）
ok 12 MDF.2 BDD-9: 旧格式（frontmatter 无 risk_level，只在正文）仍通过正则回退正确读取
ok 13 MDF.3 BDD-10: frontmatter 带引号字符串值优先于正文同名字段（证明非文本首现巧合、而是 dict 优先）
ok 14 MDF.4 BDD-3: phases 在 frontmatter 内以块式列表（每行 - Pn）声明 → 解析为空格连接列表
ok 15 MDF.5 BDD-1: 新增 op candidate_count 从 P2 frontmatter 读取（int → str）
ok 16 MDF.6 BDD-1: 新增 op packages 从 frontmatter 列表读取（空格连接）
```

## 逐条对应
- BDD-1（frontmatter 统一读取）: MDF.1（risk_level presence 优先）/ MDF.5（candidate_count int→str）/ MDF.6（packages list）+ check-gate.sh G_BDD1.1（见 bdd16-18-19-20-p6p7.md 引用的 check-gate.bats 输出第 18 行）
- BDD-2（全角冒号报错）: CF.1 — risk_level：high（全角）→ 校验失败，错误信息含 risk_level
- BDD-3（phases 块式解析）: MDF.4 — frontmatter 块式列表 '- Pn' 解析为空格连接列表
- BDD-4（缩进错误拦截）: CF.2 — coupling_checklist 列表项缩进错误 → 校验失败可定位
- BDD-5（枚举非法值拦截）: CF.3 — risk_level=HIGH（枚举外）→ 报错提示 low/medium/high
- BDD-6（缺必填字段拦截，P1/P2/P7 三类）: CF.4（P1 缺 risk_level）/ CF.5（P2 缺 candidate_count）/ CF.6（P7 只含 blocker_count 仍按 P7 schema 校验缺 design_gap_count）
- BDD-7（错误可定位）: CF.7 — P2 candidate_count 类型错误（字符串）→ 报错含字段名 candidate_count
- BDD-8（与 state-yaml 同机制接入 pre-commit）: CF.10（check-frontmatter.sh 与 check-state-yaml.sh 同构）+ 下方 pre-commit-gate.sh 源码核实
- BDD-9（旧格式回退）: MDF.2 — frontmatter 无 risk_level，正文有 → 正则回退正确读取
- BDD-10（frontmatter 优先）: MDF.3 — frontmatter 带引号字符串值优先于正文同名字段
- BDD-12（嵌套 ≤3 层）: CF.8（4 层嵌套 → 校验失败）+ 下方 schema 源码核实 MAX_DEPTH=3

## BDD-8 源码核实（pre-commit-gate.sh 挂载点，与 check-state-yaml.sh 同机制）
```
52:    bash "$AGATE_ROOT/scripts/check-state-yaml.sh" "$STATE_FILE" || exit 1
142:    # 逐个跑 check-frontmatter.sh，非空校验输出 → exit 1 拦截（坏格式 gate 直接拦，不靠主 Agent 判断）
144:    if [ -x "$AGATE_ROOT/scripts/check-frontmatter.sh" ]; then
147:                bash "$AGATE_ROOT/scripts/check-frontmatter.sh" "$TASK_DIR/$FM_NAME" || exit 1
```

## BDD-12 源码核实（MAX_DEPTH 定义）
```
104:MAX_DEPTH = 3
185:        if _value_depth(value) > MAX_DEPTH:
187:                "{}:{}: 嵌套深度超过 {} 层".format(basename, field, MAX_DEPTH)
```

## 附加验证：agate-frontmatter-check.py 异常处理 CRITICAL 修复（影响 BDD-6/7/12 的健壮性）
P4-review.md 曾发现深嵌套 risk_level 触发 RecursionError 未被捕获、gate 误判无错误放行的 CRITICAL。P4 已修复（try/except Exception 兜底 + check-frontmatter.sh fail-closed）。本次独立复现：
```
GATE FRONTMATTER: /tmp/claude-1000/-home-kity-oclab-agate--worktrees-v2-0/0017762c-52cd-4953-8bfa-89dedf49b538/scratchpad/p6verify/P1-requirements.md frontmatter 格式错误：
  - P1-requirements.md: frontmatter 处理异常（maximum recursion depth exceeded while calling a Python object）
EXIT=1
```
结论：深嵌套 risk_level（4000 层方括号）触发 RecursionError，被正确捕获并 fail-closed exit 1，不再静默放行。
