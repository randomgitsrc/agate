# tests/unit/test_skeleton_template_stack_neutral.py — TAG0007 BDD-2
# 骨架模板技术栈参数化：assets/templates/skeleton-template.md（P2-design.md §1.1 新增文件，
# 尚未产出）不得写死具体语言/框架的目录名（如 src/components、src/include），须以
# "按技术栈可选的候选目录集合 + 项目侧声明"的参数化形式表达，具体技术栈的目录选择由
# 项目自己决定（ADR-003「最小约定——不绑定技术栈」）。
#
# 本测试是**回归防线**（P2-design.md §1.3 R7），黑名单覆盖 BDD-2 原文举例的两个具体
# 反例（src/components、src/include）+ 常见框架目录名（src/hooks、src/pages），并要求
# 正面存在"候选目录集合"类参数化关键词；不是穷尽式语义证明，不能覆盖所有可能的技术栈
# 硬编码写法，只防止未来编辑把模板改回硬编码。
#
# 当前 assets/templates/skeleton-template.md 尚不存在（P4 未开始），本文件全部用例
# 目前应因 assert ... .is_file() 失败而红灯（AssertionError，非 SyntaxError）。

# BDD-2 原文举例的两个具体反例 + 常见框架目录名黑名单（P2-design.md §1.3 R7 已列出）
_STACK_SPECIFIC_BLACKLIST = [
    "src/components",
    "src/include",
    "src/hooks",
    "src/pages",
]

# 参数化关键词：模板须显式表达"候选目录集合 + 项目侧声明"的开放式设计，而非
# 具体技术栈目录名的强制清单
_PARAMETERIZATION_KEYWORDS = [
    "候选目录",
    "技术栈",
]


def _template_path(agate_assets):
    return agate_assets / "templates" / "skeleton-template.md"


def test_bdd_2_skeleton_template_exists(agate_assets):
    template = _template_path(agate_assets)
    assert template.is_file(), f"骨架模板文件不存在: {template}"


def test_bdd_2_skeleton_template_no_hardcoded_stack_dirs(agate_assets):
    template = _template_path(agate_assets)
    assert template.is_file(), f"骨架模板文件不存在: {template}"
    text = template.read_text(encoding="utf-8")
    for blacklisted in _STACK_SPECIFIC_BLACKLIST:
        assert blacklisted not in text, (
            f"骨架模板不得硬编码具体技术栈目录名 {blacklisted!r}"
            "（BDD-2：须以候选目录集合 + 项目侧声明的参数化形式表达）"
        )


def test_bdd_2_skeleton_template_has_parameterization_markers(agate_assets):
    template = _template_path(agate_assets)
    assert template.is_file(), f"骨架模板文件不存在: {template}"
    text = template.read_text(encoding="utf-8")
    for keyword in _PARAMETERIZATION_KEYWORDS:
        assert keyword in text, f"骨架模板缺少参数化关键词 {keyword!r}（BDD-2 要求）"
