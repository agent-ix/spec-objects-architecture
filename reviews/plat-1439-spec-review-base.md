---
id: SR-028
title: "Spec review (base) - PLAT-1439 FR-013 connection carries data_classification (PR #49)"
type: SpecReview
analysis: base
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-013-connection-carries-data-classification.md, spec/functional/FR-007-systems-model-kinds.md, spec/functional/index.md"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-013", type: references}
  - {target: "ix://agent-ix/spec-objects-architecture/FR-007", type: references}
---
# SR-028: Spec review (base) - FR-013 (PR #49)

## Summary

Ticket: PLAT-1439. Base checklist over the new FR-013 (Description, Inputs,
Outputs, Behavior, Engine impact, Out of scope, AC-1 to AC-8, Dependencies),
the FR-007 Behavior line and AC-5, and the index line. The review set is a
subset: base, dependency (SR-029) and EARS conformance (SR-030). Engine claims
were checked against quire-rs `origin/main`: `src/corpus/validate.rs`
(`validate_edge_targets`), `src/corpus/required_relations.rs`,
`src/corpus/relation_report.rs`, and specs FR-040 (CR-002), FR-058 and FR-084.

Clean on this pass:

- `carries` is declared once, in spec-artifacts-iso (`category: dataflow`),
  and FR-013 reuses it without redeclaring it. AC-7 pins that.
- Edge direction (connection to classification), `Connection.json` unchanged,
  and `fields` still forbidden: these agree in FR-007, FR-013 and AC-7.
- The `required_relations` entry has the same shape as the FR-010 entries.
  The check token routes as `trace:connection-without-classification`, and
  `grammar_severity` `"off"` suppresses it, as `trace:unassigned-class` does
  (AC-3, AC-4, AC-8).
- The confidentiality `level` is not extracted. The security manifest
  extracts `properties` as a whole `section_body`, so "the report contains no
  `level`" is accurate.
- Out of scope (M2 denials, PLAT-1532 crossing edge, PLAT-1657, M3, any
  derivation) matches the ticket. PLAT-1533 and PLAT-1532 are linked.
- No paywalled standard is named or quoted. No compatibility layer.

## Verdict

**FAIL.** One high finding and three medium. The relations-report criterion
asks for output the engine does not produce, which contradicts the stated "no
quire-rs change", and one AC cannot fail under the Strict posture.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | high | FR-013-AC-5 requires `quire relations --json` to list each carried classification with its `regulated_categories`. The FR-084 report cannot carry that. `RowDocument` and `LinkedEntry::Resolved` serialize only `id`, `path`, `archetype`, `repo`, `verification`, `criteria`, `verb`, `resolution` and `realized_criteria`, with no target frontmatter value, and no FR-084 AC asks for one. So AC-5 cannot pass without a quire-rs change, and the "Engine impact: No quire-rs change is expected" section is wrong as stated. PLAT-1439 AC 3 asks the spec to say whether a change is needed. Fix: state that FR-084 needs a change (name the FR, for example a carried field on `linked` entries) and route it to PLAT-1441, or drop `regulated_categories` from AC-5. | FR-013-AC-5; FR-013 Engine impact; quire-rs src/corpus/relation_report.rs:121-136; quire-rs FR-084 | missing-requirement |
| FND-002 | medium | FR-013-AC-5 and the Behavior line "SHALL list, per classification, the connections that carry it" ask for a per-classification view. No declared relation produces one. FR-084 makes rows only for the obliged `from` documents of declared relations, and the only relation FR-013 declares is `from: connection`. A reverse view needs a second `required_relations` entry (`from: data_classification`, `edges: [carries]`, `direction: incoming`). That entry brings its own check token, which would also need a default of `off`. Fix: declare that entry and its severity, or drop the per-classification clause. | FR-013-AC-5; FR-013 Behavior; quire-rs FR-084 | missing-requirement |
| FND-003 | medium | FR-013-AC-1 requires "no `disallowed-edge-type` or `disallowed-edge-target` **warning**". Under quire-rs FR-040 CR-002 (PLAT-1689), `disallowed-edge-target` is posture-routed: an error under `Strict` (this module's `compatibility_posture`), a warning under `Okf`. A test that follows AC-1 literally passes even when the edge is rejected as an error. Fix: say "no `disallowed-edge-type` or `disallowed-edge-target` finding at any severity". | FR-013-AC-1; quire-rs FR-040 CR-002; src/corpus/validate.rs | wrong-requirement |
| FND-004 | medium | The Behavior line "Quire SHALL reject a `carries` edge from a connection to anything other than a `data_classification`" is unconditional, and The edge section allows the target to be an `ix://` uri. quire-rs FR-040 skips the Tier-2 kind check for cross-repo `ix://` targets, and `validate.rs` skips `dangling-reference` for a target under another authority. So `carries` to an `ix://` part in another repo is neither rejected nor reported as dangling. Fix: limit the rejection and the dangling clause to targets in the loaded bundle, and state that cross-repo targets are not kind-checked. | FR-013 Behavior; FR-013-AC-2; quire-rs FR-040 | wrong-requirement |
