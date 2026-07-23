# Plan：BDD 格式标准化 + T068 复盘三个 gate bug 修复

> 日期：2026-07-24
> 版本影响：minor bump（v0.19.0 -> v0.20.0，P1 产出格式变更是破坏性变更）
> 破坏性变更：**有**--P1-requirements.md 的 BDD 格式从"非结构化列表项"变为"标准 heading 编号"。现有任务的 P1 需迁移（把 `- AC1: GWT` 改为 `#### BDD-1: 描述` + GWT）
> 来源：`docs/reviews/review-20260723-2311.md` T068 复盘 + 用户关于 BDD 计量单位的设计讨论

---

## 诚实标注

1. **BDD 格式标准化是用户发起的设计讨论**，不是被动 bug 修复。用户质疑"BDD 编号格式不固定"不合理，对照业界 Gherkin/Cucumber 实践后确认：验收的原子单位应该是 Scenario（一条 Given-When-Then），而非含糊的"BDD 标签"。标准化编号让 P1->P3->P6->P7 的追溯链路完整可靠。

2. **三个 gate bug 的根因均经代码核实**（非推测），每个定位到具体代码行：
   - T3/M2：`check-p6-provenance.sh:131` Given 行数计数
   - T6：`pre-commit-gate.sh:134` 步骤2 无行首锚点
   - M5：`check-gate.sh:148` 全文 bullet 计数

3. **T3 的修复方案经历了两轮迭代**：第一轮"按 BDD 标题计数"被评审否决（fixture 用 `AC1`/`- Given` 格式，不含 `BDD` 字样，15+ 测试回归）；第二轮"降级 exit 1 -> WARNING"被用户质疑"连数字都说不明白不合理"；最终方案是**标准化 BDD 格式**，让计数从根源上可靠。

4. **heading 层级经过设计讨论**：用户指出 `###` 可选 + `####` 必选会导致 markdown heading 跳级。最终方案：`###` 功能分组**必选**（简单任务写一个分组名即可），保证 `##` -> `###` -> `####` 层级一致。

---

## 第一部分：BDD 格式标准化

### 背景

agate 当前对 BDD 的定义是"格式不固定，主 Agent 自行判定"（P1-requirements.md:49、state-machine.md:390）。这导致：

1. **计数不可靠**：gate 用 Given 行数做启发式计数，一条 BDD 挂多个 Given 时虚增
2. **验收可能漏验**：一条 BDD 挂多个 Given（正常流 + 异常流），P6 只写一条 PASS，异常流被漏
3. **追溯链断裂**：P1 的 "AC1"、P3 的测试名、P6 的 "Bxx" 编号体系不一致，审计困难

业界标准（Gherkin/Cucumber）的层级模型：

| Gherkin 层级 | 职责 | 验收单位 |
|-------------|------|---------|
| Feature | 功能模块 | 否（分组） |
| Rule | 业务规则 | 否（分组） |
| Scenario | 具体行为（一条 GWT） | **是** |

agate 的 Feature 层级由 P0-brief 承载（任务本身就是"做一个 Feature"），P1 内部需要的是子功能分组 + Scenario。

### 标准 BDD 格式

```markdown
## 3. BDD 验收条件

### {功能分组名}

#### BDD-1: {行为描述}
- Given {前置条件}
- When {触发事件}
- Then {预期结果}

#### BDD-2: {行为描述}
- Given {前置条件}
- When {触发事件}
- Then {预期结果}

### {另一个功能分组名}

#### BDD-3: {行为描述}
- Given {前置条件}
- When {触发事件}
- Then {预期结果}
```

**格式规则**：

| 元素 | 格式 | 必需？ | gate 计数？ |
|------|------|--------|------------|
| 功能分组 | `### {名称}` | **必选** | 否 |
| BDD 编号 | `#### BDD-NN: {描述}` | 必选 | **是**（`grep '^#### BDD-[0-9]'`） |
| GWT | `- Given` / `- When` / `- Then` | 必选 | 否 |
| 数据驱动表 | `\| ... \|` markdown 表格 | 可选 | 否（共享一个 BDD-NN） |

**关键约束**：

1. 每个 `#### BDD-NN` 下**有且仅有一个** Given-When-Then 流
2. 正常流、异常流、边界流各自独立编号（BDD-1 正常流、BDD-2 异常流）
3. 数据驱动（同一行为不同数据）用 Examples 表，共享一个 BDD-NN：

