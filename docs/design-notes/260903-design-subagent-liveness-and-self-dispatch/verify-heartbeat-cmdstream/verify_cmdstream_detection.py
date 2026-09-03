#!/usr/bin/env python3
"""命令流日志机制验证试验：能否机械检测"调用阻塞冻结"与"逻辑空转"，
且不误报合法的"测试-修复-迭代"、"合法长命令"、"长时间思考"。

试验原理（与模型行为无关的纯机械层）：
- 心跳 mtime 只回答"进程是否活着"——各场景下心跳都新鲜（进程都活着），
  仅凭心跳无法区分卡死与正常，这是 §3.4.1 表格第二、三行的盲区。
- 命令流日志提供"活动信号"，可机械检测两类卡死模式：
    1. 调用冻结：存在未结束的 tool/call（call 无配对 result）且开始距今超阈值
    2. 活动冻结：无未结束调用时，任何活动事件（思考/输出/工具）距今超阈值
    3. 无效重复：同命令 + 同 (exit, 输出哈希) 组合重复超过阈值 → 空转

三类活动事件（2026-09-03 实测：subagent 运行 = 思考/输出/执行 三类活动）：
    think=<ts>            model 思考活动（reasoning-chunks，实测内部间隔 p95=3.8s）
    output=<ts>           model 输出活动（assistant/text-chunks）
    call id=<id> cmd=<hash> [expected=<s>]    执行 tool 开始（可能未结束）
    result id=<id> cmd=<hash> exit=<code> out=<hash> [truncated]   执行 tool 结束

关键推论（实测驱动）："最后一条命令开始距今"不能作冻结判据——
subagent 合法"只思考不调工具"最长 20 分钟（思考间隙 max≈1239s）、
"长命令执行中"最长 15 分钟（执行阶段 max≈925s），旧判据都会误杀。

阈值模型（§3.4.3）：
- 调用冻结：有未结束 call 时，若命令声明 expected → 阈值 = max(expected×2, 30)；
  未声明 → alert 300s / suspect 900s 兜底
- 活动冻结：无未结束 call 时，任何活动事件距今 > alert 60s / suspect 300s
- 无效重复：窗口内同 (命令, exit, 输出哈希) 重复 >= 5 次 → 空转
- 截断排除：truncated 输出不参与无效重复哈希比对
now 表示"主 Agent 观察时刻"的虚拟当前时间。
"""
import sys

# ---- 调用冻结（有未结束 call）----
CALL_EXPECT_MULT = 2      # expected × 2
CALL_FLOOR = 30           # 兜底下限（expected 很小时也至少给 30s）
CALL_ALERT_FALLBACK = 300  # 无 expected 声明：>300s 提示核查
CALL_SUSPECT_FALLBACK = 900  # 无 expected 声明：>900s 考虑中止
# ---- 活动冻结（无未结束 call）----
ACTIVITY_ALERT = 60       # 无任何活动 >60s 提示核查
ACTIVITY_SUSPECT = 300    # 无任何活动 >300s 考虑中止
# ---- 无效重复 ----
SPIN_THRESHOLD = 5        # 同一 (命令, exit, 输出哈希) 组合重复 >= 5 次 → 空转
REPEAT_WINDOW = 10        # 重复检测窗口
REPEAT_UNIQUE_MIN = 3     # 窗口内唯一命令数 < 3 → 重复可疑（信息级）


class Event:
    __slots__ = ("ts", "kind", "id", "cmd", "exit", "out", "expected", "truncated")

    def __init__(self, ts, kind, **kw):
        self.ts = ts
        self.kind = kind  # think / out / call / result
        self.id = kw.get("id")
        self.cmd = kw.get("cmd")
        self.exit = kw.get("exit")
        self.out = kw.get("out")
        self.expected = kw.get("expected")
        self.truncated = kw.get("truncated", False)


def parse(log_lines):
    events = []
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
                parts[kv] = "1"
        ts = int(parts["t"])
        if "think" in parts:
            events.append(Event(ts, "think"))
        elif "output" in parts:
            events.append(Event(ts, "out"))
        elif "call" in parts:
            events.append(Event(ts, "call", id=parts.get("id"),
                                cmd=parts.get("cmd"),
                                expected=int(parts["expected"]) if "expected" in parts else None))
        elif "result" in parts:
            events.append(Event(ts, "result", id=parts.get("id"),
                                cmd=parts.get("cmd"), exit=int(parts.get("exit", 0)),
                                out=parts.get("out"),
                                truncated="truncated" in parts))
    return events


