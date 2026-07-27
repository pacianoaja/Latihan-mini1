-- Active: 1784640242004@@127.0.0.1@5432@ecommerce_db
CREATE TABLE IF NOT EXISTS dim_products (
    sku TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    stock_status BOOLEAN NOT NULL,
    rating NUMERIC(2, 1),
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL
);


