## P8 releaser progress
- [读] P8-dispatch-context-implementer.md：目标=产出 P8-release.md，bump patch→v0.44.0，不执行 git 操作；7 packages 全覆盖 CHANGELOG
- [读] implementer.md（P8 模式）：逐包处理、不 commit/tag、Lessons Learned 2-3 条、临时资源清单、P8 多包发布纪律
- [读] P2-design.md：packages=[agate-scripts-sh, agate-scripts-py, agate-phase-cards, agate-docs, agate-gitconfig, agate-ci, agate-tests] 7 项；候选 26 项覆盖 S1/S2/S3/M4/M5/M6/M9/Q1/Q2/Q5/RM-AG0001/RM-AG0002+TPV0090-M4/CI/其他 a-c
- [读] P7-consistency.md：status=approved，BLOCKER=0，DESIGN_GAP 1 条已 REVIEWED，SCOPE+/SCOPE_GAP 闭环，48 文件改动 7 包全覆盖
- [读] CHANGELOG.md：Keep a Changelog 格式，顶部 [0.43.0] - 2026-08-12
- [读] P0-brief.md：Windows 兼容增量、Linux 基线不得回退、46 处改动、CI windows-latest 兜底
- [读] README.md：badge v0.43.0（L6）→ v0.44.0；version 文件 = README badge，无独立 version.txt
- [查] 当前 tag v0.43.0；git log 最新 f9f6957 (P7)
- [查] debt/ 目录为空，无 tech-debt.md → debt_check: none
- [决] bump_type: patch → v0.43.0 → v0.44.0
- [写] P8-release.md 完成：bump_type: patch (v0.44.0)、debt_check: none、版本链路 v0.43.0→v0.44.0、CHANGELOG [0.44.0] 草稿覆盖 7 packages 全部修复组、临时资源清单、Lessons Learned 3 条
## P8-fix-ci implementer progress (2026-08-13)

- 读 dispatch-context + implementer.md + AGENTS.md + P0-brief 完成
- 目标文件确认：check-protocol-consistency.py 入口在 L28-33（import sys 在 L32），main() 在 L759，中文 print 在 L782；protocol-tests.yml shellcheck Windows 步骤 L57-62（echo 指向不存在的 shellcheck-v0.10.0/），consistency/gate-backstop Windows 步骤 L85-87/L108-110
- worktree 干净，branch=feat/TAG0004-env-adaptation
- 修复完成：consistency 脚本加 stdout reconfigure（hasattr 守卫）；yaml shellcheck 解压到 $GITHUB_WORKSPACE/shellcheck + shellcheck.exe 调用 + Windows step 设 PYTHONIOENCODING=utf-8
- 自查全过：consistency --strict 0 ERROR / bats 3/3 / yaml safe_load 合法
- P8-fix-ci.md 已写（含 Header + diff 摘要 + 自查表 + 无 SCOPE_GAP + PROD_NOT_TOUCHED）
