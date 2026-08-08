# Windows（Git for Windows bash）支持加固 + 安装指引 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 agate 能在 Windows 原生（Git for Windows 自带 MSYS2 bash，不用 WSL）运行，提供安装配置指引 + 少量防御性加固，前提是不对 Linux/macOS 既有行为产生负面作用。

**Architecture:** 经调研，Git for Windows 自带的 MSYS2 bash 已提供 `grep/sed/find/stat -c%s/sha256sum/md5sum/od/readlink -f/printf/mktemp` 等全套 GNU coreutils，且支持进程替换 `< <()`、`[[ ]]`、`BASH_SOURCE` 等 bashism--**agate 的 25 个 .sh 大部分能直接跑**。真正需要加固的是：（1）`install-hook.sh` 的 `ln -sf` 在 Windows 无符号链接权限时退化为复制（升级后不自动跟随）--加检测+提醒；（2）git `autocrlf` 导致 .py/.sh 文件 CRLF 污染--加 `.gitattributes` 强制 LF；（3）缺安装指引。所有改动都是**防御性**的：Linux/macOS 上行为不变（已有 `|| fallback` 双分支或新增的 `if` 守卫），Windows 上增加兼容。

**Tech Stack:** bash + git + `.gitattributes` + Markdown 文档。

**背景调研（已确认）：**
- **MSYS2 bash 能力**：`stat -c%s`（check-p6-evidence.sh:93 已有 `-c%s || -f%z` 双 fallback）、`readlink -f`（6 处已有 `|| echo` fallback）、`find -print0/-exec/-maxdepth`、`sha256sum`、`md5sum`、`od -A n -t x1`、`mktemp`、`date -u`、`head -c` 均被 MSYS2 coreutils 支持 ✓
- **bashism**：进程替换 `< <()`（check-p6-provenance:6 处、check-p6-evidence:2 处、pre-commit-gate:2 处）--MSYS2 bash 原生支持 ✓
- **`ln -sf` 退化**：MSYS2 `ln -s` 在无 Windows 符号链接权限（未开开发者模式/非管理员）时**退化为复制**。install-hook.sh:31/45/64 三处 `ln -sf` 会变成复制 hook 文件 -> 升级 agate 后 hook 不自动更新（需重跑 install-hook.sh）。非崩溃，但需文档提醒 + 安装时检测告警。
- **CRLF 风险**：git `core.autocrlf=true`（Windows 默认）会在 checkout 时把 .sh/.py 的 LF 转 CRLF -> bash 执行 `.sh` 报 `\r` 语法错、python `.py` hash 不匹配。需 `.gitattributes` 强制 `* text=auto eol=lf` + `.sh/.py/.bats` 显式 `eol=lf`。
- **CI**：`protocol-tests.yml` 4 job 全 `runs-on: ubuntu-latest`--Windows 行为无 CI 兜底，靠本地验证 + 文档指引。
- **bats**：Windows 上 bats 安装需 Git for Windows bash + 手动 clone bats 仓库（无 apt）。文档化即可。

---

## File Structure

- **Create** `.gitattributes`（仓库根）- 强制 LF，防 CRLF 污染 .sh/.py/.bats。
- **Modify** `agate/scripts/install-hook.sh` - `ln -sf` 后检测是否真符号链接，退化（复制）时打印升级提醒。
- **Modify** `agate/platform-notes.md` - 新增「Windows 原生（Git for Windows）」章节（安装指引 + 已知限制 + 验证步骤）。
- **Modify** `agate/scripts/README.md` - 依赖节补 Windows 提示。
- **Test** `agate/tests/unit/install-hook.bats` - 新增「ln 退化检测」用例（mock 无符号链接权限场景）。

---

### Task 1: TDD - 写 install-hook 退化检测失败测试（真红）

**Files:**
- Test: `agate/tests/unit/install-hook.bats`

