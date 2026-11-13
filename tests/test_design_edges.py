"""Requirement-to-design edges (FR-010): part, connection and ADR realize FR/NFR.

Every row runs the `quire` binary over the fixture corpus in
`tests/fixtures/design_edges` with this module loaded beside the modules that
declare the requirement and ADR archetypes. The relation report is the engine's
design-element join read through `quire relations --json`; the manifest names
the relations, the engine names none of them.

The `FR`, `NFR` and `ADR` archetypes come from spec-artifacts-iso and
spec-artifacts-process, resolved from the installed filament modules
(`IX_FILAMENT_MODULES_PATH`, default `~/.ix/filament/modules`).
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess

import pytest
import yaml

from tests.conftest import FIXTURES_DIR, MANIFEST_PATH, PACKAGE_ROOT, object_type

CORPUS = FIXTURES_DIR / "design_edges"
VALID = CORPUS / "valid"
INVALID = CORPUS / "invalid"
MEMBER = "agent-ix/design-fixture"
MODULES_ROOT = pathlib.Path(
    os.environ.get("IX_FILAMENT_MODULES_PATH")
    or pathlib.Path.home() / ".ix" / "filament" / "modules"
)


def _module(name: str) -> str:
    path = MODULES_ROOT / name
    assert (path / "manifest.yaml").is_file(), (
        f"{name} is not installed under {MODULES_ROOT}; the design-edge rows "
        "load it beside this module, and a skipped row is not coverage"
    )
    return str(path)


def _modules(*extra: str, process: bool = True) -> list[str]:
    names = ["spec-artifacts-iso"] + (["spec-artifacts-process"] if process else [])
    args: list[str] = []
    for name in names:
        args += ["--module", _module(name)]
    args += ["--module", str(PACKAGE_ROOT)]
    return args + list(extra)


def _run(*args: str) -> subprocess.CompletedProcess:
    assert shutil.which("quire"), "quire CLI not installed"
    return subprocess.run(["quire", *args], capture_output=True, text=True, check=False)


def _report(
    members: dict[str, pathlib.Path], process: bool = True, relation: str | None = None
) -> dict[tuple[str, str], dict]:
    args = ["relations", "--json", *_modules(process=process)]
    for member, root in members.items():
        args += ["--repo", f"{member}={root}"]
    if relation:
        args += ["--relation", relation]
    result = _run(*args)
    assert result.returncode == 0, result.stderr
    rows = {}
    for rel in json.loads(result.stdout)["relations"]:
        for row in rel["rows"]:
            rows[(rel["name"], row["document"]["id"])] = row
    return rows


def _linked(row: dict) -> list[tuple[str, str]]:
    return [(e["id"], e["archetype"]) for e in row["linked"]]


def _bundle(
    root: pathlib.Path, *extra: str, process: bool = True
) -> subprocess.CompletedProcess:
    return _run(
        "validate",
        "--okf",
        *_modules(*extra, process=process),
        "--repo",
        f"{MEMBER}={root}",
    )


def _manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _relations() -> dict[str, dict]:
    return {r["name"]: r for r in _manifest()["traceability"]["required_relations"]}


@pytest.mark.trace("TC-140", "FR-010-AC-1")
def test_fr010_ac1_edge_declared_with_inverse_and_no_realizes_key():
    edges = _manifest()["edge_types"]
    assert edges["realizes_requirement"]["inverse"] == "requirement_realized_by"
    assert edges["realizes_requirement"]["category"] == "traceability"
    assert "realizes" not in edges
    result = _run("validate", *_modules(), str(VALID / "spec/design/scoring_engine.md"))
    assert "DuplicateEdgeType" not in result.stderr


@pytest.mark.trace("TC-141", "FR-010-AC-2")
def test_fr010_ac2_part_and_connection_admit_the_edge_toward_requirements():
    for name in ("part", "connection"):
        assert object_type(name)["allowed_links"]["realizes_requirement"] == [
            "FR",
            "NFR",
        ]
    result = _bundle(VALID)
    for doc in ("scoring_engine.md", "planner_to_scoring.md"):
        for line in result.stderr.splitlines():
            if doc in line:
                assert "disallowed-edge" not in line, line


@pytest.mark.trace("TC-142", "FR-010-AC-3", "FR-010-CON-1")
def test_fr010_ac3_manifest_declares_exactly_the_two_relations():
    manifest = _manifest()
    relations = _relations()
    assert list(relations) == ["fr-has-design-element", "nfr-has-design-element"]
    fields = {
        "fr-has-design-element": ("FR", "requirement-without-design"),
        "nfr-has-design-element": ("NFR", "nfr-without-design"),
    }
    for name, (kind, check) in fields.items():
        rel = relations[name]
        assert rel["from"] == kind
        assert rel["check"] == check
        assert rel["direction"] == "incoming"
        assert rel["edges"] == ["realizes_requirement"]
        assert rel["to"] == ["part", "connection", "ADR"]
    assert manifest["traceability"]["design_relations"] == list(fields)
    assert manifest["object_types"] and not manifest.get("archetypes")
    assert _run("relations", "--json", *_modules(), "--repo", f"{MEMBER}={VALID}")


@pytest.mark.trace("TC-143", "FR-010-AC-4")
def test_fr010_ac4_part_realizing_fr_is_covered_and_unrealized_fr_is_a_gap():
    rows = _report({MEMBER: VALID})
    assert rows[("fr-has-design-element", "FR-001")]["state"] == "covered"
    assert _linked(rows[("fr-has-design-element", "FR-001")]) == [
        ("scoring_engine", "part")
    ]
    assert rows[("fr-has-design-element", "FR-004")]["state"] == "uncovered"
    assert rows[("fr-has-design-element", "FR-004")]["linked"] == []


@pytest.mark.trace("TC-144", "FR-010-AC-5")
def test_fr010_ac5_requirement_authored_inverse_and_both_ways_join_once(tmp_path):
    rows = _report({MEMBER: VALID})
    assert _linked(rows[("fr-has-design-element", "FR-002")]) == [
        ("planner_to_scoring", "connection")
    ]
    # FR-003 authors the inverse toward the part; the part authors nothing for it.
    assert _linked(rows[("fr-has-design-element", "FR-003")]) == [
        ("scoring_engine", "part")
    ]
    both = tmp_path / "both"
    shutil.copytree(VALID, both)
    part = both / "spec/design/scoring_engine.md"
    part.write_text(
        part.read_text().replace(
            'type: "realizes_requirement"\n',
            'type: "realizes_requirement"\n'
            '  - target: "ix://agent-ix/design-fixture/FR-003"\n'
            '    type: "realizes_requirement"\n',
            1,
        )
    )
    rows = _report({MEMBER: both})
    assert _linked(rows[("fr-has-design-element", "FR-003")]) == [
        ("scoring_engine", "part")
    ]


@pytest.mark.trace("TC-145", "FR-010-AC-6")
def test_fr010_ac6_adr_covers_nfr_and_wrong_source_leaves_a_gap_without_mismatch():
    rows = _report({MEMBER: VALID})
    assert _linked(rows[("nfr-has-design-element", "NFR-001")]) == [("ADR-001", "ADR")]
    # A data_schema authors the verb toward FR-004: outside `to`, so FR-004
    # stays a gap and is not reported as a kind mismatch.
    fr4 = rows[("fr-has-design-element", "FR-004")]
    assert fr4["state"] == "uncovered"
    assert fr4["kind_mismatch"] == []
    assert "target-kind-mismatch" not in _bundle(VALID).stderr


@pytest.mark.trace("TC-146", "FR-010-AC-7")
def test_fr010_ac7_cross_repository_part_covers_fr_and_unloaded_member_does_not(
    tmp_path,
):
    req = tmp_path / "req"
    arch = tmp_path / "arch"
    shutil.copytree(VALID / "spec/functional", req / "spec/functional")
    (arch / "spec/design").mkdir(parents=True)
    for name in ("scoring_engine.md", "planner_to_scoring.md", "ADR-001.md"):
        shutil.copy(VALID / "spec/design" / name, arch / "spec/design" / name)
    # In the fixture both documents name `agent-ix/design-fixture`; rewrite the
    # requirement members' identities for the two-member corpus.
    for path in list(req.rglob("*.md")) + list(arch.rglob("*.md")):
        path.write_text(
            path.read_text()
            .replace("ix://agent-ix/design-fixture/FR-", "ix://org/req/FR-")
            .replace("ix://agent-ix/design-fixture/NFR-", "ix://org/req/NFR-")
            .replace(
                "ix://agent-ix/design-fixture/scoring_engine",
                "ix://org/arch/scoring_engine",
            )
            .replace("ix://agent-ix/design-fixture/ADR-001", "ix://org/arch/ADR-001")
        )
    both = _report({"org/req": req, "org/arch": arch})
    row = both[("fr-has-design-element", "FR-001")]
    assert row["state"] == "covered"
    assert row["linked"][0]["repo"] == "org/arch"
    only_req = _report({"org/req": req})
    # The part's repository is not loaded: its edge is absent, so FR-001 is a
    # gap with nothing dangling; FR-003 authors the inverse toward the part and
    # keeps the reference as authored.
    assert only_req[("fr-has-design-element", "FR-001")]["state"] == "uncovered"
    assert only_req[("fr-has-design-element", "FR-001")]["dangling"] == []
    fr3 = only_req[("fr-has-design-element", "FR-003")]
    assert fr3["state"] == "uncovered"
    assert fr3["dangling"]


@pytest.mark.trace("TC-147", "FR-010-AC-8")
def test_fr010_ac8_findings_are_advisory_and_a_key_maps_off():
    result = _bundle(VALID)
    assert "requirement-without-design" in result.stderr
    assert "[requirement-without-design]" in result.stderr
    assert all(
        "requirement-without-design" not in line
        for line in result.stderr.splitlines()
        if line.startswith("error")
    )
    off = _bundle(VALID, "--severity", "trace:requirement-without-design=off")
    assert "requirement-without-design" not in off.stderr


@pytest.mark.trace("TC-148", "FR-010-AC-9")
def test_fr010_ac9_undeclared_adr_vocabulary_is_reported_when_no_adr_exists(tmp_path):
    corpus = tmp_path / "no-adr"
    shutil.copytree(VALID, corpus)
    (corpus / "spec/design/ADR-001.md").unlink()
    nfr = corpus / "spec/functional/NFR-001.md"
    nfr.write_text(
        nfr.read_text().replace(
            'relationships:\n  - target: "ix://agent-ix/design-fixture/ADR-001"\n'
            '    type: "requirement_realized_by"\n',
            "",
        )
    )
    result = _bundle(corpus, process=False)
    lines = [ln for ln in result.stderr.splitlines() if "ADR" in ln]
    assert any("undeclared-relation-vocabulary" in ln for ln in lines), result.stderr


@pytest.mark.trace("TC-149", "FR-010-AC-10")
def test_fr010_ac10_criterion_edge_needs_an_obligations_source(tmp_path):
    corpus = tmp_path / "criterion-only"
    shutil.copytree(VALID, corpus)
    part = corpus / "spec/design/scoring_engine.md"
    part.write_text(
        part.read_text().replace(
            '  - target: "ix://agent-ix/design-fixture/FR-001"\n'
            '    type: "realizes_requirement"\n',
            "",
            1,
        )
    )
    row = _report({MEMBER: corpus})[("fr-has-design-element", "FR-001")]
    assert row["state"] == "covered"
    assert _linked(row) == [("scoring_engine", "part")]
    # spec-artifacts-process is the module that declares an obligations source;
    # without it the criterion edge is not an edge to FR-001.
    bare = _report({MEMBER: corpus}, process=False)[("fr-has-design-element", "FR-001")]
    assert bare["state"] == "uncovered"
    assert bare["dangling"] == []
    # `realized_criteria` is carried by the design join (`relations --design`),
    # which releases after quire 0.45.0.
    if "--design" in _run("relations", "--help").stdout:
        result = _run(
            "relations",
            "--design",
            "--json",
            *_modules(),
            "--repo",
            f"{MEMBER}={corpus}",
        )
        assert result.returncode == 0, result.stderr
        design = json.loads(result.stdout)["relations"][0]["rows"][0]
        assert design["linked"][0]["realized_criteria"] == ["FR-001-AC-1"]


@pytest.mark.trace("TC-150", "FR-010-AC-11")
def test_fr010_ac11_dangling_and_wrong_kind_targets_fail_validate_with_a_location():
    result = _bundle(INVALID, "--strict")
    assert result.returncode == 3, result.stderr
    lines = result.stderr.splitlines()
    dangling = [ln for ln in lines if "dangling-reference" in ln and "FR-999" in ln]
    assert dangling and "dangling_part.md" in dangling[0]
    assert "'realizes_requirement'" in dangling[0]
    wrong = [ln for ln in lines if "disallowed-edge-target" in ln]
    assert wrong and "wrong_kind_part" in wrong[0] and "scoring_engine" in wrong[0]
    # The valid corpus draws neither.
    clean = _bundle(VALID, "--strict").stderr
    assert "dangling-reference" not in clean
    assert "disallowed-edge-target" not in clean
