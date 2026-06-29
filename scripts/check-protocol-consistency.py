#!/usr/bin/env python3
"""
agate 协议结构一致性检查 (P3-1)
================================

回应 LIMITATIONS.md「局限 5：协议文档自身的内部一致性不在流程内」。

设计原则：只做**结构**一致性（机器可判定），不碰**语义**一致性（不可判定）。
覆盖本仓评审 agate-review-20260626-1.md 第 1-2 章里可机器化的缺陷类型：

  CHECK 1  所有 ```yaml 代码块可被 yaml.safe_load 解析            (对应 P0-3)
  CHECK 2  协议文件内引用的 docs/assets/scripts 路径真实存在        (对应 P0-4, P1-3)
  CHECK 3  协议文件内的硬编码行号引用 `xxx.md L123`               (对应 P1-4)
  CHECK 4  跨文件字段集一致：gate_commands 键集合                  (对应 P1-2)
  CHECK 5  「N 个协议文件」计数声明 vs 实际列表长度（锚点白名单）   (对应 P1-1)
   CHECK 6  README LICENSE 徽章指向的文件存在 + gstack MIT 归属保留  (对应 P0-2)
   CHECK 7  README version badge 与最新 git tag 一致

退出码：0 = 全过；1 = 有 ERROR；2 = 仅有 WARNING（可配置是否失败）。

用法：
  python3 scripts/check-protocol-consistency.py            # 从仓库根运行
  python3 scripts/check-protocol-consistency.py --strict   # WARNING 也判失败
  python3 scripts/check-protocol-consistency.py --json     # 机器可读输出
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: 需要 pyyaml。请运行: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ── 仓库结构定义 ──────────────────────────────────────────────────────────

# 「协议文件」= 主 Agent / subagent 在运行时真正遵循的规范文件。
# 对这些文件做严格检查（行号引用、死链一律 ERROR）。
PROTOCOL_FILES = {
    "WORKFLOW.md",
    "dispatch-protocol.md",
    "state-machine.md",
    "role-system.md",
    "loop-orchestration.md",
    "git-integration.md",
    "platform-notes.md",
    "LIMITATIONS.md",
    "README.md",
    "orchestrator-template.md",
}
PROTOCOL_DIRS = ("assets/",)  # 角色定义与模板也算协议文件

# 「叙事文件」= 历史评审 / 计划 / 决策记录。它们经常**引述**别处的旧问题
# （含已修复的行号引用），不应被当作活引用严格检查。仅做 YAML 解析等无害检查。
NARRATIVE_DIRS = ("docs/plans/", "docs/reviews/", "docs/design-notes/", "archived/")

# 引用扫描中要忽略的占位 / 示例 / 运行时生成路径（非仓库实文件）。
PATH_IGNORE_SUBSTRINGS = (
    "...",                      # docs/...md 之类省略写法
    "xxx",                      # {role_id}.md 示例
    "{",                        # 含占位符 {Txxx} / {agate_root}
    "docs/agents/",             # 项目侧 orchestrator 安装位置（示例）
    "docs/converse/",           # 项目侧示例
    "docs/notes/lessons.md",    # 运行时由 P8 生成
    "docs/tasks/",              # 运行时任务目录
    "docs/process/",            # 历史路径示例
    "docs/design/",             # 项目侧设计稿示例
    "tests/",                   # 项目侧测试目录示例
    "backend/", "src/", "app/", # 项目侧源码示例
)

# CHECK 5 的锚点白名单：已知的「N 个协议文件」声明，精确校验数字。
# 这是有意为之的白名单式检查——散文里的计数无法通用解析，只盯死已知关键锚点。
FILE_COUNT_ANCHORS = [
    {
        "file": "orchestrator-template.md",
        "expected": len(["WORKFLOW", "dispatch-protocol", "state-machine",
                          "role-system", "loop-orchestration", "git-integration",
                          "platform-notes", "LIMITATIONS"]),  # = 8
        "desc": "启动必读协议文件清单",
    },
    {
        "file": "state-machine.md",
        "expected": 8,
        "desc": "抗中断恢复重读的协议文件清单",
    },
]

# ── 工具函数 ──────────────────────────────────────────────────────────────

class Report:
    def __init__(self) -> None:
        self.errors: list[dict] = []
        self.warnings: list[dict] = []
        self.passed: list[str] = []

    def error(self, check: str, msg: str, loc: str = "") -> None:
        self.errors.append({"check": check, "msg": msg, "loc": loc})

    def warn(self, check: str, msg: str, loc: str = "") -> None:
        self.warnings.append({"check": check, "msg": msg, "loc": loc})

    def ok(self, check: str) -> None:
        self.passed.append(check)


def iter_md_files(root: Path):
    for p in sorted(root.rglob("*.md")):
        if ".git" in p.parts:
            continue
        yield p


def rel(root: Path, p: Path) -> str:
    return str(p.relative_to(root))


def is_protocol_file(relpath: str) -> bool:
    if relpath in PROTOCOL_FILES:
        return True
    return any(relpath.startswith(d) for d in PROTOCOL_DIRS)


def is_narrative_file(relpath: str) -> bool:
    return any(relpath.startswith(d) for d in NARRATIVE_DIRS)


def extract_code_blocks(text: str, lang: str):
    """返回 [(起始行号, 代码内容), ...]，匹配 ```{lang} ... ``` 块。"""
    blocks = []
    pattern = re.compile(rf"```{lang}\n(.*?)\n```", re.S)
    for m in pattern.finditer(text):
        start_line = text[: m.start()].count("\n") + 1
        blocks.append((start_line, m.group(1)))
    return blocks


# ── CHECK 1: YAML 代码块可解析 ────────────────────────────────────────────

def _sanitize_placeholders(code: str) -> str:
    """把 YAML 里的占位符替换成合法标量值，使含占位符的块也能被解析，
    从而仍能抓住缩进/结构错误（占位符本身不是错误，缩进才是）。"""
    # {Txxx} / {agate_root} / {任意中文或英文占位} → 用引号字符串包裹整个值有风险，
    # 改为把裸占位符替换成一个合法 token。仅替换花括号占位，不动其余内容。
    return re.sub(r"\{[^}]*\}", "PLACEHOLDER", code)


def _is_yaml_fragment(code: str) -> bool:
    """判断一个 yaml 块是否是「不该被整体解析的片段」，应跳过。

    跳过条件（任一命中）：
      - 含文档分隔符 --- / ... （是多文档或 frontmatter 片段，非单文档）
      - 全是注释 / 空行（说明性片段）
      - 首个非空非注释行就带缩进（是从某个上层 key 里截出来的子片段，无顶层 key）

    注意：含 {占位符} 不再直接跳过——改为在解析前 sanitize，以便仍能校验缩进。
    """
    lines = code.splitlines()
    for ln in lines:
        if ln.strip() in ("---", "..."):
            return True
    first_effective = None
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        first_effective = ln
        break
    if first_effective is None:
        return True
    if first_effective[:1] in (" ", "\t"):
        return True
    return False


def check_yaml_parseable(root: Path, rep: Report) -> None:
    found_any = False
    bad = 0
    for p in iter_md_files(root):
        relpath = rel(root, p)
        narrative = is_narrative_file(relpath)
        text = p.read_text(encoding="utf-8")
        for start_line, code in extract_code_blocks(text, "yaml"):
            if _is_yaml_fragment(code):
                continue
            found_any = True
            parse_target = _sanitize_placeholders(code)
            try:
                list(yaml.safe_load_all(parse_target))
            except yaml.YAMLError as e:
                first = str(e).splitlines()[0][:100]
                loc = f"{relpath}:{start_line}"
                # 「说明性示例」里的非致命瑕疵（YAML 保留字符 @ ` 作标量首字符等）
                # 降级为 WARNING。但缩进类错误（block mapping/scanning）即使在示例里
                # 也是真结构问题，保持 ERROR。
                indent_err = ("block mapping" in str(e)
                              or "block collection" in str(e)
                              or "mapping values" in str(e))
                illustrative = (("@" in code or "`" in code) or narrative) and not indent_err
                if illustrative:
                    rep.warn("CHECK1-yaml",
                             f"示例 YAML 不严格可解析（建议给含 @/特殊字符的标量加引号）: {first}",
                             loc)
                else:
                    bad += 1
                    rep.error("CHECK1-yaml",
                              f"YAML 代码块无法解析: {first}", loc)
    if found_any and bad == 0:
        rep.ok("CHECK1-yaml")


# ── CHECK 2: 仓库内文件引用真实存在 ──────────────────────────────────────

REF_RE = re.compile(r"(?<![\w/])((?:docs|assets|scripts)/[A-Za-z0-9_./\-]+\.(?:md|sh|ya?ml|py))")

def check_internal_refs(root: Path, rep: Report) -> None:
    broken = 0
    for p in iter_md_files(root):
        relpath = rel(root, p)
        # 叙事文件里的引用经常是引述别处，宽松处理：死链降级为 WARNING
        narrative = is_narrative_file(relpath)
        text = p.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in REF_RE.finditer(line):
                ref = m.group(1)
                if any(s in ref for s in PATH_IGNORE_SUBSTRINGS):
                    continue
                # 跨仓引用：同行注明「PeekView 仓库」「非本仓」则跳过
                if "PeekView" in line or "非本仓" in line:
                    continue
                target = root / ref
                if not target.exists():
                    loc = f"{relpath}:{lineno}"
                    if narrative:
                        rep.warn("CHECK2-refs",
                                 f"引用的文件不存在（叙事文件，可能是引述旧问题）: {ref}", loc)
                    else:
                        broken += 1
                        rep.error("CHECK2-refs",
                                  f"协议文件引用了不存在的文件: {ref}", loc)
    if broken == 0:
        rep.ok("CHECK2-refs")


# ── CHECK 3: 协议文件中的硬编码行号引用 ──────────────────────────────────

LINEREF_RE = re.compile(r"([A-Za-z0-9_\-]+\.md)\s+L\d+(?:-\d+)?")

def check_line_refs(root: Path, rep: Report) -> None:
    found = 0
    for p in iter_md_files(root):
        relpath = rel(root, p)
        # 只严格检查协议文件；叙事文件（评审/计划）引述行号是正常的
        if not is_protocol_file(relpath):
            continue
        text = p.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in LINEREF_RE.finditer(line):
                found += 1
                rep.error("CHECK3-lineref",
                          f"协议文件含硬编码行号引用 '{m.group(0)}' "
                          f"（应改用节标题引用，见 dispatch-protocol.md「输入导航原则」）",
                          f"{relpath}:{lineno}")
    if found == 0:
        rep.ok("CHECK3-lineref")


# ── CHECK 4: gate_commands 键集合跨文件一致 ──────────────────────────────

def _extract_gate_keys(text: str) -> set[str]:
    """从一个文件中抽出 gate_commands 块下的**直接子键**（P5/P5_e2e/P6...）。

    关键：只收集缩进**深于** gate_commands: 那一行、且是其直接子级的 'KEY:' 行，
    一旦缩进回到 gate_commands 同级或更浅，立即停止——否则会误吞后续的
    minimal_validation / files_to_read 等兄弟字段的子键。
    """
    keys: set[str] = set()
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^(\s*)gate_commands:\s*$", lines[i])
        if not m:
            i += 1
            continue
        base_indent = len(m.group(1))
        child_indent = None
        j = i + 1
        while j < len(lines):
            line = lines[j]
            if not line.strip():           # 空行：跳过但不终止
                j += 1
                continue
            indent = len(line) - len(line.lstrip())
            if indent <= base_indent:       # 回到同级/更浅 → 块结束
                break
            if child_indent is None:
                child_indent = indent       # 锁定直接子级缩进
            if indent == child_indent:      # 只收直接子键
                km = re.match(r"\s*([A-Za-z0-9_]+):", line)
                if km:
                    keys.add(km.group(1))
            j += 1
        i = j
    return keys

def check_gate_commands_keys(root: Path, rep: Report) -> None:
    sources = {
        "assets/execution-roles/architect.md": None,   # 权威来源
        "assets/templates/task-files.md": None,
        "assets/templates/dispatch-prompt.md": None,
    }
    for relpath in list(sources):
        f = root / relpath
        if f.exists():
            sources[relpath] = _extract_gate_keys(f.read_text(encoding="utf-8"))

    present = {k: v for k, v in sources.items() if v}
    if "assets/execution-roles/architect.md" not in present:
        rep.warn("CHECK4-gatekeys", "未找到 architect.md 的 gate_commands，跳过比对")
        return

    authoritative = present["assets/execution-roles/architect.md"]
    mismatched = False
    for relpath, keys in present.items():
        if relpath == "assets/execution-roles/architect.md":
            continue
        missing = authoritative - keys
        # 只对「权威里有、它没有」报警（缺字段才是 P1-2 那类 bug）；额外字段不报
        # P5_e2e 标注「ui_affected 时必填」，模板必须含它
        if missing:
            mismatched = True
            rep.error("CHECK4-gatekeys",
                      f"gate_commands 键集合不一致：{relpath} 缺少 "
                      f"{sorted(missing)}（权威来源 architect.md 含 {sorted(authoritative)}）",
                      relpath)
    if not mismatched:
        rep.ok("CHECK4-gatekeys")


# ── CHECK 5: 「N 个协议文件」计数 vs 实际列表 ────────────────────────────

def check_file_count_anchors(root: Path, rep: Report) -> None:
    all_ok = True
    for anchor in FILE_COUNT_ANCHORS:
        f = root / anchor["file"]
        if not f.exists():
            rep.warn("CHECK5-count", f"锚点文件不存在: {anchor['file']}")
            all_ok = False
            continue
        text = f.read_text(encoding="utf-8")
        # 找 "N 个...文件" 的声明
        declared = None
        for m in re.finditer(r"(\d+)\s*个[^。\n]*?文件", text):
            declared = int(m.group(1))
            break
        if declared is None:
            rep.warn("CHECK5-count",
                     f"{anchor['file']}: 未找到「N 个文件」声明，无法校验 {anchor['desc']}")
            all_ok = False
            continue
        if declared != anchor["expected"]:
            all_ok = False
            rep.error("CHECK5-count",
                      f"{anchor['file']}: {anchor['desc']} 声明 {declared} 个文件，"
                      f"但应为 {anchor['expected']} 个",
                      anchor["file"])
    if all_ok:
        rep.ok("CHECK5-count")


# ── CHECK 6: LICENSE 徽章 + gstack 归属 ──────────────────────────────────

def check_license(root: Path, rep: Report) -> None:
    ok = True
    readme = root / "README.md"
    if readme.exists():
        rtext = readme.read_text(encoding="utf-8")
        # 抓徽章里链接的目标 [...](LICENSE)
        for m in re.finditer(r"\!\[license[^\]]*\]\([^)]*\)\]\(([^)]+)\)", rtext):
            target = m.group(1).strip()
            if target.startswith("http"):
                continue
            if not (root / target).exists():
                ok = False
                rep.error("CHECK6-license",
                          f"README LICENSE 徽章指向不存在的文件: {target}", "README.md")

    lic = root / "LICENSE"
    if not lic.exists():
        ok = False
        rep.error("CHECK6-license", "仓库根目录缺少 LICENSE 文件", "LICENSE")
    else:
        ltext = lic.read_text(encoding="utf-8")
        if "MIT" not in ltext:
            ok = False
            rep.error("CHECK6-license", "LICENSE 未包含 MIT 声明", "LICENSE")
        # gstack 角色提取自 MIT 项目，需保留归属
        review_dir = root / "assets" / "review-roles"
        uses_gstack = review_dir.exists() and any(
            "gstack" in f.read_text(encoding="utf-8")
            for f in review_dir.glob("*.md")
        )
        if uses_gstack and "gstack" not in ltext:
            ok = False
            rep.error("CHECK6-license",
                      "review-roles 提取自 gstack(MIT)，但 LICENSE 未保留 gstack 归属",
                      "LICENSE")
    if ok:
        rep.ok("CHECK6-license")


# ── CHECK 7: README version badge 与最新 git tag 一致 ────────────────────────

def check_version_badge(root: Path, rep: Report) -> None:
    readme = root / "README.md"
    if not readme.exists():
        return
    rtext = readme.read_text(encoding="utf-8")
    m = re.search(r"badge/version-v(\d+\.\d+\.\d+)", rtext)
    if not m:
        rep.warn("CHECK7-version", "README.md 未找到 version badge", "README.md")
        return
    badge_ver = m.group(1)
    import subprocess
    try:
        tag = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, check=True, cwd=str(root),
        ).stdout.strip()
        tag_ver = tag.lstrip("v")
    except (subprocess.CalledProcessError, FileNotFoundError):
        rep.warn("CHECK7-version", "无法获取最新 git tag（仓库可能无 tag）", "README.md")
        return
    if badge_ver != tag_ver:
        rep.error("CHECK7-version",
                  f"README version badge v{badge_ver} != 最新 tag v{tag_ver}",
                  "README.md")
    else:
        rep.ok("CHECK7-version")


# ── 主流程 ────────────────────────────────────────────────────────────────

CHECKS = [
    ("CHECK 1  YAML 代码块可解析", check_yaml_parseable),
    ("CHECK 2  仓库内文件引用存在", check_internal_refs),
    ("CHECK 3  协议文件无硬编码行号", check_line_refs),
    ("CHECK 4  gate_commands 键集合一致", check_gate_commands_keys),
    ("CHECK 5  协议文件计数声明正确", check_file_count_anchors),
    ("CHECK 6  LICENSE 与 gstack 归属", check_license),
    ("CHECK 7  version badge 与 git tag", check_version_badge),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="agate 协议结构一致性检查")
    ap.add_argument("--root", default=".", help="仓库根目录（默认当前目录）")
    ap.add_argument("--strict", action="store_true", help="WARNING 也判失败")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not (root / "WORKFLOW.md").exists():
        print(f"ERROR: {root} 看起来不是 agate 仓库根（缺 WORKFLOW.md）", file=sys.stderr)
        return 1

    rep = Report()
    for _, fn in CHECKS:
        fn(root, rep)

    if args.json:
        print(json.dumps({
            "passed": rep.passed,
            "warnings": rep.warnings,
            "errors": rep.errors,
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 64)
        print("  agate 协议结构一致性检查 (P3-1)")
        print("=" * 64)
        for title, _ in CHECKS:
            key = "CHECK" + title.split()[1]
            status = "✅ PASS"
            if any(e["check"].startswith(key) for e in rep.errors):
                status = "❌ FAIL"
            elif any(w["check"].startswith(key) for w in rep.warnings):
                status = "⚠️  WARN"
            print(f"  {status}  {title}")
        print("-" * 64)
        if rep.errors:
            print(f"\n  ERROR ({len(rep.errors)}):")
            for e in rep.errors:
                loc = f" [{e['loc']}]" if e["loc"] else ""
                print(f"    ❌ {e['msg']}{loc}")
        if rep.warnings:
            print(f"\n  WARNING ({len(rep.warnings)}):")
            for w in rep.warnings:
                loc = f" [{w['loc']}]" if w["loc"] else ""
                print(f"    ⚠️  {w['msg']}{loc}")
        print()
        if not rep.errors and not rep.warnings:
            print("  🎉 全部检查通过，协议结构一致性无问题。")
        elif not rep.errors:
            print(f"  仅有 {len(rep.warnings)} 个 WARNING，无 ERROR。")
        print()

    if rep.errors:
        return 1
    if rep.warnings and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
