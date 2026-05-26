from flask import Flask, jsonify, request
import csv
import json
import os

app = Flask(__name__)

# Path folder project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from function import load_models_on_startup, get_recommendations as ai_get_recommendations

# Load categories.json
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
        with open(os.path.join(BASE_DIR, "netflix.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                films.append({
                    "id"          : i,
                    "title"       : row["Title"],
                    "genre"       : row["Genre"],
                    "parent_genre": row["parent_genre_str"],
                    "poster"      : row["poster"],
                    "imdb_score"  : row["IMDB Score"],
                    "runtime"     : row["Runtime"],
                    "language"    : row["Language"],
                    "premiere"    : row["Premiere"],
                })

    except FileNotFoundError:
        print("netflix.csv not found")

    return films


# Load data sekali saat server startup
CATEGORIES = load_categories()
FILMS      = load_films()
load_models_on_startup()


@app.route("/categories", methods=["GET"])
def get_categories():
    return jsonify({
        "status": "success",
        "data"  : CATEGORIES
    }), 200


@app.route("/recommendations", methods=["GET"])
def get_recommendations():

    # Support multiple query params: ?category=action&category=romance
    categories = request.args.getlist("category")

    if not categories:
        return jsonify({
            "status" : "error",
            "message": "Query parameter 'category' is required. Example: /recommendations?category=action"
        }), 400

    # Mengambil semua category valid dari categories.json
    valid_names = {c["name"].lower() for c in CATEGORIES}

    # Mengecek category yang tidak valid
    invalid = [
        c for c in categories
        if c.lower() not in valid_names
    ]

    if invalid:
        return jsonify({
            "status" : "error",
            "message": f"Unknown category: {invalid}. Valid categories: {sorted(valid_names)}"
        }), 400

    # Memanggil AI recommendation function dari model/function.py
    result = ai_get_recommendations(
        selected_genres=categories,
        num_recommendations=10
    )

    if not result["success"]:
        return jsonify({
            "status" : "error",
            "message": result["message"]
        }), 500

    # Membersihkan dan merapikan response data dari AI
    cleaned_data = []
    
    for film in result["data"]:
        cleaned_data.append({
            "title"            : film["Title"],
            "parent_genre"     : film["parent_genre_str"],
            "imdb_score"       : film["IMDB Score"],
            "runtime"          : film["Runtime"],
            "poster"           : film["poster"],
            "primary_language" : film["primary_language"],
            "premiere"         : film["Premiere"],
            "similarity_score" : film["similarity_score"],
        })

    return jsonify({
        "status": "success",
        "filter": categories,
        "total" : result["total"],
        "data"  : cleaned_data
    }), 200


@app.route("/films/<int:film_id>", methods=["GET"])
def get_film_detail(film_id):

    film = next(
        (f for f in FILMS if f["id"] == film_id),
        None
    )

    if not film:
        return jsonify({
            "status" : "error",
            "message": f"Film with id {film_id} not found."
        }), 404

    return jsonify({
        "status": "success",
        "data": {
            "id"          : film["id"],
            "title"       : film["title"],
            "genre"       : film["genre"],
            "parent_genre": film["parent_genre"],
            "poster"      : film["poster"],
        }
    }), 200


if __name__ == "__main__":
    # debug=True -> auto reload saat code berubah
    app.run(debug=True, port=5000)