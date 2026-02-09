#!/usr/bin/env node
// Starts a lightweight static web server for the Arborist UI shell.
import { spawn } from "node:child_process";
import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { readFirstLine } from "../src/list-utils.js";
import { discoverProjects } from "../src/project-discovery.js";

const DEFAULT_PORT = 7788;
const MIME_TYPES = new Map([
  [".html", "text/html; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".svg", "image/svg+xml"],
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".ico", "image/x-icon"],
]);

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const arboristDir = path.resolve(scriptDir, "..");
const repoRoot = path.resolve(arboristDir, "..");
const repoRootPrefix = repoRoot.endsWith(path.sep) ? repoRoot : `${repoRoot}${path.sep}`;
const astroRoot = path.resolve(scriptDir, "..", "web_ui");
const distRoot = path.join(astroRoot, "dist");
const distRootPrefix = distRoot.endsWith(path.sep) ? distRoot : `${distRoot}${path.sep}`;
const publicRoot = path.join(astroRoot, "public");
const publicRootPrefix = publicRoot.endsWith(path.sep) ? publicRoot : `${publicRoot}${path.sep}`;
const astroIndexPath = path.join(astroRoot, "src", "pages", "index.astro");
const shellPagePath = path.join(astroRoot, "src", "components", "ShellPage.astro");
const activeProjectsPath = path.join(arboristDir, "active_projects");
const activeProjectPath = path.join(arboristDir, "active_project");
const DEFAULT_FEEDBACK_HEADER = "# The place for the humans to give feedback";
const FEEDBACK_FILE_NAME = "feedback.md";
const WORK_LOG_FILE_NAME = "work_log.md";
const MAX_RESPONSE_ENTRIES = 6;
const SAVE_STATE_BRANCH = "main";
const LOCALHOST_URL = "http://localhost";
const UI_ENTRYPOINT = path.join(distRoot, "index.html");
const UI_BUILD_ARGS = ["exec", "--", "astro", "build", "--root", astroRoot];
const UI_BUILD_ENABLED = process.env.ARBORIST_UI_BUILD !== "0";
const UI_WATCH_ENABLED = process.env.ARBORIST_UI_WATCH !== "0";
const UI_WATCH_INTERVAL_MS = Number.parseInt(process.env.ARBORIST_UI_WATCH_INTERVAL_MS ?? "1500", 10);
const UI_WATCH_PATHS = [path.join(astroRoot, "src"), publicRoot];
const UI_SOURCE_FILES = [
  astroIndexPath,
  path.join(astroRoot, "src", "components", "ShellPage.astro"),
  path.join(astroRoot, "src", "pages", "5.astro"),
  path.join(publicRoot, "app.js"),
  path.join(publicRoot, "styles.css"),
  path.join(publicRoot, "styles-options.css"),
];
let distReady = false;
let uiBuildInFlight = false;
let uiBuildPending = false;
let uiBuildDebounceTimer = null;

/**
 * Return a content type header based on the file extension.
 * @param {string} filePath - Absolute path to the requested file.
 * @returns {string} Content type header value.
 */
const getContentType = (filePath) => {
  const ext = path.extname(filePath).toLowerCase();
  return MIME_TYPES.get(ext) ?? "application/octet-stream";
};

/**
 * Resolve the requested URL path to a safe absolute path within the web root.
 * @param {string} pathname - URL pathname (decoded).
 * @returns {string | null} Absolute path if safe, otherwise null.
 */
const resolveStaticPath = (rootDir, rootPrefix, pathname) => {
  const normalized = path.posix.normalize(pathname).replace(/^\/+/, "").replace(/\0/g, "");
  const resolved = path.resolve(rootDir, normalized);
  if (!resolved.startsWith(rootPrefix)) {
    return null;
  }
  return resolved;
};

/**
 * Read a static file if it exists inside a root directory.
 * @param {string} rootDir - Absolute root directory.
 * @param {string} rootPrefix - Root directory prefix for safety.
 * @param {string} pathname - URL pathname.
 * @returns {Promise<{data: Buffer, resolvedPath: string} | null>} File payload or null.
 */
const readStaticFile = async (rootDir, rootPrefix, pathname) => {
  const resolvedPath = resolveStaticPath(rootDir, rootPrefix, pathname);
  if (!resolvedPath) {
    return null;
  }
  try {
    const data = await fs.readFile(resolvedPath);
    return { data, resolvedPath };
  } catch (error) {
    if (error?.code === "ENOENT" || error?.code === "EISDIR") {
      return null;
    }
    throw error;
  }
};

/**
 * Attempt to resolve a pathname to an HTML route file for static builds.
 * @param {string} pathname - URL pathname.
 * @returns {string | null} Candidate route path (e.g., /1/index.html) or null.
 */
const toRouteIndexPath = (pathname) => {
  if (!pathname || pathname === "/") {
    return null;
  }
  if (pathname.endsWith(".html") || path.posix.extname(pathname)) {
    return null;
  }
  const trimmed = pathname.endsWith("/") ? pathname.slice(0, -1) : pathname;
  if (!trimmed) {
    return null;
  }
  return `${trimmed}/index.html`;
};

/**
 * Strip an Astro frontmatter block from a source file.
 * @param {string} contents - Raw file contents.
 * @returns {string} Template markup without frontmatter.
 */
