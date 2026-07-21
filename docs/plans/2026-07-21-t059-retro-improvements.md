# T059 复盘改进计划

> 来源：T059-markdown-extensions-retrospective-2026-07-20.md
> 日期：2026-07-21
> 状态：draft

## Goal

修复 T059 暴露的 gate 脚本能力不足、流程与 gate 不匹配、静默失败模式三类系统性问题，使后续任务的 P6/P8 阶段不再因 gate 格式对撞而浪费 60+ 分钟。

## Architecture

本计划独立于 dispatch-context plan v8，但标注交叉依赖。改进项按三层组织：

1. **gate 脚本层**（G1-G8）：修复脚本解析能力、阈值策略、错误输出
2. **流程规范层**（P1-P5）：调整 gate 检查逻辑与实际流程的匹配度
3. **角色/行为层**（S1-S2, M1）：subagent 和主 Agent 的行为约束

## 与 dispatch-context plan v8 的交叉

| 改进项 | 与 v8 的关系 | 处理方式 |
|--------|-------------|---------|
| G4 (AGATE_CARD 自动注入) | v8 Task 6 改 hook 为 glob + 逐文件 hash 校验，但未提供自动注入脚本 | 本计划新增 `agate-inject-card.sh`，支持 glob 匹配所有 `P{N}-dispatch-context-{role}.md` 文件并逐个注入卡片。v8 实施时适配新文件名格式 |
| G6 (SCOPE+ 排除 AGATE_CARD) | v8 Task 7 Step 4 适配 XML 标记排除（dispatch_guide + objective_info），但未排除 AGATE_CARD 块 | 本计划先在当前格式下修复，v8 实施时迁移到 XML 标记排除 |
| G7 (exit 1 必须输出错误消息) | v8 不涉及 | 独立实施 |
| P2 (PASS 行格式标准化) | v8 不涉及 | 独立实施 |

---

## 关键设计决策

### D1: provenance 解析策略——精确正则 vs 通用解析

**选择**：精确正则 `\(screenshots/[^)]+\)` 匹配截图路径，`\(vision:\s*[^)]+\)` 匹配 vision 引用，而非贪心取行末括号组。

**理由**：当前 `grep -oE '\([^)]+\)$'` 取行末最后一个括号组，嵌套括号（如 `nth(1)`）会截断路径。精确正则按语义匹配，PASS 行可包含任意描述文本而不影响解析。

### D2: ≤1KB 检查策略——PNG header check + WARNING

**选择**：降级为 WARNING（exit 2），同时增加 PNG 文件头校验（前 8 字节 = `\x89PNG\r\n\x1a\n`）。

**理由**：1KB 阈值无法区分"空文件充数"和"合法小元素截图"。PNG header check 能精确识别合法 PNG 文件，排除非 PNG 文件充数。WARNING 不阻断但提醒主 Agent 关注。

### D3: md5 去重策略——降级为 WARNING

**选择**：md5 去重从 exit 1 降级为 exit 2（WARNING）。

**理由**：行为差异类 BDD（如滚动位置变化）截图可能视觉相同，md5 相同不应自动拦截。verifier 可在 acceptance report 中解释视觉相似原因。WARNING 仍提醒主 Agent 关注潜在充数。

### D4: P8 gate 检查策略——HEAD~1..HEAD + bump commit 存在性

**选择**：P8 gate 增加"最近 commit 含 version/CHANGELOG 变更"的检查路径，作为 `git diff --cached` 的补充。

**理由**：bump-version 已单独 commit，P8 产出 commit 的暂存区不含 version/CHANGELOG 变更。检查 HEAD~1..HEAD（或最近 N 个 commit）能覆盖 bump commit 已存在的场景。`git diff --cached` 仍保留作为"version 变更与 P8 产出同 commit"的检查路径。

### D5: 静默失败——强制错误消息

**选择**：所有 gate 脚本 exit 1 必须输出 stderr 消息，格式为 `GATE {脚本名}: {检查项} — {具体什么不匹配}。建议：{修复方向}`。

