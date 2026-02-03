const hasWorkItems = (contents) =>
  contents
    .split(/\r?\n/)
    .some((raw) => raw.trim() && !raw.trim().startsWith("#"));

const readFirstLine = (contents) => {
  const [firstLine] = contents.split(/\r?\n/);
  return firstLine ?? "";
};

export { hasWorkItems, readFirstLine };
