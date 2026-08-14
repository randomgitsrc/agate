#!/usr/bin/env python3
"""check-p6-evidence.py — P6 证据格式检查（P1.7）

从 check-p6-evidence.sh 迁移（TAG0010 批次 2d）。CLI 契约与 sh 版等价：
  check-p6-evidence.py TASK_DIR
exit 0 = 通过; exit 1 = 真失败（证据目录为空 / 无 BDD / md5 重复——应阻断）
exit 2 = WARNING（低方差/小图/无 P6 文件——不阻断，提醒人工确认）

检查 P6-evidence/ 目录非空 + UI 截图实质检查（R1a）。查询类 BDD 可不截图，
但须有断言记录证据（response.json / assert.log 等）。含像素方差检测
（低方差/疑似占位图, WARNING）+ md5 去重（阻断）+ average hash 相似度（WARNING）。

- grep -cE '^\\s*- (PASS|FAIL)' → re.findall(MULTILINE) 计数（逐行语义一致）
- grep -E '^\\s*- PASS\\b' 逐行 + S2 结构判定正则 → re.findall + ref_re.search
- find ... -type f -not -name '.*'（递归）→ _find_files（os.walk，隐藏名跳过）
- stat -c%s / stat -f%z → os.path.getsize（失败回退 0）
- file -b --mime-type（有 file 时）/ magic bytes fallback → _is_image
- md5sum | sort | uniq → hashlib.md5 + Counter 等价
- 依赖既有 py：agate-md-field-get.py（env FILE）/ agate-image-check.py
  （env IMG_PATH / env SCREENSHOTS_DIR），均 sys.executable subprocess +
  $(...) 剥尾换行 → .rstrip("\n")
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _run_script(script, args, env_extra):
    """调既有 py 工具（sys.executable subprocess，env 传参），返回 (stdout 去尾换行, returncode)。

    sh 侧 `$(...) 2>/dev/null || echo ...` 的失败回退语义由调用方按 returncode 决定。
    """
    env = dict(os.environ)
    env.update(env_extra)
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, script)] + args,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env,
        )
    except OSError:
        return "", 1
    return (proc.stdout or "").rstrip("\n"), proc.returncode


def _find_files(base):
    """find base -type f -not -name '.*'（递归，排除隐藏名文件）等价。"""
    files = []
    for _root, _dirs, names in os.walk(base):
        for name in names:
            if name.startswith("."):
                continue
            files.append(os.path.join(_root, name))
    return files


def _is_image(path):
    """file 命令可用时仅用 mime 判定；否则 magic bytes fallback（PNG/JPEG/GIF/WebP）。"""
    if shutil.which("file"):
        try:
            proc = subprocess.run(
                ["file", "-b", "--mime-type", path],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
        except OSError:
            return False
        return proc.stdout.startswith("image/")
    try:
        with open(path, "rb") as f:
            magic = f.read(12)
    except OSError:
        return False
    if magic[:4] == b"\x89PNG":
        return True
    if magic[:2] == b"\xff\xd8":
        return True
    if magic[:4] == b"GIF8":
        return True
    if magic[:4] == b"RIFF" and len(magic) >= 12 and magic[8:12] == b"WEBP":
        return True
    return False


def _md5_entries(base):
    """find ... -exec md5sum {} \\; 等价（(hash, 全路径) 列表，失败跳过）。"""
    entries = []
    for f in _find_files(base):
        try:
            with open(f, "rb") as fh:
                digest = hashlib.md5(fh.read()).hexdigest()
        except OSError:
            continue
        entries.append((digest, f))
    return entries


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("用法: check-p6-evidence.py TASK_DIR\n")
        sys.exit(1)
    task_dir = sys.argv[1]
    p6_file = os.path.join(task_dir, "P6-acceptance.md")

    if not os.path.isfile(p6_file):
        sys.exit(2)

    try:
        with open(p6_file, encoding="utf-8", errors="replace") as f:
            p6_text = f.read()
    except OSError:
        p6_text = ""

    bdd_count = len(re.findall(r"^\s*- (PASS|FAIL)", p6_text, re.MULTILINE))

    if bdd_count == 0:
        sys.stderr.write("GATE P6-EVIDENCE: P6-acceptance.md 无 BDD 条目（- PASS/- FAIL 格式）\n")
        sys.exit(1)

    evidence_dir = os.path.join(task_dir, "P6-evidence")

    # 每条 PASS 行必须含文件引用（括号内路径，S2 结构判定：文件名.扩展名）
    ref_re = re.compile(r"\([^()]*[^()\s]\.[a-zA-Z0-9]+[^)]*\)")
    pass_without_ref = 0
    pass_without_ref_details = ""
    for line in re.findall(r"^\s*- PASS\b.*", p6_text, re.MULTILINE):
        if not ref_re.search(line):
            pass_without_ref += 1
            pass_without_ref_details += "  - {}\n".format(line)

    if pass_without_ref > 0:
        sys.stderr.write(
            "GATE P6-EVIDENCE: 有 {} 条 PASS 缺文件证据引用（每条 PASS 必须引用证据文件，形式不限：截图/日志/JSON/文本）\n".format(pass_without_ref)
        )
        sys.stderr.write(pass_without_ref_details + "\n")
        sys.exit(1)

    if not os.path.isdir(evidence_dir) or not os.listdir(evidence_dir):
        sys.stderr.write("GATE P6-EVIDENCE: P6-evidence/ 目录不存在或为空\n")
        sys.exit(1)

    sys.stderr.write("GATE P6-EVIDENCE: {} 条 BDD，证据目录非空\n".format(bdd_count))

    # UI 截图实质检查（R1a：仅当 P6-acceptance.md 含截图引用时才检查）
    p2_file = os.path.join(task_dir, "P2-design.md")
    ui_affected = ""
    if os.path.isfile(p2_file):
        out, rc = _run_script("agate-md-field-get.py", ["ui_affected"], {"FILE": p2_file})
        if rc == 0:
            ui_affected = out

    if ui_affected == "true":
        # evidence 类型检查：ui_affected=true 时不能全是纯文本（.md/.txt）
        # 防源码分析充数——运行时工具产出天然是 .json/.log/.png/.yaml 等结构化格式
        non_text_count = 0
        for _root, _dirs, names in os.walk(evidence_dir):
            for name in names:
                if name.startswith("."):
                    continue
                if name.endswith(".md") or name.endswith(".txt"):
                    continue
                non_text_count += 1
        if non_text_count == 0:
            sys.stderr.write(
                "GATE P6-EVIDENCE: ui_affected=true 但 evidence 全是纯文本（.md/.txt），缺少运行时数据（.json/.log/.png/.yaml 等）。源码引用不算运行时证据。\n"
            )
            sys.exit(1)

        has_screenshot_ref = sum(
            1 for line in p6_text.splitlines() if "(screenshots/" in line
        )

        if has_screenshot_ref > 0:
            screenshots_dir = os.path.join(evidence_dir, "screenshots")
            if not os.path.isdir(screenshots_dir) or not _find_files(screenshots_dir):
                sys.stderr.write(
                    "GATE P6-EVIDENCE: ui_affected=true 且 PASS 引用了截图，但 P6-evidence/screenshots/ 目录不存在或为空\n"
                )
                sys.exit(1)

            empty_count = 0
            empty_details = ""
            small_image_warning = 0
            small_image_details = ""
            variance_warning = 0
            skip_checks = os.environ.get("AGATE_SKIP_IMAGE_CHECKS", "0") == "1"
            if skip_checks:
                sys.stderr.write("GATE P6-EVIDENCE WARNING: AGATE_SKIP_IMAGE_CHECKS=1，方差/相似度检测已主动跳过\n")
            else:
                for img in _find_files(screenshots_dir):
                    try:
                        size = os.path.getsize(img)
                    except OSError:
                        size = 0
                    if size <= 1024:
                        if _is_image(img):
                            small_image_warning += 1
                            small_image_details += "  - {}\n".format(os.path.basename(img))
                        else:
                            empty_count += 1
                            empty_details += "  - {}\n".format(os.path.basename(img))
                    variance, rc = _run_script("agate-image-check.py", ["variance"], {"IMG_PATH": img})
                    if rc != 0:
                        variance = "-1"
                    if variance == "SKIP_NO_PILLOW":
                        sys.stderr.write("GATE P6-EVIDENCE WARNING: Pillow 未安装，方差/相似度检测已跳过\n")
                        break
                    else:
                        try:
                            var_int = int(variance)
                        except ValueError:
                            var_int = -1
                        if 0 <= var_int < 50:
                            variance_warning += 1
                            sys.stderr.write(
                                "GATE P6-EVIDENCE WARNING: {} 像素方差 {}（<50，疑似纯色/占位图，请确认非充数）\n".format(os.path.basename(img), var_int)
                            )
                if variance_warning > 0:
                    sys.stderr.write("GATE P6-EVIDENCE WARNING: 有 {} 张截图像素方差 < 50（疑似纯色/占位图，请确认非充数）\n".format(variance_warning))
                    sys.exit(2)

            if empty_count > 0:
                sys.stderr.write("GATE P6-EVIDENCE: P6-evidence/screenshots/ 有 {} 个非图片文件 ≤ 1KB（疑似充数）\n".format(empty_count))
                sys.stderr.write(empty_details + "\n")
                sys.exit(1)
            if small_image_warning > 0:
                sys.stderr.write("GATE P6-EVIDENCE WARNING: P6-evidence/screenshots/ 有 {} 个合法图片 ≤ 1KB（元素级小截图，不阻断但请确认非充数）\n".format(small_image_warning))
                sys.stderr.write(small_image_details + "\n")
                sys.exit(2)

            # md5 去重（逐字节相同 → 阻断）
            md5_entries = _md5_entries(screenshots_dir)
            md5_total = len(md5_entries)
            md5_unique = len(set(h for h, _ in md5_entries))
            if md5_total > md5_unique:
                md5_dupes = md5_total - md5_unique
                md5_counts = Counter(h for h, _ in md5_entries)
                md5_details = ""
                for h in sorted(h for h, c in md5_counts.items() if c > 1):
                    for path in sorted(p for hh, p in md5_entries if hh == h):
                        md5_details += "  - {}\n".format(os.path.basename(path))
                sys.stderr.write("GATE P6-EVIDENCE: 有 {} 个截图文件逐字节完全相同（md5 重复，疑似同一物理文件被多条 PASS 引用充数）\n".format(md5_dupes))
                sys.stderr.write(md5_details)
                sys.exit(1)

            if not skip_checks:
                ahash_list, _ = _run_script("agate-image-check.py", ["ahash"], {"SCREENSHOTS_DIR": screenshots_dir})
                if "SKIP_NO_PILLOW" in ahash_list:
                    sys.stderr.write("GATE P6-EVIDENCE WARNING: Pillow 未安装，相似度检测已跳过\n")
                else:
                    ahash_lines = [l for l in ahash_list.splitlines() if l]
                    ahash_total = len(ahash_lines)
                    ahash_unique = len(set(ahash_lines))
                    if ahash_total > ahash_unique:
                        ahash_dupes = ahash_total - ahash_unique
                        sys.stderr.write(
                            "GATE P6-EVIDENCE WARNING: 有 {} 组视觉高度相似截图（average hash 相同但非逐字节相同，不阻断，行为差异类 BDD 截图可能视觉相同，请在 acceptance report 说明原因）\n".format(ahash_dupes)
                        )

    sys.exit(0)


if __name__ == "__main__":
    main()
