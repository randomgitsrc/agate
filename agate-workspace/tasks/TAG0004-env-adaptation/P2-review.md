---
phase: P2
task_id: TAG0004-env-adaptation
type: review
parent: P2-design.md
trace_id: TAG0004-P2-20260813
status: approved
created: 2026-08-13
agent: review
---

# P2 方案评审 — TAG0004 脚本健壮性 + 环境适配

## 结论

**approved**。方案锚点：**候选 1A**（S1 数组化）、**候选 2A**（S3 grep 断言审计）、**候选 3A**（S2 负类加宽）、**候选 4A**（M4/M5 alternation）、**候选 5A**（M6 frontmatter CRLF 容错）、**候选 6A**（M9 grep -F 前缀）、**候选 7A**（Q1 归一化剥离）、**候选 8A**（Q2 卡片补注）、**候选 9A**（Q5 SETUP 章节）、**候选 10A**（RM-AG0001 反引号容错）、**候选 11A**（RM-AG0002+TPV0090 A/B 判定）、**候选 12A**（CI windows matrix）、**候选 13A/14A/15A/16A**（其他项）。方案充分、映射完整、风险已识别并有缓解，Q2 边界正确、协议语义未破坏。以下逐项评审。非阻塞观察项见末尾，供 P3/P4 执行时留意，不构成打回理由。

## 1. 候选方案充分性 — 通过

- **candidate_count=28 属实**：逐块清点正文候选（1A/1B…12A/12B 共 12 组 × 2 + 13A/14A/15A/16A 共 4 个 = 28），与 frontmatter `candidate_count: 28` 一致，与 check-gate.sh P2 读取逻辑（L141 `^candidate_count:`）匹配。
- **M6/S1/Q1 各 ≥2 候选**：S1（候选 1A/1B）、M6（候选 5A/5B）、Q1（候选 7A/7B）均含 做法/优点/风险/工作量 + 选择理由，满足 architect 派发约束（dispatch-context "M6/S1/Q1 至少各需 2 个候选"）。
- **稻草人检测通过**：备选方案均为真实可行的替代路径而非明显陪衬——
  - 候选 1B（IFS 换行）确实改动更小，其落选理由（PROCESSED_DIRS 成员判断换行化更绕）成立；
  - 候选 5B（.gitattributes `*.md eol=lf`）确实是"源头解决"，落选理由（污染历史 CRLF review 文件、违背 BDD-16/P1 SUGGEST）成立；
  - 候选 7B（basename）确实实现最简单，落选理由（破坏 pre-commit-gate.sh L202-220 的 hash 校验相对路径契约）成立。
- 各"选定"方案的选择理由与 P0-brief/P1 SUGGEST 方向一致（M6 frontmatter 容错、S3 grep 断言审计、RM-AG0002 保守判定）。

## 2. BDD 映射完整性 — 通过

§2 映射表逐条核对 P1 的 37 条 BDD：**BDD-1..37 全部有设计落点**（脚本级 `grep -oE 'BDD-[0-9]+'` 排序去重 = 37/37）。抽查关键映射：

- BDD-1/2/3（S1 空格路径）→ 候选 1A + §3 场景清单 ✓
- BDD-10（S2 无扩展名拒绝）→ 候选 3A 负类 `[^()[:space:]]` 结构 + minimal_validation 负面用例 ✓（实测：`(见截图)` 拒绝、中文文件名匹配）
- BDD-21/22（Q1 Windows 归一化 + Linux 字节不变）→ 候选 7A "先试直接剥离" ✓
- BDD-23/24/25（Q2 纯文档）→ 候选 8A ✓（见 §6）
- BDD-30/31/35/36/37（A/B 判定矩阵）→ 候选 11A 一次覆盖 ✓

无 BDD 漏设计。全局类 BDD-32/34 落点在 §3 全局回归与 gate_commands.P5，合理。

## 3. 方案风险评审 — 通过（含缓解）

- **S1 数组化 Linux 回归**：§3 验证场景清单 9 项覆盖根级/任务级/多任务并发/空格路径/PROCESSED_DIRS/裁剪跳阶/PAUSED-READY-DONE/P6 证据。已核验 pre-commit-gate.sh 全部 STAGED_STATE_FILES/PROCESSED_DIRS 消费点（L45/50/57/337/339/343/350）都在清单覆盖逻辑内。候选 1A 自带 `set -u` 下 `+=()` 注意事项，合理。
- **S2 过宽放行真缺证据**：候选 3A 用 `[^()]*[^()[:space:]]\.[a-zA-Z0-9]+[^)]*` 维持"文件名+扩展名"结构（BDD-10 不放松），minimal_validation 已实测 `(见截图)` 拒绝。负类也接受部分标点（如 `:`）属已知可接受（与原始 `-` 同类）。
- **M4（TPV0090）NameError B 类误放行真实测试 bug**：候选 11A 用三道闸——仅"项目模块内"NameError 归 B 类（复用 `count_prefix`）、NameError 之外错误（TypeError 等）仍 A 类（BDD-37）、`globals().get()` 兼容（BDD-36）。风险已识别并有 BDD-37 兜底。
- **RM-AG0002 关键词误判**：候选 11A 风险节明确用 `Traceback|SyntaxError|ImportError|ModuleNotFoundError` 精确组合而非裸 `error:`，规避断言失败文本含 error 关键词的误判；实测 bats 无 formatter 降级路径（gate-result.sh L93-94）需要原始输出传入——设计已列出 gate-result.sh 的 files_to_read 并给出 `raw_output` 字段方案。

