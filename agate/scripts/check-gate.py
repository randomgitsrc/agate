#!/usr/bin/env python3
"""check-gate.py — 阶段 gate 总闸（TAG0010 批次 2f-1 框架 + P0-P4，2f-2 补 P5-P8）

从 check-gate.sh 迁移。CLI 契约与 sh 版等价：
  check-gate.py PHASE TASK_DIR [OLD_PHASE]
exit 0 = gate 通过; exit 1 = gate 未通过; exit 2 = 需主 Agent 自判（含动态
gate_commands 或语义判断）。

OLD_PHASE（可选第 3 参数）：上一个 phase。省略时行为与之前完全一致（无回退检测）。
提供且数字上大于 PHASE 时，判定为"回退抵达"，跳过该阶段的完成度校验直接 exit 2
（回退抵达 ≠ 阶段已完成，不该被当"未完成"硬拦截；也不应假装"已通过"）。

P0-P8 全部分支均已实现（2f-2 补齐 P5-P8），与 sh 版 check-gate.sh 逐分支等价：
  P5: gate_commands.P5 动态读取提示 + 多命令 WARNING + pre-task-baseline 机械 diff
  P6: P6-acceptance.md pass/fail 汇总 + P6-evidence/ 非空（provenance 审计由
      pre-commit-gate.sh / ci-gate-backstop.py 单独调用 check-p6-provenance，不在本
      分支内执行——与 sh 版一致，sh check-gate.sh P6 同样不调）
  P7: BLOCKER/DEVIATION-CRITICAL + DESIGN_GAP 配对 + P4/P7 转抄交叉核对
  P8: P8-release.md bump_type/debt_check + version/CHANGELOG/tag 检查

本脚本的判定逻辑与 state-machine.md 步骤 5 保持同步。
步骤 5 变更时必须同步更新本脚本。一致性检查脚本覆盖本文件。
"""

import json
import os
import re
import shutil
import subprocess
import sys

try:
    import yaml
except ImportError:
    yaml = None

try:
    from agate_common import read_vision_tri_state, run_git
except ImportError:
    read_vision_tri_state = None
    run_git = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_FIELD_GET = os.path.join(SCRIPT_DIR, "agate-md-field-get.py")
GATE_MISSING_CMDS = os.path.join(SCRIPT_DIR, "agate-gate-missing-cmds.py")
P5_COUNT = os.path.join(SCRIPT_DIR, "agate-gate-p5-count.py")

# RM-AG0001（v0.30.2）：行首正则加可选反引号前缀（`[NEED_CONFIRM] 反引号包裹标记不再漏计；
# 含 - `[..]` 反引号在 dash 之后的形态）。与 sh `grep -cE` 逐行语义一致。
_NC_RE = re.compile(r"^\s*`*-?\s*`*\[NEED_CONFIRM\]")
_SUGGEST_RE = re.compile(r"^\s*`*-?\s*`*\[SUGGEST:")
_NO_NEED_RE = re.compile(r"^\s*`*-?\s*`*\[NO_NEED_CONFIRM\]")

# P1 流 C 描述提取（sed -E s/^...// 等价）：NEED_CONFIRM 单段剥离（含后续空白）。
_NC_DESC_RE = re.compile(r"^\s*`*-?\s*`*\[NEED_CONFIRM\]\s*")
# SUGGEST 三连 s/// 等价：剥离前缀 → 剥尾部反引号+空白 → 剥尾部 ]。
_SUGGEST_DESC_RE = re.compile(r"^\s*`*-?\s*`*\[SUGGEST:\s*")
_SUGGEST_TAIL_BT_RE = re.compile(r"`\s*$")
_SUGGEST_TAIL_BRACKET_RE = re.compile(r"\]\s*$")

# P4 暂存区排除模式（与 sh grep -qvE 同一模式）：
# 阶段产出 md（P[0-8]-*.md，路径首或 / 后）+ .state.yaml。
_STAGED_EXCLUDE_RE = re.compile(r"(^|/)P[0-8]-.*\.md$|(^|/)\.state\.yaml$")


def _git(args):
    """git 子进程（优先 agate_common.run_git，缺库时本地 subprocess 兜底）。"""
    if run_git is not None:
        return run_git(args)
    try:
        proc = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        return proc.returncode, proc.stdout
    except OSError:
        return 1, ""


def _read_text(path):
    """读文件全文；文件不存在/不可读返回 ""。"""
    if not os.path.isfile(path):
        return ""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def _lines(text):
    """逐行（splitlines 剥尾 \r，对应 sh frontmatter sed 的 s/\r$// CRLF 容错）。"""
    return text.splitlines()


def _frontmatter_lines(path):
    """sed -n 's/\r$//; /^---$/,/^---$/p' 等价：返回首个 --- 块内的行（不含 --- 定界）。"""
    lines = _lines(_read_text(path))
    in_fm = False
    out = []
    for line in lines:
        if line == "---":
            if not in_fm:
                in_fm = True
            else:
                break
            continue
        if in_fm:
            out.append(line)
    return out


def _frontmatter_field(path, field):
    """sed 提取 frontmatter 字段值（grep '^field:' | sed 's/^field:\\\\s*//' | head -1 等价）。"""
    prefix = field + ":"
    for line in _frontmatter_lines(path):
        if line.startswith(prefix):
            return re.sub(r"^" + re.escape(field) + r":\s*", "", line)
    return ""


def _md_field_get(op, file_path):
    """调 agate-md-field-get.py op（env FILE），失败回退 ""（同 sh || echo ""）。"""
    env = dict(os.environ)
    env["FILE"] = file_path
    try:
        proc = subprocess.run(
            [sys.executable, MD_FIELD_GET, op],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env,
        )
    except OSError:
        return ""
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").rstrip("\n")


def _gate_missing_cmds(gate_file):
    """调 agate-gate-missing-cmds.py（env GATE_FILE），失败回退 ""。"""
    env = dict(os.environ)
    env["GATE_FILE"] = gate_file
    try:
        proc = subprocess.run(
            [sys.executable, GATE_MISSING_CMDS],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env,
        )
    except OSError:
        return ""
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").rstrip("\n")


def _gate_p5_count(gate_file):
    """调 agate-gate-p5-count.py（env GATE_FILE），返回 (main, aux)。

    失败回退 (0, 0)（同 sh `|| echo "0 0"`）。
    """
    env = dict(os.environ)
    env["GATE_FILE"] = gate_file
    try:
        proc = subprocess.run(
            [sys.executable, P5_COUNT],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env,
        )
    except OSError:
        return 0, 0
    if proc.returncode != 0:
        return 0, 0
    parts = (proc.stdout or "").split()
    main = int(parts[0]) if parts and parts[0].isdigit() else 0
    aux = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return main, aux


