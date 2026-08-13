#!/usr/bin/env bats
# tests/unit/agate-gate-p5-count.bats — P5 命令计数工具
load ../helpers/load.bash

@test "GPC.1 统计 P5 主/辅命令数（1 主 + 2 辅 → '1 2'，BDD-3）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/gpc-XXXXXX")
    cat > "$dir/P2.md" <<'EOF'
gate_commands:
  P5: pytest
  P5_unit: pytest unit
  P5_e2e: npx vitest
EOF
    run bash -c "GATE_FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-gate-p5-count.py'"
    [ "$status" -eq 0 ]; [[ "$output" == "1 2" ]]
}

@test "GPC.2 无 gate_commands 块 → 0 0（BDD-5 边界）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/gpc-XXXXXX")
    echo "无 gate_commands" > "$dir/P2.md"
    run bash -c "GATE_FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-gate-p5-count.py'"
    [ "$status" -eq 0 ]; [[ "$output" == "0 0" ]]
}

@test "GPC.3 块含 P5+P5_formatter → 1 0（aux 排除 _formatter，BDD-3）" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/gpc-XXXXXX")
    cat > "$dir/P2.md" <<'EOF'
gate_commands:
  P5: pytest
  P5_formatter: pytest.sh
EOF
    run bash -c "GATE_FILE='$dir/P2.md' python3 '$AGATE_SCRIPTS/agate-gate-p5-count.py'"
    [ "$status" -eq 0 ]; [[ "$output" == "1 0" ]]
}