const stripAstroFrontmatter = (contents) => {
  if (contents.startsWith("---")) {
    const end = contents.indexOf("\n---", 3);
    if (end !== -1) {
      return contents.slice(end + 4).trimStart();
    }
  }
  return contents;
};

/**
 * Load a variant shell page from source as an HTML fallback.
 * @param {string} variant - Variant id ("5").
 * @returns {Promise<string | null>} HTML string or null if unavailable.
 */
const loadVariantShell = async (variant) => {
  try {
    const contents = await fs.readFile(shellPagePath, "utf8");
    const markup = stripAstroFrontmatter(contents);
    return markup
      .replace('class={`variant-${variant}`}', `class="variant-${variant}"`)
      .replaceAll("{variant}", variant);
  } catch (error) {
    if (error?.code === "ENOENT") {
      return null;
    }
    throw error;
  }
};

/**
 * Return the latest modification time under a path (file or directory).
 * @param {string} targetPath - Absolute path to scan.
 * @returns {Promise<number>} Latest mtime in milliseconds.
 */
const getLatestMtime = async (targetPath) => {
  let stat;
  try {
    stat = await fs.stat(targetPath);
  } catch (error) {
    if (error?.code === "ENOENT") {
      return 0;
    }
    throw error;
  }

  if (!stat.isDirectory()) {
    return stat.mtimeMs;
  }

  let latest = stat.mtimeMs;
  let entries = [];
  try {
    entries = await fs.readdir(targetPath, { withFileTypes: true });
  } catch (error) {
    if (error?.code === "ENOENT") {
      return latest;
    }
    throw error;
  }

  for (const entry of entries) {
    const childPath = path.join(targetPath, entry.name);
    if (entry.isDirectory()) {
      const childLatest = await getLatestMtime(childPath);
      if (childLatest > latest) {
        latest = childLatest;
      }
      continue;
    }
    if (entry.isFile()) {
      try {
        const fileStat = await fs.stat(childPath);
        if (fileStat.mtimeMs > latest) {
          latest = fileStat.mtimeMs;
        }
      } catch (error) {
        if (error?.code !== "ENOENT") {
          throw error;
        }
      }
    }
  }

  return latest;
};

/**
 * Get the latest source modification time used for UI rebuild watching.
 * @returns {Promise<number>} Latest source mtime.
 */
const getLatestUiSourceMtime = async () => {
  let latest = 0;
  for (const watchPath of UI_WATCH_PATHS) {
    const pathLatest = await getLatestMtime(watchPath);
    if (pathLatest > latest) {
      latest = pathLatest;
    }
  }
  return latest;
};

/**
 * Normalize a relative project path for comparisons and storage.
 * @param {string} value - Relative path value.
 * @returns {string} Normalized relative path.
 */
const normalizeRelativePath = (value) => {
  const trimmed = value.trim();
  if (!trimmed) {
    return "";
  }
  const normalized = path.posix.normalize(trimmed.replace(/\\/g, "/"));
  return normalized === "" ? "." : normalized;
};

/**
 * Resolve a project root directory from a normalized relative path.
 * @param {string} projectPath - Normalized relative project path.
 * @returns {string} Absolute project root path.
 */
const resolveProjectRoot = (projectPath) => {
  const normalized = normalizeRelativePath(projectPath);
  const resolved = path.resolve(repoRoot, normalized === "." ? "" : normalized);
  if (resolved !== repoRoot && !resolved.startsWith(repoRootPrefix)) {
    throw new Error("Invalid project path.");
  }
  return resolved;
};

/**
 * Resolve the arborist directory for a project.
 * @param {string} projectPath - Normalized relative project path.
 * @returns {string} Absolute arborist directory path.
 */
const resolveProjectArboristDir = (projectPath) =>
  path.join(resolveProjectRoot(projectPath), "arborist");

/**
 * Normalize a feedback message for list storage.
 * @param {string} value - Raw feedback message.
 * @returns {string} Normalized message string.
 */
const normalizeFeedbackMessage = (value) => value.replace(/\s+/g, " ").trim();

/**
 * Format a timestamp for a save-state commit message.
 * @returns {string} Timestamp formatted for commit messages.
 */
const formatCommitTimestamp = () =>
  new Date().toISOString().replace("T", " ").replace(/\..+/, " UTC");

/**
 * Build a commit message for a save-state action.
 * @param {string} projectName - Active project display name.
 * @returns {string} Commit message subject.
 */
const formatCommitMessage = (projectName) => {
  const safeName = projectName?.trim() ? projectName.trim().replace(/\s+/g, " ") : "workspace";
  return `Save state for ${safeName} (${formatCommitTimestamp()})`;
};

/**
 * Run a command and capture stdout/stderr.
 * @param {string} command - Executable to run.
 * @param {string[]} args - Command arguments.
 * @param {{cwd?: string}} options - Command options.
 * @returns {Promise<{stdout: string, stderr: string}>} Captured output.
 */
