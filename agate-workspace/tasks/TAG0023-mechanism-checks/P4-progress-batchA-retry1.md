# P4-progress-batchA-retry1

## 步骤1: 读取角色文件 + dispatch-context
- 已读 implementer.md 角色定义
- 已读 P4-dispatch-context-implementer-batchA-retry1.md 全文
- 4 条 CRITICAL：CRITICAL1(BDD-2 守卫范围决策-方案A) / CRITICAL2(UnicodeDecodeError) / CRITICAL3(_scan_bdd1_review_retry_phase 只返回首个匹配) / CRITICAL4(progress-batchX 命名漏扫)

## 步骤2: 读 P4-review.md + P1-requirements.md BDD-2 + 当前实现代码
- P4-review.md 4 条 CRITICAL 论证已通读，均已用真实数据核实（P5→P4/task_dir结构/roadmap等）
- P1-requirements.md BDD-2 原文: Given 只要求 "retries[P4]为空"，无"此前必须已有记录"前提 -> 确认方案A字面满足
- check-state-transition.py 当前实现已读全文（334行）
- test_check_state_transition.py 已读 archive 系列(L335-425) + BDD 系列(L495-713)
- 静态分析预测（去掉守卫后）：test_st_archive_1/2/3/6 会被 BDD-2 意外短路（HEAD/staged retries 皆为{}，0<=0 触发 exit1，消息与断言不符）；test_st_archive_4(P4->P5 forward, old_num<new_num) 和 archive_5(P1->P0, new_num=0) 不受影响。以实测为准，下一步先应用 CRITICAL1 代码修复再跑 pytest -k archive 验证。

## 步骤3: 实测验证 -k archive（去掉守卫后）
- 应用 CRITICAL1 代码修复（去掉 old_retries_len>0 守卫）后跑 `pytest -k archive`：
  4 failed（archive_1/2/3/6），2 passed（archive_4/5） —— 与 dispatch-context 建议一致（非盲抄，已实测）
- 修复 archive_1/2/3/6 的 fixture（给暂存版本的 new_phase 补 1 条 retries，HEAD 侧保持默认空，
  使 new_retries_len(1) > old_retries_len(0)，BDD-2 不再短路，测试回归走到原有 check4 逻辑）
- 重跑 -k archive：6 passed，确认修复生效

## 步骤4: CRITICAL2/3/4 机械修复
- CRITICAL2: `_load_current_state_yaml` open() 加 errors="replace"（对齐 _scan_bdd3_keyword_phases 风格）
- CRITICAL3: `_scan_bdd1_review_retry_phase` 返回类型 Optional[str] -> set[str]，收集全部命中；
  调用处（BDD-1 分支）改为 for 循环逐阶段检查（对齐 BDD-3 分支写法）
- CRITICAL4: `rest.startswith("progress.md")` -> `rest.startswith("progress")`

## 步骤5: 新增 4 条回归用例
- CRITICAL1: test_bdd_2_first_time_retreat_both_sides_empty_retries_exit_1（HEAD/暂存 retries 皆空，首次单步回退，exit 1）
- CRITICAL2: test_load_current_state_yaml_invalid_utf8_no_crash（直接单测内部函数，importlib spec_from_file_location 加载，
  因为端到端 CLI 路径下 agate-state-get.py 子进程会先于本函数在同一非法字节上崩溃并被 rc!=0 分支吞掉，
  导致 main() 提前 exit 0，无法通过 CLI 路径复现该函数本身的崩溃缺陷）
- CRITICAL3: test_bdd_1_multiple_phase_hits_all_warned（P1+P2 两个评审重试文件同时存在，两个 WARNING 都触发）
- CRITICAL4: test_bdd_3_progress_batch_named_file_detected（P4-progress-batchA.md 命中关键词场景）

## 步骤6: 验证结果
- `pytest agate/tests/unit/test_check_state_transition.py -q`: 44 passed，全绿无回归
- `ruff check agate/scripts/check-state-transition.py`: All checks passed
- `ruff check agate/tests/unit/test_check_state_transition.py`: All checks passed
- 边界核查：git status 确认本轮只改了 check-state-transition.py + test_check_state_transition.py 两个文件，
  未 touch batch B/C/D 涉及的任何文件

[PROD_NOT_TOUCHED]

## 完成
4 条 CRITICAL 全部修复（含代码修复 + 至少各 1 条新回归用例），既有 archive_1/2/3/6 fixture 已按方案 A 连带修复
且保持原断言语义。
