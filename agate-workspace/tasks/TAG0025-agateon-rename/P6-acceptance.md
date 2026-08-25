---
phase: P6
task_id: TAG0025
type: acceptance
parent: P5-test-results/unit.md
trace_id: TAG0025-P6-20260826
status: draft
created: 2026-08-26
agent: verifier
# ── v2.0 机器汇总 ──
pass: 16
fail: 0
ui_affected: false
---

[PROD_NOT_TOUCHED]

[NO_NEED_CONFIRM]

# P6 — 验收：TAG0025 Agateon 品牌改名执行 Phase 0-1

本文件对照 `P1-requirements.md` 全部 16 条 BDD，逐条**独立重新实跑**验证命令（不照抄
P5-test-results/unit.md 的输出，命令即使与 P5 一致也重新执行一遍取得本次真实结果）。工作目录
`/home/kity/oclab/agate/.worktrees/agate-TAG0025`，验收时 HEAD
`f30dad1152ae9cabf7384de0c9f283c1848717e2`（P5 commit）。本任务 `ui_affected: false`，全部证据
为文本类命令输出/断言日志，不涉及 Playwright/vision。

不执行任何写操作：`gh api -X PATCH`（改名）与 `git remote set-url`（迁移）均已在 P4 完成，本阶段
未重复执行；BDD-15/16 涉及的 `git remote -v`/`git fetch` 均为只读命令，按 dispatch-context 声明
允许对主 checkout `/home/kity/oclab/agate` 执行，未 cd 进入或编辑主 checkout 内任何文件。

## 品牌声明（Phase 0）

- PASS BDD-1: README.md 首屏（前 15 行内）出现 "Agateon (formerly agate)"，grep -F 精确命中 exit 0 (bdd-1-readme-en.txt)
- PASS BDD-2: README.zh-CN.md 首屏出现"Agateon（原名 agate）"，Agateon 与 agate 两个品牌词同时出现 (bdd-2-readme-zh.txt)
- PASS BDD-3: CHANGELOG.md 新增 `## [Unreleased]` 段（第11行）且含 TAG0025 条目（第13行），两条 grep 均 exit 0 (bdd-3-changelog.txt)

## 硬编码 URL 同批更新（Phase 1 核心 7 处）

- PASS BDD-4: install.sh 第 24 行指向 randomgitsrc/agateon，无旧仓 URL 残留 (bdd-4-install-sh.txt)
- PASS BDD-5: agate/scripts/agate-install.py 第 55 行 DEFAULT_REPO_URL 指向 randomgitsrc/agateon，无旧仓 URL 残留 (bdd-5-agate-install-py.txt)
- PASS BDD-6: agate/scripts/agate-changes.py 第 116 行指向 randomgitsrc/agateon，无旧仓 URL 残留 (bdd-6-agate-changes-py.txt)
- PASS BDD-7: README.md 第 5 行（badge）与第 29 行（安装入口）均指向 randomgitsrc/agateon，两行同批命中 (bdd-7-readme-md.txt)
- PASS BDD-8: README.zh-CN.md 第 5 行（badge）与第 29 行（安装入口）均指向 randomgitsrc/agateon，两行同批命中 (bdd-8-readme-zh-cn-md.txt)
- PASS BDD-9: install.sh/agate-install.py/agate-changes.py/README.md/README.zh-CN.md 5 个文件逐一 git log -1 均返回同一 SHA 751f421a4c36becd657ab12fed0e80cd7423bef3，git show --stat 确认该 commit 同批含 README.md/README.zh-CN.md/CHANGELOG.md，未跨多个 commit 分批交付 (bdd-9-atomic-commit.txt)
- PASS BDD-10: 权威判定用 pytest 版本 test_bdd_10_repo_wide_residual_scan_zero_after_exemptions 独立重新执行 exit 0，1 passed，排除 5 类豁免后全仓残留命中数为 0（已知盲区处理规则同 P5：shell 版对测试文件自身文档字符串有盲区，不作为判定依据）(bdd-10-residual-scan.txt)

## 不可逆操作前置条件

- PASS BDD-11: env-rename-handoff.md「六、版本记录」原始记录明确写出改名调用（gh api -X PATCH）执行于"用户当次会话内明确放行确认后"，本次 P6 会话人工复核该记录 + 交叉核对 P0-brief/P1-requirements 对"权限核实"与"放行确认"两条独立前置条件的声明，未发现"仅凭权限核实即执行改名"的记录漏洞 (bdd-11-confirmation-record.md)

## 仓库改名验收锚（Phase 1）

- PASS BDD-12: curl -sI https://github.com/randomgitsrc/agate 实测响应 HTTP/2 301，location 头指向 https://github.com/randomgitsrc/agateon (bdd-12-301-redirect.txt)
- PASS BDD-13: git ls-remote https://github.com/randomgitsrc/agateon.git HEAD exit 0，返回 40 位十六进制 commit SHA c1e889f9d2c77c730922ae440c5f56a2c4744ba0，无错误信息、无空输出 (bdd-13-ls-remote.txt)
- PASS BDD-14: gh api search/repositories -f q='agateon in:name' 返回结果首位即为 randomgitsrc/agateon，出现在搜索结果首屏、不需要翻页 (bdd-14-github-search.txt)

## remote 迁移影响面

- PASS BDD-15: git -C /home/kity/oclab/agate remote -v 与 git -C /home/kity/oclab/agate/.worktrees/agate-TAG0025 remote -v 均显示 origin https://github.com/randomgitsrc/agateon.git，worktree 侧 git config --show-origin 确认复用主 checkout 的 .git/config，未对 worktree 单独执行 set-url 即已生效 (bdd-15-remote-config.txt)
- PASS BDD-16: 在主 checkout 与该 worktree 内各执行一次 git fetch，两次均 exit 0，无网络/权限报错 (bdd-16-fetch-verify.txt)

**Summary**: PASS: 16, FAIL: 0（16/16 BDD 通过独立实跑验证）

## 交叉核对说明

- P5-test-results/unit.md（`gate_commands.P5_*` 24 key 全量重跑）记录的预期与本次 P6 独立实跑
  结果逐条一致，未发现漂移；但本报告的每条 PASS 判定均基于本次会话独立重新执行的命令输出
  （见各证据文件），不是转抄 P5 结果。
- BDD-10 判定口径与 dispatch-context 约束 2 一致：shell 版本命令对
  `agate/tests/regression/test_repo_url_no_stale_rename.py` 自身文档字符串有盲区，本报告未采用
  shell 版本输出作为 BDD-10 的 PASS 判定依据，只以 pytest 权威判定为准。
- BDD-11 证据形式属人工记录类，非程序化断言，符合 dispatch-context 约束 3 对该条 BDD 的证据形式
  指引。
- BDD-12~16 均为本次独立重新实跑取得的真实结果（非 P3/P4 阶段"当前不适用"状态），与
  env-rename-handoff.md「六、版本记录」已归档的 P4 执行时结果同向一致。
