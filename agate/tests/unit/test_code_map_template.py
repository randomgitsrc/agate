# tests/unit/test_code_map_template.py — TAG0007 BDD-6
# CODE-MAP 维护物的存在与初始化：assets/templates/code-map-template.md（P2-design.md §1.1
# 新增文件，尚未产出）须含模块、层、依赖方向、关键文件、约定五类必填字段，初始内容可为
# 占位声明，只要求五类字段齐全存在（不要求内容完备）。
#
# 当前 assets/templates/code-map-template.md 尚不存在（P4 未开始），本文件全部用例
# 目前应因 assert ... .is_file() 失败而红灯（AssertionError，非 SyntaxError）。

# BDD-6 要求的五类必填字段标题（模块/层/依赖方向/关键文件/约定）
_REQUIRED_HEADINGS = ["模块", "层", "依赖方向", "关键文件", "约定"]


def _template_path(agate_assets):
    return agate_assets / "templates" / "code-map-template.md"


def test_bdd_6_code_map_template_exists(agate_assets):
    template = _template_path(agate_assets)
    assert template.is_file(), f"CODE-MAP 模板文件不存在: {template}"


def test_bdd_6_code_map_template_has_five_required_headings(agate_assets):
    template = _template_path(agate_assets)
    assert template.is_file(), f"CODE-MAP 模板文件不存在: {template}"
    text = template.read_text(encoding="utf-8")
    for heading in _REQUIRED_HEADINGS:
        assert heading in text, (
            f"CODE-MAP 模板缺少必填字段标题 {heading!r}（BDD-6 要求模块/层/依赖方向/"
            "关键文件/约定五类字段齐全存在）"
        )
