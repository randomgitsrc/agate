# tests/unit/test_agate_image_check.py — 图像分析工具单元测试
# （agate-image-check.bats 4 用例迁移，TAG0011 批次 5）
# 被测：agate/scripts/agate-image-check.py（variance：IMG_PATH env；ahash：SCREENSHOTS_DIR env）
# Pillow 可选：缺 Pillow 时 IMG.1/IMG.3 运行（无 Pillow 分支），IMG.4 skipif 跳过；
#   Pillow 已装时 IMG.1/IMG.3 skipif 跳过，IMG.4 运行。收集数不受影响（BDD-1 ≥749 不破）。
# 运行时造图/造随机文件用 tmp_path（BDD-5 不写字面命中行）。

import os
import re

import pytest

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    Image = None
    HAS_PIL = False


@pytest.mark.windows_smoke
@pytest.mark.skipif(HAS_PIL, reason="Pillow 已安装，跳过无 Pillow 分支")
def test_img_1_variance_no_pillow_skip(tmp_path, agate_scripts, python_exe, run_cli):
    img = tmp_path / "a.png"
    img.write_bytes(os.urandom(100))

    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-image-check.py"),
        "variance",
        env={"IMG_PATH": str(img)},
    )
    assert result.returncode == 0
    assert result.output.strip() == "SKIP_NO_PILLOW"


def test_img_2_variance_non_image_minus1(tmp_path, agate_scripts, python_exe, run_cli):
    img = tmp_path / "a.png"
    img.write_text("not an image\n", encoding="utf-8")

    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-image-check.py"),
        "variance",
        env={"IMG_PATH": str(img)},
    )
    assert result.returncode == 0
    assert result.output.strip() in ("-1", "SKIP_NO_PILLOW")


@pytest.mark.skipif(HAS_PIL, reason="Pillow 已安装，跳过无 Pillow 分支")
def test_img_3_ahash_no_pillow_stderr_exit1(tmp_path, agate_scripts, python_exe, run_cli):
    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-image-check.py"),
        "ahash",
        env={"SCREENSHOTS_DIR": str(tmp_path / "nonexistent")},
    )
    assert result.returncode == 1


@pytest.mark.skipif(not HAS_PIL, reason="Pillow 未安装，跳过")
def test_img_4_ahash_valid_image_64bit(tmp_path, agate_scripts, python_exe, run_cli):
    img = Image.new("L", (8, 8), 128)
    img.save(str(tmp_path / "a.png"))

    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-image-check.py"),
        "ahash",
        env={"SCREENSHOTS_DIR": str(tmp_path)},
    )
    assert result.returncode == 0
    assert re.fullmatch(r"[01]{64}", result.output.strip())
