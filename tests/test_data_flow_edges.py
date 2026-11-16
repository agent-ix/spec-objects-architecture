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
import pathlib

import pytest

from tests.conftest import (
    FIXTURES_DIR,
    PACKAGE_ROOT,
    load_manifest,
    module_args,
    object_type,
    run_quire,
    validate_bundle,
)

CORPUS = FIXTURES_DIR / "data_flow"
VALID = CORPUS / "valid"
INVALID = CORPUS / "invalid"
MEMBER = "agent-ix/df"
FORWARD = "connection-carries-classification"
REVERSE = "classification-carried-by-connection"


def _validate(root: pathlib.Path, *extra: str):
    return validate_bundle(MEMBER, root, *extra, safety=True)


def _relations(root: pathlib.Path) -> dict[str, dict]:
    result = run_quire(
        "relations",
        "--json",
        *module_args(safety=True),
        "--repo",
        f"{MEMBER}={root}",
    )
    assert result.returncode == 0, result.stderr
    return {r["name"]: r for r in json.loads(result.stdout)["relations"]}


def _pairs(report: dict, name: str) -> set[tuple[str, str]]:
    return {
        (row["document"]["id"], linked["id"])
        for row in report[name]["rows"]
        for linked in row["linked"]
    }


def _rows(report: dict, name: str) -> dict[str, dict]:
    return {row["document"]["id"]: row for row in report[name]["rows"]}


def _lines(result, check: str) -> list[str]:
    return [ln for ln in result.stderr.splitlines() if f"[{check}]" in ln]


@pytest.mark.trace("TC-151", "FR-013-AC-1")
def test_fr013_ac1_connection_carrying_a_classification_validates():
    result = _validate(VALID)
    assert result.returncode == 0, result.stderr
    assert "disallowed-edge" not in result.stderr


@pytest.mark.trace("TC-152", "FR-013-AC-2")
def test_fr013_ac2_wrong_kind_and_dangling_targets_fail():
    result = _validate(INVALID, "--strict")
    assert result.returncode == 3, result.stderr
    (wrong,) = _lines(result, "disallowed-edge-target")
    assert "wrong_kind_link" in wrong and "'carries'" in wrong
    assert "scoring_engine" in wrong and "'part'" in wrong
    (dangling,) = _lines(result, "dangling-reference")
    assert "dangling_link.md" in dangling
    assert "CLASS-MISSING" in dangling and "'carries'" in dangling


@pytest.mark.trace("TC-153", "FR-013-AC-3")
def test_fr013_ac3_opted_in_checks_report_the_gaps():
    result = _validate(
        VALID,
        "--severity",
        "trace:connection-without-classification=warning",
        "--severity",
        "trace:classification-without-connection=warning",
    )
    assert result.returncode == 0, result.stderr
    (conn,) = _lines(result, "connection-without-classification")
    assert "bare_link" in conn
    (cls,) = _lines(result, "classification-without-connection")
    assert "CLASS-UNCARRIED" in cls


@pytest.mark.trace("TC-154", "FR-013-AC-4")
def test_fr013_ac4_default_severity_draws_no_finding():
    result = _validate(VALID)
    assert result.returncode == 0, result.stderr
    assert not _lines(result, "connection-without-classification")
    assert not _lines(result, "classification-without-connection")


@pytest.mark.trace("TC-155", "FR-013-AC-5")
def test_fr013_ac5_relations_list_both_views():
    report = _relations(VALID)
    assert _pairs(report, FORWARD) == {
        ("phi_link", "CLASS-PHI"),
        ("phi_link", "CLASS-PUBLIC"),
        ("public_link", "CLASS-PUBLIC"),
    }
    assert _rows(report, FORWARD)["bare_link"]["state"] == "uncovered"
    assert _pairs(report, REVERSE) == {
        ("CLASS-PHI", "phi_link"),
        ("CLASS-PUBLIC", "phi_link"),
        ("CLASS-PUBLIC", "public_link"),
    }
    assert _rows(report, REVERSE)["CLASS-UNCARRIED"]["state"] == "uncovered"


def _entries(report: dict, name: str):
    for row in report[name]["rows"]:
        yield row["document"]
        yield from row["linked"]


@pytest.mark.trace("TC-155", "FR-013-AC-5", "FR-013-AC-9")
def test_fr013_ac5_ac9_selected_key_is_included_or_omitted_and_level_never_leaks():
    report = _relations(VALID)
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

    invalid_report = _relations(INVALID)
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
    result = _validate(VALID)
    assert result.returncode == 0, result.stderr
    assert not _lines(result, "connection-without-classification")
    assert not _lines(result, "classification-without-connection")


@pytest.mark.trace("TC-157", "FR-013-AC-6")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "FR-013-AC-6 requires the PLAT-1532 crossing edge and PLAT-1441 FR-084 change"
    ),
)
def test_fr013_ac6_carried_classification_produces_no_rule_finding():
    # This integration criterion belongs to the crossing-edge work. Keep the
    # complete precondition visible so this ticket cannot claim it prematurely.
    docs = "\n".join(path.read_text() for path in VALID.rglob("*.md"))
    assert "trust_boundary" in docs and "trust_level: untrusted" in docs


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
