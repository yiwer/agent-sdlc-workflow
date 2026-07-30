# Project Constitution

> The Agent proposes recommendations and reasons based on the project; a person adopts, adjusts, or marks them not applicable. Store only cross-stage disciplines that cannot be inferred reliably from code.
> The single authoring source for behavior rules is `references/core-rules.md` inside the skill. This file references rule IDs without restating full rules.

## Recommended Engineering Baseline

| Practice | Agent recommendation and rationale | Decision: adopt / adjust / N/A |
|---|---|---|
| SDD / spec-first | Define the goal, non-goals, and numbered ACs before production behavior | |
| Test-first | Select TDD, local failing evidence, or an equivalent method based on risk | |
| Independent review | Require at least one review by a person or Agent in a different context before integration | |
| ADR | For a material tradeoff, record the recommendation, alternatives, and consequences | |
| Automated acceptance | Exercise critical paths with Playwright or an equivalent boundary-level check | |
| Local run / deployment | Provide one repeatable command to start or deploy and demonstrate the result | |

Reuse equivalent existing capability instead of adding process mechanically. Give a short reason for N/A. Keep one-off implementation details out of the constitution and ADRs (`RULE-MIN-001`).

## Capability Negotiation Result

> Under `RULE-AUT-001`, the Agent fills this after inspecting the Harness, tracker, CI, and permissions. Do not make the user fill it. Auto-ready depends on this result. See `references/capability-contract.md`.

```yaml
capabilities:
  evidence_capture: self | tool | independent | enforced   # -> A0/A1/A2/A3
  atomic_claim: harness | tracker | file | none
  blocking_permission: harness | human | none
  independent_verify: available | unavailable
  isolated_workspace: available | unavailable
```

- With `evidence_capture = self` (A0), the project remains copilot and at most Plan-ready; do not enter Project Auto.
- Forbid guarded auto until `blocking_permission` exists (`RULE-GUARD-001`).

## Version-Control Strategy

> See `RULE-REC-001` and `references/recovery-model.md`.

| Strategy | Meaning | Project choice |
|---|---|---|
| `record-only` | The Agent records the commit or diff but does not create commits or tags | |
| `agent-commit` | The user authorizes task- or Phase-level commits | |
| `branch-per-agent` | Each writer uses a branch or worktree and one integrator merges | |

Without authorization, do not create tags, branches, or commits by default.

## Project Verification Commands

| Purpose | Command | Pass criterion | Maximum assurance |
|---|---|---|---|
| Local / fast check | `__` | __ | __ |
| Affected regression | `__` | __ | __ |
| Complete / release gate | `__` | __ | __ |
| Build / package | `__` | __ | __ |
| Critical-path E2E | `__` | __ | __ |
| Local run / deploy | `__` | __ | __ |

Add security, performance, migration, and recovery gates only when those risks are real. The capture mechanism determines the assurance ceiling of a local command; see `references/evidence-assurance.md`.

## Verification Cadence

Apply `RULE-VAL-001`: local -> affected -> Phase -> Goal, escalating shared-surface changes early and reusing unchanged green evidence. See `references/core-rules.md` for full semantics and the table above for project commands.

## Agent Autonomy and Human Boundaries

- Autonomy and degradation: `RULE-AUT-001` and `RULE-SCOPE-001`; an impact area is not a permission allowlist.
- A person decides changes to the goal or ACs, new external authorization or payment, production or real-data work, and destructive or hard-to-recover operations (`RULE-USER-001`).
- Continue other safe work while locally blocked. Consolidate a question only when no safe path remains.

## Amendments

Record the reason and date for constitution changes and have a person confirm them. Do not turn one-off exceptions into permanent rules.

---
Version: v2.0 | Date: __
