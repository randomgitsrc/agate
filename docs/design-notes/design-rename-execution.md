# Agateon 改名执行设计

> 状态：评审通过（3 轮独立评审收敛，2026-08-25 合并入 main）｜ 日期：2026-08-25
> 前置：`rename-recommendation.md`（2026-08-23 已决策改名 Agateon）——本文不重复"为什么改"，只回答"怎么改"。
> 定位：RM-AG0035「品牌改名执行」的执行地基，与 `design-agateon-portal.md` 同级。

## 1. 核心原则：外部 agateon，内部 agate

改名最大的陷阱是把"改名"理解成"全局 find-replace `agate` → `agateon`"。那样会把协议基础设施一起掀翻。正确的原则是分层：

| 层 | 命名 | 决策 | 状态 |
|----|------|------|------|
| **外部品牌层** | `agateon` | 仓库名、域名、包名占位、README 标题、CLI 别名 | 已定（2026-08-23）|
| **内部命名空间** | `agate` | 目录 `agate/`、`~/.agate`、`AGATE_*`、`agate-*.py`、`agate_common` | 当前保留（v1.0 窗口重评估用户面，见 §8）|

一句话：**仓库名跟随品牌（agateon），目录名跟随功能（agate），两者解耦。** 外部层必须现在定死（产生搜索粘性），内部层多数永不改名（不参与搜索），少数用户面项在 v1.0 窗口显式重评估。

## 2. 关键教训：撞名有两个维度，org 只解决一个

改名 Agateon 的第一动机是 `agate` 的搜索污染（GitHub `in:name` 命中 1223 个仓库）。但"撞名"有两个维度，必须分清：

| 维度 | `agateon/agate`（org 方案）| `agateon`（主仓名）|
|------|---------------------------|---------------------|
| URL 唯一性 | 不撞（org 隔离）| 不撞 |
| **搜索辨识度（`in:name`）** | **撞**：仓库名还是 `agate`，照样被 1223 个淹没 | **不撞**：搜 `agateon` 直达、唯一 |

GitHub 的 `in:name` 搜索看的是**仓库名**，不区分 org。所以 `agateon/agate` 的仓库名是 `agate`：搜 `agate` 仍淹没在 1223 个里，搜 `agateon` 又查无此仓（org 名不参与仓库名搜索）。**结论：主仓名必须是 `agateon`，不能是 `agate`**（即使在 org 下）。

**措辞修正**：`agateon` 含 `agate` 子串，搜 "agate" 仍会命中本仓（子串匹配），所以严格说不是"摆脱污染"，而是**新增唯一品牌词 `agateon`**——让用户能用精确词直达，这是改名实际达成的效果。旧词 `agate` 的流量靠 README "formerly agate" 引导回收。

## 3. 决策记录

### 3.1 仓库名：主仓 `agateon`

- **主仓**：`randomgitsrc/agate` → `randomgitsrc/agateon`。原 URL 301 自动跳转；但本地 remote 与 `install.sh`/`agate-install.py` 的硬编码 URL 需**主动 `git remote set-url` + 同批更新**（301 兜底能"用"但新仓自带安装器会继续向新用户展示旧名）。
- **门户**：将来另开独立仓 `agateon-portal`（暂定），依赖单向（portal → 协议仓），物理隔离。
- **org**：暂不建（用户决策）。**风险提示**：`rename-recommendation.md` §6 与 `agateon-trademark-research.md` 摘要均建议"注册后立即占 npm/PyPI/GitHub org 防抢注"；`agateon` org 名可能被第三方抢注（这正是"将来再改来不及"场景）。建议至少注册**空 org `agateon` 仅占名**（成本≈0，不迁仓），是否执行待用户拍板。
- **否决方案**：
  - monorepo（`agateon/` 里塞 `core/` + `sitesrc/` + `dist/` + `docs/`）——否决理由：协议与门户**发布节奏不同**（协议 v0.62 补强中，门户 v1.0 后才立项）、依赖单向、单仓名只能承载一个品牌面。
  - `agateon/agate`（org 方案）——否决理由：见 §2，仓库名降回 `agate`，品牌词查无此仓。
  - `agateon.com` 作门户仓库名——否决理由：与主仓 `agateon` 只差 `.com`，搜索/分享易混。暂定 `-portal` 后缀。

### 3.2 目录名：`agate/` 永久保留

- `agate/` 不是纯品牌层，是协议基础设施：`~/.agate` 软链目标、所有 hook 的 `AGATE_ROOT`、31 个 `agate-*.py` 的自定位根、双工作区纪律的物理基础。
- 内部目录不参与搜索、不产生品牌粘性，改名成本收益不划算。**永久保留**，不议 `core/`。
- `agate-workspace/` 同理：任务数据目录（tasks/roadmap/debt），保留。
- 注：roadmap RM-AG0035 原文写目录"暂保留"，已回写对齐为"永久保留"（2026-08-25）。

