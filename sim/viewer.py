"""sim/viewer.py — Web-based FPGA output viewer for POTASSIUM-WORKSHOP.

All device names, system groups, colours, and validation rules come from
sim/device_labels.py — the viewer itself has no hardcoded device knowledge.

Usage (inside nix-shell):
    python3 sim/viewer.py            # opens browser, serves all runs
    python3 sim/viewer.py --port 8765
    python3 sim/viewer.py --no-browser
"""

import argparse
import json
import os
import pathlib
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

WORKSPACE = os.environ.get("code", str(pathlib.Path(__file__).parent.parent))
LOGS_DIR  = pathlib.Path(WORKSPACE) / "sim-data" / "logs"

# ── HTML app ──────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>POTASSIUM sim viewer</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: monospace; background: #111; color: #ddd; display: flex; height: 100vh; overflow: hidden; }

#sidebar {
  width: 230px; min-width: 180px; background: #161616;
  border-right: 1px solid #2a2a2a; display: flex; flex-direction: column;
}
#sidebar-header { padding: 10px 12px 8px; border-bottom: 1px solid #222; }
#sidebar-header h2 { font-size: 10px; color: #555; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
#sidebar-search { width: 100%; background: #1e1e1e; border: 1px solid #2e2e2e; color: #ccc;
  padding: 4px 8px; font-size: 12px; border-radius: 3px; outline: none; }
