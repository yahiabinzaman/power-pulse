/**
 * CYBER_VOLT // HACKER POWER IDE CLIENT ENGINE
 */

// State
let isPaused = false;
let isCrtOn = true;
let refreshIntervalMs = 1000;
let pollTimer = null;
let currencySymbol = localStorage.getItem("pp_currency") || "৳";
let baseTariffRate = parseFloat(localStorage.getItem("pp_base_tariff") || "10.55"); // Motijheel DPDC standard
let includeVat = localStorage.getItem("pp_include_vat") !== "false";
let tariffRate = includeVat ? baseTariffRate * 1.05 : baseTariffRate;

// DOM Elements
const totalWattsEl = document.getElementById("totalWatts");
const totalGaugeFillEl = document.getElementById("totalGaugeFill");
const powerLoadBadgeEl = document.getElementById("powerLoadBadge");

const minWattsEl = document.getElementById("minWatts");
const avgWattsEl = document.getElementById("avgWatts");
const peakWattsEl = document.getElementById("peakWatts");
const cpuLoadValEl = document.getElementById("cpuLoadVal");

const cpuWattsEl = document.getElementById("cpuWatts");
const gpuWattsEl = document.getElementById("gpuWatts");
const baseWattsEl = document.getElementById("baseWatts");
const cpuBarFillEl = document.getElementById("cpuBarFill");
const gpuBarFillEl = document.getElementById("gpuBarFill");
const ramBarFillEl = document.getElementById("ramBarFill");

// Network DOM Elements
const netQuickStatsEl = document.getElementById("netQuickStats");
const netPingBadgeEl = document.getElementById("netPingBadge");
const netDownSpeedEl = document.getElementById("netDownSpeed");
const netUpSpeedEl = document.getElementById("netUpSpeed");
const netDownBarFillEl = document.getElementById("netDownBarFill");
const netUpBarFillEl = document.getElementById("netUpBarFill");
const netDownKbsEl = document.getElementById("netDownKbs");
const netUpKbsEl = document.getElementById("netUpKbs");
const sidePingValEl = document.getElementById("sidePingVal");
const sideDownTotalEl = document.getElementById("sideDownTotal");
const sideUpTotalEl = document.getElementById("sideUpTotal");

// Speedtest Modal Elements
const btnSpeedtest = document.getElementById("btnSpeedtest");
const speedtestModal = document.getElementById("speedtestModal");
const btnCloseSpeedtest = document.getElementById("btnCloseSpeedtest");
const btnStartSpeedtest = document.getElementById("btnStartSpeedtest");
const stDlValEl = document.getElementById("stDlVal");
const stPingValEl = document.getElementById("stPingVal");
const stStatusMsgEl = document.getElementById("stStatusMsg");
const stProgressBarEl = document.getElementById("stProgressBar");
const stSpinnerEl = document.getElementById("stSpinner");

const costPerHourEl = document.getElementById("costPerHour");
const costPerDayEl = document.getElementById("costPerDay");
const costPerMonthEl = document.getElementById("costPerMonth");
const sessionKwhEl = document.getElementById("sessionKwh");
const sessionSpentEl = document.getElementById("sessionSpent");
const sessionTimerBadgeEl = document.getElementById("sessionTimerBadge");
const carbonEmissionEl = document.getElementById("carbonEmission");

const sysChipNameEl = document.getElementById("sysChipName");
const tdpProfileLabelEl = document.getElementById("tdpProfileLabel");
const tariffTagLabelEl = document.getElementById("tariffTagLabel");

const leafSoCEl = document.getElementById("leafSoC");
const leafCoresEl = document.getElementById("leafCores");
const leafGpuEl = document.getElementById("leafGpu");
const leafRamEl = document.getElementById("leafRam");

const procTableBodyEl = document.getElementById("procTableBody");
const procSearchInputEl = document.getElementById("procSearchInput");
const terminalLogStreamEl = document.getElementById("terminalLogStream");
const matrixStreamEl = document.getElementById("matrixStream");