**背景**：install-hook.sh 的 `ln -sf` 在 Windows 无符号链接权限时退化为复制。当前无检测--用户不知道 hook 不会随 agate 升级自动更新。先写失败测试：模拟「ln -sf 后 HOOK_FILE 不是符号链接」场景，断言安装输出含升级提醒。

- [ ] **Step 1: 写失败测试**

在 `agate/tests/unit/install-hook.bats` 末尾追加：

```bash
@test "install-hook: ln 退化为复制时打印升级提醒（Windows 兼容）" {
    local repo
    repo=$(git_init)
    local agate_root
    agate_root="$BATS_TEST_TMPDIR/agate-fake"
    mkdir -p "$agate_root/scripts"
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$agate_root/scripts/"
    cp "$AGATE_ROOT/scripts/commit-msg-self-gate.sh" "$agate_root/scripts/"
    cp "$AGATE_ROOT/scripts/pre-push-gate.sh" "$agate_root/scripts/"

    # mock ln：让它退化为 cp（模拟 Windows 无符号链接权限）
    # 用 PATH 注入一个假的 ln，把 -sf 当 cp 处理
    local fakebin
    fakebin="$BATS_TEST_TMPDIR/fakebin"
    mkdir -p "$fakebin"
    cat > "$fakebin/ln" <<'LNEOF'
#!/usr/bin/env bash
# 模拟 MSYS2 无符号链接权限：ln -sf 退化为复制
cp -f "$2" "$3"
LNEOF
    chmod +x "$fakebin/ln"

    run bash -c "cd '$repo' && PATH='$fakebin:$PATH' bash '$AGATE_ROOT/scripts/install-hook.sh' '$agate_root'" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" == *"复制"* || "$output" == *"需重跑"* ]]
}
```

> **红/绿说明**：当前 install-hook.sh 的 `ln -sf` 后无退化检测 -> 不打印「复制/升级提醒」-> 测试 FAIL（红）。Task 2 加检测后 -> PASS（绿）。真红真绿可区分。

- [ ] **Step 2: 运行测试确认当前失败（红）**

```bash
bats agate/tests/unit/install-hook.bats --filter '退化'
```

Expected: FAIL（输出不含「复制/升级提醒」）。

---

### Task 2: install-hook.sh 加 ln 退化检测（绿）

**Files:**
- Modify: `agate/scripts/install-hook.sh:31,45,64`

**背景**：每处 `ln -sf` 后加一行检测：若目标不是符号链接（`[ ! -L "$HOOK_FILE" ]`），说明退化为复制，打印升级提醒。Linux/macOS 上 `ln -sf` 成功创建符号链接 -> `[ -L ]` 为真 -> 不打印 -> **行为不变**。

- [ ] **Step 1: 替换三处 `ln -sf` 后加检测**

把 install-hook.sh:31：
```bash
ln -sf "$SOURCE" "$HOOK_FILE"
chmod +x "$SOURCE"

echo "pre-commit hook 已安装: $HOOK_FILE -> $SOURCE"
```
改为：
```bash
ln -sf "$SOURCE" "$HOOK_FILE"
chmod +x "$SOURCE"

if [ -L "$HOOK_FILE" ]; then
    echo "pre-commit hook 已安装: $HOOK_FILE -> $SOURCE"
else
    echo "pre-commit hook 已安装（复制模式，Windows 无符号链接权限）: $HOOK_FILE"
    echo "  ⚠️  升级 agate 后需重跑 install-hook.sh（复制不自动跟随源文件）"
fi
```

同理改 install-hook.sh:45（commit-msg）：
```bash
    ln -sf "$COMMIT_MSG_SOURCE" "$COMMIT_MSG_HOOK"
    chmod +x "$COMMIT_MSG_SOURCE"
    if [ -L "$COMMIT_MSG_HOOK" ]; then
        echo "commit-msg hook 已安装: $COMMIT_MSG_HOOK -> $COMMIT_MSG_SOURCE"
    else
        echo "commit-msg hook 已安装（复制模式）: $COMMIT_MSG_HOOK"
    fi
```