def _load_state_yaml(task_dir):
    """读 task_dir/.state.yaml 为 dict（TAG0020 gate_p65 用；仿 check-p6-provenance L209-221）。

    文件缺失 / 无 pyyaml / 解析失败 → {}（静默回退，等价 provenance 的
    no_reuse_claim_possible 静默空 dict 语义）。
    """
    state_path = os.path.join(task_dir, ".state.yaml")
    if not os.path.isfile(state_path) or yaml is None:
        return {}
    try:
        with open(state_path, encoding="utf-8", errors="replace") as f:
            data = yaml.safe_load(f)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _run_gate_script(script_name, task_dir):
    """调 {SCRIPT_DIR}/{script_name} TASK_DIR（TAG0020 gate_p65 用）。

    子脚本 stderr 透传（诊断可见）；脚本缺失/执行失败 → 非 0（fail-closed）。
    """
    path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.isfile(path):
        sys.stderr.write(f"GATE P6.5: 缺子脚本 {script_name}\n")
        return 1
    try:
        proc = subprocess.run(
            [sys.executable, path, task_dir],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return 1
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    return proc.returncode


def _to_int(value, default=0):
    """安全转 int；失败回退 default（对应 bash 算术错误按 0 处理的口径）。"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_int_or_none(value):
    """严格转 int；非数字返回 None（对应 bash `[ x -lt y ]` 非整数报错→false 的口径）。"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# ========== TAG0006 UI/UX 机制（P2 §2.1/§2.15.4/§2.3）：P1 vision 三态 + 形态声明、P2 UI 设计节 ==========
# 分类框架维度（示例性开放集合，§2.15.2）：布局结构/渲染正确性/交互行为/动效时序/视觉呈现。
_FRAMEWORK_DIMS = frozenset({"布局结构", "渲染正确性", "交互行为", "动效时序", "视觉呈现"})
_VISION_STATUSES = frozenset({"available", "supplementable", "GAP"})
# §2.15.1 同义映射表：中文标签 → 规范形态值（杜绝 ASCII 规范值 vs 中文标签字面永不匹配的误拦）。
_SHAPE_SYNONYMS = {
    "布局型": "layout",
    "渲染组件型": "render_component",
    "时序特效型": "temporal_effects",
}
# §2.3 渲染组件型分支的启发关键词（产品域启发词，仅用于识别可能的渲染组件形态分支，
# 不构成任何技术栈绑定——形态判定以 P1 ui_render_shape 规范值 / 维度选择为准）。
_RENDER_COMP_HEURISTICS = ("渲染组件", "视觉渲染", "画布", "图表", "模型", "特效", "地图", "数字地球")


def _canonical_shape(value):
    """P1/P2 形态声明 → 规范形态值（§2.15.1 规范化值比对语义）。

    声明含规范值 ASCII 词（layout/render_component/temporal_effects）直接取用；
    仅含中文标签（布局型/渲染组件型/时序特效型）经同义映射表归一化；
    其余开放形态值原样返回（扩展形态以 P1 字段值为比对基准，P2 声明行需复用同一值）。
    """
    if not value:
        return None
    for canonical in ("layout", "render_component", "temporal_effects"):
        if re.search(r"\b" + canonical + r"\b", value):
            return canonical
    for label, canonical in _SHAPE_SYNONYMS.items():
        if label in value:
            return canonical
    stripped = value.strip("（）()【】[]{}｛｝,， \t")
    return stripped or None


def _gate_p1_vision_capability(p1_file):
    """P1 检查：domains 含 frontend → capability_requirements 必须含视觉能力三态条目（BDD-3）。

    取 frontmatter domains + 正文 YAML capability_requirements 块（need/name 含 visual|vision）：
      - 条目缺失 → exit 1（frontend 任务必须显式声明视觉能力）
      - status 不在 {available, supplementable, GAP} → exit 1
      - 合法（含 GAP——GAP 是合法声明，触发的是 P6 降级链而非 P1 拦截）→ 通过
    兼容：domains 不含 frontend → 不触发（基线 825 fixture 均无 frontend domains）。
    """
    domains = _md_field_get("domains", p1_file)
    if "frontend" not in (domains or "").split():
        return True
    status = None
    if read_vision_tri_state is not None:
        status = read_vision_tri_state(p1_file)
    if status is None and yaml is not None:
        # 兜底（agate_common 不可用）：本地解析 capability_requirements 围栏块
        text = _read_text(p1_file)
        for m in re.finditer(r"```(?:yaml|yml)\s*\n(.*?)```", text, re.DOTALL):
            try:
                data = yaml.safe_load(m.group(1))
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            reqs = data.get("capability_requirements")
            if not isinstance(reqs, list):
                continue
            for item in reqs:
                if not isinstance(item, dict):
                    continue
                need = item.get("need") or item.get("name")
                if need and re.search(r"visual|vision", str(need), re.IGNORECASE):
                    status = item.get("status")
                    break
            if status is not None:
                break
    if status is None:
        sys.stderr.write(
            "GATE P1: frontend 任务必须声明 vision 能力条目（capability_requirements 含 visual/vision need）\n"
        )
        return False
    if str(status) not in _VISION_STATUSES:
        sys.stderr.write(
            f"GATE P1: frontend 任务 vision 能力条目 status 非法（当前: {status}，须 ∈ available/supplementable/GAP）\n"
        )
        return False
    return True


def _gate_p1_ui_shape(p1_file):
    """P1 检查：domains 含 frontend → ui_render_shape/ui_ux_dimensions 声明合法性（BDD-16，§2.15.4）。

    - 双字段缺失 → 通过（presence 语义，常规布局型默认，不红基线）
    - 声明了形态但维度空 → exit 1（适配层无法生效）
    - 维度 ∈ 分类框架（§2.15.2）→ 通过；维度为扩展名 → 须在 P1 UX 类别 BDD 标题出现证明其运用
    - ui_render_shape 缺失而 ui_ux_dimensions 存在 → 允许（维度选择本身合法）
    """
    text = _read_text(p1_file)
    domains = _md_field_get("domains", p1_file)
    if "frontend" not in (domains or "").split():
        return True
    shape = _md_field_get("ui_render_shape", p1_file).strip()
    dims_raw = _md_field_get("ui_ux_dimensions", p1_file)
    dims = [d.strip() for d in re.split(r"[,，\s]+", dims_raw) if d.strip()]
    if not shape and not dims:
        return True
    if shape and not dims:
        sys.stderr.write(
            "GATE P1: 已声明 ui_render_shape 但 ui_ux_dimensions 为空——形态声明必须选择适用维度（分类框架或扩展维度）\n"
        )
        return False
    bdd_titles = "\n".join(re.findall(r"^#{2,5}\s+BDD-[0-9]+.*$", text, re.MULTILINE))
    for dim in dims:
        if dim in _FRAMEWORK_DIMS:
            continue
        if dim and dim in bdd_titles:
            continue
        sys.stderr.write(
            f"GATE P1: 维度 '{dim}' 不在分类框架且未在 UX 类别 BDD 标题声明运用\n"
        )
        return False
    return True


def _gate_p2_ui_design_section(p2_file):
    """P2 检查：ui_affected: true → P2-design.md 必含 UI 设计节（BDD-4，§2.3）。

    校验：① `## UI 设计`（或 `### UI 设计`）节标题；② 渲染形态声明（`渲染形态:` / `适用维度:`）；
    ③ 按形态分支的目标维度 checklist 关键词（布局型=布局/交互/视觉；渲染组件/时序特效型=
    渲染正确性或动效时序锚点；"不适用"显式声明可豁免该维度关键词）；④ P1-P2 形态一致性
    交叉校验（§2.15.1 规范化值比对：P1 声明 ui_render_shape 时 P2 形态声明须一致）。
    兼容：ui_affected != true → 不触发（既有 fixture 中 full-task/high-risk/paused-task 均 false）。
    """
    ui_affected = _md_field_get("ui_affected", p2_file)
    if ui_affected != "true":
        return True
    p2_text = _read_text(p2_file)

    if not re.search(r"^#{2,3}\s+UI 设计", p2_text, re.MULTILINE):
        sys.stderr.write("GATE P2: ui_affected: true 但缺 UI 设计 节标题（## UI 设计）\n")
        return False

    # 节区块 = UI 设计 标题之后的文本（形态声明与 checklist 均在节内）
    ui_sec_match = re.search(r"^#{2,3}\s+UI 设计", p2_text, re.MULTILINE)
    ui_block = p2_text[ui_sec_match.start():]

    shape_line = ""
    dim_line = ""
    for line in _lines(ui_block):
        m = re.match(r"^\s*[-*]?\s*渲染形态\s*[:：]\s*(.+)$", line)
        if m and not shape_line:
            shape_line = m.group(1).strip()
        m = re.match(r"^\s*[-*]?\s*适用维度\s*[:：]\s*(.+)$", line)
        if m and not dim_line:
            dim_line = m.group(1).strip()

    # ② 形态声明（渲染形态 或 适用维度）至少出现一次
    if not shape_line and "适用维度" not in ui_block:
        sys.stderr.write(
            "GATE P2: UI 设计 节缺渲染形态声明（须含 渲染形态: 或 适用维度: 声明行）\n"
        )
        return False

    # ③ 按形态分支校验 checklist 维度锚点
    # 维度不适用豁免按"维度"粒度（§2.3）：显式声明"布局不适用"只豁免布局锚点，
    # 交互/视觉 仍须各出现关键词——避免"声明任一维度不适用即一刀切豁免全部三维"过宽。
    canonical = _canonical_shape(shape_line)
    is_render_form = (
        canonical is not None and canonical != "layout"
    ) or any(h in shape_line for h in _RENDER_COMP_HEURISTICS) or bool(
        re.search(r"渲染正确性|动效时序", dim_line or "")
    )
    if is_render_form:
        render_anchor = bool(re.search(r"渲染|渲染正确性|capture", ui_block))
        temporal_anchor = bool(re.search(r"时序|动效|animation|frame", ui_block))
        if not (render_anchor or temporal_anchor):
            sys.stderr.write(
                "GATE P2: 渲染组件/时序特效型形态缺维度锚点——须出现渲染正确性（渲染|渲染正确性|capture）或动效时序（时序|动效|animation|frame）checklist\n"
            )
            return False
    else:
        layout_ok = "布局" in ui_block or bool(re.search(r"布局\s*不适用", ui_block))
        interaction_ok = "交互" in ui_block or bool(re.search(r"交互\s*不适用", ui_block))
        visual_ok = "视觉" in ui_block or bool(re.search(r"视觉\s*不适用", ui_block))
        if not (layout_ok and interaction_ok and visual_ok):
            sys.stderr.write(
                "GATE P2: 常规布局型 UI 设计节缺维度 checklist——布局/交互/视觉 关键词须各出现至少一次（或显式声明维度不适用）\n"
            )
            return False

    # ④ P1-P2 形态一致性交集校验（规范化值比对，§2.15.1）
    p1_file = os.path.join(os.path.dirname(os.path.abspath(p2_file)), "P1-requirements.md")
    p1_shape = _md_field_get("ui_render_shape", p1_file).strip() if os.path.isfile(p1_file) else ""
    if p1_shape:
        p2_canonical = _canonical_shape(shape_line) if shape_line else None
        if p2_canonical is None:
            sys.stderr.write(
                "GATE P2: P1 声明了 ui_render_shape 但 P2 UI 设计节缺形态声明行（P1-P2 形态一致性校验不通过）\n"
            )
            return False
        if p1_shape != p2_canonical:
            sys.stderr.write(
                f"GATE P2: P1-P2 渲染形态声明不一致（P1 ui_render_shape={p1_shape}, P2 形态声明={p2_canonical}）\n"
            )
            return False
    return True


def gate_p0(task_dir):
    sys.stderr.write(
        "GATE P0: 立项阶段无需脚本 gate（仅 P0-brief.md）。主 Agent 确认 P0-brief 四字段齐全即可推进 P1。\n"
    )
    return 2


def gate_p1(task_dir):
    p1_review = os.path.join(task_dir, "P1-review.md")
    if not os.path.isfile(p1_review):
        sys.stderr.write("GATE P1: P1-review.md 不存在——P1 评审不可裁，所有任务都需独立 requirements-review\n")
        return 1

    status = _frontmatter_field(p1_review, "status")
    if status != "approved":
        sys.stderr.write("GATE P1: P1-review.md frontmatter status 非 approved（当前: {}）\n".format(
            status if status else "缺失"))
        return 1

    agent = _frontmatter_field(p1_review, "agent")
    if not agent:
        sys.stderr.write("GATE P1: P1-review.md status:approved 但缺 agent 字段\n")
        return 1
    if agent == "main":
        sys.stderr.write("GATE P1: P1-review.md status:approved 但 agent=main（主 Agent 不可自行批准评审）\n")
        return 1

    review_text = _read_text(p1_review)
    if not re.search(r"BDD-[0-9]", review_text):
        sys.stderr.write("GATE P1: P1-review.md 不含 BDD 编号引用（裸 approved 极可能是假完成，review 结论须引用具体 BDD 编号）\n")
        return 1

    # P1 NEED_CONFIRM 检查（v0.30.2 三值分级：[NEED_CONFIRM] 阻塞 / [SUGGEST:] 不阻塞 / [NO_NEED_CONFIRM] 负向）
    p1_file = os.path.join(task_dir, "P1-requirements.md")
    p1_text = _read_text(p1_file)
    p1_lines = _lines(p1_text)
    nc_blocking = sum(1 for line in p1_lines if _NC_RE.search(line))
    nc_suggest = sum(1 for line in p1_lines if _SUGGEST_RE.search(line))

    # v2.0 T001 流 C（BDD-21）：need_confirm_resolved 结构化匹配——
    # frontmatter 该字段存在时逐条匹配，未匹配才计入阻塞数；字段缺失（旧格式）沿用整段计数。
    nc_unresolved = nc_blocking
    if nc_blocking > 0:
        fm_lines = _frontmatter_lines(p1_file)
        resolved_present = sum(1 for line in fm_lines if line.startswith("need_confirm_resolved:"))
        if resolved_present > 0:
            resolved_fm = _md_field_get("need_confirm_resolved", p1_file)
            resolved = set(resolved_fm.split("\n"))
            nc_unresolved = 0
            for line in p1_lines:
                if not _NC_RE.search(line):
                    continue
                desc = _NC_DESC_RE.sub("", line)
                if not desc:
                    continue
                if desc not in resolved:
                    nc_unresolved += 1
    if nc_unresolved > 0:
        sys.stderr.write(f"GATE P1: {nc_unresolved} 个未解决的 NEED_CONFIRM 项（阻塞）\n")
        return 1

    # v2.0 T001 流 C：SUGGEST WARNING 去重——suggest_resolved 已采纳项不重复 WARNING
    nc_suggest_unacked = nc_suggest
    if nc_suggest > 0:
        fm_lines = _frontmatter_lines(p1_file)
        sg_resolved_present = sum(1 for line in fm_lines if line.startswith("suggest_resolved:"))
        if sg_resolved_present > 0:
            sg_resolved_fm = _md_field_get("suggest_resolved", p1_file)
            resolved = set(sg_resolved_fm.split("\n"))
            nc_suggest_unacked = 0
            for line in p1_lines:
                if not _SUGGEST_RE.search(line):
                    continue
                desc = _SUGGEST_DESC_RE.sub("", line)
                desc = _SUGGEST_TAIL_BT_RE.sub("", desc)
                desc = _SUGGEST_TAIL_BRACKET_RE.sub("", desc)
                if not desc:
                    continue
                if desc not in resolved:
                    nc_suggest_unacked += 1
    if nc_suggest_unacked > 0:
        sys.stderr.write(
            f"GATE P1 WARNING: {nc_suggest_unacked} 个 SUGGEST 项（主 Agent 可自行采纳，不阻塞）\n"
        )

    # typo 兜底 1：旧标记 [NEED_CONFIRM倾向:] 残留
    if "[NEED_CONFIRM倾向:" in p1_text:
        sys.stderr.write("GATE P1: 检测到旧标记 [NEED_CONFIRM倾向:]。v0.30.2 起已重命名为 [SUGGEST: ...]\n")
        return 1
    # typo 兜底 2：[SUGGEST 开头但不是 [SUGGEST:
    if "[SUGGEST" in p1_text and "[SUGGEST:" not in p1_text:
        sys.stderr.write("GATE P1: SUGGEST 格式不符。合法格式：[SUGGEST: 推荐 X，理由 Y]\n")
        return 1
    if "[NEED_CONFIRM]" in p1_text and nc_blocking == 0:
        sys.stderr.write("GATE P1: 不合规的 NEED_CONFIRM 标记格式（须用行首 [NEED_CONFIRM]、[SUGGEST: ...] 或 [NO_NEED_CONFIRM] 声明）\n")
        return 1
    if nc_blocking == 0 and nc_suggest == 0 and not any(_NO_NEED_RE.search(line) for line in p1_lines):
        sys.stderr.write("GATE P1 WARNING: 未检测到 NEED_CONFIRM 声明（[NEED_CONFIRM] / [SUGGEST: ...] / [NO_NEED_CONFIRM]）\n")

    # TAG0006（BDD-3/16）：frontend 任务 vision 三态声明 + 形态/维度声明合法性（P1 gate 新增检查）
    if not _gate_p1_vision_capability(p1_file):
        return 1
    if not _gate_p1_ui_shape(p1_file):
        return 1

    sys.stderr.write("GATE P1: P1-review.md approved + agent≠main + 含 BDD 锚点。BDD 编号格式为 #### BDD-NN:\n")
    return 2


# TAG0014（P2-design.md §3.1，BDD-2~7）：P2 门 dispatch_plan 字段校验。
# 契约：
#   * op 输出空（无字段 / 坏 YAML）→ 跳过，等同现状（BDD-2/7）
#   * 非空 → json.loads 解析；解析失败同样跳过（不误拦不崩溃，BDD-7）
#   * mode ∈ {single, static-batch, parallel, recon-then-split, serial}（BDD-3）
#   * parallel_limit 存在且 ≥1（BDD-4）
#   * mode ∈ {static-batch, parallel} 时校验 batches：每批含 id + complexity ∈ {low, medium, high}（BDD-5）
#   * batch 数 ≤ parallel_limit（缺省 3）（BDD-6）
# 返回 None = 校验通过（或无需校验）；返回非 None = ERROR 描述（调用方负责 return 1）。
def _gate_p2_dispatch_plan(p2_file):
    raw = _md_field_get("dispatch_plan", p2_file)
    if not raw:
        return None
    try:
        plan = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(plan, dict):
        return None

    valid_modes = frozenset({"single", "static-batch", "parallel", "recon-then-split", "serial"})
    mode = plan.get("mode")
    if not isinstance(mode, str) or mode not in valid_modes:
        return f"dispatch_plan.mode 非法（当前: {mode!r}），须 ∈ {sorted(valid_modes)}"

    parallel_limit = plan.get("parallel_limit")
    if parallel_limit is not None and (not isinstance(parallel_limit, int) or parallel_limit < 1):
        return f"dispatch_plan.parallel_limit 非法（当前: {parallel_limit!r}），须为 ≥1 的整数"

    if mode in ("static-batch", "parallel"):
        batches = plan.get("batches", [])
        if not isinstance(batches, list):
            return f"dispatch_plan.batches 须为列表（当前: {type(batches).__name__}）"
        limit = parallel_limit if parallel_limit is not None else 3
        if len(batches) > limit:
            return f"dispatch_plan 批次数（{len(batches)}）超过 parallel_limit（{limit}）"
        for batch in batches:
            if not isinstance(batch, dict) or "id" not in batch:
                return "dispatch_plan.batches 每批须含 id"
            complexity = batch.get("complexity")
            if complexity not in ("low", "medium", "high"):
                return f"dispatch_plan batch {batch.get('id')!r} 的 complexity 非法（当前: {complexity!r}），须 ∈ low/medium/high"
    return None


def gate_p2(task_dir):
    p2_file = os.path.join(task_dir, "P2-design.md")
    if not os.path.isfile(p2_file):
        sys.stderr.write("GATE P2: P2-design.md 不存在——P2 不可裁剪，方案设计是必经阶段\n")
        return 1

    p2_text = _read_text(p2_file)
    p2_lines = _lines(p2_text)

    # v0.31.0：候选方案数显式 candidate_count 字段（纯强制，不再用正则数标题）
    candidate_count = 0
    for line in p2_lines:
        if re.match(r"^candidate_count:", line):
            m = re.search(r"[0-9]+", line)
            if m:
                candidate_count = int(m.group(0))
            break

    p1_file = os.path.join(task_dir, "P1-requirements.md")
    min_candidates = 2
    if os.path.isfile(p1_file):
        p1_lines = _lines(_read_text(p1_file))
        if any(re.search(r"^(design_trivial|follows_existing_pattern):\s*\S", line) for line in p1_lines):
            min_candidates = 1
    if candidate_count < min_candidates:
        sys.stderr.write(
            f"GATE P2: P2-design.md candidate_count={candidate_count}，需至少 {min_candidates} 个候选方案（design_trivial/follows_existing_pattern 时可只写 1）。请显式声明 candidate_count 字段\n"
        )
        return 1

    p2_review = os.path.join(task_dir, "P2-review.md")
    if not os.path.isfile(p2_review):
        sys.stderr.write("GATE P2: P2-review.md 不存在（P2 评审不可裁剪，必须派发独立 subagent 产出）\n")
        return 1

    status = _frontmatter_field(p2_review, "status")
    if status != "approved":
        sys.stderr.write("GATE P2: P2-review.md frontmatter status 非 approved（当前: {}）\n".format(
            status if status else "缺失"))
        return 1

    agent = _frontmatter_field(p2_review, "agent")
    if not agent:
        sys.stderr.write("GATE P2: P2-review.md status:approved 但缺 agent 字段（向后兼容 WARNING）\n")
        return 2
    if agent == "main":
        sys.stderr.write("GATE P2: P2-review.md status:approved 但 agent=main（主 Agent 不可自行批准评审）\n")
        return 1

    field_count = sum(1 for line in p2_lines if re.match(r"^(packages|domains|ui_affected|gate_commands):", line))
    if field_count < 4:
        sys.stderr.write(f"GATE P2: P2-design.md 缺字段（需 packages/domains/ui_affected/gate_commands 四字段，实际 {field_count}）\n")
        return 1

    # 多方案探索"权衡/选择理由"nudge（v0.6）
    if re.search(r"权衡|选择理由|取舍|考量|trade-?off|理由与权衡", p2_text) or (re.search(r"选择", p2_text) and re.search(r"理由|原因|因为", p2_text)):
        pass
    else:
        sys.stderr.write("GATE P2: P2-design.md 有 ≥2 候选方案但缺'权衡'或'选择理由'描述\n")
        return 1

    # P2.61: gate_commands 命令可执行性检查（WARNING 不阻断，T075 教训）
    missing_cmds = _gate_missing_cmds(p2_file)
    for entry in missing_cmds.split("\n"):
        if not entry:
            continue
        key, sep, token = entry.partition(":")
        if not sep:
            token = ""
        if shutil.which(token) is None:
            sys.stderr.write(
                f"GATE P2 WARNING: gate_commands.{key} 命令 '{token}' 不存在于当前环境——请确认使用完整路径（如 .venv/bin/pytest）或安装依赖。T075 教训：python 不存在导致 P3 gate exit 127\n"
            )

    # TAG0014（dispatch_plan 字段契约，P2-design.md §3.1）：op 输出空（无字段/坏 YAML）→ 跳过，
    # 行为等同现状（BDD-2/7 向后兼容）；非空 → json.loads 校验 mode / parallel_limit / batches。
    _dispatch_error = _gate_p2_dispatch_plan(p2_file)
    if _dispatch_error:
        sys.stderr.write(f"GATE P2 ERROR: {_dispatch_error}\n")
        return 1

    # TAG0006（BDD-4）：ui_affected: true → UI 设计节检查（含形态声明 + 维度选择 + P1-P2 一致性）
    if not _gate_p2_ui_design_section(p2_file):
        return 1

    # TAG0007（BDD-1/3）：project_phase: bootstrap → P2-skeleton.md「## 骨架声明」存在性校验。
    # 字段缺失或为 established（含显式声明）时完全不检查——行为须与改动前逐字节一致（BDD-3 回归）。
    project_phase = _frontmatter_field(p1_file, "project_phase")
    if project_phase == "bootstrap":
        skeleton_file = os.path.join(task_dir, "P2-skeleton.md")
        if not os.path.isfile(skeleton_file) or "## 骨架声明" not in _read_text(skeleton_file):
            sys.stderr.write(
                "GATE P2: project_phase: bootstrap 但 P2-skeleton.md 不存在或缺少「## 骨架声明」标题\n"
            )
            return 1

    sys.stderr.write("GATE P2: 需从 P2-design.md gate_commands 动态读取，主 Agent 自行判定\n")
    return 2


def gate_p3(task_dir):
    p3_cases = os.path.join(task_dir, "P3-test-cases.md")
    if not os.path.isfile(p3_cases):
        sys.stderr.write("GATE P3: P3-test-cases.md 不存在——P3 产出文件缺失\n")
        return 1
    sys.stderr.write("GATE P3: P3-test-cases.md 存在。TDD 红灯由主 Agent 手动跑 check-tdd-red.py 确认 + CI backstop P3 兜底。\n")
    return 2


def gate_p4(task_dir):
    # P4 review 门禁（与 P2 对称，roadmap 补 gap）
    p4_review = os.path.join(task_dir, "P4-review.md")
    if not os.path.isfile(p4_review):
        sys.stderr.write(
            "GATE P4: P4-review.md 不存在（P4 评审不可裁剪，必须派发独立 subagent 产出，见 phase-cards/P4-implementation.md C8 机械映射）\n"
        )
        return 1

    status = _frontmatter_field(p4_review, "status")
    if status != "approved":
        sys.stderr.write("GATE P4: P4-review.md frontmatter status 非 approved（当前: {}）\n".format(
            status if status else "缺失"))
        return 1

    agent = _frontmatter_field(p4_review, "agent")
    if not agent:
        sys.stderr.write("GATE P4: P4-review.md status:approved 但缺 agent 字段（向后兼容 WARNING）\n")
        return 2
    if agent == "main":
        sys.stderr.write("GATE P4: P4-review.md status:approved 但 agent=main（主 Agent 不可自行批准评审）\n")
        return 1

    # pre-commit 阶段：检查暂存区有代码文件（非纯文档/状态文件）
    # N1 修复：查 git diff --cached 而非 git log——pre-commit 时 commit 还没创建
    rc, name_only = _git(["diff", "--cached", "--name-only"])
    if rc != 0:
        return 1
    has_code_file = False
    for raw_line in name_only.splitlines():
        line = raw_line.rstrip("\r")
        if not _STAGED_EXCLUDE_RE.search(line):
            has_code_file = True
            break
    if not has_code_file:
        return 1

    # TAG0007（BDD-4/7/10）：骨架/CODE-MAP 机制已采用（P2-skeleton.md 或
    # {AGATE_WORKSPACE}/agents/CODE-MAP.md 存在，OR 条件）且 P4-implementation.md 缺少
    # 「## 新增文件核对表」标题 → WARNING 不阻断（仍 return 0）。change_type 字段不读取、
    # 不分支（BDD-10：refactor 任务同样触发，不豁免）。
    skeleton_file = os.path.join(task_dir, "P2-skeleton.md")
    # [DESIGN_GAP: P2-design.md 未给出 {AGATE_WORKSPACE}/agents/CODE-MAP.md 的函数级路径解析
    # 细节（P3 测试只覆盖 P2-skeleton.md 分支）。本实现采用 task_dir 向上两级推导 workspace 根
    # （task_dir 通常形如 {AGATE_WORKSPACE}/tasks/{Txxx}），再拼接 agents/CODE-MAP.md：
    # os.path.dirname(os.path.dirname(os.path.abspath(task_dir))) + "/agents/CODE-MAP.md"。
    # 若与 agate_common._resolve_workspace / .agate.env 的实际工作区解析机制不一致，需后续对齐。]
    code_map_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(task_dir))), "agents", "CODE-MAP.md"
    )
    if os.path.isfile(skeleton_file) or os.path.isfile(code_map_file):
        p4_impl_check = os.path.join(task_dir, "P4-implementation.md")
        if "## 新增文件核对表" not in _read_text(p4_impl_check):
            sys.stderr.write(
                "GATE P4 WARNING: 骨架/CODE-MAP 机制已采用，但 P4-implementation.md 缺少「## 新增文件核对表」标题（不阻断，请补充）\n"
            )

    return 0


