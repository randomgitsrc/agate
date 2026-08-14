#!/usr/bin/env bats
# tests/unit/agate-changelog-unreleased.bats — Changelog Unreleased 提取
load ../helpers/load.bash

@test "CL.1 提取 Unreleased 区域内容" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cl-XXXXXX")
    cat > "$dir/CHANGELOG.md" <<'EOF'
## [Unreleased]
### Added
- T001 fix

## [v0.33.0]
- old
EOF
    run bash -c "CHANGELOG_FILE='$dir/CHANGELOG.md' $PYTHON '$AGATE_SCRIPTS/agate-changelog-unreleased.py'"
    [ "$status" -eq 0 ]; [[ "$output" == *"T001 fix"* ]]
}

@test "CL.2 无 Unreleased → 空" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/cl-XXXXXX")
    echo "## [v0.33.0]" > "$dir/CHANGELOG.md"
    run bash -c "CHANGELOG_FILE='$dir/CHANGELOG.md' $PYTHON '$AGATE_SCRIPTS/agate-changelog-unreleased.py'"
    [ "$status" -eq 0 ]; [ -z "$output" ]
}