#run-list { overflow-y: auto; flex: 1; }
.run-item {
  padding: 8px 12px; cursor: pointer; font-size: 12px; color: #999;
  border-left: 3px solid transparent; border-bottom: 1px solid #1a1a1a;
}
.run-item:hover { background: #1c1c1c; color: #eee; }
.run-item.active { border-left-color: #4af; color: #fff; background: #1c1c1c; }
.run-item .run-name { word-break: break-all; }
.run-item .run-meta { font-size: 10px; color: #555; margin-top: 2px; }
.warn-dot { color: #fa4; }

/* ── main ── */
#main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

#toolbar {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 6px 12px; background: #161616; border-bottom: 1px solid #2a2a2a; flex-shrink: 0;
}
.tab { padding: 5px 12px; cursor: pointer; font-size: 12px; color: #666;
  border-radius: 3px; border: 1px solid transparent; }
.tab:hover { color: #ccc; background: #222; }
.tab.active { color: #4af; border-color: #4af; background: #1a2530; }
.tool-sep { width: 1px; height: 20px; background: #2a2a2a; }
.tool-btn { padding: 4px 10px; cursor: pointer; font-size: 11px;
  background: #1e1e1e; border: 1px solid #2e2e2e; color: #888; border-radius: 3px; }
.tool-btn:hover { color: #eee; border-color: #444; }
.tool-btn.lit { background: #1a2530; border-color: #4af; color: #4af; }
#warn-badge { display: none; background: #fa4; color: #111; font-size: 10px; font-weight: bold;
  padding: 3px 9px; border-radius: 10px; cursor: pointer; }

/* ── checksum strip ── */
#checksum-bar {
  display: none; font-size: 10px; color: #555; padding: 3px 12px;
  background: #141414; border-bottom: 1px solid #1e1e1e; flex-shrink: 0;
  display: flex; align-items: center; gap: 8px;
}
#checksum-val { color: #3a3; font-family: monospace; cursor: pointer; }
#checksum-val:hover { color: #6f6; }

/* ── content ── */
#content { flex: 1; overflow-y: auto; padding: 12px 14px; }

#warn-panel { display: none; background: #1c1500; border: 1px solid #433;
  border-radius: 4px; padding: 10px 12px; margin-bottom: 12px; }
#warn-panel h3 { font-size: 10px; color: #fa4; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 1px; }
.warn-row { font-size: 11px; color: #fa4; padding: 2px 0; }
.warn-row .dim { color: #555; }

.group-header { font-size: 10px; color: #444; text-transform: uppercase; letter-spacing: 1px;
  padding: 14px 0 4px; border-bottom: 1px solid #1e1e1e; margin-bottom: 8px; }
.chart-wrap { margin-bottom: 10px; }
.chart-title { font-size: 11px; color: #666; margin-bottom: 3px; }
.chart { background: #181818; border-radius: 3px; }
.empty { color: #444; font-size: 13px; padding: 40px; text-align: center; }

#status { font-size: 11px; color: #555; padding: 4px 12px; border-top: 1px solid #1a1a1a; flex-shrink: 0; }
</style>
</head>
<body>

<div id="sidebar">
  <div id="sidebar-header">
    <h2>Runs</h2>
    <input id="sidebar-search" type="text" placeholder="filter runs…" oninput="filterRuns(this.value)">
  </div>
  <div id="run-list"><div class="empty">loading…</div></div>
</div>

<div id="main">
  <div id="toolbar">
    <div class="tab active" data-tab="ttl">TTL</div>
    <div class="tab" data-tab="dds">DDS</div>
    <div class="tab" data-tab="dac">DAC</div>
    <div class="tool-sep"></div>
    <button class="tool-btn" onclick="zoomToPulse()">Zoom → Pulse</button>
    <button class="tool-btn" id="btn-reset" onclick="zoomReset()">Reset Zoom</button>
    <div class="tool-sep"></div>
    <div id="warn-badge" onclick="toggleWarnPanel()">⚠ <span id="warn-count">0</span> warnings</div>
  </div>

  <div id="checksum-bar">
    <span style="color:#444">SHA-256</span>
    <span id="checksum-val" title="click to copy" onclick="copyChecksum()">—</span>
    <span style="color:#333" id="checksum-copy-msg"></span>
  </div>

  <div id="content">
    <div id="warn-panel">
      <h3>DDS frequency warnings</h3>
      <div id="warn-rows"></div>
    </div>
    <div id="charts"><div class="empty">Select a run from the sidebar.</div></div>
  </div>
  <div id="status">—</div>
</div>

<script>
const CFG = {responsive: true, displayModeBar: 'hover',
  modeBarButtonsToRemove: ['toImage','sendDataToCloud','lasso2d','select2d','autoScale2d']};

const BASE_LAYOUT = {
  paper_bgcolor: '#181818', plot_bgcolor: '#181818',
  font: {color: '#bbb', family: 'monospace', size: 11},
  margin: {l: 56, r: 14, t: 8, b: 36},
  legend: {bgcolor: 'rgba(24,24,24,0.9)', bordercolor: '#2a2a2a', borderwidth: 1,
    font: {size: 10}, orientation: 'v', x: 1.01, xanchor: 'left', y: 1},
  xaxis: {gridcolor: '#222', zerolinecolor: '#2a2a2a'},
  yaxis: {gridcolor: '#222', zerolinecolor: '#2a2a2a'},
};

// State
let currentData   = null;
let currentTab    = 'ttl';
let labels        = {ttl: {}, dds: {}, ttl_system_order: [], dds_system_order: [],
                     ttl_system_colors: {}, dds_system_colors: {}};
let warnings      = [];
let allDivIds     = [];
let zoomedRange   = null;
let allRuns       = [];
let currentHash   = null;

// ── boot ──────────────────────────────────────────────────────────────────────
async function boot() {
  const [runsRes, labelsRes] = await Promise.all([fetch('/api/runs'), fetch('/api/labels')]);
  allRuns = await runsRes.json();
  labels  = await labelsRes.json();
  renderRunList(allRuns);
  if (allRuns.length) {
    const first = document.querySelector('.run-item');
    if (first) first.click();
  }
}

// ── sidebar ───────────────────────────────────────────────────────────────────
function renderRunList(runs) {
  const el = document.getElementById('run-list');
  if (!runs.length) { el.innerHTML = '<div class="empty">No runs yet.</div>'; return; }
  el.innerHTML = runs.map(r =>
    `<div class="run-item" data-name="${r.name}" onclick="selectRun('${r.name}',this)">
      <div class="run-name">${r.name}${r.warnings > 0 ? ` <span class="warn-dot">⚠${r.warnings}</span>` : ''}</div>
      <div class="run-meta">${r.events} events</div>
    </div>`
  ).join('');
}

function filterRuns(q) {
  const lower = q.toLowerCase();
  renderRunList(allRuns.filter(r => r.name.toLowerCase().includes(lower)));
}

async function selectRun(name, el) {
  document.querySelectorAll('.run-item').forEach(x => x.classList.remove('active'));
  if (el) el.classList.add('active');
  document.getElementById('status').textContent = `Loading ${name}…`;

  const [dataRes, warnRes, hashRes] = await Promise.all([
    fetch(`/api/run/${name}`),
    fetch(`/api/validate/${name}`),
    fetch(`/api/checksum/${name}`),
  ]);
  currentData = await dataRes.json();
  warnings    = await warnRes.json();
  const hashData = await hashRes.json();
  currentHash = hashData.sha256;
  zoomedRange = null;

  renderWarnPanel(warnings);
  renderChecksum(currentHash);
  document.getElementById('status').textContent =
    `${name}  •  ${currentData.length} events` +
    (warnings.length ? `  •  ⚠ ${warnings.length} DDS warning(s)` : '');
  render();
}

// ── checksum ──────────────────────────────────────────────────────────────────
function renderChecksum(hash) {
  document.getElementById('checksum-bar').style.display = 'flex';
  document.getElementById('checksum-val').textContent = hash;
}

function copyChecksum() {
  navigator.clipboard.writeText(currentHash).then(() => {
    const msg = document.getElementById('checksum-copy-msg');
    msg.textContent = 'copied';
    setTimeout(() => { msg.textContent = ''; }, 1500);
  });
}

// ── warnings ──────────────────────────────────────────────────────────────────
function renderWarnPanel(warns) {
  const badge = document.getElementById('warn-badge');
  document.getElementById('warn-count').textContent = warns.length;
  badge.style.display = warns.length ? 'block' : 'none';
  if (!warns.length) { document.getElementById('warn-panel').style.display = 'none'; return; }
  document.getElementById('warn-rows').innerHTML = warns.map(w => {
    const range = w.valid_range ? `constraint: ${w.valid_range[0]}–${w.valid_range[1]} MHz` : '';
    const delta = w.delta_MHz != null ? ` (Δ ${w.delta_MHz > 0 ? '+' : ''}${w.delta_MHz} MHz from default)` : '';
    const who   = w.set_by ? ` <span class="dim">— constraint set by ${w.set_by}: ${w.source}</span>` : '';
    return `<div class="warn-row">
      <b>${w.name}</b> <span class="dim">(${w.device})</span>
      @ t=${(w.t_mu/1e6).toFixed(3)} ms —
      logged <b>${w.freq_MHz} MHz</b>${delta}
      <span class="dim">${range}</span>${who}
    </div>`;
  }).join('');
}

function toggleWarnPanel() {
  const p = document.getElementById('warn-panel');
  p.style.display = p.style.display === 'none' ? 'block' : 'none';
}

// ── tabs ──────────────────────────────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
  t.classList.add('active');
  currentTab = t.dataset.tab;
  render();
}));

// ── time scaling ──────────────────────────────────────────────────────────────
function timeScale(events) {
  const tMax = Math.max(...events.map(e => e.t_mu), 1);
  if (tMax >= 10e6)  return {scale: 1e-6, unit: 'ms'};
  if (tMax >= 10e3)  return {scale: 1e-3, unit: 'µs'};
  return {scale: 1.0, unit: 'ns'};
}

function stepXY(times, vals, tMax) {
  if (!times.length) return {x: [0, tMax], y: [0, 0]};
  const x = [], y = [];
  for (let i = 0; i < times.length; i++) {
    x.push(times[i]); y.push(vals[i]);
    if (i + 1 < times.length) { x.push(times[i+1]); y.push(vals[i]); }
    else { x.push(tMax); y.push(vals[i]); }
  }
  return {x, y};
}

// ── zoom ──────────────────────────────────────────────────────────────────────
function ramanDevices() {
  const ddsSet = new Set(Object.entries(labels.dds)
    .filter(([, v]) => v.system === 'Raman').map(([k]) => k));
  const ttlSet = new Set(Object.entries(labels.ttl)
    .filter(([, v]) => v.system === 'Raman').map(([k]) => k));
  return {ddsSet, ttlSet};
}

function zoomToPulse() {
  if (!currentData) return;
  const {scale} = timeScale(currentData);
  const {ddsSet, ttlSet} = ramanDevices();
  let tFirst = Infinity, tLast = -Infinity;
  for (const e of currentData) {
    const isRaman = (e.event === 'set' && ddsSet.has(e.device)) ||
                    (e.event === 'state' && e.state === 'ON' && ttlSet.has(e.device));
    if (isRaman) { tFirst = Math.min(tFirst, e.t_mu); tLast = Math.max(tLast, e.t_mu); }
  }
  if (!isFinite(tFirst)) { document.getElementById('status').textContent = 'No Raman activity found.'; return; }
  const margin = Math.max((tLast - tFirst) * 0.1, 100e3);
  zoomedRange = [(tFirst - margin) * scale, (tLast + margin) * scale];
  applyZoom(zoomedRange);
  document.getElementById('btn-reset').classList.add('lit');
}

function zoomReset() {
  zoomedRange = null;
  applyZoom(null);
  document.getElementById('btn-reset').classList.remove('lit');
}

function applyZoom(range) {
  for (const id of allDivIds) {
    const el = document.getElementById(id);
    if (!el || !el._fullLayout) continue;
    Plotly.relayout(el, range
      ? {'xaxis.range': range, 'xaxis.autorange': false}
      : {'xaxis.autorange': true});
  }
}

// ── render ────────────────────────────────────────────────────────────────────
function render() {
  if (!currentData) return;
  allDivIds = [];
  document.getElementById('charts').innerHTML = '';
  const {scale, unit} = timeScale(currentData);
  const tMax = Math.max(...currentData.map(e => e.t_mu * scale), 1);
  if      (currentTab === 'ttl') renderTTL(scale, unit, tMax);
  else if (currentTab === 'dds') renderDDS(scale, unit, tMax);
  else if (currentTab === 'dac') renderDAC(scale, unit, tMax);
  if (zoomedRange) applyZoom(zoomedRange);
}

// ── grouping helper ───────────────────────────────────────────────────────────
function groupDevices(deviceList, labelMap, systemOrder) {
  const groups = {};
  for (const dev of deviceList) {
    const info = labelMap[dev];
    const sys  = info ? info.system : 'Other';
    if (!groups[sys]) groups[sys] = [];
    groups[sys].push({dev, info: info || null});
  }
  return [
    ...systemOrder.filter(s => groups[s]),
    ...Object.keys(groups).filter(s => !systemOrder.includes(s)),
  ].map(sys => ({sys, devices: groups[sys] || []}));
}

// ── TTL ───────────────────────────────────────────────────────────────────────
function renderTTL(scale, unit, tMax) {
  const container = document.getElementById('charts');
  const evts = currentData.filter(e => e.event === 'state');
  if (!evts.length) { container.innerHTML = '<div class="empty">No TTL state events.</div>'; return; }

  const allDevs  = [...new Set(evts.map(e => e.device))];
  const grouped  = groupDevices(allDevs, labels.ttl, labels.ttl_system_order);
  const colorMap = labels.ttl_system_colors || {};

  for (const {sys, devices} of grouped) {
    if (!devices.length) continue;
    addGroupHeader(container, sys, devices.length);

    const CHUNK = 14;
    for (let ci = 0; ci < devices.length; ci += CHUNK) {
      const chunk  = devices.slice(ci, ci + CHUNK);
      const divId  = `ttl-${sys}-${ci}`;
      allDivIds.push(divId);
      const color  = colorMap[sys] || '#aaa';

      const div = makePlotDiv(divId, Math.max(140, chunk.length * 22 + 52));
      container.appendChild(div);

      const traces = chunk.map(({dev, info}, i) => {
        const de   = evts.filter(e => e.device === dev);
        const {x, y} = stepXY(de.map(e => e.t_mu * scale), de.map(e => e.state === 'ON' ? 1 : 0), tMax);
        const label  = info ? info.name : dev;
        return {
          x, y: y.map(v => v * 0.85 + i), name: label, mode: 'lines',
          line: {color, width: 1.5},
          hovertemplate: `<b>${label}</b> (${dev})<br>t=%{x:.3f} ${unit}<br>state=%{customdata}<extra></extra>`,
          customdata: y.map(v => v > 0.4 ? 'ON' : 'OFF'),
        };
      });

      Plotly.newPlot(div, traces, {
        ...BASE_LAYOUT,
        margin: {...BASE_LAYOUT.margin, l: 170},
        showlegend: false,
        xaxis: {...BASE_LAYOUT.xaxis, title: `Time (${unit})`},
        yaxis: {
          ...BASE_LAYOUT.yaxis,
          tickvals: chunk.map((_, i) => i + 0.42),
          ticktext: chunk.map(({dev, info}) => info ? info.name : dev),
          tickfont: {size: 10}, range: [-0.3, chunk.length], showgrid: false,
        },
      }, CFG);
    }
  }
}

// ── DDS ───────────────────────────────────────────────────────────────────────
function renderDDS(scale, unit, tMax) {
  const container = document.getElementById('charts');
  const setEvts   = currentData.filter(e => e.event === 'set');
  const attEvts   = currentData.filter(e => e.event === 'att');
  if (!setEvts.length && !attEvts.length) {
    container.innerHTML = '<div class="empty">No DDS events.</div>'; return;
  }

  const allDevs  = [...new Set([...setEvts, ...attEvts].map(e => e.device))];
  const grouped  = groupDevices(allDevs, labels.dds, labels.dds_system_order);

  // Warning index by device
  const warnMap = {};
  for (const w of warnings) { (warnMap[w.device] = warnMap[w.device] || []).push(w); }

  for (const {sys, devices} of grouped) {
    if (!devices.length) continue;
    addGroupHeader(container, sys, devices.length);

    for (const {dev, info} of devices) {
      const funcName   = info ? info.name : dev;
      const warnCount  = (warnMap[dev] || []).length;
      const defaultMHz = info ? info.default_freq_MHz : null;

      const divId = `dds-${dev}`;
      allDivIds.push(divId);

      // Title line
      const wrap = document.createElement('div');
      wrap.className = 'chart-wrap';
      const titleEl = document.createElement('div');
      titleEl.className = 'chart-title';
      titleEl.style.color = warnCount ? '#fa4' : '#555';
      titleEl.textContent = `${funcName} (${dev})` + (warnCount ? `  ⚠ ${warnCount}` : '');
      wrap.appendChild(titleEl);

      const div = document.createElement('div');
      div.id = divId; div.className = 'chart'; div.style.height = '240px';
      wrap.appendChild(div);
      container.appendChild(wrap);

      const de  = setEvts.filter(e => e.device === dev);
      const ade = attEvts.filter(e => e.device === dev);
      const traces = [];

      const hasFreq = de.length && de.some(e => e.freq_MHz != null);
      const hasAmp  = de.length && de.some(e => e.amp != null);
      const hasAtt  = ade.length > 0;
      const warns   = warnMap[dev] || [];

      if (hasFreq) {
        // ── Stacked layout: freq (top) + amp/att (bottom) ──
        const times = de.map(e => e.t_mu * scale);
        const {x: fx, y: fy} = stepXY(times, de.map(e => e.freq_MHz ?? null), tMax);
        traces.push({x: fx, y: fy, name: 'freq (MHz)', mode: 'lines', yaxis: 'y',
          line: {color: '#4af', width: 1.5},
          hovertemplate: `%{y:.4f} MHz  t=%{x:.3f} ${unit}<extra>freq</extra>`});

        if (defaultMHz != null) {
          traces.push({x: [0, tMax], y: [defaultMHz, defaultMHz],
            name: `default: ${defaultMHz} MHz`, mode: 'lines', yaxis: 'y',
            line: {color: '#2a4a5a', width: 1, dash: 'dot'}, hoverinfo: 'skip'});
        }
        if (hasAmp) {
          const {x, y} = stepXY(times, de.map(e => e.amp ?? null), tMax);
          traces.push({x, y, name: 'amp', mode: 'lines', yaxis: 'y2',
            line: {color: '#fa6', width: 1.5},
            hovertemplate: `%{y:.4f}  t=%{x:.3f} ${unit}<extra>amp</extra>`});
        }
        if (hasAtt) {
          const atimes = ade.map(e => e.t_mu * scale);
          const {x, y} = stepXY(atimes, ade.map(e => e.att_dB), tMax);
          traces.push({x, y, name: 'att (dB)', mode: 'lines', yaxis: 'y3',
            line: {color: '#c8f', width: 1.5, dash: 'dash'},
            hovertemplate: `%{y:.1f} dB  t=%{x:.3f} ${unit}<extra>att</extra>`});
        }
        if (warns.length) {
          traces.push({x: warns.map(w => w.t_mu * scale), y: warns.map(() => 0.95),
            name: '⚠ freq warn', mode: 'markers', yaxis: 'y2',
            marker: {color: '#fa4', size: 8, symbol: 'triangle-down'},
            hovertemplate: `%{x:.3f} ${unit}  freq=%{customdata} MHz<extra>⚠</extra>`,
            customdata: warns.map(w => w.freq_MHz)});
        }

        const shapes = warns.map(w => ({type: 'line', xref: 'x', yref: 'paper',
          x0: w.t_mu * scale, x1: w.t_mu * scale, y0: 0, y1: 1,
          line: {color: '#fa4', width: 1, dash: 'dot'}}));

        div.style.height = '240px';
        Plotly.newPlot(div, traces, {
          ...BASE_LAYOUT,
          margin: {l: 56, r: 14, t: 8, b: 36},
          yaxis:  {title: {text: 'MHz', standoff: 4}, domain: [0.42, 1.0],
            gridcolor: '#222', zerolinecolor: '#222', color: '#4af',
            titlefont: {color: '#4af'}, tickfont: {color: '#4af'}},
          yaxis2: {title: {text: 'amp', standoff: 4}, domain: [0, 0.34],
            range: [-0.05, 1.15], gridcolor: '#1e1e1e', zerolinecolor: '#222',
            color: '#fa6', titlefont: {color: '#fa6'}, tickfont: {color: '#fa6'}},
          yaxis3: {title: {text: 'att dB', standoff: 4}, overlaying: 'y2', side: 'right',
            color: '#c8f', titlefont: {color: '#c8f'}, tickfont: {color: '#c8f'}, showgrid: false},
          xaxis: {gridcolor: '#1e1e1e', anchor: 'y2', title: `Time (${unit})`, titlefont: {size: 10}},
          shapes,
          legend: {bgcolor: 'rgba(24,24,24,0.85)', bordercolor: '#2a2a2a', borderwidth: 1,
            font: {size: 9}, x: 1.01, xanchor: 'left', y: 1.0, yanchor: 'top'},
        }, CFG);

      } else {
        // ── Flat layout: only amp and/or att (no freq data) ──
        // Use a single panel — no domain stacking needed.
        if (hasAmp) {
          const times = de.map(e => e.t_mu * scale);
          const {x, y} = stepXY(times, de.map(e => e.amp ?? null), tMax);
          traces.push({x, y, name: 'amp', mode: 'lines', yaxis: 'y',
            line: {color: '#fa6', width: 1.5},
            hovertemplate: `%{y:.4f}  t=%{x:.3f} ${unit}<extra>amp</extra>`});
        }
        if (hasAtt) {
          const atimes = ade.map(e => e.t_mu * scale);
          const {x, y} = stepXY(atimes, ade.map(e => e.att_dB), tMax);
          // If amp also present, att goes on right axis; otherwise use main axis.
          const yax = hasAmp ? 'y2' : 'y';
          traces.push({x, y, name: 'att (dB)', mode: 'lines', yaxis: yax,
            line: {color: '#c8f', width: 1.5, dash: 'dash'},
            hovertemplate: `%{y:.1f} dB  t=%{x:.3f} ${unit}<extra>att</extra>`});
        }

        div.style.height = '120px';
        Plotly.newPlot(div, traces, {
          ...BASE_LAYOUT,
          margin: {l: 56, r: hasAmp && hasAtt ? 60 : 14, t: 8, b: 36},
          yaxis:  {title: {text: hasAmp ? 'amp' : 'att (dB)', standoff: 4},
            color: hasAmp ? '#fa6' : '#c8f',
            titlefont: {color: hasAmp ? '#fa6' : '#c8f'},
            tickfont:  {color: hasAmp ? '#fa6' : '#c8f'},
            gridcolor: '#1e1e1e', zerolinecolor: '#222'},
          yaxis2: hasAmp && hasAtt ? {
            title: {text: 'att (dB)', standoff: 4}, overlaying: 'y', side: 'right',
            color: '#c8f', titlefont: {color: '#c8f'}, tickfont: {color: '#c8f'}, showgrid: false,
          } : undefined,
          xaxis: {...BASE_LAYOUT.xaxis, title: `Time (${unit})`},
          legend: {bgcolor: 'rgba(24,24,24,0.85)', bordercolor: '#2a2a2a', borderwidth: 1,
            font: {size: 9}, x: 1.01, xanchor: 'left', y: 1.0, yanchor: 'top'},
        }, CFG);
      }
    }
  }
}

// ── DAC ───────────────────────────────────────────────────────────────────────
function renderDAC(scale, unit, tMax) {
  const container = document.getElementById('charts');
  const evts = currentData.filter(e => e.event === 'write');
  if (!evts.length) { container.innerHTML = '<div class="empty">No DAC write events.</div>'; return; }

  const COLORS    = ['#4af','#fa6','#8f8','#f88','#c8f','#ff8','#8cf','#fac'];
  const CH_CHUNK  = 4;   // channels per chart — change here to adjust grouping
  const devices   = [...new Set(evts.map(e => e.device))];

  devices.forEach(dev => {
    const de       = evts.filter(e => e.device === dev);
    const channels = [...new Set(de.map(e => e.channel))].sort((a,b) => a-b);

    // Split channels into groups of CH_CHUNK
    for (let ci = 0; ci < channels.length; ci += CH_CHUNK) {
      const chunk  = channels.slice(ci, ci + CH_CHUNK);
      const label  = chunk.length === 1
        ? `${dev}  ch${chunk[0]}`
        : `${dev}  ch${chunk[0]}–${chunk[chunk.length-1]}`;

      const divId = `dac-${dev}-${ci}`;
      allDivIds.push(divId);

      const wrap = document.createElement('div');
      wrap.className = 'chart-wrap';
      const titleEl = document.createElement('div');
      titleEl.className = 'chart-title';
      titleEl.textContent = label;
      const div = makePlotDiv(divId, 180);
      wrap.appendChild(titleEl); wrap.appendChild(div);
      container.appendChild(wrap);

      const traces = chunk.map((ch, i) => {
        const ce = de.filter(e => e.channel === ch);
        const {x, y} = stepXY(ce.map(e => e.t_mu * scale), ce.map(e => e.voltage), tMax);
        return {x, y, name: `ch${ch}`, mode: 'lines',
          line: {color: COLORS[i % COLORS.length], width: 1.5},
          hovertemplate: `ch${ch}=%{y:.4f} V  t=%{x:.3f} ${unit}<extra></extra>`};
      });

      Plotly.newPlot(div, traces, {
        ...BASE_LAYOUT,
        xaxis: {...BASE_LAYOUT.xaxis, title: `Time (${unit})`},
        yaxis: {...BASE_LAYOUT.yaxis, title: 'Voltage (V)'},
      }, CFG);
    }
  });
}

// ── DOM helpers ───────────────────────────────────────────────────────────────
function addGroupHeader(container, sys, count) {
  const hdr = document.createElement('div');
  hdr.className = 'group-header';
  hdr.textContent = `── ${sys}  (${count})`;
  container.appendChild(hdr);
}

function makePlotDiv(id, height) {
  const div = document.createElement('div');
  div.id = id; div.className = 'chart'; div.style.height = `${height}px`;
  return div;
}

boot();
</script>
</body>
</html>
"""

# ── Server helpers ────────────────────────────────────────────────────────────

def _load_labels_module():
    import sys as _sys
    root = str(pathlib.Path(__file__).parent.parent)
    if root not in _sys.path:
        _sys.path.insert(0, root)
    from sim.device_labels import api_labels_payload
    return api_labels_payload()


def _validate(events):
    """Check events against constraints in sim/constraints.py.

    Returns [] if DDS_CONSTRAINTS is empty (no constraints defined yet).
    Warnings do NOT affect the checksum.
    """
    import sys as _sys
    root = str(pathlib.Path(__file__).parent.parent)
    if root not in _sys.path:
        _sys.path.insert(0, root)
    from sim.constraints import DDS_CONSTRAINTS
    from sim.device_labels import DDS_LABELS
    if not DDS_CONSTRAINTS:
        return []
    result = []
    for e in events:
        if e.get("event") != "set":
            continue
        dev = e.get("device", "")
        c   = DDS_CONSTRAINTS.get(dev)
        if not c:
            continue
        freq = e.get("freq_MHz")
        if freq is None:
            continue
        lo, hi = c["valid_range_MHz"]
        if not (lo <= freq <= hi):
            info = DDS_LABELS.get(dev, {})
            default = info.get("default_freq_MHz")
            result.append({
                "device":      dev,
                "name":        info.get("name", dev),
                "freq_MHz":    round(freq, 4),
                "valid_range": list(c["valid_range_MHz"]),
                "set_by":      c.get("set_by", "?"),
                "source":      c.get("source", ""),
                "default_MHz": default,
                "delta_MHz":   round(freq - default, 4) if default is not None else None,
                "t_mu":        e.get("t_mu", 0),
            })
    return result


def _checksum(events):
    import sys as _sys
    root = str(pathlib.Path(__file__).parent.parent)
    if root not in _sys.path:
        _sys.path.insert(0, root)
    from sim.device_labels import checksum_events
    return checksum_events(events)


def _load_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def _safe_name(name):
    return name.endswith(".jsonl") and "/" not in name and "\\" not in name


# ── HTTP server ────────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, code, ctype, body):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        from urllib.parse import urlparse
        path = urlparse(self.path).path

        if path in ("/", "/index.html"):
            self._send(200, "text/html", HTML)

        elif path == "/api/labels":
            try:
                payload = _load_labels_module()
            except Exception as e:
                payload = {"error": str(e), "ttl": {}, "dds": {},
                           "ttl_system_order": [], "dds_system_order": [],
                           "ttl_system_colors": {}, "dds_system_colors": {}}
            self._send(200, "application/json", json.dumps(payload))

        elif path == "/api/runs":
            files = sorted(LOGS_DIR.glob("*.jsonl"), reverse=True)
            data = []
            for f in files:
                try:
                    events = _load_jsonl(f)
                    warns  = _validate(events)  # empty if DDS_CONSTRAINTS = {}
                    data.append({"name": f.name, "events": len(events), "warnings": len(warns)})
                except Exception:
                    data.append({"name": f.name, "events": "?", "warnings": 0})
            self._send(200, "application/json", json.dumps(data))

        elif path.startswith("/api/run/"):
            name = path[len("/api/run/"):]
            if not _safe_name(name):
                self._send(400, "text/plain", "bad filename"); return
            fp = LOGS_DIR / name
            if not fp.exists():
                self._send(404, "text/plain", "not found"); return
            self._send(200, "application/json", json.dumps(_load_jsonl(fp)))

        elif path.startswith("/api/validate/"):
            name = path[len("/api/validate/"):]
            if not _safe_name(name):
                self._send(400, "text/plain", "bad filename"); return
            fp = LOGS_DIR / name
            if not fp.exists():
                self._send(404, "text/plain", "not found"); return
            events = _load_jsonl(fp)
            self._send(200, "application/json", json.dumps(_validate(events)))

        elif path.startswith("/api/checksum/"):
            name = path[len("/api/checksum/"):]
            if not _safe_name(name):
                self._send(400, "text/plain", "bad filename"); return
            fp = LOGS_DIR / name
            if not fp.exists():
                self._send(404, "text/plain", "not found"); return
            events = _load_jsonl(fp)
            h      = _checksum(events)
            self._send(200, "application/json", json.dumps({"sha256": h, "events": len(events)}))

        else:
            self._send(404, "text/plain", "not found")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8756)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if not LOGS_DIR.exists():
        print(f"[viewer] {LOGS_DIR} not found — run an experiment first.")
        sys.exit(1)

    server = HTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"[viewer] {url}  (Ctrl-C to quit)")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[viewer] Stopped.")


if __name__ == "__main__":
    main()