def gate_p5(task_dir):
    # P5 gate：技术验证需动态读取 gate_commands.P5，主 Agent 自行执行并判定
    sys.stderr.write("GATE P5: 需从 P2-design.md gate_commands.P5 动态读取，主 Agent 自行判定\n")
    # WARNING：P2 声明多个 gate_commands.P5 命令（单元+集成+E2E）时提醒全部执行
    # （T060 教训：只跑子集可能掩盖预存失败）
    p2_file = os.path.join(task_dir, "P2-design.md")
    if os.path.isfile(p2_file):
        p5_main, p5_aux = _gate_p5_count(p2_file)
        p5_total = p5_main + p5_aux
        if p5_total > 1:
            sys.stderr.write(
                f"GATE P5 WARNING: P2 声明了 {p5_main} 个主命令 + {p5_aux} 个辅助命令（共 {p5_total} 条 gate_commands.P5 命令），请确认已全部执行（非子集）。\n"
            )
            sys.stderr.write("  T060 教训：只跑子集可能掩盖预存失败（T056 venv 遗漏跨 4 个任务周期无人发现）。\n")

    # 机械 diff：pre-task-baseline.md vs fail-list.txt
    baseline = os.path.join(task_dir, "pre-task-baseline.md")
    post_fails = os.path.join(task_dir, "P5-test-results", "fail-list.txt")
    if os.path.isfile(baseline) and os.path.isfile(post_fails):
        baseline_text = _read_text(baseline)
        if not any(line.startswith("captured_at_commit:") for line in _lines(baseline_text)):
            sys.stderr.write("GATE P5: pre-task-baseline.md 存在但缺少 captured_at_commit: 标记，视为损坏，\n")
            sys.stderr.write("  降级为 WARNING-only（exit 2），不做机械 diff——请检查基线文件完整性\n")
            return 2

        # sed -n '/```fail-list/,/```/p' | sed '1d;$d' | grep -v '^$' 等价
        pre_list = []
        lines = _lines(baseline_text)
        start = next((i for i, line in enumerate(lines) if "```fail-list" in line), None)
        if start is not None:
            end = next((i for i in range(start + 1, len(lines)) if "```" in lines[i]), None)
            end = len(lines) if end is None else end + 1
            pre = lines[start:end]
            if len(pre) > 0:
                pre = pre[1:]
            if len(pre) > 0:
                pre = pre[:-1]
            pre_list = [line for line in pre if line]

        pre_set = sorted(set(pre_list))
        post_set = sorted({line for line in _lines(_read_text(post_fails)) if line})
        # comm -13：仅存在于第二文件（新增失败）；comm -12：两文件共有（预存失败）
        new_fails = [x for x in post_set if x not in pre_set]
        still_failing = [x for x in pre_set if x in post_set]

        if new_fails:
            sys.stderr.write("GATE P5: 检测到基线快照中不存在的新增失败，视为本任务引入的回归，拦截：\n")
            for item in new_fails:
                sys.stderr.write(f"  - {item}\n")
            return 1
        if still_failing:
            still_count = len(still_failing)
            known_failures = os.path.join(task_dir, "known-failures.md")
            if not os.path.isfile(known_failures):
                sys.stderr.write(f"GATE P5: 检测到 {still_count} 个预存失败仍未修复，\n")
                sys.stderr.write("  基线快照证实这些失败早于本任务存在，但 known-failures.md 不存在——按协议必须登记\n")
                return 1
            known_entries = sum(
                1 for line in _lines(_read_text(known_failures))
                if re.search(r"^\|\s*[0-9]+\s*\|", line)
            )
            if known_entries < still_count:
                sys.stderr.write(
                    f"GATE P5: known-failures.md 登记条目数({known_entries}) < 预存失败数({still_count})，\n"
                )
                sys.stderr.write("  登记不完整——每个预存失败都应有对应登记行\n")
                return 1
    return 2


