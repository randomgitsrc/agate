# BDD-17: P6 逐条结果行格式从严（行首 `- PASS|FAIL BDD-NN:`）—— 判定 FAIL

## 该 BDD 字面覆盖的窄范围行为：已验证为真
- `ok 311 F_BDD17.1 BDD-17: check-p6-format.sh --check 行首 - PASS|FAIL BDD-NN: 格式被识别为有效逐条结果`
- 本次验收独立复现（--check 模式，非破坏性）：
```
$ printf -- '- PASS BDD-1: works (x.log)\n' > /tmp/p6ok.md
$ bash agate/scripts/check-p6-format.sh --check /tmp/p6ok.md; echo "exit=$?"
exit=0
$ printf -- '- pass BDD-1: works (x.log)\n' > /tmp/p6bad.md
$ bash agate/scripts/check-p6-format.sh --check /tmp/p6bad.md; echo "exit=$?"
exit=1
```
单看"body 逐条行识别"这一窄行为，`--check` 模式工作正常。

## 但本次验收发现该脚本（BDD-17 Given/When 明确指名的"check-p6-format.sh 升级版"）存在严重、
## 100% 可复现的缺陷，判定为 FAIL

### 缺陷复现（本次验收自查步骤原样命中，非人为构造边界案例）
按 P6 派发指引的强制自查步骤（"产出后跑 `check-p6-format.sh --fix docs/tasks/.../P6-acceptance.md`
做格式归一化"）对本次产出的 P6-acceptance.md（frontmatter 含合法的 `pass: 28` / `fail: 0` 字段，
这正是 BDD-16 要求的格式）执行 `--fix`：

```
$ cat P6-acceptance.md
---
phase: P6
...
pass: 28
fail: 0
ui_affected: false
---
...

$ bash agate/scripts/check-p6-format.sh --fix P6-acceptance.md; echo "exit=$?"
exit=0

$ cat P6-acceptance.md   # frontmatter 已被破坏
---
phase: P6
...
**Summary**: PASS: 28
**Summary**: FAIL: 0
ui_affected: false
---
...

$ python3 -c "import yaml; yaml.safe_load(open('P6-acceptance.md').read()[4:...])"
YAML ERROR: while scanning an alias
  in "<unicode string>", line 3, column 1:
    **Summary**: PASS: 28
    ^
expected alphabetic or numeric character, but found '*'
```
frontmatter 从合法 YAML 变为**非法 YAML**（无法被 `yaml.safe_load` 解析），`pass:`/`fail:` 两个
BDD-16 要求的必填字段被整行替换消失。

### 根因（读脚本源码确认）
`check-p6-format.sh` 的 `--fix` 模式包含这一段 sed（对整个文件内容做替换，未排除 frontmatter 块）：
```bash
FIXED=$(printf '%s' "$FIXED" \
  | sed -E 's/^([[:space:]]*)-\s+(pass)([[:space:]:：]|$)/\1- PASS\3/' \
  | sed -E 's/^([[:space:]]*)-\s+(fail)([[:space:]:：]|$)/\1- FAIL\3/' \
  | sed -E 's/^([[:space:]]*)(pass)([[:space:]:：]|$)/\1- PASS\3/' \
  | sed -E 's/^([[:space:]]*)(fail)([[:space:]:：]|$)/\1- FAIL\3/')
...
FIXED=$(printf '%s' "$FIXED" | sed -E 's/^-\s+(PASS|FAIL)\s*[:：]\s*([0-9]+)\s*$/\*\*Summary\*\*: \1: \2/')
```
第 3/4 条 sed（`s/^([[:space:]]*)(pass)([[:space:]:：]|$)/.../`）匹配**任意**行首为裸 `pass`/`fail`
后跟空格或冒号的行——不要求前面有 `-`。frontmatter 里 `pass: 28`（BDD-16 要求的标准写法本身）
精确命中这条 sed，被改写为 `- PASS: 28`，随后被第 5 条 sed（总结行归一化）再次改写为
`**Summary**: PASS: 28`。这套 sed 逻辑是 v0.35 时代为处理正文散文里"pass"/"fail" 开头的口语化
写法设计的，升级到 v2.0（P4-implementation.md 流 B 记录的"check-p6-format.sh 升级为
--check/--fix 双模式"）时未同步排除 frontmatter 块——而 frontmatter 块恰恰是同一个流 B
（BDD-16）新引入、合法地会出现裸 `pass:`/`fail:` 字段的地方。

### 影响面：不是边界案例，是 100% 确定性触发 + 无法被下游校验拦截
1. **触发条件即 BDD-16 的标准格式本身**：任何遵循 P2-design.md §3.2.1 样例（`pass: N` /
   `fail: N` 顶格声明）书写的合规 P6-acceptance.md，跑 `--fix` 后必然被破坏，不是罕见输入。