def detect(events, now):
    """返回 (verdict, reasons)。verdict ∈ {FROZEN, SPIN, NORMAL}"""
    if not events:
        return "NORMAL", ["无活动记录（进程未启动？）"]
    reasons = []

    # 未结束调用：有 call 无配对 result
    call_ids = set(e.id for e in events if e.kind == "call" and e.id)
    result_ids = set(e.id for e in events if e.kind == "result" and e.id)
    unresolved = [e for e in events if e.kind == "call" and e.id in (call_ids - result_ids)]
    completed = [e for e in events if e.kind == "result"]

    if unresolved:
        # ---- 1. 调用冻结检测（系统调用阻塞）----
        for c in unresolved:
            age = now - c.ts
            if c.expected is not None:
                thr = max(c.expected * CALL_EXPECT_MULT, CALL_FLOOR)
                src = f"expected={c.expected}s ×{CALL_EXPECT_MULT}"
            else:
                thr = CALL_ALERT_FALLBACK
                src = f"未声明 expected，兜底 {CALL_ALERT_FALLBACK}s"
            if age > thr:
                reasons.append(f"调用冻结：未结束调用 {c.id}（{c.cmd}）t={c.ts}，"
                               f"距今 {age}s > {thr}s（{src}）→ 疑似卡在单次调用")
                return "FROZEN", reasons
            reasons.append(f"提示：存在未结束调用 {c.id}（{c.cmd}）距今 {age}s，"
                           f"未超阈值 {thr}s（{src}）——长命令执行中，正常")
    else:
        # ---- 2. 活动冻结检测（进程级卡死，无未结束调用时）----
        last_activity = max(e.ts for e in events if e.kind in ("think", "out", "call", "result"))
        age = now - last_activity
        if age > ACTIVITY_SUSPECT:
            reasons.append(f"活动冻结：最后活动事件 t={last_activity}，距今 {age}s "
                           f"> suspect {ACTIVITY_SUSPECT}s → 疑似进程卡死（无任何思考/输出/工具）")
            return "FROZEN", reasons
        if age > ACTIVITY_ALERT:
            reasons.append(f"活动冻结（alert）：最后活动事件 t={last_activity}，距今 {age}s "
                           f"> alert {ACTIVITY_ALERT}s → 提示核查")
            return "FROZEN", reasons

    # ---- 3. 无效重复检测（逻辑空转）----
    window = completed[-REPEAT_WINDOW:]
    combo_counts = {}
    for r in window:
        if r.truncated:
            continue  # 截断输出不参与哈希比对
        key = (r.cmd, r.exit, r.out)
        combo_counts[key] = combo_counts.get(key, 0) + 1
    if combo_counts:
        worst = max(combo_counts.values())
        if worst >= SPIN_THRESHOLD:
            worst_key = max(combo_counts, key=combo_counts.get)
            reasons.append(f"空转：同 (命令, exit, 输出哈希) 组合 {worst_key} "
                           f"在窗口 {REPEAT_WINDOW} 内重复 {worst} 次 >= {SPIN_THRESHOLD} → 疑似逻辑空转")
            return "SPIN", reasons
    # 重复可疑（信息级）：命令名重复但结果在变 → 合法迭代，不判空转
    unique_cmds = {r.cmd for r in window}
    if len(unique_cmds) < REPEAT_UNIQUE_MIN:
        reasons.append(f"提示：窗口 {REPEAT_WINDOW} 内唯一命令数 {len(unique_cmds)} < "
                       f"{REPEAT_UNIQUE_MIN}，但结果签名在变化（合法迭代特征），不判空转")
    reasons.append("正常：活动持续推进，无冻结/空转信号")
    return "NORMAL", reasons


# ---- 场景模拟（虚拟时钟，秒）----

