---
phase: P2
task_id: TAG0008
type: design
parent: P1-requirements.md
trace_id: TAG0008-P2-20260816
status: draft
created: 2026-08-16
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2
packages: [agate]
domains: [backend, cli, security]
ui_affected: false
dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: resolve-chain, complexity: high}, {id: install, complexity: high}, {id: offline, complexity: high}]}
---

# P2 — 方案设计：agate 版本管理机制（v1）

> trace：TAG0008-P2-20260816（architect）。上游：P1-requirements.md（31 BDD + 影响面表 2.1/2.2/2.3 + I-1~I-16，review approved）、
> P0-brief.md（env_constraints + known_risks）、设计稿 `archived/docs-2026-08/plans/agate-version-management-20260813.md`（§8 决策定稿）。
> 语言路线：**Python**（P0/P1 定稿，设计稿 §3.2 的 .sh 路线已过时不引用）。
> 前置调研结论（上一轮 architect 已核实，本稿直接采信）：最小验证 3 项通过 + 代码扫描 7 项 + 设计稿 §8 决策（见 §7 与 §5）。

## 0. 设计目标（可判定完成标准）

1. **项目级版本隔离**：项目 A 锁 v0.43.0、项目 B 用 current，两项目 commit 各自跑对应版本 gate（BDD-16）；切版本不用重装 hook（BDD-18）。
2. **resolve 失败回退稳**：任何解析失败回退 current（→latest），绝不静默禁用 gate（BDD-13/14/17）。
3. **向后兼容**：存量单软链用户不跑新工具时行为不变（BDD-30）；gate 判定逻辑本身未改（BDD-31）。
4. **离线闭环**：外网打包 → 内网安装，平台核对 + checksum 校验 + 勾选覆盖（BDD-22~29）。
5. **卸载引用保护**：项目仍引用该版本时拒绝卸载（BDD-6）；重复安装幂等（BDD-3）。

## 1. 影响域分析（改什么 / 不改什么 / 风险在哪）

### 1.1 改什么（脚本层，覆盖影响面表 2.1 全部联动点）

| 文件 | 改动 | 关联 |
|------|------|------|
| `agate/scripts/agate-resolve.py`（**新**） | 版本解析 CLI：cwd 向上找 `.agate-version` → 映射版本目录；env 最高 → 项目声明 → current；输出 AGATE_ROOT + version + reason | BDD-9~14, I-1/2/5 |
| `agate/scripts/agate-install.py`（**新**） | 安装/卸载/环境探测：repo 单克隆 + worktree add tag；`--uninstall` 引用保护 + 指针清理；`--check` 分平台修复指引 | BDD-1~8, I-11~13/16 |
| `agate/scripts/agate-pack-offline.py`（**新**） | 外网打包：tag 代码 + `pip download --platform` 拉 wheels + manifest（sha256） | BDD-22~24, I-8/9 |
| `agate/scripts/install-offline.py`（**新**） | 内网安装：manifest 平台核对 + checksum 校验 + `pip install --no-index` + 建版本目录 + hook 指向 + 验证 | BDD-25~29, I-9/10 |
| `agate/scripts/agate_common.py` | `resolve_agate_root` 集成项目版本解析（env 最高 → 项目声明 → current），作为统一解析入口 | I-5 |
| `agate/scripts/pre-commit-gate.sh` / `commit-msg-self-gate.sh` / `pre-push-gate.sh` | 3 hook 薄壳：AGATE_ROOT 自定位改为**经 resolve-entry 解析后 exec 对应版本 py**；env 覆盖最高保留 | BDD-15~19, I-3/4 |
| `agate/scripts/install-hook.py` | 装**固定解析入口** resolve-entry（不装具体版本脚本）；复制模式 `.agate-root` 标记保留 | BDD-15/19, I-4 |
| `agate/scripts/agate-summary.py` | 语义迁移：显示"项目解析到的版本 + 原因"（`.agate-version` 或全局 current） | BDD-20/21, I-6 |
| `agate/scripts/agate-inject-card.py` / `agate-next-card.py` / `agate-render-dispatch-prompt.py` | 3 个内联 `_agate_root()` **统一归口** `agate_common.resolve_agate_root`（决策：是，见 §4.4） | 影响面 2.1 复核项 |
| `agate/scripts/README.md` | 新增 4 脚本入清单（install/resolve/pack-offline/install-offline）+ 解析入口说明 | 影响面 2.1, CHECK 10 |
| `agate/scripts/check-protocol-consistency.py` | CHECK 10 SCRIPT_REF_RE 白名单补 `install-offline.py` / `agate-install.py` 等新脚本名 | 影响面 2.1 复核项 |
| `agate/scripts/ci-gate-backstop.py` | **复核不改**：CI 语境 `__file__.parent.parent` 上溯即正确（CI 从 checkout 跑，不经 ~/.agate 版本解析） | 影响面 2.1 复核项 |
| `agate/scripts/pre-commit-gate.py` 等 gate 判定脚本 | **不改**（BDD-31） | 红线 |

