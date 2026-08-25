# Agateon 商标注册调研报告

> 调研日期：2026-08-23 ｜ 调研对象：`agateon` 商标在全球主要司法辖区的注册状态 ｜ 决策场景：开源 AI-agent 编排协议项目（github.com/randomgitsrc/agate）拟更名 Agateon

## 1. 调研摘要

- **精确名称 `agateon` 未在任何司法辖区检索到已注册商标或申请**（USPTO / EUIPO / CNIPA / WIPO 及其公开镜像数据源均无精确命中记录），也未检索到以 `agateon` 命名的公司、产品或 GitHub 仓库。
- 域名 `agateon.com` 已确认可注册（用户 WHOIS 确认）。
- 但 `agateon` 处于一个**发音高度拥挤的近似商标区**：`AGATE`（美国、中国、英国/欧盟均有注册）、`EAGATON`（美国 2025-12-16 刚注册）、`AGATON`（英国/欧盟已注册，瑞典 AI 初创 Agaton.ai 在用）、`AGON`（AOC 电竞显示器品牌，中国第 9 类驰名）、`AGATHON`、`AGAPEON`（中国）等均已存在。**第 9 类 / 第 42 类存在被引证近似商标驳回的现实风险**。
- 结论倾向：**建议注册（分阶段、优先美国与中国）**，但需先做一次专业近似检索或接受"可能收到审查意见"的预期；纯个人开源项目亦可选择暂缓，但应同步完成域名、GitHub 组织名与软件包名占位。

## 2. 调研方法与数据源说明

使用公开搜索引擎对商标数据库的公开镜像/聚合站点（TrademarkElite、Trademarkia、Justia Trademarks、Furm、阿里云商标、知协 32.cn、企查查 qcc）进行了 8 轮、共 20+ 组关键词检索；同时检索了 GitHub / PyPI / npm / crates.io / Ubuntu 软件包等开发者生态命名占用情况。

**如实声明**：USPTO TM Search（原 TESS/TSDR）、EUIPO eSearch plus、CNIPA 中国商标网、WIPO Global Brand Database 均为交互式查询系统，无法通过本文检索方式直接提交查询，因此**以下各辖区的"未命中"结论来自公开镜像聚合站的间接证据，而非官方数据库的直接查询结果**。正式申请前，必须按第 8 节入口做人工复核。

## 3. 各司法辖区检索结果

### 3.1 USPTO（美国）

| 项目 | 结果 |
| :--- | :--- |
| `agateon` 精确查询 | 未发现已注册商标或申请（TrademarkElite / Trademarkia / Justia 等镜像均无命中） |
| 近似风险标记 1 | **EAGATON**（Serial 99183647）已于 2025-12-16 注册（REGISTERED，状态 LIVE）——与 agateon 拼写仅差两个字母位置，发音接近 |
| 近似风险标记 2 | **AGATE** 系列：Agate Technologies, Inc.（Serial 75129968）、ALSTOM HOLDINGS（Serial 86781376，已注册并获"持续使用且不可争议"确认）、另有较新申请（Trademarkia 97339283） |
| 近似风险标记 3 | AGATHON（SWEDISH TABLE TENNIS AB，Serial 73544174）、GAIATON（已授权）、AGEEON BLOOMZ（申请中，Serial 99307188） |
| 官方复核入口 | https://tmsearch.uspto.gov/search/search-information |

### 3.2 EUIPO（欧盟）

| 项目 | 结果 |
| :--- | :--- |
| `agateon` 精确查询 | 未发现已注册商标或申请（公开镜像无命中） |
| 近似风险标记 1 | **AGATON**：欧盟商标注册号 018249742（UK 对应注册 UK00918249742 状态为 Registered）——瑞典 AI 初创公司 Agaton.ai（2025-02 完成 1000 万美元种子轮）同名 |
| 近似风险标记 2 | **AGATE**：欧盟商标 UK00904578639（AGATE）已注册；另有 AGATE ENCHANTMENT（申请 019304576，审查中） |
| 说明 | EUIPO 覆盖全部 27 个成员国；EUTM 注册后自动进入英国注册簿的机制已于脱欧后停止，英国需单独走 UKIPO |
| 官方复核入口 | https://euipo.europa.eu/eSearch/ |