**理由**：LLM Agent 对静默 exit 1 的诊断成本远高于人类开发者。具体错误消息将 P6 的 60+ 分钟调试时间压缩到 5-10 分钟。

---

## Task 列表

### Task 1: G1 — provenance 截图引用解析改进

**优先级**：高
**依赖**：无
**文件**：`agate/scripts/check-p6-provenance.sh`（第 42-63 行）

**当前状态**：第 48 行剥离 `(vision:...)` 后，第 49 行用 `grep -oE '\([^)]+\)$'` 取行末括号组。嵌套括号（如 `nth(1)`）导致路径截断。

**修改方案**：

1. 替换第 42-63 行的 PASS 行解析逻辑：
   - 先剥离 `(vision:...)` 引用（保留）
   - 用精确正则 `grep -oE '\(screenshots/[^)]+\)'` 提取截图路径（替代行末括号组）
   - 若无 screenshots/ 匹配，fallback 到原逻辑（取行末括号组，兼容非截图证据）
   - 提取路径时 `sed 's/[()]//g'` 去括号（保留）

2. 错误消息增强：第 55-56 行 MISSING_REFS 计数改为逐条输出具体 PASS 行和缺失路径

**测试**：
- `agate/tests/unit/check-p6-provenance.bats` 新增：
  - PV.18: PASS 行含嵌套括号描述 `(screenshots/b07.png — element: .katex nth(1))` → 正确提取 `screenshots/b07.png`
  - PV.19: PASS 行含描述文本但截图路径存在 → exit 0
  - PV.20: PASS 行含嵌套括号且路径不存在 → exit 1 + 错误消息含具体路径

---

### Task 2: G2 — ≤1KB 检查降级 + PNG header check

**优先级**：高
**依赖**：无
**文件**：`agate/scripts/check-p6-evidence.sh`（第 73-83 行）

**当前状态**：第 76-83 行对所有 ≤1024 字节文件 exit 1。

**修改方案**：

1. 第 73-83 行替换（76-79 统计 EMPTY_COUNT，80-83 判定 exit 1）：
   - 遍历截图文件时，先检查 PNG header（前 8 字节）
   - 非 PNG header → exit 1（非 PNG 文件充数，仍阻断）
   - PNG header 但 ≤1KB → exit 2 WARNING（合法小截图，不阻断但提醒）
   - PNG header 且 >1KB → 通过

2. PNG header check 实现：
   ```bash
   PNG_HEADER='\x89PNG\r\n\x1a\n'
   HEADER=$(head -c 8 "$img" | od -A n -t x1 | tr -d ' ')
   EXPECTED='89504e470d0a1a0a'
   ```

3. 错误消息：WARNING 级输出 "P6-evidence/screenshots/ 有 N 个合法 PNG ≤ 1KB（元素级小截图，不阻断但请确认非充数）"

**测试**：
- `agate/tests/unit/check-p6-evidence.bats` 修改 E.9：≤1KB + 合法 PNG header → exit 2（WARNING，非 exit 1）
- 新增 E.15: ≤1KB + 非 PNG header → exit 1（充数拦截）
- 新增 E.16: ≤1KB + PNG header → exit 2 + WARNING 消息含"元素级小截图"

---

### Task 3: G3 — md5 去重降级为 WARNING

**优先级**：高
**依赖**：无
**文件**：`agate/scripts/check-p6-evidence.sh`（第 84-91 行）

**当前状态**：第 87-91 行 md5 重复时 exit 1。

**修改方案**：

1. 第 87-91 行：`exit 1` → `exit 2`
2. 错误消息改为 WARNING 级："P6-evidence/screenshots/ 有 N 个 md5 重复截图（行为差异类 BDD 截图可能视觉相同，不阻断但请在 acceptance report 说明原因）"

**测试**：
- `agate/tests/unit/check-p6-evidence.bats` 修改 E.12：md5 重复 → exit 2（WARNING），非 exit 1
- 新增 E.17: md5 重复 → exit 2 + WARNING 消息含"行为差异"