const btnPauseResume = document.getElementById("btnPauseResume");
const btnToggleCrt = document.getElementById("btnToggleCrt");
const btnSettings = document.getElementById("btnSettings");
const btnCloseSettings = document.getElementById("btnCloseSettings");
const btnSaveSettings = document.getElementById("btnSaveSettings");
const settingsModal = document.getElementById("settingsModal");
const currencySelect = document.getElementById("currencySelect");
const tariffRateInput = document.getElementById("tariffRateInput");
const refreshRateSelect = document.getElementById("refreshRateSelect");
const tariffUnitText = document.getElementById("tariffUnitText");
const areaPresetSelect = document.getElementById("areaPresetSelect");
const includeVatCheck = document.getElementById("includeVatCheck");
const effectiveRateHint = document.getElementById("effectiveRateHint");

// Initialize Oscilloscope Chart
const maxChartPoints = 35;
let chartLabels = [];
let chartTotalData = [];
let chartCpuData = [];
let chartGpuData = [];

const ctx = document.getElementById("powerChart").getContext("2d");

const powerChart = new Chart(ctx, {
  type: "line",
  data: {
    labels: chartLabels,
    datasets: [
      {
        label: "TOTAL_PWR (W)",
        data: chartTotalData,
        borderColor: "#00ff66",
        backgroundColor: "rgba(0, 255, 102, 0.12)",
        borderWidth: 2,
        tension: 0.2,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 4
      },
      {
        label: "CPU_CORE (W)",
        data: chartCpuData,
        borderColor: "#00f0ff",
        borderWidth: 1.5,
        tension: 0.2,
        fill: false,
        pointRadius: 0
      },
      {
        label: "GPU_ACCEL (W)",
        data: chartGpuData,
        borderColor: "#b026ff",
        borderWidth: 1.5,
        tension: 0.2,
        fill: false,
        pointRadius: 0
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: { intersect: false, mode: "index" },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#05080e",
        titleColor: "#00ff66",
        bodyColor: "#d1dced",
        borderColor: "#283e58",
        borderWidth: 1,
        padding: 8,
        displayColors: true,
        titleFont: { family: "JetBrains Mono", size: 10 },
        bodyFont: { family: "JetBrains Mono", size: 11 }
      }
    },
    scales: {
      x: {
        grid: { color: "rgba(0, 255, 102, 0.05)" },
        ticks: { color: "#3e4f66", font: { family: "JetBrains Mono", size: 9 }, maxRotation: 0 }
      },
      y: {
        min: 0,
        suggestedMax: 35,
        grid: { color: "rgba(0, 240, 255, 0.06)" },
        ticks: { color: "#3e4f66", font: { family: "JetBrains Mono", size: 9 }, callback: v => v + "W" }
      }
    }
  }
});

// Format seconds into HH:MM:SS
function formatDuration(sec) {
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  return [h, m, s].map(v => (v < 10 ? "0" + v : v)).join(":");
}

// Add Log Line to bottom terminal
let logCount = 0;
function appendTerminalLog(text, tag = "INFO", tagClass = "neon-green") {
  if (!terminalLogStreamEl) return;
  const timeStr = new Date().toLocaleTimeString([], { hour12: false });
  const div = document.createElement("div");
  div.className = "log-line";
  div.innerHTML = `<span class="log-ts">[${timeStr}]</span> <span class="${tagClass}">[${tag}]</span> ${escapeHtml(text)}`;
  terminalLogStreamEl.appendChild(div);
  logCount++;
  if (logCount > 40) {
    terminalLogStreamEl.removeChild(terminalLogStreamEl.firstChild);
  }
  terminalLogStreamEl.scrollTop = terminalLogStreamEl.scrollHeight;
}

// Matrix Stream random generator
function updateMatrixStream() {
  if (!matrixStreamEl) return;
  let bin = "";
  for (let i = 0; i < 6; i++) {
    bin += Math.floor(Math.random() * 256).toString(2).padStart(8, "0") + " ";
  }
  matrixStreamEl.textContent = bin.trim();
}

