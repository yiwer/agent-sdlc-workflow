# Evidence Assurance Model

> Supports `RULE-EVD-001 / RULE-EVD-002 / RULE-EVD-003 / RULE-HARD-001 / RULE-GOAL-001`.
> Core proposition: **evidence trustworthiness is a multidimensional assurance property, not the value of one field and not merely the existence of an evidence path**.

## Assurance Is a Product of Multiple Dimensions

```text
author path x revision/input binding x enforced execution x verification coverage x tamper resistance x freshness
```

A missing dimension lowers overall trust. No single field can upgrade low-assurance evidence.

## Four Automated Evidence Levels

| Level | Author and execution path | Appropriate use |
|---|---|---|
| `A0 self-reported` | Agent prose or manually transcribed result | Leads, process summaries, explicit fast-track reporting |
| `A1 tool-captured` | Harness automatically records execution, revision, exit, and output | Ordinary Project evidence gates |
| `A2 independently-replayed` | A fresh context, independent verifier, or CI reruns at the same revision | Project Goals, critical ACs, guarded critical verification |
| `A3 externally-enforced` | Protected CI, permissions, branch protection, or deployment systems truly block | Hard gates |

## Human Judgment

| Level | Meaning |
|---|---|
| `J1 human-approved` | Approval identifies the person, time, object, and conclusion |
| `J0 pending/rejected` | Not yet approved or explicitly rejected |

## Machine Authorship Does Not Automatically Mean High Trust

Even machine capture can produce misleading A1 evidence unless you check:

- whether it is bound to the current commit or dirty diff;
- whether the gate definition existed before execution;
- whether the Agent can modify the capture mechanism or CI configuration;
- whether the command covers the promised AC;
- whether the result remains fresh;
- whether selective skipping was possible;
- whether raw output is locatable.

Therefore, **Harness-captured local commands are usually A1, not A2 or A3**. A2 requires a fresh context or verifier to rerun at the same revision. A3 requires a truly blocking external system whose configuration the Agent cannot rewrite.

## Compact Evidence Record

Prefer Harness-generated records. Let the Agent add explanation without manually filling every field.

```yaml
gate_id: G-P1-E2E
assurance: A1
requirement: AC-3
revision: abc123
dirty_diff_hash: null
source: "playwright test checkout"
result: passed
exit_code: 0
artifact_pointer: "run://..."
captured_by: "harness-id"
captured_at: "2026-07-23T18:21:12Z"
freshness: exact_revision   # exact_revision | impact_analyzed | stale
```

Mark Agent-supplied fields:

```yaml
provenance: self-reported
```

**Agent-supplied fields cannot upgrade A0 to A1.** Treat a self-entered `assurance: A1` as A0 when no machine author appears in `captured_by`.

A Markdown checkpoint may show compact columns, but the underlying record must cover:
`Gate | Assurance | Revision | Command/Source | Exit/Conclusion | Raw Evidence | Verifier | Freshness`.

## Baseline When Machine Capture Is Unavailable

A local command is only a reproduction recipe, not evidence that it passed this time. To prove an execution passed, also retain the revision or dirty-diff hash, start and end times, exit code, raw-output transcript, critical artifact identity, and toolchain or lockfile identity. Otherwise report A0. Do not commit sensitive logs directly: store a redacted summary and identifier, use an ignored directory, record a pointer to secure external storage, and set retention limits.

## Evidence Reuse (`RULE-EVD-003`)

Reuse evidence only when all conditions hold:

1. The current revision equals the evidence revision, or an impact analysis proves that intervening changes do not affect the gate's code, configuration, test inputs, or environment.
2. The gate definition has not changed.
3. The evidence artifact remains accessible.

"I think it is unrelated" is insufficient. At minimum, record the reuse rationale and freshness decision in the checkpoint.

## Minimum Goal Assurance (`RULE-GOAL-001`)

| Scenario | Minimum requirement |
|---|---|
| fast + standard | A0 is permitted, but the final report must explicitly say `self-reported` |
| project + standard + auto | Critical evidence gates require at least A1 |
| guarded critical action | A2 plus blocking permission |
| hard gate | A3 |
| human experience or business acceptance | J1 |
