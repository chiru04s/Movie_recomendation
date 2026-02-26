import pickle
import streamlit as st
import requests
import os
import gdown
from urllib.parse import quote
import pandas as pd


# ------------------ CONFIGURATION ------------------
OMDB_API_KEY = "92a7aba5"
POSTER_CACHE = {}

MOVIE_FILE_ID = "1Y01dyve2v34b9BToyt_j3wqLWd4KqL5y"
SIM_FILE_ID = "1Vs739G-DtThLGnAFPPAt0ZOSn_nHRQy3"

MOVIE_FILE = "model/movie_list.pkl"
SIM_FILE = "model/similarity.pkl"

os.makedirs("model", exist_ok=True)


# ------------------ DOWNLOAD FUNCTION ------------------
def download_file(file_id, output_path):
    if not os.path.exists(output_path):
        with st.spinner(f"Downloading {output_path}..."):
            gdown.download(
                id=file_id,
                output=output_path,
                quiet=False
            )

        # Validate file size (avoid corrupted HTML file)
        if os.path.getsize(output_path) < 10000:
            st.error("Downloaded file appears corrupted. Check Drive permissions.")
            st.stop()


download_file(MOVIE_FILE_ID, MOVIE_FILE)
download_file(SIM_FILE_ID, SIM_FILE)


# ------------------ SAFE PICKLE LOAD ------------------
def load_pickle(path):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"Failed to load {path}: {e}")
        st.stop()


movies = load_pickle(MOVIE_FILE)
similarity = load_pickle(SIM_FILE)


# ------------------ CLEAN MOVIE TITLES ------------------
def extract_titles(movies):
    if isinstance(movies, list):
        titles = movies

    elif isinstance(movies, pd.DataFrame):
        movies.columns = movies.columns.str.strip()

        if "title" not in movies.columns:
            st.error("'title' column missing in dataset")
            st.stop()

        titles = movies["title"].tolist()

    else:
        st.error("Movie data format invalid")
        st.stop()

    # 🔥 CRITICAL FIX
    # Remove None, NaN, non-string and convert everything to string
    clean_titles = []
    for t in titles:
        if pd.notna(t):
            clean_titles.append(str(t))

    return sorted(list(set(clean_titles)))  # remove duplicates safely


movie_titles = extract_titles(movies)


# ------------------ FETCH POSTER ------------------
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
        if isinstance(movies, list):
            index = movies.index(movie)
        else:
            index = movies[movies["title"] == movie].index[0]

        distances = sorted(
            list(enumerate(similarity[index])),
            reverse=True,
            key=lambda x: x[1]
        )

        recommendations = []

        for i in distances[1:6]:
            if isinstance(movies, list):
                movie_title = str(movies[i[0]])
            else:
                movie_title = str(movies.iloc[i[0]].title)

            recommendations.append({
                "title": movie_title,
                "poster": fetch_poster(movie_title)
            })

        return recommendations

    except Exception as e:
        st.error(f"Recommendation error: {e}")
        return []


# ------------------ STREAMLIT UI ------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🍿 Movie Recommender System")

if len(movie_titles) == 0:
    st.error("No movies available to display.")
    st.stop()

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