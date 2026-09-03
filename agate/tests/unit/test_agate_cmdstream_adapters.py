# tests/unit/test_agate_cmdstream_adapters.py — 三平台命令流适配器（TAG0028 P3，RM-AG0055）
# 被测（P4 才新建，本文件当前必须全红）：
#   - agate/scripts/agate-cmdstream-adapters.py（CommandStreamAdapter 基类 + 三平台适配器 +
#     显式注册表 ADAPTERS，P2-design.md §3.1 M2）
#   - agate/scripts/agate-cmdstream-detect.py（检测引擎 import ADAPTERS，BDD-6 零改动锚）
#
# 覆盖 P1-requirements.md BDD-2/3/4/5/6/7（claude-code JSONL / opencode SQLite / dsh zstd /
# 子 agent 会话定位 / 注册表新增平台 / fixture 脱敏）。
#
# 接口假设（P4 实现须提供，均有 P2-design.md §3.1 明文依据，非杜撰）：
#   - 基类 CommandStreamAdapter：probe(path)->bool / list_sessions(cwd)->list[str] /
#     read_commands(session_path)->list[CommandRecord]
#   - ClaudeCodeAdapter：解析 JSONL，tool_use/tool_result 按 sourceToolAssistantUUID↔uuid 配对，
#     command=input.command、ts 来自 timestamp、exit 从 is_error + "Exit code N" 文本前缀解析并写
#     exit_signal 留档（验证记录差异点 2 / BDD-2）
#   - OpenCodeAdapter：解析 SQLite（part.data.state），exit 取 state.metadata.exit 整数、
#     truncated 取 state.metadata.truncated 显式标记（BDD-3）
#   - DSHAdapter：解析 JSONL.zstd，解压隔离在适配器内部（spawn node 单行脚本 zlib.zstdDecompressSync，
#     不依赖 python zstandard）、tool/call + tool/result 按 callId 配对、exit 从 isError + "Error:"
#     前缀解析并写 exit_signal、子 agent = delegationDepth>0 独立 session 文件（BDD-4/5）
#   - 显式注册表：ADAPTERS = {"claude-code": ..., "opencode": ..., "dsh": ...}（P2 §2.1 候选 A，BDD-6）
#
# 红灯性质：被测脚本当前不存在——_load_script 检查文件存在性后 pytest.fail（B 类红灯）。
# node 探测（DSH zstd 用例）：node 可用才跑真实解压路径，不可用 pytest.skip 并标注原因（P2-review
# 非阻塞建议 2 / dispatch-context 约束 5）；不得硬依赖 python zstandard。

import importlib.util
import json
import shutil
import sqlite3
import subprocess

import pytest


