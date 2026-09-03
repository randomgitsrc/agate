# 复审留痕 2026-09-04 TAG0029-02（只复核 A2/A3/A5）

- 读 check-tdd-red.py L32：`测试运行器探测链：$TEST_RUNNER → gate_commands.P3（P2-design.md）→ which pytest → exit 3` → 精确 P3
- grep `P3\*|gate_commands\.P3` 全文件：4 命中（L19/L32/L197/L198），均为精确 P3，无 P3* → A2 ALIGNED
- 读 formatters README L89-100：单栈精确 P3 示例 + L91 退役说明 + L100 登记注记，无 P3_js 推荐示例 → A3 ALIGNED
- 读 CHANGELOG L11-18：[Unreleased] 含 TAG0029 条目（退役 + fail-closed + exit2 分支 + R2 豁免 + 无存量注记）→ A5 ALIGNED
- 成果文件原位更新：汇总表 A2/A3/A5 → ALIGNED（复审注记）+ 逐项结论 + 复审节；A1/A4/A6/A7 沿用上轮
