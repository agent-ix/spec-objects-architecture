<!-- reviewer repo=agent-ix/spec-objects-architecture visibility=public quoin=0.30.0 module=spec-artifacts-process@unresolved id=SR-039 method=spec-review/integrity-analysis lang=spec pr=spec-objects-architecture#51 model=claude-opus-5-5 run=plat-1533-pr51-r1 -->

| FND | Severity | Check | Summary |
| --- | --- | --- | --- |
| FND-001 | medium | coverage | The `region` code-format SHALL (ISO 3166-1 alpha-2, `eu`, `eea`) states no case or schema form, and no AC tests it. |
| FND-002 | low | coverage | Behavior says an out-of-enum value fails "naming the field and the value". AC-1 checks only "naming the field". |

+++ [reviewer data]

```yaml
clean: false
scope:
  - {id: FR-015, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "Behavior-to-AC coverage, Outputs-to-AC coverage, index entry, frontmatter relationships, and constraint ids FR-015-CON-1..4."}
  - {id: FR-015-AC-1, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "a `kind` outside `SinkKind` (for example `medical`), a `processor_agreement` outside the enum, and a document missing either required field each fail validation naming the field"}
  - {id: FR-015-AC-2, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "`region`, `purpose` and `audience_roles` that are not lists of non-empty strings fail."}
  - {id: FR-015-AC-12, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "the exports, manifest description, enums, both schemas, locators and skeleton state the same keys and the same two value lists"}
  - {id: spec/functional/index.md, path: spec/functional/index.md, role: examined, excerpt: "* [FR-015: A data_sink declares where data lands, ...](./FR-015-data-sink.md)"}
findings:
  - fnd: FND-001
    severity: medium
    confidence: high
    method: spec-review/integrity-analysis
    check: coverage
    artifact_id: FR-015
    related_ids: [FR-015-AC-2]
    path: spec/functional/FR-015-data-sink.md
    lines: "53, 112, 161"
    excerpt: |-
      - `region` SHALL be a list of strings, each an ISO 3166-1 alpha-2 code or `eu` or `eea`; `purpose` and `audience_roles` SHALL be lists of non-empty strings.
    finding: "The statement fixes a code format but leaves open whether it is checked against the ISO list or a `^[A-Z]{2}$` pattern, and what case applies (`DE` vs `de`, beside lowercase `eu`/`eea`). Two implementers would emit different schemas. AC-2 checks only 'lists of non-empty strings', so a `region: [xx-bad]` passes every AC. State the schema form (pattern or enum, and case), and add an AC case such as `region: [Germany]` failing."
  - fnd: FND-002
    severity: low
    confidence: high
    method: spec-review/integrity-analysis
    check: coverage
    artifact_id: FR-015-AC-1
    related_ids: [FR-015]
    path: spec/functional/FR-015-data-sink.md
    lines: "110, 160"
    excerpt: |-
      a `kind` outside `SinkKind` (for example `medical`), a `processor_agreement` outside the enum, and a document missing either required field each fail validation naming the field
    finding: "Behavior line 110 requires the out-of-enum diagnostic to name the field and the value. AC-1 asserts only the field, so the value half of that SHALL has no AC."
bindings: []
```

+++
