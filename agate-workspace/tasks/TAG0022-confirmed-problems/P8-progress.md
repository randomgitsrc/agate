# P8-progress — TAG0022 发布准备（implementer releaser 模式）

> 状态标记：[PROD_NOT_TOUCHED]（只读消费；写操作仅限 P8-release.md 与 P8-progress.md）
> 输入已读：dispatch-context / implementer.md / P8 卡 / P1 / P2 / P7 / tech-debt.md / P0-brief / README badge / CHANGELOG / UPGRADING / .state.yaml / git log v0.60.0..HEAD

## 1. 输入读取（证据链）
- [x] P8-dispatch-context-implementer.md（AGATE_CARD = P8 卡全文，派发指引强制）
- [x] implementer.md（P8 模式：不执行 git commit/tag；P8-release.md 产出）
- [x] P1-requirements.md（packages=[agate]，5 子项 BDD-1..10，phase P1-P8 全保留）
- [x] P2-design.md（packages=[agate]，gate_commands 六键，M1-M15 改动面，N3 count-tests 基线 1202）
- [x] P7-consistency.md（BLOCKER=0 / CRITICAL=0 / DESIGN_GAP 2/2 REVIEWED / SCOPE+ 闭环 / 通过）
- [x] tech-debt.md（682 行；open 10 条：DEBT0002/0003/0004/0007/0008/0014/0015/0016/0017/0018；DEBT0018 本任务登记）
- [x] P0-brief.md（5 issues + env_constraints；无 debug server/数据库/外部服务依赖）
- [x] 现状：README.md L5 badge v0.60.0 / README.zh-CN.md L5 badge v0.60.0 / CHANGELOG 无 [Unreleased]（[0.60.0] 为顶节）/ UPGRADING v0.61.0 节 ① 完整 ②③ 占位 / 无 version 文件
- [x] .state.yaml（phase=P7，judge.enabled=true，p5_pass_commit=f724e48）
- [x] git log v0.60.0..HEAD --oneline = 14 commits（10 个 wf(TAG0022-*) + 4 个 docs/merge：b88fb92 TAG0021 READY 收尾 / e30690f PR#185 merge / cc034be roadmap docs / bde3bfd PR#186 merge，均为 docs-only）

## 2. 客观查证
- [x] `git describe --tags --abbrev=0` = v0.60.0（worktree CHECK 7 前提成立）
- [x] `git merge-base --is-ancestor v0.60.0 HEAD` = true（tag 是 HEAD 祖先）
- [x] workflow ruff job：`name: ruff`（L107 稳定，可被分支保护引用）+ `pip install ruff==0.16.4`（L117）
- [x] check-gate.py judge P1 校验实现确认（grep judge_required_since L649/658/661 + dispatch.yaml `judge_required_since: "2026-08-22"`）
- [x] M15 排除钩子实现确认（check-protocol-consistency.py `_env_skip_dir_prefixes` L119 + iter_md_files 排除链 L141/160，默认关闭）
- [x] 临时 basetemp 目录复核：`agate/.bt-p6-verify` 不存在（ls 确认）；git status 仅 gate-events.jsonl（append-only 正常）+ P8 dispatch-context 未跟踪
- [x] 硬编码 v0.60.0 引用仅 README.md/README.zh-CN.md badge（UPGRADING/CHANGELOG 版本章节除外），无其他稳定版引用需更新

## 3. bump_type 判定
- 建议 **minor**。理由：① 存量兼容面≈0（judge 历史任务跳过 / 正文回退保留 / M15 默认关闭行为不变 / ruff 仅 CI 锁版本+配置文档）；② RM-AG0038 与 v0.60.0 M2 同型（判定口径不变、读取方式变、well-formed 等价），v0.60.0 判 minor 为直接先例；③ UPGRADING v0.61.0 章节已按 v0.61.0 预写，与 minor 不冲突（v0.60.0 同为 minor 且含破坏性变更节——"破坏性变更条目"列行为变化供对照，非自动触发 major）。

## 4. 产出
- [x] P8-release.md 已写入（bump_type / debt_check / 版本变更确认 / CHANGELOG 条目 / UPGRADING ②③ 补齐清单 / 临时资源清单 / 发布检查命令 / Lessons Learned）
