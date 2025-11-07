const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const fileLabelText = document.getElementById('fileLabelText');

fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    const sizeMB = (file.size / 1024 / 1024).toFixed(2);
    fileLabelText.textContent = `📁 ${file.name} (${sizeMB} MB)`;
  } else {
    fileLabelText.textContent = "Chọn audio (mp3/wav/m4a...)";
  }
});

const progressBar = document.getElementById('progress');
const player = document.getElementById('player');
const results = document.getElementById('results');
const transcriptEl = document.getElementById('transcript');
const summaryEl = document.getElementById('summary');
const mdl = document.getElementById('mdl');
const dur = document.getElementById('dur');
const snr = document.getElementById('snr');
const lat = document.getElementById('lat');
const detLang = document.getElementById('detLang');
const modelSelect = document.getElementById('modelSelect');
const computeSelect = document.getElementById('computeSelect');
const summaryLang = document.getElementById('summaryLang');

const MODEL_CHOICES = ['tiny','base','small','medium','large-v2','large-v3'];

function initDefaults(){
  MODEL_CHOICES.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m; opt.textContent = m;
    modelSelect.appendChild(opt);
  });
  modelSelect.value = window.APP_DEFAULTS?.model || 'medium';
  computeSelect.value = window.APP_DEFAULTS?.compute || 'int8_float16';
  summaryLang.value = window.APP_DEFAULTS?.summaryLang || 'auto';
}
initDefaults();

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if(!file){ alert('Hãy chọn file audio'); return; }

  const url = URL.createObjectURL(file);
  player.src = url; player.classList.remove('hidden');

  const fd = new FormData(form);
  fd.set('model', modelSelect.value);
  fd.set('compute_type', computeSelect.value);
  fd.set('lang', summaryLang.value);
  fd.append('audio', file);

  // --- Progress ---
  progressBar.classList.remove('hidden');
  results.classList.add('hidden');

  const progressEl = document.getElementById('progress');
  const progressFill = progressEl.querySelector('.progress-bar');
  const progressText = document.getElementById('progressText');
  const statusText = document.getElementById('statusText');

  let progress = 0;
  progressFill.style.width = '0%';
  progressText.textContent = '0%';
  statusText.textContent = "🔍 Bắt đầu xử lý... (ước tính 10–20 giây)";

  const steps = [
    "🎧 Tiền xử lý âm thanh (Denoise + VAD)...",
    "🧠 Nhận dạng giọng nói (Whisper đang chạy)...",
    "🪄 Tạo tóm tắt bằng GPT...",
    "📦 Hoàn tất và hiển thị kết quả..."
  ];

  let step = 0;
  const stepInterval = setInterval(() => {
    if (step < steps.length) {
      statusText.textContent = steps[step];
      step++;
    } else {
      clearInterval(stepInterval);
    }
  }, 4000);

  // --- Fake progress animation ---
  let progressInterval = setInterval(() => {
    if (progress < 95) {
      progress += 1 + Math.random() * 2;
      progressFill.style.width = `${progress}%`;
      progressText.textContent = `${Math.floor(progress)}%`;
    }
  }, 400);

  try{
    const res = await fetch('/api/transcribe', { method:'POST', body: fd });
    const data = await res.json();

    clearInterval(progressInterval);
    progress = 100;
    progressFill.style.width = '100%';
    progressText.textContent = '100%';
    setTimeout(() => progressBar.classList.add('hidden'), 800);
    clearInterval(stepInterval);

    if(!data.ok){
      statusText.textContent = "❌ Có lỗi xảy ra khi xử lý.";
      alert('Lỗi: ' + (data.error || 'unknown'));
      return;
    }

    statusText.textContent = "✅ Hoàn tất phân tích!";
    results.classList.remove('hidden');
    transcriptEl.textContent = data.transcript || '';
    summaryEl.textContent = data.summary || '';

    mdl.textContent = `Model: ${data.model} (${data.compute_type}) / ${data.device}`;
    dur.textContent = `Duration: ${data.duration ? data.duration.toFixed(2) + "s" : 'n/a'}`;
    snr.textContent = `SNR: ${data.analysis?.snr_db ?? 'n/a'} dB`;
    lat.textContent = `Processing: ${data.processing_ms} ms (pre: ${data.analysis?.processing_ms} ms)`;
    detLang.textContent = `Detected: ${data.detected_language || 'auto'}`;

    const tbody = document.querySelector('#segmentsTable tbody');
    tbody.innerHTML = '';
    (data.segments || []).forEach((s, i) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${i+1}</td>
        <td>${s.start}s</td>
        <td>${s.end}s</td>
        <td>${escapeHtml(s.text)}</td>
        <td>${s.avg_logprob ?? ''}</td>
        <td><button class="mini-play" onclick="playSegment(${s.start}, ${s.end})">▶️</button></td>
      `;
      tbody.appendChild(tr);
    });

  }catch(err){
    clearInterval(progressInterval);
    progressBar.classList.add('hidden');
    statusText.textContent = "❌ Lỗi kết nối server.";
    alert('Network error: '+ err.message);
  }
});

function playSegment(start, end) {
  const audio = document.getElementById('player');
  if (!audio.src) return alert('Chưa có file audio');
  audio.currentTime = start;
  audio.play();
  const stopAt = end || start + 5;
  const watcher = setInterval(() => {
    if (audio.currentTime >= stopAt) {
      audio.pause();
      clearInterval(watcher);
    }
  }, 200);
}

function escapeHtml(str){
  return (str || '').replace(/[&<>"']/g, (m)=>({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[m]));
}

function downloadRecap(fmt) {
  window.open(`/api/export/${fmt}`, "_blank");
}
