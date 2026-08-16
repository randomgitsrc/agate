---
phase: P1
task_id: TAG0008
type: problems
parent: P0-brief.md
trace_id: TAG0008-P1-20260816
status: revised
created: 2026-08-16
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages:
  - agate-install.py
  - agate-resolve.py
  - agate-pack-offline.py
  - install-offline.py
  - install-hook.py
  - pre-commit-gate.sh
  - commit-msg-self-gate.sh
  - pre-push-gate.sh
  - agate_common.py
  - agate-summary.py
  - install.sh
  - docs
domains: [backend, cli, security]
capability_requirements:
  - {need: git-worktree, status: available}
  - {need: windows-runtime, status: supplementable}
  - {need: external-network, status: available}
  - {need: pyyaml, status: available}
  - {need: pillow, status: available}
---

# P1 — 需求基线：agate 版本管理机制（v1）

> trace：TAG0008-P1-20260816（analyst，rev2 修订）。范围锁定来自 P0-brief.md（2026-08-16 用户确认），设计稿
> `archived/docs-2026-08/plans/agate-version-management-20260813.md` §8 决策定稿 + v1/v2 范围。
> 语言路线按 Python（TAG0010/0011 已全量 Python 化；设计稿 §3.2 的 .sh 路线已过时，不引用）。
> rev2 修订说明：按 P1-review.md（needs-revision）落实 5 处修订 + 影响面表 4 处联动点缺口补齐。

## 1. 需求复述

**要解决的问题**：`~/.agate` 是单一软链 → 指向某 checkout 的 `agate/` 子目录。`git pull` 后所有用
`~/.agate` 的项目**全部被动升级**，进行中项目被打断；hook 通过软链自动跟随，无法按项目隔离版本。

**v1 完整范围 = 6 组件**（P0-brief 已锁定，不可扩大/缩小）：

| # | 组件 | 行为 |
|---|------|------|
| 1 | **agate-install**（新，.py） | 无参 = 装 latest 指针（最新发布版）；`agate-install v0.48.0` = 装指定版本（repo clone + `worktree add` tag）；`--uninstall v0.43.0` = 删版本目录 + 清理指针；`--check` = 环境探测（python3/pyyaml/git/bash） |
| 2 | **agate-resolve**（新，.py） | 读项目 `.agate-version`（asdf 模式，cwd 向上找）→ 映射版本 → 得 AGATE_ROOT；无声明回退 `~/.agate/current`（默认 → latest）；AGATE_ROOT env 显式覆盖优先级最高 |
| 3 | **hook 解析入口** | install-hook 装**固定入口** resolve-entry，运行时读项目 `.agate-version` → exec 对应版本的 gate 逻辑。项目 A 锁旧版、项目 B 用新版互不干扰，切版本**不用重装 hook** |
| 4 | **summary 集成** | 显示当前项目解析到的版本 + 原因（`.agate-version` 或全局 current）；v2 扩展版本列表 |
| 5 | **agate-pack-offline.py**（外网打包器） | `v0.48.0 [--platform linux-x86_64\|windows-x86_64] [--include-python] [--include-pillow]` → 平台标签 bundle（agate tag 代码 + wheels（pyyaml 必装/Pillow 可选，`pip download --platform <目标>` 按目标平台拉）+ 嵌入式 Python 可选 + manifest.json 含 sha256 checksum） |
| 6 | **install-offline.py**（内网一键安装器） | 读 manifest.json 核对平台（不匹配警告防错装）+ 校验 checksum → 装 wheels（`pip install --no-index --find-links wheels/`）→ 建 `~/.agate/vX.Y.Z/` → hook/orchestrator 指向（Windows 复制模式/Linux 软链）→ 验证（agate-summary） |

**形态**：安装即建版本目录 `~/.agate/vX.Y.Z/`（git worktree 检出 tag），latest 是**纯指针** → 最新发布版。
`~/.agate` 软链保留（向后兼容）；无 `.agate-version` 的项目 resolve 回退 current。
AGATE_ROOT env 显式覆盖优先级最高。git 不打包（项目侧状态落盘依赖）。
与在线模式共用 agate-resolve/hook 逻辑，只有安装动作分叉。

**v2 边界（本任务不做，明确排除）**：`>=` 版本折中、版本列表扩展（summary）、离线包自动更新/镜像分发、
离线首次安装（无网络装从未装过版本）、prune 自动清理（v1 只做引用检查思路，uninstall 才删）。

## 2. 影响面表（全仓 `~/.agate` 消费点清单）⭐强制