### 1.2 改什么（文档层，覆盖影响面表 2.2 全部联动点）

README.md / README.zh-CN.md / SETUP.md（新增 agent 版环境准备节）/ UPGRADING.md（新增本版本破坏性变更章节）/ platform-notes.md（latest/current 指针复制模式说明）/ AGENTS.md（升级/卸载叙述适配版本目录）/ WORKFLOW.md（安装位置叙述）/ orchestrator-template.md（复核 `{agate_root}` 语义）/ handoff-template.md（复核）/ adr.md（复核 ADR-008 + 补记新 ADR）/ templates/project.md（复核）/ install.sh（兼容保留，作为 agate-install 底层或替换）。

### 1.3 改什么（测试层，覆盖影响面表 2.3）

新增 `test_agate_version_install.py` / `test_agate_version_resolve.py` / `test_agate_summary.py` / pack-offline / install-offline 测试；改 `test_install_hook.py`（resolve-entry 行为 + 复制模式）；复核 `integration/` 下 hook 相关测试（AGATE_ROOT env 显式传入仍可用）。

### 1.4 不改什么（明确边界）

- **gate 判定逻辑**（check-gate.py / pre-commit-gate.py / commit-msg-self-gate.py / pre-push-gate.py / ci-gate-backstop.py 的判定分支）：只改"如何解析到哪个版本"，不改判定本身（BDD-31）。
- **agate_common 既有函数语义**：`resolve_agate_root` / `probe_python` / `run_git` 等既有契约不变，只做加法。
- **3 个 hook 薄壳的 .sh 形态**：保留 sh 薄壳（python 探测 + exec py），不新增 .sh 脚本。
- **`~/.agate` 软链本身**：兼容保留（BDD-30）。
- **v2 边界**：`>=` 折中、版本列表、离线包自动更新、离线首次安装、prune 自动清理（不做）。

### 1.5 风险在哪

| 风险 | 影响 | 缓解 |
|------|------|------|
| hook 解析失败静默放行 | gate 防线失效 | resolve 失败必须回退 current 且 exit 0 可用，hook 侧另有 fail-closed 兜底（BDD-17 红线） |
| 存量软链用户升级断裂 | 所有下游项目 | BDD-30 legacy 布局兜底：无 current/latest 时软链目标本身 = AGATE_ROOT |
| 3 个内联解析脚本与 agate_common 不一致 | 解析入口分叉 | 统一归口 agate_common（§4.4） |
| Windows 复制模式解析入口失效 | 跨平台断链 | resolve-entry 兼容 `.agate-root` 标记恢复（BDD-19） |
| 离线包被篡改/错平台 | 内网环境损坏 | manifest checksum 校验 + 平台核对 fail-closed（BDD-25/26） |

