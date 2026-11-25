# AI Task Planner

Mini project webinar **Python for Web Development** (Prolab Learning). To-do list berbasis Flask dengan fitur AI: tulis satu tujuan besar, AI memecahnya menjadi subtask yang langsung masuk ke daftar.

## Fitur
- Tambah, selesaikan, dan hapus task
- **Pecah jadi langkah**: tujuan besar menjadi 3-7 subtask lewat Gemini
- Progress bar dan ringkasan task selesai
- **Mode cadangan**: tanpa API key (atau jika AI error/kuota habis), app tetap jalan dengan langkah contoh

## Menjalankan di komputer

```bash
# 1. buat dan aktifkan virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. install dependensi
pip install -r requirements.txt

# 3. siapkan konfigurasi
cp .env.example .env            # Windows: copy .env.example .env
# lalu isi GEMINI_API_KEY di file .env

# 4. jalankan
flask --app app run --debug
```

Buka http://127.0.0.1:5000

## Mendapatkan API key (Google AI Studio)
1. Buka https://aistudio.google.com lalu login dengan akun Google.
2. Pilih **Get API key** lalu **Create API key**.
3. Salin key, tempel di file `.env` sebagai `GEMINI_API_KEY=...`.
4. Restart server. Badge di pojok kanan atas berubah menjadi **AI aktif**.

Aturan penting: jangan menulis API key langsung di kode dan jangan commit file `.env`. File `.gitignore` sudah mengecualikannya.

Kuota free tier berbeda per model dan bisa berubah. Lihat batas aktif akunmu di halaman rate limit AI Studio. Jika model tidak ditemukan atau kuota habis, ganti `GEMINI_MODEL` di `.env` dengan model Flash lain yang tersedia di akunmu.

## Struktur proyek
```
ai-task-planner/
├── app.py              # route + logic + fitur AI
├── requirements.txt    # daftar library
├── .env.example        # contoh konfigurasi
├── .gitignore
└── templates/
    └── index.html      # tampilan (Jinja + Tailwind CDN)
```

## Deploy (contoh: Render)
1. Push project ke GitHub (pastikan `.env` tidak ikut).
2. Buat **Web Service** baru dan hubungkan repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Tambahkan environment variable: `GEMINI_API_KEY` dan `SECRET_KEY`.

Catatan: data task disimpan di memori server, jadi hilang saat restart dan dibagi untuk semua pengunjung. Itu cukup untuk demo. Cek kebijakan free tier layanan hosting yang kamu pakai sebelum deploy.

## Tantangan
- **Basic:** app berjalan dan tambah 1 fitur buatanmu (misalnya filter selesai/belum, deadline, atau kategori).
- **Intermediate:** simpan data ke SQLite atau file JSON agar tidak hilang saat restart, dan tambah satu fitur AI lain (prioritas, estimasi waktu, atau ringkasan harian).
- **Challenge:** deploy online dengan API key di environment variable dan README yang rapi.

## Troubleshooting
| Gejala | Penyebab umum | Solusi |
|---|---|---|
| Badge "Mode cadangan" padahal key sudah diisi | `.env` salah lokasi atau server belum direstart | Pastikan `.env` sejajar `app.py`, lalu restart |
| Pesan `ClientError` / kuota | Batas request tercapai (429) | Tunggu, atau coba lagi nanti |
| Pesan `ClientError` / akses ditolak | Key salah atau project dibatasi (403) | Buat key baru di AI Studio, cek verifikasi akun |
| Model tidak ditemukan | Nama model berubah | Ubah `GEMINI_MODEL` di `.env` |
