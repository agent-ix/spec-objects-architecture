---
id: SR-018
title: "Spec review r3 — FR-008, FR-002-CON-4, FR-005-AC-10 and tests.md at e164b70 (PR #41)"
type: SpecReview
analysis: base
scope: "agent-ix/spec-objects-architecture; PR #41 diff origin/main...e164b70: spec/functional/FR-002-emitted-json-schemas.md, FR-004-role-schemas.md, FR-005-executable-skeletons.md, FR-006-architecture-lowerings.md, FR-008-record-key-sections.md, spec/functional/index.md, spec/spec.md, spec/tests.md, spec/usecase/US-001-declare-architecture-objects-against-semantic-core.md, plan/Plan-001-semantic-data-schemas/tasks/Task-010-consumer-boundaries.md"
review_set: subset
---
# SR-018: Spec review r3 — FR-008, FR-002-CON-4, FR-005-AC-10 and tests.md at e164b70 (PR #41)

## Summary

Ticket: PLAT-196 (also PLAT-201). This round re-checks the spec edits made
since SR-012: the FR-002-CON-4 registry rule, FR-005-AC-10 after the
quire-rs#398 fix, spec.md Out of Scope, the tests.md Test Environment, the
FR-008 matrix rows, and US-001 and Task-010 wording.

## Verdict

**MERGEABLE after one medium wording fix.**

Verified clean:

- **FR-002-CON-4 and TC-019.** CON-4 now reads "resolve every package,
  `@agent-ix/semantic-core` included, from `registry.npmjs.org` ... with no
  registry credentials". This matches the rule TC-019 enforces: every
  `resolved` starts with `https://registry.npmjs.org/`, with no exception. It
  also matches the repo: no `.npmrc`, and no GitHub Packages or token wiring
  left anywhere.
- **FR-005-AC-10, spec.md and Task-010.** All three agree that the engine
  collapses shared-id entries (quire-rs#398). The spec.md Out of Scope bullet
  for #398 is removed. The tests.md Test Environment now lists only TC-026 as
  an expected failure, which matches the one remaining xfail.
- **The FR-008 matrix row (TC-120..TC-126).** It claims ✅, which is true at
  e164b70 under quire 0.55.0 and semantic-core 0.4.1 (coder-reported run).
- **FR-004.** The "hand-built" labelling bullet stays deleted (SR-012 FND-003).
- **FR-006.** It names quoin FR-122 / quire-rs FR-081 in both Behavior and
  Dependencies.
- **FR-008.** Its Dependencies line ("the `quire` dev dependency must carry
  them") states a real build requirement, not a version tracker.
- **Ceremony.** No new pins, digests or SHA records in the spec.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | The TC-091 row title still reads "a per-file index makes an alternate-bearing declaration ambiguous with itself". FR-005-AC-10 now states the opposite ("raises no `semantic.ambiguous-type` for a declaration against itself"). The test `test_a_per_file_bundle_index_does_not_make_a_declaration_ambiguous_with_itself` asserts that, with no xfail. The row's ✅ sits beside a title that describes the old engine failure, so the matrix cell is not honest. Reword the title to "a per-file index raises no `semantic.ambiguous-type` for a declaration against itself". | spec/tests.md:152 | wrong-requirement |
