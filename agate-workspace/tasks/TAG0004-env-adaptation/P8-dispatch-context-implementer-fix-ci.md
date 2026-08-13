> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。

---
phase: P8
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0004
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

**P8 后 CI 修复**：PR #127 的 CI 双平台矩阵抓到了 3 个 Windows 真实问题，修复后补 commit。修复对象 2 个文件：

1. **`agate/scripts/check-protocol-consistency.py`**：Windows 下 `print("  agate 协议结构一致性检查 (P3-1)")`（L782）等中文输出在 cp1252 编码下崩 `UnicodeEncodeError: 'charmap' codec can't encode`。**修复**：文件入口处（`import sys` 后）加 `sys.stdout.reconfigure(encoding='utf-8')`（Python 3.7+，Windows 下强制 stdout 用 UTF-8，不影响 Linux 默认 UTF-8 行为）。
2. **`.github/workflows/protocol-tests.yml`**：
   - **shellcheck (Windows) exit 127**：`echo "$GITHUB_WORKSPACE/shellcheck-v0.10.0" >> $GITHUB_PATH` 指向不存在的目录（zip 解压出的是 `shellcheck.exe` 在 zip 根，无 `shellcheck-v0.10.0/` 子目录）→ PATH 加空目录 → `shellcheck` 命令找不到。**修复**：解压到 `$GITHUB_WORKSPACE/shellcheck/` 并 PATH 加该目录；调用处改 `shellcheck.exe` 或确认 bash 下 `shellcheck` 可解析（Windows Git Bash 下 PATH 中的 exe 通常可直接调 `shellcheck`，但为稳妥可用 `shellcheck.exe`）。
   - **consistency/gate-backstop (Windows) UnicodeEncodeError**：Windows job 的 python 命令前设 `PYTHONIOENCODING=utf-8`（或 step env）。**双保险**：脚本侧 reconfigure（上面第 1 点）+ CI 侧环境变量。

### 约束

- **修复对象 = worktree 的 `agate/` 目录 + `.github/workflows/`**（`/home/kity/oclab/agate/.worktrees/agate-TAG0004/`）。**禁止改主 checkout `/home/kity/oclab/agate` 和 `~/.agate`**。
- **只改 2 个文件**：`agate/scripts/check-protocol-consistency.py` + `.github/workflows/protocol-tests.yml`。不改其他（避免扩大回归面）。
- **最小改动**：consistency 脚本只加 stdout reconfigure（不重构打印逻辑）；CI yaml 只修 shellcheck PATH + 加 PYTHONIOENCODING。
- **Linux 行为不变**：`sys.stdout.reconfigure(encoding='utf-8')` 在 Linux UTF-8 环境无副作用；CI ubuntu job 不受影响。
- **自查**：
  - `python3 agate/scripts/check-protocol-consistency.py --strict` → 0 ERROR（本地 Linux）
  - `bats agate/tests/unit/check-protocol-consistency.bats`（若存在相关测试）或全量相关 bats 不回归
  - shellcheck 语法：改完 yaml 后无法本地跑 Windows job，但可 `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/protocol-tests.yml'))"` 验证 yaml 合法
  - 自查 ≠ gate，P8 后修复由主 Agent 验证 + 补 commit
- **格式约束**：约束节避免行首 `- PASS`/`- FAIL`。改用"通过/失败"或加引号。

### 上游关联

- PR #127 CI 失败 4 job：shellcheck/consistency/gate-backstop (windows) + bats (ubuntu bdd-25)。
- 根因 1：consistency 脚本中文 print 在 Windows cp1252 崩（本任务 Windows 兼容目标漏掉输出侧编码）。
- 根因 2：shellcheck Windows 安装 PATH 指向错误目录（`shellcheck-v0.10.0/` 不存在，实际解压到 zip 根）。
- 根因 3（bats ubuntu bdd-25）：tag v0.44.0 未推送——由主 Agent push tag 解决，**不在本修复范围**。

### 输入文件

- `agate/scripts/check-protocol-consistency.py`（L782 中文 print + 入口）
- `.github/workflows/protocol-tests.yml`（shellcheck Windows 安装步骤 L57-64 + consistency/gate-backstop Windows 步骤）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P8

路径：phase-cards/P8-release.md
---
# P8 — 发布

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P8 + internal_only: true + internal_only_reason 已声明 → 跳过，标记 READY
> ⑨ P8 subagent 化

## 如果是首次进入本阶段

1. 主 Agent 派发 releaser subagent（implementer P8 模式）执行发布准备
   1.1 写 P8-dispatch-context-implementer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. releaser subagent 产出 P8-release.md，**不执行 git commit/tag**
3. 主 Agent 执行 gate 验证 → 通过后执行 bump-version + CHANGELOG 更新 → 同一 commit + tag
4. 主 Agent 执行 READY 收尾检查（参考 P8-release.md 临时资源清单）
5. 更新 .state.yaml phase=READY → DONE

## 如果是重试

→ 读 agate/rules/state-transitions.md 确认 retry 上限（P8 MAX=2）

## 执行方式

releaser subagent（implementer P8 模式）执行以下发布准备步骤：

1. 读取 P2-design.md packages 声明，确定需 bump 的包
2. 为每个 package 执行发布检查命令
3. 更新 CHANGELOG [Unreleased] → 版本号
4. 确认债务清单：读 `{AGATE_WORKSPACE}/debt/tech-debt.md`（若存在），在 P8-release.md 写入 `debt_check:` 字段（TAG0001 Phase 3）
5. 产出 P8-release.md（含 bump_type、版本号变更确认、CHANGELOG 更新确认、debt_check 字段、临时资源清单）

