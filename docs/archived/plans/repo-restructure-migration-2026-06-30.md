# 仓库目录结构重构迁移计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `~/.agate`（既是 git 仓库根又是协议运行时目录）拆成两层：项目资料在仓库根，协议本体在 `agate/` 子目录，`~/.agate` 软链接指向子目录。

**Architecture:** 物理迁移仓库到 `~/oclab/agate/`，git mv 协议文件到 `agate/` 子目录，修复所有脚本/CI/文档中的路径引用，`~/.agate` 改为软链接。协议内部 `{agate_root}` 占位符通过软链接透明解析，无需改动。

**Tech Stack:** bash, git, Python

---

## 前置条件

- 当前会话在 `~/.agate`，所有代码改动已 push
- 新会话将在 `~/oclab/agate` 启动

## 目标结构

```
~/oclab/agate/                    # GitHub 仓库根（项目资料）
├── README.md                     # 项目介绍（改安装说明）
├── LICENSE
├── CHANGELOG.md
├── .github/
├── .gitignore
├── docs/                         # 项目文档
├── archived/                     # 历史验证文档
├── agate/                        # 协议本体（纯净）
│   ├── WORKFLOW.md
│   ├── dispatch-protocol.md
│   ├── state-machine.md
│   ├── role-system.md
│   ├── loop-orchestration.md
│   ├── git-integration.md
│   ├── platform-notes.md
│   ├── orchestrator-template.md
│   ├── LIMITATIONS.md
│   ├── scripts/
│   └── assets/
└── install.sh                    # 安装脚本（新建）

~/.agate → ~/oclab/agate/agate    # 软链接
```

## 路径影响分析

### 不需要改的

| 项目 | 原因 |
|------|------|
| `{agate_root}` 占位符 | 软链接透明，`~/.agate` 仍指向协议本体 |
| 协议文档内交叉引用 | `WORKFLOW.md` 引 `dispatch-protocol.md` 等是同目录引用，不受影响 |
| `install-hook.sh` 的 `REPO_ROOT` | 它在**项目仓库**里运行，不是在 agate 仓库里运行 |
| `pre-commit-gate.sh` 的 `REPO_ROOT` | 同上——它在项目仓库运行，agate 脚本通过 `{agate_root}/scripts/` 找到 |

### 需要改的

| 文件 | 改动 |
|------|------|
| `scripts/check-protocol-consistency.py` | `PROTOCOL_FILES` 加 `agate/` 前缀；`PROTOCOL_DIRS` 改为 `("agate/assets/",)`；`NARRATIVE_DIRS` 改为 `("docs/plans/", "docs/reviews/", "docs/design-notes/", "archived/")`（不变）；root 检测从 `WORKFLOW.md` 改为 `agate/WORKFLOW.md`；`FILE_COUNT_ANCHORS` 的 file 字段加 `agate/` 前缀 |
| `scripts/ci-gate-backstop.py` | `Path("scripts/check-gate.sh")` → `Path("agate/scripts/check-gate.sh")`；`.state.yaml` 位置不变（项目根） |
| `.github/workflows/protocol-consistency.yml` | `python3 scripts/check-protocol-consistency.py` → `python3 agate/scripts/check-protocol-consistency.py` |
| `README.md` | 安装命令改为 clone + ln；文件结构图更新；`agate_root` 说明更新 |
| `docs/plans/pending-repo-restructure.md` | 更新为已完成状态 |
| `WORKFLOW.md` | 文件结构图更新（加 `agate/` 前缀） |
| `orchestrator-template.md` | 文件列表路径加 `agate/` 前缀 |

### 需要新建的

| 文件 | 用途 |
|------|------|
| `install.sh` | 自动化 clone + 软链接安装 |

---

## Task 1: 物理迁移仓库

**Files:**
- Move: `~/.agate/` → `~/oclab/agate/`

- [ ] **Step 1: 创建目标目录并移动仓库**

```bash
mkdir -p ~/oclab
mv ~/.agate ~/oclab/agate
```

验证：`ls ~/oclab/agate/.git` 存在

- [ ] **Step 2: 验证 git 仓库正常**

```bash
cd ~/oclab/agate && git status && git log --oneline -3
```

预期：正常输出，与迁移前一致

