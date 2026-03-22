import csv
import os
import pymysql

OUTPUT = "/app/exports/incidents.csv"

conn = pymysql.connect(
    host=os.getenv("DB_HOST", "db"),
    user=os.getenv("DB_USER", "bsiapp"),
    password=os.getenv("DB_PASSWORD", "bsiapp123"),
    database=os.getenv("DB_NAME", "bsi"),
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True,
)

try:
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, severity, owner, notes FROM incidents ORDER BY id")
        rows = cur.fetchall()
finally:
    conn.close()

os.makedirs("/app/exports", exist_ok=True)

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "title", "severity", "owner", "notes"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Export written to {OUTPUT}")
