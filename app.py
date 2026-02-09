import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "shop.db"))

# Товары
PRODUCTS = {
    "android": {"title": "Android версия", "price": 100},
    "pc": {"title": "PC версия", "price": 150},
}


@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/buy", methods=["POST"])
def buy():
    data = request.get_json(silent=True) or {}
    product = data.get("product")

    if not product or product not in PRODUCTS:
        return jsonify({"status": "error", "message": "Некорректный товар"}), 400

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT NOT NULL,
                key TEXT NOT NULL,
                is_used INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cursor.execute(
            "SELECT id, key FROM keys WHERE product = ? AND is_used = 0 LIMIT 1",
            (product,),
        )
        result = cursor.fetchone()

        if result:
            key_id, key_value = result
            cursor.execute("UPDATE keys SET is_used = 1 WHERE id = ?", (key_id,))
            conn.commit()
            return jsonify({"status": "ok", "key": key_value})

        return jsonify({"status": "error", "message": "Нет в наличии"})
    except sqlite3.Error:
        return jsonify({"status": "error", "message": "Ошибка базы данных. Проверьте DB_PATH и таблицу keys."}), 500
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    app.run(port=5000, debug=True)
