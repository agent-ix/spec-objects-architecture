#!/usr/bin/env node
/**
 * Emit this module's JSON Schemas from `typespec/main.tsp` (FR-002).
 *
 * Runs the official `@typespec/json-schema` emitter through `tsp compile`,
 * keeps only the schemas of this module's namespace, normalizes any `$id` or
 * `$ref` the emitter left relative, writes `spec_objects_architecture/schemas/`
 * plus `toolchain.json`, and rewrites `manifest.yaml`'s `data_schema.digest`
 * values textually so the file's YAML anchors and comments survive.
 *
 *   node scripts/generate-schemas.mjs            # regenerate
 *   node scripts/generate-schemas.mjs --check    # write nothing; fail on any difference
 *
 * FR-002-CON-1: the official emitter only. A wrong schema is fixed in
 * `typespec/main.tsp` and regenerated, never hand-edited here.
 * Node built-ins only, zero dependencies.
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const MIN_NODE_MAJOR = 20;
const SEMANTIC_CORE_BASE = "https://schemas.agent-ix.org/semantic-core/0.1.0/";
const NORMALIZATION = {
  name: "absolute-id-and-ref",
  version: "1.0.0",
  issue: "https://github.com/agent-ix/spec-objects-architecture/issues/8",
};

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourceDir = resolve(repoRoot, "typespec");
const packageDir = resolve(repoRoot, "spec_objects_architecture");
const outputDir = resolve(packageDir, "schemas");
const toolchainPath = resolve(outputDir, "toolchain.json");
const manifestPath = resolve(packageDir, "manifest.yaml");

class GenerateError extends Error {}

function fail(message) {
  throw new GenerateError(message);
}

function requireNode() {
  const major = Number(process.versions.node.split(".")[0]);
  if (!Number.isFinite(major) || major < MIN_NODE_MAJOR) {
    fail(
      `Node ${MIN_NODE_MAJOR} or later is required by @typespec/compiler 1.15.0; this is Node ${process.versions.node}.`,
    );
  }
}

function dependencyVersion(name) {
  const path = resolve(repoRoot, "node_modules", name, "package.json");
  if (!existsSync(path))
    fail(`${name} is not installed; run \`npm ci\` before \`make schemas\`.`);
  return JSON.parse(readFileSync(path, "utf8")).version;
}

/** The manifest `version`, read without a YAML parser so the file is never reserialized. */
function manifestVersion() {
  const match = readFileSync(manifestPath, "utf8").match(/^version:\s*(\S+)\s*$/m);
  if (!match) fail(`${relative(repoRoot, manifestPath)} declares no top-level version`);
  return match[1];
}

/** The `@jsonSchema` base declared by the source, checked against the manifest version. */
function moduleBase() {
  const source = readFileSync(resolve(sourceDir, "main.tsp"), "utf8");
  const declared = source.match(/@jsonSchema\("([^"]+)"\)/)?.[1];
  if (!declared) fail("typespec/main.tsp declares no @jsonSchema base");
  const version = manifestVersion();
  const expected = `https://schemas.agent-ix.org/agent-ix/spec-objects-architecture/${version}/`;
  if (declared !== expected) {
    fail(
      `@jsonSchema base version and manifest version disagree:\n` +
        `  typespec/main.tsp: ${declared}\n` +
        `  manifest.yaml version: ${version} (expected base ${expected})\n` +
        `A version bump edits both in one commit (FR-002-CON-5).`,
    );
  }
  return declared;
}

function compile(scratch) {
  // FR-002 Behavior: an unresolvable `tsp` exits non-zero *naming the missing
  // binary*. Without this check the failure surfaces as a Node
  // `MODULE_NOT_FOUND` stack inside "tsp compile failed", which names the
  // symptom rather than the missing toolchain.
  const cli = resolve(repoRoot, "node_modules/@typespec/compiler/entrypoints/cli.js");
  if (!existsSync(cli)) {
    fail(
      `@typespec/compiler is not resolvable at ${relative(repoRoot, cli)}; ` +
        "run `npm ci` before `make schemas`.",
    );
  }
  try {
    execFileSync(
      process.execPath,
      [
        cli,
        "compile",
        sourceDir,
        "--output-dir",
        scratch,
      ],
      { cwd: repoRoot, stdio: "pipe", encoding: "utf8" },
    );
  } catch (error) {
    const detail = [error.stdout, error.stderr].filter(Boolean).join("\n").trim();
    fail(`tsp compile failed; the committed output was not touched.\n${detail}`);
  }
}

