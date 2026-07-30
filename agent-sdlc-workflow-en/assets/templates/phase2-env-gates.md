# Template 2: Environment, Capabilities, and Complete Feedback Loop

> Turn the engineering disciplines adopted in the constitution into commands, capabilities, and evidence the Agent can execute independently. This stage may create a minimal skeleton, tests, or tracer bullet.
> See `references/evidence-assurance.md` for assurance and gate classes, and `references/capability-contract.md` for capabilities.

## Capability Negotiation (`RULE-AUT-001`)

Record capabilities tested in this project. The Agent inspects the Harness, tracker, CI, and permissions before reaching a conclusion.

```yaml
capabilities:
  evidence_capture: self | tool | independent | enforced
  atomic_claim: harness | tracker | file | none
  blocking_permission: harness | human | none
  independent_verify: available | unavailable
  isolated_workspace: available | unavailable
binding: references/bindings/<harness>.md   # use generic.md and degrade when none matches
```

When no binding matches, use `references/bindings/generic.md` and degrade under `RULE-AUT-001`: no machine evidence capture means no Project Auto; guarded work without blocking permission cannot run in auto.

## Automated Feedback Commands

| Loop | Command | When to use | Pass criterion | Gate type | Assurance ceiling | Measured duration |
|---|---|---|---|---|---|---|
| Local check | | After each coherent change | | evidence | | |
| Affected regression | | Task or batch completion | | evidence | | |
| Relevant integration / contract | | Phase exit | | evidence | | |
| Critical-path E2E | | Phase exit or risk trigger | | evidence | | |
| Complete / release gate | | Goal completion, or earlier when needed | | evidence/hard | | |
| Build / package | | At Phase or Goal when needed | | evidence | | |
| Local run / deploy | | Canary and acceptance | | evidence | | |

- Gate types: hard means externally enforced A3; evidence means executable with retained A0-A2 evidence; judgment means human J0/J1. Advisory recommendations are not gates.
- For web projects, prefer demonstrating that Playwright covers the critical path. For non-web projects, choose an equivalent acceptance check at the user or system boundary.
- Follow `RULE-VAL-001`. Escalate for shared contracts, schema, permissions, security, dependencies, global configuration, concurrency, migrations, infrastructure, or when a local failure reveals a larger impact surface. See `references/core-rules.md`.
- Evidence reuse must satisfy `RULE-EVD-003`: revision and input binding, unchanged gate definition, and accessible artifacts. A command is a reproduction recipe, not proof that this execution passed (`RULE-EVD-002`).

## Minimum Goal Assurance (`RULE-GOAL-001`)

| Scenario | Project requirement |
|---|---|
| project + standard + auto | Critical evidence gates >= A1 and `evidence_capture >= tool` |
| guarded critical action | >= A2 plus blocking permission and a recovery gate |
| hard gate | A3 by reference to an externally enforced result |
| human experience or business acceptance | J1 |

## Collaboration and Decision Loop

- [ ] `AGENTS.md` contains common commands, a directory map, project-specific prohibited areas, and the managed rules block.
- [ ] The chosen test-first method is executable.
- [ ] The independent reviewer and trigger are explicit.
- [ ] The ADR template is available and the Agent proposes a recommendation, alternatives, and rationale first.
- [ ] Failure output is sufficient for autonomous diagnosis.
- [ ] Guarded operations have a recovery or compensation path (`RULE-REC-001`).

## Project-Specific Risks

- Security / sensitive data: __
- API / data / migration compatibility: __
- Performance or cost budget: __
- Deployment, monitoring, and recovery: __

## Feedback-Loop Dry Run

Execute a minimal engineering canary: a skeleton, probe, or thin tracer bullet that proves the toolchain loop without prematurely implementing product functionality.

```text
Read spec/AC -> establish failing or baseline evidence -> implement -> local verification
-> affected regression -> independent review -> local run/deploy
-> critical-path demonstration with assurance and captured_by -> checkpoint
```

Record human intervention points. Before stage 3, eliminate interventions that reasonable defaults, documentation, or automation can remove.

## Exit Gates

- [ ] Every adopted engineering practice has an executable method; adjustments and N/A decisions have reasons.
- [ ] Capability negotiation is complete and a binding is selected; capability degradation is recorded when no binding matches.
- [ ] Local, affected, Phase, and final gate commands are executable and labeled with gate type and assurance ceiling; the canary uses the minimum sufficient combination.
- [ ] The minimal engineering canary completed the whole loop.
- [ ] The Agent does not need a person to run commands or explain ordinary failures.
- [ ] For Auto-ready, `evidence_capture` is at least tool (A1); guarded work also has blocking permission and a recovery gate.
