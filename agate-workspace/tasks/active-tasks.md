# 任务看板 (Task Board) — agate 仓库

> `.state.yaml` 是单任务的权威状态，`active-tasks.md` 是全局汇总视图（主 Agent 维护，subagent 不直接改）。

---

## 任务列表

### 进行中的任务

| 编号 | 任务名称 | 状态 | 阶段 | 优先级 | 依赖 | 创建日期 | 更新日期 |
|------|----------|------|------|--------|------|----------|----------|
| TAG0015 | agate 复盘与反馈机制统一（RM-AG0020 + RM-AG0021）：复盘模板进协议 + 正文结构/归因分层/事实依据 + orchestrator-log 扩展 + 会话 checkpoint + 跨项目反馈（结构化反馈节 + 匿名化 + 开关）| 🔄 | P3 | 高 | — | 2026-08-16 | 2026-08-19 |

### 待开始

| 编号 | 任务名称 | 状态 | 阶段 | 优先级 | 依赖 | 创建日期 | 更新日期 |
|------|----------|------|------|--------|------|----------|----------|
| TAG0007 | agate 项目结构管理：0→1 骨架（RM-0008）/ code-map + 架构演进（RM-0009）| ⬜ | P0 | 高 | — | 2026-08-13 | 2026-08-13 |
| TAG0016 | agate 协议卫生与测试效率（RM-AG0025 + RM-AG0026）：协议文档职责边界与去重 + 测试重跑审计与跨阶段证据引用 | ⬜ | P0 | 高 | — | 2026-08-17 | 2026-08-17 |

### 已完成（归档）

<details>
<summary>已完成的 task（点击展开）——历史归档，详情见各 task 目录 + .state.yaml</summary>

| 编号 | 任务名称 | 状态 | 最终阶段 | 优先级 | 完成日期 |
|------|----------|------|----------|--------|----------|
| TAG0012 | agate 协议机制增强批（RM-AG0013 同类扫描/影响面梳理 + RM-AG0014 verification_env 失败处理协议/环境准备职责边界 + RM-AG0019 P0-brief 时效性 + RM-AG0023 运行时管控 timeout_seconds/命令超时兜底/资源密集型串行）：23 条 BDD 全 PASS，12 个协议文件改动 → v0.52.0 | ✅✅ | READY | 高 | 2026-08-18 |
| TAG0006 | agate UI/UX 验收质量机制（RM-AG0007 UX 需求/评审/验收 + RM-AG0004 视觉验收能力边界 + RM-AG0006 GUI 框架评估 + SCOPE+ UI/UX 覆盖任意渲染形态）：P1 vision 三态/UX 分类框架 + P2 UI 设计节/渲染形态适配 + P6 双证据三态分档/avg-hash 降级 → v0.51.0 | ✅✅ | READY | 高 | 2026-08-18 |
| TAG0008 | agate 版本管理机制（v1）：多版本共存 + 项目锁定 + 程序化安装/升级（agate-install / agate-resolve / hook 解析入口 / summary 版本显示 / 离线部署包 + 环境探测）→ v0.50.0 | ✅✅ | READY | 高 | 2026-08-16 |
| TAG0014 | agate 派发编排机制（全阶段，RM-AG0016）：工作量评估 + 五模式编排 + 并行规则统一（dispatch_plan 可选字段 + 权威节 + 8 卡统一 + 模板兜底）→ v0.49.0 | ✅✅ | READY | 高 | 2026-08-16 |
| T001 | agate v2.0 结构化数据改造（A+B+C+D 全做，一个 task）→ v0.40.0 | ✅✅ | READY | 高 | 2026-08-10 |
| TAG0003 | agate 工作区架构（agate-workspace/ 目录规范 + roadmap 任务管理循环 + .agate.env 配置 + docs/tasks 迁移工具）→ v0.41.0 | ✅✅ | READY | 高 | 2026-08-12 |
| TAG0002 | 重构一等任务（Phase A：change_type: refactor + P6 重构验收口径 + gate 分流）→ v0.42.0 | ✅✅ | READY | 高 | 2026-08-12 |
| TAG0001 | agate 技术债登记闭环（Phase 1-3：模板+schema 校验+回退强制+P8 确认+回填验证 + debt/ 归类修正）→ v0.43.0 | ✅✅ | READY | 高 | 2026-08-12 |
| TAG0004 | agate 脚本环境适配（Windows 原生兼容 + Linux 基线回归）：S1 空格路径 fail-open / S3 encoding / S2 中文证据 / M4M5 全角冒号 / M6 CRLF / M9 元字符 / Q1 路径归一化 / Q2 卡片 / Q5 文档 / RM-AG0001 / RM-AG0002+TPV0090-M4 / CI windows matrix → v0.44.0 | ✅✅ | READY | 高 | 2026-08-13 |
| TAG0005 | agate 机制修复批：P2 gate vs C8 契约（RM-AG0010）/ P5 计数语义（RM-AG0011）/ 自定义角色两瑕疵（RM-AG0012）/ 短命会话重试（RM-AG0003）→ v0.45.0 | ✅✅ | READY | 高 | 2026-08-13 |
| TAG0009 | agate 测试套件平台无关化：78 个 Windows bats 失败根治（静态扫描器 gate + 批量修正 + Linux 模拟覆盖 Windows 分支）→ v0.45.0 | ✅✅ | READY | 高 | 2026-08-14 |
| TAG0010 | agate 产品逻辑 Python 化（阶段一）：30 个 sh → py（hook 保留 sh 薄壳），消解 bash 在 Windows 模拟层问题；TAG0008 依赖本任务 → v0.46.0 | ✅✅ | READY | 高 | 2026-08-15 |
| TAG0011 | agate 测试框架迁移（阶段二）：60 个 .bats → pytest + 协议文档全量重写 + CI 同步（达成全 Python）→ v0.47.0 | ✅✅ | READY | 高 | 2026-08-15 |
| TAG0013 | agate 脚本一致性批：CHECK 10 文档引用漂移 gate（RM-AG0015）+ self-gate 触发面补 README/AGENTS（RM-AG0017）+ tech-debt 登记提醒（RM-AG0018 剩余）→ v0.48.0 | ✅✅ | READY | 高 | 2026-08-16 |

