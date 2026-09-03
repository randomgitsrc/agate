=== P3-progress-version-mgmt.md init 2026-09-04T01:14:58+08:00 ===
开始执行任务

[已读] dispatch-context P3-dispatch-context-test-designer-version-mgmt.md
[已读] test-designer.md 角色定义

[已读] P0-brief.md / P1-requirements.md（BDD-1~5 定位）/ P2-design.md（簇A表格 + R1 全段 + files_to_read + gate_commands）

[已读] agate_common.py L1-36/L551-580, agate-pack-offline.py 全文, install-offline.py 全文, agate-install.py L1-63/L225-320, test_agate_pack_offline.py 全文, test_install_offline.py 全文, test_agate_common.py 全文, UPGRADING.md/README.md 相关段落
[已写] test_agate_common.py 追加 BDD-1 三个测试（文件hash/目录hash/单一定义grep），预期 ImportError/断言失败

[已写] test_agate_pack_offline.py 追加 BDD-1 identity 测试
[已写] test_install_offline.py 追加 BDD-1 行为一致性测试 + R1 两条测试（yaml不可用引导 / checksum不匹配前置校验）
[已写] 新建 test_agate_install_uninstall.py（BDD-4/5，_find_references 二元组解包 ValueError 红灯 + WARNING 断言）
[已写] test_agate_common.py 追加 BDD-3 文档信任边界测试（UPGRADING.md + scripts/README.md）
下一步：写 agate/tests/regression/test_offline_bundle_roundtrip.py（BDD-2 全流程回归）

[已跑] pytest agate/tests/unit/test_agate_common.py agate/tests/unit/test_agate_pack_offline.py agate/tests/unit/test_install_offline.py agate/tests/unit/test_agate_install_uninstall.py agate/tests/regression/test_offline_bundle_roundtrip.py -v
结果：12 failed, 32 passed, 0 errors（无 collection error/语法错误）
红灯类型：
- test_agate_common.py x5: ImportError(compute_sha256 subprocess returncode=1) x2 + AssertionError(单一定义grep命中2处/文档缺信任边界文案) x3
- test_agate_pack_offline.py x1: AttributeError(agate_common无compute_sha256属性)
- test_install_offline.py x3: AttributeError(agate_common无compute_sha256 / module无_ensure_agate_common) x3
- test_agate_install_uninstall.py x2: ValueError(_find_references仍返回plain list，解包(refs,hit_limit)二元组失败)
- test_offline_bundle_roundtrip.py x1: AttributeError(agate_common无compute_sha256属性)
全部为 B 类红灯（assertion失败/项目内ImportError/AttributeError/ValueError，非测试代码语法错误），已实测确认。
下一步：写 P3-test-cases-version-mgmt.md 并用 agate-md-field-set.py 填 frontmatter
