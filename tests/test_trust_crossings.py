"""Trust-boundary crossing edges on architecture connections (FR-014)."""

from __future__ import annotations

import json

import pytest

from tests.conftest import (
    FIXTURES_DIR,
    PACKAGE_ROOT,
    data_flow_relations,
    diagnostic_lines,
    load_manifest,
    validate_data_flow,
)

CORPUS = FIXTURES_DIR / "data_flow"
VALID = CORPUS / "valid"
INVALID = CORPUS / "invalid"
FORWARD = "connection-crosses-trust-boundary"


@pytest.mark.trace("TC-163", "FR-014-AC-1", "FR-014-AC-6")
def test_manifest_and_skeleton_declare_optional_crosses_relationship():
    manifest = load_manifest()
    assert manifest["edge_types"]["crosses"]["category"] == "dataflow"
    connection = next(
        item for item in manifest["object_types"] if item["name"] == "connection"
    )
    assert connection["allowed_links"]["crosses"] == ["trust_boundary"]
    schema = json.loads((PACKAGE_ROOT / "schemas/Connection.json").read_text())
    assert "crosses" not in json.dumps(schema)
    skeleton = (PACKAGE_ROOT / "skeletons/connection.md").read_text()
    assert 'type: "crosses"' in skeleton and "BOUND-INTERNET" in skeleton


@pytest.mark.trace("TC-164", "FR-014-AC-2", "FR-014-AC-4")
def test_valid_crossing_and_connection_without_crossing_validate():
    result = validate_data_flow(VALID)
    assert result.returncode == 0, result.stderr
    assert not diagnostic_lines(result, "connection-crosses-trust-boundary")
    assert "denial" not in result.stderr.lower()


@pytest.mark.trace("TC-165", "FR-014-AC-3")
def test_crossing_to_asset_and_missing_target_are_rejected():
    result = validate_data_flow(INVALID, "--strict")
    assert result.returncode == 3, result.stderr
    (wrong_kind,) = [
        line
        for line in diagnostic_lines(result, "disallowed-edge-target")
        if "wrong_kind_crossing" in line
    ]
    assert "wrong_kind_crossing" in wrong_kind
    assert "'crosses'" in wrong_kind and "ASSET-NETWORK" in wrong_kind
    assert "'asset'" in wrong_kind
    (dangling,) = [
        line
        for line in diagnostic_lines(result, "dangling-reference")
        if "dangling_crossing" in line
    ]
    assert "BOUND-MISSING" in dangling and "'crosses'" in dangling
    assert any("trust_level" in line for line in result.stderr.splitlines())
    assert any("partly" in line for line in result.stderr.splitlines())


@pytest.mark.trace("TC-166", "FR-014-AC-5", "FR-014-AC-7")
def test_relation_report_includes_trust_level_beside_carried_categories():
    report = data_flow_relations(VALID)
    crossings = report[FORWARD]
    row = next(
        row for row in crossings["rows"] if row["document"]["id"] == "CONN-PORTAL-LAB"
    )
    (boundary,) = row["linked"]
    assert boundary["id"] == "BOUND-INTERNET"
    assert boundary["record"] == {"trust_level": "untrusted"}

    carried = report["connection-carries-classification"]
    carried_row = next(
        row for row in carried["rows"] if row["document"]["id"] == "CONN-PORTAL-LAB"
    )
    health = next(
        entry for entry in carried_row["linked"] if entry["id"] == "CLASS-PHI"
    )
    assert health["record"] == {"regulatedCategories": ["health"]}

    result = validate_data_flow(VALID)
    assert result.returncode == 0, result.stderr
    assert "denial" not in result.stderr.lower()
    assert not diagnostic_lines(result, "connection-crosses-trust-boundary")
