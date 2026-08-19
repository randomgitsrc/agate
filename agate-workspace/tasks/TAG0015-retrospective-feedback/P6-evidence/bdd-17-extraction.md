# BDD-17 证据：结构化提取能力（依赖 BDD-6/BDD-7）

## Then 子句逐项核对

Given：一份复盘文档已包含 BDD-6 定义的 frontmatter 机器字段（`mechanism_issues`/
`execution_issues`/`feedback_ready`）与 BDD-7 定义的「## agate 反馈」结构化节。
When：运行 `agate-feedback.py` 指向该复盘文件。
Then：脚本正确解析并输出结构化数据（能提取 `mechanism_issues` 列表内容，不报解析错误）。

## 本轮独立构造的样例文件（非转抄 test_agate_feedback.py 的 fixture，内容独立编写）

`/tmp/.../p6-feedback/myproject-secret-repo/retrospective.md`：

```yaml
---
phase: P8
task_id: T777
mechanism_issues:
  - "check-xyz.py 在 /home/kity/oclab/agate/.worktrees/agate-TAG0015/myproject-secret-repo/scripts/build.sh 里硬编码了绝对路径，导致 CI 换机器就炸"
execution_issues:
  - "implementer 漏跑 lint，被 review 打回"
feedback_ready: true
---

# T777 复盘

## agate 反馈

本次在 myproject-secret-repo 项目里发现：agate 的 check-xyz.py 机制没有覆盖"路径硬编码检测"，
相关证据见 /home/kity/oclab/agate/.worktrees/agate-TAG0015/myproject-secret-repo/scripts/build.sh。
另外 /etc/some-other-project/secrets.env 也被误提交过一次（项目外路径，不属于本项目根）。
```

## 实际运行命令与输出

```
$ cd myproject-secret-repo
$ AGATE_FEEDBACK=on python3 agate/scripts/agate-feedback.py retrospective.md --project-name myproject-secret-repo

{
  "task_id": "T777",
  "feedback_ready": true,
  "mechanism_issues": [
    "check-xyz.py 在 <PATH> 里硬编码了绝对路径，导致 CI 换机器就炸"
  ],
  "execution_issues": [
    "implementer 漏跑 lint，被 review 打回"
  ],
  "agate_feedback_section": "本次在 <PROJECT> 项目里发现：agate 的 check-xyz.py 机制没有覆盖"路径硬编码检测"，\n相关证据见 <PATH>\n另外 <PATH> 也被误提交过一次（项目外路径，不属于本项目根）。"
}
...
EXIT_CODE: 0
```

## 判定

**满足**——`mechanism_issues` 列表内容被正确提取（原文"check-xyz.py 在...硬编码了绝对路径，
导致 CI 换机器就炸"的语义完整保留，仅路径被脱敏），`task_id`/`feedback_ready`/
`execution_issues`/「## agate 反馈」节文本均被正确解析并输出为结构化 JSON，未报任何解析错误，
`EXIT_CODE: 0`。脱敏是 BDD-18 的验收范围，见 `bdd-18-anonymize.md`，本文件只判定"是否正确
解析且不报错"这一 BDD-17 的核心要求。
