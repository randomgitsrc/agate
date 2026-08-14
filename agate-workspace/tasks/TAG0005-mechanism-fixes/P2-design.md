---
phase: P2
task_id: TAG0005-mechanism-fixes
type: design
parent: P1-requirements.md
trace_id: TAG0005-mechanism-fixes-P2-20260813
status: draft
created: 2026-08-13
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 12
packages: [agate-scripts-sh, agate-scripts-py, agate-docs, agate-tests]
domains: [backend, cli]
ui_affected: false
---

# P2 设计 — agate 机制修复批（TAG0005）

> 5 处互不耦合的机制/契约修复，无新机制。全量 bats（714）为回归红线。
> 本任务自身是 `domains: [backend, cli]` / `risk_level: medium` 的 agate 协议本体任务：
> 按本设计新增的 C8 规则，本任务 P2 评审将机械映射到 **plan-eng-review**（见 §2.1 自洽性说明）。

## 1. 设计总览

| 修复 | BDD | 变更对象 | 包 |
|------|-----|---------|----|
| RM-AG0010 C8 表补 backend P2 评审 | BDD-1/2 | role-system.md、rules/review-mapping.md、phase-cards/P2-design.md（三处 C8 表同步，仅新增行，不删既有行）| agate-docs |
| RM-AG0011 P5 主/辅计数 | BDD-3/4/5/6 | agate-gate-p5-count.py（输出格式）、check-gate.sh（L253-258 消费逻辑 + WARNING 文案）、check-gate.bats / agate-gate-p5-count.bats（断言同步）| agate-scripts-py、agate-scripts-sh、agate-tests |
| RM-AG0012① Review 指令条件注入 | BDD-7/8/9 | assets/templates/dispatch-prompt.md（拆独立块）、agate-render-dispatch-prompt.sh（按 ROLE_DIR 追加）、dispatch-protocol.md 内联模板（语义一致性备注）、agate-render-dispatch-prompt.bats（新增测试）| agate-docs、agate-scripts-sh、agate-tests |
| RM-AG0012② render 角色不存在 exit 2 回归 | BDD-10/11 | agate-render-dispatch-prompt.bats（新增 RP.17）、agate/tests/README.md（计数表）| agate-tests |
| RM-AG0003 空返回自动重试 | BDD-12/13/14 | dispatch-protocol.md（L105-135 空返回恢复策略增量措辞）| agate-docs |
| 同类扫描守卫 / check-debt.sh | BDD-15/16 | check-debt.sh（L24-30 依赖加载失败 exit 0→2）、agate-debt-check.bats（新增测试）| agate-scripts-sh、agate-tests |

**明确不改**：
- check-gate.sh P2 分支（L137-211）——BDD-2 硬约束（方向是 C8 补评审，非 gate 豁免）
- agate-read-p5-commands.py——BDD-6（执行枚举不变），现有 P5C.* 测试为回归守卫（I5）
- check-debt.sh 的 FILE 模式（L52-80）与「有意跳过」分支（无 retreat 提交 exit 0，L35-37）
- count-tests.sh L22 陈旧引用（P1 I8 明确排除：归档时 fb5b754 未同步，非本任务引入）
- agate-capture-env-baseline.sh 三处显式跳过 exit 0（P1 同类扫描裁定非同类的有意跳过）

## 2. 各修复设计方案

### 2.1 RM-AG0010 — C8 表补 backend P2 评审（BDD-1/2）

**设计目标**：backend 域任务 P2 有机械可派的评审角色，消除 TPV0090「gate 强制要 P2-review.md 但 C8 无触发角色 → 主 Agent 被迫自造评审」。

#### 候选方案 A：backend → plan-eng-review（P2）【选择】

