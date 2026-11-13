"""The part software safety class (FR-012): optional, human-assigned, never defaulted.

Validation runs through the `quire validate` binary against this module;
records are extracted by the engine. The manifest's `field_consistency`,
`vocabulary` and `required_fields` (`unassigned-class`) entries
(FR-012-AC-9, AC-10, AC-13 to AC-15) are not declared yet: the installed
engine rejects those keys until quire-rs implements FR-090 and FR-091
(PLAT-1578).
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

import pytest

from tests.conftest import (
    PACKAGE_ROOT,
    SCHEMAS_DIR,
    SKELETONS_DIR,
    object_type,
)

KEYS = (
    "software_safety_class",
    "software_safety_class_assigned_by",
    "software_safety_class_rationale",
)
RECORD_KEYS = (
    "softwareSafetyClass",
    "softwareSafetyClassAssignedBy",
    "softwareSafetyClassRationale",
)

needs_quire = pytest.mark.skipif(
    shutil.which("quire") is None, reason="quire CLI not installed"
)


def _part(lines: list[str], ident: str = "scoring_engine") -> str:
    text = (SKELETONS_DIR / "part.md").read_text()
    text = text.replace("scoring_engine", ident)
    if not lines:
        return text
    marker = "object: part\n"
    return text.replace(marker, marker + "\n".join(lines) + "\n", 1)


def _full(value: str = "class-2") -> list[str]:
    return [
        f"software_safety_class: {value}",
        "software_safety_class_assigned_by: Ada Example",
        "software_safety_class_rationale: Failure can injure the operator.",
    ]


def _validate(tmp_path: pathlib.Path, text: str) -> subprocess.CompletedProcess:
    doc = tmp_path / "part.md"
    doc.write_text(text)
    return subprocess.run(
        ["quire", "validate", "--module", str(PACKAGE_ROOT), str(doc)],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.trace("FR-012-AC-1")
def test_fr012_ac1_part_record_schema_declares_three_plain_optional_strings():
    schema = json.loads((SCHEMAS_DIR / "Part.json").read_text())
    for key in RECORD_KEYS:
        prop = schema["properties"][key]
        assert prop["type"] == "string"
        assert prop["minLength"] == 1
        assert "enum" not in prop
        assert "default" not in prop
        assert key not in schema["required"]
    dependent = schema["dependentRequired"]
    assert set(dependent["softwareSafetyClass"]) == {
        "softwareSafetyClassAssignedBy",
        "softwareSafetyClassRationale",
    }
    assert dependent["softwareSafetyClassAssignedBy"] == ["softwareSafetyClass"]
    assert dependent["softwareSafetyClassRationale"] == ["softwareSafetyClass"]


@pytest.mark.trace("FR-012-AC-2")
def test_fr012_ac2_yield_pattern_reads_the_three_frontmatter_fields():
    match = object_type("part")["body_extraction"]["yield_pattern"]["match"]
    for record_key, field in zip(RECORD_KEYS, KEYS):
        locator = match[record_key]
        assert locator["from"] == "frontmatter_field"
        assert locator["path"] == [field]
        assert locator["required"] is False


def _extract(tmp_path: pathlib.Path, text: str) -> dict:
    doc = tmp_path / "part.md"
    doc.write_text(text)
    result = subprocess.run(
        ["quire", "extract", "--module", str(PACKAGE_ROOT), str(doc)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    (record,) = json.loads(result.stdout)["extraction"]["records"]
    return record


@pytest.mark.trace("FR-012-AC-3")
@needs_quire
def test_fr012_ac3_assigned_part_validates_and_record_carries_values(tmp_path):
    text = _part(_full())
    assert _validate(tmp_path, text).returncode == 0
    record = _extract(tmp_path, text)
    assert record["softwareSafetyClass"] == "class-2"
    assert record["softwareSafetyClassAssignedBy"] == "Ada Example"
    assert record["softwareSafetyClassRationale"] == "Failure can injure the operator."


@pytest.mark.trace("FR-012-AC-4")
@needs_quire
def test_fr012_ac4_unassigned_part_validates_with_no_class_keys(tmp_path):
    text = _part([])
    result = _validate(tmp_path, text)
    assert result.returncode == 0, result.stderr
    record = _extract(tmp_path, text)
    for key in RECORD_KEYS:
        assert key not in record


@pytest.mark.trace("FR-012-AC-5", "FR-012-AC-6", "FR-012-AC-7")
@pytest.mark.parametrize(
    "record,named",
    [
        (
            {"softwareSafetyClass": "c", "softwareSafetyClassAssignedBy": "A"},
            "softwareSafetyClassRationale",
        ),
        (
            {"softwareSafetyClass": "c", "softwareSafetyClassRationale": "r"},
            "softwareSafetyClassAssignedBy",
        ),
        (
            {"softwareSafetyClassAssignedBy": "A", "softwareSafetyClassRationale": "r"},
            "softwareSafetyClass",
        ),
        (
            {
                "softwareSafetyClass": "",
                "softwareSafetyClassAssignedBy": "A",
                "softwareSafetyClassRationale": "r",
            },
            "softwareSafetyClass",
        ),
        (
            {
                "softwareSafetyClass": "c",
                "softwareSafetyClassAssignedBy": "A",
                "softwareSafetyClassRationale": "",
            },
            "softwareSafetyClassRationale",
        ),
        (
            {
                "softwareSafetyClass": "c",
                "softwareSafetyClassAssignedBy": "",
                "softwareSafetyClassRationale": "r",
            },
            "softwareSafetyClassAssignedBy",
        ),
    ],
)
def test_fr012_record_schema_refuses_incomplete_assignment_naming_the_key(
    schema_registry, record, named
):
    base = {
        "owner": "ix://agent-ix/spec-objects-architecture/search_service",
        "declaredType": {"target": {"kind": "SemanticId", "value": "ix://x/y"}},
        "multiplicity": {"lower": 1, "upper": 1, "ordered": False, "unique": False},
    }
    errs = list(schema_registry("Part").iter_errors({**base, **record}))
    messages = [f"{e.message} at {list(e.absolute_path)}" for e in errs]
    assert any(f"'{named}'" in m for m in messages), messages


@pytest.mark.trace("FR-012-AC-5", "FR-012-AC-6", "FR-012-AC-7")
@needs_quire
@pytest.mark.parametrize(
    "lines,named",
    [
        (_full()[:2], "software_safety_class_rationale"),
        ([_full()[0], _full()[2]], "software_safety_class_assigned_by"),
        (_full()[1:], "software_safety_class"),
        (
            ['software_safety_class: ""', _full()[1], _full()[2]],
            "software_safety_class",
        ),
        (
            [_full()[0], 'software_safety_class_assigned_by: ""', _full()[2]],
            "software_safety_class_assigned_by",
        ),
        (
            [_full()[0], _full()[1], 'software_safety_class_rationale: ""'],
            "software_safety_class_rationale",
        ),
    ],
)
def test_fr012_quire_validate_rejects_incomplete_assignment(tmp_path, lines, named):
    result = _validate(tmp_path, _part(lines))
    assert result.returncode != 0
    assert (
        f'"{named}"' in result.stderr or f"(at {named})" in result.stderr
    ), result.stderr


@pytest.mark.trace("FR-012-AC-8")
@needs_quire
def test_fr012_ac8_system_and_item_carry_independent_classes(tmp_path):
    system = _validate(tmp_path, _part(_full("class-3"), "pump_system"))
    item_text = _part(_full("class-1"), "pump_item").replace(
        "| search_service |", "| pump_system |"
    )
    assert "| pump_system |" in item_text
    item = _validate(tmp_path, item_text)
    assert system.returncode == 0, system.stderr
    assert item.returncode == 0, item.stderr


@pytest.mark.trace("FR-012-AC-11")
def test_fr012_ac11_skeleton_names_the_fields_and_carries_none():
    text = (SKELETONS_DIR / "part.md").read_text()
    for key in KEYS:
        assert f"`{key}`" in text
        assert f"\n{key}:" not in text


# Schema half of the part-frontmatter requirement only. The unassigned-corpus
# clause needs the module's traceability entries, which the engine cannot load yet
# (PLAT-1578), so the criterion is not claimed here.
def test_part_frontmatter_ref_is_self_contained_and_open():
    ot = object_type("part")
    assert ot["frontmatter_schema_ref"] == "schemas/PartFrontmatter.json"
    schema = json.loads((PACKAGE_ROOT / ot["frontmatter_schema_ref"]).read_text())
    assert "$ref" not in json.dumps(schema)
    assert set(schema["properties"]) == set(KEYS)
    assert schema["unevaluatedProperties"] == {}
    for prop in schema["properties"].values():
        assert prop == {"type": "string", "minLength": 1}
    assert "required" not in schema