def gate_p6(task_dir):
    # T001 v2.0 流 B（BDD-16/18，P2-design.md §3.2.1）：frontmatter pass/fail 汇总判定，
    # 无汇总（旧格式）回退正文 grep 计数（只认行首 `- PASS|FAIL ... BDD-N`，消除 F11 误判）。
    p6_file = os.path.join(task_dir, "P6-acceptance.md")

    # ── v2.0 refactor 口径分流（TAG0002 Phase A，P2-design.md §3.3）──
    change_type = ""
    p1_file = os.path.join(task_dir, "P1-requirements.md")
    if os.path.isfile(p1_file):
        change_type = _md_field_get("change_type", p1_file)
    if change_type == "refactor":
        regression_pass = _md_field_get("regression_pass", p6_file)
        if regression_pass != "true" or not os.path.isfile(os.path.join(task_dir, "P6-evidence", "regression.log")):
            sys.stderr.write(
                "GATE P6: change_type=refactor 但缺全量回归证据（须 P6-acceptance.md frontmatter regression_pass: true 且 P6-evidence/regression.log 存在）\n"
            )
            return 1

    # ↓↓ 既有判定（pass/fail 汇总 / 证据目录非空）原样保留，不随 change_type 变化 ↓↓
    pass_fm = _md_field_get("pass", p6_file)
    fail_fm = _md_field_get("fail", p6_file)
    if pass_fm != "" and fail_fm != "":
        # 新格式：frontmatter 汇总判定（BDD-16）
        total = _to_int(pass_fm) + _to_int(fail_fm)
        fail = _to_int(fail_fm)
    else:
        # 旧格式回退：正文 grep 计数（BDD-18，行首须含 BDD 编号才计入，大小写不敏感）
        p6_lines = _lines(_read_text(p6_file))
        total = sum(
            1 for line in p6_lines
            if re.search(r"^\s*- (PASS|FAIL)\b.*BDD-[0-9]", line, re.IGNORECASE)
        )
        fail = sum(
            1 for line in p6_lines
            if re.search(r"^\s*- FAIL\b.*BDD-[0-9]", line, re.IGNORECASE)
        )
    if fail != 0 or total == 0:
        sys.stderr.write(f"GATE P6: FAIL={fail}, TOTAL={total}\n")
        return 1

    # 证据存在性检查（⚠️ self-authored gate 的缓解措施）
    evidence_dir = os.path.join(task_dir, "P6-evidence")
    if not os.path.isdir(evidence_dir) or not os.listdir(evidence_dir):
        sys.stderr.write("GATE P6: P6-evidence/ 目录不存在或为空\n")
        return 1

    sys.stderr.write(
        f"GATE P6: 证据目录非空，FAIL=0，NC=0，P6_TOTAL={total}。BDD 总数对照由 check-p6-provenance.py 审计 3 自动执行。\n"
    )
    return 2


