// Thin wrapper around the CodeFlow Compiler backend API.
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function compileSource(source) {
  const res = await fetch(`${API_BASE}/api/compile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source }),
  });
  if (!res.ok) {
    throw new Error(`Backend responded with status ${res.status}`);
  }
  return res.json();
}