```markdown
#### BDD-4: API key 数量上限校验
- Given 已有 <existing> 个活跃 API key
- When 创建新 API key
- Then <result>

| existing | result    |
|----------|-----------|
| 0        | 201 成功   |
| 5        | 400 拒绝   |
```

4. 功能分组必选：简单任务写一个分组名（如功能名或"主流程"），保证 heading 层级 `##` -> `###` -> `####` 不跳级

### 各文件修改

#### 1. `agate/assets/templates/task-files.md`（P1 模板）

行 136-138，从：
```markdown
## 3. BDD 验收条件
- AC1: Given ... When ... Then ...
- AC2: Given ... When ... Then ...
```
改为：
```markdown
## 3. BDD 验收条件

### {功能分组名}

#### BDD-1: {行为描述}
- Given ...
- When ...
- Then ...

#### BDD-2: {行为描述}
- Given ...
- When ...
- Then ...
```

#### 2. `agate/assets/execution-roles/analyst.md`（analyst 角色）

行 120-123，从：
```markdown
**BDD 验收条件**
每条用 Given/When/Then，可验证：
- ✅ Given 创建 entry 不指定过期，When 查询，Then 过期时间是 15 天后
- ✅ Given MCP publish_files 不传 expires，When 发布，Then 同样默认 15 天
```
改为：
```markdown
**BDD 验收条件**

每条 BDD 用 `#### BDD-NN:` 标题编号 + 一条 Given/When/Then。每条 BDD 是独立可验证的行为单元（正常流、异常流、边界流各自独立编号）。用 `###` 功能分组组织相关 BDD。

示例：
### 过期默认值
#### BDD-1: 不指定过期时间时默认 15 天
- Given 创建 entry 不指定过期
- When 查询过期时间
- Then 过期时间是 15 天后

#### BDD-2: MCP publish_files 不传 expires 时同样默认 15 天
- Given MCP publish_files 不传 expires
- When 发布
- Then 同样默认 15 天

❌ "用户体验更好"（不可验证）
```

行 128-133 的 BDD 反模式自检清单追加：
```markdown
- [ ] 每条 BDD 是否只有一条 Given-When-Then？（多场景必须拆为独立 BDD 编号）
- [ ] BDD 编号是否连续？（BDD-1, BDD-2, ... 不跳号）
```

#### 3. `agate/assets/execution-roles/test-designer.md`（test-designer 角色）

行 15，从：
```
- **BDD->测试**：P1 的每条 BDD 验收条件（Given/When/Then）直接转成一个测试用例
```
改为：
```
- **BDD->测试**：P1 的每条 `#### BDD-NN` 直接转成一个测试用例（1:1 映射）。带 Examples 表的 BDD-NN 转为一个参数化测试（一组数据一个 test case，共享同一 BDD 编号）
```

行 38，从：
```
- 每条 P1 BDD 验收条件都有对应测试用例
```
改为：
```
- 每条 `#### BDD-NN` 都有对应测试用例，测试名引用 BDD 编号（如 `test_bdd_1_default_expiry`）
```

#### 4. `agate/phase-cards/P6-acceptance.md`（P6 卡片）

行 50，从：
```
- PASS {BDD编号}: {描述} ({证据路径})
```
改为：
```
- PASS BDD-NN: {描述} ({证据路径})
```
（明确编号格式为 `BDD-NN`，与 P1 的 `#### BDD-NN:` 对齐）

#### 5. `agate/assets/review-roles/requirements-review.md`（P1 评审）

行 19，从：
```
- BDD 编号是否唯一且与 P6 验收可对照
```
改为：
```
- BDD 编号是否使用 `#### BDD-NN:` 标准格式且连续不跳号
- 每条 BDD 是否只有一条 Given-When-Then（多场景是否已拆为独立编号）
```

#### 6. `agate/LIMITATIONS.md`

行 41，从：
```
- BDD 总数对照：P6 结果数 ≥ P1 Given 行数（挑验拦截）；P1 BDD 格式非标准时退化为 WARNING
```
改为：
```
- BDD 总数对照：P6 结果数 = P1 `#### BDD-NN` 标题数（精确计数，不再依赖 Given 行数启发式）
```

#### 7. 文档中所有"BDD 编号格式不固定"声明 + `B[0-9]` 正则收紧

搜索并更新以下位置（将"格式不固定"改为"标准 `#### BDD-NN:` 格式"，将 `B[0-9]` 正则收紧为 `BDD-[0-9]`）：

