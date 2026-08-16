## P1-progress（analyst 分阶段落盘）

### 2026-08-16 读取输入文件
- [x] P1-dispatch-context-analyst.md（派发指引已读：目标=需求基线+同类扫描影响面表；约束=字段契约定死/强制扫描/BDD 二值判定/路径硬约束）
- [x] analyst.md 角色定义（七节结构、frontmatter 机器字段、NEED_CONFIRM/SUGGEST 分级、capability_requirements 三态）
- [x] P0-brief.md（task/issues/known_risks/executor_env/env_constraints）
- [x] approved plan（agate-dispatch-orchestration-20260815.md）：Goal/Architecture/File Structure/Task1-6/验收标准/风险。关键：dispatch_plan 字段契约（frontmatter 单行 flow + mode 5 值 + agate-md-field-get.py 新 op + 不入 frontmatter-check schema + 向后兼容）
- [x] WORKFLOW.md「需求与验收机制」（需求基线活基线/SCOPE+/定向回补/NEED_CONFIRM 默认自走）
- [x] dispatch-protocol.md 部分（空返回恢复 L118「任务粒度指引」引用 / L132 引用 / L211 P0-brief task 字段引用）
- [x] dispatch-protocol.md「任务粒度指引」节 L639-663 全文（输入/产出数量上限、拆分原则、按包拆分并行、P7 例外）+ 3 处引用（L118/L132/L211）
- [x] 阶段卡 grep「按包拆分并行」：P3 L74 / P4 L94 / P5 L113 / P6 L147（证据并行模式）；P7 L99 不拆分例外；P2/P4 有评审专家组并行（不同概念）
- [x] P1-requirements.md 阶段卡片全文（gate/推进/评审/P1 基线保护）
- [x] P2-design.md 卡片全文（candidate_count 机器字段、四字段、C8 评审映射、gate）——dispatch_plan 将与之同级
- [x] P3/P4/P5/P6 卡片「按包拆分并行」节全文（P3 拆分判据/各自写测试文件；P4 共享文件后处理+基础设施隔离 L111-117；P5 只读无冲突+隔离 L121-127；P6 证据并行+汇总 verifier L147-157）
- [x] P7 不拆分例外 L97-102；P8 releaser 节（当前单 releaser，无多包拆批）
- [x] dispatch-prompt.md 模板全文（L4 已声明与 dispatch-protocol「派发 prompt 模板」节同步、权威源在协议文件；当前无粒度兜底内联约束）
- [x] grep 确认：architect.md 当前无「批次设计/dispatch_plan/拆分」任何内容（与 plan 断言一致，新增节）
- [x] dispatch-protocol.md L429 有「派发 prompt 模板」节（内联版，权威源）
- [x] dispatch-protocol.md L429-483「派发 prompt 模板」内联节全文（权威源）；architect.md 全文（P2 产出字段结构确认）
- [x] agate-md-field-get.py 全文（KNOWN_OPS 注册/双读判别/_format_value 无 dict→json.dumps 分支——N9 修改点确认）
- [x] check-gate.py gate_p2（L291-366）全文：candidate_count 正则逐行（非 _md_field_get）、四字段检查、_md_field_get 子进程模式（L115-129，env FILE）
- [x] 确认 plan N8 所指：candidate_count 是 L301-307 正则读，_md_field_get 子进程是 pass/blocker_count 同路径
- [x] test_check_gate.py：P2 gate 测试结构（_write_p2_design/add_p2_candidate_count/add_p2_review/_run_gate 模式，1907 行）——dispatch_plan 测试将复用该 fixture 模式
- [x] ~/.agate 脚本引用路径扫描完成：check-gate.py 被 pre-commit-gate.py / ci-gate-backstop.py / agate-summary.py / check-protocol-consistency.py / 多个测试引用；agate-md-field-get.py 被 check-gate.py / check-pruning.py / check-p6-evidence.py / check-p6-provenance.py / check-scope-resolved.py / test_agate_md_field_get.py 引用

