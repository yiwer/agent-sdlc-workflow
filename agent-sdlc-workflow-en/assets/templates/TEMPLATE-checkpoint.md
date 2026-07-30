# Checkpoint: <task-id>

- Result: complete / partially blocked / failed / auto_paused
- AC: __
- Lifecycle state: implementation_complete / automated_verified / human_acceptance_pending / ... (`RULE-STATE-001`)
- Summary: __

## Verification Evidence

> Prefer Harness-generated records. Let the Agent add explanation; see `references/evidence-assurance.md`.
> Mark Agent-supplied fields `self-reported`. They **cannot upgrade A0 to A1**. A command is a reproduction recipe, not proof that it passed.

| Gate | Assurance | Revision | Command / source | Exit / conclusion | Raw evidence pointer | Verifier `captured_by` | Freshness |
|---|---|---|---|---|---|---|---|
| | A0/A1/A2/A3/J0/J1 | | | | | | exact_revision/impact_analyzed/stale |

- Evidence reuse must satisfy `RULE-EVD-003`: revision and input binding, unchanged gate, accessible artifact. Reuse rationale: __
- Human gates use J0/J1 and cannot be replaced by automated self-attestation.

## Material Deviations

- None / __
- Spec delta required: no / __; `deferred` requires an approved delta and cannot bypass an AC.
- Drift found during re-anchor: no / __ (`RULE-ANCHOR-001`)

## Multi-Agent Work

> Complete when applicable under `RULE-CLAIM-001`.

- Task claim: task_id / owner / base_revision / write_scope / released: yes/no
- NOTES.md broadcasts state and never acts as a lock.

## Next Step

- Next task or recovery entry point: __
- User decision required: none / __; list only true blockers under `RULE-USER-001`.
