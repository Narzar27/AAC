// Entry point: wires the board, modal, and filter bar together.

import { applyFilters, refreshBoard, setEditHandler } from "./board.js";
import { initModal, openCreateModal, openEditModal } from "./modal.js";

initModal({ onSaved: refreshBoard });
setEditHandler(openEditModal);

document.getElementById("new-task-btn").addEventListener("click", openCreateModal);

// --- Filter bar ------------------------------------------------------------

const overdueToggle = document.getElementById("filter-overdue");
const tagInput = document.getElementById("filter-tag");

overdueToggle.addEventListener("change", () => applyFilters({ overdue: overdueToggle.checked }));

let tagDebounce;
tagInput.addEventListener("input", () => {
  clearTimeout(tagDebounce);
  tagDebounce = setTimeout(() => applyFilters({ tag: tagInput.value.trim() }), 250);
});

document.getElementById("filter-clear").addEventListener("click", () => {
  overdueToggle.checked = false;
  tagInput.value = "";
  applyFilters({ overdue: false, tag: "" });
});

refreshBoard();