- **做法**：三处 C8 表 backend 行补 `plan-eng-review（P2 方案评审）`，保留既有 `review（P4 后）`：
  - role-system.md L56：`| backend | 任意 | plan-eng-review（P2 方案评审）+ review（P4 后）|`
  - review-mapping.md L17：拆两行 `| backend | 任意 | plan-eng-review | P2 |` + 保留 `| backend | 任意 | review | P4 后 |`
  - phase-cards/P2-design.md L93-97：表内新增 `| backend | 任意 | plan-eng-review（P2 方案评审）|`
  - role-system.md「角色选择决策」节（L150-152）已写「涉及架构/技术方案 → plan-eng-review」，与表改动语义自洽，无需改
  - 新增**去重说明**（三处表同步）：同一任务命中多行且触发同一评审角色 → 去重只派发一次（backend+high 均命中 plan-eng-review，只派 1 个）
- **权衡**：
  - 优点：plan-eng-review 定义即「工程经理，审 P2 方案架构对不对」，与 backend 域语义最匹配；role-system.md 既有选择决策节已指向它；backend+high 任务因同角色自动去重，不增评审数量
  - 风险：backend 任务（含 low）P2 起恒需派一个 P2 评审 subagent，主 Agent 编排成本略增；但这是 C8「机械映射不靠临场判断」的既定代价（frontend 同理）
  - 工作量：纯文档，三处表 + 去重说明，约 10 行

#### 候选方案 B：backend → review（P2）

- **做法**：C8 表 backend 行补 `review（P2 方案评审）`，P4 后仍 review（同一角色两阶段）
- **权衡**：
  - 优点：不新增角色使用面，复用通用评审
  - 风险：review.md 定义是「偏执 Staff Engineer，P4 后审生产级 bug」，P2 审方案与其职责定位不符；backend+high 时命中 review（backend）+ plan-eng-review（high）→ 两个不同角色，评审更重；语义与 role-system.md「角色选择决策」的 P2 指引（plan-eng-review）分叉
  - 工作量：文档，略少于 A

**选择理由**：方案 A 与既有角色定义及「角色选择决策」指引一致，且 backend+high 同角色天然去重，评审负担最小。方案 B 复用通用 review 会造成角色职责漂移 + 与 high 行角色分叉。

**自洽性说明**：本任务自身是 backend+cli、medium → P2 评审按新规则机械映射 plan-eng-review；主 Agent 在 P2 必须派发 plan-eng-review 产 P2-review.md（本设计对协议本体自身立即生效，非「只修别人」）。

**BDD-2 落实**：check-gate.sh P2 分支不改——设计明确列为「明确不改」项，P5/P6 用 `grep 'P2-review.md' agate/scripts/check-gate.sh` 验证无条件要求仍在。

### 2.2 RM-AG0011 — P5 主/辅计数（BDD-3/4/5/6）

**设计目标**：`agate-gate-p5-count.py` 输出区分主命令（`P5`）与辅助命令（`P5_*`），check-gate.sh P5 WARNING 文案从「N 个命令」改为「X 个主命令 + Y 个辅助命令」。

#### 候选方案 A：空格分隔双值输出 `MAIN AUX`【选择】

- **做法**：
  - `agate-gate-p5-count.py`：`main = len(re.findall(r"^  P5:", block))`（精确 `P5:`，不匹配 `P5_e2e:`）；`aux = [k for k in re.findall(r"^  (P5_\w+):", block) if not k.endswith("_formatter")]`；无 gate_commands 块输出 `0 0`。输出单行 `"{main} {aux}"`（如 `1 2`）
  - **aux 排除 `_formatter`**：与 read-p5-commands.py L29-30 的「formatter 不执行」语义对齐——计数反映「要执行的命令」而非「键个数」（顺带修正现状 formatter 键被计入的既有偏差，见设计注）
  - check-gate.sh L253-258 消费改造：
    ```bash
    P5_CMD_DATA=$(GATE_FILE="$TASK_DIR/P2-design.md" python3 "$SCRIPT_DIR/agate-gate-p5-count.py" 2>/dev/null || echo "0 0")
    P5_MAIN=$(printf '%s\n' "$P5_CMD_DATA" | awk '{print $1}' | tail -1)
    P5_AUX=$(printf '%s\n' "$P5_CMD_DATA" | awk '{print $2}' | tail -1)
    P5_TOTAL=$((P5_MAIN + P5_AUX))
    if [ "$P5_TOTAL" -gt 1 ]; then
        echo "GATE P5 WARNING: P2 声明了 ${P5_MAIN} 个主命令 + ${P5_AUX} 个辅助命令（共 ${P5_TOTAL} 条 gate_commands.P5 命令），请确认已全部执行（非子集）。" >&2
    fi
    ```
  - WARNING 触发条件保持 `P5_TOTAL > 1`：仅 P5（无 P5_*）→ total=1 → 不 WARNING（BDD-5 现状保持）
  - 测试同步：agate-gate-p5-count.bats GPC.1 `3`→`1 2`、GPC.2 `0`→`0 0`；check-gate.bats G5_CMD.1/G5_CMD.5 断言 `2 个 gate_commands.P5` → `1 个主命令 + 1 个辅助命令` + `共 2 条`；G5.1 / G5_CMD.2/3/4 保持（G5.1 断言含 `gate_commands.P5` 仍命中；2/3/4 断言「不含 gate_commands.P5 命令」仍不命中）
