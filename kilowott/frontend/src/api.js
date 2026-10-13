const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function req(path, opts = {}) {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

export const api = {
  health: () => req("/health"),
  dashboard: () => req("/dashboard/summary"),
  customers: (params = {}) => {
    const q = new URLSearchParams();
    if (params.search) q.set("search", params.search);
    if (params.segment) q.set("segment", params.segment);
    q.set("limit", params.limit ?? 100);
    return req(`/customers?${q.toString()}`);
  },
  customer: (id) => req(`/customers/${id}`),
  customerOrders: (id) => req(`/customers/${id}/orders`),
  orders: (params = {}) => {
    const q = new URLSearchParams();
    if (params.status) q.set("status", params.status);
    if (params.customer_id) q.set("customer_id", params.customer_id);
    q.set("limit", params.limit ?? 100);
    return req(`/orders?${q.toString()}`);
  },
  order: (id) => req(`/orders/${id}`),
  campaigns: () => req("/calendar/campaigns"),
  recommend: (customerId, currentDate) => {
    const q = new URLSearchParams({ customer_id: customerId });
    if (currentDate) q.set("current_date", currentDate);
    return req(`/recommendations/generate?${q.toString()}`);
  },
  communications: (customerId) => req(`/communications${customerId ? `?customer_id=${customerId}` : ""}`),
  createCommunication: (payload) => req("/communications", { method: "POST", body: JSON.stringify(payload) }),
  updateCommStatus: (id, status) => req(`/communications/${id}/status?status=${status}`, { method: "PATCH" }),
  resetDemo: () => req("/sync/demo/reset", { method: "POST" }),
};
