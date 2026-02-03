import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";
import { discoverProjects } from "../src/project-discovery.js";

const makeTempDir = async () =>
  fs.mkdtemp(path.join(os.tmpdir(), "arborist-discovery-"));

const writeIndicator = (dir, name = "tasks.md") =>
  fs.writeFile(path.join(dir, name), "# tasks\n", "utf8");

const sortPaths = (paths) => [...paths].sort();

const removeDir = (dir) => fs.rm(dir, { recursive: true, force: true });

test("discoverProjects includes root and only indicator children", async () => {
  const rootDir = await makeTempDir();
  try {
    await writeIndicator(rootDir);

    const includedChild = path.join(rootDir, "project-a");
    const missingChild = path.join(rootDir, "project-b");
    const hiddenChild = path.join(rootDir, ".hidden");
    const modulesChild = path.join(rootDir, "node_modules");

    await fs.mkdir(includedChild);
    await fs.mkdir(missingChild);
    await fs.mkdir(hiddenChild);
    await fs.mkdir(modulesChild);
    await writeIndicator(includedChild, "todo.md");
    await writeIndicator(hiddenChild, "todo.md");
    await writeIndicator(modulesChild, "todo.md");

    const projects = await discoverProjects(rootDir);
    assert.deepEqual(
      sortPaths(projects),
      sortPaths([rootDir, includedChild])
    );
  } finally {
    await removeDir(rootDir);
  }
});

test("discoverProjects skips root without indicators", async () => {
  const rootDir = await makeTempDir();
  try {
    const includedChild = path.join(rootDir, "project-only");
    await fs.mkdir(includedChild);
    await writeIndicator(includedChild, "SEED.md");

    const projects = await discoverProjects(rootDir);
    assert.deepEqual(sortPaths(projects), sortPaths([includedChild]));
  } finally {
    await removeDir(rootDir);
  }
});
