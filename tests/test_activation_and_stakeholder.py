"""Activation and stakeholder tests, covering FR-001, IT-001 and the
StR-001 validation criteria.

FR-001-AC-1 is discharged here against the committed tree, and is an explicit
expected failure while `agent-ix/filament-core-service#25` is open: this
module's manifest carries the FR-043 `lexicon` block, which the FR-035
module-manifest schema (`additionalProperties: false`) does not admit. That
condition predates this issue — the 0.2.0 manifest fails the same way — and
the schema is neither relaxed nor is the `lexicon` dropped to make the row
green.

FR-001-AC-2..AC-4, StR-001-VC-1 and StR-001-VC-2 need a running
`filament-core-service` at revision `a77f31e` or later; they are environment-
gated and their matrix rows stay `🚧` with that note. That is pre-existing
debt from issue #1, not this issue's, and it is not the semantic suite: the
Quire rows fail rather than skip (see `conftest.py`).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess

import pytest

from tests.conftest import (
    MANIFEST_PATH,
    PACKAGE_ROOT,
    REPO_ROOT,
    SKELETONS_DIR,
    frontmatter,
    load_manifest,
)

# The filament-core-service module-manifest schema at revision `a77f31e`
# (CR-003, the revision that admits the `semantic` block and the reference-form
# `data_schema`), vendored byte-identically by Quoin and Quire. FR-001, FR-003
# and IT-001 all judge this manifest against this one revision.
VENDORED_SCHEMA = REPO_ROOT / "tests" / "fixtures" / "module-manifest.schema.json"
VENDORED_SCHEMA_DIGEST = (
    "69cf9738600e7d8daa45ed5cd7231b17ca8dc58d068bd36af9b0d2c9b69dcbbc"
)

FILAMENT_CORE_URL = os.environ.get("FILAMENT_CORE_URL")
needs_filament_core = pytest.mark.skipif(
    not FILAMENT_CORE_URL,
    reason=(
        "FR-001-AC-2..AC-4 / IT-001 need a running filament-core-service at "
        "revision a77f31e or later (no release tag contains it). Set "
        "FILAMENT_CORE_URL to run them; the matrix row stays 🚧 until then."
    ),
)


@pytest.mark.trace("TC-001", "FR-001-AC-1")
def test_the_vendored_fr035_schema_is_the_pinned_revision():
    digest = hashlib.sha256(VENDORED_SCHEMA.read_bytes()).hexdigest()
    assert digest == VENDORED_SCHEMA_DIGEST, (
        "the vendored module-manifest schema is not the a77f31e revision the "
        "spec pins; FR-001 and FR-003 would judge the manifest against "
        "different schemas"
    )


@pytest.mark.trace("TC-001", "FR-001-AC-1")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "FR-035's module-manifest schema is `additionalProperties: false` and "
        "declares no `lexicon` key, while this module has shipped a top-level "
        "`lexicon` since 0.2.0 (FR-043's concrete-term vocabulary, which "
        "quire-rs loads happily). The manifest is therefore refused by the "
        "vendored schema. agent-ix/filament-core-service#25 owns adding "
        "`lexicon` to FR-035. The row is an expected failure naming that "
        "issue; the `lexicon` is not dropped and the schema is not relaxed."
    ),
)
def test_the_manifest_validates_against_the_pinned_fr035_schema(quire_engine):
    violations = quire_engine.validate_manifest(load_manifest(), str(VENDORED_SCHEMA))
    assert violations == [], violations


@pytest.mark.trace("TC-001", "FR-001-AC-1")
def test_the_only_fr035_violation_is_the_known_lexicon_key(quire_engine):
    """What this row counts: the manifest's violations against the pinned
    FR-035 schema. Exactly one, and it is the `lexicon` key of
    agent-ix/filament-core-service#25 — so nothing this issue added is
    refused."""
    violations = quire_engine.validate_manifest(load_manifest(), str(VENDORED_SCHEMA))
    assert len(violations) == 1, violations
    assert "lexicon" in violations[0]["message"], violations


@pytest.mark.trace("TC-002", "FR-001-AC-2")
@pytest.mark.integration
@needs_filament_core
def test_activation_against_a_clean_filament_core_returns_200():
    import urllib.request

    request = urllib.request.Request(
        f"{FILAMENT_CORE_URL.rstrip('/')}/api/v1/modules/activate",
        data=MANIFEST_PATH.read_bytes(),
        headers={"Content-Type": "application/yaml"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        assert response.status == 200


@pytest.mark.trace("TC-003", "FR-001-AC-3")
@pytest.mark.integration
@needs_filament_core
def test_reactivation_is_a_content_hash_no_op():
    import urllib.request

    hashes = []
    for _ in range(2):
        request = urllib.request.Request(
            f"{FILAMENT_CORE_URL.rstrip('/')}/api/v1/modules/activate",
            data=MANIFEST_PATH.read_bytes(),
            headers={"Content-Type": "application/yaml"},
            method="POST",
        )
        with urllib.request.urlopen(request) as response:
            hashes.append(json.loads(response.read())["content_hash"])
    assert hashes[0] == hashes[1]


@pytest.mark.trace("TC-004", "FR-001-AC-4", "TC-005", "StR-001-VC-1")
@pytest.mark.integration
@needs_filament_core
def test_every_declared_contribution_is_readable_from_the_registry_endpoints():
    """FR-001-AC-4 and StR-001-VC-1 observe the same run: activation registers
    the contents this module declares, and each exported object type's
    registered `data_schema` is the reference object as posted while
    agent-ix/filament-core-service#23 is open."""
    import urllib.request

    with urllib.request.urlopen(
        f"{FILAMENT_CORE_URL.rstrip('/')}/api/v1/object-types"
    ) as response:
        registered = {row["name"]: row for row in json.loads(response.read())}
    manifest = load_manifest()
    for declared in manifest["object_types"]:
        row = registered[declared["name"]]
        assert row["data_schema"] == declared["data_schema"]


