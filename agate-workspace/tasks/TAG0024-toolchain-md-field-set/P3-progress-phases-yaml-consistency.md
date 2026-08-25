# P3 进度记录 —— 批次 phases-yaml-consistency（BDD-25~29）

- [读完] test-designer 角色定义 + dispatch-context-phases-yaml-consistency.md
- [读完] P1-requirements.md BDD-25~29 原文
- [读完] P2-design.md §1.1（改动落点表）、§3.8（P4 outputs 补全）、§3.9（P6.5 措辞统一）
- [确认] `agate/tests/unit/test_check_structure_consistency.py` 已存在（S-1~S-6 双向一致性测试），
  本批次追加到该文件末尾，不新建文件
- [确认] 该文件既有测试用 `make_fake_root`（假协议树）驱动 check-structure-consistency.py 子进程，
  但 BDD-25/26/27/28 的性质是"验真实仓库 agate/rules/phases.yaml + agate/state-machine.md"，
  与既有假协议树用例目的不同 → 新增用例直接用 `agate_root` fixture（真实仓库根）而非
  `make_fake_root`，与既有用例风格区分但共存于同一文件
- [查证] 当前真实 `agate/rules/phases.yaml`：`id: P4` outputs 仅含 `P4-implementation.md`，
  无 `P4-review.md` 条目 → BDD-25 断言"outputs 含 P4-review.md" 在当前文件下应为真红灯
- [查证] `id: P6.5` 块前当前无任何注释说明"非独立 phase 值" → BDD-27 断言应为真红灯
- [查证] `agate/state-machine.md` 第 74-78 行、152-155 行已有"P6.5 是挂载于 P6→P7 转移上的
  强门槛子阶段，非独立 phase 值"表述（作为 BDD-27 对照锚点，已存在，green 侧）
- [查证] `check-gate.py::gate_p65()`（第 1032-1055 行）判定逻辑只读 task_dir/.state.yaml 的
  `judge.enabled` 字段 + 调 check-judge-verdict.py/check-events.py 子脚本，**不读取**
  agate/rules/phases.yaml 任何内容 → 佐证 BDD-28"既有判定行为不变"可用真实二进制调用验证
  + 用 yaml.safe_load 前后对比结构化字段等价来验证（comment-only 改动对 yaml.safe_load 结果无影响）
- [查证] `check-judge-verdict.py` / `check-events.py` grep 均无 `phases.yaml`/`AGATE_ROOT` 消费点
- [设计] BDD-25：读取真实 phases.yaml，assert P4.outputs 含 {file:P4-review.md, required:true, status_field:status}（真红灯）
- [设计] BDD-26：拷贝真实 agate 根（rules/WORKFLOW.md/phase-cards/scripts/assets）到 tmp_path，
  在拷贝上打上 BDD-25 的 fix 补丁，跑真实 check-structure-consistency.py 子进程，断言 exit 0
  （回归守卫，非红灯，dispatch-context 已声明此性质）
- [设计] BDD-27：读取真实 phases.yaml 原文，提取 `- id: P6.5` 前的连续注释块，断言其中同时含
  "强门槛子阶段"与"非独立"/"不是独立"与"phase" 关键词（真红灯，当前无此注释）；state-machine.md
  侧作为控制组断言已含一致表述（green）
- [设计] BDD-28：① yaml.safe_load 对比"打补丁前/后"phases.yaml 解析出的 P6.5 条目结构化字段
  完全相等（证明 comment-only 改动对消费方不可见）；② 用 task_dir fixture 构造 judge 未启用的
  历史任务，分别以 AGATE_ROOT=真实仓库根 / AGATE_ROOT=打补丁副本根 跑 `check-gate.py P6.5`，
  断言两次 exit code 与 stderr 逐字节相同
- [设计] BDD-29：判定为"无法写出有意义自动化单测"（约束跨越 check-gate.py/check-events.py 全部
  判定逻辑 diff，属于 P7 一致性检查阶段的职责），按 dispatch-context 建议标注为
  "P7 阶段 diff 核对覆盖"，不写自动化测试函数，仅在 P3-test-cases.md 中显式列出处理方式
- [完成] 追加 4 个测试函数 + 4 个共享 helper 到 `agate/tests/unit/test_check_structure_consistency.py`
  （BDD-25/26/27/28，共 168 行新增）
- [自跑确认] `python3 -m pytest agate/tests/unit/test_check_structure_consistency.py -v
  --basetemp=.pytest-tmp -p no:cacheprovider`：17 items，15 passed / 2 failed。
  - `test_bdd_25_p4_outputs_includes_review_md` FAILED（AssertionError，真红灯 B 类）
  - `test_bdd_27_phases_yaml_p65_comment_matches_state_machine_wording` FAILED（AssertionError，真红灯 B 类）
  - `test_bdd_26_*` / `test_bdd_28_*` PASSED（回归守卫性质，符合 dispatch-context 预期）
  - 既有 13 条 S-1/S-2/S-3(a/b) 用例全部保持 PASSED，未受影响
- [自跑确认] 跑了一次全仓 `python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -q`：
  41 failed / 1202 passed / 2 skipped / 41 errors。用 `git diff --stat` 核实本次改动只涉及
  `agate/tests/unit/test_check_structure_consistency.py` 一个文件；其余失败（`test_agate_md_field_set.py`
  全部、`test_check_gate.py` 的 BDD-20/22/23、`test_env_adapt_docs.py::test_bdd_34`、
  `test_pre_commit_hook.py` 41 个 ERROR）经核实分别属于另两个并行批次
  （md-field-set-tool / check-gate-debt-fixes）的红灯产出，或与本批次改动无关的既有环境依赖，
  不在本批次处理范围
- [完成] 写 `P3-test-cases-phases-yaml-consistency.md`（含步骤 3 判断结果 + BDD-25~29 逐条映射 +
  BDD-29 非自动化处理说明 + 自跑红灯确认）
- [完成] 批次收尾，返回路径 + 摘要给主 Agent
