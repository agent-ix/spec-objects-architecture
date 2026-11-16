"""Connection data classification (FR-013): `carries` from a connection to a
`data_classification`, and the two opt-in completeness relations.

Every row runs the `quire` binary over `tests/fixtures/data_flow` with this
module loaded beside spec-artifacts-iso, spec-artifacts-process and
spec-objects-security (the owner of `data_classification`).

The manifest's `record_keys` projection needs an engine that supports it
(quire-rs 0.61.0 or later); the `regulated_categories` vocabulary comes from
spec-objects-security.
"""

from __future__ import annotations

import json

import pytest

from tests.conftest import (
    FIXTURES_DIR,
    PACKAGE_ROOT,
    data_flow_relations,
    diagnostic_lines,
    load_manifest,
    object_type,
    validate_data_flow,
)

CORPUS = FIXTURES_DIR / "data_flow"
VALID = CORPUS / "valid"
INVALID = CORPUS / "invalid"
FORWARD = "connection-carries-classification"
REVERSE = "classification-carried-by-connection"


def _pairs(report: dict, name: str) -> set[tuple[str, str]]:
    return {
        (row["document"]["id"], linked["id"])
        for row in report[name]["rows"]
        for linked in row["linked"]
    }


def _rows(report: dict, name: str) -> dict[str, dict]:
    return {row["document"]["id"]: row for row in report[name]["rows"]}


@pytest.mark.trace("TC-151", "FR-013-AC-1")
def test_fr013_ac1_connection_carrying_a_classification_validates():
    result = validate_data_flow(VALID, safety=True)
    assert result.returncode == 0, result.stderr
    assert "disallowed-edge" not in result.stderr


@pytest.mark.trace("TC-152", "FR-013-AC-2")
def test_fr013_ac2_wrong_kind_and_dangling_targets_fail():
    result = validate_data_flow(INVALID, "--strict", safety=True)
    assert result.returncode == 3, result.stderr
    (wrong,) = [
        line
        for line in diagnostic_lines(result, "disallowed-edge-target")
        if "wrong_kind_link" in line
    ]
    assert "wrong_kind_link" in wrong and "'carries'" in wrong
    assert "scoring_engine" in wrong and "'part'" in wrong
    (dangling,) = [
        line
        for line in diagnostic_lines(result, "dangling-reference")
        if "dangling_link.md" in line
    ]
    assert "dangling_link.md" in dangling
    assert "CLASS-MISSING" in dangling and "'carries'" in dangling


@pytest.mark.trace("TC-153", "FR-013-AC-3")
def test_fr013_ac3_opted_in_checks_report_the_gaps():
    result = validate_data_flow(
        VALID,
        "--severity",
        "trace:connection-without-classification=warning",
        "--severity",
        "trace:classification-without-connection=warning",
        safety=True,
    )
    assert result.returncode == 0, result.stderr
    (conn,) = diagnostic_lines(result, "connection-without-classification")
    assert "bare_link" in conn
    (cls,) = diagnostic_lines(result, "classification-without-connection")
    assert "CLASS-UNCARRIED" in cls


@pytest.mark.trace("TC-154", "FR-013-AC-4")
def test_fr013_ac4_default_severity_draws_no_finding():
    result = validate_data_flow(VALID, safety=True)
    assert result.returncode == 0, result.stderr
    assert not diagnostic_lines(result, "connection-without-classification")
    assert not diagnostic_lines(result, "classification-without-connection")


@pytest.mark.trace("TC-155", "FR-013-AC-5")
def test_fr013_ac5_relations_list_both_views():
    report = data_flow_relations(VALID, safety=True)
    assert _pairs(report, FORWARD) == {
        ("CONN-PORTAL-LAB", "CLASS-PHI"),
        ("CONN-PORTAL-LAB", "CLASS-PUBLIC"),
        ("public_link", "CLASS-PUBLIC"),
    }
    assert _rows(report, FORWARD)["bare_link"]["state"] == "uncovered"
    assert _pairs(report, REVERSE) == {
        ("CLASS-PHI", "CONN-PORTAL-LAB"),
        ("CLASS-PUBLIC", "CONN-PORTAL-LAB"),
        ("CLASS-PUBLIC", "public_link"),
    }
    assert _rows(report, REVERSE)["CLASS-UNCARRIED"]["state"] == "uncovered"


def _entries(report: dict, name: str):
    for row in report[name]["rows"]:
        yield row["document"]
        yield from row["linked"]


