# v0.21.0 — 协议自维护基础设施补丁

> 日期：2026-07-24
> 基线：main @ 9526f67（v0.20.0 已合并）
> 动机：历次评审积累的搁置项，经合理性审查后筛选出必要项

---

## 0. 合理性审查结论

原始 9 项经逐项审查，3 项 DROP、4 项 DOWNGRADE、2 项 KEEP：

| ID | 内容 | 审查结论 | 理由 |
|----|------|----------|------|
| P2.24 | ADR-007 BDD 格式标准化 | **DOWNGRADE** | 决策已落地且由 3 个脚本强制执行，ADR 是事后记录非前瞻决策指南。低优先级文档完整性 |
| P2.25 | P0-brief 补 change_nature 字段 | **DROP** | 类别错误：change_nature 是进入 agate 前的分流决策（ADR-005），不是 P0-brief 字段。P0-brief 已通过 pruning_tendency/phase_hint 捕获其下游影响。加此字段会混淆时序并增加 agent 负担 |
| P2.26 | P0 卡片导航措辞统一 | **DROP** | P0 是入口点（无前置阶段卡片、无 subagent、无 gate），结构上与 P1-P8 不同。措辞差异反映结构差异，非疏漏。无混淆证据 |
| P2.27 | python3 环境变量可覆盖 | **DOWNGRADE** | 零真实报告。8 脚本改动 + 文档 + 测试的维护成本，对应一个未发生的问题。用户遇到时 symlink 即可解决 |
| P2.28 | VERSION_TAG_PREFIX 测试 | **DROP** | 一行 bash 默认值 `${VERSION_TAG_PREFIX:-v}`，逻辑复杂度近零，测试基础设施成本远超 bug 风险 |
| P2.29 | LIMITATIONS↔ADR 交叉引用 | **KEEP** | 低成本（每条局限加 1-2 个引用）、高价值导航辅助。局限描述症状，ADR 描述架构根因，交叉引用连接二者 |
| P2.30 | 反向传播表补 BDD 传播路径 | **KEEP** | 真实缺口：BDD 格式是横切关注点（6+ 文件跨 3 类），无显式传播路径时评审员易遗漏下游文件。v0.20.0 实施经验证实此风险 |
| P2.31 | check-retrospective.sh 排除 | **DOWNGRADE** | 真实不一致（T060 评审已识别），但影响低（exit 0 永不阻断）。一致性论证有效但不紧急 |
| P2.32 | gate 错误消息列文件名 | **DOWNGRADE** | 计数已足够诊断（文件在已知目录可手动检查），加文件名是 UX 改进非 bug 修复。无用户报告 |

### 顺便修复策略

DOWNGRADE 项中，P2.31 和 P2.32 改动极小（各 2-3 行），且与 KEEP 项无文件冲突。既然本次要跑全量测试 + self-gate review，顺便修掉比单独开版本更高效。P2.24 和 P2.27 改动面大（8 脚本 / ADR 撰写），留待有真实需求时再做。

### 最终范围

| 类型 | ID | 内容 |
|------|----|------|
| KEEP | P2.29 | LIMITATIONS.md 交叉引用 ADR |
| KEEP | P2.30 | 反向传播表补 BDD 传播路径 |
| 顺便 | P2.31 | check-retrospective.sh 排除 dispatch-context + AGATE_CARD |
| 顺便 | P2.32 | check-p6-evidence.sh 错误消息列具体文件名 |

---

## 1. P2.29：LIMITATIONS.md 交叉引用 ADR

### 问题

LIMITATIONS.md 8 条局限与 adr.md 6 条 ADR 有语义对应，但无交叉引用。读者从局限描述无法追溯到架构决策根因。

### 对应关系

| 局限 | ADR | 关系 |
|------|-----|------|
| 局限 1（gate 可信度上限） | ADR-002 | ADR-002 定义 gate 机器可判定，局限 1 说明机器可判定 ≠ 正确 |
| 局限 2（同源模型盲区） | ADR-006 | ADR-006 定义双层角色隔离，局限 2 说明同源模型下隔离是认知层非真正独立 |
| 局限 3（主 Agent 单点故障） | ADR-001, ADR-005 | ADR-001 隔离性是局限 3 的根因（主 Agent 不写产出但握有最终裁量权）；ADR-005 改动性质判断是主 Agent 裁量权的典型场景 |
| 局限 5（协议文档一致性） | ADR-002 | ADR-002 的 exit code 可判定性不覆盖协议文档自身的一致性 |
| 局限 6（运行时依赖） | ADR-003 | ADR-003 不绑定技术栈，但 agate 自身运行时依赖 bash+git+python3 |

