---
phase: P8
task_id: TAG0011-test-migration
type: release
parent: P7-consistency.md
trace_id: TAG0011-P8-20260815
status: draft
created: 2026-08-15
agent: implementer
---

# P8 发布准备记录 — agate 测试框架迁移（bats → pytest，TAG0011）

> 本文件是**发布计划文档**——声明 bump 计划 / debt_check / 版本号确认 / 本任务 CHANGELOG 条目草稿 / 临时资源清单。
> **不执行版本 bump、不 git commit/tag**（releaser 不执行；bump + CHANGELOG 落地 + tag + PR 由主 Agent 在 P8 gate 验证通过后亲自执行）。

## bump_type

- **bump_type: minor**（v0.46.0 → **v0.47.0**）
- 判定依据（dispatch-context 约束 + AGENTS.md 版本发布节 + HANDOFF-TAG0010-0011.md §8b）：
  - 测试框架迁移（bats → pytest）：破坏性变更（测试命令 / 依赖 / 冒烟机制 / 目录结构）+ 新增能力（conftest fixture 体系 / windows_smoke marker / count-tests 改写）——按 minor 发布，与 TAG0010（v0.46.0，产品脚本 Python 化）构成"双阶段达成全 Python"的连续两个 minor。
  - 与 TAG0010 分两次 bump、两个 tag（v0.46.0 + v0.47.0），统一一个 PR 合并（**普通 merge --no-ff**，禁 squash——v0.31.0 事故，AGENTS.md release PR 铁律；HANDOFF L75/107 双 tag 祖先要求）。

## 受影响包（P2-design.md frontmatter `packages`）

> 5 包全部随同一个版本 bump（agate 协议本体单版本号，非逐包独立版本）。P2 §2/§5 批次 0-18 与 P4 实际执行批次一一对应（P7 §3.3 已核对一致；批次 17 从 P2「退役批」细化为「退役 + count-tests 改写 + CI 同步」、新增批次 18「bats 删档」均属设计内细化）。

| 包 | 涉及改动 | P4 批次 | 验证 |
|----|---------|--------|------|
| agate-tests | 60 个 .bats → 60 个 test_*.py（46 unit + 6 regression + 6 integration + test_sanity.py + scripts/test_check_platform_assumptions.py）+ 新增 conftest.py | 0-16 + 18 | P5 pytest 750 collected / 748 passed / 2 skipped（Pillow 可选），0 .bats 残留 |
| agate-test-helpers | helpers/ 三文件（load.bash / fixtures.bash / git-helper.bash）退役 → conftest.py fixture 体系（agate_root / agate_scripts / python_exe / task_dir / git_repo / run_cli / py_path + add_* 纯函数） | 0 + 18 | sanity 6 + helpers_python 3 全绿（P6 BDD-6） |
| agate-test-scripts | count-tests.sh 改写为 pytest 收集计数（750）+ check-windows-smoke.sh/.bats 退役（marker 承接） | 17 | count-tests.sh 输出「总计：750」≥ 749（P6 BDD-4）+ check-windows-smoke.* 0 残留（P6 BDD-12） |
| agate-protocol-docs | P1 §5 表 E 文档重写：platform-notes / SETUP / UPGRADING v0.47.0 章节 / dispatch-protocol / git-integration / AGENTS.md（仓库根）/ tests/README.md / scripts/README.md / handoff-template / protocol-alignment-review / formatters/README（bats 行保留） | 15 | P7 §3.4 核对：表 E 对应项 0 bats 引用（UPGRADING v0.47.0 章节按迁移对照表预期保留） |
| agate-ci | protocol-tests.yml：bats job → pytest job（ubuntu 全量 + windows `-m windows_smoke` 冒烟）+ ruff 扫 agate/（含 tests）+ 删除 bats 安装步骤 | 17 | P6 BDD-11（env-adapt-docs 9 passed）+ P6 BDD-5（windows_smoke 收集 78/750） |

## 版本号变更确认（计划，非已执行）

