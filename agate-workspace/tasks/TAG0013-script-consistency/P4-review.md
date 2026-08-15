---
phase: P4
task_id: TAG0013-script-consistency
type: review
parent: P4-implementation.md
trace_id: TAG0013-P4-20260816
status: approved
created: 2026-08-16
agent: review
---

# P4 实现评审 — agate 脚本一致性批（RM-AG0015 / RM-AG0017 / RM-AG0018 剩余）

> 偏执 Staff Engineer 视角，只审不写。所有结论均基于本 worktree 独立实测（非转引），
> 引用锚点 = 文件:行号 / 函数名 / BDD 编号。
> 客观查证全部重跑复核：全量 pytest **768 passed, 2 skipped**（66s）；consistency **0 ERROR / 279 WARNING**
> （CHECK 10：0 ERROR + CHANGELOG 聚合 1 WARNING）；count-tests.sh = **770**；ruff **全过**。

---

## 0. 结论摘要

**Status: approved**

- 三处脚本改动与 P2-design.md 候选方案 A 逐项一致，未发现 CRITICAL / BLOCKER。
- BLOCKER-1（main() 状态匹配前缀碰撞）修复经 **real main() 实跑**确认：CHECK 1 ✅ 与 CHECK 10 ⚠️ 状态行独立，无污染。
- 19 个新用例（TC-01..19）全部实现且全绿；integration test_csg_1 断言翻转正确。
- 5 项 INFORMATIONAL 观察（见 §3），均不阻断，不影响 approved。

---

## 1. Pass 1 — CRITICAL（数据安全与正确性）

无 CRITICAL。逐项过：

| 关注点 | 结论 | 锚点 |
|---|---|---|
| SQL 注入 / 字符串拼接 | 不适用（纯文件扫描 + git subprocess，无 DB/查询拼接） | — |
| Read-Check-Write 竞态 | 不适用（CHECK 10 只读扫描，无状态写入；hook 只读 `git diff --cached`） | check-protocol-consistency.py:816-857 |
| 状态值消费方同步（BLOCKER-1） | **正确**。`main()` 状态匹配改为 `e["check"].split("-")[0] == key`；real main() 实跑：注入 `CHECK10-scriptref` error 时输出 `✅ PASS  CHECK 1` / `❌ FAIL  CHECK 10`；warning 场景 `✅ PASS  CHECK 1` / `⚠️  WARN  CHECK 10`；全量 consistency 实跑同样 CHECK 1 ✅ + CHECK 10 ⚠️（CHANGELOG 聚合） | check-protocol-consistency.py:913,915；test_check_protocol_consistency.py:139-190（TC-04/05） |
| LLM 数据未校验写库 | 不适用 | — |
| TOCTOU | 无（`is_file()` 与后续 `read_text` 间隙的删除竞态在单用户工作区不存在；与其他 CHECK 同模式） | — |
| 正则 ReDoS | **安全**。SCRIPT_REF_RE 各分支由固定字面前缀 + 单层 `[a-z0-9-]+` + 字面 `.py/.sh` 组成，无嵌套量词 → 线性回溯；两端 `\b` 防止部分 token 误匹配（`check-gate.pyx` 不会命中 `check-gate.py`） | check-protocol-consistency.py:771-775 |

---

## 2. P2-design 方案符合性（逐项）

