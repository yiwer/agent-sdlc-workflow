# Core Rules (Canonical Authoring Source)

> This file is the **single canonical authoring source** for all Agent SDLC behavior rules. `SKILL.md`, stage templates, and managed blocks in project `AGENTS.md` files are controlled projections.
> Define each rule only here. Projections retain only a stable rule ID and the short action summary needed at that location.

## Rule ID Convention

- Use `RULE-<DOMAIN>-<NUMBER>`. Never reuse an ID or change its meaning after release; assign a new ID when semantics change.
- In a projection, write a stable ID plus its local action summary, for example: `RULE-VAL-001: expand verification from local -> affected -> Phase -> Goal`.
- Content contract tests ensure that every projected ID exists here and that the managed subset is nonempty and renderable by `init_project.py`.

---

## Runtime Core Subset (Managed Projection)

> `init_project.py` renders these entries into the managed block of a project `AGENTS.md` so they survive sessions and tools.
> This is a projection, not a second rule source. Match full semantics below by rule ID.

- RULE-AUT-001: Verification quality determines autonomy. Reduce autonomy or concurrency when capability or evidence is insufficient; do not disguise missing capability with prose.
- RULE-VAL-001: Expand verification from local -> affected -> Phase -> Goal. Reuse the latest green evidence when inputs have not changed.
- RULE-EVD-001: Classify automated evidence as A0 self-reported / A1 tool-captured / A2 independently-replayed / A3 externally-enforced, and human judgment as J1 approved / J0 pending-or-rejected.
- RULE-USER-001: Consolidate a user question only when product semantics must change, new external authorization/payment/production/real data is required, or an action is destructive and hard to recover, and no safe work can continue.
- RULE-SCOPE-001: Impact areas support estimation and write-conflict coordination; they are not permission allowlists. Edit omitted files as needed and let Git provide the file-level diff.
- RULE-STATE-001: Report lifecycle state honestly. When automated gates pass but human judgment is pending, report automated_verified, not accepted.
- RULE-FAST-001: Fast-track creates no workflow artifacts. Higher risk changes only the guarded dimension; it does not inflate the work into full Project Mode.

---

## Complete Rule Catalog

### Governance and Autonomy

- **RULE-AUT-001 Verification quality determines autonomy**: Autonomy is determined by available capabilities and evidence assurance, not prompt length. Reduce autonomy or concurrency when capabilities or assurance are insufficient; do not use more prose to pretend that missing capability exists. Projections: SKILL.md, managed block.
- **RULE-MODE-001 Orthogonal four-dimension decision**: Decide delivery scale (`fast/project`), autonomy (`copilot/auto`), risk (`standard/guarded`), and collaboration (`single/multi`) independently. AC count, a user request for auto, multi-agent use, or one high-risk operation **does not determine Project Mode by itself**; those factors affect autonomy, collaboration, and risk separately. The model still requires LLM judgment, but decomposes one broad judgment into narrower, testable questions. Projections: SKILL.md, phase3.
- **RULE-FAST-001 Zero-persistence fast-track**: Use fast-track when one verifiable increment fits one session and a persistent plan adds no real value. Do not require initialization or create rule snapshots, NOTES, specs, plans, or checkpoints. The final conversational summary is the A0 report. Higher risk changes only the guarded dimension and does not automatically inflate the task into full Project Mode. Projections: SKILL.md, managed block.
- **RULE-USER-001 User involvement boundary**: Consolidate a question only when the goal, non-goals, or ACs must change; new external permissions, paid services, production, or real data are needed; or an operation is destructive, hard to recover, or outside the authorized workspace, and no other safe task can continue. Let the Agent handle ordinary failures, omitted files, equivalent refactors, implementation choices, and first-pass diagnosis. Projections: SKILL.md, phase4, managed block.
- **RULE-SCOPE-001 Meaning of impact areas**: A task card's impact area supports effort estimation and multi-agent write-conflict coordination; it is not a permission allowlist. Edit omitted files when discovered and summarize material impact in the checkpoint. Git provides the file-level diff. Projections: phase3, phase4, managed block.
- **RULE-MIN-001 Minimal persistence and anti-theater**: Specs record intent, ADRs record material tradeoffs, NOTES record progress, and checkpoints record results and evidence. Do not manufacture process assets to prove compliance. Record "no change" when nothing reusable was learned. Give a reason for N/A instead of silently skipping it. Projections: SKILL.md, phase1, phase5.
- **RULE-SESSION-001 Runtime source of truth**: An initialized project must not depend on current-session memory, every machine having the same installed skill version, or a new Agent re-triggering the skill. Core runtime rules must live in the managed block of project `AGENTS.md` or a project file explicitly referenced by `AGENTS.md`. Projections: SKILL.md, init_project.py.

### Verification Cadence

