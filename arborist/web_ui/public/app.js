// Updates the Arborist UI shell with timestamps and project controls.

const PROJECT_API_BASE = "/api/projects";
const FEEDBACK_API_BASE = "/api/feedback";
const SAVE_STATE_API_BASE = "/api/save-state";

const projectState = {
  data: null,
  busy: false,
};

const feedbackState = {
  data: null,
  busy: false,
  followUpTarget: null,
};

const saveState = {
  busy: false,
};

const projectElements = {
  meta: document.getElementById("project-meta"),
  list: document.getElementById("project-list"),
  alert: document.getElementById("project-alert"),
};

const feedbackElements = {
  meta: document.getElementById("feedback-meta"),
  alert: document.getElementById("feedback-alert"),
  list: document.getElementById("feedback-list"),
  empty: document.getElementById("feedback-empty"),
  message: document.getElementById("feedback-message"),
  followUpForm: document.getElementById("followup-form"),
  followUpContext: document.getElementById("followup-context"),
  followUpMessage: document.getElementById("followup-message"),
  responseList: document.getElementById("response-list"),
  responseEmpty: document.getElementById("response-empty"),
};

const saveElements = {
  button: document.getElementById("save-state"),
  status: document.getElementById("save-state-status"),
};

const localUrlLink = document.getElementById("local-url");

/**
 * Escape a value for safe CSS selector use.
 * @param {string} value - Raw selector value.
 * @returns {string} Escaped value.
 */