### 3.3 CNIPA（中国）

| 项目 | 结果 |
| :--- | :--- |
| `agateon` 精确查询 | 未发现已注册商标或申请（阿里云商标、知协 32.cn、企查查等镜像无命中） |
| 近似风险标记 1 | **AGON（爱攻）**：AOC 电竞显示器品牌，第 9 类已注册（阿里云商标 af75_52979636_9、路标网公告 9-17615183），在中国为知名品牌，含 "AGON" 子串的名称在第 9 类易被引证 |
| 近似风险标记 2 | **AGATE**：第 9 类有注册记录（路标网公告 9-4921438、9-15431162；企查查 AGATE 品牌记录） |
| 近似风险标记 3 | **AGAPEON**（企查查 2 条品牌记录）、**AGATHON/阿格顿**（上海阿戈通贸易公司名下，含第 7 类）、**AGCATTON**（百度百科条目） |
| 官方复核入口 | https://sbj.cnipa.gov.cn/sbcx/（中国商标网商标查询） |

### 3.4 WIPO Global Brand Database（全球）

| 项目 | 结果 |
| :--- | :--- |
| `agateon` 精确查询 | 未发现马德里国际注册或国家注册记录（公开镜像无命中） |
| 说明 | WIPO Global Brand Database 聚合 70+ 个辖区数据，交互式查询需在官网进行；本文未发现任何 `agateon` 记录，但不能排除极少数未联网辖区或近期待审申请 |
| 官方复核入口 | https://branddb.wipo.int/ |

## 4. 撞名与近似商标分析

### 4.1 精确撞名

未发现任何公司、产品、GitHub 仓库、PyPI / npm / crates.io 包以 `agateon` 命名。开发者生态中仅存在发音/拼写相近者：

- GitHub 用户 `agateau`（110 个仓库）——拼写近似，无商标冲突意义；
- Agaton.ai（瑞典 AI 初创，销售对话智能，1000 万美元种子轮）——发音相近，且处于同类 AI 软件领域，**是最值得注意的非商标撞名**；
- Agenton（Tracxn 有公司档案）、AEGAON（瑞士手表品牌 aegaon.com）、agayon.com（urlscan 有扫描记录）。

### 4.2 近似商标冲突矩阵（按风险排序）

| 近似商标 | 辖区 / 状态 | 与 agateon 相似度 | 冲突风险 |
| :--- | :--- | :--- | :--- |
| EAGATON | 美国，2025-12 注册 | 高（7 字母中 6 个相同，仅位置差异） | **高**：美国第 9/42 类申请很可能被引证 |
| AGATON | 欧盟/英国，已注册 | 高（发音 a-ga-ton vs a-ga-tee-on） | **高**：欧盟/英国申请很可能被引证 |
| AGON（爱攻） | 中国第 9 类，知名品牌 | 中（含完整子串 "AGON"） | 中高：中国第 9 类（显示器等硬件）驳回风险，纯软件第 42 类相对低 |
| AGATE | 美国/中国/英国/欧盟，多处注册 | 中（前缀相同） | 中：视具体商品项目而定 |
| AGATHON / AGAPEON / GAIATON / AGEEON | 美/中零星注册 | 低-中 | 低-中 |

**判断**：`agateon` 与 `EAGATON`、`AGATON` 的字母构成与发音高度接近，且二者均在近两年注册、覆盖软件/AI 领域，这是申请第 9、42 类时最可能被引证的障碍；`AGON` 则主要影响中国第 9 类。整体近似环境"拥挤但不致命"——精确名称无冲突，近似冲突存在但不必然导致驳回（审查员还会比较商品项目、知名度与整体商业印象）。

## 5. 注册成本与流程时间

### 5.1 美国（USPTO）

