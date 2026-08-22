#!/usr/bin/env python3
"""agate-risk-score.py — 风险分路由客观算分（TAG0019 D1，BDD-1..5）

把任务仪式深度的判定从"agent 自报复杂度"改为"git diff --cached 客观信号算分"：

    五信号（每信号 级别 high/medium/low + 证据行）：
      file-type      暂存区路径命中 agate/**/*.md 或 agate/scripts/*.py → high；
                     纯 agate/tests/** / 配置类 → low；其余 → medium
      sensitive-path 路径命中安全关键词（security|auth|permission|data-model|...）→ high
                     并输出 security 域标注；无命中 → low
      change-size    _staged_source_count(task_dir)（复用 check-pruning 同口径）> 5 → high；≤ 5 → low
      impact         反向引用扫描（NB-3 判据）：改动文件 F 的模块标识（basename 去扩展名）
                     在 repo_root（排除 task_dir / agate/tests/ 树）被 ≥1 行、且非 F 自身引用 → high
      domain-markers 域映射（纯标注，不参与 tier）：P1 frontmatter domains 声明 + 敏感路径命中

    tier 合成（二值可判）：任一 high → full；全 low → thin（候选，须过 check-routing 四要素）；
                          其余 → standard。
    risk_score 数值（展示锚点）：加权和 high=3/medium=2/low=1 × 权重（文件类型 2、敏感路径 2、
                          改动规模 1、影响面 1），范围 4-12（实际 6-12）。tier 由 max 分级规则决定，
                          不依赖数值阈值。

平台无关（BDD-13）：git 全经 agate_common.run_git；路径 os.path.relpath(...).replace("\\\\","/")；
行数逐行 .rstrip("\\r")；无硬编码 PATH / 裸解释器 / 字面 /tmp。

异常语义（P2-design §2.3 NB-2②）：run_git 失败或 agate_common 不可导入时 → 输出 git_ok: false
（不静默降级）；由 check-routing 按 fail-closed 消费（thin 声明 + git_ok:false → exit 1）。

模块形态：score_task(task_dir) -> dict 可 import（供 check-routing 复用），CLI 为薄壳。
"""

import importlib.util
import os
import re
import sys

try:
    from agate_common import run_git
except ImportError:
    run_git = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


def _load_script(name, module_name=None):
    """importlib 加载同目录脚本（带连字符模块名无法直接 import）。"""
    path = os.path.join(SCRIPT_DIR, name + ".py")
    spec = importlib.util.spec_from_file_location(
        module_name or name.replace("-", "_"), path
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# 同源复用（R1/BDD-10）：_staged_source_count 无第二份实现
_check_pruning = _load_script("check-pruning")
_staged_source_count = _check_pruning._staged_source_count

# 敏感路径关键词（P1 BDD-3 例子集扩充；P4-review F2/F3/I3 逐轮收敛）。
# 匹配形态：左锚 (?<![A-Za-z0-9_]) + 词干 + \w* 尾随（P4 复审二轮 cso 方案）——
# 覆盖复数（secrets/credentials/passwords/tokens/permissions/logins/apis）、
# 下划线拼接（secret_store/api_key/auth_keys/socket_io/tls_config/ssl_key）与
# 词干形态（authorization/oauth2/encryption/decryptor/vaulting）；同时保持 F3
# 误标消除不回退：author（AUTHORS.md/author）经 auth(?!or) + 显式 authoriz 分支区分，
# apiary 经 api(?!ary) 区分，graphic/rapid 靠左锚拒绝（api 前是词字符），
# xmlns/innetwork 无词干或左锚拒绝。路径一律小写匹配。
_SENSITIVE_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:authoriz|authz|auth(?!or)|api(?!ary)|"
    r"login|password|passwd|session|cookie|jwt|oauth|tls|ssl|crypto|encrypt|"
    r"decrypt|vault|rbac|acl|pii|privacy|2fa|otp|csrf|xss|security|permission|secret|"
    r"credential|network|socket|token|net)\w*"
    r"|data[-_](?:model|schema)"
)

# 配置类扩展名（文件类型 low 判定之一；与 agate/tests/ 并列）
_CONFIG_EXTS = frozenset({
    ".cfg", ".conf", ".ini", ".json", ".toml", ".yml", ".yaml",
})

