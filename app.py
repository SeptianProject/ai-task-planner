import itertools
import json
import os
import re

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from google import genai
from google.genai import types

load_dotenv() 

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-ganti-di-production")

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
MAX_TITLE_LENGTH = 120
MAX_GOAL_LENGTH = 200
MAX_SUBTASKS = 7

FALLBACK_STEPS = [
    "Tentukan tujuan dan hasil akhir",
    "Kumpulkan referensi atau bahan",
    "Buat versi pertama (draft)",
    "Uji dan minta masukan",
    "Perbaiki lalu selesaikan",
]

tasks = []
_id_counter = itertools.count(1)


def tambah_task(title):
    task = {"id": next(_id_counter), "title": title, "done": False}
    tasks.append(task)
    return task


def hitung_selesai(items):
    return sum(1 for t in items if t["done"])


def pesan_progres(items):
    return f"{hitung_selesai(items)}/{len(items)} task selesai"


def cari_task(task_id):
    return next((t for t in tasks if t["id"] == task_id), None)


# ---------- Fitur AI ----------
def _bersihkan_langkah(langkah):
    hasil = []
    for item in langkah:
        if not isinstance(item, str):
            continue
        teks = re.sub(r"^[\s\-•*\d.)]+", "", item).strip()[:MAX_TITLE_LENGTH]
        if teks and teks not in hasil:
            hasil.append(teks)
    return hasil[:MAX_SUBTASKS]


def _parse_langkah(teks):
    teks = (teks or "").strip()
    try:
        data = json.loads(teks)
        if isinstance(data, list):
            return _bersihkan_langkah(data)
    except json.JSONDecodeError:
        pass
    return _bersihkan_langkah(teks.splitlines())


def pecah_tugas(goal):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return FALLBACK_STEPS[:], "cadangan", "API key belum diisi."

    prompt = (
        "Kamu asisten produktivitas untuk mahasiswa. Pecah tujuan berikut "
        f"menjadi 3 sampai {MAX_SUBTASKS} subtask konkret dan berurutan, "
        "masing-masing maksimal 10 kata, dalam bahasa Indonesia. "
        "Balas HANYA berupa JSON array berisi string.\n"
        f"Tujuan: {goal}"
    )
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        langkah = _parse_langkah(response.text)
        if not langkah:
            raise ValueError("respons AI kosong atau formatnya tidak dikenali")
        return langkah, "ai", None
    except Exception as exc:  # jaringan, kuota (429), key salah (403), dll.
        app.logger.warning("Gemini gagal: %s: %s", type(exc).__name__, exc)
        return FALLBACK_STEPS[:], "cadangan", f"AI tidak bisa dipakai ({type(exc).__name__})."


# ---------- Routes ----------
@app.route("/")
def index():
    total = len(tasks)
    persen = round(hitung_selesai(tasks) / total * 100) if total else 0
    return render_template(
        "index.html",
        tasks=tasks,
        progres=pesan_progres(tasks),
        persen=persen,
        ai_aktif=bool(os.environ.get("GEMINI_API_KEY", "").strip()),
        model=MODEL,
        max_goal=MAX_GOAL_LENGTH,
        max_title=MAX_TITLE_LENGTH,
    )


@app.route("/tambah", methods=["POST"])
def tambah():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Judul task tidak boleh kosong.", "error")
    else:
        tambah_task(title[:MAX_TITLE_LENGTH])
    return redirect(url_for("index"))


@app.route("/pecah", methods=["POST"])
def pecah():
    goal = request.form.get("goal", "").strip()[:MAX_GOAL_LENGTH]
    if not goal:
        flash("Tulis dulu tujuan yang ingin dipecah.", "error")
        return redirect(url_for("index"))

    langkah, sumber, error = pecah_tugas(goal)
    for item in langkah:
        tambah_task(item)

    if sumber == "ai":
        flash(f"AI menambahkan {len(langkah)} subtask untuk: {goal}", "ok")
    else:
        flash(f"{error} Memakai {len(langkah)} langkah contoh.", "warn")
    return redirect(url_for("index"))


@app.route("/selesai/<int:task_id>", methods=["POST"])
def selesai(task_id):
    task = cari_task(task_id)
    if task:
        task["done"] = not task["done"]
    return redirect(url_for("index"))


@app.route("/hapus/<int:task_id>", methods=["POST"])
def hapus(task_id):
    task = cari_task(task_id)
    if task:
        tasks.remove(task)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