## 2. 候选方案（candidate_count=2，方案级探索）

> 机制级任务，本设计核心决策点是 **hook 解析入口如何实现版本对应** 与 **版本目录/指针形态**。以下 2 个方案覆盖这两个决策点。

### 2.1 候选方案 A（**采纳**）：resolve-entry 固定入口 + 版本目录 + 纯指针

**核心结构**：`~/.agate/` 升级为版本管理根目录：
```
~/.agate/
├── repo/              # 唯一主仓库（首次 clone，之后只 worktree add tag）
├── scripts/           # 版本管理工具本体（resolve-entry.py + install/resolve/pack-offline/install-offline/summary/install-hook + agate_common）
├── v0.43.0/           # worktree 检出 tag（离线模式 = bundle 复制目录）
├── v0.48.0/
├── latest             # 纯指针 → v0.44.0（文本或软链，Windows 复制模式用文本）
└── current            # 默认指针 → latest
```
- **install-hook 装固定入口** `~/.agate/scripts/resolve-entry.py`（软链/复制到 `.git/hooks/`），运行时读项目 `.agate-version` → 映射版本 → exec 对应版本 gate py。
- 3 hook 薄壳改为经 resolve-entry：`exec $PY $AGATE_ROOT/scripts/resolve-entry.py <gate-name> "$@"`。
- agate-resolve 输出 AGATE_ROOT + version + reason（summary 复用）。
- 版本 = git tag 代码快照（worktree），切版本秒级。

**权衡**：
- 优点：单一解析入口（resolve-entry），3 hook 共用一套解析逻辑零重复；hook 固定指向入口、切版本不重装（BDD-18 核心）；与设计稿 §8 一致；向后兼容天然（legacy 布局下 resolve 回退软链目标）。
- 风险/成本：引入新脚本（resolve-entry.py + agate-install.py + pack/install-offline 共 5 新 py）；`~/.agate` 从单软链变目录，存量用户需文档指引；Windows 复制模式需 resolve-entry 支持 `.agate-root` 恢复。

### 2.2 候选方案 B（**否决**）：hook 直接内联版本解析（无独立 resolve-entry）

**核心结构**：不引入 resolve-entry，3 个 hook 薄壳各自内联 `.agate-version` 解析逻辑（自读项目声明 → 自算 AGATE_ROOT → exec 对应版本 py）。

**权衡**：
- 优点：少一个新脚本；改动面更集中在 3 个 hook。
- 风险/成本（否决理由）：解析逻辑在 3 个薄壳间重复三份（DRY 违反，后续维护漂移风险高）；薄壳是 sh，版本解析若用 sh 实现违背"产品逻辑全 .py"路线（P0/P1 定稿）；summary/其他脚本还要另写一份解析 → 解析入口分叉（I-5 明示的风险）；无法作为统一库被 pack-offline/install-offline 复用。

### 2.3 选择理由（选择 A）

1. **P0-brief/P1 已锁定**："install-hook 装固定入口 resolve-entry"是用户确认的形态（P0-brief issue 4），候选 A 直接落地该决策。
2. **Python 路线对齐**：候选 A 把解析逻辑放 `.py`（resolve-entry + agate_common），薄壳保持 sh 仅做转发——符合 TAG0010/0011 全量 Python 化约定；候选 B 会逼解析逻辑进 sh 或三份重复 py。
3. **I-5 统一解析入口**：候选 A 让 agate_common.resolve_agate_root / resolve-entry / agate-resolve / summary 共用一套解析，候选 B 无法满足。
4. **工作量对比**：候选 A 增加 1 个入口脚本，但消除 3 份重复解析 + summary 独立解析，总工作量更低。

> 诚实标注：候选 B 是"明显更差的陪衬"（nudge 要求）。其真实劣势（重复解析 + 违反 Python 路线）是结构性的，非可选优化项。

## 3. 四字段

### 3.1 packages / domains / ui_affected（见 frontmatter）

