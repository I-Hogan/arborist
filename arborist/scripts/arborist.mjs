#!/usr/bin/env node
import { spawn } from "node:child_process";
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { clearListFiles } from "../src/list-cleanup.js";
import { hasWorkItems } from "../src/list-utils.js";
import { discoverProjects } from "../src/project-discovery.js";
import {
  formatProjectLayoutIssues,
  formatTemplateLayoutIssues,
  hasProjectLayoutIssues,
  hasTemplateLayoutIssues,
  validateProjectLayout,
  validateTemplateLayout,
} from "../src/template-validation.js";

const sleep = (ms) =>
  new Promise((resolve) => {
    setTimeout(resolve, ms);
  });

const parseActiveProjects = (contents) =>
  contents
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0 && !line.startsWith("#"));

const loadActiveProjects = async (activeProjectsPath) => {
  try {
    const contents = await fsp.readFile(activeProjectsPath, "utf8");
    return parseActiveProjects(contents);
  } catch (error) {
    if (error?.code === "ENOENT") {
      return null;
    }
    throw error;
  }
};

const resolveActiveProjects = async (rootDir, activeProjectsPath) => {
  const activeProjects = await loadActiveProjects(activeProjectsPath);
  if (!activeProjects || activeProjects.length === 0) {
    return { projects: null, missing: [] };
  }

  const projects = [];
  const missing = [];
  const seen = new Set();

  for (const entry of activeProjects) {
    if (seen.has(entry)) {
      continue;
    }
    seen.add(entry);

    const resolved = path.resolve(rootDir, entry);
    const relative = path.relative(rootDir, resolved);
    if (relative.startsWith("..") || path.isAbsolute(relative)) {
      missing.push({ entry, reason: "outside the workspace root" });
      continue;
    }

    let stats;
    try {
      stats = await fsp.stat(resolved);
    } catch (error) {
      if (error?.code === "ENOENT") {
        missing.push({ entry, reason: "folder not found" });
        continue;
      }
      throw error;
    }

    if (!stats.isDirectory()) {
      missing.push({ entry, reason: "not a folder" });
      continue;
    }

    projects.push(resolved);
  }

  return { projects, missing };
};

const processProject = async ({ projectDir, arboristDir, repoRoot, timeBudget }) => {
  const projectSetupPath = path.join(arboristDir, "project_setup.md");
  const completeNextItemPath = path.join(arboristDir, "complete_next_item.md");
  const projectArboristDir = path.join(projectDir, "arborist");
  const tasksPath = path.join(projectArboristDir, "tasks.md");
  const todoPath = path.join(projectArboristDir, "todo.md");
  const feedbackPath = path.join(projectArboristDir, "feedback.md");
  const agentsPath = path.join(projectDir, "AGENTS.md");

  const spawnCodexExec = (prompt) => {
    const child = spawn("codex", ["exec", prompt], {
      cwd: repoRoot,
      stdio: ["inherit", "inherit", "pipe"],
    });

    if (child.stderr) {
      child.stderr.pipe(process.stdout);
    }

    return child;
  };

  // Run Codex CLI so it prints the same sanitized summary output as `codex exec`.
  const runCodex = (prompt) =>
    new Promise((resolve, reject) => {
      const child = spawnCodexExec(prompt);

      child.on("error", (error) => {
        if (error.code === "ENOENT") {
          reject(new Error("codex CLI not found on PATH."));
          return;
        }
        reject(error);
      });

      child.on("close", (code) => {
        if (code === 0) {
          resolve();
          return;
        }
        reject(new Error(`codex exec exited with code ${code}`));
      });
    });
  const runCodexWithTimeout = (prompt, timeoutMs) =>
    new Promise((resolve, reject) => {
      const child = spawnCodexExec(prompt);
      let timedOut = false;
      let killTimer;
      const timeout = setTimeout(() => {
        timedOut = true;
        console.log(`codex exec exceeded ${timeoutMs}ms; stopping and retrying.`);
        child.kill("SIGTERM");
        killTimer = setTimeout(() => child.kill("SIGKILL"), 5000);
      }, timeoutMs);

      const cleanup = () => {
        clearTimeout(timeout);
        if (killTimer) {
          clearTimeout(killTimer);
        }
      };

      child.on("error", (error) => {
        cleanup();
        if (error.code === "ENOENT") {
          reject(new Error("codex CLI not found on PATH."));
          return;
        }
        reject(error);
      });

      child.on("close", (code) => {
        cleanup();
        if (timedOut) {
          resolve({ timedOut: true });
          return;
        }
        if (code === 0) {
          resolve({ timedOut: false });
          return;
        }
        reject(new Error(`codex exec exited with code ${code}`));
      });
    });

  const deadline = Date.now() + timeBudget;
  let isFirstTask = true;
  let finishedWithoutWork = false;
  let sawTimeout = false;

  if (!fs.existsSync(projectDir)) {
    console.error(`Project folder not found: ${projectDir}`);
    return;
  }

  const layoutIssues = await validateProjectLayout(projectDir);
  if (hasProjectLayoutIssues(layoutIssues)) {
    const layoutSummary = formatProjectLayoutIssues(layoutIssues);
    const setupPrompt = [
      `Project template files are missing or misplaced in ${projectDir}.`,
      layoutSummary,
      `Follow the project setup instructions in ${projectSetupPath}.`,
      `Read AGENTS.md at ${agentsPath} before you begin if it exists.`,
      "",
      `Project root: ${projectDir}`,
    ].join("\n");
    await runCodex(setupPrompt);
  }

  // Loop until time runs out or arborist/todo.md and arborist/tasks.md have no remaining items.
  while (true) {
    const timeLeft = deadline - Date.now();
    if (timeLeft <= 0) {
      console.log("Time budget reached. Stopping before starting a new task.");
      break;
    }

    if (!fs.existsSync(todoPath) || !fs.existsSync(tasksPath)) {
      console.log("arborist/todo.md or arborist/tasks.md is still missing. Stopping.");
      break;
    }

    let todoContents;
    let tasksContents;
    let feedbackContents = "";
    try {
      todoContents = await fsp.readFile(todoPath, "utf8");
      tasksContents = await fsp.readFile(tasksPath, "utf8");
      if (fs.existsSync(feedbackPath)) {
        feedbackContents = await fsp.readFile(feedbackPath, "utf8");
      }
    } catch (error) {
      console.error(
        `Unable to read arborist/todo.md, arborist/tasks.md, or arborist/feedback.md: ${error.message}`,
      );
      process.exit(1);
    }

    const hasFeedbackItems = feedbackContents ? hasWorkItems(feedbackContents) : false;
    if (!hasWorkItems(todoContents) && !hasWorkItems(tasksContents) && !hasFeedbackItems) {
      console.log(
        "arborist/todo.md, arborist/tasks.md, and arborist/feedback.md have no remaining items. Stopping.",
      );
      finishedWithoutWork = true;
      break;
    }

    // Don't parse todo: point Codex at arborist/todo.md and ask for the next item.
    const promptLines = [
      `Complete the next item in ${todoPath}.`,
      `Follow the instructions in ${completeNextItemPath}.`,
      `Project root: ${projectDir}`,
      `Time remaining: ${Math.max(0, timeLeft)}ms`,
    ];

    if (isFirstTask) {
      promptLines.splice(1, 0, `Before starting, read AGENTS.md at ${agentsPath} if it exists.`);
    }

    const taskPrompt = promptLines.join("\n");

    const execResult = await runCodexWithTimeout(taskPrompt, 10 * 60 * 1000);
    if (execResult.timedOut) {
      sawTimeout = true;
    }
    if (!execResult.timedOut) {
      isFirstTask = false;
    }
  }

  if (finishedWithoutWork && !sawTimeout) {
    await clearListFiles([tasksPath, todoPath, feedbackPath]);
  } else if (finishedWithoutWork && sawTimeout) {
    console.log("Skipping list clearing because a previous task timed out in this run.");
  }
};