- 当前版本：**v0.46.0**（git tag v0.46.0 = 1594f0c，`git describe --tags --abbrev=0` = v0.46.0，已核实；README.md L6 + L32 version badge 均 v0.46.0，TAG0010 P8 标注的 L32 残留 v0.43.0 已随 v0.46.0 修正）
- 计划新版本：**v0.47.0**（P8 gate 通过后由主 Agent 执行）
- 需更新的版本引用（参考 AGENTS.md 版本发布节，主 Agent 亲自执行）：
  - README.md version badge：L6 + L32 `v0.46.0` → `v0.47.0`
  - CHANGELOG.md 新增 `[0.47.0]` 节（当前 CHANGELOG 顶部为 `[0.46.0]`，无 [Unreleased] 占位；草稿见下节，置于 [0.46.0] 之上）
  - UPGRADING.md v0.47.0 章节：P4 批次 15 已写完整章节（含破坏性变更全表 + CI matrix + ruff 覆盖），版本号已写 v0.47.0，无需占位更新
  - git tag v0.47.0（release 前确认 P5 重跑全绿 + READY 收尾检查全过）
- agate 仓库无独立 version.txt 文件（版本引用 = README badge + CHANGELOG + UPGRADING + git tag）

## debt_check

- **debt_check: none**
- 核对过程：读取 `{AGATE_WORKSPACE}/debt/tech-debt.md`——worktree（`agate-workspace/` 下无 `debt/` 目录）与主 checkout（`/home/kity/oclab/agate/agate-workspace/` 下无 `debt/`）**均不存在**该文件（无债务登记目录，8→9 子目录集为可选启用，本仓库未启用 debt/）。
- `git log v0.46.0..HEAD --grep="TAG0011"` 42 条提交中无 `retreat:` 回退提交；本任务无 `source: retreat` DEBT 条目登记。
- P7-consistency.md：BLOCKER=0 / DEVIATION-CRITICAL=0 / DESIGN_GAP 未配对=0 / SCOPE+ 未闭环=0；1 条非关键 DEVIATION（dispatch-protocol.md L878「pytest/bats 结果」文档重写残留）已在 **P7 提交（7b07001）中顺手修复**（L878 现为「测试类证据（pytest 结果）」），发布前无遗留偏差。无关注项，合法选项 `none`。

## 本任务变更摘要（CHANGELOG 草稿，供主 Agent 落地到 CHANGELOG.md）

> `git log v0.46.0..HEAD --oneline --grep="TAG0011"` 共 **42 条提交**（P1-P7 全阶段），下方摘要覆盖 P1 12 BDD + P4 批次 0-18 全部，无遗漏。log 范围内另有 2 条非 TAG0011 提交（`187248b` TAG0010-READY v0.46.0 发布完成 + `0ab7b60` TAG0010 归档）——属 v0.46.0 发布后收尾，内容已含于 v0.46.0 CHANGELOG，不入本版本。

### 破坏性变更（TAG0011 测试框架 bats → pytest 迁移：测试命令/依赖/冒烟机制/目录）

- **测试运行器从 Bats 全面迁移到 pytest**：`agate/tests/` 下 60 个 `.bats` 文件 / 749 @test 迁移为 `test_*.py` pytest 用例（46 unit + 6 regression + 6 integration + test_sanity.py + scripts/test_check_platform_assumptions.py），`.bats` 全部删除（0 残留）；测试命令从 `bats <file>` 改为 `python3 -m pytest agate/tests/`
- **`agate/tests/helpers/` 三文件退役**：load.bash / fixtures.bash / git-helper.bash（526 行）→ `agate/tests/conftest.py` fixture 体系承接（会话级 agate_root/agate_scripts/python_exe + 函数级 task_dir/git_repo/run_cli/py_path + add_* 纯函数）
- **`check-windows-smoke.sh` + `check-windows-smoke.bats` 退役**：Windows CI 冒烟由 `@pytest.mark.windows_smoke` marker 承接（`python -m pytest agate/tests/ -m windows_smoke`，78/750 代表用例）——语义与退役脚本「每文件第 1 个用例 + 平台关键词用例」一致
- **依赖变化**：「Bats + shellcheck + python3-yaml」→「**pytest + pyyaml**」（shellcheck 仍用于 3 个 hook 薄壳静态检查，CI shellcheck job 保留）
- **CI job 更名**：`.github/workflows/protocol-tests.yml` 的 `bats` job → `pytest` job（ubuntu 全量 + windows `-m windows_smoke` 冒烟；删除 bats 安装步骤）；分支保护 required checks 需更新为 `pytest` job 实际名（含平台后缀）
- **ruff 覆盖范围扩展**：`ruff check agate/scripts/` → `ruff check agate/`（含 tests，测试代码纳入静态检查）
- 已部署项目测试命令/CI 升级指引见 `agate/UPGRADING.md` v0.47.0 章节（迁移前→迁移后命令对照表 + CI matrix 说明）

