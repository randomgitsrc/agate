#!/usr/bin/env bats
# tests/unit/agate-gate-missing-cmds.bats — gate_commands 缺失命令检测工具
load ../helpers/load.bash

@test "GMC.1 提取命令 token 输出 key:token" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/gmc-XXXXXX")
    cat > "$dir/P2.md" <<'EOF'
gate_commands:
  P3: pytest -q
  P3_formatter: pytest.sh
  P5: npx vitest
EOF
    run bash -c "GATE_FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-gate-missing-cmds.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *"P3:pytest"* ]]
    [[ "$output" == *"P5:npx"* ]]
    [[ "$output" != *"formatter"* ]]
}

@test "GMC.2 命令含 / 或 = 的 token 跳过" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/gmc-XXXXXX")
    cat > "$dir/P2.md" <<'EOF'
gate_commands:
  P3: .venv/bin/python -m pytest
  P5: A=1 pytest
EOF
    run bash -c "GATE_FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-gate-missing-cmds.py'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}