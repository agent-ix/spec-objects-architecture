---
id: SR-024
title: "Code review — PLAT-1599 design edges and PLAT-1578 part class checks (PR #47)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-objects-architecture; pyproject.toml, poetry.lock, spec/functional/FR-010-design-realization-edge.md, spec/tests.md, spec_objects_architecture/manifest.yaml, tests/test_design_edges.py, tests/test_software_safety_class_checks.py, tests/test_software_safety_class.py, tests/test_systems_kinds.py, tests/fixtures/design_edges/, tests/fixtures/safety_class/"
review_set: subset
---
# SR-024: Code review — PLAT-1599 design edges and PLAT-1578 part class checks (PR #47)

## Summary

Tickets: PLAT-1599 and PLAT-1578. Scope is `git diff origin/main...HEAD` at
127311d (31 files). The change is Python tests, YAML manifest data, Markdown
fixtures and spec text, so the Python lane ran and no Rust or React lane did.

Checks run, confined to the change:

- The new and changed tests (`tests/test_design_edges.py`,
  `tests/test_software_safety_class_checks.py`,
  `tests/test_software_safety_class.py`, `tests/test_systems_kinds.py`) with
  quire-cli 0.45.0 (engine 0.60.0), the quire 0.60.0 Linux wheel, and
  spec-artifacts-iso at the PR #75 head: 76 passed.
- The same new tests against the installed (released) spec-artifacts-iso
  module: 4 of the 7 class-check tests fail (FND-003).
- `make schemas-check` (`node scripts/generate-schemas.mjs --check`): 41
  schemas match.
- Hand probes with `quire validate --okf [--strict]` over the valid and
  invalid fixture corpora and a criterion-only edge corpus.

What I verified as correct:

- The manifest adds `realizes_requirement` (category `traceability`,
  inverse `requirement_realized_by`), leaves `realizes` undeclared, and adds
  `realizes_requirement: [FR, NFR]` to `part` and `connection` only.
- The FR-010 narrowing from `["*"]` to `[FR, NFR]` works on the engine. A
  `part` target draws `disallowed-edge-target`, a missing id draws
  `dangling-reference` naming the file, and an edge to a criterion id
  (`FR-001-AC-1`) draws no `disallowed-edge-target` when spec-artifacts-process
  supplies the `obligations:` source.
- The class checks declare and never assign. The manifest holds only the
  `field_consistency`, `vocabulary` and `required_fields` declarations and
  `trace:unassigned-class: "off"`. No module file lists a class value. The
  skeleton carries none of the three fields. No output or file write sets a
  class.
- `poetry.lock` changes only the `quire` package block (version and the five
  wheel hashes) and `content-hash`. The Linux x86_64 wheel from quire-rs run
  43454484186 has the locked sha256. `pyproject.toml` changes only the quire
  constraint.
- There are no new pins, digests or file-tracking records. No standard is
  named or quoted. Nothing is vendored: the fixtures are small synthetic
  documents.

Not part of this diff, but found while checking: `spec/tests.md` fails
`quire validate` on `main` too, because three table headers read `Coverage
Status` and the TestMatrix archetype asserts `Status`.

## Verdict

**CONDITIONAL.** The manifest data meets FR-010 and FR-012. Two tests assert
less than they claim. FR-007-AC-5 now contradicts the manifest. The class-check
tests only pass once spec-artifacts-iso#75 has landed and its module is
installed.

## Findings

