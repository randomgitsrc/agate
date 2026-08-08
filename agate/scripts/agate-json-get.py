#!/usr/bin/env python3
"""从 stdin 读 JSON，按子命令提取/改写字段（py 抽离共享工具）。

统一 .sh 里散落的单行 JSON 提取内联段：
  echo "$x" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get(...))'

用法（JSON 从 stdin 传入）：
  get KEY DEFAULT      打印 d.get(KEY, DEFAULT)（DEFAULT 按字符串原样打印，缺失时返回）
  len KEY              打印 len(d.get(KEY, []))（缺失返回 0）
  index KEY IDX SUBKEY 打印 d[KEY][IDX][SUBKEY]
  set KEY ENVNAME      d[KEY]=os.environ[ENVNAME]；打印 json.dumps(d)
  count_prefix LIST SUBKEY ENVNAME  打印 LIST 中 SUBKEY 以 os.environ[ENVNAME] 开头的元素个数
  list KEY              逐行打印 d.get(KEY, []) 每个元素（用于 failed_tests 迭代）

未知子命令 → stderr 提示 + exit 2。
"""

import json
import os
import sys


def main():
    op = sys.argv[1]
    if op == "escape":
        print(json.dumps(sys.stdin.read()))
        return
    data = json.load(sys.stdin)

    if op == "get":
        key, default = sys.argv[2], sys.argv[3]
        print(data.get(key, default))
    elif op == "len":
        key = sys.argv[2]
        print(len(data.get(key, [])))
    elif op == "index":
        key, idx, subkey = sys.argv[2], int(sys.argv[3]), sys.argv[4]
        print(data[key][idx][subkey])
    elif op == "set":
        key, envname = sys.argv[2], sys.argv[3]
        data[key] = os.environ[envname]
        print(json.dumps(data))
    elif op == "count_prefix":
        listkey, subkey, envname = sys.argv[2], sys.argv[3], sys.argv[4]
        prefix = os.environ[envname]
        print(sum(1 for e in data.get(listkey, []) if e.get(subkey, "").startswith(prefix)))
    elif op == "list":
        key = sys.argv[2]
        for e in data.get(key, []):
            print(e)
    else:
        sys.stderr.write("agate-json-get: unknown op {}\n".format(op))
        sys.exit(2)


if __name__ == "__main__":
    main()