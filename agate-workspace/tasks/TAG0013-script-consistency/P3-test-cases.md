---
phase: P3
task_id: TAG0013-script-consistency
type: test-cases
parent: P2-design.md
trace_id: TAG0013-P3-20260816
status: draft
created: 2026-08-16
agent: test-designer
---

# P3 测试设计 — agate 脚本一致性批（RM-AG0015 / RM-AG0017 / RM-AG0018 剩余）

> 上游：P1-requirements.md（approved，11 条 BDD）+ P2-design.md（approved，候选方案 A）
> \+ P2-review.md（approved，BLOCKER-1 修复已纳入 + 测试缺口 7/8 已落实）。
> 本任务为**功能任务**（P1 frontmatter 无 `change_type: refactor`）→ 标准 TDD 口径：
> 新增用例当前须**红灯**（实现未写）。基线 count-tests.sh = 751（P2 §5 固化）。

## 1. 测试代码位置

test_code_dir: agate/tests/unit/

| 文件 | 追加内容 | 覆盖 BDD |
|------|---------|---------|
| `agate/tests/unit/test_check_protocol_consistency.py` | CHECK 10 用例（最小假协议树）+ PROTOCOL_DIRS + BLOCKER-1 回归 | BDD-1..5 |
| `agate/tests/unit/test_commit_msg_self_gate.py` | self-gate 触发面扩展用例 | BDD-6..9 |
| `agate/tests/unit/test_check_retrospective.py` | 登记提醒行用例 | BDD-10/11 |

全部为**追加**（不改既有用例，不删）。既有用例保持原样（BDD-9 由既有 test_cmsg_1..4 与新用例共同覆盖）。

## 2. 用例清单（编号 TC-NN ↔ BDD 1:1）

### 2.1 test_check_protocol_consistency.py（追加 13 用例）

| 编号 | BDD | 测试名 | 场景 | 预期（当前红灯原因） |
|------|-----|--------|------|---------------------|
| TC-01 | BDD-1 | `test_bdd_1_checks_list_registers_check10` | `cpc.CHECKS` 含 `CHECK 10` 条目 | 红灯：CHECKS 现无 CHECK 10 → AssertionError（未注册） |
| TC-02 | BDD-1 | `test_bdd_1_check10_zero_drift_passes` | 最小假协议树 + WORKFLOW.md 合法引用（check-gate.py/check-tdd-red.py）→ `rep.ok` 且 0 漂移 | 红灯：`check_script_name_refs` 未导出 → AttributeError |
| TC-03 | BDD-2 | `test_bdd_2_check10_drift_error` | phase-cards/P3-tdd.md 含 `check-nonexistent-script.py` → ERROR，msg 含脚本名、loc 含 `P3-tdd.md` | 红灯：函数未导出 → AttributeError |
| TC-04 | BDD-2 | `test_bdd_2_blocker_check1_independent_when_check10_error` | 驱动 **real main()**：CHECK10 报 ERROR → CHECK 1 状态行 ✅、CHECK 10 ❌（P2-review 缺口 8，非"复刻表达式"） | 红灯：main() 仍是 `startswith(key)` → CHECK 1 被 CHECK10-scriptref 污染显示 ❌ → 断言失败（BLOCKER-1 未修） |
| TC-05 | BDD-2 | `test_bdd_2_blocker_check1_independent_when_check10_warning` | 同上，CHECK10 报 WARNING → CHECK 1 ✅、CHECK 10 ⚠️ | 红灯：同上（CHECK 1 被污染显示 ⚠️） |
| TC-06 | BDD-3 | `test_bdd_3_exempt_upgrading_whole_file` | UPGRADING.md 含退役 `.sh` 名（check-gate.sh/check-tdd-red.sh）→ 0 漂移（豁免①整文件） | 红灯：函数未导出 → AttributeError |
| TC-07 | BDD-3 | `test_bdd_3_exempt_formatter_names_natural` | 协议文件含 `pytest.sh`/`go-test.sh`/`my-runner.sh` → 0 漂移（豁免②天然成立：不匹配白名单形状） | 红灯：函数未导出 → AttributeError |
| TC-08 | BDD-3 | `test_bdd_3_exempt_hook_shells` | 协议文件含 `pre-commit-gate.sh` → 0 漂移（豁免③） | 红灯：函数未导出 → AttributeError |
| TC-09 | BDD-3 | `test_bdd_3_exempt_count_tests_sh` | 协议文件含 `count-tests.sh` + `agate/tests/scripts/count-tests.sh` 存在 → 0 漂移（豁免④同名不同目录） | 红灯：函数未导出 → AttributeError |
| TC-10 | BDD-3 | `test_bdd_3_exempt_scripts_readme_retired_names` | scripts/README.md 含 `gate-result.sh`/`agate-workspace-resolve.sh`/`check-windows-smoke.sh` → 0 漂移（豁免⑤） | 红灯：函数未导出 → AttributeError |
| TC-11 | BDD-4 | `test_bdd_4_protocol_dirs_includes_phase_cards_rules` | `cpc.PROTOCOL_DIRS == ("agate/assets/", "agate/phase-cards/", "agate/rules/")` | 红灯：当前仅 `("agate/assets/",)` → AssertionError（未扩展） |
| TC-12 | BDD-5 | `test_bdd_5_changelog_drift_aggregated_warning` | CHANGELOG.md 含退役 `.sh` 名 → 0 ERROR + **聚合 1 条** WARNING（叙事降级） | 红灯：函数未导出 → AttributeError |
| TC-13 | BDD-5 | `test_bdd_5_docs_dir_not_scanned` | `docs/superpowers/guide.md` 含 `check-nonexistent-script.py` → 无 ERROR、无 WARNING（非扫描面无输出） | 红灯：函数未导出 → AttributeError |

