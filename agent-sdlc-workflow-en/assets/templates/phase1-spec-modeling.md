# Template 1: Requirements, Five-Dimension Model, and Prototype

> Save as `specs/<feature>.md`. The Agent investigates and proposes a draft before confirming it with a person. Do not make the user begin with an empty form.
> Reference behavior rules by ID from `references/core-rules.md` inside the skill.

## Product Positioning and Boundaries

| Item | Content |
|---|---|
| Users, scenarios, and pain points | __ |
| Value provided | __ |
| Success behavior or metrics | __ |
| Non-goals | __ |
| Critical assumptions | __ |
| Primary risks | __ |

Check relevant boundaries for input, empty states, permissions, concurrency and idempotency, failure and recovery, performance, compatibility, and the data lifecycle. Omit an inapplicable boundary only after considering it.

## Five-Dimension Entity Model

> **First ask whether this project has domain entities worth modeling.** For a pure tool, script, or thin wrapper, skip the five tables and give one sentence explaining why.
> These tables are **probes, not deliverables**. Filling them does not prove understanding; invented attributes or events are liabilities (`RULE-MIN-001`). Keep a row only when it constrains implementation or verification. Delete it when it affects no AC.

### Objects

| Object | Key attributes | Lifecycle / state | Ownership boundary |
|---|---|---|---|
| | | | |

### Behaviors

| Behavior | Initiator | Preconditions | Result / failure semantics | Related AC |
|---|---|---|---|---|
| | | | | |

### Events

| Event | Triggering behavior | Payload | Subscribers / side effects |
|---|---|---|---|
| | | | |

### Relations

| Relation | Cardinality / direction | Update or deletion rule |
|---|---|---|
| | | |

### Rules

| # | Invariant / business rule | Enforcement point | Failure behavior | Related AC |
|---|---|---|---|---|
| R-1 | | DB/service/client/policy | | |

Treat all five dimensions as requirement probes. Every Behavior and Rule row should trace to an AC; delete candidates that do not. Give one sentence for an inapplicable dimension.

## Acceptance Criteria

| AC | Observable behavior | Related rule | Verification | Expected assurance |
|---|---|---|---|---|
| AC-1 | WHEN __, the system SHALL __ | R-1 | Automated command / human experience | A1/A2/J1 |

- Make conditions, behavior, and results unambiguous without forcing one sentence pattern.
- ACs required for Agent auto must be automatically verifiable. See `references/evidence-assurance.md`.
- Mark human experience or business sign-off as a human gate (J1); never replace it with self-attestation.

## Prototype Iteration

After forming the model, choose the cheapest prototype that resolves the current uncertainty. Start with a flow table, state diagram, or static wireframe. Build a runnable prototype only when real interaction must be tested.

| Check | Result / evidence | Model or AC update |
|---|---|---|
| Does every core behavior have a sensible entry point and feedback? | | |
| Can the product express critical rules, states, and exceptions correctly? | | |
| Does the prototype fully communicate the intended product capabilities? | | |
| Are visual hierarchy, interaction, and information structure acceptable? | | |

Use the prototype to probe the model, not as a one-off visual deliverable. Feed every finding back into the five-dimension model and ACs. At stage end, ask a person to confirm the core flow, capability expression, and experience decisions that must be made now. Explicitly defer visual polish when appropriate.

## Exit Gates

- [ ] Product positioning, non-goals, assumptions, and major boundaries are clear.
- [ ] All five dimensions were considered; applicable content has no material open questions, or an N/A reason is recorded.
- [ ] ACs cover the primary path and important failure paths, with verification and expected assurance.
- [ ] The prototype communicates core capabilities and findings have been fed back into the model and ACs.
- [ ] A person confirms critical capability expression and applicable visual or interaction experience (J1).
