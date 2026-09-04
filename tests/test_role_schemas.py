"""Role-distinctness tests for the ten architecture schemas (FR-004).

Every record below is **hand-built**, not extracted. The extractor populates
`fields`, `clauses`, and `operations` only (quire-rs FR-070/FR-071); the
architecture keys these criteria exercise — `routes`, `delivery`, `carries`,
`versioning`, `registration`, `stability`, `records`, `thresholds`,
`associated_types`, `relations` — have no published Markdown mapping yet
(`agent-ix/quoin#335`). These rows are therefore **schema evidence, not
extraction evidence**, and say so.
"""

from __future__ import annotations

import json

import pytest

from tests.conftest import (
    FIXTURES_DIR,
    MODEL_OF,
    OBJECT_TYPES,
    PROFILE_KEYS,
    SCHEMAS_DIR,
    SEMANTIC_CORE_BASE,
)

MODELS = [MODEL_OF[name] for name in OBJECT_TYPES]

CLAUSE = {"language": "ocl", "clauseId": "SomeInvariant"}
KERNEL = {"target": "String", "multiplicity": {"lower": 1, "upper": 1}}
FIELD = {"name": "a", "type": KERNEL}
IDENTITY_FIELD = {"name": "a", "type": KERNEL, "identity": True}
OP = {"name": "do_it", "params": []}
RETURNING_OP = {"name": "do_it", "params": [], "returns": KERNEL}
GUARANTEED_OP = {"name": "do_it", "params": [], "post": [CLAUSE]}


def valid(registry, model, record) -> bool:
    return registry(model).is_valid(record)


def schema(model: str) -> dict:
    return json.loads((SCHEMAS_DIR / f"{model}.json").read_text())


def rule_signature(model: str) -> tuple:
    """The required / forbidden / item-rule fingerprint FR-004-AC-1 compares."""
    doc = schema(model)
    props = doc.get("properties", {})
    item_rules = {
        key: tuple(
            sorted(
                (facet, json.dumps(value, sort_keys=True))
                for facet, value in spec.items()
                if facet
                in ("minItems", "maxItems", "contains", "minContains", "maxContains")
            )
        )
        for key, spec in props.items()
        if isinstance(spec, dict)
        and any(
            facet in spec
            for facet in (
                "minItems",
                "maxItems",
                "contains",
                "minContains",
                "maxContains",
            )
        )
    }
    return (
        tuple(sorted(doc.get("required", []))),
        tuple(sorted(props)),
        tuple(sorted(item_rules.items())),
    )


@pytest.mark.trace("TC-030", "FR-004-AC-1")
def test_every_schema_is_role_distinct_and_none_is_a_bare_object():
    signatures = {model: rule_signature(model) for model in MODELS}
    for model in MODELS:
        doc = schema(model)
        assert doc.get("properties"), f"{model} declares no property at all"
        assert doc.get("unevaluatedProperties") == {"not": {}}, f"{model} is not sealed"
    for left in MODELS:
        for right in MODELS:
            if left < right:
                assert (
                    signatures[left] != signatures[right]
                ), f"{left} and {right} share one rule fingerprint"


@pytest.mark.trace("TC-031", "FR-004-AC-2")
def test_api_endpoint_requires_an_operation_that_returns(schema_registry):
    assert valid(schema_registry, "ApiEndpoint", {"operations": [RETURNING_OP]})
    assert not valid(schema_registry, "ApiEndpoint", {"operations": [OP]})
    assert not valid(
        schema_registry,
        "ApiEndpoint",
        {"operations": [RETURNING_OP], "fields": [FIELD]},
    )
    assert valid(
        schema_registry,
        "ApiEndpoint",
        {
            "operations": [RETURNING_OP],
            "routes": [{"method": "POST", "path": "/artifacts", "operation": "do_it"}],
            "requires": ["ix://agent-ix/spec-objects-architecture/type/UploadScope"],
        },
    )


@pytest.mark.trace("TC-032", "FR-004-AC-3")
def test_data_schema_requires_fields_and_forbids_operations(schema_registry):
    assert valid(schema_registry, "DataSchema", {"fields": [FIELD]})
    assert not valid(schema_registry, "DataSchema", {"fields": []})
    assert not valid(
        schema_registry, "DataSchema", {"fields": [FIELD], "operations": [OP]}
    )


