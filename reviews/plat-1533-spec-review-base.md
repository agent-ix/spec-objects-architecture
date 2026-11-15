<!-- reviewer repo=agent-ix/spec-objects-architecture visibility=public quoin=0.30.0 module=spec-artifacts-process@unresolved id=SR-037 method=spec-review/base lang=spec pr=spec-objects-architecture#51 model=claude-opus-5-5 run=plat-1533-pr51-r1 -->

| FND | Severity | Check | Summary |
| --- | --- | --- | --- |
| FND-001 | high | soundness | AC-6/AC-9 and Behavior assert a `facts.sinks` key. quire-rs FR-096 keys `facts` by archetype name (`data_sink`) and fixes no key. |
| FND-002 | high | soundness | AC-7 says `unknown` gives "one denial". FR-025 also fires `regulated-data-to-uncovered-processor` on the same sink, so there are two. |
| FND-003 | high | soundness | AC-11: lowering only the LLM-sink check leaves FR-025's other sink denial at `error`, so `quire validate` does not exit 0. |
| FND-004 | medium | untestable-ac | AC-7's `not_applicable` clause ("whatever the loaded rule states") passes for any outcome. |
| FND-005 | medium | ambiguous | Behavior: a connection with no `delivers_to` is "reported as such", but no report in FR-096 or FR-044 has that output. |
| FND-006 | medium | soundness | AC-9: "connections carry no classification" still allows a part-fed sink with its own `carries` that FR-025 rules deny. |
| FND-007 | medium | soundness | AC-3/Behavior: the `delivers_to` dangling-reference statement drops FR-013's quire-rs FR-085 exception for an `ix://` target under an unloaded authority. |

+++ [reviewer data]

