---
id: SR-033
title: "Spec review (base) - PLAT-1441 FR-013 architecture report selection (PR #50)"
type: SpecReview
analysis: base
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-013-connection-carries-data-classification.md (origin/main...62fe79c, PR #50)"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-013", type: references}
---
# SR-033: Spec review (base) - FR-013 report selection (PR #50)

## Summary

Ticket: PLAT-1441. Base checklist over the whole of FR-013 after the change. The review set is a
subset: base (this file), dependency (SR-034) and EARS conformance (SR-035). Checked against quire-rs
PR #688 (OPEN) FR-058 and FR-084, spec-objects-security FR-023 and `DataClassification.json` on
`main`.

Clean on this pass:

- Both Outputs bullets and the Behavior line select exactly `[regulatedCategories]`. That is the
  record key FR-023 defines (frontmatter `regulated_categories`, record `regulatedCategories`).
- The selection is module-declared, and FR-013 puts no category name in the engine. This matches
  FR-058 ("The engine knows no key name") and FR-084-AC-29.
- The forward entry is `from: connection`, and `Connection.json` has no `regulatedCategories`.
  FR-058-AC-36 accepts a key that only one endpoint archetype declares, so the entry loads once
  FR-023 adds the key to `DataClassification.json`.
- Both views carry the categories: the forward view on the classification's `linked` entry, and
  the reverse view on the obliged `document`. This matches FR-084.
- AC-7 and the queue `carries` scoping are unchanged. No compatibility layer. No paywalled
  standard.

## Verdict

**FAIL.** Three medium findings and one low finding. The new presence SHALL is falsified by
FR-084's validation-failure omission rule. The unchanged Engine impact section and one older
Behavior line now contradict the new lines.

## Findings

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-001 | medium | The Behavior line "the relation report SHALL contain `regulatedCategories` on the document and linked entries when the target has it" is false under FR-084 (#688). FR-084 omits `record` when record validation fails (`semantic.record-invalid` or `semantic.duplicate-record-key`) or when the archetype has no resolved `data_schema` (FR-084-AC-24). So a classification that states `regulatedCategories: [health]` but has an invalid `level` has no categories in the report. AC-5's "Where the classification's record has `regulatedCategories`" inherits this. "The target" is also wrong for the reverse view, where the classification is the obliged document. Fix: "when the entry's document has a valid composed record that states it (quire-rs FR-084)". | spec/functional/FR-013-connection-carries-data-classification.md:83-84,130 |
| FND-002 | medium | Engine impact was not updated. It says "The edge, both relations and both `off` keys need no engine change". It also says the FR-084 change is "a carried-field entry on `linked` rows that reads `regulated_categories` from the target". The amended Behavior needs FR-058's new `record_keys` key, which is validated at load (FR-058-AC-36), and FR-084's `record` on both `document` and `linked` entries, keyed `regulatedCategories`. Fix: name FR-058 `record_keys` and FR-084 `record` as the engine change routed through PLAT-1441, and drop the `linked`-only, snake_case description. | spec/functional/FR-013-connection-carries-data-classification.md:105-113 |
| FND-003 | medium | The older Behavior line still says `quire relations --json` SHALL list each `carries` target "together with each target's `regulated_categories`". The report key is the record key `regulatedCategories`, which AC-5 and the new lines now use; `regulated_categories` is the frontmatter key and never appears in the report. Two SHALLs name different keys for one output, so a test written from line 95 fails against the engine. Fix: `regulatedCategories`. | spec/functional/FR-013-connection-carries-data-classification.md:94-96 |
| FND-004 | low | The no-`level` rationale is now wrong and unneeded. Both the Behavior line and Engine impact say `level` is excluded because it "is a `## Properties` table row that the engine does not extract". `DataClassification.json` declares `level` as a record property, and the module enables `record-sections`, so the record can hold `level`. That was the premise of the #688 base-review finding that introduced `record_keys`. The exclusion now holds by declaration. Fix: ground the SHALL NOT in `record_keys` ("`level` is not in `record_keys`"), and delete the extraction claim. | spec/functional/FR-013-connection-carries-data-classification.md:98-99,112-113 |