局限 4（subagent 不可观测）和局限 7/8 无直接 ADR 对应——它们是平台/基础设施限制，非架构决策后果。

### 修改

`agate/LIMITATIONS.md`，每条局限末尾加一行引用（如有对应）：

- 局限 1 末尾加 `→ ADR-002（可判定性的边界）`
- 局限 2 末尾加 `→ ADR-006（双层角色的认知隔离上限）`
- 局限 3 末尾加 `→ ADR-001（隔离性不约束主 Agent 裁量权）、ADR-005（改动性质判断依赖主 Agent）`
- 局限 5 末尾加 `→ ADR-002（可判定性不覆盖协议文档自身）`
- 局限 6 末尾加 `→ ADR-003（不绑定被管理项目技术栈，但 agate 自身有运行时依赖）`

格式：在每条局限的"现状"段末尾追加一行，以 `→ ADR-NNN（一句话关系）` 格式。不改动现有文字。

### 测试

无新增 bats 测试（纯文档变更）。consistency CHECK 9 不涉及 LIMITATIONS.md 内容。

---

## 2. P2.30：反向传播表补 BDD 传播路径

### 问题

`protocol-alignment-review.md` 反向传播表列了 7 条常见路径，无 BDD 格式相关路径。BDD 格式是横切关注点，变更时需同步 6+ 文件跨 3 类（脚本、模板、角色文件）。v0.20.0 实施时 BDD 格式变更影响了以下文件但表中无对应行：

- `agate/scripts/check-p6-provenance.sh`（BDD 计数正则）
- `agate/scripts/check-gate.sh`（P1 BDD 锚点检查）
- `agate/scripts/check-protocol-consistency.py`（CHECK 9 BDD 锚点）
- `agate/assets/templates/task-files.md`（P1 BDD 格式模板）
- `agate/assets/execution-roles/analyst.md`（BDD 写作指令）
- `agate/assets/execution-roles/test-designer.md`（BDD→测试映射）
- `agate/assets/execution-roles/verifier.md`（BDD 验证指令）
- `agate/assets/review-roles/requirements-review.md`（BDD 评审指令）
- `agate/phase-cards/P1-requirements.md`（BDD 格式声明）
- `agate/phase-cards/P3-tdd.md`（BDD 格式引用）
- `agate/phase-cards/P6-acceptance.md`（PASS 编号格式）
- `agate/CONTEXT.md`（BDD 定义）
- `agate/LIMITATIONS.md`（BDD 计数描述）

### 修改

`agate/assets/review-roles/protocol-alignment-review.md` 反向传播表追加一行：

| 改了 X | 应传播到 Y |
|--------|------------|
| `agate/` 内 BDD 编号格式（`#### BDD-NN:` heading / `###` 功能分组）| `check-p6-provenance.sh`（BDD 计数正则）、`check-gate.sh`（P1 BDD 锚点）、`check-protocol-consistency.py`（CHECK 9 锚点）、`task-files.md`（P1 模板）、`dispatch-prompt.md`（verifier BDD 格式指令）、`analyst.md`/`test-designer.md`/`verifier.md`/`requirements-review.md`/`consistency-reviewer.md`/`architect.md`（角色 BDD 指令）、`P1-requirements.md`/`P3-tdd.md`/`P6-acceptance.md`/`P7-consistency.md`（阶段卡片 BDD 引用）、`state-machine.md`（转移条件 BDD 引用）、`dispatch-protocol.md`（P6 结果格式 + gate 表）、`WORKFLOW.md`（gate 表 BDD 引用）、`CONTEXT.md`（BDD 定义）、`LIMITATIONS.md`（BDD 计数描述） |

### 测试

无新增 bats 测试（纯文档变更）。

---

## 3. P2.31：check-retrospective.sh 排除 dispatch-context + AGATE_CARD

### 问题

`check-retrospective.sh:34-41` 扫描 `$TASK_DIR/*.md` 查找 `[SCOPE+]` 时，未排除 dispatch-context 文件和 AGATE_CARD 块。而 `check-scope-resolved.sh:17-20` 已有这两项排除。两脚本扫描同一模式但排除逻辑不一致。

### 影响

低——retrospective 始终 exit 0（仅输出建议），误匹配只产生多余 warning。但一致性维护角度，两脚本应使用相同排除逻辑。

### 修改

`agate/scripts/check-retrospective.sh` 第 34-41 行，改为与 check-scope-resolved.sh 一致的模式：

```bash
if [ -d "$TASK_DIR" ]; then
    for f in "$TASK_DIR"/*.md; do
        [ -f "$f" ] || continue
        basename "$f" | grep -q 'dispatch-context' && continue
        if sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d' "$f" | grep -qE '^\s*-?\s*\[SCOPE\+\]'; then
            WARNINGS="${WARNINGS}SCOPE+ 触发（$(basename "$f")）\n"
            break
        fi
    done
fi
```

