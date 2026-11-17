"""Data sink declarations, delivery edges and relation reports (PLAT-1535)."""

from __future__ import annotations

import json
import shutil

import pytest
import yaml

from tests.conftest import (
    FIXTURES_DIR,
    SCHEMAS_DIR,
    data_flow_relations,
    diagnostic_lines,
    load_manifest,
    object_type,
    run_quire,
    validate_data_flow,
)

CORPUS = FIXTURES_DIR / "data_flow_sinks"
VALID = CORPUS / "valid"
INVALID = CORPUS / "invalid"
SINK_KINDS = (
    "ui_screen",
    "log",
    "export_file",
    "analytics_event",
    "llm_prompt",
    "tool_call",
    "outbound_message",
    "datastore",
)
PROCESSOR_AGREEMENTS = ("covered", "not_covered", "not_applicable", "unknown")


@pytest.mark.trace("TC-167", "FR-015-AC-1", "FR-015-AC-2")
def test_every_sink_kind_and_valid_region_validate():
    result = validate_data_flow(VALID)
    assert result.returncode == 0, result.stderr
    for kind in SINK_KINDS:
        assert any(
            f"kind: {kind}" in path.read_text()
            for path in (VALID / "spec/design/sinks").glob("SINK-*.md")
        ), kind


@pytest.mark.trace("TC-168", "FR-015-AC-1", "FR-015-AC-2")
def test_invalid_kind_agreement_and_region_name_the_bad_frontmatter():
    result = validate_data_flow(INVALID, "--strict")
    assert result.returncode == 3, result.stderr
    for name, value in (
        ("SINK-BAD-KIND", "chatbot"),
        ("SINK-MISSING-AGREEMENT", "processor_agreement"),
        ("SINK-BAD-AGREEMENT", "yes"),
        ("SINK-BAD-REGION", "Germany"),
    ):
        assert name in result.stderr, result.stderr
        assert value in result.stderr, result.stderr


@pytest.mark.trace("TC-169", "FR-015-AC-3", "FR-015-AC-4", "FR-015-AC-5")
def test_delivers_to_and_carries_validate_and_refuse_wrong_or_dangling_targets():
    valid = validate_data_flow(VALID)
    assert valid.returncode == 0, valid.stderr

    invalid = validate_data_flow(INVALID, "--strict")
    assert invalid.returncode == 3, invalid.stderr
    edge_errors = diagnostic_lines(invalid, "disallowed-edge-target")
    wrong_delivery = [line for line in edge_errors if "CONN-WRONG-DELIVERY" in line]
    wrong_carries = [line for line in edge_errors if "SINK-WRONG-CARRIES" in line]
    assert len(wrong_delivery) == 1, invalid.stderr
    assert "delivers_to" in wrong_delivery[0] and "'part'" in wrong_delivery[0]
    assert len(wrong_carries) == 1, invalid.stderr
    assert "carries" in wrong_carries[0] and "'queue'" in wrong_carries[0]
    dangling = diagnostic_lines(invalid, "dangling-reference")
    assert any(
        "CONN-DANGLING-DELIVERY" in line and "SINK-MISSING" in line for line in dangling
    )


@pytest.mark.trace("TC-170", "FR-015-AC-6")
def test_relation_report_includes_each_sink_kind_and_authored_processor():
    reports = data_flow_relations(VALID)
    expected = {
        "connection-delivers-to-sink": (
            "CONN-DELIVERS",
            {
                "SINK-UI-SCREEN": "ui_screen",
                "SINK-LOG": "log",
                "SINK-EXPORT": "export_file",
                "SINK-ANALYTICS": "analytics_event",
            },
        ),
        "part-delivers-to-sink": (
            "PART-DELIVERS",
            {
                "SINK-LLM-PROMPT": "llm_prompt",
                "SINK-TOOL-CALL": "tool_call",
                "SINK-MESSAGE": "outbound_message",
                "SINK-DATASTORE": "datastore",
            },
        ),
    }
    for relation, (source_id, sinks) in expected.items():
        rows = reports[relation]["rows"]
        row = next((row for row in rows if row["document"]["id"] == source_id), None)
        assert row is not None, rows
        linked = {entry["id"]: entry for entry in row["linked"]}
        assert set(linked) == set(sinks)
        for sink_id, kind in sinks.items():
            assert linked[sink_id]["record"]["kind"] == kind
            assert "processorAgreement" in linked[sink_id]["record"]

    prompt = next(
        entry
        for row in reports["part-delivers-to-sink"]["rows"]
        for entry in row["linked"]
        if entry["id"] == "SINK-LLM-PROMPT"
    )
    tool_call = next(
        entry
        for row in reports["part-delivers-to-sink"]["rows"]
        for entry in row["linked"]
        if entry["id"] == "SINK-TOOL-CALL"
    )
    assert prompt["record"]["processor"] == "EXT-MODEL-PROVIDER"
    assert tool_call["record"]["processor"] == "PART-SINK-PROCESSOR"


