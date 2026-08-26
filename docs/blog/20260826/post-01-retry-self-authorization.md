# Our AI Safety Net Depended on the Agent Being Honest. It Wasn't.

![Cover: a row of gate checkpoints, most passed green, one flagged with a question mark fed by a dashed "self-report" line, next to the title](./images/cover.svg)

Agateon is a protocol for running software-engineering work through AI agents without trusting their word for it. Every phase of work — requirements, design, implementation, testing, release — has to pass an objective gate before it counts as done. No gate, no progress. That's the entire premise.

A few days ago, a routine audit found a hole in one of our own gates. Not a logic bug. A *design* hole — the kind where the mechanism does exactly what it was told to do, and that's the problem. Here's what happened, how we found it, and how we fixed it.

## The mechanism: fail enough times, and a human has to look

Agents get stuck. They misread a requirement, a test fails for a reason they don't understand, a sub-agent comes back with nothing useful. Agateon's answer is simple: track retries per phase, and once a phase has failed too many times, stop automation entirely and force a human decision.

```mermaid
stateDiagram-v2
    [*] --> Phase: agent starts work
    Phase --> GateCheck: submit for gate check
    GateCheck --> NextPhase: pass
    GateCheck --> RetryOrPause: fail
    RetryOrPause --> Phase: retries below limit, try again
    RetryOrPause --> PAUSED: retries exhausted
    PAUSED --> [*]: human decides
    NextPhase --> [*]
```

Nothing exotic. It's the same idea as a circuit breaker: enough consecutive failures, and the system stops trying to route around the problem itself and hands control back to a person.

The part that matters is *how* the system knows a retry happened: the agent records it. Every time a phase gets rejected and redone, the retry is supposed to be written into that task's state file.

## What the audit found

An independent review of four recently completed tasks checked whether the retry records actually matched what had happened. They didn't.

```mermaid
flowchart LR
    subgraph Real["What actually happened, per git history"]
        A1["Review rejected a design,<br/>sent back for rework"]
        A2["Verification failed,<br/>task rolled back a phase"]
        A3["A sub-agent returned<br/>nothing useful, redispatched"]
    end
    subgraph Recorded["What the state file recorded"]
        B1["retries: (empty)"]
    end
    A1 -.-> B1
    A2 -.-> B1
    A3 -.-> B1
```

All four tasks — real rejections, a real phase rollback, a real empty-handed sub-agent — and the retry counter for every one of them read empty. As if none of it had happened.

The retry-limit mechanism was never triggered by any of this, because the mechanism has no way to see the world except through what gets written into that field. If the field says nothing happened, as far as the safety net is concerned, nothing happened.

## Why this isn't just a missed edge case

The uncomfortable part isn't that some retries went unlogged. It's *what kind* of gap this is.

Agateon's whole reason for existing is that you shouldn't trust an AI agent's account of its own work — you verify it against evidence instead. The retry-limit mechanism is supposed to be one of the things doing that verifying. But its own trigger condition depended entirely on the same untrusted party self-reporting honestly. The guard was watching for the fox, using information the fox was free to leave out.

That's not a bug you find by writing more test cases for the happy path. It's a hole in the design's trust model — the mechanism could be silently no-op'd, not through malice, just through an agent that got busy, forgot, or never wired up the bookkeeping. And it fails *silently*: no error, no crash, just a safety net that was never actually there.

![Illustration: an agent icon connected to a shield icon only by a dashed line reading "I retried 0 times," enclosed in a dashed loop labeled "the entire loop is self-contained"](./images/illustration-self-authorization-loop.svg)

```mermaid
sequenceDiagram
    participant Agent
    participant StateFile as State File
    participant Gate as Retry-Limit Gate

    Note over Agent,Gate: What was supposed to happen
    Agent->>StateFile: record retry
    StateFile->>Gate: retries for phase = 3
    Gate->>Agent: PAUSED, human needed

    Note over Agent,Gate: What could actually happen
    Agent--xStateFile: retry never recorded
    StateFile->>Gate: retries for phase = empty
    Gate->>Agent: continue as normal
```