> **注意**：releaser subagent 不执行 bump-version / git commit / git tag，这些由主 Agent 在 gate 验证通过后亲自执行。

## releaser→主 Agent 交接

P8-release.md 中的**临时资源清单**是 releaser→主 Agent 的交接文件：
- releaser subagent 负责写入临时资源清单（本任务启动的临时服务/进程/数据/开发安装）
- 主 Agent 使用该清单执行 READY 收尾检查中的清理工作
- P8-release.md 由 releaser subagent 产出，主 Agent 不直接编写

## 前置条件

- [ ] P7-consistency.md 通过（无 BLOCKER / DESIGN_GAP 已配对）
- [ ] P2-design.md packages 声明（决定哪些包需要 bump）

## 产出规格

P8-release.md 必须包含：
- `bump_type: major / minor / patch`
- `debt_check: none / reviewed`——债务清单确认留痕（TAG0001 Phase 3）：`none` = 本次无关注项（合法选项，不视为失败）；`reviewed` = 已核对，建议正文附条目 id 清单。只查留痕存在，不查内容达标、不阻断发布
- 版本号变更确认（version 文件已修改）
- CHANGELOG [Unreleased] → 新版本号
- 临时资源清单：本任务启动的临时服务/进程/数据/开发安装

## gate 规则

```bash
check-gate.sh P8 $TASK_DIR
```

- bump_type 字段存在
- `debt_check` 字段存在（缺失 → exit 1；内容任意，含 `none` / 未关闭债务 → 不阻断，BDD-17）
- 暂存区有 version 文件变更
- 暂存区 CHANGELOG 有变更

主 Agent **必须亲自执行**以下验证（不可跳过、不可委托 subagent）：
- 从 P2 packages 逐包读取发布检查命令并执行 → 全部 exit 0
- 重跑 P5 gate（gate_commands.P5 exit 0 + failed==0）
- `git log v{prev_version}..HEAD --oneline` 对照 CHANGELOG 无遗漏
- 从 P2 packages 验证 version 文件路径

## READY 收尾检查（P8 gate 通过后）— 主 Agent 亲自执行（不派发 subagent）

参考 P8-release.md 临时资源清单执行清理。以上检查项无 gate 脚本自动验证（已知缺口），**必须逐项实际执行检查命令**（如 `ps aux | grep debug` 确认服务已停止、`git status` 确认工作区干净），不得仅凭记忆打勾。

**状态与版本**：
- [ ] .state.yaml phase == READY
- [ ] {AGATE_WORKSPACE}/tasks/active-tasks.md 任务行状态已更新
- [ ] git 工作区干净
- [ ] git tag 已创建

**测试环境已清理**：
- [ ] 调试服务/进程已停止
- [ ] 临时数据已删除
- [ ] 测试占用的端口已释放

**开发环境已还原**：
- [ ] 开发安装已卸载
- [ ] 系统环境无污染
- [ ] 项目依赖恢复到发布版本

**协议一致性（改造协议自身的任务必做，TAG0001-0003 批次 D4 教训）**：
- [ ] **在干净 checkout 上跑一次 `check-protocol-consistency.py`**（`git clone` 到临时目录或 CI 兜底确认），0 ERROR
  - 原因：本地 worktree 的 `.worktrees` 路径过滤会掩盖任务产出文件的扫描问题，本地 0 ERROR ≠ CI 0 ERROR
  - 若无法干净 checkout，**至少确认 CI 的 consistency job 对本次 PR 通过**
- [ ] **确认任务产出目录（`docs/tasks/` 或 `{AGATE_WORKSPACE}/tasks/`）不被一致性检查器误扫**（若为 dogfooding 任务，任务产出应已在 `NARRATIVE_DIRS` 白名单）

**生产环境无残留**：
- [ ] 无 PROD_TOUCHED 标记（触发写 `[PROD_TOUCHED] {描述}`，未触发写 `[PROD_NOT_TOUCHED]`）
- [ ] 生产数据/API 未被测试写入

## 推进条件（全部满足才写 phase: READY）

- [ ] bump-version 完成 + P5 重跑全绿
- [ ] CHANGELOG 已更新
- [ ] git tag 已创建
- [ ] READY 收尾检查全部通过

## 常见错误

1. **不重跑 P5 gate**：bump-version 后直接 tag，不确认测试仍全绿
2. **CHANGELOG [Unreleased] 留在模板状态**：版本 bump 完但 CHANGELOG 没更新
3. **忘记清理测试环境**：debug server 还在跑、临时数据没删 → READY 不干净
4. **临时资源清单遗漏**：P4/P5 阶段启动的服务/安装的包没记录 → 清理时遗漏
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- READY → DONE：任务完成，代码可合并/发布
- 本任务是 agate 链条的终点——P8 完成后任务状态转为 DONE

> 完成 → 任务 DONE
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0004`；协议 v0.44.0（tag 已打，未推送）
- 关键路径：改动 `agate/scripts/check-protocol-consistency.py` + `.github/workflows/protocol-tests.yml`；产出 `agate-workspace/tasks/TAG0004-env-adaptation/P8-fix-ci.md`
- 查证结果：shellcheck zip 解压出 `shellcheck.exe`（zip 根，无子目录）；consistency L782 print 中文；Windows cp1252 输出崩
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.sh` 审计失败。
