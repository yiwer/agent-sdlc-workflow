---
name: agent-sdlc-workflow-en
description: Windows PowerShell 5.1 must read bundled files with Get-Content -Raw -Encoding UTF8. Organize software delivery with a dual-mode Agent SDLC. Use fast-track for small one-session increments and guided four-stage Project Mode for new products, long-running or cross-session work, multiple milestones, or multi-agent projects. Select delivery scale, autonomy, risk, and collaboration independently; negotiate Harness capabilities; bind A0-A3/J0-J1 evidence to revisions; and report lifecycle state honestly. Ordinary one-off fixes do not automatically trigger the full workflow.
---

# Agent SDLC

## Nature of this skill's constraints

Treat this skill as a **behavior orchestration protocol, not a hard control system** (`RULE-HARD-001`). Skill text can shape Agent behavior, but it cannot provide permission isolation, CI enforcement, branch protection, production approval, data recovery, atomic scheduling, or an independent evidence author. Delegate enforceable boundaries to the Harness, CI, permission system, and version control.

Keep these gate types distinct:

- **hard**: CI, permissions, branch protection, or deployment approval truly blocks the action; this skill only references its A3 result.
- **evidence**: the Agent can execute the gate, but must retain revision-bound raw results and label their assurance A0-A2.
- **judgment**: a person must decide an experience, business, or risk question; record J0/J1 explicitly and never replace it with self-attestation.

## Core propositions

- **Verification quality determines autonomy** (`RULE-AUT-001`): autonomy comes from available capabilities and evidence assurance, not prompt length. Reduce autonomy when capability or assurance is insufficient.
- **`Plan-ready` is not `Auto-ready`**: a plan is reviewable; long-running autonomy additionally requires a tested local feedback loop, an engineering canary, and working evidence capture.

## Choose the lightest sufficient workflow

Expose fast-track and Project Mode to users, but decide four orthogonal dimensions independently (`RULE-MODE-001`, `RULE-FAST-001`):

| Dimension | Values | Decision rule |
|---|---|---|
| Delivery scale | `fast` / `project` | One verifiable increment that fits one session -> fast; multiple releasable increments, cross-session work, or a persistent plan/DAG -> project |
| Autonomy | `copilot` / `auto` | Product semantics, risk, or verification still needs a person -> copilot; spec, plan, canary, evidence capture, and recovery entry points are verified -> auto |
| Risk | `standard` / `guarded` | Reversible and local, with no production, real-data, or permission impact -> standard; production, real data, migration, permissions, security, paid services, or hard-to-recover actions -> guarded |
| Collaboration | `single` / `multi` | One writer -> single; two or more concurrent writers -> multi |

Do not let AC count, a request for auto, multi-agent use, or one high-risk operation determine Project Mode by itself. Those factors affect autonomy, collaboration, and risk separately. Read existing `CONSTITUTION.md`, `AGENTS.md`, `NOTES.md`, `specs/`, and `plans/` first. Reuse equivalent artifacts instead of recreating them mechanically.

## Reading order

- All bundled text files use UTF-8 without BOM. On Windows PowerShell 5.1, read them with `Get-Content -Raw -Encoding UTF8`.
- Read this file for routing and four-stage orchestration.
- Read `references/core-rules.md` as the canonical authoring source for complete behavior rules.
- Read `references/evidence-assurance.md` for assurance levels and evidence records.
- Read `references/capability-contract.md` for capability negotiation and degradation.
- Read `references/recovery-model.md` for layered recovery.
- Read `references/bindings/<harness>.md` for platform-specific implementation. Use `generic.md` and degrade when no binding matches.

For persistent projects, run `python <skill-dir>/scripts/init_project.py <project-root> --dry-run`, then remove `--dry-run` after confirming the preview. Stages may iterate and overlap. By default, clarify the product, feedback loop, and plan across the first three stages, confirm them together, and only then switch to auto.

## Project Mode: four stages

Keep the first three stages in copilot mode: investigate, propose a draft and recommendation, then ask a person to confirm product semantics and material tradeoffs. Do not make the user fill blank templates. In stage four, treat the approved plan as one complete goal and execute continuously until all gates pass.

1. **Preparation**: read `assets/templates/phase1-spec-modeling.md`. Clarify users, scenarios, value, non-goals, assumptions, and boundaries. Probe objects, behaviors, events, relations, and rules; allow N/A only after judgment (`RULE-MIN-001`). Choose the cheapest prototype that resolves the current uncertainty. Feed findings back into the model and numbered ACs, then confirm them together.
2. **Environment**: read `phase0-constitution.md` and `phase2-env-gates.md`. Recommend an engineering baseline such as SDD, test-first work, independent review, ADRs, boundary acceptance, and a local feedback loop. Negotiate capabilities using `references/capability-contract.md`. Run a minimal canary through change -> verify -> run locally -> demonstrate.
3. **Planning**: read `phase3-phase-planning.md`. Plan end-to-end verifiable Phase increments and front-load risk. Refine task cards with ACs, dependencies, local checks, escalation conditions, and completion signals. Define automated exit gates and an acyclic DAG. Declare `Plan-ready` or `Auto-ready`; **Auto-ready requires `evidence_capture` of at least `tool` (A1)**.
4. **Goal Execution**: read `phase4-execution-protocol.md` and `phase5-acceptance-retro.md`. Execute Todo items, ACs, and gates as one continuous goal. Expand regression scope by layer. Re-anchor after every Phase gate (`RULE-ANCHOR-001`), enter `auto_paused` on a circuit breaker (`RULE-BREAK-001`), keep recovery categories separate (`RULE-REC-001`), and report lifecycle state honestly (`RULE-STATE-001`).

## Verification cadence

Follow `RULE-VAL-001`: expand from local -> affected -> Phase -> Goal. Run the shortest local check after a coherent change, not the full suite after every edit. Escalate early for shared contracts, schema, permissions, security, dependencies, global configuration, concurrency, migration, infrastructure, or a widening impact surface. Reuse the latest green evidence only when inputs have not changed. See `references/core-rules.md` for full semantics and the project `CONSTITUTION.md` for concrete commands.

## When to involve the user

Under `RULE-USER-001`, consolidate a question only when the goal, non-goals, or ACs must change; new external authorization, paid services, production, or real data is required; an action is destructive, hard to recover, or out of scope; and no other safe task can continue. Let the Agent handle ordinary failures, omitted files (`RULE-SCOPE-001`), equivalent refactors, implementation choices, and first-pass diagnosis.

## Minimal persistence

Let specs record intent, ADRs record material tradeoffs, NOTES record progress, and checkpoints record results and evidence. Do not manufacture process artifacts merely to demonstrate compliance. Record "no change" when nothing reusable was learned. Fast-track creates no workflow files; the final conversational summary is the A0 report (`RULE-MIN-001`).

## Completion criteria

Report the lifecycle state truthfully under `RULE-STATE-001`. Collect evidence at the required assurance for every promised AC (`RULE-GOAL-001`): every AC has a locatable result, hard gates are satisfied only by A3, human acceptance is explicitly J0/J1, specs/implementation/tests/material ADRs agree, and every unfinished item has a disposition. When automated gates pass but human judgment is pending, report `automated_verified`, not `accepted`. See `assets/templates/phase5-acceptance-retro.md`.