// Update UI
function updateDashboard(data) {
  if (!data || !data.power) return;

  const p = data.power;
  const totalW = p.total_watts;
  const cpuW = p.cpu_watts;
  const gpuW = p.gpu_watts;
  const baseW = p.base_watts;

  // 1. LCD Reading
  totalWattsEl.textContent = totalW.toFixed(1);
  minWattsEl.textContent = `${p.min_watts.toFixed(1)} W`;
  avgWattsEl.textContent = `${p.avg_watts.toFixed(1)} W`;
  peakWattsEl.textContent = `${p.peak_watts.toFixed(1)} W`;
  cpuLoadValEl.textContent = `${data.cpu_usage_pct.toFixed(1)}%`;

  // ASCII Gauge
  const maxW = data.hardware && data.hardware.tdp_profile ? (data.hardware.tdp_profile.cpu_max_w + data.hardware.tdp_profile.gpu_max_w + 10) : 60;
  const gaugePct = Math.min(100, Math.max(5, (totalW / maxW) * 100));
  totalGaugeFillEl.style.width = `${gaugePct}%`;

  // Status Badge
  if (totalW < 8.0) {
    powerLoadBadgeEl.className = "hud-chip";
    powerLoadBadgeEl.textContent = "ECO_IDLE // LOW";
  } else if (totalW < 22.0) {
    powerLoadBadgeEl.className = "hud-chip";
    powerLoadBadgeEl.textContent = "NORMAL_LOAD // NOMINAL";
  } else if (totalW < 40.0) {
    powerLoadBadgeEl.className = "hud-chip med";
    powerLoadBadgeEl.textContent = "MODERATE_COMPUTE";
  } else {
    powerLoadBadgeEl.className = "hud-chip high";
    powerLoadBadgeEl.textContent = "CRITICAL_POWER_DRAW";
  }

  // 2. Components Matrix
  cpuWattsEl.textContent = `${cpuW.toFixed(1)} W`;
  gpuWattsEl.textContent = `${gpuW.toFixed(1)} W`;
  baseWattsEl.textContent = `${baseW.toFixed(1)} W`;

  const cpuPct = Math.min(100, (cpuW / totalW) * 100);
  const gpuPct = Math.min(100, (gpuW / totalW) * 100);
  const basePct = Math.min(100, (baseW / totalW) * 100);

  cpuBarFillEl.style.width = `${cpuPct}%`;
  gpuBarFillEl.style.width = `${gpuPct}%`;
  ramBarFillEl.style.width = `${basePct}%`;

  // 3. Hardware Profile
  if (data.hardware) {
    const hw = data.hardware;
    sysChipNameEl.innerHTML = `<span>HOST: ${hw.os.toUpperCase()} // ${hw.cpu_brand.toUpperCase()}</span>`;
    tdpProfileLabelEl.textContent = `${hw.soc_family || hw.cpu_brand}`;

    if (leafSoCEl) leafSoCEl.textContent = `${hw.soc_family || hw.cpu_brand}.SOC`;
    if (leafCoresEl) leafCoresEl.textContent = `${hw.cpu_cores}_CORES.CPU`;
    if (leafGpuEl) leafGpuEl.textContent = `${hw.gpu_brand || "GPU_CLUSTER"}.ACCEL`;
    if (leafRamEl) leafRamEl.textContent = `${hw.ram_gb}GB_DRAM.MEM`;
  }

  // 3.5 Network Telemetry Updates
  if (data.network) {
    const net = data.network;
    const dlMbps = net.down_mbps || 0;
    const ulMbps = net.up_mbps || 0;
    const ping = net.ping_ms || 12.0;

    // Top Bar quick stats
    if (netQuickStatsEl) {
      netQuickStatsEl.textContent = `⬇ ${dlMbps > 1 ? dlMbps.toFixed(1) + 'M' : net.down_kbs + 'K'} | ⬆ ${ulMbps > 1 ? ulMbps.toFixed(1) + 'M' : net.up_kbs + 'K'}`;
    }

    // Cockpit Network Radar Card
    if (netDownSpeedEl) netDownSpeedEl.textContent = `${dlMbps.toFixed(2)} Mbps`;
    if (netUpSpeedEl) netUpSpeedEl.textContent = `${ulMbps.toFixed(2)} Mbps`;
    if (netDownKbsEl) netDownKbsEl.textContent = `${net.down_kbs} KB/s`;
    if (netUpKbsEl) netUpKbsEl.textContent = `${net.up_kbs} KB/s`;
    if (netPingBadgeEl) netPingBadgeEl.textContent = `${ping}ms PING`;

    // Dynamic bandwidth progress bars (scaling to ~100 Mbps)
    const dlPct = Math.min(100, Math.max(5, (dlMbps / 80.0) * 100));
    const ulPct = Math.min(100, Math.max(5, (ulMbps / 30.0) * 100));
    if (netDownBarFillEl) netDownBarFillEl.style.width = `${dlPct}%`;
    if (netUpBarFillEl) netUpBarFillEl.style.width = `${ulPct}%`;

    // Sidebar Network Tree stats
    if (sidePingValEl) sidePingValEl.textContent = `${ping} ms`;
    if (sideDownTotalEl) sideDownTotalEl.textContent = `${net.session_down_mb} MB`;
    if (sideUpTotalEl) sideUpTotalEl.textContent = `${net.session_up_mb} MB`;
  }

  // 4. Electricity Cost
  const kw = totalW / 1000.0;
  const costHour = kw * tariffRate;
  const costDay = costHour * 24;
  const costMonth = costDay * 30;

  costPerHourEl.textContent = `${currencySymbol} ${costHour.toFixed(4)}`;
  costPerDayEl.textContent = `${currencySymbol} ${costDay.toFixed(2)}`;
  costPerMonthEl.textContent = `${currencySymbol} ${costMonth.toFixed(2)}`;

  // Session
  if (data.session) {
    const s = data.session;
    sessionKwhEl.textContent = `${s.total_kwh.toFixed(4)} kWh`;
    const sessionCost = s.total_kwh * tariffRate;
    sessionSpentEl.textContent = `${currencySymbol} ${sessionCost.toFixed(2)}`;
    sessionTimerBadgeEl.innerHTML = `<span>UPTIME: ${formatDuration(s.duration_seconds)}</span>`;
    carbonEmissionEl.textContent = `${(s.carbon_kg * 1000).toFixed(1)} g CO2`;
  }

  // 5. Chart
  const timeLabel = new Date().toLocaleTimeString([], { hour12: false });
  chartLabels.push(timeLabel);
  chartTotalData.push(totalW);
  chartCpuData.push(cpuW);
  chartGpuData.push(gpuW);

  if (chartLabels.length > maxChartPoints) {
    chartLabels.shift();
    chartTotalData.shift();
    chartCpuData.shift();
    chartGpuData.shift();
  }

  powerChart.update("none");

  // 6. Process table
  renderProcesses(data.processes || []);

  // 7. Matrix update & Terminal log
  updateMatrixStream();
  if (Math.random() < 0.3) {
    const topProc = data.processes && data.processes.length > 0 ? data.processes[0] : null;
    const topMsg = topProc ? `| TOP: ${topProc.name} (~${topProc.watts}W)` : "";
    appendTerminalLog(`TELEMETRY: ${totalW.toFixed(1)}W (CPU:${cpuW}W GPU:${gpuW}W) ${topMsg}`, "PROBE", "neon-cyan");
  }
}

