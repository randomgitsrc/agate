---
phase: P8
task_id: TAG0010-python-migration
type: release
parent: P7-consistency.md
trace_id: TAG0010-P8-20260815
status: draft
created: 2026-08-15
agent: implementer
---

# P8 发布准备记录 — agate 产品逻辑 Python 化（TAG0010）

> 本文件是**发布计划文档**——声明 bump 计划 / debt_check / 版本号确认 / 本任务 CHANGELOG 条目草稿 / 临时资源清单。
> **不执行版本 bump、不 git commit/tag**（releaser 不执行；bump + CHANGELOG 落地 + tag + PR 由主 Agent 在 P8 gate 验证通过后亲自执行）。

## bump_type

- **bump_type: minor**（v0.45.0 → **v0.46.0**）
- 判定依据（dispatch-context 约束 + AGENTS.md 版本发布节 + HANDOFF-TAG0010-0011.md §8b）：
  - 新增 py 化能力（agate_common.py 公共库 / 30 脚本 py 化 / install-hook.py / pyproject.toml ruff 规则集）+ **破坏性变更**（30 脚本改名/删档、pyyaml 强制依赖、hook 薄壳 fail-closed、shellcheck→ruff）——同时含新能力与破坏性变更，判 **minor**。
  - 与 TAG0011（测试框架迁移，下一 minor v0.47.0）分两次 bump、两个 tag，统一一个 PR 合并（普通 merge --no-ff，AGENTS.md release PR 铁律）。

## 受影响包（P2-design.md frontmatter `packages`）

> 6 包全部随同一个版本 bump（agate 协议本体单版本号，非逐包独立版本）。P2 §3.2 批次 0-4 与 P4 实际执行批次一一对应（P7 §3 已核对一致）。

| 包 | 涉及改动 | P4 批次 | 验证 |
|----|---------|--------|------|
| agate-scripts | 30 个 .sh → py（同名换后缀）+ `agate_common.py` 公共库（gate-result.sh + agate-workspace-resolve.sh 删档并入）+ `install-hook.py` + 3 hook 薄壳化 | 0/1a-1e/2a-2f/3a-3f | P5 ruff 0 error（47 py）+ shellcheck 收敛 3 薄壳 0 error + py38 target + encoding 守卫 |
| agate-hooks | pre-commit/commit-msg-self-gate/pre-push-gate 薄壳化 + 新增 .py 主程序 + install-hook.py（复制模式 .agate-root 标记） | 3 | install-hook.bats / pre-commit-hook.bats / pre-push-hook.bats / commit-msg-self-gate.bats 全绿 |
| agate-consistency | check-protocol-consistency.py CHECK 9 锚点表同步（SCRIPT_ALIGNMENT_ANCHORS 全量 .py 化）+ check-platform-assumptions.py 扩展 .py 扫描 | 4a/4b | P5 consistency --strict 0 ERROR 0 WARNING |
| agate-tests | bats 调用点 sh→py（机械调用面）+ 5 文件断言级调整（38→40 用例）+ helpers-python.bats 重构 + check-platform-assumptions.bats 14→16 用例 | 1a-1e/2a-2f/3a-3f | P5 全量 bats 733 ok / 0 not ok，count-tests.sh 727 不漂移 |
| agate-protocol-docs | 表 B 9 文档引用同步 + 5 重写文档（scripts/README / platform-notes / UPGRADING v0.46.0 章节 / SETUP / LIMITATIONS）+ rules/assets 引用同步 | 4c-1/4c-2/4e | P7 复核 .sh 残留 0（仅 3 薄壳 + tests/scripts） |
| agate-ci | protocol-tests.yml：shellcheck job 扫描面收敛 3 薄壳 + 新增独立 ruff job + check-platform-assumptions.py 调用目标 | 4c-3 | P5 ci-backstop 对照 .gate-result.json 通过 |

## 版本号变更确认（计划，非已执行）

