---
id: SR-039
title: "Spec review (integrity) - PLAT-1533 FR-015 data_sink and delivers_to (PR #51)"
type: SpecReview
analysis: integrity
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-015-data-sink.md, spec/functional/index.md (origin/main...10414f7 review pass, d0927cb disposition pass 1, 2280b19 disposition pass 2, PR #51)"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-015", type: references}
---
# SR-039: Spec review (integrity) - FR-015 data_sink (PR #51)

## Summary

Ticket: PLAT-1533. Coverage of Behavior and Outputs by ACs, the index entry, frontmatter
relationships, and constraint ids FR-015-CON-1 to CON-4. Examined AC-1, AC-2 and AC-12 for the
enum, list-field and consistency clauses. The index entry is clean.

## Verdict

**FAIL at 10414f7**: one medium and one low finding. **Disposition pass 1 at d0927cb: both fixed.**
Disposition pass 1 adds one new low finding (FND-003) that the FND-001 fix introduced. **Disposition pass 2 at 2280b19: FND-003 fixed**, no new findings.

## Findings

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-001 | medium | The `region` statement fixes a code format (ISO 3166-1 alpha-2, `eu`, `eea`), but leaves open whether it is checked against the ISO list or a `^[A-Z]{2}$` pattern, and what case applies (`DE` vs `de`, beside lowercase `eu`/`eea`). Two implementers would emit different schemas. AC-2 checks only 'lists of non-empty strings', so a `region: [xx-bad]` passes every AC. State the schema form (pattern or enum, and case), and add an AC case such as `region: [Germany]` failing. | spec/functional/FR-015-data-sink.md:53,112,161 |
| FND-002 | low | Behavior line 110 requires the out-of-enum diagnostic to name the field and the value. AC-1 asserts only the field, so the value half of that SHALL has no AC. | spec/functional/FR-015-data-sink.md:110,160 |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | d0927cb: Behavior line 121 says `region` items match `^([A-Z]{2}\|eu\|eea)$`, emitted as that `pattern` in both schemas. The Keys prose says the check is by pattern alone and not against the ISO list. AC-2 adds `region: [DE, eu, eea]` validating, `[Germany]`, `[de]` and `[xx-bad]` failing, and both schemas carrying the item `pattern`. |
| FND-002 | fixed | d0927cb AC-1: "the out-of-enum diagnostics naming the field and the offending value and the missing-field diagnostic naming the field". |
| FND-003 | fixed | 2280b19 line 53 escapes both pipes inside the table cell: `^([A-Z]{2}\|eu\|eea)$`. GFM treats `\|` in a table cell, code span included, as a literal pipe, so the row has three cells and renders the full pattern. The Behavior copy (line 119) is unchanged and outside a table. |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-003 | low | The Keys-table row for `region` puts the pattern `^([A-Z]{2}\|eu\|eea)$` in a code span with unescaped pipes. In a GFM table an unescaped `\|` splits the cell even inside backticks. The row then has five cells, and the renderer shows the Values cell as a broken `^([A-Z]{2}` and drops the rest of the row. The Behavior line 121 copy, outside a table, is unaffected, so the normative text survives. Fix: escape the pipes in the table cell (`\|`), or move the pattern out of the table. | spec/functional/FR-015-data-sink.md:55 |