_LEVEL_NUM = {"high": 3, "medium": 2, "low": 1}
_WEIGHTS = {"file-type": 2, "sensitive-path": 2, "change-size": 1, "impact": 1}


def _norm_rel(path):
    """repo 相对路径统一 / 分隔（Windows 反斜杠归一，BDD-13）。"""
    return path.replace("\\", "/")


def _is_config(path):
    """配置类判定：扩展名命中或隐藏文件（dotfile）。"""
    p = _norm_rel(path)
    base = p.rsplit("/", 1)[-1]
    if base.startswith("."):
        return True
    ext = os.path.splitext(base)[1].lower()
    return ext in _CONFIG_EXTS


def _file_type_level(path):
    """文件类型信号：agate/**/*.md / agate/scripts/*.py → high；tests/配置 → low；其余 → medium。"""
    p = _norm_rel(path)
    if re.match(r"^agate/.*\.md$", p) or re.match(r"^agate/scripts/.*\.py$", p):
        return "high", "%s 属协议本体/gate 逻辑" % p
    if p.startswith("agate/tests/") or _is_config(p):
        return "low", "%s 属测试/配置" % p
    return "medium", "%s 属普通源码" % p


def _sensitive_level(path):
    """敏感路径信号：关键词命中 → high + security 域标注；无 → low。"""
    p = _norm_rel(path)
    m = _SENSITIVE_RE.search(p.lower())
    if m:
        return "high", "%s 命中敏感关键词(%s) -> domain: security" % (p, m.group(0))
    return "low", "无敏感关键词命中"


def _change_size_level(count):
    """改动规模信号：_staged_source_count（check-pruning 同口径）> 5 → high。"""
    if count > 5:
        return "high", "source files=%d > 5" % count
    return "low", "source files=%d <= 5" % count


def _is_task_artifact(path):
    """任务产出文档判定（F1，P4-review）：只对代码模块生效——
    跳过定名 artifact（P1-requirements.md / P2-design.md / P6-acceptance.md 等
    P[0-8]-*.md）与 agate-workspace/tasks/** 树（协议工具链天然引用定名产出，
    计入影响面会造成 thin 档在 dogfood/多任务工作区不可达的假阳性）。"""
    p = _norm_rel(path)
    base = p.rsplit("/", 1)[-1]
    if re.match(r"^P[0-8]-.*\.md$", base):
        return True
    if p.startswith("agate-workspace/tasks/"):
        return True
    return False


def _impact_high(staged_files, repo_root, task_dir):
    """反向引用扫描（NB-3 判据）：改动文件 F 的模块标识被其他文件引用 → 影响面 high。

    F 排除 agate/tests/、配置类与任务产出文档（F1）；模块标识 = basename 去扩展名；
    搜索面 = repo_root 排除 task_dir 树与 agate/tests/ 树；命中 = ≥1 行且所在文件非 F 自身。
    """
    repo_root_abs = os.path.realpath(repo_root)
    task_abs = os.path.realpath(task_dir) if task_dir else None

    for f in staged_files:
        p = _norm_rel(f)
        if p.startswith("agate/tests/") or _is_config(p) or _is_task_artifact(p):
            continue
        module = os.path.splitext(os.path.basename(p))[0]
        if not module:
            continue
        f_abs = os.path.realpath(os.path.join(repo_root_abs, p))
        found = _scan_module_references(module, repo_root_abs, f_abs, task_abs)
        if found:
            return True, module
    return False, None


def _scan_module_references(module, repo_root_abs, f_abs, task_abs):
    """在 repo_root（排除 task 树 / agate/tests 树 / .git / F 自身）搜模块标识引用行。"""
    pattern = re.compile(r"\b" + re.escape(module) + r"\b")
    for dirpath, dirnames, filenames in os.walk(repo_root_abs):
        dirnames[:] = [
            d for d in dirnames
            if d != ".git"
            and not (task_abs and os.path.realpath(os.path.join(dirpath, d)) == task_abs)
        ]
        try:
            rel_dir = os.path.relpath(dirpath, repo_root_abs).replace("\\", "/")
        except ValueError:
            continue
        if rel_dir.startswith("agate/tests/"):
            dirnames[:] = []
            continue
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            if os.path.realpath(path) == f_abs:
                continue
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
            except OSError:
                continue
            if pattern.search(content):
                return True
    return False