### 2.2 test_commit_msg_self_gate.py（追加 4 用例）

| 编号 | BDD | 测试名 | 场景 | 预期（当前红灯原因） |
|------|-----|--------|------|---------------------|
| TC-14 | BDD-6 | `test_bdd_6_readme_triggers_self_gate_warning` | git_repo 暂存根级 `README.md`，commit msg 无标记 → stderr 含 "self-gate"，exit 0 | **红灯**：`_SELF_GATE_RE` 未含 `README\.md` → 不触发 → 无输出 → 断言失败 |
| TC-15 | BDD-7 | `test_bdd_7_agents_triggers_self_gate_warning` | 同上，暂存 `AGENTS.md` | **红灯**：未含 `AGENTS\.md` → 断言失败 |
| TC-16 | BDD-8 | `test_bdd_8_changelog_exempt_no_output` | 暂存 `CHANGELOG.md` → 无输出、exit 0 | 绿锁（当前已豁免，锁定扩展后仍豁免，防回归） |
| TC-17 | BDD-9 | `test_bdd_9_agate_md_trigger_not_regressed` | 暂存 `agate/WORKFLOW.md` → 仍触发 WARNING | 绿锁（锁定既有 `agate/*.md` 触发面在正则扩展后不回归） |

### 2.3 test_check_retrospective.py（追加 2 用例）

| 编号 | BDD | 测试名 | 场景 | 预期（当前红灯原因） |
|------|-----|--------|------|---------------------|
| TC-18 | BDD-10 | `test_bdd_10_debt_roadmap_reminder_on_anomaly` | task_dir 重试超限（P2 ×3）→ 输出含 "DEBT" 与 "roadmap" | **红灯**：提醒行未实现 → 输出无 DEBT/roadmap → 断言失败 |
| TC-19 | BDD-11 | `test_bdd_11_no_anomaly_empty_output` | task_dir 无异常 → 输出为空、exit 0 | 绿锁（RT.1 既有行为，锁定提醒行只进 `if warnings:` 块） |

> 红/绿说明：TC-16/17/19 是**回归锁**（锁定既有行为在本次改动后不回归），当前即绿；
> 其余 16 个用例当前红灯（失败原因均为"被测模块未实现/未修改"），套件整体满足 P3 真红灯。

## 3. BDD 1:1 映射表

