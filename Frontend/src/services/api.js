const BASE = "http://localhost:8000";

export async function analyzeImage(file, conf = 0.25, maxDets = 100, detector = null) {
  const form = new FormData();
  form.append("file", file);

  const params = new URLSearchParams();
  params.set("conf", String(conf));
  params.set("max_dets", String(maxDets));
  if (detector) params.set("detector", detector);

  const res = await fetch(`${BASE}/api/v1/analyze?` + params.toString(), {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Analyze failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function fetchHistory(limit = 20) {
  const res = await fetch(`${BASE}/api/v1/history?limit=${limit}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
export async function deleteHistoryItem(id) {
  const res = await fetch(`${BASE}/api/v1/history/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
export async function clearHistory() {
  const res = await fetch(`${BASE}/api/v1/history`, { method: "DELETE" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
