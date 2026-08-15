#!/usr/bin/env python3
"""检查 evidence JSON 与 P6-acceptance.md 的 PASS/FAIL 一致性（py 抽离批次 5）。

从 EVIDENCE_DIR / P6_FILE env 读。P6 标 PASS 但 evidence JSON 显示 FAIL 的 BDD，
逐行输出 "BDD-x: P6 标 PASS 但 evidence JSON 显示 FAIL"。
"""

import glob
import json
import os
import re
import sys

evidence_dir = os.environ["EVIDENCE_DIR"]
p6_file = os.environ["P6_FILE"]

if not os.path.isfile(p6_file):
    sys.exit(0)

pass_bdds = set()
with open(p6_file, encoding="utf-8") as f:
    for line in f:
        m = re.match(r"^\s*-\s*PASS\s+(BDD-\d+)", line, re.IGNORECASE)
        if m:
            pass_bdds.add(m.group(1))

fail_in_evidence = set()
for json_path in glob.glob(os.path.join(evidence_dir, "**/*.json"), recursive=True):
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            continue
        results = data.get("bdd_results", data.get("results", []))
        if isinstance(results, list):
            for r in results:
                if isinstance(r, dict):
                    bdd_id = r.get("id", r.get("bdd", ""))
                    status = r.get("status", "").lower()
                    if status == "fail" and bdd_id:
                        fail_in_evidence.add(bdd_id)
    except Exception:
        continue

inconsistent = pass_bdds & fail_in_evidence
for bdd in sorted(inconsistent):
    print(f"{bdd}: P6 标 PASS 但 evidence JSON 显示 FAIL")
