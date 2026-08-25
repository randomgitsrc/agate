$ head -15 README.md
# agate
> **Agateon (formerly agate)** — this project has a new name; the badge and install command below already point to the new repository.
> An orchestration protocol that verifies AI agents the way a build system verifies a compiler.

[![version](https://img.shields.io/badge/version-v0.63.0-blue)](https://github.com/randomgitsrc/agateon)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](README.md) | [中文](README.zh-CN.md)

## What is agate?

agate is a documentation-and-script orchestration protocol for software engineering tasks. There is no runtime, no daemon, and no build step — just a set of Markdown protocol files plus gate-check scripts that any coding agent can read and run. A single orchestrator agent never writes code itself. Instead it dispatches dedicated subagents through eight phases (P1 requirements → P2 design → P3 test-first → P4 implementation → P5 verification → P6 acceptance → P7 consistency → P8 release), and after every phase it runs an objective gate check before the state machine may advance. State is persisted to version-controlled Markdown, so progress survives crashes and remains auditable by humans.

## Why agate?


$ head -15 README.md | grep -F 'Agateon (formerly agate)'
> **Agateon (formerly agate)** — this project has a new name; the badge and install command below already point to the new repository.
EXIT_CODE: 0
