from fastapi import FastAPI, Query
import sqlite3
from pathlib import Path
import os
app = FastAPI(title="Ecommerce API")

#DB_PATH = Path("data/app.db")  # en local; dans Docker on mappera le volume au bon endroit
DB_PATH = Path(os.getenv("DB_PATH", "/data/app.db"))

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # pour récupérer des dict-like
    return conn


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/countries")
def countries():
    conn = get_conn()
    rows = conn.execute(
        "SELECT country, SUM(total_amount) AS revenue "
        "FROM orders GROUP BY country ORDER BY revenue DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/categories")
def categories():
    conn = get_conn()
    rows = conn.execute(
        "SELECT category, SUM(total_amount) AS revenue "
        "FROM orders GROUP BY category ORDER BY revenue DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/orders")
def orders(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    country: str | None = None,
    category: str | None = None,
):
    sql = "SELECT * FROM orders WHERE 1=1"
    params = {}

    if country:
        sql += " AND country = :country"
        params["country"] = country
    if category:
        sql += " AND category = :category"
        params["category"] = category

    sql += " ORDER BY order_date DESC LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset

    conn = get_conn()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