- `agate/phase-cards/P1-requirements.md:49` — "格式不固定" → "标准 `#### BDD-NN:` 格式"
- `agate/state-machine.md:390` — "BDD 编号格式不固定，按实际格式 grep" → "BDD 编号格式为 `#### BDD-NN:`"
- `agate/state-machine.md:117` — "BDD 总数对照需主 Agent 手动核实" → "BDD 总数对照由 provenance 审计 3 自动执行"
- `agate/state-machine.md:402-403` — "BDD 总数对照需主 Agent 手动核实" + `grep -cE '^\s*- (PASS|FAIL)'` → 更新为 provenance 审计 3 自动执行
- `agate/rules/state-transitions.md:36` — "主 Agent 手动核实 BDD 总数" → "exit 0 自动对照 / exit 2 需手动核实并迁移"
- `agate/WORKFLOW.md:222` — "主 Agent 手动核实 BDD 总数 = P1 BDD 总数（provenance exit 2 时必做）" → 更新为 provenance 审计 3 自动执行（exit 0 时无需手动核实）
- `agate/dispatch-protocol.md:787` — "主 Agent 手动核实 `grep -cE '^\s*- (PASS\|FAIL)' P6-acceptance.md` = P1 BDD 总数（provenance exit 2 时必做）" → 更新为 provenance 审计 3 自动执行
- `agate/dispatch-protocol.md:782` — "BDD 编号格式不固定，按实际格式 grep" + `含 BDD-/B[0-9] 锚点` → "BDD 编号格式为 `#### BDD-NN:`" + `含 BDD-[0-9] 锚点`
- `agate/dispatch-protocol.md:377-379,388-389,393-394,529,532-533` — 示例中 `B01/B02/B03/B07/B12` → `BDD-1/BDD-2/BDD-3/BDD-7/BDD-12`
- `agate/WORKFLOW.md:217` — `含 BDD-/B[0-9] 锚点` → `含 BDD-[0-9] 锚点`

#### 8. `agate/scripts/check-gate.sh` 过时消息

- 行 80：`echo "GATE P1: ... BDD 编号格式不固定，需主 Agent 自行判定"` -> 改为 `"GATE P1: ... BDD 编号格式为 #### BDD-NN:"`
- 行 185：`echo "GATE P6: ... BDD 总数对照需主 Agent 手动核实 P1 条数。"` -> 改为 `"GATE P6: ... BDD 总数对照由 check-p6-provenance.sh 审计 3 自动执行"`（格式标准化后审计 3 可靠工作，不再是"需手动核实"）

#### 9. `agate/assets/execution-roles/verifier.md`

- 行 134 已用 `{BDD编号}`（格式无关的占位符），**不需要修改**。
- 行 93 示例用 `B01` 格式，需改为 `BDD-1`：`- PASS B01: 描述 (...)` → `- PASS BDD-1: 描述 (...)`（2 处）

#### 10. `agate/phase-cards/P3-tdd.md`

行 27/34 引用 "P1 的 BDD 验收条件"——格式标准化后应提及 `#### BDD-NN` 标准格式，使 P3 test-designer 知道 BDD 编号结构：

- 行 27：`P1-requirements.md（BDD 验收条件）` → `P1-requirements.md（BDD 验收条件，每条 #### BDD-NN 对应一个测试用例）`
- 行 34：`每条测试用例对应一条 P1 的 BDD 验收条件` → `每条测试用例对应一条 P1 的 #### BDD-NN 验收条件（1:1 映射）`

#### 11. `agate/assets/review-roles/requirements-review.md`

行 53-54 输出格式示例仍用 `B01`/`B02`，需改为 `BDD-1`/`BDD-2`：

从：
```
- B01: <判定> + <覆盖维度：数据✓ 前端✓ 多端✗ 边界✓ 兼容✓>
- B02: ...
```
改为：
```
- BDD-1: <判定> + <覆盖维度：数据✓ 前端✓ 多端✗ 边界✓ 兼容✓>
- BDD-2: ...
```

#### 12. `agate/CONTEXT.md`

