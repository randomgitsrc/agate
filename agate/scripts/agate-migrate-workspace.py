#!/usr/bin/env python3
"""agate-migrate-workspace.py — 强制迁移工具（TAG0003 v2.0）

从 agate-migrate-workspace.sh 迁移（TAG0010 批次 1d）。用法：
  python3 ~/.agate/scripts/agate-migrate-workspace.py [--to <workspace>]

流程（P2-design.md §3.2）：
  1. 解析工作区目标（复用 resolve_workspace，--to 覆盖）
  2. 源检测：docs/tasks 不存在或为空 → no-op exit 0（空目录 rmdir 清理，BDD-19）
  3. 目标冲突检测：工作区 tasks 已存在且非空 → exit 1 防覆盖
  4. 迁移：目录级 git mv（保留历史，BDD-8）；仓库外失败（exit 128）→ fallback 普通 mv + WARNING
  5. 归档迁移：docs/archived → {workspace}/archived（BDD-18，相对结构保留）
  6. 幂等：迁移后重复运行在第 2 步即 no-op（BDD-9）
  7. 迁移后校验：清单对照 + 摘要输出（不静默，BDD-10）
  8. 迁移完成后 commit rename（git mv 只暂存，commit 才能让 git log --follow 追溯）

迁移说明：source agate-workspace-resolve.sh → agate_common.resolve_workspace；
--to 解析 → 手写循环（保持 CLI 契约）；realpath -m → os.path.realpath；
find | wc -l → os.walk 计数；git mv / 普通 mv fallback → subprocess / shutil.move；
自动 commit（core.hooksPath=/dev/null）→ subprocess.run(cwd=project_root)。
"""

import os
import shutil
import subprocess
import sys

from agate_common import resolve_workspace


def _out(msg):
    """stdout UTF-8 逐字输出（等价 sh echo，Windows 代码页安全）。"""
    sys.stdout.buffer.write((msg + "\n").encode("utf-8"))


def _err(msg):
    """stderr 输出（等价 sh `echo ... >&2`）。"""
    sys.stderr.write(msg + "\n")


def _count_files(path):
    """find "$path" -type f | wc -l 等价：统计常规文件数（目录不存在时 0）。"""
    total = 0
    for _root, _dirs, files in os.walk(path):
        total += len(files)
    return total


