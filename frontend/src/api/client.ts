const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

async function request<T>(path: string): Promise<T> {
  const token = window.localStorage.getItem("dh_mdm_access_token");
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<import("../types/api").DashboardSummary>("/dashboard"),
  devices: () => request<import("../types/api").Device[]>("/devices"),
  audit: () => request<import("../types/api").AuditEntry[]>("/audit-log")
};
