# agate/tests/unit/test_card_render.py — BDD-12/13(M3) 卡片渲染化 + 稳定版隔离
#
# 被测契约（P2-design §3.6、M3-1..M3-5）：
#   BDD-12 S-3 渲染化强制：渲染产物（phase-cards 门槛/产出/派发节）与 phases.yaml 声明
#          逐字段比对一致 → check-structure-consistency.py exit 0；人为篡改 YAML 字段 → 非 0
#   BDD-13 agate-inject-card.py 渲染化兼容 + 稳定版隔离：
#          worktree 注入的 dispatch-context 卡片块与 AGATE_ROOT 解析 YAML 的渲染结果一致；
#          AGATE_ROOT 指向稳定版时，注入不被 worktree 未发布 YAML 污染（resolve_agate_root
#          四层链 env 优先；双工作区纪律 TAG0016 教训）
#   BDD-14 渲染化回归全绿 → 声明（无新测试，P5 全量回归 + P5_structure/schema/count 覆盖）
#
# 夹具：AGATE_ROOT 指向 tmp_path 假协议树；marker 输出名只存在于假 YAML，静态卡片不含
#（保证 M3 渲染器必须读 YAML 才转绿；P3 当下注入的是静态卡片 → 真红灯 B 类）。
#
# 平台无关（BDD-16）：无临时目录字面量、无软链、无裸解释器字面量；文本 I/O 显式 utf-8。

import pytest
from _rules_test_utils import make_fake_root

_START = "<!-- AGATE_CARD_START -->"
_END = "<!-- AGATE_CARD_END -->"

_TESTER_DC = (
    "---\n"
    "phase: P3\n"
    "task_id: T001\n"
    "role: test-designer\n"
    "---\n"
    "\n"
    "<dispatch_guide>\n"
    "### 目标\n"
    "写测试\n"
    "</dispatch_guide>\n"
    "\n"
    f"{_START}\n"
    "旧占位\n"
    f"{_END}\n"
)

_ANALYST_DC = (
    "---\n"
    "phase: P1\n"
    "task_id: T001\n"
    "role: analyst\n"
    "---\n"
    "\n"
    f"{_START}\n"
    "旧占位\n"
    f"{_END}\n"
)

# 只存在于假 YAML 的 marker 输出名（静态卡片不含）
_RENDER_MARKER = "P3-render-check-output.md"


def _run_structure(agate_scripts, python_exe, run_cli, proto_root):
    script = agate_scripts / "check-structure-consistency.py"
    assert script.is_file(), "check-structure-consistency.py 未实现（P4 M0 交付）——TDD 红灯锚点"
    return run_cli(python_exe, str(script), env={"AGATE_ROOT": str(proto_root)})


def _between_markers(text):
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if _START in line)
    end = next(i for i in range(start + 1, len(lines)) if _END in lines[i])
    return "\n".join(lines[start + 1:end])


def _phases_with_p3_marker(marker):
    return (
        "schema_version: 1\n"
        "phases:\n"
        "  - id: P1\n"
        "    name: 需求基线\n"
        "    exec_role: analyst\n"
        "    outputs:\n"
        "      - {file: P1-requirements.md, required: true}\n"
        "    retry_cap: 3\n"
        "  - id: P3\n"
        "    name: 测试设计\n"
        "    exec_role: test-designer\n"
        "    outputs:\n"
        f"      - {{file: {marker}, required: true}}\n"
        "    retry_cap: 2\n"
    )


@pytest.mark.windows_smoke
def test_bdd_12_rendered_card_matches_yaml_exit_0(agate_scripts, python_exe, run_cli, tmp_path):
    """M3 渲染化后渲染产物（产出/派发节）与 phases.yaml 声明一致 → S-3 通过 exit 0。"""
    root = make_fake_root(tmp_path)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 0, result.output
    assert "S3" in result.output, "未输出 S-3 检查项（渲染一致判定缺失）"


def test_bdd_12_tampered_yaml_detected(agate_scripts, python_exe, run_cli, tmp_path):
    """人为篡改 YAML 一个字段（P3 输出名）→ S-3 渲染一致破坏 → exit 非 0。"""
    root = make_fake_root(tmp_path, phases_text=_phases_with_p3_marker(_RENDER_MARKER))
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, "篡改 YAML 未被 S-3 检出（渲染一致强制未生效）"


