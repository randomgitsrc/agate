---
phase: P8
task_id: TAG0013-script-consistency
type: release
parent: P7-consistency.md
trace_id: TAG0013-P8-20260816
status: draft
created: 2026-08-16
agent: implementer
---

# P8 发布准备 — TAG0013（agate 脚本一致性批）

> releaser subagent（implementer P8 模式）产出。**本文件只做发布准备，不执行 bump-version / git commit / git tag**（由主 Agent 在 gate 验证通过后亲自执行）。自查≠gate，未声称「P8 已过」。

## 1. bump_type

```yaml
bump_type: minor
```

**理由**：本任务为功能新增（RM-AG0015 新增 CHECK 10 协议文档脚本名引用漂移 gate + PROTOCOL_DIRS 扩展；RM-AG0017 self-gate 触发面补 README/AGENTS；RM-AG0018 剩余 复盘提醒行），**无破坏性变更**（用户可见协议语义不变，全部为脚本/测试/一致性检查内部增强）。按语义化版本：新功能 + 兼容 → minor。当前 v0.47.0 → 建议 **v0.48.0**。

## 2. debt_check

```yaml
debt_check: reviewed
```

**关联 DEBT0001 评估**（`{AGATE_WORKSPACE}/debt/tech-debt.md`）：
- 状态：`open`，`source: retrospective`（TAG0010/0011 复盘），`priority: high`，关联 RM-AG0015。
- **closure_criteria 对照（3 条）**：
  1. ✅ `check-protocol-consistency.py` 新增 CHECK 10 且通过率 0 ERROR——P7 worktree 实核 CHECK 10 内联（L816 `check_script_name_refs`）+ P5/P6 实测 0 ERROR（279 WARNING 基线，CHECK 10 对 CHANGELOG 聚合 1 WARNING）。
  2. ✅ 协议文档引用已删脚本名 → 报 ERROR（测试锁定）——P6 BDD-2 假协议树 `check-nonexistent-script.py` → ERROR + exit 1。
  3. ✅ phase-cards/rules 入 PROTOCOL_DIRS——P7 实核 `PROTOCOL_DIRS = ("agate/assets/", "agate/phase-cards/", "agate/rules/")`（L66），P6 BDD-4 实测 CHECK 2/3 对 phase-cards/rules 0 ERROR。
- **结论**：3 条 closure_criteria 全部满足 → **建议将 DEBT0001 置为 `closed`**（由主 Agent 落地，非本文件修改）。关闭时按 check-debt closed 准入：须 `task_id: TAG0013-script-consistency` + evidence 引用 P5/P6 证据（如 `agate-workspace/tasks/TAG0013-script-consistency/P6-evidence/bdd-1.log` / bdd-2.log / bdd-4.log）。本次无其他新增债务。

## 3. 版本号变更确认

- 当前版本：**v0.47.0**（README.md L5 + README.zh-CN.md L5 badge + CHANGELOG [0.47.0] + git tag v0.47.0）
- 目标版本：**v0.48.0**（`bump_type: minor`）
- 需改的 version 位置：README.md + README.zh-CN.md badge（`version-v0.47.0` → `version-v0.48.0`）。仓库无独立 version 文件（`glob **/version*` 无命中；agate-summary 用 git tag 探测）。
- 变更范围：P2 `packages` 声明 4 包共享**单一协议版本** v0.48.0：

| package | 变更内容 | 旧版本 → 新版本 |
|---------|---------|----------------|
| agate-scripts | commit-msg-self-gate.py（_SELF_GATE_RE 扩展）+ check-retrospective.py（提醒行） | v0.47.0 → v0.48.0 |
| agate-tests | 3 个测试文件新增用例（test_check_protocol_consistency / test_commit_msg_self_gate / test_check_retrospective）+ integration test 断言更新 | v0.47.0 → v0.48.0 |
| agate-protocol-docs | README/README.zh-CN badge + CHANGELOG + UPGRADING（无破坏性变更节，见 §5） | v0.47.0 → v0.48.0 |
| agate-consistency | check-protocol-consistency.py（CHECK 10 + PROTOCOL_DIRS + main() split 修复） | v0.47.0 → v0.48.0 |

> 无越界：P4 改动（3 脚本 + 测试）全部落在 4 包内（P7 §3 已核实）。

## 4. CHANGELOG 更新确认

- 现状：CHANGELOG.md **无 [Unreleased] 段**（[0.47.0] 是 latest）。
- 更新动作（主 Agent 落地）：新增 `## [0.48.0] - 2026-08-16` 段，要点：
  - **新增（RM-AG0015）**：CHECK 10「协议文档脚本名引用漂移」gate——扫描协议文档面（PROTOCOL_FILES + PROTOCOL_DIRS + 根级 README/AGENTS + agate/UPGRADING + scripts/README + CHANGELOG）脚本名引用对照 `agate/scripts/` 实际文件，漂移报 ERROR；豁免 UPGRADING 对照表/formatters/3 hook 薄壳/count-tests.sh/scripts-README 退役名；CHANGELOG 历史名聚合单条 WARNING；phase-cards/rules 入 PROTOCOL_DIRS（引用检查升级严格）；main() CHECK 状态匹配改为 `split("-")[0] == key`（修复 CHECK1/CHECK10 前缀碰撞）。
  - **变更（RM-AG0017）**：commit-msg-self-gate 触发面补 `README.md`/`AGENTS.md`（根级精确名锚定，CHANGELOG 天然豁免），stderr 提示文案同步。
  - **变更（RM-AG0018 剩余）**：check-retrospective.py warnings 块追加「新缺口请登记 DEBT/roadmap」提醒行（纯提醒，无异常不输出）。
  - 测试：19 新增用例（770 = 基线 751 + 19），11 条 BDD 全 PASS；consistency 0 ERROR；ruff 通过。
  - **无破坏性变更**（本版本不在 CHANGELOG 标「破坏性变更」节）。
