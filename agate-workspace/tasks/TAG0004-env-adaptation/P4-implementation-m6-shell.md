---
phase: P4
task_id: TAG0004-env-adaptation
type: implementation
parent: P2-design.md
trace_id: TAG0004-P4-20260813
status: draft
created: 2026-08-13
agent: implementer
---

# P4 实现记录（M6 补充：shell 侧 CRLF 容错）

implementation_dir: `agate/scripts/`

## 任务范围

只补 check-gate.sh 的 frontmatter 提取 CRLF 容错（bdd-14），不涉及其余逻辑。py 侧 CRLF 容错（agate-md-field-get.py / agate-frontmatter-check.py）已由组 3a 完成；本任务在组 1（M4 L356/357 + RM-AG0001）基础上追加 M6。

## 改动清单

### 文件：`agate/scripts/check-gate.sh`

**方案**：P2-design 候选 5A（frontmatter 提取处 CRLF 归一，选定）。

对全部 8 处 `sed -n '/^---$/,/^---$/p'` frontmatter 提取，改为 sed 首命令剥行尾 `\r`：

```
sed -n 's/\r$//; /^---$/,/^---$/p'
```

**改动位置（8 处）**：

| 行号 | 变量 | 阶段 |
|------|------|------|
| L51 | P1_REVIEW_STATUS | P1 |
| L56 | P1_REVIEW_AGENT | P1 |
| L82 | NC_RESOLVED_PRESENT | P1 |
| L102 | SG_RESOLVED_PRESENT | P1 |
| L162 | P2_REVIEW_STATUS | P2 |
| L167 | P2_REVIEW_AGENT | P2 |
| L231 | P4_REVIEW_STATUS | P4 |
| L236 | P4_REVIEW_AGENT | P4 |

L51 上方新增一段注释说明 M6 语义（CRLF 容错 + LF 不变，BDD-14/15 锚点）。

## 为什么不用"仅改 sed 范围模式 /^---\r*$/"

dispatch-context 提到两种做法（tr -d '\r' 管道 或 sed 模式 /^---\r*$/）。实测（od -c 验证）：

- **仅改范围模式 `/^---\r*$/`**：`---\r` 能匹配定界，但正文行 `status: approved\r` 的 `\r` 仍残留 → 提取出的值带 `\r`，`[ "$P1_REVIEW_STATUS" != "approved" ]` 判不等 → 依旧失败。
- **`s/\r$//` 首命令 + 原范围模式**：先剥每行行尾 `\r`，定界与字段值一并归一，CRLF 提取值纯净（od 验证 `approved\n`）；LF 文件 `s/\r$//` 无匹配，行为与原来完全一致。

选后者：单点改动、不新增管道进程、对 8 处统一、天然满足 BDD-15（LF 回归守卫）。

## 自查结果（自查 ≠ P5 gate）

| 检查 | 命令 | 结果 |
|------|------|------|
| bdd-14 红灯变绿 | `bats --filter 'bdd-14' check-gate.bats` | 1/1 通过（exit 2） |
| 全量 check-gate.bats | `bats check-gate.bats` | 117/117 通过，无回归 |
| shellcheck | `shellcheck -S warning agate/scripts/check-gate.sh` | 0 error |
| P2 CRLF 手工验证 | CRLF P2-review/P2-design | exit 2（提取成功） |
| P4 CRLF 手工验证 | CRLF P4-review + git staged | status=approved / agent=reviewer 提取正确 |

## [PROD_NOT_TOUCHED]

本次改动仅限 worktree 的 `agate/scripts/check-gate.sh`，未触碰主 checkout、`~/.agate`、生产环境或协议文档。

## 说明

- 未修改任何测试文件（bdd-14 契约原样变绿）。
- 组 1 的 M4（L356/357）与 RM-AG0001（L69/71/89/109/125/129）改动未受影响。
- check-p6-provenance.sh 也有 1 处同类 sed（L20），但不在本组文件范围（只改 check-gate.sh + 按需 check-frontmatter.sh 链路），且无对应红灯测试，未动。
