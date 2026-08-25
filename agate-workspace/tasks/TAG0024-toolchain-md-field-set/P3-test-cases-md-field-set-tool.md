---
phase: P3
task_id: TAG0024
type: test-cases
parent: P2-design.md
trace_id: TAG0024-P3-md-field-set-tool-20260825
status: draft
created: 2026-08-25
agent: test-designer
---

> 批次范围：`md-field-set-tool`（P2-design.md dispatch_plan 第 1 批）。覆盖 P1-requirements.md
> BDD-1~19（RM-AG0048 一期：`agate-md-field-set.py` / `agate-md-field-set-gate-commands.py`）。
> 测试代码：`agate/tests/unit/test_agate_md_field_set.py`（本批次产出；`test_code_dir` 字段
> 由主 Agent 合并三批次说明为统一 P3-test-cases.md 时统一声明，本文件不重复声明）。
>
> 红灯确认：`python3 -m pytest agate/tests/unit/test_agate_md_field_set.py --basetemp=.pytest-tmp
> -p no:cacheprovider -v` 当前 35/35 用例（19 条 BDD，其中 BDD-8/9/15/18 为参数化）全部失败——
> CLI 用例因 `agate-md-field-set.py` / `agate-md-field-set-gate-commands.py` 尚不存在
> （subprocess 报 "can't open file"，非 0 退出）；白盒用例（BDD-10/15/17）因
> `importlib.util.spec_from_file_location(...).loader.exec_module` 阶段抛 `FileNotFoundError`
> 而失败。均为 B 类真红灯（被测模块未实现），无 SyntaxError 等 A 类假红灯。

## 测试用例清单（BDD → 测试函数 → 断言点）

- **BDD-1** `test_bdd_1_valid_key_value_roundtrip_and_gate_pass`：在已具备其余三个 P2 必填字段的
  `P2-design.md` 上 set `packages`，断言写入 exit 0、`agate-md-field-get.py` 读回同值、
  `check-gate.py P2` 不再因缺字段被阻断（returncode != 1）。
- **BDD-2** `test_bdd_2_invalid_key_rejected_lists_valid_keys`：set 一个不在白名单的 key
  （`risks_level` 拼写变体），断言 exit 非 0 且输出中出现真实白名单成员 `risk_level`。
- **BDD-3** `test_bdd_3_invalid_value_rejected_with_enum_role_and_suggestion`：对 `P2-review.md`
  set `status Approve`（大小写非法值），断言 exit 非 0，输出同时含合法枚举（`approved`）、
  字段归属角色提示、下一步建议关键词。
- **BDD-4** `test_bdd_4_role_unauthorized_write_rejected`：`agent: implementer`（execution-roles，
  非 review 角色）的 `P4-review.md` 上 set `status approved`，断言 exit 非 0 且提示角色归属。
- **BDD-5** `test_bdd_5_list_matches_phase_task_fields`：对 P2 阶段文件跑 `--list`，断言 exit 0
  且输出包含 phases.yaml `id:P2` 声明的全部 5 个 task_fields。
- **BDD-6** `test_bdd_6_reports_remaining_missing_after_write`：在全空 `P2-design.md` 上 set
  `candidate_count`，断言写入成功后输出含"缺失"字样，且其余 4 个字段名均出现在剩余缺失报告中。
- **BDD-7** `test_bdd_7_gate_commands_block_write_and_parse`：`agate-md-field-set-gate-commands.py`
  写入合法 flow-style YAML 块，断言 exit 0，且用 `agate_common.parse_gate_commands_block` 对
  写回文本重新解析，条目值与写入值一致。
- **BDD-8** `test_bdd_8_gate_commands_invalid_block_rejected`（参数化 2 例：未声明阶段 key
  `P9_custom` / 非法 `_timeout_seconds` 值 `"abc"`）：断言 exit 非 0、输出点名具体非法 key、
  文件内容保持写入前原样（拒绝时不落盘）。
- **BDD-9** `test_bdd_9_evidence_fields_rejected`（参数化 10 例，覆盖 9 个 `NO_FALLBACK_INT_FIELDS`
  + `regression_pass`）：逐个证据字段 set，断言 exit 非 0 且提示"该字段由验证脚本产出，不可
  手动填写"语义。
