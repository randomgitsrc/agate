# tests/unit/test_self_gate_naming_docs.py — SELF-GATE 审查文件命名去重条文守护（TAG0017 P3，
# 批次 fg2-self-gate-naming，DEBT0011）
# 覆盖 P1-requirements.md BDD-7（同日不同任务的 SELF-GATE 审查文件不再同名覆盖：命名模板补
# `{task_id}` 占位符）/ BDD-8（protocol-alignment-review subagent Write 前检查目标路径存在性，
# 避免误覆盖历史记录）。
#
# 验收对象层次说明：本文件只断言"协议文档是否已把命名模板改为含 `{task_id}`" /
# "协议文档是否已声明 Write 前存在性检查逻辑"——不断言任何一次真实任务运行时产物（那是 P6
# verifier 的职责）。BDD-7 的"两次生成的文件名不同"这一行为通过 test_bdd_7_naming_template_
# produces_distinct_filenames_for_different_task_ids 用纯字符串格式化模拟验证，不依赖真实
# subagent 调用。
#
# 路径约定（P2-design.md §7 files_to_read「fg2-self-gate-naming」节，P2 review 已核实订正）：
#   - SELF-GATE.md 在仓库根目录，无 `agate/` 前缀 —— 即 agate_root.parent / "SELF-GATE.md"
#     （agate_root fixture 指向 agate/ 子目录，tests/conftest.py:306）
#   - agate/assets/review-roles/protocol-alignment-review.md 在 agate_root 下
#
# 红灯预期：SELF-GATE.md 当前命名模板（文件类型表 L53/54 + 变更触发模板 L133/143 + 全量审查
# 模板 L183/193）均为 `docs/reviews/agate-alignment-{date}-{NN}.progress.md` /
# `docs/reviews/agate-alignment-review-{date}.md`，不含 `{task_id}`；
# protocol-alignment-review.md 全文无"Write 前检查目标路径是否已存在"逻辑说明。
# 本文件全部测试函数当前预期失败，P4 implementer 改完两处文档后应转绿。

def _read_repo(agate_root, *parts):
    """读取仓库根（agate_root 的父目录）下的文件，如 SELF-GATE.md（无 agate/ 前缀）。"""
    return agate_root.parent.joinpath(*parts).read_text(encoding="utf-8")


def _read(agate_root, *parts):
    """读取 agate/ 协议本体下的文件（agate_root 内）。"""
    return agate_root.joinpath(*parts).read_text(encoding="utf-8")


SELF_GATE_PARTS = ("SELF-GATE.md",)
PROTOCOL_ALIGNMENT_REVIEW_PARTS = ("assets", "review-roles", "protocol-alignment-review.md")


# ── BDD-7：命名模板补 `{task_id}`，同日不同任务不再同名覆盖 ──────────────────


def test_bdd_7_self_gate_path_has_no_agate_prefix(agate_root):
    """约束校验：SELF-GATE.md 必须在仓库根目录（无 agate/ 前缀），否则本文件其余断言的
    路径解析前提就是错的（此前 P2 阶段曾误写成 agate/SELF-GATE.md 被 review 打回）。"""
    path = agate_root.parent / "SELF-GATE.md"
    assert path.is_file(), f"SELF-GATE.md 应位于仓库根目录：{path}"
    wrong_path = agate_root / "SELF-GATE.md"
    assert not wrong_path.is_file(), (
        "SELF-GATE.md 不应存在于 agate/ 子目录下（这是此前 P2 review 打回过的路径错误）"
    )


def test_bdd_7_file_type_table_progress_filename_has_task_id(agate_root):
    """SELF-GATE.md 文件约定表（Layer 1 开头，约 L48-60）：留痕文件命名模板应含 `{task_id}`。"""
    content = _read_repo(agate_root, *SELF_GATE_PARTS)
    assert "文件约定" in content
    assert "{task_id}" in content, (
        "SELF-GATE.md 文件类型表的留痕文件命名模板当前不含 {task_id} 占位符（DEBT0011 待修）"
    )
    assert "agate-alignment-{date}-{task_id}-{NN}.progress.md" in content, (
        "留痕文件命名模板应改为 docs/reviews/agate-alignment-{date}-{task_id}-{NN}.progress.md"
    )


def test_bdd_7_file_type_table_result_filename_has_task_id(agate_root):
    """SELF-GATE.md 文件约定表：成果文件命名模板应含 `{task_id}`。"""
    content = _read_repo(agate_root, *SELF_GATE_PARTS)
    assert "agate-alignment-review-{date}-{task_id}.md" in content, (
        "成果文件命名模板应改为 docs/reviews/agate-alignment-review-{date}-{task_id}.md"
    )


