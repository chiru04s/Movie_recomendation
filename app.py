import pickle
import streamlit as st
import requests
import os
import gdown
from urllib.parse import quote
import pandas as pd


# ------------------ CONFIGURATION ------------------
OMDB_API_KEY = "92a7aba5"  # Your OMDB API key
POSTER_CACHE = {}

# Google Drive File IDs
MOVIE_FILE_ID = "1Y01dyve2v34b9BToyt_j3wqLWd4KqL5y"
SIM_FILE_ID = "1Vs739G-DtThLGnAFPPAt0ZOSn_nHRQy3"

MOVIE_FILE = "model/movie_list.pkl"
SIM_FILE = "model/similarity.pkl"


# ------------------ CREATE MODEL FOLDER ------------------
os.makedirs("model", exist_ok=True)


# ------------------ DOWNLOAD FILES IF NOT EXISTS ------------------
if not os.path.exists(MOVIE_FILE):
    with st.spinner("Downloading movie data..."):
        gdown.download(
            f"https://drive.google.com/uc?id={MOVIE_FILE_ID}",
            MOVIE_FILE,
            quiet=False
        )

if not os.path.exists(SIM_FILE):
    with st.spinner("Downloading similarity data..."):
        gdown.download(
            f"https://drive.google.com/uc?id={SIM_FILE_ID}",
            SIM_FILE,
            quiet=False
        )


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


# ------------------ LOAD DATA ------------------
try:
    movies = pickle.load(open(MOVIE_FILE, "rb"))
    similarity = pickle.load(open(SIM_FILE, "rb"))
except Exception as e:
    st.error(f"❌ Failed to load model files: {e}")
    st.stop()


# ------------------ DATA FORMAT SAFETY CHECK ------------------
if isinstance(movies, list):
    movie_titles = movies

elif isinstance(movies, pd.DataFrame):
    movies.columns = movies.columns.str.strip()

    if "title" in movies.columns:
        movie_titles = movies["title"].values
    else:
        st.error("❌ 'title' column not found in movie data.")
        st.write("Available columns:", movies.columns)
        st.stop()

else:
    st.error("❌ Movie data format is incorrect.")
    st.stop()


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


# ------------------ MOVIE SELECT ------------------
selected_movie = st.selectbox(
    "Select a movie you like:",
    movie_titles
)


# ------------------ RECOMMEND BUTTON ------------------
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


# ------------------ FOOTER ------------------
st.markdown("---")
st.caption(
    "Recommendations are based on content similarity. "
    "Poster availability depends on OMDB API."
)