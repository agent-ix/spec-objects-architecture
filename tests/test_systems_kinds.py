"""Systems-model kind tests (FR-007).

The five QSpec FR-152 kinds — `interface`, `part`, `port`, `connection`,
`allocation` — each declared once as an object type with a `construct:`
(filament-core-service FR-035 CR-004). The record-shape rows are verified
against hand-built records named with QSpec #86 TC-197's declaration keys.
Lowering the systems tables (agent-ix/quire-rs#446) and the interface
`## Features` table (agent-ix/quire-rs#448) into the record is the engine's
work; the rows that depend on it probe the installed engine and stay strict
expected failures on one that does not lower them yet.
"""

from __future__ import annotations

import copy
import json
import re

import pytest

from tests.conftest import (
    FIXTURES_DIR,
    MODEL_OF,
    PACKAGE_ROOT,
    SCHEMAS_DIR,
    SKELETONS_DIR,
    SYSTEMS_KINDS,
    SYSTEMS_TYPES,
    engine_lowers_systems_tables,
    generalization_gate_xfail,
    load_manifest,
    locators,
    object_type,
    sha256_of,
    systems_skeletons,
    validation_params,
)
from tests.test_activation_and_stakeholder import VENDORED_SCHEMA
from tests.test_manifest_semantic import module_copy

