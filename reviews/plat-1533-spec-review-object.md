<!-- reviewer repo=agent-ix/spec-objects-architecture visibility=public quoin=0.30.0 module=spec-artifacts-process@unresolved id=SR-040 method=spec-review/object-review lang=spec pr=spec-objects-architecture#51 model=claude-opus-5-5 run=plat-1533-pr51-r1 -->

| FND | Severity | Check | Summary |
| --- | --- | --- | --- |
| FND-001 | medium | ambiguous | `processor` is "a `part` (with an external role)", but no external part role exists. It and `audience_roles` are unresolved frontmatter ids that no rule path can follow, and the spec does not say whether they are checked. |

+++ [reviewer data]

```yaml
clean: false
scope:
  - {id: FR-015, path: spec/functional/FR-015-data-sink.md, role: examined, excerpt: "A `data_sink` document states these top-level frontmatter fields ... `kind`, `processor_agreement`, `processor`, `region`, `purpose`, `audience_roles`"}
  - {id: manifest part/connection/external_contract, path: spec_objects_architecture/manifest.yaml, role: context_only, excerpt: "- name: part\n  roles: [systems-part]\n  frontmatter_schema_ref: schemas/PartFrontmatter.json"}
  - {id: FR-012, path: spec/functional/FR-012-software-safety-class-assignment.md, role: context_only, excerpt: "PartFrontmatter open frontmatter schema referenced through frontmatter_schema_ref"}
  - {id: FR-013, path: spec/functional/FR-013-connection-carries-data-classification.md, role: context_only, excerpt: "The verb `carries` is already declared by `spec-artifacts-iso` (category `dataflow`) and is reused, not redeclared."}
findings:
  - fnd: FND-001
    severity: medium
    confidence: medium
    method: spec-review/object-review
    check: ambiguous
    artifact_id: FR-015
    related_ids: [FR-015-AC-2, quire-rs FR-096]
    path: spec/functional/FR-015-data-sink.md
    lines: "52, 55"
    excerpt: |-
      | `processor` | no | the id of the `part` (with an external role) or `external_contract` that receives the data |
    finding: "At 10414f7, `part` has only the role `systems-part`, and no manifest declares an external part role, so 'a part with an external role' cannot be checked. `processor` and `audience_roles` hold document ids as frontmatter values, not relationships. The engine does not resolve them (no dangling or wrong-kind check), and an FR-096 path follows edges only, so no rule can reach the processor or a role's fields. State either that they are unresolved free ids, with no kind check, or make them edges (for example `processed_by`) with `allowed_links` targets."
bindings: []
```

+++
