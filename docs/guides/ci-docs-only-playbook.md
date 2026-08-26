# CI docs-only 快路径攻略

> 本文档记录 Agateon 仓库"docs/site 改动不被全量 CI 卡死"的完整机理、历史踩坑与操作准则。
> 面向：任何让 site/、docs/ 改动走快路径的 agent / 开发者。
> 权威源码：`.github/workflows/protocol-tests.yml` 头部修复史 + 本攻略。

## 1. 目标

- **纯内容改动**（`docs/`、`site/`、README、archived 等）必须快——不被 1300+ 用例的 pytest 全量拖住。
- **治理改动**（AGENTS.md、`.github/workflows/`）必须全量——改了门禁本身必须验透。
- 判断依据是**改了哪些路径**，不是"这次改动大不大"。

## 2. 机理（detect-docs-only 快路径）

### 2.1 白名单判定

`protocol-tests.yml` 的 `detect-docs-only` job 计算本次变更是否**纯白名单内路径**：

```yaml
NON_DOCS=$(... | grep -vE '^(agate-workspace/roadmap/|agate-workspace/debt/|archived/|docs/|site/|HANDOFF-...|README.md$|...|\.github/workflows/docs-check\.yml$)')
if [ -z "$NON_DOCS" ] && [ -n "$CHANGED" ]; then docs_only=true; fi
```

- `NON_DOCS` 为空 → 纯内容 → `docs_only=true`
- 任何白名单外路径（AGENTS.md、workflow 文件、`agate/`、`agate-workspace/` 非 roadmap/debt 部分）→ 全量
- **任何判定异常 → 保守回退 `docs_only=false`（fail-closed，跑全量）**

### 2.2 required job 内嵌 fast-pass（不是 skip）

为什么不用 `paths-ignore` / job 级 `if` 跳过？历史教训（见 protocol-tests.yml ① ②）：

| 做法 | 问题 |
|------|------|
| `paths-ignore` 跳过整个 workflow | required checks 无 check-run → 分支保护按 pending → **永久 BLOCK** |
| job 级 `if` 跳过 | check conclusion=`skipped` → 分支保护对 skipped required check 同样 **BLOCK** |
| **当前：job 始终跑，docs_only 时内嵌 `echo + exit 0`** | conclusion=`success` → 分支保护满足 ✓ |

代价：docs_only 时各 required job 仍走 checkout/setup（约 20-40s），换取 required check success。

### 2.3 建分支 push 的全零 before 陷阱（2026-08-26 实修）

**病根**：`on: [push, pull_request]` 让每个 PR 触发**两遍** workflow（push 事件 + pull_request 事件）。
git-to-main 用 `gh pr checks --watch` 等**全部 run 的全部 check**，两遍都要绿。

**更阴的**：git-to-pr 建新分支的那次 push，`github.event.before` 是**全零**（`0000...0`，
GitHub 对新建分支的约定）。detect-docs-only 里 `git merge-base 0000... <head>` 失败 →
`MERGE_BASE` 空 → fail-closed 回退 `docs_only=false` → **连纯 docs/site 的 push run 也跑全量 pytest**。

实证（PR #218，纯 docs 改名）：

| run | 事件 | pytest 耗时 |
|-----|------|------------|
| 32940917596 | push（建分支，before=全零）| **1 分钟（全量）** |
| 32940923267 | pull_request | **0 分钟（fast-pass）** |

**修法**（当前实现）：detect-docs-only 对 push 事件检测到全零 before 时，**回退 diff 对
`origin/main`**——即"分支相对 main 改了哪些"，是建分支 push 的完整范围（fetch-depth:0 全量
克隆保证 origin/main 可用）。两个事件对纯内容 PR 都正确 fast-pass。

**为什么 NOT 改 `on:` 为"push 只限 main"**（2026-08-26 PR #222 实证）：
- 改了 `on:` 触发器的 PR，**GitHub 不再运行该 workflow 自身**（自引用）——推了两次修复
  （`pull_request: {}`、`pull_request: types: [...]`）都零 run（Protocol Tests）。
  这意味着"改 CI 触发"的 PR 过不了自己的 CI，落地成本/风险远高于收益。
- 还踩到：`pull_request: {}` 导致 workflow `startup_failure`（GitHub 解析器不认）。
- all-zeros 回退已达成同样目标（纯内容 PR 两个 run 都 fast-pass），且是 body-only 改动，
  不碰触发器，CI 正常跑（PR #219/#220 先例：body 改动不影响 PR 自身 CI）。
- 结论：**改 workflow 正文可以，改 `on:` 触发器的 PR 无法自我验证**。要改触发器需走
  临时放松分支保护 + 显式 admin 合并，只在收益明确大于成本时才考虑。

## 3. 操作准则（agent 照此执行）

### 3.1 判断这次改动该不该快

| 改了哪些路径 | 预期 | 说明 |
|-------------|------|------|
| 只有 `docs/`、`site/`、README、archived | 快（~1-1.5 分钟合并）| pytest/shellcheck fast-pass |
| 动了 `AGENTS.md` 或 `.github/workflows/` | 全量（~3-4 分钟）| 治理/门禁改动，必须验透 |
| 动了 `agate/`、`agate-workspace/` 任务数据 | 全量 | 协议本体 |

### 3.2 保持快路径的经验

1. **内容改动和治理改动拆成两个 PR**：纯内容 PR 走快路径；治理改动单独 PR 接受全量。
   不要把"加一篇博客 + 顺手改 AGENTS.md 一句话"捆在一起，那样整单变全量。
2. **改 AGENTS.md / workflow 前先想清楚**：这是治理文件，改了必然全量，代价约 3-4 分钟，
   不是 bug。
3. **保持 `on: [push, pull_request]` 双触发 + all-zeros 回退**：不要改 `on:` 触发
   （改了触发器的 PR 无法自我验证，见 2.3）；建分支 push 的全零 before 已由 detect-docs-only
   回退兜底，两个事件对纯内容 PR 都 fast-pass。
4. **验证快路径**：纯内容 PR 应看到 pytest job 0 分钟（`echo "docs-only PR: pytest skipped (fast-pass)"`）。
   若某纯内容 PR 的 pytest 跑了 1 分钟以上，说明快路径失效，回查 detect-docs-only 的
   all-zeros 回退是否被改坏。

### 3.3 遇到 CI 慢/卡的正确排查顺序

1. 先看是**哪几个 run** 在等（push run + PR run 都有吗？），各自 pytest 耗时多少。
2. 若纯内容 PR 的 push run 全量（>1 分钟）→ 查 detect-docs-only 是否正确处理了全零 before。
3. 若动了治理文件（AGENTS.md / workflow 正文）→ 全量是设计，接受或拆 PR。
4. 别臆测根因：拉失败 job 日志（`gh api repos/{owner}/{repo}/actions/jobs/{id}/logs`）看真实输出。
5. 若 run 长时间 queued 不启动 → 先查 GitHub Actions 是否在排队/故障，别把基础设施抖动
   误判成配置问题（2026-08-26 PR #222 教训：一度把 Actions 调度延迟误判成"自引用限制"）。

## 4. 相关文件

- `.github/workflows/protocol-tests.yml` —— 主 CI，头部修复史 ①-④
- `.github/workflows/docs-check.yml` —— docs 一致性（轻量）
- `.github/workflows/site-check.yml` —— site build（informational）
- `.github/workflows/deploy-pages.yml` —— main 合并后部署（push 本就限 main）
