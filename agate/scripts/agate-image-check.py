#!/usr/bin/env python3
"""截图图像分析（py 抽离批次 6）。

variance 子命令：读 IMG_PATH env，PIL 灰度方差检测。无 Pillow 打印 SKIP_NO_PILLOW
（exit 0）；图像异常打印 -1。
ahash 子命令：读 SCREENSHOTS_DIR env，遍历图片算 average hash 并逐行打印。无 Pillow
stderr 打印 SKIP_NO_PILLOW + exit 1（bash 侧 2>/dev/null || echo 吞掉）；单图异常跳过。
"""

import contextlib
import glob
import os
import sys


def _load_pil():
    try:
        from PIL import Image
        return Image
    except ImportError:
        return None


def main():
    op = sys.argv[1]
    Image = _load_pil()
    if op == "variance":
        if Image is None:
            print("SKIP_NO_PILLOW")
            return
        try:
            img = Image.open(os.environ["IMG_PATH"]).convert("L")
            pixels = list(img.tobytes())
            mean = sum(pixels) / len(pixels)
            variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
            print(int(variance))
        except Exception:
            print(-1)
    elif op == "ahash":
        if Image is None:
            sys.stderr.write("SKIP_NO_PILLOW\n")
            sys.exit(1)

        def _ahash(path):
            img = Image.open(path).convert("L").resize((8, 8))
            pixels = list(img.tobytes())
            avg = sum(pixels) / len(pixels)
            return "".join("1" if p >= avg else "0" for p in pixels)

        for f in sorted(glob.glob(os.environ["SCREENSHOTS_DIR"] + "/*")):
            with contextlib.suppress(Exception):
                print(_ahash(f))
    else:
        sys.stderr.write(f"agate-image-check: unknown op {op}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
