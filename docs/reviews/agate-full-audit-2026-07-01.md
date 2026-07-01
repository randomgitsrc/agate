# agate 协议-脚本对齐审查（第一批：裁剪条件 + 状态转移）

审查日期：2026-07-01
审查范围：state-machine.md / dispatch-protocol.md ↔ scripts/check-pruning.sh / scripts/check-state-transition.sh

## 进度

- [state-machine.md] 裁剪条件表 L163-171；MAX_RETRY 表 L428-437（P1=3,P2=3,P3=2,P4=3,P5=2,P6=2,P7=2,P8=2）；回退跳变 L407-411（|diff|>=2 强制 PAUSED）
- [dispatch-protocol.md] 门槛表 L568-577；可判定门槛规范含 P1→P2 risk_level 必须存在；P5/P6 gate 命令固化 B7；裁剪条件在 check-pruning.sh 验证
- [check-pruning.sh] 检查1-7：risk_level 必填、P2 不可裁（三例外口）、P6 不可裁（no_behavior_change）、P3 high 不可裁、P7 源码≤5+无 implicit_coupling、P8 internal_only、裁剪理由"跳过风险"
- [check-state-transition.sh] MAX_RETRY 硬编码=3；回退跳变 diff>=2 降级 WARNING 不 exit 1；重试超限检查按阶段统一

## 对比判断

- [state-machine.md] 裁剪表 L163-171（P2/P3/P6/P7/P8 条件）；MAX_RETRY 表 L428-437（按阶段独立：P1=3,P2=3,P3=2,P4=3,P5=2,P6=2,P7=2,P8=2）；回退跳变 L407-411（|next-current|>=2 强制 PAUSED，P5→P4 例外）
- [dispatch-protocol.md] 门槛表 L568-577（gate_commands 从 P2-design.md 读取，B7 固化）；裁剪检查全景 L599（P2.7-P2.9 check-pruning.sh）；状态转移检查 L598（P2.3-P2.5 check-state-transition.sh）
- [check-pruning.sh] 检查2=P2例外口(legacy/design_trivial/follows_existing_pattern)；检查3=P6需no_behavior_change；检查4=P3 high不可裁；检查5=P7源码≤5且无implicit_coupling；检查6=P8需internal_only:true；检查7=裁剪理由需"跳过风险:"
- [check-state-transition.sh] MAX_RETRY=3（硬编码，不区分阶段）；回退跳变 diff>=2 → WARNING 不 exit 1（注释明说降级）；重试超限 → phase 必须是 PAUSED

## 对比判断

- [state-machine.md] 裁剪条件表 L163-171；MAX_RETRY 表 L428-437；回退跳变规则 L407-411
- [dispatch-protocol.md] 门槛表 L568-577；P2.7-P2.9 hook 描述 L599
- [check-pruning.sh] 7 项检查：P2/P3/P6/P7/P8 裁剪条件 + override + 跳过风险
- [check-state-transition.sh] 回退跳变 WARNING（不拦截）+ MAX_RETRY=3 硬编码

## 对比判断

- [state-machine.md] 裁剪表 L163-171、MAX_RETRY 表 L428-437、回退跳变 L407-411
- [dispatch-protocol.md] 门槛表 L568-577、P2.7-P2.9 节 L599
- [scripts/check-pruning.sh] 检查 1-7 对应 P2/P3/P6/P7/P8 裁剪条件 + override 一致性
- [scripts/check-state-transition.sh] MAX_RETRY=3 硬编码、回退跳变 WARNING 不拦截

## 对比判断

- [state-machine.md] 裁剪表 L163-171（P2/P3/P6/P7/P8 各自条件），MAX_RETRY 表 L428-437（按阶段独立 P1=3/P2=3/P3=2/P4=3/P5=2/P6=2/P7=2/P8=2），回退跳变 L407-411（|next-current|>=2 → 强制 PAUSED）
- [dispatch-protocol.md] 门槛表 L568-577（P1-P8 各阶段门槛命令），P5/P6 gate 命令固化 B7 L623-626
- [check-pruning.sh] 检查 1-7：risk_level/P2例外口/P6/P3/P7/P8/跳过风险 + P2.9 override 一致性
- [check-state-transition.sh] 硬编码 MAX_RETRY=3，回退跳变>=2 仅 WARNING 不拦截，重试超限检查用 retries 列表长度

