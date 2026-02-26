# 🎬 Movie Recommendation System

A content-based movie recommendation web app built using **Python**, **Machine Learning**, and **Streamlit**.
It suggests movies similar to a selected movie based on features like genres, keywords, cast, and crew.

---

## 🚀 Live Demo

👉 *(Add your deployed app link here after deployment)*

---

## 📌 Features

* 🔍 Search and select a movie
* 🎯 Get top recommended similar movies
* 🎬 Poster display for each recommendation
* ⚡ Fast content-based filtering
* 🌐 Simple interactive web interface

---

## 🧠 How It Works

This project uses **Content-Based Filtering**:

1. Movie metadata is combined into a single feature
2. Text is vectorized using CountVectorizer
3. Cosine similarity is calculated
4. Most similar movies are recommended

---

## 🛠️ Tech Stack

* Python
* Pandas
* NumPy
* Scikit-learn
* Streamlit

---

## 📂 Dataset

TMDB 5000 Movie Dataset

Files used:

* `tmdb_5000_movies.csv`
* `tmdb_5000_credits.csv`

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/chiru04s/Movie_recomendation.git
cd Movie_recomendation
```

---

### 2️⃣ Create virtual environment (optional)

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Download Model Files

Large model files are not stored in the repository.

👉 Download from:
**(Paste your Google Drive link here)**

Place the downloaded files inside:

```
model/
```

---

### 5️⃣ Run the app

```bash
streamlit run app.py
```

---

## 📸 Screenshots

*(Add screenshots of your app here)*

---

## 🎯 Project Structure

```
Movie_recomendation/
│
├── app.py
├── recommend.ipynb
├── Datasets/
│   ├── tmdb_5000_movies.csv
│   └── tmdb_5000_credits.csv
├── model/
│   └── similarity.pkl (download separately)
├── requirements.txt
└── README.md
```

---

## 👨‍💻 Author

**Your Name**

---

## 📜 License

This project is for educational purposes.
