#!/usr/bin/env node
import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

// Treat a title-only list file as "done" without parsing task contents.
const hasWorkItems = (contents) =>
  contents
    .split(/\r?\n/)
    .some((raw) => raw.trim() && !raw.trim().startsWith("#"));

const sleep = (ms) =>
  new Promise((resolve) => {
    setTimeout(resolve, ms);
  });

const readFirstLine = (contents) => {
  const [firstLine] = contents.split(/\r?\n/);
  return firstLine ?? "";
};

const clearListFile = async (filePath) => {
  if (!fs.existsSync(filePath)) {
    return;
  }
  const contents = await fsp.readFile(filePath, "utf8");
  const firstLine = readFirstLine(contents);
  const updated = firstLine ? `${firstLine}\n` : "";
  await fsp.writeFile(filePath, updated, "utf8");
};

const hasProjectIndicators = (projectDir) => {
  const indicators = [
    "tasks.md",
    "todo.md",
    "SEED.md",
    "feedback.md",
    "user_requests.md",
  ];
  return indicators.some((fileName) =>
    fs.existsSync(path.join(projectDir, fileName))
  );
};

const discoverProjects = async (rootDir) => {
  const projects = [];

  if (hasProjectIndicators(rootDir)) {
    projects.push(rootDir);
  }

  const entries = await fsp.readdir(rootDir, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }
    if (entry.name.startsWith(".") || entry.name === "node_modules") {
      continue;
    }
    const candidate = path.join(rootDir, entry.name);
    projects.push(candidate);
  }

  return projects;
};

const processProject = async ({
  projectDir,
  arboristDir,
  repoRoot,
  timeBudget,
}) => {
  const projectSetupPath = path.join(arboristDir, "project_setup.md");
  const completeNextItemPath = path.join(
    arboristDir,
    "complete_next_item.md"
  );
  const tasksPath = path.join(projectDir, "tasks.md");
  const todoPath = path.join(projectDir, "todo.md");
  const userRequestsPath = path.join(projectDir, "user_requests.md");
  const feedbackPath = path.join(projectDir, "feedback.md");
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
        console.log(
          `codex exec exceeded ${timeoutMs}ms; stopping and retrying.`
        );
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

  // If core project files are missing, send Codex to the project setup instructions.
  if (!fs.existsSync(tasksPath) || !fs.existsSync(todoPath)) {
    const setupPrompt = [
      `tasks.md or todo.md is missing in ${projectDir}.`,
      `Follow the project setup instructions in ${projectSetupPath}.`,
      `Read AGENTS.md at ${agentsPath} before you begin if it exists.`,
      "",
      `Project root: ${projectDir}`,
    ].join("\n");
    await runCodex(setupPrompt);
  }

  // Loop until time runs out or todo.md and tasks.md have no remaining items.
  while (true) {
    const timeLeft = deadline - Date.now();
    if (timeLeft <= 0) {
      console.log("Time budget reached. Stopping before starting a new task.");
      break;
    }

    if (!fs.existsSync(todoPath) || !fs.existsSync(tasksPath)) {
      console.log("todo.md or tasks.md is still missing. Stopping.");
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
        `Unable to read todo.md, tasks.md, or feedback.md: ${error.message}`
      );
      process.exit(1);
    }

    const hasFeedbackItems = feedbackContents
      ? hasWorkItems(feedbackContents)
      : false;
    if (
      !hasWorkItems(todoContents) &&
      !hasWorkItems(tasksContents) &&
      !hasFeedbackItems
    ) {
      console.log(
        "todo.md, tasks.md, and feedback.md have no remaining items. Stopping."
      );
      finishedWithoutWork = true;
      break;
    }

    // Don't parse todo: point Codex at todo.md and ask for the next item.
    const promptLines = [
      `Complete the next item in ${todoPath}.`,
      `Follow the instructions in ${completeNextItemPath}.`,
      `Project root: ${projectDir}`,
      `Time remaining: ${Math.max(0, timeLeft)}ms`,
    ];

    if (isFirstTask) {
      promptLines.splice(
        1,
        0,
        `Before starting, read AGENTS.md at ${agentsPath} if it exists.`
      );
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
    await clearListFile(tasksPath);
    await clearListFile(todoPath);
    await clearListFile(userRequestsPath);
  } else if (finishedWithoutWork && sawTimeout) {
    console.log(
      "Skipping list clearing because a previous task timed out in this run."
    );
  }
};

const main = async () => {
  const args = process.argv.slice(2);
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const arboristDir = path.resolve(scriptDir, "..");
  const repoRoot = path.resolve(arboristDir, "..");
  const rootDir = path.resolve(args[0] ?? repoRoot);
  if (!fs.existsSync(rootDir)) {
    console.error(`Projects folder not found: ${rootDir}`);
    process.exit(1);
  }

  // Fixed 4-hour budget for each project run.
  const timeBudget = 4 * 60 * 60 * 1000;

  while (true) {
    const projects = await discoverProjects(rootDir);
    if (projects.length === 0) {
      console.log(
        `No projects with tasks.md or todo.md found in ${rootDir}.`
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
