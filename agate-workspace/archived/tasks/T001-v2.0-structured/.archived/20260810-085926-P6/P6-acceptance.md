---
phase: P6
task_id: T001
type: acceptance
parent: P5-verification.md
trace_id: T001-P6-20260810
status: draft
created: 2026-08-10
agent: verifier
pass: 27
fail: 1
ui_affected: false
---

# T001 — agate v2.0 结构化数据改造（A+B+C+D 四流）：P6 验收

> 验收方法：本任务是协议工程任务（非 UI），证据形式为命令输出/断言文件，非截图。
> 对每条 BDD：① 优先引用 P5-test-results/unit.md 中已实跑的对应 `ok N {测试名}` 行（已独立留痕的真实证据）；
> ② 对无直接 P3 断言的 BDD（BDD-11/13/14/24/28 等）或需要额外确认的场景，本次验收（2026-08-10）独立重跑命令/构造场景直接复现，命令输出记录在 `P6-evidence/bdd-NN.md`。
> 每条 PASS 均在对应 `P6-evidence/bdd-NN.md` 中给出可复核的命令输出片段，不是空手声称"已验证"。
> DESIGN_GAP 交叉核对：P4-implementation.md 含 7 处 `[DESIGN_GAP:]` 声明，已在相关 BDD 的证据文件中逐条标注（BDD-1/16/18/19/20/22/25/26/27），如实记录偏离内容与本次验收观察到的影响，不擅自下"偏离不影响"的结论（除已有独立测试/复现证明影响范围有限的场景，已在对应证据文件中说明依据）。

## ⚠️ 重要发现（本次验收自查步骤中暴露的严重缺陷，导致 BDD-17 判定为 FAIL）

按派发指引要求的自查步骤（"产出后跑 `check-p6-format.sh --fix docs/tasks/.../P6-acceptance.md`
做格式归一化"）执行时，发现 `check-p6-format.sh --fix` 会**破坏 P6-acceptance.md 自身合法的
frontmatter**：其 sed 逻辑对裸 `pass:`/`fail:` 开头的行做无差别替换（未排除 frontmatter 块），
把 BDD-16 要求的标准写法 `pass: 28` / `fail: 0` 篡改为 `**Summary**: PASS: 28` /
`**Summary**: FAIL: 0`，产出**非法 YAML**（`yaml.safe_load` 直接报错）。该脚本由
`pre-commit-gate.sh` 第 154 行无条件自动调用（`|| true` 吞掉失败），且执行顺序在
`check-frontmatter.sh`（第 147 行，frontmatter schema 校验）**之后**——即合法 frontmatter 先通过
校验，随后被自动 --fix 破坏，且损坏不会被重新校验，会随 commit 直接落库。这是 100% 确定性复现
（不是边界案例），完整复现步骤见 `P6-evidence/bdd-17.md`。

**本文件的应对**：为避免自身产出物被这个已知缺陷再次破坏，本次验收在发现该问题后，**未再对本文件
重跑 `check-p6-format.sh --fix`**，而是手工核对 frontmatter 合法性 + 正文逐条行格式（已用非破坏性
的 `--check` 模式确认正文格式合规）。建议主 Agent 将 BDD-17 对应的缺陷退回 P4 修复
（check-p6-format.sh 的 `--fix` 需先剥离 frontmatter 块再对正文做归一化）。

## 流 A：字段读取可靠性（BDD-1..15）

