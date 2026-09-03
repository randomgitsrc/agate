---
review_date: 2026-09-04
reviewer: protocol-alignment-review
change_summary: TAG0031 P4 批量修复 7 条历史技术债（DEBT0002/3/4/7/16/17/18）——离线包 compute_sha256 共享单实现、离线包信任边界文档、卸载引用扫描限流 WARNING、check-pruning.py 隔离修复验证、check-gate.py CODE-MAP 路径改用 resolve_workspace 权威解析、「新增文件核对表」判定改整行正则、4 个关键读取器 fail-closed
files_changed: [agate/scripts/agate_common.py, agate/scripts/agate-pack-offline.py, agate/scripts/install-offline.py, agate/scripts/agate-install.py, agate/scripts/check-gate.py, agate/UPGRADING.md, agate/scripts/README.md, agate-workspace/debt/tech-debt.md]
---

# 协议-脚本对齐审查

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | MISALIGNED（轻微，见下） |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | ALIGNED |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（`agate/scripts/README.md` 新增段落 / `agate/UPGRADING.md:513`）：
> **信任边界（TAG0031 DEBT0003）**：checksum 校验只防损坏……不防恶意构造的整包替换……bundle 提供者需可信

**脚本实现**（`install-offline.py` `verify_checksums`/`_ensure_agate_common`，L101-L167）：checksum 校验逻辑本身未变（仍是 sha256 比对），文档只是补充了既有行为的信任边界说明，未声称新增签名机制。语义一致。

其余 6 条无对应"协议文档声明规则"需要脚本落地的场景（均为脚本内部健壮性修复，非新协议规则），A1 判定不适用/默认满足。

**结论**：ALIGNED

### A2: 脚本→文档对齐

逐条核对 `agate-workspace/debt/tech-debt.md` 的 closure evidence 描述与实际脚本代码：

- DEBT0002/0004/0016/0018 的 closure note 描述（compute_sha256 单实现、`_find_references` 返回二元组、`resolve_workspace` 权威解析、4 消费点 fail-closed）均与实际代码逐字核对一致。

- **DEBT0017 closure note 与实际代码不一致**：

  **tech-debt.md 记录**：
  > closure：……判定改为整行/标题级正则（`re.search(r"^## 新增文件核对表\s*$", text, re.MULTILINE)`），替代原子串包含 `in` 判定

  **实际代码**（`check-gate.py:1038`）：
  ```python
  if not re.search(r"^##\s+新增文件核对表", _read_text(p4_impl_check), re.MULTILINE):
  ```
  实际正则**没有** `\s*$` 结尾锚点。且代码注释（`check-gate.py:1035-1037`）与测试 `test_tag0031_bdd_11_gate_p4_real_heading_trailing_text_satisfied`（`agate/tests/unit/test_check_gate.py:3308`）明确验证"标题行尾带附加说明文字（如「## 新增文件核对表（本次新增，逐文件标注）」）应判定为已满足，不触发 WARNING"——这与 tech-debt.md note 里带 `\s*$` 的正则（会要求标题后必须无内容）语义相反。代码和测试的实际行为是正确的（对齐 DEBT0017 本意"消除自指场景假阴性，同时不引入新假阳性"），**问题出在 tech-debt.md 的 closure evidence 文字引述有误**，不是代码有 bug。

  **结论**：MISALIGNED（限于 tech-debt.md 证据文字，不影响实际 gate 判定行为，也不影响本次 commit 的功能正确性）
  **建议**：修正 `agate-workspace/debt/tech-debt.md` 中 DEBT0017 closure note 的正则引述，去掉 `\s*$`，改为 `re.search(r"^##\s+新增文件核对表", text, re.MULTILINE)`，与代码一致。

**结论**：MISALIGNED（1 处，低严重度，纯文档引述纠正，不阻断 commit 判断留给主 Agent，建议顺手修正）

### A3: 一致性连锁 + 反向传播

**A3a（连锁）**：DEBT0002 迁移 `compute_sha256` 后，`agate-pack-offline.py`/`install-offline.py` 均已同步改为 import；DEBT0016 引入 `resolve_workspace` 后，`check-gate.py` 顶层 import 块（L43-47）同步加了 fallback；均已在 diff 中完整体现，无遗漏。

**A3b（反向传播，主动推断）**：
- 检查 `agate/dispatch-protocol.md`、`agate/state-machine.md`、`agate/WORKFLOW.md`、`agate/role-system.md`、`agate/phase-cards/*.md` 是否描述过 `read_rules_yaml`/`count_p6_pass_fail`/`count_p7_markers`/`count_code_map_lines` 的 ImportError 降级细节——**均未描述**，这几处文档只讲 `check-gate.py` 的通用 exit 0/1/2 语义（`README.md:6-10`："exit 0 = gate 通过; exit 1 = gate 未通过; exit 2 = 多数 phase 正常通过码"）。DEBT0018 新增的 `return 1` 落在既有"exit 1 = gate 未通过"语义范围内，不是新增退出码值，无需更新这些文档。
- 检查 `WORKFLOW.md:91` 唯一提及 CODE-MAP.md 的位置，只描述目录结构归属，不涉及路径解析算法，DEBT0016 的实现细节改动无需传播到此处。
- 检查 `agate/assets/templates/task-files.md`、`agate/assets/execution-roles/implementer.md` 均未提及「新增文件核对表」标题的正则/子串判定细节（只在 `task-files.md:437` 提 `code_map_new_files_count` 字段本身），DEBT0017 无需传播。
- 检查 `agate/scripts/ci-gate-backstop.py`：通过 `subprocess` 调用 `check-gate.py`（`ci-gate-backstop.py:24`），不 import 其内部函数，DEBT0016/17/18 的内部实现改动对其透明，无需同步。
- `agate-workspace/debt/tech-debt.md` 反向发现的越界模式（`check-retrospective.py:74`、`agate-render-dispatch-prompt.py:191` 同款 `dirname(dirname(...))` 路径算术）已按范围锁定原则登记为 DEBT0028，未静默遗漏；`check-gate.py:881` gate_p2 同款子串判定风险已登记为 DEBT0029。

