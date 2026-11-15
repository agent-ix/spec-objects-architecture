---
id: SR-032
title: "Gap analysis - PLAT-1441 FR-013 architecture report selection (PR #50)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-013-connection-carries-data-classification.md, spec_objects_architecture/manifest.yaml (origin/main...62fe79c, PR #50)"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-013", type: references}
---
# SR-032: Gap analysis - FR-013 report selection (PR #50)

## Summary

Ticket: PLAT-1441. Planless. Plan completion: not assessed. `quoin matrix` could not run (the
permission layer required approval), so this is a manual check of acceptance criteria against
Behavior and against the implementing ticket.

- No production code changed. The manifest has no `carries` relation yet
  (`spec_objects_architecture/manifest.yaml:58-72`), and `queue` still declares
  `carries: [data_schema, event]` (line 184). So queue behaviour is unchanged.
- FR-013-AC-5 and AC-8 have no tagged test. That is expected for a spec-only PR. PLAT-1440
  implements the manifest entries and their tests.
- Each new Behavior SHALL was mapped to an FR-013 criterion. Presence of `regulatedCategories`
  maps to AC-5. Exclusion of `level` and unselected keys maps to AC-5. The `record_keys` declaration
  maps to AC-8. Omission when the classification states no categories maps to nothing (FND-001).

## Verdict

**CONDITIONAL.** One medium gap: a Behavior SHALL has no criterion. One low gap: the downstream
ticket that implements these entries does not carry `record_keys`.

## Findings

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-001 | medium | The Behavior line "the relation report SHALL omit `regulatedCategories` when the target has not" has no FR-013 criterion. AC-5 asserts presence, and absence of `level`, but no fixture classification without categories. A report that emitted `"regulatedCategories": []` or `"record": {}` for it would pass every FR-013 AC. quire-rs FR-084-AC-21/23 cover the engine, not this module's declared relations. Fix: add to AC-5 "a classification whose record states no `regulatedCategories` has no `record` key in either view". | spec/functional/FR-013-connection-carries-data-classification.md:85,130 |
| FND-002 | low | PLAT-1440, which implements the two `required_relations` entries, gives their shape in Design notes without `record_keys`. Its AC 6 asserts the connection/classification pairs but not `regulatedCategories` or the absence of `level`. An implementer following the ticket would fail FR-013-AC-8 as amended here. Fix (owner or code lead, not this PR): add `record_keys: [regulatedCategories]` to both relations in PLAT-1440, and add the AC-5 assertions to its AC 6. FR-013 is the authority. | PLAT-1440; FR-013-AC-5; FR-013-AC-8 |

## Disposition pass 1

| FND | Outcome | Reason |
| --- | --- | --- |
| FND-001 | fixed | FR-013-AC-9 covers omission when FR-084 omits the record or selected key. |
| FND-002 | fixed | PLAT-1440 now includes exact `record_keys`, selected-key behavior, no `level`, and omission cases. |

Pass-1 verdict: approved; no new findings.
