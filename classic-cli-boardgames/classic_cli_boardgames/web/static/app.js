const state = {
  options: null,
  session: null,
  autoPlay: false,
  autoTimer: null,
  autoBusy: false,
};

const elements = {
  gameSelect: document.getElementById("game-select"),
  difficultySelect: document.getElementById("difficulty-select"),
  modeSelect: document.getElementById("mode-select"),
  setupForm: document.getElementById("setup-form"),
  sessionPill: document.getElementById("session-pill"),
  metaMode: document.getElementById("meta-mode"),
  metaDifficulty: document.getElementById("meta-difficulty"),
  metaTurn: document.getElementById("meta-turn"),
  helpButton: document.getElementById("help-button"),
  helpOutput: document.getElementById("help-output"),
  boardSubtitle: document.getElementById("board-subtitle"),
  boardOutput: document.getElementById("board-output"),
  boardVisual: document.getElementById("board-visual"),
  boardNotes: document.getElementById("board-notes"),
  moveForm: document.getElementById("move-form"),
  moveInput: document.getElementById("move-input"),
  restartButton: document.getElementById("restart-button"),
  endButton: document.getElementById("end-button"),
  aiStepButton: document.getElementById("ai-step-button"),
  autoButton: document.getElementById("auto-button"),
  statusText: document.getElementById("status-text"),
  logList: document.getElementById("log-list"),
  logCount: document.getElementById("log-count"),
};

function setStatus(text) {
  elements.statusText.textContent = text;
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    const message = data && data.error ? data.error : "Request failed.";
    throw new Error(message);
  }
  return data;
}

function fillSelect(select, items, defaultKey) {
  select.innerHTML = "";
  for (const item of items) {
    const option = document.createElement("option");
    option.value = item.key;
    option.textContent = item.name;
    select.appendChild(option);
  }
  if (defaultKey) {
    select.value = defaultKey;
  }
}

function updateMeta(session) {
  if (!session) {
    elements.metaMode.textContent = "-";
    elements.metaDifficulty.textContent = "-";
    elements.metaTurn.textContent = "-";
    return;
  }
  elements.metaMode.textContent = session.player_mode;
  elements.metaDifficulty.textContent = session.difficulty;
  elements.metaTurn.textContent = session.active_color;
}

function updateSessionPill(session) {
  if (!session) {
    elements.sessionPill.textContent = "No active session";
    return;
  }
  elements.sessionPill.textContent = `${session.game} session active`;
}

function countChar(text, char) {
  let count = 0;
  for (const letter of text) {
    if (letter === char) {
      count += 1;
    }
  }
  return count;
}

function isSeparatorLine(line) {
  return (
    /[+-]/.test(line) &&
    line.includes("+") &&
    line.includes("-") &&
    /^[\s+-]+$/.test(line)
  );
}

function isGridContentLine(line) {
  return countChar(line, "|") >= 2;
}

function isGridLine(line) {
  return isSeparatorLine(line) || isGridContentLine(line);
}

function parseGridLine(line) {
  const pipeIndex = line.indexOf("|");
  if (pipeIndex === -1) {
    return null;
  }
  const label = line.slice(0, pipeIndex).trim();
  const parts = line.slice(pipeIndex + 1).split("|");
  parts.pop();
  const cells = parts.map((cell) => cell.trim());
  return { label: label || null, cells };
}

function parseGridGroup(lines) {
  const grids = [];
  let index = 0;
  while (index < lines.length) {
    while (index < lines.length && !lines[index].includes("|")) {
      index += 1;
    }
    if (index >= lines.length) {
      break;
    }
    const colLine = parseGridLine(lines[index]);
    if (!colLine) {
      break;
    }
    const colLabels = colLine.cells;
    index += 1;
    if (index < lines.length && isSeparatorLine(lines[index])) {
      index += 1;
    }
    const rows = [];
    const rowLabels = [];
    while (index < lines.length && lines[index].includes("|")) {
      const rowLine = parseGridLine(lines[index]);
      if (!rowLine) {
        break;
      }
      rows.push(rowLine.cells);
      rowLabels.push(rowLine.label || "");
      index += 1;
      if (index < lines.length && isSeparatorLine(lines[index])) {
        index += 1;
      }
      if (index < lines.length && lines[index].includes("|")) {
        const nextPrefix = lines[index]
          .slice(0, lines[index].indexOf("|"))
          .trim();
        if (nextPrefix === "") {
          break;
        }
      }
    }
    grids.push({ colLabels, rowLabels, rows });
  }
  return grids;
}

