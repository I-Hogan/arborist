import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(testDir, "..");
const templatesDir = path.join(projectRoot, "templates");
const arboristTemplatesDir = path.join(templatesDir, "arborist");

const requiredTemplateDirs = ["arborist", "docs", "experiments", "scripts"];
const requiredTemplateRootFiles = [".pre-commit-config.yaml"];
const baseTemplateFiles = [
  "AGENTS.md",
  "backlog.md",
  "feedback.md",
  "tasks.md",
  "todo.md",
];

const pathExists = async (targetPath) => {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
};

const assertIsDirectory = async (dirPath) => {
  const stats = await fs.stat(dirPath);
  assert.equal(stats.isDirectory(), true, `Expected directory: ${dirPath}`);
};

const assertIsFile = async (filePath) => {
  const stats = await fs.stat(filePath);
  assert.equal(stats.isFile(), true, `Expected file: ${filePath}`);
};

test("template root includes required directories", async () => {
  for (const dirName of requiredTemplateDirs) {
    await assertIsDirectory(path.join(templatesDir, dirName));
  }
});

test("template root includes required files", async () => {
  for (const fileName of requiredTemplateRootFiles) {
    await assertIsFile(path.join(templatesDir, fileName));
  }
});

test("base template files live under templates/arborist", async () => {
  for (const fileName of baseTemplateFiles) {
    await assertIsFile(path.join(arboristTemplatesDir, fileName));
  }
});

test("base template files are not stored in templates root", async () => {
  for (const fileName of baseTemplateFiles) {
    const inRoot = await pathExists(path.join(templatesDir, fileName));
    assert.equal(inRoot, false, `Unexpected template file at root: ${fileName}`);
  }
});
