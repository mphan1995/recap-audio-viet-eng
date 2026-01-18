const els = {
  dropzone: document.getElementById("dropzone"),
  fileInput: document.getElementById("audioFile"),
  pickFile: document.getElementById("pickFile"),
  fileMeta: document.getElementById("fileMeta"),
  startBtn: document.getElementById("startBtn"),
  btnClear: document.getElementById("btnClear"),
  btnDownload: document.getElementById("btnDownloadJson"),
  status: document.getElementById("status"),
  panelEmpty: document.getElementById("panelEmpty"),
  panelResult: document.getElementById("panelResult"),
  progressWrap: document.getElementById("progressWrap"),
  progressFill: document.getElementById("progressFill"),
  progressHint: document.getElementById("progressHint"),
  summary: document.getElementById("summary"),
  transcript: document.getElementById("transcript"),
  json: document.getElementById("json"),
  stats: document.getElementById("stats"),
  metrics: document.getElementById("metrics"),
  warnings: document.getElementById("warnings"),
  jobMeta: document.getElementById("jobMeta"),
  language: document.getElementById("language"),
  diarization: document.getElementById("diarization"),
  gpt: document.getElementById("gpt"),
  vadFilter: document.getElementById("vadFilter"),
  denoise: document.getElementById("denoise"),
  trimSilence: document.getElementById("trimSilence"),
  normalize: document.getElementById("normalize"),
  minSpeakers: document.getElementById("minSpeakers"),
  maxSpeakers: document.getElementById("maxSpeakers"),
  beamSize: document.getElementById("beamSize"),
};

const state = {
  lastResult: null,
};

function setStatus(type, text) {
  const badge = els.status.querySelector(".badge");
  const txt = els.status.querySelector(".status-text");
  badge.className = `badge ${type}`;
  badge.textContent = type === "good" ? "Ready" :
    type === "warn" ? "Running" :
      type === "bad" ? "Error" : "Idle";
  txt.textContent = text;
}

function toggleResultUI(show) {
  if (show) {
    els.panelEmpty.classList.add("hidden");
    els.panelResult.classList.remove("hidden");
    els.btnDownload.setAttribute("aria-disabled", "false");
    els.btnDownload.style.pointerEvents = "auto";
    els.btnDownload.style.opacity = "1";
  } else {
    els.panelResult.classList.add("hidden");
    els.panelEmpty.classList.remove("hidden");
    els.btnDownload.setAttribute("aria-disabled", "true");
    els.btnDownload.style.pointerEvents = "none";
    els.btnDownload.style.opacity = ".5";
  }
}

function resetUI() {
  els.fileInput.value = "";
  els.fileMeta.textContent = "No file selected.";
  state.lastResult = null;
  els.summary.textContent = "";
  els.transcript.innerHTML = "";
  els.json.textContent = "";
  els.stats.innerHTML = "";
  els.metrics.innerHTML = "";
  els.warnings.innerHTML = "";
  els.warnings.classList.add("hidden");
  els.jobMeta.textContent = "No job loaded.";
  toggleResultUI(false);
  els.progressWrap.classList.add("hidden");
  els.progressFill.style.width = "0%";
  setStatus("neutral", "Ready to analyze audio.");
}

function fmtTime(sec) {
  if (sec == null || Number.isNaN(sec)) return "--:--";
  const total = Math.max(0, Math.floor(sec));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (h > 0) return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function fmtNumber(value, digits = 2) {
  if (value == null || Number.isNaN(value)) return "-";
  return Number(value).toFixed(digits);
}

function fmtPercent(value) {
  if (value == null || Number.isNaN(value)) return "-";
  return `${(value * 100).toFixed(1)}%`;
}

function fmtDb(value) {
  if (value == null || Number.isNaN(value)) return "-";
  return `${value.toFixed(1)} dBFS`;
}

function escapeHtml(str) {
  return String(str || "").replace(/[&<>"']/g, (m) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[m]));
}

function bubbleHTML(seg) {
  const gender = (seg.gender || "unknown").toLowerCase();
  const pillCls = gender === "male" ? "pill male" : gender === "female" ? "pill female" : "pill";
  return `
    <div class="bubble">
      <div class="meta">
        <span class="pill">${escapeHtml(seg.speaker || "UNKNOWN")}</span>
        <span class="${pillCls}">${escapeHtml(gender)}</span>
        <span class="pill">${fmtTime(seg.start)} -> ${fmtTime(seg.end)}</span>
      </div>
      <div class="text">${escapeHtml(seg.text || "")}</div>
    </div>
  `;
}

function setActiveTab(tabName) {
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tabName);
  });
  document.querySelectorAll(".tabview").forEach((view) => view.classList.add("hidden"));
  const target = document.getElementById(`view-${tabName}`);
  if (target) target.classList.remove("hidden");
}

