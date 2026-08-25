
## batchB implementer 进度
- [读取] dispatch-context P4-dispatch-context-implementer-batchB.md 完成
- [读取] implementer.md 角色定义完成
- [读取] P1-requirements.md 完成（BDD-5/6/7 + D2 定案）
- [读取] P2-design.md 完成（§2.2 候选A定案，匹配算法/插入位置/RM-AG0032补记流程）
- [读取] check-gate.py gate_p8() 全函数（L1181-1257）完成，确认插入点：P8-release.md 字段检查之后、version/CHANGELOG 检查之前（bump_type/debt_check 检查之后，version_pattern 之前）
- [读取] roadmap.md 确认 RM-AG0032 两行位置：L30(backlog,关联任务=—) L31(scheduled,关联任务=TAG0020)；RM-AG0042/43/44/45 四行关联任务均=TAG0023
- [实现] check-gate.py 新增 _check_roadmap_done(task_id, roadmap_path)（在 gate_p8 定义前），插入调用点在 debt_check 检查之后、version_pattern 检查之前
- [实现] roadmap.md 新增 RM-AG0032 done 行（未删除/修改原两行 backlog/scheduled），更新列=2026-08-24