- **权衡**：
  - 优点：纯数字双值，消费方一个 awk 拆开，无结构化解析成本；单行输出保持 `tail -1` 约定兼容；改动面最小
  - 风险：消费者需同步改（I6 已锁定必须同步）；`awk` 依赖 POSIX（现有脚本已广泛用 awk，风险低）
  - 工作量：py ~6 行改 + sh ~6 行改 + 2 个测试文件断言同步

#### 候选方案 B：结构化输出（JSON / `main:N aux:N`）

- **做法**：count.py 输出 `{"main":1,"aux":2}` 或 `main:1 aux:2`，消费方解析
- **权衡**：
  - 优点：字段名自描述，可读性好
  - 风险：check-gate.sh 消费需额外解析（JSON 需 python 二次调用或 sed 抽取）；`main:` 前缀与 markdown 其他键可能误命中；对本任务「一个 WARNING 计数」场景属过度设计
  - 工作量：py ~8 行 + sh 解析 ~8 行 + 测试同步

**选择理由**：方案 A 以最小改动实现「主/辅可区分」，单行双值在 bash 消费下最稳；方案 B 的结构化收益在本场景（单一消费方、单条 WARNING）不成立。

> 设计注（不触发 [SCOPE+]）：现状 count.py 的正则 `^  (P5\w*):` 会把 `P5_formatter` 计入命令数，与 read-p5-commands.py（执行枚举跳过 formatter）语义不一致。本方案在拆分主/辅时让 aux 排除 `_formatter`，顺带消除该偏差——属 RM-AG0011「计数语义修复」的自然组成部分，不扩大文件改动面（仅 py 内一行过滤）。

**BDD-3 落实**：GPC.1 改断言 `1 2`（1 主 + 2 辅）。
**BDD-4 落实**：check-gate.bats G5_CMD.1/5 改断言主/辅文案。
**BDD-5 落实**：G5_CMD.2（仅 P5）断言不 WARNING，保持不变。
**BDD-6 落实**：read-p5-commands.py 不改；agate-read-p5-commands.bats P5C.* 保持全绿即守卫。

### 2.3 RM-AG0012① — Review 指令按角色类型条件注入（BDD-7/8/9）

**设计目标**：执行角色派发 prompt 不含「Review 角色特别指令」（status draft→approved 语义），评审角色含完整语义。

#### 候选方案 A：模板拆分独立块 + render 按 ROLE_DIR 追加【选择】

