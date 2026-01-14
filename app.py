from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("movies.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER,
            actors TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_movies():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, year, actors FROM movies ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_movie_db(title: str, year: str, actors: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO movies(title, year, actors) VALUES (?, ?, ?)",
        (title, int(year) if year.isdigit() else None, actors),
    )
    conn.commit()
    conn.close()


def delete_movies_db(ids: list[str]):
    if not ids:
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    placeholders = ",".join("?" for _ in ids)
    cur.execute(f"DELETE FROM movies WHERE id IN ({placeholders})", ids)
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def home():
    # usuwanie zaznaczonych (POST na "/")
    if request.method == "POST":
        ids = request.form.getlist("movieToRemove")
        delete_movies_db(ids)
        return redirect(url_for("home"))

    movies = get_movies()
    return render_template("home.html", movies=movies)


@app.route("/addMovie", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        year = (request.form.get("year") or "").strip()
        actors = (request.form.get("actors") or "").strip()

        if title:
            add_movie_db(title, year, actors)

        return redirect(url_for("home"))

    return render_template("add.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
