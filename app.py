import pickle
import streamlit as st
import requests
import os
import gdown
import numpy as np
from urllib.parse import quote

# ------------------ CONFIGURATION ------------------

OMDB_API_KEY = "92a7aba5"
POSTER_CACHE = {}

MOVIE_FILE_ID = "1Y01dyve2v34b9BToyt_j3wqLWd4KqL5y"
SIM_FILE_ID = "1Vs739G-DtThLGnAFPPAt0ZOSn_nHRQy3"

MOVIE_PATH = "model/movie_list.pkl"
SIM_PATH = "model/similarity.pkl"

os.makedirs("model", exist_ok=True)


# ------------------ DOWNLOAD FUNCTION ------------------

def download_file(file_id, output_path):
    if not os.path.exists(output_path):
        with st.spinner("Downloading model files... Please wait ⏳"):
            gdown.download(id=file_id, output=output_path, quiet=True)

        # Validate file size (avoid HTML download issue)
        if not os.path.exists(output_path) or os.path.getsize(output_path) < 10000:
            st.error("Model download failed. Check Google Drive permissions.")
            st.stop()


# Download only if missing
download_file(MOVIE_FILE_ID, MOVIE_PATH)
download_file(SIM_FILE_ID, SIM_PATH)


# ------------------ LOAD MODEL FILES ------------------

try:
    with open(MOVIE_PATH, "rb") as f:
        movies = pickle.load(f)

    with open(SIM_PATH, "rb") as f:
        similarity = pickle.load(f)

except Exception as e:
    st.error(f"Failed to load model files: {str(e)}")
    st.stop()


# ------------------ NORMALIZE MOVIE TITLES ------------------

def extract_titles(data):

    # Case 1: DataFrame
    if hasattr(data, "columns"):
        if "title" not in data.columns:
            st.error("'title' column missing in movie data.")
            st.stop()
        titles = data["title"].tolist()

    # Case 2: NumPy array
    elif isinstance(data, np.ndarray):
        if data.ndim > 1:
            data = data.flatten()
        titles = data.tolist()

    # Case 3: List
    elif isinstance(data, list):
        titles = data

    else:
        st.error("Unsupported movie_list.pkl format.")
        st.stop()

    # Clean values
    clean_titles = []
    for t in titles:
        if t is not None:
            clean_titles.append(str(t))

    if len(clean_titles) == 0:
        st.error("No movie titles found in data.")
        st.stop()

    return clean_titles


movie_titles = extract_titles(movies)


# ------------------ POSTER FUNCTION ------------------

def fetch_poster(movie_title):

    if movie_title in POSTER_CACHE:
        return POSTER_CACHE[movie_title]

    try:
        encoded_title = quote(movie_title)
        url = f"http://www.omdbapi.com/?t={encoded_title}&apikey={OMDB_API_KEY}"

        response = requests.get(url, timeout=5)
        response.raise_for_status()
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

def recommend(selected_movie):

    try:
        # Get index safely
        if hasattr(movies, "columns"):
            index = movies[movies["title"] == selected_movie].index[0]
        else:
            index = movie_titles.index(selected_movie)

        distances = sorted(
            list(enumerate(similarity[index])),
            key=lambda x: x[1],
            reverse=True
        )

        recommendations = []

        for i in distances[1:6]:
            if hasattr(movies, "columns"):
                title = movies.iloc[i[0]].title
            else:
                title = movie_titles[i[0]]

            recommendations.append({
                "title": str(title),
                "poster": fetch_poster(str(title))
            })

        return recommendations

    except Exception as e:
        st.error(f"Recommendation error: {str(e)}")
        return []


# ------------------ STREAMLIT UI ------------------

st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🍿 Movie Recommender System")

selected_movie = st.selectbox(
    "Select a movie you like:",
    movie_titles
)

if st.button("Get Recommendations"):

    with st.spinner("Finding similar movies..."):
        recs = recommend(selected_movie)

    if not recs:
        st.warning("No recommendations found.")
    else:
        st.subheader(f"Movies similar to: {selected_movie}")

        cols = st.columns(5)

        for i, movie in enumerate(recs):
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