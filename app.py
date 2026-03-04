import os
import hashlib
from flask import Flask, render_template, request, redirect, session
import psycopg2

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("select role from users where username=%s and password=%s",
                    (username,password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            session["role"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("select count(*) from books")
    books = cur.fetchone()[0]

    cur.execute("select count(*) from loans")
    loans = cur.fetchone()[0]

    cur.execute("select count(*) from loans where due_date < current_date")
    overdue = cur.fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           books=books,
                           loans=loans,
                           overdue=overdue,
                           user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run()