行 15 BDD 定义需补充编号格式：

从：
```
| BDD | Behavior-Driven Development，Given/When/Then 格式的验收条件 | WORKFLOW.md §需求基线 |
```
改为：
```
| BDD | Behavior-Driven Development，`#### BDD-NN:` 标题编号 + 一条 Given/When/Then 的验收条件 | WORKFLOW.md §需求基线 |
```

#### 13. `agate/scripts/check-protocol-consistency.py`

CHECK 9 锚点表追加 BDD 编号格式检查锚点（在 `SCRIPT_ALIGNMENT_ANCHORS` 末尾追加）：

```python
{
    "desc": "P1 BDD 编号格式检查（标准 #### BDD-NN: 格式）",
    "script": "agate/scripts/check-gate.sh",
    "keywords": ["BDD-[0-9]"],
},
```

**注意**：收紧后 check-gate.sh:61 用 `BDD-[0-9]`，此锚点验证该关键词存在。旧锚点中无 BDD 格式相关条目，需新增。

#### 14. `README.md` 版本号

行 6 version badge 需在实施完成后更新为 `v0.20.0`（与 git tag 同步）。

#### 15. `agate/assets/templates/dispatch-prompt.md`

行 109/111/112/125 示例用 `B01`/`B02` 格式，需改为 `BDD-1`/`BDD-2`：

- 行 109：`| B01 | ... | PASS |` → `| BDD-1 | ... | PASS |`
- 行 111：`- PASS B01: 用户可以创建分享链接` → `- PASS BDD-1: 用户可以创建分享链接`
- 行 112：`- FAIL B02: 过期链接返回 410` → `- FAIL BDD-2: 过期链接返回 410`
- 行 125：`- PASS B01: 用户可以创建分享链接（p6-b01.png）` → `- PASS BDD-1: 用户可以创建分享链接（p6-bdd-1.png）`

#### 16. `agate/assets/templates/task-files.md`（补充行）

Plan 第 1 项已列行 136-138（BDD 格式部分）。以下行也需更新：

- 行 250：`### AC1: entry 不指定过期时间默认 15 天` → `#### BDD-1: entry 不指定过期时间默认 15 天`（P6 模板中的验收编号）
- 行 254：`### AC2: ...` → `#### BDD-2: ...`
- 行 261：`- PASS B01: ... (p6-b01.png)` → `- PASS BDD-1: ... (p6-bdd-1.png)`
- 行 265：`- PASS B01: ... (screenshots/b01.png) (vision: vision-reports/b01.yaml)` → `- PASS BDD-1: ... (screenshots/bdd-1.png) (vision: vision-reports/bdd-1.yaml)`
- 行 272：`- PASS B01: 返回 3 条记录 (response.json)` → `- PASS BDD-1: 返回 3 条记录 (response.json)`

#### 17. `agate/assets/execution-roles/architect.md`

行 90 示例用 `AC6` 格式，需改为 `BDD-6`：

- `AC6 关联方案已变更` → `BDD-6 关联方案已变更`

### 测试 fixture 更新

所有 P1-requirements.md fixture 需更新为标准格式：
- `tests/fixtures/full-task/P1-requirements.md`
- `tests/fixtures/paused-task/P1-requirements.md`
- `tests/fixtures/ui-affected/P1-requirements.md`
- `tests/fixtures/high-risk/P1-requirements.md`
- `tests/fixtures/vision-blocked/P1-requirements.md`
- `tests/helpers/fixtures.bash`（`create_task_dir` 默认 P1 内容，含 1 条 `#### BDD-1:`）

所有 P6-acceptance.md fixture 需将 `AC1/AC2/AC3` 编号改为 `BDD-1/BDD-2/BDD-3`：
- `tests/fixtures/full-task/P6-acceptance.md`（AC1→BDD-1, AC2→BDD-2）
- `tests/fixtures/paused-task/P6-acceptance.md`（AC1→BDD-1, AC2→BDD-2）
- `tests/fixtures/ui-affected/P6-acceptance.md`（AC1→BDD-1, AC2→BDD-2）
- `tests/fixtures/high-risk/P6-acceptance.md`（AC1→BDD-1, AC2→BDD-2, AC3→BDD-3）
- `tests/fixtures/vision-blocked/P6-acceptance.md`（AC1→BDD-1, AC2→BDD-2）

