# Binding: claude-code (Claude Code Capability Binding)

- Applies to Claude Code CLI with hooks, permissions, subagents, worktrees, and skills.
- Status: design complete and configured in this repository through `.claude/settings.json` and `.claude/hooks/`; real dogfood data remains a v2.0 stable release gate.
- Verified: 2026-07-23 for design and repository integration.

> Honest qualification: the mapping below is based on public Claude Code capabilities and **has not yet passed real-project dogfood**. Until dogfood passes, projects using this binding must reduce claimed assurance by one level and say so.

## Repository Configuration (Dogfood in Progress)

This repository implements the binding as follows:

- `.claude/settings.json`
  - `permissions.deny` blocks destructive operations such as `git reset --hard`, `git push --force` or `-f`, `git clean -fd(x)`, and broad absolute-path or home-directory `rm -rf` commands.
  - `permissions.ask` requires confirmation for `--force-with-lease`, `branch -D`, `checkout -- .`, `restore .`, `rebase`, and similar operations.
  - An asynchronous, non-blocking `hooks.PostToolUse` rule matching Bash invokes `.claude/hooks/capture_evidence.py`.
- `.claude/hooks/capture_evidence.py` appends records only for verification commands such as test, build, lint, typecheck, and e2e. Each record contains command, revision, dirty-diff hash, exit code, result, output summary, time, and session in `plans/logs/evidence.jsonl`, marked `assurance: A1`, `provenance: tool-captured`, and `captured_by: claude-code:PostToolUse`. The hook always exits 0 and never blocks the session.

An Agent-triggered local command is at most A1, not A2 or A3. A2 requires a `code-review` skill, subagent, or CI to rerun at the same revision. A3 requires a protected external system that truly blocks. Evidence logs are local session data and are ignored by `.gitignore`; human-authored Markdown checkpoints remain commit candidates. Projects may add their own deploy, migrate, or production command prefixes to `deny`, whose permission rules match command prefixes.

> A newly created `.claude/` configuration is not observed until `/hooks` reloads or Claude Code restarts. After reload, any matching test or build command writes an evidence record.

## Capability Mapping

| Capability | Claude Code primitive | Reachable level | Honest limitation |
|---|---|---|---|
| `evidence-capture` | Bash captures stdout, stderr, and exit code; `PostToolUse` persists a record | **A1** | Agent-triggered Bash can be misread or selectively invoked, so it is at most A1 |
| `independent-verify` | `code-review` skill, fresh-context subagent, or external CI | **A2** | Must rerun at the same revision; a subagent shares model blind spots, so security gates should still go to CI or a person |
| `blocking-permission` | Allow/deny settings, blocking `PreToolUse` hooks, sandbox mode | Local **harness**; production/deployment still **human/CI** | Can block dangerous local commands; people or external systems still own production, real-data, and release approval |
| `atomic-claim` | One main session coordinates subagents; an issue tracker coordinates multiple sessions | `harness` in-session / `tracker` cross-session | Claude Code has no cross-session atomic file lock; prefer a tracker, with file claims only as fallback |
| `isolated-workspace` | `git worktree` (`EnterWorktree`) or subagent `isolation: worktree` | available | Isolates concurrent writers |

## Implementing Evidence Capture

- Execute local, affected, Phase, and Goal commands through Bash and read the real exit code and output.
- Use a `PostToolUse` hook matching test and build commands to append command, exit code, revision, output summary, and time to an evidence log such as `plans/logs/evidence.jsonl`. The user owns the hook configuration; the Agent does not rewrite it.
- Bind the record to `git rev-parse HEAD` plus a diff identifier from `git status --porcelain`.
- Rerun critical Goal gates at the same revision through `code-review`, a fresh-context subagent, or CI to reach A2. Record `captured_by` and replay origin in the checkpoint.
- Reference protected external hard-gate results as A3; never present local Bash as a hard gate.

## Implementing Blocking Permission

- Configure deny rules in `.claude/settings.json` for production commands, real-data writes, `git reset --hard`, force push, migrations, releases, and similar operations. Route guarded actions through deny rules or blocking `PreToolUse` hooks.
- Treat any guarded action not blocked by the permission system as `blocking_permission: human`, forbid auto, and consolidate a question for the user.

## Atomic Claim and Concurrency

- Within one session, let the main session dispatch subagents and serve as the single integrator. Run cross-agent regression after integration.
- Across sessions or people, prefer issue-tracker task claims. Fall back to the file claim in `generic.md` only when no tracker exists.
- Isolate concurrent writers with worktrees and let one integrator merge.

## Capability Negotiation Example

```yaml
capabilities:
  evidence_capture: tool        # Bash + PostToolUse hook -> A1
  atomic_claim: harness         # one in-session scheduler; tracker across sessions
  blocking_permission: harness  # local deny/hook; human for production
  independent_verify: available # code-review / subagent / CI -> A2
  isolated_workspace: available # worktree
```

This supports `project + auto + standard`. Guarded Auto still requires confirmed blocking and recovery paths for production and data operations.