@pytest.mark.trace("TC-155", "FR-013-AC-5", "FR-013-AC-9")
def test_fr013_ac5_ac9_selected_key_is_included_or_omitted_and_level_never_leaks():
    report = data_flow_relations(VALID, safety=True)
    for name in (FORWARD, REVERSE):
        by_id = {}
        for entry in _entries(report, name):
            by_id.setdefault(entry["id"], []).append(entry)
        for entry in by_id["CLASS-PHI"]:
            assert entry["record"] == {"regulatedCategories": ["health"]}, entry
        for entry in by_id["CLASS-PUBLIC"] + by_id.get("CLASS-UNCARRIED", []):
            assert "regulatedCategories" not in entry.get("record", {}), entry
        for entry in _entries(report, name):
            assert set(entry.get("record", {})) <= {"regulatedCategories"}, entry
    assert '"level"' not in json.dumps(report)

    invalid_report = data_flow_relations(INVALID, safety=True)
    for name in (FORWARD, REVERSE):
        bad_entries = [
            entry
            for entry in _entries(invalid_report, name)
            if entry["id"] == "CLASS-BAD"
        ]
        assert bad_entries, f"CLASS-BAD is absent from {name}"
        for entry in bad_entries:
            assert "regulatedCategories" not in entry.get("record", {}), entry
    assert '"level"' not in json.dumps(invalid_report)


@pytest.mark.trace("TC-156", "FR-013-AC-4")
def test_fr013_ac4_default_severities_draw_no_finding():
    result = validate_data_flow(VALID, safety=True)
    assert result.returncode == 0, result.stderr
    assert not diagnostic_lines(result, "connection-without-classification")
    assert not diagnostic_lines(result, "classification-without-connection")


@pytest.mark.trace("TC-157", "FR-013-AC-6")
def test_fr013_ac6_carried_classification_produces_no_rule_finding():
    report = data_flow_relations(VALID, safety=True)
    row = _rows(report, "connection-crosses-trust-boundary")["CONN-PORTAL-LAB"]
    (boundary,) = row["linked"]
    assert boundary["id"] == "BOUND-INTERNET"
    assert boundary["record"] == {"trust_level": "untrusted"}

    carried = _rows(report, FORWARD)["CONN-PORTAL-LAB"]["linked"]
    health = next(entry for entry in carried if entry["id"] == "CLASS-PHI")
    assert health["record"] == {"regulatedCategories": ["health"]}

    result = validate_data_flow(VALID, safety=True)
    assert result.returncode == 0, result.stderr
    assert "denial" not in result.stderr.lower()
    assert not diagnostic_lines(result, "connection-crosses-trust-boundary")


@pytest.mark.trace("TC-158", "FR-013-AC-7")
def test_fr013_ac7_only_connection_admits_carries_among_systems_kinds():
    manifest = load_manifest()
    assert "carries" not in manifest["edge_types"]
    assert object_type("connection")["allowed_links"]["carries"] == [
        "data_classification"
    ]
    for kind in ("part", "port", "allocation"):
        assert "carries" not in object_type(kind)["allowed_links"], kind
    assert object_type("queue")["allowed_links"]["carries"] == ["data_schema", "event"]
    assert object_type("connection")["construct"]["members"]["fields"] == "forbidden"


@pytest.mark.trace("TC-159", "FR-013-AC-8")
def test_fr013_ac8_relations_and_severities_are_declared_exactly():
    manifest = load_manifest()
    relations = {r["name"]: r for r in manifest["traceability"]["required_relations"]}
    assert relations[FORWARD] == {
        "name": FORWARD,
        "from": "connection",
        "edges": ["carries"],
        "to": ["data_classification"],
        "direction": "outgoing",
        "check": "connection-without-classification",
        "record_keys": ["regulatedCategories"],
    }
    assert relations[REVERSE] == {
        "name": REVERSE,
        "from": "data_classification",
        "edges": ["carries"],
        "to": ["connection"],
        "direction": "incoming",
        "check": "classification-without-connection",
        "record_keys": ["regulatedCategories"],
    }
    severity = manifest["grammar_severity"]
    assert severity["trace:connection-without-classification"] == "off"
    assert severity["trace:classification-without-connection"] == "off"


@pytest.mark.trace("TC-158", "FR-013-AC-7")
def test_fr013_ac7_connection_schema_has_no_carries_and_skeleton_states_it():
    schema = json.loads((PACKAGE_ROOT / "schemas/Connection.json").read_text())
    assert "carries" not in json.dumps(schema)
    skeleton = (PACKAGE_ROOT / "skeletons/connection.md").read_text()
    assert 'type: "carries"' in skeleton and "data_classification" in skeleton
