"""Activation and stakeholder tests, covering FR-001, IT-001 and the
StR-001 validation criteria.

FR-001-AC-2..AC-4 and StR-001-VC-1 need a running
`filament-core-service`; they are environment-gated and their matrix rows stay
`🚧` with that note. That is pre-existing
debt from issue #1, not this issue's, and it is not the semantic suite: the
Quire rows fail rather than skip (see `conftest.py`).
"""

from __future__ import annotations

import json
import os

import pytest

from tests.conftest import (
    MANIFEST_PATH,
    PACKAGE_ROOT,
    SKELETONS_DIR,
    frontmatter,
    load_manifest,
)

FILAMENT_CORE_URL = os.environ.get("FILAMENT_CORE_URL")
needs_filament_core = pytest.mark.skipif(
    not FILAMENT_CORE_URL,
    reason=(
        "FR-001-AC-2..AC-4 / IT-001 need a running filament-core-service. "
        "Set FILAMENT_CORE_URL to run them; the matrix row stays 🚧 until then."
    ),
)


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
    module the service serves."""
    text = (SKELETONS_DIR / "api_endpoint.md").read_text()
    result = quire_engine.validate_document(
        frontmatter(text)["type"], str(PACKAGE_ROOT), text
    )
    assert result["is_valid"]