SCENARIOS = {
    # 场景 2：系统调用层无限阻塞——call 发出后永不返回（无 result），无 expected 声明
    "A_调用冻结_系统调用阻塞": {
        "now": 1004,
        "lines": [
            "t=0 call id=c1 cmd=models_migrate",
            "t=1 result id=c1 cmd=models_migrate exit=0 out=h_ok1",
            "t=2 call id=c2 cmd=network_call_no_timeout",
            "# ↑ c2 发出后 subagent 阻塞（模拟无超时网络请求），心跳进程独立继续 touch",
            "#   c2 无 expected 声明 → 兜底 300s，now-2=1002s > 300s → 调用冻结",
        ],
    },
    # 场景 3：逻辑空转——反复执行同一条失败命令 ×10，exit 与输出哈希均不变
    "B_空转_逻辑打转": {
        "now": 20,
        "lines": [
            "t=0 call id=r1 cmd=retry_convert",
            "t=1 result id=r1 cmd=retry_convert exit=1 out=h_fail",
            "t=2 call id=r2 cmd=retry_convert",
            "t=3 result id=r2 cmd=retry_convert exit=1 out=h_fail",
            "t=4 call id=r3 cmd=retry_convert",
            "t=5 result id=r3 cmd=retry_convert exit=1 out=h_fail",
            "t=6 call id=r4 cmd=retry_convert",
            "t=7 result id=r4 cmd=retry_convert exit=1 out=h_fail",
            "t=8 call id=r5 cmd=retry_convert",
            "t=9 result id=r5 cmd=retry_convert exit=1 out=h_fail",
            "t=10 call id=r6 cmd=retry_convert",
            "t=11 result id=r6 cmd=retry_convert exit=1 out=h_fail",
"t=7 call id=r7 cmd=retry_convert",
"t=8 result id=r7 cmd=retry_convert exit=1 out=h_fail",
"t=8 call id=r8 cmd=retry_convert",
"t=9 result id=r8 cmd=retry_convert exit=1 out=h_fail",
"t=9 call id=r9 cmd=retry_convert",
"t=10 result id=r9 cmd=retry_convert exit=1 out=h_fail",
"t=10 call id=r10 cmd=retry_convert",
"t=11 result id=r10 cmd=retry_convert exit=1 out=h_fail",
        ],
    },
    # 对照：合法的"测试-修复-迭代"——命令名重复但结果签名每次变化
    "C_正常_合法迭代": {
        "now": 10,
        "lines": [
            "t=0 call id=1 cmd=run_test",
            "t=1 result id=1 cmd=run_test exit=1 out=h_fail1",
            "t=2 call id=2 cmd=apply_fix",
            "t=3 result id=2 cmd=apply_fix exit=0 out=h_fix1",
            "t=4 call id=3 cmd=run_test",
            "t=5 result id=3 cmd=run_test exit=1 out=h_fail2",
            "t=6 call id=4 cmd=apply_fix",
            "t=7 result id=4 cmd=apply_fix exit=0 out=h_fix2",
            "t=8 call id=5 cmd=run_test",
            "t=9 result id=5 cmd=run_test exit=0 out=h_pass",
        ],
    },
    # 对照：健康长尾 subagent——命令持续推进且各不相同
    "D_正常_健康长尾": {
        "now": 20,
        "lines": [
            "t=0 call id=1 cmd=a",
            "t=1 result id=1 cmd=a exit=0 out=h1",
            "t=2 call id=2 cmd=b",
            "t=3 result id=2 cmd=b exit=0 out=h2",
            "t=4 call id=3 cmd=c",
            "t=5 result id=3 cmd=c exit=0 out=h3",
            "t=6 call id=4 cmd=d",
            "t=7 result id=4 cmd=d exit=0 out=h4",
            "t=8 call id=5 cmd=e",
            "t=9 result id=5 cmd=e exit=0 out=h5",
            "t=10 call id=6 cmd=f",
            "t=11 result id=6 cmd=f exit=0 out=h6",
            "t=12 call id=7 cmd=g",
            "t=13 result id=7 cmd=g exit=0 out=h7",
            "t=14 call id=8 cmd=h",
            "t=15 result id=8 cmd=h exit=0 out=h8",
            "t=16 call id=9 cmd=i",
            "t=17 result id=9 cmd=i exit=0 out=h9",
            "t=18 call id=10 cmd=j",
            "t=19 result id=10 cmd=j exit=0 out=h10",
        ],
    },
    # 新增（2026-09-03 实测驱动）：合法长命令不误报——声明 expected=200s
    # 的长命令（全量测试/CI 等待，对应实测 max≈925s 级）执行到 100s，未结束 call 仍在跑。
    "E_正常_合法长命令_expected声明": {
        "now": 100,
        "lines": [
            "t=0 call id=0 cmd=setup",
            "t=1 result id=0 cmd=setup exit=0 out=h_setup",
            "t=2 call id=long cmd=full_pytest_xdist expected=200",
            "# ↑ 未结束 call 距今 98s < max(200×2,30)=400s → 不冻结（长命令执行中）",
        ],
    },
    # 新增（2026-09-03 实测驱动）：长命令超期仍无 result → 调用冻结（expected×2 触发）
    "F_调用冻结_expected超期": {
        "now": 500,
        "lines": [
            "t=0 call id=0 cmd=setup",
            "t=1 result id=0 cmd=setup exit=0 out=h_setup",
            "t=2 call id=long cmd=full_pytest_xdist expected=200",
            "# ↑ 未结束 call 距今 498s > max(200×2,30)=400s → 调用冻结",
        ],
    },
    # 新增（2026-09-03，§3.4.2 差异点 4）：截断排除——不同失败命令输出被截断成
    # 同前缀（h_trunc），参与哈希比对会误判空转；截断不参与比对 → 不判空转。
    "G_正常_截断输出不误判": {
        "now": 12,
        "lines": [
            "t=0 call id=1 cmd=fail_task",
            "t=1 result id=1 cmd=fail_task exit=1 out=h_trunc truncated",
            "t=2 call id=2 cmd=fail_task",
            "t=3 result id=2 cmd=fail_task exit=1 out=h_trunc truncated",
            "t=4 call id=3 cmd=fail_task",
            "t=5 result id=3 cmd=fail_task exit=1 out=h_trunc truncated",
            "t=6 call id=4 cmd=fail_task",
            "t=7 result id=4 cmd=fail_task exit=1 out=h_trunc truncated",
            "t=8 call id=5 cmd=fail_task",
            "t=9 result id=5 cmd=fail_task exit=1 out=h_trunc truncated",
            "t=10 call id=6 cmd=fail_task",
            "t=11 result id=6 cmd=fail_task exit=1 out=h_trunc truncated",
            "# ↑ 同命令同 exit 同截断前缀 ×6，但 truncated 不参与哈希比对 → 不算无效重复",
        ],
    },
    # 新增（2026-09-03，用户指出 + 实测驱动）：长时间思考不误杀——subagent 思考
    # 20 分钟不调工具（思考间隙实测 max≈1239s），但 think 事件持续流动。
    # 旧判据"最后命令开始距今"（t=3 起 1197s）会误判 FROZEN；活动冻结判据
    # 看任何活动（think 流持续）→ NORMAL。
    "H_正常_长时间思考不误杀": {
        "now": 1200,
        "lines": [
            "t=0 call id=1 cmd=setup",
            "t=1 result id=1 cmd=setup exit=0 out=h_setup",
            "t=3 call id=2 cmd=analyze",
            "t=4 result id=2 cmd=analyze exit=0 out=h_analyzed",
            "# ↑ 之后不再调工具，但 model 持续思考（reasoning-chunks 事件流）",
            "t=10 think",
            "t=300 think",
            "t=600 think",
            "t=900 think",
            "t=1190 think",
            "# 最后活动 t=1190，距今 10s < 60s → 活动冻结不触发；无未结束调用 → 正常",
        ],
    },
    # 新增（2026-09-03）：进程级卡死——无未结束调用 + 无任何活动事件（连思考都没有）
    "I_活动冻结_进程级卡死": {
        "now": 100,
        "lines": [
            "t=0 call id=1 cmd=setup",
            "t=1 result id=1 cmd=setup exit=0 out=h_setup",
            "t=2 call id=2 cmd=analyze",
            "t=3 result id=2 cmd=analyze exit=0 out=h_analyzed",
            "# ↑ 之后无任何活动（无思考/输出/工具），距今 97s > 60s → 活动冻结",
        ],
    },
}

