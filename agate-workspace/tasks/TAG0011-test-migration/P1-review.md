---
phase: P1
task_id: TAG0011-test-migration
agent: requirements-review
status: approved
created: 2026-08-15
---

# P1 需求评审 — TAG0011（agate 测试框架迁移阶段二）

## 结论

**status: approved** —— BLOCKER-1（BDD-1 计数口径与 §6.2 退役决策自相矛盾）已修复：采纳方案 B，全口径统一为 **60 文件 / 749 @test**。其余关注点复核全部通过，未发现修订引入的新矛盾。BLOCKER = 0。

> 核查记录（2026-08-15 复审，逐文件实测）：
> - 实测 `grep -c '^@test'`：unit 46 文件 / 625、regression 6 / 17、integration 6 / 85、sanity 6、scripts 2 文件（check-platform-assumptions 16 + check-windows-smoke 7）→ **合计 61 文件 / 756 @test**；迁移范围 = 60 文件 / 749 @test（除 check-windows-smoke.bats），与文档 §1/§3/§4 口径完全吻合。
> - §4 批次 @test 合计复算：19+11+39+53+37+42+69+57+146+79+60+17+20+56+19+9+16 = **749**（批次 17 为退役批 0 文件 0 用例，不计入）；文件数 3+5+6+3+4+4+3+5+3+4+4+6+4+2+2+1+1 = **60**，与批次覆盖自检一致，46+6+6+1+1 不重不漏。
> - `count-tests.sh` 实跑 = 727（count-tests 口径，58 文件），与文档"58/727"口径声明一致。
> - `check-frontmatter.py` 过 P1-requirements.md：exit 0。
> - BDD 锚点 `#### BDD-NN:` 1–12 连续无跳号，共 12 条（≥1）。
> - §8 仅 `[NO_NEED_CONFIRM]` + 1 `[DECIDED]` + 5 `[SUGGEST]`，无未决 `[NEED_CONFIRM]`。

## BLOCKER

无（BLOCKER-1 已解决，见下）。

### BLOCKER-1（已修复，方案 B）：BDD-1「收集数 ≥ 749」与 §6.2 退役决策口径统一

- 修复路径：原矛盾点（BDD-1 Given"61 文件 / 756 全部迁移" + Then"收集数 ≥ 756"，与退役 check-windows-smoke.bats 7 用例冲突）已按方案 B 消除。
- 现状核对：
  - BDD-1 Given 改为「60 个 .bats / 749 @test 全部迁移为 pytest；check-windows-smoke.bats 随脚本退役；bats 整体退役」，Then 改为「`--collect-only` 收集数 **≥ 749**」（P1-requirements.md L284-287）。
  - §6.2 由 SUGGEST 升级为 **DECIDED**（退役 check-windows-smoke.sh → `@pytest.mark.windows_smoke` marker 承接冒烟），§8 第 1 条同步为 [DECIDED]（L351）。
  - §4 批次 17 改为**退役批**（0 文件 / 0 用例），批次覆盖自检改 60 / 749（L205-207）。
  - §2.5 用例数语义、§3 口径说明、§5 表 E、BDD-4/BDD-12 全部对齐 749 口径。
- 交叉验证：749 = 756 − 7，唯一退役项为 check-windows-smoke.bats（7 用例，测退役脚本自身选取行为），逻辑自洽；`--collect-only ≥ 749` 与迁移范围一致。P6 验收计数不再 FAIL。

## BDD 评审

- BDD-1: **PASS（修复后）** — Given/Then 均 749 口径，`--collect-only ≥ 749` 二值可判 — 覆盖维度 数据✓ 多端✓
- BDD-2: PASS — `--strict` exit 0 且无 ERROR/WARNING — 数据✓
- BDD-3: PASS — `ruff check agate/` exit 0 无 error 级 — 工具链✓
- BDD-4: PASS — Windows 冒烟子集全 PASS；`requires_minimal_validation: true` 已声明，P2 须产出 `minimal_validation:` 块 — 多端✓
- BDD-5: PASS — 全树 0 命中 + R1-R5 正例可检出（非空转） — 兼容✓
- BDD-6: PASS — 迁移期双跑对照，注明"直至 bats 退役" — 多端✓
- BDD-7: PASS — encoding 守卫无违规 — 边界✓
- BDD-8: PASS — ruff py38 target + 扫描器无 R1-R5 命中 — 兼容✓
- BDD-9: PASS — 断言对象（exit 0/1/2、GATE 前缀、两行输出、gate-result.json、sha256）已枚举可判 — 数据✓ 前端✓
- BDD-10: PASS — helpers fixture 结构等价（P0-P8 文件/.state.yaml/frontmatter/Given/git 配置） — 数据✓
- BDD-11: PASS — hook 链断言行为等价 — 前端✓
- BDD-12: PASS — 冒烟机制无 bats 依赖、CI 引用 pytest 命令 — 多端✓（与 BDD-1/§6.2 口径一致）

