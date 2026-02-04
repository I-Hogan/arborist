import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";

const rootIndicatorFiles = ["SEED.md"];
const arboristIndicatorFiles = ["tasks.md", "todo.md", "feedback.md"];

const hasProjectIndicators = (projectDir) => {
  const arboristDir = path.join(projectDir, "arborist");
  return (
    rootIndicatorFiles.some((fileName) => fs.existsSync(path.join(projectDir, fileName))) ||
    arboristIndicatorFiles.some((fileName) => fs.existsSync(path.join(arboristDir, fileName)))
  );
};

const isCandidateDirectory = (entry) =>
  entry.isDirectory() && !entry.name.startsWith(".") && entry.name !== "node_modules";

const discoverProjects = async (rootDir) => {
  const projects = [];

  if (hasProjectIndicators(rootDir)) {
    projects.push(rootDir);
  }

  const entries = await fsp.readdir(rootDir, { withFileTypes: true });
  for (const entry of entries) {
    if (!isCandidateDirectory(entry)) {
      continue;
    }
    const candidate = path.join(rootDir, entry.name);
    if (hasProjectIndicators(candidate)) {
      projects.push(candidate);
    }
  }

  return projects;
};

export { discoverProjects, hasProjectIndicators };
