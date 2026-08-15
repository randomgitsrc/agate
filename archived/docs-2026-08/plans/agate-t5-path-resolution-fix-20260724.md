# T5 修复：agate-next-card.sh 路径解析解耦

> 日期：2026-07-24
> 基线：main @ 6ca3273（v0.21.0 已合并）
> 动机：agate-next-card.sh 用 `_find_git_root` + 硬编码 `agate/` 前缀定位卡片文件，与目录结构耦合。若目录改名（v2.0）或脚本在非标准路径调用，会断裂。

---

## 0. 问题

`agate-next-card.sh:30,49` 用两步定位卡片文件：

1. `_find_git_root` 找 git 仓库根 -> `AGATE_REPO`
2. 硬编码 `$AGATE_REPO/agate/phase-cards/...` -> `CARD_FILE`

步骤 2 的 `agate/` 是协议子目录名——如果目录改名或脚本从非标准路径调用，会断裂。

对比 `agate-inject-card.sh:10` 已用 `AGATE_ROOT`（协议目录）解析路径，已免疫改名。

同样，`ci-gate-backstop.py:18,151` 硬编码 `agate/scripts/...` 路径，与目录名耦合。

## 1. 修改

### 1.1 agate-next-card.sh：用 AGATE_ROOT 替代 AGATE_REPO

**当前**（:17-30, 49, 68）：
```bash
_find_git_root() { ... }
AGATE_REPO="$(_find_git_root "$SCRIPT_DIR")"
CARD_FILE="$AGATE_REPO/agate/phase-cards/${PHASE}-..."
REL_CARD="${CARD_FILE#$AGATE_REPO/}"
```

**改为**：
```bash
AGATE_ROOT="${AGATE_ROOT:-$(dirname "$SCRIPT_DIR")}"
CARD_FILE="$AGATE_ROOT/phase-cards/${PHASE}-..."
REL_CARD="${CARD_FILE#$AGATE_ROOT/}"
```

变更点：
1. 删除 `_find_git_root` 函数（:18-28）
2. 删除 `AGATE_REPO` 赋值（:30）
3. 新增 `AGATE_ROOT="${AGATE_ROOT:-$(dirname "$SCRIPT_DIR")}"` — 与 agate-inject-card.sh:10 一致，支持环境变量覆盖
4. `CARD_FILE` 中删除 `agate/` 前缀（:49）
5. `REL_CARD` 中用 `$AGATE_ROOT/` 替代 `$AGATE_REPO/`（:68）

`REL_CARD` 变化：`agate/phase-cards/P3-tdd.md` -> `phase-cards/P3-tdd.md`（更短，不含仓库子目录前缀）。

### 1.2 ci-gate-backstop.py：用 __file__ 相对路径

**当前**（:18, 151）：
```python
script = Path("agate/scripts/check-gate.sh")
provenance_script = repo_root / "agate/scripts/check-p6-provenance.sh"
```

**改为**：
```python
_AGATE_ROOT = Path(__file__).resolve().parent.parent
script = _AGATE_ROOT / "scripts/check-gate.sh"
provenance_script = _AGATE_ROOT / "scripts/check-p6-provenance.sh"
```

`_AGATE_ROOT` = `ci-gate-backstop.py` 所在目录的上一级（`scripts/` -> 协议根）。

变更点：
1. 模块级计算 `_AGATE_ROOT`（:16 后）
2. `run_gate` 中 `Path("agate/scripts/check-gate.sh")`（CWD 相对路径）-> `_AGATE_ROOT / "scripts/check-gate.sh"`（:18）
3. `provenance_script` 中 `repo_root / "agate/scripts/check-p6-provenance.sh"`（repo_root 相对路径）-> `_AGATE_ROOT / "scripts/check-p6-provenance.sh"`（:151）

## 2. 对下游的影响

### agate-inject-card.sh

`agate-inject-card.sh:10` 已用 `AGATE_ROOT`，无变更。

### 测试（agate-next-card.bats）

测试 `setup()` 中有 `AGATE_REPO="$(git -C "$AGATE_SCRIPTS" rev-parse --show-toplevel)"`（:12），用于 `sha256sum "$AGATE_REPO/agate/phase-cards/..."` 验证。需同步：

