#!/usr/bin/env bats
# tests/unit/agate-vision-blocker.bats — vision YAML blocker_count 读取
load ../helpers/load.bash

@test "VB.1 读 vision_analysis.summary.blocker_count" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/vb-XXXXXX")
    cat > "$dir/vision.yaml" <<'EOF'
vision_analysis:
  summary:
    blocker_count: 2
EOF
    run bash -c "YAML_PATH='$dir/vision.yaml' $PYTHON '$AGATE_SCRIPTS/agate-vision-blocker.py'"
    [ "$status" -eq 0 ]; [[ "$output" == "2" ]]
}

@test "VB.2 无 blocker_count → -1" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/vb-XXXXXX")
    echo "vision_analysis: {}" > "$dir/vision.yaml"
    run bash -c "YAML_PATH='$dir/vision.yaml' $PYTHON '$AGATE_SCRIPTS/agate-vision-blocker.py'"
    [ "$status" -eq 0 ]; [[ "$output" == "-1" ]]
}