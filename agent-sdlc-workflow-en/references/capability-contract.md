# Harness Capability Contract

> Supports `RULE-AUT-001 / RULE-CLAIM-001 / RULE-GUARD-001 / RULE-GOAL-001`.
> Core proposition: **define capability interfaces first, then bind them to a concrete Harness. File mechanisms are fallbacks only.** The skill orchestrates behavior; it does not invent capabilities. Degrade when a capability is missing.

## Required Capabilities

| Capability | Purpose |
|---|---|
| `evidence-capture` | Automatically capture gate execution, revision, result, and raw output; prerequisite for A1 or higher |
| `atomic-claim` | Atomically claim a task and prevent duplicate ownership |
| `blocking-permission` | Truly block production, real-data, hard-to-recover, and out-of-scope operations; prerequisite for guarded auto |

## Recommended Capabilities

| Capability | Purpose |
|---|---|
| `independent-verify` | Let a fresh context, independent Agent, or CI rerun a critical gate; source of A2 |
| `isolated-workspace` | Isolate concurrent writers with a branch, worktree, or sandbox |

## Capability Negotiation

On entry to Project Mode, inspect the existing Harness, issue tracker, CI, and permission systems and produce a conclusion. Do not make the user fill a table; ask only when product semantics, authorization, or a risk choice requires a person.

```yaml
capabilities:
  evidence_capture: self | tool | independent | enforced
  atomic_claim: harness | tracker | file | none
  blocking_permission: harness | human | none
  independent_verify: available | unavailable
  isolated_workspace: available | unavailable
```

- `evidence_capture: self` = A0; `tool` = A1; `independent` = A2; `enforced` = A3.
- Store the conclusion in the project environment checklist (`plans/env-gates-checklist.md`) as an Auto-ready criterion.

## Relationship Between Capabilities and Execution Mode

| Condition | Decision |
|---|---|
| `evidence_capture = self` | Fast-track is allowed; Project remains copilot and at most Plan-ready |
| Project Auto | `evidence_capture` must be at least `tool` (A1) |
| guarded Auto | Requires `blocking_permission` and the relevant recovery gate |
| multi Auto | Requires `atomic_claim`; otherwise serialize or degrade |
| critical Goal or release | Prefer `independent-verify` (A2) |

## Degrade Instead of Inventing Capability

| Missing capability | Degradation |
|---|---|
| No machine evidence capture | Do not enter Project Auto; remain copilot and Plan-ready |
| Multi-agent work without atomic claim | Use one writer or coordinator-serialized dispatch; do not claim multi Auto-ready |
| Guarded work without blocking permission | Forbid auto and require human approval; do not substitute text |
| No data recovery | Do not describe source rollback as complete recovery; state the uncovered area |

## Harness Binding Requirements

Core rules define capability interfaces without hard-coding platform APIs. Concrete implementations belong in `references/bindings/`, with `generic.md` plus one file for each tested Harness:

- state the applicable version or verification date;
- prefer native Harness tools, task systems, hooks, permissions, and CI;
- fall back to capability degradation when a binding is unavailable;
- before v2.0 stable, complete dogfood for at least one real binding and mark release candidates as unverified until then.
