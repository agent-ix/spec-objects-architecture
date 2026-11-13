---
id: SR-025
title: "Gap analysis — PLAT-1599 design edges and PLAT-1578 part class checks (PR #47)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-010-design-realization-edge.md, spec/functional/FR-012-software-safety-class-assignment.md, spec/tests.md, spec_objects_architecture/manifest.yaml, tests/test_design_edges.py, tests/test_software_safety_class_checks.py, tests/test_software_safety_class.py"
review_set: subset
---
# SR-025: Gap analysis — PLAT-1599 design edges and PLAT-1578 part class checks (PR #47)

## Summary

Tickets: PLAT-1599 and PLAT-1578. This review traces the criteria that the PR
adds or claims against the tagged tests, the manifest and the ticket
acceptance criteria:

- FR-010-AC-1 to AC-11 and FR-010-CON-1, through TC-140 to TC-150.
- FR-012-AC-9, AC-10 and AC-12 to AC-15.

Plan completion was not assessed. I ran the tests with quire-cli 0.45.0
(engine 0.60.0) and spec-artifacts-iso at the PR #75 head. I probed the
engine by hand on a criterion-only edge corpus, with and without
spec-artifacts-process.

Bindings checked against their asserts:

- TC-140 → FR-010-AC-1: correct.
- TC-141 → FR-010-AC-2: correct, with a weak oracle (SR-024 FND-005).
- TC-142 → FR-010-AC-3 and FR-010-CON-1: correct, but the load check is vacuous (SR-024 FND-004).
- TC-143 → FR-010-AC-4: runs a different command than the AC names (FND-003).
- TC-144 → FR-010-AC-5: correct.
- TC-145 → FR-010-AC-6: correct.
- TC-146 → FR-010-AC-7: correct.
- TC-147 → FR-010-AC-8: correct.
- TC-148 → FR-010-AC-9: correct.
- TC-149 → FR-010-AC-10: partial (FND-001).
- TC-150 → FR-010-AC-11: correct; the exit-code oracle is weak (SR-024 FND-001).
- FR-012-AC-9: correct.
- FR-012-AC-10: correct. Two tests cover it, `class-9` and wrong case.
- FR-012-AC-12: only the vocabulary half is tagged (FND-002).
- FR-012-AC-13: correct. The finding names the FR, the allocation, the part and both values. A higher-class requirement draws nothing.
- FR-012-AC-14: correct. Default off, and on with the key enabled.
- FR-012-AC-15: correct.

PLAT-1578's acceptance criteria are met:

- AC 1 (lower class, finding names both): the FR-012-AC-13 test.
- AC 2 (unassigned when the project declares classes): the FR-012-AC-14 test.
- AC 3 (no class write): only declarations are added, and the FR-012-AC-9 test finds no class value in any module file.
- AC 4 (manifest data, fixture corpora pass and fail): the `safety_class` corpus.

The checks only report. Nothing in the module or its output assigns a class.

## Verdict

**CONDITIONAL.** Every in-scope criterion has a tagged test. One test leaves
part of its criterion unasserted on the current CLI. One spec criterion and
its test disagree on the command. One PLAT-1599 ticket clause (an ADR
authoring the edge) is not delivered and has no follow-up.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | FR-010-AC-10 is only partly asserted. The `realized_criteria` check sits behind `if "--design" in relations --help`. quire-cli 0.45.0 has no `--design`, so the check is silently skipped and the test passes. The clause "the part's edge stays an FR-026 dangling reference" is never asserted, though I confirmed by hand that the engine reports `dangling-reference 'FR-001-AC-1'` without spec-artifacts-process. Assert the dangling clause now. Mark the `realized_criteria` clause as not yet claimed (an `xfail` with a reason) rather than skipping it silently: the module's own helper says "a skipped row is not coverage". | tests/test_design_edges.py:268-302 | correct-requirement-no-evidence |
| FND-002 | low | Only the vocabulary half of FR-012-AC-12 is tagged. The schema half (a self-contained, open `PartFrontmatter` with no `$ref`) is tested by the untagged `test_part_frontmatter_ref_is_self_contained_and_open`. Its comment still says the traceability entries "the engine cannot load yet (PLAT-1578), so the criterion is not claimed here". This PR makes that comment false. Tag the test FR-012-AC-12 and drop the comment. | tests/test_software_safety_class.py:239-251 | correct-requirement-no-evidence |
| FND-003 | low | FR-010-AC-4 names `quire relations --design --json`, but TC-143 runs `quire relations --json`, because the 0.45.0 CLI has no `--design`. The PR rewrote the TC-143 row in `spec/tests.md` with "where the CLI release has it" and left the AC unchanged. The spec and its test now name different commands. Change the AC so it no longer depends on the flag, or claim the AC only once `--design` ships. | spec/functional/FR-010-design-realization-edge.md:91, spec/tests.md:182 | wrong-requirement |
| FND-004 | medium | PLAT-1599 AC 1 says "the ADR archetype accept[s] a realizing edge". It is not delivered. ADR is declared by spec-artifacts-process, whose `allowed_links` does not list `realizes_requirement`, so an ADR authoring the edge draws `disallowed-edge-type`. FR-010 says so, and the fixture avoids it by authoring the inverse from NFR-001. spec-artifacts-process is not in the ticket's repo list, and no follow-up is linked. File the spec-artifacts-process change, or amend the ticket AC to "via the inverse". | spec/functional/FR-010-design-realization-edge.md:79-82 | missing-requirement |
| FND-005 | low | PLAT-1599 AC 2 asks for a "located message" for wrong-kind targets. `disallowed-edge-target` names the source id (`wrong_kind_part: edge ... targets 'scoring_engine'`) but no file path, unlike `dangling-reference`. FR-010 asks only for the source, the target and its kind, so this conforms to the spec. The difference from the ticket's wording comes from the engine (quire-rs). | spec/functional/FR-010-design-realization-edge.md:47-49 | wrong-requirement |
| FND-006 | low | FR-012 has no rows in `spec/tests.md`. This PR moves the FR-010 rows to ✅ and lands FR-012-AC-9, AC-10 and AC-12 to AC-15, but the test spec does not list any FR-012 criterion. | spec/tests.md:70-80 | missing-requirement |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | Round 1 (af58351). TC-149 now asserts that, without spec-artifacts-process, the part's edge is a `dangling-reference` to `FR-001-AC-1` naming `scoring_engine.md`, and that it resolves with spec-artifacts-process loaded. The `realized_criteria` clause is a separate `xfail(strict=True)` test that is conditional on `relations --design`. It reports XFAIL on quire-cli 0.45.0 and will fail loudly once the flag ships. FR-010-AC-10 and `spec/tests.md` say so. |
| FND-002 | fixed | Round 1 (af58351). `test_part_frontmatter_ref_is_self_contained_and_open` is tagged FR-012-AC-12, and the stale "cannot load yet" comment is gone. |
| FND-003 | fixed | Round 1 (af58351). FR-010-AC-4 now names `quire relations --json`, which is the command TC-143 runs, and `--design` only where the CLI release has it. |
| FND-004 | deferred | Moved to PLAT-1688 (ADR archetype accepts a realizing edge to requirements, spec-artifacts-process), which I verified exists. |
| FND-005 | accepted-no-change | The engine's wording: `disallowed-edge-target` names the source id, which FR-010 asks for. Adding a file path is a quire-rs output change and outside this module. |
| FND-006 | fixed | Round 1 (af58351). `spec/tests.md` adds an FR-012 coverage row and TC-160 to TC-162. |
