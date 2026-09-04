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
    MODEL_OF,
    OBJECT_TYPES,
    PACKAGE_ROOT,
    REPO_ROOT,
    SKELETONS_DIR,
    frontmatter,
    load_manifest,
    locators,
    object_type,
    object_types,
    sha256_of,
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
    assert semantic_block["exports"] == list(OBJECT_TYPES)
    assert semantic_block["imports"] == {}
    assert semantic_block["targets"] == ["json-schema", "markdown"]
    assert semantic_block["mappings"] == ["typed-table", "sysml-fence", "ocl-clause"]
    assert semantic_block["compatibility_posture"] == "additive"
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


@pytest.mark.trace("TC-022", "FR-003-AC-3")
def test_every_020_locator_is_unchanged_against_the_checked_in_baseline():
    baseline = json.loads((BASELINE_DIR / "body_extraction.json").read_text())
    assert baseline["version"] == "0.2.0"
    for name, extraction in baseline["object_types"].items():
        current = object_type(name).get("body_extraction")
        old = (extraction or {})["yield_pattern"]["match"]
        new = (current or {})["yield_pattern"]["match"]
        for key, facets in old.items():
            assert key in new, f"{name}.{key} was dropped at 0.3.0"
            assert new[key] == facets, f"{name}.{key} changed facets at 0.3.0"


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
def test_the_registry_loads_all_ten_archetypes(quire_engine):
    registry = quire_engine.Registry.load_from([str(REPO_ROOT)])
    names = set(registry.archetype_names())
    for name in OBJECT_TYPES:
        assert name in names, f"{name} did not load from the module"


@pytest.mark.trace("TC-025", "FR-003-AC-4")
def test_validate_document_reports_no_semantic_load_failure_for_any_skeleton(
    quire_engine, skeletons
):
    for path in skeletons:
        text = path.read_text()
        result = quire_engine.validate_document(
            frontmatter(text)["type"], str(PACKAGE_ROOT), text
        )
        assert result["is_valid"], (path.name, result["errors"])
        assert not [
            e for e in result["errors"] if "semantic." in e["message"]
        ], path.name


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
        with pytest.raises(Exception):
            quire_engine.validate_document(
                "data_schema", str(search_path / "module"), text
            )


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
    with pytest.raises(Exception) as error:
        quire_engine.Registry.load_from([str(unknown)])
    assert "foo" in str(error.value)