### 新增

- **`agate/tests/conftest.py` fixture 体系**：AGATE_ROOT 反推解析（fail-closed）+ `task_dir`（create_task_dir 等价）/ `git_repo`（git_init 等价）/ `run_cli`（run/$status/$output 等价，`CommandResult.output` 合并流属性复刻 bats `$output` = stdout + stderr 语义）/ `py_path`（Windows cygpath 转换）/ `python_exe`（python3→python 探测）
- **`@pytest.mark.windows_smoke` marker**：78 用例显式打标（平台敏感机制代表集），pyproject `[tool.pytest.ini_options] markers` 注册消除 PytestUnknownMarkWarning
- **`pyproject.toml` `[tool.pytest.ini_options]`**：testpaths=["agate/tests"] + markers 注册；`[tool.ruff] src` 扩展 `["agate/scripts", "agate/tests"]`
- **`count-tests.sh` 改写**：`pytest --collect-only` 收集计数（实测 750 ≥ 749 迁移基线），脚本路径与引用不变，守护职责延续

### 变更

- 协议文档表 E 全量重写（bats→pytest 引用同步）：AGENTS.md（仓库根）/ tests/README.md / scripts/README.md / platform-notes.md / SETUP.md / dispatch-protocol.md / git-integration.md / handoff-template / protocol-alignment-review.md / UPGRADING.md v0.47.0 迁移章节
- check-windows-smoke 描述 →「退役，marker 承接」；formatters/README.md `bats | generic-tap.sh` 行按 P2 决策保留（formatters 支持多框架）
- 测试用例数：749 @test + 1 流语义回归锁（EB.8 等价物）→ **750 collected**（`--collect-only ≥ 749` BDD-1 基线达成）

### 测试

- 全量 pytest **750 collected / 748 passed / 2 skipped**（Pillow 可选分支 skipif，设计行为非失败）/ 0 failed（P5/P6 实跑）+ consistency --strict 0 ERROR 0 WARNING + ruff 0 error（108 py）+ 平台假设扫描器全树 0 命中 + encoding 守卫 0 违规 + ast.parse py38 兼容 0 违规
- 12/12 BDD 全 PASS（P6 回归验收，refactor 口径）+ P7 一致性 BLOCKER=0（1 条文档 DEVIATION 已在 P7 提交修复）

### 文档

- 表 E 文档重写（见「变更」）；UPGRADING.md 新增 v0.47.0 迁移章节（bats→pytest 破坏性变更逐条列 + CI matrix + ruff 覆盖）
- tests/README.md 快速开始/覆盖度表/CI 章节/目录结构全量改 .py；R2.4 已知风险（archive flaky）迁移后重评

## 临时资源清单（releaser → 主 Agent READY 收尾交接）

本任务为纯测试迁移 + 文档 + CI 变更，P4/P5/P6/P7 阶段未启动任何临时服务/进程，未创建持久临时数据。逐项核对：

- **临时服务/进程**：无（P4/P5/P6 自查均为 pytest / ruff / shellcheck / consistency / 扫描器本地命令，无 debug server / daemon / 网络监听启动）
- **临时数据**：无持久临时数据。运行时 ephemeral 临时文件全部在 pytest `tmp_path` 内（每用例独立目录，pytest 自动清理），不落盘；P5-test-results/ 与 P6-evidence/ 为阶段产出物，属任务目录内正常产物，随任务归档，不需单独清理
- **开发安装**：开发用共享 venv `~/.venvs/agate-dev`（ruff + pyyaml + pytest，AGENTS.md 开发环境节登记）——**既有共享开发环境，非本任务启动的临时安装，无需卸载**；未做 editable install / 全局包安装
- **端口占用**：无（无网络监听服务）
- **工作区残留**：worktree `agate-TAG0010`（承载 TAG0010 + TAG0011 双任务）本身为隔离开发环境，两任务全部 READY 后由主 Agent 按 HANDOFF 统一 PR 合并处理（merge --no-ff + 清理）

## 主 Agent 待执行清单（本任务不执行）