- `packages: [agate]`——agate 协议/脚本/docs 单包发布（P8 单版本 bump，无多包版本分叉）。
- `domains: [backend, cli, security]`——脚本/CLI/卸载引用保护（安全）三域。
- `ui_affected: false`——CLI 输出变化，无浏览器/图形 UI，无需 E2E。

### 3.2 gate_commands（P3/P5/P6 固化，后续阶段不得修改）

```yaml
gate_commands:
  P3: "python3 -m pytest"
  P5: "python3 -m pytest -q --tb=no"
  P5_unit: "python3 -m pytest -q --tb=no agate/tests/unit/test_agate_version_install.py agate/tests/unit/test_agate_version_resolve.py agate/tests/unit/test_agate_summary.py agate/tests/unit/test_install_hook.py"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py"
  P5_count: "bash agate/tests/scripts/count-tests.sh"
  project_module: "agate"
```

## 4. 方案设计（候选 A 展开）

### 4.1 版本解析语义（env 最高 → 项目声明 → current）

`agate_common.resolve_agate_root(script_path)` 扩展为四层（加法，不改既有 env/上溯/.agate-root 语义）：

1. `AGATE_ROOT` env 显式设置 → 直接返回（最高优先级，BDD-12，兼容既有契约）。
2. 项目级解析：cwd（或脚本所在项目根）向上找 `.agate-version`（asdf 模式，BDD-10）→ 命中则映射 `~/.agate/vX.Y.Z/`。
3. 无声明 / 声明版本未安装 / 格式非法 → 回退 `~/.agate/current` →（默认指向）`~/.agate/latest` → 具体版本目录。失败时 stderr 警告 + 回退 current（绝不静默禁用，BDD-13/14）。
4. **legacy 布局兜底（BDD-30）**：无 current/latest 指针时，若 `~/.agate` 本身是软链 → 直接解析软链目标为 AGATE_ROOT（存量 checkout 的 `agate/` 子目录）。

> 注：`agate-resolve` 独立运行 vs hook 内 resolve-entry 均走同一逻辑；`agate-summary` 复用解析结果显示版本 + 原因。

### 4.2 `.agate-version` 语法（I-1 细化）

- 合法：`agate: v0.43.0`（精确版本，v1 只支持精确）。
- 非法格式（含空文件、`random text`、`foo: bar`）→ stderr 警告 + 回退 current（BDD-14）。
- 声明版本未安装 → stderr 警告 + 回退 current（BDD-13）。

### 4.3 hook 解析入口（BDD-15~19）

- `install-hook.py` 安装 `~/.agate/scripts/resolve-entry.py` 为 `.git/hooks/{pre-commit,commit-msg,pre-push}`（固定入口，不随版本变）。
- 运行时：resolve-entry 读项目 `.agate-version`（或 legacy 兜底）→ 得 AGATE_ROOT → exec `$AGATE_ROOT/scripts/{gate}.py`。
- Windows 复制模式：`AGATE_HOOK_COPY_MODE=1` 或 `os.symlink` OSError → 复制入口 + 写 `.agate-root` 标记；resolve-entry 启动时经 `agate_common.resolve_agate_root` 的 `.agate-root` 恢复分支定位（BDD-19）。
- AGATE_ROOT env 覆盖最高（BDD-12）：resolve-entry 优先读 env。
- 3 个 hook 薄壳：`exec $PY $AGATE_ROOT/scripts/resolve-entry.py $(basename $0) "$@"`，`basename` 决定跑哪个 gate（pre-commit / commit-msg / pre-push）。
- **不重装 hook 切版本**：resolve-entry 每次运行时读 `.agate-version`，改声明即生效（BDD-18）。

### 4.4 3 个派发脚本归口决策（rev2 结论 6）