@pytest.mark.trace("TC-171", "FR-015-AC-2", "FR-015-AC-12")
def test_data_sink_record_schema_is_closed_and_uses_the_declared_vocabularies(
    schema_registry,
):
    # schema_registry supplies the semantic-core resources for $refs.
    schema = json.loads((SCHEMAS_DIR / "DataSink.json").read_text())
    assert schema["unevaluatedProperties"] == {"not": {}}
    validator = schema_registry("DataSink")
    base = {"kind": "llm_prompt", "processorAgreement": "not_covered"}
    assert validator.is_valid(base)
    assert validator.is_valid(
        {
            **base,
            "processor": "EXT-MODEL-PROVIDER",
            "region": ["DE", "eu"],
            "purpose": ["triage-summary"],
            "audienceRoles": ["triage-agent"],
        }
    )
    for invalid in (
        {**base, "kind": "chatbot"},
        {**base, "processorAgreement": "yes"},
        {**base, "region": ["Germany"]},
        {**base, "purpose": [""]},
        {**base, "purpose": ["   "]},
        {**base, "unknown": True},
    ):
        assert not validator.is_valid(invalid), invalid


@pytest.mark.trace("TC-173", "FR-015-AC-1", "FR-015-AC-2")
def test_data_sink_frontmatter_schema_is_open_and_uses_closed_rule_vocabularies(
    schema_registry,
):
    """Frontmatter keeps optional typed fields open and exposes closed enums.

    Assumptions:
        - The schemas were generated from the TypeSpec source.
        - The schema registry resolves module-local enum references.

    Criteria:
        - Every declared sink kind and agreement value validates.
        - Values outside either enum fail validation.
        - Optional processor, audience_roles, region, and purpose fields accept
          authored values without requiring referenced documents.
        - Additional frontmatter fields remain allowed.
    """
    schema = json.loads((SCHEMAS_DIR / "DataSinkFrontmatter.json").read_text())
    assert schema["unevaluatedProperties"] == {}
    for field in ("processor", "audience_roles", "region", "purpose"):
        assert "$ref" not in schema["properties"][field], field
    assert (
        schema["properties"]["kind"]["enum"]
        == json.loads((SCHEMAS_DIR / "SinkKind.json").read_text())["enum"]
    )
    assert (
        schema["properties"]["processor_agreement"]["enum"]
        == json.loads((SCHEMAS_DIR / "ProcessorAgreement.json").read_text())["enum"]
    )
    validator = schema_registry("DataSinkFrontmatter")
    for kind in SINK_KINDS:
        assert validator.is_valid(
            {"kind": kind, "processor_agreement": "covered", "id": "SINK-1"}
        ), kind
    for agreement in PROCESSOR_AGREEMENTS:
        assert validator.is_valid(
            {"kind": "llm_prompt", "processor_agreement": agreement}
        ), agreement
    assert not validator.is_valid({"kind": "chatbot", "processor_agreement": "covered"})
    assert not validator.is_valid({"kind": "llm_prompt", "processor_agreement": "yes"})

    sink_facts = {
        "kind": "llm_prompt",
        "processor_agreement": "not_covered",
        "processor": "EXT-MODEL-PROVIDER",
        "audience_roles": ["triage-agent"],
        "region": ["US", "eea"],
        "purpose": ["triage-summary"],
    }
    assert validator.is_valid(sink_facts)
    assert validator.is_valid({"kind": "log", "processor_agreement": "not_applicable"})
    for invalid in (
        {**sink_facts, "processor": "bad id"},
        {**sink_facts, "audience_roles": [""]},
        {**sink_facts, "region": ["Germany"]},
        {**sink_facts, "purpose": ["   "]},
        {"processor": "EXT-MODEL-PROVIDER", "processor_agreement": "covered"},
        {"kind": "llm_prompt"},
    ):
        assert not validator.is_valid(invalid), invalid