const escapeCssValue = (value) => {
  if (typeof CSS !== "undefined" && typeof CSS.escape === "function") {
    return CSS.escape(value);
  }
  return String(value).replace(/[\\"]/g, "\\$&");
};

/**
 * Return the active project from the current project state.
 * @returns {{name: string, path: string} | null} Active project data.
 */
const getActiveProject = () => {
  const data = projectState.data;
  if (!data) {
    return null;
  }
  return data.projects.find((project) => project.path === data.activeProject) ?? null;
};

/**
 * Format a human-friendly timestamp for the status panel.
 * @returns {string} Localized date/time string.
 */
const formatStatusTime = () => new Date().toLocaleString();

/**
 * Update the status timestamp element if present.
 */
const updateStatusTime = () => {
  const target = document.getElementById("status-time");
  if (!target) {
    return;
  }
  target.textContent = formatStatusTime();
};

/**
 * Set the project alert copy and tone.
 * @param {string} message - Message to display.
 * @param {"info" | "error"} tone - Visual tone to apply.
 */
const setProjectAlert = (message, tone = "info") => {
  if (!projectElements.alert) {
    return;
  }
  projectElements.alert.textContent = message;
  projectElements.alert.classList.toggle("is-error", tone === "error");
  projectElements.alert.classList.toggle("is-info", tone !== "error");
};

/**
 * Set the feedback alert copy and tone.
 * @param {string} message - Message to display.
 * @param {"info" | "error"} tone - Visual tone to apply.
 */
const setFeedbackAlert = (message, tone = "info") => {
  if (!feedbackElements.alert) {
    return;
  }
  feedbackElements.alert.textContent = message;
  feedbackElements.alert.classList.toggle("is-error", tone === "error");
  feedbackElements.alert.classList.toggle("is-info", tone !== "error");
};

/**
 * Set the save state alert copy and tone.
 * @param {string} message - Message to display.
 * @param {"info" | "error" | "success"} tone - Visual tone to apply.
 */
const setSaveAlert = (message, tone = "info") => {
  if (!saveElements.status) {
    return;
  }
  saveElements.status.textContent = message;
  saveElements.status.classList.toggle("is-error", tone === "error");
  saveElements.status.classList.toggle("is-success", tone === "success");
  saveElements.status.classList.toggle("is-info", tone === "info");
};

/**
 * Format the display label for a project path.
 * @param {string} projectPath - Normalized project path.
 * @returns {string} Label to show.
 */
const formatProjectPath = (projectPath) => (projectPath === "." ? "Root" : projectPath);

/**
 * Format a response label for display.
 * @param {{date: string | null, summary: string, label: string}} entry - Response entry.
 * @returns {string} Display label.
 */
const formatResponseLabel = (entry) => entry.date ?? "Response";

/**
 * Update global project controls for busy state.
 * @param {boolean} busy - Whether requests are in flight.
 */
const setProjectBusy = (busy) => {
  projectState.busy = busy;
  if (projectElements.list) {
    projectElements.list.querySelectorAll(".project-item").forEach((item) => {
      item.setAttribute("aria-disabled", busy ? "true" : "false");
    });
    projectElements.list.querySelectorAll(".project-state").forEach((control) => {
      if (control instanceof HTMLElement) {
        control.setAttribute("aria-disabled", busy ? "true" : "false");
        control.tabIndex = busy ? -1 : 0;
      }
    });
    projectElements.list.querySelectorAll(".project-save").forEach((button) => {
      if (button instanceof HTMLButtonElement) {
        button.disabled = busy || saveState.busy;
      }
    });
  }
};

/**
 * Update feedback controls for busy state.
 * @param {boolean} busy - Whether requests are in flight.
 */
const setFeedbackBusy = (busy) => {
  feedbackState.busy = busy;
  const hasActiveProject = Boolean(feedbackState.data?.activeProject);
  const disableInputs = busy || !hasActiveProject;

  if (feedbackElements.message) {
    feedbackElements.message.disabled = disableInputs;
  }
  if (feedbackElements.followUpMessage) {
    feedbackElements.followUpMessage.disabled = disableInputs;
  }

  if (feedbackElements.responseList) {
    feedbackElements.responseList.querySelectorAll("button").forEach((button) => {
      button.disabled = disableInputs;
    });
  }
};

/**
 * Update save state controls for busy state.
 * @param {boolean} busy - Whether requests are in flight.
 */
const setSaveBusy = (busy) => {
  saveState.busy = busy;
  if (projectElements.list) {
    projectElements.list.querySelectorAll(".project-save").forEach((button) => {
      if (button instanceof HTMLButtonElement) {
        button.disabled = busy || projectState.busy;
      }
    });
  }
};

/**
 * Build a project list item element.
 * @param {{name: string, path: string, enabled: boolean, active: boolean}} project - Project data.
 * @returns {HTMLLIElement} List item element.
 */
const buildProjectItem = (project) => {
  const item = document.createElement("li");
  item.className = "project-item";
  if (project.active) {
    item.classList.add("is-active");
    item.setAttribute("aria-current", "true");
  }
  if (!project.enabled) {
    item.classList.add("is-disabled");
  }
  item.setAttribute("role", "button");
  item.tabIndex = 0;

  const main = document.createElement("div");
  main.className = "project-main";

  const info = document.createElement("div");

  const name = document.createElement("div");
  name.className = "project-name";
  name.textContent = project.name;

  const path = document.createElement("span");
  path.className = "project-path";
  path.textContent = formatProjectPath(project.path);

  info.append(name, path);
  const actions = document.createElement("div");
  actions.className = "project-actions";

  const state = document.createElement("span");
  state.className = "project-state";
  state.textContent = project.enabled ? "Enabled" : "Paused";
  state.setAttribute("role", "button");
  state.tabIndex = 0;
  state.setAttribute("aria-label", project.enabled ? "Pause project" : "Enable project");
  actions.append(state);

  const saveButton = document.createElement("button");
  saveButton.className = "project-save";
  saveButton.type = "button";
  saveButton.textContent = "Save";
  saveButton.setAttribute("aria-label", `Save state for ${project.name}`);
  actions.append(saveButton);

  main.append(info, actions);
  item.append(main);

  const handleActivate = (event) => {
    if (projectState.busy) {
      return;
    }
    const target = event.target;
    if (target instanceof HTMLElement && target.closest(".project-state, .project-save")) {
      return;
    }
    if (project.active) {
      updateActiveProject(null);
      return;
    }
    updateActiveProject(project.path);
  };

  const handleToggleEnabled = () => {
    if (projectState.busy) {
      return;
    }
    updateEnabledProject(project.path, !project.enabled);
  };

  const handleSave = async () => {
    if (projectState.busy || saveState.busy) {
      return;
    }
    if ((projectState.data?.activeProject ?? null) !== project.path) {
      await updateActiveProject(project.path);
      if ((projectState.data?.activeProject ?? null) !== project.path) {
        return;
      }
    }
    await saveWorkspaceState();
  };

  item.addEventListener("click", handleActivate);
  state.addEventListener("click", (event) => {
    event.stopPropagation();
    handleToggleEnabled();
  });
  state.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      event.stopPropagation();
      handleToggleEnabled();
    }
  });
  saveButton.addEventListener("click", (event) => {
    event.stopPropagation();
    handleSave();
  });
  item.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleActivate(event);
    }
  });

  return item;
};

