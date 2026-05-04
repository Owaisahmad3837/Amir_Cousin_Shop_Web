from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/home")
def hhome():
    return render_template("home.html")


@app.route("/aboutme")
def about():
    return render_template("aboutme.html")


@app.route("/products")
def pro():
    return render_template("products.html")


@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/login")
def lodin():
    return render_template("login.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin_add")
def admin_add():
    return render_template("admin_add.html")

if __name__ == "__main__":
    app.run(debug=True)