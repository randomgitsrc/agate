# Plan：非功能性清理--orchestrator-template 去变量 + worktree 文档 + agate-core 改名

> 日期：2026-07-23
> 版本影响：minor bump（v0.18.0 已合并，本 plan 暂定 v0.19.0）
> 破坏性变更：**有**（第三部分目录改名，需用户重新运行 install.sh 或手动更新软链接）
> 来源：(1) orchestrator-template.md frontmatter 变量分析与讨论 (2) worktree 适配讨论 (3) `agate/agate/` 目录命名讨论

---

## 诚实标注

第一部分（frontmatter 去变量）经过实际脚本源码核实，确认 frontmatter 变量不被任何脚本读取--纯 LLM 占位符。第二部分（worktree 文档）是讨论后的结论记录，不涉及代码变更。第三部分（目录改名）的影响面经两轮独立评审修正--初版只搜了 `agate/agate` 双叠词，漏掉了所有 `agate/` 路径前缀的硬编码引用；修正后用 `grep -rln 'agate/'` 全量扫描，确认 7 个功能性脚本 + 5 个测试文件 + CI workflow + ~12 个文档文件受影响。

第三部分的策略经过讨论后确定：**能用 `$AGATE_ROOT` 软链接的地方改用软链接（永久免疫目录改名），必须匹配 git 仓库相对路径的地方做一次性 sed 替换**。不做动态目录名推导（过度工程，agate 不太可能频繁改目录名）。

---

## 第一部分：orchestrator-template.md 去 frontmatter 变量

### 问题

`orchestrator-template.md` 的 frontmatter 有两个变量：

```yaml
agate_root: ~/.agate
project_root: /absolute/path/to/your-project
```

模板正文用 `{agate_root}` 和 `{project_root}` 作为占位符。问题：

1. **`agate_root: ~/.agate` 不是变量**--对所有用户都是同一个值（`~/.agate` 软链接），放在 frontmatter 里让人以为需要"配置"，实际上不需要
2. **`project_root: /absolute/path/to/your-project` 是真正的变量**--用户要填，填了不能提交（否则其他人拿到错误路径），不填又不能用
3. **没有任何脚本读这个 frontmatter**--所有脚本用 `AGATE_ROOT` 环境变量（默认 `$HOME/.agate`），Agent 自己知道工作目录在哪

### 根因

模板设计初期把 `agate_root` 和 `project_root` 当作"配置项"放 frontmatter，但实际上：
- `agate_root` 对所有用户恒等于 `~/.agate`（或 `$AGATE_ROOT` 环境变量覆盖）
- `project_root` 就是 Agent 的工作目录（`pwd` / `git rev-parse --show-toplevel`），Agent 运行时自然知道

### 方案

**去掉 frontmatter 的两个变量，模板正文直接用 `~/.agate` 和相对路径：**

```diff
 ---
-# ── agate 配置 ──────────────────────────────────────────────
-agate_root: ~/.agate
-project_root: /absolute/path/to/your-project
-
-# ── 平台配置（按需取消注释）──────────────────────────────────
+# ── 平台配置（按需取消注释）──────────────────────────────────
 ...
 ---

-| 启动 | `{agate_root}/phase-cards/P0-orchestrator.md` |
+| 启动 | `~/.agate/phase-cards/P0-orchestrator.md` |

-2. `mkdir -p {project_root}/docs/tasks/`
+2. `mkdir -p docs/tasks/`

-1. `{agate_root}/WORKFLOW.md` - 阶段总览、角色映射、裁剪规则
+1. `~/.agate/WORKFLOW.md` - 阶段总览、角色映射、裁剪规则
```

模板正文中所有 `{agate_root}` 替换为 `~/.agate`，所有 `{project_root}/` 替换为空（用相对路径）。`{项目名}` 和 `{项目特有文件}` 保留--这些是用户拷贝后需要填的，与 agate 配置无关。

### 同时更新 README.md

`README.md:77` 写着"agate_root 已预填为 ~/.agate...只需填写 project_root"--改为"模板拷贝后可直接使用，无需填写路径配置"。`README.md:92` 附近"复制后改 project_root: 等几行字段"也需同步更新。

