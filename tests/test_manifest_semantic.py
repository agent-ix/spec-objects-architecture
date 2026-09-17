"""Manifest contract tests (FR-003): the `semantic` block, its
reference-form `data_schema`, locator preservation, the frozen `lexicon`, and
what Quire's loader refuses.
"""

from __future__ import annotations

import json
import shutil

import pytest
import yaml

from tests.conftest import (
    BASELINE_DIR,
    EXPORTS,
    FIXTURES_DIR,
    MODEL_OF,
    OBJECT_ID_LOCATOR_REGEX,
    OBJECT_ID_PATTERN,
    OBJECT_TYPES,
    PACKAGE_ROOT,
    REPO_ROOT,
    SCHEMAS_DIR,
    SKELETONS_DIR,
    declaration_skeletons,
    frontmatter,
    load_manifest,
    locators,
    object_type,
    object_types,
    sha256_of,
    validation_params,
)

ADMITTED_KEYS = {
    "contract_version",
    "semantic_core",
    "package",
    "exports",
    "imports",
    "targets",
    "mappings",
    "compatibility_posture",
    "legacy_forms",
}


def module_copy(tmp_path, mutate=None):
    """A throwaway copy of the module directory, optionally with a mutated
    manifest. Returns the *search path* the loader walks, not the module dir."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    root = tmp_path / "module"
    shutil.copytree(PACKAGE_ROOT, root)
    if mutate is not None:
        data = yaml.safe_load((root / "manifest.yaml").read_text())
        mutate(data)
        (root / "manifest.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
    return tmp_path


@pytest.mark.trace("TC-020", "FR-003-AC-1", "FR-003-CON-1")
def test_the_semantic_block_carries_the_nine_admitted_keys_and_ten_exports(
    semantic_block,
):
    assert set(semantic_block) == ADMITTED_KEYS
    assert semantic_block["contract_version"] == "1.0.0"
    assert semantic_block["semantic_core"] == "0.1.0"
    assert semantic_block["package"] == "agent-ix/spec-objects-architecture"
    assert semantic_block["exports"] == list(EXPORTS)
    assert semantic_block["imports"] == {}
    assert semantic_block["targets"] == ["json-schema", "markdown"]
    assert semantic_block["mappings"] == ["typed-table", "sysml-fence", "ocl-clause"]
    assert semantic_block["compatibility_posture"] == "strict"
    assert semantic_block["legacy_forms"] == "warning"


@pytest.mark.trace("TC-021", "FR-003-AC-2")
def test_every_exported_type_carries_the_reference_form_and_a_matching_digest():
    for ot in object_types():
        data_schema = ot["data_schema"]
        assert set(data_schema) == {"schema", "digest"}, ot["name"]
        expected = f"schemas/{MODEL_OF[ot['name']]}.json"
        assert data_schema["schema"] == expected, ot["name"]
        path = PACKAGE_ROOT / data_schema["schema"]
        assert path.is_file(), path
        assert data_schema["digest"] == sha256_of(path), ot["name"]
        assert (
            "type" not in data_schema
        ), f"{ot['name']} still carries an inline data_schema"


#: The one locator added after 0.2.0 as required: the interface feature order
#: (FR-007), a break NFR-001 declares.
REQUIRED_ADDITION = ("interface", "features")


def facets_since_020(key: str, locator: dict) -> dict:
    """A locator's facets as 0.2.0 recorded them: the FR-003 object id `regex`
    on the `id` locator is the one facet added since, and it is checked on its
    own (TC-111)."""
    if key != "id":
        return locator
    assert locator["regex"] == OBJECT_ID_LOCATOR_REGEX
    return {k: v for k, v in locator.items() if k != "regex"}


@pytest.mark.trace("TC-022", "FR-003-AC-3")
def test_every_020_locator_is_unchanged_against_the_checked_in_baseline():
    baseline = json.loads((BASELINE_DIR / "body_extraction.json").read_text())
    assert baseline["version"] == "0.2.0"
    for name, extraction in baseline["object_types"].items():
        current = object_type(name).get("body_extraction")
        old = (extraction or {})["yield_pattern"]["match"]
        new = (current or {})["yield_pattern"]["match"]
        for key, facets in old.items():
            assert key in new, f"{name}.{key} was dropped from the current module"
            assert (
                facets_since_020(key, new[key]) == facets
            ), f"{name}.{key} changed facets in the current module"


@pytest.mark.trace("TC-023", "FR-003-AC-3", "FR-003-CON-2")
def test_every_locator_added_after_020_is_optional():
    baseline = json.loads((BASELINE_DIR / "body_extraction.json").read_text())
    added = 0
    for name, extraction in baseline["object_types"].items():
        old = set((extraction or {})["yield_pattern"]["match"])
        for key, facets in locators(object_type(name)).items():
            if key in old:
                continue
            added += 1
            if (name, key) == REQUIRED_ADDITION:
                assert facets.get("required") is True, f"{name}.{key}"
                continue
            assert (
                facets.get("required") is False
            ), f"{name}.{key} was added as required"
    assert added > 0, "no locator was added; FR-005's sections would not be asserted"


@pytest.mark.trace("TC-028", "FR-003-AC-7")
def test_the_prior_version_lexicon_block_is_byte_identical_now():
    baseline = json.loads((BASELINE_DIR / "lexicon.json").read_text())
    assert baseline["version"] == "0.2.0"
    assert load_manifest()["lexicon"] == baseline["lexicon"]


@pytest.mark.trace("TC-024", "FR-003-AC-4")
def test_the_registry_loads_all_fourteen_archetypes(quire_engine):
    registry = quire_engine.Registry.load_from([str(REPO_ROOT)])
    names = set(registry.archetype_names())
    for name in EXPORTS:
        assert name in names, f"{name} did not load from the module"


@pytest.mark.trace("TC-025", "FR-003-AC-4")
@pytest.mark.parametrize("path", validation_params(declaration_skeletons()))
def test_validate_document_reports_no_semantic_load_failure_for_any_skeleton(
    quire_engine, path
):
    text = path.read_text()
    result = quire_engine.validate_document(
        frontmatter(text)["type"], str(PACKAGE_ROOT), text
    )
    assert result["is_valid"], (path.name, result["errors"])
    assert not [e for e in result["errors"] if "semantic." in e["message"]], path.name


@pytest.mark.trace("TC-026", "FR-003-AC-6")
def test_an_unknown_semantic_key_and_an_altered_digest_are_refused(
    quire_engine, tmp_path
):
    """Measured against quire 0.46.0 on this module: an unknown `semantic` key
    drops every object type (the manifest is refused whole), while a wrong
    digest drops the refused object type alone. `agent-ix/quire-rs#394` reports
    a module-wide emptying for the digest case on another module; this test
    records what this module measures rather than what the report says."""

    def add_unknown_key(data):
        data["semantic"]["foo"] = "bar"

    unknown = module_copy(tmp_path / "unknown", add_unknown_key)
    assert quire_engine.Registry.load_from([str(unknown)]).archetype_names() == []

    def break_digest(data):
        assert data["object_types"][1]["name"] == "data_schema"
        data["object_types"][1]["data_schema"]["digest"] = "sha256:" + "0" * 64

    altered = module_copy(tmp_path / "digest", break_digest)
    loaded = set(quire_engine.Registry.load_from([str(altered)]).archetype_names())
    assert "data_schema" not in loaded
    assert loaded >= set(OBJECT_TYPES) - {"data_schema"}

    text = (SKELETONS_DIR / "data_schema.md").read_text()
    for search_path in (unknown, altered):
        # Narrowed to the engine's own error family: a bare `Exception` would
        # also pass on a TypeError from the call signature, which is not the
        # refusal this row observes.
        with pytest.raises(quire_engine.QuireBaseError) as error:
            quire_engine.validate_document(
                "data_schema", str(search_path / "module"), text
            )
        assert (
            "data_schema" in str(error.value) or "archetype" in str(error.value).lower()
        ), str(error.value)


@pytest.mark.trace("TC-026", "FR-003-AC-6")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "FR-003-AC-6 requires the refusal to NAME the offending key and schema "
        "path. quire 0.46.0 empties the registry silently instead: no "
        "ArchetypeLoadFailure, no semantic.* code, nothing naming `foo` or the "
        "path. Blocked on agent-ix/quire-rs#221 (unknown key) and "
        "agent-ix/quire-rs#394 (digest). The criterion stands; the schema is "
        "not relaxed and the test is not skipped."
    ),
)
def test_the_refusal_names_the_offending_key_and_path(quire_engine, tmp_path):
    def add_unknown_key(data):
        data["semantic"]["foo"] = "bar"

    unknown = module_copy(tmp_path / "named-key", add_unknown_key)
    with pytest.raises(quire_engine.QuireBaseError) as error:
        quire_engine.Registry.load_from([str(unknown)])
    assert "foo" in str(error.value)


def _missing_id(kind: str) -> str:
    return f"[{kind}] required 'id' (frontmatter_field(id)) is missing"


@pytest.mark.trace("TC-111", "FR-003-AC-9")
def test_the_id_pattern_is_stated_once_and_carried_by_every_id_locator(
    schema_registry,
):
    object_id = json.loads((SCHEMAS_DIR / "ObjectId.json").read_text())
    assert object_id["type"] == "string"
    assert object_id["pattern"] == OBJECT_ID_PATTERN
    base = json.loads((SCHEMAS_DIR / "ObjectFrontmatter.json").read_text())
    assert base["properties"]["id"]["$ref"].endswith("/ObjectId.json")
    assert set(base["required"]) == {"id", "title", "type"}
    assert OBJECT_ID_LOCATOR_REGEX == f"^({OBJECT_ID_PATTERN[1:-1]})$"
    for ot in object_types():
        assert "frontmatter_schema_ref" not in ot, ot["name"]
        loc = locators(ot)["id"]
        assert loc["from"] == "frontmatter_field", ot["name"]
        assert loc["regex"] == OBJECT_ID_LOCATOR_REGEX, ot["name"]
        assert loc["required"] is True, ot["name"]
    validator = schema_registry("ObjectFrontmatter")
    documents = (
        sorted(SKELETONS_DIR.glob("*.md"))
        + sorted(FIXTURES_DIR.glob("[!b]*/*.md"))
        + sorted(FIXTURES_DIR.glob("*.md"))
    )
    assert len(documents) > 17
    for path in documents:
        front = frontmatter(path.read_text())
        assert list(validator.iter_errors(front)) == [], path
    base_front = {"title": "Flow", "type": "interface"}
    for good in ("Flow", "sys_pump", "queue_001", "a1"):
        assert validator.is_valid({**base_front, "id": good}), good
    for bad in ("queue-001", "sys-pump_1", "_flow", "1flow", ""):
        assert not validator.is_valid({**base_front, "id": bad}), bad


@pytest.mark.trace("TC-111", "FR-003-AC-9")
def test_an_underscore_id_validates_and_a_hyphenated_id_is_refused(quire_engine):
    text = (SKELETONS_DIR / "queue.md").read_text()
    assert "id: queue_001\n" in text
    assert quire_engine.validate_document("queue", str(PACKAGE_ROOT), text)["is_valid"]
    hyphenated = text.replace("id: queue_001\n", "id: queue-001\n", 1)
    result = quire_engine.validate_document("queue", str(PACKAGE_ROOT), hyphenated)
    assert not result["is_valid"]
    messages = [e["message"] for e in result["errors"]]
    assert messages and set(messages) == {_missing_id("queue")}, messages
