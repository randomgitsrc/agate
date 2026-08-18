# 证据：BDD-16 — P2 卡 gate_commands 声明节 + architect.md 批次设计节新增 timeout_seconds 字段规则位（RM-AG0016）

验收方式：直接打开 HEAD 下的实际协议文件读新增内容，逐条核对 P1-requirements.md 该 BDD 的 Then 子句语义（非关键词存在性检查）。

## Then 子句逐项核对

- Then「均新增对 `timeout_seconds`（或等效命名的可选子字段）的声明规则」：① P2 卡「gate_commands 声明」样例块新增 `P5_timeout_seconds: 120` / `P5_e2e_timeout_seconds: 300` 两行 + 新增 `### {key}_timeout_seconds 字段规则` 子节（四点规则全文）；② architect.md「批次设计前置检查项」新增 `- [ ] **长命令已声明 {key}_timeout_seconds**` 检查项（含 per-key 形式示例 `P5_e2e_timeout_seconds: 300`，四点规则以引用 P2 卡权威节落地）—— 两处均有声明规则，满足。
- Then 问题 1「该字段是每条 gate 命令独立声明，还是整个 gate_commands 共享一个默认值 + 可选覆盖」：规则 2「**per-key 声明**：写成 `{key}_timeout_seconds`…每条 key 各自声明，**不设整体共享默认**——单元测试与 E2E 的耗时差 2.5 倍以上，共享一个值起不到分类阈值的作用。命名与既有 `{key}_formatter` / `{key}_e2e` 的 per-key 惯例一致」—— **二选一明确选定 per-key 且给出理由**，回答。
- Then 问题 2「默认阈值的基准来源是什么（如按命令类型分类：单元测试类 / E2E 类 / 构建类给不同默认档位）」：规则 3「**三档默认基准表**」——单元测试类 120s（依据：与 `AGATE_TDD_TIMEOUT` 默认值对齐）/ E2E 类 300s（依据：覆盖页面加载 + 多步操作，且须大于脚本内部硬超时 HARD 90s·180s 留够内层余量）/ 构建类 600s（依据：覆盖 npm install·编译，TPV0093 教训）。并显式标注「**建议档位，需按命令类型手动声明，不是自动推断**——没有任何代码去『猜』命令属于哪一类」—— **三档 + 每档依据 + 声明方式**，回答。
- Then 问题 3「缺字段时的向后兼容行为（沿用现有 `dispatch_plan` 惯例，不新增强制阻断）」：规则 4「**向后兼容**：缺字段 → 行为等同现状（沿用 `dispatch_plan` 的『缺字段 / 坏 YAML → gate 跳过校验』先例），不新增强制阻断，老任务无需回填」—— 逐字沿用既有先例，回答。
- Then 问题 4「新字段是否适用于 `gate_commands.P3` key；若适用，与既有 `AGATE_TDD_TIMEOUT` env var 机制…是互斥、叠加、还是字段本身排除 P3」：规则 1「**排除 P3**」——`gate_commands.P3` 继续走 `AGATE_TDD_TIMEOUT`（默认 120s，`agate_common.py` 的 `run_test_with_formatter()` 消费、`check-tdd-red.py` 读取，exit 124 → 超时 JSON），`timeout_seconds` **只服务 P5 / P6 / 其他非 P3 key**，不覆盖 P3；「两层不合并：P3 层是运行时代码真实消费的超时，`timeout_seconds` 是给人和 subagent 读的静态声明」—— **选定「字段本身排除 P3」分支并给出机制层面的理由**，回答（P1 只要求该层级关系问题被显式回答，不预设答案）。
- architect.md 侧的回答方式核对：检查项写「字段规则四点（排除 P3 / per-key 声明 / 三档默认基准表 / 缺字段向后兼容）的权威定义在 P2 卡片「gate_commands 声明」的 `{key}_timeout_seconds` 字段规则，本节只做声明位提醒，不重复展开基准表细节」—— 四点问题被逐一点名 + 指向唯一权威定义，符合 agate「权威定义 + 角色文件引用」惯例（BDD-15b/BDD-19 同款模式），未出现两处答案分叉的风险。
- 与层级 4 运行时纪律的衔接：P2 卡规则末「本字段是**静态声明**（层级 1），subagent 执行命令时真正去设 shell timeout 的是**层级 4** 的「命令超时兜底」（取值 = 预期耗时 ×1.5；本字段已声明时『预期耗时』直接取该值）」—— 与 BDD-13 的四层分层表逐层一致。

