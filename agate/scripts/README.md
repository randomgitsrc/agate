# agate scripts 目录

agate 的所有自动化脚本。`pre-commit-gate.sh` 是 hook 入口，`check-*.sh / .py` 是各检查脚本，`agate-summary.sh / agate-changes.sh` 是版本发现工具。

## 脚本清单

### Gate 检查（pre-commit hook 触发）

| 脚本 | 用途 | 退出码语义 |
|------|------|-----------|
| `pre-commit-gate.sh` | hook 入口，按顺序调度 9 项检查 | 0=通过, 1=拦截, 2=WARNING |
| `check-state-yaml.sh` (P2.15) | `.state.yaml` 格式校验 | 0=通过, 1=格式错, 2=无文件 |
| `check-gate.sh` (P1.1) | 各阶段脚本化 gate | 0=通过, 1=未通过, 2=需自判 |
| `check-changelog.sh` (P1.6) | `[Unreleased]` 含 task_id | 0=通过, 1=未记录 |
| `check-p6-evidence.sh` (P1.7) | P6/P7 证据目录非空 | 0=通过, 1=缺证据, 2=无 P6 文件 |
| `check-p6-provenance.sh` (P2.1/P2.10) | P6 客观行为审计（三道）| 0=通过, 1=审计失败, 2=WARNING |
| `check-state-transition.sh` (P2.3-P2.5) | 状态转移合法性 + 重试上限 | 0=通过, 1=非法转移 |
| `check-pruning.sh` (P2.7-P2.9) | 裁剪条件 + override 校验 | 0=通过, 1=不一致 |
| `check-scope-resolved.sh` (P2.11) | `[SCOPE+]` 标记追踪 | 0=通过, 1=未标记 |
| `check-retrospective.sh` (P2.12) | 异常模式提醒（不阻塞）| 0=总是通过 |
| `gate-result.sh` | gate 结果工具函数库 | （被 source）|

### CI 兜底

| 脚本 | 用途 |
|------|------|
| `ci-gate-backstop.py` (P1.3) | push 后重跑 gate + P6 git blame 单 author WARNING |

### 安装

| 脚本 | 用途 |
|------|------|
| `install-hook.sh` | 在项目仓库内安装 pre-commit hook（接受 `AGATE_ROOT` 参数）|

### 版本发现（agent 快速掌握协议变化）

| 脚本 | 用途 |
|------|------|
| `agate-summary.sh` | 输出当前版本 + 防护机制状态 + 启动建议 |
| `agate-changes.sh` | 显示与指定 tag 之间的变更（commits + 受影响文件 + 重要性分类）|

**典型场景**：agent 上次会话用 v0.4.0，现在 agate 升到 v0.5.0——跑 `agate-changes.sh v0.4.0` 快速看变化，决定重读哪些必读文件。

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

## 6 类检查

| 检查 | 抓什么 | 对应评审条目 |
|------|--------|-------------|
| CHECK 1 | 所有 ```yaml 代码块可被解析（含占位符的会先 sanitize 再校验缩进） | P0-3 |
| CHECK 2 | 协议文件引用的 docs/assets/scripts 路径真实存在 | P0-4, P1-3 |
| CHECK 3 | 协议文件无硬编码行号引用 `xxx.md L123`（应用节标题） | P1-4 |
| CHECK 4 | `gate_commands` 键集合跨文件一致（以 architect.md 为权威） | P1-2 |
| CHECK 5 | 「N 个协议文件」计数声明 == 实际列表长度 | P1-1 |
| CHECK 6 | README LICENSE 徽章指向的文件存在 + gstack MIT 归属保留 | P0-2 |

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

`.github/workflows/protocol-consistency.yml` 已配置：每次 push / PR 自动运行，默认 ERROR 阻断、
WARNING 放行。想让 WARNING 也阻断，把 workflow 里的命令改成加 `--strict`。

## 已知 WARNING（当前仓库，均非缺陷）

跑当前（已修复的）仓库会有 4 个 WARNING，都是预期内的、不需修：
1. `analyst.md` 的 capability_requirements 示例含 `@vision-helper`（YAML 保留字符，加引号更规范，但作为示例无害）
2-4. 几处叙事文件引用了「提议中但尚未创建」的文件（如本脚本早期提议的 `.sh` 版本名）

要消除 WARNING 1，给 analyst.md 那行加引号：`- "@vision-helper（若可调用，作为补充）"`。
