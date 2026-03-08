const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5001";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(error.error || `Request failed: ${res.status}`);
  }

  return res.json();
}

export function getItems(status) {
  const params = status ? `?status=${status}` : "";
  return request(`/api/items${params}`);
}

export function getItem(id) {
  return request(`/api/items/${id}`);
}

export function createItem(data) {
  return request("/api/items", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateItem(id, data) {
  return request(`/api/items/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteItem(id) {
  return request(`/api/items/${id}`, { method: "DELETE" });
}

export function sellItem(id, soldOn) {
  return request(`/api/items/${id}/sell`, {
    method: "POST",
    body: JSON.stringify({ sold_on: soldOn }),
  });
}

export function checkEbayStatus(id) {
  return request(`/api/items/${id}/ebay-status`);
}

export function checkEmails(after) {
  return request("/api/check-emails", {
    method: "POST",
    body: JSON.stringify({ after }),
  });
}

export function getSyncLog(itemId, limit) {
  const params = new URLSearchParams();
  if (itemId) params.set("item_id", itemId);
  if (limit) params.set("limit", limit);
  return request(`/api/sync-log?${params}`);
}
