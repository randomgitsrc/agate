#!/usr/bin/env python3
"""命令流日志机制验证试验：能否机械检测"系统调用阻塞冻结"与"逻辑空转"，
且不误报合法的"测试-修复-迭代"与"合法长命令"。

试验原理（与模型行为无关的纯机械层）：
- 心跳 mtime 只回答"进程是否活着"——三种场景下心跳都新鲜（进程都活着），
  仅凭心跳无法区分卡死与正常，这是 §3.4.1 表格第二、三行的盲区。
- 命令流日志（每条命令：开始时间戳 + 命令哈希 + exit code + 输出哈希）提供
  "活动信号"，可机械检测两类模式：
    1. 冻结：最后一条命令开始时间距今超过阈值 → 疑似卡在单次调用（场景 2）
    2. 无效重复：同命令 + 同 (exit, 输出哈希) 组合重复超过阈值 → 疑似空转（场景 3）
  合法的"测试-修复"迭代虽然命令名重复，但结果签名每次变化，不应触发空转判定。

阈值模型（§3.4.3，实测数据驱动——DSH 实测 bash 命令耗时 p50=57ms/p95≈7s/max≈196s）：
- 冻结检测**两级**：命令声明了预期耗时（expected 字段，对应 RM-AG0023 timeout_seconds
  机制）→ 冻结阈值 = max(期望×2, 兜底下限)；未声明 → 兜底阈值。
  固定 30s 会误杀 9 条 >10s 的合法长命令（实测数据），因此不能设全局固定值。
- 无效重复：窗口内同 (命令, exit, 输出哈希) 重复 >= 5 次 → 空转。
- 截断排除：输出被截断（truncated 标记）→ 不参与无效重复的哈希比对
  （两个不同失败截断成同前缀会误判为空转，§3.4.2 差异点 4）。

日志格式（虚拟时钟，秒）：t=<ts> cmd=<hash> exit=<code> out=<hash> [expected=<s>] [truncated]
now 表示"主 Agent 观察时刻"的虚拟当前时间。
"""
import sys

FREEZE_FALLBACK = 60      # 冻结兜底阈值：未声明预期耗时，最后命令开始后 >60s 无新命令 → 冻结
FREEZE_FLOOR = 30         # 冻结兜底下限：即便 expected 很小，也至少给 30s（防抖动）
FREEZE_EXPECT_MULT = 2    # 冻结主信号：有 expected 时阈值 = expected × 2
SPIN_THRESHOLD = 5        # 同一 (命令, exit, 输出哈希) 组合重复 >= 5 次 → 空转
REPEAT_WINDOW = 10        # 重复检测窗口
REPEAT_UNIQUE_MIN = 3     # 窗口内唯一命令数 < 3 → 重复可疑（信息级）


def parse(log_lines):
    cmds = []
    for line in log_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = {}
        for kv in line.split():
            if "=" in kv:
                k, v = kv.split("=", 1)
                parts[k] = v
            else:
                parts[kv] = "1"  # 裸标记（如 truncated）视为布尔标志
        rec = {
            "t": int(parts["t"]),
            "cmd": parts["cmd"],
            "exit": int(parts["exit"]),
            "out": parts["out"],
            "expected": int(parts["expected"]) if "expected" in parts else None,
            "truncated": "truncated" in parts,
        }
        cmds.append(rec)
    return cmds


def freeze_threshold(rec):
    """两级冻结阈值：有 expected 用 max(expected×2, 下限)，无则兜底。"""
    if rec["expected"] is not None:
        return max(rec["expected"] * FREEZE_EXPECT_MULT, FREEZE_FLOOR)
    return FREEZE_FALLBACK


