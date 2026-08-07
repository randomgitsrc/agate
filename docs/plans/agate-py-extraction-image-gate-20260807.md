# agate IPC 抽离批次 6（最终）：图像处理 + gate_commands 补全 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成最后 5 处内联 python 抽离：`check-p6-evidence.sh`（3 处：ui_affected 复用 `agate-md-field-get.py`、variance/ahash 新工具 `agate-image-check.py`）+ `check-gate.sh`（2 处：新工具 `agate-gate-missing-cmds.py`、`agate-gate-p5-count.py`）。至此 46 处内联 python 全部清零。

**Architecture:** （1）`agate-image-check.py` 提供 `variance`（读 `IMG_PATH` env，PIL 方差检测，无 Pillow 输出 `SKIP_NO_PILLOW`）与 `ahash`（读 `SCREENSHOTS_DIR` env，average hash 相似度，无 Pillow stderr 输出 + exit 1）两个子命令。（2）`agate-gate-missing-cmds.py` 读 `GATE_FILE` env，解析 gate_commands 每个命令第一个 token，输出 `key:token`（缺失命令检测）。（3）`agate-gate-p5-count.py` 读 `GATE_FILE` env，统计 P5 命令数。ui_affected 复用既有 `agate-md-field-get.py ui_affected`。行为等价 → 既有测试（check-p6-evidence 28、check-gate 101）是强兜底。

**Tech Stack:** bash（薄壳）+ python3（3 个新工具 + 复用 md-field-get）+ bats（测试）。

**背景调研（已确认）：**
- 触发文件：`agate/scripts/agate-image-check.py`（新增）、`agate-gate-missing-cmds.py`（新增）、`agate-gate-p5-count.py`（新增）、`check-p6-evidence.sh`（改）、`check-gate.sh`（改）、bats（改）→ self-gate 触发
- **5 处内联分布**：
  - check-p6-evidence:59 `ui_affected`：与批次 5 的 provenance:156 逐字相同 → 复用 `agate-md-field-get.py ui_affected`
  - check-p6-evidence:122 `variance`：PIL 方差检测，无 Pillow 打印 `SKIP_NO_PILLOW` 并 exit 0，异常打印 -1
  - check-p6-evidence:178 `ahash`：PIL average hash，无 Pillow stderr 打印 `SKIP_NO_PILLOW` + exit 1（bash 侧 `2>/dev/null || echo ""` 吞掉 → AHASH_LIST 空），异常跳过该文件
  - check-gate:159 `missing cmds`：解析 gate_commands 每个命令第一个 token，跳过 `/` 或 `=` 的 token，输出 `key:token`
  - check-gate:213 `P5 count`：统计 `^  (P5\w*):` 个数
- **SCRIPT_DIR**：check-p6-evidence.sh 与 check-gate.sh **均无** SCRIPT_DIR 也无 AGATE_ROOT → 需补加（与批次 4/5 一致）
- **既有工具**：`agate-md-field-get.py`（risk_level/ui_affected/phases）可直接复用 ui_affected

---

## File Structure

- **Create** `agate/scripts/agate-image-check.py`（variance/ahash 子命令）、`agate-gate-missing-cmds.py`、`agate-gate-p5-count.py`。
- **Modify** `agate/scripts/check-p6-evidence.sh`（3 处 + SCRIPT_DIR）、`check-gate.sh`（2 处 + SCRIPT_DIR）。
- **Test** `agate/tests/unit/agate-image-check.bats`、`agate-gate-missing-cmds.bats`、`agate-gate-p5-count.bats`（新建）。
- **Modify** `agate/tests/README.md`。

---

### Task 1: TDD — 写 3 个新工具直接失败测试（真红）

**Files:**
- Test: `agate/tests/unit/agate-image-check.bats`、`agate-gate-missing-cmds.bats`、`agate-gate-p5-count.bats`（均新建）

**背景**：3 个工具尚不存在。各写直接测试确立契约。

- [ ] **Step 1: 新建 `agate-image-check.bats`**