> 扫描对象：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0008` 全仓（只读 grep，未改任何文件）。
> 关键词：`~/.agate`、`AGATE_ROOT`、`.agate-version`、`agate-install`、`agate-resolve`、`install-hook`、
> `agate-pack-offline`、`install-offline`。**无既有 agate-install/agate-resolve/.agate-version 实现**（全新组件）。
> 用途：P2 改一处必须同步所有联动点；本表是 P4 实现 + P7 一致性检查的交叉核对基线。
> rev2 补齐：§2.1 补 3 个内联 AGATE_ROOT 解析脚本；§2.2 补 2 个 `~/.agate` 引用文档；§2.3 路径前缀修正。

### 2.1 脚本层（消费 AGATE_ROOT / 单软链）

| 文件 | 当前行为 | 消费点 | 受 v1 影响 |
|------|----------|--------|-----------|
| `agate/scripts/pre-commit-gate.sh` | hook 薄壳：AGATE_ROOT 自定位（软链 readlink / 复制模式 `.agate-root` 恢复）→ python 探测 → exec `$AGATE_ROOT/scripts/pre-commit-gate.py` | **直接 exec 具体版本 py** | **改**：改为经 resolve-entry 解析后 exec 对应版本 |
| `agate/scripts/commit-msg-self-gate.sh` | 同上薄壳，exec `commit-msg-self-gate.py` | 同上 | **改** |
| `agate/scripts/pre-push-gate.sh` | 同上薄壳，exec `pre-push-gate.py` | 同上 | **改** |
| `agate/scripts/install-hook.py` | AGATE_ROOT 解析：argv[1] > env AGATE_ROOT > `~/.agate`；把三个 hook 软链到 `$agate_root/scripts/*.sh`（复制模式写 `.agate-root` 标记） | **hook 直接指向具体版本脚本** | **改**：装固定解析入口 resolve-entry |
| `agate/scripts/agate_common.py` | `resolve_agate_root()`：env AGATE_ROOT 优先 → 脚本真实路径上溯 → 复制模式 `.agate-root` 恢复；`_AGATE_ROOT` 模块常量 | **脚本自身的 AGATE_ROOT 自定位** | **需集成**：resolve 逻辑在此层统一（`resolve_agate_root` 语义须与"项目版本解析"兼容） |
| `agate/scripts/pre-commit-gate.py` | 经 `resolve_agate_root` 得 AGATE_ROOT 跑 gate 判定 | AGATE_ROOT | 语义保留（只改"解析到哪个版本"） |
| `agate/scripts/ci-gate-backstop.py` | `_AGATE_ROOT = Path(__file__).resolve().parent.parent`，subprocess 调 `_AGATE_ROOT/scripts/check-gate.py` | 单软链假定（自身上溯） | 复核（CI 语境，版本解析后可能指向不同版本脚本） |
| `agate/scripts/agate-inject-card.py` | 内联 `_agate_root()`：env AGATE_ROOT 优先 → 脚本真实路径上溯两级（非走 `agate_common.resolve_agate_root`） | AGATE_ROOT | **复核**：v1 项目级版本解析（I-5）若只改 agate_common，此脚本内联解析不跟进 → 解析入口不一致；P2 评估是否统一走 `agate_common.resolve_agate_root` |
| `agate/scripts/agate-next-card.py` | 内联 `_resolve_agate_root()`：env 优先 → 脚本真实路径上溯两级（非走 `agate_common.resolve_agate_root`） | AGATE_ROOT | **复核**：同上 |
| `agate/scripts/agate-render-dispatch-prompt.py` | 内联 `_resolve_agate_root()`：env 优先 → 脚本真实路径上溯两级（非走 `agate_common.resolve_agate_root`） | AGATE_ROOT | **复核**：同上 |
| `agate/scripts/agate-summary.py` | 显示 `git describe` 版本（仓库自身 tag）+ 硬编码 `python3 ~/.agate/scripts/agate-changes.py` 提示 | **单软链 + 仓库版本显示** | **改**：显示"当前项目解析到的版本 + 原因"（`.agate-version` 或全局 current） |
| `agate/scripts/agate-changes.py` | docstring `python3 ~/.agate/scripts/agate-changes.py` | 文档串 | 复核（提示文案随版本解析变化） |
| `agate/scripts/agate-migrate-workspace.py` | docstring `python3 ~/.agate/scripts/agate-migrate-workspace.py` | 文档串 | 复核 |
| `agate/scripts/README.md` | 全篇 `python3 ~/.agate/scripts/xxx.py` 用法 + 脚本清单表 | 单软链文档 | **改**：新增 4 脚本入清单（install/resolve/pack-offline/install-offline）+ 解析入口说明 |
| `agate/scripts/check-protocol-consistency.py` | L765 扫描协议文档面的脚本名引用（含 `~/.agate/scripts/` 全路径） | 全路径引用一致性 | 复核（新脚本加入后须满足其命名/引用规则） |

### 2.2 文档层（叙述"~/.agate 单软链"）

| 文件 | 消费点 | 受 v1 影响 |
|------|--------|-----------|
| `README.md` | 快速上手第 1 步：clone + `~/.agate` 软链 + 一键 `install.sh` | **改**：新增"版本管理"接入方式（agate-install） |
| `README.zh-CN.md` | 同上（中文镜像） | **改**：同步 |
| `agate/SETUP.md` | 全篇 `~/.agate` 路径 + 装 hook + 验证；**需新增「环境准备（agent 执行）」节**（探测命令 exit code 可判 → 分平台修复 → 验证闭环） | **改**：新增 agent 版环境准备节；路径叙述随版本目录调整 |
| `agate/UPGRADING.md` | 升级 agate 本体（~/.agate 软链指向的仓库）→ `git pull` + 重跑 install-hook + 验证 | **改**：新增本版本破坏性变更章节（.agate-version 语法 / ~/.agate 目录化 / 解析入口迁移） |
| `agate/platform-notes.md` | Windows：软链退化复制模式、AGATE_ROOT 环境变量、`python3 ~/.agate/scripts/install-hook.py` | **改**：latest/current 指针在无符号链接权限时的复制/配置文件模式说明 |
| `agate/AGENTS.md` | "`~/.agate` 软链接默认指向这里" + 升级/卸载叙述 | **改**：升级/卸载叙述适配版本目录 |
| `agate/WORKFLOW.md` | L36 `~/.agate/` 标准安装位置（软链接 → 仓库 agate/ 子目录） | **改**：安装位置叙述（目录 + 解析） |
| `agate/orchestrator-template.md` | `{agate_root}` = `$AGATE_ROOT` 或默认 `~/.agate` | **复核**：`{agate_root}` 语义是否随解析入口变化 |
| `agate/adr.md` | L241 ADR-008 论据"`~/.agate` 软链接让 gate 脚本自动跟随升级" | **复核**：v1 后该机制变为 resolve-entry 解析，ADR 论据需复核是否仍成立/需补记新 ADR |
| `agate/assets/templates/project.md` | L16 "如果你的 agate 没装在默认位置 `~/.agate`" | **复核**：默认安装位置语义随 `~/.agate` 目录化变化 |
| `agate/assets/templates/handoff-template.md` | 双工作区：`~/.agate` 稳定版 + hook 的 AGATE_ROOT | 复核（dogfooding 文档，稳定版叙述保留） |
| `agate/assets/execution-roles/verifier.md` | `python3 $AGATE_ROOT/scripts/check-p6-format.py` 等 | 复核（AGATE_ROOT 语义已覆盖） |
| `agate/phase-cards/P6-acceptance.md` | `$AGATE_ROOT/scripts/check-p6-format.py` | 复核 |
| `install.sh`（仓库根） | 创建 `~/.agate` 软链 + `git pull` 升级 | **兼容保留/改造**：作为 agate-install 底层或替换（P0-brief：install.sh 保留兼容） |
| `docs/guides/worktree-dogfooding-guide.md` | 双工作区 `~/.agate` 稳定版 | 复核（稳定版概念保留，叙述可能微调） |

### 2.3 测试层

| 文件 | 现状 | 受 v1 影响 |
|------|------|-----------|
| `agate/tests/unit/test_install_hook.py` | 3 个 windows_smoke 用例 + AGATE_ROOT 解析/复制模式 | **改/扩**：hook 解析入口（resolve-entry）行为 + 复制模式下解析 |
| `agate/tests/unit/test_agate_summary.py` | 不存在（全仓 grep `agate-summary`/`agate_summary` 于 tests/ 零命中，rev2 实查确认） | **新增**：summary 版本 + 原因显示 |
| 新增 `test_agate_version_install.py` / `test_agate_version_resolve.py` | 不存在 | **新增**（HANDOFF §4 已预告命名） |
| 新增 pack-offline / install-offline 测试 | 不存在 | **新增** |
| `agate/tests/integration/test_pre_commit_hook.py`、`agate/tests/integration/test_commit_msg_self_gate_integration.py`、`agate/tests/integration/test_pre_push_hook.py`、`agate/tests/integration/test_dispatch_context_card.py` | 经 `AGATE_ROOT` env 显式传入跑 hook | **复核**：hook 解析入口改造后仍须 env 覆盖可用 |

### 2.4 关键扫描结论

1. **无既有实现**：`agate-install` / `agate-resolve` / `.agate-version` / `agate-pack-offline` / `install-offline` 均不存在，全部全新。
2. **3 个 hook 薄壳是核心改动点**：当前 `AGATE_ROOT="${AGATE_ROOT:-...readlink...}"` 单行自定位直接落到**具体版本** gate —— v1 须改为"定位到解析入口 → 运行时按项目版本解析 → exec 对应版本"，同时保留 env 覆盖最高优先级。
3. **`install-hook.py` 契约**：`argv[1] > env AGATE_ROOT > ~/.agate` 三级解析 —— 改造后"装固定解析入口"须兼容此契约（Windows 复制模式 + `.agate-root` 标记保留）。
4. **`agate_common.resolve_agate_root`**：env 优先 + 脚本上溯 + `.agate-root` 恢复，是 gate 脚本统一入口 —— 项目级版本解析（.agate-version）须在此层做**加法**（env 最高 → 项目声明 → current），不破坏现有 env 语义。
5. **`agate-summary.py`** 当前显示**仓库自身 tag**（git describe），v1 需求是显示**项目解析到的版本 + 原因** —— 语义变化，测试与提示文案需同步。
6. **3 个派发/卡片脚本内联解析（rev2 新增结论）**：`agate-inject-card.py` / `agate-next-card.py` / `agate-render-dispatch-prompt.py` 各自内联 `_agate_root()`（env → 脚本真实路径上溯两级），**未走 `agate_common.resolve_agate_root`** —— P2 需评估是否统一，避免项目级版本解析后与 3 个脚本解析入口不一致。
7. **Windows**：`platform-notes` 已定义软链退化复制模式 + `.agate-root` 标记先例 —— latest/current 指针与解析入口须复用（TAG0004 成果）。
8. **CI**（`.github/workflows/protocol-tests.yml`）：grep 无 `~/.agate`/AGATE_ROOT 引用，不受直接影响；新增测试须带 `@pytest.mark.windows_smoke`（每文件第 1 个用例 + 平台敏感用例）。
9. **check-protocol-consistency.py** L765 会扫描文档中的脚本引用全路径 —— 新增脚本名须在 `scripts/README.md` 清单登记，否则一致性检查可能 WARN。

## 3. 隐含需求识别

> 用户没说但技术上必须的依赖，每条注明"为什么必须"。

| # | 隐含需求 | 为什么必须 |
|---|----------|-----------|
| I-1 | **`.agate-version` 语法规范**：`agate: v0.43.0` 精确版本；v1 只支持精确（`>=` 留 v2）；需定义非法格式/**空文件**/未知工具前缀的处理 | resolve 是版本映射的单一入口，语法不定义清楚则 hook 行为不可预期（空文件归入"非法格式"统一处理，见 BDD-14） |
| I-2 | **resolve 失败必须回退稳（回退 current），绝不能静默禁用 gate** | hook 影响所有下游项目；解析失败若直接放行 commit = gate 防线失效（P0-brief known_risk #1，设计稿 §7 风险） |
| I-3 | **hook 薄壳改为"解析入口"间接 exec**，且 AGATE_ROOT env 覆盖仍最高 | 项目 A 锁旧版、项目 B 用新版互不干扰 + 切版本不用重装 hook（核心需求），env 覆盖是既有契约不可破坏 |
| I-4 | **`install-hook.py` 复制模式（Windows）下解析入口仍须可用**（`.agate-root` 标记 + 版本解析路径） | Windows 无符号链接权限是已定义场景（platform-notes 先例），解析入口不能只在软链模式工作 |
| I-5 | **`agate_common.resolve_agate_root` 集成项目版本解析**（env 最高 → 项目声明 → current），作为所有 gate 脚本的统一解析 | gate 逻辑（check-gate.py 等）本身不改，只改"如何解析到哪个版本"——统一入口保证不散落（rev2：3 个派发脚本的内联解析是否归口此处 P2 评估） |
| I-6 | **`agate-summary.py` 语义迁移**：从"仓库自身 tag"到"项目解析到的版本 + 原因（.agate-version 或全局 current）" | summary 集成是 v1 4 组件之一，显示原因用于排障不再靠猜（设计稿 §8.4） |
| I-7 | **文档全联动**（2.2 表全部）：SETUP/README/README.zh-CN/UPGRADING/platform-notes/AGENTS/WORKFLOW/orchestrator-template + adr + project.md 模板 + `install.sh` 兼容保留 | P0-brief known_risk #6 强制要求："用户明确：不愿意一轮一轮来回改，必须一次改全"；检查对象含文档一致性 |
| I-8 | **离线打包需外网拉取**：repo tag 检出 + `pip download --platform` 拉 wheels（pyyaml 必装/Pillow 可选）；打包器须处理"目标版本 tag 不存在/pip download 网络失败/目标平台 wheel 缺失" | pack-offline 是外网侧动作，失败路径须明确（否则内网拿到坏包）；验收见 BDD-24 |
| I-9 | **manifest.json 双时机闭环**：打包时计算 sha256 checksum → 内网安装时校验，不匹配拒绝安装 | 内网经介质传递，防传输损坏/篡改是基本保障（P0-brief 明确） |
| I-10 | **平台核对**：install-offline 读 manifest 平台标签，与安装机不符 → 警告防错装（不静默错装） | 平台维度 wheels/hook 都是平台相关，错装必炸（P0-brief 明确） |
| I-11 | **`--uninstall` 指针清理语义 + 引用保护**：删版本目录时若 latest/current 指向该版本 → 指针处理必须定义（重指其他版本 or 清理）；**项目 `.agate-version` 仍引用该版本 → 拒绝/警告卸载**（防误删被锁版本，设计稿 §8.3 引用即保护） | 防"latest 指向已删目录"悬空指针 + 防"某项目锁的版本被删"灾难（P0-brief 明确 + 设计稿 §8.3；验收见 BDD-6） |
| I-12 | **重复安装幂等**：`agate-install vX` 对已安装版本 → 不产生重复 worktree、不报错 | git worktree add 已存在路径会失败；幂等是程序化安装的基本要求 |
| I-13 | **环境探测 `--check` 的分平台修复指引**（Linux pip 装 pyyaml；Windows Python/PATH/PYTHONUTF8/Git for Windows）且**不自动装系统级依赖** | P0-brief 明确：写给 agent（exit code 可判）而非人类；Windows 自动配置不可行 |
| I-14 | **新增测试 + 平台无关原则**：新增脚本全走 pytest（TAG0011），平台分支按 windows_smoke 标记 | AGENTS.md 测试约定 + 本任务跨平台（Linux 实测 + Windows 冒烟） |
| I-15 | **`install.sh` 兼容保留**：存量用户升级路径不破坏（作为 agate-install 底层或替换，单软链场景仍可用） | P0-brief known_risk #2：~/.agate 从单软链到目录的迁移，install.sh 保留兼容 |
| I-16 | **`git worktree` 作为版本载体**：`~/.agate/vX.Y.Z` 是 worktree 检出 tag，repo 只 clone 一次 | 设计稿 §2/§3.1 决策：省磁盘 + 秒级切换 + 版本 = git tag 代码快照 |

