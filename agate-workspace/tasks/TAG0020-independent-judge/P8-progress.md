# P8 实现进度（TAG0020 — releaser / implementer P8 模式）

## 输入读取（已完成）

1. ✅ P8-dispatch-context-implementer.md（强制指令：产出 P8-release.md、不执行 commit/tag/bump、bump_type minor v0.58.0→v0.59.0、debt_check reviewed、UPGRADING v0.59.0 章节需新增给草案、临时资源清单、发布检查命令表）
2. ✅ P7-consistency.md（BLOCKER=0 / DEVIATION=0 / CODE_MAP_DRIFT 已闭环——3 新文件登记）
3. ✅ P2-design.md §5 gate_commands（P5 / P5_consistency / P5_count_tests）+ packages: [agate]
4. ✅ 版本引用现状：README.md badge `version-v0.58.0`（L5）/ README.zh-CN.md badge `version-v0.57.0`（**存量偏离**，TAG0019 未同步）/ CHANGELOG 头部 `[0.58.0]`（无 [Unreleased] 块）/ UPGRADING「已知破坏性变更」最新节 `### v0.58.0`（样式参照）/ git tag v0.58.0
5. ✅ tech-debt.md（DEBT0001-0017 全读，无 TAG0020 条目）+ judge.md（发布素材）

## 产出

1. ✅ **P8-release.md**（新建）：Header（phase: P8 / task_id: TAG0020-independent-judge / type: release / parent: P2-design.md / trace_id: TAG0020-P8-20260822 / status: draft / created: 2026-08-22 / agent: implementer / packages: [agate] / **bump_type: minor** / **debt_check: reviewed**）
   - §1 版本信息：v0.58.0 → v0.59.0，minor 理由（新增 P6.5 judge 机制、向后兼容、历史任务跳过）
   - §2 debt_check: reviewed（无 TAG0020 债务条目；4 个候选关注项三分法评估均不登记，正文留痕）
   - §3 版本号变更确认清单 5 项（README badge 必改 / zh badge 存量偏离建议同步 / CHANGELOG [0.59.0] / UPGRADING 新章节 / git tag + 远端验证 G-5）
   - §4 临时资源清单 6 项（无临时服务/进程；pytest basetemp 与复现 scratch 已清理；无端口/无开发安装；确认项列出）
   - §5 发布检查命令表 7 步（P5 全量 / consistency / count-tests / audit7-only 条件化复用 / git log 对照 / tag 创建推送 / 干净 checkout consistency；DEBT0013 时序注意）
   - §6 CHANGELOG [0.59.0] 小节草稿（judge 角色/三层防造假/新脚本/gate_p65/三档预算/历史兼容/文档清单）
   - §7 UPGRADING v0.59.0 章节草案（按 v0.58.0 样式：无破坏性变更 + 逐条说明 + 升级动作）
   - §8 releaser 边界声明（未执行 commit/tag/bump）