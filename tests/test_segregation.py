"""FR-016: a risk-control requirement is asked for its segregating element.

Every behavioural row runs the `quire` binary over a corpus built in `tmp_path`
from the committed `design_edges` fixtures (FR, NFR, part, connection, ADR,
data_schema) and the `control` skeleton of the loaded spec-objects-security
module, with the sibling modules resolved from `IX_FILAMENT_MODULES_PATH` as
`test_design_edges.py` does. The manifest names the relations; the engine names
none of them.

Rows that need the spec-artifacts-process `ADR` allowance read it from the loaded
module, so they hold both before and after it lists `segregates_for_requirement`.
"""

from __future__ import annotations

import functools
import json
import pathlib
import re
import tempfile

import pytest
import yaml

from tests.conftest import (
    FIXTURES_DIR,
    MANIFEST_PATH,
    ix_module,
    module_args,
    object_type,
    run_quire,
    validate_bundle,
)

VALID = FIXTURES_DIR / "design_edges" / "valid" / "spec"
MEMBER = "agent-ix/design-fixture"
VERB = "segregates_for_requirement"
INVERSE = "requirement_segregated_by"
FR_REL, NFR_REL = "fr-has-segregation", "nfr-has-segregation"
FR_CHECK, NFR_CHECK = "fr-without-segregation", "nfr-without-segregation"
WHEN_ANY = [
    {"verb": "satisfies", "direction": "outgoing", "other": ["control"]},
    {"verb": "satisfied_by", "direction": "incoming", "other": ["control"]},
]
CLASS_KEYS = (
    "software_safety_class: class-2\n"
    "software_safety_class_assigned_by: Ada Example\n"
    "software_safety_class_rationale: Failure can injure the operator.\n"
)

# template file, template id, and the directory a copy is written to
TEMPLATES = {
    "FR": ("functional/FR-001.md", "FR-001"),
    "NFR": ("functional/NFR-001.md", "NFR-001"),
    "part": ("design/scoring_engine.md", "scoring_engine"),
    "connection": ("design/planner_to_scoring.md", "planner_to_scoring"),
    "ADR": ("design/ADR-001.md", "ADR-001"),
    "data_schema": ("design/order_schema.md", "order_schema"),
}


def _ref(doc_id: str) -> str:
    return f"ix://{MEMBER}/{doc_id}"


def _manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _relations() -> dict[str, dict]:
    return {r["name"]: r for r in _manifest()["traceability"]["required_relations"]}


def _write(root, kind, doc_id, edges=(), extra=""):
    """A copy of the fixture `kind` named `doc_id` whose edges are exactly `edges`."""
    rel, old_id = TEMPLATES[kind]
    text = (VALID / rel).read_text().replace(old_id, doc_id)
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    front = re.sub(r"relationships:\n(?:  .*\n?)+", "", match.group(1)) + "\n" + extra
    if edges:
        front += "relationships:\n" + "".join(
            f'  - target: "{_ref(target)}"\n    type: "{verb}"\n'
            for verb, target in edges
        )
    path = root / "spec" / ("design" if rel.startswith("design") else "functional")
    path.mkdir(parents=True, exist_ok=True)
    (path / f"{doc_id}.md").write_text(
        f"---\n{front.strip()}\n---\n" + text[match.end() :]
    )
    return path / f"{doc_id}.md"


def _control(root, edges=()):
    """The security module's control skeleton, authoring exactly `edges`."""
    text = pathlib.Path(ix_module("spec-objects-security")) / "skeletons/control.md"
    text = text.read_text()
    if edges:
        block = "relationships:\n" + "".join(
            f'  - target: "{_ref(target)}"\n    type: "{verb}"\n'
            for verb, target in edges
        )
        text = text.replace("object: control\n", f"object: control\n{block}", 1)
    (root / "spec").mkdir(parents=True, exist_ok=True)
    (root / "spec" / "CTRL-001.md").write_text(text)


def _scoped(root, fr_edges=(), kind="FR", doc_id="FR-100"):
    """A requirement that satisfies a control, plus that control."""
    _write(root, kind, doc_id, [("satisfies", "CTRL-001"), *fr_edges])
    _control(root)