@pytest.mark.integration
@needs_filament_core
def test_a_shipped_skeleton_validates_against_the_module_the_service_serves(
    quire_engine,
):
    """An artifact authored from a shipped skeleton validates against the
    module the service serves. This carries no StR-001-VC-2 tag: VC-2 is about
    a generator run, which the row below performs."""
    text = (SKELETONS_DIR / "api_endpoint.md").read_text()
    result = quire_engine.validate_document(
        frontmatter(text)["type"], str(PACKAGE_ROOT), text
    )
    assert result["is_valid"]


@pytest.mark.trace("TC-006", "StR-001-VC-2")
def test_the_agent_cli_generator_produces_artifacts_that_validate(
    quire_engine, tmp_path
):
    """StR-001-VC-3's sibling criterion, discharged by a real generator run.

    What this row counts: the thirteen shipped skeletons, each rendered by
    `minijinja-cli` — the agent CLI generator StR-001 names — and then
    validated through Quire against this module. A placeholder-free skeleton
    renders to itself, so the row asserts both halves: the generator produces
    the artifact byte-for-byte, and the artifact validates.

    The row fails, never skips, when the generator is absent: a skipped row is
    not coverage.
    """
    generator = shutil.which("minijinja-cli")
    if generator is None:
        pytest.fail(
            "StR-001-VC-2 names an agent CLI generator (minijinja-cli) and it is "
            "not on PATH. Install it (`cargo install minijinja-cli`) rather than "
            "skipping: a skipped row is not coverage."
        )
    context = tmp_path / "context.json"
    context.write_text("{}\n")
    for path in sorted(SKELETONS_DIR.glob("*.md")):
        run = subprocess.run(
            [generator, str(path), str(context)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert run.returncode == 0, (path.name, run.stderr)
        rendered = run.stdout
        assert rendered == path.read_text(), path.name
        result = quire_engine.validate_document(
            frontmatter(rendered)["type"], str(PACKAGE_ROOT), rendered
        )
        assert result["is_valid"], (path.name, result["errors"])
