const dz = document.getElementById("dropzone");
const fileInput = document.getElementById("audioFile");
const pickFile = document.getElementById("pickFile");
const fileMeta = document.getElementById("fileMeta");

const startBtn = document.getElementById("startBtn");
const btnClear = document.getElementById("btnClear");
const btnDownload = document.getElementById("btnDownloadJson");

const statusEl = document.getElementById("status");
const panelEmpty = document.getElementById("panelEmpty");
const panelResult = document.getElementById("panelResult");

const progressWrap = document.getElementById("progressWrap");
const progressFill = document.getElementById("progressFill");
const progressHint = document.getElementById("progressHint");

const summaryEl = document.getElementById("summary");
const transcriptEl = document.getElementById("transcript");
const jsonEl = document.getElementById("json");

let lastResult = null;

function setStatus(type, text) {
  const badge = statusEl.querySelector(".badge");
  const txt = statusEl.querySelector(".status-text");
  badge.className = `badge ${type}`;
  badge.textContent = type === "good" ? "Ready" :
                      type === "warn" ? "Running" :
                      type === "bad" ? "Error" : "Idle";
  txt.textContent = text;
}

function showResultUI() {
  panelEmpty.classList.add("hidden");
  panelResult.classList.remove("hidden");
  btnDownload.setAttribute("aria-disabled", "false");
  btnDownload.style.pointerEvents = "auto";
  btnDownload.style.opacity = "1";
}

function resetUI() {
  fileInput.value = "";
  fileMeta.textContent = "Chưa có file.";
  lastResult = null;

  panelResult.classList.add("hidden");
  panelEmpty.classList.remove("hidden");

  summaryEl.textContent = "";
  transcriptEl.innerHTML = "";
  jsonEl.textContent = "";

  btnDownload.setAttribute("aria-disabled", "true");
  btnDownload.style.pointerEvents = "none";
  btnDownload.style.opacity = ".5";

  progressWrap.classList.add("hidden");
  progressFill.style.width = "0%";
  setStatus("neutral", "Sẵn sàng.");
}

function fmtTime(sec) {
  if (sec == null) return "--:--";
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
}

function bubbleHTML(seg) {
  const gender = (seg.gender || "unknown").toLowerCase();
  const pillCls = gender === "male" ? "pill male" : gender === "female" ? "pill female" : "pill";
  return `
    <div class="bubble">
      <div class="meta">
        <span class="pill">${seg.speaker || "UNKNOWN"}</span>
        <span class="${pillCls}">${gender}</span>
        <span class="pill">${fmtTime(seg.start)} → ${fmtTime(seg.end)}</span>
      </div>
      <div class="text">${escapeHtml(seg.text || "")}</div>
    </div>
  `;
}

function escapeHtml(str){
  return str.replace(/[&<>"']/g, (m) => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[m]));
}

function setActiveTab(tabName){
  document.querySelectorAll(".tab").forEach(b => {
    b.classList.toggle("active", b.dataset.tab === tabName);
  });
  document.querySelectorAll(".tabview").forEach(v => v.classList.add("hidden"));
  document.getElementById(`view-${tabName}`).classList.remove("hidden");
}

document.querySelectorAll(".tab").forEach(btn => {
  btn.addEventListener("click", () => setActiveTab(btn.dataset.tab));
});

// Drag & drop
pickFile.addEventListener("click", () => fileInput.click());
dz.addEventListener("click", (e) => {
  if (e.target.id !== "pickFile") fileInput.click();
});
dz.addEventListener("dragover", (e) => { e.preventDefault(); dz.classList.add("dragover"); });
dz.addEventListener("dragleave", () => dz.classList.remove("dragover"));
dz.addEventListener("drop", (e) => {
  e.preventDefault();
  dz.classList.remove("dragover");
  if (e.dataTransfer.files.length) {
    fileInput.files = e.dataTransfer.files;
    onFilePicked();
  }
});
fileInput.addEventListener("change", onFilePicked);

function onFilePicked(){
  const f = fileInput.files[0];
  if (!f) return;
  fileMeta.textContent = `✅ ${f.name} • ${(f.size/1024/1024).toFixed(2)} MB`;
  setStatus("neutral", "Đã chọn file. Bấm Start Recap để chạy.");
}

btnClear.addEventListener("click", resetUI);

btnDownload.addEventListener("click", (e) => {
  e.preventDefault();
  if (!lastResult) return;
  const blob = new Blob([JSON.stringify(lastResult, null, 2)], {type:"application/json"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "recap_result.json";
  a.click();
  URL.revokeObjectURL(url);
});

function fakeProgressStart(){
  progressWrap.classList.remove("hidden");
  let p = 0;
  const steps = [
    "Preprocess audio…",
    "ASR (speech-to-text)…",
    "Diarization (speakers)…",
    "Merge segments…",
    "Gender detection…",
    "GPT analysis…",
    "Finalize output…"
  ];
  let i = 0;
  progressHint.textContent = steps[i];

  const timer = setInterval(() => {
    p += Math.random() * 7 + 3;
    if (p > 92) p = 92;
    progressFill.style.width = `${p.toFixed(0)}%`;
    if (p > (i+1) * (92/steps.length) && i < steps.length-1) {
      i++;
      progressHint.textContent = steps[i];
    }
  }, 450);

  return () => { clearInterval(timer); };
}

startBtn.addEventListener("click", async () => {
  const f = fileInput.files[0];
  if (!f) return alert("Bạn chưa chọn file audio.");

  startBtn.disabled = true;
  setStatus("warn", "Đang xử lý… vui lòng chờ.");
  const stopFake = fakeProgressStart();

  const form = new FormData();
  form.append("file", f);
  form.append("language", document.getElementById("language").value);
  form.append("diarization", document.getElementById("diarization").checked);
  form.append("gpt", document.getElementById("gpt").checked);

  try{
    const res = await fetch("/api/recap", { method:"POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Request failed");

    lastResult = data;

    // Render
    summaryEl.textContent = data.recap || "(No recap)";
    transcriptEl.innerHTML = (data.segments || []).map(bubbleHTML).join("");
    jsonEl.textContent = JSON.stringify(data, null, 2);

    showResultUI();
    setActiveTab("summary");

    // finish progress
    progressFill.style.width = "100%";
    progressHint.textContent = "Done ✅";
    setStatus("good", "Hoàn tất. Bạn có thể xem kết quả hoặc tải JSON.");
  } catch(err){
    setStatus("bad", `Lỗi: ${err.message}`);
  } finally{
    stopFake();
    startBtn.disabled = false;
  }
});
resetUI();
