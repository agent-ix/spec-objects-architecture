"""Record-key section tests (FR-008).

Unlike the hand-built records of `test_role_schemas.py`, every record below is
**extracted** from authored Markdown by the engine's `record-sections` mapping
(quoin FR-121 and FR-122) and then validated against the module's own emitted
schemas, so each row is extraction evidence for the key it names.
"""

from __future__ import annotations

import json

import pytest

from tests.conftest import (
    SKELETONS_DIR,
    frontmatter,
    load_manifest,
    object_type,
)

PACKAGE = "agent-ix/spec-objects-architecture"
ID_PREFIX = f"ix://{PACKAGE}/"

#: Per skeleton: each record key it authors, the model that validates one value
#: of the key (`[]` when the key is an array), and whether the model is core.
SKELETON_KEYS = {
    "api_endpoint": {"routes": ("RouteDecl", True, False)},
    "queue": {"delivery": ("DeliveryPolicy", False, False)},
    "external_contract": {
        "provider": ("SemanticId", False, True),
        "versioning": ("VersioningPolicy", False, False),
    },
    "extension_point": {
        "exposes": ("SemanticId", False, True),
        "registration": ("RegistrationPolicy", False, False),
        "stability": ("StabilityPolicy", False, False),
    },
    "interface": {"associated_types": ("TypeRef", True, True)},
    "binary_format": {
        "records": ("RecordLayout", True, False),
        "endianness": ("Endianness", False, False),
    },
    "rate_limit": {"thresholds": ("Threshold", True, False)},
}

MODEL_OF = {
    "api_endpoint": "ApiEndpoint",
    "queue": "Queue",
    "external_contract": "ExternalContract",
    "extension_point": "ExtensionPoint",
    "interface": "Interface",
    "binary_format": "BinaryFormat",
    "rate_limit": "RateLimit",
}


def extract(quire_engine, schema_documents, markdown, kind, bundle=None, **extra):
    """Extract `markdown` as `kind` under the manifest's own mappings, reading
    record keys against the module's emitted schema."""
    manifest = load_manifest()
    name = MODEL_OF.get(kind) or "".join(p.title() for p in kind.split("_"))
    schema = next(
        s
        for s in schema_documents.values()
        if s["$id"].endswith(f"/spec-objects-architecture/{name}.json")
    )
    request = {
        "markdown": markdown,
        "module": {
            "contractVersion": manifest["semantic"]["contract_version"],
            "package": PACKAGE,
            "exports": [kind],
            "mappings": manifest["semantic"]["mappings"],
        },
        "path": f"{kind}.md",
        "sourceIdentity": f"{ID_PREFIX}{frontmatter(markdown)['id']}",
        "bundle": bundle or {"package": PACKAGE},
        "dataSchema": schema,
        "schemaDocuments": schema_documents,
        "objectType": kind,
        "bodyExtraction": object_type(kind)["body_extraction"],
        **extra,
    }
    return quire_engine.extract_semantic(request)


def errors(result) -> list[dict]:
    return [d for d in result.get("diagnostics", []) if d["severity"] == "error"]


def doc(kind: str, body: str) -> str:
    return (
        f"---\nid: probe_001\ntitle: Probe\ntype: {kind}\nobject: {kind}\n---\n"
        f"# [probe_001] Probe\n\n{body}"
    )


@pytest.mark.trace("TC-120", "FR-008-AC-1")
def test_the_manifest_names_the_relationships_and_record_sections_tokens(
    semantic_block,
):
    assert "relationships" in semantic_block["mappings"]
    assert "record-sections" in semantic_block["mappings"]


@pytest.mark.trace("TC-121", "FR-008-AC-2")
@pytest.mark.parametrize("kind", sorted(SKELETON_KEYS))
def test_each_skeleton_authors_its_record_keys_and_they_validate(
    quire_engine, schema_documents, schema_registry, bundle_index, kind
):
    text = (SKELETONS_DIR / f"{kind}.md").read_text()
    result = extract(quire_engine, schema_documents, text, kind, bundle_index)
    assert not errors(result), errors(result)
    record = result["record"]
    assert set(record) == set(SKELETON_KEYS[kind]), (kind, set(record))
    keys = result["availability"]["recordKeys"]
    for key, (model, is_array, core) in SKELETON_KEYS[kind].items():
        assert keys[key]["state"] == "available", (kind, key, keys[key])
        validator = schema_registry(model, core=core)
        values = record[key] if is_array else [record[key]]
        assert values, (kind, key)
        for value in values:
            assert validator.is_valid(value), (kind, key, value)


