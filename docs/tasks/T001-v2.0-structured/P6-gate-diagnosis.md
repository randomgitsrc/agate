---
phase: P6
task_id: T001
type: gate-diagnosis
parent: P6-acceptance.md
created: 2026-08-10
agent: main
---

# P6 gate 失败诊断 — T001

## 触发

P6 verifier subagent 对 28 条 BDD 逐条验收，判定 27 PASS / 1 FAIL（BDD-17）。主 Agent 已独立复核该 FAIL（不采信 subagent 自报），确认属实。

## 失败内容

**BDD-17**（P6 逐条结果行格式从严：`- PASS|FAIL BDD-NN:`）判定 FAIL。

`agate/scripts/check-p6-format.sh` 的 `--fix` 模式存在一个确定性、100% 可复现的缺陷：其归一化 sed 逻辑对整个文件内容做替换，未排除 frontmatter 块（`---...---`）。frontmatter 里合法的 `pass: 28` / `fail: 0` 字段（BDD-16 本次改造引入的标准写法）会被这条 sed 误判为"待归一化的散文 pass/fail 行"，改写为 `**Summary**: PASS: 28`，导致 frontmatter 从合法 YAML 变为**非法 YAML**（`yaml.safe_load` 直接报错）。

## 独立复现（主 Agent 亲自验证，非采信 verifier 自报）

```
$ mkdir -p /tmp/p6dirtest && cat > /tmp/p6dirtest/P6-acceptance.md << 'EOF'
---
phase: P6
task_id: T001
pass: 28
fail: 0
ui_affected: false
---

- PASS BDD-1: test (x.log)
EOF
$ bash agate/scripts/check-p6-format.sh --fix /tmp/p6dirtest/P6-acceptance.md; echo "exit=$?"
exit=0
$ cat /tmp/p6dirtest/P6-acceptance.md
---
phase: P6
task_id: T001
**Summary**: PASS: 28
**Summary**: FAIL: 0
ui_affected: false
---

- PASS BDD-1: test (x.log)
$ python3 -c "import yaml; yaml.safe_load(open('/tmp/p6dirtest/P6-acceptance.md').read()[4:...])"
INVALID YAML: while scanning an alias ... expected alphabetic or numeric character, but found '*'
```

独立确认：`pass:`/`fail:` 两个 BDD-16 要求的必填字段被整行替换消失，frontmatter 无法再被 `yaml.safe_load` 解析。

## 影响面确认

1. **触发条件即 BDD-16 标准格式本身**——不是边界案例。任何遵循 `P2-design.md` §3.2.1 样例书写的合规 `P6-acceptance.md` 跑 `--fix` 后必然被破坏。
2. **无下游校验拦截**（主 Agent 核实 `agate/scripts/pre-commit-gate.sh`）：
   ```
   147: bash "$AGATE_ROOT/scripts/check-frontmatter.sh" "$TASK_DIR/$FM_NAME" || exit 1   # 先校验（此时 frontmatter 完好，通过）
   154: bash "$AGATE_ROOT/scripts/check-p6-format.sh" --fix "$TASK_DIR/P6-acceptance.md" || true  # 后损坏，|| true 吞掉失败，且不重新校验
   ```
   这正是本次 v2.0 改造要消灭的"产出物 YAML 无机器校验、坏格式悄悄漏过"（F6）在新场景下的复现——只是这次不是 subagent 手写错的，是协议自己的自动修复步骤写错的。

## 根因定位（主 Agent 核实，非采信）

```
$ diff ~/.agate/scripts/check-p6-format.sh agate/scripts/check-p6-format.sh
```
确认两版本差异**只有**新增的独立 `--check` 分支（BDD-17/18 升级的字面对象）和收尾控制流写法；产生本缺陷的 5 条 `--fix` sed（含破坏 frontmatter 的第 3/4 条）**逐字节相同**，v2.0 流 B 的"升级"完全没有触碰这段代码。

**结论：这不是本次 v2.0 改造"引入"的新缺陷，而是 v0.35 时代就存在、此前从未被触发的潜伏缺陷**——因为 v0.35 的 `P6-acceptance.md` 从不会在文件头出现裸 `pass:`/`fail:` 字段，这正是本任务流 B（BDD-16）新引入的能力。implementer 在流 B 里交付了"让 frontmatter 合法出现 `pass:`/`fail:`"（BDD-16）和"给 `check-p6-format.sh` 加 `--check` 分支"（BDD-17/18），但没有同步排查旧 `--fix` sed 逻辑与新 frontmatter 字段的冲突——这是跨 BDD 边界的集成缺陷，P3/P4/P5 的既有测试用例均未构造过"含 frontmatter pass/fail 字段的真实 P6-acceptance.md 走一遍完整 pre-commit 流程"这个组合场景，直到本次 P6 真实 dogfooding 才暴露。

## 判定：真失败，需要退回 P4 修复

不是环境问题，不是 verifier 误报，不是"边界情况可以放行"。这是一个会在**任何**未来任务的 P6 阶段确定性触发的缺陷（不限于 T001 自身），必须在合并到 `~/.agate` 正式版本前修复。

## 目标阶段与理由

**目标：P4**（不是 P5——问题源头在流 B 实现的 `check-p6-format.sh`，P5 只是运行既有测试，本身没有构造"真实 P6-acceptance.md 走完整 pre-commit"这个场景，退到 P5 无法覆盖这个缺陷类别）。

按 `state-machine.md`「阶段回退规则」：P6→P4 diff=2，需要 PAUSED + 人工批准。本文件即诊断内容，等待人工批准后：
1. `bash ~/.agate/scripts/agate-retreat-to.sh docs/tasks/T001-v2.0-structured P4 "BDD-17: check-p6-format.sh --fix 破坏 frontmatter pass/fail 字段，需修复"` 执行两步回退（P6→P5→P4，各自独立 commit + 归档旧产出）
2. 在 P4 派发定向修复：`check-p6-format.sh` 的 `--fix` 归一化 sed 需要先剥离 frontmatter 块（`---...---`），只对正文部分做替换，不触碰 frontmatter
3. 修复验证后重跑 P5→P6

## 修复方向建议（供 P4 派发时参考，不是本次要做的事）

`check-p6-format.sh` 的 `--fix` 分支需要：先用类似 `agate-frontmatter-check.py`/`agate-md-field-get.py` 里已有的 `_extract_frontmatter_block`/`_read_frontmatter` 同款逻辑，把文件切成 frontmatter 块 + 正文两部分，5 条归一化 sed 只应用到正文部分，frontmatter 部分原样保留，最后拼回。需要新增回归测试覆盖"P6-acceptance.md 含 frontmatter pass/fail 字段时 --fix 不破坏 frontmatter"这个场景（P3/P4/P5 都没覆盖到，是本次发现的真实测试盲区）。
