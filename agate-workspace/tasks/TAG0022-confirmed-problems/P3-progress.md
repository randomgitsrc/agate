# P3 进度 — TAG0022 test-designer（分阶段落盘）

> 状态标记：`[PROD_NOT_TOUCHED]`（只写 worktree `agate/tests/` 与 `agate-workspace/tasks/`；`~/.agate` 稳定版与主 checkout 只读）。

## 2026-08-22 步骤 1：读输入文件

- 读 `assets/execution-roles/test-designer.md`（角色定义，TDD 1:1 BDD 映射、真红灯口径）✓
- 读 `P3-dispatch-context-test-designer.md`（强制指令 + AGATE_CARD=P3 卡片全文）✓
- 读 `P0-brief.md` / `P1-requirements.md`（BDD-1..10）✓
- 读 `P2-design.md` 全文件（§3 完成标准 / §4.2.1 逐点映射 / §4.3 judge 判据 / §4.5 0041 / §7 files_to_read）✓
- 读 `P2-review.md`（NB-1~6 + TG-1~3 + 锁定决策 1-8）✓
- 关键冻结：0039 判据=judge presence + P1 created(ISO) ≥ judge_required_since(2026-08-22) + created 缺失/非 ISO fail-open（锁定决策 2）；falsy 与缺失同走 created 判据（NB-4 推荐口径）；S-3a/S-3b 叠加在既有 S-3 下（NB-1）；`_run_routing` 需 env 透传（NB-5）；`_frontmatter_field` 实核 9 处调用含 L799/805（NB-6）

## 2026-08-22 步骤 2：读测试现状文件

- `agate/tests/unit/test_check_gate.py`（`_run_gate` helper L30-43；gate_p1 既有用例 L62-76；gate_p65 judge 三态 L2662-2735）✓
- `agate/tests/unit/test_check_routing.py`（`_run_routing` L20-26 无 env 参数；test_bdd_7 L148-156；`_write_p1`/`git_repo` fixture 用法）✓
- `agate/tests/unit/test_env_adapt_docs.py`（test_bdd_25 L47-60 无 basetemp 感知）✓
- `agate/tests/unit/test_check_structure_consistency.py`（S-* 既有用例 + `_rules_test_utils.make_fake_root` 夹具）✓
- `agate/tests/conftest.py`（`_run_cli_impl` L55-73 已支持 env 注入 → NB-5 可通；`create_task_dir` 默认 .state.yaml phase=P0 无 judge 块、P1 frontmatter 无 created）✓
- `agate/scripts/check-gate.py` 实读 gate_p1（L494-593）+ C 组各解析点字面（L390/417/428/693/703/736/878/909/950/1015/1048/1060/1127）+ `_frontmatter_field`（L164 定义 + L500/506/716/722/768/799/805/1108/1109 调用）→ 静态扫描模式清单据此固化 ✓
- `agate/scripts/check-protocol-consistency.py` iter_md_files（L119-138）排除链 + CHECK 2 REF_RE（L241）→ M15 单测/污染模拟依据 ✓

## 2026-08-22 步骤 3：环境自检

- ptmp 可写（mkdir -p 成功）；pyyaml 6.0.1 / pytest 9.0.3 可用 ✓
- check-protocol-consistency.py `__main__` 守卫在 L1172 → importlib 加载可安全复用 iter_md_files ✓

## 2026-08-22 步骤 4：test_md_parse_scan.py（0038/BDD-3）

- 新文件 `agate/tests/unit/test_md_parse_scan.py`：A/B/C/D 组 24 条模式清单静态扫描 check-gate.py（只扫非注释代码行；E/F 组不计入；NB-6 补全 L799/805）落盘 ✓
- 自跑：**1 failed（红）**，失败原因=check-gate.py 未迁移，命中 43 处（`_frontmatter_field` 10 + B 组 16 + C 组 16 + D 组 1），断言 `43 == 0` 失败——B 类真红灯（被测行为未实现，非测试 bug）✓

## 2026-08-22 步骤 5：test_check_gate.py 增补（0039/BDD-6/7）

- 追加 7 个用例（helpers `_write_p1_review_approved` / `_write_state_yaml_p1`；created 经 `add_p1_field`；P1-review 合规前置保证 P3 现状走到 exit 2）✓
- 自跑（-k 过滤新用例 + gate_p65）：**2 failed（红）+ 10 passed**
  - 红：`test_bdd_6_gate_p1_new_task_missing_judge_exit_1`（assert 2==1，judge P1 校验未实现）；`test_bdd_6_gate_p1_judge_disabled_after_cutoff_exit_1`（同因）——B 类
  - 绿守卫 5：judge.enabled true / 历史 pre-cutoff 无 judge / 无 created fail-open / falsy pre-cutoff / judge 非 dict fail-open
  - 既有 gate_p65 judge 五用例全绿（锁定决策 5 未破坏）✓