- [ ] **Step 3: 在 `~/oclab/agate` 启动 opencode 会话**

后续所有操作在新会话中完成

---

## Task 2: git mv 协议本体到 agate/ 子目录

**Files:**
- Move: `WORKFLOW.md` → `agate/WORKFLOW.md`
- Move: `dispatch-protocol.md` → `agate/dispatch-protocol.md`
- Move: `state-machine.md` → `agate/state-machine.md`
- Move: `role-system.md` → `agate/role-system.md`
- Move: `loop-orchestration.md` → `agate/loop-orchestration.md`
- Move: `git-integration.md` → `agate/git-integration.md`
- Move: `platform-notes.md` → `agate/platform-notes.md`
- Move: `orchestrator-template.md` → `agate/orchestrator-template.md`
- Move: `LIMITATIONS.md` → `agate/LIMITATIONS.md`
- Move: `scripts/` → `agate/scripts/`
- Move: `assets/` → `agate/assets/`

留在仓库根的：`README.md`, `LICENSE`, `CHANGELOG.md`, `.github/`, `.gitignore`, `docs/`, `archived/`

- [ ] **Step 1: 创建 agate 子目录并 git mv**

```bash
cd ~/oclab/agate
mkdir -p agate
git mv WORKFLOW.md agate/
git mv dispatch-protocol.md agate/
git mv state-machine.md agate/
git mv role-system.md agate/
git mv loop-orchestration.md agate/
git mv git-integration.md agate/
git mv platform-notes.md agate/
git mv orchestrator-template.md agate/
git mv LIMITATIONS.md agate/
git mv scripts/ agate/
git mv assets/ agate/
```

- [ ] **Step 2: 验证目录结构**

```bash
ls ~/oclab/agate/agate/
```

预期：`WORKFLOW.md  dispatch-protocol.md  state-machine.md  role-system.md  loop-orchestration.md  git-integration.md  platform-notes.md  orchestrator-template.md  LIMITATIONS.md  scripts/  assets/`

```bash
ls ~/oclab/agate/
```

预期：`README.md  LICENSE  CHANGELOG.md  .github/  .gitignore  docs/  archived/  agate/`

- [ ] **Step 3: 暂不 commit，先修路径引用**

---

## Task 3: 修复 check-protocol-consistency.py 路径

**Files:**
- Modify: `agate/scripts/check-protocol-consistency.py`

- [ ] **Step 1: 修改 PROTOCOL_FILES 集合**

把所有文件名加 `agate/` 前缀：

```python
PROTOCOL_FILES = {
    "agate/WORKFLOW.md",
    "agate/dispatch-protocol.md",
    "agate/state-machine.md",
    "agate/role-system.md",
    "agate/loop-orchestration.md",
    "agate/git-integration.md",
    "agate/platform-notes.md",
    "agate/LIMITATIONS.md",
    "README.md",
    "agate/orchestrator-template.md",
}
```

注意：`README.md` 留在仓库根，不加前缀。

- [ ] **Step 2: 修改 PROTOCOL_DIRS**

```python
PROTOCOL_DIRS = ("agate/assets/",)
```

- [ ] **Step 3: 修改 NARRATIVE_DIRS**

不变——`docs/plans/`, `docs/reviews/`, `docs/design-notes/`, `archived/` 都在仓库根。

- [ ] **Step 4: 修改 root 检测**

```python
if not (root / "agate" / "WORKFLOW.md").exists():
    print(f"ERROR: {root} 看起来不是 agate 仓库根（缺 agate/WORKFLOW.md）", file=sys.stderr)
    return 1
```

- [ ] **Step 5: 修改 FILE_COUNT_ANCHORS**

```python
FILE_COUNT_ANCHORS = [
    {
        "file": "agate/orchestrator-template.md",
        "expected": len(["WORKFLOW", "dispatch-protocol", "state-machine",
                          "role-system", "loop-orchestration", "git-integration",
                          "platform-notes", "LIMITATIONS"]),
        "desc": "启动必读协议文件清单",
    },
    {
        "file": "agate/state-machine.md",
        "expected": 8,
        "desc": "抗中断恢复重读的协议文件清单",
    },
]
```

- [ ] **Step 6: 修改 PATH_IGNORE_SUBSTRINGS**