const runCommand = (command, args, options = {}) =>
  new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: options.cwd,
      env: { ...process.env, GIT_TERMINAL_PROMPT: "0" },
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    if (child.stdout) {
      child.stdout.on("data", (chunk) => {
        stdout += chunk.toString("utf8");
      });
    }
    if (child.stderr) {
      child.stderr.on("data", (chunk) => {
        stderr += chunk.toString("utf8");
      });
    }

    child.on("error", (error) => {
      if (error?.code === "ENOENT") {
        reject(new Error(`${command} command not found.`));
        return;
      }
      reject(error);
    });

    child.on("close", (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
        return;
      }
      const message = stderr.trim() || stdout.trim() || `${command} ${args.join(" ")} failed.`;
      reject(new Error(message));
    });
  });

/**
 * Ensure the Astro build output exists before starting the static server.
 * @param {boolean} [force] - Rebuild even when output appears up to date.
 */
const ensureUiBuild = async (force = false) => {
  let buildStat;
  if (!force) {
    try {
      buildStat = await fs.stat(UI_ENTRYPOINT);
    } catch (error) {
      if (error?.code !== "ENOENT") {
        throw error;
      }
    }

    if (buildStat) {
      const buildTime = buildStat.mtimeMs;
      for (const sourceFile of UI_SOURCE_FILES) {
        try {
          const sourceStat = await fs.stat(sourceFile);
          if (sourceStat.mtimeMs > buildTime) {
            buildStat = null;
            break;
          }
        } catch {
          buildStat = null;
          break;
        }
      }
    }

    if (buildStat) {
      distReady = true;
      return;
    }
  }

  if (!UI_BUILD_ENABLED) {
    console.log("UI build disabled; serving UI from source files.");
    return;
  }

  console.log("Building Arborist UI with Astro...");
  try {
    await runCommand("npm", UI_BUILD_ARGS, { cwd: arboristDir });
    distReady = true;
  } catch (error) {
    const message = error?.message ?? "Unable to build UI.";
    console.warn(`UI build skipped: ${message}`);
    console.warn("Serving UI from source files instead.");
    distReady = false;
  }
};

/**
 * Queue a debounced UI rebuild.
 * @param {string} reason - Reason for rebuild.
 */
const queueUiRebuild = (reason) => {
  if (!UI_BUILD_ENABLED) {
    return;
  }

  distReady = false;
  if (uiBuildDebounceTimer) {
    clearTimeout(uiBuildDebounceTimer);
  }

  uiBuildDebounceTimer = setTimeout(() => {
    uiBuildDebounceTimer = null;
    if (uiBuildInFlight) {
      uiBuildPending = true;
      return;
    }

    uiBuildInFlight = true;
    console.log(`Detected UI source update (${reason}); rebuilding...`);
    ensureUiBuild(true)
      .then(() => {
        console.log("UI rebuild complete.");
      })
      .catch((error) => {
        const message = error?.message ?? "Unable to rebuild UI.";
        console.warn(`UI rebuild skipped: ${message}`);
      })
      .finally(() => {
        uiBuildInFlight = false;
        if (uiBuildPending) {
          uiBuildPending = false;
          queueUiRebuild("queued changes");
        }
      });
  }, 180);
};

/**
 * Start polling UI source files and trigger rebuilds on changes.
 * @returns {Promise<() => void>} Cleanup callback.
 */
const startUiSourceWatcher = async () => {
  if (!UI_WATCH_ENABLED) {
    return () => {};
  }

  let lastMtime = 0;
  try {
    lastMtime = await getLatestUiSourceMtime();
  } catch (error) {
    const message = error?.message ?? "Unable to read UI source timestamps.";
    console.warn(`UI watcher disabled: ${message}`);
    return () => {};
  }

  let stopped = false;
  let scanInFlight = false;
  const intervalMs = Number.isFinite(UI_WATCH_INTERVAL_MS) && UI_WATCH_INTERVAL_MS > 0
    ? UI_WATCH_INTERVAL_MS
    : 1500;

  const timer = setInterval(async () => {
    if (stopped || scanInFlight) {
      return;
    }
    scanInFlight = true;
    try {
      const latest = await getLatestUiSourceMtime();
      if (latest > lastMtime) {
        lastMtime = latest;
        queueUiRebuild("source files changed");
      }
    } catch (error) {
      const message = error?.message ?? "Unable to scan UI sources.";
      console.warn(`UI watcher scan failed: ${message}`);
    } finally {
      scanInFlight = false;
    }
  }, intervalMs);

  return () => {
    stopped = true;
    clearInterval(timer);
    if (uiBuildDebounceTimer) {
      clearTimeout(uiBuildDebounceTimer);
      uiBuildDebounceTimer = null;
    }
  };
};

/**
 * Ensure the target directory is a git repository.
 * @param {string} cwd - Directory to validate.
 */
const ensureGitRepo = async (cwd) => {
  try {
    await runCommand("git", ["rev-parse", "--is-inside-work-tree"], { cwd });
  } catch (error) {
    if (error?.message === "git command not found.") {
      throw error;
    }
    throw new Error("Git repository not found.");
  }
};

/**
 * Ensure the current branch matches the save state branch.
 * @param {string} cwd - Directory to check.
 * @returns {Promise<string>} Branch name.
 */
