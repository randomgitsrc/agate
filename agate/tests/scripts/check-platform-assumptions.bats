#!/usr/bin/env bats
# tests/scripts/check-platform-assumptions.bats — 平台假设静态扫描器行为测试（TAG0009 BDD-1~9；TAG0010 py 化）
# 被测对象：agate/scripts/check-platform-assumptions.py（TAG0010 自 check-platform-assumptions.sh 迁移；TDD 红灯目标 = 命令不存在）
#
# 扫描器契约（P4 实现须满足，P2-design §2.1）：
#   用法：check-platform-assumptions.py [target...]
#     - target 为文件或目录；目录 target 递归扫描 *.bats / *.bash / *.sh / *.py（扩展名过滤）
#     - 无参数时默认扫描 agate/tests/
#   规则：
#     R1 硬编码 PATH（/usr 或 /bin 字面赋值）
#     R2 命令位置裸 python3（豁免 command -v 探测、env 形式、shebang、行首 @test 标题、行首注释行、docstring 块）
#     R3 方括号形式 -L 单平台 symlink 断言
#     R4 临时目录字面量（豁免 BATS_TEST_TMPDIR 变量行与含 # scan-exempt: 标记的行）
#     R5 命令位置裸外部工具（bc 为已登记项；模式集可扩充 seq/timeout 等）
#   输出：命中行形如 `R{n} <file>:<line> <摘要>`（含规则号与命中文件路径）；无命中无输出
#   退出：0 = 无命中；1 = 有命中；2 = 目标不存在
#   平台无关：仅用 Python 标准库纯 re 引擎，不调用外部 grep，禁用 --perl-regexp 等 GNU 专用特性（BDD-1）
#
# 本测试文件自身必须保持"干净"：fixture 内容全部在运行时用 fragment 拼接法构造，
# 源码任何一行都不出现 R1-R5 的字面命中（含注释），确保扫描器对全树扫描时本文件 0 命中。

load ../helpers/load.bash

# 写一个 fixture 文件到 $BATS_TEST_TMPDIR 下（内容逐行给出，运行时写入）
make_fixture() {
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/scan-fx-XXXXXX")
    local f="$dir/fixture.txt"
    local line
    for line in "$@"; do
        printf '%s\n' "$line" >> "$f"
    done
    echo "$f"
}

# 运行扫描器扫描 fixture，断言命中指定规则（exit 1 + 输出含规则号与文件路径）
assert_hit() {
    local fx="$1"
    local rule="$2"
    run "$PYTHON" "$AGATE_SCRIPTS/check-platform-assumptions.py" "$fx"
    [ "$status" -eq 1 ]
    [[ "$output" == *"$rule"* ]]
    [[ "$output" == *"$fx"* ]]
}

@test "test_bdd_1_scanner_script_exists_platform_neutral" {
    # 扫描器本体存在且无 GNU 专用特性（纯 re 引擎，无外部命令调用 / 无 --perl-regexp）——BDD-1
    [ -f "$AGATE_SCRIPTS/check-platform-assumptions.py" ]
    # py 版逐行扫描仅用标准库、不调用外部命令（无 subprocess/os.system/os.popen 入口）
    run grep -nE 'subprocess|os\.system|os\.popen' "$AGATE_SCRIPTS/check-platform-assumptions.py"
    [ "$status" -eq 1 ]
    run grep -n -- '--perl-regexp' "$AGATE_SCRIPTS/check-platform-assumptions.py"
    [ "$status" -eq 1 ]
}

@test "test_bdd_2_scanner_detects_hardcoded_path" {
    # R1：fixture 含硬编码 PATH 字面 → 非零 + 报告 R1 与文件路径——BDD-2
    local lead='PATH="'
    local mid='/usr/bin:'
    local tail='/bin"'
    local line="${lead}${mid}${tail}"
    local fx
    fx=$(make_fixture "$line")
    assert_hit "$fx" "R1"
}

@test "test_bdd_3_scanner_detects_bare_python3" {
    # R2：fixture 含命令位置的 python3（非探测形态）→ 非零 + 报告 R2（豁免形态见 BDD-9 干净 fixture）——BDD-3
    local py='python'
    local ver='3'
    local line="${py}${ver} -c 'print(1)'"
    local fx
    fx=$(make_fixture "$line")
    assert_hit "$fx" "R2"
}