def _report(root, *extra, design=False):
    args = ["relations", "--json", *module_args(), "--repo", f"{MEMBER}={root}"]
    if design:
        args.append("--design")
    result = run_quire(*args, *extra)
    assert result.returncode == 0, result.stderr
    rows = {}
    for relation in json.loads(result.stdout)["relations"]:
        for row in relation["rows"]:
            rows[(relation["name"], row["document"]["id"])] = row
    return rows


def _linked(row):
    return [(e["id"], e["archetype"]) for e in row["linked"]]


def _findings(result, check):
    return [ln for ln in result.stderr.splitlines() if ln.endswith(f"[{check}]")]


def _single_file(path, **kwargs):
    """Single-file validation, the mode that reports `disallowed-edge-type`."""
    result = run_quire("validate", *module_args(**kwargs), str(path))
    return [ln for ln in result.stderr.splitlines() if "disallowed-edge" in ln]


@pytest.mark.trace("TC-175", "FR-016-AC-1")
def test_fr016_ac1_verb_declared_with_inverse_and_no_duplicate(tmp_path):
    verb = _manifest()["edge_types"][VERB]
    assert verb["inverse"] == INVERSE and verb["category"] == "traceability"
    _scoped(tmp_path)
    result = run_quire(
        "relations", "--json", *module_args(), "--repo", f"{MEMBER}={tmp_path}"
    )
    assert result.returncode == 0, result.stderr
    assert "DuplicateEdgeType" not in result.stderr, result.stderr


@pytest.mark.trace("TC-176", "FR-016-AC-2")
def test_fr016_ac2_part_and_connection_admit_the_verb_toward_requirements(tmp_path):
    for name in ("part", "connection"):
        assert object_type(name)["allowed_links"][VERB] == ["FR", "NFR"]
    _write(tmp_path, "FR", "FR-100")
    _write(tmp_path, "NFR", "NFR-100")
    part = _write(tmp_path, "part", "part_a", [(VERB, "FR-100")])
    conn = _write(tmp_path, "connection", "conn_a", [(VERB, "NFR-100")])
    for path in (part, conn):
        assert _single_file(path) == [], path
    bundle = validate_bundle(MEMBER, tmp_path, "--strict")
    assert "disallowed-edge" not in bundle.stderr, bundle.stderr
    # The control: a part authoring it toward a part is `disallowed-edge-target`.
    _write(tmp_path, "part", "part_b", [(VERB, "part_a")])
    wrong = validate_bundle(MEMBER, tmp_path, "--strict")
    lines = [ln for ln in wrong.stderr.splitlines() if "disallowed-edge-target" in ln]
    assert len(lines) == 1 and "part_b" in lines[0], wrong.stderr


@pytest.mark.trace("TC-177", "FR-016-AC-3")
def test_fr016_ac3_manifest_declares_the_two_relations_after_the_realization_pair():
    manifest = _manifest()
    relations = _relations()
    for name, kind, check in ((FR_REL, "FR", FR_CHECK), (NFR_REL, "NFR", NFR_CHECK)):
        assert relations[name] == {
            "name": name,
            "from": kind,
            "edges": [VERB],
            "to": ["part", "connection", "ADR"],
            "direction": "incoming",
            "check": check,
            "when_any": WHEN_ANY,
        }
    design = manifest["traceability"]["design_relations"]
    assert design[:2] == ["fr-has-design-element", "nfr-has-design-element"]
    assert FR_REL in design[2:] and NFR_REL in design[2:]
    assert design.index(FR_REL) < design.index(NFR_REL)
    # No relation of this requirement lacks the scope.
    assert all("when_any" in relations[name] for name in (FR_REL, NFR_REL))


