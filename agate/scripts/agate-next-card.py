#!/usr/bin/env python3
"""agate-next-card.py — 输出当前阶段卡片全文（M3 渲染化：裸模板卡片从 YAML 渲染）

从 agate-next-card.sh 迁移（TAG0010 批次 1c）。用法：
  agate-next-card.py PHASE
  PHASE 取值 P0-P8
  输出固定格式（hook 用 sha256 校验嵌入 dispatch-context 的卡片是当前版本）

exit 0：成功（输出卡片全文到 stdout）
exit 1：参数缺失或过多
exit 2：phase 不在 P0-P8 范围或阶段卡片文件不存在

M3 渲染化（TAG0021，P2-design §3.6 + BDD-12/13）：
- 正式卡片（git 管理的渲染产物，含 `## ` 节结构）→ 原样输出（字节稳定契约，
  test_nc_* 的 sha256 校验 + agate-inject-card 注入 hash 契约依赖此路径）。
- 裸模板卡片（无任何 `## ` 节，如最小假协议树中的 P3-tdd.md）→ 从 AGATE_ROOT
  解析到的 rules/phases.yaml 渲染「产出规格/派发/gate 规则/retry 上限」四节追加，
  输出与 YAML 声明一致（稳定版隔离：只读 resolve_agate_root 解析到的 YAML，
  不读取其它工作区未发布数据）。
- 平台无关（BDD-16）：无裸解释器、无 /tmp、无软链假设；文本 I/O 显式 utf-8。

迁移说明：readlink -f + dirname → os.path.realpath；tr '\\\\' '/' + 盘符小写 →
str.replace + 首字符小写；printf 头 + cat 卡片 → 二进制写出（字节稳定，供 sha256 校验）。
"""

import os
import re
import sys
from pathlib import Path

try:
    import yaml as _yaml
except ImportError:  # pyyaml 缺失时渲染降级为原样输出（既有行为不变）
    _yaml = None

try:
    from agate_common import resolve_agate_root as _agate_common_resolve
except (ImportError, SystemExit):
    _agate_common_resolve = None


def _resolve_agate_root():
    """AGATE_ROOT 解析：归口 agate_common.resolve_agate_root（env → 项目声明 → current 链
    → 脚本路径上溯）；agate_common 不可用时（独立副本场景）回退 env → 脚本真实路径上溯。"""
    if _agate_common_resolve is not None:
        return _agate_common_resolve(os.path.abspath(__file__))
    env_root = os.environ.get("AGATE_ROOT", "")
    if env_root:
        return env_root
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


_PHASE_CARDS = {
    "P0": "orchestrator",
    "P1": "requirements",
    "P2": "design",
    "P3": "tdd",
    "P4": "implementation",
    "P5": "verification",
    "P6": "acceptance",
    "P7": "consistency",
    "P8": "release",
}


def _lower_drive(p):
    """盘符小写（C:/ → c:/），替代 bash 参数替换 + tr。"""
    if re.match(r"^[A-Za-z]:", p):
        return p[0].lower() + p[1:]
    return p


def _rel_card(root, file):
    """卡片文件相对 AGATE_ROOT 的路径（TAG0004 Q1）。

    前缀剥离先试直接剥离（Linux 字节不变），失败再归一化双方（统一 \\ → /、盘符小写）
    后剥离——替代 bash ${file#$root/} 参数替换 + tr 归一化。
    """
    rel = file
    if file.startswith(root + "/"):
        rel = file[len(root) + 1:]
    else:
        root_norm = _lower_drive(root.replace("\\", "/"))
        file_norm = _lower_drive(file.replace("\\", "/"))
        rel = file_norm[len(root_norm) + 1:] if file_norm.startswith(root_norm + "/") else file_norm
    return rel


# ---- M3 渲染化：裸模板卡片从 rules/phases.yaml 渲染可判定节 ----

