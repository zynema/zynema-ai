import os
import joblib
import pandas as pd
import numpy as np
from scipy.sparse import hstack as sparse_hstack, csc_matrix
from sklearn.metrics.pairwise import cosine_similarity

api_artifacts = None

def load_models_on_startup():
    global api_artifacts
    try:
        print("Loading model and API data...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        artifacts_dir = os.path.join(base_dir, 'artifacts')
        model_path = os.path.join(artifacts_dir, "model_rekomendasi.pkl")
        api_artifacts = joblib.load(model_path)
        print("Model and data loaded successfully.")

    except Exception as e:
        print(f"Failed to load model on startup: {e}")

def get_recommendations(
    selected_genres: list,
    director_input: str = None,
    year_input: int = None,
    num_recommendations: int = 10
):
    global api_artifacts

    if not selected_genres or not isinstance(selected_genres, list):
        return {
            "success": False,
            "message": "selected_genres must be a non-empty list.",
            "data": []
        }

    if api_artifacts is None:
        return {
            "success": False,
            "message": "Model not loaded. Ensure load_models_on_startup() was called.",
            "data": []
        }

    try:
        df_movies = api_artifacts['df_movies']
        feature_matrix = api_artifacts['feature_matrix']
        tfidf_genre = api_artifacts['tfidf_vectorizer']
        tfidf_director = api_artifacts['tfidf_director']
        scaler = api_artifacts['scaler']

        selected_genres_str = " ".join(selected_genres)
        genre_vector_input = tfidf_genre.transform([selected_genres_str])

        if director_input and str(director_input).strip():
            director_vector_input = tfidf_director.transform([director_input])
        else:
            director_vocab_size = tfidf_director.transform(['']).shape[1]
            director_vector_input = csc_matrix((1, director_vocab_size))

        default_imdb = df_movies['IMDB Score'].median()
        min_runtime = df_movies['Runtime'].min()
        max_runtime = df_movies['Runtime'].max()
        df_movies['runtime_normalized'] = (df_movies['Runtime'] - min_runtime) / (max_runtime - min_runtime)
        default_runtime = df_movies['runtime_normalized'].median()
        chosen_year = int(year_input) if year_input else df_movies['year_premiere'].median()

        user_numeric_scaled = scaler.transform([[default_imdb, default_runtime, chosen_year]])
        user_imdb_scaled = user_numeric_scaled[0][0]
        user_runtime_scaled = user_numeric_scaled[0][1]
        user_year_scaled = user_numeric_scaled[0][2]

        if not year_input:
            user_year_scaled = 0.7

        numeric_vector_input = sparse_hstack([
            csc_matrix([[user_imdb_scaled]]),
            csc_matrix([[user_runtime_scaled]]),
            csc_matrix([[user_year_scaled]])
        ])

        input_feature_matrix = sparse_hstack([
            genre_vector_input,
            director_vector_input,
            numeric_vector_input
        ])

        sim_scores = cosine_similarity(input_feature_matrix, feature_matrix)[0]

        movie_scores = [
            (idx, score)
            for idx, score in enumerate(sim_scores)
            if score > 0
        ]

        movie_scores = sorted(movie_scores, key=lambda x: x[1], reverse=True)
        movie_indices = [idx for idx, score in movie_scores[:num_recommendations]]

        kolom_output = [
            "Title",
            "main_parent_genre",
            "Director",
            "year_premiere",
            "IMDB Score",
            "Runtime",
            "poster",
            "primary_language_capitalized",
            "Premiere",
            "Plot"
        ]

        recommendations = df_movies[kolom_output].iloc[movie_indices].copy()
        recommendations["similarity_score"] = [
            round(score, 4) for idx, score in movie_scores[:num_recommendations]
        ]
        recommendations = recommendations.replace({np.nan: None})

        return {
            "success": True,
            "message": "Recommendations generated successfully.",
            "total": len(recommendations),
            "data": recommendations.to_dict(orient="records")
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error in recommendation function: {str(e)}",
            "data": []
        }