def test_bdd_7_change_triggered_template_naming_has_task_id(agate_root):
    """SELF-GATE.md 变更触发模式派发模板（约 L71-147）：留痕/成果文件命名模板行
    （原 L133/L143）应各自含 `{task_id}`。"""
    content = _read_repo(agate_root, *SELF_GATE_PARTS)
    assert "变更触发模式" in content
    section_start = content.index("变更触发模式")
    section_end = content.index("全量审查模式")
    section = content[section_start:section_end]
    assert "留痕文件：" in section
    assert "docs/reviews/agate-alignment-{date}-{task_id}-{NN}.progress.md" in section, (
        "变更触发模式派发模板的留痕文件命名模板（原 L133）当前不含 {task_id}"
    )
    assert "docs/reviews/agate-alignment-review-{date}-{task_id}.md" in section, (
        "变更触发模式派发模板的成果文件命名模板（原 L143）当前不含 {task_id}"
    )


def test_bdd_7_full_review_template_naming_has_task_id(agate_root):
    """SELF-GATE.md 全量审查模式派发模板（约 L149-197）：留痕/成果文件命名模板行
    （原 L183/L193）应各自含 `{task_id}`。"""
    content = _read_repo(agate_root, *SELF_GATE_PARTS)
    assert "全量审查模式" in content
    section_start = content.index("全量审查模式")
    section = content[section_start:]
    assert "留痕文件：" in section
    assert "docs/reviews/agate-alignment-{date}-{task_id}-{NN}.progress.md" in section, (
        "全量审查模式派发模板的留痕文件命名模板（原 L183）当前不含 {task_id}"
    )
    assert "docs/reviews/agate-alignment-review-{date}-{task_id}.md" in section, (
        "全量审查模式派发模板的成果文件命名模板（原 L193）当前不含 {task_id}"
    )


def test_bdd_7_naming_template_produces_distinct_filenames_for_different_task_ids():
    """BDD-7 核心行为的纯字符串拼接模拟：两个不同 task_id 在同一日期各自按新命名模板
    生成的留痕文件名 / 成果文件名互不相同。这条测试本身不依赖协议文档是否已改——它验证
    的是"命名模板一旦补上 {task_id} 占位符，即可产出不同文件名"这一逻辑本身可判定；
    真正验证协议文档已切换到该模板的是上面几条 test_bdd_7_*_has_task_id。"""
    progress_template = "docs/reviews/agate-alignment-{date}-{task_id}-{NN}.progress.md"
    result_template = "docs/reviews/agate-alignment-review-{date}-{task_id}.md"

    date = "2026-08-20"
    progress_a = progress_template.format(date=date, task_id="TAG0015", NN="01")
    progress_b = progress_template.format(date=date, task_id="TAG0016", NN="01")
    result_a = result_template.format(date=date, task_id="TAG0015")
    result_b = result_template.format(date=date, task_id="TAG0016")

    assert progress_a != progress_b
    assert result_a != result_b


# ── BDD-8：subagent Write 前检查目标路径存在性 ──────────────────────────────


def test_bdd_8_protocol_alignment_review_has_write_precheck_logic(agate_root):
    """agate/assets/review-roles/protocol-alignment-review.md（约 L100-119，闭环规则 +
    人工验收清单附近）应新增段落：Write 前先判断目标路径是否已存在，已存在时区分
    "同一任务同日复核轮（可覆盖）" vs "别的任务遗留（不可覆盖）"。"""
    content = _read(agate_root, *PROTOCOL_ALIGNMENT_REVIEW_PARTS)
    assert "Write 前" in content, (
        "protocol-alignment-review.md 当前无 'Write 前' 存在性检查段落（DEBT0011 待修）"
    )
    assert "目标路径" in content, (
        "protocol-alignment-review.md 当前无对'目标路径是否已存在'的逻辑说明"
    )


def test_bdd_8_write_precheck_distinguishes_same_task_vs_other_task(agate_root):
    """Write 前检查逻辑必须能区分"同一任务复核轮（可覆盖）"与"别的任务遗留（不可覆盖）"，
    而不是简单地"存在即报错"或"存在即覆盖"。"""
    content = _read(agate_root, *PROTOCOL_ALIGNMENT_REVIEW_PARTS)
    assert "同一任务" in content or "同一批次" in content, (
        "protocol-alignment-review.md 当前无'同一任务复核轮可覆盖'的判断说明"
    )
    assert "不可覆盖" in content, (
        "protocol-alignment-review.md 当前无'别的任务遗留不可覆盖'的判断说明"
    )