## 实际文件文本摘录（HEAD）

### `agate/phase-cards/P2-design.md` L130-147

```markdown
### `{key}_timeout_seconds` 字段规则

`timeout_seconds` 是 `gate_commands` 块内的**可选声明性字段**，用来给每条 gate 命令声明"预期耗时上限"，供跑命令的一方（主 Agent / subagent）据此设置 shell 层超时。四点规则：

1. **排除 P3**：`gate_commands.P3` 继续走既有 `AGATE_TDD_TIMEOUT` 环境变量机制（默认 120s，由 `agate_common.py` 的 `run_test_with_formatter()` 消费、`check-tdd-red.py` 读取，exit 124 → 超时 JSON，区分 A/B 类错误）。`timeout_seconds` **只服务 P5 / P6 / 其他非 P3 key**，不覆盖 P3。两层不合并：P3 层是运行时代码真实消费的超时，`timeout_seconds` 是给人和 subagent 读的静态声明
2. **per-key 声明**：写成 `{key}_timeout_seconds`（如 `P5_timeout_seconds` / `P5_e2e_timeout_seconds`），每条 key 各自声明，**不设整体共享默认**——单元测试与 E2E 的耗时差 2.5 倍以上，共享一个值起不到分类阈值的作用。命名与既有 `{key}_formatter` / `{key}_e2e` 的 per-key 惯例一致
3. **三档默认基准表**（**建议档位，需按命令类型手动声明，不是自动推断**——没有任何代码去"猜"命令属于哪一类）：

   | 命令类型 | 建议档位 | 依据 |
   |---------|---------|------|
   | 单元测试类（pytest / vitest 等） | 120s | 与 `AGATE_TDD_TIMEOUT` 默认值对齐，同类命令的既有锚点 |
   | E2E 类（Playwright / CDP） | 300s | 覆盖页面加载 + 多步操作；比脚本内部硬超时（HARD 90s/180s）更大——外层命令级预期时长必须留够内层完整走完的余量 |
   | 构建类（编译 / 安装依赖 / 打包） | 600s | 覆盖 `npm install` / 编译等长操作。宁可档位定高，也不要让长命令被误判失败（TPV0093 教训：`make test-quick` 挂 188 分钟） |

4. **向后兼容**：缺字段 → 行为等同现状（沿用 `dispatch_plan` 的"缺字段 / 坏 YAML → gate 跳过校验"先例），不新增强制阻断，老任务无需回填

与运行时超时纪律的关系：本字段是**静态声明**（层级 1），subagent 执行命令时真正去设 shell timeout 的是**层级 4** 的「命令超时兜底」（取值 = 预期耗时 ×1.5；本字段已声明时"预期耗时"直接取该值）。四层超时机制的完整分层见 dispatch-protocol.md「命令超时兜底与既有超时机制的分层关系」。

```

### `agate/assets/execution-roles/architect.md` L212-212

```markdown
- [ ] **长命令已声明 `{key}_timeout_seconds`**：`gate_commands` 里耗时较长的 key（E2E / 构建 / 全量回归）按 per-key 形式声明预期耗时上限（如 `P5_e2e_timeout_seconds: 300`）。字段规则四点（排除 P3 / per-key 声明 / 三档默认基准表 / 缺字段向后兼容）的权威定义在 P2 卡片「gate_commands 声明」的 `{key}_timeout_seconds` 字段规则，本节只做声明位提醒，不重复展开基准表细节
```

## 结论

**PASS** —— 两处均有字段声明规则；四个必答问题（per-key vs 共享默认 / 三档基准来源 / 缺字段向后兼容 / 与 AGATE_TDD_TIMEOUT 的层级关系＝排除 P3）在 P2 卡逐条给出明确答案，architect.md 以点名四点 + 引用权威节的方式落地。