变更点：
1. 新增 `basename "$f" | grep -q 'dispatch-context' && continue`（跳过 dispatch-context 文件）
2. `grep -qE` 改为 `sed ... | grep -qE`（先剥离 AGATE_CARD 块再匹配）

### 测试

新增 2 个 bats 用例：

| 用例 | 描述 | 期望 |
|------|------|------|
| RETRO_SCOPE_DC.1 | dispatch-context 文件含 `[SCOPE+]` | 无 SCOPE+ warning |
| RETRO_SCOPE_CARD.1 | 阶段产出文件含 AGATE_CARD 块内 `[SCOPE+]` | 无 SCOPE+ warning |

---

## 4. P2.32：check-p6-evidence.sh 错误消息列具体文件名

### 问题

3 处错误消息只报计数不列文件名，影响诊断效率：

1. 行 39：`有 ${PASS_WITHOUT_REF} 条 PASS 缺文件证据引用` — 不列哪几条
2. 行 122：`有 ${EMPTY_COUNT} 个非 PNG 文件 ≤ 1KB` — 不列哪个文件
3. 行 136：`有 ${MD5_DUPES} 个截图文件逐字节完全相同` — 不列哪几个

对比 check-p6-provenance.sh 已在多处列出具体文件名/行号。

### 修改

`agate/scripts/check-p6-evidence.sh`：

**修改 1**（行 31-39）：收集缺引用的 PASS 行内容

```bash
PASS_WITHOUT_REF=0
PASS_WITHOUT_REF_DETAILS=""
while IFS= read -r line; do
    if ! echo "$line" | grep -qE '\([a-zA-Z0-9_/. -]*[a-zA-Z0-9_-]\.[a-zA-Z0-9]+[^)]*\)'; then
        PASS_WITHOUT_REF=$((PASS_WITHOUT_REF + 1))
        PASS_WITHOUT_REF_DETAILS="${PASS_WITHOUT_REF_DETAILS}  - ${line}"$'\n'
    fi
done < <(grep -E '^\s*- PASS\b' "$P6_FILE" 2>/dev/null || true)

if [ "$PASS_WITHOUT_REF" -gt 0 ]; then
    echo "GATE P6-EVIDENCE: 有 ${PASS_WITHOUT_REF} 条 PASS 缺文件证据引用（每条 PASS 必须引用证据文件，形式不限：截图/日志/JSON/文本）" >&2
    printf '%s\n' "$PASS_WITHOUT_REF_DETAILS" >&2
    exit 1
fi
```

> **R1 N1 修复**：用 `printf '%s\n'` 替代 `printf '%b'`，避免 PASS 行内容中的反斜杠序列被解释。

**修改 2**（行 74-123）：收集小文件名

在 `while` 循环内，当 `SIZE <= 1024` 时收集文件名到 `EMPTY_DETAILS` / `PNG_DETAILS` 变量，在汇总消息后打印。

```bash
EMPTY_COUNT=0
EMPTY_DETAILS=""
PNG_WARNING=0
PNG_DETAILS=""
# ... 循环内 ...
if [ "$SIZE" -le 1024 ]; then
    HEADER=$(head -c 8 "$img" 2>/dev/null | od -A n -t x1 | tr -d ' ')
    EXPECTED='89504e470d0a1a0a'
    if [ "$HEADER" = "$EXPECTED" ]; then
        PNG_WARNING=$((PNG_WARNING + 1))
        PNG_DETAILS="${PNG_DETAILS}  - $(basename "$img")"$'\n'
    else
        EMPTY_COUNT=$((EMPTY_COUNT + 1))
        EMPTY_DETAILS="${EMPTY_DETAILS}  - $(basename "$img")"$'\n'
    fi
fi
# ... 循环后 ...
if [ "$EMPTY_COUNT" -gt 0 ]; then
    echo "GATE P6-EVIDENCE: P6-evidence/screenshots/ 有 ${EMPTY_COUNT} 个非 PNG 文件 ≤ 1KB（疑似充数）" >&2
    printf '%b' "$EMPTY_DETAILS" >&2
    exit 1
fi
if [ "$PNG_WARNING" -gt 0 ]; then
    echo "GATE P6-EVIDENCE WARNING: P6-evidence/screenshots/ 有 ${PNG_WARNING} 个合法 PNG ≤ 1KB（元素级小截图，不阻断但请确认非充数）" >&2
    printf '%b' "$PNG_DETAILS" >&2
    exit 2
fi
```

