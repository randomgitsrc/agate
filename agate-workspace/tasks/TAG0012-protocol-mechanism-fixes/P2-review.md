---
phase: P2
task_id: TAG0012-protocol-mechanism-fixes
type: review
parent: P2-design.md
trace_id: TAG0012-P2-review-20260818
status: approved
created: 2026-08-18
agent: plan-eng-review
---

# P2 方案评审 — 工程经理视角（plan-eng-review）

> 评审对象：`P2-design.md`（candidate_count: 3，dispatch_plan 8 批，声称覆盖 P1 全部 23 条 BDD）
> 对照基线：`P1-requirements.md`（risk_level: high，23 条 BDD，BDD-1~22 + BDD-15b）
> 方法：逐条核对 BDD 覆盖映射；对文中引用的所有代码/协议行号、函数名、机制描述实际读取源码验证，不采信文档自述

## 架构问题（阻塞级）

无。

## 架构问题（非阻塞）

1. **批次表（§5.3）对 `dispatch-protocol-core` 批次的文件覆盖描述不够精确**：批次表写"dispatch-protocol.md（verification_env 节 + 并行规则 + 派发prompt模板正文，三处新机制原文）"，只枚举了 3 处改动点；但 §2.1 改动落点表中 `dispatch-protocol.md` 实际有 4 个改动点，第 4 处是 BDD-13 的"L521「非阶段产出的路径规范」示例块"条件性子句（判定该场景是否适用命令超时兜底展开）。因为这 4 处改动点都落在同一批次（同一文件同一 wave），P4 实现时不会因批次拆分导致真正遗漏，但批次表本身的"文件覆盖"描述与 §2.1 表不完全对齐，不满足 dispatch-context 要求的"8 批次划分应与 §2.1 表严格对齐"。建议 architect 在批次表该行补一句提及 L521 条件性子句，避免后续任务照抄本设计的批次描述范式时产生"批次描述 = 完整改动清单"的误解。
2. **verification_env 现状定性略有出入**：`dispatch-protocol.md` 中的 `verification_env 条件化` 实际是「可判定门槛规范」大节（`##`）下的一段加粗段落（L952-957 共 6 行 2 句话），不是独立的 `###` 子节。P2-design.md 多处称其为"节"（如 §2.1「verification_env 节，L940-960 现状」），实际内容远小于声明的 L940-960 范围（该范围内含大段其他内容：P5 gate 验证方式表、C7 规则等，verification_env 本身只占其中约 6 行）。这不影响 BDD-10/11 的可实现性（P4 落地时按 files_to_read 精确定位即可），但设计文档对"现状"的描述有一定夸大，建议 P4 implementer 阅读时以实际内容（L952-957）而非声明的 L940-960 范围为准，避免误判现状规模。
3. **`candidate_count: 3` 的语义是"三个正交设计维度各选 1"，而非正文候选方案写法总数（A1/A2/B1/B2/C1/C2 共 6 个候选文本块）**：P2-design.md 已自行注明该语义（"A/B/C 三维度各选 1，每维度均 ≥2 候选 + 权衡 +理由"），gate（`check-gate.py` 的 candidate_count 校验）只做数值阈值比较不解析正文，两种计数口径（3 或 6）都能通过 gate（≥2）。这是一种此前少见的"多维度候选"组织方式，语义本身自洽、不构成缺陷，但建议后续同类多维度设计任务显式沿用这一约定（写清楚 candidate_count 计的是"维度数"还是"候选文本数"），避免不同 architect 对该字段口径理解分裂。

## 测试缺口

- `test_protocol_mechanism_anchors.py`（§3.6，BDD-22 强制项）是纯关键词存在性断言（grep-in-text 模式），只能验证"该关键词是否落盘"，不能验证：
  - 规则文本的语义正确性（如"止损轮次=2"这个数字是否真的被写对、READY 后三条归属判据的措辞是否真的可判定）
  - `timeout_seconds` 在 P2 卡/architect.md/task-files.md 三处的实际取值/说明是否语义一致（只能各自验证关键词是否出现，无法验证三处内容不矛盾）
  这一测试缺口是协议文档类任务的固有限制（P2-design.md §3.6 自己也承认"回归拦截"而非语义验证），语义正确性由 P6 verifier 逐条 BDD PASS/FAIL 判定兜底，可接受，非阻塞，但记录在案供 P6 阶段verifier 提高注意力。