## 4. BDD 验收条件

> 每条独立可验证、可二值判定（PASS/FAIL）。分组 `###` 组织，编号全局连续。
> 所有"输出含 X"类判定按**退出码 + stdout/stderr 关键字段**判定（不绑定具体格式化样式）。
> rev2：新增 BDD-6（卸载引用保护）、BDD-24（打包失败路径）；修订 BDD-14（空文件变体）、BDD-25（平台不匹配单信号）、BDD-30（legacy 软链直接解析）。

### agate-install（安装 / 卸载 / 环境探测）

#### BDD-1: 无参安装建立 latest 指针指向某版本目录
- Given 干净环境（`~/.agate` 不存在版本目录）
- When 运行 `agate-install`（无参数）
- Then `~/.agate/latest` 存在且解析指向某个 `~/.agate/vX.Y.Z/` 目录（纯指针，非 checkout 本体）

#### BDD-2: 指定版本安装建立版本目录（worktree 检出 tag）
- Given `~/.agate/repo` 已就绪
- When 运行 `agate-install v0.48.0`
- Then `~/.agate/v0.48.0/` 存在，且 `git -C ~/.agate/repo worktree list` 可查到该路径对应 tag v0.48.0

#### BDD-3: 重复安装已存在版本幂等不报错
- Given `~/.agate/v0.48.0` 已安装
- When 再次运行 `agate-install v0.48.0`
- Then 退出码 0，且 `git worktree list` 中该版本路径不重复出现