def gate_p65(task_dir):
    """P6.5 judge 强门槛子阶段（TAG0020，BDD-1/2/9；P2-design §3.5 候选 1）。

    P6.5 是挂载于 P6→P7 转移上的强门槛子阶段，非独立 phase 值（.state.yaml phase
    保持 P6 至 P7）。判定：
    - judge 未启用（.state.yaml 无 judge.enabled: true / 历史任务）→ 早退 0（BDD-2）
    - 启用但缺 P6.5-judge-verdict.md → exit 1（BDD-1 fail-closed，P6→P7 阻断）
    - 否则依次调 check-judge-verdict.py + check-events.py，任一 exit 1 → exit 1
      （BDD-9：机械核对 exit code 才是门槛，LLM verdict 不单独放行）
    """
    state_yaml = _load_state_yaml(task_dir)
    judge = state_yaml.get("judge") if isinstance(state_yaml, dict) else None
    if not (isinstance(judge, dict) and judge.get("enabled")):
        sys.stderr.write("GATE P6.5: judge 机制未启用（历史任务），跳过\n")
        return 0
    verdict = os.path.join(task_dir, "P6.5-judge-verdict.md")
    if not os.path.isfile(verdict):
        sys.stderr.write("GATE P6.5: 缺 P6.5-judge-verdict.md（judge 未产出），P6→P7 阻断\n")
        return 1
    for script in ("check-judge-verdict.py", "check-events.py"):
        if _run_gate_script(script, task_dir) != 0:
            sys.stderr.write(f"GATE P6.5: {script} 未通过\n")
            return 1
    sys.stderr.write("GATE P6.5: judge 复核 + 账本审计通过\n")
    return 0


