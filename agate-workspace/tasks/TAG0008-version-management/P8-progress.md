# P8 发布准备 — 进展落盘

## 输入读取
- [x] P8-dispatch-context-implementer.md：bump minor v0.49.0→v0.50.0（P2 packages=[agate] 单包，加功能向后兼容）；文档联动清单 13+ 项；debt_check 需读 tech-debt.md；临时资源清单
- [x] implementer.md P8 模式：只改文件不 commit/tag；逐包 bump；P8-release.md 必含 bump_type/debt_check/版本变更确认/CHANGELOG 确认/临时资源清单/Lessons Learned
- [x] P1-requirements.md：影响面表 2.2 文档层 13 项联动 + 2.1 脚本层（含 scripts/README + check-protocol-consistency 白名单）
- [x] P7-consistency.md：approved；P8 承接项 = scripts/README 新增 4 脚本 + resolve-entry 说明 + SCRIPT_REF_RE 白名单补 install-offline/resolve-entry + 文档联动
- [x] tech-debt.md：DEBT0001（closed）；P4-review 遗留建议（sha256 共享 INFORMATIONAL-8 / manifest 签名 / 扫描限流 MEDIUM-3）→ debt_check: reviewed + 登记
- [x] 版本引用文件现状：README badge v0.49.0；README.zh-CN badge v0.48.0（漂移，一并 bump v0.50.0）；CHANGELOG 无 [Unreleased]（顶部即 [0.49.0]）；UPGRADING 无 v0.50.0 章节；无独立 version 文件（README badge = version 文件）

## 版本 bump + 文档联动执行
- [x] README.md badge v0.49.0 → v0.50.0（L5）
- [x] README.zh-CN.md badge v0.48.0（漂移）→ v0.50.0
- [x] CHANGELOG.md 新增 [0.50.0] 章节（TAG0008 版本管理机制 6 组件 + 离线包 + 文档联动 + 破坏性变更声明）；无 [Unreleased] 需迁移（顶部即 [0.49.0]）
- [x] agate/UPGRADING.md 新增 v0.50.0 章节（~/.agate 目录化 / .agate-version 语法 / hook 解析入口迁移 / agate-install 新工具 / BDD-30 存量兼容红线 / 迁移动作小结）
- [x] agate/scripts/README.md：顶部版本管理说明 + 3 hook 薄壳 exec resolve-entry + 安装节 + 版本管理新节（5 脚本）+ summary 描述语义更新
- [x] agate/scripts/check-protocol-consistency.py CHECK 10 白名单补 install-offline/resolve-entry（P7 承接项 2，判定逻辑未改）
- [x] agate/SETUP.md：新增「环境准备（agent 执行）」节 + 前置路径叙述随版本目录调整
- [x] agate/platform-notes.md：latest/current 指针复制/文本模式说明 + 表格行更新
- [x] agate/AGENTS.md：header 版本目录说明 + 升级/卸载适配版本目录
- [x] agate/WORKFLOW.md：安装位置叙述（目录 + 解析）
- [x] agate/orchestrator-template.md：{agate_root} 解析改为 agate-resolve 优先 + env 覆盖
- [x] agate/adr.md：ADR-008 论据复核 + 新增 ADR-009（版本管理机制）
- [x] agate/assets/templates/project.md：默认安装位置语义 + AGATE_ROOT env 说明
- [x] agate/assets/templates/handoff-template.md：版本目录说明（复核）
- [x] install.sh：兼容保留注释（单软链 + 版本管理替代入口）
- [x] tech-debt.md：登记 DEBT0002（sha256 双实现）/ DEBT0003（manifest 未签名）/ DEBT0004（扫描限流漏扫）——check-debt exit 0

## consistency 验证
- [x] check-protocol-consistency.py --strict：0 ERROR（除 CHECK 7 瞬态——badge v0.50.0 领先于 git tag v0.49.0，主 Agent tag 后自愈）+ 279 WARNING（与 P5 基线一致，未新增）
- [x] 文档脚本名引用新脚本（install-offline/resolve-entry/agate-install 等）均真实存在于 agate/scripts/ → CHECK 10 无新增 WARNING/ERROR

## 自检
- [x] grep 确认 v0.50.0 落盘：README badge（1 命中）、CHANGELOG [0.50.0]（1）、UPGRADING v0.50.0（1）
- [x] check-protocol-consistency.py --strict：0 ERROR（除 CHECK 7 tag 瞬态）+ 279 WARNING（基线未增）
- [x] check-debt.py tech-debt.md exit 0（DEBT0002-0004 登记有效）
- [x] test_check_protocol_consistency.py 16 passed（白名单扩展无回归）
- [x] P8-release.md 含 bump_type / debt_check / 版本变更确认 / CHANGELOG 确认 / 临时资源清单 / Lessons Learned
- [x] 未执行 git commit/tag
