# tests/unit/test_windows_python_probe_docs.py — DEBT0014 / BDD-12 文档断言测试
# （TAG0017 fg4-windows-python-probe 批次）
#
# 被测：agate/platform-notes.md「Windows 原生」章节（含「已知限制（Windows 原生）」表）+
#       AGENTS.md「Gate 脚本分层」节，是否已文档化 Windows Store python3.exe 占位符现象
#       与 AGATE_PYTHON 显式覆盖机制，且未夸大成"已在 Windows 实测通过"。
#
# 诚实边界（P0-brief 约束 3 / P1 verification_env）：本测试只做文本断言（grep 式检查），
# 不代表、也无法代表"已在真实 Windows 环境验证"——这正是 BDD-12 要求文档本身也不能
# 声称的事，测试与被测文档在这一点上口径一致。
#
# 当前红灯原因：P1 同类扫描 3.6 已确认 platform-notes.md / AGENTS.md 全仓对
# WindowsApps / Microsoft Store / Store 占位符 / AppExecAlias / AGATE_PYTHON 均为
# 0 命中——这些说明尚未写入（P4 implementer 的工作），故本文件全部断言当前应真实失败。

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLATFORM_NOTES = _REPO_ROOT / "platform-notes.md"
_AGENTS_MD = _REPO_ROOT.parent / "AGENTS.md"

# BDD-12：文档条目文案不得包含的"已实测通过"类夸大断言字符串——
# 覆盖 P1/P2-design.md 反复强调的确切措辞及常见变体，任一命中即判定过度声称。
_OVERCLAIM_PHRASES = (
    "已在 Windows 实测通过",
    "已在真实 Windows 环境实测通过",
    "已在 Windows 环境实测通过",
    "Windows 实测通过",
)


def _extract_section(text, start_marker, end_marker=None):
    """从 start_marker 所在行开始截取到 end_marker（不含）或文件末尾。

    marker 需在文件中恰好出现一次，否则判为测试自身前置条件不满足（文档结构漂移）。
    """
    start_idx = text.index(start_marker)
    if end_marker is None:
        return text[start_idx:]
    end_idx = text.index(end_marker, start_idx + len(start_marker))
    return text[start_idx:end_idx]


@pytest.fixture(scope="module")
def platform_notes_text():
    assert _PLATFORM_NOTES.is_file(), f"未找到 {_PLATFORM_NOTES}"
    return _PLATFORM_NOTES.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def agents_md_text():
    assert _AGENTS_MD.is_file(), f"未找到 {_AGENTS_MD}"
    return _AGENTS_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def platform_notes_windows_section(platform_notes_text):
    """「Windows 原生（Git for Windows，不用 WSL）」整节（含「已知限制（Windows 原生）」表），
    是文件最后一个顶级章节，截到文件末尾。"""
    return _extract_section(
        platform_notes_text, "## Windows 原生（Git for Windows，不用 WSL）"
    )


@pytest.fixture(scope="module")
def agents_md_gate_layering_section(agents_md_text):
    """AGENTS.md「Gate 脚本分层」节（截到下一个 `## 依赖` 小节前）。"""
    return _extract_section(agents_md_text, "## Gate 脚本分层", "## 依赖")


def test_bdd_12_platform_notes_documents_store_placeholder(
    platform_notes_windows_section,
):
    """bdd-12（文档半，Store 占位符现象说明）：platform-notes.md「Windows 原生」章节
    须包含 Windows Store python3.exe 占位符现象的说明条目（command -v/where 能找到，
    但执行失败），而不仅是当前已有的 3 条已知限制（ln -sf 复制退化 / CRLF / pytest 需装 /
    CI 仅 ubuntu / 路径分隔符）。"""
    section = platform_notes_windows_section
    has_store_wording = "Store" in section and (
        "占位符" in section or "placeholder" in section.lower()
    )
    assert has_store_wording, (
        "platform-notes.md「Windows 原生」章节未找到 Store 占位符现象说明——"
        "当前只有 ln -sf/CRLF/pytest/CI/路径分隔符 5 条已知限制，缺 DEBT0014 新增条目"
    )
    # 现象描述应能指向"探测循环 / python3 候选"这一具体机制，不能只是笼统提"Windows 有问题"
    assert "python3" in section, (
        "platform-notes.md 的 Store 占位符说明未提及 python3（探测循环候选），"
        "无法定位到具体是哪个机制受影响"
    )


def test_bdd_12_platform_notes_documents_agate_python(platform_notes_windows_section):
    """bdd-12（文档半，AGATE_PYTHON 机制说明）：platform-notes.md「Windows 原生」章节须
    包含显式指定 Python 解释器路径的 AGATE_PYTHON 环境变量机制说明。"""
    assert "AGATE_PYTHON" in platform_notes_windows_section, (
        "platform-notes.md「Windows 原生」章节未提及 AGATE_PYTHON 环境变量——"
        "缺 BDD-11 对应的显式覆盖机制文档条目"
    )


def test_bdd_12_platform_notes_no_overclaim(platform_notes_windows_section):
    """bdd-12（诚实性负面断言）：platform-notes.md 不得声称"已在 Windows 实测通过"一类
    结论——本环境（Linux）无法真实触发 Store 占位符 exit 49，验收证据只能是静态修复 +
    模拟 stub 回归 + CI matrix 冒烟，不能包装成"已实测通过"（P0-brief 约束 3）。"""
    for phrase in _OVERCLAIM_PHRASES:
        assert phrase not in platform_notes_windows_section, (
            f"platform-notes.md「Windows 原生」章节出现不实断言文案：{phrase!r}——"
            "本环境无法真实验证 Windows Store 占位符行为，不得声称已实测通过"
        )


def test_bdd_12_agents_md_documents_agate_python_probe_enhancement(
    agents_md_gate_layering_section,
):
    """bdd-12（AGENTS.md 同步一句）：「Gate 脚本分层」节须追加一句说明探测循环支持
    AGATE_PYTHON 显式覆盖 + 候选可执行性小测试（P2-design.md §1.1 files_to_read 声明的
    AGENTS.md 改动点，约 L42）。"""
    section = agents_md_gate_layering_section
    assert "AGATE_PYTHON" in section, (
        "AGENTS.md「Gate 脚本分层」节未提及 AGATE_PYTHON——"
        "缺 DEBT0014 探测循环增强的同步说明句"
    )


def test_bdd_12_agents_md_no_overclaim(agents_md_gate_layering_section):
    """bdd-12（诚实性负面断言，AGENTS.md 侧）：同 platform-notes.md，AGENTS.md 也不得
    出现"已在 Windows 实测通过"一类夸大断言。"""
    for phrase in _OVERCLAIM_PHRASES:
        assert phrase not in agents_md_gate_layering_section, (
            f"AGENTS.md「Gate 脚本分层」节出现不实断言文案：{phrase!r}"
        )