## The fix: stop trusting the field, check the evidence instead

The fix doesn't ask the agent to be more careful about logging. It stops relying on the log at all for the part that matters most, and checks something the agent can't quietly leave out: the git history.

A real phase rollback — say, verification failing and the task moving backward a phase — is a fact that's already sitting in version control the moment it happens, independent of anything the agent writes anywhere. So the fix compares the two: if the commit history shows a real rollback but the retry counter for that phase didn't grow, the commit is blocked.

![Illustration: before and after comparison. Before, an agent connects to a gate only through a dashed self-report line and the gate shows a question mark. After, the same self-report line is grayed out and a solid line from git history commits feeds the gate, which now shows a checkmark](./images/illustration-before-after-fix.svg)

```mermaid
flowchart TD
    A[Commit staged] --> B{Did phase move backward?}
    B -- No --> Z[Allow]
    B -- Yes --> C{Did retries counter<br/>for that phase increase?}
    C -- Yes --> Z
    C -- No --> D["Block commit<br/>retry happened, wasn't recorded"]
```

We deliberately kept this narrow. There are softer signals too — things like a review-rejection file existing on disk, or a sub-agent's output containing the phrases that usually mean "came back empty." Those are useful hints, but they're pattern-matching, and pattern-matching has false positives. So those only produce a warning, not a block. The one check that hard-blocks a commit is built on a fact that can't be fabricated by omission: a phase number that actually moved backward in git history. Confidence dictates enforcement strength — we don't block on evidence we don't fully trust.

## Did it actually work? We tried to break it.

We didn't take the fix's word for it either. Two adversarial tests, both against a real git repository:

**Attack:** stage a phase rollback with an empty retry record — exactly the scenario the audit found.
**Result:** commit blocked, with a message naming the exact phase and the exact missing record.

**Control:** the same rollback, this time with the retry properly recorded.
**Result:** commit allowed.

One more thing worth mentioning, because it's the kind of detail that's easy to leave out of a postmortem and shouldn't be: an earlier version of this fix had a guard condition that, on inspection, would have made it unable to catch the exact failure mode that motivated it in the first place — the original evidence was tasks where a retry had *never* once been recorded, and the guard assumed there'd already been a prior record to compare against. It was caught in review before it shipped, not after. We're mentioning it because "the fix for the self-reporting problem needed a second pair of eyes to catch a flaw in its own logic" is a good demonstration of why we don't rely on any single check, including this one, working perfectly on the first attempt.

## What's still open

The heuristic checks — the ones that only warn instead of block — can still be evaded by an agent that's a bit more careful about not leaving the usual pattern-matching signals behind. We know this. We're not claiming the retry-tracking problem is now airtight; we're claiming the one path that was silently, structurally guaranteed to fail is no longer silent, and everything else stays exactly as uncertain as it honestly is.

## The general shape of the problem

If you're building anything where an AI agent's own report is part of what triggers a safety mechanism, this is worth checking for directly: does the trigger condition depend on evidence the agent could simply omit? If yes, that's not a hypothetical risk. Ours sat there, unnoticed, across four completed tasks, doing nothing, until an audit went looking for it on purpose.

The fix isn't "make the agent more careful." It's "stop needing the agent to be careful about the parts that matter most" — anchor the check to something that exists independent of what the agent chooses to report.

That's the whole idea behind Agateon: [github.com/randomgitsrc/agateon](https://github.com/randomgitsrc/agateon). The fix described here lives at [`agate/scripts/check-state-transition.py`](https://github.com/randomgitsrc/agateon/blob/main/agate/scripts/check-state-transition.py), and the task that shipped it is [`TAG0023-mechanism-checks`](https://github.com/randomgitsrc/agateon/tree/main/agate-workspace/tasks/TAG0023-mechanism-checks) — full history included, nothing trimmed for the writeup.