// Render Detailed Processes Table
function renderProcesses(processes) {
  const searchTerm = procSearchInputEl.value.toLowerCase().trim();
  const filtered = processes.filter(p => p.name.toLowerCase().includes(searchTerm) || (p.category && p.category.toLowerCase().includes(searchTerm)));

  if (!filtered.length) {
    procTableBodyEl.innerHTML = `<tr><td colspan="8" class="loading-td">[NO ACTIVE PROCESSES MATCHING FILTER]</td></tr>`;
    return;
  }

  let html = "";
  filtered.forEach((p) => {
    const pWatts = (p.watts || 0);
    // Hourly cost for this specific app
    const appCostHr = (pWatts / 1000.0) * tariffRate;
    const appRam = p.ram_mb ? `${Math.round(p.ram_mb)} MB` : `${p.mem.toFixed(1)}%`;
    const tagClass = p.tag_class || (pWatts >= 1.5 ? "neon-rose" : pWatts >= 0.4 ? "neon-amber" : "neon-green");
    const loadTag = p.load_tag || (pWatts >= 1.5 ? "⚡ HEAVY" : pWatts >= 0.4 ? "🟡 MED" : "🟢 ECO");
    const category = p.category || "🔧 System";

    html += `
      <tr>
        <td class="neon-purple" style="font-size:10px;">${p.pid}</td>
        <td><strong style="color:#ffffff; font-weight:600;">${escapeHtml(p.name)}</strong></td>
        <td><span class="app-cat-tag">${escapeHtml(category)}</span></td>
        <td class="neon-cyan" style="font-weight:600;">${p.cpu.toFixed(1)}%</td>
        <td><span class="app-ram-tag">${appRam}</span></td>
        <td><span class="neon-green" style="font-weight:700;">~${pWatts.toFixed(2)} W</span></td>
        <td><span class="app-cost-tag">${currencySymbol}${appCostHr.toFixed(3)}/h</span></td>
        <td><span class="app-load-pill ${tagClass}">${loadTag}</span></td>
      </tr>
    `;
  });

  procTableBodyEl.innerHTML = html;
}