def gate_p7(task_dir):
    # v0.6：显式 if/elif/else；T001 v2.0 流 B（BDD-19/20，P2-design.md §3.2.2）：
    # frontmatter 声明 blocker_count/deviation_critical_count/design_gap_count/
    # design_gap_reviewed_count（新格式）→ 门禁基于结构化计数判定；缺失（旧格式）回退正文 grep。
    p7_file = os.path.join(task_dir, "P7-consistency.md")

    blocker_fm = _md_field_get("blocker_count", p7_file)
    devcrit_fm = _md_field_get("deviation_critical_count", p7_file)
    if blocker_fm != "" and devcrit_fm != "":
        # 新格式：frontmatter 结构化计数判定（BDD-19）
        blockers = _to_int(blocker_fm)
        devcrit = _to_int(devcrit_fm)
    else:
        # 旧格式回退：正文 grep + 非计数行排除正则（既有逻辑）
        # M4：[:：] bracket 在 POSIX locale 不匹配全角冒号 → alternation (:|：)
        p7_lines = _lines(_read_text(p7_file))
        blocker_lines = [line for line in p7_lines if re.search(r"^\s*-?\s*\[BLOCKER\]", line)]
        devcrit_lines = [line for line in p7_lines if re.search(r"^\s*-?\s*\[DEVIATION-CRITICAL\]", line)]
        blockers = sum(
            1 for line in blocker_lines
            if not re.search(r"\[BLOCKER\](:|：)?\s*[0-9]+\s*条?\s*$", line)
        )
        devcrit = sum(
            1 for line in devcrit_lines
            if not re.search(r"\[DEVIATION-CRITICAL\](:|：)?\s*[0-9]+\s*条?\s*$", line)
        )
    if blockers > 0 or devcrit > 0:
        sys.stderr.write(f"GATE P7: BLOCKER={blockers}, DEVIATION-CRITICAL={devcrit}\n")
        return 1

    # DESIGN_GAP 配对检查（v0.6：未配对 REVIEWED 标记的 DESIGN_GAP → 不通过）
    dg_count_fm = _md_field_get("design_gap_count", p7_file)
    dg_reviewed_fm = _md_field_get("design_gap_reviewed_count", p7_file)
    if dg_count_fm != "" and dg_reviewed_fm != "":
        # 新格式：reviewed_count >= count 通过（BDD-20，F14 消除数量相减歧义）
        dg_count = _to_int_or_none(dg_count_fm)
        dg_reviewed = _to_int_or_none(dg_reviewed_fm)
        if dg_count is not None and dg_reviewed is not None and dg_reviewed < dg_count:
            sys.stderr.write(
                f"GATE P7: 有 {dg_count - dg_reviewed} 条 [DESIGN_GAP] 未配对 [DESIGN_GAP_REVIEWED]（frontmatter: design_gap_count={dg_count}, design_gap_reviewed_count={dg_reviewed}）——主 Agent 需审查 implementer 的自主决策\n"
            )
            return 1
        if dg_count is None:
            dg_count = 0
        if dg_reviewed is None:
            dg_reviewed = 0
    else:
        # 旧格式回退：正文 grep 数量相减判定（既有逻辑）
        p7_lines = _lines(_read_text(p7_file))
        dg_count = sum(1 for line in p7_lines if re.search(r"^\s*>?\s*-?\s*\[DESIGN_GAP:", line))
        dg_reviewed = sum(1 for line in p7_lines if re.search(r"^\s*>?\s*-?\s*\[DESIGN_GAP_REVIEWED", line))
        unreviewed = dg_count - dg_reviewed
        if unreviewed > 0:
            sys.stderr.write(
                f"GATE P7: 有 {unreviewed} 条 [DESIGN_GAP] 未配对 [DESIGN_GAP_REVIEWED]——主 Agent 需审查 implementer 的自主决策\n"
            )
            return 1

    # 问题4 (T090)：P4 含"设计偏差/gap"关键词但 DESIGN_GAP 计数为 0 → WARNING 提醒人工确认
    if dg_count == 0:
        p4_impl = os.path.join(task_dir, "P4-implementation.md")
        if os.path.isfile(p4_impl) and re.search(r"设计偏差|design gap|未列入|gap:", _read_text(p4_impl), re.IGNORECASE):
            sys.stderr.write(
                    "GATE P7 WARNING: P4 检测到设计偏差相关关键词但 [DESIGN_GAP:] 计数为 0——请确认是否真的无偏差，或 P4 未按标准格式声明\n"
                )

    # R2.3 修复：P4/P7 DESIGN_GAP 数量交叉核对（architect 忘记把 P4 的 DESIGN_GAP 转抄到 P7）
    p4_gap_lines = []
    p4_impl_file = os.path.join(task_dir, "P4-implementation.md")
    if os.path.isfile(p4_impl_file):
        p4_gap_lines.extend(_lines(_read_text(p4_impl_file)))
    p4_impl_dir = os.path.join(task_dir, "P4-implementation")
    if os.path.isdir(p4_impl_dir):
        for root, _dirs, names in os.walk(p4_impl_dir):
            for name in names:
                p4_gap_lines.extend(_lines(_read_text(os.path.join(root, name))))
    # grep -rh '\[DESIGN_GAP:' 过滤后 grep -cE '^\s*-?\s*\[DESIGN_GAP:' 等价
    p4_gap_lines = [line for line in p4_gap_lines if "[DESIGN_GAP:" in line]
    p4_design_gap_count = sum(
        1 for line in p4_gap_lines
        if re.search(r"^\s*-?\s*\[DESIGN_GAP:", line)
    )
    if p4_design_gap_count > dg_count:
        sys.stderr.write(
            f"GATE P7: P4 声明了 {p4_design_gap_count} 条 [DESIGN_GAP]，P7 只转抄了 {dg_count} 条——architect 遗漏转抄\n"
        )
        return 1

    # N3: review 实质锚点 WARNING——P7 有 DESIGN_GAP_REVIEWED 但缺跨文件引用
    if dg_reviewed > 0 and not re.search(r"P1.*BDD|P2.*packages|P4.*implementation", _read_text(p7_file)):
        sys.stderr.write(
                "WARNING P7: P7-consistency.md 有 DESIGN_GAP_REVIEWED 但缺跨文件引用关键词（P1 BDD / P2 packages / P4 implementation）——review 可能未做实质性交叉检查\n"
            )

    # TAG0007（BDD-8/9/10）：CODE_MAP pairing 两层硬校验，仿照上方 DESIGN_GAP pairing 模板
    # （字段对应关系：内部一致性层比较 code_map_reviewed_count 与 code_map_new_files_count；
    # 转抄核对层比较 P4 实际标记数与 code_map_new_files_count，不是 code_map_reviewed_count）。
    # 两字段均缺失 → 机制未采用，两层校验全部跳过（回归对照）。change_type 字段不读取、不分支
    # （BDD-10：refactor 任务同样生效）。与上方 DESIGN_GAP 逻辑并行独立，不共享变量。
    # [DESIGN_GAP: dispatch-context 建议用 _md_field_get 读取 code_map_new_files_count/
    # code_map_reviewed_count（与既有 design_gap_count 读取方式一致），但
    # agate-md-field-get.py 的 KNOWN_OPS 允许列表尚未注册这两个新字段名（该文件不在本批次
    # 允许改动范围内，只能改 check-gate.py）——若照字面用 _md_field_get 调用，子进程会因
    # unknown op exit(2)，_md_field_get 恒回退为空字符串，导致两层校验永远被判定为"机制未
    # 采用"而跳过，12 个新增测试中 3 个 gate_p7 用例会失败。改用本文件已有的纯本地实现
    # _frontmatter_field(path, field)（同一文件内定义，无子进程/无 allowlist 限制）直接从
    # P7-consistency.md frontmatter 块取值，行为等价（frontmatter-only，无正文回退，因为
    # _frontmatter_field 本身只扫描 --- 块内的行）。若后续有批次把这两个字段注册进
    # agate-md-field-get.py 的 NO_FALLBACK_INT_FIELDS，可切回 _md_field_get 保持风格统一。]
    cm_count_fm = _frontmatter_field(p7_file, "code_map_new_files_count")
    cm_reviewed_fm = _frontmatter_field(p7_file, "code_map_reviewed_count")
    if cm_count_fm != "" and cm_reviewed_fm != "":
        cm_count = _to_int_or_none(cm_count_fm)
        cm_reviewed = _to_int_or_none(cm_reviewed_fm)
        # 内部一致性层
        if cm_count is not None and cm_reviewed is not None and cm_reviewed < cm_count:
            sys.stderr.write(
                f"GATE P7: CODE_MAP 新增文件核对未通过——code_map_reviewed_count={cm_reviewed} < code_map_new_files_count={cm_count}\n"
            )
            return 1
        if cm_count is None:
            cm_count = 0
        # 转抄核对层：P4 正文实际 [CODE_MAP_UPDATED]/[CODE_MAP_EXEMPT] 标记数
        # > code_map_new_files_count（注意不是 code_map_reviewed_count）→ return 1
        p4_impl_file_for_cm = os.path.join(task_dir, "P4-implementation.md")
        p4_cm_lines = _lines(_read_text(p4_impl_file_for_cm))
        p4_code_map_actual_count = sum(
            1 for line in p4_cm_lines
            if re.search(r"^\s*-?\s*\[CODE_MAP_UPDATED\]", line)
            or re.search(r"^\s*-?\s*\[CODE_MAP_EXEMPT", line)
        )
        if p4_code_map_actual_count > cm_count:
            sys.stderr.write(
                f"GATE P7: P4 实际标记 {p4_code_map_actual_count} 条 [CODE_MAP_UPDATED]/[CODE_MAP_EXEMPT]，"
                f"超过 P7 声明的 code_map_new_files_count={cm_count}（转抄核对未通过）\n"
            )
            return 1

    return 0


