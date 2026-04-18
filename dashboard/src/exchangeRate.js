import { writable } from 'svelte/store';

export const eurRate = writable(null);

export async function fetchEurRate() {
  try {
    const r = await fetch('/api/exchange-rate');
    if (!r.ok) return;
    const data = await r.json();
    eurRate.set(data.eur ?? null);
  } catch {
    eurRate.set(null);
  }
}