- `sha256sum` 路径从 `$AGATE_REPO/agate/phase-cards/...` -> `$AGATE_ROOT/phase-cards/...`
- `AGATE_ROOT` 可通过 `dirname "$AGATE_SCRIPTS"` 获取

### CLI 输出格式

`REL_CARD` 从 `agate/phase-cards/P3-tdd.md` 变为 `phase-cards/P3-tdd.md`。CLI 输出的"路径"行会变化——这是输出格式变更，下游 hook 的 sha256 校验不受影响（sha256 算的是 body，不含 header 的路径行）。

但 `跨 checkout 路径` 测试验证的是全量 hash（含 header），路径行变化后 hash 会变。这是预期变化，不影响功能。

### pre-commit-gate.sh

`pre-commit-gate.sh` 不直接调用 `agate-next-card.sh`——它只调用 `agate-inject-card.sh`（已用 `AGATE_ROOT`）。无影响。

## 3. 测试

### 3.1 agate-next-card.bats 变更

`setup()` 中 `AGATE_REPO` -> `AGATE_ROOT`：

```bash
setup() {
    CARD_CMD="$AGATE_SCRIPTS/agate-next-card.sh"
    AGATE_ROOT="$(dirname "$AGATE_SCRIPTS")"
}
```

所有 `sha256sum "$AGATE_REPO/agate/phase-cards/..."` -> `sha256sum "$AGATE_ROOT/phase-cards/..."`。

### 3.2 新增测试

| 用例 | 描述 | 期望 |
|------|------|------|
| NC_ROOT.1 | AGATE_ROOT 环境变量覆盖 | 使用覆盖值定位卡片 |
| NC_ROOT.2 | 协议目录不在 git 仓库内时仍能工作（无 .git） | exit 0（卡片存在时） |

NC_ROOT.1 验证 `AGATE_ROOT` 环境变量可覆盖自动检测——为目录改名场景提供安全网。

NC_ROOT.2 验证移除 `_find_git_root` 后不再依赖 `.git` 存在——这是 T5 的核心改善。

## 4. 实施顺序

1. 修改 `agate-next-card.sh`（删除 `_find_git_root`，用 `AGATE_ROOT`）
2. 修改 `ci-gate-backstop.py`（用 `__file__` 相对路径）
3. 修改 `agate-next-card.bats`（路径同步 + 2 新测试）
4. 跑全量 bats + consistency + shellcheck

## 5. 涉及文件

| 文件 | 修改 |
|------|------|
| `agate/scripts/agate-next-card.sh` | 删 `_find_git_root`，用 `AGATE_ROOT` |
| `agate/scripts/ci-gate-backstop.py` | 用 `__file__` 相对路径 |
| `agate/tests/unit/agate-next-card.bats` | 路径同步 + 2 新测试 |

## 6. 验证

- bats 全量通过（含 2 新用例）
- `python3 agate/scripts/check-protocol-consistency.py` 0 ERROR
- `shellcheck -S warning agate/scripts/*.sh` clean
- self-gate protocol-alignment-review

## 7. 不在本版范围

| 内容 | 理由 |
|------|------|
| 目录改名 agate/ -> agate-core/ | 留待 v2.0 breaking-change 窗口 |
| agate-changes.sh 路径更新 | 不涉及 `agate-next-card.sh`，独立改动 |
| commit-msg-self-gate.sh 路径更新 | 触发条件用 git pathspec `agate/*.md`，独立改动 |
| agate-summary.sh `_find_git_root` | 共享同一函数但需要 git repo root（`git describe/branch/log`），与 agate-next-card.sh 不同——卡片定位只需协议目录 |

> **R1 修复**：B1（AGATE_ROOT 环境变量覆盖缺失）→ 改为 `${AGATE_ROOT:-...}` 模式；F1（ci-gate-backstop.py :18 是 CWD 相对路径非 repo_root 相对）→ 描述已修正；F2（agate-summary.sh 共享 `_find_git_root`）→ 不在范围但需说明理由；F3（测试名称引用 `AGATE_REPO`）→ 实施时同步更新测试名。
