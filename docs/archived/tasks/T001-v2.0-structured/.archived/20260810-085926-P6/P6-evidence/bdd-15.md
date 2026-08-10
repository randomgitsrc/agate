# BDD-15: gate_commands 保持正文读取，四个工具无回归

## P5 测试证据
- `ok 453 TDD.G1: BDD-15 回归：gate_commands.P3 保持正文（不迁移 frontmatter）→ auto-read, red-light exit 0`
- `check-tdd-red.bats` 全部 PYX.* 用例（`ok 472-477`：agate-read-gate-commands.py 6 个用例）全绿

## 本次验收独立复现（对本任务自身 P2-design.md 实测四个工具，非引用旧结果）
本任务自身的 P2-design.md §5 把 `gate_commands` 声明在正文（未迁移 frontmatter，属流 A 明确不迁移
范围）。直接对这份真实文件跑四个读取工具：

```
$ GATE_FILE=docs/tasks/T001-v2.0-structured/P2-design.md python3 agate/scripts/agate-read-gate-commands.py
{"commands": [{"cmd": "bats agate/tests/unit/ agate/tests/regression/", "formatter": "generic-tap.sh", "suffix": ""}], "project_module": ""}

$ GATE_FILE=docs/tasks/T001-v2.0-structured/P2-design.md python3 agate/scripts/agate-gate-missing-cmds.py
P3:bats
P5:bats
P5_consistency:python3
P5_shellcheck:shellcheck
P5_count:bash

$ GATE_FILE=docs/tasks/T001-v2.0-structured/P2-design.md python3 agate/scripts/agate-gate-p5-count.py
4

$ P2_DESIGN=docs/tasks/T001-v2.0-structured/P2-design.md python3 agate/scripts/agate-read-p5-commands.py
{"commands": [{"cmd": "bats agate/tests/sanity.bats ... 2>&1 | tail -40", ...}, {"cmd": "python3 agate/scripts/check-protocol-consistency.py ...", "suffix": "_consistency"}, {"cmd": "shellcheck -S warning agate/scripts/*.sh ...", "suffix": "_shellcheck"}, {"cmd": "bash agate/tests/scripts/count-tests.sh ...", "suffix": "_count"}]}
```
四个工具（agate-read-gate-commands.py / agate-gate-missing-cmds.py / agate-gate-p5-count.py /
agate-read-p5-commands.py）均按旧正则正确读取 gate_commands，输出与 P2-design.md §5 正文声明的
P3/P5/P5_consistency/P5_shellcheck/P5_count 五个命令键一一对应，无回归。

## 判定
PASS
