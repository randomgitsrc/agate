"""BDD-5 / BDD-6 / BDD-9(文档半) 文档断言型测试。

批次: fg1-doc-boundary (TAG0017-toolchain-fixes P3)

这些测试不测代码行为，测的是"协议 Markdown 文档里是否已经写清楚了某个结论"。
判据来自 P1-requirements.md:

- BDD-5: env_constraints 声明性字段 与 gate_commands 执行机制的语义边界已文档化
  （落点：phase-cards/P2-design.md「gate_commands 声明」节 + architect.md）
- BDD-6: UI 类任务的部署类执行性约束在 P4 后有显式检查提醒
  （落点：phase-cards/P4-implementation.md「自查≠gate」节）
- BDD-9（文档半，代码半由 fg3-strict-mode-code 批次负责）: `--strict` 不放
  `&&` 链路中间的协议指引 + 反例
  （落点：phase-cards/P2-design.md「gate_commands 声明」节，与 BDD-5 共享同一落点文件，
  见 P2-design.md（task 产出）§1.3 R1）

当前这些文字段落尚未写入协议文档，测试预期真实失败（红灯）。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
P2_DESIGN_CARD = REPO_ROOT / "phase-cards" / "P2-design.md"
ARCHITECT_ROLE = REPO_ROOT / "assets" / "execution-roles" / "architect.md"
P4_IMPLEMENTATION_CARD = REPO_ROOT / "phase-cards" / "P4-implementation.md"


def _read(path: Path) -> str:
    assert path.exists(), f"目标协议文档不存在: {path}"
    return path.read_text(encoding="utf-8")


def _extract_section(text: str, start_heading: str, next_heading_prefix: str = "## ") -> str:
    """按 markdown 标题切出一个小节的正文（含 start_heading 自身这一行到下一个同级标题之前）。

    start_heading 需精确匹配一行（去除首尾空白后相等）。
    """
    lines = text.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip() == start_heading.strip():
            start_idx = i
            break
    assert start_idx is not None, f"未在文档中找到标题行: {start_heading!r}"

    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        if lines[j].startswith(next_heading_prefix):
            end_idx = j
            break

    return "\n".join(lines[start_idx:end_idx])


# ---------------------------------------------------------------------------
# BDD-5: env_constraints 声明性字段 vs gate_commands 执行机制的边界已文档化
# ---------------------------------------------------------------------------


class TestBDD5EnvConstraintsBoundaryDocumented:
    """Given 读者查阅 P2-design.md「gate_commands 声明」节或 architect.md 角色文件
    When 读者查找"env_constraints 里声明的约束是否会被自动执行"这一问题
    Then 文档明确给出结论：env_constraints 是声明性字段（仅用于信息确认/注入），
         任何需要被强制执行的约束必须落到 gate_commands 或 P4/P8 明确 checklist，二者不等价
    """

    def test_bdd_5_p2_design_gate_commands_section_states_env_constraints_is_declarative(self):
        text = _read(P2_DESIGN_CARD)
        section = _extract_section(text, "## gate_commands 声明")

        assert "env_constraints" in section, (
            "P2-design.md「gate_commands 声明」节尚未提及 env_constraints，"
            "BDD-5 要求的边界说明段落缺失"
        )
        # 要求同时出现"声明性"定语 与 "gate_commands"/"执行机制"表述，
        # 单独出现关键词（例如只提了 env_constraints 但没讲清楚它不会被自动执行）不算满足。
        assert re.search(r"env_constraints[^\n]{0,80}声明性", section) or re.search(
            r"声明性[^\n]{0,80}env_constraints", section
        ), "P2-design.md 未明确指出 env_constraints 是声明性字段"
        assert re.search(r"(执行机制|强制执行|不会被自动执行|不等价)", section), (
            "P2-design.md 缺少 env_constraints 与 gate_commands 执行边界的结论性表述"
        )

    def test_bdd_5_architect_role_states_env_constraints_is_declarative(self):
        text = _read(ARCHITECT_ROLE)
        # architect.md 用缩进列表描述各 P2 输出字段，env_constraints 段落以
        # `env_constraints:` 开头的列表项为起点，下一个同级 `- \`` 字段列表项为终点。
        match = re.search(
            r"- `env_constraints:`.*?(?=\n  - `\w|\Z)",
            text,
            flags=re.DOTALL,
        )
        assert match is not None, "architect.md 中未找到 env_constraints 字段说明段落"
        section = match.group(0)

        assert re.search(r"声明性", section), (
            "architect.md 的 env_constraints 段落尚未同步 BDD-5 边界说明"
            "（缺少'声明性'字样）"
        )
        assert re.search(r"(gate_commands|执行机制|强制执行|不会被自动执行)", section), (
            "architect.md 的 env_constraints 段落尚未同步 env_constraints 与"
            " gate_commands 执行边界的对照说明"
        )


# ---------------------------------------------------------------------------
# BDD-9（文档半）: --strict 不放 && 链路中间的协议指引 + 反例
# ---------------------------------------------------------------------------


class TestBDD9StrictAntiPatternDocumented:
    """Given 主 Agent / architect 在 P2 声明 gate_commands
    When 声明包含 check-protocol-consistency.py --strict 这类命令
    Then phase-cards/P2-design.md「gate_commands 声明」节能查到"不要把 --strict
         放进 && 链路中间"的指引，并附带反例（历史 TAG0004 等任务已踩过的写法）
    """

    def test_bdd_9_p2_design_gate_commands_section_has_strict_anti_pattern_guidance(self):
        text = _read(P2_DESIGN_CARD)
        section = _extract_section(text, "## gate_commands 声明")

        assert "--strict" in section, (
            "P2-design.md「gate_commands 声明」节尚未提及 --strict，"
            "BDD-9 文档半要求的反模式指引缺失"
        )
        assert "&&" in section, (
            "P2-design.md「gate_commands 声明」节尚未提到 && 链路场景，"
            "无法验证是否已加入反模式指引"
        )
        # 要求明确的"不要这样做"式指引措辞，而不只是顺带提了 --strict 的正常用法
        assert re.search(r"(不要|避免|反模式|不放|不要放|短路)", section), (
            "P2-design.md 未包含 --strict 不放入 && 链路中间的显式指引措辞"
        )

    def test_bdd_9_p2_design_gate_commands_section_has_concrete_anti_pattern_example(self):
        text = _read(P2_DESIGN_CARD)
        section = _extract_section(text, "## gate_commands 声明")

        # 反例应给出可辨认的 && 链路拼接样式（例如 pytest && ... --strict && ...），
        # 不能只是一句抽象提醒而没有具体示例串。
        assert re.search(r"--strict[^\n`]*&&|&&[^\n`]*--strict", section), (
            "P2-design.md 未给出 --strict 出现在 && 链路中间的具体反例命令串"
        )


# ---------------------------------------------------------------------------
# BDD-6: UI 类任务的部署类执行性约束在 P4 后有显式检查提醒
# ---------------------------------------------------------------------------


class TestBDD6P4DeployReminderDocumented:
    """Given 某任务 P2-design.md 的 env_constraints 声明了 deploy 类约束（如构建 dist / 打包产物）
    When implementer 完成 P4 实现后对照 phase-cards/P4-implementation.md「自查≠gate」节自查
    Then 该节包含"UI/需构建任务 P4 后应构建并确认 dist 类产物存在"的显式提醒条目
    """

    def test_bdd_6_p4_implementation_self_check_section_has_dist_build_reminder(self):
        text = _read(P4_IMPLEMENTATION_CARD)
        section = _extract_section(text, "## 自查≠gate", next_heading_prefix="## ")

        assert re.search(r"(UI|前端|需构建)", section), (
            "P4-implementation.md「自查≠gate」节尚未提及 UI/需构建任务这一适用条件"
        )
        assert re.search(r"(dist|构建产物|打包产物|构建后.{0,10}产物)", section), (
            "P4-implementation.md「自查≠gate」节尚未提及需要确认 dist 类构建产物存在"
        )
        assert re.search(r"(确认.{0,10}存在|存在.{0,10}确认|已构建|应构建)", section), (
            "P4-implementation.md「自查≠gate」节缺少具体的'应构建并确认产物存在'式提醒条目"
        )


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