2. **该脚本由 pre-commit 无条件自动调用，且发生在 schema 校验之后、不会被重新校验**：
   ```
   $ grep -n "check-frontmatter.sh\|check-p6-format.sh" agate/scripts/pre-commit-gate.sh
   147:  bash "$AGATE_ROOT/scripts/check-frontmatter.sh" "$TASK_DIR/$FM_NAME" || exit 1   # 2g.2，先执行
   154:  bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md" || true  # 2h，后执行
   ```
   `check-frontmatter.sh`（BDD-2/4/5/6/7/8 的校验器）在第 147 行**先**对完好的 frontmatter 做
   校验（此时通过），随后第 154 行 `check-p6-format.sh --fix` 才**破坏** frontmatter——且用
   `|| true` 吞掉任何失败，破坏后的文件**没有被重新跑一次 schema 校验**就直接进入 commit。
   这正是 v2.0 立项要消灭的"产出物 YAML 无机器校验、坏格式悄悄漏过"（F6）在新场景下的复现——
   只是这次不是 subagent 手写错的，而是协议自己的自动修复步骤写错的。
3. 已用 `--check`（非破坏性）模式确认问题只存在于 `--fix` 路径，`--check` 本身安全
   （其正则要求行首有 `-`，不会误判 frontmatter 的裸 `pass:`/`fail:`）。

### 精确定位：`--fix` 的破坏性 sed 是原封不动继承自 v0.35，本次"升级"完全没碰它
用 `diff` 直接比较 `~/.agate/scripts/check-p6-format.sh`（主 checkout，v0.35.0 稳定版）与
`agate/scripts/check-p6-format.sh`（worktree，本次 v2.0 交付版）：
```
$ diff ~/.agate/scripts/check-p6-format.sh agate/scripts/check-p6-format.sh
24a25,47
> if [ "$MODE" = "check" ]; then
>     ...（新增的独立 --check 分支，BDD-17/18 对应的"升级"部分）...
> fi
48,54c71
< if [ "$MODE" = "fix" ]; then
<     if [ "$CHANGES" -eq 1 ]; then
<         printf '%s' "$FIXED" > "$FILE"
<     fi
<     exit 0
< fi
---
> # 到这里 MODE 必为 "fix"（"check" 已在上方独立分支处理并 exit）。
...
```
两个版本的差异**只有**新增的独立 `--check` 分支和收尾的控制流写法；产生本缺陷的那 5 条
`--fix` sed（含破坏 frontmatter 的第 3/4 条）逐字节相同，v2.0 的"升级"完全没有触碰这段代码。
这意味着：这不是本次 v2.0 改造"引入"的新缺陷，而是 v0.35 时代就存在、此前从未被触发的
潜伏缺陷——因为 v0.35 的 P6-acceptance.md 从不会在文件头出现裸 `pass:`/`fail:` 字段（这正是
本任务流 B / BDD-16 新引入的能力）。implementer 在同一个流（流 B）里既交付了"让 P6-acceptance.md
文件头合法出现 `pass:`/`fail:`"（BDD-16）又交付了"给 check-p6-format.sh 加 --check 分支"
（BDD-17/18 的字面对象），但未意识到需要同步排查/修复文件里已经存在的旧 `--fix` sed 逻辑与
新 frontmatter 字段之间的冲突——这是一个跨 BDD 边界、只有在真实端到端 dogfooding（写一份
真实的、含 frontmatter pass/fail 的 P6-acceptance.md，再跑一遍完整 pre-commit 流程）时才会
暴露的集成缺陷，P3/P4/P5 的既有测试用例均未构造过这个组合场景。

## 判定
**FAIL**——BDD-17 的 When 明确指名"check-p6-format.sh 升级版"为验收对象；该脚本虽然在窄义的
"body 逐条行识别"子功能上工作正常，但作为一个整体，其 `--fix` 模式存在严重、确定性复现、且
被 pre-commit 无条件自动调用的缺陷：会破坏同一流（流 B）的另一 BDD（BDD-16）要求的合法
frontmatter 字段，产出非法 YAML，且该损坏不会被下游任何校验步骤重新捕获。这不是"应该能过"的
边界情况，是本次验收按派发指引要求的自查步骤本身就必然触发的确定性缺陷。建议主 Agent 将此
问题退回 P4（流 B implementer 需修改 check-p6-format.sh 的 --fix sed 逻辑，使其排除 frontmatter
块——即先剥离 `---...---` 头部，只对正文部分做归一化）。本次验收未擅自修复代码，仅如实记录。
