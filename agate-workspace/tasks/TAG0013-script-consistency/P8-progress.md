# P8 progress（releaser subagent 分阶段落盘）

## 已读输入
- [x] P8-dispatch-context-implementer.md（派发指引：只产出 P8-release.md，不 bump/commit/tag）
- [x] implementer.md（P8 模式）
- [x] P2-design.md（packages: [agate-scripts, agate-tests, agate-protocol-docs, agate-consistency]；无破坏性变更；CHECK 10 内联）
- [x] P7-consistency.md（BLOCKER=0，SCOPE+ 闭环，approved）
- [x] debt/tech-debt.md（DEBT0001 open，source: retrospective，closure_criteria 3 条）
- [x] CHANGELOG.md（无 [Unreleased] 段，[0.47.0] 为 latest）
- [x] README.md badge（L5 version-v0.47.0）+ README.zh-CN.md 同
- [x] UPGRADING.md（最新节 v0.47.0 bats→pytest；每版本一节）
- [x] P6-acceptance.md（PASS 11 / FAIL 0）
- [x] git log/tag（v0.47.0 最新 tag；v0.47.0..HEAD 36 commits 含 TAG0013 P1-P7）

## 评估结论
- bump_type = minor：新增 CHECK 10（功能）+ PROTOCOL_DIRS 扩展 + self-gate 触发面扩展（内部）+ 复盘提醒行；无破坏性变更（用户可见协议语义不变）→ v0.47.0 → v0.48.0
- debt_check = reviewed：DEBT0001 closure_criteria 3 条均被本任务满足（CHECK 10 落地 + 漂移报 ERROR 测试锁定 + phase-cards/rules 入 PROTOCOL_DIRS）→ 建议关闭，须 task_id + P5/P6 evidence 引用（check-debt closed 准入）
- UPGRADING：无破坏性变更 → 无需迁移动作；建议按 AGENTS.md 发布清单新增一节注明「无破坏性变更」

## P8 产出完成
- [x] P8-release.md 已写入（bump_type: minor + debt_check: reviewed + 版本确认 + CHANGELOG 确认 + UPGRADING 评估 + 临时资源清单 + 多包清单 + LL）
- [x] 未执行 bump/commit/tag（git log 无新增）
- [x] CHANGELOG.md / README badge 未修改（git status 仅 active-tasks.md 既有修改 + 3 个新 untracked 文件）