- **做法**：
  - `assets/templates/dispatch-prompt.md`：
    - 从主代码块（L9-13）**移除**「## Review 角色特别指令」节
    - 在 `## 阶段特定提示（按需追加到 prompt 末尾）` 下新增首个子节 `### Review 角色特别指令`（含完整指令文本的代码块，内容原样保留——含 status draft→approved/rejected/needs-revision 完整语义）
  - `agate-render-dispatch-prompt.sh`：
    - 复用阶段追加的既有提取惯用式（`sed -n '/^### X$/,/^### /p' | sed '/^### /d' | extract_first_code_block`），新增 review 追加分支：
      ```bash
      review_appendix=""
      if [ "$ROLE_DIR" = "review-roles" ]; then
          review_appendix="$(sed -n '/^### Review 角色特别指令$/,/^### /p' "$TEMPLATE" | sed '/^### /d' | extract_first_code_block)"
      fi
      ```
    - 组装顺序：`rendered = main_block` → 有 review_appendix 则追加 → 有阶段 appendix 则追加（review 指令位于阶段追加之前）
  - `dispatch-protocol.md` 内联模板（L427-494，I7）：在「## 你的角色定义」后加一句备注——「若派发评审角色（review-roles），须追加 assets/templates/dispatch-prompt.md 中评审角色专用节的 status 字段语义说明」。**避免在 dispatch-protocol.md 出现「Review 角色特别指令」字面量**（BDD-9 要求全仓该指令仅模板一处）
  - 测试：agate-render-dispatch-prompt.bats 新增 RP.18（execution 角色不含 Review 指令，BDD-7）+ RP.19（review 角色含 Review 指令 + approved/rejected/needs-revision 完整语义，BDD-8）
- **权衡**：
  - 优点：完全复用既有「### 节 + sed 范围 + extract_first_code_block」追加机制，render 脚本零新惯用式；执行/评审分叉由 ROLE_DIR（L63-69 已有）天然驱动；BDD-9 守卫不变（指令文本仅存于模板）
  - 风险：评审角色渲染出的 prompt 中 Review 指令位置从「开头」移到「末尾（阶段追加之前）」，语义等价但顺序变化——评审理据不依赖顺序（RP.15 已有 review-roles 识别保障）；模板主代码块与「## 阶段特定提示」边界已由既有 main_block 提取（L78）覆盖，拆块不破坏该边界
  - 工作量：模板拆块 + render 8 行 + 内联模板备注 + 2 个测试

#### 候选方案 B：模板不动，render 对 execution 角色 sed 剥除

- **做法**：模板保留 Review 节在主代码块内；render 在组装后若 ROLE_DIR=execution-roles，用 sed 范围 `'/^## Review 角色特别指令$/,/^## 你的角色定义$/'` 剥除该节
- **权衡**：
  - 优点：评审角色 prompt 顺序不变（Review 指令仍在开头）
  - 风险：render 脚本硬编码模板两个节标题（「Review 角色特别指令」+「你的角色定义」）做范围边界，标题改动即静默失效 → 回归为无条件注入（BDD-7 测试可抓但属「防呆靠测试」而非机制自洽）；剥除逻辑与既有追加机制不是同一族惯用式，维护认知负担
  - 工作量：render ~4 行 + 2 个测试

**选择理由**：方案 A 把「评审指令只给评审角色」做成**机制**（追加而非剥除），与既有阶段追加完全同构，模板是唯一内容源（BDD-9 语义最强）；方案 B 是「先全注入再剥除」，依赖标题字符串且剥除易脆。顺序变化可接受（review 指令仍完整在 prompt 内）。

**BDD-9 落实**：修复后 `rg -n 'Review 角色特别指令' agate/` 仅命中 assets/templates/dispatch-prompt.md（单文件，内含节标题 + 代码块指令文本各 1 处，同一文件不违反「模板一处」语义）。

### 2.4 RM-AG0012② — render 角色不存在 exit 2 回归测试（BDD-10/11）

**背景**：缺陷 v0.23.0 已修复（角色不存在 exit 2 + stderr 报错），P1 实测确认；仅缺 bats 回归锁定。

#### 候选方案 A：复用既有测试文件，新增 RP.17【选择】