# ---- 期望判定（验证断言） ----
EXPECTED = {
    "A_调用冻结_系统调用阻塞": "FROZEN",
    "B_空转_逻辑打转": "SPIN",
    "C_正常_合法迭代": "NORMAL",
    "D_正常_健康长尾": "NORMAL",
    "E_正常_合法长命令_expected声明": "NORMAL",
    "F_调用冻结_expected超期": "FROZEN",
    "G_正常_截断输出不误判": "NORMAL",
    "H_正常_长时间思考不误杀": "NORMAL",
    "I_活动冻结_进程级卡死": "FROZEN",
}


def main():
    print("=" * 72)
    print("命令流日志机制验证：调用冻结 / 活动冻结 / 空转 / 合法场景 区分能力")
    print("=" * 72)
    print("三类活动信号：think(model思考) / out(model输出) / call+result(执行tool)")
    print(f"判据：调用冻结 = 未结束call距今超阈值（expected×{CALL_EXPECT_MULT} 或 {CALL_ALERT_FALLBACK}s兜底）；"
          f"活动冻结 = 无未结束call且无任何活动 >{ACTIVITY_ALERT}s")
    print(f"      空转 = 同(命令,exit,输出哈希) 重复 >= {SPIN_THRESHOLD} 次（窗口 {REPEAT_WINDOW}）；截断输出不参与比对")
    print("-" * 72)
    ok = True
    for name, sc in SCENARIOS.items():
        events = parse(sc["lines"])
        verdict, reasons = detect(events, sc["now"])
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
    print(f"结论：{'全部断言通过——命令流日志可机械区分九种状态' if ok else '存在断言失败，需检查判据'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
