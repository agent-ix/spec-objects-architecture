---
id: SR-038
title: "Spec review (EARS) - PLAT-1533 FR-015 data_sink and delivers_to (PR #51)"
type: SpecReview
analysis: ears-conformance
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-015-data-sink.md Behavior and Constraints (origin/main...10414f7 review pass, d0927cb disposition pass 1, PR #51)"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-015", type: references}
---
# SR-038: Spec review (EARS) - FR-015 data_sink (PR #51)

## Summary

Ticket: PLAT-1533. EARS conformance of the FR-015 Behavior section (lines 107-142 at 10414f7: 30
SHALL / SHALL NOT statements) and the constraints FR-015-CON-1 to CON-4. Each Behavior statement has
the module, an object type, a document, an edge or the report as its subject. CON-1 and CON-2 were
already in single-SHALL form after 10414f7.

## Verdict

**FAIL at 10414f7**: two low findings. **Disposition pass 1 at d0927cb: both fixed**, no new
findings in this method. The new d0927cb Behavior lines (the `region` pattern, the SHALL NOT for
`processor`/`audience_roles`, and the reworded facts lines) are each single-subject SHALL statements.

## Findings

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-001 | low | The module ships no `flow_rules` (line 141 and CON-4), so the Behavior load-check statement's "in this module's rules" has no referent. AC-8 means any loaded module's rules read against this module's `DataSinkFrontmatter` enums. Reword it as: 'A `flow_rules` condition in any loaded module whose `any_of` reads `kind` or `processor_agreement` of a `data_sink` ...'. | spec/functional/FR-015-data-sink.md:130 |
| FND-002 | low | CON-3 and CON-4 state facts, not obligations: they have no SHALL. 10414f7 put CON-1 and CON-2 into single-SHALL form. Use 'The module SHALL NOT compute ...' and 'The module SHALL add no engine code ...'. | spec/functional/FR-015-data-sink.md:151-152 |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | d0927cb line 140: "A `flow_rules` condition in any loaded module whose `any_of` reads `kind` or `processor_agreement` of a `data_sink` SHALL be checked at module load against these two enums". |
| FND-002 | fixed | d0927cb: CON-3 reads "The module SHALL NOT compute, fill in or rewrite a `kind`, a `processor_agreement`, a region or a `delivers_to` edge in any file." CON-4 reads "The module SHALL add no engine code, no Python rule and no hard-coded sink list, because `flow_rules` is the only new engine kind." |