- 当前版本：**v0.45.0**（git tag v0.45.0 = f8b5194，`git describe --tags --abbrev=0` = v0.45.0，已核实；README.md L6 version badge v0.45.0）
- 计划新版本：**v0.46.0**（P8 gate 通过后由主 Agent 执行）
- 需更新的版本引用（参考 AGENTS.md 版本发布节 + 版本引用文件清单，主 Agent 亲自执行）：
  - README.md version badge：L6 `v0.45.0` → `v0.46.0`（**另 L32 残留 `v0.43.0` badge，TAG0005/TAG0009 P8 已两次标记，本次务必一并核对修正**）
  - CHANGELOG.md `[Unreleased]` → `[0.46.0]`（草稿见下节）
  - UPGRADING.md v0.46.0 章节：P4 批次 4c-2 已写占位章节（含破坏性变更全表 + install-hook 迁移命令 + shellcheck→ruff + pyyaml 强制 + 无 bash 可行）——**版本号占位文字「最终版本号由 P8 确认」需更新为 v0.46.0**
  - git tag v0.46.0（release 前确认 P5 重跑全绿）
- agate 仓库无独立 version.txt 文件（版本引用 = README badge + CHANGELOG + UPGRADING + git tag）

## debt_check

- **debt_check: none**
- 核对过程：读取 `{AGATE_WORKSPACE}/debt/tech-debt.md`——worktree 与主 checkout（`/home/kity/oclab/agate/agate-workspace/debt/`）该文件**均不存在**（无 `debt/` 目录）。`git log v0.45.0..HEAD --grep="^retreat"` 0 条回退提交；本任务无 `source: retreat` DEBT 条目登记。P4 的 5 条 [DESIGN_GAP] 均已 P7 REVIEWED 配对（design_gap_reviewed_count=5）且非债务；1 条 [DEVIATION]（UPGRADING 占位版本号，P7 已确认方向合理）。无关注项，合法选项 `none`。

## 本任务变更摘要（CHANGELOG 草稿，供主 Agent 落地到 CHANGELOG.md）

> `git log v0.45.0..HEAD --oneline --grep="TAG0010"` 共 33 条提交（P0-P7 全阶段），下方摘要覆盖全部批次，无遗漏。（log 范围内的 TAG0005/TAG0009 原始提交、docs/AGENTS/roadmap/交接单、TAG0011-P0 提交内容均已含于 v0.45.0 发布或属项目开发资料，不入本版本 CHANGELOG。）

### 破坏性变更（TAG0010 agate 产品逻辑 Python 化：30 个脚本跨语言迁移）

