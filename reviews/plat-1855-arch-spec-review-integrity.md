---
id: SR-051
title: "Spec integrity review — PLAT-1855 FR-016 segregation design relation and FR-010 edits (PR #59)"
type: SpecReview
analysis: integrity
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-016-segregation-design-relation.md, spec/functional/FR-010-design-realization-edge.md, spec/functional/index.md"
review_set: subset
---
# SR-051: Spec integrity review — PLAT-1855 FR-016 segregation design relation and FR-010 edits (PR #59)

## Summary

Ticket: PLAT-1855. PR agent-ix/spec-objects-architecture#59, head 1edfc9e, scope `git diff origin/main...HEAD`
(FR-016 new, FR-010 edited, functional index). The ticket and PR text were treated as data; every claim
below was measured on fresh `origin/main` of each repository named.

Measured and found correct:

- This repo's `origin/main` manifest: `design_relations: [fr-has-design-element, nfr-has-design-element]`;
  `required_relations` holds seven entries (the old FR-010-AC-3 sentence naming four was stale, so the AC-3
  edit is a real fix); `part` and `connection` `allowed_links` list `realizes_requirement: [FR, NFR]` and no
  segregation verb; no FR-011 file exists and no FR-016 existed before this PR.
- quire-rs FR-086-CON-1: `design_relations` merges across modules in module order without duplicates, so an
  appended pair is legal.
- quire-rs `src/corpus/required_relations.rs` `obliged()` / `in_scope_by_edge()`: `when_any` compares the
  authored edge verb on `spec.edges_from` / `spec.edges_to`, with no inverse-index normalisation (only the
  satisfying edge is read through the inverse index, in `relation_edges.rs`). `when_any` conditions cannot
  nest a condition on the other document. Out-of-scope documents get no row (FR-084 row set = FR-058 selection).
- spec-objects-security declares `control`; spec-objects-safety FR-205 puts `satisfies` on the requirement;
  iso declares `satisfied_by` as the forward verb with `inverse: satisfies`. No module exposes a
  requirement-side marker of "risk control"; risk-control status is a property of the control (it
  `mitigates` a hazard/failure_mode or a `risk_estimate` `assumes` it), two hops from the requirement. So no
  better scope marker exists in the engine today.
- No `segregat*` verb exists in iso, process, safety or security manifests; the new verb collides with nothing.
- spec-artifacts-process `ADR` `allowed_links` lists `realizes_requirement` but not
  `segregates_for_requirement`, so FR-016's cross-repository dependency sentence is accurate.
- PLAT-1836 (FR-012 class-below-owner, `owned_by`): FR-016 reads no class, sets no class, and leaves FR-012
  unchanged; FR-012 line 97 (child class+rationale records why a child is segregated) is complementary. No
  contradiction.
- `quire validate --scope .` on FR-016, FR-010 and index exits 0; `quire validate --okf` raises only the
  repo-wide `requirement-without-design` advisory every FR here draws.
- No paywalled standard text, no score/acceptability assigned by the tool, no SHA or pin.

## Verdict

**NOT MERGEABLE as written.** One high finding (the design-relation side effect the ticket asked the spec to
settle is neither settled nor stated) and two medium scope findings; two low.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | high | Appending the segregation relations to `design_relations` changes every consumer that aggregates all design relations, and FR-016 neither decides nor states the consequence. quire-cli FR-043 (design gate): `quire matrix --strict` exits 1 for any live requirement with an `uncovered` block, so every requirement that satisfies any `control` (including non-risk security controls, see FND-002) and has no segregation edge now fails the design gate. quoin FR-161: `design-trace` is `unmet` if any design row is `uncovered`, and `detailed-design` without `relation` reads every design relation, so a class policy asking only for design-trace reports a realized requirement `unmet` (exit 1 with `gate: true`). quoin FR-165 / quire matrix render it as "no design element (fr-without-segregation)" for a requirement that has a realizing element. FR-016 itself says realization and segregation are different facts (lines 41-43) yet places both in the one list these consumers treat as "design". State the decision (segregation gap is or is not a design gap under `--strict` / design-trace), name the upstream change it depends on if not (for example quoin `design-trace` taking an optional `relation`), and add a criterion that fixes the chosen behaviour. | spec/functional/FR-016-segregation-design-relation.md:59-64, 84 | missing-requirement |
| FND-002 | medium | The scope over-includes. "Only a risk-control requirement is in scope" (line 51) is contradicted by line 55: any requirement that satisfies any `control` is in scope, and `control` is the generic spec-objects-security type. spec-objects-safety FR-205 declares its control rules scoped precisely because unscoped rules "would report every unrelated security control"; FR-016 reintroduces that one hop down. The stated remedy is unsound: mapping the key `off` removes every true positive, and "removes the edge" deletes a true `satisfies` trace to silence a warning. No better marker exists in quire-rs today (verified), so state this as an accepted limitation with a remedy that keeps the trace (for example a project `exclude` or a follow-up engine request for a condition on the other document), and drop the "Only a risk-control requirement" claim. | spec/functional/FR-016-segregation-design-relation.md:51-57 | wrong-requirement |
| FND-003 | medium | `when_any` matches the verb as authored (quire-rs `in_scope_by_edge`, no inverse normalisation). A control that authors `satisfied_by` (the iso forward verb, whose inverse is `satisfies`) toward the requirement is accepted by safety's `control-has-requirement` through the inverse index, but leaves that requirement out of FR-016 scope: no row, no finding, silently. Add the second condition `{verb: satisfied_by, direction: incoming, other: [control]}` (and to AC-3 / AC-4), or state that only the requirement-authored form scopes it. | spec/functional/FR-016-segregation-design-relation.md:51-53, 82 | missing-requirement |
| FND-004 | low | FR-010-AC-3 replaces a stale count with a closed enumeration by reference ("the other relations are those of FR-013, FR-014, FR-015 and FR-016"), which goes stale the same way the next time an FR adds a relation. AC-3 only needs the first-two-entries prefix; drop the enumeration. | spec/functional/FR-010-design-realization-edge.md:90 | wrong-requirement |
| FND-005 | low | FR-010 (edited file, unchanged hunk) still says spec-artifacts-process "does not list the verb in its `allowed_links`"; on process `origin/main` the `ADR` type lists `realizes_requirement: [FR, NFR]`. FR-016 copies this model for its own verb, where it is accurate. Correct the FR-010 sentence while the file is open. | spec/functional/FR-010-design-realization-edge.md:79-82 | wrong-requirement |
