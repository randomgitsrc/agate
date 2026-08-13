# P5 技术验证结果 — TAG0004（环境适配：Windows 兼容 + Linux 基线回归）

- phase: P5
- task_id: TAG0004
- role: verifier
- 日期: 2026-08-13
- worktree: /home/kity/oclab/agate/.worktrees/agate-TAG0004

## 结果汇总

- **failed 数量：0（全绿）**
- 测试 runner 输出签名：`ok=714`，`not ok=0`（行首 `ok`/`not ok` 计数 714 > 0）
- 三个 gate 命令全部 exit 0
- 无预存失败（P1 基线已知问题均已在本任务 BDD 覆盖，未发现改动前就存在的失败）

## gate_commands.P5 逐条执行记录

### 命令 1/3：bats 全量（sanity + unit + regression + integration）

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

- exit code: 0
- 输出签名：`ok 714` / `not ok 0`
- 输出落盘：/tmp/opencode/tag0004-bats-full.log
- 结论：通过（全量测试已跑，含非本任务测试，未发现回归）

### 命令 2/3：consistency --strict

```bash
python3 agate/scripts/check-protocol-consistency.py --strict
```

- exit code: 0
- 输出签名：`ERROR 0` / `WARNING 0`；`✅ PASS` 全部检查通过
- 输出落盘：/tmp/opencode/tag0004-consistency.log
- 结论：通过（协议结构一致性无问题）

### 命令 3/3：shellcheck

```bash
shellcheck -S warning agate/scripts/*.sh
```

- exit code: 0
- 输出签名：0 error / 0 warning（输出为空）
- 输出落盘：/tmp/opencode/tag0004-shellcheck.log
- 结论：通过

## 预存失败

无。全量 714 条无失败。

## 环境隔离声明

`[PROD_NOT_TOUCHED]` 仅操作 worktree 与 /tmp/opencode，未触达主 checkout / `~/.agate` / 生产环境。

## 签名校验

- `grep -cE '^(PASSED|FAILED|passed|failed|ok|not ok)'`（unit.md 内 runner 签名行）：计数 > 0
- failed 计数：0
ok 700 bdd-3 pre-commit-gate 空格目录 PROCESSED_DIRS 不拆段 gate 正常执行（输出含 GATE P1）
ok 701 bdd-4 pre-commit-gate 无空格路径单任务 gate 行为不变（Linux 回归）
ok 702 bdd-17 pre-commit-gate 任务目录含 [ 元字符时 PROD_TOUCHED 检测不静默绕过（M9）
ok 703 bdd-19 pre-commit-gate 复制模式 hook 经 .agate-root 标记正确解析 AGATE_ROOT（其他-b）
ok 704 pre-push hook: 新分支首次推送提示跳过检测
ok 705 pre-push hook: 大改动触发提示
ok 706 pre-push hook: 无 agate/*.md 改动时零匹配 → 不报整数表达式错误（T086 回归）
ok 707 SG.1 角色文件 protocol-alignment-review.md 存在且含必需 frontmatter
ok 708 SG.2 角色文件含 A1-A6 审查清单
ok 709 SG.3 角色文件含 NEEDS_HUMAN_REVIEW 闭环规则 + HUMAN_CONFIRMED 标记
ok 710 SG.4 SELF-GATE.md 含派发模板
ok 711 SG.5 SELF-GATE.md 含检查清单
ok 712 SG.6 CHECK 9 锚点表覆盖全部 11 个 gate 脚本
ok 713 SG.7 commit-msg-self-gate.sh 存在且可执行
ok 714 SG.8 SELF-GATE.md 含递归终止条件