**注意**：gate 脚本（check-p6-evidence.sh、check-p6-provenance.sh）只匹配 `- PASS` / `- FAIL` 前缀，不解析编号本身，因此 AC→BDD 编号变更不影响 gate 功能。但格式必须同步以保持一致性。

**helper 处置**：`fixtures.bash` 中的 `add_p1_given`（行 242）和 `add_given_line`（行 29）添加 `- Given` 行。新格式下 Given 行不计入 BDD 计数。这两个 helper 当前无调用者（死代码），**标记废弃但不删除**（避免破坏可能的下游 fork）。新增 `add_p1_bdd` helper 添加 `#### BDD-NN:` 标题行，供新测试使用。

**`add_p1_bdd` 规格**：
- 函数签名：`add_p1_bdd <task_dir> [description]`
- 行为：在 P1-requirements.md 末尾追加 `#### BDD-NN:` 标题行（NN 为当前最大编号 +1，若无已有 BDD 则从 1 开始）
- 输出格式：`#### BDD-NN: {description}`（仅标题行，不含 GWT 子行——GWT 由测试自行追加）
- 编号自增逻辑：`grep -cE '^#### BDD-[0-9]' "$p1" 2>/dev/null || echo 0` → +1

**`create_task_dir` 默认 P1 内容修改**（行 105-112）：

从：
```markdown
---
agent: test
---
risk_level: $risk_level
phases: [$phases_csv]
- Given test precondition
```

改为：
```markdown
---
agent: test
---
risk_level: $risk_level
phases: [$phases_csv]

### 主流程

#### BDD-1: test
- Given test precondition
- When test action
- Then test result
```

**关键**：`create_task_dir` 生成的 P1 必须含 `#### BDD-1:` 标题，否则新计数逻辑下 P1_BDD=0，大量测试退化为 exit 2。

P1 fixture 从：
```markdown
- AC1: Given ... When ... Then ...
- AC2: Given ... When ... Then ...
```
改为：
```markdown
### 主流程

#### BDD-1: Given ... When ... Then ...
- Given ...
- When ...
- Then ...

#### BDD-2: Given ... When ... Then ...
- Given ...
- When ...
- Then ...
```

P6 fixture 从：
```markdown
- PASS AC1 (result1.json)
- PASS AC2 (result2.json)
```
改为：
```markdown
- PASS BDD-1 (result1.json)
- PASS BDD-2 (result2.json)
```

### 测试 .bats 文件中旧编号批量替换

以下测试文件使用旧编号格式（`AC1/AC2/...` 或 `B01/B02/B03`），需批量替换为 `BDD-1/BDD-2/BDD-3`：

| 文件 | 替换处数 | 旧格式 | 说明 |
|------|---------|--------|------|
| `tests/unit/check-p6-provenance.bats` | ~40 处 | `AC\d+` | `- PASS AC1` → `- PASS BDD-1` 等 |
| `tests/unit/check-p6-evidence.bats` | ~30 处 | `AC\d+` | 同上 |
| `tests/unit/check-gate.bats` | ~15 处 | `AC\d+` | 行 393/394/405/406/427/428/440/441/453/465/466/477/946/947/1136 |
| `tests/unit/check-p6-format.bats` | ~10 处 | `B0\d` | `B01/B02/B03` → `BDD-1/BDD-2/BDD-3`（含 grep 断言中的 `PASS B01`） |
| `tests/unit/check-gate-p1-review.bats` | 6 处 | `B01` | P1-review.md 中 `- B01: PASS` → `- BDD-1: PASS`（正则收紧后必须同步） |
| `tests/unit/check-gate.bats` G_NC_BINARY | 5 处 | `B01` | 行 1068/1096/1125/1166/1195（正则收紧后必须同步） |
| `tests/integration/pre-commit-hook.bats` | 5 处 | `B01` | 行 93/183/249/400/706（正则收紧后必须同步） |
| `tests/unit/check-p6-provenance.bats` | 1 处 | `B01` | 行 323 `- PASS B01` → `- PASS BDD-1` |

**替换规则**：
- `AC(\d+)` → `BDD-\1`（如 `AC1` → `BDD-1`，`AC10` → `BDD-10`）
- `B0(\d)` → `BDD-\1`（如 `B01` → `BDD-1`，`B03` → `BDD-3`）

