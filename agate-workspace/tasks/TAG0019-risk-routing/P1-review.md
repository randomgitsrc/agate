---
phase: P1
task_id: TAG0019-risk-routing
type: review
parent: P1-requirements.md
trace_id: TAG0019-P1-20260821
status: approved
created: 2026-08-21
agent: requirements-review
revision: 3
---

# TAG0019 风险分路由 P1 需求终审（requirements-review，⑩第 4 轮 / REV3）

> 复审对象：P1-requirements.md（analyst 已修复 R3）。R1（扫描 2 口径）已于 REV2 实证通过；R2（BDD-7 四要素固化）主体已于 REV2 确认、遗留编号错位由 R3 修复。本轮独立复核 R3 + 全量复评。结论：**approved**。

## R3 独立复核（检查编号引用）— 已修复 ✓

| 核查点 | 证据 | 结论 |
|--------|------|------|
| check-pruning.py:113-125 源码编号 | 检查 3 = P6 不可裁剪；检查 4 = P4 不可裁剪；检查 5 = P5 不可裁剪 | ✓ 与 R3 修复声明一致 |
| §1:59 引用 | "check-pruning 既有检查 3（P6 不可裁）+ 检查 5（P5 不可裁）双闸拦截" | ✓ 已改正确 |
| BDD-7 When:196 引用 | "P5/P6 情形同时由既有 check-pruning 检查 3（P6 不可裁）+ 检查 5（P5 不可裁）兜底" | ✓ 已改正确 |
| 残留错引 | grep `检查 4/5|4/5` = 0 命中 | ✓ 无残留 |
| 其余检查编号引用 | 检查 7（:90/91）、检查 9（:92/259）、检查 1/6（:123）与 check-pruning.py 源码一致 | ✓ 无连带错引 |

**R3 关闭。**

## BDD 全量评审（逐条锚点）

15 条 BDD，编号 `#### BDD-NN:` 连续 1-15 不跳号 ✓，单场景单 BDD ✓，Given/When/Then 完整、Then 含显式 FAIL 判据、无中间态 ✓：

| BDD | 判定 | 覆盖维度 |
|-----|------|----------|
| BDD-1 算分脚本输出三要素（risk_score/tier/信号证据行） | ✓ 可二值判定 | 数据✓ |
| BDD-2 文件类型信号分级 | ✓ A/B 分级严格有序，不可区分 FAIL | 数据✓ 边界✓ |
| BDD-3 敏感路径信号与 security 域映射 | ✓ 含关键词标记 / 不含无标记，误报漏报 FAIL | 数据✓ 安全✓ |
| BDD-4 规模信号与 pruning 同口径 | ✓ >5 高风险 + 与 check-pruning 口径一致，矛盾 FAIL | 数据✓ 兼容✓ |
| BDD-5 域映射与影响面 | ✓ 升级/不升级两态二值可判 | 数据✓ 多端✓ |
| BDD-6 ceremony 合法值声明 | ✓ 三值通过 + 非法字面拦截（exit 非 0） | 数据✓ 边界✓ |
| BDD-7 fail-closed 四要素（申请+逐信号 checklist+跳过风险评估+P5/P6 保留） | ✓ 任一缺回退 standard；P5/P6 双闸引用已正确 | 数据✓ fail-closed✓ |
| BDD-8 不声明 = standard | ✓ exit 0 向后兼容 + 解释偏差 FAIL | 兼容✓ fail-closed✓ |
| BDD-9 声明 vs 算分单向 fail-closed | ✓ 薄于算分拦截、保守不拦，方向反 FAIL | 数据✓ fail-closed✓ |
| BDD-10 复用不重造（check-pruning 同源） | ✓ import/同函数调用 + 对拍一致，独立重写 FAIL | 复用约束✓ |
| BDD-11 requirements-review 审声明职责 | ✓ 清单含核对项，不一致时结论 must 为 needs-revision/rejected | 评审职责✓ |
| BDD-12 M3 验收锚四要素 | ✓ 评审轮数/真实发现数/TAG0018 基线/回滚规则，缺一 FAIL | 数据✓ 兼容✓ |
| BDD-13 新脚本平台假设零命中 | ✓ check-platform-assumptions R1-R5 全树 0 命中 + 通道/路径/CRLF 鲁棒 | 多端✓ 平台✓ |
| BDD-14 full 档强制评审与 P7 不可裁 | ✓ plan-eng-review + cso + P7 不可裁，缺一 FAIL | 多端✓ 安全✓ |
| BDD-15 消费点文档同步防漂移 | ✓ consistency 0 ERROR + 各清单同步，漏检不拦 FAIL | 兼容✓ 多端✓ |

## 同类扫描三组复评

- **扫描 1（check-pruning 复用，40 处）**：REV1 独立复现 40 处 ✓；行号引用（30-44/47-53/55-81/134-136/141-146/154-157 + agate_common.py:49 + pre-commit-gate.py:338 等）精确 ✓；A/B/C 三类逐条判定齐备 ✓；
- **扫描 2（risk_level/ceremony/C8）**：REV2 实证——纯 risk_level .md=36/.py=70、C8 .md=20、并集 36+20−1=55（重叠行 P4-implementation.md:86 已 read 确认）全部可复现 ✓；ceremony=0 全新概念 ✓；逐域判定表行号抽查无误 ✓；
- **扫描 3（平台差异）**：判定链（platform-notes 登记 / check-platform-assumptions R1-R5 / relpath 归一化 check-pruning.py:66 / CRLF check-pruning.py:79+pre-commit-gate.py:354-357 / run_git 通道）全部核实存在 ✓，转 BDD-13 ✓。

## 隐含需求覆盖 / frontmatter / 裁剪 / 纯净性

- 隐含需求 I1-I9 逐条带"为什么必须"，数据/多端/边界/兼容四维覆盖齐 ✓；
- frontmatter 合法：risk_level=medium ✓ / phases=[P1..P8] 全 8 ✓ / packages=[agate-protocol, agate-scripts, agate-tests] ✓ / domains=[backend, security] ✓ / implicit_coupling: true ✓ / capability_requirements=[]（无 GAP、非 frontend、无 verification_env）✓ / [NO_NEED_CONFIRM] ✓ / trace_id/status/agent 格式合规 ✓；
- 裁剪合理性：全 8 无裁剪逐条理由充分；risk_level=medium 与实际匹配；M3 主体/M4 dogfood 范围边界清楚（§1）；P5/P6 不可裁理由引用 BDD-7 一致 ✓；
- P1 纯净性：无实现细节混入（唯一例外 D1/D3 CLI 契约名，已显式声明为契约）✓；
- P0-brief 时效性已质疑（§0，1 条轻微漂移已记录）✓。

## 结论

三轮迭代闭合：R1（扫描口径）→ REV2 实证通过；R2（P5/P6 BDD 固化）主体到位、遗留编号错位 → R3 已修正并经本审独立核实（源码+需求两处引用+无残留）；全量复评 15 条 BDD 可判定、编号连续、扫描三组扎实、隐含需求覆盖完整、frontmatter 合法、裁剪合理、P1 纯净。**status: approved**——请主 Agent 预跑 check-gate.py P1 后进入 P2。