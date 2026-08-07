#!/usr/bin/env bats
# tests/unit/agate-read-p5-commands.bats — P5 gate_commands 解析器单元测试
load ../helpers/load.bash

@test "P5C.1 P2 含 P5 + P5_formatter + P5_js → 输出对象含 commands" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/p5-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands:
  P5: pytest
  P5_formatter: pytest.sh
  P5_js: vitest run
  P5_js_formatter: vitest.sh
EOF
    run bash -c "P2_DESIGN='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-p5-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest"'* ]]
    [[ "$output" == *'"formatter": "pytest.sh"'* ]]
    [[ "$output" == *'"cmd": "vitest run"'* ]]
    [[ "$output" == *'"commands"'* ]]
}

@test "P5C.2 P2 无 gate_commands.P5 → 输出空（供 bash -z 判定）" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/p5-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands: {}
EOF
    run bash -c "P2_DESIGN='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-p5-commands.py'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "P5C.3 P2 无 gate_commands 块 → 输出空" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/p5-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
无 gate_commands
EOF
    run bash -c "P2_DESIGN='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-p5-commands.py'"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "P5C.4 P5 键双引号值被去除 + suffix/formatter 关联" {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/p5-XXXXXX")
    cat > "$dir/P2-design.md" <<'EOF'
---
agent: test
---
gate_commands:
  P5: "pytest -q"
  P5_html_formatter: vitest.sh
  P5_html: "npx vitest"
EOF
    run bash -c "P2_DESIGN='$dir/P2-design.md' python3 '$AGATE_SCRIPTS/agate-read-p5-commands.py'"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"cmd": "pytest -q"'* ]]
    [[ "$output" == *'"cmd": "npx vitest"'* ]]
    [[ "$output" == *'"formatter": "vitest.sh"'* ]]
}