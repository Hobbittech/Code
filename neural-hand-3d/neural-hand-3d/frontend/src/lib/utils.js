export const API_URL = (process.env.REACT_APP_BACKEND_URL || "http://localhost:8001").replace(/\/$/, "");

export async function api(path, options={}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: {"Content-Type":"application/json", ...(options.headers || {})},
    ...options
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}

export function clamp(v,min,max){ return Math.max(min,Math.min(max,v)); }
