=== command: head -15 README.zh-CN.md ===
# agate
> **Agateon**（原名 agate）——本项目已改名，下方徽标与安装命令已指向新仓库。
> 一种编排协议，用构建系统验证编译器的方式验证 AI Agent。

[![version](https://img.shields.io/badge/version-v0.62.0-blue)](https://github.com/randomgitsrc/agateon)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](README.md) | [中文](README.zh-CN.md)

## What is agate?

agate 是一套面向软件工程任务的文档 + 脚本编排协议。没有运行时、没有守护进程、没有构建步骤——只是一组 Markdown 协议文件加 gate 检查脚本，任何编码 Agent 都能读取并运行。单个编排 Agent（orchestrator）从不亲自写代码。它通过八个阶段派发专职 subagent（P1 需求 → P2 设计 → P3 测试先行 → P4 实现 → P5 验证 → P6 验收 → P7 一致性 → P8 发布），每阶段结束后、状态机推进前，都必须通过一次客观的 gate 检查。状态落盘到版本化 Markdown 中，进度在崩溃后得以存活，且可供人审计。

## Why agate?


=== command: head -15 README.zh-CN.md | grep -E 'Agateon.*agate|agate.*Agateon' ===
> **Agateon**（原名 agate）——本项目已改名，下方徽标与安装命令已指向新仓库。
EXIT_CODE: 0