const main = async () => {
  const args = process.argv.slice(2);
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const arboristDir = path.resolve(scriptDir, "..");
  const repoRoot = path.resolve(arboristDir, "..");
  const templatesDir = path.join(arboristDir, "templates");
  const activeProjectsPath = path.join(arboristDir, "active_projects");
  const rootDir = path.resolve(args[0] ?? repoRoot);
  if (!fs.existsSync(rootDir)) {
    console.error(`Projects folder not found: ${rootDir}`);
    process.exit(1);
  }

  const templateIssues = await validateTemplateLayout(templatesDir);
  if (hasTemplateLayoutIssues(templateIssues)) {
    const summary = formatTemplateLayoutIssues(templateIssues);
    console.error(`Template layout issues detected in ${templatesDir}:\n${summary}`);
    process.exit(1);
  }

  // Fixed 4-hour budget for each project run.
  const timeBudget = 4 * 60 * 60 * 1000;
  const warnedMissing = new Set();

  while (true) {
    const { projects: configuredProjects, missing } = await resolveActiveProjects(
      rootDir,
      activeProjectsPath,
    );
    const missingSet = new Set(missing.map((entry) => entry.entry));
    for (const entry of warnedMissing) {
      if (!missingSet.has(entry)) {
        warnedMissing.delete(entry);
      }
    }
    for (const missingEntry of missing) {
      if (warnedMissing.has(missingEntry.entry)) {
        continue;
      }
      warnedMissing.add(missingEntry.entry);
      console.warn(
        `Warning: active_projects entry "${missingEntry.entry}" does not match a folder in ${rootDir} (${missingEntry.reason}).`,
      );
    }

    const usingActiveProjects = configuredProjects !== null;
    const projects = configuredProjects ?? (await discoverProjects(rootDir));
    if (projects.length === 0) {
      console.log(
        usingActiveProjects
          ? `No active_projects entries resolved to folders in ${rootDir}.`
          : `No projects with arborist/tasks.md or arborist/todo.md found in ${rootDir}.`,
      );
    }

    for (const projectDir of projects) {
      console.log(`\n=== Arborist: ${projectDir} ===\n`);
      await processProject({
        projectDir,
        arboristDir,
        repoRoot,
        timeBudget,
      });
    }

    console.log("All projects processed. Waiting 60 seconds.");
    await sleep(60 * 1000);
  }
};

main().catch((error) => {
  console.error(error?.message || String(error));
  process.exit(1);
});
