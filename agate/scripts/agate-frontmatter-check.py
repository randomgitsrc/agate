#!/usr/bin/env python3
"""校验 P1/P2/P6/P7 frontmatter schema（v2.0 T001 流 A，P2-design.md §3.1.3）。

范式仿 agate-state-yaml-check.py：从 FILE env 读文件路径，输出错误行
（每行一个），无错误输出空。由 check-frontmatter.sh 薄壳判非空拦截 exit 1。

判别契约（FIND-1，字段级/文件级两层）：
  - 文件名判定 schema（P1-requirements.md / P2-design.md / P6-acceptance.md /
    P7-consistency.md 之外的文件不校验，exit 0）
  - frontmatter 块不存在 → 旧格式，exit 0（BDD-9 兼容，不误伤在途任务）
  - 块存在但 yaml.safe_load 结果不是 dict（FIND-5，如单行全角冒号纯量）→
    一律报错"frontmatter 必须为 key: value 映射"
  - dict 中含"该文件 schema 对应迁移字段集"（而非全集）任意一个 → 新格式 →
    走必填/枚举/类型/嵌套深度校验；否则 exit 0（旧格式，字段都在正文）
"""

import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("agate-frontmatter-check: 需要 pyyaml\n")
    sys.exit(1)


# 按文件名分类的 schema 定义。migrated_keys 对应 P2-design.md §3.1.2
# MIGRATED_KEYS_BY_SCHEMA 的按文件名子集（该常量在此校验器内消费，
# agate-md-field-get.py 的读取路由不依赖它，仅本文件级判定使用）。
SCHEMAS = {
    "P1-requirements.md": {
        "migrated_keys": frozenset({
            "risk_level", "phases", "packages", "domains", "override",
            "implicit_coupling", "coupling_checklist", "internal_only",
            "internal_only_reason", "跳过风险", "design_trivial",
            "follows_existing_pattern", "need_confirm_resolved",
            "suggest_resolved", "scope_resolved", "change_type",
            "ui_render_shape", "ui_ux_dimensions",
        }),
        "required": ("risk_level", "phases", "packages", "domains"),
        "enums": {"risk_level": ("low", "medium", "high"), "change_type": ("refactor",)},
        "types": {
            "risk_level": str,
            "phases": list,
            "packages": list,
            "domains": list,
            "implicit_coupling": bool,
            "internal_only": bool,
            "design_trivial": bool,
            "coupling_checklist": list,
            "follows_existing_pattern": list,
            "change_type": str,
            "ui_render_shape": str,
            "ui_ux_dimensions": list,
        },
        "min_values": {},
    },
    "P2-design.md": {
        "migrated_keys": frozenset({
            "candidate_count", "packages", "domains", "ui_affected", "ui_design_section",
        }),
        "required": ("candidate_count", "packages", "domains", "ui_affected"),
        "enums": {},
        "types": {
            "candidate_count": int,
            "packages": list,
            "domains": list,
            "ui_affected": bool,
            "ui_design_section": bool,
        },
        "min_values": {"candidate_count": 1},
    },
    "P6-acceptance.md": {
        "migrated_keys": frozenset({"pass", "fail", "ui_affected", "regression_pass"}),
        "required": ("pass", "fail", "ui_affected"),
        "enums": {},
        "types": {
            "pass": int,
            "fail": int,
            "ui_affected": bool,
            "regression_pass": bool,
        },
        "min_values": {"pass": 0, "fail": 0},
    },
    "P7-consistency.md": {
        "migrated_keys": frozenset({
            "blocker_count", "deviation_count", "deviation_critical_count",
            "design_gap_count", "design_gap_reviewed_count",
        }),
        "required": (
            "blocker_count", "deviation_count", "deviation_critical_count",
            "design_gap_count", "design_gap_reviewed_count",
        ),
        "enums": {},
        "types": {
            "blocker_count": int,
            "deviation_count": int,
            "deviation_critical_count": int,
            "design_gap_count": int,
            "design_gap_reviewed_count": int,
        },
        "min_values": {
            "blocker_count": 0,
            "deviation_count": 0,
            "deviation_critical_count": 0,
            "design_gap_count": 0,
            "design_gap_reviewed_count": 0,
        },
    },
}