`docs/tasks/` 等项目侧路径不变。但需要确认 `scripts/` 引用是否需要加 `agate/scripts/`——检查脚本内部引用路径的检查逻辑。

实际上 `PATH_IGNORE_SUBSTRINGS` 是忽略列表，`scripts/` 在旧结构里是协议文件路径，新结构里变成 `agate/scripts/`。协议文件内引用 `scripts/check-gate.sh` 等路径在 `agate/` 子目录下仍然有效（相对路径）。但一致性检查器扫描的是协议文件内容，引用 `scripts/` 而实际路径是 `agate/scripts/`，需要确认检查逻辑。

检查 `check_internal_refs` 函数：它从协议文件内容提取路径引用，然后检查文件是否存在。协议文件在 `agate/` 子目录下，引用 `scripts/check-gate.sh` 相对于 `agate/` 是 `agate/scripts/check-gate.sh`，但检查器用 `root / ref_path` 检查，`root` 是仓库根——所以 `scripts/check-gate.sh` 会找不到，需要改为 `agate/scripts/check-gate.sh`。

**但协议文件内容不应该改**——`{agate_root}/scripts/` 是给 Agent 读的，`agate_root` 解析为 `~/.agate`（软链接），路径是正确的。

所以需要修改检查器逻辑：对协议文件内的引用，先在 `agate/` 子目录下查找，再在仓库根查找。

在 `check_internal_refs` 函数中，路径存在性检查改为：

```python
# 协议文件内的引用可能在 agate/ 子目录下
def ref_exists(root: Path, ref: str) -> bool:
    return (root / ref).exists() or (root / "agate" / ref).exists()
```

- [ ] **Step 7: 运行一致性检查验证**

```bash
cd ~/oclab/agate
python3 agate/scripts/check-protocol-consistency.py
```

预期：0 ERROR（可能有 WARNING，记录下来）

---

## Task 4: 修复 ci-gate-backstop.py 路径

**Files:**
- Modify: `agate/scripts/ci-gate-backstop.py`

- [ ] **Step 1: 修改 check-gate.sh 路径**

```python
script = Path("agate/scripts/check-gate.sh")
```

- [ ] **Step 2: 验证语法**

```bash
python3 -c "import ast; ast.parse(open('agate/scripts/ci-gate-backstop.py').read())"
```

---

## Task 5: 修复 CI workflow 路径

**Files:**
- Modify: `.github/workflows/protocol-consistency.yml`

- [ ] **Step 1: 修改脚本路径**

```yaml
      - name: Run protocol consistency check
        run: python3 agate/scripts/check-protocol-consistency.py

      - name: Run gate backstop check
        run: python3 agate/scripts/ci-gate-backstop.py
```

---

## Task 6: 更新 README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新安装命令**

```markdown
**1. 安装 agate（标准位置 `~/.agate/`）**

```bash
git clone https://github.com/randomgitsrc/agate.git /tmp/agate-repo
ln -s /tmp/agate-repo/agate ~/.agate
```

或使用安装脚本：

```bash
curl -sSL https://raw.githubusercontent.com/randomgitsrc/agate/main/install.sh | bash
```
```

- [ ] **Step 2: 更新文件结构图**

```markdown
```
agate-repo/                      # GitHub 仓库
├── README.md                    # 项目说明（本文件）
├── CHANGELOG.md
├── .github/
├── docs/                        # 项目文档（设计、评审、路线图）
├── agate/                       # 协议本体 ← ~/.agate 指向这里
│   ├── WORKFLOW.md              # P0-P8 核心规则 ← 主入口
│   ├── dispatch-protocol.md
│   ├── state-machine.md
│   ├── loop-orchestration.md
│   ├── git-integration.md
│   ├── role-system.md
│   ├── platform-notes.md
│   ├── orchestrator-template.md # 新项目接入模板 ← 从这里开始
│   ├── LIMITATIONS.md
│   ├── scripts/                 # gate 检查脚本
│   └── assets/                  # 角色定义与模板
└── install.sh

~/.agate → agate-repo/agate      # 软链接
```
```

- [ ] **Step 3: 更新 agate_root 说明**

```markdown
打开 `orchestrator.md`，`agate_root` 已预填为 `~/.agate`（软链接指向协议本体），只需填写 `project_root` 和项目特定约束。
```

