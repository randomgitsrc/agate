---
phase: P4
task_id: TAG0025
type: review
parent: P4-implementation.md
trace_id: TAG0025-P4-review-20260826
created: '2026-08-26'
agent: review
status: approved
---

# P4 评审 — TAG0025 Agateon 品牌改名执行 Phase 0-1（批次 1）

> [PROD_NOT_TOUCHED] 本次评审为只读评审，未修改任何文件，未执行 `git add`/`git commit`/
> `git push`/`gh api`/`git remote set-url`，未接触主 checkout（`/home/kity/oclab/agate`）
> 与 `~/.agate`，不涉及生产环境。

## 评审对象

`git diff -- README.md README.zh-CN.md CHANGELOG.md install.sh agate/scripts/agate-install.py
agate/scripts/agate-changes.py`（工作区未暂存改动，6 个文件，均为纯文本替换：品牌声明句插入、
URL 字符串替换、CHANGELOG 段落新增）。已独立读取 diff 全文并逐行核对（未采信
P4-implementation.md 的自述改动清单，自己重新跑了一遍 diff 与相关命令）。

## Pass 1（CRITICAL）— 数据安全与正确性

不适用。本批次 6 个文件均为纯文本字符串替换（品牌声明句、URL 字面量、CHANGELOG 段落），无
SQL 拼接、无数据库读写、无 Read-Check-Write 竞态、无枚举/状态值消费方遗漏、无 LLM 生成数据
落库、无 TOCTOU。

## Pass 2（INFORMATIONAL）— 代码健康

不适用。无 Python async/sync 混用（改动的两处 `.py` 文件仅改字符串常量/文案，未涉及函数体
逻辑或事件循环）、无字段/列名变更、无 LLM prompt 索引假设、无 N+1/O(n²)、无资源泄漏、无被吞
错误。

## 前端专项

不适用。本任务无 `frontend` domain（P1-requirements.md frontmatter 已声明
`domains: [docs, cli, ops]`），改动的 README/CHANGELOG 属文档文本，非前端 UI 代码。

## 重点核查项逐条核实结论

### 核查项 1：URL 替换的精确性

**结论：精确，无连带副作用。**

- `agate/scripts/agate-install.py`：`grep -n randomgitsrc` 全文件只命中第 55 行
  `DEFAULT_REPO_URL = "https://github.com/randomgitsrc/agateon"`，diff 上下文（第 52-58 行）
  确认 `AGATE_DIRNAME`、`_VERSION_RE`、`_DECL_RE` 等相邻常量/正则未被触碰。
- `agate/scripts/agate-changes.py`：`grep -n randomgitsrc` 全文件只命中第 116 行
  `"https://github.com/randomgitsrc/agateon.git"`，diff 上下文（第 108-120 行）确认
  `_check_upstream` 函数其余逻辑（`upstream_range`、`_run_git` 调用等）未被触碰。
- `install.sh`：只第 24 行 `git clone` URL 被替换，diff 上下文其余行未变。
- `README.md` / `README.zh-CN.md`：第 5 行 badge、第 29 行 curl 安装入口各只替换 URL 本身，
  `img` 标签结构、其余 Markdown 语法未被触碰。
- 全仓 `grep -n randomgitsrc` 逐文件核对（见下方核查项 4 命令输出）确认这 5 个文件内不再有
  任何残留的 `randomgitsrc/agate`（旧 URL），也没有出现超出预期次数的额外替换。

### 核查项 2：implementer 记录的"实现层技术选择"是否合理

**结论：合理，未偏离 P2 设计意图，且确实避免了行号断裂——已独立复核验证。**

- 直接读取当前 `README.md`/`README.zh-CN.md` 第 1-5/29 行：第 1 行标题不变，第 2 行为品牌
  声明句（写入原第 2 行空行位置，未新增行），第 3 行为原有的协议一句话描述，第 5 行仍是
  badge，第 29 行仍是 curl 安装入口——物理行号与 P2-design.md §0.1 原始表格中"第 5 行 badge、
  第 29 行安装入口"的落点描述完全吻合，未发生任何下移。
- 交叉核对 `agate/tests/regression/test_repo_url_no_stale_rename.py:220-221`（`test_bdd_7_*`）
  与 `:233-234`（`test_bdd_8_*`）：两个测试均用 `lines[4]`/`lines[28]`（0-indexed，对应第
  5/29 行）定位 badge 与安装入口。若 implementer 按 P2 字面表述在第 2 行"插入"一整行，第 3
  行起会整体下移 1 行，`lines[4]` 会读到原第 4 行内容（而非 badge 行），这两个测试会失败。
  实测（见下）证明未发生此问题，说明"填充既有空行"这一处理确实规避了行号断裂。
