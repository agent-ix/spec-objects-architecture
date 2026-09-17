"""Systems-model kind tests (FR-007).

The five QSpec FR-152 kinds — `interface`, `part`, `port`, `connection`,
`allocation` — each declared once as an object type with a `construct:`
(filament-core-service FR-035 CR-004). The engine yields each systems table
row but does not lower it into the record (agent-ix/quire-rs#446), so the
record-shape rows here are verified against hand-built records, and TC-106
pins the known defect rather than stating the requirement.
"""

from __future__ import annotations

import copy
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

# QSpec FR-152 members per kind, named in FCD IR member form.
FR152_MEMBERS = {
    "interface": {"fields", "operations", "featureOrder"},
    "part": {"owner", "declaredType", "multiplicity"},
    "port": {"owner", "direction", "interfaceType", "multiplicity"},
    "connection": {"sourceEnd", "targetEnd", "flowDirection"},
    "allocation": {"sourceElement", "targetElement"},
}

# The FR-004 keys `Interface` carries beside its FR-152 features.
INTERFACE_FR004_KEYS = {"associated_types", "clauses", "relations"}

# agent-ix/quire-specification#86 (FR-208).
MEANING = {kind: f"quire.meaning.systems.{kind}/v1" for kind in SYSTEMS_KINDS}

LOCATOR = {
    "part": ("Part", ["Owner", "Declared Type", "Multiplicity"]),
    "port": ("Port", ["Owner", "Direction", "Interface", "Multiplicity"]),
    "connection": (
        "Connection",
        ["Source", "Source Multiplicity", "Target", "Target Multiplicity", "Direction"],
    ),
    "allocation": ("Allocation", ["Source", "Target"]),
}

# The columns whose cells name another declaration.
REFERENCE_COLUMNS = {
    "part": {"Owner", "Declared Type"},
    "port": {"Owner", "Interface"},
    "connection": {"Source", "Target"},
    "allocation": {"Source", "Target"},
}

# quire-rs FR-075 lowers a model table only when its header starts with one
# of these keys; a systems table must not be mistaken for one.
FR075_TABLE_KEYS = {"Value", "State", "Step", "From", "Term", "Member", "Type"}

EDGE_VERBS = {"owned_by", "typed_by", "connects", "allocates", "allocated_to"}
SYSTEMS_ROLES = {"systems-part", "systems-port", "systems-interface"}

PKG = "ix://test/orders/"
ONE = {"lower": 1, "upper": 1}
RECORDS = {
    "part": {
        "owner": f"{PKG}sys_pump",
        "declaredType": {"target": f"{PKG}pump"},
        "multiplicity": ONE,
    },
    "port": {
        "owner": f"{PKG}sys_pump",
        "direction": "out",
        "interfaceType": {"target": f"{PKG}flow"},
        "multiplicity": ONE,
    },
    "connection": {
        "sourceEnd": {"type": f"{PKG}pump_out"},
        "targetEnd": {"type": f"{PKG}tank_in"},
        "flowDirection": "source-to-target",
    },
    "allocation": {
        "sourceElement": f"{PKG}flow/rate",
        "targetElement": f"{PKG}sys_pump",
    },
}

ARTIFACT_ID = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
MEMBER_REF = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*/[a-z][a-z0-9_]*$")


def _is_reference(cell: str) -> bool:
    """An artifact id, or `<artifact id>/<member>` naming a member of one."""
    return bool(ARTIFACT_ID.match(cell) or MEMBER_REF.match(cell))


def _object_type_in(manifest: dict, name: str) -> dict:
    return next(ot for ot in manifest["object_types"] if ot["name"] == name)


@pytest.mark.trace("TC-100", "FR-007-AC-1")
def test_each_systems_kind_is_an_exported_object_type_with_a_pinned_schema():
    exports = load_manifest()["semantic"]["exports"]
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
def test_a_connection_end_names_its_port_and_admits_a_multiplicity(schema_registry):
    """QSpec #86 TC-197 Y05: an end may state its multiplicity."""
    connection = schema_registry("Connection")
    record = RECORDS["connection"]
    many = {"lower": 0}
    with_multiplicity = {
        **record,
        "sourceEnd": {"type": f"{PKG}pump_out", "multiplicity": ONE},
        "targetEnd": {"type": f"{PKG}tank_in", "multiplicity": many},
    }
    assert list(connection.iter_errors(with_multiplicity)) == []
    assert not connection.is_valid({**record, "sourceEnd": {"multiplicity": ONE}})
    assert not connection.is_valid(
        {**record, "sourceEnd": {"type": f"{PKG}pump_out", "role": "x"}}
    )
    assert not connection.is_valid({**record, "sourceEnd": f"{PKG}pump_out"})