@pytest.mark.trace("TC-121", "FR-008-AC-2")
def test_the_authored_skeleton_values_are_the_ones_the_skeletons_state(
    quire_engine, schema_documents, bundle_index
):
    def record(kind):
        text = (SKELETONS_DIR / f"{kind}.md").read_text()
        return extract(quire_engine, schema_documents, text, kind, bundle_index)[
            "record"
        ]

    assert record("external_contract")["provider"] == f"{ID_PREFIX}api_endpoint_001"
    assert record("extension_point")["exposes"] == f"{ID_PREFIX}quant_codec"
    assert record("extension_point")["registration"] == {
        "mechanism": "module_init",
        "conflict": "last_wins",
        "discovery": "unregistered types fall back to the generic payload renderer",
    }
    assert [r["operation"] for r in record("api_endpoint")["routes"]] == [
        "upload_artifact",
        "get_artifact",
        "stream_artifact_content",
    ]
    assert record("rate_limit")["thresholds"][2]["on_exceeded"] == {
        "status": 503,
        "retry_after": False,
        "behavior": "the gateway sheds load",
    }


@pytest.mark.trace("TC-122", "FR-008-AC-3")
def test_a_route_naming_an_undeclared_operation_is_refused(
    quire_engine, schema_documents
):
    body = (
        "## Operations\n\n### getThing\n\nReturns: String[1]\n\n"
        "## Routes\n\n| Method | Path | Operation |\n|---|---|---|\n"
        "| GET | /things/{id} | getThing |\n| POST | /things | createThing |\n"
    )
    result = extract(
        quire_engine, schema_documents, doc("api_endpoint", body), "api_endpoint"
    )
    refused = [d for d in errors(result) if d["code"] == "semantic.invalid-model-cell"]
    assert [d["reason"] for d in refused] == ["route-operation-unknown"]
    assert "record" not in result
    assert result["availability"]["recordKeys"]["routes"]["state"] == "unavailable"


@pytest.mark.trace("TC-123", "FR-008-AC-4")
def test_associated_types_come_from_the_table_and_never_from_the_contract_fence(
    quire_engine, schema_documents
):
    fence = "## Contract\n\n```yaml\nassociated_types:\n  - Money\n```\n"
    table = (
        "## Associated Types\n\n| Type | Multiplicity |\n|---|---|\n"
        "| String | 1 |\n| Integer | 0..* |\n\n"
    )
    fence_only = extract(
        quire_engine, schema_documents, doc("interface", fence), "interface"
    )
    assert "record" not in fence_only
    assert (
        fence_only["availability"]["recordKeys"]["associated_types"]["state"]
        == "not_applicable"
    )

    both = extract(
        quire_engine, schema_documents, doc("interface", table + fence), "interface"
    )
    assert not errors(both), errors(both)
    assert [t["target"]["value"] for t in both["record"]["associated_types"]] == [
        "String",
        "Integer",
    ]


LAYOUT = """## Layout

```yaml
format: segment-v1
magic: "QSEG"
endianness: little
record_types:
  - name: metadata_block
    tag: 0x21
    size: 16
    fields:
      - {{name: payload_len, offset: 0, size: 4, type: u32}}
  - name: posting_tuple
    fields:
      - {{name: doc_id, offset: 0, size: 8, type: u64}}
      {extra}
      - {{name: payload, offset: 8, size: {size}, type: bytes}}
```
"""