- **做法**：`agate/tests/unit/agate-render-dispatch-prompt.bats` 末尾新增：
  ```bats
  @test "RP.17: 角色文件不存在 -> exit 2 + stderr 报错（回归锁定 v0.23.0 修复）" {
      run bash "$AGATE_ROOT/scripts/agate-render-dispatch-prompt.sh" P2 nonexistent-role "$TEST_TASK_DIR"
      [ "$status" -eq 2 ]
      [[ "$output" == *"角色文件不存在"* ]]
  }
  ```
  - 同步 `agate/tests/README.md` L33 计数表：render 16 → **20**（RP.17/18/19 三条新增；现表记 16 实际 17——P1 I8 已确认既有 1 漂移，按实际 20 同步）。该测试即 BDD-11 要求的回归锁定（RP 系列新增编号 + 断言 exit 2 + stderr 报错）
  - `follows_existing_pattern: [agate/tests/unit/agate-render-dispatch-prompt.bats]`——RP.2/RP.3 已有 exit-2 + 参数错误断言模式，直接套用
- **权衡**：与既有错误路径用例（RP.2 非法 phase / RP.3 目录不存在）同文件同风格，便于维护；不加新文件避免文件碎片
- **风险**：无（纯测试新增，行为已修复）

#### 候选方案 B：独立 `.bats` 文件收纳错误路径用例

- **权衡**：优点是错误路径用例集中；缺点是渲染脚本已有 RP.2/RP.3 exit-2 断言在同文件，拆开反而割裂同类断言，且新增文件增加 count-tests 计数表行
- **工作量**：略高

**选择理由**：方案 A 遵循既有 RP 测试编号与错误路径断言风格（RP.2/3），改动最小、语义内聚；方案 B 的集中收益不抵文件碎片成本。

### 2.5 RM-AG0003 — 空返回自动重试（BDD-12/13/14）

**设计目标**：dispatch-protocol.md 空返回恢复策略（L105-135）增量增强——首次空返回自动重试一次 + 短会话（<1min）异常告警；不改变既有 retry 上限 / PAUSED 语义。

#### 候选方案 A：自动重试为「不占槽位的前置动作」【选择】

- **做法**：重写 L111-118「第 1 次空返回」小节为：
  ```
  1. 第 1 次空返回：
     a. 自动重试一次：相同 prompt 原样重发（本次自动重试不占用 retries[Pn] 槽位）。
        - 复用下方 L128 派发耗时弱信号：若本次会话时长 <1min → 输出「会话时长异常短」告警
          （提示可能为平台抖动 / 额度中断，而非任务结构问题），并照常自动重试一次。
        - 自动重试仍空返回 → 进入步骤 b。
     b. 计入 retries[Pn]（现成规则），记录 failure_mode: empty_return, prompt_changed: false, adjustment: null
     c. 分析失败原因：prompt 是否过复杂？输入文件是否过多？任务粒度是否过大？
     d. 调整策略后重派：拆分任务 / 补输入导航 / 换 subagent 类型
     e. 更新本次 retry 记录：prompt_changed: true, adjustment: <具体调整>
  ```
  - 在「禁止」段（L124）后补一句关系说明：**「自动重试一次」是「相同 prompt 直接重试」禁令的唯一豁免**——仅限首次、单次、原样重发；自动重试失败后进入 b-e 流程，此后仍禁止不调整直接重试
  - L128 弱信号保持原文，仅被 a 引用；「会话时长 <1min 为异常判定阈值」明确写入 a
- **权衡**：
  - 优点：`retries[Pn]` 计数时机后移一拍（自动重试不占槽位），MAX_RETRY / PAUSED 判定点与改造前完全一致（BDD-14 最强满足）；短会话告警复用既有耗时弱信号（I10），不另起炉灶；与「禁止不调整重试」边界清晰（单次豁免显式声明）
  - 风险：`retries[Pn]` 首次计数时机变化属文档语义微调——BDD-12 明确要求「自动重试后仍空返回才进入既有 retries[Pn] 流程」，与 P1 基线一致，非越界
  - 工作量：纯文档措辞，约 20 行改写

#### 候选方案 B：自动重试占用 retries[Pn] 槽位

- **做法**：首次空返回先计入 retries[Pn]，再自动重试；自动重试失败直接判定是否超 MAX_RETRY
- **权衡**：优点是计数路径不变；风险是短会话场景（平台抖动）被计入 retries[Pn]，1 次抖动即消耗 1 次重试预算——与 BDD-12「自动重试后仍空返回才进入既有 retries[Pn] 流程」及 BDD-14「不改变重试语义」冲突（重试上限语义被压缩）
- **工作量**：文档，更少