const requireSaveStateBranch = async (cwd) => {
  const { stdout } = await runCommand("git", ["rev-parse", "--abbrev-ref", "HEAD"], { cwd });
  const branch = stdout.trim();
  if (!branch) {
    throw new Error("Unable to determine current branch.");
  }
  if (branch !== SAVE_STATE_BRANCH) {
    throw new Error(
      `Current branch is ${branch}; switch to ${SAVE_STATE_BRANCH} before saving state.`,
    );
  }
  return branch;
};

/**
 * Check for local changes in a repository.
 * @param {string} cwd - Directory to check.
 * @returns {Promise<string>} Porcelain status output.
 */
const readRepoStatus = async (cwd) => {
  const { stdout } = await runCommand("git", ["status", "--porcelain"], { cwd });
  return stdout.trim();
};

/**
 * Parse a list-style configuration file into entries.
 * @param {string} contents - Raw file contents.
 * @returns {string[]} Parsed entries.
 */
const parseListFile = (contents) =>
  contents
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0 && !line.startsWith("#"))
    .map(normalizeRelativePath);

/**
 * Load a list file, returning null if it does not exist.
 * @param {string} filePath - Absolute path to the list file.
 * @returns {Promise<string[] | null>} Parsed entries or null if missing.
 */
const loadListFile = async (filePath) => {
  try {
    const contents = await fs.readFile(filePath, "utf8");
    return parseListFile(contents);
  } catch (error) {
    if (error?.code === "ENOENT") {
      return null;
    }
    throw error;
  }
};

/**
 * Persist a list file with normalized, de-duplicated entries.
 * @param {string} filePath - Absolute path to the list file.
 * @param {string[]} entries - Entries to write.
 */
const writeListFile = async (filePath, entries) => {
  const seen = new Set();
  const ordered = [];
  for (const entry of entries) {
    const normalized = normalizeRelativePath(entry);
    if (!normalized || seen.has(normalized)) {
      continue;
    }
    seen.add(normalized);
    ordered.push(normalized);
  }
  const payload = ordered.length > 0 ? `${ordered.join("\n")}\n` : "";
  await fs.writeFile(filePath, payload, "utf8");
};

/**
 * Parse the feedback file into a header and items.
 * @param {string} contents - Raw file contents.
 * @returns {{header: string, items: string[]}} Parsed feedback data.
 */
const parseFeedbackFile = (contents) => {
  const header = readFirstLine(contents).trim() || DEFAULT_FEEDBACK_HEADER;
  const items = [];
  for (const line of contents.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    const normalized = trimmed.replace(/^[-*]\s+/, "").trim();
    if (normalized) {
      items.push(normalized);
    }
  }
  return { header, items };
};

/**
 * Load feedback items from disk if the file exists.
 * @param {string} filePath - Absolute feedback file path.
 * @returns {Promise<{header: string, items: string[]}>} Parsed feedback data.
 */
const loadFeedbackFile = async (filePath) => {
  try {
    const contents = await fs.readFile(filePath, "utf8");
    return parseFeedbackFile(contents);
  } catch (error) {
    if (error?.code === "ENOENT") {
      return { header: DEFAULT_FEEDBACK_HEADER, items: [] };
    }
    throw error;
  }
};

/**
 * Write feedback items to disk, preserving a header.
 * @param {string} filePath - Absolute feedback file path.
 * @param {string} header - Header line to write.
 * @param {string[]} items - Feedback items to write.
 */
const writeFeedbackFile = async (filePath, header, items) => {
  const safeHeader = header?.trim() ? header.trim() : DEFAULT_FEEDBACK_HEADER;
  const lines = [safeHeader];
  if (items.length > 0) {
    lines.push("");
    for (const item of items) {
      lines.push(`- ${item}`);
    }
  }
  const payload = `${lines.join("\n")}\n`;
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, payload, "utf8");
};

/**
 * Append a feedback item to the feedback file.
 * @param {string} filePath - Absolute feedback file path.
 * @param {string} item - Feedback item to append.
 */
const appendFeedbackItem = async (filePath, item) => {
  const { header, items } = await loadFeedbackFile(filePath);
  items.push(item);
  await writeFeedbackFile(filePath, header, items);
};

/**
 * Clear feedback items while keeping the header.
 * @param {string} filePath - Absolute feedback file path.
 */
const clearFeedbackItems = async (filePath) => {
  const { header } = await loadFeedbackFile(filePath);
  await writeFeedbackFile(filePath, header, []);
};

/**
 * Remove a list file if it exists.
 * @param {string} filePath - Absolute path to the list file.
 */
const clearListFile = async (filePath) => {
  try {
    await fs.unlink(filePath);
  } catch (error) {
    if (error?.code !== "ENOENT") {
      throw error;
    }
  }
};

/**
 * Load the active projects list.
 * @returns {Promise<string[] | null>} Active project entries.
 */
const loadActiveProjects = async () => loadListFile(activeProjectsPath);

/**
 * Load the active project selection.
 * @returns {Promise<string | null>} Active project entry or null.
 */
const loadActiveProject = async () => {
  const entries = await loadListFile(activeProjectPath);
  if (!entries || entries.length === 0) {
    return null;
  }
  return entries[0] ?? null;
};

/**
 * Order entries to match discovered project ordering.
 * @param {string[]} entries - Entries to order.
 * @param {{path: string}[]} projects - Project metadata.
 * @returns {string[]} Ordered entries.
 */
