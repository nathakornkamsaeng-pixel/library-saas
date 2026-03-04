import os
from flask import Flask, render_template_string, request, redirect, session
import psycopg2

app = Flask(__name__)

# SECRET KEY
app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret")

# ---------- DATABASE CONNECTION ----------
def get_conn():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise Exception("DATABASE_URL is not set in environment variables!")

    # Fix old postgres:// format if exists
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return psycopg2.connect(database_url)


# ---------- ROUTES ----------

@app.route("/")
def home():
    if "user" in session:
        return f"""
        <h2>Welcome {session['user']} 🎉</h2>
        <a href='/logout'>Logout</a>
        """
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password),
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return "<h3>Invalid credentials</h3><a href='/login'>Try Again</a>"

    return """
    <h2>Login</h2>
    <form method="POST">
        <input name="username" placeholder="Username"><br><br>
        <input name="password" type="password" placeholder="Password"><br><br>
        <button type="submit">Login</button>
    </form>
    """


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