@pytest.mark.trace("TC-178", "FR-016-AC-4")
def test_fr016_ac4_scoped_fr_without_an_element_is_uncovered_and_reported(tmp_path):
    _scoped(tmp_path)
    row = _report(tmp_path)[(FR_REL, "FR-100")]
    assert row["state"] == "uncovered" and row["linked"] == []
    result = validate_bundle(MEMBER, tmp_path)
    assert result.returncode == 0, result.stderr
    findings = _findings(result, FR_CHECK)
    assert len(findings) == 1 and "FR-100" in findings[0], result.stderr


@pytest.mark.trace("TC-179", "FR-016-AC-5")
def test_fr016_ac5_part_connection_adr_and_inverse_cover_the_requirement(tmp_path):
    for kind, element in (
        ("part", "part_a"),
        ("connection", "conn_a"),
        ("ADR", "ADR-100"),
    ):
        root = tmp_path / kind
        _scoped(root)
        _write(root, kind, element, [(VERB, "FR-100")])
        row = _report(root)[(FR_REL, "FR-100")]
        assert row["state"] == "covered", kind
        assert _linked(row) == [(element, kind)], kind
        assert _findings(validate_bundle(MEMBER, root), FR_CHECK) == [], kind
    inverse = tmp_path / "inverse"
    _scoped(inverse, [(INVERSE, "part_a")])
    _write(inverse, "part", "part_a")
    row = _report(inverse)[(FR_REL, "FR-100")]
    assert row["state"] == "covered" and _linked(row) == [("part_a", "part")]
    both = tmp_path / "both"
    _scoped(both, [(INVERSE, "part_a")])
    _write(both, "part", "part_a", [(VERB, "FR-100")])
    assert _linked(_report(both)[(FR_REL, "FR-100")]) == [("part_a", "part")]


@pytest.mark.trace("TC-180", "FR-016-AC-6")
def test_fr016_ac6_unlinked_requirements_have_no_row_and_wrong_kind_leaves_a_gap(
    tmp_path,
):
    _write(tmp_path, "FR", "FR-100")
    _write(tmp_path, "NFR", "NFR-100")
    rows = _report(tmp_path)
    assert not [key for key in rows if key[0] in (FR_REL, NFR_REL)]
    result = validate_bundle(MEMBER, tmp_path)
    assert _findings(result, FR_CHECK) == [] and _findings(result, NFR_CHECK) == []
    # An edge from an archetype outside `to` leaves an in-scope requirement a gap.
    scoped = tmp_path / "scoped"
    _scoped(scoped)
    _write(scoped, "data_schema", "order_schema", [(VERB, "FR-100")])
    assert _report(scoped)[(FR_REL, "FR-100")]["state"] == "uncovered"
    # The control: the scoped requirement is a row at all.
    assert (FR_REL, "FR-100") in _report(scoped)


@pytest.mark.trace("TC-181", "FR-016-AC-7")
def test_fr016_ac7_realization_and_segregation_are_separate_facts(tmp_path):
    cases = {
        "realizes": ([("realizes_requirement", "FR-100")], "uncovered", "covered"),
        "segregates": ([(VERB, "FR-100")], "covered", "uncovered"),
        "both": (
            [("realizes_requirement", "FR-100"), (VERB, "FR-100")],
            "covered",
            "covered",
        ),
    }
    for name, (edges, segregation, realization) in cases.items():
        root = tmp_path / name
        _scoped(root)
        _write(root, "part", "part_a", edges)
        rows = _report(root)
        assert rows[(FR_REL, "FR-100")]["state"] == segregation, name
        assert rows[("fr-has-design-element", "FR-100")]["state"] == realization, name


@pytest.mark.trace("TC-182", "FR-016-AC-8")
def test_fr016_ac8_finding_is_a_tunable_warning(tmp_path):
    _scoped(tmp_path)
    plain = validate_bundle(MEMBER, tmp_path)
    assert _findings(plain, FR_CHECK)[0].startswith("warning:"), plain.stderr
    promoted = validate_bundle(
        MEMBER, tmp_path, "--severity", f"trace:{FR_CHECK}=error"
    )
    assert promoted.returncode != 0, promoted.stderr
    assert len(_findings(promoted, FR_CHECK)) == 1
    off = validate_bundle(MEMBER, tmp_path, "--severity", f"trace:{FR_CHECK}=off")
    assert _findings(off, FR_CHECK) == [], off.stderr


