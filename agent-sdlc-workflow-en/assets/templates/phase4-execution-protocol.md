# Template 4: Long-Running Goal / Auto Execution Protocol

> The Todo items, ACs, and Phase gates confirmed in stage 3 form one Goal. Except for a true blocker, execute continuously to Goal completion instead of waiting after every task card.
> Reference behavior rules by ID from `references/core-rules.md` inside the skill.

## Autonomous Execution Loop

```text
Read the constitution, spec, plan, NOTES, and capability conclusion
-> claim the next dependency-ready task under RULE-CLAIM-001
-> establish failing/baseline evidence -> implement -> verify locally -> perform required review/ADR
-> write a concise checkpoint/NOTES entry with assurance and captured_by
-> continue to the next ready task
-> all Phase gates pass -> re-anchor under RULE-ANCHOR-001 -> enter the next Phase
-> all Todo items complete -> final acceptance using phase5 and honest lifecycle reporting
```

## Autonomous Scope (`RULE-AUT-001 / RULE-SCOPE-001`)

- Read and write repository files needed for the current Goal. An impact area is not a permission allowlist.
- Let the Agent choose implementation details, code organization, test combinations, and reversible tradeoffs from repository context.
- Use checkpoints for visibility and recovery, not routine approval.
- Degrade when capability or evidence is insufficient, such as auto -> copilot. Do not use prose to pretend missing capability exists.

## Specification Discipline

Apply the SDD, TDD, review, ADR, and acceptance practices adopted in the constitution, and meet the assurance required by `RULE-GOAL-001`. When a practice is inapplicable to a task, record a short reason in the checkpoint instead of asking each time.

For cross-session or long-running work, use `plans/logs/TEMPLATE-checkpoint.md`. For a one-session task, the final verification summary is the checkpoint. Version control provides ordinary file diffs.

## Re-anchor Check

> Required after every Phase gate under `RULE-ANCHOR-001`.

Compare in this order: current approved spec -> approved spec deltas -> current Goal/ACs/non-goals -> original user intent. **Approved requirement evolution is not drift.**

1. Does every current work item trace to a valid AC, risk mitigation, or approved delta?
2. Does the current diff touch a non-goal?
3. Has an external interface, data state, or permission meaning appeared without a spec or ADR?
4. Do current tests prove user value, or only internal consistency?
5. Is every remaining task still necessary to complete the Goal?
6. If the user saw only current observable behavior, would they consider the approved problem solved?

When drift is suspected, analyze impact and make reversible corrections first. If the existing spec uniquely determines the answer, resolve it autonomously. Submit a spec delta or ask the user only when product semantics must change. Re-anchoring must not become a new high-frequency interruption. A long Phase may re-anchor at a checkpoint instead of waiting for Phase end.

## Circuit Breaker (`RULE-BREAK-001`)

Enter `auto_paused` without declaring the project failed. Preserve still-valid increments, provide recovery entry points, and do not retry silently when any condition occurs:

- The same failure recurs without a new hypothesis, evidence item, or experiment.
- Independent hypotheses are disproved up to the configured exploration limit.
- An instantiated budget is being consumed far faster than increments are passing gates; do not invent this metric when the platform exposes no budget.
- Continuing requires undoing multiple verified tasks, signaling accumulated error.
- Repeated re-anchors find the same class of goal deviation.
- Work enters an unauthorized guarded scope.

Report the `auto_paused` state, completed still-valid increments, invalid or suspicious increments, tested hypotheses, new evidence, unresolved decisions, and a recommendation: continue exploration, adjust the spec, roll back, or hand off to a person.

## Recovery

> Follow `RULE-REC-001` and `references/recovery-model.md`.

Model and report source, data, and external-side-effect recovery separately. Git rollback does not count as data or production recovery.

- Default order: revert an independent commit owned by the Agent -> restore explicitly listed files or sections -> rebuild in an isolated branch/worktree -> broad rollback only with explicit user authorization and confirmation that no other work will be lost.
- Never default to `git reset --hard`, overwrite uncommitted user work, or roll back accepted work from another Agent.
- Do not create tags, branches, or commits by default; follow the constitution's version-control strategy.
- Before guarded rollback, confirm a data down migration or backup and an external provider rollback or compensation path. Explicitly mark missing coverage.

## Verification Cadence

Under `RULE-VAL-001`, run the shortest local check after a coherent change, not the full suite after every edit. Run affected regression at task or batch completion. At Phase exit, run relevant integration, contracts, and critical paths. At Goal completion, ensure complete or release-level green evidence exists after the last code change; reuse a covering higher-level result. See `references/core-rules.md` for escalation triggers and green-evidence reuse. Change the hypothesis before rerunning a failure that yields no new information.

## Spec Feedback and User Involvement

When implementation reveals a specification error, pause the affected task, record the new fact, propose a spec delta, and update impact analysis. Continue independent work where possible.

Under `RULE-USER-001`, consolidate a user request only when the goal, non-goals, or ACs must change; new external permissions, paid services, production, or real data is required; or an action is destructive, hard to recover, or out of scope, and no safe alternative task remains. Do not ask about ordinary test failures, omitted files, equivalent refactors, implementation choices, or first-pass diagnosis.

## Multi-Agent Work (`RULE-CLAIM-001`)

- Primary path: Harness/tracker atomic claim -> branch/worktree isolation -> one integrator -> cross-agent regression.
- Without atomic claim, use one writer or coordinator-serialized dispatch, remain copilot, and do not claim multi Auto-ready.
- File claim is fallback only; see `references/bindings/generic.md`. Do not create it by default. **NOTES.md is not a lock.**
- Each Agent hands off the base revision, final revision or diff, gate evidence, new ADRs or spec deltas, and recommended integration order.

## Goal Completion (`RULE-STATE-001 / RULE-GOAL-001`)

After all Todo items finish, use the stage 5 template automatically and report lifecycle state honestly:

- collect evidence at the required A0-A3/J0-J1 assurance for every AC;
- confirm every Phase exit gate passed;
- confirm a complete or release-level gate is green after the last code change, reusing only an equivalent or stronger fresh result under `RULE-EVD-003`;
- audit agreement among the spec, implementation, tests, and material ADRs;
- give every unfinished item a disposition and retain only reusable lessons.

When automated gates pass and a human gate is pending, report `automated_verified`, not `accepted`. Report a state only when all of its criteria are met.