- **`agate/scripts/` 全部 30 个 `.sh` 的 bash 逻辑迁移为 Python（`.py`）**：24 个同名换后缀（check-changelog/check-frontmatter/check-state-yaml/check-p6-format/check-scope-resolved/agate-archive-stale-outputs/agate-extract-context/agate-next-card/agate-render-dispatch-prompt/agate-summary/agate-changes/agate-migrate-workspace/check-platform-assumptions/check-state-transition/check-retrospective/check-pruning/check-debt/check-tdd-red/check-gate/check-p6-evidence/check-p6-provenance/agate-capture-env-baseline/agate-retreat-to/agate-inject-card）+ `install-hook.sh` → `install-hook.py`；**直接调用脚本的用户调用命令从 `bash xxx.sh` 改为 `python3 xxx.py`**
- **3 个 git hook 入口保留 `.sh` 薄壳**（pre-commit-gate / commit-msg-self-gate / pre-push-gate）：只做「AGATE_ROOT 自定位 + python 探测 + exec py 主程序」，失败 **fail-closed 阻断 commit**（无 sh 兜底逻辑）；`PROD_TOUCHED` / `AGATE_ALIGNMENT_REVIEW_THRESHOLD` 锚点关键字存活于薄壳
- **`gate-result.sh` + `agate-workspace-resolve.sh` 删档并入 `agate_common.py`**：函数库（write_gate_result/read_state_phase/read_state_task_id/has_staged_phase_change/resolve_formatter/run_test_with_formatter/resolve_workspace/resolve_agate_root/probe_python/run_git/MAX_RETRY_MAP）合并为单一公共模块，执行模式输出 `AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行（契约不变）
- **pyyaml 从「可选」变「强制依赖」**：agate_common.py 及所有状态读取工具 import yaml，缺失时 fail-closed exit 1；Pillow 仍为可选（仅 check-p6-evidence.py 像素方差/ahash）
- **shellcheck → ruff**：shellcheck 扫描面收敛到 3 个 hook 薄壳；Python 脚本改用仓库根 `pyproject.toml` 规则集（`ruff check agate/scripts/`），CI 新增独立 ruff job
- **无 bash 环境（纯 cmd/PowerShell）成为可行选项**：gate 脚本全部 Python 化可直接运行（仅 git hook 入口薄壳仍需 sh / Git for Windows）
- 已部署项目升级指引见 `agate/UPGRADING.md` v0.46.0 章节（Windows 复制模式用户必须重跑 `python3 ~/.agate/scripts/install-hook.py`）

### 新增

- **`agate_common.py` 公共库**（P2 §3.1 设计，批次 0）：承载原 gate-result.sh + agate-workspace-resolve.sh 全部函数库，杜绝函数跨脚本复制漂移；MAX_RETRY_MAP 单一数据源
- **`install-hook.py`**：软链安装（Windows 复制模式 + 写 `.agate-root` 标记）+ chmod + 备份既有 hook + `.gitignore` 检测
- **`pyproject.toml` ruff 规则集**：`target-version = "py38"`（拒绝 3.10+ 语法，BDD-8）+ select/ignore 组合使既有 18 py 与新 py 全部 0 违规
- **hook 链 Python 化**：pre-commit-gate.py / commit-msg-self-gate.py / pre-push-gate.py 承载完整调度逻辑（12 子脚本 `bash xxx.sh` → `sys.executable xxx.py`；PROD_TOUCHED 三步检测 / dispatch-context hash 校验 / write_gate_result）
- **`check-platform-assumptions.py`** 扩展覆盖 `.py` 扩展名 + `r2_exempt` docstring 块豁免（docstring 内示例命令不命中 R2）

### 变更（实现细节，行为等价）

- `ci-gate-backstop.py` `resolve_tasks_dir` 改调 `agate_common.resolve_workspace`（消除对 agate-workspace-resolve.sh 的 bash subprocess，`sys.executable` 自举）
- 既有 18 个 `.py` 工具保持 subprocess 调用（不改写功能）
- 5 个测试文件断言级调整（38→40 用例）；bats 机械调用面 sh→py 全量同步
- check-gate.py 拆 P0-P8 分支子任务实现（大文件拆分）

### 测试

- 全量 733 bats ok / 0 not ok（count-tests.sh 727 @test 不漂移）+ consistency --strict 0 ERROR 0 WARNING + ruff 0 error（47 py）+ shellcheck 0 error（3 薄壳）+ 平台扫描器零命中 + ci-backstop 通过

### 文档

- scripts/README.md / platform-notes.md / SETUP.md / LIMITATIONS.md 重写（py 化引用 + pyyaml 强制 + 薄壳 fail-closed + 无 bash 可行）
- UPGRADING.md 新增 v0.46.0 章节（破坏性变更全表 + install-hook 迁移命令 + shellcheck→ruff + pyyaml 强制 + 无 bash 环境说明）+ 历史章节引用 py 化
- check-protocol-consistency.py CHECK 9 锚点表全量同步 py

## 临时资源清单（releaser → 主 Agent READY 收尾交接）

本任务为纯代码迁移 + 文档 + CI 变更，P4/P5/P6/P7 阶段未启动任何临时服务/进程，未创建持久临时数据。逐项核对：

- **临时服务/进程**：无（P4/P5/P6 自查均为 bats / ruff / shellcheck / consistency / 扫描器本地命令，无 debug server / daemon / 网络监听启动）
- **临时数据**：无持久临时数据。运行时 ephemeral 临时文件全部在 `$BATS_TEST_TMPDIR` 内（bats 每用例自建自清），不落盘；P5-test-results/ 与 P6-evidence/ 为阶段产出物，属任务目录内正常产物，随任务归档，不需单独清理
- **开发安装**：开发用共享 venv `~/.venvs/agate-dev`（ruff + pyyaml + bats，AGENTS.md 开发环境节 + 交接单登记）——**既有共享开发环境，非本任务启动的临时安装，无需卸载**；未做 editable install / 全局包安装
- **端口占用**：无（无网络监听服务）
- **工作区残留**：worktree `agate-TAG0010`（承载 TAG0010 + TAG0011 双任务）本身为隔离开发环境，两任务全部 READY 后由主 Agent 按 HANDOFF 统一 PR 合并处理（merge --no-ff + 清理）

## 主 Agent 待执行清单（本任务不执行）

- 预跑 `check-gate.sh P8 $TASK_DIR` 确认 P8 gate 通过
- 重跑 P5 gate（bats 733 全绿 / consistency --strict 0 ERROR / ruff 0 error / shellcheck 0 error / 扫描器零命中）确认 bump 后仍绿
- 落地本节 CHANGELOG 草稿到 CHANGELOG.md `[0.46.0]`（bump-version + CHANGELOG 更新 → **同一 commit + tag**，T080 教训）
- 更新版本引用：README badge（L6 + L32 残留 v0.43.0）/ CHANGELOG / UPGRADING.md v0.46.0 章节占位文字确认
- `git tag v0.46.0`；TAG0011 READY 后 `git tag v0.47.0`；统一 PR **普通 merge（--no-ff）**，禁 squash（v0.31.0 事故）
- **协议一致性收尾**：在干净 checkout 跑一次 `check-protocol-consistency.py`（或确认 CI consistency job 对本次 PR 通过）——`.worktrees` 路径过滤会掩盖任务产出文件的扫描问题，本地 0 ERROR ≠ CI 0 ERROR（TAG0001 批 D4 教训）
- **CI required checks**：shellcheck job 改名收敛 3 薄壳、新增 ruff job、bats job 平台矩阵——分支保护 required checks 需同步（TAG0004 v0.44.0 教训）
- READY 收尾检查按 P8 卡片清单逐项实际执行（不凭记忆打勾）

## Lessons Learned

| 类别 | 教训 | 来源任务 | 日期 |
|------|------|---------|------|
| 架构 | **批量跨语言迁移必须按依赖分批 + 每批全量验证**：30 脚本 sh→py 按 P1 表 E 依赖批次（0 公共库 → 1 自足叶 13 → 2 复合 11 → 3 hook 链 → 4 收尾）逐批迁移、每批全量 bats 验证后推进，公共库边界（只收 ≥2 处使用函数）避免返工——单次全量重写或边界划错都会导致批 1/2 大规模返工 | TAG0010 | 2026-08-15 |
| 架构 | **公共库（agate_common.py）是批量迁移的稳定锚点**：gate-result.sh + agate-workspace-resolve.sh 的函数库（write_gate_result / MAX_RETRY_MAP 等）被 3+ 脚本共享，合并为单一模块杜绝跨脚本函数复制漂移（P0 known_risks「协议文档与脚本引用大面积失效」的"函数级"复发）；单点工具函数留在各自脚本内 | TAG0010 | 2026-08-15 |
| 测试 | **bash `$(...)` 与 Python subprocess 的语义差异是 sh→py 迁移的高发坑**：sh 命令替换剥输出尾部换行、Python capture 不剥，导致空结果判定分支走错（check-scope-resolved.py SC.4 红）——实现用 `.rstrip("\n")` 等价还原 sh 语义；CLI 契约（exit code / 结构 / 输出格式）须逐字节 diff 验证，而非只跑绿 | TAG0010 | 2026-08-15 |
| 流程 | **破环性迁移需强制失败护栏**：hook 薄壳 fail-closed（python 探测失败 exit 非 0 阻断 commit，无 sh 兜底）、pyyaml fail-closed、encoding 守卫——迁移后「悄悄放行」的静默失效比显式报错危害更大（BDD-9 已 BASELINE_CHANGE 为阻断语义） | TAG0010 | 2026-08-15 |

## 环境隔离

`[PROD_NOT_TOUCHED]`——本阶段仅读取 worktree 内产出文件与 git log/status 核验，未接触生产环境。