def _read_declared_domains(task_dir):
    """P1 frontmatter domains 声明（经 _md_field，复用 check-pruning 读取链）。"""
    p1_file = os.path.join(task_dir, "P1-requirements.md")
    try:
        domains_raw = _check_pruning._md_field("domains", p1_file)
    except Exception:
        return []
    return [d for d in domains_raw.split() if d]


def score_task(task_dir):
    """对 task_dir 的暂存区算分，返回 dict（五信号 + risk_score + tier + domain-markers + git_ok）。"""
    result = {
        "git_ok": False,
        "risk_score": 0,
        "tier": None,
        "file-type": "low (git 通道不可用，未算分)",
        "sensitive-path": "low (git 通道不可用，未算分)",
        "change-size": "low (git 通道不可用，未算分)",
        "impact": "low (git 通道不可用，未算分)",
        "domain-markers": [],
    }
    if run_git is None:
        return result

    rc, out = run_git(["rev-parse", "--show-toplevel"], cwd=task_dir)
    if rc != 0:
        return result
    repo_root = out.rstrip("\n").strip()
    if not repo_root:
        return result

    rc, out = run_git(["diff", "--cached", "--name-only"], cwd=task_dir)
    if rc != 0:
        return result
    staged_files = [
        raw.rstrip("\r") for raw in out.splitlines() if raw.strip()
    ]

    # --- 逐信号判定 ---
    ft_level, ft_ev = _max_level(
        (_file_type_level(f) for f in staged_files), default=("low", "无暂存改动")
    )
    sn_level, sn_ev = _max_level(
        (_sensitive_level(f) for f in staged_files), default=("low", "无暂存改动")
    )
    count = _staged_source_count(task_dir) if staged_files else 0
    cs_level, cs_ev = _change_size_level(count)
    imp_found, imp_module = _impact_high(staged_files, repo_root, task_dir)
    if imp_found:
        imp_level, imp_ev = "high", "module %s 被其他文件反向引用" % imp_module
    else:
        imp_level, imp_ev = "low", "无反向引用"

    # --- 域映射（标注，不参与 tier）---
    domain_markers = []
    if sn_level == "high":
        domain_markers.append("security")
    for d in _read_declared_domains(task_dir):
        if d and d not in domain_markers:
            domain_markers.append(d)

    # --- tier 合成（max 分级规则）---
    levels = [ft_level, sn_level, cs_level, imp_level]
    if "high" in levels:
        tier = "full"
    elif all(lv == "low" for lv in levels):
        tier = "thin"
    else:
        tier = "standard"

    # --- risk_score 数值（展示锚点；权重加权和）---
    risk_score = sum(
        _LEVEL_NUM[levels[i]] * _WEIGHTS[key]
        for i, key in enumerate(("file-type", "sensitive-path", "change-size", "impact"))
    )

    result.update({
        "git_ok": True,
        "risk_score": risk_score,
        "tier": tier,
        "file-type": "%s (%s)" % (ft_level, ft_ev),
        "sensitive-path": "%s (%s)" % (sn_level, sn_ev),
        "change-size": "%s (%s)" % (cs_level, cs_ev),
        "impact": "%s (%s)" % (imp_level, imp_ev),
        "domain-markers": domain_markers,
    })
    return result


def _max_level(levels_iter, default=None):
    """多文件取最高级别（high > medium > low）；空序列用 default。"""
    best = None
    best_ev = ""
    seen = False
    for level, ev in levels_iter:
        seen = True
        if best is None or _LEVEL_NUM[level] > _LEVEL_NUM[best]:
            best, best_ev = level, ev
    if not seen:
        return default if default else ("low", "")
    return best, best_ev


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("用法: agate-risk-score.py TASK_DIR\n")
        sys.exit(1)
    task_dir = sys.argv[1]
    score = score_task(task_dir)
    print("risk_score: %s" % score["risk_score"])
    print("tier: %s" % (score["tier"] if score["tier"] else "standard"))
    print("file-type: %s" % score["file-type"])
    print("sensitive-path: %s" % score["sensitive-path"])
    print("change-size: %s" % score["change-size"])
    print("impact: %s" % score["impact"])
    print("domain-markers: [%s]" % ", ".join(score["domain-markers"]))
    print("git_ok: %s" % ("true" if score["git_ok"] else "false"))


if __name__ == "__main__":
    main()