const orderEntries = (entries, projects) => {
  const set = new Set(entries.map(normalizeRelativePath));
  return projects.map((project) => project.path).filter((entry) => set.has(entry));
};

/**
 * Build the current project state for the UI.
 * @returns {Promise<{rootDir: string, projects: Array, activeProject: string | null, usingActiveProjects: boolean}>}
 */
const buildProjectState = async () => {
  const rootDir = repoRoot;
  const projectDirs = await discoverProjects(rootDir);
  const projects = projectDirs.map((projectDir) => {
    const relativePath = normalizeRelativePath(path.relative(rootDir, projectDir) || ".");
    const name = relativePath === "." ? path.basename(rootDir) : path.basename(projectDir);
    return {
      name,
      path: relativePath,
    };
  });

  const activeProjects = await loadActiveProjects();
  const usingActiveProjects = Boolean(activeProjects && activeProjects.length > 0);
  const enabledSet = new Set((activeProjects ?? []).map(normalizeRelativePath));
  const activeProject = normalizeRelativePath((await loadActiveProject()) ?? "");
  const activeResolved =
    activeProject && projects.some((project) => project.path === activeProject)
      ? activeProject
      : null;

  const projectState = projects.map((project) => ({
    ...project,
    enabled: usingActiveProjects ? enabledSet.has(project.path) : true,
    active: activeResolved === project.path,
  }));

  return {
    rootDir,
    projects: projectState,
    activeProject: activeResolved,
    usingActiveProjects,
  };
};

/**
 * Split a work log entry into date/summary parts if possible.
 * @param {string} line - Raw work log entry text.
 * @returns {{date: string | null, summary: string, label: string}} Parsed entry data.
 */
const splitWorkLogSummary = (line) => {
  const trimmed = line.trim();
  const match = trimmed.match(/^(\d{4}-\d{2}-\d{2}):\s*(.+)$/);
  if (match) {
    return { date: match[1], summary: match[2].trim(), label: trimmed };
  }
  return { date: null, summary: trimmed, label: trimmed };
};

/**
 * Parse work log markdown into entries for display.
 * @param {string} contents - Raw work log contents.
 * @returns {Array<{id: string, date: string | null, summary: string, label: string, details: string[]}>}
 */
const parseWorkLogEntries = (contents) => {
  const entries = [];
  let current = null;
  for (const line of contents.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    if (trimmed.startsWith("- ")) {
      const entryLine = trimmed.replace(/^-\s+/, "").trim();
      const { date, summary, label } = splitWorkLogSummary(entryLine);
      current = { id: String(entries.length), date, summary, label, details: [] };
      entries.push(current);
      continue;
    }
    if (current && /^\s+/.test(line)) {
      current.details.push(trimmed);
    }
  }
  return entries;
};

/**
 * Load work log entries from disk if the file exists.
 * @param {string} filePath - Absolute work log file path.
 * @returns {Promise<Array<{id: string, date: string | null, summary: string, label: string, details: string[]}>>}
 */
const loadWorkLogEntries = async (filePath) => {
  try {
    const contents = await fs.readFile(filePath, "utf8");
    return parseWorkLogEntries(contents);
  } catch (error) {
    if (error?.code === "ENOENT") {
      return [];
    }
    throw error;
  }
};

/**
 * Resolve the active project and its arborist directory.
 * @returns {Promise<{activeProject: {name: string, path: string} | null, arboristDir: string | null}>}
 */
const resolveActiveProjectContext = async () => {
  const state = await buildProjectState();
  if (!state.activeProject) {
    return { activeProject: null, arboristDir: null };
  }
  const activeProject =
    state.projects.find((project) => project.path === state.activeProject) ?? null;
  if (!activeProject) {
    return { activeProject: null, arboristDir: null };
  }
  return {
    activeProject: { name: activeProject.name, path: activeProject.path },
    arboristDir: resolveProjectArboristDir(activeProject.path),
  };
};

/**
 * Resolve the save state context for the active project.
 * @returns {Promise<{activeProject: {name: string, path: string}, commitRoot: string, isArboristProject: boolean}>}
 */
const resolveSaveStateContext = async () => {
  const { activeProject } = await resolveActiveProjectContext();
  if (!activeProject) {
    throw new Error("No active project selected.");
  }
  const projectRoot = resolveProjectRoot(activeProject.path);
  const isArboristProject = projectRoot === arboristDir;
  const commitRoot = isArboristProject ? repoRoot : projectRoot;
  return { activeProject, commitRoot, isArboristProject };
};

/**
 * Execute the save state action for the active project.
 * @returns {Promise<{activeProject: {name: string, path: string}, result: {status: string, message: string, commitRoot: string, commitSha?: string, isArboristProject: boolean}}>}
 */
