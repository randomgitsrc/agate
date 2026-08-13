# TAG0004 交接单 — agate 脚本健壮性 + 环境适配

> 本交接单供 worktree session 的 agent 按此启动 TAG0004 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0004**：agate 协议脚本健壮性 + 环境适配（Windows 原生兼容 + Linux 基线回归）。

**一句话**：修一批已核实的环境/健壮性缺陷，让 agate 在 Windows + 中文路径/文件名/内容下也能正确运行，同时保证 Linux 现有行为完全不变。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0004` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版 v0.43.0（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定——gate 判定对象是 worktree 里的产出文件，但 gate 工具本身是 `~/.agate`。这是有意的：改造期间工具稳定，改造对象变化。
- **hook 在共享 git 目录**：worktree 的 `.git` 是文件（指向 `/home/kity/oclab/agate/.git`），hook 实际在主 checkout 的 `.git/hooks/`（pre-commit/commit-msg/pre-push 已软链安装）。worktree commit 时 hook 自动触发。

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷（全部有代码证据，见 P0-brief known_risks）

**审计发现（46 脚本逐行审计）**：
- **S1（SEVERE）** `pre-commit-gate.sh:50/57/339/343/350`：`STAGED_STATE_FILES`/`PROCESSED_DIRS` 空格拼接 + `for ... in $LIST` 未引号切词 → 路径含空格时 **fail-open 静默绕过整个 gate**
- **S3（SEVERE）** 13 个 py 的 `open()` 无 `encoding="utf-8"`（`agate-md-field-get.py:112`、`agate-changelog-unreleased.py:8`、`agate-read-gate-commands.py:16`、`agate-read-p5-commands.py:18`、`agate-retreat-state.py:28/42/49`、`agate-card-inject.py:13/15/28`、`agate-state-get.py:25`、`agate-state-yaml-check.py:21` 等）→ Windows 读中文 md 崩 UnicodeDecodeError → 被 bash `2>/dev/null || echo ""` 静默吞掉 → gate 误判
- **S2（SEVERE）** `check-p6-evidence.sh:37`：证据引用正则只认 ASCII `[a-zA-Z0-9_/. -]*` → 中文证据文件名（截图.png）P6 gate 假失败
- **M4/M5** `check-gate.sh:356`、`check-p6-format.sh:69`：`[:：]` bracket expression 在 POSIX locale 下匹配不了全角 UTF-8 冒号（v0.40.3 只修了 check-p6-format.sh:84 一处，同类残留）
- **M6** `.gitattributes` 不含 `*.md` + CRLF → Windows checkout 后 md 为 CRLF，`sed -n '/^---$/...'` 取 frontmatter 失效
- **M9** `pre-commit-gate.sh` 等多处路径拼进 `grep -E` 模式，目录含 `[`/`*` 时正则报错被吞 → 静默错判
- 其他：`.agate.env` 尾部 `\r`（agate-workspace-resolve.sh:33）、复制模式 hook AGATE_ROOT 解析（install-hook.sh:31 + pre-commit-gate.sh:26）、`agate-render-dispatch-prompt.sh:112-126` sed 替换串未转义 `&`/`|`

**TQC0001 复盘归入**：
- **Q1** `agate-next-card.sh:56`：`${CARD_FILE#$AGATE_ROOT/}` 前缀匹配在 Windows 盘符/斜杠下失效 → hash mismatch（TQC0001 实测 4 次 gate 重试）
- **Q2** 7 张阶段卡片（P1/P2/P3/P4/P6/P7/P8）残留"先更新 phase=N→N+1 再 commit"（模式 B 旧写法），与 v0.40.1 `git-integration.md` 规则 2（phase=本 commit 产出阶段）矛盾。**修复=卡片补注对齐规则 2，不改 commit 顺序（P2.64 原子性保留）**。注意：改 phase-cards/*.md 触发 SELF-GATE
- **Q5** SETUP.md 增 Windows 章节（AGATE_ROOT Unix 路径、PATH 注入、Git Bash 执行、PYTHONUTF8=1）+ .gitignore 模板预设 `!version.txt` + `dist/`

**roadmap 并入（RM-AG0001/AG0002）**：
- **RM-AG0001** `check-gate.sh` P1 标记反引号包裹识别盲区（`[SUGGEST:` 被反引号包住时行首正则不匹配，typo 兜底也不触发 → 只 WARNING）
- **RM-AG0002** `check-tdd-red.sh` 无 formatter 时（L43）退化 exit-code-only，编译失败误判红灯

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有 676 bats 测试全绿是回归底线，每个修复都必须保持全绿
2. **Windows 兼容是增量**——本环境（Linux）无法实测 Windows，靠静态修复 + Linux 回归 + CI windows-latest matrix 兜底。**不要宣称"已实测 Windows"**
3. **不破坏已有协议语义**——改动是"修正则/加 encoding/路径归一化"，不是重构协议流程

## 4. 关键验证命令

```bash
# 在 worktree 根（/home/kity/oclab/agate/.worktrees/agate-TAG0004）执行：

# 全量测试（必须全绿才算过）
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/

# 一致性（0 ERROR 才行；--strict 让 WARNING 也阻断）
python3 agate/scripts/check-protocol-consistency.py --strict

# shellcheck
shellcheck -S warning agate/scripts/*.sh

# 测试计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh

# 单脚本测试（改哪个跑哪个，TDD 先红后绿）
bats agate/tests/unit/check-gate.bats
bats agate/tests/unit/check-tdd-red.bats
bats agate/tests/unit/check-p6-evidence.bats
bats agate/tests/unit/agate-md-field-get.bats
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出（pre-commit 会用 P2 gate 检查，P2-design.md 不存在 → 拦截）
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿（AGENTS.md「改脚本的工作流」）
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf(TAG0004-P{阶段}):`** 前缀
- **改 `agate/*.md`、`agate/scripts/*.py/.sh`、`agate/phase-cards/*` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0004-env-adaptation/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0004 行
- roadmap：RM-AG0001/0002 关联本任务（scheduled）

## 7. 已知风险与止损

- **改动面大（46 脚本）**：每处修复都可能破坏 Linux 行为 → 全量 bats 兜底，P1 拆 BDD 时按"高风险单独 BDD、低风险批量 BDD"组织
- **S1 最危险**（fail-open 绕过 gate）：改数组后需验证 Linux 下全部 commit 场景
- **13 py 加 encoding 量大**：P1 需定义"所有 open() 必须带 encoding"的 grep 断言审计（防漏）
- **M6 md CRLF 影响面广**：需评估存量历史 review 文件影响，或改用 frontmatter 提取处统一容错（`tr -d '\r'`）
- **无法实测 Windows**：CI 加 windows-latest matrix 是唯一兜底，P8 验收时在 PR 里看 CI 双平台结果

## 8. 完成后

- P8 gate + READY → main 合并（PR 普通 merge 非 squash，tag 要求）
- roadmap 回写 RM-AG0001/0002 → done
- 复盘按 agate 自身变更流程归档

---

> 交接确认：worktree 基线全绿（676 tests + consistency 0 ERROR）、hooks 就位、依赖齐全。可直接开始 P1。
