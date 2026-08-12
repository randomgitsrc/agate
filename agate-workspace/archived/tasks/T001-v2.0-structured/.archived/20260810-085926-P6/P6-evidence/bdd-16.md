# BDD-16: P6 汇总（pass/fail/ui_affected）声明于 frontmatter

## P5 测试证据
- `ok 201 G_BDD16.1 BDD-16: check-gate.sh P6 frontmatter 声明 pass/fail 汇总时门禁基于该汇总判定（非正文 grep 计数）`

## 本次验收独立复现
构造一份 P6-acceptance.md：frontmatter 声明 `pass: 2, fail: 0, ui_affected: false`，**正文完全不含
任何 `- PASS`/`- FAIL` 逐条行**（刻意排除正文计数的可能性，只留一句无格式的说明文字）：
```yaml
---
phase: P6
pass: 2
fail: 0
ui_affected: false
---
Body has NO PASS/FAIL lines at all (frontmatter-only summary).
```
执行：
```
$ bash agate/scripts/check-gate.sh P6 <TASK_DIR>
GATE P6: 证据目录非空，FAIL=0，NC=0，P6_TOTAL=2。BDD 总数对照由 check-p6-provenance.sh 审计 3 自动执行。
REAL EXIT=2   (P6 gate 的成功码，参见 G6.5 "全 PASS + 证据目录非空 期望 exit 2")
```
`P6_TOTAL=2` 精确等于 frontmatter 的 `pass(2)+fail(0)`，而正文没有任何逐条 PASS/FAIL 行可供
grep 计数——这证明门禁确实是"基于 frontmatter 声明值判定（FAIL=0 且 total>0）"，而非从正文
grep 计数（正文根本没有可 grep 的行）。

## 判定
PASS

## 交叉引用：check-p6-format.sh 的已知缺陷（详见 bdd-17.md）
本条验证的是 check-gate.sh 在读取一份"完好"frontmatter 时的行为（已证实正确）。但本次验收另外
发现：`pre-commit-gate.sh` 在真实 commit 流程中会紧接着自动跑 `check-p6-format.sh --fix`，该脚本
存在缺陷会把本条 BDD 要求的 `pass:`/`fail:` frontmatter 字段破坏成非法 YAML（完整复现与根因见
bdd-17.md，本次验收已将 BDD-17 判定为 FAIL）。即：本条 BDD-16 验证的"读取正确"只在 frontmatter
未被破坏的前提下成立；frontmatter 一旦经过标准 commit 流程就可能被破坏。这不改变本条 BDD-16
字面 Given/When/Then 已验证为真的结论，但读者应结合 bdd-17.md 一并理解本任务流 B 交付物的
真实可用性状态。
