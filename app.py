from flask import Flask, render_template, request, redirect, session, url_for
from config import get_conn
from werkzeug.utils import secure_filename
from functools import wraps
import os

app = Flask(__name__)

# SECRET KEY
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# Upload folder
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= ADMIN CHECK =================
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# ================= HOME =================
@app.route("/")
def index():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    cur.execute("SELECT * FROM news")
    news = cur.fetchall()

    conn.close()

    return render_template("index.html", products=products, news=news)


# ================= ABOUT =================
@app.route("/aboutme")
def aboutme():
    return render_template("aboutme.html")


# ================= PRODUCTS PAGE =================
@app.route("/products")
def products_page():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    conn.close()

    return render_template("products.html", products=products)


# ================= NEWS PAGE =================
@app.route("/news")
def news_page():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM news")
    news = cur.fetchall()

    conn.close()

    return render_template("news.html", news=news)


# ================= NEWS DETAIL =================
@app.route("/news/<int:id>")
def news_detail(id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM news WHERE id=%s", (id,))
    news_item = cur.fetchone()

    conn.close()

    return render_template("news_detail.html", news=news_item)


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        gmail = request.form["gmail"]
        password = request.form["password"]

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE gmail=%s AND password=%s",
            (gmail, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["gmail"] = user[1]
            session["role"] = user[3]

            if user[3] == "admin":
                return redirect(url_for("admin"))
            return "❌ Not admin"

        return render_template("login.html", error="Invalid login")

    return render_template("login.html")


# ================= ADMIN =================
@app.route("/admin")
@admin_required
def admin():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    cur.execute("SELECT * FROM news")
    news = cur.fetchall()

    conn.close()

    return render_template("admin.html", products=products, news=news)


# ================= ADD =================
@app.route("/admin_add", methods=["GET", "POST"])
@admin_required
def admin_add():
    conn = get_conn()
    cur = conn.cursor()

    if request.method == "POST":

        # PRODUCT
        if "product_submit" in request.form:
            title = request.form["title"]
            quantity = request.form["quantity"]
            price = request.form["price"]
            detail = request.form["detail"]

            img = request.files["image"]
            filename = secure_filename(img.filename)
            img.save(os.path.join(UPLOAD_FOLDER, filename))

            cur.execute("""
                INSERT INTO products (title, image, quantity, price, detail)
                VALUES (%s,%s,%s,%s,%s)
            """, (title, filename, quantity, price, detail))

        # NEWS
        elif "news_submit" in request.form:
            title = request.form["title"]
            date = request.form["date"]
            detail = request.form["detail"]

            img = request.files["image"]
            filename = secure_filename(img.filename)
            img.save(os.path.join(UPLOAD_FOLDER, filename))

            cur.execute("""
                INSERT INTO news (title, date, image, detail)
                VALUES (%s,%s,%s,%s)
            """, (title, date, filename, detail))

        conn.commit()
        conn.close()

        return redirect(url_for("admin"))

    return render_template("admin_add.html")


# ================= DELETE PRODUCT =================
@app.route("/delete_product/<int:id>")
@admin_required
def delete_product(id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT image FROM products WHERE id=%s", (id,))
    img = cur.fetchone()

    if img:
        path = os.path.join(app.root_path, "static/uploads", img[0])
        if os.path.exists(path):
            os.remove(path)

    cur.execute("DELETE FROM products WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# ================= DELETE NEWS =================
@app.route("/delete_news/<int:id>")
@admin_required
def delete_news(id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT image FROM news WHERE id=%s", (id,))
    img = cur.fetchone()

    if img:
        path = os.path.join(app.root_path, "static/uploads", img[0])
        if os.path.exists(path):
            os.remove(path)

    cur.execute("DELETE FROM news WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