function splitRender(renderText) {
  const metaLines = [];
  const grids = [];
  const buffer = [];
  const lines = (renderText || "").split("\n");

  const flush = () => {
    if (buffer.length > 0) {
      grids.push(...parseGridGroup(buffer));
      buffer.length = 0;
    }
  };

  for (const line of lines) {
    if (isGridLine(line)) {
      buffer.push(line);
      continue;
    }
    flush();
    const trimmed = line.trim();
    if (trimmed) {
      metaLines.push(trimmed);
    }
  }
  flush();
  return { metaLines, grids };
}

function createPieceElement(gameKey, value) {
  if (!value || value === "." || value === " ") {
    return null;
  }

  if (gameKey === "chess") {
    const lower = value.toLowerCase();
    const types = {
      p: "pawn",
      n: "knight",
      b: "bishop",
      r: "rook",
      q: "queen",
      k: "king",
    };
    const type = types[lower];
    if (!type) {
      return null;
    }
    const piece = document.createElement("span");
    piece.className = `piece piece--${value === value.toUpperCase() ? "white" : "black"} piece--${type}`;
    piece.textContent = value.toUpperCase();
    return piece;
  }

  if (gameKey === "checkers") {
    const isWhite = value.toLowerCase() === "w";
    const isKing = value === value.toUpperCase();
    const piece = document.createElement("span");
    const kingClass = isKing ? " piece--king" : "";
    piece.className = `piece piece--checker piece--${isWhite ? "white" : "black"}${kingClass}`;
    piece.textContent = isKing ? "K" : "";
    return piece;
  }

  if (gameKey === "go") {
    const stone = value.toUpperCase();
    if (stone !== "B" && stone !== "W") {
      return null;
    }
    const piece = document.createElement("span");
    piece.className = `piece piece--go piece--${stone === "W" ? "white" : "black"}`;
    piece.textContent = "";
    return piece;
  }

  if (gameKey === "backgammon") {
    const match = value.match(/^([WB])(\d+)$/);
    if (!match) {
      return null;
    }
    const color = match[1] === "W" ? "white" : "black";
    const count = Number.parseInt(match[2], 10);
    const checker = document.createElement("span");
    checker.className = `checker checker--${color}`;
    checker.textContent = count > 1 ? String(count) : "";
    checker.title = `${color} ${count}`;
    return checker;
  }

  return null;
}

function renderGrid(grid, gameKey) {
  const rows = grid.rows.length;
  const cols = grid.colLabels.length;
  const wrapper = document.createElement("div");
  const isBackgammon = gameKey === "backgammon";
  const isGo = gameKey === "go";
  wrapper.className = `board-grid ${isBackgammon ? "board-grid--backgammon" : isGo ? "board-grid--go" : "board-grid--square"}`;
  wrapper.style.gridTemplateColumns = `minmax(36px, auto) repeat(${cols}, minmax(40px, 1fr))`;
  wrapper.style.gridTemplateRows = `minmax(28px, auto) repeat(${rows}, minmax(40px, 1fr))`;

  const corner = document.createElement("div");
  corner.className = "board-label";
  corner.style.gridRow = "1";
  corner.style.gridColumn = "1";
  wrapper.appendChild(corner);

  grid.colLabels.forEach((label, colIndex) => {
    const colLabel = document.createElement("div");
    colLabel.className = "board-label";
    colLabel.textContent = label;
    colLabel.style.gridRow = "1";
    colLabel.style.gridColumn = `${colIndex + 2}`;
    wrapper.appendChild(colLabel);
  });

  grid.rowLabels.forEach((label, rowIndex) => {
    const rowLabel = document.createElement("div");
    rowLabel.className = "board-label";
    rowLabel.textContent = label;
    rowLabel.style.gridRow = `${rowIndex + 2}`;
    rowLabel.style.gridColumn = "1";
    wrapper.appendChild(rowLabel);
  });

  grid.rows.forEach((row, rowIndex) => {
    row.forEach((value, colIndex) => {
      const cell = document.createElement("div");
      const isDark = (rowIndex + colIndex) % 2 === 1;
      const palette = isGo
        ? "board-cell--go"
        : isDark
          ? "board-cell--dark"
          : "board-cell--light";
      const style = isBackgammon ? `${palette} board-cell--point` : palette;
      cell.className = `board-cell ${style}`;
      cell.style.gridRow = `${rowIndex + 2}`;
      cell.style.gridColumn = `${colIndex + 2}`;
      const piece = createPieceElement(gameKey, value);
      if (piece) {
        cell.appendChild(piece);
      }
      wrapper.appendChild(cell);
    });
  });

  return wrapper;
}

