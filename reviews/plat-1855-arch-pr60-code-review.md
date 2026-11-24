---
id: SR-053
title: "Code review — PLAT-1855 segregation design relation (PR #60)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-objects-architecture; spec_objects_architecture/manifest.yaml, tests/test_segregation.py, tests/test_design_edges.py, tests/test_systems_kinds.py, spec/tests.md"
review_set: subset
---
# SR-053: Code review — PLAT-1855 segregation design relation (PR #60)

## Summary

Ticket: PLAT-1855 (code part of FR-016 and the FR-010 edit). Reviewed `git diff origin/main...HEAD`
at head `beff9a8`: the manifest (verb `segregates_for_requirement` with inverse
`requirement_segregated_by`, `allowed_links` on `part` and `connection`, relations
`fr-has-segregation` / `nfr-has-segregation` with the two-condition `when_any`, both appended to
`design_relations` after the FR-010 pair), the new `tests/test_segregation.py`, the TC-142 and
FR-010-AC-10 test edits, the `test_systems_kinds.py` design-verb set and `spec/tests.md` rows
TC-175..TC-188.

Measured, not read. All runs used quire 0.52.0 (engine 0.62.2) and quoin 0.36.8, with sibling
modules exported from each repository's `origin/main` into a scratch modules directory, and a
scratch copy of the PR head with `npm ci` for semantic-core:

- `test_segregation.py`, `test_design_edges.py` and `test_systems_kinds.py`: 65 passed, 1 xfailed.
  The same result with spec-artifacts-process PR #163 loaded (26 passed, 1 xfailed over the first
  two files). With iso PR #77, process PR #163 and security PR #80 loaded together: 65 passed,
  1 xfailed.
- Mutations of the manifest, each one run against the three files: dropping the `satisfied_by`
  condition fails TC-177 and TC-185; changing the verb category to `structural` fails TC-175;
  swapping the two segregation names in `design_relations` fails TC-177; moving them ahead of the
  FR-010 pair fails TC-177 and TC-142; dropping the verb from `connection.allowed_links` fails
  TC-176; removing them from `design_relations` fails TC-177, TC-184 and TC-187; dropping the
  inverse fails TC-175, TC-179 and TC-186; dropping the `satisfies` condition fails ten tests.
  Every mutation is killed.
- The `disallowed-edge-type` advisory for an ADR-authored edge appears in single-file
  `quire validate` with origin/main spec-artifacts-process and is absent under `--okf`; it is gone
  with process PR #163 loaded. TC-186 reads the loaded process manifest, so it holds both before
  and after that PR.
- The TC-142 change replaces the exact seven-name `required_relations` list and the equality on
  `design_relations` with per-relation field checks and a two-element prefix. No new pin or count
  test is added. The `len(...) == 1` assertions in the new tests count findings for one
  document, which is behaviour.
- The FR-010-AC-10 name selection is needed: origin/main's `test_design_edges.py` fails
  `test_fr010_ac10_design_join_lists_the_realized_criterion` once security PR #80 is loaded,
  because security's SOUP relations then lead the design join. The PR's version passes.
- `quire validate --scope .` over FR-016, FR-010 and `spec/tests.md` reports three `Traces To`
  pattern errors at TC-160, TC-162 and TC-169. The same three are reported on origin/main; the
  new rows TC-175..TC-188 add none.

### The FR-016-AC-14 deviation

The coder's stated cause is not the measured one. Loading origin/main's architecture module
without spec-objects-security prints `UnknownRole` warnings and then reports
`no loaded module declares traceability.required_relations`, with `quire validate --okf` exiting 0
and no trace finding at all. But the roles are not the cause. Adding the five missing roles to a
scratch copy of the manifest changes nothing. Bisecting the relations shows that the whole
relation set is dropped, silently, whenever a relation that carries `record_keys` names a kind no
loaded module declares. Here that is the module's own `connection-carries-classification` and
`classification-carried-by-connection` (`data_classification`) and
`connection-crosses-trust-boundary` (`trust_boundary`). Removing only `record_keys` from those
three relations restores the report, and FR-016-AC-14 then behaves exactly as written: each of
`fr-has-segregation` and `nfr-has-segregation` yields one advisory
`undeclared-relation-vocabulary` naming `control`.

So FR-016-AC-14 is true and observable once the engine reports instead of discarding. It needs no
amendment, and decoupling architecture from security's roles would not fix it. The defect is
the engine's silent discard (quire-rs), which also leaves any consumer that loads this module
without security with zero trace checks and exit 0; that is pre-existing on origin/main and
outside this PR.

## Verdict

**NOT MERGEABLE as is; one text fix.** The manifest change is correct and minimal, and every
FR-016 behaviour that the engine can show is covered by a test that a mutation makes fail.
FND-001 must be fixed in this PR: the strict xfail and the TC-188 row state a false cause. FND-002
is low and does not block.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | The strict xfail on `test_fr016_ac14_security_off_reports_the_undeclared_control_vocabulary` and the TC-188 row say the engine cannot load the module without security's roles (UnknownRole). Measured: UnknownRole is non-fatal; the engine silently drops every required relation when a relation with `record_keys` names an undeclared kind (the module's own `data_classification` / `trust_boundary` relations). Without them FR-016-AC-14 holds as written. Required edit: restate the reason and the TC-188 row with the measured cause and cite a quire-rs issue for the silent discard (to be filed). Better, make the xfail conditional on a probe, as `post_lines_xfail` does, so the row runs once the engine is fixed. Do not amend FR-016-AC-14. | tests/test_segregation.py:400-408, spec/tests.md TC-188 | correct-requirement-no-evidence |
| FND-002 | low | `spec/tests.md` carries a hand-written status per row (`✅`, `🚧 ...`), which the new rows TC-175..TC-188 continue. No test in this repository reads that column. It restates what the computed matrix reports and goes stale. The TC rows themselves mint the test-case ids that the trace tags bind to, so the rows stay. The repo convention predates this PR; drop the status column repo-wide rather than in this PR. | spec/tests.md:222-235 | wrong-requirement |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | Round 1 (d035469). The xfail is now conditional on the cached probe `_engine_reports_undeclared_vocabulary_without_security()`, which validates a one-FR corpus with process and security off and looks for `undeclared-relation-vocabulary`. It stays strict, and its reason `SECURITY_OFF_REASON` cites PLAT-1856 and the measured cause. The TC-188 row states the same; no other row changed. Checked that the probe can fail: with `record_keys` removed from the three relations, the probe flips and both AC-14 tests pass. Removing `control` from `when_any` as well then fails the security-off test, so a regression is caught once the engine is fixed. |
| FND-002 | deferred | PLAT-1857 (remove the hand-written status column from spec/tests.md across the repo). |
