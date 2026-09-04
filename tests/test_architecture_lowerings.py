"""Architecture-specific lowering tests (FR-006).

Each assertion compares two sections of one authored artifact: the kernel
fence the 0.2.0 manifest already yields (`contract_yaml`, `schema_json`,
`message_schema`) and the typed record the 0.3.0 semantic layer extracts.
Nothing here claims the engine performs the lowering — the engine-side
mapping is `agent-ix/quoin#335` (FR-006-CON-2). The YAML/JSON side is parsed
here; the typed side comes from `extract_semantic`.
"""

from __future__ import annotations

import ast
import json
import re

import pytest
import yaml

from tests.conftest import (
    BASELINE_DIR,
    FIXTURES_DIR,
    KERNEL_SCALARS,
    PACKAGE_ROOT,
    SKELETONS_DIR,
    frontmatter,
    locators,
    object_type,
)

TYPE_PREFIX = "ix://agent-ix/spec-objects-architecture/type/"


def extract(quire_engine, module, bundle, path):
    return quire_engine.extract_semantic(
        {
            "markdown": path.read_text(),
            "module": module,
            "path": str(path),
            "sourceIdentity": (
                "ix://agent-ix/spec-objects-architecture/"
                f"{frontmatter(path.read_text())['id']}"
            ),
            "bundle": bundle,
        }
    )


def fence(path, heading: str, language: str) -> str:
    text = re.sub(r"<!--.*?-->", "", path.read_text(), flags=re.DOTALL)
    section = re.search(
        rf"^## {re.escape(heading)}[ \t]*$(.*?)(?=^## |\Z)",
        text,
        re.DOTALL | re.MULTILINE,
    )
    assert section, f"{path.name} has no `## {heading}` section"
    block = re.search(
        rf"^```{language}[ \t]*$\n(.*?)^```", section.group(1), re.DOTALL | re.MULTILINE
    )
    assert block, f"{path.name} `## {heading}` has no ```{language} fence"
    return block.group(1)


@pytest.mark.trace("TC-080", "FR-006-AC-1")
def test_the_interface_contract_yaml_and_its_typed_operations_agree(
    quire_engine, semantic_module, bundle_index
):
    path = SKELETONS_DIR / "interface.md"
    contract = yaml.safe_load(fence(path, "Contract", "yaml"))
    record = extract(quire_engine, semantic_module, bundle_index, path)

    declared = contract["operations"]
    assert [op["name"] for op in declared] == [
        op["name"] for op in record["operations"]
    ]
    for yaml_op, typed_op in zip(declared, record["operations"]):
        assert yaml_op["inputs"] == [p["name"] for p in typed_op["params"]], yaml_op[
            "name"
        ]
        assert bool(yaml_op.get("output")) == bool(typed_op.get("returns")), yaml_op[
            "name"
        ]


@pytest.mark.trace("TC-081", "FR-006-AC-2")
def test_the_data_schema_fence_and_its_typed_properties_agree(
    quire_engine, semantic_module, bundle_index
):
    path = SKELETONS_DIR / "data_schema.md"
    document = json.loads(fence(path, "Schema", "json"))
    record = extract(quire_engine, semantic_module, bundle_index, path)

    assert sorted(document["properties"]) == sorted(
        decl["name"] for decl in record["fields"]
    )
    mandatory = {
        decl["name"]
        for decl in record["fields"]
        if decl["type"]["multiplicity"]["lower"] == 1
    }
    assert set(document["required"]) == mandatory


@pytest.mark.trace("TC-082", "FR-006-AC-3")
def test_the_queue_message_format_and_its_typed_properties_agree(
    quire_engine, semantic_module, bundle_index
):
    path = SKELETONS_DIR / "queue.md"
    message = json.loads(fence(path, "Message Format", "json"))
    record = extract(quire_engine, semantic_module, bundle_index, path)
    assert sorted(message) == sorted(decl["name"] for decl in record["fields"])


@pytest.mark.trace("TC-083", "FR-006-AC-4")
def test_every_api_endpoint_reference_resolves_to_a_shipped_data_schema(
    quire_engine, semantic_module, bundle_index
):
    titles = {
        frontmatter(path.read_text())["title"]
        for path in SKELETONS_DIR.glob("*.md")
        if frontmatter(path.read_text())["object"] == "data_schema"
    }
    assert titles, "the module ships no data_schema skeleton to reference"

    path = SKELETONS_DIR / "api_endpoint.md"
    record = extract(quire_engine, semantic_module, bundle_index, path)
    assert not [
        d
        for d in record.get("diagnostics", [])
        if d.get("code") == "semantic.unresolved-type"
    ], record.get("diagnostics")

    targets = []
    for operation in record["operations"]:
        targets += [param["type"]["target"] for param in operation["params"]]
        if operation.get("returns"):
            targets.append(operation["returns"]["target"])
    referenced = [t for t in targets if t not in KERNEL_SCALARS]
    assert referenced, "the endpoint references no declared record at all"
    for target in referenced:
        assert target.startswith(TYPE_PREFIX), target
        assert target[len(TYPE_PREFIX) :] in titles, target


@pytest.mark.trace("TC-084", "FR-006-AC-5")
def test_an_unknown_return_token_is_reported_and_placeheld_not_rewritten(
    quire_engine, semantic_module, bundle_index
):
    path = FIXTURES_DIR / "api_endpoint-unresolved-return.md"
    front = frontmatter(path.read_text())
    record = extract(quire_engine, semantic_module, bundle_index, path)
    findings = [
        d for d in record.get("diagnostics", []) if d.get("code") == front["expect"]
    ]
    assert len(findings) == 1, record.get("diagnostics")
    assert "MysteryRecord" in findings[0]["message"]
    target = record["operations"][0]["returns"]["target"]
    assert target == (
        "ix://agent-ix/spec-objects-architecture/unresolved/MysteryRecord"
    )
    assert target not in KERNEL_SCALARS


@pytest.mark.trace("TC-085", "FR-006-AC-6", "FR-006-CON-1")
def test_the_three_kernel_fence_locators_are_unchanged_and_still_yield(quire_engine):
    baseline = json.loads((BASELINE_DIR / "body_extraction.json").read_text())
    owned = {
        "interface": "contract_yaml",
        "data_schema": "schema_json",
        "queue": "message_schema",
        "binary_format": "layout_yaml",
    }
    for type_name, key in owned.items():
        old = baseline["object_types"][type_name]["yield_pattern"]["match"][key]
        assert locators(object_type(type_name))[key] == old, f"{type_name}.{key}"

        path = SKELETONS_DIR / f"{type_name}.md"
        records = quire_engine.extract(type_name, str(PACKAGE_ROOT), path.read_text())[
            "extraction"
        ]
        assert len(records) == 1, type_name
        assert records[0][key].strip(), f"{type_name}.{key} yielded nothing at 0.3.0"


@pytest.mark.trace("TC-086", "FR-006-CON-2")
def test_no_lowering_assertion_depends_on_an_engine_lowering():
    """FR-006-CON-2, static: every agreement test in this module parses the
    kernel fence itself and compares it against the extraction surface. The
    only engine entry points these tests may reach for are `extract_semantic`
    and `extract`; an entry point that claimed to lower `contract_yaml` would
    show up here."""
    tree = ast.parse(
        (FIXTURES_DIR.parent / "test_architecture_lowerings.py").read_text()
    )
    reached = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in ("quire_engine", "quire")
    }
    assert reached <= {"extract_semantic", "extract"}, reached
    assert reached, "no test in this module reaches the engine at all"
