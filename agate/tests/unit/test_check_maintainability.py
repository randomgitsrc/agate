# tests/unit/test_check_maintainability.py — 维护性反模式检测器（RM-AG0046，TAG0026 P3）
# 被测：agate/scripts/check-maintainability.py 的 check_maintainability(task_dir) -> dict（尚未实现，P4 写）。
# 契约（P2-design.md §3.1，BDD 判定锚见 P1-requirements.md §7）：
#   返回 {"git_ok": bool, "violations": [...], "god_file_count": N, "fuzzy_boundary_count": M}
#   violation 条目：god-file → {"type": "god-file", "file": <norm_rel>, "detail": ...}；
#                   fuzzy-boundary → {"type": "fuzzy-boundary", "file": <norm_rel>, "line": N, "detail": ...}
#   配置：{repo_root}/agate-workspace/maintainability.yaml（god_file_threshold / fuzzy_patterns.python /
#         fuzzy_patterns.typescript），缺失/坏值全默认（N=1000）
#   CLI：python3 check-maintainability.py TASK_DIR → exit 0（无 violation 或 git 不可用）/ 1（有 violation）
# 覆盖分组（P2-design.md §5.1）：G1 god-file 跨越（BDD-1）/ G2 存量不误伤（BDD-2）/
#   G3 fuzzy Python（BDD-3）/ G4 存量行不误伤（BDD-4）/ G5 阈值可配置（BDD-5）/
#   G6 配置缺失兜底（BDD-6）/ G7 路径平台无关（BDD-11）/ G8 移动假阳性诚实行为（BDD-12）/
#   G9 P4 数据源对齐（BDD-13）/ G10 模块契约（实现导航）。
# TDD 红灯形态（check-tdd-red 口径适配，TAG0026 P3）：
#   本文件对"模块未实现"用 skipif 整组跳过——收集期 collect-error 会在 raw_output 留下
#   ModuleNotFoundError 文本，check-tdd-red 无 formatter 分支（judge_result :97）将其判为
#   A 类（exit 1 假红灯）。红灯由 M10 文件的 assertion 失败承载（failed>0 → classic
#   red-light exit 0 真红灯）。P4 实现落地后本文件自动解除 skip 参与全量验证。
# 平台无关：全部 tmp_path；git 经 conftest git_repo fixture；解释器经 python_exe 探测；
#   AGATE_ROOT 经 agate_root fixture；不硬编码 /home/... 绝对路径。

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

# G10：模块契约组在此做单源 import（其余场景复用）
_MOD = "check_maintainability"