</details>

---

## 状态符号

| 状态 | 符号 | 说明 |
|------|------|------|
| 待开始 | ⬜ | 任务已创建，P1 尚未开始 |
| 进行中 | 🔄 | 正在执行某个阶段 |
| 暂停 | ⏸️ | gate 失败超限 / 等待人工决策 |
| 已完成 | ✅✅ | P8 gate 通过 + READY |
| 已取消 | ❌ | 需求变更或不再需要 |
| 已合并 | 🔀 | 合入另一个任务 |

---

## 阶段产出

| 阶段 | 产出文件 | 门槛（见 state-machine.md） |
|------|----------|------|
| P0 | P0-brief.md | 主 Agent 亲自写，四字段非空 |
| P1 | P1-requirements.md | ≥1 条 BDD + 无行首 [NEED_CONFIRM] + 无 CAPABILITY_GAP |
| P2 | P2-design.md + P2-review.md | review.status=approved |
| P3 | P3-test-design.md | TDD 红灯正确（`check-tdd-red.py` exit 0） |
| P4 | P4-implementation.md | 文件非空 + gate 通过 |
| P5 | P5-verification.md | 所有测试通过 |
| P6 | P6-acceptance.md + P6-evidence/ | provenance 三道审计通过 |
| P7 | P7-consistency.md | BLOCKER=0 + DESIGN_GAP 全配对 |
| P8 | P8-release.md | version bump + CHANGELOG |

---

## 目录结构

```
{AGATE_WORKSPACE}/tasks/
├── active-tasks.md          ← 本文件
├── T001-v2.0-structured/
│   ├── .state.yaml          ← 单任务权威状态
│   ├── P0-brief.md
│   ├── P1-requirements.md
│   ├── P2-design.md
│   ├── P7-consistency.md    ← 含 DESIGN_GAP + REVIEWED 配对
│   └── ...                  ← 其余阶段产出
└── ...
```

---

## 维护规则

1. 只有主 Agent 改这个文件，subagent 不直接写
2. 每次阶段推进后，同步更新对应任务行（状态/阶段/更新日期）
3. `.state.yaml` 是权威来源——怀疑不一致时从 `.state.yaml` 全表重建
4. 新任务编号 = 当前最大编号 + 1，不复用已取消任务的编号
