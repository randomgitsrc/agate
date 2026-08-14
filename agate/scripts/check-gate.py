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

import os
import re
import shutil
import subprocess
import sys

try:
    from agate_common import run_git
except ImportError:
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
            ["git"] + args,
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
        sys.stderr.write("GATE P1: {} 个未解决的 NEED_CONFIRM 项（阻塞）\n".format(nc_unresolved))
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
            "GATE P1 WARNING: {} 个 SUGGEST 项（主 Agent 可自行采纳，不阻塞）\n".format(nc_suggest_unacked)
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

    sys.stderr.write("GATE P1: P1-review.md approved + agent≠main + 含 BDD 锚点。BDD 编号格式为 #### BDD-NN:\n")
    return 2


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
            "GATE P2: P2-design.md candidate_count={}，需至少 {} 个候选方案（design_trivial/follows_existing_pattern 时可只写 1）。请显式声明 candidate_count 字段\n".format(
                candidate_count, min_candidates)
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
        sys.stderr.write("GATE P2: P2-design.md 缺字段（需 packages/domains/ui_affected/gate_commands 四字段，实际 {}）\n".format(field_count))
        return 1

    # 多方案探索"权衡/选择理由"nudge（v0.6）
    if re.search(r"权衡|选择理由|取舍|考量|trade-?off|理由与权衡", p2_text):
        pass
    elif re.search(r"选择", p2_text) and re.search(r"理由|原因|因为", p2_text):
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
                "GATE P2 WARNING: gate_commands.{} 命令 '{}' 不存在于当前环境——请确认使用完整路径（如 .venv/bin/pytest）或安装依赖。T075 教训：python 不存在导致 P3 gate exit 127\n".format(
                    key, token)
            )

    sys.stderr.write("GATE P2: 需从 P2-design.md gate_commands 动态读取，主 Agent 自行判定\n")
    return 2


