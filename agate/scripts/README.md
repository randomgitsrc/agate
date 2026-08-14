# agate scripts 目录

agate 的所有自动化脚本。产品逻辑已全部 Python 化（TAG0010）：`check-*.py / agate-*.py` 是各检查脚本，`agate_common.py` 是公共函数库，`agate-summary.py / agate-changes.py` 是版本发现工具。仅 3 个 git hook 入口保留 `.sh` 薄壳（定位 AGATE_ROOT + python 探测 + exec 对应 `.py` 主程序 + 失败 fail-closed 阻断）。`agate/tests/scripts/` 下的 `count-tests.sh` / `check-windows-smoke.sh` 不在迁移范围，保持 sh。

> **Windows 用户**：agate 的 gate 脚本已全部 Python 化，不再依赖 bash + GNU coreutils。仅 3 个 hook 薄壳需要 sh 执行（Git for Windows 自带）。脚本可直接 `python3 ~/.agate/scripts/xxx.py` 运行。详见 `agate/platform-notes.md`「Windows 原生」章节。

## 脚本清单

### Bash 薄壳（.sh — 仅 3 个 git hook 入口）

> 薄壳只承担「定位 AGATE_ROOT（软链/复制模式 `.agate-root` 恢复）+ python 探测 + exec py 主程序 + 失败阻断」四件事，gate 判定逻辑全部在对应 `.py` 主程序单份维护。

| 脚本 | 用途 |
|------|------|
| `pre-commit-gate.sh` | pre-commit hook 入口薄壳，exec `pre-commit-gate.py` |
| `commit-msg-self-gate.sh` | commit-msg hook 入口薄壳，exec `commit-msg-self-gate.py` |
| `pre-push-gate.sh` | pre-push hook 入口薄壳，exec `pre-push-gate.py`（含 `AGATE_ALIGNMENT_REVIEW_THRESHOLD` 锚点关键字）|

### Gate 检查（pre-commit hook 触发，.py 主程序）

| 脚本 | 用途 | 退出码语义 |
|------|------|-----------|
| `pre-commit-gate.py` | hook 主程序：按顺序调度 9 项检查 + PROD_TOUCHED 检测 + dispatch-context hash 校验 + write_gate_result | 0=通过, 1=拦截, 2=WARNING |
| `commit-msg-self-gate.py` | commit-msg 主程序：self-gate 触发面检测 | 0=通过, 1=拦截 |
| `pre-push-gate.py` | pre-push 主程序：alignment 审查阈值判定 | 0=通过, 1=拦截 |
| `check-state-yaml.py` (P2.15) | `.state.yaml` 格式校验 | 0=通过, 1=格式错, 2=无文件 |
| `check-gate.py` (P1.1) | 各阶段脚本化 gate | 0=通过, 1=未通过, 2=需自判 |
| `check-changelog.py` (P1.6) | `[Unreleased]` 含 task_id | 0=通过, 1=未记录 |
| `check-p6-evidence.py` (P1.7) | P6 证据目录非空 + md5 逐字节去重（阻断）+ 像素方差/average hash 检测（WARNING）| 0=通过, 1=阻断, 2=WARNING |
| `check-p6-provenance.py` (P2.1/P2.10) | P6 客观行为审计（六道 + EXIT_CODE 一致性 + 协作规范）| 0=通过, 1=审计失败, 2=WARNING |
| `check-state-transition.py` (P2.3-P2.5) | 状态转移合法性 + 重试上限 | 0=通过, 1=非法转移 |
| `check-pruning.py` (P2.7-P2.9) | 裁剪条件 + override 校验 | 0=通过, 1=不一致 |
| `check-scope-resolved.py` (P2.11) | `[SCOPE+]` 标记追踪 | 0=通过, 1=未标记 |
| `check-retrospective.py` (P2.12) | 异常模式提醒（不阻塞）| 0=总是通过 |
| `check-frontmatter.py` | 阶段文件 frontmatter 校验 | 0=通过, 1=校验失败 |
| `check-p6-format.py` | P6 验收结果格式 --check/--fix 归一化 | 0=通过, 1=格式错 |
| `check-tdd-red.py` | TDD 红灯检查（读 gate_commands.P3 + formatter 判定 A/B 类）| 0=红灯/B 类, 1=A 类, 2=绿灯, 3=无运行器 |
| `check-platform-assumptions.py` | 平台假设静态扫描器（R1-R5，扫描覆盖 .bats/.bash/.sh/.py）| 0=零命中, 1=有命中, 2=目标不存在 |
| `check-debt.py` | 技术债登记校验：默认 FILE 模式=DEBT 条目 schema 校验（fail-closed）；`--retreat-coverage`=回退覆盖比对（`git log retreat:` 提交 vs `source: retreat` 条目，缺失 WARNING）| FILE 模式 0=通过, 1=校验失败；回退模式：依赖加载失败 exit 2（需主 Agent 自判），无 retreat 提交等有意跳过 exit 0 |