/**
 * Render project data into the UI.
 */
const renderProjectState = () => {
  const data = projectState.data;
  if (!data) {
    if (projectElements.meta) {
      projectElements.meta.textContent = "Loading...";
    }
    return;
  }

  const total = data.projects.length;
  const enabledCount = data.projects.filter((project) => project.enabled).length;
  if (projectElements.meta) {
    if (total === 0) {
      projectElements.meta.textContent = "No projects found";
    } else if (!data.usingActiveProjects) {
      projectElements.meta.textContent = `All ${total} enabled (default)`;
    } else {
      projectElements.meta.textContent = `${enabledCount} of ${total} enabled`;
    }
  }

  if (projectElements.list) {
    projectElements.list.replaceChildren();
    if (total > 0) {
      const fragment = document.createDocumentFragment();
      data.projects.forEach((project) => {
        fragment.append(buildProjectItem(project));
      });
      projectElements.list.append(fragment);
    }
  }

  if (total === 0) {
    setProjectAlert("No projects discovered in this workspace.", "info");
  } else if (projectElements.alert?.classList.contains("is-info")) {
    setProjectAlert("", "info");
  }

  setProjectBusy(projectState.busy);
  renderSaveState();
};

/**
 * Build a queued feedback list item.
 * @param {string} item - Feedback item text.
 * @param {{isActive?: boolean}} [options] - Display options for the item.
 * @returns {HTMLLIElement} List item element.
 */
const buildFeedbackItem = (item, options = {}) => {
  const listItem = document.createElement("li");
  listItem.className = "feedback-item";

  if (options.isActive) {
    listItem.classList.add("is-active");
    listItem.setAttribute("aria-current", "true");
    const badge = document.createElement("span");
    badge.className = "feedback-badge";
    badge.textContent = "In progress";
    listItem.append(badge);
  }

  const text = document.createElement("p");
  text.className = "feedback-text";
  text.textContent = item;
  listItem.append(text);
  return listItem;
};

/**
 * Build a response list item with follow-up action.
 * @param {{id: string, date: string | null, summary: string, label: string, details: string[]}} entry - Response entry.
 * @returns {HTMLLIElement} List item element.
 */
const buildResponseItem = (entry) => {
  const listItem = document.createElement("li");
  listItem.className = "response-item";
  listItem.dataset.responseId = entry.id;
  listItem.setAttribute("role", "button");
  listItem.tabIndex = 0;
  listItem.setAttribute("aria-label", "Open follow-up form for this response");
  listItem.classList.add("is-selectable");
  if (feedbackState.followUpTarget?.id === entry.id) {
    listItem.classList.add("is-target");
    listItem.setAttribute("aria-current", "true");
  }

  const meta = document.createElement("div");
  meta.className = "response-meta";
  meta.textContent = formatResponseLabel(entry);

  const summary = document.createElement("p");
  summary.className = "response-summary";
  summary.textContent = entry.summary || entry.label;

  const selectTarget = () => {
    if (feedbackState.busy) {
      return;
    }
    selectFollowUpTarget(entry);
  };

  listItem.append(meta, summary);

  if (entry.details && entry.details.length > 0) {
    const details = document.createElement("p");
    details.className = "response-details";
    details.textContent = entry.details.join(" · ");
    listItem.append(details);
  }

  listItem.addEventListener("click", selectTarget);
  listItem.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      selectTarget();
    }
  });
  return listItem;
};

/**
 * Render feedback state into the UI.
 */