gate 脚本不解析编号，纯格式同步。但 `check-gate.sh:61` 正则收紧后，P1-review.md 中的 `B01` 必须改为 `BDD-1`，否则 BDD 编号检查会失败。

**不需要改的测试文件**（P1-requirements.md 的 Given 占位行不影响测试结果）：
- `check-gate-p1-review.bats`：P1-requirements.md 的 `- Given x When y Then z` 不改（只调 check-gate.sh P1 分支 NEED_CONFIRM 检测，不调 provenance）；但 P1-review.md 的 `B01` 编号引用**必须改**
- `check-gate.bats` G_NC_BINARY：P1-requirements.md 的 Given 占位行不改；但 P1-review.md 的 `B01` 编号引用**必须改**
- `check-state-transition.bats`：P1 文件仅作 commit gate 存在性证据，不调 provenance，Given 行不改

### check-gate.sh BDD 正则收紧

行 61 的 `grep -qE 'BDD-|B[0-9]'` 中 `B[0-9]` 会误匹配 B2B/B2C 等词。BDD 标准化后应收紧为：

```bash
# 修复前：
if ! grep -qE 'BDD-|B[0-9]' "$P1_REVIEW" 2>/dev/null; then

# 修复后：
if ! grep -qE 'BDD-[0-9]' "$P1_REVIEW" 2>/dev/null; then
```

**副作用**：当前 P1-review.md fixture 中使用 `B01` 格式（6 处 check-gate-p1-review.bats + 5 处 check-gate.bats G_NC_BINARY + 5 处 pre-commit-hook.bats），靠 `B[0-9]` 分支通过 BDD 编号检查。收紧后 `B01` 不再匹配，这些 fixture 必须同步改为 `BDD-1`（见上方 bats 替换表）。

---

## 第二部分：三个 gate bug 修复

### Bug 1：T6 -- PROD_TOUCHED 步骤2 误匹配 AGATE_CARD 注入文本

**根因**：`pre-commit-gate.sh:134` `grep -q '\[PROD_TOUCHED\]'` 无行首锚点，匹配 AGATE_CARD 注入的卡片说明文本中的 `[PROD_TOUCHED]` 字面量。

**修复**：扫描前剥离 AGATE_CARD 块（复用 `check-p6-provenance.sh:119` 已验证的 sed 模式）。

```bash
# 修复前（行 129）：
DIFF_ADDED=$(git diff --cached -- "$TASK_REL" | grep '^+[^+]' | sed 's/^+//' || true)

# 修复后：
DIFF_ADDED=$(git diff --cached -- "$TASK_REL" \
    | grep '^+[^+]' \
    | sed 's/^+//' \
    | sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d' \
    || true)
```

标记格式已核实：`agate-inject-card.sh:49` 用 `<!-- AGATE_CARD_START -->` / `<!-- AGATE_CARD_END -->`，`check-p6-provenance.sh:119` 已用相同 sed 模式剥离。

### 测试

| 用例 | 描述 | 期望 |
|------|------|------|
| IT_PT_T6.1 | P8 dispatch-context 含 AGATE_CARD 注入块（内有 `[PROD_TOUCHED]` 字面量） | exit 0（不误拦） |
| IT_PT_T6.2 | 任务产出文件含句中 `[PROD_TOUCHED]`（非 AGATE_CARD 块内） | exit 1（步骤2 仍拦截） |
| IT_PT_T6.3 | 任务产出文件含行首 `[PROD_TOUCHED]` | exit 1（步骤1 拦截，回归） |
| IT_PT_T6.4 | 任务产出文件含 `[PROD_NOT_TOUCHED]` | exit 0（回归） |

### Bug 2：T3/M2 -- BDD 计数（已由第一部分标准化解决）

**根因**：`check-p6-provenance.sh:131` 用 Given 行数计数，一条 BDD 多个 Given 时虚增。

**修复**：BDD 格式标准化后，改为按 `#### BDD-NN` 标题计数。因为格式已标准化，计数可靠，`exit 1` 硬阻恢复（不再降级为 WARNING）。

```bash
# 修复前（行 128-131）：
# P6 的 PASS+FAIL 数 ≥ P1 的 Given 行数（挑验拦截）
...
P1_BDD=$(grep -cE '^\s*-?\s*Given\b' "$P1_FILE" 2>/dev/null || echo 0)

# 修复后：
# P6 的 PASS+FAIL 数 ≥ P1 的 BDD 标题数（挑验拦截）
...
P1_BDD=$(grep -cE '^#### BDD-[0-9]' "$P1_FILE" 2>/dev/null || echo 0)
```

