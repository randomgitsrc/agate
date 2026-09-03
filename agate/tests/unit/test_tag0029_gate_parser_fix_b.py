# tests/unit/test_tag0029_gate_parser_fix_b.py — TAG0029 P3-B 批（BDD-4~9）
# 被测 ① agate/scripts/agate-read-gate-commands.py 收集侧旧语义
# （key.startswith("P3") 把 P3_xxx 辅助键当测试命令收集；P4 收紧为精确键 key == "P3"）
# + 被测 ② check-platform-assumptions.py R2（旧扫描器无 fixture 目录声明豁免；
# P4 新增以 agate/tests/fixtures/ 路径段绑定的目录声明豁免，仅 R2 跳过）。
# + 文档断言 BDD-6（协议卡 gate_commands 节 P3_xxx 禁令，P4 才加，当前红）
# 与 BDD-9（本任务 P2 §4 三 scanner key 已存在，锁定绿）。
# 真实调用：解析器/扫描器走子进程（GATE_FILE env）+ 块解析走公共库真实函数，不 mock。
# 平台无关：tmp_path；解释器经 python_exe fixture；裸解释器字面全片段拼接；
# 豁免路径段用 as_posix 归一化判定（Windows 反斜杠兼容）。
# BDD-1~3 由 A 批覆盖，本文件不碰 A 批文件。
# [PROD_NOT_TOUCHED] 本阶段只写测试代码，未改动任何实现代码。

import json
import sys

_PY = "python"
_VER = "3"
# 豁免绑定：P2-design §3.4 _FIXTURE_EXEMPT_DIRS（初始含 agate/tests/fixtures/）。
# P4 实现须做"相对路径前缀"语义判定（posix 归一化后含该路径段），使 tmp_path 内建的
# 同名相对结构同样豁免；禁止退化为"含 fixture 字样就跳过"的宽匹配（R3）。
_EXEMPT_SEGMENT = "agate/tests/fixtures/"


def _run_parser(python_exe, run_cli, agate_scripts, block_text, tmp_path, name):
    """tmp_path 写 gate 块文件，GATE_FILE env 调真实解析器子进程，返回结果。"""
    p2 = tmp_path / name / "P2-design.md"
    p2.parent.mkdir(parents=True, exist_ok=True)
    p2.write_text(
        "---\nagent: test\n---\ngate_commands:\n" + block_text,
        encoding="utf-8",
    )
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-read-gate-commands.py"),
        env={"GATE_FILE": str(p2)},
    )


def _load_common(agate_scripts):
    """加载真实 agate_common 模块（块解析单点 parse_gate_commands_block）。"""
    scripts_str = str(agate_scripts)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)
    import agate_common

    return agate_common


# ================= BDD-4: P3_xxx 辅助键不收集 =================


def test_tag0029_bdd_4_p3_aux_keys_not_collected(
    python_exe, run_cli, agate_scripts, tmp_path
):
    """BDD-4：含 P3_xxx 辅助键（含 _e2e 一例）的块 → commands 不含该键条目。"""
    block = '  P3: "echo tdd"\n  P3_e2e: "playwright test"\n'
    result = _run_parser(python_exe, run_cli, agate_scripts, block, tmp_path, "bdd4")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert not any(c.get("suffix") == "_e2e" for c in data["commands"])
    assert not any("playwright" in c["cmd"] for c in data["commands"])
    assert len(data["commands"]) == 1


# ================= BDD-5: 裸 P3 收集而元键豁免（锁定绿） =================


def test_tag0029_bdd_5_bare_p3_collected_meta_exempt(
    python_exe, run_cli, agate_scripts, tmp_path
):
    """BDD-5：裸 P3 + _formatter/_timeout_seconds 三键共存 → 仅裸 P3 被收集。"""
    block = (
        '  P3: "echo tdd"\n'
        '  P3_formatter: "pytest.sh"\n'
        '  P3_timeout_seconds: "120"\n'
    )
    result = _run_parser(python_exe, run_cli, agate_scripts, block, tmp_path, "bdd5")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["commands"]) == 1
    assert data["commands"][0]["cmd"] == "echo tdd"
    assert data["commands"][0]["suffix"] == ""


# ================= BDD-6: 协议卡 P3_xxx 禁令（当前红，P4 加） =================


def test_tag0029_bdd_6_protocol_card_bans_p3_aux_keys(agate_scripts):
    """BDD-6：协议卡 gate_commands 节存在 P3_xxx 禁止声明及其原因。"""
    card = agate_scripts.parent / "phase-cards" / "P2-design.md"
    text = card.read_text(encoding="utf-8")
    start = text.find("## gate_commands")
    assert start != -1
    end = text.find("\n## ", start + 1)
    section = text[start : end if end != -1 else len(text)]
    assert "P3_" in section
    assert ("禁止" in section) or ("禁令" in section)


# ================= BDD-7: fixture 数据面豁免（当前红） =================


def test_tag0029_bdd_7_fixture_data_exempt_zero_hits(
    python_exe, run_cli, agate_scripts, tmp_path
):
    """BDD-7：豁免目录内数据文件 command 字段裸调用 → R2 无命中 + exit 0。"""
    base = tmp_path / "bdd7" / "agate" / "tests" / "fixtures"
    base.mkdir(parents=True)
    bare = _PY + _VER + " -m pytest -q tests/unit"
    line = '{"type": "tool/call", "data": {"command": "' + bare + '"}}'
    data_file = base / "logged_session.py"
    data_file.write_text(line + "\n", encoding="utf-8")
    posix_path = data_file.as_posix()
    assert _EXEMPT_SEGMENT in posix_path
    result = run_cli(
        python_exe, str(agate_scripts / "check-platform-assumptions.py"), str(base)
    )
    assert result.returncode == 0
    assert result.output == ""


# ================= BDD-8: 目录外裸调用仍拦截（锁定绿） =================


def test_tag0029_bdd_8_bare_call_outside_fixture_still_hit(
    python_exe, run_cli, agate_scripts, tmp_path
):
    """BDD-8：非豁免目录测试代码行命令位置裸调用 → R2 命中 + exit 1。"""
    work = tmp_path / "bdd8"
    work.mkdir()
    call = _PY + _VER + " -m pytest -q"
    target = work / "code_under_test.py"
    target.write_text('run_cmd = "' + call + '"\n', encoding="utf-8")
    assert _EXEMPT_SEGMENT not in target.as_posix()
    result = run_cli(
        python_exe, str(agate_scripts / "check-platform-assumptions.py"), str(target)
    )
    assert result.returncode == 1
    assert "R2" in result.output
    assert str(target) in result.output


# ================= BDD-9: 本任务 P2 三 scanner key（锁定绿） =================


def test_tag0029_bdd_9_task_p2_declares_scanner_keys(agate_scripts):
    """BDD-9：本任务 P2-design.md P3/P4 块均含扫描器命令条目。"""
    task_p2 = (
        agate_scripts.parent.parent
        / "agate-workspace"
        / "tasks"
        / "TAG0029-gate-parser-fix"
        / "P2-design.md"
    )
    text = task_p2.read_text(encoding="utf-8")
    common = _load_common(agate_scripts)
    has_block, entries = common.parse_gate_commands_block(text)
    assert has_block
    keys = dict(entries)
    assert "P3_scanner" in keys
    assert "P4_scanner" in keys
    assert "check-platform-assumptions" in keys["P3_scanner"]
    assert "check-platform-assumptions" in keys["P4_scanner"]
