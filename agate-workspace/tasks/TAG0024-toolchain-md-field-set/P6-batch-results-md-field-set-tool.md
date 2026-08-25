---
phase: P6
task_id: TAG0024
type: evidence-batch
batch: md-field-set-tool
parent: P1-requirements.md
trace_id: TAG0024-P6-md-field-set-tool-20260825
status: draft
created: 2026-08-25
agent: verifier
---

> 证据并行批次（不写最终 P6-acceptance.md）。覆盖 P1-requirements.md BDD-1~19（RM-AG0048 一期，
> `agate-md-field-set.py` / `agate-md-field-set-gate-commands.py`）。每条 BDD 均实跑
> `agate/tests/unit/test_agate_md_field_set.py` 对应测试函数（`--basetemp` 隔离 /tmp 只读约束），
> 单独输出保存为证据文件，供汇总 verifier 整合进唯一 P6-acceptance.md。

## 异常诊断说明（BDD-9）

首次用共享 `.pytest-tmp` basetemp 重跑时，`test_bdd_9_evidence_fields_rejected[deviation_critical_count]`
出现 1 次瞬时失败。排查发现 `.pytest-tmp` 内混有本任务其他并行 P6 证据批次
（check-gate-debt-fixes / phases-yaml-consistency）残留的 tmp_path 目录——多个 verifier subagent
同时对同一共享 basetemp 目录跑 pytest 存在 tmp_path 编号/GC 竞态，与 `agate-md-field-set.py`
实现本身无关。改用批次专属隔离 basetemp（`.pytest-tmp-md-field-set-tool`）重跑该测试函数全部
10 个参数化用例及单独失败用例本身，各 2 次均 100% 稳定 PASS（10 passed, EXIT:0）。`bdd-9.log`
已替换为该隔离重跑的干净输出。判定 PASS，过程详见 `P6-progress-md-field-set-tool.md`。

## BDD 逐条结果

- PASS BDD-1: 合法 key（`packages`）与合法 value 写入成功，`agate-md-field-get.py` 读回同值，`check-gate.py P2` 不再因该字段被阻断 (bdd-1.log)
- PASS BDD-2: 非法 key（`risks_level`）被拒绝，exit 非 0，输出含真实白名单成员 `risk_level` (bdd-2.log)
- PASS BDD-3: 合法 key 非法值（`status Approve`）被拒绝，输出含合法枚举 `approved`、字段归属角色、下一步建议 (bdd-3.log)
- PASS BDD-4: `agent: implementer`（非 review 角色）文件上写 `status approved` 被拒绝，输出提示字段归属角色 (bdd-4.log)
- PASS BDD-5: `--list` 输出包含 P2 阶段 phases.yaml 声明的全部 5 个 task_fields，与阶段 schema 一致 (bdd-5.log)
- PASS BDD-6: 写入 `candidate_count` 后输出含"剩余缺失"字段清单（而非仅报告写入成功） (bdd-6.log)
- PASS BDD-7: `agate-md-field-set-gate-commands.py` 写入合法 YAML 块 exit 0，`parse_gate_commands_block` 能正确解析写回文本，条目值与写入值一致 (bdd-7.log)
- PASS BDD-8: gate_commands 非法块（未声明阶段 key / 非法 `_timeout_seconds`）均被拒绝，exit 非 0，输出点名具体非法 key，文件保持写入前原样（2 个参数化用例） (bdd-8.log)
- PASS BDD-9: 10 个证据字段（9 个 `NO_FALLBACK_INT_FIELDS` + `regression_pass`）逐个 set 均被拒绝，exit 非 0，输出提示"该字段由验证脚本产出，不可手动填写"语义（隔离 basetemp 重跑，见上方异常诊断说明） (bdd-9.log)
- PASS BDD-10: monkeypatch `os.replace` 模拟写入中断后调用 `main()`，目标文件字节内容与写入前完全一致，未出现半成品 frontmatter (bdd-10.log)
- PASS BDD-11: FILE 指向不存在路径，exit 非 0，输出含"请先 Write 产出文件，再 set 字段"，且未创建该文件 (bdd-11.log)
- PASS BDD-12: 无 `---` frontmatter 块的文件写入字段后，新文件以 `---\n` 开头且以原正文全文结尾，正文逐字节保留 (bdd-12.log)
- PASS BDD-13: frontmatter 已存在、正文残留同名旧格式声明的文件上写入该 key，写入成功、输出含"残留"/"清理"提示、正文残留原样保留，get 读回值以 frontmatter 为准 (bdd-13.log)
- PASS BDD-14: 在真实 `P2-design.md` 基准文件上补齐最后一个必填字段后，`check-frontmatter.py` 校验 exit 0 (bdd-14.log)
- PASS BDD-15: 直接调用 `agate-frontmatter-check.py` 真实 `_check()` 取得期望错误列表，set CLI 的接受/拒绝结论与之一致，拒绝时 CLI 输出逐字包含 `_check()` 原始错误字符串（2 个参数化用例） (bdd-15.log)
- PASS BDD-16: 零协议知识模拟调用序列按 `--list` 输出逐项 set 直至无缺失，最终 `--list` 无剩余缺失且 `check-gate.py P2` 不再阻断 (bdd-16.log)
- PASS BDD-17: 白盒调用 `_writable_keys(rules_root)`，返回值等于 `GENERIC_HEADER_KEYS` ∪ 从真实 `phases.yaml` 动态计算的全部 `task_fields` 并集；`bump_type` 命中，虚构 key 不命中 (bdd-17.log)
- PASS BDD-18: 6 个追加/嵌套语义字段（`NO_FALLBACK_LIST_FIELDS` 5 个 + `dispatch_plan`）逐个 set 均被拒绝，exit 非 0，输出含"追加/嵌套/暂不支持"语义（6 个参数化用例） (bdd-18.log)
- PASS BDD-19: `dispatch-prompt.md`/`dispatch-context.md` 模板原文均提及 `agate-md-field-set`，旧的"直接复制 Header 代码围栏"字面指引已不存在 (bdd-19.log)

**Summary**: 19/19 PASS, 0 FAIL（35 个测试项全部通过，含 4 个参数化 BDD 共 16 个子用例）