def gate_p8(task_dir):
    # P8 部分检查可脚本化，其余需主 Agent 自判。
    # version 文件路径和 CHANGELOG 文件名因项目而异，主 Agent 从 P2-design.md packages 读取。
    # 用 git diff --cached（暂存区），不用 HEAD~1——pre-commit 时本次变更还没进 HEAD
    # （与 P4/P7 同款修复，v0.6 hardening R4 chicken-and-egg 教训）。
    p8_file = os.path.join(task_dir, "P8-release.md")
    p8_text = _read_text(p8_file)

    # 检查 bump_type 字段
    if "bump_type:" not in p8_text:
        sys.stderr.write("GATE P8: P8-release.md 缺 bump_type 字段\n")
        return 1
    # 债务清单确认留痕检查（TAG0001 Phase 3）：只查留痕存在，不查内容达标、不阻断发布
    if "debt_check:" not in p8_text:
        sys.stderr.write("GATE P8: P8-release.md 缺 debt_check 字段（须确认债务清单并留痕，可为 none）\n")
        return 1

    # 检查 version 文件变更（路径 A: 暂存区 + 路径 B: 最近 commit）
    version_pattern = os.environ.get(
        "AGATE_VERSION_FILES",
        "version|__version__|package.json|Cargo.toml|pyproject.toml|go.mod|pom.xml|gemspec|csproj",
    )
    version_re = re.compile(version_pattern, re.IGNORECASE)
    cached_version = False
    rc, stat_out = _git(["diff", "--cached", "--stat"])
    if rc == 0 and version_re.search(stat_out or ""):
        cached_version = True
    recent_version = False
    if not cached_version:
        lookback = os.environ.get("AGATE_P8_LOOKBACK", "5")
        lookback_num = _to_int(lookback, 5)
        rc, _ = _git(["rev-parse", f"HEAD~{lookback_num}"])
        if rc == 0:
            rc, stat_out = _git(["diff", f"HEAD~{lookback_num}..HEAD", "--stat"])
            if rc == 0 and version_re.search(stat_out or ""):
                recent_version = True
    if not cached_version and not recent_version:
        sys.stderr.write(f"GATE P8 WARNING: 暂存区和最近 {lookback_num} 个 commit 均无 version 文件变更\n")

    # 检查 CHANGELOG 变更（双路径，降级为 WARNING）
    changelog_file = os.environ.get("CHANGELOG_FILE", "CHANGELOG.md")
    cached_changelog = False
    rc, diff_out = _git(["diff", "--cached", "--", changelog_file])
    if rc == 0 and any(line for line in (diff_out or "").splitlines()):
        cached_changelog = True
    recent_changelog = False
    if not cached_changelog:
        lookback_num = _to_int(os.environ.get("AGATE_P8_LOOKBACK", "5"), 5)
        rc, _ = _git(["rev-parse", f"HEAD~{lookback_num}"])
        if rc == 0:
            rc, diff_out = _git(["diff", f"HEAD~{lookback_num}..HEAD", "--", changelog_file])
            if rc == 0 and any(line for line in (diff_out or "").splitlines()):
                recent_changelog = True
    if not cached_changelog and not recent_changelog:
        sys.stderr.write(
            f"GATE P8 WARNING: 暂存区和最近 {lookback_num} 个 commit 均无 {changelog_file} 变更\n"
        )

    # 检查 tag 存在性（WARNING，不阻断——tag 通常在 gate 通过后才打）
    version_tag_prefix = os.environ.get("VERSION_TAG_PREFIX", "v")
    tag_version = ""
    rc, changelog_diff = _git(["diff", "--cached", "--", changelog_file])
    if rc == 0:
        m = re.search(r"\[[0-9]+\.[0-9]+\.[0-9]+[a-zA-Z0-9.-]*\]", changelog_diff or "")
        if m:
            tag_version = m.group(0).lstrip("[").rstrip("]")
    if tag_version:
        rc, tag_out = _git(["tag", "-l", version_tag_prefix + tag_version])
        if rc == 0 and not any(line for line in (tag_out or "").splitlines()):
            sys.stderr.write(
                f"GATE P8 WARNING: tag {version_tag_prefix}{tag_version} 不存在。打 tag 后再推进到 READY。若 tag 前缀非 v，设置 VERSION_TAG_PREFIX 环境变量。\n"
            )

    sys.stderr.write(
        "GATE P8: 脚本化检查通过。仍需主 Agent：① 从 P2 gate_commands 逐包读取发布检查命令 ② 重跑 P5 gate ③ 用 git log 对照 CHANGELOG 无遗漏 ④ 从 P2 packages 验证 version 文件路径\n"
    )
    return 2


