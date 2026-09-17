"""Systems-model kind tests (FR-007).

The five QSpec FR-152 kinds — `interface`, `part`, `port`, `connection`,
`allocation` — each declared once as an object type with a `construct:`
(filament-core-service FR-035 CR-004). The engine yields each systems table
row but does not lower it into the record (agent-ix/quire-rs#446), so the
record-shape rows here are verified against hand-built records, and the
skeleton-validation row pins today's single failure instead of claiming a
pass.
"""

from __future__ import annotations

import json
import re

import pytest

from tests.conftest import (
    MODEL_OF,
    PACKAGE_ROOT,
    SCHEMAS_DIR,
    SYSTEMS_KINDS,
    SYSTEMS_TYPES,
    load_manifest,
    locators,
    object_type,
    sha256_of,
    systems_skeletons,
)
from tests.test_activation_and_stakeholder import VENDORED_SCHEMA

# QSpec FR-152 members per kind, named in FCD IR member form (FR-007).
FR152_MEMBERS = {
    "part": {"owner", "declaredType", "multiplicity"},
    "port": {"owner", "direction", "interfaceType", "multiplicity"},
    "connection": {"sourceEnd", "targetEnd", "direction"},
    "allocation": {"sourceElement", "targetElement"},
}

# agent-ix/quire-specification#86 (FR-208).
MEANING = {kind: f"quire.meaning.systems.{kind}/v1" for kind in SYSTEMS_KINDS}

LOCATOR = {
    "part": ("Part", ["Owner", "Declared Type", "Multiplicity"]),
    "port": ("Port", ["Owner", "Direction", "Interface", "Multiplicity"]),
    "connection": ("Connection", ["Source", "Target", "Direction"]),
    "allocation": ("Allocation", ["Source", "Target"]),
}

# quire-rs FR-075 lowers a model table only when its header starts with one
# of these keys; a systems table must not be mistaken for one.
FR075_TABLE_KEYS = {"Value", "State", "Step", "From", "Term", "Member", "Type"}

EDGE_VERBS = {"owned_by", "typed_by", "connects", "allocates", "allocated_to"}
SYSTEMS_ROLES = {"systems-part", "systems-port", "systems-interface"}

ID = "ix://agent-ix/spec-objects-architecture/"
ONE = {"lower": 1, "upper": 1}
RECORDS = {
    "part": {
        "owner": f"{ID}search_service",
        "declaredType": {"target": f"{ID}type/quant_scoring_engine"},
        "multiplicity": ONE,
    },
    "port": {
        "owner": f"{ID}scoring_engine",
        "direction": "in",
        "interfaceType": {"target": f"{ID}type/quant_codec"},
        "multiplicity": ONE,
    },
    "connection": {
        "sourceEnd": f"{ID}planner_query_out",
        "targetEnd": f"{ID}score_query_in",
        "direction": "source-to-target",
    },
    "allocation": {
        "sourceElement": f"{ID}quant_codec.score_ip_batch",
        "targetElement": f"{ID}scoring_engine",
    },
}

UNDERSCORE_ID = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")


def _cells(row: str) -> list[str]:
    return row.split("\t")


@pytest.mark.trace("TC-100", "FR-007-AC-1")
def test_each_systems_kind_is_an_exported_object_type_with_a_pinned_schema():
    manifest = load_manifest()
    exports = manifest["semantic"]["exports"]
    for kind in SYSTEMS_KINDS:
        assert kind in exports, kind
        ot = object_type(kind)
        schema = PACKAGE_ROOT / ot["data_schema"]["schema"]
        assert schema.name == f"{MODEL_OF[kind]}.json"
        assert ot["data_schema"]["digest"] == sha256_of(schema), kind


@pytest.mark.trace("TC-101", "FR-007-AC-2")
@pytest.mark.parametrize("kind", SYSTEMS_TYPES)
def test_the_schema_accepts_the_fr152_record_and_refuses_gaps_and_extras(
    schema_registry, kind
):
    validator = schema_registry(MODEL_OF[kind])
    record = RECORDS[kind]
    assert list(validator.iter_errors(record)) == []
    for member in record:
        partial = {k: v for k, v in record.items() if k != member}
        assert not validator.is_valid(partial), (kind, member)
    for extra in ("fields", "operations", "identityFields"):
        assert not validator.is_valid({**record, extra: []}), (kind, extra)
    assert not validator.is_valid({})


@pytest.mark.trace("TC-101", "FR-007-AC-2")
def test_direction_enums_are_closed(schema_registry):
    port = schema_registry("Port")
    for value in ("in", "out", "inout"):
        assert port.is_valid({**RECORDS["port"], "direction": value})
    assert not port.is_valid({**RECORDS["port"], "direction": "bidirectional"})
    connection = schema_registry("Connection")
    for value in ("source-to-target", "target-to-source", "bidirectional"):
        assert connection.is_valid({**RECORDS["connection"], "direction": value})
    for value in ("undirected", "in"):
        assert not connection.is_valid({**RECORDS["connection"], "direction": value})


@pytest.mark.trace("TC-102", "FR-007-AC-3")
@pytest.mark.parametrize("kind", SYSTEMS_TYPES)
def test_each_kind_has_one_required_table_row_locator(kind):
    locs = locators(object_type(kind))
    loc = locs[kind]
    section, columns = LOCATOR[kind]
    assert loc["from"] == "table_row"
    assert loc["under_section"] == section
    assert loc["required"] is True
    assert loc["assert"] == {"columns": columns, "min_rows": 1}
    assert columns[0] not in FR075_TABLE_KEYS
    assert set(locs) == {"id", "title", "type", kind}


