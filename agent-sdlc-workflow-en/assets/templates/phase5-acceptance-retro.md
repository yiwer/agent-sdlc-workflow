# Template 5: Acceptance and Learning

> See `references/evidence-assurance.md` for assurance levels and `RULE-STATE-001` in `references/core-rules.md` for lifecycle semantics.

## AC Acceptance

| AC | Result | Assurance | Evidence: revision + source + pointer | Unfinished-item disposition |
|---|---|---|---|---|
| AC-1 | pass/fail/deferred | A1/A2/A3/J1 | __ | __ |

- `deferred` must come from an approved spec delta and cannot bypass a promised AC.
- Only an externally enforced A3 result satisfies a hard gate. Human experience or business acceptance requires J1 that identifies the person, time, object, and conclusion.

## Lifecycle State Report (`RULE-STATE-001`)

Final state: `planned / implementation_complete / automated_verified / human_acceptance_pending / accepted / released / closed`, with auxiliary `auto_paused / rejected / deferred`.

> Example: implementation and automated gates are complete, but AC-5 human experience approval is pending. Report `human_acceptance_pending`, not `accepted`, while still stating that implementation and automated verification are complete.

## Consistency Check

- [ ] A complete or release-level gate passed after the final code change, or equivalent or stronger fresh green evidence is reused under `RULE-EVD-003`.
- [ ] Critical-path E2E and affected regression passed without mechanically repeating unrelated suites (`RULE-VAL-001`).
- [ ] Every evidence gate meets the Goal minimum assurance under `RULE-GOAL-001`; Agent-supplied fields say self-reported under `RULE-EVD-002`.
- [ ] A3 satisfies every hard gate; text does not impersonate a hard boundary (`RULE-HARD-001`).
- [ ] The spec, implementation, and tests describe the same behavior.
- [ ] Material architecture decisions have ADRs and ordinary implementation details are not over-documented (`RULE-MIN-001`).
- [ ] When data or external side effects exist, their recovery is reported separately from source rollback (`RULE-REC-001`).
- [ ] Every unfinished item is explicitly deferred, degraded, or rejected.

## Retrospective

1. Which assumption was disproved latest?
2. Which verification loop created the most value, and which only created waiting?
3. Which full regression ran too early or too late, and how can feedback be shorter next time?
4. Which user interruption could model judgment or existing evidence have avoided?
5. Did re-anchoring catch drift in time? Which assurance level was over- or underestimated?
6. What lesson is reusable enough to automate or add to a long-lived rule?

Retain only reusable knowledge. When nothing new was learned, record "no change" instead of manufacturing constitution or template updates.

## Closure Gates

- [ ] Every promised AC has a result, assurance level, and locatable evidence.
- [ ] The final complete or release-level gate passed or reused an equivalent fresh green result.
- [ ] Lifecycle state is reported honestly; no pending judgment gate is presented as accepted.
- [ ] No goal drift or high-risk issue remains without a disposition.
- [ ] NOTES records the final state and recovery or follow-up entry point.
