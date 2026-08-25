# agate/tests/unit/test_check_structure_consistency.py — BDD-2/3/5(M0) S-1~S-6 双向一致性
#
# 被测：agate/scripts/check-structure-consistency.py（P4 M0 交付，P3 尚不存在 → 真红灯 B 类）。
# 契约（P2-design §3.3）：
#   S-1 YAML→md   phases.yaml 每个 phase（id/name/exec_role）在 WORKFLOW 阶段总览表有对应行且一致
#   S-2 md→YAML   WORKFLOW 表每行 phase id 在 phases.yaml 有定义（只匹配 P 数字前缀行，
#                 READY/表外行显式排除——P2-review 发现 #1 固化）
#   S-3 YAML→cards 抽检 phase-cards/P2-design.md 门槛/产出/派发节 vs phases.yaml P2 声明
#   S-4 YAML→scripts 脚本字段读取登记表（dispatch.yaml field_readers）与 phases.yaml 字段集一致；
#                 gate_commands 语法声明（meta_suffixes/special_keys）与 is_gate_meta_key 判据一致
#   S-5 schema    串联 check-yaml-schema.py（独立进程），rules/*.yaml 违反 schema → 报 S-5
#   S-6 引用完整性 YAML 中 file:/template:/script: 引用路径在协议根下真实存在
# 任一 ERROR → exit 1；全部 OK → exit 0。夹具入口 = AGATE_ROOT 指向最小假协议树。
#
# 平台无关（BDD-16）：无临时目录字面量、无软链、无裸解释器字面量；文本 I/O 显式 utf-8。

import shutil

import pytest
import yaml
from _rules_test_utils import (
    DEFAULT_DISPATCH_YAML,
    DEFAULT_P2_CARD,
    DEFAULT_PHASES_YAML,
    make_fake_root,
)


def _run_structure(agate_scripts, python_exe, run_cli, proto_root):
    script = agate_scripts / "check-structure-consistency.py"
    assert script.is_file(), "check-structure-consistency.py 未实现（P4 M0 交付）——TDD 红灯锚点"
    return run_cli(python_exe, str(script), env={"AGATE_ROOT": str(proto_root)})


@pytest.mark.windows_smoke
def test_bdd_2_s1_s2_consistent_exit_0(agate_scripts, python_exe, run_cli, tmp_path):
    """两侧一致（YAML 含 READY 行之外全部阶段；表含 READY 行被 S-2 排除）→ 退出码 0。
    同时固定 P2-review 发现 #1：S-2 必须忽略 READY 行。"""
    root = make_fake_root(tmp_path)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 0, result.output


