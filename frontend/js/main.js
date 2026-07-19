// Entry point: wires the board and modal together.

import { refreshBoard, setEditHandler } from "./board.js";
import { initModal, openCreateModal, openEditModal } from "./modal.js";

initModal({ onSaved: refreshBoard });
setEditHandler(openEditModal);

document.getElementById("new-task-btn").addEventListener("click", openCreateModal);

refreshBoard();