#### BDD-4: 无参安装后 latest 与 current 关系正确
- Given 首次安装完成（BDD-1）
- When 检查 `~/.agate/current` 与 `~/.agate/latest`
- Then `current` 默认指向 `latest`，`latest` 指向最新发布版本目录（设计稿 §8.2：current 默认 → latest）

#### BDD-5: 卸载已安装版本删除目录并清理指针
- Given `v0.43.0` 已安装，且无任何项目 `.agate-version` 引用它
- When 运行 `agate-install --uninstall v0.43.0`
- Then `~/.agate/v0.43.0/` 不存在，且 `git worktree list` 不再含该路径；若 latest/current 曾指向它则被重指到其他有效版本或清除

#### BDD-6: 项目仍引用该版本时卸载被拒绝并警告
- Given `v0.43.0` 已安装，且至少一个项目 `.agate-version` 声明 `agate: v0.43.0`（引用保护，设计稿 §8.3）
- When 运行 `agate-install --uninstall v0.43.0`
- Then 卸载被拒绝：退出码非 0，stderr 输出警告（指出被引用的版本号与引用来源），`~/.agate/v0.43.0/` 仍存在

#### BDD-7: 环境探测全齐时退出码 0
- Given 环境已具备 python3 / pyyaml / git / bash
- When 运行 `agate-install --check`
- Then 退出码 0，输出包含各项探测结果（python3/pyyaml/git/bash 逐项列出）

