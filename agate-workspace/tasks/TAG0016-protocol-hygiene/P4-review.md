---
phase: P4
task_id: TAG0016
type: review
parent: P4-implementation.md
trace_id: TAG0016-P4-review-20260819
status: approved
created: 2026-08-19
agent: review
---

# P4 实现评审复审（第 2 轮，偏执 Staff Engineer 视角）

这是第 2 轮复审。第 1 轮（见本文件历史版本，`status: rejected`）发现 2 个 CRITICAL：
`check-p6-provenance.py` 的 `audit7_p5_evidence_reuse` 在 `git diff` 命令失败时被静默当作
"无改动"处理，以及 `check-protocol-consistency.py` 的 `redeclares_table` 对指针文件做无范围
全文扫描、存在潜在误报风险。implementer 已在 `P4-implementation-reviewfix.md` 中给出修复说明。

按 dispatch-context 指引，本轮范围收窄为：只核查这 2 个 CRITICAL 的修复是否到位（读代码 +
自己实测），不重新审 Pass 2 INFORMATIONAL 的处理决定，不重新审协议文档去重内容。

---

## CRITICAL-1 复核：`audit7_p5_evidence_reuse` git diff 失败时的 fail-closed 处理

**核对代码**（`agate/scripts/check-p6-provenance.py:164-206`）：

```python
out, rc = _run_git(task_dir, ["diff", f"{p5_commit}..HEAD", "--name-only"])
if rc != 0:
    sys.stderr.write(
        f"GATE PROVENANCE: git diff {p5_commit}..HEAD 命令本身执行失败（returncode={rc}），"
        "无法判定 p5_pass_commit 与 HEAD 间是否存在改动（可能原因：commit 已被 rebase/squash "
        "移除、.state.yaml 手工写错哈希、CI 浅克隆导致该 commit 不在本地历史）。"
        "fail-closed：按 reuse_blocked 处理，强制重跑 P5\n"
    )
    return "reuse_blocked"

changed = [line for line in out.splitlines() if line and not line.startswith(EXCLUDE_PRODUCE_PREFIX)]

if changed:
    if p6_declares_reuse(task_dir):
        sys.stderr.write(
            "GATE PROVENANCE: 声明引用 P5 证据但检测到非产出文件改动，须重跑 P5：" + ", ".join(changed) + "\n"
        )
    return "reuse_blocked"
return "reuse_allowed"
```

确认：
- `_rc` 现已被检查（变量重命名为 `rc`，无遗漏）。`rc != 0` 分支在 `changed` 判定**之前** return，
  不会先算出空 `changed` 再走到下面。
- fail-closed 语义正确：`rc != 0` 直接返回 `"reuse_blocked"`，与 review 推荐的选项 A 一致
  （未新增第四态，而是复用 `reuse_blocked`——这是合理选择，因为 `main()`/`_run_audit7_only`
  两处调用方都已经把 `reuse_blocked` 当作"须重跑 P5"处理，不需要额外分支逻辑）。
- 两种失败的 stderr 文案确实不同、不混淆：git 命令失败分支写"命令本身执行失败...
  可能原因：...fail-closed"；真正检测到改动的分支写"声明引用 P5 证据但检测到非产出文件
  改动"。两者关键词不重叠（"命令本身执行失败" vs "检测到非产出文件改动"）。
- 两处调用方（`main()` 第 537-538 行、`_run_audit7_only` 第 227-231 行）用的是同一个函数，
  fix 对两条路径同时生效，没有遗漏 `--audit7-only` CLI 分支（这是上一轮明确指出的点）。

**实测**（自己跑，非只读代码）：

```
$ python3 -m pytest agate/tests/unit/test_check_p6_provenance.py -k "critical1" -v
test_p4_review_critical1_git_diff_command_fails_fail_closed_reuse_blocked PASSED
test_audit7_only_p4_review_critical1_fake_commit_git_fails_exit1 PASSED
2 passed, 49 deselected in 0.10s
```

读了两条测试的实际断言（非仅看测试名）：
- `test_p4_review_critical1_git_diff_command_fails_fail_closed_reuse_blocked`：构造只有一次
  init commit 的仓库，`p5_pass_commit` 传入伪造的 40 位十六进制哈希（`"a"*40`，仓库历史里
  不存在），断言 `audit7_p5_evidence_reuse(...)` 返回值 `== "reuse_blocked"`；并用 `capsys`
  实际抓取 stderr，断言含 `"命令本身执行失败"`（或 `"命令本身失败"`）且**不**含
  `"检测到非产出文件改动"`——直接验证了"两种失败不混在一条消息里"这个诉求，而不是只验证
  返回值。
- `test_audit7_only_p4_review_critical1_fake_commit_git_fails_exit1`：CLI 级，走真实子进程
  （`run_cli` 调用 `check-p6-provenance.py --audit7-only`），伪造哈希 `"b"*40` 写入
  `.state.yaml`，断言 `returncode == 1` 且 stdout 含 `"AUDIT7_RESULT: reuse_blocked"`——覆盖了
  上一轮明确点名的 `--audit7-only` CLI 路径。

