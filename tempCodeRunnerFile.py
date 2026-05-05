
from flask import Flask, render_template, request, redirect, session
from config import get_conn

app = Flask(__name__)
app.secret_key = "supersecretkey"


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

# ..............................................................................
# ..............................................................................

@app.route("/home")
def hhome():
    return render_template("home.html")


@app.route("/aboutme")
def about():
    return render_template("aboutme.html")


@app.route("/products")
def products():
    return render_template("products.html")


@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin_add")
def admin_add():
    return render_template("admin_add.html")


# ..............................................................................
# ..............................................................................
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
            # 👇 assuming role is in column index 3 or adjust accordingly
            role = user[3]

            if role == "admin":
                session["admin"] = True
                session["user"] = gmail
                return redirect("/admin")
            else:
                return "❌ You are not admin"

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    cur.execute("SELECT * FROM news")
    news = cur.fetchall()

    conn.close()

    return render_template("admin.html", products=products, news=news)

@app.route("/admin_add", methods=["GET", "POST"])
def admin_add():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_conn()
    cur = conn.cursor()

    if request.method == "POST":

        if "product_submit" in request.form:
            title = request.form["title"]
            image=request.form["image"]
            quantity = request.form["quantity"]
            price = request.form["price"]
            detail = request.form["detail"]

            cur.execute("""
    INSERT INTO products (title, image, quantity, price, detail)
    VALUES (%s,%s,%s,%s,%s)
""", (title, image, quantity, price, detail))

        if "news_submit" in request.form:
            title = request.form["title"]
            date = request.form["date"]
            image = request.form["image"]
            detail = request.form["detail"]

            cur.execute("""
                INSERT INTO news (title, date, image, detail)
                VALUES (%s,%s,%s,%s)
            """, (title, date, image, detail))

        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template("admin_add.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
      

if __name__ == "__main__":
    app.run(debug=True)
      