#### BDD-8: 环境探测缺项时非 0 退出并给分平台修复指引
- Given 环境缺 pyyaml（mock 缺失）
- When 运行 `agate-install --check`
- Then 退出码非 0，输出列出缺失项，并包含对应平台的修复指引（Linux 为 `pip install pyyaml` 类命令；Windows 为 Python/PATH/PYTHONUTF8/Git for Windows 类指引）

### agate-resolve（版本解析）

#### BDD-9: 项目锁定版本命中
- Given 项目根含 `.agate-version`，内容 `agate: v0.43.0`，且 `~/.agate/v0.43.0/` 已安装；未设 AGATE_ROOT env
- When 在项目根运行 `agate-resolve`
- Then 解析出 AGATE_ROOT=`~/.agate/v0.43.0` 与版本号 v0.43.0

#### BDD-10: 从 cwd 向上查找 `.agate-version`
- Given `.agate-version` 在项目根的上级目录（声明 v0.43.0），当前 cwd 为项目根下的子目录
- When 在子目录运行 `agate-resolve`
- Then 仍解析到 v0.43.0（向上查找命中）

#### BDD-11: 无声明回退 current → latest
- Given 项目无 `.agate-version`；`~/.agate/current` → `latest` → `~/.agate/v0.44.0`
- When 运行 `agate-resolve`
- Then 解析出 AGATE_ROOT=`~/.agate/v0.44.0`，原因标注"全局 current"

