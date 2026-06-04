<<<<<<< HEAD
from flask import Flask, jsonify, request
import csv
import json
import os
import sys

app = Flask(__name__)

# Konfigurasi Path dan Import Modul Internal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import fungsi AI dari file function_v2.py
from function_v2 import load_models_on_startup, get_recommendations as ai_get_recommendations

# DATA LOADING (dijalankan sekali saat server start)

def load_categories():
    try:
        with open(os.path.join(BASE_DIR, "categories.json"), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("categories.json not found")
        return []

def load_films():
    films = []
    try:
        with open(os.path.join(BASE_DIR, "netflix_cleaned_v3.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                films.append({
                    "id": i,
                    "title": row["Title"],
                    "genre": row["Genre"],
                    "parent_genre": row["parent_genre_str"],
                    "main_parent_genre": row["main_parent_genre"],
                    "poster": row["poster"],
                    "imdb_score": row["IMDB Score"],
                    "runtime": row["Runtime"],
                    "language": row["primary_language_capitalized"],
                    "premiere": row["Premiere"],
                    "director": row["Director"],
                    "year_premiere": row["year_premiere"],
                    "plot": row["Plot"],
                })
    except FileNotFoundError:
        print("netflix_cleaned_v3.csv not found")
    return films

# Inisialisasi data statis
CATEGORIES = load_categories()
FILMS = load_films()

# Memuat model AI (TF-IDF, scaler, matriks similarity) dari artifacts/
load_models_on_startup()

# ENDPOINTS API

@app.route("/categories", methods=["GET"])
def get_categories():
    return jsonify({"status": "success", "data": CATEGORIES}), 200

@app.route("/directors", methods=["GET"])
def get_directors():
    search = request.args.get("search", "").strip().lower()
    seen = set()
    directors = []
    for film in FILMS:
        name = (film.get("director") or "").strip()
        if not name:
            continue
        key = name.lower()
        if key not in seen:
            seen.add(key)
            directors.append(name)
    if search:
        directors = [d for d in directors if search in d.lower()]
    directors.sort()
    return jsonify({"status": "success", "total": len(directors), "data": directors}), 200

@app.route("/recommendations", methods=["GET"])
def get_recommendations():
    # --- Validasi genre (wajib) ---
    categories = request.args.getlist("category")
    if not categories:
        return jsonify({"status": "error", "message": "Parameter 'category' required"}), 400

    valid_names = {c["name"].lower() for c in CATEGORIES}
    invalid = [c for c in categories if c.lower() not in valid_names]
    if invalid:
        return jsonify({"status": "error", "message": f"Unknown category: {invalid}"}), 400

    # --- Parameter opsional ---
    director_input = request.args.get("director", "").strip() or None
    year_input = None
    raw_year = request.args.get("year", "").strip()
    if raw_year:
        try:
            year_input = int(raw_year)
        except ValueError:
            return jsonify({"status": "error", "message": "Year must be integer"}), 400

    # --- Panggil fungsi AI (cosine similarity + TF-IDF) ---
    result = ai_get_recommendations(
        selected_genres=categories,
        director_input=director_input,
        year_input=year_input,
        num_recommendations=10
    )

    if not result["success"]:
        return jsonify({"status": "error", "message": result["message"]}), 500

    # --- Enrich response dengan ID dari dataset CSV ---
    title_to_id = {f["title"].lower(): f["id"] for f in FILMS}
    cleaned_data = []
    for film in result["data"]:
        film_id = title_to_id.get(film["Title"].lower())
        cleaned_data.append({
            "id": film_id,
            "title": film["Title"],
            "parent_genre": film["main_parent_genre"],
            "imdb_score": film["IMDB Score"],
            "runtime": film["Runtime"],
            "poster": film["poster"],
            "primary_language": film["primary_language_capitalized"],
            "premiere": film["Premiere"],
            "director": film["Director"],
            "year_premiere": film["year_premiere"],
            "plot": film["Plot"],
            "similarity_score": film["similarity_score"],
        })

    return jsonify({
        "status": "success",
        "filter": {"categories": categories, "director": director_input, "year": year_input},
        "total": result["total"],
        "data": cleaned_data
    }), 200

@app.route("/films/<int:film_id>", methods=["GET"])
def get_film_detail(film_id):
    film = next((f for f in FILMS if f["id"] == film_id), None)
    if not film:
        return jsonify({"status": "error", "message": "Film not found"}), 404
    return jsonify({
        "status": "success",
        "data": {
            "id": film["id"],
            "title": film["title"],
            "genre": film["genre"],
            "parent_genre": film["parent_genre"],
            "main_parent_genre": film["main_parent_genre"],
            "poster": film["poster"],
            "imdb_score": film["imdb_score"],
            "runtime": film["runtime"],
            "primary_language": film["language"],
            "premiere": film["premiere"],
            "director": film["director"],
            "year_premiere": film["year_premiere"],
            "plot": film["plot"],
        }
    }), 200

# Run Server 
if __name__ == "__main__":
=======
from flask import Flask, jsonify, request
import csv
import json
import os
import sys

app = Flask(__name__)

# Konfigurasi Path dan Import Modul Internal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import fungsi AI dari file function_v2.py
from function_v2 import load_models_on_startup, get_recommendations as ai_get_recommendations

# DATA LOADING (dijalankan sekali saat server start)

def load_categories():
    try:
        with open(os.path.join(BASE_DIR, "categories.json"), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("categories.json not found")
        return []

def load_films():
    films = []
    try:
        with open(os.path.join(BASE_DIR, "netflix_cleaned_v3.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                films.append({
                    "id": i,
                    "title": row["Title"],
                    "genre": row["Genre"],
                    "parent_genre": row["parent_genre_str"],
                    "main_parent_genre": row["main_parent_genre"],
                    "poster": row["poster"],
                    "imdb_score": row["IMDB Score"],
                    "runtime": row["Runtime"],
                    "language": row["primary_language_capitalized"],
                    "premiere": row["Premiere"],
                    "director": row["Director"],
                    "year_premiere": row["year_premiere"],
                    "plot": row["Plot"],
                })
    except FileNotFoundError:
        print("netflix_cleaned_v3.csv not found")
    return films

# Inisialisasi data statis
CATEGORIES = load_categories()
FILMS = load_films()

# Memuat model AI (TF-IDF, scaler, matriks similarity) dari artifacts/
load_models_on_startup()

# ENDPOINTS API

@app.route("/categories", methods=["GET"])
def get_categories():
    return jsonify({"status": "success", "data": CATEGORIES}), 200

@app.route("/directors", methods=["GET"])
def get_directors():
    search = request.args.get("search", "").strip().lower()
    seen = set()
    directors = []
    for film in FILMS:
        name = (film.get("director") or "").strip()
        if not name:
            continue
        key = name.lower()
        if key not in seen:
            seen.add(key)
            directors.append(name)
    if search:
        directors = [d for d in directors if search in d.lower()]
    directors.sort()
    return jsonify({"status": "success", "total": len(directors), "data": directors}), 200

@app.route("/recommendations", methods=["GET"])
def get_recommendations():
    # --- Validasi genre (wajib) ---
    categories = request.args.getlist("category")
    if not categories:
        return jsonify({"status": "error", "message": "Parameter 'category' required"}), 400

    valid_names = {c["name"].lower() for c in CATEGORIES}
    invalid = [c for c in categories if c.lower() not in valid_names]
    if invalid:
        return jsonify({"status": "error", "message": f"Unknown category: {invalid}"}), 400

    # --- Parameter opsional ---
    director_input = request.args.get("director", "").strip() or None
    year_input = None
    raw_year = request.args.get("year", "").strip()
    if raw_year:
        try:
            year_input = int(raw_year)
        except ValueError:
            return jsonify({"status": "error", "message": "Year must be integer"}), 400

    # --- Panggil fungsi AI (cosine similarity + TF-IDF) ---
    result = ai_get_recommendations(
        selected_genres=categories,
        director_input=director_input,
        year_input=year_input,
        num_recommendations=10
    )

    if not result["success"]:
        return jsonify({"status": "error", "message": result["message"]}), 500

    # --- Enrich response dengan ID dari dataset CSV ---
    title_to_id = {f["title"].lower(): f["id"] for f in FILMS}
    cleaned_data = []
    for film in result["data"]:
        film_id = title_to_id.get(film["Title"].lower())
        cleaned_data.append({
            "id": film_id,
            "title": film["Title"],
            "parent_genre": film["main_parent_genre"],
            "imdb_score": film["IMDB Score"],
            "runtime": film["Runtime"],
            "poster": film["poster"],
            "primary_language": film["primary_language_capitalized"],
            "premiere": film["Premiere"],
            "director": film["Director"],
            "year_premiere": film["year_premiere"],
            "plot": film["Plot"],
            "similarity_score": film["similarity_score"],
        })

    return jsonify({
        "status": "success",
        "filter": {"categories": categories, "director": director_input, "year": year_input},
        "total": result["total"],
        "data": cleaned_data
    }), 200

@app.route("/films/<int:film_id>", methods=["GET"])
def get_film_detail(film_id):
    film = next((f for f in FILMS if f["id"] == film_id), None)
    if not film:
        return jsonify({"status": "error", "message": "Film not found"}), 404
    return jsonify({
        "status": "success",
        "data": {
            "id": film["id"],
            "title": film["title"],
            "genre": film["genre"],
            "parent_genre": film["parent_genre"],
            "main_parent_genre": film["main_parent_genre"],
            "poster": film["poster"],
            "imdb_score": film["imdb_score"],
            "runtime": film["runtime"],
            "primary_language": film["language"],
            "premiere": film["premiere"],
            "director": film["director"],
            "year_premiere": film["year_premiere"],
            "plot": film["plot"],
        }
    }), 200

# Run Server 
if __name__ == "__main__":
>>>>>>> 4f81ee2 (Api New)
    app.run(debug=True, port=5000)