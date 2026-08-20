## 批次 fg1-doc-boundary（BDD-5/6/9文档半）

test_code_dir: `agate/tests`
测试代码文件: `agate/tests/unit/test_p2p4_boundary_docs.py`（5 个测试用例，文档内容断言型，当前全部红灯）

说明：BDD-5/6/9(文档半) 判据是"文档能否找到结论"，不是"新增 gate 脚本执行绑定"（P2-design.md §1.3 R1 / dispatch-context 上游关联节明确）。三条 BDD 共享同一批次是因为 P2-design.md「gate_commands 声明」节是 BDD-5 与 BDD-9 文档半的共同落点文件（避免被拆到两批、同一文件改两次）。

### BDD-5: env_constraints 声明性字段与 gate_commands 执行机制的语义边界已文档化

- **测试用例**：
  1. `test_bdd_5_p2_design_gate_commands_section_states_env_constraints_is_declarative` — 从 `agate/phase-cards/P2-design.md` 切出「## gate_commands 声明」节正文（到下一个 `## ` 标题为止），断言：① 节内出现 `env_constraints` 关键词；② 出现 "env_constraints ... 声明性"（或反序）措辞；③ 出现"执行机制/强制执行/不会被自动执行/不等价"类结论性表述
  2. `test_bdd_5_architect_role_states_env_constraints_is_declarative` — 从 `agate/assets/execution-roles/architect.md` 用正则切出以 `` - `env_constraints:` `` 开头到下一个同级字段列表项之间的段落，断言：① 含"声明性"字样；② 含 `gate_commands`/"执行机制"/"强制执行"/"不会被自动执行" 之一
- **预期行为**：P4 implementer 在两处文档新增边界说明文字后，两个断言均能匹配到对应段落
- **当前状态**：红灯。P2-design.md「gate_commands 声明」节当前只讲 `{key}_timeout_seconds` 字段规则，完全未提及 `env_constraints`；architect.md 的 `env_constraints:` 字段说明段落（约 L135-141）只讲"确认/细化 P0-brief 环境约束"，无"声明性"字样，也无与 `gate_commands` 执行边界的对照说明。实测两条测试均以 `AssertionError`（非语法/import 错误）失败，属真红灯

### BDD-6: UI 类任务的部署类执行性约束在 P4 后有显式检查提醒

- **测试用例**：
  1. `test_bdd_6_p4_implementation_self_check_section_has_dist_build_reminder` — 从 `agate/phase-cards/P4-implementation.md` 切出「## 自查≠gate」节正文，断言：① 含 "UI/前端/需构建" 类适用条件词；② 含 "dist/构建产物/打包产物" 类关键词；③ 含"确认…存在/已构建/应构建"类具体动作措辞
- **预期行为**：implementer 在该节新增"UI/需构建任务 P4 后应构建并确认 dist 类产物存在"提醒条目后，三项断言均能匹配
- **当前状态**：红灯。当前「自查≠gate」节（L50-53）内容只讲"自查通过 ≠ P5 gate 通过"与"不要声称 P5 已过"，未提及 UI/构建/dist 相关字眼，`AssertionError` 真实失败

### BDD-9（文档半）: `--strict` 不放 `&&` 链路中间的协议指引 + 反例

> 代码半（`check-protocol-consistency.py --strict-errors-only` 新增互斥模式 + 其单测）由 fg3-strict-mode-code 批次负责，不在本批次范围。

- **测试用例**：
  1. `test_bdd_9_p2_design_gate_commands_section_has_strict_anti_pattern_guidance` — 同一「## gate_commands 声明」节，断言：① 含 `--strict`；② 含 `&&`；③ 含"不要/避免/反模式/不放/不要放/短路"类显式指引措辞
  2. `test_bdd_9_p2_design_gate_commands_section_has_concrete_anti_pattern_example` — 同节，断言含形如 `--strict ... &&` 或 `&& ... --strict` 的具体反例命令串（不能只是抽象提醒没有示例）
- **预期行为**：implementer 在「gate_commands 声明」节新增 `--strict` 反模式指引段（含历史 TAG0004 等任务已踩过的 `&& ... --strict ... &&` 写法反例）后，两条断言均能匹配
- **当前状态**：红灯。当前节内容完全未出现 `--strict` 或 `&&` 字样（该节只讲 timeout_seconds 字段规则），两条测试均以 `AssertionError` 失败

### 自跑结果

```
$ python3 -m pytest agate/tests/unit/test_p2p4_boundary_docs.py -v
collected 5 items
... 5 failed
5 failed in 0.04s
```

5/5 全部因 `AssertionError`（断言的文字/段落未找到）失败，无 `SyntaxError`/`ImportError` 等假红灯来源，确认真红灯。