#### BDD-12: AGATE_ROOT env 覆盖优先级最高
- Given 项目 `.agate-version` 声明 v0.43.0，但环境变量 AGATE_ROOT 指向 `/tmp/custom-agate`
- When 运行 `agate-resolve`
- Then 解析结果 AGATE_ROOT=`/tmp/custom-agate`（env 覆盖项目声明与全局 current）

#### BDD-13: 声明版本未安装时回退 current 且不静默失败
- Given `.agate-version` 声明 `agate: v0.99.0`（未安装）；`~/.agate/current` 可解析
- When 运行 `agate-resolve`
- Then 不 crash：stderr 输出警告（声明的版本未安装），仍回退解析出可用 AGATE_ROOT（指向 current），退出码为 0（可用）——绝不返回"无 AGATE_ROOT"

#### BDD-14: `.agate-version` 格式非法（含空文件）时回退 current 并警告
- Given `.agate-version` 内容为非法格式（如 `random text`、`foo: bar`，**或为空文件**——空文件归入"非法格式"统一处理，对应 I-1 三要素全验收）
- When 运行 `agate-resolve`
- Then 不 crash：stderr 输出格式警告，回退解析出可用 AGATE_ROOT（指向 current）

### hook 解析入口

#### BDD-15: install-hook 安装的是固定解析入口而非具体版本脚本
- Given 项目仓库
- When 运行 `python3 ~/.agate/scripts/install-hook.py`
- Then `.git/hooks/pre-commit` 指向解析入口（resolve-entry，固定、不随版本变），而非直接指向某具体版本的 gate 脚本

#### BDD-16: 项目 A 锁旧版、项目 B 用新版互不干扰
- Given 项目 A `.agate-version` 声明 v0.43.0（已装），项目 B 无声明（走 current）；两项目均装了 hook
- When 分别在两项目 commit
- Then 项目 A 的 gate 判定使用 v0.43.0 的 gate 逻辑，项目 B 使用 current 版本的 gate 逻辑，两项目各自成功/失败判定互不影响

#### BDD-17: resolve 失败时 hook 回退 current 跑 gate，不静默放行
- Given 项目 `.agate-version` 声明未安装版本
- When commit（触发 pre-commit）
- Then hook 回退 current 版本跑 gate 判定：commit 被该版本 gate 正常判定（通过则放行、不通过则阻断），绝不因解析失败静默跳过 gate

