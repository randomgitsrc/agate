# P8 进度追踪 — TAG0012

## 步骤 1：读 dispatch-context + implementer.md（P8 模式节）
- 已读 P8-dispatch-context-implementer.md：核心约束 7 条（版本号判定/packages vs 实际改动差异说明/CHANGELOG 三段式/debt_check/发布检查命令清单/临时资源清单“无”/README badge 行号核对）
- 已读 implementer.md：P8 模式定位（"每个受影响包做发布准备"，不执行 commit/tag，产出 P8-release.md 含 bump_type/debt_check/版本变更确认/CHANGELOG 更新确认/临时资源清单/Lessons Learned）

## 步骤 2：读 P2-design.md
- packages: [phase-cards, dispatch-protocol, state-machine, execution-roles, templates, scripts]（逻辑分组，agate 自身单版本号，无独立多包）
- gate_commands 五条：P3（pytest anchors -v）/ P5（全量 pytest -q）/ P5_consistency（check-protocol-consistency.py --strict）/ P5_count（count-tests.sh）/ P5_shellcheck（shellcheck -S warning scripts/*.sh）

## 步骤 3：读 P4-implementation.md
- 12 个改动文件清单确认（dispatch-protocol.md/state-machine.md/P0-orchestrator.md/P1-requirements.md/P2-design.md/P5-verification.md/P6-acceptance.md/analyst.md/architect.md/verifier.md/dispatch-prompt.md/task-files.md）
- 无 scripts/ 目录文件改动；新增测试文件 test_protocol_mechanism_anchors.py 属 agate/tests/
- DESIGN_GAP/SCOPE+/SCOPE_GAP/CLARIFY 均 0 条；无破坏性变更（缺字段行为等同现状）

## 步骤 4：读 P7-consistency.md
- BLOCKER=0，approved
- 观察点①：dispatch-context "13 行" 表述不准确，实际 16 行（行数≠文件数，不影响文件级结论）
- 观察点②：P2 packages 声明含 scripts，但实际改动 12 文件中无一在 agate/scripts/ 下；待 P8 核对 CHANGELOG 分类措辞 —— 已在下方 P8-release.md 中如实处理，不虚报为改了 scripts/

## 步骤 5：读 CHANGELOG.md 现有格式 + README.md version badge
- CHANGELOG.md 最新章节 `## [0.51.0] - 2026-08-18`（TAG0006），格式：新增/变更/测试 三段式
- README.md line 5：`[![version](https://img.shields.io/badge/version-v0.51.0-blue)]...` —— version badge 唯一位置
- 实测 `git describe --tags --abbrev=0` = v0.51.0，与 badge 一致

## 步骤 6：检查 tech-debt.md
- 文件存在：agate-workspace/debt/tech-debt.md，6 条 DEBT（0001/0005/0006 closed，0002/0003/0004 open）
- 全部 6 条 source task 均为 TAG0008/TAG0013/TAG0006，均与 TAG0012（协议机制增强批）无关联
- 独立核实结论：debt_check: none（本任务无相关遗留债务条目，SELF-GATE A7 止损轮次事项已被主 Agent 裁决为设计取舍非债务，未在 tech-debt.md 登记，与预期一致）

## 步骤 7：产出 P8-release.md
- 见同目录 P8-release.md

## 步骤 8：完成，返回摘要
- P8-release.md 已写入：bump_type=minor（v0.51.0→v0.52.0），debt_check=none，packages/scripts 差异如实说明未虚报，CHANGELOG 内容建议已按本任务真实改动重新撰写（未照抄 TAG0014），发布检查命令清单 5 条列出，临时资源清单声明“无”，Lessons Learned 3 条
- 未执行任何 git add/commit/tag，未修改 README.md/CHANGELOG.md 正文