def gate_p3(task_dir):
    p3_cases = os.path.join(task_dir, "P3-test-cases.md")
    if not os.path.isfile(p3_cases):
        sys.stderr.write("GATE P3: P3-test-cases.md 不存在——P3 产出文件缺失\n")
        return 1
    sys.stderr.write("GATE P3: P3-test-cases.md 存在。TDD 红灯由主 Agent 手动跑 check-tdd-red.sh 确认 + CI backstop P3 兜底。\n")
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
    for line in name_only.splitlines():
        line = line.rstrip("\r")
        if not _STAGED_EXCLUDE_RE.search(line):
            return 0
    return 1


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
                "GATE P5 WARNING: P2 声明了 {} 个主命令 + {} 个辅助命令（共 {} 条 gate_commands.P5 命令），请确认已全部执行（非子集）。\n".format(
                    p5_main, p5_aux, p5_total)
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
            if end is None:
                end = len(lines)
            else:
                end = end + 1
            pre = lines[start:end]
            if len(pre) > 0:
                pre = pre[1:]
            if len(pre) > 0:
                pre = pre[:-1]
            pre_list = [line for line in pre if line]

        pre_set = sorted(set(pre_list))
        post_set = sorted(set(line for line in _lines(_read_text(post_fails)) if line))
        # comm -13：仅存在于第二文件（新增失败）；comm -12：两文件共有（预存失败）
        new_fails = [x for x in post_set if x not in pre_set]
        still_failing = [x for x in pre_set if x in post_set]

        if new_fails:
            sys.stderr.write("GATE P5: 检测到基线快照中不存在的新增失败，视为本任务引入的回归，拦截：\n")
            for item in new_fails:
                sys.stderr.write("  - {}\n".format(item))
            return 1
        if still_failing:
            still_count = len(still_failing)
            known_failures = os.path.join(task_dir, "known-failures.md")
            if not os.path.isfile(known_failures):
                sys.stderr.write("GATE P5: 检测到 {} 个预存失败仍未修复，\n".format(still_count))
                sys.stderr.write("  基线快照证实这些失败早于本任务存在，但 known-failures.md 不存在——按协议必须登记\n")
                return 1
            known_entries = sum(
                1 for line in _lines(_read_text(known_failures))
                if re.search(r"^\|\s*[0-9]+\s*\|", line)
            )
            if known_entries < still_count:
                sys.stderr.write(
                    "GATE P5: known-failures.md 登记条目数({}) < 预存失败数({})，\n".format(known_entries, still_count)
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
        sys.stderr.write("GATE P6: FAIL={}, TOTAL={}\n".format(fail, total))
        return 1

    # 证据存在性检查（⚠️ self-authored gate 的缓解措施）
    evidence_dir = os.path.join(task_dir, "P6-evidence")
    if not os.path.isdir(evidence_dir) or not os.listdir(evidence_dir):
        sys.stderr.write("GATE P6: P6-evidence/ 目录不存在或为空\n")
        return 1

    sys.stderr.write(
        "GATE P6: 证据目录非空，FAIL=0，NC=0，P6_TOTAL={}。BDD 总数对照由 check-p6-provenance.sh 审计 3 自动执行。\n".format(total)
    )
    return 2


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
        sys.stderr.write("GATE P7: BLOCKER={}, DEVIATION-CRITICAL={}\n".format(blockers, devcrit))
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
                "GATE P7: 有 {} 条 [DESIGN_GAP] 未配对 [DESIGN_GAP_REVIEWED]（frontmatter: design_gap_count={}, design_gap_reviewed_count={}）——主 Agent 需审查 implementer 的自主决策\n".format(
                    dg_count - dg_reviewed, dg_count, dg_reviewed)
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
                "GATE P7: 有 {} 条 [DESIGN_GAP] 未配对 [DESIGN_GAP_REVIEWED]——主 Agent 需审查 implementer 的自主决策\n".format(unreviewed)
            )
            return 1

    # 问题4 (T090)：P4 含"设计偏差/gap"关键词但 DESIGN_GAP 计数为 0 → WARNING 提醒人工确认
    if dg_count == 0:
        p4_impl = os.path.join(task_dir, "P4-implementation.md")
        if os.path.isfile(p4_impl):
            if re.search(r"设计偏差|design gap|未列入|gap:", _read_text(p4_impl), re.IGNORECASE):
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
            "GATE P7: P4 声明了 {} 条 [DESIGN_GAP]，P7 只转抄了 {} 条——architect 遗漏转抄\n".format(p4_design_gap_count, dg_count)
        )
        return 1

    # N3: review 实质锚点 WARNING——P7 有 DESIGN_GAP_REVIEWED 但缺跨文件引用
    if dg_reviewed > 0:
        if not re.search(r"P1.*BDD|P2.*packages|P4.*implementation", _read_text(p7_file)):
            sys.stderr.write(
                "WARNING P7: P7-consistency.md 有 DESIGN_GAP_REVIEWED 但缺跨文件引用关键词（P1 BDD / P2 packages / P4 implementation）——review 可能未做实质性交叉检查\n"
            )
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
        rc, _ = _git(["rev-parse", "HEAD~{}".format(lookback_num)])
        if rc == 0:
            rc, stat_out = _git(["diff", "HEAD~{}..HEAD".format(lookback_num), "--stat"])
            if rc == 0 and version_re.search(stat_out or ""):
                recent_version = True
    if not cached_version and not recent_version:
        sys.stderr.write("GATE P8 WARNING: 暂存区和最近 {} 个 commit 均无 version 文件变更\n".format(lookback_num))

    # 检查 CHANGELOG 变更（双路径，降级为 WARNING）
    changelog_file = os.environ.get("CHANGELOG_FILE", "CHANGELOG.md")
    cached_changelog = False
    rc, diff_out = _git(["diff", "--cached", "--", changelog_file])
    if rc == 0 and any(line for line in (diff_out or "").splitlines()):
        cached_changelog = True
    recent_changelog = False
    if not cached_changelog:
        lookback_num = _to_int(os.environ.get("AGATE_P8_LOOKBACK", "5"), 5)
        rc, _ = _git(["rev-parse", "HEAD~{}".format(lookback_num)])
        if rc == 0:
            rc, diff_out = _git(["diff", "HEAD~{}..HEAD".format(lookback_num), "--", changelog_file])
            if rc == 0 and any(line for line in (diff_out or "").splitlines()):
                recent_changelog = True
    if not cached_changelog and not recent_changelog:
        sys.stderr.write(
            "GATE P8 WARNING: 暂存区和最近 {} 个 commit 均无 {} 变更\n".format(lookback_num, changelog_file)
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
                "GATE P8 WARNING: tag {}{} 不存在。打 tag 后再推进到 READY。若 tag 前缀非 v，设置 VERSION_TAG_PREFIX 环境变量。\n".format(
                    version_tag_prefix, tag_version)
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
                "GATE {}: 检测到回退抵达（上一阶段 {} → {}），本次 commit 视为回退声明，暂不做完成度校验\n".format(
                    phase, old_phase, phase)
            )
            sys.stderr.write("  该阶段的工作尚待重新进行；重新推进离开 {} 时会再次正常校验\n".format(phase))
            sys.exit(2)

    handlers = {
        "P0": gate_p0,
        "P1": gate_p1,
        "P2": gate_p2,
        "P3": gate_p3,
        "P4": gate_p4,
        "P5": gate_p5,
        "P6": gate_p6,
        "P7": gate_p7,
        "P8": gate_p8,
    }
    func = handlers.get(phase)
    if func is None:
        sys.stderr.write("未知阶段: {}\n".format(phase))
        sys.exit(2)
    sys.exit(func(task_dir))


if __name__ == "__main__":
    main()