@pytest.mark.trace("TC-174", "FR-015-AC-8")
def test_flow_rule_loader_resolves_sink_frontmatter_enums(tmp_path):
    """Flow-rule conditions load against sink enums and reject unknown values.

    Assumptions:
        - The installed Quire engine validates flow-rule declarations at load.
        - A module test root reuses the generated frontmatter schema.

    Criteria:
        - Conditions covering every sink kind and agreement value load.
        - An out-of-enum condition value rejects the module and names its value.
    """
    corpus = tmp_path / "corpus"
    documents = corpus / "spec"
    documents.mkdir(parents=True)
    (documents / "sink.md").write_text(
        "---\nid: SINK-1\ntitle: Sink\ntype: data_sink\n"
        "kind: llm_prompt\nprocessor_agreement: covered\n---\n# Sink\n"
    )

    valid_module = tmp_path / "valid-module"
    invalid_module = tmp_path / "invalid-module"
    for root, invalid in ((valid_module, False), (invalid_module, True)):
        schemas = root / "schemas"
        schemas.mkdir(parents=True)
        shutil.copyfile(
            SCHEMAS_DIR / "DataSinkFrontmatter.json",
            schemas / "DataSinkFrontmatter.json",
        )
        agreements = list(PROCESSOR_AGREEMENTS)
        if invalid:
            agreements[-1] = "medical"
        manifest = {
            "name": "data-sink-flow-rule-test",
            "version": "0.1.0",
            "description": "Test the sink frontmatter vocabularies.",
            "archetypes": [
                {
                    "name": "data_sink",
                    "frontmatter_schema_ref": "schemas/DataSinkFrontmatter.json",
                }
            ],
            "traceability": {
                "flow_rules": [
                    {
                        "name": "data-sink-frontmatter-enum-test",
                        "subject": ["data_sink"],
                        "match": [
                            {
                                "path": [],
                                "field": "kind",
                                "any_of": list(SINK_KINDS),
                            },
                            {
                                "path": [],
                                "field": "processor_agreement",
                                "any_of": agreements,
                            },
                        ],
                        "check": "data-sink-frontmatter-enum-test",
                        "rationale": "The test checks the declared sink vocabularies.",
                    }
                ]
            },
        }
        (root / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))

    valid = run_quire(
        "relations",
        "--flow",
        "--json",
        "--module",
        str(valid_module),
        "--repo",
        f"agent-ix/df={corpus}",
    )
    assert valid.returncode == 0, valid.stderr

    invalid = run_quire(
        "relations",
        "--flow",
        "--json",
        "--module",
        str(invalid_module),
        "--repo",
        f"agent-ix/df={corpus}",
    )
    assert invalid.returncode != 0, invalid.stderr
    assert "flow_rules" in invalid.stderr, invalid.stderr


@pytest.mark.trace("TC-172", "FR-015-AC-5", "FR-015-AC-12")
def test_data_sink_is_exported_and_declares_only_the_supported_links():
    manifest = load_manifest()
    assert "data_sink" in manifest["semantic"]["exports"]
    sink = object_type("data_sink")
    assert sink["frontmatter_schema_ref"] == "schemas/DataSinkFrontmatter.json"
    assert sink["allowed_links"] == {
        "carries": ["data_classification"],
        "references": ["part", "external_contract", "role"],
    }
    assert object_type("connection")["allowed_links"]["delivers_to"] == ["data_sink"]
    assert object_type("part")["allowed_links"]["delivers_to"] == ["data_sink"]
    assert manifest["edge_types"]["delivers_to"]["category"] == "dataflow"