## 2026-08-22 步骤 6：test_check_structure_consistency.py 增补（0038/BDD-5 S-3a/S-3b，TG-1）

- 追加 3 用例（`_phases_with_p2_gate_cmd` / `_card_with_gate_rules` helper；基于 make_fake_root 假协议树；NB-1：不触碰产出规格/派发节）✓
- 自跑：**2 failed（红）+ 11 passed**
  - 红：`s3a_yaml_gate_cmd_not_in_card_exit_1`（YAML 侧漂移不报，exit 0≠非0）；`s3b_card_gate_cmd_not_in_yaml_exit_1`（md 侧漂移不报）——B 类（S-3a/b 未实现）
  - 绿守卫 1：双侧一致 exit 0；既有 S-* 用例 10 个全绿（NB-1 未回归）✓

## 2026-08-22 步骤 7：test_check_routing.py 修改（0041/BDD-9/10，test_bdd_7）

- `_run_routing` 增 env 透传（NB-5）；test_bdd_7 注入 `GIT_CEILING_DIRECTORIES=<tmp_path>` 使 git 上下文确定性 git_ok:false（P2 §4.5.1；无裸 python3/PATH、无 /tmp 字面、无 symlink 假设）✓
- 自跑：**16 passed（全绿）**——test_bdd_7 改造后转绿属预期（git 核心机制即时生效，dispatch-context 约束 3）；其余路由用例零回归 ✓

## 2026-08-22 步骤 8：test_env_adapt_docs.py 修改（0041/BDD-9/10，test_bdd_25 + M15/TG-3）

- test_bdd_25 改造为位置感知：basetemp ∈ 仓库根 → 注入 `AGATE_CONSISTENCY_SKIP_DIRS=<rel as_posix>`；仓库外不注入（P2 §4.5.2 + [SCOPE+] M15）✓
- 新增 M15 钩子单测 2 例（importlib 加载 check-protocol-consistency.py，monkeypatch env + 唯一模块名；默认行为/注入排除两断言）✓
- 自跑（仓库外 basetemp）：**1 failed（红）+ 10 passed**——红= `test_m15_iter_md_files_skip_dirs_injected_excluded`（M15 未实现 → skip-dir/c.md 仍产出，`not in` 断言失败，B 类）；`test_m15_iter_md_files_default_unchanged` 绿（行为不变守卫）；test_bdd_25 绿（仓库外分支）；既有用例全绿 ✓
- **仓库内位置红态机制验证**（CLI 级，直接模拟）：在 `<worktree>/agate/.bt-inrepo/pollute/` 植入坏引用 `scripts/ghost-file.py`（CHECK 2 REF_RE 命中）→ 无 env 注入 ERROR=1；注入 `AGATE_CONSISTENCY_SKIP_DIRS=agate/.bt-inrepo` 仍 ERROR=1（M15 未实现 → env 无效果 → 仓库内位置失败=红）→ 验证后 rm -rf 清理 ✓
- 注意：pytest 会在会话开始时清空 `--basetemp` 目录（实证），仓库内位置的"预存污染"由同会话先跑测试生成——TAG0020 实况一致；本机权威 basetemp=ptmp 在仓库外 → test_bdd_25 本地走绿分支 ✓

## 2026-08-22 步骤 9：综合自跑 + P3-test-cases.md

- 综合自跑（5 文件，外部 basetemp=ptmp）：**红 6 + 绿 227**
  - `test_md_parse_scan.py` 1 红；`test_check_gate.py` 2 红 + 170 绿（全文件回归零意外破坏）；`test_check_structure_consistency.py` 2 红 + 11 绿；`test_env_adapt_docs.py` 1 红 + 10 绿；`test_check_routing.py` 16 绿
  - 红集首因全部 = 被测模块未实现/行为未变更（B 类）：0038 迁移（静态扫描/S-3a/S-3b）、0039 judge P1 校验（缺失/falsy）、0041 M15 钩子（注入无效果）✓
- `P3-test-cases.md` 落盘：Header 合规 + `test_code_dir: agate/tests/unit/` + BDD-3/5/6/7/9/10 1:1 映射表（16 行）+ 红/绿汇总 + 契约注解（judge 判据/S-3 叠加/M15 默认关闭/test_bdd_7 转绿预期/test_bdd_25 位置感知）✓
- 返回前自检：grep 确认测试函数已落盘（10 处匹配）；P3-test-cases.md 含 test_code_dir 与 BDD 映射表 ✓