#### BDD-18: 切版本不用重装 hook
- Given 项目已装 hook，`.agate-version` 声明 v0.43.0
- When 把 `.agate-version` 改为 v0.44.0（已装）后直接 commit（不重跑 install-hook）
- Then gate 使用 v0.44.0 的逻辑判定（无需重装 hook 即生效）

#### BDD-19: Windows 复制模式下解析入口仍可用
- Given AGATE_HOOK_COPY_MODE=1（模拟无符号链接权限），hook 以复制模式安装，含 `.agate-root` 标记
- When 项目 commit
- Then 解析入口经 `.agate-root` 恢复 AGATE_ROOT 后仍按项目版本解析并跑 gate（不因复制模式失效）

### summary 集成

#### BDD-20: summary 显示项目解析到的版本 + 原因（.agate-version）
- Given 项目 `.agate-version` 声明 v0.43.0
- When 运行 `agate-summary`
- Then 输出包含解析到的版本号 v0.43.0 与原因说明（引用 `.agate-version`）

#### BDD-21: summary 显示全局 current 回退原因
- Given 项目无 `.agate-version`，`~/.agate/current` → latest → v0.44.0
- When 运行 `agate-summary`
- Then 输出包含版本号 v0.44.0 与原因说明（全局 current）

### 离线部署包（pack-offline + install-offline）

#### BDD-22: pack-offline 产出平台标签 bundle 与 manifest
- Given 外网环境 + agate 仓库可访问
- When 运行 `agate-pack-offline.py v0.48.0 --platform linux-x86_64`
- Then 产出 bundle 目录，内含：agate v0.48.0 tag 代码、pyyaml wheel、manifest.json；manifest.json 含 `platform: linux-x86_64` 与各组件 sha256 checksum

#### BDD-23: manifest 记录平台标签与 checksum 字段
- Given BDD-22 已打包
- When 读取 manifest.json
- Then 能解析出 platform 字段（等于打包时 `--platform` 值）与每个组件的 sha256 值（非空）

#### BDD-24: pack-offline 失败路径非 0 退出且不产坏包
- Given 任一失败场景：① 目标版本 tag 不存在（如 `v0.99.0`）② pip download 网络失败（mock 断网）③ 目标平台 wheel 缺失
- When 运行 `agate-pack-offline.py <版本> --platform <目标>`
- Then 退出码非 0，stderr 输出指明失败原因的错误信息（对应上述场景），且不产出可用的 bundle 目录（manifest 缺失或不完整）
- > 三条场景逐一独立运行，均须满足同一失败契约（对应 I-8 后半句，P6 可逐场景验收）

#### BDD-25: install-offline 平台不匹配时警告并拒绝安装
- Given bundle 的 manifest platform=`linux-x86_64`，安装机为 windows-x86_64
- When 运行 `install-offline.py`
- Then 输出平台不匹配警告（警告须含 platform 字段值 `linux-x86_64` 与当前机器平台），且退出码非 0（拒绝安装，fail-closed 防错装）

#### BDD-26: checksum 校验不匹配时拒绝安装
- Given bundle 内某组件文件被篡改（checksum 与 manifest 不符）
- When 运行 `install-offline.py`
- Then 校验失败：退出码非 0，拒绝安装，输出说明被篡改的组件

#### BDD-27: wheels 以离线方式安装成功
- Given 内网无互联网，bundle 含 wheels/
- When 运行 `install-offline.py`（内部走 `pip install --no-index --find-links wheels/`）
- Then pyyaml（及按包含项 Pillow）安装成功，目标环境可直接运行 agate gate 脚本

#### BDD-28: 安装完成建立版本目录 + hook 指向 + 验证闭环
- Given install-offline 各步骤通过
- When 安装完成
- Then `~/.agate/vX.Y.Z/` 存在；hook/orchestrator 指向就位（Linux 软链 / Windows 复制模式）；验证命令（agate-summary 等价）能显示该版本

#### BDD-29: 勾选语义 --skip-python / --skip-pillow 覆盖打包包含项
- Given bundle 含嵌入式 Python 与 Pillow
- When 运行 `install-offline.py --skip-python --skip-pillow`
- Then 跳过对应安装步骤，不报错，其余步骤照常完成

### 向后兼容（红线）

#### BDD-30: 存量单软链用户不受破坏
- Given 存量安装：`~/.agate` 是软链 → 旧 checkout 的 `agate/` 子目录，无版本目录、无 `.agate-version`、无 current/latest 指针
- When 不跑任何新安装工具，直接 commit（触发既有 hook）
- Then gate 照常按既有语义运行，无 breakage，无静默禁用：resolve 在无 current/latest 的 legacy 布局下，将 `~/.agate` 软链目标（旧 checkout 的 `agate/` 子目录）**直接解析为 AGATE_ROOT**（即"legacy 软链目标本身 = AGATE_ROOT"的兜底规则，消除 P4 实现歧义）

