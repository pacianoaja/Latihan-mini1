-- Active: 1784640242004@@127.0.0.1@5432@ecommerce_db
CREATE TABLE IF NOT EXISTS dim_products (
    sku TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    stock_status BOOLEAN NOT NULL,
    rating NUMERIC(2, 1),
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL
);


CREATE TABLE IF NOT EXISTS etl_execution_logs (
    id SERIAL PRIMARY KEY,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL,            -- Contoh: 'SUCCESS' atau 'FAILED'
    total_extracted INT NOT NULL,
    total_upserted INT NOT NULL,
    data_loss_rate NUMERIC(5,2) NOT NULL,  -- Persentase data loss, misal 0.00
    duration_seconds NUMERIC(8,2) NOT NULL  -- Durasi eksekusi dalam detik
);