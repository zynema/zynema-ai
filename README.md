# Zynema — Netflix Film Recommendation System

Zynema is a content-based film recommendation system built on top of the Netflix Original Films dataset. It recommends movies using **TF-IDF vectorization** combined with **Cosine Similarity**, taking into account genre preferences, director, and premiere year. The backend is served as a REST API via Flask.

---

## Features

- Recommend films based on 1–3 genre preferences
- Optional filtering by director and premiere year
- Enriched metadata (posters, plot summaries, IMDb scores) via OMDB API
- REST API with endpoints for films, categories, directors, and recommendations
- Pre-trained model artifacts stored with `joblib` for fast inference

---

## Project Structure

```
zynema-ai/
├── backend/
│   ├── api/
│   │   ├── app.py                      # Flask application & route handlers
│   │   └── recommendation_service.py   # Core recommendation logic
│   ├── Dockerfile
│   ├── requirements.txt
│   └── vercel.json
├── data/
│   ├── processed/
│   │   ├── categories.json             # List of valid genre categories
│   │   └── netflix_cleaned_dataset.csv # Cleaned & enriched dataset
│   └── raw/
│       └── NetflixOriginals.csv        # Original Kaggle dataset
├── model/
│   └── model_rekomendasi.pkl           # Serialized model artifacts (TF-IDF, scaler, feature matrix)
├── .gitignore
└── environment.yml
```

---

## How It Works

### 1. Dataset

- **Source:** [Netflix Original Films & IMDB Scores](https://www.kaggle.com/datasets/luiscorter/netflix-original-films-imdb-scores) on Kaggle
- **Enrichment:** Plot summaries, posters, directors, and language info fetched from the [OMDB API](http://www.omdbapi.com/)

### 2. Preprocessing (`dataset-preprocessing.ipynb`)

- Standardize genre strings (normalize separators, strip whitespace)
- Map granular genres to 16 parent genre categories (action, drama, thriller, etc.)
- Extract premiere year, normalize runtime with MinMaxScaler
- Enrich each film with OMDB metadata (plot, poster, director)

### 3. Modelling (`modelling.ipynb`)

The recommendation model is built as a **hybrid feature vector** combining:

| Feature | Method |
|---|---|
| Genre | TF-IDF on `main_parent_genre` |
| Director | TF-IDF on `Director` |
| IMDb Score | MinMaxScaler (numeric) |
| Runtime | MinMaxScaler (numeric) |
| Premiere Year | MinMaxScaler (numeric) |

All features are combined into a single sparse matrix using `scipy.sparse.hstack`. At inference time, a user query vector is constructed from the selected inputs and compared against all films using **Cosine Similarity**. The top-N highest-scoring films are returned as recommendations.

The trained artifacts (vectorizers, scaler, feature matrix, and film DataFrame) are serialized into `artifacts/model_rekomendasi.pkl` using `joblib`.

---

## Getting Started

### Prerequisites

- Python 3.12
- conda (for environment management) or pip

### Installation

**Using conda:**

```bash
conda env create -f environment.yml
conda activate zynema-ai
pip install -r requirements.txt
```

**Using pip only:**

```bash
pip install -r requirements.txt
```

### Running the API

```bash
python api/app.py
```

The server starts at `http://localhost:5000`.

---

## API Endpoints

### `GET /categories`

Returns all available genre categories.

**Response:**
```json
{
  "status": "success",
  "data": ["action", "drama", "thriller", ...]
}
```

---

### `GET /directors?search=<query>`

Returns a list of directors. Optionally filter by name with the `search` parameter.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `search` | string | No | Filter directors by name (partial match) |

---

### `GET /recommendations`

Returns film recommendations based on genre, director, and year preferences.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `category` | string | Yes | Genre(s) to filter by (repeat for multiple) |
| `director` | string | No | Preferred director name |
| `year` | integer | No | Preferred premiere year |

**Example:**
```
GET /recommendations?category=action&category=thriller&director=Christopher+Nolan&year=2020
```

**Response:**
```json
{
  "status": "success",
  "filter": { "categories": ["action", "thriller"], "director": "Christopher Nolan", "year": 2020 },
  "total": 10,
  "data": [
    {
      "id": 42,
      "title": "Film Title",
      "parent_genre": "action",
      "imdb_score": "7.5",
      "runtime": 120,
      "poster": "https://...",
      "primary_language": "English",
      "premiere": "Jan 1, 2020",
      "director": "Christopher Nolan",
      "year_premiere": 2020,
      "plot": "...",
      "similarity_score": 0.8712
    }
  ]
}
```

---

### `GET /films/<film_id>`

Returns full details for a single film by ID.

---

## ☁️ Deployment (Vercel)

The project is configured for deployment on Vercel via `vercel.json`. All routes are handled by `api/app.py`.

```json
{
  "builds": [{ "src": "api/app.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "api/app.py" }]
}
```

Deploy with:

```bash
vercel deploy
```
## Frontend (Next.js) Integration Guide

The Zynema frontend is maintained in a separate repository: **[zynema/zynema-frontend](https://github.com/zynema/zynema-frontend)**

Follow the steps below to seamlessly connect the Next.js frontend with the Flask backend in both local (development) and production (Vercel) environments.

---
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Web Framework | Flask |
| ML / NLP | scikit-learn, TF-IDF, Cosine Similarity |
| Data | pandas, numpy, scipy |
| Model Serialization | joblib |
| Deployment (Backend) | Vercel (via `@vercel/python`) |
| Deployment (Frontend) | Vercel (via Next.js) |
| Frontend Repository | [zynema/zynema-frontend](https://github.com/zynema/zynema-frontend) |
| Dataset | Kaggle — Netflix Original Films |
| Metadata Enrichment | OMDB API |

---

## License

This project is for educational purposes. Dataset sourced from [Kaggle](https://www.kaggle.com/datasets/luiscorter/netflix-original-films-imdb-scores) and enriched via the [OMDB API](http://www.omdbapi.com/).
