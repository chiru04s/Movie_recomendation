import pickle
import streamlit as st
import requests
import os
import gdown
from urllib.parse import quote
import numpy as np
import pandas as pd

# ---------------- CONFIG ----------------
OMDB_API_KEY = "92a7aba5"
MOVIE_FILE_ID = "1Y01dyve2v34b9BToyt_j3wqLWd4KqL5y"
SIM_FILE_ID = "1Vs739G-DtThLGnAFPPAt0ZOSn_nHRQy3"

MOVIE_FILE = "model/movie_list.pkl"
SIM_FILE = "model/similarity.pkl"

os.makedirs("model", exist_ok=True)

# ---------------- DOWNLOAD ----------------
def download_file(file_id, output_path):
    if not os.path.exists(output_path):
        gdown.download(id=file_id, output=output_path, quiet=False)

download_file(MOVIE_FILE_ID, MOVIE_FILE)
download_file(SIM_FILE_ID, SIM_FILE)

# ---------------- LOAD ----------------
def load_pickle(path):
    with open(path, "rb") as f:
        return pickle.load(f)

movies_raw = load_pickle(MOVIE_FILE)
similarity = load_pickle(SIM_FILE)

# ---------------- FORCE SAFE TITLE EXTRACTION ----------------
def force_extract_titles(data):

    # Convert everything to list safely
    if isinstance(data, pd.DataFrame):
        if "title" in data.columns:
            titles = data["title"].tolist()
        else:
            titles = data.iloc[:, 0].tolist()

    elif isinstance(data, np.ndarray):
        titles = data.flatten().tolist()

    elif isinstance(data, list):
        titles = data

    else:
        titles = list(data)

    # Clean
    clean = []
    for t in titles:
        if t is not None:
            clean.append(str(t).strip())

    return clean

movie_titles = force_extract_titles(movies_raw)

# Extra safety check
if len(movie_titles) != len(similarity):
    st.error("Titles and similarity matrix length mismatch.")
    st.stop()

# ---------------- POSTER ----------------
def fetch_poster(title):
    try:
        url = f"http://www.omdbapi.com/?t={quote(title)}&apikey={OMDB_API_KEY}"
        data = requests.get(url, timeout=5).json()
        if data.get("Response") == "True" and data.get("Poster") not in ["N/A", None]:
            return data["Poster"]
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

# ---------------- RECOMMEND ----------------
def recommend(movie):
    index = movie_titles.index(movie)
    distances = sorted(
        list(enumerate(similarity[index])),
        key=lambda x: x[1],
        reverse=True
    )
    return [movie_titles[i[0]] for i in distances[1:6]]

# ---------------- UI ----------------
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🍿 Movie Recommender")

selected_movie = st.selectbox("Select a movie:", movie_titles)

if st.button("Recommend"):
    results = recommend(selected_movie)
    cols = st.columns(5)
    for i, title in enumerate(results):
        with cols[i]:
            st.image(fetch_poster(title), width=150)
            st.caption(title)