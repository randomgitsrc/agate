# tests/unit/test_agate_cmdstream_dispatch.py — 受控自主再派发边界（TAG0028 P3，RM-AG0055）
# 被测（P4 才落地，本文件当前必须红）：
#   - agate/role-system.md「子派发权限边界」节（M6：执行角色子派发两条硬边界 + judge 例外）
#   - agate/assets/templates/dispatch-context.md「不启用子派发能力」声明位（M7）
#   - agate/dispatch-protocol.md「subagent 自主再派发」节（M5③：产出收敛语义）
#
# 覆盖 P1-requirements.md BDD-29/30/31/32/33（不写 .state.yaml / 写权限子集 / judge 例外 /
# 产出收敛不触发 gate / gate 返回约定不破坏）。
#
# 文档断言语义：role-system.md / dispatch-context.md 模板当前不含上述边界表述（S-7 空白确认
# + M6/M7 未落地）→ 断言失败 = "被测内容未实现"语义（B 类红灯，非断言与 fixture 数据矛盾）。
# BDD-33（gate 返回约定不破坏）为长期不变量：运行既有 check-gate.py / check-state-transition.py
# 断言 exit 三态（0/1/2）可用（TAG0025：断言当前状态而非一次性交付事实）。


def _read_text(p):
    return p.read_text(encoding="utf-8")


# ================= BDD-29: 执行角色子派发权限下放（不写 .state.yaml） =================


def test_bdd_29_no_state_yaml_boundary(agate_root):
    """BDD-29（文档断言，红）：role-system.md 含子派发权限边界——子任务不写
    .state.yaml / active-tasks.md，不产生独立 phase 状态；主 Agent 视角仍是"一个 subagent
    在跑"，父汇总后仅以"路径+摘要"格式回报。"""
    text = _read_text(agate_root / "role-system.md")
    # 靶向 M6 改写后新增的"子派发权限边界"节（S-7：role-system 现无子派发权限边界描述）
    assert "子派发" in text, "role-system.md 未含子派发权限边界节（M6 未落地）"
    assert ".state.yaml" in text
    assert "active-tasks.md" in text


# ================= BDD-30: 子任务写权限严格子集 =================


def test_bdd_30_write_subset_boundary(agate_root):
    """BDD-30（文档断言，红）：role-system.md 含写权限严格子集边界——子任务只能触碰父
    约束目录内文件，父在派子任务 prompt 中显式重申约束，子任务不自动继承父权限。"""
    text = _read_text(agate_root / "role-system.md")
    assert "子派发" in text, "role-system.md 未含子派发权限边界节（M6 未落地）"
    assert "严格子集" in text, "role-system.md 未含写权限严格子集边界（M6 未落地）"


# ================= BDD-31: judge 类角色例外声明 =================


def test_bdd_31_judge_exception_role_system(agate_root):
    """BDD-31（文档断言，红）：role-system.md 声明 judge 类角色不适用子派发——不开放
    Agent/subagent_fork 工具权限，信息隔离冲突消解。"""
    text = _read_text(agate_root / "role-system.md")
    # 靶向"judge + 子派发"组合表述（judge 单独命中既有表格泛词，组合表述才是 M6 新增）
    assert "judge" in text.lower()
    assert "子派发" in text, "role-system.md 未含子派发权限边界节（M6 未落地）"
    # 例外语义：judge 不开放子派发能力（信息隔离冲突，设计 §4.4）
    assert "不开放" in text or "不启用" in text, "role-system.md 未声明 judge 子派发例外（M6 未落地）"


def test_bdd_31_judge_no_subdispatch_declaration(agate_assets):
    """BDD-31（文档断言，红）：dispatch-context 模板补「不启用子派发能力」显式声明位
    （judge 角色派发时注入，M7）。"""
    text = _read_text(agate_assets / "templates" / "dispatch-context.md")
    assert "不启用子派发能力" in text, "dispatch-context.md 模板未含声明位（M7 未落地）"


# ================= BDD-32: 子派发产出收敛、不触发 gate 判定 =================


def test_bdd_32_output_convergence_no_gate(agate_root):
    """BDD-32（文档断言，红）：子任务中间产出不计入 gate 判定对象；仅父 subagent 最终声明的
    files_modified 走既有假完成校验（D2）；不产生新编排层级。"""
    text = _read_text(agate_root / "dispatch-protocol.md")
    # 靶向 M5③ 新增的"subagent 自主再派发"节（files_modified 单独命中既有 D2 校验泛词）
    assert "自主再派发" in text, "dispatch-protocol.md 未含 subagent 自主再派发节（M5③ 未落地）"
    assert "files_modified" in text
    assert "不产生新的编排层级" in text or "不产生新编排层级" in text, (
        "dispatch-protocol.md 未声明不产生新编排层级（M5③ 未落地）")


# ================= BDD-33: 不破坏 gate 返回约定（两套独立信号） =================


def test_bdd_33_gate_return_contract_preserved(
    agate_scripts, python_exe, run_cli, task_dir, git_repo
):
    """BDD-33（长期不变量可绿）：check-gate.py 与 check-state-transition.py 对既有任务仍返回
    exit 三态约定（0/1/2）——心跳/命令流判定信号不并入 gate 判定路径。
    check-gate.py 形态：PHASE TASK_DIR（exit 0/1/2）；
    check-state-transition.py 形态：[STATE_FILE]（cwd=git repo，staged 状态驱动，exit 0/1/2）。"""
    td = task_dir(phases=["P1", "P2"])

    gate = run_cli(python_exe, str(agate_scripts / "check-gate.py"), "P1", str(td))
    assert gate.returncode in (0, 1, 2), f"check-gate.py 返回非三态: {gate.returncode}"

    repo = git_repo.path
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    git_repo.commit("init")
    (repo / ".state.yaml").write_text((td / ".state.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    trans = run_cli(
        python_exe, str(agate_scripts / "check-state-transition.py"), ".state.yaml", cwd=str(repo)
    )
    assert trans.returncode in (0, 1, 2), f"check-state-transition.py 返回非三态: {trans.returncode}"