# QSpec FR-152 members per kind, named in FCD IR member form.
FR152_MEMBERS = {
    "interface": {"fields", "operations", "featureOrder"},  # and `supertypes`, an edge
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

# QSpec #86 TC-197 fixture Y: node identities are `ix://test/orders/<artifact
# id>`, and each record names TC-197's declaration keys (`Sys`, `Pump`,
# `Flow`, `sys_pump`, `pump_out`, `tank_in`, `Pump/run`).
PKG = "ix://test/orders/"
ONE = {"lower": 1, "upper": 1}
RECORDS = {
    "part": {
        "owner": f"{PKG}Sys",
        "declaredType": {"target": f"{PKG}Pump"},
        "multiplicity": ONE,
    },
    "port": {
        "owner": f"{PKG}sys_pump",
        "direction": "out",
        "interfaceType": {"target": f"{PKG}Flow"},
        "multiplicity": ONE,
    },
    "connection": {
        "sourceEnd": {"type": f"{PKG}pump_out"},
        "targetEnd": {"type": f"{PKG}tank_in"},
        "flowDirection": "source-to-target",
    },
    "allocation": {
        "sourceElement": f"{PKG}Pump/run",
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


@pytest.mark.trace("TC-105", "FR-007-AC-6")
def test_a_reference_is_an_artifact_id_or_an_id_and_member():
    assert _is_reference("scoring_engine")
    assert _is_reference("quant_codec/score_ip_batch")
    assert not _is_reference("quant_codec.score_ip_batch")
    assert not _is_reference("ScoringEngine")


@pytest.mark.trace("TC-106", "FR-007-AC-7")
@pytest.mark.parametrize("path", systems_skeletons(), ids=lambda p: p.stem)
def test_skeleton_validation_matches_the_installed_engine(quire_engine, path):
    """FR-007-AC-7 requires zero errors. An engine that lowers the systems
    tables (agent-ix/quire-rs#446, probed) must deliver exactly that; one that
    does not yields exactly one error, the record missing its first member,
    and anything else turns this row red."""
    kind = path.stem
    result = quire_engine.validate_document(kind, str(PACKAGE_ROOT), path.read_text())
    if engine_lowers_systems_tables():
        assert result["errors"] == [], result["errors"]
        assert result["is_valid"]
        return
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


def _with_relationship(text: str, verb: str, target: str) -> str:
    front = "object: interface\n"
    assert front in text
    return text.replace(
        front,
        f"{front}relationships:\n  - type: {verb}\n    target: {target}\n",
        1,
    )


SOB_SPECIALIZES = FIXTURES_DIR / "spec-objects-business-specializes.json"


@pytest.mark.trace("TC-110", "FR-007-AC-10")
def test_an_interface_declares_supertypes_by_specializes(quire_engine):
    """QSpec #86 TC-197: `Flow2.supertypes = [Flow]`. The edge's registry entry
    equals spec-objects-business's, pinned with its source revision; the
    construct names the IR member `supertypes` optional and declares no
    `references` entry for it — the filament-core-data semantic-ir reader
    already constrains a supertype reference to the same kind
    (`CONSTRUCT_TARGET_KIND`, FCD FR-141), and `supertypes` is outside the
    closed `references` member vocabulary FCD FR-142 states, so naming it
    there makes FCD's reader refuse the whole module (FCD#173)."""
    pinned = json.loads(SOB_SPECIALIZES.read_text())
    assert pinned["source"]["repository"] == "agent-ix/spec-objects-business"
    assert re.fullmatch(r"[0-9a-f]{40}", pinned["source"]["revision"])
    manifest = load_manifest()
    assert manifest["edge_types"]["specializes"] == pinned["specializes"]
    interface = object_type("interface")
    assert interface["allowed_links"]["specializes"] == ["interface"]
    construct = interface["construct"]
    assert construct["members"]["supertypes"] == "optional"
    assert "supertypes" not in construct.get("references", {})

    text = (PACKAGE_ROOT / "skeletons" / "interface.md").read_text()
    special = _with_relationship(text, "specializes", "Flow")
    edges = quire_engine.extract("interface", str(PACKAGE_ROOT), special)["edges"]
    assert {"target": "Flow", "edge_type": "specializes"} in edges
    warnings = quire_engine.validate_document("interface", str(PACKAGE_ROOT), special)[
        "warnings"
    ]
    assert not [w for w in warnings if w["reason"] == "disallowed-edge-type"]
    refused = quire_engine.validate_document(
        "interface", str(PACKAGE_ROOT), _with_relationship(text, "owned_by", "Flow")
    )["warnings"]
    assert any(
        w["reason"] == "disallowed-edge-type" and "owned_by" in w["message"]
        for w in refused
    ), refused


def _feature_not_extractable(errors: list[dict]) -> list[dict]:
    return [
        e
        for e in errors
        if "feature-not-extractable" in e["message"]
        and "generalization" in e["message"]
    ]


def _drop_generalization(data):
    data["semantic"]["mappings"] = [
        m for m in data["semantic"]["mappings"] if m != "generalization"
    ]


@pytest.mark.trace("TC-113", "FR-007-AC-12")
def test_generalization_mapping_lets_specializes_extract(quire_engine):
    """agent-ix/spec-objects-architecture#14: quire-rs FR-075
    `ModelFeature::Generalization.declared_by_mappings` refuses an
    interface's `specializes` relationship with
    `semantic.feature-not-extractable` unless `generalization` is in
    `semantic.mappings`. TC-110 already asserts the edge extracts and draws
    no `disallowed-edge-type` warning; this asserts the mapping token itself
    is declared and that declaring it draws no such diagnostic. This half
    holds on every installed engine; the removal half that reproduces the
    diagnostic is a separate, xfail-marked test below."""
    assert "generalization" in load_manifest()["semantic"]["mappings"]

    text = (PACKAGE_ROOT / "skeletons" / "interface.md").read_text()
    special = _with_relationship(text, "specializes", "Flow")

    declared = quire_engine.validate_document("interface", str(PACKAGE_ROOT), special)
    assert not _feature_not_extractable(declared["errors"]), declared["errors"]
    edges = quire_engine.extract("interface", str(PACKAGE_ROOT), special)["edges"]
    assert {"target": "Flow", "edge_type": "specializes"} in edges


@generalization_gate_xfail()
@pytest.mark.trace("TC-113", "FR-007-AC-12")
def test_generalization_mapping_removal_is_refused(quire_engine, tmp_path):
    """agent-ix/spec-objects-architecture#14: dropping `generalization` from
    a manifest copy's `semantic.mappings` must reproduce
    `semantic.feature-not-extractable` for the same `specializes`
    relationship the declared half extracts cleanly. quire 0.46.0 (pypi.ix)
    predates the gate (PR #432, `6eec7e8`, on no tag), so this is a strict
    expected failure until agent-ix/quire-rs#463 publishes a wheel that
    carries it."""
    text = (PACKAGE_ROOT / "skeletons" / "interface.md").read_text()
    special = _with_relationship(text, "specializes", "Flow")

    without = module_copy(tmp_path / "without-generalization", _drop_generalization)
    refused = quire_engine.validate_document(
        "interface", str(without / "module"), special
    )
    assert _feature_not_extractable(refused["errors"]), refused["errors"]


# filament-core-data FR-142 (`ix://agent-ix/filament-core-data/FR-142`): the
# closed vocabulary of reference members a construct's `references` block may
# name. `supertypes` is outside this set; naming it there makes the FCD
# semantic-ir reader refuse the whole module with MODULE_REFUSED at load time
# (filament-core-data#173). FR-141 already refuses a supertype reference of
# another kind with `CONSTRUCT_TARGET_KIND`, independent of any
# construct-level `references` declaration.
FCD_FR142_REFERENCE_MEMBERS = {
    "owner",
    "members",
    "persists",
    "interfaceType",
    "declaredType",
    "sourceElement",
    "targetElement",
    "sourceEnd",
    "targetEnd",
    "transitions",
    "steps",
}


@pytest.mark.trace("TC-110", "FR-007-AC-10")
def test_every_construct_reference_member_is_in_the_fcd_vocabulary():
    """Every `references` key any construct in this manifest declares is one
    of FCD FR-142's reference members, so the module loads under FCD's
    reader rather than being refused with MODULE_REFUSED."""
    for ot in load_manifest()["object_types"]:
        construct = ot.get("construct")
        if not construct:
            continue
        for member in construct.get("references", {}):
            assert member in FCD_FR142_REFERENCE_MEMBERS, (ot["name"], member)


INTERFACE_SKELETON = SKELETONS_DIR / "interface.md"


def _features_rows(text: str) -> list[list[str]]:
    section = text.split("\n## Features\n", 1)[1]
    rows = [line for line in section.splitlines() if line.startswith("|")]
    assert rows[0] == "| Feature | Kind |", rows[0]
    return [[c.strip() for c in row.strip("|").split("|")] for row in rows[2:]]


@pytest.mark.trace("TC-112", "FR-007-AC-11")
def test_the_interface_features_table_carries_the_feature_order(quire_engine):
    loc = locators(object_type("interface"))["features"]
    assert loc == {
        "from": "table_row",
        "under_section": "Features",
        "required": True,
        "assert": {"columns": ["Feature", "Kind"], "min_rows": 1},
    }
    text = INTERFACE_SKELETON.read_text()
    operations = re.findall(r"^### (\w+)$", text.split("\n## Operations\n", 1)[1], re.M)
    assert operations
    assert _features_rows(text) == [[name, "operation"] for name in operations]
    removed = text.replace("\n## Features\n", "\n## Feature List\n")
    assert removed != text
    result = quire_engine.validate_document("interface", str(PACKAGE_ROOT), removed)
    assert not result["is_valid"]
    assert any(
        "required 'features'" in e["message"] and "missing" in e["message"]
        for e in result["errors"]
    ), result["errors"]


@pytest.mark.trace("TC-112", "FR-007-AC-11")
@pytest.mark.parametrize("path", validation_params([INTERFACE_SKELETON]))
def test_the_interface_skeleton_lowers_its_feature_order(
    quire_engine, semantic_block, path
):
    text = path.read_text()
    result = quire_engine.validate_document("interface", str(PACKAGE_ROOT), text)
    assert result["errors"] == [], result["errors"]
    record = quire_engine.extract_semantic(
        {
            "markdown": text,
            "module": {
                "contractVersion": semantic_block["contract_version"],
                "semanticCore": semantic_block["semantic_core"],
                "package": semantic_block["package"],
                "exports": semantic_block["exports"],
            },
            "path": "spec/interface.md",
            "bundle": {"package": semantic_block["package"]},
            "bodyExtraction": object_type("interface")["body_extraction"],
        }
    )
    order = [entry["name"] for entry in record["model"]["featureOrder"]]
    assert order == [row[0] for row in _features_rows(text)]
