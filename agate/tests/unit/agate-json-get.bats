#!/usr/bin/env bats
# tests/unit/agate-json-get.bats — 共享 JSON 提取工具单元测试
load ../helpers/load.bash

@test "JGET.1 get 取标量键 + 默认值" {
    run bash -c "echo '{\"exit_code\":2,\"failed\":3}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' get exit_code 1"
    [ "$status" -eq 0 ]
    [[ "$output" == "2" ]]
    run bash -c "echo '{\"exit_code\":2,\"failed\":3}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' get missing 0"
    [[ "$output" == "0" ]]
}

@test "JGET.2 get 字符串键默认空串" {
    run bash -c "echo '{\"a\":\"b\"}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' get project_module \"\""
    [ "$status" -eq 0 ]
    [[ "$output" == "" ]]
}

@test "JGET.3 len 取数组长度（默认 0）" {
    run bash -c "echo '{\"commands\":[{\"cmd\":\"a\"},{\"cmd\":\"b\"}]}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' len commands"
    [ "$status" -eq 0 ]
    [[ "$output" == "2" ]]
    run bash -c "echo '{\"commands\":[]}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' len commands"
    [[ "$output" == "0" ]]
    run bash -c "echo '{}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' len missing"
    [[ "$output" == "0" ]]
}

@test "JGET.4 index 取嵌套数组元素字段" {
    run bash -c "echo '{\"commands\":[{\"cmd\":\"pytest\",\"formatter\":\"pytest.sh\"},{\"cmd\":\"pytest\",\"formatter\":\"pytest.sh\"}]}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' index commands 0 cmd"
    [ "$status" -eq 0 ]
    [[ "$output" == "pytest" ]]
    run bash -c "echo '{\"commands\":[{\"cmd\":\"pytest\",\"formatter\":\"pytest.sh\"}]}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' index commands 0 formatter"
    [[ "$output" == "pytest.sh" ]]
}

@test "JGET.5 set 改写键并重排 JSON" {
    run bash -c "echo '{\"commands\":[{\"cmd\":\"pytest\"}],\"project_module\":\"\"}' | PROJECT_MODULE=mymod python3 '$AGATE_SCRIPTS/agate-json-get.py' set project_module PROJECT_MODULE"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"project_module": "mymod"'* ]]
}

@test "JGET.6 count_prefix 统计 module 前缀匹配数" {
    run bash -c "echo '{\"import_errors\":[{\"module\":\"mymod.foo\"},{\"module\":\"other.bar\"},{\"module\":\"mymod.baz\"}]}' | PROJECT_MODULE=mymod python3 '$AGATE_SCRIPTS/agate-json-get.py' count_prefix import_errors module PROJECT_MODULE"
    [ "$status" -eq 0 ]
    [[ "$output" == "2" ]]
}
@test "JGET.7 list 逐行打印数组每个元素" {
    run bash -c "echo '{\"failed_tests\":[\"a\",\"b\",\"c\"]}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' list failed_tests"
    [ "$status" -eq 0 ]
    [[ "$output" == *"a"* ]]
    [[ "$output" == *"b"* ]]
    [[ "$output" == *"c"* ]]
    run bash -c "echo '{}' | python3 '$AGATE_SCRIPTS/agate-json-get.py' list missing"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "JGET.8 escape json.dumps stdin 原始文本" {
    run bash -c "printf '%s' 'a\"b
c' | python3 '$AGATE_SCRIPTS/agate-json-get.py' escape"
    [ "$status" -eq 0 ]
    [[ "$output" == *'a\"b'* ]]
}