- 品牌声明的内容（"Agateon (formerly agate)" / 中文对应句）、位置（标题正下方、首屏可见，
  未滚动即可读到）与 P2 设计意图（"首屏可见品牌声明"）一致；P2 原文"新增一行"这一措辞描述
  的是"品牌声明作为独立一行呈现"这一效果，implementer 的实现同样让品牌声明独立成行、且
  内容/可见性未打折扣，只是"净行数是否 +1"这一物理操作细节因兼容 P3 已固化的行号断言而做了
  调整。判定为合理的实现层技术选择，不构成 `[DESIGN_GAP]`。

### 核查项 3：CHANGELOG.md 反引号自指问题的修复是否彻底

**结论：修复彻底。**

`grep -n randomgitsrc CHANGELOG.md` 只命中第 19 行 `` 硬编码仓库路径已同批更新为
`randomgitsrc/agateon`。`` ——全文（含 `[Unreleased]` 段落全部三条要点）不再含任何
`randomgitsrc/agate`（旧 URL）字面片段，无论是否被反引号包裹。该行只拼出新 URL
`randomgitsrc/agateon`，`\b` word-boundary 正则不会在此产生误判（`agate` 后紧跟 `on` 不构成
边界）。已用实测的 BDD-10 残留扫描命令验证 CHANGELOG.md 不再产生命中（见下）。

### 核查项 4：是否有范围外改动

**结论：核心 6 个声明文件改动均在范围内；额外发现 1 个非声明文件的差异，判定为历史遗留、
非本批次 implementer 引入的范围外改动，不构成 BLOCKER。**

`git diff --name-only` 输出：

```
CHANGELOG.md
README.md
README.zh-CN.md
agate-workspace/tasks/TAG0025-agateon-rename/gate-events.jsonl
agate/scripts/agate-changes.py
agate/scripts/agate-install.py
install.sh
```

- 前 3 + 后 3 共 6 个文件与 dispatch-context 声明的评审对象完全一致。
- `agate-workspace/tasks/TAG0025-agateon-rename/gate-events.jsonl` 有 2 行新增，内容是
  `check-gate.py P3` 的运行日志与 P2→P3 状态迁移事件，时间戳为 `2026-08-25T18:04:34Z`——早于
  本次 P4 批次 1 的执行窗口，且与品牌改名/URL 替换无任何内容关联，是 P3 阶段遗留的未提交状态
  文件差异，不是 P4 implementer 本次改动引入的。P4-implementation.md 的改动清单（6 个文件）
  与自查结果对此文件未提及，与该判断一致。**建议**：非阻断项，交由主 Agent 在统一 `git add`
  时一并核对是否应随 P3 或本批次一起提交，不影响本次 approve 判定。
- 确认未触碰 `agate/` 目录名本身、`AGATE_*` 环境变量、`agate_common`、其他 `agate-*.py` 文件名
  （`git diff --name-only` 中除已声明的 `agate-install.py`/`agate-changes.py` 外，未出现任何
  其他 `agate/` 目录下文件路径变化）。

## 独立复跑验证（未采信 implementer 自查结论，自己重新执行）

- `python3 -m pytest agate/tests/regression/test_repo_url_no_stale_rename.py -v`：
  **10 passed, 1 failed**（`test_bdd_9_seven_urls_same_commit_batch_atomicity` 失败，
  失败原因是 6 个文件当前分散在 5 个历史 commit SHA 上——`git log -1` 逐文件比对确认，与
  implementer 自查结论一致，属预期内红灯，非本次评审范围）。
- `python3 -m pytest agate/tests/regression/ -q`：**27 passed, 1 failed**（同上 BDD-9），
  与 implementer 自查结论一致，既有 17 个回归测试未被破坏。
- BDD-10 全仓残留扫描命令（P2-design.md `gate_commands.P5_bdd10_residual_scan` 原文）独立
  重跑：应用 5 类豁免后，6 个声明文件范围内命中数为 0；额外观察到该原始 shell 命令对
  `agate/tests/regression/test_repo_url_no_stale_rename.py` 自身（P3 新增的测试文件，非本批次
  改动）会产生命中——但这是该文件内部说明性文档字符串引用旧 URL（用于测试断言逻辑本身），
  pytest 版本的 `test_bdd_10_*` 已对此文件做了针对性自指豁免（见该文件 `_is_exempt` 函数），
  两者判定结果一致（均为 0 残留/PASS）。**此项是 P2 gate_commands 原始 shell 命令与 P3 pytest
  实现之间的豁免清单差异，与本次评审的 6 文件 diff 无关，不影响本次 approve 判定，仅作为
  FYI 记录供主 Agent/后续 P5 gate 阶段留意**（若 P5 直接跑 P2 原始 shell 命令而非 pytest，
  可能需要针对新增测试文件补一条排除规则）。

## 结论

未发现 CRITICAL 或 BLOCKER。4 个重点核查项全部核实通过（URL 替换精确无副作用 / 空行填充技术
选择合理且已验证不破坏行号锚点 / CHANGELOG 自指问题修复彻底 / 无范围外改动，仅有 1 处历史遗留
非本批次文件差异已如实记录）。独立复跑测试结果与 implementer 自查结论一致。

**判定：approved。**
