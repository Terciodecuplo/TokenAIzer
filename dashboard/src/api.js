const BASE = '/api';

export async function fetchSummary() {
  const r = await fetch(`${BASE}/usage/summary`);
  return r.json();
}

export async function fetchHistory(limit = 200) {
  const r = await fetch(`${BASE}/usage/history?limit=${limit}`);
  return r.json();
}

export async function fetchProxyStatus() {
  const r = await fetch(`${BASE}/proxy/status`);
  return r.json();
}

export async function startProxy() {
  const r = await fetch(`${BASE}/proxy/start`, { method: 'POST' });
  return r.json();
}

export async function stopProxy() {
  const r = await fetch(`${BASE}/proxy/stop`, { method: 'POST' });
  return r.json();
}
