## P8 releaser 分阶段落盘

### 步骤1：读取 dispatch-context 全部约束
已读 P8-dispatch-context-implementer.md 全文，7 条约束：①包核对（单包，非多包发布场景）
②bump_type=minor 判定依据 ③CHANGELOG 更新范围（新增 [0.56.0] 节，不动 README badge）
④debt_check=reviewed，DEBT0016/0017 留待后续 ⑤发布检查命令结果复用 P5/P6 既有证据
⑥Lessons Learned 3条建议方向 ⑦临时资源清单：无。

### 步骤2：核对 P2-design.md packages 声明
frontmatter packages: [phase-cards, execution-roles, templates, scripts]。确认为改动范围分类，
非多包发布清单。单包发布，无 SCOPE_GAP。

### 步骤3：核实 bump_type 判定
当前版本 v0.55.0（README.md L5 badge 确认）。本任务新增 RM-AG0008（骨架脚手架，
project_phase: bootstrap 可选字段）+ RM-AG0009（CODE-MAP 架构演进纪律，
code_map_new_files_count/code_map_reviewed_count 可选字段），均向后兼容新增能力，无破坏性变更
→ bump_type: minor，v0.55.0 → v0.56.0。

### 步骤4：核对 DEBT0016/DEBT0017
tech-debt.md 中两条均 status: open, task_id: TAG0007。
- DEBT0016：gate_p4 的 CODE-MAP.md 路径本地推导未调用 agate_common.resolve_workspace，
  closure_criteria 要求改用权威函数——留待后续任务。
- DEBT0017：gate_p4「## 新增文件核对表」子串判定假阴性 + TAG0007 自身自我应用缺口，
  closure_criteria 要求改整行匹配 + 补齐标准标记——留待后续任务。
两条均非本轮关闭范围，debt_check: reviewed。

### 步骤5：编辑 CHANGELOG.md
已在 [0.55.0] 节之上新增 `## [0.56.0] - 2026-08-20` 节，含「新增」小节（RM-AG0008/RM-AG0009 各
一段 + BDD 覆盖）+「已知遗留」小节（DEBT0016/DEBT0017）。grep -c 确认 [0.56.0] 出现 1 次。
README.md/README.zh-CN.md 未改动（git diff --stat 无输出）。

### 步骤6-9：汇总发布检查命令结果 / Lessons Learned / 临时资源清单 / 写 P8-release.md
已全部完成，P8-release.md 写入
/home/kity/oclab/agate/.worktrees/agate-TAG0007/agate-workspace/tasks/TAG0007-project-structure/P8-release.md，
含 bump_type: minor / debt_check: reviewed / 版本号建议 v0.55.0→v0.56.0 / CHANGELOG 更新确认 /
发布检查命令结果表 / 3 条 Lessons Learned / 临时资源清单（无）/ PROD_NOT_TOUCHED。

### 步骤10：自检
- P8-release.md 存在，含 bump_type/debt_check 字段：确认
- grep -c "## \[0.56.0\]" CHANGELOG.md = 1：确认
- git diff --stat README.md README.zh-CN.md 无输出：确认
- 未执行任何 git commit/tag/bump-version 操作：确认（git status 只显示未 commit 的文件改动）
全部自检通过，P8 releaser 任务完成。
