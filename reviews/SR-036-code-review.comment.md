<!-- reviewer repo=agent-ix/spec-objects-architecture visibility=public quoin=0.35.0 module=spec-objects-architecture@8dc54d1e id=SR-036 method=code-review lang=py pr=spec-objects-architecture#54 model=gpt-6.1-sol run=3548c9d2-949f-427a-9f73-a76ca26647b9 -->

| FND | Severity | Check | Summary |
| --- | --- | --- | --- |
| FND-001 | high | code-bug | TC-104 fails against the new allowed link: its existing assertion requires every target other than connection/carries to be a declared role, but trust_boundary is an object kind rather than a role. Reproduced with the locked build wrapper: tests/test_systems_kinds.py::test_edge_verbs_and_roles_are_declared_and_used fails at line 262 with AssertionError (connection, trust_boundary). Update the allowed-target check and declared verb expectations for crosses. |
| FND-002 | high | soundness | The new tests duplicate _validate, _relations, and _lines from tests/test_data_flow_edges.py. The copied helpers have the same behavior (with only the existing module-selection option differing) and can drift; generalize/share the existing helpers instead. |

+++ [reviewer data]

```yaml
clean: false
scope:
- id: FR-007-AC-5
  path: spec/functional/FR-007-systems-model-kinds.md
  role: examined
  excerpt: The declared systems edge verbs and three roles are present, interface
    carries systems-interface, and the systems kinds allowed_links use those verbs
    plus realizes_requirement; connection additionally admits carries and crosses.
    The verbs take declared roles or *, and realizes_requirement takes only FR and
    NFR.
- id: tests/test_trust_crossings.py
  path: tests/test_trust_crossings.py
  role: examined
  excerpt: The new crossing test module defines _validate, _relations, and _lines
    helpers.
- id: tests/test_data_flow_edges.py
  path: tests/test_data_flow_edges.py
  role: context_only
  excerpt: Existing data-flow test module already defines _validate, _relations, and
    _lines helpers.
findings:
- fnd: FND-001
  severity: high
  confidence: high
  method: code-review
  check: code-bug
  artifact_id: FR-007-AC-5
  related_ids:
  - TC-104
  path: tests/test_systems_kinds.py
  lines: '262'
  excerpt: The declared systems edge verbs and three roles are present, interface
    carries systems-interface, and the systems kinds allowed_links use those verbs
    plus realizes_requirement; connection additionally admits carries and crosses.
  finding: 'TC-104 fails against the new allowed link: its existing assertion requires
    every target other than connection/carries to be a declared role, but trust_boundary
    is an object kind rather than a role. Reproduced with the locked build wrapper:
    tests/test_systems_kinds.py::test_edge_verbs_and_roles_are_declared_and_used fails
    at line 262 with AssertionError (connection, trust_boundary). Update the allowed-target
    check and declared verb expectations for crosses.'
- fnd: FND-002
  severity: high
  confidence: high
  method: code-review
  check: soundness
  artifact_id: tests/test_trust_crossings.py
  related_ids:
  - tests/test_data_flow_edges.py
  path: tests/test_trust_crossings.py
  lines: 26-49
  excerpt: The new crossing test module defines _validate, _relations, and _lines
    helpers.
  finding: The new tests duplicate _validate, _relations, and _lines from tests/test_data_flow_edges.py.
    The copied helpers have the same behavior (with only the existing module-selection
    option differing) and can drift; generalize/share the existing helpers instead.
bindings: []
```

+++