function escapeHtml(str) {
  return str.replace(/[&<>'"]/g, tag => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;"
  }[tag] || tag));
}

// Fetch Telemetry
async function fetchTelemetry() {
  if (isPaused) return;
  try {
    const res = await fetch("/api/telemetry");
    if (res.ok) {
      const data = await res.json();
      updateDashboard(data);
    }
  } catch (err) {
    appendTerminalLog(`FETCH_ERR: ${err.message}`, "ERR", "neon-rose");
  }
}

// Polling
function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  fetchTelemetry();
  pollTimer = setInterval(fetchTelemetry, refreshIntervalMs);
}

// Event Listeners
btnToggleCrt.addEventListener("click", () => {
  isCrtOn = !isCrtOn;
  document.body.classList.toggle("crt-active", isCrtOn);
  btnToggleCrt.textContent = isCrtOn ? "[CRT_FX: ON]" : "[CRT_FX: OFF]";
  appendTerminalLog(`CRT Scanline Filter set to: ${isCrtOn ? "ENABLED" : "DISABLED"}`, "UI_SET", "neon-amber");
});

// Set default CRT
document.body.classList.add("crt-active");

btnPauseResume.addEventListener("click", () => {
  isPaused = !isPaused;
  btnPauseResume.textContent = isPaused ? "[RESUME_FEED]" : "[FREEZE_FEED]";
  btnPauseResume.style.color = isPaused ? "var(--neon-rose)" : "var(--neon-cyan)";
  appendTerminalLog(`Telemetry Stream ${isPaused ? "PAUSED" : "RESUMED"}`, "STATE", isPaused ? "neon-rose" : "neon-green");
  if (!isPaused) fetchTelemetry();
});

function updateEffectiveRateDisplay() {
  const base = parseFloat(tariffRateInput.value) || 0;
  const isVat = includeVatCheck.checked;
  const eff = isVat ? base * 1.05 : base;
  effectiveRateHint.textContent = `// Effective Rate ${isVat ? 'with +5% VAT' : 'without VAT'}: ${currencySelect.value} ${eff.toFixed(2)} / unit`;
}

btnSettings.addEventListener("click", () => {
  currencySelect.value = currencySymbol;
  tariffRateInput.value = baseTariffRate.toString();
  includeVatCheck.checked = includeVat;
  tariffUnitText.textContent = `${currencySymbol} / unit`;
  refreshRateSelect.value = refreshIntervalMs.toString();
  
  // Set preset selection match if exists
  let matchFound = false;
  for (let opt of areaPresetSelect.options) {
    if (Math.abs(parseFloat(opt.value) - baseTariffRate) < 0.01) {
      areaPresetSelect.value = opt.value;
      matchFound = true;
      break;
    }
  }
  if (!matchFound) areaPresetSelect.value = "custom";

  updateEffectiveRateDisplay();
  settingsModal.classList.add("active");
});

areaPresetSelect.addEventListener("change", (e) => {
  if (e.target.value !== "custom") {
    tariffRateInput.value = e.target.value;
    updateEffectiveRateDisplay();
  }
});

tariffRateInput.addEventListener("input", () => {
  let match = false;
  for (let opt of areaPresetSelect.options) {
    if (Math.abs(parseFloat(opt.value) - parseFloat(tariffRateInput.value)) < 0.01) {
      areaPresetSelect.value = opt.value;
      match = true;
      break;
    }
  }
  if (!match) areaPresetSelect.value = "custom";
  updateEffectiveRateDisplay();
});

includeVatCheck.addEventListener("change", updateEffectiveRateDisplay);

