from flask import Flask, render_template, request, redirect, session
from config import get_conn
from werkzeug.utils import secure_filename
from functools import wraps
import os

app = Flask(__name__)

# SECRET KEY (use env in production)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# Upload folder
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= ADMIN CHECK =================
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect("/login")
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
                return redirect("/admin")
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


# ================= ADD DATA =================
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

        return redirect("/admin")

    return render_template("admin_add.html")


# ================= NEWS DETAIL =================
@app.route("/news/<int:id>")
def news_detail(id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM news WHERE id=%s", (id,))
    news_item = cur.fetchone()

    conn.close()

    return render_template("news_detail.html", news=news_item)


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ================= IMPORTANT FOR RAILWAY =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
