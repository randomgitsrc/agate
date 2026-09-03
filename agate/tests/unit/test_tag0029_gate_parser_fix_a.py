# tests/unit/test_tag0029_gate_parser_fix_a.py — TAG0029 P3-A 批（BDD-1~3）
# 被测 ① agate/scripts/agate-read-gate-commands.py（值清洗旧语义：双 strip，
# 不剥行内注释、不校验引号闭合）+ 被测 ② check-tdd-red.py judge_result
# （exit 2 无显式分支，旧语义落末尾 red-light exit 0）。
# 真实调用：解析器走子进程（GATE_FILE env）+ judge_result 走 importlib 真实加载，不 mock。
# 平台无关：tmp_path；解释器经 python_exe fixture；shell 经 bash fixture。
# BDD-4~9 由 B 批另派，本文件不覆盖。

import importlib.util
import json
import sys


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


def _load_judge(agate_scripts):
    """importlib 加载真实 check-tdd-red 模块（连字符文件名），返回 judge_result。"""
    scripts_str = str(agate_scripts)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)
    path = agate_scripts / "check-tdd-red.py"
    spec = importlib.util.spec_from_file_location("check_tdd_red_real", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.judge_result


def _judge_payload(raw_output):
    """exit 2 + 零运行器统计的 formatter JSON（命令串本身语法错误，无运行器产出）。"""
    return json.dumps(
        {
            "exit_code": 2,
            "failed": 0,
            "errors": 0,
            "syntax_errors": [],
            "import_errors": [],
            "name_errors": [],
            "raw_output": raw_output,
        }
    )


# ================= BDD-1: 行内注释剥离 =================


def test_tag0029_bdd_1_inline_comment_stripped_to_pure_command(
    python_exe, run_cli, agate_scripts, tmp_path, bash
):
    """BDD-1：带行内注释的命令值须解析出纯命令且可被 shell 执行。"""
    result = _run_parser(
        python_exe,
        run_cli,
        agate_scripts,
        '  P3: "echo hi # inline comment"\n',
        tmp_path,
        "bdd1",
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["commands"][0]["cmd"] == "echo hi"
    shell = run_cli(bash, "-c", data["commands"][0]["cmd"])
    assert shell.returncode != 2
    assert "EOF" not in shell.stderr
    assert ("untermi" + "nated") not in shell.stderr


# ================= BDD-2: 引号未闭合 fail-closed =================


def test_tag0029_bdd_2_unclosed_quote_fails_closed(
    python_exe, run_cli, agate_scripts, tmp_path
):
    """BDD-2：引号未闭合的命令值须报解析错误，不产出残渣命令串。"""
    result = _run_parser(
        python_exe,
        run_cli,
        agate_scripts,
        '  P3: "echo hi\n',
        tmp_path,
        "bdd2",
    )
    assert result.returncode != 0
    assert "解析错误" in result.stderr
    assert '"cmd"' not in result.output


# ================= BDD-3: exit 2 判 A 类（双 locale） =================


def test_tag0029_bdd_3_exit2_chinese_syntax_is_a_class(agate_scripts):
    """BDD-3 中文：exit 2 + 语法文案 + 零运行器统计 → 判 exit 1。"""
    judge = _load_judge(agate_scripts)
    raw_cn = "bash: 寻找匹配的引号时遇到了未预期的 EOF"
    assert judge(_judge_payload(raw_cn), "") == 1


def test_tag0029_bdd_3_exit2_english_syntax_is_a_class(agate_scripts):
    """BDD-3 英文：exit 2 + 语法文案 + 零运行器统计 → 判 exit 1。"""
    judge = _load_judge(agate_scripts)
    raw_en = "bash: syntax error: unexpected EOF while looking for matching `'"
    assert judge(_judge_payload(raw_en), "") == 1