**选择理由**：方案 A 让「自动重试」成为对平台抖动的免费快速恢复路径，失败后才消耗重试预算，与 BDD-12/14 的措辞逐字吻合；方案 B 会把异常抖动计入重试预算，改变既有上限语义，违反 P0-brief「增量增强，不改现有重试语义」。

**BDD-12/13/14 落实**：均为 dispatch-protocol.md 文档措辞——BDD-12 由步骤 a/b 的「自动重试一次」+「自动重试后仍空返回才进入既有 retries[Pn] 流程」落实；BDD-13 由「会话时长 <1min → 输出『会话时长异常短』告警（复用 L128 派发耗时弱信号）」落实；BDD-14 由「自动重试不占用 retries[Pn] 槽位」+「retry 上限/PAUSED 段未改」落实。P6 以文本断言核对（含「自动重试一次」「会话时长异常短」「<1min」字样 + retry 上限/PAUSED 段未改）。

### 2.6 同类扫描守卫 / check-debt.sh 依赖加载失败（BDD-15/16）

**背景**：check-debt.sh `--retreat-coverage` 模式 L24-30 依赖 agate-workspace-resolve.sh，缺失或 source 失败时 stderr 报错但 exit 0（静默成功）。无脚本调用方（仅 agate-retreat-to.sh:72 注释 + 文档提及）→ 改 exit code 无 hook 波及面。

#### 候选方案 A：依赖加载失败改 exit 2（WARNING 语义）【选择】

- **做法**：
  - L26（source 失败）：`|| { echo "GATE DEBT: 无法加载 agate-workspace-resolve.sh" >&2; exit 2; }`
  - L28（文件缺失）：消息改为 `GATE DEBT: 缺少 agate-workspace-resolve.sh，无法解析工作区，回退覆盖比对无法执行`，`exit 0` → `exit 2`（原「跳过回退覆盖比对」措辞删去——依赖失败不是「跳过」，避免 BDD-15 扫描把失败误判为有意跳过）
  - 头部注释 L5/L13 同步：「覆盖模式：依赖加载失败 exit 2（需主 Agent 自判），无 retreat 提交等有意跳过分支仍 exit 0」
  - 「有意跳过」分支（L35-37 无 retreat 提交 → exit 0）保持不变
  - 新增测试（agate-debt-check.bats）：临时脚本目录仅放 check-debt.sh（无 agate-workspace-resolve.sh）→ 断言 exit 2 + stderr 含「缺少 agate-workspace-resolve.sh」；对照既有 test_bdd_13/14/15（有 resolve 脚本）仍 exit 0/1 语义不变
  - 修改既有 test_bdd_13 场景不变（resolve 脚本存在）
- **权衡**：
  - 优点：与 check-gate.sh「exit 2 = 需主 Agent 自判」约定一致；BDD-15 扫描 `rg -n '>&2;\s*exit 0'` 命中行清零（check-debt 不再命中，剩余仅 agate-capture-env-baseline.sh 三处显式「跳过」语义）→ 守卫语义清晰
  - 风险：无脚本调用方依赖 exit 0（已核实），exit 2 只影响「手动运行该工具」的主 Agent——正是设计意图（让它知道回退覆盖比对没跑成）
  - 工作量：sh ~6 行 + 1 个测试 + 头注释

#### 候选方案 B：依赖加载失败改 exit 1（硬失败）

- **权衡**：优点是失败信号最强；风险是与 check-debt.sh「只读 WARNING 不阻断」的文档定位冲突（state-transitions.md L84 / UPGRADING.md L120 均声明「不阻断 commit/发布」），exit 1 会误导后续 gate 判定为硬拦截；且 BDD-16 建议 exit 2（P1 原文「建议 exit 2 WARNING，与 check-gate.sh 约定一致」）
- **工作量**：sh ~6 行