```yaml
clean: false
scope:
  - {id: FR-015, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "The module SHALL let an author declare that place as a `data_sink` and feed it through `delivers_to` edges, so the boundary-crossing rules of milestone M2 can read the sink as data."}
  - {id: FR-015-AC-1, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "A `data_sink` document with each of the eight `SinkKind` values and each of the four `processor_agreement` values validates; a `kind` outside `SinkKind` (for example `medical`), a `processor_agreement` outside the enum, and a document missing either required field each fail validation naming the field; ..."}
  - {id: FR-015-AC-2, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "The extracted `DataSink` record carries `kind` and `processorAgreement` as written, and carries `processor`, `region`, `purpose` and `audienceRoles` if and only if their frontmatter fields are present; ..."}
  - {id: FR-015-AC-3, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "A connection with a `delivers_to` edge to a `data_sink` validates with no `disallowed-edge-type` or `disallowed-edge-target` finding at any severity; ... one to an id no document has yields `dangling-reference` naming the file and id."}
  - {id: FR-015-AC-4, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "A part with a `delivers_to` edge to a `data_sink` validates, and a `data_sink` with a `carries` edge to a `data_classification` validates; ..."}
  - {id: FR-015-AC-5, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "`connection` and `part` list `delivers_to: [data_sink]`, `data_sink` lists `carries: [data_classification]`, ... and `Connection.json` is unchanged."}
  - {id: FR-015-AC-6, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "`quire relations --flow --json` lists the sink in `facts.sinks` with `kind: llm_prompt`, `processor_agreement: not_covered` and the feeding connection and classification, and, with the security module loaded, one denial under the LLM-sink rule naming that sink."}
  - {id: FR-015-AC-7, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "with `unknown`, the sink lists `unknown` and one denial is reported; with `not_applicable`, the report lists `not_applicable` and the outcome is whatever the loaded rule states for it, never an engine default."}
  - {id: FR-015-AC-8, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "A `flow_rules` entry whose `any_of` names a value outside the `SinkKind` or `processor_agreement` enum ... makes the module fail to load, naming the rule and the value."}
  - {id: FR-015-AC-9, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "A corpus with no `delivers_to` edge, and one whose connections carry no classification, yields no denial from any starter rule; ..."}
  - {id: FR-015-AC-10, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "`quire relations --flow --json` over the seeded sink model gives byte-identical output across two runs, and `--strict` exits 1 when the sink model yields a denial and 0 when it yields none."}
  - {id: FR-015-AC-11, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "With `--severity trace:<check>=warning` for the LLM-sink rule's check, the sink's denial is reported as a warning and `quire validate` exits 0."}
  - {id: FR-015-AC-12, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "`skeletons/data_sink.md` validates with zero errors, states `kind` and `processor_agreement` and no `covered` value, ..."}
  - {id: FR-015-AC-13, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "No heading, description, example, skeleton or fixture added by this requirement names a paywalled standard, and no file computes or defaults a `kind`, `processor_agreement`, region or `delivers_to` edge."}
  - {id: quire-rs FR-096, path: "agent-ix/quire-rs#691 spec/functional/FR-096-flow-rules.md", role: context_only, excerpt: "`facts`: an object keyed by archetype name, in sorted order ... The keys are exactly the archetype names the loaded rules declare; the engine fixes no key"}
  - {id: spec-objects-security FR-025, path: "agent-ix/spec-objects-security#61 spec/functional/FR-025-control-safeguards-and-starter-flow-rules.md", role: context_only, excerpt: "The rule `regulated-data-to-uncovered-processor` and the rule `health-in-llm-prompt-or-tool-call` SHALL both be reported for a health-carrying LLM sink that fails both, each under its own check."}
findings:
  - fnd: FND-001
    severity: high
    confidence: high
    method: spec-review/base
    check: soundness
    artifact_id: FR-015-AC-6
    related_ids: [FR-015-AC-9, FR-015, quire-rs FR-096-AC-16]
    path: spec/functional/FR-015-data-sink.md
    lines: "131, 135, 165, 168"
    excerpt: |-
      `quire relations --flow --json` lists the sink in `facts.sinks` with `kind: llm_prompt`, `processor_agreement: not_covered` and the feeding connection and classification, and, with the security module loaded, one denial under the LLM-sink rule naming that sink.
    finding: "FR-015 asserts a `facts.sinks` key (Behavior 131 and 135, AC-6, AC-9). quire-rs FR-096 (PR #691) keys `facts` by the archetype names the rules declare and says the engine fixes no key, so the key is `facts.data_sink`. Each entry is `{id, repo, path, fields, edges}`, and `fields` holds only the keys some condition reads. The feeding connection and its classification appear in the `connection` entry's edges, not the sink's. As written, AC-6 can never pass."
  - fnd: FND-002
    severity: high
    confidence: high
    method: spec-review/base
    check: soundness
    artifact_id: FR-015-AC-7
    related_ids: [FR-015, spec-objects-security FR-025]
    path: spec/functional/FR-015-data-sink.md
    lines: "132, 166"
    excerpt: |-
      The same model with `processor_agreement: covered` lists the sink with `covered` and no denial under the LLM-sink rule; with `unknown`, the sink lists `unknown` and one denial is reported; with `not_applicable`, the report lists `not_applicable` and the outcome is whatever the loaded rule states for it, never an engine default.
    finding: "With `unknown`, AC-7 expects exactly one denial and is not scoped to a rule. Under FR-025's starter rules, `health-in-llm-prompt-or-tool-call` and `regulated-data-to-uncovered-processor` both match a health-fed sink with `processor_agreement: unknown`, and FR-025 requires both to be reported. The report holds two denials. Scope the clause to the LLM-sink rule's check, as the `covered` clause already is."
  - fnd: FND-003
    severity: high
    confidence: high
    method: spec-review/base
    check: soundness
    artifact_id: FR-015-AC-11
    related_ids: [FR-015-AC-6, spec-objects-security FR-025]
    path: spec/functional/FR-015-data-sink.md
    lines: "170"
    excerpt: |-
      With `--severity trace:<check>=warning` for the LLM-sink rule's check, the sink's denial is reported as a warning and `quire validate` exits 0.
    finding: "On the AC-6 seeded sink (health, llm_prompt, not_covered) with the security module loaded, `regulated-data-to-uncovered-processor` also denies at its default severity `error` (FR-096). Lowering only the LLM-sink check leaves an error, so `quire validate` exits non-zero. Either lower both checks, or use a fixture only one rule matches."
  - fnd: FND-004
    severity: medium
    confidence: high
    method: spec-review/base
    check: untestable-ac
    artifact_id: FR-015-AC-7
    related_ids: [spec-objects-security FR-025]
    path: spec/functional/FR-015-data-sink.md
    lines: "166"
    excerpt: |-
      with `not_applicable`, the report lists `not_applicable` and the outcome is whatever the loaded rule states for it, never an engine default.
    finding: "The `not_applicable` clause accepts any denial outcome, so the only thing it checks is the echoed value. FR-025's starter rules match only `not_covered` and `unknown`, so state the concrete expected result: no denial under the LLM-sink rule or `regulated-data-to-uncovered-processor`."
  - fnd: FND-005
    severity: medium
    confidence: medium
    method: spec-review/base
    check: ambiguous
    artifact_id: FR-015
    related_ids: [FR-015-AC-9, quire-cli FR-044]
    path: spec/functional/FR-015-data-sink.md
    lines: "135"
    excerpt: |-
      - A connection with no `delivers_to` edge SHALL contribute no sink to `facts.sinks` and be reported as such, not defaulted to a sink kind.
    finding: "\"Be reported as such\" names no output. FR-096 and FR-044 define no 'connection without sink' row, and AC-9 tests only the absence. Drop the clause, or name the report entry, for example the `connection` facts entry having no `delivers_to` edge."
  - fnd: FND-006
    severity: medium
    confidence: high
    method: spec-review/base
    check: soundness
    artifact_id: FR-015-AC-9
    related_ids: [spec-objects-security FR-025-AC-6]
    path: spec/functional/FR-015-data-sink.md
    lines: "168"
    excerpt: |-
      A corpus with no `delivers_to` edge, and one whose connections carry no classification, yields no denial from any starter rule; a connection with no `delivers_to` edge adds no entry to `facts.sinks`, and no sink, kind, agreement, region or edge appears in the report that no document states.
    finding: "The second corpus ('connections carry no classification') can still hold a part-fed `data_sink` with its own `carries` edge to a health classification. FR-025's `any_path` reaches that sink, and `regulated-data-in-log` and others deny it, so the AC is false for a valid corpus. Restrict the corpus, as FR-025-AC-6 does, to one where no connection carries a classification and no sink carries one."
  - fnd: FND-007
    severity: medium
    confidence: medium
    method: spec-review/base
    check: soundness
    artifact_id: FR-015-AC-3
    related_ids: [FR-015, FR-013, quire-rs FR-085]
    path: spec/functional/FR-015-data-sink.md
    lines: "121, 162"
    excerpt: |-
      ... a `delivers_to` to a non-`data_sink` target yields `disallowed-edge-target` naming source, target and kind, and one to an id no document has yields `dangling-reference` naming the file and id.
    finding: "FR-013 scopes `dangling-reference` to a bare id or an `ix://` target under a loaded member's authority, and exempts an unloaded authority (quire-rs FR-085). FR-015 says any id no document has yields `dangling-reference`, which contradicts FR-085 for a cross-repo sink. Copy FR-013's scoping."
bindings: []
```

+++