def detect(cmds, now):
    """返回 (verdict, reasons)。verdict ∈ {FROZEN, SPIN, NORMAL}"""
    if not cmds:
        return "NORMAL", ["无命令记录（心跳不存在？）"]
    reasons = []
    last = cmds[-1]
    # 1. 冻结检测（场景 2：单次调用阻塞）——两级阈值
    thr = freeze_threshold(last)
    if now - last["t"] > thr:
        src = (f"expected={last['expected']}s ×{FREEZE_EXPECT_MULT}" if last["expected"] is not None
               else f"未声明预期耗时，兜底 {FREEZE_FALLBACK}s")
        reasons.append(f"冻结：最后命令 t={last['t']}（{last['cmd']}），观察时刻 now={now}，"
                       f"间隔 {now - last['t']}s > 阈值 {thr}s（{src}）→ 疑似卡在单次调用")
        return "FROZEN", reasons
    # 2. 无效重复检测（场景 3：逻辑空转）——同命令+同结果签名；截断排除
    window = cmds[-REPEAT_WINDOW:]
    combo_counts = {}
    for rec in window:
        if rec["truncated"]:
            continue  # 截断输出不参与哈希比对（两个不同失败截断成同前缀会误判）
        key = (rec["cmd"], rec["exit"], rec["out"])
        combo_counts[key] = combo_counts.get(key, 0) + 1
    if combo_counts:
        worst = max(combo_counts.values())
        if worst >= SPIN_THRESHOLD:
            worst_key = max(combo_counts, key=combo_counts.get)
            reasons.append(f"空转：同 (命令, exit, 输出哈希) 组合 {worst_key} "
                           f"在窗口 {REPEAT_WINDOW} 内重复 {worst} 次 >= {SPIN_THRESHOLD} → 疑似逻辑空转")
            return "SPIN", reasons
    # 3. 重复可疑（信息级）：命令名重复但结果在变 → 合法迭代，不判空转
    unique_cmds = {rec["cmd"] for rec in window}
    if len(unique_cmds) < REPEAT_UNIQUE_MIN:
        reasons.append(f"提示：窗口 {REPEAT_WINDOW} 内唯一命令数 {len(unique_cmds)} < "
                       f"{REPEAT_UNIQUE_MIN}，但结果签名在变化（合法迭代特征），不判空转")
    reasons.append("正常：心跳新鲜 + 命令流持续推进，无冻结/空转信号")
    return "NORMAL", reasons


# ---- 场景模拟命令流（虚拟时钟） ----
# expected= 字段模拟"派发时声明了预期耗时"（RM-AG0023 timeout_seconds 机制）

