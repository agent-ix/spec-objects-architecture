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

## Dispositions

| FND | Outcome | Reason |
|---|---|---|
| FND-001 | fixed | Engine impact now states that FR-084 needs an engine and report change (a carried-field entry on `linked` rows reading `regulated_categories`) and routes it through PLAT-1441; AC-5 is gated on that change. |
| FND-002 | fixed | A reverse `required_relations` entry `classification-carried-by-connection` (`direction: incoming`, check `classification-without-connection`) is declared, its severity key is set to `off`, and Outputs, AC-3, AC-4 and AC-8 cover it. quire-rs FR-058 supports `direction: incoming`. |
| FND-003 | fixed | AC-1 now reads "finding at any severity". |
| FND-004 | fixed | The kind-check and dangling clauses are limited to targets in the loaded bundle, and cross-repository targets are stated as not kind-checked. The new dangling wording this introduced is FND-005. |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-005 | medium | The added Behavior line says a `carries` edge to a cross-repository `ix://` target outside the loaded bundle is "not reported as dangling ... quire-rs FR-040 skips both checks for it", and AC-2 now requires such an edge to yield "neither". quire-rs FR-040 says the opposite ("cross-repo `ix://` targets resolve as dangling", so Tier-2 checks only within one bundle). `validate.rs` suppresses `dangling-reference` for an unloaded authority only when the source's member declares an identity (bundle package, FR-085 / FR-038); "without one, every miss stays dangling". So a single-member corpus with no declared identity reports `dangling-reference` for the edge and AC-2's last clause fails. Fix: cite FR-085, not FR-040, for the dangling skip and condition it on the member declaring its identity, or drop the dangling half of the cross-repo clause and AC-2's "yields neither". | FR-013 Behavior; FR-013-AC-2; quire-rs FR-040; quire-rs FR-085; quire-rs src/corpus/validate.rs:414-433 | wrong-requirement |

## Dispositions (round 2, a61972d)

| FND | Outcome | Reason |
|---|---|---|
| FND-005 | fixed | a61972d deletes the cross-repository Behavior line and AC-2's "yields neither" sentence (the second fix option). The kind-check line stays limited to targets in the loaded bundle. That still holds: quire-rs `validate_edge_targets` runs only on edges with a resolved `target_slot`, so a target outside the bundle never reaches it. No text in FR-013 now claims an engine skip for cross-repository targets. |

## New findings (round 2)

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-006 | low | Removing the cross-repo line leaves the dangling Behavior line unconditional: "A `carries` edge to an id that no document in the loaded bundle has SHALL yield `dangling-reference`". The edge section (line 33) still allows the target to be an `ix://` uri. In quire-rs `validate.rs` (validate_view_findings, reference-resolution loop), an `ix://` target under an authority that no loaded member declares is treated as `cross_repo` and draws no `dangling-reference` when the source's member declares an identity (FR-085). So a connection in a repo with a declared package that carries `ix://agent-ix/other-repo/CLASS-X` draws no finding, and the SHALL is false for it. AC-2 is unaffected because a fixture can use a bare id. This is what remains of FND-004's dangling half. Fix: limit the line to a bare id or an `ix://` uri under a loaded member's authority, or add "unless the target is under an unloaded authority and the source member declares its identity (quire-rs FR-085)". | FR-013 Behavior (lines 69-70); FR-013 The edge (line 33); quire-rs FR-085; quire-rs src/corpus/validate.rs | wrong-requirement |

**Round-2 verdict: CONDITIONAL.** FND-001 to FND-005 are closed. One low finding (FND-006) is open. It does not affect any AC.

## Dispositions (round 3, f5970b9)

f5970b9 changes only the FR-013 dangling Behavior line. Checked against quire-rs `origin/main`
`src/corpus/validate.rs` (`validate_view_findings`, reference-resolution loop) and FR-085.

| FND | Outcome | Reason |
|---|---|---|
| FND-006 | fixed | The line now requires `dangling-reference` only for a bare id, or an `ix://` target under a loaded member's authority, that no loaded document has. It adds that an `ix://` target under an authority no loaded member declares SHALL NOT yield `dangling-reference` when the source member declares its identity (FR-085). This matches the engine: `cross_repo` is true only when `edge.authorities` (unloaded authorities only) is non-empty and `member_identity(member_of(source))` is `Some`. It also matches FR-085-AC-17. The sentence does not cover an unloaded authority when the member has no identity, and the engine reports that case as dangling. Leaving it unstated is not a contradiction. AC-2 still uses a bare id and still holds. |

Considered and not raised: CR-418 (FR-038). A dangling edge whose target is an acceptance-criterion id
minted by exactly one document draws no `dangling-reference`. The engine reads that edge as an edge to
the minting document, so the target is held by a document and the line is not falsified. This is a
general engine rule for every verb, so FR-013 does not need to restate it.

## New findings (round 3)

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-007 | medium | FR-013-AC-7 requires that "the manifest declares `carries` neither in `edge_types` nor for any kind other than `connection`". The manifest already declares `carries: [data_schema, event]` on `queue` (`spec_objects_architecture/manifest.yaml:184`), and that predates this PR. So a test that follows AC-7 literally fails on `queue` today. PLAT-1440 cannot meet it without removing an existing edge. FR-007-AC-5 says it correctly: it limits the rule to the systems kinds. Rounds 1 and 2 missed this. Fix: change AC-7 to "nor for any systems kind other than `connection`", meaning the `SYSTEMS_TYPES` that TC-104 iterates. PLAT-1440 AC 8 says "every non-connection kind rejects `carries`" and needs the same scoping. | FR-013-AC-7; FR-007-AC-5; spec_objects_architecture/manifest.yaml:181-185; PLAT-1440 AC 8 | wrong-requirement |

Not run: `quire validate spec`. The permission layer in this session refused it, as it did for
`quoin`. This was a static review.

**Round-3 verdict: FAIL.** FND-001 to FND-006 are closed. FND-007 (medium) is open: an AC that the
existing manifest cannot pass. The fix is a one-word scoping change to AC-7.