---

### Task 4: G4 — AGATE_CARD 自动注入脚本

**优先级**：高
**依赖**：无（v8 实施时需适配新文件名格式 `P{N}-dispatch-context-{role}.md`）
**文件**：新增 `agate/scripts/agate-inject-card.sh`，修改 `agate/dispatch-protocol.md`

**当前状态**：主 Agent 需手动运行 `agate-next-card.sh Pn` 并复制输出到 dispatch-context.md 的 AGATE_CARD 块。手写摘要导致 hash 不匹配。

**修改方案**：

1. 新增 `agate/scripts/agate-inject-card.sh`：
   - 支持 glob 匹配 `P{N}-dispatch-context-*.md`（v8 新文件名格式）
   - 对每个匹配文件注入 AGATE_CARD 块
   - 用法：`agate-inject-card.sh PHASE TASK_DIR`
   - 内部实现：
     ```bash
     shopt -s nullglob
     DC_FILES=("$TASK_DIR/${PHASE}-dispatch-context-"*.md)
     shopt -u nullglob
     if [ ${#DC_FILES[@]} -eq 0 ]; then
         # fallback: 旧格式（过渡期兼容）
         DC_FILES=("$TASK_DIR/${PHASE}-dispatch-context.md")
     fi
     for DC_FILE in "${DC_FILES[@]}"; do
         # 注入 AGATE_CARD 块
     done
     ```
   - 用 python3 替换 AGATE_CARD 块（sed 多行替换不可靠）。注意：`CARD_CONTENT` 含特殊字符时改用临时文件传递，避免 `-c` 字符串注入风险
   - 错误消息：`GATE: ${PHASE}-dispatch-context-{role}.md 不存在`（含具体文件名）
   with open(dc) as f: text = f.read()
   pattern = r'(<!-- AGATE_CARD_START -->\n)(.*?)(<!-- AGATE_CARD_END -->)'
   replacement = r'\g<1>' + card + r'\n\3'
   new_text = re.sub(pattern, replacement, text, flags=re.DOTALL)
   with open(dc, 'w') as f: f.write(new_text)
   "
   echo "AGATE_CARD 已注入: $DC_FILE"
   ```

2. `dispatch-protocol.md` 新增规范：主 Agent 必须用 `agate-inject-card.sh Pn TASK_DIR` 注入卡片，禁止手写 AGATE_CARD 内容

3. `orchestrator-template.md` 第 202 行更新：`agate-next-card.sh P{N}` → `agate-inject-card.sh P{N} TASK_DIR`

4. `phase-cards/P6-acceptance.md` 第 6 步更新：预跑 gate 前加 `agate-inject-card.sh P6 $TASK_DIR`

**测试**：
- 新增 `agate/tests/unit/agate-inject-card.bats`：
  - IC.1: dispatch-context 含 AGATE_CARD 块 → 注入后 hash 匹配
  - IC.2: dispatch-context 不含 AGATE_CARD 块 → exit 1
  - IC.3: 注入后 pre-commit hook hash 校验通过

---

### Task 5: G5 — P8 gate 增加 bump commit 检查路径

**优先级**：高
**依赖**：无
**文件**：`agate/scripts/check-gate.sh`（第 177-215 行 P8 分支）

**当前状态**：第 247-249 行 version 文件检查已降级为 WARNING。第 198-201 行 CHANGELOG 检查仍用 `git diff --cached`，bump commit 已存在时误报。

**修改方案**：

1. 第 190-201 行 version + CHANGELOG 检查逻辑改为双路径：
   - 路径 A（当前 commit 含变更）：`git diff --cached` 有 version/CHANGELOG 变更 → 通过
   - 路径 B（bump commit 已存在）：`git log -5 --oneline` 含 bump 相关 commit + `git diff HEAD~5..HEAD -- {version_files}` 有变更 + `git diff HEAD~5..HEAD -- CHANGELOG.md` 有变更 → 通过
   - 两条路径都不满足 → 原有错误消息

2. CHANGELOG 检查从 exit 1 降级为 WARNING（与 version 检查对称）：bump commit 已包含 CHANGELOG 变更时不应阻断

3. 具体实现（伪代码，实施时注意缩进统一为 2 空格）：
   ```bash
   # 路径 A: 暂存区含变更
   CACHED_VERSION=$(git diff --cached --stat 2>/dev/null | grep -qiE "$VERSION_PATTERN" && echo yes || echo no)
   CACHED_CHANGELOG=$(git diff --cached -- "$CHANGELOG_FILE" 2>/dev/null | grep -q . && echo yes || echo no)
   
    # 路径 B: 最近 commit 含变更（bump commit 已存在）
    RECENT_VERSION=no
    RECENT_CHANGELOG=no
    if [ "$CACHED_VERSION" = "no" ] || [ "$CACHED_CHANGELOG" = "no" ]; then
        LOOKBACK="${AGATE_P8_LOOKBACK:-5}"
        # 检查 HEAD~N 是否存在（新仓库或浅克隆时可能不存在）
        if git rev-parse "HEAD~${LOOKBACK}" >/dev/null 2>&1; then
            if git diff "HEAD~${LOOKBACK}..HEAD" --stat 2>/dev/null | grep -qiE "$VERSION_PATTERN"; then
                RECENT_VERSION=yes
            fi
            if git diff "HEAD~${LOOKBACK}..HEAD" -- "$CHANGELOG_FILE" 2>/dev/null | grep -q .; then
                RECENT_CHANGELOG=yes
            fi
        fi
    fi
   
   # 判定
   if [ "$CACHED_VERSION" = "no" ] && [ "$RECENT_VERSION" = "no" ]; then
       echo "GATE P8 WARNING: 暂存区和最近 ${LOOKBACK} 个 commit 均无 version 文件变更" >&2
   fi
   if [ "$CACHED_CHANGELOG" = "no" ] && [ "$RECENT_CHANGELOG" = "no" ]; then
       echo "GATE P8 WARNING: 暂存区和最近 ${LOOKBACK} 个 commit 均无 CHANGELOG 变更" >&2
   fi
   ```

4. P8 gate 整体从"version WARNING + CHANGELOG exit 1"改为"两者都 WARNING"——bump commit 存在时不应阻断

**测试**：
- `agate/tests/regression/v060-p8-cached.bats` 修改：
  - R5.2: 暂存区无 version → WARNING（保留）
  - R5.3: 暂存区无 CHANGELOG → 改为 WARNING（非 exit 1）
- 新增 R5.4: 暂存区无 version/CHANGELOG 但 HEAD~1 含 bump commit → exit 2（通过）
- 新增 R5.5: 暂存区和最近 5 commit 均无 version/CHANGELOG → WARNING

---

### Task 6: G6 — SCOPE+ 扫描排除 AGATE_CARD 嵌入块

**优先级**：高
**依赖**：无（v7 实施时迁移到 XML 标记排除）
**文件**：`agate/scripts/check-scope-resolved.sh`（第 14-20 行）

**当前状态**：第 15-19 行扫描所有 `.md` 文件中的 `[SCOPE+]`，不排除 AGATE_CARD 嵌入块。卡片模板文本含字面 `SCOPE+` 触发误报。

**修改方案**：

1. 第 14-20 行改为：扫描前先排除 `<!-- AGATE_CARD_START -->` 到 `<!-- AGATE_CARD_END -->` 之间的内容
   ```bash
   SCOPE_FOUND=""
   for f in "$TASK_DIR"/*.md; do
       [ -f "$f" ] || continue
       # 排除 AGATE_CARD 嵌入块后再搜索
       if sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d' "$f" | grep -q '\[SCOPE+\]'; then
           SCOPE_FOUND="${SCOPE_FOUND}$(basename "$f") "
       fi
   done
   ```

**测试**：
- `agate/tests/unit/check-scope-resolved.bats` 新增：
  - SC.6: dispatch-context 含 AGATE_CARD 块内字面 `[SCOPE+]` → exit 0（不误报）
  - SC.7: dispatch-context AGATE_CARD 块外有 `[SCOPE+]` → exit 1（正常拦截）

---

### Task 7: G7 — 所有 gate 脚本 exit 1 必须输出具体错误消息

**优先级**：高
**依赖**：Task 1-6（各脚本修改时同步增强错误消息）
**文件**：所有 `agate/scripts/check-*.sh` + `check-gate.sh`

**当前状态**：部分 exit 1 无 stderr 输出（如 provenance 审计 1a 的 MISSING_REFS 只输出总数不输出具体行）。

**修改方案**：

1. 重点增强以下 5 个位置的 exit 1 stderr 输出（见下方列表），其余脚本只做 `grep -c "exit 1"` 审计确认有配套 echo >&2
2. 错误消息格式规范：`GATE {检查项}: {具体什么不匹配}。建议：{修复方向}`
3. 重点增强的脚本和位置：
   - `check-p6-provenance.sh` 第 55-56 行：逐条输出缺失的 PASS 行和路径
   - `check-p6-evidence.sh` 第 80-82 行：输出具体哪些文件 ≤1KB
   - `check-p6-evidence.sh` 第 88-90 行：输出具体哪些文件 md5 重复
   - `check-gate.sh` P4 分支第 166 行：在 `exit 1` 前加 `echo "GATE P4: 暂存区无代码文件（只有 .md/.yaml/.state）" >&2`
   - `check-scope-resolved.sh` 第 39-41 行：输出具体哪个文件含 SCOPE+

4. 新增 shellcheck 风格检查：grep 所有 `exit 1` 前是否有 `echo ... >&2` 或 `printf ... >&2`

**测试**：
- 修改现有测试：每个 exit 1 测试用例增加 `[[ "$output" != "" ]]` 断言（确保有输出）
- 新增静默失败回归测试：`agate/tests/regression/gate-error-message.bats`
  - GM.1: provenance 缺失引用 → exit 1 + 输出含具体文件名
  - GM.2: evidence ≤1KB → exit 2 + 输出含具体文件名
  - GM.3: scope 未 resolve → exit 1 + 输出含具体文件名

---

### Task 8: G8 — P8 subagent 提交控制

**优先级**：高
**依赖**：无
**文件**：`agate/dispatch-protocol.md`，`agate/phase-cards/P8-release.md`，`agate/assets/execution-roles/implementer.md`

**当前状态**：P8 subagent（releaser）有 bash 权限可直接 `git commit`，绕过主 Agent 的 gate 验证控制点。

**修改方案**：

1. `dispatch-protocol.md` 新增"P8 subagent 提交约束"节：
   - P8 releaser subagent 只产出文件，不执行 `git commit` / `git tag`
   - bump-version 由主 Agent 亲自执行（或由主 Agent 在 gate 验证后授权 subagent 执行）
   - 主 Agent 验 gate → 通过后统一 commit + tag

2. `phase-cards/P8-release.md` 第 9-12 行修改：
   - 步骤 2 改为"releaser subagent 产出 P8-release.md（含临时资源清单），**不执行 git commit/tag**"
   - 步骤 3 改为"主 Agent 执行 gate 验证 → 通过后执行 bump-version → commit + tag"

3. `assets/execution-roles/implementer.md` P8 模式追加约束：
   - "P8 模式禁止执行 git commit / git tag——由主 Agent 在 gate 验证后统一执行"

4. `state-machine.md` 第 132 行 P8→READY 转移条件更新：增加"主 Agent 亲自执行 bump-version + commit + tag"的显式要求

**测试**：
- 无脚本测试（流程规范变更），通过 check-protocol-consistency.py 锚点检查覆盖

---

### Task 9: P1 — P5 gate 增加全量测试 WARNING

**优先级**：中
**依赖**：无
**文件**：`agate/phase-cards/P5-verification.md`，`agate/dispatch-protocol.md`

**当前状态**：P5 gate 只检查本任务相关测试，不检查全量测试套件。预存失败从 P5 推迟到 P8 才被发现。

**修改方案**：

1. `phase-cards/P5-verification.md` "判定规则"节新增：
   - **全量测试 WARNING**：P5 阶段建议运行全量测试套件（含非本任务测试），若发现预存失败：
     - 在 P5-test-results/unit.md 标注"预存失败：X（与本次改动无关）"
     - 主 Agent 判断：修复成本 < 推迟成本 → 立即修复；否则记录到 known-failures.md（见 Task 12）
   - 这是 WARNING 级建议，不阻断 P5 推进

2. `dispatch-protocol.md` 可判定门槛规范 P5→P6 行新增注释："建议主 Agent 在 P5 运行全量测试，发现预存失败时评估修复时机"

**测试**：
- 无脚本测试（流程建议变更）

---

### Task 10: P2 — P6 PASS 行格式标准化

**优先级**：中
**依赖**：无（文档规范独立于脚本实现）
**文件**：`agate/phase-cards/P6-acceptance.md`，`agate/assets/execution-roles/verifier.md`

**当前状态**：PASS 行格式无明确规范，verifier 自由发挥导致与 provenance 脚本不兼容。

**修改方案**：

1. `phase-cards/P6-acceptance.md` "产出规格"节新增 PASS 行最小格式规范：
   ```
   PASS 行最小格式：- PASS {BDD编号}: {描述} ({证据路径})
   证据路径格式：
   - 截图：(screenshots/{filename}.png)
   - vision：(vision: vision-reports/{filename}.yaml)
   - 其他：(result.json) / (assert.log) / ...
   描述文本可自由添加，不影响解析（provenance 脚本用精确正则提取路径）
   ```

2. `verifier.md` 第 93 行更新：引用最小格式规范，强调"描述文本不影响解析"

**测试**：
- `check-p6-provenance.bats` 新增 PV.21: PASS 行含自由描述文本 + 正确路径 → exit 0

---

### Task 11: P3 — P6 截图最小尺寸规范（被 G2 覆盖，降级为文档建议）

**优先级**：低（G2 实施后此建议变为文档建议）
**依赖**：Task 2（G2 PNG header check 实施后，≤1KB 不再阻断）
**文件**：`agate/phase-cards/P6-acceptance.md`

**修改方案**：

1. `P6-acceptance.md` "产出规格"节新增截图建议（非强制）：
   - "元素级截图建议使用父级元素 + padding，避免过小截图（≤1KB 虽不阻断但会触发 WARNING）"
   - "行为差异类 BDD 截图可能视觉相同（md5 重复），建议在 acceptance report 说明原因"

**测试**：无

---

### Task 12: P4 — 已知债务登记 known-failures.md

**优先级**：中
**依赖**：无
**文件**：新增 `agate/assets/templates/known-failures-template.md`，修改 `agate/phase-cards/P5-verification.md`

**当前状态**：预存失败无登记机制，"不是我的问题"合理化导致债务推迟。

**修改方案**：

1. 新增 `agate/assets/templates/known-failures-template.md`：
   ```markdown
   ---
   task_id: {Txxx}
   generated_by: {agent}
   ---
   # 已知失败登记
   
   ## 预存失败（非本任务引入）
   
   | # | 测试文件 | 失败数 | 根因 | 与本任务相关 | 处理计划 |
   |---|---------|--------|------|-------------|---------|
   | 1 | | | | 否 | 推迟到 / 立即修复 |
   ```

2. `P5-verification.md` "预存失败的处理"节更新：
   - 发现预存失败时，在 `known-failures.md` 登记（数量、文件、根因、是否与当前任务相关）
   - 即使不立即修复，也使债务可见、可追踪

3. `verifier.md` P5 模式更新：预存失败处理增加"登记到 known-failures.md"

**测试**：无脚本测试（模板和流程变更）

---

### Task 13: P5 — 版本 bump 时机调整

**优先级**：中
**依赖**：Task 8（G8 subagent 提交控制）和 Task 5（G5 P8 gate bump commit 检查）
**文件**：`agate/phase-cards/P8-release.md`，`agate/dispatch-protocol.md`

**当前状态**：bump-version 在 P8 subagent 执行时完成，与 P8 产出不在同一 commit，导致 chicken-and-egg。

**修改方案**：

Task 13 只修改 P8-release.md 的执行方式描述（bump 推迟到 gate 后），不重复 Task 8 的 subagent 提交约束内容。两者协同：

1. `P8-release.md` 执行方式修改：
   - releaser subagent 只产出 P8-release.md + 执行发布检查命令（同 Task 8）
   - **新增**：bump-version 推迟到主 Agent gate 验证通过后执行
   - 流程：releaser 产出 → 主 Agent 验 gate → 通过后主 Agent 执行 bump-version → 主 Agent commit + tag

2. `dispatch-protocol.md` P8 派发流程更新：明确 bump-version 由主 Agent 在 gate 通过后执行

3. 与 Task 8 (G8) 协同：subagent 不 commit + bump 推迟到 gate 后，两者共同解决 P8 流程控制问题

**测试**：无脚本测试（流程变更）

---

### Task 14: S1 — P1 analyst BDD 反模式检查清单

**优先级**：中
**依赖**：无
**文件**：`agate/assets/execution-roles/analyst.md`

**当前状态**：analyst.md 第 119-124 行有 BDD 正例和反例，但未列出常见反模式清单。

**修改方案**：

1. `analyst.md` "BDD 验收条件"节（第 119 行后）新增反模式检查清单：
   ```markdown
   **BDD 反模式自检清单**（写完每条 BDD 后逐项检查）：
   - [ ] Then 子句是否绑定了 CSS 类名？（如 `class="katex-block"` → 应改为"渲染结果包含数学公式"）
   - [ ] Then 子句是否绑定了 HTML 属性名？（如 `mathcolor 属性` → 应改为"公式颜色可自定义"）
   - [ ] Then 子句是否含主观形容词？（如"可读"/"美观"/"流畅" → 应改为可量化的客观标准）
   - [ ] Then 子句是否可二值判定？（必须 PASS 或 FAIL，不允许"部分通过"）
   - [ ] Given/When 是否绑定了实现细节？（如"调用 renderMath()" → 应改为用户行为描述）
   ```

**测试**：无

---

### Task 15: S2 — P6 verifier gate 格式预检

**优先级**：中
**依赖**：Task 1 (G1) 和 Task 2 (G2)（gate 脚本改进后预检才有意义）
**文件**：`agate/assets/execution-roles/verifier.md`

**当前状态**：verifier 产出 P6-acceptance.md 后直接返回，不预检 gate 格式。主 Agent 需来回修复格式问题。

**修改方案**：

1. `verifier.md` P6 模式"质量门槛"节新增：
   ```markdown
   **gate 格式预检**（返回主 Agent 前执行）：
   1. 运行 `bash $AGATE_ROOT/scripts/check-p6-format.sh --fix "$TASK_DIR/P6-acceptance.md"` 归一化格式
   2. 运行 `bash $AGATE_ROOT/scripts/check-p6-evidence.sh "$TASK_DIR"` 预检证据格式
   3. 运行 `bash $AGATE_ROOT/scripts/check-p6-provenance.sh "$TASK_DIR"` 预检 provenance
   4. 预检 exit 0 → 返回主 Agent
   5. 预检 exit 1/2 → 修复后重试（最多 2 轮），仍失败 → 返回主 Agent 并附预检错误消息
   ```

2. `phase-cards/P6-acceptance.md` 第 6 步更新：主 Agent 预跑 gate 前确认 verifier 已做格式预检

**测试**：无脚本测试（角色行为变更）

---

### Task 16: M1 — orchestrator-log.md 强制写入点

**优先级**：低但重要
**依赖**：无
**文件**：`agate/orchestrator-template.md`（第 167-177 行）

**当前状态**：第 174 行列出"应追加"的事件，但无强制写入点。T059 整个任务只写了 1 条 log。

**修改方案**：

1. 第 174 行"应追加"改为"必须追加"，增加具体写入点：
   ```markdown
   **必须追加的事件**（缺任一条 → 主 Agent 行为不合规）：
   - 派发 subagent 前：`NEXT: 派发 {角色} subagent 执行 {阶段}`
   - gate 失败后：`GATE FAIL: {阶段} gate 不通过，原因：{错误消息摘要}`
   - gate 失败诊断完成后：`DIAGNOSIS: {根因} → FIX: {修复方案}`（此条最重要——为后续类似失败提供恢复线索）
   - subagent 失败/空返回：`SUBAGENT FAIL: {角色} {失败原因}`
   - 流程决策：`DECISION: {PAUSED/回退/跳阶}，原因：{...}`
   ```

2. 新增"gate 失败诊断完成后"写入点——T059 复盘指出这是最关键的写入点，避免重复诊断同类型失败

**测试**：无脚本测试（主 Agent 行为约束）

---

## 实施顺序

**重要**：G4 (inject-card) 与 dispatch-context plan v8 的文件名冲突——v8 将文件名从 `P{N}-dispatch-context.md` 改为 `P{N}-dispatch-context-{role}.md`。建议：
- 如果 v8 先实施：G4 的 `agate-inject-card.sh` 需直接写 glob 版本（匹配所有 `P{N}-dispatch-context-*.md`）
- 如果 G4 先实施：v8 实施时需同步更新 G4 脚本

```
Phase 1（高优先级，独立可实施）：
  Task 1 (G1 provenance) ─┐
  Task 2 (G2 ≤1KB)       ─┤
  Task 3 (G3 md5)         ─┼→ Task 7 (G7 错误消息，依赖 Task 1-6 各脚本修改)
  Task 4 (G4 inject-card) ─┤
  Task 5 (G5 P8 gate)     ─┤
  Task 6 (G6 SCOPE+)      ─┘

Phase 2（高优先级，流程规范）：
  Task 8 (G8 subagent 提交控制)

Phase 3（中优先级，依赖 Phase 1）：
  Task 9  (P1 P5 WARNING)     ← 独立
  Task 10 (P2 PASS 格式)      ← 依赖 Task 1
  Task 12 (P4 known-failures) ← 独立
  Task 14 (S1 BDD 反模式)     ← 独立

Phase 4（中优先级，依赖 Phase 1+2）：
  Task 13 (P5 bump 时机)      ← 依赖 Task 5 + Task 8
  Task 15 (S2 verifier 预检)  ← 依赖 Task 1 + Task 2

Phase 5（低优先级）：
  Task 11 (P3 截图建议)       ← 依赖 Task 2
  Task 16 (M1 log 写入点)     ← 独立
```

## 验证方式

每个 Task 完成后：

1. **单元测试**：`bats agate/tests/unit/{对应脚本}.bats` → 全绿
2. **回归测试**：`bats agate/tests/regression/` → 全绿
3. **一致性检查**：`python3 agate/scripts/check-protocol-consistency.py` → 0 ERROR
4. **shellcheck**：`shellcheck -S warning agate/scripts/*.sh` → 0 error
5. **用例数**：`bash agate/tests/scripts/count-tests.sh` → 未漂移

全部 Task 完成后：

6. **全量测试**：`bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` → 全绿
7. **SELF-GATE**：改协议/脚本时按 SELF-GATE.md 执行自审

## 预期效果

| 指标 | T059 实际 | 改进后预期 |
|------|----------|-----------|
| P6 gate 被拦次数 | 6 | ≤2（provenance 解析 + evidence 阈值修复后） |
| P6 gate 被拦耗时 | 60+ min | ≤15 min（错误消息具体化 + verifier 预检） |
| P8 gate 被拦次数 | 2 | 0（bump commit 检查 + subagent 提交控制） |
| 重复 bump commit | 4 | 0（bump 时机调整 + gate 不误报） |
| 静默失败诊断时间 | ~30 min | ≤5 min（G7 错误消息强制输出） |