MAX_DEPTH = 3


def _value_depth(v):
    """标量深度 0；dict/list 深度 = 1 + 子项最大深度（空容器记 1）。"""
    if isinstance(v, dict):
        if not v:
            return 1
        return 1 + max(_value_depth(x) for x in v.values())
    if isinstance(v, list):
        if not v:
            return 1
        return 1 + max(_value_depth(x) for x in v)
    return 0


def _extract_frontmatter_block(text):
    """只认文件头 --- 块；无块（或未闭合）返回 None。"""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    return text[4:end]


def _check(basename, schema, data):
    errors = []

    for field in schema["required"]:
        if field not in data or data[field] is None:
            errors.append(f"{basename}:{field}: 缺必填字段 {field}")

    for field, allowed in schema["enums"].items():
        if field in data and data[field] is not None and data[field] not in allowed:
            errors.append(
                "{}:{}: 非法值 {!r}（合法值: {}）".format(
                    basename, field, data[field], ", ".join(allowed)
                )
            )

    for field, expected_type in schema["types"].items():
        if field not in data or data[field] is None:
            continue
        value = data[field]
        if expected_type is bool:
            if not isinstance(value, bool):
                errors.append(
                    f"{basename}:{field}: 类型错误（应为 bool，实际 {type(value).__name__}）"
                )
        elif expected_type is int:
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(
                    f"{basename}:{field}: 类型错误（应为 int，实际 {type(value).__name__}）"
                )
            else:
                min_v = schema["min_values"].get(field)
                if min_v is not None and value < min_v:
                    errors.append(
                        f"{basename}:{field}: 值 {value} 小于最小值 {min_v}"
                    )
        elif expected_type is list:
            if not isinstance(value, list):
                errors.append(
                    f"{basename}:{field}: 类型错误（应为 list，实际 {type(value).__name__}）"
                )
        elif expected_type is str and not isinstance(value, str):
            errors.append(
                f"{basename}:{field}: 类型错误（应为 str，实际 {type(value).__name__}）"
            )

    for field, value in data.items():
        if _value_depth(value) > MAX_DEPTH:
            errors.append(
                f"{basename}:{field}: 嵌套深度超过 {MAX_DEPTH} 层"
            )

    return errors


def main():
    file_path = os.environ["FILE"]
    basename = os.path.basename(file_path)
    schema = SCHEMAS.get(basename)
    if schema is None:
        return  # 非目标 4 类文件，不校验

    # P4-review.md CRITICAL fix：兜底捕获 open()/yaml.safe_load()/_check()（含其内部
    # _value_depth() 无保护递归）可能抛出的任意异常（尤其 RecursionError——深嵌套结构
    # 解析会撞 Python 递归栈上限，是 RuntimeError 的子类而非 yaml.YAMLError 的子类；
    # 以及 UnicodeDecodeError——非 UTF-8 文件内容），确保任何未预见异常都转成一行错误
    # 输出打到 stdout，而不是让异常穿透到 check-frontmatter.sh 被 2>/dev/null || true
    # 静默吞掉（那样会让"深到能让解析器自己崩溃"的坏格式被误判为放行）。
    try:
        with open(file_path, encoding="utf-8") as f:
            text = f.read().replace("\r\n", "\n")

        block = _extract_frontmatter_block(text)
        if block is None:
            return  # 无 frontmatter 块 → 旧格式，BDD-9 兼容，不触发必填校验

        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as e:
            print(str(e))
            return

        if data is None:
            return  # frontmatter 块为空 → 视同旧格式

        if not isinstance(data, dict):
            # FIND-5：safe_load 结果非 dict（无 YAMLError，如单行全角冒号纯量）→ 硬拦截
            print(
                f"{basename}: frontmatter 必须为 key: value 映射（当前解析为 {type(data).__name__}）"
            )
            return

        if not (schema["migrated_keys"] & set(data.keys())):
            return  # 无该 schema 迁移字段 → 旧格式（字段在正文），不触发必填校验

        errors = _check(basename, schema, data)
        if errors:
            print("\n".join(errors))
    except Exception as e:
        print(f"{basename}: frontmatter 处理异常（{e}）")


if __name__ == "__main__":
    main()