function renderStats(result) {
  const metrics = result.audio_metrics || {};
  const language = result.language || {};
  const runtime = result.runtime || {};
  const diarizationDevice = runtime.diarization_device ? runtime.diarization_device : "disabled";

  const stats = [
    { label: "Job ID", value: result.job_id || "-" },
    { label: "Duration", value: fmtTime(metrics.duration_sec) },
    { label: "Detected language", value: language.detected || language.requested || "-" },
    { label: "ASR device", value: `${runtime.asr_device || "-"} (${runtime.asr_compute_type || "-"})` },
    { label: "Diarization", value: diarizationDevice },
  ];

  els.stats.innerHTML = stats.map((item) => `
    <div class="stat">
      <div class="stat-label">${escapeHtml(item.label)}</div>
      <div class="stat-value">${escapeHtml(item.value)}</div>
    </div>
  `).join("");
}

function renderMetrics(result) {
  const metrics = result.audio_metrics || {};
  const timings = result.timings || {};
  const runtime = result.runtime || {};

  els.metrics.innerHTML = `
    <div class="metric-group">
      <h3>Audio quality</h3>
      <div class="metric-list">
        ${metric("Duration", fmtTime(metrics.duration_sec))}
        ${metric("Mean RMS", fmtDb(metrics.mean_rms_dbfs))}
        ${metric("Peak", fmtDb(metrics.peak_dbfs))}
        ${metric("Silence ratio", fmtPercent(metrics.silence_ratio))}
        ${metric("Clip ratio", fmtPercent(metrics.clip_ratio))}
        ${metric("Spectral flatness", fmtNumber(metrics.spectral_flatness_mean, 3))}
        ${metric("Zero-crossing rate", fmtNumber(metrics.zcr_mean, 3))}
      </div>
    </div>
    <div class="metric-group">
      <h3>Pipeline timings</h3>
      <div class="metric-list">
        ${metric("Preprocess", `${fmtNumber(timings.preprocess_sec, 2)} s`)}
        ${metric("ASR", `${fmtNumber(timings.asr_sec, 2)} s`)}
        ${metric("Diarization", timings.diarization_sec ? `${fmtNumber(timings.diarization_sec, 2)} s` : "disabled")}
        ${metric("Merge", `${fmtNumber(timings.merge_sec, 2)} s`)}
        ${metric("Gender", `${fmtNumber(timings.gender_sec, 2)} s`)}
      </div>
    </div>
    <div class="metric-group">
      <h3>Runtime</h3>
      <div class="metric-list">
        ${metric("ASR device", runtime.asr_device || "-")}
        ${metric("Compute type", runtime.asr_compute_type || "-")}
        ${metric("Diarization device", runtime.diarization_device || "disabled")}
      </div>
    </div>
  `;
}

function renderWarnings(result) {
  const metrics = result.audio_metrics || {};
  const warnings = [];

  if (metrics.silence_ratio != null && metrics.silence_ratio > 0.5) {
    warnings.push("High silence ratio detected. Consider trimming silence or enabling VAD.");
  }
  if (metrics.clip_ratio != null && metrics.clip_ratio > 0.01) {
    warnings.push("Potential clipping detected. Check input gain or enable normalization.");
  }
  if (metrics.mean_rms_dbfs != null && metrics.mean_rms_dbfs < -35) {
    warnings.push("Low average signal level. Consider noise reduction or re-recording.");
  }

  if (Array.isArray(result.warnings)) {
    result.warnings.forEach((warning) => warnings.push(String(warning)));
  }

  if (warnings.length === 0) {
    els.warnings.classList.add("hidden");
    els.warnings.innerHTML = "";
    return;
  }

  els.warnings.innerHTML = `
    <strong>Quality warnings</strong><br />
    ${warnings.map((w) => `- ${escapeHtml(w)}`).join("<br />")}
  `;
  els.warnings.classList.remove("hidden");
}

function metric(label, value) {
  return `
    <div class="metric">
      <div class="label">${escapeHtml(label)}</div>
      <div class="value">${escapeHtml(value)}</div>
    </div>
  `;
}

