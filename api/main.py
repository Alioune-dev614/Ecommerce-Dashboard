from fastapi import FastAPI, Query
import sqlite3
from fastapi import Body
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


@app.get("/kpis")
def kpis(country: str | None = None, category: str | None = None):
    sql = """
    SELECT
      COUNT(*) AS orders_count,
      SUM(total_amount) AS revenue_total,
      AVG(total_amount) AS avg_order_value
    FROM orders
    WHERE 1=1
    """
    params = {}

    if country:
        sql += " AND country = :country"
        params["country"] = country
    if category:
        sql += " AND category = :category"
        params["category"] = category

    conn = get_conn()
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return dict(row)


@app.get("/filters")
def filters():
    conn = get_conn()
    countries = [r["country"] for r in conn.execute("SELECT DISTINCT country FROM orders ORDER BY country").fetchall()]
    categories = [r["category"] for r in conn.execute("SELECT DISTINCT category FROM orders ORDER BY category").fetchall()]
    conn.close()
    return {"countries": countries, "categories": categories}



@app.post("/orders")
def add_order(order: dict = Body(...)):
    sql = """
    INSERT INTO orders
    (country, category, unit_price, quantity, order_date, total_amount)
    VALUES (:country, :category, :unit_price, :quantity, :order_date, :total_amount)
    """

    order["total_amount"] = order["unit_price"] * order["quantity"]

    conn = get_conn()
    conn.execute(sql, order)
    conn.commit()
    conn.close()

    return {"status": "ok", "message": "Order added"}