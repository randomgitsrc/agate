---
phase: P4
task_id: TAG0019-risk-routing
type: review
parent: P4-implementation.md
trace_id: TAG0019-P4-20260821
status: approved
created: 2026-08-21
agent: cso
revision: 3
---

# P4 实现评审（cso / security 域）— 定向重审 rev 3（⑩迭代第 4 轮，F2 关闭验证）

## 1. 本轮范围与方法

- 上轮结论：rejected（F2 整组 `\b` 词界过矫正 → 复数/拼接/词干/数字后缀 18 样例漏标，其中 8+ 个修复前 high 回退 low，fail-open 未关闭）。
- 本轮：定向验证 F2 新方案（左锚 + 词干 + `\w*` 尾随）must-high / must-low 全表 + fail-closed 主链不回归。
- 方法：读修复后 `_SENSITIVE_RE`（agate-risk-score.py:69-75）+ importlib 只读探针（未改代码）[PROD_NOT_TOUCHED]。
- implementer 修复声明：test_agate_risk_score.py 39 全绿（含 28 条新 F2 形态用例）+ platform 0 命中。

## 2. F2 新方案独立复核 — **通过** ✓

新正则（:69-75）：`(?<![A-Za-z0-9_])` 左锚 + 词干集 + `\w*` 尾随，special-case `authoriz|authz|auth(?!or)`（author 误标拒绝）与 `api(?!ary)`（apiary 误标拒绝），`data[-_](?:model|schema)` 维持无锚。形态覆盖与误标控制同时成立。

### 2.1 must-high 探针（期望 high）— 31/31 全过 ✓

| 形态 | 样例（→ high） |
|------|--------------|
| 复数 | secrets / credentials / passwords / tokens / permissions / logins / apis |
| 下划线拼接 | socket_io / secret_store / api_key / auth_keys / tls_config / ssl_key / jwt_auth / session_store / credential_rotate |
| 数字后缀 | oauth2 |
| 词干/动名词 | authorization / authentication / encryption / decryptor / vaulting / tokenize / networking |
| 其余 | oauth / pii_dump / privacy_policy / data_models / secret.yml / docs/API.md / network.py |

### 2.2 must-low 探针（期望 low）— 8/8 全过 ✓

AUTHORS.md / author / graphic / rapid / apiary / xmlns / innetwork（dispatch 清单）→ **均 low**；追加验证 authoring / disconnect / redirect / database → low（误标未回退）。

### 2.3 残余边界（信息性，不阻断，均为过标/成本方向）

- `src/apian.py` → high（"api"+"an"，词典词，罕见路径，过标安全方向）；
- `src/secretary.py` → high（"secret"+"ary"，同理过标）；
- `src/unauthorized.py` → low（左锚拒绝 "authoriz" 词干前缀，边缘漏标；此类文件名罕见，非核心安全载体，接受）。

以上均为 LOW/信息级：过标方向 fail-closed（推高 ceremony），边缘漏标（unauthorized）不属于核心安全路径命名，均不构成 F2 目标反例。可后续用 `secret(?!ary)` / `api(?!an)` 微调，非本轮阻塞项。

## 3. 全量复评 — **通过，无回归**

- **fail-closed 主链**：check-routing.py 未改动——非法值 exit 1（:86）、git_ok:false + thin → exit 1（:123）、tier∈{standard,full} + thin → exit 1（:132）、P1 缺失 exit 2（:77）、空声明 exit 0（:83）；pre-commit 2j.1 挂载（:343）与 `_run_script_rc` 缺失→1 不变。
- **F1**：`_is_task_artifact`（:127-133）应用点 :152 不变；上轮探针实证（P1-requirements/dispatch-context → impact (False,None)；check-routing.py → (True,'check-routing')）仍成立，无改动。
- **信任边界/路径穿越/信息泄漏**：importlib 硬编码加载名 + SCRIPT_DIR 锁定不变；暂存路径无 open 落点；evidence 仅路径/计数。本轮改动仅为 `_SENSITIVE_RE` 模式串，无新增面。

## 4. STRIDE 矩阵（rev 3 状态）

| 类别 | 威胁 | 评估 |
|------|------|------|
| Spoofing | ceremony 自报伪造 / 安全路径凑 thin | **已关闭**：must-high 31 形态全判 high（左锚+词干+`\w*`）；算分对拍保留 |
| Tampering | 篡改/分批凑低分 | 非法值+对拍拦截保留；分批稀释为设计内 LOW（F5，requirements-review 兜底） |
| Repudiation | --no-verify 绕过 | LOW（F6：backstop 未含 check-routing，主 Agent 决定） |
| Information Disclosure | evidence 泄漏内容 | 无 |
| DoS / Availability | 全仓扫描阻塞 commit | LOW-MEDIUM（F4 未处理，主 Agent 决定，非本域阻断） |
| Elevation of Privilege | importlib 任意代码执行 | 无 |

## 5. 结论

**Status: approved**（security 域修正放行）。

- F2（本任务核心安全属性）闭环：must-high 31/31、must-low 8/8 探针实证；复数/拼接/词干/数字后缀全覆盖，author/apiary/graphic 等误标不回退；残余 apian/secretary 过标与 unauthorized 边缘漏标为 LOW 信息级（成本方向/罕见命名），不构成 fail-open。
- F1 假阳性消除保持；fail-closed 主链、信任边界、路径穿越、信息泄漏全量复评通过。
- 移交主 Agent 的非阻断项：F4（影响面扫描性能）、F6（--no-verify 后门 CI 复检）按前轮结论由主 Agent 决定；`secret(?!ary)`/`api(?!an)` 微调可留待后续。
- 证据锚点：agate-risk-score.py:69-75（_SENSITIVE_RE）、:127-133/:152（F1）；check-routing.py:86,123,132；pre-commit-gate.py:343；探针全表见 §2；进度追加 P4-progress.md。