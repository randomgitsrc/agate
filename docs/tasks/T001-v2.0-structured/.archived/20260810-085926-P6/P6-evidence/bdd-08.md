# BDD-8: 校验器与 .state.yaml 校验同机制接入 pre-commit

## P5 测试证据
- `ok 159 CF.10 BDD-8: check-frontmatter.sh 与 check-state-yaml.sh 同构——非空校验输出 → exit 1；合规文件 → exit 0`
- `bats agate/tests/integration/pre-commit-hook.bats`：52/52 全绿（P5 全量结果），确认真实 pre-commit
  hook 流程未被新增挂载点破坏。

## 本次验收独立复现（挂载点机制对比）
```
$ grep -n "check-frontmatter.sh\|check-state-yaml.sh" agate/scripts/pre-commit-gate.sh
52:    bash "$AGATE_ROOT/scripts/check-state-yaml.sh" "$STATE_FILE" || exit 1
142:    # 逐个跑 check-frontmatter.sh，非空校验输出 → exit 1 拦截（坏格式 gate 直接拦，不靠主 Agent 判断）
144:    if [ -x "$AGATE_ROOT/scripts/check-frontmatter.sh" ]; then
147:                bash "$AGATE_ROOT/scripts/check-frontmatter.sh" "$TASK_DIR/$FM_NAME" || exit 1
```
两处挂载点用完全相同的 `bash <script> <file> || exit 1` 模式：`.state.yaml` 走
`check-state-yaml.sh`（第 52 行），P1/P2/P6/P7 产出文件走 `check-frontmatter.sh`（第 147 行）。
"subagent 写坏格式 → gate 直接拦，不靠主 Agent 判断"的机制对两类文件一致。

## 判定
PASS