def main():
    if len(sys.argv) < 3:
        sys.stderr.write("用法: check-gate.py PHASE TASK_DIR\n")
        sys.exit(1)
    phase = sys.argv[1]
    task_dir = sys.argv[2]
    old_phase = sys.argv[3] if len(sys.argv) > 3 else ""

    # 回退抵达检测（可选第 3 参数，向后兼容：不传 = 行为与之前完全一致）。
    if old_phase:
        old_num = re.search(r"[0-9]+", old_phase)
        new_num = re.search(r"[0-9]+", phase)
        if old_num and new_num and int(old_num.group(0)) > int(new_num.group(0)):
            sys.stderr.write(
                f"GATE {phase}: 检测到回退抵达（上一阶段 {old_phase} → {phase}），本次 commit 视为回退声明，暂不做完成度校验\n"
            )
            sys.stderr.write(f"  该阶段的工作尚待重新进行；重新推进离开 {phase} 时会再次正常校验\n")
            sys.exit(2)

    handlers = {
        "P0": gate_p0,
        "P1": gate_p1,
        "P2": gate_p2,
        "P3": gate_p3,
        "P4": gate_p4,
        "P5": gate_p5,
        "P6": gate_p6,
        "P6.5": gate_p65,
        "P7": gate_p7,
        "P8": gate_p8,
    }
    func = handlers.get(phase)
    if func is None:
        sys.stderr.write(f"未知阶段: {phase}\n")
        sys.exit(2)
    sys.exit(func(task_dir))


if __name__ == "__main__":
    main()
