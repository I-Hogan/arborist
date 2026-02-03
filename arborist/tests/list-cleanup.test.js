import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";
import { clearListFile, clearListFiles } from "../src/list-cleanup.js";

const makeTempDir = async () =>
  fs.mkdtemp(path.join(os.tmpdir(), "arborist-list-cleanup-"));

const writeList = (dir, name, body) =>
  fs.writeFile(path.join(dir, name), body, "utf8");

const readList = (dir, name) =>
  fs.readFile(path.join(dir, name), "utf8");

test("clearListFile preserves the header and clears the rest", async () => {
  const dir = await makeTempDir();
  try {
    const fileName = "todo.md";
    await writeList(dir, fileName, "# Header\n\n1. Do work\n");

    await clearListFile(path.join(dir, fileName));

    const contents = await readList(dir, fileName);
    assert.equal(contents, "# Header\n");
  } finally {
    await fs.rm(dir, { recursive: true, force: true });
  }
});

test("clearListFile is a no-op for missing files", async () => {
  const dir = await makeTempDir();
  try {
    await clearListFile(path.join(dir, "missing.md"));
  } finally {
    await fs.rm(dir, { recursive: true, force: true });
  }
});

test("clearListFiles clears multiple list files", async () => {
  const dir = await makeTempDir();
  try {
    await writeList(dir, "tasks.md", "# Tasks\n\n1. Task\n");
    await writeList(dir, "todo.md", "# Todo\n\n1. Item\n");
    await writeList(dir, "feedback.md", "# Feedback\n\n- Note\n");
    await writeList(dir, "user_requests.md", "# Requests\n\n- Request\n");

    await clearListFiles([
      path.join(dir, "tasks.md"),
      path.join(dir, "todo.md"),
      path.join(dir, "feedback.md"),
      path.join(dir, "user_requests.md"),
      path.join(dir, "missing.md"),
    ]);

    assert.equal(await readList(dir, "tasks.md"), "# Tasks\n");
    assert.equal(await readList(dir, "todo.md"), "# Todo\n");
    assert.equal(await readList(dir, "feedback.md"), "# Feedback\n");
    assert.equal(await readList(dir, "user_requests.md"), "# Requests\n");
  } finally {
    await fs.rm(dir, { recursive: true, force: true });
  }
});
