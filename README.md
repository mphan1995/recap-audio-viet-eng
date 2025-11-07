Tạo file README.md ở gốc project:

# 🎧 RECAP-MAX — Audio Analyzer & Summarizer (Vietnamese / English)

**RECAP-MAX** là ứng dụng Flask AI cho phép:
- Phân tích & tóm tắt nội dung audio (tiếng Việt / tiếng Anh)
- Denoise, chuẩn hóa âm lượng (LUFS)
- Tự động nhận diện giọng nói hoặc bài hát
- Xuất kết quả sang CSV / Excel / Word
- Giao diện hiện đại, responsive, có progress bar và trạng thái từng bước

---

## 🚀 Cài đặt nhanh

### 1️⃣ Clone project
```bash
git clone https://github.com/mphan1995/recap-audio-viet-eng.git
cd recap-audio-viet-eng

2️⃣ Tạo môi trường ảo & cài thư viện
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


⚙️ Nếu thiếu ffmpeg, cài thêm:

sudo apt install ffmpeg

3️⃣ Tạo file .env
cp .env.example .env

Chỉnh lại model / thiết bị nếu cần (ví dụ GPU CUDA):

WHISPER_MODEL=small
WHISPER_COMPUTE=int8
WHISPER_DEVICE=auto

4️⃣ Chạy ứng dụng
flask run --with-threads


Mở trình duyệt: http://127.0.0.1:5000

🧠 Cấu trúc thư mục
recap-audio-viet-eng/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── utils/
│   ├── audio/
│   │   ├── denoise.py
│   │   ├── loudness.py
│   │   ├── metrics.py
│   │   ├── pipeline.py
│   │   ├── vad.py
│   │   └── loader.py
│   └── summarize.py
├── templates/
│   ├── base.html
│   └── index.html
├── static/
│   ├── css/styles.css
│   ├── js/app.js
│   └── favicon.ico
└── storage/   # kết quả xử lý (tự tạo, không push lên GitHub)

✨ Tính năng nổi bật

🎙 Speech-to-Text: Faster-Whisper nhận dạng chính xác cao (multi-language)

🪄 Summary by GPT: Tự động tóm tắt transcript (song ngữ)

🧩 Denoise + VAD: Khử nhiễu, cắt vùng thoại chính xác

🔊 Play Segments: Nghe lại từng câu trong transcript

📦 Export CSV / Excel / Word: Định dạng đẹp, dễ chia sẻ

📈 Progress UI: Hiển thị % và trạng thái chi tiết

🎨 Modern UI: Responsive, glass style, gradient animation

🛠 Dev Notes

Flask backend xử lý audio bằng faster-whisper, noisereduce, pyloudnorm.

Frontend đơn giản bằng HTML + JS thuần.

Model và compute type có thể điều chỉnh trong .env.

💬 Liên hệ

Tác giả: MaX Phan
📧 Email: mphan1995@example.com

🔗 GitHub Repository