def _load_module_file(module_file):
    """按文件路径 importlib 加载检测器模块（连字符文件名 check-maintainability.py
    无法按模块名 import——import 语句的模块名标识符不含连字符；参照 check-gate.py
    侧兜底形态，主 Agent 定夺 1：探测被测对象的机械路径修复，断言语义不变）。"""
    spec = importlib.util.spec_from_file_location(_MOD, module_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# 收集期探测：模块未实现（P4 才写）→ 本文件全部用例 skip。
# 路径三级 parent：unit → tests → agate，再进 scripts/（原实现少算一级 parent，
# 解析到不存在的 agate/tests/scripts/，且 sys.path + import_module 机制命中不了
# 连字符文件名——均为主 Agent 定夺 1 授权修复的测试自身 bug）。
_MODULE_FILE = (
    Path(__file__).resolve().parent.parent.parent / "scripts" / "check-maintainability.py"
)
try:
    if not _MODULE_FILE.is_file():
        raise ImportError(f"check_maintainability 未实现：{_MODULE_FILE}")
    _load_module_file(_MODULE_FILE)
    _MOD_MISSING = False
except (ImportError, OSError):
    _MOD_MISSING = True

pytestmark = pytest.mark.skipif(
    _MOD_MISSING, reason="check_maintainability 未实现（P4 产出；TDD 红灯由 gate 挂载测试 assertion 承载）"
)


def _load_mod(agate_scripts):
    """按文件路径 importlib 加载 check_maintainability 模块（每次全新模块对象，
    保持原 del sys.modules + import 的新鲜语义；agate_scripts fixture 保证
    AGATE_ROOT 可经 env 覆盖——CI 无 ~/.agate 时同样成立）。"""
    module_file = Path(agate_scripts) / "check-maintainability.py"
    for name in [m for m in list(sys.modules) if m == _MOD]:
        del sys.modules[name]
    spec = importlib.util.spec_from_file_location(_MOD, module_file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MOD] = mod
    spec.loader.exec_module(mod)
    return mod


def _commit(repo, message, files=None):
    repo.commit(message, files=files)


def _write(repo, name, content):
    p = repo.path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    repo.stage(name)


def _stage(repo, name):
    repo.stage(name)


def _lines(n):
    """生成 n 行代码正文（不携带任何 fuzzy 命中词）。"""
    return "".join(f"x_{i} = {i}\n" for i in range(n))


def _god_scenario(git_repo, task_dir, before, after, name="src/big.py"):
    """god-file 场景：先 commit before 行版本，再把 staged 版本扩到 after 行。

    任务目录复制进仓库 task/（对齐 test_agate_risk_score._repo_with_staged 先例）。
    返回 (git_repo, task_dir_path)。
    """
    repo = git_repo
    repo_path = repo.path
    (repo_path / "README.md").write_text("init\n", encoding="utf-8")
    repo.commit("init")
    td = task_dir()
    shutil.copytree(td, repo_path / "task")
    _write(repo, name, _lines(before))
    _stage(repo, name)
    repo.commit("base")
    _write(repo, name, _lines(after))
    _stage(repo, name)
    return repo, repo_path / "task"


# ===== G10 模块契约（实现导航，P2-design §5.1 G10） =====


def test_g10_module_importable(agate_scripts):
    """G10：check_maintainability 模块可 import（实现导航；未实现 = 真红灯）。"""
    mod = _load_mod(agate_scripts)
    assert hasattr(mod, "check_maintainability")


def test_g10_dict_shape(
    git_repo, task_dir, agate_scripts
):
    """G10：返回 dict 形状——git_ok/violations/god_file_count/fuzzy_boundary_count 四键。"""
    _repo, td = _god_scenario(git_repo, task_dir, 5, 10, name="src/small.py")
    mod = _load_mod(agate_scripts)
    result = mod.check_maintainability(td)
    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "git_ok",
        "violations",
        "god_file_count",
        "fuzzy_boundary_count",
    }
    assert isinstance(result["git_ok"], bool)
    assert isinstance(result["violations"], list)
    assert isinstance(result["god_file_count"], int)
    assert isinstance(result["fuzzy_boundary_count"], int)


def test_g10_violation_entry_shapes(
    git_repo, task_dir, agate_scripts
):
    """G10：violation 条目形状——god-file {type,file,detail}；fuzzy-boundary {type,file,line,detail}。"""
    repo, _td = _god_scenario(git_repo, task_dir, 900, 1150)
    # 同一 staged diff 追加一个 fuzzy 新增文件（A 态即命中新增行判定；不设基线 commit——
    # 中间 commit 会把已暂存的 big.py@1150 一并收进 HEAD，god-file 场景随之消失）
    p = repo.path / "src" / "fz.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("try:\n    pass\nexcept:\n    pass\n", encoding="utf-8")
    _stage(repo, "src/fz.py")

    mod = _load_mod(agate_scripts)
    result = mod.check_maintainability(repo.path / "task")
    types = {v.get("type") for v in result["violations"]}
    assert "god-file" in types
    assert "fuzzy-boundary" in types
    for v in result["violations"]:
        if v["type"] == "god-file":
            assert set(v.keys()) == {"type", "file", "detail"}
            assert "\\" not in v["file"]  # file 为归一化相对路径
        if v["type"] == "fuzzy-boundary":
            assert set(v.keys()) == {"type", "file", "line", "detail"}
            assert isinstance(v["line"], int) and v["line"] >= 1


