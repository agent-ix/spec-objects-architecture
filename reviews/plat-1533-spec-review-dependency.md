---
id: SR-041
title: "Spec review (dependency) - PLAT-1533 FR-015 data_sink and delivers_to (PR #51)"
type: SpecReview
analysis: dependency
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-015-data-sink.md relationships, Inputs, Out of scope, Dependencies (origin/main...10414f7 review pass, d0927cb disposition pass 1, PR #51)"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-015", type: references}
---
# SR-041: Spec review (dependency) - FR-015 data_sink (PR #51)

## Summary

Ticket: PLAT-1533. The FR-015 `relationships` (implements US-001; depends_on FR-002, FR-004, FR-005,
FR-007, FR-009, FR-013, spec-objects-security FR-023, quire-rs FR-058 and FR-096, and the quire-cli
report FR) and the body Dependencies. Checked against quire-cli FR-044 (PR #205) and
spec-objects-security FR-025 (PR #61, branch `plat-1533-safeguards-spec`). PLAT-1532 (Backlog;
FR-014 not yet authored) is correctly a non-blocking sibling, because no FR-015 AC needs `crosses`.

## Verdict

**FAIL at 10414f7**: one high and one medium finding. **Disposition pass 1 at d0927cb: both fixed.**
Disposition pass 1 adds one new medium finding (FND-003) and one new low finding (FND-004), both
introduced by the FND-002 fix.

## Findings

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-001 | high | FR-015 cites quire-cli FR-026 for `quire relations --flow`. quire-cli main has `FR-026-matrix-subcommand.md`, and the PLAT-1533 ticket says FR-026 is already used. The `--flow` mode is FR-044 (quire-cli PR #205, `FR-044-relations-flow-mode.md`). The frontmatter `depends_on` target, the Inputs link, Out of scope and Dependencies all point at the matrix FR. Replace all four with FR-044. | spec/functional/FR-015-data-sink.md:26,91,181,188 |
| FND-002 | medium | AC-6, AC-7, AC-9 and AC-11 pass only with FR-025's starter rules loaded ('the LLM-sink rule', 'any starter rule'), yet FR-025 is a Sibling and not in `relationships`. FR-025 depends_on FR-015 and claims draft c, d and g as its own fixtures (FR-025-AC-3, AC-4, AC-6). It assigns h, i and j to FR-096/FR-044, while FR-015 also claims c, d, g, h, i and j. Either add FR-025 as a test-time `depends_on` and name its check `health-in-llm-prompt-or-tool-call`, or keep FR-015's seeded ACs to the facts and edges and leave the denial outcomes to FR-025. | spec/functional/FR-015-data-sink.md:174,187-189 |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | d0927cb replaces all four: frontmatter `depends_on` `ix://agent-ix/quire-cli/spec/functional/FR-044`, the Inputs link, Out of scope ("The report command: quire-cli FR-044") and Dependencies Upstream ("quire-cli FR-044"). The remaining `FR-026` at line 131 is quire-rs FR-026 (`dangling-reference`), which is correct. |
| FND-002 | fixed | d0927cb adds `ix://agent-ix/spec-objects-security/FR-025` as `depends_on` and a "Test-time" Dependencies line. AC-6, AC-7 and AC-11 name both FR-025 checks, and AC-9 names "FR-025 starter rule". The ownership paragraph credits FR-025-AC-3, AC-4 and AC-6 with the rule-level c, d and g fixtures, and keeps FR-015 to facts, edges and the end-to-end report. |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-003 | medium | The FND-002 fix adds `FR-015 depends_on spec-objects-security FR-025`. FR-025 on PR #61 already declares `depends_on ix://agent-ix/spec-objects-architecture/FR-015` (its frontmatter lines 16-17). That makes a two-node `depends_on` cycle across the repos, so a dependency-ordered plan or blast-radius walk cannot put either FR upstream. The body already separates "Upstream" from "Test-time". Fix: give the frontmatter edge a non-ordering type (for example `references`), or drop it and keep the Test-time line. This review's FND-002 offered "test-time `depends_on`" as one option and did not foresee the cycle. | spec/functional/FR-015-data-sink.md:28-29 |
| FND-004 | low | The rewritten ownership paragraph reads "... with FR-025 loaded, so FR-025 is a test-time `depends_on`: e for sink enums (AC-8), h and i (AC-10) and j (AC-11), beside the validation and typed-record criteria". After the colon, the list of FR-015's own criteria reads as FR-025's. It also drops the letters c, d and g from FR-015's share, while the AC-6, AC-7 and AC-9 labels still claim them. Fix: end the FR-025 clause with a full stop, then write "This requirement also owns e for sink enums (AC-8), ...". | spec/functional/FR-015-data-sink.md:184 |