def test_bdd_2_s1_yaml_extra_phase_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-1 漂移：phases.yaml 增一个表外阶段（P9）→ 退出码非 0。"""
    yaml_with_p9 = DEFAULT_PHASES_YAML + (
        "  - id: P9\n"
        "    name: 幽灵阶段\n"
        "    exec_role: verifier\n"
        "    retry_cap: 2\n"
    )
    root = make_fake_root(tmp_path, phases_text=yaml_with_p9)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_2_s2_md_extra_phase_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-2 漂移：WORKFLOW 表新增 P4 行（YAML 未定义；READY 行仍应排除）→ 退出码非 0。"""
    table_with_p4 = (
        "| 阶段 | 名称 | 执行角色 | 评审角色 | 门槛 |\n"
        "|------|------|----------|----------|------|\n"
        "| P1 | 需求基线 | analyst | requirements-review | P1-requirements.md 存在 |\n"
        "| P2 | 方案设计层 | architect | plan-eng-review | P2-review.md approved |\n"
        "| P3 | 测试设计 | test-designer | --- | check-tdd-red exit 0 |\n"
        "| P4 | 代码实现 | implementer | review | 暂存区含非 md 文件 |\n"
        "| READY | 待发布 | --- | --- | 人手动发布 |\n"
    )
    root = make_fake_root(tmp_path, workflow_text=table_with_p4)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_2_s1_name_mismatch_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-1 漂移：phases.yaml 的 P2 name 与总览表不一致 → 退出码非 0。"""
    yaml_renamed = DEFAULT_PHASES_YAML.replace("  - id: P2\n    name: 方案设计层", "  - id: P2\n    name: 方案设计改名")
    root = make_fake_root(tmp_path, phases_text=yaml_renamed)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_3_s6_missing_reference_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-6 引用完整性：roles.yaml 引用不存在的角色文件 → 退出码非 0。"""
    bad_roles = (
        "schema_version: 1\n"
        "execution_roles:\n"
        "  - {id: ghost-role, file: assets/execution-roles/ghost-role.md}\n"
    )
    root = make_fake_root(tmp_path, roles_text=bad_roles)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_3_s5_schema_enum_violation_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-5：structure 串联 schema 校验——phases.yaml 违反 exec_role 枚举 → 退出码非 0。"""
    bad_enum_phases = (
        "schema_version: 1\n"
        "phases:\n"
        "  - id: P2\n"
        "    name: 方案设计层\n"
        "    exec_role: not-a-role\n"
        "    retry_cap: 3\n"
    )
    root = make_fake_root(tmp_path, phases_text=bad_enum_phases)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_s3_card_output_mismatch_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-3 抽检：phase-cards/P2-design.md 产出规格节缺失 phases.yaml 声明的 P2-review.md →
    退出码非 0（BDD-5「任一处不一致 → 非 0」）。"""
    tampered_card = (
        "# P2 方案设计层\n\n"
        "## 前置条件\n"
        "- P1-requirements.md 完成\n\n"
        "## 产出规格\n"
        "- P2-design.md\n"  # P2-review.md 缺失
    )
    root = make_fake_root(tmp_path, card_text=tampered_card)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_s4_field_readers_unknown_field_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-4：dispatch.yaml field_readers 登记了 phases.yaml 未声明的字段 → 退出码非 0。"""
    bad_dispatch = DEFAULT_DISPATCH_YAML.replace(
        "fields: [candidate_count, packages, domains, ui_affected, gate_commands]",
        "fields: [nonexistent_field]",
    )
    root = make_fake_root(tmp_path, dispatch_text=bad_dispatch)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_s4_gate_commands_syntax_mismatch_exit_1(agate_scripts, python_exe, run_cli, tmp_path):
    """S-4 + P2-review 发现 #3 固化：gate_commands 合法 key = is_gate_meta_key
    （_formatter/_timeout_seconds 后缀）OR project_module 特判；语法声明缺少 project_module
    特判 → 与 agate_common.is_gate_meta_key 判据不一致 → 退出码非 0。"""
    bad_dispatch = DEFAULT_DISPATCH_YAML.replace(
        "  special_keys: [project_module]",
        "  special_keys: []",
    )
    root = make_fake_root(tmp_path, dispatch_text=bad_dispatch)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_initial_consistency_exit_0(agate_scripts, python_exe, run_cli, tmp_path):
    """BDD-5 正面路径：S-3/S-4 初始一致（默认假协议树 P2 三方一致）→ 退出码 0 且报 S-3/S-4 OK。"""
    root = make_fake_root(tmp_path)
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 0, result.output
    assert "S3" in result.output, "未输出 S-3 检查项（卡片↔YAML 一致判定缺失）"
    assert "S4" in result.output, "未输出 S-4 检查项（脚本字段登记一致判定缺失）"


# ─────────────────────────────────────────────
# TAG0022 增补：S-3 双向 gate 命令一致性（RM-AG0038 / BDD-5，P2 §4.2.2 S-3a/S-3b；TG-1）
#   S-3a（YAML→md）：phases.yaml gates[].check 中的命令串须在对应卡片 ## gate 规则
#                    （或推进条件）节出现；缺失 → ERROR（单侧漂移：YAML 侧加了，md 侧没加）。
#   S-3b（md→YAML）：卡片 ## gate 规则 节中机器可判定命令行（check-gate.py P\d+ /
#                    gate_commands.P\d+ / check-[\w-]+\.py）须在 gates[].check 有声明；
#                    未声明 → ERROR（单侧漂移：md 侧加了，YAML 侧没加）。
#   P3 现状 S-3a/S-3b 未实现 → 单侧漂移不报 → exit 0 → 断言非 0 失败 = 真红灯（B 类，行为未实现）；
#   双侧一致 → 现 exit 0（回归守卫，P4 实现后仍 exit 0）。
#   NB-1：S-3a/S-3b 是叠加在既有 S-3 outputs/orphan/exec_role 下的新增子检查——本组用例
#   不触碰产出规格/派发节，既有 S-3 用例保持绿。
#   S-3a 口径：卡片 ## gate 规则 节内须同时出现 P2 的全部 gates[].check 串（含散文描述），
#   故双侧一致用例把两条 gate 串都放进节内，对「命令串专属」或「全部串」两种实现语义均稳健。


def _phases_with_p2_gate_cmd():
    """DEFAULT_PHASES_YAML + P2 gates 增补机器可判定 gate 命令串（S-3a/S-3b 对账对象）。"""
    return DEFAULT_PHASES_YAML.replace(
        "      - {check: P2-review.md status == approved}\n",
        "      - {check: P2-review.md status == approved}\n"
        "      - {check: check-gate.py P2 $TASK_DIR}\n",
    )


def _card_with_gate_rules(extra_lines):
    """DEFAULT_P2_CARD + `## gate 规则` 节（节内行可含机器可判定命令行）。"""
    return DEFAULT_P2_CARD + "## gate 规则\n" + extra_lines


def test_bdd_5_s3a_yaml_gate_cmd_not_in_card_exit_1(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-5 S-3a：YAML gates 增补命令串但卡片 ## gate 规则 未出现 → 非 0（YAML 侧漂移）。
    TDD：P3 现状 S-3a 未实现 → exit 0 → 红灯（B 类）。"""
    root = make_fake_root(
        tmp_path,
        phases_text=_phases_with_p2_gate_cmd(),
        card_text=_card_with_gate_rules("- P3-test-cases.md 声明 test_code_dir\n"),
    )
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_s3b_card_gate_cmd_not_in_yaml_exit_1(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-5 S-3b：卡片 ## gate 规则 含机器可判定命令行但 YAML gates 未声明 → 非 0（md 侧漂移）。
    TDD：P3 现状 S-3b 未实现 → exit 0 → 红灯（B 类）。"""
    root = make_fake_root(
        tmp_path,
        card_text=_card_with_gate_rules("- check-gate.py P2 $TASK_DIR\n"),
    )
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode != 0, result.output


def test_bdd_5_s3a_s3b_both_sides_consistent_exit_0(
    agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-5 双侧一致：YAML gates 声明命令串 + 卡片 ## gate 规则 含对应命令行 → exit 0
    （S-3a/S-3b 同时通过）。回归守卫：P3 现状即 exit 0（无 S-3a/b）；P4 实现后双侧一致仍 exit 0。"""
    root = make_fake_root(
        tmp_path,
        phases_text=_phases_with_p2_gate_cmd(),
        card_text=_card_with_gate_rules(
            "- check-gate.py P2 $TASK_DIR\n- P2-review.md status == approved\n"
        ),
    )
    result = _run_structure(agate_scripts, python_exe, run_cli, root)
    assert result.returncode == 0, result.output


# ─────────────────────────────────────────────
# TAG0024 增补：RM-AG0049（phases.yaml P4 outputs 补全）+ RM-AG0050（P6.5 定位口径统一）
#   BDD-25~28（P1-requirements.md §4「RM-AG0049/50」节；P2-design.md §1.1 改动落点表第 35/36
#   行 + §3.8/§3.9 详细设计）。
#   本组用例的目标 = 真实仓库 agate/rules/phases.yaml + agate/state-machine.md 的当前内容/
#   补丁后内容，而非既有用例使用的 make_fake_root 最小假协议树——因为 BDD-25~28 断言的是
#   "真实文件当前是否已补全/补丁后是否引入新不一致"，不是脚本抽象行为，故改用 conftest.py
#   会话级 `agate_root` fixture（解析到本仓库 agate/ 目录）直接驱动，与既有假协议树用例共存
#   于同一文件、互不影响。
#   BDD-29（跨 issue 约束：check-gate.py/check-events.py 判定逻辑不变）不在本文件覆盖——
#   dispatch-context 已判定其性质更适合 P7 一致性检查阶段的 diff 逐行核对，非自动化单测覆盖，
#   见 P3-test-cases-phases-yaml-consistency.md 显式记录。

_P4_OUTPUTS_PATCH_ANCHOR = "      - {file: P4-implementation.md, required: true}\n"
_P4_OUTPUTS_PATCH_LINE = "      - {file: P4-review.md, required: true, status_field: status}\n"

_P65_COMMENT_PATCH_ANCHOR = "  - id: P6.5\n"
_P65_COMMENT_PATCH_BLOCK = (
    "  # 注：P6.5 是挂载于 P6→P7 转移的强门槛子阶段，不是与 P0-P8 平级的独立 phase 值\n"
    "  # （.state.yaml 的 phase 字段保持 P6 直至 P7）；本条目结构化声明其产出/门槛/重试上限，\n"
    "  # 供 check-gate.py P6.5 分发与 CLI 调用，口径详见 state-machine.md「状态机定义」节。\n"
    "  - id: P6.5\n"
)


def _real_phases_yaml_path(agate_root):
    return agate_root / "rules" / "phases.yaml"


def _apply_rm_ag0049_50_fixes(text):
    """套用 P2-design §3.8（P4 outputs 补全）/ §3.9（P6.5 措辞统一）声明的两处修复，
    返回补丁后的 phases.yaml 文本。只在测试临时副本上使用，不落盘到真实仓库文件。"""
    assert _P4_OUTPUTS_PATCH_ANCHOR in text, (
        "P4 outputs 锚点行缺失——真实 phases.yaml 结构已变化，需要先更新本测试的锚点常量"
    )
    assert _P65_COMMENT_PATCH_ANCHOR in text, (
        "P6.5 id 锚点行缺失——真实 phases.yaml 结构已变化，需要先更新本测试的锚点常量"
    )
    patched = text.replace(
        _P4_OUTPUTS_PATCH_ANCHOR,
        _P4_OUTPUTS_PATCH_ANCHOR + _P4_OUTPUTS_PATCH_LINE,
        1,
    )
    patched = patched.replace(_P65_COMMENT_PATCH_ANCHOR, _P65_COMMENT_PATCH_BLOCK, 1)
    return patched


def _copy_real_root_with_fixes(agate_root, dest):
    """拷贝真实协议根（rules/WORKFLOW.md/phase-cards/scripts/assets）到 dest，
    并把拷贝里的 phases.yaml 替换为打过 RM-AG0049/50 补丁的版本——其余文件保持真实内容，
    使 S-1~S-6 全量检查在"未来 P4 落地后的真实状态"下跑，而不是假协议树的抽象最小集。"""
    for rel in ("rules", "WORKFLOW.md", "phase-cards", "scripts", "assets"):
        src = agate_root / rel
        dst = dest / rel
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    real_text = _real_phases_yaml_path(agate_root).read_text(encoding="utf-8")
    patched_text = _apply_rm_ag0049_50_fixes(real_text)
    (dest / "rules" / "phases.yaml").write_text(patched_text, encoding="utf-8")
    return dest


def test_bdd_25_p4_outputs_includes_review_md(agate_root):
    """BDD-25：真实 phases.yaml 的 id:P4 outputs 须含
    {file: P4-review.md, required: true, status_field: status}。
    红灯：当前真实文件 P4 outputs 只声明了 P4-implementation.md 一条，本断言必须失败（B 类真红灯，
    非测试代码 bug——P4 落地 RM-AG0049 修复后该断言才会转绿）。"""
    phases = yaml.safe_load(_real_phases_yaml_path(agate_root).read_text(encoding="utf-8"))
    p4 = next(p for p in phases["phases"] if p["id"] == "P4")
    assert {"file": "P4-review.md", "required": True, "status_field": "status"} in p4["outputs"], (
        f"P4 outputs 未声明 P4-review.md（RM-AG0049 未落地）：{p4['outputs']!r}"
    )


def test_bdd_26_full_consistency_zero_mismatch_after_p4_outputs_fix(
    agate_root, agate_scripts, python_exe, run_cli, tmp_path
):
    """BDD-26：把 RM-AG0049/50 两处修复打到真实协议树副本上，跑真实
    check-structure-consistency.py 全量 S-1~S-6，断言 exit 0——证明补全 P4 outputs 声明不会
    因 S-1/S-2/S-3 产生新的不一致。回归守卫用例（非红灯）：P2-design §1.3 风险 5 /
    §3.8 已实测确认 "P4-review.md" 字面已出现在 phase-cards/P4-implementation.md 中 10 次，
    S-3 逐字段对账天然通过；本用例用真实文件内容再跑一遍脚本二进制做证据留痕，
    而不是只信静态 grep 论证。"""
    patched_root = _copy_real_root_with_fixes(agate_root, tmp_path / "patched-root-bdd26")
    script = patched_root / "scripts" / "check-structure-consistency.py"
    result = run_cli(python_exe, str(script), env={"AGATE_ROOT": str(patched_root)})
    assert result.returncode == 0, result.output


def test_bdd_27_phases_yaml_p65_comment_matches_state_machine_wording(agate_root):
    """BDD-27：phases.yaml 的 `- id: P6.5` 条目前须有注释块，同时表达"挂载于 P6→P7 转移的
    强门槛子阶段"与"非独立 / 不是……独立 phase 值"两层口径，与 state-machine.md 第 74-78/152-155
    行已有表述对齐，不再是"YAML 结构平铺展示、md 单方面强调非独立"的隐性矛盾。
    红灯：当前真实 phases.yaml 的 `- id: P6.5` 前没有任何注释行，comment_block 为空，
    断言必须失败（B 类真红灯）。"""
    phases_text = _real_phases_yaml_path(agate_root).read_text(encoding="utf-8")
    lines = phases_text.splitlines()
    try:
        p65_idx = next(i for i, line in enumerate(lines) if line.strip() == "- id: P6.5")
    except StopIteration:
        pytest.fail("phases.yaml 未找到 '- id: P6.5' 条目（真实文件结构变化，需要更新测试锚点）")
    preceding = lines[max(0, p65_idx - 6) : p65_idx]
    comment_block = "\n".join(line for line in preceding if line.strip().startswith("#"))

    assert "强门槛子阶段" in comment_block, (
        f"phases.yaml P6.5 条目前缺'强门槛子阶段'表述（RM-AG0050 未落地）：{comment_block!r}"
    )
    assert ("非独立" in comment_block) or ("不是" in comment_block and "独立" in comment_block), (
        f"phases.yaml P6.5 条目前缺'非独立/不是……独立 phase 值'表述（RM-AG0050 未落地）：{comment_block!r}"
    )
    assert "phase" in comment_block.lower(), (
        f"phases.yaml P6.5 条目前缺'phase 值'表述（RM-AG0050 未落地）：{comment_block!r}"
    )

    # 控制组：state-machine.md 侧口径基线本就存在（不应漂移），先确认对照锚点仍在，
    # 否则说明 state-machine.md 被改动过，本测试的"对齐"判定基准需要同步更新。
    state_machine_text = (agate_root / "state-machine.md").read_text(encoding="utf-8")
    assert "强门槛子阶段" in state_machine_text and "非独立 phase 值" in state_machine_text, (
        "state-machine.md 侧 P6.5 口径基线缺失或已漂移，需要先确认对照锚点（第 74-78/152-155 行）"
    )


def test_bdd_28_p65_wording_fix_preserves_parsed_structure_and_gate_behavior(
    agate_root, agate_scripts, python_exe, run_cli, tmp_path, task_dir
):
    """BDD-28：RM-AG0050 修复只是给 phases.yaml P6.5 条目前加纯注释，不改任何可解析字段——
    ① yaml.safe_load 解析出的 P6.5 条目在补丁前后逐字段相等（注释对 YAML 解析器不可见，
       任何消费 phases.yaml 解析结果的脚本都看不到差异，这是"既有判定行为不变"的结构性证明）；
    ② check-gate.py P6.5（判定逻辑见 check-gate.py 第 1032-1055 行 gate_p65：只读
       task_dir/.state.yaml 的 judge.enabled，未启用即历史任务早退路径，完全不读取
       phases.yaml/AGATE_ROOT 内容）在 AGATE_ROOT 分别指向真实仓库与补丁后协议树时，
       exit code 与 stderr 逐字节一致——用真实二进制调用而非只信代码走查做行为不变的证据留痕。
    回归守卫用例（非红灯）：dispatch-context 已声明 BDD-28 性质为"既有判定行为不变"验证，
    comment-only 改动理论上不可能影响任何消费点，此处用真实调用坐实这一点。"""
    real_text = _real_phases_yaml_path(agate_root).read_text(encoding="utf-8")
    patched_text = _apply_rm_ag0049_50_fixes(real_text)

    real_p65 = next(p for p in yaml.safe_load(real_text)["phases"] if p["id"] == "P6.5")
    patched_p65 = next(p for p in yaml.safe_load(patched_text)["phases"] if p["id"] == "P6.5")
    assert real_p65 == patched_p65, (
        "RM-AG0050 注释补丁不应改变 P6.5 的 yaml.safe_load 解析结构（comment-only 变更）："
        f"{real_p65!r} != {patched_p65!r}"
    )

    patched_root = _copy_real_root_with_fixes(agate_root, tmp_path / "patched-root-bdd28")
    task = task_dir()  # 默认无 judge 字段 → .state.yaml 无 judge.enabled，走历史任务早退路径

    gate_script = agate_scripts / "check-gate.py"
    result_real = run_cli(
        python_exe, str(gate_script), "P6.5", str(task), env={"AGATE_ROOT": str(agate_root)}
    )
    result_patched = run_cli(
        python_exe, str(gate_script), "P6.5", str(task), env={"AGATE_ROOT": str(patched_root)}
    )
    assert result_real.returncode == 0, result_real.output
    assert result_patched.returncode == 0, result_patched.output
    assert result_real.stderr == result_patched.stderr, (
        "GATE P6.5 判定输出因 phases.yaml 措辞修改而变化（应保持逐字节一致，既有判定行为不变）："
        f"{result_real.stderr!r} != {result_patched.stderr!r}"
    )