### 公共库

| 脚本 | 用途 |
|------|------|
| `agate_common.py` | 公共函数库（替代 `gate-result.sh` + `agate-workspace-resolve.sh`）：`write_gate_result` / `read_state_phase` / `read_state_task_id` / `has_staged_phase_change` / `resolve_formatter` / `run_test_with_formatter` / `resolve_workspace` / `probe_python` / `run_git` / `MAX_RETRY_MAP` 等。执行模式输出 `AGATE_WORKSPACE=` / `AGATE_TASKS_DIR=` 两行（workspace-resolve 契约）|

### CI 兜底

| 脚本 | 用途 |
|------|------|
| `ci-gate-backstop.py` (P1.3) | push 后重跑 gate + provenance 审计重跑 + git blame 单 author WARNING；多平台自动检测（GitHub/GitLab/Gitea）|

### 安装

| 脚本 | 用途 |
|------|------|
| `install-hook.py` | 在项目仓库内安装 pre-commit + commit-msg + pre-push hook（`ln -sf` 软链 / Windows 复制模式 + `.agate-root` 标记；接受 `AGATE_ROOT` 参数）|

### 版本发现（agent 快速掌握协议变化）

| 脚本 | 用途 |
|------|------|
| `agate-summary.py` | 输出当前版本 + 防护机制状态 + 启动建议 |
| `agate-changes.py` | 显示与指定 tag 之间的变更（commits + 受影响文件 + 重要性分类）|

**典型场景**：agent 上次会话用 v0.4.0，现在 agate 升到 v0.5.0——跑 `python3 ~/.agate/scripts/agate-changes.py v0.4.0` 快速看变化，决定重读哪些必读文件。

### 阶段卡片 CLI（Phase Card 渐进披露）

| 脚本 | 用途 |
|------|------|
| `agate-next-card.py` | 输出当前阶段卡片全文（PHASE 取值 P0-P8）|

**用途**：Phase Card 防漂移机制的权威卡片源。主 Agent 调 `python3 ~/.agate/scripts/agate-next-card.py P{N}` 拿到对应阶段卡片全文，嵌入 `dispatch-context-{role}.md`。后续 step 3 hook 会用 sha256 校验嵌入的卡片是当前版本（防过期/防篡改）。

**退出码语义**：
- 0：成功，stdout 输出卡片全文
- 1：参数缺失或过多
- 2：phase 不在 P0-P8 范围

**字节稳定性保证**：`agate/tests/unit/agate-next-card.bats` 的 9 个 sha256 测试断言 CLI 输出 body（去掉前 4 行固定头）的 sha256 等于 `cat ${PHASE}-*.md` 的 sha256。这是 step 3 hook 校验的前提。

### 工作区工具

