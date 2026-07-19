// Modal module: the create/edit form. Client-side validation trims the title
// and blocks empty submissions (no network request); everything else is
// enforced by the backend, whose 422 messages are shown without closing
// the modal.

import { createTask, updateTask, ApiError, detailToMessage } from "./api.js";

const overlay = document.getElementById("modal-overlay");
const modalTitle = document.getElementById("modal-title");
const form = document.getElementById("task-form");

const fields = {
  taskId: document.getElementById("field-task-id"),
  title: document.getElementById("field-title"),
  description: document.getElementById("field-description"),
  status: document.getElementById("field-status"),
  priority: document.getElementById("field-priority"),
  assignee: document.getElementById("field-assignee"),
};

const titleError = document.getElementById("error-title");
const serverError = document.getElementById("error-server");

let onSaved = null;
let editingTask = null; // task being edited, or null in create mode

export function initModal({ onSaved: savedHandler }) {
  onSaved = savedHandler;

  document.getElementById("modal-close-btn").addEventListener("click", closeModal);
  document.getElementById("modal-cancel-btn").addEventListener("click", closeModal);

  // Overlay click dismisses; clicks inside the dialog do not bubble to it.
  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) closeModal();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !overlay.hidden) closeModal();
  });

  form.addEventListener("submit", handleSubmit);
}

export function openCreateModal() {
  form.reset();
  editingTask = null;
  fields.taskId.value = "";
  fields.status.value = "ToDo";
  fields.priority.value = "Medium";
  clearErrors();
  modalTitle.textContent = "New Task";
  overlay.hidden = false;
  fields.title.focus();
}

export function openEditModal(task) {
  form.reset();
  editingTask = task;
  fields.taskId.value = String(task.id);
  fields.title.value = task.title;
  fields.description.value = task.description ?? "";
  fields.status.value = task.status;
  fields.priority.value = task.priority;
  fields.assignee.value = task.assignee ?? "";
  clearErrors();
  modalTitle.textContent = `Edit Task #${task.id}`;
  overlay.hidden = false;
  fields.title.focus();
}

function closeModal() {
  overlay.hidden = true;
  editingTask = null;
  form.reset();
  clearErrors();
}

function clearErrors() {
  titleError.hidden = true;
  serverError.hidden = true;
}

function readPayload() {
  return {
    title: fields.title.value.trim(),
    description: fields.description.value,
    status: fields.status.value,
    priority: fields.priority.value,
    // Backend treats assignee as optional: send null instead of "".
    assignee: fields.assignee.value.trim() || null,
  };
}

async function handleSubmit(event) {
  event.preventDefault();
  clearErrors();

  const payload = readPayload();

  // Client-side rule: never send a request with an empty (post-trim) title.
  if (!payload.title) {
    titleError.textContent = "Title is required and cannot be only whitespace.";
    titleError.hidden = false;
    return;
  }

  try {
    if (editingTask) {
      // PATCH is a partial update: send only what changed. Re-sending the
      // current status would be rejected as a same-status transition.
      const changes = {};
      for (const [key, value] of Object.entries(payload)) {
        if (value !== (editingTask[key] ?? null)) changes[key] = value;
      }
      if (Object.keys(changes).length === 0) {
        closeModal();
        return;
      }
      await updateTask(editingTask.id, changes);
    } else {
      await createTask(payload);
    }
  } catch (error) {
    // Server rejected the save (e.g. 422 invalid transition): stay open,
    // show the server's message, and do not pretend the save succeeded.
    serverError.textContent =
      error instanceof ApiError
        ? detailToMessage(error.detail)
        : "Save failed: backend unreachable.";
    serverError.hidden = false;
    return;
  }

  closeModal();
  await onSaved?.();
}
