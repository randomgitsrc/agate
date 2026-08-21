# tests/unit/test_agate_risk_score.py — 风险算分脚本（TAG0019 D1，BDD-1..5）
# 被测：agate/scripts/agate-risk-score.py（TASK_DIR）
# 输出契约（P2-design.md §2.1）：
#   risk_score: N / tier: thin|standard|full / 逐信号行 `key: level (evidence)` /
#   domain-markers: [...]（敏感路径命中或 P1 domains 声明时含 security）
# 信号分级：file-type / sensitive-path / change-size（对齐 check-pruning._staged_source_count）/
#   impact。tier 合成：任一 high→full；全 low→thin；其余→standard。
# TDD 红灯：模块 P4 前未实现 → CLI exit 非 0（本组全期望 exit 0）= 真红灯。
#
# 平台无关：无裸 python3 / 无 /tmp / 无 POSIX symlink 字面；git 经 run_git（被测脚本）。

import re
import shutil

import pytest

from conftest import add_p1_field

# 信号级别 → 数值（BDD-2 分级可区分性比较）
_LEVEL_NUM = {"high": 3, "medium": 2, "low": 1}


def _run_score(agate_scripts, python_exe, run_cli, task_arg, cwd=None):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-risk-score.py"),
        task_arg,
        cwd=cwd,
    )


def _stage(repo, git_repo, name, content):
    p = repo / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    git_repo.stage(name)


def _repo_with_staged(git_repo, task_dir, paths):
    """git repo：init commit + 拷贝任务目录到 repo/task + 暂存 paths（path→content）。"""
    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init")
    td = task_dir()
    shutil.copytree(td, repo / "task")
    for name, content in paths.items():
        _stage(repo, git_repo, name, content)
    return repo


def _signal_level(output, key):
    """取信号位级别（high/medium/low），缺失 FAIL。"""
    m = re.search(rf"{re.escape(key)}:\s*(high|medium|low)", output)
    assert m, f"输出缺信号位 {key}: {output!r}"
    return m.group(1)


@pytest.mark.windows_smoke
def test_bdd_1_output_three_elements_consistent_with_staged_diff(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-1：非空暂存区 → risk_score（数值）+ tier（三值之一）+ 逐信号证据行，且与 git diff --cached 内容一致。"""
    repo = _repo_with_staged(
        git_repo, task_dir, {"src/app_main.py": "def main():\n    pass\n"}
    )
    result = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0
    # 三要素 1：risk_score 数值
    assert re.search(r"risk_score:\s*\d+", result.output), f"缺 risk_score 数值: {result.output!r}"
    # 三要素 2：tier ∈ {thin, standard, full}
    assert re.search(r"tier:\s*(thin|standard|full)", result.output), f"缺 tier: {result.output!r}"
    # 三要素 3：逐信号证据行（至少一信号）+ 与暂存区 diff 内容一致
    assert re.search(r"(file-type|sensitive-path|change-size|impact):\s*(high|medium|low)", result.output), \
        f"缺逐信号证据行: {result.output!r}"
    assert "app_main.py" in result.output, f"证据未反映暂存区 diff 内容: {result.output!r}"


def test_bdd_2_file_type_high_for_agate_protocol(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-2：agate/**/*.md / agate/scripts/*.py（A 类）→ 文件类型信号 high。"""
    repo = _repo_with_staged(git_repo, task_dir, {"agate/scripts/foo.py": "x = 1\n"})
    result = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0
    assert _signal_level(result.output, "file-type") == "high"


def test_bdd_2_file_type_low_for_tests_config(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-2：仅 tests/配置类（B 类）→ 文件类型信号 low。"""
    repo = _repo_with_staged(
        git_repo, task_dir, {"agate/tests/unit/test_foo.py": "def test_x():\n    pass\n"}
    )
    result = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0
    assert _signal_level(result.output, "file-type") == "low"


def test_bdd_2_file_type_a_scores_strictly_higher_than_b(
    git_repo, task_dir, agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-2：A 类文件类型信号位评分严格高于 B 类（分级不可区分 = FAIL）。"""
    # A 类暂存区
    ra = _repo_with_staged(git_repo, task_dir, {"agate/scripts/foo.py": "x = 1\n"})
    res_a = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(ra))
    # B 类暂存区（独立仓库）
    rb = _repo_with_staged(
        git_repo, task_dir, {"agate/tests/unit/test_foo.py": "def test_x():\n    pass\n"}
    )
    res_b = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(rb))
    assert res_a.returncode == 0 and res_b.returncode == 0
    level_a = _LEVEL_NUM[_signal_level(res_a.output, "file-type")]
    level_b = _LEVEL_NUM[_signal_level(res_b.output, "file-type")]
    assert level_a > level_b, f"文件类型分级不可区分：A={level_a}, B={level_b}"


