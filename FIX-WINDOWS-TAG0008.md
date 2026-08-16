# TAG0008 修复交接单 — Windows 冒烟 2 失败（PR #148 CI）

> 任务：修复 TAG0008 PR #148 的 Windows 冒烟失败（pytest windows-latest 2 failed）。
> worktree：`/home/kity/oclab/agate/.worktrees/agate-TAG0008`（feat/TAG0008-version-management，13 commit 已完成 P0-P8）
> 现状：Linux 全量 823 passed 全绿；Windows 冒烟 2 用例失败阻塞 merge。

---

## 1. 两个失败（必须都修才能 merge）

### 失败 1：`test_csg_1_readme_triggers_warning`（integration/test_commit_msg_self_gate_integration.py:43）

**现象**：Windows 上改 README.md commit 后，`assert "self-gate-review" in result.output` 失败——commit-msg hook 没触发 self-gate WARNING。

**代码**（test 用 `_setup_hook` 复制 hook + `_commit` 传 AGATE_ROOT env）：
```python
@pytest.mark.windows_smoke
def test_csg_1_readme_triggers_warning(git_repo, agate_scripts, agate_root, run_cli):
    repo = _setup_hook(git_repo, agate_scripts)
    (repo / "README.md").write_text("change\n", encoding="utf-8")
    git_repo.stage("README.md")
    result = _commit(run_cli, repo, agate_root, "-m", "update readme")
    assert result.returncode == 0
    assert "self-gate-review" in result.output
```

**注意**：这是 **TAG0013 引入的功能**（README/AGENTS 触发 self-gate，`_SELF_GATE_RE` 已含 `README\.md|AGENTS\.md`），**非 TAG0008 代码引入**——但阻塞了 TAG0008 的 PR，且可能与 TAG0008 的 install/hook 改造有交互，须一并查清。

**排查方向**：
- `commit-msg-self-gate.sh` 薄壳在 Windows Git Bash 下能否 exec `commit-msg-self-gate.py`（python 探测 / AGATE_ROOT 自定位）
- `_SELF_GATE_RE`（commit-msg-self-gate.py:38）在 Windows 路径下 staged 文件列表的换行/路径格式（`git diff --cached --name-only` 在 Windows 输出 `\r\n`？`line.rstrip("\r")` 处理了吗）
- `_setup_hook` 的 AGATE_ROOT env 传递（`_commit` 里 `env={"AGATE_ROOT": str(agate_root)}`）——Windows 上 `str(WindowsPath)` 是 `D:/a/...` 正斜杠还是 `D:\a\...` 反斜杠？commit-msg-self-gate.sh 的 readlink/AGATE_ROOT 自定位在 Windows 的行为
- **关键怀疑**：commit-msg-self-gate.sh 薄壳在 Windows 上 AGATE_ROOT 自定位失败（readlink 行为）→ 找不到 py → 静默跳过 → self-gate 不触发

### 失败 2：`test_bdd_1_latest_pointer_after_noarg_install`（unit/test_agate_version_install.py:80）

**现象**：Windows 上 `agate-install`（无参数）后 `latest` 指针 `assert latest.exists()` 失败（False）。

**代码**：
```python
@pytest.mark.windows_smoke
def test_bdd_1_latest_pointer_after_noarg_install(...):
    _tag_upstream(git_repo)
    home = tmp_path / "home"
    result = _run_install(run_cli, python_exe, agate_scripts, home, repo_url=py_path(git_repo.path))
    assert result.returncode == 0
    agate_home = home / ".agate"
    latest = agate_home / "latest"
    assert latest.exists()
    if sys.platform == "win32":
        assert not latest.is_dir()
    else:
        assert latest.is_symlink()
    target = _resolve_pointer(agate_home, "latest")
    assert target.is_dir()
    assert target.name == "v0.48.0"
```

**相关实现**（agate/scripts/agate-install.py）：
- L75-85 `_write_pointer`：POSIX 用 `os.symlink`；Windows(nt) 用**复制模式文本指针**——写一个文本文件（内容是目标名？还是别的）
- L98 `_resolve_pointer`：先 `os.path.islink` 再 `os.path.isdir`（注释说：POSIX 软链指针 latest→v0.48.0 等；Windows 文本指针返回目录路径）

**排查方向**：
- `_write_pointer` 的 Windows 分支**实际写了什么**——如果是文本指针（如写入 `v0.48.0` 字符串到文件），`Path.exists()` 应该 True（文件存在）——但断言 False，说明**文件根本没创建**或路径不对
- 可能：Windows 分支条件判断错误（`os.name == "nt"`？还是别的条件，导致走了不创建的分支）
- `_run_install` 测试 helper 传的 `repo_url=py_path(git_repo.path)`——Windows 上 URL 路径格式可能影响 install 的 repo clone/指针创建

---

## 2. 排查方法（Windows 冒烟无法本地跑，靠静态分析 + Linux 模拟）

本环境（Linux）无法真机跑 Windows。按 AGENTS.md 测试平台无关原则：
- **平台差异场景按平台分支断言**——测试已用 `if sys.platform == "win32"` 分支，看分支逻辑是否与实现匹配
- **Linux 上用模拟覆盖 Windows 分支**——`os.name` mock / `PYTHONIOENCODING` / ln mock
- 检查 `test_agate_version_install.py` 的 `@pytest.mark.windows_smoke` 用例是否有 `_run_install` helper 的 Windows 路径处理

## 3. 修复后验证（worktree 内）

```bash
# 全量（Linux 必须全绿，Windows 冒烟靠静态修复 + CI 重跑）
python3 -m pytest agate/tests/ -q

# 单测定位
python3 -m pytest agate/tests/unit/test_agate_version_install.py -q
python3 -m pytest agate/tests/integration/test_commit_msg_self_gate_integration.py -q

# consistency + shellcheck
python3 agate/scripts/check-protocol-consistency.py --strict
shellcheck -S warning agate/scripts/*.sh
bash agate/tests/scripts/count-tests.sh
```

## 4. 修复纪律

- **只 add 修复文件**：不用 `git add -A`
- **commit message**：`wf(TAG0008-P5fix): Windows 冒烟修复——{描述}`
- **改脚本走 TDD**（若加测试）或**先分析根因再改**（若已有测试锁）
- 修复后 **push 分支** → CI 重跑 → Windows 冒烟绿 → 通知主 checkout merge
- 若修复涉及协议文档/脚本（agate/scripts/*.py），commit 需 self-gate-review 或 self-gate-skip 理由

## 5. 修复边界

- 两个失败**都必须在 TAG0008 分支修**（阻塞 merge）
- 失败 1（TAG0013 回归）若根因在 commit-msg-self-gate 机制本身，修完应跑 TAG0013 相关测试确认不破坏
- 若发现修复涉及超出"两个 Windows 失败"的改动，先停下与主 checkout 确认

## 6. 交接确认

- worktree 基线：Linux 823 passed 全绿 + 0 consistency ERROR（修复前）
- 任务数据：TAG0008 已完成 P0-P8（phase=READY，v0.50.0），修复是 PR 前收尾
- 交接单位置：`FIX-WINDOWS-TAG0008.md`（worktree 根）