### 测试

无新增脚本测试。验证项：
- `check-protocol-consistency.py` 仍 0 ERROR
- 模板中不再出现 `{agate_root}` 或 `{project_root}` 字面量（grep 验证）
- `{项目名}` 占位符保留（这是用户需要填的）

---

## 第二部分：worktree 文档补充（纯文档，不改脚本）

### 背景

讨论结论：agate 已经是 worktree-safe 的（git 操作用相对路径、`.state.yaml` 天然隔离、hook 共享 `.git/hooks/`）。superpowers 的 `using-git-worktrees` skill 管创建 worktree + 项目适配，agate 只需在 worktree 里正常运行。

### 方案

在 `agate/platform-notes.md` 末尾新增一节：

```markdown
## Git Worktree

agate 在 git worktree 下无需特殊配置即可工作：

- `.state.yaml` 和 `docs/tasks/` 是分支级文件，每个 worktree 有自己的 checkout，天然隔离
- pre-commit / commit-msg / pre-push hook 共享 `.git/hooks/`，worktree 里正常触发
- `AGATE_ROOT`（`~/.agate` 软链接）是全局的，与 worktree 无关

**与 superpowers 的关系**：`using-git-worktrees` skill 负责 worktree 创建 + 项目基础设施适配（dev server 端口、数据库隔离等）。agate 不管理 worktree 生命周期，只在 worktree 内正常运行。项目层面的 worktree 适配（端口/DB/env）由项目自身负责，与 agate 无关。

**已知限制**：`install-hook.sh` 从 worktree 内运行时会失败（worktree 的 `.git` 是文件而非目录，`mkdir -p "$REPO_ROOT/.git/hooks"` 报错）。hook **触发**仍正常（git 使用共享 hooks 目录），但**安装**需在主工作树运行。
```

### 测试

无。纯文档补充。

---

## 第三部分：`agate/` -> `agate-core/` 目录改名

### 问题

仓库根叫 `agate/`，里面有个子目录也叫 `agate/`，形成 `agate/agate/` 嵌套。说"agate 目录"时歧义：指仓库还是协议本体？

### 策略：两层区分处理

讨论后的关键洞察：`agate/` 路径引用分两层--

1. **软链接层**：脚本通过 `$AGATE_ROOT`（默认 `~/.agate`）访问协议文件。这一层**天然免疫目录改名**--软链接解析到哪就是哪，不关心实际目录名。
2. **git 路径层**：脚本通过 `agate/` 前缀匹配 git 输出（`git diff --name-only`、git pathspec）。这一层**不走软链接**，必须用仓库相对路径，改名就断。

**策略**：
- 能走软链接的（读协议文件的脚本）：改用 `$AGATE_ROOT`，永久免疫
- 必须匹配 git 路径的：一次性 sed 替换
- 不做动态目录名推导（过度工程，agate 不太可能频繁改目录名）

### 哪些改用 `$AGATE_ROOT`（永久免疫）

| 脚本 | 现状 | 改法 |
|------|------|------|
| `agate-next-card.sh:49` | `$AGATE_REPO/agate/phase-cards/...` | `AGATE_ROOT="$(dirname "$SCRIPT_DIR")"`（脚本自身位置反推，保留仓库相对路径给 `REL_CARD` 计算），然后 `$AGATE_ROOT/phase-cards/...` |
| `ci-gate-backstop.py:18,151` | `Path("agate/scripts/...")` | `Path(__file__).resolve().parent / "check-gate.sh"`（同级查找，CI 无 `~/.agate` 软链接也能工作）|

这两个脚本读的是协议文件（phase-cards、check-gate.sh）。`agate-next-card.sh` 用脚本自身位置反推（`dirname $SCRIPT_DIR`）而非 `~/.agate` 软链接，因为它的 `REL_CARD` 计算需要仓库相对路径（`#${AGATE_REPO}/` 前缀剥离），直接用 `~/.agate` 会破坏这个逻辑。`ci-gate-backstop.py` 用 `__file__` 同级查找，因为 CI 环境没有 `~/.agate` 软链接。

改完后这两个脚本**永久不受目录改名影响**。

