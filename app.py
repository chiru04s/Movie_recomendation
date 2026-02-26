import pickle
import streamlit as st
import requests
import os
import gdown
from urllib.parse import quote
import pandas as pd
import numpy as np


# ------------------ CONFIG ------------------
OMDB_API_KEY = "92a7aba5"
POSTER_CACHE = {}

MOVIE_FILE_ID = "1Y01dyve2v34b9BToyt_j3wqLWd4KqL5y"
SIM_FILE_ID = "1Vs739G-DtThLGnAFPPAt0ZOSn_nHRQy3"

MOVIE_FILE = "model/movie_list.pkl"
SIM_FILE = "model/similarity.pkl"

os.makedirs("model", exist_ok=True)


# ------------------ DOWNLOAD ------------------
def download_file(file_id, output_path):
    if not os.path.exists(output_path):
        with st.spinner(f"Downloading {output_path}..."):
            gdown.download(id=file_id, output=output_path, quiet=False)

        if os.path.getsize(output_path) < 10000:
            st.error("Downloaded file corrupted. Check Drive permission.")
            st.stop()


download_file(MOVIE_FILE_ID, MOVIE_FILE)
download_file(SIM_FILE_ID, SIM_FILE)


# ------------------ LOAD ------------------
def load_pickle(path):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"Failed to load {path}: {e}")
        st.stop()


movies = load_pickle(MOVIE_FILE)
similarity = load_pickle(SIM_FILE)


# ------------------ HANDLE NUMPY ARRAY PROPERLY ------------------
def extract_titles(data):

    st.write("Loaded movie data type:", type(data))

    # ✅ If numpy array
    if isinstance(data, np.ndarray):

        # If it's 2D like [[title1], [title2]]
        if data.ndim > 1:
            data = data.flatten()

        titles = data.tolist()

    # If DataFrame
    elif isinstance(data, pd.DataFrame):
        data.columns = data.columns.str.strip()
        if "title" not in data.columns:
            st.error("'title' column missing")
            st.stop()
        titles = data["title"].tolist()

    # If list
    elif isinstance(data, list):
        titles = data

    else:
        st.error(f"Unsupported movie data type: {type(data)}")
        st.stop()

    # Clean values
    clean_titles = []

    for t in titles:
        if t is not None:
            clean_titles.append(str(t))

    if len(clean_titles) == 0:
        st.error("No valid movie titles found.")
        st.stop()

    return clean_titles


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
        # Since yours is numpy array
        index = movie_titles.index(movie)

        distances = sorted(
            list(enumerate(similarity[index])),
            reverse=True,
            key=lambda x: x[1]
        )

        recommendations = []

        for i in distances[1:6]:
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