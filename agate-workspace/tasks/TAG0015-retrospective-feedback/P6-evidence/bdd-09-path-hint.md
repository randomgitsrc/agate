# BDD-9 独立实跑证据：check-retrospective.py 路径提示文案

构造场景：task_dir 含 .state.yaml（P1 retry 超限 4/3）+ P1-requirements.md 含 [SCOPE+]，
触发标准异常模式提醒，观察 stderr 路径文案。

```
task_id: T998
phase: P3
retries:
  P1: [{round: 1}, {round: 2}, {round: 3}, {round: 4}]
---P1-requirements.md---
# P1
- [SCOPE+] 发现新隐含需求：xxx
```

运行命令：python3 agate/scripts/check-retrospective.py $TASK_DIR .state.yaml

实际 stderr 输出：
```
EXIT_CODE: 0
```

断言核对：
- 含 `tasks/{Txxx}/retrospective.md`：是
- 不含 `docs/releases`：是——零命中