currencySelect.addEventListener("change", (e) => {
  tariffUnitText.textContent = `${e.target.value} / unit`;
  updateEffectiveRateDisplay();
});

btnCloseSettings.addEventListener("click", () => {
  settingsModal.classList.remove("active");
});

btnSaveSettings.addEventListener("click", () => {
  currencySymbol = currencySelect.value;
  baseTariffRate = parseFloat(tariffRateInput.value) || 10.55;
  includeVat = includeVatCheck.checked;
  tariffRate = includeVat ? baseTariffRate * 1.05 : baseTariffRate;
  refreshIntervalMs = parseInt(refreshRateSelect.value, 10) || 1000;

  localStorage.setItem("pp_currency", currencySymbol);
  localStorage.setItem("pp_base_tariff", baseTariffRate.toString());
  localStorage.setItem("pp_include_vat", includeVat.toString());
  localStorage.setItem("pp_tariff", tariffRate.toString());

  tariffTagLabelEl.textContent = `${currencySymbol}${tariffRate.toFixed(2)}/unit`;

  settingsModal.classList.remove("active");
  appendTerminalLog(`TARIFF_UPDATE: Rate=${currencySymbol}${baseTariffRate.toFixed(2)}/unit (+5% VAT=${includeVat ? 'YES' : 'NO'} -> ${currencySymbol}${tariffRate.toFixed(2)}/unit) [Motijheel DPDC Configured]`, "TARIFF", "neon-green");
  startPolling();
});

settingsModal.addEventListener("click", (e) => {
  if (e.target === settingsModal) settingsModal.classList.remove("active");
});

// Speedtest Benchmark Handlers
btnSpeedtest.addEventListener("click", () => {
  speedtestModal.classList.add("active");
  stStatusMsgEl.textContent = "Ready to initiate speed probe...";
  stProgressBarEl.style.width = "0%";
  stDlValEl.textContent = "-- Mbps";
  stPingValEl.textContent = "-- ms";
});

btnCloseSpeedtest.addEventListener("click", () => {
  speedtestModal.classList.remove("active");
});

speedtestModal.addEventListener("click", (e) => {
  if (e.target === speedtestModal) speedtestModal.classList.remove("active");
});

btnStartSpeedtest.addEventListener("click", async () => {
  btnStartSpeedtest.disabled = true;
  btnStartSpeedtest.textContent = "[BENCHMARKING...]";
  stStatusMsgEl.textContent = "Connecting to global high-speed test node...";
  stProgressBarEl.style.width = "25%";

  appendTerminalLog("SPEEDTEST: Initiating multi-stream ISP benchmark...", "NET_PROBE", "neon-cyan");

  try {
    stStatusMsgEl.textContent = "Sampling download stream throughput...";
    stProgressBarEl.style.width = "60%";

    const res = await fetch("/api/speedtest");
    if (res.ok) {
      const result = await res.json();
      stProgressBarEl.style.width = "100%";
      if (result.status === "OK") {
        stDlValEl.textContent = `${result.download_mbps} Mbps`;
        stPingValEl.textContent = `${result.ping_ms} ms`;
        stStatusMsgEl.textContent = `ISP Benchmark Complete in ${result.elapsed_sec}s (${(result.bytes_tested / (1024*1024)).toFixed(1)} MB transferred)`;
        appendTerminalLog(`SPEEDTEST_RESULT: DL=${result.download_mbps} Mbps | PING=${result.ping_ms} ms [COMPLETE]`, "SPEED_TEST", "neon-green");
      } else {
        stStatusMsgEl.textContent = `Benchmark completed with warning: ${result.error || "Limited connectivity"}`;
        stPingValEl.textContent = `${result.ping_ms} ms`;
      }
    }
  } catch (err) {
    stStatusMsgEl.textContent = `Test Error: ${err.message}`;
    appendTerminalLog(`SPEEDTEST_ERR: ${err.message}`, "ERR", "neon-rose");
  } finally {
    btnStartSpeedtest.disabled = false;
    btnStartSpeedtest.textContent = "[RETEST_BENCHMARK]";
  }
});

// Initialize
tariffTagLabelEl.textContent = `${currencySymbol}${tariffRate.toFixed(2)}/kWh`;
appendTerminalLog("KERNEL: Live hardware & network polling attached.", "SYS_INIT", "neon-green");
startPolling();