/**
 * Rewrite a relative `$id`/`$ref` to an absolute one: a file this module emits
 * resolves under the module base, anything else under the semantic-core base.
 *
 * Only a bare `<File>.json` is rewritten. A fragment (`#/$defs/Foo`) and a
 * file-plus-fragment (`Foo.json#/$defs/Bar`) are refused rather than guessed:
 * prefixing a base onto a fragment produces a URI that resolves to nothing and
 * that no downstream check would catch, so the generator stops instead of
 * emitting it. Neither shape occurs today — `toolchain.json` records
 * `applied: false` — and this is the guard for the day the emitter changes.
 */
function normalize(schemas, base, moduleFiles) {
  const rewritten = new Set();
  const absolutize = (name, value) => {
    if (typeof value !== "string" || /^https?:\/\//.test(value)) return value;
    if (value.includes("#")) {
      fail(
        `${name} carries a relative reference with a fragment (${value}); the ` +
          "normalizer rewrites bare file names only. Fix the source or extend " +
          "the normalizer deliberately — the committed output was not touched.",
      );
    }
    if (!value.endsWith(".json")) {
      fail(
        `${name} carries a relative reference that is not a schema file name ` +
          `(${value}); the committed output was not touched.`,
      );
    }
    rewritten.add(name);
    return moduleFiles.has(value) ? `${base}${value}` : `${SEMANTIC_CORE_BASE}${value}`;
  };
  const walk = (name, node) => {
    if (Array.isArray(node)) {
      for (const item of node) walk(name, item);
      return;
    }
    if (!node || typeof node !== "object") return;
    for (const key of ["$id", "$ref"]) {
      if (key in node) node[key] = absolutize(name, node[key]);
    }
    for (const [key, value] of Object.entries(node)) {
      if (key !== "$id" && key !== "$ref") walk(name, value);
    }
  };
  for (const [name, schema] of schemas) walk(name, schema);
  return [...rewritten].sort();
}

function render(schema) {
  return `${JSON.stringify(schema, null, 2)}\n`;
}

function emit() {
  requireNode();
  const base = moduleBase();
  const scratch = mkdtempSync(join(tmpdir(), "spec-objects-architecture-emit-"));
  try {
    compile(scratch);
    const all = readdirSync(scratch)
      .filter((name) => name.endsWith(".json"))
      .sort()
      .map((name) => [name, JSON.parse(readFileSync(join(scratch, name), "utf8"))]);
    // Keep this module's namespace only; the emitter re-emits every imported
    // library's models beside them.
    const mine = all.filter(
      ([, schema]) => typeof schema.$id === "string" && schema.$id.startsWith(base),
    );
    if (mine.length === 0) {
      fail(
        `tsp compile emitted no schema under ${base}; the committed output was not touched.`,
      );
    }
    const moduleFiles = new Set(mine.map(([name]) => name));
    const rewrittenFiles = normalize(mine, base, moduleFiles);
    const rendered = new Map(mine.map(([name, schema]) => [name, render(schema)]));

    const digests = new Map(
      [...rendered].map(([name, text]) => [
        name,
        `sha256:${createHash("sha256").update(text, "utf8").digest("hex")}`,
      ]),
    );
    const overall = createHash("sha256");
    for (const [name, text] of rendered) overall.update(`${name}\n${text}`);

    const toolchain = {
      compiler: {
        name: "@typespec/compiler",
        version: dependencyVersion("@typespec/compiler"),
      },
      emitter: {
        name: "@typespec/json-schema",
        version: dependencyVersion("@typespec/json-schema"),
      },
      semanticCore: {
        name: "@agent-ix/semantic-core",
        version: dependencyVersion("@agent-ix/semantic-core"),
      },
      base,
      normalization: {
        ...NORMALIZATION,
        applied: rewrittenFiles.length > 0,
        rewrittenFiles,
        note:
          rewrittenFiles.length === 0
            ? "no-op: the emitter left no relative $id or $ref"
            : "rewrote relative $id/$ref to the module base or semantic-core 0.1.0",
      },
      files: [...rendered.keys()],
      digest: `sha256:${overall.digest("hex")}`,
    };
    return { rendered, toolchain: render(toolchain), digests };
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
}

/**
 * Textual digest rewrite: replace the `digest:` line that follows each
 * `schema: schemas/<File>` line. Anchors, aliases and comments are untouched
 * because the file is never parsed or reserialized.
 */
function manifestWithDigests(digests) {
  const lines = readFileSync(manifestPath, "utf8").split("\n");
  const problems = [];
  let pending = null;
  // A `digest:` belongs to the `schema:` line immediately above it. Carrying
  // `pending` any further would let an unrelated `digest:` key elsewhere in the
  // manifest be overwritten with that schema's hash, and would let a `schema:`
  // line with no digest pass unnoticed.
  const out = lines.map((line) => {
    const schema = line.match(/^(\s*)schema:\s*schemas\/(\S+)\s*$/);
    if (schema) {
      if (pending) {
        problems.push(`manifest declares schemas/${pending} with no digest line`);
      }
      pending = schema[2];
      return line;
    }
    const digest = line.match(/^(\s*)digest:\s*(\S*)\s*$/);
    const claimed = pending;
    pending = null;
    if (digest && claimed) {
      const expected = digests.get(claimed);
      if (!expected) {
        problems.push(`manifest references schemas/${claimed}, which is not emitted`);
        return line;
      }
      return `${digest[1]}digest: ${expected}`;
    }
    if (claimed) {
      problems.push(`manifest declares schemas/${claimed} with no digest line`);
    }
    return line;
  });
  if (pending) {
    problems.push(`manifest declares schemas/${pending} with no digest line`);
  }
  if (problems.length > 0) fail(problems.join("\n"));
  return out.join("\n");
}

function readIfPresent(path) {
  try {
    return readFileSync(path, "utf8");
  } catch {
    return undefined;
  }
}

function check(rendered, toolchain, manifestText) {
  const problems = [];
  for (const [name, text] of rendered) {
    const path = join(outputDir, name);
    if (readIfPresent(path) !== text) problems.push(relative(repoRoot, path));
  }
  let committed = [];
  try {
    committed = readdirSync(outputDir).filter((name) => name.endsWith(".json"));
  } catch {
    problems.push(`${relative(repoRoot, outputDir)} (missing; run \`make schemas\`)`);
  }
  for (const name of committed) {
    if (name !== "toolchain.json" && !rendered.has(name)) {
      problems.push(`${relative(repoRoot, join(outputDir, name))} (stale)`);
    }
  }
  if (readIfPresent(toolchainPath) !== toolchain) {
    problems.push(relative(repoRoot, toolchainPath));
  }
  if (readIfPresent(manifestPath) !== manifestText) {
    problems.push(`${relative(repoRoot, manifestPath)} (data_schema.digest)`);
  }
  return problems;
}

function write(rendered, toolchain, manifestText) {
  mkdirSync(outputDir, { recursive: true });
  for (const name of readdirSync(outputDir)) {
    if (name.endsWith(".json") && name !== "toolchain.json" && !rendered.has(name)) {
      rmSync(join(outputDir, name));
    }
  }
  for (const [name, text] of rendered) writeFileSync(join(outputDir, name), text);
  writeFileSync(toolchainPath, toolchain);
  writeFileSync(manifestPath, manifestText);
}

function main() {
  // Only `--check` is recognised. A typo (`--dry-run`, `-check`) must not fall
  // through to the write path and exit 0 as though it had checked something.
  const args = process.argv.slice(2);
  const unknown = args.filter((arg) => arg !== "--check");
  if (unknown.length > 0) {
    fail(`unknown argument(s): ${unknown.join(" ")}. The only option is --check.`);
  }
  const checking = args.includes("--check");
  const { rendered, toolchain, digests } = emit();
  const manifestText = manifestWithDigests(digests);
  if (checking) {
    const problems = check(rendered, toolchain, manifestText);
    if (problems.length > 0) {
      console.error(
        `emitted schemas differ from the committed output:\n  ${problems.join("\n  ")}\n` +
          "Run `make schemas` and commit the result.",
      );
      process.exit(1);
    }
    console.log(`schemas-check: ${rendered.size} schema(s) match the committed output`);
    return;
  }
  write(rendered, toolchain, manifestText);
  console.log(
    `schemas: wrote ${rendered.size} schema(s) + toolchain.json to ${relative(repoRoot, outputDir)}`,
  );
}

try {
  main();
} catch (error) {
  if (error instanceof GenerateError) {
    console.error(error.message);
    process.exit(1);
  }
  throw error;
}