def _git_mv(project_root, src, dst):
    """git mv src dst（cwd=project_root），成功返回 True，stderr 静默（同 2>/dev/null）。"""
    proc = subprocess.run(
        ["git", "mv", src, dst],
        cwd=project_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc.returncode == 0


def _plain_mv(project_root, src, dst):
    """普通 mv src dst 等价（跨文件系统安全），失败返回 False。"""
    try:
        shutil.move(os.path.join(project_root, src), dst)
    except OSError:
        return False
    return True


def main():
    project_root = os.getcwd()

    # 解析可选 --to <workspace>（覆盖工作区目标）
    ws_override = ""
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--to":
            if i + 1 < len(args):
                ws_override = args[i + 1]
            if not ws_override:
                _err("GATE MIGRATE: --to 后需跟工作区路径")
                sys.exit(2)
            i += 2
        else:
            _err("GATE MIGRATE: 未知参数 {}（用法：python3 agate-migrate-workspace.py [--to <workspace>]）".format(args[i]))
            sys.exit(2)

    # 复用解析器取默认工作区（resolve_workspace 只返回，不创建目录）
    workspace, tasks_dir = resolve_workspace(project_root)

    if ws_override:
        if os.path.isabs(ws_override):
            workspace = os.path.realpath(ws_override)
        else:
            workspace = os.path.realpath(os.path.join(project_root, ws_override))
        tasks_dir = os.path.join(workspace, "tasks")

    docs_tasks = os.path.join(project_root, "docs/tasks")
    docs_arch = os.path.join(project_root, "docs/archived")
    migrated = []
    git_mv_staged = False
    tasks_migrated = False
    arch_migrated = False

    # 迁移单个源目录：冲突检测 → 目录级 git mv → 仓库外 fallback 普通 mv + WARNING
    def migrate_dir(src, dst, label, marker):
        nonlocal git_mv_staged, tasks_migrated, arch_migrated

        # 目标已存在且为空目录：先移除，避免 git mv 走"移入"语义产生 {dst}/src/... 嵌套（P4-review F3 观察）
        if os.path.isdir(dst) and not os.listdir(dst):
            try:
                os.rmdir(dst)
            except OSError:
                pass

        # 目标冲突检测：已存在且非空 → 防覆盖 exit 1（不自动合并）
        if os.path.isdir(dst) and os.listdir(dst):
            _err("GATE MIGRATE: 目标 {} 已存在且非空（{}）——为避免覆盖，迁移中止。请先处理冲突后重试。".format(label, dst))
            sys.exit(1)

        file_count = _count_files(src)

        # 目录级 git mv：目标在仓库内时保留 git 历史（物理移动含 gitignore 的 .state.yaml 与未追踪文件）
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if _git_mv(project_root, src, dst):
            _out("迁移：{}（{} → {}，{} 个文件，git mv 保留历史）".format(label, src, dst, file_count))
            migrated.append("{}:{} ".format(label, dst))
            git_mv_staged = True
            if marker == "tasks":
                tasks_migrated = True
            else:
                arch_migrated = True
            return

        # git mv 失败（典型：目标在仓库外 exit 128）→ fallback 普通 mv + WARNING
        if _plain_mv(project_root, src, dst):
            _err("WARNING: 工作区在 git 仓库外，{} 已用普通 mv 移动（{} → {}）——文件已移动，但 git 历史无法在新路径追溯（外部工作区固有限制）".format(label, src, dst))
            migrated.append("{}:{}(fallback) ".format(label, dst))
            return

        _err("GATE MIGRATE: 无法迁移 {}（git mv 与 mv 均失败）：{}".format(label, src))
        sys.exit(1)

    # 源检测（docs/tasks）：不存在或为空 → 空目录 rmdir 清理，不迁移
    if os.path.isdir(docs_tasks):
        if os.listdir(docs_tasks):
            migrate_dir(docs_tasks, tasks_dir, "docs/tasks → 工作区 tasks", "tasks")
        else:
            try:
                os.rmdir(docs_tasks)
            except OSError:
                pass
            _out("迁移：docs/tasks 为空目录，已清理（rmdir）")

    # 归档迁移（docs/archived → {workspace}/archived，相对结构保留，BDD-18）
    if os.path.isdir(docs_arch):
        if os.listdir(docs_arch):
            migrate_dir(docs_arch, os.path.join(workspace, "archived"), "docs/archived → 工作区 archived", "archived")
        else:
            try:
                os.rmdir(docs_arch)
            except OSError:
                pass
            _out("迁移：docs/archived 为空目录，已清理（rmdir）")

    # 幂等：无任何迁移动作 → no-op exit 0（BDD-19，不建错目录）
    if not migrated:
        _out("迁移：docs/tasks 与 docs/archived 均不存在或为空，无需迁移（no-op）")
        sys.exit(0)

    # 迁移后提交（BDD-8）：git mv 只暂存 rename，commit 才能让 git log --follow 在新路径追溯旧 commit
    #
    # ⚠️ 自动 commit 风险标注（P4-review F1/F2）：
    #  ① 裸 `git commit` 会触发项目自身 pre-commit hook——迁移任务内嵌的旧版 dispatch-context 卡片 hash
    #     与当前协议不一致，会被 pre-commit-gate.sh 的卡片校验拦截 → 自动 commit 静默失败（BDD-8 不满足）。
    #     故用 `git -c core.hooksPath=/dev/null`（git 官方临时禁用 hook 的方式）执行机械性 rename commit。
    #  ② 全量 index commit 风险：裸 commit 会把迁移前已暂存的无关改动一并提交。故 pathspec 限定只提交
    #     迁移目录（旧路径 docs/tasks|docs/archived 与对应新路径成对——rename 必须 delete+add 同 commit 才能表达，
    #     只给新路径会产生 partial commit，旧路径残留在 HEAD）。其余已暂存改动保留不动。
    #     迁移前仍建议先 commit 或 unstage 无关暂存改动（见 UPGRADING.md v0.41.0 节）。
    #  ③ 不再吞 commit 失败：失败时输出显式错误 + exit 1，而非打印"迁移完成"误导用户。
    commit_paths = []
    if tasks_migrated:
        commit_paths += ["docs/tasks", tasks_dir]
    if arch_migrated:
        commit_paths += ["docs/archived", os.path.join(workspace, "archived")]
    if git_mv_staged:
        proc = subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", "commit", "-qm",
             "chore(workspace): migrate legacy docs/tasks layout to workspace", "--"] + commit_paths,
            cwd=project_root,
        )
        if proc.returncode == 0:
            _out("迁移：已自动 commit rename（跳过项目自身 pre-commit hook，git 历史可追溯 BDD-8）")
        else:
            _err("GATE MIGRATE: 迁移已移动文件，但自动 commit 失败（BDD-8 git 历史未保留）")
            _err("      请手工完成迁移 commit：git add '{}' '{}' && git commit -m \"chore(workspace): migrate legacy docs/tasks layout to workspace\"".format(tasks_dir, os.path.join(workspace, "archived")))
            sys.exit(1)
    else:
        # 迁移走 fallback（外部工作区，rename 未进暂存区），但存在其他已暂存改动 → 不误提交，仅提示
        proc = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.stdout and proc.stdout.strip():
            _err("WARNING: 迁移目录之外存在其他已暂存改动——为避免误提交无关内容，自动 commit 已跳过，请手工处理暂存区。")

    # 迁移后校验 + 摘要（不静默，BDD-10）
    _out("迁移完成。")
    _out("  工作区根：{}".format(workspace))
    _out("  tasks 文件数：{}".format(_count_files(tasks_dir)))
    if os.path.isdir(os.path.join(workspace, "archived")):
        _out("  archived 文件数：{}".format(_count_files(os.path.join(workspace, "archived"))))
    if not ws_override and workspace != os.path.join(project_root, "agate-workspace"):
        _out("  提示：工作区位于默认 agate-workspace 之外，可在项目根写 .agate.env（AGATE_WORKSPACE={}）持久化配置。".format(workspace))
    sys.exit(0)


if __name__ == "__main__":
    main()