## 对比判断


## 对比判断

### A1 对比：MAX_RETRY 上限
- 文档（state-machine.md:428-437）：按阶段独立
  - P1=3, P2=3, P3=2, P4=3, P5=2, P6=2, P7=2, P8=2
- 脚本（check-state-transition.sh:12）：`MAX_RETRY=3` 硬编码，不区分阶段
  - Python 检查逻辑（L80-82）：`if isinstance(attempts, list) and len(attempts) >= max_retry`，对所有阶段统一用 3
- 结论：MISALIGNED
  - 对 P3/P5/P6/P7/P8（应为 2）：脚本允许 3 次重试才触发，比文档宽松 1 轮
  - 对 P1/P2/P4（应为 3）：恰好对齐
  - 影响：P3/P5/P6/P7/P8 的重试上限被放宽，违反"少轮次"设计意图

### A2 对比：回退跳变处理
- 文档（state-machine.md:407-411）：
  - `若 |next_phase_num - current_phase_num| >= 2（跨 ≥2 阶段回退）→ 强制 PAUSED，报告"跨 N 阶段回退，需人工确认"`
  - 例外：P5→P4（差 1，正常回归）不需要 PAUSED
- 脚本（check-state-transition.sh:58-68）：
  - `diff=$((old_num - new_num))`；`if [ "$diff" -ge 2 ]` → 仅 `echo WARNING`，不 exit 1
  - 注释明确："降级 WARNING，不 exit 1"
- 结论：MISALIGNED
  - 文档要求"强制 PAUSED"（拦截），脚本只警告不拦截
  - 脚本注释自称是"O1 修复"降级，待 .gate-history.jsonl 积累后改——但文档未提及此降级
  - 影响：跨多阶段回退（如 P6→P1）不会被 gate 拦截，违反 T019 教训防护

### A3 对比：裁剪 P2 条件
- 文档（state-machine.md:164）：不可裁。例外口 `design_trivial: true` / `follows_existing_pattern: [参照文件]` / `legacy_p2_pruned: true`
- 脚本（check-pruning.sh:46-60）：检查 2
  - `if ! echo "$PHASES_DECLARED" | grep -qw 'P2'` → 检查三个例外口字段，均不匹配则报错
  - 三个例外口字段与文档完全对应
- 结论：ALIGNED

### A4 对比：裁剪 P3 条件
- 文档（state-machine.md:165）：`需 risk_level=low（high 风险不可裁）`
- 脚本（check-pruning.sh:69-74）：检查 4
  - `if [ "$RISK_LEVEL" = "high" ]; then ERRORS+=...`
  - 只拦截 high，对 medium 放行
- 结论：MISALIGNED（语义偏差）
  - 文档字面"需 low"——读作"只有 low 才可裁"，medium 不应允许
  - 脚本读作"high 不可裁"——medium 默认放行
  - 影响范围有限（medium 是中间态），但与文档字面不一致
  - NEEDS_HUMAN_REVIEW：文档"需 low"是否应严格解读为"medium 不可裁"？若文档本意是"high 不可裁，medium/low 可裁"，则脚本对齐，文档措辞需修正

### A5 对比：裁剪 P6 条件
- 文档（state-machine.md:166）：不可裁（除非 no_behavior_change: true）
- 脚本（check-pruning.sh:62-67）：检查 3
  - `if ! grep -q 'no_behavior_change:\s*true'` → 报错
- 结论：ALIGNED

### A6 对比：裁剪 P7 条件
- 文档（state-machine.md:167）：`需源码文件数 ≤ 5 AND 无 implicit_coupling 声明`
- 脚本（check-pruning.sh:76-94）：检查 5
  - R4(a)：`git diff --cached --name-only | grep -cvE '...'` 计源码文件数，`> 5` 报错
  - R4(b)：`if grep -qE '^implicit_coupling:'` → 报错
- 结论：ALIGNED
  - 文件数过滤正则排除了 docs/tasks、.state.yaml、P{n}-*.md、隐藏文件、CHANGELOG——合理
  - implicit_coupling 检查字段存在性即报错，与文档"无 implicit_coupling 声明"一致