---

## Task 7: 更新协议文档内的文件结构图

**Files:**
- Modify: `agate/WORKFLOW.md`
- Modify: `agate/orchestrator-template.md`

- [ ] **Step 1: 更新 WORKFLOW.md 文件结构图**

找到文件结构图部分，给协议文件加 `agate/` 前缀（因为从仓库根视角看它们在子目录）。但注意：**协议文件是给 Agent 读的，Agent 通过 `~/.agate` 软链接访问，看到的是协议本体目录**——所以从 Agent 视角，文件结构不变。

**结论：WORKFLOW.md 和 orchestrator-template.md 内的文件结构图不需要改。** 它们描述的是 `{agate_root}/` 下的结构，软链接透明。

- [ ] **Step 2: 确认不需要改，跳过此 Task**

---

## Task 8: 创建 install.sh

**Files:**
- Create: `install.sh`

- [ ] **Step 1: 编写安装脚本**

```bash
#!/usr/bin/env bash
# install.sh — agate 协议安装脚本
# clone 仓库到临时位置，创建 ~/.agate 软链接指向协议本体

set -euo pipefail

INSTALL_DIR="${AGATE_REPO_DIR:-$HOME/oclab/agate}"
LINK_TARGET="$INSTALL_DIR/agate"
LINK_NAME="$HOME/.agate"

if [ -d "$INSTALL_DIR" ]; then
    echo "仓库已存在: $INSTALL_DIR"
    cd "$INSTALL_DIR" && git pull
else
    echo "克隆仓库到: $INSTALL_DIR"
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone https://github.com/randomgitsrc/agate.git "$INSTALL_DIR"
fi

if [ -L "$LINK_NAME" ]; then
    CURRENT=$(readlink "$LINK_NAME")
    if [ "$CURRENT" = "$LINK_TARGET" ]; then
        echo "软链接已正确: $LINK_NAME -> $LINK_TARGET"
        exit 0
    fi
    echo "更新软链接: $LINK_NAME (原指向 $CURRENT)"
    ln -sfn "$LINK_TARGET" "$LINK_NAME"
elif [ -d "$LINK_NAME" ]; then
    echo "错误: $LINK_NAME 是现有目录（非软链接），请手动处理" >&2
    echo "建议: mv $LINK_NAME ${LINK_NAME}.bak && ln -s $LINK_TARGET $LINK_NAME" >&2
    exit 1
else
    ln -s "$LINK_TARGET" "$LINK_NAME"
    echo "创建软链接: $LINK_NAME -> $LINK_TARGET"
fi

echo "安装完成。agate_root = $LINK_NAME -> $LINK_TARGET"
```

- [ ] **Step 2: 设可执行位**

```bash
chmod +x install.sh
```

---

## Task 9: 创建软链接

**Files:**
- Create: `~/.agate` (symlink)

- [ ] **Step 1: 创建软链接**

```bash
ln -sfn ~/oclab/agate/agate ~/.agate
```

- [ ] **Step 2: 验证软链接**

```bash
ls -la ~/.agate
cat ~/.agate/WORKFLOW.md | head -5
```

预期：软链接指向 `~/oclab/agate/agate`，WORKFLOW.md 可读

---

## Task 10: 运行一致性检查 + commit

**Files:**
- Modify: `docs/plans/pending-repo-restructure.md`

- [ ] **Step 1: 运行一致性检查**

```bash
cd ~/oclab/agate
python3 agate/scripts/check-protocol-consistency.py
```

预期：0 ERROR。如果有 ERROR，修复后重跑。

- [ ] **Step 2: 运行 CI backstop**

```bash
cd ~/oclab/agate
python3 agate/scripts/ci-gate-backstop.py
```

预期：SKIP（非 agate 项目仓库，无 .state.yaml）

- [ ] **Step 3: commit 所有改动**