| P2-design 要求 | 实现锚点 | 核验 |
|---|---|---|
| §2 SCRIPT_REF_RE 白名单（含 `agate_` 下划线形状，覆盖 agate_common.py） | check-protocol-consistency.py:771-775 | ✓ 与设计 L72-75 逐字符一致 |
| §2 扫描面常量 SCRIPT_REF_SCAN_FILES/DIRS（PROTOCOL_FILES + README/AGENTS/CONTEXT/UPGRADING/scripts-README + 3 目录） | :779-786 | ✓ 与设计 L82-88 一致 |
| §2 豁免①UPGRADING 整文件 | :831-832（先于行级扫描判断） | ✓ 与设计 L98（豁免先于行级判断）一致 |
| §2 豁免④ count-tests.sh 同名不同目录 | :839-840（校验 `agate/tests/scripts/count-tests.sh`） | ✓ 与设计 L96/决策 4 一致 |
| §2 豁免③ 3 hook 薄壳 | :841-842（HOOK_SHELL_NAMES） | ✓ |
| §2 豁免② formatters forward-defense | :843-844（formatter_names 目录比对） | ✓ 当前不可达（formatter 名不匹配白名单），注释已标注 forward-defense |
| §2 豁免⑤ scripts/README 退役名 | :845-846（`relpath == "agate/scripts/README.md"` 限定） | ✓ 限定正确，不溢出到其他文件 |
| §2 CHANGELOG 叙事聚合单条 WARNING | :848-852（`narrative_warned` 按文件去重） | ✓ `--json` 实跑确认 CHECK 10 恰好 1 条 WARNING，0 ERROR |
| §2 main() 状态匹配 split 修复（BLOCKER-1） | :913,915 | ✓ 见 §1；设计 §9 决策 6 / §11 完成标志 1 全落实 |
| §2 模块 docstring 补 CHECK 10 行（非阻塞 5） | :19 | ✓ |
| §3 _SELF_GATE_RE 精确名锚定 | commit-msg-self-gate.py:38-40（追加 `|README\.md|AGENTS\.md`） | ✓ 与设计 §3 候选 A 一致；CHANGELOG 天然豁免 |
| §3 stderr 文案同步 | commit-msg-self-gate.py:77 | ✓ 含 README.md / AGENTS.md |
| §4 DEBT/roadmap 提醒行 | check-retrospective.py:94（`if warnings:` 块内 L89-95） | ✓ 仅 warnings 非空时输出；含 DEBT 与 roadmap 两词；exit 0 不变 |
| PROTOCOL_DIRS 扩展 3 目录 | check-protocol-consistency.py:66 | ✓ 与设计 §9 决策 3 一致；实跑 CHECK 2/3 无新增 ERROR（CHECK 3 ✅） |
| CHECKS 注册 CHECK 10 | :879 | ✓ |

**BDD 覆盖复核**（P3 TC-01..19 ↔ 实跑）：

- BDD-1（TC-01/02）、BDD-2（TC-03/04/05）、BDD-3（TC-06..10）、BDD-4（TC-11）、BDD-5（TC-12/13）、BDD-6/7/8/9（TC-14..17）、BDD-10/11（TC-18/19）——19 个用例全部存在且通过（目标文件 42 passed；全量 768 passed, 2 skipped）。
- P2-review 缺口 8「驱动 real main() 而非复刻表达式」：TC-04/05 采用 monkeypatch CHECKS + 注入假 `CHECK10-scriptref` + `cpc.main()` + capsys 捕获，**假绿风险已堵死**（若 main() 未修，`✅ PASS  CHECK 1` 断言必败）；另显式断言 `"CHECK10-scriptref".startswith("CHECK1") is True` 锁定根因（test_check_protocol_consistency.py:166）。
- integration test_csg_1 断言翻转：`test_csg_1_non_trigger_no_warning` → `test_csg_1_readme_triggers_warning`，`not in` → `in`（diff 确认），与 RM-AG0017 新语义一致，实测通过。
- 测试口径：count-tests.sh = 770 ≥ 751（P2 §5 基线），新增恰 19 用例（770−751）。

---

## 3. INFORMATIONAL（非阻断，供后续参考）