```bash
#!/usr/bin/env bats
# tests/unit/agate-image-check.bats — 图像分析工具单元测试
load ../helpers/load.bash

@test "IMG.1 variance 无 Pillow → SKIP_NO_PILLOW" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/img-XXXXXX")
    head -c 100 /dev/urandom > "$dir/a.png"
    run bash -c "IMG_PATH='$dir/a.png' python3 -c 'import PIL' 2>/dev/null && echo HAS_PIL || echo NO_PIL"
    if [[ "$output" == "NO_PIL" ]]; then
        run bash -c "IMG_PATH='$dir/a.png' python3 '$AGATE_SCRIPTS/agate-image-check.py' variance"
        [ "$status" -eq 0 ]; [[ "$output" == "SKIP_NO_PILLOW" ]]
    else
        skip "Pillow 已安装，跳过无 Pillow 分支"
    fi
}

@test "IMG.2 variance 非图像 → -1" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/img-XXXXXX")
    echo "not an image" > "$dir/a.png"
    run bash -c "IMG_PATH='$dir/a.png' python3 '$AGATE_SCRIPTS/agate-image-check.py' variance"
    [ "$status" -eq 0 ]
    case "$output" in
        "-1"|"SKIP_NO_PILLOW") : ;;
        *) false;;
    esac
}

@test "IMG.3 ahash 无 Pillow → stderr+exit 1" {
    run bash -c "python3 -c 'import PIL' 2>/dev/null && echo HAS_PIL || echo NO_PIL"
    if [[ "$output" == "NO_PIL" ]]; then
        run bash -c "SCREENSHOTS_DIR='/nonexistent' python3 '$AGATE_SCRIPTS/agate-image-check.py' ahash"
        [ "$status" -eq 1 ]
    else
        skip "Pillow 已安装，跳过无 Pillow 分支"
    fi
}

@test "IMG.4 ahash 合法图片 → 输出 64 位 hash（Pillow 已装时）" {
    run bash -c "python3 -c 'import PIL' 2>/dev/null && echo HAS_PIL || echo NO_PIL"
    if [[ "$output" == "NO_PIL" ]]; then
        skip "Pillow 未安装，跳过"
    fi
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/img-XXXXXX")
    python3 -c "
from PIL import Image
img = Image.new('L', (8, 8), 128)
img.save('$dir/a.png')
"
    run bash -c "SCREENSHOTS_DIR='$dir' python3 '$AGATE_SCRIPTS/agate-image-check.py' ahash"
    [ "$status" -eq 0 ]
    [[ "$output" =~ ^[01]{64}$ ]]
}
```

> **红/绿说明**：`agate-image-check.py` 尚不存在 → 全 FAIL（红）。实现后 → 全 PASS（绿）。**注意**：本机若已装 Pillow，IMG.1/IMG.3 会 skip（本机检查见 Task 4 Step 0）。

- [ ] **Step 2: 新建 `agate-gate-missing-cmds.bats`**

```bash
#!/usr/bin/env bats
# tests/unit/agate-gate-missing-cmds.bats — gate_commands 缺失命令检测工具
load ../helpers/load.bash

@test "GMC.1 提取命令 token 输出 key:token" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/gmc-XXXXXX")
    cat > "$dir/P2.md" <<'EOF'
gate_commands:
  P3: pytest -q
  P3_formatter: pytest.sh
  P5: npx vitest
EOF
    run bash -c "GATE_FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-gate-missing-cmds.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *"P3:pytest"* ]]
    [[ "$output" == *"P5:npx"* ]]
    [[ "$output" != *"formatter"* ]]
}

@test "GMC.2 命令含 / 或 = 的 token 跳过" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/gmc-XXXXXX")
    cat > "$dir/P2.md" <<'EOF'
gate_commands:
  P3: .venv/bin/python -m pytest
  P5: A=1 pytest
EOF
    run bash -c "GATE_FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-gate-missing-cmds.py'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}
```

- [ ] **Step 3: 新建 `agate-gate-p5-count.bats`**

```bash
#!/usr/bin/env bats
# tests/unit/agate-gate-p5-count.bats — P5 命令计数工具
load ../helpers/load.bash

@test "GPC.1 统计 P5 命令数" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/gpc-XXXXXX")
    cat > "$dir/P2.md" <<'EOF'
gate_commands:
  P5: pytest
  P5_unit: pytest unit
  P5_e2e: npx vitest
EOF
    run bash -c "GATE_FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-gate-p5-count.py'"
    [ "$status" -eq 0 ]; [[ "$output" == "3" ]]
}

@test "GPC.2 无 gate_commands 块 → 0" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/gpc-XXXXXX")
    echo "无 gate_commands" > "$dir/P2.md"
    run bash -c "GATE_FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-gate-p5-count.py'"
    [ "$status" -eq 0 ]; [[ "$output" == "0" ]]
}
```

- [ ] **Step 4: 运行 3 个测试文件确认当前失败（红）**

