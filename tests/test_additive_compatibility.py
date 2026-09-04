"""Additive-compatibility tests (NFR-001): the 0.3.0 module stays additive
over the checked-in 0.2.0 set.

The population is the frozen baseline under `tests/fixtures/baseline-0.2.0/`:
the 0.2.0 `body_extraction` locators, the 0.2.0 edge vocabulary, and all ten
0.2.0 skeletons, captured from `origin/main` before this change touched
anything.
"""

from __future__ import annotations

import json
import re

import pytest

from tests.conftest import (
    BASELINE_DIR,
    PACKAGE_ROOT,
    frontmatter,
    locators,
    object_type,
)


def baseline_locators() -> dict:
    return json.loads((BASELINE_DIR / "body_extraction.json").read_text())


def baseline_skeletons() -> list:
    return sorted((BASELINE_DIR / "skeletons").glob("*.md"))


def extract_semantic(quire_engine, module, path):
    return quire_engine.extract_semantic(
        {
            "markdown": path.read_text(),
            "module": module,
            "path": str(path),
            "bundle": {
                "package": module["package"],
                "objects": [],
                "enumerations": [],
                "imports": {},
            },
        }
    )


def section_body(text: str, heading: str) -> str:
    """The named H2 body as it stands in the frozen fixture — an independent
    oracle, not another engine run."""
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    match = re.search(
        rf"^## {re.escape(heading)}[ \t]*$(.*?)(?=^## |\Z)",
        body,
        re.DOTALL | re.MULTILINE,
    )
    assert match, f"the fixture has no `## {heading}` section"
    return match.group(1).strip()


def code_block(text: str, heading: str, language: str) -> str:
    section = section_body(text, heading)
    match = re.search(
        rf"^```{language}[ \t]*$\n(.*?)^```", section, re.DOTALL | re.MULTILINE
    )
    assert match, f"the `## {heading}` section has no ```{language} fence"
    return match.group(1).rstrip("\n")


@pytest.mark.trace("TC-060", "NFR-001-AC-1")
def test_no_baseline_locator_definition_changed():
    baseline = baseline_locators()
    assert baseline["version"] == "0.2.0"
    changed = []
    for name, extraction in baseline["object_types"].items():
        old = (extraction or {})["yield_pattern"]["match"]
        new = locators(object_type(name))
        for key, facets in old.items():
            if new.get(key) != facets:
                changed.append(f"{name}.{key}")
    assert changed == []


@pytest.mark.trace("TC-064", "NFR-001-AC-5")
def test_no_object_type_changed_its_edge_vocabulary_or_roles():
    baseline = json.loads((BASELINE_DIR / "edge_vocabulary.json").read_text())
    assert baseline["version"] == "0.2.0"
    for name, expected in baseline["object_types"].items():
        current = object_type(name)
        assert current.get("allowed_links") == expected["allowed_links"], name
        assert current.get("roles") == expected["roles"], name


@pytest.mark.trace("TC-061", "NFR-001-AC-2")
def test_every_baseline_skeleton_validates_under_the_new_manifest(quire_engine):
    """Measured, not assumed: the ten 0.2.0 skeletons carry no frontmatter
    `object:` key, so Quire runs headings-only validation on them and the
    typed record is never assembled or checked. That is what makes 0.3.0
    additive for the artifacts that exist today."""
    baseline = baseline_skeletons()
    assert len(baseline) == 10
    failures = {}
    for path in baseline:
        text = path.read_text()
        assert "object" not in frontmatter(text), path.name
        result = quire_engine.validate_document(
            frontmatter(text)["type"], str(PACKAGE_ROOT), text
        )
        if result["errors"]:
            failures[path.name] = [e["message"] for e in result["errors"]]
    assert failures == {}


@pytest.mark.trace("TC-061", "NFR-001-AC-2")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "The engine defect NFR-001's Verification names: once a legacy-form "
        "artifact carries `object:`, quire 0.46.0 assembles its declaration "
        "record as `{}` and checks it against the type schema "
        "unconditionally, so it fails `semantic.record-invalid` at error "
        "severity even under `legacy_forms: warning`. "
        "agent-ix/quire-rs#391 owns the rule. The schema is not relaxed and "
        "the row is an expected failure, never a skip."
    ),
)
def test_a_legacy_form_artifact_that_declares_its_object_is_not_an_error(quire_engine):
    text = (BASELINE_DIR / "skeletons" / "data_schema.md").read_text()
    text = text.replace(
        "type: data_schema\n", "type: data_schema\nobject: data_schema\n", 1
    )
    result = quire_engine.validate_document("data_schema", str(PACKAGE_ROOT), text)
    assert [e["message"] for e in result["errors"]] == []


@pytest.mark.trace("TC-062", "NFR-001-AC-3")
def test_the_legacy_properties_warning_population_is_empty_and_is_recorded_as_empty(
    quire_engine, semantic_module
):
    """What this row counts: `semantic.legacy-properties-form` warnings over
    the ten checked-in 0.2.0 skeletons. The count is **0**, and the reason is
    asserted rather than assumed — no 0.2.0 architecture skeleton carries a
    `## Properties` section in any form (their sections are `Endpoint`,
    `Schema`, `Message Format`, `Inputs`, `Props`, `Contract`, `Layout`,
    `Thresholds`), so the diagnostic has no subject to fire on. This is the
    one place `spec-objects-architecture` measures differently from
    `spec-objects-business`, whose 0.2.0 skeletons do carry bullet-list
    Properties sections.
    """
    for path in baseline_skeletons():
        text = path.read_text()
        assert not re.search(r"^## Properties\b", text, re.MULTILINE), path.name
        record = extract_semantic(quire_engine, semantic_module, path)
        legacy = [
            d
            for d in record.get("diagnostics", [])
            if str(d.get("code", "")).startswith("semantic.legacy-")
        ]
        assert legacy == [], (path.name, legacy)


@pytest.mark.trace("TC-063", "NFR-001-AC-4")
def test_every_020_locator_yield_is_byte_identical_across_versions(quire_engine):
    """The untyped locator yields are what every existing consumer reads; the
    0.3.0 locators must leave them untouched. Each expectation is read from
    the frozen fixture text, not from a second engine run."""
    baseline = baseline_locators()
    for path in baseline_skeletons():
        name = path.stem
        text = path.read_text()
        extracted = quire_engine.extract(name, str(PACKAGE_ROOT), text)
        records = extracted["extraction"]
        assert len(records) == 1, (name, records)
        record = records[0]
        matched = 0
        for key, facets in baseline["object_types"][name]["yield_pattern"][
            "match"
        ].items():
            if facets["from"] == "frontmatter_field":
                continue
            heading = facets["after_heading"]
            if heading not in text:
                assert not facets.get("required"), (name, key)
                continue
            if facets["from"] == "code_block":
                expected = code_block(text, heading, facets["language"])
            else:
                expected = section_body(text, heading)
            assert record[key] == expected, (name, key)
            matched += 1
        assert matched, f"{name} yielded no body locator at all"
