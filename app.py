from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Товары
PRODUCTS = {
    "android": {"title": "Android версия", "price": 100},
    "pc": {"title": "PC версия", "price": 150},
}

@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)


@app.route("/buy", methods=["POST"])
def buy():
    data = request.get_json(silent=True) or {}
    product = data.get("product")

    if not product or product not in PRODUCTS:
        return jsonify({"status": "error", "message": "Некорректный товар"}), 400

    conn = sqlite3.connect("../shop.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, key FROM keys WHERE product = ? AND is_used = 0 LIMIT 1",
        (product,)
    )
    result = cursor.fetchone()

    if result:
        key_id, key_value = result
        cursor.execute(
            "UPDATE keys SET is_used = 1 WHERE id = ?",
            (key_id,)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "ok", "key": key_value})

    conn.close()
    return jsonify({"status": "error", "message": "Нет в наличии"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
