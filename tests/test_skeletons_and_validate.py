"""Skeleton <-> manifest parity + quire roundtrip tests for the object types.

Mirrors the spec-artifacts-iso pattern, adapted to this module's locator
vocabulary: the seven architecture object types carry no tables or
``id_pattern`` asserts — their ``body_extraction.yield_pattern.match``
locators are ``frontmatter_field``, ``section_body``, and ``code_block``.

Covered here:

* every object type ships a complete worked skeleton under
  ``spec_objects_architecture/skeletons/<name>.md``;
* parity, forward: every asserted ``after_heading`` exists in the skeleton at
  the asserted level (default H2 when the locator declares none) and every
  asserted ``code_block`` exists with the asserted language;
* parity, reverse: skeleton headings at asserted levels cannot drift ahead of
  the manifest contract;
* every ``section_body`` section carries substantive, non-placeholder body;
* the frontmatter anchors (``id``/``title``/``artifact_type``) and each
  type's defining body locator are ``required: true`` in the manifest;
* roundtrip via the quire Python wheel: each skeleton passes
  ``validate_document`` and a required-section deletion fails (skipped
  cleanly when the installed wheel lacks the FR-032 markdown validator).
"""

from __future__ import annotations

import pathlib
import re

import pytest
import yaml

PKG_ROOT = pathlib.Path(__file__).resolve().parent.parent / "spec_objects_architecture"
MANIFEST_PATH = PKG_ROOT / "manifest.yaml"
SKELETONS_DIR = PKG_ROOT / "skeletons"

_PLACEHOLDER_TOKENS = ("TODO", "TBD", "{{", "}}", "placeholder", "none specified")

# The defining body field(s) of each object type — these MUST be
# ``required: true`` in the manifest so `quire validate` is non-trivial.
_REQUIRED_BODY_FIELDS = {
    "api_endpoint": {"endpoint", "routes"},
    "data_schema": {"schema_json"},
    "queue": {"message_schema"},
    "action": {"inputs"},
    "ui_component": {"props"},
    "integration": {"endpoints", "behavior"},
    "rate_limit": {"thresholds"},
}


def _object_types() -> list[dict]:
    return yaml.safe_load(MANIFEST_PATH.read_text()).get("object_types", [])


def _object_type(name: str) -> dict:
    return next(ot for ot in _object_types() if ot["name"] == name)


def _names() -> list[str]:
    return [ot["name"] for ot in _object_types()]


def _match(ot: dict) -> dict:
    be = ot.get("body_extraction") or {}
    return (be.get("yield_pattern") or {}).get("match") or {}


def _body_locators(ot: dict) -> dict[str, dict]:
    """Non-frontmatter locators (``section_body`` / ``code_block``)."""
    return {
        field: loc
        for field, loc in _match(ot).items()
        if isinstance(loc, dict) and loc.get("from") != "frontmatter_field"
    }


def _locator_level(loc: dict) -> int:
    """Heading level a locator pins; the manifest declares none, so H2."""
    return int(loc.get("level", (loc.get("assert") or {}).get("level", 2)))


def _skeleton_path(name: str) -> pathlib.Path:
    return SKELETONS_DIR / f"{name}.md"


def _skeleton_text(name: str) -> str:
    return _skeleton_path(name).read_text()


def _frontmatter(markdown: str) -> dict:
    m = re.match(r"---\n(.*?)\n---\n", markdown, re.DOTALL)
    assert m, "skeleton missing frontmatter"
    return yaml.safe_load(m.group(1))


