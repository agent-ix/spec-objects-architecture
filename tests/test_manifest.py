"""Auto-generated test: manifest loads + object_types are well-formed."""

from __future__ import annotations

import pathlib

import pytest
import yaml

PKG_ROOT = pathlib.Path(__file__).resolve().parent.parent / "spec_objects_architecture"
MANIFEST_PATH = PKG_ROOT / "manifest.yaml"


def test_manifest_loads() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    assert manifest["manifest_version"] == "1.0.0"
    assert manifest["name"] == "spec-objects-architecture"
    assert manifest["version"]
    assert isinstance(manifest.get("object_types", []), list)


def _object_types():
    return yaml.safe_load(MANIFEST_PATH.read_text()).get("object_types", [])


@pytest.mark.parametrize("ot", _object_types(), ids=lambda ot: ot["name"])
def test_object_type_has_name_and_data_schema(ot: dict) -> None:
    assert isinstance(ot["name"], str) and len(ot["name"]) > 0
    assert "data_schema" in ot
    assert isinstance(ot["data_schema"], dict)


def test_no_duplicate_object_type_names() -> None:
    names = [ot["name"] for ot in _object_types()]
    assert len(names) == len(set(names)), f"duplicate names: {names}"