def _load_phases(agate_root):
    """读 AGATE_ROOT/rules/phases.yaml → {phase_id: phase_dict}；缺失/解析失败 → None。

    只读 resolve_agate_root 解析到的 YAML（稳定版隔离 BDD-13）：worktree 未发布
    rules/*.yaml 改动不影响 ~/.agate 稳定版注入（双工作区纪律，TAG0016 教训）。
    """
    if _yaml is None:
        return None
    path = os.path.join(agate_root, "rules", "phases.yaml")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = _yaml.safe_load(fh)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    phases = {}
    for ph in data.get("phases", []) or []:
        if isinstance(ph, dict) and ph.get("id"):
            phases[str(ph["id"])] = ph
    return phases


def _render_sections(phase):
    """从 phases.yaml 单阶段数据渲染机器可判定卡片节（产出/派发/gate/retry）。

    渲染范围 = P2-design §3.6「可判定规则」节；叙事节（首次进入/重试/常见错误/
    下游影响）不在渲染面。输出确定性（无时间戳/路径注入，字节稳定供 sha256 校验）。
    """
    blocks = []
    outputs = []
    for out in phase.get("outputs", []) or []:
        if isinstance(out, dict) and out.get("file"):
            outputs.append("- " + str(out["file"]))
    if outputs:
        blocks.append("## 产出规格\n\n" + "\n".join(outputs))
    exec_role = phase.get("exec_role")
    if exec_role:
        blocks.append("## 派发\n\n- **角色**：" + str(exec_role))
    gates = []
    for g in phase.get("gates", []) or []:
        if isinstance(g, dict) and g.get("check"):
            gates.append("- " + str(g["check"]))
    if gates:
        blocks.append("## gate 规则\n\n" + "\n".join(gates))
    if phase.get("retry_cap") is not None:
        blocks.append("## retry 上限\n\n- " + str(phase["retry_cap"]))
    return "\n\n".join(blocks)


def _needs_render(card_text):
    """裸模板判定：卡片无任何 `## ` 节结构 → 是未渲染的模板，需从 YAML 渲染。

    已提交的正式卡片（git 管理产物）含 `## ` 节 → 原样输出（字节稳定契约）。
    """
    return not any(line.strip().startswith("## ") for line in card_text.splitlines())


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        sys.stderr.write(
            f"GATE: agate-next-card.py 需要 1 个参数（PHASE: P0-P8），收到 {len(args)} 个\n"
        )
        sys.exit(1)

    phase = args[0]
    if phase not in _PHASE_CARDS:
        sys.stderr.write(f"GATE: phase '{phase}' 不在 P0-P8 范围内\n")
        sys.exit(2)

    agate_root = _resolve_agate_root()
    card_file = os.path.join(
        agate_root, "phase-cards", f"{phase}-{_PHASE_CARDS[phase]}.md"
    )
    if not os.path.isfile(card_file):
        sys.stderr.write(f"GATE: 阶段卡片文件不存在: {card_file}\n")
        sys.exit(2)

    # M3 渲染化：裸模板（无 `## ` 节）→ 从 AGATE_ROOT 解析的 rules/phases.yaml 渲染
    # 可判定节；正式卡片（含 `## ` 节，git 管理产物）→ 原样输出（字节稳定契约）。
    card_text = Path(card_file).read_text(encoding="utf-8")
    if _needs_render(card_text):
        phases = _load_phases(agate_root)
        if phases is not None:
            phase_data = phases.get(phase)
            if phase_data is not None:
                rendered = _render_sections(phase_data)
                if rendered:
                    card_text = card_text.rstrip("\n") + "\n\n" + rendered + "\n"

    rel = _rel_card(agate_root, card_file)
    header = f"## 当前阶段卡片：{phase}\n\n路径：{rel}\n---\n"
    sys.stdout.buffer.write(header.encode("utf-8"))
    # 文本 utf-8 编码写出（显式 encoding）；二进制来源 read_bytes 的既有路径含
    # 潜在 BOM/CRLF 差异，统一以 utf-8 文本 round-trip（与 test_nc_* 归一化口径一致）
    sys.stdout.buffer.write(card_text.encode("utf-8"))


if __name__ == "__main__":
    main()
