# BDD-18 证据：匿名化（项目名/绝对路径脱敏）

## Then 子句逐项核对

Given：复盘文档「## agate 反馈」节内容包含项目名 / 绝对文件路径等项目特定信息。
When：`agate-feedback.py` 提取。
Then：输出的结构化 JSON 不包含原始项目名 / 绝对路径等可识别项目身份的字段（脱敏规则至少
覆盖：项目名替换为占位符、绝对路径截断为相对路径或移除）。

## 场景 A：路径不在项目根内（应整体替换为 `<PATH>`）

样例文件同 `bdd-17-extraction.md`，绝对路径
`/home/kity/oclab/agate/.worktrees/agate-TAG0015/myproject-secret-repo/scripts/build.sh`（当时
`os.getcwd()` 是 `/tmp/.../myproject-secret-repo`，与该路径不匹配前缀）与
`/etc/some-other-project/secrets.env`（明确项目外路径）。

```
$ AGATE_FEEDBACK=on python3 agate-feedback.py retrospective.md --project-name myproject-secret-repo
...
"mechanism_issues": ["check-xyz.py 在 <PATH> 里硬编码了绝对路径，导致 CI 换机器就炸"]
"agate_feedback_section": "...相关证据见 <PATH>\n另外 <PATH> 也被误提交过一次（项目外路径，不属于本项目根）。"
```

两处绝对路径均被替换为 `<PATH>`，原始路径字符串（含目录名 `myproject-secret-repo`、
`/etc/some-other-project`）在输出 JSON 中不再出现。

## 场景 B：路径在项目根内（应截断为相对路径，而非整体移除）

本轮独立构造第二份样例（`retrospective2.md`），cwd 与文本中路径前缀一致：

```yaml
---
phase: P8
task_id: T778
mechanism_issues:
  - "配置文件路径 $WORK/myproject-secret-repo/config/secrets.yaml 被误打进日志"
execution_issues: []
feedback_ready: true
---

# T778 复盘

## agate 反馈

MyProject-Secret-Repo 团队反馈：check-abc.py 未覆盖此场景，证据路径 $WORK/myproject-secret-repo/config/secrets.yaml。
```

```
$ cd $WORK/myproject-secret-repo   # 与文本中绝对路径前缀一致
$ AGATE_FEEDBACK=on python3 agate-feedback.py retrospective2.md

{
  "task_id": "T778",
  "feedback_ready": true,
  "mechanism_issues": ["配置文件路径 config/secrets.yaml 被误打进日志"],
  "execution_issues": [],
  "agate_feedback_section": "<PROJECT> 团队反馈：check-abc.py 未覆盖此场景，证据路径 config/secrets.yaml。"
}
EXIT_CODE: 0
```

## 逐项核对

| Then 要求 | 场景 A（路径在项目根外） | 场景 B（路径在项目根内） |
|-----------|--------------------------|----------------------------|
| 绝对路径截断为相对路径或移除 | 整体替换为 `<PATH>`（移除） | 截断为 `config/secrets.yaml`（相对路径，保留仓库内信息但去掉可识别的绝对前缀） |
| 项目名替换为占位符 | `myproject-secret-repo`（全词、大小写不敏感）在 agate_feedback_section 内被替换为 `<PROJECT>` | `MyProject-Secret-Repo`（大小写不同的变体）同样被匹配替换为 `<PROJECT>`——验证大小写不敏感规则 |
| 输出 JSON 不含原始项目名/绝对路径 | 两个 JSON 输出均不含 `myproject-secret-repo`/`/home/...`/`/etc/...` 原始字符串 | 同上 |

## 判定

**满足**——本轮独立构造两个覆盖 P2-design.md 候选方案 B1 两条规则（路径截断 vs 整体替换，
按是否在项目根内分流）的场景，实跑观察到脱敏在两种路径归属下均按预期工作，且项目名替换验证
了大小写不敏感匹配。原始项目名/绝对路径在最终输出 JSON 中均不可见，符合 Then 子句"不包含
原始项目名/绝对路径等可识别项目身份的字段"的要求。
