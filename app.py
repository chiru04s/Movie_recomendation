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

MOVIE_FILE_ID = "1Y01dyve2v34b9BToyt_j3wqLWd4KqL5y"
SIM_FILE_ID = "1Vs739G-DtThLGnAFPPAt0ZOSn_nHRQy3"

MOVIE_FILE = "model/movie_list.pkl"
SIM_FILE = "model/similarity.pkl"

os.makedirs("model", exist_ok=True)


# ------------------ DOWNLOAD FUNCTION ------------------
def download_file(file_id, output_path):
    if not os.path.exists(output_path):
        with st.spinner(f"Downloading {output_path}..."):
            gdown.download(id=file_id, output=output_path, quiet=False)

        if os.path.getsize(output_path) < 10000:
            st.error("Downloaded file corrupted. Check Drive permission.")
            st.stop()


download_file(MOVIE_FILE_ID, MOVIE_FILE)
download_file(SIM_FILE_ID, SIM_FILE)


# ------------------ LOAD PICKLE ------------------
def load_pickle(path):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"Failed to load {path}: {e}")
        st.stop()


movies = load_pickle(MOVIE_FILE)
similarity = load_pickle(SIM_FILE)


# ------------------ UNIVERSAL TITLE EXTRACTOR ------------------
def extract_titles(data):

    st.write("Loaded data type:", type(data))  # debug

    # Case 1: DataFrame
    if isinstance(data, pd.DataFrame):
        data.columns = data.columns.str.strip()
        if "title" in data.columns:
            titles = data["title"].tolist()
        else:
            st.error("'title' column missing")
            st.stop()

    # Case 2: List
    elif isinstance(data, list):
        titles = data

    # Case 3: Pandas Series
    elif isinstance(data, pd.Series):
        titles = data.tolist()

    # Case 4: Numpy array
    elif isinstance(data, np.ndarray):
        titles = data.tolist()

    # Case 5: Dictionary
    elif isinstance(data, dict):
        if "title" in data:
            titles = data["title"]
        else:
            titles = list(data.values())

    else:
        st.error(f"Unsupported data type: {type(data)}")
        st.stop()

    # Clean titles
    clean_titles = []
    for t in titles:
        if pd.notna(t):
            clean_titles.append(str(t))

    if len(clean_titles) == 0:
        st.error("No valid movie titles found.")
        st.stop()

    return sorted(list(set(clean_titles)))


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

    except:
        pass

    fallback = "https://via.placeholder.com/500x750?text=Poster+Not+Available"
    POSTER_CACHE[movie_title] = fallback
    return fallback


# ------------------ RECOMMEND ------------------
def recommend(movie):
    try:
        if isinstance(movies, pd.DataFrame):
            index = movies[movies["title"] == movie].index[0]
        else:
            index = movie_titles.index(movie)

        distances = sorted(
            list(enumerate(similarity[index])),
            reverse=True,
            key=lambda x: x[1]
        )

        recommendations = []

        for i in distances[1:6]:
            if isinstance(movies, pd.DataFrame):
                title = str(movies.iloc[i[0]].title)
            else:
                title = movie_titles[i[0]]

            recommendations.append({
                "title": title,
                "poster": fetch_poster(title)
            })

        return recommendations

    except Exception as e:
        st.error(f"Recommendation error: {e}")
        return []


# ------------------ UI ------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🍿 Movie Recommender System")

selected_movie = st.selectbox("Select a movie you like:", movie_titles)

if st.button("Get Recommendations"):

    with st.spinner("Finding similar movies..."):
        recs = recommend(selected_movie)

    if not recs:
        st.warning("No recommendations found.")
    else:
        cols = st.columns(5)

        for i, movie in enumerate(recs):
            with cols[i]:
                st.image(movie["poster"], width=150, caption=movie["title"])