@test "test_bdd_4_scanner_detects_symlink_assertion" {
    # R3：fixture 含方括号形式 -L 断言 → 非零 + 报告 R3——BDD-4
    local open='[[ -'
    local flag='L'
    local line="${open}${flag} \"\$repo/.git/hooks/pre-push\" ]]"
    local fx
    fx=$(make_fixture "$line")
    assert_hit "$fx" "R3"
}

@test "test_bdd_5_scanner_detects_tmp_path" {
    # R4：fixture 含临时目录字面量逻辑路径（cd 用法）→ 非零 + 报告 R4（样例文本豁免见 scan-exempt 用例）——BDD-5
    local tm='/tm'
    local p
    p="${tm}p"
    local line="cd ${p}"
    local fx
    fx=$(make_fixture "$line")
    assert_hit "$fx" "R4"
}

@test "test_bdd_6_scanner_detects_bare_bc" {
    # R5：fixture 含命令位置的 bc（工具名，Unix-only）→ 非零 + 报告 R5——BDD-6
    local bc='b'
    bc+='c'
    local line="echo 1 | ${bc}"
    local fx
    fx=$(make_fixture "$line")
    assert_hit "$fx" "R5"
}

@test "test_bdd_8_clean_tree_zero_detection" {
    # 修复完成后 agate/tests/ 全树扫描 0 命中（同类扫描闭环；P3 红灯 = 命令不存在）——BDD-8
    run "$PYTHON" "$AGATE_SCRIPTS/check-platform-assumptions.py" "$AGATE_ROOT/tests"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "test_bdd_9_dirty_fixture_all_rules_reported" {
    # 含全部 5 类假设的 fixture → 非零 + R1~R5 全部报告——BDD-9（含假设 fixture）
    local lead='PATH="'
    local mid='/usr/bin:'
    local tail='/bin"'
    local l1="${lead}${mid}${tail}"
    local py='python'
    local ver='3'
    local l2="${py}${ver} -c 'import sys'"
    local open='[[ -'
    local flag='L'
    local l3="${open}${flag} \"\$f\" ]]"
    local tm='/tm'
    local p
    p="${tm}p"
    local l4="cd ${p}"
    local bc='b'
    bc+='c'
    local l5="echo 1 | ${bc}"
    local fx
    fx=$(make_fixture "$l1" "$l2" "$l3" "$l4" "$l5")
    run "$PYTHON" "$AGATE_SCRIPTS/check-platform-assumptions.py" "$fx"
    [ "$status" -eq 1 ]
    [[ "$output" == *"R1"* ]]
    [[ "$output" == *"R2"* ]]
    [[ "$output" == *"R3"* ]]
    [[ "$output" == *"R4"* ]]
    [[ "$output" == *"R5"* ]]
    [[ "$output" == *"$fx"* ]]
}

@test "test_bdd_9_clean_fixture_zero_report" {
    # 干净 fixture：R2 全部豁免形态（shebang / command -v 探测 / env 形式 / @test 标题 / 注释行）
    # + R4 天然豁免（BATS_TEST_TMPDIR 变量名）→ 零退出无报告——BDD-9（干净 fixture + 豁免契约）
    local sh='#!/usr/bin/env '
    local py='python'
    local ver='3'
    local line1="${sh}${py}${ver}"
    local cv='command -v '
    local line2="${cv}${py}${ver} || ${cv}${py}"
    local ev='env '
    local line3="${ev}${py}${ver}"
    local at='@test "'
    local line4="${at}${py}${ver} title\""
    local cm='# 说明 '
    local line5="${cm}${py}${ver}"
    local line6='clean_dir=$BATS_TEST_TMPDIR/demo'
    local fx
    fx=$(make_fixture "$line1" "$line2" "$line3" "$line4" "$line5" "$line6")
    run "$PYTHON" "$AGATE_SCRIPTS/check-platform-assumptions.py" "$fx"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "test_bdd_9_directory_scan_respects_shell_extension_filter" {
    # 目录目标：递归扫 *.bats/*.bash/*.sh/*.py，忽略其他扩展名——BDD-8/9（目录扫描契约）
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/scan-dir-XXXXXX")
    local lead='PATH="'
    local mid='/usr/bin:'
    local tail='/bin"'
    local dirty="${lead}${mid}${tail}"
    printf '%s\n' "$dirty" > "$dir/ignored.txt"
    printf '%s\n' "$dirty" > "$dir/dirty.bats"
    printf '%s\n' "$dirty" > "$dir/dirty.py"
    run "$PYTHON" "$AGATE_SCRIPTS/check-platform-assumptions.py" "$dir"
    [ "$status" -eq 1 ]
    [[ "$output" == *"R1"* ]]
    [[ "$output" == *"dirty.bats"* ]]
    [[ "$output" == *"dirty.py"* ]]
    [[ "$output" != *"ignored.txt"* ]]
}

@test "test_bdd_9_scan_exempt_exempts_r4_sample_text" {
    # 负向：含 # scan-exempt: 标记的样例文本行（临时目录字面量）→ R4 豁免，零命中——BDD-9（标记豁免仅限 R4）
    local tm='/tm'
    local p
    p="${tm}p"
    local line="echo imported from ${p}/demo/fixture.txt # scan-exempt: mock 输出样例文本（非路径假设）"
    local fx
    fx=$(make_fixture "$line")
    run "$PYTHON" "$AGATE_SCRIPTS/check-platform-assumptions.py" "$fx"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "test_bdd_9_scan_exempt_does_not_exempt_r1_path" {
    # 负向：标记不豁免 R1——含标记的 PATH 命中行仍应被检出（防标记被当作任意假设白名单）
    local lead='PATH="'
    local mid='/usr/bin:'
    local tail='/bin"'
    local line="${lead}${mid}${tail} # scan-exempt: 尝试用标记豁免 R1"
    local fx
    fx=$(make_fixture "$line")
    assert_hit "$fx" "R1"
}

@test "test_bdd_9_scan_exempt_does_not_exempt_r2_python" {
    # 负向：标记不豁免 R2——含标记的命令位置裸 python3（仍应被检出）
    local py='python'
    local ver='3'
    local line="${py}${ver} -c 'print(1)' # scan-exempt: 尝试用标记豁免 R2"
    local fx
    fx=$(make_fixture "$line")
    assert_hit "$fx" "R2"
}

@test "test_bdd_9_scan_exempt_does_not_exempt_r3_symlink" {
    # 负向：标记不豁免 R3——含标记的方括号 -L 断言仍被检出
    local open='[[ -'
    local flag='L'
    local line="${open}${flag} \"\$repo/.git/hooks/pre-push\" ]]# scan-exempt: 尝试用标记豁免 R3"
    local fx
    fx=$(make_fixture "$line")
    assert_hit "$fx" "R3"
}

@test "test_bdd_9_docstring_exempts_r2_python_sample" {
    # 正向：docstring 块内 python3（文档非可执行代码，与 # 注释同类豁免）→ 零命中——BLOCKER-1（TAG0010 py 化新增）
    local q='"""'
    local py='python'
    local ver='3'
    local line1="${q}"
    local line2="    ${py}${ver} -c 'print(1)'"
    local line3="${q}"
    local fx
    fx=$(make_fixture "$line1" "$line2" "$line3")
    run "$PYTHON" "$AGATE_SCRIPTS/check-platform-assumptions.py" "$fx"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "test_bdd_9_docstring_exemption_does_not_cover_bare_python3" {
    # 负向：docstring 块外裸 python3（块外示例代码非 docstring）→ 仍命中 R2——BLOCKER-1（TAG0010 py 化新增）
    local q='"""'
    local py='python'
    local ver='3'
    local line1="${q}"
    local line2="    ${py}${ver} -c 'print(1)'"
    local line3="${q}"
    local line4="${py}${ver} -c 'print(2)'"
    local fx
    fx=$(make_fixture "$line1" "$line2" "$line3" "$line4")
    run "$PYTHON" "$AGATE_SCRIPTS/check-platform-assumptions.py" "$fx"
    [ "$status" -eq 1 ]
    [[ "$output" == *"R2"* ]]
    [[ "$output" == *"$fx"* ]]
}