**选择理由**：方案 A 的 exit 2 精确匹配「该比对是只读 WARNING 工具，但工具自身故障不应静默成功」——依赖失败暴露给主 Agent 自判，不误伤「不阻断」定位；方案 B 的 exit 1 与文档「不阻断」声明冲突。P1 已裁定「同同类」并建议 exit 2，A 为唯一自洽实现。

**BDD-15 落实**：P5 跑 `rg -n '>&2;\s*exit 0' agate/scripts/*.sh` 断言仅剩含「跳过」语义的 3 行（agate-capture-env-baseline.sh）。
**BDD-16 落实**：新增测试断言依赖缺失 → exit 2 + stderr 报错；「有意跳过」（无 retreat 提交）仍有既有测试断言 exit 0。

## 3. gate_commands

```yaml
gate_commands:
  P3: "bats agate/tests/unit/agate-render-dispatch-prompt.bats agate/tests/unit/check-gate.bats agate/tests/unit/agate-gate-p5-count.bats agate/tests/unit/agate-debt-check.bats"
  P5: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict"
  P5_shellcheck: "shellcheck -S warning agate/scripts/*.sh"
```

- P5 声明 1 主 + 2 辅命令 → 恰为 RM-AG0011 新计数逻辑的真实样例（P5 gate 时输出「1 个主命令 + 2 个辅助命令」WARNING，in-situ 验证 BDD-3/4）
- consistency 必须用 worktree 自己的脚本（I13）；命令 `python3 agate/scripts/...` 以 worktree 为工作目录执行时即 worktree 脚本
- shellcheck glob `agate/scripts/*.sh` 由 shell 展开（gate 执行时工作目录在 worktree 根）

## 4. files_to_read

```yaml
files_to_read:
  - path: agate/scripts/agate-gate-p5-count.py:14-20
    why: 主/辅计数改动点（gate_commands 块提取 + P5/P5_* 正则拆分 + aux 排除 _formatter）
  - path: agate/scripts/check-gate.sh:249-259
    why: P5 WARNING 消费逻辑（读 count.py 双值、主/辅文案、触发条件 P5_TOTAL>1）
  - path: agate/scripts/agate-read-p5-commands.py:21-37
    why: 参照其 _formatter 排除语义（L29-30），count.py aux 口径须与其对齐（不改本文件）
  - path: agate/assets/templates/dispatch-prompt.md:6-101
    why: Review 指令拆独立块（原 L9-13 移除 → 新 ### Review 角色特别指令 节）；main_block 边界（## 阶段特定提示）不被破坏
  - path: agate/scripts/agate-render-dispatch-prompt.sh:63-106
    why: 条件注入实现点（ROLE_DIR 判定、review_appendix 提取、组装顺序）
  - path: agate/dispatch-protocol.md:105-135
    why: 空返回恢复策略改写（自动重试 + <1min 告警 + 与禁止段关系）
  - path: agate/dispatch-protocol.md:427-494
    why: 内联模板语义一致性备注（I7，避免 Review 指令字面量出现）
  - path: agate/scripts/check-debt.sh:19-50
    why: 依赖加载失败 exit 0→2（L26/L28）+ 头注释同步 + 有意跳过分支保留
  - path: agate/role-system.md:50-68
    why: C8 表 backend 行补 plan-eng-review + 去重说明
  - path: agate/rules/review-mapping.md:15-30
    why: C8 表 backend 行拆 P2/P4 两行 + 去重说明
  - path: agate/phase-cards/P2-design.md:89-101
    why: C8 表新增 backend 行 + 去重说明
  - path: agate/tests/unit/agate-render-dispatch-prompt.bats
    why: 新增 RP.17（角色不存在）/RP.18（exec 无 Review 指令）/RP.19（review 有完整语义）
  - path: agate/tests/unit/check-gate.bats:606-704
    why: G5_CMD.1/G5_CMD.5 断言同步主/辅文案；G5.1/G5_CMD.2/3/4 保持不变
  - path: agate/tests/unit/agate-gate-p5-count.bats:5-22
    why: GPC.1 改断言 1 2 / GPC.2 改断言 0 0
  - path: agate/tests/unit/agate-debt-check.bats:428-534
    why: 新增依赖缺失 exit 2 测试（对照 test_bdd_13/14/15 既有语义）
  - path: agate/tests/README.md:28-59
    why: render 计数表 16→20 同步（I8）
```

