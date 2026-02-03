import assert from "node:assert/strict";
import { test } from "node:test";
import { hasWorkItems, readFirstLine } from "../src/list-utils.js";

test("hasWorkItems ignores headers and blank lines", () => {
  const contents = "# Header\n\n# Another header\n";
  assert.equal(hasWorkItems(contents), false);
});

test("hasWorkItems detects non-comment content", () => {
  const contents = "# Header\n\n1. Do the thing\n";
  assert.equal(hasWorkItems(contents), true);
});

test("readFirstLine returns the first line", () => {
  const contents = "First line\nSecond line";
  assert.equal(readFirstLine(contents), "First line");
});
