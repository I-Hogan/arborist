import fs from "node:fs";
import fsp from "node:fs/promises";
import { readFirstLine } from "./list-utils.js";

const clearListFile = async (filePath) => {
  if (!filePath || !fs.existsSync(filePath)) {
    return;
  }
  const contents = await fsp.readFile(filePath, "utf8");
  const firstLine = readFirstLine(contents);
  const updated = firstLine ? `${firstLine}\n` : "";
  await fsp.writeFile(filePath, updated, "utf8");
};

const clearListFiles = async (filePaths) => {
  if (!Array.isArray(filePaths)) {
    return;
  }
  for (const filePath of filePaths) {
    if (!filePath) {
      continue;
    }
    await clearListFile(filePath);
  }
};

export { clearListFile, clearListFiles };
