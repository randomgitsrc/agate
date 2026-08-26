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

# P6 — 验收：TAG0025 Agateon 品牌改名执行 Phase 0-1（第 2 轮）

> 本轮背景：第 1 轮 P6.5 judge 独立复核判 `needs-revision`（BDD-1~9/11~16 共 15 条 PASS，BDD-10
> FAIL）。根因：P1-requirements.md BDD-10 原文当时只正式授权 5 类豁免，但判定实际依赖了测试文件
> `_is_exempt()` 里一个未经授权的第 6 类"自我豁免"逻辑。现已在 P1-requirements.md 第 4 节 BDD-10
> 正文补齐第 6 类豁免的 `[BASELINE_CHANGE]` 正式授权（第二处标注），第 3.2 节边界案例表同步补齐
> 对应判定行。第 1 轮 `P6-acceptance.md`/`P6-evidence/` 已被 `agate-archive-stale-outputs.py` 归档
> 至 `.archived/20260826-065343-P6/`，本轮从零重新产出，16 条 BDD 全部独立重新实跑，不引用归档
> 目录内容作为本轮证据。

ui_affected=false（P1-requirements.md 第 7 节：domains 无 `frontend`，不触发 UX 类别 BDD /
`ui_render_shape`/`ui_ux_dimensions` 声明要求），故不适用 vision-analyst / 双证据分档 / 人工复核
（输入态类）等 UI 专属约束；仅 BDD-11（治理类前置条件）按其固有证据形式使用人工复核记录。

## 品牌声明（Phase 0）

- PASS BDD-1: README.md 首屏第 2 行含 "Agateon (formerly agate)"，新旧品牌名同时出现，说明品牌沿革 (bdd-1-readme-en.txt)

- PASS BDD-2: README.zh-CN.md 首屏第 2 行 "**Agateon**（原名 agate）——本项目已改名" 同时含 "Agateon" 与 "agate" 两个品牌词，说明品牌沿革关系 (bdd-2-readme-zh.txt)

- PASS BDD-3: CHANGELOG.md 顶部第 11 行新增 `## [Unreleased]` 段（位于第 23 行 [0.63.0] 段之上），该段下第 13 行含 TAG0025 条目 (bdd-3-changelog.txt)

## 硬编码 URL 同批更新（Phase 1 核心 7 处）

- PASS BDD-4: install.sh 第 24 行 `git clone https://github.com/randomgitsrc/agateon.git` 已指向新仓名，旧 URL 字面扫描无命中 (bdd-4-install-sh.txt)

- PASS BDD-5: agate/scripts/agate-install.py 第 55 行 `DEFAULT_REPO_URL = "https://github.com/randomgitsrc/agateon"` 已指向新仓名，旧 URL 扫描无命中 (bdd-5-agate-install-py.txt)

- PASS BDD-6: agate/scripts/agate-changes.py 第 116 行 `"https://github.com/randomgitsrc/agateon.git"` 已指向新仓名，旧 URL 扫描无命中 (bdd-6-agate-changes-py.txt)

- PASS BDD-7: README.md 第 5 行（badge img src）与第 29 行（curl 安装入口）均含 `randomgitsrc/agateon`，两行同批更新，未出现只改一行的部分修复 (bdd-7-readme-md.txt)

- PASS BDD-8: README.zh-CN.md 第 5 行（badge）与第 29 行（安装入口）均含 `randomgitsrc/agateon`，两行同批更新 (bdd-8-readme-zh-cn-md.txt)

- PASS BDD-9: Phase 1 核心 7 处更新点所在 6 个文件（install.sh、agate-install.py、agate-changes.py、README.md、README.zh-CN.md、CHANGELOG.md）逐文件 `git log -1 --format=%H` 比对全部落在同一 commit 751f421a4c36becd657ab12fed0e80cd7423bef3；`git show --stat` 完整未截断输出（14 files changed）明确列出全部 6 个核心文件条目均在同一 commit 内，批次原子性成立 (bdd-9-atomic-commit.txt)

- PASS BDD-10: 全仓（排除 .git/、.worktrees/）执行 `randomgitsrc/agate\b` 字面扫描，应用 P1-requirements.md 第 4 节 BDD-10 正文现行 6 类豁免（含新增第⑥类 test_repo_url_no_stale_rename.py 自身）后剩余命中数为 0；pytest `test_bdd_10_repo_wide_residual_scan_zero_after_exemptions` PASSED（exit 0）+ 本轮独立手工 grep 交叉核对同样 0 残留；现在 6 类豁免均已在 P1-requirements.md 正式授权（两处 [BASELINE_CHANGE] 标注），不是已知盲区或变通处理 (bdd-10-residual-scan.txt)

## 不可逆操作前置条件

- PASS BDD-11: GitHub 仓库改名执行前获得用户在场放行确认；env-rename-handoff.md「六、版本记录」原始记录时序为"确认→执行"，执行主体与 P2-design.md 候选方案 B 一致，与 P0/P1 对权限核实/放行确认两个独立前置条件的表述交叉核对无矛盾；本轮人工复核结论 PASS (bdd-11-confirmation-record.md)

## 仓库改名验收锚（Phase 1）

- PASS BDD-12: `curl -sI https://github.com/randomgitsrc/agate` 实测响应 `HTTP/2 301`，`location: https://github.com/randomgitsrc/agateon`，响应头含完整 GitHub 真实响应特征 (bdd-12-301-redirect.txt)

- PASS BDD-13: `git ls-remote https://github.com/randomgitsrc/agateon.git HEAD` 返回码 0，输出 `c1e889f9d2c77c730922ae440c5f56a2c4744ba0	HEAD`，40 位有效 commit SHA，无错误无空输出 (bdd-13-ls-remote.txt)

- PASS BDD-14: `gh api search/repositories -f q='agateon in:name'` 返回结果第一位即 `randomgitsrc/agateon`，目标仓库出现在搜索结果首屏、不需翻页 (bdd-14-github-search.txt)

## remote 迁移影响面

- PASS BDD-15: 主 checkout 与 worktree `git remote -v` 均显示 `https://github.com/randomgitsrc/agateon.git`；worktree 内 `git config --show-origin` 确认与主仓共享同一 `.git/config`，无需重复 set-url (bdd-15-remote-config.txt)

- PASS BDD-16: 主 checkout 与该 worktree 各执行一次 `git fetch`，MAIN_CHECKOUT_FETCH_EXIT_CODE=0 / WORKTREE_FETCH_EXIT_CODE=0，两次均成功完成，无网络/权限报错 (bdd-16-fetch-verify.txt)

## 视觉质量 checklist

不适用——ui_affected=false，P1-requirements.md 第 7 节已声明"无 frontend 域，不触发 UX 类别 BDD
与 ui_render_shape/ui_ux_dimensions 声明要求"。本任务全部 BDD 属查询类/断言类（文件内容读取、
git 状态核对、网络请求状态码），非渲染/交互/输入态类，不适用输入态/交互形态变化类人工复核约束
（BDD-11 虽为人工复核，但复核对象是治理类会话记录，非"用户输入导致界面状态变化"这一判据）。

**Summary**: 16/16 PASS, 0 FAIL