### A7 对比：裁剪 P8 条件
- 文档（state-machine.md:168）：`需声明 internal_only: true + 理由`
- 脚本（check-pruning.sh:96-101）：检查 6
  - `if ! grep -qE '^internal_only:\s*true'` → 报错
  - 未检查"理由"字段
- 结论：MISALIGNED（轻微）
  - 文档要求"internal_only: true + 理由"两项，脚本只查第一项
  - 影响：可声明 internal_only: true 但不写理由即通过，违反文档"须含理由"
  - 修复建议：追加 `&& grep -qE '^internal_only_reason:' "$P1_FILE"` 或类似

### A8 对比：裁剪理由"跳过风险"评估
- 文档（state-machine.md:170）：`每条裁剪须含"跳过风险:"评估。没有评估风险的裁剪 = 无效裁剪`
- 脚本（check-pruning.sh:103-108）：检查 7
  - 触发条件：`if ! P2 || ! P3 || ! P7 || ! P8`（即 P2/P3/P7/P8 任一被裁剪）
  - 检查内容：`grep -qE '跳过风险:' "$P1_FILE"`
- 结论：MISALIGNED（轻微）
  - 文档说"每条裁剪"——P6 裁剪也应需要"跳过风险"评估
  - 脚本条件漏了 P6（`! echo "$PHASES_DECLARED" | grep -qw 'P6'`）
  - 影响：P6 裁剪时（no_behavior_change: true）不强制写"跳过风险"
  - 修复建议：在 if 条件中追加 `|| ! echo "$PHASES_DECLARED" | grep -qw 'P6'`

### A9 对比：P2.9 override 校验
- 文档（state-machine.md:175-176）：若主 Agent 决定不执行 P1 声明的裁剪（保留被裁剪的阶段），必须在 P1-requirements.md 追加 override 字段
- 脚本（check-pruning.sh:32-37, 110-135）：
  - HAS_OVERRIDE 检查 `^override:` 字段存在性
  - 对每个被声明裁剪的阶段，检查 task 目录下是否有该阶段产出文件
  - 有产出但无 override → 报错
- 结论：ALIGNED
  - 逻辑与文档一致：声明裁剪但实际执行了 → 必须 override

### A10 对比：重试超限后的 PAUSED 强制
- 文档（state-machine.md:86,92,96,112,121,126 等）：`retry>=MAX → PAUSED`
- 脚本（check-state-transition.sh:72-90）：
  - 若某阶段 retries 列表长度 >= MAX_RETRY 且 new_phase != PAUSED → exit 1
- 结论：MISALIGNED（承接 A1）
  - 逻辑结构对齐（超限则必须 PAUSED），但因 MAX_RETRY 硬编码 3（见 A1），对 P3/P5/P6/P7/P8 的判定阈值错误
  - 即：P5 重试 2 次时文档要求 PAUSED，脚本要到 3 次才拦截

### A11 对比：状态转移合法 phase 白名单
- 文档（state-machine.md:69）：状态集合 {P0..P8, READY, DONE, PAUSED}
- 脚本（check-state-transition.sh:51-53）：`case "$new_phase" in ""|PAUSED|READY|DONE) exit 0 ;;`
  - 即空/PAUSED/READY/DONE 直接放行，不检查跳变
- 结论：ALIGNED
  - 这些终态/暂停态无需跳变检查，合理放行

### A12 对比：回退跳变方向
- 文档（state-machine.md:407-411）：`|next_phase_num - current_phase_num| >= 2`——绝对值，双向
- 脚本（check-state-transition.sh:62-63）：`diff=$((old_num - new_num))`；`if [ "$diff" -ge 2 ]`
  - 只检查 old > new（回退），不检查 new > old+2（前向跨阶跳）
- 结论：MISALIGNED（轻微）
  - 文档用绝对值，脚本只查回退方向
  - 前向跨阶跳（如 P2→P5，跳过 P3/P4）不会被拦截
  - 但前向跳变协议另有阶段产出文件检查兜底（P5 gate 会因缺 P3/P4 产出失败）
  - NEEDS_HUMAN_REVIEW：文档"回退跳变"标题（L407）特指回退，但 L408 用绝对值表述——文档自身措辞有歧义

