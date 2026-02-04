import assert from "node:assert/strict";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import {
  formatProjectLayoutIssues,
  formatTemplateLayoutIssues,
  hasProjectLayoutIssues,
  hasTemplateLayoutIssues,
  validateProjectLayout,
  validateTemplateLayout,
} from "../src/template-validation.js";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(testDir, "..");
const templatesDir = path.join(projectRoot, "templates");

test("template layout matches expected structure", async () => {
  const issues = await validateTemplateLayout(templatesDir);
  assert.equal(hasTemplateLayoutIssues(issues), false, formatTemplateLayoutIssues(issues));
});

test("arborist project matches template layout requirements", async () => {
  const issues = await validateProjectLayout(projectRoot);
  assert.equal(hasProjectLayoutIssues(issues), false, formatProjectLayoutIssues(issues));
});