const saveStateForActiveProject = async () => {
  const { activeProject, commitRoot, isArboristProject } = await resolveSaveStateContext();
  await ensureGitRepo(commitRoot);
  await requireSaveStateBranch(commitRoot);

  const initialStatus = await readRepoStatus(commitRoot);
  if (!initialStatus) {
    return {
      activeProject,
      result: {
        status: "noop",
        message: "No local changes to save.",
        commitRoot,
        isArboristProject,
      },
    };
  }

  await runCommand("git", ["add", "-A"], { cwd: commitRoot });

  const stagedStatus = await readRepoStatus(commitRoot);
  if (!stagedStatus) {
    return {
      activeProject,
      result: {
        status: "noop",
        message: "No local changes to save.",
        commitRoot,
        isArboristProject,
      },
    };
  }

  const commitMessage = formatCommitMessage(activeProject.name);
  await runCommand("git", ["commit", "-m", commitMessage], { cwd: commitRoot });
  await runCommand("git", ["push", "origin", SAVE_STATE_BRANCH], { cwd: commitRoot });
  const { stdout } = await runCommand("git", ["rev-parse", "HEAD"], { cwd: commitRoot });
  const commitSha = stdout.trim();
  const shortSha = commitSha ? commitSha.slice(0, 7) : "";
  const message = shortSha
    ? `Saved state and pushed to ${SAVE_STATE_BRANCH} (${shortSha}).`
    : `Saved state and pushed to ${SAVE_STATE_BRANCH}.`;

  return {
    activeProject,
    result: {
      status: "saved",
      message,
      commitRoot,
      commitSha,
      isArboristProject,
    },
  };
};

/**
 * Build the feedback state for the UI.
 * @returns {Promise<{activeProject: {name: string, path: string} | null, feedback: {items: string[], count: number}, responses: Array}>}
 */
const buildFeedbackState = async () => {
  const { activeProject, arboristDir } = await resolveActiveProjectContext();
  if (!activeProject || !arboristDir) {
    return { activeProject: null, feedback: { items: [], count: 0 }, responses: [] };
  }
  const feedbackPath = path.join(arboristDir, FEEDBACK_FILE_NAME);
  const workLogPath = path.join(arboristDir, WORK_LOG_FILE_NAME);
  const feedbackData = await loadFeedbackFile(feedbackPath);
  const workLogEntries = await loadWorkLogEntries(workLogPath);
  const trimmedEntries =
    workLogEntries.length > MAX_RESPONSE_ENTRIES
      ? workLogEntries.slice(-MAX_RESPONSE_ENTRIES)
      : workLogEntries;
  const responses = [...trimmedEntries].reverse();
  return {
    activeProject,
    feedback: { items: feedbackData.items, count: feedbackData.items.length },
    responses,
  };
};

/**
 * Update the enabled state for a project.
 * @param {string} targetPath - Relative project path.
 * @param {boolean} enabled - Desired enabled state.
 * @returns {Promise<{rootDir: string, projects: Array, activeProject: string | null, usingActiveProjects: boolean}>}
 */
const updateEnabledProject = async (targetPath, enabled) => {
  const state = await buildProjectState();
  const normalizedTarget = normalizeRelativePath(targetPath);
  const targetProject = state.projects.find((project) => project.path === normalizedTarget);
  if (!targetProject) {
    throw new Error("Unknown project path.");
  }

  const enabledList = state.usingActiveProjects
    ? state.projects.filter((project) => project.enabled).map((project) => project.path)
    : state.projects.map((project) => project.path);
  const enabledSet = new Set(enabledList.map(normalizeRelativePath));

  if (enabled) {
    enabledSet.add(normalizedTarget);
  } else {
    enabledSet.delete(normalizedTarget);
  }

  if (enabledSet.size === 0) {
    throw new Error("At least one project must remain enabled.");
  }

  const orderedEnabled = orderEntries([...enabledSet], state.projects);
  await writeListFile(activeProjectsPath, orderedEnabled);

  if (!enabled && state.activeProject === normalizedTarget) {
    await clearListFile(activeProjectPath);
  }

  return buildProjectState();
};

/**
 * Update the active project selection.
 * @param {string | null} targetPath - Relative project path or null to clear.
 * @returns {Promise<{rootDir: string, projects: Array, activeProject: string | null, usingActiveProjects: boolean}>}
 */
const updateActiveProject = async (targetPath) => {
  if (!targetPath) {
    await clearListFile(activeProjectPath);
    return buildProjectState();
  }

  const state = await buildProjectState();
  const normalizedTarget = normalizeRelativePath(targetPath);
  const targetProject = state.projects.find((project) => project.path === normalizedTarget);
  if (!targetProject) {
    throw new Error("Unknown project path.");
  }

  if (state.usingActiveProjects && !targetProject.enabled) {
    const enabledList = state.projects
      .filter((project) => project.enabled)
      .map((project) => project.path);
    enabledList.push(normalizedTarget);
    const orderedEnabled = orderEntries(enabledList, state.projects);
    await writeListFile(activeProjectsPath, orderedEnabled);
  }

  await writeListFile(activeProjectPath, [normalizedTarget]);
  return buildProjectState();
};

/**
 * Send a response with the provided status, headers, and optional body.
 * @param {http.ServerResponse} res - Server response object.
 * @param {number} status - HTTP status code.
 * @param {Record<string, string>} headers - Response headers.
 * @param {Buffer | string | null} body - Optional response body.
 * @param {string} method - HTTP method for the request.
 */
const sendResponse = (res, status, headers, body, method) => {
  res.writeHead(status, headers);
  if (body && method !== "HEAD") {
    res.end(body);
    return;
  }
  res.end();
};