function renderBoard(session) {
  elements.boardVisual.innerHTML = "";
  elements.boardNotes.innerHTML = "";
  if (!session) {
    return;
  }

  const parsed = splitRender(session.render || "");
  elements.boardOutput.dataset.game = session.game_key || "";

  if (parsed.metaLines.length > 0) {
    for (const line of parsed.metaLines) {
      const note = document.createElement("div");
      note.className = "board-note";
      note.textContent = line;
      elements.boardNotes.appendChild(note);
    }
  }

  if (parsed.grids.length === 0) {
    const fallback = document.createElement("pre");
    fallback.className = "board-fallback";
    fallback.textContent = session.render || "";
    elements.boardVisual.appendChild(fallback);
    return;
  }

  for (const grid of parsed.grids) {
    elements.boardVisual.appendChild(renderGrid(grid, session.game_key));
  }
}

function updateBoard(session) {
  if (!session) {
    elements.boardVisual.innerHTML = "";
    elements.boardNotes.innerHTML = "";
    const empty = document.createElement("div");
    empty.className = "board-empty";
    empty.textContent = "Start a match to render the board.";
    elements.boardVisual.appendChild(empty);
    elements.boardSubtitle.textContent = "Start a match to render the board.";
    elements.boardOutput.dataset.game = "";
    return;
  }
  renderBoard(session);
  elements.boardSubtitle.textContent = session.terminal
    ? "Game over. Restart or start a new match."
    : `Active color: ${session.active_color}`;
}

function updateLog(log) {
  elements.logList.innerHTML = "";
  if (!log || log.length === 0) {
    elements.logCount.textContent = "0 entries";
    return;
  }
  for (const entry of log.slice().reverse()) {
    const item = document.createElement("li");
    item.textContent = entry;
    elements.logList.appendChild(item);
  }
  elements.logCount.textContent = `${log.length} entries`;
}

function updateActionState(session) {
  const hasSession = Boolean(session);
  const canMove = hasSession && session.human_can_move;
  elements.moveInput.disabled = !canMove;
  elements.moveForm.querySelector("button").disabled = !canMove;
  elements.restartButton.disabled = !hasSession;
  elements.endButton.disabled = !hasSession;
  elements.aiStepButton.disabled = !hasSession || !session.ai_vs_ai || session.terminal;
  elements.autoButton.disabled = !hasSession || !session.ai_vs_ai || session.terminal;

  if (!hasSession) {
    setStatus("Waiting for a session.");
    return;
  }
  if (session.terminal) {
    if (session.outcome && session.outcome.winner) {
      setStatus(`${session.outcome.winner} wins by ${session.outcome.reason}.`);
    } else {
      setStatus("Game over.");
    }
    return;
  }
  if (session.ai_vs_ai) {
    setStatus("AI vs AI mode. Use Next move or enable auto-play.");
    return;
  }
  setStatus(session.human_can_move ? "Your move." : "Waiting for the computer.");
}