- **RULE-VAL-001 Layered verification cadence**: After a coherent change, run the shortest local check rather than the full suite after every edit. At task or batch completion, run affected regressions. At Phase exit, run relevant integration tests, shared contracts, and critical-path E2E. At Goal completion, ensure complete or release-level green evidence exists after the last code change; reuse a covering higher-level result. Escalate early for changes to shared contracts, schema, permissions, security, dependencies, global configuration, concurrency, migration, or infrastructure, or when a local failure reveals a wider impact surface. Reuse the latest green evidence when code and verification inputs have not changed. When the same failure yields no new information, change the hypothesis before repeating it. Projections: SKILL.md, phase0, phase2, phase4, managed block.

### Evidence and Gates

- **RULE-EVD-001 Evidence assurance levels**: `A0 self-reported` (Agent prose or manually transcribed result) / `A1 tool-captured` (Harness automatically records execution, revision, exit, and output) / `A2 independently-replayed` (a fresh context, independent verifier, or CI reruns at the same revision) / `A3 externally-enforced` (protected CI, permissions, branch protection, or deployment systems truly block). Record human judgment separately as `J1 human-approved` / `J0 pending-or-rejected`. See `evidence-assurance.md`. Projections: phase2, checkpoint, managed block.
- **RULE-EVD-002 Self-entry does not upgrade assurance**: Agent-supplied fields must say `provenance: self-reported`. A0 must not impersonate A1. Machine-captured local commands are usually A1, not A2 or A3. Projections: checkpoint, phase2, managed block.
- **RULE-EVD-003 Evidence binding and freshness**: Bind evidence to a commit or dirty diff and to verification inputs. Downgrade or reject stale results after revisions or inputs change. Reuse requires proof that intervening changes do not affect the gate's code, configuration, test inputs, or environment; the gate definition is unchanged; and the artifact remains accessible. Projections: checkpoint, phase4, phase5.
- **RULE-HARD-001 Hard-gate exclusivity**: Only A3 externally enforced results can satisfy hard gates. Skill text must not present permission isolation, CI blocking, branch protection, or deployment approval as enforced; it may only reference their results. Projections: SKILL.md, phase2, phase5.
- **RULE-GOAL-001 Minimum Goal assurance**: Fast + standard may use A0, but the final report must explicitly say self-reported. Project + standard + auto requires at least A1 for critical evidence gates. Guarded critical actions require A2 plus blocking permission. Hard gates require A3. Human experience or business acceptance requires J1. Projections: phase2, phase5.

### Lifecycle State

- **RULE-STATE-001 Honest lifecycle reporting**: Use `planned -> implementation_complete -> automated_verified -> human_acceptance_pending -> accepted -> released -> closed`, with auxiliary states `auto_paused / rejected / deferred`. When automated gates pass and a human gate is pending, report `automated_verified`, never `accepted`. Do not hide completed implementation or automated verification because human acceptance is pending. `deferred` must come from an approved spec delta and cannot bypass an AC. A circuit breaker enters `auto_paused` without erasing still-valid completed increments. Projections: phase4, phase5, managed block.

### Re-anchoring and Circuit Breaking

- **RULE-ANCHOR-001 Re-anchor**: Compare in this order: current approved spec -> approved spec deltas -> current goal/ACs/non-goals -> original user intent. Do not mistake approved requirement evolution for drift. Trigger at Phase boundaries, context compaction, new-session recovery, Agent handoff, spec-delta merge, material impact expansion, and before final acceptance. When drift is suspected, analyze impact and make reversible corrections first. Submit a spec delta or ask the user only when product semantics must change. Re-anchoring must not become a new high-frequency interruption. Projections: phase4, phase5.
- **RULE-BREAK-001 Circuit breaker**: Enter `auto_paused` when any of these occurs: the same failure recurs without a new hypothesis or evidence; independent hypotheses are disproved up to the configured exploration limit; an instantiated budget is being consumed far faster than verified progress; continuing requires undoing multiple verified tasks; repeated re-anchors find the same goal deviation; or work enters an unauthorized guarded scope. Preserve still-valid increments and provide recovery entry points. Do not invent "half the budget" metrics when the platform exposes no budget. Projection: phase4.

### Recovery

- **RULE-REC-001 Separate three recovery classes**: Model and report source recovery (files, commits, configuration), data recovery (schema, migrations, data writes), and external-side-effect recovery (cloud resources, releases, APIs, messages, traffic) separately. Do not create tags, branches, or commits by default. Do not perform destructive resets or overwrite uncommitted work from users or other Agents. Git recovery must not impersonate data or production recovery. Guarded Auto-ready requires the corresponding recovery or compensation path. See `recovery-model.md`. Projections: phase4, phase5.

### Concurrency and Permissions

- **RULE-CLAIM-001 Concurrency control**: The primary multi-agent path is Harness task system or issue tracker atomic claim -> branch/worktree/sandbox isolation -> one integrator -> post-merge cross-agent regression. Without `atomic-claim`, prefer one writer or coordinator-serialized dispatch, remain copilot, and do not claim multi-agent Auto-ready. File claims are an independent fallback binding and are not created by default or detailed in core templates. NOTES is a broadcast board, never a lock. Projection: phase4.
- **RULE-GUARD-001 Guarded permissions**: Do not run guarded work in auto mode without real `blocking-permission`. Text rules cannot replace actual permission enforcement. Projections: phase2, phase4.