### 3.3 基础设施层：区分"纯内部"与"用户面"

- **纯内部（永久保留）**：`agate_common`（被 51 个文件引用的公共库）、`check-*.py` 20 个 gate 脚本（已不带 agate 前缀，用 `check-` 前缀）、`resolve-entry.py`。
- **用户面（当前保留，v1.0 窗口重评估，见 §8）**：`~/.agate` 安装路径、`AGATE_*` 环境变量、`agate-*.py` CLI 命令名——这些对将来真实用户是可感知的（写进 shell rc、任务卡、教程），"永不改名"的成本收益要在首个真实用户出现前再评估一次。

## 4. 影响面盘点（测量口径见尾注）

| 面 | 数量（实测）| 层次 | 处理策略 |
|----|------|------|----------|
| `agate-*.py` CLI 工具 | 31 个 | 用户面 | 当前保留；v1.0 加 `agateon-*` 别名 |
| `check-*.py` gate 脚本 | 20 个 | 纯内部 | 不涉及（已无 agate 前缀）|
| `agate_common` 公共库 | 51 个文件引用 | 纯内部 | 保留 |
| `AGATE_*` 环境变量 | 30+ 个变量（`AGATE_WORKSPACE` 225 处、`AGATE_ROOT` 178 处）| 用户面 | 当前保留，v1.0 重评估 |
| `~/.agate` 安装路径 | 440 个文件引用 | 用户面 | 当前保留，v1.0 重评估 |
| **硬编码仓库 URL** | `install.sh:24`、`agate-install.py:55`、`agate-changes.py:116`、`README.md:5` badge、`README.md:29` 安装入口、`README.zh-CN.md:5` badge、`README.zh-CN.md:29` 安装入口 | 品牌层 | **Phase 1 与改名同批更新** |
| `agate` 字符串总量 | 36,196 次（md+py+sh+yml+yaml）| 混合 | 按 §5.3 判定规则分类：独立词换、token 留 |
| CI workflow | 2 个 | 品牌/配置 | job 名、注释换，路径不动 |
| git tags / 历史 | 零影响 | — | git 不感知名 |

**尾注（测量命令，可复现；测量日期 2026-08-25）**：`grep -ro "agate" --include=*.md --include=*.py --include=*.sh --include=*.yml --include=*.yaml . --exclude-dir=.git --exclude-dir=.worktrees` 得 36,196 次（occurrence）；其中仅 `.md` 为 31,320。`AGATE_WORKSPACE` 225 处 / `AGATE_ROOT` 178 处按 `grep -rhoE ... agate/` 计 occurrence；`~/.agate` 440 为 `grep -rl` 的文件数（单位与 occurrence 不同，已标注）。**无 `from agate import`**（仓库无 `agate` 包，真实 import 面是 `agate_common`）。`agate-*.py` 用 `ls agate/scripts/agate-*.py` 计数（31 个）；`check-*.py` 用 `ls agate/scripts/check-*.py` 计数（20 个）。注：`rename-recommendation.md` §5 曾写"53 个 agate-*.py"，本文以实测 31 为准。

## 5. 分层迁移策略

### 5.1 品牌层（Phase 0-1，立即）

- README 标 "Agateon (formerly agate)"，CHANGELOG / 文档头同步
- 仓库改名 `agateon` + **同批更新 §4 表列出的所有硬编码 URL**（install.sh / agate-install.py / agate-changes.py / README badge / 安装入口）
- `git remote set-url` 主动更新本地 remote
- 域名 `agateon.com` 已注册（2026-08-25）；PyPI/npm/crates.io 包名占位（商标线独立，见 `agateon-trademark-research.md`）

### 5.2 基础设施层（v1.0 窗口，Phase 2）

- 协议正文、文档内品牌 prose 引用统一（按 §5.3 判定规则）
- CLI 别名策略（见 §5.4）
- 一致性 gate 联动（见 §6）

### 5.3 品牌 prose 的判定规则 + 迁移范围边界

**迁移范围边界（先定"哪些文件 in-scope"，再谈规则）**：

| 范围 | 文件 | 处理 |
|------|------|------|
| in-scope（品牌 prose 要换）| README.md / README.zh-CN.md、CHANGELOG.md（仅 `[Unreleased]` 与未来条目）、`agate/` 下协议正文、`docs/`（非 archived）| Phase 2 统一换 |
| 豁免 | `archived/`、`agate-workspace/`（任务记录/证据日志/历史文档）、CHANGELOG 历史条目 | 不改（保持历史真实）|

**判定规则（机器可执行）**：

