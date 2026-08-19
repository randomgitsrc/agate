# BDD-19 证据：AGATE_FEEDBACK 开关默认 off

## Then 子句逐项核对

Given：未设置 `AGATE_FEEDBACK` 环境变量（或显式设为 `off`）。
When：运行 `agate-feedback.py`。
Then：脚本不产生任何提取输出（不生成 JSON、不打印内容），exit code 提示"功能未启用"而非
静默失败。

## 场景 A：未设置环境变量（本轮独立用 `env -u AGATE_FEEDBACK` 显式确保未设置，排除测试环境
残留的干扰）

```
$ cd myproject-secret-repo
$ env -u AGATE_FEEDBACK python3 agate/scripts/agate-feedback.py retrospective.md

agate-feedback: 功能未启用（设置 AGATE_FEEDBACK=on 启用）
EXIT_CODE: 2
```

stdout 为空（无 JSON、无 Markdown 输出），stderr 输出明确的"功能未启用"文案并提示如何启用，
exit code 为 2（区别于 0=成功 / 1=真实错误，见脚本 §「BDD-19」注释"2 = 功能性跳过，区别于
1 = 真实错误"）。

## 场景 B：显式设为 off

```
$ AGATE_FEEDBACK=off python3 agate/scripts/agate-feedback.py retrospective.md

agate-feedback: 功能未启用（设置 AGATE_FEEDBACK=on 启用）
EXIT_CODE: 2
```

与场景 A 结果一致（未设置 与 显式 off 行为等价）。

## 逐项核对

| Then 要求 | 实际 |
|-----------|------|
| 不生成 JSON | stdout 为空，未观察到任何 `{` 开头的结构化输出 |
| 不打印内容 | stdout 完全无输出（"agate-feedback: 功能未启用..."文案打印到 stderr，非 stdout） |
| exit code 提示"功能未启用"而非静默失败 | exit code 2 + stderr 明确文案"功能未启用（设置 AGATE_FEEDBACK=on 启用）"，非 exit 0 静默退出、也非无提示的 exit 1 |

## 判定

**满足**——本轮两个独立场景（未设置 / 显式 off）均验证了脚本不产生任何提取输出、exit code
非 0（=2）、stderr 有明确"功能未启用"提示，不是静默失败（静默失败的反例是"exit 0 + 无任何
输出"，本脚本明确用非零 exit code + stderr 文案区分于静默失败）。