def test_bdd_13_inject_renders_from_yaml(agate_scripts, python_exe, run_cli, tmp_path):
    """agate-inject-card.py 渲染化兼容：注入的 P3 卡片块须含 AGATE_ROOT YAML 声明的输出名
    （P3 当下注入静态卡片 → 无 marker → 真红灯）。"""
    root = make_fake_root(
        tmp_path,
        phases_text=_phases_with_p3_marker(_RENDER_MARKER),
        add_files={"phase-cards/P3-tdd.md": "# P3 测试设计\n叙事节静态文本\n"},
        agate_scripts=agate_scripts,
    )
    taskdir = tmp_path / "task"
    taskdir.mkdir()
    (taskdir / "P3-dispatch-context-test-designer.md").write_text(_TESTER_DC, encoding="utf-8")

    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-inject-card.py"),
        "P3",
        str(taskdir),
        env={"AGATE_ROOT": str(root)},
    )
    assert result.returncode == 0, f"注入失败：{result.output}"
    injected = _between_markers((taskdir / "P3-dispatch-context-test-designer.md").read_text(encoding="utf-8"))
    assert _RENDER_MARKER in injected, (
        "注入卡片块未含 YAML 渲染的输出名（agate-inject-card 渲染化未实现）"
    )


def test_bdd_13_stable_isolation_not_polluted(agate_scripts, python_exe, run_cli, tmp_path):
    """稳定版隔离（BDD-13 后半）：双工具两次注入——worktree 注入反映自身 YAML；
    稳定版（AGATE_ROOT=稳定版假树）重复注入不被 worktree 未发布 YAML 污染
    （双工作区纪律；TAG0016 教训）。"""
    stable_marker = "STABLE-RENDER-MARKER-42"
    worktree_marker = "WORKTREE-UNIQUE-DELTA-77"

    stable_root = make_fake_root(
        tmp_path / "stable",
        phases_text=_phases_with_p3_marker(stable_marker),
        add_files={"phase-cards/P3-tdd.md": "# P3 测试设计\n稳定版叙事\n"},
        agate_scripts=agate_scripts,
    )
    # worktree 假树：未发布 YAML 与稳定版不同（标记名差异化）
    worktree_root = make_fake_root(
        tmp_path / "worktree",
        phases_text=_phases_with_p3_marker(worktree_marker),
        add_files={"phase-cards/P3-tdd.md": "# P3 测试设计\nworktree 未发布叙事\n"},
        agate_scripts=agate_scripts,
    )
    taskdir = tmp_path / "task_iso"
    taskdir.mkdir()
    dc = taskdir / "P3-dispatch-context-test-designer.md"
    dc.write_text(_TESTER_DC, encoding="utf-8")

    # ① worktree 工具注入：卡片块应含 worktree 自身 YAML 渲染的输出名
    r1 = run_cli(
        python_exe,
        str(agate_scripts / "agate-inject-card.py"),
        "P3",
        str(taskdir),
        env={"AGATE_ROOT": str(worktree_root)},
    )
    assert r1.returncode == 0, f"worktree 注入失败：{r1.output}"
    injected1 = _between_markers(dc.read_text(encoding="utf-8"))
    assert worktree_marker in injected1, "worktree 注入未含自身 YAML 渲染内容"

    # ② 稳定版工具重复注入：应含稳定版 YAML 渲染的输出名，且不含 worktree 未发布 marker
    r2 = run_cli(
        python_exe,
        str(agate_scripts / "agate-inject-card.py"),
        "P3",
        str(taskdir),
        env={"AGATE_ROOT": str(stable_root)},
    )
    assert r2.returncode == 0, f"稳定版注入失败：{r2.output}"
    injected2 = _between_markers(dc.read_text(encoding="utf-8"))
    assert stable_marker in injected2, "稳定版注入未含稳定版 YAML 渲染内容"
    assert worktree_marker not in injected2, "稳定版注入被 worktree 未发布 YAML 污染"