const renderFeedbackState = () => {
  const data = feedbackState.data;
  if (!data) {
    if (feedbackElements.meta) {
      feedbackElements.meta.textContent = "Loading...";
    }
    return;
  }

  const queueCount = data.feedback?.count ?? 0;
  if (feedbackElements.meta) {
    feedbackElements.meta.textContent = data.activeProject
      ? `${queueCount} queued`
      : "No active project";
  }

  if (feedbackElements.list) {
    feedbackElements.list.replaceChildren();
    const items = data.feedback?.items ?? [];
    if (items.length > 0) {
      const activeIndex = 0;
      const fragment = document.createDocumentFragment();
      items.forEach((item, index) => {
        fragment.append(buildFeedbackItem(item, { isActive: index === activeIndex }));
      });
      feedbackElements.list.append(fragment);
    }
  }
  if (feedbackElements.empty) {
    const empty = (data.feedback?.items ?? []).length === 0;
    feedbackElements.empty.hidden = !empty;
  }

  if (feedbackElements.responseList) {
    feedbackElements.responseList.replaceChildren();
    const responses = data.responses ?? [];
    if (responses.length > 0) {
      const fragment = document.createDocumentFragment();
      responses.forEach((entry) => {
        fragment.append(buildResponseItem(entry));
      });
      feedbackElements.responseList.append(fragment);
    }
  }

  if (feedbackElements.followUpForm) {
    const responseSection = feedbackElements.responseList?.parentElement ?? null;
    if (!feedbackState.followUpTarget || !feedbackElements.responseList) {
      feedbackElements.followUpForm.hidden = true;
      if (responseSection) {
        responseSection.append(feedbackElements.followUpForm);
      }
    } else {
      const targetSelector = `[data-response-id="${escapeCssValue(feedbackState.followUpTarget.id)}"]`;
      const targetRow = feedbackElements.responseList.querySelector(targetSelector);
      if (targetRow instanceof HTMLElement) {
        feedbackElements.followUpForm.hidden = false;
        targetRow.append(feedbackElements.followUpForm);
      } else {
        feedbackElements.followUpForm.hidden = true;
        if (responseSection) {
          responseSection.append(feedbackElements.followUpForm);
        }
      }
    }
  }

  if (feedbackElements.responseEmpty) {
    const empty = (data.responses ?? []).length === 0;
    feedbackElements.responseEmpty.hidden = !empty;
  }

  if (
    feedbackState.followUpTarget &&
    !(data.responses ?? []).some((entry) => entry.id === feedbackState.followUpTarget.id)
  ) {
    clearFollowUpTarget();
  }

  if (!data.activeProject) {
    clearFollowUpTarget();
  }

  if (!data.activeProject) {
    setFeedbackAlert("Select an active project to submit feedback.", "info");
  } else if (feedbackElements.alert?.classList.contains("is-info")) {
    setFeedbackAlert("", "info");
  }

  setFeedbackBusy(feedbackState.busy);
};

/**
 * Render save state UI with the latest project context.
 */
const renderSaveState = () => {
  if (!projectState.data) {
    return;
  }
  setSaveBusy(saveState.busy);
  if (saveElements.status?.classList.contains("is-info")) {
    setSaveAlert("", "info");
  }
};

/**
 * Fetch JSON from the local API.
 * @param {string} path - API path.
 * @param {RequestInit} [options] - Fetch options.
 * @returns {Promise<unknown>} Parsed JSON response.
 */
const requestJson = async (path, options = {}) => {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message = payload?.error ?? response.statusText ?? "Request failed.";
    throw new Error(message);
  }

  return payload;
};

/**
 * Load the latest feedback state from the server.
 */
const refreshFeedback = async () => {
  if (feedbackState.busy) {
    return;
  }
  setFeedbackBusy(true);
  setFeedbackAlert("Refreshing feedback...", "info");
  try {
    feedbackState.data = await requestJson(FEEDBACK_API_BASE);
    setFeedbackAlert("", "info");
    renderFeedbackState();
    updateStatusTime();
  } catch (error) {
    setFeedbackAlert(error?.message ?? "Unable to load feedback.", "error");
  } finally {
    setFeedbackBusy(false);
  }
};

