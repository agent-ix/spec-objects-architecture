"""Measured consumer boundaries: what the reference form and the bundle index
cost a downstream consumer today.

Both rows exist so that a claim this specification makes in prose is checked by
a run, and so that the day the blocking issue is fixed the row turns red and is
noticed rather than quietly becoming stale.
"""

from __future__ import annotations

import pytest
import yaml

from tests.conftest import (
    MANIFEST_PATH,
    OBJECT_TYPES,
    SCHEMAS_DIR,
    SKELETONS_DIR,
    frontmatter,
    load_manifest,
)


def snapshots(resolve: bool) -> list[dict]:
    """The object-type snapshots a registry owner would serve. With
    `resolve=False` the manifest's reference form is passed verbatim, which is
    what a consumer sees while `agent-ix/filament-core-service#23` is open."""
    import json

    out = []
    for declared in load_manifest()["object_types"]:
        data_schema = declared["data_schema"]
        if resolve:
            data_schema = json.loads(
                (SCHEMAS_DIR / data_schema["schema"].split("/", 1)[1]).read_text()
            )
        out.append(
            {
                "name": declared["name"],
                "data_schema": data_schema,
                "body_extraction": declared.get("body_extraction"),
                "allowed_links": declared.get("allowed_links"),
            }
        )
    return out


def filament(quire_engine, object_types):
    path = SKELETONS_DIR / "api_endpoint.md"
    return quire_engine.extract_filament_core(
        {
            "project_id": "spec-objects-architecture",
            "document_id": "api-endpoint-001",
            "rel_path": str(path),
            "markdown": path.read_text(),
            "repo_name": "spec-objects-architecture",
            "org": "agent-ix",
            "object_types": object_types,
        }
    )


@pytest.mark.trace("TC-090", "FR-003-AC-8")
def test_the_filament_snapshot_path_refuses_the_reference_form_it_is_handed(
    quire_engine,
):
    """What this row counts: `semantic.data-schema-unresolved-reference`
    diagnostics from `extract_filament_core` when the manifest's ten
    reference-form `data_schema` values are handed to it verbatim. The count is
    ten — one per exported object type — and no object-type snapshot node is
    produced for any of them.

    This is quire-rs FR-069 behaving as specified ("the registry owner resolves
    it before the snapshot is served"), not a defect in this module. The
    registry owner that must resolve it is
    `agent-ix/filament-core-service#23`. Until that lands, a consumer that
    reads this manifest directly and calls the Filament path sees no
    architecture object type at all — which is why the module is advisory-only
    until promotion.
    """
    result = filament(quire_engine, snapshots(resolve=False))
    refused = [
        d
        for d in result["diagnostics"]
        if d["code"] == "semantic.data-schema-unresolved-reference"
    ]
    assert {d["objectType"] for d in refused} == set(OBJECT_TYPES)
    assert all(d["severity"] == "error" for d in refused)


@pytest.mark.trace("TC-090", "FR-003-AC-8")
def test_the_same_schemas_resolved_into_snapshots_are_accepted(quire_engine):
    """The counterpart measurement: once the reference is resolved into the
    shipped schema bytes — what `filament-core-service#23` will do — the same
    ten snapshots are accepted with no unresolved-reference diagnostic."""
    result = filament(quire_engine, snapshots(resolve=True))
    assert not [
        d
        for d in result["diagnostics"]
        if d["code"] == "semantic.data-schema-unresolved-reference"
    ], result["diagnostics"]


@pytest.mark.trace("TC-091", "FR-005-AC-10", "FR-005-CON-3")
def test_the_bundle_index_is_keyed_by_declaration_id(bundle_index):
    """FR-005-CON-3: one entry per declaration, not per file. The three
    `*.sysml.md` alternates declare the same object as their table skeleton and
    share its `id` and `title` by intent."""
    ids = [entry["id"] for entry in bundle_index["objects"]]
    assert len(ids) == len(set(ids))
    assert len(ids) == len(OBJECT_TYPES)


@pytest.mark.trace("TC-091", "FR-005-AC-10", "FR-005-CON-3")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "A bundle index built one entry per document — which is what "
        "`BundleIndex::from_documents` does — lists `data-schema-001` twice "
        "and then reports every reference to it as "
        '`semantic.ambiguous-type: type "ArtifactRecord" names '
        "data-schema-001 and data-schema-001`, naming the same id on both "
        "sides. agent-ix/quire-rs#398 owns collapsing entries that share an "
        "id. The module keys its index by id, which is the correct "
        "construction; this row records that the engine does not yet."
    ),
)
def test_a_per_file_bundle_index_does_not_make_a_declaration_ambiguous_with_itself(
    quire_engine, semantic_module
):
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    objects = []
    for path in sorted(SKELETONS_DIR.glob("*.md")):
        front = frontmatter(path.read_text())
        objects.append({"id": front["id"], "names": [front["id"], front["title"]]})
    path = SKELETONS_DIR / "api_endpoint.md"
    record = quire_engine.extract_semantic(
        {
            "markdown": path.read_text(),
            "module": semantic_module,
            "path": str(path),
            "sourceIdentity": "ix://agent-ix/spec-objects-architecture/api-endpoint-001",
            "bundle": {
                "package": manifest["semantic"]["package"],
                "objects": objects,
                "enumerations": [],
                "imports": {},
            },
        }
    )
    assert not [
        d
        for d in record.get("diagnostics", [])
        if d.get("code") == "semantic.ambiguous-type"
    ], record.get("diagnostics")
