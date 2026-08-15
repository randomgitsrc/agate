#!/usr/bin/env python3
"""ci-gate-backstop.py — CI gate backstop（P1.3）

push 时重跑 gate，与 .gate-result.json 对照。
防止 git commit --no-verify 绕过 hook。

退出码：0 = 通过; 1 = 失败
"""

import json
import os
import subprocess
import sys
from pathlib import Path

_AGATE_ROOT = Path(__file__).resolve().parent.parent


def _run_python(args: list) -> list:
    return [sys.executable, *args]


def run_gate(phase: str, task_dir: str) -> tuple[int, str]:
    script = _AGATE_ROOT / "scripts/check-gate.py"
    if not script.exists():
        return 2, "check-gate.py not found"
    result = subprocess.run(
        _run_python([str(script), phase, task_dir]),
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return result.returncode, result.stderr + result.stdout


def detect_ci_platform() -> str | None:
    if os.environ.get("GITEA_ACTIONS") == "true":
        return "gitea"
    if os.environ.get("GITLAB_CI") == "true":
        return "gitlab"
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return "github"
    return None


def get_pr_metadata(platform: str) -> dict:
    if platform == "gitlab":
        return {
            "iid": os.environ.get("CI_MERGE_REQUEST_IID", ""),
            "source_branch": os.environ.get("CI_MERGE_REQUEST_SOURCE_BRANCH_NAME", ""),
            "target_branch": os.environ.get("CI_MERGE_REQUEST_TARGET_BRANCH_NAME", ""),
            "project_id": os.environ.get("CI_PROJECT_ID", ""),
        }
    if platform in ("github", "gitea"):
        event_path = os.environ.get("GITHUB_EVENT_PATH", "")
        if event_path and Path(event_path).exists():
            with open(event_path, encoding="utf-8") as f:
                return json.load(f)
        return {}
    return {}


def resolve_tasks_dir(project_root: str) -> str:
    """通过工作区解析器取 tasks 基目录（与 bash 侧共用同一解析逻辑，BDD-13）。

    批次 0 改造：改调 agate_common.resolve_workspace（消除对 agate-workspace-resolve.sh
    的 bash subprocess）。解析器不存在时（旧 AGATE_ROOT）退回 env/default，保证向后兼容。
    """
    try:
        import agate_common
    except ImportError:
        return str(Path(project_root) / os.environ.get("AGATE_TASKS_DIR", "docs/tasks"))
    _workspace, tasks_dir = agate_common.resolve_workspace(project_root)
    return str(tasks_dir)


def _read_p1_change_type(task_dir: str) -> str:
    """读 P1-requirements.md 的 change_type（TAG0002，复用 agate-md-field-get.py 通道）。

    返回 "refactor"（或空字符串）。文件不存在/读取失败时静默返回空——缺省视为功能任务。
    """
    if not task_dir:
        return ""
    p1_file = Path(task_dir) / "P1-requirements.md"
    if not p1_file.exists():
        return ""
    field_get = _AGATE_ROOT / "scripts/agate-md-field-get.py"
    if not field_get.exists():
        return ""
    env = dict(os.environ)
    env["FILE"] = str(p1_file)
    try:
        result = subprocess.run(
            ["python3", str(field_get), "change_type"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=30,
        )
    except subprocess.SubprocessError:
        return ""
    return result.stdout.strip()


def main() -> int:
    platform = detect_ci_platform()
    print(f"CI platform: {platform}")
    if platform is None:
        print("SKIP: 未识别的 CI 平台（非 Gitea/GitLab/GitHub），backstop 不生效")
        return 0

    repo_root = Path.cwd()
    state_file = repo_root / ".state.yaml"
    gate_result = repo_root / ".gate-result.json"

    if not state_file.exists():
        print("SKIP: 无 .state.yaml，非 agate 项目")
        return 0

    try:
        import yaml
        with open(state_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        phase = data.get("phase", "")
        task_id = data.get("task_id", "")
    except Exception:
        print("SKIP: 无法读取 .state.yaml")
        return 0

    if not phase or phase in ("PAUSED", "READY", "DONE", ""):
        print(f"SKIP: phase={phase}，无 gate 需要对照")
        return 0

    tasks_dir = resolve_tasks_dir(str(repo_root))
    task_dir = str(Path(tasks_dir) / task_id) if task_id else ""
    ci_exit, _ci_output = run_gate(phase, task_dir)

    if phase == "P3":
        # P3 红灯检查独立跑（check-gate.py P3 只检查文件存在）
        # 必须在 .gate-result.json 存在性判断之前执行——
        # --no-verify 场景（无 .gate-result.json）正是 P3 兜底要覆盖的核心场景
        # TAG0002 [SCOPE+]: refactor 任务跳过 TDD 红灯（P2-design.md §3.4）——
        # 重构无新功能断言，测试套件本就全绿，check-tdd-red 的 exit 2 绿灯会被误判 FAIL。
        # change_type 读 P1-requirements.md frontmatter（复用 agate-md-field-get.py 读取通道）。
        is_refactor = _read_p1_change_type(task_dir) == "refactor"
        if is_refactor:
            print("SKIP: refactor 任务，TDD 红灯不适用（回归口径由 P5/P6 全量回归兜底）")
            return 0
        # check-tdd-red.py exit 语义：
        #   0 = 真红灯（符合 TDD）→ 通过
        #   1 = 假红灯（测试代码自身 bug）→ FAIL
        #   2 = 绿灯（实现先于测试，违反 TDD）→ FAIL
        #   3 = 无测试运行器 → WARN（CI 环境可能未装测试框架，主 Agent 已手动确认过红灯）
        tdd_script = Path(os.environ.get("AGATE_TDD_RED_SCRIPT", str(_AGATE_ROOT / "scripts/check-tdd-red.py")))
        if tdd_script.exists():
            tdd_result = subprocess.run(
                _run_python([str(tdd_script), task_dir]),
                capture_output=True, text=True, encoding="utf-8", errors="replace"
            )
            tdd_exit = tdd_result.returncode
            tdd_output = tdd_result.stderr + tdd_result.stdout
            if tdd_exit == 0:
                print("OK: P3 check-tdd-red.py exit=0（真红灯，符合 TDD）")
            elif tdd_exit == 2:
                print("FAIL: P3 check-tdd-red.py exit=2（绿灯，实现先于测试，违反 TDD）")
                print(tdd_output)
                return 1
            elif tdd_exit == 1:
                print("FAIL: P3 check-tdd-red.py exit=1（假红灯，测试代码自身有 bug）")
                print(tdd_output)
                return 1
            else:
                print(f"WARN: P3 check-tdd-red.py exit={tdd_exit}（无测试运行器，CI 环境可能未装测试框架——主 Agent 已手动确认过红灯）")
        else:
            print("WARN: check-tdd-red.py 不存在，P3 红灯检查跳过")

    if not gate_result.exists():
        if ci_exit == 1:
            print(f"FAIL: gate 未通过（无 .gate-result.json，CI 重跑 exit={ci_exit}）")
            return 1
        print(f"WARN: 无 .gate-result.json（可能 --no-verify 跳过），CI exit={ci_exit}")
        return 0

    with open(gate_result, encoding="utf-8") as f:
        recorded = json.load(f)

    recorded_exit = recorded.get("exit_code")
    recorded_phase = recorded.get("phase")

    if recorded_phase != phase:
        print(f"FAIL: .gate-result.json phase={recorded_phase} != .state.yaml phase={phase}")
        return 1

    if recorded_exit != ci_exit:
        print(f"FAIL: .gate-result.json exit={recorded_exit} != CI 重跑 exit={ci_exit}")
        return 1

    # timestamp 验证（防事后补写）
    # 注意：.gate-result.json 的 prev_commit_sha 是 hook 运行时的 HEAD（上一个 commit）
    # CI 里拿到的 HEAD 是本次 push 的最新 commit，两者不同是正常的
    import datetime
    recorded_ts = recorded.get("timestamp", "")
    if recorded_ts:
        try:
            ts = datetime.datetime.fromisoformat(recorded_ts.replace("Z", "+00:00"))
            commit_ts_str = subprocess.run(
                ["git", "log", "-1", "--format=%cI"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
            ).stdout.strip()
            commit_ts = datetime.datetime.fromisoformat(commit_ts_str)
            if ts > commit_ts:
                print(f"FAIL: .gate-result.json timestamp {ts} > commit {commit_ts}")
                return 1
        except Exception as e:
            # N2 修复：不静默 pass，至少在 CI 日志留痕
            print(f"WARN: timestamp 验证无法完成（{e}），跳过防补写检查")

    print(f"PASS: phase={phase} exit_code={ci_exit} 一致")

    # P6 provenance audit (CI layer)
    # 单 author WARNING：空 png 充数等场景的兜底审计
    if task_dir:
        p6_file = Path(task_dir) / "P6-acceptance.md"
        if p6_file.exists():
            try:
                blame = subprocess.run(
                    ["git", "blame", "--line-porcelain", str(p6_file)],
                    capture_output=True, text=True, encoding="utf-8", errors="replace"
                )
                authors = set()
                for line in blame.stdout.splitlines():
                    if line.startswith("author "):
                        authors.add(line.split(" ", 1)[1])
                if len(authors) == 1:
                    print(f"WARN: P6-acceptance.md 只有一个 author: {authors.pop()}（可能为主 Agent 自写，建议审查证据真实性）")
            except Exception as e:
                print(f"WARN: P6 git blame 审计无法完成（{e}）")

    # provenance 审计兜底（--no-verify 绕过 hook 时，backstop 层补跑）
    provenance_script = _AGATE_ROOT / "scripts/check-p6-provenance.py"
    if task_dir and provenance_script.exists() and Path(task_dir, "P6-acceptance.md").exists():
        prov_result = subprocess.run(
            _run_python([str(provenance_script), task_dir]),
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if prov_result.returncode == 1:
            print(f"FAIL: check-p6-provenance.py 重跑未通过：\n{prov_result.stdout}{prov_result.stderr}")
            return 1
        print("PASS: provenance 审计 CI 层重跑通过")

    return 0


if __name__ == "__main__":
    sys.exit(main())