def _load_adapters(agate_scripts):
    """importlib 加载 agate-cmdstream-adapters.py；缺失时 pytest.fail（B 类红灯）。"""
    path = agate_scripts / "agate-cmdstream-adapters.py"
    if not path.is_file():
        pytest.fail(f"被测模块未实现: {path}（TDD 红灯，P4 实现后转绿）")
    spec = importlib.util.spec_from_file_location("agate_cmdstream_adapters", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _node_zstd_available():
    """node zstd 可用性探测：node -e 返回 function 才视为可用（dispatch-context 约束 5 同口径）。"""
    node = shutil.which("node")
    if not node:
        return False
    try:
        proc = subprocess.run(
            [node, "-e",
             "const z=require('node:zlib');"
             "process.stdout.write(typeof z.zstdDecompressSync + ' ' + typeof z.zstdCompressSync)"],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0 and "function" in proc.stdout


def _make_zstd_frame(jsonl_text, tmp_path, node_available):
    """用 node zstdCompressSync 构造真实 zstd 拼接帧（单帧），写入 tmp_path 返回路径。
    node 不可用时调用方负责 skip。"""
    node = shutil.which("node")
    script = (
        "const z=require('node:zlib');"
        "let s='';process.stdin.on('data',d=>s+=d);"
        "process.stdin.on('end',()=>process.stdout.write(z.zstdCompressSync(s)));"
    )
    proc = subprocess.run(
        [node, "-e", script], input=jsonl_text.encode("utf-8"),
        capture_output=True, text=False, timeout=30,
    )
    assert proc.returncode == 0, f"node zstdCompressSync 失败: {proc.stderr!r}"
    out = tmp_path / "session.jsonl.zstd"
    out.write_bytes(proc.stdout)
    return out


def _make_zstd_multi_frame(jsonl_frames, tmp_path):
    """构造真实 zstd 拼接帧容器（每段文本独立压缩成一帧后字节拼接），返回路径。

    对应验证记录 Q7 的拼接帧容器形态（实测 20020 帧）——CRITICAL-2 修复的复现场景。
    """
    node = shutil.which("node")
    script = (
        "const z=require('node:zlib');"
        "let s='';process.stdin.on('data',d=>s+=d);"
        "process.stdin.on('end',()=>process.stdout.write(z.zstdCompressSync(s)));"
    )
    blobs = []
    for text in jsonl_frames:
        proc = subprocess.run(
            [node, "-e", script], input=text.encode("utf-8"),
            capture_output=True, text=False, timeout=30,
        )
        assert proc.returncode == 0, f"node zstdCompressSync 失败: {proc.stderr!r}"
        blobs.append(proc.stdout)
    out = tmp_path / "multi-frame.jsonl.zstd"
    out.write_bytes(b"".join(blobs))
    return out


def _make_opencode_db(state_rows, tmp_path):
    """运行时构造最小 OpenCode SQLite 库（part 表 + data JSON blob），返回库路径。
    表结构取自验证记录（part.data.state 嵌套对象）。"""
    db = tmp_path / "opencode.db"
    conn = sqlite3.connect(str(db))
    try:
        conn.execute("CREATE TABLE part (id TEXT PRIMARY KEY, data TEXT)")
        for i, state in enumerate(state_rows):
            data = json.dumps({"type": "tool", "tool": "bash",
                               "callID": f"call_demo_{i:04d}", "state": state})
            conn.execute("INSERT INTO part (id, data) VALUES (?, ?)",
                         (f"prt_demo_{i:04d}", data))
        conn.commit()
    finally:
        conn.close()
    return db


# ================= BDD-2: claude-code 适配器从 JSONL 解析命令流 =================


def test_bdd_2_claude_adapter_parses_jsonl(agate_scripts, load_fixture):
    """BDD-2：Claude Code JSONL fixture（tool_use/tool_result 配对）→ CommandRecord，
    command=input.command、ts_start/ts_end 来自配对行 timestamp、exit 从 is_error + "Exit code N"
    解析数字并写 exit_signal 留档。"""
    adapters = _load_adapters(agate_scripts)
    adapter = adapters.ClaudeCodeAdapter()

    session = load_fixture("cmdstream/claude-code-session.jsonl")
    records = adapter.read_commands(str(session))

    assert len(records) == 3, f"期望 3 条配对记录，实际 {len(records)}"

    # toolu_demo_0002：exit=1（"Exit code 1" 文本前缀），command 来自 input.command
    r2 = next(r for r in records if r.command == "python3 -m pytest -q tests/unit")
    assert r2.platform == "claude-code"
    assert r2.tool == "Bash"
    assert r2.exit == 1
    assert "Exit code 1" in r2.exit_signal  # exit_signal 留档原始形态（验证记录差异点 2）
    assert r2.ts_start == 1788400860000  # 2026-09-03T02:01:00.000Z epoch 毫秒
    assert r2.ts_end == 1788400860387  # 2026-09-03T02:01:00.387Z epoch 毫秒

    # toolu_demo_0003：exit=0（成功路径 is_error=False + "Exit code 0"）
    r3 = [r for r in records if r.command == "python3 -m pytest -q tests/unit" and r.exit == 0]
    assert r3, "缺少 exit=0 的记录"
    assert r3[0].truncated is False


# ================= BDD-3: opencode 适配器从 SQLite 解析命令流 =================


def test_bdd_3_opencode_adapter_parses_sqlite(agate_scripts, tmp_path, load_fixture):
    """BDD-3：OpenCode SQLite fixture（part.data.state 结构，运行时构造）→ exit 直接取
    state.metadata.exit 整数、truncated 取 state.metadata.truncated 显式标记。

    fix1（T075 类修正）：fixture 含两条 command 同为 "make build-docs" 的记录（0002:
    exit=2/truncated=false；0003: exit=0/truncated=true）——旧实现以命令为键建字典会同键
    覆盖（后者覆盖前者），断言要求"同一条记录"同时具备 exit==2 与 truncated==true，fixture
    中不存在。改为参照 test_bdd_2 的过滤式匹配（(command + exit/truncated) 组合过滤），
    不依赖"命令唯一"假设；BDD-3 验收语义不变。
    """
    adapters = _load_adapters(agate_scripts)
    adapter = adapters.OpenCodeAdapter()

    state_rows = json.loads(load_fixture("cmdstream/opencode-part-state.json").read_text(encoding="utf-8"))
    db = _make_opencode_db(state_rows, tmp_path)

    records = adapter.read_commands(str(db))
    assert len(records) == 3, f"期望 3 条记录，实际 {len(records)}"

    # call_demo_0001：ip 命令唯一（exit=0 整数直接取，truncated=false）
    r1 = [r for r in records if r.command == "ip -brief addr; echo '---'; ip route"]
    assert r1 and r1[0].exit == 0
    assert r1[0].truncated is False
    assert r1[0].platform == "opencode"

    # call_demo_0002：make build-docs，exit=2（整数），truncated=false
    r2 = [r for r in records if r.command == "make build-docs" and r.exit == 2]
    assert r2, "缺少 exit=2 的 make build-docs 记录（call_demo_0002）"
    assert r2[0].truncated is False

    # call_demo_0003：make build-docs（同名命令），truncated=true（显式标记），exit=0
    r3 = [r for r in records if r.command == "make build-docs" and r.truncated is True]
    assert r3, "缺少 truncated=true 的 make build-docs 记录（call_demo_0003）"
    assert r3[0].exit == 0


# ================= BDD-4: dsh 适配器从 JSONL.zstd 解析命令流 =================


def test_bdd_4_dsh_adapter_parses_zstd(agate_scripts, tmp_path, load_fixture):
    """BDD-4：DSH JSONL.zstd 拼接帧（node 运行时构造真实 zstd 帧）→ 解压隔离在 dsh 适配器内部、
    不依赖 python zstandard、逐帧产出 CommandRecord；exit 从 isError + "Error:" 前缀解析并写
    exit_signal；tool/call + tool/result 按 callId 配对产出 ts_start/ts_end。
    node 不可用时 skip 并标注原因。"""
    if not _node_zstd_available():
        pytest.skip("node 不可用（zlib.zstdDecompressSync 非 function），跳过 DSH zstd 真实解压用例")

    adapters = _load_adapters(agate_scripts)
    adapter = adapters.DSHAdapter()

    jsonl_text = load_fixture("cmdstream/dsh-session.jsonl").read_text(encoding="utf-8")
    zstd_path = _make_zstd_frame(jsonl_text, tmp_path, node_available=True)

    records = adapter.read_commands(str(zstd_path))
    assert len(records) == 3, f"期望 3 条配对记录，实际 {len(records)}"

    by_cmd = {r.command: r for r in records}
    # call_demo_0002：isError=true + "Error:" 前缀 → exit 非 0，exit_signal 留档
    assert by_cmd["python3 -m pytest -q tests/unit"].exit != 0
    assert "Error:" in by_cmd["python3 -m pytest -q tests/unit"].exit_signal
    # call_demo_0001：isError=false → exit=0
    assert by_cmd["ls -la && find . -maxdepth 2 -type d | sort"].exit == 0
    # callId 配对：ts_start=call 时间、ts_end=result 时间（验证记录 Q3）
    r1 = by_cmd["ls -la && find . -maxdepth 2 -type d | sort"]
    assert r1.ts_start == 1787883650309
    assert r1.ts_end == 1787883650312
    assert r1.platform == "dsh"


def test_bdd_4_dsh_adapter_no_python_zstandard_dependency(agate_scripts, tmp_path, load_fixture):
    """BDD-4 补充：dsh 适配器解析路径不得硬依赖 python zstandard/zstd 二进制——加载被测模块后
    断言模块内不 import zstandard（P0 env_constraints：本机无 python zstandard）。"""
    _load_adapters(agate_scripts)  # 加载即校验被测模块存在（缺失 pytest.fail）
    src = (agate_scripts / "agate-cmdstream-adapters.py").read_text(encoding="utf-8")
    assert "import zstandard" not in src
    assert "from zstandard" not in src


# ================= BDD-5: 子 agent 会话定位（sidecar / delegationDepth） =================


def test_bdd_5_claude_subagent_sidecar_locates(agate_scripts, tmp_path):
    """BDD-5（Claude Code）：会话目录含主会话 + subagents/agent-*.jsonl sidecar 子转录时，
    list_sessions 定位到子 agent 会话文件（仅读主会话会漏掉子记录），read_commands 可解析子会话。"""
    adapters = _load_adapters(agate_scripts)
    adapter = adapters.ClaudeCodeAdapter()

    cwd = tmp_path
    (cwd / "subagents").mkdir()
    main = cwd / "main-session.jsonl"
    main.write_text(
        '{"type":"tool_use","id":"toolu_demo_main","name":"Bash","timestamp":"2026-09-03T03:00:00.000Z",'
        '"input":{"command":"python3 main.py"}}\n'
        '{"tool_use_id":"toolu_demo_main","type":"tool_result","timestamp":"2026-09-03T03:00:00.200Z",'
        '"content":"Exit code 0\\nmain done","is_error":false}\n',
        encoding="utf-8",
    )
    sub = cwd / "subagents" / "agent-demo-child.jsonl"
    sub.write_text(
        '{"type":"tool_use","id":"toolu_demo_child","name":"Bash","timestamp":"2026-09-03T03:01:00.000Z",'
        '"input":{"command":"python3 child.py"}}\n'
        '{"tool_use_id":"toolu_demo_child","type":"tool_result","timestamp":"2026-09-03T03:01:00.100Z",'
        '"content":"Exit code 0\\nchild done","is_error":false}\n',
        encoding="utf-8",
    )

    sessions = adapter.list_sessions(str(cwd))
    assert str(sub) in sessions, "sidecar 子转录文件未被 list_sessions 定位"
    assert str(main) in sessions, "主会话文件未被 list_sessions 定位"

    child_records = adapter.read_commands(str(sub))
    assert len(child_records) == 1
    assert child_records[0].command == "python3 child.py"


def test_bdd_5_dsh_delegation_depth_locates(agate_scripts, tmp_path):
    """BDD-5（DSH）：delegationDepth>0 的独立 session 文件被定位为子 agent 会话（区别于主会话）。"""
    adapters = _load_adapters(agate_scripts)
    adapter = adapters.DSHAdapter()

    cwd = tmp_path
    main = cwd / "session.jsonl.zstd"
    main.write_text("dummy-frame", encoding="utf-8")  # list_sessions 只按文件/header 定位，不解压
    child = cwd / "session-child.jsonl.zstd"
    child.write_text("dummy-frame", encoding="utf-8")

    sessions = adapter.list_sessions(str(cwd))
    # DSH 子 agent = delegationDepth>0 独立 session 文件（验证记录 Q1/Q2）
    located = [s for s in sessions if "session-child" in s]
    assert located, "delegationDepth>0 子 session 未被定位"
    assert str(main) in sessions, "主 session 未被定位"


# ================= BDD-6: 新增平台只写适配器、检测引擎零改动 =================


def test_bdd_6_adapter_registry_contract(agate_scripts):
    """BDD-6：显式注册表 ADAPTERS 含三平台键（claude-code/opencode/dsh），每项实现
    probe/list_sessions/read_commands 契约（P2 §2.1 候选 A）。"""
    adapters = _load_adapters(agate_scripts)
    assert set(adapters.ADAPTERS.keys()) >= {"claude-code", "opencode", "dsh"}
    for key, instance in adapters.ADAPTERS.items():
        for method in ("probe", "list_sessions", "read_commands"):
            assert callable(getattr(instance, method, None)), f"适配器 {key} 缺 {method} 契约方法"


def test_bdd_6_detect_consumes_registry_zero_change(agate_scripts):
    """BDD-6 补充：检测引擎代码零改动消费新平台 IR——detect 模块 import ADAPTERS 注册表
    （不感知平台），新增平台后 list_sessions/read_commands 可用。"""
    adapters = _load_adapters(agate_scripts)
    detect_path = agate_scripts / "agate-cmdstream-detect.py"
    if not detect_path.is_file():
        pytest.fail(f"被测模块未实现: {detect_path}（TDD 红灯，P4 实现后转绿）")
    spec = importlib.util.spec_from_file_location("agate_cmdstream_detect", str(detect_path))
    detect_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(detect_mod)

    # 检测引擎通过注册表消费适配器（平台无关）；模拟新增第四平台后注册表可用
    registered = set(adapters.ADAPTERS.keys())
    assert registered == {"claude-code", "opencode", "dsh"}
    # 检测引擎模块中存在对 ADAPTERS 的引用路径（零改动消费锚）
    detect_src = detect_path.read_text(encoding="utf-8")
    assert "ADAPTERS" in detect_src


# ================= BDD-7: 解析单测 fixture 取自验证记录且脱敏 =================


def test_bdd_7_fixture_sanitized(load_fixture):
    """BDD-7：fixture 样例字段结构取自验证记录，且命令/输出内容脱敏——不含真实用户路径
    （/home/kity 等）、密钥块、真实会话标识（demo 前缀占位）。"""
    import re

    for name in (
        "cmdstream/claude-code-session.jsonl",
        "cmdstream/dsh-session.jsonl",
        "cmdstream/opencode-part-state.json",
    ):
        text = load_fixture(name).read_text(encoding="utf-8")
        # 不含真实用户路径（I-14：不得泄露真实用户路径/密钥/会话标识）
        assert "/home/kity" not in text, f"{name} 含真实用户路径"
        assert "BEGIN " not in text and "PRIVATE KEY" not in text, f"{name} 含密钥块"
        # 会话/调用标识用 demo 占位（call_demo_/ses_demo_/prt_demo_/toolu_demo_），非真实 26 位 hex
        assert not re.search(r"\b(?:ses|msg|prt|call)_[0-9a-f]{26}\b", text), f"{name} 含真实会话标识"
        assert "demo" in text, f"{name} 缺 demo 脱敏占位标记"


# ================= fix1（P4-review CRITICAL-2/3/4/5/7）补充测试 =================


def test_bdd_4_dsh_multi_frame_container_returns_all_records(agate_scripts, tmp_path):
    """BDD-4 补充（CRITICAL-2，验证记录 Q7 复现）：zstd 拼接帧容器（两帧各含完整
    call+result 对）→ 逐帧解压后拼接 → 返回 2 条记录（两帧记录全部可见）。
    修复前 node zstdDecompressSync 只解第一帧 → 帧 2 的 echo late 静默丢失。"""
    if not _node_zstd_available():
        pytest.skip("node 不可用（zlib.zstdDecompressSync 非 function），跳过 DSH zstd 真实解压用例")

    adapters = _load_adapters(agate_scripts)
    adapter = adapters.DSHAdapter()

    frame1 = (
        '{"type":"tool/call","seq":101,"time":100,"data":{"callId":"call_demo_mf_1",'
        '"name":"bash","arguments":"{\\"command\\":\\"echo early@100\\"}"}}\n'
        '{"type":"tool/result","seq":102,"time":110,"data":{"message":{"source":{"kind":"tool",'
        '"callId":"call_demo_mf_1"},"content":[{"type":"tool-result","toolCallId":"call_demo_mf_1",'
        '"content":[{"type":"text","text":"early"}],"isError":false}]}}}\n'
    )
    frame2 = (
        '{"type":"tool/call","seq":103,"time":200,"data":{"callId":"call_demo_mf_2",'
        '"name":"bash","arguments":"{\\"command\\":\\"echo late@200\\"}"}}\n'
        '{"type":"tool/result","seq":104,"time":210,"data":{"message":{"source":{"kind":"tool",'
        '"callId":"call_demo_mf_2"},"content":[{"type":"tool-result","toolCallId":"call_demo_mf_2",'
        '"content":[{"type":"text","text":"late"}],"isError":false}]}}}\n'
    )
    zstd_path = _make_zstd_multi_frame([frame1, frame2], tmp_path)

    records = adapter.read_commands(str(zstd_path))
    commands = sorted(r.command for r in records)
    assert commands == ["echo early@100", "echo late@200"], (
        f"多帧容器应返回两帧全部记录（CRITICAL-2），实际 {commands}"
    )
    # 逐帧时间戳保留（帧 2 为最新帧，边写边落）
    late = next(r for r in records if r.command == "echo late@200")
    assert late.ts_start == 200 and late.ts_end == 210


def test_bdd_2_claude_unfinished_call_emits_exit_none(agate_scripts, tmp_path):
    """BDD-2 补充（CRITICAL-3）：claude-code 会话含未结束 tool_use（无配对 tool_result）
    → 适配器产出 exit=None/ts_end=None 记录（IR 契约允许 exit=None），不再静默丢弃。
    修复前 read_commands 仅从 results 反查 uses → 未结束 call 无 IR。"""
    adapters = _load_adapters(agate_scripts)
    adapter = adapters.ClaudeCodeAdapter()

    session = tmp_path / "unfinished.jsonl"
    session.write_text(
        '{"type":"tool_use","id":"toolu_unfin_1","name":"Bash",'
        '"timestamp":"2026-09-03T02:01:00.000Z",'
        '"input":{"command":"network_call_no_timeout"}}\n'
        '{"type":"tool_use","id":"toolu_done_1","name":"Bash",'
        '"timestamp":"2026-09-03T02:02:00.000Z",'
        '"input":{"command":"python3 -m pytest -q tests/unit"}}\n'
        '{"tool_use_id":"toolu_done_1","type":"tool_result",'
        '"timestamp":"2026-09-03T02:02:00.300Z",'
        '"content":"Exit code 0\\n=== 12 passed ===","is_error":false}\n',
        encoding="utf-8",
    )

    records = adapter.read_commands(str(session))
    unfinished = [r for r in records if r.command == "network_call_no_timeout"]
    assert len(unfinished) == 1, f"未结束 call 应产出记录，实际 {len(unfinished)}"
    rec = unfinished[0]
    assert rec.exit is None
    assert rec.ts_end is None
    assert rec.exit_signal == "pending"  # 未结束留档信号
    assert rec.ts_start == 1788400860000  # 2026-09-03T02:01:00.000Z epoch 毫秒
    # 已结束配对不受影响（BDD-2 既有语义保持）
    done = [r for r in records if r.command == "python3 -m pytest -q tests/unit"]
    assert done and done[0].exit == 0


def test_bdd_4_dsh_unfinished_call_emits_exit_none(agate_scripts, tmp_path):
    """BDD-4 补充（CRITICAL-3）：dsh 会话含未结束 tool/call（无配对 tool/result）
    → 适配器产出 exit=None/ts_end=None 记录。修复前 DSHAdapter 仅对配对成功者产出。"""
    if not _node_zstd_available():
        pytest.skip("node 不可用（zlib.zstdDecompressSync 非 function），跳过 DSH zstd 真实解压用例")

    adapters = _load_adapters(agate_scripts)
    adapter = adapters.DSHAdapter()

    jsonl_text = (
        '{"type":"tool/call","seq":101,"time":1787883650309,"data":{"callId":"call_demo_unfin",'
        '"name":"bash","arguments":"{\\"command\\":\\"network_call_no_timeout\\"}"}}\n'
        '{"type":"tool/call","seq":102,"time":1787883650400,"data":{"callId":"call_demo_done",'
        '"name":"bash","arguments":"{\\"command\\":\\"python3 -m pytest -q tests/unit\\"}"}}\n'
        '{"type":"tool/result","seq":103,"time":1787883650900,"data":{"message":{"source":'
        '{"kind":"tool","callId":"call_demo_done"},"content":[{"type":"tool-result",'
        '"toolCallId":"call_demo_done","content":[{"type":"text","text":"12 passed"}],'
        '"isError":false}]}}}\n'
    )
    zstd_path = _make_zstd_frame(jsonl_text, tmp_path, node_available=True)

    records = adapter.read_commands(str(zstd_path))
    unfinished = [r for r in records if r.command == "network_call_no_timeout"]
    assert len(unfinished) == 1, f"未结束 call 应产出记录，实际 {len(unfinished)}"
    rec = unfinished[0]
    assert rec.exit is None
    assert rec.ts_end is None
    assert rec.exit_signal == "pending"
    assert rec.ts_start == 1787883650309
    done = [r for r in records if r.command == "python3 -m pytest -q tests/unit"]
    assert done and done[0].exit == 0


def test_bdd_2_claude_malformed_lines_no_crash(agate_scripts, tmp_path):
    """BDD-2 补充（CRITICAL-4）：claude-code JSONL 含畸形行（timestamp 缺失/非 ISO-8601、
    非 dict 行）→ read_commands 不崩溃、跳过坏行并计数告警，合法记录不受影响。"""
    adapters = _load_adapters(agate_scripts)
    adapter = adapters.ClaudeCodeAdapter()

    session = tmp_path / "malformed.jsonl"
    session.write_text(
        # 非 JSON 行
        'this is not json\n'
        # 非 dict 行（数组）
        '["not","an","object"]\n'
        # timestamp 缺失的 tool_use（无配对 result 时也应被跳过而非崩溃）
        '{"type":"tool_use","id":"toolu_nomap_1","name":"Bash",'
        '"input":{"command":"no_timestamp_cmd"}}\n'
        # 合法配对（timestamp 非法 → 跳过该条）
        '{"type":"tool_use","id":"toolu_badts_1","name":"Bash",'
        '"timestamp":"not-a-date","input":{"command":"bad_ts_cmd"}}\n'
        '{"tool_use_id":"toolu_badts_1","type":"tool_result",'
        '"timestamp":"2026-09-03T02:00:00.100Z","content":"Exit code 0","is_error":false}\n'
        # fix2 补充：timestamp 非法类型（int）的 tool_use → 配对跳过而非崩溃（残留链 1）
        '{"type":"tool_use","id":"toolu_intts_1","name":"Bash",'
        '"timestamp":1788400860000,"input":{"command":"int_ts_cmd"}}\n'
        '{"tool_use_id":"toolu_intts_1","type":"tool_result",'
        '"timestamp":"2026-09-03T02:00:00.200Z","content":"Exit code 0","is_error":false}\n'
        # fix2 补充：timestamp 非法类型（null）的 tool_use → 配对跳过而非崩溃（残留链 1）
        '{"type":"tool_use","id":"toolu_nullts_1","name":"Bash",'
        '"timestamp":null,"input":{"command":"null_ts_cmd"}}\n'
        '{"tool_use_id":"toolu_nullts_1","type":"tool_result",'
        '"timestamp":"2026-09-03T02:00:00.300Z","content":"Exit code 0","is_error":false}\n'
        # fix2 补充：tool_result timestamp 为 int → 记录保留、ts_end=None（残留链 1）
        '{"type":"tool_use","id":"toolu_intend_1","name":"Bash",'
        '"timestamp":"2026-09-03T02:02:00.000Z",'
        '"input":{"command":"int_end_cmd"}}\n'
        '{"tool_use_id":"toolu_intend_1","type":"tool_result",'
        '"timestamp":1788400920000,"content":"Exit code 0","is_error":false}\n'
        # fix2 补充：toolUseResult 非 dict（字符串）→ 记录保留、不崩溃（残留链 2）
        '{"type":"tool_use","id":"toolu_strtr_1","name":"Bash",'
        '"timestamp":"2026-09-03T02:03:00.000Z",'
        '"input":{"command":"str_tr_cmd"}}\n'
        '{"tool_use_id":"toolu_strtr_1","type":"tool_result",'
        '"timestamp":"2026-09-03T02:03:00.300Z","content":"Exit code 0","is_error":false,'
        '"toolUseResult":"not-a-dict"}\n'
        # 合法配对（应保留）
        '{"type":"tool_use","id":"toolu_ok_1","name":"Bash",'
        '"timestamp":"2026-09-03T02:01:00.000Z",'
        '"input":{"command":"python3 -m pytest -q tests/unit"}}\n'
        '{"tool_use_id":"toolu_ok_1","type":"tool_result",'
        '"timestamp":"2026-09-03T02:01:00.300Z",'
        '"content":"Exit code 0\\n=== 12 passed ===","is_error":false}\n',
        encoding="utf-8",
    )

    records = adapter.read_commands(str(session))
    cmds = [r.command for r in records]
    assert "python3 -m pytest -q tests/unit" in cmds, "合法配对记录应保留"
    assert "no_timestamp_cmd" not in cmds, "timestamp 缺失的 use 应被跳过（不产出坏记录）"
    assert "bad_ts_cmd" not in cmds, "timestamp 非法的配对应被跳过"
    # fix2：timestamp 非法类型（int/null）的 use 配对应被跳过（不崩溃、不产出坏记录）
    assert "int_ts_cmd" not in cmds, "timestamp 为 int 的 use 配对应被跳过（残留链 1）"
    assert "null_ts_cmd" not in cmds, "timestamp 为 null 的 use 配对应被跳过（残留链 1）"
    # fix2：tool_result timestamp 为 int → 记录保留、ts_end=None（结束时间未知，不崩溃）
    intend = [r for r in records if r.command == "int_end_cmd"]
    assert intend, "tool_result timestamp 为 int 的记录应保留（残留链 1）"
    assert intend[0].ts_end is None, "tool_result timestamp 为 int → ts_end=None"
    # fix2：toolUseResult 非 dict（字符串）→ 记录保留、truncated 判定不崩溃（残留链 2）
    strtr = [r for r in records if r.command == "str_tr_cmd"]
    assert strtr, "toolUseResult 非 dict 的记录应保留（残留链 2）"
    assert strtr[0].truncated is False, "toolUseResult 非 dict → truncated 应为 False"
    # 不崩溃即通过；告警由 stderr 输出（不在此断言文本，避免平台差异）


def test_bdd_4_dsh_non_dict_lines_no_crash(agate_scripts, tmp_path):
    """BDD-4 补充（CRITICAL-4）：dsh JSONL 含非 dict 行 → read_commands 不崩溃、
    跳过畸形行，合法 call/result 不受影响。修复前 obj.get("type") 对数组/字符串行抛
    AttributeError。"""
    if not _node_zstd_available():
        pytest.skip("node 不可用（zlib.zstdDecompressSync 非 function），跳过 DSH zstd 真实解压用例")

    adapters = _load_adapters(agate_scripts)
    adapter = adapters.DSHAdapter()

    jsonl_text = (
        '["not","an","object"]\n'
        '"just a string"\n'
        '{"type":"tool/call","seq":101,"time":1787883650309,"data":{"callId":"call_demo_ok1",'
        '"name":"bash","arguments":"{\\"command\\":\\"ls -la\\"}"}}\n'
        '{"type":"tool/result","seq":102,"time":1787883650312,"data":{"message":{"source":'
        '{"kind":"tool","callId":"call_demo_ok1"},"content":[{"type":"tool-result",'
        '"toolCallId":"call_demo_ok1","content":[{"type":"text","text":"ok"}],'
        '"isError":false}]}}}\n'
    )
    zstd_path = _make_zstd_frame(jsonl_text, tmp_path, node_available=True)

    records = adapter.read_commands(str(zstd_path))
    assert len(records) == 1, f"非 dict 行应被跳过且合法记录保留，实际 {len(records)}"
    assert records[0].command == "ls -la"


def test_bdd_3_opencode_corrupt_db_no_crash(agate_scripts, tmp_path):
    """BDD-3 补充（CRITICAL-5）：OpenCode SQLite 畸形/损坏库（非 SQLite 文件/缺 part 表）
    → read_commands 返回空列表 + stderr 告警，不崩溃。修复前 DatabaseError 传播。"""
    adapters = _load_adapters(agate_scripts)
    adapter = adapters.OpenCodeAdapter()

    # 非 SQLite 文件（文本内容）
    fake_db = tmp_path / "opencode.db"
    fake_db.write_text("this is not a sqlite database\n", encoding="utf-8")
    records = adapter.read_commands(str(fake_db))
    assert records == [], "非 SQLite 文件应返回空列表（不崩溃）"

    # 合法 SQLite 但缺 part 表
    import sqlite3 as _sqlite3
    no_part = tmp_path / "no-part.db"
    conn = _sqlite3.connect(str(no_part))
    try:
        conn.execute("CREATE TABLE other (id TEXT)")
        conn.commit()
    finally:
        conn.close()
    records2 = adapter.read_commands(str(no_part))
    assert records2 == [], "缺 part 表的库应返回空列表（不崩溃）"


def test_bdd_4_dsh_truncated_marker_sets_truncated_true(agate_scripts, tmp_path):
    """BDD-4 补充（CRITICAL-7，验证记录 Q6）：DSH result content 含截断标记 → 记录
    truncated=True 且 output_hash=None（IR 契约 truncated=True → output_hash=None）。
    修复前适配器硬编码 truncated=False → 截断输出仍参与哈希比对 → 误判 SPIN。"""
    if not _node_zstd_available():
        pytest.skip("node 不可用（zlib.zstdDecompressSync 非 function），跳过 DSH zstd 真实解压用例")

    adapters = _load_adapters(agate_scripts)
    adapter = adapters.DSHAdapter()

    # 截断标记：tool-result dict 显式 truncated=true 字段（_detect_truncated 信号 ①）
    jsonl_text = (
        '{"type":"tool/call","seq":101,"time":1787883650309,"data":{"callId":"call_demo_trunc",'
        '"name":"bash","arguments":"{\\"command\\":\\"fail_task\\"}"}}\n'
        '{"type":"tool/result","seq":102,"time":1787883650312,"data":{"message":{"source":'
        '{"kind":"tool","callId":"call_demo_trunc"},"content":[{"type":"tool-result",'
        '"toolCallId":"call_demo_trunc","content":[{"type":"text","text":"error output"}],'
        '"isError":true,"truncated":true}]}}}\n'
    )
    zstd_path = _make_zstd_frame(jsonl_text, tmp_path, node_available=True)

    records = adapter.read_commands(str(zstd_path))
    assert len(records) == 1, f"期望 1 条记录，实际 {len(records)}"
    rec = records[0]
    assert rec.truncated is True, "截断标记命中应置 truncated=True"
    assert rec.output_hash is None, "truncated=True 时 output_hash 必须为 None（IR 契约）"
    # exit 解析不受影响（isError=true + 无 Error: 前缀 → isError=true 信号）
    assert rec.exit_signal == "isError=true"