@pytest.mark.trace("TC-033", "FR-004-AC-4")
def test_queue_requires_a_partition_key_and_forbids_operations(schema_registry):
    """Hand-built: `delivery` and `carries` have no Markdown mapping yet."""
    assert valid(schema_registry, "Queue", {"fields": [IDENTITY_FIELD]})
    assert valid(
        schema_registry,
        "Queue",
        {
            "fields": [IDENTITY_FIELD],
            "delivery": {"semantics": "at_least_once", "ordering": "partition"},
            "carries": ["ix://agent-ix/spec-objects-architecture/type/ArtifactRecord"],
        },
    )
    assert not valid(schema_registry, "Queue", {"fields": [FIELD]})
    assert not valid(
        schema_registry, "Queue", {"fields": [IDENTITY_FIELD], "operations": [OP]}
    )


@pytest.mark.trace("TC-034", "FR-004-AC-5")
def test_action_admits_exactly_one_operation(schema_registry):
    assert valid(schema_registry, "Action", {"operations": [OP]})
    assert not valid(schema_registry, "Action", {"operations": [OP, RETURNING_OP]})
    assert not valid(schema_registry, "Action", {"operations": [OP], "fields": [FIELD]})


@pytest.mark.trace("TC-035", "FR-004-AC-6")
def test_ui_component_admits_no_identity_prop(schema_registry):
    assert valid(schema_registry, "UiComponent", {"fields": [FIELD]})
    assert valid(
        schema_registry, "UiComponent", {"fields": [FIELD], "operations": [OP]}
    )
    assert not valid(schema_registry, "UiComponent", {"fields": [IDENTITY_FIELD]})


@pytest.mark.trace("TC-036", "FR-004-AC-7")
def test_interface_requires_operations_and_forbids_routes(schema_registry):
    """Hand-built: `associated_types` has no Markdown mapping yet."""
    assert valid(schema_registry, "Interface", {"operations": [OP]})
    assert valid(
        schema_registry,
        "Interface",
        {"operations": [OP], "associated_types": [KERNEL]},
    )
    assert not valid(schema_registry, "Interface", {"operations": []})
    assert not valid(
        schema_registry,
        "Interface",
        {
            "operations": [OP],
            "routes": [{"method": "GET", "path": "/x", "operation": "do_it"}],
        },
    )


@pytest.mark.trace("TC-037", "FR-004-AC-8")
def test_external_contract_requires_a_clause_and_a_guaranteed_operation(
    schema_registry,
):
    assert valid(
        schema_registry,
        "ExternalContract",
        {"operations": [GUARANTEED_OP], "clauses": [CLAUSE]},
    )
    assert not valid(
        schema_registry, "ExternalContract", {"operations": [GUARANTEED_OP]}
    )
    assert not valid(
        schema_registry, "ExternalContract", {"operations": [OP], "clauses": [CLAUSE]}
    )
    assert not valid(
        schema_registry,
        "ExternalContract",
        {"operations": [GUARANTEED_OP], "clauses": [CLAUSE], "fields": [FIELD]},
    )


@pytest.mark.trace("TC-038", "FR-004-AC-9")
def test_extension_point_requires_an_operation_and_a_stability_clause(schema_registry):
    """Hand-built: `registration` and `stability` have no Markdown mapping yet."""
    assert valid(
        schema_registry, "ExtensionPoint", {"operations": [OP], "clauses": [CLAUSE]}
    )
    assert valid(
        schema_registry,
        "ExtensionPoint",
        {
            "operations": [OP],
            "clauses": [CLAUSE],
            "registration": {"mechanism": "register", "conflict": "last_wins"},
            "stability": {"compatibility": "major", "deprecation_window": "one major"},
        },
    )
    assert not valid(schema_registry, "ExtensionPoint", {"operations": [OP]})
    assert not valid(
        schema_registry,
        "ExtensionPoint",
        {"operations": [OP], "clauses": [CLAUSE], "fields": [FIELD]},
    )


@pytest.mark.trace("TC-039", "FR-004-AC-10")
def test_binary_format_requires_a_clause_and_well_formed_record_layouts(
    schema_registry,
):
    """Hand-built: `records` and `endianness` have no Markdown mapping yet."""
    layout = {
        "name": "metadata_block",
        "fields": [{"name": "magic", "offset": 0, "size": 4, "type": "u32"}],
    }
    assert valid(schema_registry, "BinaryFormat", {"clauses": [CLAUSE]})
    assert valid(
        schema_registry,
        "BinaryFormat",
        {"clauses": [CLAUSE], "records": [layout], "endianness": "little"},
    )
    empty = {"name": "metadata_block", "fields": []}
    assert not valid(
        schema_registry, "BinaryFormat", {"clauses": [CLAUSE], "records": [empty]}
    )
    assert not valid(
        schema_registry, "BinaryFormat", {"clauses": [CLAUSE], "operations": [OP]}
    )