@pytest.mark.trace("TC-183", "FR-016-AC-9")
def test_fr016_ac9_the_part_class_is_never_read(tmp_path):
    _scoped(tmp_path)
    _write(tmp_path, "FR", "FR-200", [("satisfies", "CTRL-001")])
    _write(tmp_path, "part", "part_classed", [(VERB, "FR-100")], extra=CLASS_KEYS)
    _write(tmp_path, "part", "part_plain", [(VERB, "FR-200")])
    rows = _report(tmp_path)
    assert rows[(FR_REL, "FR-100")]["state"] == "covered"
    assert rows[(FR_REL, "FR-200")]["state"] == "covered"
    result = validate_bundle(MEMBER, tmp_path)
    assert _findings(result, FR_CHECK) == [], result.stderr
    # A part that states no class does not make the segregated requirement a gap,
    # and the declared relations name no class field.
    assert "software_safety_class" not in json.dumps(
        [_relations()[FR_REL], _relations()[NFR_REL]]
    )


@pytest.mark.trace("TC-184", "FR-016-AC-10")
def test_fr016_ac10_classed_fr_rows_are_what_a_class_policy_reads(tmp_path):
    """The design join rows the `segregation` kind reads (quoin FR-161).

    The quoin `class obligations` command itself is not run here: it reads the
    rows below, and the installed quoin does not yet accept the `relation` key.
    """
    _write(tmp_path, "FR", "FR-100", [("satisfies", "CTRL-001")], extra=CLASS_KEYS)
    _write(tmp_path, "FR", "FR-300", extra=CLASS_KEYS)
    _write(tmp_path, "FR", "FR-400")
    _control(tmp_path)
    before = _report(tmp_path, design=True)
    assert before[(FR_REL, "FR-100")]["state"] == "uncovered"
    assert not [key for key in before if key[0] == FR_REL and key[1] != "FR-100"]
    _write(tmp_path, "part", "part_a", [(VERB, "FR-100")])
    after = _report(tmp_path, design=True)
    assert after[(FR_REL, "FR-100")]["state"] == "covered"
    assert _linked(after[(FR_REL, "FR-100")]) == [("part_a", "part")]


@pytest.mark.trace("TC-185", "FR-016-AC-11")
def test_fr016_ac11_a_control_satisfied_by_edge_puts_the_requirement_in_scope(
    tmp_path,
):
    for kind, doc_id, relation, check in (
        ("FR", "FR-100", FR_REL, FR_CHECK),
        ("NFR", "NFR-100", NFR_REL, NFR_CHECK),
    ):
        root = tmp_path / kind
        _write(root, kind, doc_id)
        _control(root, [("satisfied_by", doc_id)])
        assert _report(root)[(relation, doc_id)]["state"] == "uncovered"
        findings = _findings(validate_bundle(MEMBER, root), check)
        assert len(findings) == 1 and doc_id in findings[0], findings
        _write(root, "part", "part_a", [(VERB, doc_id)])
        assert _report(root)[(relation, doc_id)]["state"] == "covered"
        assert _findings(validate_bundle(MEMBER, root), check) == []


def _process_lists_verb() -> bool:
    manifest = yaml.safe_load(
        (
            pathlib.Path(ix_module("spec-artifacts-process")) / "manifest.yaml"
        ).read_text()
    )
    adr = next(a for a in manifest["artifact_types"] if a["name"] == "ADR")
    return VERB in (adr["allowed_links"] or {})


@pytest.mark.trace("TC-186", "FR-016-AC-12")
def test_fr016_ac12_adr_edge_counts_and_the_advisory_follows_process(
    tmp_path,
):
    _scoped(tmp_path)
    adr = _write(tmp_path, "ADR", "ADR-100", [(VERB, "FR-100")])
    row = _report(tmp_path)[(FR_REL, "FR-100")]
    assert row["state"] == "covered" and _linked(row) == [("ADR-100", "ADR")]
    advisory = [ln for ln in _single_file(adr) if VERB in ln]
    # Until spec-artifacts-process lists the verb for ADR the advisory names it.
    assert bool(advisory) is (not _process_lists_verb()), advisory
    # The requirement authoring the inverse toward the ADR draws none.
    inverse = tmp_path / "inverse"
    _write(inverse, "FR", "FR-100", [("satisfies", "CTRL-001"), (INVERSE, "ADR-100")])
    _control(inverse)
    _write(inverse, "ADR", "ADR-100")
    assert _single_file(inverse / "spec/functional/FR-100.md") == []