| 脚本 | 用途 |
|------|------|
| `agate-migrate-workspace.py` | 旧布局（docs/tasks → agate-workspace/）迁移工具（git mv 目录级，幂等）|
| `agate-extract-context.py` | 提取任务上下文（BDD 计数 / implementation_dir / P5 失败参考）|
| `agate-archive-stale-outputs.py` | 回退时归档旧阶段产出（`.archived/{ts}-{phase}` + breadcrumb）|
| `agate-capture-env-baseline.py` | P5 环境基线捕获（gate_commands 结果快照 + fail-list）|
| `agate-retreat-to.py` | 跨阶段回退（状态 + 产出归档 + retreat commit + retries 追加）|
| `agate-inject-card.py` | 注入阶段卡片到 dispatch-context 的 AGATE_CARD 占位符 |
| `agate-render-dispatch-prompt.py` | 按角色渲染 dispatch prompt（主块 + 阶段特定提示）|

### 检查逻辑单点工具（纯 Python）

> 各 gate 脚本依赖的纯 Python 单点工具。**复制单个脚本到项目时须连带复制其依赖的 `.py`（同目录，含 `agate_common.py`）。**

| 工具 | 用途 | 依赖 |
|------|------|------|
| `agate-json-get.py` | stdin JSON → get/len/index/set/count_prefix/list/escape 子命令 | 无 |
| `agate-md-field-get.py` | frontmatter 优先 + 正则回退的双读字段提取，覆盖 P1/P2/P6/P7 共 20 个 op（risk_level/ui_affected/phases 等原有 3 个 + candidate_count/packages/domains/override/internal_only/internal_only_reason/design_trivial/follows_existing_pattern/pass/fail/blocker_count/deviation_count/deviation_critical_count/design_gap_count/design_gap_reviewed_count/need_confirm_resolved/suggest_resolved/scope_resolved 等 17 个新增 op，详见脚本内 docstring） | pyyaml |
| `agate-state-get.py` | .state.yaml 读 phase/task_id/retries_over | pyyaml |
| `agate-retreat-state.py` | 回退 check_retreat/write_retreat | pyyaml |
| `agate-read-gate-commands.py` | 解析 gate_commands.P3 块 → JSON | 无 |
| `agate-read-p5-commands.py` | 解析 gate_commands.P5 块 → JSON | 无 |
| `agate-state-yaml-check.py` | .state.yaml 格式校验 | pyyaml |
| `agate-changelog-unreleased.py` | 提取 [Unreleased] 区域 | 无 |
| `agate-card-inject.py` | 注入卡片到 AGATE_CARD 占位符 | 无 |
| `agate-vision-blocker.py` | 读 vision_analysis.blocker_count | pyyaml |
| `agate-evidence-consistency.py` | evidence JSON 与 P6 一致性 | 无 |
| `agate-image-check.py` | 截图方差 / average hash | Pillow（可选）|
| `agate-gate-missing-cmds.py` | gate_commands 缺失命令检测 | 无 |
| `agate-gate-p5-count.py` | 统计 P5 命令数（主/辅双值）| 无 |
| `agate-debt-check.py` | DEBT 条目多块 schema 校验（` ```yaml ` fenced 块解析：必填/枚举/evidence 非空/closed 准入/id 唯一；`--covered-hashes`=回退覆盖哈希提取）| pyyaml |
| `agate-frontmatter-check.py` | 阶段文件 frontmatter 校验（必需字段/顺序）| pyyaml |

---

## 协议结构一致性检查（P3-1）

> 回应 `LIMITATIONS.md`「局限 5：协议文档自身的内部一致性不在流程内」。
> 让 agate 协议文档自身也享受到它一直在鼓吹的「机器可判定的守护」。

## 它解决什么

agate 教别人「gate 必须机器可判定」，但自己的文档一致性此前全靠人肉维护——
评审 `agate-review-20260626-1.md` 挖出的低级错误（LICENSE 缺失、死引用、YAML 不可解析、
字段集不一致、清单计数对不上）就是实证。这个脚本把其中**可机器判定的结构一致性**自动化，
复发即拦。

**只做结构一致性，不碰语义一致性**——后者不可机器判定（协议自己也这么说），不在范围内。

## 8 类检查

| 检查 | 抓什么 | 对应评审条目 |
|------|--------|-------------|
| CHECK 1 | 所有 ```yaml 代码块可被解析（含占位符的会先 sanitize 再校验缩进） | P0-3 |
| CHECK 2 | 协议文件引用的 docs/assets/scripts 路径真实存在 | P0-4, P1-3 |
| CHECK 3 | 协议文件无硬编码行号引用 `xxx.md L123`（应用节标题） | P1-4 |
| CHECK 4 | `gate_commands` 键集合跨文件一致（以 architect.md 为权威） | P1-2 |
| CHECK 6 | README LICENSE 徽章指向的文件存在 + LICENSE 含 MIT + gstack 概念启发致谢保留于 NOTICES.md | P0-2 |
| CHECK 7 | README version badge 与最新 git tag 一致 | — |
| CHECK 8 | v0.6 关键词存在性（DESIGN_GAP / design_trivial / model_tier / --cached） | — |
| CHECK 9 | 协议-脚本结构对齐（锚点表：文档声明的规则 vs 脚本关键词存在性） | — |