- PASS BDD-1: 机器字段从 frontmatter 统一读取（agate-md-field-get.py 双读 + check-gate.sh/check-pruning.sh 读取点），含 DESIGN_GAP 交叉标注 (bdd-01.md)
- PASS BDD-2: 全角冒号（risk_level：high）触发 pyyaml 解析错误，check-frontmatter.sh exit 1 且报错定位到具体行 (bdd-02.md)
- PASS BDD-3: phases 块式列表（- Pn 每行）被正确解析为空格连接列表，不要求内联方括号格式 (bdd-03.md)
- PASS BDD-4: coupling_checklist 列表项缩进错误，校验失败且错误信息含具体行号/列号 (bdd-04.md)
- PASS BDD-5: risk_level 枚举外的值 HIGH 被拦截，报错提示合法值 low/medium/high (bdd-05.md)
- PASS BDD-6: P1/P2/P7 三类 schema 缺必填字段（risk_level/candidate_count/design_gap_count 等）均被 exit 1 拦截，含 FIND-1 判别契约边界场景（P7 只含 blocker_count 仍按 P7 schema 校验） (bdd-06.md)
- PASS BDD-7: candidate_count 类型错误（字符串非 int）报错含字段名 candidate_count，可直接定位修复 (bdd-07.md)
- PASS BDD-8: check-frontmatter.sh 挂载 pre-commit-gate.sh 的机制与 check-state-yaml.sh 完全同构（`bash <script> <file> || exit 1`） (bdd-08.md)
- PASS BDD-9: frontmatter 无 risk_level（只在正文）时正则回退正确读取，行为与 v0.35 一致 (bdd-09.md)
- PASS BDD-10: frontmatter 与正文同名字段值不同（"high" vs "low"）时返回 frontmatter 值，frontmatter 优先 (bdd-10.md)
- PASS BDD-11: count-tests.sh 本次独立重跑输出 594（sanity.bats 6 另计），与改造前基线一致 (bdd-11.md)
- PASS BDD-12: 4 层嵌套字段被校验器拦截（"嵌套深度超过 3 层"） (bdd-12.md)
- PASS BDD-13: check-protocol-consistency.py 本次独立重跑输出 0 ERROR，CHECK 9 锚点表 37→38 全过 (bdd-13.md)
- PASS BDD-14: P2-design.md §10 存在明确声明"结构化提高解析可靠性，不改变 gate 对内容真实性的判断" (bdd-14.md)
- PASS BDD-15: 四个 gate_commands 读取工具（agate-read-gate-commands.py/agate-gate-missing-cmds.py/agate-read-p5-commands.py/agate-gate-p5-count.py）对本任务真实 P2-design.md 实测均正确读取正文 gate_commands，无回归 (bdd-15.md)

## 流 B：P6/P7 结果结构化（BDD-16..20）

- PASS BDD-16: P6-acceptance.md 正文无任何 PASS/FAIL 行时，门禁仍基于 frontmatter pass/fail 汇总判定（P6_TOTAL=2）；本条窄义验证（check-gate.sh 读取 frontmatter）独立成立，与 BDD-17 的 --fix 缺陷是不同的观察对象，交叉引用见上方"重要发现" (bdd-16.md, bdd-17.md)
- FAIL BDD-17: check-p6-format.sh 升级版的 --check 子行为（body 逐条行识别）本身工作正常，但作为整体，其 --fix 模式存在严重、确定性复现的缺陷——会把 BDD-16 要求的合法 frontmatter pass:/fail: 字段篡改为非法 YAML，且该脚本被 pre-commit 无条件自动调用、损坏后不会被重新校验。详见"重要发现"与 (bdd-17.md)
- PASS BDD-18: 总结行 `- PASS: 16`（无 BDD 编号）不计入逐条 PASS/FAIL 总数，含 DESIGN_GAP 交叉标注（旧格式回退正则宽松度差异不影响本条结论） (bdd-18.md)
- PASS BDD-19: P7 frontmatter blocker_count/deviation_critical_count 均 0 时通过，即使正文含易混淆的"[BLOCKER]: 0 条"散文也不受影响 (bdd-19.md)
- PASS BDD-20: design_gap_reviewed_count(1) < design_gap_count(2) 时基于结构化配对状态拦截，不用数量相减判定 (bdd-20.md)

## 流 C：标记状态收尾（BDD-21..24）

