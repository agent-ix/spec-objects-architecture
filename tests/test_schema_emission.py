"""Emission tests for the schema set (FR-002), its `$id`/`$ref` shape, the drift gate,
determinism, packaging, and the version-bump procedure.

Every assertion reads the `$id` version segment from `manifest.yaml`
(FR-002-CON-5); no test hard-codes it.
"""

from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import tarfile
import zipfile

import pytest

from tests.conftest import (
    MANIFEST_PATH,
    MODEL_OF,
    OBJECT_TYPES,
    REPO_ROOT,
    SCHEMAS_DIR,
    SEMANTIC_CORE_BASE,
    SUPPORT_MODELS,
    manifest_version,
    module_base,
)

GENERATOR = REPO_ROOT / "scripts" / "generate-schemas.mjs"


def run_generator(
    *args: str, cwd: pathlib.Path | None = None
) -> subprocess.CompletedProcess:
    """Run the generator that belongs to `cwd`: it resolves its own repo root
    from its file location, so a throwaway tree must run its own copy."""
    root = cwd or REPO_ROOT
    return subprocess.run(
        ["node", str(root / "scripts" / "generate-schemas.mjs"), *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def shipped_schemas() -> dict[str, dict]:
    return {
        path.name: json.loads(path.read_text())
        for path in sorted(SCHEMAS_DIR.glob("*.json"))
        if path.name != "toolchain.json"
    }


def toolchain() -> dict:
    return json.loads((SCHEMAS_DIR / "toolchain.json").read_text())


def worktree_copy(tmp_path: pathlib.Path) -> pathlib.Path:
    """A throwaway copy of the tree the generator needs, so no test mutates the repo."""
    root = tmp_path / "tree"
    root.mkdir(parents=True)
    for item in ("typespec", "scripts", "package.json", "package-lock.json"):
        source = REPO_ROOT / item
        target = root / item
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
    (root / "spec_objects_architecture").mkdir()
    shutil.copy2(MANIFEST_PATH, root / "spec_objects_architecture" / "manifest.yaml")
    shutil.copytree(SCHEMAS_DIR, root / "spec_objects_architecture" / "schemas")
    (root / "node_modules").symlink_to(REPO_ROOT / "node_modules")
    return root


@pytest.mark.trace("TC-010", "FR-002-AC-1")
def test_emitted_set_is_the_thirtyone_files_the_toolchain_records():
    record = toolchain()
    expected = sorted(
        [f"{MODEL_OF[name]}.json" for name in OBJECT_TYPES]
        + [f"{model}.json" for model in SUPPORT_MODELS]
    )
    assert sorted(record["files"]) == expected
    assert len(expected) == 31
    assert sorted(shipped_schemas()) == expected
    assert record["compiler"] == {"name": "@typespec/compiler", "version": "1.15.0"}
    assert record["emitter"] == {"name": "@typespec/json-schema", "version": "1.15.0"}
    assert record["base"] == module_base()


@pytest.mark.trace("TC-011", "FR-002-AC-2")
def test_every_schema_declares_2020_12_and_an_id_matching_its_file_name():
    base = module_base()
    for name, schema in shipped_schemas().items():
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema", name
        assert schema["$id"] == f"{base}{name}", name


@pytest.mark.trace("TC-012", "FR-002-AC-3")
def test_every_ref_resolves_to_a_shipped_sibling_or_semantic_core():
    base = module_base()
    shipped = shipped_schemas()
    refs: list[tuple[str, str]] = []

    def walk(owner: str, node) -> None:
        if isinstance(node, list):
            for item in node:
                walk(owner, item)
        elif isinstance(node, dict):
            if "$ref" in node:
                refs.append((owner, node["$ref"]))
            for key, value in node.items():
                if key != "$ref":
                    walk(owner, value)

    for name, schema in shipped.items():
        walk(name, schema)
    assert refs, "the emitted schemas make no cross-reference at all"
    for owner, ref in refs:
        if ref.startswith(base):
            assert (
                ref[len(base) :] in shipped
            ), f"{owner} references an unshipped sibling {ref}"
        else:
            assert ref.startswith(SEMANTIC_CORE_BASE), f"{owner} references {ref}"


@pytest.mark.trace("TC-013", "FR-002-AC-4")
def test_schemas_check_is_green_on_the_committed_tree_and_names_a_mutation(tmp_path):
    assert run_generator("--check").returncode == 0

    tree = worktree_copy(tmp_path)
    target = tree / "spec_objects_architecture" / "schemas" / "DataSchema.json"
    target.write_text(
        target.read_text().replace('"type": "object"', '"type":  "object"', 1)
    )
    mutated = run_generator("--check", cwd=tree)
    assert mutated.returncode != 0
    assert "DataSchema.json" in mutated.stderr

    tree = worktree_copy(tmp_path / "digest")
    manifest = tree / "spec_objects_architecture" / "manifest.yaml"
    manifest.write_text(
        re.sub(
            r"digest: sha256:\w+",
            "digest: sha256:deadbeef",
            manifest.read_text(),
            count=1,
        )
    )
    digest_run = run_generator("--check", cwd=tree)
    assert digest_run.returncode != 0
    assert "manifest.yaml" in digest_run.stderr


@pytest.mark.trace("TC-014", "FR-002-AC-5")
def test_a_base_version_differing_from_the_manifest_version_fails_naming_both(tmp_path):
    tree = worktree_copy(tmp_path)
    source = tree / "typespec" / "main.tsp"
    source.write_text(source.read_text().replace(f"/{manifest_version()}/", "/9.9.9/"))
    result = run_generator(cwd=tree)
    assert result.returncode != 0
    assert "9.9.9" in result.stderr
    assert manifest_version() in result.stderr


@pytest.mark.trace("TC-015", "FR-002-AC-6")
def test_the_built_wheel_and_sdist_carry_every_exported_schema(tmp_path):
    dist = tmp_path / "dist"
    build = subprocess.run(
        ["poetry", "build", "--output", str(dist)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if build.returncode != 0:
        pytest.fail(f"`poetry build` failed:\n{build.stdout}\n{build.stderr}")
    wheel = next(dist.glob("*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    for name in OBJECT_TYPES:
        assert f"spec_objects_architecture/schemas/{MODEL_OF[name]}.json" in names
    sdist = next(dist.glob("*.tar.gz"))
    with tarfile.open(sdist) as archive:
        members = {pathlib.PurePosixPath(m).parts[1:] for m in archive.getnames()}
    for name in OBJECT_TYPES:
        assert (
            "spec_objects_architecture",
            "schemas",
            f"{MODEL_OF[name]}.json",
        ) in members


@pytest.mark.trace("TC-016", "FR-002-CON-3")
def test_two_generator_runs_over_one_source_are_byte_identical(tmp_path):
    tree = worktree_copy(tmp_path)
    assert run_generator(cwd=tree).returncode == 0
    first = {
        p.name: p.read_bytes()
        for p in (tree / "spec_objects_architecture/schemas").iterdir()
    }
    assert run_generator(cwd=tree).returncode == 0
    second = {
        p.name: p.read_bytes()
        for p in (tree / "spec_objects_architecture/schemas").iterdir()
    }
    assert first == second


@pytest.mark.trace("TC-017", "FR-002-CON-1")
def test_the_build_uses_the_official_emitter_only_and_no_file_is_hand_edited():
    """FR-002-CON-1, inspection: the generator shells out to the official
    compiler and writes only what the emitter produced."""
    source = (REPO_ROOT / "scripts" / "generate-schemas.mjs").read_text()
    assert "@typespec/compiler/entrypoints/cli.js" in source
    assert (
        "@typespec/json-schema"
        in json.loads((REPO_ROOT / "package.json").read_text())["devDependencies"]
    )
    # No emitter of our own, and the only writer of `schemas/` is this script.
    for path in REPO_ROOT.glob("scripts/*.mjs"):
        assert "emitter" not in path.name
    record = toolchain()
    assert record["emitter"]["name"] == "@typespec/json-schema"
    # A hand edit would make the drift gate red; that gate is the standing check.
    assert run_generator("--check").returncode == 0


@pytest.mark.trace("TC-018", "FR-002-CON-2")
def test_no_npmrc_no_local_dependency_and_exact_toolchain_pins():
    assert not (REPO_ROOT / ".npmrc").exists()
    package = json.loads((REPO_ROOT / "package.json").read_text())
    dev = package["devDependencies"]
    assert dev["@typespec/compiler"] == "1.15.0"
    assert dev["@typespec/json-schema"] == "1.15.0"
    assert dev["@agent-ix/semantic-core"] == "0.1.0"
    assert "dependencies" not in package or not package["dependencies"]
    for section in ("dependencies", "devDependencies"):
        for name, spec in (package.get(section) or {}).items():
            assert not spec.startswith(("file:", "link:")), f"{name} -> {spec}"
            assert "<" not in spec, f"{name} carries an upper bound: {spec}"


@pytest.mark.trace("TC-019", "FR-002-CON-4")
def test_the_lockfile_resolves_public_packages_from_npmjs():
    lock = json.loads((REPO_ROOT / "package-lock.json").read_text())
    for path, entry in lock["packages"].items():
        resolved = entry.get("resolved")
        if not resolved:
            continue
        if path.endswith("@agent-ix/semantic-core"):
            assert "npm.ix" in resolved, resolved
        else:
            assert resolved.startswith(
                "https://registry.npmjs.org/"
            ), f"{path} -> {resolved}"


@pytest.mark.trace("TC-071", "FR-002-AC-7")
def test_the_npm_tarball_ships_the_schemas_beside_the_manifest(tmp_path):
    staged = [
        REPO_ROOT / "manifest.yaml",
        REPO_ROOT / "schemas",
        REPO_ROOT / "skeletons",
    ]
    assert not any(path.exists() for path in staged), (
        "the npm payload is already staged at the repository root; a stray "
        "root manifest.yaml makes every Filament tool discover the repo root "
        "as a second module"
    )
    try:
        pack = subprocess.run(
            ["npm", "pack", "--pack-destination", str(tmp_path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        if pack.returncode != 0:
            pytest.fail(f"`npm pack` failed:\n{pack.stdout}\n{pack.stderr}")
        # `postpack` removes the staged copies again; assert it actually ran,
        # because a leftover root manifest.yaml silently breaks `quire validate`.
        assert not any(path.exists() for path in staged), (
            "npm pack left the staged payload at the repository root; "
            "scripts/stage-npm.mjs --clean did not run"
        )
    finally:
        for path in staged:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
    tarball = next(tmp_path.glob("*.tgz"))
    with tarfile.open(tarball) as archive:
        names = set(archive.getnames())
    assert "package/manifest.yaml" in names
    for name in OBJECT_TYPES:
        assert f"package/schemas/{MODEL_OF[name]}.json" in names


@pytest.mark.trace("TC-072", "FR-002-AC-8", "FR-002-CON-5")
def test_a_coordinated_version_bump_reemits_every_id_and_digest(tmp_path):
    tree = worktree_copy(tmp_path)
    old, new = manifest_version(), "9.9.9"
    source = tree / "typespec" / "main.tsp"
    manifest = tree / "spec_objects_architecture" / "manifest.yaml"
    source.write_text(source.read_text().replace(f"/{old}/", f"/{new}/"))

    # Half a bump: the source moved, the manifest did not.
    half = run_generator("--check", cwd=tree)
    assert half.returncode != 0
    assert new in half.stderr and old in half.stderr

    manifest.write_text(
        manifest.read_text().replace(f"\nversion: {old}\n", f"\nversion: {new}\n", 1)
    )
    assert run_generator(cwd=tree).returncode == 0
    bumped_base = (
        f"https://schemas.agent-ix.org/agent-ix/spec-objects-architecture/{new}/"
    )
    out = tree / "spec_objects_architecture" / "schemas"
    for path in out.glob("*.json"):
        if path.name == "toolchain.json":
            assert json.loads(path.read_text())["base"] == bumped_base
            continue
        schema = json.loads(path.read_text())
        assert schema["$id"] == f"{bumped_base}{path.name}"
        assert old not in json.dumps(schema)
    assert run_generator("--check", cwd=tree).returncode == 0


@pytest.mark.trace("TC-073", "FR-002-AC-9")
def test_schemas_check_names_a_stale_committed_schema_and_writes_nothing(tmp_path):
    tree = worktree_copy(tmp_path)
    out = tree / "spec_objects_architecture" / "schemas"
    stale = out / "Stale.json"
    stale.write_text("{}\n")
    before = {p.name: p.read_bytes() for p in out.iterdir()}
    manifest_before = (
        tree / "spec_objects_architecture" / "manifest.yaml"
    ).read_bytes()
    result = run_generator("--check", cwd=tree)
    assert result.returncode != 0
    assert "Stale.json" in result.stderr and "stale" in result.stderr
    after = {p.name: p.read_bytes() for p in out.iterdir()}
    assert before == after
    assert (
        tree / "spec_objects_architecture" / "manifest.yaml"
    ).read_bytes() == manifest_before


@pytest.mark.trace("TC-074", "FR-002-CON-5")
def test_no_test_hard_codes_the_id_version_segment():
    """FR-002-CON-5: a criterion that hard-codes the version churns per release."""
    version = manifest_version()
    literal = f"spec-objects-architecture/{version}/"
    for path in sorted((REPO_ROOT / "tests").rglob("*.py")):
        assert (
            literal not in path.read_text()
        ), f"{path} hard-codes the $id version segment"
