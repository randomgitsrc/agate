#!/usr/bin/env bats
# tests/unit/agate-gate-p5-count.bats — P5 命令计数工具
load ../helpers/load.bash

@test "GPC.1 统计 P5 命令数" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/gpc-XXXXXX")
    cat > "$dir/P2.md" <<'EOF'
gate_commands:
  P5: pytest
  P5_unit: pytest unit
  P5_e2e: npx vitest
EOF
    run bash -c "GATE_FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-gate-p5-count.py'"
    [ "$status" -eq 0 ]; [[ "$output" == "3" ]]
}

@test "GPC.2 无 gate_commands 块 → 0" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/gpc-XXXXXX")
    echo "无 gate_commands" > "$dir/P2.md"
    run bash -c "GATE_FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-gate-p5-count.py'"
    [ "$status" -eq 0 ]; [[ "$output" == "0" ]]
}