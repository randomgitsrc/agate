#!/usr/bin/env bats
# tests/unit/agate-scripts-encoding.bats — TAG0004 S3 grep 断言审计 + Linux ASCII 回归
# BDD-5：所有文本 open()/read_text() 必须带 encoding=utf-8（Image.open 与二进制除外）。
# TDD 红灯：当前 13 个 py（20 处）缺 encoding，本条测试应红，P4 批量加 encoding 后转绿。

load ../helpers/load.bash

@test "bdd-5 全部 agate/scripts/*.py 文本 open()/read_text() 带 encoding=utf-8（Image.open 与二进制除外，S3）" {
    run $PYTHON -c "
import glob, re
violations = []
for f in sorted(glob.glob('$AGATE_SCRIPTS/*.py')):
    with open(f, encoding='utf-8', errors='replace') as fh:
        lines = fh.readlines()
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith('#') or s.startswith('\"\"\"') or s.startswith(\"'''\"):
            continue
        if re.search(r'(?<!Image\.)\bopen\(', line) and 'encoding=' not in line and '"rb"' not in line and '"wb"' not in line:
            violations.append(f'{f}:{i}')
        if 'read_text(' in line and 'encoding=' not in line:
            violations.append(f'{f}:{i}')
assert not violations, 'open()/read_text() 缺 encoding: ' + '、'.join(violations[:30])
"
    [ "$status" -eq 0 ]
}

@test "bdd-8 agate-state-get.py Linux 纯 ASCII .state.yaml 读取行为不变（S3 回归）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/st-XXXXXX")
    printf 'task_id: T001\nphase: P1\nstatus: active\nretries: {}\n' > "$dir/.state.yaml"
    run bash -c "STATE_FILE='$dir/.state.yaml' $PYTHON '$AGATE_SCRIPTS/agate-state-get.py' phase"
    [ "$status" -eq 0 ]; [[ "$output" == "P1" ]]
}
