from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

main = Blueprint('main', __name__)

def get_db():
    conn = sqlite3.connect('instance/database.db')
    conn.row_factory = sqlite3.Row
    return conn

@main.route("/")
def index():
    return render_template("index.html")


@main.route("/persona/<nombre>")
def persona(nombre):
    db = get_db()
    persona = db.execute(
        "SELECT * FROM personas WHERE nombre = ?",
        (nombre,)
    ).fetchone()

    if persona:
        return render_template("persona.html", persona=persona)
    else:
        return render_template("error.html")


@main.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        nombre = request.form["nombre"]

        db = get_db()
        db.execute("INSERT INTO personas (nombre) VALUES (?)", (nombre,))
        db.commit()

        return redirect(url_for("main.persona", nombre=nombre))

    return render_template("upload.html")