> **CHECK 5（协议文件计数校验）已删除**：该校验基于"8 文件必读清单"假设——此清单已降级为 reference，计数不再有意义。检查项从 9 减到 8（CHECK 1-4, 6-9）。

## 用法

```bash
# 从仓库根运行（cwd 是协议仓库根 ~/<agate 仓库>）
python3 agate/scripts/check-protocol-consistency.py

# WARNING 也判失败（更严格）
python3 agate/scripts/check-protocol-consistency.py --strict

# 机器可读输出（CI 消费）
python3 agate/scripts/check-protocol-consistency.py --json
```

依赖：Python 3.8+ 和 `pyyaml`（`pip install pyyaml`）。

退出码：`0` = 无 ERROR；`1` = 有 ERROR；`2` = 仅 WARNING 且加了 `--strict`。

## 分级设计（避免假阳性爆炸）

脚本区分两类文件，避免误报：

- **协议文件**（WORKFLOW.md / dispatch-protocol.md / assets/ 等运行时遵循的规范）
  → 严格检查，死链、行号引用一律 ERROR
- **叙事文件**（docs/plans/ docs/reviews/ 等历史评审与计划）
  → 它们经常**引述**别处的旧问题（含已修复的行号、提议中的未来文件），死链降级为 WARNING

YAML 检查还区分：
- **契约结构 YAML**（缩进错误 = 真问题）→ 缩进类错误保持 ERROR
- **说明性示例 YAML**（含 `@`/反引号等 YAML 保留字符的标量）→ 降级 WARNING，提示加引号即可

## CI

`.github/workflows/protocol-tests.yml` 已配置：每次 push / PR 自动运行，默认 ERROR 阻断、
WARNING 放行。想让 WARNING 也阻断，把 workflow 里的命令改成加 `--strict`。

## 已知 WARNING（当前仓库，均非缺陷）

跑当前（已修复的）仓库会有约 280 个 WARNING，都是预期内的、不需修，主要来源：
1. `analyst.md` 的 capability_requirements 示例含 `@vision-helper`（YAML 保留字符，加引号更规范，但作为示例无害）
2. 大量叙事文件引用了「提议中但尚未创建」或已迁移/归档的文件（如历史评审引述旧路径、计划文档引用当时存在的任务产出）
3. 工作区任务产物（`agate-workspace/tasks/`）作为叙事文件宽松处理，其历史阶段产出互相引用旧 `docs/tasks/` 路径降级为 WARNING

要消除 WARNING 1，给 analyst.md 那行加引号：`- "@vision-helper（若可调用，作为补充）"`。
其余为叙事性引述，属正常现象，不需要修——WARNING 数量随任务/评审历史增长，不代表缺陷。