def test_g10_git_channel_fail_closed(
    git_repo, task_dir, agate_scripts, tmp_path, monkeypatch
):
    """G10：git 通道失败 fail-closed——git_ok=False（对齐 score_task 语义，不静默降级）。"""
    repo, _td = _god_scenario(git_repo, task_dir, 5, 10, name="src/small.py")
    mod = _load_mod(agate_scripts)
    orig = mod.run_git

    def _broken_run_git(args, cwd=None):
        # run_git 真实契约 = (returncode, stdout) 元组（agate_common.run_git）——
        # fake 按契约返回失败元组（原 fake 返回对象，测试从未执行过才暴露的形状错位）
        return 128, ""

    monkeypatch.setattr(mod, "run_git", _broken_run_git)
    result = mod.check_maintainability(repo.path / "task")
    assert result["git_ok"] is False
    assert result["violations"] == []
    assert orig is not None


def test_g10_cli_exit_codes(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """G10：CLI exit code——有 violation → 1；无 violation → 0（exit code 唯一判定）。"""
    repo, _td_hit = _god_scenario(git_repo, task_dir, 900, 1150)
    result_hit = run_cli(
        python_exe, str(agate_scripts / "check-maintainability.py"), "task", cwd=str(repo.path)
    )
    assert result_hit.returncode == 1
    assert "big.py" in result_hit.output

    # 无 violation → 0：清空暂存区（P6 形态对照，BDD-13 同机制）后复跑 CLI
    repo.git("reset", "-q")
    result_clean = run_cli(
        python_exe,
        str(agate_scripts / "check-maintainability.py"),
        str(repo.path / "task"),
        cwd=str(repo.path),
    )
    assert result_clean.returncode == 0


@pytest.mark.windows_smoke
def test_bdd_1_god_file_crossing(
    git_repo, task_dir, agate_scripts
):
    """BDD-1：900 行文件 staged 后扩到 1150 行（before<1000 and after>=1000）→ violations 含该文件。"""
    _repo, td = _god_scenario(git_repo, task_dir, 900, 1150)
    mod = _load_mod(agate_scripts)
    result = mod.check_maintainability(td)
    assert result["git_ok"] is True
    god_files = [
        v for v in result["violations"] if v.get("type") == "god-file"
    ]
    assert any(v.get("file") == "src/big.py" for v in god_files), (
        f"god-file 违规未含 src/big.py: {result['violations']!r}"
    )
    assert result["god_file_count"] >= 1


def test_bdd_2_existing_god_file_not_flagged(
    git_repo, task_dir, agate_scripts
):
    """BDD-2：1200 行存量文件（已超阈值）本次只改 5 行（未跨越）→ god_file_count 不增、不报该文件。"""
    repo, td = _god_scenario(git_repo, task_dir, 1200, 1200)
    # 本次 diff 只改 5 行（在 already-1200 的基础上改内容，行数不跨越阈值线）
    p = repo.path / "src" / "big.py"
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    for i in range(5):
        lines[i] = f"edited_{i} = {i}\n"
    p.write_text("".join(lines), encoding="utf-8")
    _stage(repo, "src/big.py")

    mod = _load_mod(agate_scripts)
    result = mod.check_maintainability(td)
    god_files = [
        v for v in result["violations"] if v.get("type") == "god-file"
    ]
    assert not any(v.get("file") == "src/big.py" for v in god_files)
    assert result["god_file_count"] == 0


def test_bdd_3_fuzzy_python_bare_except(
    git_repo, task_dir, agate_scripts
):
    """BDD-3：.py 新增裸 `except:` 行 staged → violation 含文件+新增行号（fuzzy_boundary_count>=1）。"""
    repo, td = _god_scenario(git_repo, task_dir, 5, 10, name="src/mod.py")
    p = repo.path / "src" / "mod.py"
    p.write_text(
        _lines(10) + "try:\n    pass\nexcept:\n    pass\n", encoding="utf-8"
    )
    _stage(repo, "src/mod.py")

    mod = _load_mod(agate_scripts)
    result = mod.check_maintainability(td)
    fz = [
        v
        for v in result["violations"]
        if v.get("type") == "fuzzy-boundary"
        and v.get("file") == "src/mod.py"
    ]
    assert fz, f"fuzzy-boundary 违规未含 src/mod.py: {result['violations']!r}"
    assert any(v.get("line") == 13 for v in fz), (
        f"新增行号应为 13（_lines(10) 之后 try=11/pass=12/except=13）: {fz!r}"
    )
    assert result["fuzzy_boundary_count"] >= 1


def test_bdd_4_existing_bare_except_not_flagged(
    git_repo, task_dir, agate_scripts
):
    """BDD-4：存量裸 `except:` 不在本次 diff 新增行 → fuzzy_boundary_count 不增（=0）。"""
    repo, td = _god_scenario(git_repo, task_dir, 5, 10, name="src/legacy.py")
    # 存量文件含裸 except（已在 HEAD），本次 staged diff 只改第 1 行
    p = repo.path / "src" / "legacy.py"
    p.write_text(
        "try:\n    pass\nexcept:\n    pass\n" + _lines(8), encoding="utf-8"
    )
    _stage(repo, "src/legacy.py")
    repo.commit("with legacy bare except")
    p.write_text(
        "edited = 0\ntry:\n    pass\nexcept:\n    pass\n" + _lines(8),
        encoding="utf-8",
    )
    _stage(repo, "src/legacy.py")

    mod = _load_mod(agate_scripts)
    result = mod.check_maintainability(td)
    fz = [
        v
        for v in result["violations"]
        if v.get("type") == "fuzzy-boundary"
        and v.get("file") == "src/legacy.py"
    ]
    assert fz == [], f"存量裸 except 被误伤: {fz!r}"
    assert result["fuzzy_boundary_count"] == 0


def test_bdd_5_threshold_configurable(
    git_repo, task_dir, agate_scripts, tmp_path
):
    """BDD-5：配置 god_file_threshold: 500 → 480→520 触发；默认 1000 下同场景不触发。"""
    repo, td = _god_scenario(git_repo, task_dir, 480, 520)
    ws = repo.path / "agate-workspace"
    ws.mkdir(parents=True, exist_ok=True)
    (ws / "maintainability.yaml").write_text(
        "god_file_threshold: 500\n", encoding="utf-8"
    )

    mod = _load_mod(agate_scripts)
    result_cfg = mod.check_maintainability(td)
    assert any(
        v.get("type") == "god-file" and v.get("file") == "src/big.py"
        for v in result_cfg["violations"]
    ), f"配置 500 未触发: {result_cfg['violations']!r}"

    # 默认阈值 1000：同场景（无配置文件）不触发
    (ws / "maintainability.yaml").unlink()
    result_default = mod.check_maintainability(td)
    assert not any(
        v.get("type") == "god-file" and v.get("file") == "src/big.py"
        for v in result_default["violations"]
    ), f"默认 1000 不应触发: {result_default['violations']!r}"


def test_bdd_6_config_missing_invalid_fallback(
    git_repo, task_dir, agate_scripts
):
    """BDD-6：配置缺失/坏 YAML/单键缺失三态 → 不抛错，返回有效判定（默认 N=1000）。"""
    repo, td = _god_scenario(git_repo, task_dir, 900, 1150)
    ws = repo.path / "agate-workspace"
    ws.mkdir(parents=True, exist_ok=True)
    mod = _load_mod(agate_scripts)

    # 态 1：配置文件不存在
    r1 = mod.check_maintainability(td)
    assert r1["git_ok"] is True
    assert any(
        v.get("type") == "god-file" and v.get("file") == "src/big.py"
        for v in r1["violations"]
    )
    assert isinstance(r1["god_file_count"], int)

    # 态 2：坏 YAML
    (ws / "maintainability.yaml").write_text(
        "god_file_threshold: [unclosed\n  bad:::", encoding="utf-8"
    )
    r2 = mod.check_maintainability(td)
    assert r2["git_ok"] is True
    assert any(
        v.get("type") == "god-file" for v in r2["violations"]
    ), f"坏 YAML 未兜底默认值: {r2['violations']!r}"

    # 态 3：单键缺失（只有 fuzzy_patterns，无阈值）→ 阈值走默认 1000
    (ws / "maintainability.yaml").write_text(
        "fuzzy_patterns:\n  python:\n    - '^\\\\s*except\\\\s*:'\n",
        encoding="utf-8",
    )
    r3 = mod.check_maintainability(td)
    assert r3["git_ok"] is True
    assert any(
        v.get("type") == "god-file" for v in r3["violations"]
    ), f"单键缺失未兜底默认阈值: {r3['violations']!r}"


def test_bdd_11_path_separator_normalized(
    git_repo, task_dir, agate_scripts
):
    """BDD-11：同一 diff 场景以 `/` 与 `\\` 路径形态输入 → violations 文件表示一致（反斜杠归一）。"""
    _repo, td = _god_scenario(git_repo, task_dir, 900, 1150)
    mod = _load_mod(agate_scripts)
    result = mod.check_maintainability(td)
    files = {v.get("file") for v in result["violations"]}
    assert "src/big.py" in files, f"归一化文件名缺失: {files!r}"
    # violations 里的 file 一律为 / 归一形态（Windows \\ 输入在 Linux 用模拟断言等价）
    for f in files:
        assert "\\" not in f, f"路径未归一化（含反斜杠）: {f!r}"
    # _norm_rel 语义模拟：两种分隔符形态归一到同一相对路径（平台分支：真实分隔符行为在
    # Windows CI 由 windows_smoke 用例覆盖，Linux 侧断言归一函数等价）
    if hasattr(mod, "_norm_rel"):
        assert mod._norm_rel("src\\big.py") == mod._norm_rel("src/big.py")


def test_bdd_12_moved_code_new_lines_judged(
    git_repo, task_dir, agate_scripts
):
    """BDD-12：含裸 `except:` 的代码块 A→B 移动（删除+新增）→ 新增行照判 violation（诚实行为非 bug）。"""
    repo, td = _god_scenario(git_repo, task_dir, 5, 10, name="src/mover.py")
    p = repo.path / "src" / "mover.py"
    # 基线：裸 except 在文件中部（存量行）
    p.write_text(
        _lines(10) + "try:\n    pass\nexcept:\n    pass\n" + _lines(5),
        encoding="utf-8",
    )
    _stage(repo, "src/mover.py")
    repo.commit("base with bare except")
    # 移动：删除原位置 4 行（try/pass/except/pass），在文件末尾新增同样 4 行
    p.write_text(
        _lines(10) + _lines(5) + "try:\n    pass\nexcept:\n    pass\n",
        encoding="utf-8",
    )
    _stage(repo, "src/mover.py")

    mod = _load_mod(agate_scripts)
    result = mod.check_maintainability(td)
    fz = [
        v
        for v in result["violations"]
        if v.get("type") == "fuzzy-boundary"
        and v.get("file") == "src/mover.py"
    ]
    assert fz, (
        "移动代码的新增行未被判定（被自动识别为移动而忽略 = FAIL，已知假阳性应诚实上报）"
    )
    # 新增行位于删除块之后的新位置（末尾），行号应 > 原位置行号
    assert all(v.get("line", 0) > 10 for v in fz), f"新增行号定位异常: {fz!r}"


def test_bdd_13_p4_staged_diff_readable(
    git_repo, task_dir, agate_scripts
):
    """BDD-13：P4 数据源对齐——代码 staged 状态调用能读到 diff 并判定；无 staged 代码时形态对比。"""
    repo, td = _god_scenario(git_repo, task_dir, 900, 1150)
    mod = _load_mod(agate_scripts)

    # P4 形态：代码 staged（_god_scenario 已 stage big.py）
    result_p4 = mod.check_maintainability(td)
    assert result_p4["git_ok"] is True
    assert result_p4["violations"], "staged 代码 diff 应被读到并判定（挂载在 P4 而非 P6）"
    assert any(v.get("type") == "god-file" for v in result_p4["violations"])

    # P6 形态对照：清空暂存区（P6 只 commit 验收文档，暂存区无代码 diff）→ 无判定产出
    repo.git("reset", "-q")
    result_p6 = mod.check_maintainability(td)
    assert result_p6["violations"] == [], (
        f"暂存区无代码 diff 时不应产生 violation（P6 挂载即死代码）: {result_p6['violations']!r}"
    )