```bash
cd ~/oclab/agate
git add -A
git commit -m "refactor: 仓库目录结构重构 — 协议本体移至 agate/ 子目录

- git mv 协议文件到 agate/ 子目录（WORKFLOW.md, scripts/, assets/ 等）
- 项目资料（docs/, .github/, CHANGELOG.md）留在仓库根
- check-protocol-consistency.py: PROTOCOL_FILES/DIRS 加 agate/ 前缀，ref_exists 兼容子目录
- ci-gate-backstop.py: check-gate.sh 路径加 agate/ 前缀
- CI workflow: 脚本路径加 agate/ 前缀
- README.md: 安装命令改为 clone + ln，文件结构图更新
- 新增 install.sh 安装脚本
- ~/.agate 改为软链接 → ~/oclab/agate/agate"
```

- [ ] **Step 4: push**

```bash
git push
```

- [ ] **Step 5: 更新 pending-repo-restructure.md 为已完成**

---

## Task 11: 验证端到端

- [ ] **Step 1: 验证软链接路径解析**

```bash
cat ~/.agate/WORKFLOW.md | head -3
ls ~/.agate/scripts/
ls ~/.agate/assets/
```

预期：全部可访问

- [ ] **Step 2: 验证 CI 触发**

push 后检查 GitHub Actions 是否正常运行。

- [ ] **Step 3: 验证 install-hook.sh 在项目仓库中仍可用**

在一个使用 agate 的项目（如 PeekView）中运行：

```bash
bash ~/.agate/scripts/install-hook.sh
```

预期：正常安装 pre-commit hook（REPO_ROOT 解析为项目仓库根，SOURCE 指向 `~/.agate/scripts/pre-commit-gate.sh`，软链接透明）

---

## 风险与回退

| 风险 | 缓解 |
|------|------|
| 软链接在某些工具中不透明 | `readlink -f` 可获取真实路径；git 跟随软链接 |
| install-hook.sh 的 SOURCE 路径 | `REPO_ROOT/scripts/` → 实际是项目仓库的 scripts/，不是 agate 的。需要确认 install-hook.sh 是在 agate 仓库内运行还是项目仓库内运行 |
| check-protocol-consistency.py 内部引用检查 | 协议文件内 `scripts/` 引用需兼容 `agate/scripts/` 实际路径 |
| 已有项目引用 `~/.agate/` | 软链接透明，无需改动 |

### install-hook.sh 特殊说明

`install-hook.sh` 当前逻辑：
- `REPO_ROOT = git rev-parse --show-toplevel` → 在 agate 仓库内运行时 = `~/oclab/agate`
- `SOURCE = $REPO_ROOT/scripts/pre-commit-gate.sh` → `~/oclab/agate/scripts/` → 迁移后变成 `~/oclab/agate/agate/scripts/`

**但 install-hook.sh 的设计意图是在项目仓库里运行**，不是在 agate 仓库里运行。项目仓库的 `.git/hooks/pre-commit` 需要指向 agate 的 `pre-commit-gate.sh`。

当前设计有歧义：install-hook.sh 假设 agate 仓库就是项目仓库（`~/.agate` 时代两者合一）。重构后需要明确：

**方案 A**：install-hook.sh 只在 agate 仓库内运行（自测用），项目仓库用 install.sh 安装后手动配置 hook
**方案 B**：install-hook.sh 接受参数指定 agate 路径，在项目仓库内运行

建议用方案 B，修改 install-hook.sh：

```bash
#!/usr/bin/env bash
set -euo pipefail

AGATE_ROOT="${1:-$HOME/.agate}"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || { echo "不在 git 仓库中" >&2; exit 1; })
HOOK_DIR="$REPO_ROOT/.git/hooks"
HOOK_FILE="$HOOK_DIR/pre-commit"
SOURCE="$AGATE_ROOT/scripts/pre-commit-gate.sh"

[ ! -f "$SOURCE" ] && { echo "错误: $SOURCE 不存在" >&2; exit 1; }

mkdir -p "$HOOK_DIR"

if [ -f "$HOOK_FILE" ] && [ ! -L "$HOOK_FILE" ]; then
    cp "$HOOK_FILE" "$HOOK_FILE.bak.$(date +%s)"
    echo "已备份现有 pre-commit hook"
fi

ln -sf "$SOURCE" "$HOOK_FILE"
chmod +x "$SOURCE"

echo "pre-commit hook 已安装: $HOOK_FILE -> $SOURCE"
```

这样在项目仓库里运行 `bash ~/.agate/scripts/install-hook.sh` 即可，`AGATE_ROOT` 默认 `~/.agate`（软链接透明）。
