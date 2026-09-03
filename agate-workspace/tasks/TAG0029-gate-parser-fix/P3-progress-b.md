# P3-progress-b.md — P3-B 批分阶段落盘（BDD-4~9，每用例一记）

## BDD-4（P3_xxx 不收集）已落盘 + 自跑确认红
- 测试：`test_tag0029_bdd_4_p3_aux_keys_not_collected`
- 自跑：FAILED 于 `assert not True`（suffix `_e2e` 条目被收集）——
  旧 `startswith("P3")` 语义，符合 dispatch 红因。非测试 bug（json 解析成功）。

## BDD-5（裸 P3 收集而元键豁免，锁定绿）已落盘 + 自跑确认绿
- 测试：`test_tag0029_bdd_5_bare_p3_collected_meta_exempt`
- 自跑：PASSED（旧语义下裸 P3 唯一收集 + 两元键被 `is_gate_meta_key` 豁免成立；
  P4 精确键后保持绿）。

## BDD-6（协议卡 P3_xxx 禁令，当前红）已落盘 + 自跑确认红
- 测试：`test_tag0029_bdd_6_protocol_card_bans_p3_aux_keys`
- 自跑：FAILED 于 `assert 'P3_' in section`（section 为 `## gate_commands 声明` 全节，
  无 P3_xxx 禁止声明）—— 符合"当前红，P4 才加禁令"的预期。非测试 bug
 （首轮曾锚到正文描述区，已修正为 `## gate_commands` 标题锚点，重跑仍红，真红）。


## BDD-7（fixture 数据面豁免，当前红）已落盘 + 自跑确认红
- 测试：`test_tag0029_bdd_7_fixture_data_exempt_zero_hits`
- fixture 对齐：tmp_path 内建 `agate/tests/fixtures/` 同名相对结构（P2 §3.4
  `_FIXTURE_EXEMPT_DIRS` 前缀语义；P4 实现须做 posix 归一化相对前缀判定，
  禁"含 fixture 字样"宽匹配）。
- 自跑：FAILED 于 `assert 1 == 0`（旧扫描器无豁免分支，R2 命中裸调用 → exit 1）——
  符合 dispatch 红因。非测试 bug（路径断言 `_EXEMPT_SEGMENT in posix_path` 先行通过）。

## BDD-8（目录外裸调用仍拦截，锁定绿）已落盘 + 自跑确认绿
- 测试：`test_tag0029_bdd_8_bare_call_outside_fixture_still_hit`
- 自跑：PASSED（旧 R2 本体即命中命令位置裸调用，exit 1 + 输出含 R2 与路径）。

## BDD-9（本任务 P2 三 scanner key，锁定绿）已落盘 + 自跑确认绿
- 测试：`test_tag0029_bdd_9_task_p2_declares_scanner_keys`
- 自跑：PASSED（§4 的 P3_scanner/P4_scanner 经公共库块解析真实命中，
  值含 check-platform-assumptions）。

## B 批干净契约已验证
- 旧扫描器扫 B 批测试文件 0 命中（exit 0）；首跑 3 红 3 绿分布符合预期
  （红：BDD-4/BDD-6/BDD-7；绿：BDD-5/BDD-8/BDD-9）。
- [PROD_NOT_TOUCHED] 只写 B 批测试 + progress-b，未改实现代码，未动 A 批文件。
