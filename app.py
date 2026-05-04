from flask import Flask, render_template, request, redirect, session
from Config import get_conn
from werkzeug.utils import secure_filename
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# =========================
# UPLOAD CONFIG
# =========================
UPLOAD_FOLDER = os.path.join(app.root_path, "static/uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# ADMIN DECORATOR (SECURITY)
# =========================
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


# =========================
# HOME PAGE
# =========================
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


# =========================
# STATIC PAGES
# =========================
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/aboutme")
def aboutme():
    return render_template("aboutme.html")


@app.route("/products")
def products_page():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    conn.close()

    return render_template("products.html", products=products)


@app.route("/news")
def news_page():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM news")
    news = cur.fetchall()

    conn.close()

    return render_template("news.html", news=news)


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        gmail = request.form["gmail"]
        password = request.form["password"]

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM users 
            WHERE gmail=%s AND password=%s
        """, (gmail, password))

        user = cur.fetchone()
        conn.close()

        if user:
            session.clear()

            session["user_id"] = user[0]
            session["gmail"] = user[1]
            session["role"] = user[3]  # role column

            if user[3] == "admin":
                return redirect("/admin")
            else:
                return "❌ You are not admin"

        return render_template("login.html", error="❌ Invalid credentials")

    return render_template("login.html")


# =========================
# ADMIN DASHBOARD
# =========================
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


# =========================
# ADD PRODUCT + NEWS
# =========================
@app.route("/admin_add", methods=["GET", "POST"])
@admin_required
def admin_add():
    conn = get_conn()
    cur = conn.cursor()

    if request.method == "POST":

        # ================= PRODUCT =================
        if "product_submit" in request.form:

            title = request.form["title"]
            quantity = request.form["quantity"]
            price = request.form["price"]
            detail = request.form["detail"]

            image_file = request.files["image"]
            filename = secure_filename(image_file.filename)

            image_file.save(os.path.join(UPLOAD_FOLDER, filename))

            cur.execute("""
                INSERT INTO products (title, image, quantity, price, detail)
                VALUES (%s,%s,%s,%s,%s)
            """, (title, filename, quantity, price, detail))

        # ================= NEWS =================
        elif "news_submit" in request.form:

            title = request.form["title"]
            date = request.form["date"]
            detail = request.form["detail"]

            image_file = request.files["image"]
            filename = secure_filename(image_file.filename)

            image_file.save(os.path.join(UPLOAD_FOLDER, filename))

            cur.execute("""
                INSERT INTO news (title, date, image, detail)
                VALUES (%s,%s,%s,%s)
            """, (title, date, filename, detail))

        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template("admin_add.html")


# =========================
# NEWS DETAIL PAGE
# =========================
@app.route("/news/<int:id>")
def news_detail(id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM news WHERE id=%s", (id,))
    news_item = cur.fetchone()

    conn.close()

    return render_template("news_detail.html", news=news_item)


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)