| ID | Severity | Summary | Refs | Escape Cause |
|---|---|---|---|---|
| FND-001 | medium | TC-150's `returncode == 3` does not show that the bad targets cause the failure. The valid corpus also exits 3 under `--strict`, and so does the invalid corpus with `dangling_part.md` and `wrong_kind_part.md` removed, because of other advisory warnings (`requirement-without-design`, `disallowed-edge-type`, semantic warnings). Without `--strict`, both bad targets are warnings and the run exits 0. Only the line matching carries the signal. Fix: compare against the same corpus without the two bad parts, or assert that the two findings are the ones that change the exit code. | tests/test_design_edges.py:305-321 | correct-requirement-no-evidence |
| FND-002 | medium | FR-007-AC-5 says the systems kinds' `allowed_links` use "exactly those [five] verbs with declared roles or `*`". `part` and `connection` now carry a sixth verb, whose targets `FR`/`NFR` are neither roles nor `*`. The AC was not amended. TC-104 was changed to exempt the verb, so it no longer checks the AC as written. And `used_verbs - {DESIGN_VERB} == EDGE_VERBS` no longer requires the verb to be used at all. Fix: amend FR-007-AC-5 to name the design verb and its requirement targets, and assert `used_verbs == EDGE_VERBS \| {DESIGN_VERB}`. | tests/test_systems_kinds.py:246-263, spec/functional/FR-007-systems-model-kinds.md:108 | wrong-requirement |
| FND-003 | medium | The class-check tests depend on an unmerged sibling. Against the installed spec-artifacts-iso, which has no `carried_fields`, the FR-012-AC-10 (x2), AC-12 and AC-13 tests fail. They pass only with spec-artifacts-iso#75 (still OPEN) loaded. Merging this PR first leaves the suite red for anyone with the released module. Land iso#75 and install it first, or merge them together. | tests/test_software_safety_class_checks.py | implementation-bug-despite-evidence |
| FND-004 | low | `assert _run("relations", ...)` in TC-142 is always true: a `CompletedProcess` is truthy whatever the exit code. So the "module loads under quire-rs without error" clause of FR-010-AC-3 is not checked here. Assert `returncode == 0`. | tests/test_design_edges.py:143 | correct-requirement-no-evidence |
| FND-005 | low | TC-140 (`"DuplicateEdgeType" not in stderr`), TC-141 (no `disallowed-edge` line) and the FR-012-AC-12 test check only that a message is absent, with no exit-code or positive control. They would pass if the command failed before reporting anything. Today the commands exit 0, so this is only a weak oracle. Assert the expected exit code, or a known line, alongside the absence. | tests/test_design_edges.py:102-122, tests/test_software_safety_class_checks.py:87-101 | correct-requirement-no-evidence |
| FND-006 | low | `test_software_safety_class_checks.py` imports the private helpers `_module` and `_run` from another test module (`tests.test_design_edges`). It also redefines `_bundle` and `_manifest`, which `test_design_edges.py` already defines. Move the shared helpers into `tests/conftest.py`. | tests/test_software_safety_class_checks.py:19, tests/test_design_edges.py:37-104 | implementation-bug-despite-evidence |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | Round 1 (af58351). TC-150 now adds a control: the same invalid corpus with `dangling_part.md` and `wrong_kind_part.md` removed draws no `dangling-reference` and no `disallowed-edge-target`. So the two diagnostics come from the bad parts. It also asserts exactly one `disallowed-edge-target`. |
| FND-002 | fixed | Round 1 (af58351). FR-007-AC-5 now names `realizes_requirement` and its `FR`/`NFR` targets. TC-104 asserts `used_verbs == EDGE_VERBS \| {DESIGN_VERB}`. |
| FND-003 | deferred | Merge order, not code: the coordinator rules that spec-artifacts-iso#75 merges first. Re-run at 66900a1 with the iso#75 head (8aabfc7): the class-check tests pass. |
| FND-004 | fixed | Round 1 (af58351). TC-142 asserts `loaded.returncode == 0` on `quire relations --json`. |
| FND-005 | fixed | Round 1 (af58351). TC-140, TC-141 and the FR-012-AC-12 test now assert `returncode == 0` alongside the absence checks. All pass with quire-cli 0.45.0. |
| FND-006 | fixed | Round 1 (af58351). `ix_module`, `module_args`, `run_quire` and `validate_bundle` move to `tests/conftest.py`. Neither test module imports from the other or redefines them. |
