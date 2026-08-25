# P0-brief — TAG0024 工具链批：结构化字段写入工具（agate-md-field-set）+ 前置修复

> 本文件由主 Agent 亲自填写（P0 阶段产出）。

## task

"工具链批（RM-AG0048 一期 + DEBT0019 + DEBT0020 + RM-AG0049 + RM-AG0050 合并一个 task）：给 subagent 提供'写入即校验'的结构化 set 工具（补 get 工具缺失的 set 面），消灭手写 frontmatter 摩擦（P1-gate-diagnosis 实证）；同时修复 check-gate.py roadmap-done 检查的两处健壮性缺陷（DEBT0019/20）与两处协议文档自洽 NIT（RM-AG0049/50）——同属'工具链/协议卫生'簇，合并一个 task"

### issues（合并来源）

- **RM-AG0048（一期）**：新增 `agate-md-field-set.py` + `agate-md-field-set-gate-commands.py`——key 从 schema 白名单限定（phases.yaml task_fields ∪ task-files 通用 Header）、value 写入时校验（与 check-gate 同源）、格式由工具生成（YAML 序列化）；自描述（--list/--help/错误给合法值，判据"零协议知识 subagent 照提示填对"）；写入即局部校验 + 剩余缺失报告；角色/阶段/文件三维权限（角色维度读文件 agent 字段，选项 A）；证据字段（pass/fail/blocker_count 等）set 拒绝写入；gate_commands 正文 YAML 块经专用子命令整块替换（同源校验）；原子写 + 版本一致（resolve-entry 链）；dispatch-context 模板加一行式指令 + dispatch-prompt 改"用 set 填"；验收锚=design-md-field-set.md §10 十一条
- **DEBT0019**：`check-gate.py._check_roadmap_done()` 用固定索引 split("|") 解析 roadmap.md 表格，无列数完整性校验——未来描述含字面 `|` 时状态判定可能错位。修复=列数校验（非法列数跳过/WARNING）+ 回归用例
- **DEBT0020**：`check-gate.py._check_roadmap_done()` 调用点用相对 CWD 硬编码路径拼接 roadmap.md——非仓库根 CWD 调用时 P8 roadmap-done 检查被静默绕过。修复=对齐 repo-root 定位（git rev-parse --show-toplevel）或加区分性 stderr 提示 + 回归用例
- **RM-AG0049**：phases.yaml P4 outputs 未列出 P4-review.md，但 check-gate.py gate_p4 实际要求其存在（与 P1/P2 review 产出声明不对称）。修复=phases.yaml P4 outputs 补 `{file: P4-review.md, required: true, status_field: status}` + 核对 check-structure-consistency 同步
- **RM-AG0050**：phases.yaml 将 P6.5 列为独立阶段条目，state-machine.md 明确其为"挂载于 P6→P7 转移的强门槛子阶段，非独立 phase 值"——两处定位叙述不一致。修复=统一为"强门槛子阶段"口径（state-machine 为准），核对 check-gate/check-judge-verdict 消费端不受影响

## known_risks

- "改动面：新增 agate-md-field-set.py / agate-md-field-set-gate-commands.py + check-gate.py + phases.yaml + dispatch-prompt/dispatch-context 模板 + 测试 → 触发 SELF-GATE"
- "RM-AG0048 的'与 gate 同源'需谨慎：set 的 value 校验复用 check-gate 判定逻辑，须走同一 schema 源（phases.yaml + task-files）+ resolve-entry 版本链，避免'set 说通过、gate 说不通过'的新漂移——P2 需设计同源复用路径（import vs 复制）"
- "RM-AG0048 角色权限（选项 A：读文件 agent 字段）只对'遵守协议填了 agent 的 subagent'有效——set 是引导非安全边界，防造假靠 gate 链（文档 §7 已声明，P2 需确认不产生'set 允许、gate 拒绝'的二次不一致）"
- "DEBT0019/20 改 check-gate.py 的 roadmap-done 检查——需回归 TAG0023 的 BDD（P8 roadmap 回写校验）确保不破坏"
- "RM-AG0049 改 phases.yaml P4 outputs——check-structure-consistency S-1/S-2 双向一致性 gate 可能因 YAML→md 不一致报错，需同步核对"
- "【强制要求】同类扫描：grep get 工具全部 op（agate-md-field-get.py）确认 set 白名单覆盖；grep roadmap 表格解析消费点（check-gate/check-retrospective）；grep P6.5 定位消费点（check-gate/check-judge-verdict/state-machine）"
- "design note（docs/design-notes/design-md-field-set.md）仅为参考输入，不作为本 task 交付物；执行中发现需求/设计层面弊端或缺陷，按实际情况调整（改设计/登记 DEBT），不强制照搬"

## executor_env

platform: "opencode"
has_task_tool: true
has_local_runtime: true
network: "full"
git: true

## env_constraints

debug_env: "本环境为 Linux；/tmp 只读（pytest 需 --basetemp + -p no:cacheprovider）；权限 danger-full-access；ruff 0.16.4（~/.venvs/agate-dev/bin/ruff）"
test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict-errors-only；bash agate/tests/scripts/count-tests.sh；~/.venvs/agate-dev/bin/ruff check agate/"
workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0024-toolchain-md-field-set/"