同理改 install-hook.sh:64（pre-push）：
```bash
ln -sf "$PRE_PUSH_SOURCE" "$PRE_PUSH_HOOK"
chmod +x "$PRE_PUSH_SOURCE"
if [ -L "$PRE_PUSH_HOOK" ]; then
    echo "pre-push hook 已安装: $PRE_PUSH_HOOK -> $PRE_PUSH_SOURCE (协议文件大改动自动提示)"
else
    echo "pre-push hook 已安装（复制模式）: $PRE_PUSH_HOOK"
fi
```

> **等价性**：Linux/macOS 上 `ln -sf` 成功 -> `[ -L ]` 真 -> 走原 `echo` 分支，输出与原来**逐字一致**（除 commit-msg/pre-push 也加 if 但原输出文本不变）。Windows 退化 -> `[ -L ]` 假 -> 打印复制模式提醒。**对既有 Linux/macOS 行为零负面作用**。

- [ ] **Step 2: 运行测试确认通过（绿）**

```bash
bats agate/tests/unit/install-hook.bats
```

Expected: 全部 PASS（含新退化检测用例 + 既有 4 个 install-hook 用例）。

- [ ] **Step 3: 确认既有 install-hook 测试不受影响**

```bash
bats agate/tests/unit/install-hook.bats --filter 'install-hook:'
```

Expected: 既有 4 个用例全 PASS（输出文本不变，因 Linux 上走 `[ -L ]` 真分支）。

---

### Task 3: 新增 `.gitattributes` 强制 LF（防 CRLF 污染）

**Files:**
- Create: `.gitattributes`（仓库根）

**背景**：Windows git 默认 `core.autocrlf=true`，checkout 时把 .sh/.py/.bats 的 LF 转 CRLF -> bash 执行 .sh 报 `\r` 语法错、python hash 不匹配。`.gitattributes` 强制这些文件 LF，**对 Linux/macOS 无影响**（本来就用 LF）。

- [ ] **Step 1: 创建 `.gitattributes`**

```gitattributes
# 强制 LF：bash 脚本 / python / bats 测试对 CRLF 敏感
# Windows git 默认 autocrlf=true 会在 checkout 时转 CRLF -> .sh 报 \r 语法错
# 本文件对 Linux/macOS 无影响（它们本来就用 LF）
*.sh        text eol=lf
*.py        text eol=lf
*.bats      text eol=lf
*.bash      text eol=lf
*.md        text eol=lf
*.yaml      text eol=lf
*.yml       text eol=lf
*.jsonl     text eol=lf
*.gitattributes text eol=lf
*.gitignore     text eol=lf
```

> **注意**：`text eol=lf` 表示这些文件始终用 LF 存储+checkout，不受 `core.autocrlf` 影响。对 Linux/macOS 用户**无任何行为变化**（git 本来就存 LF）。对 Windows 用户**修复** CRLF 污染问题。

- [ ] **Step 2: 验证不影响既有测试**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

Expected: 全部 PASS（.gitattributes 不影响 bats 运行）。

- [ ] **Step 3: 一致性检查**

```bash
python3 agate/scripts/check-protocol-consistency.py
```

Expected: `0 ERROR`（.gitattributes 不在协议文件扫描范围）。

---

### Task 4: 新增 platform-notes.md「Windows 原生」章节（安装指引）

**Files:**
- Modify: `agate/platform-notes.md`（末尾追加新章节）

**背景**：提供完整的 Windows 原生（Git for Windows bash）安装配置指引 + 已知限制 + 验证步骤。

- [ ] **Step 1: 在 platform-notes.md 末尾追加**