@pytest.mark.trace("TC-040", "FR-004-AC-11")
def test_rate_limit_requires_a_clause_and_a_scoped_threshold(schema_registry):
    """Hand-built: `thresholds` and `throttles` have no Markdown mapping yet."""
    threshold = {
        "scope": "per_token",
        "metric": "uploads",
        "limit": 60,
        "window": "PT1M",
        "on_exceeded": {"status": 429, "retry_after": True},
    }
    assert valid(schema_registry, "RateLimit", {"clauses": [CLAUSE]})
    assert valid(
        schema_registry, "RateLimit", {"clauses": [CLAUSE], "thresholds": [threshold]}
    )
    bad = dict(threshold, scope="per_universe")
    assert not valid(
        schema_registry, "RateLimit", {"clauses": [CLAUSE], "thresholds": [bad]}
    )
    assert not valid(
        schema_registry, "RateLimit", {"clauses": [CLAUSE], "fields": [FIELD]}
    )


@pytest.mark.trace("TC-041", "FR-004-AC-12", "FR-004-CON-2")
def test_the_empty_record_fails_every_one_of_the_ten_types(schema_registry):
    for model in MODELS:
        assert not valid(schema_registry, model, {}), f"{model} accepted `{{}}`"


@pytest.mark.trace("TC-042", "FR-004-AC-13")
def test_the_extractor_reports_an_unresolvable_token_as_unresolved_type(
    quire_engine, semantic_module, bundle_index
):
    """The extractor half of FR-004-AC-13, asserted under this criterion's own
    row rather than borrowed from FR-006-AC-5: a token no declaration carries
    is reported as `semantic.unresolved-type` and placed under the module's
    `unresolved/` namespace."""
    path = FIXTURES_DIR / "api_endpoint-unresolved-return.md"
    record = quire_engine.extract_semantic(
        {
            "markdown": path.read_text(),
            "module": semantic_module,
            "path": str(path),
            "sourceIdentity": "ix://agent-ix/spec-objects-architecture/unresolved-001",
            "bundle": bundle_index,
        }
    )
    findings = [
        d
        for d in record.get("diagnostics", [])
        if d.get("code") == "semantic.unresolved-type"
    ]
    assert len(findings) == 1, record.get("diagnostics")
    assert "MysteryRecord" in findings[0]["message"]
    assert record["operations"][0]["returns"]["target"].startswith(
        "ix://agent-ix/spec-objects-architecture/unresolved/"
    )


@pytest.mark.trace("TC-042", "FR-004-AC-13")
def test_an_unresolved_placeholder_target_is_a_semantic_id_and_a_bare_token_is_not(
    schema_registry,
):
    placeholder = {
        "name": "a",
        "type": {
            "target": "ix://agent-ix/spec-objects-architecture/unresolved/Mystery",
            "multiplicity": {"lower": 1, "upper": 1},
        },
    }
    assert valid(schema_registry, "DataSchema", {"fields": [placeholder]})
    bare = {
        "name": "a",
        "type": {"target": "Mystery", "multiplicity": {"lower": 1, "upper": 1}},
    }
    assert not valid(schema_registry, "DataSchema", {"fields": [bare]})


@pytest.mark.trace("TC-043", "FR-004-AC-14", "FR-004-CON-3")
def test_no_profile_key_is_required_and_dropping_one_keeps_the_record_valid(
    schema_registry,
):
    for model in MODELS:
        required = set(schema(model).get("required", []))
        assert not (
            required & set(PROFILE_KEYS)
        ), f"{model} requires a protocol profile key"
    cases = [
        (
            "Queue",
            {"fields": [IDENTITY_FIELD]},
            {"delivery": {"semantics": "exactly_once"}},
        ),
        (
            "ExternalContract",
            {"operations": [GUARANTEED_OP], "clauses": [CLAUSE]},
            {"versioning": {"scheme": "semver"}},
        ),
        (
            "ExtensionPoint",
            {"operations": [OP], "clauses": [CLAUSE]},
            {
                "registration": {"mechanism": "register", "conflict": "error"},
                "stability": {"compatibility": "minor"},
            },
        ),
        ("BinaryFormat", {"clauses": [CLAUSE]}, {"endianness": "big"}),
    ]
    for model, core, profile in cases:
        assert valid(schema_registry, model, {**core, **profile}), model
        assert valid(schema_registry, model, core), model