### 哪些做 sed 替换（一次性成本）

这些脚本匹配的是 git 仓库相对路径，不能用软链接替代：

| 文件 | 引用数 | 具体内容 | break 后果 |
|------|--------|---------|-----------|
| `.github/workflows/protocol-tests.yml` | 7 | `bats agate/tests/...`、`shellcheck agate/scripts/*.sh`、`python3 agate/scripts/...` | **CI 全部失败** |
| `check-protocol-consistency.py` | ~69 | `PROTOCOL_FILES`、`PROTOCOL_DIRS`、`SCRIPT_ALIGNMENT_ANCHORS` 等路径列表 | **一致性检查全部失败** |
| `commit-msg-self-gate.sh:13` | 3 | regex `^(agate/scripts/.*\.(sh\|py)\|agate/[^/]+\.md\|agate/.+/.*\.md\|SELF-GATE\.md)$` | **self-gate 不再触发** |
| `agate-changes.sh:123-138` | ~13 | `grep -E "^agate/WORKFLOW\.md$\|^agate/scripts/..."` | **变更分类全部失效** |
| `install-hook.sh:62-67` | 3 | `git diff ... -- 'agate/*.md'`（pre-push hook 内嵌 heredoc） | **pre-push 改动量检测失效** |

### 测试文件中的硬编码路径（必须同步改）

| 测试文件 | 引用数 | break 后果 |
|---------|--------|-----------|
| `tests/unit/commit-msg-self-gate.bats` | 7 | 脚本 regex 改了但测试 fixture 用旧路径 -> 不匹配 -> 测试失败 |
| `tests/unit/agate-next-card.bats` | 9 | 文件移到 `agate-core/` -> sha256sum 失败 |
| `tests/integration/pre-push-hook.bats` | 6 | pathspec 改了但测试用旧路径 -> diff 返回 0 -> 断言失败 |
| `tests/integration/consistency.bats` | 4 | 文件移到 `agate-core/scripts/` -> grep 失败 |
| `tests/integration/commit-msg-self-gate.bats` | 8 | 同 unit 测试 |

**5 个测试文件、34 处硬编码路径**必须同步更新。

### 文档引用（应改，不 break 功能）

| 文件 | 引用数 | 类型 |
|------|--------|------|
| `SELF-GATE.md` | ~12 | 触发条件路径 + 派发模板路径 |
| `AGENTS.md`（仓库根） | ~10 | 目录结构说明 + 路径引用 |
| `README.md` | ~5 | 安装指引 + 目录结构说明 |
| `install.sh` | 1 | `LINK_TARGET="$INSTALL_DIR/agate"` |
| `agate/AGENTS.md` | ~5 | `{agate_root}` 占位符说明 |
| `agate/scripts/README.md` | ~3 | 脚本路径引用 |
| `agate/tests/README.md` | ~2 | 测试路径引用 |
| `agate/WORKFLOW.md` | ~2 | 路径引用 |
| `agate/dispatch-protocol.md` | ~2 | 路径引用 |
| `agate/rules/*.md` | ~2 | 路径引用 |

`{agate_root}` 占位符是文档约定（指向 `~/.agate` 软链接），不受目录名影响。这些文件**可选更新**，优先级低于功能性硬编码。

### 不需要改的文件

- `docs/archived/` 下历史文档--archived 不维护
- `docs/reviews/` 下历史评审--同上
- `docs/plans/` 下历史 plan--同上
- `tests/helpers/load.bash`--`_resolve_agate_root` 通过目录特征（`scripts/` + `assets/`）反推，不依赖目录名
- `count-tests.sh`--相对自身路径，不依赖目录名

### 总结

| 类型 | 文件数 | 策略 |
|------|--------|------|
| 改用 `$AGATE_ROOT`（永久免疫） | 2 | 替换为软链接路径 |
| sed 替换（功能性硬编码） | 5 + CI | `agate/` -> `agate-core/` |
| sed 替换（测试断言） | 5 | 同上 |
| 文档更新（应改） | ~10 | 同上（优先级低） |
| **总计** | ~22 | |

### 实施步骤

