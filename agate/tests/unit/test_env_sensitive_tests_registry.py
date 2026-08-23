# tests/unit/test_env_sensitive_tests_registry.py — 环境敏感测试集中清单存在性
# （TAG0023 RM-AG0044，BDD-10）
# 被测：agate/tests/ENV-SENSITIVE-TESTS.md（P2-design.md §2.3 新建集中清单，登记
#   test_id / 根因分类 / 状态 / 关联 commit 或 RM 编号，初始至少含 test_bdd_7 /
#   test_bdd_25 / test_bdd_14 三条目）。
# 当前该文件尚未创建（P4 待新建），本用例红灯（assert doc.is_file() 失败）。


def test_bdd_10_env_sensitive_tests_registry_exists_with_required_entries(agate_root):
    doc = agate_root / "tests" / "ENV-SENSITIVE-TESTS.md"
    assert doc.is_file(), (
        "ENV-SENSITIVE-TESTS.md 尚未创建（RM-AG0044 环境敏感测试集中清单，"
        "P2-design.md §2.3，P4 待新建）"
    )
    text = doc.read_text(encoding="utf-8")
    for test_id in ("test_bdd_7", "test_bdd_25", "test_bdd_14"):
        assert test_id in text, f"清单缺少条目 {test_id}"
    for field_keyword in ("根因分类", "状态"):
        assert field_keyword in text, f"清单缺少字段 {field_keyword}"
