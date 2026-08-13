#!/usr/bin/env bats
# tests/unit/agate-image-check.bats — 图像分析工具单元测试
load ../helpers/load.bash

@test "IMG.1 variance 无 Pillow → SKIP_NO_PILLOW" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/img-XXXXXX")
    head -c 100 /dev/urandom > "$dir/a.png"
    run bash -c "IMG_PATH='$dir/a.png' $PYTHON -c 'import PIL' 2>/dev/null && echo HAS_PIL || echo NO_PIL"
    if [[ "$output" == "NO_PIL" ]]; then
        run bash -c "IMG_PATH='$dir/a.png' $PYTHON '$AGATE_SCRIPTS/agate-image-check.py' variance"
        [ "$status" -eq 0 ]; [[ "$output" == "SKIP_NO_PILLOW" ]]
    else
        skip "Pillow 已安装，跳过无 Pillow 分支"
    fi
}

@test "IMG.2 variance 非图像 → -1" {
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/img-XXXXXX")
    echo "not an image" > "$dir/a.png"
    run bash -c "IMG_PATH='$dir/a.png' $PYTHON '$AGATE_SCRIPTS/agate-image-check.py' variance"
    [ "$status" -eq 0 ]
    case "$output" in
        "-1"|"SKIP_NO_PILLOW") : ;;
        *) false;;
    esac
}

@test "IMG.3 ahash 无 Pillow → stderr+exit 1" {
    run bash -c "$PYTHON -c 'import PIL' 2>/dev/null && echo HAS_PIL || echo NO_PIL"
    if [[ "$output" == "NO_PIL" ]]; then
        run bash -c "SCREENSHOTS_DIR='/nonexistent' $PYTHON '$AGATE_SCRIPTS/agate-image-check.py' ahash"
        [ "$status" -eq 1 ]
    else
        skip "Pillow 已安装，跳过无 Pillow 分支"
    fi
}

@test "IMG.4 ahash 合法图片 → 输出 64 位 hash（Pillow 已装时）" {
    run bash -c "$PYTHON -c 'import PIL' 2>/dev/null && echo HAS_PIL || echo NO_PIL"
    if [[ "$output" == "NO_PIL" ]]; then
        skip "Pillow 未安装，跳过"
    fi
    local dir; dir=$(mktemp -d "$BATS_TEST_TMPDIR/img-XXXXXX")
    $PYTHON -c "
from PIL import Image
img = Image.new('L', (8, 8), 128)
img.save('$dir/a.png')
"
    run bash -c "SCREENSHOTS_DIR='$dir' $PYTHON '$AGATE_SCRIPTS/agate-image-check.py' ahash"
    [ "$status" -eq 0 ]
    [[ "$output" =~ ^[01]{64}$ ]]
}