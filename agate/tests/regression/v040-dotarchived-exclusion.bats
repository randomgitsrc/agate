#!/usr/bin/env bats
# tests/regression/v040-dotarchived-exclusion.bats — 回归测试：iter_md_files 不排除 .archived（带点）目录
# 触发：PR #111 审查发现，check-protocol-consistency.py 的 iter_md_files 只排除路径分量
# 精确等于 "archived" 的目录，但 agate-archive-stale-outputs.sh 实际产出的回退归档目录名
# 是 ".archived"（带前导点，如 agate-workspace/tasks/{Txxx}/.archived/{timestamp}-{phase}/），从未被排除过
# 影响：任何任务一旦经历过阶段回退（.archived/ 下会有历史证据/故意构造的坏格式 fixture），
# CHECK 1/CHECK 2 会误报，main 上此 bug 同样存在，只是从未有 .archived 任务目录暴露过

load ../helpers/load.bash

@test "R-DA.1 iter_md_files 排除路径含 .archived（带点）分量的文件" {
    local tmpdir
    tmpdir=$(mktemp -d "$BATS_TEST_TMPDIR/dotarchived.XXXXXX")
    mkdir -p "$tmpdir/agate-workspace/tasks/T001-fake/.archived/20260101-000000-P6"
    echo "not: valid: yaml: [" > "$tmpdir/agate-workspace/tasks/T001-fake/.archived/20260101-000000-P6/bad.md"
    mkdir -p "$tmpdir/agate-workspace/tasks/T001-fake"
    echo "# live file" > "$tmpdir/agate-workspace/tasks/T001-fake/live.md"

    run $PYTHON -c "
import sys
sys.path.insert(0, '$AGATE_SCRIPTS')
from importlib import util
from pathlib import Path
spec = util.spec_from_file_location('cpc', '$AGATE_SCRIPTS/check-protocol-consistency.py')
cpc = util.module_from_spec(spec)
spec.loader.exec_module(cpc)
files = [str(p) for p in cpc.iter_md_files(Path('$tmpdir'))]
assert not any('.archived' in f for f in files), f'.archived 下的文件未被排除: {files}'
assert any('live.md' in f for f in files), f'非归档的活文件被误排除: {files}'
"
    [ "$status" -eq 0 ]
}

@test "R-DA.2 iter_md_files 仍排除路径含 archived（不带点）分量的文件（既有行为不回归）" {
    local tmpdir
    tmpdir=$(mktemp -d "$BATS_TEST_TMPDIR/archived.XXXXXX")
    mkdir -p "$tmpdir/agate-workspace/archived/tasks/T001-fake"
    echo "not: valid: yaml: [" > "$tmpdir/agate-workspace/archived/tasks/T001-fake/bad.md"

    run $PYTHON -c "
import sys
sys.path.insert(0, '$AGATE_SCRIPTS')
from importlib import util
from pathlib import Path
spec = util.spec_from_file_location('cpc', '$AGATE_SCRIPTS/check-protocol-consistency.py')
cpc = util.module_from_spec(spec)
spec.loader.exec_module(cpc)
files = [str(p) for p in cpc.iter_md_files(Path('$tmpdir'))]
assert len(files) == 0, f'archived（不带点）目录下的文件未被排除: {files}'
"
    [ "$status" -eq 0 ]
}