```bash
# 1. 改名
git mv agate agate-core

# 2. 立即修复软链接（否则 hook 断裂）
ln -sfn "$(pwd)/agate-core" ~/.agate

# 3. 改用脚本自身位置的 2 个脚本（永久免疫）
# agate-next-card.sh: AGATE_ROOT="$(dirname "$SCRIPT_DIR")"，然后 $AGATE_ROOT/phase-cards/...
# ci-gate-backstop.py: Path(__file__).resolve().parent / "check-gate.sh"（同级查找，CI 无 ~/.agate 也能工作）

# 4. sed 替换功能性硬编码（两遍 sed：先替换 "agate" 字符串字面量，再替换 agate/ 路径前缀）
#    check-protocol-consistency.py 有 6 处 root / "agate" / ...（Python 字符串，无尾斜杠），
#    单遍 sed 's|agate/|agate-core/|g' 会漏掉这些，导致 main() 入口检查永远失败
sed -i 's|"agate"|"agate-core"|g; s|agate/|agate-core/|g' \
    agate-core/scripts/check-protocol-consistency.py

#    其余文件只有 agate/ 路径前缀，单遍 sed 即可
sed -i 's|agate/|agate-core/|g' \
    .github/workflows/protocol-tests.yml \
    agate-core/scripts/commit-msg-self-gate.sh \
    agate-core/scripts/agate-changes.sh \
    agate-core/scripts/install-hook.sh

# 5. sed 替换测试断言
sed -i 's|agate/|agate-core/|g' \
    agate-core/tests/unit/commit-msg-self-gate.bats \
    agate-core/tests/unit/agate-next-card.bats \
    agate-core/tests/integration/pre-push-hook.bats \
    agate-core/tests/integration/consistency.bats \
    agate-core/tests/integration/commit-msg-self-gate.bats

# 6. 手动更新文档引用（install.sh, README.md, SELF-GATE.md, AGENTS.md）
# 7. 更新 install.sh: LINK_TARGET="$INSTALL_DIR/agate" -> "$INSTALL_DIR/agate-core"
```

⚠️ **sed 注意事项**：
- `install-hook.sh` 和 `agate-changes.sh` 含 `~/.agate/scripts/...` 注释，单遍 `sed 's|agate/|agate-core/|g'` 会误改为 `~/.agate-core/scripts/...`。需手动检查 sed 结果，恢复被误改的 `~/.agate/` 注释。
- `check-protocol-consistency.py` 必须用两遍 sed（`"agate"` 字符串字面量 + `agate/` 路径前缀），否则 6 处 `root / "agate" / ...` 会被漏掉，`main()` 入口检查永远失败。

### 用户迁移

现有用户需：

1. `git pull`（获取改名后的代码）
2. 重新运行 `install.sh` 或手动更新软链接：`ln -sfn ~/oclab/agate/agate-core ~/.agate`
3. **重跑 `install-hook.sh`**（pre-push hook 是内嵌复制不是软链接，需重装以更新 pathspec）

CHANGELOG 需显著标注此 breaking change。

### 测试

- 全量 bats 测试通过（`load.bash` 不依赖目录名，但测试断言含硬编码路径需同步更新）
- `check-protocol-consistency.py` 0 ERROR
- `shellcheck -S warning agate-core/scripts/*.sh` clean
- `count-tests.sh` 计数不变
- CI workflow 路径更新后全部 pass

---

## 第四部分：文档传播清单