@pytest.mark.trace("TC-124", "FR-008-AC-5")
def test_the_layout_fence_lowers_to_records_and_endianness(
    quire_engine, schema_documents, bundle_index
):
    skeleton = (SKELETONS_DIR / "binary_format.md").read_text()
    record = extract(
        quire_engine, schema_documents, skeleton, "binary_format", bundle_index
    )["record"]
    assert record["endianness"] == "little"
    assert [r["name"] for r in record["records"]] == ["metadata_block", "posting_tuple"]
    assert record["records"][1]["tag"] == "0x21"
    posting = record["records"][1]["fields"]
    assert posting[2] == {
        "name": "payload",
        "offset": 7,
        "size": "payload_len",
        "type": "bytes",
    }
    assert all("magic" not in r for r in record["records"])


@pytest.mark.trace("TC-124", "FR-008-AC-5")
def test_a_layout_size_must_name_exactly_one_field_in_the_fence(
    quire_engine, schema_documents
):
    def reasons(size, extra=""):
        body = LAYOUT.format(size=size, extra=extra) + "\n## Endianness\n\n`big`\n"
        result = extract(
            quire_engine, schema_documents, doc("binary_format", body), "binary_format"
        )
        return result, [d["reason"] for d in errors(result)]

    ok, found = reasons("payload_len")
    assert found == []
    assert ok["record"]["endianness"] == "little"  # `## Endianness` is prose
    assert reasons("nowhere")[1] == ["size-unknown-field"]
    duplicate = "- {name: payload_len, offset: 99, size: 4, type: u32}"
    assert reasons("payload_len", duplicate)[1] == ["size-ambiguous"]


@pytest.mark.trace("TC-125", "FR-008-AC-6")
def test_a_threshold_without_a_status_is_refused_and_a_bullet_list_is_not_a_table(
    quire_engine, schema_documents
):
    head = "| Scope | Metric | Limit | Window | Status | Retry After | Behavior |\n"
    rule = "|---|---|---|---|---|---|---|\n"
    ok = extract(
        quire_engine,
        schema_documents,
        doc(
            "rate_limit",
            "## Thresholds\n\n"
            + head
            + rule
            + "| per_token | requests | 60 | 1m | 429 | true | |\n",
        ),
        "rate_limit",
    )
    assert ok["record"]["thresholds"] == [
        {
            "scope": "per_token",
            "metric": "requests",
            "limit": 60,
            "window": "1m",
            "on_exceeded": {"status": 429, "retry_after": True},
        }
    ]
    missing = extract(
        quire_engine,
        schema_documents,
        doc(
            "rate_limit",
            "## Thresholds\n\n"
            + head
            + rule
            + "| per_token | requests | 60 | 1m |  | true | |\n",
        ),
        "rate_limit",
    )
    assert [d["reason"] for d in errors(missing)] == ["status-required"]

    bullets = extract(
        quire_engine,
        schema_documents,
        doc("extension_point", "## Registration\n\n- Mechanism: entry_point\n"),
        "extension_point",
    )
    assert [(d["code"], d["reason"]) for d in errors(bullets)] == [
        ("semantic.feature-not-extractable", "registration")
    ]


@pytest.mark.trace("TC-126", "FR-008-AC-7")
def test_a_typed_relation_comes_from_a_relationships_row_and_not_a_requires_list(
    quire_engine, schema_documents
):
    manifest = load_manifest()
    types = {ot["name"]: ot for ot in manifest["object_types"]}
    body = (
        "## Relationships\n\n| Name | Verb | Target | Multiplicity |\n"
        "|---|---|---|---|\n| needs | requires | perm_001 | 1..1 |\n\n"
        "## Requires\n\n- other_001\n"
    )
    result = extract(
        quire_engine,
        schema_documents,
        doc("api_endpoint", body),
        "api_endpoint",
        bundle={
            "package": PACKAGE,
            "artifacts": [{"id": "perm_001", "object": "permission", "operations": []}],
        },
        relationVocabulary={
            "objectType": "api_endpoint",
            # `requires` is declared by spec-artifacts-iso, not by this module.
            "edgeTypes": {"requires": {"category": "dependency"}},
            "roles": {"permission": [], "api_endpoint": []},
            "allowedLinks": {"api_endpoint": types["api_endpoint"]["allowed_links"]},
        },
    )
    assert not errors(result), errors(result)
    assert result["requires"] == [f"{ID_PREFIX}perm_001"]
    assert not [d for d in result["diagnostics"] if "Requires" in json.dumps(d)]
