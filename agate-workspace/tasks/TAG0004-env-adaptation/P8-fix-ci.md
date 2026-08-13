---
phase: P8
task_id: TAG0004-env-adaptation
type: implementation
parent: P8-release.md
trace_id: TAG0004-P8-20260813
status: draft
created: 2026-08-13
agent: implementer
---

# P8 后 CI 修复（PR #127 Windows 问题）

## 背景

PR #127 的 CI 双平台矩阵（ubuntu-latest + windows-latest）抓到 3 个 Windows 真实问题。其中 2 个属本修复范围（consistency 中文输出编码 + shellcheck 安装 PATH），第 3 个（bats ubuntu bdd-25，tag v0.44.0 未推送）由主 Agent push tag 解决，不在本范围。

## 改动 1：`agate/scripts/check-protocol-consistency.py`

**问题**：Windows 下 `print("  agate 协议结构一致性检查 (P3-1)")` 等中文输出在 cp1252 编码崩 `UnicodeEncodeError: 'charmap' codec can't encode`。

**修复**：入口（`import sys` 后）加 stdout reconfigure：

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

- `hasattr` 守卫保证 Python 3.7- 环境不崩（reconfigure 自 3.7 引入）
- Linux UTF-8 locale 下无副作用，CI ubuntu job 行为不变
- 最小改动，未重构打印逻辑

## 改动 2：`.github/workflows/protocol-tests.yml`

**问题 a — shellcheck (Windows) exit 127**：原安装步骤 `echo "$GITHUB_WORKSPACE/shellcheck-v0.10.0" >> $GITHUB_PATH` 指向不存在的子目录（zip 解压出的是 `shellcheck.exe` 在 zip 根，无 `shellcheck-v0.10.0/` 子目录）→ PATH 加空目录 → `shellcheck` 命令找不到。

**修复**：
- 解压到 `$GITHUB_WORKSPACE/shellcheck/` 并 PATH 加该实际目录
- 调用处拆成 Linux/Windows 两步，Windows 用 `shellcheck.exe`（稳妥可解析）

```yaml
      - name: Install shellcheck (Windows)
        if: runner.os == 'Windows'
        run: |
          curl -sSLo shellcheck.zip https://github.com/koalaman/shellcheck/releases/download/v0.10.0/shellcheck-v0.10.0.zip
          unzip -q shellcheck.zip -d "$GITHUB_WORKSPACE/shellcheck"
          echo "$GITHUB_WORKSPACE/shellcheck" >> $GITHUB_PATH
      - name: Run shellcheck (Linux)
        if: runner.os == 'Linux'
        run: shellcheck -S warning agate/scripts/*.sh
      - name: Run shellcheck (Windows)
        if: runner.os == 'Windows'
        run: shellcheck.exe -S warning agate/scripts/*.sh
```

**问题 b — consistency/gate-backstop (Windows) UnicodeEncodeError**：Windows job 的 python 命令输出中文崩编码。

**修复**：两个 Windows step 设 `PYTHONIOENCODING: utf-8`（step env），与脚本侧 reconfigure 构成双保险。

```yaml
      - name: Run consistency check (Windows)
        if: runner.os == 'Windows'
        env:
          PYTHONIOENCODING: utf-8
        run: python agate/scripts/check-protocol-consistency.py
```

```yaml
      - name: Run gate backstop check (Windows)
        if: runner.os == 'Windows'
        env:
          PYTHONIOENCODING: utf-8
        run: python agate/scripts/ci-gate-backstop.py
```

## 自查结果

| 检查 | 命令 | 结果 |
|------|------|------|
| consistency | `python3 agate/scripts/check-protocol-consistency.py --strict` | 0 ERROR，exit 0，全部 8 CHECK PASS |
| bats | `bats agate/tests/unit/check-protocol-consistency.bats` | 3/3 ok |
| yaml 合法 | `python3 -c "import yaml; yaml.safe_load(...)"` | 合法，jobs: bats/shellcheck/consistency/gate-backstop |
| diff 落盘 | `git diff` | 2 文件 + progress 已落盘 |

> 自查 ≠ gate。Windows 实际验证由主 Agent 提交后 CI windows-latest job 兜底。

## 范围声明

- 只改 2 个文件：`agate/scripts/check-protocol-consistency.py` + `.github/workflows/protocol-tests.yml`，最小改动
- 未改主 checkout `/home/kity/oclab/agate` 与 `~/.agate`
- 无 [SCOPE_GAP]——本任务范围内无遗漏的 P2 已声明改动
- [PROD_NOT_TOUCHED]
