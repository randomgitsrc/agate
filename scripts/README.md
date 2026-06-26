# 协议结构一致性检查 (P3-1)

> 回应 `LIMITATIONS.md`「局限 5：协议文档自身的内部一致性不在流程内」。
> 让 agate 协议文档自身也享受到它一直在鼓吹的「机器可判定的守护」。

## 它解决什么

agate 教别人「gate 必须机器可判定」，但自己的文档一致性此前全靠人肉维护——
评审 `agate-review-20260626-1.md` 挖出的低级错误（LICENSE 缺失、死引用、YAML 不可解析、
字段集不一致、清单计数对不上）就是实证。这个脚本把其中**可机器判定的结构一致性**自动化，
复发即拦。

**只做结构一致性，不碰语义一致性**——后者不可机器判定（协议自己也这么说），不在范围内。

## 6 类检查

| 检查 | 抓什么 | 对应评审条目 |
|------|--------|-------------|
| CHECK 1 | 所有 ```yaml 代码块可被解析（含占位符的会先 sanitize 再校验缩进） | P0-3 |
| CHECK 2 | 协议文件引用的 docs/assets/scripts 路径真实存在 | P0-4, P1-3 |
| CHECK 3 | 协议文件无硬编码行号引用 `xxx.md L123`（应用节标题） | P1-4 |
| CHECK 4 | `gate_commands` 键集合跨文件一致（以 architect.md 为权威） | P1-2 |
| CHECK 5 | 「N 个协议文件」计数声明 == 实际列表长度 | P1-1 |
| CHECK 6 | README LICENSE 徽章指向的文件存在 + gstack MIT 归属保留 | P0-2 |

## 用法

```bash
# 从仓库根运行
python3 scripts/check-protocol-consistency.py

# WARNING 也判失败（更严格）
python3 scripts/check-protocol-consistency.py --strict

# 机器可读输出（CI 消费）
python3 scripts/check-protocol-consistency.py --json
```

依赖：Python 3.8+ 和 `pyyaml`（`pip install pyyaml`）。

退出码：`0` = 无 ERROR；`1` = 有 ERROR；`2` = 仅 WARNING 且加了 `--strict`。

## 分级设计（避免假阳性爆炸）

脚本区分两类文件，避免误报：

- **协议文件**（WORKFLOW.md / dispatch-protocol.md / assets/ 等运行时遵循的规范）
  → 严格检查，死链、行号引用一律 ERROR
- **叙事文件**（docs/plans/ docs/reviews/ 等历史评审与计划）
  → 它们经常**引述**别处的旧问题（含已修复的行号、提议中的未来文件），死链降级为 WARNING

YAML 检查还区分：
- **契约结构 YAML**（缩进错误 = 真问题）→ 缩进类错误保持 ERROR
- **说明性示例 YAML**（含 `@`/反引号等 YAML 保留字符的标量）→ 降级 WARNING，提示加引号即可

## CI

`.github/workflows/protocol-consistency.yml` 已配置：每次 push / PR 自动运行，默认 ERROR 阻断、
WARNING 放行。想让 WARNING 也阻断，把 workflow 里的命令改成加 `--strict`。

## 已知 WARNING（当前仓库，均非缺陷）

跑当前（已修复的）仓库会有 4 个 WARNING，都是预期内的、不需修：
1. `analyst.md` 的 capability_requirements 示例含 `@vision-helper`（YAML 保留字符，加引号更规范，但作为示例无害）
2-4. 几处叙事文件引用了「提议中但尚未创建」的文件（如本脚本早期提议的 `.sh` 版本名）

要消除 WARNING 1，给 analyst.md 那行加引号：`- "@vision-helper（若可调用，作为补充）"`。