```markdown

---

## Windows 原生（Git for Windows，不用 WSL）

> agate 的 gate 脚本依赖 bash + GNU coreutils。Windows 原生无 bash，但 **Git for Windows** 安装时自带一个精简的 MSYS2 bash + coreutils，可在**不用 WSL** 的前提下运行 agate。

### 前置条件

| 依赖 | 安装方式 | 说明 |
|------|---------|------|
| **Git for Windows** | https://git-scm.com/download/win （独立安装包，不依赖 GitHub 账号） | 自带 `bash.exe` + `grep/sed/find/stat/sha256sum` 等核心工具。装完即有 bash 环境 |
| **Python 3.8+** | https://www.python.org/downloads/ | 安装时勾选「Add to PATH」。状态/vision 类 .py 工具需要 `pip install pyyaml` |
| **Pillow（可选）** | `pip install Pillow` | 仅 check-p6-evidence 的像素方差/ahash 检测需要。未装时自动跳过（WARNING 不阻断）|
| **shellcheck（可选）** | https://github.com/koalaman/shellcheck/releases | 仅开发者跑 `shellcheck` 时需要。使用者不需要 |
| **bats（仅开发者）** | 手动 clone https://github.com/bats-core/bats-core 到任意目录并加 PATH | 使用者不需要跑测试 |

### 安装步骤

1. **装 Git for Windows**：下载安装包，全程默认即可。它会在 `C:\Program Files\Git\` 安装 git + bash + coreutils。

2. **验证 bash 可用**：打开「Git Bash」（开始菜单），运行：
   ```bash
   bash --version
   stat -c%s /dev/null 2>/dev/null && echo "stat -c OK" || echo "stat -c 不可用"
   readlink -f / && echo "readlink OK"
   ```
   三个都应输出（非空）。

3. **装 Python + pyyaml**：
   ```bash
   python --version    # 应 3.8+
   pip install pyyaml
   ```

4. **clone agate 仓库**（任意 git 托管都行，不限于 GitHub）：
   ```bash
   git clone <你的 agate 仓库地址> ~/agate
   ```

5. **建立 `~/.agate` 软链接**（Git Bash 里 `~` 是 `C:\Users\<你>`）：
   ```bash
   ln -s ~/agate/agate ~/.agate
   ```
   > 若提示无法创建符号链接（无开发者模式/非管理员），改用环境变量：
   > 在系统环境变量里设 `AGATE_ROOT=C:\Users\<你>\agate\agate`（指向 agate 仓库的 `agate/` 子目录）。

6. **在项目仓库里装 hook**：
   ```bash
   cd /path/to/your/project
   bash ~/.agate/scripts/install-hook.sh
   ```
   > Windows 无符号链接权限时，hook 会以**复制模式**安装（输出含「复制模式」提示）。**升级 agate 后需重跑此命令**更新 hook（复制不自动跟随源文件）。

7. **验证 agate 可运行**：
   ```bash
   bash ~/.agate/scripts/agate-summary.sh
   ```
   应输出版本号 + 防护状态。

### 已知限制（Windows 原生）

| 限制 | 影响 | 规避 |
|------|------|------|
| `ln -sf` 退化为复制 | hook 不随 agate 升级自动更新 | 升级 agate 后重跑 `install-hook.sh`；或开 Windows「开发者模式」启用真符号链接 |
| `core.autocrlf` CRLF 污染 | .sh 报 `\r` 语法错、.py hash 不匹配 | 仓库已含 `.gitattributes` 强制 LF；若 clone 旧版本无此文件，手动 `git config core.autocrlf false` |
| bats 安装麻烦 | 开发者无法跑 `bats` 测试 | 手动 clone bats-core；或用 WSL 跑测试（使用不受影响） |
| CI 仅 ubuntu | Windows 本地行为无 CI 兜底 | 靠本地验证；protocol-tests.yml 未来可加 `runs-on: windows-latest` matrix |
| 路径分隔符 | MSYS2 自动转换 `/c/Users/` <-> `C:\Users\`，但极少数硬编码路径可能出问题 | 遇到时用 `cygpath -w` 转换 |

### 不支持的场景

- **纯 cmd/PowerShell 无 bash**：agate 的 25 个 .sh 无法运行，只能做 P0-P2（纯文档阶段），P3-P8 交接给有 bash 的环境。
- **Cygwin（非 MSYS2）**：理论上可行但未测，不保证。推荐 Git for Windows。
```

