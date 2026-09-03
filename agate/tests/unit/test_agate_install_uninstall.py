# tests/unit/test_agate_install_uninstall.py — 卸载引用保护扫描限流提示（TAG0031 DEBT0004，BDD-4/5）
# 被测：agate/scripts/agate-install.py 的 `_find_references`（卸载引用保护扫描，限深度
# `_SCAN_MAX_DEPTH=4` + mtime 窗口 `_SCAN_MTIME_WINDOW=365 天`限流）与 `_cmd_uninstall`
# （消费点，命中限流边界时应 stderr 输出 WARNING）。
#
# 设计（P2-design.md §1.1 簇 A）：`_find_references` 返回值由现状「plain list」改为
# `(refs, hit_limit)` 二元组——`depth > _SCAN_MAX_DEPTH` 触发剪枝或 `.agate-version` 命中但
# mtime 超窗跳过时置 `hit_limit=True`；`_cmd_uninstall` 解包后，`hit_limit` 为真时立即 stderr
# 输出 WARNING（不论 refs 是否为空——WARNING 与卸载判定放行与否是两件独立的事）。
#
# 当前状态（迁移前）：`_find_references` 仍返回 plain list（不是二元组）——本文件用
# `refs, hit_limit = module._find_references(...)` 解包，1 元素 list 解包进 2 个变量触发
# `ValueError: not enough values to unpack`（真实的项目内运行时失败 = B 类红灯语义，非测试
# 代码自身语法错误）；`_cmd_uninstall` 当前无 WARNING 输出机制，行为层断言同样失败。
#
# 网络隔离：`run_git` 全程 monkeypatch（不调真实 git），HOME 环境变量重定向到 tmp_path（同
# agate-install.py 模块 docstring 既有测试隔离约定），不触碰真实 ~/.agate。

import importlib.util
import sys

import pytest


def _load_script_module(agate_scripts, module_name, filename):
    """从 agate/scripts/ 加载脚本为模块；被测模块未实现 → ModuleNotFoundError（B 类红灯）。"""
    path = agate_scripts / filename
    if not path.is_file():
        raise ModuleNotFoundError(f"No module named '{module_name}' (被测模块未实现: {filename})")
    scripts_dir = str(agate_scripts)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bdd_4_find_references_and_uninstall_warn_when_scan_limit_hit(
    tmp_path, agate_scripts, monkeypatch, capsys
):
    """BDD-4：限流边界命中时输出 WARNING。

    Given ~/.agate 卸载引用扫描的目标目录树中存在超出扫描边界（深度 > 4）的项目，该项目的
    .agate-version 声明了即将卸载的版本
    When 执行 agate-install.py uninstall <version>
    Then stderr 输出 WARNING，明确提示"扫描存在深度/时间窗口限流，可能未覆盖全部引用"，卸载
    判定不因此项目被漏扫而误判为"无引用可安全卸载"
    """
    module = _load_script_module(agate_scripts, "agate_install_bdd4", "agate-install.py")

    home = tmp_path / "home"
    version = "v1.2.3"
    # 深度 5（a/b/c/d/e）> _SCAN_MAX_DEPTH(4) —— os.walk 遍历到 'e' 时 depth=5 即触发
    # dirs[:] = [] + continue 剪枝，'e' 自身的 .agate-version 也不会被检查到（漏扫场景）。
    deep = home / "a" / "b" / "c" / "d" / "e"
    deep.mkdir(parents=True)
    (deep / ".agate-version").write_text(f"agate: {version}\n", encoding="utf-8")

    # 机制层：_find_references 返回值应为 (refs, hit_limit) 二元组，命中限流边界 → hit_limit=True
    refs, hit_limit = module._find_references(str(home), version)
    assert hit_limit is True
    assert refs == []  # 深度限流剪枝，扫不到该项目——这正是 BDD-4 描述的"漏扫"风险本身

    # 行为层：_cmd_uninstall 命中限流边界应输出 WARNING（不论 refs 是否为空都要提示）
    agate_home = home / ".agate"
    agate_home.mkdir(parents=True)
    monkeypatch.setattr(module, "run_git", lambda *a, **k: (0, ""))
    monkeypatch.setenv("HOME", str(home))

    with pytest.raises(SystemExit):
        module._cmd_uninstall(str(agate_home), version)

    err = capsys.readouterr().err
    assert "WARNING" in err


def test_bdd_5_find_references_no_warning_within_scan_bounds(
    tmp_path, agate_scripts, monkeypatch, capsys
):
    """BDD-5：未命中限流边界时不产生 WARNING 噪音（边界流，防止过度提示）。

    Given ~/.agate 卸载引用扫描范围内所有 .agate-version 文件均在深度 ≤4 且 mtime 365 天窗口内
    When 执行卸载扫描
    Then stderr 不输出限流 WARNING（仅在真实命中限流边界时才提示，避免噪音掩盖真实信号）
    """
    module = _load_script_module(agate_scripts, "agate_install_bdd5", "agate-install.py")

    home = tmp_path / "home"
    version = "v1.2.3"
    # 深度 1（home/proj），远在 _SCAN_MAX_DEPTH(4) 与 mtime 365 天窗口内 —— 正常可扫场景
    proj = home / "proj"
    proj.mkdir(parents=True)
    (proj / ".agate-version").write_text(f"agate: {version}\n", encoding="utf-8")

    # 机制层：未命中限流边界 → hit_limit=False，且该真实引用应被正常发现（refs 非空）
    refs, hit_limit = module._find_references(str(home), version)
    assert hit_limit is False
    assert refs == [str(proj)]

    # 行为层：_cmd_uninstall 应因真实引用拒绝卸载（与 WARNING 无关的独立判定），但不应有
    # 限流 WARNING 噪音——refs 非空触发的是"拒绝卸载"提示，不是限流 WARNING
    agate_home = home / ".agate"
    agate_home.mkdir(parents=True)
    monkeypatch.setattr(module, "run_git", lambda *a, **k: (0, ""))
    monkeypatch.setenv("HOME", str(home))

    with pytest.raises(SystemExit):
        module._cmd_uninstall(str(agate_home), version)

    err = capsys.readouterr().err
    assert "WARNING" not in err
