import html
import logging
import os
import subprocess
import uuid

import pymysql
from flask import Flask, abort, redirect, request, send_file, session, url_for

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")

logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)


def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "bsiapp"),
        password=os.getenv("DB_PASSWORD", "bsiapp123"),
        database=os.getenv("DB_NAME", "bsi"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f7f7f7; }}
    .card {{ background: white; padding: 20px; border-radius: 10px; max-width: 900px; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
    input {{ padding: 8px; margin: 4px 0; width: 100%; }}
    button, a.btn {{ display: inline-block; padding: 10px 14px; margin-top: 8px; text-decoration: none; background: #1f5eff; color: white; border-radius: 6px; border: none; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    code {{ background: #efefef; padding: 2px 4px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{title}</h1>
    {body}
  </div>
</body>
</html>"""


@app.before_request
def assign_request_id():
    request.reqid = uuid.uuid4().hex[:8]


@app.after_request
def add_request_id_header(response):
    response.headers["X-Request-ID"] = request.reqid
    return response


@app.route("/health")
def health():
    return {"status": "ok"}, 200


@app.route("/")
def index():
    user = session.get("user")
    if not user:
        return page(
            "Portal obsługi incydentów BSI",
            """
            <p>Wersja laboratoryjna z celową podatnością SQL injection.</p>
            <form method="post" action="/login">
              <label>Login</label>
              <input name="username" placeholder="np. analyst">
              <label>Hasło</label>
              <input name="password" type="password" placeholder="hasło">
              <button type="submit">Zaloguj</button>
            </form>
            <p><strong>Wskazówka dla prowadzącego:</strong> po udanym logowaniu jako admin pojawia się eksport CSV.</p>
            """,
        )

    username = html.escape(user["username"])
    role = html.escape(user["role"])
    export_link = '<p><a class="btn" href="/admin/export">Eksportuj incydenty CSV</a></p>' if role == "admin" else ""
    return page(
        "Panel użytkownika",
        f"""
        <p>Zalogowano jako: <strong>{username}</strong> (rola: <strong>{role}</strong>)</p>
        <p>Request-ID ostatniego żądania: <code>{request.reqid}</code></p>
        <p><a class="btn" href="/incidents">Pokaż incydenty</a></p>
        {export_link}
        <p><a class="btn" href="/logout">Wyloguj</a></p>
        """,
    )


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    # CELOWO PODATNE
    query = (
        f"SELECT id, username, role "
        f"FROM users "
        f"WHERE username='{username}' AND password='{password}' "
        f"LIMIT 1"
    )

    app.logger.warning(
        "reqid=%s ip=%s method=%s path=%s UNSAFE_SQL=%s",
        request.reqid,
        request.remote_addr,
        request.method,
        request.path,
        query,
    )

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()
    finally:
        conn.close()

    if row:
        session["user"] = {
            "id": row["id"],
            "username": row["username"],
            "role": row["role"],
        }
        return redirect(url_for("index"))

    return page(
        "Błąd logowania",
        """
        <p>Niepoprawne dane logowania.</p>
        <p><a class="btn" href="/">Powrót</a></p>
        """,
    ), 401


@app.route("/incidents")
def incidents():
    user = session.get("user")
    if not user:
        return redirect(url_for("index"))

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, severity, owner, notes FROM incidents ORDER BY id")
            rows = cur.fetchall()
    finally:
        conn.close()

    lines = []
    for row in rows:
        lines.append(
            "<tr>"
            f"<td>{row['id']}</td>"
            f"<td>{html.escape(row['title'])}</td>"
            f"<td>{html.escape(row['severity'])}</td>"
            f"<td>{html.escape(row['owner'])}</td>"
            f"<td>{html.escape(row['notes'])}</td>"
            "</tr>"
        )

    table = """
    <table>
      <thead>
        <tr><th>ID</th><th>Tytuł</th><th>Poziom</th><th>Właściciel</th><th>Notatki</th></tr>
      </thead>
      <tbody>
    """ + "\n".join(lines) + "</tbody></table>"

    return page("Lista incydentów", table + '<p><a class="btn" href="/">Powrót</a></p>')


@app.route("/admin/export")
def export_incidents():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        abort(403)

    app.logger.warning(
        "reqid=%s ip=%s action=export trigger=shell",
        request.reqid,
        request.remote_addr,
    )

    # CELOWO "efektowne" — uruchomienie shell-a w kontenerze,
    # aby Falco mogło to ładnie wykryć.
    subprocess.run(["sh", "-c", "python /app/export.py"], check=True)

    output_file = "/app/exports/incidents.csv"
    return send_file(output_file, as_attachment=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
