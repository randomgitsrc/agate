# agate

> An orchestration protocol that verifies AI agents the way a build system verifies a compiler.

[![version](https://img.shields.io/badge/version-v0.57.0-blue)](https://github.com/randomgitsrc/agate)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](README.md) | [中文](README.zh-CN.md)

## What is agate?

agate is a documentation-and-script orchestration protocol for software engineering tasks. There is no runtime, no daemon, and no build step — just a set of Markdown protocol files plus gate-check scripts that any coding agent can read and run. A single orchestrator agent never writes code itself. Instead it dispatches dedicated subagents through eight phases (P1 requirements → P2 design → P3 test-first → P4 implementation → P5 verification → P6 acceptance → P7 consistency → P8 release), and after every phase it runs an objective gate check before the state machine may advance. State is persisted to version-controlled Markdown, so progress survives crashes and remains auditable by humans.

## Why agate?

LLM agents are powerful but unreliable on long tasks: context gets polluted, subagents drift, and "it looks done" becomes the only quality signal. agate treats an AI agent the way a build system treats a compiler — you don't trust the output, you verify it through gates.

- **Gates are hard boundaries.** Progress is blocked on objective signals — a test runner's exit code, a typechecker, a git log — not on "looks about right."
- **State is persisted.** Every phase's result lands in version-controlled Markdown, so work survives interruptions and is auditable by humans.
- **Roles are isolated.** Each phase runs in a dedicated subagent, keeping the orchestrator's context clean and the review genuinely independent.
- **Zero infrastructure.** Your agent only needs to read files and run commands — nothing to deploy, no service to operate.

> agent + gate → agate

## Quick start

1. **Install agate.** Clone the repository and point `~/.agate` at the protocol body (`agate/`), or use the one-shot installer:
   ```bash
   curl -sSL https://raw.githubusercontent.com/randomgitsrc/agate/main/install.sh | bash
   ```
   For **per-project version pinning**, use the version manager instead (installs versioned directories under `~/.agate/vX.Y.Z/`, keeps the legacy `~/.agate` symlink for backward compatibility):
   ```bash
   python3 ~/.agate/scripts/agate-install.py              # latest
   python3 ~/.agate/scripts/agate-install.py v0.49.0      # a specific version
   python3 ~/.agate/scripts/agate-install.py --check      # environment probe
   ```
2. **Register the orchestrator.** Symbolically link `orchestrator-template.md` into your platform's agent directory and install the git hooks (`python3 ~/.agate/scripts/install-hook.py`). Platform-specific steps — OpenCode, Claude Code, and Windows fallbacks — are in [`agate/SETUP.md`](agate/SETUP.md).
3. **Run your first task.** Start a session with the orchestrator agent. The workspace (`agate-workspace/`) is initialized automatically on the orchestrator's first run; see [`agate/SETUP.md`](agate/SETUP.md) for the one-time setup.

## How it works

```
Orchestrator
  │ dispatches
  ▼
P0 brief → P1 analyst → P2 architect → P3 test-designer → P4 implementer
         → P5 verifier → P6 verifier → P7 consistency-reviewer → P8 release
  │ after every phase
  ▼
gate check (test runner exit code, typechecker, git log, BDD runs)
  │ pass
  ▼
state persisted (active-tasks.md / .state.yaml) → next phase
```

The orchestrator does exactly four things: read state, dispatch subagents, run gates, and update state. It never writes phase artifacts itself. A phase may only advance when its gate passes; a failed gate bounces the phase back (within a retry limit) before the state machine moves on. Phase definitions and pruning rules are in [`agate/WORKFLOW.md`](agate/WORKFLOW.md).

## Supported platforms

| Platform | Task tool | Recommended use |
|----------|-----------|-----------------|
| OpenCode | ✅ | Full P0-P8 |
| Claude Code | ✅ | Full P0-P8 |
| DSH | ✅ | Full P0-P8 |
| Claude Project sessions | ❌ | Design phases (P0-P2) only |

See [`agate/platform-notes.md`](agate/platform-notes.md) for platform-specific adaptations, including native Windows (Git for Windows) support.

## Documentation

| If you want to… | Read |
|-----------------|------|
| Integrate agate into a project for the first time | [`agate/SETUP.md`](agate/SETUP.md) |
| Understand the P0-P8 phase workflow and pruning rules | [`agate/WORKFLOW.md`](agate/WORKFLOW.md) |
| Read the protocol body entry point (for agents and deep users) | [`agate/AGENTS.md`](agate/AGENTS.md) |
| Adapt agate to your platform (OpenCode / Claude Code / Windows) | [`agate/platform-notes.md`](agate/platform-notes.md) |
| Understand known structural limitations | [`agate/LIMITATIONS.md`](agate/LIMITATIONS.md) |
| Check breaking changes before upgrading | [`agate/UPGRADING.md`](agate/UPGRADING.md) |
| Look up the glossary / ubiquitous language | [`agate/CONTEXT.md`](agate/CONTEXT.md) |
| Review architecture decision records | [`agate/adr.md`](agate/adr.md) |
| Run the test suite (maintainers) | [`agate/tests/README.md`](agate/tests/README.md) |

## Design principles

- **Document protocol, not a code framework.** Zero infrastructure — any agent that can read files can use agate.
- **Gates are hard boundaries.** An objective, externally produced result decides whether a phase passes, not a subjective "looks right."
- **State is persisted.** Any interruption resumes from the last completed phase.
- **Roles are isolated.** Dedicated subagents execute each phase; the orchestrator never pollutes its own context with implementation work.

Gates fall into two trust classes, based on who produces the judged artifact:

| Type | Phases | Judged by | Trust |
|------|--------|-----------|-------|
| External output gate | P3, P4, P5 | External tool output (test runner exit code, typechecker, git log) | High — the orchestrator cannot fake external output |
| Self-authored file gate | P1, P2, P6, P7 | Files written by the orchestrator itself | Mitigated — author and judge are the same actor |

Self-authored gates are mitigated, never cured, by evidence-existence checks, objective provenance audits, and BDD count cross-checks — raising the cost of fabrication and leaving an audit trail. See [Limitation 3 in `agate/LIMITATIONS.md`](agate/LIMITATIONS.md).

Adoption is progressive. Pruning is decided in P1, not automatic: the analyst classifies the task on a complexity × risk matrix, writes a reason for every skipped phase, and the orchestrator confirms the plan. Small single-point changes run a pruned flow (P1 + P3 + P4 + P5) — P3 test-first is kept by default and skipped only with an explicit justification (config-only changes, or a ≤3-line change already covered by a regression test), while P7 consistency is dropped for low/medium-risk changes but mandatory for high-risk (security/data/permission) ones. Medium changes run the full P1-P8; high-risk tasks keep acceptance and consistency mandatory and warrant a final human review. P6 acceptance is never pruned.

## Known limitations

agate takes the document-protocol route, which carries structural limits: the quality ceiling of its gates, the cognitive (not truly independent) nature of role isolation, and the orchestrator's judgment as a single point of failure. **Read [`agate/LIMITATIONS.md`](agate/LIMITATIONS.md) before adopting — it is honest about what this protocol does not solve.**

## Contributing

agate itself is developed with agate. Start at the maintainer entry point [`agate/AGENTS.md`](agate/AGENTS.md) and run the test suite with:

```bash
python3 -m pytest agate/tests/
```

## License

[MIT](LICENSE)
