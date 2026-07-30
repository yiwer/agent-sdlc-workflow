# Template 3: Phase and Task Plan

> Save as `plans/<milestone>.md`. Prefer end-to-end verifiable increments over horizontal technical layers.
> Reference behavior rules by ID from `references/core-rules.md` inside the skill.

For a single-task fast-track, record the goal, ACs, and verification commands in the conversation or existing issue. Do not create this file (`RULE-FAST-001`).

In Project Mode, the Agent drafts the complete plan from the spec, prototype, and environment loop. A person and the Agent discuss scope and tradeoffs here; do not make the person decompose an empty Todo list.

## Four-Dimension Execution Configuration (`RULE-MODE-001`)

Record the plan's result. AC count, a request for auto, multi-agent use, and one high-risk operation are not routing shortcuts; they affect autonomy, collaboration, and risk independently.

```text
scale: fast | project          autonomy: copilot | auto
risk: standard | guarded       collaboration: single | multi
```

Rationale: __. Adjust the configuration during execution only under the migration rules in `references/core-rules.md`.

## Phases

| Phase | Verifiable increment | Regression scope | Exit gate |
|---|---|---|---|
| P0 | Thinnest primary path | Relevant integration + critical path | __ |

Front-load high-uncertainty, high-impact, or hard-to-recover work so errors appear early.

## Task Card

```markdown
### T1: <verifiable objective>
- AC: AC-__
- Dependencies: none / T__
- Impact area: __ (estimation and concurrency coordination only, not a file permission allowlist; RULE-SCOPE-001)
- Local verification: __
- Regression escalation: none / trigger from RULE-VAL-001: __
- Evidence assurance: A0/A1/A2/A3/J1 (see references/evidence-assurance.md)
- Review/ADR: none / __
- Completion signal: __
```

Size a task so the model can understand, implement, and verify it in one focused execution. Do not impose a fixed file count or duration. When execution reveals an omitted file, edit it directly and summarize the impact in the checkpoint (`RULE-SCOPE-001`).

## Dependencies and Parallelism

- Keep the DAG acyclic and mark only real prerequisites.
- Avoid actual write conflicts. Shared read-only files do not prevent parallel work.
- Follow `RULE-CLAIM-001`: prefer Harness or tracker atomic claim, isolated workspace, one integrator, and post-merge regression. Without atomic claim, serialize or remain copilot. **NOTES.md is a broadcast board, not a lock.**
- Assign shared write points such as migrations, public schema, and lockfiles to one owner in a serialized lane.
- When one task blocks, continue other tasks whose dependencies are satisfied.

## Copilot to Auto Handoff

The Agent summarizes the four-dimension configuration, Phase increments, complete Todo list, critical path, risks, exit gates, capability negotiation, and expected human gates, then declares one state:

- `Plan-ready`: the spec and plan are reviewable, but the environment feedback loop has not been tested, or the user requested only a planning package.
- `Auto-ready`: environment commands and the engineering canary were tested; `evidence_capture` is at least tool (A1); guarded work has blocking permission and recovery gates; multi work has atomic claim.

Only an `Auto-ready` plan whose critical goal and tradeoffs a person confirms becomes the stage 4 execution Goal. After that, do not request approval for ordinary tasks or each Phase. Degrade under `RULE-AUT-001` when capability is insufficient. A `Plan-ready` result must list the remaining conditions for `Auto-ready`.

## Exit Gates

- [ ] The four-dimension configuration and rationale are recorded without AC-count routing.
- [ ] Every AC is covered by a task; every task has local verification, assurance, and necessary escalation conditions.
- [ ] Every Phase produces a verifiable increment.
- [ ] Dependencies, shared write points, and concurrency control are explicit; work is serialized when atomic claim is absent.
- [ ] Stage 2 feedback commands can verify every Phase exit gate.
- [ ] `Plan-ready` or `Auto-ready` is explicit. When handing off to execution, Auto-ready capability prerequisites are met and a person has confirmed the goal and material tradeoffs without file-by-file approval.
