DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
  order_id     INTEGER PRIMARY KEY,
  country      TEXT NOT NULL,
  category     TEXT NOT NULL,
  unit_price   REAL NOT NULL,
  quantity     INTEGER NOT NULL,
  order_date   TEXT NOT NULL,      -- stockée en ISO: YYYY-MM-DD
  total_amount REAL NOT NULL
);

CREATE INDEX idx_orders_country  ON orders(country);
CREATE INDEX idx_orders_category ON orders(category);
CREATE INDEX idx_orders_date     ON orders(order_date);
