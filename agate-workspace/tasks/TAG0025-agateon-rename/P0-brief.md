# P0-brief — TAG0025 Agateon 品牌改名执行 Phase 0-1（RM-AG0035）

> 本文件由主 Agent 亲自填写（P0 阶段产出）。执行地基：`docs/design-notes/design-rename-execution.md`
> （2026-08-25 三轮独立评审通过合入 main）。

## task

"Agateon 品牌改名执行 Phase 0-1（RM-AG0035 剩余工作②，设计文档 §7 Phase 0/1）：品牌声明——
README×2 / CHANGELOG 标 'Agateon (formerly agate)'；GitHub 主仓改名 `agate` → `agateon`；
同批更新全部硬编码仓库 URL（design §4 实测 7 处：install.sh / agate-install.py /
agate-changes.py / README.md badge+安装入口 / README.zh-CN.md badge+安装入口）；
本机所有 remote 迁移（git remote set-url）。三层解耦原则：**外部品牌层改（仓库名/品牌 prose），
内部命名空间不动**（`agate/` 目录 / `agate-workspace/` / `~/.agate` / `AGATE_*` / `agate-*.py` /
`agate_common` 永久保留或 v1.0 窗口重评估）。Phase 2（v1.0：CLI 别名 + 品牌 prose 统一 +
brand-check）与 Phase 3（门户）明确不在本任务范围。"

### scope（设计文档对应）

- **Phase 0**（设计 §5.1）：品牌声明——首页可见 "Agateon (formerly agate)"
- **Phase 1**（设计 §5.1/§7）：仓库改名 + 硬编码 URL 同批更新 + `git remote set-url` +
  验收锚（旧 URL 301 / `git ls-remote` 新名正常 / 无旧 URL 残留 / `in:name` 首屏命中 `agateon`）
- **out-of-scope**：Phase 2（agateon-* 别名/品牌 prose/brand-check/CHECK 10 白名单扩展）、
  Phase 3（agateon-portal 门户）、商标正式申请（用户侧人工，调研已完成）、
  PyPI/npm/crates.io 占位（用户侧账号操作）

## known_risks

- "同类/影响面预判（硬编码 URL）：design §4 已实测 7 处（install.sh:24 / agate-install.py:55 /
  agate-changes.py:116 / README.md:5,29 / README.zh-CN.md:5,29），须**同批全改**；
  该盘点以安装入口为中心，P1 须补全仓扫描 `randomgitsrc/agate` 字符串（CI workflows /
  docs 链接 / badge img src / 文档内嵌 URL），命中清单与数量记入 P1"
- "同类/影响面预判（remote）：仓库改名后 GitHub 301 覆盖 git 协议，但本地 clone 不自动跟随——
  本机主 checkout + 所有现存 worktree 的 remote 都需 set-url；P1 须枚举 `git worktree list`
  清单。本地目录名 `/home/kity/oclab/agate` **不改**（本地路径与 GitHub 仓名解耦，
  DSH 会话/软链/`~/.agate` 均不受影响）"
- "内部命名空间禁动：全局 find-replace `agate`→`agateon` 是本任务最大反模式（设计 §1）——
  36,196 处 `agate` 字符串中绝大多数是基础设施 token；backtick token 一律保留，
  仅非 backtick 独立词属品牌层（§5.3 判定规则），且品牌 prose 统一属 Phase 2 非本任务"
- "不可逆外部操作：GitHub 仓库改名一次、对外可见——执行前须确认：① `gh` 具备 repo 管理权限
  （实测 dry-run 或权限查询）② 用户在场确认放行；改名后立即跑验收锚 4 条（301 / ls-remote /
  无残留 / in:name）"
- "CI 耦合：改名后 push/PR 事件自动跟新仓名（GitHub 侧），但 README badge img src 与
  actions 徽章 URL 硬编码旧仓名须同批改，否则徽章断链；一致性 gate 不校验品牌词
  （设计 §6），改名本身不触发 CHECK 失败"
- "CHANGELOG 纪律：本任务首个 commit 批次建立 `[Unreleased]` 段并含 TAG0025 条目
  （P1.6 check-changelog 要求；当前 CHANGELOG 无 [Unreleased]，属正常发布间歇态）"
- "design note 为执行地基但非强制照搬：P1-P4 发现实操层面问题（如 301 行为意外、
  硬编码 URL 盘点遗漏）按实际调整（改设计/登记 DEBT），不硬套"
- "用户侧协同项（写入交接单跟踪，不计本任务交付）：① 商标申请（申请前人工复核
  EAGATON/AGATON/AGON 商品项目，见 agateon-trademark-research.md）② PyPI/npm/crates.io
  包名占位 ③ org 迁移随门户立项再议（agateon org 已占名）"

## executor_env

platform: "dsh（DeepSeek Harness Web GUI，Qwen3.8-Max）"
has_task_tool: true
has_local_runtime: true
network: "full"

## env_constraints

debug_env: "python3 -m pytest agate/tests/{unit,regression,integration}/ + test_sanity.py +
scripts/ 分片跑（每片外层 timeout）；python3 agate/scripts/check-protocol-consistency.py
--strict-errors-only；gate/hook 用 ~/.agate 稳定版；consistency 必须用 worktree 自己的"

## 推进条件自检（P0 卡要求）

- **时效性自检**：立项与启动同日（2026-08-26）；前置全部新鲜——设计文档 2026-08-25 评审通过、
  商标调研 2026-08-25、org 占名 2026-08-25、域名注册 2026-08-25 → **已核对，无漂移**
- **环境自检**：bash 5.2 / python 3.12.3 / pytest 9.0.3 / pyyaml / shellcheck / ruff 0.16.4
  全部可用（worktree Step 2 实测）；基线全绿——unit 1160+2 skipped / 其余 131 /
  consistency 0 ERROR（2026-08-26 worktree 实测）
- **同类/影响面预判**：已含（见 known_risks 前两条，量级与清单口径来自设计 §4 实测）
- **任务粒度**：一句话可描述（品牌改名 Phase 0-1 执行），不需拆分；Phase 2/3 已显式切出
