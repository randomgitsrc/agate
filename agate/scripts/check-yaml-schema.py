#!/usr/bin/env python3
"""check-yaml-schema.py — rules/*.yaml 对 rules/schema/*.json 的 draft-07 子集校验器（TAG0021 M0）

被测契约（P2-design §3.2 / P3 BDD-1）：校验 AGATE_ROOT/rules/{phases,dispatch,roles}.yaml
对 rules/schema/{phases,dispatch,roles}.schema.json：
  * 全部 YAML 合法且过 schema → exit 0
  * 任一非法字段（additionalProperties 拒绝）/ 错误枚举 / 错误类型 / 缺 required /
    schema 自身损坏（非法 JSON）→ exit 非 0

支持的 draft-07 子集：type / required / enum / properties / items / additionalProperties /
minItems。数值刻度的 minimum/exclusiveMinimum 不用（P2-design §3.2，防子集实现膨胀）。
手写校验（不依赖 jsonschema 包，依赖清单仅 pyyaml+Pillow），机制参照
agate-frontmatter-check.py 的 SCHEMAS（required/enums/types/min_values 手写遍历）。

R5 schema 自身健全性自检：schema 根必须是 object（type=object + properties + required），
required 引用的键必须在 properties 中声明——防 schema 形同虚设。

用法：check-yaml-schema.py（无参数）。AGATE_ROOT 解析链 = env → 项目声明 → current →
脚本路径上溯（agate_common.resolve_agate_root）。
输出：SCHEMA-<file>: OK / SCHEMA-<file>: ERROR <path> <msg>（仿 rep 编号风格）。
退出：0 = 全过；1 = 任一 ERROR（含解析失败 / schema 损坏）。

平台无关（BDD-16）：无裸解释器、无硬编码 PATH、无 /tmp、无软链假设；文本 I/O 显式 utf-8。
Python 3.8+（无 match / str.removeprefix）。
"""

import json
import os
import sys

try:
    import yaml
    from agate_common import resolve_agate_root
except ImportError:
    sys.stderr.write("check-yaml-schema.py: 需要 pyyaml 与 agate_common（agate 脚本公共库）。pip install pyyaml 或确认在 agate/scripts/ 下运行\n")
    sys.exit(1)

# (规则文件基名, yaml 文件名, schema 文件名)
_RULES = (
    ("phases", "phases.yaml", "phases.schema.json"),
    ("dispatch", "dispatch.yaml", "dispatch.schema.json"),
    ("roles", "roles.yaml", "roles.schema.json"),
)


def _type_ok(value, type_name):
    """draft-07 type 判定（bool 是 int 子类，integer 须排除 bool——YAML true/false 陷阱）。"""
    if type_name == "string":
        return isinstance(value, str)
    if type_name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name == "boolean":
        return isinstance(value, bool)
    if type_name == "array":
        return isinstance(value, list)
    if type_name == "object":
        return isinstance(value, dict)
    return True


def _validate_value(value, schema, path, errors):
    """递归校验单个值 vs 子集 schema；错误追加到 errors（(path, msg) 列表）。"""
    type_name = schema.get("type")
    if type_name and not _type_ok(value, type_name):
        errors.append((path, "类型应为 %s，实际 %s" % (type_name, type(value).__name__)))
        return
    if "enum" in schema and value not in schema["enum"]:
        errors.append((path, "值 %r 不在枚举 %s" % (value, schema["enum"])))
    if type_name == "object" and isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append((path, "缺 required 字段 %s" % key))
        properties = schema.get("properties", {})
        for key, item in value.items():
            child = "%s.%s" % (path, key) if path else key
            if key in properties:
                _validate_value(item, properties[key], child, errors)
            elif schema.get("additionalProperties") is False:
                errors.append((path, "未知字段 %s（additionalProperties=false）" % key))
    elif type_name == "array" and isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append((path, "数组长度 %d < minItems %d" % (len(value), schema["minItems"])))
        items = schema.get("items")
        if items:
            for idx, item in enumerate(value):
                _validate_value(item, items, "%s[%d]" % (path, idx), errors)


def _schema_self_check(file_name, schema):
    """R5：schema 自身健全性（根 object + properties + required 引用闭合）。"""
    errs = []
    if not isinstance(schema, dict):
        errs.append(("", "schema 根不是对象（损坏）"))
        return errs
    if schema.get("type") != "object":
        errs.append(("", "schema 根 type 应为 object"))
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        errs.append(("", "schema 根缺 properties（应为本文件顶层键的 dict）"))
    required = schema.get("required")
    if not isinstance(required, list):
        errs.append(("", "schema 根缺 required（list）"))
    elif isinstance(properties, dict):
        for key in required:
            if key not in properties:
                errs.append(("", "required 字段 %s 未在 properties 中声明（schema 自相矛盾）" % key))
    return errs


def _check_one(file_name, yaml_path, schema_path):
    """校验单个 rules 文件对 → ERROR 列表（空 = OK）。"""
    errors = []
    data = None
    schema = None
    if not os.path.isfile(yaml_path):
        errors.append(("", "文件缺失 %s" % os.path.relpath(yaml_path)))
    else:
        try:
            with open(yaml_path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
        except Exception as exc:  # noqa: BLE001  YAML 解析失败（scanner/parser error）
            errors.append(("", "YAML 解析失败: %s" % exc))
    if not os.path.isfile(schema_path):
        errors.append(("", "文件缺失 %s" % os.path.relpath(schema_path)))
    else:
        try:
            with open(schema_path, encoding="utf-8") as fh:
                schema = json.load(fh)
        except Exception as exc:  # noqa: BLE001  非法 JSON（R5 损坏 schema 兜底）
            errors.append(("", "schema JSON 解析失败: %s" % exc))
    if schema is not None:
        errors.extend(_schema_self_check(file_name, schema))
        if data is not None and isinstance(schema, dict):
            _validate_value(data, schema, "", errors)
    return errors


def _resolve_root():
    """AGATE_ROOT 解析：env 优先（返回原值）→ agate_common 四层链。"""
    env_root = os.environ.get("AGATE_ROOT", "")
    if env_root:
        return env_root
    try:
        return resolve_agate_root(__file__)
    except Exception:  # noqa: BLE001  agate_common 不可用时兜底脚本路径上溯
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    root = _resolve_root()
    if not root:
        sys.stderr.write("FATAL: 无法解析 AGATE_ROOT（env / .agate-version / current / 脚本上溯均不可用）\n")
        sys.exit(1)
    rules_dir = os.path.join(root, "rules")
    if not os.path.isdir(rules_dir):
        sys.stderr.write("FATAL: AGATE_ROOT=%s 下缺少 rules/ 目录\n" % root)
        sys.exit(1)

    any_error = False
    for file_name, yaml_name, schema_name in _RULES:
        yaml_path = os.path.join(rules_dir, yaml_name)
        schema_path = os.path.join(rules_dir, "schema", schema_name)
        errors = _check_one(file_name, yaml_path, schema_path)
        if errors:
            any_error = True
            for path, msg in errors:
                loc = "%s " % path if path else ""
                sys.stdout.write("SCHEMA-%s: ERROR %s%s\n" % (file_name, loc, msg))
        else:
            sys.stdout.write("SCHEMA-%s: OK\n" % file_name)
    sys.exit(1 if any_error else 0)


if __name__ == "__main__":
    main()