@pytest.mark.trace("TC-103", "FR-007-AC-4")
def test_construct_declarations_validate_and_bind_fr208_meanings(quire_engine):
    violations = quire_engine.validate_manifest(load_manifest(), str(VENDORED_SCHEMA))
    assert all("construct" not in v["message"] for v in violations), violations
    assert all("construct" not in str(v.get("path", "")) for v in violations)
    for kind in SYSTEMS_KINDS:
        assert object_type(kind)["construct"]["meaning"] == MEANING[kind]


@pytest.mark.trace("TC-103", "FR-007-AC-4")
def test_construct_references_name_only_declared_roles():
    roles = set(load_manifest()["roles"])
    for kind in SYSTEMS_KINDS:
        construct = object_type(kind)["construct"]
        for member, targets in construct.get("references", {}).items():
            assert member in construct["members"], (kind, member)
            assert "*" not in targets, (kind, member)
            assert set(targets) <= roles, (kind, member, targets)


@pytest.mark.trace("TC-104", "FR-007-AC-5")
def test_edge_verbs_and_roles_are_declared_and_used():
    manifest = load_manifest()
    assert EDGE_VERBS <= set(manifest["edge_types"])
    assert SYSTEMS_ROLES <= set(manifest["roles"])
    used_verbs: set[str] = set()
    assert "systems-interface" in object_type("interface")["roles"]
    for kind in SYSTEMS_TYPES:
        ot = object_type(kind)
        assert set(ot.get("roles", [])) <= set(manifest["roles"]), kind
        for verb, targets in ot["allowed_links"].items():
            used_verbs.add(verb)
            for token in targets:
                assert token == "*" or token in manifest["roles"], (kind, token)
    assert used_verbs == EDGE_VERBS


@pytest.mark.trace("TC-105", "FR-007-AC-6")
@pytest.mark.parametrize("path", systems_skeletons(), ids=lambda p: p.stem)
def test_each_skeleton_yields_one_row_matching_its_columns(quire_engine, path):
    kind = path.stem
    text = path.read_text()
    section, columns = LOCATOR[kind]
    assert f"| {' | '.join(columns)} |" in text
    result = quire_engine.extract(kind, str(PACKAGE_ROOT), text)
    (entry,) = result["extraction"]
    assert UNDERSCORE_ID.match(entry["id"]), entry["id"]
    cells = _cells(entry[kind])
    assert len(cells) == len(columns), cells
    for cell in cells:
        if cell not in {"in", "out", "inout", "1..1"} and "-to-" not in cell:
            assert UNDERSCORE_ID.match(cell.replace(".", "_")), cell


@pytest.mark.trace("TC-106", "FR-007-AC-7")
@pytest.mark.parametrize("path", systems_skeletons(), ids=lambda p: p.stem)
def test_skeleton_validation_fails_only_on_the_unlowered_record(quire_engine, path):
    """What this row counts: today's single error per systems skeleton. The
    record is `{}` because quire-rs#446 does not lower the table; the strict
    xfail in test_skeletons_and_validate flips when it lands."""
    kind = path.stem
    result = quire_engine.validate_document(kind, str(PACKAGE_ROOT), path.read_text())
    assert not result["is_valid"]
    (error,) = result["errors"]
    first = next(iter(RECORDS[kind]))
    assert error["message"].startswith("semantic.record-invalid"), error
    assert f'"{first}" is a required property' in error["message"], error


@pytest.mark.trace("TC-107", "FR-007-AC-8")
@pytest.mark.parametrize("path", systems_skeletons(), ids=lambda p: p.stem)
def test_a_missing_section_or_wrong_columns_is_refused(quire_engine, path):
    kind = path.stem
    text = path.read_text()
    section, columns = LOCATOR[kind]
    renamed = text.replace(f"## {section}\n", "## Elsewhere\n")
    assert renamed != text
    result = quire_engine.validate_document(kind, str(PACKAGE_ROOT), renamed)
    assert not result["is_valid"]
    assert any(
        f"required '{kind}'" in e["message"] and "missing" in e["message"]
        for e in result["errors"]
    ), result["errors"]
    header = f"| {' | '.join(columns)} |"
    wrong = text.replace(header, f"| {' | '.join(reversed(columns))} |")
    assert wrong != text
    result = quire_engine.validate_document(kind, str(PACKAGE_ROOT), wrong)
    assert not result["is_valid"]
    assert any(
        "do not match asserted columns" in e["message"] for e in result["errors"]
    ), result["errors"]


@pytest.mark.trace("TC-108", "FR-007-CON-1")
@pytest.mark.parametrize("kind", SYSTEMS_TYPES)
def test_no_member_beyond_fr152(schema_registry, kind):
    schema = json.loads((SCHEMAS_DIR / f"{MODEL_OF[kind]}.json").read_text())
    assert set(schema["properties"]) == FR152_MEMBERS[kind]
    assert set(schema["required"]) == FR152_MEMBERS[kind]
    members = object_type(kind)["construct"]["members"]
    required = {m for m, state in members.items() if state == "required"}
    assert required == FR152_MEMBERS[kind]
    assert schema["$id"].endswith(f"/{MODEL_OF[kind]}.json")
