#!/usr/bin/env bats
# tests/unit/agate-evidence-consistency.bats — evidence JSON 与 P6 一致性
load ../helpers/load.bash

@test "EC.1 PASS 但 evidence 标 FAIL → 输出不一致" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/ec-XXXXXX")
    mkdir -p "$dir/P6-evidence"
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    cat > "$dir/P6-evidence/result.json" <<'EOF'
{"bdd_results": [{"id": "BDD-1", "status": "fail"}]}
EOF
    run bash -c "EVIDENCE_DIR='$dir/P6-evidence' P6_FILE='$dir/P6-acceptance.md' python3 '$AGATE_SCRIPTS/agate-evidence-consistency.py'"
    [ "$status" -eq 0 ]; [[ "$output" == *"BDD-1"* ]]
}

@test "EC.2 无不一致 → 空" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/ec-XXXXXX")
    mkdir -p "$dir/P6-evidence"
    cat > "$dir/P6-acceptance.md" <<'EOF'
- PASS BDD-1 (result.json)
EOF
    cat > "$dir/P6-evidence/result.json" <<'EOF'
{"bdd_results": [{"id": "BDD-1", "status": "pass"}]}
EOF
    run bash -c "EVIDENCE_DIR='$dir/P6-evidence' P6_FILE='$dir/P6-acceptance.md' python3 '$AGATE_SCRIPTS/agate-evidence-consistency.py'"
    [ "$status" -eq 0 ]; [ -z "$output" ]
}