### 2026-08-16 产出 P1-requirements.md（完成）
- [x] 已写入 P1-requirements.md（272 行）：frontmatter（risk_level: high / phases: 全 P0-P8 / packages 3 个 / domains: docs,scripts,tests / capability_requirements 4 条全 available）
- [x] 含 21 条 BDD（#### BDD-NN: 格式），全部可二值判定
- [x] 含同类扫描影响面表（§3：按包拆分并行 4+2 匹配 / 任务粒度指引 5 引用 / ~/.agate 脚本消费方 15 项）
- [x] 无 [NEED_CONFIRM]，[NO_NEED_CONFIRM] + [PROD_NOT_TOUCHED] 行首声明；3 条 [SUGGEST:] 倾向项
- [x] frontmatter YAML 解析验证通过；BDD 锚点 grep 确认 21 条
## requirements-review progress

- [x] 读 dispatch-context（派发指引）
- [x] 读角色定义 requirements-review.md
- [x] 读 P1-requirements.md（评审对象，21 BDD）
- [x] 读 P0-brief.md
- [ ] 读 approved plan
- [ ] 读 P1-dispatch-context-analyst.md
- [ ] 读 WORKFLOW.md「需求与验收机制」
- [ ] 逐 BDD 评审
- [ ] 写 P1-review.md + status
- [x] 读 approved plan（字段契约/6 Task/验收标准）
- [x] 读 P1-dispatch-context-analyst.md（核对是否被遵循）
- [x] 读 WORKFLOW.md「需求与验收机制」
- [ ] 逐 BDD 评审
- [ ] 写 P1-review.md + status
- [x] 逐 BDD 评审完成（结论 needs-revision，F1-F5）
- [x] 写 P1-review.md + status

## [修复轮] P1 analyst 修订（F1-F5）
- F1(BLOCKER): 新增 §4.6 + BDD-22（self-gate 触发，plan 验收标准 6 落点）；I1 行补「验收落点：BDD-22」交叉引用
- F2: BDD-6 Given 改为 4 批全字段（每批 id+complexity），避开 BDD-5 缺字段路径
- F3: BDD-15 Given 显式 agate/phase-cards/P1-requirements.md
- F4: BDD-5 保留合并 + 注（P6 须分别构造缺 complexity / 非法值两子场景各验一次）
- F5: BDD-20 改动态表述「≥ 改造前实测基线 + 8」，不硬编码 751+/749
- 自检：BDD 1-22 连续、全部二值、无行首 [NEED_CONFIRM]、frontmatter 未动、影响面表完整；[PROD_NOT_TOUCHED]

## [复评轮] requirements-review 复核 F1-F5
- [x] 读修订后 P1-requirements.md（22 条 BDD，含 §4.6 BDD-22）+ 上轮 P1-review.md + 上轮 dispatch-context-analyst.md
- [x] F1(BLOCKER) 复核：BDD-22 已新增（§4.6 L249-252，git log 含 self-gate-review: + protocol-alignment-review 派发记录），I1 L70 已交叉引用「验收落点：BDD-22（§4.6）」→ 已解决
- [x] F2 复核：BDD-6 Given 补全每批 complexity（low×4）+ 注明「各批字段完整，不会先命中 BDD-5」→ 已解决
- [x] F3 复核：BDD-15 Given 显式 `agate/phase-cards/P1-requirements.md` + 同名消歧注 → 已解决
- [x] F4 复核：BDD-5 保留合并 + 注（P6 分别构造缺 complexity/非法值两子场景各验一次）→ 已解决（走"保留合并但注明"分支）
- [x] F5 复核：BDD-20 改动态表述「≥ 改造前实测基线 + 8」，显式不硬编码 751+/749 → 已解决
- [x] 回归复核：BDD 1-22 连续无跳号（grep 确认 22 条）、全部可二值、无 [NEED_CONFIRM]（仅 L256 [NO_NEED_CONFIRM]）、frontmatter 完整未动、P1 纯净性保持
- [x] 回归复核无问题（BDD 连续 22 条/二值/无 NEED_CONFIRM/frontmatter 完整/纯净性）
- [x] 写 P1-review.md + status: approved（覆盖写回，保留 Header 字段，F1-F5 逐项复核 + BDD-1~22 逐条判定 + 覆盖维度）
- [x] 自检：grep status: approved 已落盘；未修改 P1-requirements.md（只读）
