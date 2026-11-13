"""The part software safety class manifest checks (FR-012-AC-9, AC-10, AC-12 to AC-15).

The engine reads the `field_consistency`, `vocabulary` and `required_fields`
entries; the requirement archetypes and the class vocabulary come from
spec-artifacts-iso, which declares `carried_fields`. The modules are resolved
from the installed filament modules (`IX_FILAMENT_MODULES_PATH`, default
`~/.ix/filament/modules`); spec-artifacts-process supplies the trace targets.
"""

from __future__ import annotations

import pathlib
import shutil

import pytest
import yaml

from tests.conftest import FIXTURES_DIR, MANIFEST_PATH, PACKAGE_ROOT
from tests.test_design_edges import _module, _run

CORPUS = FIXTURES_DIR / "safety_class"
MEMBER = "agent-ix/class-fixture"


def _bundle(root: pathlib.Path, *extra: str):
    return _run(
        "validate",
        "--okf",
        "--module",
        _module("spec-artifacts-iso"),
        "--module",
        _module("spec-artifacts-process"),
        "--module",
        str(PACKAGE_ROOT),
        "--repo",
        f"{MEMBER}={root}",
        *extra,
    )


def _findings(result, check: str) -> list[str]:
    return [ln for ln in result.stderr.splitlines() if f"[{check}]" in ln]


def _manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _entry(block: str, name: str) -> dict:
    return next(e for e in _manifest()["traceability"][block] if e["name"] == name)


@pytest.mark.trace("FR-012-AC-9")
def test_fr012_ac9_vocabulary_entry_is_declared_and_no_class_value_is_listed():
    assert _entry("vocabulary", "part-class-in-vocabulary") == {
        "name": "part-class-in-vocabulary",
        "from": ["part"],
        "field": "software_safety_class",
        "carried": "software_safety_class",
        "check": "undeclared-class-value",
    }
    for path in PACKAGE_ROOT.rglob("*"):
        if path.is_file() and path.suffix in {".yaml", ".md", ".json"}:
            assert "class-1" not in path.read_text(), path


@pytest.mark.trace("FR-012-AC-10")
def test_fr012_ac10_out_of_vocabulary_part_value_is_reported_once_with_value():
    result = _bundle(CORPUS)
    found = _findings(result, "undeclared-class-value")
    assert len(found) == 1, result.stderr
    assert "part_bad" in found[0] and "'class-9'" in found[0]
    assert "software_safety_class" in found[0]
    assert not any("part_high" in ln or "part_low" in ln for ln in found)


@pytest.mark.trace("FR-012-AC-10")
def test_fr012_ac10_wrong_case_value_is_reported(tmp_path):
    corpus = tmp_path / "case"
    shutil.copytree(CORPUS, corpus)
    part = corpus / "spec/design/part_high.md"
    part.write_text(part.read_text().replace("class-2", "Class-2", 1))
    found = _findings(_bundle(corpus), "undeclared-class-value")
    assert any("part_high" in ln and "'Class-2'" in ln for ln in found)


@pytest.mark.trace("FR-012-AC-12")
def test_fr012_ac12_all_unassigned_corpus_draws_no_undeclared_vocabulary(tmp_path):
    corpus = tmp_path / "unassigned"
    (corpus / "spec/design").mkdir(parents=True)
    shutil.copy(CORPUS / "spec/design/part_none.md", corpus / "spec/design")
    result = _bundle(corpus)
    for name in (
        "requirement-class-below-allocated-part",
        "part-class-in-vocabulary",
        "part-needs-class",
    ):
        assert not any(
            "undeclared-relation-vocabulary" in ln and name in ln
            for ln in result.stderr.splitlines()
        ), result.stderr


@pytest.mark.trace("FR-012-AC-13")
def test_fr012_ac13_lower_requirement_class_is_reported_and_higher_is_not():
    result = _bundle(CORPUS)
    found = _findings(result, "class-below-part")
    assert len(found) == 1, result.stderr
    assert "FR-001" in found[0] and "part_low" in found[0] and "alloc_low" in found[0]
    assert "'class-1'" in found[0] and "'class-2'" in found[0]
    assert not any("FR-002" in ln for ln in found)
    entry = _entry("field_consistency", "requirement-class-below-allocated-part")
    assert entry["rule"] == "not_below" and entry["check"] == "class-below-part"
    assert entry["via"] == {
        "archetype": "allocation",
        "edges": ["allocates"],
        "direction": "incoming",
    }


@pytest.mark.trace("FR-012-AC-14")
def test_fr012_ac14_unassigned_part_is_reported_only_when_the_key_is_enabled():
    entry = _entry("required_fields", "part-needs-class")
    assert entry["check"] == "unassigned-class"
    assert _manifest()["grammar_severity"]["trace:unassigned-class"] == "off"
    assert _findings(_bundle(CORPUS), "unassigned-class") == []
    enabled = _findings(
        _bundle(CORPUS, "--severity", "trace:unassigned-class=warning"),
        "unassigned-class",
    )
    assert len(enabled) == 1 and "part_none" in enabled[0]


@pytest.mark.trace("FR-012-AC-15")
def test_fr012_ac15_module_loads_on_its_own(tmp_path):
    part = tmp_path / "part.md"
    part.write_text((PACKAGE_ROOT / "skeletons" / "part.md").read_text())
    result = _run("validate", "--module", str(PACKAGE_ROOT), str(part))
    assert result.returncode == 0, result.stderr
    assert "ManifestError" not in result.stderr
