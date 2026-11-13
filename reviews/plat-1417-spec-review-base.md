---
id: SR-019
title: "Spec review (base) of FR-010 design-realization edge (PR #44)"
type: SpecReview
analysis: base
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-010-design-realization-edge.md, spec/functional/index.md"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-010", type: references}
---
# SR-019: Spec review (base) of FR-010 design-realization edge (PR #44)

## Summary

Ticket: PLAT-1417. This is a base checklist review of `git diff origin/main...HEAD` at f47d7b6.
It covers the new FR-010 (Description, Inputs, Outputs, Behavior, AC-1 to AC-8, CON-1) and its
`spec/functional/index.md` entry. I checked it against quire-rs FR-086 and the FR-058 CR-416
amendment (quire-rs PR #668, head 8f9a5b9), FR-084, FR-085, FR-041, quire-cli FR-041 (PR #187),
the installed spec-artifacts-iso and spec-artifacts-process manifests, and the quire-rs engine
source. The review set is subset: base, dependency and ears-conformance. No AssuranceProfile
exists in the repo.

These parts are clean:

- The relation names `fr-has-design-element` and `nfr-has-design-element` match the FR-086 example.
  The `design_relations` order and the `direction: incoming` and `to` semantics match FR-058 and
  FR-086. The `covered`/`uncovered`/`linked`/`kind_mismatch`/`dangling` vocabulary in AC-4 to AC-7
  matches FR-084, FR-085 and FR-086-AC-1/5/6/7. AC-5 matches the FR-058 CR-416 counting rule
  (a pair authored both ways counts once).
- The existing `realizes` verb is untouched. It is declared in spec-artifacts-iso
  (`Realizes an enterprise capability/intent`) and used here only as `realizes: [business-intent]`.
  The new verb collides with no `edge_types` key or relation name in any installed module. The
  `traceability` category is a valid edge category.
- The ADR claim is correct against the code. `validate_edge_targets` skips a verb that is absent
  from the source's resolved vocabulary, and FR-041-AC-2 admits an inverse label. So the only
  ADR-side warning is `disallowed-edge-type`, and the known authoring gap is PLAT-1680.
- `allowed_links` with `["*"]` is a supported form (quire-rs FR-040-AC-4/6).
- There is no compatibility layer, no hash/digest/pin/tracking record and no quoted standard text.
- `quire validate` passes on FR-010 with no grammar warnings.
- There is no id collision with PR #45 (FR-012). Both PRs append one line after the FR-009 line in
  `spec/functional/index.md`, so the second merge needs a trivial rebase. The FR-010-then-FR-012
  order is correct.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
| --- | --- | --- | --- | --- |
| FND-001 | medium | FR-010 adds 8 ACs and CON-1, but `spec/tests.md` has no Test Matrix row and no TC for any of them, and the `spec/spec.md` FR roster (which enumerates FR-001 to FR-009) is not updated. Every prior FR PR in this repo updated both. | spec/tests.md:65-77, spec/spec.md:144-150, FR-010-AC-1..8 | correct-requirement-no-evidence |
| FND-002 | medium | FR-010 does not say what happens in a corpus that loads this module without the modules that declare `FR`/`NFR` (spec-artifacts-iso) or `ADR` (spec-artifacts-process). quire-rs `check_declaration_is_live` checks both `from` and every `to` kind (FR-058-AC-11). Each relation then emits `trace:undeclared-relation-vocabulary` in such a corpus, for example an architecture repo with no ADR module and no ADR document. No AC pins that this is the intended outcome. | FR-010 Behavior bullet 2, quire-rs src/corpus/required_relations.rs:102-141 | missing-requirement |
| FND-003 | low | AC-1 asserts "`realizes` is unchanged", but this module declares no `realizes` edge type. The verb lives in spec-artifacts-iso, and this manifest only uses it in two `allowed_links` entries. The AC does not say what is compared, so the check is either vacuous or undefined. | FR-010-AC-1, manifest.yaml:66,189 | wrong-requirement |
| FND-004 | low | `realizes_requirement: ["*"]` leaves the requirement end unconstrained. A part that authors the verb toward a port or interface (a document with an `object:`) draws no `disallowed-edge-target` warning. Narrowing to the requirement kinds would warn on a mis-aimed edge. The spec states the wildcard without a rationale. | FR-010 Outputs bullet 2, quire-rs src/corpus/validate.rs:399-466 | wrong-requirement |

## Verdict

**CONDITIONAL.** No high findings, two medium. The FR-010 design agrees with quire-rs FR-086, FR-058
CR-416, FR-084, FR-085 and quire-cli FR-041 on names, fields, order and semantics. FND-001 is a
coverage gap, because the Test Matrix does not record FR-010. FND-002 is an unspecified edge
that produces a real advisory finding.
