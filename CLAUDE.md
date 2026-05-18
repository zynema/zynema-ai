# Zynema - Netflix Originals Recommendation
# Capstone Project | Pijak x IBM SkillsBuild

---

## Project Overview

**Nama Proyek:** Zynema
**Tipe:** Netflix Originals Film Recommendation System (Content-Based Filtering)
**Author:** Ahmad Rifa'i (Ahmad)
**Team:** Zynema - Pijak x IBM SkillsBuild
**Repository:** https://github.com/rezzz59/zynema-ai
**Branch:** `feat/data-processing` (data processing selesai, ready untuk merge)

---

## Dataset

| Aspek | Value |
|-------|-------|
| File asli | `data/raw/NetflixOriginals.csv` (~600 film) |
| File bersih | `data/processed/netflix_cleaned.csv` (528 film) |
| Genre sebelum | 115 unik |
| Genre sesudah | 17 kategori |
| Poster | 100% valid (dari OMDB API) |

---

## Task & Progress

| # | Person | Task | Status |
|---|--------|------|--------|
| 1 | Hilmi | 3 endpoint API (data dummy) | Pending |
| 2 | Ahmad | EDA + Cleaning + Poster fetch | ✅ Done |
| 3 | Rafly | TF-IDF + Cosine Similarity model | Pending |
| 4 | Dexi | 3 static page HTML (category, home, detail) | Pending |

---

## Dataset Columns (netflix_cleaned.csv)

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `Title` | string | Judul film (lowercase, spasi tunggal) |
| `parent_genre_str` | string | Genre bersih (multi-label, 17 kategori) |
| `metadata` | string | Teks TF-IDF: "movie title is [x]. genre is [x]. language is [x]." |
| `poster` | URL | Poster valid dari OMDB API |
| `year` | float | Tahun release (ekstrak dari Premiere) |
| `IMDB Score` | float | Rating IMDB (1-10) |
| `Runtime` | int | Durasi dalam menit |
| `runtime_normalized` | float | Durasi MinMaxScaler (0-1, untuk model ML) |
| `primary_language` | string | Bahasa utama film |
| `Premiere` | string | Tanggal release lengkap |

---

## 17 Genre Categories

| ID | Genre | Keyword Mapping |
|----|-------|----------------|
| 1 | action | action, superhero, heist, spy, martial |
| 2 | adventure | adventure, exploration |
| 3 | animation | animation, animated, anime, stop motion, cgi |
| 4 | comedy | comedy, dark comedy, satire, slapstick, parody |
| 5 | documentary | documentary, mockumentary, making of, concert film |
| 6 | drama | drama, biopic, historical, sports, coming of age, biographical, crime drama |
| 7 | family | family, christmas, holiday, kids |
| 8 | fantasy | fantasy, magical, mythology |
| 9 | horror | horror, zombie, supernatural horror, psychological horror |
| 10 | musical | musical, concert, dance |
| 11 | mystery | mystery, detective |
| 12 | other | fallback (tidak match mapping) |
| 13 | romance | romance, romantic, love |
| 14 | scifi | science fiction, sci fi |
| 15 | thriller | thriller |
| 16 | war | war, military |
| 17 | western | western |

**Perbaikan Bug v2:** Thriller = genre terpisah (bukan masuk action). Crime drama = masuk drama (bukan action).

---

## Feature Engineering

| Fitur | Method | Output |
|-------|--------|--------|
| `year` | Ekstrak angka dari `Premiere` (regex) | Float (contoh: 2020.0) |
| `runtime_normalized` | MinMaxScaler(df['Runtime']) | Float 0-1 |
| `primary_language` | Ambil bahasa pertama dari `Language` | String |
| `metadata` | Gabungan: title + genre + language | String untuk TF-IDF |

---

## Processing Pipeline

1. **Cleaning** — lowercase, hapus spasi berlebih, standarisasi separator genre
2. **Genre Binning** — 115 → 17 kategori (keyword matching, multi-label)
3. **Feature Engineering** — year, runtime_normalized, primary_language, metadata
4. **Poster Fetching** — OMDB API, rate limit 1 req/detik, retry 3x, validasi URL
5. **Export** — `netflix_cleaned.csv` + `categories.json`

---

## Output Files

```
data/
├── raw/
│   └── NetflixOriginals.csv       ← dataset asli
└── processed/
    ├── netflix_cleaned.csv        ← 528 film × 10 kolom
    └── categories.json            ← 17 genre + ID

model/
└── notebook/
    └── zynema.ipynb               ← notebook processing (oleh Ahmad)
```

---

## Team & Tech Stack

| Orang | Tanggung Jawab |
|-------|---------------|
| **Ahmad** | Data processing, EDA, genre cleaning, poster fetch ✅ |
| **Hilmi** | FastAPI backend, 3 endpoint |
| **Rafly** | TF-IDF + Cosine Similarity model |
| **Dexi** | 3 static page HTML (category, home, detail) |

- **Backend:** FastAPI (Hilmi)
- **Frontend:** Static HTML (Dexi)
- **Model:** TF-IDF + Cosine Similarity (Rafly)
- **Data Processing:** Python, Pandas, OMDB API, MinMaxScaler

---

## Git Info

- **Repo:** https://github.com/rezzz59/zynema-ai
- **Branch:** `feat/data-processing`
- **Author:** Ahmad Rifa'i `<zonaamuntai62@gmail.com>`
- **GitHub user:** rezzz59

---

*Last updated: 2026-05-19*
