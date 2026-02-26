import pickle
import streamlit as st
import requests
import os
import gdown
from urllib.parse import quote
import pandas as pd
import numpy as np


# ------------------ CONFIGURATION ------------------
OMDB_API_KEY = "92a7aba5"
POSTER_CACHE = {}

# Google Drive File IDs
MOVIE_FILE_ID = "1Y01dyve2v34b9BToyt_j3wqLWd4KqL5y"
SIM_FILE_ID = "1Vs739G-DtThLGnAFPPAt0ZOSn_nHRQy3"

MOVIE_FILE = "model/movie_list.pkl"
SIM_FILE = "model/similarity.pkl"


# ------------------ CREATE MODEL FOLDER ------------------
os.makedirs("model", exist_ok=True)


# ------------------ DOWNLOAD FUNCTION ------------------
def download_file(file_id, output_path):
    if not os.path.exists(output_path):
        with st.spinner(f"Downloading {output_path}..."):
            gdown.download(
                id=file_id,          # ✅ correct method for large files
                output=output_path,
                quiet=False
            )

        # Validate file size (avoid HTML download issue)
        if os.path.getsize(output_path) < 10000:
            st.error("Downloaded file appears corrupted. Check Google Drive permissions.")
            st.stop()


# ------------------ DOWNLOAD FILES ------------------
download_file(MOVIE_FILE_ID, MOVIE_FILE)
download_file(SIM_FILE_ID, SIM_FILE)


# ------------------ LOAD PICKLE SAFELY ------------------
def load_pickle(path):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"❌ Failed to load {path}: {e}")
        st.stop()


movies = load_pickle(MOVIE_FILE)
similarity = load_pickle(SIM_FILE)


# ------------------ DATA FORMAT SAFETY CHECK ------------------
if isinstance(movies, (list, np.ndarray)):
    movie_titles = list(movies)

elif isinstance(movies, pd.DataFrame):
    movies.columns = movies.columns.str.strip()

    if "title" in movies.columns:
        movie_titles = movies["title"].values
    else:
        st.error("❌ 'title' column not found in movie data.")
        st.write("Available columns:", movies.columns)
        st.stop()

else:
    st.write("Loaded type:", type(movies))
    st.error("❌ Movie data format is incorrect.")
    st.stop()


# ------------------ FETCH POSTER FUNCTION ------------------
def fetch_poster(movie_title):

    if movie_title in POSTER_CACHE:
        return POSTER_CACHE[movie_title]

    try:
        encoded_title = quote(movie_title)
        url = f"http://www.omdbapi.com/?t={encoded_title}&apikey={OMDB_API_KEY}"

        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("Response") == "True" and data.get("Poster") not in ["N/A", None]:
            POSTER_CACHE[movie_title] = data["Poster"]
            return data["Poster"]

    except Exception:
        pass

    fallback = "https://via.placeholder.com/500x750?text=Poster+Not+Available"
    POSTER_CACHE[movie_title] = fallback
    return fallback


# ------------------ RECOMMEND FUNCTION ------------------
def recommend(movie):
    try:
        if isinstance(movies, (list, np.ndarray)):
            index = list(movies).index(movie)
        else:
            index = movies[movies["title"] == movie].index[0]

        distances = sorted(
            list(enumerate(similarity[index])),
            reverse=True,
            key=lambda x: x[1]
        )

        recommendations = []

        for i in distances[1:6]:

            if isinstance(movies, (list, np.ndarray)):
                movie_title = movies[i[0]]
            else:
                movie_title = movies.iloc[i[0]].title

            recommendations.append({
                "title": movie_title,
                "poster": fetch_poster(movie_title)
            })

        return recommendations

    except Exception as e:
        st.error(f"❌ Recommendation error: {e}")
        return []


# ------------------ STREAMLIT UI ------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🍿 Movie Recommender System")

selected_movie = st.selectbox(
    "Select a movie you like:",
    movie_titles
)

if st.button("Get Recommendations", type="primary"):

    with st.spinner("Finding similar movies..."):
        recommendations = recommend(selected_movie)

    if not recommendations:
        st.warning("No recommendations found.")
    else:
        st.subheader(f"Movies similar to: {selected_movie}")

        cols = st.columns(5)

        for i, movie in enumerate(recommendations):
            with cols[i]:
                st.image(
                    movie["poster"],
                    width=150,
                    caption=movie["title"]
                )


st.markdown("---")
st.caption(
    "Recommendations are based on content similarity. "
    "Poster availability depends on OMDB API."
)