**决策：统一归口 `agate_common.resolve_agate_root`**。理由：
1. I-5 明示"解析入口不一致"风险——v1 项目级版本解析后，3 脚本若各自内联（env → 上溯两级）会得到不同 AGATE_ROOT（未走 current/latest 解析）。
2. 改动量小：3 脚本的内联 `_agate_root()` 函数体替换为 `from agate_common import resolve_agate_root` + 单行调用。
3. 副作用：3 脚本从"零依赖"变为依赖 `agate_common`（含 pyyaml）——**已验证 agate_common 顶部 `import yaml` 失败即 exit 1**，而 3 脚本当前不 import agate_common（为避免 pyyaml 依赖）。归口后 3 脚本将要求 pyyaml 可用。
   - **风险缓解**：3 脚本运行场景（orchestrator 派发）本就需要 pyyaml（gate 判定链路全程依赖）；且依赖失败是 fail-closed（exit 1 报错）而非静默降级。可接受。
   - **备选**：若评审认为不可接受，可保留内联但复制同一段解析逻辑到 agate_common（仅函数体一致，不 import）——本设计取归口方案。

### 4.5 agate-install（安装/卸载/环境探测）

- **repo 单克隆**：`git clone <url> ~/.agate/repo`（首次），之后 `git worktree add ~/.agate/vX.Y.Z vX.Y.Z`。
- **无参**：装 latest 指针（最新发布 tag 的 worktree）+ current → latest（BDD-1/4）。
- **`agate-install v0.48.0`**：装指定版本 worktree（BDD-2）；幂等：先查版本目录/指针存在 → 存在即跳过不报错（BDD-3，MV 确认 git 重复 add 会 exit 128，必须程序预判）。
- **`--uninstall v0.43.0`**：引用保护扫描（设计稿 §8.3）——扫描 `$HOME` 下 `.agate-version`（限 `~` 深度，mtime 合理限流）声明该版本 → 拒绝卸载（BDD-6）；无引用 → 删版本目录 + worktree remove + 清理/重指 latest/current 指针（BDD-5）。
- **`--check`**：探测 python3 / pyyaml / git / bash，全齐 exit 0（BDD-7）；缺项非 0 + 分平台修复指引（Linux `pip install pyyaml`；Windows Python/PATH/PYTHONUTF8/Git for Windows，BDD-8，I-13）。

### 4.6 agate-summary 集成（BDD-20/21）

- 显示：解析到的版本号（`.agate-version` 声明的 vX 或全局 current→latest→vY）+ 原因说明（"引用 .agate-version" / "全局 current"）。
- 复用 agate_common 解析结果，不重复实现。

### 4.7 离线部署包（BDD-22~29，I-8/9/10）

**agate-pack-offline.py**（外网）：
- `agate-pack-offline.py v0.48.0 [--platform linux-x86_64|windows-x86_64] [--include-python] [--include-pillow]`。
- 流程：worktree 检出 tag → 平台标签 bundle 目录 → `pip download --platform <目标> --python-version 311 --only-binary=:all: --no-deps pyyaml [Pillow]`（MV 确认 `--platform win_amd64/manylinux_2_17_x86_64` 可行）→ 嵌入式 Python 可选 → manifest.json（platform + 各组件 sha256）。
- 失败路径（BDD-24）：tag 不存在 → 报错退出非 0；pip download 网络失败 → 报错非 0；wheel 缺失 → 报错非 0；不产可用 bundle。

**install-offline.py**（内网）：
- 读 manifest.json → 平台核对（不匹配警告 + 拒绝，exit 非 0，BDD-25）→ checksum 校验（不匹配拒绝 + 指明组件，BDD-26）→ `pip install --no-index --find-links wheels/`（BDD-27）→ 建 `~/.agate/vX.Y.Z/`（bundle 复制目录，非 worktree）→ hook/orchestrator 指向（Linux 软链 / Windows 复制）→ 验证（agate-summary 等价，BDD-28）。
- 勾选：`--skip-python` / `--skip-pillow` 覆盖包含项（BDD-29）。