@pytest.mark.trace("TC-101", "FR-007-AC-2")
def test_direction_enums_are_closed(schema_registry):
    port = schema_registry("Port")
    for value in ("in", "out", "inout"):
        assert port.is_valid({**RECORDS["port"], "direction": value})
    assert not port.is_valid({**RECORDS["port"], "direction": "bidirectional"})
    connection = schema_registry("Connection")
    for value in ("source-to-target", "target-to-source", "bidirectional"):
        assert connection.is_valid({**RECORDS["connection"], "flowDirection": value})
    for value in ("undirected", "in"):
        assert not connection.is_valid(
            {**RECORDS["connection"], "flowDirection": value}
        )


@pytest.mark.trace("TC-109", "FR-007-AC-9")
def test_an_interface_may_declare_fields_only_or_operations_only(schema_registry):
    """QSpec #86 TC-197: interface `Flow` declares the field `Flow/rate`."""
    interface = schema_registry("Interface")
    rate = {"name": "rate", "type": {"target": "Decimal"}}
    call = {"name": "start", "params": []}
    assert (
        list(interface.iter_errors({"fields": [rate], "featureOrder": ["rate"]})) == []
    )
    assert interface.is_valid({"operations": [call], "featureOrder": ["start"]})
    assert interface.is_valid(
        {"fields": [rate], "operations": [call], "featureOrder": ["start", "rate"]}
    )
    assert not interface.is_valid({"fields": [rate]})
    construct = object_type("interface")["construct"]
    assert construct["members"]["featureOrder"] == "required"
    assert construct["members"]["fields"] == "optional"
    assert construct["members"]["operations"] == "optional"
    assert "rules" not in construct


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
    assert all("construct" not in v["path"] for v in violations), violations
    for kind in SYSTEMS_KINDS:
        assert object_type(kind)["construct"]["meaning"] == MEANING[kind]


@pytest.mark.trace("TC-103", "FR-007-AC-4")
@pytest.mark.parametrize(
    ("mutate", "path"),
    [
        (
            lambda c: c["references"].__setitem__("owner", ["*"]),
            "construct.references.owner[0]",
        ),
        (
            lambda c: c["members"].__setitem__("owner", "sometimes"),
            "construct.members.owner",
        ),
    ],
    ids=["wildcard-reference", "unknown-member-state"],
)
def test_a_malformed_construct_is_refused(quire_engine, mutate, path):
    manifest = copy.deepcopy(load_manifest())
    mutate(_object_type_in(manifest, "port")["construct"])
    violations = quire_engine.validate_manifest(manifest, str(VENDORED_SCHEMA))
    assert any(v["path"].endswith(path) for v in violations), violations


@pytest.mark.trace("TC-103", "FR-007-AC-4")
def test_construct_references_name_only_declared_members_and_roles():
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
    assert "systems-interface" in object_type("interface")["roles"]
    used_verbs: set[str] = set()
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
    _, columns = LOCATOR[kind]
    assert f"| {' | '.join(columns)} |" in text
    result = quire_engine.extract(kind, str(PACKAGE_ROOT), text)
    (entry,) = result["extraction"]
    assert ARTIFACT_ID.match(entry["id"]), entry["id"]
    cells = entry[kind].split("\t")
    assert len(cells) == len(columns), cells
    for column, cell in zip(columns, cells, strict=True):
        if column in REFERENCE_COLUMNS[kind]:
            assert _is_reference(cell), (column, cell)


def test_a_reference_is_an_artifact_id_or_an_id_and_member():
    assert _is_reference("scoring_engine")
    assert _is_reference("quant_codec/score_ip_batch")
    assert not _is_reference("quant_codec.score_ip_batch")
    assert not _is_reference("ScoringEngine")


@pytest.mark.trace("TC-106", "FR-007-AC-7")
@pytest.mark.parametrize("path", systems_skeletons(), ids=lambda p: p.stem)
def test_known_defect_skeleton_validation_fails_on_the_unlowered_record(
    quire_engine, path
):
    """Pins a known defect, not the requirement. FR-007-AC-7 requires zero
    errors; today each systems skeleton yields exactly one, because
    agent-ix/quire-rs#446 does not lower the table into the record. When it
    lands this test fails and the strict xfails in the skeleton-validation
    tests flip."""
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
@pytest.mark.parametrize("kind", SYSTEMS_KINDS)
def test_no_member_beyond_fr152(kind):
    schema = json.loads((SCHEMAS_DIR / f"{MODEL_OF[kind]}.json").read_text())
    members = object_type(kind)["construct"]["members"]
    required = {m for m, state in members.items() if state == "required"}
    if kind == "interface":
        assert set(schema["properties"]) - INTERFACE_FR004_KEYS == FR152_MEMBERS[kind]
        assert FR152_MEMBERS[kind] <= set(members)
        assert set(schema["required"]) == required == {"featureOrder"}
        return
    assert set(schema["properties"]) == FR152_MEMBERS[kind]
    assert set(schema["required"]) == FR152_MEMBERS[kind]
    assert required == FR152_MEMBERS[kind]
