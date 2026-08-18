# 证据：BDD-21 — task-files.md gate_commands 权威 schema 样例块新增 timeout_seconds 字段格式定义（RM-AG0016）

验收方式：直接打开 HEAD 下的实际协议文件读新增内容，逐条核对 P1-requirements.md 该 BDD 的 Then 子句语义（非关键词存在性检查）。

## Then 子句逐项核对

- Then「样例块中新增 `timeout_seconds`（或等效命名）字段的格式示例」：`gate_commands:` YAML 样例块新增三行 `P5_timeout_seconds: 120` / `P5_e2e_timeout_seconds: 300` / `P6_timeout_seconds: 120`，均为可直接照抄的 `key: int` 格式 —— 满足。
- Then「含注释说明用途与缺省行为」：样例块下方新增成块注释 `# ── {key}_timeout_seconds（可选，per-key 声明）──`，含**用途**（给对应 key 声明「预期耗时上限（秒）」，供跑命令的一方据此设 shell 层超时，运行时取值 = 预期耗时 ×1.5）、**命名**（与 `{key}_formatter` / `{key}_e2e` 同为 per-key 惯例，不设整体共享默认）、**建议档位**（单元 120s / E2E 300s / 构建 600s，并标注「手动按命令类型声明，不是自动推断」）、**缺省行为**（「**不声明即等同现状**——无强制阻断、无 gate 拦截…向后兼容，沿用 dispatch_plan『缺字段 → gate 跳过校验』先例，老任务无需回填」）—— 用途与缺省行为均有，满足。
- Then「与 BDD-16 在 P2-design.md/architect.md 声明的规则一致」：四点逐条比对——排除 P3 ✓ / per-key 声明 ✓ / 三档 120·300·600s ✓ / 缺字段等同现状沿用 dispatch_plan 先例 ✓，与 P2 卡「{key}_timeout_seconds 字段规则」无数值或结论分歧 —— 满足。
- Then「三处（task-files.md 样例 / P2-design.md 卡片 / architect.md 批次设计节）字段命名、语义保持一致，不出现同一概念三种命名」：本轮实跑 `grep -n timeout_seconds` 三文件（见 shared-p6-command-output.log 第 3 节）——三处出现的形式只有 `{key}_timeout_seconds` 模板与其实例 `P5_timeout_seconds` / `P5_e2e_timeout_seconds` / `P6_timeout_seconds`，无 `timeout` / `timeout_sec` / `timeoutSeconds` 等异名 —— 满足。
- Then（联动 BDD-16 第 4 点）「若样例块的 `P3` key 下也标注 `timeout_seconds` 示例，该处注释必须附带指向 BDD-16 第 4 点『与既有 AGATE_TDD_TIMEOUT 关系』说明的引用」：条件性子句。实际落地**未在 P3 key 下加 timeout_seconds 示例**（前置条件不触发），并且反向做了更强处理——注释块含 `# ⚠️ 排除 P3：P3 key **不适用**本字段——P3 的超时继续走既有 AGATE_TDD_TIMEOUT 环境变量机制…两层不合并的完整关系说明见 P2 卡片「gate_commands 声明」的 {key}_timeout_seconds 字段规则，此处不重复展开`，并在既有 P3 键注释末补一行 `# P3 的超时不写 P3_timeout_seconds（见上方"排除 P3"），改用 AGATE_TDD_TIMEOUT 环境变量。` —— 「照抄样例时忽略既有机制冲突风险」这一 Then 的立法意图被直接消除，满足。
- 关键词可 grep：样例块含逐字 `timeout_seconds`，pytest 锚点 BDD-21 本轮独立实跑 PASSED。

## 实际文件文本摘录（HEAD）

### `agate/assets/templates/task-files.md` L265-294

```markdown
## 3. gate 命令（在 P2 固化，后续不得修改）
gate_commands:
  P3: "pytest"                     # 可选：测试运行器（verbose 输出，供 check-tdd-red.py 自动读取）
  P3_e2e: "playwright test --reporter=line tests/e2e/"   # ui_affected 且新增测试在 E2E 层时必填（T090 问题2）
  P3_formatter: "pytest.sh"  # 可选：formatter 脚本（见 assets/formatters/README.md 速查表）
  P5: "pytest -q --tb=no"          # 紧凑输出模式（见下）
  P5_formatter: "pytest.sh"        # 可选：formatter 脚本，将测试输出标准化为 JSON
  P5_timeout_seconds: 120          # 可选：该 key 命令的预期耗时上限（秒），见下方字段说明
  P5_e2e: "playwright test --reporter=line tests/e2e/"   # ui_affected: true 时必填
  P5_e2e_timeout_seconds: 300      # 可选：per-key 声明，E2E 与单元测试各取各的档
  P6: "pytest -q --tb=no tests/acceptance/"
  P6_timeout_seconds: 120          # 可选
  project_module: "myapp"  # 可选：项目模块前缀，B 类检测用
# ── {key}_timeout_seconds（可选，per-key 声明）──
# 用途：给对应 key 的 gate 命令声明"预期耗时上限（秒）"，供跑命令的一方据此设 shell 层超时
#       （运行时取值 = 预期耗时 ×1.5，见 dispatch-protocol.md「命令超时兜底与既有超时机制的分层关系」）。
# 命名：与 {key}_formatter / {key}_e2e 同为 per-key 惯例，逐条 key 各自声明，不设整体共享默认
#       （单元测试与 E2E 耗时差 2.5 倍以上，共享一个值起不到分类阈值作用）。
# 建议档位（**手动按命令类型声明，不是自动推断**——没有代码去猜命令属于哪一类）：
#       单元测试类 120s / E2E 类 300s / 构建类（编译·安装依赖·打包）600s。
# 缺省行为：**不声明即等同现状**——无强制阻断、无 gate 拦截，跑命令的一方按经验估算预期耗时
#       （向后兼容，沿用 dispatch_plan"缺字段 → gate 跳过校验"先例，老任务无需回填）。
# ⚠️ 排除 P3：P3 key **不适用**本字段——P3 的超时继续走既有 AGATE_TDD_TIMEOUT 环境变量机制
#       （默认 120s，由 agate_common.py 的 run_test_with_formatter() 消费、check-tdd-red.py 读取）。
#       两层不合并的完整关系说明见 P2 卡片「gate_commands 声明」的 {key}_timeout_seconds 字段规则，
#       此处不重复展开。
# P3 键（可选）：声明后 check-tdd-red.py 自动读取，无需主 Agent 手动设 TEST_RUNNER。
# P3 用 verbose 输出（区分 A/B 类错误），P5 用紧凑输出（只判过没过），两者分离。
# 非 pytest 项目建议声明此键（如 P3: "npx vitest run"）。
# P3 的超时不写 P3_timeout_seconds（见上方"排除 P3"），改用 AGATE_TDD_TIMEOUT 环境变量。
```

## 结论

**PASS** —— 权威 schema 样例块新增三行字段示例 + 成块注释（用途/命名/档位/缺省行为/排除 P3），三处命名统一为 {key}_timeout_seconds，联动子句以「不加 P3 示例 + 显式排除说明」闭合。
