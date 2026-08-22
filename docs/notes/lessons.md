# agate 开发 Lessons Learned

> 汇总各任务 P8 复盘的 Lessons Learned + 批次复盘教训。每条：类别 / 教训 / 来源任务 / 日期。
> 新任务 P8 复盘后，把 Lessons Learned 节汇入本文件。

---

## 2026-08-12（TAG0001-0003 批次）

### 架构

| 教训 | 来源 | 日期 |
|------|------|------|
| 路径重构类任务的暗雷是"检测逻辑里的硬编码"，不是提示文字——迁移 `docs/tasks/` 后，`grep 'docs/tasks/[^/]+/'` 这类硬编码会静默失效。P2 用 minimal_validation 验证"移动路径后的兜底分支流向"，比人肉 grep 换血清单可靠 | TAG0003 | 2026-08-12 |
| 新增 gate 分流机制必须是"前置增量分支 + 空值短路"，缺省路径逐字节保留并由基线用例反证——向后兼容靠"分支短路"而非"复制粘贴旧逻辑" | TAG0002 | 2026-08-12 |
| 登记簿类项目级状态文件（tech-debt 多条目）与任务级单 frontmatter 是两种数据形态——独立校验器复用"fail-closed + stdout 错误行"模式而非复用实现，回归风险降到零 | TAG0001 | 2026-08-12 |
| 目录归类不是小事——tech-debt 属"流程产出的项目状态记录"，归独立目录比塞进"agent 输入知识"目录更符合内容边界判据；归类修正牵动多端面，须 grep 全量同步 + BDD 重验 | TAG0001 | 2026-08-12 |

### 流程

| 教训 | 来源 | 日期 |
|------|------|------|
| 破坏性变更的版本号决策要有项目规范锚点，不套通用 semver——WORKFLOW 明文 + UPGRADING 先行写入迁移节，版本号靠既有文档惯例消除歧义，不是拍脑袋 | TAG0003 | 2026-08-12 |
| 版本 bump 必须同步核对 README badge + 本地 tag + `git describe` 三处，且发布前确认 tag 是 HEAD 祖先（release PR 普通 merge 前提） | TAG0002 | 2026-08-12 |
| **本地全绿 ≠ CI 全绿**：本地 worktree 的 `.worktrees` 路径过滤会掩盖一致性检查真实问题（D4）。dogfooding 任务发布前必须在干净 checkout 或 CI 兜底跑 consistency | 批次复盘 D4 | 2026-08-13 |
| 跨任务批次启动前，P0-brief 必须与最新协议状态核对（本次靠用户提示而非流程强制） | 批次复盘 M2 | 2026-08-13 |

### 测试

| 教训 | 来源 | 日期 |
|------|------|------|
| refactor 类任务的验证不适用 TDD 红灯语义（无新行为断言，全量即绿）——需 P3 口径 + CI backstop 双点声明跳过 check-tdd-red，否则合法重构任务被 CI 误杀 | TAG0002 | 2026-08-12 |
| bats fixture 里 `mkdir -p "$dir/{a,b,c}"` 大括号被引号包裹不展开、只建 1 目录——shell 大括号展开不做引号内求值，fixture 断言须显式参数化 | TAG0001 | 2026-08-12 |

### 协议工具（dogfooding 特有）

| 教训 | 来源 | 日期 |
|------|------|------|
| 协议工具操作 git 时必须显式考虑 `core.hooksPath`/`--no-verify`/pathspec——迁移工具自动 commit 被自身 hook 拦截（D1），与"dogfooding 项目装有 agate hook"冲突是必然现实 | TAG0003 | 2026-08-12 |
| 新增机器字段若无历史正文格式，一律 frontmatter-only——`_regex_fallback` 全文扫描会把正文提及字段名的文档误判（D2） | TAG0002 | 2026-08-12 |

---

## 2026-08-22（TAG0021）

### 测试

| 教训 | 来源 | 日期 |
|------|------|------|
| 环境假象要用可复现证据分类而非凭记录放行：P5/P6 记录的 basetemp 环境假象（test_bdd_7「basetemp 在 git 仓库外」语义、test_bdd_25「共享 basetemp 污染一致扫描」）在 P8 全量重跑原样复现，各自换 basetemp 位置/清共享根后转绿才记"非回归"——防止把真实回归误放行 | TAG0021 | 2026-08-22 |

### 流程

| 教训 | 来源 | 日期 |
|------|------|------|
| `--basetemp` 指向 git 仓库内目录有双重副作用（git 解析上溯命中仓库破坏"非 git 上下文"测试语义 + 共享根目录 fixture 残留污染后跑测试扫描面），测试设计应避免隐含"cwd 在 git 仓库外"假设，P2 env_constraints 显式声明 basetemp 位置对 git 语义的影响 | TAG0021 | 2026-08-22 |
| 非交互 shell 不读 bashrc，工具路径要写绝对路径（ruff 不在 PATH 需 /home/kity/.local/bin/ruff，与 DEBT0014 python 探测同类）——发布检查命令显式写解释器/工具绝对路径或可执行性探测，避免 exit 127 被误判为回归 | TAG0021 | 2026-08-22 |