SCENARIOS = {
    # 场景 2：系统调用层无限阻塞——最后一条命令之后不再有任何命令（sleep 1000 模拟）
    "A_冻结_系统调用阻塞": {
        "now": 1004,
        "lines": [
            "t=0 cmd=models_migrate exit=0 out=h_ok1",
            "t=1 cmd=entry_service exit=0 out=h_ok2",
            "t=2 cmd=star_service exit=0 out=h_ok3",
            "t=3 cmd=share_service exit=0 out=h_ok4",
            "t=4 cmd=network_call_no_timeout exit=0 out=h_ok5",
            "# ↑ t=4 之后 subagent 阻塞在该调用（模拟无超时网络请求），心跳进程独立继续 touch",
        ],
    },
    # 场景 3：逻辑空转——反复执行同一条失败命令，exit 与输出哈希均不变
    "B_空转_逻辑打转": {
        "now": 12,
        "lines": [
            "t=0 cmd=retry_convert exit=1 out=h_fail",
            "t=1 cmd=retry_convert exit=1 out=h_fail",
            "t=2 cmd=retry_convert exit=1 out=h_fail",
            "t=3 cmd=retry_convert exit=1 out=h_fail",
            "t=4 cmd=retry_convert exit=1 out=h_fail",
            "t=5 cmd=retry_convert exit=1 out=h_fail",
            "t=6 cmd=retry_convert exit=1 out=h_fail",
            "t=7 cmd=retry_convert exit=1 out=h_fail",
            "t=8 cmd=retry_convert exit=1 out=h_fail",
            "t=9 cmd=retry_convert exit=1 out=h_fail",
            "t=10 cmd=retry_convert exit=1 out=h_fail",
        ],
    },
    # 对照：合法的"测试-修复-迭代"——命令名重复但结果签名每次变化
    "C_正常_合法迭代": {
        "now": 7,
        "lines": [
            "t=0 cmd=run_test exit=1 out=h_fail1",
            "t=1 cmd=apply_fix exit=0 out=h_fix1",
            "t=2 cmd=run_test exit=1 out=h_fail2",
            "t=3 cmd=apply_fix exit=0 out=h_fix2",
            "t=4 cmd=run_test exit=0 out=h_pass",
        ],
    },
    # 对照：健康长尾 subagent——命令持续推进且各不相同
    "D_正常_健康长尾": {
        "now": 20,
        "lines": [
            "t=0 cmd=a exit=0 out=h1",
            "t=2 cmd=b exit=0 out=h2",
            "t=4 cmd=c exit=0 out=h3",
            "t=6 cmd=d exit=0 out=h4",
            "t=8 cmd=e exit=0 out=h5",
            "t=10 cmd=f exit=0 out=h6",
            "t=12 cmd=g exit=0 out=h7",
            "t=14 cmd=h exit=0 out=h8",
            "t=16 cmd=i exit=0 out=h9",
            "t=18 cmd=j exit=0 out=h10",
        ],
    },
    # 新增（2026-09-03 实测驱动）：合法长命令不误报——声明 expected=200s
    # 的合法长命令（全量测试/CI 等待，对应实测 max≈196s）在 100s 时仍在正常执行，
    # 固定 30s 阈值会误杀，两级阈值（expected×2=400s）不触发冻结。
    "E_正常_合法长命令_expected声明": {
        "now": 100,
        "lines": [
            "t=0 cmd=setup exit=0 out=h_setup",
            "t=1 cmd=full_pytest_xdist exit=0 out=h_run expected=200",
            "# ↑ 距 last 99s，expected=200s → 阈值 max(200×2, 30)=400s，99s < 400s → 不冻结",
        ],
    },
    # 新增（2026-09-03 实测驱动）：长命令超期仍无新命令 → 冻结（expected×2 触发）
    "F_冻结_expected超期": {
        "now": 500,
        "lines": [
            "t=0 cmd=setup exit=0 out=h_setup",
            "t=1 cmd=full_pytest_xdist exit=0 out=h_run expected=200",
            "# ↑ 距 last 499s > 阈值 max(200×2, 30)=400s → 冻结（即便声明过预期耗时）",
        ],
    },
    # 新增（2026-09-03，§3.4.2 差异点 4）：截断排除——两条不同失败命令的输出
    # 都被截断成同前缀（h_trunc），若参与哈希比对会误判空转；截断不参与比对 → 不判空转。
    "G_正常_截断输出不误判": {
        "now": 12,
        "lines": [
            "t=0 cmd=fail_task exit=1 out=h_trunc truncated",
            "t=1 cmd=fail_task exit=1 out=h_trunc truncated",
            "t=2 cmd=fail_task exit=1 out=h_trunc truncated",
            "t=3 cmd=fail_task exit=1 out=h_trunc truncated",
            "t=4 cmd=fail_task exit=1 out=h_trunc truncated",
            "t=5 cmd=fail_task exit=1 out=h_trunc truncated",
            "# ↑ 同命令同 exit 同被截断前缀 ×6，但 truncated 不参与哈希比对 → 不算无效重复",
        ],
    },
}

# ---- 期望判定（验证断言） ----
EXPECTED = {
    "A_冻结_系统调用阻塞": "FROZEN",
    "B_空转_逻辑打转": "SPIN",
    "C_正常_合法迭代": "NORMAL",
    "D_正常_健康长尾": "NORMAL",
    "E_正常_合法长命令_expected声明": "NORMAL",
    "F_冻结_expected超期": "FROZEN",
    "G_正常_截断输出不误判": "NORMAL",
}


def main():
    print("=" * 72)
    print("命令流日志机制验证：冻结 / 空转 / 合法迭代 / 长命令 / 截断 区分能力")
    print("=" * 72)
    print(f"判据：冻结 = 最后命令开始距今 > 阈值（有 expected: max(expected×2, {FREEZE_FLOOR}s)；"
          f"无: {FREEZE_FALLBACK}s 兜底）")
    print(f"      空转 = 同(命令,exit,输出哈希) 重复 >= {SPIN_THRESHOLD} 次（窗口 {REPEAT_WINDOW}）；"
          f"截断输出不参与比对")
    print("-" * 72)
    ok = True
    for name, sc in SCENARIOS.items():
        cmds = parse(sc["lines"])
        verdict, reasons = detect(cmds, sc["now"])
        expected = EXPECTED[name]
        mark = "PASS" if verdict == expected else "FAIL"
        if verdict != expected:
            ok = False
        print(f"[{mark}] {name}")
        print(f"      期望={expected:7s} 实际={verdict:7s} "
              f"心跳=新鲜(进程存活,无法区分) 命令流判定={verdict}")
        for r in reasons:
            print(f"      · {r}")
        print()
    print("-" * 72)
    print(f"结论：{'全部断言通过——命令流日志可机械区分七种状态' if ok else '存在断言失败，需检查判据'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