## 锁定决策

1. **verification_env 失败处理协议**（候选 A1）：止损轮次=2、独立计数不入 `.state.yaml`（由主 Agent 手工记录）、可/不可重试清单、批处理强制要求、READY 后三条归属判据（①本任务遗留 ②环境本身问题 ③证据不足默认按①）——规则具体、可执行，非"看情况"式空话，采纳。
2. **timeout_seconds 关系判定**（候选 B1）：排除 P3（P3 继续用既有 `AGATE_TDD_TIMEOUT` env var 机制，理由具体：改为互斥覆盖需要新增 `agate_common.py`/`check-tdd-red.py` 运行时消费链路，超出 P0-brief"少量脚本 schema 字段"定性）；per-key 声明；三档基准表（120s/300s/600s）有具体依据（分别锚定 `AGATE_TDD_TIMEOUT` 默认值、Playwright 内部 HARD 超时余量、TPV0093 188min 教训），非拍脑袋——采纳。
3. **P0-brief 漂移判据**（候选 C1）：checklist 3 条严重 / 2 条轻微，checklist 命中 TAG0008 真实案例（技术路线切换），比时间阈值方案（C2，已被 TAG0008 证伪）更贴合实际——采纳。
4. **BDD-22 分支决定：`check-gate.py` 不新增 `timeout_seconds` 脚本硬校验**：理由具体（该字段目前零运行时消费方，浅校验收益有限），非空话，BDD-22 本身允许两分支皆为合法收敛，予以认可。**个人倾向意见（非阻塞、供 architect 参考，不代为拍板）**：即便暂无运行时消费方，参照既有 `_gate_p2_dispatch_plan` 对 `parallel_limit` 的 `int ≥1` 校验先例，加一个最基础的数值合法性检查（如"若声明则须为正整数"）成本很低、能在文档层就拦住明显笔误（如 `"300seconds"` 这类格式错误），但这不是必须项，本次评审不因此判定 rejected。
5. **五维评估（§5.1）与 8 批次划分（§5.3）**：五维评估依据具体（13 个改动文件、7 个输入文件等实际数字，非套用模板），与 `architect.md`「批次设计」节的五维评级表完全对齐；8 批次边界与 §2.1 改动落点表基本严格对齐（唯一瑕疵见「非阻塞」第 1 条，已单独说明，不影响整体判定）。
6. **BDD 覆盖映射（§4）核对结果**：逐条核对 P1-requirements.md 的 BDD-1~22 + BDD-15b（共 23 条）与 P2-design.md §4 覆盖表，编号一一对应，无遗漏、无编号错位，各条款落点与内容均与 P1 对应 BDD 的 Given/When/Then 语义吻合（含 BDD-16 的 4 个子问题、BDD-13 的规范正文+条件性子句拆分、BDD-10 的 4 个子问题等均逐一在 P2 正文找到对应文本）。
7. **多方案探索真实性**：A2/B2/C2 三个未采纳候选均为可行的真实替代方案（非稻草人）——A2（并入 `retries[Pn]`）、B2（互斥覆盖含 P3）、C2（时间阈值判据）均给出具体实现路径和实质性缺点论证（分别对应"违反 P1 已警示反模式""需新增运行时消费链路""被 TAG0008 案例证伪"），满足 architect.md 反稻草人要求。
8. **P0-brief 约束 4（范围锁定）核对**：§8 `[SCOPE+]` 声明为空，§2.1 改动文件与 P1 §3 十一个文件分组严格对齐，未发现范围外扩内容。
9. **最小验证（minimal_validation）核实**：声明"纯代码逻辑，无外部系统依赖"，列出 4 项已验证的内部依赖（`agate_common.py:395-425`、`check-protocol-consistency.py` CHECK3/PROTOCOL_FILES、`check-gate.py` `_gate_p2_dispatch_plan`、`test_check_protocol_consistency.py` 测试组织模式），经独立复核，全部引用的行号/函数名/逻辑与实际源码一致，验证真实完成而非声明性走过场。
10. **技术债**：`verification_env` 止损轮次无脚本强制、靠主 Agent 人工记录这一取舍点，architect 已在 §2.3 风险表显式承认并说明是范围约束下的合理取舍（不新增 `.state.yaml` 字段），评审认可不需登记为正式 DEBT 条目（范围内、影响可控、已有缓解说明）。

## 判定

**status: approved**，阻塞问题数量：0。
