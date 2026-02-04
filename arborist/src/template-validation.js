import fs from "node:fs/promises";
import path from "node:path";

const requiredTemplateDirs = ["arborist", "docs", "experiments", "scripts"];
const requiredTemplateRootFiles = [".pre-commit-config.yaml", "AGENTS.md"];
const baseTemplateFiles = ["backlog.md", "feedback.md", "tasks.md", "todo.md"];
const requiredProjectDirs = ["arborist", "docs", "experiments", "scripts"];
const requiredProjectRootFiles = [".pre-commit-config.yaml", "AGENTS.md"];

const statOrNull = async (targetPath) => {
  try {
    return await fs.stat(targetPath);
  } catch {
    return null;
  }
};

const isDirectory = async (targetPath) => {
  const stats = await statOrNull(targetPath);
  return stats ? stats.isDirectory() : false;
};

const isFile = async (targetPath) => {
  const stats = await statOrNull(targetPath);
  return stats ? stats.isFile() : false;
};

const validateTemplateLayout = async (templatesDir) => {
  const missingDirs = [];
  const missingRootFiles = [];
  const missingBaseFiles = [];
  const misplacedBaseFiles = [];

  for (const dirName of requiredTemplateDirs) {
    if (!(await isDirectory(path.join(templatesDir, dirName)))) {
      missingDirs.push(dirName);
    }
  }

  for (const fileName of requiredTemplateRootFiles) {
    if (!(await isFile(path.join(templatesDir, fileName)))) {
      missingRootFiles.push(fileName);
    }
  }

  const arboristTemplatesDir = path.join(templatesDir, "arborist");
  for (const fileName of baseTemplateFiles) {
    if (!(await isFile(path.join(arboristTemplatesDir, fileName)))) {
      missingBaseFiles.push(fileName);
    }
    if (await isFile(path.join(templatesDir, fileName))) {
      misplacedBaseFiles.push(fileName);
    }
  }

  return { missingDirs, missingRootFiles, missingBaseFiles, misplacedBaseFiles };
};

const validateProjectLayout = async (projectDir) => {
  const missingDirs = [];
  const missingRootFiles = [];
  const missingBaseFiles = [];
  const misplacedBaseFiles = [];

  for (const dirName of requiredProjectDirs) {
    if (!(await isDirectory(path.join(projectDir, dirName)))) {
      missingDirs.push(dirName);
    }
  }

  for (const fileName of requiredProjectRootFiles) {
    if (!(await isFile(path.join(projectDir, fileName)))) {
      missingRootFiles.push(fileName);
    }
  }

  const arboristProjectDir = path.join(projectDir, "arborist");
  for (const fileName of baseTemplateFiles) {
    if (!(await isFile(path.join(arboristProjectDir, fileName)))) {
      missingBaseFiles.push(fileName);
    }
    if (await isFile(path.join(projectDir, fileName))) {
      misplacedBaseFiles.push(fileName);
    }
  }

  return { missingDirs, missingRootFiles, missingBaseFiles, misplacedBaseFiles };
};

const hasTemplateLayoutIssues = (issues) =>
  Boolean(
    issues.missingDirs.length ||
      issues.missingRootFiles.length ||
      issues.missingBaseFiles.length ||
      issues.misplacedBaseFiles.length,
  );

const hasProjectLayoutIssues = (issues) =>
  Boolean(
    issues.missingDirs.length ||
      issues.missingRootFiles.length ||
      issues.missingBaseFiles.length ||
      issues.misplacedBaseFiles.length,
  );

const formatTemplateLayoutIssues = (issues) => {
  const lines = [];
  if (issues.missingDirs.length) {
    lines.push(`Missing template directories: ${issues.missingDirs.join(", ")}`);
  }
  if (issues.missingRootFiles.length) {
    lines.push(`Missing template root files: ${issues.missingRootFiles.join(", ")}`);
  }
  if (issues.missingBaseFiles.length) {
    lines.push(`Missing base template files: ${issues.missingBaseFiles.join(", ")}`);
  }
  if (issues.misplacedBaseFiles.length) {
    lines.push(
      `Base template files found in templates root: ${issues.misplacedBaseFiles.join(", ")}`,
    );
  }
  return lines.join("\n");
};

const formatProjectLayoutIssues = (issues) => {
  const lines = [];
  if (issues.missingDirs.length) {
    lines.push(`Missing project directories: ${issues.missingDirs.join(", ")}`);
  }
  if (issues.missingRootFiles.length) {
    lines.push(`Missing project root files: ${issues.missingRootFiles.join(", ")}`);
  }
  if (issues.missingBaseFiles.length) {
    lines.push(`Missing project arborist files: ${issues.missingBaseFiles.join(", ")}`);
  }
  if (issues.misplacedBaseFiles.length) {
    lines.push(
      `Project arborist files found in project root: ${issues.misplacedBaseFiles.join(", ")}`,
    );
  }
  return lines.join("\n");
};

export {
  baseTemplateFiles,
  requiredProjectDirs,
  requiredProjectRootFiles,
  requiredTemplateDirs,
  requiredTemplateRootFiles,
  validateTemplateLayout,
  validateProjectLayout,
  hasTemplateLayoutIssues,
  hasProjectLayoutIssues,
  formatTemplateLayoutIssues,
  formatProjectLayoutIssues,
};
