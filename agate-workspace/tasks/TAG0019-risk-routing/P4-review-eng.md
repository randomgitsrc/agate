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

# P4 实现复审（③轮，backend 域，role: review）——TAG0019 风险分路由 core 批

复审依据：P4-dispatch-context-review-eng-rev2.md（增量模式，⑩迭代第 3 轮）。
范围：确认上轮 rejected 的 C1-C3（CRITICAL）+ F1/F2（MEDIUM，cso 侧）修复到位 + 全量复评防回归。

**Status: approved**。上轮全部拒绝项已修复并经独立复核（代码审 + 实测 + 手工场景），
无新发现问题；遗留 1 项环境前提（I1）不属代码缺陷，移交 P5 处理（见下）。

## 修复复核（每项含独立验证证据）

| 上轮项 | 修复声明 | 独立复核证据 | 结论 |
|--------|---------|-------------|------|
| C1 md-field-get ceremony 回退误读 | ceremony 移入 NO_FALLBACK_STRING_FIELDS，删 _regex_fallback 分支 | 代码审：`agate-md-field-get.py:87` 入 `NO_FALLBACK_STRING_FIELDS`（与 change_type 同集）、`:125-127` STRING_FIELDS 移除、grep 全文无 `_regex_fallback` ceremony 分支；回归测试 `test_c1_ceremony_prose_in_body_not_misread_exit_0`（test_check_routing.py:245-259，fixture 与上轮实证场景同构）随 60 passed 通过；手工端到端：frontmatter 无 ceremony + 正文 "按 ceremony: thin 的 checklist 逐项确认" → **exit 0**（上轮同场景 exit 1） | ✅ 修复 |
| C2 平台扫描 R4 命中测试注释 | 两测试头去字面 /tmp | `check-platform-assumptions.py` 对 P2 §4 P5_platform 全 7 文件扫描 **exit 0 / 0 命中**（实测） | ✅ 修复 |
| C3 三测试交付物缺失 | 补齐三文件用例 | `test_check_frontmatter.py:372` `test_cf_15_bdd_6_ceremony_invalid_enum_rejected`（ceremony: light → exit 1）；`test_agate_md_field_get.py:195-231` `test_mdf_18/19/20`（frontmatter 读出 / 无声明空 / 散文不误判）；`test_pre_commit_hook.py:1495+` 2j.1 挂载链集成用例。三文件随测试全绿（unit 60 passed；integration 55 passed 含 it10） | ✅ 修复 |
| F2 敏感关键词过窄/子串误标 | 关键词扩充 + 词界化 | 代码审：`agate-risk-score.py:65-70` `\b(?:login|password|passwd|session|cookie|jwt|oauth|tls|ssl|crypto|encrypt|decrypt|vault|rbac|acl|pii|privacy|2fa|otp|csrf|xss|security|permission|secret|credential|network|socket|auth|token|api|net)\b` + `data[-_](model|schema)`。手工实证：`src/AUTHORS.md` 单独 staged → sensitive **low**（cso F3 auth 子串回归）；`src/capital_flow.py` → **low**（api 子串回归）；`src/auth/login.py` → **high** + domain security（真阳性保留） | ✅ 修复 |
| F1 impact 假阳性致 thin 不可达 | 跳过任务产出文档 | 代码审：`agate-risk-score.py:122-133` `_is_task_artifact`（P[0-8]-*.md basename + `agate-workspace/tasks/**` 前缀），`:147` 计入 F 候选排除；GIT_DIR 破坏场景下仍正确输出 git_ok:false | ✅ 修复 |

## 全量复评（防修复引入新问题）

- **fail-closed 主链**：`check-routing.py` 未在修复轮改动（git status 佐证）；thin 缺要素 exit 1 / 不声明 exit 0 / 声明薄于算分 exit 1 / 更保守 exit 0 / P1 缺失 exit 2 分支由 test_check_routing 全用例覆盖并通过；手工重验 GIT_DIR=/nonexistent（git 通道破坏）→ **exit 1**（git_ok:false fail-closed，修复后仍正确）。
- **importlib 复用**：`check-routing.py:56-63` 复用 check-pruning `_md_field/_read_p1/_staged_source_count` + `score_task` 无第二份实现（未改动）；check-pruning.py **零改动**（git status 无 M）。
- **注册点**：frontmatter-check ceremony（migrated_keys/enums/types，非 required）、pre-commit-gate 2j.1（`:341-343`）、md-field-get NO_FALLBACK（`:87`）、agate-summary `_DRIFT_SCRIPTS`（`:47`）全部在位，随测试绿。
- **平台无关**：变更文件集（2 脚本 + 5 测试文件）platform 扫描 0 命中 exit 0。
- **零回归**：`test_check_pruning.py`（29）+ regression 2 文件 + `test_docs_assertions.py` 合计 **38 passed**；integration `test_pre_commit_hook.py` **55 passed**；相关 unit 4 文件 **60 passed / 1 failed**（failed 即下述 I1 环境前提）。

## 遗留（非阻塞，移交 P5 / 主 Agent）

1. **I1（环境前提）**：`test_bdd_7_thin_score_anomaly_git_ok_false_exit_1` 依赖 pytest basetemp 位于任意 git 仓库之外——本 DSH 沙箱可写路径均在仓库内，该用例在本环境必翻转（实测 0≠1）；其代码分支（git 通道不可用 → git_ok:false → thin exit 1）已两次手工验证正确。P5 须落实**可写且位于 git 仓库外**的 basetemp（P2 §4 指定路径 `/home/kity/oclab/dsh-workspace/ptmp` 在本沙箱只读不可写，实测 Errno 30），再跑该用例。
2. I2-I5（上轮 INFORMATIONAL：impact 扫描性能 / 判据字面复制漂移风险 / `_staged_source_count` cwd 语义）维持上轮记录，不阻断，由主 Agent 决定是否建 DEBT。

## 后续动作

- 主 Agent：P4 commit 推进（phase=P4）+ P5 派发（verifier 执行 gate_commands，basetemp 按 I1 落实）；anomaly 用例以非 git basetemp 验证。
- 组长：P4-review.md 汇总本文件 approved 后定稿；eng 与 cso（F1/F2 修复）结论一致时可放行。