@pytest.mark.trace("TC-187", "FR-016-AC-13")
def test_fr016_ac13_a_realized_but_unsegregated_requirement_names_its_own_token(
    tmp_path,
):
    _scoped(tmp_path)
    _write(tmp_path, "part", "part_a", [("realizes_requirement", "FR-100")])
    rows = _report(tmp_path)
    assert rows[("fr-has-design-element", "FR-100")]["state"] == "covered"
    assert rows[(FR_REL, "FR-100")]["state"] == "uncovered"
    matrix = run_quire(
        "matrix", "--strict", *module_args(), "--repo", f"{MEMBER}={tmp_path}"
    )
    assert matrix.returncode == 1, matrix.stdout + matrix.stderr
    gaps = [ln for ln in (matrix.stdout + matrix.stderr).splitlines() if "FR-100" in ln]
    assert any(FR_CHECK in ln for ln in gaps), gaps
    assert not any("requirement-without-design" in ln for ln in gaps), gaps


@pytest.mark.trace("TC-188", "FR-016-AC-14")
def test_fr016_ac14_control_vocabulary_is_declared_while_security_is_loaded(
    tmp_path,
):
    _write(tmp_path, "FR", "FR-100")
    result = validate_bundle(MEMBER, tmp_path, process=False)
    named = [ln for ln in result.stderr.splitlines() if "undeclared-relation" in ln]
    # The control: the engine does report an undeclared kind (`ADR`, absent here),
    # for each relation of this requirement, as advisories.
    adr = [ln for ln in named if "'ADR'" in ln]
    assert any(FR_REL in ln for ln in adr), result.stderr
    assert any(NFR_REL in ln for ln in adr), result.stderr
    assert all(ln.startswith("warning:") for ln in named)
    # `control` is declared by the loaded security module: no finding names it.
    assert not [ln for ln in named if "'control'" in ln], named


SECURITY_OFF_REASON = (
    "PLAT-1856: quire silently drops every loaded relation when a relation with "
    "`record_keys` names a kind no loaded module declares. With spec-objects-security "
    "off this module's `connection-carries-classification`, "
    "`classification-carried-by-connection` (data_classification) and "
    "`connection-crosses-trust-boundary` (trust_boundary) do that, so the report "
    "is empty and no `undeclared-relation-vocabulary` naming `control` appears"
)


@functools.cache
def _engine_reports_undeclared_vocabulary_without_security() -> bool:
    """PLAT-1856 probe: with security off, does the engine still report an
    undeclared kind (the `ADR` relations name one when no process module loads)?"""
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        _write(root, "FR", "FR-100")
        result = validate_bundle(MEMBER, root, process=False, security=False)
    return "undeclared-relation-vocabulary" in result.stderr


@pytest.mark.trace("TC-188", "FR-016-AC-14")
@pytest.mark.xfail(
    condition=not _engine_reports_undeclared_vocabulary_without_security(),
    strict=True,
    reason=SECURITY_OFF_REASON,
)
def test_fr016_ac14_security_off_reports_the_undeclared_control_vocabulary(tmp_path):
    _write(tmp_path, "FR", "FR-100")
    result = validate_bundle(MEMBER, tmp_path, security=False)
    named = [
        ln
        for ln in result.stderr.splitlines()
        if "undeclared-relation-vocabulary" in ln and "'control'" in ln
    ]
    assert any(FR_REL in ln for ln in named), result.stderr
    assert any(NFR_REL in ln for ln in named), result.stderr
    assert all(ln.startswith("warning:") for ln in named)
