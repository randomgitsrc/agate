---
phase: P4
task_id: TAG0019-risk-routing
type: review
parent: P4-implementation.md
trace_id: TAG0019-P4-20260821
status: approved
created: 2026-08-21
agent: review
---

# P4 实现评审（专家组组长汇总·终裁）— TAG0019 风险分路由

> 组长角色（review 担任专家组组长）：只汇总不发表新意见。**本轮为终裁（⑩迭代第 4 轮）**。
> 评审历程：① rejected（C1-C3 CRITICAL + F1/F2 MEDIUM）→ implementer 修复 → ② rejected（仅 F2 词界净回退）→ implementer 定向修复 → ③ **终裁 approved**。各轮逐项细节见 P4-review-eng.md / P4-review-cso.md 与 P4-progress.md。

## 1. 两位专家终裁表

| 输入文件 | 域 / 角色 | 终裁专家结论 | 说明 |
|---------|----------|-------------|------|
| P4-review-eng.md | backend / review | **approved** | C1 / C2 / C3 / F2 / F1 复核通过，全量复评通过 |
| P4-review-cso.md | security / cso | **approved** | F2 定向重审闭环：must-high 31/31、must-low 8/8、fail-closed 主链无回归、F1 artifact 跳过通过 |
| P4-review.md（本文件） | 组长汇总 / review | **approved** | 组长规则：全票无 BLOCKER → approved |

**组长规则判定：两位专家均 approved，全票无 BLOCKER ⇒ 汇总结论 approved。**

**专家组分歧检查：无。** 三轮接力（eng 管实现落地、cso 管安全语义关闭）均收敛一致，无交人工项。

## 2. 汇总已验证清单（终裁，均通过）

- **C1-C3 CRITICAL 全修**：
  - C1 ceremony 移入 NO_FALLBACK_STRING_FIELDS + 正文散文不误判回归（prose 误读 → check-routing exit 0，端到端实测）
  - C2 两新测试文件注释去除字面 /tmp（P5_platform 变更文件集扫描 0 命中，exit 0）
  - C3 三测试交付物补齐：test_check_frontmatter ceremony enums（cf_15）、test_agate_md_field_get ceremony 读取（mdf_18-20）、test_pre_commit_hook 2j.1 挂载链（it10）
- **F1/F2 MEDIUM 全修**：
  - F1 影响面扫描对任务文档 artifact 跳过（_is_task_artifact：P[0-8]-*.md + agate-workspace/tasks/**；代码模块判据未削弱，探针实证）
  - F2 敏感关键词集扩充 + 匹配形态修正（左锚 + 词干 + \w* 尾随 / 显式形态）：must-high 31/31、must-low 8/8（secrets/credentials/api_key/auth_keys/authorization 等复数/拼接/词干形态均判 high）
- **fail-closed 主链**：git_ok:false→exit 1、thin 薄于算分→exit 1、非法值→exit 1、_run_script_rc 缺失→1、未捕获异常默认 exit 1——无回归
- **importlib 复用**：check-routing 复用 check-pruning（_md_field/_read_p1/_staged_source_count）+ agate-risk-score score_task，无 subprocess、无第二份实现；chenck-pruning 零改动
- **平台无关**：git 全经 run_git、relpath 归一、无裸解释器/硬编码 PATH/字面 /tmp（脚本本体）
- **注册点**：frontmatter-check（migrated_keys/enums/types，非 required → R7 向后兼容）、md-field-get STRING_FIELDS、pre-commit-gate 2j.1 挂载——三节点同步到位
- **零回归**：unit / integration / 回归测试全绿（唯一例外 I1 环境前提，见 §3）

## 3. 遗留非阻断项（记录，不阻塞 approved）

- **I1（移交 P5）**：test_bdd_7 非 git 上下文环境前提（basetemp 位置敏感）——由主 Agent 在 P5 落实可写且位于 git 仓库外的 pytest basetemp 后验证，P4 不阻塞。
- **F4（LOW，主 Agent 决定）**：影响面扫描性能（全仓逐文件扫描无二进制/大小上限），大仓可感知延迟，后续优化项。
- **F6（LOW，建议扩展）**：ci-gate-backstop 只重跑 check-gate、不含 check-routing（--no-verify 绕过面，与 check-pruning 同为既有模型缺口），后续扩展复检，不阻塞。

## 4. 终裁结论

**Header status: approved。** P4 实现评审通过，主 Agent 可推进 P5（P5 前置：落实 I1 basetemp；照常重跑 P3 全量 + P5_platform + P5_consistency）。