- [ ] **Step 2: 一致性检查（platform-notes.md 是协议文件）**

```bash
python3 agate/scripts/check-protocol-consistency.py
```

Expected: `0 ERROR`。（platform-notes.md 在 PROTOCOL_FILES 里，新增章节不引入死链/YAML 错误。）

---

### Task 5: README.md 依赖节补 Windows 提示

**Files:**
- Modify: `agate/scripts/README.md`

**背景**：依赖节补一句 Windows 提示，指向 platform-notes.md。

- [ ] **Step 1: 在 scripts/README.md 第 3 行（`agate 的所有自动化脚本。` 那行）之后、`## 脚本清单` 之前插入**

```markdown

> **Windows 用户**：agate 依赖 bash + GNU coreutils，Windows 原生无 bash。安装 **Git for Windows**（自带 MSYS2 bash + coreutils）即可在不用 WSL 的前提下运行。详见 `agate/platform-notes.md`「Windows 原生」章节。
```

- [ ] **Step 2: 一致性检查**

```bash
python3 agate/scripts/check-protocol-consistency.py
```

Expected: `0 ERROR`。

---

### Task 6: 全量回归 + 一致性 + 用例数 + shellcheck

**Files:**（无改动，仅验证）

- [ ] **Step 1: 全量 bats**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

Expected: 全部 PASS（含新增 install-hook 退化检测用例）。总数 = 原 591 + 1 = **592**。

- [ ] **Step 2: 一致性**

```bash
python3 agate/scripts/check-protocol-consistency.py
```

Expected: `0 ERROR`。

- [ ] **Step 3: 用例数**

```bash
bash agate/tests/scripts/count-tests.sh
```

Expected: **592**。

- [ ] **Step 4: shellcheck**

```bash
shellcheck -S warning agate/scripts/*.sh
```

Expected: 无 error（install-hook.sh 新增 `if [ -L ]` 守卫无 shellcheck 问题）。

- [ ] **Step 5: 确认 .gitattributes 不破坏 git 状态**

```bash
git status --short
```

Expected: `.gitattributes` 显示为新文件，无其他异常。

---

### Task 7: commit（self-gate）

**Files:**
- 提交：`.gitattributes`、`install-hook.sh`、`platform-notes.md`、`scripts/README.md`、`install-hook.bats`

- [ ] **Step 1: 暂存并提交**

```bash
cd /home/kity/oclab/agate/.worktrees/py-extraction
git add .gitattributes agate/scripts/install-hook.sh agate/platform-notes.md agate/scripts/README.md agate/tests/unit/install-hook.bats
git commit -m "feat(platform): Windows（Git for Windows bash）支持加固 + 安装指引

- 新增 .gitattributes 强制 LF，防 Windows autocrlf 污染 .sh/.py/.bats
- install-hook.sh ln -sf 后加 [ -L ] 退化检测，Windows 复制模式打印升级提醒
  （Linux/macOS 走符号链接分支，行为不变）
- platform-notes.md 新增「Windows 原生」章节：前置条件 + 安装步骤 + 已知限制
- scripts/README.md 补 Windows 提示指向 platform-notes
- 新增 install-hook 退化检测 bats 用例，总数 591->592

self-gate-review: docs/plans/agate-windows-support-20260808.md"
```

Expected: commit 成功。

- [ ] **Step 2: 确认工作区干净**

```bash
git status
```

Expected: clean（仅 HANDOFF-PY-EXTRACTION.md 未跟踪）。

---

## 批次结论记录（实施后填写）

- **Windows 支持路线**：Git for Windows 自带 MSYS2 bash，不用 WSL，不依赖 GitHub。
- **对 agate 原目标的负面作用**：零。所有改动防御性--Linux/macOS 行为不变（.gitattributes 本来就 LF、install-hook 走 `[ -L ]` 真分支输出不变、文档新增章节不破坏一致性）。
- **已知限制**：ln 退化（文档化）、bats 安装麻烦（文档化）、CI 仅 ubuntu（未来可加 windows matrix）。