| 文件 | 改动类型 | 涉及部分 |
|------|---------|---------|
| `agate-core/orchestrator-template.md` | 去 frontmatter 变量 + 正文占位符替换 | 第一部分 |
| `README.md` | 安装指引路径更新 + 去变量说明更新 | 第一、三部分 |
| `install.sh` | `LINK_TARGET` 路径更新 | 第三部分 |
| `AGENTS.md`（仓库根） | 目录结构说明 + 路径引用更新 | 第三部分 |
| `SELF-GATE.md` | 触发条件路径 + 派发模板路径更新 | 第三部分 |
| `.github/workflows/protocol-tests.yml` | CI 路径更新（7 处） | 第三部分 |
| `agate-core/scripts/check-protocol-consistency.py` | 路径扫描更新（~69 处） | 第三部分 |
| `agate-core/scripts/commit-msg-self-gate.sh` | regex 路径更新（3 处） | 第三部分 |
| `agate-core/scripts/agate-next-card.sh` | 改用 `$AGATE_ROOT`（永久免疫） | 第三部分 |
| `agate-core/scripts/agate-changes.sh` | grep pattern 路径更新（~13 处） | 第三部分 |
| `agate-core/scripts/install-hook.sh` | pre-push pathspec 更新（3 处） | 第三部分 |
| `agate-core/scripts/ci-gate-backstop.py` | 改用 `$AGATE_ROOT`（永久免疫） | 第三部分 |
| `agate-core/platform-notes.md` | 新增 worktree 节 | 第二部分 |
| `agate-core/tests/unit/commit-msg-self-gate.bats` | 路径更新（7 处） | 第三部分 |
| `agate-core/tests/unit/agate-next-card.bats` | 路径更新（9 处） | 第三部分 |
| `agate-core/tests/integration/pre-push-hook.bats` | 路径更新（6 处） | 第三部分 |
| `agate-core/tests/integration/consistency.bats` | 路径更新（4 处） | 第三部分 |
| `agate-core/tests/integration/commit-msg-self-gate.bats` | 路径更新（8 处） | 第三部分 |
| `CHANGELOG.md` | v0.19.0 条目 | 全部 |

---

## 第五部分：版本与 CHANGELOG

```markdown
## [0.19.0] - 2026-07-23

### 破坏性变更
- **目录改名**：`agate/` 子目录改名为 `agate-core/`，消除 `agate/agate/` 嵌套歧义。
  现有用户需：
  1. `git pull`
  2. 重新运行 `install.sh` 或手动更新软链接：`ln -sfn ~/oclab/agate/agate-core ~/.agate`
  3. 重跑 `bash ~/.agate/scripts/install-hook.sh`（更新 pre-push hook 中的 pathspec）
- 同步更新 5 个功能性硬编码脚本（check-protocol-consistency.py、commit-msg-self-gate.sh、
  agate-changes.sh、install-hook.sh、CI workflow）和 5 个测试文件中的 `agate/` 路径前缀

### 优化
- agate-next-card.sh、ci-gate-backstop.py 改用 `$AGATE_ROOT` 软链接访问协议文件，
  永久免疫目录改名（不再依赖仓库内目录名）

### 变更
- orchestrator-template.md 去掉 frontmatter 的 `agate_root` / `project_root` 变量，
  模板正文直接用 `~/.agate` 和相对路径。拷贝后可直接使用，无需填写路径配置
- platform-notes.md 新增 Git Worktree 适配说明（含 install-hook.sh 限制）
```

---

## 第六部分：实施顺序

1. 第三部分先做（目录改名 + 脚本适配）--后续文件路径都基于新目录名
   - `git mv agate agate-core`
   - `ln -sfn "$(pwd)/agate-core" ~/.agate`（立即修复软链接）
   - 改 2 个脚本用 `$AGATE_ROOT`（永久免疫）
   - sed 替换 5 个功能性脚本 + CI workflow
   - sed 替换 5 个测试文件
   - 手动更新 install.sh、README.md、SELF-GATE.md、AGENTS.md
2. 第一部分（orchestrator-template 去变量）
3. 第二部分（worktree 文档补充）
4. 跑全量测试：
   ```bash
   bats agate-core/tests/sanity.bats agate-core/tests/unit/ agate-core/tests/regression/ agate-core/tests/integration/
   python3 agate-core/scripts/check-protocol-consistency.py
   bash agate-core/tests/scripts/count-tests.sh
   shellcheck -S warning agate-core/scripts/*.sh
   ```
5. 更新 CHANGELOG
6. self-gate：派发 protocol-alignment-review

---

## 第七部分：与已有 plan 的关系

| 已有 plan/评审 | 关系 |
|---------|-----------|
| `agate-p6-gate-friction-fixes-20260723-v2.md` | 已合并（PR #41，v0.18.0）。独立、不冲突 |
| `agate-binary-marker-declaration-20260722.md` | 已合并（PR #39，v0.17.0）。独立、不冲突 |