/**
 * Load the latest project state from the server.
 */
const refreshProjects = async () => {
  if (projectState.busy) {
    return;
  }
  setProjectBusy(true);
  setProjectAlert("Refreshing projects...", "info");
  try {
    projectState.data = await requestJson(PROJECT_API_BASE);
    setProjectAlert("", "info");
    renderProjectState();
    updateStatusTime();
  } catch (error) {
    setProjectAlert(error?.message ?? "Unable to load projects.", "error");
  } finally {
    setProjectBusy(false);
  }
};

/**
 * Update the enabled flag for a project.
 * @param {string} projectPath - Relative project path.
 * @param {boolean} enabled - Desired enabled state.
 */
const updateEnabledProject = async (projectPath, enabled) => {
  if (projectState.busy) {
    return;
  }
  const prior = projectState.data;
  setProjectBusy(true);
  setProjectAlert("Updating project...", "info");
  try {
    projectState.data = await requestJson(`${PROJECT_API_BASE}/enabled`, {
      method: "POST",
      body: JSON.stringify({ path: projectPath, enabled }),
    });
    setProjectAlert("", "info");
    renderProjectState();
    refreshFeedback();
    updateStatusTime();
  } catch (error) {
    projectState.data = prior;
    renderProjectState();
    setProjectAlert(error?.message ?? "Unable to update project.", "error");
  } finally {
    setProjectBusy(false);
  }
};

/**
 * Update the active project selection.
 * @param {string | null} projectPath - Relative project path or null to clear.
 */
const updateActiveProject = async (projectPath) => {
  if (projectState.busy) {
    return;
  }
  const prior = projectState.data;
  setProjectBusy(true);
  setProjectAlert("Updating active project...", "info");
  try {
    projectState.data = await requestJson(`${PROJECT_API_BASE}/active`, {
      method: "POST",
      body: JSON.stringify({ path: projectPath }),
    });
    setProjectAlert("", "info");
    renderProjectState();
    refreshFeedback();
    updateStatusTime();
  } catch (error) {
    projectState.data = prior;
    renderProjectState();
    setProjectAlert(error?.message ?? "Unable to update active project.", "error");
  } finally {
    setProjectBusy(false);
  }
};

/**
 * Submit new feedback to the active project.
 */
