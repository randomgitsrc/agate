# tests/regression/test_v040_dotarchived_exclusion.py — 回归测试：iter_md_files 不排除 .archived（带点）目录
# （v040-dotarchived-exclusion.bats 2 用例迁移，TAG0011 批次 11）
# 触发：PR #111 审查发现，check-protocol-consistency.py 的 iter_md_files 只排除路径分量精确等于
# "archived" 的目录，但 agate-archive-stale-outputs.sh 实际产出的回退归档目录名是 ".archived"
# （带前导点，如 agate-workspace/tasks/{Txxx}/.archived/{ts}-{phase}），从未被排除过。
# 影响：任务经历阶段回退后 CHECK 1/CHECK 2 会误报（.archived/ 下有坏格式 fixture 历史证据）。
# 迁移方式：bats 经 `$PYTHON -c` + importlib 加载脚本后调 iter_md_files(Path(tmp))——
#   pytest 用 importlib 进程内加载等价（模块纯 stdlib + yaml，同批次 10b consistency 口径）；
#   py_path 转换不再需要（pytest 在 Windows 原生运行时 Path 已是本机格式）。

from importlib import util
from pathlib import Path

import pytest


def _load_cpc(agate_scripts):
    spec = util.spec_from_file_location(
        "cpc", str(agate_scripts / "check-protocol-consistency.py")
    )
    cpc = util.module_from_spec(spec)
    spec.loader.exec_module(cpc)
    return cpc


@pytest.mark.windows_smoke
def test_rd_a_1_dotarchived_excluded(tmp_path, agate_scripts):
    task = tmp_path / "agate-workspace" / "tasks" / "T001-fake"
    archived = task / ".archived" / "20260101-000000-P6"
    archived.mkdir(parents=True)
    (archived / "bad.md").write_text("not: valid: yaml: [\n", encoding="utf-8")
    (task / "live.md").write_text("# live file\n", encoding="utf-8")

    cpc = _load_cpc(agate_scripts)
    files = [str(p) for p in cpc.iter_md_files(Path(tmp_path))]
    assert not any(".archived" in f for f in files), f".archived 下的文件未被排除: {files}"
    assert any("live.md" in f for f in files), f"非归档的活文件被误排除: {files}"


def test_rd_a_2_archived_excluded(tmp_path, agate_scripts):
    archived = tmp_path / "agate-workspace" / "archived" / "tasks" / "T001-fake"
    archived.mkdir(parents=True)
    (archived / "bad.md").write_text("not: valid: yaml: [\n", encoding="utf-8")

    cpc = _load_cpc(agate_scripts)
    files = [str(p) for p in cpc.iter_md_files(Path(tmp_path))]
    assert len(files) == 0, f"archived（不带点）目录下的文件未被排除: {files}"
