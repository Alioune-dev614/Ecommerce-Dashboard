import csv
import sqlite3
from pathlib import Path
from datetime import datetime

CSV_PATH = Path("data/global_ecommerce_sales.csv")
DB_PATH = Path("db/app.db")
SQL_INIT = Path("init.sql")

def parse_date(s: str) -> str:
    # ton CSV ressemble à "7/6/2025" (M/D/YYYY) ou parfois "8/27/2025"
    s = s.strip()
    dt = datetime.strptime(s, "%m/%d/%Y")
    return dt.strftime("%Y-%m-%d")

def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")  # mieux pour lectures concurrentes
    conn.execute("PRAGMA foreign_keys=ON;")

    # crée la table
    conn.executescript(SQL_INIT.read_text(encoding="utf-8"))

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            Country = r["Country"].strip()
            if not Country:
                Country = "UNKNOWN"
            rows.append((
                int(r["Order_ID"]),
                Country,
                r["Category"].strip(),
                float(r["Unit_Price"]),
                int(r["Quantity"]),
                parse_date(r["Order_Date"]),
                float(r["Total_Amount"]),
            ))

    conn.executemany(
        """
        INSERT INTO orders(order_id, country, category, unit_price, quantity, order_date, total_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows
    )
    conn.commit()

    # mini vérif
    count = conn.execute("SELECT COUNT(*) FROM orders;").fetchone()[0]
    print(f"✅ Import terminé. Lignes insérées : {count}")

    conn.close()

if __name__ == "__main__":
    main()