- 预跑 `check-gate.sh P8 $TASK_DIR` 确认 P8 gate 通过（bump_type 字段 + debt_check 字段 + 暂存区 version/CHANGELOG 变更）
- 从 P2 §4.1 packages 逐包读取发布检查命令并执行 → 全部 exit 0
- 重跑 P5 gate（`python3 -m pytest agate/tests/ -q --tb=no` 全绿 + consistency --strict 0 ERROR + ruff 0 error + scan 0 命中）确认 bump 后仍绿
- `git log v0.46.0..HEAD --oneline` 对照本 CHANGELOG 草稿无遗漏
- 落地本节 CHANGELOG 草稿到 CHANGELOG.md `[0.47.0]`（置于 [0.46.0] 之上；bump-version + CHANGELOG 更新 → **同一 commit + tag**，T080 教训）
- 更新版本引用：README badge（L6 + L32）`v0.46.0` → `v0.47.0`；UPGRADING v0.47.0 章节版本号已就位无需改
- `git tag v0.47.0`；与 TAG0010 的 v0.46.0 tag 统一 PR **普通 merge（--no-ff）**，禁 squash（v0.31.0 事故）
- **协议一致性收尾**：在干净 checkout 跑一次 `check-protocol-consistency.py`（或确认 CI consistency job 对本次 PR 通过）——`.worktrees` 路径过滤会掩盖任务产出文件的扫描问题，本地 0 ERROR ≠ CI 0 ERROR（TAG0001 批 D4 教训）；确认 `{AGATE_WORKSPACE}/tasks/` 在一致性检查器 NARRATIVE_DIRS 白名单（dogfooding 任务产出不被误扫）
- **CI required checks**：pytest job 名（ubuntu/windows 平台后缀）、ruff job 目标 `agate/`——分支保护 required checks 需同步（TAG0004 v0.44.0 教训；UPGRADING v0.47.0 §② 已提醒）
- **Windows CI**：`pytest (windows-latest)` 冒烟为 minimal_validation 兜底项（P6 BDD-5「待 Windows CI 确认」）——PR 合入后确认该 job 全 PASS，若失败回退修复重验
- READY 收尾检查按 P8 卡片清单逐项实际执行（不凭记忆打勾）

## Lessons Learned

| 类别 | 教训 | 来源任务 | 日期 |
|------|------|---------|------|
| 架构 | **跨语言测试迁移必须保留「语义等价」而非「机械翻译」**：bats `$output`（stdout+stderr 合并流）vs pytest 流分离是最大语义偏差源（P2-review BLOCKER-1），映射表 + 合并流 `.output` 属性 + 回归锁用例（EB.8 等价物）把「空/非空判断走合并流」固化为规则——否则 stderr 内容会被静默吞掉、反向语义假绿 | TAG0011 | 2026-08-15 |
| 架构 | **单根 conftest.py 替代三文件 helpers 是迁移的稳定锚点**：会话级 fixture（AGATE_ROOT 反推 fail-closed）+ 函数级 fixture（task_dir/git_repo/run_cli）+ 纯函数 add_* 全部收敛一个文件（~350 行），pytest 自动递归加载零样板，各批迁移只追加 fixture；分层 conftest 会重复样板且本任务无目录级覆写需求（P2 B1 决策） | TAG0011 | 2026-08-15 |
| 测试 | **超大批迁移必须子批化 + 命名契约兜底**：批次 8（check-gate 146 @test）按 gate_p0..p8 函数边界切 8 子批（≤32 @test），`-k` 关键字按 module/function 命名契约匹配（`-k "json"` 命中 test_agate_json_get）——命名契约即批次验证命令的自校验，命名违约 = 验证命令跑不通即暴露 | TAG0011 | 2026-08-15 |
| 流程 | **测试代码自身必须过平台无关纪律**：迁移产出的 test_*.py 会被 check-platform-assumptions.py 全树扫描（R1-R5）+ encoding 守卫 + py38 ast 检查——fixture 内容运行时构造（防字面命中）、所有文本 I/O 显式 encoding="utf-8"、ruff target-version py38（禁 3.9+ 语法），测试代码自己是最严格的「元测试」对象 | TAG0011 | 2026-08-15 |

## 环境隔离

`[PROD_NOT_TOUCHED]`——本阶段仅读取 worktree 内产出文件与 git log/status 核验，未接触生产环境。