### 4.8 设计中新发现的隐含需求（[SCOPE+] 标注意见）

- 无。调研结论 + P1 基线已覆盖全部实现决策点；未发现 P1 未预见的必须做的事。若实现中出现，由 implementer 标 `[DESIGN_GAP]` 回传。

## 5. files_to_read（P4 implementer 上下文地图）

> 只列实现确实需要参考的文件。大文件标行号范围。全部在 worktree `agate/` 下（AGATE_ROOT 视角同构）。

```yaml
files_to_read:
  - path: agate/scripts/agate_common.py:76-94
    why: resolve_agate_root 现有语义（env 优先 → 上溯 → .agate-root），项目版本解析在此做加法
  - path: agate/scripts/install-hook.py:86-148
    why: 现有安装契约（argv[1] > env > ~/.agate）+ 软链/复制模式；改造为装 resolve-entry
  - path: agate/scripts/pre-commit-gate.sh
    why: 3 个 hook 薄壳代表——现有 AGATE_ROOT 自定位 + python 探测 + exec py，改为经 resolve-entry
  - path: agate/scripts/agate-summary.py:115-160
    why: main 当前 git describe 显示仓库版本，改为显示项目解析版本 + 原因
  - path: agate/scripts/agate-inject-card.py:28-33
    why: 内联 _agate_root 参照，归口 agate_common.resolve_agate_root 的改造对象
  - path: agate/scripts/check-protocol-consistency.py:765-789
    why: CHECK 10 SCRIPT_REF_RE 白名单，新脚本须入清单/白名单
  - path: agate/scripts/ci-gate-backstop.py:16
    why: 复核 _AGATE_ROOT 上溯在 CI 语境下正确（不改）
  - path: agate/tests/unit/test_install_hook.py
    why: 既有 hook 测试（_make_fake_root / AGATE_HOOK_COPY_MODE 复制模式），resolve-entry 改造的回归基线
  - path: agate/tests/conftest.py
    why: fixture 体系（agate_root / task_dir / git_repo / run_cli / py_path），新增测试复用
  - path: agate/tests/integration/test_pre_commit_hook.py:1351
    why: bdd-19 复制模式既有用例，hook 改造后须仍通过
  - path: archived/docs-2026-08/plans/agate-version-management-20260813.md:152-198
    why: 设计稿 §8 决策定稿（dev 不默认 / current→latest / 引用即保护 / summary 显示版本+原因 / v1 范围）
```

## 6. env_constraints（确认/细化 P0-brief）

```yaml
env_constraints:
  debug_env: "Linux（本机）；Windows 靠 CI matrix（pytest -m windows_smoke）+ AGATE_HOOK_COPY_MODE=1 模拟，不宣称已实测 Windows"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh"
  isolation_check: "worktree 内设计 + 只读扫描代码；~/.agate（稳定版）/主 checkout 禁止改动；本任务只出设计文档，不写功能代码"
  external_tools: "git worktree / pip download --platform / pip install --no-index（最小验证已确认可用，executor_env.network=full）"
```

## 7. minimal_validation（已通过）

> 本任务依赖外部工具行为（git worktree / pip download / checksum），设计阶段已做最小验证（bash 脚本 /tmp/opencode/tag0008-mv.sh，上一轮 architect 实测通过，结论直接采信）。

```yaml
minimal_validation:
  assumption: "git worktree add tag / pip download --platform 按平台拉 wheel / sha256 checksum 计算"
  method: "20 行 bash 脚本实测三项外部工具行为"
  result: "confirmed"
  note: "[1] worktree add <path> <tag> 成功（detached HEAD @ tag）；重复 add 已存在路径 → exit 128 'already exists' → 幂等必须程序先判存在（BDD-3 依赖此预判）。[2] pip download --platform win_amd64/manylinux_2_17_x86_64 --python-version 311 --only-binary=:all: --no-deps → 按目标平台拉到对应 wheel → pack-offline 按平台拉 wheel 可行。[3] sha256 用 hashlib 标准库，64 hex 字符 → manifest checksum 链路可行。"
```

