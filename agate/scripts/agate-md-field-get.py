#!/usr/bin/env python3
"""从 P1/P2 markdown 提取字段（py 抽离共享工具，v2.0 T001 流 A 双读改造）。

从 FILE 环境变量读文件路径，按子命令（op）提取字段值。FILE 不存在/不可读时
抛异常（FileNotFoundError）→非零退出（由 bash 调用方 2>/dev/null || echo 兜底）。

双读判别契约（P2-design.md §3.1.2，FIND-1 修订，字段级 presence 检测）：
  - 文件头 "---" frontmatter 块存在、可解析为 dict、且该 op 对应字段在
    frontmatter 中存在（key 存在且值非 null）→ 取 frontmatter 值（格式化后输出）
  - 否则（无 frontmatter 块 / 解析失败 / 字段不在 frontmatter 中 / 值为 null）
    → 正则回退（v0.35 行为，扫描全文，兼容旧格式正文内嵌字段）

用法（op 列表）：
  risk_level                 frontmatter 字符串 / 正文 "risk_level: low|medium|high"
  ui_affected                frontmatter bool（归一化输出 "true"/"false"）/ 正文 "ui_affected: true|false"
  phases                     frontmatter list（内联或块式）/ 正文内联 "[P1, P2]" 或块式 "- Pn"
  candidate_count             frontmatter int（P2-design.md）/ 正文 "candidate_count: N"
  packages / domains         frontmatter list（空格连接）/ 正文内联或块式列表
  override / internal_only_reason / 跳过风险   presence 语义字符串字段
  internal_only / design_trivial               presence 语义 bool 字段
  coupling_checklist / follows_existing_pattern  presence 语义 list 字段
"""

import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("agate-md-field-get: 需要 pyyaml\n")
    sys.exit(1)


# bool 字段：_format_value 归一化为恰好 "true"/"false"（小写，FIND-4 落地）。
# 下游 check-p6-evidence.sh:64 / check-p6-provenance.sh:155 做精确字符串匹配，
# 依赖此处输出小写，不能是 Python str(bool) 的 "True"/"False"。
BOOL_FIELDS = frozenset({"ui_affected", "internal_only", "design_trivial"})

# list 字段：frontmatter 值（YAML list）格式化为空格连接字符串。
LIST_FIELDS = frozenset({
    "phases", "packages", "domains",
    "coupling_checklist", "follows_existing_pattern",
})

# int 字段：格式化为 str(int)。
INT_FIELDS = frozenset({"candidate_count"})

# presence 语义的纯字符串字段：key 存在且值非 null → 输出值原样，否则空。
STRING_FIELDS = frozenset({"override", "internal_only_reason", "跳过风险", "risk_level"})


def _read():
    with open(os.environ["FILE"]) as f:
        return f.read()


def _read_frontmatter(text):
    """只认文件头 --- 块；无块或解析失败返回 None（由校验器在 pre-commit 拦截坏格式）。"""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    try:
        return yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return None


def _format_value(value, field):
    if field in BOOL_FIELDS:
        return str(value).lower() if isinstance(value, bool) else str(value).lower()
    if field in LIST_FIELDS:
        if isinstance(value, list):
            return " ".join(str(v) for v in value)
        return str(value)
    if field in INT_FIELDS:
        return str(value)
    return str(value)


def _regex_scalar(text, pattern):
    m = re.search(pattern, text)
    return m.group(1) if m else ""


def _regex_list(text, field):
    # 内联块式列表（[a, b, c]）
    m = re.search(re.escape(field) + r":\s*\[([^\]]+)\]", text)
    if m:
        items = [p.strip() for p in m.group(1).split(",") if p.strip()]
        return " ".join(items)
    # 块式列表（每行 "- item"）
    m = re.search(re.escape(field) + r":\s*\n((?:[ \t]+-[ \t]+\S+[ \t]*\n)+)", text)
    if m:
        items = re.findall(r"-\s+(\S+)", m.group(1))
        return " ".join(items)
    return ""


def _regex_fallback(text, op):
    if op == "risk_level":
        return _regex_scalar(text, r"risk_level:\s*(low|medium|high)")
    if op == "ui_affected":
        return _regex_scalar(text, r"ui_affected:\s*(true|false)")
    if op in LIST_FIELDS:
        return _regex_list(text, op)
    if op == "candidate_count":
        return _regex_scalar(text, r"candidate_count:\s*(\d+)")
    if op in ("internal_only", "design_trivial"):
        return _regex_scalar(text, re.escape(op) + r":\s*(true|false)")
    if op in ("override", "internal_only_reason", "跳过风险"):
        m = re.search(re.escape(op) + r":\s*(.+)", text)
        if not m:
            return ""
        return m.group(1).strip().strip('"').strip("'")
    return ""


def _get(text, op):
    fm = _read_frontmatter(text)
    # 字段级 presence 检测：frontmatter 是 dict 且 key 存在且值非 null → 取 frontmatter
    if isinstance(fm, dict) and op in fm and fm[op] is not None:
        return _format_value(fm[op], op)
    return _regex_fallback(text, op)  # 字段不在 frontmatter → 正则回退


KNOWN_OPS = (
    BOOL_FIELDS | LIST_FIELDS | INT_FIELDS | STRING_FIELDS
)


def main():
    op = sys.argv[1]
    text = _read()
    if op not in KNOWN_OPS:
        sys.stderr.write("agate-md-field-get: unknown op {}\n".format(op))
        sys.exit(2)
    print(_get(text, op))


if __name__ == "__main__":
    main()
