from flask import Flask, jsonify, request
import csv
import json
import os
import sys

# INISIALISASI APLIKASI & PATH
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import fungsi AI dari function_v2.py
from function_v2 import load_models_on_startup, get_recommendations as ai_get_recommendations

# DATA LOADING — Dijalankan SEKALI saat server start

def load_categories() -> list:
    filepath = os.path.join(BASE_DIR, "categories.json")
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[Zynema] WARNING: {filepath} tidak ditemukan. /categories akan mengembalikan list kosong.")
        return []


def load_films() -> list:
    filepath = os.path.join(BASE_DIR, "netflix_cleaned_v3.csv")
    films = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                films.append({
                    "id"               : i,
                    "title"            : row["Title"],
                    "genre"            : row["Genre"],
                    "parent_genre"     : row["parent_genre_str"],
                    "main_parent_genre": row["main_parent_genre"],
                    "poster"           : row["poster"],
                    "imdb_score"       : row["IMDB Score"],
                    "runtime"          : row["Runtime"],
                    "language"         : row["primary_language_capitalized"],
                    "premiere"         : row["Premiere"],
                    "director"         : row["Director"],
                    "year_premiere"    : row["year_premiere"],
                    "plot"             : row["Plot"],
                })
    except FileNotFoundError:
        print(f"[Zynema] WARNING: {filepath} tidak ditemukan. Data film tidak tersedia.")
    return films


# Muat semua data statis ke memori server satu kali saat startup.
# Tidak perlu baca file lagi untuk setiap request — lebih cepat.
CATEGORIES = load_categories()
FILMS      = load_films()

# Muat model AI (TF-IDF vectorizer, scaler, feature matrix) dari file .pkl.
# Dipanggil di sini agar model siap sebelum request pertama masuk.
load_models_on_startup()

# Lookup dict title -> id untuk mempercepat pencarian ID film di /recommendations.
# Dibuat sekali agar tidak perlu loop FILMS setiap ada request.
TITLE_TO_ID = {film["title"].lower(): film["id"] for film in FILMS}


# ENDPOINT: GET /categories

@app.route("/categories", methods=["GET"])
def get_categories():
    return jsonify({
        "status": "success",
        "data"  : CATEGORIES,
    }), 200


# ENDPOINT: GET /directors

@app.route("/directors", methods=["GET"])
def get_directors():
    search = request.args.get("search", "").strip().lower()

    # Kumpulkan nama direktur unik, skip yang kosong/NaN
    seen      = set()
    directors = []
    for film in FILMS:
        name = (film.get("director") or "").strip()
        if not name:
            continue
        key = name.lower()
        if key not in seen:
            seen.add(key)
            directors.append(name)

    # Terapkan filter pencarian jika parameter 'search' diisi
    if search:
        directors = [d for d in directors if search in d.lower()]

    directors.sort()

    return jsonify({
        "status": "success",
        "total" : len(directors),
        "data"  : directors,
    }), 200


# ENDPOINT: GET /recommendations
@app.route("/recommendations", methods=["GET"])
def get_recommendations():

    # Validasi: category (wajib) ──────────────────────────────────────────────
    categories = request.args.getlist("category")
    if not categories:
        return jsonify({
            "status" : "error",
            "message": "Parameter 'category' wajib diisi. Contoh: /recommendations?category=action",
        }), 400

    valid_names = {c["name"].lower() for c in CATEGORIES}
    invalid_categories = [c for c in categories if c.lower() not in valid_names]
    if invalid_categories:
        return jsonify({
            "status" : "error",
            "message": f"Kategori tidak dikenal: {invalid_categories}. "
                       f"Kategori valid: {sorted(valid_names)}",
        }), 400

    # Parse: director (opsional) 
    director_input = request.args.get("director", "").strip() or None

    # Parse & validasi: year (opsional) 
    year_input = None
    raw_year   = request.args.get("year", "").strip()
    if raw_year:
        try:
            year_input = int(raw_year)
        except ValueError:
            return jsonify({
                "status" : "error",
                "message": f"Nilai 'year' tidak valid: '{raw_year}'. Harus berupa integer, contoh: ?year=2020",
            }), 400

    # Panggil fungsi AI
    result = ai_get_recommendations(
        selected_genres     = categories,
        director_input      = director_input,
        year_input          = year_input,
        num_recommendations = 10,
    )

    if not result["success"]:
        return jsonify({
            "status" : "error",
            "message": result["message"],
        }), 500

    # Format response data ────────────────────────────────────────────────────
    # Tambahkan ID film dari dataset CSV ke setiap item hasil rekomendasi.
    # Model AI hanya mengembalikan data dari df_movies (.pkl), tidak tahu ID.
    cleaned_data = []
    for film in result["data"]:
        cleaned_data.append({
            "id"              : TITLE_TO_ID.get(film["Title"].lower()),
            "title"           : film["Title"],
            "parent_genre"    : film["main_parent_genre"],
            "imdb_score"      : film["IMDB Score"],
            "runtime"         : film["Runtime"],
            "poster"          : film["poster"],
            "primary_language": film["primary_language_capitalized"],
            "premiere"        : film["Premiere"],
            "director"        : film["Director"],
            "year_premiere"   : film["year_premiere"],
            "plot"            : film["Plot"],
            "similarity_score": film["similarity_score"],
        })

    return jsonify({
        "status": "success",
        "filter": {
            "categories": categories,
            "director"  : director_input,
            "year"      : year_input,
        },
        "total" : result["total"],
        "data"  : cleaned_data,
    }), 200


# ENDPOINT: GET /films/<id>
@app.route("/films/<int:film_id>", methods=["GET"])
def get_film_detail(film_id: int):
    film = next((f for f in FILMS if f["id"] == film_id), None)

    if not film:
        return jsonify({
            "status" : "error",
            "message": f"Film dengan id {film_id} tidak ditemukan.",
        }), 404

    return jsonify({
        "status": "success",
        "data": {
            "id"               : film["id"],
            "title"            : film["title"],
            "genre"            : film["genre"],
            "parent_genre"     : film["parent_genre"],
            "main_parent_genre": film["main_parent_genre"],
            "poster"           : film["poster"],
            "imdb_score"       : film["imdb_score"],
            "runtime"          : film["runtime"],
            "primary_language" : film["language"],
            "premiere"         : film["premiere"],
            "director"         : film["director"],
            "year_premiere"    : film["year_premiere"],
            "plot"             : film["plot"],
        },
    }), 200


# RUN SERVER
if __name__ == "__main__":
    # debug=True  -> auto-reload saat ada perubahan kode (jangan pakai di production)
    # port=5000   -> sesuaikan jika port sudah dipakai proses lain
    app.run(debug=True, port=5000)