function showResult(result) {
  els.jobMeta.textContent = result.job_id ? `Job ${result.job_id}` : "Job complete";
  els.summary.textContent = result.recap || "(No summary generated)";
  els.transcript.innerHTML = (result.segments || []).map(bubbleHTML).join("");
  els.json.textContent = JSON.stringify(result, null, 2);
  renderStats(result);
  renderMetrics(result);
  renderWarnings(result);
  toggleResultUI(true);
  setActiveTab("summary");
}

function fakeProgressStart() {
  els.progressWrap.classList.remove("hidden");
  let p = 0;
  const steps = [
    "Preprocess audio...",
    "Noise reduction / trim...",
    "ASR transcription...",
    "Speaker diarization...",
    "Merge segments...",
    "Quality checks...",
    "Summary generation...",
    "Finalizing output...",
  ];
  let i = 0;
  els.progressHint.textContent = steps[i];

  const timer = setInterval(() => {
    p += Math.random() * 7 + 3;
    if (p > 92) p = 92;
    els.progressFill.style.width = `${p.toFixed(0)}%`;
    if (p > (i + 1) * (92 / steps.length) && i < steps.length - 1) {
      i += 1;
      els.progressHint.textContent = steps[i];
    }
  }, 420);

  return () => clearInterval(timer);
}

function parseOptionalInt(value) {
  if (!value) return null;
  const num = Number(value);
  if (Number.isNaN(num)) return null;
  return Math.floor(num);
}

function collectFormData(file) {
  const form = new FormData();
  form.append("file", file);
  form.append("language", els.language.value);
  form.append("diarization", String(els.diarization.checked));
  form.append("gpt", String(els.gpt.checked));
  form.append("vad_filter", String(els.vadFilter.checked));
  form.append("denoise", String(els.denoise.checked));
  form.append("trim_silence", String(els.trimSilence.checked));
  form.append("normalize", String(els.normalize.checked));

  const minSpeakers = parseOptionalInt(els.minSpeakers.value);
  const maxSpeakers = parseOptionalInt(els.maxSpeakers.value);
  const beamSize = parseOptionalInt(els.beamSize.value);

  if (minSpeakers != null) form.append("min_speakers", String(minSpeakers));
  if (maxSpeakers != null) form.append("max_speakers", String(maxSpeakers));
  if (beamSize != null) form.append("beam_size", String(beamSize));

  return form;
}

function onFilePicked() {
  const f = els.fileInput.files[0];
  if (!f) return;
  els.fileMeta.textContent = `Selected ${f.name} - ${(f.size / 1024 / 1024).toFixed(2)} MB`;
  setStatus("neutral", "File ready. Click Start Analysis to run.");
}

els.pickFile.addEventListener("click", () => els.fileInput.click());
els.dropzone.addEventListener("click", (e) => {
  if (e.target.id !== "pickFile") els.fileInput.click();
});
els.dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  els.dropzone.classList.add("dragover");
});
els.dropzone.addEventListener("dragleave", () => els.dropzone.classList.remove("dragover"));
els.dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  els.dropzone.classList.remove("dragover");
  if (e.dataTransfer.files.length) {
    els.fileInput.files = e.dataTransfer.files;
    onFilePicked();
  }
});
els.fileInput.addEventListener("change", onFilePicked);

els.btnClear.addEventListener("click", resetUI);

els.btnDownload.addEventListener("click", (e) => {
  e.preventDefault();
  if (!state.lastResult) return;
  const blob = new Blob([JSON.stringify(state.lastResult, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = state.lastResult.job_id ? `recap_${state.lastResult.job_id}.json` : "recap_result.json";
  a.click();
  URL.revokeObjectURL(url);
});

function setDiarizationControls(enabled) {
  els.minSpeakers.disabled = !enabled;
  els.maxSpeakers.disabled = !enabled;
}

els.diarization.addEventListener("change", () => {
  setDiarizationControls(els.diarization.checked);
});

document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => setActiveTab(btn.dataset.tab));
});

els.startBtn.addEventListener("click", async () => {
  const f = els.fileInput.files[0];
  if (!f) return alert("Please select an audio file first.");

  els.startBtn.disabled = true;
  setStatus("warn", "Processing audio. Please wait.");
  const stopFake = fakeProgressStart();

  try {
    const form = collectFormData(f);
    const res = await fetch("/api/recap", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Request failed");

    state.lastResult = data;
    showResult(data);

    els.progressFill.style.width = "100%";
    els.progressHint.textContent = "Done";
    setStatus("good", "Analysis complete. Review the tabs for details.");
  } catch (err) {
    setStatus("bad", `Error: ${err.message}`);
  } finally {
    stopFake();
    els.startBtn.disabled = false;
  }
});

resetUI();
setDiarizationControls(els.diarization.checked);