/**
 * Send a JSON response with the given payload.
 * @param {http.ServerResponse} res - Server response object.
 * @param {number} status - HTTP status code.
 * @param {unknown} payload - JSON-serializable payload.
 * @param {string} method - HTTP method for the request.
 */
const sendJson = (res, status, payload, method) => {
  const body = JSON.stringify(payload, null, 2);
  sendResponse(res, status, { "Content-Type": "application/json; charset=utf-8" }, body, method);
};

/**
 * Read and parse a JSON request body.
 * @param {http.IncomingMessage} req - Incoming request object.
 * @returns {Promise<unknown>} Parsed JSON payload.
 */
const readJsonBody = async (req) => {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    chunks.push(chunk);
    size += chunk.length;
    if (size > 100_000) {
      throw new Error("Request body too large.");
    }
  }
  if (chunks.length === 0) {
    return null;
  }
  const raw = Buffer.concat(chunks).toString("utf8");
  if (!raw) {
    return null;
  }
  return JSON.parse(raw);
};

/**
 * Handle API requests for project controls.
 * @param {http.IncomingMessage} req - Incoming request object.
 * @param {http.ServerResponse} res - Server response object.
 * @param {string} pathname - Parsed request pathname.
 */
const handleApiRequest = async (req, res, pathname) => {
  const method = req.method ?? "GET";

  try {
    if (method === "GET" && pathname === "/api/projects") {
      const state = await buildProjectState();
      sendJson(res, 200, state, method);
      return;
    }

    if (method === "GET" && pathname === "/api/feedback") {
      const state = await buildFeedbackState();
      sendJson(res, 200, state, method);
      return;
    }

    if (method === "POST" && pathname === "/api/projects/enabled") {
      const body = await readJsonBody(req);
      const targetPath = typeof body?.path === "string" ? body.path : "";
      const enabled = Boolean(body?.enabled);
      const state = await updateEnabledProject(targetPath, enabled);
      sendJson(res, 200, state, method);
      return;
    }

    if (method === "POST" && pathname === "/api/projects/active") {
      const body = await readJsonBody(req);
      const targetPath = typeof body?.path === "string" ? body.path : null;
      const state = await updateActiveProject(targetPath);
      sendJson(res, 200, state, method);
      return;
    }

    if (method === "POST" && pathname === "/api/feedback") {
      const body = await readJsonBody(req);
      const message = typeof body?.message === "string" ? body.message : "";
      const normalized = normalizeFeedbackMessage(message);
      if (!normalized) {
        throw new Error("Feedback message is required.");
      }
      const { activeProject, arboristDir } = await resolveActiveProjectContext();
      if (!activeProject || !arboristDir) {
        throw new Error("No active project selected.");
      }
      const feedbackPath = path.join(arboristDir, FEEDBACK_FILE_NAME);
      await appendFeedbackItem(feedbackPath, normalized);
      const state = await buildFeedbackState();
      sendJson(res, 200, state, method);
      return;
    }

    if (method === "POST" && pathname === "/api/feedback/clear") {
      const { activeProject, arboristDir } = await resolveActiveProjectContext();
      if (!activeProject || !arboristDir) {
        throw new Error("No active project selected.");
      }
      const feedbackPath = path.join(arboristDir, FEEDBACK_FILE_NAME);
      await clearFeedbackItems(feedbackPath);
      const state = await buildFeedbackState();
      sendJson(res, 200, state, method);
      return;
    }

    if (method === "POST" && pathname === "/api/feedback/follow-up") {
      const body = await readJsonBody(req);
      const responseId = typeof body?.responseId === "string" ? body.responseId : "";
      const message = typeof body?.message === "string" ? body.message : "";
      const normalized = normalizeFeedbackMessage(message);
      if (!responseId) {
        throw new Error("Response entry is required.");
      }
      const { activeProject, arboristDir } = await resolveActiveProjectContext();
      if (!activeProject || !arboristDir) {
        throw new Error("No active project selected.");
      }
      const workLogPath = path.join(arboristDir, WORK_LOG_FILE_NAME);
      const entries = await loadWorkLogEntries(workLogPath);
      const targetEntry = entries.find((entry) => entry.id === responseId);
      if (!targetEntry) {
        throw new Error("Unknown response entry.");
      }
      const context = targetEntry.label || targetEntry.summary;
      const followUp = normalized
        ? `Follow-up on ${context}: ${normalized}`
        : `Follow-up on ${context}`;
      const feedbackPath = path.join(arboristDir, FEEDBACK_FILE_NAME);
      await appendFeedbackItem(feedbackPath, followUp);
      const state = await buildFeedbackState();
      sendJson(res, 200, state, method);
      return;
    }

    if (method === "POST" && pathname === "/api/save-state") {
      const state = await saveStateForActiveProject();
      sendJson(res, 200, state, method);
      return;
    }

    sendJson(res, 404, { error: "Not Found" }, method);
  } catch (error) {
    const message = error?.message ?? "Request failed.";
    const isBadRequest =
      message === "Unknown project path." ||
      message === "At least one project must remain enabled." ||
      message === "Feedback message is required." ||
      message === "No active project selected." ||
      message === "Response entry is required." ||
      message === "Unknown response entry." ||
      message === "Invalid project path." ||
      message === "Git repository not found." ||
      message === "git command not found." ||
      message === "Unable to determine current branch." ||
      message.startsWith("Current branch is ");
    const status = message === "Request body too large." ? 413 : isBadRequest ? 400 : 500;
    sendJson(res, status, { error: message }, method);
  }
};