- **backtick 代码 token 一律保留**（`agate/`、`~/.agate`、`AGATE_*`、`agate-*.py`、`agate_common`、`agate-workspace/`、`{agate_root}` 等路径/文件名/变量/命令名）：它们是基础设施标识，不是品牌。
- **非 backtick 的独立词 `agate`（普通 prose 文字）一律视为品牌引用**：Phase 2 换 `Agateon`。
- **大小写**：`agate`（小写 prose）/ `Agate`（句首、标题）→ `Agateon`；`AGATE` 全大写仅在变量名 `AGATE_*` 中出现，属 token 保留，不在 prose 替换范围。
- **命令示例**：文档教用户敲命令时，正文写 `agateon-*`（新名），首次出现处标注"兼容旧名 `agate-*`"。文件名 token（如 `agate-summary.py`）仍保留。

规则判定方式：backtick 内外 + 词边界可由脚本判定（半机械）；最终以 Phase 2 的 brand-check 扫描 in-scope 文件为准，辅以人工抽查。

### 5.4 别名落地机制（v1.0）

- **形态**：symlink（Linux/macOS）+ 同内容 wrapper/copy（Windows，`ln -sf` 退化为复制后的 `agateon-*` 副本需同目录 `import agate_common`，按平台分支断言，遵循项目"不硬编码单平台假设"硬约束）
- **安装/卸载**：`agate-install.py` 生成/清理别名；`agate-summary` 等入口同时支持 `agate-*` 与 `agateon-*`
- **SELF-GATE 配合**：Phase 2 改 `agate/` 下协议文档与脚本属 self-gate 触发文件，每个 commit 须带 `self-gate-review:` / `self-gate-skip:` 标注

### 5.5 门户（门户立项时，Phase 3）

- 新建 `agateon-portal` 仓，依赖协议仓；届时再议是否建 org

## 6. 一致性 gate 联动（事实版）

**事实**：现有 `check-protocol-consistency.py` **不校验品牌词**——其中的 `agate` 出现均为路径前缀（`agate/WORKFLOW.md`、`agate/scripts/`、`agate-workspace/`、`{agate_root}` 占位符）或个别描述/注释文本（docstring、argparse 说明，非判定逻辑），CHECK 8 关键词是 `DESIGN_GAP`/`design_trivial`/`model_tier`/`--cached` 等协议术语，与品牌无关。**目录保留不动，Phase 1 改名不触发任何 check 变化。**

**决策**：一致性 gate 只校验结构一致性，**不新增硬性品牌 gate**。品牌统一靠 CHANGELOG/发布清单人工 + 一次性 `brand-check`（Phase 2 验收时扫描 in-scope 文件品牌残留，见 §7；它是**一次性验收工具，不进 CI 常驻 gate**，避免改名时 check 爆炸）。

**边界提示**：Phase 2 引入 `agateon-*` 别名后，`check-protocol-consistency.py` 的 CHECK 10 脚本名白名单（`SCRIPT_REF_RE` 只认 `check-*/agate-*/agate_*` 形状）不识别 `agateon-*` 引用——别名文档化后失去对 `agateon-*` 的脚本名漂移保护。若 Phase 2 落地别名，需同步扩展 CHECK 10 白名单识别 `agateon-*`（属 Phase 2 执行细节，记此备忘）。



## 7. 迁移节奏与验收锚

| Phase | 动作 | 验收锚 |
|-------|------|--------|
| 0（立即）| 品牌声明：README/CHANGELOG 标 Agateon | 首页可见 "Agateon (formerly agate)" |
| 1（决策后）| 仓库改名 `agateon` + 硬编码 URL 同批更新 | 旧 URL 301；`git ls-remote` 新名正常；`install.sh`/README.md/README.zh-CN.md/`agate-install.py`/`agate-changes.py` 无旧 URL 残留；`in:name` 首屏命中 `agateon` |
| 2（v1.0）| 基础设施统一：脚本别名 + 文档品牌引用 + brand-check | CLI `agateon-summary` 与 `agate-summary` 输出/退出码一致；brand-check 扫描权威文档（README/CHANGELOG/协议正文）品牌 prose 已统一 |
| 3（门户立项）| 新建 `agateon-portal` | portal 独立仓可跑 |

## 8. 已收敛决策

1. **`agate/` 目录名**：永久保留，不改成 `core/`。内部实现不跟品牌。
2. **`~/.agate` 安装路径**：当前保留（改名成本巨大）；**v1.0/首个真实用户出现前重评估**——届时新装路径可考虑 `~/.agateon`（软链兼容 `~/.agate`），新用户教程用 `agateon-*` 命令，避免每个新用户 home/rc 里永远印着旧品牌。
3. **`agate-workspace` 目录名**：保留。与 `AGATE_WORKSPACE` 变量（225 处）强绑定，与 `agate/` 成对。
4. **PyPI/npm/crates.io 包名**：占位 `agateon`（防抢注）；当前无打包发布计划，内部 import 面是 `agate_common`（无 `agate` 包），保持不变。

## 9. 开放问题（仅剩）

1. **GitHub org 占名**：是否立即注册空 org `agateon` 仅占名防抢注（不迁仓）？还是接受抢注风险、门户立项时再议？——待用户拍板。
