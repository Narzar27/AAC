// API layer: the only module that talks to the backend.
// The backend owns validation and business rules; this layer just reports
// exactly what the server said.

export const API_BASE = "http://localhost:8000";

export class ApiError extends Error {
  constructor(status, detail) {
    super(typeof detail === "string" ? detail : "Request failed");
    this.status = status;
    this.detail = detail;
  }
}

// FastAPI 422 bodies carry {detail: [{loc, msg, ...}]}; HTTPException carries
// {detail: "message"}. Flatten both to one human-readable string.
export function detailToMessage(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item.loc) ? item.loc[item.loc.length - 1] : "";
        return field ? `${field}: ${item.msg}` : item.msg;
      })
      .join(" ");
  }
  return "Request failed.";
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: options.body ? { "Content-Type": "application/json" } : undefined,
    ...options,
  });

  if (!response.ok) {
    let detail = null;
    try {
      detail = (await response.json()).detail;
    } catch {
      // non-JSON error body; keep detail null
    }
    throw new ApiError(response.status, detail);
  }

  return response.status === 204 ? null : response.json();
}

export function fetchTasks(filters = {}) {
  const params = new URLSearchParams();
  if (filters.overdue) params.set("overdue", "true");
  if (filters.tag) params.set("tag", filters.tag);
  const query = params.toString();
  return request(query ? `/tasks?${query}` : "/tasks");
}

export function createTask(payload) {
  return request("/tasks", { method: "POST", body: JSON.stringify(payload) });
}

export function updateTask(taskId, payload) {
  return request(`/tasks/${taskId}`, { method: "PATCH", body: JSON.stringify(payload) });
}