**结论**：CRITICAL-1 修复到位，语义正确，测试真实覆盖了 git 命令失败这条此前的盲区路径。

---

## CRITICAL-2 复核：`redeclares_table` 调用处改为先裁剪小节再扫描

**核对代码**（`agate/scripts/check-protocol-consistency.py`）：

新增 `extract_section(text, heading)`（行 924-939），定位 `heading` 标题到下一个同级 `## `
标题（或文件末尾）之间的正文；未找到该标题返回 `None`。

`extract_md_table_int_column`（行 942-957）改为调用
`extract_section(text, RETRY_LIMIT_HEADING)` 取小节文本，再在小节内 `finditer`——与权威文件
一侧的既有行为保持一致（回归不变）。

调用处 `check_authoritative_values`（行 1000-1030）：

```python
text = fpath.read_text(encoding="utf-8")
scan_section = extract_section(text, RETRY_LIMIT_HEADING)
scan_text = scan_section if scan_section is not None else text
if pf.get("must_not_redeclare_table", True) and redeclares_table(scan_text, authoritative):
    ...
elif not any(p in text for p in pf["must_contain_any"]):
    ...
```

确认：
- 指针文件（`agate/rules/state-transitions.md`）在传给 `redeclares_table` 前，已先用
  `extract_section(text, RETRY_LIMIT_HEADING)` 裁剪出「## 重试上限」小节，不再是全文无范围
  扫描——与 CRITICAL-2 的修复要求（"先用 extract_section 裁剪出「## 重试上限」小节再扫描"）
  完全一致，且复用的是权威文件一侧同一套裁剪函数，没有搞两套实现（避免未来两处逻辑漂移）。
- `must_contain_any` 指针短语检查仍用未裁剪的全文 `text`（第 1027 行），这是对的——指针短语
  不一定落在「## 重试上限」小节内，收窄会引入新的漏报，implementer 的说明与代码行为一致。
- 找不到该标题时回退为全文扫描（`scan_text = ... if ... is not None else text`）：这保留了
  修复前的行为作为退化路径，不引入新的漏报，是合理的保守选择。
- 顺手修复的 INFO-1（`must_not_redeclare_table` 死配置）也已核实：第 1021 行
  `pf.get("must_not_redeclare_table", True)` 确实参与判断，不再是声明了却不读的死 key。

**实测**（自己跑）：

```
$ python3 -m pytest agate/tests/unit/test_check_protocol_consistency.py -k "critical2" -v
test_p4_review_critical2_unrelated_table_outside_section_no_false_positive PASSED
1 passed, 23 deselected in 0.03s
```

读了测试构造的场景（`_make_check12_tree(..., unrelated_table_outside_section=True)`，行
339-415）：在 `agate/rules/state-transitions.md` 的正确指针内容（「## 重试上限」小节只含
指针句，不含表格）之外，额外追加一个语义完全无关的小节「## 状态标记绑定（与重试上限无关
的另一张表）」，其表格行 `| P1 | 3 |` / `| P2 | 3 |` / `| P3 | 2 |` 与权威表数值逐一相同、
命中数 = 3，正好达到 `redeclares_table` 的阈值（`hits >= 3`）——这个用例确实是"修复前的实现
会被误判为重新声明权威表格，修复后不会"的最小复现，不是空泛构造。断言
`errors == []` 且 `"CHECK12-authval" in rep.passed`，即 0 误报，语义验证到位。

**结论**：CRITICAL-2 修复到位，裁剪逻辑正确复用、无漏报引入，新增测试是真实的误报复现场景
而非表面断言。

---

## 回归确认

自己跑的全量测试（非读 implementer 自报数字）：

```
$ timeout 180 python3 -m pytest agate/tests/ -q --tb=short
966 passed, 2 skipped in 95.98s
```

0 failed，与 dispatch-context 给出的预期基线（966 passed / 0 failed / 2 skipped）完全一致。
新增的 3 条测试（CRITICAL-1 两条 + CRITICAL-2 一条）均计入，未见回归。

---

## 总体结论

| 项 | 结论 |
|---|---|
| CRITICAL-1（git diff 失败 fail-closed） | 已验证修复到位，代码语义正确，测试真实覆盖此前的盲区路径 |
| CRITICAL-2（redeclares_table 小节裁剪） | 已验证修复到位，复用统一裁剪逻辑，测试是真实的误报复现场景 |
| 全量回归 | 966 passed / 0 failed / 2 skipped，与预期一致 |
| Pass 2 INFORMATIONAL（4 条） | 本轮不重新评估（按 dispatch-context 指引），处理情况见
  `P4-implementation-reviewfix.md`（INFO-1 已修复，INFO-2/3/4 留待后续，均在预期范围） |
| 协议文档去重内容 | 本轮未涉及改动，沿用第 1 轮抽查结论（无问题） |

2 个 CRITICAL 均已验证修复到位（非"看起来改了"，已自己跑测试 + 读代码确认语义正确），
未发现新问题，全量测试全绿。

**Status: approved**