`exit 2` 兜底分支（无 BDD 标题行）保留 exit 2 而非升级为 exit 1：**过渡期兼容**--现有未迁移的 legacy P1 文件（用 `- AC1: Given...` 格式）在迁移前仍需能过 gate，exit 2（WARNING）让主 Agent 手动核实而非硬阻。迁移完成后（下个 major version）可考虑升级为 exit 1。消息更新为"P1 无 `#### BDD-NN` 标准格式 BDD（可能使用 legacy 格式），需主 Agent 手动核实并迁移为标准格式"。

### 测试

| 用例 | 描述 | 期望 |
|------|------|------|
| PV_BDD_COUNT.1 | P1 含 3 条 `#### BDD-NN`，P6 有 3 条 PASS | exit 0 |
| PV_BDD_COUNT.2 | P1 含 2 条 `#### BDD-NN`，P6 有 1 条 PASS | exit 1（挑验拦截，硬阻恢复） |
| PV_BDD_COUNT.3 | P1 无 `#### BDD-NN` 标题（legacy 格式） | exit 2（过渡期兜底） |
| PV_BDD_COUNT.4 | P1 含 1 条带 Examples 表的 BDD-NN，P6 有 1 条 PASS | exit 0（数据驱动共享编号） |
| PV_BDD_COUNT.5 | P1 BDD 编号有间隔（BDD-1, BDD-3，无 BDD-2），P6 有 2 条 PASS | exit 0（按标题计数，非 max 编号） |

**现有测试影响**：
- PV.9（原 4 Given vs 1 PASS -> exit 1）：fixture 改为标准格式后 P1_BDD=1（不再是 4），需更新场景为"P1 含 2 条 BDD，P6 有 1 条 PASS -> exit 1"
- PV.10（无 Given -> exit 2）：改为"P1 无 `#### BDD-NN` -> exit 2"
- 其他 PV 测试：fixture 改为标准格式后 P1_BDD 计数不变（1 条 BDD = 1 个标题），exit 0 不变

### Bug 3：M5 -- P5 gate_commands 计数统计所有缩进 bullet 行

**根因**：`check-gate.sh:148` `grep -cE '^\s+- '` 统计所有缩进 bullet 行，而非 gate_commands YAML 块内的 P5 键。

**修复**：用 python3 regex 提取 gate_commands 块，统计 P5 开头的键数。同时更新 G5.1 fixture 为 spec 格式。

```bash
# 修复前（行 148）：
P5_CMD_COUNT=$(grep -cE '^\s+- ' "$TASK_DIR/P2-design.md" 2>/dev/null || echo 0)

# 修复后：
P5_CMD_COUNT=$(GATE_FILE="$TASK_DIR/P2-design.md" python3 -c "
import re, os
with open(os.environ['GATE_FILE']) as f:
    content = f.read()
m = re.search(r'^gate_commands:\s*\n((?:  .+$|\s*$)+)', content, re.MULTILINE)
if not m:
    print(0)
    exit()
block = m.group(1)
count = len(re.findall(r'^  (P5\w*):', block, re.MULTILINE))
print(count)
" 2>/dev/null || echo 0)
P5_CMD_COUNT=$(echo "$P5_CMD_COUNT" | tail -1)
```

**注意**：block 捕获用 `.+` 而非 `.+\n`（配合 `re.MULTILINE`），消除对 trailing newline 的依赖。若 P2-design.md 末行无换行且 gate_commands 是最后一块，仍能正确捕获。

**旧格式兼容**：WARNING 仅对 spec 格式（`gate_commands:` YAML 键 + `P5: "cmd"` 字符串值）有效。旧列表格式（`P5:\n  - cmd`）仍计 P5 键=1，不触发 WARNING。这是可接受的退化--WARNING 不触发不等于放行，P5 gate 恒 exit 2。

G5.1 fixture（check-gate.bats:366-380）从 `## gate_commands` 标题 + 列表格式更新为 spec 格式：

```yaml
gate_commands:
  P5: "pytest -q --tb=no"
  P5_e2e: "playwright test --reporter=line tests/e2e/"
```