## 5. env_constraints

```yaml
env_constraints:
  debug_env: "worktree /home/kity/oclab/agate/.worktrees/agate-TAG0005-0009（协议 v0.44.0 基线）；Linux UTF-8；bats 1.10 / python3 3.12+pyyaml / shellcheck 已确认（P1 能力声明）"
  isolation_check: "全程仅在 worktree 操作；gate/consistency 用 worktree 自己的脚本；hook 判定走 ~/.agate 稳定版（不改 hook）；主 checkout /home/kity/oclab/agate 禁止改动"
```

## 6. minimal_validation

```yaml
minimal_validation:
  assumption: "本任务为纯代码逻辑（脚本条件分支 / 文档措辞），无外部系统依赖"
  method: "实测现状行为确认各缺陷前提成立：① count.py 对 P5+P5_unit+P5_e2e 输出合并值 3、对仅 P5 输出 1（合并计数缺陷）② render 对 execution 角色（architect）与 review 角色（design-review）均注入「Review 角色特别指令」（无条件注入缺陷）③ render 派发不存在角色返回 exit 2 + stderr「角色文件不存在」（v0.23.0 已修复，仅缺回归）④ check-debt.sh 在缺少 agate-workspace-resolve.sh 时 stderr 报错但 exit 0（静默成功缺陷）"
  result: "confirmed"
  note: "依赖的内部函数/数据转换：agate-gate-p5-count.py 的 gate_commands 块正则（L14）+ P5 键正则（L19）；check-gate.sh 对 count.py 输出的 tail -1 消费（L253-254）；agate-render-dispatch-prompt.sh 的 main_block 提取（L78 sed '1,/^## 阶段特定提示/'）+ extract_first_code_block（L74-76）+ ROLE_DIR 判定（L63-69）+ sed 占位符替换（L128-142）；check-debt.sh 的 source 依赖加载模式（L24-30）；read-p5-commands.py 的 _formatter 排除（L29-30，不改、仅对齐）。四处缺陷均在 P2 阶段以最小验证实测复现，无外部系统行为假设。"
```

## 7. 完成标准（实现完成的标志）

1. 三处 C8 表 backend 行含 P2 触发角色（plan-eng-review）+ 去重说明；check-gate.sh P2 分支未动（BDD-1/2）
2. count.py 输出 `MAIN AUX`；check-gate.sh P5 WARNING 文案区分主/辅；GPC/G5_CMD 断言同步全绿；read-p5-commands.py 未改且 P5C 全绿（BDD-3/4/5/6）
3. render：execution 角色渲染不含 Review 指令、review 角色含完整 status 语义；全仓 `rg 'Review 角色特别指令'` 仅命中模板一处；RP.18/19 绿（BDD-7/8/9）
4. RP.17 绿（exit 2 + stderr 报错）；README render 计数 16→20（BDD-10/11）
5. dispatch-protocol.md 空返回策略含「自动重试一次」「会话时长异常短」「<1min」；retry 上限/PAUSED 段未改（BDD-12/13/14）
6. check-debt.sh 依赖失败 exit 2 + 新测试绿；`rg -n '>&2;\s*exit 0' agate/scripts/*.sh` 仅剩 3 处「跳过」语义行（BDD-15/16）
7. 全量 bats 全绿 + consistency 0 ERROR + shellcheck 0 error；commit message 含 self-gate-review 标记（I12）

## 8. 范围确认

- 本设计未发现需超出 P1 锁定范围的新增改动（无 [SCOPE+] 条目）。
- 唯一新增的边界认知：count.py aux 排除 `_formatter` 是对现状「formatter 被计入命令数」的顺带修正，属 RM-AG0011 计数语义修复的自然范围，已在 §2.2 设计注明，不改文件改动面。
- `[PROD_NOT_TOUCHED]`——本阶段仅读取 worktree 协议文件与脚本并运行本地最小验证，未接触生产环境。