const submitFeedback = async () => {
  if (feedbackState.busy) {
    return;
  }
  const message = feedbackElements.message?.value ?? "";
  if (!message.trim()) {
    setFeedbackAlert("Enter a feedback message before submitting.", "error");
    return;
  }

  setFeedbackBusy(true);
  setFeedbackAlert("Submitting feedback...", "info");
  try {
    feedbackState.data = await requestJson(FEEDBACK_API_BASE, {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    if (feedbackElements.message) {
      feedbackElements.message.value = "";
    }
    setFeedbackAlert("Feedback queued.", "info");
    renderFeedbackState();
    updateStatusTime();
  } catch (error) {
    setFeedbackAlert(error?.message ?? "Unable to submit feedback.", "error");
  } finally {
    setFeedbackBusy(false);
  }
};

/**
 * Select a response entry for follow-up.
 * @param {{id: string, summary: string, label: string}} entry - Response entry.
 */
const selectFollowUpTarget = (entry) => {
  if (feedbackState.followUpTarget?.id === entry.id) {
    clearFollowUpTarget();
    renderFeedbackState();
    return;
  }
  const previousTargetId = feedbackState.followUpTarget?.id ?? null;
  feedbackState.followUpTarget = entry;
  if (feedbackElements.followUpContext) {
    feedbackElements.followUpContext.textContent = entry.summary || entry.label || "Response";
  }
  if (feedbackElements.followUpMessage && previousTargetId !== entry.id) {
    feedbackElements.followUpMessage.value = "";
  }
  if (feedbackElements.followUpForm) {
    feedbackElements.followUpForm.hidden = false;
  }
  renderFeedbackState();
  if (feedbackElements.followUpMessage) {
    feedbackElements.followUpMessage.focus();
  }
};

/**
 * Clear the follow-up form state.
 */
const clearFollowUpTarget = () => {
  feedbackState.followUpTarget = null;
  if (feedbackElements.followUpContext) {
    feedbackElements.followUpContext.textContent = "None selected";
  }
  if (feedbackElements.followUpForm) {
    feedbackElements.followUpForm.hidden = true;
  }
  if (feedbackElements.followUpMessage) {
    feedbackElements.followUpMessage.value = "";
  }
};

/**
 * Submit a follow-up message for a response entry.
 */
const submitFollowUp = async () => {
  if (feedbackState.busy) {
    return;
  }
  const target = feedbackState.followUpTarget;
  if (!target) {
    setFeedbackAlert("Select a response before sending a follow-up.", "error");
    return;
  }

  const message = feedbackElements.followUpMessage?.value ?? "";
  setFeedbackBusy(true);
  setFeedbackAlert("Sending follow-up...", "info");
  try {
    feedbackState.data = await requestJson(`${FEEDBACK_API_BASE}/follow-up`, {
      method: "POST",
      body: JSON.stringify({ responseId: target.id, message }),
    });
    clearFollowUpTarget();
    setFeedbackAlert("Follow-up queued.", "info");
    renderFeedbackState();
    updateStatusTime();
  } catch (error) {
    setFeedbackAlert(error?.message ?? "Unable to send follow-up.", "error");
  } finally {
    setFeedbackBusy(false);
  }
};

/**
 * Trigger the save state action for the active project.
 */
const saveWorkspaceState = async () => {
  if (saveState.busy) {
    return;
  }
  const activeProject = getActiveProject();
  if (!activeProject) {
    setSaveAlert("Select an active project to save state.", "error");
    return;
  }

  setSaveBusy(true);
  setSaveAlert(`Saving state for ${activeProject.name}...`, "info");
  try {
    const payload = await requestJson(SAVE_STATE_API_BASE, { method: "POST" });
    const result = payload?.result ?? null;
    if (result?.status === "saved") {
      setSaveAlert(result.message ?? "State saved.", "success");
    } else if (result?.status === "noop") {
      setSaveAlert(result.message ?? "No local changes to save.", "info");
    } else {
      setSaveAlert(result?.message ?? "Save state completed.", "info");
    }
    updateStatusTime();
  } catch (error) {
    setSaveAlert(error?.message ?? "Unable to save state.", "error");
  } finally {
    setSaveBusy(false);
  }
};

/**
 * Initialize the shell by updating timestamps on an interval.
 */
const startStatusLoop = () => {
  updateStatusTime();
  window.setInterval(updateStatusTime, 60 * 1000);
};

/**
 * Wire UI events and request initial project state.
 */
const startProjectControls = () => {
  refreshProjects();
  window.setInterval(() => refreshProjects(), 45000);
};

/**
 * Wire feedback panel events and request initial feedback state.
 */
const startFeedbackControls = () => {
  if (feedbackElements.message) {
    feedbackElements.message.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" || event.shiftKey || event.isComposing) {
        return;
      }
      event.preventDefault();
      submitFeedback();
    });
  }
  if (feedbackElements.followUpMessage) {
    feedbackElements.followUpMessage.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" || event.shiftKey || event.isComposing) {
        return;
      }
      event.preventDefault();
      submitFollowUp();
    });
  }
  refreshFeedback();
  window.setInterval(() => refreshFeedback(), 45000);
};

/**
 * Wire save state panel events.
 */
const startSaveStateControls = () => {
  if (saveElements.button) {
    saveElements.button.addEventListener("click", () => saveWorkspaceState());
  }
  renderSaveState();
};

/**
 * Populate the local URL link with the current origin.
 */
const setLocalUrlLink = () => {
  if (!localUrlLink) {
    return;
  }
  const origin = window.location.origin;
  localUrlLink.textContent = origin;
  localUrlLink.href = origin;
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    startStatusLoop();
    startProjectControls();
    startFeedbackControls();
    startSaveStateControls();
    setLocalUrlLink();
  });
} else {
  startStatusLoop();
  startProjectControls();
  startFeedbackControls();
  startSaveStateControls();
  setLocalUrlLink();
}