function renderSession(session) {
  state.session = session;
  updateSessionPill(session);
  updateMeta(session);
  updateBoard(session);
  updateLog(session ? session.log : []);
  updateActionState(session);
  if (state.autoPlay && (!session || session.terminal)) {
    stopAutoPlay();
  }
}

async function loadOptions() {
  const data = await fetchJson("/api/options");
  state.options = data;
  fillSelect(elements.gameSelect, data.games, data.defaults.game);
  fillSelect(elements.difficultySelect, data.difficulties, data.defaults.difficulty);
  fillSelect(elements.modeSelect, data.player_modes, data.defaults.player_mode);
  elements.helpOutput.textContent = data.help[data.defaults.game] || "";
}

async function startSession() {
  const payload = {
    game_key: elements.gameSelect.value,
    difficulty: elements.difficultySelect.value,
    player_mode: elements.modeSelect.value,
  };
  const data = await fetchJson("/api/session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  renderSession(data.session);
  setStatus("Session created. Make your move.");
}

async function sendAction(action) {
  if (!state.session) {
    return;
  }
  const data = await fetchJson(`/api/session/${state.session.id}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(action),
  });
  if (data.help) {
    elements.helpOutput.textContent = data.help;
  }
  if (data.ended) {
    renderSession(null);
    setStatus("Session ended.");
    return;
  }
  if (data.message) {
    setStatus(data.message);
  }
  if (data.session) {
    renderSession(data.session);
  }
}

function stopAutoPlay() {
  state.autoPlay = false;
  elements.autoButton.textContent = "Auto-play off";
  if (state.autoTimer) {
    clearInterval(state.autoTimer);
    state.autoTimer = null;
  }
}

function startAutoPlay() {
  if (!state.session || !state.session.ai_vs_ai) {
    return;
  }
  state.autoPlay = true;
  elements.autoButton.textContent = "Auto-play on";
  state.autoTimer = setInterval(async () => {
    if (state.autoBusy || !state.session || state.session.terminal) {
      return;
    }
    state.autoBusy = true;
    try {
      await sendAction({ type: "ai_step" });
    } catch (error) {
      setStatus(error.message);
      stopAutoPlay();
    } finally {
      state.autoBusy = false;
    }
  }, 700);
}

function toggleAutoPlay() {
  if (state.autoPlay) {
    stopAutoPlay();
  } else {
    startAutoPlay();
  }
}

function handleHelp() {
  if (state.session) {
    sendAction({ type: "help" });
    return;
  }
  if (state.options) {
    const key = elements.gameSelect.value;
    elements.helpOutput.textContent = state.options.help[key] || "";
  }
}

function wireEvents() {
  elements.setupForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    stopAutoPlay();
    try {
      await startSession();
    } catch (error) {
      setStatus(error.message);
    }
  });

  elements.moveForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = elements.moveInput.value.trim();
    if (!text) {
      setStatus("Enter a move first.");
      return;
    }
    elements.moveInput.value = "";
    try {
      await sendAction({ type: "move", text });
    } catch (error) {
      setStatus(error.message);
    }
  });

  elements.restartButton.addEventListener("click", async () => {
    stopAutoPlay();
    try {
      await sendAction({ type: "restart" });
    } catch (error) {
      setStatus(error.message);
    }
  });

  elements.endButton.addEventListener("click", async () => {
    stopAutoPlay();
    try {
      await sendAction({ type: "end" });
    } catch (error) {
      setStatus(error.message);
    }
  });

  elements.aiStepButton.addEventListener("click", async () => {
    try {
      await sendAction({ type: "ai_step" });
    } catch (error) {
      setStatus(error.message);
    }
  });

  elements.autoButton.addEventListener("click", toggleAutoPlay);
  elements.helpButton.addEventListener("click", handleHelp);
  elements.gameSelect.addEventListener("change", handleHelp);
}

async function init() {
  try {
    await loadOptions();
    renderSession(null);
  } catch (error) {
    setStatus(error.message);
  }
  wireEvents();
  document.body.classList.add("loaded");
}

init();