确保含 2 个 P5 键以触发 WARNING（2 > 1）。

### 测试

| 用例 | 描述 | 期望 |
|------|------|------|
| G5_CMD.1 | P2 gate_commands 声明 P5 + P5_e2e（2 键），P2 其他节含 20 个 bullet | WARNING 含"2"而非"22" |
| G5_CMD.2 | P2 gate_commands 只声明 P5（1 键），其他节含 10 个 bullet | 无 WARNING |
| G5_CMD.3 | P2 无 gate_commands 块 | 无 WARNING，无崩溃 |
| G5_CMD.4 | P2 gate_commands 声明 P5 + P6（1 个 P5 键） | 无 WARNING |
| G5_CMD.5 | 更新后的 G5.1 fixture（spec 格式）回归 | WARNING 含"gate_commands.P5" |

---

## 实施顺序

1. **BDD 格式标准化**（第一部分）：
   - 更新模板（task-files.md 含补充行、dispatch-prompt.md）
   - 更新角色定义（analyst.md、test-designer.md、requirements-review.md、verifier.md、architect.md）
   - 更新 phase-cards（P1-requirements.md、P6-acceptance.md、P3-tdd.md）
   - 更新协议文档（state-machine.md、dispatch-protocol.md、WORKFLOW.md、LIMITATIONS.md、CONTEXT.md）
   - 更新 check-gate.sh 行 61 BDD 正则收紧（`B[0-9]` → `BDD-[0-9]`）+ 行 80/185 过时消息
   - 更新 check-protocol-consistency.py CHECK 9 锚点表（追加 BDD-[0-9] 锚点）
   - 更新测试 fixture P1-requirements.md（5 个 fixture + fixtures.bash）
   - 更新测试 fixture P6-acceptance.md（5 个 fixture，AC→BDD 编号）
   - 批量替换测试 .bats 中旧编号（AC→BDD ~85 处 + B01→BDD-1 ~27 处，共 8 个文件）
2. **T3/M2 修复**（check-p6-provenance.sh BDD 计数改为 `#### BDD-NN`）+ 更新 PV 测试
3. **T6 修复**（pre-commit-gate.sh 剥离 AGATE_CARD 块）+ 新增 IT_PT_T6 测试
4. **M5 修复**（check-gate.sh P5 命令计数改为 YAML 块解析）+ 更新 G5.1 fixture + 新增 G5_CMD 测试
5. 跑全量 bats + consistency + shellcheck
6. 更新 README.md version badge 为 v0.20.0
7. self-gate：派发 protocol-alignment-review

---

## 不做的事

- **不改步骤2 为行首锚点**：步骤2 的"句中引用拦截"是有意设计，修复方向是排除 AGATE_CARD 块而非削弱检测
- **不修 T2/M1 的错误信息质量**（md5 重复/未引用证据不列文件名）：是改进点不是 bug
- **不修 M6（已知限制跟踪）**：workflow 问题，非 gate 职责
- **不修 T4（P3 测试覆盖）**：test-designer 职责
- **不修 T5（inject-card 路径）**：PR #46 目录改名 plan 处理中
- **不引入 Gherkin 关键字**（Feature:/Scenario:/Rule:）：agate 的 Feature 由 P0-brief 承载，P1 内部用 markdown heading 足够，不需要引入 Gherkin 语法
- **不改 check-gate-p1-review.bats / check-gate.bats G_NC_BINARY / check-state-transition.bats 中 P1-requirements.md 的 Given 占位行**：这些测试不调用 check-p6-provenance.sh，Given 行只是占位内容，改了增加无意义 diff。但 P1-review.md 中的 `B01` 编号引用**必须改**（正则收紧后不再匹配）

## 后续事项（不阻断本 plan）

- **ADR-007**：BDD 格式标准化是一个架构决策（从"格式不固定"变为"标准 `#### BDD-NN:` 格式"），建议在 `agate/adr.md` 补充 ADR-007。不阻断实施，可后续补。
- **protocol-alignment-review.md 反向传播表**：可补 BDD 格式传播路径（改了 BDD 编号格式 → 应传播到 requirements-review.md、P6-acceptance.md、verifier.md、test-designer.md、analyst.md、P1-requirements.md、P3-tdd.md）。此文件是推理起点而非穷举，优先级低。
