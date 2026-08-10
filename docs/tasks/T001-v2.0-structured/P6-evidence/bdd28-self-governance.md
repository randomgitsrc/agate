# BDD-28 — 本 task 自身 T001 全程按 v0.35 gate 通过（自举边界）

验证载体：非 worktree 内 bats 用例（P3-test-cases.md §5 已注明），而是主 Agent 每阶段实跑 ~/.agate/scripts/check-gate.sh 的运行时纪律 + 双工作区隔离的机制性证据。本次独立核实以下客观事实。

## 1. git hooks 实际指向 ~/.agate（非 worktree 自身协议），worktree 与主 checkout 共享 .git/hooks
```
/home/kity/oclab/agate/agate/scripts/pre-commit-gate.sh
```
T001 worktree 的 .git 是 gitdir 指针（/home/kity/oclab/agate/.git/worktrees/v2.0），hooks 目录未在 worktree 级别覆盖，沿用主仓库 .git/hooks/pre-commit，该文件是软链到 /home/kity/.agate/scripts/pre-commit-gate.sh（v0.35 稳定版），不是 worktree 内 agate/scripts/pre-commit-gate.sh（v2.0 本体）。即：T001 至今每一次 git commit 实际触发的都是 ~/.agate 的 v0.35 gate，不是本任务自己正在改造的新 gate。

## 2. ~/.agate 的 task_id 校验器仍是旧正则（未被本 worktree 改造影响，隔离确认）
```
39:if task_id and not re.match(r"^T\d+$", str(task_id)):
```

## 3. T001 自身 .state.yaml 用 ~/.agate（v0.35）校验：通过
```
(无输出=校验通过，task_id: T001 符合 v0.35 旧正则 ^T\d+$)
```

## 4. 反证：若用 worktree 自身新校验器（v2.0）校验 T001 的 .state.yaml，会被拒绝（证明 T001 若不走隔离机制本会被自己的新规则挡住，隔离是真实生效而非摆设）
```
task_id 格式错误: T001（应为 T + 2 个大写字母项目代号 + 数字，如 TAG0001）
```

## 5. T001 全部 P0-P8 阶段产出 commit 记录（git log，独立重新核实）
```
1483f36 wf(T001-P5-retry1): 技术验证重跑通过（P4 修复后全量复核）
afe758a wf(T001-P4-p6formatfix): 修复 check-p6-format.sh --fix 破坏 frontmatter 的 bug（P6 回退定向修复）
f4bd942 wf(T001-P5): 技术验证通过
098cb06 wf(T001-P4): 阶段收尾 — phase P4 → P5
f476834 wf(T001-P4-adr007): 补充 ADR-007 — frontmatter 单工具双读 vs 独立 facts 文件
17f11e5 wf(T001-P4-selfgate-docfix): 修复 self-gate 审查发现的 4 处 MISALIGNED 文档滞后
3064734 wf(T001-P4-rereview): C8 review 复审通过 — status: approved
e566303 wf(T001-P4-reviewfix): 修复 C8 review CRITICAL + self-gate 语义审查完成
68e4173 wf(T001-P4-streamD-fixturefix): 修复流D硬切引发的33个既有fixture回归
2b56579 wf(T001-P4-streamD): 实现 — 任务编号规则硬切（^T[A-Z]{2}\d+$）
901f61d wf(T001-P4-streamC): 实现 — P1 标记结构化 + 角色卡/模板 frontmatter 可复制样例
ebda17e wf(T001-P4-streamB): 实现 — P6/P7 结果结构化 + FIND-6 交叉校验 WARNING
3754e9d wf(T001-P4-streamA): 实现 — frontmatter 双读工具 + 新校验器 + pre-commit 挂载 + CHECK9 锚点表
293924f wf(T001-P3): 测试设计 — 28 BDD 全覆盖，594 用例配平，真红灯确认
b41c61c wf(T001-P2): 方案设计 — frontmatter 强化 + 单工具双读扩展 + 新校验器挂 pre-commit（A/B/C/D 四流）
73154fc wf(T001-P1): 需求基线 — v0.40.0 结构化改造 28 条 BDD 覆盖 A/B/C/D 四流
a1eb0a8 wf(T001-P0): 重审后完整立项 — A+B+C+D 全做，v2.0.0 一次发布
```

结论：T001 自身 task_id 保持 T001 旧格式，全程经由 ~/.agate（v0.35 稳定版）pre-commit hook 校验通过（未被自身正在开发的 v2.0 新校验器约束），双工作区隔离机制真实生效（非文档声明），符合 BDD-28 自举约束。