def test_bdd_3_sensitive_path_high_and_security_domain(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-3：敏感路径（auth/ 等）→ 敏感路径信号 high + security 域映射。"""
    repo = _repo_with_staged(git_repo, task_dir, {"auth/login.py": "def login():\n    pass\n"})
    result = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0
    assert _signal_level(result.output, "sensitive-path") == "high"
    assert re.search(r"domain[\s_-]?markers?:?\s*\[[^\]]*security|domain:\s*security", result.output), \
        f"缺 security 域映射: {result.output!r}"


def test_bdd_3_no_sensitive_no_security_marker(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-3：无敏感路径关键词 → 无 security 域标注（误报 = FAIL）。"""
    repo = _repo_with_staged(git_repo, task_dir, {"src/hello.py": "print(1)\n"})
    result = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0
    assert "security" not in result.output.lower(), f"无敏感路径却打 security 标注: {result.output!r}"


def test_bdd_4_change_size_high_when_src_count_gt5(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-4：源码文件数（对齐 _staged_source_count 口径）>5 → 改动规模 high。"""
    paths = {f"src/mod_{i}.py": "x = 1\n" for i in range(6)}
    repo = _repo_with_staged(git_repo, task_dir, paths)
    result = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0
    assert _signal_level(result.output, "change-size") == "high"
    assert re.search(r"source files?\s*=\s*[6-9]|\d+\s*>\s*5", result.output), \
        f"改动规模证据未含 >5 计数: {result.output!r}"


def test_bdd_4_change_size_low_when_le5(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-4：源码文件数 ≤5 → 改动规模 low（与 >5 相反边界）。"""
    paths = {f"src/mod_{i}.py": "x = 1\n" for i in range(3)}
    repo = _repo_with_staged(git_repo, task_dir, paths)
    result = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0
    assert _signal_level(result.output, "change-size") == "low"


def test_bdd_5_impact_high_on_cross_reference(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-5：改动文件被其他模块 grep 反向引用 → 影响面信号升级 high。"""
    repo = _repo_with_staged(
        git_repo, task_dir,
        {"core_logic.py": "VALUE = 1\n", "consumer.py": "import core_logic\nprint(core_logic.VALUE)\n"},
    )
    result = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0
    assert _signal_level(result.output, "impact") == "high"


def test_bdd_5_no_cross_reference_not_upgraded(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-5：无反向引用 → 影响面信号不升级（low，二值可判）。"""
    repo = _repo_with_staged(git_repo, task_dir, {"isolated.py": "X = 1\n"})
    result = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0
    assert _signal_level(result.output, "impact") == "low"


def test_bdd_5_domain_marker_from_declared_scope(
    git_repo, task_dir, agate_scripts, python_exe, run_cli
):
    """BDD-5：任务 scope 声明 security 域 → 输出含域映射标注（security）。"""
    td = task_dir()
    add_p1_field(td, "domains", "[security]")
    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init")
    shutil.copytree(td, repo / "task")
    (repo / "src" / "hello.py").write_text("print(1)\n", encoding="utf-8")
    git_repo.stage("src/hello.py")
    result = _run_score(agate_scripts, python_exe, run_cli, "task", cwd=str(repo))
    assert result.returncode == 0
    assert "security" in result.output.lower(), f"声明 security 域却无域映射标注: {result.output!r}"