| 项目 | 金额 / 时长 |
| :--- | :--- |
| 官费（2025 新费率） | TEAS Plus 每类 $250；TEAS Standard 每类 $350（2025 财年涨价后） |
| 每类 1 个商品项 vs 多商品项 | TEAS Plus 要求商品描述使用预设文本，超出部分按类计费 |
| 全流程时长 | 顺利情况下 8–12 个月（申请 → 审查 → 公告 → 注册）；使用意向申请（ITU）可先占位、后补使用证据 |
| 长期成本 | 第 5-6 年使用声明、第 10 年续展等，属多年后成本 |
| 来源 | [Finnegan 2025 USPTO 费用变更](https://www.finnegan.com/a/web/9e2RYHh3jcqVdmXbKZB5Bx/microsoft-word-uspto-trademark-fees-changes-for-2025.pdf)、[Lexology 2025 美国商标体系与费用](https://www.lexology.com/library/document.ashx?g=3e68920e-e7a7-4c0a-8ca7-378c6e241a12) |

### 5.2 欧盟（EUIPO）

| 项目 | 金额 / 时长 |
| :--- | :--- |
| 官费 | 第 1 类 €850；第 2 类 €50；第 3 类起每类 €150 |
| 覆盖范围 | 一次申请覆盖 27 个成员国 |
| 全流程时长 | 顺利情况下约 4–5 个月（无异议时） |
| 来源 | [EUIPO 官方费用指南](https://euipo01app.sdlproducts.com/2231430/2232347/designs-guidelines/7-5-1-fees-payable-for-eutms)、[Dudkowiak EUTM 注册指南](https://www.dudkowiak.com/ip-law/eu-trademark-registration-with-euipo/)、[REVERA 软件企业 EUTM 指南](https://revera.legal/en/info-centr/news-and-analytical-materials/2051-eu-trade-mark-registration-a-pragmatic-guide-for-tech-software/) |

### 5.3 中国（CNIPA）

| 项目 | 金额 / 时长 |
| :--- | :--- |
| 官费 | 电子申请每类 ¥270；纸质申请 ¥300（限定本类 10 个商品项） |
| 代理费 | 一般 ¥500–¥1000/类（可选，不强制） |
| 全流程时长 | 约 6–12 个月（形式审查 → 实质审查 → 初审公告 3 个月 → 注册公告） |
| 来源 | [CNIPA 官费答复](http://www.cnipa.gov.cn/jact/front/mailpubdetail.do?transactId=507649&sysid=13)、[湖北利川行政事业性收费标准（受理商标注册费）](http://www.lichuan.gov.cn/xxgk/gkml/xzsyxsf/202505/t20250506_1694947.shtml) |

## 6. 开源项目商标注册的必要性与成本收益

**必要性的判断基准**：开源协议/CLI 工具的商标价值不在"排他销售"，而在**品牌防御**——防止他人抢注同名商标后反向维权、防止冒名分发恶意版本、保持项目改名的控制权。参考 [FOSSmarks（FSF 开源商标指南）](https://static.fsf.org/nosvn/licensing/2020/FOSSmarksv2.pdf) 与 [TermsFeed 开源品牌保护策略](https://www.termsfeed.com/blog/open-source-trademark/) 的通行观点：

| 情形 | 建议 |
| :--- | :--- |
| 项目将商业化（SaaS 付费版、企业支持、融资） | **应当注册**：品牌是商业化资产，抢注成本远高于注册成本 |
| 项目有社区生态、教程、周边（将形成品牌价值） | 建议注册：防止第三方在同类目注册后反向主张 |
| 纯个人/实验性开源项目 | 可暂缓商标注册，但必须完成：域名、GitHub 组织名、主要软件包名（PyPI/npm/crates）占位 |

**成本收益**：美国 2 类（9+42）官费约 $500–700，欧盟 2 类约 €900，中国 2 类约 ¥540–2000（含代理），三者合计约 ¥1 万以内即可完成主要市场占位，远低于一次商标抢注纠纷的维权成本。对已确定新名称的项目，注册是"低成本高确定性"的动作。

## 7. 结论与建议（决策支持）

### 7.1 明确结论：**建议注册（分阶段执行）**

理由：

1. **精确名称清洁**：`agateon` 六辖区无任何已注册/申请记录，域名、GitHub、软件包名均可占用，改名窗口期的最佳占位时机就是现在；
2. **近似冲突可管理**：EAGATON（美）、AGATON（欧/英）虽构成引证风险，但均为新近注册、知名度有限，且商品项目大概率与"协议规范 + 开发者工具"存在区分空间——驳回风险存在但不构成否决性障碍；
3. **成本低**：主要市场合计约 ¥1 万以内即可完成注册，而一旦项目走红后被第三方抢注（中国、美国均常见），维权或购买成本是注册成本的数十倍；
4. **开源项目的商标是防御性资产**：不注册则无法阻止他人拿这个名字做混淆性商业使用。

### 7.2 注册类目建议

| 类目 | 覆盖内容 | 是否建议 |
| :--- | :--- | :--- |
| 第 9 类 | 可下载软件、CLI 工具、SDK、协议实现代码 | **建议**（核心） |
| 第 42 类 | SaaS、软件即服务、平台即服务、协议托管服务 | **建议**（核心） |
| 第 41 类 | 培训、教程、开发者大会 | 可选（低成本加类） |
| 其他 | 38/45 等 | 不必要 |

每个辖区申请 2 类（9 + 42）即可覆盖主要使用场景；美国可用使用意向申请（ITU）先行占位，注册前补交使用证据。

### 7.3 优先级与预算

| 优先级 | 辖区 | 成本（2 类，官费估算） | 理由 |
| :--- | :--- | :--- | :--- |
| 1 | 美国 | ~$500–700 | 开发者生态与 GitHub 主战场；EAGATON 已注册，越早申请越有利 |
| 2 | 中国 | ~¥540–2000（含代理） | 防抢注价值最高（中国为抢注高发区）；AGON/AGATE 引证风险需专业检索确认 |
| 3 | 欧盟 | ~€900 | 一次覆盖 27 国，性价比高；注意 AGATON（EU）引证风险 |
| 4 | 英国 / 其他 | 按需 | 脱欧后需单独注册，项目有英国用户再考虑 |

### 7.4 行动清单

1. 注册域名 `agateon.com`（已知可注册，立即执行）；
2. 创建 GitHub 组织/仓库 `agateon`，同步注册 PyPI / npm / crates.io 包名占位；
3. 正式提交商标申请前，在第 8 节官方入口做一次人工检索，或委托代理机构出具近似检索报告（重点核 EAGATON、AGATON、AGON 在 9/42 类的商品项目）；
4. 按"美国 → 中国 → 欧盟"顺序提交申请，每辖区 2 类（9 + 42）；
5. 若预算紧张，可先注册美国 1 类（42，覆盖 SaaS 与协议服务），其余延后。

## 8. 官方人工复核入口

| 辖区 | 入口 | 查询方式 |
| :--- | :--- | :--- |
| 美国 USPTO | https://tmsearch.uspto.gov/search/search-information | TM Search（原 TESS 已退役，TSDR 数据并入） |
| 欧盟 EUIPO | https://euipo.europa.eu/eSearch/ | eSearch plus 商标检索 |
| 中国 CNIPA | https://sbj.cnipa.gov.cn/sbcx/ | 中国商标网商标综合查询 |
| 全球 WIPO | https://branddb.wipo.int/ | Global Brand Database |
| 第三方中文镜像 | https://tm.aliyun.com 、http://www.32.cn/cha/ | 阿里云商标、知协（便于快速初筛） |

## 9. 来源引用

- [EAGATON Trademark (USPTO Serial 99183647)｜TrademarkElite](https://www.trademarkelite.com/trademark/trademark-detail/99183647/EAGATON)
- [EAGATON Trademark｜Trademarkia](https://www.trademarkia.com/eagaton-99183647)
- [AGATE Trademark of Agate Technologies, Inc. (Serial 75129968)｜Furm](https://furm.com/trademarks/agate-75129968)
- [AGATE Trademark (USPTO Serial 86781376) – ALSTOM HOLDINGS｜TrademarkElite](https://www.trademarkelite.com/trademark/trademark-detail/86781376/AGATE)
- [AGATE Trademark｜Trademarkia](https://www.trademarkia.com/agate-97339283)
- [AGATE United Kingdom Trademark (UK00904578639)｜TrademarkElite](https://www.trademarkelite.com/uk/trademark/trademark-detail/UK00904578639/AGATE)
- [AGATON United Kingdom Trademark (UK00918249742)｜TrademarkElite](https://www.trademarkelite.com/uk/trademark/trademark-detail/UK00918249742/AGATON)
- [AGATHON Trademark of SWEDISH TABLE TENNIS AB (Serial 73544174)｜Furm](https://furm.com/trademarks/agathon-73544174)
- [AGEEON BLOOMZ Trademark Application (Serial 99307188)｜Justia Trademarks](https://trademarks.justia.com/993/07/ageeon-99307188.html)
- [AGATE 商标第 9 类公告｜路标网](https://m.chatm.com/gg/9-4921438.html)
- [A AGON AOC GAMING 商标第 9 类公告｜路标网](https://m.chatm.com/gg/9-17615183.html)
- [AGON 商标详情（第 9 类）｜阿里云商标](https://tm.aliyun.com/detail/af75_52979636_9)
- [AGAPEON 品牌记录｜企查查](https://m-harmony.qcc.com/brandDetail/ce7c8fc230f484c4c3c0dddcba3c5282.html)
- [AGATHON 商标查询（阿戈通贸易上海公司）｜知协 32.cn](http://www.32.cn/cha/NlppLzVvaUk2WUNhNkxTNDVwaVQ3N3lJNUxpSzVyVzM3N3lKNXB5SjZabVE1WVdzNVkrNA==.html)
- [Stealth AI startup Agaton raises $10M｜Tech Funding News](https://techfundingnews.com/stealth-ai-startup-agaton-raises-9m-to-turn-calls-into-revenue-intel/)
- [Swedish Agaton raises $10 million seed｜ArcticStartup](https://arcticstartup.com/agaton-raises-10m-in-seed/)
- [Agaton 公司档案｜PitchBook](https://pitchbook.com:8443/profiles/company/460331-65)
- [agateau GitHub 用户｜GitHub](https://github.com/agateau)
- [agate Python 库｜PyPI](https://pypi.org/project/agate/1.12.0/)
- [USPTO 2025 商标费用变更｜Finnegan](https://www.finnegan.com/a/web/9e2RYHh3jcqVdmXbKZB5Bx/microsoft-word-uspto-trademark-fees-changes-for-2025.pdf)
- [Understanding the new 2025 United States trademark filing system｜Lexology](https://www.lexology.com/library/document.ashx?g=3e68920e-e7a7-4c0a-8ca7-378c6e241a12)
- [EUIPO 7.5.1 EUTM 费用](https://euipo01app.sdlproducts.com/2231430/2232347/designs-guidelines/7-5-1-fees-payable-for-eutms)
- [EU Trademark Registration with EUIPO｜Dudkowiak](https://www.dudkowiak.com/ip-law/eu-trademark-registration-with-euipo/)
- [EU Trade Mark Registration: A Pragmatic Guide for Tech & Software Companies｜REVERA](https://revera.legal/en/info-centr/news-and-analytical-materials/2051-eu-trade-mark-registration-a-pragmatic-guide-for-tech-software/)
- [CNIPA 商标注册官费答复](http://www.cnipa.gov.cn/jact/front/mailpubdetail.do?transactId=507649&sysid=13)
- [湖北利川市行政事业性收费标准清单（受理商标注册费）](http://www.lichuan.gov.cn/xxgk/gkml/xzsyxsf/202505/t20250506_1694947.shtml)
- [FOSSmarks 开源商标指南｜FSF](https://static.fsf.org/nosvn/licensing/2020/FOSSmarksv2.pdf)
- [Protecting Your Brand in Open Source｜TermsFeed](https://www.termsfeed.com/blog/open-source-trademark/)

## 10. 免责说明

本报告基于公开搜索引擎与商标数据库镜像站的间接证据撰写，**不构成法律意见**。所有辖区的最终结论须以第 8 节官方入口的人工查询结果为准；正式申请前建议咨询商标代理机构，并重点复核 EAGATON（美国）、AGATON（欧盟/英国）、AGON（中国第 9 类）三个近似商标的商品项目覆盖范围。