| BDD | 验收条件 | 测试用例 | 状态 |
|-----|---------|---------|------|
| BDD-1 | 0 漂移 CHECK 10 通过 | TC-01（CHECKS 注册）+ TC-02（零漂移 PASS） | 红 |
| BDD-2 | 引用不存在脚本 → ERROR + 消息含文件/位置 | TC-03 + TC-04/TC-05（BLOCKER-1 回归，ERROR/WARNING 双场景） | 红 |
| BDD-3 | 豁免清单 5 类不报漂移 | TC-06（①UPGRADING 整文件）+ TC-07（②formatter 天然豁免）+ TC-08（③hook 薄壳）+ TC-09（④count-tests）+ TC-10（⑤scripts/README 退役名） | 红 |
| BDD-4 | phase-cards/rules 入 PROTOCOL_DIRS | TC-11 | 红 |
| BDD-5 | 叙事至多 WARNING；docs/ 不扫 | TC-12（CHANGELOG 聚合 WARNING）+ TC-13（docs 非扫描面无输出） | 红 |
| BDD-6 | 暂存 README.md 触发 WARNING | TC-14 | 红 |
| BDD-7 | 暂存 AGENTS.md 触发 WARNING | TC-15 | 红 |
| BDD-8 | 暂存 CHANGELOG.md 不触发 | TC-16 | 绿锁 |
| BDD-9 | 既有触发面不回归 | TC-17 + 既有 test_cmsg_1..4（不改动） | 绿锁/回归 |
| BDD-10 | 有异常 → DEBT+roadmap 提醒 | TC-18 | 红 |
| BDD-11 | 无异常 → 空输出 | TC-19 + 既有 test_rt_1（不改动） | 绿锁/回归 |

> 11 条 BDD 全部有对应测试用例（部分 BDD 多条用例，覆盖正/反/回归三面）。

## 4. 夹具选型说明（P2 测试策略缺口 7/8 落地）

- **CHECK 10 用例（TC-02..TC-13）→ 最小假协议树**：pytest `tmp_path` 下构造
  `agate/scripts/`（假脚本 `check-gate.py`/`agate_common.py`/`check-tdd-red.py`/
  `check-protocol-consistency.py`）+ `agate/tests/scripts/count-tests.sh` + 协议文档面
  扫描文件集（PROTOCOL_FILES 11 + AGENTS/CONTEXT/UPGRADING/scripts-README/CHANGELOG +
  phase-cards/rules/assets 目录示例），`_load_cpc` importlib 加载后直接调
  `check_script_name_refs(root, rep)` 断言 `rep.errors`/`rep.ok`。**不**扫真实 worktree
  （避开 CHANGELOG 聚合 WARNING 基线干扰 + 平台无关原则要求临时目录）。
- **BLOCKER-1 用例（TC-04/05）→ 驱动 real main()**（P2-review §2 观察 2 建议优先方案）：
  monkeypatch `cpc.CHECKS` 为 [CHECK 1, CHECK 10] 标题 + `cpc.run_all_checks` 注入假
  `CHECK10-scriptref` 的 error/warning，monkeypatch `sys.argv` 传 `--root` 后调 `cpc.main()`，
  用 capsys 捕获状态行。**不"复刻表达式"**——若 P4 忘改 main() 状态匹配（L810-816），
  CHECK 1 状态行被污染，断言 `"✅ PASS  CHECK 1"` 失败（假绿风险已被堵死）。同时断言
  `"CHECK10-scriptref".startswith("CHECK1") is True` 显式锁定回归根因。
- **self-gate 用例（TC-14..17）→ git_repo fixture + `_run_csg` helper**：复用既有模式，
  暂存区造根级文档变更（等价 git add 后 commit-msg hook 读 `--cached`）。
- **复盘用例（TC-18/19）→ task_dir fixture + `_run_retro` helper**：复用既有模式。

## 5. 平台无关与边界（P1 §2 / P3 门槛）

- 不用裸 `python3`（走 conftest `python_exe` fixture）；不用 `/tmp`（走 pytest `tmp_path`）；
  不创建软链（无 POSIX symlink 假设）；文本 I/O 显式 `encoding="utf-8"`。
- 测试名全部引用 BDD 编号（`test_bdd_N_*`），可追溯。
- **不测试不可达分支**：豁免②的 formatters 目录比对是 forward-defense（当前不可达），
  P2 明确"P3 不应为不可达分支写测试"——TC-07 只断言"formatter 名天然不匹配白名单"
  （可达的 whitelist 行为），不测目录比对分支本身。
- 不修改被测脚本（check-protocol-consistency.py / commit-msg-self-gate.py / check-retrospective.py）。
