# Recovery Model

> Supports `RULE-REC-001 / RULE-GUARD-001`.
> Core proposition: **model source, data, and external-side-effect recovery separately**. Git rollback must not impersonate data or production recovery. Protect user work before rolling back.

## Three Recovery Classes

| Class | Objects | Mechanisms |
|---|---|---|
| Source recovery | Files, commits, configuration | Revert, explicit file restoration, controlled branch |
| Data recovery | Schema, data writes, migrations | Down migration, backup restoration, compensation script |
| External-side-effect recovery | Cloud resources, releases, API calls, messages, traffic | Provider rollback, compensating transaction, human remediation |

Do not summarize the last two as "return to a green Git point." Report each class and its uncovered areas separately.

## Instantiate a Version-Control Strategy

At Project Mode initialization, choose and record one strategy:

| Strategy | Meaning |
|---|---|
| `record-only` | The Agent records the current commit and diff but does not create commits or tags |
| `agent-commit` | The user has authorized task- or Phase-level Agent commits |
| `branch-per-agent` | Each writer uses a branch or worktree and one integrator merges |

Without authorization, do not create a tag, branch, or commit by default.

## Known-Good Point

After a Phase gate passes, a known-good point should record at least:

- the commit or controlled diff identifier;
- dirty-worktree state;
- gate evidence with assurance level and revision;
- data or external side effects that remain uncovered;
- authorization required for rollback;
- concurrent work from other Agents.

## Source Rollback Priority

Default order:

1. Revert an independent commit owned by the current Agent.
2. Restore explicitly listed files or sections.
3. Rebuild in an isolated branch or worktree.
4. Consider a broad rollback only with explicit user authorization and confirmation that no other work will be lost.

Never default to `git reset --hard`, overwrite uncommitted user work, roll back another Agent's accepted result, or report source restoration as completed data or production recovery.

## Guarded Recovery Gate

Before guarded Auto-ready, require the corresponding recovery or compensation path: a data down migration or backup, and an external provider rollback or compensating transaction. Without recovery, remain copilot or require human approval and explicitly mark the gap as uncovered.
