// Board module: renders the Kanban columns from task data and wires
// drag-and-drop. Status changes are persisted through the API; the backend
// decides whether a move is valid.

import { fetchTasks, updateTask, ApiError, detailToMessage } from "./api.js";

export const STATUSES = ["ToDo", "InProgress", "Done"];
export const STATUS_LABELS = { ToDo: "To Do", InProgress: "In Progress", Done: "Done" };
const PRIORITY_ORDER = { High: 0, Medium: 1, Low: 2 };

const boardEl = document.getElementById("board");
const messageEl = document.getElementById("board-message");

let onEditTask = null;

export function setEditHandler(handler) {
  onEditTask = handler;
}

// --- UI states (loading / error / ready) -----------------------------------

function showMessage(text, { isError = false } = {}) {
  messageEl.textContent = text;
  messageEl.classList.toggle("is-error", isError);
  messageEl.hidden = false;
}

function clearMessage() {
  messageEl.hidden = true;
}

export async function refreshBoard() {
  showMessage("Loading tasks…");
  boardEl.setAttribute("aria-busy", "true");
  try {
    const tasks = await fetchTasks();
    clearMessage();
    renderBoard(tasks);
  } catch (error) {
    boardEl.replaceChildren();
    showMessage(
      `Could not load tasks: ${error instanceof ApiError ? detailToMessage(error.detail) : "backend unreachable. Is uvicorn running on port 8000?"}`,
      { isError: true },
    );
  } finally {
    boardEl.setAttribute("aria-busy", "false");
  }
}

// --- Rendering ---------------------------------------------------------------

function sortByPriorityThenId(tasks) {
  return [...tasks].sort(
    (a, b) => PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority] || a.id - b.id,
  );
}

export function renderBoard(tasks) {
  const columns = STATUSES.map((status) => {
    const columnTasks = sortByPriorityThenId(tasks.filter((t) => t.status === status));
    return buildColumn(status, columnTasks);
  });
  boardEl.replaceChildren(...columns);
}

/** Create an element with a class, text content, and children. */
function el(tag, className, text = "", ...children) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  node.append(...children);
  return node;
}

function buildColumn(status, tasks) {
  const header = el(
    "div",
    "column-header",
    "",
    el("h2", "", STATUS_LABELS[status]),
    el("span", "column-count", String(tasks.length)),
  );

  const list = el("div", "card-list", "");
  if (tasks.length === 0) {
    list.append(el("p", "column-empty", "No tasks"));
  } else {
    list.append(...tasks.map(buildCard));
  }

  const column = el("section", "column", "", header, list);
  column.dataset.status = status;
  wireColumnDropTarget(column);
  return column;
}

function buildCard(task) {
  const editBtn = el("button", "btn btn-icon", "✎");
  editBtn.type = "button";
  editBtn.setAttribute("aria-label", `Edit task: ${task.title}`);
  editBtn.addEventListener("click", () => onEditTask?.(task));

  const card = el(
    "article",
    "card",
    "",
    el("div", "card-top", "", el("h3", "card-title", task.title), editBtn),
  );
  card.draggable = true;
  card.dataset.taskId = String(task.id);
  card.dataset.status = task.status;

  if (task.description) {
    card.append(el("p", "card-description", task.description));
  }

  const meta = el(
    "div",
    "card-meta",
    "",
    el("span", `priority-badge priority-${task.priority.toLowerCase()}`, task.priority),
  );
  if (task.assignee) {
    meta.append(el("span", "card-assignee", task.assignee));
  }

  card.append(meta);
  wireCardDrag(card);
  return card;
}

// --- Drag-and-drop --------------------------------------------------------------

function wireCardDrag(card) {
  card.addEventListener("dragstart", (event) => {
    card.classList.add("dragging");
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData(
      "application/json",
      JSON.stringify({ taskId: card.dataset.taskId, fromStatus: card.dataset.status }),
    );
  });
  card.addEventListener("dragend", () => card.classList.remove("dragging"));
}

function wireColumnDropTarget(column) {
  column.addEventListener("dragover", (event) => {
    event.preventDefault(); // required to allow dropping
    event.dataTransfer.dropEffect = "move";
    column.classList.add("drag-over");
  });

  column.addEventListener("dragleave", () => column.classList.remove("drag-over"));

  column.addEventListener("drop", async (event) => {
    event.preventDefault();
    column.classList.remove("drag-over");

    let payload;
    try {
      payload = JSON.parse(event.dataTransfer.getData("application/json"));
    } catch {
      return;
    }

    const newStatus = column.dataset.status;
    // Same-column drop: no state change, so no PATCH request.
    if (payload.fromStatus === newStatus) return;

    try {
      await updateTask(Number(payload.taskId), { status: newStatus });
      await refreshBoard();
    } catch (error) {
      // Revert to server truth first, then show the rejection — refreshing
      // afterwards would immediately overwrite this message.
      await refreshBoard();
      const message =
        error instanceof ApiError
          ? `Move rejected: ${detailToMessage(error.detail)}`
          : "Move failed: backend unreachable.";
      showMessage(message, { isError: true });
      setTimeout(clearMessage, 6000);
    }
  });
}