编号 `#### BDD-NN:` 1–12 连续无跳号；每条单一 GWT；均可二值判定。12 ≥ 1 达标。

## 隐含需求覆盖

- 数据：✓ §2.1（夹具契约、BATS_TEST_TMPDIR→tmp_path、run/output→run_cli 映射）
- 前端/展示：✓ §2.2（CLI 输出契约、生命周期→fixture）
- 多端：✓ §2.3（平台 + CI + hook 链 subprocess 方案）
- 边界：✓ §2.4（Windows marker 承接、encoding、路径、bats 特有工具、Pillow skip）
- 兼容：✓ §2.5（扫描器干净树、count-tests 改写、一致性锚点、用例数语义 749）
- 测试特有：✓ §2.6（sanity/helpers-python/env-adapt-docs/windows-smoke 退役/P6 视觉链）

五维 + agate 特有维度全覆盖，无遗漏。

## 裁剪评审

- phases: [P1–P8] 无裁剪，理由充分（high risk、全链影响面）。
- risk_level: high — 与「数周密集 + 高回归风险 + 与 TAG0010 同级」匹配。
- change_type: refactor — 合理（测试框架迁移、产品行为不变）；schema 仅支持 refactor，枚举合法。
- domains: [backend, cli] — 合理（测试框架 + CLI 断言），无 frontend/mcp/security 影响。
- packages: 5 项基本覆盖；表 E 引用了 `agate-workspace/archived/plans/`（count-tests 漂移提示指向），建议 P4 文档批时补 `agate-workspace` 入 packages 声明以便 P7 交叉核对（非阻塞）。

## capability_requirements

- pytest / ruff / Windows CI 均 `available`，无 GAP，不阻塞推进；`requires_minimal_validation: true` 处理正确（Windows 真机行为本地不可验证，P2 兜底）。

## NEED_CONFIRM

- §8 为 `[NO_NEED_CONFIRM]` + 1 `[DECIDED]` + 5 `[SUGGEST]`，无 `[NEED_CONFIRM]`，不阻塞。✓

## 非阻塞意见

1. **批次 8（146 @test）粒度风险**：check-gate.bats(124)+p1-review(9)+p5-diff(13) 是单批最大。文档已声明「P4 内部按 gate 阶段拆子任务」并给出 `-k gate_p1/p5/p7` 命令，方向正确；P2「批次细化方案」必须把批次 8（及 ≥60 的批次 6/9/10/13）落实为具体子批表（每子批 ≤30 @test + 独立验证命令），P4 才真正按子批派发，否则「内部拆分」停留在承诺层。
2. **BDD-9/10/11「与 bats 时代一致」的 P6 判据**：bats 终态退役后无对照物。建议 BDD-6 双跑阶段留存 bats 基线输出作 P6 证据（P2/P5 落实证据留存路径）。
3. **批次表呈现**：表头「17 批」而表格含批次 0–17 共 18 行（批次 17 为退役批）——自检已注明退役批不计入，语义一致，仅建议表头注明「17 迁移批 + 1 退役批」避免歧义（非阻塞）。
4. **P1 纯净性**：§6.1 迁移映射表 + conftest fixture 命名 + 批验证命令已接近 P2 设计深度。虽为 P0-brief「强制要求（批次 + 清单）」所逼，P2 应确认而非重做，避免双重设计分歧。
5. **count-tests.sh 定性**：§6.3 建议改写、§5 表 E 表述为「§6.3 已定改写」、§8 为 [SUGGEST]——三处措辞强度不一，方向一致（改写为 pytest 收集计数）不矛盾；P2 定实现即可。

## 门槛产出

- File: `agate-workspace/tasks/TAG0011-test-migration/P1-review.md`
- Status: **approved**（BLOCKER-1 已修复，BLOCKER=0）