**结论**：ALIGNED

### A4: 测试覆盖

直接相关 6 个测试文件实跑：
```
agate/tests/unit/test_agate_common.py
agate/tests/unit/test_install_offline.py
agate/tests/unit/test_agate_install_uninstall.py
agate/tests/unit/test_check_gate.py
agate/tests/unit/test_agate_pack_offline.py
agate/tests/regression/test_offline_bundle_roundtrip.py
→ 236 passed in 28.59s
```
全量回归实跑：
```
python3 -m pytest agate/tests/ -q
→ 1457 passed, 2 skipped in 154.41s (0:02:34), exit code 0
```
每条 DEBT 均有对应 BDD 编号测试（BDD-1/2＝DEBT0002，BDD-3＝DEBT0003，BDD-4/5＝DEBT0004，BDD-6＝DEBT0007 回归确认，BDD-8/9＝DEBT0016，BDD-10/11＝DEBT0017，BDD-12(4子用例)/13＝DEBT0018），边界场景（限流命中/未命中、非标准嵌套+`.agate.env` 覆盖、自指散文假阳性防护、标题尾缀文字、agate_common 缺失 fail-closed、正常路径回归守卫）均有覆盖。

**结论**：ALIGNED

### A5: 下游影响 + 文档传播

- 全量 pytest 1457 passed / 0 failed，无下游破坏性变更。
- `agate-workspace/debt/tech-debt.md` 7 条 closure 均含 `closed_at: 2026-09-04` + evidence（脚本引用 + 测试引用），DEBT0007 补了 `task_id: TAG0031`（原 `null`）。
- 越界发现未处理项已转登记为新 DEBT（DEBT0028/DEBT0029），不留白。
- `install-offline.py` 的 `verify_checksums` 新增 `RuntimeError` 分支，`main()`（约 L284-290）已同步捕获并 `return 1` + stderr 消息，未遗漏调用方处理。
- 未发现需要更新但未更新的下游文档。

**结论**：ALIGNED

### A6: 锚点表覆盖

`agate/scripts/check-protocol-consistency.py` CHECK 9 的 `SCRIPT_ALIGNMENT_ANCHORS`（L504 起）收录的是"文档声明的协议规则 → 脚本关键词"（如 `P2 不可裁剪`、`MAX_RETRY`、`PROD_TOUCHED`）。本次 7 条 DEBT 全部是脚本内部健壮性/去重修复，未新增任何协议文档声明的规则条文，故无需新增锚点。

**结论**：ALIGNED

### A7: 设计原则一致性

- **ADR-002（可判定性——gate 门槛机器可判定，`agate/adr.md:41-64`）**：DEBT0018 把 4 个关键读取器的降级行为从"静默 0/空→可能误判为 PASS"改为"fail-closed 显式 return 1"，直接强化 ADR-002 的核心主张（"gate 通过/不通过由脚本 exit code 决定，不能有静默的假通过"）。DEBT0016/0017 把路径算术/子串判定换成确定性更强的权威函数与整行正则，同样是在强化可判定性，方向一致。
- **ADR-011（引导型 CLI 工具的权限是早纠错，不是安全边界，`agate/adr.md:352-`）**：`install-offline.py` 的 `_ensure_agate_common` pyyaml 引导安装逻辑遵循"先校验 checksum 再 pip install，不可信不安装"，属于早纠错性质的健壮性设计，与 ADR-011 不冲突。
- 未发现需要补充新 ADR 的未记录架构决策。

**结论**：ALIGNED

## 附注（不计入 A1-A7 判定，仅记录知悉）

`agate-workspace/tasks/TAG0031-debt-cleanup/P4-implementation-version-mgmt.md:31` 存在一条 `[DESIGN_GAP:]`（P2-design.md §1.3 R1 未明确说明如何在"install-offline.py 顶层不能无条件 import agate_common"约束下满足 `test_offline_bundle_roundtrip.py` 的 identity 断言）。任务当前 `phase: P4`，尚无 `P7-consistency.md`。按审查角色原则 6：该 DESIGN_GAP 是任务内部实现方案的设计留白，已被"探测 yaml 可用性→可用才模块级暴露引用"的折中方案 + 12 个测试（含 identity 断言）验证自洽，不构成协议文档-脚本层面的 A1-A7 misalignment，留待 P7 consistency-reviewer 按常规流程复核即可，此处不升级为 MISALIGNED。
