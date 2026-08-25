# agate 改名建议（2026-08-20 调研版 → 2026-08-23 决策版）

> **✅ 决策（2026-08-23 用户拍板）：改名 **Agateon**（"agent gates on"——闸门开启/验证激活）。
> 四源核验：npm/PyPI 空闲、.com/.dev/.io 疑似可注册（WHOIS 待确认）、GitHub 0 真实撞名；
> 保留 agate 前缀 → 迁移成本最低（`~/.agate`、`AGATE_*`、`agate-*.py` 兼容别名策略）。
> 本文件其余部分为调研过程记录，供"执行改名"任务引用。

> 背景：`agate` 名称严重撞车，影响可搜索性、品牌辨识与 SEO。本文基于真实可用性核验给出分层建议。

---

## 1. 撞车现状（为什么必须改）

GitHub 全库搜索 `agate`（`in:name`）命中 **1223 个**仓库，其中三个知名项目与"协议/工具"强竞争：

| 撞名项目 | 领域 | 影响 |
|----------|------|------|
| [wireservice/agate](https://github.com/wireservice/agate) | Python 数据分析库（热门，被引用极多）| 搜索污染最重 |
| [mbrubeck/agate](https://github.com/mbrubeck/agate) | Gemini 超文本协议服务器（Rust）| 同为"协议"语义，直接混淆 |
| [RubyLouvre/agate](https://github.com/RubyLouvre/agate) | Node.js 后端框架（中文社区）| 中文搜索污染 |
| [strongdm/agate](https://github.com/strongdm/agate) | "AI rock tumbler" 编排 CLI | **同类竞品撞名**，最致命 |
| Rust crate `agate` / docs.rs 包 | Gemini 服务器同名包 | 包名生态冲突 |

**结论**：`agate` 一词在 GitHub/npm/PyPI 已被 4+ 个活跃项目占用，"agent+gate" 的谐音梗已经救不回品牌辨识度。

---

## 2. 命名原则

1. **保留核心语义**：gate（门禁/关卡）+ 验证 + 阶段推进——这是产品的灵魂
2. **全球可发音**：中英文都好念、无不良联想
3. **生态可用**：npm / PyPI / GitHub 名称空闲（已实测）
4. **域名潜力**：`.dev` / `.io` 后缀有希望（未逐一核验，需购买前确认）
5. **不与"验证/门禁"类竞品撞词**：避开 agentgate、Agent-Gate、gateway（网关类太多）、guardrails

---

## 3. 可用性核验结果（2026-08-20 实测）

| 候选名 | npm | PyPI | GitHub 撞名 | 评价 |
|--------|-----|------|-------------|------|
| **gatewise** | ✅ 空闲 | ✅ 空闲 | 无知名撞名 | ⭐ 首选（见下）|
| **gatedev** | ✅ 空闲 | ✅ 空闲 | 无 | 直白但平淡 |
| **agaton** | ✅ 空闲 | ✅ 空闲 | 无 | 保留 agate 血统，含义隐晦 |
| **gateops** | ✅ 空闲 | ✅ 空闲 | 有"Agentic DevOps"平台（GateOps，西语）| 撞"GitOps"衍生语义 |
| **gatework** | ✅ 空闲 | ✅ 空闲 | Gateworks（硬件公司，非同名）| 可用，稍长 |
| **gatelock** | ✅ 空闲 | ✅ 空闲 | RBAC 库（异域）| 语义偏"锁定" |
| **gateprotocol** | ✅ 空闲 | ✅ 空闲 | 无 | 描述性强，偏长 |
| agate-protocol | ✅ 空闲 | ✅ 空闲 | 无 | 保品牌后缀策略（不真改名）|
| phasegate | ✅ npm 空闲 | ❌ 被占 | — | 弃 |
| verigate | ✅ npm 空闲 | ❌ 被占 | — | 弃 |
| gateflow / gatepost / portcullis / gatesmith | ❌ 被占 | — | — | 弃 |

> 注：npm/PyPI 为 HTTP 200=被占、404=空闲；GitHub 为 API 搜索 top 命中，未含模糊大小写变体，正式注册前建议再做商标/域名核验。

---

## 4. 推荐方案（分层）【2026-08-23 复核版：包名空闲 ≠ 品牌空闲，已加域名维度】

### 🥇 首选：**agaton**（保留 agate 血统）

- ✅ npm / PyPI / GitHub 全空闲（实测）
- ✅ 域名：`agaton.com`（HTTP 000 疑似空闲）/ `agaton.dev`（000）/ `agaton.io`（404 空闲）——**正式使用前需 WHOIS 确认**（HTTP 000 = 无服务器响应，大概率可注册）
- ✅ 唯一性极强，无任何撞名；迁移成本最低（换品牌名，`agate*` 脚本前缀可留兼容别名）
- ⚠️ 新词无自带含义，需品牌故事（"a-gate-on → 门上的推进"）

### 🥈 备选 A：**turngate**（自然组合词路线，2026-08-23 复核）

- ✅ npm / PyPI 全空闲；`.com` / `.dev` 疑似可注册（HTTP 000，需 WHOIS）
- ✅ **读起来自然**（turn + gate，旋转闸门/翻转闸门——"过闸转弯"，语义直观），回应"agaton 像造词"的顾虑
- ⚠️ GitHub 有 4 个同名仓库（含 ICML 2026 论文 "TurnGate"，AI 域小撞名）——撞名度 4 vs agate 的 1223，可接受但非零

### 🥉 备选 B：**gatelock** / **gateon** / **zhamen**

- gatelock：npm/PyPI 空闲、.com 疑似可注册（语义 gate+lock，直白）
- gateon：三源空闲、.com 疑似可注册（gate+on，略生硬）
- zhamen（闸门）：三源空闲、.com 疑似可注册（中文语义最贴，国际拼读门槛）

### ⚠️ 已淘汰（2026-08-23 域名复核）

- **gatewise**（原首选）：`gatewise.com` 已被使用——**教训：包名空闲 ≠ 品牌空闲，须连域名一起核**
- gatedev / gatework / gatecheck / gateflow / gateops / gateprotocol：`.com` 均被占
- agate-protocol：治标不治本（GitHub 搜索仍被 1223 仓库淹没）

> 核验口径升级：候选必须过 **npm + PyPI + GitHub + 域名(.com/.dev/.io)** 四源检查；HTTP 000 判定为"疑似可注册"，正式使用前 WHOIS/注册商确认。

---

## 5. 迁移成本评估（如果改名为 gatewise）

| 迁移项 | 成本 | 说明 |
|--------|------|------|
| 仓库改名（GitHub settings）| 低 | 原 URL 自动 301 重定向 |
| `~/.agate` 软链/安装路径 | 中 | 协议本体大量引用 `{agate_root}`，路径变量不变则影响可控；`agate-install.py` 需同步 |
| 脚本命名（53 个 `agate-*.py`）| 高 | 建议**分阶段**：先只改品牌层（README/文档/仓库名），脚本内部 `agate_` 前缀保留为兼容层，v2 再统一 |
| 文档内引用（8000+ 行 md）| 高 | 一次性 sed 迁移 + 一致性 gate 校验 |
| git 历史/tag | 零 | git 不感知名字 |
| 用户心智 | 中 | 交接单/CHANGELOG 里写清"曾用名 agate" |

**推荐迁移节奏**：v0.56.0 起 README 标"gatewise (formerly agate)" → 仓库改名 → 下一大版本（v1.0）脚本/文档统一换名 → 保留 `AGATE_*` 环境变量兼容别名 2-3 个版本。

---

## 6. 其他命名备忘

- **中文品牌名建议**：「闸道/门闸」类太生硬；建议直接用英文 gatewise + 中文音译"盖特怀斯"，或取意译"门径"（门=gate，径=wise 之路）
- **域名**：`gatewise.dev` / `gatewise.io` / `gatewise.run`（购买前核验）
- **防再撞车**：注册后立即占 npm/PyPI/GitHub org + 主要域名后缀，避免第三个同名项目出现
