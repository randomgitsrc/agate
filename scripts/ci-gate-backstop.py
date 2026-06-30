#!/usr/bin/env python3
"""ci-gate-backstop.py — CI gate backstop（P1.3）

push 时重跑 gate，与 .gate-result.json 对照。
防止 git commit --no-verify 绕过 hook。

退出码：0 = 通过; 1 = 失败
"""

import json
import subprocess
import sys
from pathlib import Path


def run_gate(phase: str, task_dir: str) -> tuple[int, str]:
    script = Path("scripts/check-gate.sh")
    if not script.exists():
        return 2, "check-gate.sh not found"
    result = subprocess.run(
        ["bash", str(script), phase, task_dir],
        capture_output=True, text=True
    )
    return result.returncode, result.stderr + result.stdout


def main() -> int:
    repo_root = Path.cwd()
    state_file = repo_root / ".state.yaml"
    gate_result = repo_root / ".gate-result.json"

    if not state_file.exists():
        print("SKIP: 无 .state.yaml，非 agate 项目")
        return 0

    try:
        import yaml
        with open(state_file) as f:
            data = yaml.safe_load(f)
        phase = data.get("phase", "")
        task_id = data.get("task_id", "")
    except Exception:
        print("SKIP: 无法读取 .state.yaml")
        return 0

    if not phase or phase in ("PAUSED", "READY", "DONE", ""):
        print(f"SKIP: phase={phase}，无 gate 需要对照")
        return 0

    task_dir = str(repo_root / "docs/tasks" / task_id) if task_id else ""
    ci_exit, ci_output = run_gate(phase, task_dir)

    if not gate_result.exists():
        if ci_exit == 1:
            print(f"FAIL: gate 未通过（无 .gate-result.json，CI 重跑 exit={ci_exit}）")
            return 1
        print(f"WARN: 无 .gate-result.json（可能 --no-verify 跳过），CI exit={ci_exit}")
        return 0

    with open(gate_result) as f:
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
                capture_output=True, text=True, check=True
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
                    capture_output=True, text=True
                )
                authors = set()
                for line in blame.stdout.splitlines():
                    if line.startswith("author "):
                        authors.add(line.split(" ", 1)[1])
                if len(authors) == 1:
                    print(f"WARN: P6-acceptance.md 只有一个 author: {authors.pop()}（可能为主 Agent 自写，建议审查证据真实性）")
            except Exception as e:
                print(f"WARN: P6 git blame 审计无法完成（{e}）")

    return 0


if __name__ == "__main__":
    sys.exit(main())