## 4. gate_commands 合理性 — 通过

- P3 `bats agate/tests/unit/ ...integration/`、P5 全量 bats + `check-protocol-consistency.py --strict` + `shellcheck -S warning`：均在本环境可执行（bats 1.10 / python 3.12 / shellcheck 已就绪）。
- **bats 无 formatter 降级说明自洽**：gate_commands 未声明 `P3_formatter` → check-tdd-red.sh 走 exit-code-only 路径；A/B 判定增强测试（BDD-30/31/35/36/37）在 check-tdd-red.bats / check-tdd-red-formatter.bats 内用 `TEST_RUNNER` 环境变量指向 fake 脚本的写法可行——已核验 check-tdd-red.sh L128-131 对 `TEST_RUNNER` 的 `collect_commands` 分支，与 AGENTS.md「mock pytest」约定一致。
- 无 UI（ui_affected: false），不需要 P5_e2e，正确。

## 5. minimal_validation 充分性 — 通过

6 项假设全部 `result: confirmed`，覆盖方案的关键外部依赖：

- M4/M5 POSIX locale（`LC_ALL=C` 实测 `[:：]` vs `(:|：)`）
- S2 正则加宽（中文/负面用例）
- Q1 路径前缀剥离（5 种路径形态，含混合斜杠/盘符大小写）
- RM-AG0001 反引号包裹（计数少 1 / 0）
- M9 grep -F（含 `[` 目录名）
- M6 CRLF frontmatter（sed 空输出 vs tr -d '\r'）

均为方案成立的前提假设（非纯内部逻辑可推断），验证方法可复现。S1/S3 属纯代码逻辑改动（bash 数组 / 机械加 encoding），无需外部行为验证，设计未错误声称外部验证，合理。

## 6. Q2 边界 — 通过

候选 8A 仅补注 7 张 phase-cards（P1:17 / P2:13 / P3:13 / P4:16 / P6:16 / P7:14 / P8:14）的推进步骤描述，明确声明"gate 判定逻辑零改动（BDD-24）"。已核验：

- P1/P2 卡仍为 mode B 旧写法（P1 L17 "phase=P1 → P2"、P2 L13 "phase=P2 → P3"），P5 卡已对齐规则 2（L14-19 含"phase = 本 commit 的产出阶段"）——Q2 修复目标与参照样例真实存在；
- git-integration.md 规则 2（L27-35）为对齐依据，属实；
- §1.8 全文未隐含任何 check-gate.sh / pre-commit-gate.sh 的判定逻辑改动 → 未超出 P0-brief 锁定范围，无需暂停问用户。
- 补注触发 SELF-GATE 已在 §0 风险表声明（commit message 需 `self-gate-review:`），正确。

## 7. 不破坏协议语义 — 通过

§0「不改什么」明确：.gitattributes md 规则、commit 顺序 / gate 判定逻辑、check-tdd-red.sh formatter 机制（含 formatter 时 A/B 判定与现状一致，仅加 NameError 分支）、.state.yaml 格式 / 阶段转移 / 角色体系、主 checkout 与 ~/.agate。所有改动均为"修正则 / 加 encoding / 路径归一化 / 文档补注"，不构成协议语义变更。与 P0-brief 核心约束 3 一致。

## 8. 非阻塞观察项（供 P3/P4 留意，不构成打回理由）

1. **§3 场景清单建议补一条**："任务级 .state.yaml 变更但无 P 产出（中间 commit / dispatch-context-only commit）"——pre-commit-gate.sh L228 有该分支（STAGED_IN_TASK 无 PHASE_OUTPUT 时不强制 dispatch-context），数组化改动理论上也会经过该路径。现有清单已含根级/任务级/多任务，缺此变体，P3 补 S1 回归测试时建议一并覆盖。
2. **候选 11A 关键词清单内部不一致**：正文写 `SyntaxError|IndentationError|ImportError|ModuleNotFoundError|error:`，风险节又建议去掉 `error:`。P3 写 BDD-30 测试时应以风险节的精确组合为准（含 `error:` 会误伤断言失败文本）。
3. **候选 7A 的 `\L` 小写转换**：GNU sed 扩展，Linux 侧可行；Windows Git Bash 自带 GNU sed 也支持，但若未来跑 BSD/macOS sed 会失效。P4 实现时建议用 `tr` 或 bash 参数替换替代，避免跨平台新隐患。
4. **候选 11A 的 NameError 解析依赖 formatter 变更**：pytest.sh 目前无 `name_errors` 字段（已核验 L46-55 输出结构），需给 formatter 加解析——P3 需先为此写失败测试（formatter 输出含 name_errors 时 judge_result 归 B 类），设计已列入 files_to_read（pytest.sh），路径正确。

## 门槛对照

- [x] P2-review.md 存在且非空
- [x] Header status: approved（agent: review ≠ main）
- [x] 结论引用实质锚点（候选 1A-16A + 各关键权衡评估）
- [x] 覆盖：候选方案充分性 / BDD 映射完整性 / 方案风险 / gate_commands / minimal_validation / Q2 边界

`[PROD_NOT_TOUCHED]` 本评审仅读 worktree 内文件并跑只读验证（grep/sed/正则匹配），未接触任何生产环境。