- PASS BDD-21: frontmatter need_confirm_resolved 逐条匹配正文描述后该 NEED_CONFIRM 不再阻塞；未声明时同一标记仍阻塞（正反两面复现） (bdd-21.md)
- PASS BDD-22: check-scope-resolved.sh 基于 frontmatter scope_resolved 非空列表判定闭环通过，含 DESIGN_GAP 交叉标注（空列表与字段不存在未区分的已知边界） (bdd-22.md)
- PASS BDD-23: PROD_TOUCHED 行首锚定检测、SCOPE+ 跨文件散文扫描代码未被结构化替换，相关测试重跑行为与 v0.35 一致 (bdd-23.md)
- PASS BDD-24: task-files.md/analyst.md/architect.md/verifier.md/4 个 phase-cards 均含可直接复制的 frontmatter 样例，全部用 yaml.safe_load 验证可解析为 dict (bdd-24.md, bdd24-yaml-validation-output.txt)

## 流 D：任务编号规则改造（BDD-25..28）

- PASS BDD-25: task_id TAG0001 匹配新正则 `^T[A-Z]{2}\d+$`，check-state-yaml.sh exit 0，含 DESIGN_GAP（33 个既有 fixture 回归）已修复确认 (bdd-25.md)
- PASS BDD-26: task_id T001 被新正则拒绝，报错提示合法格式（如 TAG0001），硬切无双格式兼容 (bdd-26.md)
- PASS BDD-27: check-changelog.sh 直接匹配完整 task_id TAG0001 成功，且不被更长编号 TAG00012 误匹配，含 DESIGN_GAP 交叉标注（fallback 移除是满足本条验收的必要调整） (bdd-27.md)
- PASS BDD-28: 本 task 全程 .state.yaml task_id 保持 T001，~/.agate（主 checkout v0.35.0）task_id 正则仍为旧版 `^T\d+$`，双工作区隔离确认未被破坏 (bdd-28.md)

**Summary**: PASS 27 / FAIL 1（P1-requirements.md 全部 28 条 BDD）

## 验收方法说明（非预判，如实记录本次执行方式）

1. 输入文件已读：P0-brief.md（环境约束）、P1-requirements.md（28 条 BDD 全文）、P2-design.md §9（BDD 覆盖映射表）/§10（语义真实性边界）、P3-test-cases.md（BDD→测试映射，含红绿历史）、P4-implementation.md（含 7 处 DESIGN_GAP）、P5-test-results/unit.md（600/600 全量 TAP 原始输出）、agate/assets/templates/task-files.md。
2. 对有直接 bats 测试覆盖的 BDD：引用 P5-test-results/unit.md 中对应的 `ok N {测试名}` 行作为已跑证据，并在 P6-evidence/bdd-NN.md 中摘录"测试名 + 断言了什么 + 为什么这构成该 BDD 的证据"。
3. 对 P3 阶段无独立可执行断言的 BDD（BDD-11/13/14/24/28）及需要额外场景验证的 BDD（BDD-2/4/5/6/7/9/10/12/16/17/18/19/20/21/22/23/25/26/27）：本次验收（2026-08-10）独立构造最小复现场景，直接调用被测脚本（check-frontmatter.sh / agate-md-field-get.py / check-gate.sh / check-scope-resolved.sh / check-state-yaml.sh / check-changelog.sh / count-tests.sh / check-protocol-consistency.py / check-p6-format.sh），记录真实命令输出，不复用旧结论。
4. DESIGN_GAP 交叉核对：P4-implementation.md 的 7 处 `[DESIGN_GAP:]` 已逐条读取，涉及的 BDD（1/16/18/19/20/22/25/26/27）在对应证据文件中标注了 DESIGN_GAP 原文摘要 + 本次验收观察到的实际影响，未替 implementer 或主 Agent 下"偏离是否可接受"的最终裁决（该裁决属 P7 一致性检查范畴）。
5. BDD-17 判定为 FAIL：本次验收严格按派发指引要求的自查命令执行时，直接、确定性地复现了一个此前未被任何 P3/P4/P5 测试覆盖的缺陷（check-p6-format.sh --fix 破坏 frontmatter），如实记录，不因"其余部分应该是对的"而放行整条 BDD。其余 27 条 BDD 的独立复现命令输出与预期行为一致，且与 P5-test-results/unit.md 的 600/600 全量结果不矛盾。