## 8. dispatch_plan（high 复杂度硬规则）

### 8.1 工作量五维评估

| 维度 | 评级 | 依据 |
|------|------|------|
| 产出规模 | high | 5 新 py + 改 ~12 py/sh + 5 新测试文件 + 文档 13 项 |
| 输入规模 | high | P1（378 行）+ P0-brief + 设计稿 + 影响面表跨 2.1/2.2/2.3 |
| 改动性质 | high | 跨模块改动（scripts/文档/测试三联动）、hook 契约变更 |
| 耦合度 | high | 共享 agate_common.py（解析统一归口）+ 3 hook 共用 resolve-entry |
| 认知负荷 | high | 需读全貌（版本解析链路贯穿 install→resolve→hook→summary） |

综合：**high → 必须拆批**。

### 8.2 编排方案（frontmatter dispatch_plan 单行 YAML）

```
dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [
  {id: resolve-chain, complexity: high},
  {id: install, complexity: high},
  {id: offline, complexity: high}
]}
```

### 8.3 批次明细（P3-P6 派发用）

| 批次 id | complexity | 内容（产出） | 依赖 |
|---------|-----------|--------------|------|
| `resolve-chain` | high | agate-resolve.py + agate_common.py 解析集成 + resolve-entry.py + 3 hook 薄壳 + install-hook.py + agate-summary.py + 3 内联脚本归口 + 相应测试 | 无（解析链路最先，其他批依赖其解析语义） |
| `install` | high | agate-install.py（install/uninstall/--check）+ 相应测试 | resolve-chain 的解析语义（install 建版本目录供 resolve 消费） |
| `offline` | high | agate-pack-offline.py + install-offline.py + 相应测试 | resolve-chain 的 agate_common（checksum/平台工具函数） |

- **共享文件后处理**：`agate_common.py` 是 resolve-chain 批次的修改对象，install/offline 批次只读使用 → 主 Agent 须先跑 resolve-chain 批再并跑其余（或三批共用后由主 Agent 统一 merge，遵守 dispatch-protocol「并行规则」共享文件统一后处理）。
- **批次数 ≤ parallel_limit**：3 ≤ 3 ✓；每批含 id + complexity ✓。
- **BDD 全局编号**：三批各自承接的 BDD 已全局唯一（BDD-1~31），无包归属重复（agate 单包）。

### 8.4 完成标志（供 P3 测试设计 + P5 验证）

1. `agate-resolve` 在 4 种场景（项目锁定/向上查找/无声明回退/声明未安装回退）输出正确 AGATE_ROOT + reason（BDD-9~14）。
2. 3 个 hook 在 A 锁旧版、B 用新版、切版本、复制模式 4 场景下各自跑对应版本 gate（BDD-16~19）。
3. `agate-summary` 显示项目解析版本 + 原因（BDD-20/21）。
4. `agate-install` 幂等/卸载引用保护/环境探测 3 场景通过（BDD-1~8）。
5. pack-offline 产 manifest（platform+checksum）+ 失败路径非 0（BDD-22~24）。
6. install-offline 平台核对/checksum/wheels/勾选 4 场景通过（BDD-25~29）。
7. legacy 单软链用户不跑新工具直接 commit 无 breakage（BDD-30）；gate 判定逻辑 diff 仅解析层（BDD-31）。

## 9. 与既有模式的参照

- 版本解析的"asdf 模式 cwd 向上查找"参照设计稿 §2（业界实践参考）。
- 指针复制/配置文件模式（Windows 无符号链接权限）复用 TAG0004/platform-notes 先例（`.agate-root` 标记）。
- hook 薄壳模式（python 探测 + exec py + fail-closed）延续 TAG0010 既有薄壳结构，仅改 exec 目标为 resolve-entry。