/**
 * Handle incoming HTTP requests for static assets.
 * @param {http.IncomingMessage} req - Incoming request object.
 * @param {http.ServerResponse} res - Server response object.
 */
const handleRequest = async (req, res) => {
  const method = req.method ?? "GET";
  let pathname = "/";
  let variantPath = null;
  try {
    const requestUrl = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);
    pathname = decodeURIComponent(requestUrl.pathname);
    const match = pathname.match(/^\/(5)\/?$/);
    variantPath = match ? match[1] : null;
  } catch {
    sendResponse(res, 400, { "Content-Type": "text/plain; charset=utf-8" }, "Bad Request", method);
    return;
  }

  if (pathname.startsWith("/api/")) {
    await handleApiRequest(req, res, pathname);
    return;
  }

  if (method !== "GET" && method !== "HEAD") {
    sendResponse(
      res,
      405,
      { "Content-Type": "text/plain; charset=utf-8" },
      "Method Not Allowed",
      method,
    );
    return;
  }

  if (pathname === "/favicon.ico") {
    sendResponse(res, 204, {}, null, method);
    return;
  }

  if (pathname === "/" || pathname === "/index.html") {
    const distIndex = distReady
      ? await readStaticFile(distRoot, distRootPrefix, "/index.html")
      : null;
    if (distIndex) {
      sendResponse(
        res,
        200,
        { "Content-Type": "text/html; charset=utf-8" },
        distIndex.data,
        method,
      );
      return;
    }

    const fallbackHtml = await loadVariantShell("5");
    if (fallbackHtml) {
      sendResponse(
        res,
        200,
        { "Content-Type": "text/html; charset=utf-8" },
        fallbackHtml,
        method,
      );
      return;
    }

    sendResponse(res, 404, { "Content-Type": "text/plain; charset=utf-8" }, "Not Found", method);
    return;
  }

  try {
    const distFile = distReady ? await readStaticFile(distRoot, distRootPrefix, pathname) : null;
    if (distFile) {
      sendResponse(
        res,
        200,
        { "Content-Type": getContentType(distFile.resolvedPath) },
        distFile.data,
        method,
      );
      return;
    }

    if (distReady) {
      const routePath = toRouteIndexPath(pathname);
      if (routePath) {
        let distRouteFile = await readStaticFile(distRoot, distRootPrefix, routePath);
        if (!distRouteFile) {
          try {
            await ensureUiBuild(true);
            distRouteFile = await readStaticFile(distRoot, distRootPrefix, routePath);
          } catch {
            distReady = false;
          }
        }
        if (distRouteFile) {
          sendResponse(
            res,
            200,
            { "Content-Type": getContentType(distRouteFile.resolvedPath) },
            distRouteFile.data,
            method,
          );
          return;
        }
      }
    }

    const publicFile = await readStaticFile(publicRoot, publicRootPrefix, pathname);
    if (publicFile) {
      sendResponse(
        res,
        200,
        { "Content-Type": getContentType(publicFile.resolvedPath) },
        publicFile.data,
        method,
      );
      return;
    }

    if (variantPath) {
      const fallbackVariant = await loadVariantShell(variantPath);
      if (fallbackVariant) {
        sendResponse(
          res,
          200,
          { "Content-Type": "text/html; charset=utf-8" },
          fallbackVariant,
          method,
        );
        return;
      }
    }
  } catch (error) {
    sendResponse(res, 500, { "Content-Type": "text/plain; charset=utf-8" }, "Server Error", method);
    return;
  }

  sendResponse(res, 404, { "Content-Type": "text/plain; charset=utf-8" }, "Not Found", method);
};

/**
 * Start the HTTP server on the configured port.
 */
const startServer = async () => {
  await ensureUiBuild();
  const stopUiWatcher = await startUiSourceWatcher();
  const rawPort = Number.parseInt(process.env.ARBORIST_UI_PORT ?? "", 10);
  const port = Number.isNaN(rawPort) ? DEFAULT_PORT : rawPort;

  const server = http.createServer((req, res) => {
    const fallbackMethod = req.method ?? "GET";
    handleRequest(req, res).catch(() => {
      sendResponse(
        res,
        500,
        { "Content-Type": "text/plain; charset=utf-8" },
        "Server Error",
        fallbackMethod,
      );
    });
  });

  server.listen(port, "127.0.0.1", () => {
    console.log(`Arborist UI running at ${LOCALHOST_URL}:${port}`);
    console.log(`Serving static files from ${distReady ? distRoot : publicRoot}`);
    if (!distReady) {
      console.log("Serving HTML from the Astro source page.");
    }
  });

  const shutdown = () => {
    console.log("Shutting down Arborist UI server.");
    stopUiWatcher();
    server.close(() => process.exit(0));
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
};

startServer().catch((error) => {
  const message = error?.message ?? "Unable to start the UI server.";
  console.error(message);
  process.exit(1);
});
