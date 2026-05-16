from flask import Flask, jsonify, request
import csv
import json
import os

app = Flask(__name__)

# Path folder project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load categories.json
def load_categories():
    with open(os.path.join(BASE_DIR, "categories.json"), "r") as f:
        return json.load(f)


def load_films():

    films = []

    # Load netlifx.csv
    with open(os.path.join(BASE_DIR, "netflix.csv"), "r", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        # Generate id otomatis mulai dari 1
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

    return films


# Load data sekali saat server startup
CATEGORIES = load_categories()
FILMS      = load_films()


def film_matches_categories(film, category_names):
    film_genre = film["parent_genre"].lower()
    return any(
        cat.lower() == film_genre
        for cat in category_names
    )


@app.route("/categories", methods=["GET"])
def get_categories():
    return jsonify({
        "status": "success",
        "data"  : CATEGORIES
    }), 200


@app.route("/recommendations", methods=["GET"])
def get_recommendations():

    # Support multiple query params:
    # ?category=action&category=romance -> untuk multiple
    categories = request.args.getlist("category")

    if not categories:
        return jsonify({
            "status" : "error",
            "message": "Query parameter 'category' is required."
        }), 400

    valid_names = {
        c["name"].lower()
        for c in CATEGORIES
    }

    invalid = [
        c for c in categories
        if c.lower() not in valid_names
    ]

    if invalid:
        return jsonify({
            "status" : "error",
            "message": f"Unknown category: {invalid}. Valid categories: {sorted(valid_names)}"
        }), 400

    matched = [
        {
            "id"          : film["id"],
            "title"       : film["title"],
            "genre"       : film["genre"],
            "parent_genre": film["parent_genre"],
            "poster"      : film["poster"],
            "imdb_score"  : film["imdb_score"],
        }

        for film in FILMS
        if film_matches_categories(film, categories)
    ]

    return jsonify({
        "status": "success",
        "filter": categories,
        "total" : len(matched),
        "data"  : matched
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