```bash
bats agate/tests/unit/agate-image-check.bats agate/tests/unit/agate-gate-missing-cmds.bats agate/tests/unit/agate-gate-p5-count.bats
```

Expected: 全部 FAIL（工具不存在）。

---

### Task 2: TDD — 实现 3 个新工具（绿）

**Files:**
- Create: `agate/scripts/agate-image-check.py`、`agate-gate-missing-cmds.py`、`agate-gate-p5-count.py`

**背景**：逐个复刻内联逻辑。

- [ ] **Step 1: 创建 `agate-image-check.py`**

```python
#!/usr/bin/env python3
"""截图图像分析（py 抽离批次 6）。

variance 子命令：读 IMG_PATH env，PIL 灰度方差检测。无 Pillow 打印 SKIP_NO_PILLOW
（exit 0）；图像异常打印 -1。
ahash 子命令：读 SCREENSHOTS_DIR env，遍历图片算 average hash 并逐行打印。无 Pillow
stderr 打印 SKIP_NO_PILLOW + exit 1（bash 侧 2>/dev/null || echo 吞掉）；单图异常跳过。
"""

import glob
import os
import sys


def _load_pil():
    try:
        from PIL import Image
        return Image
    except ImportError:
        return None


def main():
    op = sys.argv[1]
    Image = _load_pil()
    if op == "variance":
        if Image is None:
            print("SKIP_NO_PILLOW")
            return
        try:
            img = Image.open(os.environ["IMG_PATH"]).convert("L")
            pixels = list(img.tobytes())
            mean = sum(pixels) / len(pixels)
            variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
            print(int(variance))
        except Exception:
            print(-1)
    elif op == "ahash":
        if Image is None:
            sys.stderr.write("SKIP_NO_PILLOW\n")
            sys.exit(1)

        def _ahash(path):
            img = Image.open(path).convert("L").resize((8, 8))
            pixels = list(img.tobytes())
            avg = sum(pixels) / len(pixels)
            return "".join("1" if p >= avg else "0" for p in pixels)

        for f in sorted(glob.glob(os.environ["SCREENSHOTS_DIR"] + "/*")):
            try:
                print(_ahash(f))
            except Exception:
                pass
    else:
        sys.stderr.write("agate-image-check: unknown op {}\n".format(op))
        sys.exit(2)


if __name__ == "__main__":
    main()
```

> **等价性**：`variance` 复刻 evidence:122（无 Pillow → SKIP_NO_PILLOW + exit()；异常 → -1）。`ahash` 复刻 evidence:178（无 Pillow → stderr + exit 1；`sorted(glob.iglob)`；异常跳过）。`_load_pil` 用函数内 import 避免顶层导入失败。

- [ ] **Step 2: 创建 `agate-gate-missing-cmds.py`**

```python
#!/usr/bin/env python3
"""gate_commands 缺失命令检测（py 抽离批次 6）。

读 GATE_FILE env。解析 gate_commands 每个命令的第一个 token，
跳过含 / 或 = 的 token，输出 "key:token"。无 gate_commands 块输出空。
"""

import os
import re
import sys

content = open(os.environ["GATE_FILE"]).read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    sys.exit(0)
block = m.group(1)
for k, v in re.findall(r"^  (P[0-9]\w*):\s*(.+)$", block, re.MULTILINE):
    if k.endswith("_formatter") or k == "project_module":
        continue
    val = v.strip().strip(chr(34)).strip(chr(39))
    if not val:
        continue
    token = val.split()[0]
    token = token.lstrip("$(").rstrip(")")
    if "/" in token or "=" in token:
        continue
    print("{}:{}".format(k, token))
```

- [ ] **Step 3: 创建 `agate-gate-p5-count.py`**

```python
#!/usr/bin/env python3
"""统计 gate_commands.P5 命令数（py 抽离批次 6）。

读 GATE_FILE env。无 gate_commands 块输出 0。
"""

import os
import re
import sys

content = open(os.environ["GATE_FILE"]).read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    print(0)
    sys.exit(0)
block = m.group(1)
count = len(re.findall(r"^  (P5\w*):", block, re.MULTILINE))
print(count)
```

- [ ] **Step 4: 运行 3 个测试文件确认通过（绿）**

```bash
chmod +x agate/scripts/agate-image-check.py agate/scripts/agate-gate-missing-cmds.py agate/scripts/agate-gate-p5-count.py
bats agate/tests/unit/agate-image-check.bats agate/tests/unit/agate-gate-missing-cmds.bats agate/tests/unit/agate-gate-p5-count.bats
```