- **BDD-10** `test_bdd_10_atomic_write_interrupted_leaves_file_unchanged`：白盒加载
  `agate-md-field-set.py`，monkeypatch `mod.os.replace` 抛异常后调用 `mod.main()`，断言
  非零/非 None 退出码，且目标文件字节内容与写入前完全一致（模拟"写入中途中断"）。
- **BDD-11** `test_bdd_11_missing_file_rejected`：FILE 指向不存在路径，断言 exit 非 0，输出
  含"请先 Write 产出文件，再 set 字段"，且未创建该文件。
- **BDD-12** `test_bdd_12_inserts_frontmatter_preserves_body`：对无 `---` 块的旧格式文件 set
  字段，断言 exit 0，新文件以 `---\n` 开头且以原正文全文结尾（原正文逐字节保留）。
- **BDD-13** `test_bdd_13_residual_body_field_warns_but_not_deleted`：frontmatter 已存在、正文
  残留同名旧格式声明的文件上 set 该 key，断言写入成功、输出含"残留"/"清理"提示、正文残留
  原样保留（未被删除）、且 get 读回值以 frontmatter 为准。
- **BDD-14** `test_bdd_14_generated_frontmatter_passes_check_frontmatter`：在真实 SCHEMAS
  基准文件名 `P2-design.md` 上补齐最后一个必填字段后，跑 `check-frontmatter.py`，断言 exit 0。
- **BDD-15** `test_bdd_15_value_validation_same_source_as_check`（参数化 2 例：`candidate_count=0`
  非法 / `=2` 合法）：直接调用 `agate-frontmatter-check.py` 的真实 `_check()` 取得期望错误列表
  （非硬编码两份期望值），断言 set CLI 的接受/拒绝结论与之一致，且拒绝时 CLI 输出**逐字包含**
  `_check()` 返回的原始错误字符串——防止 set 与 gate 两边独立漂移仍分别通过各自硬编码测试。
- **BDD-16** `test_bdd_16_zero_protocol_knowledge_walkthrough_converges`：不依赖 `--list` 具体
  排版做解析驱动（排版是 P4 实现细节），按 BDD-5 已锁定的 P2 task_fields 名单逐项 set +
  gate-commands 子命令补 `gate_commands` 块后，断言最终 `--list` 无"剩余缺失"字样且
  `check-gate.py P2` 不再阻断——验证"自描述输出足以引导零协议知识调用方填对"。
- **BDD-17** `test_bdd_17_writable_keys_is_mechanical_union`：白盒调用 `_writable_keys(rules_root)`，
  断言其返回值等于"实现自身声明的 `GENERIC_HEADER_KEYS` ∪ 从真实 `phases.yaml` 动态计算的全部
  `task_fields` 并集"（并集从 YAML 现读，非测试代码抄一份子集）；边界断言：`bump_type`
  （P8 task_fields 成员）命中，`totally_bogus_key_xyz_not_in_any_schema` 不命中。
- **BDD-18** `test_bdd_18_append_only_fields_rejected`（参数化 6 例，覆盖 `NO_FALLBACK_LIST_FIELDS`
  5 个 + `JSON_FIELDS` 的 `dispatch_plan`）：逐个 set，断言 exit 非 0 且提示含"追加/嵌套/暂不
  支持"语义。
- **BDD-19** `test_bdd_19_dispatch_templates_reference_set_tool_no_copyable_fence`：读取
  `dispatch-prompt.md`/`dispatch-context.md` 模板原文，断言均提及 `agate-md-field-set`，且
  旧的"文件必须以这段 Header 开头（直接复制"字面指引已不存在（当前仍存在，为本条真红灯来源，
  与新脚本是否实现无关，属静态内容断言）。

## 覆盖率自检

- BDD-1~19 共 19 条，均有至少一个对应测试函数（19 个函数，其中 4 个含 `@pytest.mark.parametrize`
  展开为多个 case，总计 35 个测试项），1:1 映射，无遗漏。
- dispatch-context 三项强制设计要求均已落地：BDD-15 同源铁律用真实 `_check()` 返回值驱动断言
  （非双份硬编码）；BDD-16 零协议知识场景已构造（且刻意不依赖 `--list` 排版细节，降低对
  P4 未定实现格式的耦合）；BDD-10 原子写用 monkeypatch `os.replace` 模拟中途中断。
- BDD-17 边界覆盖：白名单命中（`bump_type`）与不命中（虚构 key）均已断言。
