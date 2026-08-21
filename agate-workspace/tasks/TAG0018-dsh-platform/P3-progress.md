# TAG0018 P3 进度（test-designer）

## 步骤记录

1. **角色定义**（`agate/assets/execution-roles/test-designer.md`）：TDD 测试先行，BDD→测试 1:1 映射；分阶段落盘默认启用。
2. **派发上下文**（P3-dispatch-context-test-designer.md）：强制指令 = 产出 `P3-test-design.md` + 扩展版 `agate/tests/unit/test_dsh_preset.py`；测试当前必须红且失败原因为"实现缺失"；吸收 P2-review 建议 1/2（必做）；覆盖 BDD-15/16/17 在位互链；用例数只增不减（基线 1030）。
3. **P1-requirements.md**：19 条 BDD 通读；锚定 BDD-3 persona 两判据、BDD-7 位置判据、BDD-8 命令串、BDD-9 install-hook 调用、BDD-15/16/17 互链。
4. **P2-design.md**：设计 §3 交付物 6（5 用例基线）、§4 BDD 对照表、§5 gate_commands（P3 单文件 / P5 / P5_count ≥1030）、决策 D-1（h3 置于步骤 2 区内）。
5. **P2-review.md**：approved；测试缺口 = BDD-3 无自动化用例（建议 1）、BDD-7 位置 + BDD-9 install-hook 无自动化用例（建议 2）——本 P3 均补齐。
6. **测试约定**（tests/README.md + conftest.py）：平台无关核心约束（不写 /tmp、不假设符号链接、不裸 python3）；`agate_root` fixture（conftest L306）；count-tests.sh 计数口径。
7. **参考实现**（agate-copy 5 用例草稿）：结构与 helper（_js_loader/_read/_load_rows/_frontmatter）沿用；扩展点确认。
8. **worktree 现状核验**：`assets/templates/dsh/` 不存在（glob 0 命中）；SETUP.md 无 DSH 引用（grep 0 命中）；步骤 2 标题 L72「## 步骤 2：把 orchestrator 注册到你的平台」、步骤 3 L144「## 步骤 3（可选）：设成默认 agent」。
9. **锚点核验**：orchestrator-template.md L12 =「# Orchestrator（agate 编排 Agent）」（BDD-3 负判据精确串）；参考 SKILL.md frontmatter（name: agate-protocol + description）、preset.yml（name/description/order）、agent.cordis.yml persona 行（id: persona → config.text）；参考 SETUP.md DSH 命令块（mkdir -p + 三条独立 ln -sf + install-hook.py）。

## 产出

- `P3-test-design.md`：8 用例清单 × BDD 映射 × 红灯预期；BDD-15/16/17 在位互链表；平台无关落实表；与参考草稿差异表。
- `agate/tests/unit/test_dsh_preset.py`：8 用例（5 基线 + 3 新增：persona 薄身份 / 位置判据 / install-hook 调用），并强化用例 6 为 BDD-8 精确命令串断言。

## 红灯验证（worktree 实测）

`python3 -m pytest agate/tests/unit/test_dsh_preset.py -q --tb=line` → **8 failed in 0.04s**（exit 1）：
- 5 例 FileNotFoundError（assets/templates/dsh/ 三模板文件缺失）
- 3 例 AssertionError / pytest.fail（SETUP.md DSH 章节缺失）
- 无收集错误、无语法错误 → 全部 B 类红灯（实现缺失），check-tdd-red.py 预期 exit 0。

## 用例数影响

1030 → **1038**（只增不减，满足 P5_count ≥1030；派发指引「~1035」为估算值）。
