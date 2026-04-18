<script>
  import { onMount, onDestroy, tick } from 'svelte';
  import { writable } from 'svelte/store';
  import { fetchSummary, fetchHistory, fetchProxyStatus, startProxy, stopProxy, fetchBreakdown } from './api.js';
  import { eurRate, fetchEurRate } from './exchangeRate.js';
  import { animateValue } from './animate.js';
  import { Chart, LineElement, PointElement, LineController, CategoryScale, LinearScale, TimeScale, Filler, Tooltip, Legend } from 'chart.js';
  import 'chart.js/auto';

  // ── stores ──────────────────────────────────────────────────────────────────
  export const intervalMode = writable('hour');

  // ── state ───────────────────────────────────────────────────────────────────
  let summary = null;
  let history = [];
  let proxyStatus = 'stopped';
  let loading = true;
  let settingsOpen = false;
  let chartCanvas;
  let chart = null;
  let refreshTimer = null;

  // animated display values for global totals
  let dispInput = 0, dispOutput = 0, dispThinking = 0, dispCacheCreate = 0, dispCacheRead = 0;
  let dispCost = 0;

  // ── breakdown state ──────────────────────────────────────────────────────────
  let breakdownModel = '';
  let breakdownPeriod = 'all';
  let breakdown = null;

  const PERIODS = [
    { key: 'today', label: 'Today' },
    { key: '7d',    label: 'Last 7 days' },
    { key: '30d',   label: 'Last 30 days' },
    { key: 'all',   label: 'All time' },
  ];

  async function loadBreakdown() {
    if (!breakdownModel) return;
    breakdown = await fetchBreakdown(breakdownModel, breakdownPeriod);
  }

  $: if (breakdownModel || breakdownPeriod) loadBreakdown();

  // ── EUR store ────────────────────────────────────────────────────────────────
  let eur = null;
  eurRate.subscribe(v => { eur = v; });

  // ── interval mode ────────────────────────────────────────────────────────────
  let mode = 'hour';
  intervalMode.subscribe(v => {
    mode = v;
    if (chart && history.length) updateChart(history);
  });

  // ── data loading ─────────────────────────────────────────────────────────────
  async function loadAll() {
    const [s, h, ps] = await Promise.all([fetchSummary(), fetchHistory(500), fetchProxyStatus()]);
    summary = s;
    history = h ?? [];
    proxyStatus = ps?.status ?? 'stopped';
    animateTotals(summary?.total ?? {});
    if (!breakdownModel && s?.models?.length) breakdownModel = s.models[0].model;
    if (chart) updateChart(history);
    await loadBreakdown();
  }

  async function loadSummaryAndHistory() {
    const [s, h] = await Promise.all([fetchSummary(), fetchHistory(500)]);
    const prevTotal = summary?.total ?? {};
    summary = s;
    history = h ?? [];
    animateTotals(summary?.total ?? {}, prevTotal);
    if (chart) updateChart(history);
    await loadBreakdown();
  }

  // ── count-up animation ────────────────────────────────────────────────────────
  function animateTotals(total, prev = {}) {
    animateValue(prev.input_tokens ?? 0, total.input_tokens ?? 0, 600, v => dispInput = v);
    animateValue(prev.output_tokens ?? 0, total.output_tokens ?? 0, 600, v => dispOutput = v);
    animateValue(prev.thinking_tokens ?? 0, total.thinking_tokens ?? 0, 600, v => dispThinking = v);
    animateValue(prev.cache_creation_tokens ?? 0, total.cache_creation_tokens ?? 0, 600, v => dispCacheCreate = v);
    animateValue(prev.cache_read_tokens ?? 0, total.cache_read_tokens ?? 0, 600, v => dispCacheRead = v);
    animateValue(prev.estimated_cost ?? 0, total.estimated_cost ?? 0, 600, v => dispCost = v);
  }

  // ── proxy control ─────────────────────────────────────────────────────────────
  async function toggleProxy() {
    if (proxyStatus === 'running') {
      await stopProxy();
      proxyStatus = 'stopped';
      clearAutoRefresh();
    } else {
      await startProxy();
      proxyStatus = 'running';
      startAutoRefresh();
    }
  }

  function startAutoRefresh() {
    clearAutoRefresh();
    refreshTimer = setInterval(loadSummaryAndHistory, 10_000);
  }

  function clearAutoRefresh() {
    if (refreshTimer !== null) { clearInterval(refreshTimer); refreshTimer = null; }
  }

  // ── chart helpers ─────────────────────────────────────────────────────────────
  function groupHistory(events, groupBy) {
    const buckets = {};
    for (const ev of events) {
      const d = new Date(ev.timestamp);
      const key = groupBy === 'day'
        ? `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
        : `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:00`;
      if (!buckets[key]) buckets[key] = { input: 0, output: 0 };
      buckets[key].input += ev.input_tokens ?? 0;
      buckets[key].output += ev.output_tokens ?? 0;
    }
    const labels = Object.keys(buckets).sort();
    return {
      labels,
      input: labels.map(l => buckets[l].input),
      output: labels.map(l => buckets[l].output),
    };
  }

  function makeGradient(ctx, color) {
    const grad = ctx.createLinearGradient(0, 0, 0, 300);
    grad.addColorStop(0, color.replace(')', ', 0.15)').replace('rgb', 'rgba'));
    grad.addColorStop(1, color.replace(')', ', 0)').replace('rgb', 'rgba'));
    return grad;
  }

  function initChart(canvas) {
    const ctx = canvas.getContext('2d');
    const inputGrad = ctx.createLinearGradient(0, 0, 0, 300);
    inputGrad.addColorStop(0, 'rgba(94,106,210,0.15)');
    inputGrad.addColorStop(1, 'rgba(94,106,210,0)');
    const outputGrad = ctx.createLinearGradient(0, 0, 0, 300);
    outputGrad.addColorStop(0, 'rgba(76,175,125,0.15)');
    outputGrad.addColorStop(1, 'rgba(76,175,125,0)');

    chart = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [
        {
          label: 'Input tokens',
          data: [],
          borderColor: '#5e6ad2',
          backgroundColor: inputGrad,
          borderWidth: 1.5,
          pointRadius: 0,
          fill: true,
          tension: 0.3,
        },
        {
          label: 'Output tokens',
          data: [],
          borderColor: '#4caf7d',
          backgroundColor: outputGrad,
          borderWidth: 1.5,
          pointRadius: 0,
          fill: true,
          tension: 0.3,
        },
      ]},
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 300 },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#1a1a1a',
            borderColor: '#2a2a2a',
            borderWidth: 1,
            titleColor: '#888888',
            bodyColor: '#e0e0e0',
            cornerRadius: 6,
            padding: 10,
            displayColors: true,
          },
        },
        scales: {
          x: {
            grid: { color: '#1f1f1f', drawBorder: false },
            ticks: { color: '#555555', font: { size: 11 }, maxRotation: 0, maxTicksLimit: 8 },
          },
          y: {
            grid: { color: '#1f1f1f', drawBorder: false },
            ticks: { color: '#555555', font: { size: 11 } },
            beginAtZero: true,
          },
        },
      },
    });

    if (history.length) updateChart(history);
  }

  function updateChart(events) {
    if (!chart) return;
    const { labels, input, output } = groupHistory(events, mode);
    chart.data.labels = labels;
    chart.data.datasets[0].data = input;
    chart.data.datasets[1].data = output;
    chart.update();
  }

  // ── lifecycle ─────────────────────────────────────────────────────────────────
  onMount(async () => {
    await fetchEurRate();
    await loadAll();
    loading = false;
    if (proxyStatus === 'running') startAutoRefresh();
    await tick();
    if (chartCanvas) initChart(chartCanvas);
  });

  onDestroy(() => {
    clearAutoRefresh();
    if (chart) { chart.destroy(); chart = null; }
  });

  // ── breakdown rows ────────────────────────────────────────────────────────────
  let breakdownTotal = 0;
  let breakdownRows = [];
  $: if (breakdown) {
    breakdownTotal = (breakdown.input_tokens ?? 0) + (breakdown.output_tokens ?? 0)
      + (breakdown.thinking_tokens ?? 0) + (breakdown.cache_creation_tokens ?? 0)
      + (breakdown.cache_read_tokens ?? 0);
    breakdownRows = [
      { key: 'input',          label: 'Input',       tokens: breakdown.input_tokens,          cost: breakdown.input_cost,          color: '#5e6ad2' },
      { key: 'output',         label: 'Output',      tokens: breakdown.output_tokens,         cost: breakdown.output_cost,         color: '#4caf7d' },
      { key: 'thinking',       label: 'Thinking',    tokens: breakdown.thinking_tokens,       cost: breakdown.thinking_cost,       color: '#e5a03a', hide: breakdown.thinking_tokens === 0 },
      { key: 'cache_creation', label: 'Cache write', tokens: breakdown.cache_creation_tokens, cost: breakdown.cache_creation_cost, color: '#888888' },
      { key: 'cache_read',     label: 'Cache read',  tokens: breakdown.cache_read_tokens,     cost: breakdown.cache_read_cost,     color: '#555555' },
    ];
  }

  // ── formatting ────────────────────────────────────────────────────────────────
  function fmt(n) { return Math.round(n).toLocaleString(); }
  function fmtCost(n) { return n == null ? '—' : `$${n.toFixed(4)}`; }
  function fmtEur(usd) { return eur ? `€${(usd * eur).toFixed(4)}` : null; }
</script>

<main>
  <!-- Header -->
  <header>
    <div class="header-left">
      <span class="logo">TokenAIzer</span>
      <span class="status-dot" class:active={proxyStatus === 'running'}></span>
      <span class="status-label">{proxyStatus === 'running' ? 'Proxy active' : 'Proxy inactive'}</span>
    </div>
    <div class="header-right">
      <button
        class="power-btn"
        class:active={proxyStatus === 'running'}
        on:click={toggleProxy}
        title={proxyStatus === 'running' ? 'Stop proxy' : 'Start proxy'}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M18.36 6.64A9 9 0 1 1 5.64 6.64"/>
          <line x1="12" y1="2" x2="12" y2="12"/>
        </svg>
      </button>
      <button class="gear-btn" on:click={() => settingsOpen = !settingsOpen} title="Settings">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </button>
      {#if settingsOpen}
        <div class="settings-panel">
          <p class="settings-title">Chart interval</p>
          <div class="interval-options">
            <button
              class="interval-btn"
              class:selected={mode === 'hour'}
              on:click={() => intervalMode.set('hour')}
            >By hour</button>
            <button
              class="interval-btn"
              class:selected={mode === 'day'}
              on:click={() => intervalMode.set('day')}
            >By day</button>
          </div>
        </div>
      {/if}
    </div>
  </header>

  {#if loading}
    <div class="loading">Loading…</div>
  {:else}
    <!-- Global totals -->
    <section class="section">
      <h2 class="section-title">Usage totals</h2>
      <div class="cards-grid">
        <div class="card stagger-1">
          <span class="metric-label">Input tokens</span>
          <span class="metric-value">{fmt(dispInput)}</span>
        </div>
        <div class="card stagger-2">
          <span class="metric-label">Output tokens</span>
          <span class="metric-value">{fmt(dispOutput)}</span>
        </div>
        <div class="card stagger-3">
          <span class="metric-label">Thinking tokens</span>
          <span class="metric-value">{fmt(dispThinking)}</span>
        </div>
        <div class="card stagger-4">
          <span class="metric-label">Cache write</span>
          <span class="metric-value">{fmt(dispCacheCreate)}</span>
        </div>
        <div class="card stagger-5">
          <span class="metric-label">Cache read</span>
          <span class="metric-value">{fmt(dispCacheRead)}</span>
        </div>
        <div class="card stagger-6 cost-card">
          <span class="metric-label">Estimated cost</span>
          <span class="metric-value cost-usd">{fmtCost(dispCost)}</span>
          {#if fmtEur(dispCost)}
            <span class="cost-eur">{fmtEur(dispCost)}</span>
          {:else}
            <span class="cost-eur warning">EUR rate unavailable</span>
          {/if}
        </div>
      </div>
    </section>

    <!-- Per-model cards -->
    {#if summary?.models?.length}
      <section class="section">
        <h2 class="section-title">By model</h2>
        <div class="cards-grid">
          {#each summary.models as m, i}
            <div class="card stagger-{i + 1}">
              <span class="model-name">{m.model}</span>
              <div class="model-metrics">
                <div><span class="metric-label">Input</span><span class="metric-value sm">{(m.input_tokens ?? 0).toLocaleString()}</span></div>
                <div><span class="metric-label">Output</span><span class="metric-value sm">{(m.output_tokens ?? 0).toLocaleString()}</span></div>
                <div><span class="metric-label">Cost</span><span class="metric-value sm">{fmtCost(m.estimated_cost)}</span></div>
              </div>
            </div>
          {/each}
        </div>
      </section>
    {/if}

    <!-- Chart -->
    <section class="section">
      <h2 class="section-title">Token history</h2>
      <div class="chart-wrap">
        {#if history.length === 0}
          <div class="empty-state">No data yet — start the proxy and make some API calls.</div>
        {/if}
        <canvas bind:this={chartCanvas} class:hidden={history.length === 0}></canvas>
      </div>
      <div class="chart-legend">
        <span class="legend-dot" style="background:#5e6ad2"></span><span>Input</span>
        <span class="legend-dot" style="background:#4caf7d"></span><span>Output</span>
      </div>
    </section>
    <!-- Token breakdown -->
    <section class="section">
      <h2 class="section-title">Token breakdown</h2>
      <div class="breakdown-controls">
        <select class="model-select" bind:value={breakdownModel}>
          {#each (summary?.models ?? []) as m}
            <option value={m.model}>{m.model}</option>
          {/each}
        </select>
        <div class="period-btns">
          {#each PERIODS as p}
            <button
              class="period-btn"
              class:selected={breakdownPeriod === p.key}
              on:click={() => breakdownPeriod = p.key}
            >{p.label}</button>
          {/each}
        </div>
      </div>

      {#if breakdown}
        <div class="breakdown-table">
          {#each breakdownRows as row}
            {#if !row.hide}
              <div class="breakdown-row">
                <span class="bd-label">{row.label}</span>
                <span class="bd-tokens">{(row.tokens ?? 0).toLocaleString()}</span>
                <span class="bd-cost">{fmtCost(row.cost)}</span>
                <div class="bd-bar-track">
                  <div class="bd-bar-fill" style="width:{breakdownTotal > 0 ? ((row.tokens / breakdownTotal) * 100).toFixed(1) : 0}%; background:{row.color}"></div>
                </div>
                <span class="bd-pct">{breakdownTotal > 0 ? ((row.tokens / breakdownTotal) * 100).toFixed(1) : '0.0'}%</span>
              </div>
            {/if}
          {/each}
          <div class="breakdown-total">
            <span class="bd-label">Total cost</span>
            <span class="bd-cost-total">{fmtCost(breakdown.total_cost)}</span>
          </div>
        </div>
      {/if}
    </section>
  {/if}
</main>
