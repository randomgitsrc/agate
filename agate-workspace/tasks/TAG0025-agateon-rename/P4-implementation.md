---
implementation_dir: .
---
# P4 实现记录（批次 1）— TAG0025 Agateon 品牌改名执行 Phase 0-1

> [PROD_NOT_TOUCHED] 本批次只在本 worktree 内做纯文件层文本改动，未接触主 checkout
> （`/home/kity/oclab/agate`）与 `~/.agate`，未执行任何 `git add`/`git commit`/`git push`/
> `git remote set-url`/`gh api` 写操作，不涉及生产环境。

## 范围

按 P2-design.md 候选 B（已 approved）编排的 P4 批次 1：只做 §0.1 影响面表前 6 行的纯文件层
改动，让 P3 的 A 类红灯测试（`agate/tests/regression/test_repo_url_no_stale_rename.py`，
BDD-1~10 对应的 11 个测试函数）中除 BDD-9 外全部转绿。GitHub 仓库改名（`gh api -X PATCH`）、
`git remote set-url`、`git push` 及批次 2 的一切操作均不属于本批次范围，未执行。

## 改动清单（6 个文件，均为纯文本改动，未新增/删除文件）

| 文件 | 改动内容 | 对应 BDD |
|------|---------|---------|
| `README.md` | 第 2 行（原为空行）写入品牌声明句 `> **Agateon (formerly agate)** — this project has a new name; the badge and install command below already point to the new repository.`；第 5 行 badge img src、第 29 行 curl 安装入口的 `randomgitsrc/agate` → `randomgitsrc/agateon` | BDD-1, BDD-7 |
| `README.zh-CN.md` | 第 2 行（原为空行）写入中文品牌声明句 `> **Agateon**（原名 agate）——本项目已改名，下方徽标与安装命令已指向新仓库。`（同时含 "Agateon" 与 "agate" 两词）；第 5/29 行同上替换 | BDD-2, BDD-8 |
| `CHANGELOG.md` | 在 `## [0.63.0]` 段之上新增 `## [Unreleased]` 段，段下含 TAG0025 品牌改名 Phase 0-1 条目（3 条要点：品牌声明上线 / 7 处硬编码 URL 同批更新 / 三层解耦原则重申） | BDD-3 |
| `install.sh` | 第 24 行 `git clone https://github.com/randomgitsrc/agate.git` → `.../agateon.git` | BDD-4 |
| `agate/scripts/agate-install.py` | 第 55 行 `DEFAULT_REPO_URL = "https://github.com/randomgitsrc/agate"` → `.../agateon` | BDD-5 |
| `agate/scripts/agate-changes.py` | 第 116 行 `"https://github.com/randomgitsrc/agate.git"` → `.../agateon.git` | BDD-6 |

7 处 URL 替换用一次性脚本（用完即弃，未保留为项目资产）做精确字符串替换（`str.replace`，替换前
`assert` 每个文件的目标字符串出现次数与预期一致，非宽泛正则），未逐文件手改，避免漏改。

## 实现细节说明（非 P2 设计歧义，属实现层技术选择，供留痕）

P2-design.md §0.1 原文描述品牌声明为"第 1 行标题下方新增一行"。实测发现 README.md /
README.zh-CN.md 原文第 2 行恰好是空行，若在此处**插入**一整行新内容会导致第 3 行起全部下移
1 行，进而破坏 P3 测试硬编码的物理行号断言——`test_bdd_7_readme_en_badge_and_install_entry_*`
与 `test_bdd_8_readme_zh_badge_and_install_entry_*` 用 `lines[4]`/`lines[28]`（即第 5/29 行）
定位 badge 与安装入口，若行号整体偏移这两个断言会失败。因此改为**把品牌声明句写入既有的第 2
行空行**（净行数变化为 0），保持第 5/29 行的物理位置不变。品牌声明的内容、位置（标题正下方、
首屏可见）与 P2 设计意图完全一致，只是"新增一行"这个措辞在不破坏行号锚点测试的前提下，等价
实现为"填充既有空行"，不改变行为结果，不算 `[DESIGN_GAP]`（P2 设计的"什么内容、放哪里"意图
被完整保留，只是"是否物理新增一行"这个实现细节因为要兼容 P3 已固化的测试断言而做了必要调整）。

## 自查结果（P3 红灯测试复跑）

`python3 -m pytest agate/tests/regression/test_repo_url_no_stale_rename.py -v`：

- **10 个 PASSED**：`test_bdd_1_readme_en_brand_statement_first_screen`、
  `test_bdd_2_readme_zh_brand_statement_first_screen`、
  `test_bdd_3_changelog_unreleased_section_above_0_63_0`、
  `test_bdd_3_changelog_tag0025_entry_under_unreleased`、
  `test_bdd_4_install_sh_new_url_and_old_url_cleared`、
  `test_bdd_5_agate_install_py_new_url_and_old_url_cleared`、
  `test_bdd_6_agate_changes_py_new_url_and_old_url_cleared`、
  `test_bdd_7_readme_en_badge_and_install_entry_new_url_and_old_cleared`、
  `test_bdd_8_readme_zh_badge_and_install_entry_new_url_and_old_cleared`、
  `test_bdd_10_repo_wide_residual_scan_zero_after_exemptions`
- **1 个 FAILED（预期内）**：`test_bdd_9_seven_urls_same_commit_batch_atomicity`——
  断言 6 个文件最近一次改动的 commit SHA 全部相同，当前各文件改动尚未 commit（仍分散在改名前
  的 5 个历史 SHA 上），这是正常现象，不是实现问题。dispatch-context 约束 3 明确本批次不由
  implementer 执行 commit（批次原子性由主 Agent 统一 `git add` + 一次 `git commit` 后
  BDD-9 才会转绿）。

**过程中发现并修正的一个问题**：首次跑测试时 `test_bdd_10_repo_wide_residual_scan_zero_after_exemptions`
意外红灯——排查发现是我在 CHANGELOG.md 条目文案中写了 `` `randomgitsrc/agate` → `randomgitsrc/agateon` ``，
反引号紧跟在 `agate` 之后构成 word-boundary，被全仓残留扫描判定为一处旧 URL 残留命中（CHANGELOG.md
不在 BDD-10 豁免清单内）。已改写该条措辞为"硬编码仓库路径已同批更新为 `randomgitsrc/agateon`"，
不再在正文中拼出旧 URL 字面片段，重跑后转绿。此修正未扩大改动范围（仍在 CHANGELOG.md 内部），
未涉及测试代码改动。

全目录回归复跑 `python3 -m pytest agate/tests/regression/ -v`：27 passed, 1 failed（即上述
BDD-9 预期红灯），既有 17 个回归测试未被破坏。

## 新增文件核对表

本批次未新增任何文件（6 处改动均为对既有文件的原地编辑），核对表无行可填。

## SCOPE / DESIGN_GAP / CLARIFY 声明

无。本批次改动完全落在 P2-design.md §0.1 前 6 行声明的范围内，未发现需要标注
`[SCOPE+]`/`[DESIGN_GAP]`/`[CLARIFY]`/`[SCOPE_GAP]` 的偏差或缺口。

## 未执行的操作（明确确认）

本批次全程**未执行**以下任何操作：`git add`、`git commit`、`git push`、
`git remote set-url`、`gh api`（任何形式）。改动目前仍处于 worktree 的未暂存状态，等待主
Agent 统一 `git add` + 一次 `git commit`（满足 BDD-9 批次原子性要求）。
