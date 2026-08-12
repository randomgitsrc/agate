# BDD-28: 本 task 自身 T001 全程按 v0.35 gate 通过

## 验证方式
P3-test-cases.md 已注明该 BDD 无 worktree 内 bats 断言（验证载体是"主 Agent 运行时纪律"+
git log 可查的历史事实），验证方式是核对 T001 的 P0-P8 阶段产出文件 + .state.yaml 是否全程
`~/.agate`（v0.35.0 稳定版）gate 通过。本次验收独立执行以下核证：

## 本次验收独立复现

### 1. 本 task 全程 task_id 保持 T001（未曾切换为新格式）
```
$ git log -p --follow -- docs/tasks/T001-v2.0-structured/.state.yaml | grep -n "task_id"
task_id: T001   （P0 提交起）
task_id: T001   （历次修改后均保持不变）
```
本任务从立项到 P5，`.state.yaml` 的 task_id 字段全程为 `T001`（旧格式），未曾迁移为
`TAG` 格式——因为流 D 的硬切校验器是 worktree 本体（v2.0）的交付物，只约束 v2.0 之后新建的
任务，本 task 自身按约定继续用旧格式。

### 2. 各阶段 commit 均以 "wf(T001-Pn)" 前缀记录，逐阶段推进有据可查
```
$ git log --oneline -- docs/tasks/T001-v2.0-structured/
f4bd942 wf(T001-P5): 技术验证通过
098cb06 wf(T001-P4): 阶段收尾 — phase P4 → P5
f476834 wf(T001-P4-adr007): ...
17f11e5 wf(T001-P4-selfgate-docfix): ...
3064734 wf(T001-P4-rereview): C8 review 复审通过 — status: approved
e566303 wf(T001-P4-reviewfix): ...
68e4173 wf(T001-P4-streamD-fixturefix): ...
2b56579 wf(T001-P4-streamD): ...
901f61d wf(T001-P4-streamC): ...
ebda17e wf(T001-P4-streamB): ...
3754e9d wf(T001-P4-streamA): ...
293924f wf(T001-P3): ...
b41c61c wf(T001-P2): ...
73154fc wf(T001-P1): ...
a1eb0a8 wf(T001-P0): ...
```
每个阶段（P0-P5，本次 P6 验收对象）都有独立 commit，phase 字段递进（P1→P2→...→P5），
符合状态机推进要求——这本身就是 pre-commit hook（依赖 `~/.agate` 的 v0.35.0 gate 脚本）
放行的结果，因为 hook 会对暂存的 `.state.yaml` phase 变更做校验。

### 3. `~/.agate` 确认仍是 v0.35.0（未被本次 v2.0 改造污染），且 task_id 正则仍是旧版
```
$ readlink -f ~/.agate
/home/kity/oclab/agate/agate
$ grep -n "T\\\\d\|T\[A-Z\]" ~/.agate/scripts/agate-state-yaml-check.py
39:if task_id and not re.match(r"^T\d+$", str(task_id)):
$ git -C /home/kity/oclab/agate status --short
（无输出，工作区干净）
```
`~/.agate`（本机项目实际使用的稳定版）的 task_id 正则仍是旧版 `^T\d+$`，能接受 `T001`；
worktree 内本次改造的新正则 `^T[A-Z]{2}\d+$`（会拒绝 T001）只存在于
`/home/kity/oclab/agate/.worktrees/v2.0/agate/scripts/agate-state-yaml-check.py`，两者物理
隔离。主 checkout 的 git 工作区状态干净，未被本次改造触碰——双工作区隔离铁律保持成立，
这正是 BDD-28"本 task 不被流 D 新校验器约束"得以成立的物理基础。

## 判定
PASS
