#!/usr/bin/env python3
"""agate-summary.py — 输出当前 agate 版本 + 启动必读 + 防护状态

从 agate-summary.sh 迁移（TAG0010 批次 1d）。用法：
  python3 ~/.agate/scripts/agate-summary.py

用途：agent 启动时快速知道当前用什么协议版本，是否需要升级等。
exit 0：成功（输出到 stdout）；exit 1：无法解析脚本路径（stderr 报错）或
找不到 agate git 仓库（sh 版 set -e 在命令替换处静默退出，此处等价静默）。

迁移说明：readlink -f → os.path.realpath；find .git 逐级上溯 → os.path 循环；
git -C 调用 → subprocess.run(cwd=...)；sed 's/^/  /' → 行前缀 join；
printf '%b' "$GUARDS" → 直接构造真实换行串；cmp -s → 逐字节比较；
cat heredoc → 单串拼接 + stdout.buffer 写 UTF-8 字节（保证逐字节等价）。
"""

import os
import subprocess
import sys

_GUARD_SCRIPTS = [
    "check-state-yaml.py",
    "check-gate.py",
    "check-changelog.py",
    "check-p6-evidence.py",
    "check-p6-provenance.py",
    "check-state-transition.py",
    "check-pruning.py",
    "check-scope-resolved.py",
    "check-retrospective.py",
]

_DRIFT_SCRIPTS = ["check-tdd-red.py", "check-gate.py", "check-pruning.py"]


def _find_git_root(start):
    """从 start 逐级向上找含 .git 的目录（等价 sh 的 _find_git_root，不含根目录本身）。"""
    d = os.path.normpath(start)
    while d != os.path.sep:
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return ""


def _git(repo, args, fallback=""):
    """git -C 等价：cwd=repo 调 subprocess，stdout 剥尾换行，失败返回 fallback。"""
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return fallback
    if proc.returncode != 0:
        return fallback
    return (proc.stdout or "").rstrip("\n")


def _indent_lines(text):
    """sed 's/^/  /' 等价：每行前缀两空格。"""
    if not text:
        return ""
    return "\n".join("  " + line for line in text.split("\n"))


def _build_guards(script_dir):
    """防护机制清单（等价 sh 的 GUARDS 拼接 + printf '%b' 解释 \\n）。"""
    parts = []
    for script in _GUARD_SCRIPTS:
        if os.path.isfile(os.path.join(script_dir, script)):
            parts.append("  ✓ " + script)
    pre_commit = os.path.join(script_dir, "pre-commit-gate.sh")
    if os.path.isfile(pre_commit) and os.access(pre_commit, os.X_OK):
        parts.append("  ✓ pre-commit-gate.sh（hook 入口）")
    ci_backstop = os.path.join(script_dir, "ci-gate-backstop.py")
    if os.path.isfile(ci_backstop) and os.access(ci_backstop, os.X_OK):
        parts.append("  ✓ ci-gate-backstop.py（CI 兜底）")
    if not parts:
        return ""
    return "\n".join(parts)


def _files_identical(a, b):
    """cmp -s 等价：逐字节比较。"""
    try:
        with open(a, "rb") as f1, open(b, "rb") as f2:
            return f1.read() == f2.read()
    except OSError:
        return False


def _check_copy_drift(script_dir):
    """检测项目 scripts/ 本地副本与权威版本漂移（等价 sh 的 _check_copy_drift）。

    权威版本 = script_dir（agate/scripts/）；项目副本 = 当前目录的 scripts/。
    """
    for script in _DRIFT_SCRIPTS:
        local = os.path.join("scripts", script)
        auth = os.path.join(script_dir, script)
        if os.path.isfile(local) and os.path.isfile(auth) and not _files_identical(local, auth):
            sys.stderr.write(
                f"⚠️  scripts/{script} 与 agate 权威版本不一致——本地副本可能已过期，建议改用 "
                "{agate_root}/scripts/ 或转发脚本\n"
            )


def main():
    script_real = os.path.realpath(__file__)
    script_dir = os.path.dirname(script_real)
    if not script_dir:
        sys.stderr.write("GATE: 无法解析脚本路径（非 git 仓库或非标准安装？）\n")
        sys.exit(1)

    agate_repo = _find_git_root(script_dir)
    if not agate_repo:
        sys.exit(1)

    current_tag = _git(agate_repo, ["describe", "--tags", "--abbrev=0"], "untagged")
    branch = _git(agate_repo, ["branch", "--show-current"], "?")
    head_sha = _git(agate_repo, ["rev-parse", "--short", "HEAD"], "?")
    recent_commits = _indent_lines(_git(agate_repo, ["log", "--oneline", "-3"]))

    guards = _build_guards(script_dir)
    _check_copy_drift(script_dir)

    lines = [
        "=== agate 当前状态 ===",
        "",
        f"版本：{current_tag}",
        f"分支：{branch}",
        f"HEAD：{head_sha}",
        "",
        "最近 3 commits：",
        recent_commits,
        "",
        "防护机制（pre-commit + CI）：",
        guards,
        "",
        "快速版本对比：python3 ~/.agate/scripts/agate-changes.py [since-tag]",
        "默认输出自上一个 tag 起的 commit + 受影响的协议文件。",
        f"例：python3 ~/.agate/scripts/agate-changes.py {current_tag}",
        "查远端更新：python3 ~/.agate/scripts/agate-changes.py --check-upstream",
        "",
        "=== 启动时建议 ===",
        "",
        "1. 第一行：上面这一段（确认协议版本 + 防护机制就位）",
        "2. 读 ~/.agate/AGENTS.md（协议本体入口指引）",
        f"3. 读 ~/.agate/CHANGELOG.md（{current_tag} 段，了解自上次会话以来发生了什么）",
        "4. 按 orchestrator-template.md mapping 表读当前阶段卡片，按需查阅 Fallback reference 节",
        "",
    ]
    out = "\n".join(lines) + "\n"
    sys.stdout.buffer.write(out.encode("utf-8"))


if __name__ == "__main__":
    main()