**修改 3**（行 129-137）：md5 重复列文件名

```bash
MD5_LIST=$(find "$SCREENSHOTS_DIR" -type f -not -name '.*' -exec md5sum {} \; 2>/dev/null | sort)
MD5_TOTAL=$(echo "$MD5_LIST" | grep -c . || echo 0)
MD5_TOTAL=$(echo "$MD5_TOTAL" | tail -1)
MD5_UNIQUE=$(echo "$MD5_LIST" | cut -d' ' -f1 | sort -u | grep -c . || echo 0)
MD5_UNIQUE=$(echo "$MD5_UNIQUE" | tail -1)
if [ "$MD5_TOTAL" -gt "$MD5_UNIQUE" ]; then
    MD5_DUPES=$((MD5_TOTAL - MD5_UNIQUE))
    MD5_DUPE_DETAILS=$(echo "$MD5_LIST" | cut -d' ' -f1 | sort | uniq -d | while read -r hash; do
        echo "$MD5_LIST" | grep "^${hash}" | while read -r _ path; do
            printf '  - %s\n' "$(basename "$path")"
        done
    done)
    echo "GATE P6-EVIDENCE: 有 ${MD5_DUPES} 个截图文件逐字节完全相同（md5 重复，疑似同一物理文件被多条 PASS 引用充数）" >&2
    printf '%s' "$MD5_DUPE_DETAILS" >&2
    exit 1
fi
```

> **R1 B1+N2 修复**：用 `while read -r _ path` 替代 `awk '{print $2}'`——md5sum 输出格式为 `hash  /path`（两空格分隔），`read -r _ path` 正确捕获含空格的完整路径。用 `basename "$path"` 统一输出格式，与其他 DETAILS 一致。用命令替换 `$(...)` 收集 dupe details（管道中 while 在子 shell，变量赋值丢失——改用 `printf` 输出 + 命令替换捕获）。

### 测试

新增 4 个 bats 用例：

| 用例 | 描述 | 期望 |
|------|------|------|
| EVIDENCE_NO_REF_DETAIL.1 | P6-acceptance.md 有 PASS 行缺文件引用 | 错误消息含 `  - ` 前缀 + 具体 PASS 行文本 |
| EVIDENCE_EMPTY_DETAIL.1 | screenshots/ 有非 PNG ≤ 1KB | 错误消息含 `  - ` 前缀 + 具体 basename |
| EVIDENCE_MD5_DETAIL.1 | screenshots/ 有 md5 重复文件 | 错误消息含 `  - ` 前缀 + 具体 basename |
| EVIDENCE_MD5_DETAIL.2 | screenshots/ 有 md5 重复文件（文件名含空格） | 错误消息含完整 basename（含空格） |

> **R1 N5+N6 修复**：测试验证 DETAILS 格式（`  - ` 前缀 + 内容），新增含空格文件名测试。

---

## 5. 实施顺序

1. P2.29（LIMITATIONS↔ADR 交叉引用）— 纯文档，无依赖
2. P2.30（反向传播表补 BDD 路径）— 纯文档，无依赖
3. P2.31（retrospective 排除）— 脚本修改 + 2 测试
4. P2.32（evidence 错误消息详情）— 脚本修改 + 3 测试

## 6. 涉及文件汇总

| 文件 | 修改项 |
|------|--------|
| `agate/LIMITATIONS.md` | P2.29：5 条局限末尾加 ADR 引用 |
| `agate/assets/review-roles/protocol-alignment-review.md` | P2.30：反向传播表加 1 行 |
| `agate/scripts/check-retrospective.sh` | P2.31：加 2 行排除逻辑 |
| `agate/scripts/check-p6-evidence.sh` | P2.32：3 处消息补 DETAILS |
| `agate/tests/unit/check-retrospective.bats` | P2.31：+2 用例 |
| `agate/tests/unit/check-p6-evidence.bats` | P2.32：+4 用例 |

## 7. 验证

- bats 全量通过（含 6 新用例）
- `python3 agate/scripts/check-protocol-consistency.py` 0 ERROR
- `shellcheck -S warning agate/scripts/*.sh` clean
- self-gate protocol-alignment-review

## 8. 不在本版范围

| ID | 内容 | 理由 |
|----|------|------|
| P2.24 | ADR-007 | 事后记录非前瞻决策，低优先级 |
| P2.25 | P0-brief change_nature | 类别错误，DROP |
| P2.26 | P0 导航措辞 | 有意差异，DROP |
| P2.27 | python3 环境变量 | 零真实报告，维护成本 > 收益 |
| P2.28 | VERSION_TAG_PREFIX 测试 | 一行默认值，测试成本 > bug 风险 |