@pytest.mark.trace("TC-044", "FR-004-CON-1")
def test_no_module_schema_redeclares_a_semantic_core_model(schema_registry):
    grammar_keys = {
        "fields": "FieldDecl.json",
        "params": "FieldDecl.json",
        "clauses": "ClauseRef.json",
        "operations": "OperationDecl.json",
        "relations": "RelationDecl.json",
        "associated_types": "TypeRef.json",
    }
    for model in MODELS:
        props = schema(model).get("properties", {})
        for key, target in grammar_keys.items():
            if key not in props:
                continue
            spec = props[key]
            ref = (spec.get("items") or spec).get("$ref")
            assert (
                ref == f"{SEMANTIC_CORE_BASE}{target}"
            ), f"{model}.{key} does not $ref semantic-core {target} (got {ref})"


@pytest.mark.trace("TC-007", "StR-001-VC-3")
def test_an_api_endpoint_and_a_rate_limit_record_are_distinguishable_by_schema_alone(
    schema_registry,
):
    endpoint = {"operations": [RETURNING_OP]}
    limit = {"clauses": [CLAUSE]}
    assert valid(schema_registry, "ApiEndpoint", endpoint)
    assert not valid(schema_registry, "RateLimit", endpoint)
    assert valid(schema_registry, "RateLimit", limit)
    assert not valid(schema_registry, "ApiEndpoint", limit)


#: Key-name shapes that would mark a record as an *observation* of running code
#: rather than a declaration. The ticket's second acceptance criterion, and the
#: Project 17 resource-vocabulary alignment, reduce to keeping these out.
OBSERVATION_MARKERS = (
    "observed",
    "discovered",
    "measured",
    "runtime",
    "actual",
    "sampled",
    "detected",
    "instance",
    "call_count",
    "hit_count",
    "last_seen",
    "resource_id",
    "trace_id",
    "span_id",
)


@pytest.mark.trace("TC-045", "FR-004-AC-15")
def test_no_shipped_schema_declares_an_observation_key():
    """The ticket's "definition objects remain distinct from observed routes,
    calls, queues, and runtime resources", made checkable: a declaration record
    carries no key that names an observation, so it can never be read as an
    extraction from running code. This is also the Project 17 alignment — the
    module contributes declaration vocabulary and takes none of the measured
    extraction vocabulary for itself."""
    offenders = []
    for path in sorted(SCHEMAS_DIR.glob("*.json")):
        if path.name == "toolchain.json":
            continue
        doc = json.loads(path.read_text())
        for key in doc.get("properties", {}):
            lowered = key.lower()
            for marker in OBSERVATION_MARKERS:
                if marker in lowered:
                    offenders.append(f"{path.name}.{key} (matches {marker!r})")
    assert offenders == [], offenders


@pytest.mark.trace("TC-046", "FR-004-AC-16")
def test_relations_is_admitted_by_six_types_and_refused_by_four(schema_registry):
    """FR-004 admits `relations` where a type is reached through an edge and
    refuses it on the four reached through what they carry, expose, serialize or
    throttle. Both halves are asserted, so the Behavior rule and the table
    cannot drift apart again."""
    admits = {
        "ApiEndpoint": {"operations": [RETURNING_OP]},
        "DataSchema": {"fields": [FIELD]},
        "Action": {"operations": [OP]},
        "UiComponent": {"fields": [FIELD]},
        "Interface": {"operations": [OP]},
        "ExternalContract": {"operations": [GUARANTEED_OP], "clauses": [CLAUSE]},
    }
    refuses = {
        "Queue": {"fields": [IDENTITY_FIELD]},
        "ExtensionPoint": {"operations": [OP], "clauses": [CLAUSE]},
        "BinaryFormat": {"clauses": [CLAUSE]},
        "RateLimit": {"clauses": [CLAUSE]},
    }
    assert set(admits) | set(refuses) == set(MODELS)
    relation = {
        "verb": "contains",
        "category": "structural",
        "target": "ix://agent-ix/spec-objects-architecture/type/ArtifactRecord",
    }
    for model, core in admits.items():
        assert valid(schema_registry, model, core), model
        assert valid(schema_registry, model, {**core, "relations": [relation]}), model
    for model, core in refuses.items():
        assert valid(schema_registry, model, core), model
        assert not valid(
            schema_registry, model, {**core, "relations": [relation]}
        ), model