def _strip_frontmatter(markdown: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", markdown, count=1, flags=re.DOTALL)


def _skeleton_headings(markdown: str) -> list[tuple[int, str]]:
    """Return ``[(level, text)]`` for every ATX heading outside code fences."""
    body = _strip_frontmatter(markdown)
    out: list[tuple[int, str]] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if m:
            out.append((len(m.group(1)), m.group(2).strip()))
    return out


def _split_sections(markdown: str, level: int = 2) -> dict[str, str]:
    """Return ``{section_name: body_text}`` for headings at the given level."""
    body = _strip_frontmatter(markdown)
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    prefix = "#" * level + " "
    in_fence = False
    for line in body.splitlines():
        fence = line.lstrip().startswith("```")
        if fence:
            in_fence = not in_fence
        if not in_fence and not fence and line.startswith(prefix):
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = line[len(prefix) :].strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


# ─── Skeleton presence + frontmatter contract ─────────────────────────────


@pytest.mark.parametrize("name", _names(), ids=lambda n: n)
def test_skeleton_exists(name: str) -> None:
    assert _skeleton_path(name).exists(), f"missing skeleton {_skeleton_path(name)}"


@pytest.mark.parametrize("name", _names(), ids=lambda n: n)
def test_skeleton_frontmatter_matches_anchors(name: str) -> None:
    """Frontmatter seeds id/title/artifact_type; artifact_type names the type
    (quire resolves the archetype from ``artifact_type``)."""
    fm = _frontmatter(_skeleton_text(name))
    for field in ("id", "title", "artifact_type"):
        assert fm.get(field), f"{name}: frontmatter lacks {field!r}"
    assert fm["artifact_type"] == name, (
        f"{name}: frontmatter artifact_type is {fm['artifact_type']!r}; "
        f"it must equal the object type name"
    )


def test_frontmatter_anchor_locators_required() -> None:
    """The shared id/title/artifact_type anchors are ``required: true`` for
    every object type (the YAML anchors are reused across all seven)."""
    for ot in _object_types():
        match = _match(ot)
        for field in ("id", "title", "artifact_type"):
            loc = match[field]
            assert loc["from"] == "frontmatter_field", (ot["name"], field)
            assert (
                loc.get("required") is True
            ), f"{ot['name']}: frontmatter locator {field!r} is not required"


def test_defining_body_locators_required() -> None:
    """Each type's defining body field(s) are ``required: true``."""
    for name, fields in _REQUIRED_BODY_FIELDS.items():
        match = _match(_object_type(name))
        for field in fields:
            assert (
                match[field].get("required") is True
            ), f"{name}: defining locator {field!r} is not required"


# ─── Parity, forward: manifest asserts hold in the skeleton ──────────────


@pytest.mark.parametrize("name", _names(), ids=lambda n: n)
def test_asserted_headings_present_at_level(name: str) -> None:
    """Every asserted ``after_heading`` (section_body AND code_block) exists
    in the skeleton at the asserted level (default H2)."""
    ot = _object_type(name)
    headings = set(_skeleton_headings(_skeleton_text(name)))
    for field, loc in _body_locators(ot).items():
        expected = (_locator_level(loc), loc["after_heading"])
        assert expected in headings, (
            f"{name}: asserted heading {loc['after_heading']!r} "
            f"(H{expected[0]}, locator {field!r}) absent from skeleton"
        )


@pytest.mark.parametrize("name", _names(), ids=lambda n: n)
def test_asserted_code_blocks_present_with_language(name: str) -> None:
    """Every ``code_block`` locator finds a fenced block with the asserted
    language inside its ``after_heading`` section."""
    ot = _object_type(name)
    sections = _split_sections(_skeleton_text(name))
    for field, loc in _body_locators(ot).items():
        if loc.get("from") != "code_block":
            continue
        section = sections.get(loc["after_heading"])
        assert (
            section is not None
        ), f"{name}: code_block locator {field!r} section missing"
        language = loc["language"]
        assert f"```{language}" in section, (
            f"{name}: section {loc['after_heading']!r} lacks a "
            f"```{language} code block (locator {field!r})"
        )


# ─── Parity, reverse: skeleton cannot drift ahead of the contract ─────────


@pytest.mark.parametrize("name", _names(), ids=lambda n: n)
def test_skeleton_headings_do_not_drift(name: str) -> None:
    """Every skeleton heading at an asserted level maps back to a manifest
    locator's ``after_heading`` — the skeleton cannot carry sections the
    contract knows nothing about."""
    ot = _object_type(name)
    asserted = {
        (_locator_level(loc), loc["after_heading"])
        for loc in _body_locators(ot).values()
    }
    asserted_levels = {lvl for lvl, _ in asserted}
    for lvl, text in _skeleton_headings(_skeleton_text(name)):
        if lvl in asserted_levels:
            assert (lvl, text) in asserted, (
                f"{name}: skeleton heading {text!r} (H{lvl}) is not asserted "
                f"by the manifest (skeleton drifted ahead of the contract)"
            )


# ─── Substantive bodies for section_body locators ─────────────────────────


@pytest.mark.parametrize("name", _names(), ids=lambda n: n)
def test_section_bodies_substantive(name: str) -> None:
    """Every ``section_body`` section carries non-empty, non-placeholder
    content in the skeleton."""
    ot = _object_type(name)
    sections = _split_sections(_skeleton_text(name))
    for field, loc in _body_locators(ot).items():
        if loc.get("from") != "section_body":
            continue
        heading = loc["after_heading"]
        assert heading in sections, f"{name}: section_body {heading!r} missing"
        body = sections[heading]
        assert body, f"{name}: section_body {heading!r} is empty in skeleton"
        lowered = body.lower()
        for token in _PLACEHOLDER_TOKENS:
            assert token.lower() not in lowered, (
                f"{name}: section_body {heading!r} carries placeholder "
                f"token {token!r} (locator {field!r})"
            )


# ─── Roundtrip against the quire wheel (guarded) ──────────────────────────


def _quire_doc_validator():
    """Return the quire wheel iff it exposes the FR-032 markdown validator."""
    try:
        import quire
    except ImportError:
        return None
    if not hasattr(quire, "validate_document"):
        return None
    return quire


@pytest.mark.parametrize("name", _names(), ids=lambda n: n)
def test_skeleton_validates_via_quire(name: str) -> None:
    """Each filled skeleton passes ``validate_document``.

    Skips when the installed quire wheel predates the markdown-default
    validator (FR-032); install a quire wheel >=0.3.6 to exercise it."""
    quire = _quire_doc_validator()
    if quire is None:
        pytest.skip("quire wheel lacks validate_document (FR-032)")
    res = quire.validate_document(name, str(PKG_ROOT), _skeleton_text(name))
    assert res["is_valid"], res["errors"]


def test_required_section_deletion_fails_via_quire() -> None:
    """Deleting a required section makes ``validate_document`` fail."""
    quire = _quire_doc_validator()
    if quire is None:
        pytest.skip("quire wheel lacks validate_document (FR-032)")
    base = _skeleton_text("rate_limit")
    mutated = base.replace("## Thresholds", "## Ceilings")
    assert mutated != base, "mutation did not apply"
    res = quire.validate_document("rate_limit", str(PKG_ROOT), mutated)
    assert not res["is_valid"], "required-section deletion still validated"