1. **豁免⑤ 的 `gate-result.sh` 是天然豁免，非分支命中**：`gate-result.sh` 不以 check-/agate- 前缀开头，不匹配 SCRIPT_REF_RE 白名单形状 → 永不产生 token，:845 的 ⑤ 分支实际只被 `agate-workspace-resolve.sh` / `check-windows-smoke.sh` 命中。与豁免② 的 forward-defense 同性质（P2 §2 步骤 3.d 已声明「保留作前向防御」），当前集合无害；**若未来新增退役名且其名匹配白名单形状，需手动补进 `SCRIPTS_README_RETIRED_NAMES`**（设计已接受该维护点）。
2. **聚合 WARNING 只报首个 token**：`narrative_warned` 按文件去重后，CHANGELOG 的历史漂移只暴露第一个（实跑为 `check-windows-smoke.sh` [CHANGELOG.md:17]），完整漂移清单不在输出中。符合 P2 §9 决策 2（聚合防刷屏）——可见性牺牲是有意为之，操作者如需全量可 grep 脚本名。
3. **严格 UTF-8 读取**：CHECK 10 对扫描文件 `read_text(encoding="utf-8")`，若某扫描文件混入非 UTF-8 字节将抛 UnicodeDecodeError 中止整次一致性检查（与其他 CHECK 同模式，当前仓库全 UTF-8、CI 行为一致）。可选加固：包 try/except 降级为 WARNING——非必需。
4. **`_SELF_GATE_RE` 的 `agate/.+/.*\.md` 分支（既有）** 使 agate/ 下任意 md（含 agate/scripts/README.md）触发 self-gate。本次任务未改该分支，与「触发面 = 协议文档」语义一致，无需处理。
5. **白名单形状覆盖边界**：非 check-*/agate-*/hook 前缀的未来脚本（如 `my-tool.py`）不会被检测。P2 §2 风险/权衡已接受（新脚本必然形如 check-*/agate-*）。另 P2-review 观察 1 的计数口径差异（378/595 vs 616/219）不影响 0 漂移结论，实现注释（:768-769）已描述白名单形状，无需追加。

---

## 4. Pass 2 — 代码健康

- **资源泄漏**：无。文件读取用 `read_text`（自动关闭）；subprocess 用 `capture_output` 收管；无遗留句柄。
- **错误吞掉**：`run_git` 失败降级为空（rc!=0 返回空、returncode 0 时遍历）——hook 是提示型 exit 0，fail-open 语义正确（commit-msg-self-gate.py:53-59）；commit-msg 读取失败置空串同样符合 hook 鲁棒性原则（:66-70）。一致性检查的 `iterdir`/`rglob` 对不存在目录均 `is_dir()` 前置判空，无异常路径。
- **平台无关**：新增代码全部 Path API + `rel()` 统一 os.sep（:142）；无裸 python3、无 /tmp、无软链创建；测试全用 `tmp_path`/`git_repo` fixture 且显式 `encoding="utf-8"`；Windows CI 冒烟（csg_1）断言 README 触发——git 的 `--name-only` 输出统一正斜杠，`^...README\.md$` 跨平台成立。
- **性能**：扫描面 = 17 显式文件 + 3 目录 rglob，单轮线性，实测整轮 consistency < 数秒。无 N+1 / O(n²)。

---

## 5. 返回给主 Agent

- 状态：**approved**
- 阻塞问题数：0
- 关键发现：实现与 P2 方案 A 逐项一致；BLOCKER-1（main() split 修复）经 real main() 实跑确认；19 新用例全绿、csg_1 断言翻转正确、count-tests 770；0 ERROR / 279 WARNING 与派发查证一致。5 项 INFORMATIONAL 均非阻断（豁免⑤ gate-result.sh 天然豁免、聚合 WARNING 只报首 token、严格 UTF-8、既有 `agate/.+/.*\.md` 分支、白名单形状边界）。
- 环境隔离：本评审未触碰任何生产/协议/测试文件，无写入。

[PROD_NOT_TOUCHED] 本次评审仅读取代码/跑验证命令，未修改任何生产代码、测试或协议文档（唯一写操作是 P4-progress.md 与 P4-review.md 这两个任务产出文件）。
