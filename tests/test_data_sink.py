"""Data sink declarations, delivery edges and relation reports (PLAT-1535)."""

from __future__ import annotations

import json

import pytest

from tests.conftest import (
    FIXTURES_DIR,
    SCHEMAS_DIR,
    data_flow_relations,
    diagnostic_lines,
    load_manifest,
    object_type,
    validate_data_flow,
)

CORPUS = FIXTURES_DIR / "data_flow"
VALID = CORPUS / "valid"
INVALID_SINKS = CORPUS / "invalid/spec/design/sinks"
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


@pytest.mark.trace("TC-160", "FR-015-AC-1", "FR-015-AC-2", "FR-015-AC-3")
def test_every_sink_kind_and_valid_region_validate():
    result = validate_data_flow(VALID)
    assert result.returncode == 0, result.stderr
    for kind in SINK_KINDS:
        assert any(
            f"kind: {kind}" in path.read_text()
            for path in (VALID / "spec/design/sinks").glob("SINK-*.md")
        ), kind


@pytest.mark.trace("TC-161", "FR-015-AC-1", "FR-015-AC-2", "FR-015-AC-3")
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


@pytest.mark.trace("TC-162", "FR-015-AC-4", "FR-015-AC-5")
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
        "CONN-DANGLING-DELIVERY" in line and "SINK-MISSING" in line
        for line in dangling
    )


@pytest.mark.trace("TC-163", "FR-015-AC-6", "FR-015-AC-8")
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
        row = next(
            (row for row in rows if row["document"]["id"] == source_id), None
        )
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


@pytest.mark.trace("TC-164", "FR-015-AC-7")
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
        {**base, "unknown": True},
    ):
        assert not validator.is_valid(invalid), invalid


@pytest.mark.trace("TC-165", "FR-015-AC-7")
def test_data_sink_is_exported_and_declares_only_the_supported_links():
    manifest = load_manifest()
    assert "data_sink" in manifest["semantic"]["exports"]
    sink = object_type("data_sink")
    assert "frontmatter_schema_ref" not in sink
    assert sink["allowed_links"] == {
        "carries": ["data_classification"],
        "references": ["part", "external_contract", "role"],
    }
    assert object_type("connection")["allowed_links"]["delivers_to"] == ["data_sink"]
    assert object_type("part")["allowed_links"]["delivers_to"] == ["data_sink"]
    assert manifest["edge_types"]["delivers_to"]["category"] == "dataflow"

