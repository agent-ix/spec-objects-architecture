---
id: SR-037
title: "Spec review (base) - PLAT-1533 FR-015 data_sink and delivers_to (PR #51)"
type: SpecReview
analysis: base
scope: "agent-ix/spec-objects-architecture; spec/functional/FR-015-data-sink.md (origin/main...10414f7 review pass, d0927cb disposition pass 1, PR #51)"
review_set: subset
relationships:
  - {target: "ix://agent-ix/spec-objects-architecture/FR-015", type: references}
---
# SR-037: Spec review (base) - FR-015 data_sink (PR #51)

## Summary

Ticket: PLAT-1533. Base checklist over the whole of FR-015: the statement, every Behavior line and
FR-015-AC-1 to AC-13. Checked against quire-rs FR-096 (PR #691), quire-cli FR-044 (PR #205) and
spec-objects-security FR-025 (PR #61). The review set is a subset: base (this file), EARS (SR-038),
integrity (SR-039), object (SR-040) and dependency (SR-041).

Clean on the review pass: AC-1, AC-2, AC-4, AC-5, AC-8, AC-10, AC-12 and AC-13.

## Verdict

**FAIL at 10414f7**: three high and four medium findings. **Disposition pass 1 at d0927cb: all seven
fixed**, no new findings in this method.

## Findings

| ID | Severity | Summary | Refs |
|---|---|---|---|
| FND-001 | high | FR-015 asserts a `facts.sinks` key (Behavior 131 and 135, AC-6, AC-9). quire-rs FR-096 (PR #691) keys `facts` by the archetype names the rules declare and says the engine fixes no key, so the key is `facts.data_sink`. Each entry is `{id, repo, path, fields, edges}`, and `fields` holds only the keys some condition reads. The feeding connection and its classification appear in the `connection` entry's edges, not the sink's. As written, AC-6 can never pass. | spec/functional/FR-015-data-sink.md:131,135,165,168 |
| FND-002 | high | With `unknown`, AC-7 expects exactly one denial and is not scoped to a rule. Under FR-025's starter rules, `health-in-llm-prompt-or-tool-call` and `regulated-data-to-uncovered-processor` both match a health-fed sink with `processor_agreement: unknown`, and FR-025 requires both to be reported. The report holds two denials. Scope the clause to the LLM-sink rule's check, as the `covered` clause already is. | spec/functional/FR-015-data-sink.md:132,166 |
| FND-003 | high | On the AC-6 seeded sink (health, llm_prompt, not_covered) with the security module loaded, `regulated-data-to-uncovered-processor` also denies at its default severity `error` (FR-096). Lowering only the LLM-sink check leaves an error, so `quire validate` exits non-zero. Either lower both checks, or use a fixture only one rule matches. | spec/functional/FR-015-data-sink.md:170 |
| FND-004 | medium | The `not_applicable` clause of AC-7 accepts any denial outcome, so the only thing it checks is the echoed value. FR-025's starter rules match only `not_covered` and `unknown`, so state the concrete expected result: no denial under the LLM-sink rule or `regulated-data-to-uncovered-processor`. | spec/functional/FR-015-data-sink.md:166 |
| FND-005 | medium | "Be reported as such" names no output. FR-096 and FR-044 define no 'connection without sink' row, and AC-9 tests only the absence. Drop the clause, or name the report entry, for example the `connection` facts entry having no `delivers_to` edge. | spec/functional/FR-015-data-sink.md:135 |
| FND-006 | medium | The second AC-9 corpus ('connections carry no classification') can still hold a part-fed `data_sink` with its own `carries` edge to a health classification. FR-025's `any_path` reaches that sink, and `regulated-data-in-log` and others deny it, so the AC is false for a valid corpus. Restrict the corpus, as FR-025-AC-6 does, to one where no connection carries a classification and no sink carries one. | spec/functional/FR-015-data-sink.md:168 |
| FND-007 | medium | FR-013 scopes `dangling-reference` to a bare id or an `ix://` target under a loaded member's authority, and exempts an unloaded authority (quire-rs FR-085). FR-015 (AC-3 and Behavior) says any id no document has yields `dangling-reference`, which contradicts FR-085 for a cross-repo sink. Copy FR-013's scoping. | spec/functional/FR-015-data-sink.md:121,162 |

## Dispositions

| FND | outcome | reason |
|---|---|---|
| FND-001 | fixed | d0927cb: Behavior line 141 and AC-6 name `facts.data_sink` ("the key is the archetype name, quire-rs FR-096"), with `kind` and `processor_agreement` under `fields`. The feeding `delivers_to` and `carries` edges are on the `facts.connection` entry. AC-9 and Behavior line 145 also use `facts.data_sink`/`facts.connection`. No `facts.sinks` remains. |
| FND-002 | fixed | d0927cb: AC-7 now says that with `unknown` "the report holds one denial under each of those two checks" (`health-in-llm-prompt-or-tool-call`, `regulated-data-to-uncovered-processor`). This matches FR-025 rows 132-133, which both match `unknown`. |
| FND-003 | fixed | d0927cb: AC-11 lowers both checks to `warning` and expects exit 0. It adds that "lowering only one of them leaves an error and a non-zero exit". |
| FND-004 | fixed | d0927cb: AC-7 says that with `not_applicable` "the report holds no denial under either check, because FR-025 matches only `not_covered` and `unknown`". FR-025 rows 132-133 confirm the match set. |
| FND-005 | fixed | d0927cb: Behavior line 145 names the output: the connection's `facts.connection` entry "whose `edges` hold no `delivers_to`", with no entry added to `facts.data_sink`. AC-9 asserts the same. |
| FND-006 | fixed | d0927cb: the AC-9 second corpus is now one "in which no connection carries a classification and no `data_sink` carries one". |
| FND-007 | fixed | d0927cb: Behavior line 131 and AC-3 scope `dangling-reference` to a bare id or an `ix://` target under a loaded member's authority. Both exempt an unloaded authority when the source member declares its identity (quire-rs FR-085). |
