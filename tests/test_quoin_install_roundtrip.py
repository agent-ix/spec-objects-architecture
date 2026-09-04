"""Quoin install roundtrip (IT-002, FR-003-AC-5): the module installs into
Quoin with the semantic
contract, and the operator's prior module state is restored unconditionally.

This row is a **Demonstration**: no released Quoin carries the semantic
installer (`agent-ix/quoin` main `3e842ce`, no tag contains it), and the
install mutates the operator's global `quoin module` store. It therefore runs
only when both are true:

* a Quoin whose `module install` understands `path:` is on `PATH`, and
* `QUOIN_INSTALL_ROUNDTRIP=1` is set, which is the operator saying "you may
  touch my global module store".

The restore step runs whether or not the install succeeded (IT-002-SC-06).
"""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest

from tests.conftest import OBJECT_TYPES, PACKAGE_ROOT

OPT_IN = os.environ.get("QUOIN_INSTALL_ROUNDTRIP") == "1"
QUOIN = shutil.which("quoin")

needs_quoin = pytest.mark.skipif(
    not (OPT_IN and QUOIN),
    reason=(
        "IT-002 is a Demonstration against a Quoin built from agent-ix/quoin "
        "main at or after 3e842ce (no release carries the semantic installer), "
        "and it mutates the operator's global module store. Set "
        "QUOIN_INSTALL_ROUNDTRIP=1 with such a Quoin on PATH to run it; the "
        "matrix row stays 🚧 until then."
    ),
)


def quoin(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([QUOIN, *args], capture_output=True, text=True, check=False)


MODULE = "spec-objects-architecture"


def install_spec(entry: dict) -> str:
    """The `quoin module install` source string that reproduces one recorded
    listing entry. `quoin module install` takes a source (`path:`, `github:`,
    `package:`), never a bare module name, so the restore has to rebuild the
    source it recorded — restoring by name silently does nothing."""
    source = entry["source"]
    kind = source["type"]
    if kind == "path":
        return f"path:{source['path']}"
    if kind == "git-subdir":
        ref = f"@{source['ref']}" if source.get("ref") else ""
        return f"github:{source['url']}//{source['path']}{ref}"
    if kind == "git":
        ref = f"@{source['ref']}" if source.get("ref") else ""
        return f"github:{source['url']}{ref}"
    if kind == "npm":
        version = f"@{source['version']}" if source.get("version") else ""
        return f"package:{source['name']}{version}"
    raise AssertionError(f"unknown quoin module source type: {kind}")


def recorded_entry(listing: str) -> dict | None:
    import json

    for entry in json.loads(listing)["plugins"]:
        if entry["name"] == MODULE:
            return entry
    return None


def roundtrip():
    """Record, install, inspect, and restore — the IT-002 procedure. Returns
    the per-step observations so each criterion can assert its own."""
    import json

    before = quoin("module")
    assert before.returncode == 0, before.stderr
    recorded = before.stdout
    prior = recorded_entry(recorded)
    observed = {"recorded": recorded, "prior": prior}
    try:
        install = quoin("module", "install", f"path:{PACKAGE_ROOT}")
        observed["install"] = install
        if install.returncode == 0:
            listing = quoin("module")
            observed["listing"] = listing
            manifest_path = os.path.expanduser(
                "~/.ix/filament/modules/spec-objects-architecture/semantic/package-manifest.json"
            )
            observed["package_manifest_path"] = manifest_path
            if os.path.isfile(manifest_path):
                with open(manifest_path) as handle:
                    observed["package_manifest"] = json.load(handle)
    finally:
        # The restore (spec step 5) runs whether or not the steps above passed,
        # so a failed install never leaves the operator's global module store
        # half-written. The criteria it discharges are asserted by the tests.
        if prior is not None:
            restore = quoin("module", "install", install_spec(prior))
            observed["restore"] = restore
        else:  # pragma: no cover - nothing was installed before the run
            observed["restore"] = quoin("module", "remove", MODULE)
        observed["after"] = quoin("module").stdout
        observed["after_entry"] = recorded_entry(observed["after"])
    return observed


def same_module_state(prior: dict | None, after: dict | None) -> bool:
    """State equality for IT-002-SC-05, ignoring `installedAt`: the criterion
    is that the operator's module resolves to the same bytes from the same
    source, not that the clock did not move."""
    if prior is None or after is None:
        return prior is after
    keys = ("source", "ref", "sha", "resolvedPath", "targetPath")
    return all(prior.get(key) == after.get(key) for key in keys)


@pytest.mark.trace("TC-027", "FR-003-AC-5")
@pytest.mark.integration
@needs_quoin
def test_quoin_module_install_succeeds_and_lists_the_module():
    observed = roundtrip()
    install = observed["install"]
    assert install.returncode == 0, install.stderr
    combined = install.stdout + install.stderr
    assert "semantic." not in combined or "error" not in combined.lower(), combined
    assert "spec-objects-architecture" in observed["listing"].stdout
    assert same_module_state(
        observed["prior"], observed["after_entry"]
    ), "the prior quoin module state was not restored"


@pytest.mark.trace("TC-070", "IT-002-SC-01", "IT-002-SC-02", "IT-002-SC-03")
@pytest.mark.integration
@needs_quoin
def test_the_install_records_the_prior_listing_installs_and_lists_the_module():
    observed = roundtrip()
    assert observed["recorded"] is not None  # step 1: the listing was captured
    assert observed["install"].returncode == 0  # step 2: install exits zero
    combined = observed["install"].stdout + observed["install"].stderr
    assert "semantic." not in combined or "error" not in combined.lower(), combined
    assert "spec-objects-architecture" in observed["listing"].stdout  # step 3


@pytest.mark.trace("IT-002-SC-04", "IT-002-SC-05", "IT-002-SC-06")
@pytest.mark.integration
@needs_quoin
def test_the_roundtrip_derives_the_package_manifest_and_restores_state():
    observed = roundtrip()
    derived = observed.get("package_manifest")  # step 4: derived manifest
    assert derived is not None, observed.get("package_manifest_path")
    assert derived["package"]["identity"] == "agent-ix/spec-objects-architecture"
    assert len(derived["exports"]) == len(OBJECT_TYPES)
    # step 5: the prior source, ref and sha are back
    assert same_module_state(observed["prior"], observed["after_entry"])
    # step 6: the restore ran even though every step above could have failed
    assert observed["restore"].returncode == 0, observed["restore"].stderr
