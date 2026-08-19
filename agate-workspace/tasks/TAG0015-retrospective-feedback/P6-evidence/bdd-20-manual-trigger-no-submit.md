# BDD-20 证据：触发方式与产出边界（不自动提交）

## Then 子句逐项核对

Given：用户或 agate 项目组要求某外部项目为其 agate 使用经历登记「## agate 反馈」节后手动
运行 `agate-feedback.py`（不存在任何自动触发该脚本的钩子/CI/cron）。
When：脚本执行完成。
Then：产出物是一份待人工提交的内容（结构化 JSON + 面向 issue/PR 的文本片段），脚本本身不
执行任何网络提交动作（不调用 `gh`/`git push` 等提交命令）。

## 子项 1：脚本产出物是 JSON + Markdown 文本片段（本轮实跑，见 bdd-17/18 证据的完整输出）

```
$ AGATE_FEEDBACK=on python3 agate-feedback.py retrospective.md --project-name myproject-secret-repo
{
  "task_id": "T777", ...
}

---

# agate 反馈草稿（待人工提交）

## 机制缺口
- check-xyz.py 在 <PATH> 里硬编码了绝对路径，导致 CI 换机器就炸
...
---
请提交前人工复核以下内容是否包含未预期的项目特定信息
```

输出末尾固定一行"请提交前人工复核..."，明确产出物是**待人工提交**的草稿，非已提交内容。

## 子项 2：脚本源码不含网络提交调用（本轮独立 grep）

```
$ grep -n "subprocess" agate/scripts/agate-feedback.py
21:import subprocess
56:        proc = subprocess.run(

$ grep -n "git push\|gh " agate/scripts/agate-feedback.py
（零命中）
```

唯一一处 `subprocess.run` 调用的是本地脚本间通信 `agate-md-field-get.py`（ADR-007 单一
双读工具复用，见 `agate/scripts/agate-feedback.py:46-65` `_md_field_get` 函数），非网络提交
操作。

## 子项 3：不存在自动触发该脚本的钩子/CI/cron（本轮独立全仓 grep）

```
$ grep -rn "agate-feedback.py" --include="*.yml" --include="*.yaml" .
（零命中）
$ grep -l "agate-feedback.py" agate/scripts/pre-commit-gate.py
（零命中/文件不含该引用）
$ find . -path "*/.github/workflows/*" -name "*.yml" | xargs grep -l "agate-feedback" 2>/dev/null
（零命中）
```

三处检索（CI workflow yaml、pre-commit-gate.py、GitHub Actions 工作流目录）均未发现任何
自动触发 `agate-feedback.py` 的机制，与 Given 子句"不存在任何自动触发该脚本的钩子/CI/cron"
的前提一致（脚本本身也不是任何 gate_commands 声明的一部分，只能被人工在命令行手动调用）。

## 判定

**满足**——三个子项均本轮独立核实：产出物确为待人工提交的 JSON + Markdown 文本片段（末尾
显式提示人工复核后提交）；脚本源码不含 `git push`/`gh` 调用，唯一的 `subprocess` 调用是本地
脚本间通信；全仓无任何 hook/CI/cron 自动触发该脚本的记录。
