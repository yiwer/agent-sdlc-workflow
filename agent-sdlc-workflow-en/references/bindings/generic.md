# Binding: generic (Degraded Fallback Without Harness Primitives)

- Applies to any Agent environment without hooks, task systems, permission blocking, or isolated workspaces.
- Status: fallback baseline, available since v2.0-rc.1.
- Verified: 2026-07-23.

This binding describes behavior after capability degradation. It does not pretend that machine evidence or atomic scheduling exists.

## Capability Mapping

| Capability | Generic value | Consequence |
|---|---|---|
| `evidence-capture` | `self` (A0) | Fast-track only; Project remains copilot and Plan-ready, never Auto |
| `atomic-claim` | `file` or `none` | Prefer `none` with one writer or serialized work; use file claims only when multiple writers are truly necessary |
| `blocking-permission` | `human` | All guarded operations require human approval; auto is forbidden |
| `independent-verify` | `unavailable` | Mark critical Goals as not independently verified; never claim A2 |
| `isolated-workspace` | `unavailable` | Serialize writers |

## A0 Evidence Baseline

Without machine capture, manually record as much as possible for each evidence item: revision, command, exit, time, and raw-output location. Mark `assurance: A0` and `provenance: self-reported`. The final report must say "self-reported; not machine-captured."

## File Claim (Fallback Only)

Use a file claim only when multiple writers are necessary and no tracker or scheduler exists. Otherwise use one writer.

- Path: `plans/claims/<task-id>.json`; create the directory only when needed.
- Acquisition must use **exclusive create**. If the file exists, the claim fails; never overwrite an earlier claim.
- Include at least `task_id / owner / base_revision / write_scope / shared_write_lane / claimed_at / lease_expires_at / status`.
- An ordinary Agent must not overwrite an expired lease. A coordinator records the reclaim reason and releases it.
- A recovery task must read the original owner's checkpoint and diff.
- Shared write points such as migrations, public schema, lockfiles, global configuration, and release manifests enter a single-owner serialized lane by default.

**NOTES.md is a broadcast board and never a lock.**

## Upgrade Path

When the Harness gains native capability, switch to the matching binding, such as `claude-code.md`, and raise the supportable assurance and concurrency levels accordingly.