- `git log v0.47.0..HEAD --oneline`（36 commits）对照：本版本内容 = TAG0013 P1-P7 各阶段 commit + P0-brief/交接单（P1-P8 阶段产出）+ 上游 roadmap 规划 commit（10e15cf/40a1b41 等，多为 docs 规划，不重复计入 changelog 功能要点）。CHANGELOG [0.48.0] 聚焦 TAG0013 交付物即可。

## 5. UPGRADING 章节评估

- **结论：本版本无破坏性变更 → 无需迁移动作**。CHECK 10 是增量一致性检查（当前 0 漂移，不误伤），self-gate 触发面扩展与复盘提醒行均为内部行为，用户可见协议语义不变；已有项目升级不需要任何迁移步骤。
- **建议**：按 AGENTS.md 版本发布清单「更新 UPGRADING.md 新增本版本章节」，仍新增一节 `### v0.48.0 — 脚本一致性 gate（无破坏性变更）`，正文注明「无需迁移动作；升级只需 git pull + 重跑 install-hook.py」（与 v0.47.0 起各版本一节的结构保持一致，防漏更）。是否需要该节由主 Agent 决定——**不新增也不违反**任何强制 gate（P8 gate 只查 bump_type/debt_check/version/CHANGELOG）。

## 6. 临时资源清单

本任务为**纯文件系统 + git 操作**（脚本/测试/文档修改 + pytest 运行 + git diff --cached），未启动任何临时服务/进程/daemon，未占用端口，未做开发安装（无 editable install / 全局包安装）：

| 类型 | 明细 | 清理动作 |
|------|------|---------|
| 临时服务/进程 | 无 | 无需清理 |
| 临时数据 | pytest `tmp_path` fixture（自动清理）+ P6 假协议树（/tmp/p6-bdd* 临时目录） | pytest tmp_path 自动删除；`/tmp/p6-bdd678` 等已用完，可顺手删除（不影响 repo） |
| 开发安装 | 无（用系统 python3 + 既有 pytest/pyyaml） | 无需清理 |
| 工作区改动 | `agate-workspace/tasks/TAG0013-script-consistency/`（P1-P8 产出，需 commit）+ `active-tasks.md` 状态更新 | 随任务 commit 落地 |

> 主 Agent READY 收尾检查参考本清单执行；无需额外清理项。

## 7. P8 多包发布清单（implementer P8 要求）

逐包发布检查命令（P2 §5 gate_commands），主 Agent gate 通过后亲自执行：

| package | 发布检查命令 | 预期结果（P5 实测） |
|---------|-------------|-------------------|
| agate-scripts + agate-tests | `python3 -m pytest agate/tests/ -q --tb=no` | 768 passed / 2 skipped / 0 failed |
| agate-consistency | `python3 agate/scripts/check-protocol-consistency.py` | 0 ERROR（279 WARNING 基线） |
| agate-tests | `bash agate/tests/scripts/count-tests.sh` | 770（≥ 基线 751，无漂移） |
| agate-scripts/consistency | `~/.venvs/agate-dev/bin/ruff check agate/`（ruff） | All checks passed |
| agate-consistency | `python3 agate/scripts/check-protocol-consistency.py --strict`（仅参考，非 gate 判据） | exit 2（279 WARNING 含 CHANGELOG 聚合，CI 非 strict） |

## 8. 主 Agent 落地动作清单（P8 gate 通过后）

1. bump-version：README.md + README.zh-CN.md badge v0.47.0 → v0.48.0
2. CHANGELOG：新增 `[0.48.0]` 段（见 §4 要点）
3. UPGRADING：新增 v0.48.0 节（见 §5）
4. 单一 commit + tag：`git tag v0.48.0`（含 P8-release.md + .state.yaml phase: READY，若 .gitignore 忽略需 git add -f）
5. DEBT0001 关闭（tech-debt.md，closed 准入：task_id + P5/P6 evidence 引用）
6. 重跑 P5 gate（bump 后测试仍全绿）+ P1 §8 登记 `[SCOPE_RESOLVED]`（P7 §2 遗留，已提示主 Agent）

## 9. Lessons Learned

| 类别 | 教训 | 来源任务 | 日期 |
|------|------|---------|------|
| 流程 | 多子需求合并一批任务时，P1 必须全仓 grep 脚本名引用建影响面表（裸名 + 相对路径），避免「一轮轮来回改」；本任务 CHECK 10 影响面靠 P1 §4.4 计数正则 + 5 类豁免一次收敛 | TAG0013 | 2026-08-16 |
| 架构 | 新增一致性 CHECK 的编号碰撞是隐藏雷：CHECK 10 前缀与 CHECK 1 在 `startswith(key)` 判定下互相污染（BLOCKER-1）——新增编号 ≥10 的 CHECK 时须同步检查 main() 状态匹配逻辑 | TAG0013 | 2026-08-16 |
| 测试 | 触发面扩展（self-gate 正则）会与既有集成测试断言冲突（SCOPE+：test_csg_1 断言 README 不触发 → 更新为触发）；同类变更应先全仓 grep 相关测试再动手 | TAG0013 | 2026-08-16 |