Expected: 全部 PASS。

---

### Task 3: 改造 2 个脚本 5 处内联（薄壳）

**Files:**
- Modify: `agate/scripts/check-p6-evidence.sh`、`check-gate.sh`

**背景**：逐处替换。两脚本均无 SCRIPT_DIR/AGATE_ROOT → 先补（Step 0）。

- [ ] **Step 0: 为两脚本补 SCRIPT_DIR（前置）**

在两个脚本顶部（`set -euo pipefail` 之后、其他逻辑之前）加：
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```
补到：`agate/scripts/check-p6-evidence.sh`、`agate/scripts/check-gate.sh`。

- [ ] **Step 1: check-p6-evidence.sh 三处**

原（:59 ui_affected）：
```bash
    UI_AFFECTED=$(P2_FILE="$P2_FILE" python3 -c "
import re, os
with open(os.environ['P2_FILE']) as f:
    text = f.read()
m = re.search(r'ui_affected:\s*(true|false)', text)
print(m.group(1) if m else '')
" 2>/dev/null || echo "")
```
新：
```bash
    UI_AFFECTED=$(FILE="$P2_FILE" python3 "$SCRIPT_DIR/agate-md-field-get.py" ui_affected 2>/dev/null || echo "")
```

原（:122 variance）：
```bash
            VARIANCE=$(IMG_PATH="$img" python3 -c "
import os
try:
    from PIL import Image
except ImportError:
    print('SKIP_NO_PILLOW')
    exit()
try:
    img = Image.open(os.environ['IMG_PATH']).convert('L')
    pixels = list(img.tobytes())
    mean = sum(pixels) / len(pixels)
    variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
    print(int(variance))
except Exception:
    print(-1)
" 2>/dev/null || echo -1)
```
新：
```bash
            VARIANCE=$(IMG_PATH="$img" python3 "$SCRIPT_DIR/agate-image-check.py" variance 2>/dev/null || echo -1)
```

原（:178 ahash）：
```bash
        AHASH_LIST=$(SCREENSHOTS_DIR="$SCREENSHOTS_DIR" python3 -c "
import sys, os, glob
try:
    from PIL import Image
except ImportError:
    print('SKIP_NO_PILLOW', file=sys.stderr)
    sys.exit(1)
def ahash(path):
    img = Image.open(path).convert('L').resize((8, 8))
    pixels = list(img.tobytes())
    avg = sum(pixels) / len(pixels)
    return ''.join('1' if p >= avg else '0' for p in pixels)
for f in sorted(glob.glob(os.environ['SCREENSHOTS_DIR'] + '/*')):
    try:
        print(ahash(f))
    except Exception:
        pass
" 2>/dev/null || echo "")
```
新：
```bash
        AHASH_LIST=$(SCREENSHOTS_DIR="$SCREENSHOTS_DIR" python3 "$SCRIPT_DIR/agate-image-check.py" ahash 2>/dev/null || echo "")
```

- [ ] **Step 2: check-gate.sh 两处**

原（:159 missing cmds）：→ 新：
```bash
      MISSING_CMDS=$(GATE_FILE="$P2_FILE" python3 "$SCRIPT_DIR/agate-gate-missing-cmds.py" 2>/dev/null || echo "")
```

原（:213 P5 count）：
```bash
          P5_CMD_COUNT=$(GATE_FILE="$TASK_DIR/P2-design.md" python3 -c "
import re, os
with open(os.environ['GATE_FILE']) as f:
    content = f.read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r'^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)', content, re.MULTILINE)
if not m:
    print(0)
    exit()
block = m.group(1)
count = len(re.findall(r'^  (P5\w*):', block, re.MULTILINE))
print(count)
" 2>/dev/null || echo 0)
```
新：
```bash
          P5_CMD_COUNT=$(GATE_FILE="$TASK_DIR/P2-design.md" python3 "$SCRIPT_DIR/agate-gate-p5-count.py" 2>/dev/null || echo 0)
```

- [ ] **Step 3: 验证 2 个脚本相关测试仍绿**

```bash
bats agate/tests/unit/check-p6-evidence.bats agate/tests/unit/check-gate.bats agate/tests/unit/agate-image-check.bats agate/tests/unit/agate-gate-missing-cmds.bats agate/tests/unit/agate-gate-p5-count.bats
```

Expected: 全部 PASS。

---

### Task 4: 全量回归 + 一致性 + 用例数 + shellcheck

**Files:**（无改动，仅验证）

- [ ] **Step 0: 确认本机 Pillow 状态（影响 IMG 测试）**

```bash
python3 -c "import PIL; print('PIL installed')" 2>&1 || echo "NO_PIL"
```
若本机无 Pillow，IMG.1/IMG.3 走无 Pillow 分支（正常）；若有 Pillow，IMG.1/IMG.3 skip（也正常）。IMG.2 两者皆可。

- [ ] **Step 1: 全量 bats**

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

Expected: 全部 PASS（干净汇总）。

- [ ] **Step 2: 一致性**

```bash
python3 agate/scripts/check-protocol-consistency.py
```

Expected: `0 ERROR`。（新 .py 不匹配 check-*.sh glob，无新增锚点需求。）

- [ ] **Step 3: 用例数**

```bash
bash agate/tests/scripts/count-tests.sh
```

Expected: 原 583 + 4（IMG.1-4）+ 2（GMC.1-2）+ 2（GPC.1-2）= **591**。

- [ ] **Step 4: shellcheck**

```bash
shellcheck -S warning agate/scripts/*.sh
```

Expected: 无 error。

- [ ] **Step 5: AST 校验（3 个新 .py）**

```bash
for f in agate-image-check agate-gate-missing-cmds agate-gate-p5-count; do python3 -c "import ast; ast.parse(open('agate/scripts/$f.py').read())"; done
```

Expected: 无输出（语法有效）。

---

### Task 5: 文档同步（README 逐脚本用例数）

**Files:**
- Modify: `agate/tests/README.md`

**背景**：新增 3 个 .bats 文件需登记。

- [ ] **Step 1: 定位 README 逐脚本表 + 插入 3 行**

在 `agate-evidence-consistency.py` 行附近插入：
```
| agate-image-check.py | unit/agate-image-check.bats | 4 |
| agate-gate-missing-cmds.py | unit/agate-gate-missing-cmds.bats | 2 |
| agate-gate-p5-count.py | unit/agate-gate-p5-count.bats | 2 |
```
> **注意**：总数行是 `以 count-tests.sh 输出为准`，不需改。

---

### Task 6: commit（self-gate）

**Files:**
- 提交：3 个新 .py、3 个新 .bats、2 个 .sh、README

**背景**：触发文件含 `agate/scripts/*.py`、`agate/scripts/*.sh`、`agate/tests/*.bats` → commit-msg-self-gate hook 要求 `self-gate-review:`。

- [ ] **Step 1: 暂存并提交**

```bash
cd /home/kity/oclab/agate/.worktrees/py-extraction
git add agate/scripts/agate-image-check.py agate/scripts/agate-gate-missing-cmds.py agate/scripts/agate-gate-p5-count.py agate/scripts/check-p6-evidence.sh agate/scripts/check-gate.sh agate/tests/unit/agate-image-check.bats agate/tests/unit/agate-gate-missing-cmds.bats agate/tests/unit/agate-gate-p5-count.bats agate/tests/README.md
git commit -m "feat(scripts): 图像处理 + gate_commands 补全，完成 46 处内联 python 清零

新增 agate-image-check.py（variance/ahash，PIL）+ agate-gate-missing-cmds.py
+ agate-gate-p5-count.py。ui_affected 复用 agate-md-field-get.py。
替换 check-p6-evidence(3) check-gate(2) 共 5 处内联 python，至此 46 处全部清零。
为 2 个脚本补 SCRIPT_DIR。行为等价，既有 583 测试全绿。
新增 IMG.1-4 GMC.1-2 GPC.1-2，总数 583→591。

self-gate-review: docs/plans/agate-py-extraction-image-gate-20260807.md"
```

Expected: commit 成功，hook 识别 `self-gate-review:` 无 WARNING。

- [ ] **Step 2: 确认工作区干净**

```bash
git status
```

Expected: clean（仅 HANDOFF-PY-EXTRACTION.md 未跟踪）。

---

## 批次结论记录（实施后填写）

- **46 处全部清零**。check-p6-evidence 与 check-gate 完成抽离。
- **完整工具族**：agate-json-get / agate-read-gate-commands / agate-read-p5-commands / agate-state-get / agate-retreat-state / agate-md-field-get / agate-state-yaml-check / agate-changelog-unreleased / agate-card-inject / agate-vision-blocker / agate-evidence-consistency / agate-image-check / agate-gate-missing-cmds / agate-gate-p5-count。
- **验证**：bats 全绿、count-tests 591、consistency 0 ERROR、shellcheck 0 error。