# tests/unit/test_debt_registry_closure.py — DEBT0007 登记闭合验证点（TAG0031 P3，簇 B）
# 被测：agate-workspace/debt/tech-debt.md 中 DEBT0007 条目的 status 字段
# 背景：本簇（测试隔离，DEBT0007）不改生产代码——`check-pruning.py` 的
#   `_staged_source_count` 隔离修复已由 TAG0024 commit e2357fc 落地，
#   test_check_pruning.py 既有 4 个用例（BDD-6）已确认全绿（见 P3-test-cases-test-isolation.md）。
# 本文件唯一职责：为 BDD-7（debt 登记闭合）提供一个可判定的红/绿验证点。
# 当前预期：FAIL（DEBT0007 status 仍为 open）。P4 实现阶段把 status 改为 closed 并补齐
#   closed_at/evidence 后，本用例才转绿——这是本簇范围内唯一允许存在的"真红灯"。

import re

import pytest


def _debt_tech_debt_path(agate_root):
    return agate_root.parent / "agate-workspace" / "debt" / "tech-debt.md"


def _extract_debt_block(text, debt_id):
    """从 tech-debt.md 中取出指定 DEBT id 的 yaml fence 内容（```yaml ... ``` 之间）。"""
    heading_pat = re.compile(r"^## " + re.escape(debt_id) + r"\s*$", re.MULTILINE)
    m = heading_pat.search(text)
    assert m is not None, f"{debt_id} 章节标题未在 tech-debt.md 中找到"
    rest = text[m.end():]
    fence_m = re.search(r"```yaml\n(.*?)\n```", rest, re.DOTALL)
    assert fence_m is not None, f"{debt_id} 章节下未找到 yaml fence 块"
    return fence_m.group(1)


def test_bdd_7_debt0007_status_closed_with_closure_fields(agate_root):
    """BDD-7：DEBT0007 debt 登记闭合。

    Given check-pruning.py 的 _staged_source_count 隔离修复（TAG0024 e2357fc）与
      BDD-6 补充验证均已确认生效（见本簇 P3-test-cases-test-isolation.md 记录的复跑结果）
    When 在 debt/tech-debt.md 更新 DEBT0007 条目
    Then status 改为 closed，追加 closed_at 与 closure 说明，evidence 追加指向
      e2357fc / test_p2_6f_... 与本任务 BDD-6 验证记录，登记格式与既有 DEBT0005/DEBT0006
      closed 条目一致（status/closed_at/evidence 追加块）

    当前状态（P3 设计时点）：status 仍为 open → 本用例预期 FAIL（真红灯）。
    P4 完成 debt 登记闭合动作后：status 改为 closed 且补齐 closed_at → 本用例转 PASS。
    """
    path = _debt_tech_debt_path(agate_root)
    assert path.is_file(), f"tech-debt.md 未找到：{path}"
    text = path.read_text(encoding="utf-8")

    block = _extract_debt_block(text, "DEBT0007")

    status_m = re.search(r"^status:\s*(\S+)\s*$", block, re.MULTILINE)
    assert status_m is not None, "DEBT0007 条目缺少 status 字段"
    status = status_m.group(1)
    assert status == "closed", (
        f"DEBT0007 status 现状为 {status!r}，closure 动作尚未执行"
        "（P4 完成后应为 closed，届时本用例转绿）"
    )

    # status 已为 closed 时，进一步核对登记格式与 DEBT0005/DEBT0006 先例一致
    # （closed_at 字段存在 + evidence 至少一条引用本任务/TAG0024 commit 或 BDD-6 记录）
    assert re.search(r"^closed_at:\s*\S+\s*$", block, re.MULTILINE), (
        "DEBT0007 status 已 closed 但缺少 closed_at 字段（应与 DEBT0005/DEBT0006 先例一致）"
    )
    assert (
        "e2357fc" in block or "TAG0031" in block or "BDD-6" in block
    ), (
        "DEBT0007 evidence 未见指向 e2357fc / TAG0031 / BDD-6 的 closure 引用，"
        "登记格式与先例（DEBT0005/DEBT0006 closure 说明）不一致"
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