#### BDD-31: gate 判定逻辑本身未被修改
- Given v1 交付后
- When 对比 `check-gate.py` 等 gate 判定脚本
- Then 其 gate 判定逻辑未改（只改了"如何解析到哪个版本"；`git log` 或 diff 可证，仅新增解析层改动）

### BDD 反模式自检

- [x] Then 子句未绑定 CSS/HTML 类名（本任务无前端）
- [x] Then 子句可二值判定（退出码 + 文件存在 + 字段值，均为客观信号）
- [x] 无主观形容词（"防错装"/"互不干扰"均有可观测信号）
- [x] Given/When 不绑定实现细节（描述 CLI 命令/系统行为，不写"调用 resolve()"）
- [x] 每条 BDD 单一 Given-When-Then；多场景已拆独立编号（BDD-24 三场景共用同一失败契约，作为单条验收）
- [x] 编号连续 BDD-1 ~ BDD-31

## 5. 待确认清单

[NO_NEED_CONFIRM]

- 无阻塞项：P0-brief 已锁定完整范围（2026-08-16 用户确认离线部署包/平台维度/checksum/uninstall/环境探测）。
- 无方向性分歧：各隐含需求（I-1~I-16）均为 P0-brief/设计稿 §8 已明确的技术必然，不涉业务方向判断。
- 无 `[SUGGEST:]` 倾向项（方案细节留 P2 设计，本阶段不掺方案）。
- rev2 补充：引用保护（I-11/设计稿 §8.3"引用即保护"）已落 BDD-6（卸载拒绝）验收，无需转 P2 人工核对。

## 6. 裁剪说明

- **phases: [P1, P2, P3, P4, P5, P6, P7, P8]**（frontmatter）——**无裁剪**。
- P0-brief 明确"走完整 task（机制级，比 TAG0005/6/7 大），P0-P8"（known_risk #7）。
- risk_level=**high**：hook 改造影响所有下游项目、`~/.agate` 从单软链到目录迁移影响存量用户、
  Windows 软链退化、离线包平台/校验复杂度（P0-brief known_risks）。high → P2 全量评审 + P3 不可裁。
- 跳过理由：无跳过项。

## 7. 能力需求声明

| need | why | available 来源 | status |
|------|-----|----------------|--------|
| git-worktree | 验证版本目录为 worktree 检出 tag、worktree list、卸载清理 | 本环境 git 可用（executor_env.git=true） | available |
| windows-runtime | 验证 Windows 复制模式 / 指针退化 / windows_smoke | CI matrix（`pytest -m windows_smoke`）+ `AGATE_HOOK_COPY_MODE=1` 模拟（platform-notes 先例）；本机 Linux 无法实测 → **不宣称已实测 Windows** | supplementable |
| external-network | pack-offline 需 `pip download --platform` 拉 wheels + repo tag 检出 | executor_env.network=full | available |
| pyyaml | gate 脚本依赖（强制）+ 打包 wheel | 已具备（`~/.venvs/agate-dev/` 或系统） | available |
| pillow | Pillow 可选 wheel（`--include-pillow`）打包验证 | 已具备（agate 可选依赖） | available |

- **无 GAP**：不触发 `[CAPABILITY_GAP]`，流程可自走。
- 未设 `requires_minimal_validation: true`（无浏览器/安全模型/外部系统交互型行为依赖；checksum 属内部实现校验，非外部行为）。

## 8. 说明与备注

- 本文件是**活基线**：后续阶段若发现新隐含需求，主 Agent 标 `[SCOPE+]` 回写，本文件始终是唯一真相源。
- P1 基线保护：本文件为需求基线，P2-P8 不直接修改；确需变更走 `[BASELINE_CHANGE: 理由]`。
- 影响面表（第 2 节）是 P7 一致性检查的交叉核对基线；P2 设计须覆盖 2.1/2.2/2.3 全部联动点（含 rev2 补齐的 3 脚本 2 文档）。
- 离线首次安装（无网络装从未装过版本）明确排除（v2）；`install.sh` 兼容保留路径在 P2 细化。
- rev2 修订记录：BDD 总数 29 → 31；新增 BDD-6（卸载引用保护）、BDD-24（打包失败路径）；修订 BDD-14（空文件）、BDD-25（平台不匹配 fail-closed）、BDD-30（legacy 软链直接解析）；影响面表补 3 脚本/2 文档 + 测试路径前缀修正。
