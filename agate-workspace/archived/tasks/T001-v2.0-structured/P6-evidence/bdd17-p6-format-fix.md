# BDD-17 — P6 逐条结果行格式从严 + check-p6-format.sh --fix 破坏 frontmatter 的 bug 重点复核

本次 P6 重跑的核心复核对象。上一轮验收（27 PASS/1 FAIL）发现 `check-p6-format.sh --fix` 会把 frontmatter 里合法的 `pass:`/`fail:` 字段误伤成 `**Summary**:` 散文，导致 frontmatter 从合法 YAML 变成非法 YAML（P6-gate-diagnosis.md）。P4 已修复并新增 3 条回归测试。本次独立复现原始 bug 场景，不采信上一轮/P4 自查记录。

## 复现 1：与 P6-gate-diagnosis.md 完全一致的 bug 场景（frontmatter 含 pass/fail + 正文小写 pass 行）
```
--- BEFORE ---
---
phase: P6
- PASS BDD-1: no closing frontmatter delim (a.log)---
phase: P6
task_id: T001
pass: 28
fail: 0
ui_affected: false
---

- pass BDD-2: test lowercase (x.log)

--- RUN check-p6-format.sh --fix ---
EXIT=0
--- AFTER ---
---
phase: P6
task_id: T001
pass: 28
fail: 0
ui_affected: false
---

- PASS BDD-2: test lowercase (x.log)
--- YAML VALIDATION ---
VALID YAML, parsed: {'phase': 'P6', 'task_id': 'T001', 'pass': 28, 'fail': 0, 'ui_affected': False}
CONFIRMED: pass/fail 数值未被破坏，frontmatter 仍是合法 YAML
```

## 复现 2：frontmatter 存在时正文总结行仍被正确归一化（F_P6FMFIX.2 场景）
```
---
phase: P6
task_id: T001
pass: 2
fail: 0
ui_affected: false
---

- PASS BDD-1: ok (a.log)
- PASS BDD-2: ok (b.log)
**Summary**: PASS: 2
frontmatter 仍合法，pass=2 fail=0 未被破坏
正文总结行已正确归一化为 **Summary**: PASS: 2
```

## 复现 3：无 frontmatter 闭合边界的畸形文件（F_P6FMFIX.3 场景，验证不误判）
```
---
phase: P6
- PASS BDD-1: no closing delim (a.log)```
结论：首行是 --- 但全文无第二条 --- 闭合行 → 视为无 frontmatter 块，整份文件按正文处理，'- pass' 仍被归一化为 '- PASS'，不误判为已切分（与设计的边界判定语义一致）。

## bats 自动化回归（独立重跑，非引用 P5 记录）
```
1..13
ok 1 F1 check-p6-format.sh --check: clean file → exit 0
ok 2 F2 check-p6-format.sh --check: lowercase pass → exit 1
ok 3 F3 check-p6-format.sh --fix: lowercase pass → auto-fix → exit 0
ok 4 F5 check-p6-format.sh --check: no P6 file → exit 0
ok 5 F_BDD17.1 BDD-17: check-p6-format.sh --check 行首 - PASS|FAIL BDD-NN: 格式被识别为有效逐条结果
ok 6 F8 check-p6-format.sh --check: lowercase fail: → exit 1
ok 7 F9 check-p6-format.sh --fix: lowercase fail with space → auto-fix
ok 8 F10 check-p6-format.sh --fix: 'failure' NOT matched (word boundary)
ok 9 F_BDD18.1 BDD-18: check-gate.sh P6 审计口径不把总结行（- PASS: 16，无 BDD 编号）计入逐条 PASS/FAIL 总数
ok 10 F12 check-p6-format.sh --fix: summary line - PASS：34 → **Summary**: PASS: 34
ok 11 F_P6FMFIX.1 check-p6-format.sh --fix: frontmatter 的 pass:/fail: 字段不被正文归一化 sed 误伤，仍为合法 YAML
ok 12 F_P6FMFIX.2 check-p6-format.sh --fix: frontmatter 存在时正文总结行仍被归一化为 **Summary** 格式
ok 13 F_P6FMFIX.3 check-p6-format.sh --fix: 无 frontmatter 闭合边界的畸形文件回退按正文整体处理（不误判为已切分）
```

## --check 模式对行格式从严校验（BDD-17 正面：合规行被接受）
```
ok 1 F1 check-p6-format.sh --check: clean file → exit 0
ok 2 F2 check-p6-format.sh --check: lowercase pass → exit 1
ok 5 F_BDD17.1 BDD-17: check-p6-format.sh --check 行首 - PASS|FAIL BDD-NN: 格式被识别为有效逐条结果
```

## 结论
1. BDD-17 逐条行格式从严：--check 模式独立实现，行首 `- PASS|FAIL BDD-N` 被识别为有效逐条结果，不合规格式（小写/全角/无 BDD 编号总结行）报错要求 --fix（F1/F2/F5/F8/F_BDD17.1 全部通过）。
2. 上一轮发现的 --fix 破坏 frontmatter 的 bug：本次 3 组独立复现（原始 bug 场景 + 总结行归一化场景 + 畸形边界场景）均确认已修复，frontmatter 的 pass/fail 字段在 --fix 前后保持合法 YAML 且数值不变，正文归一化行为未受影响。bug 判定：**已真实修复**，非仅自查/自报。
3. 13/13 bats 用例（含新增 F_P6FMFIX.1/2/3）实测全绿。
